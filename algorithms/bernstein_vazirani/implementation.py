"""End-to-end hidden-string recovery using the Bernstein-Vazirani algorithm.

See math.md for the theory and paper.md for the circuit this module drives.
"""

from algorithms.bernstein_vazirani.circuit import build_oracle_query_circuit
from algorithms.bernstein_vazirani.execution import AerExecutor, Executor
from algorithms.bernstein_vazirani.oracles import HiddenStringOracle, Oracle


def find_hidden_string(n_qubits: int, oracle: Oracle, *, executor: Executor | None = None) -> str:
    """Recover the hidden bitstring `s` from `oracle`'s `f(x) = s.x mod 2`
    with a single query.

    Exact and deterministic (unlike Shor's/Grover's probabilistic
    algorithms): the measured bitstring *is* `s` with certainty (see
    math.md), so a single shot suffices.
    """
    executor = executor if executor is not None else AerExecutor()
    circuit = build_oracle_query_circuit(n_qubits, oracle)
    counts = executor.run(circuit, shots=1)
    return next(iter(counts))


if __name__ == "__main__":
    print(find_hidden_string(3, HiddenStringOracle("101")))
