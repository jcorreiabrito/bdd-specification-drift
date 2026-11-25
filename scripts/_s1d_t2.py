import urllib.request, urllib.parse
url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode({"q":"mutation testing cucumber","format":"json","h":10})
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (compatible; lit-review/1.0)"})
try:
    r = urllib.request.urlopen(req, timeout=60)
    print(r.status, r.geturl())
    b = r.read()
    print(len(b)); print(b[:800])
except Exception as e:
    print("ERR", repr(e))
