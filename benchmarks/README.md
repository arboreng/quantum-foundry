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
- [simon.md](simon.md) — gate count and `find_hidden_period` time for
  RFC-0006's `LinearOracle` (linear growth) vs. `PermutationOracle`
  (exponential growth), and the first algorithm here where classical
  post-processing genuinely competes with circuit execution for wall-clock
  time.
- [qpe.md](qpe.md) — estimation error vs. counting-qubit count for
  RFC-0007's `PhaseGateOracle`, the only benchmark here whose interesting
  axis is precision rather than search-space/oracle size.
- [qpe-precision-confidence.md](qpe-precision-confidence.md) — empirical
  success probability (over 300 trials per level) of landing within a
  fixed target precision, as extra counting qubits are added beyond it —
  confirms math.md's "failure probability roughly halves per extra
  qubit" claim, with an honest look at the sampling noise on that claim's
  own tail.
- [qaoa.md](qaoa.md) — optimal-cut recovery and classical-optimization-loop
  wall-clock cost for RFC-0008's `MaxCutProblem`, the only benchmark here
  measuring a hybrid classical-quantum loop rather than a single circuit.
- [qaoa-optimizer-comparison.md](qaoa-optimizer-comparison.md) — COBYLA
  (gradient-free) vs. BFGS (gradient-based, finite-difference) on the
  same MaxCut instance: both reach the optimum every trial, but BFGS
  costs ~3.3x more circuit evaluations for no accuracy benefit, since
  finite-difference gradients are expensive and unreliable against a
  stochastic, sampling-noise-laden objective.
- [vqe.md](vqe.md) — ground-state energy recovery and classical-
  optimization-loop wall-clock cost for RFC-0009's
  `TransverseFieldIsingHamiltonian`, including the counterintuitive
  finding that a more expressive ansatz (`reps=2`) doesn't recover a
  better energy than `reps=1` here, since the classical loop's fixed
  initial guess and iteration budget don't scale with the parameter count.
- [hhl.md](hhl.md) — clock-register precision (`n_clock`) vs. gate count
  and postselected success probability for RFC-0010's `DiagonalXOracle`,
  showing that more precision costs more circuit *and* makes a successful
  shot rarer, since the multiplexed rotation's safety margin must shrink
  as `n_clock` grows.

No cross-algorithm *simulation-cost* comparison yet (ten algorithms
implemented, but at very different scales — see
[grover.md](grover.md)'s comparison to [shor.md](shor.md), and
[deutsch-jozsa-bernstein-vazirani.md](deutsch-jozsa-bernstein-vazirani.md)'s
comparison to both, for why a direct table wouldn't be very meaningful
yet). There is, however, a cross-algorithm *transpilation* comparison:

- [cross-algorithm-transpilation.md](cross-algorithm-transpilation.md) —
  `compiler.transpilation.analyze_transpilation` applied to a
  representative, similarly-sized circuit from every algorithm except
  Shor (which has its own dedicated study above), showing that
  multi-controlled-gate-heavy circuits (Grover, HHL) cost far more
  routing overhead than CNOT/single-control circuits (Deutsch-Jozsa,
  Bernstein-Vazirani, Simon, VQE, QAOA) at similar qubit counts — even
  when the multi-controlled circuit has *fewer* qubits.
