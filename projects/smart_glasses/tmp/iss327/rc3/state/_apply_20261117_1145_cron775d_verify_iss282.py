#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1145_cron775d_verify_iss282.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 11:4x★
★★**ISS-282: fixing → verified** (★verify_by = main ⇒ 签字是 main 的活★)

★★**本轮实跑结论 (★全部自己实跑, 不抄交卷报告★)★★ ★★
· ★**hw-lead 的 ISS-282 会话 `agent:hw-lead:subagent:e1153379` (cron fb67af40 派) 已于 11:38:41 交卷** ★
  ⇒ 盘上 4/4 交付物齐全 + 分片已写 ⇒ ★**hw-lead 名额释放 ⇒ ISS-283 可派**
· ★**main 本机独立复验 (11:4x 实跑, 原样 rc)★★ ★★
  ① `python3 HW/check_fsin_rootcause.py` ⇒ **rc=0** (★D1~D5 全绿★
     D1 订正页三口径齐全 · D2 重算 1.300000/1.350000 ≥ 0.45 ⇒ escape_stub 不适用 ·
     D3 唯一挡路者 VDD_3V3_IO · 忽略后净距 0.4384 ≥ 0.3950 · D4 老 S8 行 L387 逐字仍在 + 订正行 L388 ·
     D5 受保护 5 件逐字节未变★) ★
  ② `python3 HW/check_fsin_rootcause.py --selftest` ⇒ **rc=0 · 12/12 反向用例全抓到** ★
  ③ ★**受保护 5 件实读**: 板 `611b869e…` (mtime 仍 2026-11-06 07:07:17) · `.kicad_pro` `3e504d2b…` ·
    网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` ★**= 09:58 授权落表 (A1/A2) 后的合法值 (台账 §16.2 L1270~L1272)★**
  ④ 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` = 47467 B · ★**「待填」grep = 0** ★
  ⑤ `state/fragments/hw.yaml` ★**grep -c ISS-282 = 5** (分片已写) ★
  ⇒ ★**判定 pass (★ISS-282 自己的范围: 根因订正页 + 作业包追加式订正 + 机器闸 + 布线前置闸★)★**
· ★**3 条红如实记 (★根因全部与本单无关, 且都不是本单能收的★)** ★★
  · ★**A4 `HW/check_onepass_commit_order.py` rc=1 (D0 红)** = ★**「零落表」硬基线过期** (09:58 授权落表依法改了三个 CSV 的 md5)
    ⇒ 修法 = 该闸的基线挪到落表后真值并引台账 §16.2 ⇒ ★**归 ISS-283 (hw-lead)★** ★
  · ★**A5 `HW/check_onepass_s10_manifest.py` rc=1 (M1 红)** = ★**结构性**: 清单要等 S10 那一趟 (`gen_production_pack.sh`) 生成才在盘
    ⇒ ★**「板只改一次」那一趟才转绿 ⇒ 归那一趟, 改判据就是造假★** ★
  · ★**A6 `MECH/check_onepass_mech_sync.py` rc=1 (M5 红 3 条)** = ★**同 A4 病根** (三个 CSV md5 ≠ 旧基线) ⇒ ★**文件在 MECH/ ⇒ 归 mech-lead★** ★
  · ⇒ ★**这 3 条红的归属与本单无关, 本单【不代改也不装绿】, 已在交卷单里登记成 need★**

★★**本脚本做的事 (边界写死)★★ ★★
· ★**只写 `state/issue_log.yaml` (★flock + 锁内重读 + tmp/os.replace 原子写 + 先备份★)★**
· ★**ISS-282: fixing → verified** (★fix_ref / verify_by=main / verify_result=pass / verify_date / verify_note★)★**
· ★**其它 issue 一条不动 (★ISS-283 仍 open ⇒ 等 advance.py --apply --only 单独认领★)★**
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / PROJECT_TRACKER §0★**
· ★**零外发 · 零采购 · 不替老板拍板★**
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

VERIFY_NOTE = (
    "★**main 2026-11-17 11:4x 本机独立复验 (★cron 775d9893「继续执行后继计划」· 自己实跑, 不抄交卷报告★)**: "
    "① `python3 HW/check_fsin_rootcause.py` ⇒ **rc=0** (★D1~D5 全绿: D1 订正页三口径齐全 + 锚点块可解析(9 项) · "
    "D2 重算 R_SER_FSIN→最近异网焊盘 1.300000 / TP_FSIN→1.350000 均 ≥ 阈值 0.45 ⇒ escape_stub 不适用 · "
    "D3 唯一挡路者 VDD_3V3_IO · 忽略后净距 0.4384 ≥ 判据 0.3950 · "
    "D4 老 S8 行 L387 逐字仍在 + 订正行 L388 在其下 + 六个口径齐全 · "
    "D5 受保护 5 件逐字节未变 + 落表后 md5 出处台账 L1270/L1271/L1272★) "
    "② `python3 HW/check_fsin_rootcause.py --selftest` ⇒ **rc=0 · 12/12 反向用例全抓到** (★含正向对照⑩ ⇒ 闸不是恒红★) "
    "③ ★**受保护 5 件实读**: 板 `611b869e13518c3c023fb178f91a0075` (★mtime 仍 2026-11-06 07:07:17.362193413★) · "
    "`.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` "
    "(★= 09:58 授权落表 A1+A2 后的合法值, 出处 = 落表台账 §16.2 L1270~L1272★) "
    "④ 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` = 47467 B · ★「待填」grep = 0★ · "
    "⑤ `state/fragments/hw.yaml` ★grep -c ISS-282 = 5★ (分片已写) "
    "⇒ ★**判定 pass (★本单自己的范围: 根因订正页 + 作业包追加式订正 + 机器闸 + 布线前置闸★)★** "
    "★**3 条红如实记 (★根因全部与本单无关且本单不能收★)**: "
    "A4 `HW/check_onepass_commit_order.py` rc=1 (D0) = 「零落表」硬基线过期 ⇒ 修法 = 基线挪到落表后真值并引台账 §16.2 ⇒ **归 ISS-283 (hw-lead)**; "
    "A5 `HW/check_onepass_s10_manifest.py` rc=1 (M1) = 结构性 ⇒ 清单要等 S10 那一趟生成 ⇒ **归「板只改一次」那一趟, 改判据即造假**; "
    "A6 `MECH/check_onepass_mech_sync.py` rc=1 (M5×3) = 同 A4 病根 ⇒ 文件在 MECH/ ⇒ **归 mech-lead** "
    "⇒ ★**本单不代改也不装绿, 已在交卷单里登记成 need★** "
    "★**⇒ hw-lead 名额释放 (★ISS-283 可派★)★**"
)

NOTE_TAIL = (
    "★**2026-11-17 11:4x (cron 775d9893 继续执行后继计划): fixing → verified** ★ "
    "★**会话 `agent:hw-lead:subagent:e1153379` (cron fb67af40 派) 11:38:41 交卷** ⇒ 盘上 4/4 交付物齐全 + 分片已写 "
    "⇒ ★**main 本机独立复验通过 (rc=0 · D1~D5 全绿 · selftest 12/12 · 受保护 5 件逐字节不变) ⇒ hw-lead 名额释放 ⇒ ISS-283 可派**★ "
    "★**3 条红 (A4/A5/A6) 归属已分清, 本单不代改: A4→ISS-283(hw-lead) · A5→S10 那一趟 · A6→mech-lead★**"
)


def atomic_write(path, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    lockf = open(LOCK, "a+")
    fcntl.flock(lockf, fcntl.LOCK_EX)
    try:
        with open(IL, "r", encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log.get("issues") or []
        target = None
        for it in issues:
            if it.get("id") == "ISS-282":
                target = it
                break
        if target is None:
            raise SystemExit("★ISS-282 不在 issue_log ⇒ 拒绝落账")
        if target.get("status") not in ("fixing", "verified"):
            raise SystemExit("★ISS-282 status = %r ⇒ 拒绝落账 (只认 fixing/verified)" % target.get("status"))

        shutil.copy2(IL, IL + ".bak_20261117_1145_cron775d_verify_iss282")
        before = target.get("status")

        target["status"] = "verified"
        target["fix_ref"] = "HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md | HW/PCB/FSIN_OUT_ROOTCAUSE.md | HW/check_fsin_rootcause.py"
        target["verify_by"] = "main"
        target["verify_result"] = "pass"
        target["verify_date"] = TODAY
        target["verify_note"] = VERIFY_NOTE
        old_note = target.get("note") or ""
        if "11:4x (cron 775d9893 继续执行后继计划): fixing → verified" not in old_note:
            target["note"] = (old_note.rstrip() + "\n" + NOTE_TAIL).strip()

        atomic_write(IL, log)
        print("★ISS-282: %s → verified (fix_ref + verify_note 落账)" % before)
        print("★备份: %s" % (IL + ".bak_20261117_1145_cron775d_verify_iss282"))
        return 0
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)
        lockf.close()


if __name__ == "__main__":
    raise SystemExit(main())
