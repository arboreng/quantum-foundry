"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0008 milestone v0.2).
"""

import pytest

from algorithms.qaoa import circuit, implementation
from algorithms.qaoa.problems import MaxCutProblem


def test_solve_maxcut_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        implementation.solve_maxcut(3, [(0, 1), (1, 2)])


def test_build_qaoa_circuit_not_yet_implemented():
    problem = MaxCutProblem(3, [(0, 1), (1, 2)])
    with pytest.raises(NotImplementedError):
        circuit.build_qaoa_circuit(problem, gammas=[0.5], betas=[0.5])
