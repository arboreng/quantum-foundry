# Quantum Phase Estimation: Precision vs. Counting Qubits

Generated via `uv run python -m algorithms.qpe.benchmark`
(`PhaseGateOracle(theta=0.1)` — chosen because `0.1` has no exact finite
binary expansion, so estimation error is always nonzero and meaningful to
track).

| n_count | Estimated theta | Error       | Gate count | Circuit depth | `estimate_phase` time |
| ------- | ------------------ | ------------ | ---------- | -------------- | ------------------------ |
| 3       | 0.125               | 0.025         | 16         | 11              | 0.05s                     |
| 5       | 0.09375             | 0.00625       | 31         | 22              | 0.05s                     |
| 8       | 0.1015625           | 0.00156       | 61         | 46              | 0.05s                     |
| 10      | 0.099609375         | 0.00039       | 86         | 67              | 0.05s                     |
| 12      | 0.099853515625      | 0.000146      | 115        | 92              | 0.06s                     |

## Reading this

Error shrinks roughly by half each time `n_count` increases by 1 (0.025 →
0.00625 → 0.0016 → ... ), tracking math.md's `1/2^n_count` bound closely in
this run. **This is not guaranteed on every run** — `estimate_phase`'s
default is a single shot, and math.md's precision guarantee is
probabilistic (at least `4/pi^2 ≈ 0.405` per attempt for a non-terminating
`theta`), so an individual run can occasionally land further from `theta`
at a higher `n_count` than a lower one did. This was observed directly
during development (see `tests/test_qpe.py`'s retry-based test for the
non-terminating case, which exists specifically because a single attempt
isn't reliable enough to assert on directly) — it's the expected behavior
math.md describes, not a bug.

Gate count and circuit depth both grow **roughly quadratically** in
`n_count` (the ratio `gate_count / n_count^2` decreases from ~1.78 at
`n_count=3` to ~0.80 at `n_count=12`, consistent with settling toward a
fixed quadratic coefficient rather than linear or cubic growth) — expected,
since the inverse QFT contributes `n_count*(n_count-1)/2` controlled-phase
rotations on top of the `n_count` controlled-oracle applications. Even so,
this stays far cheaper than [Shor's order-finding circuit](shor.md) at
comparable qubit counts (QPE here uses only `n_count + 1` qubits total, vs.
Shor's `n_count + n_work` or more, and no oracle nearly as expensive as
modular exponentiation).

## Reproducing

```bash
uv run python -m algorithms.qpe.benchmark
```
