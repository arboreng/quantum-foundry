# Quantum Phase Estimation — Mathematical Foundations

**Math Version 1.0.**

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

## The phase estimation problem

Given a unitary `U` and an eigenstate `|psi>` with `U|psi> = e^(2*pi*i*theta)|psi>`
for some real `theta` in `[0, 1)`, estimate `theta`. Unlike
[algorithms/shor/math.md](../shor/math.md)'s order-finding (where the
phase is known in advance to be rational, `s/r` for integer `r < N`), `theta`
here is a general real number — QPE doesn't assume any special structure.

## Why the circuit works

`n_count` counting qubits, each `H`'d into superposition, control successive
powers `U^(2^k)` applied to `|psi>`. Since `|psi>` is an eigenstate, each
controlled-`U^(2^k)` leaves `|psi>` unchanged and instead deposits a phase
`e^(2*pi*i*theta*2^k)` onto the `k`-th counting qubit's `|1>` branch (phase
kickback — the same mechanism
[algorithms/deutsch_jozsa/math.md](../deutsch_jozsa/math.md) uses, here with
a genuine eigenstate rather than the `|->` ancilla trick). After all
`n_count` controlled operations, the counting register holds

`(1/sqrt(2^n_count)) * sum_k e^(2*pi*i*theta*k) |k>`

— exactly the state the (inverse) QFT is built to concentrate: applying
`inverse_qft` peaks the amplitude near the computational basis state
`round(theta * 2^n_count)`, so measuring the counting register gives (with
high probability) the `n_count`-bit binary expansion of `theta`.

## Precision

If `theta`'s binary expansion terminates exactly within `n_count` bits (e.g.
`theta = 0.25` with `n_count >= 2`), measurement gives the exact answer with
certainty — confirmed empirically in `tests/test_qpe.py` and in the demo
notebook. Otherwise, the estimate is accurate to within `1/2^n_count` with
probability at least `4/pi^2 ≈ 0.405` (Nielsen & Chuang, Section 5.2) — and
this probability can be boosted arbitrarily close to 1 by adding a modest
number of extra counting qubits beyond the target precision (each extra
qubit roughly doubles the "in-tolerance" probability's complement). This
implementation does not add such margin qubits automatically; `n_count` is
exactly the precision `estimate_phase`'s caller requests.

**Confidence, empirically**: [benchmarks/qpe-precision-confidence.md](../../benchmarks/qpe-precision-confidence.md)
runs 300 independent trials at each of `extra_qubits = 0, 1, 2, 3, 4`
beyond a fixed target precision, for `theta = 0.1`. The `4/pi^2` bound
holds comfortably (a *guaranteed minimum*, not a typical value — the
empirical `extra_qubits=0` success rate, `0.883`, sits well above it,
since `0.1`'s particular binary expansion happens to round favorably)
and the failure probability roughly halves per extra qubit as claimed
(`0.117 -> 0.053 -> 0.027 -> 0.017 -> 0.007`) — though the ratios get
noisier at the tail, where only a handful of failures out of 300 trials
means the failure *count itself* carries substantial sampling error (see
that benchmark's "Reading this" for the honest caveat).

## Connection to Shor's order-finding

`algorithms/shor/oracles.py`'s `Oracle` protocol
(`controlled_power_gate(power) -> Gate`) is structurally identical to this
module's `Oracle` protocol — both supply controlled powers of a unitary.
The difference is the "eigenstate": Shor's `build_order_finding_circuit`
initializes the work register to the classical state `|1>`, which is *not*
a single eigenstate of the modular-multiplication unitary but a uniform
superposition over several of its eigenstates (one per eigenvalue
`e^(2*pi*i*s/r)` for `s = 0, ..., r-1`). Measuring the counting register
then yields a phase estimate for a *uniformly random one* of those
eigenvalues rather than a single fixed `theta` — which is exactly why
Shor's algorithm needs the continued-fraction step and a retry loop
(`algorithms/shor/implementation.py::factor`), while this module's
`estimate_phase` (given a true, single eigenstate) does not.

## Semiclassical (Kitaev iterative) phase estimation

`semiclassical.estimate_phase_semiclassical` estimates the same `theta`
using a single ancilla reused `n_count` times instead of `n_count`
ancillas plus a coherent inverse QFT (Kitaev's original formulation,
generalized by Griffiths-Niu's semiclassical QFT trick). Round `j`
applies `H`, controlled-`U^(2**(n_count-1-j))`, a classical phase
correction, `H`, then measures the ancilla and moves on.

Deriving *which* bit each round measures, and the correction formula,
directly from the eigenvalue equation: `U^power|psi> = e^(2*pi*i*theta*
power)|psi>`, so a bare `H`-`CU^power`-`H` round (no correction) measures
the ancilla as `1` with probability `sin^2(pi*theta*power)`. For `theta =
0.theta_1 theta_2 ... theta_n` (`theta_1` the most significant bit) and
`power = 2^(n-1)` (round `0`, the *largest* power), `theta*power mod 1 =
theta_n / 2` — i.e. round `0` measures `theta_n`, the **least**
significant bit, not the most significant one. Each subsequent round
`j` (using power `2^(n-1-j)`) picks up contributions from all
previously-measured (less significant) bits that need to be classically
cancelled before that round's bit can be read off cleanly — the
`-pi * sum(bit / 2**(j - j_prime) ...)` correction in `semiclassical.py`.
The final estimate reassembles `theta` from all `n_count` measured bits,
each weighted by `2**(j - n_count)` for the round `j` it came from
(round `0`, the least significant bit, gets the smallest weight;
the last round, the most significant bit, gets weight `1/2`).

**Getting this backwards is an easy mistake to make** — an earlier
attempt derived the round order and bit significance by tracing
`arithmetic.qft.inverse_qft`'s own gate-by-gate structure (its leading
qubit-reversing swap, then per-target `H`/controlled-phase), concluded
(incorrectly) that round `0` measures the *most* significant bit, and
that version passed for `theta=0.25, n_count=3` — but only by luck: at
`n_count=3`, this specific instance happens to make the correct and
incorrect reconstructions coincide for that one case, but the bug shows
up immediately at other `(theta, n_count)` pairs. Caught by cross-
validating against `implementation.estimate_phase` directly on all of
`tests/test_qpe.py`'s exact instances, not by trusting either derivation
in isolation — the same discipline this repo has followed since RFC-0001's
QFT bit-ordering question, applied here to catch a mistake in *this*
repo's own reasoning about its own established code, not just to confirm
an external convention.

## Known limitations (v0.2)

This implementation assumes `eigenstate_prep` exactly prepares an
eigenstate of `oracle`'s unitary. If it only approximately does (or
prepares a superposition of multiple eigenstates, as Shor's construction
deliberately does), the measured phase is a probabilistic mixture over the
component eigenphases weighted by their amplitudes — not addressed here;
see `PhaseGateOracle`'s single, exactly-known eigenstate `|1>` for what
this implementation actually guarantees.

## References

See [references.bib](references.bib). The algorithm follows Kitaev's
original paper (`kitaev1995`); the precision analysis follows Nielsen &
Chuang's textbook treatment (`nielsenchuang2010`), Section 5.2. The
semiclassical/iterative variant follows Griffiths-Niu's semiclassical
Fourier transform (`griffithsniu1996`), combined with Kitaev's original
iterative phase estimation (`kitaev1995`).
