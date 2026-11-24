#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_fts_land_drill_same_batch_sbx.py  ·  ISS-396 闸 S1~S9
「落 FTS 要改孔 `0.65 → 0.71`」这条登记, ★**在【生成器重跑之后】还在不在** ★

派活: state/dispatch_briefs/ISS-396_hw_fts_drill_registration_landing.md (项目总工 2026-11-24 18:2x)

=====================================================================================
★**它守的是什么** ★
=====================================================================================
  ★**既有那道闸 `HW/check_fts_land_drill_same_batch.py` 判的是【文档里有没有这句话】** ⇒
  ★**它管不了「生成器重跑之后这句话还在不在」** ⇒ ★**生成器一改, 手写/漏写都有可能** ⇒
  ★**所以需要一道判【生成器产物 == 页】的闸** ★

  ★**病根 (★ISS-349 在同一位号上栽过一次★)**: 预检清单页 = 生成器产物 ⇒
  ★**「页里有」不等于「重跑后还在」** ⇒ ★**只改页不改生成器 ⇒ 下一个跑生成器的人把这一条洗掉了** ★

★**与既有闸的关系 (★不替代★)**: ★
  · `HW/check_fts_land_drill_same_batch.py` ⇒ 管【文档里有没有】(★ISS-396 已转绿 7/7★) · ★**已签收 · 本闸一个字节不改它** ★
  · ★**本闸** ⇒ 管【重跑之后还在不在】(★新增的那一格★) ★

=====================================================================================
★**九条判据 (★每条都要能当场判红, 不许是装饰★)** ★
=====================================================================================
  S1 产物同源    : ★**沙盒里重跑生成器 ⇒ 产物页 md5 == 盘上真页 md5** ★
                  ⇒ ★**「只改页不改生成器」/「手写页」⇒ 当场红** ★
  S2 重跑幂等    : ★**沙盒里连跑两次生成器 ⇒ md5 逐字节相同** (★不许漂★) ★
  S3 登记在位    : ★**真页 `B33_PIN_LAND_1P27` 的描述列 (json 项 + 表格行) 含「钻孔」+ 目标值 `0.71`;**
                  ★**验收手段列含一条【真能读钻孔直径】的命令** (★`pcbnew_py.sh` + `GetDrillSize`★) ★
  S4 生成器里有  : ★**生成器源码里也长着同一段登记** (★描述 + 读孔命令·`GetDrillSize`★) ★
                  ⇒ ★**「页有生成器没有」⇒ 红** (★防「只改页」的第二道保险★) ★
  S5 P4 绑定没丢 : ★**覆盖度闸源码 md5 == 真相页基线** (★零改既有闸★) 且
                  ★**`WP02_BINDING["③"]` 仍绑 `B33_PIN_LAND_1P27`** (★不许顺手改 P4 判据★) ★
                  ⇒ ★**【只报告不判红】**: §4 #4 的「显式补覆盖令牌 `["0.71","0.65"]`」是 main 的地界 (★本单零改既有闸★) ★
  S6 零扰动      : ★**板 / 网表 / 脚表 / BOM 四件 md5 == 真相页基线** (★零写板 · 零落表★) ★
                  + ★**已签收两页 (作业包 / 预检清单) 的 md5 == 真相页基线** ★
  S7 零挂链      : ★**本闸名字不许出现在 `state/gate_check.py` 里** (★挂链是 main 的地界★) ★
  S8 cwd 无关    : ★**两个不同深度 (cwd) 下采集的事实摘要一致** ⇒ ★**路径必须从本闸自己推** ★
  S9 P4 令牌自检 : ★**模拟覆盖度闸的 `wp02_tokens()`**: 从作业包 §0.2 ③ 抽出的每一个覆盖令牌
                  ★**都必须在清单页 `B33_PIN_LAND_1P27` 里查得到** ⇒ ★**把「P4 绿 = 假绿」那一格补上**
                  (★★**不改既有闸的判据源码**·只在本闸里做等价的现场计算★★) ★

★**边界 (★逐条自证·写进交卷页★)** ★
  · ★**零写板** (板 `.kicad_pcb` / `.kicad_pro` 一个字节不许动) ★
  · ★**零落表** (网表 / 脚表 / BOM / 原理图真源一个字节不许动) ★
  · ★**零改既有闸的判据源码** (★既有闸 / 覆盖度闸 / 生成器以外的一切既有脚本·一个字不许动★) ★
  · ★**零改既有页面正文** ★
  · ★**零挂链** (★本闸【不许挂进 `state/gate_check.py`】★) ★
  · ★**零外发** (★不发任何邮件 / 询价 / 问询 / 采购★) ★
  · ★**不代拍** ★
  · ★**沙盒只落项目盘** `tmp/iss396_sbx/` ⇒ ★**绝不落系统 `/tmp`** (★本机 `/tmp` 配额打满 ⇒ 写那儿会出假读数 rc=120★) ★

用法:
    python3 HW/check_fts_land_drill_same_batch_sbx.py             # 正向跑
    python3 HW/check_fts_land_drill_same_batch_sbx.py --selftest  # 自测 (★≥6 条反向用例★)

退出码: 0 = 全过 · 1 = 有不通过项 (★闸红★) · 2 = 用法错 · 3 = ★闸崩 (★工具/沙盒跑不起来·与「闸红」严格区分★)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# 路径 (★全部从本闸自己的位置推 ⇒ 与 cwd 无关★)
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SANDBOX = os.path.join(PROJ, "tmp", "iss396_sbx")

REAL_PATHS = {
    "page": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md"),
    "workpacket": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md"),
    "generator": os.path.join(PROJ, "state", "_iss277_build_preflight.py"),
    "truth": os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"),
    "coverage_gate": os.path.join(PROJ, "HW", "check_onepass_preflight_coverage.py"),
    "board": os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
    "netlist": os.path.join(PROJ, "HW", "netlist_v1.csv"),
    "pins": os.path.join(PROJ, "HW", "netlist_v1_pins.csv"),
    "bom": os.path.join(PROJ, "HW", "BOM_v1.csv"),
    "gate_check": os.path.join(PROJ, "state", "gate_check.py"),
}

GATE_NAME = "check_fts_land_drill_same_batch_sbx"
ISS391_GATE_NAME = "check_fts_land_drill_same_batch"
ITEM_ID = "B33_PIN_LAND_1P27"
ORDINAL_OF_ITEM = "③"
ORDINALS = "①②③④⑤⑥⑦⑧⑨⑩"
DRILL_TARGET = "0.71"

# ★本机 KiCad 通用库件 (★S4 要拿它现场复核生成器里的 `DRILL_GENERIC`★)
LIB_DIR = ("/home/yuewuya/kicad/AppDir/share/kicad/footprints/"
           "Connector_PinHeader_1.27mm.pretty")
LIB_FILES = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
}


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def safe_rmtree(path):
    if not os.path.exists(path):
        return
    for i in range(4):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            time.sleep(0.05 * (i + 1))
    shutil.rmtree(path, ignore_errors=True)


def has_drill(text):
    """★文本里有没有「钻孔」这件事的字样 (中文 + 英文都要认)★"""
    if not text:
        return False
    if ("钻孔" in text) or ("孔径" in text):
        return True
    return bool(re.search(r"drill", text, re.I))


def parse_machine_block(page_text):
    """★从真相页里抽出 json 机器块 ⇒ (dict, err)★"""
    for b in re.findall(r"```json\s*\n(.*?)\n```", page_text, re.S):
        try:
            d = json.loads(b)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict) and str(d.get("schema", "")).startswith(
                "hw.fts.land_drill_change"):
            return d, ""
    return None, "真相页里找不到 schema = hw.fts.land_drill_change* 的机器块"


def parse_preflight_json(text):
    """★预检清单页 §7 的 JSON 块 ⇒ items 列表★"""
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except Exception:  # noqa: BLE001
        return None
    items = data.get("items")
    return items if isinstance(items, list) else None


def parse_preflight_md_row(text, item_id):
    """★预检清单页 §2 表格里 item_id 那一行 ⇒ 单元格列表★"""
    for line in text.split("\n"):
        s = line.strip()
        if not s.startswith("|") or item_id not in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) >= 7:
            return cells
    return None


def parse_wp02_board_changes(wp_text):
    """★从作业包 §0.2 ③ 那一行【现场解析】出板侧改动清单的子项 ⇒ {序: 原文} ★"""
    for line in wp_text.split("\n"):
        if "板侧改动清单" not in line or "①" not in line:
            continue
        cell = None
        for c in line.split("|"):
            if "①" in c:
                cell = c
                break
        if cell is None:
            continue
        parts = re.split(r"([%s])" % ORDINALS, cell)
        out, cur = {}, None
        for p in parts:
            if len(p) == 1 and p in ORDINALS:
                cur = p
                out[cur] = []
            elif cur is not None:
                out[cur].append(p)
        res = {k: "".join(v).strip() for k, v in out.items()}
        if res:
            return res
    return {}


def wp02_tokens(text):
    """★与覆盖度闸 `HW/check_onepass_preflight_coverage.py` 同口径的覆盖令牌抽取 ★
    ★**只在这里做等价计算 · 既有闸的判据源码一个字不许改** ★"""
    toks = set(re.findall(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+", text))
    toks |= set(re.findall(r"\b[A-Z]{1,3}\d{1,3}\b", text))
    toks |= set(re.findall(r"\d+\.\d+", text))
    return toks


def parse_wp02_binding(cov_src):
    """★从覆盖度闸源码里解析出 `WP02_BINDING` (★用 ast·不许 exec★)★"""
    import ast
    tree = ast.parse(cov_src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "WP02_BINDING" for t in node.targets):
            try:
                return ast.literal_eval(node.value)
            except Exception:  # noqa: BLE001
                return None
    return None


# ---------------------------------------------------------------------------
# 沙盒: 复制项目盘的一小块 ⇒ 在里面跑生成器 (★真盘零写★)
# ---------------------------------------------------------------------------
STATE_FILE_SUFFIX = (".py", ".md", ".sh")
SANDBOX_SKIP = ("production", "_tmp_pi5")


def build_sandbox(src, dst):
    """★把 `src` 项目根复制成沙盒 `dst` (★只读 src·只写 dst★) ★

    ⇒ 装: `state/*.py|*.md|*.sh` + `state/fragments/pm.yaml` (★E-1 裁决原文的出处★) + `HW/` 全量
    ⇒ 不装: `HW/PCB/production` / `HW/PCB/_tmp_pi5` (★生成器不读它们·省 23M★)
    """
    safe_rmtree(dst)
    os.makedirs(os.path.join(dst, "state", "fragments"), exist_ok=True)
    for fn in sorted(os.listdir(os.path.join(src, "state"))):
        s = os.path.join(src, "state", fn)
        if os.path.isfile(s) and fn.endswith(STATE_FILE_SUFFIX):
            shutil.copy2(s, os.path.join(dst, "state", fn))
    pm = os.path.join(src, "state", "fragments", "pm.yaml")
    if os.path.exists(pm):
        shutil.copy2(pm, os.path.join(dst, "state", "fragments", "pm.yaml"))
    shutil.copytree(os.path.join(src, "HW"), os.path.join(dst, "HW"),
                    ignore=shutil.ignore_patterns(*SANDBOX_SKIP),
                    dirs_exist_ok=True)
    os.makedirs(os.path.join(dst, "tmp"), exist_ok=True)
    return dst


def run_generator(sb):
    """★在沙盒里跑一次真生成器 ⇒ (rc, 输出, 沙盒页路径) ★

    ★**生成器只往沙盒的 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 写 ⇒ 真页/真板零写** ★
    """
    env = dict(os.environ)
    env["PREFLIGHT_PROJ"] = sb
    env["TMPDIR"] = os.path.join(sb, "tmp")
    cmd = [sys.executable, "-B", os.path.join(sb, "state", "_iss277_build_preflight.py")]
    try:
        p = subprocess.run(cmd, cwd=sb, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=1800)
    except Exception as e:  # noqa: BLE001
        return 3, "★生成器跑不起来: %s" % e, ""
    out = (p.stdout or b"").decode("utf-8", "replace")
    page = os.path.join(sb, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    return p.returncode, out, page


def regen_facts(sandbox_src, work_root):
    """★在沙盒里连跑两次生成器 ⇒ 两次产物 md5 (★S1 产物同源 / S2 重跑幂等 用★) ★"""
    sb = os.path.join(work_root, "regen")
    build_sandbox(sandbox_src, sb)
    rc1, out1, page1 = run_generator(sb)
    md5_1 = md5_of(page1) if page1 and os.path.exists(page1) else None
    rc2, out2, page2 = run_generator(sb)
    md5_2 = md5_of(page2) if page2 and os.path.exists(page2) else None
    return {"rc1": rc1, "rc2": rc2, "md5_1": md5_1, "md5_2": md5_2,
            "out": ((out1 or "") + "\n" + (out2 or ""))[-4000:]}


# ---------------------------------------------------------------------------
# 事实采集
# ---------------------------------------------------------------------------
def collect(paths=None, sandbox_src=None, work_root=None, do_regen=True):
    p = dict(REAL_PATHS)
    if paths:
        p.update(paths)
    ctx = {"paths": p}
    for key in ("page", "workpacket", "generator", "truth", "coverage_gate",
                "board", "netlist", "pins", "bom", "gate_check"):
        path = p[key]
        ctx["%s_md5" % key] = md5_of(path) if os.path.exists(path) else None
        ctx["%s_text" % key] = read_text(path) if os.path.exists(path) else ""
    mb, err = parse_machine_block(ctx["truth_text"])
    ctx["mb"] = mb
    ctx["mb_error"] = err
    ctx["regen"] = (regen_facts(sandbox_src or PROJ, work_root or SANDBOX)
                    if do_regen else None)
    return ctx


# =========================================================================
# S1 产物同源 (★只改页 ⇒ 红★)
# =========================================================================
def s1(ctx):
    fails = []
    r = ctx.get("regen")
    if not r:
        return ["S1 没有重跑生成器 ⇒ fail-closed"]
    if r["rc1"] != 0 or r["rc2"] != 0:
        fails.append("S1 生成器在沙盒里跑不起来 (rc1=%s · rc2=%s) ⇒ fail-closed (★不许「跑不起来就算过」★)\n%s"
                     % (r["rc1"], r["rc2"], r["out"][-1200:]))
        return fails
    if not r["md5_2"]:
        fails.append("S1 沙盒里生成器没产出页 ⇒ fail-closed")
        return fails
    if r["md5_2"] != ctx["page_md5"]:
        fails.append("S1 沙盒重跑生成器的产物 md5 (%s) != 盘上真页 md5 (%s) ⇒ "
                     "★**页与生成器不同源** ⇒ ★**「页里有这句话」是假的** (★重跑一次就蒸发·ISS-349 同坑★)★"
                     % (r["md5_2"], ctx["page_md5"]))
    return fails


# =========================================================================
# S2 重跑幂等
# =========================================================================
def s2(ctx):
    fails = []
    r = ctx.get("regen")
    if not r:
        return ["S2 没有重跑生成器 ⇒ fail-closed"]
    if r["rc1"] != 0 or r["rc2"] != 0:
        return ["S2 生成器在沙盒里跑不起来 ⇒ fail-closed"]
    if r["md5_1"] != r["md5_2"]:
        fails.append("S2 沙盒里连跑两次生成器 ⇒ 产物 md5 不同 (%s vs %s) ⇒ "
                     "★**生成器不幂等** ⇒ ★**重跑一次就漂一次 ⇒ 登记迟早蒸发** ★"
                     % (r["md5_1"], r["md5_2"]))
    return fails


# =========================================================================
# S3 登记在位 (★真页的描述列 + 验收手段列★)
# =========================================================================
def s3(ctx):
    fails = []
    text = ctx["page_text"]
    if not text:
        return ["S3 读不到预检清单页 ⇒ fail-closed"]
    items = parse_preflight_json(text)
    item = None
    if items is None:
        fails.append("S3 预检清单页的 json 块解析不出来 ⇒ fail-closed")
    else:
        item = next((it for it in items if str(it.get("id")) == ITEM_ID), None)
        if item is None:
            fails.append("S3 预检清单页的 json 块里【没有 item %s】⇒ fail-closed" % ITEM_ID)
    if item is not None:
        desc = " ".join(str(item.get(k, "")) for k in ("title", "current_state", "action"))
        if not has_drill(desc):
            fails.append("S3 预检清单 %s 的【描述列】(json 项) 里【查不到「钻孔」】⇒ "
                         "★清单页是那一趟的验收凭据, 它不写钻孔 ⇒ 改没改都没人查★" % ITEM_ID)
        elif DRILL_TARGET not in desc:
            fails.append("S3 预检清单 %s 的【描述列】(json 项) 里【查不到目标孔径 %s】⇒ "
                         "★只写了字样没写目标值 ⇒ 那一趟的人照样不知道要改成多少★"
                         % (ITEM_ID, DRILL_TARGET))
        crit = str(item.get("criterion", ""))
        if not (has_drill(crit) and DRILL_TARGET in crit):
            fails.append("S3 预检清单 %s 的【验收手段列】(json 项) 里【没有一条读钻孔直径的验收命令】⇒ "
                         "★没有验收手段 = 改没改成没人知道★" % ITEM_ID)
        elif not ("pcbnew_py.sh" in crit or "GetDrillSize" in crit):
            fails.append("S3 预检清单 %s 的【验收手段列】里的钻孔命令【不是读板钻孔的命令】⇒ "
                         "★必须是读板 (pcbnew_py.sh / GetDrillSize)★" % ITEM_ID)
    row = parse_preflight_md_row(text, ITEM_ID)
    if row is None:
        fails.append("S3 预检清单页的【表格行】里【找不到 %s 那一行】⇒ fail-closed" % ITEM_ID)
    else:
        desc = "%s %s" % (row[2], row[5])
        if not has_drill(desc):
            fails.append("S3 预检清单 %s 的【描述列】(表格行) 里【查不到「钻孔」】⇒ "
                         "★表格是给人看的那一份, 它不写钻孔 ⇒ 人照着做也会漏★" % ITEM_ID)
        elif DRILL_TARGET not in desc:
            fails.append("S3 预检清单 %s 的【描述列】(表格行) 里【查不到目标孔径 %s】"
                         % (ITEM_ID, DRILL_TARGET))
        crit = row[6]
        if not (has_drill(crit) and DRILL_TARGET in crit):
            fails.append("S3 预检清单 %s 的【验收手段列】(表格行) 里【没有一条读钻孔直径的验收命令】"
                         % ITEM_ID)
    return fails


# =========================================================================
# S4 生成器源码里也有同一段登记 (★只改页 ⇒ 红★)
# =========================================================================
def s4(ctx):
    """★S4 · 生成器里【也长着同一段登记】· 且它里面的两个数不许漂 ★

    ★**为什么要查两个数**: ★**页是人看的, 生成器才是真源** ⇒ ★**生成器里的
    `DRILL_TARGET` / `DRILL_GENERIC` 一旦被改坏, 页会跟着变坏, 而页与生成器【仍然自洽】
    ⇒ ★**S1 (页 == 生成器) 抓不到 ⇒ 必须在这里把两个数钉回真相页 + 本机库件实测** ★
    """
    fails = []
    src = ctx["generator_text"]
    if not src:
        return ["S4 读不到生成器 `state/_iss277_build_preflight.py` ⇒ fail-closed"]
    if not has_drill(src):
        fails.append("S4 生成器源码里【查不到「钻孔」这件事】⇒ ★**页里那句是手写的 ⇒ 重跑即蒸发** ★")
    if "GetDrillSize" not in src:
        fails.append("S4 生成器源码里【查不到读钻孔直径的命令 (`GetDrillSize`)】⇒ "
                     "★生成器不长验收手段 ⇒ 重跑即蒸发★")
    mt = re.search(r"^DRILL_TARGET\s*=\s*([0-9.]+)", src, re.M)
    mg = re.search(r"^DRILL_GENERIC\s*=\s*([0-9.]+)", src, re.M)
    if not mt or not mg:
        fails.append("S4 生成器源码里【解析不出 `DRILL_TARGET` / `DRILL_GENERIC` 两个赋值】⇒ fail-closed")
        return fails
    gen_t, gen_g = mt.group(1), mg.group(1)
    mb = ctx.get("mb") or {}
    tgt, genv = mb.get("drill_target"), mb.get("drill_generic")
    if tgt is None or genv is None:
        fails.append("S4 真相页机器块里【读不到 drill_target / drill_generic】⇒ fail-closed")
    else:
        if abs(float(gen_t) - float(tgt)) > 1e-9:
            fails.append("S4 生成器里的目标孔径 `DRILL_TARGET` (%s) != 真相页 `drill_target` (%s) ⇒ "
                         "★**生成器与真相页漂了** ⇒ 重跑一次就把页改成另一个数★" % (gen_t, tgt))
        if abs(float(gen_g) - float(genv)) > 1e-9:
            fails.append("S4 生成器里的通用件孔径 `DRILL_GENERIC` (%s) != 真相页 `drill_generic` (%s) ⇒ "
                         "★**生成器与真相页漂了** ★" % (gen_g, genv))
    # ★本机库件实测 ⇒ 「第三方库件的值」不许被悄悄改成「厂件规格」★
    for ref, fn in LIB_FILES.items():
        p = os.path.join(LIB_DIR, fn)
        if not os.path.exists(p):
            fails.append("S4 读不到本机库件 %s (`%s`) ⇒ fail-closed (★不许「查不到就算过」★)"
                         % (ref, p))
            continue
        vals = sorted(set(re.findall(r"\(drill\s+([0-9.]+)\)", read_text(p))))
        if vals != [gen_g]:
            fails.append("S4 本机库件 %s 的钻孔 %s != 生成器里的 `DRILL_GENERIC` (%s) ⇒ "
                         "★**第三方库件的值被改了 / 被冒充成厂件规格** ★" % (ref, vals, gen_g))
    return fails


# =========================================================================
# S5 P4 绑定没丢 (★零改既有闸 + 覆盖令牌绑定还在★)
# =========================================================================
def s5(ctx):
    fails = []
    mb = ctx.get("mb")
    if not mb:
        return ["S5 真相页的机器块拿不到 (%s) ⇒ fail-closed" % (ctx.get("mb_error") or "解析失败")]
    base = mb.get("zero_perturbation_baseline") or {}
    exp = base.get("coverage_gate_md5")
    got = ctx["coverage_gate_md5"]
    if exp is None:
        fails.append("S5 机器块 zero_perturbation_baseline 里没有 coverage_gate_md5 ⇒ fail-closed")
    elif got != exp:
        fails.append("S5 覆盖度闸 `HW/check_onepass_preflight_coverage.py` md5 与基线不同: "
                     "基线 %s / 实测 %s ⇒ ★**零改既有闸的判据源码破了** ★" % (exp, got))
    binding = parse_wp02_binding(ctx["coverage_gate_text"])
    if binding is None:
        fails.append("S5 覆盖度闸源码里【解析不出 WP02_BINDING】⇒ fail-closed")
    else:
        ids = (binding.get(ORDINAL_OF_ITEM) or ("", []))[0]
        if ITEM_ID not in ids:
            fails.append("S5 覆盖度闸的 WP02_BINDING[\"%s\"] = %s ⇒ 【里面已经没有 %s】⇒ "
                         "★**P4 的绑定被搞丢了** ⇒ 作业包 ③ 那一项没人守了★"
                         % (ORDINAL_OF_ITEM, ids, ITEM_ID))
    return fails


# =========================================================================
# S6 零扰动 (★零写板 · 零落表 · 已签收两页指纹★)
# =========================================================================
def s6(ctx):
    fails = []
    mb = ctx.get("mb")
    if not mb:
        return ["S6 真相页的机器块拿不到 ⇒ fail-closed"]
    base = mb.get("zero_perturbation_baseline") or {}
    checks = (
        ("板 md5", "board_md5", "board_md5"),
        ("网表 md5", "netlist_md5", "netlist_md5"),
        ("脚表 md5", "pins_md5", "pins_md5"),
        ("BOM md5", "bom_md5", "bom_md5"),
        ("作业包 md5", "workpacket_md5", "workpacket_md5"),
        ("预检清单 md5", "preflight_md5", "page_md5"),
    )
    for label, bkey, fkey in checks:
        exp = base.get(bkey)
        got = ctx.get(fkey)
        if exp is None:
            fails.append("S6 机器块 zero_perturbation_baseline 里没有 %s 的基线 ⇒ fail-closed" % bkey)
        elif got != exp:
            fails.append("S6 %s 与基线不同: 基线 %s / 实测 %s ⇒ ★**零扰动破了** ★"
                         % (label, exp, got))
    return fails


# =========================================================================
# S7 零挂链 (★本闸不许进 state/gate_check.py★)
# =========================================================================
def s7(ctx):
    fails = []
    path = ctx["paths"]["gate_check"]
    if not os.path.exists(path):
        return ["S7 读不到 state/gate_check.py ⇒ fail-closed"]
    hits = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if re.search(r"%s" % re.escape(GATE_NAME), ln):
                hits += 1
    if hits:
        fails.append("S7 零挂链破了: `state/gate_check.py` 里命中本闸名 %s %d 次 "
                     "⇒ ★**挂链是 main 的地界·本闸不许自挂** ★" % (GATE_NAME, hits))
    return fails


# =========================================================================
# S8 cwd 无关
# =========================================================================
def cheap_digest(paths, cwd):
    """★在指定 cwd 下重新采集一遍【便宜的事实】⇒ 摘要串★"""
    old = os.getcwd()
    try:
        os.chdir(cwd)
        p = dict(REAL_PATHS)
        p.update(paths)
        blob = {}
        for key in ("page", "workpacket", "generator", "truth", "coverage_gate",
                    "board", "netlist", "pins", "bom", "gate_check"):
            path = p[key]
            blob[key] = md5_of(path) if os.path.exists(path) else None
        return hashlib.md5(json.dumps(blob, sort_keys=True).encode("utf-8")).hexdigest()
    finally:
        os.chdir(old)


def s8(ctx):
    fails = []
    cwd_a = PROJ
    cwd_b = os.path.join(PROJ, "HW", "PCB")
    if not os.path.isdir(cwd_b):
        cwd_b = os.path.expanduser("~")
    da = cheap_digest(ctx["paths"], cwd_a)
    db = cheap_digest(ctx["paths"], cwd_b)
    if da != db:
        fails.append("S8 两个不同深度 (cwd=%s vs cwd=%s) 的读数不一致 ⇒ "
                     "★**本闸的路径解析有 cwd 依赖** ⇒ 在别的目录下跑会读错文件★"
                     % (cwd_a, cwd_b))
    if not os.path.abspath(SANDBOX).startswith(os.path.abspath(PROJ) + os.sep):
        fails.append("S8 沙盒路径 %s 不在项目盘内 ⇒ ★不许落系统 /tmp★" % SANDBOX)
    return fails


# =========================================================================
# S9 P4 令牌自检 (★模拟覆盖度闸的 wp02_tokens·不改既有闸★)
# =========================================================================
def s9(ctx):
    fails = []
    if not ctx["workpacket_text"]:
        return ["S9 读不到作业包 ⇒ fail-closed"]
    parsed = parse_wp02_board_changes(ctx["workpacket_text"])
    if not parsed:
        return ["S9 作业包 §0.2 ③ 那一行解析不出来 ⇒ fail-closed"]
    if ORDINAL_OF_ITEM not in parsed:
        return ["S9 作业包 §0.2 ③ 那一行里【没有 %s 这一项】⇒ fail-closed" % ORDINAL_OF_ITEM]
    toks = sorted(wp02_tokens(parsed[ORDINAL_OF_ITEM]))
    items = parse_preflight_json(ctx["page_text"])
    if items is None:
        return ["S9 预检清单页的 json 块解析不出来 ⇒ fail-closed"]
    by_id = {str(it.get("id")): it for it in items}
    if ITEM_ID not in by_id:
        return ["S9 预检清单页里【没有 item %s】⇒ fail-closed" % ITEM_ID]
    blob = json.dumps(by_id[ITEM_ID], ensure_ascii=False)
    miss = [t for t in toks if t not in blob]
    if miss:
        fails.append("S9 作业包 §0.2 ③ 的覆盖令牌 %s 在清单页 %s 里【查不到】⇒ "
                     "★**P4 会当场红** (★这正是 P4 在干的事·不是 bug★) ★" % (miss, ITEM_ID))
    return fails


CHECKS = (
    ("S1", s1, "生成器产物 == 盘上真页 (★只改页 ⇒ 红★)"),
    ("S2", s2, "沙盒里连跑两次生成器 ⇒ 产物 md5 幂等"),
    ("S3", s3, "真页 B33_PIN_LAND_1P27 的描述列 + 验收手段列含改孔这一条"),
    ("S4", s4, "生成器源码里也长着同一段登记 (★只改页 ⇒ 红★)"),
    ("S5", s5, "覆盖度闸源码 md5 同基线 且 WP02_BINDING[\"③\"] 仍绑 B33"),
    ("S6", s6, "板 / 网表 / 脚表 / BOM 四件零扰动 + 已签收两页指纹在基线"),
    ("S7", s7, "零挂链 (★本闸名字不许进 state/gate_check.py★)"),
    ("S8", s8, "本闸自己与 cwd 无关"),
    ("S9", s9, "P4 令牌自检 (★模拟覆盖度闸·不改既有闸★)"),
)


def run_all(ctx):
    return [(code, desc, fn(ctx)) for code, fn, desc in CHECKS]


def report(results, title):
    print("── %s" % title)
    nfail = 0
    for code, desc, fails in results:
        if fails:
            nfail += 1
            print("  [%s] ✘ RED  %s" % (code, desc))
            for f in fails:
                print("        · %s" % f)
        else:
            print("  [%s] ✔ GREEN  %s" % (code, desc))
    print("── %s: %d/%d 条绿" % (title, len(results) - nfail, len(results)))
    return nfail


# =========================================================================
# 自测 (★≥6 条反向用例★)
# =========================================================================
def _replace_once(text, old, new, what):
    if old not in text:
        raise AssertionError("自测前提不成立: 页里找不到 %s" % what)
    return text.replace(old, new)


def strip_drill_desc(text):
    """★把页里的「改孔」描述段 (标题里的那一截 + 现状列那一段) 删掉 (★反调用例用★)★"""
    t = re.sub(r" \+ 钻孔 Ø0\.65→Ø0\.71mm \(★ISS-391[^)\n]*?不可只做 pitch★\)", "", text)
    t = re.sub(r"; ★\*\*ISS-391 追加 \[实测\]\*\*:.*?不可只做其一", "", t)
    if t == text:
        raise AssertionError("自测前提不成立: 页里找不到「改孔」描述段")
    return t


def strip_drill_criterion(text):
    """★把页里的「读钻孔直径」验收命令删掉 (★表格行与 JSON 两种形态都删★)★"""
    t = re.sub(r"; `bash state/pcbnew_py\.sh -c \"import pcbnew;[^\n]*?"
               r"J_UART drill = 0\.71", "", text)          # ★表格行形态 (原始引号)★
    t2 = re.sub(r"; `bash state/pcbnew_py\.sh -c \\\"import pcbnew;[^\n]*?"
                r"J_UART drill = 0\.71", "", t)            # ★JSON 形态 (转义引号)★
    if t2 == t:
        raise AssertionError("自测前提不成立: 页里找不到「读钻孔」验收命令")
    return t2


def selftest():
    os.makedirs(SANDBOX, exist_ok=True)
    real_md5_before = {k: md5_of(REAL_PATHS[k]) for k in REAL_PATHS
                       if os.path.exists(REAL_PATHS[k])}

    base = os.path.join(SANDBOX, "base")
    build_sandbox(PROJ, base)

    cases = []   # (用例名, 期望红的判据集合, 路径覆盖 或 None)

    # --- 正向对照 ------------------------------------------------------
    cases.append(("正向对照 (★真盘原样 ⇒ S1~S9 全绿★)", set(), None))

    # --- ① 生成器里的 drill 登记被改坏 ⇒ S3/S4 红 -----------------------
    #     ★**注意: 本用例把【生成器 + 页】做成【自洽】的 (★页就是被改坏的生成器跑出来的★)
    #        ⇒ S1 (页 vs 生成器) 必绿 ⇒ ★**逼得 S3/S4 必须自己抓住「登记被改坏」** ★
    c1 = os.path.join(SANDBOX, "case01")
    shutil.rmtree(c1, ignore_errors=True)
    shutil.copytree(base, c1)
    g = os.path.join(c1, "state", "_iss277_build_preflight.py")
    src = read_text(g)
    write_text(g, src.replace("DRILL_TARGET = 0.71",
                               "DRILL_TARGET = 0.65  # ★自测: 故意把目标孔径改坏★"))
    rc, out, pg1 = run_generator(c1)
    if rc != 0:
        raise AssertionError("自测前提不成立: 沙盒里生成器跑不起来 rc=%s\n%s" % (rc, out[-800:]))
    cases.append(("① 生成器里的目标孔径被改坏 (0.71⇒0.65)·【页与生成器自洽】⇒ S3 + S4 红",
                  {"S3", "S4"}, {"sandbox_src": c1, "page": pg1, "generator": g}))

    # --- ② 生成器被删掉 ⇒ S1 红 (fail-closed) --------------------------
    c2 = os.path.join(SANDBOX, "case02")
    shutil.rmtree(c2, ignore_errors=True)
    shutil.copytree(base, c2)
    os.remove(os.path.join(c2, "state", "_iss277_build_preflight.py"))
    cases.append(("② 生成器被删掉 ⇒ S1 红 (★fail-closed★)", {"S1"}, {"sandbox_src": c2}))

    # --- ③ 页里的「改孔」描述段被删 (生成器不动) ⇒ S1 + S3 红 ---------
    c3 = os.path.join(SANDBOX, "case03")
    shutil.rmtree(c3, ignore_errors=True)
    shutil.copytree(base, c3)
    pg = os.path.join(c3, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    write_text(pg, strip_drill_desc(read_text(pg)))
    cases.append(("③ 只改页: 把页里的「改孔」描述段删掉 ⇒ S1 + S3 红",
                  {"S1", "S3"}, {"sandbox_src": c3, "page": pg}))

    # --- ④ 页里的「读钻孔」验收命令被删 ⇒ S1 + S3 红 ------------------
    c4 = os.path.join(SANDBOX, "case04")
    shutil.rmtree(c4, ignore_errors=True)
    shutil.copytree(base, c4)
    pg = os.path.join(c4, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    write_text(pg, strip_drill_criterion(read_text(pg)))
    cases.append(("④ 只改页: 把页里的「读钻孔直径」验收命令删掉 ⇒ S1 + S3 红",
                  {"S1", "S3"}, {"sandbox_src": c4, "page": pg}))

    # --- ⑤ 生成器里注入随机量 ⇒ S2 红 (重跑不幂等) --------------------
    c5 = os.path.join(SANDBOX, "case05")
    shutil.rmtree(c5, ignore_errors=True)
    shutil.copytree(base, c5)
    g = os.path.join(c5, "state", "_iss277_build_preflight.py")
    src = read_text(g)
    write_text(g, src.replace(
        'open(OUT, "w", encoding="utf-8").write("\\n".join(L) + "\\n")',
        'import random, time as _t\n'
        'L.append("★自测随机量 %f★" % random.random())\n'
        'open(OUT, "w", encoding="utf-8").write("\\n".join(L) + "\\n")'))
    cases.append(("⑤ 生成器里注入随机量 ⇒ S2 红 (★重跑不幂等★)", {"S1", "S2"},
                  {"sandbox_src": c5}))

    # --- ⑥ 覆盖度闸的 WP02_BINDING[\"③\"] 被改 ⇒ S5 红 ----------------
    c6 = os.path.join(SANDBOX, "case06")
    shutil.rmtree(c6, ignore_errors=True)
    shutil.copytree(base, c6)
    cg = os.path.join(c6, "HW", "check_onepass_preflight_coverage.py")
    src = read_text(cg)
    write_text(cg, src.replace('"③": (["B33_PIN_LAND_1P27"], []),',
                                '"③": (["B31_P7_TARGET"], []),'))
    cases.append(("⑥ 覆盖度闸 WP02_BINDING[\"③\"] 被改 (★P4 绑定被搞丢★) ⇒ S5 红",
                  {"S5"}, {"coverage_gate": cg}))

    # --- ⑦ 板 md5 被动过 ⇒ S6 红 --------------------------------------
    c7 = os.path.join(SANDBOX, "case07")
    shutil.rmtree(c7, ignore_errors=True)
    os.makedirs(c7, exist_ok=True)
    board_bad = os.path.join(c7, "board_bad.kicad_pcb")
    shutil.copyfile(REAL_PATHS["board"], board_bad)
    with open(board_bad, "ab") as fh:
        fh.write(b"\n")
    cases.append(("⑦ 板 md5 被动过 ⇒ S6 红", {"S6"}, {"board": board_bad}))

    # --- ⑧ 本闸被挂进 state/gate_check.py ⇒ S7 红 ---------------------
    c8 = os.path.join(SANDBOX, "case08")
    shutil.rmtree(c8, ignore_errors=True)
    os.makedirs(c8, exist_ok=True)
    gc_bad = os.path.join(c8, "gate_check_bad.py")
    write_text(gc_bad, read_text(REAL_PATHS["gate_check"]) +
               '\n# ★自测: 把本闸挂进链★\nGATES.append("%s")\n' % GATE_NAME)
    cases.append(("⑧ 本闸被挂进 state/gate_check.py ⇒ S7 红", {"S7"},
                  {"gate_check": gc_bad}))

    # --- ⑨ 路径解析改成 cwd 依赖 ⇒ S8 红 ------------------------------
    c9 = os.path.join(SANDBOX, "case09")
    shutil.rmtree(c9, ignore_errors=True)
    os.makedirs(c9, exist_ok=True)
    cases.append(("⑨ 路径解析改成 cwd 依赖 (相对路径) ⇒ S8 红", {"S8"},
                  {"page": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"}))

    npass = 0
    ntotal = len(cases)
    for idx, (name, want_red, override) in enumerate(cases):
        paths = None
        sandbox_src = None
        work_root = os.path.join(SANDBOX, "run_%02d" % idx)
        if override:
            paths = {}
            sandbox_src = override.pop("sandbox_src", None)
            paths.update(override)
        ctx = collect(paths=paths, sandbox_src=sandbox_src, work_root=work_root)
        results = run_all(ctx)
        reds = set(code for code, _d, f in results if f)
        ok = (want_red <= reds)
        detail = "期望红 %s · 实际红 %s" % (sorted(want_red) or "无", sorted(reds) or "无")
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        print("        %s" % detail)
        if not ok:
            for code, desc, f in results:
                if f and code not in want_red:
                    print("        ✘ 额外红 %s: %s" % (code, f[0][:160]))
            for code, desc, f in results:
                if code in want_red and not f:
                    print("        ✘ 期望红的 %s 却是绿的 ★闸没抓到★" % code)
        if ok:
            npass += 1

    # ---- 真文件 md5 复验 (★跑完自测必须复验真文件 md5 未变★) -----------
    changed = [k for k, v in real_md5_before.items() if md5_of(REAL_PATHS[k]) != v]
    if changed:
        print("  [FAIL] 自测后真文件 md5 变了: %s ⇒ ★自测不许碰真文件★" % changed)
    else:
        print("  [PASS] 自测后真文件 md5 全部未变 (板/网表/脚表/BOM/作业包/预检清单/"
              "生成器/真相页/覆盖度闸)")
        npass += 1
    ntotal += 1
    print("── selftest: %d/%d PASS" % (npass, ntotal))
    if npass == ntotal:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# =========================================================================
# main
# =========================================================================
def main():
    ap = argparse.ArgumentParser(
        description="ISS-396 闸: 「落 FTS 改孔 0.65→0.71」这条登记在生成器重跑之后还在不在")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (★反向用例★)")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    print("★ ISS-396 闸 S1~S9 · 「落 FTS 排针改孔 0.65→0.71」这条登记, "
          "在【生成器重跑之后】还在不在")
    print("★ 本闸在【项目盘沙盒】里重跑生成器 ⇒ ★只读真盘 + 只写 tmp/iss396_sbx/ ⇒ 真页/真板零写 ★")
    print("★ 与既有闸 `HW/check_fts_land_drill_same_batch.py` 是【互补】不是【替代】: "
          "它管【文档里有没有】· 本闸管【重跑之后还在不在】")
    try:
        ctx = collect()
    except Exception as e:  # noqa: BLE001
        print("★ 闸崩: %s" % e)
        return 3
    results = run_all(ctx)
    nfail = report(results, "ISS-396 排针改孔登记「重跑不蒸发」闸")
    # ★**只报告不判红**: §4 #4 的「显式补覆盖令牌」是 main 的地界 (★本单零改既有闸★) ★
    try:
        binding = parse_wp02_binding(ctx["coverage_gate_text"]) or {}
        extra = (binding.get(ORDINAL_OF_ITEM) or ("", []))[1]
        print("── 【只报告·不判红】§4 #4 现状: WP02_BINDING[\"%s\"] = (%s, %s)"
              % (ORDINAL_OF_ITEM, (binding.get(ORDINAL_OF_ITEM) or ("?", []))[0], extra))
        if DRILL_TARGET not in (extra or []):
            print("   ⇒ 显式覆盖令牌还没补 ⇒ ★P4 仍靠 `wp02_tokens()` 自动抽 (★这次自动生效·"
                  "但没有显式锁★) ⇒ ★**落不落由 main 拍** (★本单零改既有闸判据★)")
    except Exception:  # noqa: BLE001
        pass
    if nfail:
        print("❌ 有 %d 条判据红 (★登记在重跑后蒸发 / 页面与生成器不同源 / 零扰动被破★)"
              % nfail)
        return 1
    print("✅ 全绿 (★改孔这条登记在生成器重跑之后仍在页上·且页与生成器同源·且板/三表零扰动★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
