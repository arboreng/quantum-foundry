"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0005 milestone v0.2).
"""

import pytest

from algorithms.bernstein_vazirani import circuit, implementation
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle


def test_find_hidden_string_not_yet_implemented():
    oracle = HiddenStringOracle("101")
    with pytest.raises(NotImplementedError):
        implementation.find_hidden_string(3, oracle)


def test_build_oracle_query_circuit_not_yet_implemented():
    oracle = HiddenStringOracle("101")
    with pytest.raises(NotImplementedError):
        circuit.build_oracle_query_circuit(3, oracle)
