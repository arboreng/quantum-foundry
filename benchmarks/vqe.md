# VQE: Ground-State Energy Recovery and Optimization-Loop Cost

Generated via `uv run python -m algorithms.vqe.benchmark` (RFC-0009's
`TransverseFieldIsingHamiltonian`, `J=1.0`, `h=0.5`, `reps=1` and `reps=2`,
on 2- and 3-qubit open chains).

| n_qubits | reps | Found energy | Exact energy | Total time |
| -------- | ---- | ------------- | -------------- | ------------ |
| 2        | 1    | -1.382         | -1.414          | 5.17s         |
| 2        | 2    | -1.367         | -1.414          | 8.45s         |
| 3        | 1    | -2.316         | -2.403          | 13.03s        |
| 3        | 2    | -2.245         | -2.403          | 20.37s        |

## Reading this

Like QAOA's, VQE's interesting cost is the **classical optimization
loop**: `total_seconds` covers `scipy.optimize.minimize` (COBYLA)
repeatedly re-running one measurement circuit per non-identity Pauli term
(1000 shots each) while searching for good ansatz parameters, then a
final higher-shot-count pass to read off the energy. `reps=2` costs
noticeably more wall-clock time than `reps=1` at both qubit counts, since
each optimizer iteration now tunes twice as many parameters — the same
"bigger parameter space, not bigger circuit" pattern QAOA's `p=2` showed.

**Unlike QAOA's `p=2`, `reps=2` here doesn't recover a better energy than
`reps=1`** — if anything, slightly worse, and this held up across repeated
runs, not just sampling noise on one run. The likely cause: `reps=2` gives
the ansatz strictly more expressive power (it can represent a superset of
what `reps=1` can), but `solve_ground_state` uses the same fixed initial
guess (`0.5` for every angle) and the same COBYLA iteration budget
regardless of `reps` — with twice as many parameters to search and no more
optimizer budget or smarter initialization to spend on them, COBYLA
settles for a worse local optimum more often than it does in the smaller
`reps=1` space. This is exactly the "fixed initial guess, no multi-start"
simplification math.md/paper.md already flag — expressivity alone doesn't
help if the classical loop can't exploit it.

Every found energy sits *above* the exact ground energy (consistent with
the variational principle: `<psi|H|psi> >= E_0` always) and within roughly
0.03-0.16 of it for these small chains — close, but **not a general
guarantee**: nothing about VQE's construction proves `solve_ground_state`
gets this close for a larger chain or a harder Hamiltonian, only that
`reps=1` already gets reasonably close for these small textbook instances.

## Reproducing

```bash
uv run python -m algorithms.vqe.benchmark
```
