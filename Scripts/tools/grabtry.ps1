# Photograph the grab at several framings.   grabtry.ps1 "160,50" "185,45" "140,55"   (feet distance, stoop)
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Tries)
$root = "C:\GameDev\Unreal\WellnessCheck"
foreach ($t in $Tries) {
    $d, $s = $t -split ','
    $tag = "Grab_${d}_${s}"
    & "$root\Scripts\tools\wc.ps1" game $tag "-WCHerLook -WCGrabOnly -WCGrabDist=$d -WCGrabSink=$s -WCShots=$root/Saved/$tag" | Out-Null
    "$tag done"
}
"--- grabs done"
