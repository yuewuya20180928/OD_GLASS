#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261122_2355_cronfb67_open_iss343.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-22 23:5x
--------------------------------------------------------------------
开单: ISS-343 (sw-lead) = 老板拍板页 Q3「模型/rootfs 怎么存」的可判化

★**为什么开新单**: `state/advance.py --json` ⇒ internal=[] (队列真空) ⇒ sw-lead 名额空
  (名下 open=0 · fixing=0 · 无运行中会话) ⇒ 按「让内部待办不断线」开单。

★**为什么直接落 `fixing` 而不是 `open`**:
  ★**兄弟 job (cron 775d9893「继续执行后继计划」) 每 30 分钟跑一次, 它也读 `state/advance.py --json`**
  ★**⇒ 若本单留一个 `open` 窗口 ⇒ 兄弟 job 会把同一条当自己的货派给 sw-lead ⇒ 撞车**
  ★**⇒ 按 ISS-339 / ISS-342 的先例: status 直接落 `fixing` ⇒ 兄弟 job 看不见本单** ★

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-343_sw_storage_capacity_matrix.md")
BAK = LOG + ".bak_20261122_2355_cronfb67_open_iss343"

ISS343 = {
    "id": "ISS-343",
    "title": (
        "★★[★新主线·PCB 线·纯分析+机器矩阵类·零写板] ★★"
        "【Q3 存储轴可判化: 把「模型/rootfs 怎么存」从 [0数据] 变成【容量×存储×板框档×板侧动作】矩阵 "
        "⇒ 判定它对「板那一趟」到底卡不卡 (★main 本机实读: 网表 L202~L210 已有 J_BOOT1 启动存储焊盘位 6pin (4 条 SPI_*_BOOT "
        "串阻 + pin5 VDD_3V3_IO + pin6 GND, 全 DNP) 且板面 demo_mainboard.kicad_pcb:3143 已有该封装 ⇒ SPI-NOR 档板侧零动作; "
        "而「板宽 12→15mm」的 eMMC 代价只在产品板档成立 (台架板 160×100 ⇒ 代价≈0) ⇒ 卡面那句「外挂存储必须赶在板那一趟开工前进网表」"
        "其实是【分档才成立】, 现在整卡挂着 ★) ⇒ 交付: ① 5×4 容量矩阵 (每格带 LAY-03/LAY-08 机器输出) "
        "② rootfs 可判区间 (真值仍 [0数据] 但结论不依赖它) ③ 零代价可执行路径 (只 ADB push ⇒ 板侧零动作) "
        "④ 时点分档结论 ⑤ 机器生成器 + 交卷页 B0~B7 ★★"
    ),
    "severity": "high",
    "source_blocker": "q3_storage_and_audio",
    "source_agent": "main",
    "desc": (
        "★**main 2026-11-22 23:5x 本机实读 (不抄任何 agent 报告)★** ⇒ "
        "★**① 拍板页 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行 = need key `q3_storage_and_audio` · 决策码 Q3 · "
        "题「模型/rootfs 怎么存 (只 ADB push 是否接受外挂 SPI-NOR 16~64MB · 板宽 12→15mm) + 音频到底做不做」· "
        "卡不卡 = 「卡 (时限型)」· 证据 = 「[官网] 型号参数可自查 · 音频 = [0数据]」** ★ "
        "★**② SW 侧盘上已有: `SW/FLASH_AND_VERSION.md` §4.1 三方案 + §4.5.1 容量算术 (总量 90210304 B ⇒ 64MB SPI-NOR 装不下 ⇒ "
        "真实条件 rootfs≤30MB 且 flash≥128MB) · `SW/tools/flash_layout_check.py` (LAY-01~LAY-08) · "
        "`SW/tools/s2_rescue_config.example.json` (partitions 无 offset 键 ⇒ 偏移按序累加) · 模型产物体积 [实测] "
        "10,575,159 B = 10.09 MiB (`SW/RKNN_BENCH.md` §3.2.2) ⇒ model 槽 15MB 有 4.9MB 余量** ★ "
        "★**③ main 本轮实跑基线: `--device-size 64MB` ⇒ LAY-01/02/05/06/07 PASS · LAY-03/04 FAIL "
        "(version_block end=90210304 > 67108864) · LAY-08 PASS (rootfs=30.0MB)** ★ "
        "★**④ 关键事实: `HW/netlist_v1.csv` L202/L204/L206/L208 = 4 条 SPI 串阻位接 J_BOOT1 pin1..4 (网名 SPI_SCLK/SPI_CSn/"
        "SPI_MOSI/SPI_MISO_BOOT) · L209 = J_BOOT1 pin5 = VDD_3V3_IO (DNP, note 逐字写「pin5/pin6 预留外挂 SPI-NOR 的 3V3/GND」"
        "「V1.1: rootfs ≤30MB · flash ≥128MB」) · L210 = pin6 = GND (DNP) · 板面 `HW/PCB/demo_mainboard.kicad_pcb:3143` "
        "已有 J_BOOT1 封装 ⇒ SPI-NOR 档 = 板侧零动作** ★ "
        "★**⑤ 板框三候选 (ISS-341 已签收): B160x100 台架板 / F30A 60×30 / P60×15 ⇒ 「板宽 12→15mm」只在产品板档成立** ★ "
        "★**⑥ 本机 A7S 路径当前不可用 (`getent hosts radxa-cubie-a7s.local` 无解析 + 无 sshpass) ⇒ rootfs 实测走降级方案 "
        "(不许挂成阻塞项)** ★ "
        "★**⑦ 本单不依赖任何待拍答案 (rootfs 真值 [0数据] ⇒ 目标是让结论【不依赖它】) ⇒ 直接做, 不许挂阻塞** ★"
    ),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-22",
    "due": "2026-11-24",
    "status": "fixing",
    "external": False,
    "need_keys": [
        "q3_storage_and_audio",
        "iss338_need_boot_storage_answer",
        "iss343_storage_capacity_matrix",
    ],
    "task_brief": "",  # 下面从 brief 文件读
    "dispatched_at": "2026-11-22",
    "verify_by": "main",
    "verify_result": None,
    "note": (
        "★★2026-11-22 23:5x · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ "
        "★**开单依据 (main 本机实读·不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` ⇒ internal=[] / approvals=[] "
        "/ waiting=0 ⇒ **队列真空** (16 条 open 全是 boss/main 地界, 3 个总工名下 open=0) ⇒ 按「让内部待办不断线」开单 ★ "
        "② ★**sw-lead 名额空** (名下 open=0 / fixing=0 / `sessions_list` 无运行中会话) ⇒ hw-lead 与 mech-lead 都有在飞会话 "
        "(main 主会话 23:48 起的 ISS-340 cont3 / ISS-342 cont2) ⇒ 本轮只派 sw-lead 一条 ★ "
        "③ ★**status 直接落 `fixing` (不经过 `open` 窗口) ⇒ 兄弟 job (cron 775d9893) 的 `advance.py --json` 看不见本单 ⇒ "
        "不会重复派 sw-lead** ★ "
        "★**④ 任务书 = `state/dispatch_briefs/ISS-343_sw_storage_capacity_matrix.md` (★`check_brief_commands.py --brief-file` rc=0★) ★** "
        "★**⑤ 零写板 / 零落表 / 零改既有闸 / 零外发 / 不替老板拍 Q3** ★"
    ),
}


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
    if any(i.get("id") == "ISS-343" for i in issues):
        print("★ISS-343 已存在 ⇒ 幂等退出 (不重复开单)")
        return 0
    brief = open(BRIEF, encoding="utf-8").read()
    ISS343["task_brief"] = brief
    issues.append(ISS343)
    doc["issues"] = issues
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)
    # 自检: 回读 + 零重复 id
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = {x for x in ids if ids.count(x) > 1}
    hit = [i for i in doc2["issues"] if i.get("id") == "ISS-343"]
    print("★issues 条数 =", len(ids), "· 重复 id =", sorted(dup) or "无")
    print("★ISS-343 落表 =", bool(hit), "· status =", hit[0].get("status") if hit else None,
          "· owner =", hit[0].get("owner") if hit else None,
          "· task_brief =", len(hit[0].get("task_brief", "")) if hit else 0, "chars")
    return 0 if (hit and not dup) else 1


if __name__ == "__main__":
    sys.exit(main())
