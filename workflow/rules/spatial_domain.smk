# workflow/rules/spatial_domain.smk
rule spatial_domain_analysis:
    input:
        expand("results/{sample}/data/annotated_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        expand("results/{sample}/data/spatial_domain_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    params:
        method=config["plugins"]["spatial_domain"]["method"],
        params=config["plugins"]["spatial_domain"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/spatial_domain/run.py"