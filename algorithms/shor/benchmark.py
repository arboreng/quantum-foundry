"""Resource and performance benchmarks for Shor's algorithm.

Times each stage separately (oracle construction, QFT construction,
simulation, continued-fraction extraction, verification) rather than one
end-to-end `factor()` number, so regressions can be attributed to a specific
stage, and reports qubit/gate counts so the two oracles (RFC-0001's
`PermutationMatrixOracle`, RFC-0002's `GateDecomposedOracle`) can be compared
directly. See `benchmarks/shor.md` for a written-up comparison at N=15/21.

`GateDecomposedOracle` at N=21 takes on the order of 10 minutes per circuit
(confirmed during RFC-0002 development) — `run_benchmarks`'s defaults
deliberately exclude that combination; pass it explicitly if you want it.
"""

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

from qiskit import transpile

from algorithms.shor.circuit import build_order_finding_circuit
from algorithms.shor.execution import AerExecutor
from algorithms.shor.oracles import GateDecomposedOracle, Oracle, PermutationMatrixOracle
from arithmetic.qft import inverse_qft


@dataclass(frozen=True)
class BenchmarkResult:
    n: int
    oracle_name: str
    qubit_count: int
    gate_count: int
    circuit_depth: int
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


def _benchmark_single(
    n: int,
    executor: AerExecutor,
    oracle_cls: Callable[[int, int, int], Oracle],
) -> BenchmarkResult:
    start = time.perf_counter()
    a = _smallest_coprime_base(n)
    n_work = n.bit_length()
    n_count = 2 * n_work

    t0 = time.perf_counter()
    oracle = oracle_cls(a, n, n_work)
    for k in range(n_count):
        oracle.controlled_power_gate(2**k)
    oracle_construction_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    inverse_qft(n_count)
    qft_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    circuit = build_order_finding_circuit(n, a, n_count=n_count, oracle_cls=oracle_cls)
    transpiled = transpile(circuit, executor.backend)
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
        oracle_name=oracle_cls.__name__,
        qubit_count=circuit.num_qubits,
        gate_count=transpiled.size(),
        circuit_depth=transpiled.depth(),
        oracle_construction_seconds=oracle_construction_seconds,
        qft_seconds=qft_seconds,
        simulation_seconds=simulation_seconds,
        continued_fraction_seconds=continued_fraction_seconds,
        verification_seconds=verification_seconds,
        total_seconds=total_seconds,
    )


def run_benchmarks(
    ns: list[int] | None = None,
    oracle_classes: list[Callable[[int, int, int], Oracle]] | None = None,
) -> list[BenchmarkResult]:
    ns = ns if ns is not None else [15]
    if oracle_classes is None:
        oracle_classes = [PermutationMatrixOracle, GateDecomposedOracle]
    executor = AerExecutor()
    return [
        _benchmark_single(n, executor, oracle_cls) for n in ns for oracle_cls in oracle_classes
    ]


if __name__ == "__main__":
    for result in run_benchmarks():
        print(result)
