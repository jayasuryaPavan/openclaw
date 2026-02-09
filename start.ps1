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

node scripts/run-node.mjs gateway
