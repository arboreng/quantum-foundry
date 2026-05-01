# Cross-Algorithm Transpilation Study

Generated via `compiler.cross_algorithm_study.run_study()`: a
representative, similarly-sized (4-10 qubit) circuit from every algorithm
except Shor (which already has its own dedicated study —
[shor-transpilation.md](shor-transpilation.md)), transpiled against the
same hand-built linear nearest-neighbor `CouplingMap`
(`compiler.targets.linear_coupling_map`) with basis gates `{rz, sx, x,
cx}`, at `optimization_level=1` (RFC-0003 found this level already
captures most of the available improvement over level 0, with levels 2-3
buying little more).

| Algorithm | Qubits | Gate count | Circuit depth | SWAP count |
| ------------------- | ------ | ---------- | -------------- | ----------- |
| Deutsch-Jozsa        | 6      | 52         | 27              | 3           |
| Bernstein-Vazirani   | 6      | 32         | 13              | 1           |
| Simon                | 10     | 41         | 10              | 0           |
| VQE                  | 4      | 39         | 12              | 0           |
| QAOA                 | 5      | 72         | 43              | 4           |
| QPE                  | 6      | 149        | 101             | 18          |
| Grover               | 5      | 610        | 441             | 61          |
| HHL                  | 5      | 818        | 638             | 50          |

Deutsch-Jozsa uses `ParityOracle` (efficient, `O(n)` gates), not
`BalancedOracle` (its other implementation, exponential in gate count by
design — see its own docstring) — including `BalancedOracle` here would
measure oracle-construction cost, not routing overhead, and would dwarf
every other row regardless of connectivity.

## Reading this

At similar qubit counts, the eight circuits split into two clear groups:

-   **CNOT/single-control circuits** (Deutsch-Jozsa, Bernstein-Vazirani,
    Simon, VQE, QAOA): 32-72 gates, 0-4 swaps. Their two-qubit
    interactions are `CX` gates directly between oracle/ansatz qubits, or
    (QAOA) a fixed pattern of edges — cheap to route on a linear chain
    because there's rarely a need to move a qubit far from its
    interaction partners.
-   **Multi-controlled-gate circuits** (QPE, Grover, HHL): 149-818 gates,
    18-61 swaps. QPE's controlled phase gates are single-controlled (so
    it's the cheapest of the three), but Grover's diffusion operator and
    marking oracle, and HHL's multiplexed rotation, both use gates
    controlled by *every other qubit in the register* — each one requires
    routing several distant qubits next to each other before the native
    basis gate set can express the multi-control decomposition, and
    that's before accounting for Grover repeating this twice per
    iteration.

**Multi-controlled gates, not qubit count, drive routing cost here.**
Simon's circuit (10 qubits, the largest in this table) transpiles with
*zero* swaps, while HHL's (5 qubits, half the size) needs 50 — because
Simon's oracle is pure `CX`, while HHL's rotation gates each touch every
clock qubit at once. This is the same lesson
[shor-transpilation.md](shor-transpilation.md) draws about
`GateDecomposedOracle`'s `ccx`/multi-qubit pattern not fitting a linear
chain, now confirmed across circuit families rather than one algorithm's
scaling study.

## Reproducing

```bash
uv run python -m compiler.cross_algorithm_study
```
