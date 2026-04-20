"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0010 milestone v0.2).
"""

import pytest
from qiskit.circuit import QuantumCircuit

from algorithms.hhl import implementation
from algorithms.hhl.circuit import build_hhl_circuit
from algorithms.hhl.oracles import DiagonalXOracle


def test_controlled_power_gate_not_yet_implemented():
    oracle = DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=3.0)
    with pytest.raises(NotImplementedError):
        oracle.controlled_power_gate(1)


def test_build_hhl_circuit_not_yet_implemented():
    oracle = DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=3.0)
    b_state_prep = QuantumCircuit(1)
    with pytest.raises(NotImplementedError):
        build_hhl_circuit(oracle, t=3.0, n_clock=3, c_constant=0.5, b_state_prep=b_state_prep)


def test_solve_linear_system_not_yet_implemented():
    oracle = DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=3.0)
    b_state_prep = QuantumCircuit(1)
    with pytest.raises(NotImplementedError):
        implementation.solve_linear_system(
            oracle, t=3.0, n_clock=3, c_constant=0.5, b_state_prep=b_state_prep
        )
