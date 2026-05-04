"""Cross-validation: known-answer checks against textbook/published
instances of every algorithm, run through its top-level public API.

Distinct from each algorithm's own test suite (which validates internal
circuit-building details — gate matrices, uncomputation, GF(2) linear
algebra, and so on): this module only calls the same entry point a user
would (`factor`, `search`, `estimate_phase`, ...) with a well-known
problem instance from the algorithm's original paper or a standard
textbook, and checks the published answer comes back out. A black-box
"does the whole stack still work" regression suite, not a re-derivation
of correctness.
"""

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from qiskit.circuit import QuantumCircuit

from algorithms.bernstein_vazirani.implementation import find_hidden_string
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle
from algorithms.deutsch_jozsa.implementation import is_constant
from algorithms.deutsch_jozsa.oracles import ConstantOracle, ParityOracle
from algorithms.grover.implementation import search
from algorithms.hhl.implementation import solve_linear_system
from algorithms.hhl.oracles import DiagonalXOracle
from algorithms.qaoa.implementation import solve_maxcut
from algorithms.qpe.implementation import estimate_phase
from algorithms.qpe.oracles import PhaseGateOracle
from algorithms.shor.implementation import factor
from algorithms.simon.implementation import find_hidden_period
from algorithms.simon.oracles import LinearOracle
from algorithms.vqe.hamiltonians import PauliTerm, TransverseFieldIsingHamiltonian
from algorithms.vqe.implementation import solve_ground_state

_PAULI_MATRICES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def _exact_ground_state_energy(hamiltonian: TransverseFieldIsingHamiltonian) -> float:
    def term_matrix(term: PauliTerm) -> np.ndarray:
        matrix = _PAULI_MATRICES[term.paulis[0]]
        for pauli in term.paulis[1:]:
            matrix = np.kron(matrix, _PAULI_MATRICES[pauli])
        return term.coefficient * matrix

    dim = 2**hamiltonian.n_qubits
    matrix = np.zeros((dim, dim), dtype=complex)
    for term in hamiltonian.terms:
        matrix += term_matrix(term)
    return float(np.min(np.linalg.eigvalsh(matrix)))


def _check_shor() -> None:
    """Nielsen & Chuang Section 5.3.2's worked example: N=15 factors as
    3*5, found via order-finding for a randomly chosen base."""
    factors = factor(15, rng=random.Random(0))
    assert set(factors) == {3, 5}, factors


def _check_grover() -> None:
    """Grover (1996): finds a single marked item among 8 candidates."""
    result = search(3, {"101"})
    assert result == "101", result


def _check_deutsch_jozsa() -> None:
    """Deutsch-Jozsa (1992): distinguishes constant from balanced with a
    single oracle query."""
    assert is_constant(3, ConstantOracle(3, value=1)) is True
    assert is_constant(3, ParityOracle(3, subset={0, 1, 2})) is False


def _check_bernstein_vazirani() -> None:
    """Bernstein-Vazirani (1993): recovers a hidden string with a single
    oracle query."""
    result = find_hidden_string(3, HiddenStringOracle("101"))
    assert result == "101", result


def _check_simon() -> None:
    """Simon (1994): recovers a hidden XOR period from a two-to-one
    function."""
    result = find_hidden_period(2, LinearOracle("11"))
    assert result == "11", result


def _check_qpe() -> None:
    """Kitaev (1995): exact phase estimation for a phase with a
    terminating binary expansion."""
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)
    theta = estimate_phase(PhaseGateOracle(0.25), eigenstate_prep, n_count=3)
    assert abs(theta - 0.25) < 1e-9, theta


def _check_qaoa() -> None:
    """Farhi, Goldstone, Gutmann (2014): finds the true optimal cut for a
    triangle graph (retried a few times — QAOA's classical loop is
    approximate, see algorithms/qaoa/math.md)."""
    triangle = [(0, 1), (1, 2), (0, 2)]
    for _ in range(3):
        _, cost = solve_maxcut(3, triangle)
        if cost == 2:
            return
    raise AssertionError("solve_maxcut never found the triangle's optimal cut (2)")


def _check_vqe() -> None:
    """Peruzzo et al. (2014): approaches the exact ground-state energy of
    a small transverse-field Ising chain (retried a few times — VQE is
    variational/approximate, see algorithms/vqe/math.md)."""
    hamiltonian = TransverseFieldIsingHamiltonian(2, j_coupling=1.0, h_field=0.5)
    exact = _exact_ground_state_energy(hamiltonian)
    for _ in range(3):
        _, energy = solve_ground_state(hamiltonian)
        if energy <= exact + 0.5:
            return
    raise AssertionError("solve_ground_state never approached the exact ground energy")


def _check_hhl() -> None:
    """Harrow, Hassidim, Lloyd (2009): the b=|0> demo instance's
    postselected output matches the classical solution x = A^-1 b."""
    a, b, t, n_clock, c_constant = 1.0, 1.0 / 3.0, 3 * math.pi / 8, 3, 0.5
    oracle = DiagonalXOracle(a, b, t)
    b_state_prep = QuantumCircuit(1)
    _, b_counts = solve_linear_system(oracle, t, n_clock, c_constant, b_state_prep, shots=4000)
    total = sum(b_counts.values())
    p0 = b_counts.get("0", 0) / total
    assert abs(p0 - 0.9) < 0.05, p0


@dataclass(frozen=True)
class KnownAnswerCase:
    algorithm: str
    source: str
    check: Callable[[], None]


CASES = [
    KnownAnswerCase("Shor", "Nielsen & Chuang, Section 5.3.2 (N=15)", _check_shor),
    KnownAnswerCase("Grover", "Grover (1996)", _check_grover),
    KnownAnswerCase("Deutsch-Jozsa", "Deutsch-Jozsa (1992)", _check_deutsch_jozsa),
    KnownAnswerCase("Bernstein-Vazirani", "Bernstein-Vazirani (1993)", _check_bernstein_vazirani),
    KnownAnswerCase("Simon", "Simon (1994)", _check_simon),
    KnownAnswerCase("QPE", "Kitaev (1995)", _check_qpe),
    KnownAnswerCase("QAOA", "Farhi, Goldstone, Gutmann (2014)", _check_qaoa),
    KnownAnswerCase("VQE", "Peruzzo et al. (2014)", _check_vqe),
    KnownAnswerCase("HHL", "Harrow, Hassidim, Lloyd (2009)", _check_hhl),
]


def run_validation() -> list[tuple[KnownAnswerCase, Exception | None]]:
    """Run every case, returning `(case, error)` pairs — `error` is `None`
    on success, the raised exception otherwise (rather than stopping at
    the first failure)."""
    results: list[tuple[KnownAnswerCase, Exception | None]] = []
    for case in CASES:
        try:
            case.check()
            results.append((case, None))
        except Exception as error:  # noqa: BLE001 - intentionally broad, this is a report, not a re-raise
            results.append((case, error))
    return results


if __name__ == "__main__":
    for case, error in run_validation():
        status = "PASS" if error is None else f"FAIL ({error})"
        print(f"{case.algorithm} [{case.source}]: {status}")
