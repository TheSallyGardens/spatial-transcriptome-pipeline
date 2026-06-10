# 发布到 PyPI（1.0.0-4）

> 本文档说明怎么把 `spstpipe` 1.0.0 发到 PyPI，让用户能 `pip install spstpipe`。

## 一次性准备

### 1) 注册 PyPI 账号

到 https://pypi.org/account/register/ 注册账号（用 TheSallyGardens 这个 GitHub 用户名同名）。

### 2) 启用 2FA

到 https://pypi.org/manage/account/totp/ 启用 TOTP（推荐用 Google Authenticator / Authy）。

### 3) 配置 Trusted Publishing（推荐，不需 API token）

到 https://pypi.org/manage/account/publishing/ 加一个 trusted publisher：

- **Project name**：`spstpipe`
- **Owner**：`TheSallyGardens`
- **Repository name**：`spatial-transcriptome-pipeline`
- **Workflow filename**：`publish.yml`
- **Environment name**：`pypi`

### 4) GitHub 仓库加 Environment

到 https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/settings/environments/new

- **Name**：`pypi`
- **Required reviewers**：（可选，加自己）
- **Deployment branches**：`main` / `v*` tag

## 方式 A：本地 build + 手动推

```powershell
# 1) 装工具
pip install --upgrade build twine

# 2) 跑发布脚本
.\scripts\publish_pypi.ps1
```

`publish_pypi.ps1` 会：
1. 清理 `dist/` `build/`
2. `python -m build` 出 sdist + wheel
3. `twine check dist/*` 校验
4. `twine upload dist/*` 上传（需要 PyPI 账号密码 / API token）

**干跑（推荐先跑这个）**：
```powershell
# 1) 注册 TestPyPI 账号：https://test.pypi.org/account/register/
# 2) 配 ~/.pypirc：
#    [testpypi]
#    username = __token__
#    password = pypi-AgEIcHlwaS5vcmcC...（TestPyPI API token）
# 3) twine upload --repository testpypi dist/*
# 4) 验证：pip install -i https://test.pypi.org/simple/ spstpipe
```

## 方式 B：GitHub Actions trusted publishing（推荐）

`.github/workflows/publish.yml` 已经配好，**当你在 GitHub 发一个 release 时自动触发**：

1. 到 https://github.com/TheSallyGardens/spatial-transcriptome-pipeline/releases/new
2. **Choose a tag**：`v1.0.0`（新 tag）
3. **Release title**：`spstpipe 1.0.0`
4. **Description**：复制 CHANGELOG.md 里的 1.0.0 段
5. **Publish release**

GitHub Actions 会自动：
1. 跑 `python -m build`
2. 用 trusted publishing 推到 PyPI（无需 token）
3. 完成后 PyPI 显示 https://pypi.org/project/spstpipe/

## 验证发布

发布成功后：

```powershell
# 新建一个干净的 venv 测试
python -m venv test_env
test_env\Scripts\activate
pip install spstpipe

# 验证
python -c "import spstpipe; print(spstpipe.__version__, spstpipe.__api_version__)"
# 预期：1.0.0 1.0
```

## 不发 PyPI 的替代

如果暂时不发 PyPI，用户可以：

```powershell
# 方式 1：直接从 GitHub 装
pip install git+https://github.com/TheSallyGardens/spatial-transcriptome-pipeline.git

# 方式 2：本地开发模式
git clone https://github.com/TheSallyGardens/spatial-transcriptome-pipeline.git
cd spatial-transcriptome-pipeline
pip install -e ".[dev]"
```

## 注意事项

- **不要 commit PyPI API token 到 git**
- **第一次发**：PyPI 会要求你确认 project name
- **发错了**：可以用 `yank` 标记 deprecated，但不能删
- **版本冲突**：1.0.0 已经被其他项目占了？查 https://pypi.org/project/spstpipe/

## 后续版本发布

1.0.1 / 1.1.0 / 2.0.0 同样流程：
- 改 `pyproject.toml` version
- 改 `src/spstpipe/__init__.py` 的 `__version__`
- 跑 `git tag v1.x.y` + `git push --tags`
- 在 GitHub 发 release
- trusted publishing 自动推到 PyPI
