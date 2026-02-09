# RFC-0003: Hardware-Aware Transpilation

Status: Draft

## Vision

Measure and demonstrate what limited qubit connectivity actually costs a
quantum circuit: transpile [RFC-0002](0002-gate-decomposed-arithmetic.md)'s
`GateDecomposedOracle` circuits against a hand-built, connectivity-limited
hardware model, quantify the routing overhead this introduces, and confirm
`factor()` still produces correct results once actually executed through
that constrained transpilation.

## Why This Should Exist

[RFC-0001](0001-shors-algorithm.md)'s "Explicit Non-goals" deliberately
deferred "custom transpiler/hardware-aware layout work" — `execution.
AerExecutor` transpiles with no coupling-map constraint, i.e. implicitly
assumes every qubit can interact with every other qubit, which no real
device provides. This RFC picks that up without touching the algorithm or
either oracle: it's purely about what happens between "here is a correct
circuit" and "here is what a connectivity-limited device would actually
run."

## Prior Art

-   Qiskit's SABRE routing pass (the default router `transpile()` uses when
    given a `coupling_map`) — Li, Ding, Xie, "Tackling the Qubit Mapping
    Problem for NISQ-Era Quantum Devices" (2019).
-   Standard superconducting-qubit basis gate sets (`rz`, `sx`, `x`, `cx` —
    the gate set IBM's transpiler targets by default).

## Architecture

-   `compiler/targets.py` — a hand-built `qiskit.transpiler.CouplingMap`
    (linear nearest-neighbor) and basis gate list. Not a full `qiskit.
    transpiler.Target` (no duration/error calibration — this is about
    connectivity/basis constraints, not noise) and not `qiskit-ibm-runtime`'s
    fake backends (avoids a new dependency, keeps the constraint fully
    transparent).
-   `compiler/transpilation.py` — `analyze_transpilation`, a thin wrapper
    around `qiskit.transpile()` that reports qubit count, gate count, circuit
    depth, and SWAP-gate count (the actual signature of routing overhead).
-   `algorithms/shor/execution.py` gains `ConstrainedAerExecutor` — a second
    `Executor` (RFC-0001's seam) that transpiles against the hardware model
    before running, alongside the existing unconstrained `AerExecutor`.
-   No changes to `implementation.py`'s algorithm logic, `circuit.py`'s
    circuit shape, or either `Oracle` implementation.

## Technology Choices

Python, Qiskit (same as RFC-0001/0002). No new dependencies.

## Milestones

-   [x] v0.2: Core implementation — `compiler/targets.py`,
    `compiler/transpilation.py`, `ConstrainedAerExecutor`, routing-overhead
    study across `optimization_level` 0-3, and an end-to-end correctness
    check that `factor()` still works through the constrained transpilation.
-   [x] v0.5: Benchmarks written up — see
    [benchmarks/shor-transpilation.md](../../benchmarks/shor-transpilation.md).
-   [ ] v0.8: Documentation (math.md/paper.md-equivalent for the routing
    problem, if warranted once v0.2 is done).
-   [ ] v1.0: Folded into the public release alongside RFC-0001/0002.

## Explicit Non-goals (v0.2)

-   No custom transpiler passes beyond Qiskit's built-in ones (SABRE
    routing, the standard optimization passes at each `optimization_level`).
-   No noise or error-rate modeling — this is a structural/connectivity
    study, not a noise study.
-   No real hardware execution.
-   No exploration beyond one coupling-map topology (linear); a ring or
    heavy-hex-like topology is a stretch goal, not required here.
-   `PermutationMatrixOracle` is out of scope — transpiling its dense
    `UnitaryGate` synthesis to a constrained target measures Qiskit's
    unitary synthesis, not routing overhead on elementary-gate arithmetic.

## Stretch Goals

A second coupling-map topology (ring, heavy-hex-like) for comparison; a
custom transpiler pass exploring gate-cancellation opportunities specific to
the modular-adder structure.
