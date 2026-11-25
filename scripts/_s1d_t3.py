import urllib.request, urllib.parse, json
def get(url, hdr=None):
    req = urllib.request.Request(url, headers=hdr or {"User-Agent":"lit-review/1.0 (mailto:research@example.org)"})
    return urllib.request.urlopen(req, timeout=60).read()
tests = {
 "openalex": "https://api.openalex.org/works?search=mutation%20testing&per-page=2",
 "crossref": "https://api.crossref.org/works?query.bibliographic=mutation+testing+cucumber&rows=2&select=DOI,title",
 "s2": "https://api.semanticscholar.org/graph/v1/paper/search?query=mutation+testing+cucumber&limit=2&fields=title,year,venue,externalIds",
}
for k,u in tests.items():
    try:
        b = get(u); print(k, "OK", len(b)); print(b[:600].decode(errors="replace")); print("-"*60)
    except Exception as e:
        print(k, "ERR", repr(e))
