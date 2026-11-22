#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r73 · 2026-11-18 16:10 · 追加 §L-5 (追加式 · 只加本轮机器复核到的一条事实)"""
import hashlib, io
P = "DECISION_INDEX_2026-11-18.md"
before = open(P, encoding="utf-8").read()
bl = before.split("\n")
SEC = """
### ★L-5 · ★★【本轮追加的一条【事实】(★机器复核到★)】Q1 在本轮窗口内自己从 11/18 涨到 14/18 ⇒ ★§L-4 的「未完工不是质量回退」被证实★★★

- ★**15:54 本轮首次 `gate_check.py` 实跑**: Q1 = **11/18** (★hw 3/6 缺 B2/B4/B5 · sw 6/6 · mech 2/6 缺 B2/B3/B4/B5★) · 缺口清单 11 条 · rc=0
- ★**16:07 同一条命令复跑** (★追加 §L 之后 / 本 job 只写了决策页 + 一份 round log, 没碰任何交接单★): Q1 = ★**14/18** ★ · ★**hw-lead 6/6 缺: 无** ★ (★交接单已换成 `2026-11-18_z_hw-lead_ISS308_S8可达性判决书_门禁索引.md`★) · sw-lead 6/6 · ★**mech-lead 仍 2/6** ★ (★缺 B2/B3/B4/B5★) · 缺口清单 **8** 条 · rc=0
- ⇒ ★**实测: 涨上去的是【hw-lead 那 3 块】⇒ 正好对应 ISS-325 的交卷页在窗口内被填完 (★兄弟 job fb67af40 的会话在跑★) ⇒ ★**Q1 的波动源 = 【交卷页在写/已写完】, 不是【质量塌方】★** ★
- ⇒ ★**剩下的唯一交卷页缺口 = mech-lead 的 ISS-326 (B2/B3/B4/B5) ⇒ 那个 agent 16:0x 仍在跑最终核验 (★status=running★) ⇒ ★**[推算]** 它收尾后 Q1 会补到 16/18 (★Q2 证据分级也会从 2/3 补到 3/3★)** ★
- ★**本 job 纪律复核 (★16:07 复跑 rc 全绿★)**: `gate_check.py` rc=0 · `issue_check.py` rc=0 · `check_report_placeholders.py` rc=0 (★✔ 无占位符·可发★) ⇒ ★**本轮追加的 §L 文字没有把任何门禁带红** ★
"""
after = before + SEC
io.open(P, "w", encoding="utf-8").write(after)
now = open(P, encoding="utf-8").read()
assert now.split("\n")[:len(bl)] == bl, "★老字被改了★"
assert now.startswith(before)
print("✅ 老字逐字未改校验通过 (前 %d 行原样, 追加 %d 行)" % (len(bl), len(now.split("\n")) - len(bl)))
print("   after md5 =", hashlib.md5(now.encode("utf-8")).hexdigest())
