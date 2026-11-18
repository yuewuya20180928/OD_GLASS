#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0835_verify229.py
★main (moli) · 2026-11-16 08:3x · cron 775d9893 继续执行后继计划★

★★**做什么: 把 ISS-229 (mech-lead) 从 fixing 落 verified —— main 独立复核签字★** ★★

★★**为什么是这一条 (★不是抢兄弟 job 的活★)** ★★
· ★**兄弟 job「ARS45 队列自动派活」(fb67af40, :07/:37) 在 08:2x 清僵尸时明写**:
  「① 真交卷只差推状态 ⇒ main 独立复核后落 verified (★本轮 ISS-229 属这类:
  HANDOFF 63194 B + 7 道闸全 rc=0 + 分片 07:49 ⇒ ★**它不是僵尸, 本 job 没碰它,
  留给兄弟 job 775d9893 清账★**)」 ⇒ ★**本单 = 兄弟 job 明确交接给本 job 的账★**
· ★**为什么必须清**: ISS-229 卡着 **mech-lead 的唯一写会话名额** (status=fixing ⇒ advance.py
  的 in_flight 判据挡住 mech-lead) ⇒ 不清 ⇒ mech-lead 名额永久被"已交卷但没签字"占着
  ⇒ A 段 (internal) 永远开不出来 ⇒ ★**这正是 ISS-237 备注里说的「等 hw-lead 名额空出来」同类死锁★**

★★**本轮 main 独立复核 (★不采信子 agent 自述★, 自己实跑, 2026-11-16 08:3x)** ★★
  · MECH/hinge_power_calc.py → **rc=0**
  · MECH/verify_budget.py → **rc=0** (53/53 项与文档一致 + 口径自检 12/12)
  · MECH/cavity_recalc_check.py → **rc=0** (23/23 组通过)
  · MECH/cavity_recalc_check.py --selftest → **rc=0** (27/27 反向用例全抓到 ⇒ 不是假绿)
  · MECH/check_demo_struct_truth.py → **rc=0** (23/23 组通过 · FAIL 0 组)
  · MECH/check_demo_struct_truth.py --selftest → **rc=0** (14/14 全抓到)
  · 交付物在盘: HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md
    (**63194 B** · mtime 07:50 · **B1~B6 六块齐** · 实 grep 到 6 个 B 段标题)
  · 分片真落盘: state/fragments/mech.yaml 实 grep 到 **5 个 iss229 key**
    (iss229_mech_charge_skin_temp_scope_to_main / iss229_mech_hw_pcb_outline_old_charge_numbers /
     iss229_mech_sw_evt_pwr05_charge_current_criterion / iss229_hw_landing_must_sync_mech_anchor_iss233 /
     iss229_mech_v4_update_package_and_gate_reanchor)
  · 受保护 md5 逐字节未变: 板 **611b869e13518c3c023fb178f91a0075** ·
    .kicad_pro **3e504d2be83152e337949723e909be1b** · 网表 **34132f7e40a241e1fae1476be0eafbd5** ·
    脚表 **b21b743a7702d30729f0d653c15392df** (★网表/脚表 = ISS-233 06:48 落表后的值, 不是本单改的★)

★★**main 复核后确认的关键结论 (★数字是本轮自己从盘上脚本实跑出来的★)** ★★
· ★**`ICHG_FACTOR 0.822` = (Vbat/Vbus)/eta = `η·Vbus/Vbat` 的【倒数】⇒ 方向反了 ⇒ 电流偏小
  ⇒ 发热偏小 ⇒ 温度偏乐观 ⇒ 「390Ω 档 42.14 °C」= 无有效数字** ⇒ 活系数 = **1.216 @3.70V** /
  **1.071 @4.20V** (取最坏 = Vbat 最低) ⇒ 皮肤侧 **390Ω 档 42.1 → 50.6 °C ❌** ·
  470Ω **45.8 °C ❌** · **680Ω 40.1 °C ✅** · 1.2kΩ **36.7 °C ✅**
· ★**三条同向硬约束**: ① 皮肤侧 43 °C ② 单 pin ≤0.5 A 触点额定 ③ TS 停充门限偏差 ≤1 °C
  ⇒ 唯一杠杆 = `R_ILIM` 换料不换板 (加厚铜箔不能替代降档: 470Ω max 即便 2oz 仍 44.1 °C ❌)
· ★**本单没有代拍 V-4** (只出依据 + 推荐 + 降级) ⇒ V-4 仍在老板拍板桶里

★★**边界 (本脚本严格守住)** ★★
· ★**只改 ISS-229 一条的 status + verify_result + verify_by + verify_date + note 追加** ★
· ★**不碰**: 任何分片 (pm/hw/sw/mech.yaml 一个字节没动) · 任何真源文件 (板/网表/脚表/原理图/BOM) ·
  `PROJECT_TRACKER.md` §0 · `state/outbox/` · 决策页 · 别人的 issue 条目
· ★**零外发** (微信通道 2026-11-11 10:17 已删 ⇒ 本 job 连 message 工具都不许调) ·
  ★**零 PCB 触碰** (板 md5 一个字节没动) · ★**零替老板拍板** ★
· ★**锁**: flock(state/.issue_log.lock) + 锁内重读 + 原子写 (tmp + fsync + os.replace)
  ⇒ ★**不与兄弟 job 的 issue_log 写竞争** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0835_verify229"

VERIFY_RESULT = (
    "★main 独立复核通过 (★2026-11-16 08:3x, 只看盘上实物 + 自己实跑门禁, 不采信子 agent 自述★):\n"
    "  · MECH/hinge_power_calc.py → rc=0\n"
    "  · MECH/verify_budget.py → rc=0 (53/53 项与文档一致 + 口径自检 12/12)\n"
    "  · MECH/cavity_recalc_check.py → rc=0 (23/23 组通过)\n"
    "  · MECH/cavity_recalc_check.py --selftest → rc=0 (27/27 反向用例全抓到 ⇒ 不是假绿)\n"
    "  · MECH/check_demo_struct_truth.py → rc=0 (23/23 组通过 · FAIL 0 组)\n"
    "  · MECH/check_demo_struct_truth.py --selftest → rc=0 (14/14 全抓到)\n"
    "  · 交付物在盘: HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md (63194 B, 07:50 · B1~B6 六块齐)\n"
    "  · 分片真落盘: state/fragments/mech.yaml 实 grep 到 5 个 iss229 key\n"
    "  · md5 逐字节未变: 板 611b869e13518c3c023fb178f91a0075 · .kicad_pro 3e504d2be83152e337949723e909be1b · "
    "网表 34132f7e40a241e1fae1476be0eafbd5 · 脚表 b21b743a7702d30729f0d653c15392df\n"
    "★**main 复核后的关键结论**: ① `ICHG_FACTOR 0.822` 是 `η·Vbus/Vbat` 的【倒数】⇒ 方向反了 ⇒ "
    "「390Ω 档 42.14 °C」无有效数字 ⇒ 活系数 1.216 @3.70V / 1.071 @4.20V ⇒ 皮肤侧 390Ω 42.1→50.6 °C ❌ · "
    "470Ω 45.8 °C ❌ · 680Ω 40.1 °C ✅ · 1.2kΩ 36.7 °C ✅ "
    "② 三条同向硬约束 (皮肤 43 °C / 单 pin ≤0.5 A / TS 偏差 ≤1 °C) ⇒ 唯一杠杆 = R_ILIM 换料不换板 "
    "③ 本单【没有代拍 V-4】(只出依据 + 推荐 + 降级) ⇒ V-4 仍在老板拍板桶里 "
    "④ 板端 [实测] = 0 条 (板不在本机) ⇒ 热学数一律 [推算] ★",
    "2026-11-16 08:3x",
)

NOTE_TAIL = (
    "\n2026-11-16 08:3x (cron 775d9893 继续执行后继计划) ★**main 独立复核后落 verified · 清 mech-lead 名额** ★\n"
    "★**依据 (自己实跑, 不采信自述★)**: hinge_power_calc rc=0 · verify_budget rc=0 (53/53 + 12/12) · "
    "cavity_recalc rc=0 (23/23) + --selftest rc=0 (27/27) · check_demo_struct_truth rc=0 (23/23) + "
    "--selftest rc=0 (14/14) · 交接单 63194 B / B1~B6 齐 · 分片 5 个 iss229 key 真落盘 · "
    "板/网表/脚表/.kicad_pro md5 逐字节未变 ★\n"
    "★**为什么现在清 (★兄弟 job fb67af40 08:2x 明确交接给本 job★)**: 兄弟 job 清僵尸时明写 "
    "「ISS-229 属【真交卷只差推状态】那类 ⇒ 不是僵尸 ⇒ 留给兄弟 job 775d9893 清账」 ⇒ ★**本条 = 交接账** ★\n"
    "★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 mech-lead "
    "⇒ **mech-lead 唯一写会话名额被『已交卷但没签字』永久占着** ⇒ A 段 (internal) 开不出来 ★\n"
    "★**清账后 mech-lead 名额释放** (★该 agent 名下 open = 0 ⇒ 释放后本轮仍无可派, 下一轮有单即自动可派★) ★\n"
    "★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note · 零外发 · 零 PCB 触碰 · "
    "零代拍 V-4 · 没碰任何分片 / 真源文件 / 决策页 / outbox ★"
)


def main() -> int:
    os.makedirs(HERE, exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, "r", encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log.get("issues") or []
        hit = 0
        for it in issues:
            if it.get("id") != "ISS-229":
                continue
            hit += 1
            it["status"] = "verified"
            it["verify_result"] = VERIFY_RESULT[0]
            it["verify_by"] = "main"
            it["verify_date"] = VERIFY_RESULT[1]
            it["note"] = (it.get("note") or "") + NOTE_TAIL
        assert hit == 1, "ISS-229 not found (hit=%d)" % hit
        shutil.copy2(LOG, BAK)
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.tmp.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("OK: ISS-229 → verified (bak: %s)" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
