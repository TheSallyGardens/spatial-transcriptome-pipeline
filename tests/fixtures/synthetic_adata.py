import anndata as ad
import numpy as np


def synthetic_adata(
    n_spots: int = 50,
    n_genes: int = 100,
    platform: str = "10x_visium",
    seed: int = 0,
) -> ad.AnnData:
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_spots, n_genes)).astype(np.float32)
    # 排成 sqrt(n_spots) x sqrt(n_spots) 的网格
    side = int(np.ceil(np.sqrt(n_spots)))
    x_full = np.tile(np.arange(side, dtype=float), side)
    y_full = np.repeat(np.arange(side, dtype=float), side)
    x = x_full[:n_spots]
    y = y_full[:n_spots]
    obs = {
        "x": x,
        "y": y,
        "platform": platform,
    }
    var = {"gene_symbol": [f"g{i}" for i in range(n_genes)]}
    adata = ad.AnnData(
        X=X,
        obs=obs,
        var=var,
        obsm={"spatial": np.column_stack([x, y])},
    )
    adata.uns["synthetic"] = True
    return adata
