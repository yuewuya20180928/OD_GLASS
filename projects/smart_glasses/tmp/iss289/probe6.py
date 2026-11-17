import re, os, glob, collections
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
schrefs=[]
for p in sorted(glob.glob(os.path.join(PROJ,"HW","PCB","demo_mainboard_p*.kicad_sch"))):
    t=open(p,encoding="utf-8").read()
    rs=re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', t)
    schrefs += [(os.path.basename(p),r) for r in rs]
print("子页 property Reference 总数 =", len(schrefs), "唯一 =", len(set(r for _,r in schrefs)))
refs=[r for _,r in schrefs]
endd=sorted([r for r in refs if r[-1].isdigit()])
print("  末字符数字 =", len(endd))
print("  已带 _1 =", sorted([r for r in refs if r.endswith('_1')]))
letter=[r for r in refs if not r[-1].isdigit()]
print("  末字符字母 (要加 _1) =", len(letter))
btxt=open(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"),encoding="utf-8").read()
brefs=set(re.findall(r'\(property\s+"Reference"\s+"([^"]*)"', btxt))
srefs=set(refs)
print("原理图有但板没有 =", len(srefs-brefs), sorted(srefs-brefs))
print("板有但原理图没有 =", len(brefs-srefs), sorted(brefs-srefs))
bl=[r for r in brefs if not r[-1].isdigit()]
print("板上末字符字母 =", len(bl), " ⇒ S1 改名后板上带 _1 后缀的 ref 数 =", len(bl)+1, "(含原有的 R_BAT_DET_1)")
print("原理图侧要改的 186 里, 有多少在板上 =", len(set(bl)&srefs))
