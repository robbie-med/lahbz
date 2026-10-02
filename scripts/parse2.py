import json,re
d=json.load(open('texts.json')); idx=json.load(open('index_labcatalog.net.json'))
GEN_LABELS=['Testing Schedule','Expected TAT','Clinical Use','Notes','Performing Labcorp Test Code','CPT Code(s)','Lab Section','Internal Comments','Reference Range','Reference Interval','Limitations','Interpretive Data','Patient Preparation']
INS_LABELS=['Container:','Collection:','Causes for Rejection:','Storage Instructions:','Stability Requirements:','Patient Preparation:','Special Instructions:','Volume:','Specimen:','Transport:','Note:']
def between(t,a,bs):
    i=t.find(a)
    if i<0: return None
    i+=len(a); j=min([t.find(b,i) for b in bs if t.find(b,i)>=0] or [len(t)])
    return t[i:j].strip()
out=[]
loinc=re.compile(r'^(\d{1,6}-\d|n/a|N/A|NA)$')
for tid,t in d.items():
    if not t: continue
    L=t.split('\n'); r={'id':int(tid),'name':L[0]}
    r['order']=between(t,'Order Name\n',['\n'])
    r['num']=between(t,'Test Number:\n',['\n'])
    r['rev']=between(t,'Revision Date\n',['\n'])
    ob=between(t,'Obsolete Reason\n',['\nTest Name\nMethodology','SPECIMEN REQUIREMENTS'])
    if ob is not None: r['obsolete']=re.sub(r'\n?\[\n?','[',re.sub(r'\n?\]\n?','] ',ob)).replace('\n',' ').strip() or 'Obsolete'
    comp=between(t,'Test Name\nMethodology\nLOINC Code',['SPECIMEN REQUIREMENTS','GENERAL INFORMATION'])
    if comp:
        rows=[];cur=[]
        for x in comp.split('\n'):
            cur.append(x)
            if loinc.match(x): rows.append(cur);cur=[]
        if cur: rows.append(cur)
        r['comp']=rows
    sp=between(t,'Transport Environment\n',['\nInstructions\n','GENERAL INFORMATION'])
    if sp:
        rows=[];cur=None
        for x in sp.split('\n'):
            if re.match(r'^(Preferred|Alternate\s*\d*|Acceptable|Optional)$',x): cur=[x];rows.append(cur)
            elif cur is not None: cur.append(x)
            else: cur=['Specimen',x];rows.append(cur)
        r['spec']=rows
    ins=between(t,'\nInstructions\n',['GENERAL INFORMATION'])
    if ins: r['ins']=ins
    g=t[t.find('GENERAL INFORMATION')+19:] if 'GENERAL INFORMATION' in t else ''
    if g:
        lines=g.split('\n'); key=None; gen={}
        for x in lines:
            if x.strip() in GEN_LABELS: key=x.strip(); gen.setdefault(key,[]); continue
            if key: gen[key].append(x)
        for k,v in gen.items():
            s='\n'.join(v)
            if k in('Notes','Internal Comments'):
                s=re.sub(r'\n?:\s*\[\n?',' [',s); s=re.sub(r'\n?\]\n?','] ',s)
            gen[k]=s.strip()
        r['gen']=gen
    out.append(r)
json.dump(out,open('tests.json','w'))
print(len(out))
import collections
print(collections.Counter(len(x.get('spec',[])) for x in out))
print(sum('obsolete' in x for x in out),'obsolete')
