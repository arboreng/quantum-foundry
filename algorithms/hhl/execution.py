"""Circuit execution backends.

`implementation.py` depends only on the `Executor` protocol, not on Aer
directly, so a future hardware or noise-aware backend is a drop-in swap
rather than a rewrite of the algorithm (same pattern as
`algorithms/qpe/execution.py`, a separate module since each algorithm owns
its own).
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
