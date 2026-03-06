# Deutsch-Jozsa Algorithm

Maturity: **experimental** (v0.2 core implementation)

Reference implementation of the Deutsch-Jozsa algorithm: given a boolean
function promised to be constant or balanced, determine which with a single
query. Built to demonstrate production-quality engineering rather than a
toy demo. See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
for motivation, milestones, and success criteria (shared with
[algorithms/bernstein_vazirani/](../bernstein_vazirani/), which reuses this
directory's `circuit.py`).

## Quick Start

```bash
uv run python -m algorithms.deutsch_jozsa.implementation
```

## Layout

- [math.md](math.md) — the constant-vs-balanced promise problem, phase
  kickback, why one query suffices
- [paper.md](paper.md) — circuit derivation (`H^n -> oracle -> H^n ->
  measure`)
- [oracles.py](oracles.py) — the `Oracle` interface, `ConstantOracle`,
  `ParityOracle`, `BalancedOracle`
- [circuit.py](circuit.py) — `build_oracle_query_circuit`, shared with
  `algorithms/bernstein_vazirani/`
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `is_constant`
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

v0.2 core implementation is done: `is_constant(n_qubits, oracle)` runs end
to end on `AerSimulator`, deterministic in a single shot (no retry loop —
see math.md). Three oracle types: `ConstantOracle`, an efficient
always-balanced `ParityOracle`, and a general but exponential
`BalancedOracle`. See
[RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md) for the
v0.5 (feature complete: benchmarks, demo notebook) and later milestones.
