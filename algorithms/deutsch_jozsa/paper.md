# Deutsch-Jozsa Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The oracle gate: `|x>|y> -> |x>|y XOR f(x)>` acting on `n+1` qubits (`n`
  input + 1 ancilla) — construction for `ConstantOracle`, `ParityOracle`,
  and `BalancedOracle`.
- `build_oracle_query_circuit`: ancilla prepared in `|1>` then `H` (giving
  `|->`), `H` on the input register, apply the oracle gate, `H` on the input
  register again, measure the input register. Shared verbatim with
  `algorithms/bernstein_vazirani/circuit.py`.
- Qubit and gate count as a function of `n_qubits` for each oracle type —
  `ParityOracle` is `O(n)`, `BalancedOracle` is `O(2^n)` (see math.md and
  RFC-0005's non-goals).
- Known simplifications: `BalancedOracle`'s exponential construction is
  exact but not scalable, mirroring
  [algorithms/shor/paper.md](../shor/paper.md)'s framing of
  `PermutationMatrixOracle`.
