"""Circuit construction for Simon's algorithm.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister

from algorithms.simon.oracles import Oracle


def build_simon_circuit(n_qubits: int, oracle: Oracle) -> QuantumCircuit:
    """Build the circuit: `H^n` on the input register, apply
    `oracle.oracle_gate()`, `H^n` on the input register again, measure the
    input register only (the output register is never measured — its
    entanglement with the input is the mechanism, not something to read
    out)."""
    input_reg = QuantumRegister(n_qubits, name="x")
    output_reg = QuantumRegister(n_qubits, name="y")
    creg = ClassicalRegister(n_qubits, name="c")
    circuit = QuantumCircuit(input_reg, output_reg, creg, name="simon")

    circuit.h(input_reg)
    circuit.append(oracle.oracle_gate(), [*input_reg, *output_reg])
    circuit.h(input_reg)
    circuit.measure(input_reg, creg)
    return circuit
