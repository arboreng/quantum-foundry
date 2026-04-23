"""Oracles for HHL: a controlled-power-of-unitary abstraction for a
Hermitian matrix `A`'s time evolution `exp(i*A*t)`, structurally the same
shape as `algorithms/qpe/oracles.py`'s `Oracle`.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies controlled powers of `exp(i*A*t)` for a Hermitian
    matrix `A`."""

    num_qubits: int

    def controlled_power_gate(self, power: int) -> Gate:
        """Return a controlled gate implementing `exp(i*A*t*power)`."""
        ...


class DiagonalXOracle:
    """`Oracle` for `A = a*I + b*X` (arbitrary real `a`, `b`; eigenvalues
    `a+b` (eigenvector `|+>`) and `a-b` (eigenvector `|->`)).

    Since `I` and `X` commute, `exp(i*A*t*power)` factors exactly into a
    global phase `exp(i*a*t*power)` times `exp(i*b*t*power*X)` — no
    Trotterization needed.
    """

    def __init__(self, a: float, b: float, t: float):
        self.a = a
        self.b = b
        self.t = t
        self.num_qubits = 1

    def controlled_power_gate(self, power: int) -> Gate:
        circuit = QuantumCircuit(1, name=f"U^{power}")
        circuit.global_phase = self.a * self.t * power
        circuit.rx(-2 * self.b * self.t * power, 0)
        return circuit.to_gate(label="U^k").control(1)
