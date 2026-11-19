# Build the game code, then (only if it built) run the given jobs in order.
#   chain.ps1 -Steps "items" -Level -Inv Inv2 -Look Her7 -Run auto8 -Drive Drive2 -Items Items2
param([string]$Steps = "", [switch]$Level, [string]$Inv = "", [string]$Look = "", [string]$Run = "", [string]$Drive = "", [string]$Items = "", [switch]$NoBuild, [switch]$Real)
$root = "C:\GameDev\Unreal\WellnessCheck"
$wc = "$root\Scripts\tools\wc.ps1"
if (-not $NoBuild) {
    $ok = $true
    try { & C:\GameDev\Unreal\Setup\unreal.ps1 -Action Build -Project "$root\WellnessCheck.uproject" 2>&1 | Out-Null } catch { $ok = $false }
    if (-not $ok) {
        Select-String -Path "$env:LOCALAPPDATA\UnrealBuildTool\Log.txt" -Pattern "error C|error LNK|: error" | Select-Object -First 14 | ForEach-Object { $_.Line.Substring(0, [Math]::Min(320, $_.Line.Length)) }
        "BUILD FAILED"; "--- chain done"; exit 1
    }
    "BUILD OK"
}
if ($Steps) { & $wc import $Steps | Select-Object -Last 14; "--- import done" }
if ($Level) {
    & $wc level | Out-Null
    $tb = Select-String -Path "$root\Saved\Logs\level.log" -Pattern "Traceback|IndentationError|SyntaxError|NameError|AttributeError" | Select-Object -First 5
    if ($tb) { "LEVEL BUILD FAILED"; $tb | ForEach-Object { $_.Line }; "--- chain done"; exit 1 }
    Select-String -Path "$root\Saved\Logs\level.log" -Pattern "WC_BUILD: DONE" | Select-Object -Last 1 | ForEach-Object { $_.Line }
    "--- level done"
}
if ($Inv) { & $wc game $Inv "-WCHerLook -WCInvTest=$root/Saved/$Inv"; "--- inv done" }
if ($Look) { & $wc game $Look "-WCHerLook -WCShots=$root/Saved/$Look"; "--- look done" }
if ($Items) { & $wc game $Items "-WCItems -WCShots=$root/Saved/$Items"; "--- items done" }
if ($Drive) { & $wc game $Drive "-WCAuto -WCFast -WCAutoForce -WCDrive -WCDriveOnly -WCShots=$root/Saved/$Drive"; "--- drive done" }
if ($Run) {
    $flags = if ($Real) { "-WCAuto -WCAutoForce -WCNoDrive" } else { "-WCAuto -WCFast -WCAutoForce -WCNoDrive" }
    & $wc game $Run "$flags -WCShots=$root/Saved/$Run"; "--- run done"
}
"--- chain done"
