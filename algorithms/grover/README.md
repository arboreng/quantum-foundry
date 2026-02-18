# Grover's Algorithm

Maturity: **experimental** (v0.1 skeleton)

Reference implementation of Grover's algorithm for unstructured search,
built to demonstrate production-quality engineering rather than a toy demo.
See [RFC-0004](../../docs/rfcs/0004-grovers-algorithm.md) for motivation,
milestones, and success criteria.

## Quick Start

```bash
uv run python -m algorithms.grover.implementation
```

## Layout

- [math.md](math.md) — number-theoretic/probability foundations (amplitude
  amplification, why ~pi/4*sqrt(N/M) iterations)
- [paper.md](paper.md) — circuit derivation from the math (oracle, diffusion
  operator)
- [oracles.py](oracles.py) — the `Oracle` interface and
  `MarkedBitstringOracle`
- [circuit.py](circuit.py) — circuit construction
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end search routine
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

Skeleton only — see [RFC-0004](../../docs/rfcs/0004-grovers-algorithm.md)
milestones for what's next (v0.2: core implementation).
