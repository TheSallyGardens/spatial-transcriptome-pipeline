# 更新日志

所有重要变更都记录在这里。版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布] / Unreleased

### 卫生
- `ruff format` 统一 41 个文件的格式
- `mypy --strict` 通过（0 errors, 22 source files）：修了 18 个类型问题
  - `anndata` / `scanpy` / `scipy` / `sklearn` / `loguru` 在 [[tool.mypy.overrides]] 中声明 `ignore_missing_imports`（缺 py.typed 或 stubs）
  - 修 `loguru.logger` 不能当类型用：`setup()` 返回 `Any`
  - 修 `registry.py` `eps.get()` 的 `type: ignore` 标注（用 `arg-type` 替代 `union-attr`，删未用项）
  - 修 `spatial_domain/algorithms.py` `calculate_adj_matrix` 缺类型注解：补 `numpy.typing.NDArray` 标注
  - 修 `scrna_joint_analysis/plugin.py` 永真 `if str` 和永假字符串相等比较：清理为直接赋值
  - 修 `spatial_domain/plugin.py` 把 `**kwargs` 强转成 `float` 传给 `run_spectral_clustering` 的类型不匹配：改显式 `isinstance` 守卫

### 测试
- `conftest.py` 改用 `pytest-of-{user}` 子目录探测 sandbox Temp 权限：原探测根 Temp 不可靠（根可写但 pytest 9 创建的子目录被 DACL 拒绝）
- 本地 sandbox：36 passed, 7 skipped；CI/Linux：43 passed

### 文档
- 新 `CONTRIBUTING.md`：开发环境、跑测试、加新插件、CI 流程
- 新 `docs/ROADMAP.md`：0.2.0 / 0.3.0 / 1.0 计划

## [0.1.0] - 2026-06-10

### 重磅
- **架构现代化重构**：从 GBK 编码的 Snakemake-耦合脚本，迁移到 PEP 621 打包的 `spstpipe` Python 包
- **插件化**：6 个内置插件全部实现 `BasePlugin` 抽象，通过 entry-point 动态发现
- **统一接口**：每个插件都支持 `load → preprocess → run → save` 四步流程，可独立 CLI 调用
- **强类型**：`pydantic` 校验配置，`mypy --strict` 通过

### 改动
- 新增 `spstpipe.core`：BasePlugin / Config / IO / Logging / Registry
- 新增 `spstpipe.plugins.{spatial_domain,cell_communication,trajectory,spatial_variable_genes,multi_sample_integration,scrna_joint_analysis}`
- 新增 CLI：`spstpipe list` / `spstpipe run <plugin>`
- 删 `plugins/<name>/run.py`（被 `spstpipe.plugins.<name>.plugin` 替代）
- 删 `workflow/scripts/*.py`（业务逻辑搬到 spstpipe）
- 删 `tests/test_load_data.py` / `tests/test_end_to_end.py`（被新单元测试替代）
- Snakefile 和 rules 改成调用 `spstpipe run` 的薄壳

### 卫生
- 所有源文件统一 UTF-8
- 所有 Python 文件加 `from __future__ import annotations`
- 修 pytest tmp_path 走项目内（避开 Windows sandbox 系统 Temp 拒访）
- 加 `pre-commit` 配置（ruff + 卫生钩子）
- 加 GitHub Actions CI（lint + test-fast）

### 文档
- 新 `README.md`（中文，含架构图、徽章、快速开始）
- 新 `docs/usage.md`（CLI、Python API、Snakemake 用法、添加新插件）
- 新 `docs/superpowers/specs/`（设计 spec）
- 新 `docs/superpowers/plans/`（实施计划）

[0.1.0]: https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/releases/tag/v0.1.0
