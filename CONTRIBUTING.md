# Contributing to Quantum Foundry

Thanks for considering a contribution. This project favors rigor over
speed: every construction is expected to be verified, not just believed,
before it's trusted by anything built on top of it. Documentation, tests,
benchmarks, reproducible examples, CI, static analysis, and versioning are
part of the expected engineering standard.

## Development setup

```bash
# Install uv if you don't have it: https://docs.astral.sh/uv/
uv sync

uv run pytest              # full suite (slow-marked tests excluded)
uv run pytest -m slow      # the excluded slow tests, explicitly
uv run ruff check .        # lint
uv run mypy .               # type check
```

All three (`pytest`, `ruff`, `mypy`) run in CI on every pull request
(see `.github/workflows/ci.yml`) and are expected to be clean before a
PR merges. CI runs them on Python 3.12, 3.13, and 3.14 — the full range
`pyproject.toml` declares support for — so a change that depends on a
version-specific behavior fails on the versions that lack it. CI
additionally executes every notebook in the repository
(`uv run python scripts/execute_notebooks.py`), so a notebook that raises
fails the build; run it locally if you have touched one.

`uv run pytest --cov` enforces a coverage floor (`fail_under` in
`pyproject.toml`), measured over the algorithm code rather than the test
files. New code is expected to arrive with tests, so the floor should rise
over time; lowering it to make a build pass is the wrong fix.

## Adding a new algorithm

Every algorithm begins with an RFC under [docs/rfcs/](docs/rfcs/),
numbered sequentially, covering: Vision, Why This Should Exist, Prior
Art, Architecture, Technology Choices, Milestones, Explicit Non-goals,
and Stretch Goals. Look at any existing RFC (e.g.
[docs/rfcs/0004-grovers-algorithm.md](docs/rfcs/0004-grovers-algorithm.md))
for the expected shape before opening a new one.

Once an RFC is accepted, the algorithm lives under
`algorithms/<name>/` following the standard layout:

```text
algorithms/<name>/
  README.md          # Motivation, quick start, current status
  math.md            # Level 1: mathematical foundations
  paper.md           # Level 2: circuit derivation
  oracles.py         # Oracle (or Problem/Hamiltonian) interface + implementation(s)
  circuit.py         # Circuit construction
  execution.py       # Executor interface + implementation(s)
  implementation.py  # Level 3: end-to-end software implementation
  benchmark.py       # Performance / resource benchmarks
  visualization.py   # Circuit and result visualization
  tests/             # Test suite
  notebooks/         # Exploratory / demo notebooks
  references.bib     # Citations
```

`oracles.py` and `execution.py` are `Protocol`-based seams by
convention — this is what lets a follow-up RFC extend an algorithm
(e.g. a gate-decomposed oracle, a hardware-aware executor) without
touching its already-tested core logic. See
[algorithms/README.md](algorithms/README.md) for the full pattern,
documentation levels, and maturity model (`experimental` → `contrib` →
`incubating` → `reference`) each algorithm progresses through.

If your contribution doesn't yet meet the bar for `experimental`
status (e.g. it's missing tests or documentation), it belongs under
[contrib/](contrib/) instead — see that directory's README.

## Validate as you go

Every non-trivial gate or circuit construction should be verified
empirically (via `Statevector`/`Operator` equivalence against a
hand-derived or brute-force classical result) before being trusted or
composed further, and before anything else is built on top of it. This
project's history includes several real bugs — a modular-adder sign
error, a global-phase convention that was fine for one use but wrong
under a different one, a phase-estimation bit-order mistake — that were
caught exactly this way, by checking against theory rather than
assuming a derivation was correct. Don't skip this step because a
derivation "looks right."

## Pull requests

- Keep the scope of a PR matched to one RFC milestone (or one
  well-defined stretch goal) where practical — large, multi-purpose PRs
  are harder to review and harder to bisect later.
- Update the relevant `math.md`/`paper.md`/`README.md` alongside code
  changes; documentation that describes what the code *used to* do is
  worse than no documentation.
- New capability needs new tests. A bug fix should include a test that
  would have caught the bug.
- Don't refactor already-tested, working code as a side effect of an
  unrelated change — prefer adding a new sibling function/module and
  documenting the relationship, unless the refactor itself is the point
  of the PR.

## Versioning

An RFC's milestone numbers (`v0.1` through `v1.0`) track that RFC's own
scope — `v1.0` means its work is complete and folded into the public
release — and each RFC runs that scale independently. They are not the
package version. `version` in `pyproject.toml` follows SemVer and tracks
API stability instead, which is a separate question: it stays below
`1.0.0` while every algorithm sits at `experimental`, a tier that makes no
API-stability promise. See the maturity model in
[algorithms/README.md](algorithms/README.md) for what each tier does
promise.

## Code of conduct

Be respectful and constructive. Disagreements about technical approach
are welcome; personal attacks are not.
