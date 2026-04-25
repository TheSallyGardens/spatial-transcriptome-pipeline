# workflow/rules/scRNA_joint_analysis.smk
rule scRNA_joint_analysis:
    input:
        expand("results/{sample}/data/annotated_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        expand("results/{sample}/data/scRNA_joint_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    params:
        method=config["plugins"]["scRNA_joint_analysis"]["method"],
        params=config["plugins"]["scRNA_joint_analysis"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/scRNA_joint_analysis/run.py"