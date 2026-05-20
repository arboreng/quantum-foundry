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


@dataclass(frozen=True)
class PrecisionConfidenceResult:
    """Empirical success probability of landing within `1/2**n_target` of
    `theta`, using `n_target + extra_qubits` counting qubits — the
    "precision/confidence" relationship math.md describes qualitatively
    (each extra qubit roughly doubles the failure probability's
    complement), measured here across many independent trials rather
    than the single-draw error `BenchmarkResult` tracks."""

    n_target: int
    extra_qubits: int
    n_count: int
    trials: int
    successes: int
    empirical_success_probability: float


def _run_precision_confidence_trials(
    theta: float, n_target: int, extra_qubits: int, trials: int, executor: AerExecutor
) -> PrecisionConfidenceResult:
    n_count = n_target + extra_qubits
    tolerance = 1 / 2**n_target
    oracle = PhaseGateOracle(theta)
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)

    successes = 0
    for _ in range(trials):
        estimated = estimate_phase(oracle, eigenstate_prep, n_count, executor=executor)
        if abs(estimated - theta) <= tolerance:
            successes += 1

    return PrecisionConfidenceResult(
        n_target=n_target,
        extra_qubits=extra_qubits,
        n_count=n_count,
        trials=trials,
        successes=successes,
        empirical_success_probability=successes / trials,
    )


def run_precision_confidence_analysis(
    theta: float = 0.1, n_target: int = 4, trials: int = 300
) -> list[PrecisionConfidenceResult]:
    """For a fixed target precision `n_target` (tolerance `1/2**n_target`),
    measure how the empirical probability of landing within that
    tolerance changes as `extra_qubits` (0-4) are added on top of
    `n_target` — the "confidence" half of math.md's precision/confidence
    claim, which `BenchmarkResult`'s single-draw error doesn't capture."""
    executor = AerExecutor()
    return [
        _run_precision_confidence_trials(theta, n_target, extra_qubits, trials, executor)
        for extra_qubits in range(5)
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
    for precision_result in run_precision_confidence_analysis():
        print(precision_result)
