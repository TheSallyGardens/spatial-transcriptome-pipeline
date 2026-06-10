# trajectory 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class TrajectoryPlugin(BasePlugin):
    """trajectory 插件。

    支持方法：paga, monocle, spatial_trajectory（默认 paga，重依赖方法用占位逻辑）。
    """

    name = "trajectory"
    version = "0.1.0"

    def __init__(self, method: str = "paga", **params: object) -> None:
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
        if "pseudotime":
            adata.obs["pseudotime"] = rng.integers(0, 3, size=adata.n_obs).astype(str)
            adata.var["spatial_variable"] = rng.random(size=adata.n_vars)
        adata.uns["trajectory_method"] = self.method
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
