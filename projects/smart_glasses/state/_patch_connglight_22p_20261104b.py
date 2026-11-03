#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04 第二步: 把**测试点行**与**规格 conn 串**里的旧 39p 脚号改成 Pi5 22p 脚号
   (不改的话: TP 行会把 pin7/8/13/14 顶成双网, 且凭空多出 pin30 ⇒ 门禁 C1/C2 报错)"""
import io, json, os, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GN = os.path.join(BASE, "state", "gen_netlist.py")
SP = os.path.join(BASE, "HW", "SCHEMATIC_V1_SPEC.json")
for f in (GN, SP):
    shutil.copy2(f, f + ".bak_20261104b")

# ---------------------------------------------------------------- 1) gen_netlist.py 的 TPS 表
s = io.open(GN, encoding="utf-8").read()
tp_map = [
    ('("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin30", "光机轨", "LDO 输出", "必装"),',
     '("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin14", "屏轨 3.3V (Pi5 DISPLAY 座 pin14=3V3)", "LDO 输出", "必装"),'),
    ('("TP_DSI_CK_P", "DSI_D0_CK_P", "CONN_LIGHT pin14", "DSI 时钟差分",',
     '("TP_DSI_CK_P", "DSI_D0_CK_P", "CONN_LIGHT pin6", "DSI 时钟差分 (Pi5 DISPLAY pin6=DSI1_CP)",'),
    ('("TP_DSI_CK_N", "DSI_D0_CK_N", "CONN_LIGHT pin13", "DSI 时钟差分 (规格合并名 TP_DSI_D0_CK_P / _N)",',
     '("TP_DSI_CK_N", "DSI_D0_CK_N", "CONN_LIGHT pin5", "DSI 时钟差分 (Pi5 DISPLAY pin5=DSI1_CN; 规格合并名 TP_DSI_D0_CK_P / _N)",'),
    ('("TP_DSI_D0_P", "DSI_D0_D0_P", "CONN_LIGHT pin8", "DSI D0 数据差分", "连接器出口", "必装"),',
     '("TP_DSI_D0_P", "DSI_D0_D0_P", "CONN_LIGHT pin9", "DSI D0 数据差分 (Pi5 DISPLAY pin9=DSI1_DP0)", "连接器出口", "必装"),'),
    ('("TP_DSI_D0_N", "DSI_D0_D0_N", "CONN_LIGHT pin7", "DSI D0 数据差分", "连接器出口", "必装"),',
     '("TP_DSI_D0_N", "DSI_D0_D0_N", "CONN_LIGHT pin8", "DSI D0 数据差分 (Pi5 DISPLAY pin8=DSI1_DN0)", "连接器出口", "必装"),'),
]
for old, new in tp_map:
    assert old in s, "TPS 行没找到: " + old[:60]
    s = s.replace(old, new, 1)

# D1/D2/D3 也补上差分测点 (4-lane 段的可达性; 屏侧只用 lane0/1, 但板上 lane2/3 必须能测)
anchor = '''    ("TP_I2CA_SCL", "I2C_A_SCL", "CONN_CAM pin24", "I2C_A 时钟", "连接器出口", "必装"),'''
assert anchor in s
extra = '''    # ★2026-11-04: DSI lane1/2/3 的差分测点 (22p 座口径: D1=pin2/3 · D2=pin16/17 · D3=pin18/19)
    ("TP_DSI_D1_P", "DSI_D0_D1_P", "CONN_LIGHT pin3", "DSI D1 数据差分 (Pi5 DISPLAY pin3=DSI1_DP1)", "连接器出口", "必装"),
    ("TP_DSI_D1_N", "DSI_D0_D1_N", "CONN_LIGHT pin2", "DSI D1 数据差分 (Pi5 DISPLAY pin2=DSI1_DN1)", "连接器出口", "必装"),
    ("TP_DSI_D2_P", "DSI_D0_D2_P", "CONN_LIGHT pin17", "DSI D2 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D2_N", "DSI_D0_D2_N", "CONN_LIGHT pin16", "DSI D2 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D3_P", "DSI_D0_D3_P", "CONN_LIGHT pin19", "DSI D3 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D3_N", "DSI_D0_D3_N", "CONN_LIGHT pin18", "DSI D3 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_I2CB_SCL", "I2C_B_SCL", "CONN_LIGHT pin11", "屏控制 I2C 时钟 (Pi5 DISPLAY pin11=SCL0)", "连接器出口", "必装"),
    ("TP_I2CB_SDA", "I2C_B_SDA", "CONN_LIGHT pin12", "屏控制 I2C 数据 (Pi5 DISPLAY pin12=SDA0)", "连接器出口", "必装"),
'''
s = s.replace(anchor, extra + anchor, 1)
io.open(GN, "w", encoding="utf-8").write(s)
print("✔ gen_netlist.py TPS 已改 (22p 脚号 + 补 lane1/2/3 与 I2C_B 测点)")

# ---------------------------------------------------------------- 2) 规格 conn 串
spec = json.load(open(SP, encoding="utf-8"))
conn_map = {
    "CONN_LIGHT pin15 (MIPI_CKP) + R_SEL_CK 0Ω": "CONN_LIGHT pin6 (DSI1_CP) + R_SEL_CK 0Ω",
    "CONN_LIGHT pin14 (MIPI_CKN) + 100Ω 对地端接": "CONN_LIGHT pin5 (DSI1_CN) + 100Ω 对地端接",
    "CONN_LIGHT pin9 (MIPI_0P) + R_SEL_D0 0Ω": "CONN_LIGHT pin9 (DSI1_DP0) + R_SEL_D0 0Ω",
    "CONN_LIGHT pin8 (MIPI_0N) + 100Ω 对地端接": "CONN_LIGHT pin8 (DSI1_DN0) + 100Ω 对地端接",
    "CONN_LIGHT pin12 (MIPI_1P) + R_SEL_D1 0Ω": "CONN_LIGHT pin3 (DSI1_DP1) + R_SEL_D1 0Ω",
    "CONN_LIGHT pin11 (MIPI_1N) + 100Ω 对地端接": "CONN_LIGHT pin2 (DSI1_DN1) + 100Ω 对地端接",
    "CONN_LIGHT pin18 (MIPI_2P) + R_SEL_D2 0Ω": "CONN_LIGHT pin17 (自用: lane2 P) + R_SEL_D2 0Ω",
    "CONN_LIGHT pin17 (MIPI_2N) + 100Ω 对地端接": "CONN_LIGHT pin16 (自用: lane2 N) + 100Ω 对地端接",
    "CONN_LIGHT pin11 → 光机": "CONN_LIGHT pin11 (SCL0) → 屏控制 I2C",
    "CONN_LIGHT pin12 → 光机": "CONN_LIGHT pin12 (SDA0) → 屏控制 I2C",
    "CONN_LIGHT pin21 (MIPI_3P) + R_SEL_D3 0Ω": "CONN_LIGHT pin19 (自用: lane3 P) + R_SEL_D3 0Ω",
    "CONN_LIGHT pin20 (MIPI_3N) + 100Ω 对地端接": "CONN_LIGHT pin18 (自用: lane3 N) + 100Ω 对地端接",
}
hit = 0
for c in spec.get("connections", []):
    old = c.get("conn")
    if old in conn_map:
        c["conn"] = conn_map[old]
        hit += 1
assert hit == len(conn_map), "规格 conn 串只改了 %d/%d 条" % (hit, len(conn_map))
note = spec.get("meta", {}).get("note", "")
spec["meta"]["note"] = note + (
    " ★★2026-11-04 03:0x **CONN_LIGHT 定稿 22p/0.5mm (Pi5 DISPLAY 座口径)**: 座型 = HIROSE FH12-22S-0.5SH(55) "
    "(RPi 官方 CM5IO 封装); 针序照 **Raspberry Pi 官方 Pi 5 原理图 J4**: 1=GND 2=DSI1_DN1 3=DSI1_DP1 4=GND "
    "5=DSI1_CN 6=DSI1_CP 7=GND 8=DSI1_DN0 9=DSI1_DP0 10=GND 11=SCL0 12=SDA0 13=GND 14=3V3 15=3V3; "
    "★16..22 在 Pi5 上是 NC ⇒ 本板自用 (lane2=16/17 · lane3=18/19 · 20/21/22 预留地); "
    "★配套线 Waveshare 『DSI Cable-12cm』22p↔15p; 依据见 HW/PCB/PI5_DSI_22P_PINOUT.md")
json.dump(spec, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("✔ SCHEMATIC_V1_SPEC.json conn 串已改 (%d 条) + meta 追加变更说明" % hit)
