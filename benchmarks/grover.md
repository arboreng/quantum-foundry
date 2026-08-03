# Grover's Algorithm: Scaling

Generated via `uv run python -m algorithms.grover.benchmark` (RFC-0004's
`MarkedBitstringOracle`, single marked item, transpiled against
`AerSimulator`'s default basis gates).

| n_qubits | Search space (2^n) | Iterations | Gate count | Circuit depth | Simulation time |
| -------- | -------------------- | ------------ | ---------- | -------------- | ---------------- |
| 3        | 8                     | 2            | 22         | 10             | 0.09s             |
| 4        | 16                    | 3            | 38         | 14             | 0.09s             |
| 6        | 64                    | 6            | 96         | 26             | 0.09s             |
| 8        | 256                   | 12           | 232        | 50             | 0.10s             |
| 10       | 1024                  | 25           | 570        | 102            | 0.11s             |

## Reading this

Iteration count grows as `~sqrt(2^n)`, exactly as math.md predicts (doubling
`n_qubits` from 4 to 8 quadruples the search space's square root, and the
measured iteration count goes 3 → 12 — exactly the theoretical `4x`). Gate count and circuit depth grow correspondingly, but stay small in
absolute terms even at `n=10` (1024-item search space) — 570 gates, depth
102 — nowhere near the scale of
[Shor's algorithm's circuits](shor.md) (which need 12-23+ qubits and
thousands to hundreds of thousands of gates even at `N=15`). This is the
concrete shape of Grover's *quadratic* speedup vs. Shor's *exponential*
one (math.md): Grover's circuits stay cheap to simulate classically across
a much wider practical range, which is exactly why a quantum computer's
advantage here is smaller (and further away from threatening classical
computation) than Shor's is for factoring.

Simulation time is dominated by fixed per-shot overhead at this scale (100
shots, ~0.09-0.11s total across all five rows) — the circuits themselves are
far too small for circuit size to be the bottleneck yet.

Only a single marked item and one oracle implementation
(`MarkedBitstringOracle`) are benchmarked here — there's no gate-decomposed
alternative yet (RFC-0004's non-goals defer that, mirroring
[RFC-0002](../docs/rfcs/0002-gate-decomposed-arithmetic.md)'s relationship
to Shor's RFC-0001), so there's nothing to compare against yet the way
[benchmarks/shor.md](shor.md) compares two oracles.

## Reproducing

```bash
uv run python -m algorithms.grover.benchmark
```
