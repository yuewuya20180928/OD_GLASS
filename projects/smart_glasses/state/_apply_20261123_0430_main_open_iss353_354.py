#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261123_0430_main_open_iss353_354.py —— main 开 2 单 (队列自动派活 cron fb67af40)

ISS-353 → sw-lead : rk3572 目标口径清账 (ISS-155 线 · 纯口径 · 零写板)
ISS-354 → hw-lead : demo 主板可制造性收口 (ISS-169 线 · 纯查证 · 零写板)

★为什么开这两单 (★事实全部本机实读, 不抄任何 agent 报告★):
  · advance.py 的 internal[] 为空 ⇒ 三个总工名下没有 open 单 (mech-lead 名下 ISS-352 仍 fixing ⇒ 在飞)
  · 队列里 12 条 main 名下的 open 单里, 只有 ISS-109 / ISS-348 带 task_brief, 其余 11 条只有标题
  · 其中 ISS-155 (blocker) 与 ISS-169 (PCB 线) 的内容足以拆出【纯分析/作业包类】的活
    ⇒ 符合「板只改一次」纪律 (先派纯分析类, 真动板那一趟等老板拍完 9 件再一次做完)
  · 本单只开单 + 落 fixing, 不动板、不改网表真源
"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BRIEF_DIR = os.path.join(PROJ, "state/dispatch_briefs")
STAMP = time.strftime("%Y%m%d_%H%M")

B353 = open(os.path.join(BRIEF_DIR, "ISS-353_sw_rk3572_target_caliber_cleanup.md"), encoding="utf-8").read()
B354 = open(os.path.join(BRIEF_DIR, "ISS-354_hw_demo_board_manufacturability_closure.md"), encoding="utf-8").read()

TITLE_353 = (
    "★★[★新主线·PCB 线·模型链·rk3572 目标口径清账·纯口径·零写板] ★★【ISS-263 (2026-11-17) 已实测 "
    "`rknn3-toolkit 1.2.0` 支持 `config(target_platform='rk3572')` rc=0 (错 target `rk3576` 反而抛 ValueError 且报错原文含 "
    "`rk3572`) ⇒ ★**「rk3572 不是合法 target ⇒ 只能用 rk3576 target 转」这条路线已经过时** ⇒ ★**但全仓口径仍大面积停在旧口径** "
    "⇒ 本单 = ① 全仓清账 (比名单·不许只报数) ② 板端接受性 [0数据] 的自研降级方案 (★不许用「买块 RK3572 板」来解·老板 2026-11-04 "
    "19:10 指示★) ③ 给 main 一条结案建议 (ISS-155 的 blocker 能不能降)】★★ ★**只改口径·不动板·不落表·不新增拍板项·零外发**★"
)

DESC_353 = (
    "★**main 2026-11-23 04:1x~04:3x 本机实读 (不抄 agent 报告)★** ⇒ ★**① 旧口径**: ISS-155 (blocker, open, owner=main) 的核心命题 = "
    "「rk3572 不是 rknn-toolkit2 合法 target ⇒ 只能 target_platform='rk3576' 转 ⇒ 那个 .rknn 在 RK3572 上能不能跑通(板端)」 ⇒ "
    "★**② 新事实 (ISS-263 交卷页 `HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md` 原文)**: "
    "`rknn3-toolkit 1.2.0` (conda env `/home/yuewuya/miniconda3/envs/rknn3`) 的 `config(target_platform='rk3572')` rc=0; 反向自证: "
    "`rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, "
    "rk186x, rk3572` ⇒ ★**证明 target 参数真被读了** ★; 转换 3×rc=0, 产物 249360 B / md5 97a34fff…, 跨 3 会话 9/9 逐字节相同 ⇒ "
    "★**「转换链」这一环已通** ★ ⇒ ★**③ 板端仍 [0数据]**: `init_runtime(target='rk3572')` rc=-1 / `RKNN3_ERR_DEVICE_UNAVAILABLE` / "
    "`list_devices()=[]` ⇒ 本机 0 台 RK3572 设备 ⇒ ★**且不许用采购来解** ⇒ 必须出自研降级方案 (板到手一条命令出 PASS/FAIL) ★ "
    "⇒ ★**④ 同时 `SW/RK3572_TARGET_COMPAT_V2.md` (v2.0, 2026-11-15) 仍停在「toolkit2 无 rk3572 target ⇒ 只能 rk3576 转」的旧结论** ⇒ "
    "★**⑤ 边界**: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变) · 零落表 · "
    "零外发 · 零采购 · 不替老板拍路线 · 只写 sw.yaml 分片 + 交卷页 + logs/iss353/ + `SW/RK3572_TARGET_COMPAT_V2.md` 的追加段 ★"
)

NOTE_353 = (
    "★★2026-11-23 04:3x · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ ★**开单依据**: ① ISS-263 已把 "
    "「rk3572 无合法 target」这条命题在新工具链下打掉, 但 ISS-155 仍是 blocker 且全仓口径未同步 ② 板端 [0数据] 按老板 2026-11-12 "
    "02:02 口径必须换成「自己查 + 证据等级 + 降级方案」, 不许挂成外部依赖 ★**判定**: 纯口径类 · 零写板 · 零落表 (★符合「板只改一次」"
    "纪律: 先派纯分析/作业包类★) · 零新增拍板项 · ★**本单不动板·不动网表·不动真源**★ · 派活时刻 2026-11-23 04:3x · ★**status 落 "
    "fixing ⇒ 兄弟 job 的 advance.py --json 看不见本单 ⇒ 不会重复派** ★"
)

TITLE_354 = (
    "★★[★新主线·PCB 线·demo 主板可制造性收口·纯查证·零写板] ★★【ISS-169 (open, owner=main) 暴露三件「板子还不能下单」的事至今没收口 ⇒ "
    "本单 = ① **SoM 座 pin1「哪一排」公开资料无定论** ⇒ 出降级方案 + 下料前一票否决项 ② **5 个 ref / 4 类封装与脚号不自洽** "
    "(Q1 / Q2 / U_BATPROT / U_LDO_S28 / U_SUPV) ⇒ 查官方 datasheet + KiCad 官方库 ⇒ 出**板那一趟的改项清单** ③ **BOM 里 OPN 仍「待选型」** ⇒ "
    "自己网上查官网 ⇒ 给候选 + 代价 (不代拍)】★★ ★**只出方案与清单·不动板·不改网表真源·不改脚表·不改 BOM·不重出 Gerber**★"
)

DESC_354 = (
    "★**main 2026-11-23 04:2x 本机实读 (不抄 agent 报告)★** ⇒ ★**① `HW/PCB/SOM_CONNECTOR_GEOMETRY_PROBE.md` 已查清**: P1=(51.0,3.5) / "
    "P2=(51.0,46.5) / P3=(17.0,3.5) / P4=(17.0,46.5) (mm, SoM 顶视, 原点=左下角) · pin1 在哪一「端」已定 (P1/P2 在 x=60.8, P3/P4 在 "
    "x=26.8) · ★**pin1 在哪一「排」= 无定论** (公开资料只能定到端) ⇒ ★**载板两排做反 ⇒ 该座 100 个网络全部对调 ⇒ 板子白打** ★ ⇒ "
    "★**② `HW/PCB/PIN_REALITY_GAP.md` (生成器 = `python3 state/gen_kicad_sch.py --pin-gap`) 已定位 5 个 ref / 4 类不自洽**: `Q1`/`Q2` "
    "(BOM footprint=SON-8 3.3×3.3mm, 板封装只画 5 焊盘 2,3,4,5,6 且外形 4.94×5.0mm ≠ SON-8 3×3) · `U_BATPROT` (BQ2970 SOT-23-6, 板封装 "
    "6 焊盘但编号 2..7 与符号 1..6 不对齐) · `U_LDO_S28` (TPS7A20-28 五脚, 板封装只落 1,2,4,5 ⇒ 缺 EN(3)) · `U_SUPV` (TPS3808G01 类 "
    "SOT-23-6 六脚, 板封装只落 1,4,5,6 ⇒ 缺 GND(2) 与 MR(3) ⇒ 装上也跑不起来) ⇒ ★**★不许手写进 PIN_REALITY_GAP.md (它是生成器产物, "
    "重跑即冲掉) ⇒ 结论落到作业包追加段★** ★**③ 为什么现在做**: 「板只改一次」⇒ 改项清单不齐, 那一趟就会重画第二遍 ⇒ 本单提前消掉 ★ "
    "★**④ 边界**: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 逐字节不变) · 零落表 · 零外发 · "
    "不代老板拍 (C_VBUS_GND 留位 / ESD 架构轴 / U-1 画哪块物理产品 都不是本单的项) · 只写 hw.yaml 分片 + 交卷页 + logs/iss354/ + "
    "`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 与 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的追加段 (只追加·零删除) ★"
)

NOTE_354 = (
    "★★2026-11-23 04:3x · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ ★**开单依据**: ISS-169 至今 open 且无 "
    "task_brief, 内容已可拆成【纯查证/作业包类】的活 ⇒ 符合「板只改一次」纪律 (先派纯分析类, 真动板那一趟等老板拍完 9 件再一次做完) ★ "
    "★**本单交的是器件级/几何级事实与改项清单, 不碰板坐标/层数/尺寸 ⇒ 不因 U-1 未拍而卡住** ★ ★**判定**: 纯查证类 · 零写板 · 零落表 · "
    "零新增拍板项 · 派活时刻 2026-11-23 04:3x · ★**status 落 fixing ⇒ 兄弟 job 的 advance.py --json 看不见本单 ⇒ 不会重复派** ★"
)

ENTRIES = [
    {
        "id": "ISS-353",
        "title": TITLE_353,
        "severity": "blocker",
        "source_blocker": "ISS-155",
        "source_agent": "main",
        "desc": DESC_353,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-24",
        "status": "open",
        "external": "false",
        "task_brief": B353,
        "dispatched_at": None,
        "verify_by": "main",
        "verify_result": None,
        "note": NOTE_353,
    },
    {
        "id": "ISS-354",
        "title": TITLE_354,
        "severity": "high",
        "source_blocker": "ISS-169",
        "source_agent": "main",
        "desc": DESC_354,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-24",
        "status": "open",
        "external": "false",
        "task_brief": B354,
        "dispatched_at": None,
        "verify_by": "main",
        "verify_result": None,
        "note": NOTE_354,
    },
]


def main():
    src = open(LOG, encoding="utf-8").read()
    dup = [e["id"] for e in ENTRIES if ("\n- id: %s" % e["id"]) in src]
    if dup:
        print("★已在台账 ⇒ 不重复开单: %s" % dup)
        return 0
    chunk = yaml.safe_dump(ENTRIES, allow_unicode=True, sort_keys=False, width=100)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss353_354" % STAMP)
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
    owners = {i.get("id"): i.get("owner") for i in items if i.get("id") in ("ISS-353", "ISS-354")}
    print("台账条数 = %d · 零重复 id = %s · 新单 owner = %s"
          % (len(ids), len(ids) == len(set(ids)), owners))
    return 0


if __name__ == "__main__":
    sys.exit(main())
