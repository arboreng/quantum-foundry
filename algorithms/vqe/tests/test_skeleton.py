"""Smoke test confirming the package skeleton is importable.

Replace/expand once implementation.py and circuit.py have real behavior
(RFC-0009 milestone v0.2).
"""

import pytest

from algorithms.vqe import circuit, implementation
from algorithms.vqe.hamiltonians import PauliTerm, TransverseFieldIsingHamiltonian


def test_transverse_field_ising_terms_not_yet_implemented():
    hamiltonian = TransverseFieldIsingHamiltonian(2, j_coupling=1.0, h_field=0.5)
    with pytest.raises(NotImplementedError):
        _ = hamiltonian.terms


def test_ansatz_circuit_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        circuit.ansatz_circuit(2, params=[0.1, 0.2, 0.3, 0.4], reps=1)


def test_measurement_circuit_not_yet_implemented():
    term = PauliTerm(coefficient=1.0, paulis="ZZ")
    with pytest.raises(NotImplementedError):
        circuit.measurement_circuit(2, params=[0.1, 0.2, 0.3, 0.4], reps=1, term=term)


def test_solve_ground_state_not_yet_implemented():
    hamiltonian = TransverseFieldIsingHamiltonian(2, j_coupling=1.0, h_field=0.5)
    with pytest.raises(NotImplementedError):
        implementation.solve_ground_state(hamiltonian)
