# Shor notebooks

Exploratory / demo notebooks for Shor's algorithm.

- [shor_demo.ipynb](shor_demo.ipynb) — builds the order-finding circuit for
  N=15, visualizes it and its measurement histogram, walks through order
  finding and factor recovery, runs `factor(15)` end to end, and compares
  qubit/gate counts between `PermutationMatrixOracle` and
  `GateDecomposedOracle`. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/shor/notebooks/shor_demo.ipynb
  ```
