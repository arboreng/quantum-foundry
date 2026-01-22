"""End-to-end integer factorization using Shor's algorithm.

See math.md for the number-theoretic reduction and paper.md for the circuit
this module drives. The pipeline is deliberately staged so each part is
independently testable:

    choose_base -> find_order (circuit -> executor -> phase -> continued
    fraction -> order) -> recover_factor -> retry
"""

import random
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt

from algorithms.shor.circuit import build_order_finding_circuit
from algorithms.shor.execution import AerExecutor, Executor
from algorithms.shor.oracles import Oracle, PermutationMatrixOracle


@dataclass(frozen=True)
class OrderFindingResult:
    """Outcome of one quantum order-finding attempt for `a` modulo `N`.

    Populated even on failure (`success=False`, `order=None`) so notebooks
    and visualizations can inspect what the circuit actually measured.
    """

    success: bool
    order: int | None
    measured_phase: float
    measured_bitstring: str
    continued_fraction: Fraction
    backend: str
    shots: int


def find_order(
    a: int,
    N: int,
    *,
    executor: Executor | None = None,
    shots: int = 1,
    oracle_cls: Callable[[int, int, int], Oracle] = PermutationMatrixOracle,
) -> OrderFindingResult:
    """Estimate the multiplicative order of `a` modulo `N` via quantum phase
    estimation on `build_order_finding_circuit`."""
    executor = executor if executor is not None else AerExecutor()
    circuit = build_order_finding_circuit(N, a, oracle_cls=oracle_cls)
    n_count = circuit.qregs[0].size

    counts = executor.run(circuit, shots)
    bitstring = max(counts, key=lambda key: counts[key])

    phase = int(bitstring, 2) / 2**n_count
    fraction = Fraction(phase).limit_denominator(N)
    order = fraction.denominator

    success = order > 0 and pow(a, order, N) == 1
    return OrderFindingResult(
        success=success,
        order=order if success else None,
        measured_phase=phase,
        measured_bitstring=bitstring,
        continued_fraction=fraction,
        backend=executor.name,
        shots=shots,
    )


def choose_base(n: int, rng: random.Random) -> int:
    """Pick a random candidate base `a` in `[2, n-1]`."""
    return rng.randint(2, n - 1)


def recover_factor(n: int, a: int, order: int) -> tuple[int, int] | None:
    """Attempt to extract a nontrivial factor pair of `n` from the order `r`
    of `a` modulo `n`. Returns `None` if this order doesn't yield one (the
    caller should retry with a different base)."""
    if order % 2 != 0:
        return None

    half_power = pow(a, order // 2, n)
    if half_power == n - 1:
        return None

    for candidate in (half_power - 1, half_power + 1):
        factor_guess = gcd(candidate, n)
        if 1 < factor_guess < n:
            other = n // factor_guess
            return min(factor_guess, other), max(factor_guess, other)
    return None


def _perfect_power_factor(n: int) -> tuple[int, int] | None:
    """Return `(p, n // p)` if `n = p**k` for some prime-power base `p`, else `None`."""
    for exponent in range(2, n.bit_length() + 1):
        base = round(n ** (1 / exponent))
        for candidate in (base - 1, base, base + 1):
            if candidate > 1 and candidate**exponent == n:
                return candidate, n // candidate
    return None


def factor(
    n: int,
    *,
    max_attempts: int = 20,
    rng: random.Random | None = None,
    executor: Executor | None = None,
    oracle_cls: Callable[[int, int, int], Oracle] = PermutationMatrixOracle,
) -> tuple[int, int]:
    """Factor composite integer `n` into two nontrivial factors using Shor's
    algorithm, with classical short-circuits for even `n` and perfect powers.
    """
    if n < 2:
        raise ValueError(f"n={n} must be >= 2")
    if isqrt(n) ** 2 == n:
        root = isqrt(n)
        return min(root, n // root), max(root, n // root)
    if n % 2 == 0:
        return min(2, n // 2), max(2, n // 2)

    perfect_power = _perfect_power_factor(n)
    if perfect_power is not None:
        p, q = perfect_power
        return min(p, q), max(p, q)

    rng = rng if rng is not None else random.Random()
    executor = executor if executor is not None else AerExecutor()

    for _ in range(max_attempts):
        a = choose_base(n, rng)
        g = gcd(a, n)
        if g > 1:
            return min(g, n // g), max(g, n // g)

        result = find_order(a, n, executor=executor, oracle_cls=oracle_cls)
        if not result.success or result.order is None:
            continue

        factors = recover_factor(n, a, result.order)
        if factors is not None:
            return factors

    raise RuntimeError(f"factor(n={n}) did not converge in {max_attempts} attempts")


if __name__ == "__main__":
    print(factor(15))
