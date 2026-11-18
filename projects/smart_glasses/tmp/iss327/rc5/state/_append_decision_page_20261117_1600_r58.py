#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_decision_page_20261117_1600_r58.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 16:0x★
★★**追加式 (★老字一行不删★)**: DECISION_PENDING_2026-11-16.md §A-补20 ★★

★★**本节内容 (★全部 main 本机实跑·不抄任何交卷报告★)★★ ★★
· ★**① ISS-289 由 main 复验落 verified** (★数字齐: 交卷单 628 行 / 76908 B · 新闸 rc=0 · selftest 10/10 ·
  preflight rc=0 · caliber rc=0 · r3 rc=1 (现状读数) · 受保护 5 件逐字节未变 · 分片 iss289 = 11★)
· ★**② 新开 ISS-292 (hw-lead) 并派出** (★清单页生成器与盘面页脱钩 ⇒ 跑一次就把订正冲掉·卡动板那趟开工★)
· ★**③ 待拍板面 43 ⇒ 44 条**: ★**新增 `boss_c_vbus_gnd_reserve_pad_20261117`** (★C_VBUS_GND 预留位留不留 ·
  ★建议默认 = 下板 (收工 185)★) ⇒ ★**其余 43 条一条不动** ★
· ★**④ hw-lead 交卷单里的 4 条拍板项 P1~P4**: ★**P1 / P3 = main 自己定 (不用你拍)** · ★**P4 = 已派单 (ISS-292)**★
  · ★**P2 = 新增第 44 条给你 (见 §A-补20-①)** ★
· ★**⑤ rc**: merge 0 · gate_check 0 (Q1 18/18) · issue_check 0 · stage_gate 1 (缺 1 项 = PCB 布线 unconnected=45) ·
  daily_check 3 (★板面比网表旧 · 投产包比源旧 ⇒ 预期红★) ★

★★**边界 (★写死的)★★ ★★
· ★**只追加, 老字一行不删不rewrite** ★ · ★**先备份 (★`DECISION_PENDING_2026-11-16.md.bak_20261117_1600_r58`★)** ★
· ★**flock (`state/.decision_page.lock`) + 锁内重读 + 原子写** ★
· ★**不改 §A / §B / §C 任何一条判据与建议默认值 · 不代老板拍板 · 零外发 · 不碰 `PROJECT_TRACKER.md` §0 锁死表**
  · 不改 `state/issue_log.yaml` 任何 status (★ISS-097 仍 fixed ⇒ 等老板一句★)** ★
"""
import fcntl
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
LOCK = os.path.join(HERE, ".decision_page.lock")
BAK = PAGE + ".bak_20261117_1600_r58"

BLOCK = """
---

## §A-补20 · ★★r58 · 2026-11-17 16:0x · ★★★**ISS-289 收口 + ISS-292 派出 + 待拍板面 43 ⇒ 44 条**★★★ (★cron 775d9893 本机实跑★)

> ★**出页人**: 项目总工 (main / moli) · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**16:0x 实跑·追加式·老字一行不删★**
> ★**本节给你一件事**: ★**一条新拍板 (★C_VBUS_GND 那个预留位: 留还是不留·建议「下板」·一行回复即可★)** ★

---

### ★① ISS-289 已由 main 独立复验落 verified (★不是抄交卷报告★)

| 验收项 | main 16:0x 实跑 | 结论 |
|---|---|---|
| ★**交卷单** ★ | ★`HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md` = **628 行 / 76908 B** · B0~B6 七段齐 ★ | ★**通过** (★占位符 grep 4 处命中全是「0 处残留」这句自述, 无真实未完成标记★) ★ |
| ★**新闸本体** ★ | ★`python3 HW/check_workpack_state_values.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 · 反向用例 10/10 通过** ★ | ★**通过** ★ |
| ★**其它三道闸** ★ | ★preflight **rc=0** · caliber **rc=0** · r3 **rc=1** (★现状读数, FINDINGS=2 = F2+F3, R3-A4 零标记 **40**★) ★ | ★**通过** (★与交卷单自评逐条一致★) ★ |
| ★**受保护 5 件** ★ | ★板 `611b869e…` (mtime 仍 `2026-11-06 07:07:17`) · `.kicad_pro` `3e504d2b…` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` ★ | ★**逐字节未变 ⇒ 零写板 · 零落表 成立** ★ |
| ★**分片** ★ | ★`grep -c iss289 state/fragments/hw.yaml` = **11** (★与交卷单自报一致★) ★ | ★**通过** ★ |
| ★**三道总闸** ★ | ★merge rc=0 · gate_check rc=0 (Q1 18/18 · 按本单计分不再回退旧交接单) · issue_check rc=0 ★ | ★**全绿** ★ |

★**main 顺手验了 hw-lead 的三个问题 (★自己查, 不采信口头★)★**: ① **差的那 1 件 = `C_VBUS_GND`** ⇒ main 实读 `HW/netlist_v1.csv:10` 与 `:12` ⇒ board 列 = **`CHG_BOARD`** ⇒ **单边差集 = 板级归属差, 不是漏数** ⇒ ★**那一趟按「开工前 186 / 收工后 185」走** ★ ② **156 与 1 不是一回事** (156 = 板侧要改名的位号数 · 1 = 板上已带 `_1` 的) ⇒ 改完 = 157 (S2 下掉 `C_VBUS_GND` ⇒ 156) ★ ③ **写死的现状值 = 25 条** (29 条登记里只有 4 条走台账口径) ⇒ ★**收工必须同一次重锚** ⇒ 已写进 ISS-292 的 B4 ★

---

### ★② 新开 ISS-292 (hw-lead) 并已派出 (★卡「板只改一次」那一趟开工的那一件★)

★**病灶 (★main 16:0x 本机实读★)**: `state/_iss277_build_preflight.py` 里 R3-A4 那条仍写 **「54 颗 / 43 颗 / 43 颗」**、脚表那条仍写 **「15 条缺陷」**、且 ★**缺 `B32_V2_NET_RENAME`** ⇒ 而盘面页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 已被 ISS-289 手工订正成 **51 / 40 / 40 + 18 条** ⇒ ★**⇒ 同源关系断了 ⇒ 谁跑一次生成器, 谁就把 ISS-283/ISS-289 的订正全冲掉 ⇒ 新闸当场红 ⇒ 而那个红会出现在【动板那趟已经开工之后】⇒ 会被误读成「板改坏了」⇒ 有人会去改板凑绿 ⇒ 最坏 = 把 `C_VBUS_GND` 装回板上 = 2-4 周 + ¥4-8K** ★

★**本单要求 (★任务书 `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign.md` · 已过 `check_brief_commands --brief-file` rc=0★)**: ★**① 生成器改成从真源读 (不许再写死) ② 重跑幂等硬判据 (重跑后盘面页要么逐字节不变, 要么只多 B32 一条且九处订正 anchor 一处不少) ③ 作业包 §3-S1 的位号真源指针改对 (`SCHEMATIC_V1_SPEC.json` 没有 devices 段 ⇒ 真源 = `HW/netlist_v1_pins.csv`) ④ 「收工后同一次重锚 + 新闸跑绿」写成收工清单强制项** ★ ⇒ ★**零写板 · 零落表 · 不许碰 ISS-289 那道闸** ★

---

### ★③ ★★待拍板面: 43 ⇒ **44 条** (★新增 1 条, 其余 43 条一条不动★) ★★

#### ★★§A-补20-① · ★★`boss_c_vbus_gnd_reserve_pad_20261117` (★★★ 新增第 44 条 · 一行回复即可 ★★★) ★★

★**★事实 (★main 2026-11-17 16:0x 本机实读★)★**:
- ① ★**网表 `HW/netlist_v1.csv:10` 与 `:12` 两行的 board 列 = `CHG_BOARD`** ⇒ 生成器按 `BOARD_FILTER="MAIN_PCB"` 把它剔掉 ⇒ ★**重新生成的板里它会自然消失** ★
- ② ★**但现役官方板上有它的实物封装 @ (107.70, 42.50)** ⇒ 这就是 `check_pcb_nets.py` 报的「★**C1 多余 2**★」(它的 pad1/pad2) ★
- ③ ★**BOM L51 自己写着「板上有位置但首版不贴」** ⇒ 它本来就是【预留位】 ★
- ④ ★**作业包 §3-S2 的判据是「C1 多余 0」** ⇒ ★**⇒ 那一趟收工后它是 185 件 (下板) 还是 186 件 (留位)** ★

| 选项 | 事实/代价 | ★**建议默认值 (★仅供参考·不代你拍★)** ★ |
|---|---|---|
| ★**① 下板 (收工 185)** ★ | ★**S2 判据直接过** · 失去一个 π 滤波电容的预留焊盘 (★demo 板 Type-C 供电 · 不装电池 · 充电板不在本板上 ⇒ 这颗电容在 demo 上本来就没用★) · **网表一个字节不用改** ★ | ★★**下板 (收工 185)** ★ ★⇒ 理由 = S2 判据已是「C1 多余 0」· 网表已划给 CHG_BOARD · demo 上无用途 · 留位反而多一次落表 churn ★ |
| ★**② 留位 (收工 186)** ★ | ★要【改网表 board 列 CHG_BOARD→MAIN_PCB + 重生成脚表/BOM】⇒ 动板那趟之前多一次落表 · 且要一并处理「C1 多余 2」的判据 ★ | (★不推荐, 但可行★) ★ |

> ★**★不拍的代价 (★这条为什么必须你定, 我不代拍★)★**: ★**那一趟收工时 S2 必假红 (任务书写 185 还是 186 不定 ⇒ 两个数互卡) ⇒ 谁都会想「改板凑绿」⇒ 最坏 = 把 `C_VBUS_GND` 装回板上 = 2-4 周 + ¥4-8K 返工** ★
> ★**★⇒ 回一句「C_VBUS_GND 下板」或「C_VBUS_GND 留位」即可, 我代录落账★** ★

---

### ★④ hw-lead 交卷单里的 4 条拍板项 (★P1~P4 的去向★)

| # | 内容 | ★**去向** ★ |
|---|---|---|
| ★P1 ★ | 那一趟任务书里封装数写几个 | ★**main 自己定 (不用你拍)**: 写两个数 **186 → 185** + 注明差的那 1 件是谁 ★ |
| ★P2 ★ | `C_VBUS_GND` 预留位留不留 | ★**→ 新增第 44 条给你 (见 §A-补20-①)** ★ |
| ★P3 ★ | 「收工后重锚」要不要设成硬门 | ★**main 自己定 (不用你拍)**: 设 ⇒ 已写进 ISS-292 的 B4 (收工清单强制项 + 三条最危险重锚值 + 警告「不许为让闸绿把 C_VBUS_GND 装回板上」) ★ |
| ★P4 ★ | 清单页生成器谁对齐 | ★**已派单 = ISS-292 (hw-lead, 在飞)** ★ |

---

### ★⑤ rc 与本轮派活口径 (★main 16:0x 实跑·原样★)

| 项 | 值 |
|---|---|
| ★`state/merge.py` ★ | ★**rc=0** (完整) ★ |
| ★`state/gate_check.py` ★ | ★**rc=0** (Q1 18/18) ★ |
| ★`state/issue_check.py` ★ | ★**rc=0** (问题闭环门全过) ★ |
| ★`state/stage_gate.py` ★ | ★**rc=1** (★当前 G1 · 缺 1 项 = PCB 布线 unconnected=45 需 0 ⇒ ISS-181 · G1a 还差 G1a-4 / G1a-8★) ★ |
| ★`state/daily_check.py` ★ | ★**rc=3** (★异常已记录非崩溃: ① 板↔网表逐焊盘等价没过 ② 投产包比源旧 ⇒ 都是「板只改一次」那一趟要一次做完的事★) ★ |
| ★**internal / approvals / decisions / waiting** ★ | ★**0 / 0 / 44 / 0** (★三个总工名额全满: ISS-290 mech-lead 在飞 · ISS-291 sw-lead 在飞 · ISS-292 hw-lead 在飞★) ★ |

> ★**★一句话**: ★**板那一趟仍是唯一的大头 ⇒ 它必须一次做完 ⇒ ⇒ 在它之前, 一切零写板、零落表、零改网表真源★** ★
> ★**★本 job (每 20 分钟) 不推 GitHub (★由独立 5 小时同步 job 负责★) · 本轮只落本地快照 (`PROGRESS_SNAPSHOT.md` 已生成)★** ★
"""


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(PAGE, encoding="utf-8") as f:
            old = f.read()
        if "§A-补20" in old:
            print("· §A-补20 已存在 ⇒ 幂等跳过")
            return
        shutil.copy2(PAGE, BAK)
        new = old.rstrip("\n") + "\n" + BLOCK
        tmp = PAGE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, PAGE)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("· §A-补20 已追加")
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
