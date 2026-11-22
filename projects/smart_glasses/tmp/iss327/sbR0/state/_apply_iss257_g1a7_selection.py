#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-257 · hw-lead · G1a-7 选型落表 · 真源改写脚本 (★一次性落表器, 落完即冻结★)

★**只改三样** ★:
  ① `state/gen_netlist.py` 的 29 行 `add(...)` 的 **value + evidence** 两栏 (14 件各自行数)
  ② `state/gen_netlist.py` 的 `PARTS` 字典 (★**只加 13 条 `opn`, `footprint` 一栏一律留空**★)
  ③ `state/p10_rows.json` 的 5 行的 **value + evidence** 两栏 (★P10 页的真源就是这个 JSON★)

★**不许碰**: 脚数 / `footprint` 列 / `dnp` 列 / `net` / `node1` / `node2` / `tbd` 列 / `note` 列 / `type` 列
★**不许碰**: `HW/netlist_v1.csv` (生成物) / `HW/BOM_v1.csv` (生成物) / 板 / `.kicad_pro`
"""
from __future__ import annotations

import io
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GN = os.path.join(PROJ, "state", "gen_netlist.py")
P10 = os.path.join(PROJ, "state", "p10_rows.json")

# ─────────────────────────────────────────────────────────────────────────────
# ★落表串 (★每件的 value 必须含真实可采购的型号或规格; 不许出现占位词★)
# ─────────────────────────────────────────────────────────────────────────────
ESD_CAM = "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"
ESD_DEMO = "PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)"
ESD_TC = "SP0503BAHT (Littelfuse 3 通道 TVS/ESD 阵列 · 5.5V standoff · SOT-143 4 脚)"
ESD_USB = "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"
TVS = "SMBJ5.0A (Littelfuse 单向 TVS · SMB · VRWM 5.0V · Vc 9.2V@65.3A · 600W)"
FB_DEMO = "BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)"
FB_VBUS = "BLM31PG121SN1 (Murata 1206 · 120Ω@100MHz · 3A · DCR 25mΩ)"
Q_AND = "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)"
Q_CHG_LED = "2N7002 (onsemi N-MOS SOT-23 · VGS(th) max 2.0V · IGSS ≤10nA)"
Q_ENVC = "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)"
Q_PG = "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)"
R_SUPV = "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板"
U_PWR_SW = ("TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · "
            "R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)")

# ★opn 串 (进 `PARTS` 字典; footprint 一栏一律留空 ⇒ 网表 footprint 列逐字节不变★)
OPN = {
    "D_ESD_CAM": "TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)",
    "D_ESD_DEMO": "PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV)",
    "D_ESD_TC": "SP0503BAHT (Littelfuse · 订购码 SP0503BAHTG · 3 通道 TVS 阵列 · SOT-143-4 · 5.5VWM/8.5VC)",
    "D_ESD_USB_D": "TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)",
    "D_TVS_VBUS": "SMBJ5.0A (Littelfuse DO-214AA SMB · VRWM 5.0V · VBR 6.4V min · Vc 9.2V @ Ipp 65.3A)",
    "FB_DEMO": "BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max)",
    "FB_VBUS": "BLM31PG121SN1 (Murata BLM31PG 1206 3216 metric · 120Ω@100MHz · 3000mA · DCR 0.025Ω)",
    "Q_AND": "AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
    "Q_CHG_LED": "2N7002 (onsemi SOT-23 3-pin · 60V · RDS(on) 1.2Ω typ@10V · ID 115mA · IGSS ≤10nA)",
    "Q_ENVC": "AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
    "Q_PG": "DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA)",
    "R_SUPV_DIV1": "RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)",
    "R_SUPV_DIV2": "RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)",
}


def rep(src: str, old: str, new: str, n: int = 1, tag: str = "") -> str:
    cnt = src.count(old)
    if cnt != n:
        raise SystemExit(f"★替换失败 [{tag}]: 期望 {n} 处, 实际 {cnt} 处 ★\n---\n{old}\n---")
    return src.replace(old, new)


def main() -> int:
    src = io.open(GN, encoding="utf-8").read()

    # ══════════ ① D_ESD_TC (L369) ══════════
    src = rep(src,
              '''    add("P1", "USB_VBUS_RAW", "USB_VBUS_RAW", "D_ESD_TC", "D_ESD_TC", "ESD 阵列 [待选型]", "D",
        "必装", "[推算]", "",''',
              '''    add("P1", "USB_VBUS_RAW", "USB_VBUS_RAW", "D_ESD_TC", "D_ESD_TC",
        "%s", "D",
        "必装", "[实测]", "",''' % ESD_TC,
              tag="D_ESD_TC L369")

    # ══════════ ② FB_VBUS (L373 / L381) ══════════
    src = rep(src,
              '''    add("P1", "VBUS_5V_ESD", "D_ESD_TC", "FB_VBUS", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "",''',
              '''    add("P1", "VBUS_5V_ESD", "D_ESD_TC", "FB_VBUS", "FB_VBUS",
        "%s", "L",
        "必装", "[官网]", "",''' % FB_VBUS,
              tag="FB_VBUS L373")
    src = rep(src,
              '''    add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "",''',
              '''    add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS",
        "%s", "L",
        "必装", "[官网]", "",''' % FB_VBUS,
              tag="FB_VBUS L381")

    # ══════════ ③ U_PWR_SW (L571) ══════════
    src = rep(src,
              '''        "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)", "IC", "必装",
        "[推算]", "",''',
              '''        "%s", "IC", "必装",
        "[官网]", "",''' % U_PWR_SW,
              tag="U_PWR_SW L571")

    # ══════════ ④ Q_PG (L595 / L604 / L609) ══════════
    src = rep(src,
              '''    add("P1", "PWR_ON", "Q_PG", "U_PWR_SW ON", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",''',
              '''    add("P1", "PWR_ON", "Q_PG", "U_PWR_SW ON", "Q_PG",
        "%s", "SW",
        "必装", "[官网]", "",''' % Q_PG,
              tag="Q_PG L595")
    src = rep(src,
              '''    add("P1", "BAT_SW", "Q_PG", "NET_BAT_SW", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",''',
              '''    add("P1", "BAT_SW", "Q_PG", "NET_BAT_SW", "Q_PG",
        "%s", "SW",
        "必装", "[官网]", "",''' % Q_PG,
              tag="Q_PG L604")
    src = rep(src,
              '''    add("P1", "PWR_GOOD", "Q_PG", "J_CHG pin6", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",''',
              '''    add("P1", "PWR_GOOD", "Q_PG", "J_CHG pin6", "Q_PG",
        "%s", "SW",
        "必装", "[官网]", "",''' % Q_PG,
              tag="Q_PG L609")

    # ══════════ ⑤ Q_AND (L630 / L635 / L637) ══════════
    src = rep(src,
              '''    add("P8", "RESET_N", "Q_AND", "NET_RESET_N", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW",
        "必装", "[推算]", "TBD-12",''',
              '''    add("P8", "RESET_N", "Q_AND", "NET_RESET_N", "Q_AND",
        "%s", "SW",
        "必装", "[官网]", "TBD-12",''' % Q_AND,
              tag="Q_AND L630")
    src = rep(src,
              '''    add("P8", "GND", "Q_AND", "GND", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW", "必装", "[推算]",
        "TBD-12", "[RESET_N] Q_AND 源极接地", "B-10")''',
              '''    add("P8", "GND", "Q_AND", "GND", "Q_AND",
        "%s", "SW", "必装", "[官网]",
        "TBD-12", "[RESET_N] Q_AND 源极接地", "B-10")''' % Q_AND,
              tag="Q_AND L635")
    src = rep(src,
              '''    add("P8", "PG_AND", "Q_AND", "U_DCDC_VIO PG", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW",
        "必装", "[推算]", "TBD-12", "[PG_AND] Q_AND 栅极 = PG_AND (两路 PG 都好时为低 · Q_AND 关)", "B-10")''',
              '''    add("P8", "PG_AND", "Q_AND", "U_DCDC_VIO PG", "Q_AND",
        "%s", "SW",
        "必装", "[官网]", "TBD-12", "[PG_AND] Q_AND 栅极 = PG_AND (两路 PG 都好时为低 · Q_AND 关)", "B-10")''' % Q_AND,
              tag="Q_AND L637")

    # ══════════ ⑥ Q_ENVC (L650 / L654 / L656) ══════════
    src = rep(src,
              '''    add("P8", "PG_AND", "Q_ENVC", "U_DCDC_VIO PG", "Q_ENVC", "[待选型] N-MOS (反相)", "SW",
        "DNP", "[推算]", "TBD-12",''',
              '''    add("P8", "PG_AND", "Q_ENVC", "U_DCDC_VIO PG", "Q_ENVC",
        "%s", "SW",
        "DNP", "[官网]", "TBD-12",''' % Q_ENVC,
              tag="Q_ENVC L650")
    src = rep(src,
              '''    add("P8", "GND", "Q_ENVC", "GND", "Q_ENVC", "[待选型] N-MOS (反相)", "SW", "必装", "[推算]",
        "TBD-12", "[PG_VIO] Q_ENVC 源极接地", "B-10")''',
              '''    add("P8", "GND", "Q_ENVC", "GND", "Q_ENVC",
        "%s", "SW", "必装", "[官网]",
        "TBD-12", "[PG_VIO] Q_ENVC 源极接地", "B-10")''' % Q_ENVC,
              tag="Q_ENVC L654")
    src = rep(src,
              '''    add("P8", "EN_VCORE", "Q_ENVC", "R_EN_VCORE", "Q_ENVC", "[待选型] N-MOS (反相)", "SW", "必装",
        "[推算]", "TBD-12", "[EN_VCORE] Q_ENVC 漏极 = EN_VCORE (把 EN 拉低 = 不使能)", "B-10")''',
              '''    add("P8", "EN_VCORE", "Q_ENVC", "R_EN_VCORE", "Q_ENVC",
        "%s", "SW", "必装",
        "[官网]", "TBD-12", "[EN_VCORE] Q_ENVC 漏极 = EN_VCORE (把 EN 拉低 = 不使能)", "B-10")''' % Q_ENVC,
              tag="Q_ENVC L656")

    # ══════════ ⑦ ESD 地脚补齐的循环 (L772-L775) ══════════
    src = rep(src,
              '''    for dref, note in (("D_ESD_TC", "Type-C 入口 ESD 阵列 地脚"),
                       ("D_ESD_CAM", "跨铰链 CSI ESD 阵列 地脚")):
        add("P9", "GND", dref, "GND", dref, "ESD 阵列 [待选型]", "D", "必装", "[推算]", "",''',
              '''    for dref, dval, dev in (("D_ESD_TC", "%s", "[实测]"),
                            ("D_ESD_CAM", "%s", "[官网]")):
        add("P9", "GND", dref, "GND", dref, dval, "D", "必装", dev, "",''' % (ESD_TC, ESD_CAM),
              tag="ESD 地脚循环 L772")

    # ══════════ ⑧ R_SUPV_DIV1 / DIV2 (L1323 / L1327 / L1330) ══════════
    src = rep(src,
              '''    add("P8", "V_SOC_IO", "RAIL_V_SOC_IO", "R_SUPV_DIV1", "R_SUPV_DIV1",
        "[待选型] 分压上臂 (0Ω 跳线位)", "R", "必装", "[推算]", "TBD-02",''',
              '''    add("P8", "V_SOC_IO", "RAIL_V_SOC_IO", "R_SUPV_DIV1", "R_SUPV_DIV1",
        "%s", "R", "必装", "[官网]", "TBD-02",''' % R_SUPV,
              tag="R_SUPV_DIV1 L1323")
    src = rep(src,
              '''    add("P8", "SUPV_SENSE", "R_SUPV_DIV1", "R_SUPV_DIV2", "R_SUPV_DIV2",
        "[待选型] 分压下臂 (0Ω 跳线位)", "R", "必装", "[推算]", "TBD-02",''',
              '''    add("P8", "SUPV_SENSE", "R_SUPV_DIV1", "R_SUPV_DIV2", "R_SUPV_DIV2",
        "%s", "R", "必装", "[官网]", "TBD-02",''' % R_SUPV,
              tag="R_SUPV_DIV2 L1327")
    src = rep(src,
              '''    add("P8", "GND", "R_SUPV_DIV2", "GND", "R_SUPV_DIV2", "[待选型] 分压下臂 (0Ω 跳线位)",
        "R", "必装", "[推算]", "TBD-02", "[SUPV_SENSE] 分压下臂 地端")''',
              '''    add("P8", "GND", "R_SUPV_DIV2", "GND", "R_SUPV_DIV2",
        "%s",
        "R", "必装", "[官网]", "TBD-02", "[SUPV_SENSE] 分压下臂 地端")''' % R_SUPV,
              tag="R_SUPV_DIV2 L1330")

    # ══════════ ⑨ D_ESD_CAM (L1365 / L1368) ══════════
    src = rep(src,
              '''    add("P9", "CSI_D0_CK_P", "CONN_CAM pin18", "D_ESD_CAM", "D_ESD_CAM",
        "ESD 阵列 [待选型] (多通道 CSI)", "D", "必装", "[推算]", "TBD-03",''',
              '''    add("P9", "CSI_D0_CK_P", "CONN_CAM pin18", "D_ESD_CAM", "D_ESD_CAM",
        "%s", "D", "必装", "[官网]", "TBD-03",''' % ESD_CAM,
              tag="D_ESD_CAM L1365")
    src = rep(src,
              '''    add("P9", "GND", "D_ESD_CAM", "GND", "D_ESD_CAM", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "TBD-03", "[CSI_D0_CK_P] CSI ESD 地端")''',
              '''    add("P9", "GND", "D_ESD_CAM", "GND", "D_ESD_CAM",
        "%s", "D", "必装",
        "[官网]", "TBD-03", "[CSI_D0_CK_P] CSI ESD 地端")''' % ESD_CAM,
              tag="D_ESD_CAM L1368")

    # ══════════ ⑩ D_ESD_USB_D (L1420 / L1423) ══════════
    src = rep(src,
              '''    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",
        "ESD 阵列 [待选型] (USB 2.0 双通道)", "D", "必装", "[推算]", "",''',
              '''    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",
        "%s", "D", "必装", "[官网]", "",''' % ESD_USB,
              tag="D_ESD_USB_D L1420")
    src = rep(src,
              '''    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "", "[D_ESD_USB_D] ESD 地端", "A-24")''',
              '''    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D",
        "%s", "D", "必装",
        "[官网]", "", "[D_ESD_USB_D] ESD 地端", "A-24")''' % ESD_USB,
              tag="D_ESD_USB_D L1423")

    # ══════════ ⑪ D_ESD_DEMO (L1433 / L1436) ══════════
    src = rep(src,
              '''    add("P1", "RAIL_DEMO_5V", "D_ESD_DEMO", "RAIL_DEMO_5V", "D_ESD_DEMO",
        "ESD 阵列 [待选型] (USB 2.0)", "D", "必装", "[推算]", "",''',
              '''    add("P1", "RAIL_DEMO_5V", "D_ESD_DEMO", "RAIL_DEMO_5V", "D_ESD_DEMO",
        "%s", "D", "必装", "[官网]", "",''' % ESD_DEMO,
              tag="D_ESD_DEMO L1433")
    src = rep(src,
              '''    add("P1", "GND", "D_ESD_DEMO", "GND", "D_ESD_DEMO", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "", "[RAIL_DEMO_5V] USB ESD 阵列 地端", "A-24")''',
              '''    add("P1", "GND", "D_ESD_DEMO", "GND", "D_ESD_DEMO",
        "%s", "D", "必装",
        "[官网]", "", "[RAIL_DEMO_5V] USB ESD 阵列 地端", "A-24")''' % ESD_DEMO,
              tag="D_ESD_DEMO L1436")

    # ══════════ ⑫ FB_DEMO (L1438 / L1440) ══════════
    src = rep(src,
              '''    add("P1", "RAIL_DEMO_5V", "FB_DEMO", "RAIL_DEMO_5V", "FB_DEMO", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "", "[RAIL_DEMO_5V] VBUS π 滤波 (磁珠+体电容)", "A-24")''',
              '''    add("P1", "RAIL_DEMO_5V", "FB_DEMO", "RAIL_DEMO_5V", "FB_DEMO",
        "%s", "L",
        "必装", "[官网]", "", "[RAIL_DEMO_5V] VBUS π 滤波 (磁珠+体电容)", "A-24")''' % FB_DEMO,
              tag="FB_DEMO L1438")
    src = rep(src,
              '''    add("P1", "GND", "FB_DEMO", "GND", "FB_DEMO", "π 滤波磁珠 [待选型]", "L", "必装",
        "[推算]", "", "[RAIL_DEMO_5V] π 滤波 地端", "A-24")''',
              '''    add("P1", "GND", "FB_DEMO", "GND", "FB_DEMO",
        "%s", "L", "必装",
        "[官网]", "", "[RAIL_DEMO_5V] π 滤波 地端", "A-24")''' % FB_DEMO,
              tag="FB_DEMO L1440")

    # ══════════ ⑬ PARTS 字典: 只加 13 条 opn (footprint 一栏一律留空) ══════════
    parts_block = "\n".join(
        '    "%s": {"footprint": "", "opn": "%s"},' % (ref, opn.replace('"', "'"))
        for ref, opn in OPN.items())
    anchor = '''    "C_REGN": {
        "footprint": "0805 (2.0×1.25 mm) MLCC · 2 焊盘 (充电板侧 · 贴 U_CHG pin22 近端)",
        "opn": "GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)",
    },
}'''
    assert src.count(anchor) == 1, "PARTS 锚点定位失败"
    src = src.replace(anchor, anchor[:-1] + '''
    # ★★2026-11-16 ISS-257 落表 (G1a-7): 14 件「必装 ∩ [待选型]」的 OPN 回填 ★★
    #   ★**`footprint` 一栏一律留空** ⇒ 网表 `footprint` 列与落表前逐字节相同 (★板侧焊盘是占位, 板那一趟才定 land★)
    #   ★型号出处 = HW/PART_SELECTION_MATRIX_2026-11-16.md (ISS-241, sw-lead) 的推荐项 + 官方数据手册
''' + parts_block + '''
}''')

    io.open(GN, "w", encoding="utf-8").write(src)
    print("★ gen_netlist.py 已落表 (29 行 value/evidence + 13 条 PARTS opn) ★")

    # ══════════ ⑭ p10_rows.json: 5 行的 value + evidence ══════════
    data = json.load(io.open(P10, encoding="utf-8"))
    n = 0
    for r in data:
        if r.get("ref") == "D_TVS_VBUS":
            r["value"] = TVS
            r["evidence"] = "[官网]"
            n += 1
        elif r.get("ref") == "Q_CHG_LED":
            r["value"] = Q_CHG_LED
            r["evidence"] = "[官网]"
            n += 1
    if n != 5:
        raise SystemExit("★ p10_rows.json 行数不对: %d (期望 5) ★" % n)
    with io.open(P10, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=2))
    print("★ p10_rows.json 已落表 (5 行 value/evidence) ★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
