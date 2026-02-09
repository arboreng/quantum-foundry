# Shor's Algorithm: Oracle Comparison

Generated via `uv run python -m algorithms.shor.benchmark` (RFC-0001's
`PermutationMatrixOracle` vs. RFC-0002's `GateDecomposedOracle`), one
order-finding circuit per row (smallest coprime base `a`, `n_count = 2 *
N.bit_length()`), transpiled against `AerSimulator`'s default basis gates.

| N  | Oracle                | Qubits | Gate count | Circuit depth | Simulation time |
| -- | ---------------------- | ------ | ---------- | -------------- | ---------------- |
| 15 | PermutationMatrixOracle | 12     | 1,284      | 913            | 0.21s             |
| 15 | GateDecomposedOracle    | 19     | 127,039    | 115,918        | 41.7s             |
| 21 | PermutationMatrixOracle | 15     | 26,305     | 19,690         | 5.0s              |
| 21 | GateDecomposedOracle    | 23     | 290,728    | 266,866        | 640.0s (10.7min)  |

## Reading this

`PermutationMatrixOracle` computes the modular-multiplication permutation
matrix classically and embeds it as a single dense `UnitaryGate` — cheap to
construct and simulate, but not something that runs on real hardware.
`GateDecomposedOracle` builds the same operation from actual elementary
reversible-arithmetic gates (Draper adder → Beauregard modular adder →
controlled modular multiplication), which is what a real device would need
to execute — at the cost of roughly **two orders of magnitude more gates and
circuit depth**, and correspondingly slower classical simulation, even at the
same small `N`.

Both qubit count and gate count grow with `N`: `PermutationMatrixOracle`'s
gate count already grows quickly (1,284 → 26,305 gates from N=15 to N=21)
because `UnitaryGate.control()` synthesis cost scales with the register size;
`GateDecomposedOracle`'s cost grows faster still, since each of its
`O(n_work)` per-bit modular additions is itself an `O(n_work)`-qubit QFT-based
circuit — see [algorithms/shor/paper.md](../algorithms/shor/paper.md) for the
construction.

Simulating `GateDecomposedOracle` at N=21 takes **~10.7 minutes per circuit**
(measured above; corroborated during RFC-0002 development — see
`algorithms/shor/tests/test_gate_decomposed_oracle.py`'s `@pytest.mark.slow`
test) — 128x slower than `PermutationMatrixOracle` at the same N. That ratio
is actually *smaller* than at N=15 (199x): `PermutationMatrixOracle`'s own
cost isn't free either — `UnitaryGate.control()` synthesis of a dense
2^n_work-dimensional matrix scales steeply with N (its gate count already
grows ~20x from N=15 to N=21), it's just starting from a much smaller base.
Either way, both are firmly in "why this isn't the default oracle for
`factor()`, and why routine tests only cover the gate-decomposed one at
N=15" territory.

## Reproducing

```bash
uv run python -m algorithms.shor.benchmark          # N=15, both oracles (~45s)
```

```python
from algorithms.shor.benchmark import _benchmark_single
from algorithms.shor.execution import AerExecutor
from algorithms.shor.oracles import GateDecomposedOracle

# N=21 with the gate-decomposed oracle: budget ~10 minutes.
print(_benchmark_single(21, AerExecutor(), GateDecomposedOracle))
```

See [shor-transpilation.md](shor-transpilation.md) for what happens when
`GateDecomposedOracle`'s circuit is additionally transpiled against a
connectivity-constrained hardware model ([RFC-0003](../docs/rfcs/0003-hardware-aware-transpilation.md))
— roughly another order of magnitude in gate count and depth, on top of
these numbers.
