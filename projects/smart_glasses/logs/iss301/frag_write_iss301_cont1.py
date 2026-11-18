#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-301-cont1 分片追加 (hw-lead)
=====================================================================
纪律: 必须走 state/frag_write.py 的原子写 (tmp + fsync + os.replace),
      禁止 open(p,"w")。
本驱动直接 import state/frag_write.py 的 update_fragment(),
      走的是同一个 atomic_write_yaml() ⇒ 与 CLI 完全同一落盘路径。
      只写自己的分片 (hw-lead)。
=====================================================================
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "state"))

from frag_write import update_fragment, load_fragment  # noqa: E402

HANDOFF = "HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md"

NEED_KEY = "iss301_ti_power_facts_counterverify_result"
CLAIM_KEY = "iss301_ti_power_facts_4_claims_verified"

NEED_ITEM_CONT1 = (
    "【ISS-301-cont1 追加 (2026-11-18 05:4x · 网关重载后续做 · 只读复核)】"
    "★四条断言的事实层在 main 落表后【依然全部成立】; 本单三条订正 A/B/C 已被 main 全部追加式执行 "
    "(HW/TI_POWER_FACTS.md 与 HW/POWER_SHUTDOWN_V3.md 均 2026-11-17 23:17:57) ⇒ 零遗留文本错误; "
    "ISS-301/ISS-095/ISS-102 三条均已由 main 落 verified ⇒ 本单闭环 ★ "
    "★唯一还欠的是【订正 B 的网表侧落地】: ① 网表 L62/L65/L67/L71 四条 note 的 PG 极性至今仍写反 "
    "(L62 '任一路不 ok · 本网被上拉拉高' / L65 '两路都好 · PG_AND 低 · Q_AND 关' / L67 '两路 PG 都好时为低' / "
    "L71 'PG 有效 (低)') ⇒ 与 TI TPS62130A Rev.F 官网逐字 'High = VOUT ready' 相反 ★ "
    "② ★★【cont1 新抓到的板级硬证据】板上 Q_AND 的 pad↔net 是 G/D 对调 ★: 自读 HW/PCB/demo_mainboard.kicad_pcb ⇒ "
    "Q_AND (at 107.6,65.5) pad1=RESET_N / pad2=GND / pad3=PG_AND, 而 AO3400A 序是 G-S-D ⇒ 网表要的 G=PG_AND/D=RESET_N "
    "在板上被对调 ⇒ 这颗 MOS 根本不是 AND 门 ★ ⇒ 【★只改 note 文字不改 dnp 是不够的, 反而更误导】★ "
    "⇒ 【建议 Q_AND 整颗改 DNP (表A L65/L66/L67 + 表B Q_AND.1/.2/.3 三行必须同改) + Q_ENVC 三行 L71/L72/L73 同批 DNP】"
    "(★依据 HW/PCB/RESET_P0_FIX_PLAN.md 改法② + state/RECHAIN_ONEPASS_PLAN.md §1 行 C★) ⇒ 【零新增件 · 零新增板改项 · "
    "互锁实际损失 0 (两颗 DC-DC 本就 DNP ⇒ 它们的 PG 脚不在板上 ⇒ 这条互锁从来只按住不放行)】★ "
    "★该口径已写成交卷单 §C2 的可抄句, 请并进 RECHAIN §1 行 C 与 §3-S6 前置 (B10_Q_AND_LAND 那 3 根线本趟本来就要重画 ⇒ 不额外占趟)★ "
    "★板侧影响一句话: S6 清单【零变化】—— R_VBUS_DET_D1 / R_VBUS_DET_D2 / C_DET_VBUS_D 三件留·不动 (实测网表 L434~L438 全【必装】+ "
    "板上三颗封装都在 + 作业包零命中这三个位号 ⇒ 它们不在 S6 清单里)★ "
    "★三件真源 md5 变化 (网表 37f62ac3→6aee500e / 脚表 a4270120→9174309d / BOM 5d02bece→5b999399, mtime 2026-11-18 00:21:08) "
    "= main 的 ISS-302 落表, 不是本单写的; 板 md5 611b869e… + mtime 2026-11-06 07:07:17 逐字节不变 ⇒ 本单零写板零落表★★"
)

CLAIM_VALUE_CONT1 = (
    "★ISS-301-cont1 (2026-11-18 05:4x 只读复核) 增量读数★: "
    "① 四条断言的事实层在 main 落表后【依然全部成立】(C_SYS 现为必装 + BOM 已加 20µF; AON 仍 0 命中; 两颗 VBUS detect 球 "
    "SoC+SoM 侧均成立; TPS62130A PG 三条官网逐字成立) ★ "
    "② 本单三条订正 A/B/C 已被 main 全部追加式执行 ⇒ 【零遗留文本错误】 ★ "
    "③ ★★新增板级硬证据 [实测]: 板上 Q_AND 的 pad↔net 与网表意图【G/D 对调】(板 pad1=RESET_N / pad2=GND / pad3=PG_AND, "
    "AO3400A 序 G-S-D) ⇒ 与作业包 §3-S6 L144 B10_Q_AND_LAND 逐字一致 ⇒ 该板改项本就在 S6 清单里 ⇒ 【零新增板改项】★ "
    "⇒ 【订正 B 的正确落法 = Q_AND 整颗改 DNP + Q_ENVC 三行同批 DNP + L62/L65/L67/L71 四条 note 追加式改对】; "
    "只改 note 不改 dnp 不够 ★ "
    "④ 板侧影响: 【S6 清单零变化, 三件 VBUS_DET 分压件留·不动】 ★ "
    "⑤ 闸读数 (2026-11-18 05:4x 实跑): merge rc=0 · gate_check rc=0 (Q1 18/18 · 钉板 md5 闸链 9/9 绿 · Q6 通过) · "
    "issue_check rc=0 · check_netlist_selfconsistency rc=1 (★既有 R3/R4/R9 未落表, 属本单范围外; 未改判据★) · "
    "板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17 ⇒ 【零写板双自证】★ "
    "⑥ 边界 (cont1): 零写板 · 零落表 · 零改真源 · 零改闸 · 不自签 issue_log · 零外发 · 实物[实测]=0 条"
)

ARTIFACT_SUMMARY_CONT1 = (
    "★ISS-301-cont1 (2026-11-18 05:4x) 追加节 C1~C6 已落: ① main 落表后的现状增量与 md5 归因 ② 【★新抓到】板上 Q_AND 的 "
    "G/D 对调 (自读板文件, 非抄作业包) ③ 四问的落表后版本答案 ④ 2026-11-18 05:4x 现场 rc 原样 (含受保护 5 件 md5 + 板 mtime) "
    "⑤ cont1 边界自证 ⑥ 一句话收口 ⇒ ★【本文件 50,179 B → 70,229 B, 老字一字未删】★ · "
    "日志: logs/iss301/b3_rerun_greps_20261118_0540.log / b3_rerun_md5_20261118_0540.log / "
    "b3_rerun_netcheck_20261118_0540.log / b3_rerun_gates_20261118_0545.log"
)


def main() -> int:
    d = load_fragment("hw-lead")
    needs = d.setdefault("needs_from", [])
    claims = d.setdefault("interface_claims", [])
    arts = d.setdefault("artifacts", [])

    # needs_from: 同 key 已存在 ⇒ 追加式改写 item (老字留痕) 而不是再插一条同 key
    hit = None
    for n in needs:
        if isinstance(n, dict) and n.get("key") == NEED_KEY:
            hit = n
            break
    if hit is None:
        needs.append({"key": NEED_KEY, "to": "main", "item": NEED_ITEM_CONT1, "since": "2026-11-18"})
        print("[iss301-cont1] needs_from: 新增 1 条")
    else:
        old = str(hit.get("item") or "")
        if "ISS-301-cont1 追加" not in old:
            hit["item"] = old + " || " + NEED_ITEM_CONT1
            print("[iss301-cont1] needs_from: 追加式改写 (老字留痕)")
        else:
            print("[iss301-cont1] needs_from: 已是最新, 不动")

    chit = None
    for c in claims:
        if isinstance(c, dict) and c.get("key") == CLAIM_KEY:
            chit = c
            break
    if chit is None:
        claims.append({"key": CLAIM_KEY, "value": CLAIM_VALUE_CONT1,
                        "note": "实测: 2026-11-18 05:4x 本机实跑 (只读复核)",
                        "ref": HANDOFF + "#C1"})
        print("[iss301-cont1] interface_claims: 新增 1 条")
    else:
        old = str(chit.get("value") or "")
        if "ISS-301-cont1" not in old:
            chit["value"] = old + " || " + CLAIM_VALUE_CONT1
            print("[iss301-cont1] interface_claims: 追加式改写 (老字留痕)")
        else:
            print("[iss301-cont1] interface_claims: 已是最新, 不动")

    ahit = None
    for a in arts:
        if isinstance(a, dict) and a.get("path") == HANDOFF:
            ahit = a
            break
    if ahit is None:
        arts.append({"path": HANDOFF, "summary": ARTIFACT_SUMMARY_CONT1})
        print("[iss301-cont1] artifacts: 新增 1 条")
    else:
        old = str(ahit.get("summary") or "")
        if "ISS-301-cont1" not in old:
            ahit["summary"] = old + " || " + ARTIFACT_SUMMARY_CONT1
            print("[iss301-cont1] artifacts: 追加式改写 (老字留痕)")
        else:
            print("[iss301-cont1] artifacts: 已是最新, 不动")

    update_fragment("hw-lead", lambda _d: None)
    print("[iss301-cont1] ✅ 分片已原子写 (state/frag_write.py::update_fragment)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
