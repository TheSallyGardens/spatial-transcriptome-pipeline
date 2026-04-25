# workflow/rules/visualization.smk

# 空间聚类图
rule plot_spatial_clustering:
    input:
        "results/{sample}/data/annotated_adata.h5ad"
    output:
        "results/{sample}/visualization/spatial_clustering.png"
    params:
        plot_type="spatial",
        color_by="louvain"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../workflow/scripts/visualization.py"

# 细胞类型空间分布图
rule plot_spatial_celltype:
    input:
        "results/{sample}/data/annotated_adata.h5ad"
    output:
        "results/{sample}/visualization/spatial_celltype.png"
    params:
        plot_type="spatial",
        color_by="cell_type"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../workflow/scripts/visualization.py"

# UMAP图
rule plot_umap:
    input:
        "results/{sample}/data/annotated_adata.h5ad"
    output:
        "results/{sample}/visualization/umap.png"
    params:
        plot_type="umap",
        color_by="louvain"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../workflow/scripts/visualization.py"

# 空间域分布图
rule plot_spatial_domain:
    input:
        "results/{sample}/data/spatial_domain_adata.h5ad"
    output:
        "results/{sample}/visualization/spatial_domain.png"
    params:
        plot_type="spatial",
        color_by="spatial_domain"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../workflow/scripts/visualization.py"