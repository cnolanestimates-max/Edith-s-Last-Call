# Apply polish steps to the saved House map (no level rebuild).  polish.ps1 [-Steps "polish_pass,polish_yard"]
param([string]$Steps = "polish_pass")
$dat = Get-Content 'C:/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat' -Raw | ConvertFrom-Json
$eng = ($dat.InstallationList | Where-Object { $_.AppName -eq 'UE_5.9' } | Select-Object -First 1).InstallLocation
$cmd = Join-Path $eng 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$env:WC_POLISH_STEPS = $Steps
& $cmd "C:\GameDev\Unreal\WellnessCheck\WellnessCheck.uproject" -run=pythonscript "-script=C:/GameDev/Unreal/WellnessCheck/Scripts/level/apply_polish.py" -AllowCommandletRendering -unattended -nosplash "-abslog=C:\GameDev\Unreal\WellnessCheck\Saved\Logs\polish.log" | Out-Null
Select-String -Path "C:\GameDev\Unreal\WellnessCheck\Saved\Logs\polish.log" -Pattern "WC_POLISH|Traceback|Error:|RuntimeError" | Select-Object -Last 20 | ForEach-Object { $_.Line.Substring([Math]::Min(30, $_.Line.Length)) }
