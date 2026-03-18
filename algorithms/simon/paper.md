# Simon's Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The oracle gate: `|x>|y> -> |x>|y XOR f(x)>` acting on `2*n_qubits`
  qubits (`n_qubits` input + `n_qubits` output) — construction for
  `LinearOracle` (CNOTs per set bit of the matrix `M`) and `PermutationOracle`
  (explicit per-pair lookup, mirroring
  [algorithms/deutsch_jozsa/oracles.py](../deutsch_jozsa/oracles.py)'s
  `BalancedOracle` construction pattern extended to a full output register).
- `build_simon_circuit`: `H^n` on the input register, apply the oracle
  gate, `H^n` on the input register again, measure the input register only.
- The classical post-processing loop in `implementation.py`: collecting
  independent equations, GF(2) Gaussian elimination, and the classical
  one-to-one-vs-two-to-one check.
- Qubit and gate count as a function of `n_qubits` for each oracle type —
  `LinearOracle` is `O(n^2)`, `PermutationOracle` is `O(2^n)`.
- Known simplifications: `PermutationOracle`'s exponential construction is
  exact but not scalable, mirroring
  [algorithms/shor/paper.md](../shor/paper.md)'s framing of
  `PermutationMatrixOracle`.
