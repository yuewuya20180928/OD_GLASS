#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改派两单 (2026-11-11 19:1x · 队列自动派活 job) —— owner: main → mech-lead / sw-lead
================================================================================
★**为什么改派 (★不是绕过规则, 是把规则用到人身上★)**:
  · 老板 11-11 10:07 口径: 当前主线 = 硬件原理图 demo 绘制; **PCB 布线/布局类一律不派**;
    **优先派【原理图/网表/ERC/选型/结构/软件】类 ISS** ⇒ ★**这两条正好是"结构"与"软件"** ⇒ 不违反主线口径。
  · `advance.py --json` 的 internal[] 空 = **不是没活, 是 hw-lead 名额被在飞的 ISS-193 占着**
    (★实测: hw-lead 会话 `agent:hw-lead:subagent:32d6fc57…` status=running · 19:0x 仍在跑★)
    ⇒ sw-lead / mech-lead 两个总工**空转**, 而 issue_log 里 **21 条 open 单挂在 main 名下**
    (其中 16 条已逾期, 最早 due 11-05) ⇒ ★**"内部待办不断线"这条目的落空了**。
  · 选这两条的判据 (逐条实测): ①**不依赖外部回复** ②**不依赖老板拍板** ③**不是 PCB 布线/布局类**
    ④**与在飞的 ISS-193 零文件交集** (它只碰 BOM / 封装 / 脚数来源 / `HW/PCB/PIN_REALITY_GAP.md`)
    ⑤**严重度最高的两条**: ISS-139 = blocker · ISS-127 = high。

★**ISS-127 → mech-lead (结构总工)**: 脱模斜度把镜脚·H 链打到 **−0.577mm ⇒ 几何上做不出来**。
  ★**方向其实已经裁过** (`MECH/DFM_REVIEW.md` §7 needs_from `mech_dfm_battery_seat` = main 裁:
  "按『改 CNC 嵌件』推进") ⇒ ★**本单不是再讨论要不要改, 是把"改"落成几何**;
  ★**且重量账刚变坏** (ISS-192 交卷: 30mm 板宽下金属骨架 4 个候选全超预算, 最好 4.08g/对 vs +1~3g;
  石墨 2.16g/对 > W11 上限) ⇒ ★**要求给出"重量账内"的解**。
★**ISS-139 → sw-lead (软件总工)**: ISP tuning 这笔账躲不掉 (rkaiq 公开 iqfiles 里 ar0234/ov04c10 都没有 IQ,
  ★**本机已有实测快照 `HW/_os_snapshots/rkaiq_iqfiles.json`**) ⇒ ★**与选路解耦 ⇒ 可并行准备**。

★**验证分离 (铁律)**: 这两单原来 owner=main / verify_by= mech-lead|hw-lead (= "项目总工自办, 别人验")。
  ⇒ **现在活交给子总工做 ⇒ verify_by 改成 main** ⇒ ★**干活的人不许自签**。

★**due 不动**: 两条本来就逾期 (11-05) ⇒ ★**我没改 due 来把 issue_check 违规数洗掉** (诚实优先)。

原子写 (flock + 锁内重读 + tmp/os.replace); 写后逐条比对"其余 188 条 issue 一个字段都没变"。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"

BRIEF_127 = """\
★**目标**: 把 ISS-127 从「★几何上做不出来 (H 链最坏 −0.577mm)★」推到「★有解★」——
   给出**量产架构方案** (方向已裁: 打印件负责造型 + 金属件承担定位/承力 ⇒ **电池座/PCB 座改 CNC 嵌件**),
   使**电芯段 H 链余量 ≥ 0.40mm 判据**成立, 并把判据固化成**一条命令能复跑**的检查。

★**为什么现在做 (★main 2026-11-11 19:0x 实测, 不是推测★)**
① ISS-025 (结构 DFM 评审) 交卷里算出一条**已定的不可能** (不是余量紧张, 是不可行):
   主腔深 **38.00mm** ⇒ 双面 1° 脱模 ⇒ 内腔横截面窄端少 **1.327mm**
   ⇒ 镜脚·H 链 (电芯段, 名义余量 0.95) 量产最坏 **0.75 − 1.327 = −0.577mm** ⇒ **做不出来**
   ⇒ 皮纹面 (α=0.5°) 只救到 **0.087 < 判据 0.40** ⇒ ★**靠公差/斜度救不回来, 只能靠结构改**
   (原文与算式: `MECH/DFM_REVIEW.md` §2.1.2 / §G3 · 复算脚本 `MECH/dfm_check.py` §B/§C)
② ★**架构方向其实已经裁过了** (`MECH/DFM_REVIEW.md` §7 needs_from `mech_dfm_battery_seat` = main 裁,
   原文 "**按『改 CNC 嵌件』推进 (不回应就按此做)**") ⇒ ⇒ ★**本单不是再讨论要不要改, 是【把"改"落成几何】**
③ ★**但"改"要付的重量账刚刚变坏 (★这是你自己 2026-11-11 17:39 交卷 (ISS-192) 的新结论★)**:
   30mm 板宽下 **所有金属骨架候选全部超预算** (最好候选 C = **4.08g/对** vs 骨架预算 +1~3g ⇒ 超 1.08g),
   且 **石墨 2.16g/对 > W11 上限 1~2g** (见 `MECH/BOARD_GEOM_30MM.md` §5 / `MECH/MECH_BUDGET.md` §2.4 B)
   ⇒ ⇒ ★**你再往镜腿里加 CNC 嵌件 = 在已经超预算的账上再加钱**
   ⇒ ⇒ ★**本单必须给出"重量账内"的解, 不许给"几何上能过但重量超"的做法**
④ ★**Rev B 打印包 = 检具 + 试样, 不含量产外形件 ⇒ 量产外壳的脱模面级统计目前【0 个数据点】**
   (Rev B 几何里 **ZERO_DRAFT 面占 25~62%** 直壁; `fit_coupon` 另有 **2 个倒扣面 α=−40°/−30°**
   ⇒ FDM 能打, 注塑/压铸出不来) ⇒ ⇒ ★**本单要顺手把"量产件的脱模面统计口径"立起来 (将来才有尺子)**

★**本单要交的东西 (A~F)**
A. **口径钉死 (先做这一步, 不许跳过)**: ★**项目里有两个都叫「H 链」的口径, 不许混用** ——
   ① `MECH/DFM_REVIEW.md` §2.1.2 的**电芯段链**: 电芯腔 6.35 vs 镜腿厚 7.30 (名义 0.95 / 最坏 0.75) ⇒ **脱模后 −0.577**
   ② `MECH/BOARD_GEOM_30MM.md` §5.4 的**PCB/骨架堆叠链**: 外壁 0.8 + 骨架 1.0 + PCB 1.0 + 空隙 0.3 + 隔热垫 0.5
      + 皮肤壁 0.8 = 4.40 vs 7.30 ⇒ 余 **2.60 ✅**
   ⇒ ★**你报告第一行必须写清你用的是哪一条链、为什么**; 若两条都保留, 分别给余量与判据
   ⇒ ★**不许拿 2.60 去说 −0.577 的事, 也不许拿 −0.577 去否 2.60**
B. **最小改造集 (面级)**: 列出**必须改的面** (面名 / 当前 α / 当前腔深 / 截面贡献 / 目标 α / 目标截面 / 改后余量),
   使**电芯段链**余量从 −0.577 回到 **≥0.40** (需要补回 **≥0.977mm**)。
   ★**两种脱模角情形都要给**: 皮肤侧**皮纹面 0.5°** 与 **光面 1.5°**
   (老板还没拍 `mech_dfm_draft_texture`, due 11-10 已逾期 ⇒ ★**不许假设哪条已定**)
C. **2~3 条量产架构方案** (方向 = 电池座/PCB 座改 CNC 嵌件), 每条给: 几何余量算式 / 重量 (g/对, 对着 4.08g/对
   与 W11 的 2.16g/对 说**增量**) / 零件数与成本量级 / 装配顺序 / 风险
   ⇒ ★**至少一条必须给出"重量账内"的解** (不许四条方案全是超预算的)
D. **板厚四档都要跑**: ISS-122 的层数还没定 ⇒ 板厚可能是 **0.41 / 0.80 / 1.00 / 1.22mm** (ISS-126)
   ⇒ ★**不许假设板厚已定**; 你的方案要在四档下分别成立或不成立 (写清哪几档破)
E. **量产件脱模面统计口径 (★现在 0 数据点★)**: 立"该算什么 / 算什么 / 判据多少"
   (ZERO_DRAFT 面占比上限 / 倒扣面 α 下限 / 直壁面清单), 使将来拿到量产件或图纸时有尺子
   (★**Rev B 的统计只能当现状基线, 不能当合格判据**)
F. **一条命令能复跑的检查**: 新脚本放 `MECH/` 目录下 (★**文件名你自己定, 写进报告里★**) + `--self-test`
   (★**反向用例: 改坏一个参数必须变红**) ⇒ rc=0;
   ★**并把既有算式接进去** (`MECH/DFM_REVIEW.md` §2.1.2 / `MECH/dfm_check.py` §B/§C ⇒ 不许另起一套数)

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 MECH/dfm_check.py                 # rc=0 (既有基线; ★不许改它的结论数字)
python3 MECH/fit_check_v3_30mm.py         # rc=0 (三链锁定值)
python3 MECH/skeleton_section_check.py    # rc=0 (骨架重量账; 30mm 口径)
python3 MECH/<你新脚本的文件名>            # rc=0 + --self-test rc=0 (★把尖括号换成实际文件名★)
python3 state/merge.py                    # rc 必须 0 (冲突 0)
python3 state/gate_check.py               # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # 必须一字未动 (611b869e… / c78f9912…)
```

★**交卷 ≤ 25 行** (结论先行; 逐条给复现命令与实测输出; ★**明确写"哪条方案是推荐项 + 为什么"**)

★**边界 (不许越)**
· ★**只写**: `MECH/` 下你自己的新文件 + `MECH/DFM_REVIEW.md` (★**只许追加一节, 不许改既有章节的结论/数字★)
  + `HANDOFF/` 下的交卷报告 + ★**必要时** `state/fragments/mech.yaml` (走 `state/frag_write.py`;
  ★**只许新增条目, 不许删改别人的 key**)。
· ★**不许碰**: `HW/**` · `SW/**` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` ·
  `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · `state/gen_*.py` ·
  `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活★)。
· ★**不许联系供应商/原厂/模具厂** (外发一律经项目总工; ★**牌号级收缩率/工艺窗口不许编 ⇒ 标 [0数据]**)。
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**本机物理上无法打印/量测**
  (`MECH/print/ENV_PROBE_20261101.md`) ⇒ ★**本单一切输出都是 [推算], 不许冒充实测**。
· ★**读长文件用 grep/sed 分段, 不许整文件读进来** (`MECH/DFM_REVIEW.md` 很长 ⇒ 先 grep 定位再读片段)。
"""

BRIEF_139 = """\
★**目标**: 把 ISP tuning 这笔账从「一句『要自己做』」变成「**可排期、可询价、可验收**的立项」——
   ★**不管最后选 C 还是 D, tuning 都必须做 ⇒ 本单是【与选路解耦的可并行准备】**, 不是选型单。

★**为什么现在做 (★main 2026-11-11 19:0x 实测, 不是推测★)**
① ★**实测**: rkaiq 公开 `iqfiles/isp3x` 与 `isp32` 目录里 ★**ov04c10 与 ar0234 都没有 IQ 文件**
   (有的是 imx415 / imx327 / imx464 / os04a10 / ov02b10 / gc8034 / sc200ai 等) ⇒ ★**这笔账躲不掉**
   ⇒ ★**本机已有实测快照 `HW/_os_snapshots/rkaiq_iqfiles.json`** (目录清单实测)
   ⇒ ★**你先复核这份快照, 不许再联网重抓当新证据**
   (原文出处: `HW/OPEN_SOURCE_AVAILABILITY.md` §3.3)
② ★**它是 demo 关键路径**: demo 要跑通「sensor→RK→OD(80类)→画框→屏」⇒ ★**ISP tuning 是这条链上的必经一环**
   (rkaiq 没现成 IQ ⇒ 必须自己做) ⇒ ★**这条不占功耗, 但占人天与样机窗口 ⇒ 必须进计划, 不能默认它会自己发生**
③ ★**但它有硬前置**: 要先有 AR0234CS 在 RK3572 上驱动能出 RAW (ISS-144) + ★**镜头/模组定版才能标定**
   (IQ 文件 = sensor × 镜头 × 模组 三者绑定) ⇒ ⇒ ★**排期上与 ISS-144 并行准备, 不等它**
   ⇒ 本单要交的就是这条并行线的**准备件**
④ ★**成本量级**: 路径 A (AR0234CS) 估 **1~2 人周 + 硬件调试窗口**; 路径 B (有现成 IQ 的 sensor, 如 imx415 / ov02b10)
   可先把链路打通 (★这段对比已有 `SW/DEMO_OD_PIPELINE_SPEC.md` §4.2 ⇒ ★**你补的是立项层, 不要重写那段口径**)
⑤ ★**RK3572 专属风险**: ★**RK3572 专属 BSP / ISP tuning 不公开** (公开的只有通用 BSP kernel 6.1 与 rkaiq 本体)
   ⇒ ★**tuning 必须在 RK3572 上做, 不能拿 RK3588 的 IQ 直接套**

★**本单要交的东西 (A~D)**
A. **立项文档 (放 `SW/` 目录下, ★文件名自定, 写进报告★)**, 必含 6 节:
   ① **工作量与前置条件**: 需 RKISP Tuner + 暗室/灰卡 + 标定板 + 样机调试窗口
      ⇒ 逐项写"有没有 / 要多久 / 卡在谁手上"
   ② **谁来调的三条路线对比**: ①自研 (学习曲线) ②**模组厂随货提供 IQ** ③**第三方调像服务商**
      ⇒ 每条给前置条件 / 成本量级 / 交期 / 风险 ⇒ ★**建议权重**: ②③ 通常远低于自研
      ⇒ ★**但不许替老板拍板**, 只给可比较的账
   ③ **RK3572 专属风险** (上面 ⑤) + ★**为什么 tuning 必须在目标板做**
   ④ **验收判据**: 出图白平衡/色温/暗角/噪点达标 + ★**与 OD 模型的输入分布一致
      (★ISP 搞坏后处理阈值 ⇒ 端到端精度塌 ⇒ 这一条要写成"怎么量", 不许只写"达标")**
   ⑤ **排期账**: 与 ISS-144 (驱动出 RAW) 并行、不等它; ★**标定窗口要占样机档期 ⇒ 必须进计划表**;
      ★**"路径 B 先打通链路" 与 "路径 A 后补 tuning" 的先后**写清楚
   ⑥ **与 OD 链路的耦合**: ISP 输出 (色彩/噪声/动态范围) 与 `SW/SW_TIMING_REVIEW.md` /
      `SW/DEMO_OD_TIMING_SPEC.md` 里对输入分布的假设, 对齐口径
B. **★"要问模组厂 / 第三方服务商"的问题清单 (5~8 条)** ⇒ ★**只写清单, 一条都不许发、不许联系任何外部**
   ⇒ 落到你的交卷报告里, 由项目总工走外发流程 (★**外发一律经项目总工**: 起草可以, 发送不行)
C. **★机器可查的"现成 IQ 覆盖表"**: 从本机快照 `HW/_os_snapshots/rkaiq_iqfiles.json` 实读
   ⇒ 列出每个候选 sensor (imx415 / imx327 / imx464 / os04a10 / ov02b10 / gc8034 / sc200ai / ar0234 / ov04c10)
   **有没有 IQ 文件 + 具体文件名 + 适用版本**
   ⇒ ★**这正好答掉 `SW/DEMO_OD_PIPELINE_SPEC.md` §7 的 P2-2 待办**
   (rkaiq 公开 iqfiles 里 imx415 / ov02b10 的具体文件与适用版本)
   ⇒ 新脚本放 `SW/tools/` 目录下 (★**文件名自定, 写进报告★**), rc=0 + `--self-test` (反向用例: 改坏判据必须变红)
   ⇒ ★**若快照里查不到版本信息 ⇒ 标 [0数据], 不许猜**
   (★**不许联网重抓当新证据**; 若你一定要联网核对, 只能读公开页面, 且必须把【本机快照】与【线上结果】两份对照贴出来,
   不一致就点出来, 不许静默取其一)
D. **交卷报告 (放 `HANDOFF/` 目录下, ★文件名自定★)**: 结论先行 + 逐条复现命令与实测输出
   + 分片登记 (走 `state/frag_write.py` 原子写 `state/fragments/sw.yaml`; ★**只许新增条目, 不许删改别人的 key**)

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 SW/tools/<你新脚本的文件名>     # rc=0 + --self-test rc=0 (★把尖括号换成实际文件名★)
python3 state/merge.py                 # rc 必须 0 (冲突 0)
python3 state/gate_check.py            # Q1 必须 18/18
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb   # 必须一字未动 (c78f9912… / 611b869e…)
```

★**交卷 ≤ 25 行** (结论先行; 逐条给复现命令与实测输出;
★**明确写"ISP tuning 这笔账最小要占谁的人天与哪个样机窗口"**)

★**边界 (不许越)**
· ★**只写**: `SW/` 下你自己的新文件 + `SW/tools/` 下你的新脚本 + `HANDOFF/` 下你的交卷报告
  + ★**必要时** `state/fragments/sw.yaml` (走 `state/frag_write.py`)。
· ★**不许碰**: `HW/**` · `MECH/**` · ★**`SW/DEMO_OD_PIPELINE_SPEC.md`** (★**不许改** —— 那份的 DSI payload 口径
  刚在 2026-11-11 09:0x~11:0x 统一过 (373 ⇒ 2986 Mbps / @90Hz 4480) ⇒ ★**你要改它的地方写成 needs_from 报给 main,
  不许自己动★) · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` ·
  `HW/PCB/demo_mainboard*.kicad_sch` · `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · **别人的分片** ·
  `state/issue_log.yaml` (★**改 issue 状态是 main 的活★)。
· ★**不许联系供应商/原厂/服务商** (★**外发一律经项目总工**: 起草可以, 发送不行)。
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**板端实测现在做不了 (Radxa 板不可达)** ⇒ 板端相关一律 [0数据]。
· ★**读长文件用 grep/sed 分段, 不许整文件读进来**。
"""

NOTE_127 = (
    "\n★**2026-11-11 19:1x 队列自动派活 job 改派**: owner main → **mech-lead** (结构总工), "
    "verify_by mech-lead → **main** (★**干活的人不许自签 = 验证分离铁律**)。"
    "★**为什么派**: 老板 11-11 10:07 口径【结构类优先派】+【PCB 布线/布局类不派】⇒ 本单属结构类且不碰 PCB;"
    "★**它不是『待定』**: 方向已裁 (电池座/PCB 座改 CNC 嵌件), 缺的是『落成几何』; "
    "★**也不依赖任何外部回复** ⇒ 可立即开工。★**与在飞 ISS-193 零文件交集** (那单只碰 BOM/封装/脚数来源)。"
    "★**due 不动** (本单 due 11-05 已逾期 ⇒ 没改 due 来把 issue_check 违规数洗掉)。"
)

NOTE_139 = (
    "\n★**2026-11-11 19:1x 队列自动派活 job 改派**: owner main → **sw-lead** (软件总工), "
    "verify_by hw-lead → **main** (★**干活的人不许自签 = 验证分离铁律**)。"
    "★**为什么派**: 老板 11-11 10:07 口径【软件类优先派】; ★**本单 severity=blocker 且是 demo 关键路径** "
    "(sensor→RK→OD→画框→屏 上的必经一环); ★**与选路解耦 ⇒ 不依赖任何外部回复, 可立即开工**。"
    "★**与在飞 ISS-193 零文件交集** (那单只碰 BOM/封装/脚数来源)。"
    "★**due 不动** (本单 due 11-05 已逾期 ⇒ 没改 due 来把 issue_check 违规数洗掉)。"
)

PATCH = {
    "ISS-127": {
        "owner": "mech-lead",
        "verify_by": "main",
        "task_brief": BRIEF_127,
        "_note_append": NOTE_127,
    },
    "ISS-139": {
        "owner": "sw-lead",
        "verify_by": "main",
        "task_brief": BRIEF_139,
        "_note_append": NOTE_139,
    },
}


def main() -> int:
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        items = list(doc.get("issues") or [])
        before = {it.get("id"): dict(it) for it in items}

        touched = []
        for it in items:
            p = PATCH.get(it.get("id"))
            if not p:
                continue
            it["owner"] = p["owner"]
            it["verify_by"] = p["verify_by"]
            it["task_brief"] = p["task_brief"]
            it["note"] = (it.get("note") or "") + p["_note_append"]
            touched.append(it.get("id"))

        # ---- 写后自检: 其余每条 issue 必须逐字段不变 ----
        after = {it.get("id"): it for it in items}
        if len(after) != len(before):
            print("❌ issue 总数变了, 放弃写盘")
            return 2
        diff_other = []
        for k, b in before.items():
            if k in PATCH:
                continue
            if after[k] != b:
                diff_other.append(k)
        if diff_other:
            print("❌ 非目标 issue 发生变化: %s ⇒ 放弃写盘" % diff_other[:5])
            return 2

        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    print("✅ 已原子写 issue_log.yaml (flock + 锁内重读 + tmp/os.replace):")
    for k, p in PATCH.items():
        print("   - %s: owner → %s, verify_by → main, task_brief 已写入 (%d 字符), note 已追加"
              % (k, p["owner"], len(p["task_brief"])))
    print("   issue 总数: %d (未变) · 其余 issue 逐字段比对: 0 处差异" % len(items))
    print("   status 未动 (仍 open) ⇒ 由 advance.py --apply 落 fixing (先落 fixing 再 spawn)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
