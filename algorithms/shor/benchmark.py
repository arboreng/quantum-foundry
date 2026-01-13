"""Resource and performance benchmarks for Shor's algorithm.

Times each stage separately (oracle construction, QFT construction,
simulation, continued-fraction extraction, verification) rather than one
end-to-end `factor()` number, so regressions can be attributed to a specific
stage. See RFC-0001 milestone v0.5 for when this becomes load-bearing (CI
regression tracking, cross-algorithm comparison under `benchmarks/`).
"""

import math
import time
from dataclasses import dataclass
from fractions import Fraction

from algorithms.shor.circuit import build_order_finding_circuit, inverse_qft
from algorithms.shor.execution import AerExecutor
from algorithms.shor.oracles import PermutationMatrixOracle


@dataclass(frozen=True)
class BenchmarkResult:
    n: int
    oracle_construction_seconds: float
    qft_seconds: float
    simulation_seconds: float
    continued_fraction_seconds: float
    verification_seconds: float
    total_seconds: float


def _smallest_coprime_base(n: int) -> int:
    a = 2
    while math.gcd(a, n) != 1:
        a += 1
    return a


def _benchmark_single(n: int, executor: AerExecutor) -> BenchmarkResult:
    start = time.perf_counter()
    a = _smallest_coprime_base(n)
    n_work = n.bit_length()
    n_count = 2 * n_work

    t0 = time.perf_counter()
    oracle = PermutationMatrixOracle(a, n, n_work)
    for k in range(n_count):
        oracle.controlled_power_gate(2**k)
    oracle_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    inverse_qft(n_count)
    qft_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    circuit = build_order_finding_circuit(n, a, n_count=n_count)
    counts = executor.run(circuit, shots=1)
    simulation_seconds = time.perf_counter() - t0

    bitstring = max(counts, key=lambda key: counts[key])
    t0 = time.perf_counter()
    phase = int(bitstring, 2) / 2**n_count
    order = Fraction(phase).limit_denominator(n).denominator
    continued_fraction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    pow(a, order, n)
    verification_seconds = time.perf_counter() - t0

    total_seconds = time.perf_counter() - start
    return BenchmarkResult(
        n=n,
        oracle_construction_seconds=oracle_construction_seconds,
        qft_seconds=qft_seconds,
        simulation_seconds=simulation_seconds,
        continued_fraction_seconds=continued_fraction_seconds,
        verification_seconds=verification_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks(ns: list[int] | None = None) -> list[BenchmarkResult]:
    ns = ns if ns is not None else [15, 21]
    executor = AerExecutor()
    return [_benchmark_single(n, executor) for n in ns]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
