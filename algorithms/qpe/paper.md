# Quantum Phase Estimation — Circuit Derivation

Level 2 of the repository's documentation-level model.
Builds on [math.md](math.md) (Math Version 1.0).

## The oracle gate: `PhaseGateOracle`

`controlled_power_gate(power)` returns a controlled `P(2*pi*theta*power)`
gate: since a single-qubit phase gate `P(phi) = diag(1, e^(i*phi))` satisfies
`P(phi)^power = P(phi*power)` (phases add under exponentiation of a diagonal
unitary), `U^power = P(2*pi*theta*power)` directly — no repeated squaring or
matrix exponentiation needed, just scaling the angle. `|1>` is exactly its
eigenstate, since `P(phi)|1> = e^(i*phi)|1>`. Verified against the exact
4x4 controlled-unitary matrix (`Operator`) for several `theta`/`power`
combinations in `tests/test_qpe.py`.

## `build_qpe_circuit`

1. `H` on every counting qubit (uniform superposition).
2. `eigenstate_prep` on the eigenstate register (e.g. `X` to prepare `|1>`
   for `PhaseGateOracle`).
3. For counting qubit `k = 0, ..., n_count - 1`: apply
   `oracle.controlled_power_gate(2**k)`, controlled on qubit `k`.
4. `arithmetic.qft.inverse_qft` on the counting register — reused directly
   from [arithmetic/qft.py](../../arithmetic/qft.py), the same construction
   `algorithms/shor/circuit.py` uses (a second, independent consumer,
   exactly what that module's relocation during RFC-0002 anticipated).
5. Measure the counting register.

This is qubit-for-qubit and step-for-step the same shape as
`algorithms/shor/circuit.py::build_order_finding_circuit` — compare the two
directly. Verified empirically: for `theta` values with an exact `n_count`-bit
binary expansion (e.g. `0.25`, `0.375`, `0.5`, `0.125`), `estimate_phase`
recovers the exact value; for `theta = 0.1` (no exact finite binary
expansion) at `n_count=8`, the estimate is off by less than `1/2^8`, matching
math.md's precision bound.

## `semiclassical.py`

`_round_circuit` builds one round: `eigenstate_prep` on a fresh eigen
register (equivalent to letting it persist across rounds, since only the
ancilla is ever measured), `H` on a single ancilla, controlled
`oracle.controlled_power_gate(power)`, a classical-feedback `P(
feedback_angle)`, `H` again, then measure the ancilla.
`estimate_phase_semiclassical` runs `n_count` such rounds in sequence,
computing each round's `power` and `feedback_angle` from the bits
measured so far (see math.md's derivation), and majority-votes each
round's bit over `shots` repetitions before moving on. Verified against
`implementation.estimate_phase` directly: both recover the exact same
`theta` for every one of `tests/test_qpe.py`'s exact instances, and
approximate the same non-terminating `theta=0.1` similarly — the two
circuit shapes (one big coherent circuit vs. many small circuits plus
classical bookkeeping between `Executor.run` calls) agree.

## Known simplifications

- No refactor connecting this module's circuit-building code to
  `algorithms/shor/circuit.py`'s — the shared shape is documented, not
  extracted into common implementation (RFC-0007's explicit architecture
  decision, to avoid refactor risk to already-tested Shor code for a
  primarily pedagogical win).
- `estimate_phase` takes the single most-frequent measured bitstring across
  `shots` runs — no confidence-boosting via extra counting qubits or
  repeated-median estimation (see math.md's precision discussion).
- Simulator-oriented: validated against `AerSimulator` only.
- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.

See [RFC-0007](../../docs/rfcs/0007-quantum-phase-estimation.md)'s
"Explicit Non-goals" for the full list of what is deliberately deferred.

## References

See [references.bib](references.bib): Kitaev's original paper
(`kitaev1995`) for the algorithm; Nielsen & Chuang (`nielsenchuang2010`),
Section 5.2, for the standard circuit-derivation treatment this follows.
