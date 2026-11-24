#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-397 · mech-lead · `FTS` 座体三量 (绝缘体高 Z / 外形宽 X / 外形深 Y) 收样作业包 · 机器闸

★**本闸只【看作业包有没有把「怎么量」写死 + 三量实测档有没有被偷升级】, 不代落任何结论** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链** ★

────────────────────────────────────────────────────────────────────────────────
★★【本闸的预期读数 = rc=1 (红)】★★
  ★**红的是【现状】(三量【实测档】仍 `[0数据]` ⇒ 收样尚未发生), 不是闸故障** ★
  ★⇒ 本单【刻意不修现状】⇒ ★**不许为了让它绿而放宽判据** ★
  ★⇒ 绿的条件只有一个: 三量实测档真的升到 `[实测]` 且原始读数在盘 (§2.4 充要条件) ★
────────────────────────────────────────────────────────────────────────────────

判据:
  A  真相页 §1~§9 九节齐全 (缺一节 ⇒ 红)
  B  ★★命门★★ 三量各自的【当前证据等级】字段在位, 且 ★**现况 = `[0数据]` 时必须仍写 `[0数据]`**
     ⇒ 谁敢把 `[0数据]` 偷写成 `[官网]`/`[实测]` ⇒ 立刻红 (且点名是哪一个量)
     ⇒ 判据 B 自己实读 `logs/iss397/fts_seat_sample_measurements.json` 交叉对账:
        记录不在盘 ⇒ 实测档必须 `[0数据]`; 记录在盘 ⇒ 实测档必须 `[实测]` 且与记录逐格对得上
  C  量具 + 容差 + 「3 次取中位数」+ 极差判据 四件在位 (缺任一 ⇒ 红)
  D  §5 三处回填落点 + §6 三方分工 三行在位 (★「收样必须在投板前」这一句必须在★)
  E  §7 三种降级路径齐全, 且 ★**降级路径里明写「不许用降级刷绿」** ★
  F  零写板 / 零落表 / 零挂链 / 已签收件 md5 同基线 (★同族闸的老口径★)

用法:
  python3 MECH/check_fts_seat_sample_plan.py              # 裸跑, rc=1 = 现状红 (三量实测档仍 [0数据])
  python3 MECH/check_fts_seat_sample_plan.py --selftest   # 反向用例, 末行 ALL TESTS PASS
  python3 MECH/check_fts_seat_sample_plan.py --emit        # 打印真相页机器块 (JSON)
  python3 MECH/check_fts_seat_sample_plan.py --root DIR    # 指定树 (反向用例在 <root>/tmp/iss397/sbx/selftest/ 上做)

★【沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss397/sbx/selftest/` (★不许写系统 `/tmp`·不许用硬链接★)
             ★路径全部从本闸自己的 `ROOT` 推 ⇒ 环境无关★
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_REL = "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"
BLOCK_BEGIN = "<!-- MECH-FTS-SEAT-SAMPLE-MEASURE-PLAN-JSON-BEGIN -->"
BLOCK_END = "<!-- MECH-FTS-SEAT-SAMPLE-MEASURE-PLAN-JSON-END -->"
RECORD_REL = os.path.join("logs", "iss397", "fts_seat_sample_measurements.json")

PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
NETLIST_REL = "HW/netlist_v1.csv"
PINS_REL = "HW/netlist_v1_pins.csv"
BOM_REL = "HW/BOM_v1.csv"
GATE_REL = "state/gate_check.py"

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = "4940213"
TABLE_BASELINE = {
    NETLIST_REL: "6aee500e60ba0732f83a9cf557ba90ab",
    PINS_REL: "9174309df1ec9411ac8e8d9e80ee386a",
    BOM_REL: "5b9993992405904a60ac96a020b375d8",
}
# ★★已签收件 md5 基线 (★本单零改既有闸/既有页正文 ⇒ 收尾时必须逐个同基线★) ★★
SIGNED_OFF_MD5 = {
    "MECH/check_fts_seat_body_geometry.py": "1cdc6e9838419647e018c9a4c41319a2",
    "MECH/check_fts_vs_generic_courtyard_delta.py": "8f8424a5e632fa3d223271850109c6d0",
    "MECH/check_onepass_mech_release.py": "bd90741d38c6cd362d83e1f205cc21c5",
    "MECH/check_onepass_mech_sync.py": "5247486a6739d9b0cd5cf9a886c771e8",
    "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md": "15697668d10368e971710069c9b73994",
    "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md": "0cb3ff2de940522b467ca3b01feda11c",
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
QUANT_KEYS = ("insulator_height_z", "seat_body_width_x", "seat_body_depth_y")
QUANT_LABEL = {
    "insulator_height_z": "绝缘体高 Z",
    "seat_body_width_x": "外形宽 X",
    "seat_body_depth_y": "外形深 Y",
}
PARTS = ("FTS-104-01-F-S", "FTS-102-01-F-S")
SECTIONS = ("§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9")
SANDBOX_REL = os.path.join("tmp", "iss397", "sbx", "selftest")
# ★★降级期间不许出现的「把闸刷绿」措辞 ★★
GREEN_WASH = ("降级刷绿", "用降级把闸刷绿")
# ★★零挂起措辞 (★查不到 ⇒ 自己查 + 标等级 + 写降级方案; 不许挂外部依赖★) ★★
PENDING = ("等原厂回信", "待原厂回信", "待外部确认", "等待原厂", "等放行", "待确认")


# ==================================================================================================
# 基础工具
# ==================================================================================================
def p(root: str, rel: str) -> str:
    return os.path.join(root, rel)


def p3(root: str, a: str, b: str) -> str:
    return os.path.join(root, a, b)


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path: str, s: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(s)


def md5_of(path: str) -> str:
    return subprocess.run(["md5sum", path], capture_output=True, text=True).stdout.split()[0]


def stat_of(path: str) -> str:
    return subprocess.run(["stat", "-c", "%y", path], capture_output=True, text=True).stdout.strip()


def f4(x) -> str:
    return "%.4f" % float(x)


def extract_json_fence(text: str, begin: str, end: str):
    i = text.find(begin)
    j = text.find(end)
    if i < 0 or j < 0:
        return None
    seg = text[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


# ==================================================================================================
# 事实读取
# ==================================================================================================
class Facts:
    def __init__(self, root: str):
        self.root = root
        self.page_path = p(root, PAGE_REL)
        self.page = read_text(self.page_path) if os.path.isfile(self.page_path) else ""
        self.block = extract_json_fence(self.page, BLOCK_BEGIN, BLOCK_END)
        self.record_path = p(root, RECORD_REL)
        self.record = None
        self.record_exists = os.path.isfile(self.record_path)
        if self.record_exists:
            try:
                self.record = json.loads(read_text(self.record_path))
            except Exception:
                self.record = None

    def record_complete(self) -> bool:
        """★原始记录是否【完整】(6 格 × 3 读数 + 中位数 + 极差 + 量具 + 日期 + 样件号 + md5)★"""
        if not isinstance(self.record, dict):
            return False
        cells = self.record.get("cells")
        if not isinstance(cells, dict):
            return False
        need = ("readings", "median", "range", "gauge", "measured_at",
                "operator", "sample_id", "photo_md5", "record_md5")
        for part in PARTS:
            for q in QUANT_KEYS:
                c = cells.get("%s|%s" % (part, q))
                if not isinstance(c, dict):
                    return False
                for k in need:
                    if not str(c.get(k) or "").strip():
                        return False
                rd = c.get("readings")
                if not isinstance(rd, list) or len(rd) != 3:
                    return False
                try:
                    vals = sorted(float(x) for x in rd)
                except Exception:
                    return False
                if f4(vals[1]) != f4(c.get("median")):
                    return False
                if f4(vals[-1] - vals[0]) != f4(c.get("range")):
                    return False
                if (vals[-1] - vals[0]) > 0.05 + 1e-9:
                    return False
        return True

    def record_median(self, part: str, q: str):
        cells = (self.record or {}).get("cells") or {}
        c = cells.get("%s|%s" % (part, q)) or {}
        return c.get("median")


# ==================================================================================================
# 闸
# ==================================================================================================
class Gate:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.f = Facts(self.root)
        self.results = []
        self.notes = []

    def chk(self, kid, ok, msg):
        self.results.append((kid, bool(ok), msg))

    # ---------------- A: 九节齐全 ----------------
    def a(self):
        page = self.f.page
        # ★★必须行首精确匹配 `## ★§N` (§10 不得充作 §1; `### ★§9-①` 也不得充作 §9) ★★
        lack = []
        for s in SECTIONS:
            if not re.search(r"^## ★" + re.escape(s) + r"\b", page, re.M):
                lack.append(s)
        self.chk("A.1", not lack, "真相页 §1~§9 缺 (须行首 `## ★§N`): %s" % lack)
        self.chk("A.2", self.f.block is not None,
                 "★机器块缺失或不可解析 (%s ... %s)" % (BLOCK_BEGIN, BLOCK_END))

    # ---------------- B: ★★命门★★ 当前证据等级不许被偷升级 ----------------
    def b(self):
        blk = self.f.block or {}
        tq = blk.get("three_quantities") or {}
        lack = [q for q in QUANT_KEYS if not isinstance(tq.get(q), dict)]
        self.chk("B.1", not lack, "★三量缺项: %s" % lack)
        if lack:
            return
        complete = self.f.record_complete()
        bad_ev = []
        bad_hold = []
        bad_match = []
        for q in QUANT_KEYS:
            cell = tq[q]
            ev = str(cell.get("measured_evidence") or "").strip()
            if not ev:
                bad_ev.append("%s: 缺 measured_evidence 字段" % QUANT_LABEL[q])
                continue
            tags = re.findall(r"\[[^\]]+\]", ev)
            if not tags:
                bad_ev.append("%s: measured_evidence 无证据标记 (%r)" % (QUANT_LABEL[q], ev))
                continue
            for tg in tags:
                if tg not in EVIDENCE_WHITELIST:
                    bad_ev.append("%s: %s 不在五级白名单里" % (QUANT_LABEL[q], tg))
            # ★★现况 = [0数据] 时必须仍写 [0数据] (★不许偷写成 [官网]/[实测]★) ★★
            if not complete and ev != "[0数据]":
                bad_hold.append("%s: 实测档现况是 [0数据] (原始记录不在盘/不完整), 页面却写 %r "
                                "⇒ ★★谁敢把 `[0数据]` 偷写成 `[官网]`/`[实测]` 立刻红★★"
                                % (QUANT_LABEL[q], ev))
            # ★记录在盘 ⇒ 实测档必须 [实测] 且逐格对得上 ★
            if complete:
                if ev != "[实测]":
                    bad_match.append("%s: 原始记录已完整, 实测档却写 %r (应为 [实测])"
                                     % (QUANT_LABEL[q], ev))
                else:
                    for part in PARTS:
                        want = self.f.record_median(part, q)
                        got = cell.get("measured_value")
                        if isinstance(got, dict):
                            got = got.get(part)
                        if want is None or got is None:
                            bad_match.append("%s/%s: 记录有, 页面没有 measured_value" % (QUANT_LABEL[q], part))
                        elif f4(got) != f4(want):
                            bad_match.append("%s/%s: 页面 measured_value %s ≠ 记录中位数 %s"
                                             % (QUANT_LABEL[q], part, f4(got), f4(want)))
        self.chk("B.2", not bad_ev, "★实测档证据等级越界或缺失: %s" % bad_ev)
        self.chk("B.3", not bad_hold, "★★[0数据] 被偷升级 (★本闸命门★): %s" % bad_hold)
        self.chk("B.4", not bad_match, "★实测档与原始记录对不上: %s" % bad_match)
        # ★标称档与实测档不许混: 标称档必须 [官网] 且不许带 measured_evidence 的值 ★
        mixed = []
        for q in QUANT_KEYS:
            cell = tq[q]
            nev = str(cell.get("nominal_evidence") or "").strip()
            if "[官网]" not in nev:
                mixed.append("%s: 标称档 %r 不含 [官网] (★标称档被降级 ⇒ 判决链失据★)" % (QUANT_LABEL[q], nev))
        self.chk("B.5", not mixed, "★标称档降级: %s" % mixed)
        # ---------------- B.6 ★★★本闸【预期读数 = rc=1】的那一条★★★ ----------------
        # ★★三量的【实测档】必须真的升到 [实测] 且原始记录完整在盘★★
        # ★★⇒ 现况 (三量实测档仍 [0数据]·收样未发生) ⇒ 本条判红 = 【红的是现状, 不是闸故障】★★
        if complete:
            self.chk("B.6", True,
                     "★三量实测档已升 [实测] 且原始记录完整在盘 (极差全 ≤ 0.05·中位数逐格对得上)")
        else:
            still = [QUANT_LABEL[q] for q in QUANT_KEYS
                     if str((tq[q] or {}).get("measured_evidence") or "").strip() != "[实测]"]
            why = ("原始记录 %s 不在盘/不完整" % RECORD_REL) if not self.f.record_exists \
                else ("原始记录 %s 在盘但不完整 (6 格 × 3 读数 + 中位数 + 极差 + 量具 + 日期 + 样件号 + md5)" % RECORD_REL)
            self.chk("B.6", False,
                     "★★三量【实测档】仍不是 [实测] (未升的量: %s) ⇒ 本单刻意不修现状 ⇒ "
                     "★**红的是【现状】, 不是闸故障**★ ★★ (%s) ⇒ ★**不许为了让它绿而放宽判据** ★"
                     % (", ".join(still) if still else "无", why))

    # ---------------- C: 量具 / 容差 / 3 次取中位数 / 极差判据 ----------------
    def c(self):
        blk = self.f.block or {}
        g = blk.get("gauge") or {}
        lack = []
        if not any(str(x) in ("0.02", "0.02 ") or str(x).startswith("0.02") for x in (g.get("caliper_resolutions_mm") or [])):
            lack.append("游标卡尺分辨率 0.02 mm")
        if not any(str(x).startswith("0.05") for x in (g.get("caliper_resolutions_mm") or [])):
            lack.append("游标卡尺分辨率 0.05 mm")
        if not g.get("depth_height_gauge"):
            lack.append("深度尺/高度尺 (量绝缘体高)")
        if int(g.get("repeat_count") or 0) != 3:
            lack.append("每量 3 次")
        if "中位数" not in str(g.get("aggregate") or ""):
            lack.append("取中位数")
        if not g.get("record_raw_readings"):
            lack.append("记录原始读数")
        if not str(g.get("range_threshold_mm") or "").startswith("0.05"):
            lack.append("极差判据阈值 0.05")
        if "重测" not in str(g.get("range_fail_action") or ""):
            lack.append("极差超标后的动作 (重测并记原因)")
        self.chk("C.1", not lack, "★量具/容差/3 次取中位数/极差判据 四件缺: %s" % lack)
        page = self.f.page
        miss_txt = [w for w in ("3 次", "中位数", "极差", "0.05")
                    if w not in page]
        self.chk("C.2", not miss_txt, "★正文缺关键字: %s" % miss_txt)

    # ---------------- D: §5 三处回填落点 + §6 三方分工 ----------------
    def d(self):
        blk = self.f.block or {}
        tg = blk.get("backfill_targets") or []
        self.chk("D.1", len(tg) >= 3,
                 "★§5 回填落点不足 3 处 (现 %d)" % len(tg))
        files = " ".join(str(t.get("file") or "") for t in tg)
        miss_files = [w for w in ("BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
                                  "BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
                                  "check_fts_seat_body_geometry.py") if w not in files]
        self.chk("D.2", not miss_files, "★§5 回填落点缺 %s" % miss_files)
        roles = blk.get("roles") or []
        parties = " ".join(str(r.get("party") or "") for r in roles)
        miss_roles = [w for w in ("mech-lead", "hw-lead", "main") if w not in parties]
        self.chk("D.3", not miss_roles, "★§6 三方分工缺 %s" % miss_roles)
        hc = str(blk.get("hard_constraint") or "")
        self.chk("D.4", "投板前" in hc, "★§6 硬约束必须含『投板前』 (现 %r)" % hc)
        self.chk("D.5", "投板前" in self.f.page and "白投" in self.f.page,
                 "★正文缺『收样必须在投板前 · 晚了 = 那趟白投』这句硬约束")

    # ---------------- E: §7 三种降级路径 + 不许用降级刷绿 ----------------
    def e(self):
        blk = self.f.block or {}
        paths = blk.get("degradation_paths") or []
        trig = " ".join(str(d.get("trigger") or "") for d in paths)
        lack = [t for t in ("量不到", "样件没到", "网表没落") if t not in trig]
        self.chk("E.1", len(paths) >= 3 and not lack,
                 "★§7 降级路径必须三条齐全 (量不到/样件没到/网表没落), 缺: %s" % lack)
        # ★降级路径的实测档等级必须仍是 [0数据] ★
        bad = []
        for d in paths:
            ev = str(d.get("measured_evidence_after") or "").strip()
            if ev != "[0数据]":
                bad.append("%s: 降级后实测档写 %r (降级后必须仍 [0数据])" % (d.get("id"), ev))
        self.chk("E.2", not bad, "★降级路径把实测档刷成了非 [0数据]: %s" % bad)
        ngw = str(blk.get("no_green_washing") or "")
        self.chk("E.3", any(w in ngw for w in GREEN_WASH),
                 "★机器块必须明写『不许用降级刷绿』 (现 %r)" % ngw)
        page = self.f.page
        self.chk("E.4", any(w in page for w in GREEN_WASH),
                 "★正文必须明写『不许用降级刷绿』")
        hits = [w for w in PENDING if w in page]
        self.chk("E.5", not hits, "★页面含零挂起禁语 %r" % hits)

    # ---------------- F: 零写板 / 零落表 / 零挂链 / 已签收件 md5 同基线 ----------------
    def f_(self):
        pcb = p(self.root, PCB_REL)
        if os.path.isfile(pcb):
            got = md5_of(pcb)
            self.chk("F.1", got == BOARD_MD5,
                     "板 md5 %s ≠ 基线 %s (零写板被破坏)" % (got, BOARD_MD5))
            self.chk("F.2", stat_of(pcb).startswith(BOARD_MTIME),
                     "板 mtime %s ≠ 基线 %s" % (stat_of(pcb), BOARD_MTIME))
            self.chk("F.3", os.path.getsize(pcb) == int(BOARD_SIZE),
                     "板 size %d ≠ 基线 %s" % (os.path.getsize(pcb), BOARD_SIZE))
        else:
            self.chk("F.1", False, "板文件不在盘: %s" % PCB_REL)
        for rel, want in TABLE_BASELINE.items():
            f = p(self.root, rel)
            if not os.path.isfile(f):
                self.chk("F.4", False, "表文件不在盘: %s" % rel)
                continue
            got = md5_of(f)
            self.chk("F.4", got == want, "%s md5 %s ≠ 基线 %s (零落表被破坏)" % (rel, got, want))
        gf = p(self.root, GATE_REL)
        if os.path.isfile(gf):
            txt = read_text(gf)
            self.chk("F.5", "check_fts_seat_sample_plan" not in txt,
                     "★本闸被挂进了 state/gate_check.py (★本单零挂链·挂不挂归 main★)")
        else:
            self.chk("F.5", False, "state/gate_check.py 不在盘")
        for rel, want in SIGNED_OFF_MD5.items():
            f = p(self.root, rel)
            if not os.path.isfile(f):
                self.chk("F.6", False, "已签收件不在盘: %s" % rel)
                continue
            got = md5_of(f)
            self.chk("F.6", got == want,
                     "★已签收件 %s md5 %s ≠ 基线 %s (本单零改既有闸/既有页正文★)" % (rel, got, want))

    # ---------------- run ----------------
    def run(self):
        self.a()
        self.b()
        self.c()
        self.d()
        self.e()
        self.f_()
        return self.results


# ==================================================================================================
# 沙盒 / 反向用例
# ==================================================================================================
def make_sandbox(root: str, case: str) -> str:
    sb = p3(root, SANDBOX_REL, case)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    os.makedirs(sb, exist_ok=True)
    # ★只复制本闸要读的那几件 (★老字未动的既有页用副本, 沙盒里改副本不碰真页面★) ★
    for rel in (PAGE_REL, RECORD_REL, PCB_REL, NETLIST_REL, PINS_REL, BOM_REL, GATE_REL):
        src = p(root, rel)
        if not os.path.isfile(src):
            continue
        dst = p(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)          # ★不许硬链接 (cp -al)★
    for rel in SIGNED_OFF_MD5:
        src = p(root, rel)
        if not os.path.isfile(src):
            continue
        dst = p(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return sb


def block_mutate(sb: str, fn) -> None:
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    i = txt.find(BLOCK_BEGIN)
    j = txt.find(BLOCK_END)
    seg = txt[i:j]
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", seg, re.S)
    if not m:
        raise AssertionError("block_mutate: 找不到机器块 json fence")
    data = json.loads(m.group(1))
    fn(data)
    new_seg = seg[:m.start()] + "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```" + seg[m.end():]
    write_text(path, txt[:i] + new_seg + txt[j:])


def page_replace(sb: str, old: str, new: str) -> None:
    path = p(sb, PAGE_REL)
    txt = read_text(path)
    if old not in txt:
        raise AssertionError("page_replace: 找不到 %r" % old[:60])
    write_text(path, txt.replace(old, new, 1))


def write_fake_record(sb: str) -> None:
    """★造一份「三量已实测填齐」的假记录 (★只落沙盒·不许落真 logs/★)★"""
    cells = {}
    vals = {"insulator_height_z": "0.8600", "seat_body_width_x": None, "seat_body_depth_y": "2.1600"}
    for part in PARTS:
        for q in QUANT_KEYS:
            base = vals[q]
            if base is None:
                base = "5.0800" if part == "FTS-104-01-F-S" else "2.5400"
            rd = [base, base, base]
            cells["%s|%s" % (part, q)] = {
                "readings": rd, "median": base, "range": "0.0000",
                "gauge": "游标卡尺 0.02mm #A3", "measured_at": "2026-12-01",
                "operator": "mech-lead", "sample_id": "板只改一次-第1块",
                "photo_md5": "0" * 32, "record_md5": "0" * 32, "retest_note": "无",
            }
    write_text(p(sb, RECORD_REL), json.dumps(
        {"issue": "ISS-397", "sample_id": "板只改一次-第1块", "cells": cells},
        ensure_ascii=False, indent=2))


def fill_measured(sb: str) -> None:
    """★把三量的实测档在沙盒页里升级成 [实测] 并填上中位数 (★正向对照用★)★"""
    def f(d):
        for part in PARTS:
            for q in QUANT_KEYS:
                cell = d["three_quantities"][q]
                base = {"insulator_height_z": "0.8600", "seat_body_depth_y": "2.1600"}.get(q)
                if base is None:
                    base = "5.0800" if part == "FTS-104-01-F-S" else "2.5400"
                cell["measured_evidence"] = "[实测]"
                cell["measured_readings"] = [base, base, base]
                if isinstance(cell.get("measured_value"), dict):
                    cell["measured_value"][part] = base
                else:
                    cell["measured_value"] = {part: base}
    block_mutate(sb, f)


def selftest(root: str) -> int:
    cases = []

    def case(name, desc, mutate, expect):
        cases.append((name, desc, mutate, expect))

    # ── 01 ★★命门★★ 把实测档偷写成 [官网] ⇒ 必须红 (B) ──
    def m01(sb):
        def f(d):
            d["three_quantities"]["seat_body_depth_y"]["measured_evidence"] = "[官网]"
        block_mutate(sb, f)
    case("c01_steal_measured_as_official",
         "★★把 [0数据] 偷写成 [官网] ⇒ 必须红 (B.3 命门)", m01, "B.3")

    # ── 02 ★★命门★★ 把实测档偷写成 [实测] (无记录) ⇒ 必须红 (B) ──
    def m02(sb):
        def f(d):
            d["three_quantities"]["insulator_height_z"]["measured_evidence"] = "[实测]"
        block_mutate(sb, f)
    case("c02_steal_measured_as_tested",
         "★★把 [0数据] 偷写成 [实测] (无原始记录) ⇒ 必须红 (B.3 命门)", m02, "B.3")

    # ── 03 删掉容差 (极差阈值) ⇒ 必须红 (C) ──
    def m03(sb):
        def f(d):
            d["gauge"]["range_threshold_mm"] = ""
        block_mutate(sb, f)
    case("c03_drop_range_threshold",
         "删掉极差判据阈值 ⇒ 必须红 (C.1)", m03, "C.1")

    # ── 04 删掉「3 次取中位数」⇒ 必须红 (C) ──
    def m04(sb):
        def f(d):
            d["gauge"]["repeat_count"] = 1
            d["gauge"]["aggregate"] = "取第一个"
        block_mutate(sb, f)
    case("c04_drop_repeat_median",
         "把「3 次取中位数」改成 1 次取第一个 ⇒ 必须红 (C.1)", m04, "C.1")

    # ── 05 删掉一种降级路径 ⇒ 必须红 (E) ──
    def m05(sb):
        def f(d):
            d["degradation_paths"] = d["degradation_paths"][:2]
        block_mutate(sb, f)
    case("c05_drop_degradation_path",
         "删掉一种降级路径 ⇒ 必须红 (E.1)", m05, "E.1")

    # ── 06 降级路径把实测档刷绿 ⇒ 必须红 (E) ──
    def m06(sb):
        def f(d):
            d["degradation_paths"][0]["measured_evidence_after"] = "[实测]"
        block_mutate(sb, f)
    case("c06_degradation_grades_green",
         "★降级路径里把实测档写成 [实测] ⇒ 必须红 (E.2 降级刷绿)", m06, "E.2")

    # ── 07 删掉「不许用降级刷绿」⇒ 必须红 (E) ──
    def m07(sb):
        def f(d):
            d["no_green_washing"] = "降级期间照常"
        block_mutate(sb, f)
    case("c07_drop_no_green_wash",
         "删掉机器块里的『不许用降级刷绿』⇒ 必须红 (E.3)", m07, "E.3")

    # ── 08 删掉「投板前」硬约束 ⇒ 必须红 (D) ──
    def m08(sb):
        def f(d):
            d["hard_constraint"] = "收样在装配之后"
        block_mutate(sb, f)
    case("c08_drop_pre_board_hard_constraint",
         "★删掉『收样必须在投板前』硬约束 ⇒ 必须红 (D.4)", m08, "D.4")

    # ── 09 删掉三方分工的一行 ⇒ 必须红 (D) ──
    def m09(sb):
        def f(d):
            d["roles"] = [r for r in d["roles"] if r.get("party") != "hw-lead"]
        block_mutate(sb, f)
    case("c09_drop_role_hw_lead",
         "删掉三方分工里的 hw-lead ⇒ 必须红 (D.3)", m09, "D.3")

    # ── 10 删掉 §5 一处回填落点 ⇒ 必须红 (D) ──
    def m10(sb):
        def f(d):
            d["backfill_targets"] = d["backfill_targets"][:2]
        block_mutate(sb, f)
    case("c10_drop_backfill_target",
         "删掉 §5 一处回填落点 ⇒ 必须红 (D.1)", m10, "D.1")

    # ── 11 删掉 §9 一节 ⇒ 必须红 (A) ──
    def m11(sb):
        page_replace(sb, "## ★§9 未决项", "## ★§ 未决项")
    case("c11_drop_section_9",
         "把 §9 的节标题抹掉 ⇒ 必须红 (A.1)", m11, "A.1")

    # ── 11b 把 §10 冒充成 §1 ⇒ 必须红 (A) ──
    def m11b(sb):
        page_replace(sb, "## ★§1 口径声明", "## ★§10 口径声明")
    case("c11b_section_10_impersonates_1",
         "★把 §1 改成 §10 ⇒ 必须红 (A.1 行首精确匹配)", m11b, "A.1")

    # ── 12 板 md5 被动 ⇒ 必须红 (F) ──
    def m12(sb):
        with open(p(sb, PCB_REL), "ab") as fh:
            fh.write(b"\n")
    case("c12_board_md5_changed",
         "沙盒板被追加一字节 ⇒ 必须红 (F.1)", m12, "F.1")

    # ── 13 本闸被挂进 gate_check.py ⇒ 必须红 (F) ──
    def m13(sb):
        with open(p(sb, GATE_REL), "a", encoding="utf-8") as fh:
            fh.write("\n# check_fts_seat_sample_plan\n")
    case("c13_chained_into_gate_check",
         "把本闸挂进 state/gate_check.py ⇒ 必须红 (F.5)", m13, "F.5")

    # ── 14 已签收闸源码被改 ⇒ 必须红 (F) ──
    def m14(sb):
        f = p(sb, "MECH/check_fts_seat_body_geometry.py")
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("\n# tampered\n")
    case("c14_signed_off_gate_tampered",
         "★已签收闸源码被改 ⇒ 必须红 (F.6)", m14, "F.6")

    # ── 15 证据等级越界 ⇒ 必须红 (B) ──
    def m15(sb):
        def f(d):
            d["three_quantities"]["seat_body_width_x"]["measured_evidence"] = "[猜测]"
        block_mutate(sb, f)
    case("c15_bad_evidence_tag",
         "把证据等级写成六级之外的词 `[猜测]` ⇒ 必须红 (B.2)", m15, "B.2")

    # ── 16 标称档被降级 ⇒ 必须红 (B) ──
    def m16(sb):
        def f(d):
            d["three_quantities"]["insulator_height_z"]["nominal_evidence"] = "[0数据]"
        block_mutate(sb, f)
    case("c16_nominal_downgraded",
         "★把标称档从 [官网] 降成 [0数据] ⇒ 必须红 (B.5)", m16, "B.5")

    # ── 17 量具分辨率两档缺一 ⇒ 必须红 (C) ──
    def m17(sb):
        def f(d):
            d["gauge"]["caliper_resolutions_mm"] = ["0.02"]
        block_mutate(sb, f)
    case("c17_drop_caliper_res_005",
         "删掉 0.05 mm 那档分辨率 ⇒ 必须红 (C.1)", m17, "C.1")

    npass = 0
    for name, desc, mutate, expect in cases:
        sb = make_sandbox(root, name)
        try:
            # ★★先在【未被改动的沙盒】上跑一遍 ⇒ 必须【已经红】(★本闸预期现状红★) ★★
            pre = Gate(sb).run()
            pre_fail = [(k, m) for k, ok, m in pre if not ok]
            if not pre_fail:
                print("[FAIL] %-38s ★沙盒基线竟然全绿 (★本闸预期现状红·判据写错了★)" % name)
                continue
            mutate(sb)
            res = Gate(sb).run()
            fails = [(k, m) for k, ok, m in res if not ok]
            if not fails:
                print("[FAIL] %-38s 期望红 (点名 %s) ⇒ 实际【绿】 (闸坏了)" % (name, expect))
                continue
            hit = any(k.startswith(expect) for k, _ in fails)
            if hit:
                msg = next(m for k, m in fails if k.startswith(expect))
                print("[ok]   %-38s rc=1 且点名 %s ✓  (%s)" % (name, expect, msg[:100]))
                npass += 1
            else:
                print("[FAIL] %-38s 红了但没点名 %s ⇒ 实际点名 %s"
                      % (name, expect, sorted({k for k, _ in fails})))
        except Exception as exc:
            print("[FAIL] %-38s 反向用例执行异常: %r" % (name, exc))
        finally:
            shutil.rmtree(sb, ignore_errors=True)

    # ── 正向对照: 造一份「三量已实测填齐」的假数据 ⇒ 必须全绿 ──
    sb = make_sandbox(root, "c00_positive_control")
    try:
        write_fake_record(sb)
        fill_measured(sb)
        res = Gate(sb).run()
        fails = [(k, m) for k, ok, m in res if not ok]
        if fails:
            print("[FAIL] %-38s ★正向对照应全绿, 却红了: %s" % ("c00_positive_control", fails[0]))
        else:
            print("[ok]   %-38s ★正向对照: 三量已实测填齐 ⇒ 全绿 ✓" % "c00_positive_control")
            npass += 1
    except Exception as exc:
        print("[FAIL] %-38s 正向对照异常: %r" % ("c00_positive_control", exc))
    finally:
        shutil.rmtree(sb, ignore_errors=True)

    print("正向 1 + 反向 %d (共 %d)" % (len(cases), len(cases) + 1))
    if npass == len(cases) + 1:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED (%d/%d)" % (npass, len(cases) + 1))
    return 1


# ==================================================================================================
# main
# ==================================================================================================
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.emit:
        blk = extract_json_fence(Facts(root).page, BLOCK_BEGIN, BLOCK_END)
        if blk is None:
            print("机器块读不到")
            return 2
        print(json.dumps(blk, ensure_ascii=False, indent=2))
        return 0

    if args.selftest:
        return selftest(root)

    g = Gate(root)
    res = g.run()
    nfail = 0
    for kid, ok, msg in res:
        if not ok:
            nfail += 1
            print("[FAIL] %-8s %s" % (kid, msg))
        else:
            print("[ok]   %-8s ✓" % kid)
    print("判据 A~F · 失败 %d 条" % nfail)
    if nfail == 0:
        print("PASS")
        return 0
    print("FAIL")
    print("★**本闸的【预期读数】= rc=1 (红)**: 红的是【现状】(三量【实测档】仍 `[0数据]`·收样尚未发生), 不是闸故障 ★")
    print("★**本单刻意不修现状 ⇒ 不许为了让它绿而放宽判据** ★")
    print("★绿的唯一条件 = 三量实测档真的升到 `[实测]` 且原始 3 读数在盘 (见 §2.4 充要条件) ★")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
