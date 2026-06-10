# 贡献指南（中文）

> 欢迎贡献代码、文档、bug 报告。本项目目标是给空间转录组分析提供**插件化、可扩展、轻依赖**的流水线。

## 开发环境

### 前置

- Python 3.11+
- Git
- 可选：CUDA（如果跑 `cell2location` / `spagcn` 真实方法）

### 本地克隆

```bash
git clone https://github.com/TheSallyGardens/spatial-transcriptome-pipeline.git
cd spatial-transcriptome-pipeline
pip install -e ".[dev]"  # 含 pytest / mypy / ruff / pre-commit
```

### pre-commit 钩子

```bash
pre-commit install  # 一次，之后 commit 自动跑 ruff / 卫生检查
```

## 跑测试

```bash
# 全套（43 个）
pytest

# Windows sandbox 下 7 个 *_save 测试会自动 SKIPPED（pytest-of-{user} 子目录被 DACL 拒绝）
# 36/43 通过 + 7 skipped 是 sandbox 正常状态；CI / Linux 全 43 通过

# 单个测试
pytest tests/unit/test_spatial_domain.py -v

# 覆盖率
pytest --cov=spstpipe
```

### 在 Windows sandbox 下的说明

Codex / Windows sandbox 下 `pytest-of-{user}` 子目录被 DACL 拒绝写入。`conftest.py` 会自动检测并 skip 依赖 `tmp_path` 的测试（7 个 `*_save` 用例）。CI / Linux 不受影响。

## 代码质量

```bash
# 格式化
ruff format src tests

# lint
ruff check src tests

# 严格类型检查
mypy src   # 应该 0 errors
```

CI 跑 `ruff check` + `pytest`（不含 mypy，mypy 留给本地）。

## 添加新插件

每个插件 = 1 个 `BasePlugin` 子类，放到 `src/spstpipe/plugins/<your_plugin>/plugin.py`：

```python
# src/spstpipe/plugins/my_plugin/plugin.py
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "0.1.0"

    def __init__(self, method: str = "default", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError("expect 1 h5ad")
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        # 在这里实现你的算法
        adata.obs["my_result"] = "ok"
        adata.uns["my_plugin_method"] = self.method
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
```

然后在 `pyproject.toml` 的 `[project.entry-points."spstpipe.plugins"]` 表里加一行：

```toml
my_plugin = "spstpipe.plugins.my_plugin.plugin:MyPlugin"
```

测试放 `tests/unit/test_my_plugin.py`，用 `tests.fixtures.synthetic_adata.synthetic_adata()` 造数据。

## 提交规范

- **commit message 默认中文**：`fix: 修 xxx` / `feat: 加 xxx` / `docs: 更新 xxx`
- 一个 commit 只做一件事
- 大改动先开 issue 讨论

## PR 流程

1. fork 仓库
2. 切分支：`git checkout -b codex/your-feature`
3. 改代码 + 加测试
4. `ruff format` + `ruff check` + `mypy src` + `pytest` 全过
5. push + 开 PR
6. 等 CI 通过 + 评审通过

## 联系方式

- GitHub Issues：https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/issues
- 仓库：https://github.com/TheSallyGardens/spatial-transcriptome-pipeline
