"""Oracles for Simon's algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for a
function `f: {0,1}^n -> {0,1}^n` promised to be one-to-one or exactly
two-to-one with a hidden period `s`, that `circuit.build_simon_circuit`
applies between two layers of Hadamards on the input register.

Bit-index convention matches `algorithms.bernstein_vazirani.oracles.HiddenStringOracle`:
qubit `k` corresponds to the character at position `n_qubits - 1 - k` of a
bitstring like `s`.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    n_qubits: int

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `2 * n_qubits` qubits (input register
        + output register, each `n_qubits` wide)."""
        ...


def _bits(s: str) -> list[int]:
    """`bits[k]` = the bit of `s` for qubit `k`."""
    return [int(bit) for bit in reversed(s)]


def _linear_matrix_rows(s: str) -> list[int]:
    """Build the `n` rows (each an n-bit integer bitmask over input qubits)
    of a matrix `M` with kernel exactly `{0, s}`.

    Let `i` be the index of a `1` bit in `s`. For `j != i`: row `j` is
    `e_j` if `s_j == 0`, else `e_j XOR e_i` (`e_k` = standard basis vector).
    Both cases satisfy `row_j . s = 0 mod 2`. Row `i` is all-zero. The `n-1`
    nonzero rows are linearly independent (each has a unique leading `1` at
    its own index `j != i`), so `M` has rank `n-1` and kernel exactly
    `span{s}`.
    """
    s_bits = _bits(s)
    n = len(s_bits)
    if not any(s_bits):
        raise ValueError("s must be nonzero")
    i = s_bits.index(1)

    rows = [0] * n
    for j in range(n):
        if j == i:
            continue
        rows[j] = (1 << j) if s_bits[j] == 0 else (1 << j) | (1 << i)
    return rows


class LinearOracle:
    """`Oracle` for `f(x) = Mx` (matrix-vector product over GF(2)) for an
    `n x n` binary matrix `M` with kernel exactly `{0, s}` — efficient
    (O(n^2)-gate) and exact for the broad class of linear/affine
    two-to-one functions."""

    def __init__(self, s: str):
        self.s = s
        self.n_qubits = len(s)
        self.matrix_rows = _linear_matrix_rows(s)

    def oracle_gate(self) -> Gate:
        n = self.n_qubits
        circuit = QuantumCircuit(2 * n, name=f"linear s={self.s}")
        for k in range(n):
            row = self.matrix_rows[k]
            for j in range(n):
                if row & (1 << j):
                    circuit.cx(j, n + k)
        return circuit.to_gate(label="oracle")


def _permutation_labels(s: str) -> list[int]:
    """`labels[x]` = `f(x)` for the explicit two-to-one function with
    hidden period `s`: pair representatives (`min(x, x XOR s)`) are sorted
    and each assigned a label via bit-reversal of its sort-index — a
    deliberately non-GF(2)-linear scrambling, so this oracle can't be
    expressed as any single linear map (unlike `LinearOracle`)."""
    s_bits = _bits(s)
    n = len(s_bits)
    s_int = int("".join(str(b) for b in reversed(s_bits)), 2)
    if s_int == 0:
        raise ValueError("s must be nonzero")

    representatives = sorted({min(x, x ^ s_int) for x in range(2**n)})
    num_pairs = len(representatives)
    bit_width = (num_pairs - 1).bit_length() if num_pairs > 1 else 1

    def scramble(index: int) -> int:
        return int(format(index, f"0{bit_width}b")[::-1], 2)

    labels = [0] * (2**n)
    for index, rep in enumerate(representatives):
        label = scramble(index)
        labels[rep] = label
        labels[rep ^ s_int] = label
    return labels


class PermutationOracle:
    """`Oracle` for an arbitrary two-to-one function with hidden period
    `s`, via an explicit lookup mapping each pair `{x, x XOR s}` to a
    unique label. General (any two-to-one function, not just linear ones)
    but exponential in gate count — small `n_qubits` only."""

    def __init__(self, s: str):
        self.s = s
        self.n_qubits = len(s)
        self.labels = _permutation_labels(s)

    def oracle_gate(self) -> Gate:
        n = self.n_qubits
        circuit = QuantumCircuit(2 * n, name=f"perm s={self.s}")
        for x in range(2**n):
            label = self.labels[x]
            zero_qubits = [q for q in range(n) if not (x & (1 << q))]
            for q in zero_qubits:
                circuit.x(q)
            for k in range(n):
                if label & (1 << k):
                    circuit.mcx(list(range(n)), n + k)
            for q in zero_qubits:
                circuit.x(q)
        return circuit.to_gate(label="oracle")
