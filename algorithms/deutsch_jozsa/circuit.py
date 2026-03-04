"""Circuit construction for the Deutsch-Jozsa algorithm.

`build_oracle_query_circuit` is the shared `H^n -> oracle -> H^n -> measure`
primitive, reused verbatim by `algorithms.bernstein_vazirani.circuit`
(RFC-0005) — Deutsch-Jozsa is its canonical home since it's the historically
earlier / more foundational of the two.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.deutsch_jozsa.oracles import Oracle


def build_oracle_query_circuit(n_qubits: int, oracle: Oracle) -> QuantumCircuit:
    """Build the shared phase-kickback circuit: ancilla prepared in `|->`,
    `H` on the input register, apply `oracle.oracle_gate()`, `H` on the
    input register again, measure the input register.

    Not yet implemented — see RFC-0005 milestone v0.2.
    """
    raise NotImplementedError
