#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ru_partpos.py -- ★机器生成右上臂的 PCB_PART_POS 串 (零手抄)★

输入 (机器读):
  · logs/iss328/01_official_RSEL_TP_pos.tsv  -- ★官方板 pcbnew GetPosition 权威读法 (cont1 落的)★
  · HW/PCB/LAYOUT_FIX_SPEC.md §3 方案 A       -- ★D3_P 换位规则的唯一权威页★
输出:
  · logs/iss328/05_RU_PCB_PART_POS.txt        -- ★右上臂的 10 条 R_SEL_* 串 (机器生成)★
  · logs/iss328/05b_ru_partpos_provenance.txt -- 出处逐条登记
判定: 10 条 distinct · 全部取自官方板实测坐标 (除 R_SEL_D3_P 按方案 A 换位) · 帧 = B160x100
"""
import os
import re
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
TSV = os.path.join(PROJ, "logs/iss328/01_official_RSEL_TP_pos.tsv")
SPEC = os.path.join(PROJ, "HW/PCB/LAYOUT_FIX_SPEC.md")
OUT = os.path.join(PROJ, "logs/iss328/05_RU_PCB_PART_POS.txt")
PROV = os.path.join(PROJ, "logs/iss328/05b_ru_partpos_provenance.txt")

ORDER = ["R_SEL_D0_N", "R_SEL_D0_P", "R_SEL_D1_N", "R_SEL_D1_P",
         "R_SEL_CK_N", "R_SEL_CK_P", "R_SEL_D2_N", "R_SEL_D2_P",
         "R_SEL_D3_N", "R_SEL_D3_P"]


def main():
    # ① 读官方板实测落位
    official = {}
    with open(TSV, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            ref, x, y = parts[0], parts[1], parts[2]
            official[ref] = (float(x), float(y))

    # ② 从 §3 方案 A 的 PCB_PART_POS 串里抽 (★唯一权威页★)
    spec = open(SPEC, encoding="utf-8").read()
    # ★必须取【§3 方案 A】那条 20 件串 (★L62 那条是左上臂的坏值示例·不是方案 A★)
    # ★判据 = 串里同时含 【R_SEL_D3_P:122.30,5.50】(方案 A 换位) + 【TP_DSI_D0_N:75.70,5.50】(官方锚点)★
    cands = [mm.group(1) for mm in re.finditer(r'PCB_PART_POS="([^"]+)"', spec)]
    hit = [c for c in cands
           if "R_SEL_D3_P:122.30,5.50" in c and "TP_DSI_D0_N:75.70,5.50" in c]
    if len(hit) != 1:
        print("❌ 方案 A 串匹配到 %d 条 (期望恰好 1 条) ⇒ 收工" % len(hit))
        return 2
    plan_a = {}
    for item in hit[0].split(";"):
        item = item.strip()
        if not item:
            continue
        ref, xy = item.split(":")
        x, y = xy.split(",")
        plan_a[ref] = (float(x), float(y))

    # ③ 断言: 方案 A 的 10 条 R_SEL_* 与官方板实测一致 (R_SEL_D3_P 除外 = 换位那条)
    swapped = []
    rows = []
    for ref in ORDER:
        if ref not in official:
            print("❌ 官方板实测表里没有 %s" % ref)
            return 3
        if ref not in plan_a:
            print("❌ 方案 A 串里没有 %s" % ref)
            return 3
        ox, oy = official[ref]
        ax, ay = plan_a[ref]
        if abs(ox - ax) > 0.01 or abs(oy - ay) > 0.01:
            swapped.append((ref, (ox, oy), (ax, ay)))
        rows.append((ref, ax, ay, (ox, oy)))

    # ④ 出处自证: 方案 A 串里 R_SEL_D3_P 的换位必须是 (78.90,9.50) → (122.30,5.50)
    if [r[0] for r in rows if r[1] != r[3][0] or r[2] != r[3][1]] != ["R_SEL_D3_P"]:
        print("❌ 换位项不是唯一的 R_SEL_D3_P ⇒ 收工 (方案 A 口径变了)")
        return 4
    d3 = [r for r in rows if r[0] == "R_SEL_D3_P"][0]
    if (round(d3[3][0], 2), round(d3[3][1], 2)) != (78.90, 9.50) or (round(d3[1], 2), round(d3[2], 2)) != (122.30, 5.50):
        print("❌ R_SEL_D3_P 换位不是 (78.90,9.50) → (122.30,5.50) ⇒ 收工")
        return 5

    pp = ";".join("%s:%.2f,%.2f" % (r[0], r[1], r[2]) for r in rows)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(pp + "\n")
    with open(PROV, "w", encoding="utf-8") as f:
        f.write("# ISS-328 · 右上臂 PCB_PART_POS 出处逐条登记 (★机器生成·零手抄★)\n")
        f.write("# 坐标帧 = B160x100 (★ISS-274 帧声明★ · 160.00×100.00mm / 8 铜层 / 186 封装)\n")
        f.write("# 权威实测源 = logs/iss328/01_official_RSEL_TP_pos.tsv (★官方板 pcbnew GetPosition★)\n")
        f.write("# 方案源 = HW/PCB/LAYOUT_FIX_SPEC.md §3 方案 A 的 PCB_PART_POS 串\n")
        f.write("#\n# ref\t官方板实测(x,y)\t本臂目标(x,y)\t来源\n")
        for ref, ax, ay, (ox, oy) in rows:
            src = "官方板实测 (== 方案 A)" if (abs(ox - ax) <= 0.01 and abs(oy - ay) <= 0.01) \
                else "★方案 A 换位 (官方板 %.2f,%.2f → %.2f,%.2f)" % (ox, oy, ax, ay)
            f.write("%s\t%.2f,%.2f\t%.2f,%.2f\t%s\n" % (ref, ox, oy, ax, ay, src))
        f.write("\n# distinct = %d (10 个 R_SEL_*) · ★本臂【不钉任何 TP_DSI_*】★\n" % len(rows))
        f.write("# 本臂 PCB_PART_POS = %s\n" % pp)
    print("✅ 右上臂 PCB_PART_POS (10 条) =")
    print("   " + pp)
    print("✅ 出处登记 → %s" % PROV)
    return 0


if __name__ == "__main__":
    sys.exit(main())
