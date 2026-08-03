"""Oracles for the Bernstein-Vazirani algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for
some boolean function `f`, that `circuit.build_oracle_query_circuit`
(reused from `algorithms.deutsch_jozsa.circuit`) applies between two layers
of Hadamards.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `n_qubits + 1` qubits (input register
        + 1 ancilla)."""
        ...


class HiddenStringOracle:
    """`Oracle` for `f(x) = s.x mod 2` (inner product mod 2) for a hidden
    bitstring `s` — `O(n)` gates (one `CX` per set bit of `s`) for any `s`."""

    def __init__(self, s: str):
        if not s or any(bit not in "01" for bit in s):
            raise ValueError("s must be a non-empty binary string")
        self.s = s
        self.n_qubits = len(s)

    def oracle_gate(self) -> Gate:
        circuit = QuantumCircuit(self.n_qubits + 1, name=f"s={self.s}")
        for i, bit in enumerate(reversed(self.s)):
            if bit == "1":
                circuit.cx(i, self.n_qubits)
        return circuit.to_gate(label="oracle")
