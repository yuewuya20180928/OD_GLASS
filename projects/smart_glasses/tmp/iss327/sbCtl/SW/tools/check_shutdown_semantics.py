#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_shutdown_semantics.py — ISS-234 「关机 / 待机 / 关机充电灯」三口径机器门禁
=====================================================================================
目的: 机械判定"关机语义"的三条产品口径
      (K1 关机 = 真断电 · K2 关机(断电) <0.05W · K3 关机时充电灯)
      与**三份文档** + **网表真源**是否一致 —— 防止:
        ① 有人把"关机"悄悄改回"深睡" (或反过来) ⇒ 三份文档各说各话
        ② 文档说"真断电"但网表里其实断不了 (或反过来)
        ③ 关机态静态电流账的数字被人手改过 (三处对拍)
        ④ 交付物 (六格矩阵 / 给老板的一页 / 证据分级 / 留痕) 被删减

★铁律 (SOUL.md):
  1. 本脚本 **不编任何功耗 / 时延数字** —— 它只核对**文档口径与网表事实**;
     所有被核对的数字 (108µA / 0.40mW / 10k / 0.05W ...) 来自
     `SW/SHUTDOWN_SEMANTICS_SPEC.md` 的**机器可读基准块** 与 `HW/POWER_SHUTDOWN_V3.md`,
     本脚本只验"在位 / 不在位 / 对不对得上"。
  2. **网表是只读的**: 本脚本只读 `HW/netlist_v1.csv`, 从不写它;
     反向用例写的是**临时目录里的副本** (真盘一个字节不动)。
  3. ★**内容级, 不挂 md5**: 网表在飞 (hw-lead 并发落表) ⇒ md5 随时会漂
     ⇒ 本门禁**不锚 md5**, 一律按**位号 / 网名 / 拓扑**判定 ⇒ 落表后仍成立。
  4. 退出码 0 = 全过; 1 = 有项不通过; 2 = 用法错误。

★R4 的「作用域 + 拓扑级」判据 (为什么不是"网表里有没有开关器件"):
  · 任务书原写法「关机=深睡 ⇒ 网表里**不得**有负载开关」若按**全局**执行会**假红**:
    demo 板上 `U_EN_SW` 就在网表里 (必装) ⇒ 全局写法必红。
  · 但 `U_EN_SW` **不构成"关机 = 真断电"的能力** —— 它的输出 `RAIL_BOARD_5V`
    **不回到 SoM 的电源脚** ⇒ 拿掉它, demo 板照样带电。
  · ⇒ 本门禁改成**作用域 + 拓扑级**: "拿掉这颗器件后, 该作用域的源与受电端还连不连通"
    (图论割边判定) ⇒ 判的是**能力**, 不是**器件清单**。

★读网表的一个坑 (已写进 `SW/SHUTDOWN_SEMANTICS_SPEC.md` §6.3):
  这张网表是 **"一行 = 一根导线 = 同一网上两个器件脚"**, `ref` 列只代表这条线的其中一端
  ⇒ **器件归属必须从 node 字符串反推** (`<位号> pin<N>` ⇒ 属于 `<位号>`), 不靠 `ref` 列。

用法:
    python3 SW/tools/check_shutdown_semantics.py                # 核对 (rc=0 = 全过)
    python3 SW/tools/check_shutdown_semantics.py --selftest      # 反向自检 (每条都必须变红)
    python3 SW/tools/check_shutdown_semantics.py --json          # 机读输出
    python3 SW/tools/check_shutdown_semantics.py --root <目录>   # 指定项目根 (自检用)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile
from collections import defaultdict

try:
    import yaml
except Exception:  # noqa: BLE001
    yaml = None

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>

SPEC_REL = os.path.join("SW", "SHUTDOWN_SEMANTICS_SPEC.md")
HW_REL = os.path.join("HW", "POWER_SHUTDOWN_V3.md")
MIRROR_REL = os.path.join("SW", "POWER_STATE_SEMANTICS.md")
NETLIST_REL = os.path.join("HW", "netlist_v1.csv")

BASELINE_BEGIN = "<!-- BEGIN 口径基准块"
BASELINE_END = "<!-- END 口径基准块"

# ★六格矩阵的机器标记 (三状态 × 两口径)
SIX_CELLS = [
    "工作·demo板", "工作·整机",
    "待机·demo板", "待机·整机",
    "关机·demo板", "关机·整机",
]

# ★关机电源账的 5 个分项 (基准块里的键名 → 分项数值)
BUDGET_ITEMS = ["AON_uA", "BQ25896_uA", "BQ2970_uA", "负载开关IQ_uA", "VBUS_DET_uA"]

# ★关机电源账的 5 个分项在文档里必须出现的 µA 记号 (对拍用)
BUDGET_TOKENS = ["50µa", "2µa", "1µa", "5µa", "108µa", "0.40mw"]

EVIDENCE_TAGS = ["[实测]", "[推算]", "[0数据]", "[官网]"]

# ★归一化: 去空白 / 去引号 / 去 markdown 强调符, µ→u, °→deg, 全小写
_NORM_STRIP = re.compile(r"[\s\"'`*“”‘’「」『』]")


def norm(s) -> str:
    if s is None:
        return ""
    s = _NORM_STRIP.sub("", str(s))
    s = s.replace("µ", "u").replace("μ", "u").replace("Ω", "ohm").replace("°", "deg")
    return s.lower()


def read_text(root: str, rel: str) -> str:
    p = os.path.join(root, rel)
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _owner_of_node(node: str) -> str:
    """node → 它属于哪个位号: "U_PWR_SW pin3" → "U_PWR_SW"; "J_USB_C A4+A9" → "J_USB_C"."""
    return node.split(" ")[0].strip()


def _is_gnd(node: str) -> bool:
    """★地是公共节点: 不并进电气图 (否则 "BAT_SW 经 GND 到 RAIL_SYS" 会造出假路径)。"""
    return node.strip() == "GND"


class Netlist:
    """`HW/netlist_v1.csv` 的只读封装 + 电气连通性模型 (并查集)。"""

    def __init__(self, path: str):
        self.path = path
        with open(path, encoding="utf-8", errors="ignore") as f:
            self.rows = list(csv.DictReader(f))
        self._parent = {}
        self.pins = {}          # ref -> set(node)
        self.rows_of = {}       # ref -> list(row)
        self.dev = {}           # ref -> {value,type,dnp,opn,board}
        net_nodes = defaultdict(list)
        for r in self.rows:
            ref = (r.get("ref") or "").strip()
            if not ref:
                continue
            self.rows_of.setdefault(ref, []).append(r)
            n1 = (r.get("node1") or "").strip()
            n2 = (r.get("node2") or "").strip()
            net = (r.get("net") or "").strip()
            for n in (n1, n2):
                if not n or _is_gnd(n):
                    continue
                self.pins.setdefault(_owner_of_node(n), set()).add(n)
                self._find(n)
            if net and not _is_gnd(net):
                net_nodes[net].extend([n for n in (n1, n2) if n])
        # ★同一 net 名 = 同一电气节点 (解决 "SYS" / "RAIL_SYS" 这种网名与轨名不同字的写法)
        for _net, nodes in net_nodes.items():
            first = nodes[0]
            for n in nodes[1:]:
                self._union(first, n)
        # ★网名 → 电气节点 (作用域里写的 "BAT_SW" 是**网名**, 不是 node 名 ⇒ 必须能解析)
        self.net_group = {}
        for _net, nodes in net_nodes.items():
            self.net_group[_net] = self._find(nodes[0])
        # ★器件属性: 取 ref 列里"最像器件行"的那一行 (有 type / value 最全的)
        for ref, rr in self.rows_of.items():
            best = None
            for r in rr:
                score = 0
                if (r.get("node1") or "").strip() == ref and (r.get("node2") or "").strip() == ref:
                    score += 4
                if (r.get("type") or "") not in ("NET", "RAIL", ""):
                    score += 2
                score += len(r.get("value") or "")
                if best is None or score > best[0]:
                    best = (score, r)
            r = best[1]
            self.dev[ref] = {
                "value": r.get("value") or "",
                "type": r.get("type") or "",
                "dnp": r.get("dnp") or "",
                "opn": r.get("opn") or "",
                "board": r.get("board") or "",
                "installed": any((x.get("dnp") or "") == "必装" for x in rr),
                "rows": len(rr),
            }

    # ---------------- 并查集 ----------------
    def _find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def _union(self, a: str, b: str) -> None:
        ra, rb = self._find(a), self._find(b)
        if ra != rb:
            self._parent[rb] = ra

    def group(self, node: str) -> str:
        return self._find(node)

    def resolve(self, name: str) -> str:
        """名字 → 电气节点: 先当 node 解析, 再当 net 名解析 (★作用域里写的可能是网名)。"""
        if name in self._parent:
            return self._find(name)
        if name in self.net_group:
            return self.net_group[name]
        return self._find(name)

    def groups_of(self, ref: str) -> set:
        return {self._find(n) for n in self.pins.get(ref, set())}

    # ---------------- 开关候选 ----------------
    def switch_candidates(self) -> list:
        out = []
        for ref, d in self.dev.items():
            is_sw = False
            if ref in ("U_PWR_SW", "U_EN_SW"):
                is_sw = True
            elif d["type"] == "IC" and re.search(r"(负载开关|电源开关|load switch)", d["value"], re.I):
                is_sw = True
            elif d["type"] == "SW":
                is_sw = True
            if is_sw:
                out.append(ref)
        return sorted(out)

    # ---------------- 拓扑: 割边判定 ----------------
    def _adjacency(self, skip: str | None) -> dict:
        """器件 → 电气节点 的连通图 (★GND 整个剔除: 地是公共节点, 留着会造成假路径)。"""
        adj = defaultdict(set)
        for ref, nodes in self.pins.items():
            if ref == skip:
                continue
            gs = set()
            for n in nodes:
                g = self._find(n)
                if g == "GND":
                    continue
                gs.add(g)
            if len(gs) < 2:
                continue
            for a in gs:
                adj[a].update(gs - {a})
        return adj

    def _reachable(self, adj: dict, src: str) -> set:
        seen = {src}
        stack = [src]
        while stack:
            cur = stack.pop()
            for nxt in adj.get(cur, ()):  # noqa: B007
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def cut_devices(self, src_node: str, tgt_nodes: list, candidates: list) -> list:
        """返回"拿掉它 ⇒ 源与受电端就断开"的器件位号 (割边)。

        ★源与受电端本来就在同一个电气节点 ⇒ 任何器件都断不开 ⇒ 返回空表
          (这正是 demo 板 SoM 直连 Type-C 5V 的情形)。
        """
        src = self.resolve(src_node)
        tgts = {self.resolve(t) for t in tgt_nodes if t}
        if not tgts:
            return []
        if src in tgts:
            return []
        out = []
        for ref in candidates:
            adj = self._adjacency(skip=ref)
            reach = self._reachable(adj, src)
            if not (tgts & reach):
                out.append(ref)
        return sorted(out)

    def on_net(self, ref: str, net: str) -> bool:
        for r in self.rows_of.get(ref, []):
            if (r.get("net") or "").strip() == net:
                return True
        return False

    def boards_of(self, ref: str) -> set:
        return {(r.get("board") or "").strip() for r in self.rows_of.get(ref, [])
                if (r.get("board") or "").strip()}


# ---------------------------------------------------------------- 基���块解析
def parse_baseline(spec_text: str):
    i = spec_text.find(BASELINE_BEGIN)
    j = spec_text.find(BASELINE_END)
    if i < 0 or j < 0 or j < i:
        return None, "基准块标记不在位 (BEGIN/END 找不到)"
    block = spec_text[i + len(BASELINE_BEGIN):j]
    m = re.search(r"```ya?ml\s*(.*?)```", block, re.S)
    if not m:
        return None, "基准块里没有 yaml 代码块"
    if yaml is None:
        return None, "本机没有 PyYAML, 解析不了基准块"
    try:
        data = yaml.safe_load(m.group(1))
    except Exception as exc:  # noqa: BLE001
        return None, "基准块 yaml 解析失败: %s" % exc
    if not isinstance(data, dict) or "口径基准" not in data:
        return None, "基准块结构不对 (缺 口径基准 顶层键)"
    return data["口径基准"], ""


# ---------------------------------------------------------------- R1
def check_r1_baseline(base) -> list:
    fails = []
    if base is None:
        return ["R1 口径基准块缺失或不可解析 (fail-closed: 没有基准就不许判过)"]
    need = ["版本", "产单号", "口径字面值", "锁死项字面值", "关机电源账", "作用域"]
    for k in need:
        if k not in base:
            fails.append("R1 基准块缺字段: %s" % k)
    lits = base.get("口径字面值") or {}
    for k in ("K1", "K2", "K3"):
        if not lits.get(k):
            fails.append("R1 基准块缺口径字面值: %s" % k)
    scopes = base.get("作用域") or {}
    if not scopes:
        fails.append("R1 基准块缺作用域 (至少 demo + 整机)")
    for name, sc in scopes.items():
        for k in ("关机语义", "供电源节点", "受电节点"):
            if k not in sc:
                fails.append("R1 作用域 %s 缺字段: %s" % (name, k))
        if sc.get("关机语义") not in ("真断电", "深睡"):
            fails.append("R1 作用域 %s 的 关机语义 只能是 '真断电' 或 '深睡', 现在是 %r"
                         % (name, sc.get("关机语义")))
    return fails


# ---------------------------------------------------------------- R2
def check_r2_literals(spec_text: str, hw_text: str, mirror_text: str, base) -> list:
    fails = []
    if base is None:
        return ["R2 基准块不可解析, 口径对拍无法进行"]
    lits = base.get("口径字面值") or {}
    docs = [("口径页 SW/SHUTDOWN_SEMANTICS_SPEC.md", spec_text),
            ("HW/POWER_SHUTDOWN_V3.md", hw_text),
            ("SW/POWER_STATE_SEMANTICS.md", mirror_text)]
    for key in ("K1", "K2", "K3"):
        lit = lits.get(key)
        if not lit:
            continue
        target = norm(lit)
        for name, text in docs:
            if target not in norm(text):
                fails.append("R2 %s 在 %s 里找不到字面值 '%s'" % (key, name, lit))
    # ★K1 必须落在 HW 文档的 §0 一页纸结论里 (口径基准必须在那儿)
    hw0 = ""
    m = re.search(r"^##\s*§0\b(.*?)(?=^##\s)", hw_text, re.S | re.M)
    if m:
        hw0 = m.group(1)
    else:
        fails.append("R2 在 HW/POWER_SHUTDOWN_V3.md 里找不到 §0 一页纸结论段")
    if hw0 and norm(lits.get("K1", "")) not in norm(hw0):
        fails.append("R2 K1 ('%s') 不在 HW 文档 §0 一页纸结论里" % lits.get("K1", ""))
    return fails


# ---------------------------------------------------------------- R3
def check_r3_budget(spec_text: str, hw_text: str, mirror_text: str, base) -> list:
    fails = []
    if base is None:
        return ["R3 基准块不可解析, 电流账对拍无法进行"]
    docs = [("口径页", spec_text), ("HW/POWER_SHUTDOWN_V3.md", hw_text),
            ("SW/POWER_STATE_SEMANTICS.md", mirror_text)]
    for name, text in docs:
        n = norm(text)
        for tok in ("108µa", "0.40mw"):
            if norm(tok) not in n:
                fails.append("R3 %s 里找不到关机静态电流数字 '%s'" % (name, tok))
    # ★HW 文档的两处关机行必须含 5 个分项 + 合计
    hw_lines = hw_text.split("\n")
    budget_line = None
    off_line = None
    for ln in hw_lines:
        if "关机态的静态电流预算" in ln:
            budget_line = ln
        if re.match(r"^\|\s*\*\*关机\*\*", ln):
            off_line = ln
    if budget_line is None:
        fails.append("R3 HW/POWER_SHUTDOWN_V3.md 里找不到 §0 的『关机态的静态电流预算』行")
    else:
        for tok in BUDGET_TOKENS:
            if norm(tok) not in norm(budget_line):
                fails.append("R3 HW §0 关机预算行里缺 '%s'" % tok)
    if off_line is None:
        fails.append("R3 HW/POWER_SHUTDOWN_V3.md 里找不到 §6 的『关机 (真断电)』行")
    else:
        for tok in BUDGET_TOKENS:
            if norm(tok) not in norm(off_line):
                fails.append("R3 HW §6 关机行里缺 '%s'" % tok)
    # ★基准块自身: 分项之和 == 合计, 且合计与 mW 对得上 (3.7V)
    bud = base.get("关机电源账") or {}
    try:
        items = [float(bud[k]) for k in BUDGET_ITEMS if k in bud]
        total = float(bud.get("合计_uA", -1))
        mw = float(bud.get("合计_mW", -1))
    except Exception:  # noqa: BLE001
        return fails + ["R3 基准块的关机电源账里有非数值项"]
    if len(items) != len(BUDGET_ITEMS):
        fails.append("R3 基准块的关机电源账缺分项 (要 %d 项)" % len(BUDGET_ITEMS))
    if items and abs(sum(items) - total) > 0.5:
        fails.append("R3 基准块关机电源账: 分项之和 %.1fµA ≠ 合计 %.1fµA"
                     % (sum(items), total))
    if total > 0 and mw > 0:
        implied = mw * 1000.0 / 3.7
        if abs(implied - total) > 2.0:
            fails.append("R3 基准块关机电源账: %.2fmW @3.7V ⇒ %.1fµA, 与合计 %.1fµA 对不上"
                         % (mw, implied, total))
    return fails


# ---------------------------------------------------------------- R4
def check_r4_semantics(net: Netlist, base) -> list:
    fails = []
    if base is None:
        return ["R4 基准块不可解析, 语义对拍无法进行"]
    scopes = base.get("作用域") or {}
    for name, sc in scopes.items():
        sem = sc.get("关机语义")
        src = sc.get("供电源节点")
        tgts = sc.get("受电节点") or []
        if not src or not tgts:
            fails.append("R4 作用域 %s 的 供电源节点/受电节点 没填全" % name)
            continue
        cands = net.switch_candidates()
        cuts = net.cut_devices(src, tgts, cands)
        if sem == "真断电":
            if not cuts:
                fails.append("R4 作用域 %s 声明『关机 = 真断电』, 但网表上**没有任何器件**能断开它的主供电轨"
                             " (源 %s → 受电端 %s); ⇒ 要么改口径, 要么改板" % (name, src, "/".join(tgts)))
            declared = sc.get("断电开关位号")
            if declared and declared not in cuts:
                fails.append("R4 作用域 %s 声明的断电开关 '%s' 不在拓扑割边集合里 %s"
                             % (name, declared, cuts))
        elif sem == "深睡":
            if cuts:
                fails.append("R4 作用域 %s 声明『关机 = 深睡』, 但网表上这些器件能断开它的主供电轨 %s"
                             " ⇒ 口径页漏了新能力 (或网表与口径不一致)" % (name, cuts))
        # ---- 作用域专属附加判据 ----
        if name == "整机":
            fails += _check_scope_整机(net, sc)
        else:
            fails += _check_scope_demo(net, sc)
    return fails


def _check_scope_整机(net: Netlist, sc: dict) -> list:
    fails = []
    main_board = sc.get("主板") or "MAIN_PCB"
    pd_ref = sc.get("ON脚下拉位号") or "R_PD_ON"
    if pd_ref not in net.dev:
        fails.append("R4 整机作用域: ON 脚下拉电阻 '%s' 不在网表里" % pd_ref)
    else:
        val = norm(net.dev[pd_ref]["value"])
        want = str(sc.get("ON脚下拉阻值_ohm", 10000))
        if "10k" not in val and "10000" not in val:
            fails.append("R4 整机作用域: '%s' 的阻值不是 10k (%r)" % (pd_ref, net.dev[pd_ref]["value"]))
        if not net.on_net(pd_ref, "GND"):
            fails.append("R4 整机作用域: '%s' 没有接到 GND ⇒ 下拉不存在" % pd_ref)
        if not net.dev[pd_ref]["installed"]:
            fails.append("R4 整机作用域: '%s' 是 DNP ⇒ 默认关不成立" % pd_ref)
        if main_board not in net.boards_of(pd_ref):
            fails.append("R4 整机作用域: '%s' 不在主板 '%s' 上 (落哪块板?)" % (pd_ref, main_board))
    fet = sc.get("高边FET位号") or "Q_PG"
    if fet not in net.dev:
        fails.append("R4 整机作用域: 高边 FET '%s' 不在网表里" % fet)
    else:
        val = norm(net.dev[fet]["value"])
        if "n-mos" in val:
            fails.append("R4 整机作用域: '%s' 是 **N-MOS 低边**接法 ⇒ ★P0: 插电也开不了机"
                         " (正解是 P-MOS 高边, 见 HW/POWER_SHUTDOWN_V3.md §3)" % fet)
        elif "p-mos" not in val:
            fails.append("R4 整机作用域: '%s' 的值里没写明 P-MOS 高边 (%r)"
                         % (fet, net.dev[fet]["value"]))
        if main_board not in net.boards_of(fet):
            fails.append("R4 整机作用域: 高边 FET '%s' 不在主板 '%s' 上 (落哪块板?)" % (fet, main_board))
    sw_ref = sc.get("断电开关位号") or "U_PWR_SW"
    if sw_ref in net.dev and main_board not in net.boards_of(sw_ref):
        fails.append("R4 整机作用域: 断电开关 '%s' 不在主板 '%s' 上 (落哪块板?)" % (sw_ref, main_board))
    for ref in sc.get("上游电源链位号") or []:
        if ref not in net.dev:
            fails.append("R4 整机作用域: 上游电源链位号 '%s' 不在网表里" % ref)
    # ★关机时充电灯 (K3 适用) 的硬件必须在位
    chg = sc.get("充电链") or {}
    led = chg.get("充电灯位号") or "Q_CHG_LED"
    ic = chg.get("充电IC位号") or "U_CHG"
    if chg.get("适用性") == "适用":
        if ic not in net.dev:
            fails.append("R4 整机作用域: 充电 IC '%s' 不在网表里" % ic)
        if led not in net.dev:
            fails.append("R4 整机作用域: 充电灯驱动 '%s' 不在网表里" % led)
        else:
            if not net.dev[led]["installed"]:
                fails.append("R4 整机作用域: 充电灯驱动 '%s' 是 DNP ⇒ 关机时充电灯点不亮" % led)
            if not net.on_net(led, "CHG_STAT"):
                fails.append("R4 整机作用域: 充电灯驱动 '%s' 没挂在 CHG_STAT 网上" % led)
    return fails


def _check_scope_demo(net: Netlist, sc: dict) -> list:
    fails = []
    gate = sc.get("底板支路门控") or {}
    sw = gate.get("开关位号") or "U_EN_SW"
    rail = gate.get("门控轨") or "RAIL_BOARD_5V"
    if sw not in net.dev:
        fails.append("R4 demo 作用域: 底板支路门控开关 '%s' 不在网表里" % sw)
    else:
        main_board = sc.get("主板") or "MAIN_PCB"
        if main_board not in net.boards_of(sw):
            fails.append("R4 demo 作用域: 门控开关 '%s' 不在主板 '%s' 上 (落哪块板?)"
                         % (sw, main_board))
    rail_g = net.group(rail) if rail in net.pins or rail in net.dev else None
    if rail_g is None:
        fails.append("R4 demo 作用域: 门控轨 '%s' 不在网表里" % rail)
    else:
        for ref in gate.get("门控器件") or []:
            if ref not in net.dev:
                fails.append("R4 demo 作用域: 门控器件 '%s' 不在网表里" % ref)
                continue
            if rail_g not in net.groups_of(ref):
                fails.append("R4 demo 作用域: 门控器件 '%s' 没挂在门控轨 '%s' 上 ⇒ 断轨断不到它"
                             % (ref, rail))
    chg = sc.get("充电链") or {}
    main_board = sc.get("主板") or "MAIN_PCB"
    ic = chg.get("充电IC位号") or "U_CHG"
    if chg.get("适用性") == "不适用":
        # ★demo 装机态没有充电板 ⇒ 主板上不许有充电 IC
        for r in net.rows:
            if r.get("board") == main_board and re.search(r"BQ25896", r.get("value") or "", re.I):
                fails.append("R4 demo 作用域: 口径说 K3『关机时充电灯』不适用, 但主板 '%s' 上有充电 IC (%s)"
                             % (main_board, r.get("ref")))
                break
    return fails


# ---------------------------------------------------------------- R5
def check_r5_deliverables(spec_text: str) -> list:
    fails = []
    n = norm(spec_text)
    for cell in SIX_CELLS:
        if norm(cell) not in n:
            fails.append("R5 六格矩阵缺一格: %s (工作/待机/关机 × demo/整机)" % cell)
    n_ask = len(re.findall(r"我的推荐默认值", spec_text))
    n_cost = len(re.findall(r"不拍的后果", spec_text))
    n_q = len(re.findall(r"^###\s*Q\d", spec_text, re.M))
    if not (3 <= n_q <= 5):
        fails.append("R5 给老板的一页应是 3~5 条, 现在 %d 条" % n_q)
    if n_ask < 3:
        fails.append("R5 给老板的一页里『我的推荐默认值』只有 %d 处 (每条都要有)" % n_ask)
    if n_cost != n_ask:
        fails.append("R5 『不拍的后果』%d 处 ≠ 『我的推荐默认值』%d 处 (每条都要成对)" % (n_cost, n_ask))
    return fails


# ---------------------------------------------------------------- R6
def check_r6_evidence(spec_text: str) -> list:
    fails = []
    for tag in EVIDENCE_TAGS:
        if tag not in spec_text:
            fails.append("R6 证据分级标注缺 '%s'" % tag)
    if "60ms" not in spec_text:
        fails.append("R6 没写端到端 60ms 这条硬指标的影响")
    if "43°C" not in spec_text and "43°c" not in spec_text:
        fails.append("R6 没写皮肤 43°C 这条硬指标的影响")
    return fails


# ---------------------------------------------------------------- R7
def check_r7_trace(spec_text: str) -> list:
    fails = []
    if "ISS-234" not in spec_text:
        fails.append("R7 留痕缺失: 口径页里没有 ISS-234 标记")
    i = spec_text.find("§7.1")
    if i < 0:
        fails.append("R7 留痕缺失: 口径页里没有 §7.1『改了什么 → 谁会红』反向用例表")
        return fails
    tail = spec_text[i:]
    rows = [ln for ln in tail.split("\n") if re.match(r"^\|.*\*\*R\d\*\*", ln)]
    if len(rows) < 6:
        fails.append("R7 反向用例表只有 %d 行 (<6 条)" % len(rows))
    return fails


# ---------------------------------------------------------------- 总跑
def run_all(root: str) -> tuple:
    """⇒ (fails: list[str], info: dict)"""
    spec_text = read_text(root, SPEC_REL)
    hw_text = read_text(root, HW_REL)
    mirror_text = read_text(root, MIRROR_REL)
    base, base_err = parse_baseline(spec_text)

    fails = []
    fails += check_r1_baseline(base)
    if base is None:
        fails.append("R1 基准块解析失败: %s" % base_err)
    fails += check_r2_literals(spec_text, hw_text, mirror_text, base)
    fails += check_r3_budget(spec_text, hw_text, mirror_text, base)

    net_path = os.path.join(root, NETLIST_REL)
    info = {"netlist": net_path, "netlist_rows": 0}
    if not os.path.exists(net_path):
        fails.append("R4 读不到网表 %s" % net_path)
        net = None
    else:
        net = Netlist(net_path)
        info["netlist_rows"] = len(net.rows)
        info["switch_candidates"] = net.switch_candidates()
        fails += check_r4_semantics(net, base)
        if base:
            info["scopes"] = {}
            for name, sc in (base.get("作用域") or {}).items():
                cuts = net.cut_devices(sc.get("供电源节点", ""), sc.get("受电节点") or [],
                                      net.switch_candidates())
                info["scopes"][name] = {
                    "关机语义": sc.get("关机语义"),
                    "供电源节点": sc.get("供电源节点"),
                    "受电节点": sc.get("受电节点"),
                    "拓扑割边器件": cuts,
                }

    fails += check_r5_deliverables(spec_text)
    fails += check_r6_evidence(spec_text)
    fails += check_r7_trace(spec_text)
    return fails, info


# ---------------------------------------------------------------- 反向自检
def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _read_file(path: str) -> str:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _mut_spec_replace(old: str, new: str):
    def fn(path):
        t = _read_file(path)
        if old not in t:
            raise AssertionError("改坏动作没生效: %r 不在文件里" % old)
        _write(path, t.replace(old, new))
    return fn


def _mut_spec_drop_line(needle: str):
    def fn(path):
        lines = _read_file(path).split("\n")
        kept = [ln for ln in lines if needle not in ln]
        if len(kept) == len(lines):
            raise AssertionError("改坏动作没生效: %r 不在文件里" % needle)
        _write(path, "\n".join(kept))
    return fn


def _mut_spec_drop_block(begin: str, end: str):
    def fn(path):
        t = _read_file(path)
        out = re.sub(re.escape(begin) + r".*?" + re.escape(end), "", t, flags=re.S)
        if out == t:
            raise AssertionError("改坏动作没生效: %s 块不在文件里" % begin)
        _write(path, out)
    return fn


def _mut_csv_drop_ref(ref: str):
    def fn(path):
        lines = _read_file(path).split("\n")
        head = lines[0]
        kept = [head]
        n = 0
        for ln in lines[1:]:
            cols = ln.split(",")
            if len(cols) > 4 and cols[4].strip() == ref:
                n += 1
                continue
            kept.append(ln)
        if n == 0:
            raise AssertionError("改坏动作没生效: 网表里没有 %s 的行" % ref)
        _write(path, "\n".join(kept))
    return fn


def _mut_csv_line(ref: str, old: str, new: str):
    def fn(path):
        lines = _read_file(path).split("\n")
        hit = 0
        for i, ln in enumerate(lines):
            cols = ln.split(",")
            if len(cols) > 4 and cols[4].strip() == ref and old in ln:
                lines[i] = ln.replace(old, new, 1)
                hit += 1
        if hit == 0:
            raise AssertionError("改坏动作没生效: %s 的行里没有 %r" % (ref, old))
        _write(path, "\n".join(lines))
    return fn


# ★★ 反向用例表 (每条: 用例名 · 破坏动作 · 期望变红的规则)
#   ★ 门禁不许把红灯调没 ⇒ 每条都必须在**被破坏后**变红, 否则自检失败。
SELFTEST_CASES = [
    ("REV-01 口径页把 K1『关机 = 真断电』改成『关机 = 深睡』",
     ("spec", _mut_spec_replace("K1: \"关机 = 真断电\"", "K1: \"关机 = 深睡\"")), "R2"),
    ("REV-02 HW 文档把 K2『关机(断电) <0.05W』抹掉",
     ("hw", _mut_spec_replace("关机(断电) <0.05W", "关机(断电) <0.2W")), "R2"),
    ("REV-03 SW 镜像把 K3『关机时充电灯』抹掉",
     ("mirror", _mut_spec_replace("关机时充电灯", "关机时充点")), "R2"),
    ("REV-04 口径页把关机静态电流 108µA 改成 118µA",
     ("spec", _mut_spec_replace("108µA", "118µA")), "R3"),
    ("REV-05 基准块里把合计 0.40mW 改成 0.50mW",
     ("spec", _mut_spec_replace("合计_mW: 0.40", "合计_mW: 0.50")), "R3"),
    ("REV-06 从网表删掉 U_PWR_SW (断电主开关)",
     ("net", _mut_csv_drop_ref("U_PWR_SW")), "R4"),
    ("REV-07 从网表删掉 R_PD_ON (ON 脚 10k 下拉)",
     ("net", _mut_csv_drop_ref("R_PD_ON")), "R4"),
    ("REV-08 把 Q_PG 从 P-MOS 高边改成 N-MOS 低边 (★V1.9 P0 接法★)",
     ("net", _mut_csv_line("Q_PG", "P-MOS", "N-MOS")), "R4"),
    ("REV-09 把 demo 作用域的关机语义改成『真断电』 (网表上做不到)",
     ("spec", _mut_spec_replace("关机语义: 深睡", "关机语义: 真断电")), "R4"),
    ("REV-10 把整机作用域的关机语义改成『深睡』 (网表上有开关)",
     ("spec", _mut_spec_replace("关机语义: 真断电", "关机语义: 深睡")), "R4"),
    ("REV-11 把 Q_PG 的行从 MAIN_PCB 挪走 (断电开关不在主板上)",
     ("net", _mut_csv_line("Q_PG", "MAIN_PCB", "CHG_BOARD")), "R4"),
    ("REV-12 把充电 IC 从充电板挪到主板 (demo 的 K3『不适用』口径过期)",
     ("net", _mut_csv_line("U_CHG", "CHG_BOARD", "MAIN_PCB")), "R4"),
    ("REV-13 基准块整个删掉 (fail-closed)",
     ("spec", _mut_spec_drop_block(BASELINE_BEGIN, BASELINE_END)), "R1"),
    ("REV-14 六格矩阵删掉一格 (关机 · 整机)",
     ("spec", _mut_spec_drop_line("**关机 · 整机**")), "R5"),
    ("REV-15 给老板的一页删掉一条『不拍的后果』",
     ("spec", _mut_spec_drop_line("不拍的后果")), "R5"),
    ("REV-16 把证据分级标注 [0数据] 抹掉",
     ("spec", _mut_spec_replace("[0数据]", "[没数据]")), "R6"),
    ("REV-17 把 §7.1 反向用例表整节删掉 (留痕没了)",
     ("spec", _mut_spec_drop_line("**R4** 红")), "R7"),
]

TREE_FILES = (SPEC_REL, HW_REL, MIRROR_REL, NETLIST_REL)


def _build_tree(tmp: str, root: str, name: str) -> str:
    work = os.path.join(tmp, name)
    for rel in TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work


def selftest(root: str) -> int:
    print("=== SELFTEST (反向用例: 每条都必须在被破坏后变红) ===")
    print("    用例总数: %d (本单硬指标: ≥6)" % len(SELFTEST_CASES))
    passed = 0
    failed = 0
    with tempfile.TemporaryDirectory(prefix="iss234_gate_") as tmp:
        for idx, (name, (target, mutate), expect) in enumerate(SELFTEST_CASES, start=1):
            work = _build_tree(tmp, root, "case_%02d" % idx)
            rel = {"spec": SPEC_REL, "hw": HW_REL, "mirror": MIRROR_REL, "net": NETLIST_REL}[target]
            path = os.path.join(work, rel)
            try:
                mutate(path)
            except AssertionError as exc:
                print("  ❌ %-58s ⇒ 改坏动作失败: %s" % (name[:58], exc))
                failed += 1
                continue
            fails, _info = run_all(work)
            hit = [f for f in fails if f.startswith(expect)]
            if hit:
                print("  ✅ %-58s ⇒ %s 变红 (%s)" % (name[:58], expect, hit[0][:78]))
                passed += 1
            else:
                print("  ❌ %-58s ⇒ **没有变红** (期望 %s); 实得: %s"
                      % (name[:58], expect, (fails[0][:78] if fails else "(无失败 ⇒ 门禁没抓住)")))
                failed += 1
    print("SELFTEST %d/%d 通过, rc=%d" % (passed, passed + failed, 0 if failed == 0 else 1))
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-234 关机语义三口径机器门禁")
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认 = 本文件上两级)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    fails, info = run_all(root)
    if args.json:
        print(json.dumps({"ok": not fails, "fails": fails, "info": info},
                         ensure_ascii=False, indent=2))
        return 0 if not fails else 1

    print("=== ISS-234 关机语义三口径门禁 (SW/tools/check_shutdown_semantics.py) ===")
    print("    根目录: %s" % root)
    print("    网表:   %s (%s 行)" % (info.get("netlist"), info.get("netlist_rows")))
    print("    开关候选: %s" % (info.get("switch_candidates") or "(无)"))
    for name, sc in (info.get("scopes") or {}).items():
        print("    作用域 %s: 关机语义=%s · 拓扑割边器件=%s"
              % (name, sc.get("关机语义"), sc.get("拓扑割边器件") or "(无)"))
    if not fails:
        print("✅ R1~R7 全过 (口径页 / HW 文档 / SW 镜像 / 网表 四方一致)")
        return 0
    print("❌ ISS-234 关机语义门禁: %d 项不通过" % len(fails))
    for f in fails:
        print("   - %s" % f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
