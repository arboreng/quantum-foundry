# Grover's Algorithm

Maturity: **experimental**

Implementation of Grover's algorithm for unstructured search,
built to demonstrate rigorous engineering rather than a toy implementation.
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

`search(n_qubits, marked)` runs end to end on `AerSimulator` via a general
(arbitrary marked-set) multi-controlled-Z oracle
(`oracles.MarkedBitstringOracle`), with the iteration count computed exactly
from `len(marked)`. `counting.count(n_qubits, oracle, n_count)` lifts
`search`'s standing assumption that the caller already knows how many items
are marked, estimating that count via QPE applied to the Grover iteration
operator.

`tests/test_grover.py` checks the diffusion operator and the oracle against
their closed-form matrices, confirms the chosen iteration count maximizes
success probability, and runs `search` end to end;
`tests/test_counting.py` checks the controlled iteration powers against
matrix powers, and `count` against both an exact instance and its closed
form. Benchmarks ([benchmarks/grover.md](../../benchmarks/grover.md)) and a
demo notebook ([notebooks/grover_demo.ipynb](notebooks/grover_demo.ipynb))
are in place.

One limitation matters before reusing the pieces individually:
`circuit.diffusion_operator` carries an extra global phase relative to the
textbook `2|s><s| - I`. That is unobservable in plain Grover search, but
becomes a real phase offset once the operator is used under control, as QPE
requires — `counting.count` corrects for it rather than changing
`diffusion_operator`, which is correct for search as written. See math.md's
"Quantum counting" section and paper.md's "Known simplifications".
