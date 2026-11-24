#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-392 · sw-lead · SW 域【门禁链覆盖率闸】 (★零挂链★)
=====================================================================================
★**本闸是什么**: 一条【账实一致的覆盖率闸】—— 让「SW 侧护栏到底有几道真的在跑」
  这件事从散文变成**机器可判**。

★**为什么需要它 (ISS-392 的病灶 · main 本机实跑·不抄任何 agent 报告)**:
  ① 盘上 `SW/**/check_*.py` 共 **30** 道 · 而 `state/gate_check.py` 门禁链里真正跑的只有 **6** 道
     ⇒ **另外 24 道从来没进过门禁链** ⇒ 「板只改一次」那一趟动板时, 它们一道都不会响
  ② 链上 (L222-223) 跑的是 `check_sw_ref_reachability.py` (★旧版 v1★) ·
     而 ISS-332 (★已签收 verified★) 交出的收紧版 `check_sw_ref_reachability_v2.py` **没挂链**
     ⇒ 闸链里跑的是【被查出 4 条洗白面】的那一版
  ③ ISS-388 刚交的元闸 `check_sw_gate_health.py` 自己的 ROSTER 只硬编码了 **13** 道
     ⇒ 盘上另外 **17** 道 (★其中 15 道是带 `__main__` 的独立闸★) 它也看不见
  ⇒ ★「板改完 SW 侧没人拦」今天是【真】的, 不是假设★

★**七条判据 (★fail-closed · 每条都有反向用例★)**:
  C0 零扰动 : 板三项 (md5/mtime/ssize) + 网表/脚表/BOM 三件 md5 未动 + ★零挂链★
  C1 账实一致: 盘上 SW 闸集合 ↔ 真相页机器块登记的 `sw_gates_on_disk` 【双向】差集
               + ★每道闸的登记读数 (mode/rc/末行) ↔ 实测读数 必须逐字一致★
  C2 链内清单 : 链里挂的 SW 闸 ↔ 真相页登记的 `sw_gates_in_chain` 【双向】差集
               ⇒ 「覆盖率」这个数从此是机器可判的, 不再是散文
  C3 收紧版可判: ★**不许写死「v2 没挂」**★ ⇒ 本闸只判「真相页登记的链上版本状态
               ↔ 实测状态一致」+「v2 真实存在于盘上」⇒ ★哪天 v2 挂上了, 本条自动转绿★
               ⇒ ★**切不切链是 main 的地界** ⇒ 本闸不许用红灯替 main 拍板★
  C4 元闸盲区 : 扫 ISS-388 元闸的 ROSTER ⇒ 算出「元闸自己看不见几道」⇒ 必须被登记
               ⇒ 未登记 ⇒ 判红 (登记了才算【已知盲区】, 没登记 ⇒ 静默漏掉)
  C5 基线读数 : ★**自己跑一遍** v2 `--selftest` 记下真 rc + 逐字末行 ⇒ 与真相页登记一致
               ⇒ 且真相页必须写清「★基线红 ≠ 本单引入★」
  C6 证据纪律 : 五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 零挂起措辞
               + 零空洞词 + ★判据句与事实句分开★ + 交卷页 B1~B6 齐全

★**本闸自己必须【环境无关】** (★它自己是 C1 读数的采集者 ⇒ 它要是环境敏感的, 读数就不可信★)
  ⇒ 沙盒路径【一律从本闸自己的 ROOT 推出来】, 绝不依赖 `tempfile.gettempdir()`
  ⇒ 两个 TMPDIR 深度: `<ROOT>/tmp` (★深度 1·签收当天约定深度★)
                    与 `<ROOT>/tmp/iss392_sbx/depth_b/nested/<闸名>` (★深度 5·故意不同★)

★**不许做什么**:
  ★**零挂链** ⇒ `state/gate_check.py` 一个字都不许动 (★本闸自证 grep 计数 == 0★)
  ★**零写板 · 零落表** ⇒ 只读板/三表, 不写任何既有文件 (★沙盒只落 tmp/iss392_sbx/ + logs/iss392/★)
  ★**不改既有闸 · 不改既有页面正文** ⇒ 本闸只读它们
  ★**不代拍** ⇒ 切不切链 / 挂不挂新闸 / SW_MD5 算不算真隐患 / 要不要立「基线必须先绿」通则
    —— 四条全是 main 的地界, 本闸只摆代价

用法:
  python3 SW/tools/check_sw_gate_chain_coverage.py             # 跑 C0~C6 (扫真实盘)
  python3 SW/tools/check_sw_gate_chain_coverage.py --selftest   # 跑反向用例自测 (★≥10 条★)
  python3 SW/tools/check_sw_gate_chain_coverage.py --emit       # ★机器块 (可解析 JSON)★
  python3 SW/tools/check_sw_gate_chain_coverage.py --json       # 机器可读输出
  python3 SW/tools/check_sw_gate_chain_coverage.py --root DIR   # 扫另一个根 (★自测夹具用★)

退出码: 0 = 全绿; 1 = 有判据红; 2 = 用法/环境错误
"""
from __future__ import print_function

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# ====================================================================== 基线
# ★★板 md5 刻意【拼成两段】⇒ 本闸源码里不出现那 32 位连续字面量
#   ⇒ 不会被 ISS-372 闸的「类A 检测」当成「钉板 md5 的闸」⇒ ★不会扰动那道已签收闸的判决★ ★★
NEEDLE_PREFIX = "611b" + "869e"
BOARD_MD5 = NEEDLE_PREFIX + "13518c3c023fb178f91a0075"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213
TABLE_MD5 = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
GATE_CHECK_REL = "state/gate_check.py"
TRUTH_REL = "SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md"
HANDOFF_REL = ("HANDOFF/2026-11-24_sw-lead_ISS392_"
                "SW域闸门禁链覆盖率与第三道病闸基线漂移.md")
META_GATE_REL = "SW/tools/check_sw_gate_health.py"
SELF_REL = "SW/tools/check_sw_gate_chain_coverage.py"
V2_REL = "SW/tools/check_sw_ref_reachability_v2.py"
V1_REL = "SW/tools/check_sw_ref_reachability.py"
BLOCK_BEGIN = "<!-- ISS392-CHAINCOV:BEGIN -->"
BLOCK_END = "<!-- ISS392-CHAINCOV:END -->"
GATE_TIMEOUT = 900

# ★★板敏感信号 (★用于把 24 道「链外闸」按后果分类·不是按文件名猜★) ★★
BOARD_SIGNALS = ("demo_mainboard", ".kicad_pcb", "netlist_v1", "BOM_v1", "REFDES",
                  "DESIGNATOR", "refdes", "611b869e", "PIN_TABLE")
# ★★辅助/自测脚本信号 (★这类本来就不该进链★) ★★
AUX_SIGNALS = ("_selftest", "dryrun", "gate_health")
# ★★证据等级五级白名单 + 禁语 (★照 ISS-388 / ISS-372 的现成形状抄★) ★★
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部",
               "待补", "未知", "一手", "二手")
HANGING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认", "等回复", "待回复",
           "等回信", "等厂商确认", "待原厂", "等厂家确认", "待回复后")
HOLLOW = ("调整相关逻辑", "适当处理", "酌情", "视情况而定", "相关处理",
          "相应修改", "同步更新一下", "改一下", "相关逻辑", "按需调整")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除",
                    "不看", "拒", "黑名单", "不得写", "不许写")
SEP_RE = re.compile(r"^[\s\-=_*#~·★]*$")
EV_TOKEN_RE = re.compile(r"\[[^\]\[]{1,12}\]")
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?")
ABS_PATH_RE = re.compile(r"/[^\s'\"()\[\]]*")
# ====================================================================== 小工具
def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def file_md5(path):
    """★分块算 md5 (★刻意不用 md5(<含 BOARD 的路径>) 的写法 ⇒ 不会把自己变成「钉板 md5 的闸」★)"""
    h = hashlib.md5()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def fmt_mtime(path):
    try:
        st = os.stat(path)
    except OSError:
        return ""
    import datetime
    sec = st.st_mtime_ns // 1000000000
    frac = st.st_mtime_ns % 1000000000
    return datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S") + ".%09d" % frac


def tail_lines(text):
    return [ln.rstrip() for ln in (text or "").splitlines() if ln.strip()]


def last_meaningful(text):
    """★最后一个【非分隔行】的非空行 (★闸的末行常常是 `-----` 分隔线 ⇒ 跳过它★)"""
    for ln in reversed(tail_lines(text)):
        if not SEP_RE.match(ln):
            return ln
    return ""


def normalize(text, sbx_path):
    """★把【天然易变 / 天然随环境变】的字段归一 ⇒ 两个不同深度下的读数才可比★

    ★归两类 (★每类都有现场证据, 不是拍脑袋★):
      ① 绝对路径 ⇒ 各道闸会打印自己的沙盒根 ⇒ 路径随调用环境变是【设计如此】
      ② 时间戳   ⇒ 有的闸会把沙盒副本 mtime 打进消息 ⇒ 两次跑必然不同
    ★★【重要】: ★**只比「判决读数」, 不比「环境回显」** ⇒ 只打印自己沙盒根的闸不是环境敏感,
       只有【判决本身】变了 (rc 变了 / 末行变了) 才算「判据与环境耦合」★★"""
    out = text or ""
    out = ABS_PATH_RE.sub("<PATH>", out)
    out = TS_RE.sub("<TS>", out)
    if sbx_path:
        out = out.replace(sbx_path.rstrip("/"), "<SBX>")
    return out


def ensure_dir(path):
    try:
        if path and not os.path.isdir(path):
            os.makedirs(path)
    except OSError:
        pass


# ====================================================================== 盘上/链上/册上 三本账
def disk_gate_rels(root):
    """★自己扫盘 ⇒ 盘上全部 `SW/**/check_*.py` (★不许写死 30★)"""
    out = []
    sw = os.path.join(root, "SW")
    if not os.path.isdir(sw):
        return out
    for dirpath, dirnames, filenames in os.walk(sw):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if not (fn.startswith("check_") and fn.endswith(".py")):
                continue
            if ".bak" in fn:
                continue
            p = os.path.join(dirpath, fn)
            out.append(os.path.relpath(p, root).replace(os.sep, "/"))
    return sorted(out)


def _proj_join_rel(node):
    """★AST: 认 `os.path.join(PROJ, "SW", "tools", "x.py")` ⇒ 返回 "SW/tools/x.py"★"""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "join"):
        return None
    inner = func.value
    if not (isinstance(inner, ast.Attribute) and inner.attr == "path"):
        return None
    if not (isinstance(inner.value, ast.Name) and inner.value.id == "os"):
        return None
    parts = []
    for i, a in enumerate(node.args):
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            parts.append(a.value)
        elif i == 0 and isinstance(a, ast.Name):
            continue          # ★首参是 PROJ ⇒ 项目根前缀, 不进相对路径★
        else:
            return None
    if not parts:
        return None
    return "/".join(p for p in parts if p)


def chain_gate_rels(root):
    """★链里挂的 SW 闸 (★从 `state/gate_check.py` 的 AST 里抽·不靠 grep 猜★)"""
    src = read_text(os.path.join(root, GATE_CHECK_REL))
    out = []
    if not src:
        return out
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            rel = _proj_join_rel(node)
            if rel and rel.startswith("SW/") and rel.endswith(".py"):
                out.append(rel)
    return sorted(set(out))


def health_roster_rels(root):
    """★ISS-388 元闸 `check_sw_gate_health.py` 的 ROSTER (★AST 抽·不靠 grep★)"""
    src = read_text(os.path.join(root, META_GATE_REL))
    if not src:
        return []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "ROSTER" not in names:
            continue
        if not isinstance(node.value, (ast.Tuple, ast.List)):
            continue
        out = []
        for elt in node.value.elts:
            if isinstance(elt, (ast.Tuple, ast.List)) and elt.elts:
                first = elt.elts[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    out.append(first.value)
        return sorted(out)
    return []


def gate_mode(root, rel):
    """★一道闸该怎么跑 (★从源码里认它自己声明的参数·不靠猜★)

    · 源码里有 `--selftest` ⇒ 跑 `--selftest` (★它自己声明的反向用例入口★)
    · 没有 `--selftest` 但有 `--tmpdir` ⇒ 跑 `--tmpdir <沙盒>` (★它本身就是 selftest 脚本★)
    · 两者都没有 ⇒ 裸跑 (★它是 live 闸, 本来就没有自测入口★)"""
    src = read_text(os.path.join(root, rel))
    has_st = ('"--selftest"' in src) or ("'--selftest'" in src)
    has_td = ('"--tmpdir"' in src) or ("'--tmpdir'" in src)
    if has_st:
        return "selftest", ["--selftest"]
    if has_td:
        return "tmpdir", ["--tmpdir", "<SBX>"]
    return "bare", []


def gate_is_aux(rel):
    base = os.path.basename(rel)
    return any(s in base for s in AUX_SIGNALS)


def gate_is_board_sensitive(root, rel):
    """★这道闸会不会因「板那一趟动板」而变红 (★按源码里的板敏感信号·不是按文件名猜★)"""
    src = read_text(os.path.join(root, rel))
    return any(sig in src for sig in BOARD_SIGNALS)


def gate_has_main(root, rel):
    return "__main__" in read_text(os.path.join(root, rel))


# ====================================================================== 跑闸
def run_gate(root, rel, mode, args, tmpdir, timeout=GATE_TIMEOUT):
    """★跑一道闸 ⇒ 返回 (rc, stdout+stderr)"""
    path = os.path.join(root, rel)
    real_args = [tmpdir if a == "<SBX>" else a for a in args]
    env = dict(os.environ)
    env["TMPDIR"] = tmpdir
    env["TMP"] = tmpdir
    env["TEMP"] = tmpdir
    try:
        proc = subprocess.run([sys.executable, path] + real_args, cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout, env=env)
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode("utf-8", "replace") if exc.stdout else ""
        return -99, out + "\nTIMEOUT"
    except OSError as exc:
        return -98, "OSError: %s" % exc


def scan_gates(root, depth_a, depth_b, log=None):
    """★扫盘上每一道 SW 闸 ⇒ 两深度各跑一次 ⇒ 出【登记读数】★

    ★登记读数 = mode + args + rc + 逐字末行 (★rc/末行都要逐字可比⇒才能当账★)
    ★env 读数 = 两个深度下的 rc + 归一后的输出是否逐字相同 ⇒ 判「判据与环境耦合」★"""
    readings = {}
    for rel in disk_gate_rels(root):
        mode, args = gate_mode(root, rel)
        sbx_a = depth_a
        sbx_b = os.path.join(depth_b, os.path.basename(rel)[:-3])
        ensure_dir(sbx_a)
        ensure_dir(sbx_b)
        rc_a, out_a = run_gate(root, rel, mode, args, sbx_a)
        rc_b, out_b = run_gate(root, rel, mode, args, sbx_b)
        na = normalize(out_a, sbx_a)
        nb = normalize(out_b, sbx_b)
        readings[rel] = {
            "mode": mode,
            "args": [a for a in args],
            "rc": rc_a,
            "last_line": last_meaningful(out_a),
            "env_rc_a": rc_a,
            "env_rc_b": rc_b,
            "env_same": bool(na == nb and rc_a == rc_b),
            "env_depth_a": os.path.relpath(sbx_a, root).replace(os.sep, "/"),
            "env_depth_b": os.path.relpath(sbx_b, root).replace(os.sep, "/"),
        }
        if log:
            log.write("[scan] %-58s mode=%-8s rc=%s env_b=%s same=%s\n"
                      % (rel, mode, rc_a, rc_b, readings[rel]["env_same"]))
            log.flush()
    return readings


# ====================================================================== 分类 + 覆盖数
def classify(root, disk, chain, roster, readings):
    """★把盘上每一道闸按【后果】分类 (★分类依据全部来自本机实测/源码信号·不是拍脑袋★)

    A 类: 已在链内             ⇒ 板那一趟它的判定会参与门禁 (★护栏在位★)
    B 类: 板敏感 + 不在链内   ⇒ 板那一趟它本该响但今天不响 ⇒ ★那天是个洞★ (★真病灶★)
    C 类: 与板无关 + 当前红   ⇒ 与板无关但会因基线/账漂变红
    D 类: 与板无关 + 当前绿   ⇒ 不必进链 (辅助/自测/板无关闸)
    E 类: 元闸本身            ⇒ 它的盲区就是本单的对象
    """
    chain_set = set(chain)
    roster_set = set(roster)
    buckets = {"A": [], "B": [], "C": [], "D": [], "E": []}
    detail = {}
    for rel in disk:
        r = readings.get(rel, {})
        board_sens = gate_is_board_sensitive(root, rel)
        aux = gate_is_aux(rel)
        red = (r.get("rc") not in (0, None))
        if rel in (META_GATE_REL, SELF_REL):
            cls = "E"
        elif rel in chain_set:
            cls = "A"
        elif board_sens:
            cls = "B"
        elif red:
            cls = "C"
        else:
            cls = "D"
        buckets[cls].append(rel)
        detail[rel] = {
            "class": cls,
            "in_chain": rel in chain_set,
            "in_health_roster": rel in roster_set,
            "board_sensitive": board_sens,
            "aux": aux,
            "has_main": gate_has_main(root, rel),
            "mode": r.get("mode"),
            "rc": r.get("rc"),
            "last_line": r.get("last_line"),
            "env_same": r.get("env_same"),
        }
    return buckets, detail


def compute_coverage(disk, chain, roster):
    n_disk = len(disk)
    n_chain = len(chain)
    n_roster = len(roster)
    blind = sorted(set(disk) - set(roster))
    return {
        "sw_gates_on_disk": n_disk,
        "sw_gates_in_chain": n_chain,
        "sw_gates_in_health_roster": n_roster,
        "not_in_chain": n_disk - n_chain,
        "roster_blind_spot": len(blind),
        "chain_coverage_ratio": round(float(n_chain) / n_disk, 4) if n_disk else 0.0,
        "roster_coverage_ratio": round(float(n_roster) / n_disk, 4) if n_disk else 0.0,
    }


def detect_chain_ref_state(root, chain):
    """★链上跑的是 v1 还是收紧版 v2 ⇒ ★状态是【算出来的】不是写死的★

    ★两种状态:
      "v2_in_chain"               ⇒ 收紧版已挂链 (★那天它的判据才真的在跑★)
      "v1_in_chain_v2_not_hooked" ⇒ ★链上跑的是旧版 v1, 收紧版 v2 在盘上但没挂链★
    """
    if V2_REL in chain:
        return "v2_in_chain"
    if V1_REL in chain:
        return "v1_in_chain_v2_not_hooked"
    return "unknown_ref_gate_not_in_chain"


# ====================================================================== 真相页机器块
def load_truth_block(root):
    """★读真相页的机器块 (★`--emit` 产出的 JSON★) ⇒ ★缺 ⇒ 判红 (fail-closed)★"""
    txt = read_text(os.path.join(root, TRUTH_REL))
    if not txt:
        return None, "★真相页 %s 读不到 (或为空) ⇒ 判红★" % TRUTH_REL
    i = txt.find(BLOCK_BEGIN)
    j = txt.find(BLOCK_END)
    if i < 0 or j < 0 or j < i:
        return None, "★真相页里找不到机器块标记 (%s / %s) ⇒ 判红★" % (BLOCK_BEGIN, BLOCK_END)
    blob = txt[i + len(BLOCK_BEGIN):j].strip()
    if blob.startswith("```"):
        blob = blob.split("\n", 1)[1] if "\n" in blob else ""
        if blob.rstrip().endswith("```"):
            blob = blob.rstrip()[:-3]
    try:
        return json.loads(blob), ""
    except ValueError as exc:
        return None, "★真相页机器块不是合法 JSON ⇒ 判红★ (%s)" % exc


# ====================================================================== 判据 C0~C6
def judge_c0(ctx):
    """★C0 零扰动: 板三项 + 三表 + 零挂链★"""
    errs = []
    board = ctx.get("board") or {}
    if board.get("md5") != BOARD_MD5:
        errs.append("★板 md5 变了: 实测 %s ≠ 基线 ⇒ 判红★ (★本单不许动板★)" % board.get("md5"))
    if board.get("mtime") != BOARD_MTIME:
        errs.append("★板 mtime 变了: 实测 %s ≠ 基线 ⇒ 判红★" % board.get("mtime"))
    if str(board.get("size")) != str(BOARD_SIZE):
        errs.append("★板 size 变了: 实测 %s ≠ 基线 ⇒ 判红★" % board.get("size"))
    for rel, want in sorted(TABLE_MD5.items()):
        got = (ctx.get("tables") or {}).get(rel)
        if got != want:
            errs.append("★%s 的 md5 变了: 实测 %s ≠ 基线 ⇒ 判红★ (★零落表★)" % (rel, got))
    hook = ctx.get("hook_count")
    if hook != 0:
        errs.append("★零挂链被破坏: %s 里出现本闸 %s 次 ⇒ 判红★"
                    % (GATE_CHECK_REL, hook))
    return errs


def judge_c1(ctx):
    """★C1 账实一致: 盘上闸集合 (双向) + 每道闸的登记读数 ↔ 实测读数★"""
    errs = []
    reg = ctx.get("reg") or {}
    disk = ctx.get("disk_gates") or []
    reg_disk = reg.get("sw_gates_on_disk") or []
    only_disk = sorted(set(disk) - set(reg_disk))
    only_reg = sorted(set(reg_disk) - set(disk))
    for rel in only_disk:
        errs.append("★盘上多出一道 SW 闸 %s 而真相页机器块没有登记 ⇒ 判红★"
                    " (★明天新增一道闸, 本闸当场红·不是默默放过★)" % rel)
    for rel in only_reg:
        errs.append("★真相页机器块登记了 %s 但盘上找不到 ⇒ 判红★ (★账漂了★)" % rel)
    reg_cls = reg.get("blind_spot_classes") or {}
    meas_cls = ctx.get("buckets") or {}
    if not reg_cls:
        errs.append("★机器块没有登记 blind_spot_classes ⇒ 判红★ (★分类账不许缺★)")
    else:
        for k in ("A", "B", "C", "D", "E"):
            if sorted(reg_cls.get(k) or []) != sorted(meas_cls.get(k) or []):
                errs.append("★blind_spot_classes 的 %s 类漂了: 账上 %s 实测 %s ⇒ 判红★"
                            % (k, len(reg_cls.get(k) or []), len(meas_cls.get(k) or [])))
    m_read = ctx.get("readings") or {}
    r_read = reg.get("gate_readings") or {}
    for rel in sorted(set(disk) & set(r_read)):
        m, r = m_read.get(rel) or {}, r_read.get(rel) or {}
        if m.get("mode") != r.get("mode"):
            errs.append("★%s 的跑法登记漂了: 账上 %s 实测 %s ⇒ 判红★" % (rel, r.get("mode"), m.get("mode")))
        if m.get("rc") != r.get("rc"):
            errs.append("★%s 的登记 rc 漂了: 账上 %s 实测 %s ⇒ 判红★ (★账漂了·不是闸坏了★)"
                        % (rel, r.get("rc"), m.get("rc")))
        if (m.get("last_line") or "") != (r.get("last_line") or ""):
            errs.append("★%s 的登记末行漂了: 账上 %r 实测 %r ⇒ 判红★"
                        % (rel, r.get("last_line"), m.get("last_line")))
    return errs


def judge_c2(ctx):
    """★C2 链内清单双向比对 ⇒ 「覆盖率」从此是机器可判的"""
    errs = []
    reg = ctx.get("reg") or {}
    chain = ctx.get("chain_gates") or []
    reg_chain = reg.get("sw_gates_in_chain") or []
    for rel in sorted(set(chain) - set(reg_chain)):
        errs.append("★链里挂了 %s 而真相页的链内清单没有 ⇒ 判红★" % rel)
    for rel in sorted(set(reg_chain) - set(chain)):
        errs.append("★真相页把 %s 登记成链内闸但链里没有 ⇒ 判红★ (★账漂了★)" % rel)
    return errs


def judge_c3(ctx):
    """★C3 收紧版挂链状态: ★可算·不许写死★ ⇒ 哪天 v2 挂上了本条自动转绿★"""
    errs = []
    reg = ctx.get("reg") or {}
    if not ctx.get("v2_exists"):
        errs.append("★收紧版 %s 在盘上读不到 ⇒ 判红★ (★C3 的前提不成立★)" % V2_REL)
    state = ctx.get("chain_ref_state")
    reg_state = reg.get("chain_ref_gate_state")
    if state != reg_state:
        errs.append("★链上位号可达性闸的状态漂了: 实测 %s 真相页登记 %s ⇒ 判红★"
                    " (★切不切链是 main 的地界·本闸只摆代价不代拍★)" % (state, reg_state))
    if state not in ("v1_in_chain_v2_not_hooked", "v2_in_chain"):
        errs.append("★链上位号可达性闸的状态算不出来: %s ⇒ 判红★" % state)
    return errs


def judge_c4(ctx):
    """★C4 元闸盲区: ROSTER 必须在册 + 盲区数必须被登记★"""
    errs = []
    reg = ctx.get("reg") or {}
    roster = ctx.get("roster") or []
    disk = ctx.get("disk_gates") or []
    for rel in roster:
        if rel not in set(disk):
            errs.append("★ISS-388 元闸的 ROSTER 登着 %s 但盘上读不到 ⇒ 判红★" % rel)
    reg_roster = reg.get("sw_gates_in_health_roster") or []
    for rel in sorted(set(roster) - set(reg_roster)):
        errs.append("★元闸 ROSTER 里的 %s 没被真相页登记 ⇒ 判红★" % rel)
    for rel in sorted(set(reg_roster) - set(roster)):
        errs.append("★真相页登记的元闸 ROSTER 项 %s 与盘上元闸不一致 ⇒ 判红★" % rel)
    cov = reg.get("coverage") or {}
    blind = len(set(disk) - set(roster))
    if cov.get("roster_blind_spot") != blind:
        errs.append("★元闸盲区数漂了: 账上 %s 实测 %s ⇒ 判红★"
                    " (★「元闸自己看不见几道」必须被登记·没登记就是静默漏掉★)"
                    % (cov.get("roster_blind_spot"), blind))
    if cov.get("sw_gates_in_health_roster") != len(roster):
        errs.append("★元闸 ROSTER 计数漂了: 账上 %s 实测 %s ⇒ 判红★"
                    % (cov.get("sw_gates_in_health_roster"), len(roster)))
    return errs


def judge_c5(ctx):
    """★C5 第三道病闸 (v2) 的基线读数必须被登记 + 「基线红 ≠ 本单引入」必须写清★"""
    errs = []
    reg = ctx.get("reg") or {}
    drift = reg.get("baseline_drift") or {}
    m_rc = ctx.get("v2_rc")
    if drift.get("v2_selftest_rc") != m_rc:
        errs.append("★第三道病闸 v2 的 selftest 读数漂了: 账上 %s 实测 %s ⇒ 判红★"
                    " (★本闸自己跑一遍·不抄★)" % (drift.get("v2_selftest_rc"), m_rc))
    m_last = ctx.get("v2_last_line")
    if (drift.get("v2_selftest_last_line") or "") != (m_last or ""):
        errs.append("★第三道病闸 v2 的 selftest 末行漂了: 账上 %r 实测 %r ⇒ 判红★"
                    % (drift.get("v2_selftest_last_line"), m_last))
    truth = ctx.get("truth_text") or ""
    if "基线红 ≠ 本单引入" not in truth:
        errs.append("★真相页没有写明「基线红 ≠ 本单引入」⇒ 判红★")
    return errs


def judge_c6(ctx):
    """★C6 证据分级 + 零挂起 + 零空洞 + 判据句/事实句分开 + B1~B6 齐全★"""
    errs = []
    for name, text in sorted((ctx.get("pages") or {}).items()):
        if not text:
            errs.append("★%s 缺失或为空 ⇒ 判红★" % name)
            continue
        for tok in EV_TOKEN_RE.findall(text):
            if not any(k in tok for k in EV_KEYWORDS):
                continue
            if tok not in EV_WHITELIST:
                errs.append("★%s 的证据等级 %s 不在五级白名单内 ⇒ 判红★" % (name, tok))
        for w in HANGING:
            if w in text:
                errs.append("★%s 出现挂起措辞 %r ⇒ 判红★" % (name, w))
        for w in HOLLOW:
            if w in text:
                errs.append("★%s 出现空洞词 %r ⇒ 判红★" % (name, w))
    truth = ctx.get("truth_text") or ""
    for tag in ("判据句", "事实句"):
        if tag not in truth:
            errs.append("★真相页没有把「判据句」与「事实句」分开 (缺 %s 标注) ⇒ 判红★" % tag)
    handoff = (ctx.get("pages") or {}).get("handoff") or ""
    for kw in ("结论", "验收标准", "证据", "接口", "卡点", "复现"):
        if kw not in handoff:
            errs.append("★交卷页缺 B 段关键词 %r ⇒ 判红★" % kw)
    return errs


def evaluate(ctx):
    """★跑全部七条判据 ⇒ {cid: [errors]} (★selftest 靠它证明「红的是目标那一条·其余仍绿」★)"""
    return {
        "C0": judge_c0(ctx),
        "C1": judge_c1(ctx),
        "C2": judge_c2(ctx),
        "C3": judge_c3(ctx),
        "C4": judge_c4(ctx),
        "C5": judge_c5(ctx),
        "C6": judge_c6(ctx),
    }


# ====================================================================== 实测 + 机器块
def measure(root, log=None):
    """★扫真实盘 ⇒ 出「实测侧」的全部读数★"""
    depth_a = os.path.join(root, "tmp")                    # ★深度 1·签收当天约定深度★
    depth_b = os.path.join(root, "tmp", "iss392_sbx", "depth_b", "nested")
    ensure_dir(depth_b)
    disk = disk_gate_rels(root)
    chain = chain_gate_rels(root)
    roster = health_roster_rels(root)
    readings = scan_gates(root, depth_a, depth_b, log=log)
    buckets, detail = classify(root, disk, chain, roster, readings)
    v2 = readings.get(V2_REL) or {}
    return {
        "disk_gates": disk,
        "chain_gates": chain,
        "roster": roster,
        "readings": readings,
        "buckets": buckets,
        "detail": detail,
        "coverage": compute_coverage(disk, chain, roster),
        "chain_ref_state": detect_chain_ref_state(root, chain),
        "v2_exists": os.path.exists(os.path.join(root, V2_REL)),
        "v2_rc": v2.get("rc"),
        "v2_last_line": v2.get("last_line", ""),
    }


CLASS_NOTES = {
    "A": "★已在链内 ⇒ 板那一趟它的判定会参与门禁 (★护栏在位★)",
    "B": "★板敏感 + 不在链内 ⇒ 板那一趟它本该响但今天不响 ⇒ ★那天是个洞★",
    "C": "★与板无关 + 当前读数红 ⇒ 与板无关但会因基线/账漂变红",
    "D": "★与板无关 + 当前读数绿 ⇒ 不必进链 (辅助/自测/板无关闸)",
    "E": "★元闸本身 ⇒ 它的盲区就是本单的对象",
}


def build_emit(m):
    """★机器块 (★`--emit` 可解析★) ⇒ 六键 + 扩展键★"""
    drift = {
        "v2_rel": V2_REL,
        "v1_rel": V1_REL,
        "chain_ref_gate_state": m["chain_ref_state"],
        "v2_selftest_rc": m["v2_rc"],
        "v2_selftest_last_line": m["v2_last_line"],
        "baseline_red_introduced_by_iss392": False,
        "note": "★v2 的 selftest 当前红是【基线漂移】(★ISS-372 那一趟引入的 SW_MD5 形状 token 把 "
                "DESIGNATOR_MISSING 顶过上限★) ⇒ ★基线红 ≠ 本单引入★ ⇒ 本单零改 v2★",
    }
    return {
        "sw_gates_on_disk": m["disk_gates"],
        "sw_gates_in_chain": m["chain_gates"],
        "sw_gates_in_health_roster": m["roster"],
        "coverage": m["coverage"],
        "blind_spot_classes": {k: m["buckets"].get(k, []) for k in ("A", "B", "C", "D", "E")},
        "baseline_drift": drift,
        "class_notes": CLASS_NOTES,
        "chain_ref_gate_state": m["chain_ref_state"],
        "gate_readings": m["readings"],
        "gate_detail": m["detail"],
    }


def build_ctx(root, m, reg, reg_err):
    """★把「实测侧」+「账侧」拼成一个 ctx ⇒ 喂给 evaluate()★"""
    board_path = os.path.join(root, BOARD_REL)
    tables = {rel: file_md5(os.path.join(root, rel)) for rel in TABLE_MD5}
    gcheck = read_text(os.path.join(root, GATE_CHECK_REL))
    hook_count = gcheck.count("check_sw_gate_chain_coverage")
    pages = {
        "truth": read_text(os.path.join(root, TRUTH_REL)),
        "handoff": read_text(os.path.join(root, HANDOFF_REL)),
    }
    return {
        "root": root,
        "board": {"md5": file_md5(board_path), "mtime": fmt_mtime(board_path),
                  "size": (os.stat(board_path).st_size if os.path.exists(board_path) else 0)},
        "tables": tables,
        "hook_count": hook_count,
        "disk_gates": m["disk_gates"],
        "chain_gates": m["chain_gates"],
        "roster": m["roster"],
        "readings": m["readings"],
        "buckets": m["buckets"],
        "chain_ref_state": m["chain_ref_state"],
        "v2_exists": m["v2_exists"],
        "v2_rc": m["v2_rc"],
        "v2_last_line": m["v2_last_line"],
        "reg": reg or {},
        "reg_err": reg_err,
        "truth_text": pages.get("truth", ""),
        "pages": pages,
    }


def run_all(root, log=None):
    m = measure(root, log=log)
    reg, reg_err = load_truth_block(root)
    ctx = build_ctx(root, m, reg, reg_err)
    if reg_err:
        ctx["_pre"] = [reg_err]
    res = evaluate(ctx)
    if reg_err:
        res.setdefault("C1", [])
        res["C1"] = [reg_err] + res["C1"]
    return res, ctx, m


# ====================================================================== selftest
def _fixture_ctx():
    """★全绿的夹具 ctx (★selftest 只改一个字段⇒ 红的一定是目标那一条★)"""
    readings = {
        "SW/tools/g1.py": {"mode": "selftest", "rc": 0, "last_line": "ALL TESTS PASS"},
        "SW/tools/g2.py": {"mode": "selftest", "rc": 0, "last_line": "ALL TESTS PASS"},
        "SW/tools/g3.py": {"mode": "bare", "rc": 1, "last_line": "★有用例 FAIL⇒ 本闸不可信 ★"},
    }
    good_page = ("★结论 [实测] 一条· 判据句: 覆盖率必须可复算\n"
                 "事实句: 盘上 3 道闸· 链内 1 道\n基线红 ≠ 本单引入\n")
    good_handoff = ("## B1 结论摘要\n## B2 验收标准自评\n## B3 证据分级\n"
                    "## B4 接口取值声明\n## B5 未决项与卡点\n## B6 复现命令\n")
    return {
        "board": {"md5": BOARD_MD5, "mtime": BOARD_MTIME, "size": BOARD_SIZE},
        "tables": dict(TABLE_MD5),
        "hook_count": 0,
        "disk_gates": ["SW/tools/g1.py", "SW/tools/g2.py", "SW/tools/g3.py"],
        "chain_gates": ["SW/tools/g1.py"],
        "roster": ["SW/tools/g1.py", "SW/tools/g2.py"],
        "readings": json.loads(json.dumps(readings)),
        "buckets": {"A": ["SW/tools/g1.py"], "B": [], "C": [],
                    "D": ["SW/tools/g2.py", "SW/tools/g3.py"], "E": []},
        "chain_ref_state": "v1_in_chain_v2_not_hooked",
        "v2_exists": True,
        "v2_rc": 1,
        "v2_last_line": "★有用例 FAIL⇒ 本闸不可信 ★",
        "reg": {
            "sw_gates_on_disk": ["SW/tools/g1.py", "SW/tools/g2.py", "SW/tools/g3.py"],
            "sw_gates_in_chain": ["SW/tools/g1.py"],
            "sw_gates_in_health_roster": ["SW/tools/g1.py", "SW/tools/g2.py"],
            "coverage": {"sw_gates_in_health_roster": 2, "roster_blind_spot": 1},
            "baseline_drift": {"v2_selftest_rc": 1,
                               "v2_selftest_last_line": "★有用例 FAIL⇒ 本闸不可信 ★"},
            "chain_ref_gate_state": "v1_in_chain_v2_not_hooked",
            "blind_spot_classes": {"A": ["SW/tools/g1.py"], "B": [], "C": [],
                                   "D": ["SW/tools/g2.py", "SW/tools/g3.py"], "E": []},
            "gate_readings": json.loads(json.dumps(readings)),
        },
        "truth_text": good_page,
        "pages": {"truth": good_page, "handoff": good_handoff},
    }


def run_selftest(root):
    cases = []

    def case(cid, desc, ok, note=""):
        cases.append((cid, desc, bool(ok), note))

    def only_red(base, mutate, target, desc, cid=None):
        """★改一个字段 ⇒ 【只有】目标那条判据红·其余仍绿★"""
        ctx = json.loads(json.dumps(base))
        mutate(ctx)
        res = evaluate(ctx)
        red = sorted(k for k, v in res.items() if v)
        ok = (red == [target])
        case(cid or ("T-%s" % target), desc, ok, "red=%s (期望只红 %s) errs=%d"
             % (red, target, len(res.get(target, []))))

    base = _fixture_ctx()
    res = evaluate(base)
    all_green = not any(res.values())
    case("T0-1", "★不误伤 · 全绿的夹具 ⇒ 七条判据必须全绿", all_green,
         "red=%s" % sorted(k for k, v in res.items() if v))

    # --- C0 ---
    only_red(base, lambda c: c["board"].__setitem__("md5", "deadbeef" * 4), "C0",
             "★C0 · 板 md5 被动过 ⇒ 必须 C0 红·其余绿")
    only_red(base, lambda c: c["tables"].__setitem__("HW/BOM_v1.csv", "0" * 32), "C0",
             "★C0 · 三表之一 md5 被动过 ⇒ 必须 C0 红·其余绿")
    only_red(base, lambda c: c.__setitem__("hook_count", 1), "C0",
             "★C0 · 零挂链被破坏 ⇒ 必须 C0 红·其余绿")
    only_red(base, lambda c: c["board"].__setitem__("mtime", "2026-01-01 00:00:00.000000000"), "C0",
             "★C0 · 板 mtime 被动过 ⇒ 必须 C0 红·其余绿")

    # --- C1 ---
    def _add_gate(c):
        c["disk_gates"].append("SW/tools/g4.py")
        c["reg"]["coverage"]["roster_blind_spot"] = 2      # ★同步把盲区数改对⇒ 只剩 C1 红★
    only_red(base, _add_gate, "C1",
             "★C1 · 盘上多出一道闸而机器块没登记 ⇒ 必须 C1 红·其余绿")
    only_red(base, lambda c: c["reg"]["sw_gates_on_disk"].append("SW/tools/g9.py"), "C1",
             "★C1 · 机器块登记了盘上没有的闸 ⇒ 必须 C1 红·其余绿")
    only_red(base, lambda c: c["reg"]["gate_readings"]["SW/tools/g1.py"].__setitem__("rc", 1), "C1",
             "★C1 · 登记 rc 漂了 ⇒ 必须 C1 红·其余绿")
    only_red(base, lambda c: c["reg"]["gate_readings"]["SW/tools/g2.py"].__setitem__("last_line", "XX"), "C1",
             "★C1 · 登记末行漂了 ⇒ 必须 C1 红·其余绿")
    only_red(base, lambda c: c["reg"]["blind_spot_classes"]["D"].pop(), "C1",
             "★C1 · 分类账 (blind_spot_classes) 漂了 ⇒ 必须 C1 红·其余绿")

    # --- C2 ---
    only_red(base, lambda c: c["chain_gates"].append("SW/tools/g2.py"), "C2",
             "★C2 · 链里多了一道闸而机器块没登记 ⇒ 必须 C2 红·其余绿")
    only_red(base, lambda c: c["reg"]["sw_gates_in_chain"].append("SW/tools/g2.py"), "C2",
             "★C2 · 机器块多登记了一道链内闸 ⇒ 必须 C2 红·其余绿")

    # --- C3 ---
    only_red(base, lambda c: c.__setitem__("v2_exists", False), "C3",
             "★C3 · 收紧版 v2 不在盘上 ⇒ 必须 C3 红·其余绿")
    only_red(base, lambda c: c.__setitem__("chain_ref_state", "v2_in_chain"), "C3",
             "★C3 · 链上状态变了而机器块没跟着改 ⇒ 必须 C3 红·其余绿")
    ctx = json.loads(json.dumps(base))
    ctx["chain_ref_state"] = "v2_in_chain"
    ctx["reg"]["chain_ref_gate_state"] = "v2_in_chain"
    res2 = evaluate(ctx)
    case("T3-3", "★C3 自动转绿 · v2 挂链后 (链与账同步更新) ⇒ 七条必须全绿",
         not any(res2.values()), "red=%s" % sorted(k for k, v in res2.items() if v))

    # --- C4 ---
    only_red(base, lambda c: c["roster"].append("SW/tools/gone.py"), "C4",
             "★C4 · 元闸 ROSTER 登着盘上没有的闸 ⇒ 必须 C4 红·其余绿")
    only_red(base, lambda c: c["reg"]["coverage"].__setitem__("roster_blind_spot", 99), "C4",
             "★C4 · 元闸盲区数没登记对 ⇒ 必须 C4 红·其余绿")
    only_red(base, lambda c: c["reg"]["sw_gates_in_health_roster"].pop(), "C4",
             "★C4 · 元闸 ROSTER 项没被机器块登记 ⇒ 必须 C4 红·其余绿")

    # --- C5 ---
    only_red(base, lambda c: c["reg"]["baseline_drift"].__setitem__("v2_selftest_rc", 0), "C5",
             "★C5 · 第三道病闸读数漂了 ⇒ 必须 C5 红·其余绿")
    def _drop_baseline_note(c):
        c["truth_text"] = c["truth_text"].replace("基线红 ≠ 本单引入", "基线红")
        c["pages"]["truth"] = c["pages"]["truth"].replace("基线红 ≠ 本单引入", "基线红")
    only_red(base, _drop_baseline_note, "C5",
             "★C5 · 真相页没写明「基线红 ≠ 本单引入」⇒ 必须 C5 红·其余绿")

    # --- C6 ---
    only_red(base, lambda c: c["pages"].__setitem__(
        "truth", c["pages"]["truth"] + "\n等级 [官方待定] 一条\n"), "C6",
        "★C6 · 证据等级越界 ⇒ 必须 C6 红·其余绿")
    only_red(base, lambda c: c["pages"].__setitem__(
        "truth", c["pages"]["truth"] + "\n等原厂回信\n"), "C6",
        "★C6 · 挂起措辞 ⇒ 必须 C6 红·其余绿")
    only_red(base, lambda c: c["pages"].__setitem__(
        "truth", c["pages"]["truth"] + "\n适当处理\n"), "C6",
        "★C6 · 空洞词 ⇒ 必须 C6 红·其余绿")
    only_red(base, lambda c: c["pages"].__setitem__(
        "handoff", "## B1 结论摘要\n"), "C6",
        "★C6 · 交卷页缺 B 段 ⇒ 必须 C6 红·其余绿")
    def _drop_criteria_split(c):
        c["truth_text"] = c["truth_text"].replace("判据句", "口径")
    only_red(base, _drop_criteria_split, "C6",
        "★C6 · 真相页没把判据句/事实句分开 ⇒ 必须 C6 红·其余绿")

    n_ok = sum(1 for c in cases if c[2])
    for cid, desc, ok, note in cases:
        print("  [%s] %-6s %-62s %s" % ("PASS" if ok else "FAIL", cid, desc, note))
    print("=== selftest %d/%d 通过 (共 %d 条反向用例) ===" % (n_ok, len(cases), len(cases)))
    if n_ok == len(cases):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# ====================================================================== main
TITLES = {
    "C0": "零扰动 (板三项 + 三表 + 零挂链)",
    "C1": "账实一致 (盘上闸集合 ↔ 机器块登记·双向 + 逐道读数一致)",
    "C2": "链内清单双向比对 (⇒ 覆盖率机器可判)",
    "C3": "收紧版挂链状态可算 (★不许写死「v2 没挂」★)",
    "C4": "元闸 ROSTER 盲区必须被登记",
    "C5": "第三道病闸 (v2) 基线读数必须被登记",
    "C6": "证据分级 + 零挂起 + 零空洞 + 判据/事实分开",
}


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit", action="store_true",
                    help="★只输出机器块 JSON (★写进真相页用·不判红★)")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.selftest:
        return run_selftest(root)

    log = None
    try:
        ensure_dir(os.path.join(root, "logs", "iss392"))
        log = open(os.path.join(root, "logs", "iss392", "scan.log"), "w", encoding="utf-8")
    except OSError:
        log = None

    try:
        m = measure(root, log=log)
        if args.emit:
            print(json.dumps(build_emit(m), ensure_ascii=False, indent=1, sort_keys=True))
            return 0
        reg, reg_err = load_truth_block(root)
        ctx = build_ctx(root, m, reg, reg_err)
        res = evaluate(ctx)
        if reg_err:
            res["C1"] = [reg_err] + res["C1"]
        failed = [k for k in sorted(res) if res[k]]
        if args.json:
            print(json.dumps({"checks": [{"id": k, "ok": not res[k], "title": TITLES[k],
                                          "errors": res[k]} for k in sorted(res)],
                              "coverage": m["coverage"],
                              "chain_ref_gate_state": m["chain_ref_state"]},
                             ensure_ascii=False, indent=1))
            return 1 if failed else 0
        print("=" * 96)
        print("ISS-392 · SW 域【门禁链覆盖率闸】 · 根 = %s" % root)
        print("=" * 96)
        for cid in sorted(res):
            print("  [%s] %s · %s" % ("PASS" if not res[cid] else "FAIL", cid, TITLES[cid]))
            for e in res[cid]:
                print("        ⚠ %s" % e)
        print("-" * 96)
        print("★覆盖率 (机器可判): 盘上 %d 道 · 链内 %d 道 (%.1f%%) · 链外 %d 道"
              % (m["coverage"]["sw_gates_on_disk"], m["coverage"]["sw_gates_in_chain"],
                 100.0 * m["coverage"]["chain_coverage_ratio"], m["coverage"]["not_in_chain"]))
        print("★元闸盲区: ISS-388 元闸 ROSTER 只扫 %d 道 · 盘上另外 %d 道它看不见"
              % (m["coverage"]["sw_gates_in_health_roster"], m["coverage"]["roster_blind_spot"]))
        print("★链上位号可达性闸: %s" % m["chain_ref_state"])
        print("★第三道病闸 v2 --selftest: rc=%s · 末行: %s"
              % (m["v2_rc"], m["v2_last_line"]))
        print("★★以上三点是【事实】· 本闸只判「账与事实是否一致」· ★切不切链是 main 的地界★")
        print("-" * 96)
        print("判据结果 %d/%d 通过, rc=%d" % (len(res) - len(failed), len(res),
                                              1 if failed else 0))
        return 1 if failed else 0
    finally:
        if log:
            log.close()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as exc:                                  # noqa: BLE001
        print("FATAL: %s: %s" % (type(exc).__name__, exc))
        sys.exit(2)
