#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CURRENT_TASK.md 追加本轮 (2026-11-12 01:4x ~ 01:5x) 后继计划轮记账 —— main (项目总工)
================================================================================
★**为什么写**: `state/CURRENT_TASK.md` 是【状态速报 / 5 分钟播报 / status.sh】的唯一播报源
   ⇒ 本轮的事实必须落进去 ⇒ 否则播报会读着上一轮的旧口径 (★**11-11 23:xx 那次就栽过:
   播报说「A 段为空 = 没活」, 实际是「在飞」★**)

★**本脚本只做 1 件事**: 在 CURRENT_TASK.md 的 ★**第 1 行末尾**(★**"当前在做"那一行★**)
   追加一段本轮记账 ⇒ ★**不重写整个文件, 不删历史, 不动 §0 锁死表** ★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 issue_log · 不改任何分片 · 不改 PROJECT_TRACKER §0 · 不发邮件 · 不推 GitHub
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TASK = os.path.join(HERE, "CURRENT_TASK.md")
LOCK = os.path.join(HERE, ".current_task.lock")

MARK = "★【11-12 01:4x 后继计划轮】"

APPEND = (
    MARK
    + " ★**A 段本 job 派 0 条 (★**不是没活, 是【兄弟 job「ARS45 队列自动派活」已把两个名额占满】★**)**"
    + " ⇒ ★**实测 `advance.py --json` = `internal: []` · `approvals: []` · `decisions: 36` · `waiting: []`**"
    + " ⇒ ★**根因: 兄弟 job 01:4x 派了 ISS-195→hw-lead (会话 `dc510f7c`) + ISS-200→mech-lead (会话 `0ef5e479`), 两个都 status=running**"
    + " ⇒ ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本 job 不重复派** ★"
    + " ⇒ ★**本轮实际在飞 3 条**: ★**① ISS-195 (hw-lead) 麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算 (due 11-13)** ★"
    + "**② ISS-200 (mech-lead) 结构侧 J_CHG pin map 旧口径收敛 (due 11-13)** ★"
    + "**③ ISS-199 (hw-lead) HW 侧 J_CHG pin map 剩 4 处第二口径 (due 11-14, ★**排队中 = 等 ISS-195 交卷释放名额★**)**"
    + " ⇒ ★**这 3 条都不是 PCB 布线/布局类 (★**机械孔位净空复算 / 文档 pin map 口径 / 结构 pin map 口径★**) ⇒ ★**按原理图主线口径【跳过 0 条 PCB 类】** ★"
    + " ⇒ ★**⇒ 而 owner=main/boss 的 PCB / 几何类 open 单 6 条继续压着不派**: ISS-122 (BGA 逃线层数) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-160 (demo 板图纸链) · ISS-169 (demo 板可制造性) · ISS-060 (产品件三条几何)"
    + " ⇒ ★**没藏账 (★**仍在 G4 未闭环清单里 · stage_gate rc=1 / G1 仍开 ⇒ 不许投板没松★**) ★"
    + " ⇒ ★★★**★【ISS-136 (hw-lead) 本轮收口 = main 验收签字 (★**独立复核, 不采信自述★**)】**★"
    + " ★**兄弟 job 已落 `verified` / `verify_result=pass` / `verify_by=main`** ⇒ ★**我自己又跑了一遍** ★★: "
    + "`HW/check_bq25896_pinout.py` ⇒ **rc=0** (PASS **11** / FAIL **0**) · `state/gate_check.py` ⇒ **rc=0** (★**Q1 18/18** ★ + ★**【Q6 硬件真源闸】✅ 通过 (rc=0)★ ⇒ 证明它真在门禁链里跑, 不是装饰★**) "
    + "· ★**反向用例 (★**它真在读规格的证据★**)**: 副本上把 §5.2 pin7 改回 `PWR_GOOD` ⇒ **rc=1 且只有 ⑦ 一项 FAIL** (其余 10 项仍 PASS ⇒ 精确定位漂移点) ⇒ 恢复 ⇒ **rc=0** "
    + "⇒ ★**「规格漂移 = 闸红」这条机制是真的 (★**旧检查项 ⑦ 比的是「脚本硬编快照 vs 网表」, 规格表根本不在判定里 ⇒ 换掉规格内容结论一字不变 ⇒ 一直是「绿的假象」★**) ★"
    + "⇒ ★**§5.2 pin map 已逐脚对拍网表**: pin1/2=BAT_CHG · pin3/4=GND · pin5=CHG_STAT · pin6=PWR_GOOD · **pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV** ⇒ ★**「网表是唯一真源, 文档是它的镜像」这条口径已落地** ★"
    + "⇒ ★**残留已另开单**: HW 侧 4 处 ⇒ **ISS-199** · 结构侧 2 处 ⇒ **ISS-200** ⇒ ★**hw-lead 按纪律没代改别人地界 (★**结构侧那处登记成 need 转给我★**)** ★"
    + " ⇒ ★★★**★【核验 5 连 本轮实测 rc】★★** ⇒ ★**merge 0 (冲突 0 · 产出 177 · 阻塞 43 · 未闭合需求 102)** · "
    + "★**gate_check 0 (★**Q1 18/18** ★ + ★**Q6 硬件真源闸 ✅**★)** · ★**issue_check 1 (违规 **29** 条 · ★**比上轮 30 少 1 = ISS-136 关掉一条, 没新造违规·全是逾期类★**)** · "
    + "★**stage_gate 1 (当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0)** · ★**daily_check 3 (巡检异常已记录, 非崩溃: 问题闭环门 29 条 · 内部未闭合 100→102 · 问题单 194→196)** ★"
    + " ⇒ ★★★**★【B 段 approvals = 0 (★**老板 2026-11-11 19:31「一律不发」政策后恒为空★**) ⇒ 草稿一件没少, 一封都没发** ★**: "
    + "`state/outbox/` 实测 **19 份 .md** (16 草稿 + README + 政策件 `NO_OUTBOUND_POLICY.md` + 内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` **3 份** ⇒ ★**零缺失** ★"
    + " ⇒ ★★★**★【C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议默认值) ⇒ 本轮你不用做任何新决定】★★** ⇒ ★**决策页 `DECISION_PENDING_2026-11-12.md` 已刷第 2 次 (§0.27) ⇒ 36 条的「逾期」列逐条核对 = 0 条不一致, 建议默认值一个没动** ★"
    + " ⇒ ★**板 / 网表 / 脚表 / .kicad_pro md5 一字未动 (611b869e / c78f9912 / 4814617e / 3e504d2b)** ⇒ ★**本 job 没碰任何生产文件** ★"
    + " ⇒ ★**GitHub: 本 job 不推 (★**统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ⇒ 上次推送 2026-11-12T00:26:07** ★"
    + " ⇒ ★**本地快照已落 `PROGRESS_SNAPSHOT.md` (01:52)** ★"
    + " ⇒ ★**下一步**: 等 ISS-195 (hw-lead) / ISS-200 (mech-lead) 交卷 → main 独立验收签字 → hw-lead 名额释放 → ★**ISS-199 自动可派** ⇒ ★**另: P2 原理图设计评审 仍等你翻 PDF + `HW/PCB/REVIEW_CHECKLIST_P2.md` + `HW/PCB/PIN_REALITY_GAP.md`; 整链重出第 1 步 等 ISS-198 验完启动 (★**ISS-198 已 verified·可启动**★)** ★★"
)


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(TASK, encoding="utf-8").read()

        if MARK in raw:
            print("ℹ️ 本轮记账已在 CURRENT_TASK.md ⇒ 幂等, 不重复写 (rc=0)")
            return 0

        lines = raw.splitlines(keepends=True)
        if not lines:
            print("❌ CURRENT_TASK.md 是空的 ⇒ 拒绝写")
            return 2

        # ★**只改第 1 行 (★**"当前在做"那一行★**) ⇒ 第 2 行起一字不动
        lines[0] = lines[0].rstrip("\n") + APPEND + "\n"
        out = "".join(lines)

        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(TASK), prefix=".CURRENT_TASK.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(out)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, TASK)
            dfd = os.open(os.path.dirname(TASK), os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    print(f"✅ CURRENT_TASK.md 已原子落盘: {TASK}")
    print(f"   第 1 行末尾 +{len(APPEND)} 字符 (本轮记账)")
    print("   第 2 行起 一字未动 (★当前在做 + 待办清单 + 权威件索引 全部保留★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
