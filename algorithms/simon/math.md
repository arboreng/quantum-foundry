# Simon's Algorithm — Mathematical Foundations

**Math Version 1.0.**

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

## The hidden-period problem

`f: {0,1}^n -> {0,1}^n` is promised to be either one-to-one, or exactly
two-to-one with `f(x) = f(x XOR s)` for an unknown nonzero `s`. Find `s`
(this repo's implementation assumes the two-to-one case — see "Known
limitations" below).

Classically this needs `Omega(2^(n/2))` queries in the worst case (a
birthday-paradox argument: you need to query roughly `sqrt(2^n)` random
inputs before two of them are likely to collide under `f`, and only a
collision reveals any information about `s`). Simon's algorithm solves it
with `O(n)` quantum queries — an *exponential* separation, the same order of
speedup [algorithms/shor/math.md](../shor/math.md) achieves for factoring
(unlike [algorithms/grover/math.md](../grover/math.md)'s quadratic one).

## Why each run yields an equation `y . s = 0 mod 2`

After `H^n` on the input register and the oracle, the state is (up to
normalization) `sum_x |x>|f(x)>`. Because `f` is two-to-one, this is
`sum_{representatives r} (|r> + |r XOR s>) |f(r)>` — each output branch
`|f(r)>` is entangled with exactly the two-element superposition `|r> +
|r XOR s>`. Applying `H^n` to the input register again and computing the
amplitude of basis state `|y>`:

`sum_x (-1)^(x.y) [x in {r, r XOR s}] = (-1)^(r.y) * (1 + (-1)^(s.y))`

This is `0` whenever `s . y = 1 mod 2` (the two terms cancel), and nonzero
(magnitude `2`) whenever `s . y = 0 mod 2`. So measuring the input register
can *only* ever yield a `y` with `y . s = 0 mod 2` — every single run
produces one linear equation constraining `s`, regardless of which
`(x, f(x))` branch the (unmeasured) output register statistically
corresponds to.

## Why `n - 1` independent equations determine `s`

`s` lives in the `n`-dimensional vector space `GF(2)^n`. Each measured `y`
constrains `s` to an `(n-1)`-dimensional hyperplane (`y . s = 0`). `n - 1`
*independent* such constraints intersect in exactly a 1-dimensional
subspace — and since `s != 0` by the problem's promise, that subspace must
be exactly `{0, s}`, pinning down `s` uniquely (see
`implementation._solve_gf2_nullspace`, the from-scratch GF(2) Gaussian
elimination that does this). Each run's `y` is uniformly random over the
`2^(n-1)` vectors orthogonal to `s`, so collecting `n-1` *independent* ones
takes `O(n)` repetitions with high probability (a coupon-collector-style
argument: the probability a fresh random `y` is dependent on the ones
already collected shrinks geometrically as more are collected).

## Known limitations (v0.2)

This implementation assumes `oracle` is genuinely two-to-one — both
`LinearOracle` and `PermutationOracle` guarantee this by construction, so
`find_hidden_period` never needs to handle the one-to-one branch of the
promise problem. A complete treatment would also classically verify a
candidate `s` (e.g. checking `f(0) == f(s)`) and detect the one-to-one case
when the collected equations turn out to have full rank `n` (no nontrivial
common solution) — not implemented here, since neither of this repo's
oracles can produce that case to test against.

## Contrast with the rest of this repo's "hidden subgroup" family

[algorithms/bernstein_vazirani/math.md](../bernstein_vazirani/math.md)'s
oracle already reveals its hidden string `s` from a *single* query (its
oracle is linear in a stronger sense — a linear functional, not just a
two-to-one map). Simon's needs `O(n)` queries and a genuine classical solve
step. [algorithms/shor/math.md](../shor/math.md)'s order-finding needs
still more structure (the group is `Z`, not `GF(2)^n`, requiring the QFT and
continued fractions rather than Hadamards and linear algebra) — Simon's
algorithm is the historical and pedagogical bridge between the two.

## References

See [references.bib](references.bib). The algorithm follows Simon's
original paper (`simon1994`); the analysis follows Nielsen & Chuang's
textbook treatment (`nielsenchuang2010`).
