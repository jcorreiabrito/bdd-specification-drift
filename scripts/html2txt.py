#!/usr/bin/env python
"""Crude but dependency-free HTML -> text extractor for venue-rule evidence.

Strips script/style/nav noise, collapses whitespace, keeps paragraph breaks so a
reviewer can locate an exact quoted sentence in the cached HTML.
"""
from __future__ import annotations

import glob
import os
import re
import sys
from html.parser import HTMLParser

SKIP = {"script", "style", "noscript", "svg", "head"}
BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
         "section", "article", "table", "ul", "ol", "dd", "dt", "blockquote"}


class Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self._skip_depth += 1
        elif tag in BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP and self._skip_depth:
            self._skip_depth -= 1
        elif tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = raw.replace("\xa0", " ")
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in raw.split("\n")]
        out: list[str] = []
        for ln in lines:
            if ln:
                out.append(ln)
            elif out and out[-1] != "":
                out.append("")
        return "\n".join(out)


def main(pattern: str) -> int:
    outdir = os.path.join("data", "processed", "venue")
    os.makedirs(outdir, exist_ok=True)
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        p = Extractor()
        p.feed(html)
        txt = p.text()
        base = os.path.basename(path).rsplit(".", 2)[0]
        dest = os.path.join(outdir, base + ".txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"{len(txt):>7} chars -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/*isys*.html"))
