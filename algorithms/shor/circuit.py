"""Circuit construction for Shor's algorithm: the quantum phase estimation
circuit used for order finding, built on the shared QFT in arithmetic/.

See paper.md for the derivation this module implements.
"""

import math
from collections.abc import Callable

from qiskit.circuit import AncillaRegister, ClassicalRegister, QuantumCircuit, QuantumRegister

from algorithms.shor.oracles import Oracle, PermutationMatrixOracle
from arithmetic.qft import inverse_qft


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

    oracle = oracle_cls(a, N, n_work)

    count_reg = QuantumRegister(n_count, name="count")
    work_reg = QuantumRegister(n_work, name="work")
    creg = ClassicalRegister(n_count, name="c")
    registers: list[QuantumRegister] = [count_reg, work_reg]
    ancilla_reg = None
    if oracle.num_ancilla_qubits > 0:
        ancilla_reg = AncillaRegister(oracle.num_ancilla_qubits, name="anc")
        registers.append(ancilla_reg)
    circuit = QuantumCircuit(*registers, creg, name=f"order_finding(N={N},a={a})")

    circuit.x(work_reg[0])  # work register := |1>
    circuit.h(count_reg)

    for k in range(n_count):
        gate = oracle.controlled_power_gate(2**k)
        qargs = [count_reg[k], *work_reg]
        if ancilla_reg is not None:
            qargs += list(ancilla_reg)
        circuit.append(gate, qargs)

    circuit.append(inverse_qft(n_count).to_gate(label="QFT_dagger"), count_reg)
    circuit.measure(count_reg, creg)
    return circuit
