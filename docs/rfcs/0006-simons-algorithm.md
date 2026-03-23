# RFC-0006: Simon's Algorithm From Scratch

Status: Draft

## Vision

Educational quantum computing reference implementation of Simon's
algorithm: given oracle access to a function `f: {0,1}^n -> {0,1}^n`
promised to be either one-to-one, or exactly two-to-one with `f(x) = f(x
XOR s)` for an unknown nonzero hidden period `s`, find `s`.

## Why This Should Exist

The same "general, not hardcoded" differentiator established in
[RFC-0001](0001-shors-algorithm.md), [RFC-0004](0004-grovers-algorithm.md),
and [RFC-0005](0005-deutsch-jozsa-bernstein-vazirani.md): a general oracle
abstraction for an arbitrary hidden period, not a single hardcoded example.
Simon's algorithm is also the natural next stepping stone in the "hidden
subgroup problem" family — [algorithms/bernstein_vazirani/math.md](../algorithms/bernstein_vazirani/math.md)
already flags it as the link between Bernstein-Vazirani's single hidden
string and the order-finding subroutine at the heart of
[algorithms/shor/](../algorithms/shor/): Simon's is the first algorithm in
this repo where the oracle maps to a multi-qubit output register (`{0,1}^n
-> {0,1}^n`, not `{0,1}^n -> {0,1}`), and where recovering the hidden
structure needs genuine classical post-processing (linear algebra over
GF(2), not just reading a bitstring or a continued fraction).

## Prior Art

-   D. Simon, "On the power of quantum computation" (1994).
-   [algorithms/bernstein_vazirani/](../algorithms/bernstein_vazirani/),
    [algorithms/shor/](../algorithms/shor/) — the `Oracle`/`Executor`
    architectural pattern this reuses, and the hidden-subgroup-problem
    lineage this continues.

## Architecture

-   `algorithms/simon/oracles.py` — an `Oracle` protocol (`oracle_gate() ->
    Gate` acting on `2*n_qubits` qubits: `n_qubits` input + `n_qubits`
    output register, implementing `|x>|y> -> |x>|y XOR f(x)>`), with two
    implementations:
    -   `LinearOracle(s)` — `f(x) = Mx` for an `n x n` binary matrix `M`
        with kernel exactly `{0, s}`, built from `O(n^2)` CNOTs (one per set
        bit of `M`, generalizing
        [algorithms/deutsch_jozsa/oracles.py](../algorithms/deutsch_jozsa/oracles.py)'s
        `ParityOracle`'s single linear functional to a full matrix of them).
        Efficient, exact for the broad class of linear/affine two-to-one
        functions.
    -   `PermutationOracle(s)` — an explicit lookup mapping each pair `{x,
        x XOR s}` to an arbitrary unique label, general for *any*
        two-to-one function (not just linear ones) but exponential setup
        cost, small-`n_qubits` only (mirrors `BalancedOracle`'s role for
        Deutsch-Jozsa, `PermutationMatrixOracle`'s for Shor).
-   `algorithms/simon/circuit.py` — `build_simon_circuit`: `H^n` on the
    input register, apply the oracle, `H^n` on the input register again,
    measure the input register only (the output register is never
    measured — same "prepare, apply, undo, measure the input side" shape as
    [algorithms/deutsch_jozsa/circuit.py](../algorithms/deutsch_jozsa/circuit.py)'s
    `build_oracle_query_circuit`, but without the phase-kickback ancilla
    trick, since here the output register's *entanglement* with the input
    is the point, not a phase).
-   `algorithms/simon/implementation.py` — `find_hidden_period(n_qubits,
    oracle)`: repeatedly runs the circuit, collecting measured bitstrings
    `y` (each satisfying `y . s = 0 mod 2`) until `n_qubits - 1` linearly
    independent equations are found, then solves the resulting linear
    system over GF(2) for `s` (new: this repo's first classical
    post-processing step that isn't a simple bitstring read or a continued
    fraction — a small from-scratch GF(2) Gaussian elimination, not a
    numpy/sympy dependency).
-   `algorithms/simon/execution.py` — the standard per-algorithm
    `Executor` protocol + `AerExecutor`.

## Technology Choices

Python, Qiskit (same as RFC-0001/0002/0003/0004/0005). GF(2) linear algebra
implemented from scratch (small, self-contained — not worth a new
dependency).

## Milestones

-   [x] v0.1: Skeleton
-   [x] v0.2: Core implementation
-   [x] v0.5: Feature complete (benchmarks — see
    [benchmarks/simon.md](../../benchmarks/simon.md); demo notebook — see
    [algorithms/simon/notebooks/simon_demo.ipynb](../../algorithms/simon/notebooks/simon_demo.ipynb))
-   [x] v0.8: Documentation (References sections were already added to
    math.md/paper.md during v0.2 this time, learning from the retrofit
    needed in prior RFCs; README/references.bib were already current)
-   [ ] v1.0: Public release

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

-   No hardware execution.
-   No fault tolerance, distributed simulation, or GPU acceleration.
-   `PermutationOracle`'s explicit pair-lookup construction is exponential
    in `n_qubits` by design (mirrors `BalancedOracle`'s/`PermutationMatrixOracle`'s
    tradeoff) — only practical for small `n_qubits` demos.
-   No gate-decomposed/hardware-aware-transpilation follow-up RFCs for this
    algorithm (mirrors RFC-0005's framing) unless a future need arises.

## Stretch Goals

A worked connection from Simon's period-finding to Shor's order-finding
(both hidden-subgroup problems, solved with structurally similar
Hadamard-oracle-Hadamard-measure circuits, differing in the group being
hidden and the classical post-processing needed to extract it).
