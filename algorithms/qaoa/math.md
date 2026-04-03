# QAOA — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- MaxCut as a combinatorial optimization problem: partition a graph's `n`
  vertices into two sets maximizing the number of edges crossing between
  them. NP-hard in general; QAOA targets *approximate* solutions.
- Encoding as a cost Hamiltonian: `C = sum_{(i,j) in edges} (1 - Z_i Z_j)/2`
  — diagonal in the computational basis, with `C|z>` equal to the number of
  cut edges for cut `z`.
- The mixer Hamiltonian `B = sum_i X_i` and why alternating
  `exp(-i*gamma*C)` and `exp(-i*beta*B)` for `p` layers approximates the
  adiabatic path from the mixer's ground state (uniform superposition) to
  the cost Hamiltonian's ground state (the optimal cut) as `p -> infinity`
  (Farhi et al.'s adiabatic-theorem argument).
- Why this is a fundamentally different guarantee shape from every prior
  RFC: there's no fixed circuit depth or shot count that guarantees finding
  the optimal cut — `p` and the `(gammas, betas)` parameters trade off
  approximation quality against circuit depth, tuned by a classical
  optimization loop rather than derived in closed form.
- Known limitation: no approximation-ratio guarantee is derived or checked
  here — see paper.md's "Known simplifications."
