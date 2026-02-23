"""Resource and performance benchmarks for Grover's algorithm.

Times each stage separately (oracle construction, diffusion-operator
construction, simulation), mirroring `algorithms/shor/benchmark.py`.
"""

import time
from dataclasses import dataclass

from qiskit import transpile

from algorithms.grover.circuit import build_grover_circuit, diffusion_operator
from algorithms.grover.execution import AerExecutor
from algorithms.grover.implementation import _iteration_count
from algorithms.grover.oracles import MarkedBitstringOracle


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    num_marked: int
    iterations: int
    gate_count: int
    circuit_depth: int
    oracle_construction_seconds: float
    diffusion_construction_seconds: float
    simulation_seconds: float
    total_seconds: float


def _benchmark_single(n_qubits: int, marked: set[str], executor: AerExecutor) -> BenchmarkResult:
    start = time.perf_counter()
    iterations = _iteration_count(n_qubits, len(marked))

    t0 = time.perf_counter()
    oracle = MarkedBitstringOracle(n_qubits, marked)
    oracle.phase_flip_gate()
    oracle_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    diffusion_operator(n_qubits)
    diffusion_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    circuit = build_grover_circuit(n_qubits, oracle, iterations)
    transpiled = transpile(circuit, executor.backend)
    executor.run(circuit, shots=100)
    simulation_seconds = time.perf_counter() - t0

    total_seconds = time.perf_counter() - start
    return BenchmarkResult(
        n_qubits=n_qubits,
        num_marked=len(marked),
        iterations=iterations,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        oracle_construction_seconds=oracle_construction_seconds,
        diffusion_construction_seconds=diffusion_construction_seconds,
        simulation_seconds=simulation_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    executor = AerExecutor()
    return [
        _benchmark_single(3, {"101"}, executor),
        _benchmark_single(4, {"0000"}, executor),
        _benchmark_single(6, {"000000"}, executor),
        _benchmark_single(8, {"00000000"}, executor),
        _benchmark_single(10, {"0000000000"}, executor),
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
