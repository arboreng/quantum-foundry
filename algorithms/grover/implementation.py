"""End-to-end unstructured search using Grover's algorithm.

See math.md for the amplitude-amplification theory and paper.md for the
circuit this module drives.
"""

import math

from algorithms.grover.circuit import build_grover_circuit
from algorithms.grover.execution import AerExecutor, Executor
from algorithms.grover.oracles import MarkedBitstringOracle


def _iteration_count(n_qubits: int, num_marked: int) -> int:
    """Optimal number of Grover iterations for a known number of marked
    items (see math.md): `round(pi/(4*theta) - 1/2)` for the rotation
    half-angle `theta` with `sin(theta) = sqrt(M/N)`.

    This is the exact maximizer of `sin((2k+1)*theta)**2`, not the
    small-angle approximation `(pi/4)*sqrt(N/M)`. The two agree once
    `M/N` is small, but the approximation over-rotates badly when it is
    not — at `n_qubits=2, M=1` it gives `k=2` (success probability
    `0.25`) where the exact count gives `k=1` (probability `1.0`), and at
    `n_qubits=2, M=3` it gives `k=1`, whose success probability is
    exactly `0`.
    """
    theta = math.asin(math.sqrt(num_marked / 2**n_qubits))
    return max(0, round(math.pi / (4 * theta) - 0.5))


def search(
    n_qubits: int,
    marked: set[str],
    *,
    executor: Executor | None = None,
    shots: int = 100,
    max_attempts: int = 20,
) -> str:
    """Find a marked bitstring among `2**n_qubits` possibilities.

    With the optimal iteration count the success probability per shot is
    high but not exactly 1 (over/under-rotation — see math.md), so this
    retries (fresh shots each time) up to `max_attempts` before raising.
    `max_attempts=20` rather than a smaller number specifically to cover the
    degenerate `n_qubits=1` case, where the per-shot success probability is
    exactly 0.5 (see math.md) — 5 attempts there fails ~3% of the time
    (`0.5**5`), a real flake observed in `tests/test_grover.py` during
    development; 20 attempts reduces that to `0.5**20 ~ 1e-6`.
    """
    if not marked:
        raise ValueError("marked must be non-empty")

    executor = executor if executor is not None else AerExecutor()
    oracle = MarkedBitstringOracle(n_qubits, marked)
    iterations = _iteration_count(n_qubits, len(marked))
    circuit = build_grover_circuit(n_qubits, oracle, iterations)

    for _ in range(max_attempts):
        counts = executor.run(circuit, shots)
        bitstring = max(counts, key=lambda key: counts[key])
        if bitstring in marked:
            return bitstring

    raise RuntimeError(f"search did not find a marked item in {max_attempts} attempts")


if __name__ == "__main__":
    print(search(3, {"101"}))
