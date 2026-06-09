# CLI 的测试（用 typer.testing.CliRunner）
from __future__ import annotations

from typer.testing import CliRunner

from spstpipe.cli import app

runner = CliRunner()


def test_list_能跑通():
    """list 子命令至少应该退出码 0。"""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0, result.stdout


def test_list_显示_帮助文字():
    """help 里应该能看到 list 子命令。"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout