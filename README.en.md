# spstpipe · Spatial Transcriptome Analysis Pipeline

> Plugin-based spatial transcriptomics analysis pipeline built on Snakemake + Python.
> Supports 10x Visium and Stereo-seq data.

[中文文档](README.md) | English (this file)

[![CI](https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Features

- **Plugin architecture**: 6 built-in analysis plugins, individually callable and testable
- **Unified interface**: All plugins implement the `BasePlugin` abstraction (load / preprocess / run / save)
- **Strongly typed config**: `pydantic` validates YAML, fail fast
- **CI-ready**: GitHub Actions auto-runs lint + unit tests
- **Works without Snakemake**: `spstpipe run spatial_domain ...` CLI

## Supported Analysis Modules

| Plugin | Default Method | Description |
|------|---------|------|
| `spatial_domain` | spectral_clustering | Identify contiguous spatial regions in tissue |
| `cell_communication` | placeholder | Cell-cell communication (CellChat / NicheNet / Squidpy) |
| `trajectory` | paga | Developmental trajectory inference (PAGA / Monocle) |
| `spatial_variable_genes` | morans_i | Spatially variable genes (Moran's I / SPARK / LISA) |
| `multi_sample_integration` | harmony | Multi-sample integration (Harmony / BBKNN / Liger) |
| `scrna_joint_analysis` | seurat | scRNA label transfer (Seurat / Cell2location / SpatialGLUE) |

## Quick Start

```bash
# 1) Install
pip install spstpipe

# 2) List available plugins
spstpipe list

# 3) Run a plugin
spstpipe run spatial_domain --input data.h5ad --output result.h5ad
```

### Run the end-to-end demo (no real data needed)

```bash
python examples/synthetic_end_to_end.py
```

## Documentation

- [中文 README](README.md) — Chinese README
- [docs/usage.md](docs/usage.md) — CLI / Python API / Snakemake usage
- [docs/API.md](docs/API.md) — Public API (frozen since 1.0.0)
- [docs/ROADMAP.md](docs/ROADMAP.md) — Project roadmap
- [docs/PUBLISH.md](docs/PUBLISH.md) — How to publish to PyPI
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute

## Architecture

```
┌─────────────────┐
│   CLI / Snakefile │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ spstpipe.core.BasePlugin (abstract) │
└────────┬────────┘
         │
         v
┌────────────────────────────────────────┐
│ 6 built-in plugins (entry-point discovery) │
│ - spatial_domain                       │
│ - cell_communication                  │
│ - trajectory                          │
│ - spatial_variable_genes              │
│ - multi_sample_integration            │
│ - scrna_joint_analysis                │
└────────────────────────────────────────┘
```

## License

MIT — see [LICENSE](LICENSE).
