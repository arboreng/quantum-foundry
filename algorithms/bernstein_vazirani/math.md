# Bernstein-Vazirani Algorithm — Mathematical Foundations

**Math Version 1.0.**

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

## The hidden-string problem

Given oracle access to `f(x) = s.x mod 2` (bitwise-AND then parity, i.e.
inner product mod 2) for an unknown `s` in `{0,1}^n`, recover `s`.

Classically this needs exactly `n` queries: querying the standard basis
vector `e_i` (all zeros except a `1` in position `i`) returns `f(e_i) = s_i`
directly, and no fewer than `n` queries can determine `n` independent bits.
Bernstein-Vazirani solves it with a **single** quantum query — but note the
gap here (`O(1)` vs. `O(n)`) is far smaller than Deutsch-Jozsa's (`O(1)` vs.
`O(2^n)`, see [algorithms/deutsch_jozsa/math.md](../deutsch_jozsa/math.md))
even though it's *the same circuit* achieving both.

## Why measurement gives `s` directly

Exactly the same phase-kickback mechanism as Deutsch-Jozsa (see
[algorithms/deutsch_jozsa/math.md](../deutsch_jozsa/math.md)): with the
ancilla in `|->`, the oracle becomes `|x> -> (-1)^(s.x) |x>`. After
`H^n -> oracle -> H^n`, the amplitude of basis state `|z>` is:

`(1/2^n) * sum_x (-1)^(s.x) (-1)^(x.z) = (1/2^n) * sum_x (-1)^((s XOR z).x)`

This sum is `1` if `s = z` (every term is `+1`) and exactly `0` otherwise
(the `+1`/`-1` terms cancel in pairs whenever `s XOR z != 0`, the same
cancellation argument as Deutsch-Jozsa's balanced case). So measuring the
input register gives `|s>` with certainty — the measured bitstring *is* the
answer, not just correlated with it. Single-shot, deterministic, no retry
loop needed (`implementation.find_hidden_string`).

## Historical context

Bernstein-Vazirani is often presented as a stepping stone toward Simon's
algorithm and, ultimately, the order-finding subroutine at the heart of
Shor's algorithm (`algorithms/shor/math.md`) — all three belong to the
"hidden subgroup problem" family, where a hidden algebraic structure (a
string, a period, a subgroup) is extracted via a similar
Hadamard-oracle-Hadamard pattern applied to progressively richer oracles.
See VISION.md's long-term algorithm list.

## References

See [references.bib](references.bib). The algorithm follows Bernstein &
Vazirani's original paper (`bernsteinvazirani1993`); the Hadamard-transform
derivation follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
