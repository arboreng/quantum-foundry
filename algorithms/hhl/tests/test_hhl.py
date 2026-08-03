"""Tests for the HHL implementation."""

import math

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from scipy.linalg import expm

from algorithms.hhl.circuit import build_amplified_hhl_circuit, build_hhl_circuit
from algorithms.hhl.implementation import (
    amplify_and_solve_linear_system,
    optimal_amplification_iterations,
    solve_linear_system,
)
from algorithms.hhl.oracles import DiagonalXOracle

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)

# The demo instance from RFC-0010: A = I + (1/3)X (eigenvalues 4/3, 2/3),
# t chosen so both eigenvalues land on exact 3-bit binary fractions of
# 2*pi (k=2 for lambda=4/3, k=1 for lambda=2/3).
_A, _B, _T, _N_CLOCK, _C = 1.0, 1.0 / 3.0, 3 * math.pi / 8, 3, 0.5

# A negative-eigenvalue instance: A = (1/4)I + (3/4)X has eigenvalues +1
# (eigenvector |+>) and -1/2 (eigenvector |->). t = pi/2 puts both on exact
# 3-bit binary fractions of 2*pi — k=2 for lambda=1, and k=7 for
# lambda=-1/2, which unwraps to signed k=-1 — while keeping every
# eigenvalue inside the |lambda*t| < pi spectral bound the signed
# interpretation requires. c_constant stays below the smallest
# representable |lambda_k| = 2*pi/(t*2**n_clock) = 1/2.
_NEG_A, _NEG_B, _NEG_T, _NEG_C = 0.25, 0.75, math.pi / 2, 0.25


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


def test_clock_register_uncomputes_to_zero_with_amplification():
    """Extends `test_clock_register_uncomputes_to_zero` through one or
    more amplitude-amplification rounds: `A`, `A^-1`, and the `S_0`
    reflection all act on the clock register too, so this checks the
    exact uncomputation property still holds with amplification in the
    mix, not just for the plain circuit."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)
    mask = 2**_N_CLOCK - 1

    for num_iterations in (0, 1, 2):
        circuit = build_amplified_hhl_circuit(
            oracle, _T, _N_CLOCK, _C, b_state_prep, num_iterations
        )
        unitary_part = circuit.remove_final_measurements(inplace=False)
        state = Statevector(unitary_part)
        for index, amplitude in enumerate(state.data):
            if abs(amplitude) > 1e-9:
                assert index & mask == 0


def test_amplified_success_probability_matches_closed_form():
    """b = |+>, the exact single-eigenvalue branch: the amplified success
    probability should match `sin((2k+1)*theta)**2` exactly (via
    `Statevector`, no shot noise), for `theta = arcsin(sqrt(p))` and `p`
    the unamplified success probability."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)
    b_state_prep.h(0)

    lambda_1 = _A + _B
    p = (_C / lambda_1) ** 2
    theta = math.asin(math.sqrt(p))
    ancilla_mask = 1 << (_N_CLOCK + oracle.num_qubits)

    for num_iterations in (0, 1, 2, 3):
        circuit = build_amplified_hhl_circuit(
            oracle, _T, _N_CLOCK, _C, b_state_prep, num_iterations
        )
        unitary_part = circuit.remove_final_measurements(inplace=False)
        state = Statevector(unitary_part)

        success = sum(
            abs(amplitude) ** 2
            for index, amplitude in enumerate(state.data)
            if index & ancilla_mask
        )
        expected = math.sin((2 * num_iterations + 1) * theta) ** 2
        assert success == pytest.approx(expected, abs=1e-6)


def test_amplify_and_solve_linear_system_boosts_success_probability():
    """b = |0>, the mixed instance: amplification should raise the
    success probability while leaving the b-register's conditional
    distribution (the actual solution) unchanged."""
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)

    lambda_1, lambda_2 = _A + _B, _A - _B
    unamplified_success = 0.5 * ((_C / lambda_1) ** 2 + (_C / lambda_2) ** 2)
    num_iterations = optimal_amplification_iterations(unamplified_success)
    assert num_iterations >= 1

    success_probability, b_counts = amplify_and_solve_linear_system(
        oracle, _T, _N_CLOCK, _C, b_state_prep, num_iterations, shots=4000
    )
    assert success_probability > unamplified_success + 0.1

    matrix_a = np.array([[_A, _B], [_B, _A]])
    x = np.linalg.solve(matrix_a, np.array([1.0, 0.0]))
    expected_probs = (x**2) / np.sum(x**2)
    total = sum(b_counts.values())
    assert b_counts.get("0", 0) / total == pytest.approx(expected_probs[0], abs=0.05)
    assert b_counts.get("1", 0) / total == pytest.approx(expected_probs[1], abs=0.05)


def test_optimal_amplification_iterations_matches_expected_value():
    lambda_1, lambda_2 = _A + _B, _A - _B
    p = 0.5 * ((_C / lambda_1) ** 2 + (_C / lambda_2) ** 2)
    assert optimal_amplification_iterations(p) == 1


def test_negative_eigenvalue_solution_matches_classical_exactly():
    """Regression test for the signed phase unwrapping, via `Statevector`
    so no shot noise is involved: conditioned on the ancilla reading 1, the
    b-register distribution should match |A^-1 b|^2 for an `A` with a
    negative eigenvalue.

    QPE encodes lambda=-1/2 as the wrapped clock value k=7. Reading that as
    a positive eigenvalue 2*pi*7/(t*2**n_clock) = +7/2 rather than
    unwrapping it to -1/2 inverts the sign of that branch's contribution
    and shrinks its magnitude sevenfold, which moves this distribution from
    [0.1, 0.9] to roughly [0.76, 0.24] — so this fails loudly against the
    pre-fix interpretation."""
    oracle = DiagonalXOracle(_NEG_A, _NEG_B, _NEG_T)
    b_state_prep = QuantumCircuit(1)  # |0>

    lambda_1, lambda_2 = _NEG_A + _NEG_B, _NEG_A - _NEG_B
    assert lambda_2 < 0, "instance must actually exercise a negative eigenvalue"
    assert abs(lambda_1 * _NEG_T) < math.pi and abs(lambda_2 * _NEG_T) < math.pi

    matrix_a = np.array([[_NEG_A, _NEG_B], [_NEG_B, _NEG_A]])
    x = np.linalg.solve(matrix_a, np.array([1.0, 0.0]))
    expected_probs = (x**2) / np.sum(x**2)

    circuit = build_hhl_circuit(oracle, _NEG_T, _N_CLOCK, _NEG_C, b_state_prep)
    unitary_part = circuit.remove_final_measurements(inplace=False)
    state = Statevector(unitary_part)

    ancilla_mask = 1 << (_N_CLOCK + oracle.num_qubits)
    conditional = [0.0, 0.0]
    for index, amplitude in enumerate(state.data):
        if index & ancilla_mask:
            conditional[(index >> _N_CLOCK) & 1] += abs(amplitude) ** 2

    success_probability = sum(conditional)
    expected_success = 0.5 * ((_NEG_C / lambda_1) ** 2 + (_NEG_C / lambda_2) ** 2)
    assert success_probability == pytest.approx(expected_success, abs=1e-9)

    assert conditional[0] / success_probability == pytest.approx(expected_probs[0], abs=1e-9)
    assert conditional[1] / success_probability == pytest.approx(expected_probs[1], abs=1e-9)


def test_solve_linear_system_with_negative_eigenvalue():
    """The same negative-eigenvalue instance end to end through the
    sampled path, so the fix is covered through the public API and not
    only at the statevector level."""
    oracle = DiagonalXOracle(_NEG_A, _NEG_B, _NEG_T)
    b_state_prep = QuantumCircuit(1)  # |0>

    matrix_a = np.array([[_NEG_A, _NEG_B], [_NEG_B, _NEG_A]])
    x = np.linalg.solve(matrix_a, np.array([1.0, 0.0]))
    expected_probs = (x**2) / np.sum(x**2)

    lambda_1, lambda_2 = _NEG_A + _NEG_B, _NEG_A - _NEG_B
    expected_success = 0.5 * ((_NEG_C / lambda_1) ** 2 + (_NEG_C / lambda_2) ** 2)

    success_probability, b_counts = solve_linear_system(
        oracle, _NEG_T, _N_CLOCK, _NEG_C, b_state_prep, shots=4000
    )
    assert success_probability == pytest.approx(expected_success, abs=0.03)
    total = sum(b_counts.values())
    assert b_counts.get("0", 0) / total == pytest.approx(expected_probs[0], abs=0.05)
    assert b_counts.get("1", 0) / total == pytest.approx(expected_probs[1], abs=0.05)


def test_negative_eigenvalue_clock_register_uncomputes_to_zero():
    """`test_clock_register_uncomputes_to_zero` for the negative-eigenvalue
    instance: the wrapped clock branch must uncompute as cleanly as the
    unwrapped ones."""
    oracle = DiagonalXOracle(_NEG_A, _NEG_B, _NEG_T)
    b_state_prep = QuantumCircuit(1)
    circuit = build_hhl_circuit(oracle, _NEG_T, _N_CLOCK, _NEG_C, b_state_prep)
    unitary_part = circuit.remove_final_measurements(inplace=False)
    state = Statevector(unitary_part)

    mask = 2**_N_CLOCK - 1
    for index, amplitude in enumerate(state.data):
        if abs(amplitude) > 1e-9:
            assert index & mask == 0


def test_optimal_amplification_rejects_zero_probability():
    with pytest.raises(ValueError):
        optimal_amplification_iterations(0.0)


def test_optimal_amplification_rejects_probability_above_one():
    with pytest.raises(ValueError):
        optimal_amplification_iterations(1.01)
