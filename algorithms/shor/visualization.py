"""Circuit and result visualization for Shor's algorithm.

Data computation is kept separate from matplotlib rendering (`histogram_data`
vs. `plot_measurement_histogram`) so a future non-matplotlib renderer isn't
blocked by these functions — see RFC-0001's roadmap for richer visualization
(oracle/QFT/continued-fraction views) planned once a second algorithm exists
to justify a shared `visualization/` module.
"""

from typing import Any

from qiskit.circuit import QuantumCircuit
from qiskit.visualization import plot_histogram


def circuit_figure(circuit: QuantumCircuit) -> Any:
    """Render a circuit diagram (matplotlib figure)."""
    return circuit.draw("mpl")


def histogram_data(counts: dict[str, int]) -> dict[str, float]:
    """Convert raw measurement counts into normalized probabilities.

    Pure computation, no plotting — reusable by any renderer.
    """
    total = sum(counts.values())
    return {bitstring: count / total for bitstring, count in counts.items()}


def plot_measurement_histogram(counts: dict[str, int]) -> Any:
    """Render measurement counts as a matplotlib histogram."""
    return plot_histogram(counts)
