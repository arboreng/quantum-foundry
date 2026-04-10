"""End-to-end ground-state energy estimation using VQE.

See math.md for the theory and paper.md for the circuit this module
drives. Reuses `algorithms.qaoa`'s `scipy.optimize.minimize`-driven
classical-loop pattern, generalized from a diagonal cost function to an
arbitrary Pauli-sum Hamiltonian requiring per-term basis rotation.
"""

from algorithms.vqe.hamiltonians import Hamiltonian


def expectation_value(
    hamiltonian: Hamiltonian, params: list[float], reps: int, shots: int = 1000
) -> float:
    """Estimate `<psi(params)|hamiltonian|psi(params)>` by running one
    measurement circuit per non-identity Pauli term and combining
    counts-weighted `+-1` parities.

    Not yet implemented — see RFC-0009 milestone v0.2.
    """
    raise NotImplementedError


def solve_ground_state(
    hamiltonian: Hamiltonian, reps: int = 1
) -> tuple[list[float], float]:
    """Approximate `hamiltonian`'s ground-state energy: optimize the
    ansatz parameters via `scipy.optimize.minimize`, then return the
    optimized params and a final energy estimate.

    Not yet implemented — see RFC-0009 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.vqe.implementation is not yet implemented (RFC-0009 v0.2)")
