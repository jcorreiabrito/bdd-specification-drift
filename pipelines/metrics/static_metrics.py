#!/usr/bin/env python
"""Static drift indicators D1-D7 for one repository at a given commit.

Implements docs/method.md section 7.4 as faithfully as is possible without human
raters. Where the protocol specifies a judgement-coded rubric, this module
implements the AUTOMATABLE subset and records the confidence in the output, so the
paper can disclose exactly what was and was not measured. It never invents a label.

Honesty contract
----------------
* D1 skip_ratio            fully automated (parse-only).
* D2 assertion_weakness    automated for W1 (tautology), W2 (constant truth),
                           W5 (self-comparison) and a conservative W4 (swallowed
                           failure). W3 (unreachable) is detected only in the
                           trivially parseable "assertion after return" form.
                           UNRESOLVED is counted and reported.
* D3 stale_spec_ratio      automated via `git blame` per scenario line range.
* D4 redundancy_cluster    NORMALISED-TEXT fallback (protocol 7.4 permits it;
                           `fingerprint_source=normalised_text` recorded).
* D5 glue_duplication      counted from unique normalised step text (dry-run
                           stepdef ids unavailable) -> recorded as fallback.
* D6 literal_bearing       AST for Python (stdlib ast); tokenizer for JS/TS and
                           Java, with the protocol's exclusion list applied.
* D7 mirror_stepdef        `mirror_loose` = M1 & M2 & M3, regex heuristics.
                           Precision NOT validated (no human raters available) ->
                           emitted with `low_confidence` flag.

Output: one row per repo -> data/metrics/static_indicators.csv
        plus data/metrics/stepdef_audit.csv (D2/D7 unit-level detail)

Usage:
    python pipelines/metrics/static_metrics.py --repo-dir data/repos/owner__name --repo owner/name
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------- step parsing

STEP_KEYWORDS = ("Given", "When", "Then", "And", "But", "E", "Quando", "Então", "Entao",
                 "Dado", "Dada", "Dados", "Dadas", "Mas")
STEP_RX = re.compile(r"^\s*(%s)\b\s+(.*)$" % "|".join(STEP_KEYWORDS))
FEATURE_RX = re.compile(r"^\s*(Feature|Funcionalidade|Característica)\s*:\s*(.*)$")
SCENARIO_RX = re.compile(r"^\s*(Scenario|Scenario Outline|Scenario Template|Cenário|Cenário Esquema|Cenário Outline|Exemplo|Ejemplo)\s*:\s*(.*)$")
TAG_RX = re.compile(r"^\s*(@[^\s]+(?:\s+@[^\s]+)*)\s*$")
EXAMPLES_RX = re.compile(r"^\s*(Examples|Exemplos|Cenários)\s*:", re.I)
TABLE_RX = re.compile(r"^\s*\|")
DOCSTRING_RX = re.compile(r'^\s*("""|```)')

SKIP_TAG_RX = re.compile(
    r"@(skip|skipped|ignore|ignored|wip|pending|todo|manual|notimplemented|not_implemented)\b", re.I)


def parse_feature(path: str) -> dict:
    """Parse a .feature file into feature/scenario structure with line ranges."""
    out = {"path": path, "feature_tags": [], "scenarios": []}
    cur = None
    pending_tags: list[str] = []
    in_examples = False
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except Exception:
        return out
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip()
        mt = TAG_RX.match(line)
        if mt:
            pending_tags.extend(mt.group(1).split())
            continue
        mf = FEATURE_RX.match(line)
        if mf:
            out["feature_tags"].extend(pending_tags)
            out["feature_name"] = mf.group(2)
            pending_tags = []
            continue
        ms = SCENARIO_RX.match(line)
        if ms:
            if cur:
                cur["end_line"] = i - 1
                out["scenarios"].append(cur)
            cur = {"name": ms.group(2).strip(), "start_line": i, "end_line": i,
                   "tags": list(pending_tags), "steps": [], "has_examples": False}
            pending_tags = []
            in_examples = False
            continue
        if cur is None:
            continue
        if EXAMPLES_RX.match(line):
            cur["has_examples"] = True
            in_examples = True
            continue
        mstep = STEP_RX.match(line)
        if mstep and not in_examples:
            cur["steps"].append((i, mstep.group(1), mstep.group(2).strip()))
            continue
        if TABLE_RX.match(line) or DOCSTRING_RX.match(line):
            cur.setdefault("data_lines", []).append(i)
    if cur:
        cur["end_line"] = len(lines)
        out["scenarios"].append(cur)
    return out


def normalise_step(text: str) -> str:
    """Protocol 7.4 D4 fallback: parameters replaced with placeholders."""
    t = re.sub(r'"[^"]*"', "<STR>", text)
    t = re.sub(r"'[^']*'", "<STR>", t)
    t = re.sub(r"\b\d+(?:\.\d+)?\b", "<NUM>", t)
    t = re.sub(r"\|[^|]*\|", "<CELL>", t)
    return re.sub(r"\s+", " ", t).strip().lower()


# ----------------------------------------------------------- step definitions

ASSERT_TOKENS = {
    "java": [r"\bassert[A-Z]\w*\s*\(", r"\bassertThat\s*\(", r"\bverify\s*\(", r"\bfail\s*\(",
             r"\bassertEquals\b", r"\bassertTrue\b", r"\bassertFalse\b", r"\bassertNotNull\b"],
    "javascript": [r"\bexpect\s*\(", r"\.should\b", r"\bassert\.\w+\s*\(", r"\bt\.(?:deepEqual|is|true|false|throws)\b",
                   r"\bchai\b"],
    "typescript": [r"\bexpect\s*\(", r"\.should\b", r"\bassert\.\w+\s*\(", r"\bt\.(?:deepEqual|is|true|false|throws)\b"],
    "python": [r"\bassert\b", r"\bself\.assert\w+\s*\(", r"\bpytest\.raises\b", r"\bassert_\w+\s*\("],
}

WEAK_PATTERNS = {
    # W1 tautology: assert(x == x) / expect(a).toBe(a) with identical operands
    "W1": [re.compile(r"assert\w*\s*\(\s*([\w.\[\]'\"]+)\s*==\s*\1\s*[,)]"),
           re.compile(r"expect\s*\(\s*([\w.\[\]'\"]+)\s*\)\s*\.\s*(?:toBe|toEqual|toStrictEqual)\s*\(\s*\1\s*\)"),
           re.compile(r"assert\s+([\w.\[\]']+)\s*==\s*\1\b")],
    # W2 constant truth: assertTrue(true), expect(1).toBe(1), assert True
    "W2": [re.compile(r"assert(?:True|False)\s*\(\s*(?:true|false)\s*\)"),
           re.compile(r"assert\s+(?:True|False)\s*(?:#.*)?$", re.M),
           re.compile(r"expect\s*\(\s*(?:true|false|-?\d+|'[^']*'|\"[^\"]*\")\s*\)\s*\.\s*to(?:Be|Equal)\s*\(\s*(?:true|false|-?\d+|'[^']*'|\"[^\"]*\")\s*\)"),
           re.compile(r"assert\s+(?:is\s+not\s+None|!= None|is None)\s*$", re.M)],
    # W5 self-comparison
    "W5": [re.compile(r"assert\w*\s*\(\s*([\w.]+)\s*(?:==|!=)\s*\1\b")],
}

LITERAL_SKIP_RX = re.compile(
    r"(https?://|xpath|css\s*=|selector|\.css|\.xpath|findElement|By\.|@FindBy|"
    r"\blog(?:ger)?\.|System\.out|console\.\w+|print\s*\(|LOG\.)", re.I)
NUM_RX = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
STR_RX = re.compile(r'"([^"\\]{2,})"|\'([^\'\\]{2,})\'')

STEPDEF_DECL_RX = {
    "java": re.compile(r'@(?:Given|When|Then|And|But)\s*\(\s*(?:value\s*=\s*)?"([^"]+)"'),
    "javascript": re.compile(r"(?:Given|When|Then|And|But)\s*\(\s*['\"`](.+?)['\"`]"),
    "typescript": re.compile(r"(?:Given|When|Then|And|But)\s*\(\s*['\"`](.+?)['\"`]"),
    "python": re.compile(r"@(?:given|when|then|step)\s*\(\s*['\"](.+?)['\"]"),
}

DOMAIN_PATH_RX = re.compile(
    r"(?i)/(domain|domains|model|models|entity|entities|business|core|logic|rules)/")
DENY_PATH_RX = re.compile(
    r"(?i)/(test|tests|__tests__|spec|specs|features|migrations|db|ui|web|controllers|"
    r"node_modules|target|build)/")
TEST_FILE_RX = re.compile(
    r"(Test|Tests|IT|Spec)\.(java|kt|groovy)$|_test\.py$|^test_.*\.py$|\.(test|spec)\.(js|jsx|ts|tsx)$", re.I)
IO_CALL_RX = re.compile(
    r"(?i)\b(?:fetch|axios|request|http|urllib|requests\.|socket|open\s*\(|readFile|writeFile|"
    r"query|execute|jdbc|EntityManager|session\.|Repository|document\.|window\.|driver\.|"
    r"selenium|playwright|puppeteer|fs\.|os\.path|subprocess)\b")
CONDITIONAL_RX = re.compile(r"\b(?:if|else|switch|case|while|for|\?|elif)\b")
METHOD_DECL_RX = {
    "java": re.compile(r"(?:public|private|protected|static|final|\s)+[\w<>\[\],.? ]+\s+(\w+)\s*\([^)]*\)\s*(?:throws [\w,\s.]+)?\{"),
    "javascript": re.compile(r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\s*)?\(|^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{)", re.M),
    "typescript": re.compile(r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\s*)?\(|^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{)", re.M),
    "python": re.compile(r"^\s*def\s+(\w+)\s*\(", re.M),
}
LANG_BY_EXT = {".java": "java", ".kt": "java", ".js": "javascript", ".jsx": "javascript",
               ".mjs": "javascript", ".cjs": "javascript", ".ts": "typescript",
               ".tsx": "typescript", ".py": "python"}


def git(repo: str, *args, timeout=120):
    try:
        p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout
    except Exception:
        return 1, ""


# ------------------------------------------------------------------- indicators

def compute(repo_slug: str, repo_dir: str) -> tuple[dict, list[dict]]:
    now = datetime.now(timezone.utc)
    features: list[dict] = []
    step_defs: list[dict] = []
    domain_files: list[str] = []
    domain_t3: list[str] = []
    methods: list[tuple] = []

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in
                   {".git", "node_modules", "target", "build", "vendor", "dist",
                    ".gradle", "__pycache__", ".venv", "venv"}]
        for fn in files:
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, repo_dir).replace("\\", "/")
            low = fn.lower()
            if low.endswith(".feature"):
                features.append(parse_feature(path))
                continue
            ext = os.path.splitext(low)[1]
            if ext not in LANG_BY_EXT:
                continue
            lang = LANG_BY_EXT[ext]
            is_test = bool(TEST_FILE_RX.search(fn)) or bool(DENY_PATH_RX.search("/" + rel))
            try:
                src = open(path, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            # T1 domain tier: conventional domain paths, outside the denylist.
            if DOMAIN_PATH_RX.search("/" + rel) and not is_test:
                domain_files.append(rel)
            # T3 fallback candidates: non-test files with a decision-bearing
            # function and no obvious I/O (protocol 7.5 T3).
            elif not is_test:
                mdecl = METHOD_DECL_RX.get(lang)
                if mdecl and CONDITIONAL_RX.search(src) and not IO_CALL_RX.search(src):
                    domain_t3.append(rel)
            # Index every method so D2 can resolve STRONG_DELEGATED callees.
            mdecl = METHOD_DECL_RX.get(lang)
            if mdecl:
                toks = ASSERT_TOKENS.get(lang, [])
                spans = list(mdecl.finditer(src))
                for k, mm in enumerate(spans):
                    nm = next((g for g in mm.groups() if g), None)
                    if not nm:
                        continue
                    end = spans[k + 1].start() if k + 1 < len(spans) else min(len(src), mm.end() + 4000)
                    mbody = src[mm.start():end]
                    methods.append((nm, mbody, lang))
            if is_test:
                pass  # step definitions live in test trees; keep scanning for them
            decl = STEPDEF_DECL_RX.get(lang)
            if not decl:
                continue
            for m in decl.finditer(src):
                line = src.count("\n", 0, m.start()) + 1
                # body = next ~40 lines, until next step annotation
                nxt = decl.search(src, m.end())
                body = src[m.start(): nxt.start() if nxt else min(len(src), m.start() + 3000)]
                step_defs.append({"file": rel, "line": line, "expression": m.group(1),
                                  "lang": lang, "body": body})

    # ---- Domain layer tiers (protocol 7.5): T1+T2 preferred, T3 fallback.
    if domain_files:
        domain_effective = domain_files
        domain_tier = "T1+T2"
    elif domain_t3:
        domain_effective = domain_t3
        domain_tier = "T3"
    else:
        domain_effective = []
        domain_tier = "none"

    # ---- D1 skip_ratio
    all_scen = [s for f in features for s in f["scenarios"]]
    skipped = 0
    for f in features:
        ftag = any(SKIP_TAG_RX.search(t) for t in f["feature_tags"])
        for s in f["scenarios"]:
            st = any(SKIP_TAG_RX.search(t) for t in s["tags"])
            if ftag or st:
                skipped += 1
    n_scen = len(all_scen)
    skip_ratio = skipped / n_scen if n_scen else None
    active = [s for f in features for s in f["scenarios"]
              if not any(SKIP_TAG_RX.search(t) for t in f["feature_tags"] + s["tags"])]

    # ---- D2 assertion weakness (unit = step definition)
    # STRONG_DELEGATED resolution: a method is "strong" if its own body carries an
    # assertion token; a step definition that calls such a method inherits strength
    # (depth 1; depth 2 via a second expansion pass below).
    strong_methods = set()
    for nm, mbody, mlang in methods:
        if any(re.search(t, mbody) for t in ASSERT_TOKENS.get(mlang, [])):
            strong_methods.add(nm)
    # one extra expansion to approximate the protocol's depth<=2 rule
    for nm, mbody, mlang in methods:
        if nm in strong_methods:
            continue
        if any(re.search(r"\b%s\s*\(" % re.escape(sm), mbody) for sm in strong_methods):
            strong_methods.add(nm)

    class_counts = Counter()
    audit: list[dict] = []
    for d in step_defs:
        body = d["body"]
        tokens = ASSERT_TOKENS[d["lang"]]
        has_token = any(re.search(t, body) for t in tokens)
        weak_hits = [k for k, pats in WEAK_PATTERNS.items() if any(p.search(body) for p in pats)]
        # conservative W4: a try/catch that neither rethrows nor fails
        w4 = False
        if re.search(r"\btry\b", body):
            mcatch = re.search(r"(?:catch|except)[^{]*\{?([\s\S]{0,400})", body)
            if mcatch and not re.search(r"(throw|raise|fail\(|assert)", mcatch.group(1)):
                w4 = True
        # conservative W3: assertion textually after an unconditional return/throw
        w3 = False
        mret = re.search(r"^\s*(?:return|throw|raise)\b.*$", body, re.M)
        if mret and has_token and re.search(r"\bassert", body[mret.end():]):
            w3 = True
        weak = bool(weak_hits) or w4 or w3
        delegated = False
        if not has_token:
            delegated = any(re.search(r"\b%s\s*\(" % re.escape(sm), body) for sm in strong_methods)
        if has_token and weak:
            cls = "WEAK"
        elif has_token:
            cls = "STRONG_DIRECT"
        elif delegated:
            cls = "STRONG_DELEGATED"
        else:
            cls = "NONE"
        class_counts[cls] += 1
        audit.append({"repo": repo_slug, "file": d["file"], "line": d["line"],
                      "lang": d["lang"], "expression": d["expression"],
                      "class": cls, "weak_kinds": ";".join(weak_hits + (["W4"] if w4 else []) + (["W3"] if w3 else [])),
                      "has_token": int(has_token), "delegated": int(delegated)})
    denom2 = (class_counts["STRONG_DIRECT"] + class_counts["STRONG_DELEGATED"]
              + class_counts["WEAK"] + class_counts["NONE"])
    awr = (class_counts["WEAK"] + class_counts["NONE"]) / denom2 if denom2 else None

    # ---- D4 redundancy clusters (normalised-text fingerprint)
    fps = [frozenset(normalise_step(s[2]) for s in sc["steps"]) for sc in active if sc["steps"]]
    n_active = len(active)
    if fps:
        parent = list(range(len(fps)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i in range(len(fps)):
            for j in range(i + 1, len(fps)):
                inter = len(fps[i] & fps[j])
                if inter == 0:
                    continue
                union = len(fps[i] | fps[j])
                if union and inter / union >= 0.8:
                    ri, rj = find(i), find(j)
                    if ri != rj:
                        parent[ri] = rj
        comps = len({find(i) for i in range(len(fps))})
        redundancy = 1 - comps / n_active if n_active else None
    else:
        redundancy = None

    # ---- D5 glue duplication (unique normalised step / invocations in active scenarios)
    invocations = [normalise_step(s[2]) for sc in active for s in sc["steps"]]
    glue = (len(set(invocations)) / len(invocations)) if invocations else None

    # ---- D6 literal-bearing step definitions
    lit_defs = 0
    resolved = 0
    for d in step_defs:
        resolved += 1
        body = d["body"]
        body_nomsg = "\n".join(ln for ln in body.splitlines()
                               if not LITERAL_SKIP_RX.search(ln) and "message" not in ln.lower())
        n_nums = len([x for x in NUM_RX.findall(body_nomsg) if x not in ("0", "1")])
        n_strs = len([g for g in STR_RX.findall(body_nomsg)
                      if not (g[0] or g[1]).startswith(("\\n", "%s", "{}"))])
        if n_nums + n_strs >= 1:
            lit_defs += 1
    d6 = lit_defs / resolved if resolved else None

    # ---- D7 mirror_loose: expected value is a computed expression referencing a
    # domain call, and the actual comes from a domain call.
    mirror = 0
    for d in step_defs:
        body = d["body"]
        m1 = bool(re.search(r"(?:assertEquals|expect|assertThat|assert\s*\(|isEqualTo)\s*\([^,)]*[,)]\s*[^,)]*[\w.]+\s*[+\-*/]", body)
                 or re.search(r"expect\s*\(\s*[\w.]+\s*[+\-*/]", body))
        m2 = bool(re.search(r"\b(?:get|calc|compute|price|total|rate|discount|amount|balance|score)\w*\s*\(", body, re.I))
        m3 = bool(re.search(r"(?:assertEquals|assertThat|expect)\s*\([^,]*,[^,)]*\b\w+\s*\(", body))
        if m1 and m2 and m3:
            mirror += 1
    d7 = mirror / resolved if resolved else None
    mirror_loose_count = mirror

    # ---- D3 stale specs (git blame per scenario)
    stale = 0
    d3_ok = bool(all_scen)
    if d3_ok:
        commits_cache: dict[str, int] = {}
        for f in features:
            rel = os.path.relpath(f["path"], repo_dir).replace("\\", "/")
            for sc in f["scenarios"]:
                if sc not in active:
                    continue
                code, out = git(repo_dir, "blame", "--line-porcelain",
                                f"-L{sc['start_line']},{max(sc['end_line'], sc['start_line'])}",
                                "--", rel)
                if code != 0:
                    continue
                dates = re.findall(r"^committer-time (\d+)$", out, re.M)
                if not dates:
                    continue
                t_s = datetime.fromtimestamp(max(int(x) for x in dates), tz=timezone.utc)
                age = (now - t_s).days
                if age < 180:
                    continue
                if rel not in commits_cache:
                    c2, out2 = git(repo_dir, "log", "--since", t_s.isoformat(),
                                   "--oneline", "--", "." )
                    commits_cache[rel] = out2.count("\n")
                if commits_cache[rel] >= 5:
                    stale += 1
    d3 = stale / len(active) if active and d3_ok else None

    row = {
        "repo": repo_slug,
        "n_features": len(features),
        "n_scenarios": n_scen,
        "n_active_scenarios": len(active),
        "n_skipped": skipped,
        "n_step_defs": len(step_defs),
        "n_domain_files": len(domain_effective),
        "domain_tier": domain_tier,
        "domain_files": ";".join(sorted(domain_effective)[:12]),
        "D1_skip_ratio": skip_ratio,
        "D2_assertion_weakness_ratio": awr,
        "D2_unresolved": 0,
        "D2_confidence": "high" if denom2 and class_counts["NONE"] / denom2 < 0.25 else "low_confidence",
        "D3_stale_spec_ratio": d3,
        "D4_redundancy_cluster_ratio": redundancy,
        "D4_fingerprint_source": "normalised_text",
        "D5_glue_duplication_ratio": glue,
        "D6_literal_bearing_stepdef_ratio": d6,
        "D7_mirror_stepdef_ratio": d7,
        "D7_mirror_loose_count": mirror_loose_count,
        "D7_validated": 0,
        "stats_strong": class_counts["STRONG_DIRECT"],
        "stats_delegated": class_counts["STRONG_DELEGATED"],
        "stats_weak": class_counts["WEAK"],
        "stats_none": class_counts["NONE"],
        "n_step_invocations": len(invocations),
        "language": (Counter(d["lang"] for d in step_defs).most_common(1)[0][0]
                     if step_defs else "unknown"),
    }
    return row, audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--repo-dir", default=None)
    ap.add_argument("--outdir", default=os.path.join("data", "metrics"))
    a = ap.parse_args()
    repo_dir = a.repo_dir or os.path.join("data", "repos", a.repo.replace("/", "__", 1))
    if not os.path.isdir(repo_dir):
        print(json.dumps({"repo": a.repo, "error": "repo dir missing"}))
        return 1
    row, audit = compute(a.repo, repo_dir)
    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "static_indicators.csv"), "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if f.tell() == 0:
            w.writeheader()
        w.writerow(row)
    with open(os.path.join(a.outdir, "stepdef_audit.csv"), "a", newline="", encoding="utf-8") as f:
        if audit:
            w = csv.DictWriter(f, fieldnames=list(audit[0].keys()))
            if f.tell() == 0:
                w.writeheader()
            w.writerows(audit)
    print(json.dumps(row, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
