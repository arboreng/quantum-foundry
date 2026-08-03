"""Tests for the Bernstein-Vazirani algorithm implementation."""

import pytest
from qiskit.quantum_info import Statevector

from algorithms.bernstein_vazirani.implementation import find_hidden_string
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle


@pytest.mark.parametrize("s", ["101", "000", "111", "010", "1"])
def test_oracle_matches_truth_table(s):
    n = len(s)
    oracle = HiddenStringOracle(s)
    gate = oracle.oracle_gate()
    dim = 2 ** (n + 1)
    s_int = int(s, 2)
    for x in range(2**n):
        f_x = bin(x & s_int).count("1") % 2
        for y in (0, 1):
            actual = Statevector.from_int(x | (y << n), dims=dim).evolve(gate)
            expected = Statevector.from_int(x | ((y ^ f_x) << n), dims=dim)
            assert actual.equiv(expected)


@pytest.mark.parametrize("s", ["101", "000", "111", "010", "1", "1010"])
def test_find_hidden_string_recovers_s(s):
    assert find_hidden_string(len(s), HiddenStringOracle(s)) == s


def test_hidden_string_oracle_rejects_nonbinary_string():
    with pytest.raises(ValueError):
        HiddenStringOracle("10x")


def test_hidden_string_oracle_rejects_empty_string():
    with pytest.raises(ValueError):
        HiddenStringOracle("")
