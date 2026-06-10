# scRNA_joint_analysis 规则 - 调 spstpipe CLI
rule run_scRNA_joint_analysis:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/scRNA_joint_analysis/{{sample}}.h5ad"
    log:
        "logs/scRNA_joint_analysis/{{sample}}.log"
    shell:
        "spstpipe run scRNA_joint_analysis --input {{input}} --output {{output}} 2> {{log}}"