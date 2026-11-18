"""Install a list of Fab library items (by listing-id prefix) at the 2K tier.  python fab_install.py <prefix> <prefix> ...
Records what was installed in Saved/fab/_installed.json (title, listing id, file) for the asset manifest."""
import json, os, sys, time
from fab import tool

OUT = "C:/GameDev/Unreal/WellnessCheck/Saved/fab"
seen = json.load(open(OUT + "/_seen.json"))
done = json.load(open(OUT + "/_installed.json")) if os.path.exists(OUT + "/_installed.json") else {}
for short in sys.argv[1:]:
    lid = next((k for k in seen if k.startswith(short)), None)
    if not lid:
        print(short, "unknown"); continue
    if lid in done:
        print(short, "already installed:", done[lid]["title"]); continue
    info = seen[lid]
    opts = info.get("opts") or []
    if not opts:
        print(short, "not installable"); continue
    pref = {"gltf": 0, "glb": 1, "fbx": 2, "unreal-engine": 3, "converted-files": 4}
    o = sorted(opts, key=lambda x: pref.get(x.get("assetFormat"), 9))[0]
    args = {"ListingId": lid, "AssetFormat": o["assetFormat"], "Title": info["title"]}
    if o.get("engineVersion"):
        args["EngineVersion"] = o["engineVersion"]
    if o.get("distributionMethod"):
        args["DistributionMethod"] = o["distributionMethod"]
    r = tool("InstallFabListing", args)
    chosen = ""
    if isinstance(r, dict) and r.get("status") == "choose-file":
        files = r.get("files", [])
        pick = next((f for f in files if "2k" in f["fileName"].lower()), None) or next((f for f in files if "mid" in f["fileName"].lower()), None) or (files[0] if files else None)
        if not pick:
            print(short, "no files"); continue
        chosen = pick["fileName"]
        args["FileId"] = pick["fileId"]
        r = tool("InstallFabListing", args)
    status = r.get("status") if isinstance(r, dict) else str(r)[:80]
    print(short, info["title"][:50], "->", status, chosen)
    if status in ("handed-to-editor", "installed", "already-installed"):
        done[lid] = {"title": info["title"], "format": o["assetFormat"], "file": chosen, "type": info.get("type")}
        json.dump(done, open(OUT + "/_installed.json", "w"), indent=1)
    time.sleep(1.0)
