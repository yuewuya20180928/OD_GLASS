#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_demo_struct_truth.py —— ISS-213 结构侧真值门禁 (demo 板当前成立的条目)
=================================================================================
★**它守的不是"54 项全绿", 是"demo 板当前成立的条目不许变红 + 那 6 条 PCB 类
不许被静默 + 板框真源/判据阈值不许被偷改"** ★

为什么要有这个闸 (main 2026-11-15 23:2x~23:4x 实测):
  ① `MECH/hw_cross_review_check.py` 报 **PASS 14 / FAIL 17 / 条件通过 8 / 说明 15
     (共 54 项) 而 rc = 0** ⇒ 17 条"按现在的图纸/口径做出来会出问题"挂着, 一个红灯都不点;
  ② `state/daily_check.py` 里 grep 不到 `hw_cross_review` / `service_port` /
     `hinge_usb` / `display_biosafety` / `cavity_recalc` 任何一个 ⇒ **这 17 条在每日
     巡检里完全隐形** (本项目同类问题第三次复发);
  ⇒ 本闸 = **让这 17 条从"隐形"变成"有账"**: G1 专门断言那 17 条**仍然是 FAIL**
    (谁把它们"修绿" ⇒ 门禁立刻红), G3 断言 6 个 PCB 类 id **已登记排队** (不许静默)。

判据来源 (全部只读, 一个字不改):
  · `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 的 `MECH_ANCHORS` yaml 块 (本单写死的口径)
  · `MECH/BOARD_GEOM_30MM.md` §1 (板框真源四数)
  · `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` (判据阈值, **只 import 读常量**)
  · `HW/netlist_v1.csv` (网表实读)

用法:
    python3 MECH/check_demo_struct_truth.py               # rc=0 全过 / rc=2 有红
    python3 MECH/check_demo_struct_truth.py --selftest     # 反向用例: 改坏任一锚点必须变红
    python3 MECH/check_demo_struct_truth.py --json         # 机器可读输出

★**边界**: 本脚本 **只读** 任何文件; 不改 `MECH/hw_cross_review_check.py` /
  `MECH/service_port_check.py` / `MECH/hinge_usb_check.py` 的判据语义, 不改板框真源,
  不改判据阈值, 不碰 `HW/`, 不碰 `state/daily_check.py` (是否挂巡检由 main 裁)。
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TRIAGE = os.path.join(HERE, "HW_CROSS_REVIEW_TRIAGE.md")
BOARD_GEOM = os.path.join(HERE, "BOARD_GEOM_30MM.md")

# ★ 受保护文件 md5 (交卷前逐字节不变; 值来自任务书 + cavity_recalc_check.py 的 MD5_EXPECTED)
MD5_EXPECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/netlist_v1.csv": "c78f991283cc82d56c8e3dd31657c785",
    "HW/netlist_v1_pins.csv": "4814617e22b567d76164e56bc5e39dc8",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "MECH/hinge_usb_check.py": "3425bc141508de8a35f34c7cf7b803e8",
    "MECH/service_port_check.py": "9b24bf985764880f0105aee677fba6a8",
    "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
}

# ★ 6 个 PCB 类 id (排队等原理图定稿 —— 判定语义不许改, 只登记排队)
PCB_CLASS_IDS = ("STK-FANOUT", "PCB-X-GAP", "MRG-54P", "MRG-X-4", "MRG-X-3", "FRM-SUM")

# ★ 基准判定汇总 (hw_cross_review_check.py 迁移后基准)
BASE_SUMMARY = dict(pass_=14, fail=17, cond=8, info=15, total=54)

# ★ demo 板当前成立且必须 PASS 的项 (从 triage §2 判定表里摘出来的 PASS 项)
DEMO_PASS_IDS = ("STK-cav_v_-触点", "STK-cav_v_-FP", "RAD-fpc_t", "RAD-fpc_t_2oz", "PCB-Y",
                 "MRG-14P", "TOPO-2", "C1 铰链区 V 向", "C2 铰链区 H 向",
                 "C3 镜脚电芯段 V 向", "C4 主 PCB 段 H 向", "C5 镜脚 L 向")


# ====================================================================== 工具
def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: str, name: str):
    """只 import 读常量 (两个 check 脚本都是 `if __name__ == '__main__'` 保护的, 安全)。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_anchors(doc_text: str) -> dict:
    m = re.search(r"# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS", doc_text, re.S)
    if not m:
        raise SystemExit("[gate] 定性表里找不到 MECH_ANCHORS 块")
    import yaml
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict) or "anchors" not in data:
        raise SystemExit("[gate] MECH_ANCHORS 块格式不对")
    return data["anchors"]


def load_sources(root: str) -> dict:
    """从**只读**真源里独立读出判据/几何事实 (不读定性表的锚点)。"""
    sp = load_module(os.path.join(root, "MECH", "service_port_check.py"), "_sp_ref")
    hx = load_module(os.path.join(root, "MECH", "hw_cross_review_check.py"), "_hx_ref")
    bg = read_text(os.path.join(root, "MECH", "BOARD_GEOM_30MM.md"))
    sec1 = re.search(r"##\s*1\.\s*板框(.*?)(?=\n##\s)", bg, re.S)
    sec1 = sec1.group(1) if sec1 else ""
    facts = {
        "sp": dict(sp.BASE),
        "sp_crit": sp.CRIT,
        "sp_tol": dict(sp.TOL),
        "hx": dict(hx.BASE),
        "geom_sec1": sec1,
    }
    return facts


def normalize_item(item: str) -> str:
    """定性表里为了区分同名的两个实例加了后缀/括注, 归一化回脚本的原始项号。"""
    it = item.strip("`").strip()
    it = re.sub(r"\s*\(\d+\.\d+\)\s*$", "", it)     # STK-cav_v_-触点 (38.00) -> STK-cav_v_-触点
    if it.endswith("b"):                            # MRG-X-3b (深度上界 7.5 档) -> MRG-X-3
        it = it[:-1]
    return it


def parse_triage_rows(doc_text: str) -> list:
    """切出 §2 定性表, 逐行解出 (序号, 项号, 判定, 处置)。"""
    m = re.search(r"##\s*2\s*★\s*54 项逐条定性表(.*?)\n---\n\n##\s*3", doc_text, re.S)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        if not line.startswith("| **"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        num = cells[0].replace("*", "")
        item = cells[1].strip("`")
        verdict = cells[2]
        disp = cells[6].replace("*", "")
        rows.append(dict(num=num, item=item, base=normalize_item(item),
                         verdict=verdict, disp=disp))
    return rows


def parse_queue_rows(doc_text: str) -> dict:
    """切出 §4 排队表, 解出 {id: 恢复条件}。"""
    m = re.search(r"##\s*4\s*6 个 PCB 类 id 的排队表(.*?)\n---", doc_text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        item = cells[0].strip("`")
        resume = cells[-1]
        out.setdefault(item, "")
        out[item] = out[item] + " " + resume
    return out


def run_cross_review(root: str) -> dict:
    """实跑 hw_cross_review_check.py --json (只读, 不改它)。"""
    p = subprocess.run([sys.executable, os.path.join(root, "MECH", "hw_cross_review_check.py"),
                        "--json"], capture_output=True, text=True, cwd=root, timeout=300)
    txt = p.stdout
    i = txt.find('{\n  "results"')
    if i < 0:
        raise SystemExit("[gate] hw_cross_review_check.py --json 没吐 JSON:\n" + txt[-2000:])
    d = json.loads(txt[i:])
    return d


# ====================================================================== 检查组
def run_checks(root: str, anchors: dict, facts: dict, xrev: dict) -> list:
    """返回 [(组号, 组名, ok, 明细)]。anchors 可被 --selftest 篡改 ⇒ 反向用例。"""
    out = []
    A = anchors
    sp, hx = facts["sp"], facts["hx"]

    def g(code, name, ok, detail):
        out.append((code, name, bool(ok), detail))

    # ---------------- G1 不许把红灯调没 ----------------
    s = xrev["summary"]
    n_total = len(xrev["results"])
    g("G1", "不许把红灯调没 (FAIL 名单仍是 17 条)",
      s["pass"] == BASE_SUMMARY["pass_"] and s["fail"] == BASE_SUMMARY["fail"]
      and s["cond"] == BASE_SUMMARY["cond"] and s["info"] == BASE_SUMMARY["info"]
      and n_total == BASE_SUMMARY["total"],
      f"实测汇总 PASS {s['pass']} / FAIL {s['fail']} / 条件通过 {s['cond']} / "
      f"说明 {s['info']} (共 {n_total})")

    fail_ids = [r["id"] for r in xrev["results"] if r["verdict"] == "FAIL"]
    exp_fail = list(A.get("fail_expect", []))
    from collections import Counter
    same = Counter(fail_ids) == Counter(exp_fail)
    g("G1b", "FAIL 名单逐条对齐 (一条不许少/一条不许多)", same,
      f"实测 {len(fail_ids)} 条 vs 锚点 {len(exp_fail)} 条; 差集 "
      f"实测多={sorted((Counter(fail_ids)-Counter(exp_fail)).elements())} "
      f"锚点多={sorted((Counter(exp_fail)-Counter(fail_ids)).elements())}")

    # ---------------- G2 demo 板当前成立的条目全过 ----------------
    # G2-1 盖板内腔 (ISS-126 现口径)
    cavity = sp["h_outer_out"] - sp["h_pcb_face"]
    g("G2.1", "检修口盖板内腔 ≥ cavity_req (ISS-126 现口径)",
      cavity >= sp["cavity_req"] and abs(cavity - A["service_port"]["cavity_now"]) < 1e-9,
      f"内腔 = {sp['h_outer_out']} − {sp['h_pcb_face']} = {cavity:.2f}mm "
      f"vs 硬要求 {sp['cavity_req']:.2f} (余 {cavity - sp['cavity_req']:+.2f}); "
      f"锚点写 {A['service_port']['cavity_now']}")

    # G2-2 Type-C 开孔: 新口径两档在最坏公差下过判据, 两档现候选判不合格
    tc = A["typec_panel"]
    crit = A["thresholds"]["crit"]

    def worst_gap(op, body, tol):
        return (op - tol - body) / 2.0

    new_x = worst_gap(tc["new_opening_x"], tc["body_x"], tc["fdm_tol"])
    new_y = worst_gap(tc["new_opening_y"], tc["body_y"], tc["fdm_tol"])
    mt_x = worst_gap(tc["metal_opening_x"], tc["body_x"], 0.05)
    mt_y = worst_gap(tc["metal_opening_y"], tc["body_y"], 0.05)
    g("G2.2", "Type-C 新开孔口径最坏单边间隙 ≥ 判据 (FDM 直成型档)",
      new_x >= crit and new_y >= crit,
      f"{tc['new_opening_x']}×{tc['new_opening_y']} ⇒ 最坏 X {new_x:.2f} / Y {new_y:.2f} "
      f"vs 判据 {crit:.2f}")
    g("G2.3", "Type-C 金属/CNC 档最坏单边间隙 ≥ 判据 (±0.05)",
      mt_x >= crit and mt_y >= crit,
      f"{tc['metal_opening_x']}×{tc['metal_opening_y']} ⇒ 最坏 X {mt_x:.2f} / Y {mt_y:.2f} "
      f"vs 判据 {crit:.2f}")
    rej_bad = []
    for r in tc["rejected"]:
        gx = worst_gap(r["x"], tc["body_x"], tc["fdm_tol"])
        gy = worst_gap(r["y"], tc["body_y"], tc["fdm_tol"])
        rej_bad.append((r["name"], gx, gy))
    g("G2.4", "两档现候选 (打印包现试样) 判不合格 —— 证明'二选一'是假选择",
      all(gx < crit or gy < crit for _n, gx, gy in rej_bad),
      "; ".join(f"{n}: 最坏 X {gx:.2f} / Y {gy:.2f}" for n, gx, gy in rej_bad))

    # G2-5 端件温升口径 (buck) + P_max + 金属热路
    th = A["thermal"]
    dt = th["p_buck_w"] * th["r_conv_k_per_w"]
    surf = th["ambient_c"] + dt
    p_max = (th["surface_limit_c"] - th["ambient_c"]) / th["r_conv_k_per_w"]
    g("G2.5", "端件温升按 buck 口径 (Pin−Pout+DCR), 不用 MECH_BUDGET 的 0.8W 线性口径",
      abs(dt - 83.33) < 1.0 and abs(surf - 108.33) < 1.0,
      f"P={th['p_buck_w']:.2f}W × R={th['r_conv_k_per_w']:.2f} K/W ⇒ ΔT {dt:.1f}K ⇒ 表面 {surf:.1f}°C "
      f"(线性口径 {th['p_mech_linear_w']:.2f}W ⇒ ΔT {th['p_mech_linear_w']*th['r_conv_k_per_w']:.0f}K ⇒ "
      f"{th['ambient_c']+th['p_mech_linear_w']*th['r_conv_k_per_w']:.0f}°C)")
    g("G2.6", "60°C 判据 ⇒ 端件表面能吃下的最大耗散 P_max (现值必须超它 ⇒ 强制金属热路)",
      abs(p_max - th["p_max_w"]) < 0.01 and th["p_buck_w"] > p_max,
      f"P_max = ({th['surface_limit_c']:.0f}−{th['ambient_c']:.0f})/{th['r_conv_k_per_w']:.2f} "
      f"= {p_max:.3f}W; 现耗散 {th['p_buck_w']:.2f}W ⇒ 超 {th['p_buck_w']/p_max:.2f}× ⇒ 必须金属热路")
    g("G2.7", "散热路径必须是金属 (打印件 R 远大于铝)",
      th["r_print_k_per_w"] > 100 * th["r_alu_k_per_w"],
      f"打印件 {th['r_print_k_per_w']:.0f} K/W vs 铝 {th['r_alu_k_per_w']:.3f} K/W "
      f"(差 {th['r_print_k_per_w']/th['r_alu_k_per_w']:.0f}×) ⇒ 0.5W 打进去 "
      f"+{th['p_buck_w']*th['r_print_k_per_w']:.0f}K (打印件) vs "
      f"+{th['p_buck_w']*th['r_alu_k_per_w']:.2f}K (铝)")

    # G2-8 buck 功率守恒
    pw = A["power"]
    r37 = pw["eta"] * pw["v_bus"] / 3.70
    r42 = pw["eta"] * pw["v_bus"] / 4.20
    g("G2.8", "buck 功率守恒 ICHG/IIN = η·Vbus/Vbat (规格书的 0.822/0.933 是倒数)",
      abs(r37 - pw["ratio_370"]) < 5e-4 and abs(r42 - pw["ratio_420"]) < 5e-4,
      f"3.70V ⇒ {r37:.3f} (锚点 {pw['ratio_370']}) · 4.20V ⇒ {r42:.3f} (锚点 {pw['ratio_420']}); "
      f"规格书倒数 = {3.70/pw['v_bus']/pw['eta']:.3f} / {4.20/pw['v_bus']/pw['eta']:.3f}")

    # G2-9 demo 当前必须 PASS 的项
    by_id = {}
    for r in xrev["results"]:
        by_id.setdefault(r["id"], []).append(r["verdict"])
    bad_pass = [i for i in DEMO_PASS_IDS if not any(v == "PASS" for v in by_id.get(i, []))]
    g("G2.9", "demo 当前成立的 PASS 项 (公差链 C1~C5 / 径向 / 堆叠余量 / 合并 14P / 拓扑 B) 全过",
      not bad_pass, f"共 {len(DEMO_PASS_IDS)} 项, 不再 PASS 的 = {bad_pass or '无'}")

    # ---------------- G3 6 条 PCB 类已登记排队 (不许静默) ----------------
    doc = read_text(os.path.join(root, "MECH", "HW_CROSS_REVIEW_TRIAGE.md"))
    q = parse_queue_rows(doc)
    missing = [i for i in PCB_CLASS_IDS if not q.get(i, "").strip()]
    in_anchor = [i for i in PCB_CLASS_IDS if i not in A.get("pcb_class_queued", [])]
    g("G3", "6 个 PCB 类 id 已登记排队且恢复条件非空 (不许静默丢弃)",
      not missing and not in_anchor,
      f"排队表缺恢复条件的 = {missing or '无'}; 锚点 pcb_class_queued 缺的 = {in_anchor or '无'}")
    # 排队的这 6 个 id 必须**仍然是 FAIL** (不许被"修绿")
    still_fail = [i for i in PCB_CLASS_IDS if "FAIL" not in by_id.get(i, [])]
    g("G3b", "排队的 PCB 类 id 在 hw_cross_review_check.py 里仍然是 FAIL (不许修绿)",
      not still_fail, f"不再是 FAIL 的 = {still_fail or '无'}")

    # ---------------- G4 板框真源四数不变 ----------------
    sec1 = facts["geom_sec1"]
    bg = A["board_geom"]
    four = [("板长 X", bg["board_len_x"], "60.00mm", "板长 X"),
            ("板宽 Y", bg["board_width_y"], "30.00mm", "板宽 Y"),
            ("板厚", bg["board_thickness"], "1.00mm", "板厚"),
            ("板重", bg["board_mass_g"], "3.33g", "板重")]
    miss4 = [n for n, v, tok, _lbl in four if tok not in sec1]
    mism4 = [f"{n}: 锚点 {v} vs 文档要求 {tok}" for n, v, tok, _lbl in four
             if abs(float(v) - float(tok.replace("mm", "").replace("g", ""))) > 1e-9]
    g("G4", "MECH/BOARD_GEOM_30MM.md §1 四数 (60.00/30.00/1.00/3.33g) 一个没被改",
      not miss4 and not mism4,
      f"§1 缺失项 = {miss4 or '无'}; 锚点与文档不一致 = {mism4 or '无'}")
    # 板框四数还要与 hw_cross_review_check.py / service_port_check.py 的口径一致
    g("G4b", "板框四数与两个 check 脚本的现行口径一致 (pcb_len/pcb_w/pcb_thk)",
      abs(hx["pcb_len"] - bg["board_len_x"]) < 1e-9
      and abs(hx["pcb_w"] - bg["board_width_y"]) < 1e-9
      and abs(sp["pcb_thk"] - bg["board_thickness"]) < 1e-9,
      f"脚本 pcb_len={hx['pcb_len']} / pcb_w={hx['pcb_w']} / pcb_thk={sp['pcb_thk']} "
      f"vs 锚点 {bg['board_len_x']}/{bg['board_width_y']}/{bg['board_thickness']}")

    # ---------------- G5 判据阈值一个没松 ----------------
    th_anchor = A["thresholds"]
    g("G5", "判据阈值未松: cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00",
      abs(sp["cavity_req"] - th_anchor["cavity_req"]) < 1e-9
      and abs(sp["cav_v"] - th_anchor["cav_v"]) < 1e-9
      and abs(sp["duct_v"] - th_anchor["duct_v"]) < 1e-9
      and abs(facts["sp_crit"] - th_anchor["crit"]) < 1e-9
      and abs(hx["judge"] - th_anchor["crit"]) < 1e-9
      and abs(hx["cav_v_now"] - th_anchor["cav_v"]) < 1e-9,
      f"service_port: cavity_req={sp['cavity_req']} cav_v={sp['cav_v']} duct_v={sp['duct_v']} "
      f"CRIT={facts['sp_crit']:.2f}; hw_cross_review: judge={hx['judge']} cav_v_now={hx['cav_v_now']}")
    badmd5 = []
    for rel, want in MD5_EXPECTED.items():
        got = md5(os.path.join(root, rel))
        if got != want:
            badmd5.append(f"{rel}: {got} != {want}")
    g("G5b", "受保护文件 md5 逐字节未变 (板/网表/脚表/.kicad_pro + 3 个 check 脚本)", not badmd5,
      "; ".join(badmd5) if badmd5 else f"{len(MD5_EXPECTED)} 个文件全部一致")

    # ---------------- G6 定性表 54/54 + 处置不留空 ----------------
    rows = parse_triage_rows(doc)
    items = [r["base"] for r in rows]
    src_ids = [r["id"] for r in xrev["results"]]
    from collections import Counter as _C
    miss_items = sorted((_C(src_ids) - _C(items)).elements())
    extra_items = sorted((_C(items) - _C(src_ids)).elements())
    empty_disp = [r["item"] for r in rows if not r["disp"].strip() or "待定" in r["disp"]]
    g("G6", "定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'",
      len(rows) == BASE_SUMMARY["total"] and not miss_items and not extra_items and not empty_disp,
      f"表内 {len(rows)} 行 / 应 {BASE_SUMMARY['total']}; 缺项号 = {miss_items or '无'}; "
      f"多余项号 = {extra_items or '无'}; 处置留空或待定 = {empty_disp or '无'}")
    # 17 条 FAIL 每条都有明确去处
    fail_rows = [r for r in rows if "FAIL" in r["verdict"]]
    ok_disp = ("维持现状", "出规格", "修掉", "登记 need 给 main", "排队等原理图定稿")
    no_dest = [r["item"] for r in fail_rows if r["disp"].strip() not in ok_disp]
    g("G6b", "17 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)",
      len(fail_rows) == BASE_SUMMARY["fail"] and not no_dest,
      f"FAIL 行 {len(fail_rows)} 条; 去处不在受控词表里的 = {no_dest or '无'}")

    # ---------------- G7 分片账 (ISS-206 U-3) ----------------
    import yaml
    frag = os.path.join(root, "state", "fragments", "mech.yaml")
    fixed = None
    if os.path.exists(frag):
        d = yaml.safe_load(read_text(frag)) or {}
        for c in (d.get("interface_claims") or []):
            if c.get("key") == "mech_hinge_stack_fixed_mm":
                fixed = str(c.get("value"))
    g("G7", "分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)",
      fixed == "25.00", f"实测 value = {fixed}")

    return out


# ====================================================================== selftest
def selftest(root: str, anchors: dict, facts: dict, xrev: dict) -> int:
    base = run_checks(root, anchors, facts, xrev)
    base_bad = [c for c in base if not c[2]]
    cases = []

    def mut(name, fn, expect):
        a = copy.deepcopy(anchors)
        fn(a)
        cases.append((name, a, expect))

    mut("反向1: 板宽锚点 30.00 → 15.00 (旧板宽)",
        lambda a: a["board_geom"].__setitem__("board_width_y", 15.00), "G4")
    mut("反向2: 判据 CRIT 0.60 → 0.30 (松判据)",
        lambda a: a["thresholds"].__setitem__("crit", 0.30), "G5")
    mut("反向3: 新开孔 10.50 → 9.50 (退回到不合格的现口径)",
        lambda a: a["typec_panel"].__setitem__("new_opening_x", 9.50), "G2.2")
    mut("反向4: buck 耗散 0.50 → 0.15 (假装不需要金属热路)",
        lambda a: a["thermal"].__setitem__("p_buck_w", 0.15), "G2.6")
    mut("反向5: FAIL 名单里删掉 NET-LED (把红灯调没)",
        lambda a: a.__setitem__("fail_expect", [x for x in a["fail_expect"] if x != "NET-LED"]), "G1b")
    mut("反向6: 排队表里删掉 FRM-SUM (静默丢弃排队条目)",
        lambda a: a.__setitem__("pcb_class_queued",
                                [x for x in a["pcb_class_queued"] if x != "FRM-SUM"]), "G3")
    mut("反向7: 板重 3.33 → 3.30 (板框真源被偷改)",
        lambda a: a["board_geom"].__setitem__("board_mass_g", 3.30), "G4")
    mut("反向8: cavity_req 4.50 → 5.00 (松硬要求)",
        lambda a: a["thresholds"].__setitem__("cavity_req", 5.00), "G5")

    print("=" * 100)
    print("ISS-213 机器门禁 —— 反向用例 (改坏任一锚点必须变红)")
    print("=" * 100)
    if base_bad:
        print(f"❌ 基线就不绿: {[c[0] for c in base_bad]} ⇒ 门禁本身有问题, 自测不成立")
        return 2
    print(f"  ✅ 基线全绿 ({len(base)}/{len(base)} 组检查)")
    ok = 0
    for name, a, expect in cases:
        res = run_checks(root, a, facts, xrev)
        red = [c[0] for c in res if not c[2]]
        hit = expect in red
        flag = "✅" if hit else "❌"
        if hit:
            ok += 1
        print(f"  {flag} {name:<48} 期望红组 {expect:<6} 实际红组 {red or '无'}")
    print("-" * 100)
    print(f"反向用例: {ok}/{len(cases)} 抓到了")
    return 0 if ok == len(cases) else 2


# ====================================================================== main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="反向用例: 改坏任一锚点必须变红")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = read_text(TRIAGE)
    anchors = load_anchors(doc)
    facts = load_sources(PROJ)
    xrev = run_cross_review(PROJ)

    if args.selftest:
        return selftest(PROJ, anchors, facts, xrev)

    res = run_checks(PROJ, anchors, facts, xrev)
    print("=" * 100)
    print("ISS-213 结构侧真值门禁 (demo 板当前成立的条目 + 板框/阈值/红灯保护)")
    print("=" * 100)
    print(f"定性表: MECH/HW_CROSS_REVIEW_TRIAGE.md  |  源: MECH/service_port_check.py + "
          f"MECH/hw_cross_review_check.py + MECH/BOARD_GEOM_30MM.md")
    print("-" * 100)
    for code, name, ok, detail in res:
        print(f"  [{'OK ' if ok else 'FAIL'}] {code:<5} {name}")
        print(f"         {detail}")
    npass = sum(1 for r in res if r[2])
    print("-" * 100)
    print(f"【结论】{npass}/{len(res)} 组检查通过 | FAIL {len(res)-npass} 组")
    print("口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。")
    print("          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。")
    print("          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。")
    print("=" * 100)
    if args.json:
        print(json.dumps({"checks": [{"code": c, "name": n, "ok": o, "detail": d}
                                      for c, n, o, d in res],
                          "summary": {"pass": npass, "total": len(res)}},
                         ensure_ascii=False, indent=2))
    return 0 if npass == len(res) else 2


if __name__ == "__main__":
    sys.exit(main())
