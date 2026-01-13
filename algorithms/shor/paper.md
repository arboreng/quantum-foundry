# Shor's Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md) (Math Version 1.0).

## Quantum Fourier Transform

The QFT on `n` qubits maps computational basis state `|x>` to
`(1/sqrt(2^n)) * sum_y e^(2*pi*i*x*y/2^n) |y>`. `circuit.py`'s `qft`/`inverse_qft`
build this directly from `H` and controlled-phase gates (`cp`) plus a final
qubit-order swap, rather than calling `qiskit.circuit.library.QFTGate` — the
construction is verified against Qiskit's own implementation in
`tests/test_shor.py::test_qft_matches_qiskit` via `Operator` equivalence.

Phase estimation uses the *inverse* QFT: given a counting register in the
state produced by controlled powers of `U` applied to an eigenstate of `U`
(see math.md), the inverse QFT concentrates the amplitude near the
computational basis state encoding the eigenphase, so measurement recovers
it directly.

## The oracle: `PermutationMatrixOracle`

`build_order_finding_circuit` needs, for each counting qubit `k`, a gate
implementing `U^(2^k) |y> = |a^(2^k) * y mod N>` controlled on that qubit.
`oracles.PermutationMatrixOracle` computes `a^(2^k) mod N` classically (cheap
— `O(log N)` via `pow(a, 2**k, N)`), then classically builds the
`2^n_work x 2^n_work` permutation matrix for "multiply by that residue mod N"
and embeds it as a Qiskit `UnitaryGate`, controlled on the relevant counting
qubit. Because `gcd(a, N) = 1` (checked before circuit construction), this
map is a bijection on `{0, ..., N-1}`, extended by the identity on
`{N, ..., 2^n_work - 1}` so the full matrix is unitary.

This gives an *exact*, general oracle for any `N` and any `a` coprime to it —
unlike tutorial implementations that hand-derive a fixed gate sequence for a
single `N` (typically 15). See "Known simplifications" below for what this
does *not* do.

## Full circuit

`build_order_finding_circuit(N, a)`:

1. Counting register: `n_count = 2 * N.bit_length()` qubits, each set to
   `|+>` via `H`.
2. Work register: `N.bit_length()` qubits, initialized to `|1>`.
3. For counting qubit `k = 0, ..., n_count - 1`: apply
   `oracle.controlled_power_gate(2**k)`, controlled on qubit `k`, targeting
   the work register.
4. Apply `inverse_qft` to the counting register.
5. Measure the counting register.

Qubit count grows as `n_count + n_work = 3 * N.bit_length()` — e.g. 12 qubits
for `N=15`, 15 qubits for `N=21` — well within reach of `AerSimulator`'s
statevector method for the small `N` this implementation targets (see
`algorithms/shor/README.md`).

## Known simplifications (v0.2)

- Uses exact, classically-computed permutation matrices for the oracle (via
  `UnitaryGate`) rather than synthesizing modular multiplication from
  elementary/reversible-arithmetic gates (e.g. Cuccaro adders, Beauregard's
  construction).
- Not NISQ-optimized: no gate-count or T-count minimization.
- Simulator-oriented: validated against `AerSimulator` only, not against real
  hardware or a noise model.
- No transpiler-level circuit optimization beyond Qiskit's default
  `transpile()` pass used by `execution.AerExecutor`.

See [RFC-0001](../../docs/rfcs/0001-shors-algorithm.md)'s "Explicit
Non-goals" section for the full list of what v0.2 deliberately defers.
