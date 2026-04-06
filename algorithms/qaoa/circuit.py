"""Circuit construction for QAOA.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.qaoa.problems import Problem


def mixer_gate(n_qubits: int, beta: float) -> QuantumCircuit:
    """`exp(-i*beta*B)` for the mixer Hamiltonian `B = sum_i X_i`: one
    `RX(2*beta)` per qubit."""
    circuit = QuantumCircuit(n_qubits, name=f"mixer({beta})")
    for q in range(n_qubits):
        circuit.rx(2 * beta, q)
    return circuit


def build_qaoa_circuit(
    problem: Problem, gammas: list[float], betas: list[float]
) -> QuantumCircuit:
    """Build the QAOA circuit: `H^n` (uniform superposition), then
    `p = len(gammas)` layers of (`problem.cost_gate(gammas[l])`,
    `mixer_gate(n_qubits, betas[l])`), then measure."""
    if len(gammas) != len(betas):
        raise ValueError("gammas and betas must have the same length")

    n = problem.n_qubits
    circuit = QuantumCircuit(n, n, name="qaoa")
    circuit.h(range(n))

    for gamma, beta in zip(gammas, betas, strict=True):
        circuit.append(problem.cost_gate(gamma), range(n))
        circuit.append(mixer_gate(n, beta).to_gate(label="mixer"), range(n))

    circuit.measure(range(n), range(n))
    return circuit
