# Simon's Algorithm

Maturity: **experimental** (v0.8 documentation)

Reference implementation of Simon's algorithm: given an oracle for a
function `f: {0,1}^n -> {0,1}^n` promised to be one-to-one or exactly
two-to-one with `f(x) = f(x XOR s)` for an unknown nonzero hidden period
`s`, find `s`. Built to demonstrate production-quality engineering rather
than a toy demo. See [RFC-0006](../../docs/rfcs/0006-simons-algorithm.md)
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

Done through v0.5: `find_hidden_period(n_qubits, oracle)` runs end to end
on `AerSimulator`, collecting independent equations until solvable via a
from-scratch GF(2) Gaussian elimination — this repo's first algorithm
needing genuine classical linear algebra rather than a bitstring read or a
continued fraction. Two oracle types: an efficient `LinearOracle` and a
general but exponential `PermutationOracle`; benchmarks and a demo notebook
are both in place. Done through v0.8 (documentation). See
[RFC-0006](../../docs/rfcs/0006-simons-algorithm.md) for v1.0 (public
release, folded in alongside RFC-0001/0002/0003/0004/0005).
