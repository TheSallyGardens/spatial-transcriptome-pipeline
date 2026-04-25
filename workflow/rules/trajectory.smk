# workflow/rules/trajectory.smk
rule trajectory_analysis:
    input:
        expand("results/{sample}/data/clustered_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        expand("results/{sample}/data/trajectory_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    params:
        method=config["plugins"]["trajectory"]["method"],
        params=config["plugins"]["trajectory"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/trajectory/run.py"