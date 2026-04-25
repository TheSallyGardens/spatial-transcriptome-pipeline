# Spatial Transcriptome Pipeline

基于Snakemake的空间转录组下游高级分析流程，支持10x Visium和Stereo-seq数据。

## 支持的数据平台

- **10x Visium**: 标准Space Ranger输出
- **Stereo-seq**: STA格式输出

## 支持的分析模块

| 模块 | 工具 | 描述 |
|------|------|------|
| 空间域识别 | SpaGCN, BayesSpace, STlearn | 识别空间连续区域 |
| 细胞间通讯 | CellChat, NicheNet, Squidpy | 推断细胞通讯 |
| 轨迹分析 | PAGA, Monocle, ST trajectory | 发育轨迹分析 |
| 空间变量基因 | Moran's I, SPARK, LISA | 识别空间变量基因 |
| 多样本整合 | Harmony, BBKNN, Liger | 批次校正与整合 |
| 单细胞联合 | Seurat, cell2location, SpatialGlue | 与scRNA联合分析 |

## 快速开始

### 1. 安装环境

```bash
# 使用Mamba创建分析环境
mamba env create -f envs/scanpy.yaml
mamba env create -f envs/r-seurat.yaml  # 如需R工具支持

# 激活环境
mamba activate scanpy
```

### 2. 配置样本

编辑 `config/samples.yaml`:

```yaml
samples:
  - id: sample1
    platform: 10x_visium
    input_dir: "data/sample1"
    config:
      min_genes: 200
      min_cells: 50

  - id: sample2
    platform: stereo_seq
    input_dir: "data/sample2"
    config:
      min_genes: 200
      min_cells: 50
```

### 3. 配置分析模块

编辑 `config/config.yaml`，启用/禁用各分析模块：

```yaml
plugins:
  - name: spatial_domain
    enabled: true
    method: spagcn
    params:
      resolution: 0.5
```

### 4. 运行流程

```bash
# 完整运行
snakemake --use-conda

# 查看可用的规则
snakemake --list

# Dry run测试
snakemake --use-conda -n

# 并行运行
snakemake --use-conda -j 8
```

## 目录结构

```
spatial_transcriptome_pipeline/
├── Snakefile              # 主流程入口
├── config/
│   ├── config.yaml        # 主配置
│   └── samples.yaml       # 样本配置
├── workflow/
│   ├── rules/            # Snakemake规则
│   └── scripts/           # Python脚本
├── plugins/               # 分析插件
│   ├── spatial_domain/
│   ├── cell_communication/
│   └── ...
├── envs/                  # Conda环境定义
└── results/               # 分析结果
```

## 输出

- `results/{sample}/data/`: 处理后的AnnData数据
- `results/{sample}/visualization/`: 可视化图片
- `results/{sample}/reports/`: 分析报告
- `results/integrated/`: 整合分析结果

## 插件开发

新增分析方法：

1. 在 `plugins/` 下创建新插件目录
2. 编写 `run.py` 和 `config.yaml`
3. 在 `config/config.yaml` 中声明即可启用

## 许可证

MIT License
