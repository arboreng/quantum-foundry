"""Tests for semiclassical (Kitaev iterative) phase estimation."""

import pytest
from qiskit.circuit import QuantumCircuit

from algorithms.qpe.implementation import estimate_phase
from algorithms.qpe.oracles import PhaseGateOracle
from algorithms.qpe.semiclassical import estimate_phase_semiclassical


def _eigenstate_prep() -> QuantumCircuit:
    circuit = QuantumCircuit(1)
    circuit.x(0)
    return circuit


# theta values with an exact n_count-bit binary expansion -> deterministic,
# exact recovery with no retry loop needed (mirrors test_qpe.py's EXACT_CASES).
EXACT_CASES = [
    (0.25, 2),
    (0.25, 3),
    (0.375, 3),
    (0.5, 4),
    (0.125, 5),
    (0.0, 3),
]


@pytest.mark.parametrize("theta,n_count", EXACT_CASES)
def test_estimate_phase_semiclassical_exact_for_terminating_binary_theta(theta, n_count):
    result = estimate_phase_semiclassical(PhaseGateOracle(theta), _eigenstate_prep(), n_count)
    assert result == pytest.approx(theta)


@pytest.mark.parametrize("theta,n_count", EXACT_CASES)
def test_estimate_phase_semiclassical_matches_coherent_qpe(theta, n_count):
    """The whole point of this circuit shape: a single reused ancilla
    with classical feedback between rounds should recover exactly the
    same phase as `n_count` ancillas plus a coherent inverse QFT."""
    coherent = estimate_phase(PhaseGateOracle(theta), _eigenstate_prep(), n_count)
    iterative = estimate_phase_semiclassical(PhaseGateOracle(theta), _eigenstate_prep(), n_count)
    assert iterative == pytest.approx(coherent)


def test_estimate_phase_semiclassical_approximates_non_terminating_theta():
    """theta=0.1 has no exact finite binary expansion — same tolerance
    argument as `test_qpe.py`'s coherent-QPE analog."""
    theta, n_count = 0.1, 8
    tolerance = 1 / 2**n_count
    for _ in range(20):
        result = estimate_phase_semiclassical(
            PhaseGateOracle(theta), _eigenstate_prep(), n_count, shots=5
        )
        if abs(result - theta) <= tolerance:
            return
    pytest.fail(f"estimate_phase_semiclassical never landed within {tolerance} of {theta}")


def test_estimate_phase_semiclassical_single_counting_qubit():
    result = estimate_phase_semiclassical(PhaseGateOracle(0.5), _eigenstate_prep(), n_count=1)
    assert result == pytest.approx(0.5)
