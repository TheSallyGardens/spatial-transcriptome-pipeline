# 路线图（中文）

> 本文档列出空间转录组分析流水线（`spstpipe`）的中长期计划。
> 标 ✅ = 已完成 / 🟡 = 进行中 / ⏳ = 计划中

## ✅ 0.1.0（2026-06-10）— 架构现代化

- 从 GBK 编码的 Snakemake-耦合脚本，迁移到 PEP 621 打包的 `spstpipe` Python 包
- 6 个内置插件全部实现 `BasePlugin` 抽象，entry-point 动态发现
- CLI：`spstpipe list` / `spstpipe run <plugin>`
- Snakefile 和 rules 改成调用 `spstpipe run` 的薄壳
- 单元测试 36/43 在 sandbox 通过，CI/Linux 全 43 通过
- pre-commit + GitHub Actions CI
- 中文 README / usage / CHANGELOG / FINAL_REPORT

## 🟡 0.2.0（2026-Q2）— 类型 + 卫生硬化

- ✅ `ruff format` 统一 41 个文件
- ✅ `mypy --strict` 0 errors（22 source files）
- ✅ 修 `conftest.py` sandbox 探测：检测 `pytest-of-{user}` 子目录
- ✅ CONTRIBUTING.md / ROADMAP.md
- ⏳ 在 6 个内置插件里接入至少 1 个轻量真实方法（候选：squidpy.gr.spatial_neighbors）
- ⏳ 提供 1 个 `examples/` 端到端 demo（合成 AnnData → spatial_domain → 保存）

## ⏳ 0.3.0（2026-Q3）— 重依赖接入

- 0.3.0-1：把 `spatial_domain.spectral_clustering` 升级到 `squidpy.gr.spatial_neighbors` + `leidenalg`
- 0.3.0-2：把 `cell_communication` 占位升级到 `squidpy.gr.ligrec` 或 `liana`
- 0.3.0-3：把 `trajectory.paga` 升级到 `scanpy.tl.paga`（轻依赖，scanpy 已有）
- 0.3.0-4：把 `spatial_variable_genes.morans_i` 升级到 `squidpy.gr.spatial_autocorr`
- 0.3.0-5：把 `multi_sample_integration.harmony` 升级到 `harmonypy`（真依赖）
- 0.3.0-6：把 `scrna_joint_analysis.seurat` 升级到 `cell2location`（torch 依赖）
- 0.3.0-7：写 `examples/10x_visium_demo/` 真实数据示例
- 0.3.0-8：CI 跑 mypy 严格模式

## ⏳ 1.0.0（2026-Q4+）— 稳定版

- 1.0.0-1：API 冻结（BasePlugin / Config / Registry 签名不再变）
- 1.0.0-2：性能基准：5 万 spots × 2 万 genes 全流程 < 10 分钟
- 1.0.0-3：跨平台测试（Windows / macOS / Linux）
- 1.0.0-4：发布到 PyPI：`pip install spstpipe`
- 1.0.0-5：完整中英双语文档

## 原则

1. **零重依赖优先**：默认方法用 numpy / scipy / sklearn，能不引 torch/rpy2 就不引
2. **重依赖懒加载**：torch / liana / cell2location 走 optional extras，需要时再 `pip install spstpipe[torch]`
3. **占位即接口**：每个 plugin 必须有 `placeholder` 方法名，run() 内走占位实现，不让用户卡在依赖缺失
4. **测试零外网**：单元测试用合成 AnnData，CI 不下载数据集
5. **中文优先**：所有文档、commit message、代码注释默认中文

## 已放弃的想法

- ❌ 接入 10x Visium 真实示例（用户本地内存资源不足，0.2.0-1 取消）
