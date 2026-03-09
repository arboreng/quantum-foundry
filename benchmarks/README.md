# benchmarks/

Cross-algorithm benchmark harness and aggregated results. Each algorithm owns
its own `benchmark.py` (e.g. [algorithms/shor/benchmark.py](../algorithms/shor/benchmark.py));
this directory is for comparing results across algorithms and tracking
regressions over time.

- [shor.md](shor.md) — qubit count, gate count, circuit depth, and simulation
  time comparing RFC-0001's `PermutationMatrixOracle` against RFC-0002's
  `GateDecomposedOracle` at N=15/21.
- [shor-transpilation.md](shor-transpilation.md) — gate count/depth/SWAP-count
  overhead RFC-0003's connectivity-constrained transpilation adds on top of
  RFC-0002's `GateDecomposedOracle`, across Qiskit optimization levels 0-3.
- [grover.md](grover.md) — iteration count, gate count, circuit depth, and
  simulation time for RFC-0004's `MarkedBitstringOracle` as the search space
  grows from `n_qubits=3` to `10`.
- [deutsch-jozsa-bernstein-vazirani.md](deutsch-jozsa-bernstein-vazirani.md) —
  gate count, circuit depth, and simulation time for RFC-0005's two
  algorithms, both scaling linearly in `n_qubits` — the cheapest growth rate
  of any algorithm here.

No cross-algorithm comparisons yet (four algorithms implemented, but at very
different scales — see [grover.md](grover.md)'s comparison to
[shor.md](shor.md), and [deutsch-jozsa-bernstein-vazirani.md](deutsch-jozsa-bernstein-vazirani.md)'s
comparison to both, for why a direct table wouldn't be very meaningful yet).
