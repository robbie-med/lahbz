import requests,os,time,sys
from concurrent.futures import ThreadPoolExecutor
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'
urls=[l.strip() for l in open('lcn_urls.txt') if l.strip()]
def f(u):
    code=u.split('/tests/')[1].split('/')[0]
    p=f'lcn/{code}.html'
    if os.path.exists(p) and os.path.getsize(p)>5000: return
    for k in range(4):
        try:
            r=S.get(u,timeout=40)
            if r.status_code==404: return
            r.raise_for_status(); open(p,'w').write(r.text); return
        except Exception: time.sleep(2**k)
    print('FAIL',u,file=sys.stderr)
with ThreadPoolExecutor(5) as ex: list(ex.map(f,urls))
print('done',len(os.listdir('lcn')))
