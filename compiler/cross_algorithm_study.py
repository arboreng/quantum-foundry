"""Cross-algorithm transpilation study.

`analyze_transpilation` (RFC-0003) has, until now, only ever been applied
to Shor's `GateDecomposedOracle` circuit (see
`benchmarks/shor-transpilation.md`). This module runs it against a
representative, similarly-sized (4-10 qubit) circuit from every other
algorithm in this repo, to compare routing overhead across genuinely
different circuit shapes — oracle-heavy (Grover, Deutsch-Jozsa,
Bernstein-Vazirani, Simon), QFT-heavy (QPE, HHL), and parameterized-
ansatz (QAOA, VQE) — at a single representative optimization level.
Deutsch-Jozsa uses `ParityOracle` rather than `BalancedOracle` (its other
implementation): `BalancedOracle` is exponential in gate count by design
(see its own docstring), which would dominate this comparison and isn't
about routing at all.
"""

import math
from dataclasses import dataclass

from qiskit.circuit import QuantumCircuit

from algorithms.bernstein_vazirani.circuit import build_oracle_query_circuit as bv_query_circuit
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle
from algorithms.deutsch_jozsa.circuit import build_oracle_query_circuit as dj_query_circuit
from algorithms.deutsch_jozsa.oracles import ParityOracle
from algorithms.grover.circuit import build_grover_circuit
from algorithms.grover.oracles import MarkedBitstringOracle
from algorithms.hhl.circuit import build_hhl_circuit
from algorithms.hhl.oracles import DiagonalXOracle
from algorithms.qaoa.circuit import build_qaoa_circuit
from algorithms.qaoa.problems import MaxCutProblem
from algorithms.qpe.circuit import build_qpe_circuit
from algorithms.qpe.oracles import PhaseGateOracle
from algorithms.simon.circuit import build_simon_circuit
from algorithms.simon.oracles import LinearOracle
from algorithms.vqe.circuit import measurement_circuit
from algorithms.vqe.hamiltonians import TransverseFieldIsingHamiltonian
from compiler.targets import BASIS_GATES, linear_coupling_map
from compiler.transpilation import analyze_transpilation


@dataclass(frozen=True)
class CrossAlgorithmReport:
    algorithm: str
    qubit_count: int
    gate_count: int
    circuit_depth: int
    swap_count: int


def _representative_circuits() -> dict[str, QuantumCircuit]:
    circuits: dict[str, QuantumCircuit] = {}

    circuits["Grover"] = build_grover_circuit(
        5, MarkedBitstringOracle(5, marked={"10110"}), iterations=2
    )

    circuits["Deutsch-Jozsa"] = dj_query_circuit(5, ParityOracle(5, subset={0, 1, 2, 3, 4}))

    circuits["Bernstein-Vazirani"] = bv_query_circuit(5, HiddenStringOracle("10110"))

    circuits["Simon"] = build_simon_circuit(5, LinearOracle("10110"))

    qpe_eigenstate_prep = QuantumCircuit(1)
    qpe_eigenstate_prep.x(0)
    circuits["QPE"] = build_qpe_circuit(5, PhaseGateOracle(0.375), qpe_eigenstate_prep)

    triangle_plus_two = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    circuits["QAOA"] = build_qaoa_circuit(
        MaxCutProblem(5, triangle_plus_two), gammas=[0.5], betas=[0.3]
    )

    ising = TransverseFieldIsingHamiltonian(4, j_coupling=1.0, h_field=0.5)
    circuits["VQE"] = measurement_circuit(4, params=[0.3] * 8, reps=1, term=ising.terms[0])

    hhl_t = 3 * math.pi / 8
    hhl_b_state_prep = QuantumCircuit(1)
    circuits["HHL"] = build_hhl_circuit(
        DiagonalXOracle(a=1.0, b=1.0 / 3.0, t=hhl_t),
        t=hhl_t,
        n_clock=3,
        c_constant=0.5,
        b_state_prep=hhl_b_state_prep,
    )

    return circuits


def run_study(optimization_level: int = 1) -> list[CrossAlgorithmReport]:
    reports = []
    for name, circuit in _representative_circuits().items():
        coupling_map = linear_coupling_map(circuit.num_qubits)
        result = analyze_transpilation(circuit, coupling_map, BASIS_GATES, optimization_level)
        reports.append(
            CrossAlgorithmReport(
                algorithm=name,
                qubit_count=result.qubit_count,
                gate_count=result.gate_count,
                circuit_depth=result.circuit_depth,
                swap_count=result.swap_count,
            )
        )
    return reports


if __name__ == "__main__":
    for report in run_study():
        print(report)
