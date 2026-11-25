import csv, io, sys
p = 'lit/matrix.bdd.csv'
rows = list(csv.reader(open(p, encoding='utf-8')))
hdr = rows[0]
print('header cols', len(hdr), hdr)
idx = hdr.index('public_repos')
fix = {'zhang2015assertions', 'kim2020testsmell', 'sun2023coevolution', 'leotta2024mutta'}
for r in rows[1:]:
    if r[0] in fix:
        r[idx] = 'unclear'
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerows(rows)
rows2 = list(csv.reader(open(p, encoding='utf-8')))
print('rows', len(rows2), 'col counts', sorted(set(len(r) for r in rows2)))
for r in rows2[1:]:
    print(r[0], '|', r[1], '|', r[2], '|', r[5], r[6], r[7], r[8])
