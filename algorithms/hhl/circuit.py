"""Circuit construction for HHL.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.hhl.oracles import Oracle


def build_hhl_circuit(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
) -> QuantumCircuit:
    """Build the HHL circuit: `b_state_prep` on the b-register, QPE
    (`H^n_clock` -> controlled powers of `oracle` -> inverse QFT) on the
    clock register entangled with the b-register, a multiplexed `RY`
    rotation on the ancilla conditioned on the clock register's value,
    QPE's inverse (uncomputing the clock register), then measure the
    ancilla (and the b-register).

    Not yet implemented — see RFC-0010 milestone v0.2.
    """
    raise NotImplementedError
