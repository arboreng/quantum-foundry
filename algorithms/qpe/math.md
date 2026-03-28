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
Chuang's textbook treatment (`nielsenchuang2010`), Section 5.2.
