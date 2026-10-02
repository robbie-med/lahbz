import sys
from bs4 import BeautifulSoup
def text(f):
    s=BeautifulSoup(open(f).read(),'html.parser')
    for t in s(['script','style']): t.decompose()
    if s.body is None: return ""
    txt=s.body.get_text('\n',strip=True)
    i=txt.find('Print Test Information')
    if i<0: i=txt.find('Interpretive Data Search')+len('Interpretive Data Search')
    else: i+=len('Print Test Information')
    j=txt.find('Test Directory Service provided by')
    return txt[i:j].strip()
if __name__=='__main__':
    for f in sys.argv[1:]: print('#####',f); print(text(f))
