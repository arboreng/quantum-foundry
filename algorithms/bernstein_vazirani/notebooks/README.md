# Bernstein-Vazirani notebooks

Exploratory / demo notebooks for the Bernstein-Vazirani algorithm.

- [bernstein_vazirani_demo.ipynb](bernstein_vazirani_demo.ipynb) — builds
  the oracle for a hidden bitstring, visualizes the circuit and its
  measurement histogram, runs `find_hidden_string()` on several hidden
  strings including the degenerate all-zeros case. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/bernstein_vazirani/notebooks/bernstein_vazirani_demo.ipynb
  ```
