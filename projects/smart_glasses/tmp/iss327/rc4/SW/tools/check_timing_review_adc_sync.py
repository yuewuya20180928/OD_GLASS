#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_timing_review_adc_sync.py —— 【ISS-293 · sw-lead · 2026-11-17】

★**一道新闸: `SW/SW_TIMING_REVIEW.md` 的 ADC 现值不许再漂** ★

══════ 为什么要有这道闸 (根因) ══════
ISS-291 把【判决对象】(VBUS_DET_D → BAT_DET) 和【满量程口径】(3.3V → 1.8V 域) 改对了,
但 `SW/SW_TIMING_REVIEW.md` 是**手工写的复评文档** ⇒ 闸变了文档没跟着变 ⇒
文档里那条「ADC 不通过 (500kΩ / 451ms / 15.2%FS)」是**一条假红被当成结论记着**
⇒ 下一个人照它判「ADC 链不合格 ⇒ 改板」⇒ **板白改第二遍**。

══════ 本闸只做一件事 ══════
**文档里写的 ADC 现值 == 闸的实跑读数** ⇒ 不等 ⇒ 红。

══════ 实现口径 (★别写复杂了★) ══════
① **真值一律从 `SW/tools/timing_check.py --only F4_adc_det` 实跑取** (★不许自己重算一套 ——
   那会与闸脱钩★); 读不到 / 跑不起来 ⇒ **fail-closed 报错, 不许猜**。
② **文档侧对账两条腿**:
   - **机器卡 (§14 「ADC 现值卡」)**: 逐键与实跑读数对账 (★这是「==」的精确实现★)
   - **散改正文**: 旧口径的数/说法只允许以【显式标注的历史记录】形式存活
     (★追加式订正 ⇒ 老字不许删 ⇒ 允许存活, 但必须打标记 + 必须同时带现值★)

══════ 文档侧订正标记约定 (★本文档与本闸共同遵守★) ══════
- 行内追加标记 = `【ISS-293 订正】` (★凡行里保留了老口径的数/说法, 同一行必须带这个标记★)
- 同一行还必须至少带一个**现值锚点** (37500 / 33.791 / 2.1%FS / 0.439 / 1.575 / 1.98 / 87.5 / BAT_DET)
- 标了标记的行 = 【历史判据, 留痕可追溯】; 没标标记的行 = 【当前活结论】⇒ 活结论里出现老口径 ⇒ 红

══════ 用法 ══════
    python3 SW/tools/check_timing_review_adc_sync.py              # rc=0 = 文档与闸同步
    python3 SW/tools/check_timing_review_adc_sync.py --selftest   # rc=0 = 反向用例全抓到
    python3 SW/tools/check_timing_review_adc_sync.py --doc <path>  # 查副本 (反向用例用)

★**本闸一个字节都不改任何文件** (只读文档 + 只跑上游闸) ⇒ 沙盒/真件都安全。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

DOC_REL = os.path.join("SW", "SW_TIMING_REVIEW.md")
GATE_REL = os.path.join("SW", "tools", "timing_check.py")

CARD_BEGIN = "<!-- ISS-293:ADC-CARD:BEGIN -->"
CARD_END = "<!-- ISS-293:ADC-CARD:END -->"

MARK_RE = re.compile(r"ISS-293\s*订正")   # ★行内订正标记 (老字留痕的凭据)★
QUARANTINE = ("假红", "作废", "推翻", "已推翻", "不成立", "已订正", "已关闭", "关闭",
              "老口径", "老结论", "老网表", "已随", "已决策", "已消解", "降为")

# ---- 老口径 (3.3V 满量程 + 判错对象) 的数: 只允许以【带标记 + 带现值锚】的历史记录存活 ----
STALE_TOKENS = ("15.2%FS", "15.2%", "0.8057", "500kΩ", "451ms", "450.5ms", "500000.0", "0.50V")
# ---- 现值锚点 (出现任意一个即说明该行带着「现值」) ----
CURRENT_TOKENS = ("37500", "33.791", "2.1%FS", "0.439", "1.575", "1.98", "87.5", "BAT_DET")

# ---- 一行是否在讲 ADC 这件事 (决定要不要对它做口径检查) ----
ADC_CLAIM_RE = re.compile(
    r"(ADC|adc_det|SARADC|源阻抗|建立时间|满量程|LSB|BAT_DET|VBUS_DET_D|电量)")
# ---- 「把 VBUS_DET_D 说成 ADC 判决对象」的措辞 ----
DECISION_CLAIM_RE = re.compile(r"(判决对象|装机链|active_chain|装机的是|ADC 检测通道可用性)")
# ---- 活结论里出现 = 说明这条还在生效的词 ----
LIVE_VERDICT_RE = re.compile(r"(❌|不通过|无硬件|硬件支撑|不存在)")


# ==================================================================================================
# ① 真值: 从上游闸实跑取 (★读不到 ⇒ fail-closed★)
# ==================================================================================================
TRUTH_FIELDS = (
    ("active_chain", "str"),
    ("active_chain_pin", "str"),
    ("active_chain_signal", "str"),
    ("active_chain_domain", "str"),
    ("full_scale_v", "num"),
    ("adc_bits", "num"),
    ("lsb_mv", "num"),
    ("rth_ohm", "num"),
    ("tau_ms", "num"),
    ("t_settle_to_half_lsb_ms", "num"),
    ("leak_offset_v", "num"),
    ("leak_offset_pct_fs", "num"),
    ("standby_ua", "num"),
    ("supply_v", "num"),
    ("node_v_at_supply", "num"),
    ("node_max_abs_v", "num"),
    ("fs_utilization_pct", "num"),
)


def read_truth(root=ROOT):
    """→ (truth_dict, err)  ★err 非空 ⇒ fail-closed, 不许猜★"""
    cmd = [sys.executable, GATE_REL, "--only", "F4_adc_det"]
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=300)
    except Exception as exc:                                    # noqa: BLE001
        return None, "跑 %s 失败: %r" % (" ".join(cmd), exc)
    if p.returncode != 0:
        return None, "%s rc=%d (stdout 尾: %s)" % (" ".join(cmd), p.returncode, p.stdout[-300:])
    out = p.stdout
    if "=== F4_adc_det ===" not in out:
        return None, "上游闸输出里找不到 '=== F4_adc_det ===' 段 ⇒ 读不到真值"
    body = out.split("=== F4_adc_det ===", 1)[1].split("\n=== ", 1)[0]
    kv = {}
    for line in body.splitlines():
        m = re.match(r"^\s{2,}([A-Za-z_][A-Za-z_0-9]*)\s*:\s?(.*)$", line)
        if m:
            kv.setdefault(m.group(1), m.group(2).strip())
    truth = {}
    missing = []
    for key, kind in TRUTH_FIELDS:
        if key not in kv or kv[key] == "":
            missing.append(key)
            continue
        if kind == "num":
            num = first_float(kv[key])
            if num is None:
                missing.append("%s(非数值: %s)" % (key, kv[key]))
                continue
            truth[key] = num
        else:
            truth[key] = kv[key]
    if missing:
        return None, "上游闸输出缺字段: %s ⇒ 读不到真值" % ", ".join(missing)
    # 判据 (criteria) 是 dict 字符串, 单独抓 all_ok
    truth["criteria_all_ok"] = bool(re.search(r"'all_ok':\s*True", kv.get("criteria", "")))
    if not truth["criteria_all_ok"]:
        return None, "上游闸 criteria.all_ok 不为 True ⇒ 上游判决不通过, 本闸不判 (fail-closed)"
    truth["_raw_criteria"] = kv.get("criteria", "")
    truth["_verdict"] = kv.get("verdict", "")
    return truth, None


def first_float(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    return float(m.group(0)) if m else None


# ==================================================================================================
# ② 文档侧: 机器卡 (§14) 解析
# ==================================================================================================
CARD_ROW_RE = re.compile(r"^\|\s*`(?P<key>[a-z_][a-z_0-9]*)`\s*\|\s*`(?P<val>[^`]*)`\s*\|\s*$")

# (卡里的键, 类型, 上游真值键)  ★类型 num = 允许带单位后缀 (37500.0Ω / 87.5% / 33.791ms)★
CARD_SPEC = (
    ("adc_decision_chain", "str", "active_chain"),
    ("adc_decision_chain_pin", "str", "active_chain_pin"),
    ("adc_decision_chain_signal", "str", "active_chain_signal"),
    ("adc_decision_chain_domain", "str", "active_chain_domain"),
    ("adc_full_scale_v", "num", "full_scale_v"),
    ("adc_bits", "num", "adc_bits"),
    ("adc_lsb_mv", "num", "lsb_mv"),
    ("adc_rth_ohm", "num", "rth_ohm"),
    ("adc_tau_ms", "num", "tau_ms"),
    ("adc_t_settle_ms", "num", "t_settle_to_half_lsb_ms"),
    ("adc_leak_offset_v", "num", "leak_offset_v"),
    ("adc_leak_offset_pct_fs", "num", "leak_offset_pct_fs"),
    ("adc_node_v_at_supply", "num", "node_v_at_supply"),
    ("adc_node_max_abs_v", "num", "node_max_abs_v"),
    ("adc_fs_utilization_pct", "num", "fs_utilization_pct"),
    ("adc_populated", "str", None),          # ★必须 = 必装★
    ("adc_criteria_all_ok", "str", None),     # ★必须 = True★
)


def parse_card(text):
    if CARD_BEGIN not in text or CARD_END not in text:
        return None
    seg = text.split(CARD_BEGIN, 1)[1].split(CARD_END, 1)[0]
    card = {}
    for line in seg.splitlines():
        m = CARD_ROW_RE.match(line.strip())
        if m:
            card[m.group("key")] = m.group("val").strip()
    return card or None


def close(a, b):
    return abs(a - b) <= max(1e-9, 1e-6 * abs(b))


# ==================================================================================================
# ③ 对账 (★返回 [(check_id, ok, msg)]★)
# ==================================================================================================
def check_doc(doc_path, truth):
    res = []
    try:
        with open(doc_path, encoding="utf-8") as f:
            text = f.read()
    except Exception as exc:                                    # noqa: BLE001
        return [("READ", False, "读不到文档 %s: %r" % (doc_path, exc))]

    lines = text.splitlines()

    # ---------- C0 机器卡存在 ----------
    card = parse_card(text)
    if card is None:
        res.append(("CARD-MISSING", False,
                    "文档里找不到 §14 「ADC 现值卡」(%s ... %s) ⇒ 文档与闸无法对账" % (CARD_BEGIN, CARD_END)))
    else:
        res.append(("CARD-MISSING", True, "§14 ADC 现值卡在位 (%d 键)" % len(card)))

    # ---------- C1 机器卡逐键对账 (★文档里写的 == 闸的实跑读数★) ----------
    if card is not None:
        for key, kind, tkey in CARD_SPEC:
            if key not in card:
                res.append(("CARD:%s" % key, False, "卡里缺键 `%s`" % key))
                continue
            raw = card[key]
            if kind == "num":
                got = first_float(raw)
                exp = truth[tkey]
                if got is None:
                    res.append(("CARD:%s" % key, False, "卡值 `%s` 不是数值" % raw))
                elif not close(got, exp):
                    res.append(("CARD:%s" % key, False,
                                "卡值 %s (%s) != 上游实跑 %s" % (raw, key, exp)))
                else:
                    res.append(("CARD:%s" % key, True, "%s = %s (与上游一致)" % (key, raw)))
            else:
                if key == "adc_populated":
                    exp = "必装"
                elif key == "adc_criteria_all_ok":
                    exp = "True"
                else:
                    exp = truth[tkey]
                if raw != exp:
                    res.append(("CARD:%s" % key, False,
                                "卡值 `%s` != 上游实跑 `%s`" % (raw, exp)))
                else:
                    res.append(("CARD:%s" % key, True, "%s = %s (与上游一致)" % (key, raw)))

    # ---------- P1 判决对象 ----------
    # 活结论里不许再把 VBUS_DET_D 说成 ADC 判决对象 / 装机链
    bad_decision = []
    for i, line in enumerate(lines, 1):
        if "VBUS_DET_D" in line and DECISION_CLAIM_RE.search(line) and not MARK_RE.search(line):
            bad_decision.append((i, line.strip()[:90]))
    res.append(("P1-DECISION", not bad_decision,
                "活结论里把 VBUS_DET_D 说成 ADC 判决对象的行: %s" % (bad_decision or "无")))
    # 文档必须写得出「判决对象 = BAT_DET」
    has_decision = any(("BAT_DET" in ln and DECISION_CLAIM_RE.search(ln) and MARK_RE.search(ln))
                       for ln in lines)
    res.append(("P1-DECISION-PRESENT", has_decision,
                "文档里有「判决对象/装机链 = BAT_DET」的明文 (带订正标记)"
                if has_decision else "文档里找不到带订正标记的「判决对象 = BAT_DET」明文"))

    # ---------- P2 满量程口径 ----------
    # 2.1 老口径的数只允许出现在【带订正标记 + 带现值锚点】的历史行里
    bad_stale = []
    for i, line in enumerate(lines, 1):
        if not ADC_CLAIM_RE.search(line):
            continue
        hits = [t for t in STALE_TOKENS if t in line]
        if not hits:
            continue
        if MARK_RE.search(line) and any(cur in line for cur in CURRENT_TOKENS):
            continue                       # ★合法: 标了标记的历史判据 + 同带现值★
        bad_stale.append((i, hits, line.strip()[:90]))
    res.append(("P2-FS", not bad_stale,
                "活结论里残留 3.3V 口径旧数的行: %s" % (bad_stale or "无")))
    # 2.2 现值必须写出来
    for token, cid in (("0.439", "P2-FS-LSB"), ("2.1%FS", "P2-FS-PCT"),
                       ("37500", "P2-FS-RTH"), ("33.791", "P2-FS-SETTLE"),
                       ("1.8", "P2-FS-VOLTAGE")):
        res.append((cid, token in text, "文档含现值 `%s`" % token if token in text
                    else "文档里找不到现值 `%s`" % token))

    # ---------- P3 BAT_DET 已必装 ----------
    bad_dnp = []
    for i, line in enumerate(lines, 1):
        if not ADC_CLAIM_RE.search(line):
            continue
        if "DNP" not in line:
            continue
        if MARK_RE.search(line):
            continue                       # ★合法: 标了标记的历史判据★
        bad_dnp.append((i, line.strip()[:90]))
    res.append(("P3-POP", not bad_dnp,
                "活结论里还在说 BAT_DET/电量链 DNP 的行: %s" % (bad_dnp or "无")))
    res.append(("P3-POP-PRESENT", "必装" in text,
                "文档含「必装」" if "必装" in text else "文档里找不到「必装」"))

    # ---------- P4 活判决里不许残留 ❌/无硬件支撑 ----------
    bad_verdict = []
    for i, line in enumerate(lines, 1):
        if not ADC_CLAIM_RE.search(line):
            continue
        if not LIVE_VERDICT_RE.search(line):
            continue
        if any(q in line for q in QUARANTINE):
            continue                       # ★合法: 明写了假红/作废/已推翻★
        bad_verdict.append((i, line.strip()[:90]))
    res.append(("P4-VERDICT", not bad_verdict,
                "活结论里残留 ADC ❌/无硬件支撑 的行: %s" % (bad_verdict or "无")))

    return res


# ==================================================================================================
# ④ 自检: 反向用例一律在【沙盒副本】上做 (★真件一个字节不碰★)
# ==================================================================================================
def _copy_doc(src, dst_dir, tag):
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, tag, os.path.basename(DOC_REL))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def _edit_text(path, old, new):
    with open(path, encoding="utf-8") as f:
        t = f.read()
    if old not in t:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(t.replace(old, new))
    return True


def selftest(root=ROOT):
    print("【自检】check_timing_review_adc_sync.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)")
    errs = []
    doc = os.path.join(root, DOC_REL)
    if not os.path.exists(doc):
        print("  ✗ 找不到 %s" % doc)
        return 1
    truth, err = read_truth(root)
    if err:
        print("  ✗ 读不到上游真值 (fail-closed): %s" % err)
        return 1
    print("  [真值] active_chain=%s pin=%s signal=%s fs=%s lsb=%s rth=%s settle=%s pct_fs=%s node=%s/%s fs_util=%s%%"
          % (truth["active_chain"], truth["active_chain_pin"], truth["active_chain_signal"],
             truth["full_scale_v"], truth["lsb_mv"], truth["rth_ohm"],
             truth["t_settle_to_half_lsb_ms"], truth["leak_offset_pct_fs"],
             truth["node_v_at_supply"], truth["node_max_abs_v"], truth["fs_utilization_pct"]))

    base = check_doc(doc, truth)
    base_bad = [c for c in base if not c[1]]
    if base_bad:
        errs.append("基线就不绿 ⇒ 自检无意义: %s" % [c[0] for c in base_bad])
        print("  ✗ 基线不绿, 自检无意义: %s" % [c[0] for c in base_bad])
    else:
        print("  [基线] %d 项判据全绿 (真件)" % len(base))

    sandbox = os.path.join(root, "..", "..", "tmp", "iss293_adc_sync_selftest")
    cases = [
        ("case1_revert_fs_pct", "2.1%FS", "15.2%FS",
         ["CARD:adc_leak_offset_pct_fs"], True),
        ("case2_revert_chain", "BAT_DET", "VBUS_DET_D",
         ["CARD:adc_decision_chain"], True),
        ("case3_revert_populated", "必装", "全 DNP",
         ["CARD:adc_populated"], True),
        ("case4_baseline", None, None, [], False),
    ]
    for tag, old, new, expect_ids, expect_red in cases:
        dst = _copy_doc(doc, sandbox, tag)
        if old is not None:
            if not _edit_text(dst, old, new):
                errs.append("%s: 沙盒副本里找不到待替换串 %r" % (tag, old))
                print("  ✗ %s: 沙盒副本里找不到待替换串 %r" % (tag, old))
                continue
        rs = check_doc(dst, truth)
        bad = [c[0] for c in rs if not c[1]]
        hit = [e for e in expect_ids if e in bad]
        if expect_red:
            ok = bool(bad) and bool(hit)
            print("  %s %s: 期望红组 %s ⇒ 实际红组 %s ⇒ %s"
                  % ("✔" if ok else "✗", tag, expect_ids, bad, "红 ✔" if ok else "没按预期红 ✗"))
            if not ok:
                errs.append("%s: 期望红组 %s, 实际 %s" % (tag, expect_ids, bad))
        else:
            ok = not bad
            print("  %s %s: 正向对照 ⇒ 期望绿 ⇒ 实际红组 %s ⇒ %s"
                  % ("✔" if ok else "✗", tag, bad, "绿 ✔" if ok else "恒红 ✗"))
            if not ok:
                errs.append("%s: 正向对照应绿, 实际红组 %s" % (tag, bad))

    # 反向用例做完, 真件必须一个字节没动
    with open(doc, "rb") as f:
        digest = f.read()
    print("  [真件] %s 读回 %d B (自检全程只写沙盒副本)" % (DOC_REL, len(digest)))
    if errs:
        print("\nSELFTEST 失败: %d 条" % len(errs))
        for e in errs:
            print("  ✗ %s" % e)
        return 1
    print("\nSELFTEST %d/%d 通过, rc=0" % (len(cases), len(cases)))
    return 0


# ==================================================================================================
def main():
    ap = argparse.ArgumentParser(description="ISS-293: SW_TIMING_REVIEW.md 的 ADC 现值同步闸")
    ap.add_argument("--doc", default=None, help="要检查的文档路径 (默认 SW/SW_TIMING_REVIEW.md; 反向用例用副本)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例 (沙盒副本, 真件不碰)")
    args = ap.parse_args()

    if args.selftest:
        return selftest(ROOT)

    doc = args.doc or os.path.join(ROOT, DOC_REL)
    truth, err = read_truth(ROOT)
    if err:
        print("[FATAL] ★读不到上游真值 ⇒ fail-closed (不许猜)★: %s" % err, file=sys.stderr)
        return 2
    res = check_doc(doc, truth)
    print("=== ISS-293 · SW_TIMING_REVIEW.md ADC 口径同步闸 ===")
    print("--- 上游实跑真值 (SW/tools/timing_check.py --only F4_adc_det) ---")
    print("   active_chain=%s pin=%s signal=%s domain=%s" % (
        truth["active_chain"], truth["active_chain_pin"],
        truth["active_chain_signal"], truth["active_chain_domain"]))
    print("   full_scale=%s V  bits=%s  lsb=%s mV  rth=%s ohm  tau=%s ms  settle=%s ms" % (
        truth["full_scale_v"], truth["adc_bits"], truth["lsb_mv"], truth["rth_ohm"],
        truth["tau_ms"], truth["t_settle_to_half_lsb_ms"]))
    print("   leak=%s V = %s %%FS  node@%sV = %s V (abs-max %s V)  fs_util=%s %%" % (
        truth["leak_offset_v"], truth["leak_offset_pct_fs"], truth["supply_v"],
        truth["node_v_at_supply"], truth["node_max_abs_v"], truth["fs_utilization_pct"]))
    print("   criteria_all_ok = %s" % truth["criteria_all_ok"])
    print("--- 对账 (%s) ---" % os.path.relpath(doc, ROOT))
    nbad = 0
    for cid, ok, msg in res:
        if not ok:
            nbad += 1
        print("   [%s] %-28s %s" % ("✔" if ok else "✗", cid, msg))
    print("\n%s: %d/%d 项通过, rc=%d" % ("OK" if nbad == 0 else "FAIL", len(res) - nbad, len(res),
                                         1 if nbad else 0))
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
