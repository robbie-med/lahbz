import json,re
T=json.load(open('../tests.json'))
# dedupe by test number, prefer active
by={}
for x in T:
    k=x['num'] or str(x['id'])
    if k not in by or ('obsolete' in by[k] and 'obsolete' not in x): by[k]=x
T=list(by.values())
ABBR={'ab':'antibody','abs':'antibody','ag':'antigen','preg':'pregnancy','qual':'qualitative','quant':'quantitative','qnt':'quantitative','toxo':'toxoplasma','vzv':'varicella','ebv':'epstein','cmv':'cytomegalovirus','hcg':'hcg','lvl':'level','scr':'screen','myco':'mycoplasma','mycopla':'mycoplasma','chlam':'chlamydia','centrom':'centromere','citruln':'citrullinated','cytoker':'cytokeratin','granmb':'glomerular','mitoch':'mitochondrial','neuronl':'neuronal','phos':'phosphatidylserine','phoslip':'phospholipid','sclero':'scleroderma','thyro':'thyroid','neutro':'neutrophil','striat':'striated','echovi':'echovirus','cardio':'cardiolipin','hrana':'ana','lkm':'liver kidney microsomal','liv':'liver','kid':'kidney','sprue':'gliadin','int':'intrinsic','bl':'factor','mur':'murine','typ':'typhus','bor':'bordetella','per':'pertussis','chaff':'chaffeensis','achr':'acetylcholine','dna':'dna','doublestranded':'double','nontrep':'nontreponemal','eos':'eosinophil'}
def toks(s):
    s=s.lower().replace('/',' ')
    w=re.findall(r'[a-z0-9]+',s)
    out=set()
    for t in w:
        out.add(t)
        if t in ABBR: out.update(ABBR[t].split())
    return out-{'serum','level','the','and','with','w','of','by','test','plasma'}
def score(c,x):
    a=toks(c); b=toks(x['name']+' '+(x['order'] or '')+' '+' '.join(r[0] for r in x.get('comp',[])[:3]))
    if not a: return 0
    return len(a&b)/len(a) - 0.02*len(b)/10
names=[l.strip() for l in open('cerner.txt') if l.strip()]
res={}
for c in names:
    cu=c.upper()
    ex=[x for x in T if (x['order'] or '').upper()==cu or x['name'].upper()==cu]
    sc=sorted(T,key=lambda x:-score(c,x))[:5]
    res[c]={'exact':[(x['name'],x['order'],x['num'],'OBS' if 'obsolete' in x else '',x.get('gen',{}).get('Performing Labcorp Test Code','')) for x in ex],
            'cand':[(round(score(c,x),2),x['name'],x['order'],x['num'],'OBS' if 'obsolete' in x else '',x.get('gen',{}).get('Performing Labcorp Test Code','')) for x in sc]}
json.dump(res,open('cand.json','w'),indent=1)
for c,r in res.items():
    print('##',c)
    if r['exact']: print('  EXACT',r['exact'])
    else:
        for z in r['cand'][:4]: print('   ',z)
