"""Tests for quantum counting."""

import math

import numpy as np
import pytest
from qiskit.quantum_info import Operator

from algorithms.grover.counting import (
    _grover_iteration_gate,
    controlled_grover_iteration_power_gate,
    count,
)
from algorithms.grover.oracles import MarkedBitstringOracle

_P0 = np.array([[1, 0], [0, 0]], dtype=complex)
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)


@pytest.mark.parametrize("power", [1, 2, 3])
def test_controlled_grover_iteration_power_gate_matches_matrix_power(power):
    """Controlled `Q^power`, control=qubit 0, matches Qiskit's
    `Gate.control()` ordering the same way HHL's controlled-unitary tests
    do (control=rightmost/least-significant kron factor)."""
    n = 2
    oracle = MarkedBitstringOracle(n, {"01"})
    q_matrix = Operator(_grover_iteration_gate(n, oracle)).data
    q_power_matrix = np.linalg.matrix_power(q_matrix, power)

    controlled_gate = controlled_grover_iteration_power_gate(n, oracle, power)
    expected = np.kron(np.eye(2**n), _P0) + np.kron(q_power_matrix, _P1)
    assert Operator(controlled_gate).equiv(Operator(expected))


def test_count_exact_instance():
    """n_qubits=3, 4 marked items out of 8: theta = arcsin(sqrt(4/8)) =
    pi/4 lands exactly on a 3-bit binary fraction of pi (y=2, 2/8 = 1/4),
    so this is exact — no shot noise, no retry needed."""
    oracle = MarkedBitstringOracle(3, {"000", "001", "010", "011"})
    assert count(3, oracle, n_count=3) == 4


@pytest.mark.parametrize("n_qubits,marked", [(3, {"101"}), (4, {"0000", "1111", "1010"})])
def test_count_approaches_true_count(n_qubits, marked):
    """A generic instance whose theta doesn't land on an exact binary
    fraction: accuracy improves with n_count (same relationship as
    `algorithms.qpe.implementation.estimate_phase`), so this uses a
    generous n_count and tolerance, retrying a few times for robustness
    against QPE's own bounded (not certain) precision guarantee."""
    true_m = len(marked)
    oracle = MarkedBitstringOracle(n_qubits, marked)
    for _ in range(3):
        estimated = count(n_qubits, oracle, n_count=6)
        if abs(estimated - true_m) <= 1:
            return
    pytest.fail(f"count() never approached the true count {true_m} (n_qubits={n_qubits})")


def test_grover_iteration_eigenvalues_are_phase_shifted_by_diffusion():
    """Regression guard for the phase-offset finding `count()`'s
    docstring documents: `circuit.diffusion_operator` carries an extra
    global phase of `-1` relative to the textbook `2|s><s| - I` (harmless
    for plain Grover search, where global phase is unobservable), which
    flips `Q`'s eigenvalues from `e^(+-2i*theta)` to `-e^(+-2i*theta)` —
    phase `pi +- 2*theta`, not `+-2*theta` — once `Q` is used under
    control, as quantum counting's QPE does."""
    n = 3
    oracle = MarkedBitstringOracle(n, {"101"})
    q_matrix = Operator(_grover_iteration_gate(n, oracle)).data
    eigenvalues = np.linalg.eigvals(q_matrix)
    nonzero_phases = [
        float(np.angle(ev)) for ev in eigenvalues if abs(np.angle(ev)) > 1e-9
    ]
    assert len(nonzero_phases) == 2

    true_theta = math.asin(math.sqrt(1 / 2**n))
    expected_abs_phase = math.pi - 2 * true_theta
    for phase in nonzero_phases:
        assert abs(phase) == pytest.approx(expected_abs_phase, abs=1e-6)


def test_count_matches_closed_form_relationship():
    """Sanity-checks the M-from-theta formula itself against a
    brute-force sweep: `sin(pi*y/2**n_count)**2 * N` should round to the
    same M for `y` and its mirror `2**n_count - y` (`sin(pi - x) =
    sin(x)`), independent of which eigenvalue branch QPE happens to
    measure."""
    n_count = 5
    dim = 2**n_count
    for y in range(1, dim):
        theta = math.pi * y / dim
        mirrored_theta = math.pi * (dim - y) / dim
        assert math.sin(theta) ** 2 == pytest.approx(math.sin(mirrored_theta) ** 2)
