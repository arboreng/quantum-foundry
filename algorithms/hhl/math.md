# HHL — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The linear systems problem: given Hermitian `A` and `|b>`, find `|x>`
  proportional to `x = A^-1 b`. Expand `|b>` in `A`'s eigenbasis
  (`|b> = sum_i beta_i |u_i>` for eigenpairs `(lambda_i, |u_i>)`); then
  `|x> ~ sum_i (beta_i / lambda_i) |u_i>` — HHL's job is to apply the
  `1/lambda_i` factor to each eigencomponent without knowing the
  eigendecomposition in advance.
- Using QPE (RFC-0007) to estimate each `lambda_i` onto a clock register
  in superposition, entangled with `|b>`'s eigenbasis decomposition.
- The conditional rotation: `RY(2*arcsin(C/lambda))` on an ancilla,
  applied (via a multiplexed rotation) once per clock-register branch,
  encoding the `1/lambda` factor into the ancilla's `|1>` amplitude.
- Uncomputing the clock register (QPE's inverse) so it factors out of the
  final state, leaving the b-register (conditioned on measuring the
  ancilla as `1`) proportional to `|x>`.
- Why success is postselected, not guaranteed: measuring the ancilla as
  `0` discards the shot entirely — a fundamentally different
  success/failure shape from every prior RFC (a bounded retry loop for
  Shor/Grover, a classical optimization loop for QAOA/VQE).
- The demo instance: `A = a*I + b*X`, chosen so `t` and `n_clock` make the
  eigenvalues land on exact `n_clock`-bit binary fractions (mirrors
  RFC-0007's `PhaseGateOracle` choice) — general eigenvalues would only be
  approximately estimated, per QPE's own precision/error tradeoff.
- Known limitation: no condition-number analysis or success-probability
  bound beyond citing Harrow-Hassidim-Lloyd's original result — see
  paper.md's "Known simplifications."
