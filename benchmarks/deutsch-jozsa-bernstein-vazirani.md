# Deutsch-Jozsa and Bernstein-Vazirani: Scaling

Generated via `uv run python -m algorithms.deutsch_jozsa.benchmark` and
`uv run python -m algorithms.bernstein_vazirani.benchmark`. Combined into
one doc (rather than two near-duplicates) since [RFC-0005](../docs/rfcs/0005-deutsch-jozsa-bernstein-vazirani.md)
bundles both algorithms — they share the exact same circuit shape.

| Algorithm          | n_qubits | Gate count | Circuit depth | Simulation time |
| ------------------- | -------- | ---------- | -------------- | ---------------- |
| Deutsch-Jozsa (`ParityOracle`) | 3  | 7  | 4  | 0.11s |
| Deutsch-Jozsa (`ParityOracle`) | 4  | 8  | 4  | 0.09s |
| Deutsch-Jozsa (`ParityOracle`) | 6  | 10 | 4  | 0.09s |
| Deutsch-Jozsa (`ParityOracle`) | 8  | 12 | 4  | 0.09s |
| Deutsch-Jozsa (`ParityOracle`) | 10 | 14 | 4  | 0.09s |
| Bernstein-Vazirani (`HiddenStringOracle`, all-ones `s`) | 3  | 13 | 7  | 0.10s |
| Bernstein-Vazirani (`HiddenStringOracle`, all-ones `s`) | 4  | 17 | 8  | 0.10s |
| Bernstein-Vazirani (`HiddenStringOracle`, all-ones `s`) | 6  | 25 | 10 | 0.10s |
| Bernstein-Vazirani (`HiddenStringOracle`, all-ones `s`) | 8  | 33 | 12 | 0.10s |
| Bernstein-Vazirani (`HiddenStringOracle`, all-ones `s`) | 10 | 41 | 14 | 0.10s |

## Reading this

Both scale **linearly** in `n_qubits` — the cheapest growth rate of any
algorithm in this repo, and the concrete shape of the fact that neither
algorithm is *searching* a space that grows with `n_qubits` (contrast with
[benchmarks/grover.md](grover.md)'s `sqrt(2^n)` iteration growth, or
[benchmarks/shor.md](shor.md)'s far steeper growth).

Deutsch-Jozsa's `ParityOracle` circuit depth is **constant** (`4`,
regardless of `n_qubits`) because its oracle is a layer of parallel CNOTs
(one per qubit in the parity subset, all targeting the same ancilla but
otherwise independent) that Qiskit's transpiler schedules without adding
depth — only gate *count* grows with `n_qubits`. Bernstein-Vazirani's depth
does grow slowly (`7` to `14` across this range) because its
`HiddenStringOracle`'s CNOTs are less parallelizable in general (depends on
which bits of `s` are set); with an all-ones `s` here, every qubit
participates, so growth is close to worst-case for this construction.

Simulation time is flat (~0.09-0.11s) across the entire range for both —
dominated by fixed per-shot/per-call overhead, the same as
[benchmarks/grover.md](grover.md)'s finding at this scale. Both algorithms
use exactly 1 shot (`implementation.py`'s `is_constant`/`find_hidden_string`
are deterministic single-query algorithms — see each algorithm's math.md),
so there isn't even a shots-count lever to grow simulation cost the way
Shor's/Grover's `shots=100+` calls have.

## Reproducing

```bash
uv run python -m algorithms.deutsch_jozsa.benchmark
uv run python -m algorithms.bernstein_vazirani.benchmark
```
