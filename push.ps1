<#
.SYNOPSIS
  把本地仓库推到 GitHub（用 SSH v4 deploy key）。

.DESCRIPTION
  这个脚本使用项目内 .ssh/id_ed25519_v4 私钥（Deploy Key）。
  GitHub 仓库里必须已经加过 v4 公钥（指纹 SHA256:yBh1qVUx+iCDZDrHKmDENr+0u6p2+ndy75muRVZA0Ds，标题 spstpipe-deploy-key-2026，Allow write access 勾上）。

  在你自己 PowerShell 窗口里跑（不是 Codex 内置终端）：

    Set-Location -LiteralPath "D:\project\spatial-transcriptome-pipeline-main"
    .\push.ps1

  脚本会：
    1. 自检 .git / .ssh\id_ed25519_v4 / 远端
    2. 打印 ahead / behind / dirty 状态
    3. 设置 core.sshCommand 永久指 v4 私钥
    4. 用 ssh -T 探测认证
    5. 必要时 git pull --rebase --autostash
    6. git push -u origin main
#>

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "    [!]  $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "    [X]  $msg" -ForegroundColor Red }

# ---- 1. Preflight -----------------------------------------------------------
Step "Preflight checks"
if (-not (Test-Path -LiteralPath ".git")) {
    Fail "Not a git repository (missing .git). Run this from the project root."
    exit 1
}
if (-not (Test-Path -LiteralPath ".ssh\id_ed25519_v4")) {
    Fail "Missing .ssh\id_ed25519_v4. The agent should have placed it here."
    exit 1
}
if (-not (Test-Path -LiteralPath ".ssh\id_ed25519_v4.pub")) {
    Fail "Missing .ssh\id_ed25519_v4.pub (public key)."
    exit 1
}
Ok "Repo and SSH v4 deploy key present."

# ---- 2. Repo state ---------------------------------------------------------
Step "Repo state"
git rev-parse --is-inside-work-tree | Out-Null
$branch  = (git rev-parse --abbrev-ref HEAD).Trim()
$remote  = (git remote get-url origin 2>$null)
$ahead   = (git rev-list --count "origin/$branch..$branch" 2>$null)
$behind  = (git rev-list --count "$branch..origin/$branch" 2>$null)
$status  = (git status --porcelain)

Write-Host "    Branch : $branch"
Write-Host "    Remote : $remote"
Write-Host "    Ahead  : $ahead commit(s) ahead of origin/$branch"
Write-Host "    Behind : $behind commit(s) behind origin/$branch"
if ($status) { Warn "Working tree is dirty:" ; $status | ForEach-Object { Write-Host "           $_" } }

# ---- 3. Set core.sshCommand to v4 key -------------------------------------
$keyPath  = (Resolve-Path ".ssh\id_ed25519_v4").Path
$confPath = (Resolve-Path ".ssh\config").Path
$knownHosts = Join-Path $PSScriptRoot ".ssh\known_hosts"

Step "Configuring git core.sshCommand (v4 key)"
$sshCmd = "ssh -i `"$keyPath`" -F `"$confPath`" -o IdentitiesOnly=yes -o UserKnownHostsFile=`"$knownHosts`" -o StrictHostKeyChecking=accept-new"
git config core.sshCommand $sshCmd
Ok "core.sshCommand set."

# ---- 4. Quick connectivity probe ------------------------------------------
Step "Testing SSH authentication to github.com"
# ssh -T 认证成功时退出码 1（GitHub 不给 shell）。用 cmd /c 调，PowerShell 不会因 ssh 非零退出抛异常。2>&1 把 stderr 合到 stdout。
$probe = cmd /c "ssh -i `"$keyPath`" -F `"$confPath`" -o IdentitiesOnly=yes -o UserKnownHostsFile=`"$knownHosts`" -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1"
if ($probe -match "successfully authenticated") {
    Ok "GitHub acknowledged the v4 key."
} else {
    Warn "Probe did not show a clean success line:"
    $probe | ForEach-Object { Write-Host "           $_" }
    $ans = Read-Host "    Continue anyway? (y/N)"
    if ($ans -ne "y") { Fail "Aborted by user." ; exit 1 }
}

# ---- 5. Pull (rebase) if behind, then push --------------------------------
if ($behind -gt 0) {
    Step "Pulling $behind commit(s) from origin/$branch with rebase"
    git pull --rebase --autostash origin $branch
    if ($LASTEXITCODE -ne 0) { Fail "Pull failed. Resolve conflicts and re-run." ; exit 1 }
    Ok "Rebase done."
}

Step "Pushing $branch -> origin/$branch"
git push -u origin $branch
if ($LASTEXITCODE -ne 0) {
    Fail "git push failed. Scroll up for the error."
    exit 1
}
Ok "Push complete."

Step "Done"
Write-Host "    Verify at: https://github.com/TheSallyGardens/spatial-transcriptome-pipeline"
