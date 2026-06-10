# 使用说明

## CLI 用法

### `spstpipe list`

列出所有已注册的插件。

```bash
$ spstpipe list
已注册 6 个插件：
  - cell_communication             spstpipe.plugins.cell_communication.plugin:CellCommunicationPlugin  v0.1.0
  - multi_sample_integration       spstpipe.plugins.multi_sample_integration.plugin:MultiSampleIntegrationPlugin  v0.1.0
  - scrna_joint_analysis           spstpipe.plugins.scrna_joint_analysis.plugin:ScRNAJointAnalysisPlugin  v0.1.0
  - spatial_domain                 spstpipe.plugins.spatial_domain.plugin:SpatialDomainPlugin  v0.1.0
  - spatial_variable_genes         spstpipe.plugins.spatial_variable_genes.plugin:SpatialVariableGenesPlugin  v0.1.0
  - trajectory                     spstpipe.plugins.trajectory.plugin:TrajectoryPlugin  v0.1.0
```

### `spstpipe run <plugin>`

跑指定插件。

```bash
spstpipe run <plugin> --input <input.h5ad> --output <output.h5ad>
```

可选参数（未来）：
- `--method` 覆盖插件默认方法

## Python API

### 基础用法

```python
import anndata as ad
from spstpipe.plugins.spatial_domain import SpatialDomainPlugin

adata = ad.read_h5ad("data/sample1.h5ad")
plugin = SpatialDomainPlugin()
result = plugin(adata)  # 等价于 plugin.run(adata)
print(result.obs["spatial_domain"].value_counts())
```

### 自定义参数

```python
plugin = SpatialDomainPlugin(method="spectral_clustering", resolution=0.8)
result = plugin.run(adata)
```

### 完整流水线（load → preprocess → run → save）

```python
from pathlib import Path
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.spatial_domain import SpatialDomainPlugin

adata = load_anndata("data/sample1.h5ad")
plugin = SpatialDomainPlugin()
preprocessed = plugin.preprocess(adata)
result = plugin.run(preprocessed)
save_anndata(result, "results/spatial_domain/sample1.h5ad")
```

## 通过 Snakemake 跑

### Dry run（看 DAG 不真跑）

```bash
snakemake -n
```

### 完整跑

```bash
snakemake --use-conda -j 4
```

### 跑单个插件

```bash
snakemake run_spatial_domain
```

## 配置文件

### `config/config.yaml`

```yaml
project:
  name: "my_project"
  author: "alice"
  date: "2026-06-09"

mamba:
  env_dir: "envs"
  create_env: true

plugins:
  - name: spatial_domain
    enabled: true
    method: spectral_clustering
    params:
      resolution: 0.5
```

### `config/samples.yaml`

```yaml
samples:
  - id: sample1
    platform: 10x_visium
    input_dir: "data/sample1"
    config:
      min_genes: 200
      min_cells: 50
```

## 添加新插件

### 1. 创建插件目录

```
src/spstpipe/plugins/my_plugin/
├── __init__.py
├── plugin.py
└── algorithms.py
```

### 2. 实现 `plugin.py`

```python
from __future__ import annotations
from pathlib import Path
import anndata as ad
from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "0.1.0"

    def __init__(self, method: str = "default", **params):
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        # 你的算法
        adata.obs["my_result"] = ...
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
```

### 3. 在 `pyproject.toml` 注册 entry-point

```toml
[project.entry-points."spstpipe.plugins"]
my_plugin = "spstpipe.plugins.my_plugin.plugin:MyPlugin"
```

### 4. 写测试

```python
# tests/unit/test_my_plugin.py

> [English Version](usage.en.md) | 简体中文（本文件）
from spstpipe.plugins.my_plugin.plugin import MyPlugin


def test_my_plugin_能_跑():
    from tests.fixtures.synthetic_adata import synthetic_adata
    a = synthetic_adata()
    out = MyPlugin().run(a)
    assert "my_result" in out.obs.columns
```

### 5. 跑测试

```bash
pytest tests/unit/test_my_plugin.py
```
