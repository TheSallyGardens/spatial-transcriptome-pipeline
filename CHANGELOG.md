# 更新日志

所有重要变更都记录在这里。版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
