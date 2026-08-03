# Shor's Algorithm

Maturity: **experimental**

Implementation of Shor's algorithm for integer factorization,
built to demonstrate rigorous engineering rather than a toy implementation.
See [RFC-0001](../../docs/rfcs/0001-shors-algorithm.md) (algorithm, default
permutation-matrix oracle) and [RFC-0002](../../docs/rfcs/0002-gate-decomposed-arithmetic.md)
(gate-decomposed alternative oracle) for motivation, milestones, and success
criteria.

## Quick Start

```bash
uv run python -m algorithms.shor.implementation
```

## Layout

- [math.md](math.md) — number-theoretic foundations (order finding, period
  finding, why factoring reduces to it)
- [paper.md](paper.md) — circuit derivation from the math (QFT, modular
  exponentiation)
- [oracles.py](oracles.py) — the `Oracle` interface and its two
  implementations (`PermutationMatrixOracle`, `GateDecomposedOracle`, the
  latter built on [../../arithmetic/adders.py](../../arithmetic/adders.py) —
  see [../../arithmetic/math.md](../../arithmetic/math.md) and
  [../../arithmetic/paper.md](../../arithmetic/paper.md) for that
  construction's own derivation)
- [circuit.py](circuit.py) — phase estimation circuit construction
- [execution.py](execution.py) — the `Executor` interface (`AerExecutor`)
  circuit execution runs through
- [implementation.py](implementation.py) — end-to-end factorization routine
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/shor.md](../../benchmarks/shor.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite (`test_shor.py` for the default oracle,
  `test_gate_decomposed_oracle.py` for RFC-0002's)
- [notebooks/shor_demo.ipynb](notebooks/shor_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

`factor(15)` / `factor(21)` run end to end on `AerSimulator` via a general
(not hardcoded-per-N) permutation-matrix oracle
(`oracles.PermutationMatrixOracle`, the default).
`oracles.GateDecomposedOracle` is a drop-in alternative built from actual
reversible adder circuits (`arithmetic/adders.py` — Draper's QFT-based
constant adder, Beauregard's modular adder, controlled modular
multiplication; see [../../arithmetic/math.md](../../arithmetic/math.md) and
[../../arithmetic/paper.md](../../arithmetic/paper.md)), selected via
`factor(n, oracle_cls=GateDecomposedOracle)`. `execution.Executor` is a
third extension seam: swap `AerExecutor` for a real-hardware or noise-aware
backend without touching the algorithm.

`tests/test_shor.py` checks the permutation matrices against classical
modular multiplication, the classical pre- and post-processing (perfect
powers, even inputs, factor recovery from a known order), and `find_order` /
`factor` end to end. `tests/test_gate_decomposed_oracle.py` checks the
gate-decomposed oracle against the permutation-matrix one directly, runs it
end to end at N=15/21, and confirms order finding survives
[RFC-0003](../../docs/rfcs/0003-hardware-aware-transpilation.md)'s
constrained, hardware-aware transpilation. Benchmarks
([benchmarks/shor.md](../../benchmarks/shor.md)) and a demo notebook
([notebooks/shor_demo.ipynb](notebooks/shor_demo.ipynb)) are in place.

Limitations: `GateDecomposedOracle` is significantly slower to simulate than
the default — it is the elementary-gate construction the permutation-matrix
oracle deliberately skips — so it is not the default and its test coverage
is narrower; [benchmarks/shor.md](../../benchmarks/shor.md) quantifies the
gap (qubit count, gate count, circuit depth, simulation time at N=15/21).
Neither oracle is NISQ-optimized for gate or T count, and both are validated
against `AerSimulator` only, not against real hardware or a noise model. See
paper.md's "Known simplifications".
