"""Shot list: a camera in front of each named piece (kit furniture faces local +Y), for -WCShotFile.
python audit_front_shots.py <out.txt> label/folder_end[/dist] ..."""
import json, math, sys
A = "C:/GameDev/Unreal/WellnessCheck/Saved/_audit/"
rows = json.load(open(A + "props.json", encoding="utf-8"))
FLOORS = [-350.0, 0.0, 350.0, 700.0]
out = []
for spec in sys.argv[2:]:
    parts = spec.split("/")
    label, folder = parts[0], parts[1]
    dist0 = float(parts[2]) if len(parts) > 2 else 170.0
    front_axis = parts[3] if len(parts) > 3 else "+Y"
    for r in rows:
        if r["label"] != label or not r["folder"].endswith("/" + folder):
            continue
        mn, mx = r["world_min"], r["world_max"]
        cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
        yaw = math.radians(r["yaw"])
        lx, ly = {"+Y": (0, 1), "-Y": (0, -1), "+X": (1, 0), "-X": (-1, 0)}[front_axis]
        fx, fy = lx * math.cos(yaw) - ly * math.sin(yaw), lx * math.sin(yaw) + ly * math.cos(yaw)
        half = abs(fx) * (mx[0] - mn[0]) / 2 + abs(fy) * (mx[1] - mn[1]) / 2
        d = half + dist0
        camx, camy = cx + fx * d, cy + fy * d
        floor = min(FLOORS, key=lambda f: abs(mn[2] - f))
        tz = mn[2] + (mx[2] - mn[2]) * 0.55
        pitch = max(-40.0, min(10.0, math.degrees(math.atan2(tz - (floor + 156), d))))
        yawc = math.degrees(math.atan2(cy - camy, cx - camx))
        out.append(f"{label}_{folder}|{camx:.0f},{camy:.0f},{floor + 92:.0f},{yawc:.1f},{pitch:.1f}")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(out), "shots")
