"""BasePlugin 抽象类 —— 所有空间转录组分析插件的契约。

每个插件必须实现四个方法：
  - load(paths)              : 读入原始数据（10x Visium / Stereo-seq / h5ad），返回 AnnData
  - preprocess(adata)        : 质控、归一化、标准化等，返回新的 AnnData
  - run(adata)               : 核心算法（聚类、轨迹推断等），返回带结果注释的 AnnData
  - save(adata, path)        : 把结果写盘

__call__ 直接代理到 run(adata)，让插件实例可以当函数用。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import anndata as ad


class BasePlugin(ABC):
    """空间转录组分析插件的抽象基类。"""

    #: 插件名（小写、下划线分隔），注册表里靠它索引。
    name: ClassVar[str] = ""

    #: 插件版本（语义化版本号）。
    version: ClassVar[str] = "0.1.0"

    @abstractmethod
    def load(self, paths: list[Path]) -> ad.AnnData:
        """读入原始数据，返回 AnnData。"""
        raise NotImplementedError

    @abstractmethod
    def preprocess(self, adata: ad.AnnData) -> ad.AnnData:
        """预处理（QC / 归一化 / 标准化等）。"""
        raise NotImplementedError

    @abstractmethod
    def run(self, adata: ad.AnnData) -> ad.AnnData:
        """跑核心算法，返回带结果注释的 AnnData。"""
        raise NotImplementedError

    @abstractmethod
    def save(self, adata: ad.AnnData, path: Path) -> None:
        """把结果写到指定路径。"""
        raise NotImplementedError

    def __call__(self, adata: ad.AnnData) -> ad.AnnData:
        """便捷调用：plugin(adata) 等价于 plugin.run(adata)。"""
        return self.run(adata)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} version={self.version}>"