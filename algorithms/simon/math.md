# Simon's Algorithm — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The hidden-period problem: `f: {0,1}^n -> {0,1}^n` promised to be either
  one-to-one, or exactly two-to-one with `f(x) = f(x XOR s)` for an unknown
  nonzero `s`; find `s`.
- Classical query complexity: exponential (`Omega(2^(n/2))`, a
  birthday-paradox-style collision-finding lower bound) — contrast with the
  quantum algorithm's `O(n)` queries.
- Why each run of `H^n -> oracle -> H^n -> measure input register` yields a
  uniformly random `y` satisfying `y . s = 0 mod 2` (derive from the
  entangled state `sum_x |x>|f(x)>` after the oracle, and what measuring —
  or simply not caring about — the output register does to the input
  register's state).
- Why `n - 1` linearly independent such `y` (over GF(2)) determine `s`
  uniquely (up to the one bit of information that no measurement can ever
  supply: whether `f` is one-to-one at all, distinguished by checking
  `f(0) == f(s)` for the candidate `s` classically after the fact), and why
  `O(n)` repetitions suffice with high probability to collect `n-1`
  independent equations.
- Contrast with [algorithms/bernstein_vazirani/math.md](../bernstein_vazirani/math.md):
  same "collect linear equations via Hadamard-oracle-Hadamard" shape, but
  Bernstein-Vazirani's oracle is already linear in a way that directly
  reveals `s` in one shot; Simon's needs multiple shots and a genuine
  classical solve step, foreshadowing
  [algorithms/shor/math.md](../shor/math.md)'s continued-fraction
  post-processing.
