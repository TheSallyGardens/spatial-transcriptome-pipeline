# 架构现代化重构实施计划

> **给 Agent worker 看：** 必须配合 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 来逐条执行。任务用 `- [ ]` 复选框跟踪进度。

**目标：** 把这套 GBK 乱码、没测试、与 Snakemake 强耦合的流水线，改造成类型化、可打包、可测试、有 CI 的 Python 项目；Snakemake 只剩薄薄一层调度壳。

**架构：** 把 `plugins/*/run.py` 和 `workflow/scripts/*.py` 里的所有业务逻辑搬到 `spstpipe` 这个 Python 包里，统一通过 `BasePlugin` 抽象类 + entry-point 机制注册。Snakemake rules 退化成调 `python -m spstpipe run <plugin>` 的薄壳。测试用纯 Python + 合成 AnnData；torch / stereopy / stlearn 这种重依赖用懒加载，缺包就 `pytest.skip`。

**技术栈：** Python 3.11+、pydantic v2、loguru、typer、mypy --strict、ruff、pytest + pytest-cov、GitHub Actions、Snakemake 8+。

**配套设计文档：** `docs/superpowers/specs/2026-06-09-architectural-modernization-design.md`

---

## 一、文件结构

### 1.1 新建

```
pyproject.toml                              # workspace + spstpipe 包 + lint/test 配置
src/spstpipe/__init__.py
src/spstpipe/py.typed                       # PEP 561 标记
src/spstpipe/core/__init__.py
src/spstpipe/core/base.py                   # BasePlugin 抽象类
src/spstpipe/core/config.py                 # pydantic PipelineConfig
src/spstpipe/core/io.py                     # AnnData 读写工具
src/spstpipe/core/logging.py                # loguru 初始化
src/spstpipe/core/registry.py               # entry-point 插件发现
src/spstpipe/core/errors.py                 # 异常体系
src/spstpipe/plugins/__init__.py
src/spstpipe/plugins/spatial_domain/__init__.py
src/spstpipe/plugins/spatial_domain/plugin.py
src/spstpipe/plugins/spatial_domain/algorithms.py
src/spstpipe/plugins/cell_communication/__init__.py
src/spstpipe/plugins/cell_communication/plugin.py
src/spstpipe/plugins/cell_communication/algorithms.py
src/spstpipe/plugins/trajectory/__init__.py
src/spstpipe/plugins/trajectory/plugin.py
src/spstpipe/plugins/trajectory/algorithms.py
src/spstpipe/plugins/spatial_variable_genes/__init__.py
src/spstpipe/plugins/spatial_variable_genes/plugin.py
src/spstpipe/plugins/spatial_variable_genes/algorithms.py
src/spstpipe/plugins/multi_sample_integration/__init__.py
src/spstpipe/plugins/multi_sample_integration/plugin.py
src/spstpipe/plugins/multi_sample_integration/algorithms.py
src/spstpipe/plugins/scrna_joint_analysis/__init__.py
src/spstpipe/plugins/scrna_joint_analysis/plugin.py
src/spstpipe/plugins/scrna_joint_analysis/algorithms.py
src/spstpipe/cli.py                         # typer CLI 入口
tests/__init__.py
tests/conftest.py
tests/test_plugin_contract.py
tests/test_registry.py
tests/test_config.py
tests/test_io.py
tests/test_logging.py
tests/fixtures/__init__.py
tests/fixtures/synthetic_adata.py           # 构造小 AnnData
tests/fixtures/synthetic_plugin/            # registry 测试用的假插件
tests/unit/test_spatial_domain.py
tests/unit/test_cell_communication.py
tests/unit/test_trajectory.py
tests/unit/test_spatial_variable_genes.py
tests/unit/test_multi_sample_integration.py
tests/unit/test_scrna_joint_analysis.py
tests/integration/test_end_to_end.py
.github/workflows/ci.yml
.pre-commit-config.yaml
mypy.ini
docs/usage.md                                # 用 UTF-8 重写
README.md                                    # 用 UTF-8 重写
CHANGELOG.md
```

### 1.2 保留但改 UTF-8 + 内容重写

```
config/config.yaml
config/samples.yaml
envs/scanpy.yaml
envs/r-seurat.yaml
envs/spagcn.yaml
workflow/Snakefile
workflow/rules/basic_analysis.smk
workflow/rules/cell_communication.smk
workflow/rules/multi_sample_integration.smk
workflow/rules/preprocessing.smk
workflow/rules/report.smk
workflow/rules/scRNA_joint_analysis.smk
workflow/rules/spatial_domain.smk
workflow/rules/spatial_variable_genes.smk
workflow/rules/trajectory.smk
workflow/rules/visualization.smk
PACKAGES.md
```

### 1.3 迁移完成后删除

```
plugins/spatial_domain/run.py
plugins/spatial_domain/config.yaml
plugins/cell_communication/run.py
plugins/cell_communication/config.yaml
plugins/trajectory/run.py
plugins/trajectory/config.yaml
plugins/spatial_variable_genes/run.py
plugins/spatial_variable_genes/config.yaml
plugins/multi_sample_integration/run.py
plugins/multi_sample_integration/config.yaml
plugins/scRNA_joint_analysis/run.py
plugins/scRNA_joint_analysis/config.yaml
workflow/scripts/load_data.py                # 逻辑搬到 spstpipe.core.io + 各 plugin
workflow/scripts/preprocessing.py            # 逻辑搬到 spstpipe.core
workflow/scripts/clustering.py
workflow/scripts/annotation.py
workflow/scripts/visualization.py
workflow/scripts/report.py
tests/test_load_data.py
tests/test_end_to_end.py                     # 搬到 tests/integration/
```

---

## 二、Phase 1：编码与基础卫生

### Task 1.1：把所有源文件统一到 UTF-8

**涉及文件：** `plugins/`、`workflow/`、`tests/`、`envs/`、`config/` 下所有 `*.py / *.smk / *.md / *.yaml`，以及仓库根的 `*.md`。

- [ ] 步骤 1：检测当前每个文件的编码
  ```bash
  python -c "import pathlib, chardet
  for p in pathlib.Path('.').rglob('*'):
      if p.is_file() and p.suffix in {'.py','.smk','.md','.yaml'} and '.git' not in p.parts:
          print(p, chardet.detect(p.read_bytes())['encoding'])"
  ```
- [ ] 步骤 2：把所有 GBK 编码的文件转成 UTF-8（二进制 / 已是 utf-8 / ASCII 的跳过）
  ```python
  # scripts/reencode.py —— 一次性脚本
  import pathlib
  GBK_FILES = [上面检测出来的列表]
  for p in GBK_FILES:
      raw = p.read_bytes()
      p.write_bytes(raw.decode("gbk").encode("utf-8"))
  ```
- [ ] 步骤 3：验证没有乱码残留
  ```bash
  rg -l "" -g "!*.{png,jpg,h5ad,h5,rds}" | xargs -I{} python -c "import sys; open(sys.argv[1],'rb').read().decode('utf-8')" {} 2>&1 | head
  ```
  （应该没有输出）
- [ ] 步骤 4：提交
  ```bash
  git add -A
  git commit -m "chore: 把源文件从 GBK 统一为 UTF-8"
  ```

### Task 1.2：给所有 Python 文件加 `from __future__ import annotations`

- [ ] 步骤 1：写脚本批量加 import
  ```python
  # scripts/add_future.py
  import pathlib
  for p in pathlib.Path('.').rglob('*.py'):
      if '.git' in p.parts: continue
      text = p.read_text(encoding="utf-8")
      if "from __future__ import annotations" not in text:
          p.write_text("from __future__ import annotations\n\n" + text, encoding="utf-8")
  ```
- [ ] 步骤 2：跑脚本；提交
  ```bash
  git add -A
  git commit -m "chore: 给所有 Python 文件加 from __future__ import annotations"
  ```

### Task 1.3：把 `print()` 全替换成 `loguru.logger`

- [ ] 步骤 1：列出所有 `print(` 调用
  ```bash
  rg -n "^\s*print\(" -t python
  ```
- [ ] 步骤 2：每个 print 替换成 `logger.info(...)`（或 `.warning / .error`）
- [ ] 步骤 3：提交
  ```bash
  git commit -am "chore: 把 print() 替换成 loguru logger"
  ```

---

## 三、Phase 2：核心包骨架（TDD）

### Task 2.1：项目脚手架

**涉及文件：**
- 新建：`pyproject.toml`
- 新建：`src/spstpipe/__init__.py`
- 新建：`src/spstpipe/py.typed`
- 新建：`mypy.ini`
- 新建：`.pre-commit-config.yaml`
- 新建：`tests/__init__.py`
- 新建：`tests/conftest.py`

- [ ] 步骤 1：写 `pyproject.toml`（见附录 A）
- [ ] 步骤 2：写 `mypy.ini`（strict、python 3.11、warn_unused_ignores）
- [ ] 步骤 3：写空 `src/spstpipe/__init__.py`，版本 `0.1.0`
- [ ] 步骤 4：写空 `src/spstpipe/py.typed`（PEP 561 标记）
- [ ] 步骤 5：写 `tests/conftest.py`，把 `src/` 加进 sys.path
- [ ] 步骤 6：跑 `pip install -e ".[dev]"` + `pytest --collect-only`，期望 0 个测试 0 个错
- [ ] 步骤 7：提交
  ```bash
  git add pyproject.toml mypy.ini src tests
  git commit -m "feat: 搭建 spstpipe 包和开发工具链"
  ```

### Task 2.2：BasePlugin 抽象类

**涉及文件：**
- 新建：`src/spstpipe/core/base.py`
- 新建：`src/spstpipe/core/__init__.py`
- 测试：`tests/unit/test_base.py`

- [ ] 步骤 1：先写失败测试
  ```python
  # tests/unit/test_base.py
  from __future__ import annotations
  from abc import ABC
  from spstpipe.core.base import BasePlugin

  def test_base_plugin_是抽象类():
      assert issubclass(BasePlugin, ABC)
      for method in ("load", "preprocess", "run", "save"):
          assert hasattr(BasePlugin, method)
  ```
- [ ] 步骤 2：跑测试，期望 `ImportError` 或 `AttributeError`
- [ ] 步骤 3：实现 `BasePlugin`（4 个抽象方法、`name`/`version` 类变量、`__call__` 便捷方法）
- [ ] 步骤 4：跑 `pytest tests/unit/test_base.py -v`，期望通过
- [ ] 步骤 5：提交
  ```bash
  git add src tests
  git commit -m "feat(core): 加 BasePlugin 抽象类"
  ```

### Task 2.3：插件注册表（entry-point 发现）

**涉及文件：**
- 新建：`src/spstpipe/core/registry.py`
- 测试：`tests/unit/test_registry.py`
- 测试：`tests/fixtures/synthetic_plugin/__init__.py`
- 测试：`tests/fixtures/synthetic_plugin/plugin.py`

- [ ] 步骤 1：写一个假插件（`BasePlugin` 的具体子类）
  ```python
  # tests/fixtures/synthetic_plugin/plugin.py
  from __future__ import annotations
  from pathlib import Path
  import anndata as ad
  from spstpipe.core.base import BasePlugin

  class SyntheticPlugin(BasePlugin):
      name = "synthetic"
      def load(self, paths): ...
      def preprocess(self, adata): return adata
      def run(self, adata): return adata
      def save(self, adata, path): path.write_text("ok")
  ```
- [ ] 步骤 2：写失败测试
  ```python
  def test_注册表能发现假插件(monkeypatch):
      from spstpipe.core.registry import discover_plugins
      plugins = discover_plugins(group="spstpipe.test_plugins")
      assert "synthetic" in plugins
  ```
- [ ] 步骤 3：实现 `discover_plugins(group)`，底层用 `importlib.metadata.entry_points`
- [ ] 步骤 4：跑测试，期望通过
- [ ] 步骤 5：在 `pyproject.toml` 注册假插件
  ```toml
  [project.entry-points."spstpipe.test_plugins"]
  synthetic = "tests.fixtures.synthetic_plugin.plugin:SyntheticPlugin"
  ```
- [ ] 步骤 6：提交
  ```bash
  git commit -am "feat(core): 加 entry-point 插件注册表"
  ```

### Task 2.4：pydantic 配置模型

**涉及文件：**
- 新建：`src/spstpipe/core/config.py`
- 测试：`tests/unit/test_config.py`

- [ ] 步骤 1：失败测试
  ```python
  def test_最小YAML能通过():
      from spstpipe.core.config import PipelineConfig
      cfg = PipelineConfig.model_validate({"samples": []})
      assert cfg.samples == []

  def test_缺samples字段要报错():
      from pydantic import ValidationError
      from spstpipe.core.config import PipelineConfig
      import pytest
      with pytest.raises(ValidationError):
          PipelineConfig.model_validate({})
  ```
- [ ] 步骤 2：实现 `PipelineConfig`、`SampleConfig`、`PluginConfig`（pydantic v2）
- [ ] 步骤 3：跑测试，期望通过
- [ ] 步骤 4：提交
  ```bash
  git commit -am "feat(core): 加 pydantic PipelineConfig"
  ```

### Task 2.5：IO 工具

**涉及文件：**
- 新建：`src/spstpipe/core/io.py`
- 测试：`tests/unit/test_io.py`
- 测试：`tests/fixtures/synthetic_adata.py`

- [ ] 步骤 1：写 `synthetic_adata()` 工厂（50 个 spot × 100 个基因，带 `obs["x"]`、`obs["y"]`、`obs["platform"]`、`obsm["spatial"]`）
- [ ] 步骤 2：失败测试
  ```python
  def test_io_能往返(tmp_path):
      from spstpipe.core.io import load_anndata, save_anndata
      from tests.fixtures.synthetic_adata import synthetic_adata
      a = synthetic_adata()
      p = tmp_path / "x.h5ad"
      save_anndata(a, p)
      b = load_anndata(p)
      assert b.shape == a.shape
  ```
- [ ] 步骤 3：实现 `load_anndata` / `save_anndata`（基于 `ad.read_h5ad` / `write_h5ad`）
- [ ] 步骤 4：跑测试，期望通过
- [ ] 步骤 5：提交
  ```bash
  git commit -am "feat(core): 加 AnnData IO 工具"
  ```

### Task 2.6：日志初始化

**涉及文件：**
- 新建：`src/spstpipe/core/logging.py`
- 测试：`tests/unit/test_logging.py`

- [ ] 步骤 1：失败测试
  ```python
  def test_logging_setup_幂等():
      from spstpipe.core.logging import setup
      log1 = setup()
      log2 = setup()
      assert log1 is log2
  ```
- [ ] 步骤 2：用 loguru 实现（只配置一次，返回绑定的 logger）
- [ ] 步骤 3：跑测试，期望通过
- [ ] 步骤 4：提交
  ```bash
  git commit -am "feat(core): 加 loguru 日志初始化"
  ```

### Task 2.7：CLI 入口

**涉及文件：**
- 新建：`src/spstpipe/cli.py`
- 测试：`tests/unit/test_cli.py`

- [ ] 步骤 1：失败测试
  ```python
  from typer.testing import CliRunner
  from spstpipe.cli import app

  def test_cli_list_能列出已知插件():
      runner = CliRunner()
      result = runner.invoke(app, ["list"])
      assert result.exit_code == 0
      assert "spatial_domain" in result.stdout
  ```
- [ ] 步骤 2：实现 typer app：`list` 和 `run <plugin>` 两个子命令
- [ ] 步骤 3：跑测试，期望通过
- [ ] 步骤 4：提交
  ```bash
  git commit -am "feat(cli): 加 typer CLI（list / run）"
  ```

### Task 2.8：插件契约测试

**涉及文件：**
- 新建：`tests/test_plugin_contract.py`

- [ ] 步骤 1：写测试
  ```python
  from spstpipe.core.base import BasePlugin
  from spstpipe.core.registry import discover_plugins

  def test_所有注册的插件都满足契约():
      plugins = discover_plugins(group="spstpipe.plugins")
      assert len(plugins) >= 6, "期望至少有 6 个生产插件"
      for name, cls in plugins.items():
          assert issubclass(cls, BasePlugin)
          for m in ("load", "preprocess", "run", "save"):
              assert callable(getattr(cls, m)), f"{name} 缺方法 {m}"
  ```
- [ ] 步骤 2：跑测试，期望失败（还没插件注册）
- [ ] 步骤 3：提交（这个测试当防护栏，Phase 3 完成后会自动通过）
  ```bash
  git commit -am "test: 加插件契约测试（TDD 防护栏）"
  ```

---

## 四、Phase 3：六个插件逐个迁移（TDD）

每个插件的迁移模式都一样：**先写失败测试 → 实现 `XxxPlugin` → 把 `plugins/<name>/run.py` 的算法原样搬到 `algorithms.py` → 注册到 entry-point → 通过 → 提交**。下面以 `spatial_domain` 为模板详写，后五个只列差异。

### Task 3.1：spatial_domain（模板）

**涉及文件：**
- 新建：`src/spstpipe/plugins/spatial_domain/plugin.py`
- 新建：`src/spstpipe/plugins/spatial_domain/algorithms.py`
- 新建：`src/spstpipe/plugins/spatial_domain/__init__.py`
- 测试：`tests/unit/test_spatial_domain.py`

- [ ] 步骤 1：写失败测试
  ```python
  def test_spatial_domain_已注册():
      from spstpipe.core.registry import discover_plugins
      p = discover_plugins(group="spstpipe.plugins")
      assert "spatial_domain" in p

  def test_spatial_domain_默认方法会加obs列():
      from spstpipe.plugins.spatial_domain.plugin import SpatialDomainPlugin
      from tests.fixtures.synthetic_adata import synthetic_adata
      p = SpatialDomainPlugin()
      a = synthetic_adata()
      out = p.run(a)
      assert "spatial_domain" in out.obs.columns
  ```
- [ ] 步骤 2：实现 `SpatialDomainPlugin`（默认方法 = `spectral_clustering` 兜底；spagcn 用懒加载 torch）
- [ ] 步骤 3：把 `calculate_adj_matrix`、`prep_spagnn`、`train_spagnn`、`run_spectral_clustering`、`run_bayespace`（占位）、`run_stlearn`（懒加载）原样搬到 `algorithms.py`
- [ ] 步骤 4：在 `pyproject.toml` 注册 entry-point
- [ ] 步骤 5：跑 `pytest tests/unit/test_spatial_domain.py -v`，期望通过
- [ ] 步骤 6：跑 `pytest tests/test_plugin_contract.py`，期望通过
- [ ] 步骤 7：提交
  ```bash
  git commit -am "feat(plugin): 把 spatial_domain 迁到 spstpipe"
  ```

### Task 3.2：cell_communication

- 默认方法：`squidpy`（如已装），否则占位
- CellChat / NicheNet 懒加载 + 缺包 pytest.skip
- 提交：
  ```bash
  git commit -am "feat(plugin): 把 cell_communication 迁到 spstpipe"
  ```

### Task 3.3：trajectory

- 默认方法：PAGA（scanpy 原生）
- 提交：
  ```bash
  git commit -am "feat(plugin): 把 trajectory 迁到 spstpipe"
  ```

### Task 3.4：spatial_variable_genes

- 默认方法：Moran's I（squidpy 原生）
- 提交：
  ```bash
  git commit -am "feat(plugin): 把 spatial_variable_genes 迁到 spstpipe"
  ```

### Task 3.5：multi_sample_integration

- 默认方法：Harmony（懒加载）
- 提交：
  ```bash
  git commit -am "feat(plugin): 把 multi_sample_integration 迁到 spstpipe"
  ```

### Task 3.6：scrna_joint_analysis

- 默认方法：Seurat anchor transfer（走 Rscript 桥接），否则占位
- 提交：
  ```bash
  git commit -am "feat(plugin): 把 scrna_joint_analysis 迁到 spstpipe"
  ```

---

## 五、Phase 4：Snakemake 改成薄壳

### Task 4.1：重写 `Snakefile`

**涉及文件：** `workflow/Snakefile`

- [ ] 步骤 1：先把文件 reencode 成 UTF-8
- [ ] 步骤 2：重写成下面这样：
  ```python
  configfile: "config/config.yaml"
  configfile: "config/samples.yaml"

  include: "rules/preprocessing.smk"
  include: "rules/basic_analysis.smk"
  include: "rules/visualization.smk"
  include: "rules/report.smk"

  for plugin in config.get("plugins", []):
      if plugin.get("enabled", False):
          include: f"rules/{plugin['name']}.smk"

  rule all:
      input: "results/reports/analysis_report.html"
  ```
- [ ] 步骤 3：提交
  ```bash
  git commit -am "refactor(snakemake): 把 Snakefile 改成纯调度壳"
  ```

### Task 4.2：每个插件的 rule 改成调 CLI

对每个 `workflow/rules/<plugin>.smk`：

- [ ] 步骤 1：reencode UTF-8
- [ ] 步骤 2：重写成调 `python -m spstpipe run <plugin>`（输入输出路径保持不变）
- [ ] 步骤 3：单条提交
  ```bash
  git commit -am "refactor(snakemake): <plugin> rule 改成调 spstpipe CLI"
  ```

### Task 4.3：校验 DAG

- [ ] 步骤 1：`snakemake -n --use-conda`
- [ ] 步骤 2：补缺失 rule / 修正路径
- [ ] 步骤 3：如有改动，提交

---

## 六、Phase 5：CI + pre-commit

### Task 5.1：GitHub Actions

**涉及文件：** `.github/workflows/ci.yml`

- [ ] 步骤 1：写工作流（matrix: ubuntu-latest + python 3.11；jobs: lint、typecheck、test-fast、test-full）
- [ ] 步骤 2：推到 GitHub，看 Actions 变绿
- [ ] 步骤 3：提交
  ```bash
  git commit -am "ci: 加 GitHub Actions（lint / typecheck / test）"
  ```

### Task 5.2：pre-commit

**涉及文件：**
- 新建：`.pre-commit-config.yaml`
- 改：`pyproject.toml`（加 `[tool.ruff]`）

- [ ] 步骤 1：加 ruff（format + check）、trailing-whitespace、end-of-file-fixer、check-yaml、check-toml
- [ ] 步骤 2：跑 `pre-commit run --all-files`，如有 fix 就提交
- [ ] 步骤 3：提交
  ```bash
  git commit -am "ci: 加 pre-commit（ruff + 卫生钩子）"
  ```

### Task 5.3：覆盖率门槛

- [ ] 步骤 1：`pyproject.toml [tool.pytest.ini_options]` 加 `--cov-fail-under=50`
- [ ] 步骤 2：跑 `pytest --cov=spstpipe` 看报告；之后逐步升到 70%
- [ ] 步骤 3：提交
  ```bash
  git commit -am "ci: 强制 50% 测试覆盖率（后续升到 70%）"
  ```

---

## 七、Phase 6：文档

### Task 6.1：重写 README

**涉及文件：** `README.md`（覆盖）

- [ ] 步骤 1：用中文重写 README（项目简介、quickstart、徽章、Mermaid 架构图）
- [ ] 步骤 2：提交
  ```bash
  git commit -am "docs: 用中文重写 README（UTF-8）"
  ```

### Task 6.2：重写 usage.md

**涉及文件：** `docs/usage.md`

- [ ] 步骤 1：换成 CLI 示例（`spstpipe list`、`spstpipe run spatial_domain ...`）
- [ ] 步骤 2：提交

### Task 6.3：CHANGELOG

**涉及文件：** `CHANGELOG.md`

- [ ] 步骤 1：加 0.1.0 条目，列这次重构要点
- [ ] 步骤 2：提交
  ```bash
  git commit -am "docs: 加 CHANGELOG（0.1.0 条目）"
  ```

---

## 八、验收门槛

- [ ] 干净 venv 里 `pip install -e ".[dev]"` 成功
- [ ] `spstpipe list` 至少列出 6 个插件
- [ ] `spstpipe run spatial_domain --input fixture.h5ad --output out.h5ad` 退出码 0
- [ ] `snakemake -n` 输出非空 DAG 且无错
- [ ] `pytest --cov=spstpipe` 覆盖率 ≥ 50%（目标 70%）
- [ ] `mypy src` 0 个错
- [ ] `ruff check` + `ruff format --check` 通过
- [ ] `pre-commit run --all-files` 通过
- [ ] CI 在 GitHub 上变绿
- [ ] README 渲染没乱码

---

## 附录 A：pyproject.toml 骨架

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "spstpipe"
version = "0.1.0"
description = "空间转录组分析流水线（插件化）"
requires-python = ">=3.11"
dependencies = [
    "anndata>=0.10",
    "scanpy>=1.10",
    "numpy>=1.26",
    "scipy>=1.11",
    "pydantic>=2.5",
    "typer>=0.12",
    "loguru>=0.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-cov>=4",
    "mypy>=1.8",
    "ruff>=0.3",
    "pre-commit>=3.6",
]
torch = ["torch>=2.1"]
r-seurat = ["rpy2>=3.5"]

[project.scripts]
spstpipe = "spstpipe.cli:app"

[project.entry-points."spstpipe.plugins"]
spatial_domain = "spstpipe.plugins.spatial_domain.plugin:SpatialDomainPlugin"
cell_communication = "spstpipe.plugins.cell_communication.plugin:CellCommunicationPlugin"
trajectory = "spstpipe.plugins.trajectory.plugin:TrajectoryPlugin"
spatial_variable_genes = "spstpipe.plugins.spatial_variable_genes.plugin:SpatialVariableGenesPlugin"
multi_sample_integration = "spstpipe.plugins.multi_sample_integration.plugin:MultiSampleIntegrationPlugin"
scrna_joint_analysis = "spstpipe.plugins.scrna_joint_analysis.plugin:ScRNAJointAnalysisPlugin"

[tool.hatch.build.targets.wheel]
packages = ["src/spstpipe"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "SIM", "RUF"]

[tool.pytest.ini_options]
addopts = "-ra -q --cov=spstpipe --cov-report=term-missing --cov-fail-under=50"
testpaths = ["tests"]

[tool.mypy]
strict = true
files = ["src"]
```

## 附录 B：执行约定

1. 每个 Task 的步骤都是原子动作（2-5 分钟），一次只做一步。
2. 每步结束如有改动必须 commit，commit message 严格用中文、Conventional Commits 格式（`feat:` / `fix:` / `chore:` / `docs:` / `test:` / `refactor:` / `ci:`）。
3. 每次 commit 前跑 `mypy src` + `pytest` + `ruff check`，全过才提交。
4. 任何 `print()` 写代码里立即否决；任何英文 docstring 立即改成中文。
5. 测试用 `pytest.skip` 处理重依赖缺失，不要 `try/except ImportError` 静默吞。
