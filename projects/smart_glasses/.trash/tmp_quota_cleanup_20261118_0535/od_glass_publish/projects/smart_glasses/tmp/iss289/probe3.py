import csv, os, re, collections
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
rows=list(csv.DictReader(open(os.path.join(PROJ,"HW","netlist_v1.csv"),encoding="utf-8")))
main_rows=[r for r in rows if (r.get("board") or "MAIN_PCB").strip()=="MAIN_PCB"]
print("MAIN_PCB 行数 =", len(main_rows))
main_refs_only={ (r.get("ref") or "").strip() for r in main_rows }
print("MAIN_PCB 唯一 ref (行口径) =", len(main_refs_only))
# board file parse
txt=open(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"),encoding="utf-8").read()
fprefs=re.findall(r'\(footprint\s+"([^"]*)"', txt)
# better: reference property
refs=re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', txt)
print("板文件 footprint 块数 =", len(fprefs))
print("板文件 Reference 属性数 =", len(refs))
print("板文件唯一 ref 数 =", len(set(refs)))
dup=[r for r,c in collections.Counter(refs).items() if c>1]
print("板文件重复 ref =", dup)
suf=[r for r in refs if r.endswith("_1")]
print("板文件带 _1 后缀的 ref =", sorted(suf))
endd=[r for r in refs if r[-1].isdigit()]
print("板文件末字符为数字的 ref 数 =", len(endd))
print("  =", sorted(endd))
print("板文件在 MAIN_PCB 但生成器会剔的 (官方板独有) =", sorted(set(refs)-main_refs_only))
print("网表 MAIN_PCB 里板文件没有的 数 =", len(main_refs_only-set(refs)))
print("  =", sorted(main_refs_only-set(refs))[:80])
print("板文件 'dnp' 出现次数 =", txt.count("dnp"))
print("板文件 DNP 属性标记数 (attr dnp) =", len(re.findall(r'\(attr\s+[^)]*dnp', txt)))
