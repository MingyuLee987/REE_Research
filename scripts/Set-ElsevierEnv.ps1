$envFile = Join-Path (Split-Path $PSScriptRoot -Parent) '.env'
if (-not (Test-Path -LiteralPath $envFile)) {
    throw 'Missing .env. Copy .env.example to .env and set ELSEVIER_API_KEY.'
}

$variables = @('ELSEVIER_API_KEY', 'SPRINGER_OPEN_ACCESS_API_KEY', 'SPRINGER_META_API_KEY', 'WILEY_TDM_TOKEN', 'OPENAI_API_KEY', 'OPENAI_MODEL', 'OPENAI_SCREENING_MODEL')
foreach ($variable in $variables) {
    $keyLine = Get-Content -LiteralPath $envFile | Where-Object { $_ -match ('^' + $variable + '=') } | Select-Object -First 1
    if (-not $keyLine) { continue }
    $apiKey = ($keyLine -split '=', 2)[1].Trim().Trim('"').Trim("'")
    if ($apiKey -and -not $apiKey.StartsWith('your_')) {
        [Environment]::SetEnvironmentVariable($variable, $apiKey, 'Process')
        Write-Host "$variable loaded for this PowerShell session."
    }
}
