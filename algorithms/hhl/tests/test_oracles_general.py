"""Tests for `GeneralSingleQubitOracle`, validated directly against exact
matrix exponentiation before anything is built on top of it."""

import math

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator
from scipy.linalg import expm

from algorithms.hhl.implementation import solve_linear_system
from algorithms.hhl.oracles import DiagonalXOracle, GeneralSingleQubitOracle

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def _exact_controlled_unitary(a, vx, vy, vz, t, power) -> np.ndarray:
    """Same control=qubit 0 / target=qubit 1 convention as
    `test_hhl.py::_exact_controlled_unitary`."""
    matrix_a = a * _I2 + vx * _X + vy * _Y + vz * _Z
    u = expm(1j * matrix_a * t * power)
    p0 = np.array([[1, 0], [0, 0]], dtype=complex)
    p1 = np.array([[0, 0], [0, 1]], dtype=complex)
    return np.kron(_I2, p0) + np.kron(u, p1)


@pytest.mark.parametrize(
    "a,vx,vy,vz,t,power",
    [
        (1.0, 1.0 / 3.0, 0.0, 0.0, 3.0, 1),  # X axis only
        (0.5, 0.0, 0.4, 0.0, 1.7, 2),  # Y axis only
        (0.0, 0.0, 0.0, 0.6, 2.2, 1),  # Z axis only
        (1.0, 0.2, 0.3, 0.4, 1.1, 1),  # general axis
        (0.7, -0.3, 0.5, -0.2, 0.9, 3),  # general axis, negative components
        (0.0, 0.0, 0.0, 0.0, 1.0, 2),  # v = 0 (pure global phase)
    ],
)
def test_controlled_power_gate_matches_exact_matrix_exponential(a, vx, vy, vz, t, power):
    oracle = GeneralSingleQubitOracle(a, vx, vy, vz, t)
    gate = oracle.controlled_power_gate(power)
    expected = _exact_controlled_unitary(a, vx, vy, vz, t, power)
    assert Operator(gate).equiv(Operator(expected))


@pytest.mark.parametrize("a,b,t,power", [(1.0, 1.0 / 3.0, 3.0, 1), (0.5, -0.2, 1.3, 2)])
def test_matches_diagonal_x_oracle_for_x_only_axis(a, b, t, power):
    """`GeneralSingleQubitOracle(a, b, 0, 0, t)` should exactly reproduce
    `DiagonalXOracle(a, b, t)` — the same physical system, two different
    (both now-validated) constructions."""
    general = GeneralSingleQubitOracle(a, b, 0.0, 0.0, t)
    diagonal = DiagonalXOracle(a, b, t)
    assert Operator(general.controlled_power_gate(power)).equiv(
        Operator(diagonal.controlled_power_gate(power))
    )


def test_solve_linear_system_with_genuinely_3d_axis():
    """The actual point of this oracle: HHL should work end to end for a
    Hermitian matrix that isn't diagonal in any single Pauli basis (here,
    an equal mix of X, Y, and Z — genuinely exercising the Y component
    `DiagonalXOracle` can't express at all), not just validate the gate
    in isolation.

    `|v| = 1/3` (an equal 3-way split of the same magnitude
    `DiagonalXOracle`'s demo instance uses) keeps the eigenvalues at
    exactly `4/3` and `2/3`, so `t = 3*pi/8` still lands them on exact
    3-bit binary fractions — same precision-exactness trick, general
    axis."""
    a = 1.0
    c = (1.0 / 3.0) / math.sqrt(3)  # vx=vy=vz=c, so |v| = sqrt(3*c**2) = 1/3
    t = 3 * math.pi / 8
    n_clock, c_constant = 3, 0.5

    oracle = GeneralSingleQubitOracle(a, c, c, c, t)
    b_state_prep = QuantumCircuit(1)  # |0>

    matrix_a = np.array([[a + c, c - 1j * c], [c + 1j * c, a - c]], dtype=complex)
    b_vector = np.array([1.0, 0.0], dtype=complex)
    x = np.linalg.solve(matrix_a, b_vector)
    expected_probs = (np.abs(x) ** 2) / np.sum(np.abs(x) ** 2)

    # Unlike DiagonalXOracle's X-only axis (orthogonal to Z, so |0> always
    # splits 50/50 across the eigenbasis), this axis has a nonzero Z
    # component, so |0>'s overlap with each eigenvector isn't 50/50 —
    # computed here via exact diagonalization, not assumed.
    eigenvalues, eigenvectors = np.linalg.eigh(matrix_a)
    expected_success = sum(
        abs(np.vdot(eigenvectors[:, i], b_vector)) ** 2 * (c_constant / eigenvalues[i]) ** 2
        for i in range(2)
    )

    success_probability, b_counts = solve_linear_system(
        oracle, t, n_clock, c_constant, b_state_prep, shots=4000
    )
    assert success_probability == pytest.approx(expected_success, abs=0.03)
    total = sum(b_counts.values())
    assert b_counts.get("0", 0) / total == pytest.approx(expected_probs[0], abs=0.05)
    assert b_counts.get("1", 0) / total == pytest.approx(expected_probs[1], abs=0.05)
