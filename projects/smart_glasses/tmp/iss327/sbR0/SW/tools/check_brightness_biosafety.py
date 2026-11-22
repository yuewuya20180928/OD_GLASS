#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_brightness_biosafety.py
================================================================================
ISS-226 · 光生物安全 · SW 侧亮度控制策略 + 蓝通道占比上限 (25%) + 蓝通道占比可标定量
的**机器门禁**。

★**为什么要有这个门禁 (ISS-226 的核心)** ★
  判据真源在结构侧 (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`), SW 侧**只读引用**。
  ⇒ 风险不在"算错", 而在**SW 侧的人把这条上限悄悄改小/改大、或把后果链删掉、
    或把亮度 API 上的蓝通道占比量摘掉** ⇒ **凡是"判据被静默改弱"的动作, 必须立刻红**。

★**fail-closed 纪律 (★门禁不许靠「把判据删掉」变绿★)** ★
  · 策略文档 / API 文档 / 锚点块 **任一缺失 ⇒ 直接红** (不是"没找到就跳过")
  · 判据数值不是脚本里写死的就算数 —— **还要与结构侧真源交叉核对**:
    ★**SW 侧写小 25% ⇒ 脚本冻结值红 + 与 MECH 真源对不上也红 (双保险)** ★
  · 反向用例在**临时目录**里做 (不碰真盘)。

检查项 (rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条):
  [C1] 判据数值锁定: 上限 25% / 名义 8.26% / Y_B=0.0798 / 红 0.3850 / 绿 0.5017 /
       1500 cd/m2 —— 与**冻结值**逐字节相等 (不许改小, 也不许改大)
  [C2] 越限后果链三段不许被删 (L_eye>1500 cd/m2 ⇒ Exempt(RG0)→RG1 ⇒ 用户信息/标签说明;
       且"不是禁视警示, 那要到 RG2 才有"不许被删)
  [C3] 亮度 API 上的蓝通道占比量不许被摘掉 (字段名 / 上限 / 量程 / 名义值 / 标定方法四要素)
  [C4] ★**跨域交叉核对**: SW 侧的判据数必须能在**结构侧真源**里查到
       (`MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md`, ★只读, 不许改★)
  [C5] ★**不许编造实测值**: API 侧板端标定值必须仍是 null / uncalibrated;
       两个文档里**除 25% / 8.26% 之外不得出现第三个蓝通道百分数**
  [C6] 降级方案不许被删 (L-1 / L-2 / L-3 三级 + 标定方法四要素在位)

用法:
  python3 SW/tools/check_brightness_biosafety.py             # 跑门禁
  python3 SW/tools/check_brightness_biosafety.py --selftest   # 跑自测 (反向用例, 全在临时目录)
  python3 SW/tools/check_brightness_biosafety.py --json       # 机读输出
  python3 SW/tools/check_brightness_biosafety.py --root DIR   # 指定项目根 (自测用)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))     # .../projects/smart_glasses

# ---------------------------------------------------------------- 路径 (相对 root)
POLICY_DOC = os.path.join("SW", "SW_BRIGHTNESS_CONTROL_POLICY.md")
API_DOC = os.path.join("SW", "BRIGHTNESS_API_BLUE_RATIO.md")
MECH_CRITERIA = os.path.join("MECH", "DISPLAY_BIOSAFETY_CRITERIA_V2.md")

POLICY_ANCHOR_BEGIN = "# BEGIN SW_BRIGHTNESS_POLICY_ANCHORS"
POLICY_ANCHOR_END = "# END SW_BRIGHTNESS_POLICY_ANCHORS"
API_ANCHOR_BEGIN = "# BEGIN SW_BRIGHTNESS_API_ANCHORS"
API_ANCHOR_END = "# END SW_BRIGHTNESS_API_ANCHORS"

# ---------------------------------------------------------------- ★冻结判据 (不许改)
# ★★**这些数一个不许动** ★★ (ISS-226 边界: 25% / 8.26% / 1500 cd/m2 /
#    Y_B=0.0798 / 红 0.3850 / 绿 0.5017) ⇒ 脚本里冻结一份, 文档里也冻结一份,
#    **两边必须一致** ⇒ 谁改了文档, 门禁立刻红。
FROZEN = {
    "cap_pct": 25,
    "nominal_pct": 8.26,
    "y_blue": 0.0798,
    "y_red": 0.3850,
    "y_green": 0.5017,
    "eye_limit_cd_m2": 1500,
}
# ★名义值的算式 (脚本每次重算, 证明 8.26% 不是拍脑袋写上去的)
NOMINAL_FORMULA = ("y_blue", "y_red", "y_green")
NOMINAL_TOLERANCE = 0.01          # 8.26% vs 0.0798/(0.0798+0.3850+0.5017) = 8.2565...

# ★越限后果链: 锚点里必须恰好 3 段, 且这 6 个关键措辞必须出现在**正文**里
CHAIN_LEN = 3
CHAIN_KEYS = [
    "L_eye > 1500 cd/m²",
    "Exempt (RG0) 进 RG1",
    "100..10000 W/(m²·sr)",
    "需要用户信息 / 标签说明",
    "不是禁视警示",
    "RG2",
]

# ★亮度 API 上的蓝通道占比量 (字段名不许被摘掉)
API_FIELD = "blue_channel_luminance_ratio_pct"
API_RANGE_MIN = 0
API_RANGE_MAX = 25
API_NOMINAL = 8.26
# ★标定方法四要素 (缺一条 ⇒ 标定方法没法执行 ⇒ 红)
CALIB_KEYS = ["440", "480", "380", "780", "outpupil_spectral_band_integral"]

# ★降级方案三级 + 标定方法关键词
DEGRADE_KEYS = ["L-1", "L-2", "L-3", "uncalibrated"]

# ★不许出现的"第三个百分数" (除 25 / 25.0 / 8.26 外)
ALLOWED_API_PERCENT = {"25", "25.0", "8.26"}
ALLOWED_API_PERCENT_CTX = {"100"}          # ★只允许出现在 APL / duty 工况描述里
ALLOWED_POLICY_PERCENT = {"25", "8.26"}

_PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")


# ---------------------------------------------------------------- 小工具
def _read(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
        return f.read()


def _exists(root: str, rel: str) -> bool:
    return os.path.isfile(os.path.join(root, rel))


def _extract_anchor(text: str, begin: str, end: str, rel: str):
    """抽出 ```yaml 锚点块并解析 ⇒ (data, err)。★解析失败 ⇒ fail-closed 红★"""
    m = re.search(re.escape(begin) + r"(.*?)" + re.escape(end), text, re.S)
    if not m:
        return None, "%s 里找不到锚点块 (%s ... %s)" % (rel, begin, end)
    blob = m.group(1)
    # 去掉围栏与 marker 行, 只留 YAML
    blob = re.sub(r"^\s*```ya?ml\s*$", "", blob, flags=re.M)
    blob = re.sub(r"^\s*```\s*$", "", blob, flags=re.M)
    try:
        import yaml
    except ImportError as exc:                     # noqa: BLE001
        return None, "PyYAML 不可用, 读不了锚点块 (%s)" % exc
    try:
        data = yaml.safe_load(blob)
    except Exception as exc:                      # noqa: BLE001
        return None, "%s 锚点块 YAML 解析失败: %s" % (rel, exc)
    if not isinstance(data, dict):
        return None, "%s 锚点块解析出来不是 dict" % rel
    return data, ""


def _anchor_body(root: str, rel: str, begin: str, end: str):
    """读锚点 + 正文 ⇒ (anchor_dict, body_text, err)"""
    if not _exists(root, rel):
        return None, "", "文件缺失: %s ⇒ 门禁 fail-closed (不许'没找到就跳过')" % rel
    text = _read(root, rel)
    data, err = _extract_anchor(text, begin, end, rel)
    if data is None:
        return None, text, err
    return data, text, ""


def _num_eq(got, want) -> bool:
    try:
        return abs(float(got) - float(want)) < 1e-9
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- [C1] 判据数值锁定
def check_c1(root: str):
    fails = []
    anchor, _body, err = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if anchor is None:
        return ["C1 " + err]
    bb = anchor.get("brightness_biosafety")
    if not isinstance(bb, dict):
        return ["C1 策略锚点里没有 brightness_biosafety 段"]
    # 上限
    if "cap_pct" not in bb:
        fails.append("C1 策略锚点缺 cap_pct (上限 25% 失锚)")
    elif not _num_eq(bb.get("cap_pct"), FROZEN["cap_pct"]):
        fails.append("C1 上限被改了: cap_pct = %r (冻结值 %r) ⇒ 判据不许改小也不许改大"
                     % (bb.get("cap_pct"), FROZEN["cap_pct"]))
    # 名义值
    if "nominal_pct" not in bb:
        fails.append("C1 策略锚点缺 nominal_pct (名义 8.26% 失锚)")
    elif not _num_eq(bb.get("nominal_pct"), FROZEN["nominal_pct"]):
        fails.append("C1 名义值被改了: nominal_pct = %r (冻结值 %r) ⇒ 判据不许改小也不许改大"
                     % (bb.get("nominal_pct"), FROZEN["nominal_pct"]))
    # Y 三值
    for k in ("y_blue", "y_red", "y_green"):
        if k not in bb:
            fails.append("C1 策略锚点缺 %s" % k)
        elif not _num_eq(bb.get(k), FROZEN[k]):
            fails.append("C1 %s 被改了: %r (冻结值 %r)" % (k, bb.get(k), FROZEN[k]))
    # 出瞳阈值
    if "eye_limit_cd_m2" not in bb:
        fails.append("C1 策略锚点缺 eye_limit_cd_m2 (1500 cd/m2 失锚)")
    elif not _num_eq(bb.get("eye_limit_cd_m2"), FROZEN["eye_limit_cd_m2"]):
        fails.append("C1 出瞳阈值被改了: eye_limit_cd_m2 = %r (冻结值 %r)"
                     % (bb.get("eye_limit_cd_m2"), FROZEN["eye_limit_cd_m2"]))
    # ★算式自洽: 名义值必须真能从三个 Y 值算出来 (证明 8.26% 有出处)
    try:
        yb, yr, yg = (float(bb[k]) for k in NOMINAL_FORMULA)
        computed = yb / (yb + yr + yg) * 100.0
        if abs(computed - float(FROZEN["nominal_pct"])) > NOMINAL_TOLERANCE:
            fails.append("C1 名义值与算式不自洽: 0.0798/(0.0798+0.3850+0.5017) = %.4f%% ≠ %r%%"
                         % (computed, FROZEN["nominal_pct"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        fails.append("C1 名义值算式重算失败 (三个 Y 值缺失或非数)")
    return fails


# ---------------------------------------------------------------- [C2] 后果链三段
def check_c2(root: str):
    fails = []
    anchor, body, err = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if anchor is None:
        return ["C2 " + err]
    bb = anchor.get("brightness_biosafety") or {}
    chain = bb.get("chain")
    if not isinstance(chain, list):
        return ["C2 策略锚点里没有 chain 段 (后果链失锚)"]
    if len(chain) != CHAIN_LEN:
        fails.append("C2 后果链段数 = %d (必须 %d: ① L_eye>1500 cd/m2 ② Exempt(RG0)→RG1 "
                     "③ 用户信息/标签说明)" % (len(chain), CHAIN_LEN))
    for i, seg in enumerate(chain, 1):
        if not isinstance(seg, str) or not seg.strip():
            fails.append("C2 后果链第 %d 段是空的" % i)
    for k in CHAIN_KEYS:
        if k not in body:
            fails.append("C2 后果链关键措辞「%s」没了 (⇒ 判据被删弱)" % k)
    return fails


# ---------------------------------------------------------------- [C3] API 蓝通道占比量
def check_c3(root: str):
    fails = []
    anchor, body, err = _anchor_body(root, API_DOC, API_ANCHOR_BEGIN, API_ANCHOR_END)
    if anchor is None:
        return ["C3 " + err]
    api = anchor.get("brightness_api")
    if not isinstance(api, dict):
        return ["C3 API 锚点里没有 brightness_api 段"]
    if api.get("field") != API_FIELD:
        fails.append("C3 亮度 API 的蓝通道占比量被摘掉/改名了: field = %r (必须 %r)"
                     % (api.get("field"), API_FIELD))
    if not _num_eq(api.get("range_max_pct"), API_RANGE_MAX):
        fails.append("C3 API 量程上限被改了: range_max_pct = %r (必须 %r)"
                     % (api.get("range_max_pct"), API_RANGE_MAX))
    if not _num_eq(api.get("range_min_pct"), API_RANGE_MIN):
        fails.append("C3 API 量程下限被改了: range_min_pct = %r (必须 %r)"
                     % (api.get("range_min_pct"), API_RANGE_MIN))
    if not _num_eq(api.get("nominal_pct"), API_NOMINAL):
        fails.append("C3 API 名义值被改了: nominal_pct = %r (必须 %r)"
                     % (api.get("nominal_pct"), API_NOMINAL))
    if api.get("unit") != "percent":
        fails.append("C3 API 单位被改了: unit = %r (必须 'percent')" % api.get("unit"))
    # ★板端状态字段不许被摘掉 (它是"未标定"这个事实的载体; 值本身由 C5 判"不许编造实测值")
    if "board_status" not in api:
        fails.append("C3 API 锚点里没有 board_status (板端标定状态失锚)")
    if "board_value" not in api:
        fails.append("C3 API 锚点里没有 board_value (板端标定值字段失锚)")
    calib = api.get("calibration")
    if not isinstance(calib, dict):
        fails.append("C3 API 锚点里没有 calibration 段 (标定方法失锚)")
    else:
        for k in CALIB_KEYS:
            if k not in yaml_dump(calib):
                fails.append("C3 标定方法要素「%s」没了" % k)
    # 字段名必须在**正文**里也出现 (不许只在锚点里有)
    if API_FIELD not in body:
        fails.append("C3 亮度 API 文档正文里没有 %s 这个量 (⇒ API 量被摘掉)" % API_FIELD)
    # 策略侧锚点必须指向同一个字段与同一个上限
    p_anchor, _pb, perr = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if p_anchor is None:
        fails.append("C3 " + perr)
    else:
        pbb = p_anchor.get("brightness_biosafety") or {}
        p_api = pbb.get("api")
        if not isinstance(p_api, dict):
            fails.append("C3 策略锚点里没有 api 段 (API 挂靠点失锚)")
        else:
            if p_api.get("field") != API_FIELD:
                fails.append("C3 策略侧挂靠的 API 字段 = %r ≠ %r (两处各说各话)"
                             % (p_api.get("field"), API_FIELD))
            if not _num_eq(p_api.get("cap_pct"), FROZEN["cap_pct"]):
                fails.append("C3 策略侧挂靠的 API 上限 = %r ≠ %r" % (p_api.get("cap_pct"),
                                                                    FROZEN["cap_pct"]))
    return fails


def yaml_dump(obj) -> str:
    try:
        import yaml
        return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)
    except Exception:                               # noqa: BLE001
        return str(obj)


# ---------------------------------------------------------------- [C4] 跨域交叉核对
def check_c4(root: str):
    """★SW 侧的判据数必须能在结构侧真源里查到 (只读) ⇒ 改小/改大都对不上★"""
    fails = []
    if not _exists(root, MECH_CRITERIA):
        return ["C4 结构侧判据真源缺失: %s ⇒ 门禁 fail-closed (SW 侧不许自己另立一套)"
                % MECH_CRITERIA]
    mech = _read(root, MECH_CRITERIA)
    anchor, _b, err = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if anchor is None:
        return ["C4 " + err]
    bb = anchor.get("brightness_biosafety") or {}
    # ★结构侧真源里必须仍在的话 (25% / 8.26% / 1500 cd/m²)
    for token, why in (("25%", "上限 25%"),
                       ("8.26%", "名义值 8.26%"),
                       ("1500 cd/m²", "出瞳阈值 1500 cd/m²")):
        if token not in mech:
            fails.append("C4 结构侧真源 %s 里查不到「%s」(%s) ⇒ 结构侧判据口径变了, "
                         "SW 侧要按 H-1 流程重锚 (只读引用, SW 侧不许改判据)"
                         % (MECH_CRITERIA, token, why))
    # ★SW 侧写的数必须与结构侧真源**一致** (改小上限 ⇒ 这里对不上)
    cap = bb.get("cap_pct")
    if cap is not None:
        s = ("%g" % float(cap))
        if ("≤ %s%%" % s) not in mech and ("%s%%" % s) not in mech:
            fails.append("C4 SW 侧的上限 %s%% 在结构侧真源里查不到 ⇒ 两侧口径已分叉 "
                         "(改判据只能走 H-1 流程)" % s)
    nom = bb.get("nominal_pct")
    if nom is not None:
        s = ("%g" % float(nom))
        if ("%s%%" % s) not in mech:
            fails.append("C4 SW 侧的名义值 %s%% 在结构侧真源里查不到 ⇒ 两侧口径已分叉" % s)
    eye = bb.get("eye_limit_cd_m2")
    if eye is not None:
        s = ("%g" % float(eye))
        if ("%s cd/m²" % s) not in mech:
            fails.append("C4 SW 侧的出瞳阈值 %s cd/m² 在结构侧真源里查不到 ⇒ 两侧口径已分叉" % s)
    return fails


# ---------------------------------------------------------------- [C5] 不许编造实测值
def check_c5(root: str):
    fails = []
    api_anchor, api_body, err = _anchor_body(root, API_DOC, API_ANCHOR_BEGIN, API_ANCHOR_END)
    if api_anchor is None:
        return ["C5 " + err]
    api = api_anchor.get("brightness_api") or {}
    if api.get("board_value") is not None:
        fails.append("C5 API 侧板端标定值不是 null (=%r) ⇒ 本单板不在本机, "
                     "任何具体数都只能是编的" % api.get("board_value"))
    if api.get("board_status") != "uncalibrated":
        fails.append("C5 API 侧板端状态 = %r (必须 'uncalibrated' ⇒ 本单板端 [0数据])"
                     % api.get("board_status"))
    # ★API 文档正文里不得出现第三个百分数 (25 / 25.0 / 8.26 之外)
    for m in _PERCENT_RE.finditer(api_body):
        val = m.group(1)
        line = api_body[api_body.rfind("\n", 0, m.start()) + 1: api_body.find("\n", m.end())]
        if val in ALLOWED_API_PERCENT:
            continue
        if val in ALLOWED_API_PERCENT_CTX and ("APL" in line or "duty" in line):
            continue
        fails.append("C5 API 文档里出现了第三个百分数「%s%%」(行: %s) ⇒ "
                     "本单只允许 25%% (上限) / 8.26%% (名义值), 其余都可能是编出来的实测值"
                     % (val, line.strip()[:60]))
    # ★策略文档正文里同样只允许 25% / 8.26%
    _pa, pol_body, perr = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if _pa is None:
        fails.append("C5 " + perr)
    else:
        for m in _PERCENT_RE.finditer(pol_body):
            val = m.group(1)
            if val not in ALLOWED_POLICY_PERCENT:
                line = pol_body[pol_body.rfind("\n", 0, m.start()) + 1: pol_body.find("\n", m.end())]
                fails.append("C5 策略文档里出现了第三个百分数「%s%%」(行: %s) ⇒ "
                             "只允许 25%% / 8.26%%" % (val, line.strip()[:60]))
    return fails


# ---------------------------------------------------------------- [C6] 降级方案在位
def check_c6(root: str):
    fails = []
    _pa, body, err = _anchor_body(root, POLICY_DOC, POLICY_ANCHOR_BEGIN, POLICY_ANCHOR_END)
    if _pa is None:
        return ["C6 " + err]
    for k in DEGRADE_KEYS:
        if k not in body:
            fails.append("C6 降级方案要素「%s」没了 (⇒ 板端不可达时没有兜底口径)" % k)
    if "[0数据]" not in body:
        fails.append("C6 降级方案里没有 [0数据] 标记 (⇒ 板端缺数据这件事没被写下来)")
    api_anchor, api_body, aerr = _anchor_body(root, API_DOC, API_ANCHOR_BEGIN, API_ANCHOR_END)
    if api_anchor is None:
        fails.append("C6 " + aerr)
    else:
        for k in ("outpupil_spectral_band_integral", "440", "480"):
            if k not in api_body:
                fails.append("C6 API 标定方法要素「%s」没了" % k)
    return fails


CHECKS = [
    ("C1", "判据数值锁定 (25% / 8.26% / Y 三值 / 1500 cd/m2)", check_c1),
    ("C2", "越限后果链三段不许被删", check_c2),
    ("C3", "亮度 API 的蓝通道占比量不许被摘掉", check_c3),
    ("C4", "跨域交叉核对 (结构侧真源只读)", check_c4),
    ("C5", "不许编造实测值 (板端 [0数据])", check_c5),
    ("C6", "降级方案不许被删", check_c6),
]


def run_checks(root: str):
    results = []
    for cid, name, fn in CHECKS:
        try:
            fails = fn(root)
        except Exception as exc:                   # noqa: BLE001 —— 门禁不能因异常假绿
            fails = ["检查异常: %r" % (exc,)]
        results.append((cid, name, fails))
    return results


# ---------------------------------------------------------------- 自测
TREE_FILES = (POLICY_DOC, API_DOC, MECH_CRITERIA)


def _build_tree(tmp: str, root: str, name: str) -> str:
    work = os.path.join(tmp, name)
    for rel in TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work


def _mutate(path: str, fn):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    out = fn(text)
    if out == text:
        raise AssertionError("改坏动作没生效 (用例本身坏了): %s" % path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)


def _drop_lines(path: str, needle: str):
    _mutate(path, lambda t: "\n".join(ln for ln in t.split("\n") if needle not in ln))


def selftest(root: str) -> int:
    print("=== SELFTEST (ISS-226 反向用例: 每条都必须在被破坏后变红) ===")
    passed, failed = 0, 0
    with tempfile.TemporaryDirectory(prefix="iss226_gate_") as tmp:
        # 基线
        work = _build_tree(tmp, root, "base")
        base = run_checks(work)
        bad = [(cid, f) for cid, _n, fs in base for f in fs]
        if bad:
            print("  ❌ 基线就不绿: %s ⇒ 反向用例不成立" % (bad[:3],))
            failed += 1
        else:
            print("  ✅ 基线全绿 (C1~C6 在临时树上全过)")
            passed += 1

        cases = [
            ("REV-1 把上限 25% 改小成 10%", "C1",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("cap_pct: 25", "cap_pct: 10"))),
            ("REV-2 把越限后果链整段删掉", "C2",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("需要用户信息 / 标签说明", "见后文"))),
            ("REV-3 把后果链里的『不是禁视警示…RG2』删掉", "C2",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("不是禁视警示", "见备注"))),
            ("REV-4 把亮度 API 的蓝通道占比量摘掉 (字段改名)", "C3",
             lambda w: _mutate(os.path.join(w, API_DOC),
                               lambda t: t.replace(API_FIELD, "some_other_field"))),
            ("REV-5 把亮度 API 文档整个删掉 (fail-closed)", "C3",
             lambda w: os.remove(os.path.join(w, API_DOC))),
            ("REV-6 把名义值 8.26% 改成 6.00%", "C1",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("nominal_pct: 8.26", "nominal_pct: 6.00"))),
            ("REV-7 把名义值的算式输入 Y_B 改小", "C1",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("y_blue: 0.0798", "y_blue: 0.0400"))),
            ("REV-8 在 API 里手填一个编出来的板端实测值", "C5",
             lambda w: _mutate(os.path.join(w, API_DOC),
                               lambda t: t.replace("board_value: null", "board_value: 11.8"))),
            ("REV-9 在 API 文档里加一个第三个数 (疑似实测占比)", "C5",
             lambda w: _mutate(os.path.join(w, API_DOC),
                               lambda t: t.replace("## 6 与其它单的关系",
                                                   "实测蓝通道占比 12.4%\n\n## 6 与其它单的关系"))),
            ("REV-10 把策略锚点块整个删掉 (fail-closed)", "C1",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: re.sub(re.escape(POLICY_ANCHOR_BEGIN) + r".*?"
                                                + re.escape(POLICY_ANCHOR_END), "", t,
                                                flags=re.S))),
            ("REV-11 把降级方案 L-1/L-2/L-3 删掉", "C6",
             lambda w: _mutate(os.path.join(w, POLICY_DOC),
                               lambda t: t.replace("L-1", "X-1").replace("L-2", "X-2")
                                        .replace("L-3", "X-3"))),
            ("REV-12 把结构侧真源里的 25% 删掉 (跨域分叉 ⇒ 红)", "C4",
             lambda w: _drop_lines(os.path.join(w, MECH_CRITERIA), "25%")),
        ]

        for idx, (name, expect, action) in enumerate(cases):
            work = _build_tree(tmp, root, "case_%02d" % idx)
            try:
                action(work)
            except AssertionError as exc:
                print("  ❌ %-56s ⇒ %s" % (name, exc))
                failed += 1
                continue
            fails = [f for _cid, _n, fs in run_checks(work) for f in fs]
            hit = [f for f in fails if f.startswith(expect)]
            if hit:
                print("  ✅ %-56s ⇒ %s 变红 (%s)" % (name, expect, hit[0][:74]))
                passed += 1
            else:
                print("  ❌ %-56s ⇒ %s 没变红 (期望它红) — 实得: %s"
                      % (name, expect, fails[:2]))
                failed += 1

    print("--- SELFTEST %d/%d 通过 ---" % (passed, passed + failed))
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-226 光生物安全 SW 侧亮度控制门禁")
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--root", default=ROOT, help="项目根目录 (默认: 脚本所在项目根)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)

    results = run_checks(root)
    nbad = sum(1 for _c, _n, fs in results for _f in fs)
    if args.json:
        print(json.dumps({"root": root, "ok": nbad == 0,
                          "checks": [{"id": c, "name": n, "fails": fs} for c, n, fs in results]},
                         ensure_ascii=False, indent=2))
        return 0 if nbad == 0 else 1

    if nbad == 0:
        print("✅ ISS-226 光生物安全 SW 侧门禁: 全过")
        for cid, name, _fs in results:
            print("   %s %s ✅" % (cid, name))
        print("   ★ 判据数值: 上限 25%% / 名义 8.26%% / Y_B=0.0798 / 红 0.3850 / 绿 0.5017 / 1500 cd/m²")
        print("   ★ 名义值算式自洽: 0.0798/(0.0798+0.3850+0.5017) = %.4f%% (≈8.26%%)"
              % (FROZEN["y_blue"] / (FROZEN["y_blue"] + FROZEN["y_red"] + FROZEN["y_green"]) * 100.0))
        print("   ★ 板端标定值 = null / uncalibrated ([0数据], 本单板不在本机)")
        return 0

    print("❌ ISS-226 光生物安全 SW 侧门禁: %d 项不通过" % nbad)
    for cid, name, fs in results:
        for f in fs:
            print("   - [%s] %s" % (cid, f))
    print("   ★⇒ 判据不许被静默改弱: 上限 25% / 名义 8.26% / 后果链三段 / API 蓝通道占比量 "
          "任一被动 ⇒ 门禁红 ⇒ 改判据只能走 SW_BRIGHTNESS_CONTROL_POLICY.md §6 H-1 流程")
    return 1


if __name__ == "__main__":
    sys.exit(main())
