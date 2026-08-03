"""Circuit construction for HHL.

See paper.md for the derivation this module implements.
"""

import math

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import RYGate, ZGate

from algorithms.hhl.oracles import Oracle
from arithmetic.qft import inverse_qft


def _build_state_prep(
    clock_reg: QuantumRegister,
    b_reg: QuantumRegister,
    ancilla_reg: QuantumRegister,
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
) -> QuantumCircuit:
    """The "A" operator shared by `build_hhl_circuit` and
    `build_amplified_hhl_circuit`: `b_state_prep` on the b-register, QPE
    (`H^n_clock` -> controlled powers of `oracle` -> inverse QFT) on the
    clock register entangled with the b-register, a multiplexed `RY`
    rotation on the ancilla conditioned on the clock register's value,
    QPE's inverse (uncomputing the clock register) — everything up to,
    but not including, measurement."""
    if n_clock < 1:
        raise ValueError("n_clock must be positive")
    if t == 0:
        raise ValueError("t must be nonzero")
    if c_constant <= 0:
        raise ValueError("c_constant must be positive")
    if b_state_prep.num_qubits != oracle.num_qubits:
        raise ValueError(
            f"b_state_prep must act on {oracle.num_qubits} qubits, "
            f"got {b_state_prep.num_qubits}"
        )

    circuit = QuantumCircuit(clock_reg, b_reg, ancilla_reg, name="hhl_state_prep")

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
        signed_k = k if k < dim / 2 else k - dim
        lambda_k = 2 * math.pi * signed_k / (t * dim)
        ratio = c_constant / abs(lambda_k)
        if ratio > 1.0:
            raise ValueError(
                f"c_constant={c_constant} is too large for eigenvalue estimate "
                f"lambda_k={lambda_k}; require c_constant <= |lambda_k|"
            )
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

    return circuit


def build_hhl_circuit(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
) -> QuantumCircuit:
    """Build the HHL circuit: the "A" state-prep operator (see
    `_build_state_prep`), then measure the ancilla and the b-register."""
    clock_reg = QuantumRegister(n_clock, name="clock")
    b_reg = QuantumRegister(oracle.num_qubits, name="b")
    ancilla_reg = QuantumRegister(1, name="ancilla")
    creg = ClassicalRegister(1 + oracle.num_qubits, name="c")

    state_prep = _build_state_prep(
        clock_reg, b_reg, ancilla_reg, oracle, t, n_clock, c_constant, b_state_prep
    )
    circuit = QuantumCircuit(clock_reg, b_reg, ancilla_reg, creg, name="hhl")
    circuit.compose(state_prep, inplace=True)
    circuit.measure(ancilla_reg, creg[0:1])
    circuit.measure(b_reg, creg[1:])
    return circuit


def build_amplified_hhl_circuit(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
    num_iterations: int,
) -> QuantumCircuit:
    """Like `build_hhl_circuit`, but runs `num_iterations` rounds of
    amplitude amplification (generalized Grover, Brassard-Hoyer-Mosca-Tapp
    1998) before measuring, to boost the ancilla-`1` postselection success
    probability (see math.md's "Amplitude amplification" section).

    Each round applies `Q = A . S_0 . A^-1 . S_chi` to the state-prep
    operator `A` (`_build_state_prep`): `S_chi` (a `Z` on the ancilla —
    flips the sign of exactly the "good" ancilla-`1` subspace), `A^-1`,
    `S_0` (reflection about `|0...0>`, the same construction as
    `algorithms.grover.circuit.diffusion_operator`'s phase flip, applied
    to every qubit here rather than just the search register), then `A`
    again. See `implementation.optimal_amplification_iterations` for
    choosing `num_iterations` from an estimated success probability.
    """
    clock_reg = QuantumRegister(n_clock, name="clock")
    b_reg = QuantumRegister(oracle.num_qubits, name="b")
    ancilla_reg = QuantumRegister(1, name="ancilla")
    creg = ClassicalRegister(1 + oracle.num_qubits, name="c")

    if num_iterations < 0:
        raise ValueError("num_iterations must be non-negative")

    state_prep = _build_state_prep(
        clock_reg, b_reg, ancilla_reg, oracle, t, n_clock, c_constant, b_state_prep
    )
    all_qubits = [*clock_reg, *b_reg, *ancilla_reg]
    state_prep_gate = state_prep.to_gate(label="A")
    state_prep_dagger_gate = state_prep.inverse().to_gate(label="A_dagger")

    circuit = QuantumCircuit(clock_reg, b_reg, ancilla_reg, creg, name="hhl_amplified")
    circuit.compose(state_prep, inplace=True)

    for _ in range(num_iterations):
        circuit.z(ancilla_reg[0])
        circuit.append(state_prep_dagger_gate, all_qubits)
        circuit.x(all_qubits)
        if len(all_qubits) == 1:
            circuit.z(all_qubits[0])
        else:
            circuit.append(ZGate().control(len(all_qubits) - 1, annotated=False), all_qubits)
        circuit.x(all_qubits)
        circuit.append(state_prep_gate, all_qubits)

    circuit.measure(ancilla_reg, creg[0:1])
    circuit.measure(b_reg, creg[1:])
    return circuit
