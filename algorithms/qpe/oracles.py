"""Oracles for Quantum Phase Estimation.

An `Oracle` supplies controlled powers of a unitary `U` (structurally the
same shape as `algorithms.shor.oracles.Oracle`, but for an arbitrary
unitary rather than modular multiplication specifically — see paper.md).
"""

import math
from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies the controlled gate for a power of some unitary `U`."""

    num_qubits: int

    def controlled_power_gate(self, power: int) -> Gate:
        """Return the controlled gate implementing `U^power`."""
        ...


class PhaseGateOracle:
    """`Oracle` for the single-qubit phase gate `U = P(2*pi*theta)`, whose
    eigenstate is `|1>` with eigenvalue `e^(2*pi*i*theta)`."""

    def __init__(self, theta: float):
        self.theta = theta
        self.num_qubits = 1

    def controlled_power_gate(self, power: int) -> Gate:
        circuit = QuantumCircuit(1, name=f"P({self.theta}*{power})")
        circuit.p(2 * math.pi * self.theta * power, 0)
        return circuit.to_gate(label="U^k").control(1)
