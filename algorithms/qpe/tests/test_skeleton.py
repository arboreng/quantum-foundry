"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0007 milestone v0.2).
"""

import pytest
from qiskit.circuit import QuantumCircuit

from algorithms.qpe import circuit, implementation
from algorithms.qpe.oracles import PhaseGateOracle


def test_estimate_phase_not_yet_implemented():
    oracle = PhaseGateOracle(theta=0.25)
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)
    with pytest.raises(NotImplementedError):
        implementation.estimate_phase(oracle, eigenstate_prep, n_count=3)


def test_build_qpe_circuit_not_yet_implemented():
    oracle = PhaseGateOracle(theta=0.25)
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)
    with pytest.raises(NotImplementedError):
        circuit.build_qpe_circuit(3, oracle, eigenstate_prep)
