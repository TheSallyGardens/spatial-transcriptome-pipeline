# workflow/rules/report.smk
rule generate_report:
    input:
        expand("results/{sample}/data/annotated_adata.h5ad", sample=[s["id"] for s in config["samples"]]),
        expand("results/{sample}/visualization/", sample=[s["id"] for s in config["samples"]])
    output:
        "results/reports/analysis_report.html"
    conda:
        "../envs/scanpy.yaml"
    script:
        "../../scripts/report.py"