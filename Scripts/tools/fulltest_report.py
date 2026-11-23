"""Summarise a full bot playthrough log (wc.ps1 game <tag> "-WCAuto -WCAutoForce ..."): how far it got, the story beats
and scares in order, every stuck spot and failed check, engine errors and missing assets, and frame times.
python fulltest_report.py <log> [out.md]"""
import collections, re, sys

log = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else None
L = open(log, encoding="utf-8", errors="replace").read().splitlines()


def body(line):
    m = re.search(r"\]\[\s*\d+\](.*)", line)
    return (m.group(1) if m else line).strip()


sec = collections.OrderedDict((k, []) for k in ("end", "timeline", "scares", "stuck", "fail", "why", "errors", "missing", "warnings", "perf"))
noise = ("HttpListener", "ModelContextProtocol", "UnifiedErrorTest", "FError that has been", "Error with param", "Error with context",
         "OutlinerUnsaved", "LogEditorDataStorage")
warn_counts = collections.Counter()
for line in L:
    b = body(line)
    if any(n in b for n in noise):
        continue
    if "WCAUTO DONE" in b or "WCAUTO TIMEOUT" in b or "WCENDING" in b or "WCAUTO stop point" in b:
        sec["end"].append(b)
    elif re.search(r"WC(OBJECTIVE|CHECKPOINT|MEMORY) t", b):
        sec["timeline"].append(b)
    elif "WCSCARE t" in b:
        sec["scares"].append(b)
    elif "WCAUTO STUCK" in b:
        sec["stuck"].append(b)
    elif "WCAUTO FAIL" in b:
        sec["fail"].append(b)
    elif "WCAUTO WHY" in b:
        sec["why"].append(b)
    elif "WCPERF" in b:
        sec["perf"].append(b)
    elif "LoadErrors" in b or "Failed to load" in b or "Can't find file" in b or "was not available" in b:
        sec["missing"].append(b)
    elif re.search(r"\bError\b|Accessed None|Ensure condition failed|Assertion failed|Fatal", b):
        sec["errors"].append(b)
    elif ": Warning:" in b:
        cat = b.split(":")[0]
        warn_counts[cat] += 1
        if cat.startswith("LogWC") or "LogScript" in cat or "LogBlueprint" in cat:
            sec["warnings"].append(b)


def uniq(xs, n=60):
    seen, r = set(), []
    for x in xs:
        k = re.sub(r"[-\d.]+", "#", x)
        if k in seen:
            continue
        seen.add(k)
        r.append(x)
    return r[:n]


lines = [f"# Full playthrough report\n\nLog: `{log}`\n"]
titles = {"end": "How it ended", "timeline": "Objectives, checkpoints and memories (in order)", "scares": "Scares that fired",
          "stuck": "Where the bot got stuck", "fail": "Failed checks", "why": "Why the bot stalled", "errors": "Engine and game errors",
          "missing": "Missing assets", "warnings": "Game warnings", "perf": "Frame times"}
for k, v in sec.items():
    lines.append(f"\n## {titles[k]} ({len(v)})\n")
    for x in (v if k in ("timeline", "scares", "end") else uniq(v)):
        lines.append(f"- {x[:400]}")
lines.append("\n## Warning counts by category\n")
for c, n in warn_counts.most_common(25):
    lines.append(f"- {c}: {n}")
txt = "\n".join(lines)
if out:
    open(out, "w", encoding="utf-8").write(txt)
print(txt[:20000])
