"""Search the Fab library for many keywords, save thumbnails, print compact rows.
python fabq.py "kw1" "kw2" ...     -> Saved/fab/<listing>.jpg + rows
"""
import json, os, sys, urllib.request
from fab import tool

OUT = "C:/GameDev/Unreal/WellnessCheck/Saved/fab"
os.makedirs(OUT, exist_ok=True)
seen = {}
if os.path.exists(OUT + "/_seen.json"):
    seen = json.load(open(OUT + "/_seen.json"))
for q in sys.argv[1:]:
    out = tool("SearchFabMyLibrary", {"Keywords": q, "Count": 24})
    rows = out.get("results", []) if isinstance(out, dict) else []
    print("==", q, len(rows))
    for r in rows:
        lid = r.get("listingId")
        opts = ["%s%s" % (o.get("assetFormat"), ("/" + o.get("engineVersion")) if o.get("engineVersion") else "") for o in r.get("installOptions", [])]
        new = lid not in seen
        seen[lid] = {"title": r.get("title"), "opts": r.get("installOptions", []), "type": r.get("listingType")}
        if new and r.get("thumbnailUrl"):
            try:
                urllib.request.urlretrieve(r["thumbnailUrl"], "%s/%s.jpg" % (OUT, lid))
            except Exception:
                pass
        print("  %s | %s | %s | %s%s" % (lid[:8], r.get("title", "")[:70], r.get("listingType"), ",".join(opts) or "X", "" if new else " (seen)"))
json.dump(seen, open(OUT + "/_seen.json", "w"), indent=1)
