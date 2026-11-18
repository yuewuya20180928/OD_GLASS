#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss306_probe_board.py —— ISS-306 只读溯源探针 (★零写板 / 零落表 / 零改闸★)

用途:
  ① 复刻 `HW/check_netlist_selfconsistency.py` 的 `_read_board` / `_board_ref_xy` 口径
     (★逐字同源: 直接 import 该模块的私有函数, 不重写逻辑 ⇒ 口径不会漂★)
  ② 把 R3 / R4(×2) / R9 四条红各自的【机器读数】打出来 (哪条红 = 哪个事实)
  ③ 回答 B3: R9 的 47.99 mm 是【现状事实】还是【判据算错】
  ④ 回答 B1/B2: 哪些 ESD 位号挂在 D− 那条网上 (hit 列表为空 ⇒ D− 裸奔)

边界: 只 open(..., "r"); 不写任何文件。
"""
from __future__ import annotations
import importlib.util
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")

spec = importlib.util.spec_from_file_location(
    "cns", os.path.join(ROOT, "HW", "check_netlist_selfconsistency.py"))
cns = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cns)

board = cns._read_board(BOARD)
xy = cns._board_ref_xy(BOARD)

print("=" * 78)
print("ISS-306 只读探针 · 板文件读数")
print("=" * 78)
print(f"板文件: {BOARD}")
print(f"ESD_MAX_DIST_MM (R9 阈值常量) = {cns.ESD_MAX_DIST_MM}")
print()

print("★① 板上全部含 'ESD' 的位号 (R4 的扫描范围 = ref 含 ESD) ★")
for ref in sorted(board):
    if "ESD" not in ref.upper():
        continue
    info = board[ref]
    print(f"  {ref:16s} pads={info['pads']}  value={info['value']!r}")
    for num, net in info["pads_list"]:
        print(f"       pad{num} -> {net!r}")

dminus = {"USB_D_N_SRC", "NET_USB_D_N_TYPEC"}
hit = []
for ref, info in board.items():
    if "ESD" not in ref.upper():
        continue
    for _num, pnet in info.get("pads_list", []):
        if pnet in dminus:
            hit.append((ref, pnet))
            break
print()
print("★② R4 判据复刻 (L1359~L1378) ★")
print(f"  dminus 集合 = {sorted(dminus)}")
print(f"  hit (D− 上挂了 ESD 的位号) = {hit}   ⇒ len={len(hit)}")
print(f"  ⇒ 判据行1「没有任何 ESD 位号挂在 D− 那条网上」: "
      f"{'判红 (真)' if not hit else '判绿'}")
if "D_ESD_USB_D" in board:
    info = board["D_ESD_USB_D"]
    fires = info["pads"] < 3 and not hit
    print(f"  D_ESD_USB_D pads={info['pads']} (<3 且 not hit ⇒ {fires}) "
          f"⇒ 判据行2「仍然只有 2 个焊盘」: {'判红 (真)' if fires else '判绿'}")
    print(f"  ★★ 关键耦合: 判据行2 的触发条件是 `info['pads'] < 3 and not hit`")
    print(f"     ⇒ 它【不是】独立要求 D_ESD_USB_D 必须 3 脚 ⇒ 只要 D− 上出现【任何】ESD 位号, 行2 自动转绿")
    print(f"     ⇒ 行2 是行1 的【派生句】, 不是第二条独立要求")

print()
print("★③ R9 距离 (逐字复刻 L1446~L1460) ★")
if "J_USB_C" in xy and "D_ESD_USB_D" in xy:
    a, b = xy["J_USB_C"], xy["D_ESD_USB_D"]
    d = math.hypot(a[0] - b[0], a[1] - b[1])
    print(f"  J_USB_C      原点 = {a}")
    print(f"  D_ESD_USB_D  原点 = {b}")
    print(f"  距离 = hypot(dx={a[0]-b[0]:.2f}, dy={a[1]-b[1]:.2f}) = {d:.2f} mm")
    print(f"  阈值 = {cns.ESD_MAX_DIST_MM} mm ⇒ {'判红 (真)' if d > cns.ESD_MAX_DIST_MM else '判绿'}")
    print(f"  ★ 要挪到 ≤{cns.ESD_MAX_DIST_MM} mm ⇒ 至少要挪 {d - cns.ESD_MAX_DIST_MM:.2f} mm")
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    tgt = (a[0] + ux * cns.ESD_MAX_DIST_MM, a[1] + uy * cns.ESD_MAX_DIST_MM)
    print(f"  [推算] 沿 J_USB_C→D_ESD_USB_D 直线方向平移, 落位候选 ≈ "
          f"({tgt[0]:.2f}, {tgt[1]:.2f})  [★推算, 非实测★]")
else:
    print("  板上找不到 D_ESD_USB_D 或 J_USB_C 的坐标")

print()
print("★④ R3: 板封装 U_EN_SW 的 Value 属性 ★")
if "U_EN_SW" in board:
    bv = cns._norm(board["U_EN_SW"].get("value"))
    bad = bv in ("EN 输入 (高=放行底板)", "5V 输入", "5V 输出 (受 CARRIER_BOARD_EN 门控)", "GND")
    print(f"  U_EN_SW.value = {board['U_EN_SW']['value']!r}")
    print(f"  _norm 后 = {bv!r}")
    print(f"  ∈ 脚级功能串黑名单 = {bad} ⇒ 判据行: {'判红 (真)' if bad else '判绿'}")
    print(f"  ★ 该属性写在【板文件 footprint 块】里 ⇒ 改它 = 改板 ⇒ 同趟消化")
else:
    print("  板上找不到 U_EN_SW")

print()
print("★⑤ D− 两条网 (USB_D_N_SRC / NET_USB_D_N_TYPEC) 在板上的所有连接点 ★")
for target in sorted(dminus):
    owners = []
    for ref, info in board.items():
        for num, net in info.get("pads_list", []):
            if net == target:
                owners.append(f"{ref}.pad{num}")
    print(f"  {target:24s} -> {owners}")

print()
print("=" * 78)
print("探针结束 (只读; 本脚本未写任何文件)")
print("=" * 78)
