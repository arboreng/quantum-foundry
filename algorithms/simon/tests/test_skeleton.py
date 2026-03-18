"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0006 milestone v0.2).
"""

import pytest

from algorithms.simon import circuit, implementation
from algorithms.simon.oracles import LinearOracle


def test_find_hidden_period_not_yet_implemented():
    oracle = LinearOracle("101")
    with pytest.raises(NotImplementedError):
        implementation.find_hidden_period(3, oracle)


def test_build_simon_circuit_not_yet_implemented():
    oracle = LinearOracle("101")
    with pytest.raises(NotImplementedError):
        circuit.build_simon_circuit(3, oracle)
