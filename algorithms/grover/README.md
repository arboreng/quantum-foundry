# Grover's Algorithm

Maturity: **experimental** (v0.8 documentation)

Implementation of Grover's algorithm for unstructured search,
built to demonstrate production-quality engineering rather than a toy demo.
See [RFC-0004](../../docs/rfcs/0004-grovers-algorithm.md) for motivation,
milestones, and success criteria.

## Quick Start

```bash
uv run python -m algorithms.grover.implementation
```

## Layout

- [math.md](math.md) — number-theoretic/probability foundations (amplitude
  amplification, why `round(pi/(4*theta) - 1/2)` iterations)
- [paper.md](paper.md) — circuit derivation from the math (oracle, diffusion
  operator)
- [oracles.py](oracles.py) — the `Oracle` interface and
  `MarkedBitstringOracle`
- [circuit.py](circuit.py) — circuit construction
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end search routine
- [counting.py](counting.py) — quantum counting: estimate the number of
  marked items without knowing it in advance
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/grover.md](../../benchmarks/grover.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/grover_demo.ipynb](notebooks/grover_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

Done through v0.5: `search(n_qubits, marked)` runs end to end on
`AerSimulator` via a general (arbitrary marked-set) multi-controlled-Z
oracle (`oracles.MarkedBitstringOracle`), with iteration count computed
exactly from `len(marked)`; benchmarks
([benchmarks/grover.md](../../benchmarks/grover.md)) and a demo notebook
([notebooks/grover_demo.ipynb](notebooks/grover_demo.ipynb)) are both in
place. Done through v0.8 (documentation) and v1.0 (folded into the
public release alongside every other RFC in this repo — see the root
[CONTRIBUTING.md](../../CONTRIBUTING.md) and
[LICENSE](../../LICENSE)). See
[RFC-0004](../../docs/rfcs/0004-grovers-algorithm.md).

**Beyond v0.8**: RFC-0004's "quantum counting" stretch goal is now
implemented — `counting.count(n_qubits, oracle, n_count)` estimates the
number of marked items via QPE applied to the Grover iteration operator,
removing `search`'s biggest standing assumption (that the caller already
knows `M`). Building this surfaced a genuine subtlety: `circuit.
diffusion_operator` carries an extra global phase (relative to the
textbook `2|s><s| - I`) that's unobservable in plain Grover search but
becomes a real phase offset once the operator is used under control, as
QPE requires — `counting.count` corrects for it rather than changing
`diffusion_operator` itself (already correct for search, and not worth
the refactor risk to already-tested code). See math.md's "Quantum
counting" section.
