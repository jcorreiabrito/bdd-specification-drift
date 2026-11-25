#!/usr/bin/env python
"""Probe which public GitHub surfaces can be enumerated WITHOUT an API token.

Context: this host has no GitHub token and the unauthenticated REST quota is
60 requests/hour, which is useless for a sampling frame. The study therefore needs
an enumeration source that is (a) reproducible, (b) token-free, and (c) not ranked
by popularity (the brief forbids "top search results").

Candidate surfaces probed here:
  1. github.com/topics/<topic>        - curated topic listings, paginated
  2. github.com/search?type=repositories (HTML) - usually needs JS / is bot-gated
  3. api.github.com (control)         - works but quota-limited
"""
from __future__ import annotations

import gzip
import io
import re
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def get(url: str, timeout: int = 40) -> tuple[int | None, str, bytes]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            return r.status, r.headers.get("Content-Type", ""), raw
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}", b""


def main() -> int:
    targets = [
        ("topics_cucumber", "https://github.com/topics/cucumber"),
        ("topics_cucumber_js", "https://github.com/topics/cucumber?l=javascript"),
        ("topics_bdd", "https://github.com/topics/bdd"),
        ("topics_gherkin", "https://github.com/topics/gherkin"),
        ("topics_behave", "https://github.com/topics/behave"),
        ("topics_cucumber_java", "https://github.com/topics/cucumber?l=java"),
        ("topics_p2", "https://github.com/topics/bdd?page=2"),
        ("search_html", "https://github.com/search?q=cucumber+feature+files&type=repositories"),
        ("api_control", "https://api.github.com/rate_limit"),
    ]
    for name, url in targets:
        status, ctype, raw = get(url)
        text = raw.decode("utf-8", "replace")
        # Topic pages link repositories as /owner/repo inside <h3>/<a> blocks.
        repos = re.findall(r'href="/([\w.-]+/[\w.-]+)"[^>]*data-view-component', text)
        if not repos:
            repos = re.findall(r'<h3[^>]*>\s*<a[^>]*href="/([\w.-]+/[\w.-]+)"', text)
        uniq = list(dict.fromkeys(repos))
        print(f"{name:20s} status={status!s:5s} bytes={len(raw):>8} ct={(ctype or '')[:40]:40s} repos={len(uniq)}")
        for r in uniq[:6]:
            print(f"      {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
