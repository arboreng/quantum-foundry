# Hardware-Aware Transpilation — Derivation

Level 2 of the repository's documentation-level model.
Builds on [math.md](math.md) (Math Version 1.0). Describes the exact
mechanics in [targets.py](targets.py) and [transpilation.py](transpilation.py).

## `targets.py`

`linear_coupling_map(num_qubits)` is `CouplingMap.from_line(num_qubits)` —
Qiskit's built-in helper for the edge list `{(0,1), (1,0), (1,2), (2,1),
...}` (bidirectional, since either qubit in an adjacent pair can be the
control of a `cx`). `BASIS_GATES = ["rz", "sx", "x", "cx"]` is a fixed
module-level constant, not parameterized — this RFC studies one basis gate
set, not basis-set selection.

## `analyze_transpilation`: the swap-counting trick

The naive approach — `transpile(circuit, coupling_map=..., basis_gates=BASIS_GATES)`,
then `result.count_ops().get("swap", 0)` — silently returns `0` even when
routing inserted many swaps, because `swap` isn't in `BASIS_GATES` and basis
translation decomposes it into 3 `cx` gates as part of the same `transpile()`
call. This was verified empirically (not just reasoned about) while building
this module:

```python
# same circuit, same coupling map, different basis_gates argument:
transpile(circuit, coupling_map=cm, basis_gates=["rz","sx","x","cx"])            # swap -> 0
transpile(circuit, coupling_map=cm, basis_gates=["rz","sx","x","cx","swap"])     # swap -> real count
```

`analyze_transpilation` therefore runs `transpile()` **twice**:

1. `basis_gates=[*basis_gates, "swap"]` — routing runs exactly as it would
   otherwise, but `swap` is preserved as a distinct, countable gate rather
   than being decomposed. `swap_count = routed.count_ops().get("swap", 0)`.
2. `transpile(routed, basis_gates=basis_gates, optimization_level=0)` — a
   **second, layout-preserving** pass (no `coupling_map` this time — routing
   already happened in step 1, so there's nothing left to route) that
   decomposes the remaining `swap` gates into the real basis. `gate_count`
   and `circuit_depth` are read off *this* circuit, since it's the one that
   reflects what a real device would actually execute.

`optimization_level=0` for the second pass specifically (regardless of the
caller's requested level) because its only job is basis translation of
already-final gates — re-running heavier optimization here would conflate
"how good was the routing at this optimization level" with "how good is
basis translation," muddying the very comparison this module exists to make.

## `ConstrainedAerExecutor`

`algorithms/shor/execution.py`'s `ConstrainedAerExecutor.run` is a single
`transpile()` call (routing, basis translation, and `swap`-decomposition all
in one pass, unlike `analyze_transpilation`'s two — there's no need to count
swaps separately when the goal is just "run this correctly") followed by
`AerSimulator.run()` on the result. Because it satisfies the same `Executor`
protocol as RFC-0001's `AerExecutor`, `find_order`/`factor` need no changes
at all to use it — passing `executor=ConstrainedAerExecutor(...)` is the
entire integration.

## Cost accounting

For the N=15 `GateDecomposedOracle` order-finding circuit (19 qubits,
127,039 gates / 115,918 depth unconstrained — see
[benchmarks/shor.md](../benchmarks/shor.md)), routing onto
`linear_coupling_map(19)` costs 10.3-12.9x more gates and 9.1-12.0x more
depth depending on `optimization_level` (0-3), with 94,195-145,960 `swap`
gates inserted — see
[benchmarks/shor-transpilation.md](../benchmarks/shor-transpilation.md) for
the full table and how each optimization level trades off transpile time
against output quality.

## Known simplifications

- One coupling-map topology (linear) — the most constrained, chosen to make
  routing overhead maximally visible, not necessarily representative of any
  specific real device's topology (e.g. IBM's heavy-hex).
- No custom transpiler passes — only Qiskit's built-in routing
  (SABRE) and optimization passes at each `optimization_level`.
- No noise or error-rate modeling (see math.md's "Common misconceptions").
- `PermutationMatrixOracle` out of scope, per RFC-0003's non-goals.
