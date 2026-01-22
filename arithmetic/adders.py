"""Reversible modular arithmetic built from the QFT (Draper's construction),
used by `algorithms.shor.oracles.GateDecomposedOracle` (RFC-0002) as an
elementary-gate alternative to RFC-0001's classically-computed permutation
matrix.

Built and verified bottom-up: `add_constant_gate` (plain Draper adder mod
`2**num_qubits`) -> `add_constant_mod_N_gate` (Beauregard's modular adder) ->
`controlled_mult_mod_N_gate` (controlled multiplication by a classical
constant mod `N`, via repeated doubling).
"""

import math

from qiskit.circuit import Gate, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import CXGate

from arithmetic.qft import inverse_qft, qft


def add_constant_gate(num_qubits: int, c: int) -> Gate:
    """`|x> -> |x + c mod 2**num_qubits>`, via QFT -> phase rotations -> inverse QFT."""
    circuit = QuantumCircuit(num_qubits, name=f"+{c}")
    circuit.append(qft(num_qubits).to_gate(), range(num_qubits))
    for j in range(num_qubits):
        angle = 2 * math.pi * c / 2 ** (num_qubits - j)
        circuit.p(angle, j)
    circuit.append(inverse_qft(num_qubits).to_gate(), range(num_qubits))
    return circuit.to_gate(label=f"+{c} mod 2^{num_qubits}")


def add_constant_mod_N_gate(num_qubits: int, c: int, N: int) -> Gate:
    """`|x> -> |x + c mod N>` for `x < N`, using Beauregard's construction:
    add `c`, conditionally subtract `N` if the result did *not* overflow
    (detected via the high-order qubit of an `(num_qubits + 1)`-qubit
    register), recording the decision in an ancilla that is then uncomputed
    via an anti-controlled correction.

    Total width: `num_qubits + 1` register qubits + 1 ancilla qubit
    = `num_qubits + 2` qubits.
    """
    c = c % N
    n = num_qubits + 1  # extra high bit so partial sums don't wrap mod 2**n
    reg = QuantumRegister(n, name="x")
    anc = QuantumRegister(1, name="anc")
    circuit = QuantumCircuit(reg, anc, name=f"+{c} mod {N}")
    msb = reg[n - 1]

    add_c = add_constant_gate(n, c)
    add_neg_c = add_constant_gate(n, -c)
    add_N = add_constant_gate(n, N)
    add_neg_N = add_constant_gate(n, -N)

    circuit.append(add_c, reg)
    circuit.append(add_neg_N, reg)
    # msb = 1 iff x + c - N is negative, i.e. x + c < N (shouldn't have subtracted N)
    circuit.append(CXGate(), [msb, anc[0]])
    circuit.append(add_N.control(1), [anc[0], *reg])
    # register now holds the correct (x + c) mod N in both branches; uncompute anc
    circuit.append(add_neg_c, reg)
    # after subtracting c: msb is 1 iff the *other* branch was taken, so anc
    # must be cleared by an anti-controlled (control-on-0) CNOT on msb
    circuit.x(msb)
    circuit.append(CXGate(), [msb, anc[0]])
    circuit.x(msb)
    circuit.append(add_c, reg)

    return circuit.to_gate(label=f"+{c} mod {N}")


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x, y = _egcd(b, a % b)
    return g, y, x - (a // b) * y


def modinv(a: int, N: int) -> int:
    g, x, _ = _egcd(a % N, N)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {N}")
    return x % N


def controlled_mult_mod_N_gate(num_qubits: int, a: int, N: int) -> Gate:
    """Controlled `|y> -> |a*y mod N>` for `y < N`, via repeated modular
    addition of shifted constants into an accumulator, controlled-swap back
    into the input register, then inverse multiplication by `a**-1 mod N` to
    uncompute the accumulator.

    Each modular addition needs to be controlled on *both* the outer control
    qubit and one bit of `y`; rather than asking Qiskit to synthesize
    `.control(2)` of an already-composite gate (fragile/slow for deeply
    nested custom gates), a Toffoli ANDs the two controls into one scratch
    qubit and `add_constant_mod_N_gate(...).control(1)` — the same
    single-control pattern already verified inside `add_constant_mod_N_gate`
    itself — is applied from that.

    Qubit layout: 1 control + `num_qubits` input register (`y`) +
    `num_qubits + 2` accumulator ancillas + 1 combined-control ancilla
    = `num_qubits + 3` total ancillas, matching `Oracle.num_ancilla_qubits`.
    """
    ctrl = QuantumRegister(1, name="ctrl")
    y_reg = QuantumRegister(num_qubits, name="y")
    acc_reg = QuantumRegister(num_qubits + 2, name="acc")
    cc_reg = QuantumRegister(1, name="cc")
    circuit = QuantumCircuit(ctrl, y_reg, acc_reg, cc_reg, name=f"*{a} mod {N}")

    def accumulate(multiplier: int) -> None:
        for i in range(num_qubits):
            shifted = (multiplier * 2**i) % N
            gate = add_constant_mod_N_gate(num_qubits, shifted, N).control(1)
            circuit.ccx(ctrl[0], y_reg[i], cc_reg[0])
            circuit.append(gate, [cc_reg[0], *acc_reg])
            circuit.ccx(ctrl[0], y_reg[i], cc_reg[0])

    accumulate(a)

    # acc_reg's low num_qubits qubits now hold a*y mod N; controlled-swap into y_reg
    for i in range(num_qubits):
        circuit.cswap(ctrl[0], y_reg[i], acc_reg[i])

    # uncompute the accumulator (now holding the pre-swap y) via -a^-1
    a_inv = modinv(a, N)
    accumulate(-a_inv)

    return circuit.to_gate(label=f"c-*{a} mod {N}")
