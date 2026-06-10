# cell_communication 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.cell_communication.algorithms import (
    run_cell_communication,
)


class CellCommunicationPlugin(BasePlugin):
    """细胞通讯分析插件。

    支持方法：
      - placeholder : 占位（默认，零依赖）
      - squidpy_ligrec : squidpy.gr.ligrec 真方法（需要装 `pip install spstpipe[spatial]`）

    输入要求：
      - `obs["cell_type"]` 必须存在
      - 有空间坐标更佳（`obsm["spatial"]`），但非强制

    输出：
      - `obs["cell_communication_score"]`：每个 spot 的总体通讯强度
      - `uns["cell_communication_result"]`：通讯结果（p-values 矩阵或占位结构）
      - `uns["cell_communication_method"]`：实际走的方法
    """

    name = "cell_communication"
    version = "0.1.0"

    def __init__(self, method: str = "placeholder", **params: object) -> None:
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
        use_squidpy = bool(self.params.get("use_squidpy", True))
        # 任何 method 名都走 run_cell_communication（内部按 use_squidpy 决定真/占位）
        return run_cell_communication(adata, use_squidpy=use_squidpy)

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
