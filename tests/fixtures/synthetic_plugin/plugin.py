"""测试用假插件 —— 给注册表测试用。"""
from __future__ import annotations

from pathlib import Path

import anndata as ad

from spstpipe.core.base import BasePlugin


class SyntheticPlugin(BasePlugin):
    """什么都不做，只是用来验证注册表能发现。"""

    name = "synthetic"
    version = "0.0.1-test"

    def load(self, paths: list[Path]) -> ad.AnnData:  # noqa: ARG002
        import numpy as np

        return ad.AnnData(np.zeros((0, 0)))

    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        return adata

    def run(self, adata: ad.AnnData) -> ad.AnnData:
        adata.obs["synthetic_run"] = True
        return adata

    def save(self, adata: ad.AnnData, path: Path) -> None:  # noqa: ARG002
        path.write_text("synthetic", encoding="utf-8")