"""Resource and performance benchmarks for QAOA.

Unlike every other algorithm's benchmark (a single circuit's gate
count/depth/simulation time), QAOA's interesting cost is the classical
optimization loop: total wall-clock time across many circuit evaluations,
and how close the found cut gets to the true optimum (brute-forceable
classically for these small graphs).
"""

import itertools
import time
from dataclasses import dataclass

from scipy.optimize import minimize

from algorithms.qaoa.circuit import build_qaoa_circuit
from algorithms.qaoa.execution import AerExecutor
from algorithms.qaoa.implementation import expectation_value, solve_maxcut
from algorithms.qaoa.problems import MaxCutProblem


@dataclass(frozen=True)
class BenchmarkResult:
    n_qubits: int
    num_edges: int
    p: int
    found_cost: float
    optimal_cost: float
    total_seconds: float


def _brute_force_optimal_cost(n_qubits: int, edges: list[tuple[int, int]]) -> float:
    problem = MaxCutProblem(n_qubits, edges)
    return max(
        problem.cost_value("".join(bits))
        for bits in itertools.product("01", repeat=n_qubits)
    )


def _benchmark_single(n_qubits: int, edges: list[tuple[int, int]], p: int) -> BenchmarkResult:
    executor = AerExecutor()
    t0 = time.perf_counter()
    _, found_cost = solve_maxcut(n_qubits, edges, p=p, executor=executor)
    total_seconds = time.perf_counter() - t0

    return BenchmarkResult(
        n_qubits=n_qubits,
        num_edges=len(edges),
        p=p,
        found_cost=found_cost,
        optimal_cost=_brute_force_optimal_cost(n_qubits, edges),
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    triangle = [(0, 1), (1, 2), (0, 2)]
    square = [(0, 1), (1, 2), (2, 3), (3, 0)]
    return [
        _benchmark_single(3, triangle, p=1),
        _benchmark_single(3, triangle, p=2),
        _benchmark_single(4, square, p=1),
        _benchmark_single(4, square, p=2),
    ]


@dataclass(frozen=True)
class OptimizerComparisonResult:
    method: str
    trial: int
    found_cost: float
    optimal_cost: float
    nfev: int
    total_seconds: float


def _run_with_optimizer(
    n_qubits: int,
    edges: list[tuple[int, int]],
    p: int,
    method: str,
    trial: int,
    executor: AerExecutor,
) -> OptimizerComparisonResult:
    """Mirrors `implementation.solve_maxcut`'s objective exactly, but
    with `method` as a free parameter (`solve_maxcut` itself stays
    hardcoded to COBYLA, unchanged) — the whole point being to compare
    optimizers, not to add a new supported mode to the algorithm."""
    problem = MaxCutProblem(n_qubits, edges)

    def objective(params: list[float]) -> float:
        gammas, betas = list(params[:p]), list(params[p:])
        return -expectation_value(problem, gammas, betas, executor=executor, shots=1000)

    initial_guess = [0.5] * (2 * p)
    t0 = time.perf_counter()
    result = minimize(objective, initial_guess, method=method)
    total_seconds = time.perf_counter() - t0

    gammas, betas = list(result.x[:p]), list(result.x[p:])
    circuit = build_qaoa_circuit(problem, gammas, betas)
    counts = executor.run(circuit, 2000)
    bitstring = max(counts, key=lambda key: counts[key])

    return OptimizerComparisonResult(
        method=method,
        trial=trial,
        found_cost=problem.cost_value(bitstring),
        optimal_cost=_brute_force_optimal_cost(n_qubits, edges),
        nfev=result.nfev,
        total_seconds=total_seconds,
    )


def run_optimizer_comparison(trials: int = 5) -> list[OptimizerComparisonResult]:
    """Compares COBYLA (gradient-free — `solve_maxcut`'s default) against
    BFGS (gradient-based, using `scipy`'s own finite-difference gradient
    estimate, since no analytic gradient is supplied) on the same
    triangle MaxCut instance, across several independent trials (the
    objective is a finite-shots Monte Carlo estimate, so a single trial
    isn't representative for either optimizer)."""
    triangle = [(0, 1), (1, 2), (0, 2)]
    executor = AerExecutor()
    return [
        _run_with_optimizer(3, triangle, p=1, method=method, trial=trial, executor=executor)
        for method in ("COBYLA", "BFGS")
        for trial in range(trials)
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
    for comparison_result in run_optimizer_comparison():
        print(comparison_result)
