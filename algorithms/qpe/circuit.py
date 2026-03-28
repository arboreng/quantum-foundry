"""Circuit construction for Quantum Phase Estimation.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister

from algorithms.qpe.oracles import Oracle
from arithmetic.qft import inverse_qft


def build_qpe_circuit(
    n_count: int, oracle: Oracle, eigenstate_prep: QuantumCircuit
) -> QuantumCircuit:
    """Build the QPE circuit: `H` on every counting qubit, `eigenstate_prep`
    on the eigenstate register, controlled `oracle.controlled_power_gate(2**k)`
    per counting qubit, inverse QFT (`arithmetic.qft.inverse_qft`) on the
    counting register, measure the counting register.
    """
    count_reg = QuantumRegister(n_count, name="count")
    eigen_reg = QuantumRegister(oracle.num_qubits, name="eigen")
    creg = ClassicalRegister(n_count, name="c")
    circuit = QuantumCircuit(count_reg, eigen_reg, creg, name="qpe")

    circuit.h(count_reg)
    circuit.append(eigenstate_prep.to_gate(label="eigenstate_prep"), eigen_reg)

    for k in range(n_count):
        gate = oracle.controlled_power_gate(2**k)
        circuit.append(gate, [count_reg[k], *eigen_reg])

    circuit.append(inverse_qft(n_count).to_gate(label="QFT_dagger"), count_reg)
    circuit.measure(count_reg, creg)
    return circuit
