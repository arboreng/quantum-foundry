# Simon's Algorithm: Oracle Comparison and Scaling

Generated via `uv run python -m algorithms.simon.benchmark` and direct
calls to `_benchmark_single` (RFC-0006's `LinearOracle` vs.
`PermutationOracle`, all-ones hidden period `s`).

| n_qubits | Oracle | Gate count | Circuit depth | `find_hidden_period` time |
| -------- | -------------------- | ---------- | -------------- | --------------------------- |
| 3        | `LinearOracle`        | 13         | 6              | 0.09s                        |
| 4        | `LinearOracle`        | 18         | 7              | 0.14s                        |
| 6        | `LinearOracle`        | 28         | 9              | 0.28s                        |
| 8        | `LinearOracle`        | 38         | 11             | 0.37s                        |
| 10       | `LinearOracle`        | 48         | 13             | 0.60s                        |
| 2        | `PermutationOracle`   | 10         | 6              | 0.18s                        |
| 3        | `PermutationOracle`   | 26         | 16             | 0.14s                        |
| 4        | `PermutationOracle`   | 60         | 40             | 0.28s                        |
| 6        | `PermutationOracle`   | 296        | 224            | 0.31s                        |

## Reading this

`LinearOracle`'s gate count grows **linearly** in `n_qubits` (13 → 48 gates
from `n=3` to `n=10`, roughly `5*n - 2`) — expected, since its `O(n^2)`
worst-case bound is dominated in practice by the number of set bits across
all matrix rows, which for a fixed-density `s` grows closer to linearly.
`PermutationOracle`'s gate count grows **exponentially** (10 → 296 gates
from `n=2` to `n=6`, roughly doubling-plus per qubit) — its explicit
per-pair lookup construction needs `O(2^n * n)` gates by design (see
paper.md), the same tradeoff
[benchmarks/shor.md](shor.md)'s `PermutationMatrixOracle` and
[benchmarks/deutsch-jozsa-bernstein-vazirani.md](deutsch-jozsa-bernstein-vazirani.md)'s
`BalancedOracle` make.

`find_hidden_period`'s time grows with `n_qubits` for `LinearOracle` (0.09s
to 0.60s from `n=3` to `n=10`) because it's not a single circuit execution
— it's a *loop*, running the circuit repeatedly (1 shot each) until
`n_qubits - 1` independent GF(2) equations are collected, so total time
scales with both the number of repetitions needed (`O(n)`) and each
individual run's cost.

This is the first benchmark in this repo where **the classical
post-processing genuinely competes with circuit execution for wall-clock
time** — unlike Shor's continued-fraction extraction or
Deutsch-Jozsa/Bernstein-Vazirani's direct bitstring reads (both
microseconds), Simon's GF(2) Gaussian elimination and the repeated-run
collection loop are a non-trivial fraction of `total_seconds`, because
recovering `s` fundamentally requires multiple oracle queries, not one.

## Reproducing

```bash
uv run python -m algorithms.simon.benchmark   # LinearOracle, n=3..10
```

```python
from algorithms.simon.benchmark import _benchmark_single
from algorithms.simon.execution import AerExecutor
from algorithms.simon.oracles import PermutationOracle

executor = AerExecutor()
for n in [2, 3, 4, 6]:
    print(_benchmark_single(n, PermutationOracle("1" * n), executor))
```
