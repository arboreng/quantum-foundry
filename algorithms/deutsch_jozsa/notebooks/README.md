# Deutsch-Jozsa notebooks

Exploratory / demo notebooks for the Deutsch-Jozsa algorithm.

- [deutsch_jozsa_demo.ipynb](deutsch_jozsa_demo.ipynb) — builds a constant
  and a balanced (both `ParityOracle` and explicit `BalancedOracle`)
  oracle, visualizes each circuit and its measurement histogram, runs
  `is_constant()` on all three. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/deutsch_jozsa/notebooks/deutsch_jozsa_demo.ipynb
  ```
