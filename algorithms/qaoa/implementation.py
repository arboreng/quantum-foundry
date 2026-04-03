"""End-to-end approximate combinatorial optimization using QAOA.

See math.md for the theory and paper.md for the circuit this module
drives. Uses `scipy.optimize.minimize` for the classical outer loop — a new
direct dependency; generic numerical optimization isn't quantum-specific,
unlike e.g. `algorithms.simon`'s from-scratch GF(2) linear algebra.
"""

from algorithms.qaoa.problems import Problem


def expectation_value(
    problem: Problem, gammas: list[float], betas: list[float], shots: int = 1000
) -> float:
    """Average `problem.cost_value` over measured counts for the QAOA
    circuit with parameters `(gammas, betas)`.

    Not yet implemented — see RFC-0008 milestone v0.2.
    """
    raise NotImplementedError


def solve_maxcut(
    n_qubits: int, edges: list[tuple[int, int]], p: int = 1
) -> tuple[str, float]:
    """Approximately solve MaxCut for the given graph: optimize QAOA
    parameters via `scipy.optimize.minimize`, then return the best-measured
    cut and its value.

    Not yet implemented — see RFC-0008 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.qaoa.implementation is not yet implemented (RFC-0008 v0.2)")
