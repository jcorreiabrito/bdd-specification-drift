import sys, json, urllib.request, urllib.parse, time

BASE = "https://api.openalex.org/works"

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "bdd-lit/1.0 (mailto:research@example.org)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def inv_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))

def show(w, nabs=900):
    return {
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": (w.get("title") or "")[:115],
        "year": w.get("publication_year"),
        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "type": w.get("type"),
        "oa": (w.get("open_access") or {}).get("oa_url"),
        "cited": w.get("cited_by_count"),
        "abstract": inv_abstract(w.get("abstract_inverted_index"))[:nabs],
    }

def search(term, rows=5):
    url = BASE + "?search=" + urllib.parse.quote(term) + "&per-page=%d" % rows
    d = json.loads(get(url))
    return [show(w) for w in d.get("results", [])]

def by_doi(doi):
    d = json.loads(get(BASE + "/https://doi.org/" + urllib.parse.quote(doi)))
    return show(d, 2000)

def brief(term, rows=5):
    url = BASE + "?search=" + urllib.parse.quote(term) + "&per-page=%d" % rows
    d = json.loads(get(url))
    out = []
    for w in d.get("results", []):
        out.append({
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "t": (w.get("title") or "")[:100],
            "y": w.get("publication_year"),
            "v": (((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "")[:45],
            "c": w.get("cited_by_count"),
        })
    return out

if __name__ == "__main__":
    mode = sys.argv[1]
    for t in sys.argv[2:]:
        print("### " + t)
        try:
            if mode == "doi":
                r = by_doi(t)
                print(json.dumps(r, ensure_ascii=False, indent=1))
            elif mode == "brief":
                for r in brief(t):
                    print("  -", json.dumps(r, ensure_ascii=False))
            else:
                for r in search(t):
                    print("  -", json.dumps(r, ensure_ascii=False))
        except Exception as e:
            print("  ERR", e)
        time.sleep(1.0)
