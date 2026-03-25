"""End-to-end phase estimation using Quantum Phase Estimation.

See math.md for the theory and paper.md for the circuit this module drives.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.qpe.oracles import Oracle


def estimate_phase(oracle: Oracle, eigenstate_prep: QuantumCircuit, n_count: int) -> float:
    """Estimate `theta` for `oracle`'s unitary `U` and eigenstate prepared
    by `eigenstate_prep`, such that `U|psi> = e^(2*pi*i*theta)|psi>`.

    Not yet implemented — see RFC-0007 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.qpe.implementation is not yet implemented (RFC-0007 v0.2)")
