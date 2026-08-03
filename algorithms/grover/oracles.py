"""Marking oracles for Grover's algorithm.

An `Oracle` supplies the phase-flip gate `|x> -> -|x>` for marked `x`,
identity otherwise, that `circuit.build_grover_circuit` applies once per
iteration alongside the diffusion operator.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit
from qiskit.circuit.library import ZGate


class Oracle(Protocol):
    """Supplies the phase-flip gate marking a set of target states."""

    def phase_flip_gate(self) -> Gate:
        """Return the gate implementing `|x> -> -|x>` for marked `x`."""
        ...


class MarkedBitstringOracle:
    """`Oracle` marking an explicit, arbitrary set of bitstrings via
    multi-controlled-Z gates.

    Bit-index convention matches measurement bitstrings: qubit `q`
    corresponds to the character at position `n_qubits - 1 - q` of a marked
    string (i.e. the same convention Qiskit's own `counts` dict keys use).
    """

    def __init__(self, n_qubits: int, marked: set[str]):
        if n_qubits < 1:
            raise ValueError("n_qubits must be positive")
        for m in marked:
            if len(m) != n_qubits:
                raise ValueError(f"marked bitstring {m!r} does not have length n_qubits={n_qubits}")
            if any(bit not in "01" for bit in m):
                raise ValueError(f"marked bitstring {m!r} must contain only 0 and 1")
        self.n_qubits = n_qubits
        self.marked = marked

    def phase_flip_gate(self) -> Gate:
        circuit = QuantumCircuit(self.n_qubits, name="oracle")
        for m in self.marked:
            zero_qubits = [q for q in range(self.n_qubits) if m[self.n_qubits - 1 - q] == "0"]
            for q in zero_qubits:
                circuit.x(q)
            if self.n_qubits == 1:
                circuit.z(0)
            else:
                circuit.append(
                    ZGate().control(self.n_qubits - 1, annotated=False), range(self.n_qubits)
                )
            for q in zero_qubits:
                circuit.x(q)
        return circuit.to_gate(label="oracle")
