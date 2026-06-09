# multi_sample_integration 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class MultiSampleIntegrationPlugin(BasePlugin):
    """multi_sample_integration 插件。

    支持方法：harmony, bbknn, liger（默认 harmony，重依赖方法用占位逻辑）。
    """

    name = "multi_sample_integration"
    version = "0.1.0"

    def __init__(self, method: str = "harmony", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError(f"{self.__class__.__name__}.load 期望 1 个 h5ad 路径，实际 {len(paths)}")
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        # 所有方法当前用占位/默认逻辑
        rng = np.random.default_rng(42)
        if "integration_batch":
            adata.obs["integration_batch"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
            adata.var["spatial_variable"] = rng.random(size=adata.n_vars)
        adata.uns["multi_sample_integration_method"] = self.method
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
