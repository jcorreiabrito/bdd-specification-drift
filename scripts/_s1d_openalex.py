import urllib.request, urllib.parse, json, time, sys, os, io

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "lit-review/1.0 (mailto:research@example.org)"}

def oa(search=None, filt=None, per=25):
    p = {"per-page": per, "mailto": "research@example.org"}
    if search: p["search"] = search
    if filt: p["filter"] = filt
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(p)
    for attempt in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            return json.loads(b)
        except Exception as e:
            print("  retry", attempt, repr(e)[:80], flush=True); time.sleep(5*(attempt+1))
    return None

def abstract(w):
    inv = w.get("abstract_inverted_index")
    if not inv: return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs: pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))

def show(d, label=""):
    if not d: return
    print("=" * 110)
    print("QUERY:", label, "| count:", d["meta"]["count"])
    for w in d["results"]:
        au = "; ".join((a["author"]["display_name"] or "") for a in w.get("authorships", [])[:3])
        src = (w.get("primary_location") or {}).get("source") or {}
        print(f'  [{w.get("publication_year")}] {w.get("title")}')
        print(f'      venue={src.get("display_name")} | doi={w.get("doi")} | cited={w.get("cited_by_count")} | {au}')
        ab = abstract(w)
        if ab: print("      ABS:", ab[:460].replace("\n", " "))

CS = "primary_topic.field.id:fields/17"
QUERIES = sys.argv[1:]
for q in QUERIES:
    show(oa(search=q, filt=CS, per=25), q)
    time.sleep(1)
