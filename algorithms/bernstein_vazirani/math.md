# Bernstein-Vazirani Algorithm — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The hidden-string problem: given oracle access to `f(x) = s.x mod 2`
  (inner product mod 2) for an unknown `s` in `{0,1}^n`, recover `s`.
- Classical query complexity: exactly `n` queries (one per bit of `s`, e.g.
  querying each standard basis vector `e_i`) — contrast with
  [algorithms/deutsch_jozsa/math.md](../deutsch_jozsa/math.md)'s
  *exponential* classical query complexity for the constant/balanced
  decision problem. Bernstein-Vazirani's quantum-vs-classical gap is
  `O(1)` vs. `O(n)` queries — a smaller gap than Deutsch-Jozsa's, but the
  *same circuit* achieves it.
- Why measuring the input register after `H^n -> oracle -> H^n` gives `s`
  directly and deterministically (derive via the Hadamard transform of
  `(-1)^(s.x)`, same phase-kickback mechanism as
  `algorithms/deutsch_jozsa/math.md`).
- Historical note: Bernstein-Vazirani is often presented as a special case
  of / stepping stone to Simon's algorithm and, ultimately, Shor's algorithm
  (all in the "hidden subgroup problem" family) — see VISION.md's long-term
  algorithm list.
