# Log user prompts for analytics and debugging

# Read JSON input from stdin
$Input = $input | Out-String

# Extract relevant information
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Log the prompt
Add-Content -Path logs/prompts.log -Value "[$Timestamp] User prompt submitted"

# Output JSON for Copilot
$output = @{
    logged = $true
    timestamp = $Timestamp
} | ConvertTo-Json -Compress

Write-Output $output
