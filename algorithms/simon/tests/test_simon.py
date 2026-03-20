"""Tests for the v0.2 Simon's algorithm implementation."""

from collections import Counter

import pytest
from qiskit.quantum_info import Statevector

from algorithms.simon.circuit import build_simon_circuit
from algorithms.simon.execution import AerExecutor
from algorithms.simon.implementation import (
    _rank_gf2,
    _solve_gf2_nullspace,
    find_hidden_period,
)
from algorithms.simon.oracles import LinearOracle, PermutationOracle, _permutation_labels

TEST_STRINGS = ["101", "110", "111", "100", "010", "001", "1", "11", "1010"]


def _classical_linear_f(oracle: LinearOracle, x: int) -> int:
    n = oracle.n_qubits
    result = 0
    for k in range(n):
        bit = bin(oracle.matrix_rows[k] & x).count("1") % 2
        result |= bit << k
    return result


def _oracle_truth_table_matches(oracle, n_qubits, f):
    gate = oracle.oracle_gate()
    dim = 2 ** (2 * n_qubits)
    for x in range(2**n_qubits):
        f_x = f(x)
        for y in range(2**n_qubits):
            actual = Statevector.from_int(x | (y << n_qubits), dims=dim).evolve(gate)
            expected = Statevector.from_int(x | ((y ^ f_x) << n_qubits), dims=dim)
            if not actual.equiv(expected):
                return False
    return True


# --- Oracle correctness -----------------------------------------------


@pytest.mark.parametrize("s", TEST_STRINGS)
def test_linear_oracle_matches_truth_table(s):
    oracle = LinearOracle(s)
    assert _oracle_truth_table_matches(oracle, len(s), lambda x: _classical_linear_f(oracle, x))


@pytest.mark.parametrize("s", TEST_STRINGS)
def test_linear_oracle_kernel_is_exactly_s(s):
    oracle = LinearOracle(s)
    n = len(s)
    s_int = int(s, 2)
    kernel = {x for x in range(2**n) if _classical_linear_f(oracle, x) == 0}
    assert kernel == {0, s_int}


@pytest.mark.parametrize("s", TEST_STRINGS)
def test_permutation_oracle_matches_truth_table(s):
    oracle = PermutationOracle(s)
    assert _oracle_truth_table_matches(oracle, len(s), lambda x: oracle.labels[x])


@pytest.mark.parametrize("s", TEST_STRINGS)
def test_permutation_oracle_is_exactly_two_to_one_with_period_s(s):
    n = len(s)
    s_int = int(s, 2)
    labels = _permutation_labels(s)
    assert all(labels[x] == labels[x ^ s_int] for x in range(2**n))
    assert all(count == 2 for count in Counter(labels).values())


def test_oracles_reject_zero_period():
    with pytest.raises(ValueError):
        LinearOracle("000")
    with pytest.raises(ValueError):
        PermutationOracle("000")


# --- Circuit property ----------------------------------------------------


@pytest.mark.parametrize("s", ["101", "1010"])
@pytest.mark.parametrize("oracle_cls", [LinearOracle, PermutationOracle])
def test_measured_y_always_satisfies_ys_equals_zero(s, oracle_cls):
    n = len(s)
    s_int = int(s, 2)
    oracle = oracle_cls(s)
    circuit = build_simon_circuit(n, oracle)
    counts = AerExecutor().run(circuit, shots=200)
    for y_str in counts:
        y = int(y_str, 2)
        assert bin(y & s_int).count("1") % 2 == 0


# --- GF(2) linear algebra ------------------------------------------------


def test_row_reduce_and_solve_hand_example():
    # n=3, s=101 (int 5): equations orthogonal to s are y with even parity of y&5
    equations = [0b010, 0b101]
    assert _rank_gf2(equations, 3) == 2
    assert _solve_gf2_nullspace(equations, 3) == 0b101


def test_rank_detects_dependence():
    # 0b0001 ^ 0b0100 == 0b0101, so these three are NOT all independent
    assert _rank_gf2([0b0001, 0b0100, 0b0101], 4) == 2
    assert _rank_gf2([0b0001, 0b0100, 0b1010], 4) == 3


def test_solve_gf2_nullspace_n1():
    # n=1: zero equations needed, only nonzero element is "1"
    assert _solve_gf2_nullspace([], 1) == 1


# --- End to end -----------------------------------------------------------


@pytest.mark.parametrize("s", TEST_STRINGS)
@pytest.mark.parametrize("oracle_cls", [LinearOracle, PermutationOracle])
def test_find_hidden_period_recovers_s(s, oracle_cls):
    assert find_hidden_period(len(s), oracle_cls(s)) == s
