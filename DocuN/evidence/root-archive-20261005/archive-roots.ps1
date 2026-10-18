param([ValidateSet('Copy','Remove')][string]$Phase = 'Copy')
$ErrorActionPreference = 'Stop'
$taskArchiveRoot = [IO.Path]::GetFullPath('D:/shspic/project_NO3_RetroLume-agent').TrimEnd('\')
$taskArchiveBase = [IO.Path]::GetFullPath((Join-Path $taskArchiveRoot 'DocuN/archives/legacy-roots-20261005'))
$taskArchiveEvidence = Join-Path $taskArchiveRoot 'DocuN/evidence/root-archive-20261005'
$taskArchiveNames = @('docu','evidence','Ndocu','spikes')
$taskArchiveEncoding = New-Object Text.UTF8Encoding($false)

function Write-ArchiveJson([string]$Path, $Value) {
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 12), $taskArchiveEncoding)
}

function Assert-ArchivePath([string]$Path, [string]$ExpectedParent) {
    $absolute = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    if (-not [IO.Path]::GetDirectoryName($absolute).Equals($ExpectedParent.TrimEnd('\'), [StringComparison]::OrdinalIgnoreCase)) {
        throw "路径不在指定直接父目录 $absolute"
    }
    $walk = $absolute
    while ($walk -and $walk.Length -ge $taskArchiveRoot.Length) {
        if (Test-Path -LiteralPath $walk) {
            $item = Get-Item -LiteralPath $walk -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "路径含链接 $walk" }
        }
        if ($walk.Equals($taskArchiveRoot, [StringComparison]::OrdinalIgnoreCase)) { break }
        $walk = [IO.Path]::GetDirectoryName($walk)
    }
    if (-not $walk -or -not $walk.Equals($taskArchiveRoot, [StringComparison]::OrdinalIgnoreCase)) { throw '路径越出项目' }
    return $absolute
}

function Get-ArchiveInventory([string]$Path) {
    $resolved = (Resolve-Path -LiteralPath $Path).ProviderPath.TrimEnd('\')
    $entries = @(Get-ChildItem -LiteralPath $resolved -Recurse -Force)
    if (@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw "目录内含链接 $resolved" }
    $files = @(foreach ($item in $entries | Where-Object { -not $_.PSIsContainer } | Sort-Object FullName) {
        [pscustomobject]@{
            relative_path = $item.FullName.Substring($resolved.Length + 1).Replace('\','/')
            bytes = [long]$item.Length
            sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    })
    $directories = @($entries | Where-Object { $_.PSIsContainer } | ForEach-Object { $_.FullName.Substring($resolved.Length + 1).Replace('\','/') } | Sort-Object)
    return [pscustomobject]@{files=$files; directories=$directories}
}

function Assert-ArchiveInventory($Expected, $Actual, [string]$Label) {
    if (@($Expected.files).Count -ne @($Actual.files).Count -or @($Expected.directories).Count -ne @($Actual.directories).Count) { throw "文件或目录数量不符 $Label" }
    $current = @{}
    foreach ($file in $Actual.files) { $current[$file.relative_path] = $file }
    foreach ($file in $Expected.files) {
        if (-not $current.ContainsKey($file.relative_path)) { throw "缺失归档文件 $Label/$($file.relative_path)" }
        $found = $current[$file.relative_path]
        if ($found.bytes -ne $file.bytes -or $found.sha256 -ne $file.sha256) { throw "归档字节不符 $Label/$($file.relative_path)" }
    }
    if ((@($Expected.directories) -join "`n") -ne (@($Actual.directories) -join "`n")) { throw "目录清单不符 $Label" }
}

$null = Assert-ArchivePath $taskArchiveBase (Join-Path $taskArchiveRoot 'DocuN/archives')
if ($Phase -eq 'Copy') {
    if (-not (Test-Path -LiteralPath $taskArchiveBase)) { $null = New-Item -ItemType Directory -Path $taskArchiveBase }
    $records = @()
    foreach ($name in $taskArchiveNames) {
        $source = Assert-ArchivePath (Join-Path $taskArchiveRoot $name) $taskArchiveRoot
        $target = Assert-ArchivePath (Join-Path $taskArchiveBase $name) $taskArchiveBase
        if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw "源目录不存在 $source" }
        if (Test-Path -LiteralPath $target) { throw "不覆盖既有归档 $target" }
        $inventory = Get-ArchiveInventory $source
        Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
        Assert-ArchiveInventory $inventory (Get-ArchiveInventory $target) $name
        Assert-ArchiveInventory $inventory (Get-ArchiveInventory $source) $name
        $records += [pscustomobject]@{name=$name; source=$source; destination=$target; files=$inventory.files; directories=$inventory.directories; copy_verified=$true}
    }
    $manifest = [pscustomobject]@{
        schema='retrolume.legacy-root-archive.v1'
        at=(Get-Date -Format o)
        authorization='用户2026-10-05同意完整归档、更新当前引用后移除docu/evidence/Ndocu/spikes四个根目录'
        project_root=$taskArchiveRoot
        archive_root=$taskArchiveBase
        records=$records
        history_bytes_preserved=$true
        roots_removed=$false
    }
    Write-ArchiveJson (Join-Path $taskArchiveBase 'manifest.json') $manifest
    Write-ArchiveJson (Join-Path $taskArchiveEvidence 'copy-verification.json') ([pscustomobject]@{at=(Get-Date -Format o); result='PASS'; manifest=(Join-Path $taskArchiveBase 'manifest.json'); copied=(@($records.files).Count); source_roots_retained=$true})
    $records | ForEach-Object { [pscustomobject]@{Directory=$_.name;Files=@($_.files).Count;CopyVerified=$_.copy_verified} } | ConvertTo-Json
    exit 0
}

$manifestPath = Join-Path $taskArchiveBase 'manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$readyPath = Join-Path $taskArchiveEvidence 'maintenance-ready.json'
if (-not (Test-Path -LiteralPath $readyPath)) { throw '当前引用维护与完整性检查尚未完成，不移除源目录' }
$ready = Get-Content -LiteralPath $readyPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($ready.result -ne 'PASS') { throw '维护检查不通过' }
foreach ($changed in $ready.changed_files) {
    if ((Get-FileHash -LiteralPath (Join-Path $taskArchiveRoot $changed.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $changed.sha256) { throw "维护后文件发生并行变化 $($changed.path)" }
}
if (@($manifest.records).Count -ne 4) { throw '归档清单不完整' }
foreach ($record in $manifest.records) {
    if ($record.name -notin $taskArchiveNames) { throw '清单含未授权目标' }
    $source = Assert-ArchivePath (Join-Path $taskArchiveRoot $record.name) $taskArchiveRoot
    $target = Assert-ArchivePath (Join-Path $taskArchiveBase $record.name) $taskArchiveBase
    if ($source -ne $record.source -or $target -ne $record.destination) { throw '清单绝对路径不符' }
    Assert-ArchiveInventory $record (Get-ArchiveInventory $source) $record.name
    Assert-ArchiveInventory $record (Get-ArchiveInventory $target) $record.name
}

# 用户已明确授权这四个具体根目录的移除；每次动作前再核绝对路径和归档。
$removed = @()
foreach ($record in $manifest.records) {
    $source = Assert-ArchivePath (Join-Path $taskArchiveRoot $record.name) $taskArchiveRoot
    $target = Assert-ArchivePath (Join-Path $taskArchiveBase $record.name) $taskArchiveBase
    Assert-ArchiveInventory $record (Get-ArchiveInventory $source) $record.name
    Assert-ArchiveInventory $record (Get-ArchiveInventory $target) $record.name
    Remove-Item -LiteralPath $source -Recurse -Force
    if (Test-Path -LiteralPath $source) { throw "源目录未移除 $source" }
    $removed += $source
}
foreach ($record in $manifest.records) { Assert-ArchiveInventory $record (Get-ArchiveInventory $record.destination) $record.name }
Write-ArchiveJson (Join-Path $taskArchiveEvidence 'removal-verification.json') ([pscustomobject]@{
    at=(Get-Date -Format o); result='PASS'; removed=$removed; removed_count=$removed.Count
    archive_verified_after_removal=$true; manifest_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
})
[pscustomobject]@{Phase='Remove';Result='PASS';Removed=$removed.Count;Archive=$taskArchiveBase} | ConvertTo-Json
