#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 16:3x · 新开 ISS-364 (hw-lead) + ISS-365 (mech-lead) 并直接派出** ★

★**为什么新开 (★逐条本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工名下**零 `open` 可派** ⇒ 队列真空 ⇒ 不开单就断线 ★
  ② sw-lead 名下 ISS-363 = `fixing` 且会话**活着** (★`logs/iss363/` 16:02 仍在落盘·base_check_* 全量跑完★) ⇒ ★**本轮不碰 sw-lead** ★
  ③ hw-lead 名下 ISS-361 已 `verified` ⇒ ★**槽位空出来** ⇒ 可派 ★
  ④ mech-lead 名下零 open 零 fixing ⇒ ★**槽位空着** ⇒ 可派 ★
  ⑤ ★**派活前置闸**: `python3 state/check_brief_commands.py --brief-file <brief>` ⇒ ★**两份 brief 都 rc=0** ★

★**纪律**: ★**status 直接落 `fixing` ⇒ 无 `open` 窗口 ⇒ 下一轮 in_flight 规则会跳过这两个 agent ⇒ 兄弟 job 775d9893 不会重复派** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·本 job 自己也不发★)**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_1630_cronfb67_open_iss364_365"
BRIEF364 = "ISS-364_hw_c4_target68_reachability.md"
BRIEF365 = "ISS-365_mech_s10_fp_swap_impact.md"

B364 = open(os.path.join(HERE, "dispatch_briefs", BRIEF364), encoding="utf-8").read()
B365 = open(os.path.join(HERE, "dispatch_briefs", BRIEF365), encoding="utf-8").read()

TITLE364 = (
    "★★[★新主线·PCB 线·HW 侧「S10 换封装真值」收口·纯分析+作业包+新建闸+沙盒可达性证明·零写板] ★★"
    "【ISS-361 (hw-lead) 已把「封装真值覆盖缺口」查清 (90 件 = 靶内 77 + 缺口 13 · 四桶 TP 42/DNP 26/靶内 77/缺口 13 = 158) "
    "⇒ 而 main 15:3x 落进 `state/board_trip_baseline_20260723.txt` 的《订正一》写着「C4 目标 = 68 ⇒ 须【换官方 land 90 件 + 网表节点具名 90 件】」"
    "⇒ ★★但这句「可达」没有任何沙盒证明 ⇒ ★★而它已经是那一趟的验收条件 ⇒ ⇒ 同一类坑刚在 15:3x 踩过一次"
    "(原口径「158 全随封装基线收敛」被沙盒实跑推翻: 换 land 根本不动 C4, 只有网表节点具名才动)★ ⇒ ⇒ 本单 = 把这句话做成可执行 + 可证伪】★★ "
    "⇒ ★**本单 = ① 逐件 90 行可执行作业包 (现占位几何 / 目标 lib:name + .kicad_mod + md5 / 目标几何 / 几何 Δ / pad↔net 序 / 要重接的 net / 腿 B 具名脚清单) "
    "② 一条机器闸 (判几何不判 lib:name 字符串 · 板面 186 个封装库名全空 ⇒ 判字符串是哑弹) "
    "③ 沙盒可达性证明: 158 → ? (腿 A / 腿 B 各自的 ΔC4 + 能不能到 68 + 到不了时真实可达值与差距) "
    "④ 一页 + 交卷页 + 分片 + 留证** "
    "★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC364 = (
    "★**main 2026-11-23 16:1x~16:3x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 三个口径 (实算自 `logs/iss361/04_recon.json`)**: C4 占位脚号器件 = 158 · ISS-356 靶子 = 100 (镜脚主 PCB 78 + 镜框充电板 22) · "
    "交集 77 · 差集 81 · 其中【真器件·必装·非 TP】13 ⇒ ★**本单对象 = 90 件 = 77 + 13** ★ "
    "★**② 四桶 (机器跑出来的)**: TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158 ⇒ 豁免 68 + 要收口 90 ⇒ ★**C4 目标 = 158 − 90 = 68** ★ "
    "★**③ ★★两条腿的区别 (决定闸怎么写)★★**: C4 数的是「网表节点串是不是 bare」, 不是「land 是不是官方封装」 ⇒ "
    "★**沙盒实测: 只把 5 件网表节点串改成具名 pinN ⇒ C4 158 → 153 (板面零改动); 反过来 100 件 land 全换官方封装 ⇒ C4 读数仍是 158** ⇒ "
    "⇒ ★**换 land 不动 C4, 具名脚才动 C4** ⇒ ★**⇒ 「158 → 68」这条路必须沙盒证明存在, 否则又是一句「看起来合理、实际不成立」的验收条件** ★ "
    "★**④ ★★板面封装的真实状态 (决定闸不许判什么)★**: 板面 186 个封装库名全空 (`GetFPIDAsString()` 唯一值 = `''`) ⇒ 板是【自绘通用占位】, "
    "不是「库名写错」 ⇒ ★**⇒ 新闸【不许】判「板面 lib:name == 台账 lib:name」(恒无意义·哑弹), 【必须】判几何: 焊盘数/焊盘坐标/fab 外框/中心距** ★ "
    "★**⑤ 板侧 5 条差异 (要跟 90 件绑在一张表上)**: 多余 2 (`C_VBUS_GND` pad1/pad2) + 同号异网 3 (`Q_PG` pad1/pad3 对调 · `D_ESD_USB_D` pad1 错) "
    "⇒ 且 `Q_PG`/`Q_AND`/`Q_ENVC` 三件 pad↔net 序反 (器件 1=G/2=S/3=D vs 板 1=D/2=S/3=G) ⇒ ★**换 land 时必须同时改 pad 序, 否则换完更错** ★ "
    "★**⑥ 两条只登记不代拍的分支 (继承 ISS-361 §5)**: K3 · 5 只按键换 KMR2 = 4 焊盘 vs 网表 2 脚 (沙盒实测 C3 判红「板 4 脚/网表 2 脚」) "
    "⇒ (a) 网表加 2 个具名脚 或 (b) 改选 2 焊盘封装 (代价: 按动力度 3N → 1.5N) ⇒ 不代选; "
    "K2 · `D_ESD_USB_D` 2 vs 3 脚随老板 W-1/W-2 分叉 ⇒ 只登记两分支候选 + 代价 ★ "
    "★**⑦ 两条被漏掉的件 (ISS-361 §5 已登记, 本单并进去·零改既有页)**: `FB_DEMO` 在 BOARD_ONEPASS_WORKPACKET.md 与 PREFLIGHT.md 里各 0 次命中 "
    "(现占位斜置 2 land @对角 1.000 vs 官方 0805 正置 @2.124 ⇒ 不改封装装不上) ⇒ 并入 land 重画清单建议 + 机器判据; "
    "`CHG_GND_STAR` 在 ISS-356 基线页 §2.2 那一格自相矛盾 (官方 `TestPoint_Pad_D1.0mm.kicad_mod` 实测只有 1 个焊盘, 那格却写「官方是 2 焊盘 ⇒ 必须新增第 2 个焊盘」) "
    "⇒ ★**照那一格改板会给它加一个不存在的第 2 个 land** ⇒ 本单零改基线页 (ISS-356 签收页), 只登记 + 订正建议 + 机器判据 ★ "
    "★**⑧ 台账**: `HW/FP_TRUTH_BASELINE.md` §2 逐 ref 表 (78 件 11 字段) + `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2 (13 件) + §3.2 (四桶建议) + §5 (K1~K5) ★ "
    "★**⑨ 沙盒落项目盘 `tmp/iss364_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)** ★ "
    "★**⇒ 本单只出【纯分析 + 作业包 + 新建闸 + 沙盒证明】, 一个字节都不许写板** ★"
)

NOTE364 = (
    "★2026-11-23 16:30 cron fb67af40 新开并直接派出 (status 落 fixing ⇒ 下一轮 in_flight 规则会跳过 hw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② sw-lead 名下 ISS-363 会话活着 (logs/iss363/ 16:02 仍在落盘) ⇒ 本轮不碰 "
    "③ hw-lead 名下 ISS-361 已 verified ⇒ 槽位空出来 ⇒ 可派 "
    "④ mech-lead 名下零 open 零 fixing ⇒ 本轮同批派 ISS-365 ⇒ 不凑数 ★ "
    "⑤ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ ★**本 brief rc=0** ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (9,594 B)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/落表台账/issue_log 一字不改) · 零改既有闸 (check_fp_truth_baseline.py / check_fp_truth_coverage_gap.py / "
    "check_onepass_preflight_coverage.py / check_onepass_s10_manifest.py / gate_check.py / merge.py / frag_write.py 一字不改) · "
    "零改既有页面 (HW/FP_TRUTH_BASELINE.md / HW/PCB/FP_TRUTH_COVERAGE_GAP.md / BOARD_ONEPASS_WORKPACKET.md / BOARD_ONEPASS_PREFLIGHT.md / "
    "state/board_trip_baseline_20260723.txt 老字零改动) · 零挂链 · 只写自己的分片 state/fragments/hw.yaml (只走 frag_write.py) · "
    "沙盒只落 tmp/iss364_sbx/ + logs/iss364/ · 不替老板拍板 (D_ESD_USB_D 2vs3脚 / 按键 3N vs 1.5N / D_LED_G 落位) · "
    "零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF364

TITLE365 = (
    "★★[★新主线·PCB 线·MECH 侧「S10 换封装真值」影响面·纯分析+新建闸+沙盒重判·零写板] ★★"
    "【ISS-290 (mech-lead) 已把「S6 的 20 个目标落位 × MECH 保留区」逐个交叉核对过 (最小净距 4.6500) · "
    "但那些数全是按【当前板上自绘占位 land】算的 ⇒ 而那一趟 S10 要把 90 件换成官方封装 ⇒ 器件 fab 外框/中心距/本体都会变 "
    "⇒ ★★main 本机实算: 20 个 S6 落位 = 10 个 `R_SEL_*` + 10 个 `TP_DSI_*` ⇒ ★★那 10 个 `R_SEL_*` 全落在 90 件里 ⇒ "
    "⇒ 换封装 ⇒ 4.6500 那条净距结论的几何基线会漂 ⇒ 而本机没有一条闸会知道 ⇒ "
    "★★⇒ 不查清 ⇒ 那一趟改完板才发现结构装不下 ⇒ 板 md5 变第二次 ⇒ 整趟白跑】★★ "
    "⇒ ★**本单 = ① 敏感度逐件表 (现占位几何 / 目标封装几何 / Δ / 碰 MECH 哪一条 / 判定 / 重算后的数) "
    "② 那 10 个 `R_SEL_*` 的专项 (换封装前后净距两列 + Δ + 要不要重排) "
    "③ 负结论机器化 (座体类 6 组 + 10 个 `TP_DSI_*` 与 90 件交集 = ∅ ⇒ 不受 S10 影响) "
    "④ 一条机器闸 + 沙盒三道 MECH 闸换封装前后的并排输出 + 一页 + 交卷页 + 分片 + 留证** "
    "★【纯分析 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC365 = (
    "★**main 2026-11-23 16:1x~16:3x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 最硬的一条交集 (实算自 `logs/iss361/04_recon.json` + `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:S6_TARGETS` 块)★**: "
    "S6 的 20 个目标落位 = 10 个 `R_SEL_*` + 10 个 `TP_DSI_*` (帧 B160x100) ⇒ ★**那 10 个 `R_SEL_*` 全部落在 S10 的 90 件集合里** "
    "⇒ ★**⇒ MECH 侧 §9「20 个目标落位 × MECH 保留区」的最小净距结论, 用的就是这些件【当前占位 fab 外框 1.80×1.00 · 中心距 1.60】** "
    "⇒ ★**⇒ 换官方 land 后必须重算, 而本机没人算过** ⇒ 10 个 `TP_DSI_*` 落在 TP 42 桶豁免 ⇒ 不受影响 (负结论也要写) ★ "
    "★**② 座体类不受影响 (负结论 · 同样要有机器证据)★**: `J_DEBUG`/`J_UART`/`J_USB_C`/`J_CHG`/`J_SOM_P1..P4` 与 90 件交集 = ∅ "
    "(★`J_SOM_P1`/`J_SOM_P3` 的 BOM type=NET ⇒ 进不了「必装 ∩ 非 NET/TP」★) ⇒ ★**⇒ MECH §10 的座体三方对照/开口尺寸/排针 pitch 结论不受 S10 影响** ★ "
    "★**③ 90 件里真碰 MECH 侧开口/光孔/键位/ESD 位置的件 (逐条给依据)★**: `D_LED_G` (结构光孔有/无 = 老板项) · "
    "`D_ESD_CAM`/`D_ESD_DEMO`/`D_ESD_USB_D` (ESD 结构位置要求: 距连接器 ≤3.0 mm · 共面接地 · 封装 ≤0.5 mm 高 · ISS-085 登记) · "
    "5 只按键 (`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST` · 官方 KMR2 = 4 焊盘 + 更大本体 vs 现占位 3.450×3.100) · "
    "`FB_DEMO` (现占位斜置 2 land @对角 1.000 / bbox 2.100×1.700 vs 官方 0805 正置 @2.124) · "
    "`Q_AND`/`Q_ENVC`/`Q_PG` (3 焊盘, 现占位 bbox 4.100×5.100 ⇒ SOT-23 ⇒ 高件 ⇒ 与腔体/屏蔽罩关系要重核) ★ "
    "★**④ MECH 侧现有三道闸现在全绿 (main 本机实跑)★**: `MECH/check_onepass_struct_crosscheck.py` rc=0 (N1~N6) · "
    "`MECH/check_onepass_mech_sync.py` rc=0 (M1~M5) · `MECH/check_board_frame_coords.py` rc=0 ⇒ ★**它们读的是当前板 ⇒ 换封装后会自动重判 ⇒ "
    "⇒ 本单要做的正是【提前把这个重判算出来】** ★ "
    "★**⑤ 沙盒怎么跑 (main 实读过源码·别踩坑)★**: `MECH/check_onepass_mech_sync.py` 有 `--root` (默认 PROJ) ⇒ 直接指沙盒根即可; "
    "但 `MECH/check_onepass_struct_crosscheck.py` 【没有】 `--root` ⇒ 它靠 `PROJ = HERE/..` ⇒ ★**⇒ 沙盒做法: 把 `MECH/` 整个目录 + "
    "`HW/PCB/demo_mainboard.kicad_pcb`(副本) + 它要读的表, 复制到 `tmp/iss365_sbx/` ⇒ 跑 `tmp/iss365_sbx/MECH/check_onepass_struct_crosscheck.py` "
    "⇒ 它自动把 PROJ 指向沙盒根 ⇒ ★**真闸一个字节不许改 (只改沙盒副本)】★** ★ "
    "★**⑥ MECH 侧台账 (在其上作业, 不许重写)★**: `MECH/BOARD_ONEPASS_MECH_SYNC.md` (ISS-278) · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` "
    "(ISS-290 · §2 保留区 / §3 20 落位明细 / §4 座体三方对照 / §5.6 E-1~E-6 / §6 贴角口径 / §7 机器块) · `MECH/BOARD_GEOM_30MM.md` · "
    "`MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` ★ "
    "★**⇒ 本单只出【纯分析 + 新建闸 + 沙盒重判】, 一个字节都不许写板** ★"
)

NOTE365 = (
    "★2026-11-23 16:30 cron fb67af40 新开并直接派出 (status 落 fixing ⇒ 下一轮 in_flight 规则会跳过 mech-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② sw-lead 名下 ISS-363 会话活着 ⇒ 本轮不碰 "
    "③ hw-lead 名下 ISS-361 已 verified ⇒ 同批派 ISS-364 "
    "④ mech-lead 名下零 open 零 fixing ⇒ 本轮派本单 ⇒ 不凑数 ★ "
    "⑤ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ ★**本 brief rc=0** ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (9,651 B)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/issue_log 一字不改) · 零改既有闸 (MECH/check_onepass_struct_crosscheck.py / check_onepass_mech_sync.py / "
    "check_board_frame_coords.py / check_demo_struct_truth.py / gate_check.py / merge.py / frag_write.py 一字不改) · "
    "零改既有页面 (MECH/BOARD_ONEPASS_MECH_SYNC.md / BOARD_ONEPASS_STRUCT_CROSSCHECK.md / BOARD_GEOM_30MM.md / "
    "BOARD_PORT_OPENING_S6_WORKPACKET.md / HW/PCB/BOARD_ONEPASS_WORKPACKET.md / HW/PCB/BOARD_FRAME_CALIBER.md 老字零改动) · "
    "零挂链 · 只写自己的分片 state/fragments/mech.yaml (只走 frag_write.py) · 沙盒只落 tmp/iss365_sbx/ + logs/iss365/ · "
    "不替老板拍板 (D_LED_G 光孔有/无 / D_ESD_USB_D 2vs3脚 / 按键 3N vs 1.5N) · "
    "零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF365


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


NEW = [
    {
        "id": "ISS-364",
        "title": TITLE364,
        "severity": "high",
        "source_blocker": "ISS-361",
        "source_agent": "main",
        "desc": DESC364,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-25",
        "status": "fixing",
        "external": False,
        "need_keys": [],
        "task_brief": B364,
        "note": NOTE364,
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-365",
        "title": TITLE365,
        "severity": "high",
        "source_blocker": "ISS-361",
        "source_agent": "main",
        "desc": DESC365,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-25",
        "status": "fixing",
        "external": False,
        "need_keys": [],
        "task_brief": B365,
        "note": NOTE365,
        "dispatched_at": "2026-11-23",
    },
]


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        for spec in NEW:
            iid = spec["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = "fixing"
                it["task_brief"] = spec["task_brief"]
                it["note"] = spec["note"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
            else:
                issues.append(dict(spec))
                applied.append("新开 %s (%s) · status 直接落 fixing" % (iid, spec["owner"]))

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        for spec in NEW:
            iid = spec["id"]
            if not any(e.get("issue") == iid for e in entries):
                entries.append({
                    "issue": iid,
                    "agent": spec["owner"],
                    "at": "2026-11-23",
                    "brief": spec["note"],
                    "job": (
                        "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-23 16:30 · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                    ),
                })
                applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, spec["owner"]))
        out = dlog
        if dlog_is_dict:
            out["dispatches"] = entries
        else:
            out = entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
