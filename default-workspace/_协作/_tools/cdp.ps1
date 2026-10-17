# cdp.ps1 -- Drive Microsoft Edge over CDP to read login-gated pages.
# ASCII-only on purpose: Windows PowerShell 5.1 reads .ps1 as ANSI/GBK
# unless a BOM is present, so non-ASCII source breaks parsing.
#
# Usage:
#   Start + navigate : .\cdp.ps1 -Url "https://example.com" -Headless
#   Reuse + evaluate : .\cdp.ps1 -Js "document.title"
#   Headed (for QR)  : .\cdp.ps1 -Url "https://www.xiaohongshu.com"
#   Close            : .\cdp.ps1 -Close
#
# Login state is persisted in -ProfileDir, so a QR scan survives
# across invocations and reboots.

param(
  [int]$Port = 9333,
  [string]$ProfileDir = "",
  [string]$Url = "",
  [string]$Js = "",
  [string]$JsFile = "",
  [string]$Shot = "",
  [int]$WaitMs = 5000,
  [switch]$Headless,
  [switch]$Close
)

$ErrorActionPreference = "Stop"
$Edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (-not $ProfileDir) {
  $ProfileDir = Join-Path $env:TEMP "edge_cdp_profile"
}

# -JsFile exists because passing JS inline fights PowerShell quoting:
# backslash is not an escape char in PowerShell, so any \" inside the JS
# terminates the string early. Keep non-trivial JS in files instead.
if ($JsFile) {
  $Js = Get-Content -Raw -Encoding UTF8 -LiteralPath $JsFile
}

function Test-Cdp {
  param([int]$P)
  try {
    Invoke-RestMethod "http://127.0.0.1:$P/json/version" -TimeoutSec 3 | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Start-Cdp {
  param([int]$P, [string]$Prof, [bool]$Hl)
  if (-not (Test-Path $Prof)) {
    New-Item -ItemType Directory -Path $Prof -Force | Out-Null
  }
  $a = @(
    "--remote-debugging-port=$P",
    "--user-data-dir=$Prof",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-blink-features=AutomationControlled"
  )
  if ($Hl) { $a += "--headless=new" }
  Start-Process $Edge -ArgumentList $a | Out-Null
  for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-Cdp $P) { return $true }
  }
  throw "Edge start timeout: CDP port $P not responding"
}

function New-Ws {
  param([string]$WsUrl)
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.ConnectAsync([Uri]$WsUrl, [System.Threading.CancellationToken]::None).Wait()
  return $ws
}

function Send-Ws {
  param($Ws, [hashtable]$Obj)
  $json = $Obj | ConvertTo-Json -Depth 12 -Compress
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
  $Ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [System.Threading.CancellationToken]::None).Wait()
}

function Recv-Ws {
  param($Ws, [int]$WantId)
  $buf = New-Object byte[] 262144
  for ($n = 0; $n -lt 600; $n++) {
    $sb = New-Object System.Text.StringBuilder
    do {
      $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
      $res = $Ws.ReceiveAsync($seg, [System.Threading.CancellationToken]::None).Result
      if ($res.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { return $null }
      [void]$sb.Append([System.Text.Encoding]::UTF8.GetString($buf, 0, $res.Count))
    } while (-not $res.EndOfMessage)
    $o = $sb.ToString() | ConvertFrom-Json
    if ($o.id -eq $WantId) { return $o }
  }
  return $null
}

# ---------------- main ----------------

if ($Close) {
  # Match on the leaf folder name only: Edge rewrites --user-data-dir to an
  # 8.3 short path (ADMINI~1), so a full-path Contains() never matches.
  $leaf = Split-Path $ProfileDir -Leaf
  $killed = 0
  Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($leaf) } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $killed++ }
  Write-Output "CDP_CLOSED leaf=$leaf killed=$killed"
  exit 0
}

if (-not (Test-Cdp $Port)) {
  [void](Start-Cdp -P $Port -Prof $ProfileDir -Hl ([bool]$Headless))
  Write-Output "EDGE_STARTED profile=$ProfileDir port=$Port"
} else {
  Write-Output "EDGE_REUSED port=$Port"
}

$list = Invoke-RestMethod "http://127.0.0.1:$Port/json/list" -TimeoutSec 10
$page = $list | Where-Object { $_.type -eq "page" } | Select-Object -First 1
if (-not $page) { throw "No page target found on port $Port" }

$ws = New-Ws $page.webSocketDebuggerUrl
$id = 1

try {
  if ($Url) {
    Send-Ws $ws @{ id = $id; method = "Page.enable" }
    [void](Recv-Ws $ws $id); $id++
    Send-Ws $ws @{ id = $id; method = "Page.navigate"; params = @{ url = $Url } }
    [void](Recv-Ws $ws $id); $id++
    Start-Sleep -Milliseconds $WaitMs
  }

  if ($Shot) {
    Send-Ws $ws @{ id = $id; method = "Emulation.setDeviceMetricsOverride"; params = @{ width = 750; height = 1334; deviceScaleFactor = 2; mobile = $true } }
    [void](Recv-Ws $ws $id); $id++
    Start-Sleep -Milliseconds 1000
    Send-Ws $ws @{ id = $id; method = "Page.captureScreenshot"; params = @{ format = "png"; captureBeyondViewport = $true; fromSurface = $true } }
    $r = Recv-Ws $ws $id
    if ($r -and $r.result -and $r.result.data) {
      [IO.File]::WriteAllBytes($Shot, [Convert]::FromBase64String($r.result.data))
      Write-Output "SHOT_SAVED $Shot"
    } else {
      Write-Output "SHOT_FAILED"
    }
  }

  if ($Js) {
    Send-Ws $ws @{ id = $id; method = "Runtime.evaluate"; params = @{
      expression    = $Js
      returnByValue = $true
      awaitPromise  = $true
    } }
    $r = Recv-Ws $ws $id
    if ($r -and $r.result -and $r.result.exceptionDetails) {
      Write-Output "JS_ERROR"
      Write-Output $r.result.exceptionDetails.text
      if ($r.result.exceptionDetails.exception) {
        Write-Output $r.result.exceptionDetails.exception.description
      }
    } elseif ($r -and $r.result -and $r.result.result) {
      Write-Output "JS_RESULT_BEGIN"
      Write-Output ($r.result.result.value | ConvertTo-Json -Depth 12)
      Write-Output "JS_RESULT_END"
    } else {
      Write-Output "JS_NO_RESULT"
    }
  }

  if (-not $Url -and -not $Js) {
    $list2 = Invoke-RestMethod "http://127.0.0.1:$Port/json/list" -TimeoutSec 10
    $page2 = $list2 | Where-Object { $_.type -eq "page" } | Select-Object -First 1
    Write-Output "CURRENT_URL"
    Write-Output $page2.url
    Write-Output "TITLE"
    Write-Output $page2.title
  }
} finally {
  try { $ws.Dispose() } catch { }
}
