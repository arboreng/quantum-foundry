# Quantum Approximate Optimization Algorithm (QAOA)

Maturity: **experimental** (v0.8 documentation)

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
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/qaoa.md](../../benchmarks/qaoa.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/qaoa_demo.ipynb](notebooks/qaoa_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

Done through v0.5: `solve_maxcut(n_qubits, edges, p=1)` runs end to end on
`AerSimulator`, using `scipy.optimize.minimize` (COBYLA) to tune the QAOA
parameters against the sampled expectation value, then returns the
best-measured cut. Finds the true optimal cut for the small test graphs in
`tests/test_qaoa.py` (a triangle, a 4-cycle, a path) — not a guarantee for
larger instances, since QAOA is approximate by construction (see math.md).
Benchmarks and a demo notebook are both in place. Done through v0.8
(documentation) and v1.0 (folded into the public release alongside
every other RFC in this repo — see the root
[CONTRIBUTING.md](../../CONTRIBUTING.md) and
[LICENSE](../../LICENSE)). See [RFC-0008](../../docs/rfcs/0008-qaoa.md).

**Beyond v0.8**: RFC-0008's "optimizer comparison" stretch goal is now
done — [benchmarks/qaoa-optimizer-comparison.md](../../benchmarks/qaoa-optimizer-comparison.md)
runs COBYLA against BFGS (gradient-based, finite-difference) on the same
instance: both reach the optimum every trial, but BFGS costs ~3.3x more
circuit evaluations for no accuracy benefit, confirming empirically what
paper.md's "classical optimization loop" section already argued
theoretically. See math.md's "Why COBYLA over a gradient-based
optimizer" section.
