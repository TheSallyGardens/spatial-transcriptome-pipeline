# workflow/rules/spatial_variable_genes.smk
rule spatial_variable_genes_analysis:
    input:
        expand("results/{sample}/data/normalized_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        expand("results/{sample}/data/spatial_variable_genes_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    params:
        method=config["plugins"]["spatial_variable_genes"]["method"],
        params=config["plugins"]["spatial_variable_genes"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/spatial_variable_genes/run.py"