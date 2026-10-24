import re, sys, glob, xml.etree.ElementTree as ET
doc = open(sys.argv[1]).read()
start = doc.index("## Element types and their properties")
sec = doc[start:]
props = {}
for m in re.finditer(r"^#### (\w+)\n(.*?)(?=^#### |\Z)", sec, re.S | re.M):
    props[m.group(1)] = set(re.findall(r"^\s*\* `(\w+)`", m.group(2), re.M))
props["sound"] = {"path"}
errs = 0
for fn in glob.glob(sys.argv[2] + "/layouts/*.xml") + [sys.argv[2] + "/navigationsounds.xml"]:
    root = ET.parse(fn).getroot()
    for view in root.iter("view"):
        for el in view:
            known = props.get(el.tag)
            if known is None:
                print("unknown element", el.tag, fn); errs += 1; continue
            for p in el:
                if p.tag not in known:
                    print(f"{fn}: <{el.tag} name={el.get('name')}> unknown prop {p.tag}"); errs += 1
                t = (p.text or "").strip()
                if p.tag in ("pos","size","origin","itemSize","itemSpacing","cropSize","maxSize","tileSize","backgroundMargins","selectedBackgroundMargins","itemMargin"):
                    vals = t.split()
                    if "${" in t: continue
                    if len(vals)!=2: print("bad pair",fn,el.get('name'),p.tag,t); errs+=1; continue
                    v=[float(x) for x in vals]
                    if p.tag=="itemSpacing" and max(v)>0.1: print("itemSpacing>0.1",fn,v); errs+=1
                    if p.tag=="itemSize" and (min(v)<0.05 or max(v)>1): print("itemSize range",fn,el.get('name'),v); errs+=1
                    if p.tag=="itemMargin" and max(v)>0.2: print("itemMargin",fn); errs+=1
                if "CornerRadius" in p.tag or p.tag=="cornerRadius":
                    if not 0 <= float(t) <= 0.5: print("radius range", fn, t); errs+=1
                if p.tag.lower().endswith("color") and t.startswith("$") is False:
                    if not re.fullmatch(r"[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?", t): print("bad color",fn,t); errs+=1
print("errors:", errs)
