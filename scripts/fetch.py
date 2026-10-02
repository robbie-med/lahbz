import requests, json, os, time, sys
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
idx=json.load(open('index_labcatalog.net.json'))
S=requests.Session(); S.headers.update(UA)
def f(i):
    p=f'raw/{i}.html'
    if os.path.exists(p) and os.path.getsize(p)>2000: return 0
    for k in range(5):
        try:
            r=S.get(f'https://labcatalog.net/tests/?test={i}',timeout=30); r.raise_for_status()
            open(p,'w').write(r.text); return 1
        except Exception as e: time.sleep(2**k)
    print('FAIL',i,file=sys.stderr); return 0
with ThreadPoolExecutor(6) as ex: n=sum(ex.map(f,idx))
print('fetched',n, 'total files',len(os.listdir('raw')))
