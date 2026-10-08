"""Build tool/data.json for the lab-order finder page.

Inputs (all in the repo):
  data/rml_labcorp_oklahoma_catalog_2026-10-02.json  local (former RML) catalog
  data/labcorp_national_menu_2026-10-02.json         Labcorp national test menu
  cerner_to_labcorp.md                               Cerner names seen in screenshots

Run from the repo root:  python3 -I scripts/build_tool_data.py
"""
import json
import re
from collections import Counter

LOCAL = json.load(open("data/rml_labcorp_oklahoma_catalog_2026-10-02.json"))
NAT = json.load(open("data/labcorp_national_menu_2026-10-02.json"))

# ---------------------------------------------------------------- clinic facts
# The clinic's "labs that can not be drawn here" list (staff email, 2026-09-24).
# Each item: (label as written, regex over test names, note on how it was read).
CLINIC_NO = [
    ("Lactic Acid / Lactate", r"^lact(ate|ic acid)\b(?!.*(dehydrogenase|spinal|csf|fluid))", ""),
    ("Vit D 1-25-Dihydroxy", r"1,25-dihydroxy|1-25-doh|1,25 dihydroxy", ""),
    ("Levetiracetam level", r"levetiracetam", ""),
    ("Parathyroid Hormone-Related Protein", r"pth-related|parathyroid hormone-related", ""),
    ("Ammonia", r"^ammonia", ""),
    ("Calcium Ionized", r"calcium,? ionized|ionized calcium", ""),
    ("Lupus", r"lupus anticoagulant", "Clinic list says only \"Lupus\"; read as lupus anticoagulant. Confirm."),
    ("Aluminum", r"^aluminum(?!.*urine)", ""),
    ("C-Peptide", r"^(?!.*urine)(insulin and )?c-peptide", ""),
    ("Vitamin K1", r"vitamin k", ""),
    ("Cold Agglutinin Antibody", r"cold agglutinin", ""),
    ("Nickel", r"^nickel(?!.*urine)", ""),
    ("D-Dimer", r"d-dimer", ""),
    ("Copper", r"^copper(?!.*(urine|liver))", ""),
    ("DHEA", r"^(?!.*sulfate)(?!.*dhea[- ]?s\b).*(\bdhea\b|dehydroepiandrosterone)", "Clinic list says \"DHEA\"; DHEA-sulfate not included. Confirm."),
    ("Protein C Antigen", r"protein c antigen", ""),
    ("Protein S Antigen", r"protein s antigen", ""),
    ("Lead Levels", r"^(?!.*urine)lead\b", ""),
    ("Lipid group w/ NMR particle count", r"\bnmr\b", ""),
    ("Magnesium, RBC", r"magnesium, rbc|magnesium,? red", ""),
    ("ACTH level", r"^acth \(adrenocorticotropic hormone\), plasma|^adrenocorticotropic hormone \(acth\), plasma$", ""),
    ("Insulin Level (fasting)", r"^insulin(, serum)?$", "Patient must be fasting."),
    ("3 hour Glucose", r"glucose tolerance \(3 hour", "Morning only; nothing but water for 8+ hours."),
    ("Zinc level", r"^zinc(, serum| level|$)", ""),
    ("Vitamin B1 (Thiamine)", r"thiamine|vitamin b1\b", ""),
    ("Abnormal PT/PTT Analyzer", r"abnormal pt/ptt", ""),
    ("Vitamin B6", r"vitamin b6|pyridox", ""),
]

# What the clinic can do with a specimen. None = not answered yet (lab tech to confirm).
CLINIC_CAN = {"centrifuge": None, "freezer": None, "ice": None, "warm": None, "courier_minutes": None}

# Orders the clinic has reported it cannot use, and what to use instead.
NOT_ORDERABLE = {
    "L4502350": ("Reported not orderable in Cerner.", ["N330015", "L4501925", "L4502550"]),
    "L6987003": ("MySwab can no longer be ordered.", ["L5195317"]),
    "L6987004": ("MySwab can no longer be ordered.", ["L5195314"]),
    "L6987005": ("MySwab can no longer be ordered.", ["L5195310"]),
    "L6987006": ("MySwab can no longer be ordered.", ["N188070"]),
}

# Extra notes attached to specific tests.
NOTES = {
    "L5195364": "Two specimens: orange-label Aptima vaginal swab AND a bacterial culture swab (eSwab). Includes a routine genital culture.",
    "L5195362": "Despite the \"+\" in the name, this one does NOT include chlamydia or gonorrhea.",
    "N330015": "Its TPO reflex shows in Cerner as \".Thyroid Peroxidase (TPO) Ab 330018\", but the parent order wasn't found by name. Order as Miscellaneous Test 330015.",
}

# ------------------------------------------------------------ plain-language terms
# term -> test keys (L = local catalog test number, N = Labcorp national code).
ALIASES = {
    "cbc|blood count|hemoglobin|hgb|platelets|wbc": ["L0101301", "L0101425"],
    "cmp|comprehensive metabolic|chem 14": ["L2028075"],
    "bmp|basic metabolic|chem 8|electrolytes": ["L2028100"],
    "a1c|hba1c|hemoglobin a1c|glycated": ["L5002400"],
    "lipid|lipids|cholesterol|ldl|hdl|triglycerides": ["L2019100", "L2012900"],
    "tsh|thyroid": ["L4501925", "N330015", "L4502550"],
    "free t4|ft4|t4 free": ["L4502550"],
    "free t3|ft3": ["L3606325"],
    "tpo|thyroid peroxidase|hashimoto": ["L3612430", "L3612580"],
    "trab|tsi|graves|thyroid stimulating antibody": ["L4502225", "L3603200"],
    "thyroid cascade|tsh reflex|tsh with reflex": ["N330015"],
    "ua|urinalysis|urine dip": ["L1003000", "L1002500"],
    "urine culture|uti|ucx": ["L6002002"],
    "ferritin": ["L4500800"],
    "iron|iron studies|tibc|transferrin saturation|tsat": ["L4501000", "L4500800"],
    "b12|vitamin b12|cobalamin": ["L4500900", "L5194465"],
    "folate|folic acid": ["L4500950"],
    "vitamin d|vit d|25-hydroxy|25 oh": ["L2023925"],
    "retic|reticulocyte": ["L0111800"],
    "lft|liver|hepatic function|liver panel": ["L2006125", "L2002100"],
    "ggt": ["L2002100"],
    "hepatitis|hep panel": ["L3603500", "L3603000", "L5553650", "L5590850"],
    "hep a|hepatitis a": ["L3603500"],
    "hep b|hepatitis b|hbsag": ["L3603000", "L3611850", "L3603253"],
    "hep b immunity|hepatitis b antibody|hbsab": ["L3611850"],
    "hep c|hepatitis c|hcv": ["L5590850"],
    "hiv": ["L3609705"],
    "syphilis|rpr|vdrl|treponemal": ["L5500605", "L5197168"],
    "gc|ct|chlamydia|gonorrhea|std|sti": ["N183160", "L6910127", "L6910129"],
    "trich|trichomonas": ["N188052", "L5195314"],
    "bv|bacterial vaginosis|vaginitis|vaginosis|yeast|candida|discharge": ["L5195314", "L5195310", "L5195317", "L5195322"],
    "nuswab": ["L5195314", "L5195310", "L5195317", "L5195364", "L5195362"],
    "myswab": ["L5195317", "L5195314", "L5195310"],
    "mycoplasma genitalium|m gen|mgen": ["L5195327", "L5195311"],
    "hsv|herpes": ["N188056", "L5586635"],
    "hpv|pap": ["L6910105", "L5195627"],
    "psa|prostate": ["L2012225", "L2001575"],
    "hcg|pregnancy|beta hcg|upt": ["L1001120", "L3601450", "L3601425"],
    "magnesium|mag": ["L2004100"],
    "phosphorus|phos": ["L2004400"],
    "calcium": ["L2001150", "L2020125"],
    "ionized calcium": ["L2020125"],
    "pth|parathyroid": ["L5577075"],
    "uric acid|gout": ["L2005750"],
    "esr|sed rate|sedimentation": ["L0107000"],
    "crp|c-reactive": ["L2008425"],
    "hs-crp|hscrp|cardio crp": ["L2023150"],
    "ana|antinuclear": ["L5500050"],
    "rf|rheumatoid factor": ["L5572775"],
    "ccp|anti-ccp|citrullinated": ["L5570175"],
    "dsdna|ds dna|double stranded": ["L5572000"],
    "complement|c3 c4": ["L5002000"],
    "hla b27|hla-b27": ["L5580000"],
    "pt|inr|protime|coumadin|warfarin": ["L1500350"],
    "ptt|aptt": ["L1500050"],
    "d-dimer|ddimer": ["L1501625"],
    "fibrinogen": ["L1501600"],
    "microalbumin|uacr|albumin creatinine|urine albumin": ["L2022200"],
    "upcr|protein creatinine|urine protein": ["L3010000"],
    "strep|strep throat": ["L6001700", "L6000250"],
    "flu|influenza": ["L5565578"],
    "covid|sars-cov-2|coronavirus": ["L6907557"],
    "mono|monospot|ebv": ["L5504950"],
    "lyme": ["L5570801"],
    "h pylori|pylori": ["L5579675", "L3502325"],
    "c diff|c. diff|clostridium difficile": ["L6001200"],
    "o&p|ova and parasites|parasites": ["L5195166"],
    "stool culture|diarrhea": ["L6001075", "L6001200"],
    "fit|fobt|occult blood|ifobt": ["L3510285"],
    "tb|quantiferon|tb gold|tuberculosis": ["L5587326"],
    "cortisol": ["L4400350"],
    "acth": ["L2022775"],
    "aldosterone|renin|aldo renin": ["L5194931"],
    "prolactin": ["L3602400"],
    "igf|igf-1|somatomedin": ["L2022625"],
    "testosterone": ["L3602650", "L3602545"],
    "estradiol|estrogen": ["L2006475"],
    "fsh": ["L3601200"],
    "lh": ["L3601750"],
    "amh|anti-mullerian|ovarian reserve": ["L5570915"],
    "dhea-s|dheas|dhea sulfate": ["L2022725"],
    "lipase|pancreatitis": ["L2004000"],
    "amylase": ["L2000350"],
    "ck|cpk|creatine kinase": ["L2001950"],
    "bnp|nt-probnp|probnp|heart failure": ["L2015175", "L2015177"],
    "lp(a)|lipoprotein a|lpa": ["L2020875"],
    "apob|apolipoprotein b": ["L2015050"],
    "drug screen|uds|tox screen|urine drug": ["L4313625"],
    "lithium": ["L4003050"],
    "valproic|depakote|valproate": ["L4005800"],
    "digoxin": ["L4500550"],
    "keppra|levetiracetam": ["L3658525"],
    "lead": ["L6906339", "L6906338"],
    "thiamine|vitamin b1|b1": ["L3603380"],
    "vitamin b6|b6": ["L3603660"],
    "zinc": ["L3603800"],
    "copper": ["L3605025"],
    "g6pd": ["L2003750"],
    "sickle|hemoglobin electrophoresis|thalassemia": ["L5000750"],
    "celiac|ttg|gluten": ["L5537600", "L5537525"],
    "semen|sperm|vasectomy": ["L2901101", "L2929026"],
    "glucose|fasting glucose|blood sugar": ["L2002150", "L2002240"],
    "gtt|glucose tolerance|gestational diabetes": ["L2002250", "L2006700", "L2023550"],
    "ammonia": ["L2000300"],
    "lactate|lactic acid": ["L2003800"],
    "cystatin|cystatin c": ["L3623775"],
    "insulin": ["L2023075"],
    "lupus anticoagulant": ["L1506550"],
    "protein c|protein s|thrombophilia": ["L1503250", "L1503400"],
    "nmr|lipoprotein particle": ["L5194452", "L5520007"],
}

# Browse tree: system -> [(condition, [alias terms])]. Lists common orders; not clinical guidance.
TREE = [
    ("Routine / annual", [
        ("Basic labs", ["cbc", "cmp", "lipid", "a1c", "tsh", "ua"]),
        ("Men 50+", ["psa"]),
    ]),
    ("Diabetes & metabolic", [
        ("Diabetes screen / follow-up", ["a1c", "glucose", "cmp", "lipid", "microalbumin"]),
        ("Gestational diabetes", ["gtt"]),
        ("Insulin resistance", ["insulin", "glucose"]),
    ]),
    ("Thyroid", [
        ("Screen / follow-up", ["tsh", "thyroid cascade", "free t4"]),
        ("Hypothyroid / Hashimoto", ["tsh", "free t4", "tpo"]),
        ("Hyperthyroid / Graves", ["tsh", "free t4", "free t3", "trab"]),
    ]),
    ("Blood & anemia", [
        ("Anemia workup", ["cbc", "retic", "ferritin", "iron", "b12", "folate"]),
        ("Hemoglobinopathy", ["sickle", "g6pd"]),
    ]),
    ("Liver & GI", [
        ("Liver tests", ["lft", "ggt", "pt"]),
        ("Hepatitis", ["hep a", "hep b", "hep c"]),
        ("Pancreas", ["lipase", "amylase"]),
        ("Diarrhea / stool", ["stool culture", "c diff", "o&p", "h pylori"]),
        ("Colon cancer screen", ["fit"]),
        ("Celiac", ["celiac"]),
    ]),
    ("Kidney & electrolytes", [
        ("Kidney function", ["bmp", "cystatin", "ua", "microalbumin", "upcr"]),
        ("Minerals / bone", ["calcium", "ionized calcium", "phosphorus", "magnesium", "pth", "vitamin d"]),
    ]),
    ("Heart & lipids", [
        ("Lipids / risk", ["lipid", "lp(a)", "apob", "hs-crp"]),
        ("Heart failure", ["bnp", "bmp"]),
        ("Muscle", ["ck"]),
    ]),
    ("Rheumatology & inflammation", [
        ("Inflammation", ["esr", "crp"]),
        ("Rheumatoid arthritis", ["rf", "ccp"]),
        ("Lupus / connective tissue", ["ana", "dsdna", "complement"]),
        ("Gout", ["uric acid"]),
        ("Spondyloarthritis", ["hla b27"]),
    ]),
    ("Women's health", [
        ("Pregnancy", ["hcg"]),
        ("Vaginitis / discharge", ["nuswab"]),
        ("Cervical screening", ["hpv"]),
        ("Fertility / menstrual", ["fsh", "lh", "estradiol", "prolactin", "amh", "tsh"]),
        ("PCOS / androgens", ["testosterone", "dhea-s"]),
    ]),
    ("STI", [
        ("STI screen", ["gc", "trich", "hiv", "syphilis", "hep c", "hep b"]),
        ("Herpes", ["hsv"]),
        ("M. genitalium", ["mycoplasma genitalium"]),
    ]),
    ("Infection", [
        ("Respiratory", ["flu", "covid", "strep"]),
        ("Mono", ["mono"]),
        ("Lyme", ["lyme"]),
        ("TB screen", ["tb"]),
        ("Urine infection", ["ua", "urine culture"]),
    ]),
    ("Endocrine & hormones", [
        ("Adrenal", ["cortisol", "acth", "aldosterone", "dhea-s"]),
        ("Pituitary", ["prolactin", "igf", "tsh"]),
        ("Male hypogonadism", ["testosterone", "lh", "fsh"]),
    ]),
    ("Coagulation", [
        ("Bleeding / anticoagulation", ["pt", "ptt", "fibrinogen"]),
        ("Clot / thrombophilia", ["d-dimer", "lupus anticoagulant", "protein c"]),
    ]),
    ("Nutrition & vitamins", [
        ("Vitamins", ["b12", "folate", "vitamin d", "thiamine", "vitamin b6"]),
        ("Trace elements", ["zinc", "copper"]),
    ]),
    ("Drug levels & toxicology", [
        ("Drug screen", ["drug screen"]),
        ("Drug levels", ["lithium", "valproic", "digoxin", "keppra"]),
        ("Lead", ["lead"]),
    ]),
    ("Men's health", [
        ("Prostate", ["psa"]),
        ("Semen analysis", ["semen"]),
    ]),
]


# ------------------------------------------------------------------- helpers
def clean(s, n=None):
    if not s:
        return ""
    s = s.replace(" ", " ")
    s = re.sub(r"[ \t]*\n[ \t]*", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s).strip()
    # national pages split inline words onto their own lines ("should | not | exercise")
    s = re.sub(r"\n(?=(not|or|and|frozen|Freeze|freeze|\d|°|,|\.|\)|\())", " ", s)
    if n and len(s) > n:
        s = s[: n].rsplit(" ", 1)[0] + "…"
    return s


def stab_table(s):
    """'Temperature | Period | Room temperature | 14 days | ...' -> 'Room temp 14 days; ...'."""
    if not s:
        return ""
    parts = [p.strip() for p in s.split("\n") if p.strip()]
    if parts[:2] == ["Temperature", "Period"]:
        parts = parts[2:]
        pairs = []
        for i in range(0, len(parts) - 1, 2):
            v = re.sub(r"\s*\(stability provided by[^)]*\)", "", parts[i + 1])
            pairs.append(f"{parts[i]}: {v}")
        return "; ".join(pairs)
    return clean(s, 300)


def minutes_from(text):
    """Shortest 'within N minutes/hours' processing window mentioned, in minutes."""
    best = None
    for m in re.finditer(r"within\s+(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|h)\b", text):
        v = float(m.group(1)) * (60 if m.group(2).startswith("h") else 1)
        best = v if best is None else min(best, v)
    if re.search(r"(centrifuge|separate|spin|freeze)\w*\s+immediately|immediately\s+(centrifuge|separate|spin|freeze)", text):
        best = 15 if best is None else min(best, 15)
    return int(best) if best is not None else None


def flags_for(spec_fields, handling_text, prep_text, stability_text=""):
    """Handling flags from specimen text. spec_fields excludes stability tables."""
    t = handling_text.lower()
    s = spec_fields.lower()
    f = {}
    if re.search(r"\bfrozen\b", s) or re.search(r"(^|\n|\.\s)freeze\b|freeze (immediately|within|plasma|serum|specimen|and)|transport frozen|ship frozen|maintain frozen", t):
        if not re.search(r"(do not|don't|never) freeze|frozen (specimens? )?(are |is )?(not acceptable|unacceptable)", t + " " + s) or re.search(r"\bfrozen\b", s):
            f["frozen"] = 1
    if re.search(r"\bon ice\b|\biced\b|ice bath|ice slurry|ice water|prechill|pre-chill|\bchilled\b", t + " " + s) and not re.search(r"do not (place on |put on )?ice", t):
        f["ice"] = 1
    if re.search(r"37\s*°?\s*c|37'c|body temp|keep warm|pre-?warm", t + " " + s):
        f["warm"] = 1
    if re.search(r"protect(ed)? from light|light[- ]protect|amber (tube|vial|container)", t + " " + s):
        f["light"] = 1
    if re.search(r"centrifug|\bspin\b|separate (the )?(serum|plasma)|remove (the )?(serum|plasma)", t):
        f["spin"] = 1
    mins = minutes_from(t)
    if re.search(r"room temperature:?\s*\|?\s*unstable", stability_text.lower()):
        mins = min(mins or 120, 120)
    if mins is not None and mins <= 240:
        f["mins"] = mins
    p = (prep_text + " " + handling_text).lower()
    if re.search(r"\bfast(ing|ed)?\b", p) and not re.search(r"fasting (is )?not (required|necessary)|no fasting|non-?fasting is acceptable", p):
        f["fast"] = 1
    if re.search(r"\b(\d{1,2})\s*(a\.?m\.?)\s*(and|to|-|–)\s*(\d{1,2})\s*(a\.?m\.?|p\.?m\.?|noon)|morning specimen|early morning|first morning", p):
        f["timed"] = 1
    if re.search(r"24[- ]hour urine|24-hour|24 hr urine|timed urine", s + " " + t):
        f["u24"] = 1
    if re.search(r"contact (labcorp|the laboratory|client services).{0,60}(tube|kit|container|supplies|supply)|supply department|special (collection )?(kit|tube|container)|trace element|royal blue|tan-top|metal-free", t + " " + s):
        f["kit"] = 1
    return f


def kind_of(spec):
    s = spec.lower()
    if re.search(r"swab|aptima|thinprep|pap", s):
        return "swab"
    if re.search(r"urine", s):
        return "urine"
    if re.search(r"stool|feces|fecal", s):
        return "stool"
    if re.search(r"csf|spinal|synovial|body fluid|amniotic|tissue|bone marrow|aspirate|biopsy|bal\b|bronch", s):
        return "other"
    if re.search(r"serum|plasma|blood|sst|edta|lavender|gray|red-top|gel", s):
        return "blood"
    return "other"


# ------------------------------------------------------------------- entries
entries = {}

nat_ok = {k: v for k, v in NAT.items() if re.fullmatch(r"\d{6}", k)}

# Local catalog: one entry per test number, active versions preferred.
local_by_num = {}
for a in LOCAL:
    if not a.get("num") or not a.get("gen"):
        continue
    cur = local_by_num.get(a["num"])
    if cur is None or ("obsolete" in cur and "obsolete" not in a):
        local_by_num[a["num"]] = a

twin_of_nat = {}  # national code -> local key when the local test is a send-out of it
for num, a in local_by_num.items():
    key = "L" + num
    if "obsolete" in a and key not in NOT_ORDERABLE:
        continue
    g = a.get("gen", {})
    pc = (g.get("Performing Labcorp Test Code") or "").strip()
    pc = pc if re.fullmatch(r"\d{6}", pc) else ""
    spec_rows = a.get("spec", [])
    pref = spec_rows[0] if spec_rows else []
    spec_txt = " / ".join(x for x in pref[1:] if x)
    alts = [" / ".join(x for x in r[1:] if x) for r in spec_rows[1:]]
    ins = a.get("ins", "") or ""
    ins_no_stab = re.sub(r"(?im)^.*stabilit.*$", "", ins)
    notes = g.get("Notes", "")
    e = {
        "k": key, "src": "L", "name": a["name"], "code": a.get("order") or "", "num": num,
        "nat": pc, "sec": g.get("Lab Section", ""),
        "spec": spec_txt, "alt": alts,
        "col": clean(ins, 1200), "tat": g.get("Expected TAT", ""), "cpt": g.get("CPT Code(s)", "").replace("\n", " "),
        "use": clean(g.get("Clinical Use", ""), 300),
        "inc": [c[0] for c in a.get("comp", [])][:20],
        "url": a.get("url", ""),
    }
    transport = (pref[-1] if pref else "")
    spec_for_flags = " ".join(pref[1:-1]) + " " + ("frozen" if re.fullmatch(r"(?i)frozen.*", transport) else "")
    if re.search(r"(?i)on ice", transport):
        spec_for_flags += " on ice"
    if re.search(r"37", transport):
        spec_for_flags += " 37'C"
    e["fl"] = flags_for(spec_for_flags, ins_no_stab + "\n" + notes, ins + "\n" + notes)
    if "obsolete" in a:
        e["obs"] = clean(a["obsolete"], 300)
    entries[key] = e
    if pc and pc in nat_ok:
        twin_of_nat[pc] = key

# National menu: merge into the local twin when there is one, else its own entry.
for code, v in nat_ok.items():
    spec = clean(v.get("Specimen", ""), 200).replace("\n", " ")
    cont = clean(v.get("Container", ""), 400)
    vol = clean(v.get("Volume", ""), 120).replace("\n", " ")
    col = clean(v.get("Collection Instructions", ""), 1200)
    stor = clean(v.get("Storage Instructions", ""), 300)
    stab = stab_table(v.get("Stability Requirements", ""))
    prep = clean(v.get("Patient Preparation", ""), 400)
    special = clean(v.get("Special Instructions", ""), 400)
    fl = flags_for(spec + " " + stor, col + "\n" + stor + "\n" + special, prep, v.get("Stability Requirements", ""))
    nat_spec = {
        "spec": spec, "vol": vol, "cont": cont, "col": col, "stor": stor, "stab": stab, "prep": prep,
        "tat": clean(v.get("Result Turnaround Time", "").split("\n")[0], 60),
        "fl": fl, "nurl": v.get("url", f"https://www.labcorp.com/tests/{code}"),
    }
    if code in twin_of_nat:
        e = entries[twin_of_nat[code]]
        e["n"] = nat_spec  # Labcorp's own specimen requirements for this send-out
        continue
    e = {"k": "N" + code, "src": "N", "name": v["name"], "code": "", "num": "", "nat": code, "sec": "Labcorp national",
         "use": clean(v.get("Use", ""), 300), "inc": [], "url": "", "fl": {}, "spec": "", "alt": [], "col": "", "tat": "", "cpt": ""}
    e["n"] = nat_spec
    entries["N" + code] = e

# Flags: the national requirements win for send-outs; local ones apply to in-house tests.
for e in entries.values():
    if "n" in e:
        merged = dict(e["fl"])
        merged.update(e["n"]["fl"])
        e["fl"] = merged

# ------------------------------------------------------- Cerner names (screenshots)
md = open("cerner_to_labcorp.md").read()
cerner = {}
for line in md.splitlines():
    if not line.startswith("| ") or line.startswith("| Cerner name") or line.startswith("|---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if len(cells) < 4:
        continue
    cname, local_cell, nat_cell, note = cells[:4]
    if "REFLEX ADD-ON" in note or "POC" in cname or note.startswith("⚠"):
        continue
    nums = re.findall(r"#(\d{7,8})", local_cell)
    nats = re.findall(r"\((\d{6})\)", nat_cell)
    if len(nums) == 1:
        cerner.setdefault("L" + nums[0], []).append(cname)
    elif not nums and len(nats) == 1:
        cerner.setdefault("N" + nats[0], []).append(cname)
for k, names in cerner.items():
    if k in entries:
        entries[k]["cer"] = sorted(set(names))
    elif k[0] == "N" and k[1:] in twin_of_nat:
        entries[twin_of_nat[k[1:]]].setdefault("cer", []).extend(names)

# ---------------------------------------------------------------- clinic list
hits = Counter()
for e in entries.values():
    for label, rx, note in CLINIC_NO:
        if re.search(rx, e["name"], re.I):
            e["no"] = label
            if note:
                e["non"] = note
            hits[label] += 1
            break

for k, (why, use) in NOT_ORDERABLE.items():
    if k in entries:
        entries[k]["dead"] = why
        entries[k]["use_instead"] = [u for u in use if u in entries]
for k, note in NOTES.items():
    if k in entries:
        entries[k]["note"] = note
for e in entries.values():
    if e["src"] == "L" and re.search(r"\banalyzer\b", e["name"], re.I) and "dead" not in e:
        e["warn"] = "RML \"Analyzer\" orders may be retired (Thyroid Analyzer was). If Cerner won't take it, order the individual tests."
    if e["src"] == "L" and re.search(r"\bTMA\b", e["name"]) and "dead" not in e:
        e["warn"] = "Old RML in-house TMA test, the same lab section as MySwab (which is no longer orderable). May be retired."

# ---------------------------------------------------------------- aliases & tree
alias_out = []
missing = []
for terms, keys in ALIASES.items():
    ks = []
    for k in keys:
        if k in entries:
            ks.append(k)
        elif k[0] == "N" and k[1:] in twin_of_nat:
            ks.append(twin_of_nat[k[1:]])
        else:
            missing.append((terms, k))
    alias_out.append([terms.split("|"), ks])
term_index = {t: i for i, (ts, _) in enumerate(alias_out) for t in ts}
tree_out = []
for system, conds in TREE:
    cs = []
    for cond, terms in conds:
        for t in terms:
            assert t in term_index, f"tree term not an alias: {t}"
        cs.append([cond, terms])
    tree_out.append([system, cs])

# ---------------------------------------------------------------- output
order = sorted(entries.values(), key=lambda e: (e["src"] != "L", e["name"].lower()))
for e in order:
    if not e["fl"]:
        del e["fl"]
    for f in ("alt", "inc", "url", "code", "num", "nat", "use", "col", "tat", "cpt", "spec"):
        if f in e and not e[f]:
            del e[f]
out = {
    "built": "2026-10-08",
    "sources": {
        "local": "RML / Labcorp Oklahoma test directory (rml.labcatalog.net), saved 2026-10-02",
        "national": "Labcorp national test menu (labcorp.com/tests), saved 2026-10-02",
        "clinic": "Clinic \"labs that can not be drawn here\" list, 2026-09-24",
    },
    "can": CLINIC_CAN,
    "no": [[l, n] for l, _, n in CLINIC_NO],
    "aliases": alias_out,
    "tree": tree_out,
    "tests": order,
}
import os
os.makedirs("tool", exist_ok=True)
json.dump(out, open("tool/data.json", "w"), separators=(",", ":"), ensure_ascii=False)

print("tests:", len(order), " local:", sum(e["src"] == "L" for e in order), " national-only:", sum(e["src"] == "N" for e in order))
print("merged send-outs:", len(twin_of_nat), " cerner-confirmed:", sum("cer" in e for e in order))
print("clinic list hits:", dict(hits))
print("clinic items with no match:", [l for l, _, _ in CLINIC_NO if not hits[l]])
print("alias keys missing:", missing)
print("size MB:", round(os.path.getsize("tool/data.json") / 1e6, 2))
c = Counter(f for e in order for f in e.get("fl", {}))
print("flag counts:", dict(c))
