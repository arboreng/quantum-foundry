# VQE notebooks

Exploratory / demo notebooks for VQE.

- [vqe_demo.ipynb](vqe_demo.ipynb) — builds the hardware-efficient ansatz
  and a per-term measurement circuit for a transverse-field Ising chain,
  visualizes the circuit and a measurement histogram before parameter
  optimization, then runs the full classical-quantum loop via
  `solve_ground_state()` and checks the result against exact classical
  diagonalization. Re-execute with:
  ```bash
  uv run jupyter execute --inplace algorithms/vqe/notebooks/vqe_demo.ipynb
  ```
