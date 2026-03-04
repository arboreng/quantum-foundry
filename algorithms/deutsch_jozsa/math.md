# Deutsch-Jozsa Algorithm — Mathematical Foundations

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

TODO:

- The promise problem: `f: {0,1}^n -> {0,1}` is promised to be either
  constant (same output for all `2^n` inputs) or balanced (output `1` for
  exactly half the inputs); determine which.
- Classical query complexity: `2^(n-1) + 1` queries in the worst case
  (adversarial: any fewer, and all queries so far could be consistent with
  either a constant or a balanced function).
- Phase kickback: preparing the oracle's target qubit in `|-> = (|0>-|1>)/sqrt(2)`
  turns a bit-flip oracle `|x>|y> -> |x>|y XOR f(x)>` into a phase oracle
  `|x> -> (-1)^f(x) |x>` acting only on the input register — the same trick
  Grover's algorithm's oracle uses (`algorithms/grover/math.md`), here
  applied to a different problem.
- Why one query suffices: measuring the input register after `H^n -> oracle
  -> H^n` gives all-zeros with certainty if `f` is constant, and a nonzero
  result with certainty if `f` is balanced (derive via the Hadamard
  transform of `(-1)^f(x)`).
- Contrast with Bernstein-Vazirani (`algorithms/bernstein_vazirani/math.md`):
  same circuit, different oracle, different problem (recovering a hidden
  string rather than a constant/balanced decision) — and, unlike
  Deutsch-Jozsa's classical query complexity being *exponential*,
  Bernstein-Vazirani's classical query complexity is only *linear* (`n`
  queries), making its quantum-vs-classical gap much smaller.
