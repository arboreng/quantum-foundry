"""Oracles for HHL: a controlled-power-of-unitary abstraction for a
Hermitian matrix `A`'s time evolution `exp(i*A*t)`, structurally the same
shape as `algorithms/qpe/oracles.py`'s `Oracle`.
"""

import math
from typing import Protocol

from qiskit.circuit import Gate, QuantumCircuit


class Oracle(Protocol):
    """Supplies controlled powers of `exp(i*A*t)` for a Hermitian
    matrix `A`."""

    num_qubits: int

    def controlled_power_gate(self, power: int) -> Gate:
        """Return a controlled gate implementing `exp(i*A*t*power)`."""
        ...


class DiagonalXOracle:
    """`Oracle` for `A = a*I + b*X` (arbitrary real `a`, `b`; eigenvalues
    `a+b` (eigenvector `|+>`) and `a-b` (eigenvector `|->`)).

    Since `I` and `X` commute, `exp(i*A*t*power)` factors exactly into a
    global phase `exp(i*a*t*power)` times `exp(i*b*t*power*X)` — no
    Trotterization needed.
    """

    def __init__(self, a: float, b: float, t: float):
        self.a = a
        self.b = b
        self.t = t
        self.num_qubits = 1

    def controlled_power_gate(self, power: int) -> Gate:
        circuit = QuantumCircuit(1, name=f"U^{power}")
        circuit.global_phase = self.a * self.t * power
        circuit.rx(-2 * self.b * self.t * power, 0)
        return circuit.to_gate(label="U^k").control(1)


class GeneralSingleQubitOracle:
    """`Oracle` for `A = a*I + v.sigma` — any single-qubit Hermitian
    matrix, for arbitrary real `a` and real 3-vector `v = (vx, vy, vz)`
    (`v.sigma = vx*X + vy*Y + vz*Z`). Eigenvalues `a +- |v|`; generalizes
    `DiagonalXOracle` (`v = (b, 0, 0)`) to an arbitrary axis, not just the
    `X` axis.

    `exp(i*A*t*power)` factors into the same global phase
    `exp(i*a*t*power)` times `exp(i*theta*(v_hat.sigma))` for `theta =
    |v|*t*power` and unit vector `v_hat = v/|v|`. Writing `v_hat`'s
    spherical coordinates as polar angle `theta_p` (from the `Z` axis)
    and azimuthal angle `phi` (from the `X` axis in the `XY` plane),
    `W = RZ(phi).RY(theta_p)` rotates `Z` onto `v_hat`, so
    `exp(i*theta*(v_hat.sigma)) = W . RZ(-2*theta) . W^dagger` (`RZ(-2*
    theta) = exp(i*theta*Z)` exactly, no extra global phase). Verified
    against `scipy.linalg.expm`'s exact matrix exponential of `A`, for
    several `(a, v, t, power)` combinations including axis-aligned and
    general directions, in `tests/test_oracles_general.py`.
    """

    def __init__(self, a: float, vx: float, vy: float, vz: float, t: float):
        self.a = a
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.t = t
        self.num_qubits = 1

    def controlled_power_gate(self, power: int) -> Gate:
        v_norm = math.sqrt(self.vx**2 + self.vy**2 + self.vz**2)

        circuit = QuantumCircuit(1, name=f"U^{power}")
        circuit.global_phase = self.a * self.t * power

        if v_norm == 0.0:
            return circuit.to_gate(label="U^k").control(1)

        theta = v_norm * self.t * power
        theta_p = math.acos(self.vz / v_norm)
        phi = math.atan2(self.vy, self.vx)

        circuit.rz(-phi, 0)
        circuit.ry(-theta_p, 0)
        circuit.rz(-2 * theta, 0)
        circuit.ry(theta_p, 0)
        circuit.rz(phi, 0)
        return circuit.to_gate(label="U^k").control(1)
