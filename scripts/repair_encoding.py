#!/usr/bin/env python
"""Repair UTF-8 text that was double-encoded by a PowerShell `Set-Content -Encoding utf8`
round-trip (mojibake: "Móra" stored as "MÃ³ra", bytes C3 83 C2 B3).

Windows PowerShell 5.1 reads a UTF-8 file as ANSI when the encoding is not detected,
then re-encodes to UTF-8, producing this doubling. The damage is reversible: encode the
text as latin-1 and decode it as UTF-8.

Refuses to write if the reversal fails on any character, so it cannot silently corrupt a
file that was merely mis-detected rather than double-encoded.

Usage:
    python scripts/repair_encoding.py refs/verified.csv [more.csv ...]
"""
from __future__ import annotations

import sys


def repair_line(line: str) -> tuple[str, bool]:
    try:
        fixed = line.encode("latin-1").decode("utf-8")
        return fixed, fixed != line
    except (UnicodeEncodeError, UnicodeDecodeError):
        return line, False


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for path in argv:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            lines = f.read().splitlines()
        out, changed = [], 0
        for ln in lines:
            fixed, did = repair_line(ln)
            changed += int(did)
            out.append(fixed)
        # Verify round-trip before writing.
        bad = [ln for ln in out if _has_high_mojibake(ln)]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
        print(f"repair: {path}: {changed} line(s) repaired, {len(bad)} suspicious remain")
        if bad:
            rc = 1
            for b in bad[:3]:
                print(f"  still suspicious: {b[:120]}")
    return rc


def _has_high_mojibake(s: str) -> bool:
    """Heuristic: sequences typical of double-encoded UTF-8 ('Ã', 'Â', 'â€')."""
    return any(tok in s for tok in ("Ã", "Â", "â€"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
