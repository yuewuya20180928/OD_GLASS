#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_onepass_legb_sw_impact.py — ISS-370 「板那一趟」腿 B ⇒ SW 侧影响面闸
======================================================================================
目的: 让「板只改一次」那一趟里的【腿 B = 网表节点具名 200 条指令】那一跳, 当天 SW 侧
      【红的每一条都能被解释 + 每一类红都能被机器分开】—— 而不是开工当天现场抓瞎。

★**本闸是只读闸 + 沙盒预演闸**: 真件 (板 / 网表 / 脚表 / BOM / 落表台账 / 既有闸脚本 /
  既有页面) 一个字节都不许动 ⇒ 所有写操作只发生在项目内 `tmp/iss370_gate_sbx/` ★

★**判据九条 (G0~G8)** ★:
  G0 基准块存在且是合法 JSON (★同款 `<!-- NAME:BEGIN -->` / `<!-- NAME:END -->` 块★)
  G1 腿 B 的三个数由【本脚本自己算出来】(改动格数 / 改动栏 ⊆ {node1,node2} / 行数 513→517)
       ⇒ 页里写的 ≠ 脚本实算 ⇒ 红
  G2 红项集合由【本脚本自己实跑 timing_check.py】抓来 ⇒ 抓到的 == 页里声明的
       (★两套口径: `--netlist` 口径 15 条 + 落表仿真口径 16 条★)
  G3 每条红项的归类非空且 ∈ {语义破坏, 落表义务, 反向用例}
  G4 「语义红」与「落表义务红」可分离 (★本闸的核心: 它抓的是【把两类红混为一谈】★)
  G5 §2 同批清单每件 8 字段齐全 + 归属/时序不许空 + 跨域件必须写「跨域」+ 改法不许空洞
  G6 证据等级全在五级白名单 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ 写 `[官方]` = 红)
  G7 正文无挂起措辞 (禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」)
  G8 四份真源的 md5 用【受保护基线值】判 (板 / 网表 / 脚表 / BOM)
       ⇒ ★这一条同时钉住「你没有偷偷改真源」★

★★**G4 的精确口径 (★本闸与派活书措辞的差异·本闸以实测为准★)** ★:
  派活书 G4 写「只改名变体的红项里没有落表义务红」⇒ ★实测【不成立】:
  只改名变体【确实】含 1 条落表义务红 (md5 锚点), 因为 md5 锚点判的是【内容变了没有】★
  ⇒ ★本闸按【实测成立的分离关系】实现★:
    ① 只补行变体的红项 【全部】 归落表义务 ⇒ 且【一条语义红都没有】
    ② 只改名变体里 【与只补行变体同名的】 归落表义务, 【其余】 归语义破坏/反向用例
    ③ 腿 B 全量红项集合 == 只改名 ∪ 只补行 (集合并, 不多不少)
  ⇒ ★这一条若照抄派活书措辞, 本闸会【恒红】(= 判据自毁)★

用法:
    python3 SW/tools/check_onepass_legb_sw_impact.py                # 核对 (rc=0 = 九条全过)
    python3 SW/tools/check_onepass_legb_sw_impact.py --selftest      # 反向用例 (≥7 条 · 必须全 PASS)
    python3 SW/tools/check_onepass_legb_sw_impact.py --json          # 机读输出
    python3 SW/tools/check_onepass_legb_sw_impact.py --page <路径>   # 指定被检页 (★沙盒用★)

★边界 (★本闸只读真件★): 不写板 / 不落表 / 不改既有闸 / 不改既有页面 / 不改 STATE.yaml /
  不改任何人的分片 ⇒ 沙盒只落项目内 `tmp/iss370_gate_sbx/` · ★禁止写系统 /tmp★
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_LEGB_SW_IMPACT.md")
LEGB_NET_REL = os.path.join("tmp", "iss364_sbx", "netlist_v1_legB.csv")
RENAME_NET_REL = os.path.join("tmp", "iss370_sbx", "netlist_v1_rename_only.csv")
ROWADD_NET_REL = os.path.join("tmp", "iss370_sbx", "netlist_v1_rowadd_only.csv")
BASE_NET_REL = os.path.join("HW", "netlist_v1.csv")

SBX_REL = os.path.join("tmp", "iss370_gate_sbx")
GATE_TIMEOUT = 300

# ★★受保护基线 (★G8 用·★取值来自「板只改一次」那一趟开工前的受保护台账★) ★★
PROTECTED_MD5 = {
    "board_md5": "611b869e13518c3c023fb178f91a0075",
    "netlist_md5": "6aee500e60ba0732f83a9cf557ba90ab",
    "pins_md5": "9174309df1ec9411ac8e8d9e80ee386a",
    "bom_md5": "5b9993992405904a60ac96a020b375d8",
}
PROTECTED_FILES = {
    "board_md5": os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    "netlist_md5": os.path.join("HW", "netlist_v1.csv"),
    "pins_md5": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom_md5": os.path.join("HW", "BOM_v1.csv"),
}

CLASSES = ("语义破坏", "落表义务", "反向用例")
LEVELS_ALLOWED = ("官网", "实测", "媒体", "推算", "0数据")
LEVELS_FORBIDDEN = ("官方", "现场", "听说", "估计", "大概", "据说")
HANGING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认",
           "等回复", "待回复", "等回信", "等厂商确认", "待原厂", "等厂家确认")
HOLLOW = ("调整相关逻辑", "适当处理", "酌情", "视情况而定", "相关处理",
          "相应修改", "同步更新一下", "改一下", "相关逻辑", "按需调整")
SAMEBATCH_FIELDS = ("no", "file", "owner", "timing", "kind", "fix", "readback", "evidence")

BLOCK_RE = re.compile(
    r"<!--\s*ISS370-IMPACT:BEGIN\s*-->(.*?)<!--\s*ISS370-IMPACT:END\s*-->", re.S)


# ===================================================================== 观测层
def md5_of(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return ""


def _csv_rows(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _sig(r):
    return (r.get("ref", ""), r.get("net", ""), r.get("value", ""),
            r.get("type", ""), r.get("dnp", ""))


def compute_numbers(base_csv: str, legb_csv: str) -> dict:
    """★G1 的三个数: 本脚本自己算, 不许抄页里的★。"""
    b = _csv_rows(base_csv)
    l = _csv_rows(legb_csv)
    pool = {}
    for r in b:
        pool.setdefault(_sig(r), []).append(r)
    cells = 0
    cols = {}
    for r in l:
        cand = pool.get(_sig(r))
        if not cand:
            continue
        br = cand.pop(0)
        for k in br.keys():
            if (br.get(k) or "") != (r.get(k) or ""):
                cells += 1
                cols[k] = cols.get(k, 0) + 1
    return {"changed_cells": cells, "changed_columns": sorted(cols),
            "column_counts": cols, "rows_before": len(b), "rows_after": len(l)}


def _fails_of(stdout: str):
    return [ln.strip()[len("[FAIL]"):].strip()
            for ln in stdout.splitlines() if "[FAIL]" in ln]


def _run_timing(script: str, cwd: str, netlist: str = None):
    argv = [sys.executable, script]
    if netlist:
        argv += ["--netlist", netlist]
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=GATE_TIMEOUT)
    return p.returncode, p.stdout + (p.stderr or "")


def build_landing_root(root: str, netlist_src: str) -> str:
    """★落表仿真镜像根 (★全部【拷贝】·不用软链·不碰真件★)。

    ★为什么要这个: `timing_check.py` L325 那条判据直接读【盘上真源】
      (`disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)`) ⇒ `--netlist` 覆盖改不到它
      ⇒ 只跑 `--netlist` 会【少算一条落表义务红】(★实测: 15 vs 16★)
    """
    if os.path.isdir(root):
        shutil.rmtree(root)
    files = [
        ("HW/netlist_v1.csv", netlist_src),
        ("HW/SCHEMATIC_LANDING_V1_LANDED.md",
         os.path.join(PROJ, "HW", "SCHEMATIC_LANDING_V1_LANDED.md")),
        ("HW/PCB/FET3572C_PIN_TABLE.csv",
         os.path.join(PROJ, "HW", "PCB", "FET3572C_PIN_TABLE.csv")),
        ("SW/SW_MD5_BASELINE_LEDGER.md",
         os.path.join(PROJ, "SW", "SW_MD5_BASELINE_LEDGER.md")),
        ("SW/tools/check_demo_panel_spec.py",
         os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec.py")),
        ("state/issue_log.yaml", os.path.join(PROJ, "state", "issue_log.yaml")),
        ("SW/tools/timing_check.py", os.path.join(PROJ, "SW", "tools", "timing_check.py")),
    ]
    for rel, src in files:
        if not os.path.exists(src):
            continue
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    return os.path.join(root, "SW", "tools", "timing_check.py")


def observe() -> dict:
    """★把页里写的每个数/每条红都【自己实跑一遍】拿回来。"""
    obs = {"errors": []}
    base = os.path.join(PROJ, BASE_NET_REL)
    legb = os.path.join(PROJ, LEGB_NET_REL)
    rename = os.path.join(PROJ, RENAME_NET_REL)
    rowadd = os.path.join(PROJ, ROWADD_NET_REL)

    for label, p in (("腿 B 网表", legb), ("只改名变体", rename), ("只补行变体", rowadd)):
        if not os.path.exists(p):
            obs["errors"].append("沙盒缺件: %s (%s) ⇒ 判据 fail-closed" % (label, p))
    if obs["errors"]:
        obs["numbers"] = {}
        obs["legb_fails"] = []
        obs["rename_fails"] = []
        obs["rowadd_fails"] = []
        obs["landing_fails"] = []
        obs["protected"] = {}
        return obs

    obs["numbers"] = compute_numbers(base, legb)

    tc = os.path.join(PROJ, "SW", "tools", "timing_check.py")
    rc, out = _run_timing(tc, PROJ, legb)
    obs["legb_rc"] = rc
    obs["legb_fails"] = _fails_of(out)
    rc, out = _run_timing(tc, PROJ, rename)
    obs["rename_rc"] = rc
    obs["rename_fails"] = _fails_of(out)
    rc, out = _run_timing(tc, PROJ, rowadd)
    obs["rowadd_rc"] = rc
    obs["rowadd_fails"] = _fails_of(out)

    # ★落表仿真: 镜像根里【盘上真源】= 腿 B 网表 ★
    lroot = os.path.join(PROJ, SBX_REL, "land_root")
    script = build_landing_root(lroot, legb)
    rc, out = _run_timing(script, lroot, None)
    obs["landing_rc"] = rc
    obs["landing_fails"] = _fails_of(out)

    obs["protected"] = {k: md5_of(os.path.join(PROJ, v)) for k, v in PROTECTED_FILES.items()}
    return obs


# ===================================================================== 判据层
def _g(ok, msg, bad=None):
    return {"ok": bool(ok), "msg": msg, "bad": list(bad or [])}


def check_page(text: str, obs: dict) -> dict:
    res = {}

    # ---- G0 基准块 ----
    data = None
    m = BLOCK_RE.search(text)
    if not m:
        res["G0"] = _g(False, "页里找不到基准块 <!-- ISS370-IMPACT:BEGIN/END -->")
    else:
        jm = re.search(r"```json\s*(.*?)\s*```", m.group(1), re.S)
        if not jm:
            res["G0"] = _g(False, "基准块里没有 ```json 代码块")
        else:
            try:
                data = json.loads(jm.group(1))
                res["G0"] = _g(True, "基准块存在且是合法 JSON (顶层键 %d 个)" % len(data))
            except Exception as exc:
                res["G0"] = _g(False, "基准块不是合法 JSON: %s" % exc)
    if data is None:
        for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"):
            res.setdefault(k, _g(False, "G0 红 ⇒ 本条判据无法判定 (fail-closed)"))
        return res

    reds = data.get("reds") or []
    land = data.get("landing_only_reds") or []
    sb = data.get("samebatch") or []
    counts = data.get("counts") or {}

    # ---- G1 三个数 ----
    bad = []
    num = obs.get("numbers") or {}
    if obs.get("errors"):
        bad.append("; ".join(obs["errors"]))
    else:
        dc = counts.get("changed_cells")
        if dc != num.get("changed_cells"):
            bad.append("改动格数: 页里 %r ≠ 脚本实算 %r" % (dc, num.get("changed_cells")))
        cols = counts.get("changed_columns") or []
        if sorted(cols) != num.get("changed_columns"):
            bad.append("改动栏: 页里 %r ≠ 脚本实算 %r" % (sorted(cols), num.get("changed_columns")))
        if not set(cols) <= {"node1", "node2"}:
            bad.append("改动栏 ⊄ {node1,node2}: %r" % (sorted(cols),))
        for k in ("rows_before", "rows_after"):
            if counts.get(k) != num.get(k):
                bad.append("%s: 页里 %r ≠ 脚本实算 %r" % (k, counts.get(k), num.get(k)))
        if num.get("rows_after") != num.get("rows_before") + 4:
            bad.append("行数增量: 脚本实算 %r (不是 +4)" % (num.get("rows_after", 0) - num.get("rows_before", 0),))
    res["G1"] = _g(not bad, "三个数 (改动格数 %s / 改动栏 %s / 行数 %s→%s) 与脚本实算一致"
                   % (num.get("changed_cells"), num.get("changed_columns"),
                      num.get("rows_before"), num.get("rows_after")), bad)

    # ---- G2 红项集合 ----
    bad = []
    declared = [r.get("text", "") for r in reds]
    if data.get("red_count") != len(declared):
        bad.append("页里声明的红数 %r ≠ 实际列出的 %d 条" % (data.get("red_count"), len(declared)))
    if data.get("red_count") != 15:
        bad.append("红数必须是 15 (页里写的是 %r)" % (data.get("red_count"),))
    if obs.get("errors"):
        bad.append("; ".join(obs["errors"]))
    else:
        got = set(obs["legb_fails"])
        want = set(declared)
        for t in sorted(want - got):
            bad.append("页里声明但实跑【没有】这条红: %s" % t)
        for t in sorted(got - want):
            bad.append("实跑【有】但页里没声明这条红: %s" % t)
        lf = set(obs["landing_fails"])
        lw = set(declared) | {r.get("text", "") for r in land}
        for t in sorted(lf - lw):
            bad.append("落表仿真多出这条红, 页里没声明: %s" % t)
        for t in sorted(lw - lf):
            bad.append("落表仿真没有这条红, 页里声明了: %s" % t)
    res["G2"] = _g(not bad, "红项集合与实跑一致 (--netlist 口径 %d 条 + 落表仿真口径 %d 条)"
                   % (len(obs.get("legb_fails", [])), len(obs.get("landing_fails", []))), bad)

    # ---- G3 归类非空 ----
    bad = []
    for r in list(reds) + list(land):
        cl = (r.get("class") or "").strip()
        if not cl:
            bad.append("第 %s 条归类为空: %s" % (r.get("no"), (r.get("text") or "")[:60]))
        elif cl not in CLASSES:
            bad.append("第 %s 条归类 %r 不在三选一 %r 内" % (r.get("no"), cl, list(CLASSES)))
    res["G3"] = _g(not bad, "全部 %d 条红项的归类非空且 ∈ %s"
                   % (len(reds) + len(land), "/".join(CLASSES)), bad)

    # ---- G4 两类红可分离 (★核心★) ----
    bad = []
    if obs.get("errors"):
        bad.append("; ".join(obs["errors"]))
    else:
        rn = set(obs["rename_fails"])
        ra = set(obs["rowadd_fails"])
        lb = set(obs["legb_fails"])
        for r in reds:
            cl = (r.get("class") or "").strip()
            if cl not in CLASSES:
                continue            # ★归类非法是 G3 的活·这里跳过·不许两处一起红★
            t = r.get("text", "")
            if cl in ("语义破坏", "反向用例"):
                if t not in rn:
                    bad.append("第 %s 条归为 %s, 但它【不在只改名变体】的红项里: %s"
                               % (r.get("no"), cl, t[:60]))
                if t in ra:
                    bad.append("第 %s 条归为 %s, 但它【出现在只补行变体】里 ⇒ 两类红被混了: %s"
                               % (r.get("no"), cl, t[:60]))
            else:  # 落表义务
                if t not in ra:
                    bad.append("第 %s 条归为 落表义务, 但它【不在只补行变体】的红项里: %s"
                               % (r.get("no"), t[:60]))
        if lb != (rn | ra):
            only_lb = sorted(lb - (rn | ra))
            only_union = sorted((rn | ra) - lb)
            if only_lb:
                bad.append("腿 B 全量红项比【只改名 ∪ 只补行】多出: %s" % only_lb)
            if only_union:
                bad.append("腿 B 全量红项比【只改名 ∪ 只补行】少: %s" % only_union)
    res["G4"] = _g(not bad, "语义红与落表义务红可分离 (只改名 %d / 只补行 %d / 全量 %d, 并集恒等成立)"
                   % (len(obs.get("rename_fails", [])), len(obs.get("rowadd_fails", [])),
                      len(obs.get("legb_fails", []))), bad)

    # ---- G5 同批清单 8 字段 ----
    bad = []
    for it in sb:
        no = it.get("no", "?")
        for f in SAMEBATCH_FIELDS:
            if f == "no":
                continue
            v = it.get(f)
            if v is None or not str(v).strip():
                bad.append("第 %s 件的字段 %r 为空" % (no, f))
        owner = str(it.get("owner") or "")
        timing = str(it.get("timing") or "")
        fix = str(it.get("fix") or "")
        file_rel = str(it.get("file") or "")
        if owner and file_rel.startswith(("HW/", "state/")):
            if "跨域" not in owner or "不是 SW 的域" not in owner:
                bad.append("第 %s 件改的是 %s ⇒ 归属必须写「跨域 · 不是 SW 的域」, 现在写的是 %r"
                           % (no, file_rel, owner))
        if timing and not ("必须同批" in timing or "可板后补" in timing):
            bad.append("第 %s 件的时序 %r 不在 {必须同批, 可板后补} 内" % (no, timing))
        if fix:
            for h in HOLLOW:
                if h in fix:
                    bad.append("第 %s 件的改法含空洞词 %r (不许写「调整相关逻辑」这种废话)" % (no, h))
                    break
            if len(fix.strip()) < 20:
                bad.append("第 %s 件的改法太短 (%d 字) ⇒ 照着干不了" % (no, len(fix.strip())))
    res["G5"] = _g(not bad, "§2 同批清单 %d 件 · 每件 8 字段齐全 + 跨域归属正确 + 改法无空洞词"
                   % len(sb), bad)

    # ---- G6 证据等级白名单 ----
    bad = []
    for tag in LEVELS_FORBIDDEN:
        if ("[%s]" % tag) in text:
            bad.append("正文出现禁用证据等级 [%s]" % tag)
    for it in sb:
        ev = str(it.get("evidence") or "").strip()
        core = ev.strip("[]").strip()
        if ev and core not in LEVELS_ALLOWED:
            bad.append("第 %s 件的证据等级 %r 不在白名单 %r 内" % (it.get("no"), ev, list(LEVELS_ALLOWED)))
    res["G6"] = _g(not bad, "证据等级全在五级白名单 %s" % (list(LEVELS_ALLOWED),), bad)

    # ---- G7 挂起措辞 ----
    bad = []
    for h in HANGING:
        if h in text:
            bad.append("正文出现挂起措辞 %r" % h)
    res["G7"] = _g(not bad, "正文零挂起措辞 (%d 个禁词全扫)" % len(HANGING), bad)

    # ---- G8 受保护基线 ----
    bad = []
    decl = data.get("protected") or {}
    for k, want in PROTECTED_MD5.items():
        got_disk = (obs.get("protected") or {}).get(k, "")
        if got_disk != want:
            bad.append("%s 盘上 md5 = %r ≠ 受保护基线 %r ⇒ 真源被改了" % (k, got_disk, want))
        if decl.get(k) != want:
            bad.append("%s 页里声明的 md5 %r ≠ 受保护基线 %r" % (k, decl.get(k), want))
    res["G8"] = _g(not bad, "板/网表/脚表/BOM 四份真源 md5 逐字节等于受保护基线", bad)

    return res


# ===================================================================== 自检
def _mutate_json(text: str, fn) -> str:
    m = BLOCK_RE.search(text)
    if not m:
        return text
    jm = re.search(r"```json\s*(.*?)\s*```", m.group(1), re.S)
    if not jm:
        return text
    data = json.loads(jm.group(1))
    fn(data)
    new = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
    return text[:m.start(1)] + new + text[m.end(1):]


def _selftest(page_text: str, obs: dict) -> int:
    cases = []

    def add(name, target, mutate):
        cases.append((name, target, mutate))

    def m_del_red(d):
        d["reds"] = [r for r in d["reds"] if "F4 实读: ADC 节点 @4.2V" not in r.get("text", "")]

    def m_empty_class(d):
        for r in d["reds"]:
            if "F4 实读: ADC 节点 @4.2V" in r.get("text", ""):
                r["class"] = ""

    def m_count_14(d):
        d["red_count"] = 14

    def m_owner_empty(d):
        d["samebatch"][0]["owner"] = ""

    def m_timing_empty(d):
        d["samebatch"][0]["timing"] = ""

    def m_cells_195(d):
        d["counts"]["changed_cells"] = 195

    def m_class_swap(d):
        for r in d["reds"]:
            if "F4 实读: ADC 节点 @4.2V" in r.get("text", ""):
                r["class"] = "落表义务"

    def m_evidence_official(d):
        d["samebatch"][0]["evidence"] = "[官方]"

    def m_hollow_fix(d):
        d["samebatch"][0]["fix"] = "调整相关逻辑"

    add("① 删掉 §1 第 10 条红 (F4 实读: ADC 节点 @4.2V) ⇒ G2 红, 其余仍绿",
        "G2", lambda t: _mutate_json(t, m_del_red))
    add("② 把 §1 某条红的归类清空 ⇒ G3 红, 其余仍绿",
        "G3", lambda t: _mutate_json(t, m_empty_class))
    add("③ 把 §1 的红数 15 改成 14 ⇒ G2 红, 其余仍绿",
        "G2", lambda t: _mutate_json(t, m_count_14))
    add("④ 把 §2 第 1 件的「归属」清空 ⇒ G5 红, 其余仍绿",
        "G5", lambda t: _mutate_json(t, m_owner_empty))
    add("⑤ 把 §2 第 1 件的「时序」清空 ⇒ G5 红, 其余仍绿",
        "G5", lambda t: _mutate_json(t, m_timing_empty))
    add("⑥ 把 §0 的「改动格数 196」改成 195 ⇒ G1 红, 其余仍绿",
        "G1", lambda t: _mutate_json(t, m_cells_195))
    add("⑦ 正文塞「等原厂回信」⇒ G7 红, 其余仍绿",
        "G7", lambda t: t + "\n\n等原厂回信\n")
    add("⑧ 把 §2 第 1 件的证据等级写成 [官方] ⇒ G6 红, 其余仍绿",
        "G6", lambda t: _mutate_json(t, m_evidence_official))
    add("⑨ 把 §2 第 1 件的「改法」换成「调整相关逻辑」⇒ G5 红, 其余仍绿",
        "G5", lambda t: _mutate_json(t, m_hollow_fix))
    add("⑩ 把 §1 某条【语义破坏】的归类改成「落表义务」⇒ G4 红 (★抓两类红混为一谈★), 其余仍绿",
        "G4", lambda t: _mutate_json(t, m_class_swap))

    npass = 0
    print("=== ISS-370 · 腿 B ⇒ SW 侧影响面闸 · 反向自检 (%d 条) ===" % len(cases))
    for name, target, mutate in cases:
        try:
            mutated = mutate(page_text)
            r = check_page(mutated, obs)
        except Exception as exc:
            print("  ❌ %s ⇒ 抛异常: %s" % (name, exc))
            continue
        reds = sorted(k for k, v in r.items() if not v["ok"])
        if reds == [target]:
            print("  ✅ PASS  %s" % name)
            npass += 1
        else:
            print("  ❌ FAIL  %s" % name)
            print("      期望只有 %s 红, 实际红项 = %s" % (target, reds))
            for k in reds:
                for b in r[k]["bad"][:4]:
                    print("        [%s] %s" % (k, b))
    print("\nSELFTEST %d/%d 通过" % (npass, len(cases)))
    return 0 if npass == len(cases) else 1


# ===================================================================== main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--page", default=None, help="被检页路径 (默认 SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md)")
    ap.add_argument("--root", default=PROJ, help="项目根 (默认本脚本上两级)")
    args = ap.parse_args()

    page = args.page or os.path.join(PROJ, PAGE_REL)
    if not os.path.exists(page):
        print("❌ 被检页不存在: %s" % page)
        return 2
    with open(page, encoding="utf-8") as f:
        text = f.read()

    obs = observe()

    if args.selftest:
        return _selftest(text, obs)

    res = check_page(text, obs)
    order = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
    if args.json:
        print(json.dumps({k: res[k] for k in order}, ensure_ascii=False, indent=2))
        return 0 if all(res[k]["ok"] for k in order) else 1

    print("=" * 78)
    print("ISS-370 · 「板那一趟」腿 B ⇒ SW 侧影响面闸")
    print("  被检页 = %s" % page)
    print("  沙盒   = %s (★项目盘·不写系统 /tmp★)" % os.path.join(PROJ, SBX_REL))
    print("=" * 78)
    npass = 0
    for k in order:
        v = res[k]
        npass += 1 if v["ok"] else 0
        print("  [%s] %s · %s" % ("PASS" if v["ok"] else "FAIL", k, v["msg"]))
        for b in v["bad"]:
            print("        ⚠ %s" % b)
    print("\n闸结果 %d/%d 通过, rc=%d" % (npass, len(order), 0 if npass == len(order) else 1))
    return 0 if npass == len(order) else 1


if __name__ == "__main__":
    raise SystemExit(main())
