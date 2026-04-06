# QAOA — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md) (Math Version 1.0).

## The cost gate: `MaxCutProblem.cost_gate`

`exp(-i*gamma*C)` for `C = sum_{(i,j)} (1 - Z_i*Z_j)/2` factors into one
two-qubit gate per edge (all terms commute, being sums of commuting
`Z_i*Z_j` operators). Dropping the per-edge unobservable global phase
`exp(-i*gamma/2)` from the `(1 - Z_i*Z_j)/2` term leaves
`exp(i*(gamma/2)*Z_i*Z_j)` per edge, built from elementary gates rather
than Qiskit's built-in `rzz` convenience method (matching this repo's
"from scratch" ethos): `CX(i,j)` -> `RZ(-gamma)` on `j` -> `CX(i,j)` — the
standard identity `CX; RZ(theta); CX = exp(-i*theta/2*Z_i*Z_j)` with
`theta = -gamma` gives exactly `exp(i*(gamma/2)*Z_i*Z_j)`. Verified against
the exact diagonal unitary `exp(-i*gamma*C)` via `Operator` equivalence
(global phase ignored) for several graphs/angles in `tests/test_qaoa.py`.

## The mixer gate: `circuit.mixer_gate`

`exp(-i*beta*B)` for `B = sum_i X_i` factors into one `RX(2*beta)` per
qubit (`RX(theta) = exp(-i*theta/2*X)`, so `RX(2*beta) = exp(-i*beta*X)`).
Verified against the exact tensor product of single-qubit rotation
matrices.

## `build_qaoa_circuit`

`H` on every qubit (uniform superposition over all `2^n` candidate cuts),
then `p = len(gammas)` layers of (`problem.cost_gate(gammas[l])`,
`mixer_gate(n_qubits, betas[l])`), then measure every qubit. Verified
empirically: even with arbitrary (non-optimized) angles, measurement
already favors higher-cost cuts over the trivial all-same partitions (see
development notes) — the optimization loop's job is to find angles that
sharpen this bias further.

## The classical optimization loop

`implementation.expectation_value` runs the circuit and returns the
shots-weighted average of `problem.cost_value` over measured outcomes —
this is `implementation.solve_maxcut`'s objective (negated, since
`scipy.optimize.minimize` minimizes). `COBYLA` was chosen because it's
gradient-free: `expectation_value` is a noisy, finite-shots Monte Carlo
estimate, so a gradient-based method would need to estimate gradients via
finite differences anyway (adding more circuit evaluations for no clear
benefit at this problem scale). After optimization, a final higher-shot-count
run reads off the single most-frequent measured bitstring as the answer.

## Qubit and gate count

`n_qubits` qubits total. Each layer costs `3 * |edges|` elementary gates
for the cost gate (`CX`-`RZ`-`CX` per edge) plus `n_qubits` `RX` gates for
the mixer — `O(p * (|edges| + n_qubits))` overall, small even for
several layers on graphs with tens of vertices.

## Known simplifications

- No approximation-ratio guarantee derived or checked (see math.md).
- Fixed classical optimizer (`scipy.optimize.minimize`'s COBYLA) — no
  comparison across optimizers.
- Fixed initial parameter guess (`0.5` for every angle) — no
  multi-start or problem-informed initialization.
- Only `MaxCutProblem` — no other QUBO/Ising-encodable problems.
- Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0008](../../docs/rfcs/0008-qaoa.md)'s "Explicit Non-goals" for the
full list of what v0.2 deliberately defers.

## References

See [references.bib](references.bib): Farhi, Goldstone, and Gutmann's
original paper (`farhi2014`) for the algorithm; Nielsen & Chuang
(`nielsenchuang2010`) for the standard Hamiltonian-simulation treatment
this follows.
