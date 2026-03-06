"""End-to-end constant-vs-balanced decision using the Deutsch-Jozsa
algorithm.

See math.md for the promise-problem theory and paper.md for the circuit
this module drives.
"""

from algorithms.deutsch_jozsa.circuit import build_oracle_query_circuit
from algorithms.deutsch_jozsa.execution import AerExecutor, Executor
from algorithms.deutsch_jozsa.oracles import ConstantOracle, Oracle


def is_constant(n_qubits: int, oracle: Oracle, *, executor: Executor | None = None) -> bool:
    """Determine whether `oracle`'s function is constant (True) or balanced
    (False) with a single query.

    Exact and deterministic (unlike Shor's/Grover's probabilistic
    algorithms): a single shot suffices, since the measured bitstring is
    all-zeros with certainty iff the function is constant (see math.md).
    """
    executor = executor if executor is not None else AerExecutor()
    circuit = build_oracle_query_circuit(n_qubits, oracle)
    counts = executor.run(circuit, shots=1)
    bitstring = next(iter(counts))
    return bitstring == "0" * n_qubits


if __name__ == "__main__":
    print(is_constant(3, ConstantOracle(3, value=0)))
