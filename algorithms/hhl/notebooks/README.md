# HHL notebooks

Exploratory / demo notebooks for HHL.

- [hhl_demo.ipynb](hhl_demo.ipynb) — builds the HHL circuit for a 2x2
  linear system, visualizes it and the postselected measurement
  histogram, then runs the full pipeline via `solve_linear_system()` and
  checks the result against `numpy.linalg.solve`'s classical answer.
  Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/hhl/notebooks/hhl_demo.ipynb
  ```
