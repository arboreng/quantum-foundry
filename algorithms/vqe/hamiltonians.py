"""Hamiltonians for VQE.

A `Hamiltonian` supplies its Pauli-string decomposition (`terms`), used by
`implementation.py`'s `expectation_value` to compute `<psi|H|psi>` from
per-term measurement circuits.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PauliTerm:
    """One term `coefficient * P_0 (x) P_1 (x) ... (x) P_{n-1}` of a
    Hamiltonian, where each `P_i` is one of `I`, `X`, `Y`, `Z`.

    Unlike a measurement bitstring, `paulis[q]` directly indexes qubit `q`
    (no bit-reversal) — this is an operator specification, not a measured
    outcome.
    """

    coefficient: float
    paulis: str


class Hamiltonian(Protocol):
    """Supplies a Pauli-string decomposition for a Hermitian operator."""

    n_qubits: int

    @property
    def terms(self) -> list[PauliTerm]: ...


class TransverseFieldIsingHamiltonian:
    """The 1D transverse-field Ising model on an open chain:
    `H = -J * sum_i Z_i Z_{i+1} - h * sum_i X_i`."""

    def __init__(self, n_qubits: int, j_coupling: float, h_field: float):
        self.n_qubits = n_qubits
        self.j_coupling = j_coupling
        self.h_field = h_field

    @property
    def terms(self) -> list[PauliTerm]:
        terms = []
        for i in range(self.n_qubits - 1):
            paulis = ["I"] * self.n_qubits
            paulis[i] = "Z"
            paulis[i + 1] = "Z"
            terms.append(PauliTerm(coefficient=-self.j_coupling, paulis="".join(paulis)))
        for i in range(self.n_qubits):
            paulis = ["I"] * self.n_qubits
            paulis[i] = "X"
            terms.append(PauliTerm(coefficient=-self.h_field, paulis="".join(paulis)))
        return terms
