# HHL (Harrow-Hassidim-Lloyd)

Maturity: **experimental** (v0.8 documentation)

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
- [circuit.py](circuit.py) — `build_hhl_circuit`,
  `build_amplified_hhl_circuit` (amplitude amplification)
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `solve_linear_system`
  and `amplify_and_solve_linear_system`
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/hhl.md](../../benchmarks/hhl.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/hhl_demo.ipynb](notebooks/hhl_demo.ipynb) — end-to-end demo
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
classical solution. Benchmarks and a demo notebook are both in place —
notably, [benchmarks/hhl.md](../../benchmarks/hhl.md) found that adding
clock-register precision (`n_clock`) doesn't just cost more circuit: it
also makes a successful (ancilla-`1`) shot rarer, since the multiplexed
rotation's safety margin (`c_constant`) must shrink as `n_clock` grows.
Done through v0.8 (documentation). See
[RFC-0010](../../docs/rfcs/0010-hhl.md) for v1.0 (public release, folded
in alongside RFC-0001/0002/0003/0004/0005/0006/0007/0008/0009).

**Beyond v0.8**: RFC-0010's "amplitude amplification" stretch goal is now
implemented — `build_amplified_hhl_circuit` / `amplify_and_solve_
linear_system` run Brassard-Hoyer-Mosca-Tapp amplitude amplification
before measuring, boosting the postselection success probability
(`optimal_amplification_iterations` picks the iteration count from an
estimated success probability) without changing the b-register's
conditional solution distribution — verified exactly (via `Statevector`,
no shot noise) against the closed-form `sin((2k+1)*theta)**2` formula in
`tests/test_hhl.py`. See math.md's "Amplitude amplification" section.
