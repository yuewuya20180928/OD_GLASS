#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (fb67af40 队列自动派活) 2026-11-16 18:1x: 僵尸 fixing 复记 + 重派记录
=========================================================================================
★**本脚本只做两件事 (不碰任何真源 / 分片 / 板 / 台账)** ★
  ① 给 ISS-246 / ISS-247 的 `note` 追加一段【僵尸会话 + 断点定位 + 本轮重派】的留痕
     (★status 保持 fixing ⇒ 下一轮 cron 的 in_flight 规则会跳过这两个 agent ⇒ 不撞车★)
  ② 在 `state/dispatch_log.yaml` 追加两条重派记录 (★可追溯★)

★**实测依据 (★main 2026-11-16 18:0x~18:1x 自己查的, 不抄任何交卷报告★)** ★★
★**A) ISS-246 (mech-lead) —— 僵尸会话 + 半成品已经落盘 (★交付物 1/3★)** ★
· 子会话 `agent:mech-lead:subagent:b56b051e-b0e1-497d-9e28-6fd444c295e5` (session 6c104a66)
  17:39:40 → 17:46:46 (460s) ⇒ ★**status=timeout · abortedLastRun=true** ⇒ transcript 末条 =
  「file lock stale for …/mech-lead/sessions/6c104a66….jsonl」+ 一次 transcript 修复 ⇒ ★**死在交卷物② 之前**★
· ★**盘上交付物 1/3**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` mtime 17:43 ⇒ **第 3 跳重锚已落**
  (顶部 ISS-246 注 + §0 Q-11 + §3.1 **R-04** + §3.1 机器保证段 + §7 G5/G5b 行 + §3.1 第三跳注)
  ⇒ ★**main 18:0x 自己实跑复核: `python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23**
  (原样: 「【结论】23/23 组检查通过 | FAIL 0 组」) ⇒ ★**`--selftest` ⇒ rc=0 · 14/14 抓到了** ★
· ★**缺的 2/3**: `HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md` **不存在**
  (★`ls HANDOFF/ | grep ISS245` 只有 sw-lead 那一份★) · `state/fragments/mech.yaml` 里 ★**0 处 ISS-246**★
· ⇒ ★**「交付物① 已落且门禁已绿, 但没交卷」⇒ 归【交卷缺件】而不是【没干活】★** ★

★**B) ISS-247 (hw-lead) —— 僵尸会话 + 沙盒里的活还在, 真盘 0 件** ★
· 子会话 `agent:hw-lead:subagent:9eab132b-2680-45d1-9249-23fec358194e` (session 2ad65579)
  17:39:40 → 17:46:46 (460s) ⇒ ★**status=timeout · abortedLastRun=true** ⇒ transcript 末条 = 「Aborted」★
· ★**盘上 5 件交付物 0 件**: `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` 不存在 ·
  `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` 不存在 · `HW/check_iss247_f1_landed.py` 不存在 ·
  `HANDOFF/2026-11-16_hw-lead_ISS247_F1落表作业包v1.md` 不存在 · `state/fragments/hw.yaml` 里 ★**0 处 ISS-247**★
· ★**但沙盒还在** (★main 18:0x 自己复核过★): `/home/yuewuya/.openclaw/workspace-hw/.sandbox_iss247/{sb0,sb1}`
  · ★**`sb1/state/gen_netlist.py` 比 `sb0` 多 2 行改法 (L381 / L393 的 `add()` 第 4 参数 = node2)** ★
    (★L381: `"C_VBUS_OUT"` → `"VBUS_5V_F1"` · L393: `"C_VBUS_OUT"` → `"VBUS_5V_CHG"`★)
  · ★**sb0 → sb1 的 `HW/netlist_v1.csv` diff = L8 + L12 两行** · **`HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 逐字节不变**
    (md5 `ef436a37…` / `2a730574…` 两边相同) · ★**`HW/SCHEMATIC_V1.md` 变 2 行 (L51 / L55)** ★
  · ★**真盘 5 个受保护 md5 (main 18:0x 实测) 与 ISS-243 落表后一致 ⇒ 真盘零写入成立**:
    网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★
· ⇒ ★**「沙盒实跑已做完, 盘上零产出」⇒ 续做派活必须把沙盒路径交给它, 不许它重跑一遍★** ★

★**C) ISS-245 (sw-lead) —— 不碰** ★
· 子会话 `agent:sw-lead:subagent:6555dbe9-b274-4bef-8797-b3c8042d5672` (session 50fc57f8)
  17:39:40 起 ⇒ ★**18:08 时仍 status=running** ★ ⇒ ★**交卷单 `HANDOFF/2026-11-16_sw-lead_ISS245_SW侧H1重锚第4跳.md`
  已落 (38448 B · mtime 18:07) ⇒ 它在正常干活 ⇒ ★**本 job 不派 sw-lead (铁律: 一个 agent 同时只允许一条写会话)★** ★

★**铁律**: 干活的人不许自签 ⇒ verify_by=main (已在 log 里, 不改) ★
"""
import fcntl
import os
import shutil
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_1810_redispatch246_247"
DLOG = os.path.join(HERE, "dispatch_log.yaml")
DBAK = DLOG + ".bak_20261116_1810_redispatch246_247"
TODAY = "2026-11-16"

NOTE = """
★2026-11-16 18:1x 队列自动派活 job (fb67af40) **僵尸 fixing 复记 + 续做重派**: ★**上一轮 (兄弟 job 775d9893 17:39:40 spawn) 的子会话 460s 撞 timeout 死掉了** ⇒ %s ⇒ ★**盘上现状 (main 18:0x~18:1x 自己实跑复核, 不抄交卷报告)**: %s ⇒ ★**本 job 续做重派 (runTimeout 5400s) ⇒ 续做硬规矩块已写进 brief** ⇒ ★**status 保持 fixing (下一轮 cron 的 in_flight 规则会跳过这个 agent ⇒ 不撞车)** ★
"""


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8"))
        touched = []
        for it in log.get("issues") or []:
            iid = it.get("id")
            if iid == "ISS-246":
                txt = ("子会话 `agent:mech-lead:subagent:b56b051e-b0e1-497d-9e28-6fd444c295e5` "
                       "(session 6c104a66) 17:39:40 → 17:46:46 (460s) · status=timeout · abortedLastRun=true "
                       "⇒ 死在交卷物② 之前")
                st = ("**交付物 1/3**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 3 跳重锚已落 (mtime 17:43 · "
                      "顶部注 + §0 Q-11 + §3.1 R-04 + §3.1 机器保证段 + §7 G5/G5b 行 + §3.1 第三跳注) "
                      "⇒ main 实跑 `python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23, `--selftest` ⇒ rc=0 · 14/14 "
                      "⇒ **缺 2/3**: 交卷单 `HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md` 不存在 + "
                      "`state/fragments/mech.yaml` 里 0 处 ISS-246 + 验收 ⑤-3 沙盒反向自证未跑")
                if it.get("status") != "fixing":
                    print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过" % (iid, it.get("status")))
                    continue
                it["note"] = (it.get("note") or "") + (NOTE % (txt, st))
                it["dispatched_at"] = TODAY
                touched.append(iid)
            elif iid == "ISS-247":
                txt = ("子会话 `agent:hw-lead:subagent:9eab132b-2680-45d1-9249-23fec358194e` "
                       "(session 2ad65579) 17:39:40 → 17:46:46 (460s) · status=timeout · abortedLastRun=true "
                       "⇒ transcript 末条 = 「Aborted」")
                st = ("**盘上 5 件交付物 0 件** (作业包 / 下一批清单 / 新门禁 / 交卷单 / 分片 全缺) "
                      "⇒ **但沙盒还在**: `/home/yuewuya/.openclaw/workspace-hw/.sandbox_iss247/{sb0,sb1}` "
                      "⇒ sb1 的 `state/gen_netlist.py` 已含改法 (L381/L393 的 add() 第 4 参数 node2) ⇒ "
                      "sb0→sb1 的 `HW/netlist_v1.csv` diff = L8 + L12 两行 · 脚表/BOM 逐字节不变 · "
                      "`HW/SCHEMATIC_V1.md` 变 2 行 ⇒ **真盘 5 个受保护 md5 与 ISS-243 落表后一致 ⇒ 真盘零写入成立**")
                if it.get("status") != "fixing":
                    print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过" % (iid, it.get("status")))
                    continue
                it["note"] = (it.get("note") or "") + (NOTE % (txt, st))
                it["dispatched_at"] = TODAY
                touched.append(iid)
        if not touched:
            print("⚠ 没有可复记的 ⇒ 未写盘")
            fcntl.flock(lk, fcntl.LOCK_UN)
            return
        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)
    for iid in touched:
        print(" - %s note 追加僵尸复记, status 保持 fixing" % iid)


if __name__ == "__main__":
    main()
