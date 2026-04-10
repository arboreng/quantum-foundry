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
    Hamiltonian, where each `P_i` is one of `I`, `X`, `Y`, `Z`."""

    coefficient: float
    paulis: str


class Hamiltonian(Protocol):
    """Supplies a Pauli-string decomposition for a Hermitian operator."""

    n_qubits: int
    terms: list[PauliTerm]


class TransverseFieldIsingHamiltonian:
    """The 1D transverse-field Ising model on an open chain:
    `H = -J * sum_i Z_i Z_{i+1} - h * sum_i X_i`.

    Not yet implemented — see RFC-0009 milestone v0.2.
    """

    def __init__(self, n_qubits: int, j_coupling: float, h_field: float):
        self.n_qubits = n_qubits
        self.j_coupling = j_coupling
        self.h_field = h_field

    @property
    def terms(self) -> list[PauliTerm]:
        raise NotImplementedError
