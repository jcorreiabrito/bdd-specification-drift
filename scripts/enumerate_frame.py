#!/usr/bin/env python
"""Enumerate a reproducible sampling FRAME for the BDD corpus, token-free.

Why not the GitHub search API:
  * this host has no token; unauthenticated REST is 60 req/h, unusable;
  * code search is capped at ~1000 results and ranked by popularity, which the
    protocol forbids us from exploiting ("do not take top results").

What we do instead: enumerate GitHub *topic* pages across a fixed, declared set of
topics and language filters, page by page, and record every repository found.
Topic pages are public HTML, need no token, and are stable enough to enumerate
within a declared snapshot date. The frame is therefore "repositories that have
adopted at least one of the declared BDD-related topic tags, as observed on
<date>". That is a real limitation (topic-tagging bias) and is declared in the
method, not hidden.

The frame is NOT the sample. A random draw with a fixed seed happens afterwards
in draw_sample.py.

Outputs:
  data/frame/frame_raw.csv    one row per (repo, topic, language_filter, page)
  data/frame/frame_repos.csv  deduplicated repos with best-known star hint
  data/frame/FRAME.md         provenance: date, topics, filters, counts, hashes
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT_DIR = os.path.join("data", "frame")

TOPICS = [
    "cucumber", "bdd", "gherkin", "behave", "cucumber-jvm", "cucumber-js",
    "pytest-bdd", "specflow", "behavior-driven-development", "bdd-framework",
    "acceptance-testing", "living-documentation",
]
# '' means "all languages"; the rest are GitHub's ?l= slugs.
LANG_FILTERS = ["", "java", "javascript", "typescript", "python"]
MAX_PAGES = 6

NON_REPO_OWNERS = {
    "topics", "sponsors", "login", "signup", "features", "orgs", "collections",
    "events", "explore", "marketplace", "pricing", "about", "settings", "new",
    "codespaces", "mobile", "security", "enterprise", "site", "contact", "apps",
    "dashboard", "notifications", "issues", "pulls", "search", "join", "gist",
    "readme", "trending", "articles", "customer-stories", "solutions", "team",
}

REPO_RX = re.compile(r'href="/([A-Za-z0-9][\w.-]*)/([\w.-]+)"')


def get(url: str, timeout: int = 45) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
                return r.status, raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception:  # noqa: BLE001 - 10054 resets are routine here
            time.sleep(1.0 + attempt)
    return None, ""


def parse_topic_page(html: str) -> list[tuple[str, str]]:
    """Return [(owner/repo, star_hint)] found on a topic listing page."""
    found: list[tuple[str, str]] = []
    # Topic pages wrap each repo in <article class="border rounded color-shadow-small ...">
    for art in re.findall(r'<article\b.*?</article>', html, re.S):
        m = re.search(r'<h3[^>]*>(.*?)</h3>', art, re.S)
        block = m.group(1) if m else art
        slug = None
        for owner, repo in REPO_RX.findall(block):
            if owner.lower() in NON_REPO_OWNERS:
                continue
            slug = f"{owner}/{repo}"
            break
        if not slug:
            continue
        stars = ""
        sm = re.search(r'aria-label="([\d,]+) users starred', art)
        if not sm:
            sm = re.search(r'([\d.,]+k?)\s*</span>\s*</a>\s*<a[^>]*aria-label="[^"]*star', art)
        if sm:
            stars = sm.group(1).replace(",", "")
        if slug not in [s for s, _ in found]:
            found.append((slug, stars))
    return found


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict] = []
    raw_blob = hashlib.sha256()
    pages_fetched = 0

    for topic in TOPICS:
        for lang in LANG_FILTERS:
            for page in range(1, MAX_PAGES + 1):
                q = []
                if lang:
                    q.append(f"l={lang}")
                if page > 1:
                    q.append(f"page={page}")
                url = f"https://github.com/topics/{topic}" + ("?" + "&".join(q) if q else "")
                status, html = get(url)
                pages_fetched += 1
                if status != 200 or not html:
                    print(f"  [{status}] {url}")
                    break
                raw_blob.update(html.encode("utf-8", "replace"))
                found = parse_topic_page(html)
                new = 0
                for slug, stars in found:
                    rows.append({"repo": slug, "topic": topic, "lang_filter": lang or "any",
                                 "page": page, "stars_hint": stars, "snapshot_utc": stamp})
                    new += 1
                print(f"  ok pages={page} topic={topic:26s} lang={lang or 'any':11s} found={new}")
                if not found:
                    break
                time.sleep(0.5)

    raw_path = os.path.join(OUT_DIR, "frame_raw.csv")
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["repo", "topic", "lang_filter", "page", "stars_hint", "snapshot_utc"])
        w.writeheader()
        w.writerows(rows)

    # Deduplicate, keeping the largest observed star hint per repo.
    best: dict[str, str] = {}
    topics_of: dict[str, set[str]] = {}
    langs_of: dict[str, set[str]] = {}
    for r in rows:
        best.setdefault(r["repo"], "")
        if r["stars_hint"]:
            try:
                if not best[r["repo"]] or float(r["stars_hint"].rstrip("k")) > float(best[r["repo"]].rstrip("k") or 0):
                    best[r["repo"]] = r["stars_hint"]
            except ValueError:
                pass
        topics_of.setdefault(r["repo"], set()).add(r["topic"])
        langs_of.setdefault(r["repo"], set()).add(r["lang_filter"])

    dedup_path = os.path.join(OUT_DIR, "frame_repos.csv")
    with open(dedup_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "stars_hint", "topics", "lang_filters", "snapshot_utc"])
        for repo in sorted(best):
            w.writerow([repo, best[repo], ";".join(sorted(topics_of[repo])),
                        ";".join(sorted(langs_of[repo])), stamp])

    prov = os.path.join(OUT_DIR, "FRAME.md")
    with open(prov, "w", encoding="utf-8") as f:
        f.write("# Sampling frame provenance\n\n")
        f.write(f"- Snapshot UTC: `{stamp}`\n")
        f.write(f"- Topics enumerated ({len(TOPICS)}): {', '.join(TOPICS)}\n")
        f.write(f"- Language filters: {', '.join(l or 'any' for l in LANG_FILTERS)}\n")
        f.write(f"- Max pages per (topic, language): {MAX_PAGES}\n")
        f.write(f"- Topic pages fetched: {pages_fetched}\n")
        f.write(f"- Raw rows: {len(rows)}\n")
        f.write(f"- Unique repositories: {len(best)}\n")
        f.write(f"- SHA-256 of concatenated page HTML: `{raw_blob.hexdigest()}`\n")
        f.write("\n**Declared limitation.** The frame is defined as repositories that adopted at least\n"
                "one declared BDD-related GitHub topic tag, observable on the snapshot date. This\n"
                "introduces topic-tagging bias: a qualifying BDD repository that never tagged itself\n"
                "is out of frame. This is stated as a threat to external validity, not concealed.\n")
    print(f"\nframe: {len(rows)} raw rows -> {len(best)} unique repos")
    print(f"frame: wrote {raw_path}, {dedup_path}, {prov}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
