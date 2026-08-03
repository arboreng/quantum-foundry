# Quantum Phase Estimation

Maturity: **experimental**

Implementation of Quantum Phase Estimation (QPE): given a unitary
`U` and one of its eigenstates `|psi>` with eigenvalue `e^(2*pi*i*theta)`,
estimate `theta`. Built to demonstrate rigorous engineering rather than a
toy implementation. See
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

`estimate_phase(oracle, eigenstate_prep, n_count)` runs end to end on
`AerSimulator`, exactly recovering `theta` when it has a terminating
`n_count`-bit binary expansion and within `1/2**n_count` otherwise (with the
probabilistic guarantee math.md describes). `build_qpe_circuit` reuses
`arithmetic/qft.py`'s `inverse_qft` directly — the same construction
`algorithms/shor/circuit.py` uses.
`semiclassical.estimate_phase_semiclassical` provides Kitaev's iterative
variant: a single reused ancilla with classical feedback between rounds,
instead of `n_count` ancillas plus a coherent inverse QFT.

`tests/test_qpe.py` checks `PhaseGateOracle` against its expected unitary at
each power and `estimate_phase` on both terminating and non-terminating
`theta`; `tests/test_semiclassical.py` cross-validates the iterative variant
against `estimate_phase`, recovering the same `theta` on every exact
instance. Benchmarks ([benchmarks/qpe.md](../../benchmarks/qpe.md)) and a
demo notebook ([notebooks/qpe_demo.ipynb](notebooks/qpe_demo.ipynb)) are in
place, alongside a precision/confidence study
([benchmarks/qpe-precision-confidence.md](../../benchmarks/qpe-precision-confidence.md))
running 300 trials at each of several extra-counting-qubit levels: the
`4/pi^2` lower bound holds comfortably, and failure probability roughly
halves per extra qubit.

Limitations: `eigenstate_prep` is assumed to prepare an eigenstate exactly.
Given an approximate eigenstate or a superposition of several — as Shor's
construction deliberately uses — the measured phase becomes a probabilistic
mixture over the component eigenphases, which this implementation does not
address. See math.md's "Known limitations" and paper.md's "Known
simplifications".
