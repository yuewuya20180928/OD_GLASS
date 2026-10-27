#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1.7 收口: 验收 sw-lead ISS-090 交叉评审 + 落 6 条裁决 + 并进 ISS-096/097/098"""
import json
import os
import shutil
import yaml

WS = "/home/yuewuya/.openclaw/workspace"
PRJ = os.path.join(WS, "projects/smart_glasses")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    t = p + ".tmp"
    with open(t, "w", encoding="utf-8") as f:
        f.write(s)
    os.replace(t, p)


# ---------- 1) DECISIONS ----------
dec = os.path.join(PRJ, "DECISIONS.md")
rows = """| 2026-10-27 | 项目总工 | **分压臂的值不许写 0Ω 跳线位** —— `R_SUPV_DIV1/2` 是分压上/下臂, 装 0Ω = V_SOC_IO 对地短路 (sw-lead ISS-090 抓到) → 值改成**电阻** (值随 V_SOC_IO 电压定) | [官方] 分压拓扑 + sw-lead 评审 | P8 电源监督链 |
| 2026-10-27 | 项目总工 | **RESET_N 的 RC 注记修正**: 1k × 100nF ⇒ **τ = 0.1ms** (我原来写 100ms, **错 1000 倍**) —— 复位释放几乎无延时, 上电时序必须靠 U_SUPV/PG 链, 不能指望 RC | [推算] RC 公式 | P8 |
| 2026-10-27 | 项目总工 | **VBUS_DET / BAT_DET 的 1M+1M 分压不可用** (源阻抗 500kΩ: 漏电 1µA→0.5V 误差 = 15%FS, ADC 建立时间 ~451ms) → 改 **100k+100k** (源阻抗 50kΩ, 误差 50mV) —— ★最终值待 SoC 的 ADC 采样要求 (TBD-02/原厂) | [推算] + sw-lead 评审 | P2 模拟检测 |
| 2026-10-27 | 项目总工 | **`CONN_USB` 的 pin4 由预留改 GND** (零成本): 跨铰链 USB 的回流脚与信号脚成对 (ISS-085 自定规则) → 4p = D+/D−/GND/**GND** | sw-lead 评审 + ISS-085 | P6/P9 |
| 2026-10-27 | 项目总工 | ★**TMP117 测点定案: 镜脚主 PCB 贴皮肤面一侧, SoC 投影 ≤10mm** —— 依据: ① ISO 13732-1 的 43°C 红线**唯一直接相关部位** ② 皮肤是热沉 ⇒ T_PCB ≥ T_skin (**保守方向**) ③ 自热 16.5µW 可忽略; 不选 die (测不到 Tj), 不选电池 (NTC→TS 已硬件停充) | sw-lead ISS-090 评审 (含 ISO 13732-1 推导) | P2 温度测点 / SW 温控策略 |
| 2026-10-27 | 项目总工 | **量产刷机改镜脚有线 pogo 刷写器** (镜脚已有 J_DEBUG/J_UART + ISS-092 检修口) —— 跨铰链 USB 救砖只作条件式可行 (枚举前提缺 VBUS + 回流脚要补) | sw-lead 评审 | 产线 / ISS-098 |
"""
write(dec, read(dec) + rows)
print("DECISIONS.md 已追加 6 条")

# ---------- 2) issue_log ----------
P = os.path.join(PRJ, "state/issue_log.yaml")
shutil.copy(P, P + ".bak_v17")
d = yaml.safe_load(open(P, encoding="utf-8"))
items = d["issues"]
by = {str(i.get("id")): i for i in items}


def app(iid, f, t):
    i = by[iid]
    o = (i.get(f) or "").rstrip()
    i[f] = (o + "\n" + t).strip() if o else t


i = by["ISS-090"]
i["status"] = "verified"
i["verify_by"] = "main"
i["fix_ref"] = ("SW/SW_TIMING_REVIEW.md (478 行) + SW/tools/timing_check.py (自检 21/21 rc=0) "
                "+ HANDOFF/2026-10-27_sw-lead_时序交叉评审.md (B1-B6)")
i["verify_result"] = (
    "2026-10-27 20:1x 项目总工逐条复核: ① 它的机械复核器自跑 rc=0 (21/21) ✅ "
    "② **它报的 3 条我逐条查了网表**: "
    "「R_SUPV_DIV 两颗 0Ω 同时装 → V_SOC_IO 对地短路」**成立, 但要说清是值层问题** —— 分压上/下臂的 value 写成了 0Ω 跳线位; "
    "拓扑本身是分压, 不是短路 (我在 V1.6 已把那行改名, 拓扑无短) → **裁决: 值改成电阻**; "
    "「RESET RC 的 τ 注释 100ms 实为 0.1ms」**成立且是我自己的错** (1k×100nF=0.1ms, 我写错 1000 倍) → 记 DECISIONS 待改; "
    "「1M+1M 分压 → 源阻抗 500kΩ / 漏电 0.5V 不可用」**成立** (确认 1M+1M) → 裁决改 100k+100k; "
    "「CONN_USB 只 1 个 GND 脚, pin4 改 GND 零成本」**成立** (确认 pin3=GND, pin4=预留) → 采纳; "
    "③ **TMP117 测点定案采纳** (镜脚主 PCB 贴皮肤面一侧, SoC 投影 ≤10mm; 依据: ISO 13732-1 43°C 红线唯一直接相关部位 "
    "+ 皮肤是热沉 ⇒ T_PCB≥T_skin 保守方向 + 自热 16.5µW 可忽略); "
    "④ 它在评审期间发现网表被并发重生 (419→476 行) 并**全部重跑复核**, 结论仍成立 —— 这个做法我认可; "
    "⑤ 合并器抓到的 thermal_control_tiers 冲突, 它拆成两个 key (Tj 口径 / 皮肤口径) 而没有改对方取值 → 正确; "
    "⑥ 17 条 SW 返工点 (11 条自主发现) 已接收, 架构级那条 (无硬件断电通路) 与 ISS-097 合并")
app("ISS-090", "note",
    "★项目总工已验收 (verify_by=main): 机械复核器 21/21 rc=0; 3 个关键数 2 条成立 1 条是值层问题(拓扑已修); "
    "TMP117 测点定案采纳; 9 项硬件请求并进 ISS-096+098; 3 项结构输入排队给 mech-lead")

add96 = (
    "\n★2026-10-27 20:1x 追加 (sw-lead ISS-090 评审的硬件请求, 项目总工裁决后并入本单): "
    "(1) `R_SUPV_DIV1/2` 的值不许写 0Ω 跳线位 (装上=短路) → 改成**电阻**, 值随 V_SOC_IO 电压定; "
    "(2) RESET RC 的 τ 注记 100ms → **0.1ms** (1k×100nF, 我写错 1000 倍) → 复位几乎无延时, 时序必须靠 PG/监督链; "
    "(3) `R_PU_CHG_STAT` 的 board 列错标 CHG_BOARD → **MAIN_PCB** (上拉轨在主板侧); "
    "(4) **EN/SS/CT/MR 脚全网表 0 条** → 上电时序链要补全 (含 CT 延时); "
    "(5) SoC 侧 USB **VBUS 检测脚**缺失 → 枚举前提 (含 'USB VBUS 是否需要' 的原厂问); "
    "(6) `CONN_USB` pin4 预留 → **改 GND** (跨铰链 USB 双回流, 零成本); "
    "(7) `R_VBUS_DET_1/2` 与 `R_BAT_DET_1/2` 的 1M+1M → **100k+100k** (源阻抗 50kΩ; 最终值待 SoC ADC 采样要求)")
app("ISS-096", "note", add96)
app("ISS-098", "note",
    "\n★2026-10-27 20:1x 追加: `CONN_USB` pin4 由预留改 **GND** (双回流, 零成本) —— 采纳 sw-lead 评审; "
    "另: 量产刷机路线**改镜脚有线 pogo 刷写器** (镜脚已有 J_DEBUG/J_UART + ISS-092 检修口) → 跨铰链 USB 救砖只作条件式可行")
app("ISS-097", "note",
    "\n★2026-10-27 20:1x sw-lead 评审并入 3 条**必须重定义**的语义: 售后『长按10s=关机』/ 老板锁死的『待机 <0.05W』/ "
    "关机时充电灯行为 —— 现状 (无负载开关) 下这三条都做不到真关机; 另: 热学换算由 sw-lead 复核 "
    "(0.05W → 37.5°C, 0.16W → 43.0°C 红线; timing_check.py 自检 21/21)")
d["issues"] = items
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False))
chk = yaml.safe_load(open(P, encoding="utf-8"))
print("issue_log 回读 OK, 总数", len(chk["issues"]))
for x in ("ISS-090", "ISS-096", "ISS-097", "ISS-098"):
    e = [y for y in chk["issues"] if y["id"] == x][0]
    print(f"  {x}: {e['status']} owner={e['owner']}")
