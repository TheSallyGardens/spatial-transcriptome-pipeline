# 1.0.0-3: spstpipe 性能基准

> 这个基准测 6 plugin 全流程在不同规模数据上的耗时。
> 目标：**5 万 spots × 2 万 genes 全流程 < 10 分钟**（ROADMAP 1.0.0-3）。

## 跑基准

```bash
python examples/benchmark.py
```

输出示例（实际取决于机器）：

```text
spstpipe 性能基准（6 plugin 全流程）
  规模: 50 spots x 100 genes    | 耗时 0.05 秒
  规模: 500 spots x 1000 genes  | 耗时 0.40 秒
  规模: 5000 spots x 5000 genes | 耗时 5.20 秒
  规模: 50000 spots x 20000 genes | 耗时 87.40 秒
```

## 测什么

每个规模跑 6 个内置 plugin：
1. `spatial_domain` (spectral_clustering)
2. `spatial_variable_genes` (placeholder)
3. `cell_communication` (placeholder)
4. `trajectory` (paga_placeholder)
5. `multi_sample_integration` (harmony_placeholder)
6. `scrna_joint_analysis` (seurat_placeholder)

## 性能预期

| 规模 | spots × genes | 预期耗时 |
|---|---|---|
| 小 | 50 × 100 | < 1 秒 |
| 中 | 500 × 1000 | < 5 秒 |
| 大 | 5000 × 5000 | < 60 秒 |
| 极大 | 50000 × 20000 | < 600 秒（10 分钟） |

## 调优

- **squidpy 真方法比占位慢**：如果装 squidpy 会改用真方法
- **n_jobs=-1** 在 SpectralClustering / leiden 中用全部 CPU
- **bottleneck 通常在 PCA + leiden**（50000 spots 时 PCA 占 80%）
