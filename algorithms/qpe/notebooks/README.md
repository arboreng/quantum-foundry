# QPE notebooks

Exploratory / demo notebooks for Quantum Phase Estimation.

- [qpe_demo.ipynb](qpe_demo.ipynb) — builds the oracle for a known phase,
  visualizes the circuit and its measurement histogram, estimates a
  terminating-binary-fraction phase exactly and a non-terminating one with
  precision improving across `n_count`. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/qpe/notebooks/qpe_demo.ipynb
  ```
