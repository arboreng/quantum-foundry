"""End-to-end approximate combinatorial optimization using QAOA.

See math.md for the theory and paper.md for the circuit this module
drives. Uses `scipy.optimize.minimize` for the classical outer loop — a new
direct dependency; generic numerical optimization isn't quantum-specific,
unlike e.g. `algorithms.simon`'s from-scratch GF(2) linear algebra.
"""

from scipy.optimize import minimize

from algorithms.qaoa.circuit import build_qaoa_circuit
from algorithms.qaoa.execution import AerExecutor, Executor
from algorithms.qaoa.problems import MaxCutProblem, Problem


def expectation_value(
    problem: Problem,
    gammas: list[float],
    betas: list[float],
    *,
    executor: Executor | None = None,
    shots: int = 1000,
) -> float:
    """Average `problem.cost_value` over measured counts for the QAOA
    circuit with parameters `(gammas, betas)`."""
    executor = executor if executor is not None else AerExecutor()
    circuit = build_qaoa_circuit(problem, gammas, betas)
    counts = executor.run(circuit, shots)
    total = sum(counts.values())
    return sum(count * problem.cost_value(bitstring) for bitstring, count in counts.items()) / total


def solve_maxcut(
    n_qubits: int,
    edges: list[tuple[int, int]],
    *,
    p: int = 1,
    executor: Executor | None = None,
    shots: int = 1000,
    final_shots: int = 2000,
) -> tuple[str, float]:
    """Approximately solve MaxCut for the given graph: optimize QAOA
    parameters via `scipy.optimize.minimize` (COBYLA — gradient-free,
    robust to the sampling noise inherent in a finite-shots expectation
    value), then return the best-measured cut and its value."""
    executor = executor if executor is not None else AerExecutor()
    problem = MaxCutProblem(n_qubits, edges)

    def objective(params: list[float]) -> float:
        gammas, betas = list(params[:p]), list(params[p:])
        return -expectation_value(problem, gammas, betas, executor=executor, shots=shots)

    initial_guess = [0.5] * (2 * p)
    result = minimize(objective, initial_guess, method="COBYLA")
    gammas, betas = list(result.x[:p]), list(result.x[p:])

    circuit = build_qaoa_circuit(problem, gammas, betas)
    counts = executor.run(circuit, final_shots)
    bitstring = max(counts, key=lambda key: counts[key])
    return bitstring, problem.cost_value(bitstring)


if __name__ == "__main__":
    triangle = [(0, 1), (1, 2), (0, 2)]
    print(solve_maxcut(3, triangle))
