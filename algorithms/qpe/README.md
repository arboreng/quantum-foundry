# Quantum Phase Estimation

Maturity: **experimental** (v0.2 core implementation)

Reference implementation of Quantum Phase Estimation (QPE): given a unitary
`U` and one of its eigenstates `|psi>` with eigenvalue `e^(2*pi*i*theta)`,
estimate `theta`. Built to demonstrate production-quality engineering
rather than a toy demo. See
[RFC-0007](../../docs/rfcs/0007-quantum-phase-estimation.md) for
motivation, milestones, and success criteria — including how
[algorithms/shor/](../shor/)'s order-finding circuit is a special case of
this one.

## Quick Start

```bash
uv run python -m algorithms.qpe.implementation
```

## Layout

- [math.md](math.md) — the phase estimation problem, precision vs.
  counting-qubit count, connection to Shor's order-finding
- [paper.md](paper.md) — circuit derivation (`H^n_count -> eigenstate_prep
  -> controlled powers of U -> inverse QFT -> measure`)
- [oracles.py](oracles.py) — the `Oracle` interface and `PhaseGateOracle`
- [circuit.py](circuit.py) — `build_qpe_circuit` (reuses
  `arithmetic/qft.py`'s `inverse_qft`)
- [execution.py](execution.py) — the `Executor` interface
- [implementation.py](implementation.py) — end-to-end `estimate_phase`
- [benchmark.py](benchmark.py) — resource/performance benchmarks
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/](notebooks/) — exploratory / demo notebooks
- [references.bib](references.bib) — citations

## Status

v0.2 core implementation is done: `estimate_phase(oracle, eigenstate_prep,
n_count)` runs end to end on `AerSimulator`, exactly recovering `theta`
when it has a terminating `n_count`-bit binary expansion, and within
`1/2**n_count` otherwise (with the probabilistic guarantee math.md
describes). `build_qpe_circuit` reuses `arithmetic/qft.py`'s `inverse_qft`
directly — the same construction `algorithms/shor/circuit.py` uses, now
independently validated by a second consumer. See
[RFC-0007](../../docs/rfcs/0007-quantum-phase-estimation.md) for the v0.5
(feature complete: benchmarks, demo notebook) and later milestones.
