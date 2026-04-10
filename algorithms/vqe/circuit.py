"""Circuit construction for VQE.

See paper.md for the derivation this module implements.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.vqe.hamiltonians import PauliTerm


def ansatz_circuit(n_qubits: int, params: list[float], reps: int) -> QuantumCircuit:
    """Hardware-efficient ansatz: `reps` layers of per-qubit `RY(theta)`
    plus a ladder of entangling `CX` gates, then one final `RY` layer
    (`n_qubits * (reps + 1)` parameters total).

    Not yet implemented — see RFC-0009 milestone v0.2.
    """
    raise NotImplementedError


def measurement_circuit(
    n_qubits: int, params: list[float], reps: int, term: PauliTerm
) -> QuantumCircuit:
    """`ansatz_circuit` followed by the basis-rotation gates for `term`
    (`H` for `X`, `Sdg` then `H` for `Y`, nothing for `Z`/`I`) and a
    measurement of every qubit.

    Not yet implemented — see RFC-0009 milestone v0.2.
    """
    raise NotImplementedError
