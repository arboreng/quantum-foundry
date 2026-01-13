"""Tests for the v0.2 Shor's algorithm implementation."""

import math
import random

import numpy as np
import pytest
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator, Statevector

from algorithms.shor import implementation
from algorithms.shor.circuit import inverse_qft, qft
from algorithms.shor.implementation import (
    OrderFindingResult,
    _perfect_power_factor,
    factor,
    find_order,
    recover_factor,
)
from algorithms.shor.oracles import PermutationMatrixOracle, _permutation_matrix

# --- QFT -----------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_matches_qiskit(n):
    """Our from-scratch QFT/inverse_qft must be operator-equivalent to
    Qiskit's own QFTGate — an educational proof of correctness, not just
    internal self-consistency."""
    assert Operator(qft(n)).equiv(Operator(QFTGate(n)))
    assert Operator(inverse_qft(n)).equiv(Operator(QFTGate(n)).adjoint())


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_inverse_qft_round_trip(n):
    for basis_state in range(2**n):
        sv = Statevector.from_int(basis_state, dims=2**n)
        round_tripped = sv.evolve(qft(n)).evolve(inverse_qft(n))
        assert round_tripped.equiv(sv)


# --- Oracle ----------------------------------------------------------------


def _coprime_pairs(seed: int, count: int) -> list[tuple[int, int]]:
    rng = random.Random(seed)
    pairs: list[tuple[int, int]] = []
    while len(pairs) < count:
        N = rng.randint(3, 31)
        a = rng.randint(2, N - 1)
        if math.gcd(a, N) == 1:
            pairs.append((a, N))
    return pairs


@pytest.mark.parametrize("a,N", _coprime_pairs(seed=0, count=20))
def test_permutation_matrix_matches_classical_multiplication(a, N):
    num_qubits = N.bit_length()
    matrix = _permutation_matrix(a, N, num_qubits)

    # Exactly one 1 per column/row (a valid permutation matrix).
    assert np.array_equal(matrix.sum(axis=0), np.ones(2**num_qubits))
    assert np.array_equal(matrix.sum(axis=1), np.ones(2**num_qubits))

    for x in range(2**num_qubits):
        expected = (a * x) % N if x < N else x
        actual = int(np.argmax(matrix[:, x]))
        assert actual == expected


def test_permutation_matrix_rejects_non_coprime_base():
    with pytest.raises(ValueError):
        _permutation_matrix(6, 15, 4)  # gcd(6, 15) = 3


def test_oracle_gate_caches_by_power():
    oracle = PermutationMatrixOracle(a=7, N=15, num_qubits=4)
    gate_a = oracle.controlled_power_gate(2)
    gate_b = oracle.controlled_power_gate(2)
    assert gate_a is gate_b


# --- find_order --------------------------------------------------------


def _true_order(a: int, N: int) -> int:
    x, r = a % N, 1
    while x != 1:
        x = (x * a) % N
        r += 1
    return r


@pytest.mark.parametrize("a,N", [(7, 15), (2, 15), (2, 21), (4, 21)])
def test_find_order_recovers_true_order(a, N):
    """find_order is probabilistic per call (bounded by math.md's >=1/2
    success argument), so retry until success and check correctness rather
    than asserting a single call succeeds."""
    expected = _true_order(a, N)
    for _ in range(25):
        result = find_order(a, N)
        assert isinstance(result, OrderFindingResult)
        if result.success:
            assert result.order == expected
            return
    pytest.fail(f"find_order didn't succeed for a={a}, N={N} in 25 attempts")


# --- recover_factor / _perfect_power_factor -----------------------------


def test_recover_factor_from_known_order():
    # order of 7 mod 15 is 4; 7^2 mod 15 = 4, gcd(3, 15)=3, gcd(5, 15)=5
    assert recover_factor(15, 7, 4) == (3, 5)


def test_recover_factor_rejects_odd_order():
    assert recover_factor(15, 2, 3) is None  # order of 2 mod 15 is 4, not 3


@pytest.mark.parametrize("n,expected", [(27, (3, 9)), (49, (7, 7)), (9, (3, 3))])
def test_perfect_power_factor(n, expected):
    assert _perfect_power_factor(n) == expected


def test_perfect_power_factor_none_for_non_perfect_power():
    assert _perfect_power_factor(15) is None


# --- factor (end to end) -------------------------------------------------


@pytest.mark.parametrize("n,expected", [(15, (3, 5)), (21, (3, 7))])
def test_factor_end_to_end(n, expected):
    assert factor(n, rng=random.Random(0)) == expected


def test_factor_even_short_circuits_without_quantum_path(monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("find_order should not be called for even n")

    monkeypatch.setattr(implementation, "find_order", _fail)
    assert factor(20) == (2, 10)


def test_factor_perfect_power_short_circuits_without_quantum_path(monkeypatch):
    def _fail(*args, **kwargs):
        raise AssertionError("find_order should not be called for a perfect power")

    monkeypatch.setattr(implementation, "find_order", _fail)
    assert factor(27) == (3, 9)
