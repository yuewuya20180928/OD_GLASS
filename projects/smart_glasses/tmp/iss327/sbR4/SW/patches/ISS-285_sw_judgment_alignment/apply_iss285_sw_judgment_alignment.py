#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-285 · sw-lead · 一次性补丁套用器 (★情形二才跑★)
=====================================================================
★★【落表之后: SW 侧三道判据过期】★★ —— ★**零写板 · 零落表 · 零改 HW/ MECH/ 文件**★

本脚本干三件事 (★全部只改 SW 侧两个文件★):

  ★B1★ `SW/tools/timing_check.py` 的【网表锚点判据】改成读【落表台账链头】
       (★与 `SW/tools/check_demo_panel_spec.py` 的 R6 同一个判决源 · 同一份实现 ⇒ 真同源★)
       ⇒ 授权落表后不再红; 悄悄换真源照样红; fail-closed 三条一条不动。
  ★B2★ `SW/tools/timing_check.py` 的 F4' 期望从「BAT_DET 三颗全 DNP」改成
       「BAT_DET 三颗必装 (V-3=E 落表后)」⇒ ★按【器件本体行】逐颗读 dnp★。
  ★B3★ `SW/tools/timing_check.py` 追加一条反向用例 REV-11 (把 BAT_DET 三颗改回 DNP ⇒ 必须变红)。

  ★**另** (可选, `--reanchor`): 把 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点副本
       前移到【落表台账链头】(★历史留痕同步, 不是"让闸变绿的手段"★ —— 见方案页 §2.3★)。

★**判据方向一个字没变**: 盘上真源 md5 ∉ 台账登记的合法状态集合 ⇒ 仍必须红。
★**fail-closed 三条一条没动**: 链头不唯一 / 链断 / 链头无单号 ⇒ 红。
★**不许把落表台账当"锚点可写集合"**: 落表台账 append-only + 链完整性防线没松。

跑法:
    python3 SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py --dry-run
    python3 SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py --apply
    python3 SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py --apply --reanchor

退出码: 0 = 套用成功 (或已是最新 · 幂等) · 1 = 失败 (锚点没命中 / 套用后自检红)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))      # projects/smart_glasses
TARGET = os.path.join("SW", "tools", "timing_check.py")
LEDGER = os.path.join("SW", "SW_MD5_BASELINE_LEDGER.md")
BAK_DIR_REL = os.path.join("state", ".bak_iss285_sw_alignment")

# ★★【每条编辑的「已套用特征标记」】★★
#   ★幂等判定必须用【标记】而不是【整段逐字相等】——
#     后续单号 (★ISS-288 落地补丁 + 再往后的单号继续改同一段★) 会让整段逐字相等不再成立
#     ⇒ 只认标记 ⇒ 本套用器在【已套过 / 又被后人改过】的树上都只报「已是最新」, 不崩、不瞎改 ★
EDIT_MARKERS = {
    "B1-1 判决源同源化 (头)": "def _dps():",
    "B1-2 判决源同源化 (尾)": "判决源 = 落表台账【链头】",
    "B2-1 逐颗读器件本体行": '"device_populated":',
    "B2-2 verdict 不许说假话": "_bat_det_verdict(det_chains)",
    "B2-3 F4' 判据": "; BAT_DET 三颗必装",
    "B3 REV-11 反向用例": "REV-11 反向: 把 BAT_DET 三颗",
}

# ===================================================================== 补丁正文
# ---------------------------------------------------------------- B1-1: 判决源同源化
OLD_B1 = '''def _netlist_baseline_state():
    """→ (状态串, 允许的网表 md5 集合, 详情)。三方对账: 锚点 ↔ 落表台账 ↔ 盘上真源。"""
    got = _sw_anchor_entries()
    if not isinstance(got, tuple) or got[0] is None:
        why = got[1] if isinstance(got, tuple) else "未知"
        return ("BAD", set(), "读不到 SW 台账锚点: %s" % why)
    (anchors, entry), _ = got
    want = str(entry.get("md5") or "")
    prev = str(entry.get("prev_md5") or "")
    by = str(entry.get("by") or "")
    if not want:
        return ("BAD", set(), "锚点里 %s 没登记 md5" % NETLIST_REL)
'''

NEW_B1 = '''# ★★【ISS-285 · 2026-11-17 · sw-lead】★★ 网表锚点判据的【判决源同源化】
#   ★★【根因】同一个事实 («网表当前合法 md5 是多少») 原有两个判决源 ⇒ 授权落表后一个绿一个红:
#     ① `SW/tools/check_demo_panel_spec.py` 的 R6 ⇒ 判决源 = 落表台账【链头】 ⇒ 绿 ✅
#     ② 本文件的网表锚点判据 ⇒ 判决源 = SW 台账 §1 锚点块里【冻结的 md5】 ⇒ 红 ❌
#   ★★【修法落在「让两个判据源同源」, 不落在「放宽判据」★★
#   ★★【四条不许破】★★
#     ① 判据方向不许变: 盘上真源 md5 ∉ 台账登记的合法状态集合 ⇒ 仍必须红 (这一条逐字保留)
#     ② 不许把「取不准」放宽成「取最近一条」⇒ fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条都不许动
#     ③ 不许把落表台账当「锚点可写集合」⇒ 落表台账 append-only + 链完整性防线不许松
#     ④ 不许弱化 ISS-275 已跑通的那条链头逻辑 ⇒ 链头实现**直接 import R6 那份**
#        (★同域 SW/tools, 不 import MECH —— 那是别人地界★) ⇒ 链头 / 链 / 产出单号 逐字一致,
#        且 `check_demo_panel_spec.py` 一个字节没被本单碰过 ⇒ 第 ④ 条自动成立

def _dps():
    """→ (R6 那个文件的模块, 错误原因)。读不到 ⇒ (None, 原因) ⇒ 判红 (fail-closed)。"""
    global _DPS
    if _DPS is None:
        import importlib.util
        p = os.path.join(_HERE, "check_demo_panel_spec.py")
        try:
            spec = importlib.util.spec_from_file_location("_sw_dps_iss285", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _DPS = mod
        except Exception as exc:                  # ★fail-closed: 读不到判决源实现 ⇒ 红, 不许降级★
            return None, "读不到 R6 判决源实现 %s: %s" % (p, exc)
    return _DPS, ""


_DPS = None


def _device_dnp_rows(nl, ref: str) -> list:
    """该位号的【器件本体行】(type ∉ {NET, TP}) 上的 dnp 列表。

    ★为什么要单独一个读法: `Netlist.dnp_of()` 取的是【该位号第一条行】的 dnp
      ⇒ 同一个位号有多行时可能拿错行 (ISS-190 的老教训) ⇒ 判据要判【器件本体行】。
    ★空列表 = 该位号在网表里没有器件本体行 ⇒ 判据不许当「装上了」 (fail-closed)。
    """
    return [x.get("dnp", "") for x in nl.rows_of(ref) if x.get("type") not in ("NET", "TP")]


def _netlist_baseline_state():
    """→ (状态串, 允许的网表 md5 集合, 详情)。三方对账: 锚点 ↔ 落表台账 ↔ 盘上真源。

    ★★【ISS-285】判决源 = 【落表台账链头】, 与 `check_demo_panel_spec.py` 的 R6 **同源** ★★
      ① 盘上真源的 md5 必须 == 台账链头 (★判据方向不许变★)
      ② 链头取不准 (不唯一 / 链断 / 有记录不在链上 / 链头没单号) ⇒ 一律判红 (★fail-closed 三条一条没动★)
      ③ 域侧锚点副本降级为【历史留痕】: 允许停在历史值, 但不许胡说
         (md5 必须在台账链上 + 落表单号必须与台账产出该 md5 的单号对得上 + 旧 md5 也必须在链上)
    """
    got = _sw_anchor_entries()
    if not isinstance(got, tuple) or got[0] is None:
        why = got[1] if isinstance(got, tuple) else "未知"
        return ("BAD", set(), "读不到 SW 台账锚点: %s" % why)
    (anchors, entry), _ = got
    want = str(entry.get("md5") or "")
    prev = str(entry.get("prev_md5") or "")
    by = str(entry.get("by") or "")
    if not want:
        return ("BAD", set(), "锚点里 %s 没登记 md5" % NETLIST_REL)
'''

OLD_B1_TAIL = '''    # ① 落表台账对账: 单号 + 文件名 + 新旧 md5 必须在同一行
    recs = []
    for spec in ((anchors.get("source_ledger") or {}).get("landing_records")) or []:
        p = os.path.join(_PROJECT_ROOT, spec)
        if os.path.isfile(p):
            recs.append((spec, open(p, encoding="utf-8").read()))
            continue
        d = os.path.dirname(spec) or "."
        b = os.path.basename(spec)
        for hit in sorted(glob.glob(os.path.join(_PROJECT_ROOT, d, b))):
            recs.append((os.path.relpath(hit, _PROJECT_ROOT),
                         open(hit, encoding="utf-8").read()))
    if not recs:
        return ("BAD", {want}, "落表台账位置一个都不存在")
    hit = None
    for name, text in recs:
        if by and by not in text:
            continue
        ok = False
        for line in text.split("\\n"):
            if NETLIST_REL not in line:
                continue
            if not _md5_seen(line, want):
                continue
            if prev and not _md5_seen(line, prev):
                continue
            ok = True
            break
        if ok:
            hit = name
            break
    if hit is None:
        return ("BAD", {want}, "落表台账里查不到 (单号 %s / 文件 %s / 新 md5 %s / 旧 md5 %s)"
                % (by or "无", NETLIST_REL, want[:12], prev[:12] if prev else "无"))
    # ② 盘上真源 vs 锚点
    disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)
    got_md5 = hashlib.md5(open(disk, "rb").read()).hexdigest() if os.path.exists(disk) else ""
    if got_md5 != want:
        return ("BAD", {want}, "盘上真源 md5 %s ≠ 锚点登记 %s (真源被换了或锚点过期)"
                % (got_md5, want))
    allowed = {want} | ({prev} if prev else set())
    return ("OK", allowed, "落表台账 = %s (单号 %s) · 盘上 md5 = %s" % (hit, by, got_md5))
'''

NEW_B1_TAIL = '''    # ★★【ISS-285】判决源 = 落表台账【链头】(★与 R6 同一份实现 ⇒ 真同源★) ★★
    dps, err = _dps()
    if dps is None:
        return ("BAD", set(), err)
    led_text, led_spec = dps.sw_ledger_canonical_text(_PROJECT_ROOT, anchors)
    if not led_text:
        return ("BAD", set(), "判决源落表台账读不到 ⇒ 无从对账 (fail-closed)")
    st = dps.sw_ledger_state(NETLIST_REL, led_text)
    recs = st.get("records") or []
    head = st.get("head")
    known = set(st.get("known") or set())
    if not recs:
        return ("BAD", set(), "落表台账 (%s) 里查不到 %s 的任何落表记录" % (led_spec, NETLIST_REL))
    if not head:
        return ("BAD", set(), "落表台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红"
                % (st.get("why")))
    if not st.get("head_iss"):
        return ("BAD", known, "落表台账最新记录 (%s) 缺落表单号 (字段缺失) ⇒ 判红" % head)
    if not st.get("chain"):
        return ("BAD", known, "落表台账链断了 / 不唯一 (%s)" % (st.get("why")))
    orphan = sorted({r["new"] for r in recs} - set(st.get("chain") or []))
    if orphan:
        return ("BAD", known, "落表台账里有记录不在链上 = %s" % orphan)
    # ★★【域侧锚点副本 = 历史留痕】允许停在历史值, 但不许胡说 ★★
    am = want[:12]
    if am not in known:
        return ("BAD", known, "锚点副本 md5 %s 台账链里查不到 (锚点胡说?)" % (am or "(空)"))
    if by and by not in (st.get("producer") or {}).get(am, set()):
        return ("BAD", known, "锚点副本落表单号 %s 与台账对不上 (台账产出该 md5 的单号 = %s)"
                % (by or "(空)", sorted((st.get("producer") or {}).get(am, []))))
    if prev and prev[:12] not in known:
        return ("BAD", known, "锚点副本旧 md5 %s 台账链里查不到 (历史留痕断了?)" % prev[:12])
    # ★★【判据方向不许变】盘上真源 vs 台账链头 ★★
    disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)
    got_md5 = hashlib.md5(open(disk, "rb").read()).hexdigest() if os.path.exists(disk) else ""
    if got_md5[:12] != head:
        return ("BAD", known, "盘上真源 md5 %s ≠ 台账链头 %s (真源被换了或台账没更新)"
                % (got_md5[:12], head))
    return ("OK", known, "判决源 = %s 链头 %s (单号 %s) · 盘上 md5 = %s"
            % (led_spec, head, ",".join(st.get("head_iss") or []), got_md5))
'''

# ---------------------------------------------------------------- B2-1: 逐颗读器件本体行
OLD_B2A = '''        det_chains.append({
            "tag": tag, "r_top_ohm": rt, "r_bot_ohm": rb, "c_f": cv,
            "r_top_dnp": nl.dnp_of(top) or nl.rows_of(top)[0].get("dnp", "") if nl.rows_of(top) else "",
            "r_bot_dnp": nl.rows_of(bot)[0].get("dnp", "") if nl.rows_of(bot) else "",
            "c_dnp": nl.rows_of(cap)[0].get("dnp", "") if nl.rows_of(cap) else "",
            "populated": bool(nl.rows_of(top)) and nl.rows_of(top)[0].get("dnp") == "必装"
                          and bool(nl.rows_of(bot)) and nl.rows_of(bot)[0].get("dnp") == "必装",
        })
'''

NEW_B2A = '''        dev_dnp = {r: _device_dnp_rows(nl, r) for r in (top, bot, cap)}
        det_chains.append({
            "tag": tag, "r_top_ohm": rt, "r_bot_ohm": rb, "c_f": cv,
            "r_top_dnp": nl.dnp_of(top) or nl.rows_of(top)[0].get("dnp", "") if nl.rows_of(top) else "",
            "r_bot_dnp": nl.rows_of(bot)[0].get("dnp", "") if nl.rows_of(bot) else "",
            "c_dnp": nl.rows_of(cap)[0].get("dnp", "") if nl.rows_of(cap) else "",
            "populated": bool(nl.rows_of(top)) and nl.rows_of(top)[0].get("dnp") == "必装"
                          and bool(nl.rows_of(bot)) and nl.rows_of(bot)[0].get("dnp") == "必装",
            # ★★【ISS-285】逐颗【器件本体行】的 dnp (★不许拿该位号第一条行★)
            "device_dnp": dev_dnp,
            "device_populated": bool(dev_dnp.get(top)) and all(d == "必装" for d in dev_dnp.get(top))
                                and bool(dev_dnp.get(bot)) and all(d == "必装" for d in dev_dnp.get(bot))
                                and bool(dev_dnp.get(cap)) and all(d == "必装" for d in dev_dnp.get(cap)),
        })
'''

# ---------------------------------------------------------------- B2-2: verdict 不许说假话
OLD_B2B = '''        "verdict": "★现网表装机的是 %s 链 (%s+%s+%s): 源阻抗 %sΩ / τ=%sms; 12bit 精度需 %.0fms 建立; "
                   "1µA 漏电流 ⇒ %.2fV 偏移 (%.0f%% 满量程) ⇒ 该分压值对 ADC 不可用; "
                   "★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**全是 DNP** ⇒ **电量检测分压在现网表上不存在**"
                   % (act[0]["tag"], act[0]["r_top_ohm"], act[0]["r_bot_ohm"], act[0]["c_f"],
                      rth, r(tau_adc * 1e3), t_settle * 1e3, leak_err,
                      leak_err / DEVICE["V_DET_FS"] * 100),
'''

NEW_B2B = '''        "verdict": "★现网表装机的是 %s 链 (%s+%s+%s): 源阻抗 %sΩ / τ=%sms; 12bit 精度需 %.0fms 建立; "
                   "1µA 漏电流 ⇒ %.2fV 偏移 (%.0f%% 满量程) ⇒ 该分压值对 ADC 不可用; "
                   "%s"
                   % (act[0]["tag"], act[0]["r_top_ohm"], act[0]["r_bot_ohm"], act[0]["c_f"],
                      rth, r(tau_adc * 1e3), t_settle * 1e3, leak_err,
                      leak_err / DEVICE["V_DET_FS"] * 100, _bat_det_verdict(det_chains)),
'''

# ---------------------------------------------------------------- B2-3: 判据 + helper
OLD_B2C = '''    ("F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP",
     lambda o: o["F4_adc_det"]["active_chain"] == "VBUS_DET_D"
               and all(not c["populated"] for c in o["F4_adc_det"]["chains"] if c["tag"] == "BAT_DET")),
'''

NEW_B2C = '''    ("F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)",
     lambda o: o["F4_adc_det"]["active_chain"] == "VBUS_DET_D"
               and _bat_det_all_populated(o)),
'''

HELPER_B2 = '''

# ===================================================================== F4' / BAT_DET 口径 (ISS-285)
# ★★【ISS-285 · 2026-11-17 · sw-lead】★★ BAT_DET 三颗的期望值随 V-3=E 落表翻了:
#   ★旧期望 (落表前): 「BAT_DET 三颗全 DNP」⇒ 落表后【过期】⇒ 红 ★
#   ★新期望 (落表后): 「BAT_DET 三颗必装」★ (证据 = HW/netlist_v1.csv L182/L183/L184 + 落表台账 §16 老板凭据)
#   ★**判据强度不许比原来弱**: 原来判「三颗**没有**装机」(一个负面事实),
#     现在判「三颗**逐颗**按【器件本体行】都是必装」(全集正面事实 + 三颗都必须在场) ⇒ **更强** ★
#   ★**逐颗读【器件本体行】的 dnp**, 不读该位号第一条行 (ISS-190 的老教训: dnp 是行级, 拿错行 = 假绿) ★
BAT_DET_REFS = ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT")


def _bat_det_all_populated(o: dict) -> bool:
    """BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 逐颗【器件本体行】必装?"""
    chains = [c for c in (o.get("F4_adc_det") or {}).get("chains") or [] if c.get("tag") == "BAT_DET"]
    if len(chains) != 1:
        return False
    dev = chains[0].get("device_dnp") or {}
    if set(dev) != set(BAT_DET_REFS):
        return False
    for ref in BAT_DET_REFS:
        rows = dev.get(ref) or []
        if not rows or not all(d == "必装" for d in rows):
            return False
    return True


def _bat_det_verdict(det_chains: list) -> str:
    """BAT_DET 链的现状一句话 (★数据驱动 ⇒ 网表翻回 DNP 时老话自动回来★)。"""
    bat = [c for c in det_chains or [] if c.get("tag") == "BAT_DET"]
    if not bat:
        return "★BAT_DET 链在网表里查不到"
    c = bat[0]
    if not c.get("device_populated"):
        return ("★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**全是 DNP** ⇒ "
                "**电量检测分压在现网表上不存在**")
    return ("★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**已改成必装** (V-3=E 落表后) ⇒ "
            "**电量检测分压在现网表上存在** (100k+60k+100nF ⇒ R_th=%sΩ / τ=%sms)"
            % (c.get("rth_ohm"), c.get("tau_ms")))

'''

# ---------------------------------------------------------------- B1-3: md5 比较口径 (12 位前缀)
OLD_B1C = '''def netlist_md5_allowed(md5: str) -> bool:
    """这个网表 md5 是落表台账登记过的状态之一吗 (落表前 / 落表后)?"""
    return md5 in _netlist_baseline_state()[1]
'''

NEW_B1C = '''def netlist_md5_allowed(md5: str) -> bool:
    """这个网表 md5 是落表台账登记过的状态之一吗 (落表前 / 落表后)?

    ★★【ISS-285】落表台账里登记的 md5 是【12 位前缀】(★R6 也是按 12 位比★
      ⇒ 这里也按 12 位前缀比, 口径与判决源 (R6) 完全一致
      (★不然拿 32 位去比 12 位前缀 ⇒ 这条恒红 = 判据自毁★)。
    ★**判据方向一个字没变**: 盘上 md5 ∉ 台账登记的状态集合 ⇒ 仍必须红。★
    """
    if not md5:
        return False
    allowed = _netlist_baseline_state()[1]
    return str(md5).strip().lower()[:12] in {str(x).strip().lower()[:12] for x in allowed}
'''

# ---------------------------------------------------------------- B3: REV-11
OLD_B3 = '''    ("REV-10 反向: 把 PG_AND 网上**任意一行**改成 DNP ⇒ 对应判据必须变红 (逐行试, 不跳行)",
     _rev_pg_and_any_row),
]
'''

NEW_B3 = '''    ("REV-10 反向: 把 PG_AND 网上**任意一行**改成 DNP ⇒ 对应判据必须变红 (逐行试, 不跳行)",
     _rev_pg_and_any_row),
    # ★★【ISS-285】F4' 期望值随落表翻了 ⇒ 必须有反向用例锁死「改回 DNP ⇒ 变红」 ★★
    _mk_reverse_dnp(
        "REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
        "F4'『BAT_DET 三颗必装』必须变红",
        targets=[("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
                 ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")],
        fn=lambda o, mo: (_bat_det_all_populated(o) is True
                          and _bat_det_all_populated(mo) is False)),
]
'''

EDITS = [
    ("B1-1 判决源同源化 (头)", OLD_B1, NEW_B1),
    ("B1-2 判决源同源化 (尾)", OLD_B1_TAIL, NEW_B1_TAIL),
    ("B1-3 md5 比较口径 (12 位前缀)", OLD_B1C, NEW_B1C),
    ("B2-1 逐颗读器件本体行", OLD_B2A, NEW_B2A),
    ("B2-2 verdict 不许说假话", OLD_B2B, NEW_B2B),
    ("B2-3 F4' 判据", OLD_B2C, NEW_B2C),
    ("B3 REV-11 反向用例", OLD_B3, NEW_B3),
]

# helper 插在哪: `NEW_TESTS = [` 之前
HELPER_ANCHOR = "\nNEW_TESTS = [\n"


# ===================================================================== 套用逻辑
def apply_edits(text: str) -> str:
    for name, old, new in EDITS:
        marker = EDIT_MARKERS.get(name)
        if marker and marker in text:
            print("★已套过 (特征标记命中: %s) ⇒ 跳过: %s" % (marker, name))
            continue                                   # ★幂等: 已套过 ⇒ 跳过
        if new in text:
            continue                                   # ★幂等: 已套过 ⇒ 跳过
        cnt = text.count(old)
        if cnt != 1:
            raise SystemExit("★锚点没命中 (或命中 %d 次): %s" % (cnt, name))
        text = text.replace(old, new)
    if "_bat_det_all_populated" not in text:
        if text.count(HELPER_ANCHOR) != 1:
            raise SystemExit("★helper 锚点没命中: NEW_TESTS = [")
        text = text.replace(HELPER_ANCHOR, HELPER_B2 + HELPER_ANCHOR)
    else:
        print("★helper 已套过 (特征标记命中: _bat_det_all_populated) ⇒ 跳过")
    return text


def md5_of(path: str) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def reanchor_ledger(root: str) -> str:
    """把 SW 台账 §1 锚点副本前移到【落表台账链头】(★历史留痕同步★)。

    ★**这不是「让闸变绿的手段」** —— B1 改完, 锚点停在历史值也是绿的;
      这一步只是让【锚点副本】跟台账链头对齐 (免得留下一条「锚点过期」的假线索)。★
    """
    sys.path.insert(0, os.path.join(root, "SW", "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_dps_reanchor", os.path.join(root, "SW", "tools", "check_demo_panel_spec.py"))
    dps = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dps)

    ledger_path = os.path.join(root, LEDGER)
    text = open(ledger_path, encoding="utf-8").read()
    anchors, err = dps.load_sw_anchor(root)
    if anchors is None:
        raise SystemExit("★读不到锚点块: %s" % err)
    led_text, led_spec = dps.sw_ledger_canonical_text(root, anchors)
    rel = os.path.join("HW", "netlist_v1.csv")
    st = dps.sw_ledger_state(rel, led_text)
    head = st.get("head")
    if not head:
        raise SystemExit("★台账链头取不准: %s" % st.get("why"))
    # 找完整 32 位 md5
    full = ""
    for r in st.get("records") or []:
        if r["new"] == head:
            full = r.get("new_full") or ""
    if not full:
        # 从台账原文里捞 32 位
        import re as _re
        for line in led_text.split("\n"):
            if rel in line and head in line:
                toks = _re.findall(r"\b[0-9a-f]{32}\b", line)
                if toks and toks[-1][:12] == head:
                    full = toks[-1]
                    break
    if not full:
        raise SystemExit("★台账里捞不到链头的 32 位 md5 (head=%s)" % head)
    prev_full = ""
    import re as _re
    for line in led_text.split("\n"):
        if rel in line and head in line:
            toks = _re.findall(r"\b[0-9a-f]{32}\b", line)
            if toks and toks[-1][:12] == head and len(toks) >= 2:
                prev_full = toks[0]
                break
    iss = (st.get("head_iss") or [None])[0]
    if not iss:
        raise SystemExit("★链头没单号 ⇒ 不许重锚 (fail-closed)")

    old_block = None
    for e in (anchors.get("source_ledger") or {}).get("entries") or []:
        if str(e.get("file") or "") == rel:
            old_block = e
            break
    if old_block is None:
        raise SystemExit("★锚点里没有 %s 的条目" % rel)

    # ★★【修】原来用「逐字段拼字符串」去命中 YAML 块 ⇒ 台账里 `by:` 后面带行内注释时必不命中
    #   ⇒ 改成【正则按字段行定位】(★只改那 5 行的值, 其余字节原样保留★)
    import re as _re
    pat = _re.compile(
        r"(?P<head>^      - file: " + _re.escape(rel) + r"\n)"
        r"(?P<by>^        by: .*\n)"
        r"(?P<prev>^        prev_md5: .*\n)"
        r"(?P<md5>^        md5: .*\n)"
        r"(?P<at>^        landed_at: .*\n)", _re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit("★锚点块原文没命中 (yaml 缩进/字段顺序变了?) ⇒ 不许瞎改")
    new_txt = (m.group("head")
               + "        by: %s\n" % iss
               + "        prev_md5: %s\n" % old_block.get("md5")
               + "        md5: %s\n" % full
               + '        landed_at: "%s"\n' % time.strftime("%Y-%m-%d %H:%M"))
    return text[:m.start()] + new_txt + text[m.end():]


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true",
                   help="★只算不写盘 (★默认档: 不带 --apply 就是 dry-run★)")
    g.add_argument("--apply", action="store_true", help="★真的写盘★")
    ap.add_argument("--reanchor", action="store_true", help="★另外★把 §1 锚点副本前移到台账链头")
    ap.add_argument("--root", default=PROJ)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    tgt = os.path.join(root, TARGET)

    old_text = open(tgt, encoding="utf-8").read()
    old_md5 = md5_of(tgt)
    new_text = apply_edits(old_text)
    if new_text == old_text:
        print("★已是最新 (幂等) ⇒ 不用写盘")
    else:
        print("★待写入 %s" % TARGET)
        print("  修前 md5 = %s" % old_md5)
        print("  修后 md5 = %s" % hashlib.md5(new_text.encode("utf-8")).hexdigest())
        print("  改动行数 = %d" % (len(new_text.split("\n")) - len(old_text.split("\n"))))
        if args.apply:
            bak_dir = os.path.join(root, BAK_DIR_REL)
            os.makedirs(bak_dir, exist_ok=True)
            bak = os.path.join(bak_dir, "timing_check.py.bak_%s" % time.strftime("%Y%m%d-%H%M%S"))
            shutil.copy2(tgt, bak)
            open(tgt, "w", encoding="utf-8").write(new_text)
            print("  ★已写盘 (备份 %s)" % bak)

    if args.reanchor:
        led = os.path.join(root, LEDGER)
        new_led = reanchor_ledger(root)
        if new_led != open(led, encoding="utf-8").read():
            print("★待重锚 §1 锚点副本 (前移到台账链头)")
            if args.apply:
                bak_dir = os.path.join(root, BAK_DIR_REL)
                os.makedirs(bak_dir, exist_ok=True)
                shutil.copy2(led, os.path.join(bak_dir, "SW_MD5_BASELINE_LEDGER.md.bak_%s"
                                              % time.strftime("%Y%m%d-%H%M%S")))
                open(led, "w", encoding="utf-8").write(new_led)
                print("  ★已写盘")
        else:
            print("★锚点副本已在链头 ⇒ 不用重锚")

    if args.apply:
        print("★下一步: python3 SW/tools/timing_check.py   (期望 rc=0)")
    else:
        print("★★这是 dry-run (没写盘) ★★ ⇒ 情形一不许 --apply ⇒ 套用时机 = ISS-283 落 verified 之后")
    return 0


if __name__ == "__main__":
    sys.exit(main())
