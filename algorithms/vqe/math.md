# VQE — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The variational principle: for any Hermitian `H` and any normalized
  `|psi>`, `<psi|H|psi> >= E_0` (the true ground-state energy), with
  equality iff `|psi>` is a ground state. VQE searches over a
  parameterized family `|psi(theta)>` (the ansatz) for the `theta`
  minimizing `<psi(theta)|H|psi(theta)>`, giving an upper bound on `E_0`
  that improves as the ansatz/optimizer improve.
- Pauli-string decomposition: any Hermitian `H` on `n` qubits can be
  written as a real-weighted sum of tensor products of `{I, X, Y, Z}`
  (the Pauli basis spans all `2^n x 2^n` Hermitian matrices). `<psi|H|psi>`
  is then the same weighted sum of per-term expectation values
  `<psi|P_0 (x) ... (x) P_{n-1}|psi>`.
- Measuring a Pauli term: `Z` measures directly in the computational
  basis; `X`/`Y` require rotating into the `Z` basis first (`H` for `X`,
  `Sdg` then `H` for `Y`) before reading `+-1` off each qubit and taking
  the product over the term's non-`I` qubits.
- The transverse-field Ising model `H = -J * sum_i Z_i Z_{i+1} - h *
  sum_i X_i` as the demonstration Hamiltonian: small, exactly
  diagonalizable classically for validation, and requires no
  quantum-chemistry mapping.
- The hardware-efficient ansatz (`RY` layers + `CX` ladder) and why it's
  used here instead of a chemistry-motivated ansatz like UCCSD (this RFC
  targets spin Hamiltonians, not molecular ones — see Non-goals).
- Contrast with [algorithms/qaoa/math.md](../qaoa/math.md): QAOA's cost
  Hamiltonian is diagonal, so its expectation value is read directly off
  measured bitstrings; VQE's general Hamiltonian requires the basis-
  rotation step above.
- Known limitation: no convergence-rate analysis — only the variational
  principle's basic guarantee, not a bound on how close COBYLA gets in
  practice.
