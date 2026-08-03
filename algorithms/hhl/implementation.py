"""End-to-end linear-system solving using HHL.

See math.md for the theory and paper.md for the circuit this module
drives. Reuses `algorithms.qpe`'s controlled-power-of-unitary `Oracle`
pattern for eigenvalue estimation, and `arithmetic.qft` directly for the
clock register's (inverse) QFT.
"""

import math

from qiskit.circuit import QuantumCircuit

from algorithms.hhl.circuit import build_amplified_hhl_circuit, build_hhl_circuit
from algorithms.hhl.execution import AerExecutor, Executor
from algorithms.hhl.oracles import DiagonalXOracle, Oracle


def _postselect_on_ancilla(counts: dict[str, int]) -> tuple[float, dict[str, int]]:
    """Split measured counts by the ancilla bit (the last character of
    each bitstring, this repo's usual convention): returns
    `(success_probability, b_register_counts_given_ancilla_1)`."""
    total = sum(counts.values())
    success_count = 0
    b_register_counts: dict[str, int] = {}
    for bitstring, count in counts.items():
        ancilla_bit, b_bits = bitstring[-1], bitstring[:-1]
        if ancilla_bit == "1":
            success_count += count
            b_register_counts[b_bits] = b_register_counts.get(b_bits, 0) + count
    return success_count / total, b_register_counts


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
    return _postselect_on_ancilla(counts)


def optimal_amplification_iterations(success_probability: float) -> int:
    """Standard amplitude-amplification formula (Brassard-Hoyer-Mosca-Tapp
    1998, the same argument as Grover's optimal iteration count): after
    `k` rounds of `Q`, the success probability is `sin((2k+1)*theta)**2`
    for `theta = arcsin(sqrt(success_probability))`, maximized (nearest
    integer) at `k = round(pi / (4*theta) - 1/2)`, at least 0."""
    if not 0.0 < success_probability <= 1.0:
        raise ValueError(
            f"success_probability must be in (0, 1], got {success_probability}"
        )
    theta = math.asin(math.sqrt(success_probability))
    return max(0, round(math.pi / (4 * theta) - 0.5))


def amplify_and_solve_linear_system(
    oracle: Oracle,
    t: float,
    n_clock: int,
    c_constant: float,
    b_state_prep: QuantumCircuit,
    num_iterations: int,
    *,
    executor: Executor | None = None,
    shots: int = 1000,
) -> tuple[float, dict[str, int]]:
    """Like `solve_linear_system`, but runs `num_iterations` rounds of
    amplitude amplification first (`circuit.build_amplified_hhl_circuit`)
    to boost the postselection success probability — same postselection
    and return shape, different circuit. Use
    `optimal_amplification_iterations` to choose `num_iterations` from an
    estimated (or, as here, exactly known) success probability."""
    executor = executor if executor is not None else AerExecutor()
    circuit = build_amplified_hhl_circuit(
        oracle, t, n_clock, c_constant, b_state_prep, num_iterations
    )
    counts = executor.run(circuit, shots)
    return _postselect_on_ancilla(counts)


if __name__ == "__main__":
    demo_t = 3 * math.pi / 8
    demo_oracle = DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=demo_t)
    demo_b_state_prep = QuantumCircuit(1)
    print(
        solve_linear_system(
            demo_oracle, t=demo_t, n_clock=3, c_constant=0.5, b_state_prep=demo_b_state_prep
        )
    )
    print(
        amplify_and_solve_linear_system(
            demo_oracle,
            t=demo_t,
            n_clock=3,
            c_constant=0.5,
            b_state_prep=demo_b_state_prep,
            num_iterations=optimal_amplification_iterations(0.3515625),
        )
    )
