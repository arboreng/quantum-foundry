# arithmetic/

Shared quantum arithmetic building blocks, factored out for reuse across
algorithms.

- [math.md](math.md) — number-theoretic foundations (why addition is
  diagonal in the Fourier basis, Beauregard's overflow trick, double-and-add
  multiplication)
- [paper.md](paper.md) — circuit derivation for each gate below
- [qft.py](qft.py) — from-scratch Quantum Fourier Transform (`qft`,
  `inverse_qft`). Originally written for
  [algorithms/shor/](../algorithms/shor/)'s phase estimation circuit
  ([RFC-0001](../docs/rfcs/0001-shors-algorithm.md)); relocated here in
  [RFC-0002](../docs/rfcs/0002-gate-decomposed-arithmetic.md) once the adders
  below needed it too.
- [adders.py](adders.py) — reversible modular arithmetic built on `qft.py`:
  `add_constant_gate` (Draper's QFT-based constant adder),
  `add_constant_mod_N_gate` (Beauregard's modular adder),
  `controlled_mult_mod_N_gate` (controlled multiplication by a classical
  constant mod `N`). Used by `algorithms.shor.oracles.GateDecomposedOracle`
  as an elementary-gate alternative to RFC-0001's classically-computed
  permutation-matrix oracle.
- [tests/](tests/) — correctness tests, verified against brute-force
  classical arithmetic at each layer.
