"""Oracles for Simon's algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for a
function `f: {0,1}^n -> {0,1}^n` promised to be one-to-one or exactly
two-to-one with a hidden period `s`, that `circuit.build_simon_circuit`
applies between two layers of Hadamards on the input register.
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    n_qubits: int

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `2 * n_qubits` qubits (input register
        + output register, each `n_qubits` wide)."""
        ...


class LinearOracle:
    """`Oracle` for `f(x) = Mx` (matrix-vector product over GF(2)) for an
    `n x n` binary matrix `M` with kernel exactly `{0, s}` — efficient
    (O(n^2)-gate) and exact for the broad class of linear/affine
    two-to-one functions.

    Not yet implemented — see RFC-0006 milestone v0.2.
    """

    def __init__(self, s: str):
        self.s = s
        self.n_qubits = len(s)

    def oracle_gate(self) -> Gate:
        raise NotImplementedError


class PermutationOracle:
    """`Oracle` for an arbitrary two-to-one function with hidden period
    `s`, via an explicit lookup mapping each pair `{x, x XOR s}` to a
    unique label. General (any two-to-one function, not just linear ones)
    but exponential in gate count — small `n_qubits` only.

    Not yet implemented — see RFC-0006 milestone v0.2.
    """

    def __init__(self, s: str):
        self.s = s
        self.n_qubits = len(s)

    def oracle_gate(self) -> Gate:
        raise NotImplementedError
