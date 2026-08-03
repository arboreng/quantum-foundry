# Quantum Phase Estimation

Maturity: **experimental** (v0.8 documentation)

Implementation of Quantum Phase Estimation (QPE): given a unitary
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
- [semiclassical.py](semiclassical.py) — `estimate_phase_semiclassical`
  (Kitaev iterative phase estimation, a single reused ancilla instead of
  `n_count`)
- [benchmark.py](benchmark.py) — resource/performance benchmarks (see
  [../../benchmarks/qpe.md](../../benchmarks/qpe.md) for results)
- [visualization.py](visualization.py) — circuit and result visualization
- [tests/](tests/) — test suite
- [notebooks/qpe_demo.ipynb](notebooks/qpe_demo.ipynb) — end-to-end demo
- [references.bib](references.bib) — citations

## Status

Done through v0.5: `estimate_phase(oracle, eigenstate_prep, n_count)` runs
end to end on `AerSimulator`, exactly recovering `theta` when it has a
terminating `n_count`-bit binary expansion, and within `1/2**n_count`
otherwise (with the probabilistic guarantee math.md describes).
`build_qpe_circuit` reuses `arithmetic/qft.py`'s `inverse_qft` directly —
the same construction `algorithms/shor/circuit.py` uses, now independently
validated by a second consumer. Benchmarks and a demo notebook are both in
place. Done through v0.8 (documentation) and v1.0 (folded into the
public release alongside every other RFC in this repo — see the root
[CONTRIBUTING.md](../../CONTRIBUTING.md) and
[LICENSE](../../LICENSE)). See
[RFC-0007](../../docs/rfcs/0007-quantum-phase-estimation.md).

**Beyond v0.8**: RFC-0007's "semiclassical/iterative QPE" stretch goal is
now implemented — `semiclassical.estimate_phase_semiclassical` uses a
single reused ancilla with classical feedback between rounds (Kitaev's
iterative phase estimation) instead of `n_count` ancillas plus a coherent
inverse QFT, verified to recover exactly the same `theta` as
`estimate_phase` on every exact test instance. Getting the round order
and bit-significance right took a genuine wrong turn first — see math.md's
"Semiclassical (Kitaev iterative) phase estimation" section for how
cross-validating against `estimate_phase` caught it.

RFC-0007's "precision/confidence analysis" stretch goal is also done —
[benchmarks/qpe-precision-confidence.md](../../benchmarks/qpe-precision-confidence.md)
runs 300 trials at each of several extra-counting-qubit levels, confirming
math.md's `4/pi^2` lower bound holds (comfortably, since it's a
guarantee not a typical value) and that failure probability roughly
halves per extra qubit — while being explicit about the sampling noise on
that ratio's own tail.
