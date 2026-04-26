# HHL: Clock-Register Precision vs. Gate Count and Success Probability

Generated via `uv run python -m algorithms.hhl.benchmark` (RFC-0010's
`DiagonalXOracle` demo instance, `A = I + (1/3)X`, `t = 3*pi/8` fixed
across all runs).

| n_clock | c_constant | Gate count | Circuit depth | Success probability | Total time |
| ------- | ---------- | ---------- | -------------- | --------------------- | ------------ |
| 3       | 0.600      | 130        | 110             | 0.483                  | 0.07s         |
| 4       | 0.300      | 697        | 506             | 0.120                  | 0.08s         |
| 5       | 0.150      | 2443       | 1529            | 0.034                  | 0.14s         |
| 6       | 0.075      | 6715       | 4079            | 0.006                  | 0.29s         |

## Reading this

`A` and `t` are held fixed across every row — only `n_clock` changes —
isolating the multiplexed rotation's cost from any change in the
underlying problem. Gate count and circuit depth both grow faster than a
straight doubling per added clock qubit (roughly 2.7x-5.4x here): the
multiplexed rotation adds one `n_clock`-controlled `RY` branch per
nonzero clock value (`2**n_clock - 1` branches total, so the branch count
alone roughly doubles per qubit), and each branch's multi-controlled `RY`
also costs more to decompose into elementary gates with one more control
qubit — the two effects compound.

**`c_constant` can't be held fixed either.** The smallest nonzero clock
value (`k=1`) corresponds to eigenvalue `lambda_min = 2*pi / (t *
2**n_clock)` — with the same `t`, more clock qubits means a *smaller*
`lambda_min`, so `c_constant` (which must stay under every reachable
`lambda_k` for the multiplexed rotation's `arcsin` to stay in domain) has
to shrink in lockstep — here, exactly halving every time `n_clock`
increases by 1, since `lambda_min` halves.

That shrinking `c_constant` is not free: success probability depends on
`(c_constant / lambda)^2` (see math.md), so halving `c_constant` quarters
the success probability at fixed `lambda` — which is exactly what the
table shows (`0.483 -> 0.12 -> 0.034 -> 0.006`, each roughly a quarter of
the last). **More precision costs more circuit *and* makes a successful
(ancilla-`1`) shot rarer** — a real tradeoff inherent to this
construction, not a quirk of this particular demo instance: adding clock
qubits without also adjusting `t` (to keep `lambda_min` from shrinking)
always pushes `c_constant` down and success probability down with it.
This is exactly the gap [amplitude amplification](../docs/rfcs/0010-hhl.md#stretch-goals)
(a stretch goal, not implemented here) exists to close.

## Reproducing

```bash
uv run python -m algorithms.hhl.benchmark
```
