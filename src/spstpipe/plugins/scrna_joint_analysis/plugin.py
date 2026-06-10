# scrna_joint_analysis 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class ScRNAJointAnalysisPlugin(BasePlugin):
    """scrna_joint_analysis 插件。

    支持方法：seurat, cell2location, spatialglue（默认 seurat，重依赖方法用占位逻辑）。
    """

    name = "scrna_joint_analysis"
    version = "0.1.0"

    def __init__(self, method: str = "seurat", **params: object) -> None:
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
        # 所有方法当前用占位/默认逻辑
        rng = np.random.default_rng(42)
        adata.obs["predicted_cell_type"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
        adata.uns["scrna_joint_analysis_method"] = self.method
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
