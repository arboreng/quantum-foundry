"""End-to-end constant-vs-balanced decision using the Deutsch-Jozsa
algorithm.

See math.md for the promise-problem theory and paper.md for the circuit
this module drives.
"""

from algorithms.deutsch_jozsa.oracles import Oracle


def is_constant(n_qubits: int, oracle: Oracle) -> bool:
    """Determine whether `oracle`'s function is constant (True) or balanced
    (False) with a single query.

    Not yet implemented — see RFC-0005 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(
        "algorithms.deutsch_jozsa.implementation is not yet implemented (RFC-0005 v0.2)"
    )
