#!/usr/bin/env python
"""Flatten tarball-extracted repository directories.

`tarfile.extractall` preserves the archive's single top-level directory
(`<repo>-HEAD/`), so every cloned project ends up one level too deep. That breaks
path-based domain detection (`src/main/java/...`), licence/build discovery and any
`git`-relative operation. This script moves the contents of that wrapper directory
up one level, in place, and is idempotent.

Usage:
    python scripts/flatten_repos.py
"""
from __future__ import annotations

import os
import shutil
import sys

REPO_DIR = os.path.join("data", "repos")


def flatten(path: str) -> bool:
    entries = [e for e in os.listdir(path) if e not in (".git",)]
    dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
    files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
    # Wrapper layout: exactly one directory and no project files beside it.
    if len(dirs) != 1:
        return False
    candidate = os.path.join(path, dirs[0])
    # Only flatten if the wrapper itself looks like the archive root.
    if not dirs[0].endswith(("-HEAD", "-main", "-master")) and files:
        return False
    moved = 0
    for item in os.listdir(candidate):
        src = os.path.join(candidate, item)
        dst = os.path.join(path, item)
        if os.path.exists(dst):
            continue
        shutil.move(src, dst)
        moved += 1
    try:
        os.rmdir(candidate)
    except OSError:
        pass
    return moved > 0


def main() -> int:
    if not os.path.isdir(REPO_DIR):
        print(f"no {REPO_DIR}")
        return 1
    flattened = 0
    for name in sorted(os.listdir(REPO_DIR)):
        d = os.path.join(REPO_DIR, name)
        if not os.path.isdir(d):
            continue
        try:
            if flatten(d):
                flattened += 1
                print(f"  flattened {name}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAILED {name}: {e}")
    print(f"flatten: {flattened} directories flattened")
    return 0


if __name__ == "__main__":
    sys.exit(main())
