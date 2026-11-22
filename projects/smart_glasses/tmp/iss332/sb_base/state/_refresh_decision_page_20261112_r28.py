#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页 2026-11-12 · r27 补记 (r28) —— 由 main (项目总工) 执行
================================================================================
★★**为什么要有这次补记 (★实测, 不是推测★)** ★★:
· r27 落盘时 (02:3x) 本 job 只派了 ISS-202 ⇒ 页面上写的「A 段派 1 条 / 僵尸 fixing 落账 1 条」
· ★**但 ISS-202 在 02:35 就交卷了 (★本 job 派的那条自己干完了★)** ⇒ ★**main 02:4x 独立复核并签字 ⇒ verified** ★
  ⇒ ★**A 段立刻又冒出 ISS-203 (mech-lead) ⇒ 本 job 02:4x 派了出去** ★
  ⇒ ★**同时 main 清掉了第 8 条僵尸 fixing (ISS-202 若不落账就是第 8 条)★** ★

★★**本脚本只做 3 件事 (★全是【记账】, 不替老板决定任何事★)**:
   ① 改页首标题行 + §0.28 标题 (A 段派 1 条 → 2 条; 僵尸 fixing 落账 1 条 → 2 条; 本轮时间窗拉长)
   ② **§0.28.1** = 补上 ISS-202 的落账 + ISS-203 的派出 (★**含 ISS-203 为什么不是 PCB 类**★)
   ③ **§0.28.2** = 订正核验 5 连的实测 rc (★**decision_truth --self-test 从 rc=1 修回 rc=0** ★)
      + **§0.28.3** = 补记第 4 处改动 (★**decision_truth.py 的硬编数护栏修正**★)

★★**★本轮唯一一处【动了闸脚本】的地方 (必须向老板说清)★** ★★:
· ★**`state/daily_check.py` 巡检报出 `decision_truth --self-test` rc=1** ⇒ ★**这是本轮新出现的红★**
· ★**根因 (★我亲自做了反事实实测, 不是推测★)**: ★**老板 2026-11-12 02:02 的「不再发信, 全靠自己查资料」
  在 pm.yaml 给 `iss105_jchg_rfq_release` 落了 `decision`** ⇒ ★**hw.yaml 里同一 key 的那条别名 need
  被【跨分片同 key 规则】正确关闭** ⇒ ★**降幅 8 → 9** ★ ⇒ ★**而 `decision_truth.py` 的回归护栏把降幅
  硬编成了 `== 8`** ⇒ ★**老板新拍一次板, 这道护栏就自己炸** ★
  ⇒ ★**反事实实测 (main 亲手跑)**: 把 pm.yaml 里那条 `decision` 去掉 ⇒ ★**降幅立刻回到 8** ★
  ⇒ ★**⇒ 证明第 9 条确实由老板 02:02 那条决定产生, 不是别的改动带进来的** ★
· ★**修法 (★不是把断言放宽成"随便多少都行"★)**: ★**硬编 `== 8` 改成【下限 `>= 9` + 具名 key 断言】** ★
  ⇒ ★**下限**: ★**"跨分片规则彻底失效 ⇒ 降幅掉回 0" 仍然会红 (这才是这道护栏真正要抓的)** ★
  ⇒ ★**具名**: ★**7 个 key 必须各自找得到对应别名 need ⇒ 「数字对但关错了对象」也会红** ★
    (★**旧护栏只数个数 ⇒ 关错对象它抓不到**★)
· ★**自证 (★我自己造了 3 个反向用例, 逐个跑过★)**:
  ① ★**把 `decision_keys` 改成返回空集 (模拟跨分片规则失效) ⇒ rc=1 红** ★
  ② ★**删掉 hw.yaml 里 `iss105_jchg_rfq_release` 那条别名 need ⇒ 降幅 8 ⇒ rc=1 红** ★
  ③ ★**把 sw.yaml 里 `demo_od_p0_4_panel_init_code` 别名换成另一个已拍板 key (⇒ 降幅数字仍是 9, 但关错了对象)
     ⇒ ★**具名断言红 (rc=1)** ★ ⇒ ★**这条正是旧护栏抓不到的** ★
  ⇒ ★**改完三个反向用例全部恢复原状, 分片与脚本逐字节比对一致 (我 diff 过)** ★
· ★**★这是同一个病第 2 次复发 (2026-11-10 已经为「补录老板 11-04 决定」把硬编数 7 改成 8 一次)★** ⇒
  ★**⇒ 本次不再硬编, 改成下限 + 具名 ⇒ 以后老板再拍板不会再自己炸** ★

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

# ---------------- ① 页首标题行 ----------------
OLD_TITLE = (
    "# 待老板拍板页 · 2026-11-12 02:3x (第 3 次刷新 · ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** "
    "+ ★**A 段本 job 派 1 条 (ISS-202 → mech-lead)** ★** + ★**僵尸 fixing 落账 1 条 (ISS-200) ⇒ "
    "A 段从空变 1 条★**)** ⇒ ★**本轮你不用做任何新决定** ★★)"
)
NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-12 02:5x (第 4 次刷新 · ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** "
    "+ ★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** ★** + ★**僵尸 fixing 落账 2 条 "
    "(ISS-200 / ISS-202) ⇒ A 段从空变 2 条★**)** ⇒ ★**本轮你不用做任何新决定** ★★)"
)

OLD_SEC_HEAD = (
    "## 0.28 ★★★ 本轮 (2026-11-12 02:16 ~ 02:3x): ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** + "
    "★**A 段本 job 派 1 条 (ISS-202 → mech-lead)** ★★"
)
NEW_SEC_HEAD = (
    "## 0.28 ★★★ 本轮 (2026-11-12 02:16 ~ 02:5x): ★**C 段 36 → 36 (1 退休 / 1 新增 / 0 改建议值)** + "
    "★**A 段本 job 派 2 条 (ISS-202 / ISS-203 → mech-lead)** + ★**僵尸 fixing 落账 2 条 (ISS-200 / ISS-202)** ★★"
)

# ---------------- ② §0.28.1 补记 ----------------
OLD_281_TAIL = (
    "| ★**另外两个名额为什么没派** | ★**hw-lead = 真在飞** (ISS-195 · 会话 `dc510f7c` 实测 status=**running**, "
    "★**起于 01:48, 已跑 37 分钟+**★ ⇒ ★**ISS-199 (HW 侧 J_CHG 剩 4 处第二口径) 排队等它交卷**★) · "
    "★**sw-lead = 真在飞** (ISS-201 · 会话 `be918818` 实测 status=**running**, ★**兄弟 job 02:0x 派的**★) ★ "
    "⇒ ★**铁律: 一个 agent 同时只允许一个写会话** ★ |"
)
NEW_281_TAIL = OLD_281_TAIL + (
    "\n| ★★**★补记 (02:4x): ISS-202 自己干完了 (★02:26 派 → 02:35 交卷★) ⇒ main 当场独立复核并签字 ⇒ "
    "**verified** ⇒ ★**A 段立刻又冒出 ISS-203 (mech-lead) ⇒ 02:4x 派了出去** ★** | ★**交卷页 `HANDOFF/2026-11-12_mech-lead_ISS202_J_CHG旧口径收尾.md` "
    "(16,331 B, 02:34)★ ⇒ ★**我逐条独立复核过 (不采信自述)**: ★**网表逐脚对拍一致** (pin7=NC · pin8=TS_BAT · "
    "pin9/10=HINGE_RSV) · ★**两条 claim (`j_chg_pin_map` + `mech_j_chg_pins`) 各仍只有 1 条 (无 key 重复)** · "
    "★**§5.1 表 J_CHG 行已改** (`10 (1×10 @0.5)` / 必装 7 / DNP 3 / 3.5mm / 5.5mm, ★**旧值是 `6 (1×6 @1.27)`**★) · "
    "★**文档里 TS_RTN 0 行, 分片里 6 行我逐行看过全属【变更说明/残留报告/历史沿革/已订正注记】** ⇒ 当前口径断言 0 条 · "
    "★**claims 186 未变 · 板/网表/pins/.kicad_pro 一字未变** · merge rc=0 · **Q1 18/18** ⇒ ★**它报的 5 条残留全部登记成 "
    "need 给 main (都 due 11-14 ⇒ 没藏账)★** ★ |\n"
    "| ★**★补记 (02:4x): ISS-202 若不落账就是【第 8 条僵尸 fixing】★ | ★**它 02:35 交卷、02:4x 落账 ⇒ "
    "★**没等下一轮 cron, 本 job 当场清掉**★ ⇒ ★**⇒ 这是本 job 连续第 2 次亲手清僵尸** (ISS-200 是第 7 次) ★★ |\n"
    "| ★**ISS-203 为什么派 (★不是 PCB 类★)** | ★**它是【机械复核器的板宽常量迁移】(★`hw_cross_review_check.py` / "
    "`service_port_check.py` 的 `pcb_w` 从 15.00 → 30.00★) ⇒ ★**改的是【给旧板打分的假判据】, 不是布线/布局** ★ "
    "⇒ ★**符合你 10-07「先解决原理图绘制」的主线口径** ★ ⇒ ★**它自己的边界还写死了「不许碰 `MECH/BOARD_GEOM_30MM.md` "
    "权威表」「不许改任何阈值」「不许降级 FAIL 凑绿」** ★ ⇒ ★**我 02:4x 亲自 grep 复核过它的前提**: "
    "★**`hw_cross_review_check.py:52` 与 `service_port_check.py:44` 的 `pcb_w` 确实还是 15.00** · "
    "★**权威表 `MECH/BOARD_GEOM_30MM.md` 板宽 Y = 30.00mm (老板 10-29 19:16 拍板) / 板长 X = 60.00mm** · "
    "★**分片里那 2 条板长 claim 确实还是旧值 (69mm / 76mm)** ⇒ ★**不是空单, 是真活** ★ |"
)

# ---------------- ③ §0.28.2 订正 rc ----------------
OLD_282_ROW = (
    "| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃) |"
)
NEW_282_ROW = (
    "| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 29 条 (★**全是逾期类**★) "
    "| ★★**`decision_truth --self-test` 的 rc 由 1 修回 0** ★★ | ★**本轮巡检新报出这个红 ⇒ 我做了反事实实测 ⇒ "
    "根因 = ★**老板 02:02 政策在 pm.yaml 给 `iss105_jchg_rfq_release` 落了 `decision` ⇒ hw.yaml 同 key 的别名 need "
    "被跨分片规则正确关闭 ⇒ 降幅 8→9 ⇒ 而护栏把降幅硬编成 `== 8`** ★ ⇒ ★**反事实: 去掉那条 decision ⇒ 降幅立刻回到 8** ★ "
    "⇒ ★**修法: 硬编 `== 8` 改成【下限 `>= 9` + 7 个具名 key 断言】⇒ 老板再拍板不会自己炸, 且「数字对但关错对象」也抓得到** ★ "
    "⇒ ★**我自己造了 3 个反向用例逐个跑过 (规则失效 ⇒ 红 / 删别名 ⇒ 红 / 换错对象 ⇒ 红) ⇒ 全部恢复原状并逐字节 diff 核对** ★ "
    "⇒ ★**这是同一个病第 2 次复发 (11-10 已为「补录老板 11-04 决定」把硬编数 7 改 8 一次)★** |"
)

# ---------------- ④ §0.28.3 补第 4 处改动 ----------------
OLD_283_ROW = (
    "| 3 | ★**订正页尾「逾期分布」** (已逾期 **33 → 32** · 新增「剩 2 天 1」) + ★**订正 §1 清点行** "
    "(§2 外发 1 → 0 · §7 方法论 2 → 3) + ★**§8 与页首标题行改写** ★ | "
    "★**天数每天都在走 + 本轮 1 退休 1 新增 ⇒ 不重算就是给老板看假账** ★ |"
)
NEW_283_ROW = OLD_283_ROW + (
    "\n| 4 | ★**★改 `state/decision_truth.py` 的回归护栏 (★**唯一一处动了闸脚本**★)★**: ★**硬编 `== 8` → "
    "【下限 `>= 9` + 7 个具名 key 断言】** ★ | ★**本轮巡检实测报出这个红** ⇒ ★**根因已用反事实实测钉死 "
    "(去掉老板 02:02 那条 decision ⇒ 降幅立刻回到 8)⇒ 不是别处的改动带进来的** ★ ⇒ ★**修法不是「放宽成随便多少都行」: "
    "下限仍能抓「跨分片规则彻底失效 ⇒ 降幅掉回 0」, 具名断言还能抓「数字对但关错了对象」(★**旧护栏只数个数, 抓不到这个**★)** "
    "⇒ ★**我自己造了 3 个反向用例逐个跑过, 全部按预期变红, 之后全部恢复原状并逐字节 diff 核对** ★ ⇒ "
    "★**闸变强了, 不是变松了** ★ |"
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
            (OLD_282_ROW, NEW_282_ROW, "§0.28.2 核验行"),
            (OLD_283_ROW, NEW_283_ROW, "§0.28.3 改动行"),
        ):
            if old not in text:
                print("★%s 锚点不存在 ⇒ 拒绝写 (页面已被别人改过)" % tag)
                return 2
            text = text.replace(old, new, 1)

        if text == raw:
            print("★无变化 ⇒ 拒绝写")
            return 2

        atomic_write(PAGE, text)
        print("✅ 决策页 r28 已落盘 (5 处改动)")
        print("   DECISION_PENDING_2026-11-12.md %d B → %d B" % (len(raw), len(text)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
