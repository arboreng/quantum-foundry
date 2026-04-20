"""End-to-end linear-system solving using HHL.

See math.md for the theory and paper.md for the circuit this module
drives. Reuses `algorithms.qpe`'s controlled-power-of-unitary `Oracle`
pattern for eigenvalue estimation, and `arithmetic.qft` directly for the
clock register's (inverse) QFT.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.hhl.oracles import Oracle


def solve_linear_system(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
    shots: int = 1000,
) -> tuple[float, dict[str, int]]:
    """Run the HHL circuit and return `(success_probability,
    b_register_counts_given_ancilla_1)`: the fraction of shots where the
    ancilla measured `1` (this repo's first postselection-based success
    pattern), and the b-register's measured distribution conditioned on
    that outcome.

    Not yet implemented — see RFC-0010 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.hhl.implementation is not yet implemented (RFC-0010 v0.2)")
