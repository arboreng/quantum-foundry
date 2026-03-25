# Quantum Phase Estimation — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The phase estimation problem: given a unitary `U` and an eigenstate
  `|psi>` with `U|psi> = e^(2*pi*i*theta)|psi>`, estimate `theta` (a real
  number in `[0, 1)`, not generally rational).
- Why controlled powers of `U` applied to a counting register in
  superposition, followed by an inverse QFT, concentrate the counting
  register's amplitude near the `n_count`-bit binary expansion of `theta`.
- Precision: with `n_count` counting qubits, the estimate is accurate to
  `1/2^n_count` with probability at least `4/pi^2 ≈ 0.405` if `theta`'s
  binary expansion doesn't terminate exactly within `n_count` bits, and
  with certainty if it does. Contrast with
  [algorithms/shor/math.md](../shor/math.md)'s continued-fraction argument,
  which needs `theta` to be *rational* with a small denominator — QPE in
  general estimates arbitrary real `theta`, and Shor's order-finding is the
  special case where the underlying phase is known in advance to be
  rational.
- Connection to Shor: `algorithms/shor/oracles.py`'s `Oracle` protocol
  supplies controlled powers of the modular-multiplication unitary; the
  "eigenstate" there is actually a uniform superposition over that
  unitary's eigenbasis (prepared implicitly by initializing the work
  register to `|1>`), not a single true eigenstate — see
  `algorithms/shor/math.md`'s eigenstate argument for why this still works.
- Known limitation: this implementation assumes `eigenstate_prep` exactly
  prepares an eigenstate of `oracle`'s unitary; it does not address
  imperfect eigenstate preparation.

## References

See [references.bib](references.bib). The algorithm follows Kitaev's
original paper (`kitaev1995`); the precision analysis follows Nielsen &
Chuang's textbook treatment (`nielsenchuang2010`), Section 5.2.
