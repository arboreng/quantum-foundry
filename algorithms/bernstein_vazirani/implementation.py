"""End-to-end hidden-string recovery using the Bernstein-Vazirani algorithm.

See math.md for the theory and paper.md for the circuit this module drives.
"""

from algorithms.bernstein_vazirani.oracles import Oracle


def find_hidden_string(n_qubits: int, oracle: Oracle) -> str:
    """Recover the hidden bitstring `s` from `oracle`'s `f(x) = s.x mod 2`
    with a single query.

    Not yet implemented — see RFC-0005 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(
        "algorithms.bernstein_vazirani.implementation is not yet implemented (RFC-0005 v0.2)"
    )
