# Variational Quantum Eigensolver (VQE)

Maturity: **experimental** (v0.2 core implementation)

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
- [hamiltonians.py](hamiltonians.py) — the `Hamiltonian` interface and
  `TransverseFieldIsingHamiltonian`
- [circuit.py](circuit.py) — `ansatz_circuit`, `measurement_circuit`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `solve_ground_state`
  (includes the `scipy.optimize`-driven classical loop)
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

v0.2 core implementation is done: `solve_ground_state(hamiltonian,
reps=1)` runs end to end on `AerSimulator`, using `scipy.optimize.minimize`
(COBYLA) to tune the hardware-efficient ansatz's parameters against the
sampled expectation value, then returns a ground-state energy estimate.
Validated against exact diagonalization (`numpy`) of small transverse-
field Ising chains in `tests/test_vqe.py` — not a guarantee of reaching
the true ground energy for larger instances, since VQE is variational/
approximate by construction (see math.md). See
[RFC-0009](../../docs/rfcs/0009-vqe.md) for the v0.5 (feature complete:
benchmarks, demo notebook) and later milestones.
