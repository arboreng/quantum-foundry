# VQE — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

## `ansatz_circuit`

`reps` layers of per-qubit `RY(theta)` plus a ladder of entangling `CX`
gates (`CX(0,1), CX(1,2), ..., CX(n-2,n-1)`), then one final `RY` layer —
`n_qubits * (reps + 1)` parameters total, consumed in order: each layer's
`n_qubits` angles, then the final layer's `n_qubits` angles. Verified
against the exact tensor product of single-qubit `RY` rotation matrices
for `reps=0` (no entangling layer), and against an explicit,
independently-written gate sequence for `reps=1` (`tests/test_vqe.py`).
Rejects a `params` list of the wrong length rather than silently
truncating or padding.

## `measurement_circuit`

`ansatz_circuit` followed by the basis-rotation gates for a given
`PauliTerm` (`H` for `X`, `Sdg` then `H` for `Y`, nothing for `Z`/`I`),
then a measurement of every qubit. Verified against an explicit basis
rotation built by hand, via `Operator` equivalence on the
measurement-free unitary portion of the circuit (`remove_final_measurements`).

## The classical loop in `implementation.py`

`expectation_value` runs one measurement circuit per non-identity Pauli
term, combines each shot's `+-1` parity (the product of `(-1)^bit` over
the term's non-`I` qubits, read via this repo's usual bit-index
convention — qubit `q` maps to bitstring position `n_qubits - 1 - q`)
weighted by counts, and sums `coefficient * <term>` over all terms (a
pure-identity term contributes its coefficient with zero circuit
executions — verified directly in `tests/test_vqe.py` with an `Executor`
stub that raises if ever called). This is `solve_ground_state`'s
objective, which `scipy.optimize.minimize` (COBYLA, matching RFC-0008)
minimizes over the ansatz `params`; a final, higher-shot-count
`expectation_value` call re-estimates the energy at the optimized
parameters.

## Qubit and gate count

`n_qubits` qubits total. The ansatz costs `n_qubits * (reps + 1)` `RY`
gates plus `(n_qubits - 1) * reps` `CX` gates. Each `expectation_value`
call costs one full circuit execution *per non-identity Hamiltonian
term* — for `TransverseFieldIsingHamiltonian`, `2*n_qubits - 1` terms
(`n_qubits - 1` `ZZ` terms, `n_qubits` `X` terms), all non-identity, so
`2*n_qubits - 1` circuit executions per optimizer iteration.

## Known simplifications

-   No convergence-rate analysis — only the variational principle's basic
    guarantee (see math.md).
-   No measurement grouping: qubit-wise-commuting Pauli terms aren't
    batched into shared circuit executions, even though several terms
    here (e.g. all the `X_i` terms) commute and could in principle share
    a measurement basis.
-   No gradient-based optimization (e.g. the parameter-shift rule) —
    `scipy.optimize.minimize`'s COBYLA only, matching RFC-0008.
-   A fixed hardware-efficient ansatz (`RY` + `CX` ladder) — no
    chemistry-motivated ansatz like UCCSD.
-   Fixed initial parameter guess (`0.5` for every angle) — no
    multi-start or problem-informed initialization.
-   Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0009](../../docs/rfcs/0009-vqe.md)'s "Explicit Non-goals" for the
full list of what v0.2 deliberately defers.

## References

See [references.bib](references.bib): Peruzzo et al.'s original paper
(`peruzzo2014`) for the algorithm; McClean et al. (`mcclean2016`) for the
hybrid classical-quantum framing; Nielsen & Chuang (`nielsenchuang2010`)
for the standard Pauli/Hamiltonian treatment this follows.
