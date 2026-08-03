# Deutsch-Jozsa Algorithm — Mathematical Foundations

**Math Version 1.0.**

Level 1 of the repository's documentation-level model.

## The promise problem

`f: {0,1}^n -> {0,1}` is promised to be either **constant** (`f(x)` is the
same for all `2^n` inputs) or **balanced** (`f(x) = 1` for exactly half the
inputs, `0` for the other half). Determine which, using as few queries to
`f` as possible.

Classically, in the worst case this needs `2^(n-1) + 1` queries: an
adversary can answer the first `2^(n-1)` queries all `0` (or all `1`) and
still be consistent with either a constant function or a balanced one — only
the `(2^(n-1)+1)`-th query can force a distinction. Deutsch-Jozsa solves it
with a **single** quantum query.

## Phase kickback

Given a bit-flip oracle `|x>|y> -> |x>|y XOR f(x)>` (implemented as a
reversible circuit — `f` itself needn't be reversible, only this larger map
is), prepare the second register in `|-> = (|0> - |1>)/sqrt(2)` before
querying:

```
|x>|-> -> |x>|(-1)^f(x) ->  =  (-1)^f(x) |x>|->
```

The oracle's effect "kicks back" onto the first register as a phase, and
the second register is left unchanged (still `|->`) — so for the rest of
the circuit it can be ignored, and the oracle acts as if it were the
*phase* oracle `|x> -> (-1)^f(x)|x>` on the `n`-qubit input register alone.
(This is the same trick Grover's algorithm's oracle uses to turn a marking
condition into a phase flip — see
[algorithms/grover/math.md](../grover/math.md) — applied here to a
completely different problem.)

## Why one query suffices

Starting from `|0>^n`, applying `H^n` gives the uniform superposition
`(1/sqrt(2^n)) * sum_x |x>`. After the phase-kicked-back oracle:
`(1/sqrt(2^n)) * sum_x (-1)^f(x) |x>`. Applying `H^n` again and computing the
amplitude of `|0>^n` in the result:

`<0^n| H^n (sum_x (-1)^f(x) |x>) / sqrt(2^n) = (1/2^n) * sum_x (-1)^f(x)`

- If `f` is **constant**, every term in the sum has the same sign, so this
  amplitude is `+-1` — measuring gives `|0>^n` (all-zeros) with certainty.
- If `f` is **balanced**, exactly half the terms are `+1` and half `-1`, so
  they cancel exactly and the amplitude of `|0>^n` is `0` — measuring
  *never* gives all-zeros, only some nonzero bitstring, with certainty.

So a single measurement of the input register, checked against all-zeros,
answers the promise problem with probability 1 on a perfect simulator —
`implementation.is_constant` needs exactly one shot, no retry loop (unlike
Shor's/Grover's inherently probabilistic algorithms).

## Contrast with Bernstein-Vazirani

[algorithms/bernstein_vazirani/](../bernstein_vazirani/) uses the *exact
same circuit* (`build_oracle_query_circuit`, shared verbatim) with a
different oracle (`f(x) = s.x mod 2` for a hidden `s`, instead of a
constant/balanced promise) to solve a different problem (recover `s`,
rather than decide constant-vs-balanced). The interesting asymmetry: Deutsch-Jozsa's
classical query complexity is *exponential* (`2^(n-1)+1`), while
Bernstein-Vazirani's is only *linear* (`n`) — so Deutsch-Jozsa demonstrates
a much larger classical-vs-quantum gap, even though the *quantum* circuit
solving both is identical.

## References

See [references.bib](references.bib). The algorithm and its analysis follow
Deutsch & Jozsa's original paper (`deutschjozsa1992`); the phase-kickback
derivation follows Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`).
