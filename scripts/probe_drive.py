#!/usr/bin/env python
"""Probe a public Google Drive folder for the iSys template files.

Drive folder pages are JS-driven, but the initial HTML payload embeds the folder
listing as an escaped JSON blob. We extract file ids + names heuristically and,
failing that, dump the raw HTML for a human/browser fallback.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

FOLDER = "1N6UsfqLkN8hILbBW3NPgOsfj5iH-JyMR"
URL = f"https://drive.google.com/drive/folders/{FOLDER}?usp=sharing"
OUT = os.path.join("data", "raw", "drive_folder.html")


def main() -> int:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"html bytes={len(html)}")

    # Unescape the layer Google embeds its listing in.
    unescaped = html.encode().decode("unicode_escape", errors="ignore")

    blob = None
    m = re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'(.*?)';", html, re.S)
    if m:
        blob = m.group(1).encode().decode("unicode_escape", errors="ignore")
        print("found _DRIVE_ivd blob")
    if blob is None:
        blob = unescaped

    # File entries look like ["<id>",["<parent>"],"<name>","mime/type",...]
    entries = re.findall(
        r'\["([A-Za-z0-9_-]{25,50})",\["[A-Za-z0-9_-]*"\],"([^"]{1,200})","([^"]{1,120})"', blob
    )
    if not entries:
        entries = re.findall(r'"([A-Za-z0-9_-]{28,44})"[^\]]{0,200}?"([^"]{1,200}\.(?:tex|zip|docx|pdf|cls|bst|sty|bib))"', blob, re.I)

    seen = set()
    print(f"entries={len(entries)}")
    for e in entries:
        if e[0] in seen:
            continue
        seen.add(e[0])
        print("  id=%s mime=%s name=%s" % (e[0], e[2] if len(e) > 2 else "?", e[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
