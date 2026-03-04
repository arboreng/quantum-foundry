"""Oracles for the Bernstein-Vazirani algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for
some boolean function `f`, that `circuit.build_oracle_query_circuit`
(reused from `algorithms.deutsch_jozsa.circuit`) applies between two layers
of Hadamards.
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `n_qubits + 1` qubits (input register
        + 1 ancilla)."""
        ...


class HiddenStringOracle:
    """`Oracle` for `f(x) = s.x mod 2` (inner product mod 2) for a hidden
    bitstring `s` — `O(n)` gates (one `CX` per set bit of `s`) for any `s`.

    Not yet implemented — see RFC-0005 milestone v0.2.
    """

    def __init__(self, s: str):
        self.s = s

    def oracle_gate(self) -> Gate:
        raise NotImplementedError
