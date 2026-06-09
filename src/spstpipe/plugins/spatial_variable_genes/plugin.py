# spatial_variable_genes 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata


class SpatialVariableGenesPlugin(BasePlugin):
    """空间可变基因识别插件。

    支持方法：morans_i（默认）、spark、lisa。
    当前所有方法用占位逻辑（重依赖懒加载，留待后续 Phase 接入）。
    """

    name = "spatial_variable_genes"
    version = "0.1.0"

    def __init__(self, method: str = "morans_i", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError(f"{self.__class__.__name__}.load 期望 1 个 h5ad 路径，实际 {len(paths)}")
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        # 占位逻辑：给每个基因一个随机 score
        rng = np.random.default_rng(42)
        adata.var["spatial_variable"] = rng.random(size=adata.n_vars)
        adata.uns["spatial_variable_genes_method"] = self.method
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)