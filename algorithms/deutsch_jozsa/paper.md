# Deutsch-Jozsa Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md) (Math Version 1.0).

## The oracle gate

`oracles.py` needs `|x>|y> -> |x>|y XOR f(x)>` acting on `n_qubits + 1`
qubits (`n_qubits` input + 1 ancilla, the ancilla always last):

- `ConstantOracle(value)`: `value=0` is the identity (`f(x) = 0` for all
  `x`, so `y XOR f(x) = y` — nothing to do); `value=1` is an unconditional
  `X` on the ancilla (flips `y` regardless of `x`).
- `ParityOracle(subset)`: one `CX` from each input qubit `i` in `subset` to
  the ancilla — `f(x) = XOR_{i in subset} x_i`, exactly what a chain of
  CNOTs onto a shared target computes. `O(|subset|)` gates, always balanced
  for non-empty `subset` (flipping any single input bit flips `f`).
- `BalancedOracle(marked)`: for each marked bitstring `m`, the same
  "X-sandwich a multi-controlled-X" trick as
  [algorithms/grover/oracles.py](../grover/oracles.py)'s
  `MarkedBitstringOracle` (there, targeting phase via multi-controlled-Z;
  here, targeting the ancilla via multi-controlled-X, since this oracle
  needs an explicit bit-flip target rather than a phase). `O(|marked| *
  n_qubits)` gates — exact for any half-sized marked set, but exponential
  in `n_qubits` since `|marked| = 2^(n_qubits-1)` by the balanced-function
  definition.

All three verified against the exact `|x>|y> -> |x>|y XOR f(x)>` truth table
via `Statevector`/`Operator` equivalence in `tests/test_deutsch_jozsa.py`.

## `build_oracle_query_circuit`

Shared verbatim with `algorithms/bernstein_vazirani/circuit.py`:

1. Ancilla: `X` then `H` (prepares `|1> -> |->`).
2. `H` on every input qubit (uniform superposition).
3. Apply `oracle.oracle_gate()` across the input register + ancilla (phase
   kickback — see math.md).
4. `H` on every input qubit again (undoes the superposition if the
   accumulated phase pattern allows constructive interference at `|0>^n`).
5. Measure the input register only (the ancilla is never measured — its
   role was entirely to enable phase kickback).

## Known simplifications

- `BalancedOracle`'s explicit marked-set construction is exact but
  exponential — a genuinely balanced function on many qubits would in
  practice be given by a formula (like `ParityOracle`'s), not an explicit
  enumerated half of all bitstrings. Mirrors
  [algorithms/shor/paper.md](../shor/paper.md)'s framing of
  `PermutationMatrixOracle`'s tradeoff.
- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.
- Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)'s
"Explicit Non-goals" for the full list of what v0.2 deliberately defers.

## References

See [references.bib](references.bib): Deutsch & Jozsa's original paper
(`deutschjozsa1992`) for the algorithm; Nielsen & Chuang
(`nielsenchuang2010`) for the standard circuit-derivation treatment this
follows.
