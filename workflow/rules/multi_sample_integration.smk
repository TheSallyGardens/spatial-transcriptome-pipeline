# workflow/rules/multi_sample_integration.smk
rule multi_sample_integration:
    input:
        expand("results/{sample}/data/annotated_adata.h5ad", sample=[s["id"] for s in config["samples"]])
    output:
        "results/integrated/integrated_adata.h5ad"
    params:
        method=config["plugins"]["multi_sample_integration"]["method"],
        params=config["plugins"]["multi_sample_integration"]["params"]
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../plugins/multi_sample_integration/run.py"