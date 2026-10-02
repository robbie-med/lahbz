import json,re
T=json.load(open('../tests.json')); N=json.load(open('../national.json'))
bynum={}
for x in T:
    if x['num'] not in bynum or ('obsolete' in bynum[x['num']] and 'obsolete' not in x): bynum[x['num']]=x
cand=json.load(open('cand.json'))
# Cerner name -> ([rml test nums], [national codes], note, confident?)
M={
'Serum Bactericidal Test':([],[],'Not in RML catalog or Labcorp national menu. Ask lab.',False),
'Serum Drug Alcohol Screen':(['4300050'],['700845'],'Best guess. RML "Drug Screen, Blood"; Labcorp national serum drug screen is 700845.',False),
'Serum HCG':(['3601425','3601450'],['004416'],'Quantitative vs qualitative is unclear from the name; both RML versions listed.',False),
'Serum HCG Level':(['3601425'],['004416'],'',True),
'Quantitative serum HCG':(['3601425'],['004416'],'',True),
'Serum Osmolality':(['2004300'],[],'',True),'Osmolality Serum':(['2004300'],[],'',True),
'Serum Protein Electrophoresis Analyzer':(['5004425'],[],'RML "Analyzer" = RML-only reflex build, like Thyroid Analyzer. May no longer be orderable.',True),
'Electrophoresis Serum (No Reflex)':(['5002125'],[],'',True),
'AFP, Serum, Open Spina Bifida':(['5194838'],[],'',True),
'Aldosterone Serum':(['3800325'],[],'',True),'Aluminum Serum':(['3800750'],[],'',True),
'Biotinidase Serum':(['5613879'],[],'',True),'Carnitine Serum':(['3613200'],[],'',True),
'Ciproflaxacin Serum Level':([],[],'Not in RML catalog or Labcorp national public menu.',False),
'Ciprofloxacin Quant Serum Level':([],[],'Not in RML catalog or Labcorp national public menu.',False),
'Gold Serum Level':(['3658375'],[],'',True),'Imipramine Serum':(['4302400'],[],'',True),
'Immunofix Serum':(['3960845'],['001685'],'',True),'Immunofixation, Serum (M20)':(['3960845'],['001685'],'',True),
'.Immunofixation Reflex, Serum 001496':([],['001496'],'Labcorp national code 001496 (not on Labcorp public menu).',True),
'Insulin Serum':(['2023075'],[],'',True),
'Lysozyme Serum':(['3611450'],[],'',True),'Muramidase Serum':(['3611450'],[],'Same test as Lysozyme.',True),
'Microglobulin Serum':(['2005800'],[],'',True),'Beta 2 Microglobulin Serum':(['2005800'],[],'',True),
'Myoglobin Serum':(['2004240'],[],'',True),'Nicotine Serum Quantitative':(['4312555'],[],'',True),
'Potassium Serum/Plasma':(['2004600'],[],'',True),
'Preg Serum Qual':(['3601450'],['004556'],'',True),'HCG Qualitative Serum':(['3601450'],['004556'],'',True),'Beta HCG Qual Serum Preg Test':(['3601450'],['004556'],'',True),
'Salicylate-Serum Level':(['4004550'],[],'',True),'Thiocyante Serum Level':(['5613595'],[],'',True),'Zinc Serum':(['3603800'],[],'',True),
'Alkaline Phosphatase, Serum':(['2000250'],[],'',True),
'Bordetella Pertussis Serum Antibody':(['6908547','5521005'],[],'Two RML versions: IgG only, or IgA+IgG w/ reflex.',False),
'C3 Complement Serum':(['5000300'],[],'',True),'C4 Complement Serum':(['5000350'],[],'',True),'C5 Complement Serum':(['5000370'],[],'',True),'C7 Complement Serum':(['5000575'],[],'',True),
'Cholesterol Total Serum':(['2001850'],[],'',True),'Cortisol Free Serum':(['4503500'],[],'',True),
'Cryptococcus Antigen Serum Scr':(['6002175'],[],'',True),'IgA Subclasses Serum':(['6907825'],[],'',True),
'Mycophenolic Level Serum':(['3630000'],[],'',True),'Pregabalin (Lyrica) Serum':(['6906325'],[],'',True),
'.Cryptococcus Ag Titer, Serum 183036':(['6002300'],['183036'],'Labcorp national code 183036 (not on public menu). RML equivalent was Cryptococcus Antigen Titer.',True),
'.DPPX Antibody, Titer, Serum 505282':([],['505282'],'Labcorp national code only.',True),
'1,5 Anhydroglucitol Quant, Serum/Plasma':(['2907676'],[],'',True),
'Enterovirus DNA PCR Serum':(['5586525'],['138636'],'RML catalog lists this test under CSF; check specimen.',False),
'Luteinizing Hormone (LH) Serum':(['3601750'],[],'',True),
'.Anti-LGI1 Antibody Titer,Serum 505357':([],['505357'],'Labcorp national code only.',True),
'.Anti-MOG Antibody Titer, Serum 505312':([],['505312'],'Labcorp national code only.',True),
'.hCG,Beta Subunit,Qnt,Serum 004613':(['5196957'],['004613'],'Labcorp national code 004613 (not on public menu).',False),
'Fatty Acid Profile Essential Serum':(['6907817'],[],'',True),'Oligoclonal Bands CSF and Serum':(['0804040'],[],'',True),
'.Reflex Anti-LGI1 Ab Titer,Serum':([],[],'Reflex component of the LGI1 titer; not ordered by itself.',False),
'HSV 1/2 PCR Qualitative Plasma/Serum':(['5586635'],[],'',True),
'Anti-Leucine-Rich, Glioma-Inactivated Protein 1 (LGI1), Serum':(['5194491'],[],'',True),
'.APCA+IF Ab 010423':(['5666675','5590600'],['006486','010413'],'Labcorp national code 010423 (not on public menu). Looks like parietal cell Ab + intrinsic factor Ab combined.',False),
'CARDIO AB':(['5564450'],['161802'],'Cardiolipin; IgG+IgM is the likely build.',False),
'Centrom AB':(['5508597'],['164814'],'',True),
'Citruln AB':(['5570175'],[],'Likely CCP (citrullinated peptide) antibody.',False),
'Coccidioides Ab':(['6907491'],['164798'],'',False),
'Cysticercosis Ab IgG CSF':(['6906665'],[],'',True),
'Cytoker AB':([],[],'Not found (cytokeratin?). Ask lab.',False),
'EBV Ab Panel':([],['240610'],'No RML panel; Labcorp national "EBV Antibody Profile" 240610.',False),
'GRANMB AB':([],[],'Not found. Ask lab.',False),
'Histoplasma Ab':(['5522700'],[],'',True),
'HRANA AB':([],[],'Not found. Ask lab.',False),
'JCV Ab Stratify with Index and Reflex to Inhibition Assay':(['6006452'],[],'',True),
'LKM AB':(['3606775'],[],'',True),'LIV KID AB':(['3606775'],[],'',True),
'Mitoch AB Titer':(['5567825'],[],'',True),'Myeloperoxidase Ab':(['5551850'],[],'',True),
'NEURONL AB':(['5194477'],['505240'],'Likely the Hu/Ri/Yo (neuronal nuclear) antibody profile.',False),
'Neuronal Nuclear Ab Hu Ri Yo IgG':(['5194477'],['505240'],'',True),
'PHOS AB':(['5503950'],[],'Likely phosphatidylserine antibodies.',False),
'PHOSLIP AB':(['5575075'],['164535'],'Likely antiphospholipid antibody panel.',False),
'Pneumococcal Ab Panel PCV15, 15-Seroty':(['5197336'],[],'',True),'Pneumococcal Ab Panel PCV20, 20-Seroty':(['5197339'],[],'',True),
'Pneumococcal Ab Panel PCV21, 21-Seroty':(['5197337'],[],'',True),'Pneumococcal Ab Panel PPSV23, 23-Seroty':(['5197338'],[],'',True),
'Rubella Ab IgG IgM':(['5518903'],[],'',True),'Schistosoma Ab IgG':(['5566775'],[],'',True),
'Sclero AB':(['5564053'],[],'Likely Scl-70.',False),'Smith Ab':(['5510450'],[],'',True),
'SPERM AB':([],[],'Not in RML catalog or Labcorp national public menu.',False),
'Sporothrix Ab':(['6907749'],[],'',True),
'SPRUE AB':(['5537600'],['164010'],'Likely celiac antibodies.',False),
'Toxo Ab IgG IgM':(['5505626'],[],'',True),
'ABG':(['2000500'],[],'Arterial blood gas; hospital/ED only.',False),'ABG w/Base Excess':(['2000500'],[],'Arterial blood gas; hospital/ED only.',False),
'Absolute Eosinophil Count':(['0100050'],[],'',True),
'.Coccidioides immitis Ab, by ID 830946':([],['830946'],'Labcorp national code only.',True),
'Blastomyces dermatitidis Ab w/ Reflex':(['5501505'],[],'',True),
'BOR PER AB':(['5521005'],[],'Likely the IgA+IgG w/ reflex version.',False),
'Doublestranded DNA AB':(['5572000'],[],'',True),'EBV VCA Ab IgG IgM':(['5580926'],[],'',True),
'GM1 Ganglioside AB':(['5565950'],[],'',True),
'Hepatitis A Ab IgG':(['6906969'],[],'',True),'Hepatitis A Ab IgM':(['3603500'],[],'',True),'Hepatitis C Ab':(['5590850'],[],'',True),
'Hepatitis E Ab IgG IgM':(['3603480'],[],'',True),'Hepatitis E Ab IgM':(['3606276'],[],'',True),
'HIV Ag/Ab Screen':(['3609705'],[],'',True),
'MUR TYP AB':(['3805300'],['016188'],'',True),
'Proteinase 3 Ab':(['5551900'],[],'',True),'Streptolysin O AB Titer':(['5509550'],[],'',True),
'Thyroid Stimulating Ab':(['3603200','4502225'],['140749','010314'],'Ambiguous: could be TSI (stimulating immunoglobulin) or TRAb (TSH receptor Ab). Different tests.',False),
'Toxocara IgG Ab':(['5510025'],[],'',True),'West Nile Ab':(['3609525'],[],'',True),
'.Blastomyces Abs, Qn, DID':([],['164293'],'',True),
'ACHR ABS':(['5500010'],['085902'],'Likely AChR binding antibody (blocking and modulating are separate tests).',False),
'5-Nucleotidase':(['2007150'],[],'',True),
'COVID-19 IgG, Nucleocapsid':(['6901550'],[],'Same test as "SARS-CoV-2 IgG, Nucleocapsid".',True),
'Nuts Allergy Panel IgE':(['5616500'],[],'Likely same as "A NUTS PNL".',False),
'NuSwab VG Plus+Mycopl+Genita':(['5195364'],[],'Includes a genital culture: needs orange Aptima swab AND an eSwab.',True),
'Trich vag by NAA':([],['188052'],'Not in RML catalog. Labcorp national 188052.',True),
'Vaginal Profile From Swab':(['2915445'],[],'',False),
'Vaginosis Profile + STD Swab':(['6987005'],[],'Old RML MySwab test.',True),
'Vaginosis Profile + Trichomonas Swab':(['6987004'],[],'Old RML MySwab test.',True),
'Vaginosis Profile MySwab':(['6987003'],[],'Old RML MySwab test.',True),
'Vaginosis Profile Saline Wet Mount':(['2915425'],[],'',False),
'Bacterial Vaginosis Swab':(['6987001'],[],'Old RML TMA test.',True),
'Candida Vaginitis Swab':(['6987000'],[],'Old RML TMA test.',True),
'MySwab Vaginosis Profile':(['6987003'],[],'',True),'MySwab Vaginosis Profile + STD':(['6987005'],[],'',True),'MySwab Vaginosis Profile + Trichomonas':(['6987004'],[],'',True),
'HPV, Self-Collect, Vaginal Swab':(['5195627'],[],'',True),
'Ferritin Level (FERRITIN)':(['4500800'],[],'',True),
'EBV EA Ab IgG':(['5580901'],[],'',True),
}
R='REFLEX ADD-ON, do not order. '
M.update({
'.Immunofixation Reflex, Serum 001496':([],['123026'],R+'Labcorp adds it from the parent listed (serum protein electrophoresis with reflex to IFE).',True),
'.Cryptococcus Ag Titer, Serum 183036':([],['183025'],R+'Order Cryptococcus Antigen; the titer is added if positive.',True),
'.DPPX Antibody, Titer, Serum 505282':([],['164126','505413','505490'],R+'Part of the neuro antibody profiles listed.',True),
'.Anti-LGI1 Antibody Titer,Serum 505357':([],['505355'],R+'Order Anti-LGI1, Serum.',True),
'.Reflex Anti-LGI1 Ab Titer,Serum':([],['505355'],R+'Order Anti-LGI1, Serum.',True),
'.Anti-MOG Antibody Titer, Serum 505312':([],['505310'],R+'Order Anti-MOG, Serum.',True),
'.APCA+IF Ab 010423':([],['141503'],R+'Comes from the Vitamin B12 Deficiency Cascade.',True),
'.hCG,Beta Subunit,Qnt,Serum 004613':([],[],'Leading "." usually means a reflex add-on; parent not found on Labcorp public menu. Do not order directly; ask lab.',False),
'.Coccidioides immitis Ab, by ID 830946':(['6907491'],[],'Probably a reflex add-on of the Coccidioides Ab Reflexive Panel (830945). Do not order directly.',False),
'.Blastomyces Abs, Qn, DID':(['5501505'],['164293'],'Probably the reflex step of "Blastomyces dermatitidis Ab w/ Reflex". Order that instead.',False),
'.Thyroglobulin by LCMS 070121':([],['042045'],R+'Order Thyroglobulin Antibody and Thyroglobulin (042045).',True),
'.Arsenic Toxic Species Ur 007086':([],['007045','250281'],R+'Part of the urine arsenic / heavy metals profiles listed.',True),
'.PSEUDOEPHEDRINE CONFIRMATION 764632':([],[],'Leading "." usually means a reflex add-on (drug confirmation). Parent not found on Labcorp public menu.',False),
'.BARBITURATES,MS,WB/SP RFX 700813':([],['700845'],R+'Confirmation step of the serum drug screen listed. All ".<DRUG>,MS,WB/SP RFX 7008xx" entries work the same way.',True),
'.THC,MS,WB/SP RFX 700817':([],['700845'],R+'Confirmation step of the serum drug screen listed.',True),
})

import glob,os,re as _re
_pages={os.path.basename(f)[:-5]:open(f).read() for f in glob.glob('../lcn/*.html')}
def parents(code):
    return [k for k,h in _pages.items() if k!=code and _re.search(r'Reflex \d+\s*(?:<[^>]+>\s*)*'+code, h)] or [k for k,h in _pages.items() if k!=code and code in h]
for c in [l.strip() for l in open('cerner.txt') if l.strip()]:
    m=_re.match(r'^\..*?(\d{6})$',c)
    if m and c not in M:
        p=parents(m.group(1))[:4]
        M[c]=([],p,R+('Labcorp adds it automatically from the parent test listed.' if p else 'Parent test not found on Labcorp public menu.'),bool(p))
    pm=_re.match(r'^(\d{5}) (.*) POC$',c)
    if pm and c not in M:
        M[c]=([],[],'Point-of-care (bedside) test, not sent to Labcorp. The 5-digit number is its billing (CPT) code.',True)
names=[l.strip() for l in open('cerner.txt') if l.strip()]
rows_diff=[];rows_same=[];missing=[]
def natname(c): return N[c]['name'] if c in N else None
for c in names:
    r=cand[c]
    if c in M: nums,nats,note,conf=M[c]
    elif r['exact']:
        nums=[r['exact'][0][2]];nats=[];note='';conf=True
    else: missing.append(c);continue
    rml=[];natl=[];obs=False
    for n in nums:
        x=bynum.get(n)
        if not x: rml.append(f'?{n}');continue
        o=' **(RML catalog marks discontinued)**' if 'obsolete' in x else ''
        obs|=bool(o)
        rml.append(f"{x['name']} — order code `{x['order']}`, #{x['num']}{o}")
        pc=x.get('gen',{}).get('Performing Labcorp Test Code')
        if pc and pc not in nats: nats=nats+[pc]
    pcs={bynum[n].get('gen',{}).get('Performing Labcorp Test Code') for n in nums if n in bynum}
    for k in nats:
        nm=natname(k); tag='' if (k in pcs or not nums or any(pcs)) else ' — closest national equivalent; RML ran this in-house'
        natl.append((f"{nm} ({k})" if nm else f"{k} (not on Labcorp's public menu)")+tag)
    exact = bool(r['exact']) and len(nums)==1 and r['exact'][0][2]==nums[0]
    row=(c,'<br>'.join(rml) or '—','<br>'.join(natl) or '—',('' if conf else '⚠ ')+note)
    (rows_same if exact else rows_diff).append(row)
print('missing',missing)
def table(rows):
    out=['| Cerner name | Old RML / Labcorp Oklahoma name | Labcorp national name (code) | Notes |','|---|---|---|---|']
    for r in rows: out.append('| '+' | '.join(x.replace('|','/') for x in r)+' |')
    return '\n'.join(out)
md=f"""# Cerner lab names → Labcorp names

Built {__import__('datetime').date.today()} from the Cerner search screenshots. Sources: the old RML / Labcorp Oklahoma test catalog (rml.labcatalog.net, saved 2026-10-02) and Labcorp's national test menu (labcorp.com/tests).

- **Old RML / Labcorp Oklahoma name**: what Cerner's "Reference Information" link opens. The short code in backticks (e.g. `TSH REC AB`) is sometimes the exact Cerner display name. Cerner only matches text in the display name, so search with words, not test numbers.
- **Labcorp national name (code)**: the test Labcorp actually runs, for tests sent to Labcorp national. A 6-digit code in the Cerner name (e.g. ".Immunofixation Reflex, Serum 001496") is one of these.
- **Names ending in "POC" with a 5-digit number** (e.g. "80061 Lipid Panel POC") are point-of-care (bedside) tests, not Labcorp orders; the number is the billing code.
- **Names starting with "." are reflex add-ons.** Labcorp adds them automatically when the parent test calls for it. Don't order them; order the parent listed in that row. That's also why these are the only Cerner names with numbers in them.
- **⚠** = my best guess from the abbreviation. Confirm before relying on it.
- "RML catalog marks discontinued" means RML retired it before the switch. An RML test still listed as active may still not be orderable now (e.g. Thyroid Analyzer).

**Thyroid Analyzer** (RML `THYROID AN`, #4502350, TSH reflexing to free T4/free T3) is an RML-only build and no longer orderable. Closest Labcorp national test: **Thyroid Cascade Profile (330015)**, TSH reflexing to free T4, free T3 and/or TPO antibodies. Other options: TSH and Free T4 (224576); TSH alone (004259).

## Cerner names that differ from the catalog ({len(rows_diff)})

{table(rows_diff)}

## Cerner names that match the catalog exactly ({len(rows_same)})

{table(rows_same)}
"""
open('cerner_to_labcorp.md','w').write(md)
print(len(rows_diff),len(rows_same))
