#!/usr/bin/env python
"""Provenance-preserving HTTP fetcher for the bdd-specification-drift project.

Every retrieved resource is cached under data/raw/ and indexed in
data/raw/INDEX.jsonl with: url, UTC timestamp, HTTP status, sha256, byte size,
content type and saved path.

Rationale: the integrity contract requires that every quantitative claim trace to
a recorded command. Network resources (venue rules, API responses, literature
landing pages) are evidence too, so they get the same treatment.

Host quirk (measured 2026-11-25): curl.exe and PowerShell Invoke-WebRequest are
blocked on this machine; Python urllib works. Hence this script.

Usage:
    python scripts/fetch.py <url> [<url> ...] [--tag TAG] [--binary] [--timeout 40]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
INDEX = os.path.join(RAW_DIR, "INDEX.jsonl")
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 bdd-spec-drift-research/1.0"
)


def slugify(url: str) -> str:
    s = re.sub(r"^[a-z]+://", "", url)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:120].strip("_")


def fetch(url: str, tag: str | None, binary: bool, timeout: int) -> dict:
    os.makedirs(RAW_DIR, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rec = {"url": url, "retrieved_utc": started, "tag": tag}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            rec["status"] = r.status
            rec["content_type"] = r.headers.get("Content-Type", "")
            rec["final_url"] = r.geturl()
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        rec["status"] = e.code
        rec["content_type"] = e.headers.get("Content-Type", "") if e.headers else ""
        rec["final_url"] = url
        rec["error"] = f"HTTPError {e.code}"
    except Exception as e:  # noqa: BLE001 - network layer is unreliable here
        rec["status"] = None
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["sha256"] = None
        rec["bytes"] = 0
        rec["saved_to"] = None
        _append_index(rec)
        return rec

    digest = hashlib.sha256(body).hexdigest()
    ext = ".bin" if binary else ".html"
    ct = (rec.get("content_type") or "").lower()
    if "pdf" in ct or url.lower().endswith(".pdf"):
        ext = ".pdf"
    elif "json" in ct:
        ext = ".json"
    elif "xml" in ct:
        ext = ".xml"
    name = f"{slugify(url)}.{digest[:12]}{ext}"
    path = os.path.join(RAW_DIR, name)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(body)
    rec.update(sha256=digest, bytes=len(body), saved_to=os.path.relpath(path, os.path.join(RAW_DIR, "..", "..")))
    _append_index(rec)
    return rec


def _append_index(rec: dict) -> None:
    with open(INDEX, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--binary", action="store_true")
    ap.add_argument("--timeout", type=int, default=40)
    a = ap.parse_args()
    rc = 0
    for u in a.urls:
        rec = fetch(u, a.tag, a.binary, a.timeout)
        ok = rec.get("status") and 200 <= rec["status"] < 300
        print(f"[{'OK ' if ok else 'ERR'}] {rec.get('status')} {rec.get('bytes', 0):>8}B "
              f"{rec.get('saved_to') or rec.get('error')} <- {u}")
        if not ok:
            rc = 1
        time.sleep(0.4)
    return rc


if __name__ == "__main__":
    sys.exit(main())
