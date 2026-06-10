# spstpipe · 空间转录组分析流水线

> 基于 Snakemake + Python 插件化架构的空间转录组分析流水线，支持 10x Visium 和 Stereo-seq 数据。
>
> [English Version](README.en.md) | 简体中文（本文件）

[![CI](https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 特性

- **插件化架构**：6 个内置分析插件，可独立调用、可单独测试
- **统一接口**：所有插件实现 `BasePlugin` 抽象（load / preprocess / run / save）
- **强类型配置**：`pydantic` 校验 YAML 配置，错误早失败
- **CI 就绪**：GitHub Actions 自动跑 lint + 单元测试
- **零 Snakemake 也能跑**：`spstpipe run spatial_domain ...` CLI 入口

## 支持的分析模块

| 插件 | 默认方法 | 描述 |
|------|---------|------|
| `spatial_domain` | spectral_clustering | 识别组织里的连续空间区域 |
| `cell_communication` | placeholder | 细胞间通讯（CellChat / NicheNet / Squidpy） |
| `trajectory` | paga | 发育轨迹推断（PAGA / Monocle） |
| `spatial_variable_genes` | morans_i | 空间可变基因（Moran's I / SPARK / LISA） |
| `multi_sample_integration` | harmony | 多样本整合（Harmony / BBKNN / Liger） |
| `scRNA_joint_analysis` | seurat | 单细胞联合分析（Seurat 标签迁移） |

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/TheSallyGardens/spatial-transcriptome-pipeline.git
cd spatial-transcriptome-pipeline

# 创建 conda 环境
mamba create -n spstpipe python=3.11 -y
mamba activate spstpipe

# 以开发模式安装
pip install -e ".[dev]"
```

### 2. 命令行使用（无需 Snakemake）

```bash
# 列出所有已注册插件
spstpipe list

# 跑单个插件
spstpipe run spatial_domain --input data/sample1.h5ad --output results/spatial_domain/sample1.h5ad
```

### 3. Python API

```python
import anndata as ad
from spstpipe.plugins.spatial_domain import SpatialDomainPlugin

adata = ad.read_h5ad("data/sample1.h5ad")
plugin = SpatialDomainPlugin(method="spectral_clustering")
result = plugin(adata)  # 等价于 plugin.run(adata)
print(result.obs["spatial_domain"].value_counts())
```

### 4. 通过 Snakemake 跑完整流水线

```bash
# 完整跑
snakemake --use-conda

# Dry run
snakemake -n

# 跑指定插件
snakemake run_spatial_domain
```

## 架构

```
┌────────────────┐      ┌──────────────────┐      ┌──────────────┐
│  config/*.yaml │ ──▶  │  spstpipe.cli    │ ──▶  │  BasePlugin  │
└────────────────┘      │  (typer entry)   │      │  抽象类       │
                        └──────────────────┘      └──────┬───────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
              │ spatial_domain  │               │   trajectory    │               │  cell_communication │
              │  (6 个内置插件) │               │                 │               │                 │
              └────────┬────────┘               └─────────────────┘               └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  algorithms.py  │  (懒加载 torch / stereopy / stlearn)
              └─────────────────┘
```

## 开发

### 跑测试

```bash
pytest                       # 全部测试
pytest tests/unit/test_X.py  # 单文件
pytest -k "spatial"          # 按名字过滤
pytest --cov=spstpipe        # 覆盖率
```

### 添加新插件

1. 在 `src/spstpipe/plugins/<your_plugin>/` 下创建 `plugin.py`
2. 继承 `BasePlugin`，实现 4 个抽象方法
3. 在 `pyproject.toml` 的 `[project.entry-points."spstpipe.plugins"]` 注册
4. 写 `tests/unit/test_<your_plugin>.py`
5. 跑 `pytest` 确认通过

## 文档

- [docs/usage.md](docs/usage.md) - 详细使用说明
- [docs/superpowers/specs/](docs/superpowers/specs/) - 设计文档
- [docs/superpowers/plans/](docs/superpowers/plans/) - 实施计划

## 许可

MIT
