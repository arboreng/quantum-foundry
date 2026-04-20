"""Oracles for HHL: a controlled-power-of-unitary abstraction for a
Hermitian matrix `A`'s time evolution `exp(-i*A*t)`, structurally the same
shape as `algorithms/qpe/oracles.py`'s `Oracle`.
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies controlled powers of `exp(-i*A*t)` for a Hermitian
    matrix `A`."""

    num_qubits: int

    def controlled_power_gate(self, power: int) -> Gate:
        """Return a controlled gate implementing `exp(-i*A*t*power)`."""
        ...


class DiagonalXOracle:
    """`Oracle` for `A = a*I + b*X` (arbitrary real `a`, `b`; eigenvalues
    `a+b` and `a-b`, always diagonal in the `|+>`/`|->` basis).

    Not yet implemented — see RFC-0010 milestone v0.2.
    """

    num_qubits = 1

    def __init__(self, a: float, b: float, t: float):
        self.a = a
        self.b = b
        self.t = t

    def controlled_power_gate(self, power: int) -> Gate:
        raise NotImplementedError
