# Reversible Modular Arithmetic — Mathematical Foundations

**Math Version 1.0.** Written for [RFC-0002](../docs/rfcs/0002-gate-decomposed-arithmetic.md)
(gate-decomposed modular arithmetic); mirrors the versioning convention set
by [algorithms/shor/math.md](../algorithms/shor/math.md).

Level 1 of [VISION.md's understanding model](../VISION.md#levels-of-understanding),
for the constructions in [adders.py](adders.py).

## Addition is diagonal in the Fourier basis

The classical operation `x -> x + c mod 2^n` is a cyclic shift on
`Z/2^n Z`. The discrete Fourier transform diagonalizes cyclic shifts: in the
Fourier basis, "shift by `c`" becomes "multiply basis state `|y>` by the
phase `e^(2*pi*i*c*y/2^n)`" — no carrying, no entangling gates between
qubits, just one single-qubit phase rotation per output qubit of the QFT.
This is exactly why `add_constant_gate` is `QFT -> per-qubit phase rotation
-> inverse QFT` (Draper 2000): it's cheaper to add in the basis where
addition is diagonal than to build a ripple-carry adder directly in the
computational basis.

Concretely: qubit `j` (0-indexed) of the post-QFT register picks up phase
angle `2*pi*c / 2^(n-j)`. Subtracting `c` is the same construction with `-c`
(equivalently `2^n - c`), since phase rotations are additive and the QFT
doesn't care whether `c` is expressed as a positive residue or a negative
offset.

## Modular reduction: Beauregard's overflow trick

`add_constant_gate` only computes mod `2^n`, but Shor's algorithm needs mod
`N` for the specific composite being factored, where `N` is not generally a
power of two. `add_constant_mod_N_gate` reduces `x + c mod N` (for `x < N`)
to *two* mod-`2^n` additions plus a comparison:

1. Compute `x + c - N` mod `2^n` on an `(n+1)`-bit register (the extra bit
   is headroom so the result doesn't silently wrap).
2. If `x + c >= N`, this value is `>= 0` (correct — no action needed). If
   `x + c < N`, this value is negative, which in `(n+1)`-bit two's-complement
   representation shows up as the high-order bit being `1`.
3. So the high-order bit *is* the "did I subtract too much" flag: copy it
   into an ancilla (a plain CNOT), and conditionally add `N` back based on
   that ancilla.

The subtlety is returning the ancilla to `|0>` for reuse (every ancilla in a
reversible circuit must be uncomputed, or it silently entangles with — and
corrupts — every later use of the same qubit). After the correction, the
register holds the true answer `(x + c) mod N` in *both* branches, so
subtracting `c` again recovers `x` in the branch that needed correction and
`x - N` (negative) in the branch that didn't — the two branches' high-order
bits are now swapped relative to step 2, so the ancilla must be cleared with
an *anti*-controlled correction (fire when the bit is `0`, not `1`) rather
than the same plain CNOT used to set it. Getting this backwards was an actual
bug caught during RFC-0002 development (see `add_constant_mod_N_gate`'s
inline comments) — it's the kind of sign error that only shows up as
incorrect results, not a crash, which is why every layer here is verified
against brute-force classical arithmetic in `arithmetic/tests/test_adders.py`
rather than trusted by derivation alone.

## Controlled multiplication via double-and-add

`a * y mod N` for a quantum register `|y>` is computed the same way you'd
compute it by hand in binary: `a * y = sum_i y_i * (a * 2^i)`, so
accumulating `a * 2^i mod N` into a scratch register once for each set bit
`y_i` of `y` gives `a * y mod N` in the scratch register — this is exactly
what `controlled_mult_mod_N_gate`'s `accumulate` does, reusing
`add_constant_mod_N_gate` as the accumulation primitive with a classically
precomputed shifted constant (`a * 2^i mod N`) at each step. `pow(a, 2**i, N)`-style
values are cheap to compute classically ahead of time — only the
*addition into the register* needs to happen quantumly.

Once the scratch register holds `a * y mod N`, a controlled-swap moves that
value into the original `y` register (and moves the original `y` into
scratch). The scratch register must then be zeroed for reuse; multiplying
the *new* contents of `y` (which is `a * y mod N`) by `-a^-1 mod N` and
accumulating that into scratch cancels it back to `0`, using the number
-theoretic fact `a^-1 * a ≡ 1 (mod N)` (`modinv`, via the extended Euclidean
algorithm) — the same "compute, use, uncompute" discipline as the ancilla
above, just one level up.

## Common misconceptions

- **This construction is not the most qubit-efficient possible.** Beauregard's
  original paper describes a `2n + 3`-qubit total circuit; the version here
  uses more (see [paper.md](paper.md)'s qubit accounting) because of an
  additional combined-control ancilla — a deliberate simplicity-over-optimality
  tradeoff, not a claim of matching the literature's qubit count. See
  [benchmarks/shor.md](../benchmarks/shor.md) for what this costs in practice.
- **"Reversible" does not mean "the accumulator is never touched."** Every
  intermediate register (the overflow-detection ancilla, the multiplication
  scratch register) *is* written to — it must be, that's how the computation
  happens — the requirement is only that it's returned to `|0>` by the time
  the gate finishes, so it doesn't carry information (and therefore
  entanglement/decoherence risk) forward into later gates.
- **The QFT-based adder is not "using the QFT to add" in the sense Shor's
  algorithm uses the QFT for phase estimation.** These are two unrelated uses
  of the same primitive: phase estimation uses the QFT to read a phase out
  as a bitstring; the adder uses it because addition happens to be diagonal
  (i.e. phase-only) in that basis. Building both from the same `arithmetic/qft.py`
  is a code-reuse convenience, not a mathematical coincidence.
