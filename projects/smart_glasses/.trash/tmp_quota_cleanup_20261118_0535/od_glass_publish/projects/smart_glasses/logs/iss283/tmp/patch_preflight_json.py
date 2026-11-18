#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-283 · cont2 · 板侧清单 JSON 块改写 (★加 B32 + 更新 B11 / B30★)"""
import json
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md")

txt = open(P, encoding="utf-8").read()
m = re.search(r"(```json\s*)(\{.*?\})(\s*```)", txt, re.S)
if not m:
    raise SystemExit("找不到 JSON 块")
raw = m.group(2)
obj = json.loads(raw)
# ★先确认往返不改变原文 (★不许顺手重排整个块★)★
rt = json.dumps(obj, ensure_ascii=False, indent=2)
if rt.strip() != raw.strip():
    print("⚠ 往返不一致 ⇒ 原块不是 indent=2 格式 ⇒ 手工改", file=sys.stderr)
    sys.exit(2)

by = {i["id"]: i for i in obj["items"]}

# ── ① B32_V2_NET_RENAME (★§③-1★) ──
assert "B32_V2_NET_RENAME" not in by
b32 = {
    "id": "B32_V2_NET_RENAME",
    "source_iss": "ISS-283",
    "title": "V-2 网改名: D_ESD_USB_D pad1 网名 USB_D_P_SRC → NET_USB_D_P_TYPEC ⇒ 板面 3 处焊盘网名必须同趟改 (★§③-1★)",
    "current_state": "[实测] 网表 L417 已落 NET_USB_D_P_TYPEC (★台账 §16.2 链头 L1353 · ISS-283 · 12:16:08★); 板面仍挂旧网名 USB_D_P_SRC 的焊盘 3 处: D_ESD_USB_D.pad1 / R_SER_USB_D_P 一端 / J_SOM_P1 的 USB_D_P 脚 ⇒ 网表与板对不上",
    "action": "板那一趟把这 3 处焊盘网名同趟改成 NET_USB_D_P_TYPEC (★不改 ⇒ 网表与板对不上★) ⇒ 见板侧清单 §③-1; ★本单零写板★",
    "criterion": "python3 HW/check_board_frame_caliber.py ⇒ C6 绿 (★盘上 md5 == 落表台账登记★)",
    "step": "S4",
    "blocked_by": "板只改一次那一趟 (★本单零写板★)",
    "evidence": "[实测]",
}
# ★插在 B09 之后 (★保持 §2 表的顺序★) ★
idx = next(i for i, it in enumerate(obj["items"]) if it["id"] == "B09_ESD_USB_D_MINUS")
obj["items"].insert(idx + 1, b32)

# ── ② B11_Q_PG_LAND: 网表 note 已落写法A ⇒ 只剩板那一趟重画 land (★§③-2★) ──
b11 = by["B11_Q_PG_LAND"]
b11["title"] = ("Q_PG 占位 land 序错 (开不了机) ★**网表 note 已落写法A "
                "(★ISS-283·12:30:23★) ⇒ 只剩板那一趟重画 land (★§③-2★)**★")
b11["current_state"] = (
    "[实测] 板: pad1=PWR_ON(S) / pad2=BAT_SW(D) / pad3=PWR_GOOD(G) = S/D/G; "
    "DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 ⇒ 写法B ⇒ Vgs=0 不导通, "
    "PG 高时 Vgs=+3.3V 反偏 ⇒ 开机路径彻底不通; "
    "★**网表 note 已落写法A: pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D) "
    "(★台账 §16.2 链头 L1353 · ISS-283 · 12:30:23★) ⇒ 板面与网表对不上**★")
b11["action"] = ("板那一趟重画 Q_PG 的 3 根线 (★pad1→PWR_GOOD(G) / pad2→BAT_SW(S) / pad3→PWR_ON(D)★) "
                 "+ 网表 note 角色已于 2026-11-17 12:30:23 同批落成写法A (★S=BAT_SW / D=ON / G=PG★)")
b11["blocked_by"] = ("★**写法A 已拍 (★老板 2026-11-17 09:49★) + 网表 note 已落表 "
                     "(★台账 §16.2 链头 L1353·12:30:23★) ⇒ 只剩板那一趟重画这 3 根线**★")

# ── ③ B30_LED_BRIGHTNESS: G-5 已拍 = 20mA 档 且已落表 ──
b30 = by["B30_LED_BRIGHTNESS"]
b30["title"] = ("LED 亮度档 G-5 **已拍 = 20mA 档** (R_LED_R 68Ω / R_LED_G 55Ω) "
                "★**已落表 (★ISS-283·12:30:23★) ⇒ 板那一趟只须重出 BOM "
                "(footprint 不变 ⇒ 不构成额外板改)**★")
b30["current_state"] = (
    "[实测] G-5 已拍「选项 ② = 改 R 到 20 mA 档」⇒ 已落表: R_LED_R = 68Ω ±1% / "
    "R_LED_G = 55Ω ±1% ⇒ 单颗 ~20 mA · 功耗 2.2 mW→66 mW (★两颗 ≈ 0.13 W 进电池账★) · "
    "亮度 ×14 ⇒ IEC 62471 分级要重算 (★已登记 need·不代拍★); "
    "★旧 1kΩ + 3.3V ⇒ 1.10 mA ⇒ KP-2012SGC 仅 0.7~0.9 mcd ⇒ 白天看不见 "
    "(★已被 20 mA 档取代★)★")
b30["action"] = ("落表已完成 (★R 值写进 BOM ⇒ 台账 §16.2 链头 L1353★) ⇒ 板那一趟只须重出 BOM + 投产包 "
                 "(★footprint 不变 ⇒ 不构成额外板改★) ⇒ 另: IEC 62471 分级重算登记给 main (★不代拍★)")
b30["criterion"] = ("python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 且条数不变 "
                    "(★20mA 档已落表; 板侧项归 §③-1~§③-3★)")
b30["blocked_by"] = ("★**已拍 (★老板 2026-11-17 09:49·A5 = 20mA★) ⇒ 剩【IEC 62471 分级重算】"
                     "登记给 main (★不代拍★)**★")
b30["evidence"] = "[实测]+[官网]"

new = json.dumps(obj, ensure_ascii=False, indent=2)
txt2 = txt[:m.start(2)] + new + txt[m.end(2):]
open(P, "w", encoding="utf-8").write(txt2)
print("✔ JSON 块已改写 · items = %d" % len(obj["items"]))
print("  新增: B32_V2_NET_RENAME")
print("  更新: B11_Q_PG_LAND / B30_LED_BRIGHTNESS")
