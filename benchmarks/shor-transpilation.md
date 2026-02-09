# Shor's Algorithm: Hardware-Aware Transpilation ([RFC-0003](../docs/rfcs/0003-hardware-aware-transpilation.md))

Generated via `compiler.transpilation.analyze_transpilation`: the N=15
`GateDecomposedOracle` order-finding circuit (19 qubits — see
[benchmarks/shor.md](shor.md) for how it's built), transpiled against a
hand-built linear nearest-neighbor `CouplingMap` (`compiler.targets.
linear_coupling_map`) with basis gates `{rz, sx, x, cx}`, at each Qiskit
`optimization_level`.

| Opt. level | Gate count | Circuit depth | SWAP count | Gate ratio vs. unconstrained | Depth ratio vs. unconstrained |
| ---------- | ---------- | -------------- | ----------- | ----------------------------- | ------------------------------- |
| 0          | 1,636,637  | 1,395,488      | 145,960     | 12.88x                        | 12.04x                          |
| 1          | 1,328,914  | 1,126,904      | 97,001      | 10.46x                        | 9.72x                            |
| 2          | 1,304,180  | 1,054,851      | 94,284      | 10.27x                        | 9.10x                            |
| 3          | 1,303,906  | 1,054,711      | 94,195      | 10.26x                        | 9.10x                            |

"Unconstrained" is [benchmarks/shor.md](shor.md)'s N=15 `GateDecomposedOracle`
row (127,039 gates, 115,918 depth) — the same circuit, transpiled only
against `AerSimulator`'s default (no coupling map, i.e. implicit all-to-all
connectivity).

## Reading this

Limited qubit connectivity alone — no noise, no gate-error modeling, just
"qubit 5 can only talk to qubits 4 and 6" — costs **roughly an order of
magnitude** in both gate count and circuit depth on top of RFC-0002's
already-expensive gate-decomposed oracle. Nearly all of that overhead is
`swap` insertions from Qiskit's SABRE router: at `optimization_level=0`,
145,960 swaps (each costing 3 `cx` once decomposed to the native basis) are
inserted; better optimization levels reduce this by ~35%, but even at
level 3 there are still 94,195 swaps — the modular-multiplication circuit's
`ccx`/multi-qubit interaction pattern simply doesn't fit a linear chain
without substantial rerouting.

`optimization_level=1` already captures most of the available improvement
(10.46x vs. level 0's 12.88x); levels 2 and 3 buy a further ~2% on top of
level 1, at 2x the transpile time (13-15s vs. ~7s) for this circuit — level 1
is the practical default for a circuit this size.

This is a **structural** result (connectivity/basis-gate constraints only),
verified separately for logical correctness: `algorithms/shor/tests/
test_gate_decomposed_oracle.py::test_find_order_survives_hardware_aware_transpilation`
(`@pytest.mark.slow`) confirms `find_order` still recovers the correct order
of 7 mod 15 when actually executed through this same constrained
transpilation via `execution.ConstrainedAerExecutor`, not just checked for
coupling-map compliance.

## Reproducing

```python
from algorithms.shor.circuit import build_order_finding_circuit
from algorithms.shor.oracles import GateDecomposedOracle
from compiler.targets import linear_coupling_map, BASIS_GATES
from compiler.transpilation import analyze_transpilation

circuit = build_order_finding_circuit(15, 7, oracle_cls=GateDecomposedOracle)
coupling_map = linear_coupling_map(circuit.num_qubits)
for level in range(4):
    print(analyze_transpilation(circuit, coupling_map, BASIS_GATES, level))
```
