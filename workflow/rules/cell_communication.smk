# workflow/rules/cell_communication.smk
rule cell_communication_analysis:
    input:
        expand("results/{sample}/data/spatial_domain_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        expand("results/{sample}/data/cellchat_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    params:
        method=config["plugins"]["cell_communication"]["method"],
        params=config["plugins"]["cell_communication"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/cell_communication/run.py"