# spatial_variable_genes 规则 - 调 spstpipe CLI
rule run_spatial_variable_genes:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/spatial_variable_genes/{{sample}}.h5ad"
    log:
        "logs/spatial_variable_genes/{{sample}}.log"
    shell:
        "spstpipe run spatial_variable_genes --input {{input}} --output {{output}} 2> {{log}}"