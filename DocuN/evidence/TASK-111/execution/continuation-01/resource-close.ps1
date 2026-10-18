$ErrorActionPreference = 'Stop'
$receiptRoot = 'D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-01'
$checkStarted = [System.Diagnostics.Stopwatch]::GetTimestamp()
$resourceErrors = @()
$resourcePG = $null
$resourceImage = $null
$resourcePreviews = @()
$dockerBinary = (Get-Command docker.exe).Source
try {
    $resourceRaw = & $dockerBinary inspect --type container --format '{"id":{{json .Id}},"name":{{json .Name}},"image":{{json .Image}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"status":{{json .State.Status}},"restarts":{{json .RestartCount}}}' '1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51' 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'PG exact inspect refused' }
    $resourcePG = ($resourceRaw -join "`n") | ConvertFrom-Json
    if ($resourcePG.id -ne '1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51' -or $resourcePG.name -ne '/retrolume-task-111-g11-v2-pg1' -or $resourcePG.image -ne 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f') { throw 'PG binding mismatch' }
} catch { $resourceErrors += 'PG_inspect_unknown' }
try {
    $resourceRaw = & $dockerBinary image inspect --format '{"id":{{json .Id}},"os":{{json .Os}},"arch":{{json .Architecture}}}' 'sha256:8ec35cf6df9c13eef0c3b15567e72ac0cd7382c19b586469cb4aaca48e8ef015' 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'image inspect refused' }
    $resourceImage = ($resourceRaw -join "`n") | ConvertFrom-Json
} catch { $resourceErrors += 'renderer_image_unknown' }
try {
    $resourceRaw = & $dockerBinary ps --all --filter 'name=retrolume-task-111-g11-preview-' --format '{{json .}}' 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'preview listing refused' }
    foreach ($containerLine in $resourceRaw) {
        if ([string]::IsNullOrWhiteSpace([string]$containerLine)) { continue }
        $containerRow = $containerLine | ConvertFrom-Json
        if ($containerRow.Names -match '^retrolume-task-111-g11-preview-(0[1-9]|1[0-4])$') {
            $resourcePreviews += [ordered]@{ id=$containerRow.ID; name=$containerRow.Names; state=$containerRow.State; status=$containerRow.Status }
        }
    }
} catch { $resourceErrors += 'preview_inventory_unknown' }
$resourceListeners = @()
try {
    $resourceListeners = @(Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(18111,55451) } | Select-Object LocalAddress,LocalPort,OwningProcess)
} catch { $resourceErrors += 'listeners_unknown' }
$resourceProcesses = @()
try {
    $resourceProcesses = @(Get-CimInstance Win32_Process | Where-Object {
        $_.ProcessId -ne $PID -and $_.Name -match '^(python(w)?|node|docker|powershell|pwsh)\.exe$' -and
        $_.CommandLine -match '(tests[\\./]fixtures[\\./]task111|tests\.fixtures\.task111|retrolume-task-111-g11|frontend[\\/]tests[\\/]task111)'
    } | ForEach-Object { [ordered]@{ pid=$_.ProcessId; ppid=$_.ParentProcessId; name=$_.Name; birth_utc=$_.CreationDate.ToUniversalTime().ToString('o') } })
} catch { $resourceErrors += 'host_process_inventory_unknown' }
$checkSeconds = ([System.Diagnostics.Stopwatch]::GetTimestamp() - $checkStarted) / [System.Diagnostics.Stopwatch]::Frequency
$receipt = [ordered]@{
    permit='TASK-111-G11-C01-20261010'; at_utc=[DateTime]::UtcNow.ToString('o'); seconds=$checkSeconds
    read_only=$true; pg=$resourcePG; renderer_image=$resourceImage; previews=$resourcePreviews
    listeners=$resourceListeners; matching_processes=$resourceProcesses; errors=$resourceErrors
    new_resources_started=$false
    scope='精确任务对象与限定主机元数据；不读完整Env或口令、不启动或重启、不声明动态TreeProof或持久预算结算'
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath "$receiptRoot/resource-close.json" -Encoding UTF8
$receipt | ConvertTo-Json -Depth 8
