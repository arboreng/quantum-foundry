"""Circuit construction for Grover's algorithm.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.grover.oracles import Oracle


def diffusion_operator(n_qubits: int) -> QuantumCircuit:
    """The Grover diffusion operator: reflection about the uniform
    superposition's average amplitude.

    Not yet implemented — see RFC-0004 milestone v0.2.
    """
    raise NotImplementedError


def build_grover_circuit(n_qubits: int, oracle: Oracle, iterations: int) -> QuantumCircuit:
    """Build the full Grover circuit: uniform superposition, then
    `iterations` rounds of (oracle, diffusion), then measurement.

    Not yet implemented — see RFC-0004 milestone v0.2.
    """
    raise NotImplementedError
