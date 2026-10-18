<#
TASK-059 只读进程身份查询辅助。

本文件只读：不启动、不停止、不修改任何进程，也不读写任何项目文件（只读进程元数据并输出JSON）。
由 tests/task059_proc_tree.mjs 调用；输出为stdout上的JSON（无匹配时无输出），退出码0/2。

模式：
  -Mode query       -Pids 123,456      查询指定PID；仅返回存在的进程，含创建时间/名称/命令行
  -Mode descendants -RootPid 123       递归返回该PID的全部后代（最多12层）
  -Mode find        -CmdMatch <子串>   返回命令行包含该子串的进程（大小写不敏感）
  -Mode portowner   -Port 8000         返回监听该端口的进程（Get-NetTCPConnection，回退netstat）
#>
param(
  [Parameter(Mandatory = $true)][string]$Mode,
  [int]$RootPid = 0,
  [string]$Pids = "",
  [string]$CmdMatch = "",
  [int]$Port = 0
)

$ErrorActionPreference = "Stop"
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }

function Get-ProcessRows {
  foreach ($p in Get-CimInstance Win32_Process) {
    $created = $null
    if ($p.CreationDate) { $created = $p.CreationDate.ToUniversalTime().ToString("o") }
    [pscustomobject]@{
      pid     = [int]$p.ProcessId
      ppid    = [int]$p.ParentProcessId
      created = $created
      name    = [string]$p.Name
      cmd     = [string]$p.CommandLine
    }
  }
}

function Write-Rows($rows) {
  $arr = @($rows)
  if ($arr.Count -gt 0) { $arr | ConvertTo-Json -Compress -Depth 4 }
}

switch ($Mode) {
  "query" {
    $ids = @()
    foreach ($part in $Pids.Split(",")) {
      $t = $part.Trim()
      if ($t -ne "") { $ids += [int]$t }
    }
    Write-Rows @(Get-ProcessRows | Where-Object { $ids -contains $_.pid })
  }
  "descendants" {
    if ($RootPid -le 0) { Write-Error "descendants needs -RootPid"; exit 2 }
    $all = @(Get-ProcessRows)
    $acc = @()
    $frontier = @($RootPid)
    for ($depth = 0; $depth -lt 12 -and $frontier.Count -gt 0; $depth++) {
      $next = @($all | Where-Object { $frontier -contains $_.ppid })
      if ($next.Count -eq 0) { break }
      $acc += $next
      $frontier = @($next | ForEach-Object { $_.pid })
    }
    Write-Rows @($acc)
  }
  "find" {
    if ($CmdMatch -eq "") { Write-Error "find needs -CmdMatch"; exit 2 }
    Write-Rows @(Get-ProcessRows | Where-Object {
        $_.cmd -and $_.cmd.IndexOf($CmdMatch, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
      })
  }
  "portowner" {
    if ($Port -le 0) { Write-Error "portowner needs -Port"; exit 2 }
    $owners = @()
    try {
      $conns = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop)
      $owners = @($conns | Select-Object -ExpandProperty OwningProcess -Unique)
    } catch {
      $owners = @()
      foreach ($line in @(netstat -ano | Select-String -Pattern "LISTENING")) {
        $text = $line.ToString().Trim()
        if ($text -match "[:.]$Port\s") {
          $parts = @($text -split "\s+")
          if ($parts.Count -ge 5) { $owners += [int]$parts[-1] }
        }
      }
      $owners = @($owners | Select-Object -Unique)
    }
    Write-Rows @(Get-ProcessRows | Where-Object { $owners -contains $_.pid })
  }
  default { Write-Error "unknown mode: $Mode"; exit 2 }
}
