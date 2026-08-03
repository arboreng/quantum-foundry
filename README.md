# Quantum Foundry

> Quantum Foundry is an open collection of quantum algorithm implementations,
> documented and tested with the engineering rigor expected of production
> software and the transparency expected of scientific computing.

## Motivation

Many public quantum algorithm implementations are presented as toy
demonstrations or embedded in framework examples. Quantum Foundry aims to be
neither:
each algorithm gets a rigorously documented, benchmarked, and tested
implementation, organized under a consistent architecture. See [docs/rfcs/](docs/rfcs/) for the design record behind each algorithm.

## Project principles

Each implementation should make the path from theory to executable software explicit: why the algorithm exists, its mathematical foundations, its circuit derivation, its software implementation, and—when available—its behavior on real hardware. Major algorithm additions begin with an RFC; architecture changes are recorded as ADRs. Tests, benchmarks, reproducible examples, CI, static analysis, versioning, and documentation are part of the engineering standard rather than post-release polish.

The repository uses five documentation levels:

0. **Engineer intuition** — what the algorithm does and why it matters.
1. **Mathematics** — the mathematical foundations and derivation.
2. **Circuit derivation** — how the mathematics becomes a quantum circuit.
3. **Implementation** — how the circuit and algorithm are expressed in software.
4. **Hardware behavior** — what changes when the implementation reaches real hardware.

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

## Current scope

The repository currently contains nine algorithm implementations: Shor, Grover, Deutsch-Jozsa, Bernstein-Vazirani, Simon, Quantum Phase Estimation, QAOA, VQE, and HHL, with the Shor work also covering gate-decomposed arithmetic and hardware-aware transpilation. Each has tests, benchmarks, and mathematical/circuit documentation. Several also contain extensions beyond their original RFC milestone; see each algorithm's `README.md`. Cross-algorithm infrastructure includes hardware-aware transpilation comparison and a known-answer cross-validation harness under [validation/](validation/).

`hardware/` remains reserved for Level 4 hardware-behavior results. No algorithm is currently classified as `reference`; the maturity table in [algorithms/README.md](algorithms/README.md) is authoritative.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, the RFC
process for proposing a new algorithm, and pull request expectations.
To report a vulnerability, see [SECURITY.md](SECURITY.md); suspected
algorithmic *correctness* bugs are normal issues, and that document
explains the difference.
Licensed under the [MIT License](LICENSE).
