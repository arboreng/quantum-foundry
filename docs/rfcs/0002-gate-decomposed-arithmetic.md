# RFC-0002: Gate-Decomposed Modular Arithmetic

Status: Draft

## Vision

A second, hardware-realistic oracle for Shor's algorithm: modular
multiplication synthesized from elementary reversible-arithmetic gates
(adders → modular adders → controlled modular multipliers), rather than
[RFC-0001](0001-shors-algorithm.md)'s classically-computed permutation
matrix.

## Why This Should Exist

[RFC-0001](0001-shors-algorithm.md)'s "Known simplifications" and "Explicit
Non-goals" deliberately deferred synthesizing the modular-multiplication
oracle from elementary gates — the permutation-matrix oracle is exact and
general, but a `UnitaryGate` built from a classically-computed matrix isn't
something that runs on real hardware. This RFC replaces that gap with an
actual gate-decomposed construction, without touching the algorithm
(`implementation.py`) or the QPE circuit shape (`circuit.py`) that RFC-0001
already validated — only the oracle changes, via the `Oracle` seam RFC-0001
built for exactly this purpose.

## Prior Art

-   T. Draper, "Addition on a Quantum Computer" (2000) — QFT-based constant
    adder.
-   S. Beauregard, "Circuit for Shor's algorithm using 2n+3 qubits" (2002) —
    modular adder and controlled modular multiplication built on Draper's
    adder.
-   Vedral, Barenco, Ekert, "Quantum Networks for Elementary Arithmetic
    Operations" (1996) — the classical reference for reversible arithmetic
    circuits generally (ripple-carry alternative to Draper's construction;
    not used here, see Architecture).

## Architecture

-   `arithmetic/qft.py` — `qft`/`inverse_qft`, relocated from
    `algorithms/shor/circuit.py` (RFC-0001) since they are now a shared
    dependency of both the phase-estimation circuit and the new adders.
-   `arithmetic/adders.py` — `add_constant_gate` (Draper adder),
    `add_constant_mod_N_gate` (Beauregard modular adder),
    `controlled_mult_mod_N_gate` (controlled modular multiplication by a
    classical constant, via repeated modular addition of shifted constants
    and a controlled-swap uncomputation trick).
-   `algorithms/shor/oracles.py` — `GateDecomposedOracle`, a second
    implementation of RFC-0001's `Oracle` protocol built on
    `arithmetic.adders`. The `Oracle` protocol gains a `num_ancilla_qubits`
    field so `build_order_finding_circuit` can allocate the scratch qubits
    this construction needs (RFC-0001's `PermutationMatrixOracle` needs
    none).
-   No changes to the QPE circuit shape, `implementation.py`'s algorithm
    logic, or `execution.py`. `factor`/`find_order` gain an `oracle_cls`
    parameter (default unchanged: `PermutationMatrixOracle`) so this is
    additive, not a replacement.

## Technology Choices

Python, Qiskit (same as RFC-0001).

## Milestones

-   [x] v0.2: Core implementation (adders, modular adder, controlled
    modular multiplier, `GateDecomposedOracle`, tests at N=15/21) — no
    separate v0.1 skeleton; this RFC starts from RFC-0001's already-scaffolded
    repo structure.
-   [x] v0.5: Benchmarks comparing qubit/gate count and simulation time
    against RFC-0001's `PermutationMatrixOracle` — see
    [benchmarks/shor.md](../../benchmarks/shor.md).
-   [ ] v0.8: Documentation (math.md/paper.md equivalents for the adder
    constructions).
-   [ ] v1.0: Folded into the public release alongside RFC-0001.

## Explicit Non-goals (v0.2)

This RFC is about the *correctness* of elementary-gate modular arithmetic,
not NISQ-readiness:

-   No hardware execution
-   No T-count or gate-count optimization
-   No custom transpiler/hardware-aware layout work
-   No ripple-carry (Cuccaro/VBE) alternative construction — Draper/QFT-based
    only, see [RFC-0001](0001-shors-algorithm.md)'s design review for why
-   No fault tolerance

## Stretch Goals

Ripple-carry adder as an alternative `Oracle` implementation (comparison
benchmark against the QFT-based one); qubit-count-optimal variants.
