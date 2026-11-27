import csv,gzip,io,json,urllib.request
from collections import defaultdict
def read(name):
    url='https://cdn.rebrickable.com/media/downloads/'+name+'.csv.gz'
    with urllib.request.urlopen(url,timeout=120) as r:
        return list(csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(r.read())),encoding='utf-8-sig')))
themes=read('themes')
ids={t['id'] for t in themes if 'ninjago' in t['name'].lower()}
while True:
    new=ids|{t['id'] for t in themes if t['parent_id'] in ids}
    if new==ids: break
    ids=new
sets={s['set_num']:s for s in read('sets') if s['theme_id'] in ids}
inv={i['id']:i['set_num'] for i in read('inventories') if i['set_num'] in sets}
links=defaultdict(set)
for row in read('inventory_minifigs'):
    if row['inventory_id'] in inv: links[row['fig_num']].add(inv[row['inventory_id']])
out=[]
for f in read('minifigs'):
    n=f['fig_num']
    if n not in links: continue
    numbers=sorted(links[n])
    year=min(int(sets[k]['year']) for k in numbers)
    out.append(dict(id='rb-'+n,category='LEGO',title=f['name'],number=n,series=f['name'].split(' - ')[0],arc=str(year),brand=', '.join(numbers),image=f.get('img_url',''),status='Missing',condition='Unknown',price='',value='',photo='',notes=''))
assert len(out)>100, 'Unexpectedly small catalogue'
with open('catalog.json','w',encoding='utf-8') as f: json.dump(sorted(out,key=lambda x:(x['arc'],x['title'],x['id'])),f,ensure_ascii=False,separators=(',',':'))
print(len(out),'figures')
