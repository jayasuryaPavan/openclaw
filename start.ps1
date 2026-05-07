Set-Location $PSScriptRoot

$env:PORT=18789
$env:OPENCLAW_CONFIG_PATH="openclaw.json"

# Check if .env exists and load it to set additional variables if needed
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)\s*=\s*(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"').Trim("'")
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Ensure Python is in PATH for capability checks
$env:PATH = "C:\Python314;C:\Python314\Scripts;" + $env:PATH

$url = "http://localhost:$env:PORT/panda/"

# ── Check if gateway is already running and serving the panda UI ──
$alreadyRunning = $false
try {
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($resp.StatusCode -eq 200) {
        $alreadyRunning = $true
    }
} catch { }

if ($alreadyRunning) {
    Write-Host "[gateway] Already running, opening browser..." -ForegroundColor Green
    Start-Process $url
    exit 0
}

# ── Kill anything else holding port 18789 ──
$portPids = @()
try {
    $portPids = Get-NetTCPConnection -LocalPort $env:PORT -ErrorAction Stop |
                Select-Object -ExpandProperty OwningProcess -Unique
} catch { }

if ($portPids.Count -gt 0) {
    Write-Host "[gateway] Killing process(es) on port $env:PORT : $($portPids -join ', ')" -ForegroundColor Yellow
    foreach ($procId in $portPids) {
        if ($procId -and $procId -ne 0) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

# ── Start quota reminder in the background ──
$quotaScript = Join-Path $PSScriptRoot "scripts\quota_reminder.py"
if (Test-Path $quotaScript) {
    Start-Process -FilePath "python" -ArgumentList $quotaScript `
        -WindowStyle Hidden -PassThru | Out-Null
    Write-Host "[quota-reminder] Started in background." -ForegroundColor Cyan
}

# ── Build Panda UI if not already built ──
$pandaBuild = Join-Path $PSScriptRoot "dist\panda-ui\index.html"
if (-not (Test-Path $pandaBuild)) {
    Write-Host "[panda-ui] Building UI..." -ForegroundColor Cyan
    pnpm panda-ui:build
}

# ── Start gateway in background ──
$gatewayJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    $env:PORT = 18789
    $env:OPENCLAW_CONFIG_PATH = "openclaw.json"
    node scripts/run-node.mjs gateway
} -ArgumentList $PSScriptRoot

Write-Host "[gateway] Starting on port $env:PORT..." -ForegroundColor Green

# ── Poll until gateway is up then open browser ──
$maxWait = 20
$waited = 0
$opened = $false
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 1
    $waited++
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Host "[panda-ui] Opening $url" -ForegroundColor Green
            Start-Process $url
            $opened = $true
            break
        }
    } catch { }
}

if (-not $opened) {
    Write-Host "[panda-ui] Gateway took too long - open manually: $url" -ForegroundColor Yellow
}

# Keep running and forward gateway output
Receive-Job $gatewayJob -Wait -AutoRemoveJob
