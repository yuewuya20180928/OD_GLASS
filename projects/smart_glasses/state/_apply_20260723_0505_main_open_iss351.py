#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0505_main_open_iss351.py —— main 开 ISS-351 (hw-lead · 存储轴旧口径清账)"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

TITLE = ("★★[★新主线·PCB 线·存储轴旧口径清账·纯口径·零写板] ★★【ISS-346 + ISS-350 连续两单把存储轴口径从「整卡」改成【分档】"
         "⇒ ★**但 hw.yaml 的 answer `vendor_q19_boot_storage` 还在说「外挂 SPI-NOR 16-64MB · 板宽可能 12->15mm」"
         "⇒ 这句话同时错了两处 (容量口径 / 板宽归属) ⇒ 同仓并存两个打架的容量说法 ⇒ 机器读分片会读错 ⇒ 清掉它】★★ "
         "★**只改措辞·不动板·不落表·不新增拍板项**★")

DESC = ("★**main 2026-11-23 05:0x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 病灶**: `state/fragments/hw.yaml` 的 answer "
        "`vendor_q19_boot_storage` 的 value 逐字 = 「已并入原厂邮件问题清单第7问(内置boot storage? 容量?); 当前按无内置boot "
        "storage设计: 外挂 SPI-NOR 16-64MB, 吃镜脚空间, 板宽可能 12->15mm; 请并入第一轮跟进邮件」⇒ ★**错 1**: 容量 16-64MB ⇒ "
        "★**作废** ⇒ 应为 ≥128 MiB (1 Gbit) 起 (★ISS-080 已锁死 flash ≥128MB · 且 Winbond 料号里的数字是 Mbit 不是 MB, "
        "`W25Q64` = 8 MB·ISS-346 机器判决 5×4 矩阵 20/20 格★) ⇒ ★**错 2**: 「板宽可能 12->15mm」那是 **eMMC 档**的事 ⇒ 外挂 "
        "SPI-NOR 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58 + 4 条 0Ω 串阻位必装) ⇒ **板侧零动作 · 不改板宽 · 不重出板** ⇒ "
        "★**错 3**: 「请并入第一轮跟进邮件」这条指令 ★**已作废**★ (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, "
        "全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案·outbox 草稿一律不发★) ⇒ ★**② 同型残留**: "
        "main 实扫 hw.yaml 得 24 条带【等外部/邮件/询价】字样的条目 ⇒ 逐条筛后 ★**要处置的是【结论层面矛盾】的那些, 不是历史叙述**★ "
        "⇒ 本单要求 ★**比名单, 不许只报「扫到 N 条」**★ ⇒ ★**③ 边界**: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime "
        "`2026-11-06 07:07:17.362193413` 必须逐字节不变) · 零落表 · 零改闸 · 只写自己的分片 hw.yaml + 交卷页 + logs/iss351/ · 零外发 · "
        "零新增拍板项 ★")

BRIEF = (
    "★**题**: 存储轴口径已由 ISS-346/ISS-350 连改两轮成【分档】⇒ ★**hw.yaml 的 `vendor_q19_boot_storage` 还在说 "
    "「外挂 SPI-NOR 16-64MB · 板宽可能 12->15mm · 请并入第一轮跟进邮件」⇒ 错 3 处 (容量 / 板宽归属 / 已作废的邮件指令) ⇒ 本单 = "
    "把它改成分档口径 + 把 hw.yaml 里同型残留逐条列出来处置 (★只改措辞·零写板·零落表·零新增拍板项★)**★ "
    "★**做 3 件**: ① 改 `vendor_q19_boot_storage` 这一条 (容量 ⇒ ≥128 MiB (1 Gbit) 起 · 板宽 ⇒ 只有 eMMC 档才 12→15mm, "
    "SPI-NOR 档板侧零动作不重出板 · 证据等级 [实测]+[官网]+[0数据] + rootfs 降级方案 ⇒ 「区间 [7.969 MiB, 199.969 MiB] 内结论都成立, "
    "不存在等数据出来再判的状态」· 不许再出现「请并入邮件/询价/等回信」★) ② 扫 hw.yaml 同型残留 ⇒ ★**比名单, 逐条列, 不许只报数**★ "
    "⇒ 要么改成分档口径, 要么写明「已由 ISS-346/ISS-350 分档口径取代·保留作历史留档·结论不再引用」 ③ 交卷页 "
    "`HANDOFF/2026-11-23_hw-lead_ISS351_存储轴旧口径清账.md` (★骨架已由 main 预落·B0~B7 + 引用 MISS=0 + 板指纹前后双证 + "
    "§B6-2 改动前后逐条 diff★) ★**纪律**: 零写板 · 零落表 (不改网表/脚表/BOM/原理图/闸) · 只写 hw.yaml + 交卷页 + logs/iss351/ · "
    "★**零外发**★ · 证据分级必标 · 不替老板拍板 · 不新增拍板项 · 写分片只用 frag_write.py ★**必跑**: `python3 state/merge.py` (rc=0) && "
    "`python3 state/gate_check.py` (★Q1 必须 18/18 · Q7 必须 10/10★) && `python3 state/frag_write.py --agent hw-lead --show` && "
    "`md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 611b869e13518c3c023fb178f91a0075) ★ ★**任务书全文**: "
    "`state/dispatch_briefs/ISS-351_hw_storage_legacy_caliber_cleanup.md` (★check_brief_commands.py --brief-file rc=0★) ★")

NOTE = ("★★2026-11-23 · cron 775d9893 (ARS45 继续执行后继计划) 开单并派出 (★项目总工 main★) ★★ ★**开单依据**: ISS-349 cont1 交卷时 "
        "点名「hw.yaml 的 `vendor_q19_boot_storage` 仍写着 16-64MB ⇒ 同一分片并存两个打架的容量说法」+ ISS-346/ISS-350 已把口径改成分档 ⇒ "
        "main 实读确认后开单 ★**判定**: 纯口径类 · 零写板 · 零落表 (★符合「板只改一次」纪律: 先派纯分析/作业包类★) · 零新增拍板项 · "
        "★**本单不动板·不动网表·不动真源·只改措辞**★ · 派活时刻 2026-11-23 05:0x · ★**status 落 fixing ⇒ 兄弟 job fb67af40 的 "
        "advance.py --json 看不见本单 ⇒ 不会重复派** ★")

ENTRY = {
    "id": "ISS-351",
    "title": TITLE,
    "severity": "medium",
    "source_blocker": "ISS-346",
    "source_agent": "main",
    "desc": DESC,
    "owner": "hw-lead",
    "reporter": "main",
    "raised": "2026-11-23",
    "due": "2026-11-24",
    "status": "open",
    "external": "false",
    "task_brief": BRIEF,
    "dispatched_at": None,
    "verify_by": "main",
    "verify_result": None,
    "note": NOTE,
}


def main():
    src = open(LOG, encoding="utf-8").read()
    if "\n- id: ISS-351" in src:
        print("★ISS-351 已在台账 ⇒ 不重复开单")
        return 0
    chunk = yaml.safe_dump([ENTRY], allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss351" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    if isinstance(items, dict):
        items = list(items.values())
    ids = [i.get("id") for i in items]
    print("台账条数 = %d · ISS-351 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-351" in ids, len(ids) == len(set(ids))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
