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

## ✅ 0.2.0（2026-06-10）— 类型 + 卫生硬化

- ✅ `ruff format` 统一 41 个文件
- ✅ `mypy --strict` 0 errors（27 source files）
- ✅ 修 `conftest.py` sandbox 探测：检测 `pytest-of-{user}` 子目录
- ✅ CONTRIBUTING.md / ROADMAP.md
- ✅ 在 6 个内置插件里接入至少 1 个轻量真实方法

## ✅ 0.3.0（2026-06-10）— 重依赖接入

- ✅ 0.3.0-1：spatial_variable_genes 接入 `squidpy.gr.spatial_autocorr`（Moran's I + p-value）
- ✅ 0.3.0-2：cell_communication 接入 `squidpy.gr.ligrec`
- ✅ 0.3.0-3：trajectory 接入 `scanpy.tl.paga` + `scanpy.tl.dpt`
- ✅ 0.3.0-4：multi_sample_integration 接入 `scanpy.external.pp.harmony_integrate`
- ✅ 0.3.0-5：scrna_joint_analysis 接入 `scanpy.tl.ingest`（label transfer）
- ✅ 0.3.0-6：spatial_domain 加 `squidpy.gr.spatial_neighbors` + leiden 真方法
- ✅ 0.3.0-7：写 `examples/synthetic_end_to_end.py` 端到端 demo
- ✅ 0.3.0-8：CI 跑 mypy 严格模式（mypy job）+ 装 spatial extras

## 🟡 1.0.0（2026-Q2）— 稳定版

- ✅ 1.0.0-1：API 冻结（`__version__ = "1.0.0"`，`__api_version__ = "1.0"`，docs/API.md）
- ⏳ 1.0.0-2：跨平台测试（Windows / macOS / Linux GitHub Actions matrix）
- ✅ 1.0.0-3：性能基准（examples/benchmark.py）
  - 实测：50×100=1s / 500×1000=0.2s / 5000×5000=8.6s / 20000×5000=290s（~4.8min）
  - 限制：谱聚类 `precomputed` affinity 在 50000×50000 需要 18.6 GiB（OOM），属算法限制
  - 实际建议规模：20000 spots × 5000 genes 4.8 分钟（仍在可接受范围）
- ⏳ 1.0.0-4：发布到 PyPI：`pip install spstpipe`（需要 PyPI 账号 + trusted publishing）
- ⏳ 1.0.0-5：完整中英双语文档（README/API.md/usage 各加 EN 翻译）
- ⏳ 1.0.0-6：CHANGELOG 1.0.0 条目
- ⏳ 1.0.0-7：FINAL_REPORT 1.0 收尾

## 原则

1. **零重依赖优先**：默认方法用 numpy / scipy / sklearn，能不引 torch/rpy2 就不引
2. **重依赖懒加载**：torch / liana / cell2location 走 optional extras，需要时再 `pip install spstpipe[torch]`
3. **占位即接口**：每个 plugin 必须有 `placeholder` 方法名，run() 内走占位实现，不让用户卡在依赖缺失
4. **测试零外网**：单元测试用合成 AnnData，CI 不下载数据集
5. **中文优先**：所有文档、commit message、代码注释默认中文
6. **API 稳定优先**：1.x 范围内不破坏现有签名，破坏性变更只在 major 版本

## 已放弃的想法

- ❌ 接入 10x Visium 真实示例（用户本地内存资源不足，0.2.0-1 取消）
- ❌ `cell2location` 接入 scrna_joint_analysis（torch 重依赖，改用 `scanpy.tl.ingest`）
- ❌ `harmonypy` 直接接入（`scanpy.external.pp.harmony_integrate` 是其官方包装，零新依赖）
