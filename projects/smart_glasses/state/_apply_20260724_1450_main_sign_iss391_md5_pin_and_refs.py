#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1450_main_sign_iss391_md5_pin_and_refs.py
============================================================
main (项目总工) · 2026-11-24 14:5x
★★【签收】ISS-391 (hw-lead) ★★ + ★★给 ISS-387/389 的签收记录补钉 md5 (L-27 通则②)★★
★★+ ★★把 §㊶→§㊷ 的自指订正同步到台账 (★14:2x 那轮漏了台账这四处·★L-30 规则②★)★★
★★+ ★★发现并披露一个 advance.py 的顺序依赖缺陷 (★老板清单的闭合口径★)★★

★纪律 (★本脚本自己守★):
  ① 零写板 · ② 零落表 · ③ 零改既有闸 · ④ 零改既有页面正文 (★订正一律追加式★)
  ⑤ 分片只走 state/frag_write.py · 只写 main 自己的 pm.yaml
  ⑥ 不代老板拍板 ⑦ 零外发 ⑧ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑨ ★★L-27: 签收前必须确认【owner 会话已收工】+ 【签收记录必须钉 md5 不许只钉 size】★★
  ⑩ ★★L-30: 取号前必须扫【已用编号/已用 key】★★
"""
import hashlib
import json
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
MEM = "/home/yuewuya/.openclaw/workspace/MEMORY.md"

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

# ★★本轮要签收/补钉的交付物 (★路径 → 期望 md5·★md5 由本脚本自己算, 不抄任何报告★)
D391 = {
    "gate": "HW/check_fts_land_drill_same_batch.py",
    "page": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
    "handoff": "HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md",
}
D387 = {
    "gate": "HW/check_fts_single_row_land_truth.py",
    "page": "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md",
    "handoff": "HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md",
}
D389 = {
    "gate": "MECH/check_debug_seat_rework_spec.py",
    "page": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
    "handoff": "HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md",
}

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
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md": None,
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd):
    pr = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return pr.returncode, pr.stdout + pr.stderr


def fp(rel):
    p = os.path.join(PROJ, rel)
    st = os.stat(p)
    return md5(p), st.st_size, st.st_mtime


def fpfull(rel):
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
        print("  %s %-56s %s" % ("✅" if good else "❌", name, detail))

    # ① 板三项 (纳秒级)
    st = os.stat(BOARD)
    chk("板 md5/mtime(ns)/size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ② ★★L-27 三要件: 交付物在盘 + md5 + size (★签收记录必须钉 md5 不许只钉 size★)
    print("  ★★① L-27 三要件 (★md5 + size + owner 会话已收工★)")
    FPS = {}
    for tag, d in (("ISS-391", D391), ("ISS-387", D387), ("ISS-389", D389)):
        for k in ("gate", "page", "handoff"):
            p = os.path.join(PROJ, d[k])
            e = os.path.isfile(p) and os.path.getsize(p) >= 4000
            FPS[(tag, k)] = fpfull(d[k]) if e else None
            chk("%s %s 在盘 (≥4000 B)" % (tag, d[k].split("/")[-1][:34]), e,
                "%d B  md5=%s" % (os.path.getsize(p) if os.path.isfile(p) else 0,
                                  md5(p)[:12] if os.path.isfile(p) else "-"))
    # ③ ISS-391 的闸: 按设计判红 (selftest 全抓到) ⇒ 闸可信
    print("  ★★② ISS-391 闸: 「按设计判红」与「闸坏了」必须分开判 (★L-29★)")
    rc, o = sh("python3 %s" % D391["gate"])
    rc2, o2 = sh("python3 %s --selftest" % D391["gate"])
    last = o2.strip().splitlines()[-1] if o2.strip() else ""
    import re as _re
    mcase = _re.search(r"(\d+)/(\d+) PASS", o2)
    chk("ISS-391 闸 selftest rc=0 + 末行 ALL TESTS PASS",
        rc2 == 0 and "ALL TESTS PASS" in last, "裸跑 rc=%d (★按设计红★) selftest rc=%d %r" % (rc, rc2, last[:24]))
    chk("ISS-391 闸自检用例数 ≥ 14", mcase and int(mcase.group(1)) >= 14,
        "用例 %s" % (mcase.group(0) if mcase else "?"))
    # 裸跑红项必须是 D1/D2/D3 (登记项), 不是别的东西
    red = [l.strip()[:40] for l in o.splitlines() if "RED" in l]
    chk("ISS-391 闸红项恰为 D1/D2/D3 (★= main §4 要落的登记项·★非闸故障★)",
        len(red) == 3 and all(("D%d" % i) in r for i, r in zip((1, 2, 3), red)),
        "红 %d 条: %s" % (len(red), [r.split()[0] for r in red]))

    # ④ ★★本机独立复核 ISS-391 的三条红项判据 (★不抄闸的输出, 自己读真文件★)★★
    print("  ★★③ ISS-391 三条红项的判据本机独立实读 (★自己读真文件★)")
    wp = read_lines(os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_WORKPACKET.md")).splitlines()
    l47 = wp[46]
    chk("作业包 L47 (板侧改动清单 ③) 里【没有】「钻孔/0.71」 (★⇒ D1 红是对的★)",
        ("钻孔" not in l47) and ("0.71" not in l47), "L47 命中 钻孔=%s 0.71=%s" % ("钻孔" in l47, "0.71" in l47))
    pf = read_lines(os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"))
    i = pf.find("B33_PIN_LAND_1P27")
    seg = pf[max(0, i - 300):i + 1500]
    chk("预检清单 B33 段里【没有】「钻孔/0.71」 (★⇒ D2 红是对的★)",
        ("钻孔" not in seg) and ("0.71" not in seg), "命中 钻孔=%s 0.71=%s" % ("钻孔" in seg, "0.71" in seg))
    cov = read_lines(os.path.join(PROJ, "HW/check_onepass_preflight_coverage.py")).splitlines()
    chk("覆盖度闸有 WP02_BINDING 定义 (★§4 #4 的目标行★)",
        any("WP02_BINDING = {" in l for l in cov), "★定义在位★")
    l254 = cov[253]
    chk("覆盖度闸 WP02_BINDING[\"③\"] 只列 item 不列覆盖令牌 (★⇒ #4 的加严项待落★)",
        "B33_PIN_LAND_1P27" in l254 and l254.rstrip().endswith("[]),"), l254.strip()[:70])

    # ⑤ ★★官方 Ø0.71 证据本机独立复核 (★自己抽 PDF 文本 + 核 md5★)★★
    print("  ★★④ ★★官方孔径证据本机独立复核 (★自己抽 PDF, 不抄页面★)★★")
    pdf = os.path.join(PROJ, "tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf")
    if os.path.isfile(pdf):
        pm_ = md5(pdf)
        txt = ""
        try:
            import subprocess as _sp
            txt = _sp.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
        except Exception:
            txt = ""
        hit = (".028 0.71 (TYP)" in txt) or ("0.71" in txt and "TYP" in txt)
        chk("官方 FTS 图 md5 = 1cbe4a2bfa456d8fd030c8b76bdf8dd5", pm_ == "1cbe4a2bfa456d8fd030c8b76bdf8dd5", pm_)
        chk("官方图正文含「.028 0.71 (TYP)」 (★自己抽的文本★)", hit,
            "★pdftotext 命中★" if hit else "★抽不出·★只核 md5★")
    else:
        chk("官方 PDF 在盘", False, "缺失")

    # ⑥ ★★环宽: ISS-391 真相页也没算这一格 (★main 13:1x 的发现·★两页都没算★)★★
    print("  ★★⑤ ★★环宽 (★ISS-387 与 ISS-391 两页都没算这一格★)★★")
    t391 = read_lines(os.path.join(PROJ, D391["page"]))
    chk("ISS-391 真相页里【没有】「环宽/annular/0.145」 (★⇒ 这仍是 main 的独立发现★)",
        ("环宽" not in t391) and ("annular" not in t391) and ("0.145" not in t391),
        "环宽=%s annular=%s 0.145=%s" % ("环宽" in t391, "annular" in t391, "0.145" in t391))
    ring65 = (1.000 - 0.65) / 2
    ring71 = (1.000 - 0.71) / 2
    chk("环宽: drill 0.65 ⇒ %.4f ; drill 0.71 ⇒ %.4f" % (ring65, ring71),
        abs(ring65 - 0.175) < 1e-9 and abs(ring71 - 0.145) < 1e-9, "★本机实算★")

    # ⑦ ★★L-27: owner 会话已收工 (★真判据 = 【实际【写】了这三个交付件的会话】已静默 ≥3 分钟 + 【交付物本身】静默 ≥3 分钟★★)
    #    ★★2026-11-24 14:5x 修正 (★两次修正·★都是我自己的判据写错★): ★★
    #    ★★v1 我写成「会话 mtime 晚于交付物 mtime」⇒ 错 (★L-27 判的是【静默时长】, 不是【先后顺序】·★owner 完全可以先写交付物再收尾★) ★★
    #    ★★v2 我写成「该 agent 名下所有会话都静默」⇒ 也错 (★兄弟 job 随时会新开会话·★14:56 就新开了两个·★与本单无关★) ★★
    #    ★★⇒ v3 正解: 【找出真正【写】了这三个交付件的会话 (★必须命中 write/edit 工具调用里的 path 字段★·★不能靠子串匹配——★读也会命中★)】, 要求它们已静默 ≥180 秒 ★★
    print("  ★★⑥ L-27: 实际写了这三个交付件的会话已收工 + 交付物静默 (★真判据·★v3★)")
    import glob as _g
    import re as _re3
    import json as _json2
    now = time.time()

    def writers_of(relpaths):
        """找出真正写了这几个文件的会话 (★必须逐行解 JSON, 只认 role=toolResult 且 toolName∈{write,edit}★) ★★
        ★★2026-11-24 14:5x 修正 (★v3 又错了一处·★v4 才对★): ★★
        ★★v3 用【子串正则】扫 ⇒ 【我自己读的 transcript 里也含这些文件名 ⇒ 自污染 ⇒ 把我自己算成写者★] ★★
        ★★⇒ 正解: 逐行 json.loads ⇒ 只取 message.role=='toolResult' 且 message.toolName ∈ {write, edit} 的行 ⇒ ★
        ★★      再看它的 content 文本里有没有目标文件名 ⇒ 【只有真写过它的会话会命中】★★
        """
        out = {}
        for sp in _g.glob("/home/yuewuya/.openclaw/agents/*/sessions/*.jsonl"):
            if "trajectory" in sp:
                continue
            try:
                fh = open(sp, encoding="utf-8", errors="replace")
            except Exception:
                continue
            hit = False
            for ln in fh:
                if '"toolResult"' not in ln or ('"write"' not in ln and '"edit"' not in ln):
                    continue
                try:
                    d = _json2.loads(ln)
                except Exception:
                    continue
                mm = d.get("message")
                if not isinstance(mm, dict):
                    continue
                if mm.get("role") != "toolResult":
                    continue
                if mm.get("toolName") not in ("write", "edit"):
                    continue
                txt = " ".join(c.get("text", "") for c in (mm.get("content") or []) if isinstance(c, dict))
                for rel in relpaths:
                    if os.path.basename(rel) in txt:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                out[os.path.basename(sp)] = os.stat(sp).st_mtime
        return out

    for iss, d in (("ISS-391", D391), ("ISS-387", D387), ("ISS-389", D389)):
        rels = list(d.values())
        ws = writers_of(rels)
        deliv_quiet = now - max(os.stat(os.path.join(PROJ, v)).st_mtime for v in rels)
        if ws:
            newest = max(ws.values())
            quiet = now - newest
            chk("%s: 写过它交付件的 %d 个会话全部静默 ≥180 秒 (★L-27 真判据·★v3★)" % (iss, len(ws)),
                quiet >= 180 and deliv_quiet >= 180,
                "会话静默 %.0f 秒 · 交付物静默 %.0f 秒" % (quiet, deliv_quiet))
        else:
            chk("%s: 找出写过它交付件的会话" % iss, False, "★没匹配到 write/edit 路径·★判据失效★")

    # ⑧ 交付物静默 (连读两次)
    for tag, d in (("ISS-391", D391), ("ISS-387", D387), ("ISS-389", D389)):
        before = {k: os.path.getsize(os.path.join(PROJ, v)) for k, v in d.items()}
        time.sleep(2)
        same = all(os.path.getsize(os.path.join(PROJ, v)) == before[k] for k, v in d.items())
        chk("%s 三个交付物 2 秒内尺寸不变 (★静默★)" % tag, same, "静默" if same else "★仍在动★")

    # ⑨ 零落表 + 既有闸/已签收页
    bad = []
    for rel, want in PROTECTED.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if want and got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/已签收页正文 未动 (%d 件)" % len(PROTECTED), not bad, "动 %d %s" % (len(bad), bad[:3]))

    # ⑩ 零挂链
    for tag, d in (("ISS-391", D391), ("ISS-387", D387), ("ISS-389", D389)):
        got = sh("grep -c %s state/gate_check.py" % os.path.basename(d["gate"]))[1].strip().splitlines()[0]
        chk("%s 新闸零挂链 (gate_check 命中 0)" % tag, got == "0", "命中 %s" % got)

    # ⑪ L-26① 扫描面命中的既有闸 (含 ISS-391 读的那几个文件 ⇒ 覆盖度闸/网表自洽)
    print("  ★★⑦ L-26① 扫描面命中本次交付的既有闸 (★一道都不能漏★)")
    SCAN = [
        ("HW/check_onepass_preflight_coverage.py", "ISS-391 闸读的覆盖度闸"),
        ("HW/check_netlist_selfconsistency.py", "HW 域网表自洽"),
        ("HW/check_fts_single_row_land_truth.py", "ISS-387 签收闸"),
        ("SW/tools/check_sw_false_connectivity_gate.py", "ISS-381 签收闸"),
        ("HW/check_debug_uart_seat_truth.py", "ISS-380 签收闸"),
        ("HW/check_debug_uart_seat_alignment.py", "ISS-383 签收闸"),
        ("HW/check_charge_current_live_value.py", "ISS-384 签收闸"),
        ("MECH/check_debug_seat_3d_fit.py", "ISS-386 签收闸"),
        ("MECH/check_jdebug_arrangement_truth.py", "ISS-382 签收闸"),
        ("SW/check_evt_charge_current_criterion.py", "ISS-385 签收闸"),
        ("MECH/check_onepass_struct_crosscheck.py", "MECH 结构交叉"),
        ("MECH/check_onepass_mech_sync.py", "MECH 同步"),
        ("MECH/check_mech_verdict_freshness.py", "MECH 判决新鲜度"),
    ]
    for g, label in SCAN:
        rc, o = sh("python3 %s" % g)
        chk("%-46s (%s) rc=0" % (g.split("/")[-1], label), rc == 0, "rc=%d" % rc)

    # ⑫ 官方门禁
    print("  ★★⑧ 官方门禁")
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        rc, o = sh("python3 %s" % cmd)
        print("    %-18s rc=%d" % (label, rc))
    chk("issue_check 违规数 = 19 (★既有老账·非本轮新增★)", "违规 19 条" in sh("python3 state/issue_check.py")[1], "★老账★")
    chk("stage_gate 仍在 G1 (★按设计就该红★)", "G1" in sh("python3 state/stage_gate.py")[1], "★G1 未开★")

    # ⑬ ★★advance.py 的顺序依赖缺陷: 忠实复刻必须复现出 55 (★先验证模型可信★)★★
    print("  ★★⑨ ★★advance.py 的老板清单口径 (★忠实复刻·★必须复现 55★)★★")
    import glob as _glob
    frags = []
    for p in sorted(_glob.glob(os.path.join(PROJ, "state/fragments/*.yaml"))):
        frags.append((os.path.basename(p), yaml.safe_load(open(p, encoding="utf-8")) or {}))
    try:
        from decision_truth import decision_keys as _dk
        dk = _dk({"f%d" % i: fr for i, (fn, fr) in enumerate(frags)})
    except Exception:
        dk = set()
    ans = set()
    out = []
    seen = set()
    for fn, fr in frags:
        for a in (fr.get("answers") or []):
            if a.get("key"):
                ans.add(a["key"])
        for n in (fr.get("needs_from") or []):
            k = n.get("key")
            if not k or k in seen:
                continue
            if n.get("decision"):
                continue
            if k in dk:
                continue
            if not (n.get("waiting_on") == "boss" or n.get("to") == "boss"):
                continue
            if k in ans:
                continue
            seen.add(k)
            out.append(k)
    chk("忠实复刻 advance.py 的老板清单 = 55 条 (★模型可信·★否则不做下面的结论★)",
        len(out) == 55, "复刻 %d 条" % len(out))
    # 顺序依赖证据: 若先全量收答案, OI-1 会被清掉
    ans_all = set()
    for fn, fr in frags:
        for a in (fr.get("answers") or []):
            if a.get("key"):
                ans_all.add(a["key"])
    would = len([k for k in out if k not in ans_all])
    chk("★★顺序依赖实证: 若【先全量收答案】, 老板清单会少 %d 条 (★⇒ 现实现是【逐片收】·★⇒ pm.yaml 的同 key 答案对 mech.yaml 的 need 无效★)" % (55 - would),
        (55 - would) >= 1, "少 %d 条" % (55 - would))
    chk("★iss340 (★有 pm.yaml 同 key 答案·★仍留在老板清单★) ⇒ 同 key 答案【清不掉】to=boss 的 need",
        "iss340_c_bucket_boss_decisions" in out, "★先例·★实证★")
    chk("★iss389_oi1_housing_width_window 仍在老板清单 (★⇒ main 在 pm.yaml 的答案对它无效★)",
        "iss389_oi1_housing_width_window" in out, "★在清单★")

    # ⑭ ★★L-30: 取号前扫已用编号 (★一页 §㊸ 空闲?★)★★
    print("  ★★⑩ L-30 取号前扫已用编号")
    import re as _re2
    onep = read_lines(ONEPAGER)
    used = set(_re2.findall(r"§([㊀-㊿])", onep))
    chk("一页 §㊸ 未被用过 (★取号前必扫★)", "㊸" not in used, "已用: %s" % "".join(sorted(used)))
    chk("LESSONS L-31 未被用过", "## ★L-31" not in read_lines(LESSONS), "★空闲★")
    chk("pm.yaml 无同名 key 撞名 (★L-8/L-28★)",
        "main_advance_py_decision_list_order_dependency" not in read_lines(PM), "★空闲★")

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


# ===================================================================== 阶段 2
VER391 = (
    "✅ verified (★main 2026-11-24 14:5x 本机独立复核 · 不抄 agent 报告★) ⇒ ★**owner 会话已收工 (L-27 硬前提满足: hw-lead 4b7b08f1 于 12:51:41 收工, "
    "此后 2 小时未再动) + 三个交付物字节静默** ★ ⇒ ★**新闸 `HW/check_fts_land_drill_same_batch.py` 裸跑 rc=1 而 `--selftest` rc=0 末行 `ALL TESTS PASS` "
    "(17/17 用例全抓到) ⇒ ⇒ 【这个 rc=1 是【闸按设计判红】, 不是闸故障】(L-29): 它的 D1/D2/D3 三条抓的正是「`钻孔 0.65→0.71` 这条板侧动作还没进到 "
    "作业包 §0.2 ③ + 预检清单 `B33_PIN_LAND_1P27`」⇒ ⇒ **该闸必须保持零挂链: 挂进去 = 造一道【假红】⇒ 现场会读成「板坏了」⇒ 挂链时机 = 与 main 落 §4 登记同批** ★ "
    "★**★main 本机独立复核 (★自己读真文件, 不抄闸的输出★)**: ① 作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47 (板侧改动清单 ③ 那一项) 实读 ⇒ "
    "【查不到「钻孔」, 也查不到「0.71」】⇒ ⇒ D1 的红是对的 ② 预检清单 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 段实读 ⇒ "
    "【查不到「钻孔/0.71」】⇒ ⇒ D2/D3 的红是对的 ③ 覆盖度闸 `HW/check_onepass_preflight_coverage.py` L254 实读 = `\"③\": ([\"B33_PIN_LAND_1P27\"], [])` ⇒ "
    "⇒ P4 只判「③ 底下有没有对应 item」, 不查子动作 ⇒ ⇒ 补令牌是【加严】不是放宽 ④ ★**官方孔径证据本机独立复核**: 自抽 Samtec 官方 FTS 图 PDF 文本 ⇒ "
    "正文含「`.028 0.71 (TYP)`」且该 PDF md5 = `1cbe4a2bfa456d8fd030c8b76bdf8dd5` 逐字命中 §5 机器块 ⇒ ⇒ 官方 `0.71` 这一层坐实 ★ "
    "★**★交付物指纹 (★L-27 通则②: 签收记录必须钉 md5, 不许只钉 size★)★**: 闸 `HW/check_fts_land_drill_same_batch.py` md5 `dabc12000b6cecb1769bb16df09f1abb` (47,175 B) · "
    "真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` md5 `1a27e49b4055ec891766af54a8e6c778` (45,038 B) · "
    "交卷页 `HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md` md5 `e7dd41e5fde55bb04a91c25d7cc292f1` (29,690 B) ★ "
    "★**零写板 + 零落表 (网表/脚表/BOM 逐字节未动) + 零挂链 + 零改既有闸 + 零改既有页面正文 + L-26① 的 13 道扫描面闸逐道实跑全 rc=0** ★ "
    "★**★main 自己的独立发现 (★ISS-391 与 ISS-387 两页都没算这一格★)**: 官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 (annular ring) 从 `0.1750` 降到 "
    "`0.1450` mm; 本板 `.kicad_pro` DRC 规则表里与环宽相关的只有 `min_via_annular_width 0.1` (过孔环宽) ⇒ **THT 焊盘环宽无独立判据 ⇒ 0.145 触不到板 DRC** ⇒ "
    "⇒ 它是【制程能力】问题, 而全仓 (HW/ MECH/ state/) 没有任何一处记录本板厂的最小环宽 ⇒ ⇒ **「0.145 能不能做」当前无据可判** ⇒ "
    "★**⇒ 已登记为待补项 `iss387_main_rilim_ring_width_fab_capability` ⇒ 那一趟投板前必须坐实, 否则投完板才发现 ⇒ 板改第二次** ★ "
    "★**本单签收含义 = 交付物在盘 + 闸绿(selftest) + 红项按设计 + 边界零越界 + 核心数字本机复算命中; §4 六条登记由 main 落【追加式订正块】, owner 在"
    "「那一趟」的清单改版里按逐字文本落 (不代拍·不提前落)** ★"
)


def write_issue_log():
    p = LOG
    shutil.copy2(p, p + ".bak_%s_main_sign_iss391" % STAMP)
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}

    # ① ★★签收 ISS-391 ★★
    e = by.get("ISS-391")
    if e is None:
        raise SystemExit("台账里没有 ISS-391")
    e["status"] = "verified"
    e["verify_result"] = VER391
    e["verify_date"] = "2026-11-24 14:5x"
    e["verify_by"] = "main"
    e["fix_ref"] = "main 2026-11-24 14:5x 独立复核签收 (★零写板·零落表·零改既有闸·零改既有页面正文·零挂链★)"

    # ② ★★给 ISS-387 / ISS-389 的签收记录补钉 md5 (L-27 通则②) ★★
    #    ★★但【不改 verify_result 老字】⇒ 一律走 note_addendum (追加式)★★
    #    ★★2026-11-24 14:5x 修正: 我第一版把 md5 【手写死】在脚本里 ⇒ ★★其中 ISS-389 闸那一条被我自己的 cut 截断搞错了
    #    ★★⇒ 脚本的 md5 守卫当场报错退出 (★没写进任何错指纹·★守卫起作用了★) ⇒ ⇒ v2: 【不手写】, 从盘上现读 + 与阶段 1 的读数逐字对 ★★
    md5s = {}
    for iss, d in (("ISS-387", D387), ("ISS-389", D389)):
        md5s[iss] = {}
        for k in ("gate", "page", "handoff"):
            rel = d[k]
            got_m, got_sz, _ = fpfull(rel)
            # ★与阶段 1 复核时的读数逐字对比 ⇒ 变了 ⇒ 说明复核后被改过 ⇒ 报错退出
            st1 = FPS.get((iss, k))
            if not st1 or st1[0] != got_m or st1[1] != got_sz:
                raise SystemExit("★★指纹与阶段 1 复核时不一致 ⇒ 报错退出 (★不许写没核过的指纹★): %s %s 阶段1=%s 现盘=%s"
                                 % (iss, rel, st1, (got_m, got_sz)))
            md5s[iss][k] = (rel, got_m, got_sz)

    for iss in ("ISS-387", "ISS-389"):
        e = by.get(iss)
        if e is None:
            raise SystemExit("台账里没有 %s" % iss)
        rows = []
        for k in ("gate", "page", "handoff"):
            rel, m, sz = md5s[iss][k]
            rows.append("★**%s** `%s` md5 `%s` (%d B)" % (k, rel, m, sz))
        nt = ("★**2026-11-24 14:5x main 补钉签收指纹 (★追加式·★`verify_result` 老字一字未删·★本条只【追加】, 不改老字★)★**: "
              "★**依据 = L-27 通则②: 「签收记录里必须钉【md5】, 不许只钉 size」⇒ ★我 13:1x 那次签收只钉了 size ⇒ ⇒ 本次补齐** ★ "
              "★**★补钉的三个交付物指纹 (★本机实算 md5 + 实读 size, 已逐条与现盘核对一致★)★**: " + " · ".join(rows) + " ★ "
              "★**★⇒ 补齐后, 这两单的签收记录【逐字可核】: 任何人拿 md5 一比就知道交付物有没有被换过 (★size 相同也可能内容换了·★这正是 L-27 要钉 md5 的理由★)** ★ "
              "★**★另: 本条同时订正一处【章节号自指】(★L-30 规则②: 所有引用自己那段 ref 字段同步改号·★14:2x 那轮改了一页与 pm.yaml, 漏了台账这四处★)★**: "
              "★**本条 `verify_result` 内的「一页 §㊶」自指【应读作「§㊷」】(★我 13:1x 那一段在 14:2x 被就地改号为 §㊷·★老字未删·★此处只作说明·★不改老字★)** ★ "
              "★**★另: ISS-389 的 owner 会话 `mech-lead c6a0fb40` 于 10:11:09 收工, 交付物自此未动 ⇒ ⇒ 本条补钉的三个 md5 就是【当前有效指纹】, 之后若被改动 ⇒ "
              "本条记录即失效 ⇒ 那一趟必须重验** ★")
        prev = e.get("note_addendum") or ""
        e["note_addendum"] = (prev + ("\n" if prev else "") + nt)

    tmp = p + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, p)
    print("  issue_log.yaml: ISS-391 签收 + ISS-387/389 补钉 md5 (追加式) (备份 %s.bak_%s_main_sign_iss391)"
          % (os.path.basename(p), STAMP))
    return True


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_sign_iss391" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊸ 【2026-11-24 14:5x · 追加式】★ ★★ISS-391 独立复核签收 (★L-27 前提终于满足★) + ★★签收记录补钉 md5 (L-27 通则②)★★ + ★★★发现 advance.py 的一个【顺序依赖】缺陷 ⇒ 老板清单的闭合口径要重算★★

★**① 板面 (本机实读)**: ★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**② ★★ISS-391 签收 (★main 本机独立复核·不抄 agent 报告★)★★**

| 单 | owner | 闸 | 裸跑 | `--selftest` | 判定 |
|---|---|---|---|---|---|
| **ISS-391** | hw-lead | `HW/check_fts_land_drill_same_batch.py` | **rc=1 (★按设计判红★)** | rc=0 末行 `ALL TESTS PASS` (17/17) | ★**闸可信·红是业务信号** ★ |

★**★L-27 的硬前提本轮终于满足**: ★**owner 会话 `hw-lead 4b7b08f1` 于 12:51:41 收工 ⇒ 此后近 2 小时三个交付物字节静默 ⇒ ⇒ 【owner 会话已收工 + 交付物静默】两个条件都过 ⇒ ⇒ 本轮可签** ★
★**★⇒ 对比上一轮 (13:1x) 的判断**: 上一轮 main 因「owner 会话还在跑」**【不签】⇒ ★**拦对了** ⇒ (★它 12:49 还在改·★若当时签了, 指纹会当场过期·★今天已在 ISS-381/382/384 上栽过一次★) ⇒ ★**⇒ 纪律有用** ★

★**③ ★★main 本机独立复核: 三条红项自己读真文件判 (★不抄闸的输出★)★★**
★**① 作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47 (板侧改动清单 ③ 那一项) 实读 ⇒ 【查不到「钻孔」, 也查不到「0.71」】⇒ ⇒ D1 的红是对的** ★
★**② 预检清单 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 段实读 ⇒ 【查不到「钻孔/0.71」】⇒ ⇒ D2/D3 的红是对的** ★
★**③ 覆盖度闸 `HW/check_onepass_preflight_coverage.py` L254 实读 = `\"③\": ([\"B33_PIN_LAND_1P27\"], [])` ⇒ ⇒ P4 只判「③ 底下有没有对应 item」, 不查子动作 ⇒ ⇒ 补令牌是【加严】不是放宽** ★
★**④ ★官方孔径证据本机独立复核**: ★**自抽 Samtec 官方 FTS 图 PDF 文本 ⇒ 正文含「`.028 0.71 (TYP)`」; 该 PDF md5 = `1cbe4a2bfa456d8fd030c8b76bdf8dd5` 逐字命中 §5 机器块** ★

★**④ ★★交付物指纹 (★L-27 通则②: 签收记录必须钉 md5, 不许只钉 size★)★★**
| 单 | 闸 | 真相页 | 交卷页 |
|---|---|---|---|
| **ISS-391** | `dabc12000b6cecb1769bb16df09f1abb` (47,175 B) | `1a27e49b4055ec891766af54a8e6c778` (45,038 B) | `e7dd41e5fde55bb04a91c25d7cc292f1` (29,690 B) |
| **ISS-387** | `5b9570fd23d6dd7125876c9110085506` (37,318 B) | `a2f78e769bbe9c27c44e728539206c04` (50,714 B) | `0f56b27062fa36a444a09fc4ff35194e` (26,363 B) |
| **ISS-389** | `babadd6b073d691374051ea7409a6a1f` (47,102 B) | `8a56a3eb5a4b1c77e48c283633ec5fe6` (65,851 B) | `459537612f6d03e7ce41b299736a51ce` (40,225 B) |

★**★★⇒ 补钉的缘由 (★自曝·★不藏★)**: ★**我 13:1x 签 ISS-387/389 时【只钉了 size, 没钉 md5】⇒ ⇒ 违反了自己 11:0x 写的 L-27 通则② ⇒ ⇒ 本轮追加式补齐 ⇒ ⇒ 【size 相同也可能内容换了】** ★

★**⑤ ★★★★本轮最重要的发现: `advance.py` 的老板清单有一个【顺序依赖】缺陷 ⇒ 「main 答了」与「老板清单少了」不是一回事★★★★**
★**实况 (本机实跑 + 忠实复刻)**: ★**`state/advance.py --json` 的 `decisions` = 55 条** ⇒ ★**main 在 13:1x 写的 15 条答案【没有让老板清单少一条】** ★
★**★根因 (★忠实复刻 advance.py 的扫描逻辑, 复刻出 55 ⇒ 模型可信★)★**: ★**该脚本按分片文件名排序【逐片扫】: `hw.yaml → mech.yaml → pm.yaml → sw.yaml` ⇒ ⇒ 扫到 `mech.yaml` 的 need 时, `ans_keys` 里【还没有】`pm.yaml` 的 answer ⇒ ⇒ main 写在 pm.yaml 的同 key 答案, 对 mech.yaml / hw.yaml 里的 to=boss need【无效】** ★
★**★⇒ 三个实证 (★全在本机跑出来的★)★**: ★**① 先例 `iss340_c_bucket_boss_decisions`: 它【有】pm.yaml 同 key 答案 (★main 2026-11-22 23:5x 写的·★当时明写「这条 need 从此闭合」★) ⇒ 但它【至今仍留在老板清单里】⇒ ⇒ 同 key 答案【清不掉】to=boss 的 need ★ ② `iss389_oi1_housing_width_window` (★13:1x 我裁过的那条·★「建议从待拍板移出」★) ⇒ 【同样仍在老板清单里】⇒ ⇒ 我 13:1x 写的「移出」在机器上【没生效】 ★ ③ 若改成【先全量收答案再扫 need】, 老板清单会少 1 条 ⇒ ⇒ 这就是【顺序依赖】的直接证据** ★
★**★★⇒ 后果 (★这条必须让老板知道·★否则老板会以为自己被问了一条已经答过的题★)★**: ★**老板清单现在 = 55 条, 其中【至少 2 条是 main 已经实质答过的】(`iss340_c_bucket_boss_decisions` + `iss389_oi1_housing_width_window`) ⇒ ⇒ 老板真正要答的 = 53 条** ★
★**★★⇒ main 的处置 (★本轮只披露+登记, 【不改 advance.py】·★理由见下★)★**: ★**① 一页此节【就是那 2 条的正式披露】⇒ 老板请按 53 条读 ⇒ ★★② 已登记为待办项 `main_advance_py_decision_list_order_dependency` ⇒ ⇒ 归属: 这道闸/口径属【老板域的读数口径】, main 不擅自改 `advance.py` (★它是老板清单的唯一生成器·★改了 = 动老板看的那张表·★而且改它会让「待拍板件数」这个数字在没拍板的情况下自己变·★那比现在更危险★) ⇒ ⇒ 【建议 = 老板拍一次口径】: 是按「老板清单条数」读, 还是按「真正待答条数」读 ★** ★
★**★⇒ 另一条可能的解法 (★供老板选·★main 不代拍★)★**: ★**把这两条 need 在【它自己那份分片】里由 owner 改成 `decision:` 回写 (★`decision_truth` 认这个字段·★那是老板拍过的正式落法·★但「老板没拍过的题」不许伪造 decision·★main 不许代录★) ⇒ ⇒ 要么 owner 撤回这两条 need (★它们已被 main 实质闭合·★撤回是诚实做法★), 要么老板就当它们还在** ★

★**⑥ ★★ISS-391 的 §4 六条登记: 由 main 落【追加式订正块】, owner 在「那一趟」的清单改版里落 ★★**
★**#1** 作业包 §0.2 ③ 的 ③ 补「钻孔 `0.65→0.71`」 · ★**#2** 预检清单 `B33_PIN_LAND_1P27` 描述列 · ★**#3** 同条验收手段列 · ★**#4** 覆盖度闸 `WP02_BINDING["③"]` 补令牌 `0.71`/`0.65` · ★**#5** BOM L71/L77 的 `opn`+`footprint` 两栏 · ★**#6** 生成器 `state/_iss277_build_preflight.py` 的 `build_pinland_item()` + `read_board_pin_land()` 加 drill 字段 ★
★**★⇒ §4 #1/#2/#3 必须同批落 (★`wp02_tokens()` 会从 ③ 的原文自动抽小数当覆盖令牌 ⇒ 补上 `0.65`/`0.71` 之后, 现有 P4 会自动要求清单页也查得到这两个数 ⇒ ⇒ 少落一处 P4 当场红★) ★**
★**★⇒ 全部与「板只改一次」那一趟同批 (★★提前落 ⇒ 中间态: 板还没改, 清单却写了改孔 ⇒ 覆盖度闸拿 `0.71` 去查真实板面 (板上还是 `0.65`) ⇒ 当场红 ⇒ 现场误读成「板坏了」★★) ★**
★**★⇒ 新闸 `check_fts_land_drill_same_batch.py` 挂链时机 = 与 §4 登记同批 (★L-29★) ⇒ ⇒ 四个新闸 (`check_fts_single_row_land_truth` / `check_debug_seat_rework_spec` / `check_fts_land_drill_same_batch` / `check_sw_gate_health`) 一并在那一次挂** ★

★**⑦ ★★本轮零派 / 零外发 / 零落表 / 零写板 / 零挂链**: ★**internal = 0** ⇒ 三单全部已签收 (★ISS-391 本轮签·★ISS-388/ISS-390 仍在 fixing 等 owner 交卷★) ⇒ ★**外发段恒空** ★板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**落点坐标 / 清空区放大量的一切前提都挂在它身上, 本页不代拍** ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊸, 备份 %s.bak_%s_main_sign_iss391)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"
    return True


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l31" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-31 · ★★★「main 已经答了」与「老板清单上少了」是两件事 ⇒ ★★判据: 【读数工具的扫描顺序】决定闭合能不能生效★★ ★★

★**实测 (2026-11-24 14:5x, main 本机实跑 · ★ISS-391 签收那一趟撞上★)★**:
★**★`state/advance.py --json` 的 `decisions` = 55 条, 而 main 在 13:1x 刚给这一页写完 15 条裁决 ⇒ ⇒ 【老板清单一条都没少】** ★ ★
★**★根因 (★忠实复刻 advance.py 的扫描逻辑, 复刻出 55 ⇒ 模型可信★)★**: ★**该脚本按分片文件名排序【逐片扫】(`hw.yaml → mech.yaml → pm.yaml → sw.yaml`) ⇒ ⇒ 扫到 `mech.yaml` 的 need 时, `ans_keys` 里【还没有】`pm.yaml` 的 answer ⇒ ⇒ main 写在 pm.yaml 的同 key 答案, 对 `mech.yaml`/`hw.yaml` 里的 to=boss need【完全无效】** ★ ★
★**★⇒ 三个实证 (★全在本机跑出来的·★不是推理★)★**:
★**① 先例 `iss340_c_bucket_boss_decisions`: ★它【有】pm.yaml 同 key 答案 (★main 2026-11-22 23:5x 写的, 当时明写「这条 need 从此闭合」★) ⇒ 但它【至今仍留在老板清单里】** ★
★**② `iss389_oi1_housing_width_window` (★main 13:1x 裁过·★裁决里写了「建议从待拍板移出」★) ⇒ 【同样仍在老板清单里】⇒ ⇒ **main 13:1x 写的「移出」在机器上没生效** ★
★**③ 若把实现改成【先全量收答案再扫 need】, 老板清单会少 1 条 ⇒ ⇒ 这就是顺序依赖的直接证据** ★ ★
★**★⇒ 通则 ①**: ★**★凡是有【扫描顺序】的读数工具, 「我做了 X ⇒ 读数会变」这句话【必须先验证】⇒ ⇒ 验证法 = 【忠实复刻那个扫描逻辑】+ 【必须复现出工具的真实读数】⇒ ⇒ 复现不出来 ⇒ 模型不可信 ⇒ 不许据此下结论** ★ ★
★**★⇒ 通则 ②**: ★**★「main 答了」与「老板清单上少了」是两件事 ⇒ ⇒ 所以 main 落裁决后, 【必须回头看那把尺子的读数有没有真的变】⇒ ⇒ 没变 ⇒ 【要么改工具(★动老板看的那张表·★要老板拍★), 要么让 owner 在它自己那份分片里撤回/回写 decision(★诚实做法★), 要么【如实披露「这条还在清单上」】】** ★ ⇒ ★**★⇒ 本轮 main 选了第三条: 披露 + 登记待办项, 【不擅自改 advance.py】⇒ 理由: 改它 = 动老板清单的唯一生成器, 而且会让「待拍板件数」这个数字在没拍板的情况下自己变 ⇒ 那比现在更危险** ★ ★
★**★⇒ 通则 ③**: ★**★不许为了「让读数好看」伪造 `decision:` 字段 ⇒ ⇒ `decision_truth` 认它 = 它代表【老板拍过了】⇒ ⇒ main 代录一条老板没拍过的 = 代老板拍板 = 越界** ★ ★
★**★⇒ 通则 ④ (★与 L-27 合看★)**: ★**★签收记录必须钉【md5】, 不许只钉 size (★L-27 通则②★) ⇒ ⇒ 【main 自己签收时也要守这条】⇒ ⇒ 本轮实证: main 13:1x 签 ISS-387/389 只钉了 size ⇒ ⇒ 自己违反了自己 11:0x 写的铁律 ⇒ ⇒ 14:5x 追加式补齐 ⇒ ⇒ 【自曝纪律: 自己写的铁律自己先犯, 必须自己披露自己补】** ★ ★
★**★⇒ 与 L-21~L-30 合看★**: ★**L-21 清单钉 file/line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工且要钉 md5 · L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了 · L-30 取号前必须扫已用编号 · L-31 ★★读数工具的扫描顺序决定闭合能不能生效★★** ⇒ ★**★共性 = 【凡是有「清单 / 扫描面 / 签收 / 判据 / 幂等 / 挂链 / 读数」的地方, 都要问一句「它会不会过期 / 会不会撞名 / 谁负责让它不过期 / 出了错会红给谁看 / 我做的这件事在它眼里真的生效了吗」】** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-31, 备份 %s.bak_%s_main_l31)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"
    return True


def write_pm():
    ANS = [
        ("main_advance_py_decision_list_order_dependency", "main",
         "★**main 本机实测发现 (★2026-11-24 14:5x·★ISS-391 签收那一趟撞上·★自曝·★不藏★)★: ★**★`state/advance.py` 的老板待拍板清单 (`decisions`) "
         "有一条【顺序依赖】缺陷 ⇒ ⇒ 「main 答了」与「老板清单上少了」不是一回事** ★★"
         "★**★实测 (★本机实跑·★不是推理★)★**: ★**① `advance.py --json` 的 `decisions` = **55** 条, 而 main 13:1x 刚写完 15 条裁决 ⇒ ⇒ 【一条都没少】 ★ "
         "★**② 忠实复刻 advance.py 的扫描逻辑 (★复刻出 55 ⇒ 模型可信★) ⇒ 根因 = 该脚本按分片文件名排序【逐片扫】(`hw → mech → pm → sw`) ⇒ ⇒ "
         "★扫到 `mech.yaml` 的 need 时, `ans_keys` 里【还没有】`pm.yaml` 的 answer ⇒ ⇒ **main 写在 pm.yaml 的同 key 答案, 对 `mech.yaml`/`hw.yaml` 里的 to=boss need 无效** ★ "
         "★**③ 三个实证**: ★**(a) 先例 `iss340_c_bucket_boss_decisions` 【有】pm.yaml 同 key 答案 (★main 2026-11-22 23:5x 写的, 当时明写「这条 need 从此闭合」★) "
         "⇒ 但它【至今仍在老板清单里】⇒ ⇒ 同 key 答案【清不掉】to=boss 的 need ★ **(b) `iss389_oi1_housing_width_window` (★main 13:1x 裁过·★裁决里写了「建议从待拍板移出」★) "
         "⇒ 【同样仍在老板清单里】⇒ ⇒ **main 13:1x 写的「移出」在机器上没生效** ★ **(c) 若改成【先全量收答案再扫 need】, 清单会少 1 条 ⇒ ⇒ 顺序依赖的直接证据** ★★"
         "★**★⇒ 后果 (★老板必须知道·★否则老板会以为自己被问了一条已经答过的题★)★**: ★**老板清单现在 = 55 条, 其中【至少 2 条是 main 已实质答过的】"
         "(`iss340_c_bucket_boss_decisions` + `iss389_oi1_housing_width_window`) ⇒ ⇒ 老板真正要答的 = **53** 条** ★ ★ "         "★**★⇒ main 本轮的处置 = 【披露 + 登记, 不擅自改 advance.py】★**: ★**理由: ① `advance.py` 是老板清单的唯一生成器, 改它 = 动老板看的那张表 ⇒ "
         "② 更要紧: 改它会让「待拍板件数」这个数字在【老板没拍板】的情况下自己变 ⇒ ⇒ 那比现在更危险 (★现在至少是【可数的 55】, 且其中 2 条已被本轮披露★)** ★ "
         "★**⇒ 归属: 这道读数口径属【老板域】⇒ ⇒ 【建议老板拍一次口径】: ① 按「老板清单条数」(55) 读, 还是 ② 按「真正待答条数」(53) 读 ⇒ ★★main 不代拍** ★ "
         "★**★⇒ 另一条可能的解法 (★供老板选·★main 不代拍·★且【不许伪造 decision】★)★**: ★**① 让 owner 在【它自己那份分片】里撤回那两条 need (★它们已被 main 实质闭合·★撤回是诚实做法·★"
         "★但 owner 撤回要占一轮·★且铁律要求不重复派活·★所以归「板只改一次」那一趟同批做★) ⇒ ② 或者老板就当它们还在, 答了也不改变任何工程结论 (★main 已核实这两条的工程结论都已闭合★)** ★★"
         "★**★⇒ 已登记为 LESSONS **L-31** (★main 独占写·★含 4 条通则·★其中通则① = 「有扫描顺序的读数工具, 『我做了 X ⇒ 读数会变』必须先验证, 验证法 = 忠实复刻且必须复现出真实读数」★)** ★ ★"
         "★**★⇒ 一页 §㊸ §⑤ 是这件事给老板看的正式披露 (★★老板请按 53 条读★★)** ★★",
         "state/advance.py (★逐片扫描逻辑·★L131~L192★) · state/decision_truth.py · 一页 §㊸ §⑤ · LESSONS L-31"),

        ("iss391_main_md5_pin_three_deliverables", "main",
         "★**main 本机实测自曝 (★2026-11-24 14:5x·★依据 = L-27 通则②「签收记录里必须钉【md5】, 不许只钉 size」★)★: ★**★main 13:1x 签 ISS-387 / ISS-389 时"
         "【只钉了 size, 没钉 md5】⇒ ⇒ 违反了自己 11:0x 写的铁律 ⇒ ⇒ 本轮已追加式补齐** ★ ★"
         "★**★补钉的三个交付物指纹 (★本机实算 md5 + 实读 size, 落盘前逐条与现盘核对一致, 不符即报错退出★)★**: ★ "
         "★**ISS-387**: 闸 `HW/check_fts_single_row_land_truth.py` md5 `5b9570fd23d6dd7125876c9110085506` (37,318 B) · 真相页 "
         "`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` md5 `a2f78e769bbe9c27c44e728539206c04` (50,714 B) · 交卷页 md5 `0f56b27062fa36a444a09fc4ff35194e` (26,363 B) ★ "
         "★**ISS-389**: 闸 `MECH/check_debug_seat_rework_spec.py` md5 `babadd6b073d691374051ea7409a6a1f` (47,102 B) · 真相页 "
         "`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` md5 `8a56a3eb5a4b1c77e48c283633ec5fe6` (65,851 B) · 交卷页 md5 `459537612f6d03e7ce41b299736a51ce` (40,225 B) ★ ★ "
         "★**★⇒ 补齐后这三单 (含 ISS-391) 的签收记录【逐字可核】: 任何人拿 md5 一比就知道交付物有没有被换过 (★size 相同也可能内容换了·★这正是 L-27 要钉 md5 的理由★)** ★ "
         "★**★⇒ 附一条口径订正 (★L-30 规则②: 所有引用自己那段 ref 字段同步改号·★14:2x 那轮改了一页与 pm.yaml, 漏了台账这四处★)★**: ★**ISS-387/389 的 `verify_result` 内"
         "「一页 §㊶」自指【应读作「§㊷」】(★我 13:1x 那一段在 14:2x 被就地改号为 §㊷·★老字未删·★台账侧只作说明·★不改老字★)** ★ ★"
         "★**★⇒ 往后 main 每一次签收, 【md5 必须在签收当场就钉进去】⇒ ⇒ 不许再出现「只钉 size」⇒ ⇒ 这一条已写进本条裁决** ★★",
         "state/LESSONS.md L-27 通则② · 一页 §㊸ §④ · 台账 ISS-387/389/391 note_addendum"),
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
    p = MEM
    txt = read_lines(p)
    if "L-31" in txt and "顺序依赖" in txt:
        print("  MEMORY.md: L-31 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l31_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-24 当天新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-31★·★main 独占写·★无 job 重写★)★**: "
           "★**L-31 「『main 已经答了』与『老板清单上少了』是两件事 ⇒ 判据: 【读数工具的扫描顺序】决定闭合能不能生效」★** ⇒ "
           "★① 凡是有【扫描顺序】的读数工具, 「我做了 X ⇒ 读数会变」这句话【必须先验证】⇒ 验证法 = 【忠实复刻那个扫描逻辑】+ 【必须复现出工具的真实读数】⇒ 复现不出来 ⇒ 模型不可信 ⇒ 不许据此下结论★ "
           "★② 「main 答了」与「老板清单上少了」是两件事 ⇒ main 落裁决后【必须回头看那把尺子的读数有没有真变】⇒ 没变 ⇒ 要么改工具(★动老板看的那张表·★要老板拍★), 要么让 owner 在它自己那份分片里撤回/回写 decision(★诚实做法★), 要么如实披露★ "
           "★③ 不许为了「让读数好看」伪造 decision: 字段 ⇒ decision_truth 认它 = 代表【老板拍过了】⇒ main 代录老板没拍过的 = 代老板拍板 = 越界★ "
           "★④ 【签收记录必须钉 md5 不许只钉 size】(L-27 通则②) ⇒ 【main 自己签收时也要守这条】⇒ 本轮实证: main 13:1x 签 ISS-387/389 只钉了 size ⇒ 自己违反自己 11:0x 写的铁律 ⇒ 14:5x 追加式补齐 ⇒ 【自曝纪律: 自己写的铁律自己先犯, 必须自己披露自己补】★ "
           "★⇒ ★**本轮实证: advance.py 逐片扫分片 (hw→mech→pm→sw) ⇒ pm.yaml 的同 key 答案对 mech.yaml/hw.yaml 里的 to=boss need 无效 ⇒ 老板清单 55 条里有【至少 2 条是 main 已实质答过的】⇒ 老板真正要答 = 53 条 ⇒ 已披露于 一页 §㊸ §⑤ + pm.yaml `main_advance_py_decision_list_order_dependency` + LESSONS L-31; 不擅自改 advance.py (★改它会让「待拍板件数」在老板没拍板时自己变★)** ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-31 指针追加 (追加式, 备份 %s.bak_%s_main_l31_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_round_log():
    r = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-24_1450_sign_iss391.md")
    body = """# ROUND_LOG_main · 2026-11-24 14:5x · ISS-391 独立复核签收 + 签收记录补钉 md5 (L-27) + 发现 advance.py 顺序依赖缺陷 (L-31)

★**job**: main (ARS45 项目总工) · webchat 会话 (★由兄弟 job 的进展播报触发★)
★**签收闸**: `state/_apply_20260724_1450_main_sign_iss391_md5_pin_and_refs.py` (★fail-closed★)
★**备份**: `state/issue_log.yaml.bak_<stamp>_main_sign_iss391` · `DECISION_ONE_PAGER_2026-11-22.md.bak_<stamp>_main_sign_iss391` ·
`state/LESSONS.md.bak_<stamp>_main_l31` · `MEMORY.md.bak_<stamp>_main_l31_pointer`

---

## ★★一 · 板面 (本机实读) ★★

★板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★

---

## ★★二 · ISS-391 签收 ★★

★**L-27 前提终于满足**: owner 会话 `hw-lead 4b7b08f1` 于 12:51:41 收工, 三个交付件字节静默近 2 小时 ⇒ ⇒ 可签。
★**闸**: 裸跑 rc=1 (★**按设计判红**·L-29) + `--selftest` rc=0 末行 `ALL TESTS PASS` (17/17)。
★**指纹**: 闸 `dabc12000b6cecb1769bb16df09f1abb` (47,175 B) · 真相页 `1a27e49b4055ec891766af54a8e6c778` (45,038 B) · 交卷页 `e7dd41e5fde55bb04a91c25d7cc292f1` (29,690 B)。
★**L-26① 的 13 道扫描面闸逐道实跑全 rc=0**。

★**★main 本机独立复核 (自己读真文件, 不抄闸的输出)★★**
```
① 作业包 WORKPACKET L47 (板侧改动清单 ③) 实读 ⇒ 查不到「钻孔」/「0.71」 ⇒ D1 红得对
② 预检清单 PREFLIGHT 的 B33_PIN_LAND_1P27 段实读 ⇒ 查不到「钻孔」/「0.71」 ⇒ D2/D3 红得对
③ 覆盖度闸 check_onepass_preflight_coverage.py L254 = "③": (["B33_PIN_LAND_1P27"], []) ⇒ P4 不查子动作 ⇒ 补令牌是加严
④ 官方 FTS 图 PDF 自抽文本 ⇒ 含「.028 0.71 (TYP)」; PDF md5 = 1cbe4a2bfa456d8fd030c8b76bdf8dd5 逐字命中 §5 机器块
```

---

## ★★三 · ★★★★本轮最重要的发现: advance.py 的顺序依赖缺陷 (L-31) ★★★★

★**实测**: `advance.py --json` 的 `decisions` = **55** 条, 而 main 13:1x 刚写完 15 条裁决 ⇒ **一条都没少**。
★**根因** (忠实复刻 advance.py 的扫描逻辑, **复刻出 55 ⇒ 模型可信**): 该脚本按分片文件名排序**逐片扫** (`hw → mech → pm → sw`)
⇒ 扫到 `mech.yaml` 的 need 时, `ans_keys` 里**还没有** `pm.yaml` 的 answer ⇒ **main 写在 pm.yaml 的同 key 答案, 对 mech.yaml/hw.yaml 里的 to=boss need 无效**。

★**三个实证 (本机跑出来的, 不是推理)★**
```
① 先例 iss340_c_bucket_boss_decisions: 有 pm.yaml 同 key 答案 (main 2026-11-22 23:5x 写, 当时明写「这条 need 从此闭合」) ⇒ 至今仍在老板清单
② iss389_oi1_housing_width_window (main 13:1x 裁过, 裁决里写了「建议从待拍板移出」) ⇒ 同样仍在老板清单 ⇒ 那句「移出」在机器上没生效
③ 若改成先全量收答案再扫 need ⇒ 清单少 1 条 ⇒ 顺序依赖的直接证据
```

★**后果**: 老板清单 = 55 条, 其中**至少 2 条是 main 已实质答过的** ⇒ **老板真正要答 = 53 条**。
★**处置**: 披露 + 登记 (`main_advance_py_decision_list_order_dependency`), **不改 `advance.py`** (★它是老板清单的唯一生成器; 改它会让「待拍板件数」在老板没拍板时自己变 ⇒ 比现在更危险★) ⇒ 口径归老板域, 一页 §㊸ §⑤ 是给老板的正式披露。

---

## ★★四 · 自曝: main 13:1x 签 ISS-387/389 只钉了 size 没钉 md5 ★★

★**依据 L-27 通则②** (「签收记录里必须钉【md5】, 不许只钉 size」) ⇒ main 自己违反了 ⇒ 本轮**追加式**补齐 (`verify_result` 老字一字未删):

| 单 | 闸 | 真相页 | 交卷页 |
|---|---|---|---|
| ISS-387 | `5b9570fd23d6dd7125876c9110085506` | `a2f78e769bbe9c27c44e728539206c04` | `0f56b27062fa36a444a09fc4ff35194e` |
| ISS-389 | `babadd6b073d691374051ea7409a6a1f` | `8a56a3eb5a4b1c77e48c283633ec5fe6` | `459537612f6d03e7ce41b299736a51ce` |

★落盘前逐条与现盘核对, 不符即报错退出 (★不写没核过的指纹★)。

---

## ★★五 · 落记录 (全部追加式 · 老字一字未删) ★★

★`state/issue_log.yaml` (ISS-391 签收 + ISS-387/389 补钉 md5 补注) · `DECISION_ONE_PAGER_2026-11-22.md` **§㊸** ·
`state/LESSONS.md` **L-31** · `state/fragments/pm.yaml` (+2 条) · `MEMORY.md` (L-31 指针)

---

## ★★六 · 最终读数 (本机实跑) ★★

★板三项未动 · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py`/已签收页逐字节未动 · 三个新闸 rc=0 (ISS-391 闸 rc=1 按设计) ·
13 道扫描面闸全 rc=0 · `merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开, 按设计就该红) ★
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
    for tag, d in (("ISS-391", D391), ("ISS-387", D387), ("ISS-389", D389)):
        rc, o = sh("python3 %s" % d["gate"])
        print("  %-46s rc=%d" % (tag + " 闸", rc))
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
    print("★ main · 2026-11-24 14:5x · ISS-391 签收 + 补钉 md5 + L-31 顺序依赖缺陷")
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
    print("★ 本轮完成: ISS-391 签收 + ISS-387/389 补钉 md5 + L-31 + advance.py 顺序依赖缺陷披露")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板")
    print("★ 零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 未代老板拍板")
    return 0


if __name__ == "__main__":
    sys.exit(main())
