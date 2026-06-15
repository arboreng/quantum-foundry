# Quantum Foundry

> Quantum Foundry is an open collection of reference implementations for quantum
> algorithms, built with the engineering rigor expected of production software
> and the transparency expected of scientific computing.

## Motivation

Most public quantum algorithm implementations are either toy demonstrations or
buried inside framework example folders. Quantum Foundry aims to be neither:
each algorithm gets a rigorously documented, benchmarked, and tested reference
implementation, organized under a consistent architecture. See
[VISION.md](VISION.md) for the full project philosophy and
[docs/rfcs/](docs/rfcs/) for the design record behind each algorithm.

## Quick Start

```bash
# Install uv if you don't have it: https://docs.astral.sh/uv/
uv sync

# Run the test suite
uv run pytest

# Run an algorithm's example entry point
uv run python -m algorithms.shor.implementation
```

## Architecture

```text
quantum-foundry/
  algorithms/       # One directory per algorithm (see algorithms/README.md)
  arithmetic/       # Shared quantum arithmetic building blocks
  compiler/         # Circuit optimization / transpilation passes
  hardware/         # Hardware backend integration and calibration notes
  visualization/    # Shared plotting and circuit visualization utilities
  benchmarks/       # Cross-algorithm benchmark harness and results
  notebooks/        # Repo-wide exploratory notebooks
  docs/             # RFCs, ADRs, and other design documentation
  papers/           # Reference papers and citations
  validation/       # Cross-validation against known results / other frameworks
  contrib/          # Community-contributed, not-yet-reference-grade work
```

Each algorithm under `algorithms/` follows a maturity model (experimental →
contrib → incubating → reference) with increasing expectations around tests,
documentation, benchmarks, and API stability. See
[algorithms/README.md](algorithms/README.md).

## Examples

See each algorithm's own `README.md` and `notebooks/` directory, e.g.
[algorithms/shor/](algorithms/shor/).

## Benchmarks

Benchmark harnesses live alongside each algorithm (`benchmark.py`) and are
aggregated under [benchmarks/](benchmarks/), including a cross-algorithm
transpilation study ([benchmarks/cross-algorithm-transpilation.md](benchmarks/cross-algorithm-transpilation.md))
comparing routing overhead across every algorithm's circuit shape. See
[benchmarks/README.md](benchmarks/README.md) for the full index.

## Roadmap

All ten algorithms on [VISION.md](VISION.md#long-term-vision)'s long-term
list — Shor ([RFC-0001](docs/rfcs/0001-shors-algorithm.md)/[0002](docs/rfcs/0002-gate-decomposed-arithmetic.md)/[0003](docs/rfcs/0003-hardware-aware-transpilation.md)),
Grover ([RFC-0004](docs/rfcs/0004-grovers-algorithm.md)), Deutsch-Jozsa /
Bernstein-Vazirani ([RFC-0005](docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)),
Simon ([RFC-0006](docs/rfcs/0006-simons-algorithm.md)), Quantum Phase
Estimation ([RFC-0007](docs/rfcs/0007-quantum-phase-estimation.md)), QAOA
([RFC-0008](docs/rfcs/0008-qaoa.md)), VQE ([RFC-0009](docs/rfcs/0009-vqe.md)),
and HHL ([RFC-0010](docs/rfcs/0010-hhl.md)) — are implemented, tested,
benchmarked, and documented through each RFC's v0.8 milestone. Several
have stretch-goal extensions beyond v0.8 (amplitude amplification for
HHL, measurement grouping for VQE, quantum counting for Grover,
semiclassical phase estimation and precision/confidence analysis for
QPE, a general single-qubit oracle for HHL, a Heisenberg model for VQE,
and an optimizer comparison for QAOA) — see each algorithm's own
`README.md` "Beyond v0.8" section. Cross-algorithm infrastructure
(hardware-aware transpilation comparison, a known-answer cross-validation
harness under [validation/](validation/)) is also in place.

`hardware/` (Level 4, hardware-validated results) remains for a future
algorithm reaching `incubating` maturity — see
[algorithms/README.md](algorithms/README.md)'s maturity model.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, the RFC
process for proposing a new algorithm, and pull request expectations.
Licensed under the [MIT License](LICENSE).
