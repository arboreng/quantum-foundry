# Variational Quantum Eigensolver (VQE)

Maturity: **experimental** (v0.8 documentation)

Reference implementation of VQE: a hybrid classical-quantum algorithm
estimating a Hamiltonian's ground-state energy via a parameterized ansatz
and a classical optimization loop. Built to demonstrate production-quality
engineering rather than a toy demo. See [RFC-0009](../../docs/rfcs/0009-vqe.md)
for motivation, milestones, and success criteria — including how this
generalizes [algorithms/qaoa/](../qaoa/)'s classical-optimization-loop
pattern from a diagonal cost function to an arbitrary Pauli-sum
Hamiltonian.

## Quick Start

```bash
uv run python -m algorithms.vqe.implementation
```

## Layout

- [math.md](math.md) — the variational principle, Pauli-string
  decomposition, measuring non-diagonal Hamiltonians, contrast with
  QAOA's diagonal cost function
- [paper.md](paper.md) — circuit derivation (hardware-efficient ansatz,
  per-term basis rotation) and the classical optimization loop
- [hamiltonians.py](hamiltonians.py) — the `Hamiltonian` interface,
  `TransverseFieldIsingHamiltonian`, and `group_qwc_terms` (measurement
  grouping)
- [circuit.py](circuit.py) — `ansatz_circuit`, `measurement_circuit`,
  `group_measurement_circuit`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `solve_ground_state`
  / `solve_ground_state_grouped` (includes the `scipy.optimize`-driven
  classical loop)
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/vqe.md](../../benchmarks/vqe.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/vqe_demo.ipynb](notebooks/vqe_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

Done through v0.5: `solve_ground_state(hamiltonian, reps=1)` runs end to
end on `AerSimulator`, using `scipy.optimize.minimize` (COBYLA) to tune the
hardware-efficient ansatz's parameters against the sampled expectation
value, then returns a ground-state energy estimate. Validated against
exact diagonalization (`numpy`) of small transverse-field Ising chains in
`tests/test_vqe.py` — not a guarantee of reaching the true ground energy
for larger instances, since VQE is variational/approximate by construction
(see math.md). Benchmarks and a demo notebook are both in place — notably,
[benchmarks/vqe.md](../../benchmarks/vqe.md) found that a more expressive
ansatz (`reps=2`) doesn't recover a better energy than `reps=1` here,
since the classical loop's fixed initial guess and iteration budget don't
scale with the parameter count. Done through v0.8 (documentation). See
[RFC-0009](../../docs/rfcs/0009-vqe.md) for v1.0 (public release, folded
in alongside RFC-0001/0002/0003/0004/0005/0006/0007/0008).

**Beyond v0.8**: RFC-0009's "measurement grouping" stretch goal is now
implemented — `hamiltonians.group_qwc_terms` batches qubit-wise-commuting
Pauli terms so `implementation.expectation_value_grouped` /
`solve_ground_state_grouped` run one circuit per group instead of one per
term, cutting `TransverseFieldIsingHamiltonian`'s circuit executions from
`2*n_qubits - 1` down to exactly 2, regardless of `n_qubits` — verified
both for correctness (same expectation value as the ungrouped path) and
for the actual execution-count reduction in `tests/test_vqe.py`. See
math.md's "Measurement grouping" section.
