# Shor's Algorithm

Maturity: **experimental** (v0.1 skeleton)

Reference implementation of Shor's algorithm for integer factorization,
built to demonstrate production-quality engineering rather than a toy demo.
See [RFC-0001](../../docs/rfcs/0001-shors-algorithm.md) for motivation,
milestones, and success criteria.

## Quick Start

```bash
uv run python -m algorithms.shor.implementation
```

## Layout

- [math.md](math.md) — number-theoretic foundations (order finding, period
  finding, why factoring reduces to it)
- [paper.md](paper.md) — circuit derivation from the math (QFT, modular
  exponentiation)
- [circuit.py](circuit.py) — circuit construction
- [implementation.py](implementation.py) — end-to-end factorization routine
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

v0.2 core implementation is done: `factor(15)` / `factor(21)` run end to end
on `AerSimulator` via a general (not hardcoded-per-N) permutation-matrix
oracle. Two extension seams exist for future RFCs:

- `oracles.Oracle` — swap `PermutationMatrixOracle` for a gate-decomposed
  (Beauregard/Cuccaro) oracle without touching `circuit.py` or
  `implementation.py`.
- `execution.Executor` — swap `AerExecutor` for a real-hardware or
  noise-aware backend without touching the algorithm.

See [RFC-0001](../../docs/rfcs/0001-shors-algorithm.md) for the v0.5 (feature
complete: gate-decomposed oracle, richer benchmarks) and later milestones.
