"""Modular-multiplication oracles for Shor's order-finding circuit.

An `Oracle` supplies the controlled unitary `U^power |y> = |a^power * y mod N>`
that `circuit.build_order_finding_circuit` applies once per counting qubit.
`PermutationMatrixOracle` is the only implementation for now: it computes the
exact permutation matrix for `x -> a*x mod N` classically and embeds it as a
`UnitaryGate`. This is correct for arbitrary `N`/`a` (unlike per-N hand-derived
tutorial circuits) but does not decompose into elementary/reversible-arithmetic
gates — see paper.md's "Known simplifications". A future gate-decomposed
oracle (Beauregard/Cuccaro-style adders) is meant to be a drop-in replacement
behind this same `Oracle` interface.
"""

from math import gcd
from typing import Protocol

import numpy as np
from qiskit.circuit import Gate
from qiskit.circuit.library import UnitaryGate


class Oracle(Protocol):
    """Supplies the controlled modular-multiplication gate for a given power."""

    def controlled_power_gate(self, power: int) -> Gate:
        """Return the controlled gate implementing `|y> -> |a^power * y mod N>`."""
        ...


def _permutation_matrix(a: int, N: int, num_qubits: int) -> np.ndarray:
    """Build the `2**num_qubits x 2**num_qubits` permutation matrix for
    `x -> a*x mod N` on basis states `x < N`, identity on `x >= N`.

    `a` must be coprime to `N` for this map to be a bijection on `{0, ..., N-1}`.
    """
    if gcd(a, N) != 1:
        raise ValueError(f"a={a} is not coprime to N={N}")

    dim = 2**num_qubits
    if N > dim:
        raise ValueError(f"num_qubits={num_qubits} cannot represent N={N}")

    matrix = np.zeros((dim, dim))
    for x in range(dim):
        y = (a * x) % N if x < N else x
        matrix[y, x] = 1.0
    return matrix


class PermutationMatrixOracle:
    """`Oracle` backed by a classically-computed permutation matrix."""

    def __init__(self, a: int, N: int, num_qubits: int):
        self.a = a
        self.N = N
        self.num_qubits = num_qubits
        self._gate_cache: dict[int, Gate] = {}

    def controlled_power_gate(self, power: int) -> Gate:
        if power not in self._gate_cache:
            a_power = pow(self.a, power, self.N)
            matrix = _permutation_matrix(a_power, self.N, self.num_qubits)
            label = f"a^{power} mod {self.N}"
            gate = UnitaryGate(matrix, label=label).control(1)
            self._gate_cache[power] = gate
        return self._gate_cache[power]
