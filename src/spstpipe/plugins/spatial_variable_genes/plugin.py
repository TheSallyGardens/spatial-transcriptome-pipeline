# spatial_variable_genes 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.spatial_variable_genes.algorithms import run_morans_i


class SpatialVariableGenesPlugin(BasePlugin):
    """空间可变基因识别插件。

    支持方法：
      - morans_i : Moran's I 空间自相关（默认）
          - 装了 squidpy 时走 squidpy.gr.spatial_autocorr 真方法
          - 没装时优雅降级到占位（随机 score），无重依赖也能跑

    所有方法都写到 `adata.var["spatial_variable"]`。
    """

    name = "spatial_variable_genes"
    version = "0.1.0"

    def __init__(self, method: str = "morans_i", **params: object) -> None:
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
        # use_squidpy: True=有就真方法，没有就降级；False=强制占位（测试/轻依赖用）
        use_squidpy = bool(self.params.get("use_squidpy", True))
        if self.method == "morans_i":
            return run_morans_i(adata, use_squidpy=use_squidpy)
        raise ValueError(f"未知方法：{self.method}")

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
