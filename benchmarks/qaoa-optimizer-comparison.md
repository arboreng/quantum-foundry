# QAOA: Classical Optimizer Comparison

Generated via `uv run python -m algorithms.qaoa.benchmark`
(`OptimizerComparisonResult`): the same triangle MaxCut instance
(`p=1`, so 2 parameters), 5 independent trials each, comparing
`scipy.optimize.minimize`'s `COBYLA` (gradient-free — `solve_maxcut`'s
default) against `BFGS` (gradient-based, using `scipy`'s own
finite-difference gradient estimate, since no analytic gradient is
supplied to either).

| Method  | Trial | Found cost | Optimal cost | Function evaluations | Total time |
| ------- | ----- | ---------- | -------------- | ----------------------- | ------------ |
| COBYLA  | 0     | 2.0         | 2.0             | 32                       | 1.63s         |
| COBYLA  | 1     | 2.0         | 2.0             | 30                       | 1.48s         |
| COBYLA  | 2     | 2.0         | 2.0             | 27                       | 1.34s         |
| COBYLA  | 3     | 2.0         | 2.0             | 31                       | 1.51s         |
| COBYLA  | 4     | 2.0         | 2.0             | 32                       | 1.57s         |
| BFGS    | 0     | 2.0         | 2.0             | 78                       | 3.81s         |
| BFGS    | 1     | 2.0         | 2.0             | 124                      | 6.02s         |
| BFGS    | 2     | 2.0         | 2.0             | 103                      | 4.99s         |
| BFGS    | 3     | 2.0         | 2.0             | 68                       | 3.29s         |
| BFGS    | 4     | 2.0         | 2.0             | 125                      | 6.04s         |

Averages: COBYLA — 30.4 evaluations, 1.51s. BFGS — 99.6 evaluations,
4.83s.

## Reading this

**Both optimizers find the true optimum on every trial** for this easy,
2-parameter instance — neither is more *accurate* here. The real
difference is cost: **BFGS uses roughly 3.3x more function evaluations
and 3.2x more wall-clock time than COBYLA**, consistently across all 5
trials (never overlapping — even BFGS's best trial, 68 evaluations,
costs more than COBYLA's worst, 32).

This is exactly the expected cost of gradient-based optimization without
an analytic gradient: BFGS estimates each gradient step via finite
differences (perturbing each of the 2 parameters and re-evaluating the
noisy, finite-shots expectation value), so every gradient estimate alone
costs multiple extra circuit-evaluation rounds beyond what COBYLA (which
never estimates a gradient at all) needs to make comparable progress.
Since `expectation_value` is a **stochastic**, sampling-noise-laden
estimate (not a smooth analytic function), a finite-difference gradient
estimate is also less reliable than it would be for a noiseless
objective — the extra cost buys **no accuracy benefit** on this instance,
consistent with why `solve_maxcut` defaults to COBYLA (see its own
docstring) and why parameter-shift gradients (an *exact*, not
finite-difference, gradient — VQE's own stretch-goal list, not
implemented here) are the standard alternative in the literature when a
gradient-based method is actually wanted.

## Reproducing

```bash
uv run python -c "
from algorithms.qaoa.benchmark import run_optimizer_comparison
for result in run_optimizer_comparison():
    print(result)
"
```
