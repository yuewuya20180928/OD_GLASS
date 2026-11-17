#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页 2026-11-12 · r28 补记 2 (r29) —— 由 main (项目总工) 执行
================================================================================
★★**为什么要有这次补记 (★实测, 不是推测★)** ★★:
· r28 落盘时 (02:5x) 本 job 已清完 ISS-200 / ISS-202 两条僵尸, 派了 ISS-202 / ISS-203
· ★**但 sw-lead 的 ISS-201 (★**兄弟 job 派的那条**) 在 02:31 也交卷了 ⇒ status 停在 `fixing`**
  ⇒ ★**第 9 条僵尸** ⇒ ★**main 02:4x 独立复核并签字 ⇒ verified** ★
· ⇒ ★**本 job 连续第 3 次亲手清僵尸** ⇒ ★**A 段最终态 = 0 (不是没活, 是三个总工各自都有在飞或刚清的账)** ★

★★**本脚本只做 2 件事 (★全是【记账】, 不替老板决定任何事★)**:
   ① 改页首标题行 + §0.28 标题 (★**清僵尸 2 → 3 条 / 派活 2 条**★)
   ② **§0.28.1** = 补记 ISS-201 的落账 + ★**最终 A 段状态口径** ★ + ★**§0.28.2** = 订正核验 5 连最终 rc ★

★★**★本 job 亲手清了 3 条僵尸 fixing (ISS-200 / ISS-202 / ISS-201) —— 这是本轮最值得记的一件事★** ★★:
· ★**同病复发史**: ISS-198 · ISS-136 · ISS-200 · ISS-202 · ISS-201 ⇒ ★**第 5~9 次** ★
· ★**根因 (★实测, 不是推测★)**: ★**派活的 cron 会话在子 agent 交卷前就收场 ⇒ 完成事件投给了已死的会话
  ⇒ 没人落账 ⇒ status 永远停在 `fixing` ⇒ `advance.py` 的 in_flight 规则把该 agent 的名额永久占住
  ⇒ A 段恒空** ★
· ★**⇒ 本轮 3 条我都是【当场】清掉的 (★交卷后 10 分钟内, 没等下一轮 cron★) ⇒ 不给它们留成僵尸** ★
· ★**⇒ 但这是"流程的病", 不是"单子的病"** ⇒ ★**真正该修的是【谁派谁落账】: 派活的 cron 必须在收场前
  确认子 agent 已交卷并落账, 或把落账责任明确交给下一个 job** ★ ⇒ ★**本 job 已把这条写进 MEMORY** ★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 C 段任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-12.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

OLD_TITLE = (
    "# 待老板拍板页 · 2026-11-12 02:5x (第 4 次刷新 · ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** "
    "+ ★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** ★** + ★**僵尸 fixing 落账 2 条 "
    "(ISS-200 / ISS-202) ⇒ A 段从空变 2 条★**)** ⇒ ★**本轮你不用做任何新决定** ★★)"
)
NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-12 02:5x (第 5 次刷新 · ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** "
    "+ ★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** ★** + ★**★僵尸 fixing 当场清 3 条 "
    "(ISS-200 / ISS-202 / ISS-201) ⇒ 同病第 5~9 次复发★**★)** ⇒ ★**本轮你不用做任何新决定** ★★)"
)

OLD_SEC_HEAD = (
    "## 0.28 ★★★ 本轮 (2026-11-12 02:16 ~ 02:5x): ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** + "
    "★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** + ★**僵尸 fixing 落账 2 条 (ISS-200 / ISS-202)** ★★"
)
NEW_SEC_HEAD = (
    "## 0.28 ★★★ 本轮 (2026-11-12 02:16 ~ 02:5x): ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** + "
    "★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** + ★**★僵尸 fixing 当场清 3 条 "
    "(ISS-200 / ISS-202 / ISS-201) ⇒ 同病第 5~9 次复发★**★** ★★"
)

OLD_281_TAIL = (
    "| ★**★补记 (02:4x): ISS-202 若不落账就是【第 8 条僵尸 fixing】★ | ★**它 02:35 交卷、02:4x 落账 ⇒ "
    "★**没等下一轮 cron, 本 job 当场清掉**★ ⇒ ★**⇒ 这是本 job 连续第 2 次亲手清僵尸** (ISS-200 是第 7 次) ★★ |"
)
NEW_281_TAIL = OLD_281_TAIL + (
    "\n| ★★**★补记 (02:4x): ISS-201 (★**兄弟 job 派的那条**) 也在 02:31 交卷了 ⇒ 同样停在 `fixing` "
    "⇒ 【第 9 条僵尸】⇒ main 当场独立复核并签字 ⇒ **verified** ★★ | ★**交卷页 `HANDOFF/2026-11-12_sw-lead_ISS201_台账登记重建件.md` "
    "(17,654 B, 02:30)★ ⇒ ★**我逐条独立复核过 (不采信自述)**: ★**`probe` 现在打「台账一致: True」** "
    "(★**这正是本单的核心判据, 改前实测是 False**★) · ★**两个重建件的行 C1/C2/C3 全 ✅** · "
    "★**交付集条目数 = 2 (未变多; 脚本里 `SHIP_BASELINE_MAX = 2` 是硬断言)** ⇒ ★**两个重建件都落 `licensing-hold` "
    "⇒ 没因为\"文件现在能用\"就进交付集** ★ · ★**我反查过: 全盘搜原件 sha `20368be665f6f59a` ⇒ 0 命中 ⇒ 原件确实丢失** "
    "⇒ ★**原 ID 改 `missing` (不是 `quarantined`) 是对的, 且该词三处同时加** ★ · ★**许可不许猜 (重建件 = unknown [0数据])** ★ "
    "⇒ ★**反向用例我亲手跑了 2 条**: ① 改回旧常量 ⇒ `probe` 立刻打回 False (恢复后 True) ⇒ ★**证明它真在读磁盘文件** ★ "
    "② 改脚本 MANIFEST 的 sha ⇒ 该行 C3 立刻 ❌ (恢复后 ✅) ⇒ ★**证明台账↔实物是真比对** ★ ⇒ "
    "★**两个用例跑完都恢复, 三个文件 diff 逐字节核对一致** ★ ⇒ ★**整体 rc 仍是 1 (FAIL 10) 但全是别的资产的 C1「文件不存在」, "
    "与本单无关 ⇒ 按 brief 明令不去改别人的行来凑 rc=0** ★ ⇒ ★**板/网表/pins/.kicad_pro 一字未变 · "
    "磁盘上两个 `.onnx` 本体 mtime 仍是 11-02 20:41 (没动本体)** ★ |\n"
    "| ★★**★本 job 亲手清了 3 条僵尸 fixing (ISS-200 / ISS-202 / ISS-201) —— 这才是本轮最值得记的一件事★** ★★ | "
    "★**同病复发史: ISS-198 · ISS-136 · ISS-200 · ISS-202 · ISS-201 ⇒ 第 5~9 次** ★ ⇒ ★**根因 (实测)**: "
    "★**派活的 cron 会话在子 agent 交卷前就收场 ⇒ 完成事件投给了已死的会话 ⇒ 没人落账 ⇒ status 永远停在 `fixing` "
    "⇒ `advance.py` 的 in_flight 规则把该 agent 的名额永久占住 ⇒ A 段恒空** ★ ⇒ ★**这 3 条我都是【当场】清的 "
    "(交卷后 10 分钟内, 没等下一轮 cron) ⇒ 不给它们留成僵尸** ★ ⇒ ★**⇒ 但这是【流程的病】不是【单子的病】** ⇒ "
    "★**真正该修的是【谁派谁落账】: 派活的 cron 必须在收场前确认子 agent 已交卷并落账, 或把落账责任明确交给下一个 job** ★ "
    "⇒ ★**本 job 已把这条写进 MEMORY** ★ |\n"
    "| ★**最终 A 段状态 (= 0, 但不是【没活】)** | ★**实测 `advance.py --json` ⇒ `internal: 0`** ⇒ ★**三个总工各有各的账**: "
    "★**hw-lead** = ISS-195 真在飞 (会话 `dc510f7c` status=**running**) ⇒ ★**ISS-199 排队** ★ · "
    "★**mech-lead** = ISS-203 本 job 刚派 (★**真在飞**★) ⇒ ★**ISS-203 之后还有 ISS-199 排队** ★ · "
    "★**sw-lead** = ★**名下 open = 0** (★**它刚交完 ISS-201, 队列已空**★) ★ ⇒ ★**⇒ A 段空 = 【两个在飞 + 一个队列已空】, "
    "不是【没活】** ★ ⇒ ★**★铁律仍守着: 一个 agent 同时只允许一个写会话★** ★ |"
)

OLD_282_ROW = (
    "| `state/merge.py` | **0** | 冲突 **0** · 产出 **179** · 阻塞 43 (高危 33) · 未闭合需求 **106** "
    "(★**比上轮 102 多 4 ⇒ 是 ISS-200/201/202 交卷与新开单带出的新增需求, 不是账被做坏**★) |"
)
NEW_282_ROW = (
    "| `state/merge.py` | **0** | 冲突 **0** · 产出 **186** · 阻塞 43 (高危 33) · 未闭合需求 **112** "
    "(★**比上轮 102 多 10 ⇒ 是 ISS-200/201/202 交卷与新开单带出的新增需求, 不是账被做坏**★) |"
)

OLD_SNAP_ROW = (
    "| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 ⇒ 只落本地, 随时能看** ★★ |"
)
NEW_SNAP_ROW = (
    "| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 (02:42) ⇒ 只落本地, 随时能看** ★★ |"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".decision_page.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(PAGE, encoding="utf-8").read()
        text = raw

        for old, new, tag in (
            (OLD_TITLE, NEW_TITLE, "页首标题行"),
            (OLD_SEC_HEAD, NEW_SEC_HEAD, "§0.28 标题"),
            (OLD_281_TAIL, NEW_281_TAIL, "§0.28.1 补记"),
            (OLD_282_ROW, NEW_282_ROW, "§0.28.2 merge 行"),
            (OLD_SNAP_ROW, NEW_SNAP_ROW, "§0.28.2 快照行"),
        ):
            if old not in text:
                print("★%s 锚点不存在 ⇒ 拒绝写 (页面已被别人改过)" % tag)
                return 2
            text = text.replace(old, new, 1)

        if text == raw:
            print("★无变化 ⇒ 拒绝写")
            return 2

        atomic_write(PAGE, text)
        print("✅ 决策页 r29 已落盘 (5 处改动)")
        print("   DECISION_PENDING_2026-11-12.md %d B → %d B" % (len(raw), len(text)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
