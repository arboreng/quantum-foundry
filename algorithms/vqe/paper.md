# VQE — Circuit Derivation

Level 2 of the repository's documentation-level model.
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

## `group_qwc_terms` and `group_measurement_circuit`

`hamiltonians.group_qwc_terms` greedily partitions a Hamiltonian's terms:
a term joins the first existing group where it qubit-wise commutes with
*every* term already there, else it starts a new group. `circuit.
group_measurement_circuit` builds one shared measurement circuit for a
group — for each qubit, it scans the group for the (unique, by
qubit-wise-commutativity) non-identity Pauli acting there, if any, and
applies that Pauli's basis rotation — rather than `measurement_circuit`'s
one-rotation-set-per-term. `implementation.expectation_value_grouped`
runs one circuit per group instead of one per term, computing each
group's terms' expectation values from that group's shared counts.
Verified against `measurement_circuit`/`expectation_value` two ways in
`tests/test_vqe.py`: the grouped and ungrouped expectation values agree
(same physics), and an instrumented `Executor` confirms the grouped path
actually issues fewer circuit executions (not just returns a similar
number).

## Qubit and gate count

`n_qubits` qubits total. The ansatz costs `n_qubits * (reps + 1)` `RY`
gates plus `(n_qubits - 1) * reps` `CX` gates. `expectation_value` costs
one full circuit execution *per non-identity Hamiltonian term* — for
`TransverseFieldIsingHamiltonian`, `2*n_qubits - 1` terms (`n_qubits - 1`
`ZZ` terms, `n_qubits` `X` terms), all non-identity, so `2*n_qubits - 1`
circuit executions per optimizer iteration. `expectation_value_grouped`
costs exactly **2** circuit executions instead, regardless of `n_qubits`
(one for the `ZZ` group, one for the `X` group) — see math.md's
"Measurement grouping".

## `HeisenbergHamiltonian`

Three `PauliTerm`s per adjacent qubit pair (`XX`, `YY`, `ZZ`, all
coefficient `J`) instead of TFIM's `ZZ` + `X`. Its `YY` terms are the
first real exercise of `measurement_circuit`'s `Y`-basis rotation
(`Sdg` then `H`) through an actual Hamiltonian, not just an isolated
`PauliTerm` test. `group_qwc_terms` splits its terms into 3 groups (all
`X` pairs, all `Y` pairs, all `Z` pairs) rather than TFIM's 2, since
adjacent pairs sharing a qubit only agree there within the same Pauli
type. Solving it end to end needed more ansatz depth (`reps=3`) than TFIM
required (`reps=1`) to reliably approach the exact ground energy — traced
to the 3-qubit open chain's ground energy being doubly degenerate, a
harder variational landscape (see math.md).

## Known simplifications

-   No convergence-rate analysis — only the variational principle's basic
    guarantee (see math.md).
-   `group_qwc_terms`' greedy grouping isn't optimal (minimizing group
    count is itself NP-hard graph coloring) — exact for this
    Hamiltonian's structure, but not guaranteed minimal in general.
-   No gradient-based optimization (e.g. the parameter-shift rule) —
    `scipy.optimize.minimize`'s COBYLA only, matching RFC-0008.
-   A fixed hardware-efficient ansatz (`RY` + `CX` ladder) — no
    chemistry-motivated ansatz like UCCSD.
-   Fixed initial parameter guess (`0.5` for every angle) — no
    multi-start or problem-informed initialization.
-   Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0009](../../docs/rfcs/0009-vqe.md)'s "Explicit Non-goals" for the
full list of what is deliberately deferred.

## References

See [references.bib](references.bib): Peruzzo et al.'s original paper
(`peruzzo2014`) for the algorithm; McClean et al. (`mcclean2016`) for the
hybrid classical-quantum framing; Nielsen & Chuang (`nielsenchuang2010`)
for the standard Pauli/Hamiltonian treatment this follows.
