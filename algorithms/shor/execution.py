"""Circuit execution backends.

`find_order` in implementation.py depends only on the `Executor` protocol, not
on Aer directly, so a future hardware backend (IBM, IonQ, noise-aware
simulation, ...) is a drop-in swap rather than a rewrite of the algorithm.
"""

from typing import Protocol

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit_aer import AerSimulator


class Executor(Protocol):
    """Runs a circuit and returns measurement counts keyed by bitstring."""

    name: str

    def run(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]: ...


class AerExecutor:
    """Executor backed by `qiskit_aer.AerSimulator`."""

    name = "aer_simulator"

    def __init__(self) -> None:
        self.backend = AerSimulator()

    def run(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        transpiled = transpile(circuit, self.backend)
        result = self.backend.run(transpiled, shots=shots).result()
        return result.get_counts()
