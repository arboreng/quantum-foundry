"""Circuit and result visualization for the Bernstein-Vazirani algorithm.

Data computation is kept separate from matplotlib rendering, mirroring
`algorithms/shor/visualization.py`.
"""

from typing import Any

from qiskit.circuit import QuantumCircuit
from qiskit.visualization import plot_histogram


def circuit_figure(circuit: QuantumCircuit) -> Any:
    """Render a circuit diagram (matplotlib figure)."""
    return circuit.draw("mpl")


def histogram_data(counts: dict[str, int]) -> dict[str, float]:
    """Convert raw measurement counts into normalized probabilities."""
    total = sum(counts.values())
    return {bitstring: count / total for bitstring, count in counts.items()}


def plot_measurement_histogram(counts: dict[str, int]) -> Any:
    """Render measurement counts as a matplotlib histogram."""
    return plot_histogram(counts)
