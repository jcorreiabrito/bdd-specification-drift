import sys, json, urllib.request, urllib.parse, time

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "bdd-lit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def q(term, rows=8):
    url = ("https://dblp.org/search/publ/api?q=" + urllib.parse.quote(term)
           + "&format=json&h=%d" % rows)
    d = json.loads(get(url))
    hits = d.get("result", {}).get("hits", {}).get("hit", [])
    out = []
    for h in hits:
        i = h["info"]
        au = i.get("authors", {}).get("author", [])
        if isinstance(au, dict):
            au = [au]
        out.append({
            "t": i.get("title", "")[:105],
            "v": i.get("venue", ""),
            "y": i.get("year", ""),
            "doi": i.get("doi", ""),
            "type": i.get("type", ""),
            "a": "; ".join([a.get("text", "") for a in au][:4]),
        })
    return out

if __name__ == "__main__":
    for t in sys.argv[1:]:
        print("### " + t)
        try:
            for r in q(t):
                print("   ", json.dumps(r, ensure_ascii=False))
        except Exception as e:
            print("   ERR", e)
        time.sleep(1.5)
