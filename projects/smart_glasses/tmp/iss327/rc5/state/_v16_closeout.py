#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1.6 收口: 裁决 P10 数据 (4 条) + 落地 P10 子 agent 要我动的 3 处 + 修它发现的 2 个主网表缺陷"""
import json

# ---------- A) 裁决 P10 数据里的 4 条 ----------
p = 'state/p10_rows.json'
d = json.load(open(p, encoding='utf-8'))

def rows_by(ref=None, net=None):
    out = []
    for r in d:
        if ref and r['ref'] != ref:
            continue
        if net and r['net'] != net:
            continue
        out.append(r)
    return out

def app(r, txt):
    r['note'] = ((r.get('note') or '') + ' ' + txt).strip()

n = 0
# ① VSYS (pin15/16) → NC
for r in rows_by(net="SYS_CHG"):
    r['dnp'] = "DNP"
    app(r, "★裁决 (PM): 电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 → **VSYS 脚不接 (NC)**; "
           "充电路径 = IN → 内部 BATFET → BAT → 跨铰链 → 电芯 (反向阻断由 BATFET 提供); "
           "★若 TI 数据手册要求 VSYS 必接, 则要把镜脚 SYS 经 J_CHG pin9/10 引过来 (会多两根电源 pin) → 记为后继项")
    n += 1
# ② R_STAR_PGND 必装 + 铜皮口径
for r in rows_by(ref="R_STAR_PGND"):
    r['value'] = "0Ω / 铜皮短接 (PGND 单点星接)"
    app(r, "★裁决 (PM): **必装** (DNP 会让 PGND 整个悬空 = 硬伤); 但 **1A 回流不要走 0402 0Ω** "
           "(0.1V/0.1W) → 实际用**铜皮短接**做单点星接, 0Ω 只作选装位")
    n += 1
# ③ I2C 上拉 必装 (本板自闭环)
for r in rows_by(ref="R_PU_SCL") + rows_by(ref="R_PU_SDA"):
    r['dnp'] = "必装"
    app(r, "★裁决 (PM): **必装** —— 充电 IC 的 I2C 本板自闭环 (不跨铰链, 见 J_CHG pin9/10 预留); "
           "上拉挂 REGN 5V (充电板唯一的逻辑轨); 将来若要在线配置再引到镜脚")
    n += 1
# ④ D_TVS_VBUS 必装
for r in rows_by(ref="D_TVS_VBUS"):
    r['dnp'] = "必装"
    app(r, "★裁决 (PM): **必装** (Type-C 入口 TVS 是标配); VRWM 5-6V 档, **脉冲电流额定 ≥3A** "
           "(PD 5V/2A 场景); 选型待定 [待选型]")
    n += 1
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"P10 JSON 已裁决 {n} 行 (VSYS→NC / PGND 必装+铜皮 / I2C 上拉必装 / TVS 必装)")

# ---------- B) 主网表 ----------
g = 'state/gen_netlist.py'
s = open(g, encoding='utf-8').read()

def rep(o, nw):
    global s
    assert o in s, "NOT FOUND: " + o[:70]
    s = s.replace(o, nw)

rep('"U_CHG BAT"', '"U_CHG pin13+pin14"')
rep('"U_CHG TS"', '"U_CHG pin11"')
rep('"U_CHG REGN"', '"U_CHG pin22"')
rep('"U_CHG IINLIM"', '"U_CHG pin10"')
rep('''    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
}''', '''    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
    # ★V1.6: P10 充电板页新增的件 (BQ25896 外围) 全在镜框充电板
    "R_PSEL", "R_CE", "R_OTG", "R_PU_SCL", "R_PU_SDA", "R_PU_INT", "R_STAR_PGND",
    "C_VBUS_IC", "C_PMID", "C_BST", "C_BAT", "C_SYS", "L_CHG", "D_TVS_VBUS", "TP_TS",
    # ★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**
    #   (充电板 VBUS 不过铰链到主板 → 分压放在主板 = 采不到电)
    "R_VBUS_DET_1", "R_VBUS_DET_2",
}''')
rep('''    add("P1", "TS_BAT", "R_NTC_BAT", "BAT_PROT_CELL", "R_NTC_BAT", "103AT NTC ±1% (贴电芯)",''',
    '''    add("P1", "TS_BAT", "R_NTC_BAT", "GND", "R_NTC_BAT", "103AT NTC ±1% (贴电芯, 另一端接电芯负极=系统 GND)",''')
rep('''"(与 30.31k 并联构成温度检测网络)", "C-01")''',
    '''"(与 30.31k 并联构成温度检测网络); ★V1.6 修正: NTC 另一端按 datasheet 三件式接 **GND** (电芯负极侧), 原来接电芯正极 = 与分压公式不符", "C-01")''')
open(g, 'w', encoding='utf-8').write(s)
print("gen_netlist.py: U_CHG 4 脚显式化 + 15 新件归充电板 + VBUS 分压挪充电板 + NTC 改接 GND")

# ---------- C) gen_bom: DNP 计数口径统一 ----------
b = 'state/gen_bom.py'
t = open(b, encoding='utf-8').read()
o = '''    dnp_net = len({r["ref"] for r in rows if r.get("ref") and r.get("dnp") == "DNP"})'''
nw = '''    # ★口径与 BOM 侧一致 (2026-10-27 19:5x, P10 子 agent 指出): **所有行都 DNP 才算不装**
    by_ref_dnp: dict[str, set] = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            by_ref_dnp.setdefault(ref, set()).add(r.get("dnp") or "")
    dnp_net = sum(1 for v in by_ref_dnp.values() if v == {"DNP"})'''
assert o in t
t = t.replace(o, nw)
open(b, 'w', encoding='utf-8').write(t)
print("gen_bom.py: DNP 计数口径已统一")
