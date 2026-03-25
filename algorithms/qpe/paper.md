# Quantum Phase Estimation — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- The oracle gate: `controlled_power_gate(power)` for `PhaseGateOracle` —
  a controlled `P(2*pi*theta*power)` gate, since `P(phi)^power =
  P(phi*power)` for a single-qubit phase gate.
- `build_qpe_circuit(n_count, oracle, eigenstate_prep)`: `H` on every
  counting qubit, `eigenstate_prep` on the eigenstate register, controlled
  `oracle.controlled_power_gate(2**k)` per counting qubit `k`,
  `arithmetic.qft.inverse_qft` on the counting register (reused directly —
  the same construction `algorithms/shor/circuit.py` uses, now with a
  second, independent consumer), measure the counting register.
- Qubit count: `n_count + oracle.num_qubits`. For `PhaseGateOracle`,
  `oracle.num_qubits = 1`.
- Explicit comparison to `algorithms/shor/circuit.py::build_order_finding_circuit`:
  same shape, different oracle and different (implicit vs. explicit)
  eigenstate preparation — see math.md.
- Known simplifications: no refactor connecting to Shor's code (RFC-0007's
  non-goals); simulator-oriented; no transpiler optimization beyond
  Qiskit's default.

## References

See [references.bib](references.bib): Kitaev's original paper
(`kitaev1995`) for the algorithm; Nielsen & Chuang (`nielsenchuang2010`),
Section 5.2, for the standard circuit-derivation treatment this follows.
