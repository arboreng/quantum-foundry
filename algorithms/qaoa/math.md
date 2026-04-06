# QAOA — Mathematical Foundations

**Math Version 1.0.**

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

## MaxCut

Given a graph with vertex set `{0, ..., n-1}` and edge set `E`, partition
the vertices into two sets maximizing the number of edges with one endpoint
in each set (a "cut" edge). NP-hard in general (no known polynomial-time
exact algorithm, and unlikely to have one). QAOA targets *approximate*
solutions, trading circuit depth (`p`, the number of cost/mixer layers)
against solution quality.

## Cost and mixer Hamiltonians

Encode each candidate partition as a computational basis state `|z>` (bit
`z_i = 0` or `1` assigns vertex `i` to one side or the other). The cost
Hamiltonian

`C = sum_{(i,j) in E} (1 - Z_i*Z_j)/2`

is diagonal, and `C|z> = (number of cut edges for z)|z>` — each term
contributes `1` exactly when `z_i != z_j` (a cut edge, since `Z_i*Z_j` then
has eigenvalue `-1`) and `0` when `z_i = z_j`. The mixer Hamiltonian
`B = sum_i X_i` doesn't commute with `C` and is used to drive the state
between computational basis states.

## Why alternating them approximates the optimum

Starting from the uniform superposition (the ground state of `-B`), QAOA
applies `p` layers of `exp(-i*gamma_l*C)` (`problem.cost_gate`) followed by
`exp(-i*beta_l*B)` (`circuit.mixer_gate`), with the `2p` angles
`(gammas, betas)` chosen to maximize the final state's expected cost. As
`p -> infinity` with appropriately chosen angles, this reproduces the
adiabatic path from `-B`'s ground state to `C`'s ground state (the Farhi et
al. argument, itself a Trotterized adiabatic evolution) — so, in principle,
arbitrarily good solutions are reachable with enough layers and well-chosen
angles. In practice, `p` is kept small (this implementation defaults to
`p=1`) and the angles are found by a classical optimization loop rather
than derived in closed form.

## A different guarantee shape

Every prior RFC in this repo (Shor through QPE) runs a **fixed** circuit —
possibly with a bounded retry loop for an inherently probabilistic
algorithm — and returns an answer with a provable success probability (or,
for Deutsch-Jozsa/Bernstein-Vazirani/QPE with an exact phase, a *certain*
one). QAOA has no such guarantee: there is no fixed `p`, no fixed
`(gammas, betas)`, and no shot count that guarantees finding the true
optimal cut. `implementation.solve_maxcut`'s classical optimization loop
(`scipy.optimize.minimize`, tuning `(gammas, betas)` against the sampled
expectation value) searches for good parameters, but "good" is empirical,
not proven — the returned cut is the best one *found*, which for the small
test graphs in `tests/test_qaoa.py` happens to be optimal, but that isn't
guaranteed for larger or harder instances.

## Known limitations (v0.2)

No approximation-ratio bound is derived or checked (see paper.md's "Known
simplifications"); `p` and the initial parameter guess are fixed, not
tuned per problem instance; only MaxCut is implemented (`Problem` could
generalize to other QUBO/Ising-encodable problems — a future RFC, per
RFC-0008's non-goals).

## References

See [references.bib](references.bib). The algorithm follows Farhi,
Goldstone, and Gutmann's original paper (`farhi2014`); the Hamiltonian
formalism follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
