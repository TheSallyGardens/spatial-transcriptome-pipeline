# publish_pypi.ps1 — 发 spstpipe 到 PyPI

# 一次性准备：
#   1) 注册 PyPI 账号：https://pypi.org/account/register/
#   2) 在 https://pypi.org/manage/account/totp/ 启用 2FA（推荐）
#   3) 在 https://pypi.org/manage/account/publishing/ 加 trusted publisher：
#      - Project: spstpipe
#      - Owner: TheSallyGardens
#      - Repository: spatial-transcriptome-pipeline
#      - Workflow: publish.yml
#      - Environment: pypi
#   4) 在 GitHub repo 加 Environment "pypi"

# 跑这个脚本：

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

# 1) 装 build + twine
pip install --upgrade build twine

# 2) 清理 + build sdist + wheel
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
python -m build

# 3) 检查 sdist 内容
twine check dist/*

# 4) 干跑（TestPyPI）
# twine upload --repository testpypi dist/*

# 5) 正式发（PyPI）
# twine upload dist/*
