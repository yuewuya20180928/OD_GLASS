#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logs/iss318/probe_landing_trace_board_trip.py
=================================================================================================
★ISS-318 · 挂链前体检用的【只读探针】★ —— 回答任务书 §1 第二件的第 ④ 问:

  ★**`check_landing_trace_obligation.py` 会不会对「板那一趟的合法落表」假红?** ★
  ⇒ ★**不给「应该不会」** ⇒ ★本探针在【沙盒】上真跑 5 种盘面, 把每种的读数打出来★ ★

★**沙盒纪律** ★:
  · 只拷 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (落表台账) + `state/issue_log.yaml` (独立信源) ★
  · ★**真盘一个字节都不写** (只读拷贝) ★
  · 沙盒里【必须】放自己的 issue_log 拷贝 ⇒ ★否则 `sw_issue_log_path()` 会退回真盘那份, 测不到「没留痕」★

用法:
    python3 logs/iss318/probe_landing_trace_board_trip.py
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import shutil
import sys
import tempfile

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name: str, path: str):
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gate = _load("iss318_cdps", os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec.py"))
lto = _load("iss318_lto", os.path.join(PROJ, "SW", "tools", "check_landing_trace_obligation.py"))

LEDGER = gate.LEDGER_CANON
ISSUELOG = "state/issue_log.yaml"

BOARD_PREV = "611b869e13518c3c023fb178f91a0075"          # ★真盘板 md5 (只读·不改)★
BOARD_NEW = "aaaa1111bbbb2222cccc3333dddd4444"          # ★假想改后 md5 (★沙盒里只写在台账文本里★)★
PRO_NEW = "55556666777788889999000011112222"             # ★假想 .kicad_pro 改后 md5★

CHANGE_ROW = (
    "| ★**ISS318-PROBE** ★ | `HW/PCB/demo_mainboard.kicad_pcb` | `%s` | `%s` | "
    "★**2026-11-18 09:0x** ★ | ★**%s** ★ |" % (BOARD_PREV, BOARD_NEW, "%(iss)s")
)
AMBIG_ROW = (
    "| ★**ISS318-PROBE-AMBIG** ★ | `HW/PCB/demo_mainboard.kicad_pcb` + `HW/PCB/demo_mainboard.kicad_pro` | "
    "`%s` | `%s` | ★**2026-11-18 09:0x** ★ | ★**%s** ★ |" % (BOARD_PREV, BOARD_NEW, "%(iss)s")
)


def make_tree(base: str, name: str, ledger_extra: str = "", iss_log_extra: str = "") -> str:
    work = os.path.join(base, name)
    os.makedirs(os.path.join(work, "HW"), exist_ok=True)
    os.makedirs(os.path.join(work, "state"), exist_ok=True)
    shutil.copy2(os.path.join(PROJ, LEDGER), os.path.join(work, LEDGER))
    shutil.copy2(os.path.join(PROJ, ISSUELOG), os.path.join(work, ISSUELOG))
    if ledger_extra:
        p = os.path.join(work, LEDGER)
        txt = open(p, encoding="utf-8").read()
        txt += "\n" + ledger_extra + "\n"
        open(p, "w", encoding="utf-8").write(txt)
    if iss_log_extra:
        p = os.path.join(work, ISSUELOG)
        txt = open(p, encoding="utf-8").read()
        # ★把留痕行插到【指定单号】那一条的末尾 (★下一条 `- ` 之前★)★
        lines = txt.splitlines(True)
        out = []
        inserted = False
        cur_iss = None
        for ln in lines:
            if ln.startswith("- "):
                if cur_iss and not inserted and cur_iss == iss_log_extra.split("|ISS|")[0].strip():
                    out.append(iss_log_extra.split("|ISS|")[1].lstrip("\n"))
                    inserted = True
                cur_iss = None
                import re as _re
                m = _re.search(r"id:\s*['\"]?(ISS-\d+)", ln)
                if m:
                    cur_iss = m.group(1)
            out.append(ln)
        if cur_iss and not inserted and cur_iss == iss_log_extra.split("|ISS|")[0].strip():
            out.append(iss_log_extra.split("|ISS|")[1].lstrip("\n"))
            inserted = True
        if not inserted:
            raise AssertionError("★找不到要插留痕的单号★")
        open(p, "w", encoding="utf-8").write("".join(out))
    return work


def run_case(name: str, desc: str, work: str):
    fails, notes, n = lto.run_gate(work)
    print("-" * 96)
    print(f"【{name}】{desc}")
    print(f"   义务条数 = {n}   红项 = {len(fails)}   ⇒ 判决 = {'★绿★' if not fails else '★红★'}")
    for f in fails:
        print(f"      [FAIL] {f}")
    for nt in notes:
        print(f"      {nt}")
    return len(fails)


def main() -> int:
    base = os.path.join(PROJ, "tmp", "iss318_tmp")
    os.makedirs(base, exist_ok=True)
    work_root = tempfile.mkdtemp(prefix="iss318_ltprobe_", dir=base)
    try:
        # E-0 · 现状 (不加任何东西)
        w = make_tree(work_root, "E0")
        run_case("E-0", "★现状盘面 (不加任何东西) ⇒ 基线读数★", w)

        # E-1 · 台账加一行【板的变更行】, 单号 = 真单号 ISS-302, 但 issue_log 里【没有】板的留痕
        w = make_tree(work_root, "E1", ledger_extra=CHANGE_ROW % {"iss": "ISS-302"})
        run_case("E-1", "★台账加板的变更行 (真单号 ISS-302) · issue_log【没留痕】★", w)

        # E-2 · 同 E-1, 但在 issue_log 的 ISS-302 条目里补一行留痕 (文件名 + 新 md5)
        trace = ("ISS-302", "\n  note: \"ISS318-PROBE: 落表留痕 ★**HW/PCB/demo_mainboard.kicad_pcb** ★ "
                             "改后 md5 ★**%s** ★ (★沙盒探针·真盘没写★)\"\n" % BOARD_NEW)
        w = make_tree(work_root, "E2", ledger_extra=CHANGE_ROW % {"iss": "ISS-302"},
                      iss_log_extra="%s|ISS|%s" % trace)
        run_case("E-2", "★同 E-1 + issue_log 里补了【文件名 + 新 md5】留痕 ⇒ 期望绿★", w)

        # E-3 · 台账加变更行, 单号 = 假单号
        w = make_tree(work_root, "E3", ledger_extra=CHANGE_ROW % {"iss": "ISS-9900"})
        run_case("E-3", "★台账加板的变更行 (★假单号 ISS-9900★) ⇒ 期望红★", w)

        # E-4 · 【歧义行】: 一行同时写板与 .kicad_pro (★权威闸口径: 这种行不算变更行★)
        w = make_tree(work_root, "E4", ledger_extra=AMBIG_ROW % {"iss": "ISS-302"})
        run_case("E-4", "★台账用【一行两件】的歧义行写板+pro ⇒ 权威口径不算变更行 ⇒ 义务会【消失】★", w)

        # E-5 · 台账加变更行, 单号 = 真单号, issue_log 的留痕写的是【改前的 md5】(★LT-3 同款形状·但场景是「板那一趟」★)
        trace2 = ("ISS-302", "\n  note: \"ISS318-PROBE: 落表留痕 ★**HW/PCB/demo_mainboard.kicad_pcb** ★ "
                              "改后 md5 ★**%s** ★ (★沙盒探针·真盘没写★)\"\n" % BOARD_PREV)
        w = make_tree(work_root, "E5", ledger_extra=CHANGE_ROW % {"iss": "ISS-302"},
                      iss_log_extra="%s|ISS|%s" % trace2)
        run_case("E-5", "★issue_log 的留痕写的是【改前的 md5】⇒ 期望红 (缺新 md5)★", w)
    finally:
        shutil.rmtree(work_root, ignore_errors=True)
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
