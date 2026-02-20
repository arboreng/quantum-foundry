# Grover's Algorithm — Mathematical Foundations

**Math Version 1.0.**

Level 1 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).

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

## Why `~(pi/4) * sqrt(N/M)` iterations

Maximizing `sin^2((2k+1)*theta)` means getting `(2k+1)*theta` as close to
`pi/2` as possible, i.e. `k ~ pi/(4*theta) - 1/2`. For small `M/N`,
`theta ~ sqrt(M/N)` (small-angle approximation of `sin(theta) = sqrt(M/N)`),
giving the standard `k ~ (pi/4) * sqrt(N/M)` — exactly what
`implementation._iteration_count` computes. Because `k` must be an integer,
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
- **More iterations is not always better** — see "why ~(pi/4)*sqrt(N/M)"
  above; this is a real, provable failure mode, not a simulator artifact.
