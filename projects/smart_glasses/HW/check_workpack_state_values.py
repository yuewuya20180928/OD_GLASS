#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-289 · 「作业包 + 清单页里的现状值 == 盘面实测」漂移闸
=================================================================================================
派活: state/dispatch_briefs/ISS-289_hw_workpack_state_values_reconcile.md (项目总工 2026-11-17 14:3x)

★**本闸守的是【文档里的现状值还成不成立】, 不是板** ⇒ ★**零写板 · 零落表 · 零改生成器代码** ★

★**为什么要有这道闸 (★病灶原话★)** ★
    ★**S7 的验收目标是「零标记数 = 0」⇒ 若照作业包里写死的「43」走, 而盘上真值是 40 ⇒
    要么 S7 验收假红, 要么为了凑够 43 去把刚落表的三颗必装又标回 DNP ⇒ 那等于把老板拍板 undo** ★
    ⇒ ★**⇒ 凡是「写死的现状数字」都必须【跟着盘面走】, 而「跟没跟」必须有机器判据** ★
    ⇒ ★**★不许只加一条 DNP 探针 (★那等于下次落表又漂别的★)** ★

七条判据:
  V1 登记表结构    : 两份文档各有一份可解析的 `state_baseline` JSON 块 + 字段齐全 + ★两份口径逐字一致★
  V2 追加式自证    : 每条的 `anchor` (老字原句) 必须在它声明的文档里找得到 ⇒ ★老字不许删★
  V3 订正块在位    : 每条的 `correction_anchor` + `fresh` (订正后的现值句) 必须在那份文档里
  V4 现状值 == 实测: 实跑探针 ⇒ 抽到的值必须 == 期望值, 且期望值必须出现在 `fresh` 里
  V5 类别覆盖      : ★7 个必备类别每类至少一条 ⇒ ★只加一条 DNP 探针 = 红★
  V6 受保护 5 件   : 板 / .kicad_pro 写死基线 · 网表/脚表/BOM ★走落表台账为准, 不写死★
  V7 探针真实性    : 探针必须是盘上真实存在的脚本 · 不许 echo/true · 类别之间不许共用同一个测量源

★**V5 的七个必备类别 (★缺任何一类即红★)** ★
    dnp_zero_mark / footprint_count / dnp_token_count / defect_count /
    md5_baseline / copper_and_frame / ref_suffix

★**★「期望值」写在文档里, 不写死在闸里 ⇒ 文档漂了当场红; 而 md5 基线的【取值来源】是落表台账
    (★`HW/landing_md5.py`★) ⇒ 落表一次, 闸自己就知道新基线是多少, 不必改闸★** ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_workpack_state_values.py             # 主模式
  python3 HW/check_workpack_state_values.py --selftest  # 反向用例 (>=6 条, 每条自证改到了目标)
  ★自检用 env 覆盖★: WP_WORKPACKET / WP_CHECKLIST / WP_PCB / WP_PRO /
                     WP_NETLIST / WP_PINS / WP_BOM
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
sys.path.insert(0, HERE)
import landing_md5                                          # noqa: E402
# ★★ISS-297 · 2026-11-17 20:5x (hw-lead): HW 侧「合法改板」通道 (★共用判决库·不许自己再写一份★)
import board_reboard                                          # noqa: E402

DOC_FILES = {
    "workpacket": ("HW/PCB/BOARD_ONEPASS_WORKPACKET.md", "WP_WORKPACKET"),
    "checklist": ("HW/PCB/BOARD_ONEPASS_PREFLIGHT.md", "WP_CHECKLIST"),
}

PROTECTED = {
    "板": ("HW/PCB/demo_mainboard.kicad_pcb", "WP_PCB",
           "611b869e13518c3c023fb178f91a0075"),
    ".kicad_pro": ("HW/PCB/demo_mainboard.kicad_pro", "WP_PRO",
                   "3e504d2be83152e337949723e909be1b"),
    "网表": ("HW/netlist_v1.csv", "WP_NETLIST", None),
    "脚表": ("HW/netlist_v1_pins.csv", "WP_PINS", None),
    "BOM": ("HW/BOM_v1.csv", "WP_BOM", None),
}

# ★V5 的七个必备类别 (★少一类即红 ★) ★
MANDATORY_CATEGORIES = ("dnp_zero_mark", "footprint_count", "dnp_token_count",
                        "defect_count", "md5_baseline", "copper_and_frame",
                        "ref_suffix")

REQUIRED_FIELDS = ("id", "category", "doc", "anchor", "correction_anchor",
                   "fresh", "probe", "probe_regex")

# ★V7: 探针不许是「空转」命令 ★
BANNED_PROBE_HEADS = ("echo", "printf", "true", "false", ":", "cat", "head", "tail",
                      "ls", "wc", "date", "sleep")
ALLOWED_PROBE_HEADS = ("python3", "bash", "md5sum", "sh")

_CACHE = {}


def doc_path(key: str) -> str:
    rel, env = DOC_FILES[key]
    return os.environ.get(env) or os.path.join(PROJ, rel)


def protected_path(name: str) -> str:
    rel, env, _ = PROTECTED[name]
    return os.environ.get(env) or os.path.join(PROJ, rel)


def md5(path: str) -> str:
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def sh(cmd, timeout=900):
    key = " ".join(cmd)
    if key in _CACHE:
        return _CACHE[key]
    try:
        r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
        out = (r.stdout or b"").decode("utf-8", "replace")
        rc = r.returncode
    except Exception as e:                                    # pragma: no cover
        out, rc = "EXC: %s" % e, -1
    _CACHE[key] = (rc, out)
    return rc, out


def find_state_block(txt: str):
    """★找出文档里的 `state_baseline` JSON 块 ⇒ (data, start, end) ★"""
    for m in re.finditer(r"```json\s*\n(\{.*?\n\})\s*\n```", txt, re.S):
        try:
            data = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(data, dict) and "state_baseline" in data:
            return data, m.start(), m.end()
    return None, -1, -1


def doc_body(txt: str) -> str:
    """★正文 (★把 state_baseline 登记表块挖掉 ★)

    ★**为什么必须挖掉**: 登记表里本身就写着 anchor / fresh ⇒ 不挖掉的话
    「老字还在吗」会被登记表自己回答 (★恒真 ⇒ 闸是假的★) ★
    """
    _data, s, e = find_state_block(txt)
    if s < 0:
        return txt
    return txt[:s] + txt[e:]


def entries_of(data):
    if not data:
        return []
    sb = data.get("state_baseline")
    if isinstance(sb, dict):
        return list(sb.get("entries") or [])
    if isinstance(sb, list):
        return list(sb)
    return []


def numeric_present(value: str, text: str) -> bool:
    """★期望值必须出现在 fresh 里 (★纯数字用严格边界, 免得 `F2` 里的 2 冒充★) ★"""
    if value.isdigit():
        pat = r"(?<![0-9A-Za-z_.])" + re.escape(value) + r"(?![0-9A-Za-z_.])"
        return bool(re.search(pat, text))
    return value in text


def expected_of(entry):
    """★期望值: 普通条目写在文档里; md5 基线条目走落表台账 (★不写死★) ★"""
    mode = entry.get("expect_mode", "probe")
    if mode == "ledger":
        rel = entry.get("expect_target", "")
        want, issue, why = landing_md5.registered_md5(PROJ, rel)
        return want, issue, why
    return str(entry.get("expect", "")), "", ""


# ==============================================================================
# 七条判据
# ==============================================================================
def check_V1(blocks):
    ok, bad, good = True, [], []
    for key in DOC_FILES:
        if key not in blocks:
            ok = False
            bad.append("%s 不存在或读不出" % key)
            continue
        data, txt = blocks[key]
        if data is None:
            ok = False
            bad.append("%s 里找不到可解析的 state_baseline JSON 块" % key)
            continue
        ents = entries_of(data)
        if not ents:
            ok = False
            bad.append("%s 的 state_baseline 里没有 entries" % key)
            continue
        for e in ents:
            miss = [f for f in REQUIRED_FIELDS if f not in e]
            empty = [f for f in REQUIRED_FIELDS if f in e and not str(e[f]).strip()]
            if miss or empty:
                ok = False
                bad.append("%s: id=%s 缺字段=%s 空字段=%s"
                           % (key, e.get("id", "?"), miss, empty))
            if e.get("expect_mode") != "ledger" and "expect" not in e:
                ok = False
                bad.append("%s: id=%s 没有 expect (★或用 expect_mode=ledger + expect_target★)"
                           % (key, e.get("id")))
            if e.get("expect_mode") == "ledger" and not e.get("expect_target"):
                ok = False
                bad.append("%s: id=%s 声明 ledger 模式但没有 expect_target" % (key, e.get("id")))
        good.append("     ✔ %s 的 state_baseline 可解析 (%d 条)" % (key, len(ents)))
    # ★两份文档的口径必须逐字一致 (★不许一份订了另一份没订★) ★
    if len(blocks) == len(DOC_FILES):
        pass
    if len(blocks) == len(DOC_FILES):
        ids = {}
        for key, (data, _txt) in blocks.items():
            ids[key] = {str(e.get("id")): e for e in entries_of(data)}
        ka, kb = sorted(ids)
        only_a = sorted(set(ids[ka]) - set(ids[kb]))
        only_b = sorted(set(ids[kb]) - set(ids[ka]))
        if only_a or only_b:
            ok = False
            bad.append("两份文档的条目 id 集合不一致: %s 只在 %s / %s 只在 %s"
                       % (only_a, ka, only_b, kb))
        else:
            diff = []
            for i in sorted(ids[ka]):
                for f in ("category", "doc", "anchor", "correction_anchor", "fresh",
                          "expect", "expect_mode", "expect_target", "probe_regex"):
                    if ids[ka][i].get(f) != ids[kb][i].get(f):
                        diff.append("%s.%s" % (i, f))
            if diff:
                ok = False
                bad.append("两份文档同一条目的口径不一致: %s" % diff[:12])
            else:
                good.append("     ✔ 两份文档的 %d 条登记逐字一致 (★口径不许分叉★)" % len(ids[ka]))
    return ok, ["     两份文档的登记表结构: %s" % ("✔" if ok else "❌")] + good + \
        ["     ❌ %s" % b for b in bad]


def check_V2(ents_by_id, blocks):
    ok, bad, good = True, [], []
    for e in ents_by_id.values():
        key = str(e.get("doc", ""))
        if key not in blocks:
            ok = False
            bad.append("id=%s 的 doc=%r 不是已登记的文档" % (e.get("id"), key))
            continue
        txt = blocks[key][1]
        body = doc_body(txt)
        a = str(e.get("anchor", ""))
        if a and a not in body:
            ok = False
            bad.append("id=%s 的老字原句不在 %s 里 ⇒ ★订正不是追加式的, 或者老字被改了★"
                       % (e.get("id"), key))
    return ok, ["     老字 (anchor) 逐条还在 (★追加式自证★): %s" % ("✔" if ok else "❌")] + \
        (["     ✔ %d 条老字原句全部在位" % len(ents_by_id)] if ok else []) + \
        ["     ❌ %s" % b for b in bad]


def check_V3(ents_by_id, blocks):
    ok, bad, good = True, [], []
    for e in ents_by_id.values():
        key = str(e.get("doc", ""))
        if key not in blocks:
            ok = False
            bad.append("id=%s 的 doc=%r 不是已登记的文档" % (e.get("id"), key))
            continue
        txt = blocks[key][1]
        body = doc_body(txt)
        ca = str(e.get("correction_anchor", ""))
        pos = body.find(ca) if ca else -1
        if pos < 0:
            ok = False
            bad.append("id=%s 的订正块锚点不在 %s 里 ⇒ 订正块不在位" % (e.get("id"), key))
            continue
        fresh = str(e.get("fresh", ""))
        if not fresh:
            ok = False
            bad.append("id=%s 的 fresh 为空" % e.get("id"))
            continue
        tail = body[pos:pos + 60000]
        if fresh not in tail:
            ok = False
            bad.append("id=%s 的订正块里没有 fresh 原句 ⇒ 订正没带现值" % e.get("id"))
    return ok, ["     订正块在位 + 订正句自带现值: %s" % ("✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_V4(ents_by_id, blocks):
    ok, bad, good = True, [], []
    if True:
        for e in ents_by_id.values():
            cmd = e.get("probe")
            if not isinstance(cmd, list) or not cmd:
                ok = False
                bad.append("id=%s 的 probe 不是命令数组" % e.get("id"))
                continue
            rc, out = sh(cmd)
            m = re.search(str(e.get("probe_regex", "")), out)
            if not m:
                ok = False
                bad.append("id=%s 的探针没抽到值 (rc=%d): %s" % (e.get("id"), rc, e.get("probe_regex")))
                continue
            val = m.group(1)
            want, issue, why = expected_of(e)
            if not want:
                ok = False
                bad.append("id=%s 取不到期望值: %s" % (e.get("id"), why or issue))
                continue
            if val != want:
                ok = False
                bad.append("id=%s: 盘面实测 = %r, 期望 = %r ⇒ 现状值漂了" % (e.get("id"), val, want))
                continue
            fresh = str(e.get("fresh", ""))
            if not numeric_present(want, fresh):
                ok = False
                bad.append("id=%s: 实测值 %r 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面"
                           % (e.get("id"), want))
                continue
            good.append("     ✔ %-26s 实测 %-34s == 期望" % (str(e.get("id")), val))
    return ok, ["     现状值 == 盘面实测 (★实跑探针★): %s" % ("✔" if ok else "❌")] + good + \
        ["     ❌ %s" % b for b in bad]


def check_V5(ents_by_id, blocks):
    ok, bad, good = True, [], []
    for key in DOC_FILES:
        if key not in blocks:
            continue
        cats = {}
        for e in entries_of(blocks[key][0]):
            cats.setdefault(str(e.get("category")), []).append(str(e.get("id")))
        miss = [c for c in MANDATORY_CATEGORIES if c not in cats]
        if miss:
            ok = False
            bad.append("★%s 这份文档缺 %d 个必备类别 ⇒ ★只加一条 DNP 探针 = 不合格★: %s"
                       % (key, len(miss), miss))
        else:
            good.append("     ✔ %-11s 七类齐全 (%d 条登记)" % (key, sum(len(v) for v in cats.values())))
    return ok, ["     七个必备类别覆盖 (★两份文档各须齐全 · 不许只加一条 DNP 探针★): %s"
                % ("✔" if ok else "❌")] + good + ["     ❌ %s" % b for b in bad]


def check_V6():
    ok, bad, good = True, [], []
    # ★★ISS-297 · 2026-11-17 20:5x (hw-lead): 板 / `.kicad_pro` 两件改走【落表台账链头 + 合法改板通道】★★
    #   ★判据方向一字未变 (★盘上 ≠ 判决源 ⇒ 红★); ★变的只是【判决源】: 写死常量 → 落表台账链头 ★
    #   ★`reboard: null` (还没发生过合法改板) ⇒ ★仍按纯 md5 硬保护判 (盘上 ≠ 基线 ⇒ 红)★ ★
    #   ★fail-closed 三条一条不许动 (★链头不唯一 / 链断 / 链头无单号 ⇒ 仍红★) ★
    heads = {}
    for name, rel in (("板", board_reboard.PCB_REL), (".kicad_pro", board_reboard.PRO_REL)):
        path = protected_path(name)
        base = PROTECTED[name][2]
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        res = board_reboard.check_file(PROJ, rel, path, base, md5fn=md5)
        heads[rel] = res.get("head")
        if res["ok"]:
            good.append("     ✔ %s" % res["msg"])
        else:
            ok = False
            for e in res["errs"]:
                bad.append("%s: %s" % (name, e))
    # ★同组覆盖: 一次合法改板必须覆盖同组全部件 (★只来一条记录 ⇒ 红★) ★
    for e in board_reboard.check_trip_coverage(board_reboard.ledger_text(PROJ), heads):
        ok = False
        bad.append(e)
    for name, (rel, _env, base) in PROTECTED.items():
        if name in ("板", ".kicad_pro"):
            continue
        path = protected_path(name)
        if not os.path.exists(path):
            ok = False
            bad.append("%s 不存在: %s" % (name, path))
            continue
        cur = md5(path)
        if base is None:
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


def check_V7(ents_by_id, blocks):
    ok, bad, good = True, [], []
    srcs = {}
    if True:
        for e in ents_by_id.values():
            cmd = e.get("probe")
            if not isinstance(cmd, list) or not cmd:
                ok = False
                bad.append("id=%s 的 probe 缺失" % e.get("id"))
                continue
            head = str(cmd[0])
            if head in BANNED_PROBE_HEADS:
                ok = False
                bad.append("id=%s 的探针是空转命令 (%s) ⇒ 判据不成立" % (e.get("id"), head))
                continue
            if head not in ALLOWED_PROBE_HEADS:
                ok = False
                bad.append("id=%s 的探针头 %r 不在允许清单里" % (e.get("id"), head))
                continue
            for tok in cmd[1:]:
                if re.search(r"\.(py|sh)$", str(tok)):
                    p = str(tok) if os.path.isabs(str(tok)) else os.path.join(PROJ, str(tok))
                    if not os.path.exists(p):
                        ok = False
                        bad.append("id=%s 的探针引用了不存在的文件: %s" % (e.get("id"), tok))
            srcs.setdefault(str(e.get("category")), set()).add(" ".join(cmd))
    for c, s in sorted(srcs.items()):
        good.append("     ✔ %-18s 探针源 %d 个" % (c, len(s)))
    if len({tuple(sorted(v)) for v in srcs.values()}) < 3:
        ok = False
        bad.append("★所有类别只用了 2 个以内的测量源 ⇒ 七类现状值其实是同一个数换皮★")
    return ok, ["     探针真实性 + 测量源多样性: %s" % ("✔" if ok else "❌")] + good + \
        ["     ❌ %s" % b for b in bad]


CHECKS = ("V1", "V2", "V3", "V4", "V5", "V6", "V7")


def load_docs():
    """★⇒ (登记条目总表 by id, 各文档的块) ★

    ★**两份文档里放的是同一份登记表 (★同源★) ⇒ 取并集按 id 去重;
      每一条按它自己的 `doc` 字段去对应文档里查** ★
    """
    ents_by_id = {}
    blocks = {}
    for key in DOC_FILES:
        p = doc_path(key)
        if not os.path.exists(p):
            continue
        txt = read_text(p)
        data, _s, _e = find_state_block(txt)
        blocks[key] = (data, txt)
        for e in entries_of(data):
            eid = str(e.get("id"))
            if eid not in ents_by_id:
                ents_by_id[eid] = e
    return ents_by_id, blocks


def evaluate(only=None):
    ents_by_id, blocks = load_docs()
    lines, ok = [], True
    fns = {
        "V1": lambda: check_V1(blocks),
        "V2": lambda: check_V2(ents_by_id, blocks),
        "V3": lambda: check_V3(ents_by_id, blocks),
        "V4": lambda: check_V4(ents_by_id, blocks),
        "V5": lambda: check_V5(ents_by_id, blocks),
        "V6": lambda: check_V6(),
        "V7": lambda: check_V7(ents_by_id, blocks),
    }
    for cid in CHECKS:
        if only and cid != only:
            continue
        r_ok, r_lines = fns[cid]()
        lines.append("  %s  %s" % ("OK " if r_ok else "FAIL", cid))
        lines.extend(r_lines)
        ok = ok and r_ok
    return ok, lines


# ==============================================================================
# --selftest
# ==============================================================================
def write_variant(src_path, dst_path, mutate):
    """★把文档里的 state_baseline JSON 块换掉, 写一份副本 (★反向用例用★) ★"""
    txt = read_text(src_path)
    data, s, e = find_state_block(txt)
    if data is None:
        raise SystemExit("selftest: %s 里没有 state_baseline 块" % src_path)
    mutate(data)
    new_block = "```json\n%s\n```" % json.dumps(data, ensure_ascii=False, indent=2)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(txt[:s] + new_block + txt[e:])
    return dst_path


def run_selftest():
    tmpd = tempfile.mkdtemp(prefix="iss289_selftest_")
    cases = []
    wp = doc_path("workpacket")
    cl = doc_path("checklist")
    try:
        # ① 把某条的期望值改错 ⇒ V4 红
        p = os.path.join(tmpd, "v1.md")
        def mut1(d):
            for e in entries_of(d):
                if e.get("id") == "W02_S7_QUANT_ZERO":
                    e["expect"] = "39"
        write_variant(wp, p, mut1)
        ok, _ = evaluate_only(p, cl, "V4")
        cases.append(("① 把 W02 的期望值改成 39 ⇒ V4 红", ok is False))

        # ② 删掉某一类 (封装数) ⇒ V5 红 (★只加 DNP 一条 = 不合格★)
        p = os.path.join(tmpd, "v2.md")
        def mut2(d):
            d["state_baseline"]["entries"] = [
                e for e in entries_of(d) if e.get("category") != "footprint_count"]
        write_variant(wp, p, mut2)
        ok, _ = evaluate_only(p, cl, "V5")
        cases.append(("② 删掉「封装数」这一类 ⇒ V5 红 (★不许只加一条 DNP 探针★)", ok is False))

        # ③ 改老字 anchor ⇒ V2 红 (★老字被改 = 不是追加式★)
        p = os.path.join(tmpd, "v3.md")
        def mut3(d):
            for e in entries_of(d):
                if e.get("id") == "W01_S7_HEADING":
                    e["anchor"] = "★老字被改过了★"
        write_variant(wp, p, mut3)
        ok, _ = evaluate_only(p, cl, "V2")
        cases.append(("③ 把老字 anchor 改掉 ⇒ V2 红 (★追加式自证★)", ok is False))

        # ④ 订正块锚点指向不存在的地方 ⇒ V3 红
        p = os.path.join(tmpd, "v4.md")
        def mut4(d):
            for e in entries_of(d):
                if e.get("id") == "W03_S7_QUANT_TOKEN":
                    e["correction_anchor"] = "★没有这个订正块★"
        write_variant(wp, p, mut4)
        ok, _ = evaluate_only(p, cl, "V3")
        cases.append(("④ 把订正块锚点改成不存在的 ⇒ V3 红", ok is False))

        # ⑤ 抽掉一个字段 ⇒ V1 红
        p = os.path.join(tmpd, "v5.md")
        def mut5(d):
            for e in entries_of(d):
                if e.get("id") == "W09_SAME_PAD_NET":
                    e.pop("probe_regex")
        write_variant(wp, p, mut5)
        ok, _ = evaluate_only(p, cl, "V1")
        cases.append(("⑤ 抽掉一条的 probe_regex ⇒ V1 红", ok is False))

        # ⑥ 两份文档口径分叉 (清单页少一条) ⇒ V1 红
        p = os.path.join(tmpd, "v6.md")
        def mut6(d):
            d["state_baseline"]["entries"] = [
                e for e in entries_of(d) if e.get("id") != "C01_B17_ZERO_MARK"]
        write_variant(cl, p, mut6)
        ok, _ = evaluate_only(wp, p, "V1")
        cases.append(("⑥ 清单页少一条 ⇒ V1 红 (★两份口径不许分叉★)", ok is False))

        # ⑦ 只留 DNP 一类 ⇒ V5 红
        p = os.path.join(tmpd, "v7.md")
        def mut7(d):
            d["state_baseline"]["entries"] = [
                e for e in entries_of(d) if e.get("category") == "dnp_zero_mark"]
        write_variant(wp, p, mut7)
        ok, _ = evaluate_only(p, cl, "V5")
        cases.append(("⑦ 只留 DNP 一类 ⇒ V5 红 (★七类必须齐★)", ok is False))

        # ⑧ 探针指向不存在的脚本 ⇒ V4/V7 红
        p = os.path.join(tmpd, "v8.md")
        def mut8(d):
            for e in entries_of(d):
                if e.get("id") == "W08_PINS_DEFECT":
                    e["probe"] = ["python3", "HW/check_this_does_not_exist_zzz.py"]
        write_variant(wp, p, mut8)
        ok4, _ = evaluate_only(p, cl, "V4")
        ok7, _ = evaluate_only(p, cl, "V7")
        cases.append(("⑧ 探针指向不存在的脚本 ⇒ V4 红 且 V7 红",
                      ok4 is False and ok7 is False))

        # ⑨ 板文件被改一个字节 ⇒ V6 红
        pcb_src = protected_path("板")
        pcb_bad = os.path.join(tmpd, "board_bad.kicad_pcb")
        with open(pcb_bad, "w", encoding="utf-8") as f:
            f.write(read_text(pcb_src) + "\n; ★selftest 注入的一行 ★\n")
        old = os.environ.get("WP_PCB")
        os.environ["WP_PCB"] = pcb_bad
        ok, _ = evaluate_only(wp, cl, "V6")
        if old is None:
            os.environ.pop("WP_PCB", None)
        else:
            os.environ["WP_PCB"] = old
        cases.append(("⑨ 板文件被改一个字节 ⇒ V6 红", ok is False))

        # ⑩ 基线: 真盘必须全绿 (否则上面那些红没意义)
        ok0, _ = evaluate()
        cases.append(("★基线: 真盘 V1~V7 全绿", ok0 is True))

        # ── ★★ISS-297 · ⑯ 「合法改板」通道的反向用例 (★沙盒跑·真盘零写·判决源 = 落表台账链头★) ──
        #   ★机制: `HW/board_reboard.py` 的 CASES (★照 ISS-284 已跑通的口径·不许自创★) ★
        #   ★每条都【真跑本闸的 V6】(★受保护 5 件指向沙盒副本★) ⇒ 判据变红/变绿都必须是本闸自己的结论 ★
        ch_cases = []

        def ch_prepare(sb):
            for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
                src = os.path.join(PROJ, rel)
                d = os.path.join(sb, rel)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(src, d)

        def ch_judge(sb):
            old = {k: os.environ.get(k) for k in
                   ("WP_PCB", "WP_PRO", "WP_NETLIST", "WP_PINS", "WP_BOM")}
            try:
                os.environ["WP_PCB"] = os.path.join(sb, board_reboard.PCB_REL)
                os.environ["WP_PRO"] = os.path.join(sb, board_reboard.PRO_REL)
                os.environ["WP_NETLIST"] = os.path.join(sb, "HW/netlist_v1.csv")
                os.environ["WP_PINS"] = os.path.join(sb, "HW/netlist_v1_pins.csv")
                os.environ["WP_BOM"] = os.path.join(sb, "HW/BOM_v1.csv")
                ok, lines = evaluate_only(wp, cl, "V6")
                return ok, ("★本闸 V6 绿? %s★ · %s" % ("是" if ok else "否", " | ".join(lines)))
            finally:
                for k, v in old.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

        for _name, _exp, _got, _note in board_reboard.run_cases(
                PROJ, os.path.join(tmpd, "iss297_channel"), ch_judge, prepare=ch_prepare):
            ch_cases.append(("★ISS-297★ " + _name, _exp == _got, _note))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 78)
    print("  ISS-289 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 78)
    bad = 0
    for item in cases:
        name, caught = item[0], item[1]
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

    # ★★ISS-297 · ⑯ 「合法改板」通道反向用例 (★10 条·判决源 = 落表台账链头 + 四项原子映射★) ★★
    print("=" * 78)
    print("  ★★ISS-297 · ⑯ 「合法改板」通道反向用例 (%d 条·判决源 = 落表台账链头 + 四项原子映射★)" % len(ch_cases))
    print("=" * 78)
    bad_ch = 0
    for name, passed, info in ch_cases:
        if not passed:
            bad_ch += 1
        print("  %s %s" % ("✔" if passed else "✘", name))
        print("       %s" % info)
    print("-" * 78)
    print("  ⇒ 通道用例: %d/%d 通过 · 合计 %d/%d"
          % (len(ch_cases) - bad_ch, len(ch_cases),
             (len(cases) - bad) + (len(ch_cases) - bad_ch), len(cases) + len(ch_cases)))
    if bad_ch:
        print("  ❌ 有通道反向用例没抓到 ⇒ 通道判据是摆设 ⇒ 闸不算数")
        return 1
    print("  ✅ 通道反向用例全抓到 ⇒ 「合法改板」当天不会再集体假红, 且没背书照样红★")
    return 0


def evaluate_only(wp_path, cl_path, only):
    """★selftest 专用: 临时把两份文档指到副本上跑单条判据 ★"""
    old_wp, old_cl = os.environ.get("WP_WORKPACKET"), os.environ.get("WP_CHECKLIST")
    os.environ["WP_WORKPACKET"] = wp_path
    os.environ["WP_CHECKLIST"] = cl_path
    try:
        return evaluate(only=only)
    finally:
        if old_wp is None:
            os.environ.pop("WP_WORKPACKET", None)
        else:
            os.environ["WP_WORKPACKET"] = old_wp
        if old_cl is None:
            os.environ.pop("WP_CHECKLIST", None)
        else:
            os.environ["WP_CHECKLIST"] = old_cl


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    for key, (rel, _env) in DOC_FILES.items():
        if not os.path.exists(doc_path(key)):
            print("❌ 用法错: 找不到 %s (%s)" % (key, rel))
            return 2

    if args.selftest:
        return run_selftest()

    print("=" * 78)
    print("  ISS-289 · 「作业包 + 清单页里的现状值 == 盘面实测」漂移闸")
    print("  (★V1 结构 / V2 追加式 / V3 订正块 / V4 现状值==实测 / V5 七类覆盖 / V6 受保护 / V7 探针真实★)")
    print("=" * 78)
    ok, lines = evaluate()
    for l in lines:
        if l.strip():
            print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★两份文档里的现状值 == 盘面实测, 且七类判据齐 ★★")
        return 0
    print("  ❌ rc=1: ★★文档里的现状值漂了 / 订正没到位 / 判据不齐 ⇒ 那一趟会照着过期数字验收 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
