<#
.SYNOPSIS
  Push the local repo to GitHub via SSH.

.DESCRIPTION
  Idempotent push helper for the spatial-transcriptome-pipeline repo.
  Uses the SSH key that lives in ./.ssh/id_ed25519 (already added to the
  GitHub account by the user).

  Run this in PowerShell 5+ (Windows PowerShell) or PowerShell 7+.

  First run will add GitHub to known_hosts (under your user profile).
  If git complains about line-ending warnings, that is normal on Windows.
#>

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "    [!]  $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "    [X]  $msg" -ForegroundColor Red }

# ---- 1. Preflight -----------------------------------------------------------
Step "Preflight checks"
if (-not (Test-Path -LiteralPath '.git')) {
    Fail "Not a git repository (missing .git). Run this from the project root."
    exit 1
}
if (-not (Test-Path -LiteralPath '.ssh\id_ed25519')) {
    Fail "Missing .ssh\id_ed25519. The agent should have placed it here."
    exit 1
}
if (-not (Test-Path -LiteralPath '.ssh\id_ed25519.pub')) {
    Fail "Missing .ssh\id_ed25519.pub (public key)."
    exit 1
}
Ok "Repo and SSH key present."

# ---- 2. Show repo state -----------------------------------------------------
Step "Repo state"
git rev-parse --is-inside-work-tree | Out-Null
$branch  = (git rev-parse --abbrev-ref HEAD).Trim()
$remote  = (git remote get-url origin 2>$null)
$status  = (git status --porcelain)
$ahead   = (git rev-list --count "origin/$branch..$branch" 2>$null)
$behind  = (git rev-list --count "$branch..origin/$branch" 2>$null)

Write-Host "    Branch : $branch"
Write-Host "    Remote : $remote"
Write-Host "    Ahead  : $ahead commit(s) ahead of origin/$branch"
Write-Host "    Behind : $behind commit(s) behind origin/$branch"
if ($status) { Warn "Working tree is dirty:" ; $status | ForEach-Object { Write-Host "           $_" } }

# ---- 3. Tell git to use the project-local SSH config + key -----------------
# The key already corresponds to a public key on the GitHub account.
# Pin IdentityFile explicitly so OpenSSH never falls back to a wrong key.
Step "Configuring git core.sshCommand"
$keyPath  = (Resolve-Path '.ssh\id_ed25519').Path
$confPath = (Resolve-Path '.ssh\config').Path
$sshCmd   = "ssh -i `"$keyPath`" -F `"$confPath`" -o IdentitiesOnly=yes -o UserKnownHostsFile=`"$PSScriptRoot\.ssh\known_hosts`" -o StrictHostKeyChecking=accept-new"
git config core.sshCommand $sshCmd
Ok "core.sshCommand set."

# ---- 4. Quick connectivity probe (non-destructive) -------------------------
Step "Testing SSH authentication to github.com"
$probe = ssh -i $keyPath -F $confPath -o IdentitiesOnly=yes -o UserKnownHostsFile="$PSScriptRoot\.ssh\known_hosts" -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1
if ($LASTEXITCODE -ne 0 -and $probe -notmatch "successfully authenticated") {
    Warn "Probe returned non-zero. Output:"
    $probe | ForEach-Object { Write-Host "           $_" }
    $ans = Read-Host "    Continue anyway? (y/N)"
    if ($ans -ne 'y') { Fail "Aborted by user." ; exit 1 }
} elseif ($probe -match "successfully authenticated") {
    Ok "GitHub acknowledged the key."
} else {
    Warn "Probe did not show a clean success line. Continuing cautiously."
}

# ---- 5. Make sure the local branch tracks origin/$branch -------------------
Step "Ensuring upstream tracking"
try {
    $up = (git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null)
    if ($up) { Ok "Already tracking $up" } else { throw "no upstream" }
} catch {
    Write-Host "    No upstream set; will use: git push -u origin $branch"
}

# ---- 6. Pull (rebase) if behind, then push ---------------------------------
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
