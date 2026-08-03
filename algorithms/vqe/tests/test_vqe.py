"""Tests for the VQE implementation."""

import numpy as np
import pytest
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from algorithms.vqe.circuit import ansatz_circuit, group_measurement_circuit, measurement_circuit
from algorithms.vqe.execution import AerExecutor
from algorithms.vqe.hamiltonians import (
    HeisenbergHamiltonian,
    PauliTerm,
    TransverseFieldIsingHamiltonian,
    group_qwc_terms,
)
from algorithms.vqe.implementation import (
    expectation_value,
    expectation_value_grouped,
    solve_ground_state,
    solve_ground_state_grouped,
)

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


class _CountingExecutor:
    """Wraps a real `Executor`, counting how many circuits were run — to
    prove measurement grouping actually reduces circuit executions, not
    just to check the returned numbers."""

    name = "counting"

    def __init__(self):
        self._inner = AerExecutor()
        self.call_count = 0

    def run(self, circuit, shots):
        self.call_count += 1
        return self._inner.run(circuit, shots)


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


def test_group_qwc_terms_separates_z_and_x_terms():
    """For the transverse-field Ising model, every ZZ term qubit-wise
    commutes with every other ZZ term (they only ever share `Z` or `I` at
    any qubit), and likewise for the X terms — but a ZZ term and an X
    term never qubit-wise commute if they share a qubit (`Z` vs `X`
    there). So greedy grouping should find exactly 2 groups: all ZZ terms,
    all X terms."""
    hamiltonian = TransverseFieldIsingHamiltonian(4, j_coupling=1.0, h_field=0.5)
    groups = group_qwc_terms(hamiltonian.terms)
    assert len(groups) == 2
    paulis_by_group = [{term.paulis for term in group} for group in groups]
    assert {"ZZII", "IZZI", "IIZZ"} in paulis_by_group
    assert {"XIII", "IXII", "IIXI", "IIIX"} in paulis_by_group


def test_group_measurement_circuit_applies_shared_basis_rotation():
    n = 3
    params = [0.1, 0.2, 0.3]
    group = [PauliTerm(1.0, "XII"), PauliTerm(1.0, "IIX")]
    built = group_measurement_circuit(n, params, reps=0, group=group)
    unitary_part = built.remove_final_measurements(inplace=False)

    expected = ansatz_circuit(n, params, reps=0)
    expected.h(0)
    expected.h(2)

    assert Operator(unitary_part).equiv(Operator(expected))


def test_expectation_value_grouped_matches_expectation_value():
    """Same physics, fewer circuits: grouped and ungrouped expectation
    values should agree up to shot noise."""
    hamiltonian = TransverseFieldIsingHamiltonian(3, j_coupling=1.0, h_field=0.5)
    params = [0.3, 0.6, 0.9, 0.2, 0.5, 0.8]

    ungrouped = expectation_value(hamiltonian, params, reps=1, shots=8000)
    grouped = expectation_value_grouped(hamiltonian, params, reps=1, shots=8000)
    assert grouped == pytest.approx(ungrouped, abs=0.15)


def test_expectation_value_grouped_uses_fewer_circuit_executions():
    """The actual point of grouping: for the transverse-field Ising model
    (2 qwc groups regardless of n_qubits), `expectation_value_grouped`
    should run exactly 2 circuits, vs. `expectation_value`'s one per
    non-identity term (2*n_qubits - 1)."""
    hamiltonian = TransverseFieldIsingHamiltonian(4, j_coupling=1.0, h_field=0.5)
    params = [0.5] * (4 * 2)

    ungrouped_executor = _CountingExecutor()
    expectation_value(hamiltonian, params, reps=1, executor=ungrouped_executor, shots=100)
    assert ungrouped_executor.call_count == 2 * 4 - 1

    grouped_executor = _CountingExecutor()
    expectation_value_grouped(hamiltonian, params, reps=1, executor=grouped_executor, shots=100)
    assert grouped_executor.call_count == 2


def test_expectation_value_grouped_skips_circuit_execution_for_identity_term():
    hamiltonian = _FixedHamiltonian(2, [PauliTerm(2.0, "II")])
    value = expectation_value_grouped(
        hamiltonian, params=[0.0, 0.0], reps=0, executor=_ExplodingExecutor(), shots=100
    )
    assert value == pytest.approx(2.0)


@pytest.mark.parametrize("n_qubits,j,h", [(2, 1.0, 0.5), (3, 1.0, 0.3)])
def test_solve_ground_state_grouped_approaches_exact_ground_energy(n_qubits, j, h):
    """Mirrors `test_solve_ground_state_approaches_exact_ground_energy`
    for the grouped-measurement version."""
    hamiltonian = TransverseFieldIsingHamiltonian(n_qubits, j_coupling=j, h_field=h)
    exact = _exact_ground_state_energy(hamiltonian)
    for _ in range(3):
        _, found_energy = solve_ground_state_grouped(hamiltonian)
        if found_energy <= exact + 0.5:
            return
    pytest.fail(f"solve_ground_state_grouped never approached exact ground energy {exact}")


def test_heisenberg_terms():
    hamiltonian = HeisenbergHamiltonian(3, j_coupling=1.0)
    terms = {(term.coefficient, term.paulis) for term in hamiltonian.terms}
    assert terms == {
        (1.0, "XXI"),
        (1.0, "YYI"),
        (1.0, "ZZI"),
        (1.0, "IXX"),
        (1.0, "IYY"),
        (1.0, "IZZ"),
    }


def test_group_qwc_terms_separates_heisenberg_by_pauli_type():
    """Unlike the transverse-field Ising model's 2 groups, adjacent
    Heisenberg terms sharing a qubit (e.g. `XXI` and `IXX` share qubit 1)
    always agree there only within the *same* Pauli type — `XXI` and
    `YYI` share two qubits and disagree at both — so grouping splits
    strictly by type: all `X` pairs, all `Y` pairs, all `Z` pairs, giving
    exactly 3 groups regardless of `n_qubits`."""
    hamiltonian = HeisenbergHamiltonian(4, j_coupling=1.0)
    groups = group_qwc_terms(hamiltonian.terms)
    assert len(groups) == 3
    paulis_by_group = [{term.paulis for term in group} for group in groups]
    assert {"XXII", "IXXI", "IIXX"} in paulis_by_group
    assert {"YYII", "IYYI", "IIYY"} in paulis_by_group
    assert {"ZZII", "IZZI", "IIZZ"} in paulis_by_group


def test_expectation_value_matches_exact_statevector_for_heisenberg():
    """The point of this Hamiltonian: its `YY` terms genuinely exercise
    `measurement_circuit`'s `Y`-basis rotation for the first time via a
    real Hamiltonian (not just the abstract `PauliTerm(1.0, "XY")` unit
    test), checked here against the exact expectation value computed
    from the ansatz's own statevector."""
    n, reps = 2, 0
    params = [0.4, 0.9]
    hamiltonian = HeisenbergHamiltonian(n, j_coupling=1.0)

    state = Statevector(ansatz_circuit(n, params, reps))
    exact = 0.0
    for term in hamiltonian.terms:
        matrix = _PAULI_MATRICES[term.paulis[0]]
        for pauli in term.paulis[1:]:
            matrix = np.kron(matrix, _PAULI_MATRICES[pauli])
        exact += term.coefficient * np.real(state.data.conj() @ matrix @ state.data)

    estimated = expectation_value(hamiltonian, params, reps, shots=8000)
    assert estimated == pytest.approx(exact, abs=0.1)


def test_solve_ground_state_grouped_approaches_exact_ground_energy_for_heisenberg():
    """Mirrors the transverse-field Ising model's end-to-end test, for
    the Heisenberg model instead — a genuinely different Hamiltonian,
    same classical-optimization-loop machinery."""
    hamiltonian = HeisenbergHamiltonian(2, j_coupling=1.0)
    exact = _exact_ground_state_energy(hamiltonian)
    for _ in range(3):
        _, found_energy = solve_ground_state_grouped(hamiltonian)
        if found_energy <= exact + 0.5:
            return
    pytest.fail(f"solve_ground_state_grouped never approached exact ground energy {exact}")


def test_solve_ground_state_grouped_approaches_exact_ground_energy_for_heisenberg_n3():
    """The 3-qubit open Heisenberg chain's ground energy (-4.0) is
    *doubly degenerate* (confirmed via `numpy.linalg.eigvalsh`: the two
    lowest eigenvalues both equal -4.0) — a harder variational landscape
    than the transverse-field Ising model's non-degenerate ground states,
    empirically needing more ansatz depth (`reps=3`, not the default `1`)
    and more retries (COBYLA reaches within `0.5` of exact on ~7/8
    attempts at `reps=3`, vs. essentially never at `reps=1`) to reliably
    approach the true minimum. This is a real property of this
    Hamiltonian's landscape, not a bug — see math.md."""
    hamiltonian = HeisenbergHamiltonian(3, j_coupling=1.0)
    exact = _exact_ground_state_energy(hamiltonian)
    for _ in range(5):
        _, found_energy = solve_ground_state_grouped(hamiltonian, reps=3)
        if found_energy <= exact + 0.5:
            return
    pytest.fail(f"solve_ground_state_grouped never approached exact ground energy {exact}")
