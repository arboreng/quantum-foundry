"""Tests for the v0.2 VQE implementation."""

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator

from algorithms.vqe.circuit import ansatz_circuit, measurement_circuit
from algorithms.vqe.hamiltonians import PauliTerm, TransverseFieldIsingHamiltonian
from algorithms.vqe.implementation import expectation_value, solve_ground_state

_PAULI_MATRICES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def _term_matrix(term: PauliTerm) -> np.ndarray:
    matrix = _PAULI_MATRICES[term.paulis[0]]
    for pauli in term.paulis[1:]:
        matrix = np.kron(matrix, _PAULI_MATRICES[pauli])
    return term.coefficient * matrix


def _exact_ground_state_energy(hamiltonian) -> float:
    dim = 2**hamiltonian.n_qubits
    matrix = np.zeros((dim, dim), dtype=complex)
    for term in hamiltonian.terms:
        matrix += _term_matrix(term)
    return float(np.min(np.linalg.eigvalsh(matrix)))


class _FixedHamiltonian:
    """A `Hamiltonian` with hand-specified terms, for testing
    `implementation.py` in isolation from `TransverseFieldIsingHamiltonian`."""

    def __init__(self, n_qubits: int, terms: list[PauliTerm]):
        self.n_qubits = n_qubits
        self.terms = terms


class _ExplodingExecutor:
    """An `Executor` that fails any circuit execution, to prove a
    pure-identity term never triggers one."""

    name = "exploding"

    def run(self, circuit, shots):
        raise AssertionError("should not execute a circuit for a pure-identity term")


def test_transverse_field_ising_terms():
    hamiltonian = TransverseFieldIsingHamiltonian(3, j_coupling=1.0, h_field=0.5)
    terms = {(term.coefficient, term.paulis) for term in hamiltonian.terms}
    assert terms == {
        (-1.0, "ZZI"),
        (-1.0, "IZZ"),
        (-0.5, "XII"),
        (-0.5, "IXI"),
        (-0.5, "IIX"),
    }


@pytest.mark.parametrize("n_qubits,theta", [(1, 0.7), (2, 1.1), (3, 0.4)])
def test_ansatz_circuit_matches_ry_tensor_product_with_no_entangling_layer(n_qubits, theta):
    matrix = Operator(ansatz_circuit(n_qubits, [theta] * n_qubits, reps=0))
    ry = np.array(
        [[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]]
    )
    expected = ry
    for _ in range(n_qubits - 1):
        expected = np.kron(ry, expected)
    assert matrix.equiv(Operator(expected))


def test_ansatz_circuit_matches_explicit_construction_with_entangling_layer():
    n = 3
    params = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    built = ansatz_circuit(n, params, reps=1)

    expected = QuantumCircuit(n)
    expected.ry(params[0], 0)
    expected.ry(params[1], 1)
    expected.ry(params[2], 2)
    expected.cx(0, 1)
    expected.cx(1, 2)
    expected.ry(params[3], 0)
    expected.ry(params[4], 1)
    expected.ry(params[5], 2)

    assert Operator(built).equiv(Operator(expected))


def test_ansatz_circuit_rejects_wrong_param_count():
    with pytest.raises(ValueError):
        ansatz_circuit(2, params=[0.1, 0.2], reps=1)


def test_measurement_circuit_applies_correct_basis_rotation():
    n = 2
    params = [0.3, 0.4]
    term = PauliTerm(1.0, "XY")
    built = measurement_circuit(n, params, reps=0, term=term)
    unitary_part = built.remove_final_measurements(inplace=False)

    expected = ansatz_circuit(n, params, reps=0)
    expected.h(0)
    expected.sdg(1)
    expected.h(1)

    assert Operator(unitary_part).equiv(Operator(expected))


def test_expectation_value_single_qubit_z_term():
    hamiltonian = _FixedHamiltonian(1, [PauliTerm(1.0, "Z")])
    up = expectation_value(hamiltonian, params=[0.0], reps=0, shots=500)
    down = expectation_value(hamiltonian, params=[np.pi], reps=0, shots=500)
    assert up == pytest.approx(1.0, abs=0.05)
    assert down == pytest.approx(-1.0, abs=0.05)


def test_expectation_value_skips_circuit_execution_for_identity_term():
    hamiltonian = _FixedHamiltonian(2, [PauliTerm(2.0, "II")])
    value = expectation_value(
        hamiltonian, params=[0.0, 0.0], reps=0, executor=_ExplodingExecutor(), shots=100
    )
    assert value == pytest.approx(2.0)


@pytest.mark.parametrize("n_qubits,j,h", [(2, 1.0, 0.5), (3, 1.0, 0.3)])
def test_solve_ground_state_approaches_exact_ground_energy(n_qubits, j, h):
    """VQE is variational/approximate (see math.md): the variational
    principle guarantees the found energy is an upper bound on the true
    ground energy, not that it's exactly reached. Retry a few times for
    robustness against the classical optimizer occasionally settling on a
    local optimum or unlucky sampling noise on a single run."""
    hamiltonian = TransverseFieldIsingHamiltonian(n_qubits, j_coupling=j, h_field=h)
    exact = _exact_ground_state_energy(hamiltonian)
    for _ in range(3):
        _, found_energy = solve_ground_state(hamiltonian)
        if found_energy <= exact + 0.5:
            return
    pytest.fail(f"solve_ground_state never approached exact ground energy {exact}")
