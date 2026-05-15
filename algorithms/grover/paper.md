# Grover's Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md) (Math Version 1.0).

## The oracle: `MarkedBitstringOracle`

`oracles.py`'s `phase_flip_gate` needs to implement `|x> -> -|x>` for each
marked `x`, identity otherwise. Qiskit doesn't have a direct "Z controlled
on an arbitrary bitstring" gate, but a plain multi-controlled-Z
(`ZGate().control(n-1)`, which flips the phase of `|11...1>` only) does —
so for each marked bitstring `m`, the construction is:

1. `X` on every qubit where `m`'s bit is `0` — this remaps `|m>` to
   `|11...1>` (and everything else to some other, non-all-ones state).
2. Multi-controlled-`Z` — flips the phase of exactly `|11...1>`.
3. `X` again on the same qubits — undoes step 1, so the net effect on every
   basis state other than `|m>` is identity, and `|m>` picks up a `-1`.

Repeating this block once per marked bitstring is correct because phase
flips on distinct computational basis states commute and don't interfere —
each block only ever touches its own target state's phase. Verified against
the exact diagonal matrix (`+1` everywhere except `-1` at each marked index)
via `Operator` in `tests/test_grover.py`.

## The diffusion operator

`circuit.py`'s `diffusion_operator` is `H^n -> X^n -> (multi-controlled-Z
on |0...0>) -> X^n -> H^n`. This implements reflection about the uniform
superposition `|s>`, i.e. `2|s><s| - I` (up to an unobservable global
phase — the actual matrix this circuit produces is `I - 2|s><s|`; both
implement the same physical reflection, verified via `Operator.equiv` rather
than exact matrix equality). The `X`-sandwiched multi-controlled-Z is the
same "remap the target state to all-ones, flip it, remap back" trick as the
oracle, just with the fixed target `|0...0>` reached directly by the `H`
gates rather than needing per-target `X` gates.

## Full circuit

`build_grover_circuit(n_qubits, oracle, iterations)`:

1. `H` on every qubit — uniform superposition `|s>`.
2. `iterations` rounds of `(oracle.phase_flip_gate(), diffusion_operator(n_qubits))`.
3. Measure every qubit.

`iterations` comes from `implementation._iteration_count` (math.md). Qubit
count is exactly `n_qubits` (no ancillas, unlike Shor's oracle/QPE
machinery); gate count per iteration is `O(n_qubits)` for the oracle (one
multi-controlled-Z per marked item, each needing `O(n_qubits)` elementary
gates once Qiskit's transpiler decomposes it) plus a fixed `O(n_qubits)` for
the diffusion operator — overall `O(n_qubits * (iterations + |marked|))`
gates, dramatically smaller than Shor's circuits at comparable qubit counts.

## Quantum counting (`counting.py`)

`_grover_iteration_gate` wraps one `(oracle.phase_flip_gate(),
diffusion_operator)` pair as a single gate `Q` — the same construction
`build_grover_circuit`'s loop body applies, reused rather than
re-derived. `controlled_grover_iteration_power_gate` builds controlled
`Q^power` by literally repeating `Q` `power` times before adding one
control (`Q` has no closed-form exponentiation the way
`algorithms.hhl.oracles.DiagonalXOracle` does) — verified via `Operator`
against `numpy.linalg.matrix_power` of `Q`'s own matrix, for several
`power` values including the larger powers `build_counting_circuit`
actually needs (up to `2**(n_count-1)`), since this is exactly the kind
of deeply-nested, heavily-repeated composite-gate construction that
caused a real `.control()` bug during RFC-0002's development — verifying
this generalizes to larger powers, not just power `1`, mattered.

`build_counting_circuit(n_qubits, oracle, n_count)`: `H^n_count` on the
counting register, `H^n_qubits` on the search register (the same `|s>`
`build_grover_circuit` starts from), controlled `Q^(2**k)` per counting
qubit `k`, `arithmetic.qft.inverse_qft` on the counting register (a fifth
consumer), measure the counting register. `count` reads off the measured
integer `y` and converts it to `M` via `theta = pi * abs(y/2**n_count -
0.5)` then `M = round(N * sin(theta)**2)` — see math.md's "Quantum
counting" for why the `abs(... - 0.5)` term is there (a phase offset from
`diffusion_operator`'s extra global phase, harmless in `search` but
exposed here since `Q` is used under control).

## Known simplifications (v0.2)

- `ZGate().control(n_qubits - 1)` is an exact multi-controlled-Z, not
  synthesized from an arbitrary boolean predicate/circuit — marking an
  explicit bitstring set is general (any `N`, any marked subset) but is a
  different problem from "compile an oracle from a boolean function," which
  RFC-0004's non-goals defer (mirrors
  [algorithms/shor/paper.md](../shor/paper.md)'s framing of
  `PermutationMatrixOracle` vs. a gate-decomposed follow-up).
- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.
- Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0004](../../docs/rfcs/0004-grovers-algorithm.md)'s "Explicit
Non-goals" for the full list of what v0.2 deliberately defers.

## References

See [references.bib](references.bib) for full citations: Grover's original
paper (`grover1996`) for the algorithm this circuit implements; Nielsen &
Chuang (`nielsenchuang2010`) for the standard circuit-derivation treatment;
Brassard-Høyer-Mosca (`brassard2000`) for the amplitude-amplification
generalization this oracle/diffusion-operator pair is a special case of.
