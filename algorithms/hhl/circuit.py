"""Circuit construction for HHL.

See paper.md for the derivation this module implements.
"""

import math

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import RYGate

from algorithms.hhl.oracles import Oracle
from arithmetic.qft import inverse_qft


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
    ancilla (and the b-register)."""
    clock_reg = QuantumRegister(n_clock, name="clock")
    b_reg = QuantumRegister(oracle.num_qubits, name="b")
    ancilla_reg = QuantumRegister(1, name="ancilla")
    creg = ClassicalRegister(1 + oracle.num_qubits, name="c")
    circuit = QuantumCircuit(clock_reg, b_reg, ancilla_reg, creg, name="hhl")

    circuit.append(b_state_prep.to_gate(label="b_prep"), b_reg)

    # QPE: estimate A's eigenvalues onto the clock register, entangled
    # with the b-register's decomposition in A's eigenbasis.
    circuit.h(clock_reg)
    for k in range(n_clock):
        gate = oracle.controlled_power_gate(2**k)
        circuit.append(gate, [clock_reg[k], *b_reg])
    qft_dagger = inverse_qft(n_clock).to_gate(label="QFT_dagger")
    circuit.append(qft_dagger, clock_reg)

    # Multiplexed rotation: encode 1/lambda_k into the ancilla's |1>
    # amplitude for each clock-register branch k (k=0 left as identity,
    # avoiding division by the null eigenvalue).
    dim = 2**n_clock
    for k in range(1, dim):
        lambda_k = 2 * math.pi * k / (t * dim)
        theta_k = 2 * math.asin(c_constant / lambda_k)
        zero_bits = [i for i in range(n_clock) if not (k >> i) & 1]
        for i in zero_bits:
            circuit.x(clock_reg[i])
        circuit.append(
            RYGate(theta_k).control(n_clock, annotated=False), [*clock_reg, ancilla_reg[0]]
        )
        for i in zero_bits:
            circuit.x(clock_reg[i])

    # QPE's inverse: uncompute the clock register (exact, since t/n_clock
    # were chosen so A's eigenvalues land on exact n_clock-bit fractions).
    # The multiplexed rotation above only acts on the ancilla, so it
    # doesn't disturb the clock register and this uncomputation is
    # unaffected by it.
    circuit.append(qft_dagger.inverse(), clock_reg)
    for k in reversed(range(n_clock)):
        gate = oracle.controlled_power_gate(2**k)
        circuit.append(gate.inverse(), [clock_reg[k], *b_reg])
    circuit.h(clock_reg)

    circuit.measure(ancilla_reg, creg[0:1])
    circuit.measure(b_reg, creg[1:])
    return circuit
