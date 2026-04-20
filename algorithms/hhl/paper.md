# HHL — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- `DiagonalXOracle.controlled_power_gate`: `exp(-i*A*t*power)` for
  `A = a*I + b*X` factors into a controlled global phase (`P(-a*t*power)`
  on the control qubit) times `RX(-2*b*t*power)` on the target, since `I`
  and `X` commute.
- `build_hhl_circuit`: `b_state_prep` -> QPE (`H^n_clock` -> controlled
  powers of the oracle -> inverse QFT, reusing `arithmetic.qft`) -> a
  multiplexed `RY` rotation on the ancilla, conditioned on the clock
  register's value -> QPE's inverse (uncomputing the clock register) ->
  measure the ancilla and the b-register.
- The multiplexed rotation: one `RY(2*arcsin(C/lambda_k))` per clock
  value `k` (`lambda_k = 2*pi*k / (t * 2**n_clock)`, angle `0` for `k=0`
  to avoid dividing by the null eigenvalue), implemented as `2**n_clock`
  multi-controlled `RY` gates (X-gate open-controls on the clock qubits
  that should be `0` for that branch, then a controlled rotation, then
  undo the X gates).
- `implementation.solve_linear_system`: runs the circuit, computes the
  ancilla-`1` success probability, and returns the b-register's measured
  distribution conditioned on that postselection.
- Qubit and gate count as a function of `n_clock` (the multiplexed
  rotation's `2**n_clock` branches dominate gate count for larger
  `n_clock`).
- Known simplifications: only `A = a*I + b*X` (no general Hermitian
  matrix, no higher-dimensional systems); `t`/`n_clock` chosen for exact
  eigenvalue-to-clock-register mapping, not derived for a general
  instance; no amplitude amplification to boost the postselection success
  probability; simulator-oriented.
