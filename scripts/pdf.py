import sys, os, urllib.request, io

def fetch(url, out, timeout=90):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) bdd-lit/1.0",
        "Accept": "application/pdf,*/*"})
    data = urllib.request.urlopen(req, timeout=timeout).read()
    if not data[:4] == b"%PDF":
        return "NOT_PDF len=%d head=%r" % (len(data), data[:80])
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out + ".pdf", "wb") as f:
        f.write(data)
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(data))
    txt = []
    for i, p in enumerate(r.pages):
        try:
            txt.append("\n===== PAGE %d =====\n" % (i + 1) + (p.extract_text() or ""))
        except Exception as e:
            txt.append("\n===== PAGE %d ERR %s =====\n" % (i + 1, e))
    with open(out + ".txt", "w", encoding="utf-8") as f:
        f.write("".join(txt))
    return "OK pages=%d chars=%d" % (len(r.pages), sum(len(t) for t in txt))

if __name__ == "__main__":
    print(fetch(sys.argv[1], sys.argv[2]))
