# scrna_joint_analysis 插件主类
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin
from spstpipe.core.io import load_anndata, save_anndata
from spstpipe.plugins.scrna_joint_analysis.algorithms import (
    run_joint_analysis,
)


class ScRNAJointAnalysisPlugin(BasePlugin):
    """scRNA + spatial 联合分析插件（label transfer）。

    支持方法：
      - seurat : scanpy.tl.ingest 真方法（需要 reference AnnData 有 obs['cell_type']）
      - seurat_placeholder : 占位（随机 cell_type，零依赖）

    输入：
      - paths[0] : query AnnData（spatial，缺 cell_type）
      - params["reference"] : reference AnnData（可选；用 load_anndata 加载 h5ad）
        或 params["reference_path"] : h5ad 路径，自动 load

    输出：
      - obs["predicted_cell_type"] : 每个 spot 预测的 cell type
      - uns["scrna_joint_analysis_method"] : 实际走的方法
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

    def _load_reference(self) -> ad.AnnData | None:
        ref = self.params.get("reference")
        if isinstance(ref, ad.AnnData):
            return ref
        ref_path = self.params.get("reference_path")
        if isinstance(ref_path, (str, Path)):
            return load_anndata(ref_path)
        return None

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        use_scanpy = bool(self.params.get("use_scanpy", True))
        reference = self._load_reference()
        return run_joint_analysis(adata, reference=reference, use_scanpy=use_scanpy)

    def save(self, adata: ad.AnnData, path: Path) -> None:
        save_anndata(adata, path)
