#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CURRENT_TASK.md 状态行订正 (2026-11-12 01:5x · r28) —— main (项目总工) 执行
================================================================================
★★【★★★本脚本修一个【我自己在 01:4x 轮犯的错】★★★】★★★
★**错在哪**: 上一版 `_update_current_task_20261112_r27.py` 把本轮记账追加到了 **L1 (★**注释行**
  ★**—— 而 `state/board_progress.py` 的读法是: `if l.strip().startswith("#")` ⇒ ★**L1 被整条过滤掉**★
  ⇒ ⇒ ★**那段记账一个字符都到不了播报器 ⇒ 等于没写** ⇒ ⇒ ★**本脚本把 L1 还原成原文, 改写到 L2** ★

★**L2 才是真状态行**: `board_progress.py:119-125` ⇒ `lines = [非#行]` ⇒ ★**`cur = lines[0]` = L2 (那条 `★[状态] …` 长行)** ★
  ⇒ ★**L2 末尾追加 = 播报器第 1 行就会显示本轮口径** ★

★**本脚本做 3 件事 (★全是【订正过期事实】, 不新增任何待办, 不替老板决定★)**:
   ① L1 还原成原文 (★**撤掉我 r27 误写进去的 dead text** ★)
   ② L2 (★**真状态行** ★) 末尾追加本轮 (01:4x~01:5x) 的事实段
   ③ L7 (★**「⑤ 在飞」** ★) 改写成当刻真实在飞 (★**ISS-136 已 verified · 现在在飞 ISS-195/ISS-200 · ISS-199 排队** ★)
      ⇒ ★**不改 = 老板看不懂为什么还是没派活, 而且会读到一条已经收口的单还在飞** ★★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir)) + 逐行 diff 自证
★**边界**: 不改 `PROJECT_TRACKER.md` (★尤其 §0 锁死表★) · 不发邮件 · 不写任何子总工的分片 · 不动 L3~L6 / L8~L10
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

ORIG_L1 = ("# CURRENT_TASK -- 当前在做什么 (board_progress.py 会读本文件: 第 1 行 = 当前在做; "
           "后面【不以 ★ 开头】的行 = 待办清单)")

MARK = "★【11-12 01:4x 后继计划轮】"

APPEND = (
    MARK
    + " ★**A 段本 job 派 0 条 (★**不是没活, 是【兄弟 job「ARS45 队列自动派活」已把两个名额占满】★**)**"
    + " ⇒ ★**实测 `advance.py --json` = `internal: []` · `approvals: []` · `decisions: 36` · `waiting: []`**"
    + " ⇒ ★**根因: 兄弟 job 01:4x 派了 ISS-195→hw-lead (会话 `dc510f7c`) + ISS-200→mech-lead (会话 `0ef5e479`), 两个实测 status=running**"
    + " ⇒ ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本 job 不重复派 (★**两个 job 同时派同一个 agent = 撞 R18, 分片合并丢 12%~38%★**)** ★"
    + " ⇒ ★**本轮实际在飞 3 条**: ★**① ISS-195 (hw-lead) 麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算 (due 11-13)** ★"
    + "**② ISS-200 (mech-lead) 结构侧 J_CHG pin map 旧口径收敛 (due 11-13)** ★"
    + "**③ ISS-199 (hw-lead) HW 侧 J_CHG pin map 剩 4 处第二口径 (due 11-14, ★**排队中 = 等 ISS-195 交卷释放名额★**)**"
    + " ⇒ ★**这 3 条都不是 PCB 布线/布局类 (★**机械孔位净空复算 / HW 侧文档 pin map 口径 / 结构侧 pin map 口径★**) ⇒ ★**按原理图主线口径【跳过 0 条 PCB 类】** ★"
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
    + "★**gate_check 0 (★**Q1 18/18** ★ + ★**Q6 硬件真源闸 ✅**★)** · ★**issue_check 1 (违规 **29** 条 · ★**比上轮 30 少 1 = ISS-136 关掉一条, 没新造违规 · 全是逾期类★**)** · "
    + "★**stage_gate 1 (当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0)** · ★**daily_check 3 (巡检异常已记录, 非崩溃: 问题闭环门 29 条 · 内部未闭合 100→102 · 问题单 194→196)** ★"
    + " ⇒ ★★★**★【B 段 approvals = 0 (★**老板 2026-11-11 19:31「一律不发」政策后恒为空★**) ⇒ 草稿一件没少, 一封都没发** ★**: "
    + "`state/outbox/` 实测 **19 份 .md** (16 草稿 + README + 政策件 `NO_OUTBOUND_POLICY.md` + 内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` **3 份** ⇒ ★**零缺失** ★"
    + " ⇒ ★★★**★【C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议默认值) ⇒ 本轮你不用做任何新决定】★★** ⇒ ★**决策页 `DECISION_PENDING_2026-11-12.md` 已刷第 2 次 (§0.27) ⇒ 36 条的「逾期」列逐条核对 = 0 条不一致, 建议默认值一个没动** ★"
    + " ⇒ ★**板 / 网表 / 脚表 / .kicad_pro md5 一字未动 (611b869e / c78f9912 / 4814617e / 3e504d2b)** ⇒ ★**本 job 没碰任何生产文件** ★"
    + " ⇒ ★**GitHub: 本 job 不推 (★**统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ⇒ 上次推送 2026-11-12T00:26:07** ★"
    + " ⇒ ★**本地快照已落 `PROGRESS_SNAPSHOT.md` (01:56)** ★"
    + " ⇒ ★**下一步**: 等 ISS-195 (hw-lead) / ISS-200 (mech-lead) 交卷 → main 独立验收签字 → hw-lead 名额释放 → ★**ISS-199 自动可派** ⇒ ★**另: P2 原理图设计评审 仍等你翻 PDF + `HW/PCB/REVIEW_CHECKLIST_P2.md` + `HW/PCB/PIN_REALITY_GAP.md`; 整链重出第 1 步 等 ISS-198 验完启动 (★**ISS-198 已 verified·可启动**★)** ★★"
)

NEW_L7 = (
    "⑤ ★**在飞 (此刻 3 条 ⇒ A 段本 job 无可派)**: ★**① ISS-195 → hw-lead** (★麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算 · due 11-13 · 会话 `dc510f7c` 01:48 起 **status=running**★) · "
    "★**② ISS-200 → mech-lead** (★结构侧 J_CHG pin map 旧口径收敛 · due 11-13 · 会话 `0ef5e479` 01:48 起 **status=running**★) · "
    "★**③ ISS-199 → hw-lead 排队中** (★HW 侧 J_CHG pin map 剩 4 处第二口径 · due 11-14 · ★**等 ISS-195 交卷释放名额★**) ⇒ "
    "★**⇒ 兄弟 job「ARS45 队列自动派活」01:4x 派的 (★**它已把两个总工的名额占满 ⇒ 本 job 不重复派, 铁律: 一个 agent 同时只允许一个写会话★**) ⇒ sw-lead 名下 open = 0** ⇒ "
    "★**⇒ ISS-136 已于本轮收口 (fixing→verified, verify_by=main) · ISS-193 / ISS-198 亦已 verified/pass ⇒ 三条都不在飞了** ⇒ "
    "★**⇒ 交卷后由 main 独立验收签字, 本 job 不插手** ★★"
)


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(P, encoding="utf-8").read()
        lines = raw.splitlines(keepends=True)

        if len(lines) < 8:
            print("❌ CURRENT_TASK.md 行数异常 ⇒ 拒绝改")
            return 2

        # ---- ① L1 还原成原文 (撤掉 r27 误写的 dead text: 它在 # 注释行里, 播报器读不到) ----
        if lines[0].startswith(ORIG_L1):
            if lines[0].rstrip("\n") == ORIG_L1:
                print("ℹ️ L1 已是原文 (无 r27 误写) ⇒ 跳过还原")
            else:
                lines[0] = ORIG_L1 + "\n"
                print("✅ L1 已还原成原文 (★撤掉 r27 误写进 # 注释行的 dead text★)")
        else:
            print("❌ L1 不是预期原文 ⇒ 拒绝改 (防误伤)")
            return 2

        # ---- ② L2 (真状态行) 末尾追加本轮 ----
        if MARK in lines[1]:
            print("ℹ️ L2 已含本轮记账 ⇒ 幂等, 跳过追加")
        else:
            lines[1] = lines[1].rstrip("\n") + APPEND + "\n"
            print(f"✅ L2 已追加本轮记账 (+{len(APPEND)} 字符)")

        # ---- ③ L7 (⑤ 在飞) 订正 ----
        if "ISS-136 → hw-lead" in lines[6] and "在飞 (此刻 3 条" not in lines[6]:
            lines[6] = NEW_L7 + "\n"
            print("✅ L7「⑤ 在飞」已订正 (★ISS-136 已收口; 真实在飞 = ISS-195 / ISS-200 / ISS-199 排队★)")
        elif "在飞 (此刻 3 条" in lines[6]:
            print("ℹ️ L7 已是本轮口径 ⇒ 幂等, 跳过")
        else:
            print("❌ L7 不是预期内容 ⇒ 拒绝改 (防误伤)")
            return 2

        out = "".join(lines)

        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(P), prefix=".CURRENT_TASK.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(out)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, P)
            dfd = os.open(os.path.dirname(P), os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    # ---- 逐行自证: 只有 L1 / L2 / L7 变了 ----
    old = raw.splitlines()
    new = out.splitlines()
    changed = [i + 1 for i in range(min(len(old), len(new))) if old[i] != new[i]]
    print(f"✅ CURRENT_TASK.md 已原子落盘: {P}")
    print(f"   变更行: {changed} (★预期 = [1, 2, 7]★)")
    print("   L3~L6 / L8~L10 一字未动")

    # ---- 验证播报器真能读到 L2 ----
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "board_progress.py")],
                       capture_output=True, text=True, cwd=PROJ)
    hit = "11-12 01:4x" in (r.stdout or "")
    print(f"   board_progress.py 播报第 1 行含本轮口径: {'✅ 是' if hit else '❌ 否'} (rc={r.returncode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
