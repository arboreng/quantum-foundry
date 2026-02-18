# Grover's Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The phase-flip oracle: `|x> -> -|x>` for marked `x`, identity otherwise —
  construction from multi-controlled-Z gates for an arbitrary marked set.
- The diffusion operator: `H^n -> (phase flip about |0>) -> H^n`, i.e.
  reflection about the uniform superposition's average amplitude.
- Full circuit: `H^n` (uniform superposition) -> repeated
  `(oracle, diffusion)` pairs, iteration count from math.md -> measurement.
- Qubit and gate count as a function of `n_qubits` and the marked set size.
- Simplifications used in the simulator implementation vs. a hardware-
  faithful circuit (mirrors `algorithms/shor/paper.md`'s "Known
  simplifications" framing).
