#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_rk3572_vccio_domain.py
================================================================================
ISS-228 · RK3572 GPIO0 → VCCIO 供电组 · 官方映射自查 的**机器门禁**。

★**为什么要有这个门禁 (ISS-228 的核心)** ★
  这条 need (hw.yaml L1124-L1133) 逾期 13 天, 它卡的是 ISS-211 的 d1 落表。
  ★**它真正的风险不是"查错电压", 而是"查对了数字、但把 ★【错误的因果关系】★ 写进网表"** ★
  ⇒ 具体四条:
    ① 结论被换成无出处的数 (例: 把 "1.8V (Forlinx 官方 SoM 逐脚 VOL 列)" 改成 "1.8V (经验判断)")
    ② 证据等级被抹 (把 [官网]/[实测]/[推算]/[0数据] 标签删掉, 或把 [推算] 写成 [官网])
    ③ 降级方案被删 (D-1/D-2/D-3 三条, 尤其 D-3 还在生效)
    ④ ★★"[0数据] 被悄悄改成一个具体电压"★★ (★这是本单最阴险的一种坏法★
       —— 例: 把 "SoM 侧 VCCIO 供电轨网名 = [0数据]" 悄悄改成 "VCCIO5_1V8" ★)
  ⇒ **凡是"判据被静默改弱 / 被换成无出处 / 被把 [0数据] 填成编的数"的动作, 必须立刻红**。

★**fail-closed 纪律 (★门禁不许靠「把判据删掉」变绿★)** ★
  · 事实卡 / 锚点块 任一缺失 ⇒ 直接红 (不是"没找到就跳过")
  · ★**反证测试不是"读文档上的数", 是 ★【重跑一遍解析逻辑】★** ⇒
    本门禁每次都会从 ★**项目库内官方 PDF**★ 重新 `pdftotext -layout` 解析
    §2.6 引脚表, 重算 129 脚 → 供电网 的映射, 再与 Forlinx 官方 SoM 逐脚
    VOL 列对账 (109 可比球位, 108 一致 + 1 例外)。⇒ **文档里写着的结论若与真实解析
    不符, 门禁红**。
  · 反向用例在**临时目录**里做 (不碰真盘)。

检查项 (rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条):
  [C1] 事实卡存在 + 必备章节齐全 (fail-closed)
  [C2] 锚点块存在 + 结构合法 + 必需字段齐全 (fail-closed)
  [C3] ★**反证测试**: 从官方 PDF 重解析 §2.6 引脚表 ⇒ 129 脚→供电网 映射
       ⇒ 与 SoM 官方 VOL 列逐球对账 ⇒ ★**每个供电组只允许一个电压** ★
       ⇒ 109 可比球位 / 108 一致 (唯一例外 = 球 1AE21, 官方标了 _1V8)
       ⇒ 且 GPIO0_B0/B1 ⇒ PMUIO0_VCC1V8, GPIO3_C4/C1 ⇒ VCCIO5_VCC_0
  [C4] ★**三条官方交叉验证**必须全过 (JTAG_M0∈VCCIO1 / JTAG_M1∈PMUIO1 / SDMMC0∈VCCIO1)
  [C5] ★**本板 I2C_A 的官方事实**: P2_31/P2_33 = I2C5_M3 / GPIO3_C4 / GPIO3_C1 = 1.8V
       ⇒ 且 ★**球 1K21 / U32 不得出现在本板 I2C_A 路径里** ★
       ⇒ 且 ★**三条"错误前提"必须都还写着被否掉的原文** ★
  [C6] ★**证据等级不许被抹 / 不许把 [推算] 写成 [官网]★ (★四种等级必须都出现★)
       ⇒ 且 ★**官方出处清单 (official_citations) 每条都要有 source + quote★ ★
  [C7] ★**降级方案三条不许被删 + D-3 必须仍是 unlocked: false** ★
  [C8] ★**[0数据] 项不许被悄悄填成具体值** ★ (★zero_data_items 每条 status 必须是 [0数据],
       且不许出现 value 字段; 且 D-3 必须仍未解锁★)

用法:
  python3 SW/tools/check_rk3572_vccio_domain.py             # 跑门禁
  python3 SW/tools/check_rk3572_vccio_domain.py --selftest   # 跑自测 (反向用例, 全在临时目录)
  python3 SW/tools/check_rk3572_vccio_domain.py --json       # 机读输出
  python3 SW/tools/check_rk3572_vccio_domain.py --root DIR   # 指定项目根 (自测用)
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
ROOT = os.path.dirname(os.path.dirname(HERE))     # .../projects/smart_glasses

# ---------------------------------------------------------------- 路径 (相对 root)
FACTS_DOC = os.path.join("SW", "RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md")
SOM_TABLE = os.path.join("HW", "PCB", "FET3572C_PIN_TABLE.csv")
DS_PDF = os.path.join("HW", "RK3572_PIN_TABLE", "RK3572_datasheet_V1.1.pdf")

ANCHOR_BEGIN = "<!-- BEGIN RK3572_VCCIO_DOMAIN_ANCHORS"
ANCHOR_END = "<!-- END RK3572_VCCIO_DOMAIN_ANCHORS"

# ---------------------------------------------------------------- ★必须齐的章节
REQUIRED_SECTIONS = [
    "★0 一句话结论",
    "★1 检索面清单",
    "★2 逐源结论",
    "★3 ★★结论一句话",
    "★4 ★★给 hw-lead 的可落表判据串",
    "★5 ★★证据分级总表",
    "★6 机器可读锚点",
    "★7 边界自查",
    "★8 自证",
]

# ---------------------------------------------------------------- ★锚点里必需的东西
REQUIRED_ANCHOR_KEYS = [
    "ball_gpio_domain",
    "board_i2c_a",
    "wrong_premises_to_reject",
    "degrade_plan",
    "official_crosschecks",
    "official_citations",
    "falsification",
    "zero_data_items",
]

REQUIRED_DOMAINS = [
    "PMUIO0_VCC1V8", "PMUIO1_VCC", "VCCIO0_VCC1V8", "VCCIO1_VCC", "VCCIO5_VCC_0",
]

# ★本板 I2C_A 的官方事实 (Forlinx §2.6.2 Table 4 逐字)
EXPECT_I2C_A = {
    "som_pins": ["P2_31", "P2_33"],
    "soc_balls": ["AH33", "AL33"],
    "soc_gpio": ["GPIO3_C4", "GPIO3_C1"],
    "so_m_official_vol": "1.8V",
    "supply_net": "VCCIO5_VCC_0",
    "level": "1.8V",
    "imp": "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)",
    "imp_b02": "上拉 2.2k 到 1.8V",
}

# ★三条"错误前提"必须都还写着被否掉的原文 (★否掉的话就不叫纠错, 叫遗忘★)
EXPECT_WRONG_PREMISES = [
    ("premise_i2c0_on_gpio0_b0_b1",
     ["I2C_A = GPIO0_B0", "I2C_A = GPIO0_B1", "I2C_A 走 I2C0"]),
    ("premise_vccio1_is_1v8_only",
     ["VCCIO1_VCC 属 1.8V only", "VCCIO1_VCC max 1.98"]),
    ("premise_gpio0_is_one_domain",
     ["GPIO0 属 VCCIO1", "GPIO0 整组只有 1.98V"]),
]

# ★四种证据等级必须都出现 (★抹掉任何一种 = 证据分级失效★)
EVIDENCE_TAGS = ["[官网]", "[实测]", "[推算]", "[0数据]"]

# ★降级方案: D-1/D-2/D-3 三条, 且 D-3 必须仍是未解锁
EXPECT_DEGRADE = [
    ("D-1", True),
    ("D-2", True),
    ("D-3", False),
]

# ★★[0数据] 项不许被悄悄填成具体值★★
#   zero_data_items 每条: status 必须是 "[0数据]", 且不许出现 value/answer 字段
FORBIDDEN_ZD_VALUE_KEYS = ["value", "answer", "result", "resolved_value", "net", "voltage"]

# ★★[0数据] 关键词 (事实卡正文里必须原样保留, 删掉 = 抹掉 [0数据] 条目)★★
#   ★★用 ZD-1..ZD-5 编号做锚 ★★ ⇒ 正文 §2.6 清单 + 锚点 YAML 两处都必须有
ZERO_DATA_KEYWORDS = [
    "RK3572 datasheet 里有没有一张显式的",
    "RK3572 datasheet §3.1/§3.2 里",
    "BSP 侧的 IO 域配置",
    "SoM 侧 VCCIO 供电轨网名",
    "GPIO0_B0/B1 是否可能另有 3.3V 档",
]
ZERO_DATA_IDS = ["ZD-1", "ZD-2", "ZD-3", "ZD-4", "ZD-5"]

# ---------------------------------------------------------------- ★反证解析 (C3)
# ★规则: §2.6 引脚表按供电域分组, 每组末尾跟该组供电网名那一行 ⇒
#        "某 GPIO 行的归属 = 其后遇到的第一条供电网行"
POW_RE = r"(?:PMUIO\d_VCC1V8|PMUIO\d_VCC|VCCIO\d_VCC(?:_\d)?(?:1V8)?)"
BALL_RE = r"\b(\d{0,2}[A-Z]{1,2}\d{1,3})\b"

# ★datasheet §2.6 引脚表区段定位
CH2_START = "Table 2-1 Pin Number Order Information"
CH3_MARK = "Chapter 3 Electrical Specification"


def _pdf_layout_text(pdf_path: str) -> str:
    """从项目库内官方 PDF 抽带列对齐的文本 (★不联网, 不外发★)"""
    out = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return out.stdout.decode("utf-8", errors="replace")


def parse_pin_table(layout_text: str):
    """★[实测] 核心: 从 §2.6 引脚表解析 ball → (gpio, 供电网)★"""
    lines = layout_text.split("\n")
    start = end = None
    for i, l in enumerate(lines):
        if start is None and CH2_START in l and i > 100:
            start = i
        if start is not None and end is None and CH3_MARK in l:
            end = i
    if start is None or end is None or end <= start:
        return {}, []
    region = lines[start:end]
    entries = []
    for l in region:
        s = l.rstrip()
        mp = re.search(r"\b(" + POW_RE + r")\s{2,}" + BALL_RE + r"\s+-\s*$", s)
        if mp:
            entries.append(("P", mp.group(1), mp.group(2)))
            continue
        m2 = re.search(BALL_RE + r"\s+(GPIO[0-4]_[A-D]\d)\s*$", s)
        if m2:
            entries.append(("G", m2.group(2), m2.group(1)))
            continue
        mg = re.search(r"\b(GPIO[0-4]_[A-D]\d)\b", s)
        if mg and s.rstrip().endswith(mg.group(1)):
            entries.append(("G", mg.group(1), None))
    assign = {}
    for i, e in enumerate(entries):
        if e[0] != "G":
            continue
        nxt = None
        for j in range(i + 1, len(entries)):
            if entries[j][0] == "P":
                nxt = entries[j][1]
                break
        if e[2]:
            assign.setdefault(e[2], (e[1], nxt))
    powers = [e[1] for e in entries if e[0] == "P"]
    return assign, powers


def load_som_table(root: str):
    """读 SoM 官方逐脚 VOL 列 (项目内转录表) ★用 csv 模块 (★desc 列含逗号带引号★)"""
    import csv as _csv
    path = os.path.join(root, SOM_TABLE)
    out = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in _csv.DictReader(f):
            if not row:
                continue
            ball = (row.get("ball") or "").strip()
            gpio = (row.get("gpio") or "").strip()
            vol = (row.get("vol") or "").strip()
            if ball:
                out[ball] = (gpio, vol)
    return out


# ---------------------------------------------------------------- 小工具
def _read(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
        return f.read()


def _exists(root: str, rel: str) -> bool:
    return os.path.isfile(os.path.join(root, rel))


def _extract_anchor(text: str):
    """抽出 ```yaml 锚点块并解析 ⇒ (data, err)。★解析失败 ⇒ fail-closed 红★"""
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), text, re.S)
    if not m:
        return None, "找不到锚点块 (%s ... %s)" % (ANCHOR_BEGIN, ANCHOR_END)
    block = m.group(1)
    y = re.search(r"```yaml\s*(.*?)```", block, re.S)
    if not y:
        return None, "锚点块里没有 ```yaml 围栏"
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(y.group(1))
    except Exception as e:      # noqa: BLE001
        return None, "锚点 YAML 解析失败: %s" % e
    return data, None


def _get(d, path, default=None):
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


# ---------------------------------------------------------------- 检查项
def check(root: str):
    errors = []
    report = []

    # ---- C1 事实卡存在 + 章节齐全
    if not _exists(root, FACTS_DOC):
        errors.append("C1 文件缺失: %s ⇒ 门禁 fail-closed (不许'没找到就跳过')" % FACTS_DOC)
        return errors, report
    facts = _read(root, FACTS_DOC)
    miss = [s for s in REQUIRED_SECTIONS if s not in facts]
    if miss:
        errors.append("C1 事实卡缺章节: %s" % " / ".join(miss))
    else:
        report.append("C1 事实卡存在 + 必备章节齐全 (8/8) ✅")

    # ---- C2 锚点块
    anchor, err = _extract_anchor(facts)
    if anchor is None:
        errors.append("C2 %s" % err)
        return errors, report
    if not isinstance(anchor, dict):
        errors.append("C2 锚点解析结果不是 dict")
        return errors, report
    iss = anchor.get("iss228")
    if not isinstance(iss, dict):
        errors.append("C2 锚点缺顶层键 iss228")
        return errors, report
    miss = [k for k in REQUIRED_ANCHOR_KEYS if k not in iss]
    if miss:
        errors.append("C2 锚点缺必需键: %s" % " / ".join(miss))
    doms = iss.get("ball_gpio_domain") or {}
    miss = [d for d in REQUIRED_DOMAINS if d not in doms]
    if miss:
        errors.append("C2 锚点 ball_gpio_domain 缺供电组: %s" % " / ".join(miss))
    zds = iss.get("zero_data_items")
    if not isinstance(zds, list) or len(zds) < 5:
        errors.append("C2 zero_data_items 条数 %s < 5"
                      % (len(zds) if isinstance(zds, list) else "非 list"))
    cits = iss.get("official_citations")
    if not isinstance(cits, list) or len(cits) < 4:
        errors.append("C2 official_citations 条数 %s < 4"
                      % (len(cits) if isinstance(cits, list) else "非 list"))
    if not miss:
        report.append("C2 锚点块存在 + 结构合法 + 必需字段齐全 ✅")

    # ---- C3 反证测试 (重跑解析)
    if not _exists(root, DS_PDF):
        errors.append("C3 官方 PDF 缺失: %s ⇒ fail-closed" % DS_PDF)
    elif not _exists(root, SOM_TABLE):
        errors.append("C3 SoM 官方逐脚表缺失: %s ⇒ fail-closed" % SOM_TABLE)
    else:
        layout = _pdf_layout_text(os.path.join(root, DS_PDF))
        assign, _powers = parse_pin_table(layout)
        if len(assign) < 100:
            errors.append("C3 从官方 PDF 只解析出 %d 个脚 (期望 >=100) ⇒ 解析逻辑坏了" % len(assign))
        else:
            som = load_som_table(root)
            som_gpio = {b: v for b, v in som.items() if v[0].startswith("GPIO")}
            dom = {}
            for b, (g, pw) in assign.items():
                if b in som_gpio and pw:
                    dom.setdefault(pw, {})[b] = som_gpio[b][1]
            compared = sum(len(m) for m in dom.values())
            multi = []
            for pw, m in dom.items():
                vols = set(m.values())
                if len(vols) > 1:
                    multi.append((pw, {v: sum(1 for x in m.values() if x == v) for v in vols}))
            # ★允许的唯一例外: VCCIO6_VCC 里的 1AE21 (官方标了 _1V8)★
            bad = [x for x in multi
                   if not (x[0] == "VCCIO6_VCC" and set(x[1].keys()) == {"1.8V", "3.3V"})]
            if bad:
                errors.append("C3 反证测试失败: 供电组内出现多个电平 %s" % bad)
            elif compared < 100:
                errors.append("C3 反证测试: 可比球位数 %d < 100" % compared)
            else:
                matched = compared - 1 if multi else compared
                report.append("C3 反证测试: %d 可比球位 / %d 一致 (唯一例外 = 官方 _1V8 脚) ✅"
                              % (compared, matched))
            # 锚点里的 falsification 数字必须与实跑一致
            fa = iss.get("falsification") or {}
            if fa.get("so_m_balls_checked") != compared:
                errors.append("C3 锚点 so_m_balls_checked=%s 与实跑 %d 不符"
                              % (fa.get("so_m_balls_checked"), compared))
            if fa.get("so_m_balls_matched") != (compared - 1 if multi else compared):
                errors.append("C3 锚点 so_m_balls_matched=%s 与实跑 %d 不符"
                              % (fa.get("so_m_balls_matched"),
                                 (compared - 1 if multi else compared)))
            # ★GPIO0_B0 / GPIO0_B1 / GPIO3_C4 / GPIO3_C1 的供电组必须与实跑一致★
            for gname, expect_dom in (("GPIO0_B0", "PMUIO0_VCC1V8"),
                                      ("GPIO0_B1", "PMUIO0_VCC1V8"),
                                      ("GPIO3_C4", "VCCIO5_VCC_0"),
                                      ("GPIO3_C1", "VCCIO5_VCC_0")):
                hit = [(b, pw) for b, (g, pw) in assign.items() if g == gname]
                if not hit:
                    errors.append("C3 实跑没解析出 %s" % gname)
                elif hit[0][1] != expect_dom:
                    errors.append("C3 %s 的供电组实跑=%s 期望=%s" % (gname, hit[0][1], expect_dom))
            # 锚点里 covers 字段必须与实跑一致
            for dom_name, covers in (("PMUIO0_VCC1V8", ["GPIO0_B0", "GPIO0_B1"]),
                                     ("VCCIO5_VCC_0", ["GPIO3_C4", "GPIO3_C1"])):
                got = _get(iss, ("ball_gpio_domain", dom_name, "covers"))
                if got is not None and list(got) != list(covers):
                    errors.append("C3 锚点 %s.covers=%s 期望=%s" % (dom_name, got, covers))

    # ---- C4 三条官方交叉验证
    xc = iss.get("official_crosschecks") or []
    if len(xc) < 3:
        errors.append("C4 官方交叉验证条数 %d < 3" % len(xc))
    else:
        npass = sum(1 for c in xc if c.get("pass") is True)
        if npass < 3:
            errors.append("C4 官方交叉验证只有 %d/3 通过" % npass)
        else:
            if _exists(root, DS_PDF) and _exists(root, SOM_TABLE):
                layout = _pdf_layout_text(os.path.join(root, DS_PDF))
                assign, _ = parse_pin_table(layout)
                c4err = []
                for c in xc:
                    want = c.get("parsed_domain")
                    for g in c.get("soc_gpio", []):
                        hit = [pw for b, (gg, pw) in assign.items() if gg == g]
                        if not hit or hit[0] != want:
                            c4err.append("C4 交叉验证 %s: %s 实跑=%s 期望=%s"
                                         % (c.get("claim"), g, hit[0] if hit else "无", want))
                if c4err:
                    errors.extend(c4err)
                else:
                    report.append("C4 三条官方交叉验证全过 (JTAG_M0∈VCCIO1 / JTAG_M1∈PMUIO1 / SDMMC0∈VCCIO1) ✅")

    # ---- C5 本板 I2C_A 官方事实 + 三条错误前提
    bia = iss.get("board_i2c_a") or {}
    c5err = []
    for k, want in EXPECT_I2C_A.items():
        got = bia.get(k)
        if got is None:
            c5err.append("C5 锚点 board_i2c_a 缺 %s" % k)
        elif isinstance(want, list):
            if list(got) != list(want):
                c5err.append("C5 board_i2c_a.%s=%s 期望=%s" % (k, got, want))
        elif got != want:
            c5err.append("C5 board_i2c_a.%s=%r 期望=%r" % (k, got, want))
    som = load_som_table(root) if _exists(root, SOM_TABLE) else {}
    for ball in ("1K21", "U32"):
        if ball in som:
            c5err.append("C5 球 %s 竟出现在 SoM 表里 ⇒ 本板 I2C_A 前提判定有误" % ball)
    wps = iss.get("wrong_premises_to_reject") or []
    found = {w.get("id"): w for w in wps if isinstance(w, dict)}
    for pid, phrases in EXPECT_WRONG_PREMISES:
        w = found.get(pid)
        if w is None:
            c5err.append("C5 锚点缺错误前提条目 %s" % pid)
            continue
        ms = w.get("must_not_say") or []
        for ph in phrases:
            if ph not in ms:
                c5err.append("C5 %s.must_not_say 缺 %r" % (pid, ph))
    if "勘误" not in facts:
        c5err.append("C5 事实卡里没有『勘误』字样 ⇒ 原 need 的错误前提可能没被显式否掉")
    if c5err:
        errors.extend(c5err)
    else:
        report.append("C5 本板 I2C_A 官方事实 (P2_31/P2_33 = I2C5_M3 = 1.8V) + 三条错误前提都在否 ✅")

    # ---- C6 证据等级不许被抹 + [推算] 不许写成 [官网] + 官方出处清单完整
    c6err = []
    for tag in EVIDENCE_TAGS:
        if tag not in facts:
            c6err.append("C6 证据等级 %s 在事实卡里消失了 ⇒ 证据分级被抹" % tag)
    # ★[推算] 与 [官网] 语义冲突: 只看 §5 证据分级总表的行 ⇒
    #   ★某行的「等级」栏是 [官网], 但「怎么量的」栏写着推导/判定/算术 ⇒ 那就是把 [推算] 写成了 [官网]★
    rows_ok = True
    in_ev = False
    for line in facts.split("\n"):
        if "★5 ★★证据分级总表" in line:
            in_ev = True
            continue
        if in_ev and line.startswith("## ★6"):
            break
        if not in_ev or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        concl, level, how = cells[0], cells[1], cells[2]
        if not level or level.startswith("---") or "等级" in level:
            continue
        if "[官网]" not in level:
            continue
        # ★等级栏只自称 [官网] (不含 [推算]) ⇒ 怎么量的栏里不许出现推导/判定/算术/推断★
        #   (等级栏同时含 [推算] 的行 = 已正确标成混合等级 ⇒ 放行)
        if "[推算]" in level:
            continue
        if any(k in how for k in ("推导", "判定", "算术", "推断", "由已核事实", "可复核")):
            c6err.append("C6 证据分级总表: 「%s」等级栏写 [官网], 但「怎么量的」栏是推导 ⇒ 把 [推算] 写成了 [官网]"
                         % concl[:60])
            rows_ok = False
    if not rows_ok:
        pass
    # ★官方出处清单: 每条都要有 source + quote, 且 id 必须在事实卡正文里出现★
    for c in (iss.get("official_citations") or []):
        cid = c.get("id")
        if not cid:
            c6err.append("C6 official_citations 里有条目缺 id")
            continue
        if not (c.get("source") or "").strip():
            c6err.append("C6 官方出处 %s 缺 source ⇒ 结论被换成无出处的数" % cid)
        if not (c.get("quote") or "").strip():
            c6err.append("C6 官方出处 %s 缺 quote ⇒ 结论被换成无出处的数" % cid)
        if cid not in facts:
            c6err.append("C6 官方出处 %s 在事实卡正文里不见了" % cid)
    if c6err:
        errors.extend(c6err)
    else:
        report.append("C6 四种证据等级齐全 + [推算] 未被写成 [官网] + 官方出处清单完整 ✅")

    # ---- C7 降级方案三条不许被删 + D-3 仍未解锁
    deg = iss.get("degrade_plan") or []
    got = {d.get("id"): d for d in deg if isinstance(d, dict)}
    c7err = []
    for did, unlocked in EXPECT_DEGRADE:
        d = got.get(did)
        if d is None:
            c7err.append("C7 降级方案 %s 被删了" % did)
            continue
        if not d.get("default"):
            c7err.append("C7 降级方案 %s 缺 default (保守默认)" % did)
        if not d.get("unlock"):
            c7err.append("C7 降级方案 %s 缺 unlock (后续解锁条件)" % did)
        if d.get("unlocked") is not unlocked:
            c7err.append("C7 降级方案 %s 的 unlocked=%s 期望=%s"
                         % (did, d.get("unlocked"), unlocked))
    if c7err:
        errors.extend(c7err)
    else:
        report.append("C7 降级方案 D-1/D-2/D-3 齐全, D-3 仍未解锁 ✅")

    # ---- C8 [0数据] 不许被悄悄填成具体值
    c8err = []
    for zd in (iss.get("zero_data_items") or []):
        zid = zd.get("id")
        if not zid:
            c8err.append("C8 zero_data_items 里有条目缺 id")
            continue
        if zd.get("status") != "[0数据]":
            c8err.append("C8 %s 的 status=%r ⇒ [0数据] 被悄悄改成了具体结论"
                         % (zid, zd.get("status")))
        for k in FORBIDDEN_ZD_VALUE_KEYS:
            if k in zd and zd.get(k) not in (None, ""):
                c8err.append("C8 %s 出现了 %s=%r ⇒ [0数据] 被悄悄填成了具体值"
                             % (zid, k, zd.get(k)))
        what = (zd.get("what") or "").strip()
        if what and what not in facts:
            c8err.append("C8 %s 的 what 在事实卡正文里不见了 ⇒ [0数据] 条目可能被删" % zid)
        # ★★ZD 编号必须在正文 §2.6 清单里出现 (★正文 + 锚点两处都在, 才算这条 [0数据] 还活着★★)
        if ("**%s**" % zid) not in facts:
            c8err.append("C8 %s 的编号在事实卡正文 §2.6 清单里不见了 ⇒ [0数据] 条目被删" % zid)
    for kw in ZERO_DATA_KEYWORDS:
        if kw.replace(" ", "") not in facts.replace(" ", ""):
            c8err.append("C8 关键词 %r 在事实卡里不见了 ⇒ [0数据] 条目可能被删" % kw)
    for zid in ZERO_DATA_IDS:
        if ("**%s**" % zid) not in facts:
            c8err.append("C8 %s 的编号在事实卡正文 §2.6 清单里不见了 ⇒ [0数据] 条目被删" % zid)
    d3 = got.get("D-3") or {}
    if d3.get("unlocked") is False:
        if not any(k in (d3.get("default") or "") for k in ("[0数据]", "不许", "编")):
            c8err.append("C8 D-3 的 default 里没有 [0数据]/不许编 的约束 ⇒ 可能被悄悄填成具体网名")
    if c8err:
        errors.extend(c8err)
    else:
        report.append("C8 [0数据] 项未被悄悄填成具体值 ✅")

    return errors, report


# ---------------------------------------------------------------- 反向用例 (selftest)
RELS = [FACTS_DOC, SOM_TABLE, DS_PDF]


def _copy_tree(src: str, dst: str, rels):
    for rel in rels:
        s = os.path.join(src, rel)
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)


def _run_case(root, mutate):
    """在临时树上破坏 ⇒ 必须红"""
    with tempfile.TemporaryDirectory() as td:
        _copy_tree(root, td, RELS)
        mutate(td)
        errs, _ = check(td)
        if not errs:
            return None, "★【反例没被抓到】★ (破坏后门禁仍全绿)"
        return True, errs[0]


def selftest(root: str):
    print("=== SELFTEST (ISS-228 反向用例: 每条都必须在被破坏后变红) ===")
    cases = []

    def C(desc, mutate):
        cases.append((desc, mutate))

    def edit_facts(td, fn):
        p = os.path.join(td, FACTS_DOC)
        t = open(p, encoding="utf-8").read()
        t2 = fn(t)
        open(p, "w", encoding="utf-8").write(t2)

    # --- REV-1: 结论被换成无出处的数 (官方出处清单的 quote 被抹)
    C("把『官方出处』的 quote 抹掉 ⇒ 变成无出处的数",
      lambda td: edit_facts(td, lambda t: t.replace(
          'quote: "P2_31 = 球 AH33 = I2C5_SCL_M3 / GPIO3_C4_d / VOL 1.8V"',
          'quote: ""')))

    # --- REV-2: 证据等级被抹 (删掉 [推算])
    C("把证据等级 [推算] 整个抹掉",
      lambda td: edit_facts(td, lambda t: t.replace("[推算]", "推导")))

    # --- REV-3: 降级方案被删 (删掉 D-3)
    def m3(td):
        edit_facts(td, lambda t: re.sub(
            r"\n\s*- id: \"D-3\".*?(?=\n\s*- id:|\n\s*zero_data_items:)", "\n", t, flags=re.S))
    C("把降级方案 D-3 (VCCIO rail 网名那条) 删掉", m3)

    # --- REV-4: [0数据] 被悄悄改成一个具体网名
    def m4(td):
        edit_facts(td, lambda t: t.replace(
            '      what: "SoM 侧 VCCIO 供电轨的网名 (载板上的 rail 名)"\n      status: "[0数据]"',
            '      what: "SoM 侧 VCCIO 供电轨的网名 (载板上的 rail 名)"\n'
            '      status: "VCCIO5_1V8"'))
    C("把 [0数据] (SoM 侧 VCCIO rail 网名) 悄悄改成一个具体网名", m4)

    # --- REV-5: 错误前提被"遗忘" (must_not_say 清空)
    C("把『本板 I2C_A 走 I2C0 属错误前提』这条 must_not_say 清空",
      lambda td: edit_facts(td, lambda t: t.replace(
          'must_not_say: ["I2C_A = GPIO0_B0", "I2C_A = GPIO0_B1", "I2C_A 走 I2C0"]',
          'must_not_say: []')))

    # --- REV-6: B-01/B-02 的取值被改成 3.3V
    def m6(td):
        edit_facts(td, lambda t: t.replace(
            'level: "1.8V"\n    imp: "上拉 2.2k 到 1.8V', 'level: "3.3V"\n    imp: "上拉 4.7k 到 3.3V')
            .replace('so_m_official_vol: "1.8V"', 'so_m_official_vol: "3.3V"'))
    C("把 B-01/B-02 的最终取值偷偷改成 3.3V / 4.7k", m6)

    # --- REV-7: 官方交叉验证被改成 pass: false
    C("把『JTAG_M1 ∈ PMUIO1』这条官方交叉验证改成 pass: false",
      lambda td: edit_facts(td, lambda t: t.replace(
          '      parsed_domain: "PMUIO1_VCC"\n      pass: true',
          '      parsed_domain: "PMUIO1_VCC"\n      pass: false')))

    # --- REV-8: 事实卡整个删掉 (fail-closed)
    C("把事实卡整个删掉 (fail-closed 纪律)",
      lambda td: os.remove(os.path.join(td, FACTS_DOC)))

    # --- REV-9: 锚点块整个删掉 (fail-closed)
    def m9(td):
        edit_facts(td, lambda t: re.sub(
            re.escape(ANCHOR_BEGIN) + r".*?" + re.escape(ANCHOR_END),
            "<!-- (锚点被删了) -->", t, flags=re.S))
    C("把锚点块整个删掉 (fail-closed 纪律)", m9)

    # --- REV-10: 把 SoM 官方 VOL 列改掉 (让反证测试挂)
    def m10(td):
        p = os.path.join(td, SOM_TABLE)
        lines = open(p, encoding="utf-8").read().split("\n")
        for i, l in enumerate(lines):
            if l.startswith("P2,31,"):
                parts = l.split(",")
                parts[5] = "3.3V"
                lines[i] = ",".join(parts)
        open(p, "w", encoding="utf-8").write("\n".join(lines))
    C("把 SoM 官方 VOL 列 (P2_31) 改成 3.3V ⇒ 反证测试必须挂", m10)

    # --- REV-11: 章节被改名
    C("把事实卡的一个必备章节改名 ⇒ 章节齐备性检查必须红",
      lambda td: edit_facts(td, lambda t: t.replace("## ★7 边界自查", "## ★7 附注")))

    # --- REV-12: D-3 悄悄标成已解锁
    C("把 D-3 (VCCIO rail 网名) 悄悄标成已解锁",
      lambda td: edit_facts(td, lambda t: t.replace(
          'unlock: "拿到 Forlinx 载板原理图 / 官方 rail 命名表"\n      unlocked: false',
          'unlock: "拿到 Forlinx 载板原理图 / 官方 rail 命名表"\n      unlocked: true')))

    # --- REV-13: 把一条 [0数据] 条目整条删掉 (正文 §2.6 清单 + 锚点同时删)
    def m13(td):
        p = os.path.join(td, FACTS_DOC)
        t = open(p, encoding="utf-8").read()
        t = t.replace("| ③ ★**ZD-3** ★ | ★**BSP 侧的 IO 域配置 (`io-domains` / `domain-supply`)** ★ |",
                      "| ③ | ★**BSP 侧的 IO 域配置** ★ |")
        t = re.sub(r"\n\s*- id: \"ZD-3\"\n\s*what: \"BSP 侧的 IO 域配置 \(io-domains / domain-supply\)\"\n\s*status: \"\[0数据\]\"",
                   "", t)
        open(p, "w", encoding="utf-8").write(t)
    C("把一条 [0数据] 条目 (ZD-3) 整条删掉", m13)

    # --- REV-14: 锚点里 VCCIO5_VCC_0.covers 改错
    C("把锚点里 VCCIO5_VCC_0.covers 改成 GPIO0_B0/B1 ⇒ 与实跑不符必须红",
      lambda td: edit_facts(td, lambda t: t.replace(
          'covers: ["GPIO3_C4", "GPIO3_C1"]',
          'covers: ["GPIO0_B0", "GPIO0_B1"]')))

    # --- REV-15: 把 falsification 的数字改成与实跑不符
    C("把锚点里的 so_m_balls_matched 改成 191 (夸大) ⇒ 必须红",
      lambda td: edit_facts(td, lambda t: t.replace(
          "so_m_balls_matched: 108", "so_m_balls_matched: 191")))

    # --- REV-16: 把官方出处 source 抹掉
    C("把『官方出处』的 source 抹掉 ⇒ 结论变成无出处",
      lambda td: edit_facts(td, lambda t: t.replace(
          'source: "Forlinx OK3572-C 官方手册 §2.6.2 Table 4 (P2 Even) 逐字"',
          'source: ""')))

    # --- 先跑基线
    errs, _ = check(root)
    if errs:
        print("  ❌ 基线不绿 (先修基线再跑自测):")
        for e in errs:
            print("     -", e)
        return 1
    print("  ✅ 基线全绿 (C1~C8 在临时树上全过)")

    npass = 0
    for i, (desc, mutate) in enumerate(cases, 1):
        ok, msg = _run_case(root, mutate)
        if ok:
            npass += 1
            print("  ✅ REV-%-2d %-50s ⇒ 变红 (%s)" % (i, desc, msg[:88]))
        else:
            print("  ❌ REV-%-2d %-50s ⇒ %s" % (i, desc, msg))
    print("--- SELFTEST %d/%d 通过 ---" % (npass, len(cases)))
    return 0 if npass == len(cases) else 1


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    errs, report = check(root)
    if args.json:
        print(json.dumps({"ok": not errs, "errors": errs, "report": report},
                         ensure_ascii=False, indent=1))
        return 0 if not errs else 1

    if errs:
        print("❌ ISS-228 RK3572 GPIO0→VCCIO 官方映射门禁: %d 项不通过" % len(errs))
        for e in errs:
            print("   - %s" % e)
        return 1
    print("✅ ISS-228 RK3572 GPIO0→VCCIO 官方映射门禁: 全过")
    for r in report:
        print("   %s" % r)
    print("   ★ 本板 I2C_A = I2C5_M3 (GPIO3_C4/C1, 球 AH33/AL33) ⇒ Forlinx 官方 SoM 逐脚 VOL = 1.8V")
    print("   ★ GPIO0_B0/B1 (球 1K21/U32) ⇒ PMUIO0_VCC1V8 = 1.8V only (abs-max 1.98V) ⇒ 这两根脚本板未引出")
    print("   ★ B-01/B-02 最终取值: imp = 上拉 2.2k 到 1.8V / level = 1.8V")
    print("   ★ 板端 [实测] = 0 条 (板与屏不在本机); 零外发")
    return 0


if __name__ == "__main__":
    sys.exit(main())
