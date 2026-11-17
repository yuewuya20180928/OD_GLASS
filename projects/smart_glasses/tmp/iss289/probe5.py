import re, os, collections
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sch=os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_sch")
txt=open(sch,encoding="utf-8").read()
refs=re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', txt)
print("sch property Reference 数 =", len(refs), "唯一 =", len(set(refs)))
endd=[r for r in refs if r and r[-1].isdigit()]
print("  末字符数字 =", len(endd))
print("  已带 _1 后缀 =", sorted([r for r in refs if r.endswith('_1')]))
print("  样例末字符数字:", sorted(endd))
# board
btxt=open(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"),encoding="utf-8").read()
brefs=set(re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', btxt))
srefs=set(refs)
print("原理图 refs 不在板上的 =", len(srefs-brefs), sorted(srefs-brefs)[:20])
print("板上 refs 不在原理图的 =", len(brefs-srefs), sorted(brefs-srefs))
letter_board=[r for r in brefs if r[-1].isdigit() is False]
print("板上末字符非数字 (会被加 _1 的候选) =", len(letter_board))
# 子页?
import glob
print("sch 文件列表:", sorted(os.path.basename(p) for p in glob.glob(os.path.join(PROJ,"HW","PCB","*.kicad_sch"))))
