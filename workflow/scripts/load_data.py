from __future__ import annotations

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
    """
    加载Stereo-seq GEF格式数据

    Stereo-seq使用GEF (Gene Expression File)格式存储表达矩阵和空间坐标。
    需要安装Stereopy: pip install stereopy

    华大官方分析流程会产生gef格式文件，读取方式:
    -gef文件: 包含表达矩阵和空间坐标的二进制文件

    安装: pip install stereopy
    """
    try:
        import stereopy as st
    except ImportError:
        raise ImportError(
            "Stereopy is required to read Stereo-seq GEF format. "
            "Install with: pip install stereopy"
        )

    # GEF文件路径
    gef_file = Path(input_dir)
    if gef_file.is_dir():
        # 如果input_dir是目录，查找gef文件
        gef_files = list(gef_file.glob("*.gef"))
        if gef_files:
            gef_file = gef_files[0]
        else:
            raise FileNotFoundError(
                f"No .gef file found in {input_dir}. "
                "Please provide the path to a GEF file or a directory containing a .gef file."
            )

    # 使用Stereopy读取GEF文件
    # st.io.read_gef() 返回AnnData对象
    adata = st.io.read_gef(str(gef_file))

    # Stereopy返回的AnnData通常包含:
    # - X: 表达矩阵
    # - obsm['spatial']: 空间坐标
    # - var: 基因信息

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