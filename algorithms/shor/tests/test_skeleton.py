"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0001 milestone v0.2).
"""

import pytest

from algorithms.shor import circuit, implementation


def test_factor_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        implementation.factor(15)


def test_build_shor_circuit_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        circuit.build_shor_circuit(15, 7)
