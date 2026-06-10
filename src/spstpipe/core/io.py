"""AnnData IO 工具 —— 集中处理 h5ad 读/写。"""

from __future__ import annotations

from pathlib import Path

import anndata as ad


def load_anndata(path: str | Path) -> ad.AnnData:
    """读 h5ad 文件返回 AnnData。"""
    return ad.read_h5ad(Path(path))


def save_anndata(adata: ad.AnnData, path: str | Path) -> None:
    """把 AnnData 写到 h5ad 文件，自动建父目录。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(p)
