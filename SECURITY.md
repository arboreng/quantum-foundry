# Security Policy

## Supported versions

Quantum Foundry is pre-1.0. Only the latest released version receives
fixes; there are no maintained backport branches.

| Version | Supported |
| ------- | --------- |
| 0.9.x   | ✅        |
| < 0.9   | ❌        |

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
(the **Security** tab → **Report a vulnerability**). Please do not open a
public issue for something you believe is exploitable.

Include the affected version or commit, what an attacker gains, and the
smallest reproduction you have.

## What to expect

- **Acknowledgement** within 7 days.
- **Initial assessment** — whether it is reproducible and in scope — within 30 days.
- **Disclosure** coordinated with you once a fix is available. Credit is given
  by default; say so if you would rather not be named.

This is a volunteer-maintained project with no paid on-call rotation, so
these are good-faith targets rather than a contractual SLA. There is no
bug bounty.

## Reporting correctness problems

Most of what could go wrong in this repository is not a memory-safety bug
but a **wrong answer**: an algorithm that silently returns an incorrect
result. That matters here because the repository implements Shor's
algorithm and other primitives with cryptographic relevance, and because
this code is written to be read and learned from — a plausible-looking
derivation that is subtly wrong propagates into whatever a reader builds
next.

Correctness problems are **normal public issues**, not security reports.
Open an issue with the construction involved and the evidence that it is
wrong — ideally a `Statevector`/`Operator` equivalence check or a
brute-force classical comparison, as described in
[CONTRIBUTING.md](CONTRIBUTING.md#validate-as-you-go). These are treated
as high-priority defects.

Use private reporting instead if the flaw is exploitable against
*something other than this repository* — for example, if an implementation
here reveals a weakness in a downstream system that depends on it.

## Scope

This repository is a research and educational codebase. It is **not**
hardened for adversarial or production use, and nothing here should be
treated as a vetted cryptographic implementation:

- No constant-time or side-channel-resistant guarantees. Timing,
  branching, and memory access depend on input values.
- Circuit construction and simulation execute the parameters they are
  given. Treat oracle definitions, Hamiltonians, and circuit inputs as
  trusted; they are not sandboxed.
- Notebooks and benchmark harnesses are development tooling and are
  outside the scope of a security report.

Reports about dependencies (Qiskit, NumPy, SciPy, Matplotlib) should go to
those projects. If a dependency advisory requires a version constraint
change here, an issue on this repository is the right place for that.
