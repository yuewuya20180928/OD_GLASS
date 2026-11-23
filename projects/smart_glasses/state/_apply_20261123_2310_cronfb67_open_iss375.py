#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 23:1x · 新开 ISS-375 并落 `fixing`** ★

★**为什么开这一单 (★本机实读 + 本机实算·不是猜★)★**:
  ① `python3 state/advance.py --json` ⇒ ★**internal: []** (三个总工名下零 `open` 可派)
  ② ★**本轮 22:4x~23:0x main 把 ISS-369 / ISS-371 / ISS-372 三条全签收了 (★verified★)
     ⇒ ★**三个槽位【同时】真空出来了** ⇒ ★**名下零 open 项 ⇒ 队列对三条线全都真断线** ★
  ③ ★**这一单有本机实算出来的真依据 (★全部可复跑·不抄任何 agent 报告★)★**:
     · ★**ISS-371 自己在 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 点了这件事但只点到一半★**
       (★本机实读原文: 「① 居中解 rot 90° ⇒ 原点 (141.0450, 56.6000) ; ② 居中解 rot 270° ⇒ 原点 (144.8550, 56.6000)
       · ★**两条都过 `CRIT` ; 但 ① 与 ② 的 pin1 朝向相反 (JTAG 线序要跟 hw-lead 对齐)** · … ⇒ **板那一趟必须写死**
       · ★归 **main → hw-lead** ★ ⇒ ★**「必须写死」的那件事, 全项目至今【没有任何一处】写死了** ★)
     · ★**main 本机实跑 pcbnew 验过 (★用 KiCad 自己的 FOOTPRINT 变换·不是手算★)★**:
       rot 0  ⇒ pad abs X = 142.2 / 142.7 / 143.2 / 143.7 (★顺排·TCK→TDO·★现状【无 pin1 极性标记】·四 pad 全 RECT SMD★)
       rot 90 ⇒ pad abs X 全 = 142.9 ; rot 270 ⇒ 全 = 145.7 (★在真 board 上验旋转约定★)
       ⇒ ★**配官方 land 的局部坐标 (pad1=(0,0)·pad2=(0,1.27)·pad3=(0,2.54)·pad4=(0,3.81)·轴向=局部 Y)
         ⇒ rot 90 ⇒ pad1 在 X 最小端 (顺排) ; rot 270 ⇒ pad1 在 X 最大端 (逆排) ⇒ 【两候选互为镜像】★**
     · ★**官方 land 自带 pin1 极性标记 (★本机实读 .kicad_mod★)**: pad "1" = `thru_hole rect` (★方形=行业标准 pin1 标记★)
       · pad "2"/"3"/"4" = `thru_hole circle` ⇒ ★**换官方 land 后板面【第一次】出现 pin1 标记 ⇒ 选错 = 实物排线插反** ★
     · ★**更狠的一半: JTAG 链在 SoM 侧【今天就是断的】★** (★本机实读 `HW/netlist_v1.csv` 第 388/390/392/394 行★)
       ⇒ `JTAG_TCK_SOC` / `JTAG_TMS_SOC` / `JTAG_TDI_SOC` / `JTAG_TDO_SOC` 四条网的 SoM 侧端点 ★**全部是 `SoC_NC`**★
       ⇒ ★**且 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行: 四条 JTAG 信号在官方 399 行脚表里【没有同名/后缀相同的信号】★
       ⇒ ★★**⇒ 与 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁直接冲突** ★
         (★终裁把 `JTAG_TDI` 判为「★**必需**★ (★进 S8 布线目标·★**板侧不许标 NC / no-connect**★)」, ★**而网表里它此刻就是 `SoC_NC`**★)
       ⇒ ★★**⇒ 「那一趟选哪个 pin1 朝向」【救不了这条链】⇒ 这件事必须在【开工前】被看见, 不是板做完才发现** ★★
  ④ ★**本单 = 纯分析 + 文档 + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① (先派纯分析/作业包类)★**

★**★防撞车 (★铁律⑩-i: 先落 `fixing` 再 spawn★)★**:
  ★**status 直接落 `fixing` ⇒ 兄弟 job 775d9893 读的是同一个字段 ⇒ 它看到 fixing 就不会再派 ⇒ 零撞车窗口** ★
  ★**issue_log / dispatch_log 写回用【文本追加】(★不是全文件 yaml 重排·★实测全文件重排会把已签收单的 verify_result 折行重排·属 churn★)⇒ 前 369 条逐条逐字节不变** ★

★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ★ (★不动分片 · 不动板 · 不动网表/脚表/BOM · 不动既有闸 · 不动既有页面 · 不推 GitHub · 零外发·不替老板拍板★)
"""
from __future__ import annotations

import fcntl
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_2310_cronfb67_open_iss375"

BRIEF375 = "ISS-375_sw_debug_pin_order_contract.md"
B375 = open(os.path.join(HERE, "dispatch_briefs", BRIEF375), encoding="utf-8").read()

TITLE375 = (
    "★★[★新主线·PCB 线·SW 侧·「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的【物理针序契约】(pin1 朝向 / JTAG 线序) + JTAG 链 SoM 侧真相·纯分析+文档+新建闸+沙盒预演·零写板] ★★"
    "【★main 2026-11-23 22:4x~23:1x 本机实读 + 本机实算★: ISS-371 (2026-11-23 22:4x 刚被 main 签收 verified) 自己已经在 "
    "`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 点了这件事但只点到一半 —— 原文「★**① 居中解 rot 90° ⇒ 原点 (141.0450, 56.6000) ; "
    "② 居中解 rot 270° ⇒ 原点 (144.8550, 56.6000) ★**两条都过 `CRIT` ; 但 ① 与 ② 的 pin1 朝向相反 (JTAG 线序要跟 hw-lead 对齐)** ★ · … ⇒ "
    "★**板那一趟必须写死** ★」⇒ ★★**而「必须写死」的那件事, 全项目至今【没有任何一处】写死了** ★★ "
    "⇒ ★**main 本机实跑 pcbnew 验过 (★用 KiCad 自己的 FOOTPRINT 变换·不是手算★)★**: rot 0 ⇒ pad abs X 142.2/142.7/143.2/143.7 "
    "(★现状顺排·TCK→TDO·★且现状【无 pin1 极性标记】·四 pad 全 RECT SMD·★所以今天「pin1 在哪」只是网表约定, 不是实物事实★) ; "
    "rot 90 ⇒ pad abs X 全 142.9 ; rot 270 ⇒ 全 145.7 ⇒ ★**配官方 land 的局部坐标 (pad1=(0,0)·pad2=(0,1.27)·pad3=(0,2.54)·pad4=(0,3.81)·轴向=局部 Y) "
    "⇒ rot 90 ⇒ pad1 在 X 最小端 (顺排) ; rot 270 ⇒ pad1 在 X 最大端 (逆排) ⇒ 两候选互为镜像** ★ "
    "⇒ ★**官方 land 自带 pin1 极性标记 (★本机实读 .kicad_mod★)**: pad \"1\" = `thru_hole rect` (★方形 = 行业标准 pin1 标记★) · pad \"2\"/\"3\"/\"4\" = "
    "`thru_hole circle` ⇒ ★**换官方 land 后板面【第一次】出现 pin1 标记 ⇒ 选错 = 实物排线插反 ⇒ JTAG 救砖链不通 ⇒ "
    "而 `SW/FLASH_AND_VERSION.md` 的 4 级救砖里 S3 = JTAG 是【除返厂换板外】唯一的软救砖路径** ★ "
    "⇒ ★★**更狠的一半: JTAG 链在 SoM 侧【今天就是断的】★★** (★本机实读 `HW/netlist_v1.csv` 第 388/390/392/394 行★) ⇒ "
    "`JTAG_TCK_SOC`/`JTAG_TMS_SOC`/`JTAG_TDI_SOC`/`JTAG_TDO_SOC` 四条网的 SoM 侧端点 ★**全部是 `SoC_NC`**★ ⇒ "
    "★**且 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行: 四条 JTAG 信号在官方 399 行脚表里【没有同名/后缀相同的信号】**★ ⇒ "
    "★★**⇒ 与 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁直接冲突** ★ (★终裁把 `JTAG_TDI` 判为「★**必需**★ "
    "(★进 S8 布线目标·★**板侧不许标 NC / no-connect**★)」, ★**而网表里它此刻就是 `SoC_NC`**★) ⇒ ★★**「那一趟选哪个 pin1 朝向」"
    "【救不了这条链】⇒ 这件事必须在【开工前】被看见, 不是板做完才发现** ★★ "
    "⇒ ★★**本单 = ① 一页物理针序契约 (逐件给现状/官方标记/两候选朝向/四线物理线序/裁决建议+代价/落点写死值) "
    "② 一条闸 (D0~D8 · 官方 land pad1 形状自算不许写死 · 两候选针序必须由 KiCad 自己的变换算出且互为逆序 · 页与闸不许各说各话 · "
    "网表 SoC_NC 结论必须实读相等 · 零挂链) ③ 沙盒 S0~S3 (含 S1↔S2 的【几何完全等价】与【针序互为逆序】两件事分别用数证明)** ★ "
    "★【纯分析 + 文档 + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★"
)

DESC375 = (
    "★**main 2026-11-23 22:4x~23:1x 本机实读 + 本机实算 (★不抄任何 agent 报告·全部可复跑★)★** ⇒ "
    "★**① ISS-371 已点到但没写死的那一条 (★本机实读原文★)★**: "
    "`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 = 「① 居中解 rot 90° ⇒ 原点 (141.0450, 56.6000) ; ② 居中解 rot 270° ⇒ 原点 "
    "(144.8550, 56.6000) · ★**两条都过 `CRIT` ; 但 ① 与 ② 的 pin1 朝向相反 (JTAG 线序要跟 hw-lead 对齐)** · 且两条都要求原点从 (144.30, 58.00) "
    "挪掉 ⇒ **板那一趟必须写死**」· 归 **main → hw-lead** ⇒ ★**全项目至今【没有任何一处】写死了 pin1 朝向** ★ "
    "★**② 现状板面【没有 pin1 极性标记】(★本机实跑 pcbnew 实读板★)★**: `J_DEBUG` 4 个 pad 全是 `shape=1` (RECT) / 全 SMD / 全 0.275×0.900 · "
    "pad abs X = 142.2 / 142.7 / 143.2 / 143.7 (net 依次 JTAG_TCK / TMS / TDI / TDO) ⇒ ★**四个长得一模一样 ⇒ 「pin1 在哪」今天只是【网表约定】, "
    "不是实物事实** ★ "
    "★**③ 官方 land 自带 pin1 标记 (★本机实读盘上 .kicad_mod★)★**: `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ pad \"1\" = `thru_hole rect` "
    "(★方形 = 行业标准 pin1 标记★) · pad \"2\"/\"3\"/\"4\" = `thru_hole circle` ⇒ ★**换官方 land 后板面【第一次】出现 pin1 标记 ⇒ "
    "那一刻「哪端是 pin1」从约定变成实物事实 ⇒ 选错 = 排线插反** ★ "
    "★**④ 两个候选互为镜像 (★main 本机实跑 KiCad 自己的变换验的·不是手算★)★**: 真 board 上 `FOOTPRINT.SetOrientationDegrees(0/90/270)` 实测 ⇒ "
    "rot 0 ⇒ 142.2/142.7/143.2/143.7 (顺排) ; rot 90 ⇒ pad abs X 全 142.9 ; rot 270 ⇒ 全 145.7 ⇒ ★**配官方 land 局部坐标 "
    "(轴向 = 局部 Y) ⇒ rot 90 ⇒ pad1 在 X 最小端 (顺排) ; rot 270 ⇒ pad1 在 X 最大端 (逆排)** ★ "
    "★**⑤ JTAG 链在 SoM 侧【今天就是断的】(★本机实读 `HW/netlist_v1.csv` 第 388/390/392/394 行★)★**: 四条网 "
    "`JTAG_TCK_SOC` / `JTAG_TMS_SOC` / `JTAG_TDI_SOC` / `JTAG_TDO_SOC` 的 SoM 侧端点 ★**全部是 `SoC_NC`**★ (★`SoC_NC` 全表出现 11 行★) ⇒ "
    "★**且 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行: 四条 JTAG 信号在官方 399 行脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` 里【没有同名/后缀相同的信号】**★ "
    "⇒ ★★**⇒ 与 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁直接冲突** ★ (★终裁把 `JTAG_TDI` 判为「★**必需**★ "
    "(★进 S8 布线目标·★**板侧不许标 NC / no-connect**★)」, ★**而网表里它此刻就是 `SoC_NC`**★) ⇒ ★★**⇒ 「那一趟选哪个 pin1 朝向」【救不了这条链】** ★★ "
    "★**本单零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动) · "
    "零落表 (网表/脚表/BOM 只读) · 零改既有闸 · 零改既有页面正文 (含 ISS-371 与 ISS-344 已签收件) · 零挂链 · 零外发 · 不代老板拍板** ★"
)

NEW = [
    {
        "id": "ISS-375",
        "title": TITLE375,
        "severity": "high",
        "source_blocker": "ISS-371",
        "source_agent": "main",
        "desc": DESC375,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss338_need_jtag_group_decision"],
        "task_brief": B375,
        "note": (
            "★2026-11-23 23:1x cron fb67af40 新开并【直接落 fixing】"
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★)"
            " ★ **开单依据**: ① `state/advance.py --json` 实跑 ⇒ internal: [] "
            "② ★**本轮 22:4x~23:0x main 把 ISS-369 / ISS-371 / ISS-372 三条全签收了 ⇒ 三个槽位【同时】真空** "
            "⇒ ★**名下零 open 项 ⇒ 队列对三条线全都真断线** "
            "③ ★**本机实算出来的真依据 (★全部可复跑·不抄任何 agent 报告★)★**: "
            "★**ISS-371 自己已在 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 点了「① 与 ② 的 pin1 朝向相反 … 板那一趟必须写死」, "
            "却至今没写死** ★ + ★**官方 land 的 pad \"1\" 是 `thru_hole rect` (行业标准 pin1 标记) 而现状板面四个 pad 全 RECT 无标记** ★ "
            "⇒ ★**换 land 后 pin1 从「网表约定」变成「实物事实」⇒ 选错 = 排线插反 ⇒ JTAG 救砖链不通 (S3 是除返厂外唯一的软救砖路径)** ★ "
            "+ ★**JTAG 四线的 SoM 侧端点【全部是 `SoC_NC`】且官方 399 行脚表里没有 JTAG 同名信号 ⇒ 与 ISS-344 终裁「JTAG_TDI 必需·板侧不许标 NC」"
            "直接冲突 ⇒ 那一趟选哪个 pin1 朝向【救不了它】** ★ "
            "④ 本单 = 纯分析 + 文档 + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① "
            "★ **任务书全文**: `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract.md` "
            "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★)"
        ),
        "dispatched_at": "2026-11-23",
    },
]


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        orig_log = open(LOG, encoding="utf-8").read()
        log = yaml.safe_load(orig_log) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        blocks = []
        for new in NEW:
            iid = new["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = new["status"]
                it["task_brief"] = new["task_brief"]
                it["note"] = new["note"]
                it["dispatched_at"] = new["dispatched_at"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
                continue
            blk = yaml.safe_dump([new], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- id:"), blk[:80]
            blocks.append(blk)
            applied.append("新开 %s (%s) · status 落 fixing (★先落 fixing 再 spawn⇒零撞车窗口★)"
                           % (iid, new["owner"]))

        if blocks:
            out = orig_log.rstrip("\n") + "\n" + "".join(blocks)
            atomic_write(LOG, out)
        else:
            out = orig_log

        back = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        after = back.get("issues") or []
        if len(after) != len(issues) + len(blocks):
            raise SystemExit("★issue_log 写回条数不对: 期望 %d, 实际 %d"
                             % (len(issues) + len(blocks), len(after)))
        if not all(a == b for a, b in zip(issues, after[:len(issues)])):
            raise SystemExit("★issue_log 写回自检失败: 前 %d 条有变动" % len(issues))
        applied.append("issue_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK"
                       % (len(issues), len(blocks)))

        orig_dl = open(DLOG, encoding="utf-8").read()
        dlog = yaml.safe_load(orig_dl) or []
        dl_is_dict = isinstance(dlog, dict)
        entries = dlog.get("dispatches") or [] if dl_is_dict else dlog

        dl_blocks = []
        for new in NEW:
            iid = new["id"]
            if any(e.get("issue") == iid for e in entries):
                applied.append("dispatch_log.yaml: %s 已有记录 ⇒ 不重复追加" % iid)
                continue
            entry = {
                "issue": iid,
                "agent": new["owner"],
                "at": "2026-11-23 23:1x",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: "
                        "★**开单 + 直接落 fixing + spawn** (★铁律⑩-i 先落 fixing 再 spawn⇒兄弟 job 读同一字段⇒零撞车窗口★)"),
                "brief": new["note"],
            }
            blk = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- issue:"), blk[:80]
            dl_blocks.append(blk)
            applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, new["owner"]))

        if dl_blocks:
            out_dl = orig_dl.rstrip("\n") + "\n" + "".join(dl_blocks)
            atomic_write(DLOG, out_dl)
        else:
            out_dl = orig_dl

        back_dl = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        e2 = back_dl.get("dispatches") or [] if dl_is_dict else back_dl
        if len(e2) != len(entries) + len(dl_blocks):
            raise SystemExit("★dispatch_log 写回条数不对")
        if not all(a == b for a, b in zip(entries, e2[:len(entries)])):
            raise SystemExit("★dispatch_log 写回自检失败: 前 %d 条有变动" % len(entries))
        applied.append("dispatch_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK"
                       % (len(entries), len(dl_blocks)))

    print("=" * 78)
    print("★ cron fb67af40 · 开单落盘 (★文本追加 + flock + 备份 + 写回自检★)")
    for a in applied:
        print("  · %s" % a)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
