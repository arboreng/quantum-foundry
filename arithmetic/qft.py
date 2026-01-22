"""Quantum Fourier Transform, built from scratch (H, controlled-phase, swap
gates) rather than `qiskit.circuit.library.QFTGate`.

Originally written for [algorithms/shor](../algorithms/shor/circuit.py)'s
phase estimation circuit (RFC-0001); relocated here once a second consumer
needed it — the constant adders in [adders.py](adders.py) (RFC-0002).
"""

import math

from qiskit.circuit import QuantumCircuit


def qft(num_qubits: int) -> QuantumCircuit:
    """Quantum Fourier Transform on `num_qubits`, built from H, controlled-phase,
    and swap gates (not `qiskit.circuit.library.QFTGate`)."""
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
