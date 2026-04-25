# 使用指南

## 环境准备

### 安装Miniforge3

推荐使用Miniforge3管理Conda环境：

1. 下载Miniforge3: https://github.com/conda-forge/miniforge
2. 安装: `bash Miniforge3-Linux-x86_64.sh`
3. 初始化: `source ~/.bashrc`

### 创建分析环境

```bash
# 主要Python环境
mamba env create -f envs/scanpy.yaml

# R环境（如需Seurat/CellChat）
mamba env create -f envs/r-seurat.yaml

# 激活环境
mamba activate scanpy
```

## 数据准备

### 10x Visium数据

将Space Ranger输出目录配置到 `samples.yaml`:

```
data/sample1/
├── filtered_feature_bc_matrix/
│   ├── matrix.mtx
│   ├── barcodes.tsv.gz
│   └── features.tsv.gz
└── spatial/
    ├── tissue_positions_list.csv
    └── images/
```

### Stereo-seq数据

配置STA格式数据:

```
data/sample2/
├── STA.txt      # 空间坐标
└── matrix.csv   # 表达矩阵
```

## 配置详解

### samples.yaml

```yaml
samples:
  - id: "样本ID"
    platform: "10x_visium" | "stereo_seq"
    input_dir: "数据目录路径"
    config:
      min_genes: 200      # 最小基因数
      min_cells: 50      # 最小细胞数
      max_genes: 5000     # 最大基因数（可选）
```

### config.yaml

```yaml
project:
  name: "项目名称"
  author: "作者"
  date: "日期"

plugins:
  - name: "插件名称"
    enabled: true | false
    method: "方法名"
    params:
      key: value
```

## 运行模式

### 本地运行

```bash
# 单线程
snakemake --use-conda

# 多线程
snakemake --use-conda -j 4

# 指定规则运行
snakemake --use-conda results/sample1/data/filtered_adata.h5ad
```

### 集群运行

```bash
# 使用SLURM
snakemake --use-conda --cluster "sbatch -N 1 -n 1 -t 60" -j 32

# 使用LSF
snakemake --use-conda --cluster "bsub -q queue -n 1 -R span[hosts=1]" -j 32
```

## 结果解读

### AnnData文件

- `raw_adata.h5ad`: 原始数据
- `filtered_adata.h5ad`: 过滤后数据
- `normalized_adata.h5ad`: 归一化后数据
- `clustered_adata.h5ad`: 聚类结果
- `annotated_adata.h5ad`: 细胞注释结果

### 可视化

- `spatial_clustering.png`: 空间聚类图
- `spatial_celltype.png`: 细胞类型空间分布
- `umap.png`: UMAP降维图

### 报告

`results/reports/analysis_report.html`: HTML格式分析报告

## 常见问题

Q: 报`ModuleNotFoundError`？
A: 确保已激活正确的conda环境

Q: 内存不足？
A: 减少并行任务数，或增大 `--resources mem=XXX`

Q: 数据加载失败？
A: 检查输入路径和数据格式是否正确
