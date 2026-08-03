# Bernstein-Vazirani Algorithm — Circuit Derivation

Level 2 of the repository's documentation-level model.
Builds on [math.md](math.md) (Math Version 1.0).

## The oracle gate

`oracles.py`'s `HiddenStringOracle(s).oracle_gate()` implements
`|x>|y> -> |x>|y XOR (s.x mod 2)>` as one `CX` per set bit of `s` (input
qubit `i` to the ancilla, wherever `s`'s bit at that position is `1`) — this
computes `y XOR (s.x mod 2)` directly, since `s.x mod 2` is exactly the XOR
of `x_i` over the positions where `s_i = 1`, and a chain of CNOTs onto a
shared target computes exactly that XOR. `O(n)` gates for *any* `s`
(including the all-zero string, the degenerate case where `f` is constantly
`0` and the "hidden string" is trivially `000...0`) — no multi-controlled
gates needed at all, unlike
[algorithms/deutsch_jozsa/oracles.py](../deutsch_jozsa/oracles.py)'s
`BalancedOracle`.

Verified against the exact `|x>|y> -> |x>|y XOR (s.x mod 2)>` truth table
via `Statevector` equivalence in `tests/test_bernstein_vazirani.py`, for
several `s` including the all-zeros and all-ones cases.

## The circuit

`circuit.py` imports `algorithms.deutsch_jozsa.circuit.build_oracle_query_circuit`
directly — no changes, no wrapper logic, just a different `Oracle` passed
in. This *is* the point of RFC-0005 bundling these two algorithms together:
the circuit shape is identical, only the oracle (and therefore the problem
being solved) differs.

## Cost

`n_qubits + 1` qubits total, `O(n_qubits)` gates (the oracle) plus a fixed
`O(n_qubits)` for the two Hadamard layers — the cheapest circuit in this
repo by a wide margin. Contrast with
[benchmarks/shor.md](../../benchmarks/shor.md) (thousands to hundreds of
thousands of gates even at `N=15`) and
[benchmarks/grover.md](../../benchmarks/grover.md) (tens to hundreds of
gates, growing with the search space) — Bernstein-Vazirani's circuit size
doesn't grow with any search space at all, since it isn't searching;
`O(n_qubits)` gates recovers all `n_qubits` bits of `s` in one shot.

## Known simplifications

- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.
- Simulator-oriented: validated against `AerSimulator` only.

See [RFC-0005](../../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)'s
"Explicit Non-goals" for the full list of what is deliberately deferred.

## References

See [references.bib](references.bib): Bernstein & Vazirani's original paper
(`bernsteinvazirani1993`) for the algorithm; Nielsen & Chuang
(`nielsenchuang2010`) for the standard circuit-derivation treatment this
follows.
