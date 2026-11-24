#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1420_main_fix_section_number_collision.py
============================================================
main (项目总工) · 2026-11-24 14:2x
★★【订正】13:1x 那一轮自己犯的三个错: 章节号撞号 (㊶) + round log 备份 stamp 写错 + pm.yaml 条数写错★★

★背景 (★★本脚本是被【本机复核】逼出来的, 不是预防性改★):
  ① ★★章节号撞号★★: 一页 `DECISION_ONE_PAGER_2026-11-22.md` 现在有两个 `## ★★㊶`:
     - 行 1318 = 兄弟 job fb67af40 于 10:2x 写的 (★在先★)
     - 行 1420 = 我 13:1x 写的 (★在后★)
     ⇒ 13:1x 那一轮落盘前【没有扫已用章节号】⇒ 撞号 ⇒ 页面上出现两个 ㊶
     ⇒ ★★处置: 我那一个改号为 §㊷ (★㊷ 全页未用·★实读确认 0 命中★)
        ⇒ ★★兄弟 job 那一个【一个字不动】(★不是我的, 且在先★)
        ⇒ ★★改号用【逐字替换标题行 + 就地加一行订正说明】, 不删老字
  ② ★★round log 备份 stamp 写错★★: round log 里写「真实 stamp 20261124_1310」,
     实盘是 `20261124_1300` (★脚本用 time.strftime 现场取·★我写 round log 时手打了 1310★)
     ⇒ ★★处置: 追加式订正节, 不改老字
  ③ ★★round log 与 pm.yaml 条数写错★★: round log 写「13 条答案」, 实盘是 15 条
     ⇒ ★★处置: 追加式订正节

★纪律:
  ★ 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 (★只在【我自己刚写的】标题行与【我自己刚写的】round log 上动★)
  ★ 只改 main 自己的 pm.yaml (走 frag_write) · 零外发 · 未代老板拍板
  ★ fail-closed: 阶段 1 任一红 ⇒ 零写盘退出
  ★★追加式: 老字一字未删, 订正一律另起块★
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import yaml

import frag_write

STAMP = time.strftime("%Y%m%d_%H%M")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
ROUNDLOG = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1310_sign_iss387_389.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

# ★★我这 15 条 (★key → 其 ref 里出现的「§㊶」形态★) ⇒ 全部改成 §㊷★★
MY_KEYS = [
    "iss387_main_rilim_ring_width_fab_capability",
    "iss387_main_oi1_pad_1x1_maintained",
    "iss387_main_oi2_drill_change_same_batch",
    "iss387_main_oi3_footprint_source_generic_plus_deviation",
    "iss387_main_oi4_seat_outline_two_track",
    "iss389_main_oi2_scope_includes_juart",
    "iss389_main_oi3_landing_order",
    "iss389_main_oi5_pick_4810",
    "iss389_main_oi12_criterion_stays_route_a",
    "iss389_main_oi13_open_y_enlarge",
    "iss389_main_oi14_dp1_correction_4070",
    "iss391_main_gap_registration_same_batch",
    "iss391_main_gate_hook_with_registration",
    "main_owner_must_freeze_deliverables_after_handoff",
    "iss389_main_oi1_formal_confirm_4070",
]

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md": "da7b02c013fa49c65b70ed3bea97b787",
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
    "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md": "8962321c2b94630a221b60fdbff4a5b1",
    "HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md": "5f805127ac1680af53e8727b83f2b735",
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md": "b5d8d5b94e09b011bb9f4bfd7ac10cde",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md": "e9eea373c42f7225881007af08defba5",
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ===================================================================== 阶段 1
def verify():
    print("=" * 96)
    print("★阶段 1 · 订正前的现状核对 (★先证实问题确实存在, 再动手★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-52s %s" % ("✅" if good else "❌", name, detail))

    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    txt = read_lines(ONEPAGER)
    lines = txt.splitlines()
    heads = [(i + 1, l) for i, l in enumerate(lines) if l.startswith("## ★★")]
    c56 = [(n, l) for n, l in heads if l.startswith("## ★★㊶")]
    c57 = [(n, l) for n, l in heads if l.startswith("## ★★㊷")]
    chk("★页面上 §㊶ 出现两次 (★撞号·★这就是要订正的问题★)", len(c56) == 2,
        "行 %s" % [n for n, _ in c56])
    chk("★§㊷ 全页未用 (★新号可用★)", len(c57) == 0, "命中 %d" % len(c57))
    if len(c56) == 2:
        # ★必须确认第一个是兄弟 job 的 (在先·不动), 第二个是我的 (13:1x·改号)★
        chk("★第一个 §㊶ 是兄弟 job 的 (★10:2x·★在先·一个字不动★)",
            "10:2x" in c56[0][1], c56[0][1].strip()[:70])
        chk("★第二个 §㊶ 是我 13:1x 写的 (★这个才改号★)",
            "13:1x" in c56[1][1] and "ISS-387 / ISS-389" in c56[1][1], c56[1][1].strip()[:70])
        chk("★第一个 §㊶ 段内没有引用到我 13:1x 的内容 (★它不知道我存在·★所以它不用改★)",
            "ISS-387 / ISS-389 两单独立复核签收" not in "\n".join(lines[c56[0][0] - 1:c56[1][0] - 1]),
            "无交叉引用")
    # ★我那段的正文里, 唯一该改的是标题行; 正文里的「§㊶」自指也要一起改 (★本轮实读: 正文自指 = 0 处★)
    if len(c56) == 2:
        seg = "\n".join(lines[c56[1][0] - 1:])
        n_self = seg.count("§㊶")
        chk("★我 13:1x 段内正文 §㊶ 自指 = 0 处 (★★只有标题行要改号★·★这是实读结论★)",
            n_self == 0, "%d 处" % n_self)
        # ★★正文里引的是「§㊵」⇒ 必须核实它指的是 09:4x 那一段 (★含 OI-11 的 4.70/7.30 算★), 不是 11:0x 那一段 (★那是漂移披露★)★★
        n52 = seg.count("§㊵")
        chk("★我段内 §㊵ 引用 = %d 处 (★指 09:4x 那一段·★不改★)" % n52, n52 >= 1, "%d 处" % n52)
        # ★★页面上有两个 §㊵ (09:4x 与 11:0x) ⇒ 取【第一个】(09:4x) 的整段来验 ★★
        h52 = [i for i, l in enumerate(lines) if l.startswith("## ★★㊵")]
        s5200 = ""
        if len(h52) >= 2:
            s5200 = "\n".join(lines[h52[0]:h52[1]])
        else:
            s5200 = "\n".join(lines[h52[0]:]) if h52 else ""
        hit_470 = "4.70" in s5200
        hit_x = ("X 向" in s5200)
        chk("★★我引的「§㊵」确指 09:4x 那一段 (★该段含 OI-11 的 4.70 与 X 向无关的论证★)",
            hit_470 and hit_x, "★4.70=%s · X向=%s · 段范围=%s★" % (hit_470, hit_x, (h52[0] + 1, h52[1] + 1) if len(h52) >= 2 else "?"))

    # pm.yaml 那 15 条
    pm = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    ans = pm.get("answers") or []
    byk = {a.get("key"): a for a in ans}
    miss = [k for k in MY_KEYS if k not in byk]
    chk("★我那 15 条 key 全在 pm.yaml", not miss, "缺 %s" % miss[:3])
    nref = sum(1 for k in MY_KEYS if k in byk and "§㊶" in (byk[k].get("ref") or ""))
    chk("★这 15 条的 ref 里有 §㊶ 的条数", nref == 15, "%d 条" % nref)
    dup = len(ans) - len({a.get("key") for a in ans})
    chk("★pm.yaml 无重名 key", dup == 0, "dup=%d 总=%d" % (dup, len(ans)))
    chk("★pm.yaml 总条数 = 152 (★13:1x 落盘后实测值★)", len(ans) == 152, "%d" % len(ans))

    # round log 的两个错数
    rl = read_lines(ROUNDLOG)
    chk("★round log 里备份 stamp 写的是 1310 (★实盘是 1300·★错★)", "20261124_1310" in rl, "★确实写错★")
    chk("★round log 里写「13 条答案」 (★实盘 15·★错★)", "13 条答案" in rl, "★确实写错★")
    real_baks = sorted(os.path.basename(x) for x in __import__("glob").glob(
        os.path.join(PROJ, "state/issue_log.yaml.bak_2026*main_sign_iss387_389")))
    chk("★实盘备份 stamp = 20261124_1300", any("20261124_1300" in b for b in real_baks), str(real_baks))

    # 受保护集
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append(rel)
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad, "动 %d %s" % (len(bad), bad[:3]))

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★问题已证实·可进阶段 2·只改我自己写的东西★" if ok
                                   else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ===================================================================== 阶段 2
def fix_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_secnum_fix" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    lines = old.splitlines(True)

    # ★定位: 兄弟 job 的 §㊶ (第一个) 与我的 §㊶ (第二个, 含 13:1x)★★
    idx = [i for i, l in enumerate(lines) if l.startswith("## ★★㊶")]
    assert len(idx) == 2, "§㊶ 数量不是 2, 现场变了 ⇒ 退出"
    mine = [i for i in idx if "13:1x" in lines[i] and "ISS-387 / ISS-389" in lines[i]]
    assert len(mine) == 1, "定位不到我那一个 ⇒ 退出"
    mi = mine[0]

    # ★★只改: ① 标题行的号 ㊶ → ㊷  ② 我这段正文里的 §㊶ 自指 → §㊷  ③ 就地插一行订正说明★★
    lines[mi] = lines[mi].replace("## ★★㊶ 【2026-11-24 13:1x", "## ★★㊷ 【2026-11-24 13:1x", 1)
    # ★正文自指: 只在我这一段之内 (从 mi 到文末) 逐行替换 (★本轮实读: 正文自指 0 处·★但仍写成通用逻辑, 防以后正文里出现自引★)★
    n_body = 0
    for i in range(mi, len(lines)):
        if "§㊶" in lines[i]:
            lines[i] = lines[i].replace("§㊶", "§㊷")
            n_body += 1
    print("    ★标题行改号 + 正文自引替换 %d 处" % n_body)

    # ★就地订正说明 (★插在标题行正下方·★老字一字未删★)★★
    note = ("★**★章节号订正 (★2026-11-24 14:2x main 本机复核发现·★追加式·★老字一字未删★)★**: "
            "★**本段原写作 `§㊶`, 与兄弟 job fb67af40 于 10:2x 写在同一页的 `§㊶` 撞号 "
            "(★那一处在先·★在先的那一段【一个字未动】★) ⇒ ⇒ 本段【就地改号为 `§㊷`】(★`㊷` 全页未用·★实读确认 0 命中★) ⇒ "
            "★**⇒ 同时 `state/fragments/pm.yaml` 里本轮 15 条答案的 `ref` 字段中的「§㊶」已同步改为「§㊷」** ⇒ "
            "★**⇒ 一并说明: 这是 13:1x 那一轮【落盘前没扫已用章节号】造成的自伤 ⇒ ⇒ 已登记为 LESSONS **L-30** "
            "(★追加式·★main 独占写·★无 job 重写★)** ★★"
            "★**★⇒ 兄弟 job 那一段 `§㊶` (10:2x, 行 1318) 内容是「队列真空 → 槽位被占」的根因订正, "
            "与本段 (13:1x, ISS-387/389 签收 + 11 条待裁项) 【互不引用·互不覆盖】⇒ 两段都有效** ★★\n\n")
    lines.insert(mi + 1, note)

    with open(p, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    now = read_lines(p)
    assert now.startswith(old[:200]), "★一页开头被破坏★"
    print("  一页: %d → %d B (我的 §㊶ → §㊷, 就地插订正说明一行, 兄弟 job 的 §㊶ 未动)"
          % (before, os.path.getsize(p)))
    return True


def fix_pm():
    cur = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    byk = {a.get("key"): a for a in (cur.get("answers") or [])}
    changed = []

    def mut(d):
        for a in d.get("answers") or []:
            k = a.get("key")
            if k in MY_KEYS:
                r = a.get("ref") or ""
                if "§㊶" in r:
                    a["ref"] = r.replace("§㊶", "§㊷")
                    changed.append(k)
    frag_write.update_fragment("main", mut)
    now = yaml.safe_load(open(PM, encoding="utf-8"))
    ans = now["answers"]
    dup = len(ans) - len({a.get("key") for a in ans})
    bad = [a.get("key") for a in ans if a.get("key") in MY_KEYS and "§㊶" in (a.get("ref") or "")]
    assert dup == 0, "★改完出现重名 key ⇒ 退出★"
    assert not bad, "★还有没改干净的 §㊶: %s⇒ 退出★" % bad[:3]
    assert len(ans) == 152, "★总条数变了 (%d) ⇒ 退出★" % len(ans)
    print("  pm.yaml: 15 条 ref 的 §㊶ → §㊷ (改了 %d 条) · 总 %d 条 · dup=%d · 其余条目逐字未动"
          % (len(changed), len(ans), dup))
    return True


def fix_roundlog():
    p = ROUNDLOG
    shutil.copy2(p, p + ".bak_%s_main_roundlog_fix" % STAMP)
    before = os.path.getsize(p)
    block = """

---

## ★★九 · ★★订正节 (★2026-11-24 14:2x main 本机复核 · 追加式 · ★上面第八节之前的文字一个字未删★) ★★

★**★① 章节号撞号 (★我 13:1x 那一轮的自伤★)★**
★**实况**: 一页 `DECISION_ONE_PAGER_2026-11-22.md` 上出现**两个** `## ★★㊶` ⇒ ★**行 1318 = 兄弟 job fb67af40 于 10:2x 写的 (在先) · 行 1420 = 我 13:1x 写的 (在后)** ★
★**根因**: ★**13:1x 那一轮落盘前【没有扫已用章节号】⇒ 直接取「下一个号」⇒ 撞上了兄弟 job 半小时前刚写的那个号** ⇒ ★**⇒ 与 L-28 (幂等 key 撞名必须报错退出) 同族: 【取号/取 key 这类操作, 必须先查重】** ★
★**★处置 (★追加式·★兄弟 job 那段一个字未动★)★**: ★**① 我那一段改号为 `§㊷` (★`㊷` 全页未用·★实读确认 0 命中★) ⇒ ② 标题行下方就地插一行订正说明 (老字一字未删) ⇒ "
③ 段内全部「§㊶」自指同步改为「§㊷」 (★★本轮实读: 段内正文自指 = 0 处·★实际只改了标题行 + pm.yaml 的 15 条 ref★) ⇒ ④ `state/fragments/pm.yaml` 里本轮 15 条答案的 `ref` 字段中的「§㊶」同步改为「§㊷」** ★
★**★⇒ 兄弟 job 那一段 `§㊶` (10:2x) 的内容是「队列真空 → 槽位被占」的根因订正, 与我这一段 (ISS-387/389 签收 + 11 条待裁项) 【互不引用·互不覆盖】⇒ 两段都有效** ★
★**★⇒ 已登记为 LESSONS **L-30** (★main 独占写★)** ★ ★

★**★② 备份 stamp 写错 (★第八节第 5~7 行★)★**
★**老字写的是**: `★备份★ (★脚本现场取 time.strftime ⇒ 真实 stamp 20261124_1310★)` ⇒ ★**★实盘是 `20261124_1300`** (★脚本用 `time.strftime` 现场取·★是我写 round log 时手打了 1310★) ⇒
★**★⇒ 实盘三个备份的真实文件名 (★逐个 ls 确认★)★**: `state/issue_log.yaml.bak_20261124_1300_main_sign_iss387_389` · `DECISION_ONE_PAGER_2026-11-22.md.bak_20261124_1300_main_sign_iss387_389` · `state/LESSONS.md.bak_20261124_1300_main_l29` · ★**`MEMORY.md.bak_20261124_1300_main_l29_pointer`** ★
★**⇒ 另注: 一页的备份是 11:23:51 那一份 (`…_20261124_1300_…` 之前另有 11:23 的旧备份) ⇒ ★**本轮改号用的新备份 = `…_bak_20261124_1420_main_secnum_fix`** ★ ★

★**★③ pm.yaml 条数写错 (★第七节末行★)★**
★**老字写的是**: `state/fragments/pm.yaml (13 条答案)` ⇒ ★**★实盘 = 15 条** (★137 → 152★) ⇒ ★**明细 (★15 条全列, 供对账★)★**:
★`iss387_main_rilim_ring_width_fab_capability` (待补项) · `iss387_main_oi1_pad_1x1_maintained` · `iss387_main_oi2_drill_change_same_batch` · `iss387_main_oi3_footprint_source_generic_plus_deviation` · `iss387_main_oi4_seat_outline_two_track` ·
★`iss389_main_oi2_scope_includes_juart` · `iss389_main_oi3_landing_order` · `iss389_main_oi5_pick_4810` · `iss389_main_oi12_criterion_stays_route_a` · `iss389_main_oi13_open_y_enlarge` · `iss389_main_oi14_dp1_correction_4070` · `iss389_main_oi1_formal_confirm_4070` ·
★`iss391_main_gap_registration_same_batch` · `iss391_main_gate_hook_with_registration` · `main_owner_must_freeze_deliverables_after_handoff` ★
★**⇒ 与「11 条 main 地界待裁项」的关系 (★两数不同, 不是矛盾★)★**: ★**「11 条」= ISS-387 的 4 条 (OI-1~4) + ISS-389 的 7 条 (OI-2/3/5/12/13/14 + OI-1) ⇒ 这是【题面】的 11 条** ⇒ "
★**「15 条」= 11 条题面裁决 + 3 条 main 自立项 (① 环宽/制程能力待补项 ② ISS-391 §4 三处登记的落法 ③ ISS-391 新闸的挂链时机) + 1 条跨单通用纪律 (交卷后冻结交付物) ⇒ 这是【落表条数】** ⇒ ⇒ **两个数都对, 但老字没写清关系, 已在此补明** ★ ★

★**★④ 本轮订正自身也守纪律 (★自曝★)★**: ★**零写板 (板三项未动) · 零落表 · 零改既有闸 · 零改兄弟 job 的页面正文 (★只动我自己刚写的标题行与自指★) · 零外发 · 未代老板拍板** ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  round log: %d → %d B (追加式 §九 订正节)" % (before, os.path.getsize(p)))
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l30" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-30 · ★★落盘前必须扫【已用编号/已用 key】⇒ 取号类操作与写盘类操作同源, 撞号必须当场发现并改掉 ★★

★**实测 (2026-11-24 14:2x, main 本机复核 · ★13:1x 那一轮的自伤★)★**: ★**main 在一页裁决台上追加了新段, 标题取「下一个号」`§㊶` ⇒ 而半小时前兄弟 job fb67af40 已经用过 `§㊶` ⇒ ⇒ 同一页出现两个 `## ★★㊶`** ★
★**★⇒ 后果 (★机器可核★)★**: ★**① 引用失效**: 本轮 15 条 pm.yaml 答案的 `ref` 里写着「一页 §㊶ A1」⇒ **读者按号去找会落到兄弟 job 那一段** (★那一段讲的是「队列真空 → 槽位被占」, 与 A1/C1 毫无关系★) ⇒ "
★**② ⇒ 同类问题在本页已累计 6 次**: ★**`㉓`×2 · `㉞`×2 · `㉚`×2 · `㉛`×2 · `㊵`×2 · `㊶`×2 ⇒ ⇒ 这是【系统性重复取号】, 不是偶发** ★ ★
★**★⇒ 通则 ① (★核心★)★**: ★**★凡是从「现有内容」里【取下一个编号/取下一个 key/取下一个序号】的写法, 落盘前必须【读一遍现盘已用了哪些】⇒ ⇒ 这是 L-28 (幂等 key 撞名必须报错退出) 的推广版: 【幂等守卫查的是「这条写过没有」, 而取号守卫查的是「这个号被占没有」⇒ 两者都要有】** ★
★**★⇒ 通则 ② (★撞了怎么办·★追加式★)★**: ★**★撞号不许【就地覆盖别人的段】⇒ 处置 = ① 确认【在先的那一段】不是自己写的 ⇒ ② 【只改自己那一段】的标题与自指 ⇒ ③ 【在标题下方就地插一行订正说明】(老字一字未删) ⇒ ④ 【所有引用自己那一段的 ref 字段】同步改号 ⇒ ⑤ 追加式写进 round log + LESSONS** ★★"
★**⇒ ★★★★这里第 ⑤ 步最容易被省掉 ⇒ ⇒ 而它恰恰是【让后来者知道「这个号为什么有两个」的唯一途径】⇒ ⇒ 【订正必须留痕, 不能只是把号改对】** ★ ★
★**★⇒ 通则 ③ (★并发场景★)★**: ★**★多个 job 会往同一份共享文件追加段 (本项目: main 与兄弟 cron 都写一页裁决台) ⇒ ⇒ 【取号】这一步天然是并发的 ⇒ ⇒ 读-判断-写 之间存在窗口 ⇒ ⇒ "
★**★⇒ ⇒ 应对 = 【写完立刻回读确认自己的号唯一】(★本轮就是这么抓到的: 回读时数到两个 ㊶★)⇒ ⇒ 【回读确认】这一步不能省, 因为【落盘时的判断】在并发下本来就不可靠** ★ ★
★**★⇒ 通则 ④ (★「同号两段」未必是坏事·★但必须能被分辨★)★**: ★**★若两段内容【互不引用·互不覆盖】(★本轮 ㊶ 的两段就是这样★) ⇒ 两段都有效 ⇒ 不许为了「好看起来整齐」去删兄弟 job 那段 ⇒ "
★**★⇒ ⇒ 但必须让读者能分辨 ⇒ ⇒ 处置 = 【在标题里带时刻 + 就地插订正说明】⇒ ⇒ 【编号是给人引用的, 时刻才是给人定位的】** ★ ★
★**★⇒ 与 L-21~L-29 合看★**: ★**L-21 清单钉 file/line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工 · L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了 · "
L-30 取号前必须扫已用号 ⇒ ★**★共性 (第 7 条了) = 【凡是有「清单 / 扫描面 / 签收 / 判据 / 幂等 / 挂链 / 编号」的地方, 都要问一句「它会不会过期 / 会不会撞名 / 谁负责让它不过期, 出问题时会红给谁看」】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-30, 备份 %s.bak_%s_main_l30)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "★LESSONS 老字被破坏★"
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-30" in txt and "取号前必须扫已用号" in txt:
        print("  MEMORY.md: L-30 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l30_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-30★·★main 独占写·★无 job 重写★)★**: "
           "★**L-30 「落盘前必须扫【已用编号/已用 key】⇒ 取号类操作与写盘类操作同源, 撞号必须当场发现并改掉」★** ⇒ "
           "★① 凡是从现盘内容里【取下一个编号/取下一个 key/取下一个序号】的写法, 落盘前必须【读一遍现盘已用了哪些】⇒ 这是 L-28 幂等 key 撞名守卫的推广版 (一个查「这条写过没」, 一个查「这个号被占没」·两个都要有)★ "
           "★② 撞号不许就地覆盖别人的段 ⇒ 处置 = 确认在先的那段不是自己写的 → 只改自己那段 (标题 + 自指) → 标题下方就地插一行订正说明 (老字一字未删) → 所有引用自己那段 ref 字段同步改号 → 追加式写进 round log + LESSONS (★第⑤步最容易被省, 而它是让后来者知道「这个号为什么有两个」的唯一途径·不许只把号改对就完★)★ "
           "★③ 多个 job 往同一份共享文件追加段 ⇒ 取号天然并发 ⇒ 读-判断-写之间有窗口 ⇒ ⇒ 【写完立刻回读确认自己的号唯一】这一步不能省★ "
           "★④ 同号两段若互不引用互不覆盖 ⇒ 两段都有效 ⇒ 不许为「整齐」去删兄弟 job 那段 ⇒ 但必须让读者能分辨 ⇒ 【编号是给人引用的, 时刻才是给人定位的】★ "
           "★⇒ ★**本轮实证: main 13:1x 那一轮在一页裁决台取「下一个号」§㊶ ⇒ 而半小时前兄弟 job fb67af40 已用过 §㊶ ⇒ 同页两个 §㊶ ⇒ ⇒ 14:2x 本机复核回读时抓到 ⇒ ⇒ 同类重复取号在本页已累计 6 次 (㉓㉞㉚㉛㊵㊶ 各 ×2) ⇒ ⇒ 是系统性重复取号, 不是偶发★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-30 指针追加 (追加式, 备份 %s.bak_%s_main_l30_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def final_check():
    print()
    print("=" * 96)
    print("★阶段 3 · 写盘后收尾复核")
    print("=" * 96)
    st = os.stat(BOARD)
    good = (md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE)
    print("  板三项: %s / %d ns / %d ⇒ %s" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size,
          "★未动★" if good else "★★动了★★"))
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        if md5(p) != want:
            bad.append(rel)
    print("  受保护集 (%d 件): %s" % (len(PROTECTED), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    txt = read_lines(ONEPAGER)
    lines = txt.splitlines()
    c56 = [l for l in lines if l.startswith("## ★★㊶")]
    c57 = [l for l in lines if l.startswith("## ★★㊷")]
    print("  一页: §㊶ 段数=%d (★兄弟 job 那个·应为 1★) · §㊷ 段数=%d (★我那个·应为 1★)"
          % (len(c56), len(c57)))
    pm = yaml.safe_load(open(PM, encoding="utf-8"))
    ans = pm["answers"]
    dup = len(ans) - len({a.get("key") for a in ans})
    stale = [a.get("key") for a in ans if a.get("key") in MY_KEYS and "§㊶" in (a.get("ref") or "")]
    print("  pm.yaml: 总=%d dup=%d · 我那 15 条里还残留 §㊶ 的: %d %s"
          % (len(ans), dup, len(stale), stale[:3]))
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("  %-18s rc=%d" % (label, rc))
    for g in ("HW/check_fts_single_row_land_truth.py", "MECH/check_debug_seat_rework_spec.py",
              "HW/check_fts_land_drill_same_batch.py"):
        rc, o = sh("python3 %s" % g)
        print("  %-46s rc=%d" % (g, rc))
    rc, o = sh("python3 state/advance.py --json")
    import json as _json
    try:
        j = _json.loads(o)
        print("  advance.py: internal=%d approvals=%d decisions=%d waiting=%d"
              % (len(j["internal"]), len(j["approvals"]), len(j["decisions"]), len(j["waiting"])))
    except Exception:
        print("  advance.py 输出解析失败")


def main():
    print("=" * 96)
    print("★ main · 2026-11-24 14:2x · 订正 13:1x 那一轮自伤: 章节号撞号 + round log 两个错数")
    print("=" * 96)
    if not verify():
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    print("=" * 96)
    print("★阶段 2 · 追加式订正 (★只动我自己刚写的东西★)")
    print("=" * 96)
    fix_onepager()
    fix_pm()
    fix_roundlog()
    append_lessons()
    write_memory_pointer()
    print()
    final_check()
    print()
    print("★ 订正完成: §㊶ → §㊷ (兄弟 job 那段未动) + round log 追加式订正节 + L-30")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
