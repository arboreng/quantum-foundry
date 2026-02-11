# compiler/

Circuit optimization and transpilation passes shared across algorithms.

- [math.md](math.md) — the qubit-mapping problem, SABRE routing, basis
  translation, what optimization levels trade off
- [paper.md](paper.md) — derivation of `analyze_transpilation`'s two-pass
  swap-counting trick and `ConstrainedAerExecutor`'s integration
- [targets.py](targets.py) — a hand-built, transparent hardware model:
  `linear_coupling_map` (linear nearest-neighbor connectivity) and
  `BASIS_GATES` (`rz`, `sx`, `x`, `cx` — a standard superconducting-qubit gate
  set). Not a full `qiskit.transpiler.Target` (no duration/error
  calibration — this is about connectivity/basis constraints, not noise) and
  not `qiskit-ibm-runtime`'s fake backends (no new dependency, fully
  inspectable).
- [transpilation.py](transpilation.py) — `analyze_transpilation`, reporting
  qubit count, gate count, circuit depth, and SWAP-gate count (routing
  overhead) for a circuit transpiled against a given coupling map and
  optimization level.
- [tests/](tests/) — coupling-map-compliance and report-sanity tests.

Used by `algorithms.shor.execution.ConstrainedAerExecutor`
([RFC-0003](../docs/rfcs/0003-hardware-aware-transpilation.md)) to actually
execute circuits under this hardware model, not just analyze them
structurally. See [benchmarks/shor-transpilation.md](../benchmarks/shor-transpilation.md)
for the resulting routing-overhead study.
