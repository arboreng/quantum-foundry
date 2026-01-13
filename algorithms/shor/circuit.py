"""Circuit construction for Shor's algorithm: a from-scratch QFT plus the
quantum phase estimation circuit used for order finding.

See paper.md for the derivation this module implements.
"""

import math
from collections.abc import Callable

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister

from algorithms.shor.oracles import Oracle, PermutationMatrixOracle


def qft(num_qubits: int) -> QuantumCircuit:
    """Quantum Fourier Transform on `num_qubits`, built from H, controlled-phase,
    and swap gates (not `qiskit.circuit.library.QFT`)."""
    circuit = QuantumCircuit(num_qubits, name="QFT")
    for target in reversed(range(num_qubits)):
        circuit.h(target)
        for control in range(target):
            angle = math.pi / 2 ** (target - control)
            circuit.cp(angle, control, target)
    for i in range(num_qubits // 2):
        circuit.swap(i, num_qubits - 1 - i)
    return circuit


def inverse_qft(num_qubits: int) -> QuantumCircuit:
    """Inverse Quantum Fourier Transform, built directly (not via `qft(...).inverse()`)."""
    circuit = QuantumCircuit(num_qubits, name="QFT_dagger")
    for i in range(num_qubits // 2):
        circuit.swap(i, num_qubits - 1 - i)
    for target in range(num_qubits):
        for control in reversed(range(target)):
            angle = -math.pi / 2 ** (target - control)
            circuit.cp(angle, control, target)
        circuit.h(target)
    return circuit


def build_order_finding_circuit(
    N: int,
    a: int,
    n_count: int | None = None,
    oracle_cls: Callable[[int, int, int], Oracle] = PermutationMatrixOracle,
) -> QuantumCircuit:
    """Build the quantum phase estimation circuit that estimates the phase
    `s/r` for the order `r` of `a` modulo `N`.

    Counting register (size `n_count`, default `2 * N.bit_length()`) is put in
    superposition and controls successive powers `a^(2**k) mod N` of the
    modular-multiplication oracle applied to the work register (size
    `N.bit_length()`, initialized to `|1>`). The counting register is then
    passed through `inverse_qft` and measured.
    """
    if math.gcd(a, N) != 1:
        raise ValueError(f"a={a} is not coprime to N={N}")

    n_work = N.bit_length()
    if n_count is None:
        n_count = 2 * n_work

    count_reg = QuantumRegister(n_count, name="count")
    work_reg = QuantumRegister(n_work, name="work")
    creg = ClassicalRegister(n_count, name="c")
    circuit = QuantumCircuit(count_reg, work_reg, creg, name=f"order_finding(N={N},a={a})")

    circuit.x(work_reg[0])  # work register := |1>
    circuit.h(count_reg)

    oracle = oracle_cls(a, N, n_work)
    for k in range(n_count):
        gate = oracle.controlled_power_gate(2**k)
        circuit.append(gate, [count_reg[k], *work_reg])

    circuit.append(inverse_qft(n_count).to_gate(label="QFT_dagger"), count_reg)
    circuit.measure(count_reg, creg)
    return circuit
