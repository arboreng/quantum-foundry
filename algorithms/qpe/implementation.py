"""End-to-end phase estimation using Quantum Phase Estimation.

See math.md for the theory and paper.md for the circuit this module drives.
"""

from qiskit.circuit import QuantumCircuit

from algorithms.qpe.circuit import build_qpe_circuit
from algorithms.qpe.execution import AerExecutor, Executor
from algorithms.qpe.oracles import Oracle, PhaseGateOracle


def estimate_phase(
    oracle: Oracle,
    eigenstate_prep: QuantumCircuit,
    n_count: int,
    *,
    executor: Executor | None = None,
    shots: int = 1,
) -> float:
    """Estimate `theta` for `oracle`'s unitary `U` and eigenstate prepared
    by `eigenstate_prep`, such that `U|psi> = e^(2*pi*i*theta)|psi>`.

    Accurate to `1/2**n_count` (see math.md); takes the most-frequent
    measured bitstring across `shots` runs.
    """
    executor = executor if executor is not None else AerExecutor()
    circuit = build_qpe_circuit(n_count, oracle, eigenstate_prep)
    counts = executor.run(circuit, shots)
    bitstring = max(counts, key=lambda key: counts[key])
    return int(bitstring, 2) / 2**n_count


if __name__ == "__main__":
    eigenstate_prep = QuantumCircuit(1)
    eigenstate_prep.x(0)
    print(estimate_phase(PhaseGateOracle(0.25), eigenstate_prep, n_count=3))
