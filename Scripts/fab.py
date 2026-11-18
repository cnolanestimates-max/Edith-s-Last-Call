"""Search / install from the user's Fab library through the editor MCP.
python fab.py lib "<keywords>" [n]      -> compact rows
python fab.py details <listingId>
python fab.py install <listingId> <assetFormat> <engineVersion|-> <distributionMethod|-> "<title>" [fileId]
"""
import json, sys
from mcp import call


def tool(name, args, timeout=900):
    res = call("call_tool", {"toolset_name": "FabToolset.FabToolset", "tool_name": name, "arguments": args}, timeout)
    r = res.get("result", res)
    txt = "".join(c.get("text", "") for c in r.get("content", [])) if isinstance(r, dict) else str(r)
    try:
        out = json.loads(txt)
        if isinstance(out, dict) and isinstance(out.get("returnValue"), str):
            try:
                out = json.loads(out["returnValue"])
            except Exception:
                out = out["returnValue"]
        return out
    except Exception:
        return txt


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "lib":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        out = tool("SearchFabMyLibrary", {"Keywords": sys.argv[2], "Count": n})
        if isinstance(out, str):
            print(out[:3000]); sys.exit()
        for r in out.get("results", out if isinstance(out, list) else []):
            opts = ["%s/%s/%s" % (o.get("assetFormat"), o.get("engineVersion", "-"), o.get("distributionMethod", "-")) for o in r.get("installOptions", [])]
            print("%s | %s | %s | %s" % (r.get("listingId"), r.get("title"), r.get("seller"), ";".join(opts) or "X " + r.get("notInstallableReason", "")[:40]))
        if not isinstance(out, list) and not out.get("results"):
            print(json.dumps(out)[:2000])
    elif cmd == "details":
        print(json.dumps(tool("GetFabListingDetails", {"ListingId": sys.argv[2]}), indent=1)[:6000])
    elif cmd == "install":
        a = {"ListingId": sys.argv[2], "AssetFormat": sys.argv[3], "Title": sys.argv[6]}
        if sys.argv[4] != "-": a["EngineVersion"] = sys.argv[4]
        if sys.argv[5] != "-": a["DistributionMethod"] = sys.argv[5]
        if len(sys.argv) > 7: a["FileId"] = sys.argv[7]
        print(json.dumps(tool("InstallFabListing", a), indent=1)[:4000])
    elif cmd == "schema":
        res = call("describe_tools", {"tool_names": ["FabToolset.FabToolset." + sys.argv[2]]})
        print(json.dumps(res)[:5000])
