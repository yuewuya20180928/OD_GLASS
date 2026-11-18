#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_en_p0.py —— ★★P0 修复: 9 路电源 IC 的 EN 脚全没画 (TPS7A20 ×7 + TPS62130A ×2)

现象 (hw-lead ISS-151 实测 TI datasheet 得出, main 复核):
  ★ TPS7A20 **有 EN 脚**, 内部 **500kΩ 下拉** ⇒ 原文 "keeps the LDO disabled even when the EN pin is left floating"
  ★ EN 门限: VEN(LOW) ≤ 0.3V 关断 / VEN(HIGH) ≥ 0.9V 使能 (绝对值)
  ★ 而本项目 7 路 LDO + 2 路 DC-DC 的网表行**没有任何 EN 网络** ⇒ **投板后 9 路全灭 = 整板不上电 = 2~4 周返工**
  ★ 好消息: 现在 BOM footprint/opn 全是"待定" ⇒ **现在改网表成本 ≈ 0**

修法:
  ① 除 SENSOR_AVDD 外: 每颗 IC 的 EN **直接接 RAIL_SYS** (3.5-4.2V ≫ 0.9V ⇒ 永远使能) ⇒ 零新增器件
  ② SENSOR_AVDD (U_LDO_S28): EN 走 **RC 延时** (R 100k: SYS→EN, C 1µF: EN→GND)
     ⇒ 时间常数 (100k‖500k)×1µF ≈ 83ms ⇒ **AVDD 最后上电** ⇒ 满足 IMX415 的 DVDD→OVDD→AVDD 顺序
     ⇒ ★**顺手把 ISS-152 解掉: 1R + 1C, 不换 LDO 家族, 不改板层数**
  ③ 同步纠正项目内"TPS7A20 无 EN"的错误说法 (ISS-152 desc/note 已改)
"""
import json
import os

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'
GEN = f'{PROJ}/state/gen_netlist.py'

# ── ① 规格 JSON: meta 里记 EN 规则 (规格是真源) ──
d = json.load(open(SPEC, encoding='utf-8'))
meta = d.get('meta')
if isinstance(meta, dict):
    meta['en_policy'] = ("★★2026-11-02 20:3x P0: TPS7A20 / TPS62130A 都有 EN 脚 (TPS7A20 内部 500kΩ 下拉 ⇒ 悬空=关断) ⇒ "
                         "每颗电源 IC 的 EN 必须显式连接: 除 SENSOR_AVDD 外直连 RAIL_SYS (永远使能); "
                         "SENSOR_AVDD 走 RC 延时 (R 100k + C 1µF, t≈83ms) ⇒ AVDD 最后上电 (IMX415 要求 DVDD→OVDD→AVDD)")
    json.dump(d, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('[1] SCHEMATIC_V1_SPEC.json: meta.en_policy 已写')

# ── ② 生成器: 在每颗电源 IC 的输入行之后补 EN 网络 ──
s = open(GEN, encoding='utf-8').read()
anchor = """        # ★V1.1 补画 4: 电压不确定性的吸收方式写进图纸 (ISS-082 前提修正)"""
assert anchor in s, '没找到插入点 (V1.1 补画 4)'
en_block = '''        # ★★2026-11-02 20:3x ★★P0 修复: EN 脚必须显式画!
        #   依据: TPS7A20 datasheet —— EN 内部 500kΩ 下拉, 悬空 = LDO 关断 ("keeps the LDO disabled even
        #   when the EN pin is left floating"); VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能 (绝对值)。
        #   ★TPS62130A (DC-DC) 同样有 EN。⇒ 原网表 7 路 LDO + 2 路 DC-DC **全都没有 EN 网络**
        #   ⇒ 投板后 9 路全灭 = 整板不上电 = 2~4 周返工 ⇒ 现在改成本≈0 (BOM footprint 还全是"待定")。
        #   修法: ①除 SENSOR_AVDD 外, EN 直连 RAIL_SYS (3.5-4.2V ≫ 0.9V ⇒ 永远使能, 零新增器件)
        #        ②SENSOR_AVDD: EN 走 RC 延时 (R 100k: SYS→EN, C 1µF: EN→GND) ⇒ t=(100k‖500k)×1µF≈83ms
        #          ⇒ AVDD 最后上电 ⇒ 满足 IMX415 的 DVDD→OVDD→AVDD 顺序 (顺手解掉 ISS-152)
        if part.startswith("TPS7A20") or part.startswith("TPS62130A"):
            if ref == "U_LDO_S28":
                add("P1", "SYS_PCB", "RAIL_SYS", "R_EN_AVDD", "NET_LDO_EN_AVDD", "100k ±1%", "R", dnp,
                    "[推算]", "",
                    "[SENSOR_AVDD] ★EN 延时电阻 (SYS→EN) — ★P0: TPS7A20 的 EN 内部 500kΩ 下拉, 悬空=LDO 关断 ⇒ 必须显式驱动; "
                    "★本路给 EN 加 RC 延时 ⇒ **AVDD 最后上电** (满足 IMX415 的 DVDD→OVDD→AVDD 顺序); "
                    "时间常数 (100k‖500k)×1µF ≈ 83ms, 落在 datasheet 的 200ms 窗口内", cid)
                add("P1", "NET_LDO_EN_AVDD", "NET_LDO_EN_AVDD", "C_EN_AVDD", "C_EN_AVDD", "1µF", "C", dnp,
                    "[推算]", "",
                    "[SENSOR_AVDD] EN 延时电容 (EN→GND) — 与 R_EN_AVDD 构成 RC 延时 (★EN 内部 500k 下拉要并联算)", cid)
                add("P1", "GND", "C_EN_AVDD", "GND", "C_EN_AVDD", "1µF", "C", dnp, "[推算]", "",
                    "[SENSOR_AVDD] EN 延时电容 地端", cid)
                add("P1", "NET_LDO_EN_AVDD", "NET_LDO_EN_AVDD", "U_LDO_S28", "U_LDO_S28 EN", "EN", "NET", dnp,
                    "[官方]", "",
                    "[SENSOR_AVDD] ★U_LDO_S28 的 EN 脚 (由 RC 延时驱动 ⇒ 使 AVDD 最后上电) — "
                    "★★**P0: EN 悬空 = LDO 关断**", cid)
            else:
                add("P1", "SYS_PCB", "RAIL_SYS", ref, f"{ref} EN", "EN", "NET", dnp, "[官方]", "",
                    f"[{rail}] ★{ref} 的 EN 脚**直连 RAIL_SYS** ⇒ 永远使能 — "
                    f"★★**P0: EN 内部 500kΩ 下拉, 悬空 = 关断 ⇒ 不画 EN = 投板后整板不上电**; "
                    f"datasheet 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能 ⇒ 接 SYS (3.5-4.2V) 安全", cid)

'''
s = s.replace(anchor, en_block + anchor, 1)
open(GEN, 'w', encoding='utf-8').write(s)
print('[2] gen_netlist.py: 9 路电源 IC 的 EN 网络已补 (AVDD 走 RC 延时)')
