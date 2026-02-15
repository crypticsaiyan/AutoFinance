# Post-tool check to verify successful execution

# Read JSON input from stdin
$InputData = $input | Out-String

# Extract tool information
try {
    $Json = $InputData | ConvertFrom-Json
    $ToolName = $Json.toolName
} catch {
    $ToolName = "unknown"
}

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log completion
New-Item -ItemType Directory -Force -Path logs | Out-Null
Add-Content -Path logs/tool-usage.log -Value "[$Timestamp] Post-tool check: $ToolName completed"

# Run specific checks based on tool
switch ($ToolName) {
    {$_ -in @("file_edit", "file_create")} {
        # Check if Python files have syntax errors
        Get-ChildItem -Filter "*.py" -ErrorAction SilentlyContinue | ForEach-Object {
            $result = python -m py_compile $_.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "⚠️  Syntax error in $($_.Name)" -ForegroundColor Yellow
            }
        }
    }
    "pip_install" {
        Write-Host "Verifying pip packages..."
        pip check 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Dependency issues detected" -ForegroundColor Yellow
        }
    }
}

# Return success
$output = @{
    checked = $true
    toolName = $ToolName
    timestamp = $Timestamp
} | ConvertTo-Json -Compress

Write-Output $output
