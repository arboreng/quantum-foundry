"""Resource and performance benchmarks for Simon's algorithm.

Times each stage separately (oracle construction, circuit construction, the
full find_hidden_period call — which itself loops running the circuit
until enough independent equations are collected, unlike every other
algorithm's single-shot or fixed-shots benchmark), mirroring
`algorithms/shor/benchmark.py`.
"""

import time
from dataclasses import dataclass

from qiskit import transpile

from algorithms.simon.circuit import build_simon_circuit
from algorithms.simon.execution import AerExecutor
from algorithms.simon.implementation import find_hidden_period
from algorithms.simon.oracles import LinearOracle, Oracle


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    oracle_name: str
    gate_count: int
    circuit_depth: int
    oracle_construction_seconds: float
    circuit_construction_seconds: float
    find_hidden_period_seconds: float
    total_seconds: float


def _benchmark_single(n_qubits: int, oracle: Oracle, executor: AerExecutor) -> BenchmarkResult:
    start = time.perf_counter()

    t0 = time.perf_counter()
    oracle.oracle_gate()
    oracle_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    circuit = build_simon_circuit(n_qubits, oracle)
    transpiled = transpile(circuit, executor.backend)
    circuit_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    find_hidden_period(n_qubits, oracle, executor=executor)
    find_hidden_period_seconds = time.perf_counter() - t0

    total_seconds = time.perf_counter() - start
    return BenchmarkResult(
        n_qubits=n_qubits,
        oracle_name=type(oracle).__name__,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        oracle_construction_seconds=oracle_construction_seconds,
        circuit_construction_seconds=circuit_construction_seconds,
        find_hidden_period_seconds=find_hidden_period_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    executor = AerExecutor()
    return [_benchmark_single(n, LinearOracle("1" * n), executor) for n in (3, 4, 6, 8, 10)]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
