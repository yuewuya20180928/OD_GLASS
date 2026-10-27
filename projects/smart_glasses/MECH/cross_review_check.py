#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/cross_review_check.py —— ISS-089 硬件交叉评审 (机械/热/装配) 机械自检

用法:
    cd projects/smart_glasses && python3 MECH/cross_review_check.py
退出码: 0 = 自检通过 (FAIL 0)  /  1 = 有 FAIL

它做什么:
    解析 HW/netlist_v1.csv + HW/BOM_v1.csv (真源, 不靠人肉数), 复算
    交叉评审正文的每一个关键数字, 并把判据与正文对表。

边界:
    只读 HW/ 下两个文件, 不写任何东西。不碰 state/ 与 PROJECT_TRACKER.md。
    所有 [推算] 的封装/高度假设集中在 ASSUMPTIONS 里, 换数只改这一处。
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETLIST = os.path.join(ROOT, "HW", "netlist_v1.csv")
BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
CHARGE_SPEC = os.path.join(ROOT, "HW", "CHARGE_BOARD_SPEC.md")

# ---------------------------------------------------------------- 假设表 [推算]
ASSUMPTIONS = {
    # 锁死值 (来自 MECH_BUDGET.md §1.4.2 / PROJECT_TRACKER §0)
    "temple_h_total": 7.3,      # 镜腿前后厚 (老板锁死, 电池 340mAh 档)
    "temple_h_used": 7.0,       # H 叠层已用 (0.8 壁 + 0.3 导热垫 + 0.8 PCB + 4.3 电池 + 0.8 壁)
    "temple_v_net": 37.0,       # 镜脚根部净高 (电池 22 + PCB 12 + 走线槽 3)
    "board_w": 12.0,            # 主板板宽 (暂锁, hw-lead 建议 15mm)
    "board_l": 76.0,            # 主板长 [推算] (SOC_CARRIER_EVAL)
    "board_t": 0.8,             # 4 层 FR4
    # 热模型 (MECH_BUDGET §2.3)
    "k_eff": 50.13,             # K/W (镜腿内发热量 → 皮肤侧温升, 主模型)
    "t_amb": 35.0,              # 基准
    "t_redline": 43.0,          # ISO 13732-1 红线
    "p_budget_temple": 0.16,    # 43°C 对应的镜腿内持续功耗上限
    # 器件 [推算]
    "header_body_h": 2.54,      # 1.27mm 直插排针塑料体高 (J_DEBUG 1×4 / J_UART 1×2)
    "conn_side_margin": 1.25,   # 0.5mm pitch 连接器: 接触跨度两侧各留的固定/定位边 (合计 2.5)
    "soc_pkg": (8.0, 10.0),     # FCCSP 8×10mm [官方/媒体]
    "ldo_eff_rail": "SYS",      # 现状: 7 颗 LDO 输入统一挂 SYS (P1 V1.1 C5)
    "dcdc_eff": 0.90,           # DC-DC 转换效率
    "soc_domain_p": 0.55,       # SoC 域功耗中位 (POWER_BUDGET_V2 口径 b)
    "chg_board_l": 25.0,        # 充电板长 (MECH_BUDGET M3)
    "chg_board_w": 10.0,        # 充电板宽
    "chg_board_t": 0.8,
}

RESULTS = []


def rec(ok, code, title, detail):
    RESULTS.append((bool(ok), code, title, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {code} {title}\n        {detail}")


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- 读网表
def load_netlist():
    with open(NETLIST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_bom():
    with open(BOM, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = load_netlist()
    bom = load_bom()
    A = ASSUMPTIONS

    # ============================================================ C-1 跨板网名复用
    # 一块板分两块 (充电板=镜框 / 主 PCB=镜脚) 之后, 同一个物理节点在两侧必须有唯一网名;
    # 若两侧用了同名网但中间没有铰链连接器 → 物理上不可能 (要么短接, 要么导出后断链)。
    HINGE_CONN = ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT")
    net_boards, net_rows = {}, {}
    for r in rows:
        net_boards.setdefault(r["net"], set()).add(r.get("board", ""))
        net_rows.setdefault(r["net"], []).append(r)

    def crosses(net):
        hit = []
        for r in net_rows[net]:
            for tok in (r["node1"], r["node2"]):
                for hc in HINGE_CONN:
                    if re.search(rf"\b{hc}\b", tok):
                        hit.append((hc, tok))
        return hit

    viol = []
    for net, bs in net_boards.items():
        if {"镜框充电板", "镜脚主 PCB"} <= bs and not crosses(net):
            viol.append(net)
    rec(not viol, "C-1", "跨板网名复用 (同名网跨两块板但无铰链通路)",
        f"命中 {len(viol)} 条: {viol}" if viol else "0 条")

    # ============================================================ C-2 充电板引用主板专有轨
    # 充电板只有 VBUS 5V + REGN 5V 两条轨; 3.3V (VDD_3V3_IO) 由主板的 LDO 产生。
    main_only_rails = set()
    for r in rows:
        if r.get("board") == "镜脚主 PCB" and r["type"] == "RAIL":
            main_only_rails.add(r["node1"])
    bad = []
    for r in rows:
        if r.get("board") != "镜框充电板":
            continue
        if r["type"] in ("NET", "RAIL"):
            continue
        if r["node2"] in main_only_rails or r["node1"] in main_only_rails:
            bad.append((r["ref"], r["net"], r["node1"], r["node2"]))
    rec(not bad, "C-2", "充电板器件引用主板专有电源轨 (物理上无此轨)",
        f"命中 {len(bad)} 条: {bad}" if bad else "0 条")

    # ============================================================ C-3 电池 NTC 是否真的跨铰链
    # V1.1 把电池 NTC 当安全项补画 (BQ25896 TS 脚); V1.2 把电池挪到镜脚 → TS 必须跨铰链。
    ts_rows = [r for r in rows if r["net"] == "TS_BAT"]
    ts_board = {r.get("board") for r in ts_rows}
    ts_cross = any(crosses("TS_BAT"))
    bat_board = {r.get("board") for r in rows if r["ref"] == "BT_432243"}
    ok3 = ts_cross and bat_board and "镜脚主 PCB" in bat_board
    rec(ok3, "C-3", "电池 NTC 跨铰链 (电芯在镜脚 / 充电 IC 在镜框)",
        f"TS_BAT 行 {len(ts_rows)} 条, board={ts_board}; 电芯板={bat_board}; "
        f"经铰链连接器={ts_cross} → " +
        ("✓ 通过" if ok3 else "★不通过: NTC 画在充电板侧, 但电芯在镜脚 → TS 脚接不到电芯, 过温保护不工作"))

    # ============================================================ C-4 LDO 本地损耗 (镜脚内)
    # P_loss = I_out × (V_in − V_out); V_in = SYS 满电 4.2V
    rail_spec = {}
    for r in rows:
        if r["type"] == "RAIL":
            m_v = re.search(r"目标\s*([\d.]+)\s*V", r["value"])
            m_i = re.search(r"最大电流\s*([\d.]+)\s*mA", r["value"])
            if m_v and m_i:
                rail_spec[r["node1"]] = (float(m_v.group(1)), float(m_i.group(1)))
    v_sys = 4.2
    ldo_loss_max = 0.0
    ldo_loss_typ = 0.0
    detail = []
    for r in rows:
        if r["type"] == "IC" and r["ref"].startswith("U_LDO"):
            out = r["node2"] if r["node1"].startswith("RAIL_") else r["node1"]
            if out not in rail_spec:
                continue
            v_out, i_max = rail_spec[out]
            loss = (i_max / 1000.0) * (v_sys - v_out)
            ldo_loss_max += loss
            ldo_loss_typ += loss * 0.5
            detail.append(f"{r['ref']}:{out} {v_out}V×{i_max}mA → {loss*1000:.0f}mW")
    dcdc_loss = A["soc_domain_p"] * (1 - A["dcdc_eff"]) / A["dcdc_eff"]
    temple_p = A["soc_domain_p"] + ldo_loss_max + dcdc_loss
    skin_max = A["t_amb"] + A["k_eff"] * temple_p
    skin_typ = A["t_amb"] + A["k_eff"] * (A["soc_domain_p"] + ldo_loss_typ + dcdc_loss)
    rec(skin_max > A["t_redline"], "C-4", "镜脚内转换损耗 → 皮肤侧温度 (主模型)",
        f"7×LDO 声明最大电流合计 {ldo_loss_max*1000:.0f}mW (典型 50% 负载 {ldo_loss_typ*1000:.0f}mW); "
        f"DC-DC 损耗 {dcdc_loss*1000:.0f}mW; 镜腿内 P = {A['soc_domain_p']}+{ldo_loss_max:.3f}+{dcdc_loss:.3f} = "
        f"{temple_p:.2f}W → 皮肤 {skin_max:.1f}°C (典型 {skin_typ:.1f}°C) vs 43°C 红线 "
        f"(43°C 只允许镜脚内 {A['p_budget_temple']}W) | 明细: {'; '.join(detail)}")

    # ============================================================ C-5 跨铰链触点区叠放 (沿镜脚高度)
    # 每个 0.5mm pitch 连接器的触点跨度 = pin 数 × 0.5mm; 4 条竖排带在铰链区叠放
    conn_pins = {"J_CHG": 10, "CONN_USB": 4, "CONN_CAM": 18, "CONN_LIGHT": 21}
    stack = sum(n * 0.5 for n in conn_pins.values())
    rec(stack <= A["temple_v_net"], "C-5", "铰链区 4 条排线竖向叠放 ≤ 镜脚净高",
        f"(10+4+18+21)×0.5 = {stack:.1f}mm vs 镜脚根部净高 {A['temple_v_net']}mm → 余 "
        f"{A['temple_v_net']-stack:.1f}mm")

    # ============================================================ C-6 连接器体宽 vs 板宽 (★决定 12 vs 15mm)
    worst = None
    for name, n in conn_pins.items():
        span = n * 0.5
        body = span + A["conn_side_margin"] * 2
        if worst is None or body > worst[1]:
            worst = (name, body, span)
    ok6 = worst[1] <= A["board_w"]
    rec(ok6, "C-6", "跨铰链连接器体宽 ≤ 主板板宽 (12mm 暂锁)",
        f"最宽 = {worst[0]} 1×{conn_pins[worst[0]]}p@0.5 → 接触跨度 {worst[2]:.1f}mm + 两侧边 {A['conn_side_margin']*2:.1f}mm "
        f"= 体宽 {worst[1]:.1f}mm vs 板宽 {A['board_w']}mm → " +
        ("✓ 放得下" if ok6 else f"★放不下 (差 {worst[1]-A['board_w']:.1f}mm); 板宽 ≥ {worst[1]:.1f}mm 才成立"))

    # ============================================================ C-7 镜脚 H 叠层余量 vs 直插排针
    margin = A["temple_h_total"] - A["temple_h_used"]
    ok7 = A["header_body_h"] <= margin
    rec(ok7, "C-7", "J_DEBUG/J_UART 直插排针高度 ≤ 镜脚 H 余量",
        f"镜腿厚 {A['temple_h_total']}mm, H 叠层已用 {A['temple_h_used']}mm → 余 {margin:.1f}mm; "
        f"1.27mm 直插排针塑料体高 {A['header_body_h']}mm → " +
        ("✓" if ok7 else f"★超 {A['header_body_h']-margin:.2f}mm (必装件 J_DEBUG 1×4) → 必须改贴片/开槽/挪到检修口"))

    # ============================================================ C-8 BOM 封装列全空
    fp_unknown = sum(1 for b in bom if (b.get("footprint") or "").strip() in ("", "待定"))
    rec(fp_unknown == 0, "C-8", "BOM 封装 (footprint) 全部回填",
        f"{fp_unknown}/{len(bom)} 条 footprint = 待定 → 板面积/器件高度/连接器外形全部无法核算")

    # ============================================================ C-9 网表里没有安装孔/固定点
    keys = ("固定孔", "安装孔", "M1.2", "定位销", "keepout", "螺钉", "沉孔")
    hits = sum(1 for r in rows if any(k in (r.get("note", "") + r.get("value", "")) for k in keys))
    rec(hits > 0, "C-9", "网表含安装孔/固定点/keepout (PCB 画出来装得上)",
        f"网表里与机械固定相关的行数 = {hits} → " +
        ("有" if hits else "★0 条 → PCB 出来没有固定孔, 装不进骨架 (ISS-042 解 A 要求 2×M1.2 + ⌀2.0H7 定位销)"))

    # ============================================================ C-10 板级归属档位 vs 物理板数
    boards = sorted({r.get("board", "") for r in rows if r.get("board")})
    need_boards = {"镜脚主 PCB", "镜框充电板", "镜框摄像头板", "跨铰链界面"}
    missing = sorted(need_boards - set(boards))
    rec(not missing, "C-10", "板级归属覆盖全部物理板",
        f"netlist board 列现有 {boards}; 物理上至少还有 {missing} → "
        + ("✓" if not missing else "★连接器的另一半装哪块板没口径 (装配/备料/开孔三件事没有唯一口径)"))

    # ============================================================ C-11 充电板器件数 vs 外形
    p10_refs = set()
    if os.path.exists(CHARGE_SPEC):
        txt = open(CHARGE_SPEC, encoding="utf-8").read()
        for m in re.finditer(r"^P10,.*$", txt, re.M):
            parts = m.group(0).split(",")
            if len(parts) > 4:
                p10_refs.add(parts[4].strip().strip('"'))
    board_area = A["chg_board_l"] * A["chg_board_w"]
    rec(len(p10_refs) <= 40, "C-11", "充电板器件级清单 vs 25×10×0.8 外形",
        f"P10 唯一位号 {len(p10_refs)} 个, 外形面积 {board_area:.0f}mm² "
        f"(扣 Type-C 座体 8.9×7.4≈66mm² → 可用 {board_area-66:.0f}mm²) → "
        + ("✓ 密度可接受" if len(p10_refs) <= 40 else
           f"★{len(p10_refs)} 个器件 (M3 的 25×10 是按 4 类件估的) → 外形要重出, 否则装不下"))

    # ============================================================ C-12 跨铰链压降测点只有一个
    tp_bat = [r for r in rows if r["ref"] == "TP_BAT_CHG"]
    bat_chg_boards = {r.get("board") for r in rows if r["net"] == "BAT_CHG"}
    ok12 = len(bat_chg_boards & {"镜框充电板", "镜脚主 PCB"}) >= 2
    rec(ok12, "C-12", "跨铰链段压降测点成对 (Kelvin 双点)",
        f"BAT_CHG 网涉及的板 = {bat_chg_boards}; TP_BAT_CHG 共 {len(tp_bat)} 个 → " +
        ("✓ 两端都有测点" if ok12 else
         "★只有一侧有测点 → 单点测不出铰链段压降 (要框侧 + 脚侧各一个, 或 4 线制)"))

    # ---------------------------------------------------------------- 汇总
    fails = [x for x in RESULTS if not x[0]]
    print("\n" + "=" * 78)
    print(f"自检汇总: {len(RESULTS)-len(fails)}/{len(RESULTS)} PASS · FAIL {len(fails)}")
    print("=" * 78)
    for ok, code, title, _ in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {code}  {title}")
    print(f"\n[实测] 条数 = 0 (无实物); 唯二可复现的是本脚本解析 netlist/BOM 的复算结果")
    print("用法: cd projects/smart_glasses && python3 MECH/cross_review_check.py")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
