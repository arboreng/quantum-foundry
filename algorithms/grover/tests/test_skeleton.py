"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0004 milestone v0.2).
"""

import pytest

from algorithms.grover import circuit, implementation
from algorithms.grover.oracles import MarkedBitstringOracle


def test_search_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        implementation.search(3, {"101"})


def test_build_grover_circuit_not_yet_implemented():
    oracle = MarkedBitstringOracle(3, {"101"})
    with pytest.raises(NotImplementedError):
        circuit.build_grover_circuit(3, oracle, iterations=1)
