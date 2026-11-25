import sys, json, time, urllib.request, urllib.parse

BASE = "https://api.openalex.org/works"

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "bdd-lit/1.0 (mailto:research@example.org)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def inv(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))

N = int(sys.argv[1])
for doi in sys.argv[2:]:
    try:
        d = json.loads(get(BASE + "/https://doi.org/" + urllib.parse.quote(doi)))
        au = [a["author"]["display_name"] for a in d.get("authorships", [])][:6]
        print("==", doi)
        print("T:", (d.get("title") or "")[:150])
        print("V:", ((d.get("primary_location") or {}).get("source") or {}).get("display_name"), "|", d.get("publication_year"), "|", d.get("type"))
        print("A:", "; ".join(au))
        print("OA:", (d.get("open_access") or {}).get("oa_url"))
        print("ABS:", inv(d.get("abstract_inverted_index"))[:N])
        print()
    except Exception as e:
        print("==", doi, "ERR", e)
    time.sleep(0.7)
