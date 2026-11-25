import urllib.request, urllib.parse, json, time, sys, os, re

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "lit-review/1.0 (mailto:research@example.org)"}
CS = "primary_topic.field.id:fields/17"

def get_json(url):
    for a in range(5):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read())
        except Exception as e:
            print("   retry", a, repr(e)[:70], flush=True); time.sleep(4 * (a + 1))
    return None

def abstract(w):
    inv = w.get("abstract_inverted_index")
    if not inv: return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs: pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))

def search(q, per=100, pages=1, extra_filter=""):
    out, cursor = [], "*"
    for _ in range(pages):
        p = {"per-page": per, "cursor": cursor, "mailto": "research@example.org", "search": q,
             "filter": CS + ("," + extra_filter if extra_filter else "")}
        d = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(p))
        if not d: break
        out += d.get("results", [])
        cursor = d.get("meta", {}).get("next_cursor")
        if not cursor: break
    return out

KEY = re.compile(r"cucumber|gherkin|\bbdd\b|behaviou?r.driven|acceptance.test|end.to.end|\be2e\b|system.test|system.level|specification.based|executable specification|test.oracle|oracle problem|higher.level|integration test|test level|test pyramid", re.I)

def screen(label, works, show_all=False):
    print("=" * 110); print("QUERY:", label, "| fetched:", len(works))
    seen = set()
    for w in works:
        t = w.get("title") or ""
        ab = abstract(w)
        if (w.get("doi") or t) in seen: continue
        seen.add(w.get("doi") or t)
        blob = t + " " + ab
        if not show_all and not KEY.search(blob): continue
        src = (w.get("primary_location") or {}).get("source") or {}
        au = "; ".join((a["author"]["display_name"] or "") for a in w.get("authorships", [])[:3])
        print(f'  [{w.get("publication_year")}] {t}')
        print(f'      venue={src.get("display_name")} | doi={w.get("doi")} | cited={w.get("cited_by_count")} | {au}')
        if ab: print("      ABS:", ab[:400].replace("\n", " "))

QUERIES = [
 "mutation testing cucumber",
 "mutation testing behavior driven development",
 "mutation analysis BDD scenarios",
 "mutation testing acceptance tests",
 "mutation testing end-to-end web tests",
 "mutation analysis system tests",
 "mutation testing test oracle",
 "test oracle quality acceptance testing",
 "mutation testing executable specifications",
 "mutation testing integration tests",
 "test pyramid empirical study",
 "specification coverage business rules tests",
]
for q in QUERIES:
    ws = search(q, per=100, pages=2)
    screen(q, ws)
    time.sleep(1.5)
