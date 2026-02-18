# Grover's Algorithm — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The unstructured search problem: given a boolean oracle marking `M` out of
  `N = 2^n` items, find a marked item using as few oracle queries as
  possible.
- Amplitude amplification: how alternating the oracle's phase flip with a
  reflection about the average amplitude (the diffusion operator) rotates
  the state vector toward the marked subspace.
- Why the optimal number of iterations is `~ (pi/4) * sqrt(N/M)`, and why
  overshooting/undershooting that count reduces success probability
  (over-rotation past the marked subspace).
- The `O(sqrt(N))` query complexity and why this is provably optimal (the
  BBBV lower bound) — i.e. why Grover's algorithm is a quadratic, not
  exponential, speedup (contrast with Shor's algorithm's exponential
  speedup — see `algorithms/shor/math.md`).
