#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-277 · 「板只改一次」板侧漏项【覆盖度闸】 —— 清单页 + 作业包 + 交卷单三处一致性的机器判据
=================================================================================================
派活: state/dispatch_briefs/ISS-277_hw_onepass_preflight_coverage.md (项目总工 2026-11-17 07:3x)

★**本闸守的是「清单全不全 / 清不新鲜」, 不是板** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★

六条判据:
  P1 清单可解析  : JSON 块能解析 + 每条固定 9 个字段齐全 (★缺一个即红★) + 字段非空
  P2 归属步合法  : `step` ∈ S1~S13 + ★S1~S13 每步至少被覆盖一次★ (★不许有步没人管★)
  P3 判据命令真存在: 每条 `criterion` 里引用的脚本文件在本机真实存在 (★不许把不存在的命令写进清单★)
  P4 覆盖度      : ★本闸核心★ —— 25 个板侧标记每个都必须在清单里出现 (★漏一条即红★)
                    + 反向: 每条 `source_iss` 必须落在来源单全集里 (★不许有来源不明的项★)
  P5 现状一致    : ★标 [实测] 的现状值必须与盘面实测一致★ (★改了盘面没改清单 = 清单过期 = 当场红★)
  P6 受保护 5 件 : 板 / .kicad_pro / 网表 / 脚表 / BOM 的 md5 逐字节不变

★**★P4 是本单的核心判据**: ★**「只在交卷单里、没进清单」的漏项才会被抓住** ⇒ ★**漏做一项 = 板 md5 变第二次** ★
★**★P5 是防「清单变成第二份过期文档」的关键**: 盘面一变, 清单不跟 = 当场红 ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_onepass_preflight_coverage.py            # 主模式
  python3 HW/check_onepass_preflight_coverage.py --selftest  # 反向用例 (≥6 条, 每条自证改到了目标)
  ★自检用 env 覆盖★: PREFLIGHT_CHECKLIST / PREFLIGHT_PCB / PREFLIGHT_PRO /
                     PREFLIGHT_NETLIST / PREFLIGHT_PINS / PREFLIGHT_BOM
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
PROJ = os.path.dirname(HERE)
# ★★ISS-283 · ⑩-b: 落表台账的 md5 注册表 (★网表/脚表/BOM 的基线走「落表台账为准」★) ★★
sys.path.insert(0, HERE)
import landing_md5

CHECKLIST = os.environ.get("PREFLIGHT_CHECKLIST") or os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")

def protected_map():
    """★受保护 5 件 (★每次调用都重读 env ⇒ --selftest 能在运行中换路径 ★)

    ★★ISS-283 · ⑩-b (★2026-11-17 12:4x 实测★): 网表 / 脚表 / BOM 三件的基线 【不再写死】★★
      ⇒ 改成 ★**「落表台账为准」**★ (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 的最新登记★)
      ⇒ ★★**理由: 只把基线数字改成新值 = 下次落表又红一遍 ⇒ 判据的【取值来源】必须变·不是【取值】变★★**
      ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 四项不齐 ⇒ 一律红** (★fail-closed·见 `HW/landing_md5.py`★) ★
    ★**板 / `.kicad_pro` 两件的基线照旧写死** (★它们不归落表链管 ⇒ 那两条一条不许动★) ★
    ⇒ 返回值第 2 项 = 写死的基线 (None = 走落表台账) · 第 3 项 = 该件的相对路径 (查台账要用★)
    """
    return {
        "板": (os.environ.get("PREFLIGHT_PCB") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
               "611b869e13518c3c023fb178f91a0075",
               "HW/PCB/demo_mainboard.kicad_pcb"),
        ".kicad_pro": (os.environ.get("PREFLIGHT_PRO") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro"),
                       "3e504d2be83152e337949723e909be1b",
                       "HW/PCB/demo_mainboard.kicad_pro"),
        "网表": (os.environ.get("PREFLIGHT_NETLIST") or os.path.join(PROJ, "HW", "netlist_v1.csv"),
                 # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 (★出处 = 落表台账 §16.2★) ★★
                 None,
                 "HW/netlist_v1.csv"),
        "脚表": (os.environ.get("PREFLIGHT_PINS") or os.path.join(PROJ, "HW", "netlist_v1_pins.csv"),
                 # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 ★★
                 None,
                 "HW/netlist_v1_pins.csv"),
        "BOM": (os.environ.get("PREFLIGHT_BOM") or os.path.join(PROJ, "HW", "BOM_v1.csv"),
                # ★★ISS-283 · ⑩-b: 不写死 ⇒ 走「落表台账为准」 ★★
                None,
                "HW/BOM_v1.csv"),
    }

FIELDS = ("id", "source_iss", "title", "current_state", "action",
          "criterion", "step", "blocked_by", "evidence")

STEPS = ["S%d" % i for i in range(1, 14)]

# ★P4 的覆盖度标记 (★从 6 份来源交卷单反查出来的板侧项标记 ★)
MARKERS = ["D_ESD_CAM", "Q_AND", "Q_PG", "D_ESD_TC", "U_LDO_S28", "J_CHG",
           "D_CHG_LED", "D_LED_G", "D_LED_R", "SW_BOOT", "SW_KEY_PWR",
           "SW_KEY_VM", "SW_KEY_VP", "SW_RST", "R_SEL_D3_P", "J_DEBUG",
           "J_UART", "R_SUPV_DIV", "U_SUPV", "TPS7A20", "Q_ENVC",
           "D_ESD_USB_D", "C_REGN", "C_VBUS_GND", "U_EN_SW", "R_BAT_DET_1"]

# ★来源单全集 (★每条 source_iss 必须落在里面 ★)
# ★★ISS-283 · cont2: 增 ISS-283 (★本单落表带来的板侧同步项 §③ 三条的来源单★
#   ⇒ ★★只【增来源】不【放宽判据】: 来源不明 (不在这个全集里) 照样判红★★)
SOURCES = {"ISS-239", "ISS-241", "ISS-244", "ISS-247", "ISS-266",
           "ISS-269", "ISS-271", "ISS-274", "ISS-276", "ISS-283"}

# ★P5 现状探针 (★item_id → (命令, 抽取正则, 必须在该条 current_state 里出现的串 ★)
PROBES = {
    "B02_C_VBUS_GND": (
        ["bash", "state/pcbnew_py.sh", "state/check_pcb_nets.py"],
        r"(多余 \d+)"),
    "B17_DNP_43": (
        ["python3", "HW/check_netlist_contradiction_r3.py"],
        r"(零标记 \d+ 颗)"),
    "B25_UNCONNECTED": (
        ["python3", "state/check_pcb_drc.py"],
        r"(unconnected items = \d+)"),
    "B03_ULDO_S28_PAD3": (
        ["python3", "HW/check_pin_function_labels.py"],
        r"(\d+ 条缺陷)"),
    "B20_LAND_8ROWS": (
        ["python3", "-c",
         "import csv;rs=csv.DictReader(open('HW/netlist_v1_pins.csv'));"
         "refs={r['ref'] for r in rs};t={'D_CHG_LED','D_LED_G','D_LED_R','SW_BOOT',"
         "'SW_KEY_PWR','SW_KEY_VM','SW_KEY_VP','SW_RST'};"
         "print('落表残项 %d 行'%len(t&refs))"],
        r"(落表残项 \d+ 行)"),
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
def check_P1(items):
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


def check_P2(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    dist = {s: 0 for s in STEPS}
    for it in items:
        st = str(it.get("step", "")).strip()
        if st not in STEPS:
            ok = False
            bad.append("id=%s 的 step=%r 不在 S1~S13" % (it.get("id"), st))
        else:
            dist[st] += 1
    empty = [s for s in STEPS if dist[s] == 0]
    if empty:
        ok = False
        bad.append("这些步没人管 (零覆盖): %s" % empty)
    return ok, ["     步覆盖: %s" % " ".join("%s=%d" % (s, dist[s]) for s in STEPS)] + \
        ["     ❌ %s" % b for b in bad]


def check_P3(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    for it in items:
        crit = str(it.get("criterion", ""))
        m = re.search(r"(python3|bash|md5sum)\s+([^\s⇒;]+)", crit)
        if not m:
            ok = False
            bad.append("id=%s 的 criterion 里认不出命令: %r" % (it.get("id"), crit[:60]))
            continue
        for tok in re.findall(r"[\w./\-]+\.(?:py|sh)", crit):
            p = tok if os.path.isabs(tok) else os.path.join(PROJ, tok)
            if not os.path.exists(p):
                ok = False
                bad.append("id=%s 的 criterion 引用了不存在的文件: %s" % (it.get("id"), tok))
    return ok, ["     每条 criterion 的脚本文件都在盘上: %s" % ("✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_P4(items, txt):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    blob = json.dumps(items, ensure_ascii=False)
    for mk in MARKERS:
        if mk not in blob:
            ok = False
            bad.append("★板侧标记 %s 在清单里找不到 ⇒ 漏项 (★它只存在于来源交卷单里 ★)" % mk)
    for it in items:
        s = str(it.get("source_iss", "")).strip()
        if s not in SOURCES:
            ok = False
            bad.append("id=%s 的 source_iss=%r 不在来源单全集里 ⇒ 来源不明" % (it.get("id"), s))
    return ok, ["     覆盖度: %d 个标记全部在清单里: %s" % (len(MARKERS), "✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_P5(items):
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 没有 items"]
    by_id = {str(it.get("id")): it for it in items}
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


def check_P6():
    ok, bad, good = True, [], []
    for name, (path, base, rel) in protected_map().items():
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        cur = md5(path)
        if base is None:
            # ★★ISS-283 · ⑩-b: 网表/脚表/BOM 走「落表台账为准」的口径 (★不是把基线数字改成新值★) ★
            g, msg = landing_md5.check_registered(PROJ, rel, path, md5)
            if g:
                good.append("     ✔ %s" % msg)
            else:
                ok = False
                bad.append("%s: %s" % (name, msg))
            continue
        if cur != base:
            ok = False
            bad.append("%s md5 %s ≠ 基线 %s" % (name, cur, base))
        else:
            good.append("     ✔ %s md5 未变 (%s) (★基线写死·不归落表链管★)" % (name, cur))
    return ok, ["     受保护 5 件 md5 逐字节不变: %s" % ("✔" if ok else "❌")] + good + \
        ["     ❌ %s" % b for b in bad]


CHECKS = {
    "P1": lambda items, txt: check_P1(items),
    "P2": lambda items, txt: check_P2(items),
    "P3": lambda items, txt: check_P3(items),
    "P4": lambda items, txt: check_P4(items, txt),
    "P5": lambda items, txt: check_P5(items),
    "P6": lambda items, txt: check_P6(),
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
    tmpd = tempfile.mkdtemp(prefix="iss277_selftest_")
    cases = []
    try:
        # ① 清单里删掉一条 (含标记 D_ESD_CAM) ⇒ P4 红
        p = os.path.join(tmpd, "v1.md")
        write_variant(checklist_path, p, lambda d: d["items"].remove(
            next(i for i in d["items"] if i["id"] == "B13_ESD_CAM_PAD")))
        ok, _ = evaluate(p, only="P4")
        cases.append(("① 删掉含 D_ESD_CAM 的那一条 ⇒ P4 红", ok is False))

        # ② 改一条现状值 ⇒ P5 红
        p = os.path.join(tmpd, "v2.md")
        def mut2(d):
            it = next(i for i in d["items"] if i["id"] == "B25_UNCONNECTED")
            it["current_state"] = it["current_state"].replace("unconnected items = 45",
                                                             "unconnected items = 40")
        write_variant(checklist_path, p, mut2)
        ok, _ = evaluate(p, only="P5")
        cases.append(("② 把 unconnected 现状值改成 40 ⇒ P5 红", ok is False))

        # ③ 抽掉一个字段 ⇒ P1 红
        p = os.path.join(tmpd, "v3.md")
        def mut3(d):
            it = next(i for i in d["items"] if i["id"] == "B01_REF_SUFFIX")
            it.pop("step")
        write_variant(checklist_path, p, mut3)
        ok, _ = evaluate(p, only="P1")
        cases.append(("③ 抽掉一条的 step 字段 ⇒ P1 红", ok is False))

        # ④ 归属步改成 S99 ⇒ P2 红
        p = os.path.join(tmpd, "v4.md")
        def mut4(d):
            next(i for i in d["items"] if i["id"] == "B02_C_VBUS_GND")["step"] = "S99"
        write_variant(checklist_path, p, mut4)
        ok, _ = evaluate(p, only="P2")
        cases.append(("④ 把归属步改成 S99 ⇒ P2 红", ok is False))

        # ⑤ 判据命令写成不存在的 ⇒ P3 红
        p = os.path.join(tmpd, "v5.md")
        def mut5(d):
            next(i for i in d["items"] if i["id"] == "B01_REF_SUFFIX")["criterion"] = \
                "python3 HW/check_this_does_not_exist_zzz.py ⇒ rc=0"
        write_variant(checklist_path, p, mut5)
        ok, _ = evaluate(p, only="P3")
        cases.append(("⑤ 判据命令指向不存在的脚本 ⇒ P3 红", ok is False))

        # ⑥ 改受保护 5 件之一 (板) ⇒ P6 红
        pcb_src = protected_map()["板"][0]
        pcb_bad = os.path.join(tmpd, "board_bad.kicad_pcb")
        t = read_text(pcb_src)
        open(pcb_bad, "w", encoding="utf-8").write(t + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("PREFLIGHT_PCB")
        os.environ["PREFLIGHT_PCB"] = pcb_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if old is None:
            os.environ.pop("PREFLIGHT_PCB", None)
        else:
            os.environ["PREFLIGHT_PCB"] = old
        cases.append(("⑥ 板文件被改一个字节 ⇒ P6 红", ok is False))

        # ⑥b ★★ISS-283 · ⑩-b: 网表被改一个字节 ⇒ P6 红 (★新口径: 台账登记 vs 盘上·不是 vs 写死基线★) ★
        net_src = protected_map()["网表"][0]
        net_bad = os.path.join(tmpd, "netlist_bad.csv")
        t = read_text(net_src)
        open(net_bad, "w", encoding="utf-8").write(t + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("PREFLIGHT_NETLIST")
        os.environ["PREFLIGHT_NETLIST"] = net_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if old is None:
            os.environ.pop("PREFLIGHT_NETLIST", None)
        else:
            os.environ["PREFLIGHT_NETLIST"] = old
        cases.append(("⑥b 网表被改一个字节 ⇒ P6 红 (★台账登记 ≠ 盘上★)", ok is False))

        # ⑥c ★★ISS-283 · ⑩-b: 落表台账里【查不到该文件的登记】⇒ P6 红 (★fail-closed·不许猜★) ★
        #   ★★cont2 修: 旧写法的过滤条件是 `A not in l or B not in l` ⇒ 【逻辑取反】⇒
        #      台账里没有任何一行同时含 A 和 B ⇒ 【一行都没删掉】⇒ 台账原样 ⇒ P6 仍绿 ⇒ 用例假失败★
        #      ⇒ 现在改成【真的把网表的登记行删掉】(★台账里所有链都删 ⇒ 「查不到」无歧义★) ★
        led_src = os.path.join(PROJ, "HW", "SCHEMATIC_LANDING_V1_LANDED.md")
        led_bad = os.path.join(tmpd, "ledger_bad.md")
        lt = read_text(led_src)
        lt_lines = lt.split("\n")
        lt2_lines = [l for l in lt_lines if "`HW/netlist_v1.csv`**" not in l]
        n_removed = len(lt_lines) - len(lt2_lines)
        if n_removed < 1:
            print("  ⚠ ⑥c ★★突变没咬到台账里网表的登记行 ⇒ 用例自身没写完★")
        open(led_bad, "w", encoding="utf-8").write("\n".join(lt2_lines))
        oldl = os.environ.get("LANDING_LEDGER")
        os.environ["LANDING_LEDGER"] = led_bad
        ok, _ = evaluate(checklist_path, only="P6")
        if oldl is None:
            os.environ.pop("LANDING_LEDGER", None)
        else:
            os.environ["LANDING_LEDGER"] = oldl
        cases.append(("⑥c 落表台账里【所有链】都查不到网表的登记 ⇒ P6 红 (★fail-closed★)", ok is False,
                      "★自证改动★: 台账删掉 %d 行网表登记 (md5 %s → %s)"
                      % (n_removed, md5(led_src)[:8], md5(led_bad)[:8])))

        # ⑥d (★cont2 增★): 落表台账里【最新一条链】的 BOM 登记【新 md5 缺了】⇒ 四项不齐 ⇒ P6 红
        #   ★★反向用例只许增不许减★ ⇒ 这条把 C6 那边的「四项不齐」也搬到 P6 侧测一遍 ★
        led_bad2 = os.path.join(tmpd, "ledger_bad2.md")
        ll = read_text(led_src).split("\n")
        heads = [i for i, l in enumerate(ll) if l.startswith("## ")]
        n_fixed = 0
        if heads:
            s0 = heads[-1]
            secs = [i for i in range(s0, len(ll))
                    if ll[i].startswith("### ") and "16.2" in ll[i] and "新旧 md5" in ll[i]]
            if secs:
                s = secs[-1]
                for i in range(s + 1, len(ll)):
                    if ll[i].startswith("### ") or ll[i].startswith("## "):
                        break
                    if ll[i].startswith("|") and "`HW/BOM_v1.csv`" in ll[i]:
                        parts = ll[i].split("|")
                        if len(parts) >= 4:
                            parts[3] = " `★(缺)★` "
                            ll[i] = "|".join(parts)
                            n_fixed += 1
                        break
        open(led_bad2, "w", encoding="utf-8").write("\n".join(ll))
        oldl = os.environ.get("LANDING_LEDGER")
        os.environ["LANDING_LEDGER"] = led_bad2
        ok, _ = evaluate(checklist_path, only="P6")
        if oldl is None:
            os.environ.pop("LANDING_LEDGER", None)
        else:
            os.environ["LANDING_LEDGER"] = oldl
        cases.append(("⑥d 落表台账【最新一条链】里 BOM 的【新 md5】缺了 ⇒ P6 红 (★四项不齐★)", ok is False,
                      "★自证改动★: 台账改 %d 行 BOM 登记 (md5 %s → %s)"
                      % (n_fixed, md5(led_src)[:8], md5(led_bad2)[:8])))

        # ⑦ 把 source_iss 改成来源不明的 ⇒ P4 红 (反向: 不许有来源不明的项)
        p = os.path.join(tmpd, "v7.md")
        def mut7(d):
            next(i for i in d["items"] if i["id"] == "B05_U_EN_SW_VALUE")["source_iss"] = "ISS-999"
        write_variant(checklist_path, p, mut7)
        ok, _ = evaluate(p, only="P4")
        cases.append(("⑦ source_iss 改成来源不明 (ISS-999) ⇒ P4 红", ok is False))

        # ★基线: 真盘必须全绿 (否则上面那些红没意义)
        ok0, _ = evaluate(checklist_path)
        cases.append(("★基线: 真盘 P1~P6 全绿", ok0 is True))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 78)
    print("  ISS-277 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 78)
    bad = 0
    for item in cases:
        name, caught = item[0], item[1]
        proof = item[2] if len(item) > 2 else None
        mark = "✔" if caught else "✘"
        if not caught:
            bad += 1
        print("  %s  %s" % (mark, name))
        if proof:
            print("       %s" % proof)
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
    print("  ISS-277 · 板侧漏项覆盖度闸 (★P1 清单 / P2 归属步 / P3 判据真命令 / P4 覆盖度 / P5 现状 / P6 受保护 ★)")
    print("=" * 78)
    ok, lines = evaluate(args.checklist)
    for l in lines:
        print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★")
        return 0
    print("  ❌ rc=1: ★★有板侧项漏在清单外, 或清单现状已过期 ⇒ 那一趟会漏做 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
