"""Tests for the v0.2 Deutsch-Jozsa algorithm implementation."""

import pytest
from qiskit.quantum_info import Statevector

from algorithms.deutsch_jozsa.implementation import is_constant
from algorithms.deutsch_jozsa.oracles import BalancedOracle, ConstantOracle, ParityOracle


def _oracle_truth_table_matches(oracle, n_qubits, f):
    gate = oracle.oracle_gate()
    dim = 2 ** (n_qubits + 1)
    for x in range(2**n_qubits):
        for y in (0, 1):
            actual = Statevector.from_int(x | (y << n_qubits), dims=dim).evolve(gate)
            expected = Statevector.from_int(x | ((y ^ f(x)) << n_qubits), dims=dim)
            if not actual.equiv(expected):
                return False
    return True


@pytest.mark.parametrize("value", [0, 1])
def test_constant_oracle_matches_truth_table(value):
    assert _oracle_truth_table_matches(ConstantOracle(3, value), 3, lambda x: value)


def test_parity_oracle_matches_truth_table():
    subset = {0, 2}

    def f(x):
        return bin(x & 0b101).count("1") % 2

    assert _oracle_truth_table_matches(ParityOracle(3, subset), 3, f)


def test_parity_oracle_rejects_empty_subset():
    with pytest.raises(ValueError):
        ParityOracle(3, set())


def test_balanced_oracle_matches_truth_table():
    marked = {format(i, "03b") for i in range(4)}

    def f(x):
        return 1 if x in range(4) else 0

    assert _oracle_truth_table_matches(BalancedOracle(3, marked), 3, f)


def test_balanced_oracle_rejects_wrong_size_marked_set():
    with pytest.raises(ValueError):
        BalancedOracle(3, {"000", "001"})  # needs exactly 4, not 2


@pytest.mark.parametrize("value", [0, 1])
def test_is_constant_true_for_constant_oracle(value):
    assert is_constant(3, ConstantOracle(3, value)) is True


def test_is_constant_false_for_parity_oracle():
    assert is_constant(3, ParityOracle(3, {0, 2})) is False


def test_is_constant_false_for_balanced_oracle():
    marked = {format(i, "03b") for i in range(4)}
    assert is_constant(3, BalancedOracle(3, marked)) is False


def test_is_constant_single_qubit():
    assert is_constant(1, ConstantOracle(1, 0)) is True
    assert is_constant(1, ParityOracle(1, {0})) is False


def test_balanced_oracle_rejects_nonbinary_bitstring():
    with pytest.raises(ValueError):
        BalancedOracle(2, {"00", "0x"})
