# multi_sample_integration 规则 - 调 spstpipe CLI
rule run_multi_sample_integration:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/multi_sample_integration/{{sample}}.h5ad"
    log:
        "logs/multi_sample_integration/{{sample}}.log"
    shell:
        "spstpipe run multi_sample_integration --input {{input}} --output {{output}} 2> {{log}}"