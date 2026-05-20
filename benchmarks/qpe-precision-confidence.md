# QPE: Precision/Confidence Analysis

Generated via `uv run python -m algorithms.qpe.benchmark`
(`PrecisionConfidenceResult`, `PhaseGateOracle(theta=0.1)` — same
non-terminating instance [qpe.md](qpe.md) uses). Fixes a target precision
`n_target=4` (tolerance `1/2**4 = 0.0625`) and adds `extra_qubits` (0-4)
of counting-register precision beyond it, running 300 independent trials
of `estimate_phase` at each level to measure the empirical probability of
landing within that fixed tolerance.

| Extra qubits | n_count | Trials | Successes | Empirical success probability | Empirical failure probability |
| ------------- | ------- | ------ | ---------- | -------------------------------- | -------------------------------- |
| 0             | 4       | 300    | 265        | 0.883                             | 0.117                             |
| 1             | 5       | 300    | 284        | 0.947                             | 0.053                             |
| 2             | 6       | 300    | 292        | 0.973                             | 0.027                             |
| 3             | 7       | 300    | 295        | 0.983                             | 0.017                             |
| 4             | 8       | 300    | 298        | 0.993                             | 0.007                             |

## Reading this

**The theoretical lower bound holds, comfortably**: math.md cites `4/pi^2
~ 0.405` as the *guaranteed minimum* success probability with zero extra
qubits (Nielsen & Chuang, Section 5.2). The empirical value here
(`0.883`) is well above it — expected, since `4/pi^2` is a *worst-case*
guarantee over all possible `theta`, not a typical value; `theta=0.1`'s
specific binary expansion happens to land favorably relative to the
`n_target`-bit rounding boundary. A bound being loose for a particular
instance doesn't make it wrong — it's a guarantee, not a prediction.

**Failure probability roughly halves per extra qubit**, matching
math.md's qualitative claim: `0.117 -> 0.053 -> 0.027 -> 0.017 -> 0.007`,
ratios `0.46, 0.50, 0.63, 0.40` between consecutive levels. These ratios
bounce around `0.5` rather than sitting exactly on it — expected, since
at `extra_qubits=3` and `4` there are only `5` and `2` failures out of
`300` trials respectively, so the *sampling noise on the failure count
itself* is a large fraction of the count. This is a real limitation of
this specific run, not a sign the halving claim is wrong: with a
binomial standard error of `sqrt(p(1-p)/n)`, the `extra_qubits=4` row's
`0.007` failure rate carries roughly `±0.005` of 95%-CI noise from `300`
trials alone — resolving the tail more precisely would need substantially
more trials there specifically (the failure event gets rarer exactly
where more trials are needed to pin it down, the usual tension in
estimating small probabilities empirically).

## Reproducing

```bash
uv run python -c "
from algorithms.qpe.benchmark import run_precision_confidence_analysis
for result in run_precision_confidence_analysis():
    print(result)
"
```
