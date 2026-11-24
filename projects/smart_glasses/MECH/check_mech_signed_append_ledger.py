#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-399 · mech-lead · MECH 域【已签收件追加登记台账】自守闸

★性质★: 纯读判据闸 · 零写板 · 零落表 · 零改既有闸 · 零挂链 · 零外发
★它是 SW 侧 `SW/tools/check_sw_board_md5_rebase_readiness.py` (ISS-372) 的 MECH 对偶★

★判据 M1~M8★:
  M1 枚举 + 在册   : 代码级 AST 枚举 MECH 域「把别的文件的 md5 写死成常量」的 pin
                     ⇒ 每处必须在本单真相页 §1 机器块里【在册】⇒ 新闸从缝里溜过去 ⇒ 判红
  M2 陈旧检测      : 每处 pin 的「写死基线」≠ 盘上现值 ⇒ 判红 (★红的是现状不是闸故障★)
  M3 归因可查      : 每处陈旧 pin 必须在台账里查到一行 (单号+文件+prev_md5+md5) ⇒ 否则判红
                     (★查不到 = 【来源不明的漂移】★)
  M4 不许悄悄换基线: pin 的写死常量若与 §1 机器块登记的基线不同 ⇒ 基线被换过
                     ⇒ 必须有台账行 (prev = 登记基线, md5 = 新常量) ⇒ 否则判红
                     (★本闸最核心的护栏★)
  M5 板三证        : 板 md5 / mtime / size 三项 == 基线
  M6 证据分级      : 五级白名单 + 零挂起措辞
  M7 零挂链        : 本闸在 state/gate_check.py 里的挂链数必须 == 0
  M8 自证          : --selftest ≥8 条反向用例 (含一条专打 M4)

★预期读数★: 裸跑 rc=1 (现状红 · 3 处陈旧 pin 归因不到) · --selftest rc=0 · 末行 ALL TESTS PASS
"""
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)

# ------------------------------------------------------------------ 落表常量
TRUTH_REL = "MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md"
# ★★待 main 拍 (M-A): 台账放哪 / 叫什么 / 谁写 ★★ 本单按【建议默认值】实现
#   (★建议: 新建 MECH 域自己的台账·理由见真相页 §3·★不替 main 拍★)
#   ⇒ 路径是本闸的一个常量 ⇒ main 拍了别的路径 ⇒ 改这一行即可 (★不改判据★)
LEDGER_REL = "MECH/SIGNED_APPEND_LEDGER.md"

INV_BEGIN = "<!-- MECH-SIGNED-APPEND-LEDGER-INVENTORY-BEGIN -->"
INV_END = "<!-- MECH-SIGNED-APPEND-LEDGER-INVENTORY-END -->"
REC_BEGIN = "<!-- MECH-SIGNED-APPEND-LEDGER-RECORDS-BEGIN -->"
REC_END = "<!-- MECH-SIGNED-APPEND-LEDGER-RECORDS-END -->"

BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

BOARD_FAMILY = ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro")
# ★落表台账 (★板侧·ISS-296/303 已用它做【合法改板通道】)★
LANDING_LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
GATE_CHAIN_REL = "state/gate_check.py"

MD5RE = re.compile(r"^[0-9a-f]{32}$")
# ★落表台账管理的文件 = 板侧三件 + 板族 (★通道存在 ⇒ 不在本台账口径内★)
LEDGER_MANAGED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概值]", "[大概]")
FORBIDDEN_PENDING = ("等原厂回信", "等原厂回复", "等待原厂", "等原厂", "待外部确认",
                      "等外部回复", "等待外部回复", "回头再问原厂", "等原厂回覆",
                      "待原厂回信", "等放行", "待确认")

# ★★台账记录表头 (★机器可解析·★人工也读得懂★)★★
REC_HEADER = ("单号", "文件", "prev_md5", "md5", "追加类型", "追加位置", "自证")
APPEND_KINDS = ("纯字节追加", "局部订正")


# ====================================================================== 工具
def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def md5_of(path):
    h = hashlib.md5()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def norm_rel(s):
    return str(s or "").replace("\\", "/").strip()


# ====================================================================== M1 枚举
def const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join":
        parts = []
        for a in node.args:
            s = const_str(a)
            if s is None:
                return None
            parts.append(s)
        return os.path.join(*parts) if parts else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        l = const_str(node.left)
        r = const_str(node.right)
        if l is not None and r is not None:
            return l + r
    return None


def resolve_rel(cand, gate_dir, root):
    if not cand:
        return None
    c = norm_rel(cand)
    if c.startswith("/"):
        return None
    cands = []
    if "/" in c:
        cands.append(c)
    else:
        cands.append(os.path.join(gate_dir, c))
        cands.append(os.path.join("MECH", c))
        cands.append(os.path.join("HW", "PCB", c))
        cands.append(os.path.join("HW", c))
    for x in cands:
        x = norm_rel(os.path.normpath(x))
        if os.path.isfile(os.path.join(root, x)):
            return x
    return None


class _PinVisitor(ast.NodeVisitor):
    def __init__(self, gate_rel, root):
        self.gate_rel = gate_rel
        self.gate_dir = os.path.dirname(gate_rel)
        self.root = root
        self.pins = []
        self.scope = []
        self.dictname = []
        self.consts = {}

    def collect_consts(self, tree):
        for node in tree.body:
            tgt = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                tgt = node.targets[0].id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                tgt = node.target.id
            if tgt:
                s = const_str(node.value) if getattr(node, "value", None) is not None else None
                if s is not None:
                    self.consts[tgt] = s

    def _resolve_key(self, keynode):
        if isinstance(keynode, ast.Constant) and isinstance(keynode.value, str):
            return keynode.value
        if isinstance(keynode, ast.Name):
            return self.consts.get(keynode.id)
        if isinstance(keynode, ast.Call):
            return const_str(keynode)
        return None

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        dname = None
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            dname = node.targets[0].id
        self.dictname.append(dname)
        self.generic_visit(node)
        self.dictname.pop()

    def visit_Dict(self, node):
        infunc = bool(self.scope)
        for k, v in zip(node.keys, node.values):
            if k is None:
                continue
            vs = const_str(v)
            if not vs or not MD5RE.match(vs):
                continue
            cand = self._resolve_key(k)
            rel = resolve_rel(cand, self.gate_dir, self.root)
            if rel is None:
                continue
            self.pins.append({
                "gate": self.gate_rel,
                "target": rel,
                "baseline": vs,
                "line": getattr(v, "lineno", 0),
                "dict_name": self.dictname[-1] if self.dictname else "",
                "in_func": infunc,
            })
        self.generic_visit(node)


def _gate_files(root):
    out = []
    for d in ("MECH", "MECH/tools"):
        pdir = os.path.join(root, d)
        if not os.path.isdir(pdir):
            continue
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".py") or ".bak" in fn:
                continue
            rel = norm_rel(os.path.join(d, fn))
            if rel == norm_rel(os.path.join("MECH", "check_mech_signed_append_ledger.py")):
                continue                       # ★本闸自己 ⇒ 不参与判定 (★防自噬★)
            out.append(rel)
    return out


def has_ledger_channel(gate_rel, root):
    """★代码级形态检测: 这个闸有没有【台账/合法变更通道】的形状 (★照 SW 侧同款口径·不造新判据★)★"""
    txt = read_text(os.path.join(root, gate_rel))
    if not txt:
        return False
    if LANDING_LEDGER_REL.replace("/", os.sep) not in txt and "SCHEMATIC_LANDING_V1_LANDED" not in txt:
        return False
    # ★必须真的读台账出【链头】才算通道 (★光提一句路径不算★)
    for tok in ("ledger_state", "ledger_records", "LEDGER_CANON", "PROTECTED_LEDGER", "ledger_head"):
        if tok in txt:
            return True
    return False


def classify_pin(pin, root):
    """★分类: P1 硬钉(无通道) / P2 板族钉 / P3 台账通道钉 ★"""
    if pin["target"] in BOARD_FAMILY:
        return "P2"
    if pin["target"] in LEDGER_MANAGED and has_ledger_channel(pin["gate"], root):
        return "P3"
    if has_ledger_channel(pin["gate"], root) and pin["target"] in LEDGER_MANAGED:
        return "P3"
    return "P1"


def enumerate_pins(root):
    """★M1 的枚举器: 代码级 AST 解析出 MECH 域每一处「钉别人 md5」★"""
    out = []
    for g in _gate_files(root):
        src = read_text(os.path.join(root, g))
        if not src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        v = _PinVisitor(g, root)
        v.collect_consts(tree)
        v.visit(tree)
        for p in v.pins:
            if p["in_func"]:
                continue                      # ★函数体内 = 自测夹具 ⇒ 不是 pin★)
            p["cls"] = classify_pin(p, root)
            p["actual"] = md5_of(os.path.join(root, p["target"]))
            p["stale"] = (p["actual"] is not None and p["actual"] != p["baseline"])
            out.append(p)
    return out


# ====================================================================== 台账
def load_inventory(root):
    """★读真相页 §1 机器块 (★在册清单)★"""
    txt = read_text(os.path.join(root, TRUTH_REL))
    if not txt:
        return None
    i = txt.find(INV_BEGIN)
    j = txt.find(INV_END)
    if i < 0 or j < 0 or j < i:
        return None
    blob = txt[i + len(INV_BEGIN):j].strip()
    if blob.startswith("```"):
        blob = blob.split("\n", 1)[1] if "\n" in blob else ""
    if blob.endswith("```"):
        blob = blob.rsplit("\n", 1)[0]
    try:
        data = json.loads(blob)
    except Exception:                          # noqa: BLE001
        return None
    if not isinstance(data, dict) or not isinstance(data.get("pins"), list):
        return None
    return data


def load_ledger(root, ledger_rel):
    """★读台账记录表 (★append-only·链式·fail-closed★)"""
    txt = read_text(os.path.join(root, ledger_rel))
    if not txt:
        return {"ok": False, "why": "台账 %s 读不到 (★还没建·★或路径不对·★M-A 待 main 拍★)" % ledger_rel,
                "records": [], "by_file": {}}
    i = txt.find(REC_BEGIN)
    j = txt.find(REC_END)
    if i < 0 or j < 0 or j < i:
        return {"ok": False, "why": "台账 %s 里读不到记录块 (%s..%s) ⇒ fail-closed 判红"
                % (ledger_rel, REC_BEGIN, REC_END), "records": [], "by_file": {}}
    seg = txt[i + len(REC_BEGIN):j]
    rows = []
    header_seen = False
    for ln in seg.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            if tuple(cells[:7]) == REC_HEADER:
                header_seen = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if len(cells) < 7:
            continue
        rows.append({
            "iss": cells[0], "file": norm_rel(cells[1]),
            "prev": cells[2].lower(), "md5": cells[3].lower(),
            "kind": cells[4], "where": cells[5], "proof": cells[6],
        })
    if not header_seen:
        return {"ok": False, "why": "台账 %s 的记录块表头不是 %s ⇒ fail-closed 判红"
                % (ledger_rel, " | ".join(REC_HEADER)), "records": [], "by_file": {}}
    by_file = {}
    for r in rows:
        by_file.setdefault(r["file"], []).append(r)
    return {"ok": True, "why": "", "records": rows, "by_file": by_file}


def ledger_match(led, target, prev, cur):
    """★在台账里找一条能解释 (prev → cur) 的合法记录 (★四项齐全才算★)★"""
    out = []
    for r in led.get("by_file", {}).get(target, []):
        if r["prev"] != prev or r["md5"] != cur:
            continue
        if not r["iss"] or not re.match(r"^ISS-[0-9]+", r["iss"]):
            continue
        if r["kind"] not in APPEND_KINDS:
            continue
        if not r["proof"]:
            continue
        out.append(r)
    return out


def chain_state(led, target):
    """★台账链完整性 (★fail-closed: 链断 / 链头不唯一 / 链头无单号 ⇒ 判红★)"""
    recs = led.get("by_file", {}).get(target, [])
    if not recs:
        return {"ok": False, "why": "台账里没有 %s 的记录" % target}
    for r in recs:
        if not re.match(r"^ISS-[0-9]+", r["iss"]):
            return {"ok": False, "why": "台账 %s 有一行缺单号 (★链头无单号 ⇒ 判红★)" % target}
        if r["kind"] not in APPEND_KINDS:
            return {"ok": False, "why": "台账 %s 有一行的追加类型 %r 不在枚举内" % (target, r["kind"])}
    for a, b in zip(recs, recs[1:]):
        if a["md5"] != b["prev"]:
            return {"ok": False, "why": "台账 %s 的链断了 (★上一行 md5 %s ≠ 下一行 prev_md5 %s★)"
                    % (target, a["md5"][:8], b["prev"][:8])}
    return {"ok": True, "why": "", "head": recs[-1]["md5"], "tail_prev": recs[0]["prev"]}


# ====================================================================== 八条判据
def run_checks(root, ledger_rel):
    res = {}

    def add(cid, ok, title, errs, extra=None):
        res[cid] = {"ok": bool(ok), "id": cid, "title": title,
                    "errors": list(errs), "extra": extra or {}}

    pins = enumerate_pins(root)
    p1 = [p for p in pins if p["cls"] == "P1"]
    p2 = [p for p in pins if p["cls"] == "P2"]
    p3 = [p for p in pins if p["cls"] == "P3"]
    stale = [p for p in p1 if p["stale"]]

    inv = load_inventory(root)
    led = load_ledger(root, ledger_rel)

    # ---------- M1 枚举 + 在册 ----------
    errs = []
    if inv is None:
        errs.append("★真相页 %s 读不到 §1 机器块 (INVENTORY) ⇒ fail-closed 判红★" % TRUTH_REL)
        inv_pins = {}
    else:
        inv_pins = {}
        for e in inv["pins"]:
            inv_pins[(e["gate"], e["target"])] = e
    for p in p1:
        k = (p["gate"], p["target"])
        if k not in inv_pins:
            errs.append("★MECH 域有闸 %s L%d 硬钉了 %s 的 md5 (基线 %s) 但它没进 §1 在册清单 ⇒ "
                        "★下一道新闸再硬钉就是从这儿溜过去的★ ⇒ 判红★"
                        % (p["gate"], p["line"], p["target"], p["baseline"][:8]))
    for k, e in inv_pins.items():
        if not any(p["gate"] == k[0] and p["target"] == k[1] for p in p1):
            errs.append("★§1 清单登记了 %s 钉 %s 但盘上扫不到 ⇒ 清单过期 ⇒ 判红★" % (k[0], k[1]))
    add("M1", not errs, "MECH 域每一处【硬钉别人 md5】的 pin 必须在 §1 在册清单里 (★新闸溜过去 ⇒ 判红★)",
        errs, {"p1": len(p1), "p2": len(p2), "p3": len(p3), "total": len(pins)})

    # ---------- M2 陈旧检测 ----------
    errs = []
    for p in stale:
        errs.append("★陈旧 pin: %s L%d 钉 %s 基线 %s ≠ 盘上现值 %s ⇒ 判红 (★红的是现状不是闸故障★)"
                    % (p["gate"], p["line"], p["target"], p["baseline"][:8], (p["actual"] or "")[:8]))
    add("M2", not errs, "每处硬钉 pin 的写死基线必须 == 盘上现值 (★现状红·★不是闸故障★)",
        errs, {"stale": len(stale)})

    # ---------- M3 归因可查 ----------
    errs = []
    if not led["ok"]:
        errs.append("★台账判决失败: %s ⇒ 全部陈旧 pin 归因不到 ⇒ 判红 (★fail-closed★)" % led["why"])
    for p in stale:
        if not led["ok"]:
            break
        m = ledger_match(led, p["target"], p["baseline"], p["actual"] or "")
        if not m:
            errs.append("★陈旧 pin %s 钉 %s (基线 %s → 现值 %s) 在台账 %s 里查不到一行 "
                        "(单号+文件+prev_md5+md5 四项齐全) ⇒ ★来源不明的漂移★ ⇒ 判红★"
                        % (p["gate"], p["target"], p["baseline"][:8], (p["actual"] or "")[:8], ledger_rel))
            continue
        cs = chain_state(led, p["target"])
        if not cs["ok"]:
            errs.append("★台账 %s 的 %s 链不完整: %s ⇒ 判红 (★fail-closed★)"
                        % (ledger_rel, p["target"], cs["why"]))
            continue
        if cs["head"] != (p["actual"] or ""):
            errs.append("★台账 %s 的 %s 链头 %s ≠ 盘上现值 %s ⇒ 判红 (★真源被换了或台账没更新★)"
                        % (ledger_rel, p["target"], cs["head"][:8], (p["actual"] or "")[:8]))
    add("M3", not errs, "每一处陈旧 pin 必须在台账里查到一行 (★查不到 = 来源不明 = 判红★)",
        errs)

    # ---------- M4 不许悄悄换基线 ----------
    errs = []
    if inv is not None:
        for p in p1:
            e = inv_pins.get((p["gate"], p["target"]))
            if e is None:
                continue
            reg = str(e.get("baseline") or "").lower()
            if reg and reg != p["baseline"]:
                m = ledger_match(led, p["target"], reg, p["baseline"])
                if not m:
                    errs.append("★悄悄换基线: %s L%d 钉 %s 的常量已从登记基线 %s 改成 %s "
                                "★但台账 %s 里没有对应的一行 (prev=%s md5=%s)★ ⇒ 判红★"
                                % (p["gate"], p["line"], p["target"], reg[:8], p["baseline"][:8],
                                   ledger_rel, reg[:8], p["baseline"][:8]))
                else:
                    cs = chain_state(led, p["target"])
                    if not cs["ok"]:
                        errs.append("★悄悄换基线: %s 钉 %s 的常量被换了 (登记基线 %s → 现常量 %s) "
                                    "★台账链不完整: %s★ ⇒ 判红 (★fail-closed★)"
                                    % (p["gate"], p["target"], reg[:8], p["baseline"][:8], cs["why"]))
                    elif cs["tail_prev"] != reg:
                        errs.append("★悄悄换基线: %s 钉 %s 的常量被换了 (登记基线 %s → 现常量 %s) "
                                    "★但台账链尾 prev_md5 = %s ≠ 登记基线 %s★ ⇒ 判红 (★基线被换·台账没跟上★)"
                                    % (p["gate"], p["target"], reg[:8], p["baseline"][:8],
                                       cs["tail_prev"][:8], reg[:8]))
    else:
        errs.append("★§1 在册清单读不到 ⇒ M4 无法判定 ⇒ fail-closed 判红★")
    add("M4", not errs, "★不许靠改常量消红★ (★改常量必须同时在台账留一行·★否则判红★)",
        errs)

    # ---------- M5 板三证 ----------
    errs = []
    pcb = os.path.join(root, BOARD_REL)
    if not os.path.exists(pcb):
        errs.append("★板读不到 (%s) ⇒ fail-closed ⇒ 判红★" % BOARD_REL)
    else:
        got = md5_of(pcb)
        st = os.stat(pcb)
        if got != BOARD_MD5:
            errs.append("★板 md5=%s ≠ 基线 %s ⇒ 判红 (★板被换过⇒零写板自证失败★)" % (got, BOARD_MD5))
        if st.st_size != BOARD_SIZE:
            errs.append("★板 size=%d ≠ 基线 %d ⇒ 判红" % (st.st_size, BOARD_SIZE))
        from datetime import datetime
        # ★★ISS-399 cont2 实现缺陷修正 (★阈值常量一字未改·★比较精度反而更严★)★★
        #   缺陷: 原式用 datetime.fromtimestamp(st.st_mtime) (★只到 6 位微秒★)
        #         去比 9 位纳秒基线 "2026-11-06 07:07:17.362193413"
        #         ⇒ 微秒截断成 "…362193" ⇒ ★永远 != 基线 ⇒ M5 永远红★
        #         ⇒ 且红的时候打印 "板被写过" ⇒ ★对真没被写过的板做假指控★
        #   实测: st_mtime_ns = 1793920037362193413 ⇒ 纳秒位 = 362193413 == 基线 ⇒
        #         ★板从未被写 (md5/size/纳秒 mtime 三项全等于基线·本机实读)★
        #   改法: 直接取 st_mtime_ns 的纳秒位, 按 9 位拼 ⇒ ★与基线同精度同量纲★
        mt = "%s.%09d" % (datetime.fromtimestamp(st.st_mtime_ns // 1000000000)
                          .strftime("%Y-%m-%d %H:%M:%S"), st.st_mtime_ns % 1000000000)
        if mt != BOARD_MTIME:
            errs.append("★板 mtime=%s ≠ 基线 %s ⇒ 判红 (★板被写过★)" % (mt, BOARD_MTIME))
    add("M5", not errs, "板三证 (md5 / mtime / size) == 基线 (★零写板自证★)", errs)

    # ---------- M6 证据分级 + 零挂起措辞 ----------
    errs = []
    for rel in (TRUTH_REL, ledger_rel):
        txt = read_text(os.path.join(root, rel))
        if not txt:
            continue
        for w in FORBIDDEN_EVIDENCE:
            if w in txt:
                errs.append("★%s 里出现不在白名单的证据等级 %s ⇒ 判红 (★白名单=%s★)"
                            % (rel, w, "/".join(EVIDENCE_WHITELIST)))
        for w in FORBIDDEN_PENDING:
            if w in txt:
                errs.append("★%s 里出现零挂起清单里的措辞 %s ⇒ 判红 (★缺口一律自己查+标等级★)" % (rel, w))
    src = read_text(os.path.join(root, "MECH/check_mech_signed_append_ledger.py"))
    if src:
        # ★★ISS-399 cont2 实现缺陷修正 (★词表本身一字未改★)★★
        #   缺陷: 本闸源码里【就有】FORBIDDEN_PENDING 这个词表常量 ⇒ 扫本闸源码全文
        #         必然自命中 ⇒ M6 永远红 ⇒ 且红的原因是【闸自己的词表】⇒ 假红
        #   改法: 扫本闸源码时先把【词表常量定义块】剔掉再扫 ⇒ ★只剔定义·不改词表·
        #         不改判据口径 (★真相页 / 台账两处的扫描一个字没动★)
        src_scan = re.sub(r"FORBIDDEN_PENDING\s*=\s*\([^)]*\)", "", src, flags=re.S)
        for w in FORBIDDEN_PENDING:
            if w in src_scan:
                errs.append("★本闸源码里出现零挂起措辞 %s ⇒ 判红" % w)
    add("M6", not errs, "证据分级五级白名单 + 零挂起措辞", errs)

    # ---------- M7 零挂链 ----------
    errs = []
    gt = read_text(os.path.join(root, GATE_CHAIN_REL))
    if not gt:
        errs.append("★门禁链 %s 读不到 ⇒ fail-closed 判红★" % GATE_CHAIN_REL)
    else:
        n = gt.count("check_mech_signed_append_ledger")
        if n != 0:
            errs.append("★本闸在 %s 里的挂链数 = %d ≠ 0 ⇒ 本单零挂链 (★挂不挂是 main 的地界★) ⇒ 判红★"
                        % (GATE_CHAIN_REL, n))
    add("M7", not errs, "零挂链 (★本闸不在官方门禁链里·★挂不挂是 main 的地界★)", errs)

    return res, pins, inv, led


# ====================================================================== 自测
def _copy_tree(src, dst, rels):
    for r in rels:
        s = os.path.join(src, r)
        if not os.path.exists(s):
            continue
        d = os.path.join(dst, r)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)


def build_sandbox(root, sbx):
    """★沙盒: 只复制本闸判据面要用的文件 (★不建符号链接 ⇒ 写操作不穿透真件★)"""
    shutil.rmtree(sbx, ignore_errors=True)
    os.makedirs(sbx, exist_ok=True)
    rels = []
    for d in ("MECH", "MECH/tools"):
        pdir = os.path.join(root, d)
        if not os.path.isdir(pdir):
            continue
        for fn in sorted(os.listdir(pdir)):
            if fn.endswith(".py") and ".bak" not in fn:
                rels.append(norm_rel(os.path.join(d, fn)))
    rels += [TRUTH_REL, LEDGER_REL, GATE_CHAIN_REL, BOARD_REL, LANDING_LEDGER_REL]
    # ★★ISS-399 cont2 修正 (★不改判据·只把沙盒的【判据面】补齐★)★★
    #   缺陷: 沙盒只复制了 MECH/*.py + 几个固定文件 ⇒ 【被钉的 .md 真相页】不在沙盒里
    #         ⇒ 沙盒里 resolve_rel 找不到那一页 ⇒ 该 pin 根本没被枚举
    #         ⇒ 归因用例 (c03 抹单号 / c04 断链 / c05 改链头 / c10 改类型) 改的
    #           恰好是【页】那一行 ⇒ 沙盒里那条 pin 不存在 ⇒ 用例「应红却绿」
    #         ⇒ ★假通过比假红更坏 (★用例看着过了·其实什么都没测到★)
    #   改法: 把盘上每一处 pin 的【被钉文件本身】也复制进沙盒 (★只读副本·真件零碰★)
    try:
        for _p in enumerate_pins(root):
            _t = _p["target"]
            if _t not in rels and os.path.isfile(os.path.join(root, _t)):
                rels.append(_t)
    except Exception:                          # noqa: BLE001
        pass
    for r in rels:
        s = os.path.join(root, r)
        if os.path.exists(s):
            d = os.path.join(sbx, r)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    return rels


def _mk_ledger(sbx, rel, rows):
    """★在沙盒里造一份台账 (★表头必须一字不差★)"""
    p = os.path.join(sbx, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = ["| " + " | ".join(REC_HEADER) + " |",
            "|" + "|".join(["---"] * len(REC_HEADER)) + "|"]
    for r in rows:
        body.append("| " + " | ".join([r["iss"], r["file"], r["prev"], r["md5"],
                                       r["kind"], r["where"], r["proof"]]) + " |")
    txt = ("# 沙盒台账 (★仅供 --selftest·★非真实台账★)\n\n"
           + REC_BEGIN + "\n" + "\n".join(body) + "\n" + REC_END + "\n")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(txt)


def _judge(sbx):
    """★在沙盒里跑判据 (★只看 M1~M4·★M5/M6/M7 与沙盒无关故略★)"""
    res, pins, inv, led = run_checks(sbx, LEDGER_REL)
    return res


def selftest(root):
    sbx = os.path.join(root, "tmp", "iss399", "sbx_selftest")
    cases = []

    def case(cid, title, want_red, expect_ids=None):
        # ★★ISS-399 cont2 修正 (★不改判据·只改【自测用例的期望写法】★★)
        #   expect_ids 可以是 list (★整组同一期望★) 或 dict (★逐判据给期望: eid→want_red★)
        #   ⇒ 理由: M2 是【现状判据】⇒ 3 处陈旧 pin 在盘 ⇒ M2 必红 (★红的是现状★)
        #   ⇒ 「台账齐全 ⇒ 全绿」的正向对照只对 M3/M4 成立 (★M2 红了才是正常态★)
        cases.append((cid, title, want_red, expect_ids or []))

    # c01 正向对照: 台账齐全 ⇒ M3/M4 全绿 (★M2 仍红: 它是现状判据·3 处陈旧 pin 在盘★)
    case("c01", "正向对照: 3 处陈旧 pin 都在台账留行 ⇒ M3/M4 应绿 (★M2 红 = 现状★)",
         False, {"M3": False, "M4": False, "M2": True})
    # c02 陈旧 pin 无台账 ⇒ M3 红
    case("c02", "把台账清空 ⇒ 陈旧 pin 归因不到 ⇒ M3 应红", True, ["M3"])
    # c03 台账行缺单号 ⇒ M3 红 (链头无单号)
    case("c03", "台账行的单号字段抹掉 ⇒ M3 应红 (★链头无单号★)", True, ["M3"])
    # c04 台账链断 ⇒ M3 红
    case("c04", "台账链断 (第二行 prev_md5 ≠ 第一行 md5) ⇒ M3 应红", True, ["M3"])
    # c05 台账链头 ≠ 盘上现值 ⇒ M3 红
    case("c05", "台账链头改成不是盘上现值 ⇒ M3 应红", True, ["M3"])
    # c06 ★专打 M4: 悄悄改常量无台账行 ⇒ M4 红
    case("c06", "★专打 M4★ 把闸里的基线常量悄悄改成盘上现值 (台账不动) ⇒ M4 应红", True, ["M4"])
    # c07 M4 反向自证: 改常量 + 台账留一行 ⇒ M4 应绿
    case("c07", "★M4 反向自证★ 改常量 + 台账留对应行 ⇒ M4 应绿 (★证明 M4 不是宽放乱抓★)", False, ["M4"])
    # c08 新闸 (不在 §1 在册) 加一处硬钉 ⇒ M1 红
    case("c08", "在沙盒里新造一道闸硬钉一个 md5 (不在 §1 在册) ⇒ M1 应红", True, ["M1"])
    # c09 §1 在册清单过期 ⇒ M1 红
    case("c09", "把 §1 在册清单里删掉一条 ⇒ M1 应红 (★清单过期★)", True, ["M1"])
    # c10 台账追加类型不在枚举 ⇒ M3 红
    case("c10", "台账行的追加类型写成枚举外的词 ⇒ M3 应红", True, ["M3"])
    # c11 真相页写「零挂起清单里的一个词」 ⇒ M6 红
    case("c11", "在真相页里写入【零挂起措辞清单里的一个词】 ⇒ M6 应红 (★零挂起措辞★)", True, ["M6"])
    # c12 真相页机器块被删 ⇒ M1/M4 fail-closed 红
    case("c12", "把 §1 机器块整块删掉 ⇒ M1/M4 应 fail-closed 判红", True, ["M1", "M4"])

    # ---------- 先取真实的三处陈旧 pin ----------
    res0, pins0, inv0, led0 = run_checks(root, LEDGER_REL)
    stale = [p for p in pins0 if p["cls"] == "P1" and p["stale"]]
    print("沙盒自测 · 真实陈旧 pin %d 处 · %s"
          % (len(stale), ", ".join("%s→%s" % (p["target"].split("/")[-1], (p["actual"] or "")[:8])
                                   for p in stale)))
    if not stale:
        print("★没有陈旧 pin ⇒ 自测无法构造 (★fail-closed★)")
        return 1

    pristine = {}
    npass = 0
    for cid, title, want_red, expect_ids in cases:
        # 每次重建沙盒 (★干净起点★)
        rels = build_sandbox(root, sbx)
        for r in rels:
            p = os.path.join(sbx, r)
            if os.path.exists(p):
                pristine[r] = (p, open(p, "rb").read())
        try:
            _apply_case(cid, sbx, stale, inv0)
            res = _judge(sbx)
            bad = []
            for eid in expect_ids:
                ok = res.get(eid, {}).get("ok", False)
                wr = expect_ids[eid] if isinstance(expect_ids, dict) else want_red
                if wr and ok:
                    bad.append("%s 应红却绿" % eid)
                if (not wr) and (not ok):
                    bad.append("%s 应绿却红: %s" % (eid, "; ".join(res.get(eid, {}).get("errors", [])[:2])))
            if bad:
                print("[FAIL] %-6s %s ⇒ %s" % (cid, title, " / ".join(bad)))
            else:
                print("[ok]   %-6s %s" % (cid, title))
                npass += 1
        except Exception as exc:                # noqa: BLE001
            print("[FAIL] %-6s %s ⇒ 异常 %r" % (cid, title, exc))
        finally:
            shutil.rmtree(sbx, ignore_errors=True)

    print("反向 %d 条 (共 %d)" % (len(cases), len(cases)))
    if npass == len(cases):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED (%d/%d)" % (npass, len(cases)))
    return 1


def _apply_case(cid, sbx, stale, inv):
    """★按用例施加变异 (★全部在沙盒里·★真件一个字节不动★)"""
    p0 = stale[0]
    tgt0 = p0["target"]
    base0 = p0["baseline"]
    act0 = p0["actual"]

    def rows_full():
        out = []
        for p in stale:
            out.append({"iss": "ISS-374", "file": p["target"], "prev": p["baseline"],
                        "md5": p["actual"] or "", "kind": "纯字节追加", "where": "§7",
                        "proof": "★沙盒合成记录·仅供自测★"})
        return out

    if cid == "c01":
        _mk_ledger(sbx, LEDGER_REL, rows_full())
    elif cid == "c02":
        _mk_ledger(sbx, LEDGER_REL, [])
    elif cid == "c03":
        rows = rows_full()
        rows[0]["iss"] = "—"
        _mk_ledger(sbx, LEDGER_REL, rows)
    elif cid == "c04":
        rows = rows_full()
        rows.append({"iss": "ISS-399", "file": tgt0, "prev": "0" * 32, "md5": "1" * 32,
                     "kind": "纯字节追加", "where": "§9", "proof": "★沙盒合成记录·仅供自测★"})
        _mk_ledger(sbx, LEDGER_REL, rows)
    elif cid == "c05":
        rows = rows_full()
        rows[0]["md5"] = "2" * 32
        _mk_ledger(sbx, LEDGER_REL, rows)
    elif cid == "c06":
        # ★专打 M4: 把闸里的常量悄悄改成盘上现值, 台账留空★
        _mk_ledger(sbx, LEDGER_REL, [])
        gp = os.path.join(sbx, p0["gate"])
        txt = open(gp, encoding="utf-8").read()
        assert base0 in txt, "常量不在闸源码里"
        txt = txt.replace(base0, act0)
        open(gp, "w", encoding="utf-8").write(txt)
    elif cid == "c07":
        # ★M4 反向自证: 改常量 + 台账留一行 (prev=登记基线, md5=新常量)★
        rows = rows_full()
        rows[0]["prev"] = base0
        rows[0]["md5"] = act0
        _mk_ledger(sbx, LEDGER_REL, rows)
        gp = os.path.join(sbx, p0["gate"])
        txt = open(gp, encoding="utf-8").read()
        txt = txt.replace(base0, act0)
        open(gp, "w", encoding="utf-8").write(txt)
    elif cid == "c08":
        # 新造一道不在 §1 在册的闸, 硬钉一个 md5
        np = os.path.join(sbx, "MECH", "check_iss399_newgate.py")
        open(np, "w", encoding="utf-8").write(
            'import os\nPIN = {"MECH/check_demo_struct_truth.py": "%s"}\n'
            'def main():\n    return 0\n' % ("3" * 32))
    elif cid == "c09":
        tp = os.path.join(sbx, TRUTH_REL)
        txt = open(tp, encoding="utf-8").read()
        i = txt.find(INV_BEGIN)
        j = txt.find(INV_END)
        blob = txt[i + len(INV_BEGIN):j]
        import re as _re
        blob2 = _re.sub(r'\n\s*\{\s*"gate":\s*"%s"[\s\S]*?\}\s*,\n' % _re.escape(p0["gate"]), "\n", blob, count=1)
        if blob2 == blob:
            # 退一步: 直接把该闸的所有条目删掉
            blob2 = "\n".join(l for l in blob.splitlines()
                              if not (p0["gate"] in l and '"target"' in l))
        open(tp, "w", encoding="utf-8").write(txt[:i] + INV_BEGIN + blob2 + INV_END + txt[j + len(INV_END):])
    elif cid == "c10":
        rows = rows_full()
        rows[0]["kind"] = "随便改改"
        _mk_ledger(sbx, LEDGER_REL, rows)
    elif cid == "c11":
        tp = os.path.join(sbx, TRUTH_REL)
        txt = open(tp, encoding="utf-8").read()
        # ★ISS-399 cont2 修正: 词【从词表里取】而不是在本源码里再写一遍 ⇒
        #   否则本闸源码自己就含那个词 ⇒ M6 扫本闸源码时自命中 ⇒ 假红
        open(tp, "w", encoding="utf-8").write(txt + "\n" + FORBIDDEN_PENDING[0] + "\n")
    elif cid == "c12":
        tp = os.path.join(sbx, TRUTH_REL)
        txt = open(tp, encoding="utf-8").read()
        i = txt.find(INV_BEGIN)
        j = txt.find(INV_END)
        open(tp, "w", encoding="utf-8").write(txt[:i] + txt[j + len(INV_END):])
    else:
        raise AssertionError("未知用例 %s" % cid)


# ====================================================================== main
def main(argv):
    ap = argparse.ArgumentParser(description="ISS-399 MECH 域已签收件追加台账自守闸")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ledger", default=LEDGER_REL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    res, pins, inv, led = run_checks(root, args.ledger)
    if args.json:
        print(json.dumps({k: {"ok": v["ok"], "title": v["title"], "errors": v["errors"]}
                          for k, v in res.items()}, ensure_ascii=False, indent=1))
        return 0 if all(v["ok"] for v in res.values()) else 1

    print("ISS-399 · MECH 域【已签收件追加登记台账】自守闸")
    print("=" * 78)
    nfail = 0
    for cid in ("M1", "M2", "M3", "M4", "M5", "M6", "M7"):
        v = res.get(cid, {})
        if v.get("ok"):
            print("[ok]   %-4s %s" % (cid, v.get("title", "")))
        else:
            nfail += 1
            print("[FAIL] %-4s %s" % (cid, v.get("title", "")))
            for e in v.get("errors", []):
                print("       · %s" % e)
    p1 = [p for p in pins if p["cls"] == "P1"]
    p2 = [p for p in pins if p["cls"] == "P2"]
    p3 = [p for p in pins if p["cls"] == "P3"]
    print("-" * 78)
    print("枚举: 硬钉(无通道) %d 处 / 板族钉 %d 处 / 台账通道钉 %d 处 ⇒ 合计 %d 处"
          % (len(p1), len(p2), len(p3), len(pins)))
    print("判据 M1~M7 · 失败 %d 条" % nfail)
    if nfail == 0:
        print("PASS")
        return 0
    print("FAIL")
    print("★**本闸的【预期读数】= rc=1 (红)**: 红的是【现状】"
          "(★3 处陈旧 pin 归因不到台账·★不是闸故障★) ⇒ ★**不许为了让它绿而放宽判据** ★")
    print("★绿的唯一条件 = ① 3 处陈旧 pin 在台账里有登记行 (单号+prev_md5+md5 四项齐全)"
          "② 台账落位 (M-A 待 main 拍) ③ §1 在册清单与盘面零差 ★")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
