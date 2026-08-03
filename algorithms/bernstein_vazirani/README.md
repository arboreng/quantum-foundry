# Bernstein-Vazirani Algorithm

Maturity: **experimental**

Implementation of the Bernstein-Vazirani algorithm: given an
oracle for `f(x) = s.x mod 2` for a hidden bitstring `s`, recover `s` with a
single query. Built to demonstrate rigorous engineering rather than a toy
implementation. See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
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

`find_hidden_string(n_qubits, oracle)` runs end to end on `AerSimulator`,
deterministic in a single shot with no retry loop (see math.md), recovering
the hidden string exactly for any `s` including the degenerate all-zeros
case.

`tests/test_bernstein_vazirani.py` checks `HiddenStringOracle` against its
truth table and its input validation, and recovers `s` end to end across
hidden strings. Benchmarks
([benchmarks/deutsch-jozsa-bernstein-vazirani.md](../../benchmarks/deutsch-jozsa-bernstein-vazirani.md))
and a demo notebook
([notebooks/bernstein_vazirani_demo.ipynb](notebooks/bernstein_vazirani_demo.ipynb))
are in place.

Limitations: no transpiler-level circuit optimization beyond the default
`transpile()` pass `execution.AerExecutor` applies, and execution is
validated against `AerSimulator` only. See paper.md's "Known
simplifications".
