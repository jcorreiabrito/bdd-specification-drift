import json, os, shutil

cache = {}
for f in ('notes_db/crossref_bdd.json', 'notes_db/crossref_bdd2.json'):
    if os.path.exists(f):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            cache[k] = v
os.makedirs('lit', exist_ok=True)
json.dump(cache, open('lit/crossref-cache.bdd.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('cache entries:', len(cache), 'ok:',
      sum(1 for v in cache.values() if 'error' not in v))
