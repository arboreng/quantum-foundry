"""Marking oracles for Grover's algorithm.

An `Oracle` supplies the phase-flip gate `|x> -> -|x>` for marked `x`,
identity otherwise, that `circuit.build_grover_circuit` applies once per
iteration alongside the diffusion operator.
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies the phase-flip gate marking a set of target states."""

    def phase_flip_gate(self) -> Gate:
        """Return the gate implementing `|x> -> -|x>` for marked `x`."""
        ...


class MarkedBitstringOracle:
    """`Oracle` marking an explicit, arbitrary set of bitstrings via
    multi-controlled-Z gates. Not yet implemented — see RFC-0004 milestone
    v0.2."""

    def __init__(self, n_qubits: int, marked: set[str]):
        self.n_qubits = n_qubits
        self.marked = marked

    def phase_flip_gate(self) -> Gate:
        raise NotImplementedError
