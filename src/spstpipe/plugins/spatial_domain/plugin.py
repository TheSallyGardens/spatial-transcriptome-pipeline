# spatial_domain 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.spatial_domain.algorithms import (
    run_spatial_domain,
)


class SpatialDomainPlugin(BasePlugin):
    """空间域识别插件。

    支持方法：
      - spectral_clustering : 谱聚类（默认，无重依赖）
      - leiden              : squidpy + scanpy leiden（需 pip install spstpipe[spatial]）
      - spagcn / bayespace / stlearn : 占位（走谱聚类）

    输出：
      - obs["spatial_domain"] : 每个 spot 的 domain 标签
      - uns["spatial_domain_method"] : 实际走的方法
    """

    name = "spatial_domain"
    version = "0.1.0"

    def __init__(self, method: str = "spectral_clustering", **params: object) -> None:
        self.method = method
        self.params = params

    def load(self, paths: list[Path]) -> ad.AnnData:
        if len(paths) != 1:
            raise ValueError(f"SpatialDomainPlugin.load 期望 1 个 h5ad 路径，实际 {len(paths)}")
        return load_anndata(paths[0])

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        if "spatial" not in adata.obsm and "x" in adata.obs and "y" in adata.obs:
            import numpy as np

            adata.obsm["spatial"] = np.column_stack([adata.obs["x"].values, adata.obs["y"].values])
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        params = self._safe_params(["resolution"])
        raw = params.get("resolution", 0.5)
        resolution = float(raw) if isinstance(raw, (int, float)) else 0.5
        return run_spatial_domain(adata, method=self.method, resolution=resolution)

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)

    def _safe_params(self, keys: list[str]) -> dict[str, object]:
        return {k: v for k, v in self.params.items() if k in keys}
