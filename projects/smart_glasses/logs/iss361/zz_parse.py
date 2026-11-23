#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 7: 纯 python 读板 (kicad_pcb 文本解析) + FP_TRUTH 靶子名单解析 + TP 脚数"""
import re, os, csv, json

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")

def parse_board(path):
    """纯文本解析 kicad_pcb → {ref: [pad 编号...]}"""
    txt = open(path, encoding="utf-8").read()
    out = {}
    # 顶层 (footprint ... ) 块
    for m in re.finditer(r'^\t\(footprint ', txt, re.M):
        s = m.start()
        # 找块结束: 用括号配平 (缩进 1 层 = 到下一个 "\n\t(footprint " 或 "\n\t(net " 之前)
        nxt = txt.find("\n\t(footprint ", s + 1)
        alt = txt.find("\n\t(net ", s + 1)
        cands = [x for x in (nxt, alt) if x != -1]
        e = min(cands) if cands else len(txt)
        blk = txt[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        pads = re.findall(r'\(pad "([^"]*)"', blk)
        out[ref] = pads
    return out

board = parse_board(PCB)
print("=== 纯 python 读板结果 ===")
print("  footprint 数 = %d" % len(board))
recon = json.load(open(os.path.join(ROOT, "logs/iss361/04_recon.json")))
c4 = recon["c4"]
print("  C4-158 全部在板上? %s" % all(r in board for r in c4))
missing = [r for r in c4 if r not in board]
print("  不在板上的 = %s" % missing)
from collections import Counter
print("  板面 pad 数分布 = %s" % dict(sorted(Counter(len(v) for v in board.values()).items())))
print("  板上 1-pad 件数 = %d" % len([v for v in board.values() if len(v) == 1]))

print("\n=== 13 件板面 pad 编号 (纯 python 读) ===")
G13 = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO", "Q_AND",
       "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"]
for r in G13:
    print("  %-14s pads=%s" % (r, board.get(r)))

print("\n=== 42 TP 件的板面 pad 数 (TP 都是单 land?) ===")
bom = {x['ref']: x for x in csv.DictReader(open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8"))}
tps = [r for r in recon['diff'] if bom[r]['type'] == 'TP']
print("  TP 件数 = %d · 板面 pad 数分布 = %s"
      % (len(tps), dict(sorted(Counter(len(board.get(r, [])) for r in tps).items()))))

print("\n=== FP_TRUTH_BASELINE.md 靶子名单解析 ===")
fp = open(os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md"), encoding="utf-8").read()
lines = fp.splitlines()
s2 = next(i for i, l in enumerate(lines) if l.startswith("## §2 逐 ref 表"))
s2b = next(i for i, l in enumerate(lines) if l.startswith("### §2.1"))
s4 = next(i for i, l in enumerate(lines) if l.startswith("### §4.1"))
s4b = next(i for i, l in enumerate(lines) if l.startswith("### §4.2"))
def rows_of(seg):
    out = []
    for l in seg:
        if l.startswith("| `"):
            out.append(l.split("|")[1].strip().strip("`"))
    return out
r78 = rows_of(lines[s2:s2b])
r22 = rows_of(lines[s4:s4b])
print("  §2 表 ref 数 = %d" % len(r78))
print("  §4.1 表 ref 数 = %d" % len(r22))
print("  §2+§4.1 并集 = %d" % len(set(r78) | set(r22)))
# 与 BOM 实算比
m78 = [x['ref'] for x in csv.DictReader(open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8"))
       if x['dnp'] == '必装' and x['type'] not in ('NET', 'TP') and x['footprint'] == '待定' and x['board'] == '镜脚主 PCB']
c22 = [x['ref'] for x in csv.DictReader(open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8"))
       if x['dnp'] == '必装' and x['type'] not in ('NET', 'TP') and x['footprint'] == '待定' and x['board'] == '镜框充电板']
print("  §2 表 set == BOM 78 set ? %s" % (set(r78) == set(m78)))
print("  §4.1 表 set == BOM 22 set ? %s" % (set(r22) == set(c22)))
print("  FP_TRUTH 页 100 靶子 == BOM 实算 100 ? %s" % (set(r78) | set(r22) == set(m78) | set(c22)))
print("  页 100 靶子 ∩ C4-158 = %d" % len((set(r78) | set(r22)) & set(c4)))
json.dump({"r78": r78, "r22": r22, "board_pads": board}, open(os.path.join(ROOT, "logs/iss361/11_fp_targets.json"), "w"),
          ensure_ascii=False, indent=1)
