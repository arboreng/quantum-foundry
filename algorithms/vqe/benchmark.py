"""Resource and performance benchmarks for VQE.

Like QAOA's, VQE's interesting cost is the classical optimization loop:
total wall-clock time across many circuit evaluations (one per
non-identity Pauli term, per optimizer iteration), and how close the found
energy gets to the true ground-state energy (exactly diagonalizable for
these small chains).
"""

import time
from dataclasses import dataclass

import numpy as np

from algorithms.vqe.execution import AerExecutor
from algorithms.vqe.hamiltonians import Hamiltonian, PauliTerm, TransverseFieldIsingHamiltonian
from algorithms.vqe.implementation import solve_ground_state

_PAULI_MATRICES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    reps: int
    found_energy: float
    exact_energy: float
    total_seconds: float


def _term_matrix(term: PauliTerm) -> np.ndarray:
    matrix = _PAULI_MATRICES[term.paulis[0]]
    for pauli in term.paulis[1:]:
        matrix = np.kron(matrix, _PAULI_MATRICES[pauli])
    return term.coefficient * matrix


def _exact_ground_state_energy(hamiltonian: Hamiltonian) -> float:
    dim = 2**hamiltonian.n_qubits
    matrix = np.zeros((dim, dim), dtype=complex)
    for term in hamiltonian.terms:
        matrix += _term_matrix(term)
    return float(np.min(np.linalg.eigvalsh(matrix)))


def _benchmark_single(hamiltonian: Hamiltonian, reps: int) -> BenchmarkResult:
    executor = AerExecutor()
    t0 = time.perf_counter()
    _, found_energy = solve_ground_state(hamiltonian, reps=reps, executor=executor)
    total_seconds = time.perf_counter() - t0

    return BenchmarkResult(
        n_qubits=hamiltonian.n_qubits,
        reps=reps,
        found_energy=found_energy,
        exact_energy=_exact_ground_state_energy(hamiltonian),
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    return [
        _benchmark_single(TransverseFieldIsingHamiltonian(2, 1.0, 0.5), reps=1),
        _benchmark_single(TransverseFieldIsingHamiltonian(2, 1.0, 0.5), reps=2),
        _benchmark_single(TransverseFieldIsingHamiltonian(3, 1.0, 0.5), reps=1),
        _benchmark_single(TransverseFieldIsingHamiltonian(3, 1.0, 0.5), reps=2),
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
