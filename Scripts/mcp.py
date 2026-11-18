"""Tiny client for the Unreal editor's MCP endpoint (http://127.0.0.1:8000/mcp).
Usage:  python mcp.py list [filter]
        python mcp.py call <tool> '<json args>'   (or @file.json)
"""
import json, sys, urllib.request

URL = "http://127.0.0.1:8000/mcp"
HDR = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def post(body, sid=None, timeout=600):
    h = dict(HDR)
    if sid:
        h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        sid = r.headers.get("Mcp-Session-Id") or sid
    if raw.lstrip().startswith("{"):
        return json.loads(raw), sid
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"):
            try:
                out = json.loads(line[5:].strip())
            except Exception:
                pass
    return out, sid


def session():
    _, sid = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "wc", "version": "1"}}})
    try:
        post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid, 10)
    except Exception:
        pass
    return sid


def call(tool, args, timeout=600):
    sid = session()
    res, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}}, sid, timeout)
    return res


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "list":
        sid = session()
        res, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, sid)
        flt = sys.argv[2].lower() if len(sys.argv) > 2 else ""
        for t in res["result"]["tools"]:
            if flt in t["name"].lower() or flt in (t.get("description") or "").lower():
                print(t["name"], "-", (t.get("description") or "")[:160].replace("\n", " "))
                if len(sys.argv) > 3:
                    print(json.dumps(t.get("inputSchema"), indent=1))
    else:
        a = sys.argv[3] if len(sys.argv) > 3 else "{}"
        if a.startswith("@"):
            a = open(a[1:], encoding="utf-8").read()
        res = call(sys.argv[2], json.loads(a))
        r = res.get("result", res)
        if isinstance(r, dict) and "content" in r:
            for c in r["content"]:
                print(c.get("text", c))
        else:
            print(json.dumps(res, indent=1))


def tool(toolset, name, args, timeout=600):
    """Call a toolset tool; returns (text, images[bytes])."""
    import base64
    res = call("call_tool", {"toolset_name": toolset, "tool_name": name, "arguments": args}, timeout)
    r = res.get("result", res)
    txt, imgs = "", []
    for c in (r.get("content", []) if isinstance(r, dict) else []):
        if c.get("type") == "image":
            imgs.append(base64.b64decode(c["data"]))
        else:
            txt += c.get("text", "")
    return txt, imgs


def py(script, timeout=900):
    t, _ = tool("editor_toolset.toolsets.python_scripting.PythonScriptingTools", "execute_python", {"script": {"content": script, "language": "Python"}}, timeout)
    return t


def pyv(script, timeout=900):
    """Run Python in the editor and return its final expression (parsed JSON when possible)."""
    t = py(script, timeout)
    try:
        d = json.loads(t)
        v = d.get("returnValue", d) if isinstance(d, dict) else d
        try:
            return json.loads(v) if isinstance(v, str) else v
        except Exception:
            return v
    except Exception:
        return t
