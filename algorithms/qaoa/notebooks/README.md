# QAOA notebooks

Exploratory / demo notebooks for QAOA.

- [qaoa_demo.ipynb](qaoa_demo.ipynb) — builds the cost/mixer gates for a
  MaxCut instance, visualizes the circuit and its measurement histogram
  before parameter optimization, then runs the full classical-quantum
  loop via `solve_maxcut()` and checks the result against the
  brute-forced true optimum. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/qaoa/notebooks/qaoa_demo.ipynb
  ```
