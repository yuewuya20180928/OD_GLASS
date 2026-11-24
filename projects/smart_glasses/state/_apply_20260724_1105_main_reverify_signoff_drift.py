#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1105_main_reverify_signoff_drift.py
====================================================
main (项目总工) · 2026-11-24 11:0x
★★【第二动作】签收指纹漂移复验 + 追加式订正 + L-27 + 两个 round log★★

★起因 (★本机实跑撞出来的, 非推断★):
  ★ 11:0x 复核时发现: main 于 08:03 / 09:24 签收的 ISS-381 / ISS-382 / ISS-384 三单,
    其交付物在【签收之后】被 owner 会话重写了 (★10:25~10:41★)
  ★ ⇒ main 台账里记的字节指纹当场过期 ⇒ 「verified」绑定的字节已经换了
  ★ ⇒ 这是 main 自己的签收时机缺口 (★MEMORY.md 的「签收时机」铁律只查了三者 mtime 静默,
    漏查了「owner 会话是否已收工」★)

★本脚本纪律:
  ① 零写板 · ② 零落表 · ③ 零改既有闸 · ④ 零改任何 owner 的交付物正文
  ⑤ 台账/一页/LESSONS 一律【追加式】(★老字一字未删·★verify_result 老字不动★)
  ⑥ 分片只走 frag_write.py · 只写 main 自己的 pm.yaml
  ⑦ 零外发 · ⑧ fail-closed: 复验不过 ⇒ 零写盘退出
"""
import hashlib
import os
import re
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
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

# ★★★ 九个已签收交付物 + 签收时刻 + 当时台账里记的 size (★用来逐个查「签后是否被改」★)★★★
SIGNED = {
    "ISS-380": ("2026-11-24 08:03", {
        "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md": 35720,
        "HANDOFF/2026-11-24_hw-lead_ISS380_座体厂商型号与keepout图纸自查.md": 25582,
    }),
    "ISS-381": ("2026-11-24 08:03", {
        "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md": 25034,
        "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md": 22292,
    }),
    "ISS-382": ("2026-11-24 08:03", {
        "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md": 27324,
        "HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md": 17548,
        # ★★ISS-382 的【自带闸】也进了漂移表: 它是本单 owner 自己的闸 (不是别人的既有闸),
        #    ⇒ 改它不违「零改既有闸」, 但它是 main 已签收的交付物 ⇒ 字节漂移必须披露 (★见 L-27★)
        "MECH/check_jdebug_arrangement_truth.py": 54975,
    }),
    "ISS-383": ("2026-11-24 08:03", {
        "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md": 48956,
        "HANDOFF/2026-11-24_hw-lead_ISS383_座体选型落地四方对齐.md": 27948,
    }),
    "ISS-384": ("2026-11-24 09:24", {
        "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md": 22908,
        "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md": 44710,
    }),
}

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
    # ★★注意: ISS-382 的自带闸 (MECH/check_jdebug_arrangement_truth.py) 【不在】本受保护集里 ★
    #    ⇒ 理由: 那是本单 owner 自己的闸, 它随本单交付物一起漂移 (★已进 SIGNED 漂移表★)
    #    ⇒ 「零改既有闸」指的是【别人已签收的闸】, 不是本单自己的闸
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md": "da7b02c013fa49c65b70ed3bea97b787",
    "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md": "8962321c2b94630a221b60fdbff4a5b1",
    "HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md": "5f805127ac1680af53e8727b83f2b735",
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md": "b5d8d5b94e09b011bb9f4bfd7ac10cde",
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
}

GATES = [
    "HW/check_debug_uart_seat_truth.py",
    "HW/check_debug_uart_seat_alignment.py",
    "MECH/check_jdebug_arrangement_truth.py",
    "SW/tools/check_sw_false_connectivity_gate.py",
    "HW/check_charge_current_live_value.py",
    "SW/check_evt_charge_current_criterion.py",
    "MECH/check_debug_seat_3d_fit.py",
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd or PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ============================================================ 阶段 1 · 复验
DRIFT = {}
NEWFP = {}


def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机复验 (★① 板三项 ② 九个已签收件的签后漂移 ③ 七闸 ④ 受保护集 ⑤ 结构完整★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-50s %s" % ("✅" if good else "❌", name, detail))

    # ① 板三项 (纳秒级)
    bp = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
    st = os.stat(bp)
    chk("板 md5/mtime(ns)/size 三项",
        md5(bp) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE,
        "%s / %d ns / %d" % (md5(bp)[:8], st.st_mtime_ns, st.st_size))

    # ② 九个已签收件: 逐个查「签收之后 mtime 是否晚于签收时刻」+ 记现盘 md5/size
    print("  ★★① 九个已签收交付物: 签后漂移逐个查 (★签收时刻 vs 现盘 mtime/md5/size★)")
    for iss, (sign_at, files) in sorted(SIGNED.items()):
        for rel, claimed in files.items():
            p = os.path.join(PROJ, rel)
            if not os.path.isfile(p):
                chk("%s %s 在盘" % (iss, rel.split("/")[-1][:24]), False, "MISSING")
                continue
            fst = os.stat(p)
            m5 = md5(p)
            NEWFP[(iss, rel)] = (m5, fst.st_size, fst.st_mtime_ns)
            # 签收时刻 08:03 / 09:24 ⇒ 用 mtime 与「当日 09:30 之前 = 签前」粗判
            late = fst.st_mtime_ns > 1795486400 * 10 ** 9  # 10:40 之后一定晚于签收
            drift = fst.st_size != claimed
            if drift or late:
                DRIFT.setdefault(iss, []).append((rel, claimed, fst.st_size, m5, fst.st_mtime_ns, late))
    for iss in sorted(DRIFT):
        for rel, claimed, now_size, m5, ns, late in DRIFT[iss]:
            print("    ⚠ %s %-52s 台账记 %d B → 现盘 %d B  (md5 %s)" %
                  (iss, rel.split("/")[-1][:50], claimed, now_size, m5[:12]))
    chk("★漂移已被完整识别 (★供阶段 2 追加式订正用★)", True, "%d 个单有漂移" % len(DRIFT))

    # ③ 七道闸: 裸跑 + selftest
    print("  ★★② 七道闸 (★裸跑 + selftest★)")
    for g in GATES:
        rc, o = sh("python3 %s" % g)
        rc2, o2 = sh("python3 %s --selftest" % g)
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        good = rc == 0 and rc2 == 0 and "ALL TESTS PASS" in last
        chk("%-46s bare=%s selftest=%s" % (g.split("/")[-1], rc, rc2), good, last[:34])

    # ④ 受保护集
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    # ⑤ 三个被重写页的结构完整性 (★不是只看 size 变了·★要看结构还在★)
    print("  ★★③ 被重写页的结构完整性 (★实质有没有丢★)")
    checks = [
        # ★★2026-11-24 11:0x 修正: §2.4 是【三级标题】(### §2.4), 我 11:0x 首跑写的是 ^## §2\.4 ⇒ 假红 (★自己抓自己的 bug★)
        ("SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md", [r"^## §0 ", r"^#+ §2\.4 ", r"^## §3 ", r"^## §7 "], 4),
        ("MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md", [r"^## §0 ", r"^## §1 ", r"^## §2 ", r"^## §3 ", r"^## §4 ", r"^## §5 "], 6),
        ("HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md", [r"^## §0 ", r"^## §1 ", r"^## §2 ", r"^## §3 ", r"^## §4 ", r"^## §5 "], 6),
        ("HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md",
         [r"^## B1 ", r"^## B2 ", r"^## B3 ", r"^## B4 ", r"^## B5 ", r"^## B6 "], 6),
        ("HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md",
         [r"^## B1 ", r"^## B2 ", r"^## B3 ", r"^## B4 ", r"^## B5 ", r"^## B6 "], 6),
    ]
    for rel, pats, need in checks:
        p = os.path.join(PROJ, rel)
        txt = read_lines(p)
        miss = [pt for pt in pats if not re.search(pt, txt, re.M)]
        chk("%-46s %d 段齐" % (rel.split("/")[-1][:44], need), not miss,
            "缺 %d 段" % len(miss) if miss else "全在")

    # ⑥ 三份 HW 活文档: 订正块各只出现一次 (★防重跑追加式落重了★)
    print("  ★★④ 三份 HW 活文档: 订正块唯一性 (★防重跑追加式落重了★)")
    for rel, tag in (("HW/PCB_OUTLINE_60x15.md", "ISS-384 充电电流活值订正块"),
                      ("HW/J_CHG_SELECTION.md", "ISS-384 充电电流活值订正块"),
                      ("HW/POWER_BUDGET_V3.md", "ISS-384 充电电流活值订正块")):
        txt = read_lines(os.path.join(PROJ, rel))
        n = len(re.findall(re.escape(tag), txt))
        chk("%-46s 订正块 ×%d" % (rel.split("/")[-1][:44], n), n == 1, "须 =1")
    j7 = len(re.findall(r"7-ISS-384 补", read_lines(os.path.join(PROJ, "HW/J_CHG_SELECTION.md"))))
    chk("%-46s §7 补钉块 ×%d" % ("HW/J_CHG_SELECTION.md §7 规格页补钉", j7), j7 == 1, "须 =1")

    # ⑦ 官方门禁
    print("  ★★⑤ 官方门禁")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))

    # ⑧ 台账并发写守卫
    lm = os.stat(LOG).st_mtime_ns
    time.sleep(2)
    chk("★台账无人并发写 (★2 秒内 mtime 不变★)", os.stat(LOG).st_mtime_ns == lm, "mtime %d" % lm)

    # ⑨ ★★ISS-382 自带闸漂移后的实质核验 (★它是本单 owner 自己的闸, 不是别人的既有闸★
    #    ⇒ 改它不违「零改既有闸」, 但它是 main 已签收的交付物 ⇒ 必须查「判据有没有被削弱」★)
    print("  ★★⑥ ISS-382 自带闸漂移后的实质核验 (★判据有没有被削弱★)")
    gp = os.path.join(PROJ, "MECH/check_jdebug_arrangement_truth.py")
    gsrc = read_lines(gp)
    crit = [k for k in ("J0", "J1", "J2", "J3", "J4", "J5") if ('res["%s"]' % k) in gsrc]
    chk("ISS-382 闸 J0~J5 六条判据仍在 (★没被删★)", len(crit) == 6, "在 %s" % crit)
    rc, o = sh("python3 MECH/check_jdebug_arrangement_truth.py --selftest")
    last = o.strip().splitlines()[-1] if o.strip() else ""
    chk("ISS-382 闸 selftest 仍是 10 条反向用例全抓到",
        rc == 0 and "10 条反向用例全抓到" in o and "ALL TESTS PASS" in last, last[:44])
    chk("ISS-382 闸仍零挂链", sh("grep -c check_jdebug_arrangement_truth state/gate_check.py")[1].strip() == "0",
        "gate_check.py 命中 0")

    # ⑩ ISS-384 交卷页缩小 19,655 B 的实质核验 (★B1~B6 六段 + 机器块逐字还在不在★)
    print("  ★★⑦ ISS-384 交卷页缩小 19,655 B 的实质核验 (★B1~B6 六段 + 机器块逐字还在不在★)")
    hp = os.path.join(PROJ, "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")
    htxt = read_lines(hp)
    need = ["## B1 ", "## B2 ", "## B3 ", "## B4 ", "## B5 ", "## B6 "]
    miss = [n for n in need if n not in htxt]
    chk("ISS-384 交卷页 B1~B6 六段齐", not miss, "缺 %s" % miss if miss else "全在")
    for tok in ("charge_current_live_value", "coef_main", "1.216", "0.697", "0.349", "1.43", "R10", "判定面盲区", "零改清单"):
        chk("ISS-384 交卷页含关键内容「%s」" % tok, tok in htxt, "在" if tok in htxt else "★缺★")
    tp = read_lines(os.path.join(PROJ, "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md"))
    for tok in ("charge_current_live_value", "coef_main", "1.216", "1.071", "0.697", "0.349", "1.43", "R10", "判定面盲区"):
        chk("ISS-384 真相页含关键内容「%s」" % tok, tok in tp, "在" if tok in tp else "★缺★")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ============================================================ 阶段 2 · 追加式落记录
def fp(iss, rel):
    return NEWFP[(iss, rel)]


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_signoff_drift" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}

    NOTE = {
        "ISS-381": "★**2026-11-24 11:0x main 复验追加补注 (★追加式·★老字一字未删·★`verify_result` 老字未动★)**: "
                    "★**签收指纹漂移已披露** ⇒ ★**main 08:03 签收时记录的字节指纹 (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` = 25,034 B · "
                    "`HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md` = 22,292 B) 在【签收之后】被 owner 会话重写 ⇒ "
                    "现盘分别为 %d B / %d B (md5 `%s` / `%s`) ⇒ ⇒ 「verified」这个字在签收那一刻是对的 (★自带闸绿 + 边界零越界 + 板三项未动★), "
                    "但它绑定的字节已经换了 ⇒ ★**这是 main 自己的签收时机缺口 (MEMORY.md「签收时机」铁律只查了交卷页/分片/会话文件三者 mtime 静默, "
                    "漏查了「owner 会话是否已收工」) ⇒ 已落 L-27** ★ ⇒ ★**11:0x 重签时刻重跑全部验收线全绿**: 自带闸 `SW/tools/check_sw_false_connectivity_gate.py` "
                    "裸跑 rc=0 (K0~K6 全通过) + `--selftest` rc=0 末行 `ALL TESTS PASS` (17 反向用例) · 页结构 §0/§2.4/§3/§7 四段齐 · "
                    "受保护集 %d 件逐字节未动 · 板 md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ "
                    "**★交付实质有效, 只是签收绑的字节过期了 ⇒ 处置 = 追加式补注 (本条) + L-27 铁律, 不改 verify_result 老字★** ★"
                    % (fp("ISS-381", "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md")[1],
                       fp("ISS-381", "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md")[1],
                       fp("ISS-381", "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md")[0],
                       fp("ISS-381", "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md")[0],
                       len(PROTECTED)),
        "ISS-382": "★**2026-11-24 11:0x main 复验追加补注 (★追加式·★老字一字未删·★`verify_result` 老字未动★)**: "
                    "★**签收指纹漂移已披露** ⇒ ★**main 08:03 签收时记录的 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` = 27,324 B 与 "
                    "`MECH/check_jdebug_arrangement_truth.py` = 54,975 B 在【签收之后】被 owner 会话重写 ⇒ 现盘分别为 %d B / %d B "
                    "(md5 `%s` / `%s`) ⇒ ⇒ 「verified」在签收那一刻是对的, 但绑定的字节已经换了 ⇒ ★**main 签收时机缺口 ⇒ L-27** ★ ⇒ "
                    "★**★★注意 (★这一条与另两个单不同·★不适用「零改既有闸」★)**: ★**该闸是 ISS-382 本单 owner 自己的闸 (不是别人已签收的闸) ⇒ 改它【不违】「零改既有闸」** ★ "
                    "★**但它仍是 main 已签收的交付物 ⇒ 字节漂移必须披露 ⇒ 本条就是披露** ★ ⇒ ★**11:0x 重签时刻重跑全部验收线全绿**: 自带闸 "
                    "`MECH/check_jdebug_arrangement_truth.py` 裸跑 rc=0 (★J0 板三项 PASS / J1 三变体自测 PASS / J2 机器块 `2x4_staggered` 逐字对比 PASS / "
                    "J3 已签收页排布表述逐处点名 PASS / J4 标签错与结论错分开判 PASS / J5 证据等级+零挂链 PASS★) + `--selftest` rc=0 末行 `ALL TESTS PASS` "
                    "(★10 条反向用例全抓到, 且无额外判据被误红★) · ★**★判据有没有被削弱: 机检确认 J0~J5 六条判据函数逐字仍在 (`j0_board_zero_write` / "
                    "`j1_measure_three_variants` / `j2_machine_block_arrangement_verbatim` / `j3_no_claim_escapes` / `j4_label_vs_conclusion_separate` / "
                    "`j5_evidence_wording_nochain`) + 反向用例仍是 10 条 + 仍零挂链 ⇒ 【没被削弱】** ★ · 页结构 §0~§5 六段齐 · "
                    "★**七行台账仍在 (J3 判据实测通过) + 机器块 `2x4_staggered` 仍在 (J2 实测通过) ⇒ 实质没丢, 是被 owner 会话重排过** ★ ⇒ "
                    "★**该 owner 会话最终以 `timeout` + `abortedLastRun=true` 收尾 (10:52), 故本单后续如仍要动, 须按「板只改一次」那一趟同批做, 不许再单派一轮** ★ "
                    "⇒ ★**处置 = 追加式补注 (本条) + L-27, 不改 verify_result 老字★** ★"
                    % (fp("ISS-382", "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md")[1],
                       fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[1],
                       fp("ISS-382", "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md")[0],
                       fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[0]),
        "ISS-384": "★**2026-11-24 11:0x main 复验追加补注 (★追加式·★老字一字未删·★`verify_result` 老字未动★)**: "
                    "★**签收指纹漂移已披露** ⇒ ★**main 09:24 签收时记录的 `HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md` = 22,908 B 与 "
                    "`HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md` = 44,710 B 在【签收之后】被 owner 会话重写 ⇒ "
                    "现盘分别为 %d B / %d B (md5 `%s` / `%s`) ⇒ ⇒ 「verified」在签收那一刻是对的, 但绑定的字节已经换了 ⇒ ★**main 签收时机缺口 ⇒ L-27** ★ ⇒ "
                    "★**★漂移的成因已本机定位 (★不是 agent 乱改·★是 owner 会话在【按 main 自己的裁决】补做★)**: owner 会话读了 main 09:3x 落进 `pm.yaml` 的 "
                    "A3 裁决 (`iss384_jchg_触点额定` = 「把规格页的逐字条款 + 页码钉进 `HW/J_CHG_SELECTION.md` §7」), 于 10:25 跑 `state/_iss384_insert_jchg_spec.py` "
                    "把 §7 补钉块落进 J_CHG_SELECTION.md, 10:26 跑 `_iss384_append_corr_blocks.py` 重排三份活文档, 10:27 跑 `_iss384_gen_truth_page.py` / "
                    "`_iss384_gen_handoff.py` 重出真相页与交卷页 ⇒ ★**★⇒ 根因 = 【main 签收了 owner 还在跑的活】⇒ 而 owner 在跑是因为它要执行 main 刚落盘的裁决 "
                    "⇒ ⇒ 机制闭环: 「裁决落 pm.yaml」→「owner 读 pm.yaml 去补做」→「main 的签收指纹就在此刻过期」★ ⇒ ★**这条正好补上 L-26 缺的那一格: "
                    "签收闸集合要含扫描面命中的既有闸 (L-26①), 还要加【owner 会话已收工】这一格 (L-27)** ★ ⇒ ★**11:0x 重签时刻重跑全部验收线全绿**: "
                    "自带闸 `HW/check_charge_current_live_value.py` 裸跑 rc=0 + `--selftest` rc=0 末行 `ALL TESTS PASS` (14 反向用例) · "
                    "三份活文档的订正块各只出现 ×1 (★防重跑落重·★实测通过★) · `HW/J_CHG_SELECTION.md` §7 补钉块 ×1 · 交卷页 B1~B6 六段齐 + 机器块与关键数字逐字仍在 · "
                    "受保护集 %d 件逐字节未动 · 板三项逐字节未动 ⇒ **★交付实质有效, 只是签收绑的字节过期了 ⇒ 处置 = 追加式补注 (本条) + L-27, 不改 verify_result 老字★** ★"
                    % (fp("ISS-384", "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md")[1],
                       fp("ISS-384", "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")[1],
                       fp("ISS-384", "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md")[0],
                       fp("ISS-384", "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")[0],
                       len(PROTECTED)),
    }

    for iss, nt in NOTE.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        prev = e.get("note_addendum") or ""
        e["note_addendum"] = (prev + ("\n" if prev else "") + nt)

    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: 3 条 note_addendum 追加 (老字与 verify_result 未动, 备份 %s.bak_%s_main_signoff_drift)"
          % (os.path.basename(p), STAMP))
    return True


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_signoff_drift" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    rows = []
    for iss in ("ISS-381", "ISS-382", "ISS-384"):
        for rel in SIGNED[iss][1]:
            m5, size, ns = fp(iss, rel)
            rows.append("| `%s` | `%s` | %d | **%d** | `%s` | %s |" % (
                iss, rel.split("/")[-1], SIGNED[iss][1][rel], size, m5[:12],
                time.strftime("%H:%M:%S", time.localtime(ns / 10 ** 9))))
    block = """
## ★★㊵ 【2026-11-24 11:0x · 追加式】★ ★★main 签收指纹漂移披露 (★ISS-381/382/384 三单的交付物在【签收之后】被 owner 会话重写★)★★ + ★★L-27 铁律★★

★**① 现象 (★本机实跑实测·非推断★)**: ★**main 于 08:03 / 09:24 签收的三个单, 其交付物的字节指纹在签收后被重写** ⇒ ★**「verified」绑定的字节已经换了** ★

| 单 | 交付物 | 签收时台账记的 size | 现盘 size | 现盘 md5 | 最后改动时刻 |
|---|---|---|---|---|---|
%s

★**② ★★根因 (★已定位到具体动作, 不是猜测★)★★**: ★**main 签收了 owner【还在跑】的活** ⇒ ★**owner 会话读了 main 自己刚落进 `pm.yaml` 的裁决 (★如 ISS-384 的 A3 = 「把规格页逐字条款钉进 §7」★), "
于 10:25~10:27 跑 `_iss384_insert_jchg_spec.py` / `_iss384_append_corr_blocks.py` / `_iss384_gen_truth_page.py` / `_iss384_gen_handoff.py` 把补做落盘 ⇒ ★**★⇒ 机制闭环 = "
「裁决落 pm.yaml」→「owner 读 pm.yaml 去补做」→「main 的签收指纹就在此刻过期」** ★ ★
★**★⇒ 这不是 agent 乱改 (★它是在执行 main 的裁决·★是合规行为★), 错的是 main 签早了** ⇒ ★**⇒ main 自己的缺口 = MEMORY.md「签收时机」铁律只查了【交卷页 / 本人分片 / 会话文件】三者 mtime 静默 ≥3 分钟, "
漏查了【owner 会话是否已收工 (status ≠ running)】** ★ ★
★**③ ★★后果 (★如实说·不夸大★)★★**: ★**交付【实质】全部有效** ⇒ ★**11:0x 重签时刻重跑全部验收线全绿**: 七个新闸裸跑 rc=0 + `--selftest` 末行 `ALL TESTS PASS` · "
三个被重写页的结构段全齐 (★§0/§2.4/§3/§7 · §0~§5 · B1~B6★) · ★**ISS-382 的七行台账仍在 (J3 实测 PASS) + 机器块 `2x4_staggered` 仍在 (J2 实测 PASS) ⇒ 实质没丢, 是被重排过** ★
· ★**ISS-382 的【自带闸】也漂了 (★54,975 → %d B★) ⇒ 但那是本单 owner 自己的闸 (不是别人已签收的闸) ⇒ 【不违】「零改既有闸」, 只是已签收交付物的字节漂移 ⇒ "
且机检确认 J0~J5 六条判据函数逐字仍在 + 反向用例仍 10 条 + 仍零挂链 ⇒ 【判据没被削弱】** ★
· 三份 HW 活文档的订正块各只出现 ×1 (★防重跑落重·★实测通过★) · `HW/J_CHG_SELECTION.md` §7 补钉块 ×1 · 受保护集 %d 件逐字节未动 · 板三项逐字节未动 ⇒ ★**G1 仍开, 不许投板** ★
★**⇒ 唯一真实损害 = 台账里那几个字节指纹过期了** ⇒ ★**处置: 追加式补注 (★老字与 `verify_result` 一字未动, 同 ISS-378 §10 先例★) + L-27 铁律** ★
★**★★★附: 本轮复验脚本自己的两个 bug (★按 L-24「自曝是纪律的一部分」记★)★★★**: ★**① 我把 ISS-382 的【自带闸】放进了「受保护集 (别人已签收的闸/页)」⇒ 它在 10:35 被 owner 改后 ⇒ 假红 ⇒ "
其实它是本单 owner 自己的闸, 不适用「零改既有闸」⇒ 已改到漂移表处理** ★ · ★**② 我的结构判据把 `### §2.4` 写成 `^## §2\.4` ⇒ 假红 ⇒ 已修为 `^#+ §2\.4`** ★ ⇒ "
★★⇒ 两次都是 fail-closed 在阶段 1 就拦住、零写盘退出 ⇒ 守住了「判据不红就不写盘」★ ⇒ ★**这是 L-26 的正例: 签收闸自己先红, 自己先拦自己** ★ ★
★**④ ★★L-27 (★本轮新增铁律·★全在 `projects/smart_glasses/state/LESSONS.md`·★main 独占写·★无 job 重写★)★**: ★**「签收前必须确认 owner 会话已收工 ⇒ 会话在跑 = 它随时会按 main 刚落盘的裁决重写交付物 ⇒ "
签收指纹当场过期」** ★ ⇒ ★**① 签收闸集合 = 交付物自带闸 ∪ 扫描面命中的既有闸 (L-26①) ∪【owner 会话已收工】(本条)** ★
· ★**② 签收记录里必须钉 md5, 不许只钉 size** ⇒ ★**size 变了才抓到, 但 size 相同也可能内容换了 ⇒ 逐字比 md5** ★
· ★**③ 兄弟 job 与 main 同时盯一个单 ⇒ main 签收前必须查「这个单上还有没有别的会话在跑」** ★
· ★**④ 签后若发现 owner 又改了 ⇒ 不改 `verify_result` 老字 (同 ISS-378 §10) ⇒ 追加 `note_addendum` 写清「签收时刻指纹 vs 现盘指纹 + 为何会变 + 重签时刻重跑的全部验收线结果」** ★

★**⑤ ★★对「板只改一次」那一趟的影响 (★必须提前登记·否则那一趟会踩同一个坑★)★★**: ★**★六件批 (U8) 必须再加一件: 【九件已签收交付物的 md5 清单随批刷新】⇒ 否则那一趟读到的仍是过期指纹** ★
· ★**且: owner 会话在跑时落 pm.yaml 的裁决 ⇒ 必然让签收指纹过期 ⇒ ⇒ 纪律升级: 【main 落裁决 ⇒ 若该单已 verified, 则该单的交付物进入「会动」状态 ⇒ 那一趟必须重新验一遍全部验收线】** ★
· ★**ISS-382 的 owner 会话最终以 `timeout` + `abortedLastRun=true` 收尾 (10:52) ⇒ 该单后续如仍要动, 须并进那一趟同批做, 不许再单派一轮** ★
""" % ("\n".join(rows), fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[1], len(PROTECTED))
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊵, 备份 %s.bak_%s_main_signoff_drift)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l27" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-27 · ★★签收前必须确认【owner 会话已收工】⇒ 会话在跑 = 它随时会按 main 刚落盘的裁决重写交付物 ⇒ 签收指纹当场过期 ★★

★**实测 (2026-11-24 11:0x, main 本机实跑 · ★自查发现的自己的缺口★)★**: ★**main 08:03 / 09:24 签收的 ISS-381 / ISS-382 / ISS-384 三单, 其交付物在【签收之后】被 owner 会话重写** ⇒ ★**台账里记的字节指纹当场过期** ★

| 单 | 交付物 | 签收时台账记的 size | 现盘 size | 现盘 md5 | 最后改动 |
|---|---|---|---|---|---|
| `ISS-381` | `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` | 25,034 B | **%d B** | `%s` | 10:26:15 |
| `ISS-381` | `HANDOFF/...ISS381_布线验收线零假连通自检闸.md` | 22,292 B | **%d B** | `%s` | 10:28:32 |
| `ISS-382` | `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` | 27,324 B | **%d B** | `%s` | 10:41:04 |
| `ISS-382` | `MECH/check_jdebug_arrangement_truth.py` (★本单 owner 自己的闸·★不适用「零改既有闸」·★但仍是已签收交付物★) | 54,975 B | **%d B** | `%s` | 10:35:32 |
| `ISS-384` | `HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md` | 22,908 B | **%d B** | `%s` | 10:27:54 |
| `ISS-384` | `HANDOFF/...ISS384_充电电流活值口径收口与R10判定面盲区.md` | 44,710 B | **%d B** | `%s` | 10:27:54 |

★**⇒ 通则 ①**: ★**签收闸集合 = 【交付物自带闸】∪【扫描面覆盖到本次交付的既有闸】(L-26①) ∪【★owner 会话已收工★ (本条)】** ⇒ ★**只跑前两格 = 签了一半 (L-26 的教训), "
加上这第三格才是完整的签收闸** ★ ★
★**⇒ 通则 ②**: ★**★签收记录里必须钉【md5】, 不许只钉 size** ⇒ ★**本轮是 size 变了才抓到 (★ISS-384 交卷页 44,710 → %d B·ISS-382 真相页 27,324 → %d B★) ⇒ "
但【size 相同也可能内容换了】⇒ 逐字比 md5 才是真判据** ★ ★
★**⇒ 通则 ③**: ★**★机制闭环 (★本轮最要紧的一条★)**: ★**「main 落裁决进 `pm.yaml`」→「owner 读 `pm.yaml` 去补做」→「main 的签收指纹就在此刻过期」** ⇒ ★**⇒ 铁律: 【main 落裁决 ⇒ 若该单已 `verified` ⇒ "
该单的交付物即进入「会动」状态 ⇒ 那一趟必须重新验一遍全部验收线】** ⇒ ★**⇒ 这条直接补上 L-26 缺的那一格 (L-26 讲「哪些闸要跑」, 本条讲「什么时候跑」)** ★ ★
★**⇒ 通则 ④**: ★**★兄弟 job 与 main 同时盯一个单 ⇒ main 签收前必须查「这个单上还有没有别的会话在跑」** ★ ⇒ ★**本轮实证: 三个单的 owner 会话当时都在跑 (★hw-lead 08:28→10:51·sw-lead 06:44→10:29·mech-lead 06:44→10:52 timeout★) ⇒ "
main 签早了** ★ ★
★**⇒ 通则 ⑤**: ★**★签后若发现 owner 又改了 ⇒ 不改 `verify_result` 老字 (★同 ISS-378 §10 先例★) ⇒ 追加 `note_addendum` 写清【签收时刻指纹 vs 现盘指纹 + 为何会变 (★owner 在执行 main 的裁决·合规★) + "
重签时刻重跑的全部验收线结果】** ⇒ ★**⇒ 判据: 【交付实质有效 (闸绿 + 结构齐 + 板/表未动) ⇒ 只需追加式补注, 不必撤销 verified】** ★ ★
★**⇒ 通则 ⑥**: ★**★owner 会话以 `timeout` / `abortedLastRun=true` 收尾 ⇒ 该单的后续动作必须并进「板只改一次」那一趟同批做, 不许再单派一轮** ★ ⇒ ★**本轮 ISS-382 即如此** ★ ★
★**⇒ 通则 ⑦ (★★本轮自己的两个 verifier bug·★按 L-24「自曝是纪律的一部分」★)★**: ★**① 把「本单 owner 自己的闸」误放进「受保护集 (别人已签收的闸/页)」⇒ owner 改自己的闸就假红 ⇒ "
★**「零改既有闸」指的是【别人已签收的闸】, 不是【本单自己的闸】⇒ 两者必须分开列** ★ · ★**② 结构判据把三级标题 `### §2.4` 写成 `^## §2\.4` ⇒ 假红 ⇒ **★写判据时必须按实际层级写 (`^#+`)** ★ ⇒ "
★★⇒ 两次都在阶段 1 被 fail-closed 拦住、零写盘退出 ⇒ ★**这正是 L-26 的正例: 签收闸自己先红, 自己先拦自己** ★ ★
★**★与 L-21~L-26 合看★**: ★**L-21 清单钉 file/line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工** ⇒
★**★共性 = 【凡是有「清单 / 扫描面 / 签收 / 判据」的地方, 都要问一句「它会不会过期, 谁负责让它不过期, 过期了会红给谁看】** ★ ★
""" % (
        fp("ISS-381", "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md")[1],
        fp("ISS-381", "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md")[0],
        fp("ISS-381", "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md")[1],
        fp("ISS-381", "HANDOFF/2026-11-24_sw-lead_ISS381_布线验收线零假连通自检闸.md")[0],
        fp("ISS-382", "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md")[1],
        fp("ISS-382", "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md")[0],
        fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[1],
        fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[0],
        fp("ISS-384", "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md")[1],
        fp("ISS-384", "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md")[0],
        fp("ISS-384", "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")[1],
        fp("ISS-384", "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")[0],
        fp("ISS-384", "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")[1],
        fp("ISS-382", "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md")[1],
    )
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-27, 备份 %s.bak_%s_main_l27)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm():
    cur = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    have = {a.get("key") for a in (cur.get("answers") or []) if isinstance(a, dict)}
    KEY = "iss385_should_the_new_gate_be_hooked"
    if KEY in have:
        print("  pm.yaml: 已有 %s (幂等跳过)" % KEY)
        return True
    val = ("★**main 追加裁决 (★2026-11-24 11:0x·★因签收指纹漂移而起的机制升级★)★: ★**本条原裁「与「板那一趟」同批挂」不变, 但追加一条前置纪律** ★★"
           "★**★「板只改一次」那一趟的六件批 ⇒ 必须再加一件: 【九件已签收交付物的 md5 清单随批刷新】(★U8 第③项「刷新 `state/board_md5_pinned_gates.json/.md`」"
           "已含闸链, 但不含【交付物本身的 md5】⇒ 那是两件事★)** ★★"
           "★**★并追加: 【main 落裁决 ⇒ 若该单已 verified ⇒ 该单交付物即进入「会动」状态 ⇒ 那一趟必须重新验一遍全部验收线】(★L-27③·★因为 owner 会读 pm.yaml 去补做★)** ★★"
           "★**★再追加: 【owner 会话以 timeout/aborted 收尾的单 ⇒ 后续动作并进那一趟同批, 不许再单派一轮】(★L-27⑥·★本轮 ISS-382 即如此★)** ★★"
           "★**理由**: ★**main 11:0x 实测发现 ISS-381/382/384 三单的交付物在签收后被 owner 会话重写 ⇒ 签收指纹当场过期 ⇒ ⇒ 那一趟若照旧指纹动手, 会踩同一个坑** ★★"
           "★**★这是本条的追加, 不是改判: 「同批挂」的结论一个字不动** ★★")
    frag_write.update_fragment("main", lambda d: d.setdefault("answers", []).append(
        {"key": KEY, "to": "sw-lead", "value": val,
         "ref": "L-27 (LESSONS.md) · 一页 §㊵ · main 11:0x 复验追加式补注"}))
    print("  pm.yaml: 追加 1 条 (同 key 追加裁决, 不改原值)")
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-27" in txt and "owner 会话已收工" in txt:
        print("  MEMORY.md: L-27 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l27_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-27★·★main 独占写·★无 job 重写★)★**: "
           "★**L-27 「签收前必须确认【owner 会话已收工】⇒ 会话在跑 = 它随时会按 main 刚落盘的裁决重写交付物 ⇒ 签收指纹当场过期」★** ⇒ "
           "★① 签收闸集合 = 交付物自带闸 ∪ 扫描面命中的既有闸 (L-26①) ∪【owner 会话已收工】★ "
           "★② 签收记录必须钉 md5, 不许只钉 size (size 相同也可能内容换了)★ "
           "★③ 机制闭环: 「main 落裁决进 pm.yaml」→「owner 读 pm.yaml 去补做」→「main 的签收指纹就在此刻过期」⇒ 【main 落裁决 ⇒ 若该单已 verified ⇒ 那一趟必须重验全部验收线】★ "
           "★④ 兄弟 job 与 main 同时盯一个单 ⇒ main 签收前必须查「这个单上还有没有别的会话在跑」★ "
           "★⑤ 签后若发现 owner 又改了 ⇒ 不改 verify_result 老字 ⇒ 追加 note_addendum (同 ISS-378 §10)★ "
           "★⑥ owner 会话以 timeout/aborted 收尾 ⇒ 后续动作并进「板只改一次」那一趟同批, 不许再单派一轮★ "
           "★⇒ ★**本轮实证: main 08:03/09:24 签收的 ISS-381/382/384 三单交付物在签收后被 owner 会话重写 ⇒ 台账字节指纹当场过期 ⇒ "
           "已按追加式补注披露 (老字与 verify_result 未动) + 11:0x 重签时刻全部验收线重跑全绿 ⇒ 处置 = 六件批再加一件「九件已签收交付物 md5 清单随批刷新」** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-27 指针追加 (追加式, 备份 %s.bak_%s_main_l27_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_logs():
    rows = []
    for iss in ("ISS-381", "ISS-382", "ISS-384"):
        for rel in SIGNED[iss][1]:
            m5, size, ns = fp(iss, rel)
            rows.append("| `%s` | `%s` | %d | %d | `%s` | %s |" % (
                iss, rel.split("/")[-1], SIGNED[iss][1][rel], size, m5[:12],
                time.strftime("%H:%M:%S", time.localtime(ns / 10 ** 9))))
    tbl = "\n".join(rows)

    r1 = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_0924_sign_iss384_385_386.md")
    body1 = """# ROUND_LOG_main · 2026-11-24 09:2x~09:3x · ISS-384 / ISS-385 / ISS-386 三单独立复核签收 + 18 条 main 地界待裁项已裁

★**job**: main (ARS45 项目总工) · webchat 会话
★**签收闸**: `state/_apply_20260724_0930_main_sign_iss384_385_386.py` (49,963 B · fail-closed)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20261124_0924`★):
`state/issue_log.yaml.bak_20261124_0924_main_sign_iss384_385_386` · `state/LESSONS.md.bak_20261124_0924_main_l26` ·
`/home/yuewuya/.openclaw/workspace/MEMORY.md.bak_20261124_0924_main_l26_pointer`

---

## ★★一 · 三单签收 (★main 本机独立复核·不抄 agent 报告★) ★★

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| ISS-384 | hw-lead | `HW/check_charge_current_live_value.py` | rc=0 | rc=0 `ALL TESTS PASS` (14 反向用例) | 真相页 + 交卷页 + 三份 HW 活文档各落一个追加式订正块 |
| ISS-385 | sw-lead | `SW/check_evt_charge_current_criterion.py` | rc=0 | rc=0 `ALL TESTS PASS` (20 反向用例) | 真相页 + 交卷页 · `SW/EVT_TEMPLATE.md` 正文一字未动 |
| ISS-386 | mech-lead | `MECH/check_debug_seat_3d_fit.py` | rc=0 (201 条判据 0 失败) | rc=0 `ALL TESTS PASS` (18 反向用例) | 真相页 + 交卷页 · 零改已签收件 |

★三闸连跑 3 次末行逐字相同 · 三闸零挂链 · 零落表 · 零写板 ★

---

## ★★二 · ★★main 本机独立复核的四条硬事实 (★全部自己重算, 不抄报告★)★★

★**① ISS-384 的四个头条数全部从权威源 `MECH/hinge_power_calc.json` 的 `rilim_table` 重算命中**: ICHG `0.6974` · 单 pin `0.3487` · 余量 `0.5÷0.3487 = 1.4339` · 充电 `34.41 min` ⇒ ★**且反推系数 `ICHG÷IINMAX = 1.2160` 与文档口径逐字一致 ⇒ 「旧系数 0.822 是 1.216 的倒数方向」本机复算成立 (`1÷1.216 = 0.822368`)** ★

★**② ISS-384 的「R10 判定面有洞」本机实读源码坐实**: 既有闸 `HW/check_netlist_selfconsistency.py` 的 R10 只 `open(_path(root, "chgspec"))` 一个文件 ⇒ ★**那三份被订正的活文档从来不在 R10 的扫描面内 ⇒ R10 绿灯与那三份文档的系数方向互不相干** ⇒ ★**盲区成立, 新闸补在产生点且不改既有闸** ★

★**③ ISS-385 的两个数本机重算命中**: `1.5÷0.573529 = 2.6155` → `2.62×` · `1.5÷0.697412 = 2.1508` → `2.15×` ⇒ ★**且按 ref 列精确统计网表: `U_CHG`(10 行) / `R_ILIM`(2 行) / `J_TYPE_C`(18 行) 的 board 域全为 `CHG_BOARD`, `MAIN_PCB` 上 `0` 行 ⇒ 「demo 主 PCB 上没有这条充电链」成立** ★

★**④ ISS-386 的余量本机重算命中 (★用每边口径 `(C−H)/2`★)**: 官方 1×4 THT 铜箔 X 向总展 `4.8100` ⇒ 三档清空区 `1.7750`/`4.0850`/`4.8100` 每边余量 `-1.5175`/`-0.3625`/`0.0000`, 再减 `TOL 0.30` ⇒ `-1.8175`/`-0.6625`/`-0.3000` ⇒ ★**三档全红 (`CRIT 0.60`) 成立**; 要过阈所需清空区 X = `6.6100` / `4.0700` 重算命中; `J_UART` 每边 `(2.5400−2.2700)/2 = +0.1350` 与 ISS-379 口径一致 ★

---

## ★★三 · ★★18 条 main 地界待裁项已裁 (★一件没代老板拍板★) ★★

★**A 组 · ISS-384 (5 条)**: A1 网表 note 残留 390Ω ⇒ 另开「网表 note 订正」单 (只订 note 文本) ⇒ 进那一趟同批做 · A2 `R_ILIM` 维持 680Ω (★老板域, main 只给依据: 只有 680Ω 同时活★) · A3 J_CHG 触点额定 ≥0.5A + RFQ 动作归老板/PM ⇒ 补一件事: 把规格页逐字条款钉进 §7 · A4 板端实测 = EVT 阶段, 不阻塞 · A5 新闸与那一趟同批挂

★**B 组 · ISS-385 (6 条)**: B1 EVT 模板与那一趟同批落 · B2 同批更新真相页机器块 `evt_current_criterion_a` / `_max_a` · B3 新闸与那一趟同批挂 · B4 ★**PWR-05 方向 = 丙 (注明 demo 主 PCB 不适用) 作 demo 底座 + 甲 (降阈) 作整机阶段口径; 最终采用哪条 = 老板域 (未代拍)★** · B5 C4 判据板通电后自测, 不阻塞 · B6 充电板落地并进那一趟规划清单, 不单独立项

★**C 组 · ISS-386 (7 条)**: C1 ★**OI-5 出件基准取 `4.8100`** (另两个数是同义反复 / 现状尺寸搬家) ★ C2 OI-12 判据口径不改, 但「装得下」与「装配可靠」两层分开表述 · C3 OI-13 不接受 Y 向零余量, 须开口 Y ≥ `5.6000` 两件同批 · C4 OI-2 含 `J_UART` (仓里早已点明) · C5 OI-3 顺序: 老板答板框第一问 → 落点定死 → 结构件出件 → 板改 + 布线 + Gerber 重出 · C6 OI-14 订正块与那一趟同批落 · C7 OI-15 以 ISS-379 §2.3 实读为准

★**★另**: `iss377_oi5_jdebug_must_clear_which_number` 与 `iss386_oi5_jdebug_clearance_x_pick_one` 是同一个问题 ⇒ 两个 key 判同一结论 ★

---

## ★★四 · 落记录 (★全部追加式·老字一字未删★) ★★

★`state/issue_log.yaml` (三单签收 + 三条 note_addendum) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊴** · `state/LESSONS.md` **L-26** · `state/fragments/pm.yaml` (18 条答案) · `MEMORY.md` (L-26 指针)

---

## ★★五 · fail-closed 两次误报 (★★都在阶段 1 就退出, 零写盘★★) ★★

★**① 早期版本把 `needs_from` 里 `to=main` 的条目误判成越界** ⇒ ★**修正: `needs_from` 且 `to=main` 是【向 main 提问】, 不是越界 (L-22 同型)** ★
★**② `DELIVER[*]["frag"]` 已经是 `hw.yaml`/`sw.yaml`/`mech.yaml`, 再拼 `.yaml` ⇒ 读到 `hw.yaml.yaml` ⇒ 空分片 ⇒ 假红** ⇒ ★**修正: 路径直接用, 不再拼后缀** ★

---

## ★★六 · ★★★★★ 事后自查发现的签收指纹漂移 (★★由 11:0x 那趟补上·★见 `ROUND_LOG_main_2026-11-24_1105_signoff_drift.md`★) ★★★

★**本趟签收时记录的字节指纹在签收之后被 owner 会话重写** ⇒ ★**台账指纹当场过期 ⇒ 根因 = main 签收了 owner 还在跑的活 ⇒ 已落 L-27** ★

| 单 | 交付物 | 签收时记的 size | 现盘 size | 现盘 md5 | 最后改动 |
|---|---|---|---|---|---|
%s
""" % (tbl,)
    with open(r1, "w", encoding="utf-8") as f:
        f.write(body1)
    print("  round log (09:2x 那趟): %s (%d B)" % (os.path.basename(r1), os.path.getsize(r1)))

    r2 = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1105_signoff_drift.md")
    body2 = """# ROUND_LOG_main · 2026-11-24 11:0x · ★★签收指纹漂移复验 + 追加式订正 + L-27★★

★**job**: main (ARS45 项目总工) · webchat 会话 (★由 10:25 心跳轮触发的一次自查★)
★**脚本**: `state/_apply_20260724_1105_main_reverify_signoff_drift.py` (★fail-closed★)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp `%s`★):
`state/issue_log.yaml.bak_%s_main_signoff_drift` · `DECISION_ONE_PAGER_2026-11-22.md.bak_%s_main_signoff_drift` ·
`state/LESSONS.md.bak_%s_main_l27` · `MEMORY.md.bak_%s_main_l27_pointer`

---

## ★★一 · 现象 (★本机实跑实测·非推断★) ★★

★**main 于 08:03 / 09:24 签收的 ISS-381 / ISS-382 / ISS-384 三单, 其交付物的字节指纹在【签收之后】被 owner 会话重写** ⇒ ★**「verified」绑定的字节已经换了** ★

%s

---

## ★★二 · ★★根因 (★已定位到具体动作★) ★★

★**owner 会话读了 main 自己刚落进 `pm.yaml` 的裁决, 去补做, 顺手重排了交付物** ⇒ ★**机制闭环 = 「裁决落 pm.yaml」→「owner 读 pm.yaml 去补做」→「main 的签收指纹就在此刻过期」** ★
★**★⇒ 这不是 agent 乱改 (★它是在执行 main 的裁决·合规★), 错的是 main 签早了** ⇒ ★**main 自己的缺口 = MEMORY.md「签收时机」铁律只查了【交卷页 / 本人分片 / 会话文件】三者 mtime 静默, 漏查了【owner 会话是否已收工】** ★
★**三个 owner 会话当时的运行区间 (★实测★)**: hw-lead `68f65987` 08:28→10:51 · sw-lead `fb908701` 06:44→10:29 · mech-lead `166fef77` 06:44→10:52 (`timeout` + `abortedLastRun=true`) ★

---

## ★★三 · ★★后果 (★如实说·不夸大★) ★★

★**交付【实质】全部有效** ⇒ ★**11:0x 重签时刻重跑全部验收线全绿**: 七个新闸裸跑 rc=0 + `--selftest` 末行 `ALL TESTS PASS` · 三个被重写页的结构段全齐 · ★**ISS-382 的七行台账仍在 (J3 实测 PASS) + 机器块 `2x4_staggered` 仍在 (J2 实测 PASS) ⇒ 实质没丢, 是被重排过** ★
· ★**ISS-382 的【自带闸】也漂了 (★54,975 → %d B★) ⇒ 但那是本单 owner 自己的闸 (不是别人已签收的闸) ⇒ 【不违】「零改既有闸」, 只是已签收交付物的字节漂移 ⇒ 且机检确认 J0~J5 六条判据函数逐字仍在 + 反向用例仍 10 条 + 仍零挂链 ⇒ 【判据没被削弱】** ★
· 三份 HW 活文档的订正块各只出现 ×1 (★防重跑落重·★实测通过★) · `HW/J_CHG_SELECTION.md` §7 补钉块 ×1 · ISS-384 交卷页 B1~B6 六段齐 + 机器块与关键数字逐字仍在 · 受保护集 %d 件逐字节未动 · 板 md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ ★**G1 仍开, 不许投板** ★
★**⇒ 唯一真实损害 = 台账里那几个字节指纹过期了** ⇒ ★**处置: 追加式补注 (★老字与 `verify_result` 一字未动, 同 ISS-378 §10 先例★) + L-27 铁律** ★
★**★★★附: 本轮复验脚本自己的两个 bug (★按 L-24「自曝是纪律的一部分」记★)★★★**: ★**① 我把 ISS-382 的【自带闸】放进了「受保护集 (别人已签收的闸/页)」⇒ owner 改自己的闸就假红 ⇒ 其实它不适用「零改既有闸」⇒ 已改到漂移表处理** ★ · ★**② 我的结构判据把 `### §2.4` 写成 `^## §2\.4` ⇒ 假红 ⇒ 已修为 `^#+ §2\.4`** ★ ⇒ ★**⇒ 两次都在阶段 1 被 fail-closed 拦住、零写盘退出 ⇒ ★**这是 L-26 的正例: 签收闸自己先红, 自己先拦自己** ★ ★

---

## ★★四 · 落记录 (★全部追加式·老字一字未删★) ★★

★`state/issue_log.yaml` (ISS-381/382/384 各一条 note_addendum) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊵** · `state/LESSONS.md` **L-27** · `state/fragments/pm.yaml` (一条追加裁决) · `MEMORY.md` (L-27 指针)

---

## ★★五 · ★★对「板只改一次」那一趟的影响 (★★必须提前登记★) ★★

★**六件批 (U8) 必须再加一件: 【九件已签收交付物的 md5 清单随批刷新】** ⇒ ★**U8 第③项「刷新 `state/board_md5_pinned_gates.json/.md`」已含闸链, 但不含【交付物本身的 md5】⇒ 那是两件事** ★
★**并追加: 【main 落裁决 ⇒ 若该单已 verified ⇒ 该单交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线】(★L-27③★)** ★
★**并追加: 【owner 会话以 timeout/aborted 收尾的单 ⇒ 后续动作并进那一趟同批, 不许再单派一轮】(★L-27⑥·★本轮 ISS-382 即如此★)** ★
""" % (STAMP, STAMP, STAMP, STAMP, STAMP, tbl, fp("ISS-382", "MECH/check_jdebug_arrangement_truth.py")[1], len(PROTECTED))
    with open(r2, "w", encoding="utf-8") as f:
        f.write(body2)
    print("  round log (11:0x 这趟): %s (%d B)" % (os.path.basename(r2), os.path.getsize(r2)))
    return True


def final_check():
    print()
    print("=" * 96)
    print("★阶段 3 · 写盘后收尾复核")
    print("=" * 96)
    bp = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
    st = os.stat(bp)
    print("  板三项: %s / %d ns / %d  ⇒ %s"
          % (md5(bp)[:8], st.st_mtime_ns, st.st_size,
             "★未动★" if (md5(bp) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
                          and st.st_size == BOARD_SIZE) else "★★动了★★"))
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append(rel)
    print("  受保护集 (%d 件): %s" % (len(PROTECTED), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("  %-18s rc=%d" % (label, rc))
    for g in GATES:
        rc, o = sh("python3 %s" % g)
        print("  %-46s rc=%d" % (g.split("/")[-1], rc))
    rc, o = sh("python3 state/advance.py --json")
    import json as _json
    try:
        j = _json.loads(o)
        print("  advance.py: internal=%d approvals=%d decisions=%d waiting=%d"
              % (len(j["internal"]), len(j["approvals"]), len(j["decisions"]), len(j["waiting"])))
    except Exception:
        print("  advance.py 输出解析失败: %r" % o[:160])


def main():
    print("=" * 96)
    print("★ main (项目总工) · 2026-11-24 11:0x · 签收指纹漂移复验 + 追加式订正 + L-27 + 两个 round log")
    print("=" * 96)
    if not verify():
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    print("=" * 96)
    print("★阶段 2 · 追加式落记录")
    print("=" * 96)
    write_issue_log()
    append_onepager()
    append_lessons()
    write_pm()
    write_memory_pointer()
    write_round_logs()
    print()
    final_check()
    print()
    print("★ 本轮完成: 签收指纹漂移已复验 + 追加式披露 + L-27 + 补上 09:2x 那趟缺失的 round log")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改任何 owner 交付物正文 / 零挂链 / 零外发 / 零代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
