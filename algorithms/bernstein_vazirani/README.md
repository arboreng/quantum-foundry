# Bernstein-Vazirani Algorithm

Maturity: **experimental** (v0.5 feature complete)

Reference implementation of the Bernstein-Vazirani algorithm: given an
oracle for `f(x) = s.x mod 2` for a hidden bitstring `s`, recover `s` with a
single query. Built to demonstrate production-quality engineering rather
than a toy demo. See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
for motivation, milestones, and success criteria (shared with
[algorithms/deutsch_jozsa/](../deutsch_jozsa/), whose `circuit.py` this
directory reuses — same circuit shape, different oracle/problem).

## Quick Start

```bash
uv run python -m algorithms.bernstein_vazirani.implementation
```

## Layout

- [math.md](math.md) — the hidden-string recovery problem, why one query
  suffices, contrast with Deutsch-Jozsa
- [paper.md](paper.md) — circuit derivation (reuses
  `algorithms/deutsch_jozsa/circuit.py`'s `build_oracle_query_circuit`)
- [oracles.py](oracles.py) — the `Oracle` interface and `HiddenStringOracle`
- [circuit.py](circuit.py) — re-exports the shared circuit builder
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `find_hidden_string`
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/deutsch-jozsa-bernstein-vazirani.md](../../benchmarks/deutsch-jozsa-bernstein-vazirani.md)
  for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/bernstein_vazirani_demo.ipynb](notebooks/bernstein_vazirani_demo.ipynb)
  — end-to-end demo
- [references.bib](references.bib) — citations

## Status

Done through v0.5: `find_hidden_string(n_qubits, oracle)` runs end to end on
`AerSimulator`, deterministic in a single shot (no retry loop — see
math.md), recovering the hidden string exactly for any `s` including the
degenerate all-zeros case; benchmarks and a demo notebook are both in
place. See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
for v0.8 (documentation) and v1.0.
