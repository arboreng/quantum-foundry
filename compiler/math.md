# Hardware-Aware Transpilation — Foundations

**Math Version 1.0.** Written for [RFC-0003](../docs/rfcs/0003-hardware-aware-transpilation.md);
mirrors the versioning convention set by
[algorithms/shor/math.md](../algorithms/shor/math.md) and
[arithmetic/math.md](../arithmetic/math.md).

Level 1 of [VISION.md's understanding model](../VISION.md#levels-of-understanding),
for the constructions in [transpilation.py](transpilation.py) and
[targets.py](targets.py).

## The qubit-mapping problem

A circuit is written assuming any qubit can interact with any other (a
2-qubit gate `cx(3, 17)` is just as valid to write down as `cx(3, 4)`). Real
hardware doesn't offer that: each qubit is physically wired to only a few
neighbors (a **coupling map**), and a 2-qubit gate can only execute directly
between qubits that share an edge in that map. Given a circuit and a
coupling map, **qubit mapping** is the problem of (a) choosing an initial
assignment of the circuit's logical qubits to physical qubits, and (b)
inserting `swap` gates wherever a 2-qubit gate's operands aren't adjacent
under the current assignment, so that every gate in the final circuit only
ever acts on physically-adjacent qubits. Finding the assignment and swap
placement that minimizes overhead is NP-hard in general (it's a graph
minor-embedding problem); real transpilers use heuristics.

`compiler/targets.py`'s `linear_coupling_map` builds the most
connectivity-constrained realistic topology (a chain, where qubit `i` is
only adjacent to `i-1` and `i+1`) deliberately — it's the topology where
routing overhead is most visible, which is the point of this RFC's study
(see [benchmarks/shor-transpilation.md](../benchmarks/shor-transpilation.md)).

## SABRE routing

`qiskit.transpile()`'s default router (used whenever a `coupling_map` is
given, as `compiler.transpilation.analyze_transpilation` does) is **SABRE**
(Li, Ding, Xie 2019): a heuristic that runs the circuit forward and backward
several times, at each step picking whichever candidate `swap` reduces the
total remaining distance (in coupling-map graph edges) between not-yet-adjacent
gate operands, and using the final pass's qubit assignment as the initial
layout for a clean forward pass. It doesn't guarantee the minimum number of
swaps, but it is fast enough to run on circuits with hundreds of thousands
of gates (as [benchmarks/shor-transpilation.md](../benchmarks/shor-transpilation.md)'s
~7-15 second transpile times for a 1.3M-gate circuit demonstrate) — an exact
minimum-swap solver would not be.

## Basis translation is a separate concern from routing

Even with perfect connectivity, most gates in a circuit (`p`, `cp`, `ccx`,
custom `UnitaryGate`s, ...) aren't things real hardware executes directly —
devices support a small fixed **basis gate set** (here, `rz`, `sx`, `x`,
`cx` — a standard single-qubit-rotation-plus-CNOT set used by many
superconducting processors) and everything else must be decomposed into it.
This is why `analyze_transpilation` runs `transpile()` at all even without a
coupling map: `basis_gates` alone (no `coupling_map`) still forces
translation. The two are logically independent — a circuit can be
routing-compliant but not in the target basis, or vice versa — but Qiskit's
`transpile()` does both together, which is *why* `swap` gates (not in the
basis) silently decompose into `cx` unless kept in the basis explicitly (see
paper.md's "the swap-counting trick").

## Optimization levels

`optimization_level` (0-3) trades transpile time for output quality: level 0
does the minimum required (trivial layout, routing, direct basis
translation, no cleanup); higher levels add increasingly aggressive
gate-cancellation, commutation-based reordering, and better initial-layout
search. [benchmarks/shor-transpilation.md](../benchmarks/shor-transpilation.md)
shows this concretely: level 0 to level 1 is a real improvement (12.9x to
10.5x gate-count overhead vs. unconstrained), but level 2 and 3 buy only a
further ~2% at roughly double the transpile time — for this circuit, level 1
already captures nearly all of what's available.

## Common misconceptions

- **Routing overhead is not a bug or an artifact of this repo's circuits.**
  Every circuit with 2-qubit gates between non-adjacent logical qubits needs
  swaps on any real device's limited connectivity; RFC-0002's
  `GateDecomposedOracle` triggers a lot of it because its `ccx`-heavy
  modular-adder structure has many such interactions, not because anything
  is implemented incorrectly.
- **A higher optimization level is not strictly "more correct."** All four
  levels produce logically equivalent circuits (verified by
  `test_find_order_survives_hardware_aware_transpilation`); they differ only
  in resource cost, not in what they compute.
- **This is a structural study, not a noise study.** No error rates, gate
  durations, or decoherence are modeled here — see RFC-0003's non-goals.
  More gates and more depth *correlate* with more real-world error on actual
  hardware, but that correlation itself isn't derived or measured in this
  repo.
