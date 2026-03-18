"""Circuit construction for Simon's algorithm.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.simon.oracles import Oracle


def build_simon_circuit(n_qubits: int, oracle: Oracle) -> QuantumCircuit:
    """Build the circuit: `H^n` on the input register, apply
    `oracle.oracle_gate()`, `H^n` on the input register again, measure the
    input register only (the output register is never measured).

    Not yet implemented — see RFC-0006 milestone v0.2.
    """
    raise NotImplementedError
