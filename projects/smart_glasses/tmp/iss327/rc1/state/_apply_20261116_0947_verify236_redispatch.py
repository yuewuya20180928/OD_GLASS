#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0947_verify236_redispatch.py
★main (moli) 验收签字 · 2026-11-16 09:47 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**ISS-236 (hw-lead) 子会话 `agent:hw-lead:subagent:8718cb66` ★**status=done** ★ (交卷 09:44:55)
  ⇒ ★**main 本轮自己实跑 8 道闸 + 3 道尺子** ⇒ 落 `verified` ⇒ **放掉 hw-lead 名额** ★
· ★**★这一轮特别之处 (★main 09:3x 亲历的【僵尸 fixing 第 21 次复发·新变体】★)★**:
  ★**09:13 兄弟 job (cron fb67af40) 写了续做 brief 但它的 spawn 被中止 (父会话 abort) ⇒ 零会话**
  ⇒ ★**⇒ ISS-236 处于 fixing 却没人干活 ⇒ 连带把 ISS-237 (open, hw-lead) 也堵住了**
  ⇒ ★**⇒ main 09:33 重派 (runTimeoutSeconds=5400 ⇒ 90 分钟, 绕开前几轮 8 分钟默认超时掐死) ⇒ 本轮真交卷** ★

★★**main 09:4x 自己实跑的验收证据 (★一条不抄交卷报告★)★★ ★★
· ★**8 道验收命令全绿**: `HW/check_netlist_selfconsistency.py` **rc=0** · `--selftest` **rc=0 (21/21 通过)** ·
  `--expect-resolved` **rc=1 (18 条未落表 · ★不变·正符合「一个 V 值都不许落」★)**
  · `state/check_netlist.py` **rc=0** · `state/check_netlist_pins.py` **rc=0**
  · `state/check_sch_erc.py` **rc=0 (ERC 违规数 = 0)** · `state/check_sch_pinfull.py` **rc=0 (584 脚全等)**
  · `state/merge.py` **rc=0** · `state/gate_check.py` **rc=0 (Q1 18/18)** ★
· ★**受保护 5 个 md5 逐字节不变 (main 09:44 复测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` ·
  脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` ·
  板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
  ⇒ ★**⇒ 一个 V 值都没落 (★落表器默认 dry-run + `--apply` 必须带 `--boss-decision` = 机器化保证★)** ★
· ★**交付物 3 件在盘 (main 实测)**: `state/land_v_values.py` (83266 B) · `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` (20470 B)
  · `HANDOFF/2026-11-16_hw-lead_ISS236_一键落表器与定稿收口清单.md` (45413 B · **B1~B6 六块齐全** · L13/L39/L60/L406/L438/L451) ★
· ★**收口清单结尾有【还差什么才能定稿】的总数 (★main 实读逐字★)**:
  ★**「老板 3 个值 (V-2/V-3/V-4) → 网表侧转绿 14 条 → 板那一趟转绿 4 条 (CR-14~CR-17 + B-1~B-8) → `--expect-resolved` 18 → 0 ⇒ 原理图定稿」** ★
  + ★**「若老板拍 V-3 = 降级④ ⇒ 下限 = 13 条 ⇒ 原理图【不能】定稿 ⇒ V-3 必须划掉落表清单, 改成挂起 + 归 V-7」** ★
  ⇒ ★**★⇒ 这条【降级④ = 不能定稿】的结论是本单的隐藏价值 (★main 复核后确认成立: 18 条里 V-3 占 13 条, 降级④就是把 BAT_DET 链留 DNP ⇒ 那 13 条永远红⇒ 原理图永远定不了稿★)** ★
· ★**分片已落 (走 frag_write.py 原子写)**: `state/fragments/hw.yaml` artifact 95 条, ★**本单 3 条 artifact 全在**
  (`state/land_v_values.py` tool / `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` breakdown / 交卷单 handoff) ★
· ★**/tmp 副本已还原 (main 实测)**: `/tmp/iss236_root/HW/netlist_v1.csv` md5 = `34132f7e…` = 真盘值 ⇒ ★**副本真落验证做完且已还原** ★
· ★**拍板码映射已对上决策页**: ★**A1 = V-3 · A2 = V-4 · A3 = V-2** ★ (★与 `DECISION_PENDING_2026-11-16.md` §A 的 A1/A2/A3 逐字对应★)

★★**边界 (本脚本)★★ ★★
· ★**只改 `state/issue_log.yaml` 里 ISS-236 一条的 status/verify_result/verify_date/note** ★
· ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** ★
· ★**零外发** · ★**不替老板拍 V-2 / V-3 / V-4** · ★**本单不自签** (verify_by = main) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

VERIFY = (
    "★main 2026-11-16 09:4x 自己实跑 (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**8 道验收命令全绿**: `HW/check_netlist_selfconsistency.py` rc=0 · `--selftest` rc=0 (**21/21 通过**) · "
    "`--expect-resolved` rc=1 (**18 条未落表** · ★不变 ⇒ 正符合「一个 V 值都不许落」★) · "
    "`state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 · "
    "`state/check_sch_erc.py` rc=0 (**ERC 违规数 = 0**) · `state/check_sch_pinfull.py` rc=0 (**584 脚全等**) · "
    "`state/merge.py` rc=0 · `state/gate_check.py` rc=0 (**Q1 18/18**) ★\n"
    "· ★**受保护 5 个 md5 逐字节不变 (main 09:44 复测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` · "
    "脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · "
    "板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★ ⇒ "
    "**⇒ 一个 V 值都没落** (★落表器默认 dry-run + `--apply` 必须带 `--boss-decision` = 「不许替老板拍板」的机器化保证★) ★\n"
    "· ★**交付物 3 件在盘**: `state/land_v_values.py` (83266 B) · `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` (20470 B) · "
    "`HANDOFF/2026-11-16_hw-lead_ISS236_一键落表器与定稿收口清单.md` (45413 B · ★B1~B6 六块齐全★ · "
    "main 实测行号 L13/L39/L60/L406/L438/L451) ★\n"
    "· ★**★【本单最有价值的一条·main 实读逐字】★**: 收口清单 §5 写明 ★**「还差什么才能定稿: 老板 3 个值 (V-2/V-3/V-4) "
    "→ 网表侧转绿 14 条 → 板那一趟转绿 4 条 (CR-14~CR-17 + 板侧同步 B-1~B-8) → `--expect-resolved` 18 → 0 ⇒ 原理图定稿」** ★ "
    "且 ★**「若老板拍 V-3 = 降级④ (BAT_DET 链保持 DNP) ⇒ `--expect-resolved` 的下限 = 13 条 ⇒ 原理图【不能】定稿 "
    "⇒ V-3 必须从落表清单划掉, 改成挂起 + 归 V-7」** ★ ⇒ ★**main 复核确认成立 (18 条里 V-3 占 13 条; "
    "降级④ = 把 BAT_DET 链留 DNP ⇒ 那 13 条永远红 ⇒ 原理图永远定不了稿) ⇒ 这条【降级④ 不能定稿】的结论此前没人写出来过** ★\n"
    "· ★**分片已落 (走 frag_write.py 原子写)**: `state/fragments/hw.yaml` artifact 95 条, ★**本单 3 条 artifact 全在** ★\n"
    "· ★**/tmp 副本已还原 (main 实测)**: `/tmp/iss236_root/HW/netlist_v1.csv` md5 = `34132f7e…` = 真盘值 ★\n"
    "· ★**拍板码映射**: ★**A1 = V-3 · A2 = V-4 · A3 = V-2** ★ (与决策页 §A 逐字对应) ★\n"
    "· ★**零外发** · ★**实物 [实测] = 0 条** · ★**没碰板 / 没碰布线布局 / 没改 SW MECH / 没改 PROJECT_TRACKER §0 / 没自签本条 (verify_by = main)** ★"
)


def main() -> int:
    log = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = log["issues"]
    by_id = {it["id"]: it for it in items}
    it = by_id["ISS-236"]

    # 硬断言: 只能给 fixing 的单落 verified, 且修复人不得自验
    assert it.get("status") == "fixing", "ISS-236 状态不是 fixing, 拒绝改"
    assert it.get("owner") == "hw-lead", "ISS-236 owner 不是 hw-lead, 拒绝改"
    assert it.get("verify_by") == "main", "verify_by 不是 main, 拒绝改"

    it["status"] = "verified"
    it["verify_result"] = VERIFY
    it["verify_date"] = TODAY
    it["note"] = str(it.get("note") or "") + (
        "\n"
        "★**2026-11-16 09:47 (cron 775d9893 继续执行后继计划) main 验收签字** ★\n"
        "★**这一轮的起因 = 僵尸 fixing 第 21 次复发 (★新变体★)**: ★**09:13 兄弟 job (cron fb67af40) 写了续做 brief "
        "(`state/dispatch_briefs/ISS-236_task.txt`, 10550 B) 但它的 `sessions_spawn` 被中止 (父会话 toolResult 逐字 = "
        "\"Aborted\") ⇒ 实测 hw-lead 会话目录 09:1x 之后零新文件 ⇒ 那个 spawn 根本没起来 ⇒ ISS-236 处于 fixing 却没人干活** ★ "
        "⇒ ★**连带把 ISS-237 (open, hw-lead, due 11-19) 也堵住 (in_flight 规则正确工作)** ★ "
        "⇒ ★**main 09:33 重派 (runTimeoutSeconds=5400 ⇒ 90 分钟, ★绕开前 3~4 轮那个 8 分钟默认超时掐死★) ⇒ 本轮真交卷** ★\n"
        "★**main 09:4x 实跑 8 道闸全绿 + 受保护 5 md5 逐字节不变 + 3 件交付物在盘 ⇒ 落 verified ⇒ 放掉 hw-lead 名额** ★\n"
        "★**⇒ 下一轮 hw-lead 名额空出来 ⇒ ISS-237 (P2 屏口径自相矛盾 · due 11-19) 自动可派** ★\n"
        "★**★注意: 落 verified 不等于原理图定稿** ★ —— ★**`--expect-resolved` 仍是 18 条** ★ "
        "(★V-3 13 + V-2+板 3 + V-4 1 + 板侧 R3 1★) ⇒ ★**只等老板拍 A1/A2/A3 三个值 (决策页 §A) + 板那一趟 (按 11-11 10:07 口径排队)** ★\n"
        "★**★特别提示 (★main 09:4x 实读交卷单 §5 后新增的判断★)**: ★**若老板拍 V-3 = 降级④ (BAT_DET 链保持 DNP) "
        "⇒ `--expect-resolved` 下限 = 13 条 ⇒ 原理图【不能】定稿 ⇒ V-3 必须从落表清单划掉 (改成挂起 + 归 V-7)** ★ "
        "⇒ ★**这条是此前没人写出来的 ⇒ 已并进决策页 §A 的 A1 说明 (2026-11-16 09:3x 复核段)** ★"
    )

    shutil.copy2(LOG, LOG + ".bak_20261116_0947_verify236")
    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(LOG, encoding="utf-8"))
    c = {i["id"]: i for i in chk["issues"]}["ISS-236"]
    assert c["status"] == "verified" and c["verify_by"] == "main"
    print("✅ issue_log.yaml 已原子写 (flock + tmp/os.replace):")
    print("   - ISS-236 (owner=hw-lead) fixing → verified · verify_by=main · verify_date=2026-11-16")
    print(f"   - issue 总数: {len(chk['issues'])}")
    print(f"   - 备份: issue_log.yaml.bak_20261116_0947_verify236")
    print("   ★**⇒ hw-lead 名额释放 ⇒ 下一轮 ISS-237 (P2 屏口径) 自动可派** ★")
    print("   ★**⚠ 落 verified ≠ 原理图定稿: `--expect-resolved` 仍是 18 条 (只等老板拍 A1/A2/A3 + 板那一趟)** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
