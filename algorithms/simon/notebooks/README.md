# Simon notebooks

Exploratory / demo notebooks for Simon's algorithm.

- [simon_demo.ipynb](simon_demo.ipynb) — builds the oracle for a hidden
  period, visualizes the circuit and its measurement histogram (verifying
  every measured `y` satisfies `y.s = 0 mod 2`), recovers the period via
  `find_hidden_period()` for both `LinearOracle` and `PermutationOracle`.
  Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/simon/notebooks/simon_demo.ipynb
  ```
