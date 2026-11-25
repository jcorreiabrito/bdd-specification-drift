#!/usr/bin/env python
"""Extract text from a PDF with pypdf, preserving page boundaries.

Used to read open-access papers/slides that a scout has located. Output goes to
data/processed/pdf/<basename>.txt so quotes can be located and cited by page.

Usage:
    python scripts/pdf_extract.py <pdf-path-or-url> [...]
"""
from __future__ import annotations

import hashlib
import os
import sys
import urllib.request

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    print("pypdf not installed", file=sys.stderr)
    raise SystemExit(2)


def fetch(url: str) -> str:
    dest_dir = os.path.join("data", "raw", "pdf")
    os.makedirs(dest_dir, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = r.read()
    name = hashlib.sha256(url.encode()).hexdigest()[:16] + ".pdf"
    path = os.path.join(dest_dir, name)
    with open(path, "wb") as f:
        f.write(body)
    print(f"fetched {len(body)} bytes -> {path}")
    return path


def extract(path: str) -> str:
    reader = PdfReader(path)
    parts: list[str] = []
    for i, page in enumerate(reader.pages, 1):
        try:
            txt = page.extract_text() or ""
        except Exception as e:  # noqa: BLE001
            txt = f"[extract error: {e}]"
        parts.append(f"\n=== page {i} ===\n{txt}")
    return "".join(parts)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    outdir = os.path.join("data", "processed", "pdf")
    os.makedirs(outdir, exist_ok=True)
    for target in argv:
        path = fetch(target) if target.startswith("http") else target
        text = extract(path)
        base = os.path.splitext(os.path.basename(path))[0]
        dest = os.path.join(outdir, base + ".txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{len(text):>8} chars -> {dest}  ({text.count('=== page ')} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
