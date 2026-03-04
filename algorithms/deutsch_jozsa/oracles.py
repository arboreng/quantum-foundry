"""Oracles for the Deutsch-Jozsa algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for
some boolean function `f`, that `circuit.build_oracle_query_circuit` applies
between two layers of Hadamards.
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `n_qubits + 1` qubits (input register
        + 1 ancilla)."""
        ...


class ConstantOracle:
    """`Oracle` for `f(x) = value` (0 or 1) for all `x`.

    Not yet implemented — see RFC-0005 milestone v0.2.
    """

    def __init__(self, n_qubits: int, value: int):
        self.n_qubits = n_qubits
        self.value = value

    def oracle_gate(self) -> Gate:
        raise NotImplementedError


class ParityOracle:
    """`Oracle` for `f(x) = XOR of x_i for i in subset` — an efficient
    (O(n)-gate), always-balanced linear function (for non-empty `subset`).

    Not yet implemented — see RFC-0005 milestone v0.2.
    """

    def __init__(self, n_qubits: int, subset: set[int]):
        self.n_qubits = n_qubits
        self.subset = subset

    def oracle_gate(self) -> Gate:
        raise NotImplementedError


class BalancedOracle:
    """`Oracle` for `f(x) = 1` iff `x` is in an explicit, arbitrary marked
    set of exactly half of all `2**n_qubits` bitstrings. Exact but
    exponential in gate count (mirrors
    `algorithms.shor.oracles.PermutationMatrixOracle`'s tradeoff).

    Not yet implemented — see RFC-0005 milestone v0.2.
    """

    def __init__(self, n_qubits: int, marked: set[str]):
        self.n_qubits = n_qubits
        self.marked = marked

    def oracle_gate(self) -> Gate:
        raise NotImplementedError
