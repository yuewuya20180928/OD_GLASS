#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 22:5x · job fb67af40「ARS45 队列自动派活」
★★ISS-299 验收签字落地 (fixing → verified) + 新开 ISS-301 → hw-lead★★
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘 + 自己跑命令, 不抄任何 agent 交卷报告★)**:
· ★**ISS-299 (hw-lead · cont1) 的子会话已正常结束**:
  `agent:hw-lead:subagent:018e190a` (sessionId 5ee180f5) · 22:34:44 → 22:39:31 · runtime 285s
  · status=**done** · abortedLastRun=false ⇒ ★**不是僵尸 · 是【干完了但没人签字】** ★
  ⇒ ★**上一轮 22:2x 那次是僵尸 (status=timeout / 父 run 被掐 ⇒ 子被连带杀) ⇒ 本轮它自己跑完了** ★
· ★**main 本轮独立复核 (★全部本机实跑, 不采信自述★)**:
  - `HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md` = **23,417 B** · mtime **2026-11-17 22:38:31.996004918**
    (★agent 自述 23,417 B / 22:38:31.996 ⇒ **逐位一致**★)
  - ★**真判据 (★不是 `check_report_placeholders.py`★)**:
    `grep -nE "🔄|待填|★\(回归跑完后现场填入\)★" <交卷单>` ⇒ **grep_rc=1 ⇒ 0 行命中 ⇒ 通过** ★
  - `python3 HW/check_pin_function_labels.py --expect-known` ⇒ **rc=0** (★快照 15 / 实算 15 · 15/15 逐条一致★)
  - `python3 HW/check_pin_function_labels.py --selftest` ⇒ **rc=0** (★13 条既有 + 10 条通道反向用例 全过★)
  - `python3 HW/check_pin_function_labels.py` (默认) ⇒ **rc=1** 且 **恰好 15 条缺陷** = 既有冻结缺陷基线 (★不是回归★)
  - `grep -c iss299 state/fragments/hw.yaml` ⇒ **10** (★分片已齐★)
  - ★**受保护 5 件逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`)
    · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07`
    · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表 成立** ★
· ★**⇒ ISS-299 = 真完工 ⇒ main 验收签字 ⇒ fixing → verified (★签字人是 main, 不是干活的人★)** ★
· ★**★ISS-299 卡在 `fixing` 的副作用 (★本 job 必须清★)**: ★**hw-lead 的唯一名额被它占着**
  ⇒ ★**`advance.py` 的 in_flight 判据把 hw-lead 名下所有 open 单全挡住** ⇒ ★**队列真空**
  ⇒ ★**⇒ 这就是「让内部待办不断线」被卡住的真实原因 (★不是没活, 是名额被一个已完工的单占着★)** ★
★**★本轮新开 ISS-301 → hw-lead (★理由: 名额释放后不能空着, 且主线内有一件真活★)**:
  - ★**ISS-095 / ISS-102 两条自 11-16 起卡在 `fixed`** (owner=main · **verify_by=hw-lead** · due 11-19)
    ⇒ ★**`HW/TI_POWER_FACTS.md` 是 main 自产的 [官网] 事实卡, 按铁律「自己产的必须别人验」至今没人验过** ★
  - ★**main 22:5x 实测到卡里自己承认的唯一残余 [0数据]**: 「SoM (Forlinx RK3572 模组) 有没有把这两个球引出来」
    ⇒ ★**main 已先查一步**: `HW/PCB/FET3572C_PIN_TABLE.csv` L101 `P1,100,B28,USB_DRD1_VBUSDET` ·
    L216 `P3,16,1C18,USB_DRD0_VBUSDET` ⇒ ★**SoM 两颗球都引出来了 ⇒ 网表 L439 那条 [官网] 断言成立
    ⇒ 【板只改一次】那一趟的 S6 布局清单里 `R_VBUS_DET_D1`/`R_VBUS_DET_D2`/`C_DET_VBUS_D` 三件【不用动】**
    ⇒ ★**但结论仍要 hw-lead 独立复核并补齐证据链 (★自己产的必须别人验★)** ★
  - ★**本单 = 纯分析 + 复核类 ⇒ 零写板 · 零落表 · 零改网表真源 ⇒ 合 11-17 00:43 主线口径规则 ①** ★
★**不碰**: 板 / 网表 / 脚表 / BOM / `HW/TI_POWER_FACTS.md` 本体 / 任何分片 / 决策页 / outbox /
          兄弟 job 的任何单 (★ISS-300 在飞, mech-lead 真在跑 ⇒ 一律不碰★) / 任何闸本体
★**铁律**: 干活的人不许自签 ⇒ ISS-301 的 verify_by=main; ISS-095/ISS-102 的签字由 main 在收到 ISS-301 交卷后落
"""
import fcntl
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

BRIEF_FILE = "state/dispatch_briefs/ISS-301_hw_ti_power_facts_counterverify.md"

VERIFY_299 = """★main (moli) 2026-11-17 22:5x 独立验收签字 (★本机实跑, 不采信 agent 自述★)

★**① 交卷单**: `HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md` = **23,417 B** · mtime **2026-11-17 22:38:31.996004918** ⇒ 与 agent 自述逐位一致。
★**② 真判据 (★不用 `check_report_placeholders.py` —— 它抓不到 `🔄 待填` / `★(…填入…)★` 这两种形态★)**:
`grep -nE "🔄|待填|★\\(回归跑完后现场填入\\)★" <交卷单>` ⇒ **grep_rc=1 ⇒ 0 行命中 ⇒ 通过**。
★**③ 闸读数 (★现场 rc 原样★)**:
· `python3 HW/check_pin_function_labels.py --expect-known` ⇒ **rc=0** (★快照 15 / 实算 15 ⇒ 15/15 逐条一致★)
· `python3 HW/check_pin_function_labels.py --selftest` ⇒ **rc=0** (★13 条既有 + 10 条通道反向用例 全过★)
· `python3 HW/check_pin_function_labels.py` (默认) ⇒ **rc=1** 且 **恰好 15 条缺陷** = 既有冻结缺陷基线 (★不是回归★)
★**④ 分片**: `grep -c iss299 state/fragments/hw.yaml` ⇒ **10** ⇒ 分片已齐 (claims/needs/artifacts 均已登记)。
★**⑤ 受保护 5 件 (★md5 + mtime 双重自证★)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表 成立**。
★**⑥ 会话**: `agent:hw-lead:subagent:018e190a` (sessionId 5ee180f5) · 22:34:44 → 22:39:31 · runtime 285s · status=**done** · abortedLastRun=false ⇒ **正常完工, 非僵尸**。

★**判定: PASS ⇒ ISS-299 落 `verified`** (★签字人 = main, 干活的人没自签★)
★**遗留 (★不阻断本单, 留给下一单★)**: 卡里那 15 条脚表功能缺陷本身**仍未修** (★冻结快照基线·不是本单目标★) ⇒ 已另由 ISS-301 复核链承接说明 (★hw-lead 自报 need `iss299_hw_remaining_15_pin_defects_still_open`★)。
"""


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① ISS-299 验收签字 ----------
        it299 = by_id.get("ISS-299")
        if it299 is None:
            print("⚠ ISS-299 不存在 ⇒ 中止")
            return 1
        if it299.get("status") == "verified":
            print("✔ ISS-299 已是 verified ⇒ 幂等跳过")
        elif it299.get("status") == "fixing":
            it299["status"] = "verified"
            it299["verify_by"] = "main"
            it299["verify_result"] = VERIFY_299
            it299["verify_date"] = TODAY
            it299["note"] = (it299.get("note") or "") + (
                "\n\n★2026-11-17 22:5x (cron fb67af40) ★main 验收签字 ⇒ 落 `verified` ★"
                "\n★依据 = 本机实跑 (交卷单 23,417 B / 22:38:31.996 · 真判据 grep 0 行命中 · "
                "--expect-known rc=0 (15/15) · --selftest rc=0 (13+10) · 默认 rc=1 恰好 15 条既有缺陷 · "
                "分片 grep -c=10 · 受保护 5 件 md5+mtime 逐字节不变) ★"
                "\n★⇒ **hw-lead 名额释放** (★此前它以 fixing 占位 ⇒ advance.py 的 in_flight 把 hw-lead 名下所有 open 单全挡住★) ★"
            )
            print("✔ ISS-299 fixing → verified (main 签字)")
        else:
            print("⚠ ISS-299 status=%s (既不是 fixing 也不是 verified) ⇒ 不动" % it299.get("status"))

        # ---------- ② 新开 ISS-301 ----------
        brief_path = os.path.join(PROJ, BRIEF_FILE)
        if not os.path.exists(brief_path):
            print("⚠ 缺 brief 文件 ⇒ 中止: %s" % brief_path)
            return 1
        with open(brief_path, encoding="utf-8") as f:
            brief = f.read()

        if "ISS-301" in by_id:
            print("✔ ISS-301 已存在 ⇒ 幂等跳过 (status=%s)" % by_id["ISS-301"].get("status"))
        else:
            issues.append({
                "id": "ISS-301",
                "title": ("★★[主线内·HW 侧·复核类+残余事实类·零写板] ★★【复核 main 自产的 `HW/TI_POWER_FACTS.md` 四条 [官网] 结论 "
                          "⇒ 给 ISS-095 / ISS-102 两条卡在 `fixed` 的单交签字依据】★★ ⇒ ★**其中卡里自承的唯一残余 [0数据] "
                          "(★Forlinx SoM 引不引出两颗 USB VBUS detect 球★) 是【板只改一次】那一趟的板侧输入, 必须现在答掉** ★ ⇒ "
                          "★**零写板 · 零落表 · 零改网表真源** ★"),
                "severity": "medium",
                "source_blocker": None,
                "source_agent": "main",
                "owner": "hw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-19",
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": ("2026-11-17 22:5x 队列自动派活 job (fb67af40) 新开 ★★\n"
                         "★**派活依据 = main 2026-11-17 22:4x~22:5x 本机实跑** (★不抄任何 agent 报告★)\n"
                         "★**① 名额**: ISS-299 交卷后由 main 验收落 `verified` ⇒ hw-lead 名额释放 ⇒ "
                         "★**但零写板的 PCB 侧复核类活不能空着 (★主线 = 画 PCB 图 ⇒ 规则 ① 先派纯分析/复核类★)**\n"
                         "★**② 两条卡住的单**: ISS-095 / ISS-102 自 11-16 起卡在 `fixed` (owner=main · verify_by=hw-lead · due 11-19) "
                         "⇒ ★**`HW/TI_POWER_FACTS.md` (7,765 B) 是 main 自产的 [官网] 事实卡, 按铁律「自己产的必须别人验」至今没人验过** ★\n"
                         "★**③ 唯一残余 [0数据]**: 卡 L61 自承「SoM 有没有把这两个球引出来, 本卡无法判定」⇒ "
                         "★**main 22:5x 实测 `HW/PCB/FET3572C_PIN_TABLE.csv` L101 `P1,100,B28,USB_DRD1_VBUSDET` · "
                         "L216 `P3,16,1C18,USB_DRD0_VBUSDET` ⇒ 两颗球 SoM 都引出来了 ⇒ 网表 L439 那条 [官方] 断言成立 ⇒ "
                         "【板只改一次】那一趟的 S6 布局清单里 `R_VBUS_DET_D1`/`R_VBUS_DET_D2`/`C_DET_VBUS_D` 三件【不用动】** ⇒ "
                         "★**但结论仍要 hw-lead 独立复核 + 补齐证据链 (★自己产的必须别人验★)** ★\n"
                         "★**④ 顺带要判的规格张力**: TI 说 BQ25896 的 SYS 必挂 20µF, 而网表 L499 `C_SYS` = DNP (★依据「本板 SYS 无负载」这条 PM 裁决★) "
                         "⇒ ★**只出事实与代价, 不代拍 (★C_SYS 归属 CHG_BOARD, 不在 demo 主 PCB 上★)** ★\n"
                         "★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM/`HW/TI_POWER_FACTS.md` 本体 · 零改闸 · 零外发 · 不自签 issue_log "
                         "(★ISS-095/ISS-102 的签字是 main 的活★)"),
                "dispatched_at": None,
                "task_brief": brief,
            })
            print("✔ 新开 ISS-301 (owner=hw-lead · status=open · brief %d B)" % len(brief))

        with open(LOG, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        print("✔ issue_log.yaml 已落盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
