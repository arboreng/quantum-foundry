# Shor's Algorithm — Mathematical Foundations

**Math Version 1.0.** This document derives the classical number theory
implemented in `implementation.py`. Later RFCs that introduce alternate
constructions (e.g. Beauregard's circuit or a semiclassical QFT) should add a
new versioned section rather than rewriting this one — see [paper.md](paper.md)
for the versioning rationale.

Level 1 of the repository's documentation-level model.

## Factoring reduces to order finding

To factor a composite odd integer `N` (even `N` and prime powers are handled
classically — see `_perfect_power_factor` in `implementation.py`, no quantum
step needed):

1. Pick a random `a` with `1 < a < N`. If `gcd(a, N) > 1`, that gcd is already
   a nontrivial factor — done classically, no quantum step needed.
2. Otherwise, `a` is invertible mod `N`, so the sequence `a mod N, a^2 mod N,
   a^3 mod N, ...` is eventually periodic. Its **order** `r` is the smallest
   positive integer such that `a^r ≡ 1 (mod N)`.
3. If `r` is even and `a^(r/2) ≢ -1 (mod N)`, then `x = a^(r/2) mod N`
   satisfies `x^2 ≡ 1 (mod N)` but `x ≢ ±1 (mod N)` — a nontrivial square
   root of 1. Then `(x-1)(x+1) ≡ 0 (mod N)` while neither factor is `≡ 0`, so
   `N` must divide the product without dividing either term individually,
   which means `gcd(x - 1, N)` and `gcd(x + 1, N)` are nontrivial factors of
   `N`. This is exactly `recover_factor` in `implementation.py`.
4. If `r` is odd, or `a^(r/2) ≡ -1 (mod N)`, this choice of `a` doesn't work
   — pick a new random `a` and retry (`factor`'s retry loop).

For a random `a` coprime to `N` (with `N` odd and not a prime power), the
probability that `r` is even *and* `a^(r/2) ≢ -1 (mod N)` is at least `1/2`,
so a handful of retries succeeds with overwhelming probability.

## Order finding via quantum phase estimation

Classically, finding `r` requires computing `a^x mod N` for up to `O(N)`
values of `x` — exponential in the bit length of `N`. The quantum speedup
comes entirely from this step: phase estimation lets us extract `r` using
only `O(log N)` applications of modular multiplication, in superposition.

Define the unitary `U|y> = |a*y mod N>`. Its eigenstates have eigenvalues
`e^(2*pi*i*s/r)` for `s = 0, ..., r-1`. Preparing (an equal superposition
over) these eigenstates and running quantum phase estimation on `U` yields a
measurement that is, with high probability, close to `s/r` for a random `s`.
See [paper.md](paper.md) for how the counting register, controlled powers of
`U`, and inverse QFT realize this in `circuit.py`.

## Continued-fraction recovery of `r`

Phase estimation gives a phase `phi ≈ s/r` as an `n_count`-bit binary
fraction, not `r` directly. Because `r < N`, the continued-fraction
expansion of `phi` is guaranteed (Nielsen & Chuang, Theorem 5.1) to contain
`s/r` in lowest terms as one of its convergents whenever `n_count >= 2 *
log2(N)` — which is why `build_order_finding_circuit` defaults to `n_count =
2 * N.bit_length()`. `find_order` uses Python's `fractions.Fraction(phi).
limit_denominator(N)` to compute exactly this convergent; its denominator is
the candidate order, which `find_order` then verifies classically via
`pow(a, order, N) == 1` before reporting success.

## Common misconceptions

- **Shor's algorithm does not factor `N` on the quantum computer.** The
  quantum computer solves order finding; a nontrivial factor is only
  recovered afterward via a classical `gcd`. No quantum operation ever
  "divides" `N`.
- **The speedup is entirely in order finding, not in the gcd/continued-fraction
  post-processing**, which are both classical and efficient (`O(log N)` /
  polynomial time) whether or not a quantum computer is involved.
- **A single run is not guaranteed to succeed.** Both the choice of `a` and
  the phase measurement are probabilistic; `factor`'s retry loop is not a
  workaround for a bug, it's inherent to the algorithm.
- **The circuit in this repo does not demonstrate quantum speedup when
  simulated classically.** `PermutationMatrixOracle` computes the modular
  multiplication classically to build the oracle matrix — see paper.md's
  "Known simplifications". The speedup argument is about circuit depth on a
  real quantum computer, not simulator wall-clock time.

## References

See [references.bib](references.bib). The order-finding reduction and
phase-estimation argument above follow Shor's original paper
(`shor1994`) and Nielsen & Chuang's textbook treatment (`nielsenchuang2010`,
particularly Theorem 5.1 for the continued-fraction convergent guarantee).
