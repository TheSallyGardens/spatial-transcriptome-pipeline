rule load_10x_data:
    input:
        lambda w: f"{config['samples'][w.sample]['input_dir']}"
    output:
        "results/{sample}/data/raw_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../scripts/load_data.py"

rule filter_cells:
    input:
        "results/{sample}/data/raw_adata.h5ad"
    output:
        "results/{sample}/data/filtered_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../scripts/preprocessing.py"

rule normalize_data:
    input:
        "results/{sample}/data/filtered_adata.h5ad"
    output:
        "results/{sample}/data/normalized_adata.h5ad"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../scripts/preprocessing.py"
