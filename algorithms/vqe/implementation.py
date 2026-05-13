"""End-to-end ground-state energy estimation using VQE.

See math.md for the theory and paper.md for the circuit this module
drives. Reuses `algorithms.qaoa`'s `scipy.optimize.minimize`-driven
classical-loop pattern, generalized from a diagonal cost function to an
arbitrary Pauli-sum Hamiltonian requiring per-term basis rotation.
"""

from scipy.optimize import minimize

from algorithms.vqe.circuit import group_measurement_circuit, measurement_circuit
from algorithms.vqe.execution import AerExecutor, Executor
from algorithms.vqe.hamiltonians import (
    Hamiltonian,
    TransverseFieldIsingHamiltonian,
    group_qwc_terms,
)


def expectation_value(
    hamiltonian: Hamiltonian,
    params: list[float],
    reps: int,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
) -> float:
    """Estimate `<psi(params)|hamiltonian|psi(params)>` by running one
    measurement circuit per non-identity Pauli term and combining
    counts-weighted `+-1` parities. A pure-identity term contributes its
    coefficient directly, with no circuit execution."""
    executor = executor if executor is not None else AerExecutor()
    total = 0.0
    for term in hamiltonian.terms:
        non_identity = [q for q, pauli in enumerate(term.paulis) if pauli != "I"]
        if not non_identity:
            total += term.coefficient
            continue

        circuit = measurement_circuit(hamiltonian.n_qubits, params, reps, term)
        counts = executor.run(circuit, shots)
        shots_total = sum(counts.values())

        term_expectation = 0.0
        for bitstring, count in counts.items():
            bits = [int(bitstring[hamiltonian.n_qubits - 1 - q]) for q in non_identity]
            parity = (-1) ** sum(bits)
            term_expectation += parity * count
        term_expectation /= shots_total

        total += term.coefficient * term_expectation
    return total


def expectation_value_grouped(
    hamiltonian: Hamiltonian,
    params: list[float],
    reps: int,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
) -> float:
    """Like `expectation_value`, but batches qubit-wise-commuting terms
    into shared circuit executions (`hamiltonians.group_qwc_terms`) —
    same result (up to shot noise), fewer circuit executions per call.
    A pure-identity term still contributes its coefficient directly, with
    no circuit execution."""
    executor = executor if executor is not None else AerExecutor()
    total = 0.0

    non_identity_terms = [
        term for term in hamiltonian.terms if any(pauli != "I" for pauli in term.paulis)
    ]
    total += sum(
        term.coefficient for term in hamiltonian.terms if all(p == "I" for p in term.paulis)
    )

    for group in group_qwc_terms(non_identity_terms):
        circuit = group_measurement_circuit(hamiltonian.n_qubits, params, reps, group)
        counts = executor.run(circuit, shots)
        shots_total = sum(counts.values())

        for term in group:
            non_identity = [q for q, pauli in enumerate(term.paulis) if pauli != "I"]
            term_expectation = 0.0
            for bitstring, count in counts.items():
                bits = [int(bitstring[hamiltonian.n_qubits - 1 - q]) for q in non_identity]
                parity = (-1) ** sum(bits)
                term_expectation += parity * count
            term_expectation /= shots_total
            total += term.coefficient * term_expectation

    return total


def solve_ground_state(
    hamiltonian: Hamiltonian,
    reps: int = 1,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
    final_shots: int = 2000,
) -> tuple[list[float], float]:
    """Approximate `hamiltonian`'s ground-state energy: optimize the
    ansatz parameters via `scipy.optimize.minimize` (COBYLA, matching
    RFC-0008), then return the optimized params and a final,
    higher-shot-count energy estimate."""
    executor = executor if executor is not None else AerExecutor()
    num_params = hamiltonian.n_qubits * (reps + 1)

    def objective(params: list[float]) -> float:
        return expectation_value(hamiltonian, list(params), reps, executor=executor, shots=shots)

    initial_guess = [0.5] * num_params
    result = minimize(objective, initial_guess, method="COBYLA")
    params = list(result.x)

    energy = expectation_value(
        hamiltonian, params, reps, executor=executor, shots=final_shots
    )
    return params, energy


def solve_ground_state_grouped(
    hamiltonian: Hamiltonian,
    reps: int = 1,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
    final_shots: int = 2000,
) -> tuple[list[float], float]:
    """Like `solve_ground_state`, but uses `expectation_value_grouped` for
    the classical optimization loop's objective — same optimization,
    fewer circuit executions per objective evaluation."""
    executor = executor if executor is not None else AerExecutor()
    num_params = hamiltonian.n_qubits * (reps + 1)

    def objective(params: list[float]) -> float:
        return expectation_value_grouped(
            hamiltonian, list(params), reps, executor=executor, shots=shots
        )

    initial_guess = [0.5] * num_params
    result = minimize(objective, initial_guess, method="COBYLA")
    params = list(result.x)

    energy = expectation_value_grouped(
        hamiltonian, params, reps, executor=executor, shots=final_shots
    )
    return params, energy


if __name__ == "__main__":
    chain = TransverseFieldIsingHamiltonian(2, j_coupling=1.0, h_field=0.5)
    print(solve_ground_state(chain))
    print(solve_ground_state_grouped(chain))
