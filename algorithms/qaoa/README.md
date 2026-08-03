# Quantum Approximate Optimization Algorithm (QAOA)

Maturity: **experimental**

Implementation of QAOA: a hybrid classical-quantum algorithm
approximating solutions to combinatorial optimization problems, targeting
MaxCut (partition a graph's vertices to maximize edges crossing the
partition). Built to demonstrate rigorous engineering rather than a toy
implementation. See [RFC-0008](../../docs/rfcs/0008-qaoa.md) for
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

`solve_maxcut(n_qubits, edges, p=1)` runs end to end on `AerSimulator`,
using `scipy.optimize.minimize` (COBYLA) to tune the QAOA parameters against
the sampled expectation value, then returns the best-measured cut.

`tests/test_qaoa.py` checks the cost and mixer gates against their exact
unitaries, confirms the sampled expectation value is bounded by the optimal
cost, and finds the true optimal cut for small graphs (a triangle, a
4-cycle, a path). Benchmarks ([benchmarks/qaoa.md](../../benchmarks/qaoa.md))
and a demo notebook ([notebooks/qaoa_demo.ipynb](notebooks/qaoa_demo.ipynb))
are in place, alongside an optimizer comparison
([benchmarks/qaoa-optimizer-comparison.md](../../benchmarks/qaoa-optimizer-comparison.md))
running COBYLA against finite-difference BFGS on the same instance: both
reach the optimum every trial, but BFGS costs ~3.3x more circuit evaluations
for no accuracy benefit.

Limitations: QAOA is approximate by construction, so reaching the optimum on
these small graphs is not a guarantee for larger instances. No
approximation-ratio bound is derived or checked; `p` and the initial
parameter guess are fixed rather than tuned per instance; and MaxCut is the
only problem implemented, though `Problem` could generalize to other
QUBO/Ising-encodable ones. See math.md's "Known limitations" and "Why COBYLA
over a gradient-based optimizer".
