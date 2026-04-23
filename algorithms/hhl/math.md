# HHL — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

## The linear systems problem

Given Hermitian `A` and a normalized state `|b>`, find (a state proportional
to) `|x>` for `x = A^-1 b`. Expand `|b>` in `A`'s eigenbasis, `|b> = sum_i
beta_i |u_i>` for eigenpairs `(lambda_i, |u_i>)`; then `A^-1|b> = sum_i
(beta_i / lambda_i) |u_i>` — HHL's job is to apply the `1/lambda_i` factor
to each eigencomponent without ever learning the eigendecomposition
classically.

## Using QPE to estimate eigenvalues

[algorithms/qpe/](../qpe/) estimates the phase `theta` of an eigenvalue
`e^(2*pi*i*theta)` for a *known* eigenstate. HHL runs the same QPE
subroutine on `|b>` directly (not a known eigenstate) — since `|b>` is a
superposition of `A`'s eigenvectors, QPE entangles the clock register with
*each* eigencomponent's estimated eigenvalue simultaneously: the joint
state becomes `sum_i beta_i |u_i> |lambda_i-estimate>`. This is exactly
what makes the algorithm work without ever collapsing `|b>` into a single
eigenvector first.

## The conditional rotation

For each clock-register branch `k` (interpreted as an eigenvalue estimate
`lambda_k`), a multiplexed `RY(2*arcsin(C/lambda_k))` rotation on a fresh
ancilla qubit encodes the desired `1/lambda_k` factor into the ancilla's
`|1>` amplitude: `RY(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>`, so
`sin(theta_k/2) = C/lambda_k` after the `2*arcsin(...)` angle choice. `C`
must be chosen no larger than the smallest reachable `|lambda_k|` so every
branch's rotation angle stays in `arcsin`'s domain; `k=0` (the null
eigenvalue) is left as the identity, since `1/0` is undefined.

## Uncomputing the clock register

The multiplexed rotation only touches the ancilla — it never modifies the
clock register — so QPE's *exact* inverse (run backwards: inverse QFT's
inverse, each controlled power gate inverted in reverse order, then `H`
again) disentangles the clock register back to `|0...0>`, leaving:

`sum_i (beta_i / lambda_i-estimate) |u_i> (x) [sqrt(1-(C/lambda_i)^2)|0> + (C/lambda_i)|1>]_ancilla`

(dropping the now-separable `|0...0>` clock register). Measuring the
ancilla as `1` projects the b-register onto (a normalization of)
`sum_i (beta_i/lambda_i) |u_i>` — exactly `A^-1|b>`, up to normalization.

## Why success is postselected, not guaranteed

Measuring the ancilla as `0` discards the shot entirely — the b-register
in that branch is *not* proportional to the solution. This is a
fundamentally different success/failure shape from every prior RFC: a
bounded retry loop for Shor/Grover (the retry itself succeeds with
overwhelming probability), a classical optimization loop searching for a
best answer for QAOA/VQE. Here, a single fixed circuit runs once, and
whether that *particular shot* is usable is only known after measuring
the ancilla — the "success probability" is the fraction of shots where it
does.

## The demo instance

`A = a*I + b*X` (`oracles.DiagonalXOracle`), with `t` and `n_clock` chosen
so both eigenvalues (`a+b`, `a-b`) land on exact `n_clock`-bit binary
fractions of `2*pi/t` — mirrors [algorithms/qpe/math.md](../qpe/math.md)'s
`PhaseGateOracle` choice, making the clock-register uncomputation and the
final answer both *exact* (verified directly against the statevector in
`tests/test_hhl.py`, with no shot noise), rather than only approximately
correct as QPE generally is for an arbitrary eigenvalue.

## Known limitations (v0.2)

No condition-number analysis or success-probability bound beyond citing
Harrow-Hassidim-Lloyd's original result (see paper.md's "Known
simplifications"); no amplitude amplification to boost the postselection
success probability; only a 2x2 system (`A = a*I + b*X`) is implemented.

## References

See [references.bib](references.bib). The algorithm follows
Harrow-Hassidim-Lloyd's original paper (`harrow2009`); the Hamiltonian/
eigenbasis formalism follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
