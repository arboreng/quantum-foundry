"""Circuit construction for the Bernstein-Vazirani algorithm.

Reuses `algorithms.deutsch_jozsa.circuit.build_oracle_query_circuit`
verbatim (RFC-0005) — Bernstein-Vazirani is mechanically the same
`H^n -> oracle -> H^n -> measure` circuit as Deutsch-Jozsa, with a different
`Oracle`. See paper.md.
"""

from algorithms.deutsch_jozsa.circuit import build_oracle_query_circuit

__all__ = ["build_oracle_query_circuit"]
