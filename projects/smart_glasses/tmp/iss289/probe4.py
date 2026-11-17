import csv, os, re, collections
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
rows=list(csv.DictReader(open(os.path.join(PROJ,"HW","netlist_v1.csv"),encoding="utf-8")))
prows=list(csv.DictReader(open(os.path.join(PROJ,"HW","netlist_v1_pins.csv"),encoding="utf-8")))
print("pins 表行数 =", len(prows))
for t in ("C_VBUS_GND","J_CHG","J_SOM_P2","J_SOM_P4","R_BAT_DET_1","C_DET_BAT"):
    b=sorted({(r.get("board") or "").strip() for r in rows if (r.get("ref") or "").strip()==t})
    bp=sorted({(r.get("board") or "").strip() for r in prows if (r.get("ref") or "").strip()==t})
    n=len([r for r in rows if (r.get("ref") or "").strip()==t])
    print("  %-12s netlist行=%d board=%s | pins board=%s" % (t,n,b,bp))
# 板上有但 netlist 无行的 ref
txt=open(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"),encoding="utf-8").read()
refs=re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', txt)
nlrefs={(r.get("ref") or "").strip() for r in rows}
print("板上有但 netlist_v1.csv 里查无此 ref 的 =", sorted(set(refs)-nlrefs))
# generator filter
print("--- gen filter ---")
g=open(os.path.join(PROJ,"state","gen_pcb_netlist_board.py"),encoding="utf-8").read()
for m in re.finditer(r'.*BOARD_FILTER.*', g):
    print("   ", m.group(0).strip()[:160])
