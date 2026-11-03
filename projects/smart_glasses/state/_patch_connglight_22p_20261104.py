#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04: CONN_LIGHT 从过渡态 34/39p 改成 **Pi5 22p/0.5mm DISPLAY 座**
   依据: HW/PCB/PI5_DSI_22P_PINOUT.md (Pi5 官方原理图 J4 + Waveshare 官方 15p + RPi 官方封装)
   ★针序照 Pi5 DISPLAY 座, 不照 CM5IO 的 22p (两者不同!)"""
import io, os, re, shutil, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GN = os.path.join(BASE, "state", "gen_netlist.py")
CK = os.path.join(BASE, "state", "check_netlist_pins.py")

# ---------------------------------------------------------------- 备份
for f in (GN, CK):
    shutil.copy2(f, f + ".bak_20261104")

s = io.open(GN, encoding="utf-8").read()
orig = s

# ---------------------------------------------------------------- 1) DSI_LANES 板侧脚号
old_lanes = '''DSI_LANES = [
    # lane, net_P, net_N, cid_P, cid_N, src_P, src_N, pin_P, pin_N, sel_dnp, 有对地端接
    # ★★2026-11-02 19:5x 按 Radxa Display 8HD/10FHD 40 针表 (0.5mm): P=正脚 / N=负脚
    ("CK", "DSI_D0_CK_P", "DSI_D0_CK_N", "A-13", "A-14",
     "DSI_TX_CK_P", "DSI_TX_CK_N", 14, 13, "必装", False),      # ★板侧 39p: MIPI_CKP14 / MIPI_CKN13 (屏侧 15/14)
    ("D0", "DSI_D0_D0_P", "DSI_D0_D0_N", "A-15", "A-16",
     "DSI_TX_D0_P", "DSI_TX_D0_N", 8, 7, "必装", False),         # ★板侧 39p: MIPI_0P8 / MIPI_0N7 (屏侧 9/8)
    ("D1", "DSI_D0_D1_P", "DSI_D0_D1_N", "A-17", "A-18",
     "DSI_TX_D1_P", "DSI_TX_D1_N", 11, 10, "必装", False),       # ★板侧 39p: MIPI_1P11 / MIPI_1N10 (屏侧 12/11)
    ("D2", "DSI_D0_D2_P", "DSI_D0_D2_N", "A-19", "A-20",
     "DSI_TX_D2_P", "DSI_TX_D2_N", 17, 16, "必装", False),       # ★板侧 39p: MIPI_2P17 / MIPI_2N16 (屏侧 18/17)
    ("D3", "DSI_D0_D3_P", "DSI_D0_D3_N", "A-21", "A-22",
     "DSI_TX_D3_P", "DSI_TX_D3_N", 20, 19, "必装", False),       # ★板侧 39p: MIPI_3P20 / MIPI_3N19 (屏侧 21/20)
]'''
new_lanes = '''DSI_LANES = [
    # lane, net_P, net_N, cid_P, cid_N, src_P, src_N, pin_P, pin_N, sel_dnp, 有对地端接
    # ★★2026-11-04: 板侧座 = **Pi5 22p/0.5mm DISPLAY 座** (针序照 Pi5 官方原理图 J4, 逐针)
    #   CK = pin5/6 · D0 = pin8/9 · D1 = pin2/3 · D2 = pin16/17 · D3 = pin18/19
    #   ★16..19 在 Pi5 上是 NC ⇒ 本板自用 (承载 lane2/lane3 ⇒ 主板→屏段 4-lane)
    #   依据: HW/PCB/PI5_DSI_22P_PINOUT.md
    ("CK", "DSI_D0_CK_P", "DSI_D0_CK_N", "A-13", "A-14",
     "DSI_TX_CK_P", "DSI_TX_CK_N", 6, 5, "必装", False),        # Pi5 DISPLAY: pin6=DSI1_CP / pin5=DSI1_CN
    ("D0", "DSI_D0_D0_P", "DSI_D0_D0_N", "A-15", "A-16",
     "DSI_TX_D0_P", "DSI_TX_D0_N", 9, 8, "必装", False),        # Pi5 DISPLAY: pin9=DSI1_DP0 / pin8=DSI1_DN0
    ("D1", "DSI_D0_D1_P", "DSI_D0_D1_N", "A-17", "A-18",
     "DSI_TX_D1_P", "DSI_TX_D1_N", 3, 2, "必装", False),        # Pi5 DISPLAY: pin3=DSI1_DP1 / pin2=DSI1_DN1
    ("D2", "DSI_D0_D2_P", "DSI_D0_D2_N", "A-19", "A-20",
     "DSI_TX_D2_P", "DSI_TX_D2_N", 17, 16, "必装", False),      # ★自用脚 (Pi5 侧 NC): lane2
    ("D3", "DSI_D0_D3_P", "DSI_D0_D3_N", "A-21", "A-22",
     "DSI_TX_D3_P", "DSI_TX_D3_N", 19, 18, "必装", False),      # ★自用脚 (Pi5 侧 NC): lane3
]'''
assert old_lanes in s, "DSI_LANES 块没找到"
s = s.replace(old_lanes, new_lanes, 1)

# ---------------------------------------------------------------- 2) CONN_LIGHT 逐脚块
start = s.find("    # ---- 光机连接器 ----")
end = s.find("# ------------------------------------------------------- P5 MIPI-CSI 传感器")
assert start > 0 and end > start, "找不到 CONN_LIGHT 块边界 (%d,%d)" % (start, end)
new_block = '''    # ---- 显示 FPC 座 (板内, 屏幕模组 ↔ 主板) ----
    # ★★2026-11-04 定稿: **Pi5 22p/0.5mm (HIROSE FH12-22S-0.5SH(55))**
    #   依据链: ① Raspberry Pi 官方 Pi 5 原理图 J4 (DISPLAY 座) 逐脚网名
    #           ② Waveshare 官方 wiki 『2.8inch DSI LCD』屏侧 15p 表 (逐脚与 ① 一致)
    #           ③ Raspberry Pi 官方 CM4IO/CM5IO KiCad 里的 FH12-22S 封装 (机械/land pattern)
    #   ★★**针序必须照 Pi5 DISPLAY 座抄** —— CM5IO 那套 22p (2/3=D0, 5/6=D1, 8/9=CLK, 20/21=I2C) 与之**不同**
    add("P4", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT",
        "★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)",
        "CONN", "必装", "[官方]", "",
        "[CONN_LIGHT] ★2026-11-04 定稿: 板内 FPC 座 22p/0.5mm, 针序照 **Raspberry Pi 5 官方 DISPLAY 座 (J4)**: "
        "1=GND 2=DSI1_DN1 3=DSI1_DP1 4=GND 5=DSI1_CN 6=DSI1_CP 7=GND 8=DSI1_DN0 9=DSI1_DP0 10=GND "
        "11=SCL0 12=SDA0 13=GND 14=3V3 15=3V3; ★16..22 在 Pi5 上是 NC ⇒ 本板自用 (lane2/lane3 + 预留地). "
        "★配套线: Waveshare 『DSI Cable-12cm』22p↔15p; ★详见 HW/PCB/PI5_DSI_22P_PINOUT.md")

    # --- 22p 座逐脚 (Pi5 DISPLAY 座口径) ---
    _light_gnd = [1, 4, 7, 10, 13, 20, 21, 22]
    for _pn in _light_gnd:
        add("P4", "GND", f"CONN_LIGHT pin{_pn}", "GND", "CONN_LIGHT", "GND", "NET", "必装", "[官方]", "",
            f"[CONN_LIGHT] Pi5 DISPLAY 座 pin{_pn} = GND"
            + (" (★16..22 在 Pi5 上是 NC ⇒ 本板自用, 这里当预留地)" if _pn >= 20 else ""), "")
    for _pn in (14, 15):
        add("P4", "LIGHT_3V3", f"CONN_LIGHT pin{_pn}", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V", "NET",
            "必装", "[官方]", "",
            f"[CONN_LIGHT] Pi5 DISPLAY 座 pin{_pn} = 3V3 (★屏侧 15p 的 14/15 都是 3V3)", "")
    # ★★屏控制 I2C (不是触控!) —— Pi5 DISPLAY 座 pin11 = SCL0 / pin12 = SDA0
    #   ★I2C_B 上拉已在 VDD_3V3_IO (3.3V) ⇒ 与屏内 MCU 的 3.3V I2C 同域 ⇒ 不需要电平转换
    add("P4", "I2C_B_SCL", "CONN_LIGHT pin11", "NET_I2C_B_SCL", "NET_I2C_B_SCL",
        "I2C_B_SCL", "NET", "必装", "[官方]", "",
        "[I2C_B_SCL] ★Pi5 DISPLAY 座 pin11 = SCL0 ⇒ **屏控制 I2C** (屏内 MCU @0x45; 树莓派驱动实测 probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · 背光 0xAB/0xAA) ⇒ **必须接**, 否则屏不亮也无法调光; "
        "★上拉在 VDD_3V3_IO (3.3V) ⇒ 与屏 3.3V 同域, 无需电平转换", "B-03")
    add("P4", "I2C_B_SDA", "CONN_LIGHT pin12", "NET_I2C_B_SDA", "NET_I2C_B_SDA",
        "I2C_B_SDA", "NET", "必装", "[官方]", "",
        "[I2C_B_SDA] ★Pi5 DISPLAY 座 pin12 = SDA0 ⇒ 屏控制 I2C (与 TMP117@0x48 同总线, 地址不冲突)", "B-04")


'''
s = s[:start] + new_block + s[end:]

# ---------------------------------------------------------------- 3) PARTS 里补 CONN_LIGHT
anchor = '''    # ---- ISS-112: BQ25896 封装从 "VQFN-16 3×3mm (RGT)" 改为官方真实封装 ----'''
assert anchor in s
parts_entry = '''    # ★2026-11-04 显示 FPC 座 (Pi5 22p) 封装/OPN 落定 —— 官方封装抄 Raspberry Pi 官方 CM4IO/CM5IO KiCad
    #   (Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal.kicad_mod); 焊盘 0.3x1.3mm / pitch 0.5 / pad1 在 +x 端
    "CONN_LIGHT": {"footprint": "Hirose FH12-22S-0.5SH, 22P / 0.5mm pitch / 右角(水平) / 底接触 / 1 固定柱, "
                               "焊盘 0.3x1.3mm (RPi 官方 CM5IO 封装: Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal)",
                   "opn": "FH12-22S-0.5SH(55)"},
'''
s = s.replace(anchor, parts_entry + anchor, 1)

io.open(GN, "w", encoding="utf-8").write(s)
print("✔ gen_netlist.py 已改 (%d → %d 字符)" % (len(orig), len(s)))

# ---------------------------------------------------------------- 4) 门禁: 22p + 去掉过渡豁免
c = io.open(CK, encoding="utf-8").read()
old_spec = """        'CONN_LIGHT': 34,   # ★过渡态 (2026-11-04 屏换 Waveshare 2.8inch: 座正从 39p 重画成 22p; Pi5 22p 针位表回来后一次性定稿, 见 ISS-176)"""
new_spec = """        'CONN_LIGHT': 22,   # ★2026-11-04 定稿: Pi5 22p/0.5mm DISPLAY 座 (针序见 HW/PCB/PI5_DSI_22P_PINOUT.md)"""
assert old_spec in c, "SPEC_PINS 里没有 CONN_LIGHT 行"
c = c.replace(old_spec, new_spec, 1)
old_gap = """        if ref == "CONN_LIGHT":
            gaps = []   # ★过渡态: 座正从 39p 重画成 22p (ISS-176) ⇒ 缺号是预期的
"""
assert old_gap in c, "没找到 CONN_LIGHT 缺号豁免"
c = c.replace(old_gap, "", 1)
io.open(CK, "w", encoding="utf-8").write(c)
print("✔ check_netlist_pins.py 已改 (22p, 去掉过渡豁免)")
