"""Tests for the v0.2 Grover's algorithm implementation."""

import math

import numpy as np
import pytest
from qiskit.quantum_info import Operator, Statevector

from algorithms.grover.circuit import build_grover_circuit, diffusion_operator
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
    # exact maximizer round(pi/(4*theta) - 1/2), sin(theta) = sqrt(M/N)
    assert _iteration_count(3, 1) == 2  # theta ~ 0.3614 -> 1.67 -> 2
    assert _iteration_count(1, 1) == 0  # theta = pi/4 -> 0.5 -> 0; sin^2(theta) = 0.5 either way
    assert _iteration_count(2, 1) == 1  # theta = pi/6 -> 1.0; the approximation would give 2
    assert _iteration_count(2, 3) == 0  # theta = pi/3 -> 0.0; the approximation would give 1


@pytest.mark.parametrize(
    "n,marked",
    [
        (2, {"00"}),
        (2, {"01", "10"}),
        (2, {"00", "01", "10"}),
        (3, {"000", "001"}),
        (4, {"0000", "0001", "0010"}),
    ],
)
def test_iteration_count_maximizes_success_probability(n, marked):
    """The shipped iteration count must be the true argmax of
    sin^2((2k+1)*theta) — regression for the small-angle approximation,
    which over-rotated for these (n, M) and in two cases drove the
    success probability to 0.25 and 0.0 respectively."""
    theta = math.asin(math.sqrt(len(marked) / 2**n))
    k = _iteration_count(n, len(marked))
    # argmax within the first peak: (2k+1)*theta <= pi. Beyond that the state
    # has rotated past |s_marked> and back, and a later k can land near pi/2
    # again by wrap-around — never useful, since it costs more oracle queries.
    ks = [j for j in range(50) if (2 * j + 1) * theta <= math.pi]
    best = max(ks, key=lambda j: math.sin((2 * j + 1) * theta) ** 2)
    assert math.sin((2 * k + 1) * theta) ** 2 == pytest.approx(
        math.sin((2 * best + 1) * theta) ** 2, abs=1e-12
    )

    circuit = build_grover_circuit(n, MarkedBitstringOracle(n, marked), k)
    state = Statevector(circuit.remove_final_measurements(inplace=False))
    # the oracle marks basis index int(m, 2) — same convention as the
    # measured bitstring `search` compares against
    success = sum(
        abs(a) ** 2 for i, a in enumerate(state.data) if format(i, f"0{n}b") in marked
    )
    assert success == pytest.approx(math.sin((2 * k + 1) * theta) ** 2, abs=1e-9)
    assert success > 0.4


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


def test_oracle_rejects_nonbinary_bitstring():
    with pytest.raises(ValueError):
        MarkedBitstringOracle(3, {"10x"})


def test_oracle_rejects_nonpositive_qubit_count():
    with pytest.raises(ValueError):
        MarkedBitstringOracle(0, set())
