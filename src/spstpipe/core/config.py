"""pydantic 配置模型 —— 把 config/*.yaml 解析成强类型对象。

Schema 对应仓库根 config/config.yaml + config/samples.yaml：
  - project  : 项目元信息
  - mamba    : conda 环境相关
  - plugins  : 启用的插件列表（每个含 method + params）
  - samples  : 样本列表（每个含 platform + input_dir + config）
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ProjectMeta(BaseModel):
    """项目元信息（project 段）。"""

    model_config = ConfigDict(extra="ignore")

    name: str = "spatial_transcriptome_pipeline"
    author: str = "unknown"
    date: str = ""


class MambaConfig(BaseModel):
    """conda 环境配置（mamba 段）。"""

    model_config = ConfigDict(extra="ignore")

    env_dir: str = "envs"
    create_env: bool = True


class PluginConfig(BaseModel):
    """单个插件的配置（plugins 列表元素）。"""

    model_config = ConfigDict(extra="ignore")

    name: str
    enabled: bool = True
    method: str = ""
    params: dict[str, object] = Field(default_factory=dict)


class SampleConfig(BaseModel):
    """单个样本的配置（samples 列表元素）。"""

    model_config = ConfigDict(extra="ignore")

    id: str
    platform: str
    input_dir: str
    config: dict[str, object] = Field(default_factory=dict)


class PipelineConfig(BaseModel):
    """流水线根配置（合并 config.yaml + samples.yaml 后的视图）。"""

    model_config = ConfigDict(extra="ignore")

    project: ProjectMeta = Field(default_factory=ProjectMeta)
    mamba: MambaConfig = Field(default_factory=MambaConfig)
    plugins: list[PluginConfig] = Field(default_factory=list)
    samples: list[SampleConfig] = Field(default_factory=list)


def _read_yaml(path: str | Path) -> dict[str, object]:
    """读一个 YAML 文件，注释或空文件返回空 dict。"""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} 顶层必须是 mapping，实际是 {type(data).__name__}")
    return data


def load_config(
    config_path: str | Path = "config/config.yaml",
    samples_path: str | Path = "config/samples.yaml",
) -> PipelineConfig:
    """读两份 YAML 并合并为 PipelineConfig。"""
    merged: dict[str, object] = {}
    merged.update(_read_yaml(config_path))
    merged.update(_read_yaml(samples_path))  # samples 字段在 samples.yaml 里
    return PipelineConfig.model_validate(merged)
