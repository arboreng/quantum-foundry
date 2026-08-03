# RFC-0004: Grover's Algorithm From Scratch

Status: Implemented

## Vision

Educational quantum computing reference implementation of Grover's
algorithm for unstructured search, built with the same engineering rigor as
[RFC-0001](0001-shors-algorithm.md)'s Shor's algorithm implementation.

## Why This Should Exist

A focused educational reference that demonstrates rigorous engineering
rather than a toy implementation — most public Grover
implementations hardcode a single marked bitstring for a fixed small `N`;
this one should work for an arbitrary search space size and an arbitrary set
of marked items, the same "general, not hardcoded" differentiator RFC-0001
established for Shor's algorithm.

## Prior Art

-   L. Grover, "A fast quantum mechanical algorithm for database search"
    (1996) — the original algorithm.
-   Brassard, Høyer, Mosca, "Quantum Amplitude Amplification and
    Estimation" (2000) — the generalization Grover's algorithm is a special
    case of, and the standard reference for quantum counting (unknown-`M`
    search), out of scope for this RFC's v0.2 (see Non-goals).
-   [algorithms/shor/](../../algorithms/shor/) — the `Oracle`/`Executor`
    architectural seams this implementation reuses the *pattern* of (not the
    code — Grover's oracle is a different mathematical object from Shor's
    modular-multiplication oracle).

## Architecture

-   `algorithms/grover/oracles.py` — an `Oracle` protocol (phase-flip on
    marked states) with a `MarkedBitstringOracle` implementation built from
    multi-controlled-Z gates, exact and general for any search-space size
    and any set of marked bitstrings — analogous to
    [RFC-0001](0001-shors-algorithm.md)'s `PermutationMatrixOracle` as the
    v0.2 baseline that a future gate-decomposed (compiled-from-a-boolean-
    predicate) oracle could extend, mirroring
    [RFC-0002](0002-gate-decomposed-arithmetic.md)'s relationship to
    RFC-0001.
-   `algorithms/grover/circuit.py` — the full circuit: `H` on all qubits,
    then the oracle and diffusion operator repeated the iteration count
    computed from a known number of marked items `M`.
-   `algorithms/grover/execution.py` — an `Executor` protocol, reusing the
    RFC-0001 pattern (not the code — this is a separate module per
    algorithm) so a future hardware or noise-aware backend is a drop-in
    swap.
-   `algorithms/grover/implementation.py` — `search(n_qubits, marked, ...)`
    driving circuit construction, execution, and measurement interpretation.

## Technology Choices

Python, Qiskit (same as RFC-0001/0002/0003).

## Milestones

-   [x] v0.1: Skeleton
-   [x] v0.2: Core implementation
-   [x] v0.5: Feature complete (benchmarks — see
    [benchmarks/grover.md](../../benchmarks/grover.md); demo notebook — see
    [algorithms/grover/notebooks/grover_demo.ipynb](../../algorithms/grover/notebooks/grover_demo.ipynb))
-   [x] v0.8: Documentation (References sections added to math.md/paper.md;
    README/references.bib were already current from v0.2/v0.5)
-   [x] v1.0: Public release (LICENSE, CONTRIBUTING.md, and CI added;
    publishing to a public GitHub remote is a manual step the repo
    owner performs, not tracked in commit history)

## Seed GitHub Issues

-   Project scaffolding
-   Tests
-   Benchmarks
-   Documentation

## README Outline

-   Motivation
-   Quick Start
-   Architecture
-   Examples
-   Benchmarks
-   Roadmap
-   Contributing

## Explicit Non-goals (v0.2)

So reviewers see these as deliberately deferred, not overlooked:

-   No gate-decomposed oracle synthesis from an arbitrary boolean predicate
    or circuit (mirrors RFC-0001's non-goal that became RFC-0002; a future
    RFC could pick this up the same way).
-   No quantum counting / unknown-`M` search (Brassard-Høyer-Mosca) — `M`
    (the number of marked items) must be known/provided.
-   No hardware execution.
-   No custom transpiler/hardware-aware layout work (mirrors RFC-0001; a
    future RFC could pick this up the way RFC-0003 did for Shor).
-   No fault tolerance, distributed simulation, or GPU acceleration.

## Stretch Goals

-   ~~Quantum counting for unknown `M`~~ — **implemented**, beyond v0.8:
    `counting.count`, see
    [algorithms/grover/math.md](../../algorithms/grover/math.md)'s "Quantum
    counting" section (including a genuine phase-offset subtlety this
    surfaced in `circuit.diffusion_operator`).
-   Oracle compilation from an arbitrary boolean predicate/circuit.
-   Amplitude amplification beyond the uniform-superposition-initial-
    state case (RFC-0010's HHL now implements the general form of this).
