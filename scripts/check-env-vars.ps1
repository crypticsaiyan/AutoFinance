# Check environment variables required for AutoFinance

Write-Host "Checking required environment variables..."

# List of required API keys
$RequiredVars = @(
    "ALPHA_VANTAGE_API_KEY",
    "FINNHUB_API_KEY",
    "POLYGON_API_KEY",
    "NEWS_API_KEY"
)

$MissingVars = @()

foreach ($var in $RequiredVars) {
    if (-not (Test-Path "env:$var")) {
        $MissingVars += $var
    }
}

if ($MissingVars.Count -gt 0) {
    Write-Host "⚠️  Warning: Missing environment variables:" -ForegroundColor Yellow
    foreach ($var in $MissingVars) {
        Write-Host "  - $var"
    }
    Write-Host ""
    Write-Host "Some MCP servers may not function properly."
    Write-Host "Please set these in your .env file."
} else {
    Write-Host "✅ All required environment variables are set" -ForegroundColor Green
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Create one from .env.example if available"
}

exit 0
