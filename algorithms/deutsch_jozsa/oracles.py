"""Oracles for the Deutsch-Jozsa algorithm.

An `Oracle` supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>` for
some boolean function `f`, that `circuit.build_oracle_query_circuit` applies
between two layers of Hadamards.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies the gate implementing `|x>|y> -> |x>|y XOR f(x)>`."""

    def oracle_gate(self) -> Gate:
        """Return the gate acting on `n_qubits + 1` qubits (input register
        + 1 ancilla)."""
        ...


class ConstantOracle:
    """`Oracle` for `f(x) = value` (0 or 1) for all `x`."""

    def __init__(self, n_qubits: int, value: int):
        if n_qubits < 1:
            raise ValueError("n_qubits must be positive")
        if value not in (0, 1):
            raise ValueError(f"value must be 0 or 1, got {value}")
        self.n_qubits = n_qubits
        self.value = value

    def oracle_gate(self) -> Gate:
        circuit = QuantumCircuit(self.n_qubits + 1, name=f"const={self.value}")
        if self.value == 1:
            circuit.x(self.n_qubits)  # unconditional flip of the ancilla
        return circuit.to_gate(label="oracle")


class ParityOracle:
    """`Oracle` for `f(x) = XOR of x_i for i in subset` — an efficient
    (O(n)-gate), always-balanced linear function (for non-empty `subset`)."""

    def __init__(self, n_qubits: int, subset: set[int]):
        if n_qubits < 1:
            raise ValueError("n_qubits must be positive")
        if not subset:
            raise ValueError("subset must be non-empty (empty subset is the constant-0 function)")
        if any(i < 0 or i >= n_qubits for i in subset):
            raise ValueError(f"subset indices must be in [0, {n_qubits})")
        self.n_qubits = n_qubits
        self.subset = subset

    def oracle_gate(self) -> Gate:
        circuit = QuantumCircuit(self.n_qubits + 1, name="parity")
        for i in self.subset:
            circuit.cx(i, self.n_qubits)
        return circuit.to_gate(label="oracle")


class BalancedOracle:
    """`Oracle` for `f(x) = 1` iff `x` is in an explicit, arbitrary marked
    set of exactly half of all `2**n_qubits` bitstrings. Exact but
    exponential in gate count (mirrors
    `algorithms.shor.oracles.PermutationMatrixOracle`'s tradeoff)."""

    def __init__(self, n_qubits: int, marked: set[str]):
        if n_qubits < 1:
            raise ValueError("n_qubits must be positive")
        expected = 2 ** (n_qubits - 1)
        if len(marked) != expected:
            raise ValueError(
                f"marked must contain exactly half of all bitstrings "
                f"({expected} for n_qubits={n_qubits}), got {len(marked)}"
            )
        for m in marked:
            if len(m) != n_qubits:
                raise ValueError(f"marked bitstring {m!r} does not have length n_qubits={n_qubits}")
            if any(bit not in "01" for bit in m):
                raise ValueError(f"marked bitstring {m!r} must contain only 0 and 1")
        self.n_qubits = n_qubits
        self.marked = marked

    def oracle_gate(self) -> Gate:
        circuit = QuantumCircuit(self.n_qubits + 1, name="balanced")
        for m in self.marked:
            zero_qubits = [q for q in range(self.n_qubits) if m[self.n_qubits - 1 - q] == "0"]
            for q in zero_qubits:
                circuit.x(q)
            circuit.mcx(list(range(self.n_qubits)), self.n_qubits)
            for q in zero_qubits:
                circuit.x(q)
        return circuit.to_gate(label="oracle")
