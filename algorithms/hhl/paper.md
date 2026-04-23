# HHL — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

## `DiagonalXOracle.controlled_power_gate`

`exp(i*A*t*power)` for `A = a*I + b*X` factors into a global phase
`exp(i*a*t*power)` (since `I` commutes with everything) times
`exp(i*b*t*power*X) = RX(-2*b*t*power)`. Built as a 1-qubit circuit with
`circuit.global_phase` set to the phase term and an `RX` gate, then
`.control(1)` — Qiskit's `Gate.control()` correctly promotes a base
circuit's `global_phase` into a controlled-phase correction on the
control qubit (verified against `scipy.linalg.expm`'s exact matrix
exponential of `A`, for the controlled 2-qubit unitary, across several
`(a, b, t, power)` combinations, in `tests/test_hhl.py`).

## `build_hhl_circuit`

1. `b_state_prep` on the b-register.
2. QPE: `H` on every clock qubit, controlled
   `oracle.controlled_power_gate(2**k)` per clock qubit `k` (entangling
   the clock register with `A`'s eigenbasis decomposition of `|b>`), then
   `arithmetic.qft.inverse_qft` on the clock register (a fourth consumer
   of that shared module).
3. A multiplexed `RY` rotation on the ancilla: for each nonzero clock
   value `k` (`1` to `2**n_clock - 1`), `X` gates flip the clock qubits
   that should read `0` for that branch, a `RYGate(theta_k).control(
   n_clock)` targets the ancilla, then the `X` gates are undone.
   `theta_k = 2*arcsin(c_constant / lambda_k)` for `lambda_k =
   2*pi*k / (t * 2**n_clock)`; `k=0` is skipped entirely (angle `0`,
   avoiding division by the null eigenvalue).
4. QPE's inverse: `inverse_qft`'s inverse (the forward QFT) on the clock
   register, each controlled power gate inverted in reverse order, then
   `H` again — uncomputing the clock register back to `|0...0>` (verified
   directly against the circuit's statevector in `tests/test_hhl.py`:
   every nonzero-amplitude basis state has all clock-register bits `0`).
5. Measure the ancilla, then the b-register.

## `implementation.solve_linear_system`

Runs the circuit, then partitions the measured counts by the ancilla bit
(the last character of each bitstring, this repo's usual convention):
shots with ancilla `1` are kept, their b-register bits tallied separately,
and the ancilla-`1` fraction reported as the success probability.
Verified end to end against two closed forms in `tests/test_hhl.py`: a
single-eigenvalue branch (`|b> = |+>`, where the success probability and
`50/50` b-register split both follow directly from the rotation formula),
and a full mixed instance (`|b> = |0>`), where the b-register's
conditional distribution matches `|A^-1 b|^2` computed via plain
`numpy.linalg.solve`.

## Qubit and gate count

`n_clock + oracle.num_qubits + 1` qubits total. The multiplexed rotation
costs `2**n_clock - 1` branches, each an `n_clock`-controlled `RY` plus up
to `n_clock` `X` gates for the open controls — this dominates gate count
for larger `n_clock`, the same "exponential in the precision register"
shape as the rest of QPE-based estimation.

## Known simplifications

-   Only `A = a*I + b*X` (no general Hermitian matrix, no higher-
    dimensional systems, no sparse Hamiltonian-simulation techniques).
-   `t`/`n_clock` chosen for exact eigenvalue-to-clock-register mapping,
    not derived for a general instance (mirrors RFC-0007's
    `PhaseGateOracle` choice).
-   No amplitude amplification to boost the postselection success
    probability (`c_constant` trades off success probability against how
    close it can safely get to the smallest eigenvalue).
-   No condition-number analysis or success-probability bound derivation
    beyond citing Harrow-Hassidim-Lloyd's original result.
-   Simulator-oriented: validated against `AerSimulator` (via shots) and
    exact `Statevector`/`Operator` checks, not real hardware.

See [RFC-0010](../../docs/rfcs/0010-hhl.md)'s "Explicit Non-goals" for the
full list of what v0.2 deliberately defers.

## References

See [references.bib](references.bib): Harrow-Hassidim-Lloyd's original
paper (`harrow2009`) for the algorithm; Nielsen & Chuang
(`nielsenchuang2010`) for the standard eigenbasis/Hamiltonian treatment
this follows.
