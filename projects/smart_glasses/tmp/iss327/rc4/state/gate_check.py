#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目总工质量门 (Quality Gate) —— 把控 3 个子模块总工交付的可检查看板
=====================================================================
老板 10-25 09:23: "3 个子模块总工的工作和质量, 你打算如何负责把控?"

把控不能靠"我看过了", 得能**机械判定**。本脚本把"交付质量"拆成 5 个可量化指标:
  Q1 交付齐备率   交接单是否含 6 项必填验收块 (结论/自评/证据分级/接口取值/卡点/复现命令)
  Q2 证据分级率   关键结论是否标了 [实测]/[官方]/[推算]/[0数据]
  Q3 接口声明率   每个总工把自己对跨模块接口的取值写进 interface_claims (冲突才能被检出)
  Q4 需求闭环率   needs_from → answered 的闭环比例 (需求发出去有没有回音)
  Q5 硬指标覆盖   各总工交付里有没有报出硬指标数字 (功耗/皮肤温度/厚度/延迟/球间距)

用法:  python3 state/gate_check.py [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
HANDOFF = os.path.join(PROJ, "HANDOFF")
FRAG_DIR = os.path.join(HERE, "fragments")
TRACKER = os.path.join(PROJ, "PROJECT_TRACKER.md")

AGENTS = ["main", "hw-lead", "sw-lead", "mech-lead"]
FILE_OF = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}

# ★★2026-11-12 (ISS-136): 硬件侧的**真源一致性闸** ★★
#   HW/check_bq25896_pinout.py = BQ25896 24 脚 pinout 复核 + **J_CHG 跨铰链 pin map
#   规格 §5.2 表 vs 网表逐脚对拍**。
#   ★**为什么必须接进门禁链**: 它以前 rc=1 却**没人跑** ⇒ 门禁链缺它 ⇒ 规格↔网表漂移
#   长期没人拦 (ISS-136 的根因: 检查项 ⑦ 当时只比"脚本硬编快照 vs 网表",
#   **规格文件根本不在判定里** ⇒ 规格怎么改它都不红 ⇒ "一直是绿的假象")。
#   ★接进来后: 规格表再漂移一次 ⇒ 本闸红 ⇒ daily_check/alignment_check 立刻看得见。
HW_PINOUT_GATE = os.path.join(PROJ, "HW", "check_bq25896_pinout.py")

# 6 项必填验收块: (代号, 说明, 标题关键词候选)
REQUIRED_BLOCKS = [
    ("B1", "结论摘要", ["结论", "结论摘要", "结论 (给", "一句话"]),
    ("B2", "验收标准自评 (逐条 通过/不通过/未验)", ["验收标准自评", "自评", "验收标准"]),
    ("B3", "证据分级 (实测/官方/推算/0数据)", ["证据分级", "证据等级", "证据"]),
    ("B4", "接口取值声明 (interface_claims)", ["接口取值", "接口声明", "interface_claims", "接口请求"]),
    ("B5", "未决项与卡点 (需要谁回答什么)", ["阻塞", "卡点", "未决", "待办"]),
    ("B6", "自证复现命令", ["复现", "复现命令", "自证"]),
]
EVIDENCE_TAGS = ["实测", "官方", "推算", "0数据", "0 数据"]
HARD_METRICS = {
    "功耗(W)": r"\d+(\.\d+)?\s*W\b|功耗",
    "皮肤温度(°C)": r"\d+(\.\d+)?\s*°C|皮肤侧|ISO 13732",
    "镜腿/镜脚厚度(mm)": r"\d+(\.\d+)?\s*mm|厚度",
    "端到端延迟(ms)": r"\d+(\.\d+)?\s*ms|延迟",
    "FCCSP 球间距(pitch)": r"pitch|球间距|FCCSP",
}


def handoff_files() -> dict:
    """每个 agent 的**全部**交接单 (按文件名倒序 = 时间倒序; 文件名带日期前缀)。

    ★2026-11-04 10:0x 实测修正: 原来只取"最新一份" ⇒ **一份临时的 per-issue 交接单
    (结构是 §1..§10, 不是 B1-B6) 会把周更新那份合规交接单顶掉** ⇒ 齐备率 18/18 假跌成 15/18 ⇒
    漂移检测误报。⇒ 现在取**全部**, 评分时按下面 `pick_handoff` 的规则挑。
    """
    out = {}
    if not os.path.isdir(HANDOFF):
        return out
    for fn in sorted(os.listdir(HANDOFF), reverse=True):
        if not fn.endswith(".md") or fn == "README.md":
            continue
        for a in AGENTS:
            if f"_{a}_" in fn:
                out.setdefault(a, []).append(os.path.join(HANDOFF, fn))
    return out


FALLBACK_WINDOW_DAYS = 7      # ★回退到更早那份交接单的最长时效


def pick_handoff(paths):
    """→ (用来评分的那份, 最新那份, 缺口列表, 是否用了回退)

    ★规则 (2026-11-04 定): 
      ① 优先用**最新一份**交接单;
      ② 若最新一份**不是** B1-B6 结构 (例如 per-issue 单用 §1..§10), 且**7 天内**还有一份
         B1-B6 齐全的交接单 ⇒ **回退到那份评分** (并在输出里写明"最新一份缺 X, 按 Y 计分"),
         ★但**不回退到 7 天以外** (那会掩盖真倒退);
      ③ 缺口清单始终**按最新一份**报 (⇒ per-issue 单确实缺哪几块, 看得见)。
    """
    if not paths:
        return None, None, [], False
    latest = paths[0]
    def blocks_of(p):
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                t = f.read()
        except Exception:
            return None
        return check_blocks(t) if t else {}
    lb = blocks_of(latest) or {}
    miss = [c for c, b in lb.items() if not b.get("ok")]
    if not miss:
        return latest, latest, [], False
    # ★★2026-11-18 03:0x (main): ★**回退不许掩盖【真倒退】**★★
    #   ★**病灶 (★ISS-306 点名★)**: 最新那份是【标准 B1~B6 格式】但【少了块】⇒ 那就是【倒退】⇒
    #     ★**不许回退到 7 天内那份齐备的老单来把齐备率顶住** ⇒ ★**倒退必须立刻可见** ★
    #   ★**保留原意**: per-issue 单用 §1..§10 结构 (★根本不是 B1~B6 单★) ⇒ ★**允许回退** (★原设计如此★)
    try:
        _lt = open(latest, encoding="utf-8", errors="ignore").read()
    except Exception:
        _lt = ""
    _heads = re.findall(r"^#{1,4}\s*(.+)$", _lt, re.M)
    _uses_b_blocks = any(re.match(r"^\s*B[0-6]\b", h) for h in _heads)
    if _uses_b_blocks:
        # ★**它自称 B 块结构 ⇒ 缺块就是倒退 ⇒ 不回退** ★
        return latest, latest, miss, False
    # 找 7 天内 B1-B6 齐全的一份
    try:
        newest_mtime = os.path.getmtime(latest)
    except Exception:
        newest_mtime = None
    for p in paths[1:]:
        try:
            if newest_mtime and (newest_mtime - os.path.getmtime(p)) > FALLBACK_WINDOW_DAYS * 86400:
                break
        except Exception:
            continue
        pb = blocks_of(p) or {}
        if pb and all(b.get("ok") for b in pb.values()):
            return p, latest, miss, True
    return latest, latest, miss, False


def check_blocks(text: str) -> dict:
    heads = re.findall(r"^#{1,4}\s*(.+)$", text, re.M)
    blob = "\n".join(heads)
    res = {}
    for code, desc, kws in REQUIRED_BLOCKS:
        hit = any(kw in blob for kw in kws)
        res[code] = {"desc": desc, "ok": hit}
    return res


def check_evidence(text: str) -> dict:
    found = [t for t in EVIDENCE_TAGS if t in text]
    return {"tags": found, "n": len(found), "ok": len(found) >= 2}


def check_hard_metrics(text: str) -> dict:
    res = {}
    for name, pat in HARD_METRICS.items():
        res[name] = bool(re.search(pat, text))
    return res


def load_frag(aid: str) -> dict:
    p = os.path.join(FRAG_DIR, FILE_OF[aid])
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def run_hw_pinout_gate() -> dict:
    """★ISS-136 (2026-11-12): 跑 `HW/check_bq25896_pinout.py` —— 硬件侧真源一致性闸。

    ★**为什么单独一个函数**: 这个闸以前是"**孤儿**" —— rc=1 却**没有任何门禁调用它**
    ⇒ 规格 §5.2 与网表漂移长期没人拦 ⇒ ISS-136。
    ★**为什么必须 subprocess 而不是 import**: 该脚本自己带 rc 契约 (0=过 / 1=有 FAIL),
    用 subprocess 才能把它真实的失败传上来 (import 会把它的 rc 语义吃掉)。
    ★**不许让失败静默**: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律当作**闸红** (fail-closed),
    绝不 "没跑就当过" (那又是一个新的绿的假象)。
    """
    if not os.path.exists(HW_PINOUT_GATE):
        return {"ok": False, "rc": None, "name": "HW pinout 真源闸",
                "detail": f"★闸脚本不存在: {HW_PINOUT_GATE} ⇒ 视为闸红 (不许静默跳过)"}
    try:
        p = subprocess.run([sys.executable, HW_PINOUT_GATE],
                           cwd=PROJ, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "name": "HW pinout 真源闸",
                "detail": "★闸脚本超时 (300s) ⇒ 视为闸红"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "rc": None, "name": "HW pinout 真源闸",
                "detail": f"★闸脚本跑不起来: {e} ⇒ 视为闸红"}
    out = p.stdout or ""
    fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]
    detail = ("; ".join(fails) if fails else "全部检查项通过")
    if p.returncode != 0 and not fails:
        detail = f"rc={p.returncode} 但未解析出 FAIL 行: " + (p.stderr or out).strip()[-300:]
    return {"ok": p.returncode == 0, "rc": p.returncode, "name": "HW pinout 真源闸",
            "detail": detail}



# ★★2026-11-17 20:0x (main): 新闸挂进门禁链 (★fail-closed 同款语义★)
#   ★**为什么必须挂**: ISS-295 的「MECH 结构结论防漂闸」+ ISS-298 的「SW 侧合法改板通道闸」
#   ★**以前谁都不跑 ⇒ 它们的判据形同虚设** ⇒ ★**门禁链缺它 = 判据漂移无人拦 (ISS-136 同款根因)** ★
#   ★**语义与 HW pinout 闸完全一致**: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算【闸红】, 绝不「没跑就当过」★
EXTRA_GATES = [
    (os.path.join(PROJ, "MECH", "check_mech_verdict_freshness.py"), "MECH 结构结论防漂闸 (ISS-295)", ()),
    (os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py"), "SW 侧板侧输入/合法改板闸 (ISS-298)", ()),
    # ★★2026-11-18 10:5x (main): 把 ISS-318 的 SW 侧五道闸挂进门禁链 (★sw-lead 交卷页 §B4-1 逐字写法★
    #   ★**为什么必须挂**: 「板只改一次」那一趟, 板面动作一旦落地, SW 侧的护栏只有这几道
    #     ⇒ 第 1 位是【S1 位号改名漂移的唯一拦截器】(板改了但 SW 文档/代码里的位号没跟上 ⇒ 它立刻红)
    #     ⇒ 第 2 位是【落表留痕义务】(板改了但单号/md5 没留痕 ⇒ 它立刻红)
    #   ★**为什么之前没人挂**: ISS-318 交卷页 §B5-2 第 1 条自己写明「闸【没挂链】· 卡在 main (机制地界)」★**
    #   ★**三道 selftest 闸【必须裸跑】**: 它们本来就是 selftest 脚本 ⇒ 带 --selftest 会 rc=2 usage 错误
    #   ★**TMPDIR 指到项目内**: 本机 /tmp 带 usrquota 且配额已满 ⇒ 不指会 EDQUOT 假红
    #   ★**fail-closed 语义不变**: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算【闸红】(run_external_gate 原语义)
    (os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py"),
     "SW 侧位号引用可达性闸 (ISS-318)", ()),
    (os.path.join(PROJ, "SW", "tools", "check_landing_trace_obligation.py"),
     "SW 侧落表留痕义务闸 (ISS-315)", ()),
    (os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec_r6_hardprot_iss315_selftest.py"),
     "SW 侧 R6 硬保护路径反向用例 (ISS-315)", ("--tmpdir", os.path.join(PROJ, "tmp", "iss318_gates"))),
    (os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec_r6_chainjudge_selftest.py"),
     "SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312)", ("--tmpdir", os.path.join(PROJ, "tmp", "iss318_gates"))),
    (os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec_r6_selftest.py"),
     "SW 侧 R6 判决源反向用例 (ISS-309 · 7/7)", ("--tmpdir", os.path.join(PROJ, "tmp", "iss318_gates"))),
]

# ★★2026-11-17 22:1x (main): 9 道「钉板 md5 闸」挂进门禁链 (★ISS-136 同款根因的最后一处★)
#   ★**为什么必须挂**: 这 9 道是「板 md5 钉死」判据的持有者 (★ISS-292/296/297/298 建好了【合法改板通道】★)
#     ⇒ 「板只改一次」那一趟当天, 板 md5 一旦偏离, **只有它们能拦** ⇒ 它们在链外 = 判据形同虚设
#     ⇒ ★**与 ISS-136 完全同款**: 「以前谁都不跑 ⇒ 漂移长期没人拦」★
#   ★**为什么现在才挂**: 第 5 道 `HW/check_pin_function_labels.py` 此前 rc=1 (★基线常量停在 ISS-257 旧值★)
#     ⇒ 挂上去链当场红 ⇒ ★**main 把它排进 ISS-299 (hw-lead 在飞) 重锚 ⇒ 交卷后再挂**★
#     ⇒ ★**本清单里 9 道现在全绿 (2026-11-17 22:0x main 本机实跑) ⇒ 可以挂**★
#   ★**per-gate 参数 (★为什么必须支持★)**: 不同闸的「绿」口径不一样 ——
#     · `check_pin_function_labels.py` 的**已知缺陷基线**要靠 `--expect-known` 才是绿 (★裸跑必然 rc=1★
#       ★因为它把「15 条脚表功能缺陷」当成失败 ⇒ 那是**冻结快照**, 不是回归★ ⇒ 不加参数挂上去 = 假红★)
#     · 其余 8 道裸跑即绿 ⇒ 参数为空
#   ★**fail-closed 语义不变**: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算【闸红】, 绝不「没跑就当过」★
PINNED_MD5_GATES = [
    (os.path.join(PROJ, "HW", "check_fsin_rootcause.py"), "钉板闸① FSIN 根因闸", ()),
    (os.path.join(PROJ, "HW", "check_g1a7_selection_landed.py"), "钉板闸② G1a-7 选型落表闸", ()),
    (os.path.join(PROJ, "HW", "check_onepass_commit_order.py"), "钉板闸③ 改板提交顺序闸", ()),
    (os.path.join(PROJ, "HW", "check_onepass_preflight_coverage.py"), "钉板闸④ 作业包覆盖度闸", ()),
    (os.path.join(PROJ, "HW", "check_pin_function_labels.py"), "钉板闸⑤ 脚表功能标签闸", ("--expect-known",)),
    (os.path.join(PROJ, "HW", "check_workpack_state_values.py"), "钉板闸⑥ 作业包现状值闸", ()),
    (os.path.join(PROJ, "MECH", "check_board_frame_coords.py"), "钉板闸⑦ 板框坐标闸", ()),
    (os.path.join(PROJ, "MECH", "check_demo_struct_truth.py"), "钉板闸⑧ 结构真值闸", ()),
    (os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py"), "钉板闸⑨ SW 侧合法改板通道闸", ()),
]


def run_external_gate(path: str, name: str, args=()) -> dict:
    """通用 fail-closed 外部闸 (★抄 HW pinout 闸的语义, 不另发明★)

    ★2026-11-17 22:1x (main): 加 per-gate 参数 `args` (★tuple★)
      ⇒ ★**为什么**: 不同闸的「绿」口径不同 (★例: `check_pin_function_labels.py` 裸跑 rc=1 是因为
        「15 条脚表功能缺陷」是**冻结快照**不是回归 ⇒ 必须 `--expect-known` 才绿★)
      ⇒ ★**不许**为了挂上去绿而改闸本体 (★那是 agent 的地界★) ⇒ 参数是唯一正确的适配手段★
    """
    if not os.path.exists(path):
        return {"ok": False, "rc": None, "name": name,
                "detail": f"★闸脚本不存在: {path} ⇒ 视为闸红 (不许静默跳过)"}
    cmd = [sys.executable, path] + list(args)
    try:
        p = subprocess.run(cmd, cwd=PROJ, capture_output=True,
                           text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "name": name, "detail": "★闸脚本超时 (300s) ⇒ 视为闸红"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "rc": None, "name": name, "detail": f"★闸脚本跑不起来: {e} ⇒ 视为闸红"}
    out = p.stdout or ""
    fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]
    detail = ("; ".join(fails) if fails else "全部检查项通过")
    if p.returncode != 0 and not fails:
        detail = f"rc={p.returncode} 但未解析出 FAIL 行: " + (p.stderr or out).strip()[-300:]
    return {"ok": p.returncode == 0, "rc": p.returncode, "name": name, "detail": detail}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    handoffs = handoff_files()
    report = {"agents": {}, "gaps": []}

    # 全局答案索引: 别人回答给我的 key
    global_answers = {}
    # 全局需求索引: 每个人发出的 needs key (用来判断我的 answers 是否真对上了别人的需求)
    global_needs = {}
    for aid in AGENTS:
        d = load_frag(aid)
        for a in d.get("answers") or []:
            k, to = a.get("key"), a.get("to")
            if k and to:
                global_answers.setdefault(to, set()).add(k)
        for n in d.get("needs_from") or []:
            if n.get("key"):
                global_needs.setdefault(n["key"], {})[aid] = n.get("to")

    for aid in AGENTS:
        d = load_frag(aid)
        hp, hp_latest, hp_miss, hp_fallback = pick_handoff(handoffs.get(aid) or [])
        text = ""
        if hp and os.path.exists(hp):
            with open(hp, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        blocks = check_blocks(text) if text else {}
        ev = check_evidence(text) if text else {"tags": [], "n": 0, "ok": False}
        hm = check_hard_metrics(text) if text else {}

        needs = d.get("needs_from") or []
        answers = d.get("answers") or []
        answered_keys = {a.get("key") for a in answers if a.get("key")}
        # 【问方视角】我的需求被别人答了没有 (口径与 merge.py 一致: 被问方作答才算)
        globally_answered = global_answers.get(aid, set())
        answered_incoming = sum(1 for n in needs if n.get("key") in globally_answered)
        # 【答方视角】我登记的答复里, 有多少真对上了别人的需求 key
        effective_answers = sum(1 for a in answers
                                if any(owner == a.get("to") and tgt == aid
                                       for owner, tgt in global_needs.get(a.get("key"), {}).items()))
        # ★ 真·可立即闭: 答案写在被问方交接单正文里, 但没登记进 answers
        #   (用 need.item 的中文原文去被问方文档里搜 —— key 是英文, 搜 key 没用)
        closable = 0
        closable_detail = []
        for n in needs:
            if n.get("waiting_on", "agent") != "agent":
                continue
            k = n.get("key")
            if k in globally_answered:
                continue                      # 已被答方登记 → merge 已闭合
            item = (n.get("item") or "").strip()
            probe = item[:8] if len(item) >= 8 else item
            if not probe:
                continue
            for other in AGENTS:
                if other == aid or other not in handoffs:
                    continue
                try:
                    body = open(handoffs[other], encoding="utf-8").read()
                except Exception:
                    continue
                if probe and probe in body:
                    closable += 1
                    closable_detail.append(f"{aid}←{other} {k}")
                    break
        ext = sum(1 for n in needs if n.get("waiting_on", "agent") != "agent")
        # 自闭合: 需求的发起人自己回答了它 (说明 key 双向重用时 to 写错了)
        self_closed = 0
        for n in needs:
            k = n.get("key")
            # 需求发起人自己答了自己 (author==owner 且 to==owner) → 真自闭合
            if any(a.get("key") == k and a.get("to") == aid for a in answers):
                self_closed += 1
        ext_st = sum(1 for n in needs if n.get("state") == "waiting_external")
        claims = d.get("interface_claims") or []

        entry = {
            "handoff": os.path.basename(hp) if hp else None,
            "handoff_latest": os.path.basename(hp_latest) if hp_latest else None,
            "handoff_latest_miss": hp_miss,
            "handoff_fallback": hp_fallback,
            "blocks": blocks,
            "blocks_ok": sum(1 for b in blocks.values() if b["ok"]),
            "blocks_total": len(REQUIRED_BLOCKS),
            "evidence": ev,
            "hard_metrics": hm,
            "hard_metrics_n": sum(1 for v in hm.values() if v),
            "interface_claims": len(claims),
            "needs_total": len(needs),
            "needs_answered_incoming": answered_incoming,
            "answers_registered": len(answers),
            "answers_effective": effective_answers,
            "needs_closable_unregistered": closable,
            "needs_closable_detail": closable_detail,
            "needs_self_closed": self_closed,
            "needs_waiting_external": ext,
            "artifacts": len(d.get("artifacts") or []),
            "blockers": len(d.get("blockers") or []),
        }
        report["agents"][aid] = entry

    # ---- 全局汇总 ----
    subs = [a for a in AGENTS if a != "main"]
    tot_b = sum(report["agents"][a]["blocks_total"] for a in subs)
    ok_b = sum(report["agents"][a]["blocks_ok"] for a in subs)
    tot_n = sum(report["agents"][a]["needs_total"] for a in subs)
    ok_n = sum(report["agents"][a]["needs_answered_incoming"] for a in subs)
    tot_c = sum(report["agents"][a]["interface_claims"] for a in subs)
    ev_ok = sum(1 for a in subs if report["agents"][a]["evidence"]["ok"])
    hm_ok = sum(1 for a in subs if report["agents"][a]["hard_metrics_n"] >= 3)

    tot_closable = sum(report["agents"][a]["needs_closable_unregistered"] for a in subs)
    tot_ext = sum(report["agents"][a]["needs_waiting_external"] for a in subs)
    # ★ 全局口径 (含 main) —— 规则与 merge.py **完全一致**, 两边数字必须对得上
    #   merge.py: ans = [a for a in answers_by_key[k] if a["_by"] == ask_to]
    #   → 需求 (owner,key,to) 被闭合 ⟺ 存在 key 相同且 author == to 的答复
    all_frags = {aid: load_frag(aid) for aid in AGENTS}
    _answers_by_key = {}
    for _aid, _d in all_frags.items():
        for _a in (_d.get("answers") or []):
            if _a.get("key"):
                # ★ 作者 = 分片归属的 agent (merge.py 就是这么记的: {"**a, "_by": aid})
                _answers_by_key.setdefault(_a["key"], []).append(_aid)
    def _answered(n):
        k, to = n.get("key"), n.get("to")
        # 老板决策 (need 带 decision 字段, 由项目总工代录) 同样算闭合
        if n.get("decision"):
            return True
        # ★★2026-11-06 20:6x 【与 merge.py 对齐, 修对账 ok=false】: ★**老板拍过板的 key 是全局事实**
        #   ⇒ ★**同 key 在别的分片没回写 decision 时, 这边也必须判 answered**
        #   ⇒ ★**唯一真源 = `state/decision_truth.py`** (★三处平行实现只改一处 ⇒ 这次漏改就红了)
        if k and k in _dec_keys:
            return True
        return bool(to) and to in (_answers_by_key.get(k) or [])
    # ★**老板决策全局 key 集合 (唯一真源: state/decision_truth.py)**
    try:
        from decision_truth import decision_keys as _dk
    except Exception as _e:  # noqa: BLE001
        # ★**响亮失败, 不静默降级** (★防口径漂移 ⇒ 宁可直接挂)
        sys.exit("★decision_truth 导入失败 ⇒ 拒绝跑 (防口径漂移): %s" % _e)
    _dec_keys = _dk(all_frags)
    glob_ext = sum(1 for aid, d in all_frags.items() for n in (d.get("needs_from") or [])
                   if (n.get("waiting_on") or "agent") != "agent" and not _answered(n))
    glob_pending = sum(1 for aid, d in all_frags.items() for n in (d.get("needs_from") or [])
                       if (n.get("waiting_on") or "agent") == "agent" and not _answered(n))
    # ★ 与 merge.py 自对账 (防止两边口径再次漂移)
    _recon = None
    try:
        with open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8") as f:
            _st = yaml.safe_load(f) or {}
        _ms = (_st.get("summary") or {})
        _recon = {
            "merge_open_needs": _ms.get("open_needs"),
            "gate_global_pending": glob_pending,
            "merge_waiting_external": _ms.get("waiting_external_needs"),
            "gate_global_waiting_external": glob_ext,
            "ok": (_ms.get("open_needs") == glob_pending
                   and _ms.get("waiting_external_needs") == glob_ext),
        }
    except Exception as e:  # noqa: BLE001
        _recon = {"error": str(e), "ok": None}

    report["summary"] = {
        "blocks_ok": ok_b, "blocks_total": tot_b,
        "needs_closable_unregistered": tot_closable,
        "needs_waiting_external": tot_ext,
        "global_waiting_external": glob_ext,
        "global_pending": glob_pending,
        "reconciliation": _recon,
        "evidence_ok_agents": ev_ok, "evidence_total_agents": len(subs),
        "needs_answered_incoming": ok_n, "needs_total": tot_n,
        "answers_effective": sum(report["agents"][a]["answers_effective"] for a in subs),
        "answers_registered": sum(report["agents"][a]["answers_registered"] for a in subs),
        "interface_claims_total": tot_c,
        "hard_metric_agents": hm_ok, "hard_metric_total_agents": len(subs),
    }

    # ★★2026-11-12 (ISS-136): 硬件侧真源一致性闸 ⇒ **真门禁** (不是只打印一行)
    #   ★这条闸决定了本脚本的 rc: 硬件闸红 ⇒ gate_check 红 ⇒ daily_check / alignment_check 立刻看得见。
    #   ★**以前这个脚本 rc=1 却没人跑** ⇒ 门禁链缺它 ⇒ 规格↔网表漂移无人拦 (ISS-136 根因)。
    hw_gate = run_hw_pinout_gate()
    report["hw_pinout_gate"] = hw_gate
    report["summary"]["hw_pinout_gate_ok"] = hw_gate["ok"]
    report["summary"]["extra_gates_ok"] = True

    # ★★2026-11-17 20:0x (main): 新闸挂链 (★ISS-295 / ISS-298·★fail-closed 同款★)★★
    report["extra_gates"] = []
    extra_ok = True
    for _p, _n, _a in EXTRA_GATES:
        _g = run_external_gate(_p, _n, _a)
        report["extra_gates"].append(_g)
        report["summary"][f"extra_gate_ok::{_n}"] = _g["ok"]
        if not _g["ok"]:
            extra_ok = False
            report["gaps"].append(f"★新闸红: {_g['name']} — {_g['detail']}")

    # ★★2026-11-17 22:1x (main): 9 道「钉板 md5 闸」挂链 (★ISS-136 同款根因的最后一处★)
    #   ★**板只改一次那一趟的护栏**: 板 md5 偏离时, **只有这 9 道能拦** ⇒ 链外 = 判据形同虚设★
    report["pinned_md5_gates"] = []
    pinned_ok = True
    for _p, _n, _a in PINNED_MD5_GATES:
        _g = run_external_gate(_p, _n, _a)
        report["pinned_md5_gates"].append(_g)
        report["summary"][f"pinned_gate_ok::{_n}"] = _g["ok"]
        if not _g["ok"]:
            pinned_ok = False
            report["gaps"].append(f"★钉板闸红: {_g['name']} — {_g['detail']}")

    # ---- 缺口清单 (可直接转成派活项) ----
    for a in subs:
        e = report["agents"][a]
        for code, desc, _ in REQUIRED_BLOCKS:
            if not e["blocks"].get(code, {}).get("ok"):
                report["gaps"].append(f"{a}: 交接单缺 [{code}] {desc}"
                                      + (f" (最新一份 {e.get('handoff_latest')} 也缺, 已回退用 {e.get('handoff')} 计分)" if e.get("handoff_fallback") else ""))
        if not e["evidence"]["ok"]:
            report["gaps"].append(f"{a}: 关键结论未做证据分级 (实测/官方/推算/0数据)")
        if e["interface_claims"] < 3:
            report["gaps"].append(f"{a}: interface_claims 只有 {e['interface_claims']} 条 → 冲突检测形同虚设 (目标 ≥3 条关键接口)")
        if e["needs_closable_unregistered"]:
            report["gaps"].append(f"{a}: {e['needs_closable_unregistered']} 条需求**对方已答但没登记 answers** → 状态源说\"没人答\", 会导致重复催办 (立即可闭)")
        real_open = e["needs_total"] - e["needs_answered_incoming"] - e["needs_closable_unregistered"] - e["needs_waiting_external"]
        if real_open > 0:
            report["gaps"].append(f"{a}: {real_open} 条需求确实还没人答 (等另一个总工)")
    # ★ISS-136: 硬件闸红 ⇒ 进缺口清单 (不许只在正文里飘一行)
    if not hw_gate["ok"]:
        report["gaps"].append(f"★硬件闸红: {hw_gate['name']} — {hw_gate['detail']}")
    # ★★2026-11-18 03:0x (main): ★**「用了回退」本身要是一条独立告警** (★不许把齐备率被顶住这件事埋在句子里★)
    for _a in AGENTS:
        _e = report["agents"].get(_a) or {}
        if _e.get("handoff_fallback"):
            report["gaps"].append(
                f"★{_a}: Q1 齐备率用了【回退】⇒ 最新一份 {(_e.get('handoff_latest') or '?')} 缺块, 按老的 {(_e.get('handoff') or '?')} 计分 ⇒ "
                f"★**齐备率被顶住, 不代表最新交付齐** ★")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return 0 if (hw_gate["ok"] and extra_ok and pinned_ok) else 1

    s = report["summary"]
    print("=" * 74)
    print("项目总工质量门 · 3 个子模块总工交付看板")
    print("=" * 74)
    print(f"\n【Q1 交付齐备率】 {s['blocks_ok']}/{s['blocks_total']} 个必填验收块齐全")
    for a in subs:
        e = report["agents"][a]
        miss = [c for c, b in e["blocks"].items() if not b["ok"]]
        extra = ""
        if e.get("handoff_fallback"):
            extra = f"   ★按 {e['handoff']} 计分 (最新一份 {e['handoff_latest']} 缺 {e.get('handoff_latest_miss')})"
        print(f"   {a:<10} {e['blocks_ok']}/{e['blocks_total']}  缺: {miss or '无'}   交接单: {e['handoff']}{extra}")
    print(f"\n【Q2 证据分级率】 {s['evidence_ok_agents']}/{s['evidence_total_agents']} 个总工的交付做了证据分级")
    for a in subs:
        print(f"   {a:<10} 标签: {report['agents'][a]['evidence']['tags'] or '无'}")
    print(f"\n【Q3 接口声明率】 全员 interface_claims 共 {s['interface_claims_total']} 条 (目标 ≥3 条/总工 → 冲突才能自动检出)")
    for a in subs:
        print(f"   {a:<10} {report['agents'][a]['interface_claims']} 条")
    print(f"\n【Q4 需求闭环率】")
    print(f"   问方视角 (我的需求被别人答了): {s['needs_answered_incoming']}/{s['needs_total']}  ← 与 merge.py 口径一致")
    print(f"   答方视角 (我登记的答复): {s['answers_registered']} 条, 其中 {s['answers_effective']} 条真对上了别人的需求 key")
    for a in subs:
        e = report["agents"][a]
        print(f"   {a:<10} 被答 {e['needs_answered_incoming']}/{e['needs_total']} | 我答 {e['answers_registered']} 条(有效 {e['answers_effective']})"
              f" | 产出 {e['artifacts']} | 阻塞 {e['blockers']}")
    print(f"   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: {s['needs_closable_unregistered']} 条  ← 需人工判定, 也有可能是 waiting_on 标错")
    print(f"   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 {s['needs_waiting_external']} 条 | **全局 {s['global_waiting_external']} 条** (含 main)")
    print(f"   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 {s['global_pending']} 条**")
    rc = s.get("reconciliation") or {}
    if rc.get("ok") is True:
        print(f"   ✅ 与 merge.py 自对账一致 (等外部 {rc['merge_waiting_external']} / 等总工 {rc['merge_open_needs']})")
    elif rc.get("ok") is False:
        print(f"   ❌ 与 merge.py **不一致** (merge: 外部 {rc['merge_waiting_external']} / 总工 {rc['merge_open_needs']}"
              f" vs gate: 外部 {rc['gate_global_waiting_external']} / 总工 {rc['gate_global_pending']}) → 先重跑 merge.py")
    else:
        print(f"   ⚠️ 对账未完成: {rc.get('error', 'STATE.yaml 读不到')} → 先跑 merge.py")
    sc = sum(report["agents"][a]["needs_self_closed"] for a in subs)
    print(f"   ⚠️ 自闭合 (自己答自己 = to 写错): {sc} 条")
    overloaded = {k: list(v.keys()) for k, v in global_needs.items() if len(v) > 1}
    if overloaded:
        print(f"   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): {len(overloaded)} 个")
        for k, owners in list(overloaded.items())[:5]:
            print(f"      {k}: 发起方 {owners}")
    print(f"\n【Q5 硬指标覆盖】 {s['hard_metric_agents']}/{s['hard_metric_total_agents']} 个总工报出了 ≥3 类硬指标数字")
    for a in subs:
        e = report["agents"][a]
        hit = [k for k, v in e["hard_metrics"].items() if v]
        print(f"   {a:<10} {e['hard_metrics_n']}/5 类: {hit}")
    # ★★2026-11-12 (ISS-136): 硬件侧真源一致性闸 —— **真门禁** (红 ⇒ 本脚本 rc=1)
    print(f"\n【Q6 硬件真源闸】 {hw_gate['name']}: "
          f"{'✅ 通过' if hw_gate['ok'] else '❌ 红了'} (rc={hw_gate['rc']})")
    print(f"   {hw_gate['detail']}")
    if not hw_gate["ok"]:
        print("   ★⇒ 规格 §5.2 与网表漂移 / 硬件 pinout 不合规 ⇒ 本闸红, 不许投板")
    # ★★2026-11-17 22:1x (main): 9 道钉板 md5 闸的链上读数 (★板只改一次那一趟的护栏★)★★
    _pg = report["pinned_md5_gates"]
    _pg_ok = sum(1 for _x in _pg if _x["ok"])
    print(f"\n【Q7 钉板 md5 闸链】 {_pg_ok}/{len(_pg)} 道绿 (★9 道全部 fail-closed 挂在门禁链里★)")
    for _x in _pg:
        print(f"   {'✅' if _x['ok'] else '❌'} {_x['name']}: rc={_x['rc']}")
    if not pinned_ok:
        print("   ★⇒ 板 md5 / 落表链 / 结构真值 出现漂移 ⇒ 板那一趟不许开工")
    print(f"\n【缺口清单】(可直接转成下一轮派活项) —— {len(report['gaps'])} 条")
    for g in report["gaps"]:
        print(f"   · {g}")
    print("\n" + "=" * 74)
    # ★闸红 ⇒ rc=1 (以前这个硬件闸是孤儿: rc=1 却没人跑 ⇒ 门禁链缺它)
    return 0 if (hw_gate["ok"] and extra_ok and pinned_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
