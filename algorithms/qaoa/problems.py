"""Problem instances for QAOA.

A `Problem` supplies the parameterized cost gate `exp(-i*gamma*C)` for its
cost Hamiltonian `C`, and a classical `cost_value` function used both to
compute the expectation value `implementation.py`'s optimization loop
maximizes and to evaluate a final candidate answer.
"""

from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Problem(Protocol):
    """Supplies the cost gate and classical cost function for a
    combinatorial optimization problem instance."""

    n_qubits: int

    def cost_gate(self, gamma: float) -> Gate:
        """Return the gate implementing `exp(-i*gamma*C)` for this
        problem's cost Hamiltonian `C`."""
        ...

    def cost_value(self, bitstring: str) -> float:
        """Classically evaluate the cost function for a candidate
        bitstring (e.g. number of cut edges for MaxCut)."""
        ...


class MaxCutProblem:
    """`Problem` for MaxCut: partition a graph's vertices into two sets
    maximizing the number of edges crossing between them.

    Cost Hamiltonian `C = sum_{(i,j) in edges} (1 - Z_i*Z_j)/2` (`C|z>`
    equals the number of cut edges for bitstring `z`); `exp(-i*gamma*C)`
    factors into one two-qubit gate per edge since all terms commute.
    """

    def __init__(self, n_qubits: int, edges: list[tuple[int, int]]):
        self.n_qubits = n_qubits
        self.edges = edges

    def cost_gate(self, gamma: float) -> Gate:
        circuit = QuantumCircuit(self.n_qubits, name=f"cost({gamma})")
        for i, j in self.edges:
            # exp(i*(gamma/2)*Z_i*Z_j), dropping the per-edge global phase
            # exp(-i*gamma/2) from the (1 - Z_i*Z_j)/2 term (unobservable).
            circuit.cx(i, j)
            circuit.rz(-gamma, j)
            circuit.cx(i, j)
        return circuit.to_gate(label="cost")

    def cost_value(self, bitstring: str) -> float:
        bits = [int(bit) for bit in reversed(bitstring)]
        return float(sum(1 for i, j in self.edges if bits[i] != bits[j]))
