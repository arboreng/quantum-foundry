"""Tests for RFC-0003's hardware-aware transpilation.

Uses one `controlled_mult_mod_N_gate` call (RFC-0002) as a representative
elementary-gate circuit — the same building block `GateDecomposedOracle`
chains together, but small enough to transpile quickly.
"""

import pytest
from qiskit import QuantumCircuit, transpile

from arithmetic.adders import controlled_mult_mod_N_gate
from compiler.targets import BASIS_GATES, linear_coupling_map
from compiler.transpilation import analyze_transpilation


def _representative_circuit() -> QuantumCircuit:
    gate = controlled_mult_mod_N_gate(4, 7, 15)
    circuit = QuantumCircuit(gate.num_qubits)
    circuit.append(gate, range(gate.num_qubits))
    return circuit


def test_linear_coupling_map_edges():
    cm = linear_coupling_map(5)
    edges = {tuple(e) for e in cm.get_edges()}
    assert edges == {(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)}


def test_transpile_respects_coupling_map():
    """The actual property a coupling map is supposed to enforce: every
    2-qubit gate in the transpiled circuit acts on adjacent physical
    qubits."""
    circuit = _representative_circuit()
    coupling_map = linear_coupling_map(circuit.num_qubits)
    transpiled = transpile(
        circuit, coupling_map=coupling_map, basis_gates=BASIS_GATES, optimization_level=1
    )
    edges = {tuple(e) for e in coupling_map.get_edges()}

    two_qubit_gates = 0
    for instruction in transpiled.data:
        if len(instruction.qubits) == 2:
            two_qubit_gates += 1
            physical = tuple(transpiled.find_bit(q).index for q in instruction.qubits)
            assert physical in edges, f"{physical} is not a coupling-map edge"
    assert two_qubit_gates > 0


@pytest.mark.parametrize("optimization_level", [0, 1, 2, 3])
def test_analyze_transpilation_reports_sane_values(optimization_level):
    circuit = _representative_circuit()
    coupling_map = linear_coupling_map(circuit.num_qubits)
    report = analyze_transpilation(circuit, coupling_map, BASIS_GATES, optimization_level)

    assert report.optimization_level == optimization_level
    assert report.qubit_count == circuit.num_qubits
    assert report.gate_count > 0
    assert report.circuit_depth > 0
    assert report.swap_count >= 0
