"""Tests for the v0.2 Quantum Phase Estimation implementation."""

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator

from algorithms.qpe.implementation import estimate_phase
from algorithms.qpe.oracles import PhaseGateOracle


def _eigenstate_prep() -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    circuit.x(0)
    return circuit


@pytest.mark.parametrize("theta", [0.25, 0.1, -0.3, 0.0])
@pytest.mark.parametrize("power", [1, 2, 3, 5])
def test_phase_gate_oracle_matches_expected_unitary(theta, power):
    oracle = PhaseGateOracle(theta)
    matrix = Operator(oracle.controlled_power_gate(power)).data
    expected_phase = np.exp(2j * np.pi * theta * power)
    expected = np.diag([1, 1, 1, expected_phase])
    assert np.allclose(matrix, expected)


# theta values with an exact n_count-bit binary expansion -> deterministic,
# exact recovery with no retry loop needed.
EXACT_CASES = [
    (0.25, 2),
    (0.25, 3),
    (0.375, 3),
    (0.5, 4),
    (0.125, 5),
    (0.0, 3),
]


@pytest.mark.parametrize("theta,n_count", EXACT_CASES)
def test_estimate_phase_exact_for_terminating_binary_theta(theta, n_count):
    result = estimate_phase(PhaseGateOracle(theta), _eigenstate_prep(), n_count)
    assert result == pytest.approx(theta)


def test_estimate_phase_approximates_non_terminating_theta():
    """theta=0.1 has no exact finite binary expansion; per math.md the
    single-shot estimate is within 1/2**n_count with probability >= 4/pi^2
    ~ 0.405 — retry rather than assert on one probabilistic attempt."""
    theta, n_count = 0.1, 8
    tolerance = 1 / 2**n_count
    for _ in range(20):
        result = estimate_phase(PhaseGateOracle(theta), _eigenstate_prep(), n_count)
        if abs(result - theta) <= tolerance:
            return
    pytest.fail(f"estimate_phase never landed within {tolerance} of {theta} in 20 attempts")


def test_estimate_phase_single_counting_qubit():
    result = estimate_phase(PhaseGateOracle(0.5), _eigenstate_prep(), n_count=1)
    assert result == pytest.approx(0.5)
