# trajectory 规则 - 调 spstpipe CLI
rule run_trajectory:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/trajectory/{{sample}}.h5ad"
    log:
        "logs/trajectory/{{sample}}.log"
    shell:
        "spstpipe run trajectory --input {{input}} --output {{output}} 2> {{log}}"