#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排单: ISS-136 → hw-lead (排队, 不 spawn) —— 把 check_bq25896 从【假绿】变成【真闸】

★**为什么排而不是现在派**: hw-lead 名额被在飞的 ISS-193 占着 (★铁律: 一个 agent 同时只允许一个写会话★)
   ⇒ ★**排进队列 (owner=hw-lead · status=open) ⇒ 等 ISS-193 交卷后由 advance.py 自动派出**
   ⇒ ★**本轮不 spawn, 所以没有"同一 agent 两条会话"的窗口★

★**为什么这一单值得排 (★main 2026-11-11 19:2x 实测★)**:
   `python3 HW/check_bq25896_pinout.py` ⇒ **rc=1** (失败项 = ⑦ "J_CHG 跨铰链 pin map: 规格 §5.2 提案 == 网表实际",
   ★**不一致 pin7: VBUS_DET vs NC; pin10: TS_RTN vs HINGE_RSV**)
   ⇒ ★**它一直是"绿的假象" (其实 FAIL 但没人跑) ⇒ 门禁链缺它 ⇒ 方法论问题, 不是单个脚本问题★

★**主线口径**: 老板 11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类不派。
   ⇒ ★**本单不改板/不改网表/不改原理图** ⇒ 只是【规格表 + 脚本快照 + 门禁链接线】⇒ 不违反主线口径。
   ⇒ ★**与在飞 ISS-193 零文件交集** (那单只碰 BOM/封装/脚数来源/`HW/PCB/PIN_REALITY_GAP.md`);
   ⇒ ★**与已排队的 ISS-194 也零交集** (那单只碰 `HW/pcb60x30_check.py` + 它的 .json)。

★**due 不动** (本单 due 11-06 已逾期 ⇒ 没改 due 来把 issue_check 违规数洗掉)。
原子写 (flock + 锁内重读 + tmp/os.replace) + 写后逐条比对。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

BRIEF_136 = """\
★**目标**: 把 `HW/check_bq25896_pinout.py` 这个【一直是绿的假象】变成【真闸】——
   ① `HW/CHARGE_BOARD_SPEC.md` §5.2 的 J_CHG 跨铰链 pin map 表 ⇒ 订正到与网表一致
   ② 脚本里硬编的 `spec_proposal` ⇒ 与同一个真源一致
   ③ ★**把该脚本接进 `state/gate_check.py` 的门禁链** (★它现在 rc=1 却没人跑 ⇒ 门禁链缺它★)

★**为什么现在做 (★main 2026-11-11 19:2x 实测, 不是推测★)**
★**实测**: `python3 HW/check_bq25896_pinout.py` ⇒ **rc=1**, 失败项 = ⑦
   "J_CHG 跨铰链 pin map: 规格 §5.2 提案 == 网表实际" ⇒
   ★**不一致: pin7: VBUS_DET vs NC; pin10: TS_RTN vs HINGE_RSV**
⇒ ★**门禁脚本必须进 gate_check 链, 否则等于没有** (★这是方法论问题, 不是单个脚本问题★)

★**你要先自己做的一步 (★不许照抄题单的判定★)**: ★**三方口径自己复算一遍** ——
   ① `HW/CHARGE_BOARD_SPEC.md` §5.2 表里的提案
   ② 脚本里硬编的 `spec_proposal` (自己 grep 出来)
   ③ 网表实际 (`HW/netlist_v1.csv` 里 J_CHG 每一脚)
⇒ ★**写清"哪个是真源、依据是什么"**; ★**默认按题单判定走 (网表为准, 文档与脚本快照是旧的)**,
   ★**但若你实测发现网表那侧另有说法 ⇒ 只报给 main 裁决, 不许自己改网表**。

★**做法**
1. ①② 两处订正到与网表一致 (★**只改这两处, 别的章节一个字不动**)
2. ③ 接进 `state/gate_check.py` ⇒ ★**接进去之后 `python3 state/gate_check.py` 必须仍然 rc=0 且 Q1 18/18**
   ⇒ ★**若接进去会让闸变红 ⇒ 不许接, 只把这件事写进交卷报告报给 main** (★**不许制造一个永久红的闸★**)
3. 反向用例 (★**要能证明它真在读规格/网表★**): ★**在副本上把规格表改回旧口径 ⇒ 该脚本必须变红** (rc≠0) ⇒ 恢复后回 rc=0

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 HW/check_bq25896_pinout.py     # ★**必须 rc=0** (现在 rc=1)
python3 state/gate_check.py            # Q1 必须 18/18 (且 rc=0)
python3 state/merge.py                 # rc 必须 0
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb   # 必须一字未变 (c78f9912… / 611b869e…)
```

★**交卷 ≤ 20 行** (结论先行 + 三方口径复算结果 + 逐条复现命令输出)

★**边界 (不许越)**
· ★**只写**: `HW/CHARGE_BOARD_SPEC.md` (★**只许改 §5.2 那张 pin map 表**) + `HW/check_bq25896_pinout.py`
  + `state/gate_check.py` (★只许加这一项检查★) + `HANDOFF/` 下交卷报告 + ★**必要时** `state/fragments/hw.yaml`
  (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key)。
· ★**不许碰**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` ·
  `HW/PCB/demo_mainboard*.kicad_sch` · `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · **别人的分片** ·
  `state/issue_log.yaml` (★**改 issue 状态是 main 的活★)。
· ★**不许联系供应商/原厂** (外发一律经项目总工)。· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标。
"""


def main() -> int:
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        items = list(doc.get("issues") or [])
        before = {it.get("id"): dict(it) for it in items}

        hit = False
        for it in items:
            if it.get("id") != "ISS-136":
                continue
            hit = True
            it["owner"] = "hw-lead"
            it["verify_by"] = "main"
            it["task_brief"] = BRIEF_136
            it["note"] = (it.get("note") or "") + (
                "\n★**2026-11-11 19:2x 队列自动派活 job 排单**: owner main → **hw-lead** (status 仍 open ⇒ "
                "★**排队, 等 ISS-193 交卷后由 advance.py 自动派出; 本轮不 spawn ⇒ 没有并发写会话窗口★), "
                "verify_by hw-lead → **main** (干活的人不许自签)。"
                "★**为什么排**: hw-lead 名额被在飞 ISS-193 占着 (一个 agent 同时只允许一个写会话)。"
                "★**实测依据**: `python3 HW/check_bq25896_pinout.py` ⇒ rc=1 (失败项 ⑦; "
                "pin7 VBUS_DET vs NC; pin10 TS_RTN vs HINGE_RSV) ⇒ 一直是'绿的假象'。"
                "★**主线口径**: 老板 11-11 10:07 ⇒ PCB 布线/布局类不派; ★**本单不改板/不改网表/不改原理图** ⇒ 不违反。"
                "★**与在飞 ISS-193 / 已排 ISS-194 均零文件交集**。★**due 不动** (due 11-06 已逾期, 没改 due 洗违规数)。"
            )
        if not hit:
            print("❌ 没找到 ISS-136, 放弃写盘")
            return 2

        after = {it.get("id"): it for it in items}
        if len(after) != len(before):
            print("❌ issue 总数变了, 放弃写盘")
            return 2
        diff_other = [k for k, b in before.items() if k != "ISS-136" and after[k] != b]
        if diff_other:
            print("❌ 非目标 issue 发生变化: %s ⇒ 放弃写盘" % diff_other[:5])
            return 2

        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    print("✅ 已原子写 issue_log.yaml:")
    print("   - ISS-136: owner → hw-lead, verify_by → main, task_brief 已写入 (%d 字符), note 已追加" % len(BRIEF_136))
    print("   - status 仍 open (排队) ⇒ 等 ISS-193 交卷后由 advance.py 自动派出")
    print("   - issue 总数 %d (未变) · 其余 issue 逐字段比对: 0 处差异" % len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
