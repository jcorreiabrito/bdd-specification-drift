import sys, json, urllib.request, urllib.error, time

def get(url, timeout=40):
    req = urllib.request.Request(url, headers={
        "User-Agent": "bdd-lit-review/1.0 (mailto:research@example.org)",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def cr(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    try:
        d = json.loads(get(url))["message"]
    except Exception as e:
        return {"doi": doi, "error": str(e)}
    auth = d.get("author", []) or []
    names = []
    for a in auth:
        fam = a.get("family", "")
        giv = a.get("given", "")
        ini = "".join([p[0] + "." for p in giv.replace("-", " ").split() if p])
        names.append((fam + ", " + ini).strip(", "))
    if len(names) > 6:
        names = names[:6] + ["et al."]
    yr = None
    for k in ("published-print", "published-online", "issued", "created"):
        if k in d and d[k].get("date-parts") and d[k]["date-parts"][0][0]:
            yr = d[k]["date-parts"][0][0]
            break
    return {
        "doi": d.get("DOI"),
        "title": (d.get("title") or [""])[0],
        "authors": "; ".join(names),
        "year": yr,
        "container": (d.get("container-title") or [""])[0],
        "type": d.get("type"),
        "abstract": (d.get("abstract") or "")[:1600],
        "url": d.get("URL"),
    }

if __name__ == "__main__":
    for doi in sys.argv[1:]:
        r = cr(doi)
        print(json.dumps(r, ensure_ascii=False))
        print("---")
        time.sleep(0.4)
