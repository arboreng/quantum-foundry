"""Circuit construction for Quantum Phase Estimation.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.qpe.oracles import Oracle


def build_qpe_circuit(
    n_count: int, oracle: Oracle, eigenstate_prep: QuantumCircuit
) -> QuantumCircuit:
    """Build the QPE circuit: `H` on every counting qubit, `eigenstate_prep`
    on the eigenstate register, controlled `oracle.controlled_power_gate(2**k)`
    per counting qubit, inverse QFT (`arithmetic.qft.inverse_qft`) on the
    counting register, measure the counting register.

    Not yet implemented — see RFC-0007 milestone v0.2.
    """
    raise NotImplementedError
