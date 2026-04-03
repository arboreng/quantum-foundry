"""Circuit execution backends.

`implementation.py`'s optimization loop depends only on the `Executor`
protocol, not on Aer directly, so a future hardware or noise-aware backend
is a drop-in swap rather than a rewrite of the algorithm (same pattern as
`algorithms/shor/execution.py`, a separate module since each algorithm owns
its own).
"""

from typing import Protocol

from qiskit.circuit import QuantumCircuit


class Executor(Protocol):
    """Runs a circuit and returns measurement counts keyed by bitstring."""

    name: str

    def run(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]: ...


class AerExecutor:
    """Executor backed by `qiskit_aer.AerSimulator`.

    Not yet implemented — see RFC-0008 milestone v0.2.
    """

    name = "aer_simulator"

    def run(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        raise NotImplementedError
