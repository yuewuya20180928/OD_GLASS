#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_map_som_pins.py —— A2 段准备: 把网表里的 SoC 节点自动映射到 SOM 座的针号

背景: A1 段已把两个 FPC 座改成真实针位 (31p/0.3mm + 40p/0.5mm), 板子 DRC=0 且与网表逐点等价。
      A2 段 = **主板上放一颗 RK3572 核心板 (Forlinx FET3572-C, 4×100pin/0.4mm BTB)** ⇒
      ★**网表里所有 `SoC[RK3572].<信号>` 必须改挂到 SOM 座的对应针脚** (SoC 集成在 SOM 上, 主板不直连 SoC)。
      ⇒ 映射依据 = `HW/PCB/FET3576C_PIN_TABLE.csv` (399 行: num / ball / 电平 / **signal (SoM 侧网名)** / net_or_desc)

本脚本只做**映射与核对** (不改网表) ⇒ 输出:
  ① 逐条映射表 (netlist 节点 → SOM 针号 + SoM 侧网名 + 电平 + ball)
  ② **未映射清单** ⇒ 这些要么名字对不上, 要么 RK3572 上没有 ⇒ ★**这是 A2 段真正需要人看的部分**
"""
import csv
import json
import os
import re
from collections import defaultdict

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
PIN_CSV = f'{PROJ}/HW/PCB/FET3576C_PIN_TABLE.csv'
NET_CSV = f'{PROJ}/HW/netlist_v1.csv'
OUT_MD = f'{PROJ}/HW/PCB/SOM_PIN_MAPPING.md'
OUT_JSON = f'{PROJ}/HW/PCB/SOM_PIN_MAPPING.json'


def norm(s):
    """把信号名归一化, 便于跨命名体系匹配"""
    s = (s or '').upper()
    s = s.replace('MIPI_DPHY_', '').replace('MIPI_DPHY', '')
    # ★我们: CSI_D0_D3_P / DSI_TX_D3_P / DSI_D0_CK_P ...  他们: MIPI_DPHY_CSI_RX_D3P / MIPI_DPHY_DSI_TX_D3P
    s = re.sub(r'^CSI_', 'CSI_RX_', s)
    s = re.sub(r'^DSI_', 'DSI_TX_', s)
    s = re.sub(r'^DSI_TX_', 'DSI_TX_', s)
    s = s.replace('CK_P','CKP').replace('CK_N','CKN')
    s = re.sub(r'_P$', 'P', s)
    s = re.sub(r'_N$', 'N', s)
    s = re.sub(r'D(\d)P', r'DP', s)
    s = re.sub(r'[^A-Z0-9]', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


def main():
    rows = list(csv.DictReader(open(PIN_CSV, encoding='utf-8')))
    by_sig = {}
    for r in rows:
        sig = (r.get('signal') or '').strip()
        if not sig or sig in ('——', '---'):
            continue
        key = norm(sig)
        by_sig.setdefault(key, []).append(r)

    net_rows = list(csv.DictReader(open(NET_CSV, encoding='utf-8')))
    soc_nodes = defaultdict(set)
    for r in net_rows:
        for col in ('node1', 'node2'):
            n = (r.get(col) or '').strip()
            if n.startswith('SoC[RK3572].'):
                soc_nodes[n[len('SoC[RK3572].'):]].add(n)

    mapped, unmapped = [], []
    for node in sorted(soc_nodes):
        key = norm(node)
        cands = by_sig.get(key)
        if not cands:
            # 退化: 后缀匹配 (例如 DSI_TX_CK_P → MIPI_DPHY_DSI_TX_CK_P)
            cands = [r for k, v in by_sig.items() if k.endswith(key) or key.endswith(k)
                     for r in v]
        if cands:
            r = cands[0]
            mapped.append({"node": node, "som_pin": r.get('num'), "ball": r.get('ball'),
                           "som_signal": r.get('signal'), "vol": r.get('vol') or '—',
                           "desc": (r.get('desc') or '')[:60]})
        else:
            unmapped.append({"node": node})

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write("# SoC 节点 → SOM 座针号 映射表 (A2 段用)\n\n")
        f.write(f"★**来源**: `HW/PCB/FET3576C_PIN_TABLE.csv` (Forlinx FET3576-C 逐针 399 行; ★**FET3572-C 与 FET3576-C 引脚兼容**)\n")
        f.write(f"★**网表里的 SoC 节点共 {len(soc_nodes)} 个** ⇒ 已映射 **{len(mapped)}** / 未映射 **{len(unmapped)}**\n\n")
        f.write("## ① 已映射\n\n| 网表节点 | SOM 针号 | ball | SoM 侧网名 | 电平 | 说明 |\n|---|---|---|---|---|---|\n")
        for m in mapped:
            f.write(f"| `{m['node']}` | **{m['som_pin']}** | {m['ball']} | `{m['som_signal']}` | {m['vol']} | {m['desc']} |\n")
        f.write("\n## ② ★未映射 (A2 段真正要人看的部分)\n\n")
        if not unmapped:
            f.write("★无 —— 全部 SoC 节点都能在逐针表里找到。\n")
        else:
            f.write("| 网表节点 | 说明 |\n|---|---|\n")
            for u in unmapped:
                f.write(f"| `{u['node']}` | ★**逐针表里没有同名/后缀相同的信号** ⇒ 要么是 RK3572 内部命名不同, 要么该信号在 FET3576-C 上不存在 (⇒ 需换引脚或换板) |\n")
        f.write("\n## ★A2 段怎么用这张表\n")
        f.write("1. 网表里每个 `SoC[RK3572].<节点>` 改成 `SOM_<pin号>` (走 4×100pin/0.4mm BTB 座)\n")
        f.write("2. ★**焊盘宽度 ≤0.18mm** (0.4 间距 − 0.18 = 0.22 > 0.2 clearance) ⇒ 本段唯一几何硬约束\n")
        f.write("3. ★**未映射的节点逐条解决** (换引脚 / 换板 / 删功能)\n")
        f.write("4. ★**F13**: pin87 `CARRIER_BOARD_EN` ⇒ 主板 3.3V/5V 主开关由它驱动 (不直连)\n")
    json.dump({"mapped": mapped, "unmapped": unmapped}, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"★ SoC 节点 {len(soc_nodes)} 个 ⇒ 已映射 {len(mapped)} / 未映射 {len(unmapped)}")
    for u in unmapped[:18]:
        print(f"    未映射: {u['node']}")
    print(f"→ {OUT_MD}")


if __name__ == '__main__':
    main()
