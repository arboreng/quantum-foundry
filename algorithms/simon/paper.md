# Simon's Algorithm — Circuit Derivation

Level 2 of the repository's documentation-level model.
Builds on [math.md](math.md) (Math Version 1.0).

## The oracle gate

`oracles.py` needs `|x>|y> -> |x>|y XOR f(x)>` acting on `2 * n_qubits`
qubits (`n_qubits` input + `n_qubits` output):

- **`LinearOracle(s)`**: build an `n x n` GF(2) matrix `M` with kernel
  exactly `{0, s}` — let `i` be the index of a `1` bit in `s`; for `j != i`,
  row `j` is `e_j` (if `s_j = 0`) or `e_j XOR e_i` (if `s_j = 1`); row `i`
  is all-zero. Both row constructions satisfy `row_j . s = 0 mod 2` by
  direct computation, and the `n-1` nonzero rows are linearly independent
  (each has a unique leading `1` at its own index), so `M` has rank `n-1`
  and kernel exactly `span{s}` (verified empirically: the classical kernel
  of the resulting `f(x) = Mx` is exactly `{0, s_int}` for every tested
  `s`). `f(x)_k = row_k . x`, implemented as one `CX` per set bit of row
  `k` (input qubit `j` -> output qubit `k`) — `O(n^2)` gates, generalizing
  [algorithms/deutsch_jozsa/oracles.py](../deutsch_jozsa/oracles.py)'s
  `ParityOracle` (a single linear functional) to a full matrix of them.
- **`PermutationOracle(s)`**: pair representatives `min(x, x XOR s)` are
  sorted and each assigned a label via bit-reversal of its sort-index — a
  deliberately non-GF(2)-linear scrambling (verified empirically to differ
  from `LinearOracle`'s labels for the same `s`), demonstrating the oracle
  abstraction covers non-linear two-to-one functions too. Circuit: per
  `x`, the same X-sandwich-multi-controlled-X trick as
  `BalancedOracle`, targeting the output register's bits matching `f(x)` —
  `O(2^n * n)` gates, exact but exponential.

Both verified against the exact `|x>|y> -> |x>|y XOR f(x)>` truth table via
`Statevector` equivalence, and against the "exactly two-to-one, period `s`"
property directly on the classical label tables, in
`tests/test_simon.py`.

## `build_simon_circuit`

`H^n` on the input register (uniform superposition) -> the oracle gate
(entangles input and output registers, per math.md) -> `H^n` on the input
register again -> measure the input register only. Verified empirically:
running the circuit many times, every measured bitstring `y` satisfies
`y . s = 0 mod 2` for the oracle's true `s`, and the number of distinct `y`
values observed approaches `2^(n-1)` (all vectors orthogonal to `s`) as
shots increase.

## Classical post-processing

`implementation.py`'s `_row_reduce` performs GF(2) Gaussian elimination via
XOR (representing each equation as an `n`-bit integer bitmask), reused for
two purposes: checking whether a newly measured `y` is independent of the
equations collected so far (`_rank_gf2`), and — once `n_qubits - 1`
independent equations are collected — solving for `s`
(`_solve_gf2_nullspace`): the one column not covered by a pivot after
elimination is the free variable (set to `1`), and each pivot column's bit
in `s` is read directly off that pivot row's free-column coefficient.
Verified against hand-picked independent equation sets with known solutions
before trusting it inside `find_hidden_period`'s retry loop.

## Qubit and gate count

`2 * n_qubits` qubits total. `LinearOracle`: `O(n_qubits^2)` gates.
`PermutationOracle`: `O(2^n_qubits * n_qubits)` gates — exponential,
small-`n_qubits` only (mirrors
[algorithms/shor/paper.md](../shor/paper.md)'s framing of
`PermutationMatrixOracle`'s tradeoff, and
[algorithms/deutsch_jozsa/paper.md](../deutsch_jozsa/paper.md)'s
`BalancedOracle`).

## Known simplifications

- `PermutationOracle`'s explicit lookup construction is exact but
  exponential — impractical beyond small `n_qubits` demos.
- `find_hidden_period` assumes a two-to-one oracle (see math.md's "Known
  limitations") — no one-to-one detection.
- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.
- Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0006](../../docs/rfcs/0006-simons-algorithm.md)'s "Explicit
Non-goals" for the full list of what is deliberately deferred.

## References

See [references.bib](references.bib): Simon's original paper
(`simon1994`) for the algorithm; Nielsen & Chuang (`nielsenchuang2010`) for
the standard circuit-derivation treatment this follows.
