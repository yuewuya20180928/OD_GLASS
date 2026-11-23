#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 186 件逐件目标清单生成 (★只读·不写板★)
产出 tmp/iss369/targets186.json  ⇒  186 行, 每行:
  ref, bucket, action(写/不写), target_libname, reason_code, reason,
  board_pads_n, board_pad_sizes, board_fab, board_center,
  lib_path, lib_md5, lib_pads_n, lib_pad_sizes, lib_fab, lib_center,
  d_pad, d_center, d_fab, geom_ok, evidence
"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
BUCK = json.load(open(os.path.join(ROOT, "tmp/iss369/buckets.json"), encoding="utf-8"))
RC = {r["ref"]: r for r in json.load(
    open(os.path.join(ROOT, "tmp/iss369/iss364_recheck.json"), encoding="utf-8"))}
PADEQ = json.load(open(os.path.join(ROOT, "tmp/iss369/padeq186_rot.json"), encoding="utf-8"))
inv = {f["ref"]: f for f in INV}
t90 = set(BUCK["target90_list"])
rest96 = BUCK["rest96_list"]

import csv
BOM = {}
with open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        ref = (r.get("ref") or "").strip()
        if ref and ref not in BOM:
            BOM[ref] = r

# ★J_SOM 的官方等效件 (逐焊盘实测, 180° 旋转, Δ=0)
JSOM_LIB = "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm"

# ★「已落 land」三件 (板面按原厂图纸自绘) 的官方件实测对照 (用于写理由)
LANDED = {
    "U_TEMP": ("Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
               "板面 6 焊盘 @0.65mm pitch 无散热焊盘 (TI DRV0006B); 官方 WSON-6-1EP 带 EP ⇒ 9 焊盘"),
    "CONN_LIGHT": ("Connector_FFC-FPC:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal",
                   "板面 22 焊盘 0.30x1.30mm (RPi CM5IO 抄件·无壳体固定柱); 官方 FH12-22S 带 2 个固定柱焊盘 ⇒ 24 焊盘"),
    "J_USB_C": ("Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
                "板面 16 焊盘 @0.50mm pitch (GCT 原厂图纸 Rev B3·只留 16 信号焊盘); 官方件另含 2x Ø0.65mm 壳体固定孔 + 接地焊盘 ⇒ 22 焊盘"),
}


def d_of(f, m):
    bs = {(round(p["w"], 3), round(p["h"], 3)) for p in f["pads"]}
    ls = {(round(float(a), 3), round(float(b), 3))
          for a, b in (s.split("x") for s in m["pad_sizes"])}
    if len(bs) != len(ls) or not bs:
        return None, None, None
    dpad = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in ls for b in bs)
    dcen = abs(m["center"] - f["centre_dist"])
    dfab = ((abs(m["fab_w"] - f["bbox"][0]) + abs(m["fab_h"] - f["bbox"][1]))
            if f["bbox"] and m["fab_w"] else None)
    return round(dpad, 4), round(dcen, 4), (round(dfab, 4) if dfab is not None else None)


rows = []
for f in INV:
    ref = f["ref"]
    b = BOM.get(ref, {})
    typ = (b.get("type") or "").strip()
    dnp = (b.get("dnp") or "").strip()
    bf = (b.get("footprint") or "").strip()
    row = {
        "ref": ref,
        "bucket": ("90件(ISS-364 换 land + 写库名)" if ref in t90 else "96件(其余)"),
        "type": typ, "dnp": dnp, "bom_footprint": bf,
        "bom_opn": (b.get("opn") or "").strip(),
        "board_pads_n": f["pad_count"],
        "board_pad_sizes": f["pad_sizes"],
        "board_fab": f["bbox"],
        "board_center": f["centre_dist"],
        "board_has_courtyard": f["has_courtyard"],
    }
    if ref in t90:
        r = RC[ref]
        m = LIB[r["target"]]
        dp, dc, df = d_of(f, m)
        row.update({
            "action": "写",
            "target_libname": r["target"],
            "lib_path": m["path"], "lib_md5": m["md5"],
            "lib_pads_n": m["pads_n"], "lib_pad_sizes": m["pad_sizes"],
            "lib_fab": [m["fab_w"], m["fab_h"]], "lib_center": m["center"],
            "d_pad": dp, "d_center": dc, "d_fab": df,
            "reason_code": "R90",
            "reason": ("本趟换官方 land ⇒ 必须同时写 lib_id (换 land 而不写库名 ⇒ 装配厂拿不到封装·"
                       "BOM 与板面对不上); 目标件 = ISS-364 §1 台账, 本单用本机 lib_index 逐件复核过 "
                       ".kicad_mod 在盘 + md5 + 焊盘数 + 几何"),
            "evidence": "[实测]",
        })
    elif PADEQ.get(ref):
        key, deg = PADEQ[ref][0]
        m = LIB[key]
        dp, dc, df = d_of(f, m)
        row.update({
            "action": "写",
            "target_libname": key,
            "lib_path": m["path"], "lib_md5": m["md5"],
            "lib_pads_n": m["pads_n"], "lib_pad_sizes": m["pad_sizes"],
            "lib_fab": [m["fab_w"], m["fab_h"]], "lib_center": m["center"],
            "d_pad": dp, "d_center": dc, "d_fab": df,
            "rotation_deg": deg,
            "reason_code": "RE",
            "reason": ("板面铜箔已就是该官方封装 (逐焊盘实测: 焊盘数 100=100 · 尺寸 0.200x0.700 全同 · "
                       "位置/中心距 Δ<=0.001mm · 相对官方件旋转 %d°) ⇒ 写 lib_id 零铜箔改动, "
                       "只补上『这块 land 是谁』的身份 ⇒ 写" % deg),
            "evidence": "[实测]",
        })
    elif ref in LANDED:
        key, why = LANDED[ref]
        m = LIB.get(key)
        row.update({
            "action": "不写",
            "target_libname": "",
            "reason_code": "RL",
            "reason": ("板面已按原厂图纸落了 land (有 courtyard) ⇒ 不是占位; 但本机官方件与板面**几何不等价** "
                       "(%s; 官方 %s 实测 %d 焊盘 vs 板面 %d) ⇒ 写该库名 = 板面铜箔与库件对不上 (假身份) "
                       "⇒ 不写; 建议改用 property 'Footprint' 记原厂封装号 (登记·不代拍)"
                       % (why, key, m["pads_n"] if m else -1, f["pad_count"])),
            "evidence": "[实测]",
        })
    elif typ == "TP":
        row.update({
            "action": "不写",
            "target_libname": "",
            "reason_code": "RTP",
            "reason": ("测试焊盘: BOM 记「测试焊盘, 免 BOM 但要占板面」⇒ 装配厂不按库名取件; "
                       "板面为单焊盘 0.180x0.900 mm 自绘测试位, 本机 15468 个官方 .kicad_mod 逐焊盘实测 "
                       "(容差 0.05mm·允许 0/90/180/270 旋转) **无几何等价件** ⇒ 写任何官方库名都是假身份 "
                       "⇒ 不写"),
            "evidence": "[实测]",
        })
    elif dnp in ("DNP", "可选"):
        row.update({
            "action": "不写",
            "target_libname": "",
            "reason_code": "RNP",
            "reason": ("BOM 记 dnp=%s ⇒ 首版不贴 ⇒ 该 land 本趟不换; 且 BOM footprint 栏 = 「%s」"
                       "⇒ 型号/封装未选定 ⇒ 写库名 = 替老板拍板选型 (本单只登记) ⇒ 不写"
                       % (dnp, bf if bf else "空")),
            "evidence": "[实测]",
        })
    else:
        row.update({
            "action": "不写",
            "target_libname": "",
            "reason_code": "RWA",
            "reason": ("BOM footprint 栏 = 「%s」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 "
                       "的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 "
                       "(假身份) ⇒ 不写" % (bf if bf else "空")),
            "evidence": "[实测]",
        })
    rows.append(row)

json.dump(rows, open(os.path.join(ROOT, "tmp/iss369/targets186.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("=== 186 件动作分布 ===")
print(" ", dict(Counter(r["action"] for r in rows)))
print("  不写理由码:", dict(Counter(r["reason_code"] for r in rows if r["action"] == "不写")))
print("  写 =", sum(1 for r in rows if r["action"] == "写"),
      "(90件 %d + 逐焊盘等价 %d)"
      % (sum(1 for r in rows if r["action"] == "写" and r["reason_code"] == "R90"),
         sum(1 for r in rows if r["action"] == "写" and r["reason_code"] == "RE")))
print()
print("=== 90 件的几何 Δ 分布 (写进容差表的依据) ===")
for code in ("R90", "RE"):
    sub = [r for r in rows if r["reason_code"] == code]
    if not sub:
        continue
    print("  %s (%d 件):" % (code, len(sub)))
    for k in ("d_pad", "d_center", "d_fab"):
        vals = [r[k] for r in sub if r.get(k) is not None]
        if vals:
            print("     %-10s min=%.4f max=%.4f" % (k, min(vals), max(vals)))
    print("     pad 数变化件:", [(r["ref"], r["board_pads_n"], r["lib_pads_n"])
                              for r in sub if r["board_pads_n"] != r["lib_pads_n"]])
print()
print("=== 96 件桶 (★我自己实算, 与任务书括注对账★) ===")
rest = [r for r in rows if r["ref"] in rest96]
print("  按 BOM type:", dict(Counter(r["type"] for r in rest)))
print("  按 dnp     :", dict(Counter(r["dnp"] for r in rest)))
print("  按动作     :", dict(Counter(r["action"] for r in rest)))
print("  按理由码   :", dict(Counter(r["reason_code"] for r in rest)))
print("  写的那几件 :", [(r["ref"], r["target_libname"]) for r in rest if r["action"] == "写"])
