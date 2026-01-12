# algorithms/

One directory per quantum algorithm. Every algorithm directory follows the
same layout:

```text
algorithms/<name>/
  README.md          # Motivation, quick start, current status
  paper.md            # Level 1: mathematical foundations
  math.md              # Level 2: circuit derivation
  implementation.py     # Level 3: software implementation
  circuit.py             # Circuit construction
  benchmark.py             # Performance / resource benchmarks
  visualization.py           # Circuit and result visualization
  tests/                       # Test suite
  notebooks/                    # Exploratory / demo notebooks
  references.bib                 # Citations
```

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
| Shor      | experimental | [RFC-0001](../docs/rfcs/0001-shors-algorithm.md) |
