# VQE — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

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

## Known limitations (v0.2)

No convergence-rate analysis — only the variational principle's basic
guarantee (`<psi|H|psi> >= E_0`) is invoked, not a bound on how close
COBYLA gets in practice (see paper.md's "Known simplifications"); no
measurement grouping (qubit-wise-commuting terms could in principle share
a measurement basis and circuit execution, but don't here); only the
transverse-field Ising model is implemented (a future RFC could
generalize `Hamiltonian` further, per RFC-0009's non-goals).

## References

See [references.bib](references.bib). The algorithm follows Peruzzo et
al.'s original paper (`peruzzo2014`); the hybrid classical-quantum
framing follows McClean et al. (`mcclean2016`); the Hamiltonian/Pauli
formalism follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
