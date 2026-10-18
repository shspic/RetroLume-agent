$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $env:RETROLUME_DATA_DIR -or -not $env:RETROLUME_BACKUP_DIR) {
    throw "请先在当前会话设置 RETROLUME_DATA_DIR 和 RETROLUME_BACKUP_DIR；不要把资料目录提交到项目内。"
}
if (-not $env:RETROLUME_DATABASE_URL) {
    $databaseConfig = Join-Path $projectRoot "config/database.local.json"
    if (Test-Path -LiteralPath $databaseConfig) {
    $env:RETROLUME_DATABASE_URL = (Get-Content -LiteralPath $databaseConfig -Raw | ConvertFrom-Json).url
    }
}
Push-Location (Join-Path $projectRoot "backend")
try {
    & .\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --loop app.runtime:psycopg_compatible_loop_factory --host 127.0.0.1 --port 8000
} finally {
    Pop-Location
}
