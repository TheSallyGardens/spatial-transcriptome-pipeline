# workflow/scripts/load_data.py
import scanpy as sc
import anndata as ad
from pathlib import Path
import yaml

def load_10x_visium(sample_id, input_dir):
    """加载10x Visium标准输出数据"""
    adata = sc.read_visium(input_dir)
    adata.var_names_make_unique()
    adata.obs_names_make_unique()

    # 存储样本元数据
    adata.uns["sample_id"] = sample_id
    adata.uns["platform"] = "10x_visium"

    return adata

def load_stereo_seq(sample_id, input_dir):
    """加载Stereo-seq标准输出数据 (STA格式)"""
    # Stereo-seq STA格式: bin矩阵 + 空间坐标
    sta_file = Path(input_dir) / "STA.txt"

    # 读取STA文件
    positions = []
    with open(sta_file, 'r') as f:
        for line in f:
            cols = line.strip().split('\t')
            positions.append([int(cols[0]), int(cols[1]), float(cols[2]), float(cols[3])])

    # 读取表达矩阵
    adata = sc.read_csv(Path(input_dir) / "matrix.csv")
    adata.obsm["spatial"] = positions

    adata.uns["sample_id"] = sample_id
    adata.uns["platform"] = "stereo_seq"

    return adata

# Snakemake script接口
if __name__ == "__snakemake__":
    sample_id = snakemake.wildcards["sample"]
    sample_config = config["samples"][sample_id]
    input_dir = sample_config["input_dir"]

    if sample_config["platform"] == "10x_visium":
        adata = load_10x_visium(sample_id, input_dir)
    elif sample_config["platform"] == "stereo_seq":
        adata = load_stereo_seq(sample_id, input_dir)
    else:
        raise ValueError(f"Unsupported platform: {sample_config['platform']}")

    adata.write_h5ad(snakemake.output[0])