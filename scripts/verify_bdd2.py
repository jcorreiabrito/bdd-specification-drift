import sys, json, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cr import cr

DOIS = [
    "10.1109/ICST.2011.50",
    "10.1109/ICSTW.2013.49",
    "10.1145/2786805.2786858",
    "10.1145/3377812.3382176",
    "10.1145/3607183",
    "10.1007/s11219-023-09616-6",
    "10.1007/s10664-022-10251-1",
    "10.1016/j.infsof.2021.106717",
    "10.1016/j.jss.2021.110944",
    "10.1016/j.jss.2020.110840",
]

OUT = "notes_db/crossref_bdd2.json"
res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT, encoding="utf-8"))

for doi in DOIS:
    if doi in res and "error" not in res[doi]:
        print("skip", doi)
        continue
    r = None
    for attempt in range(3):
        r = cr(doi)
        if "error" not in r:
            break
        time.sleep(3 + 3 * attempt)
    res[doi] = r
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(doi, "->", "OK" if "error" not in r else r["error"], flush=True)
    time.sleep(2.0)
print("DONE2", len(res))
