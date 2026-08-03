# Simon's Algorithm

Maturity: **experimental**

Implementation of Simon's algorithm: given an oracle for a
function `f: {0,1}^n -> {0,1}^n` promised to be one-to-one or exactly
two-to-one with `f(x) = f(x XOR s)` for an unknown nonzero hidden period
`s`, find `s`. Built to demonstrate rigorous engineering rather than a toy
implementation. See [RFC-0006](../../docs/rfcs/0006-simons-algorithm.md)
for motivation, milestones, and success criteria.

## Quick Start

```bash
uv run python -m algorithms.simon.implementation
```

## Layout

- [math.md](math.md) — the hidden-period problem, why measured bitstrings
  satisfy `y.s = 0 mod 2`, classical GF(2) linear algebra needed to recover
  `s`
- [paper.md](paper.md) — circuit derivation (`H^n -> oracle -> H^n ->
  measure input register`)
- [oracles.py](oracles.py) — the `Oracle` interface, `LinearOracle`,
  `PermutationOracle`
- [circuit.py](circuit.py) — `build_simon_circuit`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `find_hidden_period`
  (includes from-scratch GF(2) Gaussian elimination)
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/simon.md](../../benchmarks/simon.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/simon_demo.ipynb](notebooks/simon_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

`find_hidden_period(n_qubits, oracle)` runs end to end on `AerSimulator`,
collecting independent equations until they are solvable via a from-scratch
GF(2) Gaussian elimination. Two oracle types are available: an efficient
`LinearOracle` and a general but exponential `PermutationOracle`.

`tests/test_simon.py` checks both oracles against their truth tables and
against the structure they promise (`LinearOracle`'s kernel is exactly `s`;
`PermutationOracle` is exactly two-to-one with period `s`), verifies every
measured `y` satisfies `y.s = 0 mod 2`, exercises the GF(2) routines against
a hand-worked example, and recovers `s` end to end for both oracles.
Benchmarks ([benchmarks/simon.md](../../benchmarks/simon.md)) and a demo
notebook ([notebooks/simon_demo.ipynb](notebooks/simon_demo.ipynb)) are in
place.

Limitations: both oracles are two-to-one by construction, so
`find_hidden_period` never exercises the one-to-one branch of the promise
problem and does not classically verify a candidate `s`. `PermutationOracle`
enumerates an explicit permutation over all `2**n` inputs — general, but a
small-`n` construction rather than a scalable one. See math.md's "Known
limitations" and paper.md's "Known simplifications".
