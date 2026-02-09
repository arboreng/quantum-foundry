"""Tests for RFC-0002's GateDecomposedOracle: verifies it's operator-
equivalent to RFC-0001's PermutationMatrixOracle, and that the full
find_order/factor pipeline produces correct results when driven by it.

These circuits are significantly more expensive to simulate than the
permutation-matrix oracle (that's the whole point of a gate-decomposed
circuit), so coverage here is intentionally narrower than test_shor.py's.
"""

import random

import pytest
from qiskit.quantum_info import Statevector

from algorithms.shor.execution import ConstrainedAerExecutor
from algorithms.shor.implementation import factor, find_order
from algorithms.shor.oracles import GateDecomposedOracle
from compiler.targets import BASIS_GATES, linear_coupling_map


def test_gate_decomposed_oracle_matches_permutation_matrix_oracle():
    """For a fixed (a, N, power), GateDecomposedOracle's controlled gate must
    produce the same classical result as PermutationMatrixOracle's (both are
    deterministic permutations of computational basis states), with
    GateDecomposedOracle's extra ancillas verified back at |0>."""
    a, N, power = 7, 15, 2
    num_qubits = N.bit_length()

    gate_decomposed = GateDecomposedOracle(a, N, num_qubits).controlled_power_gate(power)
    n_ancilla = num_qubits + 3
    dim = 2 ** (1 + num_qubits + n_ancilla)

    a_power = pow(a, power, N)
    for ctrl in (0, 1):
        for y in range(N):
            input_int = ctrl | (y << 1)
            actual = Statevector.from_int(input_int, dims=dim).evolve(gate_decomposed)
            expected_y = (a_power * y) % N if ctrl == 1 else y
            expected_int = ctrl | (expected_y << 1)  # ancillas back at |0>
            expected = Statevector.from_int(expected_int, dims=dim)
            assert actual.equiv(expected)


def test_find_order_with_gate_decomposed_oracle():
    a, N = 7, 15
    expected_order = 4  # 7^4 mod 15 = 1, and 7^k != 1 for k < 4
    for _ in range(10):
        result = find_order(a, N, oracle_cls=GateDecomposedOracle)
        if result.success:
            assert result.order == expected_order
            return
    raise AssertionError(f"find_order with GateDecomposedOracle didn't succeed for a={a}, N={N}")


def test_factor_with_gate_decomposed_oracle():
    assert factor(15, rng=random.Random(0), oracle_cls=GateDecomposedOracle) == (3, 5)


@pytest.mark.slow
def test_find_order_with_gate_decomposed_oracle_at_n21():
    """N=21 (5 work qubits) is dramatically slower to simulate than N=15 (a
    single find_order call took ~10 minutes during development) — excluded
    from the default run via the `slow` marker; run explicitly with
    `pytest -m slow`. Retries (each ~10 min) up to 3 times rather than
    asserting on a single probabilistic attempt."""
    a, N = 4, 21
    expected_order = 3  # 4^3 mod 21 = 1
    for _ in range(3):
        result = find_order(a, N, oracle_cls=GateDecomposedOracle)
        if result.success:
            assert result.order == expected_order
            return
    raise AssertionError(f"find_order with GateDecomposedOracle didn't succeed for a={a}, N={N}")


@pytest.mark.slow
def test_find_order_survives_hardware_aware_transpilation():
    """RFC-0003: routing onto a connectivity-constrained linear coupling map
    (via ConstrainedAerExecutor) must preserve logical correctness, not just
    satisfy the coupling-map constraint structurally (that part is covered,
    faster, in compiler/tests/test_transpilation.py). ~50s/attempt measured
    during development — comparable to the unconstrained oracle, not the
    order-of-magnitude jump N=21 was."""
    a, N = 7, 15
    expected_order = 4
    executor = ConstrainedAerExecutor(linear_coupling_map(19), BASIS_GATES)
    for _ in range(3):
        result = find_order(a, N, oracle_cls=GateDecomposedOracle, executor=executor)
        if result.success:
            assert result.order == expected_order
            return
    raise AssertionError(f"find_order didn't succeed for a={a}, N={N} under constrained routing")
