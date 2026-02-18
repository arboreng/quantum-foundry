"""End-to-end unstructured search using Grover's algorithm.

See math.md for the amplitude-amplification theory and paper.md for the
circuit this module drives.
"""


def search(n_qubits: int, marked: set[str]) -> str:
    """Find a marked bitstring among `2**n_qubits` possibilities.

    Not yet implemented — see RFC-0004 milestone v0.2.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit("algorithms.grover.implementation is not yet implemented (RFC-0004 v0.2)")
