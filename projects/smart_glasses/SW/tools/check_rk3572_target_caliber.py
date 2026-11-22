#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SW/tools/check_rk3572_target_caliber.py  (v2.0)
=====================================================================
ISS-353 · sw-lead · 全仓「rk3572 目标口径」清账闸 (★只读★)

★它查什么★
  全仓 (SW/ HW/ state/fragments/ HANDOFF/ logs/ REQ/) 的文本文件里, 凡是把
  「旧口径」当作**当下有效的结论 / 路线 / 前置条件**在陈述的 ⇒ 逐条点名列出
  (文件 + 行号 + 原文片段 + 判定 + 处置建议 + 处置通道)。

★旧口径是什么 (2026-11-23 起的当前真值, 三句)★
  ① toolkit2 (2.3.2 / 2.5.0) 不支持 rk3572 target  ⇒ [官网]+[实测]
     (官方 rknn-toolkit2 README「Support Platform」清单无 RK3572)
     ⇒ ★所以转换链要用 rknn3-toolkit 1.2.0★
  ② rknn3-toolkit 1.2.0 支持 target_platform='rk3572' ⇒ [实测]
     (官方 rknn3-toolkit README「Supported Platforms」含 RK3572;
      CHANGELOG V1.0.4「Added RK3572 platform support (Beta)」)
  ③ 板端接受性仍 [0数据] ⇒ 降级方案 = 板到手一条命令出 PASS/FAIL
     (SW/tools/rk3572_rknn3_board_smoke.sh)

★它不许做什么★
  · 只读 —— 一个字节都不改被检文件 (★本单唯一的闸, 不许有副作用★)
  · 不许只报数量 —— 输出必须带【名单】(文件+行号+原文+判定+处置), 否则脚本自己判 FAIL
  · 不写 /tmp —— 自测沙盒强制落项目盘 (<root>/tmp/iss353_selftest_*) ★/tmp 配额已打满★
    (2026-11-23 04:4x 实测: /tmp userquota tmpfs 已满 ⇒ 连 1MB 写都失败 ⇒ 写 /tmp 会拿到假读数)

★rc 语义 (fail-closed, 与本项目其它闸一致)★
  rc = 0  全仓无「结论矛盾(要处置)」条目
  rc = 1  ★仍存在「结论矛盾(要处置)」条目 ⇒ 旧口径没清干净★
  rc = 2  用法/自测错误

★判定三分法 (铁律: 历史叙述不许改, 只处置结论层面矛盾的那些)★
  结论矛盾(要处置)      该行把旧口径当作**当下有效的结论/路线**在陈述      ⇒ rc=1
  结论待裁(交 main 裁)  该行陈述的是**只有老板能改的状态标签** (ISS-155 定位) ⇒ 不判红, 但点名
  历史叙述(可留)        该行只是描述「曾经测出过什么」/ 已被取代且已标注 /
                        代码与脚本的现状陈述 / 仍然成立的 toolkit2 层事实

★处置通道 (谁有权改)★
  本单可处置  ∈ ISS-353 允许写范围 (SW/RK3572_TARGET_COMPAT_V2.md · state/fragments/sw.yaml
              · HANDOFF/2026-11-23_sw-lead_ISS353_* · logs/iss353/*)
  越权·交 main 裁  其余 (HW/* 属 hw-lead 地界; 其它 SW 文档不在本单允许写范围)
  ⇒ 越权条目一律附「逐字替换文本」+ 一键补丁脚本 logs/iss353/apply_caliber_dispositions.py

★v2.0 相对上一趟 (04:27:14 / 04:27:42 两版脚本) 的规则修订 (★全部记录在案, 方向不变: 仍抓旧口径结论★)★
  F1 R2 旧版缺 rk3576 约束 ⇒ 「RK3572 … 必须/只能 …」(任意 40 字内) 被当成旧口径
     ⇒ ★误报 HW/SCHEMATIC_V1.md 的 DSI 网表行等 ≥10 条 (DSI 行里「已随 RK3572 删除」+
     「必须拆」偶合)★ ⇒ 本版要求同一句里必须同时出现 rk3576 才算 R2 命中 (已进自测)
  F2 规定动作词表删掉「支持用」(那是证据措辞不是规定) ⇒ 少误报
  F3 「用/转 rk3576 转」省略写法的窗口 14 → 30 字 ⇒ 不再漏
     「用 `target_platform='rk3576'` 转」(24 字)
  F4 代码/脚本行 (config(...)/RKNN(verbose=...)/say "..." 等) 默认判「历史叙述(可留)」,
     除非同一行带强规定词 (只能/必须/唯一/写死/一律用)
  F5 state/fragments/*.yaml 台账是**追加式** ⇒ 命中行之后若存在取代标记
     (已由 ISS-263 / 已被取代 / 保留作历史留档 …) ⇒ 判「历史叙述(可留)」(后条取代前条)
  F6 R5 (ISS-155 = demo 头号卡点) 从「结论矛盾」改判「结论待裁(交 main 裁)」——
     ★因为 ISS-155 的定位是只有老板能改的状态标签, sw-lead 不代拍★ (仍逐条点名)

用法:
  python3 SW/tools/check_rk3572_target_caliber.py                 # 扫全仓 (只读)
  python3 SW/tools/check_rk3572_target_caliber.py --root DIR      # 扫别处 (自测用)
  python3 SW/tools/check_rk3572_target_caliber.py --json          # 机器读
  python3 SW/tools/check_rk3572_target_caliber.py --selftest      # ★反向用例★
=====================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys

# ── 扫面 (★与 ISS-353 任务书一致★) ───────────────────────────────────────────
SCAN_ROOTS = ("SW", "HW", "state/fragments", "HANDOFF", "logs", "REQ")
TEXT_EXT = (".md", ".yaml", ".yml", ".json", ".txt", ".sh", ".py", ".rst")
MAX_BYTES = 4 * 1024 * 1024

# ── 本单允许写范围 (★越权 ⇒ 交 main 裁★) ───────────────────────────────────
WRITABLE = (
    "SW/RK3572_TARGET_COMPAT_V2.md",
    "state/fragments/sw.yaml",
)
WRITABLE_PREFIX = ("logs/iss353/", "HANDOFF/2026-11-23_sw-lead_ISS353_")

# ── 取代标记: 带这些 ⇒ 已被明确标注取代 ⇒ 判「历史叙述(可留)」 ──────────────
SUPERSEDED_PAT = re.compile(
    r"已由\s*ISS-263|ISS-263\s*已|已被\s*ISS-263|已由\s*ISS-250|已被\s*ISS-250"
    r"|已被\s*ISS-353|ISS-353\s*已|已被取代|已取代|取代了|保留作历史留档|结论不再引用"
    r"|被再证伪|被证伪|已被官方分层|不再是默认|已过时|已失效|已被\s*rknn3-toolkit"
)

# ── 强规定词 (出现即判结论矛盾, 不受历史标记豁免) ────────────────────────────
STRONG = r"只能|必须|只能用|须用|应当|应当用|应该用|需要用|统一用|一律用|不得用|唯一路径|唯一目标|唯一合法|写死|定义为|默认(?:路线|走|target)|主路线|替代路线|不存在.{0,40}(?:路径|选项|可能|途径)"

# ── 中性/历史标记 (命中即倾向「历史叙述(可留)」) ─────────────────────────────
HIST = (r"20\d\d-\d\d-\d\d|实测|原文|日志|曾|当时|历史|已核|复现|脚注|脚注|"
        r"ValueError|Unsupported target_platform|Invalid target_platform|rc\s*=\s*0|"
        r"ret\s*=\s*0|\[0数据\]|\[实测\]|\[官网\]|\[推算\]|\[媒体\]|见 §|见 §|引自")

# ── rk3576 作为「转换 target」的写法 ────────────────────────────────────────
RK3576_TGT = (r"(?:rk3576|RK3576)[^\n]{0,24}?target"
              r"|target[^\n]{0,24}?(?:rk3576|RK3576)"
              r"|rk3576-target"
              r"|target_platform\s*[=:]\s*['\"]?(?:rk3576|RK3576)"
              r"|['\"`](?:rk3576|RK3576)['\"`][^\n]{0,8}?(?:转|来转)")

# ── 代码/脚本行 (⇒ 默认历史叙述, 除非带强规定词) ────────────────────────────
CODEISH = re.compile(
    r"config\s*\(\s*target_platform|RKNN\s*\(\s*verbose|print\s*\(|^\s*say\s+\"|"
    r"^\s*#|^\s*\$|r\.config\s*\(|RKNN\.config|target_platform\s*=\s*['\"]rk3576['\"]\s*,|"
    r"\.config\(target_platform")

RULES = [
    # ── A 类: 把 rk3576 写成当下必须/唯一/默认的转换 target ─────────────────
    ("A1", re.compile(r"(?:%s)[^\n]{0,90}?(?:%s)|(?:%s)[^\n]{0,90}?(?:%s)"
                      % (STRONG, RK3576_TGT, RK3576_TGT, STRONG)),
     "把 rk3576 写成当下必须/唯一/默认的转换 target ⇒ 已由 ISS-263 (rknn3-toolkit 1.2.0 支持 "
     "target_platform='rk3572') 取代 ⇒ 改写成「toolkit2 不支持 rk3572 ⇒ 转换链走 rknn3-toolkit 1.2.0」"),
    # ── A1b: 强规定词 + 裸引号 rk3576 (不带 target 字样, 如「只能用 `'rk3576'`」) ─
    ("A1b", re.compile(r"(?:%s)[^\n]{0,60}?['\"`](?:rk3576|RK3576)['\"`]|"
                       r"['\"`](?:rk3576|RK3576)['\"`][^\n]{0,60}?(?:%s)"
                       % (STRONG, STRONG)),
     "把 rk3576 写成唯一/必须的转换 target (裸引号写法) ⇒ 已由 ISS-263 (rknn3-toolkit 1.2.0 "
     "支持 target_platform='rk3572') 取代"),
    # ── A2: 「用 / 转成 / 改用 rk3576 target 转」省略写法 (窗口 30) ───────────
    ("A2", re.compile(r"(?:用|转成|改用|复用|走|拿)[^\n]{0,30}?(?:rk3576|RK3576)[^\n]{0,12}?"
                      r"(?:来转|转|target|编译)"),
     "「用 rk3576 转」省略写法 ⇒ 同 A1 (已被 rknn3-toolkit 1.2.0 的 rk3572 target 取代)"),
    # ── A3: rk3576-target 产物「直上板 / 维持现状」当路线①默认 ────────────────
    ("A3", re.compile(r"rk3576[^\n]{0,30}?(?:直上板|维持现状|零新增成本|先试)"),
     "路线① (rk3576-target 直上板) 已降为次要 ⇒ 主路线 = rknn3-toolkit 1.2.0 + target_platform='rk3572'"),
    # ── C 类: 「不存在升级就有 rk3572 的路 / 根本没有 rk3572 这个编译目标」 ────
    ("C1", re.compile(r"不存在[^\n]{0,80}?(?:升级|更新)[^\n]{0,60}?(?:rk3572|RK3572)[^\n]{0,40}?"
                      r"(?:选项|路|可能|途径)"
                      r"|根本没有[^\n]{0,30}?(?:rk3572|RK3572)[^\n]{0,20}?编译目标"
                      r"|不存在[^\n]{0,60}?(?:rk3572|RK3572)[^\n]{0,40}?(?:路|选项|可能|途径)"),
     "「不存在升级就有 rk3572 的路」已被 rknn3-toolkit 1.2.0 证伪 (它就是那条路)"),
    # ── E 类: 「RK3572 与 RK3576 同代同架构」当事实陈述 ───────────────────────
    ("E1", re.compile(r"同代同架构"),
     "「同代同架构」是 ISS-155 自推 [推算], 已被 ISS-250 官方反证 "
     "(RK3576=6 TOPS / 归族 RKNN2-rkcp vs RK3572=RKNN3-native)"),
    # ── D 类: ISS-155 的状态标签 (★只有老板能改 ⇒ 交 main 裁★) ──────────────
    ("D1", re.compile(r"ISS-155[^\n]{0,90}?(?:头号卡点|头号阻塞|一号卡点|第一卡点|blocker|阻塞项)"
                      r"|(?:头号卡点|头号阻塞|一号卡点)[^\n]{0,70}?ISS-155"),
     "ISS-155 的定位是否从「demo 头号卡点」降为「转换链已通 / 板端待板」⇒ ★交 main 裁★ (sw-lead 不代拍)"),
    # ── B 类: toolkit2 层「rk3572 不是合法 target」这条**仍然成立**的事实 ────
    ("B1", re.compile(r"(?:rk3572|RK3572)[^\n]{0,50}?不是[^\n]{0,50}?(?:合法|target_platform)"
                      r"|Invalid target_platform|Unsupported target_platform"),
     "toolkit2 层事实仍成立 [官网]+[实测] (2.3.2/2.5.0 无 rk3572) ⇒ 但它不是终点: "
     "转换链走 rknn3-toolkit 1.2.0 (★补一句指向即可, 不算矛盾★)"),
    # ── F 类: 「rk3576-target 产物在 RK3572 上能不能跑」跨芯片命题 ───────────
    ("F1", re.compile(r"rk3576-target|rk3576[^\n]{0,12}?转出来的\s*\.rknn"
                      r"|在\s*RK3572\s*上(?:能不能|能否|可不可以)"),
     "跨芯片接受性仍 [0数据] ⇒ 官方 RKNN3 demo README 把 RK3572(native) 与 RK3576/RK3588(rkcp) "
     "分成两条 runtime ⇒ 官方无互换表述"),
]

VERDICT_STALE = "结论矛盾(要处置)"
VERDICT_PEND = "结论待裁(交 main 裁)"
VERDICT_HIST = "历史叙述(可留)"

# 各规则的默认强度: strong = 带强规定词时判矛盾; weak = 有历史标记时判历史
RULE_STRONG = {"A1", "A1b", "A2", "A3", "C1", "E1"}
# 芯片语境词 (BSP/runtime/SDK/模组…): 出现即说明在讲「芯片」而不是「转换 target」
CHIP_CTX = re.compile(r"BSP|SoC|runtime|Runtime|SDK|模组|芯片|主控|供电|封装|引脚|管脚")
# ★F7 否定语境: 「官方不存在/没有/无此口径 … rk3576 …」= 陈述【官方没有这句话】⇒ 事实类 (可留)
NEG_CTX = re.compile(r"(?:不存在|没有|无此口径|没有任何|从未|并非|查不到)[^。\n]{0,60}?"
                     r"(?:rk3576|RK3576)")
# ★F8 台账取代标记必须【切题】: 只认与本口径 (rk3572/rk3576/target/ISS-155/263/250/353) 相关的取代标记
#   (否则 hw.yaml 里一条与本口径无关的取代标记会把整份台账的历史条目误判成「已被取代」)
LEDGER_TOPIC = re.compile(r"rk3572|rk3576|RK3572|RK3576|target_platform|ISS-155|ISS-263|"
                           r"ISS-250|ISS-353")
RULE_PEND = {"D1"}


def snippet(line: str, width: int = 160) -> str:
    s = line.strip().replace("\t", " ")
    s = re.sub(r"\s+", " ", s)
    return s[:width] + ("…" if len(s) > width else "")


def writable(rel: str) -> bool:
    return rel in WRITABLE or rel.startswith(WRITABLE_PREFIX)


def channel(rel: str) -> str:
    return "本单可处置" if writable(rel) else "越权·交 main 裁"


def scan_line(rel: str, lineno: int, line: str, tail_supersede_line: int = -1):
    """→ hit dict 或 None"""
    if not line.strip():
        return None
    if not re.search(r"rk3572|rk3576|RK3572|RK3576|ISS-155|rknn", line):
        return None

    hit_rule = None
    for rid, rx, action in RULES:
        if rx.search(line):
            hit_rule = (rid, action)
            break
    if hit_rule is None:
        return None
    rid, action = hit_rule

    # 1) 已被明确标注取代 ⇒ 历史叙述
    if SUPERSEDED_PAT.search(line):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "★已标注取代 (本行自带取代标记) | " + action)

    # 2) 路径级铁律: logs/ = 原始证据留档; HANDOFF/ = 交卷单 (历史留档, 不许改)
    if rel.startswith("logs/"):
        return _mk(rel, lineno, line, rid, VERDICT_HIST, "logs/ 原始证据留档 | " + action)
    if rel.startswith("HANDOFF/"):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "交卷单 = 历史留档 (ISS-353 铁律: 历史叙述不许改) | " + action)

    # 3) 台账追加式: 命中行之后有【切题的】取代标记 ⇒ 后条取代前条 ⇒ 历史叙述
    if rel.startswith("state/fragments/") and tail_supersede_line > lineno:
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "★台账追加式 ⇒ 命中行之后 (L%d) 已有切题取代标记 ⇒ 后条取代前条 (历史登记) | %s"
                   % (tail_supersede_line, action))

    has_strong = re.search(STRONG, line) is not None
    has_hist = re.search(HIST, line) is not None

    # 4) E1 「同代同架构」: 自己否定 / 引述 / 已标注 ⇒ 历史叙述
    if rid == "E1" and re.search(r"不是|仍是我方|推算|证伪|不能|官方结论吗|已不成立|错|自推|反证",
                                 line):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "已自己否定 / 已标注 (非官方结论) | " + action)

    # 5) D1 ISS-155 状态标签 ⇒ 交 main 裁 (不判红)
    if rid in RULE_PEND:
        return _mk(rel, lineno, line, rid, VERDICT_PEND, action)

    # 6) 弱规则 (B1/F1) ⇒ 事实/命题类 ⇒ 历史叙述
    if rid not in RULE_STRONG:
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   ("过去测得的记录 (含日期/实测/原文标记) | " if has_hist else "") + action)

    # 7) 强规则: 带强规定词 ⇒ 矛盾 (不受历史标记豁免)
    #    ★A1b 例外: 裸引号 rk3576 若出现在芯片语境 (BSP/runtime/SDK…) ⇒ 不算「转换 target」★
    if rid == "A1b" and CHIP_CTX.search(line):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "芯片语境 (BSP/runtime/SDK/模组…) ⇒ 讲的是芯片不是转换 target | " + action)
    # ★F7: 否定语境 (「官方不存在…关于 rk3576 的表述」) = 陈述官方没说过 ⇒ 事实类, 不算旧口径结论
    if rid in ("A1", "A1b", "A2") and NEG_CTX.search(line):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "★否定语境 (官方层不存在该表述 ⇒ [0数据] 命题) | " + action)
    if has_strong:
        return _mk(rel, lineno, line, rid, VERDICT_STALE, action)

    # 8) 强规则 + 只有历史标记 (无强规定词) ⇒ 历史叙述
    if has_hist:
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "过去测得的记录 (含日期/实测/原文标记) | " + action)

    # 9) 代码/脚本行 ⇒ 现状陈述 ⇒ 历史叙述 (F4)
    if CODEISH.search(line):
        return _mk(rel, lineno, line, rid, VERDICT_HIST,
                   "代码/脚本现状陈述 (描述脚本当前行为, 非口径结论) | " + action)

    return _mk(rel, lineno, line, rid, VERDICT_STALE, action)


def _mk(rel, lineno, line, rid, verdict, action):
    return {"file": rel, "line": lineno, "rule": rid, "verdict": verdict,
            "snippet": snippet(line), "action": action, "channel": channel(rel)}


# ── 闸自身输出的回显文件 (★含本闸表头的文件 = 本闸自己的输出回显 ⇒ 跳过, 避免自引用把命中数吹大★) ──
ECHO_MARK = "rk3572 目标口径清账闸"


def iter_files(root: str):
    self_name = os.path.basename(__file__)
    for r in SCAN_ROOTS:
        base = os.path.join(root, r)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames
                           if d not in ("__pycache__", ".cache_iss244", ".git")]
            for fn in sorted(filenames):
                if fn == self_name:
                    continue          # ★不扫自己 (闸脚本里写着那些正则, 不算旧口径★)
                p = os.path.join(dirpath, fn)
                if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                    continue
                try:
                    if os.path.getsize(p) > MAX_BYTES:
                        continue
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        head = fh.read(8192)
                    if ECHO_MARK in head:
                        continue      # ★本闸自己的输出回显 ⇒ 跳过 (防自引用)★
                except OSError:
                    continue
                yield p, os.path.relpath(p, root)


def scan(root: str):
    hits, files = [], 0
    for p, rel in iter_files(root):
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        files += 1
        lines = text.splitlines()
        tail = -1
        if rel.startswith("state/fragments/"):
            for i, ln in enumerate(lines, 1):
                if SUPERSEDED_PAT.search(ln) and LEDGER_TOPIC.search(ln):
                    tail = i
        for i, line in enumerate(lines, 1):
            h = scan_line(rel, i, line, tail)
            if h:
                hits.append(h)
    hits.sort(key=lambda h: (h["file"], h["line"]))
    return files, hits


def report(root: str, files: int, hits: list) -> None:
    stale = [h for h in hits if h["verdict"] == VERDICT_STALE]
    pend = [h for h in hits if h["verdict"] == VERDICT_PEND]
    hist = [h for h in hits if h["verdict"] == VERDICT_HIST]
    print("=" * 78)
    print("ISS-353 · rk3572 目标口径清账闸 · 只读扫描 (v2.0)")
    print("=" * 78)
    print("root            : %s" % root)
    print("扫面            : %s" % " / ".join(SCAN_ROOTS))
    print("扫描文本文件数  : %d" % files)
    print("命中行数        : %d  (结论矛盾=%d · 结论待裁=%d · 历史叙述=%d)"
          % (len(hits), len(stale), len(pend), len(hist)))
    print("")
    print("─── ★【名单】★ 逐条: 文件 + 行号 + 原文片段 + 判定 + 处置建议 + 处置通道 ───")
    print("(★只报数量不算交卷★ ⇒ 本表必须整份带走★)")
    print("")
    cur = None
    for h in hits:
        if h["file"] != cur:
            cur = h["file"]
            print("\n◆ %s" % cur)
        print("   L%-6d [%s] %s" % (h["line"], h["rule"], h["verdict"]))
        print("      原文: %s" % h["snippet"])
        print("      处置: %s" % h["action"])
        print("      通道: %s" % h["channel"])
    print("")
    print("=" * 78)
    if stale:
        in_scope = [h for h in stale if h["channel"] == "本单可处置"]
        out_scope = [h for h in stale if h["channel"] != "本单可处置"]
        print("★结论: 仍有 %d 条「结论矛盾(要处置)」⇒ 旧口径没清干净 ⇒ rc=1" % len(stale))
        print("  · 本单可处置残留 : %d 条" % len(in_scope))
        print("  · 越权交 main 裁  : %d 条  (逐字替换文本见交卷页 §B1.2 + "
              "logs/iss353/apply_caliber_dispositions.py)" % len(out_scope))
    else:
        print("★结论: 全仓无「结论矛盾(要处置)」⇒ 旧口径已清 ⇒ rc=0")
    if pend:
        print("  · 结论待裁(交 main 裁): %d 条 (ISS-155 定位 / 状态标签 ⇒ sw-lead 不代拍)" % len(pend))
    print("=" * 78)


# ── 反向自测 (★故意留一条旧结论在临时副本里 ⇒ 必须被抓出来★) ─────────────────
SELFTEST_FIXTURES = {
    # 新口径三句 ⇒ 不许被判成结论矛盾
    "A_clean_new_caliber.md": (
        "# 新口径样例\n"
        "★★**toolkit2 (2.3.2 / 2.5.0) 不支持 rk3572 target** ⇒ [官网]+[实测]\n"
        "★★**rknn3-toolkit 1.2.0 支持 `target_platform='rk3572'`** ⇒ [实测]\n"
        "★★**板端接受性仍 [0数据]** ⇒ 降级方案 = 板到手一条命令出 PASS/FAIL\n"
    ),
    # 反向用例: 故意留一条旧结论 ⇒ 必须被抓出来
    "B_stale_conclusion.md": (
        "# 旧口径样例\n"
        "★★**只能用 `'rk3576'`** ⇒ 在 RK3572 上也必须用 `target_platform='rk3576'` 转\n"
    ),
    # 已标注取代 ⇒ 判历史叙述(可留)
    "C_superseded.md": (
        "# 已取代样例\n"
        "★★**只能用 `'rk3576'`** ⇒ ★已由 ISS-263 (rknn3-toolkit 1.2.0 支持 rk3572) "
        "取代·本条保留作历史留档·结论不再引用★\n"
    ),
    # 纯历史叙述 (日期+实测+原文) ⇒ 判历史叙述(可留)
    "D_historical.md": (
        "# 历史叙述样例\n"
        "★★2026-11-02 实测: `config(target_platform='rk3572')` 抛 "
        "`ValueError: Invalid target_platform 'rk3572'!`\n"
    ),
    # ★F1 回归: 旧版 R2 误报样本 (DSI 网表行: 「已随 RK3572 删除」+「必须拆」) ⇒ 不许判矛盾
    "E_dsi_netlist_false_positive.md": (
        "| DSI_D0_CK_P | R_SEL_CK_P | CONN_LIGHT pin6 | R_SEL_CK_P | 0Ω | R | 必装 | MAIN_PCB | "
        "[官方] | TBD-04 | [DSI_D0_CK_P] DSI 直通位 (SoC 原生 DSI → 光机; "
        "★方案B 已随 RK3572 删除, 此位是**唯一通路**) — ★规格位 R_SEL_* 必须拆 |\n"
    ),
    # 代码行 ⇒ 判历史叙述(可留) (现状陈述)
    "F_code_line.md": (
        "r=RKNN(verbose=False); print('config', r.config(target_platform='rk3576'))\n"
    ),
    # 「用 `target_platform='rk3576'` 转」省略写法 (F3 回归: 24 字窗口) ⇒ 必须被抓出来
    "G_ellipsis_form.md": (
        "★**用 `target_platform='rk3576'` 转** 产物直接上 RK3572 板\n"
    ),
    # 「不存在升级就有 rk3572 的路」⇒ 必须被抓出来 (C1)
    "H_no_upgrade_path.md": (
        "★★ `rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform` —— "
        "从 2.2.0 到最新 2.5.0 全部拒绝, **不存在\"升级到某版本就有 rk3572\"这个选项**。\n"
    ),
    # ★F8 回归: 台账里一条【与本口径无关】的取代标记不许把旧条目误判成「已被取代」
    "state/fragments/ledger_unrelated.md": (
        "★**旧登记**: RK3572 NPU 与 RK3576 **同代同架构** ⇒ 用 `target_platform='rk3576'` 转换\n"
        "★**无关的取代标记**: 12→15mm 投板前必须 close」已由 ISS-346 / ISS-350 分档口径取代 · "
        "本条保留作历史留档 · 结论不再引用**★\n"
    ),
    # ★F8 回归: 台账里一条【切题的】取代标记 ⇒ 旧条目判历史叙述(可留)
    "state/fragments/ledger_related.md": (
        "★**旧登记**: RK3572 NPU 与 RK3576 **同代同架构** ⇒ 用 `target_platform='rk3576'` 转换\n"
        "★**切题的取代标记**: 已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代·"
        "本条保留作历史留档·结论不再引用**★\n"
    ),
}


def _selftest_tmpdir(root: str) -> str:
    """★沙盒强制落项目盘 (★不许写 /tmp★)"""
    base = os.environ.get("ISS353_TMPDIR") or os.path.join(root, "tmp")
    os.makedirs(base, exist_ok=True)
    return base


def selftest(root: str) -> int:
    ok, total = 0, 0
    base = _selftest_tmpdir(root)
    td = os.path.join(base, "iss353_selftest_%d" % os.getpid())
    shutil.rmtree(td, ignore_errors=True)
    try:
        fdir = os.path.join(td, "SW")
        os.makedirs(fdir, exist_ok=True)
        for name, body in SELFTEST_FIXTURES.items():
            if name.startswith("state/fragments/"):
                # ★台账夹具必须落在 state/fragments/ 下, 否则 F5/F8 台账规则不生效★
                tgt = os.path.join(td, name)
                os.makedirs(os.path.dirname(tgt), exist_ok=True)
            else:
                tgt = os.path.join(fdir, name)
            with open(tgt, "w", encoding="utf-8") as f:
                f.write(body)

        def stale_of(hits, fname):
            return [h for h in hits if h["verdict"] == VERDICT_STALE
                    and os.path.basename(h["file"]) == fname]

        _, hits = scan(td)

        # 1) 反向用例: 故意留的旧结论必须被抓出来
        total += 1
        named = stale_of(hits, "B_stale_conclusion.md")
        if named:
            print("  ✅ 反向用例1: 故意留的旧结论被抓出来 ⇒ %s L%d (规则 %s)"
                  % (named[0]["file"], named[0]["line"], named[0]["rule"]))
            ok += 1
        else:
            print("  ❌ 反向用例1 FAIL: 故意留的旧结论没被抓出来")

        # 2) 新口径三句不许被误判
        total += 1
        if not stale_of(hits, "A_clean_new_caliber.md"):
            print("  ✅ 反向用例2: 新口径三句没被误判")
            ok += 1
        else:
            print("  ❌ 反向用例2 FAIL: 新口径被误判成结论矛盾")

        # 3) 已标注取代 ⇒ 历史叙述(可留)
        total += 1
        sup = [h for h in hits if os.path.basename(h["file"]) == "C_superseded.md"]
        if sup and sup[0]["verdict"] == VERDICT_HIST:
            print("  ✅ 反向用例3: 已标注取代的行判「历史叙述(可留)」")
            ok += 1
        else:
            print("  ❌ 反向用例3 FAIL: 已标注取代的行没被判成历史叙述 (%s)" % (sup or "没命中"))

        # 4) 纯历史叙述 ⇒ 历史叙述(可留)
        total += 1
        hh = [h for h in hits if os.path.basename(h["file"]) == "D_historical.md"]
        if hh and hh[0]["verdict"] == VERDICT_HIST:
            print("  ✅ 反向用例4: 历史叙述判「历史叙述(可留)」")
            ok += 1
        else:
            print("  ❌ 反向用例4 FAIL: 历史叙述被判成结论矛盾 (%s)" % (hh or "没命中"))

        # 5) ★F1 回归: 旧版 R2 误报样本 (DSI 网表行) 不许判矛盾
        total += 1
        if not stale_of(hits, "E_dsi_netlist_false_positive.md"):
            print("  ✅ 反向用例5: F1 回归 —— DSI 网表行 (RK3572…必须…) 不再被误判成结论矛盾")
            ok += 1
        else:
            print("  ❌ 反向用例5 FAIL: F1 回归 —— DSI 网表行仍被误判")

        # 6) 代码行 ⇒ 历史叙述(可留)
        total += 1
        cf = [h for h in hits if os.path.basename(h["file"]) == "F_code_line.md"]
        if not stale_of(hits, "F_code_line.md"):
            print("  ✅ 反向用例6: 代码/脚本现状陈述判「历史叙述(可留)」")
            ok += 1
        else:
            print("  ❌ 反向用例6 FAIL: 代码行被判成结论矛盾 (%s)" % (cf or "没命中"))

        # 7) F3 回归: 「用 `target_platform='rk3576'` 转」省略写法必须被抓出来
        total += 1
        g = stale_of(hits, "G_ellipsis_form.md")
        if g:
            print("  ✅ 反向用例7: F3 回归 —— 省略写法 (用 `target_platform='rk3576'` 转) 被抓出来 ⇒ L%d"
                  % g[0]["line"])
            ok += 1
        else:
            print("  ❌ 反向用例7 FAIL: 省略写法没被抓出来")

        # 8) C1 回归: 「不存在升级就有 rk3572 的路」必须被抓出来
        total += 1
        h = stale_of(hits, "H_no_upgrade_path.md")
        if h:
            print("  ✅ 反向用例8: C1 回归 —— 「不存在升级就有 rk3572 的路」被抓出来 ⇒ L%d (规则 %s)"
                  % (h[0]["line"], h[0]["rule"]))
            ok += 1
        else:
            print("  ❌ 反向用例8 FAIL: C1 没抓到")

        # 9) 闸不是恒红: 删掉旧结论后 ⇒ 必须 0 条矛盾
        total += 1
        os.remove(os.path.join(fdir, "B_stale_conclusion.md"))
        os.remove(os.path.join(fdir, "G_ellipsis_form.md"))
        os.remove(os.path.join(fdir, "H_no_upgrade_path.md"))
        os.remove(os.path.join(td, "state/fragments/ledger_unrelated.md"))  # ★它本就是故意留的旧结论夹具★
        _, hits2 = scan(td)
        if not [h for h in hits2 if h["verdict"] == VERDICT_STALE]:
            print("  ✅ 反向用例9: 删掉旧结论后 ⇒ 0 条结论矛盾 ⇒ 闸会转 rc=0 (不是恒红)")
            ok += 1
        else:
            print("  ❌ 反向用例9 FAIL: 删掉旧结论后仍有 %d 条"
                  % len([h for h in hits2 if h["verdict"] == VERDICT_STALE]))

        # 10) 沙盒没写 /tmp (★/tmp 配额已打满★)
        total += 1
        if td.startswith(base) and base.startswith(root):
            print("  ✅ 反向用例10: 自测沙盒落在项目盘 (%s) ⇒ 没写 /tmp" % base)
            ok += 1
        else:
            print("  ❌ 反向用例10 FAIL: 自测沙盒不在项目盘 (%s)" % td)

        # 11) F8 回归: 台账里【无关】的取代标记不许把旧条目误判成已被取代
        total += 1
        unrel = [h for h in hits if h["file"].endswith("ledger_unrelated.md")
                 and h["verdict"] == VERDICT_STALE]
        if unrel:
            print("  ✅ 反向用例11: F8 回归 —— 台账里的无关取代标记没把旧条目误判成已被取代 ⇒ L%d"
                  % unrel[0]["line"])
            ok += 1
        else:
            print("  ❌ 反向用例11 FAIL: F8 —— 无关取代标记把旧条目误判成历史叙述")

        # 12) F8 回归: 台账里【切题的】取代标记 ⇒ 旧条目判历史叙述(可留)
        total += 1
        rel_hits = [h for h in hits if h["file"].endswith("ledger_related.md")]
        if rel_hits and rel_hits[0]["verdict"] == VERDICT_HIST:
            print("  ✅ 反向用例12: F8 回归 —— 切题的取代标记把旧条目判成历史叙述(可留)")
            ok += 1
        else:
            print("  ❌ 反向用例12 FAIL: F8 —— 切题取代标记没把旧条目判成历史叙述 (%s)" % (rel_hits or "没命中"))
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("SELFTEST %d/%d 通过, rc=%d" % (ok, total, 0 if ok == total else 1))
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="扫别的目录 (selftest 用); 默认 = 本脚本上两级")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if args.selftest:
        print("### ISS-353 清账闸 · 反向自测 (沙盒落项目盘 tmp/) ###")
        return selftest(root)

    files, hits = scan(root)
    stale = [h for h in hits if h["verdict"] == VERDICT_STALE]
    if args.json:
        print(json.dumps({"root": root, "files": files, "hits": hits,
                          "stale_count": len(stale)}, ensure_ascii=False, indent=2))
    else:
        report(root, files, hits)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
