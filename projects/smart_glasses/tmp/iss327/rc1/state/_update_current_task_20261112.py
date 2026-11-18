#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CURRENT_TASK.md 状态行订正 (2026-11-12 00:4x) —— main (项目总工) 执行
================================================================================
★**为什么本轮要改它**: `state/CURRENT_TASK.md` 的 L2 是"当前状态"长行, L3~L8 是老板待办清单
   ⇒ ★**老板每天翻的就是这个文件** ⇒ ★**里面躺着两处【已经过期的事实】= 给老板看假账** ★★:

   ★**① L3「批不批那封问原厂的信 … 回一句"可以发"即可」**
      ⇒ ★**已于 2026-11-11 19:31 被老板的政策直接覆盖** (「以后不再做任何邮件咨询」)
      ⇒ ⇒ ★**它现在不是"等你回一句", 是"按政策不发"** ⇒ 继续挂在那儿 = 老板以为还有一封信等他批 ★★

   ★**② L7「在飞: ISS-193 → hw-lead · ISS-192 → mech-lead」**
      ⇒ ★**这两条都已交卷并经 main 独立验收签字 (ISS-193 verified/pass · ISS-198 verified/pass)**
      ⇒ ⇒ ★**此刻真正在飞的是 ISS-136 → hw-lead** (★兄弟 job「ARS45 队列自动派活」23:5x 派出★
      ⇒ ⇒ ★**会话 `824ac5a1` status=running★**) ⇒ ⇒ ★**这正是 A 段本轮为空的原因** ⇒ ★**L7 不改 = 老板看不懂为什么没派活** ★★

★**本脚本做的三件事 (★全是【订正过期事实】, 不新增任何待办, 不替老板决定★)**:
   ① L2 末尾追加本轮 (11-12 00:2x) 的事实段
   ② L3 标「19:31 已按政策退休 (不发)」
   ③ L7 改成当刻真实在飞 (ISS-136 → hw-lead) + 注明 ISS-193/198 已闭环

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir)) + 逐行 diff 自证
★**边界**: 不改 `PROJECT_TRACKER.md` (★尤其 §0 锁死表★) · 不发邮件 · 不写任何子总工的分片 · 不动 L1/L9/L10
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
P = os.path.join(HERE, "CURRENT_TASK.md")
LOCK = os.path.join(HERE, ".current_task.lock")

APPEND = (
    " ⇒ ★★★**★【11-12 00:2x 后继计划轮 · A 段仍为空 (★**真在飞: ISS-136 占住 hw-lead 名额★**) "
    "+ ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** ⇒ ★**本轮你不用做任何新决定** ★★★**★**"
    "★★**【A 段 0 条 · 根因是【真在飞】不是死单占位】★★** ⇒ ★**实测 `advance.py --json` 的 `internal` = **0 条** "
    "(`approvals` 0 / `decisions` 36 / `waiting` 0) ⇒ ★**根因: 兄弟 job「ARS45 队列自动派活」23:5x 派出 "
    "**ISS-136 → hw-lead** (★J_CHG 跨铰链 pin map 订正 + 接进 gate_check 门禁链★) ⇒ ★**会话 "
    "`agent:hw-lead:subagent:f8ab912e` (sessionId `824ac5a1`) 本轮实测 status=**running** (★起于 00:18, 已跑 6 分钟+★)** "
    "⇒ ⇒ ★**`issue_log.yaml` 里 ISS-136 = `fixing` ⇒ `advance.py` 的 in_flight 判据正确挡住 hw-lead** ⇒ ⇒ "
    "★**⇒ ISS-195 (hw-lead 名下唯一 open, 麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算, due 11-13) 本轮不派** "
    "(★**铁律: 一个 agent 同时只允许一个写会话★**) ⇒ ★**⇒ sw-lead / mech-lead 名下 open = 0** (★**实测 open/fixing 的 owner 分布 = "
    "boss **5** · main **19** · hw-lead **2**★**) ⇒ ⇒ ★**⇒ A 段空是【真空 + 一个正在跑】, 不是【队列全是死单】** ⇒ "
    "⇒ ★**本 job 不新开单、不硬塞** (★**两边同时派同一个 agent 会撞铁律★**) ★★ "
    "★★**【本轮按【原理图主线】跳过了哪几条 PCB 类】★★** ⇒ ★**跳过 0 条** (★**三个总工的 open 队列里根本没有 PCB 布线/布局类单: "
    "ISS-136 = 规格/网表/门禁侧, ISS-195 = 机械孔位净空复算, 两条都不是 PCB 布线★**) ⇒ ★**⇒ 而 owner=main/boss 的 PCB 类 open 单 —— "
    "ISS-122 (BGA 逃线层数) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-160 (demo 板图纸链) · "
    "ISS-169 (demo 板可制造性) · ISS-060 (产品件三条几何) —— ★**本轮继续压着不派 (★老板 2026-11-11 10:07 口径: "
    "先解决原理图绘制, 再解决 PCB 绘制★)**, 也没藏账 (★**它们仍列在 G4 未闭环清单里, 且 stage_gate rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★★ "
    "★★**【B 段 approvals = 0 ⇒ 草稿一件没少, 一封都没发】★★** ⇒ ★**`state/outbox/` 实测 **19 份 .md** "
    "(16 份草稿 + README + 政策件 `NO_OUTBOUND_POLICY.md` + 内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` **3 份** "
    "⇒ ★**零缺失** ⇒ ★**按 19:31 政策【一律不发, 只留档】** ★★ "
    "★★**【C 段 36 项 ⇒ 今日实数】★★** ⇒ ★**与 11-11 r24a 页 **36/36 完全对齐 (0 新增 / 0 退休 / 0 改建议值)** ⇒ "
    "★**⇒ 新开当天拍板页 `DECISION_PENDING_2026-11-12.md`** (★**§1~§8 的 36 条建议默认值逐字沿用 11-11 原文★**) ⇒ "
    "★**⇒ 本轮只订正了每张表的「逾期」列 (34 格) + 页尾逾期分布表 (36 项 / 已逾期 33 / 剩 0 天 1 / 无 due 2) + §8 那句陈旧的「其余 38 项」→ 33** ⇒ "
    "★**⇒ 建议默认值列逐条比对: 39 条全同, **0 条不同** (★**一个字的建议值都没改**★) ★★ "
    "★★**【核验 5 连本轮实测 rc】★★** ⇒ ★**merge **0** (冲突 0 · 产出 175 · 阻塞 43 · 未闭合需求 101) · "
    "gate_check **0** (★**齐备率 18/18** ★ · 证据分级 3/3 · 接口声明 489) · issue_check **1** (违规 **30** 条, 全是逾期类) · "
    "stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0) · daily_check **3** (巡检异常已记录, 非崩溃: 问题闭环门 30 条) ★** "
    "⇒ ★**另复跑原理图侧尺子: ERC **0** 条 · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) ⇒ 原理图侧机器可查部分仍全绿** ★★ "
    "★★**【板面零变化】★★** ⇒ ★**板 `611b869e` · 网表 `c78f9912` · 脚表 `4814617e` · `.kicad_pro` `3e504d2b` **一字未动** ★★ "
    "★★**【GitHub: 本 job 不推】★★** (★**统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ⇒ ★**本地快照已落 `PROGRESS_SNAPSHOT.md` (00:40)** ★★ "
    "★★**【下一步】★★** ⇒ ★**等 ISS-136 交卷 → main 独立验收签字 → hw-lead 名额释放 → A 段恢复可派 (ISS-195 优先)** ⇒ "
    "★**另: P2 原理图设计评审 仍等你翻 PDF + `REVIEW_CHECKLIST_P2.md` + `PIN_REALITY_GAP.md`; 整链重出第 1 步 等 ISS-198 交卷验完就启动** ★★"
)

L3_NEW = (
    "① ⛔ ★**【已退休: 按你 2026-11-11 19:31「以后不再做任何邮件咨询」政策 ⇒ 这封信【不发】, 只留档】** ★ "
    "(★草稿 `state/outbox/som_balltable_inquiry.md` 仍在 (16:59 就绪 · **未发送**) · 问①完整 4 座×100 球位表+电源地接法+可悬空清单+PG/RESET_N 时序 · "
    "问②P2 座恰好缺 num=40 二选一确认★) ⇒ ★**不必回「可以发」了 —— 那条路已经关闭** ⇒ ★**替代动作 = 自己网上查 (★政策件 "
    "`state/outbox/NO_OUTBOUND_POLICY.md` 已列「要自己查的清单」★) ⇒ ★**其中 29 个器件真实脚数那半已经内部做完 (ISS-198: [0数据] 29 → 3, 3 个全是非器件)****★"
)

L7_NEW = (
    "⑤ ★**在飞 (此刻只有一条 ⇒ A 段本轮为空)**: **ISS-136 → hw-lead** (★J_CHG 跨铰链 pin map 订正 + 接进 gate_check 门禁链 · "
    "★兄弟 job「ARS45 队列自动派活」23:5x 派出 · 会话 `824ac5a1` 00:18 起 · **本轮实测 status=running**★) ⇒ ★**⇒ hw-lead 名额被占 ⇒ "
    "ISS-195 (麦 M1→S1 孔壁净空按套A 重算 · due 11-13) 本轮不派 (★**铁律: 一个 agent 同时只允许一个写会话★**) ⇒ sw-lead / mech-lead 名下 open = 0** ⇒ "
    "★**⇒ ISS-193 (BOM 口径) 与 ISS-198 (三张查找表补全, [0数据] 29→3) 均已交卷并经 main 独立验收签字 verified/pass ⇒ 不在飞了** ⇒ "
    "★**⇒ 交卷后由 main 独立验收签字, 本 job 不插手** ★★"
)


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".ct.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    if not os.path.exists(P):
        print("❌ 找不到 %s" % P)
        return 2
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        old = open(P, encoding="utf-8").read()
        lines = old.split("\n")

        # ① L2 追加本轮 (幂等: 已有标记就不重复追加)
        if "【11-12 00:2x 后继计划轮" not in lines[1]:
            lines[1] = lines[1] + APPEND
        else:
            print("ℹ️ L2 本轮段已存在 ⇒ 不重复追加")

        # ② L3 换新 (幂等: 以 "① ⛔" 开头就跳过)
        if not lines[2].startswith("① ⛔"):
            if not lines[2].startswith("① "):
                print("❌ L3 不是以「① 」开头 ⇒ 结构变了 ⇒ 停手")
                return 2
            lines[2] = L3_NEW

        # ③ L7 换新 (幂等: 含 ISS-136 就跳过)
        if "ISS-136 → hw-lead" not in lines[6]:
            if not lines[6].startswith("⑤ "):
                print("❌ L7 不是以「⑤ 」开头 ⇒ 结构变了 ⇒ 停手")
                return 2
            lines[6] = L7_NEW

        new = "\n".join(lines)
        if new == old:
            print("ℹ️ 无变化")
            return 0
        atomic_write(P, new)

        # 自证: 只有 L2/L3/L7 变了, L1/L4/L5/L6/L8/L9/L10 逐字节相同
        ol = old.split("\n"); nl = new.split("\n")
        changed = [i + 1 for i in range(min(len(ol), len(nl))) if ol[i] != nl[i]]
        print("✅ 已写 CURRENT_TASK.md · 变动行 = %s (期望 [2, 3, 7])" % changed)
        if changed != [2, 3, 7]:
            print("❌ 变动行不符预期 ⇒ 请人工查")
            return 1
        print("   行数 %d → %d" % (len(ol), len(nl)))
        print("   L2 长度 %d → %d" % (len(ol[1]), len(nl[1])))
        return 0
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()


if __name__ == "__main__":
    sys.exit(main())
