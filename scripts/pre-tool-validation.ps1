# Pre-tool validation to ensure safe execution

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

# Log tool usage
New-Item -ItemType Directory -Force -Path logs | Out-Null
Add-Content -Path logs/tool-usage.log -Value "[$Timestamp] Pre-tool validation: $ToolName"

# Validate specific tools
switch ($ToolName) {
    {$_ -in @("file_edit", "file_create")} {
        if ($PWD.Path -notmatch "AutoFinance") {
            Write-Host "⚠️  Warning: Tool $ToolName used outside project directory" -ForegroundColor Yellow
        }
    }
    {$_ -in @("bash", "shell")} {
        Add-Content -Path logs/shell-commands.log -Value "[$Timestamp] Shell command requested"
    }
}

# Return success
$output = @{
    validated = $true
    toolName = $ToolName
    timestamp = $Timestamp
} | ConvertTo-Json -Compress

Write-Output $output
