# Variational Quantum Eigensolver (VQE)

Maturity: **experimental**

Implementation of VQE: a hybrid classical-quantum algorithm
estimating a Hamiltonian's ground-state energy via a parameterized ansatz
and a classical optimization loop. Built to demonstrate rigorous
engineering rather than a toy implementation. See [RFC-0009](../../docs/rfcs/0009-vqe.md)
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
  `TransverseFieldIsingHamiltonian`, `HeisenbergHamiltonian`, and
  `group_qwc_terms` (measurement grouping)
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

`solve_ground_state(hamiltonian, reps=1)` runs end to end on `AerSimulator`,
using `scipy.optimize.minimize` (COBYLA) to tune the hardware-efficient
ansatz's parameters against the sampled expectation value, then returns a
ground-state energy estimate. `hamiltonians.group_qwc_terms` batches
qubit-wise-commuting Pauli terms so
`implementation.expectation_value_grouped` / `solve_ground_state_grouped`
run one circuit per group instead of one per term, cutting
`TransverseFieldIsingHamiltonian`'s circuit executions from
`2*n_qubits - 1` down to exactly 2 regardless of `n_qubits`. Two
Hamiltonians are implemented: the transverse-field Ising model and the
isotropic Heisenberg (XXX) model, the latter exercising
`measurement_circuit`'s `Y`-basis rotation and splitting into 3 measurement
groups rather than 2.

`tests/test_vqe.py` checks the ansatz and measurement circuits against
explicit constructions, validates the energy estimate against exact
diagonalization (`numpy`) of small chains of both Hamiltonians, and checks
the grouped path both for correctness (same expectation value as the
ungrouped path) and for the actual execution-count reduction. Benchmarks
([benchmarks/vqe.md](../../benchmarks/vqe.md)) and a demo notebook
([notebooks/vqe_demo.ipynb](notebooks/vqe_demo.ipynb)) are in place.

Limitations: VQE is variational and approximate by construction, so matching
exact diagonalization on small chains is not a guarantee of reaching the
true ground energy for larger instances, and no convergence-rate analysis is
offered beyond the variational principle's `<psi|H|psi> >= E_0`. A more
expressive ansatz does not automatically help —
[benchmarks/vqe.md](../../benchmarks/vqe.md) found `reps=2` recovering no
better energy than `reps=1`, since the classical loop's fixed initial guess
and iteration budget don't scale with the parameter count. The Heisenberg
chain's doubly-degenerate ground energy needs more ansatz depth (`reps=3`)
to reach reliably, a property of the optimization landscape rather than a
bug. `group_qwc_terms`' greedy grouping is not optimal in general (that is
an NP-hard graph-coloring problem), though it is exact for both
Hamiltonians' structures. See math.md's "Known limitations", "Measurement
grouping", and "The Heisenberg model" sections.
