"""Quantum counting: estimate the number of marked items `M` without
knowing it in advance, via QPE applied to the Grover iteration operator
`Q` (oracle, then diffusion — the same iteration `circuit.
build_grover_circuit` repeats `iterations` times; here, the number of
marked items `search()`'s caller must otherwise supply is exactly what
this module estimates instead).

Reuses `arithmetic.qft.inverse_qft` directly (a fifth consumer, after
`algorithms.shor.circuit`, `arithmetic.adders`, `algorithms.qpe.circuit`,
and `algorithms.hhl.circuit`).
"""

import math

from qiskit.circuit import ClassicalRegister, Gate, QuantumCircuit, QuantumRegister

from algorithms.grover.circuit import diffusion_operator
from algorithms.grover.execution import AerExecutor, Executor
from algorithms.grover.oracles import Oracle
from arithmetic.qft import inverse_qft


def _grover_iteration_gate(n_qubits: int, oracle: Oracle) -> Gate:
    """One Grover iteration `Q` (oracle, then diffusion) as a single gate
    — the same construction `build_grover_circuit`'s loop body applies,
    reused here rather than re-derived."""
    circuit = QuantumCircuit(n_qubits, name="Q")
    circuit.append(oracle.phase_flip_gate(), range(n_qubits))
    circuit.append(diffusion_operator(n_qubits).to_gate(label="diffusion"), range(n_qubits))
    return circuit.to_gate(label="Q")


def controlled_grover_iteration_power_gate(n_qubits: int, oracle: Oracle, power: int) -> Gate:
    """Controlled `Q^power`. `Q` has no convenient closed form for
    exponentiation (unlike e.g. `algorithms.hhl.oracles.DiagonalXOracle`),
    so this literally repeats `Q` `power` times before adding a single
    control — fine for the small instances this module targets."""
    circuit = QuantumCircuit(n_qubits, name=f"Q^{power}")
    q_gate = _grover_iteration_gate(n_qubits, oracle)
    for _ in range(power):
        circuit.append(q_gate, range(n_qubits))
    return circuit.to_gate(label=f"Q^{power}").control(1)


def build_counting_circuit(n_qubits: int, oracle: Oracle, n_count: int) -> QuantumCircuit:
    """Build the quantum counting circuit: `H^n_count` on the counting
    register, `H^n_qubits` (uniform superposition, the same starting state
    `search()` uses) on the search register, controlled `Q^(2**k)` per
    counting qubit, inverse QFT on the counting register, measure the
    counting register."""
    count_reg = QuantumRegister(n_count, name="count")
    search_reg = QuantumRegister(n_qubits, name="search")
    creg = ClassicalRegister(n_count, name="c")
    circuit = QuantumCircuit(count_reg, search_reg, creg, name="counting")

    circuit.h(count_reg)
    circuit.h(search_reg)

    for k in range(n_count):
        gate = controlled_grover_iteration_power_gate(n_qubits, oracle, 2**k)
        circuit.append(gate, [count_reg[k], *search_reg])

    circuit.append(inverse_qft(n_count).to_gate(label="QFT_dagger"), count_reg)
    circuit.measure(count_reg, creg)
    return circuit


def count(
    n_qubits: int,
    oracle: Oracle,
    n_count: int,
    *,
    executor: Executor | None = None,
    shots: int = 1,
) -> int:
    """Estimate the number of items `oracle` marks among `2**n_qubits`
    candidates, without being told it in advance. Textbook treatments give
    `Q`'s two eigenvalues as `e^(+-2i*theta)` for `sin(theta)**2 = M/N`,
    which would make `theta = pi*y/2**n_count` directly — but
    `circuit.diffusion_operator` (RFC-0004) carries an extra, harmless-
    for-plain-Grover-search global phase of `-1` relative to that textbook
    formula (see its own test's "verified up to global phase" comment),
    which becomes *observable* once `Q` is used under control here. That
    flips `Q`'s actual eigenvalues to `-e^(+-2i*theta)`, i.e. phases
    `pi +- 2*theta`, so the measured `y` estimates `0.5 +- theta/pi`
    instead of `+-theta/pi` directly (see math.md, empirically confirmed
    against the statevector in `tests/test_counting.py`). Either sign
    gives the same `sin(theta)**2` back out (`sin(pi - x) = sin(x)`), so
    which branch QPE happens to measure doesn't matter. Accuracy improves
    with `n_count`, the same precision/`n_count` relationship as
    `algorithms.qpe.implementation.estimate_phase`."""
    executor = executor if executor is not None else AerExecutor()
    circuit = build_counting_circuit(n_qubits, oracle, n_count)
    counts = executor.run(circuit, shots)
    bitstring = max(counts, key=lambda key: counts[key])
    y = int(bitstring, 2)
    theta = math.pi * abs(y / 2**n_count - 0.5)
    return round(2**n_qubits * math.sin(theta) ** 2)


if __name__ == "__main__":
    from algorithms.grover.oracles import MarkedBitstringOracle

    demo_oracle = MarkedBitstringOracle(3, {"000", "001", "010", "011"})
    print(count(3, demo_oracle, n_count=3))
