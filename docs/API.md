# 公共 API（冻结）

> **API 版本**：`1.0`（自 `1.0.0` 起冻结，签名不再破坏性变化）
> **包版本**：`1.0.0`
> **冻结日期**：2026-06-10

## 稳定 API

以下 API 在 1.x 范围内**保证向后兼容**（签名不变，行为不变）。
破坏性变更只会发生在 2.0.0。

### `spstpipe.__version__`

```python
>>> import spstpipe
>>> spstpipe.__version__
"1.0.0"
```

### `spstpipe.__api_version__`

```python
>>> spstpipe.__api_version__
"1.0"
```

只增不减的 API 版本号。1.x 范围内不变。

### `spstpipe.BasePlugin`

```python
from spstpipe import BasePlugin

class MyPlugin(BasePlugin):
    name: ClassVar[str] = "my_plugin"
    version: ClassVar[str] = "1.0.0"

    def load(self, paths: list[Path]) -> ad.AnnData: ...
    def preprocess(self, adata: ad.AnnData) -> ad.AnnData: ...
    def run(self, adata: ad.AnnData) -> ad.AnnData: ...
    def save(self, adata: ad.AnnData, path: Path) -> None: ...
```

**类属性**（必须由子类覆盖）：
- `name: ClassVar[str]` — 插件名（小写、下划线分隔）
- `version: ClassVar[str]` — 插件版本

**实例方法**（必须由子类实现）：
- `load(paths: list[Path]) -> ad.AnnData`
- `preprocess(adata: ad.AnnData) -> ad.AnnData`
- `run(adata: ad.AnnData) -> ad.AnnData`
- `save(adata: ad.AnnData, path: Path) -> None`

**便利方法**（由基类提供）：
- `__call__(adata) -> ad.AnnData` — 等价于 `run(adata)`
- `__repr__() -> str` — `<ClassName name='' version=''>`

### `spstpipe.discover_plugins(group: str) -> dict[str, type[BasePlugin]]`

通过 entry-point 发现插件。

```python
>>> from spstpipe import discover_plugins
>>> plugins = discover_plugins("spstpipe.plugins")
>>> "spatial_domain" in plugins
True
```

## 内置插件

| 插件 | name | 默认方法 | 真方法（需 optional deps） |
|---|---|---|---|
| `SpatialDomainPlugin` | `spatial_domain` | spectral_clustering | leiden (squidpy) |
| `SpatialVariableGenesPlugin` | `spatial_variable_genes` | morans_i_placeholder | morans_i_squidpy |
| `CellCommunicationPlugin` | `cell_communication` | placeholder | squidpy_ligrec |
| `TrajectoryPlugin` | `trajectory` | paga_placeholder | paga_scanpy |
| `MultiSampleIntegrationPlugin` | `multi_sample_integration` | harmony_placeholder | harmony_scanpy |
| `ScRNAJointAnalysisPlugin` | `scrna_joint_analysis` | seurat_placeholder | seurat_scanpy_ingest |

## 实验性 API

以下 API 在 1.x 内**可能**改变，**不**保证稳定。如果你要写自己的插件，建议只用稳定 API。

- `spstpipe.core.config.*` — pydantic 配置类（用于未来 CLI 参数校验，1.1 可能重写）
- `spstpipe.core.logging.setup()` — loguru 配置入口（签名稳定，但参数可能加）
- `spstpipe.core.io.load_anndata / save_anndata` — 稳定，但未来可能加 `format=` 参数

## 内部（不导出）

- `spstpipe.plugins.*.algorithms` — 算法实现细节，**不**是公共 API
- `spstpipe.cli` — CLI 内部，可能改

## 升级路径

从 0.x 升到 1.0：

- `from spstpipe.core.base import BasePlugin` 改为 `from spstpipe import BasePlugin`（更短）
- 插件 `version` 从 `"0.1.0"` 升到 `"1.0.0"`
- `__version__` 从 `"0.1.0"` 变 `"1.0.0"`（破坏性，仅一项目录）
- 算法入口从 `from spstpipe.plugins.X.run import ...` 改为 `from spstpipe.plugins.X.algorithms import ...`
