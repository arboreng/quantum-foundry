"""Tests for the v0.2 HHL implementation."""

import math

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from scipy.linalg import expm

from algorithms.hhl.circuit import build_hhl_circuit
from algorithms.hhl.implementation import solve_linear_system
from algorithms.hhl.oracles import DiagonalXOracle

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)

# The demo instance from RFC-0010: A = I + (1/3)X (eigenvalues 4/3, 2/3),
# t chosen so both eigenvalues land on exact 3-bit binary fractions of
# 2*pi (k=2 for lambda=4/3, k=1 for lambda=2/3).
_A, _B, _T, _N_CLOCK, _C = 1.0, 1.0 / 3.0, 3 * math.pi / 8, 3, 0.5


def _exact_controlled_unitary(a: float, b: float, t: float, power: int) -> np.ndarray:
    """Controlled-U with control=qubit 0, target=qubit 1, matching
    Qiskit's `Gate.control()` qubit ordering (control qubits first) and
    little-endian `Operator` convention (higher qubit index = more
    significant / leftmost kron factor)."""
    matrix_a = a * _I2 + b * _X
    u = expm(1j * matrix_a * t * power)
    p0 = np.array([[1, 0], [0, 0]], dtype=complex)
    p1 = np.array([[0, 0], [0, 1]], dtype=complex)
    return np.kron(_I2, p0) + np.kron(u, p1)


@pytest.mark.parametrize(
    "a,b,t,power",
    [
        (1.0, 1.0 / 3.0, 3 * math.pi / 8, 1),
        (0.5, 0.2, 1.3, 2),
        (1.0, 1.0 / 3.0, 3 * math.pi / 8, 2),
    ],
)
def test_controlled_power_gate_matches_exact_matrix_exponential(a, b, t, power):
    oracle = DiagonalXOracle(a, b, t)
    gate = oracle.controlled_power_gate(power)
    assert Operator(gate).equiv(Operator(_exact_controlled_unitary(a, b, t, power)))


def test_clock_register_uncomputes_to_zero():
    """The multiplexed rotation only touches the ancilla, so QPE's
    inverse should disentangle the clock register back to |0...0> exactly
    (by construction, since the demo instance's eigenvalues land on exact
    n_clock-bit fractions) — checked directly against the statevector,
    with no measurement/shot noise involved."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)
    circuit = build_hhl_circuit(oracle, _T, _N_CLOCK, _C, b_state_prep)
    unitary_part = circuit.remove_final_measurements(inplace=False)
    state = Statevector(unitary_part)

    mask = 2**_N_CLOCK - 1
    for index, amplitude in enumerate(state.data):
        if abs(amplitude) > 1e-9:
            assert index & mask == 0


def test_solve_linear_system_single_eigenvalue_branch():
    """b = |+>, a pure eigenvector of A: both the success probability and
    the b-register's conditional distribution should match the closed
    form exactly (up to shot noise), since only one clock-register branch
    ever has nonzero amplitude."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)
    b_state_prep.h(0)

    lambda_1 = _A + _B
    expected_success = (_C / lambda_1) ** 2

    success_probability, b_counts = solve_linear_system(
        oracle, _T, _N_CLOCK, _C, b_state_prep, shots=4000
    )
    assert success_probability == pytest.approx(expected_success, abs=0.03)
    total = sum(b_counts.values())
    assert b_counts.get("0", 0) / total == pytest.approx(0.5, abs=0.1)
    assert b_counts.get("1", 0) / total == pytest.approx(0.5, abs=0.1)


def test_solve_linear_system_matches_classical_solution():
    """b = |0>, a mix of both eigenvectors: the b-register's conditional
    distribution should match |A^-1 b|^2 (normalized), computed here via
    plain linear algebra for comparison — this is HHL's actual point,
    recovering (a state proportional to) the classical solution."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)  # |0>

    matrix_a = np.array([[_A, _B], [_B, _A]])
    x = np.linalg.solve(matrix_a, np.array([1.0, 0.0]))
    expected_probs = (x**2) / np.sum(x**2)

    lambda_1, lambda_2 = _A + _B, _A - _B
    expected_success = 0.5 * ((_C / lambda_1) ** 2 + (_C / lambda_2) ** 2)

    success_probability, b_counts = solve_linear_system(
        oracle, _T, _N_CLOCK, _C, b_state_prep, shots=4000
    )
    assert success_probability == pytest.approx(expected_success, abs=0.03)
    total = sum(b_counts.values())
    assert b_counts.get("0", 0) / total == pytest.approx(expected_probs[0], abs=0.05)
    assert b_counts.get("1", 0) / total == pytest.approx(expected_probs[1], abs=0.05)
