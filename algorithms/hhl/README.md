# HHL (Harrow-Hassidim-Lloyd)

Maturity: **experimental**

Implementation of HHL: given a Hermitian matrix `A` and
efficient preparation of `|b>`, produce (conditioned on a postselected
ancilla measurement) the quantum state proportional to the solution
`x = A^-1 b`. Built to demonstrate rigorous engineering rather than a toy
implementation. See [RFC-0010](../../docs/rfcs/0010-hhl.md) for
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
- [oracles.py](oracles.py) — the `Oracle` interface, `DiagonalXOracle`,
  and `GeneralSingleQubitOracle` (any single-qubit Hermitian matrix)
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

`solve_linear_system(oracle, t, n_clock, c_constant, b_state_prep)` runs end
to end on `AerSimulator` for the `A = a*I + b*X` demo system, returning the
postselected (ancilla `1`) success probability and the b-register's
conditional measurement distribution. `build_amplified_hhl_circuit` /
`amplify_and_solve_linear_system` add Brassard-Hoyer-Mosca-Tapp amplitude
amplification before measuring, raising the postselection success
probability (`optimal_amplification_iterations` picks the iteration count
from an estimated success probability) without changing the b-register's
conditional distribution. `oracles.GeneralSingleQubitOracle` covers
`A = a*I + v.sigma` for any real 3-vector `v` via an arbitrary-Bloch-axis
rotation, not just the `X`-aligned `DiagonalXOracle`.

`tests/test_hhl.py` validates the oracle's controlled time-evolution gate
against `scipy.linalg.expm`'s exact matrix exponential, the clock register's
exact uncomputation against the circuit's statevector (no shot noise), the
full postselected output against both a single-eigenvalue closed form and
`numpy.linalg.solve`'s classical solution — including a negative-eigenvalue
system — and the amplified success probability against the closed-form
`sin((2k+1)*theta)**2`. `tests/test_oracles_general.py` checks the general
oracle against `scipy.linalg.expm`, against `DiagonalXOracle` for the
`X`-only case, and end to end for a genuinely 3D axis. Benchmarks
([benchmarks/hhl.md](../../benchmarks/hhl.md)) and a demo notebook
([notebooks/hhl_demo.ipynb](notebooks/hhl_demo.ipynb)) are in place.

Limitations: added clock-register precision (`n_clock`) is not purely a
circuit-size cost — it also makes a successful (ancilla-`1`) shot rarer,
since the multiplexed rotation's safety margin (`c_constant`) must shrink as
`n_clock` grows (see [benchmarks/hhl.md](../../benchmarks/hhl.md)). `|0>`
splits
evenly across eigenvectors only when the Bloch axis is orthogonal to `Z`, as
`DiagonalXOracle`'s demo instance happens to be; a general axis needs that
overlap computed by diagonalization rather than assumed. Only 2x2 systems
are implemented, `optimal_amplification_iterations` requires the unamplified
success probability to be known or separately estimated, and no
condition-number analysis is derived beyond citing the original result. See
math.md's "Known limitations", "Amplitude amplification", and "Generalizing
beyond the `X` axis" sections.
