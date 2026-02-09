"""Circuit execution backends.

`find_order` in implementation.py depends only on the `Executor` protocol, not
on Aer directly, so a future hardware backend (IBM, IonQ, noise-aware
simulation, ...) is a drop-in swap rather than a rewrite of the algorithm.
"""

from typing import Protocol

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.transpiler import CouplingMap
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


class ConstrainedAerExecutor:
    """Executor that transpiles against a connectivity- and basis-gate-
    constrained hardware model (RFC-0003's `compiler.targets`) before running
    on `AerSimulator`, so `factor`/`find_order` can be checked for
    correctness under the same routing overhead `compiler.transpilation`
    measures structurally."""

    name = "constrained_aer_simulator"

    def __init__(
        self,
        coupling_map: CouplingMap,
        basis_gates: list[str],
        optimization_level: int = 1,
    ) -> None:
        self.coupling_map = coupling_map
        self.basis_gates = basis_gates
        self.optimization_level = optimization_level
        self.backend = AerSimulator()

    def run(self, circuit: QuantumCircuit, shots: int) -> dict[str, int]:
        transpiled = transpile(
            circuit,
            coupling_map=self.coupling_map,
            basis_gates=self.basis_gates,
            optimization_level=self.optimization_level,
        )
        result = self.backend.run(transpiled, shots=shots).result()
        return result.get_counts()
