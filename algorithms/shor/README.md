# Shor's Algorithm

Maturity: **experimental** (RFC-0001 v0.8, RFC-0002 v0.8)

Implementation of Shor's algorithm for integer factorization,
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
  implementations (`PermutationMatrixOracle`, `GateDecomposedOracle`, the
  latter built on [../../arithmetic/adders.py](../../arithmetic/adders.py) —
  see [../../arithmetic/math.md](../../arithmetic/math.md) and
  [../../arithmetic/paper.md](../../arithmetic/paper.md) for that
  construction's own derivation)
- [circuit.py](circuit.py) — phase estimation circuit construction
- [execution.py](execution.py) — the `Executor` interface (`AerExecutor`)
  circuit execution runs through
- [implementation.py](implementation.py) — end-to-end factorization routine
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/shor.md](../../benchmarks/shor.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite (`test_shor.py` for the default oracle,
  `test_gate_decomposed_oracle.py` for RFC-0002's)
- [notebooks/shor_demo.ipynb](notebooks/shor_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

**[RFC-0001](../../docs/rfcs/0001-shors-algorithm.md)** is done through v0.8:
`factor(15)` / `factor(21)` run end to end on `AerSimulator` via a general
(not hardcoded-per-N) permutation-matrix oracle
(`oracles.PermutationMatrixOracle`, the default), with benchmarks
([benchmarks/shor.md](../../benchmarks/shor.md)) and a demo notebook
([notebooks/shor_demo.ipynb](notebooks/shor_demo.ipynb)) both in place, plus
a full README/math.md/paper.md documentation pass. Done through v1.0 too —
see the repo root's [CONTRIBUTING.md](../../CONTRIBUTING.md) and
[LICENSE](../../LICENSE).

**[RFC-0002](../../docs/rfcs/0002-gate-decomposed-arithmetic.md)** is done
through v0.8 (and v1.0, folded in alongside RFC-0001): `oracles.
GateDecomposedOracle` is a drop-in alternative built from actual reversible
adder circuits (`arithmetic/adders.py` — Draper's QFT-based constant adder,
Beauregard's modular adder, controlled modular multiplication; see
[../../arithmetic/math.md](../../arithmetic/math.md) and
[../../arithmetic/paper.md](../../arithmetic/paper.md)), available via
`factor(n, oracle_cls=GateDecomposedOracle)`. It is significantly slower to
simulate than the default (that's the point — it's the elementary-gate
construction the default oracle deliberately skips), so it isn't the default
and its test coverage is narrower — see
[../../benchmarks/shor.md](../../benchmarks/shor.md) for exactly how much
(qubit count, gate count, circuit depth, simulation time at N=15/21).

`execution.Executor` remains a third extension seam — swap `AerExecutor` for
a real-hardware or noise-aware backend without touching the algorithm (no RFC
yet).
