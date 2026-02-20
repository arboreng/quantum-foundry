"""Tests for the v0.2 Grover's algorithm implementation."""

import numpy as np
import pytest
from qiskit.quantum_info import Operator

from algorithms.grover.circuit import diffusion_operator
from algorithms.grover.implementation import _iteration_count, search
from algorithms.grover.oracles import MarkedBitstringOracle


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_diffusion_operator_matches_closed_form(n):
    """`2|s><s| - I` where `|s>` is the uniform superposition — verified up
    to global phase since `X`-sandwiched constructions like this commonly
    differ from the textbook formula by an unobservable overall sign."""
    matrix = Operator(diffusion_operator(n))
    dim = 2**n
    s = np.ones(dim) / np.sqrt(dim)
    expected = 2 * np.outer(s, s) - np.eye(dim)
    assert matrix.equiv(Operator(expected))


@pytest.mark.parametrize(
    "n,marked",
    [
        (3, {"101"}),
        (3, {"101", "010"}),
        (4, {"0000", "1111", "1010"}),
        (1, {"0"}),
        (1, {"1"}),
    ],
)
def test_oracle_phase_flip_matches_expected_diagonal(n, marked):
    oracle = MarkedBitstringOracle(n, marked)
    matrix = Operator(oracle.phase_flip_gate()).data
    dim = 2**n
    expected_diag = np.ones(dim)
    for m in marked:
        expected_diag[int(m, 2)] = -1
    assert np.allclose(matrix, np.diag(expected_diag))


def test_oracle_rejects_wrong_length_bitstring():
    with pytest.raises(ValueError):
        MarkedBitstringOracle(3, {"10"})


def test_iteration_count():
    assert _iteration_count(3, 1) == 2  # (pi/4) * sqrt(8) ~ 2.22 -> 2
    assert _iteration_count(1, 1) == 1  # minimum of 1


@pytest.mark.parametrize(
    "n,marked",
    [
        (3, {"101"}),
        (3, {"000"}),
        (4, {"0000", "1111"}),
        (4, {"1010", "0101", "1100"}),
        (1, {"0"}),
        (1, {"1"}),
    ],
)
def test_search_finds_marked_item(n, marked):
    assert search(n, marked) in marked


def test_search_rejects_empty_marked_set():
    with pytest.raises(ValueError):
        search(3, set())
