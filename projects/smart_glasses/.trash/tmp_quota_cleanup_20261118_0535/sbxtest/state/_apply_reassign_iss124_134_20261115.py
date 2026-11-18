#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-15 21:3x 后继计划轮 · main 改派 + 落 fixing (★先落 fixing 再 spawn★)
=====================================================================
★背景: 三个总工的在飞单 (ISS-195/205/206) 已在 21:05~21:08 全部交卷 + main 独立验收签字
  ⇒ 三个名额全部释放 ⇒ 但 sw-lead / mech-lead 名下 open = 0 (★队列真空★)
  ⇒ 从 main 名下 open 单里挑两条【"等外部回复"的假阻塞】按老板 2026-11-12 02:02 政策
    转成【自己查公开官方资料】派下去 ⇒ ★不外发·不催回信·缺口自己补★
  · ISS-124 (high, 瑞芯微 ISP 吞吐/功耗) → sw-lead  (SW 地界)
  · ISS-134 (med, JBD 角色收窄 + 光生物安全口径) → mech-lead (MECH 地界)
★ISS-199 → hw-lead 走 `advance.py --apply --only ISS-199` (不在本脚本里)
★文件交集实测 = 0: HW/ (hw-lead) · SW/ (sw-lead) · MECH/ (mech-lead)
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")

HEADER = """【项目总工派活 · 后继计划推进 · 闭环 {iid}】你是 {role}。
{body}
★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复
★并发提示 (★2026-11-15 21:3x 实测★): 同一时刻有 3 个 agent 在跑 ⇒ ★**merge.py 若报 rc=2 (并发写 STATE.yaml 冲突) ⇒ 等 30 秒重跑一次; 重跑仍红就如实报, 不要死磕** ★
"""

BRIEF_124 = """★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: 按 ★**老板 2026-11-12 02:02 新口径「不再发信，全靠自己查资料」**★, 把本单两条「等瑞芯微/RK3576 模组厂回复」**改成你自己查公开官方资料** ⇒ ★**查不到就写降级方案**★ ⇒ ★**绝不外发** ★

★★**为什么是现在 (★main 2026-11-15 21:3x 实测, 不是推测★)** ★★
· ★**原问询对象已作废**: 酷芯微/ARS45 代理线 10-29 19:20 全作废 ⇒ 原单挂在「等外部回信」上是 ★**假阻塞** ★
· ★**原问询口径本身已被裁过一轮**: 2026-11-01 20:5x main 裁决 ★**「1.9% 还是 50.7%」是伪命题**★ (两个数分属不同物理量: ISP 能力上限 vs 4K 视频像素率, 比较对象错配) ⇒ ★**剩下的真问题只有两条, 就是本单 03a / 03b'** ★
· ★**换芯到 RK3572 后口径又变了**: ISP 16M → **12M Pixel**, 需求 245.1 → **124.4 MP/s** (1080p60 直出) ⇒ ★**紧迫性从「一票否决」降到「常规确认」** ★
· ★**既有资料已经在盘上, 你的活是【把矛盾 close 掉】, 不是从零查**: `SW/ISP_SCALING_MODE.md` §6 (R-GEO-2 第 3 问) 已经写明 ★**「250 MP/s 口径下 = 98.1% 几乎无余量」 vs 「官网 497.7 MP/s 口径下 = 49.3%」 两口径差 2 倍**★ ⇒ ★**你要做的是: 查官方资料判定哪套口径成立, 或者判定两套都不成立** ★

★★**① 问 03a — ISP 像素吞吐上限 (MP/s)** ★★
· 需求侧 [推算]: 全幅 2688×1520@60 = **245.1 MP/s** · 1080p60 直出 = **124.4 MP/s** · 640×480@60 = **18.4 MP/s**
· ★**要查 [官网]**: Rockchip 官方 RK3572 Datasheet / RK3576 Brief Datasheet / Rockchip 官方 wiki 文档 / rkaiq 与 rkisp 公开仓库文档 ⇒ 找 (a) ★**ISP 每秒像素吞吐上限 MP/s**★ (b) ★**ISP 支持的最大分辨率@帧率组合**★ (c) ★**是否给出 ISP 典型/最大功耗** ★
· ★**★必须守住的一条口径纪律★**: ★**不许把「12M Pixel」当成「12M MP/s」**★ ⇒ ★**12M Pixel 是【单帧分辨率上限】, 不是【每秒处理能力】**★ ⇒ ★**结论里这两个量必须分开写, 写混了这条单就白做** ★
· ★**不许只回一句「官方没给」**★ ⇒ ★**必须给降级方案**★ (见 ③)

★★**② 问 03b' — ISP 动态功耗 vs 吞吐** ★★
· 现状 [推算]: ★**`HW/POWER_BUDGET_V3.md` 的 ISP 动态功耗地板 60mW 是按 1080p30 (62 MP/s) 反推的**★ ⇒ 若按全幅 60fps (245.1 MP/s) 重估 ⇒ ISP 动态功耗要涨 ⇒ ★**皮肤温度 43°C 红线结论可能翻案** ★ ⇒ ★**这是本单真正卡的东西, 不是 03a** ★
· ★**要查 [官网]**: 官方 datasheet 的典型/最大功耗表 (按分辨率×帧率) / 官方 ISP 功耗模型 / 公开实测 [媒体] ★
· ★**ISP 段时延侧**: `SW/SW_REQUIREMENTS.md` §"软件侧影响" 已写明 ★**「延迟预算里 ISP 段用官方口径 (E2), 不用 MP/s 推算」**★ ⇒ ★**你的结论要能喂进这个口径**: ISP 段到底占多少 ms

★★**③ 降级方案 (★查不到时的必须项, 不是可选项★)** ★★
★**必须同时给三条 (缺一条都算没做完)**: ★
· **降级方案 A (算值)**: 用官方功耗表「ISP 工作 / 待机 / 关闭」三档 × 官方帧率做**线性插值** ⇒ 把插值假设写清楚 ⇒ 标 **[推算]** ★
· **降级方案 B (反解·★这条你必须给, 它不依赖查到什么★)**: ★**用现有 `SW/tools/timing_check.py` 的现成模型反解「ISP 段最多能占多少 ms 才不破 60ms 硬线」**★ ⇒ 给出数字 (★**对模式A 与模式B 分别给**★) ⇒ ★**这条是把「推算」变成「可判」的钥匙, 老板最需要的就是这个数** ★
· **降级方案 C (实测计划)**: 要拿到真值需要什么条件 (★**哪块板 + 哪条命令 + 判据多少**★) ⇒ ★**注意: Radxa 板此刻不可达 (★2026-11-15 21:3x main 实测: mDNS `radxa-cubie-a7s.local` 解析不到, 192.168.2.3 是本机自己, 网段扫描只有网关 192.168.2.1★) ⇒ ★**所以实测计划必须写「需要一块可达的 RK357x 板」, 不许写「等板子回来」** ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. `SW/ISP_CAPABILITY_RESEARCH.md` — ①查证表 (每条: 结论 + ★**证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`**★ + 出处 URL/文档章节 + 你自己复算的依据) ②★**反解**: ISP 段在 60ms 硬线下能占多少 ms (模式A/模式B 各给) ★ ③降级方案 A/B/C ④与 `SW/ISP_SCALING_MODE.md` §6 现有「98.1% vs 49.3%」的逐条对齐 (哪套口径成立/都不成立/都不判)
2. `SW/ISP_CAPABILITY_RESEARCH.json` — 机器可读: `{"demand_mpps": {"full_2688x1520_60": 245.1, "1080p60": 124.4}, "isp_mpps_max": <值或 null>, "isp_mpps_source": "<等级+出处>", "isp_power_mw_at_mpps": {"62": <值或 null>, "124": <值或 null>, "245": <值或 null>}, "isp_ms_budget_60ms_line": {"modeA": <值>, "modeB": <值>}, "fallback": "<一句话>"}`
3. `HANDOFF/2026-11-15_sw-lead_ISS124_ISP能力与功耗自查.md` — 交卷报告 (★≤25 行: 结论先行 + 表 + ★**反解数字**★ + 复现命令输出)
4. ★**必要时** `state/fragments/sw.yaml` (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key★)

★★**⑤ 你自己的复算工具 (★不许改既有脚本★)** ★★
· ★**不许改 `SW/tools/timing_check.py` 的任何一个数 (判据阈值/护栏/自测)**★ ⇒ 它的 md5 现在是 `cdc59f554fc6c82fe2588c2845b08977` ⇒ ★**交卷前后各记一次, 必须相同** ★
· ★**要算反解就新写一个脚本** `SW/tools/isp_budget_solve.py` (★**import 现有模型, 不许复制粘贴一份阈值出来自己算**★ ⇒ ★**否则两边阈值会漂**★) ⇒ rc=0 且打印反解数字
· ★**先跑一次 `python3 SW/tools/timing_check.py` 看它到底怎么用** (★它有 `--json` / `--netlist` / `--only KEY` / `--reverse-demo` 四个参数★) ⇒ ★**命令存在性: 你要用的每条命令都必须实测存在, 不许照抄不存在的路径** ★

★★**⑥ 验收自证 (交卷前跑, 把输出贴进回复)** ★★
```
python3 SW/tools/timing_check.py                    # rc=0 (★全量跑, 看护栏全绿★)
python3 SW/tools/isp_budget_solve.py                # rc=0 (★打印反解★)
python3 state/merge.py                              # rc 必须 0
python3 state/gate_check.py                         # rc=0, 【Q1】必须 18/18
md5sum SW/tools/timing_check.py HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```
★**md5 期望 (不许变)**: `SW/tools/timing_check.py` `cdc59f554fc6c82fe2588c2845b08977` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ★

★★**⑦ 边界 (不许越)** ★★
· ★**不许写 `HW/` 下任何文件** (★`HW/POWER_BUDGET_V3.md` 是 hw-lead 的地界 ★ ⇒ ★**只报不改, 由 main 转交**★)
· ★**不许碰**: `SW/DEMO_OD_TIMING_SPEC.md` · `SW/ISP_SCALING_MODE.md` (★**只许引用, 不许改**★) · `SW/SW_REQUIREMENTS.md` · `HW/e2e_budget_rk3572.py` · `HW/netlist_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` · `state/outbox/` 下任何草稿 (★**只留档, 永不发**★) · `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**★)
· ★**实物 [实测] 仍然是 0 条** ⇒ ★**你产出的所有数字要么 [官网], 要么 [推算], 要么 [0数据] ⇒ 不许写 [实测]** ★
· ★**交卷 ≤ 25 行** (结论先行 + 表 + 反解数字 + 复现命令输出) ★"""

BRIEF_134 = """★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: 按 ★**老板 2026-11-12 02:02 新口径「不再发信，全靠自己查资料」**★, 把「走鹃Ⅱ / JBD 问询」这条外部依赖**改成你自己查公开官方资料 + 自己重建判据口径** ⇒ ★**查不到就写降级方案**★ ⇒ ★**绝不外发** ★

★★**为什么是现在 (★main 2026-11-15 21:3x 实测, 不是推测★)** ★★
· ★**ISS-016 / ISS-048 / ISS-004 / ISS-013 现在全是 `deferred` 且 owner=`jbd`** (★2026-11-15 21:3x main 实测 issue_log★) ⇒ ★**它们挂着的理由是「等 JBD 回信」⇒ 按 11-12 政策这已经是假阻塞** ★
· ★**但老板锁死 #19「MIPI-DSI 输入的光机由 JBD 的蜂鸟提供」与 #21「光机型号 = 走鹃Ⅱ」已作废** ★ ⇒ ★**显示件从 JBD 走鹃Ⅱ 换成了 视涯 0.49" SiOLED 面板** ⇒ ⇒ ★**所以本单不是「去问 JBD」, 是「自己把口径重建出来」** ★

★★**① ISS-048 光生物安全判据 V2 (★核心交付★)** ★★
· ★**旧口径 (已作废)**: 走鹃Ⅱ 是 **LED 点光源** ⇒ 问 LED 波长 / 亮度 / 光通量 / 辐亮度 ★
· ★**新现实**: ★**硅基 OLED 是面光源自发光, 且蓝光 ~460nm 在衍射光波导里散射** ★ ⇒ ⇒ ★**判据表必须重建** ★
· ★**你要建的判据表 (每条都要: 判据名 / 数值(若有) / 证据等级 / 出处 / 怎么测 / 查不到时的降级方案)**: ★
  ① 出光面辐亮度 (Cd/m²) ② 光谱分布与蓝光峰值波长 / 蓝光占比上限 ③ 45–50°C 下的亮度衰减 (硅基 OLED 高温下亮度衰减是已知现象 ⇒ 判据要给限值) ④ IEC 62471 要出哪几个条款 / 哪几个报告 ⑤ 观察距离与视场角 (结合视涯 0.49" 面板的实际出光面) ⑥ 波导散射后对观察者的等效辐亮度怎么折算 ★
· ★**查什么**: 官方标准摘要 (IEC 62471 / GB/T 20145 公开摘要) / 视涯官方公开规格 (★**只查公开资料, 不发问询**★) / 公开的 OLED + 衍射光波导 光生物安全评估文献 [媒体] ⇒ ★**查不到就写 [0数据] + 降级方案 (用什么可测的近似量代替)** ★
· ★**已有交叉参考 (★只读, 不许改★)**: `HW/DISPLAY_MODULE_DECISION.md` · `HW/EMC_PRECHECK.md` · `SW/INTEGRATION_PLAN.md` · `FRAMEWORK_SCOPE.md` ★**这 4 份是别的地界 (HW/SW) ⇒ 只许引用, 不许改** ★

★★**② JBD 角色收窄 (文档口径)** ★★
· 角色收窄为 ★**只保留「波导」**★ ⇒ 走鹃Ⅱ / 蜂鸟光机 / ISS-016 三条全部标作废 ⇒ ★**把「作废了什么、保留了什么、对哪个 issue 有什么影响」写清楚** ★
· ★**只改 MECH 侧文档** ⇒ ★**根目录 `JBD_QUESTION_LIST.md` 是 main 的地界 ⇒ 只报不改** ★ ⇒ ★**`state/outbox/` 下所有草稿一律不发, 只留档** ★

★★**③ 波导归属的可查部分 (★老板级归属你不许决定★)** ★★
· 要查 [官网]: ★**衍射光波导市场上有谁在售** (JBD 官网产品线 / 其他公开在售供应商 / 公开规格) ⇒ 给出「★**波导是不是必须找 JBD**」这个问题的**可查结论** ★
· ⇒ ⇒ ★**老板要拍的那一维 (最终选谁) 你只列 2~3 个候选 + 各自取舍 + 你的建议, 不替老板定** ★
· ★**同时**: ISS-004 / ISS-013 现在是 `deferred` 且理由是「等 JBD」⇒ ★**你的结论若能把它变成「可自选」或「必须 JBD」, 就写清楚这一条的影响** ★

★★**④ 交付物 (★只写这些★)** ★★
1. `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` — 判据表 (每条: 判据 / 数值 / ★**证据等级**★ / 出处 / 怎么测 / 查不到时的降级方案) + §"与旧口径 (ISS-048 · LED 点光源) 的逐条差异"
2. `MECH/JBD_ROLE_NARROWING.md` — 角色收窄记录 (作废清单 / 保留项 / 波导归属的可查结论 / ★**老板待拍板那一维的候选表 + 建议**★)
3. `HANDOFF/2026-11-15_mech-lead_ISS134_显示口径与光生物安全V2.md` — 交卷报告 (★≤25 行★)
4. ★**必要时** `state/fragments/mech.yaml` (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key★)

★★**⑤ 验收自证 (交卷前跑, 把输出贴进回复)** ★★
```
python3 state/merge.py        # rc 必须 0
python3 state/gate_check.py   # rc=0, 【Q1】必须 18/18
grep -rn "走鹃" MECH/*.md      # ★只允许出现在「已作废 / 历史沿革」语境★
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```
★**md5 期望 (★只作对照, 本单不该碰它们★)**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ★

★★**⑥ 边界 (不许越)** ★★
· ★**不许碰**: `HW/DISPLAY_MODULE_DECISION.md` · `HW/EMC_PRECHECK.md` · `SW/INTEGRATION_PLAN.md` · `FRAMEWORK_SCOPE.md` · 根目录 `JBD_QUESTION_LIST.md` · `state/outbox/` 下任何草稿 (★**只留档, 永不发**★) · `MECH/USB_HINGE_STRUCTURE.md` (★**那是 ISS-199/ISS-206 已定版的地界★) · `MECH/BOARD_GEOM_30MM.md` · 任何 `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**★)
· ★**实物 [实测] 仍然是 0 条** ⇒ ★**你产出的所有数字要么 [官网], 要么 [媒体], 要么 [推算], 要么 [0数据] ⇒ 不许写 [实测]** ★
· ★**交卷 ≤ 25 行** (结论先行 + 两张表 + 复现命令输出) ★"""

REASSIGN = [
    ("ISS-124", "sw-lead", "软件总工", BRIEF_124),
    ("ISS-134", "mech-lead", "结构总工", BRIEF_134),
]


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {i.get("id"): i for i in issues}

    for iid, owner, role, brief in REASSIGN:
        it = by_id[iid]
        assert it.get("status") == "open", "%s status=%s 非 open" % (iid, it.get("status"))
        it["owner"] = owner
        it["status"] = "fixing"
        it["verify_by"] = "main"
        it["dispatched_at"] = "2026-11-15"
        it["task_brief"] = brief
        it["note"] = (it.get("note") or "") + (
            "\n★**【2026-11-15 21:3x 项目总工 (main) 改派 + 落 fixing】**\n"
            "★**依据 (★三条全查过, 不是推测★)**:\n"
            "  ① ★**本单原来是「等外部回复」的假阻塞** ★ (原 owner=main · 原 verify_by=hw-lead · 原口径「外发一律经项目总工, 老板放行才发」)\n"
            "     ⇒ ★**老板 2026-11-11 19:31 + 2026-11-12 02:02 已把这条封死: 不再发信, 全靠自己查资料** ★ ⇒ ★**本单改为【自己查公开官方资料 + 查不到写降级方案】** ★\n"
            "  ② ★**sw-lead / mech-lead 名下 open = 0 (★队列真空★)** ⇒ ★**本单是主线内可干的纯查资料活 (★不是 PCB 布线/布局类 ⇒ 不违反老板 2026-11-11 10:07 口径★)** ★\n"
            "  ③ ★**文件交集实测 = 0**: hw-lead 只写 `HW/` (ISS-199) · sw-lead 只写 `SW/` · mech-lead 只写 `MECH/` ⇒ ★**三个写会话地界不重叠, 撞不了 R18 (分片合并丢 12%~38%)** ★\n"
            "★**本单只改: owner / status / verify_by / task_brief / dispatched_at** ⇒ ★**desc / title / due / severity 一个字没动** ★\n"
        )

    shutil.copy2(LOG, LOG + ".bak_20261115_2130_reassign")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    # 派活日志
    dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
    for iid, owner, role, brief in REASSIGN:
        dl.setdefault("dispatches", []).append({
            "issue": iid, "agent": owner, "at": "2026-11-15",
            "brief": brief[:300]})
    shutil.copy2(DL, DL + ".bak_20261115_2130")
    with open(DL, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)

    print("改派+落 fixing:", ", ".join("%s→%s" % (a, b) for a, b, _c, _d in REASSIGN))


if __name__ == "__main__":
    main()
