$ErrorActionPreference = 'Stop'
$out114 = Split-Path -Parent $PSCommandPath
$pg114 = (& docker image inspect 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f' | ConvertFrom-Json)[0]
if ($LASTEXITCODE -ne 0) { throw 'PG image identity unavailable' }
$preview114 = (& docker image inspect 'sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789' | ConvertFrom-Json)[0]
if ($LASTEXITCODE -ne 0) { throw 'accepted preview image unavailable' }
$prior114 = (& docker inspect '1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51' | ConvertFrom-Json)[0]
if ($LASTEXITCODE -ne 0) { throw 'prior owned PG identity unavailable' }
$names114 = @(& docker ps -a --format '{{.Names}}' --filter 'name=retrolume-task-114')
if ($LASTEXITCODE -ne 0) { throw 'task namespace metadata unavailable' }
$ports114 = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {($_.LocalPort -ge 55461 -and $_.LocalPort -le 55469) -or $_.LocalPort -eq 18114 -or $_.LocalPort -eq 15114} | Select-Object LocalAddress,LocalPort,OwningProcess)
$os114 = Get-CimInstance Win32_OperatingSystem
$cpu114 = @(Get-CimInstance Win32_Processor | Select-Object NumberOfLogicalProcessors)
$disk114 = Get-PSDrive -Name D
$observation114 = [ordered]@{
    at=(Get-Date).ToString('o')
    kind='read-only resource metadata; no product or resource started'
    pg_image=[ordered]@{Id=$pg114.Id;OS=$pg114.Os;Architecture=$pg114.Architecture;Digests=$pg114.RepoDigests;DeclaredVersion=@($pg114.Config.Env | Where-Object {$_ -match '^PG_(MAJOR|VERSION)='})}
    preview_image=[ordered]@{Id=$preview114.Id;OS=$preview114.Os;Architecture=$preview114.Architecture}
    prior_owned_pg_untouched=[ordered]@{Id=$prior114.Id;Name=$prior114.Name;Image=$prior114.Image;Running=$prior114.State.Running;Pid=$prior114.State.Pid}
    new_task_namespace_existing_names=$names114
    new_task_listening_ports=$ports114
    host=[ordered]@{TotalVisibleMemoryKiB=$os114.TotalVisibleMemorySize;FreePhysicalMemoryKiB=$os114.FreePhysicalMemory;CPU=$cpu114;DriveDFreeBytes=$disk114.Free}
    Config_Env_dumped=$false
    execution_permission_created_by_observation=$false
}
$observation114 | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $out114 'resource-observation.json') -Encoding utf8
[ordered]@{pg_image=$pg114.Id;preview_image=$preview114.Id;namespace_matches=$names114.Count;port_conflicts=$ports114.Count;prior_pg_running=$prior114.State.Running;free_memory_KiB=$os114.FreePhysicalMemory;resources_started=0} | ConvertTo-Json
