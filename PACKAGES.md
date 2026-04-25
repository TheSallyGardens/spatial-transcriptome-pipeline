# 所需软件包

本文档记录空间转录组分析流程所需的所有软件包及其安装方式。

---

## 核心Python包 (必须)

```bash
# 使用mamba/conda安装
mamba install -c conda-forge -c bioconda \
    python=3.10 \
    scanpy \
    squidpy \
    anndata \
    harmonypy \
    leidenalg \
    python-igraph \
    matplotlib \
    seaborn \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    pysodb

# Stereo-seq数据读取 (GEF格式)
pip install stereopy
```

---

## 插件依赖

### spatial_domain (空间域识别)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| **PyTorch** | `pip install torch` 或 `conda install pytorch -c pytorch` | SpaGCN必需 |
| SpaGCN | `pip install spagcn` | 完整SpaGCN (可选，代码已包含简化版) |
| STlearn | `pip install stlearn` | STlearn方法 |
| BayesSpace | R环境 + `remotes::install_github("edward130603/BayesSpace")` | BayesSpace方法 |

```bash
# Python
pip install torch
pip install spagcn  # 可选

# R (用于BayesSpace)
R> remotes::install_github("edward130603/BayesSpace")
```

### cell_communication (细胞间通讯)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| squidpy | `pip install squidpy` | 已包含在核心包中 |
| CellChat | R环境 | R包，见下方 |
| NicheNet | R环境 | R包，见下方 |

```bash
# R (用于完整CellChat和NicheNet)
R> remotes::install_github("sqjin/CellChat")
R> remotes::install_github("saeyslab/nichenetr")
```

### trajectory (轨迹分析)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| Monocle3 | `pip install monocle3` 或 R | 轨迹分析 |

```bash
# Python
pip install monocle3

# R
R> install.packages('monocle3')
```

### spatial_variable_genes (空间变量基因)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| esda | `pip install esda` | Moran's I统计检验 |
| SPARK | `pip install SPARK` | 完整SPARK实现 |

```bash
pip install esda  # 用于Moran's I检验
pip install SPARK  # 可选，完整SPARK
```

### multi_sample_integration (多样本整合)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| harmonypy | `pip install harmonypy` | Harmony批次校正 |
| bbknn | `pip install bbknn` | BBKNN方法 |
| rliger | `pip install rliger` | LIGER方法 |
| scanorama | `pip install scanorama` | SCANORAMA方法 |

```bash
pip install harmonypy bbknn rliger scanorama
```

### scRNA_joint_analysis (单细胞联合分析)

| 包 | 安装方式 | 说明 |
|----|----------|------|
| **Seurat 5.x** | R环境 | **必须** - 见下方详细安装 |
| cell2location | `pip install cell2location scvi-tools` | 空间解卷积 |
| SpatialGlue | `pip install spatialglue` | 多模态整合 |

```bash
# Python可选包
pip install cell2location scvi-tools
pip install spatialglue

# R - Seurat 5.x (重要!)
R> remotes::install_github("satijalab/seurat", "seurat5")
R> install.packages('SeuratObject')
```

---

## Seurat V5 安装详解 (重要)

Seurat V5是最新的R包版本，提供了改进的标签迁移功能。

### R环境要求
- R >= 4.3.0
- 推荐 16GB+ RAM

### 安装步骤

```r
# 1. 安装SeuratObject
install.packages('SeuratObject', repos='https://satijalab.r-universe.dev')

# 2. 安装Seurat 5.x
remotes::install_github("satijalab/seurat", "seurat5")

# 3. 验证安装
library(Seurat)
packageVersion("Seurat")  # 应该显示 5.x.x
```

### Seurat V5 新特性
- 更快的PCA/UMAP计算
- 改进的多模态整合
- 新的标签迁移API

---

## 快速安装脚本

```bash
#!/bin/bash

# 创建conda环境
mamba create -n spatial_pipe python=3.10 -y

# 激活环境
mamba activate spatial_pipe

# 核心包
mamba install -c conda-forge -c bioconda \
    scanpy squidpy anndata harmonypy leidenalg \
    python-igraph matplotlib seaborn pandas numpy scipy \
    scikit-learn pysodb -y

# Python可选包
pip install torch esda bbknn rliger scanorama
pip install cell2location scvi-tools  # 如果需要
pip install spatialglue  # 如果需要
```

---

## Windows注意事项

部分包在Windows上可能有兼容性问题：

| 包 | Windows支持 | 替代方案 |
|----|-------------|----------|
| spagcn | ⚠️ 可能需要编译 | 使用内置简化版 |
| rliger | ❌ 不支持 | 使用harmony/bbknn |
| spatialglue | ⚠️ 可能有问题 | 使用内置方法 |

---

## 验证安装

```python
import scanpy as sc
import squidpy as sq
import harmonypy as hm

print("Core packages OK")

# 检查可选包
try:
    import torch
    print("PyTorch OK")
except ImportError:
    print("PyTorch not installed")

try:
    import esda
    print("esda OK")
except ImportError:
    print("esda not installed")
```

---

## 按需安装建议

如果你只需要部分功能：

**基础分析** (聚类、注释):
```bash
# 只需要核心包
mamba install scanpy squidpy anndata harmonypy leidenalg
```

**完整空间分析** (包括spatial_domain):
```bash
# 核心 + PyTorch
pip install torch
```

**完整联合分析** (包括scRNA joint):
```bash
# 需要R环境和Seurat 5.x
# 按照上面Seurat V5安装详解安装
```

---

## 获取帮助

- Scanpy: https://scanpy.readthedocs.io
- Squidpy: https://squidpy.readthedocs.io
- Seurat: https://satijalab.org/seurat
- SpaGCN: https://github.com/mggg/SpaGCN
