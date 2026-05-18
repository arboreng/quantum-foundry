"""Semiclassical (Kitaev iterative) phase estimation: estimates the same
phase as `implementation.estimate_phase`, using a single reused ancilla
qubit and classical feedback between rounds, instead of `n_count`
ancillas and a coherent inverse QFT.

The round order and feedback-angle formula below are derived directly
from the eigenvalue equation `U^power|psi> = e^(2*pi*i*theta*power)|psi>`
(not from a memorized textbook statement of Kitaev's algorithm, and not
from tracing `arithmetic.qft.inverse_qft`'s gate-by-gate structure — an
earlier attempt at the latter got the bit order backwards and was caught
by cross-checking against `implementation.estimate_phase`, see math.md)
— see `tests/test_semiclassical.py` for that empirical check.
"""

import math

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister

from algorithms.qpe.execution import AerExecutor, Executor
from algorithms.qpe.oracles import Oracle


def _round_circuit(
    oracle: Oracle, eigenstate_prep: QuantumCircuit, power: int, feedback_angle: float
) -> QuantumCircuit:
    """One round: a fresh eigenstate-register preparation (equivalent to
    letting it persist across rounds, since only the ancilla is ever
    measured — see math.md), a single ancilla in `|0>`, `H`, controlled
    `U^power`, the classical feedback correction `P(feedback_angle)`, `H`
    again, then measure the ancilla."""
    ancilla = QuantumRegister(1, name="ancilla")
    eigen_reg = QuantumRegister(oracle.num_qubits, name="eigen")
    creg = ClassicalRegister(1, name="c")
    circuit = QuantumCircuit(ancilla, eigen_reg, creg, name="iterative_qpe_round")

    circuit.append(eigenstate_prep.to_gate(label="eigenstate_prep"), eigen_reg)
    circuit.h(ancilla)
    gate = oracle.controlled_power_gate(power)
    circuit.append(gate, [ancilla[0], *eigen_reg])
    circuit.p(feedback_angle, ancilla[0])
    circuit.h(ancilla)
    circuit.measure(ancilla, creg)
    return circuit


def estimate_phase_semiclassical(
    oracle: Oracle,
    eigenstate_prep: QuantumCircuit,
    n_count: int,
    *,
    executor: Executor | None = None,
    shots: int = 1,
) -> float:
    """Like `implementation.estimate_phase`, but uses a single ancilla
    reused `n_count` times with classical feedback between rounds
    (Kitaev's iterative phase estimation), instead of `n_count` ancillas
    and a coherent inverse QFT. Round `j` uses power `2**(n_count-1-j)`
    (the *largest* power first) and measures theta's bit at weight
    `2**(j - n_count)` — so round `0` (largest power) measures theta's
    *least* significant bit, and the last round (power `2**0`) measures
    its most significant bit, each round's feedback angle built from all
    previously-measured (less significant) bits' contributions at the
    current power (see math.md for the derivation). Each round takes the
    majority bit over `shots` repetitions before feeding it forward, for
    robustness on instances whose phase isn't an exact binary fraction."""
    executor = executor if executor is not None else AerExecutor()
    measured_bits: list[int] = []

    for j in range(n_count):
        power = 2 ** (n_count - 1 - j)
        feedback_angle = -math.pi * sum(
            bit / 2 ** (j - j_prime) for j_prime, bit in enumerate(measured_bits)
        )
        circuit = _round_circuit(oracle, eigenstate_prep, power, feedback_angle)
        counts = executor.run(circuit, shots)
        bitstring = max(counts, key=lambda key: counts[key])
        measured_bits.append(int(bitstring))

    return sum(bit * 2 ** (j - n_count) for j, bit in enumerate(measured_bits))


if __name__ == "__main__":
    from algorithms.qpe.oracles import PhaseGateOracle

    demo_eigenstate_prep = QuantumCircuit(1)
    demo_eigenstate_prep.x(0)
    print(estimate_phase_semiclassical(PhaseGateOracle(0.25), demo_eigenstate_prep, n_count=3))
