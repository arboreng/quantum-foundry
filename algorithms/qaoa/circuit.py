"""Circuit construction for QAOA.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.qaoa.problems import Problem


def mixer_gate(n_qubits: int, beta: float) -> QuantumCircuit:
    """`exp(-i*beta*B)` for the mixer Hamiltonian `B = sum_i X_i`: one
    `RX(2*beta)` per qubit.

    Not yet implemented — see RFC-0008 milestone v0.2.
    """
    raise NotImplementedError


def build_qaoa_circuit(
    problem: Problem, gammas: list[float], betas: list[float]
) -> QuantumCircuit:
    """Build the QAOA circuit: `H^n` (uniform superposition), then
    `p = len(gammas)` layers of (`problem.cost_gate(gammas[l])`,
    `mixer_gate(n_qubits, betas[l])`), then measure.

    Not yet implemented — see RFC-0008 milestone v0.2.
    """
    raise NotImplementedError
