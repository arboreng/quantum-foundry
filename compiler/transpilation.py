"""Hardware-aware transpilation reporting for RFC-0003.

`analyze_transpilation` wraps `qiskit.transpile()` against a connectivity-
constrained `CouplingMap` and reports the routing overhead (SWAP-gate count)
this introduces, alongside gate count and circuit depth, so it can be
compared across `optimization_level`s and against an unconstrained
transpilation (see `benchmarks/shor-transpilation.md`).
"""

from dataclasses import dataclass

from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.transpiler import CouplingMap


@dataclass(frozen=True)
class TranspilationReport:
    optimization_level: int
    qubit_count: int
    gate_count: int
    circuit_depth: int
    swap_count: int


def analyze_transpilation(
    circuit: QuantumCircuit,
    coupling_map: CouplingMap,
    basis_gates: list[str],
    optimization_level: int,
) -> TranspilationReport:
    """Two passes: first with `swap` kept in the basis, so routing-inserted
    swaps are counted rather than silently decomposed into `cx` during basis
    translation; then a second (layout-preserving, no re-routing) pass
    without `swap` in the basis, to get the final native-gate count and
    depth a real device would actually need to execute.
    """
    routed = transpile(
        circuit,
        coupling_map=coupling_map,
        basis_gates=[*basis_gates, "swap"],
        optimization_level=optimization_level,
    )
    swap_count = routed.count_ops().get("swap", 0)

    native = transpile(routed, basis_gates=basis_gates, optimization_level=0)
    return TranspilationReport(
        optimization_level=optimization_level,
        qubit_count=native.num_qubits,
        gate_count=native.size(),
        circuit_depth=native.depth(),
        swap_count=swap_count,
    )
