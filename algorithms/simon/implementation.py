"""End-to-end hidden-period recovery using Simon's algorithm.

See math.md for the theory and paper.md for the circuit this module drives.
"""

from algorithms.simon.oracles import Oracle


def find_hidden_period(n_qubits: int, oracle: Oracle) -> str:
    """Recover the hidden period `s` from `oracle`'s two-to-one function
    `f(x) = f(x XOR s)`.

    Not yet implemented — see RFC-0006 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.simon.implementation is not yet implemented (RFC-0006 v0.2)")
