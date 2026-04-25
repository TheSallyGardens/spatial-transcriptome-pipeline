# workflow/rules/basic_analysis.smk
rule run_pca:
    input:
        "results/{sample}/data/normalized_adata.h5ad"
    output:
        "results/{sample}/data/pca_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../scripts/clustering.py"

rule run_neighbors:
    input:
        "results/{sample}/data/pca_adata.h5ad"
    output:
        "results/{sample}/data/neighbors_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../scripts/clustering.py"

rule run_clustering:
    input:
        "results/{sample}/data/neighbors_adata.h5ad"
    output:
        "results/{sample}/data/clustered_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../scripts/clustering.py"

rule annotate_cells:
    input:
        "results/{sample}/data/clustered_adata.h5ad"
    output:
        "results/{sample}/data/annotated_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../scripts/annotation.py"