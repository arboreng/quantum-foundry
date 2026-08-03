# Reversible Modular Arithmetic — Circuit Derivation

Level 2 of the repository's documentation-level model.
Builds on [math.md](math.md) (Math Version 1.0). Describes the exact circuits
in [adders.py](adders.py), in the order they compose.

## `add_constant_gate(num_qubits, c)`

```
|x>  --[QFT]--[P(θ_0) on qubit 0]...[P(θ_{n-1}) on qubit n-1]--[QFT†]-->  |x + c mod 2^n>
```

where `θ_j = 2*pi*c / 2^(n-j)` for `j = 0, ..., n-1` (see math.md for why
this is exactly the phase a cyclic shift by `c` induces). `n = num_qubits`
qubits, no ancillas. Verified against brute-force classical addition (all
`x`, several `c` including negative) in `test_add_constant_gate_matches_classical_addition`.

## `add_constant_mod_N_gate(num_qubits, c, N)`

Operates on an `(num_qubits + 1)`-qubit register `reg` (the extra bit is
overflow headroom) plus 1 ancilla — `num_qubits + 2` qubits total:

```
reg: |x>  --[+c]--[+(-N)]--•------------------[+(-c)]--X--•--X--[+c]-->  |x+c mod N>
                            |                                |
anc: |0>  ------------------⊕---[+N, controlled on anc]------⊕--------->  |0>
```

Step by step (see math.md for the *why*):
1. `+c`, `+(-N)` on `reg` (both `add_constant_gate` calls on `n = num_qubits + 1` qubits).
2. `CX(msb -> anc)`: `anc = 1` iff `reg` is negative (i.e. `x + c < N`).
3. `add_N.control(1)` from `anc`: conditionally undoes the speculative `-N`.
4. `+(-c)` on `reg`: subtracts `c` back out, to recompute `msb` for uncomputing `anc`.
5. `X(msb)`, `CX(msb -> anc)`, `X(msb)`: **anti**-controlled clear of `anc`
   (math.md explains why this must be anti-controlled, not a repeat of step 2).
6. `+c` on `reg`: restores the correct final value `(x + c) mod N`.

Verified against brute-force classical modular addition (all `c`, all `x < N`,
both N=15 and N=21, ancilla checked back at `|0>`) in
`test_add_constant_mod_N_gate_matches_classical_addition`.

## `controlled_mult_mod_N_gate(num_qubits, a, N)`

Qubit layout: 1 control (`ctrl`) + `num_qubits` input register (`y`) +
`(num_qubits + 2)` accumulator (`acc`, sized to match
`add_constant_mod_N_gate`'s own width) + 1 combined-control ancilla (`cc`) —
`num_qubits + 3` ancillas total beyond the control and work register,
matching `Oracle.num_ancilla_qubits` in `algorithms/shor/oracles.py`.

For each bit `i` of `y` (accumulation phase, multiplier `a`, then again with
multiplier `-a^-1 mod N` for uncomputation):

```
ctrl, y[i]  --•--------------------------•-->
              |                          |
cc          --⊕--•------------------•----⊕-->
                  |                  |
acc         ------[+(a·2^i mod N) mod N, controlled on cc]------>
```

The `Toffoli(ctrl, y[i] -> cc)` / `Toffoli` pair implements "controlled on
*both* `ctrl` and `y[i]`" without asking Qiskit to synthesize `.control(2)`
directly on an already-composite `add_constant_mod_N_gate` — an approach that
was tried first during RFC-0002 development and found to be both **wrong**
(silently produced identity-like behavior for most inputs, only accidentally
correct at fixed points of the multiplication map — see the git history for
the debugging session) and **~10x slower** to even construct than the
Toffoli-AND + single-`.control(1)` version used here. `.control(1)` on a
composite gate is the same pattern already validated inside
`add_constant_mod_N_gate` itself (`add_N.control(1)`), so this reuses a
building block that was independently verified rather than trusting a new,
more complex synthesis path.

After accumulation, a controlled-swap moves `acc`'s low `num_qubits` bits
(holding `a*y mod N`) into `y`; a second accumulation pass with multiplier
`-a^-1 mod N` (over the now-swapped-in `y`) returns `acc` to `|0>`.

Verified against brute-force classical multiplication (both `ctrl` values,
all `y < N`, ancillas checked back at `|0>`) in
`test_controlled_mult_mod_N_gate_matches_classical_multiplication` (N=15) and
the `@pytest.mark.slow` N=21 test in
`algorithms/shor/tests/test_gate_decomposed_oracle.py`.

## Qubit and cost accounting

For a Shor order-finding circuit at a given `N` (`n_work = N.bit_length()`,
`n_count = 2 * n_work`), `GateDecomposedOracle` needs
`n_count + n_work + (n_work + 3)` qubits total (counting register + work
register + this module's ancillas) — 19 at N=15, 23 at N=21, matching
[benchmarks/shor.md](../benchmarks/shor.md)'s measured `qubit_count` column.
That doc also has the gate-count and simulation-time cost of all this
elementary-gate machinery relative to
[algorithms/shor/oracles.py](../algorithms/shor/oracles.py)'s
`PermutationMatrixOracle` — two to three orders of magnitude more gates, for
the sake of being an actual reversible-arithmetic circuit rather than a
classically-precomputed dense unitary.

## Known simplifications

- Not qubit-count-optimal: Beauregard's original construction totals
  `2n + 3` qubits; the extra combined-control ancilla here trades a qubit for
  implementation simplicity (see math.md).
- No T-count / gate-count optimization — see RFC-0002's non-goals.
- The Toffoli-AND + `.control(1)` pattern is a pragmatic workaround for a
  specific Qiskit control-synthesis limitation observed during development,
  not a claim that ripple-carry-style controlled arithmetic is superior in
  general.

## References

See [algorithms/shor/references.bib](../algorithms/shor/references.bib) —
`draper2000`, `beauregard2002`, `vedral1996` — and [math.md](math.md) for how
each maps to the constructions above.
