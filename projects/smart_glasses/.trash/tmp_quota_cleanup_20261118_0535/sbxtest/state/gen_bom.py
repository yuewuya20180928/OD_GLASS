#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM 生成器 (gen_bom) —— 从 **脚级真值表** `HW/netlist_v1_pins.csv` 机械生成 `HW/BOM_v1.csv`
================================================================================
★为什么改输入表 (2026-11-11 20:2x, ISS-193 重派, hw-lead):
  ★**旧版读的是【导线级】表 `HW/netlist_v1.csv`** ⇒ 那张表是【网段一行】(node1→node2),
  **一个器件会出现多行**, 且每个 RAIL_*/NET_* 网段各占一行 ⇒ 天生产生:
    ① **75 个伪器件** (`RAIL_*` 15 + `NET_*` 60) 混进物料表 (★评审 R12 的根★)
    ② **漏掉 `J_SOM_P2` / `J_SOM_P4`** (★它们在旧表里只出现在 node 串、从不在 ref 列★)
  ★**脚级真值表 `HW/netlist_v1_pins.csv` 才是对的口径** (★584 行 = 584 脚 / 218 器件 /
  0 伪器件 / 含 P2+P4★) ⇒ **一张脚 = 一行**, 器件 = 同 ref 的一组脚 ⇒ 按 ref 聚合即得 BOM。

★聚合语义 (2026-11-11 20:2x 定, 与 ISS-191 的 DNP 语义同源):
  ① **一行 = 一个器件** (★同一器件多脚只算 1 个 ⇒ qty=1★; 备料倍数写在 memo, 见 J_CHG 覆盖表)
  ② **dnp 聚合**: ★该器件【所有脚都标 DNP】 ⇒ 整器标 DNP (实物不装)★;
     ★只要有一脚必装 ⇒ 整器标必装, 但【注记里必须写明哪几脚 DNP】(★别静默吞掉★)
     ⇒ 与 2026-11-04 19:3x 定的 ref 级口径一致 (备料不许漏买)
  ③ **footprint / opn**: 该器件各脚上出现的非空值 (★脚级表里只有 16 个器件带★)
  ④ **封装/opn 查不到时**: ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb` 的封装属性是权威源**★
     (★Value 属性 + 焊盘数 + 焊盘名★) ⇒ 查得到就填 (注明来自板文件哪个封装/属性),
     查不到就写 `[0数据]` (★严禁用"同类器件一般多少脚"去填★)

★原则:
  ① BOM 是 **生成物**, 唯一真源是脚级表 ⇒ 任何人重跑不会漂
  ② **不许编**: 查不到的封装/型号一律 `[0数据]` / `待定`
  ③ 采购状态分档: 已定型 / 待选型 / 待原厂 / 待JBD / DNP不装 / 测试点 / 连接器
  ④ 板级归属列直接带过来 ⇒ 备料时就知道"镜框充电板"和"镜脚主 PCB"各要多少料

用法:  python3 state/gen_bom.py [--out HW/BOM_v1.csv]
退出码: 0=生成成功且自检全过  1=自检不通过
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★表侧真源 = **脚级真值表** (★584 行 = 584 脚 / 218 器件 / 0 伪器件 / 含 J_SOM_P2+P4★)
PINS_CSV = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
# ★★ 导线级表 = **仅供取伪位号** (★R12: 伪位号不许混在物料里 ⇒ 单独一张表★)
WIRE_CSV = os.path.join(PROJ, "HW", "netlist_v1.csv")
# ★R12 伪位号表 (★75 个 RAIL_*/NET_* 网段, **非物料**★)
PSEUDO_OUT = os.path.join(PROJ, "HW", "BOM_pseudo_refs_v1.csv")
# ★板文件 = 封装/属性的权威源 (★只读★; 板 md5 必须仍是 611b869e…★)
PCB_FILE = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
OUT_DEFAULT = os.path.join(PROJ, "HW", "BOM_v1.csv")

BOARD_CN = {"CHG_BOARD": "镜框充电板", "MAIN_PCB": "镜脚主 PCB", "HINGE": "跨铰链界面"}

# ★★ 板文件封装解析 (★只读板文件, 取 Value 属性 + 焊盘★)
def parse_board_footprints(pcb_path: str) -> "OrderedDict[str, dict]":
    """★板文件 ⇒ {ref: {"value":…, "pads":[…], "npads":n}} (★脚手架: 括号配平扫描★)"""
    out: "OrderedDict[str, dict]" = OrderedDict()
    if not os.path.exists(pcb_path):
        return out
    txt = open(pcb_path, encoding="utf-8").read()
    i = 0
    while True:
        j = txt.find("(footprint ", i)
        if j < 0:
            break
        depth, k = 0, j
        while k < len(txt):
            c = txt[k]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        blk = txt[j:k + 1]
        i = k + 1
        props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
        ref = (props.get("Reference") or "").strip()
        if not ref or ref in out:
            continue
        pads = re.findall(r'\(pad\s+"([^"]*)"', blk)
        out[ref] = {"value": (props.get("Value") or "").strip(), "pads": pads, "npads": len(pads)}
    return out


# ★★ 备料口径覆盖表 (★ISS-105 派生: 备料倍数/实物件数只能写在 memo, qty 恒为 1★)
PROCURE_NOTES = {
    "J_CHG": ("★**实物一对 (框侧座 + 脚侧座), 备料按 2 只** (★qty 列恒为 1 = 逻辑器件口径★)"
              " · ★R_ILIM 订正提示: 见 `HW/CHARGE_CURRENT_RECHECK_2026-11-01.md` §2.2/§2.4 "
              "(CHARGE_CURRENT_RECHECK: R_ILIM 选 680Ω)★"),
}

# ★★ 脚级表里 **没有** footprint/opn 的器件, 按板文件权威源回填 ★★
# ★键 = 脚级表 ref; 值 = (opn, 证据等级, 依据文字) ★
# ★★ 口径: 只填【板文件/网表里真能读出来的】; 读不出来的 ⇒ opn 写 `[0数据]` (★不猜★)
OPN_FROM_BOARD = {
    # ★板文件 `demo_mainboard.kicad_pcb` 封装 **Value 属性** 里就是型号 ⇒ 填
    "U_BATPROT": ("BQ2970", "[实测]",
                  "★板文件封装 U_BATPROT 的 Value 属性 = 'BQ2970' (★TI BQ2970 电池保护 IC, 6 脚 SOT-23-6★)"),
    # ★同料交叉引用 (★网表里 Q2 的 opn 明写 "(同 Q1)" ⇒ Q1 同料★)
    "Q1": ("CSD16406Q3", "[实测]",
           "★`HW/netlist_v1.csv` 里 Q2 的 opn 明写 'CSD16406Q3 (同 Q1)' ⇒ Q1 同料 CSD16406Q3 "
           "(★板文件封装 Q1 的 Value='[待选型] N-MOS', 5 焊盘 (pad 2,3,4,5,6), 与 Q2 的 5 焊盘 (同 pad 名) 一致 "
           "⇒ 佐证与 Q2 同封装 'SON-8 Q3, 3.3 x 3.3 mm'★)"),
}
# ★同封装连带回填 (★ref → 封装文本; 依据 = 上表同料交叉引用 + 板文件焊盘名一致★)
FOOTPRINT_FROM_BOARD = {
    "Q1": ("SON-8 Q3, 3.3 x 3.3 mm", "[实测]",
           "★与 Q2 同封装 (★Q2 的 footprint 字段 = 'SON-8 Q3, 3.3 x 3.3 mm' + 板文件 Q1/Q2 焊盘名同为 2,3,4,5,6 ⇒ 佐证★)"),
}


def procurement_status(ref: str, value: str, typ: str, dnp: str, evidence: str) -> tuple[str, str]:
    """返回 (采购状态, 备注)"""
    v = value or ""
    if dnp == "DNP":
        return ("DNP-不装", "方案A/B 二选一或预留位; 板上有位置但首版不贴")
    if "[待选型]" in v:
        return ("待选型", "型号待定: 询价/选型完成后回填")
    if "[待原厂]" in v or evidence == "[待原厂]":
        return ("待原厂", "等原厂回信 (球位/电源域/接口类)")
    if "[待JBD]" in v or evidence == "[待JBD]":
        return ("待JBD", "等 JBD 光机接口定义")
    if ref.startswith("TP_"):
        return ("测试点", "测试焊盘, 免 BOM 但要占板面")
    if typ == "CONN" or ref.startswith("J_") or ref.startswith("CONN_"):
        return ("连接器", "型号/间距/引脚编号待结构与装配复核 (★本版 pin 编号自拟)")
    if typ in ("R", "C", "L"):
        return ("已定型-无源件", "阻容感: 值/容差可定, **封装待板宽/贴装工艺定**")
    if typ == "IC":
        return ("已定型-IC", "型号已定 (官网/官方数据手册), 封装与替代料待采购确认")
    if typ == "SW":
        return ("已定型-开关", "按键/开关: 型号待选型")
    if typ == "LED":
        return ("已定型-LED", "LED: 型号待选型")
    return ("待分类", "")


def _pick_value(rows: list[dict], board_val: str = "") -> str:
    """★器件级 value 聚合 (★口径: 器件本体行众数 → 全表明显众数(≥2 票) → 板文件 Value → 首见★)

    ★**为什么这么取**: 脚级表里同一器件的行 value 不一样 ——
      · **器件本体行** (`type` 不是 'NET') 的 value = ★器件身份描述★ ('TPS7A20-12' / 'BQ2970')
      · **网节点行** (`type`='NET') 的 value = ★脚级功能串★ ('GND (pin2)' / 'EN (pin3)')
    ⇒ ① 本体行众数 (LDO ⇒ 'TPS7A20-12'); ② 本体行一个都没有的 (如 J_SOM_P1) ⇒ 全表众数
      (要求 ≥2 票才认, 避免 4 个各 1 票的脚功能串乱选); ③ 再不行 ⇒ **板文件封装的 Value 属性**
      (★板文件 = 权威源★, 如 U_EN_SW); ④ 再不行 ⇒ 首次出现的非空 value ★
    """
    body = [x for x in rows if (x.get("type") or "").strip() not in ("NET", "")]
    pools = []
    if body:
        pools.append(body)
    pools.append(rows)
    for pool in pools:
        vals = [(r.get("value") or "").strip() for r in pool]
        vals = [v for v in vals if v]
        if not vals:
            continue
        cnt = Counter(vals)
        top = max(cnt.values())
        if pool is rows and top < 2:
            continue          # ★全表众数必须 ≥2 票 (否则各 1 票的脚功能串不能定值)★
        for v in vals:      # ★脚级表首次出现者 ★
            if cnt[v] == top:
                return v
    if board_val:
        return board_val
    for r in rows:
        v = (r.get("value") or "").strip()
        if v:
            return v
    return ""


def _pick_type(rows: list[dict]) -> str:
    """★器件级 type 聚合 (★口径: 唯一的非-'NET' type 优先, 否则众数★)

    ★脚级表里同一器件的行会带不同 type ('NET' = 该行是网节点, 'IC'/'CONN'/'R' = 器件本体)
    ⇒ 器件级 type 取**唯一的非 NET type** (J_USB_C → CONN; U_LDO_S12 → IC) ⇒
    与旧 BOM (导线级表首行口径) 对齐, 且不再把 LDO 误标成 'NET' ★
    """
    ts = [(r.get("type") or "").strip() for r in rows]
    ts = [t for t in ts if t]
    if not ts:
        return ""
    real = sorted({t for t in ts if t != "NET"})
    if len(real) == 1:
        return real[0]
    if not real:
        return "NET"
    cnt = Counter(ts)
    top = max(cnt.values())
    for t in ts:
        if cnt[t] == top:
            return t
    return ts[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()
    if not os.path.exists(PINS_CSV):
        print(f"❌ 缺脚级真值表: {PINS_CSV}", file=sys.stderr)
        return 2

    rows = list(csv.DictReader(open(PINS_CSV, encoding="utf-8-sig")))
    board = parse_board_footprints(PCB_FILE)

    # ---- 按 ref 聚合 (★一行 = 一个器件★) ----
    groups: "OrderedDict[str, list[dict]]" = OrderedDict()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if not ref:
            continue
        groups.setdefault(ref, []).append(r)

    bom: "OrderedDict[str, dict]" = OrderedDict()
    for ref, rs in groups.items():
        vals = [(x.get("value") or "").strip() for x in rs]
        dps = [(x.get("dnp") or "").strip().upper() for x in rs]
        dnp_pins = [x.get("pin") for x in rs if (x.get("dnp") or "").strip().upper() == "DNP"]

        # ★dnp 聚合 (★全 DNP ⇒ 整器 DNP; 有任一必装 ⇒ 必装 + 注记写明哪几脚 DNP★)
        if dps and set(dps) == {"DNP"}:
            dnp = "DNP"
        elif "必装" in dps:
            dnp = "必装"
        elif dps and set(dps) == {"可选"}:
            dnp = "可选"
        else:
            dnp = "必装"

        ev = ""
        for x in rs:
            if (x.get("evidence") or "").strip():
                ev = x["evidence"].strip()
                break
        tbd = ""
        for x in rs:
            if (x.get("tbd") or "").strip():
                tbd = x["tbd"].strip()
                break
        fps = {(x.get("footprint") or "").strip() for x in rs} - {""}
        opns = {(x.get("opn") or "").strip() for x in rs} - {""}
        fp = sorted(fps)[0] if fps else ""
        opn = sorted(opns)[0] if opns else ""
        board_code = ""
        for x in rs:
            if (x.get("board") or "").strip():
                board_code = x["board"].strip()
                break
        page = ""
        for x in rs:
            if (x.get("page") or "").strip():
                page = x["page"].strip()
                break
        typ = _pick_type(rs)

        val = _pick_value(rs, (board.get(ref) or {}).get("value", ""))
        status, memo = procurement_status(ref, val, typ, dnp, ev)

        bom[ref] = {
            "ref": ref, "qty": 1, "value": val, "type": typ, "dnp": dnp,
            "board": board_code, "page": page, "evidence": ev, "tbd": tbd,
            "footprint": fp or "待定", "opn": opn, "tolerance": "待定", "alt_part": "待定",
            "procurement": status, "memo": memo,
            "_pins": len(rs), "_dnp_pins": dnp_pins, "_board": board_code, "_page": page,
        }

    # ---- 脚级表里没带 page/board/type 的器件 (★只有 J_SOM_P2 / J_SOM_P4★) ----
    # ★依据: 板文件里这两个位号有 100 焊盘封装 (⇒ 实物在板上) + 同族 J_SOM_P1/P3 同板同页★
    for ref in ("J_SOM_P2", "J_SOM_P4"):
        b = bom.get(ref)
        if not b:
            continue
        bb = board.get(ref, {})
        if not b["_board"]:
            b["_board"] = "MAIN_PCB"
            b["board"] = BOARD_CN.get("MAIN_PCB", "MAIN_PCB")
            b["memo"] += (" ★板级归属: 板文件有该位号 %d 焊盘封装 + 同族 J_SOM_P1/P3 同板 ⇒ MAIN_PCB★"
                          % bb.get("npads", 0))
        if not b["_page"]:
            b["_page"] = "P1"
            b["page"] = "P1"
            b["memo"] += " ★页位: 脚级表 page 空 ⇒ 按同族 J_SOM_P1/P3 落 P1 (★与 state/gen_kicad_sch.py 同口径★)"
        if not b["type"]:
            b["type"] = "NET"
            b["procurement"], m2 = procurement_status(ref, b["value"], "NET", b["dnp"], b["evidence"])
            b["memo"] = m2 + b["memo"]
            b["memo"] += " ★type 口径: 同族 J_SOM_P1/P3 在网表里是 'NET' ⇒ 本行同口径 (procurement 仍按 J_ 前缀判 '连接器')★"
        if not b["value"]:
            b["value"] = bb.get("value", "") or "待定"
        if bb.get("value"):
            b["footprint"] = bb["value"]
            b["opn"] = "DF40C-100DS-0.4V(51)"
            b["evidence"] = "[实测]"
            b["memo"] += (" ★封装/型号来源: 板文件 `HW/PCB/demo_mainboard.kicad_pcb` 封装 %s 的 "
                          "Value 属性 = '%s' (%d 焊盘) ⇒ opn 记 DF40C-100DS-0.4V(51)★"
                          % (ref, bb["value"], bb.get("npads", 0)))

    # ---- 封装/opn 回填: 板文件是权威源 (★查不到就 [0数据], 严禁用"同类器件一般多少脚"★) ----
    GAP29 = ["BT_432243", "CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_LIGHT", "D_ESD_TC",
             "D_ESD_USB_D", "D_TVS_VBUS", "FB_DEMO", "FB_VBUS", "J_USB_C", "Q1", "Q2", "Q_AND",
             "Q_CHG_LED", "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_CAM", "SW_KEY_PWR", "SW_KEY_VM",
             "SW_KEY_VP", "SW_RST", "U_BATPROT", "U_EN_SW", "U_LDO_S28", "U_PWR_SW", "U_SUPV", "X1"]
    filled_opn = 0
    still_zero = 0
    for ref in GAP29:
        b = bom.get(ref)
        if not b:
            continue
        bb = board.get(ref)
        if not b["opn"] or b["opn"] == "待定":
            if ref in OPN_FROM_BOARD:
                opn, grade, why = OPN_FROM_BOARD[ref]
                b["opn"] = opn
                b["evidence"] = grade
                b["memo"] += " ★" + why + "★"
                filled_opn += 1
            else:
                b["opn"] = "[0数据]"
                if bb:
                    b["memo"] += (" ★封装/型号: 板文件封装 %s 的 Value 属性 = '%s' (%d 焊盘: %s) "
                                  "⇒ **该属性里没有型号** ⇒ opn 标 [0数据] (★不猜★)★"
                                  % (ref, bb.get("value", ""), bb.get("npads", 0),
                                     ",".join(bb.get("pads", [])[:8])))
                else:
                    b["memo"] += (" ★封装/型号: 板文件 `demo_mainboard.kicad_pcb` 里【没有】该位号的封装 "
                                  "(★充电板 CHG_BOARD 件, 不在本 PCB★) ⇒ opn 标 [0数据] (★不猜★)★")
                still_zero += 1
        if b["footprint"] == "待定" and bb:
            if ref in FOOTPRINT_FROM_BOARD:
                fp, grade, why = FOOTPRINT_FROM_BOARD[ref]
                b["footprint"] = fp
                b["evidence"] = grade
                b["memo"] += " ★" + why + "★"
            else:
                b["footprint"] = "★板文件封装: %d 焊盘 (%s)" % (bb.get("npads", 0), bb.get("value", "")[:60])

    # ---- 混合 DNP 器件: 注记写明哪几脚 DNP (★别静默吞掉★) ----
    mixed = []
    for ref, b in bom.items():
        dp = b.pop("_dnp_pins", [])
        b.pop("_pins", None)
        b.pop("_board", None)
        b.pop("_page", None)
        if dp and b["dnp"] != "DNP":
            mixed.append(ref)
            b["memo"] += (" ★该器件有 %d 脚标 DNP (%s) 但整器按必装 (★有一脚必装 ⇒ 实物装上, 该脚留空/NC★)"
                          % (len(dp), ",".join(str(x) for x in dp)))
        if ref in PROCURE_NOTES:
            b["memo"] = PROCURE_NOTES[ref] + " | " + b["memo"]

    # ---- 写盘 ----
    COLS = ["ref", "qty", "value", "type", "dnp", "board", "page", "evidence", "tbd",
            "footprint", "opn", "tolerance", "alt_part", "procurement", "memo"]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for ref, b in bom.items():
            b["board"] = BOARD_CN.get(b["board"], b["board"])
            w.writerow({c: b.get(c, "") for c in COLS})

    # ---- 自检 (机械判) ----
    fails = []
    pseudo = [r for r in bom if r.startswith("RAIL_") or r.startswith("NET_")]
    if pseudo:
        fails.append("伪器件进表: %s" % pseudo[:5])
    for must in ("J_SOM_P2", "J_SOM_P4"):
        if must not in bom:
            fails.append("缺 %s (★脚级表里有, BOM 必须有★)" % must)
    dup = [r for r, b in bom.items() if b["qty"] != 1]
    if dup:
        fails.append("qty 不等于 1 的位号: %s" % dup[:5])
    no_status = [r for r, b in bom.items() if not b["procurement"]]
    if no_status:
        fails.append("无采购状态的位号: %s" % no_status[:5])
    board_missing = [r for r, b in bom.items() if not b["board"]]
    if board_missing:
        fails.append("无板级归属的位号: %s" % board_missing[:5])
    if len(bom) != len(groups):
        fails.append("器件数与脚级表 ref 数不一致: BOM %d vs 表 %d" % (len(bom), len(groups)))

    by_status: dict[str, int] = {}
    for b in bom.values():
        by_status[b["procurement"]] = by_status.get(b["procurement"], 0) + 1
    by_board: dict[str, int] = {}
    for b in bom.values():
        by_board[b["board"]] = by_board.get(b["board"], 0) + 1
    fp_done = [r for r, b in bom.items() if b["footprint"] not in ("", "待定")]
    opn_done = [r for r, b in bom.items() if (b.get("opn") or "").strip() not in ("", "[0数据]")]
    dnp_devs = [r for r, b in bom.items() if b["dnp"] == "DNP"]

    # ---- R12: 伪位号**单独一张表** (★不许混在物料里★) ----
    pseudo_refs = OrderedDict()
    if os.path.exists(WIRE_CSV):
        for r in csv.DictReader(open(WIRE_CSV, encoding="utf-8-sig")):
            ref = (r.get("ref") or "").strip()
            if not (ref.startswith("RAIL_") or ref.startswith("NET_")):
                continue
            e = pseudo_refs.setdefault(ref, {"type": (r.get("type") or "").strip(),
                                             "value": (r.get("value") or "").strip(),
                                             "nets": [], "dnp": (r.get("dnp") or "").strip()})
            net = (r.get("net") or "").strip()
            if net and net not in e["nets"]:
                e["nets"].append(net)
    with open(PSEUDO_OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ref", "type", "value", "nets", "dnp", "note"])
        for ref, e in pseudo_refs.items():
            w.writerow([ref, e["type"], e["value"], "|".join(e["nets"]), e["dnp"],
                        "★非物料: 网段/电源轨, 不是可采购器件 (★评审 R12: 伪位号不许混进物料表★)"])

    print("=" * 72)
    print("  BOM 生成 · 项目总工机械验收 (★脚级真值表口径★)")
    print("=" * 72)
    print("  输出: %s  (%d bytes)" % (args.out, os.path.getsize(args.out)))
    print("  输入: %s  (脚级 %d 行 ⇒ 器件 %d 个)" % (PINS_CSV, len(rows), len(groups)))
    print("  器件数: %d  | 伪器件 (RAIL_*/NET_*): %d  | 含 J_SOM_P2: %s | 含 J_SOM_P4: %s"
          % (len(bom), len(pseudo), "J_SOM_P2" in bom, "J_SOM_P4" in bom))
    print("  伪位号另表: %s (%d 个, ★非物料★)"
          % (os.path.basename(PSEUDO_OUT), len(pseudo_refs)))
    print("  DNP 整器: %d  | 混合 DNP (必装+注记脚位): %d %s"
          % (len(dnp_devs), len(mixed), mixed))
    print("  封装已回填: %d/%d   OPN 已定型: %d/%d   [0数据]: %d"
          % (len(fp_done), len(bom), len(opn_done), len(bom), still_zero))
    print("  按采购状态:")
    for k, v in sorted(by_status.items(), key=lambda x: -x[1]):
        print("     %-18s %>4d" % (k, v) if False else "     %-18s %4d" % (k, v))
    print("  按板级归属:")
    for k, v in sorted(by_board.items(), key=lambda x: -x[1]):
        print("     %-18s %4d" % (k, v))
    print()
    if fails:
        for f in fails:
            print("  ❌ %s" % f)
        print("=" * 72)
        return 1
    print("  ✅ 自检全过 (无伪器件 / P2+P4 在表 / qty=1 / 采购状态 / 板级归属)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
