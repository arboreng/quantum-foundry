"""Tests for the from-scratch QFT (relocated from algorithms/shor in RFC-0002)."""

import pytest
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator, Statevector

from arithmetic.qft import inverse_qft, qft


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_matches_qiskit(n):
    """Our from-scratch QFT/inverse_qft must be operator-equivalent to
    Qiskit's own QFTGate — an educational proof of correctness, not just
    internal self-consistency."""
    assert Operator(qft(n)).equiv(Operator(QFTGate(n)))
    assert Operator(inverse_qft(n)).equiv(Operator(QFTGate(n)).adjoint())


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_inverse_qft_round_trip(n):
    for basis_state in range(2**n):
        sv = Statevector.from_int(basis_state, dims=2**n)
        round_tripped = sv.evolve(qft(n)).evolve(inverse_qft(n))
        assert round_tripped.equiv(sv)
