"""Circuit construction for Grover's algorithm.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import ZGate

from algorithms.grover.oracles import Oracle


def diffusion_operator(n_qubits: int) -> QuantumCircuit:
    """The Grover diffusion operator: reflection about the uniform
    superposition's average amplitude.

    The matrix this actually produces is `I - 2|s><s|`, the negation of
    the textbook `2|s><s| - I`. The two are the same physical reflection
    and the global phase is unobservable for plain Grover search, but it
    becomes a real relative phase once this is applied *under control* —
    see `counting.count`, which corrects for it. See paper.md.
    """
    circuit = QuantumCircuit(n_qubits, name="diffusion")
    circuit.h(range(n_qubits))
    circuit.x(range(n_qubits))
    if n_qubits == 1:
        circuit.z(0)
    else:
        circuit.append(ZGate().control(n_qubits - 1, annotated=False), range(n_qubits))
    circuit.x(range(n_qubits))
    circuit.h(range(n_qubits))
    return circuit


def build_grover_circuit(n_qubits: int, oracle: Oracle, iterations: int) -> QuantumCircuit:
    """Build the full Grover circuit: uniform superposition, then
    `iterations` rounds of (oracle, diffusion), then measurement."""
    circuit = QuantumCircuit(n_qubits, n_qubits, name="grover")
    circuit.h(range(n_qubits))

    oracle_gate = oracle.phase_flip_gate()
    diffusion_gate = diffusion_operator(n_qubits).to_gate(label="diffusion")
    for _ in range(iterations):
        circuit.append(oracle_gate, range(n_qubits))
        circuit.append(diffusion_gate, range(n_qubits))

    circuit.measure(range(n_qubits), range(n_qubits))
    return circuit
