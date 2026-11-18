#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_land_row_anchors.py —— ★★落表行号锚点守卫 (ISS-262 · hw-lead)★★

★★**为什么要有它 (★病灶, 实锤, 不是理论★)** ★:
  ★**`HW/check_netlist_selfconsistency.py` 的 `EXPECT` 表里的行号锚点, 在落表后会整段位移** ★
  (★V-3 删 3 行 `DEMO_DNP` ⇒ 表A/脚表 344 行之后全体 -3★)
  ⇒ ★**最阴的一种后果叫「假绿」: 锚点行号没改, 但那一行已经换了别的器件 ★**
  ⇒ ★**而门禁只查「内容对不对」(谓词), 不查「还是不是同一颗器件」⇒ 照样绿 ★**
  ⇒ ★**于是下一个按行号改东西的人 (人或 agent) 会改错行, 门禁不会喊 ★**

★★**本闸的判据 (★与任务书 §③① 的 1/2/3 逐条对应★)** ★:
  ① ★**落表前登记 (文件, 行号, 内容指纹) ⇒ 清单来源【机器可枚举】, 不许手抄** ★
     · 锚点清单 = ★**AST 解析 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 赋值** ★
       (★机器枚举: 从源码的 AST 里拿, 不是从人抄的表里拿★)
     · ★**交叉校验**: 同一份锚点表还必须逐字出现在 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md`
       的 `<!-- ANCHORS:BEGIN/END -->` 块里 (★两边不一致 ⇒ 红★)
     · ★**指纹 = 两层**: `id_fp` (★实体身份指纹★) + `full_fp` (★整行内容指纹★)
       (★身份指纹用「哪几列能唯一认出这颗器件」自动挑, 挑法是机器枚举出来的, 不是人拍的★)
  ② ★**落表后三种情形分开判 (★不许合并成一句「通过」★)** ★:
     · ★**行号没变 + 内容没变** ⇒ ✅ **通过** (PASS)
     · ★**行号变了 + 内容没变 (纯漂移)** ⇒ ⚠️ **必须报出来** (DRIFT)
       ⇒ ★**不许静默★** ⇒ ★**并且【锚点更新必须机器写】(★`--reanchor` 机器改行号, 不许人手改★)** ★
     · ★**行号变了 + 内容也变了** ⇒ ❌ **红** (RED)
       (★另加: 行号没变但**实体**被换了 ⇒ ❌ 红 —— 这就是「假绿」本体★)
  ③ ★**锚点更新必须机器写** ⇒ `--reanchor` 机器改:
       · `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 行号
       · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `ANCHORS` 块行号
       · ★**台账 `HW/land_row_anchors_registry.json`** ★
       · ★**并同步更新本脚本里的 `REGISTRY_SHA256` 常量 (★防台账被偷改★)** ★

★★**rc 语义 (★不制造假绿★)** ★:
  · `rc=0` ⇒ 全绿 (PASS, 无漂移, 无红)
  · `rc=1` ⇒ ★**有红 (RED)** ★ (★内容变了 / 实体消失 / 台账被偷改 / 源码⇄规格页不一致★)
  · `rc=3` ⇒ ★**只有纯漂移 (DRIFT)** ★ (★实体挪了行, 锚点行号没跟着改 ⇒ 假绿风险 ⇒ 必须 `--reanchor`★)
  · `rc=2` ⇒ 用法错 / 文件缺

用法:
  python3 HW/check_land_row_anchors.py                 # ★体检: 逐条判 + 汇总 (rc 见上★)
  python3 HW/check_land_row_anchors.py --strict        # ★同默认 (★DRIFT 也算红 ⇒ rc=1★)
  python3 HW/check_land_row_anchors.py --reanchor      # ★机器重锚 (★修 DRIFT, 并更新台账★)
  python3 HW/check_land_row_anchors.py --init-registry # ★机器建台账 (★只许在「重新基线」时用★)
  python3 HW/check_land_row_anchors.py --selftest      # ★反向用例 (≥6 条·全在临时副本里做·真盘零写入★)
  python3 HW/check_land_row_anchors.py --json          # ★机器读格式★

★★**零落表**: 本闸只读 + `--reanchor` 只改【行号锚点】, ★**不许碰 value/dnp/board/任何器件参数**★
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)

# ── 相对路径 (工程根相对) ──
REL_CHECK = os.path.join("HW", "check_netlist_selfconsistency.py")
REL_SPEC = os.path.join("HW", "NETLIST_SELF_CONSISTENCY_SPEC.md")
REL_REGISTRY = os.path.join("HW", "land_row_anchors_registry.json")
REL_SELF = os.path.join("HW", "check_land_row_anchors.py")
REL_GEN = os.path.join("state", "gen_netlist.py")
# ★★ISS-283 · B1: 落表台账 (★「合法落表改 net 名」的授权证据源★) ★★
REL_LEDGER = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")

TABLE_FILES = {
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom": os.path.join("HW", "BOM_v1.csv"),
}

# ★**身份列候选 (★按优先级挑「哪几列能唯一认出这颗器件」· 机器枚举出来的★)** ★
# ★第一层: 只认器件身份 (落表改 value/dnp/board/evidence 都不该误报) ★
# ★第二层: 加上那颗器件在网上的位置 (★当第一层不唯一时才用★) ★
IDENT_PRIORITY = {
    "netlist": [["ref"], ["ref", "net"], ["ref", "net", "node1", "node2"],
                ["ref", "net", "node1", "node2", "page"]],
    "pins": [["ref", "pin"], ["ref", "pin", "net"], ["ref", "pin", "page", "net"]],
    "bom": [["ref"], ["ref", "type"], ["ref", "type", "page"]],
}

# ★**台账防偷改常量 (★改台账必须同时改这里, 且要在交卷单里说明为什么改★)** ★
# ★格式: sha256(规范化台账正文)★ —— `--init-registry` / `--reanchor` 会机器同步它 ★
REGISTRY_SHA256 = "087cb3919fa667e1a4961d263ed25589cce9d5c9b6d047a4a9e15f0d07da0cd4"


# ═════════════════════════════════════════════════════════════════════════════
# 小工具
# ═════════════════════════════════════════════════════════════════════════════
def md5_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path: str, txt: str) -> None:
    tmp = path + ".tmp_iss262"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
    os.replace(tmp, path)


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ═════════════════════════════════════════════════════════════════════════════
# ① 锚点清单 (★机器可枚举: AST 解析 EXPECT 赋值★)
# ═════════════════════════════════════════════════════════════════════════════
def parse_expect_py(root: str) -> list[tuple[str, str, str, str]]:
    """★AST 解析 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 赋值 ⇒ 锚点清单★

    ★**机器可枚举**: 直接从源码 AST 里取, ★不许手抄、不许硬编码行号表★ ★
    """
    path = os.path.join(root, REL_CHECK)
    src = read_text(path)
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "EXPECT":
            val = ast.literal_eval(node.value)
            return [tuple(x) for x in val]
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", None) == "EXPECT":
                    val = ast.literal_eval(node.value)
                    return [tuple(x) for x in val]
    raise RuntimeError(f"★{REL_CHECK} 里找不到 EXPECT 赋值 (★结构变了?★)")


def parse_spec_md(root: str) -> dict[str, tuple[str, str, str]]:
    """★解析规格页 `<!-- ANCHORS:BEGIN/END -->` 块里的锚点表 (★交叉校验用★) ★"""
    path = os.path.join(root, REL_SPEC)
    txt = read_text(path)
    m = re.search(r"<!-- ANCHORS:BEGIN -->\n(.*?)\n<!-- ANCHORS:END -->", txt, re.S)
    if not m:
        raise RuntimeError(f"★{REL_SPEC} 里找不到 ANCHORS 块 (★结构变了?★)")
    out: dict[str, tuple[str, str, str]] = {}
    for line in m.group(1).split("\n"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        key, f, ln, chk = cells[0], cells[1], cells[2], "|".join(cells[3:])
        if key in ("key", "---") or set(key) <= {"-"}:
            continue
        out[key] = (f, ln, chk)
    return out


# ═════════════════════════════════════════════════════════════════════════════
# ①B 源码行锚点 (★state/gen_netlist.py 的 add() 调用·★这才是 V-3 真正漂的那对行号★)
# ═════════════════════════════════════════════════════════════════════════════
def parse_gen_calls(root: str) -> list[dict]:
    """★AST 枚举 `state/gen_netlist.py` 里所有 `add(...)` 调用 ⇒ 源码行锚点★

    ★**为什么必须有这一层** ★:
      ★**V-3=E 删的是 `state/gen_netlist.py` 的 `DEMO_DNP` 字典 3 个条目 (L348 一带)** ★
      ⇒ ★**gen_netlist.py 里 L348 之后的所有行号整体 -3** ★
      ⇒ ★**F1 那对锚点 (L381 / L393 一带) 真的漂 ★**
      ⇒ ★**而【网表 CSV】的行数不变 (★ISS-230 实测: 表A 513 行不变 / 脚表 584 行不变 / BOM 218 行不变★)** ★
      ⇒ ★**所以“行号漂移撞车 1 处”落在【生成器源码行号】上, 不在 CSV 行号上** ★

    ★**身份签名 = (page, ref, type, 同键序号)** ★:
      · ★**只用 page/ref/type + 序号 ⇒ 落表改 value/note/dnp/evidence 不影响身份 (不误报)** ★
      · ★**不用 net/node ⇒ V-2 把网名从 USB_D_P_SRC 改成 NET_USB_D_P_TYPEC 也不影响身份 (不误报)** ★
      · ★**序号 = 同 (page,ref,type) 的第几个 add() ⇒ 唯一可定位** ★
    """
    path = os.path.join(root, REL_GEN)
    tree = ast.parse(read_text(path))
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "add"]
    calls.sort(key=lambda n: n.lineno)
    counter: dict[tuple, int] = {}
    out: list[dict] = []
    for n in calls:
        def lit(i: int) -> str:
            if i >= len(n.args):
                return "?"
            a = n.args[i]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                return a.value
            try:
                return "?" + ast.dump(a)
            except Exception:
                return "?"
        key = (lit(0), lit(2), lit(6))
        ordn = counter.get(key, 0)
        counter[key] = ordn + 1
        sig = md5_text("|".join([key[0], key[1], key[2], str(ordn)]))
        out.append({"sig": sig, "line": n.lineno, "page": key[0], "ref": key[1],
                    "type": key[2], "ord": ordn})
    return out


# ═════════════════════════════════════════════════════════════════════════════
# ② 表格读取 (★行号口径必须与 check_netlist_selfconsistency.py 完全一致★)
# ═════════════════════════════════════════════════════════════════════════════
def read_table(root: str, table: str) -> list[dict]:
    """★读 CSV ⇒ 带 `_line` 的行字典 (★口径 = 现状守卫那套: 表头 = 第 1 行★)★"""
    path = os.path.join(root, TABLE_FILES[table])
    raw = read_text(path)
    rows = list(csv.reader(raw.split("\n")))
    while rows and rows[-1] == []:
        rows.pop()
    if not rows:
        raise RuntimeError(f"★空文件: {TABLE_FILES[table]}")
    head = rows[0]
    out = []
    for i, r in enumerate(rows[1:]):
        if len(r) != len(head):
            r = r + [""] * (len(head) - len(r))
        d = dict(zip(head, r))
        d["_line"] = i + 2
        out.append(d)
    return out


def row_full_fp(row: dict) -> str:
    """★整行内容指纹 (★不含 `_line` ⇒ 行号变了内容指纹不变★)★"""
    body = {k: v for k, v in row.items() if k != "_line"}
    return md5_text(canon(body))


def row_id_fp(row: dict, cols: list[str]) -> str:
    """★实体身份指纹 (★只用身份列 ⇒ 改 value/dnp/board 不会误报★)★"""
    return md5_text("|".join((row.get(c, "") or "").strip() for c in cols))


def pick_ident_cols(rows: list[dict], table: str) -> dict[str, list[str]]:
    """★给每行挑「能唯一认出它」的身份列 (★机器枚举, 不是人拍的★)★

    ★做法: 对候选列组合逐个试, 取**第一个让该行在全表里唯一**的组合 ★
    ⇒ 落表改 value/dnp/board 不影响身份 ⇒ 不误报; ★换了器件一定被抓★ ★
    """
    chosen: dict[str, list[str]] = {}
    for row in rows:
        line = str(row["_line"])
        for cand in IDENT_PRIORITY[table]:
            fp = row_id_fp(row, cand)
            hits = sum(1 for r in rows if row_id_fp(r, cand) == fp)
            if hits == 1:
                chosen[line] = cand
                break
        else:
            chosen[line] = IDENT_PRIORITY[table][-1]   # ★兜底: 用最长的那组★
    return chosen


# ═════════════════════════════════════════════════════════════════════════════
# ③-B 落表授权通道 (★ISS-283 · B1 · 「合法落表改 net 名」⇒ 守卫认得的一条合法通道★)
# ═════════════════════════════════════════════════════════════════════════════
# ★**为什么必须有它 (★病灶, 不是理论★)**:
#   V-2 (A3=1) 的落表动作 = 把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC`
#   ⇒ ★**这改的是守卫的【实体身份 (ref + net)】** ⇒ 守卫判「器件被换/被删」⇒ RED ⇒ 落表器自回滚
#   ⇒ ★**不是落表内容错, 是【落表器 ↔ 行号锚点守卫】两个工具的接口没接上** ★
#
# ★★**合法通道的三条硬规矩 (★一条都不许破★)** ★:
#   ① ★**判据必须是【可机器查的授权证据】** ⇒ 落表台账里能查到 (落表单号 + 文件名 + 旧身份 + 新身份)
#      ⇒ ★**查不到 ⇒ 仍 RED** ★
#   ② ★**不许把 RED 改成静默 PASS** ⇒ 合法通道必须留痕 (registry 里记「本次身份变更由哪个单号授权」)
#      ⇒ ★**台账被偷改 ⇒ 仍 RED** (★`REGISTRY_SHA256` 防偷改那条不许动★) ★
#   ③ ★**不许放宽 fail-closed** (链头不唯一 / 链断 / 链头无单号 ⇒ 仍红) ★
#   ④ ★**只许改「网名/位置」不许换器件** (★ref 必须不变·否则授权也救不了「器件被换」★) ★
AUTH_BLOCK_RE = re.compile(r"<!--\s*LANDING_AUTH:BEGIN\s*-->(.*?)<!--\s*LANDING_AUTH:END\s*-->", re.S)
ISSUE_RE = re.compile(r"ISS-\d+")


def row_id_vals(row: dict, cols: list[str]) -> list[str]:
    """★实体身份的值列表 (★与 `row_id_fp` 同源·只是不哈希 ⇒ 人可读 + 台账可登记★)"""
    return [(row.get(c, "") or "").strip() for c in cols]


def parse_landing_auths(root: str) -> list[dict]:
    """★抽落表台账里的【身份变更授权记录】 ⇒ [{issue, file, table, line, old, new, date, cred, ledger_line}] ★

    ★**口径 (★机器可查★)**: 台账里 `<!-- LANDING_AUTH:BEGIN -->` … `<!-- LANDING_AUTH:END -->` 之间的表格行 ★
      `| 单号 | 文件 | 表 | 行号 | 旧身份 | 新身份 | 日期 | 凭据 |`
      · 旧身份 / 新身份 = JSON 数组 (★身份列的值·按台账登记的顺序★) ⇒ 例 `["D_ESD_USB_D","USB_D_P_SRC"]` ★
    ★**四项不齐 (单号 / 文件 / 旧身份 / 新身份 任一缺) ⇒ 这条记录不算授权** (★判红·不许猜★) ★
    """
    out: list[dict] = []
    p = os.path.join(root, REL_LEDGER)
    if not os.path.exists(p):
        return out
    in_block = False
    for i, raw in enumerate(read_text(p).split("\n"), 1):
        s = raw.strip()
        if "LANDING_AUTH:BEGIN" in s:
            in_block = True
            continue
        if "LANDING_AUTH:END" in s:
            in_block = False
            continue
        if not in_block or not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 8:
            continue
        if set(cells[0]) <= {"-"} or not cells[0]:
            continue
        if cells[0] in ("单号", "issue", "Issue"):
            continue
        rec = {"issue": cells[0], "file": cells[1].strip().strip("`"),
               "table": cells[2], "line": cells[3],
               "old_raw": cells[4], "new_raw": cells[5],
               "date": cells[6], "cred": cells[7], "ledger_line": i}
        try:
            rec["old"] = json.loads(rec["old_raw"])
            rec["new"] = json.loads(rec["new_raw"])
            if not isinstance(rec["old"], list) or not isinstance(rec["new"], list):
                raise ValueError("身份必须写成 JSON 数组")
        except Exception:
            rec["old"] = None
            rec["new"] = None
        out.append(rec)
    return out


def ledger_issue_set(root: str) -> set[str]:
    """★落表台账里【授权块之外】出现过的单号 (★授权记录自己的单号不算数·要在台账别处能查到★)"""
    out: set[str] = set()
    p = os.path.join(root, REL_LEDGER)
    if not os.path.exists(p):
        return out
    in_block = False
    for raw in read_text(p).split("\n"):
        s = raw.strip()
        if "LANDING_AUTH:BEGIN" in s:
            in_block = True
            continue
        if "LANDING_AUTH:END" in s:
            in_block = False
            continue
        if in_block:
            continue
        if s.startswith("#") or s.startswith("|"):
            out.update(ISSUE_RE.findall(s))
    return out


def reg_id_vals(base: dict, rows: list[dict], cols: list[str]) -> list | None:
    """★台账里那条锚点的【旧身份值列表】 (★优先读 registry 的 `id_str`·否则按行号回查★)"""
    v = base.get("id_str")
    if isinstance(v, list) and v:
        return [str(x) for x in v]
    line = int(base.get("line", -1))
    for r in rows:
        if r["_line"] == line and row_id_fp(r, cols) == base.get("id_fp"):
            return row_id_vals(r, cols)
    return None


def find_auth(auths: list[dict], table: str, file_rel: str, old_vals: list | None,
              new_vals: list, reg_line: int, cols: list[str], issues: set[str]):
    """★找「这一次身份变更」的授权记录 ⇒ (状态, 记录, 说明) ★

    ★**状态**: `OK` (四项齐全 + 单号可查 + 行号对得上 + ref 没变 ⇒ 放行) ★
      `NONE` (压根没有这条记录 ⇒ 走原来的 RED 逻辑) ★
      其它 (⇒ **判红**·并把为什么不成立写进消息里★) ★
    """
    if old_vals is None:
        return ("NOOLD", None, "★台账里查不到这一行的旧身份 (registry 没登记 `id_str` 且按行号回查不到) ⇒ 不许放行★")
    cands = [a for a in auths
             if a["table"] == table and a["file"] == file_rel
             and a["old"] == old_vals and a["new"] == new_vals]
    if not cands:
        return ("NONE", None, "")
    if len(cands) > 1:
        return ("AMBIG", cands[0],
                f"★授权记录不唯一 (台账 L{cands[0]['ledger_line']} 等 {len(cands)} 条) ⇒ 取不准 ⇒ **红**★")
    a = cands[0]
    miss = [k for k in ("issue", "file", "old", "new")
            if not a[k] or a[k] == [] or a[k] is None]
    if miss:
        return ("INCOMPLETE", a,
                f"★授权记录四项不齐 (缺 {', '.join(miss)}) ⇒ 台账 L{a['ledger_line']} ⇒ **红**★")
    if a["issue"] not in issues:
        return ("NOISSUE", a,
                f"★授权记录的单号 `{a['issue']}` 在落表台账里查不到 (授权块之外没有) ⇒ 台账 L{a['ledger_line']} ⇒ **红**★")
    if str(a["line"]).strip() != str(reg_line):
        return ("BADLINE", a,
                f"★授权记录的行号 {a['line']} ≠ 台账登记的行号 {reg_line} ⇒ 台账 L{a['ledger_line']} ⇒ **红**★")
    ridx = cols.index("ref") if "ref" in cols else 0
    if a["old"][ridx] != a["new"][ridx]:
        return ("REFCHG", a,
                f"★授权记录把器件换了 (ref {a['old'][ridx]} → {a['new'][ridx]}) ⇒ "
                f"★合法通道只许改 net/位置·不许换器件★ ⇒ **红**★")
    return ("OK", a, "")


# ═════════════════════════════════════════════════════════════════════════════
# ③ 台账 (★机器写 + 防偷改★)
# ═════════════════════════════════════════════════════════════════════════════
def registry_path(root: str) -> str:
    return os.path.join(root, REL_REGISTRY)


def registry_canon(reg: dict) -> str:
    """★台账规范化正文 (★只含 anchors, 不含生成时间 ⇒ 同内容 ⇒ 同 sha★)★"""
    return canon(reg.get("anchors", {}))


def registry_sha(reg: dict) -> str:
    return sha_text(registry_canon(reg))


def load_registry(root: str) -> dict:
    p = registry_path(root)
    if not os.path.exists(p):
        raise RuntimeError(f"★台账不存在: {REL_REGISTRY} ⇒ 先跑 `--init-registry`★")
    return json.loads(read_text(p))


def save_registry(root: str, reg: dict) -> None:
    write_text(registry_path(root), json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def sync_self_sha(root: str, sha: str) -> bool:
    """★机器同步本脚本里的 `REGISTRY_SHA256` 常量 (★防台账被偷改★)★"""
    p = os.path.join(root, REL_SELF)
    txt = read_text(p)
    new_txt, n = re.subn(r'^REGISTRY_SHA256 = "[0-9a-f]{64}"$',
                         f'REGISTRY_SHA256 = "{sha}"', txt, count=1, flags=re.M)
    if n != 1:
        raise RuntimeError("★本脚本里找不到 REGISTRY_SHA256 常量 (★结构变了?★)")
    if new_txt != txt:
        write_text(p, new_txt)
    return n == 1


def self_expected_sha(root: str) -> str:
    txt = read_text(os.path.join(root, REL_SELF))
    m = re.search(r'^REGISTRY_SHA256 = "([0-9a-f]{64})"$', txt, re.M)
    return m.group(1) if m else ""


# ═════════════════════════════════════════════════════════════════════════════
# ④ 判据 (★三种情形分开判★)
# ═════════════════════════════════════════════════════════════════════════════
class Finding:
    def __init__(self, kind: str, aid: str, table: str, decl: int, reg: int, msg: str):
        self.kind = kind        # "PASS" | "DRIFT" | "RED"
        self.aid = aid
        self.table = table
        self.decl = decl        # ★源码里现在写的行号★
        self.reg = reg          # ★台账里登记的行号★
        self.msg = msg
        self.auth = None        # ★ISS-283 B1: 若是「合法落表改身份」⇒ 这里记授权单号 + 台账行号★

    def as_dict(self) -> dict:
        return {"kind": self.kind, "id": self.aid, "table": self.table,
                "decl_line": self.decl, "reg_line": self.reg, "msg": self.msg}


def judge(root: str) -> tuple[list[Finding], dict]:
    """★逐条判 ⇒ (findings, 机器可读上下文)★"""
    reg = load_registry(root)
    findings: list[Finding] = []
    ctx: dict = {"registry": reg}

    # ── 0. 台账防偷改 ──
    want = self_expected_sha(root)
    got = registry_sha(reg)
    if want != got:
        findings.append(Finding("RED", "__registry__", "-", -1, -1,
                                f"★台账被改过 (本脚本登记 sha={want[:12]}… / 实际 sha={got[:12]}…) ⇒ "
                                f"★**不许为了凑绿改台账**★ ⇒ 只有「落表那一趟显式重新基线」才允许, 且必须在交卷单说明★"))

    # ── 1. 锚点清单 (机器枚举) ──
    expect = parse_expect_py(root)
    spec = parse_spec_md(root)

    tables: dict[str, list[dict]] = {}
    idcols: dict[str, dict[str, list[str]]] = {}

    def tbl(t: str) -> list[dict]:
        if t not in tables:
            tables[t] = read_table(root, t)
            idcols[t] = pick_ident_cols(tables[t], t)
        return tables[t]

    # 源码 ⇄ 规格页 交叉校验
    for aid, (f, ln, chk) in spec.items():
        hit = next((e for e in expect if e[0] == aid), None)
        if hit is None:
            findings.append(Finding("RED", aid, f, -1, -1,
                                    "★规格页 ANCHORS 块里有这条, 但源码 EXPECT 里没有 ⇒ 两边漂了★"))
        elif (hit[1], hit[2], hit[3]) != (f, ln, chk):
            findings.append(Finding("RED", aid, f, -1, -1,
                                    f"★源码⇄规格页不一致: 源码 = {hit[1]}/{hit[2]} / 规格页 = {f}/{ln} ⇒ "
                                    f"★不许只改一边★"))
    for e in expect:
        if e[0] not in spec:
            findings.append(Finding("RED", e[0], e[1], -1, -1,
                                    "★源码 EXPECT 里有这条, 但规格页 ANCHORS 块里没有 ⇒ 两边漂了★"))

    anchors = reg.get("anchors", {})
    seen = set()

    # ── 0-bis 落表授权通道 (★ISS-283 · B1★) ──
    auths = parse_landing_auths(root)
    issues = ledger_issue_set(root)

    def auth_check(base: dict, rows: list[dict], cols: list[str], f: str,
                   reg_line: int, decl: int, cur: dict):
        """★「这次身份变更」有没有合法授权 ⇒ (放行?, 记录, 不成立的原因) ★

        ★**只覆盖【行号不变】的身份变更** (★挪行 + 改身份 ⇒ 判红·要人裁决★·不许机器放行★) ★
        """
        if decl != reg_line:
            return (False, None,
                    f"★这次身份变更同时挪了行 (台账行号 {reg_line} → 声明行号 {decl}) ⇒ "
                    f"★合法通道只覆盖【行号不变】的身份变更 ⇒ **红**★")
        reg_vals = reg_id_vals(base, rows, cols)
        state, rec, why = find_auth(auths, f, TABLE_FILES[f], reg_vals,
                                    row_id_vals(cur, cols), reg_line, cols, issues)
        if state == "OK":
            return (True, rec, "")
        if state == "NONE":
            return (False, None, "")      # ★压根没有授权记录 ⇒ 走原来的红★
        return (False, rec, why)

    for aid, f, ln, chk in expect:
        if f not in TABLE_FILES or not str(ln).isdigit():
            continue                      # ★"?" 与非表类锚点不管 (★它们不是行号锚点★)
        decl = int(ln)
        seen.add(aid)
        base = anchors.get(aid)
        if base is None:
            findings.append(Finding("RED", aid, f, decl, -1,
                                    "★台账里没有这条锚点的登记 ⇒ 跑 `--init-registry` 建台账★"))
            continue
        reg_line = int(base["line"])
        rows = tbl(f)
        by_line = {r["_line"]: r for r in rows}
        if decl not in by_line:
            findings.append(Finding("RED", aid, f, decl, reg_line,
                                    f"★锚点行号 {decl} 超出文件范围 (共 {len(rows)+1} 行) ⇒ 锚点指向了不存在的行★"))
            continue
        cur = by_line[decl]
        cols = base.get("idcols") or idcols[f][str(decl)]
        cur_id = row_id_fp(cur, cols)
        cur_full = row_full_fp(cur)
        reg_id = base["id_fp"]
        reg_full = base["full_fp"]

        if cur_id == reg_id:
            # ── 行号处的实体还是同一颗 ──
            if decl == reg_line:
                if cur_full == reg_full:
                    findings.append(Finding("PASS", aid, f, decl, reg_line, "★行号没变 + 内容没变 ⇒ 通过★"))
                else:
                    findings.append(Finding("PASS", aid, f, decl, reg_line,
                                            "★行号没变 + 实体没变, 但整行内容被就地改过 (落表改 value/dnp/board 属正常) ⇒ 记账通过★"))
            else:
                if cur_full == reg_full:
                    findings.append(Finding("DRIFT", aid, f, decl, reg_line,
                                            f"★行号变了 ({reg_line} → {decl}) + 实体内容没变 ⇒ 纯漂移 ⇒ "
                                            f"★已自动更新锚点行号 = {decl}★"))
                else:
                    findings.append(Finding("RED", aid, f, decl, reg_line,
                                            f"★行号变了 ({reg_line} → {decl}) + 内容也变了 ⇒ **红**: "
                                            f"★实体在挪行时被改了, 机器不许自动改 (要人/落表那一趟裁决★)"))
        else:
            # ── 行号处的实体换了 ⇒ 找它跑到哪去了 ──
            hits = [r for r in rows if row_id_fp(r, cols) == reg_id]
            if len(hits) == 0:
                # ★★ISS-283 · B1: 这本来要判红 ⇒ 先问「这次身份变更有没有合法授权」★★
                ok_auth, auth_rec, auth_why = auth_check(base, rows, cols, f, reg_line, decl, cur)
                if ok_auth:
                    fnd = Finding("PASS", aid, f, decl, reg_line,
                                  f"★合法落表改身份 ⇒ 授权单号 {auth_rec['issue']} "
                                  f"(落表台账 L{auth_rec['ledger_line']}) ⇒ 放行 + 同步 registry★")
                    fnd.auth = {"issue": auth_rec["issue"], "ledger_line": auth_rec["ledger_line"],
                                "old": auth_rec["old"], "new": auth_rec["new"]}
                    findings.append(fnd)
                    ctx.setdefault("auth_sync", []).append({
                        "aid": aid, "file": f, "decl": decl, "reg_line": reg_line,
                        "rec": auth_rec, "new_vals": row_id_vals(cur, cols),
                        "new_id": cur_id, "new_full": cur_full})
                elif auth_why:
                    findings.append(Finding("RED", aid, f, decl, reg_line,
                                            f"★实体身份变了, 但台账授权不成立 ⇒ {auth_why} ⇒ **红**★"))
                else:
                    findings.append(Finding("RED", aid, f, decl, reg_line,
                                            f"★行号没变 + 实体内容变了 (台账里那颗器件在本表里找不到了) ⇒ "
                                            f"**红**: 器件被换/被删, 锚点已指向别的行★"))
            elif len(hits) > 1:
                findings.append(Finding("RED", aid, f, decl, reg_line,
                                        f"★实体不唯一 (本表里 {len(hits)} 行同身份) ⇒ 无法自动定位 ⇒ **红**★"))
            else:
                moved = hits[0]["_line"]
                m_full = row_full_fp(hits[0])
                if m_full == reg_full:
                    findings.append(Finding("DRIFT", aid, f, decl, reg_line,
                                            f"★行号变了 ({reg_line} → {moved}) + 内容没变 ⇒ 纯漂移 ⇒ "
                                            f"★已自动更新锚点行号 = {moved}★"))
                else:
                    ok_auth, auth_rec, auth_why = auth_check(base, rows, cols, f, reg_line, decl, cur)
                    if ok_auth:
                        fnd = Finding("PASS", aid, f, decl, reg_line,
                                      f"★合法落表改身份 ⇒ 授权单号 {auth_rec['issue']} "
                                      f"(落表台账 L{auth_rec['ledger_line']}) ⇒ 放行 + 同步 registry★")
                        fnd.auth = {"issue": auth_rec["issue"], "ledger_line": auth_rec["ledger_line"],
                                    "old": auth_rec["old"], "new": auth_rec["new"]}
                        findings.append(fnd)
                        ctx.setdefault("auth_sync", []).append({
                            "aid": aid, "file": f, "decl": decl, "reg_line": reg_line,
                            "rec": auth_rec, "new_vals": row_id_vals(cur, cols),
                            "new_id": cur_id, "new_full": cur_full})
                    elif auth_why:
                        findings.append(Finding("RED", aid, f, decl, reg_line,
                                                f"★实体身份变了, 但台账授权不成立 ⇒ {auth_why} ⇒ **红**★"))
                    else:
                        findings.append(Finding("RED", aid, f, decl, reg_line,
                                                f"★行号变了 ({reg_line} → {moved}) + 内容也变了 ⇒ **红**: "
                                                f"★实体被替换, 机器不许自动改 (要人/落表那一趟裁决★)"))

    for aid in sorted(set(anchors) - seen):
        if anchors[aid].get("kind") == "gen_call":
            continue                      # ★源码行锚点由下一段单独判★
        findings.append(Finding("RED", aid, anchors[aid].get("table", "-"), -1,
                                int(anchors[aid].get("line", -1)),
                                "★台账里有这条锚点, 但源码 EXPECT 里已经没有了 ⇒ 锚点被删/被改名★"))

    # ── ② 源码行锚点 (★state/gen_netlist.py 的 add() 调用★) ──
    if os.path.exists(os.path.join(root, REL_GEN)):
        gcalls = {c["sig"]: c for c in parse_gen_calls(root)}
        for aid, base in sorted(anchors.items()):
            if base.get("kind") != "gen_call":
                continue
            seen.add(aid)
            cur = gcalls.get(base["sig"])
            if cur is None:
                findings.append(Finding("RED", aid, "gen", -1, int(base["line"]),
                                        "★生成器里这个 add() 调用找不到了 (★被删/被改签名★) ⇒ **红**★"))
            elif cur["line"] != int(base["line"]):
                findings.append(Finding("DRIFT", aid, "gen", cur["line"], int(base["line"]),
                                        f"★行号变了 ({base['line']} → {cur['line']}) + 调用签名没变 ⇒ "
                                        f"纯漂移 ⇒ ★已自动更新锚点行号 = {cur['line']}★"))
            else:
                findings.append(Finding("PASS", aid, "gen", cur["line"], int(base["line"]),
                                        "★行号没变 + 签名没变 ⇒ 通过★"))

    ctx["expect"] = expect
    ctx["tables"] = tables
    ctx["idcols"] = idcols
    return findings, ctx


# ═════════════════════════════════════════════════════════════════════════════
# ④-bis 机器补 `id_str` (★ISS-283 · B1 · 授权通道的【旧身份】来源★)
# ═════════════════════════════════════════════════════════════════════════════
def migrate_id_str(root: str, dry: bool = False) -> tuple[int, list[str]]:
    """★台账补 `id_str` (★实体身份值列表·★行号锚点守卫判【合法落表改 net 名】的旧身份来源★)

    ★★**为什么必须有它 (★2026-11-17 12:1x 实测到的坑·不是推测★)** ★★:
      守卫判「实体身份变了 (ref+net)」时, 要拿【旧身份】去落表台账的授权记录里比对
      (★合法落表那条通道的判据 = 单号 + 文件名 + 旧身份 + 新身份★)
      ⇒ 【旧身份】在盘上只有两个来源: ① registry 的 `id_str` ② 按行号回查
      (★② 的前提是「那一行现在还是原来那颗」★)
      ⇒ ★**落表已经把 net 改了 ⇒ ② 必然查不到 ⇒ ① 必须【提前】补齐★**
      ⇒ ★**不补 ⇒ 合法落表必判红 (NOOLD) ⇒ 落表器自回滚 ⇒ 合法落表这条路根本走不通★**
      (★2026-11-17 12:12 实测: A3 落表跑完就被这条判红 ⇒ 自动回滚了·实证★)

    ★**fail-closed (★不许猜★)**:
      · ★**只有「该行号处的实体还是原来那颗」(`row_id_fp` 相同)才补** ⇒
        身份已经变了的那一条【不补】⇒ 要人裁决 ⇒ 不许机器替它编一个旧身份★
      · ★**`kind == "gen_call"` 的源码行锚点不补** (★它们靠调用签名匹配·没有身份值列表★)
      · ★**幂等**: 已有 `id_str` 的条目一律不碰 ★
      · ★**台账只许机器写** ⇒ 写完同步本脚本的 `REGISTRY_SHA256` (★防偷改那条不许动★)★
    """
    reg = load_registry(root)
    tables: dict[str, list] = {}
    for t in TABLE_FILES:
        try:
            tables[t] = read_table(root, t)
        except Exception:
            pass
    n = 0
    skipped = 0
    for aid, base in sorted((reg.get("anchors") or {}).items()):
        if base.get("kind") == "gen_call":
            continue
        if base.get("id_str"):
            continue
        t = base.get("table")
        if t not in tables:
            continue
        cols = base.get("idcols") or []
        if not cols:
            continue
        try:
            line = int(base.get("line", -1))
        except Exception:
            continue
        row = next((r for r in tables[t] if r["_line"] == line), None)
        if row is None or row_id_fp(row, cols) != base.get("id_fp"):
            skipped += 1            # ★身份已经不是原来那颗 ⇒ 不许补 (要人裁决)★
            continue
        base["id_str"] = row_id_vals(row, cols)
        reg["anchors"][aid] = base
        n += 1
    msgs: list[str] = []
    if n and not dry:
        save_registry(root, reg)
        sync_self_sha(root, registry_sha(reg))
        msgs.append(f"★台账补 `id_str` (实体身份值列表): {n} 条 ⇒ 已更新 `{REL_REGISTRY}` "
                    f"+ 同步本脚本 `REGISTRY_SHA256`")
    elif n:
        msgs.append(f"★台账补 `id_str`: {n} 条 (★干跑·未写盘★)")
    else:
        msgs.append("★台账 `id_str` 已是最新 (★无需补★)")
    if skipped:
        msgs.append(f"★有 {skipped} 条【身份已不是原来那颗】⇒ 不补 `id_str` "
                    f"(★fail-closed·要人裁决·不许机器猜★)")
    return 0, msgs


# ═════════════════════════════════════════════════════════════════════════════
# ⑤ 机器重锚 (★锚点更新必须机器写★)
# ═════════════════════════════════════════════════════════════════════════════
def reanchor(root: str, dry: bool = False) -> tuple[int, list[str]]:
    """★把纯漂移的锚点行号机器改对 (★改 .py EXPECT + 规格页 ANCHORS 块 + 台账★)★"""
    findings, ctx = judge(root)
    reg = load_registry(root)
    drift = [f for f in findings if f.kind == "DRIFT"]
    auth_sync = ctx.get("auth_sync", [])
    if not drift and not auth_sync:
        # ★★ISS-283 · B1: 没有漂移也【必须】把台账的 `id_str` 补齐 ★★
        #   (★`id_str` = 实体身份值列表 ⇒ 【合法落表改 net 名】的旧身份来源·守卫要靠它比对★)
        #   ★★**不补 ⇒ 下一次落表改了身份 ⇒ 守卫查不到旧身份 ⇒ 判红 ⇒ 落表器自回滚 ⇒
        #      合法落表这条路走不通 (★2026-11-17 12:12 实测过的坑★)★★
        return migrate_id_str(root, dry=dry)

    expect = ctx["expect"]
    tables = ctx["tables"]
    idcols = ctx["idcols"]
    anchors = reg["anchors"]

    # ── 算每个漂移锚点的新行号 ──
    new_line: dict[str, int] = {}
    for f in drift:
        aid, tblname = f.aid, f.table
        base = anchors[aid]
        if base.get("kind") == "gen_call":
            continue                      # ★源码行锚点的重锚在台账刷新那一步做★
        cols = base.get("idcols") or idcols[tblname][str(base["line"])]
        rows = tables[tblname]
        # 新行号 = 实体现在的行号 (★优先「声明行号处的实体就是它」, 否则按身份找★)
        by_line = {r["_line"]: r for r in rows}
        if f.decl in by_line and row_id_fp(by_line[f.decl], cols) == base["id_fp"]:
            new_line[aid] = f.decl
        else:
            hits = [r for r in rows if row_id_fp(r, cols) == base["id_fp"]]
            if len(hits) == 1:
                new_line[aid] = hits[0]["_line"]

    if not new_line and not auth_sync:
        # ★只有源码行锚点漂了 (★表行一条没漂★) ⇒ 照样能机器重锚 (台账刷新那一步做)★
        if not any(f.table == "gen" for f in drift):
            return 1, ["★有漂移, 但没有一个能唯一定位 ⇒ 不许自动改★"]

    msgs = []
    # ── ① 改 .py EXPECT ──
    path = os.path.join(root, REL_CHECK)
    txt = read_text(path)
    n_changed = 0
    for aid, nl in sorted(new_line.items()):
        pat = re.compile(r"^(\s*\(\s*['\"]" + re.escape(aid) + r"['\"]\s*,\s*['\"][a-z]+['\"]\s*,\s*['\"])(\d+)(['\"]\s*,.*)$", re.M)
        txt, n = pat.subn(lambda m: m.group(1) + str(nl) + m.group(3), txt, count=1)
        n_changed += n
    if n_changed and not dry:
        write_text(path, txt)
    msgs.append(f"★改 `HW/check_netlist_selfconsistency.py` 的 EXPECT 行号: {n_changed} 条")

    # ── ② 改规格页 ANCHORS 块 ──
    spath = os.path.join(root, REL_SPEC)
    stxt = read_text(spath)
    n_spec = 0
    for aid, nl in sorted(new_line.items()):
        m = re.search(r"<!-- ANCHORS:BEGIN -->\n(.*?)\n<!-- ANCHORS:END -->", stxt, re.S)
        if not m:
            break
        block = m.group(1)
        pat = re.compile(r"^(\|\s*" + re.escape(aid) + r"\s*\|\s*[a-z]+\s*\|\s*)(\d+)(.*)$", re.M)
        block2, n = pat.subn(lambda mm: mm.group(1) + str(nl) + mm.group(3), block, count=1)
        n_spec += n
        stxt = stxt[:m.start(1)] + block2 + stxt[m.end(1):]
    if n_spec and not dry:
        write_text(spath, stxt)
    msgs.append(f"★改 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 ANCHORS 块行号: {n_spec} 条")

    # ── ③ 改台账 (★漂移的行号 + 落表改过的整行内容指纹 ⇒ 一起重基线★) ──
    if not dry:
        red_ids = {f.aid for f in findings if f.kind == "RED"}
        auth_aids = {s["aid"] for s in auth_sync}
        # ── ③-0 迁移: 补 `id_str` (★身份值列表·ISS-283 B1 的授权通道要靠它★) ──
        n_mig = 0
        for aid, base in sorted(anchors.items()):
            if base.get("kind") == "gen_call" or base.get("id_str"):
                continue
            tblname = base.get("table")
            if tblname not in tables:
                continue
            cols0 = base.get("idcols") or idcols[tblname].get(str(base["line"]))
            if not cols0:
                continue
            vals = reg_id_vals(base, tables[tblname], cols0)
            if vals:
                base["id_str"] = vals
                anchors[aid] = base
                n_mig += 1
        if n_mig:
            msgs.append(f"★台账补 `id_str` (身份值列表): {n_mig} 条")
        for aid, base in sorted(anchors.items()):
            if aid in red_ids or aid in auth_aids:
                continue                      # ★红的条目不许自动改 (要人裁决)★ / ★授权通道的条目走下面那条路★
            if base.get("kind") == "gen_call":
                gcalls2 = {c["sig"]: c for c in parse_gen_calls(root)}
                cur2 = gcalls2.get(base["sig"])
                if cur2 is not None:
                    base["line"] = cur2["line"]
                    anchors[aid] = base
                continue
            tblname = base["table"]
            cols = base.get("idcols") or idcols[tblname][str(base["line"])]
            rows = tables[tblname]
            hits = [r for r in rows if row_id_fp(r, cols) == base["id_fp"]]
            if len(hits) == 1:
                base["line"] = hits[0]["_line"]
                base["full_fp"] = row_full_fp(hits[0])
                base["id_str"] = row_id_vals(hits[0], cols)
                anchors[aid] = base
        # ── ③-bis 合法落表改身份 ⇒ 同步 registry 的身份指纹 (★ISS-283 · B1★) ──
        for s in auth_sync:
            aid = s["aid"]
            base = anchors.get(aid)
            if base is None:
                continue
            base["line"] = s["decl"]
            base["id_fp"] = s["new_id"]
            base["full_fp"] = s["new_full"]
            base["id_str"] = s["new_vals"]
            base["auth"] = {"issue": s["rec"]["issue"],
                            "ledger_line": s["rec"]["ledger_line"],
                            "date": s["rec"]["date"],
                            "cred": s["rec"]["cred"],
                            "old": s["rec"]["old"],
                            "new": s["rec"]["new"],
                            "note": "★合法落表改身份 (ISS-283 · B1 授权通道)★"}
            anchors[aid] = base
            msgs.append(f"★授权同步: {aid} ({s['file']}) L{s['reg_line']} ⇒ 身份 "
                        f"{s['rec']['old']} → {s['new_vals']} (★单号 {s['rec']['issue']} · 台账 L{s['rec']['ledger_line']}★)")
        reg["anchors"] = anchors
        reg["note"] = ("★机器写 (ISS-262 · HW/check_land_row_anchors.py --reanchor)★ "
                       "★每条 = {id, table, line, id_fp(实体身份), full_fp(整行内容), idcols(身份列), "
                       "id_str(身份值列表·ISS-283 B1 授权通道用) }★")
        save_registry(root, reg)
        sync_self_sha(root, registry_sha(reg))
        msgs.append(f"★更新台账 `{REL_REGISTRY}` + 同步本脚本 `REGISTRY_SHA256`")

    msgs.insert(0, f"★★【纯漂移 {len(drift)} 条 ⇒ 机器已重锚】★★")
    for f in drift:
        msgs.append(f"   ⚠️ {f.aid} ({f.table}): 行号 {f.reg} → {new_line.get(f.aid, '?')} · {f.msg}")
    return 0, msgs


# ═════════════════════════════════════════════════════════════════════════════
# ⑥ 建台账 (★--init-registry★)
# ═════════════════════════════════════════════════════════════════════════════
def init_registry(root: str) -> int:
    expect = parse_expect_py(root)
    tables: dict[str, list[dict]] = {}
    idcols: dict[str, dict[str, list[str]]] = {}

    def tbl(t: str) -> list[dict]:
        if t not in tables:
            tables[t] = read_table(root, t)
            idcols[t] = pick_ident_cols(tables[t], t)
        return tables[t]

    anchors: dict[str, dict] = {}
    for aid, f, ln, chk in expect:
        if f not in TABLE_FILES or not str(ln).isdigit():
            continue
        rows = tbl(f)
        by_line = {r["_line"]: r for r in rows}
        line = int(ln)
        if line not in by_line:
            print(f"★★ rc=1: 锚点 {aid} 的行号 {line} 不在 {f} 里 ⇒ 台账建不了★", file=sys.stderr)
            return 1
        row = by_line[line]
        cols = idcols[f][str(line)]
        anchors[aid] = {
            "table": f,
            "file": TABLE_FILES[f],
            "line": line,
            "idcols": cols,
            "id_fp": row_id_fp(row, cols),
            "full_fp": row_full_fp(row),
            "id_str": row_id_vals(row, cols),
        }
    # ★源码行锚点 (gen_netlist.py 的 add() 调用) ★
    n_gen = 0
    for c in parse_gen_calls(root):
        aid = "gen_" + c["sig"][:10] + "_" + str(c["ord"])
        anchors[aid] = {
            "kind": "gen_call",
            "table": "gen",
            "file": REL_GEN,
            "line": c["line"],
            "sig": c["sig"],
            "page": c["page"],
            "ref": c["ref"],
            "type": c["type"],
            "ord": c["ord"],
        }
        n_gen += 1
    reg = {
        "schema": 1,
        "note": ("★机器写 (ISS-262 · HW/check_land_row_anchors.py --init-registry)★ "
                 "★每条 = {id, table, line, id_fp(实体身份), full_fp(整行内容), idcols(身份列) }★"),
        "anchor_count": len(anchors),
        "anchors": anchors,
    }
    save_registry(root, reg)
    sync_self_sha(root, registry_sha(reg))
    print(f"★★ 台账已建: {REL_REGISTRY} · {len(anchors)} 条行号锚点 (★表行 {len(anchors)-n_gen} 条 + 源码行 {n_gen} 条★)")
    print(f"★★ 已同步 `{REL_SELF}` 的 REGISTRY_SHA256 = {registry_sha(reg)}")
    return 0


# ═════════════════════════════════════════════════════════════════════════════
# ⑦ 打印 / 汇总
# ═════════════════════════════════════════════════════════════════════════════
def report(root: str, findings: list[Finding]) -> int:
    npass = sum(1 for f in findings if f.kind == "PASS")
    ndrift = sum(1 for f in findings if f.kind == "DRIFT")
    nred = sum(1 for f in findings if f.kind == "RED")
    print("╔══ 落表行号锚点守卫 (ISS-262) ══╗")
    print(f"★ 工程根: {root}")
    print(f"★ 锚点条数: {len(findings)}  (PASS={npass} · DRIFT={ndrift} · RED={nred})")
    if ndrift:
        print("")
        print("★★【⚠️ 纯漂移 (行号变了 · 实体内容没变) ⇒ 假绿风险 ⇒ 必须机器重锚】★★")
        for f in findings:
            if f.kind == "DRIFT":
                print(f"   ⚠️ {f.aid} [{f.table}] 行号 {f.reg} → {f.decl} · {f.msg}")
    if nred:
        print("")
        print("★★【❌ 红 (内容变了 / 实体没了 / 台账被改 / 两边漂了)】★★")
        for f in findings:
            if f.kind == "RED":
                print(f"   ❌ {f.aid} [{f.table}] {f.msg}")
    auths = [f for f in findings if f.auth]
    if auths:
        print("")
        print("★★【🔑 合法落表改身份 (★ISS-283 B1 授权通道·已留痕★)】★★")
        for f in auths:
            print(f"   🔑 {f.aid} [{f.table}] {f.auth['old']} → {f.auth['new']} "
                  f"· 授权单号 {f.auth['issue']} · 落表台账 L{f.auth['ledger_line']}")
    if not ndrift and not nred:
        print("★ ✅ 全部锚点: 行号没变 + 实体没变 ⇒ 通过")
    return 0


def run_check(root: str, strict: bool = False) -> int:
    findings, _ = judge(root)
    rc = report(root, findings)
    ndrift = sum(1 for f in findings if f.kind == "DRIFT")
    nred = sum(1 for f in findings if f.kind == "RED")
    if nred:
        return 1
    if ndrift:
        return 1 if strict else 3
    return rc


# ═════════════════════════════════════════════════════════════════════════════
# ⑧ 反向用例 (★--selftest · ≥6 条 · 真盘零写入★)
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_FILES = [
    REL_CHECK,
    REL_SPEC,
    REL_REGISTRY,
    REL_SELF,
    REL_GEN,
    REL_LEDGER,
    TABLE_FILES["netlist"],
    TABLE_FILES["pins"],
    TABLE_FILES["bom"],
]


def make_sandbox(root: str) -> str:
    tmp = tempfile.mkdtemp(prefix="iss262_anchor_")
    for rel in FIXTURE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return tmp


def _csv_line_set(path: str, line: int, col: str, newval: str) -> None:
    """★把某个物理行的某一列改掉 (★按 CSV 解析后重写, 不做字符串硬替换★) ★"""
    lines = read_text(path).split("\n")
    head = next(csv.reader([lines[0]]))
    vals = next(csv.reader([lines[line - 1]]))
    if col not in head:
        raise RuntimeError(f"★列 {col} 不在表头里")
    vals[head.index(col)] = newval
    lines[line - 1] = ",".join('"' + v.replace('"', '""') + '"' if ("," in v or '"' in v)
                               else v for v in vals)
    write_text(path, "\n".join(lines))


def _bump_ref(tmp: str, table: str, line: int) -> None:
    _csv_line_set(os.path.join(tmp, TABLE_FILES[table]), line, "ref", "ISS262_REF_X")


def _bump_value(tmp: str, table: str, line: int) -> None:
    _csv_line_set(os.path.join(tmp, TABLE_FILES[table]), line, "value", "ISS262_VALUE_X")


def _swap_rows(tmp: str, table: str, a: int, b: int) -> None:
    p = os.path.join(tmp, TABLE_FILES[table])
    lines = read_text(p).split("\n")
    lines[a - 1], lines[b - 1] = lines[b - 1], lines[a - 1]
    write_text(p, "\n".join(lines))


def _set_expect_line(tmp: str, aid: str, table: str, newline: int) -> None:
    cp = os.path.join(tmp, REL_CHECK)
    ctxt = read_text(cp)
    pat = re.compile(r"^(\s*\(\s*['\"]" + re.escape(aid) + r"['\"]\s*,\s*['\"]"
                     + re.escape(table) + r"['\"]\s*,\s*['\"])(\d+)(['\"]\s*,.*)$", re.M)
    ctxt, n = pat.subn(lambda m: m.group(1) + str(newline) + m.group(3), ctxt, count=1)
    write_text(cp, ctxt)


# ── ★ISS-283 B1 · 落表授权通道 的反向用例工具 ★─
def _pick_net_anchor(tmp: str):
    """★挑一条【身份列含 net】的网表锚点 (★只有改 net 才会动身份★) ⇒ (aid, line, cols, old_vals)"""
    reg = load_registry(tmp)
    rows = read_table(tmp, "netlist")
    for aid, base in sorted(reg["anchors"].items()):
        if base.get("table") != "netlist":
            continue
        cols = base.get("idcols") or []
        if "net" not in cols:
            continue
        line = int(base["line"])
        row = next((r for r in rows if r["_line"] == line), None)
        if row is None:
            continue
        return aid, line, cols, row_id_vals(row, cols)
    raise RuntimeError("★沙盒里找不到身份列含 net 的网表锚点★")


def _bump_net(tmp: str, table: str, line: int, newnet: str) -> None:
    _csv_line_set(os.path.join(tmp, TABLE_FILES[table]), line, "net", newnet)


def _reg_migrate_id_str(tmp: str) -> None:
    """★沙盒里把 registry 的 `id_str` 补齐 (★按当前盘面行回填★)"""
    p = registry_path(tmp)
    reg = json.loads(read_text(p))
    tables = {t: read_table(tmp, t) for t in TABLE_FILES}
    for aid, base in sorted(reg["anchors"].items()):
        t = base.get("table")
        if t not in tables or base.get("id_str"):
            continue
        cols = base.get("idcols") or []
        row = next((r for r in tables[t] if r["_line"] == int(base["line"])), None)
        if row is None or row_id_fp(row, cols) != base.get("id_fp"):
            continue
        base["id_str"] = row_id_vals(row, cols)
    write_text(p, json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    sync_self_sha(tmp, registry_sha(reg))


def _reg_drop_id_str(tmp: str) -> None:
    """★沙盒里把 registry 的 `id_str` 全部抹掉 (★构造【旧身份查不到】的前提★)

    ★**为什么要有它 (★2026-11-17 12:1x 实测★)**: 沙盒是从真盘拷的 ⇒ 真盘的台账一旦补了 `id_str`,
      那些【前提是「台账里查不到旧身份」】的反向用例 (T16 / T18) 就会【前提不成立 ⇒ 假失败】★
      ⇒ ★**用例必须自己【造出】它要测的那个前提★ 不许依赖真盘状态★★
    """
    p = registry_path(tmp)
    reg = json.loads(read_text(p))
    for aid, base in sorted(reg["anchors"].items()):
        if "id_str" in base:
            del base["id_str"]
    write_text(p, json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    sync_self_sha(tmp, registry_sha(reg))


def _ledger_add_auth(path: str, rows: list[str], heading: str = "") -> None:
    txt = read_text(path) if os.path.exists(path) else ""
    block = ""
    if heading:
        block += heading.rstrip("\n") + "\n"
    block += ("<!-- LANDING_AUTH:BEGIN -->\n"
              "| 单号 | 文件 | 表 | 行号 | 旧身份 | 新身份 | 日期 | 凭据 |\n"
              "|---|---|---|---|---|---|---|---|\n")
    block += "\n".join(rows) + "\n<!-- LANDING_AUTH:END -->\n"
    write_text(path, txt.rstrip("\n") + "\n" + block)


def _auth_row(issue: str, rel: str, table: str, line: int, old: list, new: list,
              date: str = "2026-11-17", cred: str = "ISS283 自测凭据") -> str:
    return ("| %s | %s | %s | %d | %s | %s | %s | %s |"
            % (issue, rel, table, line,
               json.dumps(old, ensure_ascii=False), json.dumps(new, ensure_ascii=False),
               date, cred))


def sandbox_line_of(tmp: str, table: str, ref: str) -> int:
    """★沙盒里找某行 (按 ref 找第一行) 的行号★"""
    rows = read_table(tmp, table)
    for r in rows:
        if (r.get("ref") or "").strip() == ref:
            return int(r["_line"])
    raise RuntimeError(f"★沙盒里找不到 ref={ref}")


def selftest(root: str) -> int:
    cases: list[tuple[str, bool, str]] = []

    def case(name: str, ok: bool, detail: str = ""):
        cases.append((name, ok, detail))

    # ── 基准: 不改任何东西 ⇒ 必须全绿 ──
    tmp = make_sandbox(root)
    try:
        rc = run_check(tmp)
        case("T1 ★正向: 一条都没漂 ⇒ 必须绿 (rc=0)", rc == 0, f"rc={rc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T2: 纯漂移 (行号变 / 内容不变) ⇒ 必须被报出来 (DRIFT) ──
    tmp = make_sandbox(root)
    try:
        # 在网表表头后插 2 行垃圾 ⇒ 表内所有行整体 +2 ⇒ 实体挪行, 内容不变
        p = os.path.join(tmp, TABLE_FILES["netlist"])
        lines = read_text(p).split("\n")
        head = next(csv.reader([lines[0]]))
        dummies = []
        for tag in ("A", "B"):
            vals = [""] * len(head)
            vals[head.index("page")] = "P1"
            vals[head.index("net")] = f"ISS262_DUMMY_{tag}"
            vals[head.index("node1")] = f"ISS262_DUMMY_{tag}"
            vals[head.index("node2")] = f"ISS262_DUMMY_{tag}"
            vals[head.index("ref")] = f"ISS262_DUMMY_{tag}"
            vals[head.index("value")] = "ISS262_DUMMY"
            vals[head.index("type")] = "NET"
            vals[head.index("dnp")] = "必装"
            dummies.append(",".join(vals))
        lines = [lines[0]] + dummies + lines[1:]
        write_text(p, "\n".join(lines))
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        ndrift = sum(1 for f in findings if f.kind == "DRIFT")
        ok = (rc in (1, 3)) and ndrift > 0
        case("T2 ★反向: 纯漂移 (行号变 / 内容不变) ⇒ 必须被报出来", ok,
             f"rc={rc} · DRIFT={ndrift}")
        # ── T3: 机器重锚 ⇒ 改完再跑必须绿 ──
        rc2, msgs = reanchor(tmp)
        rc3 = run_check(tmp)
        findings3, _ = judge(tmp)
        ndrift3 = sum(1 for f in findings3 if f.kind == "DRIFT")
        nred3 = sum(1 for f in findings3 if f.kind == "RED")
        case("T3 ★反向: 纯漂移 ⇒ `--reanchor` 机器改完 ⇒ 必须重新变绿",
             rc2 == 0 and rc3 == 0 and ndrift3 == 0 and nred3 == 0,
             f"reanchor rc={rc2} · 复跑 rc={rc3} · DRIFT={ndrift3} · RED={nred3}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T4: 内容变 (行号不变) ⇒ 必须红 ──
    tmp = make_sandbox(root)
    try:
        reg = load_registry(tmp)
        aid, base = next((k, v) for k, v in sorted(reg["anchors"].items())
                          if v["table"] == "netlist")
        line = int(base["line"])
        # ★把该行的 ref 改掉 ⇒ 实体被换 ⇒ 行号没变 + 实体内容变了 ⇒ 红 ★
        _bump_ref(tmp, "netlist", line)
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        case("T4 ★反向: 内容变 (行号不变) ⇒ 必须红 (rc=1)", rc == 1 and nred > 0,
             f"rc={rc} · RED={nred} · 锚点={aid}@L{line}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T5: 行号 + 内容都变 ⇒ 必须红 ──
    tmp = make_sandbox(root)
    try:
        reg = load_registry(tmp)
        aid, base = next((k, v) for k, v in sorted(reg["anchors"].items())
                          if v["table"] == "netlist")
        line = int(base["line"])
        # ★① 把锚点行与下一行对调 ⇒ 实体挪到 line+1; ② 改它的 value ⇒ 内容也变;
        #   ③ 把 EXPECT 的行号改到 line+1 ⇒ 行号变了 + 内容也变了 ⇒ 必须红 ★
        _swap_rows(tmp, "netlist", line, line + 1)
        _bump_value(tmp, "netlist", line + 1)
        _set_expect_line(tmp, aid, "netlist", line + 1)
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T5 ★反向: 行号 + 内容都变 ⇒ 必须红 (rc=1)", rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 锚点={aid}@{line}→{line+1} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T6: 台账被偷改 ⇒ 必须红 ──
    tmp = make_sandbox(root)
    try:
        p = registry_path(tmp)
        reg = json.loads(read_text(p))
        first = sorted(reg["anchors"])[0]
        reg["anchors"][first]["line"] = int(reg["anchors"][first]["line"]) + 7
        write_text(p, json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        rc = run_check(tmp)
        case("T6 ★反向: 台账被偷改 ⇒ 必须红 (rc=1)", rc == 1, f"rc={rc} · 改的是 {first}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T7: 源码 ⇄ 规格页 漂了 ⇒ 必须红 ──
    tmp = make_sandbox(root)
    try:
        sp = os.path.join(tmp, REL_SPEC)
        stxt = read_text(sp)
        stxt = stxt.replace("| d2_b307_dnp | pins | 307 |", "| d2_b307_dnp | pins | 999 |", 1)
        write_text(sp, stxt)
        rc = run_check(tmp)
        case("T7 ★反向: 源码 ⇄ 规格页 锚点表漂了 ⇒ 必须红 (rc=1)", rc == 1, f"rc={rc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T8: 生成器源码行号漂移 (★这才是 V-3 真正漂的那对行号★) ──
    tmp = make_sandbox(root)
    try:
        gp = os.path.join(tmp, REL_GEN)
        gtxt = read_text(gp)
        write_text(gp, "# ISS262 SELFTEST DRIFT 1\n# ISS262 SELFTEST DRIFT 2\n# ISS262 SELFTEST DRIFT 3\n" + gtxt)
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        ndrift = sum(1 for f in findings if f.kind == "DRIFT")
        ngen = sum(1 for f in findings if f.table == "gen" and f.kind == "DRIFT")
        ok = (rc in (1, 3)) and ngen > 0
        case("T8 ★反向: 生成器源码行号漂移 (★V-3 删 DEMO_DNP 3 行那一种★) ⇒ 必须被报出来",
             ok, f"rc={rc} · DRIFT={ndrift} · 其中源码行={ngen}")
        rc2, _ = reanchor(tmp)
        rc3 = run_check(tmp)
        findings3, _ = judge(tmp)
        ndrift3 = sum(1 for f in findings3 if f.kind == "DRIFT")
        nred3 = sum(1 for f in findings3 if f.kind == "RED")
        case("T9 ★反向: 源码行漂移 ⇒ `--reanchor` 机器改完 ⇒ 必须重新变绿",
             rc2 == 0 and rc3 == 0 and ndrift3 == 0 and nred3 == 0,
             f"reanchor rc={rc2} · 复跑 rc={rc3} · DRIFT={ndrift3} · RED={nred3}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── ★ISS-283 · B1 · 落表授权通道 (★合法落表改 net 名★) 的反向用例 ──
    #   T10 无授权 ⇒ 红   T11 授权齐全 ⇒ 绿 + 同步 registry
    #   T12 授权四项不齐 ⇒ 红   T13 单号台账里查不到 ⇒ 红
    #   T14 授权记录不唯一 ⇒ 红   T15 registry 被手改 ⇒ 仍红
    #   T16 旧身份查不到 (id_str 缺) ⇒ 仍红 (★不许猜★)
    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        _bump_net(tmp, "netlist", line, "ISS283_NET_NOAUTH")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T10 ★反向: 盘上那行的 net 被改了, 但落表台账里查不到授权记录 ⇒ 必须红 (rc=1)",
             rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 锚点={aid}@L{line} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_AUTH"
        _bump_net(tmp, "netlist", line, "ISS283_NET_AUTH")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("ISS-283", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.auth and f.aid == aid for f in findings)
        rc2, _ = reanchor(tmp)
        rc3 = run_check(tmp)
        reg = load_registry(tmp)
        synced = reg["anchors"][aid].get("id_str") == new_vals
        case("T11 ★反向: 落表台账里有完整授权 (单号+文件名+旧身份+新身份) ⇒ 放行并同步 registry",
             rc == 0 and nred == 0 and hit and rc2 == 0 and rc3 == 0 and synced,
             f"判定 rc={rc} · RED={nred} · 走授权通道={hit} · reanchor rc={rc2} · 复跑 rc={rc3} · "
             f"registry 已同步={synced} · 锚点={aid}@L{line}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_INCOMPLETE"
        _bump_net(tmp, "netlist", line, "ISS283_NET_INCOMPLETE")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T12 ★反向: 授权记录【单号缺了】(四项不齐) ⇒ 必须红 (rc=1)",
             rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_NOISSUE"
        _bump_net(tmp, "netlist", line, "ISS283_NET_NOISSUE")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("ISS-999999", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T13 ★反向: 授权记录里的单号在落表台账里查不到 ⇒ 必须红 (rc=1)",
             rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_AMBIG"
        _bump_net(tmp, "netlist", line, "ISS283_NET_AMBIG")
        rowtxt = _auth_row("ISS-283", TABLE_FILES["netlist"], "netlist",
                           line, old_vals, new_vals)
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER), [rowtxt, rowtxt],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T14 ★反向: 授权记录不唯一 (两条一模一样) ⇒ 必须红 (rc=1)",
             rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_migrate_id_str(tmp)
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_TAMPER"
        _bump_net(tmp, "netlist", line, "ISS283_NET_TAMPER")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("ISS-283", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        p = registry_path(tmp)
        reg = json.loads(read_text(p))
        reg["anchors"][aid]["line"] = int(reg["anchors"][aid]["line"]) + 3   # ★手改台账·不重算 sha★
        write_text(p, json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        case("T15 ★反向: registry 被手改 (sha256 对不上) ⇒ 仍红 (rc=1) (★既有行为·不许因本单破例★)",
             rc == 1 and nred > 0, f"rc={rc} · RED={nred} · 改的是 {aid}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_drop_id_str(tmp)          # ★构造前提: 台账里【查不到旧身份】★
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_NOOLD"
        _bump_net(tmp, "netlist", line, "ISS283_NET_NOOLD")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("ISS-283", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T16 ★反向: 台账里查不到这一行的旧身份 (id_str 缺) ⇒ 仍红 (★不许猜★)",
             rc == 1 and nred > 0 and hit,
             f"rc={rc} · RED={nred} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── ★ISS-283 · B1: `--migrate-id-str` 这条【机器补台账】通道本身的反向用例 ★─
    #   T17 身份没变 ⇒ 必须补上 `id_str` ⇒ 补完再改 net + 有授权 ⇒ 绿 (★落表能走通★)
    #   T18 身份已经变了 ⇒ 【不许补】⇒ 仍红 (★fail-closed·不许机器猜旧身份★)
    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        reg0 = load_registry(tmp)
        had0 = bool(reg0["anchors"][aid].get("id_str"))
        rc_m, _msgs = migrate_id_str(tmp)
        reg1 = load_registry(tmp)
        filled = reg1["anchors"][aid].get("id_str") == old_vals
        rc_m2, _msgs2 = migrate_id_str(tmp)          # ★幂等: 第二次必须不再改★
        reg2 = load_registry(tmp)
        idem = reg2["anchors"][aid] == reg1["anchors"][aid]
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_MIGRATED"
        _bump_net(tmp, "netlist", line, "ISS283_NET_MIGRATED")
        _ledger_add_auth(os.path.join(tmp, REL_LEDGER),
                         [_auth_row("ISS-283", TABLE_FILES["netlist"], "netlist",
                                    line, old_vals, new_vals)],
                         heading="## ★★自测授权段 (ISS-283 · B1 反向用例)★★")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        case("T17 ★正向: `--migrate-id-str` 补齐 `id_str` ⇒ 之后【合法落表改 net 名】走通 (rc=0)",
             rc_m == 0 and filled and idem and rc == 0 and nred == 0,
             f"补之前有 id_str={had0} · 补完一致={filled} · 幂等={idem} · 判定 rc={rc} · RED={nred} · 锚点={aid}@L{line}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    tmp = make_sandbox(root)
    try:
        aid, line, cols, old_vals = _pick_net_anchor(tmp)
        _reg_drop_id_str(tmp)          # ★构造前提: 那一条的 `id_str` 还没补★
        new_vals = list(old_vals)
        new_vals[cols.index("net")] = "ISS283_NET_CHANGED"
        _bump_net(tmp, "netlist", line, "ISS283_NET_CHANGED")
        rc_m, _msgs = migrate_id_str(tmp)
        reg3 = load_registry(tmp)
        notfilled = not reg3["anchors"][aid].get("id_str")
        rc = run_check(tmp)
        findings, _ = judge(tmp)
        nred = sum(1 for f in findings if f.kind == "RED")
        hit = any(f.kind == "RED" and f.aid == aid for f in findings)
        case("T18 ★反向: 身份已经被改过的那一条 ⇒ `--migrate-id-str` 【不许补】旧身份 ⇒ 仍红 (★fail-closed★)",
             rc_m == 0 and notfilled and rc == 1 and nred > 0 and hit,
             f"migrate rc={rc_m} · 没补 id_str={notfilled} · 判定 rc={rc} · RED={nred} · 该锚点判红={hit}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("╔══ 落表行号锚点守卫 · 反向用例 (--selftest) ══╗")
    npass = 0
    for name, ok, detail in cases:
        print(f"   {'✅' if ok else '❌'} {name}" + (f"  ★{detail}★" if detail else ""))
        npass += 1 if ok else 0
    print(f"★ 结果: {npass}/{len(cases)}")
    if npass != len(cases):
        print("★★ rc=1: 有用例没过 ★★", file=sys.stderr)
        return 1
    print("★ rc=0: 全部反向用例通过 (★真盘零写入★)")
    return 0


# ═════════════════════════════════════════════════════════════════════════════
# ⑨ main
# ═════════════════════════════════════════════════════════════════════════════
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="★落表行号锚点守卫 (ISS-262)★")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--strict", action="store_true", help="★DRIFT 也算红 (rc=1)★")
    ap.add_argument("--reanchor", action="store_true", help="★机器重锚 (纯漂移 ⇒ 自动改行号 + 更新台账)★")
    ap.add_argument("--dry-run", action="store_true", help="★--reanchor 的干跑 (只报不改)★")
    ap.add_argument("--init-registry", action="store_true", help="★机器建台账★")
    ap.add_argument("--migrate-id-str", action="store_true",
                    help="★台账补 `id_str` (★实体身份值列表·★ISS-283 B1 授权通道的【旧身份】来源★)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "HW")):
        print(f"★★ rc=2: 工程根不对: {root}", file=sys.stderr)
        return 2

    if args.selftest:
        return selftest(root)
    if args.init_registry:
        return init_registry(root)
    if args.migrate_id_str:
        rc, msgs = migrate_id_str(root, dry=args.dry_run)
        for m in msgs:
            print(m)
        return rc
    if args.reanchor:
        rc, msgs = reanchor(root, dry=args.dry_run)
        for m in msgs:
            print(m)
        if rc == 0:
            print("★ 重锚后自检:")
            return run_check(root, strict=args.strict)
        return rc
    if args.json:
        findings, _ = judge(root)
        out = [f.as_dict() for f in findings]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1 if any(f.kind == "RED" for f in findings) else 0
    return run_check(root, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
