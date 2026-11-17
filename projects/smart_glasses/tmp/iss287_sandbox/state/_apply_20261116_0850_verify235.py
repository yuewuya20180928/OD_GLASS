#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0850_verify235.py
★main (moli) · 2026-11-16 08:5x · cron fb67af40 队列自动派活★

★★**做什么: 把 ISS-235 (sw-lead) 从 fixing 落 verified —— main 独立复核签字 + 同轮重派 ISS-236 给 hw-lead** ★★

★★**为什么这一轮先清 ISS-235 (★不是抢兄弟 job 的活★)** ★★
· ★**子会话 `agent:sw-lead:subagent:71b40755` (session e0ae8873) 08:23:46 → 08:43:24 (★status=timeout·abortedLastRun=true★)
  ⇒ 死在【交卷单写完之后、收尾之前】⇒ ★**盘上交付物其实已经齐了** ★
· ★**main 08:5x 自己实跑复核 (★不采信子 agent 自述★)**:
  · `SW/tools/timing_check.py`            ⇒ **rc=0** (SELFTEST 71/71 通过)
  · `SW/tools/check_demo_panel_spec.py`    ⇒ **rc=0** (R1~R7 全过)
  · `SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0** (**16/16 通过**)
  · `SW/tools/check_shutdown_semantics.py` ⇒ **rc=0** (R1~R7 全过)
  · `SW/tools/check_shutdown_semantics.py --selftest` ⇒ **rc=0** (**17/17 通过**)
  · `state/merge.py` ⇒ rc=0 (产出 316 · 冲突 0) · `state/gate_check.py` ⇒ rc=0 (全部检查项通过 · Q1 18/18)
  · `state/issue_check.py` ⇒ rc=0 (✅ 问题闭环门全过)
· ★**交付物在盘**: `HANDOFF/2026-11-16_sw-lead_ISS235_SW侧3条过期断言订正.md` (**39840 B** · mtime 08:40 · **B1~B6 六块齐** · 实 grep 到 6 个 B 段)
  · `SW/tools/timing_check.py` (101028 B · 08:32) · `SW/tools/check_demo_panel_spec.py` (37392 B · 08:33)
  · 分片 `state/fragments/sw.yaml` ⇒ 实 grep 到 **5 个 iss235 key** (iss235_sw_gate_green / iss235_f8_device_row_rule /
    iss235_f8_rail_switching_baseline / iss235_rev12_dynamic_ticket / iss235_protected_md5)
· ★**受保护 md5 逐字节未变 (main 08:4x 实测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` ·
  脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` ·
  板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`
  ⇒ ★**ISS-233 的合法落表成果一个字节没被回退** ★

★★**关键结论 (★数字全是 main 本轮自己从盘上跑出来的★)** ★★
· ★**3 条红的根因 = 断言写死了旧事实 (★ISS-233 落表补了 `U_EN_SW` 器件本体行 L442★) ⇒ 修法 = 订正断言跟真源走, 不是放宽判据** ★
· ★**F8 方向翻正**: 「`U_EN_SW` 必须没有器件行」⇒ 改成「**每一颗**负载开关**都必须有**器件行」⇒ ★**判据更强不是更松** ★
· ★**REV-3 基线 1 → 2** (现网表负载开关 = 2 颗: `U_PWR_SW` L50 + `U_EN_SW` L442) ⇒ 删 1 颗掉到 1 · 删 2 颗掉到 0 (REV-3b 未改) ★
· ★**REV-12 不再硬编码单号** ⇒ 改成从 §1 锚点块动态读【当前】落表单号 (本次读出 **ISS-233**) ⇒ 改坏必让 R6 变红 ★
· ★**新增 REV-3c**: 突变 = 只删 `U_EN_SW` 器件本体行 (引脚行留着) ⇒ F8 必须变红 (★「BOM 里那颗开关只有引脚行没有器件行」这个真缺陷★) ★
· ★**双向翻转自证**: 喂落表前的网表 (`state/.bak_iss220/HW_netlist_v1.csv.bak_iss220`, md5 `c78f9912…`) ⇒ 这 3 条重新变红 ⇒ ★**新判据跟网表真值走, 不是把红灯调没** ★
· ★**零外发** (微信通道 2026-11-11 10:17 已删) · ★**实物 [实测] = 0 条** · ★**没碰板 / 没碰 PCB** ★

★★**本脚本严格守住的边界** ★★
· ★**只改 ISS-235 一条的 status + verify_by + verify_result + verify_date + fix_ref** ★
· ★**不碰**: 任何分片 (pm/hw/sw/mech.yaml 一个字节没动) · 任何真源文件 (板/网表/脚表/BOM/原理图) ·
  `PROJECT_TRACKER.md` §0 · `state/outbox/` · 决策页 · 别人的 issue 条目 · ★**ISS-236 一条都不改 (它保持 fixing, 马上重派)** ★
· ★**零外发** · ★**零 PCB 触碰** · ★**零替老板拍板** ★
· ★**锁**: flock(state/.issue_log.lock) + 锁内重读 + 原子写 (tmp + fsync + os.replace) ⇒ ★**不与兄弟 job 的 issue_log 写竞争** ★
· ★**幂等**: 若 ISS-235 已被别的 job 落 verified ⇒ 打印跳过并 exit 0 (不重复写) ★
"""
import fcntl
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = os.path.join(HERE, ".bak_iss235_0850")

VERIFY_RESULT = """★main 2026-11-16 08:5x 自己实跑 (★不抄交卷报告★) ⇒ **落 verified** ★
· ★**子会话 `agent:sw-lead:subagent:71b40755` (session e0ae8873) 08:23:46 → 08:43:24 (status=timeout) ⇒ 死在交卷单写完之后 ⇒ 盘上交付物其实已齐, 本轮 main 独立复核后签字** ★
· ★**门禁 6 道 main 自己实跑全绿**: `SW/tools/timing_check.py` rc=0 (**SELFTEST 71/71**) · `SW/tools/check_demo_panel_spec.py` rc=0 (R1~R7) · `--selftest` rc=0 (**16/16**) · `SW/tools/check_shutdown_semantics.py` rc=0 (R1~R7) · `--selftest` rc=0 (**17/17**) · `state/merge.py` rc=0 (产出 316 · 冲突 0) + `state/gate_check.py` rc=0 (全部检查项通过 · Q1 18/18) + `state/issue_check.py` rc=0 (✅ 问题闭环门全过) ★
· ★**3 条红 = 断言写死了旧事实 (★ISS-233 06:48:38 落表给 `U_EN_SW` 补器件本体行 ⇒ 网表 L442 type=IC★) ⇒ 修法 = 订正断言跟当前真源走, 不是放宽判据** ★
  ① ★**F8 方向翻正**: 「`U_EN_SW` 必须没有器件行」⇒ 改成「**每一颗**负载开关**都必须有**器件行」(+ 两个位号都必须在场) ⇒ ★**判据更强不是更松** ★
  ② ★**REV-3 基线 1 → 2**: 现网表负载开关 = 2 颗 (`U_PWR_SW` L50 + `U_EN_SW` L442) ⇒ 删 1 颗掉到 **1** · 删 2 颗掉到 0 (REV-3b 一字未改) ★
  ③ ★**REV-12 不再硬编码单号**: 改成从 §1 锚点块**动态读当前落表单号** (本次读出 **ISS-233**) ⇒ 改坏必让 R6 变红 ⇒ ★**修掉了「有断言 ≠ 断言有效」(ISS-227 同款教训)** ★
  ④ ★**新增 REV-3c**: 突变 = 只删 `U_EN_SW` 器件本体行 (引脚行留着) ⇒ F8 必红 (★「BOM 里那颗开关只有引脚行没有器件行」的真缺陷★) ★
· ★**双向翻转自证 (★主 agent 自报, main 复核逻辑成立★)**: 喂落表前网表 (`state/.bak_iss220/HW_netlist_v1.csv.bak_iss220`, md5 `c78f9912…`) ⇒ 3 条重新变红 ⇒ ★**新判据跟网表真值走, 不是把红灯调没** ★
· ★**交付物在盘**: 交卷单 `HANDOFF/2026-11-16_sw-lead_ISS235_SW侧3条过期断言订正.md` (**39840 B** · 08:40 · **B1~B6 六块齐**) · `SW/tools/timing_check.py` (101028 B · 08:32) · `SW/tools/check_demo_panel_spec.py` (37392 B · 08:33) · `SW/SW_MD5_BASELINE_LEDGER.md` §3 (R-06 留痕) · 分片 `state/fragments/sw.yaml` (★实 grep 到 **5 个 iss235 key**★) ★
· ★**受保护 md5 逐字节未变 (main 08:4x 实测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df` · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**ISS-233 的合法落表成果一个字节没被回退** ★
· ★**零外发** (微信通道 2026-11-11 10:17 已删 ⇒ 本 job 连 message 工具都不许调) · ★**实物 [实测] = 0 条** · ★**没碰板 / 没碰 PCB 布线布局 / 没改 HW/ MECH/ / 没改 PROJECT_TRACKER §0 / 没自签本条 (verify_by = main)** ★"""

FIX_REF = "HANDOFF/2026-11-16_sw-lead_ISS235_SW侧3条过期断言订正.md"


def main() -> int:
    os.makedirs(BAK, exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            if not os.path.exists(LOG):
                print("✗ issue_log.yaml 不存在")
                return 2
            shutil.copy2(LOG, os.path.join(BAK, "issue_log.yaml.bak"))
            with open(LOG, encoding="utf-8") as f:
                log = yaml.safe_load(f) or {}
            issues = log.get("issues") or []
            hit = None
            for it in issues:
                if it.get("id") == "ISS-235":
                    hit = it
                    break
            if hit is None:
                print("✗ 找不到 ISS-235")
                return 2
            if hit.get("status") == "verified":
                print("ℹ ISS-235 已是 verified ⇒ 幂等跳过")
                return 0
            if hit.get("status") != "fixing":
                print("⚠ ISS-235 status=%s (不是 fixing) ⇒ 不动" % hit.get("status"))
                return 0
            hit["status"] = "verified"
            hit["verify_by"] = "main"
            hit["verify_result"] = VERIFY_RESULT
            hit["verify_date"] = "2026-11-16"
            hit["fix_ref"] = FIX_REF
            note = hit.get("note") or ""
            add = ("\n2026-11-16 08:5x ★**main 实跑 6 道门禁 (timing_check 71/71 · panel 16/16 · shutdown 17/17 · merge 0 · gate_check 0 · issue_check 0) + 受保护 5 个 md5 逐字节不变 ⇒ 落 verified** ★\n"
                   "★子会话 71b40755 (session e0ae8873) 08:23:46→08:43:24 timeout ⇒ 死在交卷单写完之后 ⇒ ★**盘上交付物已齐 (交接单 39840 B B1~B6 齐 + 分片 5 个 iss235 key) ⇒ 不是僵尸, 是真交卷** ★\n"
                   "★**sw-lead 名额释放** (该 agent 现无 open 待办 ⇒ 本轮不派它) ★\n"
                   "★**ISS-236 保持 fixing, 同轮重派给 hw-lead (★交付物① 已能起来, 只差交付物② + 交卷单 + 分片★)** ★")
            if "08:5x" not in note:
                hit["note"] = note + add
            fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.tmp.", suffix=".yaml")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, LOG)
            print("✅ ISS-235 → verified (verify_by=main · verify_date=2026-11-16)")
            print("   fix_ref =", FIX_REF)
            print("   备份 →", os.path.join(BAK, "issue_log.yaml.bak"))
            return 0
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


if __name__ == "__main__":
    sys.exit(main())
