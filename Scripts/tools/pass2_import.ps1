# Audio pass 2: import the approved sounds (SourceArt/AudioPass2/applied.json).  Refuses to run while Unreal is open.
param([string]$Only = "")
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { "UnrealEditor is running: not importing."; exit 1 }
$proj = "C:\GameDev\Unreal\WellnessCheck\WellnessCheck.uproject"
$dat = Get-Content 'C:/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat' -Raw | ConvertFrom-Json
$eng = ($dat.InstallationList | Where-Object { $_.AppName -eq 'UE_5.9' } | Select-Object -First 1).InstallLocation
$cmd = Join-Path $eng 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$log = "C:\GameDev\Unreal\WellnessCheck\Saved\Logs\pass2_import.log"
$env:WC_PASS2_ONLY = $Only
& $cmd $proj -run=pythonscript "-script=C:/GameDev/Unreal/WellnessCheck/Scripts/audio/pass2_import.py" -unattended -nosplash "-abslog=$log" | Out-Null
Select-String -Path $log -Pattern "WC_PASS2|Traceback|Error: " | Select-Object -Last 120 | ForEach-Object { $_.Line }
