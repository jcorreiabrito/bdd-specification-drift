import urllib.request, urllib.parse, json, re, sys, time, xml.etree.ElementTree as ET

QUERIES = [
    'all:"mutation testing" AND all:cucumber',
    'all:"mutation testing" AND all:"behaviour-driven development"',
    'all:"mutation testing" AND all:"behavior-driven development"',
    'all:"mutation testing" AND all:"acceptance test"',
    'all:"mutation analysis" AND all:"acceptance testing"',
    'all:"mutation testing" AND all:"end-to-end"',
    'all:"mutation score" AND all:"system tests"',
    'all:"oracle problem" AND all:"acceptance test"',
    'all:"test oracle" AND all:"automated testing" AND all:specification',
    'all:"mutation testing" AND all:"executable specification"',
    'all:"mutation" AND all:"test level" AND all:empirical',
    'all:"behaviour-driven development" AND all:empirical',
    'all:"test pyramid" AND all:empirical',
    'all:"oracle strength"',
    'all:"domain mutation"',
]

NS = {'a': 'http://www.w3.org/2005/Atom'}
for q in QUERIES:
    url = 'http://export.arxiv.org/api/query?' + urllib.parse.urlencode({
        'search_query': q, 'start': 0, 'max_results': 25, 'sortBy': 'relevance'})
    try:
        data = urllib.request.urlopen(url, timeout=60).read()
    except Exception as e:
        print('ERR', q, e); continue
    root = ET.fromstring(data)
    entries = root.findall('a:entry', NS)
    print('=' * 100)
    print('QUERY:', q, ' -> ', len(entries), 'entries')
    for e in entries:
        title = ' '.join(e.find('a:title', NS).text.split())
        pub = e.find('a:published', NS).text[:10]
        doi_el = e.find('{http://arxiv.org/schemas/atom}doi')
        doi = doi_el.text if doi_el is not None else ''
        aid = e.find('a:id', NS).text
        print(f'  [{pub}] {title}  | {aid} | doi={doi}')
    time.sleep(3)
