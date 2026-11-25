import urllib.request, urllib.parse, time
for scheme in ("https","http"):
    url = scheme + "://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query":'all:"mutation testing" AND all:cucumber',"max_results":5})
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (research lit review; contact: local)"})
    try:
        d = urllib.request.urlopen(req, timeout=45).read()
        print(scheme, "OK", len(d)); print(d.decode()[:1500]); break
    except Exception as e:
        print(scheme, "ERR", repr(e)); time.sleep(5)
