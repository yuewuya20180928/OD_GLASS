#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0120_cronfb67_land_iss346_orphan.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 01:2x
--------------------------------------------------------------------
把【本 job 上一轮 (2026-11-22 23:55) 写下但那一轮被 abort 前没来得及落台账的孤儿单】
补落成 ISS-346 (owner=sw-lead, status=open)

★**为什么要救这张单**:
  ★**上一轮 (23:55) 写了 brief `state/dispatch_briefs/ISS-343_sw_storage_capacity_matrix.md`
  ★**(★来源 = 老板拍板页 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行 need key
  ★`q3_storage_and_audio` · 决策码 Q3★) ⇒ ★**但那一轮在写 issue_log 之前就被 abort 了
  ★(★parent run 结束 ⇒ 子会话连带 abort, 23:37:52 那次同型事故★) ⇒ ★**台账里没有这张单,
  ★brief 成了孤儿 ⇒ 队列永远看不见它 ⇒ 这张卡会静默丢失** ★

★**为什么要【改号】而不是照用 ISS-343**:
  ★**本轮 (00:1x) 我已经用掉 ISS-343 了 (= hw-lead 的板侧项全集漏项单)** ⇒ ★**两张卡不能同号
  ★(★同号 = 交卷页文件名撞 + frag key 撞 + 台账歧义★) ⇒ ★**孤儿单统一改号 ISS-346
  ★(★brief 内的 ISS-343/iss343/ISS343_ 全部逐字改成 ISS-346/iss346/ISS346_★)** ★

★**为什么 status = open 而不是 fixing**:
  ★**sw-lead 名下已经压着 ISS-344 (★本轮已派出·在跑★) ⇒ ★**铁律「一个 agent 同时只派 1 条」
  ★⇒ ★**本轮不派它 ⇒ 落 `open` ⇒ 下一轮 (sw-lead 交卷后) 队列自然把它捞出来** ★
  ★**⇒ 这也意味着兄弟 job (cron 775d9893) 现在就能看见它并派 ⇒ 那是它的地界, 合法 ★**

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261123_0120_cronfb67_land_iss346_orphan"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-346_sw_storage_capacity_matrix.md")
TODAY = "2026-11-23"

TITLE = (
    "★★[★新主线·PCB 线·存储轴 Q3 分档可判·纯分析+机器矩阵+一页决策口径·零写板] ★★"
    "【把 Q3「模型/rootfs 怎么存」从 [0数据] 变成【可判矩阵】: 容量 × 存储 × 板框档 × 板侧动作 "
    "⇒ 判定它对「板那一趟」到底卡不卡 (★分档才成立: SPI-NOR 档板侧零动作·eMMC 档只卡产品板档★)】★★ "
    "★**来源 = 老板拍板页 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行 (need key `q3_storage_and_audio` · 决策码 Q3); "
    "交付 `SW/STORAGE_CAPACITY_MATRIX.md` + `SW/tools/gen_storage_capacity_matrix.py` + 交卷页 B0~B7 + sw.yaml 分片**★"
)

DESC = (
    "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
    "★**① 题面 (main 原文实读拍板页 §① 第 6 行)**: need key `q3_storage_and_audio` · 决策码 Q3 · "
    "「模型/rootfs 怎么存 (只 ADB push 是否接受外挂 SPI-NOR 16~64 MB · 板宽 12→15 mm) + 音频到底做不做」· "
    "卡不卡 = 【卡·时限型】· 证据 = [官网] 型号参数可自查 · 音频 = [0数据] ★ "
    "★**② SW 侧已有的别重做**: `SW/FLASH_AND_VERSION.md` §4.1 三方案 + §4.5.1 容量算术 ⇒ 分区表总量 90210304 B ⇒ 64MB SPI-NOR 装不下 ⇒ 真条件 = 「rootfs ≤ 30MB 且 flash ≥ 128MB」; "
    "`SW/tools/flash_layout_check.py` = 机器闸 (LAY-01~LAY-08) ★ "
    "★**③ 本单最关键的那条 (main 实读网表 + 板面)**: `HW/netlist_v1.csv` L202/L204/L206/L208 = 4 条 SPI 串阻 (R_SER_SPI_SCLK / R_SER_SPI_CSn / R_SER_SPI_MOSI / R_SER_SPI_MISO) 各自接 `J_BOOT1` pin1..pin4; "
    "L209 = pin5 = VDD_3V3_IO (CONN/DNP, note 逐字写明「SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)」+「★V1.1: 容量下限已由 SW 总工锁死 (ISS-080): rootfs ≤30MB · flash ≥128MB」); L210 = pin6 = GND (DNP) ⇒ "
    "★**板面上 `J_BOOT1` 封装【已经存在】(板文件 :3143 有 Reference J_BOOT1) ⇒ SPI-NOR 档 = 板侧零动作** ★ "
    "★**⇒ 推论**: 卡面那句「外挂存储必须赶在板那一趟开工前进网表」**只在 eMMC 档成立** (eMMC 要占板面 ⇒ 板宽 12→15mm ⇒ 必须重出板); "
    "★**而「板宽 12→15mm」这个代价只在产品板档成立** (ISS-341 已签收: B160x100 = 改现役板一次·台架板 160mm 宽 ⇒ eMMC 的 25% 板面代价 ≈ 0 ⇒ 连 eMMC 档也不卡这一趟) ⇒ "
    "★**Q3 的「时限型卡」很可能是【分档才成立】, 现在却整卡挂着 ⇒ 本单的作用就是把分档算出来** ★ "
    "★**④ 板只改一次铁律**: 引 `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-1~INV-4 ⇒ 任何【要改网表/改板框】的拍板项, 晚进 = 板 md5 变第二次 ⇒ 那一批 Gerber/投产包/留证链/盖章/发布全部作废重做 ★ "
    "★**⑤ A7S 那条实测路径当前不可用 (main 本轮实读)**: `getent hosts radxa-cubie-a7s.local` ⇒ 无解析 · 本机没有 `sshpass` ⇒ 「去 A7S 上量 rootfs」这条路走不通 ⇒ 不许写成阻塞项 ⇒ 走降级方案 (降级方案是必须项, 不是兜底选项) ★ "
    "★**⑥ 板基线**: 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4940213 B ★ "
    "★**⑦ 本单另发现一条 need 措辞要订正 (交 main, 不许自己改真源)**: sw.yaml 里 `iss338_need_boot_storage_answer` 写的是「3 条 SPI_*_BOOT」, ★**本单实读网表是 4 条** (SCLK/CSn/MOSI/MISO) 且焊盘位已在板 ★"
)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    if any(i.get("id") == "ISS-346" for i in issues):
        print("★ISS-346 已存在 ⇒ 幂等退出")
        return 0
    brief = open(BRIEF, encoding="utf-8").read()
    issues.append({
        "id": "ISS-346",
        "title": TITLE,
        "severity": "medium",
        "source_blocker": "ISS-338",
        "source_agent": "main",
        "desc": DESC,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-25",
        "status": "open",
        "external": False,
        "need_keys": ["q3_storage_and_audio"],
        "task_brief": brief,
        "dispatched_at": None,
        "verify_by": "main",
        "verify_result": None,
        "note": (
            "★★%s · cron fb67af40 (ARS45 队列自动派活) 补落【孤儿单】★ ★ "
            "★**这张单的 brief 是本 job 上一轮 (2026-11-22 23:55) 写下的, 但那一轮在写 issue_log 之前就被 abort 了 (★parent run 结束 ⇒ 子会话连带 abort, 23:37:52 那次同型事故★) ⇒ 台账里没有它, brief 成孤儿 ⇒ 队列看不见它 ⇒ 会静默丢失** ★ "
            "★**所以本轮把它捡回来, 并把号从 ISS-343 改成 ISS-346 (★本轮 00:1x 我已经用掉 ISS-343 = hw-lead 的板侧项全集漏项单 ⇒ 同号会撞交卷页文件名 + frag key + 台账★)** ★ "
            "★**status 落 `open` 而不是 `fixing`**: sw-lead 名下已压着 ISS-344 (★本轮已派出·在跑★) ⇒ 铁律「一个 agent 同时只派 1 条」⇒ 本轮不派它 ⇒ 下一轮队列自然捞 ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-346_sw_storage_capacity_matrix.md` (★check_brief_commands.py --brief-file rc=0★) ★" % TODAY
        ),
    })
    doc["issues"] = issues
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    hit = [i for i in doc2["issues"] if i.get("id") == "ISS-346"]
    print("★issues 条数 =", len(ids), "· 重复 id =", dup or "无")
    if hit:
        h = hit[0]
        print("★ISS-346 status=%s owner=%s brief=%d chars verify_by=%s"
              % (h.get("status"), h.get("owner"), len(h.get("task_brief") or ""), h.get("verify_by")))
    return 0 if (hit and not dup) else 1


if __name__ == "__main__":
    sys.exit(main())
