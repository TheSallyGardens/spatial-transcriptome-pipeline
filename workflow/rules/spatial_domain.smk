# spatial_domain 规则 - 调 spstpipe CLI
rule run_spatial_domain:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/spatial_domain/{{sample}}.h5ad"
    log:
        "logs/spatial_domain/{{sample}}.log"
    shell:
        "spstpipe run spatial_domain --input {{input}} --output {{output}} 2> {{log}}"