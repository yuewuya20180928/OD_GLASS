import csv, os, re, collections
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
rows=list(csv.DictReader(open(os.path.join(PROJ,"HW","netlist_v1.csv"),encoding="utf-8")))
print("netlist_v1.csv 数据行 =", len(rows))
refs=collections.OrderedDict()
for r in rows:
    ref=(r.get("ref") or "").strip()
    if not ref: continue
    refs.setdefault(ref, []).append(r)
print("唯一 ref 数 =", len(refs))
# board distribution per ref
byboard=collections.defaultdict(set)
for ref,rs in refs.items():
    for r in rs:
        byboard[(r.get("board") or "").strip()].add(ref)
for b,s in byboard.items():
    print("  board=%r ref 数 = %d" % (b, len(s)))
main=byboard.get("MAIN_PCB", set())
print("MAIN_PCB ref 数 =", len(main))
endd=sorted([r for r in main if r[-1].isdigit()])
print("MAIN_PCB 中末字符为数字的 ref 数 =", len(endd))
print("  = ", endd)
suf=sorted([r for r in main if r.endswith("_1")])
print("MAIN_PCB 中已带 _1 后缀的 ref =", suf)
# dnp per ref (main)
dnp_refs=set()
for ref,rs in refs.items():
    st={ (r.get("dnp") or "").strip() for r in rs }
    if "DNP" in st:
        dnp_refs.add(ref)
print("全表 DNP ref 数 =", len(dnp_refs))
print("MAIN_PCB ∩ DNP ref 数 =", len(main & dnp_refs))
# BAT_DET 三颗
for t in ("R_BAT_DET_1","R_BAT_DET_2","C_DET_BAT"):
    if t in refs:
        print("  %-12s dnp 状态集 = %s board = %s" % (t, sorted({(r.get('dnp') or '').strip() for r in refs[t]}), sorted({(r.get('board') or '').strip() for r in refs[t]})))
