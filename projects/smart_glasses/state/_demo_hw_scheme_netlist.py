#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_hw_scheme_netlist.py —— 老板 19:25/19:35 硬件方案定案 → 网表落地 (demo 板形态)

决策来源: HW/DEMO_BOARD_HW_DECISION.md (2026-11-02 19:4x, 项目总工定案)
本脚本只做**机械且自洽**的三件事, 不碰判据强度:
  ① CONN_CAM / CONN_LIGHT 从"跨铰链(HINGE)"改成"主板上的板内 FPC 座(MAIN_PCB)"
     ⇒ 依据: 老板 19:25「sensor 模组 / 屏幕模组 通过 FPC 软排连到主板」+ 19:35「不跨铰链」
  ② CSI 保持 **2-lane 必装 + D2/D3 预留 DNP** (原网表已是此形态 ⇒ 决策一致, 无需改)
  ③ 充电链 (J_CHG / CONN_USB / CHG_BOARD) **保持原样** (属整机阶段的镜框充电板)
     ⇒ demo 阶段直接 USB 供电、不装电池 ⇒ 整机阶段再合并
门禁同步: check_netlist.py 的"跨铰链 4 个连接器标 HINGE"改成
          "camera/display FPC 在主板 + 充电链连接器仍属铰链界面(整机阶段保留)"
"""
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
CHK = f'{PROJ}/state/check_netlist.py'

# ───────────────────────── ① gen_netlist.py ─────────────────────────
s = open(GEN, encoding='utf-8').read()
orig = s

# 1.1 HINGE_REFS: 只留充电链两个连接器
old_hinge = 'HINGE_REFS = {"J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"}'
new_hinge = ('# ★★2026-11-02 19:4x demo 板形态 (老板 19:25/19:35): camera/display 改成**板内 FPC 座** ⇒ 不再跨铰链\n'
             '#   ⇒ HINGE 只剩**充电链**两个连接器 (J_CHG 充电 + CONN_USB) —— 那属整机阶段的镜框充电板\n'
             '#   ⇒ demo 板阶段: 充电链不装 (直接 USB 供电), camera/display 两个模组用 FPC 连主板\n'
             'HINGE_REFS = {"J_CHG", "CONN_USB"}')
assert old_hinge in s, 'HINGE_REFS 没找到'
s = s.replace(old_hinge, new_hinge, 1)

# 1.2 板级归属函数里的 CONN_CAM/CONN_LIGHT 分支 → 主板
old_attr = ('        if re.search(r"J_CHG|CONN_USB|CONN_CAM|CONN_LIGHT", blob):\n'
            '            return BOARD_HINGE')
new_attr = ('        # ★★2026-11-02 19:4x: camera/display 的 FPC 座在**主板** (不再跨铰链) ⇒ 不进 HINGE\n'
            '        if re.search(r"J_CHG|CONN_USB", blob):\n'
            '            return BOARD_HINGE')
assert old_attr in s, '板级归属里的铰链分支没找到'
s = s.replace(old_attr, new_attr, 1)

# 1.3 页标题
s = s.replace('"P5": "MIPI-CSI 传感器 (CONN_CAM 40p 跨铰链)"',
              '"P5": "MIPI-CSI 传感器 (CONN_CAM 40p **板内 FPC 座**, demo 阶段 2-lane)"', 1)
s = s.replace('"P9": "跨铰链界面 (4 组跨铰链通道 + 保护/滤波件 + 板级归属)"',
              '"P9": "跨铰链界面 (★demo 阶段仅充电链 USB+充电; camera/display 已改板内 FPC)"', 1)

# 1.4 连接器描述行 (CONN_CAM / CONN_LIGHT 的 note)
s = re.sub(r'"\[CONN_CAM\] 显示/光机↔主板连接器',
            '"[CONN_CAM] ★demo 2026-11-02 19:4x: 改**板内 FPC 座** (sensor 模组 ↔ 主板, 不跨铰链; 针位目标 0.5mm/24p 见 HW/DEMO_BOARD_HW_DECISION.md §4)\n        "[CONN_CAM] 显示/光机↔主板连接器', s)
s = re.sub(r'"\[CONN_LIGHT\] 显示/光机↔主板连接器',
            '"[CONN_LIGHT] ★demo 2026-11-02 19:4x: 改**板内 FPC 座** (屏幕模组 ↔ 主板, 不跨铰链; 针位目标 0.5mm/20p 见 HW/DEMO_BOARD_HW_DECISION.md §4)\n        "[CONN_LIGHT] 显示/光机↔主板连接器', s)

open(GEN, 'w', encoding='utf-8').write(s)
print('[1] gen_netlist.py 已改: HINGE_REFS 去掉 camera/display + 板级归属分支 + 页标题 + 连接器 note')

# ───────────────────────── ② check_netlist.py ─────────────────────────
c = open(CHK, encoding='utf-8').read()
m = re.search(r'    # ---- 14\) 跨铰链 4 个连接器必须标 HINGE\n(.*?)\n    chk\("跨铰链 4 个连接器标 HINGE", not bad_h,\n(.*?)\)\n', c, re.S)
assert m, '没找到 14) 跨铰链判据'
new_block = (
    '    # ---- 14) ★★2026-11-02 19:4x (demo 板形态): camera/display 的 FPC 座在**主板**, '
    '只有充电链两个连接器属铰链界面\n'
    '    #     ★依据: 老板 19:25「sensor 模组 + 屏幕模组 通过 FPC 软排连主板」+ 19:35「敲定硬件方案」\n'
    '    #     ★**判据强度不放松**: 改成"谁必须在主板 / 谁必须在铰链", 不是删判据\n'
    '    hinge_conn = {"J_CHG", "CONN_USB"}\n'
    '    main_fpc_conn = {"CONN_CAM", "CONN_LIGHT"}\n'
    '    bad_h = [r for r in rows\n'
    '             if cell(r, "ref") in hinge_conn and cell(r, "board") != "HINGE"]\n'
    '    bad_m = [r for r in rows\n'
    '             if cell(r, "ref") in main_fpc_conn and cell(r, "board") != "MAIN_PCB"]\n'
    '    chk("camera/display FPC 座在主板 (demo 形态, 不跨铰链)", not bad_m,\n'
    '        f"{len(bad_m)} 行归属不是 MAIN_PCB")\n'
    '    chk("充电链连接器仍标 HINGE (整机阶段镜框充电板)", not bad_h,\n'
    '        f"{len(bad_h)} 行归属不是 HINGE")\n')
c = c[:m.start()] + new_block + c[m.end():]
open(CHK, 'w', encoding='utf-8').write(c)
print('[2] check_netlist.py 判据已替换 (14 条: 跨铰链4个 → camera/display 在主板 + 充电链仍铰链)')
