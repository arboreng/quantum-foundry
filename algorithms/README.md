# algorithms/

One directory per quantum algorithm. Every algorithm directory follows the
same layout:

```text
algorithms/<name>/
  README.md          # Motivation, quick start, current status
  math.md             # Level 1: mathematical foundations
  paper.md             # Level 2: circuit derivation
  oracles.py             # Oracle interface + implementation(s)
  circuit.py               # Circuit construction
  execution.py               # Executor interface + implementation(s)
  implementation.py            # Level 3: end-to-end software implementation
  benchmark.py                   # Performance / resource benchmarks
  visualization.py                 # Circuit and result visualization
  tests/                              # Test suite
  notebooks/                            # Exploratory / demo notebooks
  references.bib                          # Citations
```

`oracles.py` and `execution.py` are separate `Protocol`-based seams (an
`Oracle` for whatever the algorithm's "black box" is, an `Executor` for
circuit execution) — this is what let RFC-0002 and RFC-0003 extend Shor's
algorithm without touching its core logic; see
[algorithms/shor/oracles.py](shor/oracles.py) and
[algorithms/shor/execution.py](shor/execution.py) for the pattern.

See [VISION.md](../VISION.md#levels-of-understanding) for what each level
(engineer intuition → mathematics → circuit derivation → implementation →
hardware behavior) is expected to cover.

## Maturity model

1. **experimental** — exists, may be incomplete or unverified
2. **contrib** — community-contributed, basic tests
3. **incubating** — full test/benchmark coverage, API may still shift
4. **reference** — stable API, full documentation, hardware-validated

## Status

| Algorithm | Maturity     | RFC                                                     |
| --------- | ------------ | -------------------------------------------------------- |
| Shor      | experimental | [RFC-0001](../docs/rfcs/0001-shors-algorithm.md) (+[0002](../docs/rfcs/0002-gate-decomposed-arithmetic.md), [0003](../docs/rfcs/0003-hardware-aware-transpilation.md)) |
| Grover    | experimental | [RFC-0004](../docs/rfcs/0004-grovers-algorithm.md) |
| Deutsch-Jozsa | experimental | [RFC-0005](../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md) |
| Bernstein-Vazirani | experimental | [RFC-0005](../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md) |
| Simon     | experimental | [RFC-0006](../docs/rfcs/0006-simons-algorithm.md) |
| Quantum Phase Estimation | experimental (v0.1 skeleton) | [RFC-0007](../docs/rfcs/0007-quantum-phase-estimation.md) |
