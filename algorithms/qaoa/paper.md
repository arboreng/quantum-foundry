# QAOA — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The cost gate: `exp(-i*gamma*C)` for `C = sum_{(i,j)} (1 - Z_i Z_j)/2`
  factors into one two-qubit `RZZ`-equivalent gate per edge (`CX` - `RZ` -
  `CX`, since all terms commute), implemented in `MaxCutProblem.cost_gate`.
- The mixer gate: `exp(-i*beta*B)` for `B = sum_i X_i` factors into one
  single-qubit `RX(2*beta)` per qubit (`circuit.mixer_gate`).
- `build_qaoa_circuit`: `H^n` (uniform superposition over all `2^n`
  candidate cuts) -> `p` layers of (cost gate, mixer gate) -> measure.
- The classical loop in `implementation.py`: `expectation_value` (average
  `problem.cost_value` over measured counts) as the objective
  `scipy.optimize.minimize` tunes `(gammas, betas)` against.
- Qubit and gate count as a function of `n_qubits`, `|edges|`, and `p`.
- Known simplifications: no approximation-ratio guarantee derived or
  checked; a fixed classical optimizer (`scipy.optimize.minimize`'s
  default method) rather than a comparison across optimizers; simulator-
  oriented.
