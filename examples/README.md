# 0.3.0-7: spstpipe 端到端 demo（合成数据 → 6 plugin 串跑）

> 这个例子用**合成 AnnData**演示 6 个内置插件的完整流程。
> 不需要任何真实 10x Visium 数据，**完全离线可跑**。
> 用于快速验证你的安装和管道是否正常。

## 跑这个 demo

```bash
# 1) 装 spstpipe（含 dev 依赖）
pip install -e ".[dev]"

# 2) 跑 demo
python examples/synthetic_end_to_end.py
```

> **sandbox 用户注意**：在 Windows sandbox 下 scanpy/scikit-learn 的并行（`joblib`/`loky`）会调 `wmic` 探测 CPU 核心，wmic 在 sandbox 下 hang。
> 跑 demo 之前先设：
> ```powershell
> $env:LOKY_MAX_CPU_COUNT = 1
> ```
> 我们的 demo 默认走**占位实现**（不需要 scanpy 真方法），不会触发并行，
> 所以 sandbox 下也能秒跑。

## 它做什么

1. 造 50 spots × 100 genes 的合成 AnnData（5x10 网格 + 高斯噪声）
2. 跑 `spatial_domain`（谱聚类，**无重依赖**）→ 写 `obs["spatial_domain"]`
3. 跑 `spatial_variable_genes`（占位 Moran's I）→ 写 `var["spatial_variable"]`
4. 跑 `cell_communication`（占位，注入 `obs["cell_type"]`）→ 写通讯 score
5. 跑 `trajectory`（占位 PAGA）→ 写 `obs["pseudotime"]`
6. 跑 `multi_sample_integration`（占位，注入 `obs["batch"]`）→ 写 integration_batch
7. 跑 `scrna_joint_analysis`（占位）→ 写 `obs["predicted_cell_type"]`
8. 保存 `out.h5ad` 到当前目录

## 输出

```text
==> 造合成数据 (50 spots x 100 genes, 5x10 网格)
    [OK] 50 spots x 100 genes
==> 跑 spatial_domain (spectral_clustering)
    [OK] 5 domains
==> 跑 spatial_variable_genes (morans_i_placeholder)
    [OK] 100 gene scores
==> 跑 cell_communication (placeholder)
    [OK] 50 cell communication scores
==> 跑 trajectory (paga_placeholder)
    [OK] 50 pseudotime
==> 跑 multi_sample_integration (harmony_placeholder)
    [OK] 2 batches
==> 跑 scrna_joint_analysis (seurat_placeholder)
    [OK] 3 predicted cell types
==> 保存 out.h5ad
    [OK] out.h5ad (50 x 100)
```

## 下一步

- 想跑真方法？`pip install spstpipe[spatial]` 装 squidpy，然后改 demo 里的 `use_squidpy=False` → `True`
- 想用真数据？看 `docs/usage.md` 里的 10x Visium 加载部分
