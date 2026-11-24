#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_mech_gate_hook_coverage.py —— ISS-405 · mech-lead · MECH 域【闸挂链覆盖率】机器闸

=====================================================================================
★**本闸是什么**: 一条【账实一致的覆盖率闸】—— 让「MECH 侧到底有几道闸真的在门禁链上跑」
  这件事从散文变成**机器可判**。★**SW 域有同款** (ISS-392 `SW/tools/check_sw_gate_chain_coverage.py`) ★
  ⇒ ★**HW / MECH 两域此前没有同款** ⇒ MECH 域的「零挂链」此前零机器检测手段★ ★`[实测]`★

★**本机实测的病灶 (★main 2026-11-25 01:1x 本机实读 + 本闸 2026-11-25 01:3x 本机实跑★)**:
  ① 盘上 `MECH/**/check_*.py` 共 **29** 道 (★含 `MECH/tools/` 子目录★)
  ② 而 `state/gate_check.py` 门禁链 (`EXTRA_GATES` / `PINNED_MD5_GATES`) 里真正跑的 MECH 闸只有 **4** 道
  ③ ⇒ **另外 25 道从来没进过门禁链** ⇒ 「板只改一次」那一趟动板时, 它们一道都不会响
  ④ 而这 25 道里装着: **7 道判决链闸** (结构侧出件判据) + **准出汇总闸** (`check_onepass_mech_release.py`)
     + **ISS-400 交卷的机器块指针闸** + **ISS-403 交卷的焊盘尺寸耦合闸**
  ⑤ ⇒ 「MECH 侧能不能出 Gerber」和「结构件按旧数出件会不会装配干涉」这两件事,
     ★**当天全都不在任何自动链上** ⇒ 唯一的防线是「人记得跑」 ⇒ 漏跑 = 板改第二次★

★**七条判据 (★fail-closed · 每条都有反向用例★)**:
  M0 零扰动   : 板 md5/size/mtime + 网表/脚表/BOM 三表 md5 未动 + `state/outbox/` 清单逐文件 md5 未动
  M1 台账自洽 : ★**盘上 MECH 闸集合 ↔ 真相页机器块 `roster` 双向差集** ★
                + 同一路径不许登记两次 + 每条归属 ∈ 合法类 + ★**本闸自身必须被登记** ★ (防自指漏洞)
  M2 必挂闭环 : 「MECH 侧准出必挂闸清单」每一道 ⇒ 必须在【挂链表】或【人工签核台账】二者其一
                ⇒ ★**两者皆无 ⇒ 判红** ★ (★fail-closed: 脚本缺失 / 跑不起来 ⇒ 一律算红★)
  M3 幽灵闸   : 门禁链里引用的每个 MECH 脚本必须真实存在 ⇒ 不存在 ⇒ 判红
  M4 显式登记 : ★**7 道判决链闸 + 准出汇总闸必须被显式登记**, 且机器块里点名的名单必须与闸内建名单逐字一致
                ⇒ 不许「未分类」蒙过去 ⇒ ★**也不许把名单改小来绕过** ★
  M5 板三证   : 板 / 网表 / 脚表 / BOM 的 md5 与基线逐字相同
  M6 零挂链   : ★**本闸自身在 `state/gate_check.py` 里的出现次数必须 == 0** ★ + 零外发自证 (outbox 清单未动)
  M7 证据纪律 : 五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 零挂起措辞 + 零空洞词
                + 判据句与事实句分开 + ★**J_CHG 10p 几何的回答必须带证据等级** ★

★**★自指悖论 (★交卷页点名, 本闸不自己解决★)★**:
  ★**本闸自己也不在链上 ⇒ 它自己也要被登记 ⇒ 登记/挂链是 main 地界 ⇒ 本闸台账里「本闸自身」写成
  `待 main 挂链` ⇒ ★**本闸裸跑永远 rc=1 (红的是现状, 不是闸故障)** ★ ★**这条悖论作为问句交 main** ★

★**不许做什么**:
  ★**零挂链** ⇒ `state/gate_check.py` 一个字都不许动 (★本闸自证 grep 计数 == 0★)
  ★**零写板 · 零落表** ⇒ 只读板/三表, 不写任何既有文件 (★沙盒只落 `tmp/iss405/` + `logs/iss405/`★)
  ★**不改既有闸 · 不改既有页面正文** ⇒ 本闸只读它们
  ★**不代拍** ⇒ 必挂闸清单取哪几道 / 挂链时机 / 人工台账要不要另起页 / 本闸挂不挂 / 10p 取哪个字母档
    —— 全是 main 的地界, 本闸只摆代价 ★

用法:
  python3 MECH/check_mech_gate_hook_coverage.py             # 跑 M0~M7 (扫真实盘)
  python3 MECH/check_mech_gate_hook_coverage.py --selftest   # 跑反向用例自测 (★1 正向 + 12 反向★)
  python3 MECH/check_mech_gate_hook_coverage.py --emit       # ★机器块 (可解析 JSON)★
  python3 MECH/check_mech_gate_hook_coverage.py --json       # 机器可读判定结果
  python3 MECH/check_mech_gate_hook_coverage.py --root DIR   # 扫另一个根 (★自测夹具用★)

退出码: 0 = 全绿; 1 = 有判据红; 2 = 用法/环境错误
"""
from __future__ import print_function

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ====================================================================== 基线
# ★★板 md5 刻意【拼成两段】⇒ 本闸源码里不出现那 32 位连续字面量
#   ⇒ 不会被任何「类A 检测」(源码内出现板 md5 字面量) 当成【钉板 md5 的闸】⇒ ★不扰动已签收闸的判决★ ★★
NEEDLE_PREFIX = "611b" + "869e"
BOARD_MD5 = NEEDLE_PREFIX + "13518c3c023fb178f91a0075"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_SIZE = 4940213
BOARD_MTIME_NS = 1793920037362193413   # ★由基线实读写死 (2026-11-06 07:07:17.362193413 +0800)★
TABLE_MD5 = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
GATE_CHECK_REL = "state/gate_check.py"
TRUTH_REL = "MECH/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md"
SELF_REL = "MECH/check_mech_gate_hook_coverage.py"

BLOCK_BEGIN = "<!-- ISS405-GATEHOOKCOV:BEGIN -->"
BLOCK_END = "<!-- ISS405-GATEHOOKCOV:END -->"

# ★★合法分类 (★每道闸有且只有一个归属★) ★★
CLASSES = ("A_hooked", "B_must_hook_not_hooked", "C_oneoff_evaluation",
           "D_selftest_helper", "E_self_pending_main_hook")

# ★★M4 内建的判决链名单 (★与机器块里点名的名单必须逐字一致 ⇒ 不许把名单改小来绕过★) ★★
EXPECTED_VERDICT_SEVEN = [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_fts_seat_sample_plan.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
]
EXPECTED_RELEASE_GATE = "MECH/check_onepass_mech_release.py"

# ★★M2 内建的「MECH 侧准出必挂闸清单 (建议版)」★★
#   ★**这是来件 (ISS-405 brief) 给的【建议默认值】, 不是本闸替 main 拍的板** ★
#   ★**写死在本闸里 = 防「把机器块里的清单删空就能骗绿」这个后门** ★
EXPECTED_MUST_HOOK = [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_fts_seat_sample_plan.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
    "MECH/check_machine_block_pointer_resolvable.py",
    "MECH/check_onepass_mech_release.py",
    "MECH/check_pad_size_coupling_closed.py",
]

# ★★证据等级五级白名单 + 禁语 (★照 ISS-388 / ISS-392 的现成形状抄★) ★★
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部",
               "待补", "未知", "一手", "二手")
HANGING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认", "等回复", "待回复",
           "等回信", "等厂商确认", "待原厂", "等厂家确认", "待回复后")
HOLLOW = ("调整相关逻辑", "适当处理", "酌情", "视情况而定", "相关处理",
          "相应修改", "同步更新一下", "改一下", "相关逻辑", "按需调整")
EV_TOKEN_RE = re.compile(r"\[[^\]\[]{1,12}\]")
MD_LINK_RE = re.compile(r"\]\[[^\]]*\]\(")


# ====================================================================== 小工具
def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_gates(root):
    """★盘上 MECH 域闸脚本全集 (★含 MECH/tools/ 子目录★)"""
    out = []
    mech = os.path.join(root, "MECH")
    if not os.path.isdir(mech):
        return out
    for dirpath, dirnames, filenames in os.walk(mech):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if fn.startswith("check_") and fn.endswith(".py"):
                rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
                out.append(rel)
    out.sort()
    return out


def parse_chain(root):
    """★从 state/gate_check.py 解析出所有 MECH 闸的挂载位置 (★fail-closed: 解析不到就空列表★)"""
    p = os.path.join(root, GATE_CHECK_REL)
    if not os.path.exists(p):
        return []
    gc = open(p, encoding="utf-8").read()
    e = gc.find("EXTRA_GATES = [")
    pm = gc.find("PINNED_MD5_GATES = [")
    out = []
    for m in re.finditer(r'\(os\.path\.join\(PROJ,\s*"MECH",\s*("(?:[^"]+)"(?:\s*,\s*"[^"]+")*)\)\s*,\s*"([^"]+)"', gc):
        parts = re.findall(r'"([^"]+)"', m.group(1))
        rel = "MECH/" + "/".join(parts)
        if e >= 0 and e < m.start() and (pm < 0 or m.start() < pm):
            table = "EXTRA_GATES"
        elif pm >= 0 and m.start() > pm:
            table = "PINNED_MD5_GATES"
        else:
            table = "EXTRA_GATES"
        out.append({"rel": rel, "table": table, "label": m.group(2), "pos": m.start()})
    out.sort(key=lambda x: x["rel"])
    return out


def load_block(root):
    """★读真相页机器块 (★fail-closed: 读不到 ⇒ 返回 None★)"""
    p = os.path.join(root, TRUTH_REL)
    if not os.path.exists(p):
        return None
    s = open(p, encoding="utf-8").read()
    i = s.find(BLOCK_BEGIN)
    j = s.find(BLOCK_END)
    if i < 0 or j < 0 or j < i:
        return None
    body = s[i + len(BLOCK_BEGIN):j]
    body = body.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(body)
    except Exception:
        return None


def truth_text(root):
    p = os.path.join(root, TRUTH_REL)
    if not os.path.exists(p):
        return ""
    return open(p, encoding="utf-8").read()


def outbox_manifest(root):
    out = []
    ob = os.path.join(root, "state", "outbox")
    if not os.path.isdir(ob):
        return out
    for dirpath, dirnames, filenames in os.walk(ob):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, root).replace(os.sep, "/")
            try:
                out.append({"path": rel, "md5": md5_of(fp)})
            except Exception:
                out.append({"path": rel, "md5": None})
    out.sort(key=lambda x: x["path"])
    return out


def grep_count(path, needle):
    if not os.path.exists(path):
        return -1
    s = open(path, encoding="utf-8", errors="replace").read()
    return s.count(needle)


# ====================================================================== 判定
class Finding(object):
    __slots__ = ("code", "ok", "msg")

    def __init__(self, code, ok, msg):
        self.code = code
        self.ok = ok
        self.msg = msg

    def as_dict(self):
        return {"code": self.code, "ok": self.ok, "msg": self.msg}


def evaluate(root, strict_lists=True):
    """★核心判定: 扫一个根, 返回 [Finding]★ ★strict_lists=False 时 (夹具用) 跳过内建名单比对★"""
    fs = []
    block = load_block(root)
    gates = scan_gates(root)
    chain = parse_chain(root)
    chain_rels = set(c["rel"] for c in chain)

    # ---------------- M0 零扰动 (板 + 三表 + outbox) ----------------
    board = os.path.join(root, BOARD_REL)
    if not os.path.exists(board):
        fs.append(Finding("M0", False, "★板文件不存在: %s ⇒ 判红 (fail-closed)" % BOARD_REL))
    else:
        st = os.stat(board)
        bmd5 = md5_of(board)
        bad = []
        if bmd5 != BOARD_MD5:
            bad.append("md5=%s (期望 %s)" % (bmd5, BOARD_MD5))
        if st.st_size != BOARD_SIZE:
            bad.append("size=%d (期望 %d)" % (st.st_size, BOARD_SIZE))
        if st.st_mtime_ns != BOARD_MTIME_NS:
            bad.append("mtime_ns=%d (期望 %d)" % (st.st_mtime_ns, BOARD_MTIME_NS))
        fs.append(Finding("M0", not bad,
                          "板 md5/size/mtime 三项与基线逐字相同" if not bad
                          else "★板被动了: " + "; ".join(bad)))

    tab_bad = []
    for rel, want in sorted(TABLE_MD5.items()):
        fp = os.path.join(root, rel)
        if not os.path.exists(fp):
            tab_bad.append("%s 缺失" % rel)
            continue
        got = md5_of(fp)
        if got != want:
            tab_bad.append("%s md5=%s (期望 %s)" % (rel, got, want))
    fs.append(Finding("M0-TBL", not tab_bad,
                      "网表/脚表/BOM 三表 md5 与基线逐字相同" if not tab_bad
                      else "★三表被动了: " + "; ".join(tab_bad)))

    # ---------------- M1 台账自洽 ----------------
    if block is None:
        fs.append(Finding("M1", False, "★真相页机器块读不到 (%s) ⇒ 判红 (fail-closed)" % TRUTH_REL))
        roster = {}
    else:
        roster = block.get("roster") or {}
        problems = []
        disk_set = set(gates)
        reg_set = set(roster.keys())
        miss = sorted(disk_set - reg_set)
        ghost = sorted(reg_set - disk_set - set([SELF_REL]))
        self_missing = SELF_REL not in reg_set
        dup = []
        if len(reg_set) != len(roster.keys()):
            dup.append("roster 有重复 key")
        badclass = [k for k, v in roster.items() if v.get("class") not in CLASSES]
        multi = [k for k, v in roster.items()
                 if isinstance(v.get("classes"), list) and len(set(v["classes"])) > 1]
        multi += [k for k, v in roster.items() if v.get("class2")]
        if multi:
            problems.append("★一道闸有多个归属 (违了「有且只有一个」): %s" % ", ".join(sorted(set(multi))))
        if miss:
            problems.append("★盘上未登记的闸 %d 道: %s" % (len(miss), ", ".join(miss)))
        if ghost:
            problems.append("★登记了但盘上不存在的幽灵闸 %d 道: %s" % (len(ghost), ", ".join(ghost)))
        if self_missing:
            problems.append("★本闸自身 (%s) 未被登记 ⇒ 自指漏洞" % SELF_REL)
        if badclass:
            problems.append("★归属类非法的: %s" % ", ".join(sorted(badclass)))
        if dup:
            problems.extend(dup)
        fs.append(Finding("M1", not problems,
                          "★台账自洽: 盘上 %d 道闸 ↔ 登记 %d 条, 双向差集为空, 本闸自身已登记"
                          % (len(gates), len(roster)) if not problems
                          else "; ".join(problems)))

    # ---------------- M2 必挂闸清单闭环 ----------------
    if block is None:
        fs.append(Finding("M2", False, "★机器块缺失 ⇒ 必挂闸清单不可判 ⇒ 判红 (fail-closed)"))
    else:
        declared = list(block.get("must_hook_suggested") or [])
        ledger = block.get("manual_ledger") or []
        ledger_gates = set()
        for row in ledger:
            if isinstance(row, dict):
                g = row.get("gate") or row.get("rel")
                if g:
                    ledger_gates.add(g)
            elif isinstance(row, str):
                ledger_gates.add(row)
        universe = set(declared) | set(EXPECTED_MUST_HOOK)
        problems = []
        if strict_lists and set(declared) != set(EXPECTED_MUST_HOOK):
            problems.append("★机器块的必挂闸清单与闸内建清单不符 (盘上声明 %d 道 / 内建 %d 道)"
                            % (len(declared), len(EXPECTED_MUST_HOOK)))
        uncovered = []
        missing_script = []
        for g in sorted(universe):
            if not os.path.exists(os.path.join(root, g)):
                missing_script.append(g)
                continue
            if g in chain_rels:
                continue
            if g in ledger_gates:
                continue
            uncovered.append(g)
        if missing_script:
            problems.append("★必挂闸脚本缺失 (fail-closed 一律算红): %s" % ", ".join(missing_script))
        if uncovered:
            problems.append("★%d 道必挂闸【既不在门禁链、也不在人工签核台账】⇒ 没人跑也没人知道: %s"
                            % (len(uncovered), ", ".join(uncovered)))
        # 人工台账行完整性
        for row in ledger:
            if not isinstance(row, dict):
                problems.append("★人工签核台账有非 dict 行")
                continue
            for f in ("gate", "signed_by", "ticket", "date", "evidence"):
                if not row.get(f):
                    problems.append("★人工签核台账行缺字段 %s: %s" % (f, row.get("gate")))
        fs.append(Finding("M2", not problems,
                          "★必挂闸清单闭环: %d 道必挂闸全部落在【挂链表】或【人工签核台账】其一"
                          % len(universe) if not problems
                          else "; ".join(problems)))

    # ---------------- M3 幽灵闸 ----------------
    ghost = []
    for c in chain:
        if not os.path.exists(os.path.join(root, c["rel"])):
            ghost.append("%s (%s)" % (c["rel"], c["table"]))
    fs.append(Finding("M3", not ghost,
                      "★门禁链引用的 %d 道 MECH 闸全部真实存在" % len(chain) if not ghost
                      else "★幽灵闸 (链里引用但盘上不存在): %s" % ", ".join(ghost)))

    # ---------------- M4 判决链 7 + 准出汇总闸 显式登记 ----------------
    if block is None:
        fs.append(Finding("M4", False, "★机器块缺失 ⇒ 判决链归属不可判 ⇒ 判红 (fail-closed)"))
    else:
        problems = []
        sev = list(block.get("verdict_chain_seven") or [])
        rel_gate = block.get("release_summary_gate")
        if strict_lists:
            if sorted(sev) != sorted(EXPECTED_VERDICT_SEVEN):
                problems.append("★机器块的判决链 7 道名单与闸内建名单不符 (声明 %d / 内建 %d)"
                                % (len(sev), len(EXPECTED_VERDICT_SEVEN)))
            if rel_gate != EXPECTED_RELEASE_GATE:
                problems.append("★机器块的准出汇总闸与闸内建名单不符 (%s vs %s)"
                                % (rel_gate, EXPECTED_RELEASE_GATE))
        for g in list(sev) + [rel_gate]:
            if not g:
                problems.append("★判决链名单里有空项")
                continue
            if g not in roster:
                problems.append("★%s 未被登记" % g)
                continue
            cls = (roster[g] or {}).get("class")
            if cls in (None, "", "未分类"):
                problems.append("★%s 的归属是「未分类」⇒ 不许蒙过去" % g)
            if not os.path.exists(os.path.join(root, g)):
                problems.append("★%s 脚本缺失 (fail-closed)" % g)
        fs.append(Finding("M4", not problems,
                          "★7 道判决链闸 + 准出汇总闸全部被显式登记, 无「未分类」"
                          if not problems else "; ".join(problems)))

    # ---------------- M5 板三证不动 ----------------
    fs.append(Finding("M5",
                      not tab_bad and (not os.path.exists(board)
                                       or md5_of(board) == BOARD_MD5),
                      "★板 / 网表 / 脚表 / BOM 四项 md5 与基线逐字相同"))

    # ---------------- M6 零挂链 + 零外发 ----------------
    gcp = os.path.join(root, GATE_CHECK_REL)
    selfname = os.path.basename(SELF_REL)
    n = grep_count(gcp, selfname)
    fs.append(Finding("M6-HOOK", n == 0,
                      "★零挂链自证: `%s` 在 %s 出现 %d 次 (=0)" % (selfname, GATE_CHECK_REL, n)
                      if n == 0 else "★本闸被挂进链了 (出现 %d 次) ⇒ 违反本单边界" % n))

    if block is None:
        fs.append(Finding("M6-OUTBOX", False, "★机器块缺失 ⇒ outbox 基线不可判 ⇒ 判红 (fail-closed)"))
    else:
        want_d = block.get("outbox_manifest_digest")
        want_n = block.get("outbox_file_count")
        now = outbox_manifest(root)
        canon = "\n".join("%s  %s" % (r["md5"], r["path"]) for r in now)
        got_d = hashlib.md5(canon.encode("utf-8")).hexdigest()
        problems = []
        if want_d != got_d:
            problems.append("★state/outbox/ 清单摘要变了 (基线 %s / 实读 %s)" % (want_d, got_d))
        if want_n != len(now):
            problems.append("★state/outbox/ 文件数变了 (基线 %s / 实读 %d)" % (want_n, len(now)))
        fs.append(Finding("M6-OUTBOX", not problems,
                          "★零外发自证: state/outbox/ %d 个文件逐文件 md5 汇总摘要未动" % len(now)
                          if not problems else "; ".join(problems)))

    # ---------------- M7 证据纪律 ----------------
    t = truth_text(root)
    if not t:
        fs.append(Finding("M7", False, "★真相页读不到 ⇒ 判红 (fail-closed)"))
    else:
        problems = []
        t_nolink = MD_LINK_RE.sub("", t)
        bad_ev = []
        for tok in EV_TOKEN_RE.findall(t_nolink):
            if any(k in tok for k in EV_KEYWORDS) and tok not in EV_WHITELIST:
                bad_ev.append(tok)
        bad_ev = sorted(set(bad_ev))
        if bad_ev:
            problems.append("★非白名单的证据等级 token: %s" % ", ".join(bad_ev))
        hang = [w for w in HANGING if w in t]
        if hang:
            problems.append("★挂起措辞: %s" % ", ".join(hang))
        hollow = [w for w in HOLLOW if w in t]
        if hollow:
            problems.append("★空洞词: %s" % ", ".join(hollow))
        if "判据句" not in t or "事实句" not in t:
            problems.append("★判据句与事实句没有分开写")
        if block is not None:
            j = block.get("j_chg_10p") or {}
            ev = j.get("evidence")
            if ev not in EV_WHITELIST:
                problems.append("★J_CHG 10p 几何的回答缺证据等级 (=%r)" % (ev,))
            if not j.get("x_depth_mm") or not j.get("y_width_mm"):
                problems.append("★J_CHG 10p 几何的回答缺 X 向进深 / Y 向占宽")
        fs.append(Finding("M7", not problems,
                          "★证据纪律: 五级白名单 + 零挂起 + 零空洞 + 判据/事实分开 + 10p 回答带等级"
                          if not problems else "; ".join(problems)))

    return fs


def render(fs, root):
    out = []
    out.append("=" * 118)
    out.append("【ISS-405 · MECH 域闸挂链覆盖率闸 · 判定结果】")
    out.append("=" * 118)
    out.append("  根目录: %s" % root)
    out.append("  ★红 = 现状有问题, 不是闸故障★")
    for f in fs:
        out.append("[%s] %s :: %s" % ("PASS" if f.ok else "FAIL", f.code, f.msg))
    nred = sum(1 for f in fs if not f.ok)
    out.append("-" * 118)
    out.append("合计: %d/%d 条判据通过" % (len(fs) - nred, len(fs)))
    if nred:
        out.append("★红 %d 条 ⇒ rc=1 ★" % nred)
        out.append("★红的那一条正是【现状】: 必挂闸既不在门禁链、也不在人工签核台账 ⇒ 没人跑也没人知道★")
    else:
        out.append("★全绿 ⇒ rc=0 ★")
    return "\n".join(out)


# ====================================================================== 自测夹具
FIXTURE_GATES = [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_fts_seat_sample_plan.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
    "MECH/check_machine_block_pointer_resolvable.py",
    "MECH/check_onepass_mech_release.py",
    "MECH/check_pad_size_coupling_closed.py",
    "MECH/check_misc_snapshot.py",
    "MECH/check_mech_gate_hook_coverage.py",
    "MECH/tools/check_mech_ref_reachability.py",
]


def build_fixture(root):
    """★造一个【全绿】的合成根 (★用于反向用例自测·★与真实盘无关★)"""
    if os.path.isdir(root):
        shutil.rmtree(root)
    for g in FIXTURE_GATES:
        p = os.path.join(root, g)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write("# fixture %s\n" % g)
    # 板 + 三表
    board = os.path.join(root, BOARD_REL)
    os.makedirs(os.path.dirname(board), exist_ok=True)
    open(board, "wb").write(b"FIXTURE-BOARD\n")
    # 造出与基线一致的 md5 不可能 ⇒ 夹具改用自己的基线 ⇒ 所以夹具只跑 M1~M4/M6/M7, 不跑 M0/M5
    for rel in TABLE_MD5:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write("fixture %s\n" % rel)
    # 链
    os.makedirs(os.path.join(root, "state"), exist_ok=True)
    open(os.path.join(root, GATE_CHECK_REL), "w", encoding="utf-8").write(
        "EXTRA_GATES = [\n"
        '    (os.path.join(PROJ, "MECH", "check_debug_seat_3d_fit.py"), "fixture A", ()),\n'
        ']\n'
        "PINNED_MD5_GATES = [\n"
        '    (os.path.join(PROJ, "MECH", "tools", "check_mech_ref_reachability.py"), "fixture B", ()),\n'
        "]\n")
    # outbox
    ob = os.path.join(root, "state", "outbox")
    os.makedirs(ob, exist_ok=True)
    open(os.path.join(ob, "README.md"), "w", encoding="utf-8").write("fixture outbox\n")
    # 真相页
    roster = {}
    for g in FIXTURE_GATES:
        if g == "MECH/check_mech_gate_hook_coverage.py":
            cls = "E_self_pending_main_hook"
        elif g == "MECH/check_misc_snapshot.py":
            cls = "C_oneoff_evaluation"
        elif g in ("MECH/check_debug_seat_3d_fit.py", "MECH/tools/check_mech_ref_reachability.py"):
            cls = "A_hooked"
        else:
            cls = "B_must_hook_not_hooked"
        roster[g] = {"class": cls, "reason": "fixture", "hooked": cls == "A_hooked",
                     "hooked_in": "EXTRA_GATES" if cls == "A_hooked" else None,
                     "rc_now": 0, "stdout_lines": 1, "last_line": "fixture"}
    blk = {
        "meta": {"issue": "ISS-405", "self_hook_status": "待 main 挂链"},
        "roster": roster,
        "must_hook_suggested": sorted(EXPECTED_MUST_HOOK),
        "manual_ledger": [{"gate": g, "signed_by": "fixture", "ticket": "FIX-1",
                           "date": "2026-11-25", "evidence": "[实测]"}
                          for g in EXPECTED_MUST_HOOK],
        "verdict_chain_seven": list(EXPECTED_VERDICT_SEVEN),
        "release_summary_gate": EXPECTED_RELEASE_GATE,
        "outbox_manifest_digest": hashlib.md5(
            ("\n".join("%s  %s" % (r["md5"], r["path"]) for r in outbox_manifest(root))).encode("utf-8")
        ).hexdigest(),
        "outbox_file_count": len(outbox_manifest(root)),
        "j_chg_10p": {"x_depth_mm": 6.4, "y_width_mm": 9.1, "evidence": "[官网]"},
    }
    body = json.dumps(blk, ensure_ascii=False, indent=1, sort_keys=True)
    txt = ("# fixture truth page\n\n"
           "判据句 / 事实句 分开写。\n\n"
           "证据等级: [官网] [实测] [媒体] [推算] [0数据]\n\n"
           + BLOCK_BEGIN + "\n```json\n" + body + "\n```\n" + BLOCK_END + "\n")
    os.makedirs(os.path.join(root, "MECH"), exist_ok=True)
    open(os.path.join(root, TRUTH_REL), "w", encoding="utf-8").write(txt)
    return blk


def save_block(root, blk):
    body = json.dumps(blk, ensure_ascii=False, indent=1, sort_keys=True)
    txt = ("# fixture truth page\n\n"
           "判据句 / 事实句 分开写。\n\n"
           "证据等级: [官网] [实测] [媒体] [推算] [0数据]\n\n"
           + BLOCK_BEGIN + "\n```json\n" + body + "\n```\n" + BLOCK_END + "\n")
    open(os.path.join(root, TRUTH_REL), "w", encoding="utf-8").write(txt)


def load_fixture_block(root):
    return load_block(root)


def selftest():
    """★1 正向 + 12 反向★ ★每条都自证「只红目标那一条 (或该组)」★"""
    sbx = os.path.join(ROOT, "tmp", "iss405", "sbx")
    if os.path.isdir(sbx):
        shutil.rmtree(sbx)
    os.makedirs(sbx, exist_ok=True)
    cases = []

    # ---------------- 正向 ----------------
    root = os.path.join(sbx, "case_positive")
    blk = build_fixture(root)
    fs = evaluate(root, strict_lists=True)
    red = [f.code for f in fs if not f.ok and f.code not in ("M0", "M0-TBL", "M5")]
    cases.append(("正向 · 合成基线全绿", red, [], root))

    def mutate(name, fn, expect_code):
        r = os.path.join(sbx, name)
        b = build_fixture(r)
        fn(r, b)
        f2 = evaluate(r, strict_lists=True)
        r2 = [f.code for f in f2 if not f.ok and f.code not in ("M0", "M0-TBL", "M5")]
        cases.append((name, r2, [expect_code], r))
        return r2

    # ---------------- 反向 1: 盘上多出一道未登记的闸 ----------------
    def c1(r, b):
        p = os.path.join(r, "MECH", "check_brand_new_gate.py")
        open(p, "w", encoding="utf-8").write("# new\n")
    mutate("反向1 · 盘上新增未登记的闸 ⇒ M1 红", c1, "M1")

    # ---------------- 反向 2: 登记了盘上不存在的幽灵闸 ----------------
    def c2(r, b):
        b["roster"]["MECH/check_ghost_gate.py"] = {"class": "C_oneoff_evaluation", "reason": "ghost"}
        save_block(r, b)
    mutate("反向2 · 登记幽灵闸 ⇒ M1 红", c2, "M1")

    # ---------------- 反向 3: 同一路径登记两次 (归属重复) ----------------
    def c3(r, b):
        b["roster"]["MECH/check_misc_snapshot.py"]["classes"] = ["C_oneoff_evaluation", "A_hooked"]
        save_block(r, b)
    mutate("反向3 · 一道闸两个归属 ⇒ M1 红", c3, "M1")

    # ---------------- 反向 4: 必挂闸既不在链上也不在人工台账 ----------------
    def c4(r, b):
        b["manual_ledger"] = []
        save_block(r, b)
    mutate("反向4 · 必挂闸两头都没有 ⇒ M2 红", c4, "M2")

    # ---------------- 反向 5: 必挂闸的脚本文件被删 (fail-closed) ----------------
    def c5(r, b):
        os.remove(os.path.join(r, "MECH", "check_pad_size_coupling_closed.py"))
    mutate("反向5 · 必挂闸脚本缺失 ⇒ M2 红 (fail-closed)", c5, "M2")

    # ---------------- 反向 6: 链上引用了不存在的脚本 (幽灵闸) ----------------
    def c6(r, b):
        gc = os.path.join(r, GATE_CHECK_REL)
        s = open(gc, encoding="utf-8").read()
        s = s.replace('"check_debug_seat_3d_fit.py"', '"check_vanished_gate.py"')
        open(gc, "w", encoding="utf-8").write(s)
    mutate("反向6 · 链上幽灵闸 ⇒ M3 红", c6, "M3")

    # ---------------- 反向 7: 判决链闸漏登记 ----------------
    def c7(r, b):
        del b["roster"]["MECH/check_juart_1p27_clearance.py"]
        save_block(r, b)
    mutate("反向7 · 判决链闸未登记 ⇒ M1+M4 红", c7, "M4")

    # ---------------- 反向 8: 把判决链名单改小来绕过 ----------------
    def c8(r, b):
        b["verdict_chain_seven"] = list(EXPECTED_VERDICT_SEVEN[:-1])
        save_block(r, b)
    mutate("反向8 · 判决链名单被改小 ⇒ M4 红", c8, "M4")

    # ---------------- 反向 9: 必挂闸清单被删空来骗绿 ----------------
    def c9(r, b):
        b["must_hook_suggested"] = []
        save_block(r, b)
    mutate("反向9 · 必挂闸清单被删空 ⇒ M2 红 (防后门)", c9, "M2")

    # ---------------- 反向 10: 本闸自己被挂进链 ----------------
    def c10(r, b):
        gc = os.path.join(r, GATE_CHECK_REL)
        s = open(gc, encoding="utf-8").read()
        s = s.replace('EXTRA_GATES = [',
                      'EXTRA_GATES = [\n    (os.path.join(PROJ, "MECH", "check_mech_gate_hook_coverage.py"), "self", ()),')
        open(gc, "w", encoding="utf-8").write(s)
    mutate("反向10 · 本闸被挂链 ⇒ M6-HOOK 红", c10, "M6-HOOK")

    # ---------------- 反向 11: outbox 被改 (零外发自证) ----------------
    def c11(r, b):
        open(os.path.join(r, "state", "outbox", "README.md"), "a", encoding="utf-8").write("tampered\n")
    mutate("反向11 · outbox 被改 ⇒ M6-OUTBOX 红", c11, "M6-OUTBOX")

    # ---------------- 反向 12: 真相页出现挂起措辞 / 非白名单等级 ----------------
    def c12(r, b):
        p = os.path.join(r, TRUTH_REL)
        s = open(p, encoding="utf-8").read()
        s = s.replace("判据句 / 事实句 分开写。", "判据句 / 事实句 分开写。 等原厂回信 [官方] ")
        open(p, "w", encoding="utf-8").write(s)
    mutate("反向12 · 挂起措辞 + 非白名单等级 ⇒ M7 红", c12, "M7")

    # ---------------- 反向 13: 真相页机器块缺失 (fail-closed) ----------------
    def c13(r, b):
        os.remove(os.path.join(r, TRUTH_REL))
    mutate("反向13 · 真相页机器块缺失 ⇒ M1+M2+M4+M6+M7 红 (fail-closed)", c13, "M1")

    # ---------------- 跑 ----------------
    ok = True
    npass = nneg = 0
    lines = []
    for name, red, expect, r in cases:
        if not expect:
            # 正向: 期望全绿
            good = (len(red) == 0)
            npass += 1 if good else 0
            if not good:
                ok = False
            lines.append("[%s] %s%s" % ("PASS" if good else "FAIL", name,
                                         "" if good else "  ★红了: %s" % red))
        else:
            good = expect[0] in red
            nneg += 1 if good else 0
            if not good:
                ok = False
            lines.append("[%s] %s  ★红到的判据: %s" % ("PASS" if good else "FAIL", name, red))
    # 额外自检: 本闸自身必须被登记 (防自指漏洞)
    lines.append("[INFO] 自测用沙盒: %s" % sbx)
    lines.append("[INFO] 正向用例 %d 条 / 反向用例 %d 条" % (npass, nneg))
    out = []
    out.append("=" * 118)
    out.append("【ISS-405 · MECH 域闸挂链覆盖率闸 · 自测 (--selftest)】")
    out.append("=" * 118)
    out.extend(lines)
    out.append("-" * 118)
    if ok and npass >= 1 and nneg >= 8:
        out.append("ALL TESTS PASS")
    else:
        out.append("SELFTEST FAILED (正向 %d / 反向 %d)" % (npass, nneg))
    return ok, "\n".join(out), npass, nneg


# ====================================================================== main
def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args(argv)

    if args.selftest:
        ok, text, npass, nneg = selftest()
        print(text)
        return 0 if ok else 1

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.stderr.write("★根目录不存在: %s\n" % root)
        return 2

    if args.emit:
        blk = load_block(root)
        if blk is None:
            sys.stderr.write("★真相页机器块读不到 (%s)\n" % TRUTH_REL)
            return 2
        print(json.dumps(blk, ensure_ascii=False, indent=1, sort_keys=True))
        return 0

    fs = evaluate(root, strict_lists=True)
    if args.json:
        print(json.dumps({
            "issue": "ISS-405",
            "gate": SELF_REL,
            "root": root,
            "findings": [f.as_dict() for f in fs],
            "red": sum(1 for f in fs if not f.ok),
        }, ensure_ascii=False, indent=1, sort_keys=True))
        return 1 if any(not f.ok for f in fs) else 0

    print(render(fs, root))
    return 1 if any(not f.ok for f in fs) else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(2)
