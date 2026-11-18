# Rebuild chain: (optional Blender export of her) -> import steps -> level -> look test.   cycle.ps1 [-Her] [-Steps "her,audio"] [-Look Her5]
param([switch]$Her, [string]$Steps = "", [string]$Look = "", [switch]$NoLevel)
$root = "C:\GameDev\Unreal\WellnessCheck"
$wc = "$root\Scripts\tools\wc.ps1"
if ($Her) {
    $b = "C:\Users\cheye\AppData\Local\Programs\Blender Foundation\Blender 5.2\blender.exe"
    & $b -b --factory-startup -P "$root\Scripts\her\build_her.py" -- "C:/GameDev/Unreal/WellnessCheck/SourceArt/Her/her_meshy_raw.glb" "C:/GameDev/Unreal/WellnessCheck/SourceArt/Her/export" all 2>&1 | Select-String -Pattern "HER|Error|Traceback" | Select-Object -Last 14 | ForEach-Object { $_.Line }
    "--- her exported"
}
if ($Steps) { & $wc import $Steps; "--- import done" }
if (-not $NoLevel) {
    & $wc level
    $tb = Select-String -Path "$root\Saved\Logs\level.log" -Pattern "Traceback|IndentationError|SyntaxError|NameError|AttributeError" | Select-Object -First 5
    if ($tb) { "LEVEL BUILD FAILED"; $tb | ForEach-Object { $_.Line }; exit 1 }
    Select-String -Path "$root\Saved\Logs\level.log" -Pattern "RuthBed|memory:|forest:" | Select-Object -Last 6 | ForEach-Object { $_.Line }
    "--- level done"
}
if ($Look) { & $wc game $Look "-WCHerLook -WCShots=C:/GameDev/Unreal/WellnessCheck/Saved/$Look"; "--- look done" }
