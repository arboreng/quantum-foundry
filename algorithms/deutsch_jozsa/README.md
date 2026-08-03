# Deutsch-Jozsa Algorithm

Maturity: **experimental**

Implementation of the Deutsch-Jozsa algorithm: given a boolean
function promised to be constant or balanced, determine which with a single
query. Built to demonstrate rigorous engineering rather than a toy
implementation. See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
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
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/deutsch-jozsa-bernstein-vazirani.md](../../benchmarks/deutsch-jozsa-bernstein-vazirani.md)
  for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/deutsch_jozsa_demo.ipynb](notebooks/deutsch_jozsa_demo.ipynb) —
  end-to-end demo
- [references.bib](references.bib) — citations

## Status

`is_constant(n_qubits, oracle)` runs end to end on `AerSimulator`,
deterministic in a single shot with no retry loop (see math.md). Three
oracle types are available: `ConstantOracle`, an efficient always-balanced
`ParityOracle`, and a general but exponential `BalancedOracle`.

`tests/test_deutsch_jozsa.py` checks each oracle against its truth table and
its input validation, and runs `is_constant` end to end against all three
(including the single-qubit case). Benchmarks
([benchmarks/deutsch-jozsa-bernstein-vazirani.md](../../benchmarks/deutsch-jozsa-bernstein-vazirani.md))
and a demo notebook
([notebooks/deutsch_jozsa_demo.ipynb](notebooks/deutsch_jozsa_demo.ipynb))
are in place.

Limitations: `BalancedOracle`'s explicit marked-set construction is exact
but exponential — a balanced function on many qubits would in practice be
given by a formula, as `ParityOracle`'s is. Execution is validated against
`AerSimulator` only. See paper.md's "Known simplifications".
