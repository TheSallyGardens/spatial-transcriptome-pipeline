# spstpipe CLI —— 列出 / 运行 插件
from __future__ import annotations

from pathlib import Path

import typer

from spstpipe.core.logging import setup
from spstpipe.core.registry import discover_plugins

app = typer.Typer(help="spstpipe - 空间转录组分析流水线")


@app.command(name="list")
def list_plugins() -> None:
    """列出所有已注册的插件。"""
    setup()
    plugins = discover_plugins(group="spstpipe.plugins")
    if not plugins:
        typer.echo("（暂无插件）")
        return
    typer.echo(f"已注册 {len(plugins)} 个插件：")
    for name, cls in sorted(plugins.items()):
        typer.echo(f"  - {name:30s} {cls.__module__}.{cls.__name__}  v{cls.version}")


@app.command(name="run")
def run_plugin(
    plugin: str = typer.Argument(..., help="插件名（spstpipe list 看得到）"),
    input_path: Path = typer.Option(..., "--input", "-i", help="输入 h5ad 文件"),
    output_path: Path = typer.Option(..., "--output", "-o", help="输出 h5ad 文件"),
) -> None:
    """跑指定插件（load → preprocess → run → save）。"""
    from spstpipe.core.io import load_anndata, save_anndata

    setup()
    plugins = discover_plugins(group="spstpipe.plugins")
    if plugin not in plugins:
        typer.echo(f"未知插件：{plugin}", err=True)
        raise typer.Exit(code=1)
    cls = plugins[plugin]
    instance = cls()
    adata = load_anndata(input_path)
    adata = instance.preprocess(adata)
    adata = instance.run(adata)
    save_anndata(adata, output_path)
    typer.echo(f"OK: {output_path}")


if __name__ == "__main__":
    app()
