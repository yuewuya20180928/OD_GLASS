#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04 04:0x: U_TEMP (TMP117) 从**4 脚抽象**改成**官方 6 脚 WSON-6** (DRV0006B)

★**为什么改**: TI TMP117 datasheet §5 Table 5-1 明确 6 个脚:
    1=SCL  2=GND  3=ALERT  4=ADD0  5=V+  6=SDA
   原来的 4 脚写法 (1=SDA 2=SCL 3=VDD 4=GND) **与原厂脚号完全对不上** ⇒ 照原厂封装焊上去必然不工作。

★**另外两处按原厂改**:
  · ADD0 (pin4) 是**地址选择脚** ⇒ 必须接死 ⇒ 本设计接 GND ⇒ I2C 地址 **0x48** (与现有软件口径一致)
  · 散热焊盘 (EP): 原厂明确 "not connected to the device ground and should be left unsoldered
    for best measurement accuracy" ⇒ **不画 EP** (皮肤侧测温尤其要这样)
"""
import io, os, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GN = os.path.join(BASE, "state", "gen_netlist.py")
GB = os.path.join(BASE, "state", "gen_pcb_netlist_board.py")
for f in (GN, GB):
    shutil.copy2(f, f + ".bak_20261104c")

s = io.open(GN, encoding="utf-8").read()

old = '''    add("P2", "I2C_B_SCL", "U_TEMP pin2", "NET_I2C_B_SCL", "U_TEMP",
        "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)", "IC", "必装", "[官方]", "",
        "[I2C_A_SCL] ★V1.1 定型: 选 TI TMP117 [官方 ti.com/product/TMP117] (1.7-5.5V 供电, 5µA max, "
        "WSON-2 2×2mm); I2C_A 从设备地址 0x48, ★**11-02 19:5x 订正**: sensor 地址随换料变 —— IMX415 = **0x1a** / AR0234CS = **0x10** (实拉 RPi overlay 核过; ★**旧注释写的 0x36 是 OV04C10 的, 已作废**) / 桥接 0x50 / 充电 IC 0x12 / "
        "光机 0x72 都不冲突; 若原厂坚持裸 NTC, 改 ADC 分压位 (不换板)", "B-01")
    add("P2", "I2C_B_SDA", "U_TEMP pin1", "NET_I2C_B_SDA", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_A_SDA] TMP117 SDA", "B-01")
    add("P2", "VDD_3V3_IO", "U_TEMP pin3", "RAIL_VDD_3V3_IO", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_A_SCL] TMP117 供电 (3.3V, 5µA max)",
        "B-01")
    add("P2", "GND", "U_TEMP pin4", "GND", "U_TEMP", "TMP117 数字温度计", "IC", "必装",
        "[官方]", "", "[I2C_A_SCL] TMP117 地脚", "B-01")'''

new = '''    # ★★2026-11-04 04:0x: U_TEMP 改成**官方 6 脚 WSON-6 (DRV0006B)** —— TI TMP117 datasheet §5 Table 5-1:
    #   1=SCL  2=GND  3=ALERT  4=ADD0  5=V+  6=SDA   (★原来的 4 脚写法与原厂脚号完全对不上)
    add("P2", "I2C_B_SCL", "U_TEMP pin1", "NET_I2C_B_SCL", "U_TEMP",
        "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)", "IC", "必装", "[官方]", "",
        "[I2C_B_SCL] ★TMP117 **pin1 = SCL** (TI SNOSD82D Table 5-1: 1=SCL 2=GND 3=ALERT 4=ADD0 5=V+ 6=SDA); "
        "★V1.1 定型: TI TMP117 [官方 ti.com/product/TMP117] (1.7-5.5V 供电, 5µA max, WSON-6 2×2mm); "
        "地址 0x48, ★**11-02 19:5x 订正**: sensor 地址随换料变 —— IMX415 = 0x1a / AR0234CS = 0x10 / "
        "桥接 0x50 / 充电 IC 0x12 / 光机 0x72 都不冲突", "B-01")
    add("P2", "I2C_B_SDA", "U_TEMP pin6", "NET_I2C_B_SDA", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_B_SDA] TMP117 **pin6 = SDA**", "B-01")
    add("P2", "VDD_3V3_IO", "U_TEMP pin5", "RAIL_VDD_3V3_IO", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[VDD_3V3_IO] TMP117 **pin5 = V+** (1.7-5.5V)",
        "B-01")
    add("P2", "GND", "U_TEMP pin2", "GND", "U_TEMP", "TMP117 数字温度计", "IC", "必装",
        "[官方]", "", "[GND] TMP117 **pin2 = GND**", "B-01")
    # ★ADD0 (pin4) = 地址选择脚 ⇒ 必须接死 ⇒ 接 GND ⇒ 地址 0x48 (与上面口径一致)
    add("P2", "GND", "U_TEMP pin4", "GND", "U_TEMP", "TMP117 ADD0 (地址选择)", "IC", "必装",
        "[官方]", "", "[GND] TMP117 **pin4 = ADD0** ⇒ 地址选择脚, 原厂: 接 GND/V+/SDA/SCL 之一; "
        "★本设计接 **GND ⇒ 地址 0x48** (与网表/软件口径一致)", "B-01")
    # ★ALERT (pin3) = 开漏输出 (过温/数据就绪告警) ⇒ demo 不接 (原厂允许悬空; 需告警再占一个 SoM 脚)
    add("P2", "NC_U_TEMP_ALERT", "U_TEMP pin3", "NC_U_TEMP_ALERT", "U_TEMP", "ALERT (开漏输出, 未接)",
        "IC", "必装", "[官方]", "", "[NC_U_TEMP_ALERT] TMP117 **pin3 = ALERT** (开漏输出, 需上拉) "
        "⇒ ★demo 悬空 (原厂: 可接 GND 或悬空); ★若要过温告警上报 ⇒ 需另占一个 SoM GPIO + 4.7k 上拉", "B-01")'''

assert old in s, "没找到 U_TEMP 旧行块"
s = s.replace(old, new, 1)
io.open(GN, "w", encoding="utf-8").write(s)
print("✔ gen_netlist.py: U_TEMP → 官方 6 脚")

# ---------------------------------------------------------------- 板生成器: U_TEMP 用官方封装
b = io.open(GB, encoding="utf-8").read()
old_imp = "from display_fpc_footprint import add_display_fpc  # noqa: E402"
new_imp = old_imp + "\nfrom tmp117_footprint import add_tmp117  # noqa: E402"
assert old_imp in b
b = b.replace(old_imp, new_imp, 1)

old_call = """        make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap,
                       px + w / 2.0, py + h / 2.0)"""
new_call = """        if ref == "U_TEMP":
            # ★TMP117 = WSON-6 (DRV0006B) 官方封装 —— 通用 IC 封装是"假封装" (1.27mm pitch) ⇒ 单独画
            add_tmp117(board, netmap, pins, px + w / 2.0, py + h / 2.0)
        else:
            make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap,
                           px + w / 2.0, py + h / 2.0)"""
assert old_call in b
b = b.replace(old_call, new_call, 1)
io.open(GB, "w", encoding="utf-8").write(b)
print("✔ gen_pcb_netlist_board.py: U_TEMP 走官方 TMP117 封装")
