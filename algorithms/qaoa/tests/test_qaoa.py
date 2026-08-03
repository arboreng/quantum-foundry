"""Tests for the QAOA implementation."""

import itertools

import numpy as np
import pytest
from qiskit.quantum_info import Operator

from algorithms.qaoa.circuit import build_qaoa_circuit, mixer_gate
from algorithms.qaoa.implementation import expectation_value, solve_maxcut
from algorithms.qaoa.problems import MaxCutProblem

TRIANGLE = [(0, 1), (1, 2), (0, 2)]
SQUARE = [(0, 1), (1, 2), (2, 3), (3, 0)]
PATH = [(0, 1), (1, 2), (2, 3)]


def _brute_force_optimal(n_qubits: int, edges: list[tuple[int, int]]) -> float:
    problem = MaxCutProblem(n_qubits, edges)
    return max(
        problem.cost_value("".join(bits)) for bits in itertools.product("01", repeat=n_qubits)
    )


@pytest.mark.parametrize(
    "n,edges,gamma", [(3, TRIANGLE, 0.3), (3, TRIANGLE, 1.0), (4, SQUARE, 0.7)]
)
def test_cost_gate_matches_exact_diagonal_unitary(n, edges, gamma):
    problem = MaxCutProblem(n, edges)
    matrix = Operator(problem.cost_gate(gamma))
    dim = 2**n
    expected_diag = np.zeros(dim, dtype=complex)
    for z in range(dim):
        bits = [(z >> k) & 1 for k in range(n)]
        cost = sum(1 for i, j in edges if bits[i] != bits[j])
        expected_diag[z] = np.exp(-1j * gamma * cost)
    assert matrix.equiv(Operator(np.diag(expected_diag)))


@pytest.mark.parametrize("n,beta", [(1, 0.4), (2, 0.4), (3, 0.9)])
def test_mixer_gate_matches_exact_rotation_product(n, beta):
    matrix = Operator(mixer_gate(n, beta))
    rx = np.array(
        [[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]]
    )
    expected = rx
    for _ in range(n - 1):
        expected = np.kron(rx, expected)
    assert matrix.equiv(Operator(expected))


def test_cost_value_triangle():
    problem = MaxCutProblem(3, TRIANGLE)
    assert problem.cost_value("000") == 0
    assert problem.cost_value("111") == 0
    assert problem.cost_value("010") == 2


def test_cost_value_square_bipartition_is_optimal():
    problem = MaxCutProblem(4, SQUARE)
    assert problem.cost_value("0101") == 4  # alternating -> every edge cut


def test_build_qaoa_circuit_rejects_mismatched_lengths():
    problem = MaxCutProblem(3, TRIANGLE)
    with pytest.raises(ValueError):
        build_qaoa_circuit(problem, gammas=[0.5, 0.5], betas=[0.5])


def test_expectation_value_is_bounded_by_optimal_cost():
    problem = MaxCutProblem(3, TRIANGLE)
    value = expectation_value(problem, gammas=[0.5], betas=[0.3], shots=500)
    assert 0 <= value <= _brute_force_optimal(3, TRIANGLE)


@pytest.mark.parametrize(
    "n,edges,p",
    [(3, TRIANGLE, 1), (4, SQUARE, 1), (4, PATH, 1), (3, TRIANGLE, 2)],
)
def test_solve_maxcut_finds_optimal_cut(n, edges, p):
    """QAOA is approximate by construction (see math.md); for these small
    graphs it consistently finds the true optimum, but retry a few times
    for robustness against the classical optimizer occasionally settling
    on a local optimum on a single run."""
    optimal = _brute_force_optimal(n, edges)
    for _ in range(3):
        _, found_cost = solve_maxcut(n, edges, p=p)
        if found_cost == optimal:
            return
    pytest.fail(f"solve_maxcut never found the optimal cost {optimal} for n={n}, edges={edges}")


def test_maxcut_rejects_invalid_edges():
    with pytest.raises(ValueError):
        MaxCutProblem(3, [(0, 3)])
    with pytest.raises(ValueError):
        MaxCutProblem(3, [(1, 1)])


def test_maxcut_rejects_invalid_bitstrings():
    problem = MaxCutProblem(3, TRIANGLE)
    with pytest.raises(ValueError):
        problem.cost_value("01x")
