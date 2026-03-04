# Bernstein-Vazirani Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The oracle gate: `|x>|y> -> |x>|y XOR (s.x mod 2)>`, implemented as one
  `CX` per set bit of `s` (input qubit `i` to the ancilla, for each `i`
  where `s_i = 1`) — `O(n)` gates for any `s`, no multi-controlled gates
  needed at all (contrast with
  [algorithms/deutsch_jozsa/oracles.py](../deutsch_jozsa/oracles.py)'s
  `BalancedOracle`, which needs `O(2^n)`).
- The circuit is exactly `algorithms/deutsch_jozsa/circuit.py`'s
  `build_oracle_query_circuit` — no changes, just a different `Oracle`.
- Why the measured bitstring *is* `s` (not just correlated with it) —
  derive from math.md's Hadamard-transform argument.
- Qubit and gate count: `n_qubits + 1` qubits, `O(n_qubits)` gates total —
  the cheapest circuit in this repo by a wide margin (contrast with
  [benchmarks/shor.md](../../benchmarks/shor.md) and
  [benchmarks/grover.md](../../benchmarks/grover.md)).
