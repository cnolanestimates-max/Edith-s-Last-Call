# One helper for the three headless jobs.  Usage:
#   wc.ps1 import her,props,mats      -> import steps
#   wc.ps1 level                      -> rebuild the map
#   wc.ps1 game <tag> <extra args>    -> run the game windowed, log to Saved/Logs/<tag>.log (returns when it exits)
param([string]$What, [string]$A1 = "", [string]$A2 = "")
$proj = "C:\GameDev\Unreal\WellnessCheck\WellnessCheck.uproject"
$dat = Get-Content 'C:/ProgramData/Epic/UnrealEngineLauncher/LauncherInstalled.dat' -Raw | ConvertFrom-Json
$eng = ($dat.InstallationList | Where-Object { $_.AppName -eq 'UE_5.9' } | Select-Object -First 1).InstallLocation
$cmd = Join-Path $eng 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$ed = Join-Path $eng 'Engine/Binaries/Win64/UnrealEditor.exe'
$logs = "C:\GameDev\Unreal\WellnessCheck\Saved\Logs"
if ($What -eq 'import') {
    $env:WC_STEPS = $A1
    & $cmd $proj -run=pythonscript "-script=C:/GameDev/Unreal/WellnessCheck/Scripts/level/import_assets.py" -AllowCommandletRendering -unattended -nosplash "-abslog=$logs\import_$($A1 -replace ',','_').log" | Out-Null
    Select-String -Path "$logs\import_$($A1 -replace ',','_').log" -Pattern "WC_IMPORT|WC_BUILD|Error:|Traceback|RuntimeError|Exception" | Select-Object -Last 60 | ForEach-Object { $_.Line }
}
elseif ($What -eq 'level') {
    & $cmd $proj -run=pythonscript "-script=C:/GameDev/Unreal/WellnessCheck/Scripts/level/build_house.py" -AllowCommandletRendering -unattended -nosplash "-abslog=$logs\level.log" | Out-Null
    Select-String -Path "$logs\level.log" -Pattern "WC_BUILD|Traceback|RuntimeError|Exception|Error: " | Select-Object -Last 40 | ForEach-Object { $_.Line }
}
elseif ($What -eq 'game') {
    $extra = $A2 -split ' ' | Where-Object { $_ }
    $p = Start-Process -FilePath $ed -ArgumentList (@($proj, '/Game/WC/Maps/House', '-game', '-windowed', '-resx=1280', '-resy=720', '-unattended', '-nosplash', '-log', "-abslog=$logs\$A1.log") + $extra) -PassThru
    $p.WaitForExit()
    "exit " + $p.ExitCode
}
