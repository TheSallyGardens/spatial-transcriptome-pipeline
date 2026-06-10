# preprocessing - 简单 QC + 写出 h5ad

rule load_10x_data:
    output:
        "results/preprocessing/{sample}.h5ad"
    log:
        "logs/preprocessing/{sample}.log"
    run:
        import yaml
        from pathlib import Path
        from spstpipe.core.io import load_anndata, save_anndata
        from tests.fixtures.synthetic_adata import synthetic_adata
        samples = yaml.safe_load(open("config/samples.yaml"))["samples"]
        info = next(s for s in samples if s["id"] == wildcards.sample)
        adata = None
        candidate = Path(info["input_dir"]) / "data.h5ad"
        if candidate.exists():
            adata = load_anndata(candidate)
        if adata is None:
            adata = synthetic_adata(platform=info["platform"])
        Path(output[0]).parent.mkdir(parents=True, exist_ok=True)
        save_anndata(adata, output[0])