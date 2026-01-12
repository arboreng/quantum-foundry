# Shor's Algorithm — Circuit Derivation

Level 2 of [VISION.md's understanding model](../../VISION.md#levels-of-understanding).
Builds on [math.md](math.md).

TODO:

- Quantum Fourier Transform (QFT) construction and its role in phase estimation
- Modular exponentiation circuit: `|x>|1> -> |x>|a^x mod N>`
- Full circuit: superposition -> modular exponentiation -> inverse QFT -> measurement
- Qubit count and gate depth as a function of `N`
- Simplifications used in the simulator implementation vs. a hardware-faithful circuit
