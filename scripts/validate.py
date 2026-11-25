import csv, json, os

refs = list(csv.reader(open('refs/verified.bdd.csv', encoding='utf-8')))
mat = list(csv.reader(open('lit/matrix.bdd.csv', encoding='utf-8')))
print('refs rows(excl header):', len(refs) - 1, 'col counts:', sorted(set(len(r) for r in refs)))
print('matrix rows(excl header):', len(mat) - 1, 'col counts:', sorted(set(len(r) for r in mat)))

cr = {}
for f in ('notes_db/crossref_bdd.json', 'notes_db/crossref_bdd2.json'):
    if os.path.exists(f):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            if 'error' not in v:
                cr[k.lower()] = v

rk = [r[0] for r in refs[1:]]
mk = [r[0] for r in mat[1:]]
print('dup keys refs:', [k for k in set(rk) if rk.count(k) > 1])
print('refs keys not in matrix:', sorted(set(rk) - set(mk)))
print('matrix keys not in refs:', sorted(set(mk) - set(rk)))

bad = []
for r in refs[1:]:
    doi = r[5]
    if doi.lower() not in cr:
        bad.append((r[0], doi, 'NOT_IN_CROSSREF_CACHE'))
        continue
    v = cr[doi.lower()]
    if not r[1][:25].lower() in (v['title'] or '').lower():
        bad.append((r[0], doi, 'TITLE_MISMATCH: ' + (v['title'] or '')[:40]))
print('--- integrity problems:')
for b in bad:
    print('  ', b)
print('--- all DOIs verified in cache:', len(refs) - 1 - len(bad), '/', len(refs) - 1)
