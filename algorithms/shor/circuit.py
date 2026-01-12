"""Circuit construction for Shor's algorithm.

See paper.md for the derivation this module implements.
"""

from qiskit import QuantumCircuit


def build_shor_circuit(n: int, a: int) -> QuantumCircuit:
    """Build the full Shor circuit for factoring `n` using base `a`.

    Not yet implemented — see RFC-0001 milestone v0.2.
    """
    raise NotImplementedError
