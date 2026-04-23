"""End-to-end linear-system solving using HHL.

See math.md for the theory and paper.md for the circuit this module
drives. Reuses `algorithms.qpe`'s controlled-power-of-unitary `Oracle`
pattern for eigenvalue estimation, and `arithmetic.qft` directly for the
clock register's (inverse) QFT.
"""

import math

from qiskit.circuit import QuantumCircuit

from algorithms.hhl.circuit import build_hhl_circuit
from algorithms.hhl.execution import AerExecutor, Executor
from algorithms.hhl.oracles import DiagonalXOracle, Oracle


def solve_linear_system(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
) -> tuple[float, dict[str, int]]:
    """Run the HHL circuit and return `(success_probability,
    b_register_counts_given_ancilla_1)`: the fraction of shots where the
    ancilla measured `1` (this repo's first postselection-based success
    pattern), and the b-register's measured distribution conditioned on
    that outcome."""
    executor = executor if executor is not None else AerExecutor()
    circuit = build_hhl_circuit(oracle, t, n_clock, c_constant, b_state_prep)
    counts = executor.run(circuit, shots)
    total = sum(counts.values())

    success_count = 0
    b_register_counts: dict[str, int] = {}
    for bitstring, count in counts.items():
        ancilla_bit, b_bits = bitstring[-1], bitstring[:-1]
        if ancilla_bit == "1":
            success_count += count
            b_register_counts[b_bits] = b_register_counts.get(b_bits, 0) + count

    return success_count / total, b_register_counts


if __name__ == "__main__":
    demo_t = 3 * math.pi / 8
    demo_oracle = DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=demo_t)
    demo_b_state_prep = QuantumCircuit(1)
    print(
        solve_linear_system(
            demo_oracle, t=demo_t, n_clock=3, c_constant=0.5, b_state_prep=demo_b_state_prep
        )
    )
