# benchmarks/

Cross-algorithm benchmark harness and aggregated results. Each algorithm owns
its own `benchmark.py` (e.g. [algorithms/shor/benchmark.py](../algorithms/shor/benchmark.py));
this directory is for comparing results across algorithms and tracking
regressions over time.

- [shor.md](shor.md) — qubit count, gate count, circuit depth, and simulation
  time comparing RFC-0001's `PermutationMatrixOracle` against RFC-0002's
  `GateDecomposedOracle` at N=15/21.

No cross-algorithm comparisons yet (only one algorithm implemented so far).
