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


def _qubit_wise_commutes(term_a: PauliTerm, term_b: PauliTerm) -> bool:
    """Two Pauli terms qubit-wise commute if, at every qubit, their
    single-qubit operators are equal or at least one is `I` — the
    condition under which both can be read off the same computational-
    basis measurement (after a shared basis rotation), rather than
    needing separate circuit executions."""
    return all(
        pa == pb or pa == "I" or pb == "I"
        for pa, pb in zip(term_a.paulis, term_b.paulis, strict=True)
    )


def group_qwc_terms(terms: list[PauliTerm]) -> list[list[PauliTerm]]:
    """Greedily partition `terms` into qubit-wise-commuting groups: each
    group is measurable with a single circuit execution (one shared basis
    rotation per qubit, see `circuit.group_measurement_circuit`) instead
    of one execution per term. Not optimal (greedy, first-fit; minimizing
    the number of groups is itself an NP-hard graph-coloring problem) but
    exact — every term in a returned group is pairwise qubit-wise
    commuting with every other term in that group."""
    groups: list[list[PauliTerm]] = []
    for term in terms:
        for group in groups:
            if all(_qubit_wise_commutes(term, other) for other in group):
                group.append(term)
                break
        else:
            groups.append([term])
    return groups
