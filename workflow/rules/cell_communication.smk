# cell_communication 规则 - 调 spstpipe CLI
rule run_cell_communication:
    input:
        "results/preprocessing/{{sample}}.h5ad"
    output:
        "results/cell_communication/{{sample}}.h5ad"
    log:
        "logs/cell_communication/{{sample}}.log"
    shell:
        "spstpipe run cell_communication --input {{input}} --output {{output}} 2> {{log}}"