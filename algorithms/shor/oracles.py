"""Modular-multiplication oracles for Shor's order-finding circuit.

An `Oracle` supplies the controlled unitary `U^power |y> = |a^power * y mod N>`
that `circuit.build_order_finding_circuit` applies once per counting qubit.
`PermutationMatrixOracle` computes the exact permutation matrix for
`x -> a*x mod N` classically and embeds it as a `UnitaryGate`. This is correct
for arbitrary `N`/`a` (unlike per-N hand-derived tutorial circuits) but does
not decompose into elementary/reversible-arithmetic gates — see paper.md's
"Known simplifications". `GateDecomposedOracle` (RFC-0002) is a drop-in
replacement behind the same `Oracle` interface, built from actual reversible
adder circuits in `arithmetic.adders`.
"""

from math import gcd
from typing import Protocol

import numpy as np
from qiskit.circuit import Gate
from qiskit.circuit.library import UnitaryGate

from arithmetic.adders import controlled_mult_mod_N_gate


class Oracle(Protocol):
    """Supplies the controlled modular-multiplication gate for a given power."""

    num_ancilla_qubits: int
    """Extra scratch qubits (beyond 1 control + the work register) that
    `controlled_power_gate`'s returned gate expects, appended after the work
    register qubits. Zero for oracles (like `PermutationMatrixOracle`) that
    don't need any."""

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

    num_ancilla_qubits = 0

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


class GateDecomposedOracle:
    """`Oracle` backed by `arithmetic.adders.controlled_mult_mod_N_gate` —
    reversible modular multiplication built from Draper/Beauregard-style
    elementary-gate adders (RFC-0002), rather than a classically-computed
    dense unitary."""

    def __init__(self, a: int, N: int, num_qubits: int):
        self.a = a
        self.N = N
        self.num_qubits = num_qubits
        self.num_ancilla_qubits = num_qubits + 3
        self._gate_cache: dict[int, Gate] = {}

    def controlled_power_gate(self, power: int) -> Gate:
        if power not in self._gate_cache:
            a_power = pow(self.a, power, self.N)
            gate = controlled_mult_mod_N_gate(self.num_qubits, a_power, self.N)
            self._gate_cache[power] = gate
        return self._gate_cache[power]
