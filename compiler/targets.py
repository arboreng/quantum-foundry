"""A hand-built, transparent hardware model for RFC-0003's transpilation
study: linear nearest-neighbor qubit connectivity plus a standard
superconducting basis gate set. Not a full `qiskit.transpiler.Target` (no
duration/error calibration — this is about connectivity/basis constraints,
not noise) and not one of `qiskit-ibm-runtime`'s fake backends (avoids a new
dependency, keeps the constraint fully inspectable).
"""

from qiskit.transpiler import CouplingMap

BASIS_GATES = ["rz", "sx", "x", "cx"]


def linear_coupling_map(num_qubits: int) -> CouplingMap:
    """Linear chain `0-1-2-...-(num_qubits-1)` — the most connectivity-
    constrained realistic topology, so it shows routing overhead most
    clearly."""
    return CouplingMap.from_line(num_qubits)
