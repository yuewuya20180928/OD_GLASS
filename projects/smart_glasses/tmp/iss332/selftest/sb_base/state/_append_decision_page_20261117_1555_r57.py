#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_decision_page_20261117_1555_r57.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 15:5x★
★★**追加式 (★老字一行不删★)**: DECISION_PENDING_2026-11-16.md §A-补19 ★★

★★**本节内容 (★全部 main 本机实跑·不抄任何交卷报告★)★★ ★★
· ★**① 本轮内部推进**: ISS-288 (sw-lead) 由 main 复验落 verified (★数字齐★) · ISS-291 (sw-lead) 新开并派出
  (★本轮唯一合法可派的一条★) · ISS-289 (hw-lead) 在飞 · ISS-290 (mech-lead) 在飞
· ★**② 待拍板面 = 43 条 (★与 r56 同·一条不多一条不少★)**: ★**新增第 3 条【知会型】**
  `boss_adc_fullscale_domain_notice_20261117` —— ★**★同一分压链在网表与 SW 闸里差 7 倍 (2.1% FS vs 15.2%)★★**
  ⇒ ★**不需要你拍任何值**, 但你要知道「板那一趟之前必须先把这条口径钉死, 否则板会白改第二遍」★
· ★**③ 阶段门 / 链门 / 巡检 rc**: ★**G1 · G1a 还差 2 条 (G1a-4 / G1a-8) · merge rc=0 · gate_check rc=0 (Q1 18/18) ·
  issue_check rc=0 · stage_gate rc=1 (★缺 1 项 = PCB 布线 unconnected=45 ⇒ ISS-181★) · daily_check rc=3 (★板面比网表旧·
  投产包比源旧 ⇒ 预期红★)★** ★
· ★**④ 本 job 派活口径 (★`state/advance.py --json` 实跑·原样★)**: internal=1 (ISS-291) / approvals=0 / decisions=43 / waiting=0 ★

★★**边界 (★写死的)★★ ★★
· ★**只追加, 老字一行不删不rewrite** ★ · ★**先备份 (★`DECISION_PENDING_2026-11-16.md.bak_20261117_1555_r57`★)** ★
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
BAK = PAGE + ".bak_20261117_1555_r57"

BLOCK = """
---

## §A-补19 · ★★r57 · 2026-11-17 15:5x · ★★★**待拍板面 43 条 (与 r56 同) + 新增 1 条知会 + 本轮派活口径**★★★ (★cron 775d9893 本机实跑★)

> ★**出页人**: 项目总工 (main / moli) · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**15:5x 实跑·追加式·老字一行不删★**
> ★**本节给你一件事**: ★**一条知会 (★不需要你拍值★)** ★**—— 同一个电池分压链, 网表说 2.1% FS, SW 闸算 15.2% FS, 差 7 倍★** ★

---

### ★① 本轮内部推进 (★五单状态 · main 本机实查★)

| 单号 | owner | 状态 | main 15:4x~15:5x 实查 |
|---|---|---|---|
| ★**ISS-288** ★ | sw-lead | ★**verified** ★ | ★**已由 main 独立复验收口** (★不是抄交卷报告★): `python3 SW/tools/timing_check.py` ⇒ **rc=0 · 末行 `SELFTEST 72/72 通过, rc=0`** (★开工前 rc=1 · 68/71 三条红★) · 补丁 md5 `68c4becffe6bcd708e388dba9d18a505` (= ISS-285 写死的期望值, 逐字一致) · 交卷单 555 行 / 43335 B / md5 `e6662435a1671dada9793b5c03470168` · 分片 artifacts 3 + claims 3 + needs 2 ⇒ **零写板 · 零落表 · 交付物齐** ★ ⇒ ★**sw-lead 名额空出来** ★ |
| ★**ISS-289** ★ | hw-lead | ★**fixing · 在飞** ★ | ★**续做 cont1 会话 `agent:hw-lead:subagent:1e68b706` running** (★交卷单 B0~B6 + 回归验收贴 rc★) ⇒ ★**本 job 不重复派第二个 hw-lead 会话** ★ |
| ★**ISS-290** ★ | mech-lead | ★**fixing · 在飞** ★ | ★**结构侧交叉核对会话 `agent:mech-lead:subagent:cedabf25` running** ⇒ ★**本 job 不重复派第二个 mech-lead 会话** ★ |
| ★**ISS-291** ★ | sw-lead | ★**★新开 · 本轮已派出★★** ★ | ★**《SW 侧 ADC 判据的【判决对象 + 满量程口径】双错》** ⇒ 会话 `agent:sw-lead:subagent:b0a6d0ff` · 任务书 `state/dispatch_briefs/ISS-291_sw_adc_fullscale_domain_reconcile.md` (★已过 `check_brief_commands --brief-file` rc=0★) ⇒ ★**纯判据口径 + 机器闸 · 零写板 · 零落表 · 零改 `HW/`** ★ |

> ★**⇒ 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro 3e504d2be83152e337949723e909be1b` / 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` 本 job 15:4x 逐字节未变 ⇒ ★**「板只改一次」铁律本轮未破** ★

---

### ★② ★★新增知会项 (★第 3 条 · r56 的 43 条一条没动★) ★★

#### ★★§A-补19-① · ★★`boss_adc_fullscale_domain_notice_20261117` (★★★ 知会型 · 不需要你拍值★★★) ★★

★**★事实 (★main 15:4x~15:5x 本机实读 + 实跑, 逐条带行号★)★**:

| # | 事实 | 出处 (逐字) |
|---|---|---|
| ① | ★**SW 闸把 SoM ADC 满量程写死 3.3V** ★ | ★`SW/tools/timing_check.py:81` `"V_DET_FS": 3.3,  # V   SoC ADC 满量程 (3.3V 域)`★ |
| ② | ★**官方是 1.8V 域 (12 bit)** ★ | ★`HW/PCB/FET3572C_PIN_TABLE.csv:39` `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` + 官方 datasheet `:2454` `SARADC_AVDD1V8 1.62 1.8 1.98 V` · `:2864` `Anglog Input Range AIN AVSS18 NA AVDD18 V`★ |
| ③ | ★**网表自己写的是 1.8V FS 口径** ★ | ★`HW/netlist_v1.csv:182` note: 「R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (**2.1% FS**, 可软件标定)」★ |
| ④ | ★**⇒ 同一个 BAT_DET 分压链: 网表 2.1% FS vs SW 闸 15.2% FS (差 7 倍)** ★ | ★**两源不同 ⇒ 错的是 SW 闸** ★ |
| ⑤ | ★**更要命的是【判错了对象】**: F4 取链规则 = 「元组顺序第一条 populated」⇒ 判的是 `VBUS_DET_D` (1M+1M), 而它落到 `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` = ★**USB 插入检测数字脚**★; 真正接 ADC 的 `BAT_DET` (→ pin38 = `SARADC_VIN5`) ★**一条判据都没有**★ ⇒ ★**现在这条红是「假红」, 而真 ADC 链处于无判据状态**★ | ★`HW/netlist_v1.csv:439` vs `:186` + `FET3572C_PIN_TABLE.csv:101`★ |

★**★为什么这条要你知道 (★就这一句★)★**: ★**板是照着网表画的 ⇒ 如果带着这条口径分歧去改板, 改完闸还是红的 ⇒ 板要白改第二遍 ⇒ ⇒ 所以这一条必须在「板只改一次」那一趟【之前】钉死★** ★

★**★处置 (★不需要你介入★)★**: ★**已开 ISS-291 派给 sw-lead (★会话在飞★)**: 把满量程口径改成 1.8V (带官方出处) + 取链规则改成「按落点是不是 SAR-ADC 脚判」+ 反向用例 + ★**改完 F4 的漏电偏移 %FS 必须与网表 note 逐字对上 (2.1%)** ★ ⇒ ★**若分析结论指向硬件必须改 (★例: VBUS_DET_D 的 2.5V 电平★)⇒ 只登记 need 给 main, 由我并进「板只改一次」那一趟 ⇒ 不改网表真源** ★

> ★**★⇒ 这条是「知会」, 不是「拍板」: 你不用出任何值。★** ★**唯一请求 = 「已知悉」** ★

---

### ★③ 阶段门 / 链门 / 巡检 (★main 15:5x 本机实跑·原样 rc★)

| 命令 | rc | 事实 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★**完整** ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★**Q1 = 18/18** ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★**问题闭环门全过** ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★**当前 G1 (原理图 / PCB 定稿) · 缺 1 项** ⇒ ★**PCB 布线 unconnected=45 需 0 (DRC 已 0) ⇒ ISS-181** ★ · ★**G1a (原理图侧) 还差 2 条 = G1a-4 (板侧 ESD 落表) + G1a-8 (★= §A-补18① 的 A4/A5·你一句话★)** ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★**异常已记录 (非崩溃)**: ★**① PCB↔网表逐焊盘等价没过 (板面比网表旧 ⇒ 板不许投) ② 生产链准入/准出没过 (投产包比源旧 ⇒ 下游产物不许用)** ★ ⇒ ★**这两条正是「板只改一次」那一趟要一次做完的事** ★ |

> ★**★一句话**: ★**板那一趟仍是唯一的大头 ⇒ 它必须一次做完 ⇒ ⇒ 在它之前, 一切零写板、零落表、零改网表真源★** ★

---

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 实跑·原样★)

| 段 | 条数 | 事实 |
|---|---|---|
| ★**internal (内部可派)** ★ | ★**1** ★ | ★**ISS-291 → sw-lead (★ISS-288 落 verified 后 sw-lead 名额空出 ⇒ advance.py 复算才把它放出来★) ⇒ 已派 (会话 `agent:sw-lead:subagent:b0a6d0ff`)** ★ |
| ★**approvals (外发待批)** ★ | ★**0** ★ | ★**符合老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ 恒为空 ⇒ 本轮零外发 · 零采购 · 零联系供应商** ★ (★`state/outbox/` 18 份草稿原样留存, 不发★) ★ |
| ★**decisions (待你拍板)** ★ | ★**43** ★ | ★**与 r56 同数 (★41 + r56 的 2★) ⇒ 本节再加 1 条【知会型】⇒ ★**拍板面仍是 43 条, 一条不多一条不少**★** ★ |
| ★**waiting (纯等待)** ★ | ★**0** ★ | —— |

> ★**★本轮 main 自办 (不占任何 agent 名额)★**: ★**ISS-288 独立复验 + 落 verified · ISS-291 开单 + 任务书 + `check_brief_commands` 守卫 + `advance.py --apply --only` 标 fixing + 派活 + dispatch_log + 本决策页追加 + 核验 + 本地快照** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写别的 agent 的分片 (★sw.yaml 里那个已满足的 need 由 sw-lead 自己标★)** ★
"""


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(PAGE, encoding="utf-8") as f:
            old = f.read()
        if "§A-补19" in old:
            print("· §A-补19 已存在 ⇒ 幂等跳过")
            return
        shutil.copy2(PAGE, BAK)
        new = old.rstrip("\n") + "\n" + BLOCK
        tmp = PAGE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(new)
        os.replace(tmp, PAGE)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("· §A-补19 已追加")
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
