import glob,os,json,re
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
def one(f):
    code=os.path.basename(f)[:-5]
    s=BeautifulSoup(open(f).read(),'html.parser')
    for t in s(['script','style','nav','header','footer']): t.decompose()
    h1=s.find('h1'); name=h1.get_text(' ',strip=True) if h1 else ''
    sec={}
    for h in s.find_all('h3'):
        k=h.get_text(' ',strip=True)
        if k in sec: continue
        p=h.parent
        txt=p.get_text('\n',strip=True)
        if txt.startswith(k): txt=txt[len(k):].strip()
        sec[k]=txt[:3000]
    txt=s.get_text('\n',strip=True)
    oc=re.search(r'Order Code\s*\n?\s*(\d{6})',txt)
    cpt=re.search(r'CPT\s*\n([^\n]+)',txt)
    return code,{'name':name,'sec':sec,'cpt':cpt.group(1) if cpt else ''}
fs=glob.glob('lcn/*.html')
with ProcessPoolExecutor() as ex: d=dict(ex.map(one,fs,chunksize=40))
json.dump(d,open('national.json','w'))
print(len(d))
import collections
c=collections.Counter(k for v in d.values() for k in v['sec'])
print(c.most_common(40))
print(d.get('330015',{}).get('name'), list(d.get('330015',{}).get('sec',{}).items())[:4])
