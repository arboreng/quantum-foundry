# VQE — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- `ansatz_circuit`: `reps` layers of per-qubit `RY(theta)` plus a ladder of
  entangling `CX` gates, then one final `RY` layer — `n_qubits * (reps +
  1)` parameters total.
- `measurement_circuit`: `ansatz_circuit` followed by the basis-rotation
  gates for a given `PauliTerm` (`H` for `X`, `Sdg` then `H` for `Y`,
  nothing for `Z`/`I`), then measure every qubit.
- The classical loop in `implementation.py`: `expectation_value` runs one
  measurement circuit per non-identity Pauli term, combines each shot's
  `+-1` parity weighted by counts, and sums `coefficient * <term>` over
  all terms (an identity term contributes its coefficient with no circuit
  execution) — this is `solve_ground_state`'s objective,
  `scipy.optimize.minimize` (COBYLA, matching RFC-0008) tunes `params`
  against.
- Qubit and gate count as a function of `n_qubits`, `reps`, and the number
  of Hamiltonian terms (one full circuit execution per non-identity term —
  see Known simplifications).
- Known simplifications: no measurement grouping (qubit-wise-commuting
  terms aren't batched into shared circuit executions); no gradient-based
  optimization (COBYLA only); a fixed hardware-efficient ansatz (no
  chemistry-motivated ansatz like UCCSD); simulator-oriented.
