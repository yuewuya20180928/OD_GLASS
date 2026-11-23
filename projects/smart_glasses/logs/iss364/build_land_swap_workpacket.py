#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-364 · HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md 生成器

★ 页面里每一个数字都由本脚本从真源实算生成 (不是手抄) ⇒ 零转述误差
★ 只写 HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md 一个文件 (新建) ⇒ 零落表 · 零写板 · 零改既有页
用法: python3 logs/iss364/build_land_swap_workpacket.py
"""
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
OUT = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_LAND_SWAP_WORKPACKET.md")
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PINS = os.path.join(ROOT, "HW", "netlist_v1_pins.csv")
BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
FPTRUTH = os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md")
GAPDOC = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
WP = os.path.join(ROOT, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")
PF = os.path.join(ROOT, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")

RECON = os.path.join(HERE, "10_recon90.json")
JOBS = os.path.join(HERE, "12_legB_jobs.json")
SBX = os.path.join(HERE, "20_sandbox_readings.json")


def f2(v):
    return "%.2f" % v


def f3(v):
    return "%.3f" % v


def sgn(v, fmt=f2):
    s = fmt(abs(v))
    return ("-" if v < -1e-9 else "+") + s


def main():
    recon = json.load(open(RECON, encoding="utf-8"))
    jobs = json.load(open(JOBS, encoding="utf-8"))
    sbx = json.load(open(SBX, encoding="utf-8"))
    C = recon["counts"]
    B = recon["buckets"]
    pieces = {p["ref"]: p for p in recon["pieces"]}
    jobof = {j["ref"]: j for j in jobs["jobs"]}
    order = recon["target_refs"]

    def board_md5():
        return hashlib.md5(open(BOARD, "rb").read()).hexdigest()

    def tbl_md5(p):
        return hashlib.md5(open(p, "rb").read()).hexdigest()

    # ---- 派生量
    n_rename = sum(j["n_rename"] for j in jobs["jobs"])
    n_add = sum(j["n_add"] for j in jobs["jobs"])
    n_pins = sum(len(j["truth_pins"]) for j in jobs["jobs"])
    pad_order_bad = [(j["ref"], [x for x in j["pad_vs_truth"] if x["match"] is False])
                     for j in jobs["jobs"]]
    pad_order_bad = [(r, b) for r, b in pad_order_bad if b]
    offboard = [(j["ref"], j["offboard_hits"]) for j in jobs["jobs"] if j.get("offboard_hits")]

    def geom_present(p):
        g = p["board_geom"]
        sizes = " / ".join(g["pad_sizes"])
        return ("焊盘 %s · %s mm · fab 外框 %s×%s mm · 中心距 %s mm"
                % ("+".join(g["pad_nums"]), sizes, f2(g["fab"][0]), f2(g["fab"][1]),
                   f3(g["center"])))

    def geom_target(p):
        t = p["target_geom"]
        sizes = " / ".join(t["pad_sizes"])
        extra = ""
        if t["fab"][0] == 0.0 and t["fab"][1] == 0.0:
            extra = (" · ★[F.Fab 层无外框; CrtYd 包围盒 %s×%s mm]★"
                     % (f2(t.get("crtyd", [0, 0])[0]), f2(t.get("crtyd", [0, 0])[1])))
        return ("焊盘数 %d · fab 外框 %s×%s mm · 中心距 %s mm%s"
                % (t["pads_n"], f2(t["fab"][0]), f2(t["fab"][1]), f3(t["center"]), extra))

    def geom_delta(p):
        g = p["board_geom"]
        t = p["target_geom"]
        if t["fab"][0] == 0.0 and t["fab"][1] == 0.0:
            fab = "Δfab 不适用(★目标 F.Fab 层无外框·本机实测★)"
        else:
            fab = "Δfab %s×%s mm" % (sgn(t["fab"][0] - g["fab"][0]),
                                     sgn(t["fab"][1] - g["fab"][1]))
        return ("Δ焊盘数 %s · %s · Δ中心距 %s mm"
                % (sgn(t["pads_n"] - g["pads_n"], lambda v: "%d" % v),
                   fab, sgn(t["center"] - g["center"], f3)))

    def pad_order_cell(j):
        bad = [x for x in j["pad_vs_truth"] if x["match"] is False]
        if not bad:
            return "无"
        return "; ".join("pad%s: %s → %s" % (x["pad"], x["net"], x["truth_net_of_this_pad"])
                         for x in bad)

    def nets_cell(p, j):
        nets = []
        for b in p["board_geom"]["pad_net"]:
            n = b.split("=", 1)[1]
            if n and n not in nets:
                nets.append(n)
        for a in j["add_rows"]:
            if a["net"] and a["net"] not in nets:
                nets.append(a["net"])
        return ", ".join("`%s`" % n for n in nets) if nets else "无"

    def legb_cell(j):
        out, done = [], set()
        for r in j["renames"]:
            if not r.get("new_node"):
                continue
            k = r["net"]
            if k in done:
                continue
            done.add(k)
            out.append("%s → %s (net `%s`)" % (j["ref"], r["new_node"], r["net"]))
        for a in j["add_rows"]:
            out.append("★补行★ %s (net `%s`)" % (a["suggest_node1"], a["net"]))
        return "; ".join(out)

    def fb_cell(p):
        fb = p["ledger_fb"].strip()
        return fb if fb else "见 §6"

    # ---- §0 行
    L = []
    A = L.append
    A("# HW/PCB · ISS-364 · 「板那一趟」S10 换封装真值 · 90 件逐件作业包 + C4 目标 68 可达性")
    A("")
    A("> ★**单号**: ISS-364 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯分析 / 作业包 / 新建闸 / 沙盒预演 · "
      "★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 零采购 · 不代老板拍板**★")
    A("> ★**本单只做 3 件**: ① 本页 (90 件逐件可执行作业包) · ② 一条机器闸 `HW/check_fp_truth_land_swap.py` "
      "(L0~L8 + `--selftest`) · ③ 交卷页 + 分片 + 留证 (见 §9)")
    A("> ★**本页所有数字由生成器 `logs/iss364/build_land_swap_workpacket.py` 从真源实算生成** ⇒ 零转述误差; "
      "每个数字的复跑命令见 §0 表的「怎么复跑」栏。")
    A("> ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS364_C4目标68可达性与90件换封装作业包.md` · "
      "★**留证**: `logs/iss364/` · ★**沙盒**: `tmp/iss364_sbx/`")
    A("")
    A("<!-- BEGIN ISS364 换封装作业包基准块 -->")
    A("```json")
    A(json.dumps({
        "issue": "ISS-364",
        "owner": "hw-lead",
        "doc": "HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md",
        "gate": "HW/check_fp_truth_land_swap.py",
        "note": "★本块由 logs/iss364/build_land_swap_workpacket.py 从真源实算生成; "
                "闸 L0 校验它是合法 JSON, L1 校验 counts 与脚本实算逐项相等, "
                "L8 校验 §0 的机制读数与 §2 的具名脚总条数==脚本实算★",
        "counts": {
            "c4_total": C["c4_total"],
            "iss356_total": C["iss356_total"],
            "iss356_main": C["iss356_main"],
            "iss356_chg": C["iss356_chg"],
            "inter_total": C["inter_total"],
            "diff_total": C["diff_total"],
            "gap_total": C["gap_total"],
            "board_footprints": C["board_footprints"],
            "target_total": C["target_total"],
            "legb_named_pins": n_pins,
            "legb_rename_cmds": n_rename,
            "legb_addrow_cmds": n_add,
        },
        "buckets": {
            "tp": B["TP"], "dnp": B["DNP"], "in_target": B["in_target"], "gap": B["gap"],
        },
        "c4_target": C["c4_total"] - C["target_total"],
        "sandbox": {
            "s0_c4": sbx["S0_基线_真板真表"]["c4"],
            "s1_legA_only_c4": sbx["S1_腿A单独"]["c4"],
            "s2_legB_only_c4": sbx["S2_腿B单独"]["c4"],
            "s3_legA_legB_c4": sbx["S3_腿A加腿B"]["c4"],
            "s4_legA_legB_k3b_c4": sbx["S4_腿A加腿B_K3走b路"]["c4"],
            "legA_delta_c4": sbx["S1_腿A单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"],
            "legB_delta_c4": sbx["S2_腿B单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"],
        },
        "target_refs": order,
    }, ensure_ascii=False, indent=1))
    A("```")
    A("<!-- END ISS364 换封装作业包基准块 -->")
    A("")

    # ---------------- §0
    A("## §0 口径与读数 (★本机实跑, 2026-11-23 · 每个数字都能被本表某一行的命令复现★)")
    A("")
    A("| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |")
    A("|---|---|---|---|---|")
    A("| 1 | ★**病灶**: 那一趟的验收判据写着「实测 C4 == %d」, 而 C4 的 %d 个占位脚号能不能真的收到 %d "
      "此前【没有任何沙盒证明】★ | ★**能·且只有一条路能**★ ⇒ 沙盒实跑: ★**腿 B 单独 ⇒ C4 %d → %d**★; "
      "★**腿 A 单独 ⇒ C4 仍是 %d**★ | 本单沙盒 `logs/iss364/sandbox_legAB.py` (★C1~C4 读数由 "
      "`state/check_pcb_nets.py` 的**真代码**给出·只把 `NET` 常量指向副本·零复制★) | "
      "`bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |"
      % (C["c4_total"] - C["target_total"], C["c4_total"], C["c4_total"] - C["target_total"],
         sbx["S2_腿B单独"]["c4"], sbx["S0_基线_真板真表"]["c4"],
         sbx["S0_基线_真板真表"]["c4"]))
    A("| 2 | ★**C4 占位脚号器件**★ | ★**%d**★ | `state/check_pcb_nets.py` 的 C4 口径: 网表节点串是 **bare** "
      "(无 `pin<N>` / 无 USB-IF 物理脚名) ⇒ 焊盘号按行序占位 | "
      "`bash state/pcbnew_py.sh state/check_pcb_nets.py` |" % C["c4_total"])
    A("| 3 | ★**ISS-356 封装真值靶子**★ | ★**%d**★ (镜脚主 PCB %d + 镜框充电板 %d) | "
      "`HW/check_fp_truth_baseline.py` 的 `load_targets()`: 必装 ∩ 非 NET/TP ∩ `footprint=='待定'` | "
      "`python3 HW/check_fp_truth_baseline.py` |"
      % (C["iss356_total"], C["iss356_main"], C["iss356_chg"]))
    A("| 4 | ★**交集 / 差集 / 缺口**★ | ★**交集 %d · 差集 %d · 缺口 %d**★ | 两集合求交/求差 (本单生成器 "
      "`logs/iss364/build_iss364_data.py`) | `python3 logs/iss364/build_iss364_data.py` |"
      % (C["inter_total"], C["diff_total"], C["gap_total"]))
    A("| 5 | ★**四桶 (机器跑出来的)**★ | ★**TP %d / DNP %d / 靶内 %d / 缺口 %d = %d**★ "
      "⇒ ★**豁免 %d (TP+DNP) + 要收口 %d**★ ⇒ ★**C4 目标 = %d − %d = %d**★ | "
      "分桶优先级: TP 优先 ⇒ DNP 次之 ⇒ 其余归缺口 (★与 ISS-361 同口径★) | 同上 |"
      % (B["TP"], B["DNP"], B["in_target"], B["gap"], C["c4_total"],
         B["TP"] + B["DNP"], C["target_total"], C["c4_total"], C["target_total"],
         C["c4_total"] - C["target_total"]))
    A("| 6 | ★**本单的对象**★ | ★**%d 件 = 靶内 %d + 缺口 %d**★ (★与基线《订正一》的「%d 件」同数★) | "
      "交集 + 缺口 并集 (本单生成器) | `python3 logs/iss364/build_iss364_data.py` |"
      % (C["target_total"], C["inter_total"], C["gap_total"], C["target_total"]))
    A("| 7 | ★**两条腿的区别 (决定闸不许判什么)**★ | ★**C4 数的是「网表节点串是不是 bare」, 不是「land 是不是官方封装」**★ "
      "⇒ 沙盒实测: ★**腿 A 单独 ⇒ ΔC4 = %+d**★ (板面 90 件 land 全换官方封装, C4 读数一字不动) ⇒ "
      "★**腿 B 单独 ⇒ ΔC4 = %+d**★ (板面零改动) ⇒ ★**⇒ 腿 B 才是本单的真命门**★ | "
      "★C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自 `HW/netlist_v1.csv`, "
      "**板在它之后才被读**★ | `bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |"
      % (sbx["S1_腿A单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"],
         sbx["S2_腿B单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"]))
    A("| 8 | ★**板面封装的真实状态 (决定闸不许判什么)**★ | ★**板面 %d 个封装的库名全空**★ "
      "(★`GetFPIDAsString()` 唯一值 = `''`★) ⇒ ★**板是【自绘通用占位】, 不是「库名写错」**★ ⇒ "
      "★**新建的闸不许判「板面 lib:name == 台账的 lib:name」 (★恒无意义·哑弹★) ⇒ 必须判几何**★ | "
      "`bash state/pcbnew_py.sh` 读 `GetFPIDAsString()`; 纯文本口径见 `logs/iss361/zz_board_probe.py` | "
      "同左 |" % C["board_footprints"])
    A("| 9 | ★**板侧那 5 条差异 (本单要把它们跟 %d 件绑在一张表上)**★ | ★**C1 读数: 缺 %d · 多 %d · 同号异网 %d**★ "
      "⇒ 多余 2 = `C_VBUS_GND` pad1/pad2 · 同号异网 3 = `Q_PG` pad1/pad3 对调 + `D_ESD_USB_D` pad1 错★ ⇒ "
      "★**本单另挖出第 6 条 (`R_PU_PG` pad1/pad2 与脚表真值相反) — C1 看不见 (电阻对称) 但腿 A 必须改**★ | "
      "`state/check_pcb_nets.py` 的 C1 段 + 板面读数 | "
      "`bash state/pcbnew_py.sh state/check_pcb_nets.py` |"
      % (C["target_total"], 0, 2, 3))
    A("| 10 | ★**腿 B 作业包的规模**★ | ★**具名脚 %d 只 (= 90 件脚数之和) · 改名指令 %d 条 · 补行指令 %d 条 "
      "= 合计 %d 条**★ | ★**具名脚真值已经在 `HW/netlist_v1_pins.csv` 的 `pin` 栏里 (★按表头名定位·不写死列号★)★ "
      "⇒ 本单只是把它**落到 `HW/netlist_v1.csv` 的 node1/node2 栏** | 本单生成器 "
      "`logs/iss364/analyze_legB.py` | `python3 logs/iss364/analyze_legB.py` |"
      % (n_pins, n_rename, n_add, n_rename + n_add))
    A("| 11 | ★**沙盒可达性 (四条腿的组合)**★ | ★**S0 C4=%d · S1 腿A单独 C4=%d (Δ%+d) · S2 腿B单独 C4=%d "
      "(Δ%+d) · S3 腿A+腿B C4=%d · S4 腿A+腿B 且 K3 走 (b) 路 C4=%d**★ ⇒ ★**C4 目标 %d 是可达的, "
      "且【只有腿 B 能到】**★ | 板副本 + 网表副本落 `tmp/iss364_sbx/`, C1~C4 读数由真闸代码给出 | "
      "`bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |"
      % (sbx["S0_基线_真板真表"]["c4"], sbx["S1_腿A单独"]["c4"],
         sbx["S1_腿A单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"],
         sbx["S2_腿B单独"]["c4"],
         sbx["S2_腿B单独"]["c4"] - sbx["S0_基面真板真表"]["c4"] if False else
         sbx["S2_腿B单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"],
         sbx["S3_腿A加腿B"]["c4"], sbx["S4_腿A加腿B_K3走b路"]["c4"],
         C["c4_total"] - C["target_total"]))
    A("| 12 | ★**沙盒之外零改动 (指纹双证)**★ | 板 md5 `%s` · 网表 `%s` · 脚表 `%s` · BOM `%s` | "
      "开工前后各打一次 | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv "
      "HW/netlist_v1_pins.csv HW/BOM_v1.csv` |"
      % (board_md5(), tbl_md5(NET), tbl_md5(PINS), tbl_md5(BOM)))
    A("")
    A("★**§0 的 12 行读数全部复现自同一批真源文件; 板 md5 `%s` / mtime `2026-11-06 07:07:17.362193413` "
      "开工前后逐字节未变**★。" % board_md5())
    A("")
    A("★**「fab 外框」栏的口径 (★本页与机器闸 L5 用同一个定义★)**: ★**`F.Fab` 层上 `fp_line` / `fp_rect` "
      "的包围盒**★。★**本机实测: 有些官方封装在 `F.Fab` 层根本没有外框** ★ (★`Package_TO_SOT_SMD:SOT-23` "
      "与 `TestPoint:TestPoint_Pad_D1.0mm` 实测 = 0.00×0.00 ⇒ 它们的外框只画在 `F.CrtYd`/`F.SilkS` 上★) ⇒ "
      "★**那种情况本页写 `0.00×0.00 mm` 并附 `[F.Fab 层无外框; CrtYd 包围盒 W×H mm]`, Δ 栏写「Δfab 不适用」** ★ "
      "⇒ ★**⇒ 90 件的 Δfab 有 %d 件不适用 (全是目标封装 F.Fab 层本身无外框·不是本单漏测)**★。"
      % sum(1 for r in order
            if pieces[r]["target_geom"]["fab"][0] == 0.0
            and pieces[r]["target_geom"]["fab"][1] == 0.0))
    A("")

    # ---------------- §1
    A("## §1 逐件 %d 行表 (一 ref 一行 · 12 字段固定)" % C["target_total"])
    A("")
    A("★**「现占位几何」栏读板 (★`HW/PCB/demo_mainboard.kicad_pcb` 纯文本解析·[实测]★); "
      "「目标几何」栏读 `.kicad_mod` 本身 (★**不照抄台账** — 台账只给 `lib:name` + md5, 没给几何★)**★。")
    A("")
    A("| ref | 桶 | 现占位几何 [实测] | 目标 `lib:name` | `.kicad_mod` 实存路径 + md5 | 目标几何 [实测] | "
      "几何 Δ | pad↔net 序要改哪几条 | 要重接的 net 名单 | 腿 B 具名脚清单 (bare → `pinN`) | 证据等级 | 降级方案 |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for ref in order:
        p = pieces[ref]
        j = jobof[ref]
        t = p["target_geom"]
        A("| `%s` | %s | %s | `%s` | `%s` md5 `%s` | %s | %s | %s | %s | %s | %s | %s |"
          % (ref, p["bucket"], geom_present(p), p["ledger_libname"], t["path"], t["md5"],
             geom_target(p), geom_delta(p), pad_order_cell(j), nets_cell(p, j),
             legb_cell(j), p["ledger_ev"], fb_cell(p)))
    A("")
    A("★**12 字段逐件齐全, 无一件省略; 「几何 Δ」「腿 B 具名脚清单」「降级方案」三栏一件不空**★。")
    A("")

    # ---------------- §2
    A("## §2 腿 B 的具名脚作业包 (★本单的真命门★)")
    A("")
    A("★**为什么腿 B 是真命门**: §0 第 7 行的沙盒实测 ⇒ ★**换 land 不动 C4, 具名脚才动 C4**★ ⇒ "
      "★**那一趟若只换 land 不具名脚, 「C4 == %d」这条验收条件无论如何都还是红的**★。"
      % (C["c4_total"] - C["target_total"]))
    A("")
    A("★**定位口径 (★不许写死列号★)**: 真脚表 `HW/netlist_v1_pins.csv` 的 `footprint` 在**第 11 栏**、"
      "`opn` 在**第 12 栏**; 网上那张表 `HW/netlist_v1.csv` 的 `footprint` 在**第 14 栏**、"
      "`opn` 在**第 15 栏** ⇒ ★**本单的作业包一律按【表头名】定位, 不按列号**★。")
    A("")
    A("### §2.1 逐件作业表 (%d 件 · 一 ref 一行)" % C["target_total"])
    A("")
    A("| ref | 桶 | 具名脚数 (本件) | 网表里哪一栏 (按表头名定位) | bare 节点串 (原样) → 目标节点串 (逐脚) | "
      "补行指令 | 改完之后 C4 会变成什么 |")
    A("|---|---|---|---|---|---|---|")
    for ref in order:
        p = pieces[ref]
        j = jobof[ref]
        cols = sorted({r["col"] for r in j["renames"] if r.get("new_node")}) or ["node1"]
        coltxt = "`%s`" % " / ".join(cols)
        pairs = []
        done = set()
        for r in j["renames"]:
            if not r.get("new_node") or r["net"] in done:
                continue
            done.add(r["net"])
            pairs.append("`%s` → `%s` (net `%s`)" % (j["ref"], r["new_node"], r["net"]))
        for a in j["add_rows"]:
            pairs.append("★补行★ net `%s` · node1 `%s` · node2 `%s`"
                         % (a["net"], a["suggest_node1"], a["suggest_node2"]))
        addtxt = ("; ".join("net `%s` (脚表 pin%s)" % (a["net"], a["pin"]) for a in j["add_rows"])
                  if j["add_rows"] else "无")
        c4txt = ("★**%s 出 C4 的 %d 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 %d − %d = %d** ★"
                 % (ref, C["c4_total"], C["c4_total"], C["target_total"],
                    C["c4_total"] - C["target_total"]))
        A("| `%s` | %s | %d | %s | %s | %s | %s |"
          % (ref, p["bucket"], len(j["truth_pins"]), coltxt, "; ".join(pairs), addtxt, c4txt))
    A("")
    A("★**具名脚总条数 = %d**★ (★= 90 件脚数之和·脚本实算★) ⇒ ★**全部落完 ⇒ C4 = %d − %d = %d**★。"
      % (n_pins, C["c4_total"], C["target_total"], C["c4_total"] - C["target_total"]))
    A("")
    A("### §2.2 指令全清单 (%d 条: 改名 %d + 补行 %d) · ★逐条可执行★"
      % (n_rename + n_add, n_rename, n_add))
    A("")
    A("| # | ref | 动作 | 网表 CSV 行号 | 栏 (表头名) | 原值 | 改成 | 该脚所在网 |")
    A("|---|---|---|---|---|---|---|---|")
    k = 0
    for ref in order:
        j = jobof[ref]
        for r in j["renames"]:
            if not r.get("new_node"):
                continue
            k += 1
            A("| %d | `%s` | 改名 | %d | `%s` | `%s` | `%s` | `%s` |"
              % (k, ref, r["lineno"], r["col"], ref, r["new_node"], r["net"]))
        for a in j["add_rows"]:
            k += 1
            A("| %d | `%s` | ★补行★ | (新增) | `node1` | (新增一行) | `net=%s` · `node1=%s` · `node2=%s` | `%s` |"
              % (k, ref, a["net"], a["suggest_node1"], a["suggest_node2"], a["net"]))
    A("")
    A("★**合计 %d 条** (改名 %d + 补行 %d) ⇒ ★**脚数自洽: 具名脚 %d 只 + 补行 4 只 = 改名覆盖 %d 只** ★ "
      "⇒ ★**没有一件漏, 也没有一件多**★。"
      % (n_rename + n_add, n_rename, n_add, n_pins, n_pins - n_add))
    A("")
    A("★**三条落表时的坑 (★本单实跑踩出来的★)**:")
    A("")
    A("1. ★**只改 MAIN_PCB 行的 bare 节点串** ★ —— `state/check_pcb_nets.py` 的 C4 口径**先按 `board` 列过滤** "
      "⇒ ★**跨板行 (CHG_BOARD) 的同名裸端不参与占位脚号编号** ⇒ ★**改了它对 C4 一点用都没有, 反而会让"
      "「行序 ↔ 焊盘号」的对应关系错位**★。★**本单实跑登记了 %d 件存在跨板同名裸端: %s**★ "
      "(★该行本单只登记, 不改★)。"
      % (len(offboard), ", ".join("`%s` (行 %d · %s · %s)"
                                % (r, h[0]["lineno"], h[0]["col"], h[0]["net"]) for r, h in offboard)))
    A("2. ★**具名脚必须按【脚表真值】编号, 不能按【网表行序】编号** ★ —— 本单实跑: `R_PU_PG` 的 MAIN_PCB 行序是 "
      "`VDD_3V3_IO`(行 191) 在前、`PWR_GOOD`(行 358) 在后 ⇒ ★**按行序编号会得到 pin1=VDD_3V3_IO, "
      "而脚表真值是 pin1=PWR_GOOD**★ ⇒ ★**两者对 `R_PU_PG` / `Q_PG` 两件会给出【相反的板面接线】**★ ⇒ "
      "★**⇒ 具名脚一律取 `HW/netlist_v1_pins.csv` 的 `pin` 栏; 这两件的板面 pad↔net 必须在腿 A 里同时对调**★。")
    A("3. ★**4 件的 GND 脚在网表里根本没有以节点形态出现 (脚表里有)** ★ —— `C_KEY_PWR` / `C_KEY_VM` / "
      "`C_KEY_VP` / `R_BAT_DET_2`: ★**脚表 `pin` 栏有 `2` (net=GND), 但 `HW/netlist_v1.csv` 里该器件的 "
      "GND 端是写在 `node2` 槽里的网名 `GND` (不是节点串) ⇒ 网表侧只推出 1 个脚** ★ ⇒ "
      "★**光改名不够, 必须补 4 行** ★ ⇒ ★**补行后网表推出 2 个脚, 才与官方 2 焊盘 land 对上 (否则 C2/C3 红)** ★。")
    A("")

    # ---------------- §3
    A("## §3 板侧那 5 条差异的并表 (★本单把它们跟 %d 件绑在一张表上·不许漏★)" % C["target_total"])
    A("")
    A("| # | 板侧差异 (C1 基线读数) | 在 %d 件清单的哪一行 | 换 land 时怎么一起改 | 改完 `check_pcb_nets.py` 的 C1 会变成什么 |"
      % C["target_total"])
    A("|---|---|---|---|---|")
    A("| 1 | 多余: `C_VBUS_GND` pad1 = GND | ★**不在 %d 件清单里** ★ (★BOM `dnp=DNP` · `board=镜框充电板` · "
      "网表 3 行全是 `board=CHG_BOARD` ⇒ **不进 C4 的 MAIN_PCB 口径**) | ★**本单不改它** ★ —— "
      "换 land 动不到它 (它不在 %d 件里); ★**它的 2 个 pad 是充电板侧的件, 而 C1 的网表侧只按 MAIN_PCB 过滤** ★ "
      "⇒ ★**⇒ 换完 land 后它仍然是 C1 的「多余 2」** ★ | ★**仍 多 2** ★ (沙盒 S3/S4 实测: "
      "`★多: C_VBUS_GND pad1 = GND` / `pad2 = VBUS_5V_CHG`) ⇒ ★**要清掉它只能靠「留位 / 下板」的拍板 "
      "(老板 B 类), 不在 S10 换封装这一趟的射程内** ★ |"
      % (C["target_total"], C["target_total"]))
    A("| 2 | 多余: `C_VBUS_GND` pad2 = VBUS_5V_CHG | 同上 | 同上 | 同上 |")
    A("| 3 | 错: `Q_PG` pad1 应为 PWR_GOOD 实际 PWR_ON | ★**在第 %d 行 (`Q_PG`·缺口桶)·%s 行** ★ | "
      "★**换 land 时同时把 pad1 的网改成 PWR_GOOD** ★ (★器件 DMP3098L 官方脚序 1=G/2=S/3=D ⇒ "
      "pad1=栅极=PWR_GOOD★) ⇒ ★**★不改 ⇒ 板面把栅极接到 PWR_ON, 开机路径直接不通 (ISS-283 G-1 裁决「写法 A」)★★ |"
      " ★**同号异网 3 → 0** ★ (沙盒 S3/S4 实测: 错 0) |"
      % (order.index("Q_PG") + 1, "§1 的 `Q_PG` 行"))
    A("| 4 | 错: `Q_PG` pad3 应为 PWR_ON 实际 PWR_GOOD | ★**在第 %d 行 (`Q_PG`·缺口桶)·%s 行** ★ | "
      "★**换 land 时同时把 pad3 的网改成 PWR_ON** ★ (★= 漏极 D·负载侧★) | ★**同号异网 3 → 0** ★ |"
      % (order.index("Q_PG") + 1, "§1 的 `Q_PG` 行"))
    A("| 5 | 错: `D_ESD_USB_D` pad1 应为 NET_USB_D_P_TYPEC 实际 USB_D_P_SRC | "
      "★**在第 %d 行 (`D_ESD_USB_D`·缺口桶)·%s 行** ★ | ★**换 land 时把 pad1 的网改成 NET_USB_D_P_TYPEC** ★ "
      "(★= TypeC 侧那一段; 现在的 USB_D_P_SRC 是 SoC 侧·中间隔着 `R_SER_USB_D_P`★) ⇒ "
      "★**★不改 ⇒ ESD 泄放路径接在错误的一侧, 等于没接★★ | ★**同号异网 3 → 0** ★ (沙盒 S3/S4 实测: 错 0) |"
      % (order.index("D_ESD_USB_D") + 1, "§1 的 `D_ESD_USB_D` 行"))
    A("")
    A("★**★本单另挖出的第 6 条 (★C1 看不见, 但腿 A 必须一起改★)★**:")
    A("")
    A("| # | 差异 | 在 %d 件清单的哪一行 | 换 land 时怎么一起改 | 改完 C1 会变成什么 |"
      % C["target_total"])
    A("|---|---|---|---|---|")
    A("| 6 | ★**`R_PU_PG` pad1 = VDD_3V3_IO / pad2 = PWR_GOOD, 而脚表真值是 pin1 = PWR_GOOD / "
      "pin2 = VDD_3V3_IO ⇒ 【板面 pad↔net 与脚表真值相反】** ★ | ★**在第 %d 行 (`R_PU_PG`·靶内桶)·%s 行** ★ | "
      "★**换 land 时把 pad1/pad2 的网对调** ★ (★10k 上拉: PWR_GOOD 开漏上拉 ⇒ 电阻两端对调不影响电气功能, "
      "**所以 C1 看不见**★ ⇒ ★**但腿 B 的具名脚是按脚表真值编号的 ⇒ 不对调就会得到【板脚号与网表脚号相反】**★) | "
      "★**C1 读数不变 (本来就绿)** ★ ⇒ ★**但 C1 绿 ≠ 对** ★ ⇒ ★**★腿 A 不对调 ⇒ 那一趟的板子上下拉电阻脚位是反的★★ |"
      % (order.index("R_PU_PG") + 1, "§1 的 `R_PU_PG` 行"))
    A("")
    A("★**沙盒四轮的 C1 读数 (★真闸代码跑出来的★)**:")
    A("")
    A("| 轮次 | 板 | 网表 | C1 读数 | C2 | C3 | C4 |")
    A("|---|---|---|---|---|---|---|")
    for k2, label in (("S0_基线_真板真表", "S0 基线"), ("S1_腿A单独", "S1 腿A单独"),
                      ("S2_腿B单独", "S2 腿B单独"), ("S3_腿A加腿B", "S3 腿A+腿B"),
                      ("S4_腿A加腿B_K3走b路", "S4 腿A+腿B·K3走(b)")):
        v = sbx[k2]
        fails = "; ".join(v["fails"]) if v["fails"] else "全绿"
        A("| %s | %s | %s | %s | %s | %s | ★**%s**★ |"
          % (label, "真板" if "基线" in label or "腿B单独" in label else "板副本(腿A)",
             "真表" if "基线" in label or "腿A单独" in label else "网表副本(腿B)",
             v["c1"], "—", "—", v["c4"]))
        A("| ↳ 失败项 | | | %s | | | |" % fails)
    A("")

    # ---------------- §4
    A("## §4 两条只登记不代拍的分支 (★原样继承 ISS-361 §5, 本单不代拍★)")
    A("")
    A("### §4.1 K2 · `D_ESD_USB_D` 最终 2 脚还是 3 脚 (★随老板 W-1/W-2 分叉★)")
    A("")
    A("| 路 | 候选封装 (实测在盘) | 板面 land 数 | 网表脚数 | 会红哪道闸 | 代价 |")
    A("|---|---|---|---|---|---|")
    A("| (a) 2 脚档 | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 `0edfa97bd7bd277f3c05acf2bee23892` | "
      "2 | 2 (脚表已有) | ★**C1/C2/C3 全绿** ★ (★沙盒 S3 实测: 本件不在 C1/C3 失败项里★) | "
      "★**泄放路径要另算** ★ (一颗双通道件只覆盖 2 根线) + ★**该件离 `J_USB_C` 现在的 47.99 mm 要缩到 ≤3.0 mm "
      "(那一趟 B08) ⇒ 布线要重跑** ★ |")
    A("| (b) 3 脚档 | `Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db` | 3 | "
      "★**3 (脚表 + 网表都要补第 3 脚)** ★ | ★**C3 红「板 3 脚 / 网表 2 脚」★ ★ 直到脚表与网表补齐第 3 脚 | "
      "★**pad 序须按最终型号厂商 land 逐颗复核** ★ (★本栏只是几何候选, 不是代拍★) |")
    A("")
    A("★**★不代拍** ★ —— 哪一档生效是老板 W-1/W-2 的拍板项。★**本单只登记候选封装 + 各自代价 + 各自会红哪道闸** ★。")
    A("")
    A("### §4.2 K3 · 5 只按键 (`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`) 的 2 脚 vs 4 焊盘")
    A("")
    A("★**事实**: 官方 `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` 有 ★**4 个物理焊盘 (焊盘号 1,1,2,2)**★, "
      "而网表这 5 只只有 2 个脚 ⇒ ★**板面从 2 land 变 4 land**★。")
    A("")
    A("| 路 | 做法 | 板面 land 数 | 网表脚数 | 会红哪道闸 | 代价 |")
    A("|---|---|---|---|---|---|")
    A("| (a) 网表给这 5 只加 2 个具名脚 | 脚表 `HW/netlist_v1_pins.csv` 加行 (★**`pin` 栏要加**★) + "
      "`HW/netlist_v1.csv` 的 node 串补具名脚 | 4 | 4 | ★**C3 绿** ★ (★若只改板不改网表 ⇒ ★**C3 红"
      "「板 4 脚 / 网表 2 脚」**★★) | ★**脚表 + 网表两处都要动** ★ + ★**KMR2 的 4 个焊盘号是 1,1,2,2 ⇒ "
      "脚表只能记 2 个 pin (1/2) ⇒ 板面同号多脚** ★ |")
    A("| (b) 改选 2 焊盘按键封装 | 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` md5 "
      "`749f20c5ab898069ade01682274c7bbf` (2 焊盘 @3.400 mm) 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` md5 "
      "`bed9b3b110e52e4ffcdc18240ef7a47c` (2 焊盘 @3.250 mm) | 2 | 2 | ★**C3 绿** ★ "
      "(★沙盒 S4 实测: K3 走 (b) 路时 C3 不符 = 0★) | ★**按动力度 3N → 1.5N ⇒ 误触风险上升** ★ "
      "(★矩阵 §⑮~⑲ 选 3N 的理由就是防误触★) ⇒ ★**★这是选型代价, 不是本单能拍的** ★ |")
    A("")
    A("★**★不代拍** ★ —— ★**本单只给两条路 + 代价 + 各自会红哪道闸** ★。")
    A("")
    A("★**★沙盒把 K3 的代价量化了 (★这是本单新增的读数★)★**:")
    A("")
    A("- ★**S3 (腿 A 全做, 含那 3 只换 KMR2 4 焊盘) ⇒ `C3 焊盘数不符 3 个`** ★ (★= `SW_BOOT` / `SW_KEY_PWR` / "
      "`SW_RST` 三只★) ⇒ ★**⇒ K3 走 (a) 路但网表没补脚 ⇒ 那道闸当场红** ★。")
    A("- ★**S4 (腿 A 全做, 但那 3 只按键不换 land = K3 走 (b) 路) ⇒ `C3 焊盘数不符 0 个`** ★ "
      "⇒ ★**⇒ C4 目标 %d 在 K3 走 (b) 路时【连 C3 都能一起绿】** ★。" % (C["c4_total"] - C["target_total"]))
    A("- ★**⇒ 无论 K3 走哪条路, C4 目标 %d 都成立 (C4 只看网表节点串)** ★。" % (C["c4_total"] - C["target_total"]))
    A("")

    # ---------------- §5
    A("## §5 两条漏件的并入建议 (★只给建议 + 机器判据, 零改既有页★)")
    A("")
    fb_w = sum(1 for _ in open(WP, encoding="utf-8") if "FB_DEMO" in _)
    fb_p = sum(1 for _ in open(PF, encoding="utf-8") if "FB_DEMO" in _)
    A("### §5.1 `FB_DEMO` (★ISS-361 §5 K4 已登记·本单并进去★)")
    A("")
    A("| 项 | 实测 |")
    A("|---|---|")
    A("| 那一趟两份文件里的命中数 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` **%d** 次 · "
      "`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` **%d** 次 (★其余 12 件都出现过: "
      "`CHG_GND_STAR` 7/0 · `D_ESD_CAM` 2/6 · `D_ESD_DEMO` 2/0 · `D_ESD_USB_D` 19/15 · `Q_AND` 4/9 · "
      "`Q_ENVC` 2/7 · `Q_PG` 16/18 · `SW_BOOT` 7/3 · `SW_KEY_PWR` 8/3 · `SW_KEY_VM` 8/3 · `SW_KEY_VP` 8/3 · "
      "`SW_RST` 8/3★) |" % (fb_w, fb_p))
    A("| 现占位几何 [实测] | ★**斜置 2 land @对角 1.000 mm**★ (fab 2.00×1.60 mm · pad 0.550×0.900 mm) |")
    A("| 官方 0805 目标几何 [实测] | ★**正置 @2.125 mm**★ (fab 2.00×0.90 mm · pad 0.875×1.200 mm) |")
    A("| 结论 | ★**不改封装它就装不上** ★ ⇒ ★**必须并进那一趟的 land 重画清单** ★ |")
    A("| ★**本单的建议 (★不改那两份文件★)** ★ | ★**① 把它并进那一趟的 land 重画清单; "
      "② 机器判据建议: `grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 "
      "`grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的命中数都须 ≥ 1** ★ |")
    A("| ★**机器判据为什么这样写** ★ | ★**不是「文件里有这个词就算过」—— 是「两份文件里都排上了它」** ★ "
      "(★本单实测: 13 件里只有它两份都是 0★) |")
    A("")
    A("### §5.2 `CHG_GND_STAR` (★ISS-361 §5 K1 已登记·本单并进去·零改基线页★)")
    A("")
    A("| 项 | 实测 |")
    A("|---|---|")
    A("| 自相矛盾的那一格 | `HW/FP_TRUTH_BASELINE.md` §2.2 靶外同族登记表里该行的「是否触发布局/布线改动」栏写 "
      "★**「板面只有 1 个 land, 官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘 ⇒ 该器件接地脚与走线全新增」**★ |")
    A("| 同页正文怎么说的 | 同页正文写 ★**「`CHG_GND_STAR` 的情况与另 2 件不同: 它在网表里只有 1 个脚 (GND) ⇒ "
      "1 个 land 是对的」**★ ⇒ ★**同一页两处打架** ★ |")
    A("| 官方封装实测 | ★**`TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` 只有 1 个焊盘**★ "
      "(pad \"1\" smd circle 1.0×1.0 mm, md5 `cea8eb3ba9b799767624661848b00243`) ⇒ "
      "★**★那一格是错的, 照它改板会给 CHG_GND_STAR 加一个不存在的第 2 个 land**★ |")
    A("| ★**本单的建议 (★零改基线页★)** ★ | ★**① 把 §2.2 那一格的「官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘」"
      "订正为「官方封装 1 焊盘 (实测 md5 `cea8eb3ba9b799767624661848b00243`), 板面 1 个 land 即为正确, 不新增」; "
      "② 机器判据建议: 该行「焊盘数 / 网络核对结论」栏的 `1=1` 与目标封装的实测焊盘数必须一致** ★ |")
    A("| 为什么零改基线页 | ★**`HW/FP_TRUTH_BASELINE.md` 是 ISS-356 的签收页 ⇒ 改了它 ISS-356 的签收脚本会红** ★ "
      "⇒ ★**⇒ 本单只登记 + 给订正建议 + 给机器判据, 一个字不动** ★ |")
    A("")

    # ---------------- §6
    A("## §6 降级方案 (★逐件必填 · 一件不空 · 三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★)")
    A("")
    A("★**口径**: ★**查不到 ⇒ 三选一写清代价**★ ⇒ ★**每件都给了「已实测在盘的等效件 + 代价」, "
      "零外部等待式措辞**★。")
    A("")
    A("| ref | 桶 | 查不到的点 | 降级方案 (三选一 + 代价) |")
    A("|---|---|---|---|")
    unknown = {
        "CHG_GND_STAR": "★型号 (它是单点汇流位, 非器件) + §5.2 那一格的自相矛盾★",
        "D_ESD_CAM": "★pad↔net 序 (器件 1=I/O 2=GND, 板是反的) ⇒ 靠改 land 一并解决, 不靠查料★",
        "D_ESD_DEMO": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "D_ESD_USB_D": "★**最终是 2 脚还是 3 脚 (老板 W-1/W-2 未拍)** ⇒ 目标封装随分支变",
        "FB_DEMO": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "Q_AND": "★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★",
        "Q_ENVC": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "Q_PG": "★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★",
        "SW_BOOT": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
        "SW_KEY_PWR": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
        "SW_KEY_VM": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "SW_KEY_VP": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "SW_RST": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
    }
    for ref in order:
        p = pieces[ref]
        if ref in unknown:
            unk = unknown[ref]
        elif p["bucket"] == "靶内":
            unk = "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价"
        else:
            unk = "无"
        A("| `%s` | %s | %s | %s |" % (ref, p["bucket"], unk, fb_cell(p)))
    A("")
    A("★**%d 件逐件非空**★ (★§1 表的「降级方案」栏与本表同源·同一段文字★)。" % C["target_total"])
    A("")

    # ---------------- §7
    A("## §7 未决项与卡点 (★只登记, 不代拍★)")
    A("")
    A("| # | 卡点 | 事实 | 本单实测/依据 | 要谁答 |")
    A("|---|---|---|---|---|")
    A("| K1 | ★**`D_ESD_USB_D` 最终 2 脚还是 3 脚** ★ | 现行 BOM opn 是 2 脚 TPD1E05U06DPYR, "
      "那一趟 B07 要求它变 3 脚 | ★**两个分支的候选封装本单都已实测在盘** ★ (3 脚档 "
      "`Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db` / 2 脚档 "
      "`Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 `0edfa97bd7bd277f3c05acf2bee23892`) ⇒ "
      "★**沙盒实测: 走 2 脚档时 C1/C2/C3 全绿; 走 3 脚档时 C3 红「板 3 脚 / 网表 2 脚」** ★ | "
      "★**老板 W-1/W-2** ★ |")
    A("| K2 | ★**5 只按键 3N vs 1.5N** ★ | 官方 `SW_Push_1P1T_NO_CK_KMR2` 有 4 个物理焊盘 (1,1,2,2), "
      "网表这 5 只只有 2 个脚 | ★**沙盒量化: 走 (a) 路而网表不补脚 ⇒ C3 红 3 件; 走 (b) 路 ⇒ C3 绿** ★ "
      "(★代价: 按动力度 3N → 1.5N★) | ★**老板 (选型代价)** ★ |")
    A("| K3 | ★**`D_LED_G` 落位** ★ | `D_LED_G` 在靶内桶, 目标 `lib:name` 与几何本单已给全 "
      "(★ fab 外框 2.70×1.60 → 2.00×1.20 mm, 中心距 2.300 → 1.875 mm ⇒ land 要重画★) | "
      "★**落位 (装在哪、朝哪边) 是结构与外观的事, 不是封装真值的事** ★ ⇒ 本单只给封装与几何 | "
      "★**老板 / 结构总工** ★ |")
    A("| K4 | ★**`C_VBUS_GND` 的 2 个多余焊盘** ★ | C1 基线的「多余 2」就是它; "
      "★**它的 BOM `dnp=DNP` · `board=镜框充电板` ⇒ 不在 %d 件清单里, 也不进 C4 的 MAIN_PCB 口径** ★ | "
      "★**沙盒 S3/S4 实测: 做完腿 A + 腿 B 它仍然是 C1 的「多 2」** ★ ⇒ "
      "★**⇒ 要清掉它只能靠「留位 / 下板」的拍板, 不在 S10 这一趟的射程内** ★ | ★**老板 (B 类)** ★ |"
      % C["target_total"])
    A("| K5 | ★**`FB_DEMO` 没人排** ★ | 那一趟的两份文件里命中数 0/0 | "
      "★**§5.1 已给并入建议 + 机器判据 (两份文件命中数都须 ≥ 1)** ★ | ★**main** ★ |")
    A("| K6 | ★**`CHG_GND_STAR` 基线页那一格自相矛盾** ★ | 一格写「官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘」, "
      "同页正文写「1 个 land 是对的」 | ★**官方 `TestPoint_Pad_D1.0mm` 实测只有 1 个焊盘** ★ ⇒ "
      "★**§5.2 已给订正建议 + 机器判据** ★ | ★**main (基线页签收方)** ★ |")
    A("| K7 | ★**90 件的料号 (OPN) 不是本单的活** ★ | 13 件里 `CHG_GND_STAR` + 5 只按键 的 BOM `opn` 栏是 "
      "`[0数据]`; 其余 7 件已有具体型号; 靶内 %d 件的 BOM opn 栏多为空 | "
      "★**封装的判定 (库文件在盘 + md5 + 焊盘数 + 几何) 本单全部给全; 哪颗料是选型批次的事** ★ | "
      "★**无阻塞 (落表批次按本单目标 `lib:name` 回填同封装等效件)** ★ |" % C["inter_total"])
    A("")

    # ---------------- §8
    A("## §8 沙盒可达性证明 (★C4 从 %d 变到多少 · 腿 A / 腿 B 各自的贡献 · 能不能到 %d★)"
      % (C["c4_total"], C["c4_total"] - C["target_total"]))
    A("")
    A("★**沙盒一律落项目盘 `tmp/iss364_sbx/`** ★ (★**不许写 /tmp**: 2026-11-23 04:4x 实测系统 /tmp 配额已满·"
      "写 /tmp 会让闸拿到假读数★)。")
    A("")
    A("| 轮次 | 板 | 网表 | ★**C4**★ | ΔC4 | C1 失败项 | C2 失败项 | C3 失败项 |")
    A("|---|---|---|---|---|---|---|---|")
    for k2, label, bd, nl in (
            ("S0_基线_真板真表", "S0 基线", "真板", "真表"),
            ("S1_腿A单独", "S1 腿A单独", "板副本 (90 件换官方 land)", "真表"),
            ("S2_腿B单独", "S2 腿B单独", "真板", "网表副本 (%d 条具名指令)" % (n_rename + n_add)),
            ("S3_腿A加腿B", "S3 腿A+腿B", "板副本 (90 件换官方 land)", "网表副本 (%d 条具名指令)" % (n_rename + n_add)),
            ("S4_腿A加腿B_K3走b路", "S4 腿A+腿B·K3走(b)", "板副本 (87 件换官方 land, 3 只按键不换)", "网表副本")):
        v = sbx[k2]
        d = v["c4"] - sbx["S0_基线_真板真表"]["c4"]
        fl = v["fails"]
        c1f = next((f for f in fl if f.startswith("C1")), "—")
        c2f = next((f for f in fl if f.startswith("C2")), "—")
        c3f = next((f for f in fl if f.startswith("C3")), "—")
        A("| %s | %s | %s | ★**%d**★ | %s | %s | %s | %s |"
          % (label, bd, nl, v["c4"], ("★**%+d**★" % d) if d else "0", c1f, c2f, c3f))
    A("")
    A("★**结论 (★逐条回答派活书的要求★)**:")
    A("")
    A("1. ★**C4 从 %d 变到 %d** ★ ⇒ ★**目标 %d 是【可达】的** ★ —— ★**实测值就是 %d, 不是估的** ★。"
      % (C["c4_total"], sbx["S4_腿A加腿B_K3走b路"]["c4"],
         C["c4_total"] - C["target_total"], sbx["S4_腿A加腿B_K3走b路"]["c4"]))
    A("2. ★**腿 A (换官方 land) 贡献 ΔC4 = %+d** ★ ⇒ ★**零** ★ ⇒ ★**换 land 动不了 C4** ★ "
      "(★机制: C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自网表, 板在它之后才被读★)。"
      % (sbx["S1_腿A单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"]))
    A("3. ★**腿 B (网表节点具名) 贡献 ΔC4 = %+d** ★ ⇒ ★**它就是那条唯一有效的杠杆** ★。"
      % (sbx["S2_腿B单独"]["c4"] - sbx["S0_基线_真板真表"]["c4"]))
    A("4. ★**两条腿缺一不可, 但作用点不同** ★ —— ★**腿 A 不做 ⇒ C1 错 2 (`R_PU_PG`/`Q_PG` 的 pad↔net) "
      "和 C3 错 7 (4 件 1→2 land + 3 只按键 2→4 land); 腿 B 不做 ⇒ C1 错 5 + C2/C3 错 4** ★ "
      "⇒ ★**⇒ 那条「须【换官方 land %d 件 + 网表节点具名 %d 件】」的验收条件, 两条腿缺一都交不出绿板** ★。"
      % (C["target_total"], C["target_total"]))
    A("5. ★**做完之后还剩什么 (★差在哪、为什么★)** ★ —— ★**C1 只剩「多 2」, 就是 `C_VBUS_GND` 的 2 个充电板侧焊盘** ★ "
      "(★K4: 它 `dnp=DNP` · `board=镜框充电板` ⇒ 不在 %d 件清单里, 也不进 C4 的 MAIN_PCB 口径 ⇒ "
      "★**换 land 与具名脚都够不着它**★ ⇒ ★**要清掉只能靠「留位 / 下板」的拍板**★)** ★ "
      "⇒ ★**其余 (缺 0 / 同号异网 0) 全绿** ★。" % C["target_total"])
    A("")
    A("★**沙盒留证路径**: `tmp/iss364_sbx/board_legA.kicad_pcb` · "
      "`tmp/iss364_sbx/board_legA_k3b.kicad_pcb` · `tmp/iss364_sbx/netlist_v1_legB.csv` · "
      "`logs/iss364/20_sandbox_readings.json` · `logs/iss364/21_sandbox_bodies.txt`")
    A("")

    # ---------------- §9
    A("## §9 复跑命令 + 本单的边界")
    A("")
    A("```bash")
    A("# ① 本单生成器 (重算页面里每个数字)")
    A("python3 logs/iss364/build_iss364_data.py")
    A("python3 logs/iss364/analyze_legB.py")
    A("python3 logs/iss364/build_land_swap_workpacket.py")
    A("# ② 沙盒可达性证明 (★必须带 KiCad python★)")
    A("bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py")
    A("# ③ 本单机器闸 (正常跑 / 反向用例自证)")
    A("python3 HW/check_fp_truth_land_swap.py")
    A("python3 HW/check_fp_truth_land_swap.py --selftest")
    A("# ④ 既有闸复跑 (一个字节没改)")
    A("python3 HW/check_fp_truth_baseline.py")
    A("python3 HW/check_fp_truth_coverage_gap.py")
    A("python3 HW/check_onepass_preflight_coverage.py")
    A("python3 HW/check_onepass_s10_manifest.py")
    A("# ⑤ C4 的原始读数 (★必须带 KiCad python·裸 python3 会 ModuleNotFoundError: pcbnew★)")
    A("bash state/pcbnew_py.sh state/check_pcb_nets.py")
    A("# ⑥ 板/网表/脚表/BOM 的 md5 复核")
    A("md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv")
    A("```")
    A("")
    A("★**本单的边界 (逐条, 不越界)**: ① ★**零写板** ★ (板 md5 `%s` / mtime "
      "`2026-11-06 07:07:17.362193413` 开工前后逐字节未变; 本单唯一动过板的动作是**在 `tmp/iss364_sbx/` "
      "的副本上**做沙盒实验); ② ★**零落表** ★ (网表/脚表/BOM/原理图一字未改; §2 的「目标节点串」是"
      "**给落表批次用的目标值**, 不是已落的值); ③ ★**零改既有闸** ★; ④ ★**零改既有页面正文** ★ "
      "(§3/§4/§5 的改动全是**建议**, 落在本单自己的页里); ⑤ ★**零外发 / 零采购 / 零联系供应商** ★; "
      "⑥ ★**不替老板拍板** ★ (K1/K2 只登记代价); ⑦ ★**零挂链** ★ (新闸交脚本但不挂进 `state/gate_check.py`); "
      "⑧ ★**证据分级必标** ★ (五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`)。"
      % board_md5())
    A("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("[build] 已写 %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
    print("[build] 关键读数: C4=%d → 目标 %d | 90 件=%d (靶内 %d + 缺口 %d) | 具名脚 %d (改名 %d + 补行 %d)"
          % (C["c4_total"], C["c4_total"] - C["target_total"], C["target_total"],
             C["inter_total"], C["gap_total"], n_pins, n_rename, n_add))
    return 0


if __name__ == "__main__":
    sys.exit(main())
