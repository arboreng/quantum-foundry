"""Resource and performance benchmarks for HHL.

Since the demo instance's eigenvalues are exact dyadic fractions of
`2*pi/t` at n_clock=3 (see math.md), they stay exact at any larger
n_clock too (any exact eighth is also an exact sixteenth, thirty-second,
...) — so this benchmark holds the physical system (`A`, `t`) fixed and
scales only `n_clock`, isolating the multiplexed rotation's
`2**n_clock`-branch cost from any change in the underlying problem.

`c_constant` can't be held fixed across `n_clock`, though: the smallest
nonzero clock value (`k=1`) corresponds to a smaller eigenvalue as
`n_clock` grows (same `t`, more bits), so `c_constant` must shrink to stay
inside the multiplexed rotation's `arcsin` domain for every branch — see
"Reading this" in benchmarks/hhl.md for what that costs in practice.
"""

import math
import time
from dataclasses import dataclass

from qiskit import transpile
from qiskit.circuit import QuantumCircuit

from algorithms.hhl.circuit import build_hhl_circuit
from algorithms.hhl.execution import AerExecutor
from algorithms.hhl.implementation import solve_linear_system
from algorithms.hhl.oracles import DiagonalXOracle

_A, _B, _T = 1.0, 1.0 / 3.0, 3 * math.pi / 8
_SAFETY_MARGIN = 0.9


@dataclass(frozen=True)
class BenchmarkResult:
    n_clock: int
    c_constant: float
    gate_count: int
    circuit_depth: int
    success_probability: float
    total_seconds: float


def _benchmark_single(n_clock: int, executor: AerExecutor) -> BenchmarkResult:
    oracle = DiagonalXOracle(_A, _B, _T)
    b_state_prep = QuantumCircuit(1)

    dim = 2**n_clock
    lambda_min = 2 * math.pi / (_T * dim)
    c_constant = _SAFETY_MARGIN * lambda_min

    circuit = build_hhl_circuit(oracle, _T, n_clock, c_constant, b_state_prep)
    transpiled = transpile(circuit, executor.backend)

    t0 = time.perf_counter()
    success_probability, _ = solve_linear_system(
        oracle, _T, n_clock, c_constant, b_state_prep, executor=executor
    )
    total_seconds = time.perf_counter() - t0

    return BenchmarkResult(
        n_clock=n_clock,
        c_constant=c_constant,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        success_probability=success_probability,
        total_seconds=total_seconds,
    )


def run_benchmarks() -> list[BenchmarkResult]:
    """n_clock starts at 3: the demo instance's eigenvalues need at least
    3 bits to land on an exact binary fraction (see math.md)."""
    executor = AerExecutor()
    return [_benchmark_single(n, executor) for n in (3, 4, 5, 6)]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
