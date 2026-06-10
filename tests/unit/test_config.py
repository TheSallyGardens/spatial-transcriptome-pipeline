"""pydantic 配置模型的测试。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from spstpipe.core.config import (
    PipelineConfig,
    PluginConfig,
    SampleConfig,
    load_config,
)


def test_最小有效配置_可以通过():
    """空 samples 列表是合法的最小配置。"""
    cfg = PipelineConfig.model_validate({"samples": []})
    assert cfg.samples == []
    assert cfg.plugins == []


def test_缺_samples_字段_默认是空列表():
    """缺 samples 字段时走默认值（空列表），不报错。"""
    cfg = PipelineConfig.model_validate({})
    assert cfg.samples == []
    assert cfg.plugins == []
    assert cfg.project.name == "spatial_transcriptome_pipeline"


def test_解析_完整配置():
    """能完整解析 config.yaml + samples.yaml 的合集。"""
    raw = {
        "project": {
            "name": "sp",
            "author": "alice",
            "date": "2026-06-09",
        },
        "mamba": {"env_dir": "envs", "create_env": True},
        "plugins": [
            {
                "name": "spatial_domain",
                "enabled": True,
                "method": "spagcn",
                "params": {"resolution": 0.5},
            },
            {"name": "trajectory", "enabled": False, "method": "paga", "params": {}},
        ],
        "samples": [
            {
                "id": "s1",
                "platform": "10x_visium",
                "input_dir": "data/s1",
                "config": {"min_genes": 200, "min_cells": 50},
            }
        ],
    }
    cfg = PipelineConfig.model_validate(raw)
    assert cfg.project is not None and cfg.project.name == "sp"
    assert len(cfg.plugins) == 2
    assert cfg.plugins[0].name == "spatial_domain"
    assert cfg.plugins[0].method == "spagcn"
    assert len(cfg.samples) == 1
    assert cfg.samples[0].id == "s1"
    assert cfg.samples[0].platform == "10x_visium"


def test_SampleConfig_校验_必填字段():
    """id / platform / input_dir 都必须有。"""
    with pytest.raises(ValidationError):
        SampleConfig.model_validate({"id": "x"})


def test_PluginConfig_默认_方法为空字符串():
    """method 缺省时是空串。"""
    p = PluginConfig.model_validate({"name": "x", "enabled": True})
    assert p.method == ""
    assert p.params == {}


def test_load_config_读_项目内的_yaml():
    """load_config('config/config.yaml', 'config/samples.yaml') 能跑通。"""
    cfg = load_config("config/config.yaml", "config/samples.yaml")
    assert len(cfg.samples) == 2
    assert len(cfg.plugins) == 6
    assert cfg.samples[0].id == "sample1"
    assert cfg.samples[0].platform == "10x_visium"
    assert cfg.samples[1].platform == "stereo_seq"
