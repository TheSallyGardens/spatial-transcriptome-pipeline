# multi_sample_integration 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.multi_sample_integration.algorithms import (
    run_integration,
)


class MultiSampleIntegrationPlugin(BasePlugin):
    """多样本整合插件（Harmony）。

    支持方法：
      - harmony : Harmony 整合（默认，scanpy 真方法）
      - harmony_placeholder : 占位（无整合效果，零依赖也能跑）

    输入要求：
      - `obs["batch"]` 必须存在

    输出：
      - `obs["integration_batch"]`：复制 batch 标签
      - `obsm["X_pca_harmony"]`：校正后的 PCA（真方法才有）
      - `uns["multi_sample_integration_method"]`：实际走的方法
    """

    name = "multi_sample_integration"
    version = "0.1.0"

    def __init__(self, method: str = "harmony", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError(
                f"{self.__class__.__name__}.load 期望 1 个 h5ad 路径，实际 {len(paths)}"
            )
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        use_scanpy = bool(self.params.get("use_scanpy", True))
        return run_integration(adata, use_scanpy=use_scanpy)

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
