# validation/

Cross-validation of algorithm results against known-correct outputs and other
frameworks (e.g. comparing against a reference Qiskit tutorial implementation
or published factorization results).

- [known_answers.py](known_answers.py) — `CASES`: one known-answer instance
  per algorithm (Shor's N=15 textbook factorization, Grover's search for a
  marked item, Deutsch-Jozsa/Bernstein-Vazirani's promise-problem examples,
  Simon's hidden period, QPE's exact phase, QAOA/VQE's approximate-optimum
  instances, HHL's linear system), each run through that algorithm's
  top-level public API (`factor`, `search`, `estimate_phase`, ...) rather
  than any internal circuit-building detail. Distinct from each algorithm's
  own test suite: a black-box "does the whole stack still reproduce the
  published answer" regression check, not a re-derivation of correctness.
  `run_validation()` runs every case and reports pass/fail without stopping
  at the first failure; `tests/test_known_answers.py` runs each case as its
  own pytest test.

```bash
uv run python -m validation.known_answers
```
