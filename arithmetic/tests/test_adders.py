"""Correctness tests for the RFC-0002 Draper/Beauregard-style adders.

Each layer is checked against brute-force classical arithmetic on the full
statevector (so ancilla qubits returning to `|0>` is verified along with the
result), before being trusted as a building block for the next layer.
"""

import pytest
from qiskit.quantum_info import Statevector

from arithmetic.adders import (
    add_constant_gate,
    add_constant_mod_N_gate,
    controlled_mult_mod_N_gate,
    modinv,
)


@pytest.mark.parametrize("num_qubits", [3, 4, 5])
def test_add_constant_gate_matches_classical_addition(num_qubits):
    for c in [0, 1, 3, -1, -5, 2**num_qubits - 1]:
        gate = add_constant_gate(num_qubits, c)
        for x in range(2**num_qubits):
            actual = Statevector.from_int(x, dims=2**num_qubits).evolve(gate)
            expected = Statevector.from_int((x + c) % 2**num_qubits, dims=2**num_qubits)
            assert actual.equiv(expected)


@pytest.mark.parametrize("num_qubits,N", [(4, 15), (5, 21)])
def test_add_constant_mod_N_gate_matches_classical_addition(num_qubits, N):
    dim = 2 ** (num_qubits + 2)
    for c in range(N):
        gate = add_constant_mod_N_gate(num_qubits, c, N)
        for x in range(N):
            actual = Statevector.from_int(x, dims=dim).evolve(gate)
            expected = Statevector.from_int((x + c) % N, dims=dim)
            assert actual.equiv(expected)


def test_modinv():
    for a, N in [(7, 15), (2, 15), (4, 21), (5, 21)]:
        inv = modinv(a, N)
        assert (a * inv) % N == 1


def test_modinv_rejects_non_coprime():
    with pytest.raises(ValueError):
        modinv(6, 15)


@pytest.mark.parametrize("num_qubits,N", [(4, 15)])
def test_controlled_mult_mod_N_gate_matches_classical_multiplication(num_qubits, N):
    """Full brute-force check (both ctrl values, all y < N) at N=15 only —
    each (a, N) pair here costs real wall-clock time to simulate (this is
    exactly the point of a gate-decomposed circuit vs. RFC-0001's dense
    permutation-matrix oracle), so N=21 coverage is left to the higher-level
    `find_order`/`factor` integration test in algorithms/shor instead."""
    a = 7
    gate = controlled_mult_mod_N_gate(num_qubits, a, N)
    dim = 2 ** (1 + num_qubits + (num_qubits + 3))
    y_bit = 1
    for ctrl in (0, 1):
        for y in range(N):
            input_int = ctrl | (y << y_bit)
            actual = Statevector.from_int(input_int, dims=dim).evolve(gate)
            expected_y = (a * y) % N if ctrl == 1 else y
            expected_int = ctrl | (expected_y << y_bit)
            expected = Statevector.from_int(expected_int, dims=dim)
            assert actual.equiv(expected)
