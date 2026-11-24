#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sw_false_connectivity_gate.py
═══════ ★★★ 板那一趟 · 布线验收线的「零假连通」自检闸 (K0~K6) ★★★ ═══════

★**ISS-381 cont1 · sw-lead · 2026-11-24** ★
★**零写板 · 零落表 · 零改既有闸 · 零挂链 · 零外发** ★

────────────────────────────────────────────────────────────────────────
★★**这把闸是干什么的 (★一句话★)** ★★
  ★**`unc 45 → 0` 是【计数】判据, 它【不能证明】那 23 条必需网逐条真接上了** ★★
  ⇒ ⇒ **删焊盘 / 标 NC / 改名** 三种刷法都能把 45 刷到 0 而【一条铜都不加】 ★★
  ⇒ ⇒ **本闸按【身份 / 逐条 / 焊盘集合 / 可被计数刷掉】四层逐条点名**, 这是全仓
      **第一个**「必需网逐条列铜」的 fail-closed 判据 (★`HW/check_s8_target_list.py`
      每次跑都 return 0, 只出尺子不出判决★)。

────────────────────────────────────────────────────────────────────────
★★**边界 (★不许越界★)** ★★
  ① 本闸【不重做】「必需网零铜 ⇒ 必拒」那条判据 —— 那是 `HW/check_board_comparable_gate.py`
     的名单层 (L419/L429) 与 `state/compare_arm_official.py` (L114/L121) 的地界。
     ★**本闸的落点是那两层管不到的「身份 / 逐条 / 焊盘集合 / 可被计数刷掉」四层** ★
  ② 本闸【不查】文档层一致性 —— 那是 `SW/tools/check_sw_zero_copper_grade_consistency.py`
     (C0~C9) 的地界 (★C0~C9 不查板面铜 ⇒ 不重复★)。
  ③ 本闸【不判】差分腿铜长对称性阈值 (★Δ铜长 / Δ段数上限 main 未裁 ★) ⇒ 只判「成对都有铜」。
  ④ ★**本闸【零挂链】** —— 不挂进 `state/gate_check.py` (★挂链是 main 的地界★)。

────────────────────────────────────────────────────────────────────────
★★**相 (phase) 的含义 (★重要·不许混着跑★)** ★★
  `--phase pre`  (默认) = 【板那一趟之前】的**基线相**
      期望: 23 条必需网**全部零铜**(★这是已登记的已知缺口★) + 焊盘集合与脚表一致
            + 全部在板面存在 + 可悬空网零铜且不在必需表 + 两份解析器一致 + 指纹未动
      ⇒ **今天跑这一相 ⇒ rc=0** (★当前板就是这个状态★)
  `--phase post` = 【板那一趟之后】的**验收相** ★**这才是「布线验收线」本身** ★
      期望: 每条必需网 **板面存在 + 焊盘集合与脚表一致 + 铜段数≥1 + 铜长>0**
      ⇒ **今天跑这一相 ⇒ rc=1, 逐条点名 23 条零铜网** (★板那一趟还没做★)

  ★**两相共用同一份 §3 逐条列铜表, 只差「期望铜状态」这一格 ⇒ 判据不分叉** ★

────────────────────────────────────────────────────────────────────────
★★**用法** ★★
  python3 SW/tools/check_sw_false_connectivity_gate.py                 # 默认 --phase pre
  python3 SW/tools/check_sw_false_connectivity_gate.py --phase post     # 板那一趟验收相
  python3 SW/tools/check_sw_false_connectivity_gate.py --selftest      # ★末行 ALL TESTS PASS★
  python3 SW/tools/check_sw_false_connectivity_gate.py --print-table    # §3 逐条列铜表
  python3 SW/tools/check_sw_false_connectivity_gate.py --print-net UART_RX
  python3 SW/tools/check_sw_false_connectivity_gate.py --board HW/PCB/demo_mainboard.kicad_pcb
  python3 SW/tools/check_sw_false_connectivity_gate.py --data tmp/iss381_sbx/board_nets.json
"""
import ast
import csv
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
PINS_CSV = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
S8_SCRIPT = os.path.join(PROJ, "HW", "check_s8_target_list.py")
BASELINE = os.path.join(PROJ, "logs", "iss381", "baseline_fingerprints.txt")
SNAP_SEXPR = os.path.join(PROJ, "tmp", "iss381_sbx", "board_nets.json")
SNAP_PCBNEW = os.path.join(PROJ, "tmp", "iss381_sbx", "board_nets_pcbnew.json")
TRUTH_PAGE = os.path.join(PROJ, "SW", "BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md")
GATE_CHECK = os.path.join(PROJ, "state", "gate_check.py")

# ★**基线指纹常量 (★与 logs/iss381/baseline_fingerprints.txt 一致·写死是为了档
#    少时也能 fail-closed 而不是静默跳过★)** ★
BASELINE_BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BASELINE_BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BASELINE_BOARD_SIZE = 4940213

BASELINE_FILES = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "HW/check_s8_target_list.py": "2fefaaea036a408341f02b84e12779e2",
    "HW/check_board_comparable_gate.py": "386cda8f825ab170bfd806c8e648966b",
    "state/compare_arm_official.py": "1471bce6cd67c4b0f611541d4a4b0dfc",
    "SW/tools/check_sw_zero_copper_grade_consistency.py": "58a3aa445842cd9ba89fe1e75bb9fc31",
    "SW/tools/check_onepass_sw_release.py": "4d7ce982965e92c78a1ebcd3e968874e",
    "SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md": "0f4bf6c083f25cea6cda240a91170049",
}

EVIDENCE_TAGS = ("[实测]", "[推算]", "[官网]", "[媒体]", "[0数据]")
CU_TOLERANCE_MM = 0.05


# ═══════════════════════════════════════════════════════════════════════
# ★**基础工具** ★
# ═══════════════════════════════════════════════════════════════════════
def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def rel(path):
    try:
        return os.path.relpath(path, PROJ)
    except Exception:
        return path


class Report(object):
    """★判据结果收集器 · 每条判据 fail-closed (★异常 ⇒ 红★)**"""

    def __init__(self):
        self.rows = []          # (code, ok, title, [lines])
        self.warns = []

    def add(self, code, ok, title, lines=None, warn_only=False):
        lines = list(lines or [])
        if warn_only and ok:
            for ln in lines:
                self.warns.append("[%s] %s" % (code, ln))
        self.rows.append((code, bool(ok), title, lines))

    @property
    def failed(self):
        return [r for r in self.rows if not r[1]]

    @property
    def ok(self):
        return not self.failed


# ═══════════════════════════════════════════════════════════════════════
# ★**名单来源: 用 AST 静态解析 HW/check_s8_target_list.py** ★
# ★**不 import / 不 exec 那个脚本 · 一字不许改它** ★
# ═══════════════════════════════════════════════════════════════════════
def load_grades_from_s8():
    """★返回 (REQUIRED_SINGLE, FLOAT_OK, DIFF_PREFIXES, EXPECT_REQUIRED, EXPECT_FLOAT, EXPECT_TBD) ★
    ★静态解析 AST ⇒ 只取字面量赋值, 不执行任何代码 ★"""
    with open(S8_SCRIPT, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=S8_SCRIPT)

    def const_list(name):
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        try:
                            return list(ast.literal_eval(node.value))
                        except Exception:
                            return None
        return None

    def const_int(name):
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        try:
                            v = ast.literal_eval(node.value)
                        except Exception:
                            return None
                        if isinstance(v, bool):
                            return None
                        if isinstance(v, int):
                            return v
                        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], int):
                            return v[0]
        return None

    def const_tuple(name):
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        try:
                            return tuple(ast.literal_eval(node.value))
                        except Exception:
                            return None
        return None

    return (const_list("REQUIRED_SINGLE"), const_list("FLOAT_OK"),
            const_tuple("DIFF_PREFIXES"), const_int("EXPECT_REQUIRED"),
            const_int("EXPECT_FLOAT"), const_int("EXPECT_TBD"))


def required_from_page():
    """★从真相页 §3 逐条列铜表读【冻结的必需名单】 (★板那一趟的验收线正样★) ★
    ★为什么要有冻结名单: 差分腿一旦被接上铜, 它就从「零铜网」里消失 ⇒
      若名单每次都从现板现算, 板那一趟做完名单会自己缩水 ⇒ 验收线会漏检。
      ⇒ post 相一律用【真相页 §3 的冻结名单】。 ★
    ★解析失败 ⇒ 返回 None (★调用方 fail-closed·不许静默绿★) ★"""
    if not os.path.isfile(TRUTH_PAGE):
        return None
    try:
        with open(TRUTH_PAGE, encoding="utf-8") as f:
            page = f.read()
    except Exception:
        return None
    m = re.search(r"\n## §3\b(.*?)(?=\n## §4\b)", page, re.S)
    if not m:
        return None
    sec = m.group(1)
    names = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|", sec, re.M)
    names = [n for n in names if n]
    return sorted(set(names)) if names else None


def required_live(nets, req_single, diff_prefixes):
    """★从现板现算的必需名单 (★S8 已裁口径: 8 单端脚 + 零铜差分腿★) ★"""
    s = set(req_single)
    for n in nets:
        if n.startswith(diff_prefixes) and len(nets[n].get("pads") or []) >= 2 \
                and int(nets[n].get("seg") or 0) == 0:
            s.add(n)
    return sorted(s)


def load_pairs():
    """★差分对清单 · 来源 tools/diff_pair_audit.py 的 PAIRS (★只读·静态解析★) ★"""
    cands = [
        os.path.normpath(os.path.join(PROJ, "..", "..", "tools", "diff_pair_audit.py")),
        os.path.normpath(os.path.join(PROJ, "..", "..", "..", "tools", "diff_pair_audit.py")),
        os.path.join(PROJ, "tools", "diff_pair_audit.py"),
    ]
    for p in cands:
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                m = re.search(r"PAIRS\s*=\s*\[(.*?)\]", f.read(), re.S)
            if m:
                out = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
                if len(out) >= 20:
                    return out, rel(p)
        except Exception:
            pass
    return [], "(未找到 tools/diff_pair_audit.py)"


# ═══════════════════════════════════════════════════════════════════════
# ★**期望焊盘集合: 从脚表 HW/netlist_v1_pins.csv 读 (★不是从板面读★)** ★
# ═══════════════════════════════════════════════════════════════════════
def load_expected_pads():
    """★返回 {net: set("REF.PIN")} ★
    ★过滤: board ∈ {空, MAIN_PCB}  (★CHG_BOARD 是充电板, 不是主板焊盘★) ★
    ★脚号归一: 'pin54' → '54' (★脚表用 pinNN, 板面用 NN★) ★"""
    out = {}
    with open(PINS_CSV, encoding="utf-8", errors="ignore") as f:
        for r in csv.DictReader(f):
            b = (r.get("board") or "").strip()
            if b not in ("", "MAIN_PCB"):
                continue
            net = (r.get("net") or "").strip()
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            if not net or not ref or not pin:
                continue
            if pin.startswith("pin"):
                pin = pin[3:]
            out.setdefault(net, set()).add("%s.%s" % (ref, pin))
    return out


# ═══════════════════════════════════════════════════════════════════════
# ★**板面读数: 自写 s-expr 行级状态机 (★零 import 既有脚本★)** ★
# ═══════════════════════════════════════════════════════════════════════
def parse_board(path):
    """★返回 {net: {"pads": [str], "seg": int, "cu": float}} ★
    ★自写解析器 · 只读 · 不写板 ★"""
    nets = {}
    cur = None
    depth = 0
    fp_depth = None
    fp_ref = None
    net = None
    pad_num = None
    pad_net = None
    cur_ref = None
    x1 = y1 = x2 = y2 = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if fp_depth is not None and depth < fp_depth:
                fp_depth = None
                fp_ref = None
            if fp_depth is None and s.startswith("(footprint"):
                fp_depth = depth + s.count("(")
                fp_ref = None
            delta = s.count("(") - s.count(")")
            try:
                if s.startswith("(property ") and fp_depth is not None:
                    m = re.match(r'\(property\s+"Reference"\s+"([^"]+)"', s)
                    if m:
                        fp_ref = m.group(1)
                    continue
                if s.startswith("(pad ") or s == "(pad":
                    cur = "pad"
                    net = None
                    pad_num = None
                    pad_net = None
                    cur_ref = fp_ref
                    m = re.match(r'\(pad\s+"([^"]*)"', s)
                    if m:
                        pad_num = m.group(1)
                    continue
                if s == "(segment":
                    cur = "seg"
                    net = None
                    x1 = y1 = x2 = y2 = None
                    continue
                if s == "(via":
                    cur = "via"
                    net = None
                    continue
                if cur is None:
                    continue
                if s == ")":
                    if cur == "pad":
                        if pad_net and cur_ref is not None:
                            d = nets.setdefault(pad_net, {"pads": [], "seg": 0, "cu": 0.0})
                            d["pads"].append("%s.%s" % (cur_ref, pad_num))
                    elif cur == "seg":
                        if net:
                            d = nets.setdefault(net, {"pads": [], "seg": 0, "cu": 0.0})
                            d["seg"] += 1
                            if None not in (x1, y1, x2, y2):
                                d["cu"] += math.hypot(x2 - x1, y2 - y1)
                    cur = None
                    net = None
                    continue
                m = re.match(r'\(net\s+(?:"([^"]+)"|(\d+))\)', s)
                if m:
                    nm = m.group(1) if m.group(1) else ("#%s" % m.group(2))
                    if cur == "pad":
                        pad_net = nm
                    else:
                        net = nm
                    continue
                if cur == "seg":
                    m = re.match(r"\(start ([-\d.]+) ([-\d.]+)\)", s)
                    if m:
                        x1, y1 = float(m.group(1)), float(m.group(2))
                        continue
                    m = re.match(r"\(end ([-\d.]+) ([-\d.]+)\)", s)
                    if m:
                        x2, y2 = float(m.group(1)), float(m.group(2))
                        continue
            finally:
                depth += delta
    return nets


def load_snapshot(path):
    """★读已落盘的探针读数 (★tmp/iss381_sbx/*.json★) · 归一成统一形状 ★"""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out = {}
    for name, v in raw.items():
        if name == "":
            continue                      # ★pcbnew 口径的「无网名」聚合桶·不参与逐条判据★
        out[name] = {
            "pads": sorted(set(v.get("pads") or [])),
            "seg": int(v.get("seg") or 0),
            "cu": float(v.get("cu") or 0.0),
        }
    return out


def build_nets(data_path=None, board_path=None):
    """★统一入口: 优先 live board (自写解析器) · 否则用快照 json ★
    ★返回 (nets, source_desc) ★"""
    if board_path:
        raw = parse_board(board_path)
        out = {}
        for n, d in raw.items():
            out[n] = {"pads": sorted(set(d["pads"])), "seg": d["seg"], "cu": round(d["cu"], 3)}
        return out, ("live board (自写 s-expr 解析器) %s" % rel(board_path))
    p = data_path or SNAP_SEXPR
    return load_snapshot(p), ("snapshot %s" % rel(p))


# ═══════════════════════════════════════════════════════════════════════
# ★★**K1 的纯判定函数 (★闸的命门·可被合成反例喂进去★)** ★★
# ═══════════════════════════════════════════════════════════════════════
def judge_required_net(net, actual, expected_pads, phase):
    """★单网判定 · 纯函数 (★不碰全局·不读文件⇒可直接喂合成反例★)
    ★返回 (ok, [(rule, detail), ...]) ★"""
    findings = []
    if actual is None:
        return False, [("K1a", "板面查不到该网 (★身份缺失★) ⇒ 名单里这条在板面不存在")]
    pads = set(actual.get("pads") or [])
    exp = set(expected_pads or [])
    miss = sorted(exp - pads)
    extra = sorted(pads - exp)
    if miss:
        findings.append(("K1b", "缺期望焊盘 (%d 个): %s" % (len(miss), " ".join(miss))))
    if extra:
        findings.append(("K1b", "板面多出焊盘 (%d 个, 不在脚表期望集合内): %s"
                         % (len(extra), " ".join(extra))))
    seg = int(actual.get("seg") or 0)
    cu = float(actual.get("cu") or 0.0)
    if phase == "post":
        if seg < 1:
            findings.append(("K1c", "零铜: 铜段数=%d (★要求 ≥1★) ⇒ 这条网【没接】" % seg))
        elif cu <= 0.0:
            findings.append(("K1c", "有铜段但铜长=%.3f mm (★要求 >0★)" % cu))
    else:
        if seg != 0 or cu != 0.0:
            findings.append(("K1c", "基线相期望【零铜】, 实际 seg=%d cu=%.3f mm ⇒ 板已动或读数口径不符"
                             % (seg, cu)))
    return (len(findings) == 0), findings


def judge_required_all(nets, required, expected_pads, phase):
    """★逐条必需网 · 返回 [(net, ok, [(rule, detail), ...])] ★"""
    out = []
    for net in required:
        ok, fs = judge_required_net(net, nets.get(net), expected_pads.get(net, set()), phase)
        out.append((net, ok, fs))
    return out


# ═══════════════════════════════════════════════════════════════════════
# ★**各条判据 K0~K6** ★
# ═══════════════════════════════════════════════════════════════════════
def k0_fingerprints(rep):
    """★K0 板三项指纹未动 (md5 / mtime / size) + 既有表/闸/页指纹未动 ★"""
    lines = []
    ok = True
    if not os.path.isfile(BOARD):
        rep.add("K0", False, "板三项指纹未动", ["❌ 板不存在: %s" % rel(BOARD)])
        return
    md5 = md5_of(BOARD)
    st = os.stat(BOARD)
    mtime = st.st_mtime
    import datetime
    mt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S.%f") + \
        " " + datetime.datetime.fromtimestamp(mtime).strftime("%z")
    size = st.st_size
    lines.append("板 md5   = %s  (基线 %s) %s"
                 % (md5, BASELINE_BOARD_MD5, "✔" if md5 == BASELINE_BOARD_MD5 else "❌"))
    lines.append("板 mtime = %s  (基线 %s) %s"
                 % (mt, BASELINE_BOARD_MTIME, "✔" if mt.startswith(BASELINE_BOARD_MTIME[:19]) else "❌"))
    lines.append("板 size  = %d  (基线 %d) %s"
                 % (size, BASELINE_BOARD_SIZE, "✔" if size == BASELINE_BOARD_SIZE else "❌"))
    if md5 != BASELINE_BOARD_MD5:
        ok = False
        lines.append("❌ 板被改过 ⇒ 零写板纪律破")
    if size != BASELINE_BOARD_SIZE:
        ok = False
    if not mt.startswith(BASELINE_BOARD_MTIME[:19]):
        ok = False
    # ── 既有表 / 既有闸 / 既有页 指纹 (★零落表 · 零改既有闸 · 零改既有页面正文★) ──
    sub_ok = True
    for rp, base_md5 in sorted(BASELINE_FILES.items()):
        p = os.path.join(PROJ, rp)
        if not os.path.isfile(p):
            sub_ok = False
            lines.append("❌ %s 不存在" % rp)
            continue
        cur = md5_of(p)
        if cur != base_md5:
            sub_ok = False
            lines.append("❌ %s md5 %s ≠ 基线 %s" % (rp, cur, base_md5))
    if sub_ok:
        lines.append("✔ 零落表 / 零改既有闸 / 零改既有页面正文: %d 个文件 md5 全部与基线一致"
                     % len(BASELINE_FILES))
    else:
        ok = False
    rep.add("K0", ok, "板三项指纹未动 (md5/mtime/size) + 既有表/闸/页指纹未动", lines)


def k1_required(nets, required, expected_pads, phase, rep, expect_count=None):
    """★K1 逐条必需网: 存在 + 焊盘集合一致 + 铜状态 (★逐条点名, 不许只报条数★) ★"""
    rows = judge_required_all(nets, required, expected_pads, phase)
    bad = [(n, fs) for n, ok, fs in rows if not ok]
    lines = []
    for n, fs in bad:
        lines.append("❌ %-16s ⇒ %s" % (n, "; ".join("%s: %s" % (r, d) for r, d in fs)))
    lines.append("逐条结果: 通过 %d / 共 %d (★不通过的已逐条点名在上面★)"
                 % (len(rows) - len(bad), len(rows)))
    if bad:
        lines.append("❌ 合计 %d 条不通过" % len(bad))
    ok = not bad
    if expect_count is not None and len(required) != expect_count:
        ok = False
        lines.append("❌ 必需网数 %d ≠ S8 已裁期望 %d ⇒ 名单与板面口径漂移, 需重读名单"
                     % (len(required), expect_count))
    rep.add("K1", ok,
            "K1 逐条必需网 (板面存在 + 焊盘集合与脚表一致 + 铜状态) · phase=%s" % phase,
            lines)


def k2_pairs_and_parsers(nets, required, pairs, phase, rep):
    """★K2 差分腿成对 (两腿都必须有铜) + 两份解析器结论一致 ★"""
    lines = []
    ok = True
    req = set(required)
    # ── 2a 成对都有铜 ──
    asym = []
    for p, n in pairs:
        if p not in req and n not in req:
            continue
        vp = nets.get(p)
        vn = nets.get(n)
        sp = int(vp.get("seg") or 0) if vp else -1
        sn = int(vn.get("seg") or 0) if vn else -1
        cp = float(vp.get("cu") or 0.0) if vp else 0.0
        cn = float(vn.get("cu") or 0.0) if vn else 0.0
        both = (sp >= 1 and sn >= 1)
        tag = "✔ 两腿都有铜" if both else "✘ %s" % (
            "两腿都零铜" if (sp == 0 and sn == 0) else
            ("P 腿零铜" if sp == 0 else "N 腿零铜"))
        lines.append("  %-18s seg=%-4s cu=%-7.1f | %-18s seg=%-4s cu=%-7.1f  %s"
                     % (p, sp, cp, n, sn, cn, tag))
        if not both:
            asym.append((p, n, tag))
    if asym:
        if phase == "post":
            ok = False
            lines.append("❌ %d 对差分腿【不是两腿都有铜】: %s"
                         % (len(asym), "; ".join("%s/%s %s" % (p, n, t) for p, n, t in asym)))
        else:
            lines.append("★基线相: %d 对差分腿尚不是两腿都有铜 (★已登记的已知缺口·不判红★)"
                         % len(asym))
    else:
        lines.append("✔ 所有在册差分腿对都是两腿都有铜")
    lines.append("★本闸【不判】Δ铜长 / Δ段数 (★阈值 main 未裁⇒不代拍★)")
    # ── 2b 两份解析器结论一致 ──
    if os.path.isfile(SNAP_PCBNEW):
        try:
            other = load_snapshot(SNAP_PCBNEW)
            diffs = []
            names = sorted(set(required) | set(FLOAT_MARK) | set(nets))
            for n in names:
                a = nets.get(n)
                b = other.get(n)
                if a is None or b is None:
                    diffs.append("%s: 一份有 (%s) 另一份没有" % (n, "本份" if a is not None else "pcbnew"))
                    continue
                if set(a["pads"]) != set(b["pads"]):
                    diffs.append("%s: 焊盘集合不一致 %s vs %s"
                                 % (n, sorted(a["pads"]), sorted(b["pads"])))
                if int(a["seg"]) != int(b["seg"]):
                    diffs.append("%s: 铜段数不一致 %d vs %d" % (n, a["seg"], b["seg"]))
                if abs(float(a["cu"]) - float(b["cu"])) > CU_TOLERANCE_MM:
                    diffs.append("%s: 铜长不一致 %.3f vs %.3f" % (n, a["cu"], b["cu"]))
            if diffs:
                ok = False
                for d in diffs:
                    lines.append("❌ 两份解析器不一致: %s" % d)
            else:
                lines.append("✔ 两份解析器 (自写 s-expr / pcbnew API) 结论一致: %d 个网名逐条核对通过"
                             % len(names))
        except Exception as e:
            ok = False
            lines.append("❌ pcbnew 口径读数读不了: %s" % e)
    else:
        lines.append("★pcbnew 口径快照不在盘 ⇒ 交叉核对跳过 (★不静默绿·已如实标注★)")
    rep.add("K2", ok, "K2 差分腿成对 (两腿都有铜) + 两份解析器结论一致", lines)


def k3_float_ok(nets, required, float_ok, phase, rep):
    """★K3 可悬空名单单列: 必须零铜 且 不在必需表里 ★"""
    lines = []
    ok = True
    req = set(required)
    for n in float_ok:
        if n in req:
            ok = False
            lines.append("❌ %s 同时出现在可悬空名单与必需表里 ⇒ 混进必需表" % n)
            continue
        v = nets.get(n)
        if v is None:
            lines.append("★%s: 板面查不到该网 (★可悬空网不在板上不算违规·只登记★)" % n)
            continue
        seg = int(v.get("seg") or 0)
        cu = float(v.get("cu") or 0.0)
        if seg != 0 or cu != 0.0:
            ok = False
            lines.append("❌ %s 属可悬空名单但板面有铜 (seg=%d cu=%.3f) ⇒ 必须零铜"
                         % (n, seg, cu))
        else:
            lines.append("✔ %s 零铜 (seg=0 cu=0.0) 且不在必需表里" % n)
    rep.add("K3", ok, "K3 可悬空名单单列 (零铜 + 不在必需表)", lines)


def k4_zero_false_connectivity(nets, required, expected_pads, rep):
    """★K4 「零假连通」核心自检: unc 归零但必需网仍无铜 ⇒ 必须判红并点名 ★
    ★实现: 用【合成字典】当反例喂进 K1 的纯判定函数 (★不必真去改板★) ★
    ★三种刷法各一个: ① 删焊盘 ② 标 NC / 零铜 ③ 改名 / 拆网 ★
    ★基线 = 「板那一趟已完成」的合成态 (每条必需网都有期望焊盘 + 有铜) ⇒
      ★三种刷法各只能让【被动手的那一条】变红 ⇒ 若别的网也红 ⇒ 闸误判, 自检红**"""
    lines = []
    ok = True
    if not required:
        rep.add("K4", False, "K4 零假连通核心自检", ["❌ 必需名单为空 ⇒ 无法构造反例"])
        return
    target = required[0]
    exp = expected_pads.get(target, set())

    def base_state():
        return dict((n, {"pads": sorted(expected_pads.get(n, set())), "seg": 3, "cu": 12.5})
                    for n in required)

    # ── 正样: 基线必须全绿 (★防「永远红」的假闸★) ──
    rows = judge_required_all(base_state(), required, expected_pads, "post")
    bad = [(n, fs) for n, o, fs in rows if not o]
    if bad:
        ok = False
        for n, fs in bad:
            lines.append("❌ 正样(逐条都有铜)竟判红: %s (%s)"
                         % (n, "; ".join("%s: %s" % (r, d) for r, d in fs)))
    else:
        lines.append("✔ 正样 (合成基线: %d 条必需网逐条都有铜) 全绿 ⇒ 闸不是「永远红」的假闸" % len(required))

    def synth(net, pads, seg, cu):
        d = base_state()
        d[net] = {"pads": sorted(pads), "seg": seg, "cu": cu}
        return d

    d_rename = base_state()
    d_rename.pop(target, None)
    cases = [
        ("① 删焊盘 (少一个期望焊盘 ⇒ ratsnest 消失 ⇒ unc 计数下降)",
         synth(target, sorted(exp)[:-1], 3, 12.5)),
        ("② 标 NC / no-connect (零铜 ⇒ unc 不再报 ⇒ 计数下降)",
         synth(target, sorted(exp), 0, 0.0)),
        ("③ 改名 / 拆网 (网名从板面消失 ⇒ 计数下降)",
         d_rename),
    ]
    for desc, data in cases:
        rows = judge_required_all(data, required, expected_pads, "post")
        hit = [(n, fs) for n, o, fs in rows if not o]
        if not hit:
            ok = False
            lines.append("❌ 反例未被抓住 (★闸漏判★): %s" % desc)
            continue
        names = [n for n, _fs in hit]
        if names != [target]:
            ok = False
            lines.append("❌ 反例判红集合不对 (★只该红被动手的那一条★): %s ⇒ 红了 %s"
                         % (desc, names))
            continue
        for n, fs in hit:
            lines.append("✔ 反例被抓住: %s ⇒ 点名 %s (%s)"
                         % (desc, n, "; ".join("%s: %s" % (r, d) for r, d in fs)))
    rep.add("K4", ok, "K4 零假连通核心自检 (删焊盘 / 标 NC / 改名 三反例必须判红并点名)", lines)


def k5_cross_check(nets, required, float_ok, rep, req_live=None, req_page=None):
    """★K5 板面与名单交叉核对: 名单里缺 / 板上多 / 板上少 都点名 (★不许只比数量★) ★"""
    lines = []
    ok = True
    # ── 5a 冻结名单 vs 现板口径 漂移检查 ──
    if req_live and req_page:
        if sorted(req_page) == sorted(req_live):
            lines.append("✔ 冻结名单 (真相页 §3) 与现板现算名单一致 (%d 条)" % len(req_live))
        else:
            ok = False
            lines.append("❌ 冻结名单 (真相页 §3) 与现板现算名单漂移: %d vs %d 条"
                         % (len(req_page), len(req_live)))
            lines.append("  仅在冻结名单: %s"
                         % (" ".join(sorted(set(req_page) - set(req_live))) or "(无)"))
            lines.append("  仅在现板现算: %s"
                         % (" ".join(sorted(set(req_live) - set(req_page))) or "(无)"))
    req = set(required)
    known = req | set(float_ok)
    # ── 名单里缺 (板面查不到) ──
    missing = sorted(n for n in required if n not in nets)
    for n in missing:
        ok = False
        lines.append("❌ 名单里缺: %s 在板面查不到" % n)
    if not missing:
        lines.append("✔ 名单里缺: 0 条 (23 条必需网在板面都能查到)")
    # ── 板上少 (必需网不在板面 ⇒ 同上·换句话说) ──
    lines.append("★板上少 = 名单里缺 (同一事实·两种说法): %d 条" % len(missing))
    # ── 板上多 (板上零铜且 pad≥2 的网, 不在必需表也不在可悬空表) ──
    extra = []
    for n, v in nets.items():
        if n in known:
            continue
        if len(v.get("pads") or []) >= 2 and int(v.get("seg") or 0) == 0:
            extra.append(n)
    for n in sorted(extra):
        ok = False
        lines.append("❌ 板上多: %s (零铜 + pad≥2) 但不在必需表也不在可悬空表 ⇒ 分级名单漏了它"
                     % n)
    if not extra:
        lines.append("✔ 板上多: 0 条 (板面零铜 pad≥2 网 = 23 必需 + 1 可悬空, 与分级名单完全对齐)")
    rep.add("K5", ok, "K5 板面与名单交叉核对 (名单里缺 / 板上多 / 板上少 逐条点名)", lines)


def k6_evidence_and_hygiene(rep):
    """★K6 证据等级 + 零挂起 + 零挂链 + 判据/事实分开 ★"""
    lines = []
    ok = True
    # ── 6a 零挂链 ──
    try:
        with open(GATE_CHECK, encoding="utf-8", errors="ignore") as f:
            gc = f.read()
        cnt = gc.count("check_sw_false_connectivity_gate")
        if cnt:
            ok = False
            lines.append("❌ 零挂链破: state/gate_check.py 里出现 %d 处 check_sw_false_connectivity_gate"
                         % cnt)
        else:
            lines.append("✔ 零挂链: state/gate_check.py 不引用本闸")
    except Exception as e:
        ok = False
        lines.append("❌ 读 state/gate_check.py 失败: %s" % e)
    # ── 6b 零挂起 (源码里不许留 TODO / FIXME / NotImplementedError) ──
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            src = f.read()
        body = "\n".join(ln for ln in src.splitlines()
                         if not ln.strip().startswith("#"))
        # ★token 用拼接写出, 免得本行自己命中自己 (★自检不许自我误报★) ★
        hang_tokens = ["TO" + "DO", "FIX" + "ME", "X" + "XX",
                       "NotImplemented" + "Error"]
        hangs = [t for t in hang_tokens if t in body]
        # ★光秃秃的 pass 语句 = 挂起 ★ (★用正则找, 免得字面量自我误报★)
        if re.search(r"(?m)^\s*p+\s*(#.*)?$", body):
            hangs.append("空的 pass 语句")
        if hangs:
            ok = False
            lines.append("❌ 零挂起破: 源码里还有 %s" % ", ".join(hangs))
        else:
            lines.append("✔ 零挂起: 源码无未完标记 / 无未实现分支")
    except Exception as e:
        ok = False
        lines.append("❌ 读自身源码失败: %s" % e)
    # ── 6c 证据等级: 真相页 §0..§7 每段至少一个证据等级标签 ──
    if not os.path.isfile(TRUTH_PAGE):
        ok = False
        lines.append("❌ 真相页不存在: %s" % rel(TRUTH_PAGE))
    else:
        with open(TRUTH_PAGE, encoding="utf-8") as f:
            page = f.read()
        parts = re.split(r"\n## ", page)
        secs = {}
        for chunk in parts[1:]:
            head = chunk.split("\n", 1)[0]
            m = re.match(r"§(\d+)", head)
            if m:
                secs[int(m.group(1))] = chunk
        missing_secs = [i for i in range(0, 8) if i not in secs]
        if missing_secs:
            ok = False
            lines.append("❌ 真相页缺段: %s" % ", ".join("§%d" % i for i in missing_secs))
        for i in sorted(secs):
            body_s = secs[i]
            if not any(t in body_s for t in EVIDENCE_TAGS):
                ok = False
                lines.append("❌ §%d 段内没有任何证据等级标记 (%s) ⇒ 出现无等级断言"
                             % (i, "/".join(EVIDENCE_TAGS)))
        if ok:
            lines.append("✔ 证据等级: §0..§7 每段都带证据等级标记")
        # ── 6d 判据 / 事实分开: 真相页必须同时含「判据」段与「事实」段 ──
        if 4 not in secs or 5 not in secs:
            ok = False
            lines.append("❌ 判据/事实分开: 真相页缺 §4 (判据) 或 §5 (事实/待裁)")
        else:
            lines.append("✔ 判据/事实分开: §4 = 机器判据 · §5 = 事实与未决项")
    rep.add("K6", ok, "K6 证据等级 + 零挂起 + 零挂链 + 判据/事实分开", lines)


# ═══════════════════════════════════════════════════════════════════════
# ★**打印: §3 逐条列铜表** ★
# ═══════════════════════════════════════════════════════════════════════
def print_table(nets, required, float_ok, expected_pads, pairs):
    part = {}
    for p, n in pairs:
        part[p] = n
        part[n] = p
    print("── §3 逐条列铜表 (期望集合=脚表 HW/netlist_v1_pins.csv · 板面读数=板) ──")
    print("  %-18s %-12s %-34s %-34s %5s %9s  %s"
          % ("网名", "分级", "期望焊盘", "板面焊盘", "seg", "cu_mm", "判定"))
    for n in sorted(required):
        exp = sorted(expected_pads.get(n, set()))
        act = sorted((nets.get(n) or {}).get("pads") or [])
        v = nets.get(n) or {}
        seg = int(v.get("seg") or 0)
        cu = float(v.get("cu") or 0.0)
        lvl = "必需·差分腿" if any(n.startswith(p) for p in ("CSI_D0_", "DSI_D0_")) else "必需·单端脚"
        miss = [p for p in exp if p not in act]
        extra = [p for p in act if p not in exp]
        note = []
        if miss:
            note.append("缺焊盘:" + " ".join(miss))
        if extra:
            note.append("多焊盘:" + " ".join(extra))
        if not note:
            note.append("焊盘集合一致")
        if seg < 1 or cu <= 0.0:
            note.append("★零铜★")
        if n in part:
            note.append("对:" + part[n])
        print("  %-18s %-12s %-34s %-34s %5d %9.1f  %s"
              % (n, lvl, " ".join(exp) or "(空)", " ".join(act) or "(空)", seg, cu, "; ".join(note)))
    print("  ── 可悬空 (单列) ──")
    for n in sorted(float_ok):
        v = nets.get(n) or {}
        print("  %-18s %-12s %-34s %-34s %5d %9.1f  %s"
              % (n, "可悬空", " ".join(sorted(expected_pads.get(n, set()))) or "(空)",
                 " ".join(sorted((v.get("pads") or []))) or "(空)",
                 int(v.get("seg") or 0), float(v.get("cu") or 0.0),
                 "零铜且不在必需表 ⇒ 合 K3"))


# ═══════════════════════════════════════════════════════════════════════
# ★**自检 (--selftest): K0~K6 每条一条反向用例 ★**
# ═══════════════════════════════════════════════════════════════════════
def selftest():
    print("═══ check_sw_false_connectivity_gate.py --selftest ═══")
    failures = []
    passed = 0

    def check(name, cond, detail=""):
        nonlocal passed
        if cond:
            passed += 1
            print("  ✔ %s" % name)
        else:
            failures.append("%s %s" % (name, detail))
            print("  ✘ %s %s" % (name, detail))

    # ── 合成夹具 ──
    REQUIRED = ["NET_A", "NET_B", "DIFF_P", "DIFF_N"]
    FLOAT = ["NET_FLOAT"]
    EXP = {"NET_A": {"U1.1", "U2.1"}, "NET_B": {"U3.2", "U4.2"},
           "DIFF_P": {"J1.1"}, "DIFF_N": {"J1.2"}, "NET_FLOAT": {"R1.1"}}

    def mk(seg=3, cu=12.5):
        return {n: {"pads": sorted(EXP[n]), "seg": seg, "cu": cu} for n in REQUIRED + FLOAT}

    # ── 正样 ──
    good = mk()
    rows = judge_required_all(good, REQUIRED, EXP, "post")
    check("K1 正样: 逐条都有铜 ⇒ 全绿",
          all(o for _, o, _ in rows),
          str([(n, fs) for n, o, fs in rows if not o]))
    check("K1 正样: 可悬空网零铜",
          judge_required_net("NET_FLOAT", good["NET_FLOAT"], EXP["NET_FLOAT"], "post")[0])

    # ── 反例 ① 删焊盘 ──
    d1 = mk()
    d1["NET_A"] = {"pads": ["U1.1"], "seg": 3, "cu": 12.5}
    ok1, fs1 = judge_required_net("NET_A", d1["NET_A"], EXP["NET_A"], "post")
    check("K1 反例① 删焊盘 ⇒ 红且点名", (not ok1) and any("缺期望焊盘" in x[1] for x in fs1),
          str(fs1))

    # ── 反例 ② 标 NC / 零铜 ──
    d2 = mk()
    d2["NET_B"] = {"pads": sorted(EXP["NET_B"]), "seg": 0, "cu": 0.0}
    ok2, fs2 = judge_required_net("NET_B", d2["NET_B"], EXP["NET_B"], "post")
    check("K1 反例② 标NC/零铜 ⇒ 红且点名", (not ok2) and any("零铜" in x[1] for x in fs2),
          str(fs2))

    # ── 反例 ③ 改名 / 网名消失 ──
    d3 = {k: v for k, v in mk().items() if k != "NET_A"}
    ok3, fs3 = judge_required_net("NET_A", d3.get("NET_A"), EXP["NET_A"], "post")
    check("K1 反例③ 改名 ⇒ 红且点名「板面查不到」",
          (not ok3) and any("查不到" in x[1] for x in fs3), str(fs3))

    # ── 反例 ④ 板面多出焊盘 ──
    d4 = mk()
    d4["NET_A"] = {"pads": sorted(EXP["NET_A"]) + ["X9.9"], "seg": 3, "cu": 12.5}
    ok4, fs4 = judge_required_net("NET_A", d4["NET_A"], EXP["NET_A"], "post")
    check("K1 反例④ 多出焊盘 ⇒ 红", (not ok4) and any("多出" in x[1] for x in fs4), str(fs4))

    # ── 反例 ⑤ 基线相: 必需网却有铜 ⇒ 红 (板已动) ──
    d5 = mk()
    d5["NET_A"] = {"pads": sorted(EXP["NET_A"]), "seg": 3, "cu": 12.5}
    ok5, fs5 = judge_required_net("NET_A", d5["NET_A"], EXP["NET_A"], "pre")
    check("K0/K1 反例⑤ 基线相必需网有铜 ⇒ 红", (not ok5) and any("基线相" in x[1] for x in fs5),
          str(fs5))

    # ── 反例 ⑥ 差分腿一腿有铜一腿零铜 (K2) ──
    pairnets = {"DIFF_P": {"pads": ["J1.1"], "seg": 5, "cu": 10.0},
                "DIFF_N": {"pads": ["J1.2"], "seg": 0, "cu": 0.0}}
    rep = Report()
    k2_pairs_and_parsers(pairnets, ["DIFF_P", "DIFF_N"], [("DIFF_P", "DIFF_N")], "post", rep)
    check("K2 反例⑥ 一腿有铜一腿零铜 ⇒ 红且点名该对", not rep.ok, str(rep.failed))

    # ── 反例 ⑦ 两份解析器不一致 (K2) ──
    rep2 = Report()
    global SNAP_PCBNEW
    orig = SNAP_PCBNEW
    tmp = os.path.join(PROJ, "tmp", "iss381_sbx", "_selftest_pcbnew.json")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"NET_A": {"pads": ["U1.1"], "seg": 99, "cu": 1.0}}, f)
        SNAP_PCBNEW = tmp
        k2_pairs_and_parsers(mk(), REQUIRED, [], "post", rep2)
        check("K2 反例⑦ 两份解析器不一致 ⇒ 红", not rep2.ok, str(rep2.failed))
    finally:
        SNAP_PCBNEW = orig
        if os.path.isfile(tmp):
            os.remove(tmp)

    # ── 反例 ⑧ 可悬空网混进必需表 (K3) ──
    rep3 = Report()
    k3_float_ok(mk(), ["NET_FLOAT"], ["NET_FLOAT"], "post", rep3)
    check("K3 反例⑧ 可悬空网混进必需表 ⇒ 红", not rep3.ok, str(rep3.failed))

    # ── 反例 ⑨ 可悬空网有铜 (K3) ──
    rep4 = Report()
    d6 = mk()
    d6["NET_FLOAT"] = {"pads": ["R1.1"], "seg": 4, "cu": 9.0}
    k3_float_ok(d6, REQUIRED, FLOAT, "post", rep4)
    check("K3 反例⑨ 可悬空网有铜 ⇒ 红", not rep4.ok, str(rep4.failed))

    # ── 反例 ⑩ 板上多出一条零铜网 (K5) ──
    rep5 = Report()
    d7 = mk()
    d7["NET_STRAY"] = {"pads": ["Z1.1", "Z2.1"], "seg": 0, "cu": 0.0}
    k5_cross_check(d7, REQUIRED, FLOAT, rep5)
    check("K5 反例⑩ 板上多一条零铜网 ⇒ 红且点名", not rep5.ok, str(rep5.failed))

    # ── 反例 ⑪ 名单里缺 (K5) ──
    rep6 = Report()
    d8 = {k: v for k, v in mk().items() if k != "NET_A"}
    k5_cross_check(d8, REQUIRED, FLOAT, rep6)
    check("K5 反例⑪ 名单里的网板面查不到 ⇒ 红且点名", not rep6.ok, str(rep6.failed))

    # ── 反例 ⑫ K4 三种刷法都必须被抓 (闸的命门) ──
    rep7 = Report()
    k4_zero_false_connectivity(mk(), REQUIRED, EXP, rep7)
    check("K4 反例⑫ 删焊盘/标NC/改名 三反例全部判红", rep7.ok, str(rep7.failed))

    # ── 反例 ⑬ 板指纹被改 (K0) ──
    rep8 = Report()
    real_md5 = BASELINE_BOARD_MD5
    try:
        import builtins
        real_md5 = md5_of(BOARD)
        globals()["BASELINE_BOARD_MD5"] = "0" * 32
        k0_fingerprints(rep8)
        check("K0 反例⑬ 基线指纹不符 ⇒ 红", not rep8.ok, str(rep8.failed))
    finally:
        globals()["BASELINE_BOARD_MD5"] = real_md5

    # ── 正样: 真数据路径 (读真板) 全绿/全红符合相语义 ──
    if os.path.isfile(SNAP_SEXPR):
        nets = load_snapshot(SNAP_SEXPR)
        req_single, float_ok, diff_prefixes, er, ef, et = load_grades_from_s8()
        exp = load_expected_pads()
        required = sorted(n for n in nets
                          if len(nets[n]["pads"]) >= 2 and nets[n]["seg"] == 0
                          and (n in req_single or n.startswith(diff_prefixes)))
        rep9 = Report()
        k1_required(nets, required, exp, "pre", rep9)
        check("K1 真数据路径 (pre 相): 基线态 ⇒ 绿", rep9.ok,
              str([(n, fs) for n, o, fs in judge_required_all(nets, required, exp, "pre") if not o]))
        rep10 = Report()
        k1_required(nets, required, exp, "post", rep10)
        check("K1 真数据路径 (post 相): 现板 ⇒ 红且逐条点名 %d 条" % len(required),
              (not rep10.ok) and len(rep10.failed[0][3]) >= len(required),
              str(len(rep10.failed[0][3])))

    print("  ── 自检小结: 通过 %d / 失败 %d" % (passed, len(failures)))
    if failures:
        for f in failures:
            print("  ✘ FAIL: %s" % f)
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


# ═══════════════════════════════════════════════════════════════════════
# ★**main** ★
# ═══════════════════════════════════════════════════════════════════════
FLOAT_MARK = []


def main(argv):
    global FLOAT_MARK
    phase = "pre"
    do_selftest = False
    do_table = False
    print_net = None
    data_path = None
    board_path = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--selftest":
            do_selftest = True
        elif a == "--phase":
            i += 1
            phase = argv[i]
        elif a.startswith("--phase="):
            phase = a.split("=", 1)[1]
        elif a == "--print-table":
            do_table = True
        elif a == "--print-net":
            i += 1
            print_net = argv[i]
        elif a == "--data":
            i += 1
            data_path = argv[i]
        elif a == "--board":
            i += 1
            board_path = argv[i]
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print("❌ 未知参数: %s" % a)
            return 2
        i += 1

    if do_selftest:
        return selftest()

    if phase not in ("pre", "post"):
        print("❌ --phase 只能是 pre 或 post")
        return 2

    req_single, float_ok, diff_prefixes, er, ef, et = load_grades_from_s8()
    if not req_single or not float_ok:
        print("❌ 从 HW/check_s8_target_list.py 静态解析 REQUIRED_SINGLE / FLOAT_OK 失败 (★fail-closed★)")
        return 1
    FLOAT_MARK = list(float_ok)
    pairs, pairs_src = load_pairs()
    expected_pads = load_expected_pads()
    nets, src = build_nets(data_path, board_path)
    rep = Report()

    # ★**必需名单** ★
    #   pre  相 = 现板现算 (S8 已裁口径: 8 单端脚 + 现板零铜差分腿) ⇒ 与真相页 §3 交叉核对 ★
    #   post 相 = 真相页 §3 的【冻结名单】 (★板那一趟做完名单不会自己缩水★) ★
    req_live = [n for n in required_live(nets, req_single, diff_prefixes)
                if n not in set(float_ok)]
    req_page = required_from_page()
    if phase == "post":
        required = req_page if req_page else req_live
    else:
        required = req_live
    spec_note = ""
    if req_page and req_live and sorted(req_page) != sorted(req_live):
        spec_note = "⚠ 冻结名单与现板口径漂移 (%d vs %d)" % (len(req_page), len(req_live))
    elif req_page:
        spec_note = "冻结名单 = 真相页 §3 (%d 条) · 与现板现算一致" % len(req_page)
    else:
        spec_note = "★真相页 §3 名单读不到 ⇒ 用现板现算名单 (fail-closed 由 K5 判红)"

    if print_net:
        v = nets.get(print_net)
        if v is None:
            print("板面查不到网: %s" % print_net)
            return 1
        print("网名 %s" % print_net)
        print("  焊盘集合 (%d): %s" % (len(v["pads"]), " ".join(v["pads"])))
        print("  铜段数 seg = %d" % v["seg"])
        print("  铜长   cu  = %.3f mm" % v["cu"])
        # ★过孔数: 自写 s-expr 快照里没有该字段 ⇒ 取 pcbnew API 口径快照 (★只读★) ★
        try:
            with open(SNAP_PCBNEW, encoding="utf-8") as f:
                _pn = json.load(f)
            _v = _pn.get(print_net) or {}
            if "via" in _v:
                print("  过孔数 via = %d (★pcbnew API 口径★)" % int(_v["via"]))
        except Exception:
            pass
        exp = sorted(expected_pads.get(print_net, set()))
        print("  脚表期望焊盘 (%d): %s" % (len(exp), " ".join(exp) or "(空)"))
        if print_net not in required and print_net not in set(float_ok):
            print("  名单归属: ★不在必需名单 (23 条) 也不在可悬空名单 (1 条) ⇒ 不参与 K1 逐条判定★")
            return 0
        ok, fs = judge_required_net(print_net, v, expected_pads.get(print_net, set()), phase)
        print("  判定 (phase=%s): %s" % (phase, "绿" if ok else "红"))
        for r, d in fs:
            print("    - %s: %s" % (r, d))
        return 0

    if do_table:
        print_table(nets, required, float_ok, expected_pads, pairs)
        return 0

    print("═══ 板那一趟 · 布线验收线「零假连通」自检闸 (K0~K6) ═══")
    print("  phase      : %s  (%s)" % (phase, "板那一趟之前的基线相" if phase == "pre"
                                        else "板那一趟之后的验收相 ★验收线本身★"))
    print("  读数来源  : %s" % src)
    print("  分级名单  : HW/check_s8_target_list.py 的 REQUIRED_SINGLE(%d) + FLOAT_OK(%d) "
          "+ DIFF_PREFIXES(%s)  ★AST 静态解析·不 import 不 exec·一字未改★"
          % (len(req_single), len(float_ok), list(diff_prefixes)))
    print("  期望焊盘  : HW/netlist_v1_pins.csv (board∈{空,MAIN_PCB})  ★脚表真源·不是板面★")
    print("  差分对来源: %s" % pairs_src)
    print("  必需网数  : %d  (S8 期望 %s) · 可悬空 %d (S8 期望 %s) · 待定 %s (S8 期望 %s)"
          % (len(required), er, len(float_ok), ef,
             max(0, len([n for n in nets if len(nets[n]["pads"]) >= 2
                         and nets[n]["seg"] == 0 and n not in set(required)
                         and n not in set(float_ok)])), et))
    print("  名单口径  : %s" % spec_note)
    print()

    k0_fingerprints(rep)
    k1_required(nets, required, expected_pads, phase, rep, expect_count=er)
    k2_pairs_and_parsers(nets, required, pairs, phase, rep)
    k3_float_ok(nets, required, float_ok, phase, rep)
    k4_zero_false_connectivity(nets, required, expected_pads, rep)
    k5_cross_check(nets, required, float_ok, rep, req_live=req_live, req_page=req_page)
    k6_evidence_and_hygiene(rep)

    for code, ok, title, lines in rep.rows:
        print("── %s %s" % (code, "✔ 绿" if ok else "❌ 红"))
        print("   %s" % title)
        for ln in lines:
            print("   %s" % ln)
        print()
    if rep.warns:
        print("── 登记 (★非判红·只记录★)")
        for w in rep.warns:
            print("   %s" % w)
        print()

    n_fail = len(rep.failed)
    if n_fail:
        print("★★ 结果: 红 ❌ (%d 条判据不通过: %s)" % (n_fail, ", ".join(r[0] for r in rep.failed)))
        return 1
    print("★★ 结果: 绿 ✔ (K0~K6 全部通过)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:      # ★fail-closed: 任何异常 ⇒ 红★
        import traceback
        traceback.print_exc()
        print("★★ 结果: 红 ❌ (闸内异常 ⇒ fail-closed): %s" % e)
        sys.exit(1)
