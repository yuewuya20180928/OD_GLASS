#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_frame_freeze_gate.py —— ISS-336 「板只改一次」那一趟的【板框冻结闸 U-1 机器闸】 (mech-lead)
==================================================================================================
干什么:
  「板框冻结了没有」这件事, 以前只有一句人话 (ISS-313 立的 need `proto_pcb_freeze_gate`),
  机器判不出来 ⇒ 谁都能在作业包里宣称已冻结 ⇒ 板那一趟可以在 U-1 未拍时开工 ⇒ 板 md5 第二次变
  ⇒ Gerber / 投产包 / 留证链全部作废重做 (ISS-319 §D-2-1 逐字: 2-4 周 + ¥4-8K)。

  本闸把 ISS-316 §2-4 已出好的 **C1~C7 七条判据**实现成一条可跑的闸:
    C1 帧 id ∈ `cal:FRAMES` 三套之内 且非空
    C2 帧 id == `cal:FRAMES.current_frame`            ★只在【有 U-1 认领句】时才判★
    C3 板厚 ∈ 允许板厚集 (从 36 档的盖板内腔判据现推, 不写死)
    C4 层数 ∈ 层数档集 (从 `board_frame_feasibility.LAYER_TIERS` 现读)
    C5 孔位口径 = PIN-SET-2 套 A 且该帧上四孔全部成立 (`holes.all_fit == true`)
    C6 该 (帧, 板厚, 层数) 组合在 36 档里 `can_open == true` 且 `red_reasons == []`
    C7 need `proto_pcb_freeze_gate` 已闭合, 且闭合答案正文**逐字**含【帧 id + 板厚 + 层数】三个数

★口径纪律 (硬) ★
  ① **阈值一个字节都不许自己写** ⇒ 本脚本把 `MECH/board_frame_feasibility.py` 当**只读模块 import**
     (它自己又把 `MECH/service_port_check.py` 当只读模块 import ⇒ BASE/TOL/CRIT 零漂移),
     并**独立**再只读一次 `service_port_check.py` 做零漂移对拍 (BASE 逐项相等才算过);
     帧 id / current_frame 只读 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES`
     ⇒ **代码里没有第二份阈值表** (允许板厚集是从 36 档的 `cavity_ok` 现推的, 不是抄的)。
  ② **不改任何既有文件** (★`service_port_check.py` / `board_frame_feasibility.py` /
     `check_board_frame_coords.py` / `check_onepass_mech_release.py` / `HW/PCB/BOARD_FRAME_CALIBER.md` /
     `state/fragments/*.yaml` 一个字节没动★) —— 本文件是**新增的独立脚本**, 只读 + 只打印。
  ③ **零写盘**: 本脚本只读既有文件 + 只打印到 stdout (★不写盘 / 不写板 / 不落表★)。
  ④ **不代老板拍 U-1**: 板框三选一 (B160x100 / F30A / P60x15) 只「列档 + 判红原因 + 谁拍」;
     本脚本**不会**替 main 造一条闭合记录, **也不会**把某个答案写进任何文件。
  ⑤ 证据级: 全部几何读数 = 设计态几何 + 公差栈 ⇒ `[推算]`; 盘上板读数 = `[实测]`。

★C7 的真源 (★2026-11-19 本机实读纠正·★ISS-316 §2-4 原写「读 `state/issue_log.yaml` 的闭合记录」⇒ 盘上不存在★)★:
  `state/issue_log.yaml` 的顶层只有 `_schema` / `_owners_legal` / `issues` 三项 ⇒ **零条 need 闭合记录**
  ⇒ 真源是【分片侧】: `state/fragments/mech.yaml` 的 `needs_closed` 台账 (64 条) + `answers` (79 条),
  以及 merge 口径的配对闭合 (`state/fragments/pm.yaml` 的 `answers` 里同 key 的一条 ⇒ main 已答)。
  ⇒ 本闸读哪份文件 / 读哪个字段 / 怎么匹配 ⇒ 见 `read_claim()` 的 docstring (逐字口径写在那里,
    `--print-c7-source` 可单独打出来)。**这条订正已在 ISS-336 交卷页 §B5 显式登记。**

★判定对象 (★「认领句」的两层来源·★本闸唯一的裁量点·★已写进交卷页 §B5★)★:
  L1 **U-1 认领句** (need 已闭合 ⇒ 答案正文在): 从正文里解析【帧 id / 板厚 / 层数 / 孔位口径】。
     ⇒ **从严**: 认领句里缺哪个数, 哪条判据就判红 (★RC-1「只拍帧 id 没拍板厚」必须被 C3 抓住★)。
  L2 **现行几何口径** (need 尚未闭合 ⇒ 还没拍): 从 `service_port_check.BASE['pcb_l'/'pcb_w'/'pcb_thk']` +
     `cal:FRAMES` + `board_frame_feasibility.PIN_SET_A` 现读 ⇒ 帧 id / 板厚 / 层数 / 套 A 四孔
     (★对应 `MECH/BOARD_GEOM_30MM.md` §1/§3 的 60×30 / 1.00mm / 6 层 / 套 A 四孔★)。
     ⇒ 无认领句时 C2 判**不判红** (★ISS-316 §2-4 C2 的判红条件本身是以「认领句写 X 但 current_frame
       仍是 Y」措辞写的 ⇒ 没有认领句就没有判红条件★); 其余五条判**现行口径的绝对量** (与拍没拍无关)。
  ⇒ **今天盘上的读数**: C1~C6 全绿 (现行口径自洽: 60×30 / 1.00mm / 6 层 / 套 A ⇒ F30A 能开),
    C7 红 (need 未闭合) ⇒ **今天红 = U-1 还没拍, 正确** (★如实报告病灶, 不是闸坏了★)。

用法:
  python3 MECH/check_board_frame_freeze_gate.py                ⇒ 打印 C1~C7 逐条 + 阈值来源表, rc=0/2
  python3 MECH/check_board_frame_freeze_gate.py --json          ⇒ 机器可读
  python3 MECH/check_board_frame_freeze_gate.py --print-c7-source ⇒ 逐字打印 C7 读哪份文件/哪个字段/怎么匹配
  python3 MECH/check_board_frame_freeze_gate.py --root DIR      ⇒ ★只读别的根 (沙盒副本用; 不碰真件★)

退出码: 0 = C1~C7 全绿; 2 = 至少一条判红 (逐条打印判红原因, 措辞与 `red_reasons` 同款)。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ★need key (★ISS-313 立的闸; ★ISS-316 §2-4 的 C7 用的就是它★)
NEED_KEY = "proto_pcb_freeze_gate"

# ★分片文件名 (★state/frag_write.py FILE_OF 的口径: main→pm.yaml / hw-lead→hw.yaml / sw-lead→sw.yaml / mech-lead→mech.yaml★)
MECH_FRAG = "mech.yaml"      # ★need `proto_pcb_freeze_gate` 的登记所在分片 (owner=mech-lead)
MAIN_FRAG = "pm.yaml"        # ★main 的分片 (★merge 口径的配对闭合落在这里★)

# ★★注意: 本文件里**没有任何写死的阈值表** ★★
#   · 允许板厚集 (C3) = 36 档的 `cavity_ok` 现推 ⇒ 阈值来自 service_port_check.BASE['cavity_req']
#   · 层数档集 (C4)   = board_frame_feasibility.LAYER_TIERS (只读 import)
#   · 板厚档全集 (C7 存在性判据用) = board_frame_feasibility.THICKNESS_TIERS (只读 import)
#   · 帧 id 三套 (C1/C2/C7) = HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES (只读)
#   ⇒ 代码里若出现第二个 {0.80, 1.00} / {4, 6, 8} 常量表 = 违规 ⇒ 本文件没有


# ==================================================================================================
# ★只读 import 既有闸脚本 ⇒ 阈值零漂移 (★不写回、不改它★)
# ==================================================================================================
def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ★只执行模块顶层 (无副作用: 只定义常量与函数)★
    return mod


def load_spc(root: str):
    """只读 import `MECH/service_port_check.py` (★同 `board_frame_feasibility.load_spc()` 的做法★)"""
    return _load_module(os.path.join(root, "MECH", "service_port_check.py"), "spc_readonly_iss336")


def load_bff(root: str):
    """只读 import `MECH/board_frame_feasibility.py` (★它自己 import service_port_check ⇒ BASE/TOL/CRIT 同源★)"""
    return _load_module(os.path.join(root, "MECH", "board_frame_feasibility.py"), "bff_readonly_iss336")


def zero_drift_check(bff, spc) -> tuple:
    """零漂移对拍: board_frame_feasibility 转手的 BASE / TOL / CRIT 必须与 service_port_check 原件逐项相等。"""
    diffs = []
    for k, v in spc.BASE.items():
        if k not in bff.BASE or abs(float(bff.BASE[k]) - float(v)) > 1e-12:
            diffs.append("BASE[%s]" % k)
    for k, v in spc.TOL.items():
        if k not in bff.TOL or abs(float(bff.TOL[k]) - float(v)) > 1e-12:
            diffs.append("TOL[%s]" % k)
    if abs(float(bff.CRIT) - float(spc.CRIT)) > 1e-12:
        diffs.append("CRIT")
    return (not diffs), diffs


# ==================================================================================================
# `cal:FRAMES` 读取 (★帧 id + current_frame 的唯一权威表: HW/PCB/BOARD_FRAME_CALIBER.md §2★)
# ==================================================================================================
def read_cal_frames(root: str) -> dict:
    """读 `HW/PCB/BOARD_FRAME_CALIBER.md` 的 ```json cal:FRAMES``` 块 ⇒ {current_frame, frames{...}}"""
    path = os.path.join(root, "HW", "PCB", "BOARD_FRAME_CALIBER.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"```json cal:FRAMES\s*\n(.*?)\n```", text, re.S)
    if not m:
        raise SystemExit("★致命: 在 %s 里找不到 `cal:FRAMES` JSON 块 ⇒ 拒绝跑 (防口径漂移)" % path)
    return json.loads(m.group(1))


# ==================================================================================================
# ★C7 的真源读取 (★读哪份文件 / 读哪个字段 / 怎么匹配 —— 逐字口径★)
# ==================================================================================================
def read_claim(root: str) -> dict:
    """读「U-1 认领句」(need `proto_pcb_freeze_gate` 的闭合答案正文)。

    ★★ 逐字口径 (★2026-11-19 本机实读确认·★ISS-336 §B5 登记的订正★★):
      【读哪份文件】
        ① `state/fragments/mech.yaml`   —— need `proto_pcb_freeze_gate` 的登记所在分片 (owner=mech-lead)
        ② `state/fragments/pm.yaml`     —— main 的分片 (★merge 口径的配对闭合落在这里★)
        (★`state/issue_log.yaml` 的顶层只有 `_schema` / `_owners_legal` / `issues` 三项 ⇒
          **零条 need 闭合记录** ⇒ 读它 = 引用盘上不存在的字段 ⇒ 本闸不读它★)
      【读哪个字段】
        ① 闭合台账: `needs_closed[]` 里 `key == "proto_pcb_freeze_gate"` 的那条 (字段:
             key / iss / closed_at / closed_by / cls / action / reason / evidence / evidence_level /
             answer_key / answer_ref)
        ② 答案正文: `answers[]` 里 `key == "proto_pcb_freeze_gate"` 的那条的 `value` 字段
             (★回落顺序: 同文件 answers[NEED_KEY].value → needs_closed.answer_key 对应的 answers.value →
               pm.yaml 的同 key answers.value → needs_closed.evidence + .reason★)
      【怎么匹配】
        · **闭合** = ① 或 ② 任一命中 (★merge.py 自己的口径: needs_from × answers 按 key 配对,
          作者 = need 的 `to` ⇒ main 答 ⇒ 闭合★)
        · **内容** = 答案正文里**逐字**含【帧 id + 板厚 + 层数】三个数
          (帧 id = `cal:FRAMES` 三套 id 之一的**字面串**; 板厚 = 板厚档数值 (0.80/1.00/1.22/1.60)
           的**字面串**; 层数 = `层数` 后的数字或 `N 层` 的**字面串**)
        ⇒ 答案只有一句「板框已定」 ⇒ 三个数一个都没有 ⇒ **C7 判红** (★空转闭合★)
    """
    frag_dir = os.path.join(root, "state", "fragments")
    data = {}
    for fn in (MECH_FRAG, MAIN_FRAG):
        p = os.path.join(frag_dir, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                data[fn] = yaml.safe_load(f) or {}

    mech = data.get(MECH_FRAG) or {}
    main_ = data.get(MAIN_FRAG) or {}

    def _answer(frag, key):
        for a in (frag.get("answers") or []):
            if a.get("key") == key:
                return a
        return None

    closed_rec = next((r for r in (mech.get("needs_closed") or []) if r.get("key") == NEED_KEY), None)
    main_ans = _answer(main_, NEED_KEY)

    # ---- 答案正文解析 (顺序即优先级) ----
    text, src = "", ""
    cand = _answer(mech, NEED_KEY)
    if cand is not None and (cand.get("value") or "").strip():
        text, src = cand.get("value") or "", "state/fragments/%s answers[key=%s].value" % (MECH_FRAG, NEED_KEY)
    if not text and closed_rec is not None:
        ak = closed_rec.get("answer_key")
        if ak:
            a2 = _answer(mech, ak)
            if a2 is not None and (a2.get("value") or "").strip():
                text = a2.get("value") or ""
                src = "state/fragments/%s answers[key=%s].value (needs_closed.answer_key)" % (MECH_FRAG, ak)
    if not text and main_ans is not None and (main_ans.get("value") or "").strip():
        text = main_ans.get("value") or ""
        src = "state/fragments/%s answers[key=%s].value" % (MAIN_FRAG, NEED_KEY)
    if not text and closed_rec is not None:
        text = " ".join(x for x in (closed_rec.get("evidence"), closed_rec.get("reason")) if x)
        src = "state/fragments/%s needs_closed[key=%s].evidence + .reason" % (MECH_FRAG, NEED_KEY)

    closed_in_ledger = closed_rec is not None
    closed_by_merge = main_ans is not None
    still_open = any(n.get("key") == NEED_KEY for n in (mech.get("needs_from") or []))
    open_ledger = next((n for n in (mech.get("needs_open_ledger") or []) if n.get("key") == NEED_KEY), None)

    return {
        "text": text,
        "src": src or "(无答案正文)",
        "closed_in_ledger": closed_in_ledger,
        "closed_by_merge": closed_by_merge,
        "still_in_needs_from": still_open,
        "closed_rec": closed_rec,
        "open_ledger": open_ledger,
    }


# ==================================================================================================
# 认领句解析 (★从答案正文里解析【帧 id / 板厚 / 层数 / 孔位口径】★)
# ==================================================================================================
def _find_frame_id(text: str, frames: dict) -> tuple:
    """解析帧 id —— 顺序化, 避免「正文里同时出现两个帧 id」时取错。

    ① 显式标签: `帧 id = X` / `帧 = X`
    ② 认领句:   `认领句写在 X` / `认领为 X`
    ③ 板框句:   `板框用 X` / `板框 = X` (X 可以是帧 id, 也可以是尺寸串 `60×30`)
    ④ 尺寸串:   正文里唯一的 `N×N` ⇒ 用 `cal:FRAMES` 的 width_mm × height_mm 反查帧 id
    ⑤ 帧 id:    正文里**唯一**出现的 `cal:FRAMES` 帧 id 字面串
    ⇒ 找不到 ⇒ None (调用方按「缺帧 id」判红)
    """
    ids = list(frames.keys())

    pats_id = [
        r"帧\s*id\s*(?:=|:|：)?\s*([A-Za-z0-9_]+)",
        r"认领(?:句)?\s*(?:写在|写为|写|为|是|:|：|=)\s*([A-Za-z0-9_]+)",
        r"板框\s*(?:用|为|是|:|：|=)\s*([A-Za-z0-9_]+)",
    ]
    for p in pats_id:
        m = re.search(p, text)
        if m and m.group(1) in ids:
            return m.group(1), "显式标签 `%s`" % m.group(0).strip()

    dims = list(re.finditer(r"(?<![0-9])(\d{2,3})\s*[×xX*]\s*(\d{2,3})(?![0-9])", text))
    if len(dims) == 1:
        w, h = float(dims[0].group(1)), float(dims[0].group(2))
        for fid, spec in frames.items():
            if abs(float(spec.get("width_mm", -1)) - w) < 1e-6 and abs(float(spec.get("height_mm", -1)) - h) < 1e-6:
                return fid, "尺寸串 `%s` ⇒ cal:FRAMES 尺寸反查" % dims[0].group(0)
        return None, "尺寸串 `%s` 在 cal:FRAMES 里反查不到" % dims[0].group(0)

    found = [fid for fid in ids if fid in text]
    if len(found) == 1:
        return found[0], "正文里唯一的帧 id 字面串 `%s`" % found[0]
    if len(found) > 1:
        return None, "正文里出现多个帧 id (%s) ⇒ 无法判定认领的是哪一个" % ", ".join(found)
    return None, "(正文里没有帧 id)"


def _find_thickness(text: str) -> tuple:
    """解析板厚 —— ① `板厚/厚度` 后的数字; ② `N.NN mm` 形式。"""
    m = re.search(r"(?:板厚|厚度)\s*(?:=|:|：)?\s*(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1)), "`%s` 后的数字" % m.group(0).split()[0]
    m = re.search(r"(?<![0-9.])(\d+\.\d{1,2})\s*(?:mm|毫米)", text)
    if m:
        return float(m.group(1)), "`%s mm`" % m.group(1)
    return None, "(正文里没有板厚)"


def _find_layers(text: str) -> tuple:
    """解析层数 —— ① `层数` 后的数字; ② `N 层`。"""
    m = re.search(r"层数\s*(?:=|:|：)?\s*(\d+)", text)
    if m:
        return int(m.group(1)), "`%s` 后的数字" % m.group(0).strip()
    m = re.search(r"(?<![0-9])(\d+)\s*层", text)
    if m:
        return int(m.group(1)), "`%s 层`" % m.group(1)
    return None, "(正文里没有层数)"


def parse_claim(text: str, frames: dict) -> dict:
    """从答案正文里解析【帧 id / 板厚 / 层数 / 孔位口径】(★L1 认领句模式★)"""
    out = {"frame_id": None, "frame_src": "", "thk": None, "thk_src": "",
           "layers": None, "layers_src": "", "hole_set": None, "hole_src": ""}

    out["frame_id"], out["frame_src"] = _find_frame_id(text, frames)
    out["thk"], out["thk_src"] = _find_thickness(text)
    out["layers"], out["layers_src"] = _find_layers(text)

    if re.search(r"套\s*B|PIN-SET-2\s*套\s*B", text):
        out["hole_set"], out["hole_src"] = "套B", "文本点名「套 B」(套 B 已于 ISS-192 被否决)"
    elif re.search(r"套\s*A|PIN-SET-2", text):
        out["hole_set"], out["hole_src"] = "套A", "文本点名「套 A / PIN-SET-2」"
    else:
        out["hole_set"], out["hole_src"] = "套A", "(正文未点名 ⇒ 按 PIN-SET-2 套 A 定版口径判)"
    return out


def derive_standing(bff, frames: dict) -> dict:
    """L2: 无认领句时的【现行几何口径】—— 全部现读, 不写死。

    · 板长 × 板宽 = `service_port_check.BASE['pcb_l'] × BASE['pcb_w']`
    · 帧 id      = `cal:FRAMES` 里 width_mm × height_mm 与之相等的那一套
    · 板厚       = `BASE['pcb_thk']`
    · 层数       = `cal:FRAMES[帧].layers`
    · 孔位口径   = `board_frame_feasibility.PIN_SET_A` (PIN-SET-2 套 A)
    ⇒ 对应 `MECH/BOARD_GEOM_30MM.md` §1/§3 (60×30 / 1.00mm / 6 层 / 套 A 四孔) —— 人读权威表在那边。
    """
    base = dict(bff.BASE)
    l, w = float(base["pcb_l"]), float(base["pcb_w"])
    fid = None
    for k, spec in frames.items():
        if abs(float(spec.get("width_mm", -1)) - l) < 1e-6 and abs(float(spec.get("height_mm", -1)) - w) < 1e-6:
            fid = k
            break
    spec = frames.get(fid) or {}
    return {
        "frame_id": fid,
        "frame_src": "service_port_check BASE['pcb_l'×'pcb_w'] = %s×%s ⇒ cal:FRAMES 尺寸反查" % (l, w),
        "thk": float(base["pcb_thk"]),
        "thk_src": "service_port_check BASE['pcb_thk']",
        "layers": int(spec["layers"]) if spec.get("layers") is not None else None,
        "layers_src": "cal:FRAMES[%s].layers" % fid,
        "hole_set": "套A",
        "hole_src": "board_frame_feasibility.PIN_SET_A (PIN-SET-2 套 A)",
    }


# ==================================================================================================
# ★阈值来源表 (★每个阈值都能追到一行出处 · 代码里没有第二份阈值表★)
# ==================================================================================================
def threshold_table(bff, spc, rows: list, frames: dict) -> list:
    """允许板厚集 / 层数档集 / 判据阈值 —— 全部现读, 逐条给出处。"""
    allowed_thk = sorted({r["thk"] for r in rows if r["cavity_ok"]})
    ok, diffs = zero_drift_check(bff, spc)
    out = [
        ("允许板厚集 (C3)",
         "{%s}" % ", ".join("%.2f" % t for t in allowed_thk),
         "board_frame_feasibility 36 档的 `cavity_ok` 现推 (盖板内腔 ≥ BASE['cavity_req']) ⇒ 不是抄的阈值表"),
        ("层数档集 (C4)",
         "{%s}" % ", ".join(str(x) for x in bff.LAYER_TIERS),
         "MECH/board_frame_feasibility.py LAYER_TIERS (只读 import)"),
        ("板厚档全集 (36 档枚举)",
         "{%s}" % ", ".join("%.2f" % t for t, _ in bff.THICKNESS_TIERS),
         "MECH/board_frame_feasibility.py THICKNESS_TIERS (只读 import)"),
        ("盖板内腔判据",
         "%.2f mm" % bff.BASE["cavity_req"],
         "MECH/service_port_check.py BASE['cavity_req'] (经 board_frame_feasibility 转手)"),
        ("余量判据 CRIT",
         "%.2f mm" % bff.CRIT,
         "MECH/service_port_check.py CRIT = 2 × TOL['fdm_part'] (经 board_frame_feasibility 转手)"),
        ("镜脚内腔 cav_h / cav_v / cav_l",
         "%s / %s / %s mm" % (bff.BASE["cav_h"], bff.BASE["cav_v"], bff.BASE["cav_l"]),
         "MECH/service_port_check.py BASE['cav_h'/'cav_v'/'cav_l']"),
        ("帧 id 唯一权威表",
         "、".join(sorted(frames["frames"].keys())),
         "HW/PCB/BOARD_FRAME_CALIBER.md §2 `cal:FRAMES` (只读)"),
        ("现役帧 current_frame",
         "%s" % frames.get("current_frame"),
         "HW/PCB/BOARD_FRAME_CALIBER.md §2 `cal:FRAMES.current_frame` (只读)"),
        ("零漂移对拍 (BASE/TOL/CRIT)",
         "逐项相等" if ok else "★不等: %s" % ",".join(diffs),
         "board_frame_feasibility 转手的值 vs service_port_check.py 原件 (独立只读 import 两次)"),
    ]
    return out


# ==================================================================================================
# ★C7 的「逐字含三个数」存在性判据 (★独立于 C1~C6 的取值解析★)
# ==================================================================================================
def literal_three_hits(text: str, frames: dict, thk_tiers, layer_tiers) -> list:
    """答案正文里逐字命中的三个数 (帧 id / 板厚 / 层数) —— ★C7 的存在性判据用★

    ★口径 (★与「C1~C6 判值合法性」严格分工: C7 只判**在不在**, C3/C4 判**合不合法**★)★:
      · 帧 id = `cal:FRAMES` 三套 id 之一的**字面串**出现在正文里
      · 板厚 = 正文里 `板厚/厚度` 后 (或 `N.NN mm` 形式) 的那个**数字** (取值不限 ⇒ 1.22 也算"写了板厚")
      · 层数 = 正文里 `层数` 后 (或 `N 层` 形式) 的那个**数字** (取值不限 ⇒ 8 也算"写了层数")
    ⇒ 答案只有一句「板框已定」 ⇒ 三样一个都没有 ⇒ C7 判红 (空转闭合)
    ★档集不是写死的: 板厚档全集 / 层数档集都从 `board_frame_feasibility` 只读 import 现读,
      本函数只把它们当**展示用**的档位说明, 判据本身只看「正文里有没有写」。
    """
    hits = []
    ids = sorted(frames.keys())
    for fid in ids:
        if fid and fid in text:
            hits.append(("帧 id", fid))
            break
    if not hits:
        # ★与 C1 同口径: 正文里若写的是【等价尺寸串】(如「板框用 60×30」) ⇒ 也能解析出帧 id
        #   (★C7 判的是「答案里逐字含三个数」, 不许用空话糊弄 ⇒ 尺寸串能反查到帧 id 就算写到了★)
        fid, _src = _find_frame_id(text, frames)
        if fid:
            hits.append(("帧 id", fid))
    thk, thk_src = _find_thickness(text)
    if thk is not None:
        hits.append(("板厚", "%.2f" % thk))
    layers, layers_src = _find_layers(text)
    if layers is not None:
        hits.append(("层数", str(layers)))
    return hits


# ==================================================================================================
# 主判定
# ==================================================================================================
def judge(root: str) -> dict:
    bff = load_bff(root)
    spc = load_spc(root)
    rows = bff.all_rows()
    frames = read_cal_frames(root)

    claim_raw = read_claim(root)
    has_claim = bool(claim_raw["text"].strip())

    if has_claim:
        subject = parse_claim(claim_raw["text"], frames["frames"])
        subject["origin"] = "L1 U-1 认领句 (need 已闭合 ⇒ 从严判) · 来源: %s" % claim_raw["src"]
    else:
        subject = derive_standing(bff, frames["frames"])
        subject["origin"] = "L2 现行几何口径 (need 未闭合 ⇒ U-1 还没拍)"

    # ---- 阈值 (全部现读) ----
    allowed_thk = sorted({r["thk"] for r in rows if r["cavity_ok"]})
    allowed_layers = sorted(int(x) for x in bff.LAYER_TIERS)
    frame_ids = sorted(frames["frames"].keys())
    current_frame = frames.get("current_frame")

    results = []   # (代号, 是否通过, 标题, 理由, 依据)

    # ---- C1 帧 id ∈ 三套之内 且非空 ----
    fid = subject.get("frame_id")
    if fid is None:
        results.append(("C1", False, "帧 id ∈ cal:FRAMES 三套之内 且非空",
                        "认领句/现行口径里没有解析出帧 id (空 / 拼错 / 第四个值)",
                        subject.get("frame_src") or "(无)"))
    elif fid in frame_ids:
        results.append(("C1", True, "帧 id ∈ cal:FRAMES 三套之内 且非空",
                        "帧 id = `%s` ∈ {%s}" % (fid, ", ".join(frame_ids)), subject.get("frame_src")))
    else:
        results.append(("C1", False, "帧 id ∈ cal:FRAMES 三套之内 且非空",
                        "帧 id = `%s` ∉ {%s} (第四个值 / 拼错)" % (fid, ", ".join(frame_ids)),
                        subject.get("frame_src")))

    # ---- C2 帧 id == cal:FRAMES.current_frame (只在有认领句时判) ----
    if not has_claim:
        results.append(("C2", True, "帧 id == cal:FRAMES.current_frame",
                        "★尚无 U-1 认领句 ⇒ 本条无对照文档 ⇒ 不判红 (ISS-316 §2-4 C2 的判红条件是以"
                        "「认领句写 X 但 current_frame 仍是 Y」措辞写的; U-1 落表后本条立即生效)",
                        "cal:FRAMES.current_frame = `%s`" % current_frame))
    elif fid == current_frame:
        results.append(("C2", True, "帧 id == cal:FRAMES.current_frame",
                        "认领句帧 id = `%s` == cal:FRAMES.current_frame" % fid,
                        "cal:FRAMES.current_frame"))
    else:
        results.append(("C2", False, "帧 id == cal:FRAMES.current_frame",
                        "认领句帧 id = `%s` ≠ cal:FRAMES.current_frame = `%s` (两处各写各的, 谁都没错, 合起来错)"
                        % (fid, current_frame), "cal:FRAMES.current_frame"))

    # ---- C3 板厚 ∈ 允许板厚集 ----
    thk = subject.get("thk")
    allow_txt = "{%s}" % ", ".join("%.2f" % t for t in allowed_thk)
    if thk is None:
        results.append(("C3", False, "板厚 ∈ 允许板厚集",
                        "缺板厚 (认领句/现行口径里没解析出板厚)", "允许板厚集 = %s" % allow_txt))
    elif any(abs(thk - t) < 1e-9 for t in allowed_thk):
        results.append(("C3", True, "板厚 ∈ 允许板厚集",
                        "板厚 = %.2f mm ∈ %s" % (thk, allow_txt), subject.get("thk_src")))
    else:
        cav = next((r for r in rows if abs(r["thk"] - thk) < 1e-9), None)
        extra = ""
        if cav is not None:
            extra = (" (盖板内腔 %.2f < %.2f, 余 %+.2f ⇒ 永判红)"
                     % (cav["cavity"], bff.BASE["cavity_req"], cav["cavity_margin"]))
        results.append(("C3", False, "板厚 ∈ 允许板厚集",
                        "板厚 = %.2f mm ∉ %s%s" % (thk, allow_txt, extra), subject.get("thk_src")))

    # ---- C4 层数 ∈ 层数档集 ----
    layers = subject.get("layers")
    lay_txt = "{%s}" % ", ".join(str(x) for x in allowed_layers)
    if layers is None:
        results.append(("C4", False, "层数 ∈ 层数档集",
                        "缺层数 (认领句/现行口径里没解析出层数)", "层数档集 = %s" % lay_txt))
    elif layers in allowed_layers:
        results.append(("C4", True, "层数 ∈ 层数档集",
                        "层数 = %d ∈ %s" % (layers, lay_txt), subject.get("layers_src")))
    else:
        results.append(("C4", False, "层数 ∈ 层数档集",
                        "层数 = %d ∉ %s" % (layers, lay_txt), subject.get("layers_src")))

    # ---- 定位 (帧, 板厚, 层数) 组合 ----
    row = None
    if fid is not None and thk is not None and layers is not None:
        row = next((r for r in rows
                    if r["frame_id"] == fid and r["layers"] == layers and abs(r["thk"] - thk) < 1e-9), None)
    # ★孔位成立性只跟【帧】有关 (孔壁 vs 板边, 与板厚/层数无关) ⇒ 板厚缺了也能判★
    frame_row = next((r for r in rows if r["frame_id"] == fid), None) if fid else None

    # ---- C5 孔位 = PIN-SET-2 套 A 四孔 且该帧上四孔全部成立 ----
    hole_set = subject.get("hole_set")
    if hole_set == "套B":
        results.append(("C5", False, "孔位 = PIN-SET-2 套 A 四孔 且该帧上四孔全部成立",
                        "孔位口径错: 认领句点名「套 B」(套 B 已于 ISS-192 被否决 ⇒ 套 A 是定版口径)",
                        subject.get("hole_src")))
    elif frame_row is None:
        results.append(("C5", False, "孔位 = PIN-SET-2 套 A 四孔 且该帧上四孔全部成立",
                        "没有可定位的帧 (帧=%s) ⇒ 孔位成立性无法判 ⇒ 按 fail-closed 判红" % fid,
                        "36 档矩阵 (board_frame_feasibility.all_rows())"))
    elif not frame_row["holes"]["all_fit"]:
        bad = [h for h in frame_row["holes"]["holes"] if not h["fit"]]
        detail = " · ".join("%s 板外 %.2f" % (h["hole"], h["outside_mm"]) for h in bad)
        results.append(("C5", False, "孔位 = PIN-SET-2 套 A 四孔 且该帧上四孔全部成立",
                        "该帧上套 A 四孔不成立 (%s) ⇒ 开口 Y 的 P-5 判据无基准" % detail,
                        "36 档矩阵 row['holes']['all_fit'] == false"))
    else:
        results.append(("C5", True, "孔位 = PIN-SET-2 套 A 四孔 且该帧上四孔全部成立",
                        "孔位口径 = PIN-SET-2 套 A; 该帧 (`%s`) 四孔全部成立 (holes.all_fit == true)" % fid,
                        subject.get("hole_src")))

    # ---- C6 该 (帧, 板厚, 层数) 组合在 36 档里 can_open == true 且 red_reasons == [] ----
    if row is None:
        results.append(("C6", False, "(帧, 板厚, 层数) 组合在 36 档里 can_open == true",
                        "组合 (帧=%s, 板厚=%s, 层数=%s) 不在 36 档矩阵里 (或前面的判据缺值) ⇒ 判红"
                        % (fid, subject.get("thk"), subject.get("layers")),
                        "36 档矩阵 (board_frame_feasibility.all_rows())"))
    elif row["can_open"] and not row["red_reasons"]:
        results.append(("C6", True, "(帧, 板厚, 层数) 组合在 36 档里 can_open == true",
                        "组合 (帧=%s, 层=%d, 板厚=%.2f) can_open == true 且 red_reasons == []"
                        % (row["frame_id"], row["layers"], row["thk"]),
                        "36 档矩阵 row['can_open']"))
    else:
        results.append(("C6", False, "(帧, 板厚, 层数) 组合在 36 档里 can_open == true",
                        "组合 (帧=%s, 层=%d, 板厚=%.2f) 不能开 ⇒ %s"
                        % (row["frame_id"], row["layers"], row["thk"], "; ".join(row["red_reasons"])),
                        "36 档矩阵 row['red_reasons']"))

    # ---- C7 need 已闭合 + 答案正文逐字含三个数 ----
    closed = claim_raw["closed_in_ledger"] or claim_raw["closed_by_merge"]
    hits = literal_three_hits(claim_raw["text"], frames["frames"],
                              bff.THICKNESS_TIERS, bff.LAYER_TIERS) if has_claim else []
    if not closed:
        results.append(("C7", False, "need `%s` 已闭合 且答案逐字含帧 id + 板厚 + 层数" % NEED_KEY,
                        "need `%s` 未闭合 (mech.yaml needs_closed 里零条 + pm.yaml answers 里零条 ⇒ 闸还没满足); "
                        "板框三选一 (B160x100 / F30A / P60x15) 仍待老板拍 ⇒ ★今天红 = U-1 还没拍, 正确★"
                        % NEED_KEY, claim_raw["src"]))
    elif not has_claim:
        results.append(("C7", False, "need `%s` 已闭合 且答案逐字含帧 id + 板厚 + 层数" % NEED_KEY,
                        "need 已闭合, 但答案正文取不到 ⇒ 三个数一个都没读到 (空转闭合)", claim_raw["src"]))
    elif len(hits) < 3:
        got = "、".join("%s %s" % (a, b) for a, b in hits) if hits else "一个都没有"
        results.append(("C7", False, "need `%s` 已闭合 且答案逐字含帧 id + 板厚 + 层数" % NEED_KEY,
                        "need 已闭合, 但答案正文里只读到 %d/3 个数 (%s) ⇒ 不许用空话闭合" % (len(hits), got),
                        claim_raw["src"]))
    else:
        results.append(("C7", True, "need `%s` 已闭合 且答案逐字含帧 id + 板厚 + 层数" % NEED_KEY,
                        "已闭合 且答案正文逐字含 %s" % " + ".join("%s %s" % (a, b) for a, b in hits),
                        claim_raw["src"]))

    return {
        "results": results,
        "subject": subject,
        "claim": claim_raw,
        "frames": frames,
        "allowed_thk": allowed_thk,
        "allowed_layers": allowed_layers,
        "current_frame": current_frame,
        "rows_n": len(rows),
        "bff": bff,
        "spc": spc,
        "has_claim": has_claim,
    }


def print_report(rep: dict) -> None:
    bff, spc = rep["bff"], rep["spc"]
    print("=" * 104)
    print("BOARD FRAME FREEZE GATE — ISS-336 「板只改一次」那一趟的【板框冻结闸 U-1】 | mech-lead 2026-11-19")
    print("=" * 104)
    print("★只读: service_port_check.py / board_frame_feasibility.py / HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES /")
    print("  state/fragments/{mech,pm}.yaml ⇒ **本脚本零写盘** (板 md5 / 网表 / 脚表 / BOM 一个字节没动)")
    print("★证据级: 全部几何读数 = 设计态几何 + 公差栈 ⇒ [推算]; 盘上板读数 = [实测]")
    print("★本闸不代老板拍 U-1: 板框三选一只「列档 + 判红原因 + 谁拍」")
    print()
    print("【判定对象】%s" % rep["subject"].get("origin"))
    print("   帧 id = %s  (%s)" % (rep["subject"].get("frame_id"), rep["subject"].get("frame_src")))
    print("   板厚   = %s  (%s)" % (rep["subject"].get("thk"), rep["subject"].get("thk_src")))
    print("   层数   = %s  (%s)" % (rep["subject"].get("layers"), rep["subject"].get("layers_src")))
    print("   孔位   = %s  (%s)" % (rep["subject"].get("hole_set"), rep["subject"].get("hole_src")))
    print()
    print("【表 0】判据来源表 (★每个阈值都能追到一行出处; 本脚本阈值零自造 = 只读 import★)")
    print("-" * 104)
    for name, val, src in threshold_table(bff, spc, bff.all_rows(), rep["frames"]):
        print("  %-26s = %-30s ← %s" % (name, val, src))
    print()
    print("【C1~C7】七条判据逐条 (★ISS-316 §2-4 设计稿的逐字实现★)")
    print("-" * 104)
    for code, ok, title, reason, src in rep["results"]:
        print("  %s %s  %s" % (code, "✅ 通过" if ok else "❌ 判红", title))
        print("       理由: %s" % reason)
        print("       依据: %s" % src)
    print()
    reds = [r[0] for r in rep["results"] if not r[1]]
    if not reds:
        print("★结论: C1~C7 全绿 ⇒ 板框已冻结 (帧 id / 板厚 / 层数 / 孔位口径 四项齐全且自洽)")
    else:
        print("★结论: %d 条判红 ⇒ %s" % (len(reds), "; ".join(reds)))
        print("  ★本闸只报「哪条红 + 为什么红」, 不代拍 (★板框三选一 = 老板级★)")
    print("  ★真源提醒: C7 读的是**分片侧** (`state/fragments/mech.yaml` 的 needs_closed + answers, 以及")
    print("    `state/fragments/pm.yaml` 的 answers 配对闭合) —— `state/issue_log.yaml` 顶层只有")
    print("    _schema / _owners_legal / issues 三项 ⇒ **零条 need 闭合记录** ⇒ 读它 = 引用盘上不存在的字段。")
    print("=" * 104)


def print_c7_source(root: str) -> None:
    """逐字打印 C7 读哪份文件 / 读哪个字段 / 怎么匹配 (★ISS-336 交卷页 §B5 登记的订正★)"""
    rep = read_claim(root)
    print("=" * 104)
    print("C7 真源口径 (★2026-11-19 本机实读确认★)")
    print("=" * 104)
    print("【读哪份文件】")
    print("  ① state/fragments/mech.yaml  ← need `%s` 的登记所在分片 (owner=mech-lead)" % NEED_KEY)
    print("  ② state/fragments/pm.yaml    ← main 的分片 (merge 口径的配对闭合落在这里)")
    print("  ✗ state/issue_log.yaml       ← 顶层只有 _schema / _owners_legal / issues 三项 ⇒ 零条 need 闭合记录")
    print("                                ⇒ **不读它** (引用盘上不存在的字段 = ISS-281 §3-S10 那一类病)")
    print("【读哪个字段】")
    print("  ① 闭合台账: needs_closed[] 里 key == `%s` 的那条" % NEED_KEY)
    print("     (字段 key/iss/closed_at/closed_by/cls/action/reason/evidence/evidence_level/answer_key/answer_ref)")
    print("  ② 答案正文: answers[] 里 key == `%s` 的那条的 value 字段" % NEED_KEY)
    print("     (回落顺序: mech answers[NEED_KEY].value → needs_closed.answer_key 对应的 answers.value →")
    print("      pm.yaml 同 key 的 answers.value → needs_closed.evidence + .reason)")
    print("【怎么匹配】")
    print("  · 闭合 = ① 或 ② 任一命中 (merge.py 口径: needs_from × answers 按 key 配对, 作者 = need 的 to)")
    print("  · 内容 = 答案正文逐字含【帧 id + 板厚 + 层数】三个数")
    print("     (帧 id = cal:FRAMES 三套 id 的字面串; 板厚 = 0.80/1.00/1.22/1.60 的字面串;")
    print("      层数 = `层数` 后的数字或 `N 层`) ⇒ 「板框已定」这种空话 ⇒ 一个都没有 ⇒ 判红")
    print()
    print("【本机实测读数】")
    print("  闭合台账命中 (mech.yaml needs_closed) = %s" % rep["closed_in_ledger"])
    print("  merge 配对闭合 (pm.yaml answers)      = %s" % rep["closed_by_merge"])
    print("  仍在 mech.yaml needs_from (未退休)      = %s" % rep["still_in_needs_from"])
    print("  答案正文来源                            = %s" % rep["src"])
    print("  答案正文 (前 300 字)                     = %s" % (rep["text"][:300] if rep["text"] else "(空)"))
    ol = rep.get("open_ledger")
    if ol:
        print("  needs_open_ledger 的 why               = %s" % str(ol.get("why"))[:400])
    print("=" * 104)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT, help="★只读别的根 (沙盒副本用); 默认 = 本脚本所在仓库根")
    ap.add_argument("--json", action="store_true", help="机器可读")
    ap.add_argument("--print-c7-source", action="store_true",
                    help="逐字打印 C7 读哪份文件/哪个字段/怎么匹配")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.print_c7_source:
        print_c7_source(root)
        return 0

    rep = judge(root)
    if args.json:
        print(json.dumps({
            "gate": "check_board_frame_freeze_gate",
            "iss": "ISS-336",
            "root": root,
            "mode": "L1-claim" if rep["has_claim"] else "L2-standing",
            "subject": dict(rep["subject"]),
            "allowed_thk": rep["allowed_thk"],
            "allowed_layers": rep["allowed_layers"],
            "current_frame": rep["current_frame"],
            "rows_n": rep["rows_n"],
            "claim_src": rep["claim"]["src"],
            "claim_closed_in_ledger": rep["claim"]["closed_in_ledger"],
            "claim_closed_by_merge": rep["claim"]["closed_by_merge"],
            "criteria": [{"code": c, "ok": o, "title": t, "reason": r, "source": s}
                         for c, o, t, r, s in rep["results"]],
            "rc": 0 if all(r[1] for r in rep["results"]) else 2,
        }, ensure_ascii=False, indent=2, default=str))
        return 0 if all(r[1] for r in rep["results"]) else 2

    print_report(rep)
    return 0 if all(r[1] for r in rep["results"]) else 2


if __name__ == "__main__":
    sys.exit(main())
