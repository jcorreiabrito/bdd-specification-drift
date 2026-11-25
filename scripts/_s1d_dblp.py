import urllib.request, json, time, urllib.parse
def dblp(q, h=60):
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode({"q":q,"format":"json","h":h})
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    hits = d["result"]["hits"]
    print("="*100); print("DBLP Q:", q, "total:", hits.get("@total"))
    for hh in hits.get("hit", []):
        i = hh["info"]
        au = i.get("authors",{}).get("author",[])
        if isinstance(au, dict): au=[au]
        names = "; ".join(a["text"] for a in au)
        print(f'  {i.get("year")} | {i.get("title")} | {i.get("venue")} | doi={i.get("doi","")} | {names[:90]}')
    time.sleep(2)
for q in ["mutation testing cucumber", "mutation analysis BDD", "mutation testing behavior-driven development",
          "mutation testing acceptance tests", "mutation testing end-to-end", "mutation analysis E2E web tests"]:
    try: dblp(q)
    except Exception as e: print("ERR",q,e)
