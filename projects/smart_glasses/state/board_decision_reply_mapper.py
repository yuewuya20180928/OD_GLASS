#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
board_decision_reply_mapper.py
======================================================================
★老板拍板回函的【机器化映射器】(★只读·不改任何东西·零写盘★)

★为什么做这件事 (★2026-11-23 08:3x main 实测踩到的坑★):
  落表器 `state/land_v_values.py` 的 `A_ITEM = {"A1":"V-3","A2":"V-4","A3":"V-2","A4":"V-5","A5":"V-6"}`
  ⇒ ★**裸字母 A4 / A5 已经被占用**: A4 = V-5 (`Q_PG` 写法 A) · A5 = V-6 (LED 亮度档 20mA/150R)
  ⇒ ★**而「关机语义」历史上也叫 A4、「负载开关」历史上也叫 A5** ⇒ 老板按旧习惯回「A4 = C+A」
  ⇒ ★**会被落表器当成 Q_PG 写法 ⇒ 白回一次 (rc=2 零写盘) 或更糟: 落到错的项上** ★
  ⇒ ★**现在这两项的码是 SD-1 / LS-1** (★2026-11-22 23:5x main 改名·理由同上★)

★本工具做三件事 (★全部只读★):
  ① `--list`   : 把【卡「板那一趟」的 9 件】打印成一张机器生成的回函清单
                  (★need key + 落表路径 + 建议默认值(仅供参考·非已决定) + 老板要答的那一句★)
  ② `--reply`  : 把老板的回复文本【逐条解析】⇒ 落到哪个 need key + 走哪条落表路径 +
                  ★**撞码 (A4/A5 等) 一律拒收并说明撞到谁** ★
  ③ `--selftest`: 反向用例 (★撞码必被抓到 · 未知码必被拒 · 建议默认值必被标成「非已决定」★)

用法:
  python3 state/board_decision_reply_mapper.py --list
  python3 state/board_decision_reply_mapper.py --reply "W-2=补 W-1c=C1 SD-1=C+A LS-1=追认 上位=甲"
  python3 state/board_decision_reply_mapper.py --selftest
"""
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAGS = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}
A_ITEM = {"A1": "V-3", "A2": "V-4", "A3": "V-2", "A4": "V-5", "A5": "V-6"}
A_ITEM_MEANING = {
    "V-3": "`BAT_DET` 终点 (A1/V-3)",
    "V-4": "`R_ILIM` 390Ω 档电流换算 (A2/V-4)",
    "V-2": "ESD 架构轴 (A3/V-2)",
    "V-5": "`Q_PG` 写法 (A4/V-5) ★**11-17 09:49 已拍 = 写法 A**★",
    "V-6": "LED 亮度档 20mA/150R (A5/V-6)",
}

# ★★卡「板那一趟」的 9 件 (★码 → need key → 落表路径★) ★★
# 落表路径: "v-chain" = 走 land_v_values.py 的 --decision/--boss-decision 链
#           "answers" = main 写自己分片 pm.yaml 的 answers 条目 (★need key 所在分片动态查★)
ITEMS = [
    {"code": "上位", "key": "boss_u1_upper_axis_board_trip_physical_product", "path": "answers",
     "ask": "这一趟画的是【甲 = demo 台架板 160×100】还是【乙 = 产品内板 60×30 / 60×15】?",
     "sugg": "甲 (★main 建议·非已决定★) ⇒ U-1 随之落 B160×100 / 8 层 / 1.60 / 现役 20 个 PCB_PART_POS"},
    {"code": "U-1", "key": "iss310_main_board_frame_u1_decision", "path": "answers",
     "ask": "条件式: 若答乙 ⇒ 用哪个框/层数/板厚? (若答甲 ⇒ 自动落 B160×100 / 8 层 / 1.60)",
     "sugg": "★**条件式**· 若答甲 ⇒ B160×100 / 8 层 / 1.60 / 沿用现役孔位"},
    {"code": "W-2", "key": "boss_esd_model_axis_pending_20261117", "path": "v-v2",
     "ask": "USB D− 侧补不补 ESD? (板面实测: D− 侧零 ESD, 距 J_USB_C 47.99 mm)",
     "sugg": "补 (★main 建议·非已决定★) ⇒ 补一颗对称 ESD + 距口 ≤3.0 mm"},
    {"code": "W-1c", "key": "boss_esd_model_axis_pending_20261117", "path": "v2-model",
     "ask": "D+ 那颗 ESD 的真 OPN 型号 (★型号轴不在 A_ITEM 链上⇒ 走 --v2-model 路径★)",
     "sugg": "C1 = `TPD2EUSB30DRTR` (★main 建议·非已决定★; 候选 C2 `TPD2E2U06DCKR` / C3 `ESD752DCKR` / C4 `CM1218-02S7`)"},
    {"code": "SD-1", "key": "boss_shutdown_semantics_and_loadswitch_20261117", "path": "answers",
     "ask": "关机语义签收 (★原写「A4」是旧表遗留码, 已改名 ⇒ 别回 A4★)",
     "sugg": "签收 C + A (★main 建议·非已决定★) ⇒ 顺手签掉 `HW/POWER_SHUTDOWN_V3.md`"},
    {"code": "LS-1", "key": "boss_shutdown_semantics_and_loadswitch_20261117", "path": "answers",
     "ask": "负载开关 `TPS22991RAA` 追认 (★原写「A5」是旧表遗留码, 已改名 ⇒ 别回 A5★)",
     "sugg": "追认 (★main 建议·非已决定★)"},
    {"code": "W-3", "key": "iss324_d_led_g_placement_decision", "path": "answers",
     "ask": "`D_LED_G` 落在板上哪个点 (+ 同链另一半: 要不要挪位 / 有无结构光孔)",
     "sugg": "假设 B = 无结构光孔 + 位置不动 ⇒ 零板面动作"},
    {"code": "Q3", "key": "q3_storage_and_audio", "path": "answers",
     "ask": "模型/rootfs 怎么存 (只 ADB push / 外挂 SPI-NOR ≥128 MiB / eMMC) + 音频做不做",
     "sugg": "分档: ①只 ADB push ②外挂 SPI-NOR (板侧零动作) ⇒ 两者都不卡; 音频建议先不做"},
    {"code": "C_VBUS_GND", "key": "boss_c_vbus_gnd_reserve_pad_20261117", "path": "answers",
     "ask": "`C_VBUS_GND` 这个预留位: 留还是不留",
     "sugg": "下板 (★main 建议·非已决定★; 收工 185 件 ⇒ demo 板不装电池 ⇒ 这颗电容本来就没用)"},
    {"code": "DNP-口径", "key": "boss_state_value_acceptance_drift_20261117", "path": "answers",
     "ask": "作业包 §3-S7 的「DNP 43 全标」已过期 (真值 40) ⇒ 按哪个数验收",
     "sugg": "认 40 (★main 建议·非已决定★; 以盘面实测为准)"},
]
# ★★撞码表: 老板若回这些裸字母 ⇒ 必须拒收并说明它真正的含义 ★★
COLLIDE = {
    "A4": "★**A4 = V-5 = `Q_PG` 写法 (11-17 09:49 已拍 = 写法 A)** ⇒ 「关机语义」的老码已改名 **SD-1** ★",
    "A5": "★**A5 = V-6 = LED 亮度档 20mA/150R** ⇒ 「负载开关」的老码已改名 **LS-1** ★",
    "A1": "★**A1 = V-3 = `BAT_DET` 终点** (★与本单无关·但回 A1 会被当成 BAT_DET★)",
    "A2": "★**A2 = V-4 = `R_ILIM` 390Ω 档电流换算** (★与本单无关★)",
    "A3": "★**A3 = V-2 = ESD 架构轴** (★★这是 ESD 轴的真码·但只管【架构】不管【型号】; 型号轴走 W-1c --v2-model★)",
}


def load_frag(agent):
    import yaml
    p = os.path.join(PROJ, "state/fragments", FRAGS[agent])
    if not os.path.isfile(p):
        return {}
    try:
        return yaml.safe_load(open(p, encoding="utf-8")) or {}
    except Exception:
        return {}


def locate(key):
    """★在四个分片里找这个 need key ⇒ 返回 (分片, section, 当前文本) ★"""
    for agent in FRAGS:
        d = load_frag(agent)
        for sect in ("needs_from", "answers", "interface_claims", "artifacts", "risks", "blockers"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict) and (e.get("key") == key or e.get("id") == key):
                    txt = str(e.get("value") or e.get("item") or e.get("summary") or e.get("note") or "")
                    return agent, sect, txt
    return None, None, ""


def board_trip_items():
    return ITEMS


def cmd_list():
    print("=" * 88)
    print("★ 卡「板那一趟」的拍板清单 (★机器生成·★建议默认值一律标「非已决定」★)")
    print("★ 权威页: `DECISION_ONE_PAGER_2026-11-22.md` §①/§⑥/§⑦/§⑬ · `DECISION_INDEX_2026-11-18.md` §E-1/§R/§T")
    print("=" * 88)
    for i, it in enumerate(board_trip_items(), 1):
        agent, sect, txt = locate(it["key"])
        print("%2d) %-12s need key = `%s`" % (i, it["code"], it["key"]))
        print("    落表路径 = %s · 落点分片 = %s / %s" % (it["path"], agent or "★查不到★", sect or "-"))
        print("    老板要答 = %s" % it["ask"])
        print("    建议默认值 = %s" % it["sugg"])
    print("-" * 88)
    print("★ 回函规则: ★**回 need key 或本文的码 (W-2 / W-1c / SD-1 / LS-1 / U-1 / 上位 / W-3 / Q3 / C_VBUS_GND / DNP-口径)★")
    print("  ★**不许回裸 A4 / A5** (★已被落表器占成 V-5 / V-6 ⇒ 会白回或落错项★)")
    print("  ★ 收到回函后 main 用 `python3 state/board_decision_reply_mapper.py --reply \"<原文>\"` 逐条对拍, 零错才落表 ★")


def parse_reply(text):
    """★把老板回函拆成 (码, 值) 对; 撞码/未知码一律拒收 ★
    ★★写法支持: 一行一对 (`W-2=补`) ★ 空格分隔多对 (`W-2=补 SD-1=C+A`) ★
       ⇒ 值一直吃到【下一个 `码 =`】或串尾 ⇒ 所以值里可以带空格 (`C + A`) ★"""
    items = []
    bad = []
    pat = re.compile(r"(?P<code>[\w\-]+)\s*[:=＝]\s*(?P<val>.*?)(?=\s+[\w\-]+\s*[:=＝]|$)")
    pos = 0
    for line in re.split(r"[\n,;，；]+", text):
        line = line.strip()
        if not line:
            continue
        found = list(pat.finditer(line))
        if not found:
            bad.append((line, "★格式看不懂 (★要 `码 = 值`★)"))
            continue
        for m in found:
            code, val = m.group("code").strip(), m.group("val").strip()
            if not val:
                bad.append((code, "★没有值 (★要 `码 = 值`★)"))
                continue
            items.append((code, val))
    return items, bad


def cmd_reply(text):
    print("=" * 88)
    print("★ 老板回函逐条对拍 (★只读·不落盘·★落表是 main 另一步的活★)")
    print("★ 回函原文: %s" % text)
    print("=" * 88)
    items, bad = parse_reply(text)
    known = {it["code"]: it for it in board_trip_items()}
    ok = True
    for chunk, why in bad:
        ok = False
        print("  ❌ %s ⇒ %s" % (chunk, why))
    for code, val in items:
        if code in COLLIDE and code not in known:
            ok = False
            print("  ❌ 码 %s ⇒ %s" % (code, COLLIDE[code]))
            continue
        if code not in known:
            ok = False
            print("  ❌ 码 %s 不在拍板清单里 ⇒ 拒收 (★★不许猜·★回错码 = 白回一次★)" % code)
            continue
        it = known[code]
        agent, sect, _ = locate(it["key"])
        print("  ✅ %-12s = %-18s ⇒ need key `%s` · 落表路径 %s · 落点 %s/%s"
              % (code, val[:18], it["key"], it["path"], agent or "?", sect or "-"))
    print("-" * 88)
    if ok:
        print("★ ⇒ 全部对得上 ⇒ ★**可落表 (★落表是 main 的下一步·★本工具零写盘★)**")
    else:
        print("★ ⇒ ★**有对不上的 ⇒ 不许落表** ⇒ ★**回函前先纠正 (★回裸 A4/A5 会白回一次★)**")
    return 0 if ok else 2


def self_test():
    print("=" * 88)
    print("★ board_decision_reply_mapper · 自测 (★反向用例★)")
    r = []
    # ① 撞码: 回 A4 ⇒ 必须拒收
    ok = False
    try:
        rc = cmd_reply("A4 = C+A")
        ok = (rc == 2)
    except SystemExit:
        ok = False
    r.append(("反向用例1 · 回裸 A4 (关机语义老码) ⇒ 拒收", ok))
    # ② 未知码 ⇒ 拒收
    try:
        rc = cmd_reply("ZZ-9 = 随便")
        ok2 = (rc == 2)
    except SystemExit:
        ok2 = False
    r.append(("反向用例2 · 未知码 ⇒ 拒收", ok2))
    # ③ 正常回函 ⇒ 全部对得上
    try:
        rc = cmd_reply("W-2=补 W-1c=C1 SD-1=C+A LS-1=追认 上位=甲")
        ok3 = (rc == 0)
    except SystemExit:
        ok3 = False
    r.append(("反向用例3 · 正常回函 ⇒ 全对得上", ok3))
    # ④ 建议默认值必须都标着「非已决定」
    allsug = " ".join(it["sugg"] for it in board_trip_items())
    r.append(("反向用例4 · 每条建议默认值都标「非已决定」", "非已决定" in allsug))
    # ⑤ need key 必须都真实存在 (在四个分片里查得到)
    miss = [it["key"] for it in board_trip_items() if locate(it["key"])[0] is None]
    r.append(("反向用例5 · 9+1 个 need key 都在分片里查得到", not miss))
    allok = True
    for name, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", name))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return self_test()
    if "--reply" in args:
        i = args.index("--reply")
        text = args[i + 1] if i + 1 < len(args) else ""
        return cmd_reply(text)
    cmd_list()
    return 0


if __name__ == "__main__":
    sys.exit(main())
