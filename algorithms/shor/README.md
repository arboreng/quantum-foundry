# Shor's Algorithm

Maturity: **experimental** (v0.2 core implementation)

Reference implementation of Shor's algorithm for integer factorization,
built to demonstrate production-quality engineering rather than a toy demo.
See [RFC-0001](../../docs/rfcs/0001-shors-algorithm.md) (algorithm, default
permutation-matrix oracle) and [RFC-0002](../../docs/rfcs/0002-gate-decomposed-arithmetic.md)
(gate-decomposed alternative oracle) for motivation, milestones, and success
criteria.

## Quick Start

```bash
uv run python -m algorithms.shor.implementation
```

## Layout

- [math.md](math.md) — number-theoretic foundations (order finding, period
  finding, why factoring reduces to it)
- [paper.md](paper.md) — circuit derivation from the math (QFT, modular
  exponentiation)
- [oracles.py](oracles.py) — the `Oracle` interface and its two
  implementations (`PermutationMatrixOracle`, `GateDecomposedOracle`)
- [circuit.py](circuit.py) — phase estimation circuit construction
- [implementation.py](implementation.py) — end-to-end factorization routine
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

**RFC-0001 (v0.2 core implementation)** is done: `factor(15)` / `factor(21)`
run end to end on `AerSimulator` via a general (not hardcoded-per-N)
permutation-matrix oracle (`oracles.PermutationMatrixOracle`, the default).

**RFC-0002 (gate-decomposed arithmetic)** is also done: `oracles.
GateDecomposedOracle` is a drop-in alternative built from actual reversible
adder circuits (`arithmetic/adders.py` — Draper's QFT-based constant adder,
Beauregard's modular adder, controlled modular multiplication), available via
`factor(n, oracle_cls=GateDecomposedOracle)`. It is significantly slower to
simulate than the default (that's the point — it's the elementary-gate
construction the default oracle deliberately skips) so it isn't the default
and its test coverage is narrower — see
[../../benchmarks/shor.md](../../benchmarks/shor.md) for exactly how much
(qubit count, gate count, circuit depth, simulation time at N=15/21).

`execution.Executor` remains a third extension seam — swap `AerExecutor` for
a real-hardware or noise-aware backend without touching the algorithm (no RFC
yet).
