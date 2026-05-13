"""Circuit construction for VQE.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.vqe.hamiltonians import PauliTerm


def ansatz_circuit(n_qubits: int, params: list[float], reps: int) -> QuantumCircuit:
    """Hardware-efficient ansatz: `reps` layers of per-qubit `RY(theta)`
    plus a ladder of entangling `CX` gates, then one final `RY` layer
    (`n_qubits * (reps + 1)` parameters total)."""
    expected = n_qubits * (reps + 1)
    if len(params) != expected:
        raise ValueError(
            f"expected {expected} params for n_qubits={n_qubits}, reps={reps}, got {len(params)}"
        )

    circuit = QuantumCircuit(n_qubits, name="ansatz")
    idx = 0
    for _ in range(reps):
        for q in range(n_qubits):
            circuit.ry(params[idx], q)
            idx += 1
        for q in range(n_qubits - 1):
            circuit.cx(q, q + 1)
    for q in range(n_qubits):
        circuit.ry(params[idx], q)
        idx += 1
    return circuit


def measurement_circuit(
    n_qubits: int, params: list[float], reps: int, term: PauliTerm
) -> QuantumCircuit:
    """`ansatz_circuit` followed by the basis-rotation gates for `term`
    (`H` for `X`, `Sdg` then `H` for `Y`, nothing for `Z`/`I`) and a
    measurement of every qubit."""
    circuit = QuantumCircuit(n_qubits, n_qubits, name=f"measure({term.paulis})")
    circuit.append(
        ansatz_circuit(n_qubits, params, reps).to_gate(label="ansatz"), range(n_qubits)
    )
    for q, pauli in enumerate(term.paulis):
        if pauli == "X":
            circuit.h(q)
        elif pauli == "Y":
            circuit.sdg(q)
            circuit.h(q)
    circuit.measure(range(n_qubits), range(n_qubits))
    return circuit


def group_measurement_circuit(
    n_qubits: int, params: list[float], reps: int, group: list[PauliTerm]
) -> QuantumCircuit:
    """Like `measurement_circuit`, but for a qubit-wise-commuting group of
    terms (`hamiltonians.group_qwc_terms`): one shared basis rotation per
    qubit — the group's non-identity Pauli at that position, if any
    (qubit-wise commutativity guarantees every term in the group agrees
    on it) — then a single measurement of every qubit, usable to compute
    every term in the group's expectation value."""
    circuit = QuantumCircuit(n_qubits, n_qubits, name="measure_group")
    circuit.append(
        ansatz_circuit(n_qubits, params, reps).to_gate(label="ansatz"), range(n_qubits)
    )
    for q in range(n_qubits):
        pauli = next((term.paulis[q] for term in group if term.paulis[q] != "I"), "I")
        if pauli == "X":
            circuit.h(q)
        elif pauli == "Y":
            circuit.sdg(q)
            circuit.h(q)
    circuit.measure(range(n_qubits), range(n_qubits))
    return circuit
