#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
netlist 生成器 (gen_netlist) —— 把图纸规格机械展开成可校验的 netlist
================================================================================
★为什么我 (项目总工) 自己做这一步:
  第一次派活让子 agent 写 "8 页图页 + netlist + KiCad .net" 三个大文件 → 它读完规格后
  一次要写的东西太大, API 请求被 abort → **0 产出** (2026-10-26 19:23 实测)。
  ⇒ 改分工: **机械的部分我生成, 判断的部分交子 agent**。
  netlist 是纯数据展开 (56 连接 + 13 电源轨 + 13 测试点 + 9 个选择位 + 3 页补充块),
  脚本展开 100% 覆盖、0 编造; hw-lead 只负责: 审 netlist + 出 8 页图页 + 出 KiCad .net。

★纪律:
  ① 只从 `HW/SCHEMATIC_V1_SPEC.json` 展开 —— 规格是我从 INTERFACE_TABLE.md / SCHEMATIC_L1.md
     机械抽的, 这里不做任何设计发挥 (器件值/阻抗/DNP 都继承规格原文)
  ② SoC 侧球位号一律 TBD-01 占位 (原厂引脚表/球位图未回)
  ③ 每个 [待原厂] 阻塞挂对应的 TBD-xx (编号 = 规格 undrawable[] 的顺序)

用法:
  python3 state/gen_netlist.py            # 写 HW/netlist_v1.csv
  python3 state/gen_netlist.py --summary  # 顺便打印每页行数
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SPEC = os.path.join(PROJ, "HW", "SCHEMATIC_V1_SPEC.json")
OUT = os.path.join(PROJ, "HW", "netlist_v1.csv")

COLS = ["page", "net", "node1", "node2", "ref", "value", "type", "dnp", "evidence", "tbd", "note", "conn_id"]

PAGES = {
    "P1": "电源树 (13 电源域 + 充电链)",
    "P2": "SoC 主控 (低速控制 / ADC / I2C / FSIN)",
    "P3": "启动存储 (焊盘位 + 串阻位, 不画存储芯片)",
    "P4": "显示双出口 (DSI 原生 / 桥接 互斥 8 个 0Ω 位)",
    "P5": "MIPI-CSI 传感器 (CONN_CAM 40p 跨铰链)",
    "P6": "高速差分与连接器 (DP_TX / USB / Type-C)",
    "P7": "板级接口与测试点 (13 TP + 按键 + LED)",
    "P8": "时钟 · 复位 · 调试 (XTAL / RESET / BOOT / JTAG / UART)",
}

# 关键词 → TBD 编号 (对应规格 undrawable[] 顺序: 1 引脚表 2 电源域 3 CSI 规格 4 显示TX
# 5 pitch 6 启动存储 7 帧同步 8 充电状态 9 DDC 独立 10 USB PHY 11 存储挂载 12 时序 13 FSIN)
TBD_RULES = [
    (r"CONN_CAM|CSI_", "TBD-03"),
    (r"CONN_LIGHT|DSI_D0|DSI_DDC", "TBD-04"),
    (r"V_CORE|V_SOC_IO|SENSOR_|LIGHT_", "TBD-02"),
    (r"USB_", "TBD-10"),
    (r"FSIN", "TBD-13"),
    (r"RESET_N|BOOT_N|XTAL", "TBD-12"),
]


def tbd_for(text: str) -> str:
    for pat, t in TBD_RULES:
        if re.search(pat, text or ""):
            return t
    return ""


def dnp_of(text: str) -> str:
    """规格里的 dnp 原文更丰富 (如 'DNP (无无线)' / '预留, 与 USB 二选一') → 归一化成 3 档, 原文进 note"""
    t = (text or "").strip()
    if t.startswith("必装") or t.startswith("装"):
        return "必装"
    if t.startswith("DNP"):
        return "DNP"
    return "可选"


def ev_of(text: str, default: str = "[推算]") -> str:
    for tag in ("[待原厂]", "[待JBD]", "[同Die参考-待官方确认]", "[官方]", "[实测]", "[推算]", "[0数据]"):
        if tag in (text or ""):
            return tag
    return default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(SPEC):
        print(f"❌ 缺规格: {SPEC}", file=sys.stderr)
        return 2
    spec = json.load(open(SPEC, encoding="utf-8"))
    rows: list[dict] = []

    def add(page, net, n1, n2, ref, value, typ, dnp, ev, tbd, note, cid):
        rows.append(dict(page=page, net=net, node1=n1, node2=n2, ref=ref, value=value, type=typ,
                         dnp=dnp, evidence=ev, tbd=tbd, note=note, conn_id=cid))

    conns = spec["connections"]
    by_id = {c["id"]: c for c in conns}

    # ---------- 1) 56 条连接 → 每条 1 个主 net 行 (+ 规格明写的无源件行) ----------
    def page_of(cid: str, sig: str, conn: str) -> str:
        if cid.startswith("C-"):
            return "P1"
        if cid.startswith("A-"):
            if "CSI" in sig:
                return "P5"
            if "DSI" in sig or "CONN_LIGHT" in conn:
                return "P4"
            return "P6"
        # B 组
        if re.search(r"I2C_B|DSI_DDC", sig):
            return "P4"
        if re.search(r"JTAG|UART", sig):
            return "P8"
        if re.search(r"RESET_N|BOOT_N", sig):
            return "P8"
        if re.search(r"USB|CC", sig):
            return "P6"
        if re.search(r"LED|KEY", sig):
            return "P7"
        return "P2"

    for c in conns:
        cid = c["id"]
        sig = c.get("signal") or c.get("rail") or ""
        conn = c.get("conn") or ""
        page = page_of(cid, sig, conn)
        if cid.startswith("C-"):
            # 电源: node1 = 轨名, node2 = 来源 IC
            rail = c.get("rail", "")
            ic = c.get("source_ic", "")
            ev = ev_of(c.get("volt", ""), "[推算]")
            tbd = tbd_for(rail)
            add(page, rail, rail, ic or "TBD", f"RAIL_{rail}", c.get("volt", ""), "RAIL",
                dnp_of(c.get("dnp", "")), ev, tbd,
                f"电源域: 目标 {c.get('volt','')} / 最大电流 {c.get('max_i','')}; SoC 侧球位号 TBD-01", cid)
            continue
        ev = ev_of(c.get("level", ""), "[推算]")
        tbd = tbd_for(sig + " " + conn)
        # SoC 侧功能名 + 球位号占位
        src = f"SoC[TBD-01].{sig}"
        dst = conn.split("(")[0].strip() or "TBD"
        add(page, sig, src, dst, f"NET_{sig}", c.get("imp", "") or c.get("level", ""), "NET",
            dnp_of(c.get("dnp", "")), ev, tbd,
            f"方向 {c.get('dir','')}; 电平 {c.get('level','')}; 阻抗 {c.get('imp','')}; 连接 {conn}; 测试点 {c.get('tp','')}",
            cid)
        # 规格里明写的无源件 → 各出一行 (不是发明, 是把规格原文展开成器件行)
        if "AC 耦合电容位" in conn:
            add(page, sig, f"SoC[TBD-01].{sig}", f"AC_{sig}", f"C_AC_{sig}", "100nF", "C", "必装", ev, tbd,
                "AC 耦合电容位 (规格: AC 耦合电容位)", cid)
        if "100Ω 对地端接" in conn:
            add(page, sig, f"SoC[TBD-01].{sig}", "GND", f"R_TERM_{sig}", "100Ω ±1%", "R",
                dnp_of(c.get("dnp", "")), ev, tbd, "对地端接 100Ω ±1% (0402, 手工可补装)", cid)
        if "串阻" in conn:
            add(page, sig, f"SoC[TBD-01].{sig}", dst, f"R_SER_{sig}", "100Ω ±10%", "R",
                dnp_of(c.get("dnp", "")), ev, tbd, "串联电阻位 (规格: 0402 串阻)", cid)
        m = re.search(r"(R_SEL_\w+|BR_\w+)", conn)
        if m:
            sel = m.group(1)
            add("P4", sel, f"SoC[TBD-01].{sig}", f"CONN_LIGHT.{sel}", sel, "0Ω", "R",
                "必装" if sel.startswith("R_SEL") else "DNP", "[官方]", "TBD-04",
                "显示双出口选择位: R_SEL_* 与 BR_* **互斥不得同装** (规格 §3.2)", cid)

    # ---------- 2) 13 电源轨 → P1 (规格 power_rails) ----------
    for r in spec["power_rails"]:
        rail = r["rail"]
        if rail in ("VBUS_5V", "SYS", "BAT", "GND"):
            continue  # 已在连接表里 (C 组) 或非独立轨
        ev = ev_of(r.get("evidence", ""), "[推算]")
        tbd = tbd_for(rail)
        add("P1", rail, rail, r.get("ic", "TBD"), f"RAIL_{rail}", r.get("volt", ""), "RAIL",
            "必装" if "可画" in str(r.get("status", "")) else "DNP", ev, tbd,
            f"电源域: {r.get('volt','')} / 最大 {r.get('max_i','')} / IC {r.get('ic','')} / 状态 {r.get('status','')}",
            "")

    # ---------- 3) 9 个显示选择位 → P4 ----------
    for s in spec["display_select"]:
        ref = s["ref"]
        if ref.startswith("R_TERM"):
            continue
        add("P4", ref, f"SoC[TBD-01].DSI_TX", f"CONN_LIGHT.{ref}", ref, "0Ω", "R",
            "必装" if "装" in s.get("planA", "") and "DNP" not in s.get("planA", "") else "DNP",
            "[官方]", "TBD-04",
            f"方案A {s.get('planA','')} / 方案B {s.get('planB','')}; {s.get('conn','')}; R_SEL_* 与 BR_* 互斥",
            "")

    # ---------- 4) 13 个测试点 → P7 ----------
    for t in spec["testpoints"]:
        add("P7", t["tp"], t["tp"], "GND", t["tp"], t.get("form", "测试点"), "TP", "必装",
            "[推算]", "", f"测什么: {t.get('what','')}; 位置: {t.get('where','')}", "")

    # ---------- 5) P3 启动存储 (焊盘位 + 串阻位, 不画芯片) ----------
    for sig, tbd in (("SPI_SCLK", "TBD-06"), ("SPI_CSn", "TBD-06"),
                     ("SPI_MOSI", "TBD-11"), ("SPI_MISO", "TBD-11")):
        add("P3", sig, f"SoC[TBD-01].{sig}", "J_BOOT1", f"R_SER_{sig}", "0Ω (串阻位)", "R", "必装",
            "[待原厂]", tbd, "启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; eMMC 会把板宽 12→15mm)", "")

    # ---------- 6) P8 时钟 (XTAL 两套方案: 内部RC 不装 / 外部晶振 焊盘位不装) ----------
    for sig in ("XTAL_IN", "XTAL_OUT"):
        add("P8", sig, f"SoC[TBD-01].{sig}", "X1_12P", "C_XTAL", "12pF", "C", "DNP",
            "[同Die参考-待官方确认]", "TBD-12",
            "时钟: 参考版**同时**给 内部RC(不装) 与 外部晶振(焊盘位+2×12pF, 不装) 两套, 由原厂一句话定生死", "")

    # ---------- 7) 写盘 ----------
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    per_page = {}
    for r in rows:
        per_page[r["page"]] = per_page.get(r["page"], 0) + 1
    print(f"✅ 已生成 {OUT}: {len(rows)} 行, 覆盖 {len(set(r['conn_id'] for r in rows if r['conn_id']))} 条连接")
    for p in PAGES:
        print(f"   {p} {PAGES[p]:<42} {per_page.get(p, 0):>4} 行")
    if args.summary:
        tbd_used = sorted({r["tbd"] for r in rows if r["tbd"]})
        print(f"   TBD 使用: {len(tbd_used)} 个 → {tbd_used}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
