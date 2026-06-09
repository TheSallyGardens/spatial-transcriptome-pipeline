from __future__ import annotations

# tests/test_end_to_end.py
import pytest
import scanpy as sc
from pathlib import Path
import sys
import yaml

# 添加workflow/scripts到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow" / "scripts"))

def test_config_files_exist():
    """测试配置文件是否存在"""
    config_dir = Path(__file__).parent.parent / "config"
    assert (config_dir / "config.yaml").exists()
    assert (config_dir / "samples.yaml").exists()

def test_samples_config_valid():
    """测试samples.yaml格式是否有效"""
    config_dir = Path(__file__).parent.parent / "config"
    with open(config_dir / "samples.yaml") as f:
        samples = yaml.safe_load(f)
    assert "samples" in samples
    assert len(samples["samples"]) > 0
    for sample in samples["samples"]:
        assert "id" in sample
        assert "platform" in sample
        assert sample["platform"] in ["10x_visium", "stereo_seq"]

def test_main_config_valid():
    """测试config.yaml格式是否有效"""
    config_dir = Path(__file__).parent.parent / "config"
    with open(config_dir / "config.yaml") as f:
        config = yaml.safe_load(f)
    assert "project" in config
    assert "plugins" in config
    assert len(config["plugins"]) > 0

def test_plugin_config_exists():
    """测试所有插件配置是否存在"""
    plugins_dir = Path(__file__).parent.parent / "plugins"
    expected_plugins = [
        "spatial_domain",
        "cell_communication",
        "trajectory",
        "spatial_variable_genes",
        "multi_sample_integration",
        "scRNA_joint_analysis"
    ]
    for plugin in expected_plugins:
        config_file = plugins_dir / plugin / "config.yaml"
        assert config_file.exists(), f"Missing config for {plugin}"

def test_env_files_exist():
    """测试conda环境文件是否存在"""
    envs_dir = Path(__file__).parent.parent / "envs"
    assert (envs_dir / "scanpy.yaml").exists()
    assert (envs_dir / "r-seurat.yaml").exists()

def test_snakefile_syntax():
    """测试Snakefile语法是否正确"""
    snakefile = Path(__file__).parent.parent / "Snakefile"
    assert snakefile.exists()
    content = snakefile.read_text()
    assert "configfile:" in content
    assert "rule all:" in content

def test_load_data_functions():
    """测试load_data函数签名"""
    from load_data import load_10x_visium, load_stereo_seq
    assert callable(load_10x_visium)
    assert callable(load_stereo_seq)

def test_preprocessing_functions():
    """测试preprocessing函数签名"""
    from preprocessing import (
        filter_cells_and_genes,
        normalize_total,
        log_transform,
        highly_variable_genes,
        scale_data
    )
    assert callable(filter_cells_and_genes)
    assert callable(normalize_total)
    assert callable(log_transform)
    assert callable(highly_variable_genes)
    assert callable(scale_data)
