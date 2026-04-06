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

from algorithms.qaoa.execution import AerExecutor
from algorithms.qaoa.implementation import solve_maxcut
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


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
