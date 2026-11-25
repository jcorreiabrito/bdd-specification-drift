import sys, json, urllib.request, urllib.parse, time

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={
        "User-Agent": "bdd-lit/1.0 (mailto:research@example.org)",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def q(title, rows=3):
    url = ("https://api.crossref.org/works?query.bibliographic="
           + urllib.parse.quote(title) + "&rows=%d&select=DOI,title,container-title,author,issued,type" % rows)
    for attempt in range(5):
        try:
            items = json.loads(get(url))["message"]["items"]
            break
        except Exception as e:
            if attempt == 4:
                return [{"error": str(e)}]
            time.sleep(3 + 3 * attempt)
    out = []
    for it in items:
        yr = None
        if it.get("issued", {}).get("date-parts"):
            yr = it["issued"]["date-parts"][0][0]
        au = it.get("author", []) or []
        fam = [a.get("family", "") for a in au[:3]]
        out.append({
            "doi": it.get("DOI"),
            "title": (it.get("title") or [""])[0][:110],
            "venue": (it.get("container-title") or [""])[0][:60],
            "year": yr,
            "type": it.get("type"),
            "a": "; ".join(fam),
        })
    return out

if __name__ == "__main__":
    for t in sys.argv[1:]:
        print("### " + t)
        for r in q(t, 3):
            print("   ", json.dumps(r, ensure_ascii=False))
        time.sleep(1.0)
