"""Resource and performance benchmarks for the Bernstein-Vazirani algorithm.

Times each stage separately (oracle construction, circuit construction,
simulation), mirroring `algorithms/shor/benchmark.py` and
`algorithms/grover/benchmark.py`.
"""

import time
from dataclasses import dataclass

from qiskit import transpile

from algorithms.bernstein_vazirani.circuit import build_oracle_query_circuit
from algorithms.bernstein_vazirani.execution import AerExecutor
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    gate_count: int
    circuit_depth: int
    oracle_construction_seconds: float
    circuit_construction_seconds: float
    simulation_seconds: float
    total_seconds: float


def _benchmark_single(s: str, executor: AerExecutor) -> BenchmarkResult:
    start = time.perf_counter()
    n_qubits = len(s)

    t0 = time.perf_counter()
    oracle = HiddenStringOracle(s)
    oracle.oracle_gate()
    oracle_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    circuit = build_oracle_query_circuit(n_qubits, oracle)
    circuit_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    transpiled = transpile(circuit, executor.backend)
    executor.run(circuit, shots=1)
    simulation_seconds = time.perf_counter() - t0

    total_seconds = time.perf_counter() - start
    return BenchmarkResult(
        n_qubits=n_qubits,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        oracle_construction_seconds=oracle_construction_seconds,
        circuit_construction_seconds=circuit_construction_seconds,
        simulation_seconds=simulation_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    executor = AerExecutor()
    return [_benchmark_single("1" * n, executor) for n in (3, 4, 6, 8, 10)]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
