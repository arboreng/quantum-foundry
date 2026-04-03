# Quantum Approximate Optimization Algorithm (QAOA)

Maturity: **experimental** (v0.1 skeleton)

Reference implementation of QAOA: a hybrid classical-quantum algorithm
approximating solutions to combinatorial optimization problems, targeting
MaxCut (partition a graph's vertices to maximize edges crossing the
partition). Built to demonstrate production-quality engineering rather
than a toy demo. See [RFC-0008](../../docs/rfcs/0008-qaoa.md) for
motivation, milestones, and success criteria — including how this is the
first algorithm in this repo with a parameterized circuit and a classical
optimization loop, rather than a fixed circuit with a bounded retry.

## Quick Start

```bash
uv run python -m algorithms.qaoa.implementation
```

## Layout

- [math.md](math.md) — combinatorial optimization via cost/mixer
  Hamiltonians, why alternating them approximates the optimum, contrast
  with every prior RFC's fixed-circuit-with-guarantee shape
- [paper.md](paper.md) — circuit derivation (`H^n -> p layers of (cost
  gate, mixer gate) -> measure`) and the classical optimization loop
- [problems.py](problems.py) — the `Problem` interface and `MaxCutProblem`
- [circuit.py](circuit.py) — `mixer_gate`, `build_qaoa_circuit`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `solve_maxcut`
  (includes the `scipy.optimize`-driven classical loop)
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

Skeleton only — see [RFC-0008](../../docs/rfcs/0008-qaoa.md) milestones for
what's next (v0.2: core implementation).
