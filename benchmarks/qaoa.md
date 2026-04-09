# QAOA: Optimal-Cut Recovery and Optimization-Loop Cost

Generated via `uv run python -m algorithms.qaoa.benchmark` (RFC-0008's
`MaxCutProblem`, `p=1` and `p=2` layers, on a triangle and a 4-cycle).

| Graph    | n_qubits | Edges | p | Found cost | Optimal cost | Total time |
| -------- | -------- | ----- | - | ------------ | -------------- | ------------ |
| Triangle | 3        | 3     | 1 | 2.0          | 2.0            | 1.75s         |
| Triangle | 3        | 3     | 2 | 2.0          | 2.0            | 2.07s         |
| 4-cycle  | 4        | 4     | 1 | 4.0          | 4.0            | 1.58s         |
| 4-cycle  | 4        | 4     | 2 | 4.0          | 4.0            | 2.15s         |

## Reading this

Unlike every other benchmark in this repo (which tracks a single circuit's
gate count/depth/simulation time), QAOA's interesting cost is the
**classical optimization loop**: `total_seconds` here covers `scipy.optimize.minimize`
(COBYLA) repeatedly re-running the circuit (1000 shots each call) while
searching for good `(gammas, betas)`, then one final higher-shot-count run
to read off the answer. `p=2` (twice as many parameters to optimize) costs
noticeably more wall-clock time than `p=1` for both graphs — the
optimizer needs more function evaluations to search a larger parameter
space, not because any individual circuit got bigger.

Both graphs' true optimum (brute-forced classically: 2 cut edges out of 3
for the triangle, all 4 edges for the bipartite 4-cycle) was found in every
run at both `p` values. **This is not a general guarantee** — see math.md's
"a different guarantee shape": nothing about QAOA's construction proves
`solve_maxcut` finds the optimal cut for a larger or harder graph, only that
`p=1` already suffices for these small textbook instances.

## Reproducing

```bash
uv run python -m algorithms.qaoa.benchmark
```
