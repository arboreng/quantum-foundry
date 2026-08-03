# VQE — Mathematical Foundations

Level 1 of the repository's documentation-level model.

## The variational principle

For any Hermitian operator `H` and any normalized state `|psi>`,
`<psi|H|psi> >= E_0`, the true ground-state energy, with equality iff
`|psi>` is a ground state. VQE searches over a parameterized family
`|psi(theta)>` (the ansatz, `circuit.ansatz_circuit`) for the `theta`
minimizing `<psi(theta)|H|psi(theta)>`, giving an upper bound on `E_0`
that improves as the ansatz and classical optimizer improve — the same
"best found, not proven optimal" guarantee shape as
[algorithms/qaoa/math.md](../qaoa/math.md)'s MaxCut search.

## Pauli-string decomposition

Any Hermitian `H` on `n` qubits can be written as a real-weighted sum of
tensor products of `{I, X, Y, Z}` (the Pauli basis spans all `2^n x 2^n`
Hermitian matrices) — `hamiltonians.PauliTerm(coefficient, paulis)`, one
per term. `<psi|H|psi>` is then the same weighted sum of per-term
expectation values `<psi|P_0 (x) ... (x) P_{n-1}|psi>`.

## Measuring a Pauli term

`Z` measures directly in the computational basis: `+1` for a measured
`0`, `-1` for a measured `1`. `X` and `Y` require rotating into the `Z`
basis first (`H` for `X`; `Sdg` then `H` for `Y`, since `Y = S H Z H
Sdg`... equivalently, `H Sdg` diagonalizes `Y` into `Z`) before reading
`+-1` off each qubit. A multi-qubit term's value for one shot is the
*product* of `+-1` over its non-`I` qubits (not the sum) — `<term>` is
then the counts-weighted average of that per-shot product across all
shots. `circuit.measurement_circuit` builds exactly this: the ansatz,
then the term's basis-rotation gates, then a measurement of every qubit;
`implementation.expectation_value` does the counts-weighted parity
combination.

## The transverse-field Ising model

`hamiltonians.TransverseFieldIsingHamiltonian`: `H = -J * sum_i Z_i
Z_{i+1} - h * sum_i X_i` on an open 1D chain. Chosen as this RFC's
demonstration Hamiltonian because it's small, exactly diagonalizable
classically for validation (see `benchmark.py`'s
`_exact_ground_state_energy`), and requires no quantum-chemistry mapping
from a molecular Hamiltonian (see Non-goals).

## The hardware-efficient ansatz

`circuit.ansatz_circuit`: `reps` layers of per-qubit `RY(theta)` plus a
ladder of entangling `CX` gates, then one final `RY` layer. This is
"hardware-efficient" in the VQE literature's sense — built from gates
that are cheap on real hardware, rather than derived from the
Hamiltonian's physics (contrast: a chemistry-motivated ansatz like UCCSD,
out of scope here — see Non-goals). Entanglement (via `CX`) is necessary
because the Ising model's ground state is generally entangled for `J, h
!= 0`; a product-state ansatz (`reps=0`, no `CX` at all) can't reach it.

## Contrast with QAOA

[algorithms/qaoa/math.md](../qaoa/math.md)'s cost Hamiltonian is diagonal
in the computational basis, so its expectation value is read directly off
measured bitstrings with no basis change — one circuit execution total
per parameter setting. VQE's Hamiltonian is general (here, including the
non-diagonal `X` terms), so `expectation_value` runs one circuit
execution *per non-identity Pauli term* per parameter setting, each
requiring its own basis rotation before measurement.

## Measurement grouping

Two Pauli terms *qubit-wise commute* if, at every qubit, their single-
qubit operators are equal or at least one is `I` — exactly the condition
under which both can be read off the *same* measurement (after a shared
basis rotation), rather than needing separate circuit executions.
`hamiltonians.group_qwc_terms` greedily partitions a Hamiltonian's terms
into such groups; `circuit.group_measurement_circuit` builds one shared
measurement circuit per group (rotating each qubit into whichever
non-identity Pauli the group uses there, if any); `implementation.
expectation_value_grouped` computes every term's expectation value from
its group's shared counts. For `TransverseFieldIsingHamiltonian`, this
collapses `2*n_qubits - 1` circuit executions (one per term) down to
exactly **2** (all `ZZ` terms mutually qubit-wise commute, and likewise
all `X` terms — but a `ZZ` term and an `X` term never do, since they
disagree at their shared qubit), regardless of `n_qubits` — verified
directly in `tests/test_vqe.py`, both that the grouping is correct and
that it produces the same expectation value (up to shot noise) with
fewer circuit executions.

## The Heisenberg model

`hamiltonians.HeisenbergHamiltonian`: the isotropic Heisenberg (XXX)
model, `H = J * sum_i (X_i X_{i+1} + Y_i Y_{i+1} + Z_i Z_{i+1})` on an
open 1D chain — a second demonstration Hamiltonian alongside the
transverse-field Ising model, chosen specifically because its `YY` terms
are the *first* Hamiltonian in this repo to genuinely exercise
`measurement_circuit`'s `Y`-basis rotation (`Sdg` then `H`) — TFIM has no
`Y` terms at all, so that code path was previously validated only via
the abstract `PauliTerm(1.0, "XY")` unit test, never through an actual
physical Hamiltonian.

Grouping behaves differently here too: TFIM's terms split into 2
qubit-wise-commuting groups (all `Z`, all `X`), but Heisenberg's adjacent
terms sharing a qubit (e.g. `X_0 X_1` and `X_1 X_2` share qubit 1) only
ever agree there *within the same Pauli type* — `X_0 X_1` and `Y_1 Y_2`
disagree at qubit 1 (`X` vs `Y`), so grouping splits strictly by type:
all `X` pairs, all `Y` pairs, all `Z` pairs, giving exactly **3** groups
regardless of `n_qubits` (verified in `tests/test_vqe.py`).

**A genuine finding, not a bug**: the open 3-qubit Heisenberg chain's
ground energy (`-4.0` for `J=1`) is *doubly degenerate* (confirmed via
`numpy.linalg.eigvalsh`) — a harder variational landscape than TFIM's
non-degenerate ground states. `solve_ground_state_grouped` needed more
ansatz depth (`reps=3`, not the default `1`) and more retries to reach
within the same tolerance TFIM reaches easily at `reps=1`; even at
`reps=3`, COBYLA lands within tolerance on roughly 7 of 8 attempts, not
essentially every attempt. This is an honest property of variational
optimization over a degenerate ground-state manifold, not a
construction bug — see `tests/test_vqe.py`'s dedicated `n=3` test for
the measured pass rate this claim is based on.

## Known limitations

No convergence-rate analysis — only the variational principle's basic
guarantee (`<psi|H|psi> >= E_0`) is invoked, not a bound on how close
COBYLA gets in practice (see paper.md's "Known simplifications"); only
the transverse-field Ising and Heisenberg models are implemented (a
future RFC could generalize `Hamiltonian` further, per RFC-0009's
non-goals); `group_qwc_terms`' greedy grouping isn't optimal (minimizing
the number of groups is itself an NP-hard graph-coloring problem), though
it is exact for both Hamiltonians' structures.

## References

See [references.bib](references.bib). The algorithm follows Peruzzo et
al.'s original paper (`peruzzo2014`); the hybrid classical-quantum
framing follows McClean et al. (`mcclean2016`); the Hamiltonian/Pauli
formalism follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
