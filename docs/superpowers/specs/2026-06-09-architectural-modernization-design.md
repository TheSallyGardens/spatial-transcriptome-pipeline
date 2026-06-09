# Architectural Modernization Design

**Date**: 2026-06-09
**Status**: Draft
**Owner**: Codex (with user delegation)

## 1. Context

`spatial-transcriptome-pipeline` is a Snakemake-based pipeline for 10x Visium and
Stereo-seq data with 6 analysis plugins. The repository was first pushed on
2026-04-25 as a one-shot dump (16 commits, 1 day) and has never been executed,
lacked tests, and contained many latent issues:

- All Python source and the Snakefile are **GBK-encoded** ("mojibake" when
  read as UTF-8). Docstrings and string literals are unreadable.
- No test runs (the only tests import heavy deps like `scanpy` at module top
  level and are not designed to run in CI).
- No type hints, no configuration validation, inconsistent logging
  (`print()` everywhere, no structured output).
- Plugin logic is intermingled with the Snakemake `__snakemake__` glue code,
  making it impossible to invoke a plugin without Snakemake.
- No CI, no pre-commit, no linter, no formatter.
- `README.md` is a partial Chinese draft that did not survive the encoding
  round-trip; `PACKAGES.md` is the only real dependency list.
- The first push to GitHub from this session added only a `.gitignore`.

The user has asked for an **architectural modernization** with maximum
autonomy for the agent.

## 2. Goals (in scope)

1. **Packaging**: Convert each plugin into an installable Python package that
   can run **without** Snakemake.
2. **Unified plugin interface**: All plugins implement the same
   `BasePlugin` contract (`load → preprocess → run → save`) and are
   discoverable via Python entry-points.
3. **Strict type checking** (mypy), **pydantic**-based config validation,
   and **loguru** structured logging.
4. **Testable**: every plugin has unit tests with >=70% line coverage; CI
   runs on every push via GitHub Actions.
5. **Quality gates**: ruff (lint+format), pre-commit, conventional commits,
   semantic-release version metadata.
6. **Fix the encoding rot**: re-encode every source file as UTF-8 with
   proper `from __future__ import annotations` and PEP 263 declarations
   where needed.
7. **Runnable**: the Snakefile invokes the new packages; `snakemake -n`
   on the bundled sample config produces a valid DAG with no missing
   rules.

## 3. Non-goals (out of scope)

- Algorithm re-implementation. We keep the existing analysis logic; we are
  refactoring, not improving the science.
- Cloud execution, S3/GCS backends, SLURM templates.
- Real data fixtures. Tests use synthetic AnnData only.
- Performance tuning (Dask, numba, GPU paths) beyond what the original
  code already required.
- A full Chinese translation of the documentation (English only;
  a separate doc-update task can add i18n later).

## 4. Target Architecture

```
spatial-transcriptome-pipeline/
├── pyproject.toml              # workspace + plugin packages, ruff, mypy
├── README.md                   # rewritten, English, with quickstart
├── CHANGELOG.md
├── src/
│   └── spstpipe/               # core library (replaces scattered scripts)
│       ├── __init__.py
│       ├── core/
│       │   ├── base.py         # BasePlugin abstract class
│       │   ├── config.py       # pydantic models
│       │   ├── io.py           # AnnData load/save helpers
│       │   ├── logging.py      # loguru setup
│       │   └── registry.py     # entry-point based plugin discovery
│       ├── plugins/
│       │   ├── spatial_domain/
│       │   ├── cell_communication/
│       │   ├── trajectory/
│       │   ├── spatial_variable_genes/
│       │   ├── multi_sample_integration/
│       │   └── scrna_joint_analysis/
│       └── cli.py              # typer-based CLI: `spstpipe run <plugin>`
├── workflow/                   # Snakemake glue, only thin wrappers
│   ├── Snakefile
│   └── rules/
├── config/                     # YAML, validated against pydantic
├── envs/                       # conda env files
├── tests/
│   ├── unit/                   # one per plugin
│   ├── integration/            # end-to-end with synthetic data
│   └── fixtures/               # tiny AnnData, sample YAML
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
└── docs/
    ├── usage.md
    └── superpowers/specs/      # design + plan docs
```

### 4.1 Plugin contract

```python
# src/spstpipe/core/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar
import anndata as ad

class BasePlugin(ABC):
    name: ClassVar[str]
    version: ClassVar[str] = "0.1.0"

    @abstractmethod
    def load(self, paths: list[Path]) -> ad.AnnData: ...

    @abstractmethod
    def preprocess(self, adata: ad.AnnData) -> ad.AnnData: ...

    @abstractmethod
    def run(self, adata: ad.AnnData) -> ad.AnnData: ...

    @abstractmethod
    def save(self, adata: ad.AnnData, path: Path) -> None: ...

    def __call__(self, adata: ad.AnnData) -> ad.AnnData:
        return self.run(adata)
```

Each plugin registers itself via `pyproject.toml`:

```toml
[project.entry-points."spstpipe.plugins"]
spatial_domain = "spstpipe.plugins.spatial_domain:SpatialDomainPlugin"
```

### 4.2 Config validation

`config/config.yaml` and per-plugin configs are loaded into a
`PipelineConfig` pydantic model. Invalid configs raise before any
expensive import.

### 4.3 Logging

`spstpipe.core.logging.setup(level="INFO", json=False)` returns a
configured `loguru` logger. Snakemake rules call this once per job;
the CLI uses it as default.

## 5. Migration Strategy (6 phases)

Phase 1 — **Hygiene**
- Convert all source files from GBK → UTF-8 (verify with `file -i` or
  `chardet`).
- Replace `print()` with loguru calls.
- Add `from __future__ import annotations` to all Python files.

Phase 2 — **Core package skeleton**
- Create `pyproject.toml` (workspace), `src/spstpipe/core/{base,config,
  io,logging,registry}.py` with full type hints and unit tests.
- Implement entry-point discovery; prove it with a `test_registry.py`
  using a synthetic plugin in `tests/fixtures/`.

Phase 3 — **Plugin migration** (one at a time, in this order)
1. `spatial_domain` (largest, most central)
2. `cell_communication`
3. `trajectory`
4. `spatial_variable_genes`
5. `multi_sample_integration`
6. `scrna_joint_analysis`

Each migration: TDD — write contract test first, then re-implement the
plugin against `BasePlugin`, then port the original logic verbatim.

Phase 4 — **Snakemake glue**
- Rewrite `workflow/rules/*.smk` to shell out to
  `python -m spstpipe run <plugin>`. Keep one rule per plugin.
- Validate with `snakemake -n` (dry run) on the sample config.

Phase 5 — **CI + pre-commit + quality gates**
- `.github/workflows/ci.yml`: ruff, mypy, pytest with coverage badge.
- `.pre-commit-config.yaml`: ruff-format, ruff-check, trailing-whitespace,
  end-of-file-fixer, check-yaml.
- Coverage threshold 70% (fail build below).

Phase 6 — **Docs**
- Rewrite `README.md` in English (encoding-safe).
- Add a CHANGELOG.
- Update `docs/usage.md` to reflect the new CLI.
- Add architecture diagram (Mermaid) to `docs/`.

## 6. Test Strategy

- **Unit tests** (one per plugin): build tiny synthetic `AnnData`
  (50 spots, 100 genes) with `obs["x"]`, `obs["y"]`, `obs["platform"]`,
  run plugin, assert expected `obs` / `uns` keys.
- **Contract test** (`tests/test_plugin_contract.py`): every registered
  plugin satisfies the `BasePlugin` protocol (has `name`, implements
  the 4 methods, returns `AnnData`).
- **Config test** (`tests/test_config.py`): valid YAML passes; invalid
  YAML raises `pydantic.ValidationError` with the expected field name.
- **CLI test** (`tests/test_cli.py`): `spstpipe run spatial_domain
  --input fixture.h5ad --output out.h5ad` exits 0 and produces a file.
- **Smoke test** (`tests/test_end_to_end.py`): run
  `snakemake -n` from a clean checkout and assert 0 exit.

Heavy scientific deps (`torch`, `stlearn`, `BayesSpace`) are imported
**lazily** inside plugin methods and the corresponding tests are
**skipped** if the import fails, with an explanatory `pytest.skip`
message. The CI matrix is split: a "fast" job (no torch) and a "full"
job (installs all extras).

## 7. Risks

- **Encoding migration risk**: A misdecoded file becomes silent garbage.
  Mitigation: hash-check each file before/after, keep a backup branch
  `backup/gbk-original` for the first push, run a smoke import on every
  migrated file.
- **Snakemake behavior change**: the new thin rules may produce
  different output paths. Mitigation: keep output paths identical to
  the originals so users do not need to re-run anything.
- **Coverage threshold too high**: 70% is aspirational for the
  scientific code. Mitigation: start at 50% and ratchet to 70% in
  phase 5 only.
- **CI runtime**: torch+scanpy CI can take 10+ min. Mitigation: cache
  pip, use `pytest -x --no-cov` for the fast job, only run coverage
  in the full job.

## 8. Acceptance Criteria

- `pip install -e .` works in a clean venv.
- `spstpipe list` prints all 6 plugins.
- `spstpipe run spatial_domain` succeeds on the fixture data.
- `snakemake -n` reports a non-empty DAG.
- `pytest --cov=spstpipe` reports >= 70% coverage.
- `mypy src` reports 0 errors.
- `ruff check` and `ruff format --check` pass.
- CI workflow on GitHub Actions is green on the resulting commit.
- README renders correctly (no mojibake).

## 9. Out of Band

- We will not run Snakemake against real data. The acceptance test
  is the dry run.
- The push to GitHub is the **only** external surface. All work
  happens in the local repository and the `main` branch.
