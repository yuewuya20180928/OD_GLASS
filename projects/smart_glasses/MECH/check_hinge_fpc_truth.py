#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_hinge_fpc_truth.py —— 跨铰链 FPC 几何口径真值门禁 (ISS-240 · mech-lead · 2026-11-16)
==================================================================================================
★**本门禁不依赖任何受保护脚本** (不 import / 不调用 hinge_usb_check.py / check_demo_struct_truth.py /
   cavity_recalc_check.py / service_port_check.py / hw_cross_review_check.py / display_biosafety_v2_check.py)
   ⇒ 自己解析 `HW/netlist_v1.csv` (只读) + `HW/STEP1_PARTS_SPEC.md` (只读) + 本项目的收口页与正文
   + `state/fragments/mech.yaml` (只读) ⇒ **受保护脚本改了, 本门禁照样能跑** (只会报"legacy 块要重核")。

它判 9 件事 (G1~G9), 每条都能自己重算:

  G1 跨铰链链路清单必须与【网表 board 栏】一致 (board == "HINGE" 才算跨铰链)
     —— ★不是"ref 在网表里存在" (CONN_CAM/CONN_LIGHT 在网表里存在, 但 board=MAIN_PCB ⇒ 不跨铰链)★
  G2 每颗 FPC 座必须用它【自己的 pitch】 (camera 0.3 / display 0.5 / J_CHG 0.5) —— 禁止"全 0.5mm"一刀切
  G3 占位数与 claim 必须能从【网表真源】重算出来 (门禁自己算, 不比字面)
     —— demo 口径 5.00 / 3.35; 整机口径 25.30 / 4.05; 余量 33.00 / 2.05 / 12.70 / 1.35
  G4 正文里的旧口径 (40p / 16p / 20p / 26p / 12 mm 板宽 / 声明列 40) 必须带 canonical 作废标注 —— 裸命中 = 红
  G5 正文里必须存在【现行口径行】(31p/0.3mm + 22p/0.5mm) —— 缺 = 红 (防止下次又只留旧数)
  G6 canonical 标注串本身必须能在正文里找到 (否则门禁自己失效都没人知道)
  G7 正文里必须存在【demo 板真跨铰链口径行】(J_CHG 单链 5.00 / 3.35 ⇒ 余 33.00 / 2.05)
  G8 收口页的【真源锚点】必须齐全, 且被引用的裁定文件真的还在 (防锚点腐烂)
  G9 legacy 块记录的受保护脚本 md5 必须与现文件一致 (脚本被改 ⇒ legacy 口径要重核, H-1 的一部分)

纪律:
  · 本文所有几何输入 = 网表/脚表/裁定块的【实测值】(脚本现场解析), **无样机 ⇒ 实物 [实测] = 0 条**
  · 本文【不修改】任何受保护脚本 / 判据阈值 / 网表 / 脚表 / BOM / 板 —— 只判"口径有没有收干净"
  · 已知不一致 (legacy divergence) 必须在收口页 `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` 的机器块里登记
    (带 owner + action) —— **登记过的差异 = 已知问题 (可追踪); 没登记的差异 = 红**

用法:
    python3 MECH/check_hinge_fpc_truth.py             # 人读报告
    python3 MECH/check_hinge_fpc_truth.py --json      # 机读
    python3 MECH/check_hinge_fpc_truth.py --selftest  # 反向用例 (每条自证"真的改到了目标")

退出码: 0 = 全部断言 PASS ; 1 = 有 FAIL
==================================================================================================
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
SPEC = os.path.join(PROJ, "HW", "STEP1_PARTS_SPEC.md")
TRUTH = os.path.join(HERE, "HINGE_FPC_GEOMETRY_TRUTH.md")
DOC = os.path.join(HERE, "USB_HINGE_STRUCTURE.md")
FRAG = os.path.join(PROJ, "state", "fragments", "mech.yaml")

# ---------------------------------------------------------------- 几何基线 (与收口页 §1 同源)
TEMPLE_H_MM = 38.00          # 镜脚根部净高 (MECH_BUDGET.md L1124)
TEMPLE_T_MM = 7.00           # 镜脚前后厚需求 (MECH_BUDGET.md L135)
WALL_MM = 0.80               # 打印件单壁 (MECH_BUDGET.md §5.4)
THROAT_MM = round(TEMPLE_T_MM - 2 * WALL_MM, 3)     # 铰链段前后内净空 = 5.40
BEND_R_MM = 3.00             # 跨铰链 FPC 弯折半径 R_min (MECH_BUDGET §1.3 M9)
FPC_T_MM = 0.20              # FPC 成品厚
FPC_GAP_MM = 0.15            # FPC 嵌套间隙
HINGE_BOARD = "HINGE"        # ★网表 board 栏: 这个值才算跨铰链 ★

# ---------------------------------------------------------------- canonical 标注串 (收口页 §5)
MARK_PIN = "【已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)】"
MARK_ARCH = "【已作废 (依据 老板 2026-11-02 19:25 指示② · demo 硬件形态: 跨铰链取消)】"
MARKERS = (MARK_PIN, MARK_ARCH)

TOL = 0.005                  # mm 比较容差


# ================================================================= 网表解析 (自解析, 不 import 受保护脚本)
def _pitch_of(value: str):
    m = re.search(r"@\s*([\d.]+)\s*mm", value or "")
    return float(m.group(1)) if m else None


def _pins_of(value: str):
    v = value or ""
    m = re.search(r"(\d+)\s*[×xX]\s*(\d+)\s*p", v)
    if m:
        return int(m.group(1)) * int(m.group(2))
    m = re.search(r"(\d+)\s*p\b", v)
    return int(m.group(1)) if m else None


def load_netlist(path: str = NETLIST) -> dict:
    """返回 {seats: {ref: {pins,pitch,board,lines[]}}, pin_counts: {ref: n}, board_hist: {...}}"""
    seats, pin_counts, board_hist = {}, {}, {}
    conn_pat = re.compile(r"^(J_CHG|CONN_CAM|CONN_LIGHT|CONN_USB|J_TYPE_C|J_DEBUG|J_UART)(?:\s+pin(\d+))?$")
    with open(path, encoding="utf-8") as f:
        for lineno, row in enumerate(csv.DictReader(f), start=2):
            board = (row.get("board") or "").strip()
            board_hist[board] = board_hist.get(board, 0) + 1
            ref = (row.get("ref") or "").strip()
            if (row.get("type") or "").strip() == "CONN":
                pitch = _pitch_of(row.get("value") or "")
                pins = _pins_of(row.get("value") or "")
                if pitch is None or pins is None:
                    continue                      # 不是带 pitch 的 FPC/FFC 座 (Type-C 座 / 排针 / 焊盘位)
                s = seats.setdefault(ref, {"pins": pins, "pitch": pitch, "board": board, "lines": []})
                s["lines"].append(lineno)
                if s["board"] != board or s["pins"] != pins or s["pitch"] != pitch:
                    s["conflict"] = True           # 同一 ref 多行且口径不一致
            for col in ("node1", "node2"):
                v = (row.get(col) or "").strip()
                m = conn_pat.match(v)
                if m and m.group(2) is not None:
                    pin_counts.setdefault(m.group(1), set()).add(int(m.group(2)))
    return {
        "seats": seats,
        "pin_counts": {k: len(v) for k, v in pin_counts.items()},
        "board_hist": board_hist,
    }


# ================================================================= 收口页机器块解析
def extract_machine_block(text: str) -> str:
    m = re.search(r"<!--\s*MACHINE:BEGIN\s*-->(.*?)<!--\s*MACHINE:END\s*-->", text, re.S)
    if not m:
        return ""
    inner = m.group(1)
    y = re.search(r"```ya?ml\s*(.*?)```", inner, re.S)
    return y.group(1) if y else inner


def load_truth(path: str = TRUTH):
    txt = open(path, encoding="utf-8").read()
    block = extract_machine_block(txt)
    import yaml
    data = yaml.safe_load(block) if block.strip() else {}
    return data or {}, txt


def load_claims(path: str = FRAG) -> dict:
    try:
        import yaml
        d = yaml.safe_load(open(path, encoding="utf-8").read()) or {}
    except Exception:
        return {}
    out = {}
    for c in (d.get("interface_claims") or []):
        k = c.get("key")
        if k:
            out.setdefault(k, str(c.get("value")))
    return out


def read(path: str) -> str:
    return open(path, encoding="utf-8").read()


# ================================================================= 正文扫描 (旧口径裸命中)
def doc_lines_with_context(text: str):
    """返回 [(lineno, line, ctx_heading)] —— ctx = 最近的标题行 (用来判"这条属于哪个连接器")"""
    out, ctx = [], ""
    for i, ln in enumerate(text.splitlines(), start=1):
        if re.match(r"^#{1,6}\s", ln):
            ctx = ln
        out.append((i, ln, ctx))
    return out


def _typec_exempt(s: str) -> bool:
    """Type-C 的 16p (USB2.0-only 母座) 与跨铰链 FPC 座口径无关 —— 不得误判"""
    return any(k in s for k in ("Type-C", "J_TYPE_C", "USB 2.0", "USB2.0", "USB-C", "USB-C 座"))


def legacy_hits(line: str, ctx: str = "") -> list:
    """返回该行命中的旧口径 token 列表 (空 = 该行没有旧口径)"""
    both = line + "\n" + ctx
    hits = []
    if "40p" in line or "40 pin" in line:
        hits.append("40p")
    if re.search(r"`CONN_(CAM|LIGHT)`\s*\|\s*40\b", line):
        hits.append("声明列40p")
    if "26p" in line:
        hits.append("26p")
    if "16p" in line and not _typec_exempt(both):
        cam_ctx = ("CONN_CAM" in both) or ("mech_conn_cam_pins" in both)
        stack_ctx = any(k in both for k in ("收敛版", "铰链区堆叠", "pin 数收敛", "缩 pin"))
        if cam_ctx or stack_ctx:
            hits.append("16p")
    if "20p" in line and not _typec_exempt(both):
        light_ctx = ("CONN_LIGHT" in both) or ("mech_conn_light_pins" in both)
        stack_ctx = any(k in both for k in ("收敛版", "铰链区堆叠", "pin 数收敛", "缩 pin"))
        if light_ctx or stack_ctx:
            hits.append("20p")
    if re.search(r"(?:12\s*mm\s*板宽|板宽[^|\n]{0,8}12\s*mm)", line):
        hits.append("12mm板宽")
    return hits


def bare_legacy_hits(doc_text: str):
    """正文里带旧口径 token 却没有 canonical 作废标注的行 —— 裸命中 = 红"""
    out = []
    for lineno, ln, ctx in doc_lines_with_context(doc_text):
        hits = legacy_hits(ln, ctx)
        if hits and not any(m in ln for m in MARKERS):
            out.append((lineno, hits, ln.strip()[:110]))
    return out


# ================================================================= 断言求值 (纯函数 —— 反向用例靠它做内存变异)
def evaluate(net: dict, truth: dict, truth_text: str, doc_text: str, claims: dict) -> list:
    res = []
    seats = net["seats"]
    pin_counts = net["pin_counts"]

    def add(gid, name, ok, detail):
        res.append({"id": gid, "name": name, "ok": bool(ok), "detail": detail})

    # ---------------- G1 跨铰链链路清单 ↔ 网表 board 栏 ----------------
    net_hinge = sorted(r for r, s in seats.items() if s["board"] == HINGE_BOARD)
    canon = truth.get("canonical_cross_hinge_links") or []
    canon_refs = sorted(c.get("ref") for c in canon)
    miss = [r for r in canon_refs if r not in seats]
    wrong_board = [r for r in canon_refs if r in seats and seats[r]["board"] != HINGE_BOARD]
    divs = {d.get("key"): d for d in (truth.get("legacy_divergences") or [])}
    reg = divs.get("script_cross_links_vs_netlist_board")
    ok = (canon_refs == net_hinge) and not miss and not wrong_board and bool(reg)
    add("G1", "跨铰链链路清单必须与网表 board 栏一致 (board==HINGE 才算跨铰链)", ok,
        f"网表 board==HINGE 的座 = {net_hinge or '无'}; 收口页 canonical = {canon_refs or '无'}; "
        f"不在网表 = {miss or '无'}; board 不符 = {wrong_board or '无'}; "
        f"旧 4 条清单差异登记 = {'有 (owner=' + str(reg.get('owner')) + ')' if reg else '★无 ⇒ 红'}")

    # ---------------- G2 每颗座用自己的 pitch ----------------
    prob2 = []
    all_seats = truth.get("fpc_seats_all") or []
    for c in all_seats:
        r = c.get("ref")
        if r not in seats:
            prob2.append(f"{r} 不在网表 FPC 座里")
            continue
        s = seats[r]
        if int(c.get("pins", -1)) != s["pins"]:
            prob2.append(f"{r} pins 收口页={c.get('pins')} 网表={s['pins']}")
        if abs(float(c.get("pitch_mm", -1)) - s["pitch"]) > 1e-9:
            prob2.append(f"{r} pitch 收口页={c.get('pitch_mm')} 网表={s['pitch']}")
        if (c.get("board") or "") != s["board"]:
            prob2.append(f"{r} board 收口页={c.get('board')} 网表={s['board']}")
    pitches = sorted({float(c.get("pitch_mm")) for c in all_seats})
    if len(pitches) < 2:
        prob2.append(f"★全部座用同一个 pitch {pitches} ⇒ 一刀切 (camera 必须 0.3)")
    ok2 = not prob2
    add("G2", "每颗 FPC 座必须用它自己的 pitch (禁止全 0.5mm 一刀切)", ok2,
        f"收口页 pitch 集合 = {pitches} (网表实解析: "
        + "; ".join(f"{r}={s['pins']}p@{s['pitch']}mm/{s['board']}" for r, s in sorted(seats.items()))
        + "); 问题 = " + ("无" if ok2 else "; ".join(prob2)))

    # ---------------- G3 占位数/claim 必须能重算 ----------------
    comp = truth.get("computed") or {}
    # demo 口径: canonical 清单 (board==HINGE)
    demo_stack = sum(int(c["pins"]) * float(c["pitch_mm"]) for c in canon)
    demo_radial = round(BEND_R_MM + len(canon) * (FPC_T_MM + FPC_GAP_MM), 3)
    demo_smar = round(TEMPLE_H_MM - demo_stack, 3)
    demo_rmar = round(THROAT_MM - demo_radial, 3)
    # 整机口径: 网表里所有 FPC 座 (不论 board)
    prod_stack = round(sum(s["pins"] * s["pitch"] for s in seats.values()), 3)
    prod_radial = round(BEND_R_MM + len(seats) * (FPC_T_MM + FPC_GAP_MM), 3)
    prod_smar = round(TEMPLE_H_MM - prod_stack, 3)
    prod_rmar = round(THROAT_MM - prod_radial, 3)
    prob3 = []

    def chk(key, got):
        want = comp.get(key)
        if want is None:
            prob3.append(f"收口页 computed 缺 {key}")
        elif abs(float(want) - got) > TOL:
            prob3.append(f"{key}: 收口页={want} 重算={got}")

    chk("demo_stack_mm", demo_stack)
    chk("demo_radial_mm", demo_radial)
    chk("demo_stack_margin_mm", demo_smar)
    chk("demo_radial_margin_mm", demo_rmar)
    chk("product_stack_mm", prod_stack)
    chk("product_radial_mm", prod_radial)
    chk("product_stack_margin_mm", prod_smar)
    chk("product_radial_margin_mm", prod_rmar)

    # 声明版/收敛版 legacy 值也必须能重算 (从收口页登记的 legacy 口径反推)
    legacy = truth.get("legacy") or {}
    if "script_declared_stack_mm" in legacy:
        want = 31 * 0.5 + 22 * 0.5 + 0 * 0.5 + 10 * 0.5
        if abs(float(legacy["script_declared_stack_mm"]) - want) > TOL:
            prob3.append(f"legacy.script_declared_stack_mm={legacy['script_declared_stack_mm']} "
                         f"重算(31+22+0+10 全 0.5)={want}")
    if "script_recommended_stack_mm" in legacy:
        want = 16 * 0.5 + 20 * 0.5 + 4 * 0.5 + 10 * 0.5
        if abs(float(legacy["script_recommended_stack_mm"]) - want) > TOL:
            prob3.append(f"legacy.script_recommended_stack_mm={legacy['script_recommended_stack_mm']} "
                         f"重算(16+20+4+10 全 0.5)={want}")

    # 分片 claim: 新增的两条必须 == 重算值
    for key, got in (("mech_hinge_stack_truth_mm", prod_stack),
                     ("mech_hinge_stack_demo_mm", demo_stack)):
        v = claims.get(key)
        if v is None:
            prob3.append(f"分片缺 claim {key}")
        elif abs(float(v) - got) > TOL:
            prob3.append(f"分片 claim {key}={v} ≠ 重算 {got}")

    # ★收口页 claims 块里的两条新 claim 也必须 == 重算值 (ISS-240 补漏: 判据只加不减)★
    #   —— 收口页 claims 块 与 分片 interface_claims 是【两份载体】⇒ 两边都得能自己自证;
    #      以前只比分片 + computed 块 ⇒ ★收口页 claims 块被改成任何数, 门禁都看不见 ⇒ 假绿★
    truth_claims = truth.get("claims") or {}
    for key, got in (("mech_hinge_stack_truth_mm", prod_stack),
                     ("mech_hinge_stack_demo_mm", demo_stack)):
        v = truth_claims.get(key)
        if v is None:
            prob3.append(f"收口页 claims 块缺 {key}")
        else:
            try:
                fv = float(v)
            except (TypeError, ValueError):
                prob3.append(f"收口页 claims {key}={v!r} 不是数 (≠ 重算 {got})")
                continue
            if abs(fv - got) > TOL:
                prob3.append(f"收口页 claims {key}={v} ≠ 重算 {got}")

    # 旧 claim (25.00) 必须登记为差异 ⇒ 否则它是"假绿"
    fixed = claims.get("mech_hinge_stack_fixed_mm")
    if fixed is not None:
        if abs(float(fixed) - prod_stack) <= TOL:
            prob3.append(f"分片 claim mech_hinge_stack_fixed_mm={fixed} 与真源重算相同 ⇒ "
                         "它就不再是旧口径, 请同步更新收口页 legacy 块")
        if not any("mech_hinge_stack_fixed_mm" in (d.get("key") or "") for d in divs.values()):
            prob3.append("★分片 claim mech_hinge_stack_fixed_mm 未在收口页 legacy_divergences 登记 "
                         "(⇒ 25.00 这个假绿没人管)")
    ok3 = not prob3
    add("G3", "占位数与分片 claim 必须能从网表真源重算出来 (不比字面)", ok3,
        f"重算 demo: 高度 {demo_stack} mm ({'+'.join(str(int(c['pins'])) + '×' + str(c['pitch_mm']) for c in canon)}) "
        f"径向 {demo_radial} mm (3.00+{len(canon)}×0.35) 余 {demo_smar}/{demo_rmar} mm; "
        f"重算 整机: 高度 {prod_stack} mm 径向 {prod_radial} mm 余 {prod_smar}/{prod_rmar} mm; "
        f"分片 claim fixed={fixed} / truth={claims.get('mech_hinge_stack_truth_mm')} / "
        f"demo={claims.get('mech_hinge_stack_demo_mm')}; "
        f"收口页 claims truth={(truth_claims or {}).get('mech_hinge_stack_truth_mm')} / "
        f"demo={(truth_claims or {}).get('mech_hinge_stack_demo_mm')}; 问题 = "
        + ("无" if ok3 else "; ".join(prob3)))

    # ---------------- G4 正文旧口径裸命中 ----------------
    bare = bare_legacy_hits(doc_text)
    add("G4", "正文里的旧口径必须带 canonical 作废标注 (裸命中 = 红)", not bare,
        f"裸命中 {len(bare)} 处" + ("" if not bare else ": " + "; ".join(f"L{n} [{'/'.join(h)}]" for n, h, _ in bare[:8])))

    # ---------------- G5 正文现行口径行 ----------------
    lines = [ln for _, ln, _ in doc_lines_with_context(doc_text)]
    cam_ok = any(("31p" in ln) and ("0.3mm" in ln) and ("Radxa Camera 4K" in ln) for ln in lines)
    lit_ok = any(("22p" in ln) and ("0.5mm" in ln) and ("Waveshare 2.8inch" in ln) for ln in lines)
    add("G5", "正文里必须存在现行口径行 (31p/0.3mm + 22p/0.5mm)", cam_ok and lit_ok,
        f"31p/0.3mm (Radxa Camera 4K) 行 = {'有' if cam_ok else '★无'}; "
        f"22p/0.5mm (Waveshare 2.8inch) 行 = {'有' if lit_ok else '★无'}")

    # ---------------- G6 canonical 标注串存在 ----------------
    miss6 = [m for m in MARKERS if m not in doc_text]
    miss6t = [m for m in MARKERS if m not in truth_text]
    add("G6", "canonical 作废标注串本身必须能在正文里找到 (否则门禁自己失效没人知道)",
        not miss6 and not miss6t,
        f"正文缺 = {miss6 or '无'}; 收口页缺 = {miss6t or '无'}")

    # ---------------- G7 正文 demo 口径行 ----------------
    demo_line = any(("demo 板真跨铰链" in ln) and ("5.00" in ln) and ("3.35" in ln)
                    and ("33.00" in ln) and ("2.05" in ln) for ln in lines)
    add("G7", "正文里必须存在 demo 板真跨铰链口径行 (J_CHG 单链 5.00 / 3.35 ⇒ 余 33.00 / 2.05)",
        demo_line, f"demo 口径行 = {'有' if demo_line else '★无'}")

    # ---------------- G8 真源锚点齐全且没腐烂 ----------------
    anchors = ["HW/STEP1_PARTS_SPEC.md", "ISS-237", "HW/netlist_v1.csv", "board",
               "2026-11-02 19:25", "2026-11-11 19:31"]
    miss8 = [a for a in anchors if a not in truth_text]
    spec_ok = False
    spec_detail = "找不到裁定文件"
    if os.path.exists(SPEC):
        st = read(SPEC)
        spec_ok = ("ISS-237" in st) and ("31p" in st) and ("22p" in st)
        spec_detail = f"{os.path.basename(SPEC)} 含 ISS-237/31p/22p = {spec_ok}"
    add("G8", "收口页真源锚点齐全 + 被引用的裁定文件没腐烂",
        not miss8 and spec_ok,
        f"收口页缺锚点 = {miss8 or '无'}; {spec_detail}")

    # ---------------- G9 legacy 块记录的受保护脚本 md5 必须一致 ----------------
    ps = legacy.get("protected_script") or ""
    want_md5 = legacy.get("protected_script_md5") or ""
    got_md5 = ""
    if ps:
        p = os.path.join(PROJ, ps) if not os.path.isabs(ps) else ps
        if os.path.exists(p):
            got_md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    ok9 = bool(ps) and bool(want_md5) and got_md5 == want_md5
    add("G9", "legacy 块记录的受保护脚本 md5 必须与现文件一致 (脚本改过 ⇒ legacy 口径要重核)",
        ok9, f"{ps}: 记录 {want_md5 or '无'} / 实测 {got_md5 or '无'}")

    return res


# ================================================================= main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    net = load_netlist()
    truth, truth_text = load_truth()
    doc_text = read(DOC)
    claims = load_claims(FRAG)

    res = evaluate(net, truth, truth_text, doc_text, claims)

    print("=" * 96)
    print("MECH/check_hinge_fpc_truth.py —— 跨铰链 FPC 几何口径真值门禁 (ISS-240)")
    print("=" * 96)
    print(f"\n[输入] 网表 {os.path.relpath(NETLIST, PROJ)} (只读) · 收口页 {os.path.relpath(TRUTH, PROJ)} · "
          f"正文 {os.path.relpath(DOC, PROJ)} · 分片 {os.path.relpath(FRAG, PROJ)} (只读)")
    print(f"[输入] ★本门禁不 import / 不调用任何受保护脚本 ★")
    print(f"\n[重算] 网表 board 分布 = {net['board_hist']}")
    for r, s in sorted(net["seats"].items()):
        print(f"        FPC 座 {r:11s} = {s['pins']:>2}p @ {s['pitch']} mm  board={s['board']:9s} "
              f"(网表行 L{s['lines'][0]}…) 逐脚行数={net['pin_counts'].get(r, 0)}")
    print()
    fails = 0
    for r in res:
        flag = "PASS" if r["ok"] else "FAIL"
        if not r["ok"]:
            fails += 1
        print(f"[{flag}] {r['id']}  {r['name']}")
        print(f"       {r['detail']}")
    print("\n" + "=" * 96)
    if fails:
        print(f"[FAIL] {fails} / {len(res)} 项")
        print("\n结论: ❌ 口径没收干净 (先看收口页 T3 改法映射, 门禁本身不许放水)")
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        return 1
    print(f"[FAIL] 0 项 · 断言 {len(res)}/{len(res)} PASS")
    print("\n结论: ✅ 跨铰链 FPC 几何口径已收口到真源 (★实物 [实测] 条数 = 0 · 全部为网表/裁定块实测值驱动的 [推算]★)")
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


# ================================================================= 反向用例 (每条自证"真的改到了目标")
def selftest() -> int:
    net = load_netlist()
    truth, truth_text = load_truth()
    doc_text = read(DOC)
    claims = load_claims(FRAG)
    pristine = evaluate(net, truth, truth_text, doc_text, claims)

    def ok_ids(rs):
        return {r["id"]: r["ok"] for r in rs}

    base = ok_ids(pristine)

    # --- 变异器 ---
    def m_pitch(t):
        return t.replace("pitch_mm: 0.3", "pitch_mm: 0.5", 1)

    def m_drop_marker(d):
        # 删掉 CONN_CAM (40p) 那一行的 canonical 标注
        out = []
        for ln in d.splitlines():
            if "CONN_CAM` (40p)" in ln and any(m in ln for m in MARKERS):
                ln = ln.replace(MARK_PIN, "").replace(MARK_ARCH, "")
            out.append(ln)
        return "\n".join(out) + "\n"

    def m_claim_value(t):
        return t.replace('mech_hinge_stack_truth_mm: "25.30"', 'mech_hinge_stack_truth_mm: "26.00"', 1)

    def m_drop_marker_all(d):
        for mk in MARKERS:
            d = d.replace(mk, "")
        return d

    def m_drop_current_line(d):
        out = [ln for ln in d.splitlines()
               if not ("31p" in ln and "0.3mm" in ln and "Radxa Camera 4K" in ln)]
        return "\n".join(out) + "\n"

    def m_add_canon_link(t):
        anchor = "canonical_cross_hinge_links:      # board == HINGE 才算跨铰链 (demo 板)\n"
        return t.replace(anchor, anchor + "  - ref: CONN_CAM\n    pins: 31\n    pitch_mm: 0.3\n"
                           "    board: MAIN_PCB\n    netlist_line: 290\n", 1)

    def m_drop_demo_line(d):
        out = [ln for ln in d.splitlines() if not ("demo 板真跨铰链" in ln and "5.00" in ln)]
        return "\n".join(out) + "\n"

    def m_demo_value(t):
        return t.replace("demo_stack_mm: 5.0", "demo_stack_mm: 25.0", 1)

    def m_md5(t):
        return t.replace("protected_script_md5: 3425bc141508de8a35f34c7cf7b803e8",
                         "protected_script_md5: 00000000000000000000000000000000", 1)

    def m_board_width(d):
        out = []
        for ln in d.splitlines():
            if "12 mm 板宽" in ln and any(m in ln for m in MARKERS):
                ln = ln.replace(MARK_PIN, "").replace(MARK_ARCH, "")
            out.append(ln)
        return "\n".join(out) + "\n"

    cases = [
        ("T1", "把 camera 的 pitch 从 0.3 改成 0.5 (收口页机器块)", "G2", "G3",
         m_pitch, "truth", "pitch_mm: 0.3", "pitch_mm: 0.5"),
        ("T2", "把正文 CONN_CAM(40p) 那行的作废标记删掉", "G4", None,
         m_drop_marker, "doc", "CONN_CAM` (40p)", MARK_PIN),
        ("T3", "把 claim mech_hinge_stack_truth_mm 从 25.30 改成 26.00", "G3", None,
         m_claim_value, "truth", 'mech_hinge_stack_truth_mm: "25.30"', '"26.00"'),
        ("T4", "把正文里全部 canonical 标注串删掉", "G6", None,
         m_drop_marker_all, "doc", MARK_PIN, ""),
        ("T5", "把正文的现行口径行 (31p/0.3mm) 删掉", "G5", None,
         m_drop_current_line, "doc", "Radxa Camera 4K", ""),
        ("T6", "把 CONN_CAM 塞进 canonical 跨铰链清单 (它 board=MAIN_PCB)", "G1", None,
         m_add_canon_link, "truth", "canonical_cross_hinge_links:", "ref: CONN_CAM"),
        ("T7", "把正文的 demo 板真跨铰链口径行删掉", "G7", None,
         m_drop_demo_line, "doc", "demo 板真跨铰链", ""),
        ("T8", "把收口页 demo_stack_mm 从 5.0 改成 25.0", "G3", None,
         m_demo_value, "truth", "demo_stack_mm: 5.0", "demo_stack_mm: 25.0"),
        ("T9", "把收口页 legacy 块记录的受保护脚本 md5 改成假的", "G9", None,
         m_md5, "truth", "protected_script_md5: 3425bc141508de8a35f34c7cf7b803e8", "00000000"),
        ("T10", "把正文 12mm 板宽那行的作废标记删掉", "G4", None,
         m_board_width, "doc", "12 mm 板宽", MARK_PIN),
    ]

    print("=" * 96)
    print("MECH/check_hinge_fpc_truth.py --selftest —— 反向用例 (每条自证「真的改到了目标」)")
    print("=" * 96)

    # 控制组: 未变异时全部断言必须 PASS
    ctrl_fail = [r["id"] for r in pristine if not r["ok"]]
    print(f"\n[控制组] 未变异时 PASS = {len(pristine) - len(ctrl_fail)}/{len(pristine)}"
          + (f" ★FAIL: {ctrl_fail}" if ctrl_fail else " (全部 PASS)"))

    passed = 0
    lines_out = []
    for cid, desc, target, target2, mut, target_kind, before, after in cases:
        t2, d2 = truth_text, doc_text
        if target_kind == "truth":
            t2 = mut(truth_text)
        else:
            d2 = mut(doc_text)
        # 自证 1: 变异真的改了输入 (不是空变异)
        mutated = (t2 != truth_text) or (d2 != doc_text)
        # 自证 2: 变异后的目标断言必须变红
        truth2, truth_text2 = load_truth_from_text(t2), t2
        res2 = evaluate(net, truth2, truth_text2, d2, claims)
        o2 = ok_ids(res2)
        # 自证 3: 控制组里该断言原本是 PASS (变异前 green, 变异后 red)
        was_green = base.get(target, False)
        now_red = (o2.get(target) is False)
        also = ""
        if target2:
            also = f" · 连带 {target2}={'红' if o2.get(target2) is False else '绿'}"
        good = mutated and was_green and now_red
        if good:
            passed += 1
        lines_out.append(
            f"[{'PASS' if good else 'FAIL'}] {cid}  {desc}\n"
            f"         期望红 {target}{also} · 实测: 变异生效={mutated} 变异前绿={was_green} 变异后红={now_red}\n"
            f"         变异点: 「{before}」→「{after}」")
    print()
    for l in lines_out:
        print(l)
    print("\n" + "=" * 96)
    print(f"[selftest] 反向用例 {passed}/{len(cases)} 全抓到 (每条自证)")
    if passed != len(cases):
        print("\n结论: ❌ 有反向用例没抓到 (说明门禁有洞)")
        return 1
    print("\n结论: ✅ 反向用例全抓到 —— 门禁确实在判目标, 不是假用例")
    return 0


def load_truth_from_text(text: str) -> dict:
    import yaml
    block = extract_machine_block(text)
    try:
        return yaml.safe_load(block) or {}
    except Exception:
        return {}


if __name__ == "__main__":
    sys.exit(main())
