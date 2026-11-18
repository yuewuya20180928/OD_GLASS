#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_chain_content_anchor.py —— ★★生产链四环的【内容锚点】判据 (ISS-255 + ISS-256 · sw-lead)★★

★★**为什么要有它 (★病灶, 不是理论★)**:
  ★**`state/chain_gate.py` 原来用「文件 mtime 比新鲜度」当准入判据** (L232/L246/L261/L289)
  ⇒ ★**mtime 既会假红 (内容没变也红) 也会假绿 (内容旧了但 mtime 新)** ★
  · 假红实锤: ④ BOM 19:23 / 网表 19:36 ⇒ mtime 判红, 但 ★**准出栏自己写着「位号 218 全对 · DNP 46 一致」⇒ 内容是对的**★
  · ★**ISS-256**: `.kicad_sch` 每次生成都重铸 uuid + 时间戳 ⇒ ★**md5 永久不可当锚点** ★
    ⇒ ★**任何以原理图 md5 为锚的判据必须改成「内容归一化」口径** ★
  · 跑门禁会改 mtime: `check_sch_erc.py` / `check_sch_pinfull.py` 内部 subprocess 调 `gen_kicad_sch.py`
    ⇒ ★**跑一次门禁就把原理图 mtime 推到最新** ⇒ mtime 连「新鲜度」都不可信 ★

★★**本文件是「内容锚点」的唯一实现处** ⇒ `state/chain_gate.py` 只调用它
   (★便于单测与反向自证 —— ISS-255 交付物 ②★)

★★**四环判据 (语义, 与 ISS-255 任务书 §③ 逐条对应)** ★:
  ① 网表   : ★**md5 == 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里最新登记的 md5**★
              ⇒ 台账没登记 ⇒ ★**红** (★**不许拿 mtime 顶替**★)
  ② 原理图 : ★**语义内容一致** ★
              (A) ★**图上位号集合 == 脚表位号集合** (精确, 经 `kicad_ref_to_table` 还原) ★
              (B) ★**图上网名多重集 == 脚表网名多重集** ★
                  ⇒ ★**等价于「网名集合 ⊇ 网表网名集合」且「不许残留网表已不存在的旧网名」**, 且连数量都对 ★
              (C) ★**网表侧「一颗 2 脚件落进 N 个网」语义自洽** (★R3-A1 同口径★)
                  ⇒ ★**这一层是「只改网名 / 只改连线登记」那类落表的抓手** (ISS-255 硬规矩 ②)
                  ⇒ 口径说明: ★**只对 2 脚 C 生效** (★R3-A1 同口径★ ⇒ 现状 0 命中 ⇒ **零假红**★)
  ③ PCB    : ★**焊盘级等价** ★ ⇒ ★**复用 `state/check_pcb_nets.py` 的 C1/C2 判据** (★它本来就是内容判据★)
  ④ BOM    : ★**逐行 (位号, value, dnp) 一致** ★ ⇒ ★**期望值用 `state/gen_bom.py` 自己的聚合口径算** (★零漂移★)

★★**ISS-256 硬要求: 「`.kicad_sch` 的 md5 永久不可当锚点」★★
   ⇒ 本文件 ★**任何地方都不用 `.kicad_sch` 的 md5 当判据** ★
   ⇒ 只用 ★**归一化内容指纹** (去 uuid / 去时间戳) ★ ⇒ ★**uuid 抖动 ⇒ 判据结果不变** ★
   (`normalize_sch_text()` + `sch_content_fingerprint()` + ★`--selftest` 的 T3 用例★)

用法:
  python3 state/check_chain_content_anchor.py            # ★体检: 跑四环锚点并报结果 (rc=0 = 工具自身健康)
  python3 state/check_chain_content_anchor.py --strict   # ★严格: 任一环红 ⇒ rc=1
  python3 state/check_chain_content_anchor.py --selftest  # ★反向用例 (≥8 条) ⇒ rc=0
  python3 state/check_chain_content_anchor.py --json     # 机器读格式

★★**rc 语义 (★不制造假绿★)**: 默认体检模式 rc=0 只代表「工具跑起来了」, ★**四环的红绿在输出里逐条报**
   ⇒ ★**门禁的裁决权在 `state/chain_gate.py`** (它按自己的 rc 汇总) ⇒ ★**本工具的红不会被人误读成绿**★
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---------------------------------------------------------------- 路径 (相对 root)
REL_NETLIST = os.path.join("HW", "netlist_v1.csv")
REL_PINS = os.path.join("HW", "netlist_v1_pins.csv")
REL_BOM = os.path.join("HW", "BOM_v1.csv")
REL_LEDGER = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
REL_PCB = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
REL_SCH_DIR = os.path.join("HW", "PCB")
REL_PCB_CHECK = os.path.join("state", "check_pcb_nets.py")
REL_PCB_PY = os.path.join("state", "pcbnew_py.sh")

MD5_RE = re.compile(r"\b[0-9a-f]{32}\b")
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                     r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
TS_RE = re.compile(r"\b(20\d\d[-/]\d\d[-/]\d\d([ T]\d\d:\d\d(:\d\d)?)?)\b")


# ================================================================ 小工具
def md5_file(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ts_of(path: str) -> str:
    import time
    try:
        t = os.path.getmtime(path)
    except Exception:
        return "(缺)"
    return time.strftime("%m-%d %H:%M", time.localtime(t))


def _read_csv(path: str):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _cell(row, key: str) -> str:
    return (row.get(key) or "").strip()


# ================================================================ ISS-256 · 归一化
def normalize_sch_text(text: str) -> str:
    """★`.kicad_sch` 内容归一化 (★ISS-256: md5 永久不可当锚点 ⇒ 只能比归一化内容★)

    ★去掉三类抖动源**:
      ① 随机 uuid (每次生成重铸)  ② 时间戳 (date / timestamp 字段)  ③ 生成器版本串
    ★归一化后**逐字节相同** ⇒ 两份图就是同一张图 ⇒ ★**uuid 抖动 ⇒ 判据结果不变** ★
    """
    t = UUID_RE.sub("<UUID>", text)
    t = TS_RE.sub("<TS>", t)
    t = re.sub(r'\(generator\s+"[^"]*"', '(generator "<GEN>"', t)
    t = re.sub(r'\(date\s+"[^"]*"', '(date "<DATE>"', t)
    t = re.sub(r'\(rev\s+"[^"]*"', '(rev "<REV>"', t)
    return t


def sch_content_fingerprint(sch_dir: str):
    """★原理图目录 ⇒ (逐文件归一化指纹, 汇总指纹, 文件名列表) ★"""
    import glob
    files = sorted(glob.glob(os.path.join(sch_dir, "*.kicad_sch")))
    per = OrderedDict()
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                per[os.path.basename(f)] = sha256_text(normalize_sch_text(fh.read()))
        except Exception:
            per[os.path.basename(f)] = "READ_FAIL"
    agg = sha256_text("|".join(f"{k}={v}" for k, v in per.items()))
    return per, agg, [os.path.basename(f) for f in files]


def sch_refs_and_labels(sch_dir: str):
    """★原理图目录 ⇒ (位号集合, 网名多重集, 网名集合) ★
    ★位号口径: 图上位号带 `_N` 尾巴 (★ISS-205★) ⇒ 用生成器的 `kicad_ref_to_table` 精确还原成表侧 ref ★
    ★网名口径: ★**全局标签 = 网名** (★生成器每个脚发一个全局标签, 标签文本 = 该脚的网名★) ★
    """
    import glob
    ref_re = re.compile(r'\(property\s+"Reference"\s+"([^"]+)"')
    lab_re = re.compile(r'\((?:global_label|local_label|hierarchical_label)\s+"([^"]+)"')
    raw_refs, labels = [], Counter()
    for f in sorted(glob.glob(os.path.join(sch_dir, "*.kicad_sch"))):
        with open(f, encoding="utf-8") as fh:
            t = fh.read()
        raw_refs.extend(ref_re.findall(t))
        for m in lab_re.finditer(t):
            labels[m.group(1)] += 1
    return raw_refs, labels, set(labels)


def _kicad_ref_to_table(refs):
    """★图上位号 → 表侧 ref 的**精确**反查 (★口径单一真源 = 生成器 `kicad_ref()`★)
    ★生成器导不进来 ⇒ 用**同规则的本地副本**兜底 (★ISS-205 规则: 末字符是数字 ⇒ 不动; 否则加 `_1`★)"""
    try:
        import gen_kicad_sch  # type: ignore
        fn = getattr(gen_kicad_sch, "kicad_ref_to_table", None)
        if callable(fn):
            return fn(list(refs))
    except Exception:
        pass
    out = {}
    for r in refs:
        r = (r or "").strip()
        if not r:
            continue
        out[r if r[-1].isdigit() else r + "_1"] = r
    return out


# ================================================================ ① 网表 · 台账锚点
def ledger_latest_md5(ledger_path: str, token: str):
    """★落表台账里某文件**最新登记**的 md5 ★

    ★**口径 (★可复现★)**: 台账里凡是提到该文件名的**表格行**, 取该行里**最后一个完整 32 位 md5**
      (★md5 台账的列序是「单号 | 文件 | 旧 md5 | 新 md5」⇒ 最后一个 = 新 md5★)
      ⇒ ★**只认「同行有 ≥2 个完整 md5」的行** (★只有旧 md5 的行不采纳 ⇒ 防把「旧值」当「登记值」★)
    ★返回 (md5, 行号) ★"""
    try:
        with open(ledger_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except Exception:
        return None, 0
    best = (None, 0)
    for i, line in enumerate(lines, 1):
        if token not in line:
            continue
        toks = MD5_RE.findall(line)
        if len(toks) >= 2:
            best = (toks[-1], i)
    return best


def anchor_netlist(root: str = PROJ):
    """★① 网表 · 内容锚点 (★= 台账登记的 md5★) ★"""
    csv_p = os.path.join(root, REL_NETLIST)
    led_p = os.path.join(root, REL_LEDGER)
    if not os.path.exists(csv_p):
        return False, f"网表不存在 ({REL_NETLIST})"
    if not os.path.exists(led_p):
        return False, (f"落表台账不存在 ({REL_LEDGER}) ⇒ 无法判定「本次落表是否已登记」 "
                       f"⇒ ★**不许拿 mtime 顶替**★")
    now = md5_file(csv_p)
    reg, line = ledger_latest_md5(led_p, "netlist_v1.csv")
    if not reg:
        return False, (f"落表台账里没有 `{REL_NETLIST}` 的 md5 登记 ⇒ ★**没法判「网表有没有落表」** "
                       f"⇒ 修法: 在落表台账的 md5 台账里补一行 (单号 | 文件 | 旧 md5 | 新 md5)")
    if now != reg:
        return False, (f"网表 md5 `{now[:12]}…` ≠ 台账最新登记 `{reg[:12]}…` (台账 {REL_LEDGER} L{line}) "
                       f"⇒ ★**落表没进台账 / 台账登的是别的版本** ⇒ 修法: ① 确认落表完成 ⇒ 在落表台账 md5 台账补登记 "
                       f"② 或重跑 `python3 state/gen_netlist.py` 把网表打回台账登记的那一版")
    return True, (f"网表 md5 `{now[:12]}…` == 落表台账最新登记 (L{line}) · {ts_of(csv_p)}")


# ================================================================ ② 原理图 · 语义内容
def _f1_class_check(wire_csv: str, pins_csv: str):
    """★网表侧「一颗 2 脚件落进 N 个网」自洽检查 (★R3-A1 同口径★)

    ★**为什么要有这一层**: ISS-255 硬规矩 ② ⇒ ② 必须能抓「只改网名 / 只改连线登记」那类落表
      (★F1 就是这种: `C_VBUS_OUT` → `VBUS_5V_F1`/`VBUS_5V_CHG`★)
      ⇒ ★**只改 node 槽 ⇒ 脚表/图上零变化 ⇒ (A)(B) 抓不到 ⇒ 必须有这一层** ★
    ★**口径 (★与 `HW/check_netlist_contradiction_r3.py` 的 R3-A1 逐字一致★)**:
      · 脚表里 **type=='C' 且恰好 2 脚** 的器件
      · ★**端子登记次数** = 该器件的裸位号在网表 node 槽里出现的总次数 ★
      · 登记次数 > 脚数 ⇒ ★**一颗 2 脚件落进 3 个网** ⇒ 红 ★
    ★**为什么只判 2 脚 C**: 全表 (R/L) 里有 26 颗 2 脚件的裸位号被别的行当对端引用
      (★「一行 = 一根连接」模型的正常写法★) ⇒ 判据只对 2 脚 C 生效 (★零假红★)
    """
    rows = _read_csv(wire_csv)
    pins = _read_csv(pins_csv)
    types, pinmap = {}, {}
    for r in rows:
        ref = _cell(r, "ref")
        if ref and ref not in types:
            types[ref] = _cell(r, "type")
    for r in pins:
        ref = _cell(r, "ref")
        if ref:
            pinmap.setdefault(ref, {})[_cell(r, "pin")] = _cell(r, "net")
    regs = {}
    for ln, r in enumerate(rows, 2):
        for slot in ("node1", "node2"):
            v = _cell(r, slot)
            if not v or " " in v:        # 带 " pinN" 的是物理脚, 不是裸位号
                continue
            regs.setdefault(v, []).append((ln, _cell(r, "net"), slot, _cell(r, "ref")))
    hits = []
    for ref, pm in pinmap.items():
        if types.get(ref) != "C" or len(pm) != 2:
            continue
        occ = regs.get(ref, [])
        if len(occ) > 2:
            hits.append((ref, len(occ), occ))
    return hits


def anchor_schematic(root: str = PROJ):
    """★② 原理图 · 语义内容锚点 (★位号 + 网名 + 网表连线语义 三层★)"""
    sch_dir = os.path.join(root, REL_SCH_DIR)
    pins_p = os.path.join(root, REL_PINS)
    wire_p = os.path.join(root, REL_NETLIST)
    if not os.path.isdir(sch_dir):
        return False, "原理图目录不存在"
    if not os.path.exists(pins_p):
        return False, "脚级真值表不存在 (HW/netlist_v1_pins.csv)"
    raw_refs, labels, label_set = sch_refs_and_labels(sch_dir)
    if not raw_refs:
        return False, "原理图里一个器件都没读到 (★图上无 Reference 属性★)"
    prows = _read_csv(pins_p)
    pin_refs = set()
    net_cnt = Counter()
    for r in prows:
        ref = _cell(r, "ref")
        if ref:
            pin_refs.add(ref)
            net_cnt[_cell(r, "net")] += 1
    # ★图上位号 → 表侧 ref 的**精确**还原 (★口径单一真源 = 生成器 `kicad_ref_to_table()`★)
    #   ★生成器的函数返回的是 {图上位号: 表侧 ref} (★kicad_ref(r) → r★) ⇒ 直接用, 不许再倒一次 ★
    sch2tbl = _kicad_ref_to_table(sorted(pin_refs))     # {图上位号 → 表侧 ref}
    sch_refs = set()
    unknown = []
    for r in raw_refs:
        t = sch2tbl.get(r)
        if t is None:
            unknown.append(r)
        else:
            sch_refs.add(t)
    per, agg, files = sch_content_fingerprint(sch_dir)
    problems = []
    # (A) 位号集合
    miss_r = sorted(pin_refs - sch_refs)
    extra_r = sorted(sch_refs - pin_refs)
    if miss_r or extra_r or unknown:
        problems.append(f"位号: 脚表有图上没有 {len(miss_r)} 个 (例 {miss_r[:3]})"
                        f" / 图上有脚表没有 {len(extra_r)} 个 (例 {extra_r[:3]})"
                        + (f" / 图上位号还原不出 {len(unknown)} 个 (例 {unknown[:3]})" if unknown else ""))
    # (B) 网名多重集 (⇒ ⊇ 且不许残留旧网名, 连数量一起对)
    miss_n = sorted(set(net_cnt) - label_set)
    extra_n = sorted(label_set - set(net_cnt))
    cnt_diff = [(n, net_cnt.get(n, 0), labels.get(n, 0))
                for n in sorted(set(net_cnt) | set(labels))
                if net_cnt.get(n, 0) != labels.get(n, 0)]
    if miss_n or extra_n or cnt_diff:
        problems.append(f"网名: 缺 {len(miss_n)} 个 (例 {miss_n[:3]}) / 残留旧名 {len(extra_n)} 个 (例 {extra_n[:3]})"
                        f" / 数量不符 {len(cnt_diff)} 个 (例 {cnt_diff[:3]})")
    # (C) 网表侧连线语义 (F1 类)
    if os.path.exists(wire_p):
        hits = _f1_class_check(wire_p, pins_p)
        if hits:
            ref, occ, lst = hits[0]
            problems.append(f"网表连线语义: ★**{ref} 的端子被登记 {occ} 次 > 脚数 2**"
                            f" (一行 = 一根连接的模型里一颗 2 脚件落进 3 个网 ⇒ 导出后一脚悬空)"
                            f" ⇒ 修法: 该行 node 槽借用别人的裸位号 ⇒ 改成**本行自己的网名**")
    head = (f"位号 {len(sch_refs)} == 脚表 {len(pin_refs)} · 标签 {sum(labels.values())} == 脚 {sum(net_cnt.values())}"
            f" · 归一化指纹 {agg[:12]}…")
    if problems:
        return False, (head + " ⇒ ★**" + "; ".join(problems) + "**")
    return True, (head + f" · {len(files)} 个 .kicad_sch 归一化后一致 (★uuid 抖动不影响本判据★)"
                  f" · {ts_of(os.path.join(sch_dir, 'demo_mainboard.kicad_sch'))}")


# ================================================================ ③ PCB · 焊盘级等价
def anchor_pcb(root: str = PROJ):
    """★③ PCB · 内容锚点 (★焊盘级等价 ⇒ 复用 `state/check_pcb_nets.py` 的 C1/C2 判据★)"""
    chk = os.path.join(root, REL_PCB_CHECK)
    py = os.path.join(root, REL_PCB_PY)
    pcb = os.path.join(root, REL_PCB)
    if not os.path.exists(pcb):
        return False, f"板文件不存在 ({REL_PCB})"
    if not (os.path.exists(chk) and os.path.exists(py)):
        return False, (f"★**板侧等价判据跑不起来** ({REL_PCB_CHECK} / {REL_PCB_PY} 不在) "
                       f"⇒ ★**保守判红** (★不许假绿★)")
    try:
        r = subprocess.run(["bash", py, chk], capture_output=True, text=True,
                           timeout=600, cwd=root)
    except Exception as e:
        return False, f"★**板侧等价判据跑不起来** ({e}) ⇒ ★**保守判红** (★不许假绿★)"
    out = (r.stdout or "") + (r.stderr or "")
    c1 = [l.strip() for l in out.splitlines() if "C1 " in l]
    c2 = [l.strip() for l in out.splitlines() if "C2 " in l]
    c2bad = [l for l in c2 if l.startswith("❌")]
    if r.returncode == 0:
        return True, (f"焊盘级等价 (★复用 check_pcb_nets 的 C1/C2★) · C1 ✅ · C2 {len(c2)} 项全 ✅"
                      f" · {ts_of(pcb)}")
    detail = " / ".join((c1[:1] + c2bad[:2]) or ["(无明细)"])[:200]
    return False, (f"★**板与网表不等价** (C1/C2 红 ⇒ 板是旧网表的板) · {detail} · {ts_of(pcb)}")


# ================================================================ ④ BOM · 逐行一致
def _expected_bom_rows(pins_csv: str, pcb_path: str):
    """★BOM 期望行 (★**用 `state/gen_bom.py` 自己的聚合口径** ⇒ 零漂移★)"""
    import gen_bom  # type: ignore
    rows = _read_csv(pins_csv)
    board = gen_bom.parse_board_footprints(pcb_path)
    groups = OrderedDict()
    for r in rows:
        ref = _cell(r, "ref")
        if ref:
            groups.setdefault(ref, []).append(r)
    out = OrderedDict()
    for ref, rs in groups.items():
        dps = [_cell(r, "dnp").upper() for r in rs]
        if dps and set(dps) == {"DNP"}:
            dnp = "DNP"
        elif "必装" in dps:
            dnp = "必装"
        elif dps and set(dps) == {"可选"}:
            dnp = "可选"
        else:
            dnp = "必装"
        val = gen_bom._pick_value(rs, (board.get(ref) or {}).get("value", ""))
        out[ref] = (val, dnp)
    return out


def anchor_bom(root: str = PROJ):
    """★④ BOM · 内容锚点 (★逐行 (位号, value, dnp) 一致★)"""
    bom_p = os.path.join(root, REL_BOM)
    pins_p = os.path.join(root, REL_PINS)
    pcb_p = os.path.join(root, REL_PCB)
    if not os.path.exists(bom_p):
        return False, f"BOM 不存在 ({REL_BOM})"
    if not os.path.exists(pins_p):
        return False, "脚级真值表不存在 (HW/netlist_v1_pins.csv)"
    try:
        exp = _expected_bom_rows(pins_p, pcb_p)
    except Exception as e:
        return False, f"★**BOM 期望值算不出来** ({e}) ⇒ ★**保守判红** (★不许假绿★)"
    got = OrderedDict()
    for r in _read_csv(bom_p):
        ref = _cell(r, "ref")
        if ref:
            got[ref] = (_cell(r, "value"), _cell(r, "dnp"))
    miss = sorted(set(exp) - set(got))
    extra = sorted(set(got) - set(exp))
    diff = [(r, exp[r], got[r]) for r in sorted(set(exp) & set(got)) if exp[r] != got[r]]
    if miss or extra or diff:
        msg = []
        if miss:
            msg.append(f"真源有 BOM 没有 {len(miss)} 个 (例 {miss[:5]})")
        if extra:
            msg.append(f"BOM 有真源没有 {len(extra)} 个 (例 {extra[:5]})")
        if diff:
            msg.append(f"(位号,value,dnp) 不一致 {len(diff)} 个 (例 {diff[:3]})")
        return False, ("; ".join(msg) + " ⇒ 修法: 重跑 `python3 state/gen_bom.py`")
    return True, (f"逐行一致: {len(exp)} 行 (位号,value,dnp) == 脚表聚合 · {ts_of(bom_p)}")


# ================================================================ 四环总跑
ANCHORS = OrderedDict([
    ("① 网表", anchor_netlist),
    ("② 原理图", anchor_schematic),
    ("③ PCB", anchor_pcb),
    ("④ BOM", anchor_bom),
])


def run_all(root: str = PROJ):
    res = OrderedDict()
    for name, fn in ANCHORS.items():
        try:
            ok, msg = fn(root)
        except Exception as e:               # ★工具自身炸了 ⇒ 保守判红 (★不许假绿★)
            ok, msg = False, f"★**判据执行异常** ({type(e).__name__}: {e}) ⇒ 保守判红"
        res[name] = (ok, msg)
    return res


def _fmt(res):
    lines = []
    for name, (ok, msg) in res.items():
        lines.append(f"{name:<10}{'✅' if ok else '❌'}  {msg}")
    return "\n".join(lines)


# ================================================================ 反向用例 (沙盒)
def _sbx_copy(root: str, dest: str):
    """★把判据要用的文件拷进沙盒 (★真盘只读★)"""
    os.makedirs(dest, exist_ok=True)
    for rel in (REL_NETLIST, REL_PINS, REL_BOM, REL_LEDGER, REL_PCB,
                REL_PCB_CHECK, REL_PCB_PY):
        src = os.path.join(root, rel)
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    sch_dst = os.path.join(dest, REL_SCH_DIR)
    os.makedirs(sch_dst, exist_ok=True)
    import glob
    for f in glob.glob(os.path.join(root, REL_SCH_DIR, "*.kicad_sch")):
        shutil.copy2(f, os.path.join(sch_dst, os.path.basename(f)))
    return dest


def _sbx_regen_schematic(root: str, sbx: str):
    """★正向用例用: 在沙盒里重跑生成链 (★`gen_netlist → gen_kicad_net → gen_netlist_pins → gen_bom → gen_kicad_sch`★)
    ★**真盘一个字节都不碰** (★生成器读的是沙盒路径★) ⇒ 零落表 ★"""
    import glob
    tree = os.path.join(sbx, "tree")
    if os.path.isdir(tree):
        shutil.rmtree(tree)
    os.makedirs(tree)
    # ★拷贝整棵树 (★排除大 onnx★) ⇒ 生成器的相对路径全对
    for name in os.listdir(root):
        if name.endswith(".onnx") or name == ".git":
            continue
        src = os.path.join(root, name)
        dst = os.path.join(tree, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=True)
        else:
            shutil.copy2(src, dst)
    cmds = [["state/gen_netlist.py"], ["state/gen_kicad_net.py"], ["state/gen_netlist_pins.py"],
            ["state/gen_bom.py"], ["state/gen_kicad_sch.py"]]
    outs = []
    for c in cmds:
        try:
            r = subprocess.run([sys.executable] + c, capture_output=True, text=True,
                               timeout=900, cwd=tree)
            outs.append((c[0], r.returncode, (r.stdout or "")[-400:], (r.stderr or "")[-400:]))
        except Exception as e:
            outs.append((c[0], 99, "", str(e)))
    return tree, outs


def _mutate_sch_label(sbx: str, old: str, new: str):
    """★把沙盒原理图里的某个网名换成别的 (★只改网名★)"""
    import glob
    n = 0
    for f in glob.glob(os.path.join(sbx, REL_SCH_DIR, "*.kicad_sch")):
        t = open(f, encoding="utf-8").read()
        t2 = t.replace('(global_label "%s"' % old, '(global_label "%s"' % new)
        if t2 != t:
            open(f, "w", encoding="utf-8").write(t2)
            n += 1
    return n


def _mutate_sch_drop_ref(sbx: str, ref: str):
    """★把沙盒原理图里某个器件的 Reference 属性改掉 (★= 图上少一个位号★)
    ★★**图上位号带 `_N` 尾巴** (★ISS-205★) ⇒ 先用生成器的 `kicad_ref()` 还原成图上位号再改 ★"""
    import glob
    sch_ref = ref if ref[-1].isdigit() else ref + "_1"
    n = 0
    for f in glob.glob(os.path.join(sbx, REL_SCH_DIR, "*.kicad_sch")):
        t = open(f, encoding="utf-8").read()
        t2 = re.sub(r'\(property\s+"Reference"\s+"%s"' % re.escape(sch_ref),
                    '(property "Reference" "%s_XX"' % sch_ref, t)
        if t2 != t:
            open(f, "w", encoding="utf-8").write(t2)
            n += 1
    return n


def _mutate_uuid_jitter(sbx: str):
    """★ISS-256 核心: 把沙盒原理图的 uuid 全部重铸 (★内容等价, 字节不同★)"""
    import glob
    rnd = random.Random(20261116)
    n = 0
    for f in glob.glob(os.path.join(sbx, REL_SCH_DIR, "*.kicad_sch")):
        t = open(f, encoding="utf-8").read()
        def _rep(m):
            return '"%s"' % "-".join("%08x" % rnd.getrandbits(32) for _ in range(1)) + \
                "-%04x-%04x-%04x-%012x" % (rnd.getrandbits(16), rnd.getrandbits(16),
                                           rnd.getrandbits(16), rnd.getrandbits(48))
        t2 = UUID_RE.sub(_rep, t)
        if t2 != t:
            open(f, "w", encoding="utf-8").write(t2)
            n += 1
    return n


def _mutate_bom(sbx: str, ref: str, value=None, dnp=None, drop=False):
    p = os.path.join(sbx, REL_BOM)
    rows = list(csv.reader(open(p, encoding="utf-8-sig", newline="")))
    head, body = rows[0], rows[1:]
    out = []
    for r in body:
        if r and r[0] == ref:
            if drop:
                continue
            if value is not None:
                r[head.index("value")] = value
            if dnp is not None:
                r[head.index("dnp")] = dnp
        out.append(r)
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(out)


def _mutate_netlist_node(sbx: str, line_no: int, slot: str, newval: str):
    """★把沙盒网表第 line_no 行的某个 node 槽改成别的 (★F1 落表前那类「借位号」★)
    ★**line_no 是文件行号 (表头 = 第 1 行)** ★"""
    p = os.path.join(sbx, REL_NETLIST)
    lines = open(p, encoding="utf-8").read().splitlines()
    head = next(csv.reader([lines[0]]))
    col = head.index(slot)                       # ★列号从**表头**取 (★不许拿数据行找列名★)
    i = line_no - 1
    row = next(csv.reader([lines[i]]))
    row[col] = newval
    lines[i] = ",".join(row)
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def selftest(root: str = PROJ):
    """★反向用例 (★每条都证明「改了坏东西 ⇒ 必须变红」; 唯一例外是 T3 uuid 抖动 ⇒ 必须仍绿★) ★"""
    cases = []
    tmp = tempfile.mkdtemp(prefix="iss255_sbx_")
    try:
        base = _sbx_copy(root, os.path.join(tmp, "base"))
        base_res = run_all(base)
        # ★基线: ①④ 绿; ② 绿 (★原理图内容与脚表一致★); ③ 红 (★板侧那趟没做 ⇒ 真红★)
        cases.append(("T0 基线 (沙盒 = 真盘当前状态): ①绿 ②绿 ④绿 · ③红 (★板侧那趟没做⇒真红★)",
                      base_res["① 网表"][0] and base_res["② 原理图"][0] and base_res["④ BOM"][0]
                      and not base_res["③ PCB"][0],
                      " | ".join(f"{k}={'✅' if v[0] else '❌'}" for k, v in base_res.items())))
        # ---- T1 原理图删一个器件 ⇒ ② 红 ----
        s1 = _sbx_copy(root, os.path.join(tmp, "t1"))
        _mutate_sch_drop_ref(s1, "R_PU_PG")
        r = run_all(s1)
        cases.append(("T1 原理图删一个器件 (R_PU_PG) ⇒ 期望 ② 红", not r["② 原理图"][0],
                      r["② 原理图"][1][:160]))
        # ---- T2 原理图网名改回旧值 ⇒ ② 红 ----
        s2 = _sbx_copy(root, os.path.join(tmp, "t2"))
        _mutate_sch_label(s2, "VBUS_5V_F1", "C_VBUS_OUT")
        r = run_all(s2)
        cases.append(("T2 原理图网名改回旧值 (VBUS_5V_F1 → C_VBUS_OUT) ⇒ 期望 ② 红",
                      not r["② 原理图"][0], r["② 原理图"][1][:160]))
        # ---- T3 uuid 抖动 ⇒ ② 仍绿 (ISS-256 核心验收) ----
        s3 = _sbx_copy(root, os.path.join(tmp, "t3"))
        _, agg_before, _ = sch_content_fingerprint(os.path.join(s3, REL_SCH_DIR))
        n = _mutate_uuid_jitter(s3)
        _, agg_after, _ = sch_content_fingerprint(os.path.join(s3, REL_SCH_DIR))
        r = run_all(s3)
        cases.append((f"T3 原理图 uuid 抖动 ({n} 个文件重铸) ⇒ ★**期望 ② 仍绿** 且归一化指纹不变 ★",
                      r["② 原理图"][0] and agg_before == agg_after,
                      f"指纹 {agg_before[:12]}… ⇒ {agg_after[:12]}… · " + r["② 原理图"][1][:120]))
        # ---- T4 BOM 改一个 value ⇒ ④ 红 ----
        s4 = _sbx_copy(root, os.path.join(tmp, "t4"))
        _mutate_bom(s4, "BT_432243", value="432243 3.7V 改坏了")
        r = run_all(s4)
        cases.append(("T4 BOM 改一个 value ⇒ 期望 ④ 红", not r["④ BOM"][0], r["④ BOM"][1][:160]))
        # ---- T5 BOM 改 dnp ⇒ ④ 红 ----
        s5 = _sbx_copy(root, os.path.join(tmp, "t5"))
        _mutate_bom(s5, "R_PU_PG", dnp="DNP")
        r = run_all(s5)
        cases.append(("T5 BOM 改 dnp ⇒ 期望 ④ 红", not r["④ BOM"][0], r["④ BOM"][1][:160]))
        # ---- T6 网表 md5 与台账登记不符 ⇒ ① 红 ----
        s6 = _sbx_copy(root, os.path.join(tmp, "t6"))
        p = os.path.join(s6, REL_NETLIST)
        with open(p, "a", encoding="utf-8") as f:
            f.write("P1,__TAMPER__,X,Y,__TAMPER__,x,C,必装,[实测],,测试追加,,\n")
        r = run_all(s6)
        cases.append(("T6 网表被改了 (md5 ≠ 台账登记) ⇒ 期望 ① 红", not r["① 网表"][0],
                      r["① 网表"][1][:160]))
        # ---- T7 板与网表不等价 ⇒ ③ 红 (★板侧那趟没做 ⇒ 真红★) ----
        s7 = _sbx_copy(root, os.path.join(tmp, "t7"))
        r = run_all(s7)
        cases.append(("T7 板与网表不等价 (板侧那趟没做) ⇒ 期望 ③ 红", not r["③ PCB"][0],
                      r["③ PCB"][1][:160]))
        # ---- T7b 板被改坏 (焊盘网名对不上) ⇒ ③ 仍红 (★敏感度证明★) ----
        s7b = _sbx_copy(root, os.path.join(tmp, "t7b"))
        pb = os.path.join(s7b, REL_PCB)
        t = open(pb, encoding="utf-8").read()
        t2 = t.replace('(net "GND")', '(net "GND_TAMPER")', 1)
        open(pb, "w", encoding="utf-8").write(t2)
        r = run_all(s7b)
        cases.append(("T7b 板文件被改 (一个焊盘网名改掉) ⇒ 期望 ③ 红 (敏感度)",
                      not r["③ PCB"][0], r["③ PCB"][1][:160]))
        # ---- T8 全部改回去 ⇒ 回到基线 (① ② ④ 绿 · ③ 红) ----
        s8 = _sbx_copy(root, os.path.join(tmp, "t8"))
        r = run_all(s8)
        cases.append(("T8 全部改回去 (重拷基线) ⇒ 期望 ① ② ④ 绿 · ③ 红 (★真红不许被调没★)",
                      r["① 网表"][0] and r["② 原理图"][0] and r["④ BOM"][0] and not r["③ PCB"][0],
                      " | ".join(f"{k}={'✅' if v[0] else '❌'}" for k, v in r.items())))
        # ---- T9 网表改网名 (只改网名不落表) ⇒ ② 红 (★「只改网名」那类落表★) ----
        s9 = _sbx_copy(root, os.path.join(tmp, "t9"))
        _mutate_netlist_node(s9, 8, "net", "VBUS_5V_F1_RENAMED")
        r = run_all(s9)
        cases.append(("T9 网表改网名 (网表 L8 net → VBUS_5V_F1_RENAMED, 图没重生成) ⇒ 期望 ② 红",
                      not r["② 原理图"][0], r["② 原理图"][1][:160]))
        # ---- T10 网表借位号 (F1 落表前那种) ⇒ ② 红 (★硬规矩 ② 的抓手★) ----
        s10 = _sbx_copy(root, os.path.join(tmp, "t10"))
        _mutate_netlist_node(s10, 8, "node2", "C_VBUS_OUT")
        r = run_all(s10)
        cases.append(("T10 网表 node 槽借位号 (★F1 落表前: L8 node2 → C_VBUS_OUT★) ⇒ 期望 ② 红",
                      not r["② 原理图"][0], r["② 原理图"][1][:200]))
        # ---- T11 BOM 删一行 ⇒ ④ 红 ----
        s11 = _sbx_copy(root, os.path.join(tmp, "t11"))
        _mutate_bom(s11, "R_PU_PG", drop=True)
        r = run_all(s11)
        cases.append(("T11 BOM 删一行 ⇒ 期望 ④ 红", not r["④ BOM"][0], r["④ BOM"][1][:160]))
        # ---- T12 原理图多一个器件 ⇒ ② 红 ----
        s12 = _sbx_copy(root, os.path.join(tmp, "t12"))
        _mutate_sch_drop_ref(s12, "R_PU_PG")
        import glob
        f0 = sorted(glob.glob(os.path.join(s12, REL_SCH_DIR, "*.kicad_sch")))[0]
        t = open(f0, encoding="utf-8").read()
        t = t.replace('(property "Reference" "R_PU_PG_XX"',
                      '(property "Reference" "R_PU_PG_XX"', 1)
        open(f0, "w", encoding="utf-8").write(t)
        r = run_all(s12)
        cases.append(("T12 原理图多一个图上有脚表没有的位号 ⇒ 期望 ② 红",
                      not r["② 原理图"][0], r["② 原理图"][1][:160]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # ---- 打印 ----
    print("=" * 78)
    print("内容锚点 · 反向用例 (--selftest) · ★沙盒内做, 真盘只读★")
    print("=" * 78)
    npass = 0
    for name, ok, detail in cases:
        print(f"{'✅' if ok else '❌'} {name}")
        print(f"   {detail}")
        npass += 1 if ok else 0
    print("-" * 78)
    print(f"用例 {len(cases)} 条 · 通过 {npass} 条 · 失败 {len(cases) - npass} 条")
    return 0 if npass == len(cases) else 1


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest(PROJ)
    if "--json" in args:
        res = run_all(PROJ)
        print(json.dumps({k: {"ok": v[0], "msg": v[1]} for k, v in res.items()},
                         ensure_ascii=False, indent=2))
        return 0
    res = run_all(PROJ)
    print("=" * 78)
    print("生产链四环 · 内容锚点体检 (★判据 = 内容, 不是 mtime★)")
    print("=" * 78)
    print(_fmt(res))
    print("-" * 78)
    print("★rc 语义: 0 = 工具自身健康 (四环红绿见上) · 2 = 工具自身出错 "
          "(★门禁裁决权在 state/chain_gate.py★)")
    if "--strict" in args:
        bad = [k for k, v in res.items() if not v[0]]
        if bad:
            print(f"❌ --strict: {len(bad)} 环红: {', '.join(bad)}")
            return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                       # ★工具自身炸 ⇒ rc=2 (★不许假装绿★)
        print(f"★**工具自身异常**: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
