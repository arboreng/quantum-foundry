"""Resource and performance benchmarks for the Deutsch-Jozsa algorithm.

Times each stage separately (oracle construction, circuit construction,
simulation), mirroring `algorithms/shor/benchmark.py` and
`algorithms/grover/benchmark.py`.
"""

import time
from dataclasses import dataclass

from qiskit import transpile

from algorithms.deutsch_jozsa.circuit import build_oracle_query_circuit
from algorithms.deutsch_jozsa.execution import AerExecutor
from algorithms.deutsch_jozsa.oracles import Oracle, ParityOracle


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    oracle_name: str
    gate_count: int
    circuit_depth: int
    oracle_construction_seconds: float
    circuit_construction_seconds: float
    simulation_seconds: float
    total_seconds: float


def _benchmark_single(n_qubits: int, oracle: Oracle, executor: AerExecutor) -> BenchmarkResult:
    start = time.perf_counter()

    t0 = time.perf_counter()
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
        oracle_name=type(oracle).__name__,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        oracle_construction_seconds=oracle_construction_seconds,
        circuit_construction_seconds=circuit_construction_seconds,
        simulation_seconds=simulation_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    executor = AerExecutor()
    return [
        _benchmark_single(n, ParityOracle(n, {0}), executor) for n in (3, 4, 6, 8, 10)
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
