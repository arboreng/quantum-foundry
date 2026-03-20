"""End-to-end hidden-period recovery using Simon's algorithm.

See math.md for the theory and paper.md for the circuit this module drives.
Includes this repo's first genuine classical post-processing step: GF(2)
Gaussian elimination (not just a bitstring read or a continued fraction).
"""

from algorithms.simon.circuit import build_simon_circuit
from algorithms.simon.execution import AerExecutor, Executor
from algorithms.simon.oracles import Oracle


def _row_reduce(rows: list[int], n_qubits: int) -> tuple[list[int], dict[int, int]]:
    """GF(2) Gaussian elimination via XOR to full row-echelon form.

    Returns the (possibly reordered/reduced) rows and a `{pivot_column:
    row_index}` map. Used both to check rank (independence testing) and,
    once enough independent equations are collected, to solve for the
    hidden period.
    """
    rows = rows[:]
    pivot_row_for_col: dict[int, int] = {}
    r = 0
    for col in range(n_qubits):
        bit = 1 << col
        pivot = next((i for i in range(r, len(rows)) if rows[i] & bit), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and (rows[i] & bit):
                rows[i] ^= rows[r]
        pivot_row_for_col[col] = r
        r += 1
    return rows, pivot_row_for_col


def _rank_gf2(rows: list[int], n_qubits: int) -> int:
    _, pivot_row_for_col = _row_reduce(rows, n_qubits)
    return len(pivot_row_for_col)


def _solve_gf2_nullspace(equations: list[int], n_qubits: int) -> int:
    """Given `n_qubits - 1` independent equations (each an n-bit integer `y`
    with `y . s = 0 mod 2`), solve for the unique nonzero `s` in the null
    space."""
    rows, pivot_row_for_col = _row_reduce(equations, n_qubits)
    free_cols = [col for col in range(n_qubits) if col not in pivot_row_for_col]
    if len(free_cols) != 1:
        raise RuntimeError(
            f"expected exactly one free column, got {len(free_cols)} "
            f"(equations may not have rank n_qubits - 1)"
        )
    free_col = free_cols[0]

    s = 1 << free_col
    for col, row_index in pivot_row_for_col.items():
        if rows[row_index] & (1 << free_col):
            s |= 1 << col
    return s


def find_hidden_period(
    n_qubits: int,
    oracle: Oracle,
    *,
    executor: Executor | None = None,
    max_attempts: int | None = None,
) -> str:
    """Recover the hidden period `s` from `oracle`'s two-to-one function
    `f(x) = f(x XOR s)`.

    Collects nonzero measured bitstrings that increase the rank of the
    equation set until `n_qubits - 1` independent equations are found, then
    solves the resulting GF(2) linear system for `s`. Assumes `oracle` is
    genuinely two-to-one (both `LinearOracle` and `PermutationOracle` are,
    by construction) — see math.md for the one-to-one case, not handled
    here.
    """
    executor = executor if executor is not None else AerExecutor()
    circuit = build_simon_circuit(n_qubits, oracle)
    max_attempts = max_attempts if max_attempts is not None else 4 * n_qubits + 20

    equations: list[int] = []
    attempts = 0
    target = n_qubits - 1
    while len(equations) < target and attempts < max_attempts:
        attempts += 1
        counts = executor.run(circuit, shots=1)
        y = int(next(iter(counts)), 2)
        if y == 0:
            continue
        if _rank_gf2([*equations, y], n_qubits) > _rank_gf2(equations, n_qubits):
            equations.append(y)

    if len(equations) < target:
        raise RuntimeError(
            f"find_hidden_period did not collect {target} independent equations "
            f"in {max_attempts} attempts"
        )

    s_int = _solve_gf2_nullspace(equations, n_qubits)
    return format(s_int, f"0{n_qubits}b")


if __name__ == "__main__":
    from algorithms.simon.oracles import LinearOracle

    print(find_hidden_period(3, LinearOracle("101")))
