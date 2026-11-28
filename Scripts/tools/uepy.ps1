# Run one Unreal Python script headless (no window).  uepy.ps1 <script path under the project> [-Tag name] [-Show regex]
# Refuses while UnrealEditor is running (Cheyenne may be playing; only one Unreal fits in memory).
param([string]$Script, [string]$Tag = "", [string]$Show = "WC_", [int]$Last = 60)
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { "UnrealEditor is running: not starting."; exit 1 }
$root = "C:\GameDev\Unreal\WellnessCheck"
if (-not $Tag) { $Tag = [IO.Path]::GetFileNameWithoutExtension($Script) }
$dat = Get-Content 'C:/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat' -Raw | ConvertFrom-Json
$eng = ($dat.InstallationList | Where-Object { $_.AppName -eq 'UE_5.9' } | Select-Object -First 1).InstallLocation
$cmd = Join-Path $eng 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$log = "$root\Saved\Logs\$Tag.log"
$full = (Join-Path $root $Script).Replace('\', '/')
& $cmd "$root\WellnessCheck.uproject" -run=pythonscript "-script=$full" -AllowCommandletRendering -unattended -nosplash "-abslog=$log" | Out-Null
Select-String -Path $log -Pattern "$Show|Traceback|Error: |RuntimeError" | Select-Object -Last $Last | ForEach-Object { $_.Line -replace '^\[[^\]]*\]\[[^\]]*\]', '' }
