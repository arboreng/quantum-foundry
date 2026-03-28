"""Resource and performance benchmarks for Quantum Phase Estimation.

Unlike every other algorithm's benchmark (which scales a search space or
oracle size), QPE's interesting axis is precision: how estimation error
shrinks as `n_count` grows, alongside the usual gate count/depth/time.
"""

import time
from dataclasses import dataclass

from qiskit import transpile
from qiskit.circuit import QuantumCircuit

from algorithms.qpe.circuit import build_qpe_circuit
from algorithms.qpe.execution import AerExecutor
from algorithms.qpe.implementation import estimate_phase
from algorithms.qpe.oracles import PhaseGateOracle


@dataclass(frozen=True)
class BenchmarkResult:
    n_count: int
    theta: float
    estimated_theta: float
    error: float
    gate_count: int
    circuit_depth: int
    estimate_phase_seconds: float


def _benchmark_single(n_count: int, theta: float, executor: AerExecutor) -> BenchmarkResult:
    oracle = PhaseGateOracle(theta)
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)

    circuit = build_qpe_circuit(n_count, oracle, eigenstate_prep)
    transpiled = transpile(circuit, executor.backend)

    t0 = time.perf_counter()
    estimated = estimate_phase(oracle, eigenstate_prep, n_count, executor=executor)
    estimate_phase_seconds = time.perf_counter() - t0

    return BenchmarkResult(
        n_count=n_count,
        theta=theta,
        estimated_theta=estimated,
        error=abs(estimated - theta),
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        estimate_phase_seconds=estimate_phase_seconds,
    )


def run_benchmarks(theta: float = 0.1) -> list[BenchmarkResult]:
    executor = AerExecutor()
    return [_benchmark_single(n, theta, executor) for n in (3, 5, 8, 10, 12)]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
