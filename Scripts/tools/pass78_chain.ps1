# Build, try the one voice line that was rate-limited once more (single attempt), then import audio and rebuild the level.
$root = "C:\GameDev\Unreal\WellnessCheck"
$ok = $true
try { & C:\GameDev\Unreal\Setup\unreal.ps1 -Action Build -Project "$root\WellnessCheck.uproject" 2>&1 | Out-Null } catch { $ok = $false }
if (-not $ok) {
    Select-String -Path "$env:LOCALAPPDATA\UnrealBuildTool\Log.txt" -Pattern "error C|error LNK|: error" | Select-Object -First 14 | ForEach-Object { $_.Line.Substring(0, [Math]::Min(320, $_.Line.Length)) }
    "BUILD FAILED"; "--- chain done"; exit 1
}
"BUILD OK"
if (-not (Test-Path "$root\SourceArt\Audio\VO_dry\m_whyleave.wav")) {
    python "$root\Scripts\audio\gen_vo.py" --only m_whyleave 2>&1 | Select-Object -Last 3
}
python "$root\Scripts\audio\demon_vo.py" m_whyleave 2>&1 | Select-Object -Last 1
& "$root\Scripts\tools\chain.ps1" -NoBuild -Steps "audio" -Level
