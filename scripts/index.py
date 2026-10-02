import requests, re, json, sys, time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
host=sys.argv[1]
S=requests.Session(); S.headers.update(UA)
def get(url):
    for i in range(4):
        try:
            r=S.get(url,timeout=30); r.raise_for_status(); return r.text
        except Exception as e:
            time.sleep(2**i)
    raise
def letter(L):
    out={}; page=1
    while True:
        h=get(f'https://{host}/search/?letter={L}&page={page}')
        s=BeautifulSoup(h,'html.parser')
        found=0
        for a in s.find_all('a',href=True):
            m=re.search(r'tests/?\?test=(\d+)',a['href'])
            if m:
                out[m.group(1)]=a.get_text(' ',strip=True); found+=1
        pages=[int(p) for p in re.findall(r'letter=%s&(?:amp;)?page=(\d+)'%L,h)]
        if not pages or page>=max(pages) or not found: break
        page+=1
    return L,out
res={}
with ThreadPoolExecutor(4) as ex:
    for L,o in ex.map(letter,list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')):
        print(L,len(o),file=sys.stderr); res.update(o)
json.dump(res,open(f'index_{host}.json','w'),indent=0)
print(host,len(res))
