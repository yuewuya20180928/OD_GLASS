#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-279 · 「板只改一次」那一趟的【SW 侧板侧输入收口闸】
=================================================================================================
派活: state/dispatch_briefs/ISS-279_sw_board_side_input_sync.md (项目总工 2026-11-17 07:5x / 08:1x 续做)

★**本闸守的是「SW 侧清单全不全 / 清不新鲜」, 不是板** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★
★**本闸是【新建】文件 ⇒ `SW/tools/check_demo_panel_spec.py` 一个字节不许动** ★

六条判据:
  W1 清单可解析  : JSON 块能解析 + 每条固定 9 个字段齐全 (★缺一个即红★) + 字段非空
  W2 归属步合法  : 每条 `step` ∈ S1~S13 (★不许写「S0」/「TBD」/ 空★)
  W3 判据命令真存在: 每条 `criterion` 里引用的脚本文件在本机真实存在 (★不许把不存在的命令写进清单★)
  W4 覆盖度      : ★本闸核心★ —— ①~⑧ 八条一个不缺 (★漏一条即红★)
                    + 反向: 每条 `source_iss` 必须落在来源单全集里 (★不许有来源不明的项★)
  W5 现状一致    : ★标 [实测] 的现状值必须与盘面实测一致★ (★改了盘面没改清单 = 清单过期 = 当场红★)
  W6 受保护 5 件 : 板 / .kicad_pro / 网表 / 脚表 / BOM 的 md5 逐字节不变
                    + ★SW 台账 §1 锚点块里那两个 md5 一个字节没动★ (★「不许手改 md5 凑绿」由这条兜住★)

★**★W4 是本单的核心判据**: ★**「那一趟改了板, SW 侧会漂的那几处」一条都不能漏** ★
★**★W6 的第二条 (锚点块两个 md5) 是 ISS-273 / ISS-275 花大力气堵掉的「悄悄换真源」漏洞的兜底** ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 SW/tools/check_onepass_sw_sync.py            # 主模式
  python3 SW/tools/check_onepass_sw_sync.py --selftest  # 反向用例 (≥6 条, 每条自证改到了目标)
  ★自检用 env 覆盖★: SW_SYNC_CHECKLIST / SW_SYNC_PCB / SW_SYNC_PRO /
                     SW_SYNC_NETLIST / SW_SYNC_PINS / SW_SYNC_BOM / SW_SYNC_LEDGER
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))

CHECKLIST = (os.environ.get("SW_SYNC_CHECKLIST")
             or os.path.join(PROJ, "SW", "BOARD_ONEPASS_SW_SYNC.md"))
LEDGER = (os.environ.get("SW_SYNC_LEDGER")
          or os.path.join(PROJ, "SW", "SW_MD5_BASELINE_LEDGER.md"))

FIELDS = ("id", "source_iss", "title", "current_state", "action",
          "criterion", "step", "blocked_by", "evidence")

STEPS = ["S%d" % i for i in range(1, 14)]

# ★W4 的覆盖度全集 (★任务书 §1.3 的 ①~⑧ 八条, 一条不许漏 ★)
REQUIRED_IDS = ["SW01_PCB_MD5", "SW02_KICAD_PRO_MD5", "SW03_LAND8_DNP",
                "SW04_CHG_LED_REF", "SW05_KEY_NETNAMES", "SW06_TP_INT",
                "SW07_C_VBUS_GND", "SW08_ESD_USB_D"]

# ★来源单全集 (★每条 source_iss 的每个 token 必须落在里面 ★)
SOURCES = {"ISS-225", "ISS-234", "ISS-241", "ISS-244", "ISS-266", "ISS-269",
           "ISS-271", "ISS-273", "ISS-274", "ISS-275", "ISS-276", "ISS-277",
           "ISS-278", "ISS-279"}

# ★台账 §1 锚点块里那两个 md5 的基线 (★W6 第二条: 一个字节不许动 ★)
ANCHOR_MD5 = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
}


def protected_map():
    """★受保护 5 件 (★每次调用都重读 env ⇒ --selftest 能在运行中换路径 ★)"""
    return {
        "板": (os.environ.get("SW_SYNC_PCB") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
               "611b869e13518c3c023fb178f91a0075"),
        ".kicad_pro": (os.environ.get("SW_SYNC_PRO") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro"),
                       "3e504d2be83152e337949723e909be1b"),
        "网表": (os.environ.get("SW_SYNC_NETLIST") or os.path.join(PROJ, "HW", "netlist_v1.csv"),
                 "e06c1dd633566aa44732762c2ff99d1c"),
        "脚表": (os.environ.get("SW_SYNC_PINS") or os.path.join(PROJ, "HW", "netlist_v1_pins.csv"),
                 "287e7861a0d1007748d92d9fbecdd490"),
        "BOM": (os.environ.get("SW_SYNC_BOM") or os.path.join(PROJ, "HW", "BOM_v1.csv"),
                "94642d07a69e8d60dd2af57f69b93607"),
    }


# ★W5 现状探针 (★item_id → (命令, 抽取正则, 必须在该条 current_state 里出现的串 ★)
PROBES = {
    "SW01_PCB_MD5": (
        ["md5sum", os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")],
        r"([0-9a-f]{32})"),
    "SW02_KICAD_PRO_MD5": (
        ["md5sum", os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro")],
        r"([0-9a-f]{32})"),
    "SW03_LAND8_DNP": (
        ["python3", "-c",
         "import csv;rs=list(csv.DictReader(open('HW/netlist_v1_pins.csv')));"
         "refs={r['ref'] for r in rs};"
         "t={'D_CHG_LED','D_LED_G','D_LED_R','SW_BOOT','SW_KEY_PWR',"
         "'SW_KEY_VM','SW_KEY_VP','SW_RST'};"
         "print('落表残项 %d 行' % len(t&refs))"],
        r"(落表残项 \d+ 行)"),
    "SW04_CHG_LED_REF": (
        ["python3", "-c",
         "p='SW/SHUTDOWN_SEMANTICS_SPEC.md';t=open(p,encoding='utf-8').read().splitlines();"
         "d=sum(1 for l in t if 'D_CHG_LED' in l);q=sum(1 for l in t if 'Q_CHG_LED' in l);"
         "print('D_CHG_LED %d 次 · Q_CHG_LED %d 次' % (d,q))"],
        r"(D_CHG_LED \d+ 次 · Q_CHG_LED \d+ 次)"),
    "SW05_KEY_NETNAMES": (
        ["python3", "-c",
         "import csv;rs=list(csv.DictReader(open('HW/netlist_v1_pins.csv')));"
         "m={r['ref']:r['net'] for r in rs if r['pin']=='1' and r['ref'] in "
         "{'SW_BOOT','SW_KEY_PWR','SW_KEY_VM','SW_KEY_VP','SW_RST'}};"
         "print(' · '.join('%s→%s'%(k,m[k]) for k in "
         "['SW_BOOT','SW_KEY_PWR','SW_KEY_VM','SW_KEY_VP','SW_RST'] if k in m))"],
        r"(SW_BOOT→\S+ · SW_KEY_PWR→\S+ · SW_KEY_VM→\S+ · SW_KEY_VP→\S+ · SW_RST→\S+)"),
    "SW06_TP_INT": (
        ["python3", "-c",
         "ps=['HW/netlist_v1.csv','HW/netlist_v1_pins.csv','HW/PCB/demo_mainboard.kicad_pcb'];"
         "c=[sum(1 for l in open(p,encoding='utf-8',errors='replace') if 'TP_INT' in l) for p in ps];"
         "print('TP_INT 命中数: 网表 %d · 脚表 %d · 板 %d' % tuple(c))"],
        r"(TP_INT 命中数: 网表 \d+ · 脚表 \d+ · 板 \d+)"),
    "SW07_C_VBUS_GND": (
        ["bash", "state/pcbnew_py.sh", "state/check_pcb_nets.py"],
        r"(多余 \d+)"),
    "SW08_ESD_USB_D": (
        ["python3", "HW/check_netlist_selfconsistency.py"],
        r"(板面距离 = [\d.]+ mm)"),
}

_CACHE = {}


def sh(cmd, timeout=900):
    key = " ".join(cmd)
    if key in _CACHE:
        return _CACHE[key]
    try:
        r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        out = (r.stdout or b"").decode("utf-8", "replace")
        rc = r.returncode
    except Exception as e:                                   # pragma: no cover
        out, rc = "EXC: %s" % e, -1
    _CACHE[key] = (rc, out)
    return rc, out


def md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def load_items(checklist_path):
    """★从清单页里抽 JSON 块 ⇒ (items, 全文) ★"""
    txt = read_text(checklist_path)
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    if not m:
        return None, txt
    try:
        data = json.loads(m.group(1))
    except Exception:
        return None, txt
    items = data.get("items")
    return (items if isinstance(items, list) else None), txt


# ==============================================================================
# 六条判据
# ==============================================================================
def check_W1(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 清单页里找不到可解析的 JSON 块 (或 items 不是数组)"]
    for it in items:
        if not isinstance(it, dict):
            bad.append("item 不是 dict: %r" % (it,))
            ok = False
            continue
        miss = [f for f in FIELDS if f not in it]
        empty = [f for f in FIELDS if f in it and not str(it[f]).strip()]
        if miss or empty:
            ok = False
            bad.append("id=%s 缺字段=%s 空字段=%s" % (it.get("id", "?"), miss, empty))
    return ok, ["     条目 %d 条 · 9 字段齐全且非空: %s" % (len(items), "✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_W2(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    dist = {s: 0 for s in STEPS}
    for it in items:
        st = str(it.get("step", "")).strip()
        if st not in STEPS:
            ok = False
            bad.append("id=%s 的 step=%r 不在 S1~S13 (★不许写 S0 / TBD / 空★)" % (it.get("id"), st))
        else:
            dist[st] += 1
    return ok, ["     归属步分布: %s" % (" ".join("%s=%d" % (s, dist[s]) for s in STEPS) or "-")] + \
        ["     ❌ %s" % b for b in bad]


def check_W3(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    for it in items:
        crit = str(it.get("criterion", ""))
        if not re.search(r"(python3|bash|md5sum|grep)\s", crit):
            ok = False
            bad.append("id=%s 的 criterion 里认不出命令: %r" % (it.get("id"), crit[:70]))
            continue
        for tok in re.findall(r"[\w./\-]+\.(?:py|sh)", crit):
            p = tok if os.path.isabs(tok) else os.path.join(PROJ, tok)
            if not os.path.exists(p):
                ok = False
                bad.append("id=%s 的 criterion 引用了不存在的文件: %s" % (it.get("id"), tok))
    return ok, ["     每条 criterion 的脚本文件都在盘上: %s" % ("✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_W4(items, txt):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    blob = json.dumps(items, ensure_ascii=False)
    ids = [str(it.get("id", "")) for it in items if isinstance(it, dict)]
    for rid in REQUIRED_IDS:
        if rid not in ids:
            ok = False
            bad.append("★清单里没有 %s ⇒ 漏项 (★①~⑧ 八条一条都不许漏★)" % rid)
    for it in items:
        if not isinstance(it, dict):
            continue
        s = str(it.get("source_iss", "")).strip()
        for tok in [x.strip() for x in s.split("+") if x.strip()]:
            if tok not in SOURCES:
                ok = False
                bad.append("id=%s 的 source_iss=%r 不在来源单全集里 ⇒ 来源不明"
                           % (it.get("id"), tok))
    return ok, ["     覆盖度: ①~⑧ 八条全部在清单里: %s" % ("✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_W5(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    by_id = {str(it.get("id")): it for it in items if isinstance(it, dict)}
    for item_id, (cmd, rx) in PROBES.items():
        it = by_id.get(item_id)
        if it is None:
            ok = False
            bad.append("清单里没有探针绑定的条目 %s" % item_id)
            continue
        rc, out = sh(cmd)
        m = re.search(rx, out)
        if not m:
            ok = False
            bad.append("%s 的探针没抽到值 (rc=%d): %s" % (item_id, rc, rx))
            continue
        val = m.group(1)
        state = str(it.get("current_state", ""))
        if val not in state:
            ok = False
            bad.append("%s: 盘面实测 = %r, 但清单 current_state 里没有这个值 ⇒ 清单过期"
                       % (item_id, val))
    return ok, ["     %d 个现状探针: 清单里的现状值 == 盘面实测: %s"
                % (len(PROBES), "✔" if ok else "❌")] + ["     ❌ %s" % b for b in bad]


def check_W6():
    ok, bad = True, []
    for name, (path, base) in protected_map().items():
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        cur = md5(path)
        if cur != base:
            ok = False
            bad.append("%s md5 %s ≠ 基线 %s" % (name, cur, base))
    # ---- 第二条: SW 台账 §1 锚点块里那两个 md5 一个字节不许动 (★不许手改 md5 凑绿 ★) ----
    led = os.environ.get("SW_SYNC_LEDGER") or LEDGER
    if not os.path.exists(led):
        ok = False
        bad.append("SW 台账不存在: %s" % led)
    else:
        txt = read_text(led)
        m = re.search(r"#\s*BEGIN\s+SW_MD5_ANCHORS(.*?)#\s*END\s+SW_MD5_ANCHORS", txt, re.S)
        if not m:
            ok = False
            bad.append("SW 台账 §1 锚点块 (# BEGIN/END SW_MD5_ANCHORS) 读不到 ⇒ fail-closed")
        else:
            blk = m.group(1)
            for rel, want in ANCHOR_MD5.items():
                mm = re.search(r"-\s*file:\s*%s\s*\n\s*md5:\s*([0-9a-fA-F]{32})"
                               % re.escape(rel), blk)
                if not mm:
                    ok = False
                    bad.append("台账 §1 锚点块里找不到 %s 的 md5 条目 ⇒ 硬保护件失保护" % rel)
                    continue
                got = mm.group(1).lower()
                if got != want:
                    ok = False
                    bad.append("台账 §1 锚点块里 %s 的 md5 = %s ≠ 基线 %s ⇒ 有人手改 md5 凑绿"
                               % (rel, got, want))
    return ok, ["     受保护 5 件 md5 逐字节不变 + 台账 §1 锚点块两个 md5 未被手改: %s"
                % ("✔" if ok else "❌")] + ["     ❌ %s" % b for b in bad]


CHECKS = {
    "W1": lambda items, txt: check_W1(items),
    "W2": lambda items, txt: check_W2(items),
    "W3": lambda items, txt: check_W3(items),
    "W4": lambda items, txt: check_W4(items, txt),
    "W5": lambda items, txt: check_W5(items),
    "W6": lambda items, txt: check_W6(),
}


def evaluate(checklist_path, only=None):
    items, txt = load_items(checklist_path)
    lines, ok = [], True
    for cid, fn in CHECKS.items():
        if only and cid != only:
            continue
        r_ok, r_lines = fn(items, txt)
        lines.append("  %s  %s" % ("OK " if r_ok else "FAIL", cid))
        lines.extend(r_lines)
        ok = ok and r_ok
    return ok, lines


# ==============================================================================
# --selftest
# ==============================================================================
def write_variant(src_path, dst_path, mutate):
    """★把清单页的 JSON 块换掉, 写一份副本 (★用来做反向用例 ★)"""
    txt = read_text(src_path)
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    data = json.loads(m.group(1))
    mutate(data)
    new_block = "```json\n%s\n```" % json.dumps(data, ensure_ascii=False, indent=2)
    txt2 = txt[:m.start()] + new_block + txt[m.end():]
    open(dst_path, "w", encoding="utf-8").write(txt2)
    return dst_path


def run_selftest(checklist_path):
    tmpd = tempfile.mkdtemp(prefix="iss279_selftest_")
    cases = []
    try:
        # ① 删掉 ①~⑧ 里的一条 ⇒ W4 红
        p = os.path.join(tmpd, "v1.md")
        write_variant(checklist_path, p, lambda d: d["items"].remove(
            next(i for i in d["items"] if i["id"] == "SW03_LAND8_DNP")))
        ok, _ = evaluate(p, only="W4")
        cases.append(("① 删掉 ①~⑧ 里的 SW03_LAND8_DNP ⇒ W4 红", ok is False))

        # ② 归属步改成 S99 ⇒ W2 红
        p = os.path.join(tmpd, "v2.md")
        def mut2(d):
            next(i for i in d["items"] if i["id"] == "SW07_C_VBUS_GND")["step"] = "S99"
        write_variant(checklist_path, p, mut2)
        ok, _ = evaluate(p, only="W2")
        cases.append(("② 把归属步改成 S99 ⇒ W2 红", ok is False))

        # ③ 判据命令指向不存在的脚本 ⇒ W3 红
        p = os.path.join(tmpd, "v3.md")
        def mut3(d):
            next(i for i in d["items"] if i["id"] == "SW01_PCB_MD5")["criterion"] = \
                "python3 SW/tools/check_onepass_sw_does_not_exist_zzz.py ⇒ rc=0"
        write_variant(checklist_path, p, mut3)
        ok, _ = evaluate(p, only="W3")
        cases.append(("③ 判据命令指向不存在的脚本 ⇒ W3 红", ok is False))

        # ④ 把某条 [实测] 值改错 (板 md5 改一位) ⇒ W5 红
        p = os.path.join(tmpd, "v4.md")
        def mut4(d):
            it = next(i for i in d["items"] if i["id"] == "SW01_PCB_MD5")
            it["current_state"] = it["current_state"].replace(
                "611b869e13518c3c023fb178f91a0075", "611b869e13518c3c023fb178f91a0076")
        write_variant(checklist_path, p, mut4)
        ok, _ = evaluate(p, only="W5")
        cases.append(("④ 把板 md5 改错一位 ⇒ W5 红 (清单过期当场被抓)", ok is False))

        # ⑤ 改受保护 5 件之一 (板) ⇒ W6 红
        pcb_src = protected_map()["板"][0]
        pcb_bad = os.path.join(tmpd, "board_bad.kicad_pcb")
        with open(pcb_bad, "w", encoding="utf-8") as f:
            f.write(read_text(pcb_src) + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("SW_SYNC_PCB")
        os.environ["SW_SYNC_PCB"] = pcb_bad
        ok, _ = evaluate(checklist_path, only="W6")
        if old is None:
            os.environ.pop("SW_SYNC_PCB", None)
        else:
            os.environ["SW_SYNC_PCB"] = old
        cases.append(("⑤ 板文件被改一个字节 ⇒ W6 红", ok is False))

        # ⑥ 改台账 §1 锚点块里板的 md5 ⇒ W6 红 (★「不许手改 md5 凑绿」那一条 ★)
        led_src = os.environ.get("SW_SYNC_LEDGER") or LEDGER
        led_bad = os.path.join(tmpd, "ledger_bad.md")
        t = read_text(led_src)
        assert "611b869e13518c3c023fb178f91a0075" in t
        with open(led_bad, "w", encoding="utf-8") as f:
            f.write(t.replace("md5: 611b869e13518c3c023fb178f91a0075",
                              "md5: 611b869e13518c3c023fb178f91a0076", 1))
        old = os.environ.get("SW_SYNC_LEDGER")
        os.environ["SW_SYNC_LEDGER"] = led_bad
        ok, _ = evaluate(checklist_path, only="W6")
        if old is None:
            os.environ.pop("SW_SYNC_LEDGER", None)
        else:
            os.environ["SW_SYNC_LEDGER"] = old
        cases.append(("⑥ 台账 §1 锚点块里板的 md5 被手改 ⇒ W6 红 (★不许手改 md5 凑绿★)", ok is False))

        # ⑦ 抽掉一条的一个字段 ⇒ W1 红
        p = os.path.join(tmpd, "v7.md")
        def mut7(d):
            next(i for i in d["items"] if i["id"] == "SW05_KEY_NETNAMES").pop("criterion")
        write_variant(checklist_path, p, mut7)
        ok, _ = evaluate(p, only="W1")
        cases.append(("⑦ 抽掉一条的 criterion 字段 ⇒ W1 红", ok is False))

        # ⑧ source_iss 改成来源不明 ⇒ W4 红
        p = os.path.join(tmpd, "v8.md")
        def mut8(d):
            next(i for i in d["items"] if i["id"] == "SW06_TP_INT")["source_iss"] = "ISS-999"
        write_variant(checklist_path, p, mut8)
        ok, _ = evaluate(p, only="W4")
        cases.append(("⑧ source_iss 改成来源不明 (ISS-999) ⇒ W4 红", ok is False))

        # ★基线: 真盘必须全绿 (否则上面那些红没意义)
        ok0, _ = evaluate(checklist_path)
        cases.append(("★基线: 真盘 W1~W6 全绿", ok0 is True))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 78)
    print("  ISS-279 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 78)
    bad = 0
    for name, caught in cases:
        mark = "✔" if caught else "✘"
        if not caught:
            bad += 1
        print("  %s  %s" % (mark, name))
    print("-" * 78)
    print("  反向用例 %d/%d 通过" % (len(cases) - bad, len(cases)))
    if bad:
        print("  ❌ 有反向用例没抓到 ⇒ 闸不是判据 (或用例本身写错了)")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--checklist", default=CHECKLIST)
    args = ap.parse_args()

    if not os.path.exists(args.checklist):
        print("❌ 用法错: 找不到清单页 %s" % args.checklist)
        return 2

    if args.selftest:
        return run_selftest(args.checklist)

    print("=" * 78)
    print("  ISS-279 · SW 侧板侧输入收口闸 (★W1 清单 / W2 归属步 / W3 判据真命令 / W4 覆盖度 / W5 现状 / W6 受保护★)")
    print("=" * 78)
    ok, lines = evaluate(args.checklist)
    for l in lines:
        print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★SW 侧板侧输入清单齐全 (①~⑧ 八条一条不缺) 且现状值与盘面一致 ★★")
        return 0
    print("  ❌ rc=1: ★★SW 侧清单有漏项, 或现状值已过期 ⇒ 那一趟改完 SW 侧会漂一处 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
