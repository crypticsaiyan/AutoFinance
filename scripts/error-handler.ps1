# Error handler for Copilot CLI

# Read JSON input from stdin
$InputData = $input | Out-String

# Extract error information
try {
    $Json = $InputData | ConvertFrom-Json
    $ErrorMsg = $Json.error
} catch {
    $ErrorMsg = "Unknown error"
}

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log error
New-Item -ItemType Directory -Force -Path logs | Out-Null
Add-Content -Path logs/copilot-errors.log -Value "[$Timestamp] ERROR: $ErrorMsg"

# Check for common issues
if ($ErrorMsg -match "API") {
    Write-Host "💡 Tip: Check your API credentials in .env file" -ForegroundColor Cyan
} elseif ($ErrorMsg -match "connection") {
    Write-Host "💡 Tip: Check your network connection and MCP server status" -ForegroundColor Cyan
} elseif ($ErrorMsg -match "import") {
    Write-Host "💡 Tip: Try running 'pip install -r requirements.txt'" -ForegroundColor Cyan
}

# Return error metadata
$output = @{
    handled = $true
    timestamp = $Timestamp
    errorLogged = $true
} | ConvertTo-Json -Compress

Write-Output $output
