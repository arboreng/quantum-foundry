# RFC-0005: Deutsch-Jozsa and Bernstein-Vazirani From Scratch

Status: Implemented

## Vision

Educational quantum computing reference implementations of the
Deutsch-Jozsa and Bernstein-Vazirani algorithms — the two canonical
single-query "oracle interrogation" algorithms, covered together because
they share nearly identical circuit structure (`H^n -> oracle -> H^n ->
measure`) and are conventionally taught as a pair.

## Why This Should Exist

The same "general, not hardcoded" differentiator established in
[RFC-0001](0001-shors-algorithm.md) and [RFC-0004](0004-grovers-algorithm.md):
a general oracle abstraction for arbitrary constant/balanced/linear boolean
functions, not a single hardcoded example function. Bundling both
algorithms under one RFC (rather than two near-duplicate RFCs) reflects how
tightly related they actually are — Bernstein-Vazirani is, mechanically, the
same phase-kickback circuit as Deutsch-Jozsa with a linear-function oracle
in place of a constant/balanced one.

## Prior Art

-   D. Deutsch, R. Jozsa, "Rapid solution of problems by quantum
    computation" (1992).
-   E. Bernstein, U. Vazirani, "Quantum Complexity Theory" (1993/1997).
-   [algorithms/shor/](../../algorithms/shor/), [algorithms/grover/](../../algorithms/grover/)
    — the `Oracle`/`Executor` architectural pattern this reuses (not the
    code — a new pair of algorithms with their own oracle types).

## Architecture

Two separate algorithm directories (each following the standard per-algorithm
template), sharing one circuit-building primitive rather than one merged
directory — reflects that these are two distinct algorithms (different
problems solved: constant-vs-balanced decision vs. hidden-string recovery)
that happen to reuse the same circuit shape, not one algorithm with two
oracle strategies (contrast with how [RFC-0001](0001-shors-algorithm.md)'s
`PermutationMatrixOracle`/`GateDecomposedOracle` are two strategies for the
*same* problem):

-   `algorithms/deutsch_jozsa/circuit.py` — `build_oracle_query_circuit(n_qubits, oracle)`,
    the shared `H^n -> oracle -> H^n -> measure` primitive (ancilla prepared
    in `|->` for phase kickback). Canonical home for this circuit since
    Deutsch-Jozsa is the historically earlier / more foundational of the two.
-   `algorithms/deutsch_jozsa/oracles.py` — `ConstantOracle`, `ParityOracle`
    (an efficient, always-balanced linear function), and `BalancedOracle` (a
    general, explicit marked-half oracle — exact for any balanced function
    but exponential in gate count, the same tradeoff
    `PermutationMatrixOracle` makes for Shor).
-   `algorithms/deutsch_jozsa/implementation.py` — `is_constant(n_qubits, oracle) -> bool`.
-   `algorithms/bernstein_vazirani/circuit.py` — imports and reuses
    `build_oracle_query_circuit` from `algorithms.deutsch_jozsa.circuit`.
-   `algorithms/bernstein_vazirani/oracles.py` — `HiddenStringOracle(s)`,
    `O(n)` gates (one `CX` per set bit of `s`) for any hidden bitstring.
-   `algorithms/bernstein_vazirani/implementation.py` — `find_hidden_string(n_qubits, oracle) -> str`.
-   Each directory gets its own `execution.py` (`Executor` protocol +
    `AerExecutor`), per the established per-algorithm pattern — not shared,
    same as Shor's and Grover's.

Both algorithms are **exact, single-query** (deterministic given a perfect
simulator — no retry loops, unlike Shor's/Grover's inherently probabilistic
algorithms), which is itself worth highlighting pedagogically (see math.md).

## Technology Choices

Python, Qiskit (same as RFC-0001/0002/0003/0004).

## Milestones

-   [x] v0.1: Skeleton (both directories)
-   [x] v0.2: Core implementation (both algorithms working end to end)
-   [x] v0.5: Feature complete (benchmarks — see
    [benchmarks/deutsch-jozsa-bernstein-vazirani.md](../../benchmarks/deutsch-jozsa-bernstein-vazirani.md);
    demo notebooks — see
    [algorithms/deutsch_jozsa/notebooks/deutsch_jozsa_demo.ipynb](../../algorithms/deutsch_jozsa/notebooks/deutsch_jozsa_demo.ipynb)
    and
    [algorithms/bernstein_vazirani/notebooks/bernstein_vazirani_demo.ipynb](../../algorithms/bernstein_vazirani/notebooks/bernstein_vazirani_demo.ipynb))
-   [x] v0.8: Documentation (References sections added to both math.md
    files; READMEs/references.bib were already current from v0.2/v0.5)
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

-   No gate-decomposed/hardware-aware-transpilation follow-up RFCs for
    these two (mirrors RFC-0002/0003's relationship to RFC-0001) unless a
    future need arises — these circuits are already small and shallow, so
    there's less to demonstrate.
-   No hardware execution.
-   No fault tolerance, distributed simulation, or GPU acceleration.
-   `BalancedOracle`'s explicit marked-half construction is exponential in
    `n_qubits` by design (mirrors `PermutationMatrixOracle`'s tradeoff) —
    only practical for small `n_qubits` demos, not a scalability claim.

## Stretch Goals

Simon's algorithm (the next step up in this family in the repository's current algorithm scope — periodicity rather than a single hidden string), a
gate-decomposed `BalancedOracle` alternative.
