#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_update_current_task_20261112_r30.py —— ★★本 job (ARS45 继续执行后继计划) 03:3x 这一轮的 CURRENT_TASK 落账★★

★★只改两处 (★其余逐字不动★)★★:
  ① 第 8 行 (★"⑤ 在飞"★) ⇒ 改成【此刻 3 条在飞 + 2 条排队 + 本轮派了什么 + 为什么】
  ② 第 2 行 (★★[状态] 那条 mega 行★) ⇒ **只追加**一段本轮小结 (★不改历史段★)

★★纪律 (★house pattern★)★★: flock + 锁内重读 + 原子写 + 改前改后逐行 diff 自证
★★边界★★: 不改 §0 锁死表 · 不改 C 段任何建议默认值 · 不写任何子总工的分片 · 不碰任何生产文件
"""
import fcntl
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PATH = os.path.join(HERE, "CURRENT_TASK.md")
LOCK = os.path.join(HERE, ".current_task.lock")

OLD_LINE8_START = "⑤ ★**在飞 (此刻 3 条 ⇒ A 段本 job 无可派)**: ★**① ISS-195 → hw-lead**"

NEW_LINE8 = (
    "⑤ ★**在飞 (★2026-11-12 03:3x 实测·本 job 刚派完★)**: "
    "★**① ISS-195 → hw-lead** (★麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算 · due 11-13 · 会话 `dc510f7c` "
    "01:48 起 **status=running**·★03:17:37 仍在写 ⇒ **真在飞, 不是僵尸**★) · "
    "★**② ISS-205 → sw-lead (★本 job 03:27 派出·owner 由 hw-lead 改派★)** (★原理图位号加 `_1` 数字后缀 ⇒ "
    "KiCad 导出的 BOM 不再带 `?` · high · due 11-14 · 会话 `660e4fce` **running**★) · "
    "★**③ ISS-206 → mech-lead (★本 job 03:28 派出·新开单★)** (★结构侧 J_CHG 旧口径一次性收口 ⇒ 消灭第 3 套 "
    "pin map · medium · due 11-13 · 会话 `d5a63589` **running**★) · "
    "★**排队 2 条 (都等 hw-lead 名额)**: ISS-199 (HW 侧 J_CHG 剩 4 处第二口径) + ISS-204 (J_SOM_P2.pin7 引脚复用"
    "合法性查证) ⇒ ★**三个总工此刻各有一个在跑写会话 ⇒ A 段真空 ⇒ 本 job 不重复派 (铁律)★** ★★ ⇒ "
    "★**本 job 本轮做了什么 (★03:2x~03:3x 实测·不是推测★)**: "
    "① ★**`advance.py --json` 起初 = `internal: []`·`approvals: []`·`decisions: 36`·`waiting: []` ⇒ A 段空的根因 = "
    "★**hw-lead 名额被 ISS-195 占着 (真在飞) + sw-lead / mech-lead 名下 open = 0 (队列真空)**★ ⇒ "
    "② ★**改派 ISS-205: hw-lead → sw-lead** (★依据三条全查过: hw-lead 真在飞 ⇒ 铁律不许两个写会话; "
    "本单 high + due 11-14 + 卡整链重出第 3 步 ⇒ 干等会把最高优先级压在 medium 队列后面; sw-lead 实测无在跑会话; "
    "★**文件交集实测 = 0**★) ⇒ ★**随之唯一一处改动 = 分片写入目标 hw.yaml → sw.yaml (不许写别人的分片)**** ⇒ "
    "③ ★**新开 ISS-206 → mech-lead** (★ISS-202/ISS-203 登记给 main 的 8 条 need 已由 main 逐条裁完 ⇒ 6 条要做 + "
    "2 条明令不许动 ⇒ 本单 = 裁完之后的执行单★) ⇒ "
    "④ ★**ISS-122 `fixing` → `deferred`** (★陈旧标记清理: 它 owner=main·`dispatched_at`=None ⇒ 从来没有在飞会话; "
    "且它 = BGA 逃线层数 = PCB 布局类 ⇒ 按 10:07 口径排队; 且它的结论前提「问 PCB 厂 DFM 报告」已被 02:02 "
    "「不再发信」封死 ⇒ 恢复条件已写死在 note 里★) ⇒ "
    "⑤ ★**板面零变化**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · "
    "脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` **一字未动** ⇒ "
    "**G1 仍开, 不许投板** ★★"
)

APPEND_STATE = (
    " ⇒ ★★★★★**★【11-12 03:3x 后继计划轮 · A 段从【空】到【派 2 条】(★派活不是本 job 抢功, 是因为"
    "hw-lead 名额被真在飞的单占着, 而另两个总工名下是真空⇒ 排队逻辑自己把主线堵住了★)】**★**"
    "本轮实测 `advance.py --json` 起初 = `internal: []`·`approvals: []`·`decisions: 36`·`waiting: []` "
    "⇒ 根因 = ★**hw-lead 名额被 ISS-195 占着 (会话 `dc510f7c` 03:17:37 仍在写 ⇒ **真在飞, 不是僵尸**) + "
    "sw-lead / mech-lead 名下 open = 0 (队列真空)**★ ⇒ "
    "★**⇒ 本 job 做了三件事 (★都是【内部可动】, 没碰老板的拍板桶★)**: "
    "① ★**ISS-205 改派 owner: hw-lead → sw-lead** (★high + due 11-14 + 卡整链重出第 3 步 + 文件交集实测 = 0 + "
    "sw-lead 实测无在跑会话★) ⇒ ★**随之唯一一处改动 = 分片写入目标 `hw.yaml` → `sw.yaml` (不许写别人的分片)**** ⇒ "
    "② ★**新开 ISS-206 → mech-lead** (★ISS-202/ISS-203 的 8 条 need 由 main 逐条裁完: 6 条要做 + 2 条明令不许动 + "
    "一条留给 main 的闸 (裁 6 若属【两种互斥方案】⇒ 只报不改)★) ⇒ "
    "③ ★**ISS-122 `fixing` → `deferred`** (★陈旧标记: 从来没有在飞会话 + PCB 布局类排队 + 「问 PCB 厂 DFM 报告」"
    "这条路已被「不再发信」封死 ⇒ 恢复条件写死在 note 里★) ⇒ "
    "★**⇒ 在飞 3 条 (hw-lead ISS-195 / sw-lead ISS-205 / mech-lead ISS-206) ⇒ 三个总工各占一个写会话 ⇒ 排队 2 条 "
    "(ISS-199 / ISS-204, 都等 hw-lead 名额)**** ★★ ⇒ "
    "★**核验 5 连本轮实测 rc**: merge **0** (冲突 **0** · 产出 **189** · 阻塞 43 · 未闭合需求 **117**) · "
    "gate_check **0** (★**齐备率 18/18** ★ + 证据分级 3/3 + 接口声明 489 + 【Q6 硬件真源闸】✅) · "
    "issue_check **1** (违规 **29** 条 · 全是逾期类) · stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ "
    "unconnected=45 需 0) · daily_check **3** (巡检异常已记录, 非崩溃: 问题闭环门 29 条) ⇒ ★**原理图侧尺子复跑: "
    "ERC **0** 条 · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网)** ★★ ⇒ "
    "★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议默认值) ⇒ 决策页 `DECISION_PENDING_2026-11-12.md` (02:50 第 6 次刷新) "
    "实测 36/36 逐 key 命中 ⇒ 本轮不用再刷** ★★ ⇒ "
    "★**GitHub: 本 job 不推 (★统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ⇒ 只落本地快照 "
    "`PROGRESS_SNAPSHOT.md` (03:30)**** ★★ ⇒ "
    "★**下一步**: ① 等三条交卷 → main 独立验收签字 (★不采信自述★) ⇒ ② **sw-lead 交卷后由 main 重出投产包** "
    "(★重生成原理图 ⇒ `doc/sch_src/` + PDF 变旧 ⇒ `chain_gate.py` 会红 ⇒ 那是预期中间态, 不是它没做完★) ⇒ "
    "③ ISS-195 交卷 ⇒ hw-lead 名额释放 ⇒ ISS-199 / ISS-204 自动可派 ⇒ ④ ★**整链重出第 1 步的落表作业包已备好** "
    "(`state/RECHAIN_STEP1_LANDING_SPEC.md` · ★纯规格页·一个字没改真文件★) ⇒ ★**但 D 项 (R3 去耦) 仍卡老板评审"
    "的一句话 ⇒ 建议 C+E+D 一次落, 别分两趟白跑留证链/Gerber/投产包/盖印** ★★"
)


def atomic_write(text, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(PATH, encoding="utf-8").read()
        lines = raw.split("\n")
        assert len(lines) >= 11, "CURRENT_TASK.md 行数异常 ⇒ 中止"
        assert lines[7].startswith(OLD_LINE8_START), "第 8 行锚点不存在 ⇒ 中止 (别人改过?)"

        before = list(lines)
        lines[7] = NEW_LINE8
        # ★第 2 行只追加, 不动历史段
        assert "11-12 03:3x 后继计划轮" not in lines[1], "本轮小结已追加过 ⇒ 中止"
        lines[1] = lines[1] + APPEND_STATE

        text = "\n".join(lines)
        if text == raw:
            print("★无变化 ⇒ 中止")
            return 2
        atomic_write(text, PATH)

        # 自证: 只有第 2 行和第 8 行变了
        after = open(PATH, encoding="utf-8").read().split("\n")
        assert len(after) == len(before), "行数变了 ⇒ 中止"
        changed = [i + 1 for i in range(len(before)) if before[i] != after[i]]
        assert changed == [2, 8], "改动行 = %s (期望 [2, 8]) ⇒ 中止" % changed
        assert after[1].startswith(before[1][:200]), "第 2 行被重写 (只该追加) ⇒ 中止"
        print("✅ CURRENT_TASK.md 已落账: 改动行 =", changed)
        print("   第 2 行: %d B → %d B (只追加本轮小结)" % (len(before[1]), len(after[1])))
        print("   第 8 行: %d B → %d B (在飞状态)" % (len(before[7]), len(after[7])))
        print("   其余 %d 行逐字未动 (已实测)" % (len(before) - 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
