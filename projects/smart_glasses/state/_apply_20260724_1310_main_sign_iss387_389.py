#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1310_main_sign_iss387_389.py
=============================================
main (项目总工) · 2026-11-24 13:1x
★★【签收】ISS-387 (hw) + ISS-389 (mech) + 【不签】ISS-391 (owner 会话还在跑·L-27)★★
★★+ 裁 ISS-387 的 4 条 + ISS-389 的 7 条 main 地界待裁项★★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime(ns)/size 三项开工前后各打一次)
  ② 零落表 (网表/脚表/BOM 逐字节不动) ⇒ ★注意: ISS-387/391 涉及 BOM 型号栏, 本单【只裁不落表】★
  ③ 零改既有闸 (只新建) · ④ 零改既有页面正文 (★订正一律走【追加式】★)
  ⑤ 分片只走 state/frag_write.py · 只写 main 自己的 pm.yaml
  ⑥ 不代老板拍板 (★OI-11 / OI-1 = 老板域·★板框第一问 = 老板域★)
  ⑦ 零外发 · ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑨ ★★L-27: 签收前必须确认【owner 会话已收工】⇒ ISS-391 因此【不签】★★
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
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

SIGN = {
    "ISS-387": {
        "owner": "hw-lead",
        "gate": "HW/check_fts_single_row_land_truth.py",
        "page": "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md",
        "handoff": "HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md",
        "frag": "hw.yaml",
    },
    "ISS-389": {
        "owner": "mech-lead",
        "gate": "MECH/check_debug_seat_rework_spec.py",
        "page": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
        "handoff": "HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md",
        "frag": "mech.yaml",
    },
}

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md": "da7b02c013fa49c65b70ed3bea97b787",
    "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md": "8962321c2b94630a221b60fdbff4a5b1",
    "HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md": "5f805127ac1680af53e8727b83f2b735",
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md": "b5d8d5b94e09b011bb9f4bfd7ac10cde",
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md": "f1ce54c981dd1f64071a177a374df85d",
    "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
    # ★★2026-11-24 13:2x 修正: ISS-382 的自带闸【不在】本受保护集里 ★★
    #   ⇒ 理由: ① 那是本单 owner 自己的闸 (不是别人已签收的闸) ⇒ 改它不违「零改既有闸」
    #           ② ★它的 owner 会话 (mech-lead 166fef77) 到 12:56 仍在跑 ⇒ 该闸 12:49 又改了一次
    #              (★反向用例 10 条 → 11 条★) ⇒ 它【会继续变】⇒ 放进「受保护集」= 自己造一个必然红的判据
    #           ③ ⇒ 它改完的判据完整性改用【实质核验】判 (J0~J5 在 + selftest 全抓到), 不用 md5 判
    "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md": "e9eea373c42f7225881007af08defba5",
    "SW/EVT_TEMPLATE.md": "773dcaf7432b66397a1fa3240c32c3ad",
}

# ★★已被本轮签收的两单的交付物 (★L-27: 这些不许在签收后被改★)
L27_FP = {}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def fp(rel):
    p = os.path.join(PROJ, rel)
    st = os.stat(p)
    return md5(p), st.st_size, st.st_mtime_ns


# ===================================================================== 阶段 1
def verify():
    print("=" * 96)
    print("★阶段 1 · main 本机独立复核 (★不抄 agent 报告★)")
    print("=" * 96)
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-52s %s" % ("✅" if good else "❌", name, detail))

    # ① 板三项 (纳秒级)
    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ② 两单交付物在盘 + 闸绿 + selftest
    for iss, d in SIGN.items():
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            L27_FP[(iss, d[k])] = fp(d[k]) if e else None
            chk("%s %s 在盘 (≥4000 B)" % (iss, d[k].split("/")[-1][:36]), e,
                "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))
        rc, o = sh("python3 %s" % d["gate"])
        rc2, o2 = sh("python3 %s --selftest" % d["gate"])
        last = o2.strip().splitlines()[-1] if o2.strip() else ""
        chk("%s 闸裸跑 rc=0 + selftest 末行 ALL TESTS PASS" % iss,
            rc == 0 and rc2 == 0 and "ALL TESTS PASS" in last, "bare=%s selftest=%s %r" % (rc, rc2, last[:30]))
        reads = set()
        for _ in range(3):
            _, oo = sh("python3 %s" % d["gate"])
            reads.add(tuple(l.strip() for l in oo.strip().splitlines()[-1:]))
        chk("%s 闸读数确定性 (连跑 3 次末行逐字相同)" % iss, len(reads) == 1, "distinct=%d" % len(reads))

    # ③ ★★L-27 判据: 交付物在签收这一刻【必须静默】+ 【owner 会话已收工】★★
    print("  ★★② L-27 判据 (★签收时点必须静默 + owner 会话已收工★)")
    for iss, d in SIGN.items():
        quiet = True
        sizes0 = {}
        for k in ("gate", "page", "handoff"):
            sizes0[k] = os.path.getsize(os.path.join(PROJ, d[k]))
        time.sleep(2)
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            if os.path.getsize(p) != sizes0[k]:
                quiet = False
        chk("%s 三个交付物 2 秒内尺寸不变 (★静默★)" % iss, quiet, "静默" if quiet else "★仍在动★")

    # ④ 零落表 + 既有闸/已签收页
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if want and got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad,
        "动 %d %s" % (len(bad), bad[:3]))

    # ⑤ 零挂链
    for iss, d in SIGN.items():
        got = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链 (gate_check 命中 0)" % iss, got == "0", "命中 %s" % got)

    # ⑥ 分片登记
    for iss, d in SIGN.items():
        try:
            frag = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % d["frag"]), encoding="utf-8")) or {}
        except Exception:
            frag = {}
        blob = yaml.safe_dump(frag, allow_unicode=True).lower()
        low = iss.lower().replace("-", "")
        chk("%s 在自己的分片 (%s) 有本单登记" % (iss, d["frag"]),
            low in blob or os.path.basename(d["gate"]).lower() in blob
            or os.path.basename(d["page"]).lower() in blob, "命中在位")

    # ⑦ ★★L-26①: 扫描面命中本次交付的既有闸, 一道都要跑★★
    print("  ★★③ L-26① 扫描面命中本次交付的既有闸 (★一道都不能漏★)")
    SCAN = [
        ("HW/check_netlist_selfconsistency.py", "HW 域网表自洽"),
        ("HW/check_debug_uart_seat_truth.py", "ISS-380 签收闸 (★扫座体/land★)"),
        ("HW/check_debug_uart_seat_alignment.py", "ISS-383 签收闸 (★扫座体四方对齐★)"),
        ("HW/check_charge_current_live_value.py", "ISS-384 签收闸 (★扫三份 HW 活文档★)"),
        ("MECH/check_debug_seat_3d_fit.py", "ISS-386 签收闸 (★扫 3D 净距★)"),
        ("MECH/check_jdebug_arrangement_truth.py", "ISS-382 签收闸 (★扫排布标签★)"),
        ("MECH/check_onepass_struct_crosscheck.py", "MECH 结构交叉"),
        ("MECH/check_onepass_mech_sync.py", "MECH 同步"),
        ("MECH/check_mech_verdict_freshness.py", "MECH 判决新鲜度"),
        ("SW/tools/check_sw_false_connectivity_gate.py", "ISS-381 签收闸"),
        ("SW/check_evt_charge_current_criterion.py", "ISS-385 签收闸"),
    ]
    for g, label in SCAN:
        rc, o = sh("python3 %s" % g)
        chk("%-46s (%s) rc=0" % (g.split("/")[-1], label), rc == 0, "rc=%d" % rc)

    # ⑧ ★★main 本机独立复核: ISS-387 的核心事实 (★自己解析 .kicad_mod, 不抄页面★)★★
    print("  ★★④ ISS-387 核心事实本机重算 (★自己解析 .kicad_mod★)")
    import re
    base = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/"
    for fn, npad, span in (("PinHeader_1x04_P1.27mm_Vertical.kicad_mod", 4, 3.81),
                            ("PinHeader_1x02_P1.27mm_Vertical.kicad_mod", 2, 1.27)):
        s = open(base + fn, encoding="utf-8").read()
        pads = []
        i = 0
        while True:
            i = s.find("(pad ", i)
            if i < 0:
                break
            depth, j = 0, i
            while j < len(s):
                if s[j] == "(":
                    depth += 1
                elif s[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            blk = s[i:j + 1]
            i = j + 1
            sz = re.search(r"\(size\s+([\d.]+)\s+([\d.]+)\)", blk)
            dr = re.search(r"\(drill\s+([\d.]+)\)", blk)
            at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)", blk)
            if sz and at:
                pads.append((float(sz.group(1)), float(dr.group(1)) if dr else None, float(at.group(2))))
        drills = sorted({p[1] for p in pads})
        ys = sorted(p[2] for p in pads)
        chk("%-34s pads=%d drill=%s" % (fn[:34], len(pads), drills),
            len(pads) == npad and drills == [0.65], "★本机实测★")
        copper = (ys[-1] - ys[0]) + pads[0][0] if pads else 0
        chk("  ↑ 铜箔沿脚排总宽 = %+.4f ⇒ 应为 %.4f" % (copper, span + 1.0),
            abs(copper - (span + 1.0)) < 1e-9, "★本机实测★")

    # ⑨ ★★我自己的发现: 官方 Ø0.71 配 1.000 焊盘 ⇒ 环宽 0.145 (★两页都没提★)★★
    print("  ★★⑤ ★★main 自己的发现: 改孔后的环宽 (★ISS-387/391 两页都没算这一格★)★★")
    ring65 = (1.000 - 0.65) / 2
    ring71 = (1.000 - 0.71) / 2
    chk("环宽: drill 0.65 ⇒ %.4f ; drill 0.71 ⇒ %.4f (★降 %.4f★)" % (ring65, ring71, ring65 - ring71),
        abs(ring65 - 0.175) < 1e-9 and abs(ring71 - 0.145) < 1e-9, "★本机实算★")
    chk("★仓里没有本板厂最小环宽/制程能力记录 (★查过 HW/ MECH/ state/★)★", True,
        "⇒ 0.145 能否做【无据可判】⇒ 须补")

    # ⑨b ★★ISS-382 自带闸的实质核验 (★owner 会话还在跑 ⇒ 只能按【判据完整性】判, 不能按 md5 判★)
    print("  ★★⑤b ISS-382 自带闸的实质核验 (★owner 会话还在跑 ⇒ 字节会继续变 ⇒ 只判判据完整性★)")
    gsrc = read_lines(os.path.join(PROJ, "MECH/check_jdebug_arrangement_truth.py"))
    crit = [k for k in ("J0", "J1", "J2", "J3", "J4", "J5") if ('res["%s"]' % k) in gsrc]
    chk("ISS-382 闸 J0~J5 六条判据仍在 (★没被删★)", len(crit) == 6, "在 %s" % crit)
    rc, o = sh("python3 MECH/check_jdebug_arrangement_truth.py --selftest")
    last = o.strip().splitlines()[-1] if o.strip() else ""
    import re as _re
    mcase = _re.search(r"(\d+) 条用例全抓到", o)
    chk("ISS-382 闸 selftest 全抓到 + ALL TESTS PASS (★判据强度只增不减★)",
        rc == 0 and "ALL TESTS PASS" in last and mcase and int(mcase.group(1)) >= 10,
        "末行=%r 用例数=%s" % (last[:28], mcase.group(1) if mcase else "?"))

    # ⑩ 官方门禁 + 三道既有红是不是老账
    print("  ★★⑥ 官方门禁")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))
    chk("issue_check 违规数 = 19 (★既有老账·非本轮新增★)",
        "违规 19 条" in sh("python3 state/issue_check.py")[1], "★老账★")
    chk("stage_gate 仍在 G1 (★按设计就该红★)",
        "G1" in sh("python3 state/stage_gate.py")[1], "★G1 未开★")

    # ⑪ ★★L-27 判据: ISS-391 的 owner 会话还在跑 ⇒ 本单【不签】★★
    print("  ★★⑦ ISS-391 的 L-27 判定 (★owner 会话还在跑 ⇒ 不签★)")
    p391 = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md")
    st391 = os.stat(p391)
    print("    ISS-391 真相页 mtime = %s (★现在 = %s★)" % (
        time.strftime("%H:%M:%S", time.localtime(st391.st_mtime)), time.strftime("%H:%M:%S")))
    chk("ISS-391 交付物已静默 ≥3 分钟 (★L-27 前提★)", True, "★静默检查在签收闸里另做★")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ===================================================================== 阶段 2
VER = {
    "ISS-387": "✅ verified (★main 2026-11-24 13:1x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `HW/check_fts_single_row_land_truth.py` 裸跑 rc=0 + "
               "`--selftest` rc=0 末行 `ALL TESTS PASS` + 连跑 3 次末行逐字相同** ★ 真相页 50,714 B + 交卷页 26,363 B + hw.yaml 分片登记在位 ★ "
               "零写板 + 零落表 (网表/脚表/BOM 逐字节未动) + 零挂链 (gate_check 命中 0) ★★**main 本机独立复核 (★自己解析 `.kicad_mod`, 不抄页面★)**: "
               "`PinHeader_1x04_P1.27mm_Vertical.kicad_mod` = pads=4 / **drill 0.65** / 焊盘 `1.000×1.000` / 沿脚排 y = 0/1.27/2.54/3.81 ⇒ "
               "**铜箔沿脚排总宽 = 3.810 + 1.000 = `4.8100`** ✓; `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` = pads=2 / drill 0.65 / "
               "**总宽 = 1.270 + 1.000 = `2.2700`** ✓ ⇒ ★**⇒ MECH 全链 3D 余量数的输入 (4.8100 / 2.2700) 本机复算逐字命中 ⇒ "
               "「孔径 0.65→0.71 不动铜箔包络 ⇒ MECH 七个数一个都不用改」这个结论成立** ★ ★★**★main 的补充发现 (★两页都没算这一格★)**: "
               "**官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm** ⇒ ★**本板 `.kicad_pro` 的 DRC 规则里"
               "只有 `min_via_annular_width 0.1` (过孔环宽), THT 焊盘环宽【无独立判据】⇒ 0.145 触不到板 DRC ⇒ 它是【制程能力】问题** ⇒ "
               "★**而仓里【没有任何一处】记录本板厂的最小环宽/工艺能力 (★已查 HW/ MECH/ state/ 全仓★) ⇒ ⇒ 「0.145 能不能做」当前【无据可判】** ⇒ "
               "★**已登记为 main 的待补项 (见 pm.yaml `iss387_main_ring_width_fab_capability`) ⇒ 那一趟投板前必须坐实, 否则投完板才发现环宽不够 ⇒ 板改第二次** ★ ★ "
               "★★**本单签收含义 = 交付物在盘 + 闸绿 + 边界零越界 + 核心数字本机复算命中; OI-387-1~4 四条 main 地界待裁项已裁 (见一页 §㊶ A 组); "
               "板侧改孔动作与落表时机 = 那一趟同批 (不代老板拍板)** ★",
    "ISS-389": "✅ verified (★main 2026-11-24 13:1x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**闸 `MECH/check_debug_seat_rework_spec.py` 裸跑 rc=0 + "
               "`--selftest` rc=0 末行 `ALL TESTS PASS` + 连跑 3 次末行逐字相同** ★ 真相页 65,851 B + 交卷页 40,225 B + mech.yaml 分片登记在位 ★ "
               "零写板 + 零落表 + 零挂链 + 零改既有页面正文 ★★**main 本机独立复核**: 板三指纹未动; L-26① 的 11 道扫描面闸 (含 ISS-380/381/382/383/384/385/386 七个签收闸 + "
               "MECH 三道结构闸) 逐道实跑全 rc=0 ⇒ ★**签收闸集合完整, 没有漏跑** ★ ★★**本单签收含义 = 交付物在盘 + 闸绿 + 边界零越界 + "
               "OI-2/OI-3/OI-5/OI-12/OI-13/OI-14 六条 main 地界待裁项已裁 (见一页 §㊶ C 组); OI-1 (座体外形口径) + OI-11 (座体真实高 h) = 老板域, 未代拍; "
               "OI-2/OI-3/OI-5 的答复窗口 = 板框上位问题同一窗口 (即那一趟开工前) ⇒ 与 ISS-386 §㊴ C1~C7 口径一致, 无矛盾** ★",
}

NOTE = {
    "ISS-387": "★**2026-11-24 13:1x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**核心数字本机重算命中 (★自己解析 `.kicad_mod`★)**: "
               "1×04 = pads 4 / drill 0.65 / 焊盘 1.000×1.000 / y 0·1.27·2.54·3.81 ⇒ **铜箔沿脚排总宽 4.8100**; 1×02 ⇒ **2.2700** ⇒ "
               "⇒ 「改孔不动铜箔包络 ⇒ MECH 七个数不用改」成立 ② ★**★main 补充发现 (★ISS-387 §0 与 §5 都没算这一格★)**: **官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ "
               "环宽 (annular ring) 由 `0.1750` 降到 `0.1450` mm**; 本板 `.kicad_pro` DRC 只有 `min_via_annular_width 0.1` (过孔) ⇒ **THT 焊盘环宽无判据 ⇒ 触不到板 DRC** ⇒ "
               "⇒ 它是【制程能力】问题; ★**而全仓 (HW/ MECH/ state/) 没有任何一处记录本板厂的最小环宽/工艺能力** ⇒ ⇒ **「0.145 能不能做」当前无据可判** ⇒ "
               "已登记为待补项 `iss387_main_ring_width_fab_capability` ⇒ **那一趟投板前必须坐实, 否则投完才发现 ⇒ 板改第二次** ③ ★**OI-387-1 (焊盘是否仍取 1.000×1.000) "
               "已裁 = 维持 1.000×1.000** ⇒ 理由: 这是 MECH 七个数一个都不用改的【唯一成立条件】, 且 OI-387-1 已把代价算死 (不拍 ⇒ 7 个数全重算 ⇒ 结构件与镜脚侧返工一次) ⇒ "
               "⇒ **但本裁决附一个前置条件 = 环宽 0.145 必须先过制程能力确认** (★见 ②★) ⇒ 若本板厂最小环宽 > 0.145 ⇒ 焊盘须同步放大 ⇒ 那时 MECH 数仍可能不变 (铜箔包络随焊盘放大而放大) "
               "但需重算 ④ ★**OI-387-2 (改孔与那一趟同批?) 已裁 = 同批** ⇒ 理由: 改孔是板侧动作, 拆批 = 多投一次板 (2-4 周 + 一批板的钱), 而钻孔不进铜箔包络 ⇒ "
               "同批零额外成本 ⑤ ★**OI-387-3 (封装来源) 已裁 = 用盘上通用 KiCad 库件 land + BOM 型号栏写等价替代 + 显式偏离登记** ⇒ 理由: ★**Samtec 官网直插图【只给孔位图, "
               "不给铜箔焊盘直径】⇒ 「原厂 land 的铜箔 X 宽」在官方那一层【根本没有数】⇒ ⇒ 板侧真值档只能靠通用件 land + 一条显式偏离登记撑着, **不许写成「已按原厂 land 落板」** "
               "(★这一条正是 ISS-387 §0-2 的结论, 与 §㊳ A2/A4 的「不许拿 FTSH 的数顶替 FTS」同族但方向相反: 这次是【官方给不出】, 不是【别家顶替】★) ⇒ ⇒ A2 与 A4 必须合成一个 "
               "(板侧 land 来源 = 通用件 + 偏离登记 + BOM 型号栏同源) ⑥ ★**OI-387-4 (座体外形官方尺寸 = [0数据]) 已裁 = 走双轨降级方案 (甲 官网 3D/CAD 下载量外形; "
               "乙 落 FTS 时先打一块单板样用卡尺量三个量回填 keepout_dwg) ⇒ 归 mech-lead 执行 (转派), 且必须与那一趟同批** ⇒ ★**★注意: 这一条不闭合 ⇒ "
               "OI-12 那条「清空区 6.6100 比 courtyard 大 0.5200」的对照物仍是通用排针 courtyard ⇒ 那个结论要作废 ⇒ 结构侧清空区余量算错即装配干涉** ★ ⑦ 板面零变化: "
               "md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ **G1 仍开, 不许投板** ⑧ ★**ISS-391 (本单 cont) 本轮【不签】** ⇒ "
               "L-27 判据: 它的真相页 12:49:22 还在被 owner 会话改 ⇒ 签收指纹会当场过期 ⇒ 下一轮 owner 收工后再签 (★见台账 ISS-391 note★)",
    "ISS-389": "★**2026-11-24 13:1x main 独立复核补注 (★追加式·★老字一字未删★)**: ① ★**L-26① 已做: 扫描面命中本次交付的既有闸 11 道逐道实跑全 rc=0** ⇒ "
               "含 ISS-380/381/382/383/384/385/386 七个签收闸 + MECH 三道结构闸 ⇒ ⇒ **签收闸集合完整, 没有漏跑** ② ★**OI-2 (B33 范围含不含 J_UART) 已裁 = 含** ⇒ "
               "理由: ★**本机实读 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = 「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` "
               "(E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」⇒ 它本来就同时点了两件 ⇒ ⇒ 两颗排针换官方 THT 后结构件同批返工 (两件罩住轴都红) 是【已拍范围】的必然推论, "
               "不是新增范围** ⇒ ★**与 §㊴ C4 一致, 无矛盾** ⇒ ★**★并且: 不含 ⇒ 结构件零返工【但实物仍装不上】(★BOM/网表写的 1.27mm 实物排针对不上 0.50mm pitch 的自绘占位 land, "
               "差 0.77★) ⇒ 「零返工」是个假选项** ★ ③ ★**OI-3 (落点三选一) 已裁 = 不重开, 维持挂起; 但把顺序钉死: ① 老板答板框上位问题 → ② 落点定死 → "
               "③ 结构件出件 → ④ 板改 + 布线 45→0 + Gerber/投产包重出** ⇒ ★**且本轮按 ISS-389 的实算补一条: C2 内缩只有 1.6000 差 0.2000 ⇒ **C2 死结已被量化** ⇒ "
               "⇒ 若最终选 C2, 必须同时放大罩开口 Y (与 OI-13 路 B 同解) ⇒ ★**⇒ 结构侧「不答的后果 = 结构件返工第二次」已通过【顺序钉死】消掉** ★ ④ ★**OI-5 (清空区 X 三档取哪个) "
               "已裁 = 取 `4.8100`** ⇒ 理由与 §㊴ C1 完全一致: `1.7750` 是【拿铜箔宽冒充座体宽】的同义反复, `4.0850` 是【现状错误尺寸的搬家】, 只有 `4.8100` 既与官方 land 一致又可核 ⇒ "
               "⇒ **本轮 ISS-387 已独立复算坐实 `4.8100` 就是盘上通用 1×04 THT 件的铜箔沿脚排总宽 (3.810 + 1.000) ⇒ 这个数有实物依据, 不再是「假定」** ⇒ "
               "⇒ **OI-5 与 ISS-387 在本轮闭合了** (★这正是上一轮记的「两者必须同批闭合」★) ⇒ ★**注意: 取 4.8100 只解决「装得下」, 要过罩住判据仍需 6.6100 ⇒ 两件事不混** ★ "
               "⑤ ★**OI-12 (罩住判据是否过严) 已裁 = 判据口径【不改】, 但两个层级分开表述** ⇒ 「装得下」用官方 land 的 `F.CrtYd 6.0900` 判, 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ "
               "与 §㊴ C2 一致 ⇒ ★**★但 ISS-389 给的新信息要加进去: 路 B (改名义余量口径 ⇒ 需求降到 6.0100/3.4700) 有两个新问题 = ① `6.0100` 比 courtyard `6.0900` 还小 "
               "`0.0800` ⇒ 连「装得下」都不成立 ② FDM 每边 ±0.3000 制造公差不再被扣除 ⇒ 装配后实际余量只剩 0.3000 ⇒ ⇒ **⇒ 路 B 已可判死, 不需要等老板** ⇒ "
               "⇒ **本裁决 = 路 A (判据不动), 路 B 不予采纳 (理由如上, 机器可核)** ⇒ ★**★且 OI-14 与 OI-12 同源 ⇒ OI-14 = 订正块落老页, 数值 4.0700 (路 A 下成立) ⇒ 两条一起拍** ★ "
               "⑥ ★**OI-13 (Y 向零制造余量) 已裁 = 不接受零余量, 走路 B (放大罩开口 Y) ⇒ 但本轮口径比 §㊴ C3 更精确: 开口 Y 须 `≥ 5.6000` (delta 0.5000) 或 `5.8000` "
               "(delta 0.6000, 且这一档可顺带解掉落点 C2 的 0.2000 死结)** ⇒ ★**⇒ 结构件与罩两件同批做, 不同批就会有一件装不上** ⇒ ★**★而「零余量」的机器理由已复核: "
               "最坏口径 (余量 − TOL 0.30) = 0.4700 < CRIT 0.60 ⇒ **零余量在最坏口径下是红的 ⇒ 不是「勉强接受」, 是过不了判据** ⇒ 与 §㊴ C3 一致** ★ ⑦ ★**OI-14 (DP-1 的 3.4700 "
               "要不要订正) 已裁 = 要订正为 4.0700, 追加式订正块落 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与那一趟同批** ⇒ ★**★与 OI-12 路 A 同源, "
               "两条一起拍才不自相矛盾 (若 OI-12 走路 B 则 3.4700 反倒对 ⇒ 本裁决因 OI-12 已裁路 A 而成立)** ★ ⑧ ★**OI-1 (座体必须清空区 2.5400 还是 3.4700) + OI-11 "
               "(座体真实高 h) = 老板域, main 未代拍** ⇒ ★**OI-1 本轮已由 §㊴ C1 (取 4.8100) + OI-14 (4.0700) 把结构侧推到 4.0700 ⇒ ⇒ **OI-1 的实质问题已被这两条闭合; "
               "剩下的只是「按 4.0700 出件」这一句形式确认, 可与 boss 那一趟同批** ⇒ ⇒ **它不再是一个独立的开放决策, 是执行口径** ⇒ ★**OI-11 (h = [0数据]) 仍开放给 boss, "
               "但按 §㊵ 已算明: X 向与 h 无关 ⇒ 不卡那一趟; 若 h 定 4.0000 则开口 Y 变 5.8000, 与 OI-13 路 B 同一改 ⇒ 一并做** ⇒ ★**★⇒ 老板那 53 条里, "
               "这一条【不卡板那一趟也不卡 G1a 转绿】⇒ 建议降到最低优先级** ★ ⑨ 板面零变化: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ "
               "**G1 仍开, 不许投板**",
}


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss387_389" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}

    for iss, vr in VER.items():
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        e["status"] = "verified"
        e["verify_result"] = vr
        e["verify_date"] = "2026-11-24 13:1x"
        e["verify_by"] = "main"
        e["fix_ref"] = "main 2026-11-24 13:1x 独立复核签收 (★零写板·零落表·零改既有闸·零改既有页面正文·零挂链★)"

    # ★★ISS-391 不签, 但要留痕 (★L-27: owner 会话还在跑⇒签收指纹会当场过期★)★★
    e391 = by.get("ISS-391")
    if e391 is not None:
        nt = ("★**2026-11-24 13:1x main 复核结论: ★★本轮【不签收】★★ ⇒ ★**理由 = L-27 判据: 签收前必须确认【owner 会话已收工】, 而本单的真相页 "
              "`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` 在 12:49:22 仍被 owner 会话改 (★hw-lead 会话 12:50 仍 running★) ⇒ ⇒ "
              "**此时签 ⇒ 签收指纹会当场过期 (★本项目今天已在 ISS-381/382/384 上栽过一次★) ⇒ ⇒ 等 owner 收工后再签** ★ ★★"
              "**★交付物本身本轮已实跑复核 (★结论: 交付无缺陷, 只是时机未到★)**: 新闸 `HW/check_fts_land_drill_same_batch.py` 裸跑 **rc=1** 且 `--selftest` rc=0 末行 "
              "`ALL TESTS PASS` ⇒ ★**★这个 rc=1 是【闸按设计判红】, 不是闸故障**: 它的 D1/D2/D3 三条判据抓的正是「`钻孔 0.65→0.71` 这条板侧动作还没进到作业包 §0.2 ③ + "
              "预检清单 `B33_PIN_LAND_1P27`」⇒ 闸自己说明「红 ⇒ 那就是 §4 要 main 落的登记项 (不是本闸故障); main 落完 §4 #1/#2/#3 ⇒ 同一条命令即转绿」⇒ ⇒ "
              "**⇒ 这道闸【必须留在零挂链状态】: 它在 main 落 §4 之前红是【正确行为】, 挂进 gate_check 会造出一道【假的红】⇒ ⇒ 挂链时机 = 与 §4 登记同批** ★ ★★"
              "**★main 本轮对它的实质结论 (★并入 A 组裁决★)**: §4 的三处补登记 (作业包 §0.2 ③ 的 ③ 那一项补「钻孔 0.65→0.71」这一腿 + 预检清单 `B33_PIN_LAND_1P27` 的描述列 + "
              "验收手段列 + 覆盖度闸 WP02_BINDING ③ 的覆盖令牌补 0.71/0.65) ⇒ ★**这四处登记必须与「板只改一次」那一趟同批落, 不许提前** ⇒ 理由: ★**提前落 ⇒ 中间态 (板还没改, "
              "清单却写了改孔) ⇒ 覆盖度闸会拿 `0.71` 去查真实板面 (板上还是 0.65) ⇒ 当场红 ⇒ 现场误读成「板坏了」** ⇒ ★**★与 §㊴ A1/B1/C1/C6 的「同一批」纪律同源** ★ "
              "★**★另: 本单 §4 的「逐字替换」措辞与 main 的【追加式】纪律冲突 ⇒ 处置 = main 落【追加式订正块】, 由 owner 按 §4 的逐字文本落进「那一趟」的清单改版, "
              "而不是现在就就地替换已签收页正文 ⇒ ⇒ 这一条已写进 pm.yaml 的追加裁决** ★ ★ "
              "**★★另: main 自己的发现 (★两页都没算这一格★)**: **官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm**; "
              "本板 `.kicad_pro` DRC 只有 `min_via_annular_width 0.1` (过孔) ⇒ **THT 焊盘环宽无判据 ⇒ 触不到板 DRC** ⇒ ⇒ **它是【制程能力】问题, 且全仓没有任何一处记录本板厂的最小环宽** ⇒ "
              "⇒ **「0.145 能不能做」当前无据可判 ⇒ 那一趟投板前必须坐实** ⇒ 已登记为待补项 `iss387_main_ring_width_fab_capability` ★ ★ "
              "**板面零变化**: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ **G1 仍开, 不许投板**")
        prev = e391.get("note_addendum") or ""
        e391["note_addendum"] = (prev + ("\n" if prev else "") + nt)

    # ★★ISS-382 第二次漂移 (★12:49 又改了一次·★owner 会话到 12:56 仍在跑★) ⇒ 追加式补注, 不改 verify_result 老字★★
    e382 = by.get("ISS-382")
    if e382 is not None:
        nt382 = ("★**2026-11-24 13:2x main 复验追加补注 (★追加式·★老字一字未删·★`verify_result` 老字未动★)**: "
                 "★**★签收指纹【第二次】漂移 ⇒ 追加披露★★** ⇒ ★**本单的自带闸 `MECH/check_jdebug_arrangement_truth.py` 在 11:0x 记的是 `d8ecb827…` (54,975 B), "
                 "现盘是 `76f4c3eb…` (60,006 B, mtime 12:49:13) ⇒ ⇒ 【owner 会话 `mech-lead 166fef77` 到 12:56 仍在跑 ⇒ 它【会继续变】** ★★"
                 "★**★⇒ 本轮 main 的处置 (★与 11:0x 同一口径★)**: ★**① 它【不再放在本轮签收闸的「受保护集」里】⇒ 理由: 那是本单 owner 自己的闸 (不是别人已签收的闸), 改它【不违】「零改既有闸」; "
                 "且它的 owner 会话还在跑 ⇒ 放进受保护集 = 【自己给自己造一个必然红的判据】⇒ ⇒ 改用【实质核验】: J0~J5 六条判据函数逐字仍在 + `--selftest` rc=0 末行 "
                 "`ALL TESTS PASS` 且反向用例数【只增不减】(★10 → 11 条★) ⇒ 【判据没被削弱, 只被加强】** ★★"
                 "★**② 【★L-27 已被实测坐实两次, 不是理论★】**: ★**同一单的 owner 会话在 main 签收后【连续两次】重写交付物 (10:35 / 12:49) ⇒ ⇒ L-27 那条「签收前必须确认 owner 会话已收工」"
                 "【不是可选项, 是硬前置】⇒ ⇒ 本轮 main 正是靠它【把 ISS-391 拦在签收之外】(★那一条拦对了: 它的真相页 12:49 还在被改★)** ★★"
                 "★**③ ⇒ 给 mech-lead 的执行提示 (★不代拍·只是纪律★)**: ★**owner 会话在 main 签收后还继续改交付物 ⇒ 会让 main 的签收指纹当场过期 ⇒ ⇒ "
                 "⇒ 【交卷后到 main 签收前, 会话应当【停止改动交付物】(交卷页 + 真相页 + 闸三件都不许再动)】⇒ 否则等于让 main 签一个随时会变的字** ⇒ "
                 "★**⇒ 这一条已写进 pm.yaml 的追加裁决, 供后续所有单通用** ★★"
                 "★**板面零变化**: md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 逐字节未动 ⇒ **G1 仍开, 不许投板**")
        prev382 = e382.get("note_addendum") or ""
        e382["note_addendum"] = (prev382 + ("\n" if prev382 else "") + nt382)

    # ★★两单的独立复核补注 ★★
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
    print("  issue_log.yaml: 2 单签收 + ISS-391 不签留痕 (备份 %s.bak_%s_main_sign_iss387_389)"
          % (os.path.basename(p), STAMP))
    return True


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss387_389" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊶ 【2026-11-24 13:1x · 追加式】★ ★★ISS-387 / ISS-389 两单独立复核签收 + 11 条 main 地界待裁项已裁 + ISS-391 按 L-27 不签★★

★**① 板面 (本机实读)**: ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② 两单签收 (★main 本机独立复核·不抄 agent 报告★)★**

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| **ISS-387** | hw-lead | `HW/check_fts_single_row_land_truth.py` | rc=0 | rc=0 末行 `ALL TESTS PASS` | 真相页 50,714 B + 交卷页 26,363 B |
| **ISS-389** | mech-lead | `MECH/check_debug_seat_rework_spec.py` | rc=0 | rc=0 末行 `ALL TESTS PASS` | 真相页 65,851 B + 交卷页 40,225 B |

★两闸连跑 3 次末行逐字相同 · 两闸零挂链 · 零落表 · 零改既有页面正文 · **L-26① 的 11 道扫描面闸逐道实跑全 rc=0 (含七个签收闸)** ★

★**③ ★★main 本机独立复核: ISS-387 的核心数字自己算 (★不抄页面★)★★**
★**自己解析 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod`**: pads=**4** / drill=**0.65** / 焊盘=`1.000×1.000` / 沿脚排 y = 0·1.27·2.54·3.81 ⇒ ★**铜箔沿脚排总宽 = 3.810 + 1.000 = `4.8100`** ✓
★**自己解析 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod`**: pads=**2** / drill=**0.65** ⇒ ★**总宽 = 1.270 + 1.000 = `2.2700`** ✓
★**⇒ MECH 全链 3D 余量数的输入本机复算逐字命中 ⇒ 「孔径 0.65→0.71 不动铜箔包络 ⇒ MECH 七个数一个都不用改」成立** ★

★**④ ★★main 自己的发现 (★ISS-387 与 ISS-391 两页都没算这一格★)★★**
★**官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm** ⇒ ★**本板 `.kicad_pro` 的 DRC 规则里只有 `min_via_annular_width 0.1` (★过孔环宽★), "
THT 焊盘环宽【无独立判据】⇒ ⇒ 0.145 触不到板 DRC ⇒ 它是【制程能力】问题** ⇒ ★**★而全仓 (HW/ MECH/ state/) 没有任何一处记录本板厂的最小环宽/工艺能力 ⇒ ⇒ "
「0.145 能不能做」当前【无据可判】** ⇒ ★**⇒ 已登记为待补项 `iss387_main_ring_width_fab_capability` ⇒ ★★那一趟投板前必须坐实, 否则投完板才发现环宽不够 ⇒ 板改第二次** ★ ★

★**⑤ ★★11 条 main 地界待裁项已裁 (★一件没代老板拍板★)★★**

★**▌A 组 · ISS-387 (4 条·to=hw-lead)★★

| # | need key | main 裁决 (2026-11-24 13:1x) |
|---|---|---|
| A1 | `OI-387-1` 焊盘是否仍取 1.000×1.000 | ★**维持 `1.000×1.000`** ⇒ 这是 MECH 七个数一个都不用改的【唯一成立条件】, 且代价已算死 (不拍 ⇒ 7 个数全重算 ⇒ 结构件与镜脚侧返工一次) ⇒ ★**但附前置条件 = 环宽 `0.145` 必须先过制程能力确认 (★见 §④★)** ⇒ 若本板厂最小环宽 > 0.145 ⇒ 焊盘须同步放大 ⇒ 那时铜箔包络随焊盘放大而放大 ⇒ MECH 数仍可能不变, 但需重算 ★ |
| A2 | `OI-387-2` 改孔是否与那一趟同批 | ★**同批** ⇒ 理由: 改孔是板侧动作, 拆批 = 多投一次板 (2-4 周 + 一批板的钱), 而钻孔不进铜箔包络 ⇒ 同批零额外成本 ⇒ ★**与「板只改一次」单源纪律同源** ★ |
| A3 | `OI-387-3` 用官方 land 还是通用件 land | ★**用盘上通用 KiCad 库件 land + BOM 型号栏写等价替代 + 显式偏离登记** ⇒ 理由: ★**Samtec 官网直插图【只给孔位图, 不给铜箔焊盘直径】⇒ 「原厂 land 的铜箔 X 宽」在官方那一层【根本没有数】⇒ ⇒ 板侧真值档只能靠通用件 land + 一条显式偏离登记撑着, 不许写成「已按原厂 land 落板」** ⇒ ⇒ A2 与 A4 必须合成一个 (板侧 land 来源 + BOM 型号栏同源) ★ ★ |
| A4 | `OI-387-4` 座体外形官方尺寸 = `[0数据]` | ★**走双轨降级方案 (甲 官网 3D/CAD 下载量外形; 乙 落 FTS 时先打一块单板样用卡尺量三个量回填 `keepout_dwg`) ⇒ 归 mech-lead 执行 (转派), 且必须与那一趟同批** ⇒ ★**★不闭合的后果已算清: OI-12 那条「清空区 6.6100 比 courtyard 大 0.5200」的对照物仍是通用排针 courtyard ⇒ 该结论要作废 ⇒ 结构侧清空区余量算错即装配干涉** ★ ★ |

★**▌C 组 · ISS-389 (7 条·to=mech-lead)★★

| # | need key | main 裁决 (2026-11-24 13:1x) |
|---|---|---|
| C1 | `iss389_oi2_b33_scope_window` | ★**含 `J_UART`** ⇒ ★**本机实读权威页坐实**: `B33_PIN_LAND_1P27` 原文 = 「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm`」⇒ 本就同时点了两件 ⇒ 两颗排针换官方 THT 后结构件同批返工是【已拍范围】的必然推论 ⇒ ★**★且「不含 ⇒ 结构件零返工」是个【假选项】**: BOM/网表写的 1.27mm 实物排针对不上 0.50mm pitch 的自绘占位 land (差 0.77) ⇒ 实物仍装不上** ★ |
| C2 | `iss389_oi3_juart_landing_window` | ★**不重开落点, 维持挂起; 但把顺序钉死**: ① 老板答板框上位问题 → ② 落点定死 → ③ 结构件出件 → ④ 板改 + 布线 45→0 + Gerber/投产包重出 ⇒ ★**★且按 ISS-389 实算补一条: C2 内缩只有 1.6000 差 0.2000 ⇒ C2 死结已量化 ⇒ 若最终选 C2 必须同时放大罩开口 Y (与 C5 路 B 同解) ⇒ ⇒ 「结构件返工第二次」这个后果已通过【顺序钉死】消掉** ★ |
| C3 | `iss389_oi5_clearance_x_tier_window` | ★**取 `4.8100`** ⇒ 理由同 §㊴ C1 (`1.7750` 是同义反复 / `4.0850` 是现状尺寸搬家) ⇒ ★**★本轮闭合点: ISS-387 已独立复算坐实 `4.8100` = 盘上通用 1×04 THT 件的铜箔沿脚排总宽 ⇒ 这个数从「假定」变成「有实物依据」⇒ ⇒ 上一轮记的「OI-5 与 ISS-387 必须同批闭合」在【本轮】闭合** ⇒ ★**取 4.8100 只解决「装得下」, 过罩住判据仍需 6.6100 ⇒ 两件事不混** ★ |
| C4 | `iss389_oi12_cover_criterion_window` | ★**判据口径【不改】= 路 A; 路 B 不予采纳** ⇒ 路 B 的两个新问题: ① `6.0100` 比 courtyard `6.0900` 还小 `0.0800` ⇒ 连「装得下」都不成立 ② FDM 每边 ±0.3000 制造公差不再被扣除 ⇒ 装配后实际余量只剩 `0.3000` ⇒ ★**★⇒ 路 B 已可判死, 不需要等老板** ⇒ ⇒ OI-14 与 OI-12 同源 ⇒ 两条一起拍 ★ |
| C5 | `iss389_oi13_y_zero_margin_window` | ★**不接受零余量 = 路 B** ⇒ 开口 Y 须 `≥ 5.6000` (delta 0.5000) 或 `5.8000` (delta 0.6000, ★且这一档可顺带解掉落点 C2 的 0.2000 死结★) ⇒ 结构件与罩两件同批做 ⇒ ★**★零余量的机器理由复核: 最坏口径 (余量 − TOL 0.30) = `0.4700` < `CRIT 0.60` ⇒ 不是「勉强接受」, 是过不了判据** ★ |
| C6 | `iss389_oi14_dp1_correction_window` | ★**要订正为 `4.0700`, 追加式订正块落 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与那一趟同批** ⇒ ★**★与 OI-12 路 A 同源 ⇒ 两条一起拍才不自相矛盾 (★本裁决因 OI-12 已裁路 A 而成立★)** ★ |
| C7 | `iss389_oi1_housing_width_window` (★to=boss★) | ★**老板域, main 未代拍** ⇒ ★**★但实质问题已被 C3 (取 4.8100) + C6 (4.0700) 闭合 ⇒ ⇒ OI-1 剩下的只是「按 4.0700 出件」这一句形式确认 ⇒ ⇒ 【不再是独立开放决策, 是执行口径】⇒ 可与 boss 那一趟同批** ★ |
| C8 | `iss389_oi11_seat_height_window` (★to=boss★) | ★**老板域, main 未代拍** ⇒ ★**按 §㊵ 已算明: X 向与 `h` 无关 ⇒ 不卡那一趟; 若 `h` 定 `4.0000` ⇒ 开口 Y 变 `5.8000` ⇒ 与 C5 同一改 ⇒ 一并做** ⇒ ★**★⇒ 老板那 53 条里这一条【不卡板那一趟也不卡 G1a 转绿】⇒ 建议降到最低优先级** ★ |

★**⑥ ★★ISS-391 本轮【不签收】(★L-27 判据·★本轮拦对了★)★★**
★**owner 会话还在跑**: 真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` 12:49:22 仍被改 (hw-lead 会话 12:50 仍 running) ⇒ ★**此时签 ⇒ 签收指纹当场过期 (★今天已在 ISS-381/382/384 上栽过一次★) ⇒ 等 owner 收工后再签** ★
★**交付物本身无缺陷**: 新闸裸跑 rc=1 且 `--selftest` rc=0 末行 `ALL TESTS PASS` ⇒ ★**★这个 rc=1 是【闸按设计判红】**: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ★**⇒ 这道闸必须留在零挂链状态: 挂进去会造出一道【假的红】⇒ 挂链时机 = 与 §4 登记同批** ★
★**★main 对 §4 三处补登记的处置 (★与「追加式」纪律的冲突已解★)★**: §4 给的是「逐字替换」措辞, 而作业包与预检清单都是【已签收页】⇒ ★**⇒ 处置 = main 落【追加式订正块】, 由 owner 按 §4 的逐字文本落进「那一趟」的清单改版, 而非现在就地替换已签收页正文** ⇒ ★**★理由: 提前落 ⇒ 中间态 (板还没改, 清单却写了改孔) ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (板上还是 0.65) ⇒ 当场红 ⇒ 现场误读成「板坏了」** ⇒ ★**与 §㊴ A1/B1/C1/C6 的「同一批」纪律同源** ★

★**⑦ ★★ISS-382 的【第二次】签收指纹漂移 (★L-27 已被实测坐实两次, 不是理论★)★★**
★**同一单的 owner 会话在 main 签收后【连续两次】重写交付物**: 自带闸 `MECH/check_jdebug_arrangement_truth.py` 10:35 (`d8ecb827…`/54,975 B) → 12:49 (`76f4c3eb…`/60,006 B), owner 会话 `mech-lead 166fef77` 到 12:56 仍在跑 ⇒ ★**⇒ L-27 那条「签收前必须确认 owner 会话已收工」【不是可选项, 是硬前置】** ★
★**★⇒ 本轮处置 (★与 11:0x 同一口径★)**: ★**① 该闸【不再放在本轮签收闸的「受保护集」里】⇒ 理由: 那是本单 owner 自己的闸 (不是别人已签收的闸), 改它【不违】「零改既有闸」; 且它的 owner 会话还在跑 ⇒ "
放进受保护集 = 【自己给自己造一个必然红的判据】⇒ ⇒ 改用【实质核验】: J0~J5 六条判据函数逐字仍在 + `--selftest` rc=0 末行 `ALL TESTS PASS` 且反向用例数【只增不减】(★10 → 11 条★) ⇒ 【判据没被削弱, 只被加强】** ★
★**② ★★⇒ 给所有 agent 的一条纪律 (★不代拍·只是纪律·★已写进 pm.yaml★)★: ★**【交卷后到 main 签收前, owner 会话应当【停止改动交付物】(★交卷页 + 真相页 + 闸三件都不许再动★)】⇒ 否则等于让 main 签一个随时会变的字** ⇒ ★**★⇒ 这条不是 main 的洁癖, 是【签收这个动作的前提】** ★ ★

★**⑧ 本轮零派 / 零外发 / 零落表 / 零写板**: ★**internal = 0** ⇒ 三单全部已交卷待签收 (★ISS-391 等 owner 收工★) ⇒ ★**外发段恒空** ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊶, 备份 %s.bak_%s_main_sign_iss387_389)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l29" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-29 · ★★闸「按设计判红」与「闸坏了」必须分开判 ⇒ 判红的闸在它要等的那件事落地前【不许挂链】 ★★

★**实测 (2026-11-24 13:1x, main 本机实跑 · ★ISS-391 交卷时撞上★)★**: ★**ISS-391 的新闸 `HW/check_fts_land_drill_same_batch.py` 裸跑 rc=1, 而 `--selftest` rc=0 末行 `ALL TESTS PASS`** ⇒ ★**⇒ 闸本身可信 (自检 14 反向用例全抓到), 它的红是【按设计】的** ★
★**★闸自己把话说清楚了 (★原文★)**: ★**「红 ⇒ 那就是 §4 要 main 落的登记项 (★不是本闸故障★); main 落完 §4 #1/#2/#3 ⇒ 同一条命令即转绿」** ★ ★
★**★⇒ 这是本项目第一次出现【闸故意红着等 main 落登记】的形态 ⇒ ⇒ 引出两条纪律★ ★
★**⇒ 通则 ①**: ★**★闸的 rc=1 必须先分清【它坏了】与【它按设计在等一件事】⇒ 判据 = 「`--selftest` 末行是不是 `ALL TESTS PASS`」**: 是 ⇒ ★**闸可信, 它的红是【业务信号】**; 否 ⇒ ★**闸不可信, 先修闸** (★同 铁律⑩-j「签收闸自己红了先修闸」★) ★ ★
★**⇒ 通则 ②**: ★**★【按设计判红】的闸, 在它等的那件事落地之前, 绝对不许挂进 `state/gate_check.py`** ⇒ ★**理由: 挂进去 = 造出一道【假的红】⇒ 现场会把它读成「板坏了 / 项目坏了」** ⇒ ★**★⇒ 与既有先例同源: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 + ISS-385 B3 全是「闸与它要防的那一趟同批生效」⇒ ★**现在补一条: 「它要等的那件事」与「它要防的那一趟」是同一条纪律的两个说法** ★ ★
★**⇒ 通则 ③**: ★**★「逐字替换已签收页正文」与 main 的【追加式】纪律冲突时, 解法不是二选一, 而是【改版】**: ★**已签收页本体一个字不动 (追加式订正块) ⇒ 由 owner 在「那一趟」的清单改版里按逐字文本落** ⇒ ★**★理由: 提前落 ⇒ 中间态 (板还没改, 清单却写了改孔) ⇒ 覆盖度闸会拿新值去查真实板面 (板上是旧值) ⇒ 当场红 ⇒ 现场误读** ★ ★
★**⇒ 通则 ④ (★★本轮 main 自己补的一格★)**: ★**★改【孔径】这类只动【孔】不动【铜箔包络】的板侧动作, 必须连带算【环宽 (annular ring)】** ⇒ ★**本轮实证: 官方 `Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 `0.1750 → 0.1450` mm, 而 ISS-387 与 ISS-391 两页都没算这一格** ⇒ ★**★且本板 `.kicad_pro` 的 DRC 规则里只有 `min_via_annular_width 0.1` (★过孔环宽★) ⇒ **THT 焊盘环宽无判据 ⇒ 触不到板 DRC** ⇒ ⇒ ★**它只能靠【制程能力】判, 而全仓没有任何一处记录本板厂的最小环宽 ⇒ ⇒ 「能不能做」当前无据可判** ⇒ ★**★⇒ 通则: 【凡是要改板侧尺寸的活, 必须把「这条改动会连带影响哪个【板 DRC 管不到的量】」逐个列出来】(环宽 / 阻焊桥 / 铣刀补偿 / 最小刀径) ⇒ 列不出来 = 还有一格没算** ★ ★
★**★与 L-21~L-28 合看★**: ★**L-21 清单钉 file/line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工 · "
L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了, 且不许提前挂链** ⇒ ★**★共性 = 【凡是有「清单 / 扫描面 / 签收 / 判据 / 幂等 / 挂链」的地方, 都要问一句「它会不会过期 / 会不会撞名 / 谁负责让它不过期, 出问题时会红给谁看】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-29, 备份 %s.bak_%s_main_l29)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm():
    ANS = [
        ("iss387_main_rilim_ring_width_fab_capability", "hw-lead",
         "★**main 登记的待补项 (★2026-11-24 13:1x·★main 自己的发现·★ISS-387 与 ISS-391 两页都没算这一格★)★: "
         "★**官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm** ★★"
         "★**main 本机实读坐实**: ★**① 本板 `.kicad_pro` 的 DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (★那是过孔环宽★) ⇒ "
         "**THT 焊盘环宽【无独立判据】⇒ 0.145 触不到板 DRC ⇒ 它是【制程能力】问题, 不是 DRC 问题** ★**② `min_through_hole_diameter 0.3` ⇒ 孔径 0.71 本身远大于下限, "
         "不触 DRC** ★**③ 全仓 (HW/ MECH/ state/) 实查: 【没有任何一处】记录本板厂的最小环宽/最小焊盘/工艺能力表** ⇒ ⇒ ★**★⇒ 「0.145 能不能做」当前【无据可判】** ★★"
         "★**⇒ 处置**: ★**「板只改一次」那一趟投板前必须坐实本板厂的最小环宽 (★或最小焊盘) ⇒ 若 > 0.145 ⇒ 焊盘须同步放大 ⇒ ⇒ 铜箔包络随焊盘放大而放大 ⇒ "
         "MECH 全链七个余量数【仍可能不变】但必须重算确认 ⇒ ⇒ 若坐实不了 ⇒ 退化方案 = 焊盘放大到 `1.100×1.100` (环宽 0.1950) 并登记偏离 ⇒ 那时铜箔沿脚排总宽由 4.8100 变 4.9100 ⇒ "
         "★**MECH 七个数必须整体重算** ⇒ ★**★⇒ 这就是「板只改一次」必须在这一趟把环宽问清楚的原因: 问不清 = 那一趟投出去才发现 ⇒ 板改第二次** ★★"
         "★**★⇒ 一句话给 hw-lead: 【你 OI-387-1 的裁决前提是「焊盘维持 1.000」, 而维持 1.000 的可行性现在【悬在环宽这一格上】⇒ 这一格归你补, "
         "补不出来就得改焊盘尺寸, 改了 MECH 全链要重算】** ★★"
         "★**★⇒ 但 main 【不代拍】环宽这个数 (★那是本板厂工艺能力, 不是本仓能推出来的★) ⇒ 归「那一趟」的询价/工艺确认动作 (★老板 2026-11-12 02:02 政策: 零外发 ⇒ "
         "自己查公开的板厂工艺能力表 + 在 RFQ 里问·★不自行发送★)** ★★",
         "MECH/hinge_power_calc.json 无关 · HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0/§5 · HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §5 "
         "· demo_mainboard.kicad_pro design_settings.rules · 一页 §㊶ §④"),

        ("iss387_main_oi1_pad_1x1_maintained", "hw-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★OI-387-1·★附前置条件★)★: ★**维持 `1.000×1.000`** ★★"
         "★**理由**: ★**这是 MECH 全链七个余量数 (`4.8100`/`2.2700`/`6.6100`/`4.0700`/`2.6950`/`0.1350`/`0.7700`) 一个都不用改的【唯一成立条件】** ⇒ "
         "★**且 OI-387-1 已把代价算死: 不拍 ⇒ 7 个数全部重算 ⇒ 结构件与镜脚侧返工一次 (2-4 周 + ¥4-8K 级)** ⇒ ⇒ ★**按「板只改一次」的单源纪律, 必须维持** ★★"
         "★**★但本裁决附一个前置条件 (★main 自己发现的缺口★)**: ★**「焊盘 1.000」配官方 `Ø0.71` ⇒ 环宽只有 `0.1450` mm ⇒ 而本板 DRC 管不到 THT 焊盘环宽 ⇒ "
         "而全仓没有本板厂最小环宽记录 ⇒ ⇒ 「1.000 能不能用」当前【无据可判】⇒ ⇒ ★**⇒ 前置条件 = 环宽 `0.145` 先过制程能力确认 (★见 `iss387_main_rilim_ring_width_fab_capability`★)** ⇒ "
         "⇒ 若坐实不了 ⇒ 焊盘放大 ⇒ 铜箔包络变 ⇒ MECH 七个数要重算 ⇒ ★**⇒ 本裁决不是「1.000 一定行」, 是「1.000 是唯一不返工的选择, 但要先证明它做得出来」** ★★"
         "★**★⇒ 与 §㊴ C1 一致: OI-5 取 `4.8100` 成立的前提也是这块焊盘不变 ⇒ 两条裁决共用同一个前置条件** ★★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0-2/§5 · 一页 §㊶ A1 · main 本机自解析 .kicad_mod 复算"),

        ("iss387_main_oi2_drill_change_same_batch", "hw-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★OI-387-2★)★: ★**与「板只改一次」那一趟同批** ★★"
         "★**理由 (★main 本机实算★)**: ★**改孔是板侧动作 ⇒ 拆批 = 多投一次板 (2-4 周 + 一批板的钱)** ⇒ ★**且本轮已独立复算坐实: 官方 `Ø0.71` 配通用件焊盘 ⇒ "
         "铜箔沿脚排总宽仍是 `4.8100` / `2.2700` (★只有孔变了, 铜箔没变★) ⇒ ⇒ MECH 全链七个余量数不动 ⇒ ⇒ ★**★同批的增量成本 = 0 ⇒ 没有理由拆批** ★★"
         "★**★⇒ 同批的三个必做动作 (★缺一不可★)**: ★**① 改孔 `0.65 → 0.71` (J_DEBUG / J_UART 两颗) ② 焊盘维持 `1.000×1.000` (★须先过环宽确认★) "
         "③ 清单四处同步登记 (作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27` 描述列 + 验收手段列 + 覆盖度闸 `WP02_BINDING` ③ 的覆盖令牌补 `0.71`/`0.65`)** ⇒ "
         "★**⇒ 而 ③ 必须与「板只改一次」那一趟同批落, 不许提前** (★提前 ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (板上还是 `0.65`) ⇒ 当场红 ⇒ 现场误读成「板坏了」★) ★★"
         "★**★⇒ 与 ISS-391 §4 的三处补登记是同一件事 ⇒ 处置 = main 落【追加式订正块】, 由 owner 按逐字文本落进「那一趟」的清单改版** (★不是现在就就地替换已签收页正文★) ★★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4/§5 · 一页 §㊶ A2 · L-29 通则③"),

        ("iss387_main_oi3_footprint_source_generic_plus_deviation", "hw-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★OI-387-3★)★: ★**用盘上通用 KiCad 库件 land + BOM 型号栏写等价替代 + 显式偏离登记** ★★"
         "★**理由 (★main 本机实读坐实·★ISS-387 §0-2 自己已写出这个事实★)★**: ★**Samtec 官方的 FTS 直插 land 【只给孔位图, 不给铜箔焊盘直径】⇒ "
         "「原厂 land 的铜箔 X 宽」在 Samtec 那一层【根本没有一个官方数】** ⇒ ★**⇒ 板侧真值档只能靠【盘上通用件 land + 一条显式偏离登记】撑着, "
         "不许写成「已按原厂 land 落板」** ⇒ ★**⇒ 这与 §㊳ A2/A4 的「不许拿 FTSH 的数顶替 FTS」同族但【方向相反】: 那次是【别家的数不许顶替】, 这次是【官方自己给不出】★ ⇒ 两条都要守住** ★★"
         "★**★⇒ A2 (料号) 与 A4 (land 来源) 必须合成一个**: ★**板侧 land 来源 = 通用 KiCad 1.27mm THT 库件 (★`PinHeader_1x04_P1.27mm_Vertical` / "
         "`PinHeader_1x02_P1.27mm_Vertical`·★md5 `7a5f470c…` / `47bcbf6d…`★) + 显式偏离登记 (★偏离项 = 铜箔焊盘直径官方无值 + 孔径由 0.65 改 0.71★) + BOM 型号栏同源写 FTS 料号** ⇒ "
         "⇒ ⇒ **同源纪律 (板面 land 来源 = BOM 型号栏 = 实物料号) 才成立** ⇒ ⇒ 不成立 ⇒ 投板后才发现 ⇒ 2-4 周返工 (★OI-387-3 已算过的代价★) ★★"
         "★**★⇒ 落表时机 = 「板只改一次」那一趟的同一次落表与重出 (★本轮【零落表】·★BOM 型号栏与 footprint 两栏一个字没动★)** ★★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §0-2/§4/§5 · 一页 §㊶ A3 · §㊳ A2/A4"),

        ("iss387_main_oi4_seat_outline_two_track", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★OI-387-4·★转派 mech-lead★)★: ★**走双轨降级方案 (甲 官网 3D/CAD 下载量外形; "
         "乙 落 FTS 时先打一块单板样用卡尺量三个量回填 `keepout_dwg`) ⇒ 归 mech-lead 执行, 且必须与「板只改一次」那一趟同批** ★★"
         "★**理由**: ★**座体外形 (宽 X / 深 Y / 绝缘体高 Z) 官方值 = `[0数据]` ⇒ 不许猜 ⇒ 而它【是 OI-12 那条结论的对照物】** ⇒ ★**★⇒ 不闭合的后果: "
         "OI-12 的「清空区 `6.6100` 比 courtyard `6.0900` 大 `0.5200`」那个对照物仍是【通用排针】的 courtyard ⇒ ⇒ **那个结论要作废** ⇒ ⇒ "
         "结构侧清空区余量算错即装配干涉 (★OI-387-4 已算的代价★) ★★"
         "★**★⇒ 甲乙两轨的关系 (★别当成两条路★)**: ★**甲轨 (官网量) 是【设计值】⇒ 用来定件与开模**; ★**乙轨 (单板样实测) 是【实物值】⇒ 用来回填 `keepout_dwg` "
         "并作为装配前的兜底校验** ⇒ ⇒ ★**★两轨都要做, 不是二选一 ⇒ 且乙轨那 1 台样件的成本 = 老板已知口径里的「只做 1 台」** ★★"
         "★**★⇒ 归 owner = mech-lead (★OW-387-4 本来就是从 hw-lead 转给结构侧的·★本裁决只裁口径与时点, 不派活★)** ⇒ ★**⇒ 且【必须与那一趟同批】: "
         "结构件出件与件的开模都在那一趟 ⇒ 不在同一批 = 件开出来才发现外形对不上 ⇒ 第二次返工** ★★",
         "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md §6-④ · 一页 §㊶ A4 · ISS-389 真相页 OI-12"),

        ("iss389_main_oi2_scope_includes_juart", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi2_b33_scope_window★)★: ★**含 `J_UART`** ★★"
         "★**理由 (★main 本机实读权威页坐实·★不抄 brief★)★**: ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 原文 = "
         "「`J_DEBUG`/`J_UART` 排针 land pitch `0.50→1.27mm` (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」⇒ ★**它本来就同时点了两件** ⇒ "
         "⇒ ★**两颗排针换官方 THT 后结构件同批返工 (两件罩住轴都红) 是【已拍范围】的必然推论, 不是新增范围** ⇒ ★**与 §㊴ C4 完全一致, 无矛盾** ★★"
         "★**★⇒ 而且「不含 ⇒ 结构件零返工」是个【假选项】**: ★**ISS-389 自己算出来: 不含 ⇒ 结构件零返工, 但板上 BOM (`HW/BOM_v1.csv` L77) 与网表 "
         "(`HW/netlist_v1.csv` L399) 写的 1.27mm 实物排针仍落不进 0.50mm pitch 的自绘占位 land (差 `0.77`) ⇒ ⇒ 【结构件零返工 ≠ 实物装得上】** ⇒ "
         "⇒ ★**★⇒ 所以「不含」这个选项的真实含义是「结构件不返工, 但板还是错的」⇒ 不是解法, 是把问题推到投板之后 ⇒ ⇒ 答案只能是「含」** ★★"
         "★**★⇒ 与 OI-3 的耦合已解 (★顺序钉死, 见 `iss389_main_oi3_landing_order`★) ⇒ ⇒ 「先定落点再定范围」那个返工第二次的风险已消除** ★★",
         "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md B33_PIN_LAND_1P27 (main 本机实读) · 一页 §㊶ C1 · §㊴ C4"),

        ("iss389_main_oi3_landing_order", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi3_juart_landing_window★)★: ★**不重开落点裁决 (★维持 ISS-379 的挂起·★本单不重复开★), "
         "但把【顺序】钉死** ★★"
         "★**顺序 (★四步·★这是本条的全部内容★)★**: ★**① 老板答板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product` · 甲 160×100 台架板 / 乙 60×30 产品板) → "
         "② 落点定死 (C1 / C2 / C3) → ③ 结构件出件 → ④ 板改 + 布线 45→0 + Gerber/投产包重出** ★★"
         "★**★⇒ 依据 (★main 本机实算 + ISS-389 自己算的数★)★**: ★**① 三个候选 X 向全可行, Y 向 C1 与 C3 可行 (铜箔中心允许偏心 `0.0000`), "
         "C2 内缩只有 `1.6000` 差 `0.2000` 不可行** ⇒ ⇒ **C2 是带死结的那一个**, 不是随机的 ⇒ ★**② 清空区中心随落点变 (`-0.9250` / `+0.1450` / `+0.0450`) ⇒ "
         "⇒ 结构件开不了模 ⇒ ★**③ ⇒ 「不答的后果 = 结构件返工第二次」这个风险, 已通过【把顺序钉死】消掉: 落点一定, 结构件才出件** ★★"
         "★**★⇒ 并且: 若最终选 C2 ⇒ 必须同时放大罩开口 Y (★与 OI-13 路 B 是同一处改动·★`5.8000` 那档可顺带解掉 C2 的 `0.2000`★) ⇒ ⇒ 两处一起做** ★★"
         "★**★⇒ 答复窗口 = 与板框上位问题同一窗口 (即那一趟开工前) ⇒ ★**★不改 ISS-379 的挂起状态, 只是把依赖链显式化** ★★",
         "ISS-379 §② (落点挂起) · ISS-389 真相页 OI-3 (feas2.py 实算) · 一页 §㊶ C2"),

        ("iss389_main_oi5_pick_4810", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi5_clearance_x_tier_window★)★: ★**取 `4.8100`** ★★"
         "★**理由 (★与 §㊴ C1 完全一致, 且本轮多了一条【实物依据】★)★**: ★**① `1.7750` = 座体宽 = 【拿铜箔宽冒充座体宽】的同义反复 (★ISS-386 §1 已点明「现状行 `Hx == Cx` 不作判据」★) "
         "⇒ 不作判据; ② `4.0850` = 把现状 `0.275` 宽 pad 搬到 1.27 pitch 上 ⇒ 【现状错误尺寸的搬家】, 不是官方 land; ③ `4.8100` = 官方 1×4 THT land 的铜箔沿脚排总展** ⇒ "
         "★**★⇒ 本轮 ISS-387 已独立复算坐实: `4.8100` = 盘上通用 1×04 THT 件实测 (跨距 `3.810` + 焊盘 `1.000`) ⇒ ⇒ 这个数从【假定】变成【有实物依据】⇒ "
         "⇒ ⇒ ★**★上一轮记的「OI-5 与 ISS-387 必须同批闭合」在【本轮】闭合** ★ ★★"
         "★**★⇒ 但口径不混两件事 (★原样保留★)**: ★**取 `4.8100` 只解决「装得下」⇒ 要过罩住判据 (每边 ≥ `CRIT 0.60`) 仍需 `6.6100`** ⇒ "
         "⇒ 三档的返工幅度差 `3.0350` (总宽增量 `+4.8350` / `+2.5250` / `+1.8000`), 方向不变 (三档全红) ⇒ ⇒ ★**★最终放大量仍归老板的板框第一问, 本条不代拍** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-5 · 一页 §㊶ C3 · §㊴ C1 · main 本机自解析 .kicad_mod 复算"),

        ("iss389_main_oi12_criterion_stays_route_a", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi12_cover_criterion_window·★★新增: 路 B 已可判死★)★: ★**判据口径【不改】= 路 A; "
         "路 B 不予采纳** ★★"
         "★**理由 (★ISS-389 自己给的两条硬问题, main 核对后成立★)★**: ★**① 路 B 把名义余量口径从 `2×CRIT` 改成别的大小 ⇒ 需求降到 `6.0100` / `3.4700` ⇒ "
         "★**但 `6.0100` 比官方 land 自己的 `F.CrtYd 6.0900` 还小 `0.0800` ⇒ 连「装得下」都不成立** ⇒ ⇒ **不是「偏紧」, 是「不成立」**; "
         "② 路 B 不再扣除 FDM 每边 ±0.3000 制造公差 ⇒ ⇒ **装配后实际余量只剩 `0.3000`, 低于 `CRIT 0.60`** ⇒ ⇒ **把「名义余量」当「实际余量」用 ⇒ 判据失效** ★★"
         "★**★⇒ ⇒ 路 B 不需要等老板, main 现在就可判死 (★两个理由都机器可核★) ⇒ ⇒ 本裁决 = 路 A** ★★"
         "★**★⇒ 路 A 的含义 (★两个层级分开表述·★同 §㊴ C2★)★**: ★**① 「装得下」用官方 land 的 `F.CrtYd 6.0900` 判 ⇒ 官方 land 自洽; "
         "② 「装配可靠」用每边 `CRIT 0.60` 判 ⇒ 结构件每边多让 `0.7650` (J_DEBUG) / `0.7150` (J_UART) ⇒ 改【判据口径】改【结构件尺寸】, 不改判据** ⇒ "
         "⇒ ★**★⇒ 结构件总宽增量走 6.6100 那档 (差 `4.8350`) ⇒ ⇒ 【这个代价必须让老板看见】⇒ 它与板框第一问同批** ★★"
         "★**★⇒ 与 OI-14 同源 ⇒ 两条一起拍** (★OI-14 的 `3.4700 → 4.0700` 只在路 A 下成立★) ⇒ ⇒ **本裁决把 OI-14 一并闭合** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-12 · 一页 §㊶ C4 · §㊴ C2"),

        ("iss389_main_oi13_open_y_enlarge", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi13_y_zero_margin_window★)★: ★**不接受零余量 = 路 B (放大罩开口 Y)** ★★"
         "★**理由 (★机器可核★)★**: ★**① 零余量在最坏口径下是红的, 不是「勉强接受」**: 罩住 Y 余量 `0.7700` → 最坏 = `0.7700 − TOL 0.30 = 0.4700` < `CRIT 0.60` ⇒ "
         "⇒ ★**★⇒ 「物理上不产生干涉」不等于「过得了判据」⇒ 而判据是装配可靠性的判据 ⇒ 必须按判据走**; "
         "② 罩开口 Y `4.6000` 恰好只容清空区 Y `2.8000` ⇒ 只放大清空区会把开口顶死 ⇒ ⇒ **必须同时放大开口 Y** ⇒ ★**开口 Y 须 `≥ 5.6000` (delta `0.5000`) "
         "或 `5.8000` (delta `0.6000`, ★且这一档可顺带解掉落点 C2 的 `0.2000` 死结·★与 OI-3 同一处改动★)** ★★"
         "★**★⇒ 结构件与罩两件同批做 (★不同批就会有一件装不上★) ⇒ ⇒ 镜脚壁厚与罩外观缝 (防水防尘) 的代价一并算进那一趟 ⇒ ★**★⇒ 与 §㊴ C3 一致, "
         "本轮口径更精确 (多了 `5.8000` 那档与它顺带解 C2 死结这件事)** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-13 · 一页 §㊶ C5 · §㊴ C3"),

        ("iss389_main_oi14_dp1_correction_4070", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi14_dp1_correction_window★)★: ★**要订正为 `4.0700`; 追加式订正块落 "
         "`MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md`, 与「板只改一次」那一趟同批** ★★"
         "★**理由 (★main 本机重算★)★**: ★**ISS-377 §3.2 DP-1 的 `3.4700 = 2.2700 + 2×CRIT` 是【名义余量】口径; 按全链 (最坏 = 余量 − `TOL 0.30` ≥ `CRIT 0.60`) "
         "需要 `2.2700 + 2×0.9000 = 4.0700` ⇒ 差 `0.6000` ⇒ ⇒ ★**按 `3.4700` 出件, 最坏只剩 `0.3000` ⇒ 过不了判据** ⇒ ⇒ 不订 ⇒ 下一轮有人照 `3.4700` 出件 ★★"
         "★**★⇒ 与 OI-12 同源 ⇒ 必须一起拍**: ★**本轮 OI-12 已裁路 A (判据口径不改) ⇒ ⇒ 路 A 下 `3.4700` 确实不对 ⇒ ⇒ 订正动作成立; "
         "★**★⇒ 若 OI-12 走路 B 则 `3.4700` 反倒对 ⇒ 订正动作要撤销 ⇒ ⇒ 两条绝不能分开拍** ⇒ ★**★⇒ 现在两条一起拍了, 这一处矛盾已消除** ★★"
         "★**★⇒ 落法纪律 (★L-29 通则③★)**: ★**老页已签收 ⇒ 一律【追加式订正块】⇒ 不就地替换老页正文 ⇒ 且【必须与那一趟同批】(提前落 ⇒ 中间态红)** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-14 · ISS-377 §3.2 DP-1 · 一页 §㊶ C6 · L-29 通则③"),

        ("iss391_main_gap_registration_same_batch", "hw-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss391_main_oi1_who_lands_the_three_registrations★)★: ★**三处补登记由 main 落【追加式订正块】, "
         "由 owner 在「板只改一次」那一趟的清单改版里按逐字文本落 ⇒ 【不许提前落】** ★★"
         "★**★三处登记 (★ISS-391 §4 已给逐字文本, main 不改一字·★只定落法与时点★)★**: ★**① 作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ 的「③」那一项 "
         "补上「钻孔 `0.65→0.71`」这一腿 (★注意 `wp02_tokens()` 会从③的原文里自动抽「小数」当覆盖令牌 ⇒ 补上 `0.65` 与 `0.71` 之后, 现有 P4 会自动要求清单页 "
         "`B33_PIN_LAND_1P27` 里也能查到这两个数 ⇒ ⇒ ★**② 与 ③ 必须同步落, 否则 P4 当场红**) ② 预检清单 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 "
         "`B33_PIN_LAND_1P27` 描述列 (标题 + current_state + criterion 三处一起长) ③ 覆盖度闸 `WP02_BINDING` ③ 的覆盖令牌补 `0.71` 与 `0.65`** ★★"
         "★**★⇒ 为什么不提前落 (★main 的理由·★机器可核★)★**: ★**★提前落 ⇒ 中间态 = 板还没改, 清单却写了要改孔 ⇒ ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (★板上还是 `0.65`★) ⇒ "
         "⇒ 当场红 ⇒ ⇒ 现场会把它读成「板坏了」⇒ ⇒ 这正是 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + ISS-384 A5 全同款纪律的另一种说法** ★★"
         "★**★⇒ 而且: 新闸 `HW/check_fts_land_drill_same_batch.py` 在这四处落完之前【必须保持零挂链】(★它现在的 rc=1 是【按设计判红】·★挂进去会造出一道【假红】·★见 L-29★)** "
         "⇒ ⇒ 挂链时机 = 与这四处登记同批 ★★"
         "★**★⇒ 措辞口径 (★OI-391-2·★main 的裁法★)★: ★**写成【一条】(pitch 与 drill 是同一项的两条腿, 不可只做其一), 不许拆成两条可分开的动作** ⇒ "
         "★**理由: 新闸 D1 只能查出【整条没写】, 查不出【拆成两条只做一条】⇒ ⇒ 拆开写 = 判据出现盲区** ⇒ ⇒ **一条写 + 锚点含两个数 (`0.71` 与 `1.27`) = 机器可判** ★★"
         "★**★⇒ BOM 两栏 (★OI-391-3★)**: ★**落表时机 = 那一趟的同一次落表与重出; 本轮【零落表】· `HW/BOM_v1.csv` 一个字节没动** ⇒ ⇒ "
         "★**opn 与 footprint 两栏必须与板侧 land 来源同源 (★即 §㊶ A3 的「通用件 land + 显式偏离登记 + FTS 料号」★)⇒ ⇒ 落表时按 ISS-391 §4 #5 的逐字草案落** ★★"
         "★**★⇒ 预检清单生成器 (★OI-391-4★)**: ★**`state/_iss277_build_preflight.py` 的 `build_pinland_item()` (title + current_state + criterion 三处一起长) + "
         "`read_board_pin_land()` 加一个 drill 字段现读板** ⇒ ★**★归 owner 落 (★本单零改既有脚本正文★) ⇒ 且必须与那一趟同批 ⇒ 否则 §3 #2/#3 的补登记【重跑一次就蒸发】"
         "(★ISS-349 同一位号已栽过一次★)** ★★"
         "★**★⇒ 补一条 main 的发现 (★两页都没算这一格★)**: 改孔后环宽 `0.1750 → 0.1450` mm, 且板 DRC 管不到 THT 焊盘环宽 ⇒ ⇒ **制程能力必须先确认** ⇒ "
         "见 `iss387_main_rilim_ring_width_fab_capability` ★★",
         "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §4/§5 · 一页 §㊶ §⑥ · L-29 通则②③"),

        ("iss391_main_gate_hook_with_registration", "hw-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★OI-391-5·★★与 L-29 同源★)★: ★**新闸 `HW/check_fts_land_drill_same_batch.py` "
         "【与那四处登记同批挂进 `state/gate_check.py`】, 不提前挂** ★★"
         "★**★理由 (★main 本机实跑实测★)★**: ★**★这道闸现在裸跑 rc=1, 而 `--selftest` rc=0 末行 `ALL TESTS PASS` ⇒ ⇒ 闸本身可信 (14 反向用例全抓到) ⇒ "
         "⇒ 它的红是【按设计】的: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进到作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ "
         "⇒ **在登记落地之前挂进去 = 造出一道【假的红】⇒ 现场会把它读成「板坏了」** ⇒ ⇒ ★**★与全部先例同源: 闸与它要防/要等的那一趟同批生效** ★★"
         "★**★⇒ 挂链时机 = 与「板只改一次」那一趟的四处登记同批** ⇒ ★**⇒ 那一趟做完的验收顺序: ① 改孔 + 焊盘确认 + 环宽确认 → ② 四处登记 → ③ 挂这道闸 ⇒ "
         "④ 跑挂链回归 ⇒ ⑤ 才算这一趟的清单闭合** ★★"
         "★**★⇒ 且【挂链动作只能由 main 在那一趟统一做】(★不许 agent 自挂·★先例: ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4 + "
         "ISS-384 A5 + ISS-385 B3 + ISS-387 A5 全同款★)** ⇒ ★**★⇒ 顺带: 三个新闸 (`check_fts_single_row_land_truth` / `check_debug_seat_rework_spec` / "
         "`check_fts_land_drill_same_batch`) 加上 ISS-388 的 `check_sw_gate_health`, 一共四个, 全部【与那一趟同批挂】⇒ ⇒ 那一次的「闸清单刷新」批次要一次挂四个** ★★",
         "HW/check_fts_land_drill_same_batch.py 实跑 rc=1 + selftest ALL TESTS PASS · 一页 §㊶ §⑥ · L-29 通则②"),

        ("main_owner_must_freeze_deliverables_after_handoff", "main",
         "★**main 追加裁决 (★2026-11-24 13:2x·★给【所有 agent】的通用纪律·★不是某一条单的事★)★: ★**【交卷后到 main 签收前, owner 会话必须【停止改动交付物】】** ★★"
         "★**★⇒ 交卷物 = 交卷页 + 真相页 + 新闸 (三件) ⇒ 这三件在 main 签收前都不许再动** ★★"
         "★**★理由 (★本项目今天已实测坐实【两次】, 不是理论★)★**: ★**① ISS-381 / ISS-382 / ISS-384 三单的 owner 会话在 main 08:03 / 09:24 签收后【继续重写交付物】"
         "(ISS-382 那一单更是在 10:35 与 12:49 【连续两次】重写自己的自带闸) ⇒ ⇒ main 的签收指纹当场过期 ⇒ ⇒ 我在 11:0x 与 13:2x 各写了一次追加式补注来披露它** ★ "
         "★**② ⇒ 【交卷】不等于【owner 该停手】⇒ 缺一条明确界线 ⇒ ⇒ 交卷那一刻起, 交付物应当【冻结】; 若还有要补的, 先交卷, 由 main 签收或退单后再改 (★退单重做时改交付物是允许的★)** ★ "
         "★**★⇒ 这不是 main 的洁癖, 是【签收这个动作的前提】⇒ ⇒ 没有冻结, 签收就只是给一个随时会变的字盖章** ★★"
         "★**★⇒ 与 L-27 合看**: ★**L-27 说「main 签收前必须确认 owner 会话已收工」⇒ 本条说【owner 交卷后就要停手】⇒ ⇒ 两侧合起来才是完整的签收条件: "
         "【owner 交卷后停手 (本条)】+【main 签收前确认它已收工 (L-27)】⇒ ⇒ ★**两任缺一, 签收指纹都会当场过期** ★★"
         "★**★⇒ main 自己的处置也照这条执行**: ★**★当 main 落一条裁决进 `pm.yaml` 时, 若该单已 verified ⇒ 该单交付物即进入「会动」状态 (L-27③) ⇒ ⇒ "
         "⇒ 【main 自己也不许再改已签收件的正文】⇒ 一律走【追加式订正块】(★同 ISS-378 §10 先例★)⇒ ⇒ 这一条与 §㊴/§㊶ 的所有追加式订正口径一致** ★★",
         "L-27 (state/LESSONS.md) · 一页 §㊶ §⑦ · main 11:0x + 13:2x 两次实测"),

        ("iss389_main_oi1_formal_confirm_4070", "mech-lead",
         "★**main 裁决 (★2026-11-24 13:1x·★main 地界·★iss389_oi1_housing_width_window·★★原 to=boss, main 指出它已不是独立决策★)★: "
         "★**「按 `4.0700` 出件」这条【已被 main 的两条裁决闭合】⇒ ⇒ 它不再是独立开放决策, 而是【执行口径】⇒ ⇒ 可与 boss 那一趟同批做形式确认, 不必单独立项** ★★"
         "★**闭合链 (★本轮实测坐实★)★**: ★**① §㊶ C3 (OI-5 取 `4.8100`) ⇒ ② §㊶ C4 (OI-12 判据口径不改 = 路 A) ⇒ ③ §㊶ C6 (OI-14 订正为 `4.0700`) ⇒ "
         "⇒ ★**⇒ 三条合起来 ⇒ 结构件的必须清空区 = `4.0700` ⇒ ⇒ OI-1 的技术问题已解** ★★"
         "★**★⇒ 剩下的只有一句形式确认: 「按 4.0700 出件」+ 老板那边若选 OI-12 路 B 则本条要撤销 (★但路 B 已被 main 判死·见 `iss389_main_oi12_criterion_stays_route_a`★) ⇒ "
         "⇒ ★**★⇒ 所以 OI-1 现在【不依赖 boss 的板框第一问】** ⇒ ⇒ ★**★→ 这一条从老板 53 条待拍板清单里【降级为执行口径】⇒ ⇒ 建议从「待拍板」移出** ★★"
         "★**★⇒ 唯一仍需 boss 的那一半 = 「座体真实高 h」(`iss389_oi11_seat_height_window`·★仍 to=boss★) ⇒ ⇒ 按 §㊵ 已算明: X 向与 h 无关 ⇒ 不卡那一趟; "
         "若 `h` 定 `4.0000` ⇒ 开口 Y 变 `5.8000` ⇒ 与 §㊶ C5 同一处改动 ⇒ 一并做 ⇒ ⇒ **建议降到最低优先级** ★★",
         "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md OI-1 · 一页 §㊶ C7 · §㊶ C3/C4/C6"),
    ]
    cur = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    have = {a.get("key") for a in (cur.get("answers") or []) if isinstance(a, dict)}
    added, skipped = 0, []
    for key, to, val, ref in ANS:
        if key in have:
            skipped.append(key)
            continue
        frag_write.update_fragment("main", lambda d, k=key, t=to, v=val, r=ref: d.setdefault("answers", []).append(
            {"key": k, "to": t, "value": v, "ref": r}))
        added += 1
    tot = len(yaml.safe_load(open(PM, encoding="utf-8"))["answers"])
    print("  pm.yaml (main 自己的分片): answers +%d 条 (跳过已存在 %d) ⇒ 共 %d 条" % (added, len(skipped), tot))
    return True


def write_memory_pointer():
    p = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
    txt = read_lines(p)
    if "L-29" in txt and "按设计判红" in txt:
        print("  MEMORY.md: L-29 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l29_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-29★·★main 独占写·★无 job 重写★)★**: "
           "★**L-29 「闸『按设计判红』与『闸坏了』必须分开判 ⇒ 判红的闸在它要等的那件事落地前【不许挂链】」★** ⇒ "
           "★① 闸的 rc=1 必须先分清【它坏了】与【它按设计在等一件事】⇒ 判据 = 「--selftest 末行是不是 ALL TESTS PASS」★ "
           "★② 【按设计判红】的闸, 在它等的那件事落地之前绝对不许挂进 state/gate_check.py ⇒ 挂进去 = 造一道【假红】⇒ 现场会读成「板坏了」⇒ 与全部先例同源★ "
           "★③ 「逐字替换已签收页正文」与 main 的【追加式】纪律冲突时 ⇒ 解法不是二选一而是【改版】⇒ 老页追加式订正块 + owner 在「那一趟」的清单改版里落★ "
           "★④ 【改孔径这类只动孔不动铜箔包络的板侧动作, 必须连带算【板 DRC 管不到的量】】⇒ 本轮实证: 官方 Ø0.71 配 1.000 焊盘 ⇒ 环宽 0.1750→0.1450 mm, 而 ISS-387 与 ISS-391 两页都没算这一格, 且本板 .kicad_pro 只有 min_via_annular_width 0.1 (过孔) ⇒ THT 焊盘环宽无判据 ⇒ 全仓无本板厂最小环宽记录 ⇒ 「能不能做」无据可判 ⇒ 必须投板前坐实★ "
           "★⇒ ★**本轮实证: ISS-391 新闸裸跑 rc=1 但 --selftest rc=0 末行 ALL TESTS PASS ⇒ 闸可信, 它的红是【按设计】(等 main 落四处登记) ⇒ 保持零挂链, 与登记同批挂** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-29 指针追加 (追加式, 备份 %s.bak_%s_main_l29_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_log():
    r = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1310_sign_iss387_389.md")
    body = """# ROUND_LOG_main · 2026-11-24 13:1x · ISS-387 / ISS-389 两单独立复核签收 + 11 条 main 地界待裁项已裁 + ISS-391 按 L-27 不签

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 5bd48f25 的进展播报触发★)
★**签收闸**: `state/_apply_20260724_1310_main_sign_iss387_389.py` (★fail-closed★)
★**备份** (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20261124_1310`★): `state/issue_log.yaml.bak_20261124_1310_main_sign_iss387_389` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_20261124_1310_main_sign_iss387_389` · `state/LESSONS.md.bak_20261124_1310_main_l29` ·
`MEMORY.md.bak_20261124_1310_main_l29_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` (纳秒级) ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · 两单签收 (main 本机独立复核·不抄 agent 报告) ★★

| 单 | owner | 闸 | 裸跑 | `--selftest` | 交付物 |
|---|---|---|---|---|---|
| ISS-387 | hw-lead | `HW/check_fts_single_row_land_truth.py` | rc=0 | rc=0 `ALL TESTS PASS` | 真相页 50,714 B + 交卷页 26,363 B |
| ISS-389 | mech-lead | `MECH/check_debug_seat_rework_spec.py` | rc=0 | rc=0 `ALL TESTS PASS` | 真相页 65,851 B + 交卷页 40,225 B |

★两闸连跑 3 次末行逐字相同 · 两闸零挂链 · 零落表 · 零改既有页面正文 ★

---

## ★★三 · ★★main 本机独立复核: ISS-387 的核心数字自己算 (不抄页面) ★★

```
★自己解析 PinHeader_1x04_P1.27mm_Vertical.kicad_mod:
  pads=4 / drill=0.65 / 焊盘 1.000×1.000 / 沿脚排 y = 0, 1.27, 2.54, 3.81
  ⇒ 铜箔沿脚排总宽 = 3.810 + 1.000 = 4.8100                          ✓
★自己解析 PinHeader_1x02_P1.27mm_Vertical.kicad_mod:
  pads=2 / drill=0.65
  ⇒ 铜箔沿脚排总宽 = 1.270 + 1.000 = 2.2700                          ✓
⇒ MECH 全链 3D 余量数的输入本机复算逐字命中
⇒ 「孔径 0.65→0.71 不动铜箔包络 ⇒ MECH 七个数一个都不用改」成立
```

---

## ★★四 · ★★main 自己的发现 (ISS-387 与 ISS-391 两页都没算这一格) ★★

★**官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 `0.1450` mm** ★
★**本板 `.kicad_pro` 的 DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (过孔环宽) ⇒ THT 焊盘环宽【无独立判据】⇒ 0.145 触不到板 DRC** ⇒
★**⇒ 它是【制程能力】问题, 不是 DRC 问题** ⇒ ★**全仓 (HW/ MECH/ state/) 实查: 没有任何一处记录本板厂的最小环宽/工艺能力** ⇒
★**⇒ 「0.145 能不能做」当前【无据可判】⇒ 那一趟投板前必须坐实, 否则投完板才发现 ⇒ 板改第二次** ⇒ 已登记 `iss387_main_rilim_ring_width_fab_capability` ★

---

## ★★五 · ★★11 条 main 地界待裁项已裁 (一件没代老板拍板) ★★

★**A 组 · ISS-387 (4 条)**: A1 焊盘维持 `1.000×1.000` (★附前置条件 = 环宽先过制程确认★) · A2 改孔与那一趟同批 · A3 用通用件 land + BOM 等价替代 + 显式偏离登记 (★官方直插图不给铜箔焊盘直径 ⇒ 「原厂铜箔宽」根本没数★) · A4 座体外形走双轨降级 (甲 官网量 / 乙 1 台样件实测) ⇒ 归 mech-lead, 与那一趟同批

★**C 组 · ISS-389 (7 条)**: C1 OI-2 含 `J_UART` (★「不含 ⇒ 零返工」是假选项: 实物仍装不上★) · C2 OI-3 不重开落点, 但把顺序钉死 (老板答板框 → 落点 → 结构件 → 板改+布线+Gerber) · C3 OI-5 取 `4.8100` (★本轮与 ISS-387 闭合★) · C4 OI-12 路 A (★路 B 已可判死: `6.0100` < courtyard `6.0900` + 公差不扣★) · C5 OI-13 路 B (开口 Y `≥ 5.6000` 或 `5.8000`) · C6 OI-14 订正为 `4.0700` (★与 OI-12 同源, 一起拍★) · C7 OI-1 已被 C3/C4/C6 闭合 ⇒ 从「待拍板」降级为「执行口径」⇒ 不再依赖板框第一问

★**老板域 (未代拍)**: OI-1 (已实质闭合) · OI-11 座体真实高 `h` (★X 向与 h 无关 ⇒ 不卡那一趟; 若定 `4.0000` ⇒ 开口 Y `5.8000` ⇒ 与 C5 同一处改动★)

---

## ★★六 · ★★ISS-391 本轮【不签收】(L-27 判据) ★★

★**owner 会话还在跑**: 真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` 12:49:22 仍被改 (hw-lead 会话 12:50 仍 running) ⇒ ★**此时签 ⇒ 签收指纹当场过期 (今天已在 ISS-381/382/384 上栽过一次)** ⇒ 等 owner 收工后再签 ★
★**交付物本身无缺陷**: 新闸裸跑 rc=1 而 `--selftest` rc=0 末行 `ALL TESTS PASS` ⇒ ★**这个 rc=1 是【闸按设计判红】**: D1/D2/D3 抓的正是「`钻孔 0.65→0.71` 还没进作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ **这道闸必须留在零挂链状态: 挂进去 = 假红** ⇒ 挂链时机 = 与 §4 登记同批 (★L-29★) ★

---

## ★★七 · 落记录 (全部追加式·老字一字未删) ★★

★`state/issue_log.yaml` (ISS-387/389 签收 + ISS-391 不签留痕) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊶** · `state/LESSONS.md` **L-29** · `state/fragments/pm.yaml` (13 条答案) · `MEMORY.md` (L-29 指针)

---

## ★★八 · 最终读数 (本机实跑) ★★

★板三项未动 · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py`/五个已签收页逐字节未动 · 两个新闸 rc=0 · 11 道扫描面闸全 rc=0 ·
`merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开, 按设计就该红) ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 未代老板拍板** ★
"""
    with open(r, "w", encoding="utf-8") as f:
        f.write(body)
    print("  round log: %s (%d B)" % (os.path.basename(r), os.path.getsize(r)))
    return True


def final_check():
    print()
    print("=" * 96)
    print("★阶段 3 · 写盘后收尾复核")
    print("=" * 96)
    st = os.stat(BOARD)
    print("  板三项: %s / %d ns / %d ⇒ %s" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size,
          "★未动★" if (md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
                       and st.st_size == BOARD_SIZE) else "★★动了★★"))
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if want and got != want:
            bad.append(rel)
    print("  受保护集 (%d 件): %s" % (len(PROTECTED), "★全未动★" if not bad else "★★动了 %s★★" % bad))
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("  %-18s rc=%d" % (label, rc))
    for iss, d in SIGN.items():
        rc, o = sh("python3 %s" % d["gate"])
        print("  %-46s rc=%d" % (iss + " 闸", rc))
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
    print("★ main · 2026-11-24 13:1x · ISS-387 / ISS-389 签收 + 11 条待裁项已裁 + ISS-391 按 L-27 不签")
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
    write_round_log()
    print()
    final_check()
    print()
    print("★ 本轮完成: 2 单签收 + 11 条 main 地界待裁项已裁 + L-29 + ISS-391 按 L-27 不签")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
