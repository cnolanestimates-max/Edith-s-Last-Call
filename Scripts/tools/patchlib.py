"""Whitespace-tolerant find-and-replace for source patches."""
import io
import re


def edit(path, pairs):
    """Replace each `old` (any run of whitespace matches any other run) by `new`; every one must be found.

    The match starts at old's first token, so the file's own indentation before it is kept.  `new` therefore has its
    leading whitespace removed (otherwise the first line ends up indented twice, which silently changes Python)."""
    s = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        pat = r"\s+".join(re.escape(tok) for tok in old.split())
        m = re.search(pat, s)
        assert m, (path, old[:100])
        s = s[:m.start()] + new.lstrip(" \t") + s[m.end():]
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    if path.endswith(".py"):
        compile(s, path, "exec")
