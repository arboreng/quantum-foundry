# Grover's Algorithm — Mathematical Foundations

**Math Version 1.0.**

Level 1 of the repository's documentation-level model.

## The unstructured search problem

Given a boolean oracle `f: {0,1}^n -> {0,1}` marking `M` out of `N = 2^n`
possible inputs (`f(x) = 1` iff `x` is marked), find a marked `x` using as
few oracle queries as possible. Classically this needs `O(N/M)` queries on
average (nothing better than checking candidates one at a time — there's no
structure to exploit). Grover's algorithm does it in `O(sqrt(N/M))` quantum
queries — a quadratic, not exponential, speedup (contrast with
[algorithms/shor/math.md](../shor/math.md)'s exponential speedup for
factoring). Quadratic is still provably optimal: the Bennett-Bernstein-Brassard-Vazirani
(BBBV) lower bound shows no quantum algorithm can solve unstructured search
in fewer than `Omega(sqrt(N/M))` queries.

## The geometric picture

Let `|s>` be the uniform superposition over all `N` basis states, and split
it into two orthogonal parts: `|s_marked>` (uniform superposition over just
the `M` marked states) and `|s_unmarked>` (uniform superposition over the
`N-M` unmarked states). Every state Grover's algorithm ever produces stays
in the 2D plane spanned by `|s_marked>` and `|s_unmarked>` — this is what
makes the analysis tractable despite the exponentially large ambient
Hilbert space.

`|s>` starts at angle `theta` from `|s_unmarked>` in this plane, where
`sin(theta) = sqrt(M/N)`. Each Grover iteration (oracle phase-flip, then the
diffusion operator's reflection about `|s>`) is a composition of two
reflections, which is a rotation — specifically, a rotation by `2*theta`
*toward* `|s_marked>`. So iterating rotates the state closer and closer to
the marked subspace, and measuring in that state gives a marked outcome with
probability `sin^2((2k+1)*theta)` after `k` iterations.

## Why `round(pi/(4*theta) - 1/2)` iterations

Maximizing `sin^2((2k+1)*theta)` means getting `(2k+1)*theta` as close to
`pi/2` as possible, i.e. `k = round(pi/(4*theta) - 1/2)` — exactly what
`implementation._iteration_count` computes. For small `M/N`, `theta ~
sqrt(M/N)` (small-angle approximation of `sin(theta) = sqrt(M/N)`), which
recovers the more commonly quoted `k ~ (pi/4) * sqrt(N/M)`.

That approximation is **only** valid in that small-`M/N` limit, and this
implementation deliberately does not use it: it drops the `-1/2` term,
which over-rotates whenever `M/N` is not small. At `n=2, M=1` it gives
`k=2` (success probability `0.25`) where the exact count gives `k=1`
(probability `1.0`); at `n=2, M=3` it gives `k=1`, whose success
probability is exactly `0` — the retry loop cannot rescue that, since
every attempt runs the same circuit. Because `k` must be an integer,
rounding introduces a small deviation from the theoretical optimum, and
**overshooting past the optimal `k` rotates the state *past* `|s_marked>`
and back toward `|s_unmarked>`** — more iterations is not always better,
unlike most classical amplification schemes. This is why `search`'s retry
loop (`implementation.py`) re-runs the *same* fixed-iteration circuit with
fresh shots on failure, rather than adding more iterations.

## Common misconceptions

- **Grover's algorithm is not a "faster classical search."** It requires the
  marking condition to be expressed as a quantum oracle (a unitary that
  phase-flips marked computational basis states); it doesn't examine a
  classical list of items the way a hash lookup or a database index does.
- **The speedup is quadratic, not exponential** — for large `N` this is
  still a real, asymptotically meaningful advantage, but it's a much smaller
  effect than Shor's algorithm's factoring speedup, and doesn't threaten
  cryptographic schemes the way Shor's does (this is why NIST's
  post-quantum-cryptography key-size recommendations mostly just double key
  lengths to compensate for Grover, rather than replacing the underlying
  hard problem the way RSA/ECC need replacing against Shor).
- **More iterations is not always better** — see "why
  `round(pi/(4*theta) - 1/2)` iterations" above; this is a real, provable
  failure mode, not a simulator artifact.

## The degenerate `n_qubits=1` case

At the smallest possible scale (`N=2`, `M=1`), `sin(theta) = sqrt(1/2)`, so
`theta = pi/4` exactly. `pi/(4*theta) - 1/2 = 1/2`, so `_iteration_count(1,
1)` rounds to `k=0`, giving success probability `sin^2(theta) =
sin^2(pi/4) = 0.5` — exactly a coin
flip, not the near-certain success Grover's algorithm typically achieves at
larger `N`. This is an inherent property of this specific tiny instance
(confirmed empirically: 10,000 shots split ~50/50), not a bug — but it does
mean `search`'s retry loop needs more attempts here than elsewhere to reach
a comparably low failure rate, which is why `max_attempts` defaults to `20`
rather than a smaller number (see `implementation.search`'s docstring).

## Quantum counting

`search` needs `M` (the number of marked items) in advance, to compute
the iteration count. `counting.count` removes that requirement: QPE
(`algorithms/qpe/`'s pattern) applied to the Grover iteration operator
`Q = diffusion_operator . oracle.phase_flip_gate()` estimates `Q`'s
eigenvalue phase, which — per the geometric picture above — encodes
`theta`, and hence `M = N * sin(theta)^2`. Unlike ordinary QPE, the input
state (`H^n_qubits`, the uniform superposition `|s>`) isn't a single
eigenstate of `Q`; it's a real combination of `Q`'s two eigenvectors (the
same 2D rotation subspace `|s_marked>`/`|s_unmarked>` spans above), so QPE
returns *one of two* symmetric estimates — both give the same `M` back
out, since `sin(pi - x) = sin(x)` (see paper.md).

**A subtlety this surfaced**: paper.md's "diffusion operator" section
already notes `diffusion_operator` implements `I - 2|s><s|`, not the
textbook `2|s><s| - I` — an unobservable global-phase difference *for
plain Grover search*, where global phase never affects measurement
probabilities. Quantum counting applies `Q` **under control** (as QPE
requires), and a controlled operation exposes global phase as a
real, relative phase — exactly the same mechanism `algorithms/hhl/
oracles.py`'s `DiagonalXOracle` deliberately *uses* (there, a chosen
global phase becomes a controlled-phase correction on purpose). Here it's
incidental: the extra `-1` flips `Q`'s eigenvalues from `e^(+-2i*theta)`
to `-e^(+-2i*theta)`, so the measured phase estimates `0.5 +- theta/pi`
rather than `+-theta/pi` directly. `counting.count` corrects for this
(`theta = pi * abs(y/2**n_count - 0.5)`); confirmed empirically against
both the exact eigenvalues (`np.linalg.eigvals`) and the full statevector
in `tests/test_counting.py`, the same "validate the actual construction,
don't just trust the textbook formula" discipline this repo has followed
since RFC-0001's QFT bit-ordering. `diffusion_operator` itself is left
unchanged — it's correct for the purpose it already serves.

## References

See [references.bib](references.bib). The algorithm and its analysis follow
Grover's original paper (`grover1996`); the geometric/rotation picture and
the BBBV optimality argument follow Nielsen & Chuang's textbook treatment
(`nielsenchuang2010`). Brassard-Høyer-Mosca (`brassard2000`)'s amplitude
amplification generalizes Grover's algorithm to arbitrary initial-state
rotations and to unknown-`M` search (quantum counting, now implemented in
`counting.py`, beyond v0.8 — see "Quantum counting" above).
