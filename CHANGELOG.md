# 更新日志

所有重要变更都记录在这里。版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-06-10

### 重磅
- **API 冻结**：从 1.0.0 起，公共 API 签名不再破坏性变化
  - `spstpipe.__version__ = "1.0.0"`
  - `spstpipe.__api_version__ = "1.0"`（只增不减）
  - `from spstpipe import BasePlugin, discover_plugins` 成为稳定导入路径
- **6 个内置插件全部接入真方法**（graceful degradation 保留占位兜底）：
  - `spatial_domain` → squidpy + leiden
  - `spatial_variable_genes` → squidpy Moran's I
  - `cell_communication` → squidpy ligrec
  - `trajectory` → scanpy PAGA + DPT
  - `multi_sample_integration` → scanpy harmony
  - `scrna_joint_analysis` → scanpy ingest (label transfer)
- **端到端 demo**：`examples/synthetic_end_to_end.py`（6 plugin 串跑）

### 改动
- 0.3.0-1 到 0.3.0-6：6 个 plugin 抽 `algorithms.py`，加占位 / squidpy / scanpy 三档真方法
- 0.3.0-7：写 examples demo
- 0.3.0-8：CI 加 mypy job + 装 spatial extras
- 1.0.0-1：API 冻结 + docs/API.md
- `pyproject.toml` mypy overrides 加 `squidpy` / `scanpy.external`
- `addopts` 加 `-m "not slow"`：默认 skip 慢测试（CI 友好）
- `pyproject.toml` version 升 `1.0.0`

### 测试
- 43 passed, 9 skipped, 8 deselected
- `test_spstpipe_version_已发布_1_0`：验证 `__version__` / `__api_version__`
- `test_spstpipe_公开API_可导入`：验证 BasePlugin / discover_plugins 顶层导入 + `__all__`

### 文档
- 新 `docs/API.md`：稳定 API / 实验性 API / 内部（不导出）/ 升级路径
- `docs/ROADMAP.md` 标完 0.2.0 / 0.3.0；1.0.0 子任务拆 7 项
- 中英双语翻译留到 1.0.0-5

## [未发布] / Unreleased

### 卫生
- `ruff format` 统一 41 个文件的格式
- `mypy --strict` 通过（0 errors, 22 source files）：修了 18 个类型问题
  - `anndata` / `scanpy` / `scipy` / `sklearn` / `loguru` 在 [[tool.mypy.overrides]] 中声明 `ignore_missing_imports`（缺 py.typed 或 stubs）
  - 修 `loguru.logger` 不能当类型用：`setup()` 返回 `Any`
  - 修 `registry.py` `eps.get()` 的 `type: ignore` 标注（用 `arg-type` 替代 `union-attr`，删未用项）
  - 修 `spatial_domain/algorithms.py` `calculate_adj_matrix` 缺类型注解：补 `numpy.typing.NDArray` 标注
  - 修 `scrna_joint_analysis/plugin.py` 永真 `if str` 和永假字符串相等比较：清理为直接赋值
  - 修 `spatial_domain/plugin.py` 把 `**kwargs` 强转成 `float` 传给 `run_spectral_clustering` 的类型不匹配：改显式 `isinstance` 守卫

### 测试
- `conftest.py` 改用 `pytest-of-{user}` 子目录探测 sandbox Temp 权限：原探测根 Temp 不可靠（根可写但 pytest 9 创建的子目录被 DACL 拒绝）
- 本地 sandbox：36 passed, 7 skipped；CI/Linux：43 passed

### 文档
- 新 `CONTRIBUTING.md`：开发环境、跑测试、加新插件、CI 流程
- 新 `docs/ROADMAP.md`：0.2.0 / 0.3.0 / 1.0 计划
