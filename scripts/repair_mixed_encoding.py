#!/usr/bin/env python
"""Repair a file with MIXED UTF-8 and CP1252 bytes (results/RUNLOG.md).

Cause: this file was appended to both by the harness (UTF-8) and by an earlier
PowerShell `Add-Content` (CP1252), producing a file that is neither. Byte 0x97 (an
em dash in CP1252) makes the whole file invalid UTF-8.

The repair is lossless: decode as UTF-8 with `surrogateescape`, which turns each
invalid byte into a lone surrogate, then re-decode only those surrogates as CP1252.
Valid UTF-8 multi-byte sequences are left untouched.

Usage:
    python scripts/repair_mixed_encoding.py results/RUNLOG.md
"""
from __future__ import annotations

import sys


def repair(path: str) -> int:
    raw = open(path, "rb").read()
    text = raw.decode("utf-8", "surrogateescape")
    out: list[str] = []
    fixed = 0
    for ch in text:
        code = ord(ch)
        if 0xDC80 <= code <= 0xDCFF:
            b = code - 0xDC00
            out.append(bytes([b]).decode("cp1252", "replace"))
            fixed += 1
        else:
            out.append(ch)
    open(path, "w", encoding="utf-8", newline="\n").write("".join(out))
    print(f"repair_mixed_encoding: {path}: {fixed} CP1252 byte(s) converted; now valid UTF-8")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(repair(sys.argv[1]))
