# RFC-0007: Quantum Phase Estimation From Scratch

Status: Draft

## Vision

Educational quantum computing reference implementation of Quantum Phase
Estimation (QPE): given a unitary `U` and (an approximation of) one of its
eigenstates `|psi>` with eigenvalue `e^(2*pi*i*theta)`, estimate `theta`.

## Why This Should Exist

QPE is the general subroutine [algorithms/shor/](../algorithms/shor/)'s
order-finding circuit is a special case of: Shor's `Oracle` protocol
(`controlled_power_gate(power) -> Gate`) is exactly "a unitary you can get
controlled powers of" — QPE's core requirement — specialized to modular
multiplication with the uniform-superposition-over-the-work-register trick
standing in for an eigenstate. This RFC makes that generalization concrete
as its own algorithm: a general `Oracle`-like abstraction for *any* unitary,
not just modular multiplication, plus a standalone demonstration (estimating
a single-qubit phase gate's angle) that has nothing to do with factoring.

## Prior Art

-   Kitaev, "Quantum measurements and the Abelian Stabilizer Problem"
    (1995) — the original phase estimation algorithm.
-   Nielsen & Chuang, *Quantum Computation and Quantum Information*,
    Section 5.2.
-   [algorithms/shor/](../algorithms/shor/), specifically
    `algorithms/shor/oracles.py`'s `Oracle` protocol and
    `algorithms/shor/circuit.py`'s `build_order_finding_circuit` — the
    special case this RFC generalizes. See "Architecture" for why this RFC
    does *not* refactor that already-tested code to share implementation,
    only documents the connection.
-   `arithmetic/qft.py` — QPE's inverse-QFT step reuses this directly (a
    third consumer, after `algorithms/shor/circuit.py` and
    `arithmetic/adders.py`).

## Architecture

-   `algorithms/qpe/oracles.py` — an `Oracle` protocol
    (`controlled_power_gate(power) -> Gate`, `num_qubits`), structurally the
    same shape as `algorithms/shor/oracles.py`'s but for an arbitrary
    unitary rather than modular multiplication specifically.
    `PhaseGateOracle(theta)`: single-qubit phase gate `P(2*pi*theta)`,
    eigenstate `|1>`, `controlled_power_gate(power)` returns
    controlled-`P(2*pi*theta*power)` (since `P(phi)^power = P(phi*power)`).
-   `algorithms/qpe/circuit.py` — `build_qpe_circuit(n_count, oracle,
    eigenstate_prep)`: `H^n_count` on the counting register, `eigenstate_prep`
    on the eigenstate register, controlled `oracle.controlled_power_gate(2**k)`
    per counting qubit, `arithmetic.qft.inverse_qft` on the counting
    register (reused directly, not reimplemented), measure the counting
    register.
-   `algorithms/qpe/implementation.py` — `estimate_phase(oracle,
    eigenstate_prep, n_count) -> float`, converting the measured bitstring
    to `theta_hat = int(bitstring, 2) / 2**n_count`.
-   No changes to `algorithms/shor/`'s existing code — the connection is
    documented (math.md/paper.md cross-links showing Shor's `Oracle` is a
    QPE controlled-unitary applied to a uniform superposition instead of a
    true eigenstate), not refactored into shared implementation, to avoid
    refactor risk to already-tested, working code for what is primarily a
    pedagogical/documentation win.

## Technology Choices

Python, Qiskit (same as RFC-0001 through 0006).

## Milestones

-   [x] v0.1: Skeleton
-   [x] v0.2: Core implementation
-   [ ] v0.5: Feature complete (benchmarks, demo notebook)
-   [ ] v0.8: Documentation
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

-   No refactor of `algorithms/shor/`'s working code to share
    implementation with this RFC (see Architecture).
-   No hardware execution.
-   No fault tolerance, distributed simulation, or GPU acceleration.
-   No general eigenstate-finding (the caller must supply a state
    preparation circuit for a known/assumed eigenstate — this RFC doesn't
    address what happens when `eigenstate_prep` only approximately
    prepares an eigenstate, beyond noting it in math.md as a known
    limitation).

## Stretch Goals

Precision/confidence analysis (relating `n_count` to estimation error and
success probability, generalizing
[algorithms/shor/math.md](../algorithms/shor/math.md)'s continued-fraction
precision argument); semiclassical/iterative QPE (Kitaev's original,
one-counting-qubit-at-a-time variant, using only 1 ancilla instead of
`n_count`).
