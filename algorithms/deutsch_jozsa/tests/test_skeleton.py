"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0005 milestone v0.2).
"""

import pytest

from algorithms.deutsch_jozsa import circuit, implementation
from algorithms.deutsch_jozsa.oracles import ConstantOracle


def test_is_constant_not_yet_implemented():
    oracle = ConstantOracle(3, value=0)
    with pytest.raises(NotImplementedError):
        implementation.is_constant(3, oracle)


def test_build_oracle_query_circuit_not_yet_implemented():
    oracle = ConstantOracle(3, value=0)
    with pytest.raises(NotImplementedError):
        circuit.build_oracle_query_circuit(3, oracle)
