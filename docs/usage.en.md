# Usage Guide (English)

> [中文文档](usage.md) | English (this file)

## CLI

### List available plugins

```bash
spstpipe list
```

Output:
```
Loaded 6 plugins:
  - cell_communication         ... v0.1.0
  - multi_sample_integration   ... v0.1.0
  - scrna_joint_analysis       ... v0.1.0
  - spatial_domain             ... v0.1.0
  - spatial_variable_genes     ... v0.1.0
  - trajectory                 ... v0.1.0
```

### Run a plugin

```bash
spstpipe run <plugin-name> --input input.h5ad --output result.h5ad
```

## Python API

### Discover plugins

```python
import spstpipe

plugins = spstpipe.discover_plugins("spstpipe.plugins")
print(plugins.keys())
# dict_keys(['spatial_domain', 'cell_communication', ...])
```

### Run a plugin directly

```python
import anndata as ad
from spstpipe import discover_plugins

plugins = discover_plugins("spstpipe.plugins")
plugin_cls = plugins["spatial_domain"]
plugin = plugin_cls()
adata = ad.read_h5ad("input.h5ad")
result = plugin.run(adata)
result.write_h5ad("output.h5ad")
```

### Use plugin's full pipeline (load → preprocess → run → save)

```python
from pathlib import Path
from spstpipe import discover_plugins

plugins = discover_plugins("spstpipe.plugins")
plugin = plugins["spatial_domain"]()

adata = plugin.load([Path("input.h5ad")])
adata = plugin.preprocess(adata)
adata = plugin.run(adata)
plugin.save(adata, Path("output.h5ad"))
```

## Snakemake

Snakefile and rules are thin wrappers around the CLI. See [Snakefile](../Snakefile) and [workflow/rules/](../workflow/rules/).

## Adding a new plugin

1. Create `src/spstpipe/plugins/my_plugin/plugin.py` with a `BasePlugin` subclass
2. Add to `[project.entry-points."spstpipe.plugins"]` in `pyproject.toml`
3. Add tests in `tests/unit/test_my_plugin.py`
4. Run `spstpipe list` to verify

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
