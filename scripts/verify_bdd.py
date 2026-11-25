import sys, json, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cr import cr

DOIS = [
    "10.1109/SANER53432.2022.00134",
    "10.1109/SANER.2018.8330207",
    "10.1007/978-3-030-49392-9_6",
    "10.1109/ACCESS.2023.3302356",
    "10.1016/j.jss.2023.111749",
    "10.1145/3350768.3351301",
    "10.1145/3571473.3571492",
    "10.1109/REW.2017.62",
    "10.1007/978-3-319-77243-1_18",
    "10.1145/2786805.2786858",
    "10.1109/ICST.2011.50",
    "10.1109/ICSTW.2013.49",
    "10.48550/arXiv.2501.01873",
    "10.1145/3377812.3382176",
    "10.1145/3607183",
    "10.1007/s11219-023-09616-6",
    "10.1007/s10664-022-10251-1",
    "10.1007/s10664-010-9143-7",
    "10.1016/j.jss.2020.110840",
    "10.1016/j.infsof.2021.106717",
    "10.1016/j.jss.2021.110944",
    "10.48550/arXiv.2604.20462",
    "10.1109/ICSME.2015.7332456",
    "10.1109/ICSE43902.2021.00087",
]

OUT = "notes_db/crossref_bdd.json"
res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT, encoding="utf-8"))

for doi in DOIS:
    if doi in res and "error" not in res[doi]:
        print("skip", doi)
        continue
    r = None
    for attempt in range(6):
        r = cr(doi)
        if "error" not in r:
            break
        time.sleep(6 + 5 * attempt)
    res[doi] = r
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(doi, "->", "OK" if "error" not in r else r["error"])
    time.sleep(2.5)
print("DONE", len(res))
