# trajectory 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.trajectory.algorithms import (
    run_trajectory,
)


class TrajectoryPlugin(BasePlugin):
    """轨迹推断插件（PAGA + DPT）。

    支持方法：
      - paga : PAGA + DPT（默认，scanpy 真方法，依赖硬装）
      - paga_placeholder : 占位（随机伪时间，零依赖也能跑）

    任何 paga 方法名都走 run_trajectory() 入口，
    内部按 use_scanpy 参数决定真/占位。
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
        use_scanpy = bool(self.params.get("use_scanpy", True))
        return run_trajectory(adata, use_scanpy=use_scanpy)

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
