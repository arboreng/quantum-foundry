"""Problem instances for QAOA.

A `Problem` supplies the parameterized cost gate `exp(-i*gamma*C)` for its
cost Hamiltonian `C`, and a classical `cost_value` function used both to
compute the expectation value `implementation.py`'s optimization loop
maximizes and to evaluate a final candidate answer.
"""

from typing import Protocol

from qiskit.circuit import Gate


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

    Not yet implemented — see RFC-0008 milestone v0.2.
    """

    def __init__(self, n_qubits: int, edges: list[tuple[int, int]]):
        self.n_qubits = n_qubits
        self.edges = edges

    def cost_gate(self, gamma: float) -> Gate:
        raise NotImplementedError

    def cost_value(self, bitstring: str) -> float:
        raise NotImplementedError
