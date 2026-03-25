"""Oracles for Quantum Phase Estimation.

An `Oracle` supplies controlled powers of a unitary `U` (structurally the
same shape as `algorithms.shor.oracles.Oracle`, but for an arbitrary
unitary rather than modular multiplication specifically — see paper.md).
"""

from typing import Protocol

from qiskit.circuit import Gate


class Oracle(Protocol):
    """Supplies the controlled gate for a power of some unitary `U`."""

    num_qubits: int

    def controlled_power_gate(self, power: int) -> Gate:
        """Return the controlled gate implementing `U^power`."""
        ...


class PhaseGateOracle:
    """`Oracle` for the single-qubit phase gate `U = P(2*pi*theta)`, whose
    eigenstate is `|1>` with eigenvalue `e^(2*pi*i*theta)`.

    Not yet implemented — see RFC-0007 milestone v0.2.
    """

    def __init__(self, theta: float):
        self.theta = theta
        self.num_qubits = 1

    def controlled_power_gate(self, power: int) -> Gate:
        raise NotImplementedError
