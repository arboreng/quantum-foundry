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

# Run an algorithm's example entry point (once implemented)
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
aggregated under [benchmarks/](benchmarks/). No results are published yet.

## Roadmap

See [VISION.md](VISION.md#long-term-vision) for the target algorithm list and
[docs/rfcs/0001-shors-algorithm.md](docs/rfcs/0001-shors-algorithm.md) for the
current milestone (v0.1: Skeleton).

## Contributing

The project is pre-public-release; contribution guidelines will land before
the v1.0 milestone. In the meantime, every algorithm begins with an RFC under
`docs/rfcs/` describing motivation, design, validation, and success criteria.
