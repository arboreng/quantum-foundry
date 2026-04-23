# HHL (Harrow-Hassidim-Lloyd)

Maturity: **experimental** (v0.2 core implementation)

Reference implementation of HHL: given a Hermitian matrix `A` and
efficient preparation of `|b>`, produce (conditioned on a postselected
ancilla measurement) the quantum state proportional to the solution
`x = A^-1 b`. Built to demonstrate production-quality engineering rather
than a toy demo. See [RFC-0010](../../docs/rfcs/0010-hhl.md) for
motivation, milestones, and success criteria — including how this reuses
[algorithms/qpe/](../qpe/)'s controlled-power-of-unitary `Oracle` pattern
and introduces this repo's first postselection-based success shape.

## Quick Start

```bash
uv run python -m algorithms.hhl.implementation
```

## Layout

- [math.md](math.md) — the linear systems problem, using QPE to estimate
  eigenvalues, the conditional rotation, why success is postselected
- [paper.md](paper.md) — circuit derivation (state prep -> QPE ->
  multiplexed rotation -> inverse QPE -> measure)
- [oracles.py](oracles.py) — the `Oracle` interface and `DiagonalXOracle`
- [circuit.py](circuit.py) — `build_hhl_circuit`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `solve_linear_system`
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

v0.2 core implementation is done: `solve_linear_system(oracle, t,
n_clock, c_constant, b_state_prep)` runs end to end on `AerSimulator` for
the `A = a*I + b*X` demo system, returning the postselected (ancilla `1`)
success probability and the b-register's conditional measurement
distribution. Validated three ways in `tests/test_hhl.py`: the oracle's
controlled time-evolution gate against `scipy.linalg.expm`'s exact matrix
exponential, the clock register's exact uncomputation against the
circuit's statevector (no shot noise), and the full postselected output
against both a single-eigenvalue closed form and `numpy.linalg.solve`'s
classical solution. See [RFC-0010](../../docs/rfcs/0010-hhl.md) for the
v0.5 (feature complete: benchmarks, demo notebook) and later milestones.
