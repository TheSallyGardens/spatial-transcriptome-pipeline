"""插件注册表 —— 通过 Python entry-points 动态发现插件。

用法：
  plugins = discover_plugins("spstpipe.plugins")
  for name, cls in plugins.items():
      instance = cls()
      result = instance.run(adata)

entry-point 声明见 pyproject.toml 的 [project.entry-points."<group>"] 节。
"""

from __future__ import annotations

from importlib import metadata

from spstpipe.core.base import BasePlugin


def discover_plugins(group: str) -> dict[str, type[BasePlugin]]:
    """发现指定 entry-point 组里的所有 BasePlugin 子类。

    返回 {plugin_name: plugin_class}。组不存在或没有条目时返回空字典。
    加载失败的 entry-point 会被跳过（不抛错），由调用方在插件构造时再处理。
    """
    result: dict[str, type[BasePlugin]] = {}
    eps = metadata.entry_points()
    # Python 3.10+ 用 eps.select(group=...)；3.9 用 eps.get(group, [])
    try:
        entries = eps.select(group=group)
    except AttributeError:
        entries = eps.get(group, [])  # type: ignore[arg-type]
    for ep in entries:
        try:
            obj = ep.load()
        except Exception:
            # 加载失败的 entry-point（导入错误等）跳过
            continue
        if isinstance(obj, type) and issubclass(obj, BasePlugin):
            key = obj.name or ep.name
            result[key] = obj
    return result
