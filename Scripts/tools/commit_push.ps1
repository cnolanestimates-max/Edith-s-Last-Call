# Build; if it builds, commit everything and push to the private repo.
param([string]$Message = "Checkpoint")
$root = "C:\GameDev\Unreal\WellnessCheck"
& "$root\Scripts\tools\chain.ps1" | Select-String -Pattern "BUILD|error" | ForEach-Object { $_.Line.Substring(0, [Math]::Min(220, $_.Line.Length)) }
if ($LASTEXITCODE -eq 1) { "not committed: build failed"; exit 1 }
Set-Location $root
git add -A 2>&1 | Select-Object -Last 2
$msgFile = "$root\Saved\_commit_msg.txt"
git commit -q -F $msgFile 2>&1 | Select-Object -Last 3
git log --oneline -1
$ok = $false
foreach ($wait in 0, 2, 4, 8, 16) {
    if ($wait) { Start-Sleep -Seconds $wait }
    git push -u origin main 2>&1 | Select-Object -Last 3
    if ($LASTEXITCODE -eq 0) { $ok = $true; break }
}
if ($ok) { "PUSHED" } else { "PUSH FAILED" }
