#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1050_open_iss238_reassign_iss172.py
★main (moli) 2026-11-16 10:5x (cron 775d9893 继续执行后继计划)★
★新开 ISS-238 (mech-lead · 光生物安全 C1 门禁红) + ISS-172 改派 sw-lead (负载开关选型证据矩阵)★

★★**为什么是这两条 (★main 本轮 10:4x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**advance.py 的 internal 段是空的** (三个总工名下 open = 0; hw-lead 有 ISS-237 fixing 且会话在跑) ⇒ ★**本轮自己找活**
· ★**main 本轮把全仓 47 个 check 脚本逐个实跑了一遍 (★用正确的入口★)** ⇒ ★**抓到 1 盏【隐形红】** ★
· ★**ISS-238**: `python3 MECH/display_biosafety_v2_check.py` ⇒ **rc=1**, [C1] 活动口径 = 5 (必须 0) ⇒ ★**5 行全在 `MECH/MECH_BUDGET.md` (L71/94/849/880/944)**★
  ⇒ ★**这盏红不在 daily_check 链上 (★grep: daily_check 只引用 check_pcb_nets.py★) ⇒ 巡检看不见 = 隐形红 (ISS-213 同款)** ★
· ★**ISS-172**: 网表 L50 `U_PWR_SW` 的 value 栏至今是 ★**"[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)"**★ ⇒ ★**主板 BOM 出不来 OPN; 决策页 A5 卡在"老板先拍优先级序"⇒ 缺的正是【官方参数证据矩阵】**★

★★**边界 (两条单共同的)★★ ★★
★零外发 (老板 2026-11-12 02:02: 不再发信, 全靠自己查资料) · ★不改 PROJECT_TRACKER.md §0 · ★不写别人的分片 · ★不碰 PCB 布线/布局/板框 · ★不替老板拍板
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

TITLE_238 = (
    "★★[主线内·结构/判据侧·内部活] ★★`MECH/display_biosafety_v2_check.py` C1 红灯 (走鹃旧口径 活动口径=5) "
    "⇒ 4 处假阳性 (判据只认单一标注串) + 1 处真漏标 (L880) ⇒ 文档侧补标 + 判据侧放宽提案 + 新机器门禁"
)

DESC_238 = (
    "★main 2026-11-16 10:4x 自己实跑出来的 (★全仓 47 个 check 脚本逐个跑, 用正确入口★) ★\n"
    "★**① 红灯本体**: `python3 MECH/display_biosafety_v2_check.py` ⇒ **rc=1** ⇒\n"
    "  `[C1] 走鹃旧口径收口 (5 份旧文档) FAIL` · `活动口径 = 5 (必须 0) ; 历史沿革 = 31` ·\n"
    "  逐文件(活动/历史): MECH_BUDGET.md 5/23 · PROTOTYPE_PLAN.md 0/3 · SOC_CARRIER_EVAL.md 0/1 · "
    "STRUCT_REVIEW_ISS065.md 0/3 · CLEARANCE_FIX.md 0/1 ·\n"
    "  违规行: **MECH/MECH_BUDGET.md:71, :94, :849, :880, :944** (★C2/C3/C4/C5 全 PASS★)\n"
    "★**② 判据怎么算的 (脚本实读)**: `MECH/display_biosafety_v2_check.py` 第 40 行 `MARKER = \"已作废 (2026-11-15, ISS-134 V2)\"` "
    "⇒ 第 95~120 行 `check_c1()`: 逐行扫 5 份旧文档, ★**行内含「走鹃」且不含这个【单一字符串】⇒ 记「活动口径」⇒ FAIL**★; "
    "含该串 ⇒ 记「历史沿革」⇒ 允许。\n"
    "★**③ main 逐行读了那 5 行原文 ⇒ 4 处是【假阳性】+ 1 处是【真漏标】**: ★\n"
    "  · L71 = 「★**已作废 (ISS-222 · 2026-11-16, C-6 落地)**: 上面这段按走鹃Ⅱ 2.9 mm 光束推的; … 只作历史沿革, 活口径见 §1.3 M6 + §1.10.1」 ⇒ ★**有作废标注, 只是不是那个字符串**★\n"
    "  · L94 = M6 行 ⇒ 「旧行 ~14×10×6 / 0.79 cc 是走鹃Ⅱ 2.9 mm 光束口径, **已作废** (依据 MECH/CENTER_CAVITY_REBALANCE_V3.md §1 + MECH/cavity_recalc_check.py C13/C18)」 ⇒ ★**同上**★\n"
    "  · L849 = W4 行 ⇒ 「★**旧值 3-6 g 是走鹃Ⅱ 2.9 mm 光束口径, 已作废**」 ⇒ ★**同上**★\n"
    "  · L944 = 「★**已作废 (ISS-222 · C-6 落地)**: … 「14×10×6 的光学舱」是走鹃Ⅱ 口径, 活口径见 §1.3 M6 / §1.10.1」 ⇒ ★**同上**★\n"
    "  · ★**L880 = 「> - **为什么这不是「预扣」**: … (分光件从走鹃Ⅱ 口径 14×10×6 放大到 平板 11×11×1.5 + 棱镜 2×9×9×5, 体积 0.79 → 0.9697 cc) …」⇒ ★★**这行一个作废标注都没有** ⇒ 【真漏标】★★★\n"
    "★**④ 根因 (为什么要提【判据侧】)**: ★**判据只认一个硬编码字符串 ⇒ ISS-222 引入的作废标注形态不被认 ⇒ 同一个事实两种写法, 门禁只认一种** ★\n"
    "  ⇒ ★**下一个 ISS-2xx 再写一种作废标注, 这盏红会再次亮** ⇒ ★**这是判据口径问题, 不是文档脏**★\n"
    "★**⑤ 为什么这盏红危险**: ★**它不在 daily_check 链上** (★main 实测: `grep daily_check.py` 只有 `check_pcb_nets.py`★) ⇒ ★**巡检 rc=3 也看不见它** ⇒ "
    "★**「光生物安全旧口径已收口」这句话现在没有机器背书** (★ISS-213 同款「隐形红」★)★\n"
    "★**⑥ 本单要做的三件事**: ★**① 文档侧补标 (主修复, 不改受保护脚本) ② 判据侧放宽提案 (只出文档, 不改受保护脚本 ⇒ 交 main 决定是否走 H-1 重基线) ③ 新建一个不依赖受保护脚本的机器门禁 + 反向用例** ★"
)

BRIEF_238 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**`MECH/display_biosafety_v2_check.py` C1 那盏红灯转绿**★ ⇒ ★**拆成「4 处假阳性 + 1 处真漏标」分别处理**★ ⇒ ★**文档侧补标 + 判据侧放宽提案 (交 main) + 一个不依赖受保护脚本的新机器门禁 (带反向用例)**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 10:4x 自己实跑, 不是推测★)** ★★
· ★**main 把全仓 47 个 check 脚本逐个实跑了一遍** (★`state/check_footprint_geom.py` 那个 ModuleNotFoundError 是 main 用错入口 (它要 `bash state/pcbnew_py.sh …`), 实跑 rc=0 几何全对 ⇒ **不是缺陷, 不许去"修"它**★) ⇒ ★**真抓到 1 盏隐形红: `MECH/display_biosafety_v2_check.py` rc=1** ★
· ★**红灯原文 (逐字)**: `[C1] 走鹃旧口径收口 (5 份旧文档) FAIL` · `活动口径 = 5 (必须 0) ; 历史沿革 = 31` · `违规行: MECH/MECH_BUDGET.md:71, :94, :849, :880, :944` (★C2/C3/C4/C5 全 PASS★) ★
· ★**判据怎么算的 (脚本实读)**: `MECH/display_biosafety_v2_check.py` L40 `MARKER = "已作废 (2026-11-15, ISS-134 V2)"` ⇒ L95~120 `check_c1()`: 行内含「走鹃」且★**不含这个单一字符串**★⇒ 记「活动口径」⇒ FAIL; 含 ⇒ 记「历史沿革」⇒ 允许 ★
· ★**main 逐行读了那 5 行 ⇒ 4 处假阳性 + 1 处真漏标** (★逐条原文在 issue 的 desc 里, 自己再去盘上核对一遍, 不许照抄★)
· ★**这盏红不在 daily_check 链上** (★`grep -n "display_biosafety" state/daily_check.py` ⇒ 0 命中★) ⇒ ★**巡检看不见 ⇒ 「走鹃旧口径已收口」这句话现在没有机器背书** ★

★★**① 文档侧补标 (★主修复·不许删改实测原文★)** ★★
· ★**只许动 `MECH/MECH_BUDGET.md` 的那 5 行 (L71 / L94 / L849 / L880 / L944)★** ⇒ ★**逐字追加 canonical 标注 `已作废 (2026-11-15, ISS-134 V2)` (脚本认的就是这一串)★**
· ★**L71 / L94 / L849 / L944 = 假阳性**: 它们★**已经带了作废标注**★ (ISS-222 · C-6 落地形态) ⇒ ★**canonical 标注是【追加】(两个标注并存), 语义真实**: 走鹃Ⅱ 2.9 mm 光束口径★**自 ISS-134 V2 (11-15) 起即作废**★ ⇒ ★**不许因为"已经有标注了"就跳过这 4 行** ★
· ★**L880 = 真漏标**: 这行★**一个作废标注都没有**★ ⇒ ★**除了补标注, 还要把行内「走鹃Ⅱ 口径 14×10×6」明确写成历史口径 (加限定语), 让它自己站得住** ★
· ★**绝对不许**: ★**删行 / 删数值 / 改口径内容 / 改 M6 W4 等表里的任何数字**★ ⇒ ★**删掉 = 失去「当初为什么这么选」的留痕 (★本项目的判据本体只许加不许放宽★)** ★
· ★**不许改**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (md5 96239070… · C5 硬判据) · `MECH/JBD_ROLE_NARROWING.md` (md5 bda4a294…) · `MECH/display_biosafety_v2_check.py` (md5 29c77fc3… · ★**在 `MECH/check_demo_struct_truth.py` 的受保护清单里**★) · `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` 的 33 行定性表 (★**C4 查它: 33 行 + 分布 21/6/3/2/1 ⇒ 不许改结构/分布, 不许增删行★) ★
· ★**改 `MECH/MECH_BUDGET.md` 前先查锚点**: ★**main 已实测: 全仓没有任何地方锚着 `MECH_BUDGET.md` 的 md5 (grep `1b4ae5d8…` ⇒ 0 命中) ⇒ 不需要走 H-1 重锚**★ ⇒ ★**但你改之前自己再 grep 一次 (★万一并发会话刚加了锚点★)** ★

★★**② 判据侧放宽提案 (★只出文档, 不许改受保护脚本★)** ★★
· ★**新建** `MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md` ⇒ ★**写清三件事**: ★**① 病灶**: MARKER 只认单一字符串 ⇒ 作废标注形态每多一种就再打红一次 (★ISS-222 形态已经打过一次★) ★**② 建议口径** (★给 2~3 个可选方案, 不许只给一个★): 例如 ① 改成 regex「已作废」+ (日期 或 ISS 号) 任意一种都算历史沿革 ② 改成「已作废」或「作废」或「历史沿革」或「旧口径」四选一 ③ 维持单一字符串 + 加一条"新增作废标注形态必须同步进 MARKER 清单"的流程约束 ★**③ 每条建议都要给反向用例设计** (★怎么证明放宽后仍能抓住真漏标★): 例如 ★**「把 L880 的标注删掉 ⇒ 必须红」/「把某行的标注换成另一种形态 ⇒ 按你建议的口径应该红还是绿, 说清楚」** ★
· ★**★不许自己改 `MECH/display_biosafety_v2_check.py`★** ⇒ ★**放宽判据要走 H-1 重基线 (改脚本 + md5 台账 + 反向用例 + 留痕), 那是 main 的活** ★ ⇒ ★**本单只交提案** ★
· ★**提案里必须写明一条底线**: ★**放宽的只是「什么算作废标注」, 不许放宽成「有走鹃字样就算过」⇒ 裸走鹃命中必须仍然是红** ★

★★**③ 新机器门禁 (★不许靠受保护脚本, 新建一个★)** ★★
· ★**新建** `MECH/check_zoujuan_marker_consistency.py` ⇒ ★**至少查 5 条**: ★
  ① **5 份旧文档里含「走鹃」的行必须全部带 canonical MARKER** (活动口径 = 0) ⇒ 逐行点名
  ② ★**canonical MARKER 串本身必须存在于文档里** (★否则门禁自己失效了都没人知道★)
  ③ ★**`MECH/MECH_BUDGET.md` 里不许出现【无标注的裸走鹃命中】** (★L880 这类 = 真漏标★)
  ④ ★**「作废标注形态」清单**: 把当前盘上实际出现过的作废标注形态 (★ISS-134 V2 串 / ISS-222 串 / 裸「已作废」/ 其它你扫到的★) 列成清单 ⇒ ★**与提案文件里的清单对得上** (★两份不许各写各的★)
  ⑤ ★**受保护文件 md5 未变** (★`display_biosafety_v2_check.py` 29c77fc3… · `DISPLAY_BIOSAFETY_CRITERIA_V2.md` 96239070… · `JBD_ROLE_NARROWING.md` bda4a294… · `check_demo_struct_truth.py` fa9b59e5…★)
· ★**rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**必须支持 `--selftest`, ★≥5 条反向用例★ (★建议: 删掉 L880 的标注 ⇒ ③ 红 · 删掉某行的 canonical 标注 ⇒ ① 红 · 把 canonical 标注串从脚本/文档里删掉 ⇒ ② 红 · 篡改提案清单使其与文档形态对不上 ⇒ ④ 红 · 篡改判据文件 ⇒ ⑤ 红★) ★
· ★**★反向用例必须自证「它真的改到了目标」★** ⇒ ★**不许写一条永远绿着的假用例 (★ISS-227 同款教训: 「有断言」≠「断言有效」★)** ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**改** `MECH/MECH_BUDGET.md` (★只动那 5 行, 只加标注/限定语★)
2. ★**新建** `MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md` (★判据侧放宽提案 + 反向用例设计★)
3. ★**新建** `MECH/check_zoujuan_marker_consistency.py` (★门禁 + `--selftest`★)
4. ★**新建** `HANDOFF/2026-11-16_mech-lead_ISS238_走鹃旧口径C1门禁红.md` (★B1~B6 六块齐全★)
5. `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写: 只加 artifact/claim/answer; ★**不许删改别人的 key**★)

★★**⑤ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 MECH/display_biosafety_v2_check.py` ⇒ **rc=0** 且 ★**5/5 全 PASS (含 C1 活动口径 = 0)**★
· `python3 MECH/display_biosafety_v2_check.py --selftest` ⇒ **rc=0** (★它自己那 5 个用例★)
· `python3 MECH/check_zoujuan_marker_consistency.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 且 ≥5/5**
· `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0** (★23/23 · 受保护 md5 一个没变★)
· `python3 MECH/cavity_recalc_check.py` ⇒ **rc=0** (★23/23★)
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· ★**`md5sum MECH/display_biosafety_v2_check.py MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md MECH/JBD_ROLE_NARROWING.md MECH/check_demo_struct_truth.py` ⇒ 与上面写的 4 个值逐字节一致** ★
· ★**零外发** · ★**实物 [实测] = 0 条** (★板不在本机★) · ★**没碰 PCB 布线/布局/板框** · ★**没改 PROJECT_TRACKER.md §0** · ★**没改 `state/issue_log.yaml`** (★verify_by = main★) · ★**没写别人的分片** ★

★★**⑥ 边界提醒 (★并发实况·10:5x 实测★)** ★★
· ★**hw-lead 名额在跑 ISS-237 (P2 屏口径收死) ⇒ 它在动 `HW/STEP1_PARTS_SPEC.md` / `HW/PART_ALTERNATIVES_REGISTRY.md` / `HW/check_step1_parts_spec.py` / `HW/netlist_v1*.csv` ⇒ ★**你一个 HW/ 文件都不许碰** ★
· ★**sw-lead 名额在跑 ISS-172 (负载开关选型证据) ⇒ ★**你一个 SW/ 文件都不许碰** ★
· ★**板 md5 `611b869e…` / `.kicad_pro` `3e504d2b…` / 网表 `34132f7e…` / 脚表 `b21b743a…` ⇒ 交卷时逐字节不变** ★
"""

TITLE_172 = (
    "★★[主线内·硬件选型/官方口径侧·内部活] ★**负载开关 U_PWR_SW / U_EN_SW 选型证据矩阵** "
    "(★网表 L50 value 栏至今是「[待选型] …」⇒ 主板 BOM 出不来 OPN★) ⇒ ≥3 候选 × `HW/POWER_SHUTDOWN_V3.md §2` 八条判据逐条对照 + RCB 缺口做实 + 降级方案 + 机器门禁"
)

BRIEF_172 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**负载开关 U_PWR_SW / U_EN_SW 的选型从「[待选型] 一句话」变成「可拍板的证据矩阵」**★ ⇒ ★**≥3 个原厂在售候选 × `HW/POWER_SHUTDOWN_V3.md §2` 的 8 条判据逐条对照 (每格带官方数值 + 出处 + 证据等级) + 把「无 RCB (反向电流阻断)」这个缺口做实 + 同封装可否换料 + 降级方案 + 一个机器门禁**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 10:4x 逐行实读, 不是抄交卷报告★)** ★★
· ★**网表 `HW/netlist_v1.csv` L50 (U_PWR_SW 本体行)** = `P1,SYS,U_PWR_SW pin3,RAIL_SYS,U_PWR_SW,"[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",IC,必装,[推算],…` ⇒ ★**value 栏至今是一个判据串, 不是型号 ⇒ 主板 BOM 出不来 OPN** ★
  · 同行的封装栏 = ★**`UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch`**★ · MPN 栏 = `TPS22991RAA` · note 里 ★**「选型判据 8 条见 HW/POWER_SHUTDOWN_V3.md §2 (型号待选型, 询价经项目总工)」**★
· ★**网表 L442 (U_EN_SW 本体行)** = `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)` · note 里 ★**「选型 = TPS22991RAA (项目总工 11-03 已裁, ISS-172 待老板点头; 同 UQFN-4 封装 ⇒ 若改 TPS22916/17 = 换料不换板)」**★
· ★**决策页 `DECISION_PENDING_2026-11-16.md` §A5 = 「原厂在售型号的判据互斥: RON vs IQ vs 反向阻断 ⇒ 没有单一冠军」⇒ ★**老板要先拍【优先级序】(不是拍型号) ⇒ 缺的就是【每个候选在这三条上的官方数】** ★
· ★**ISS-234 已交卷 (sw-lead 07:02)**: `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 给了 Q2 推荐 = ★**`TPS22991RAA`** (同封装 ⇒ 可换料不换板) + ★**要求登记「无 RCB (反向电流阻断)」这个缺口** ★
  ⇒ ★**本单不重复 ISS-234 的活**: ★**ISS-234 给的是【推荐 + 缺口名】, 本单要补的是【缺口做实: 到底哪些原厂在售型号带 RCB + 它们的官方参数 + 同封装能否换料 + 无解时的降级方案】** ★
· ★**政策 (老板 2026-11-12 02:02)**: ★**不再发信, 全靠自己查资料** ⇒ ★**官网/数据手册自己查, 每条标 [官网]/[实测]/[媒体]/[推算]/[0数据] ⇒ 查不到就写 [0数据] + 降级方案, 不许编** ★

★★**① 候选矩阵 (★≥3 个候选, 一行都不许少★)** ★★
· ★**候选必须是【原厂在售】的负载开关 / 电源开关**, 至少含: ★**TI TPS22991 / TPS22916 / TPS22917 (★这三个是网表/ISS-234 点名的同族★) + ★**带 RCB (反向电流阻断) 的型号 (★TI TPS22918 / TPS22919 一类, ★**具体是不是带 RCB 以官方数据手册为准, 不许凭印象★**) + ★**国产同档型号 (★至少 1 个, 要官网数据手册级参数★)** ★
  ⇒ ★**候选不够 3 个就把「查到的全部」写上 + 一行写明「官方在售型号总数只有 N 个, 不足 3」** ★
· ★**逐候选 × 八条判据逐格填满 (★八条判据原文照抄 `HW/POWER_SHUTDOWN_V3.md §2`, 不许改判据★)**: ★**RON (含测试条件: Vin 几伏?)、IQ/静态电流 (typ 与 max 分列)、额定电流、是否带 RCB (★有/无/查不到★)、封装 (★是不是 UQFN-4 RAA 0.85×0.75 0.4mm pitch ⇒ 能不能直接换料不换板★)、引脚定义 (★1=VIN/2=ON/3=VOUT/4=GND 是否与网表一致, 不一致要写明差异★)、上电/掉电时序与 ON 脚行为、绝对最大额定 + 温度范围** ★
· ★**每格必须带**: ★**官方数值 + 出处 (数据手册章节/表格/页码 + URL) + 证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据])** ★ ⇒ ★**没有出处的格子 = 没查, 不许填「大概/应该」★ ★
· ★**RCB 专项小节**: ★**逐候选写清「有/无/查不到」+ 官方依据原文摘录 (★原文摘录, 不是你的转述★)** ★

★★**② 建议 + 降级方案 (★给依据, 不代拍★)** ★★
· ★**按决策页 A5 建议的优先级序 (① 反向阻断 > ② IQ<5µA > ③ RON 越小越好 > ④ 封装/面积) 打分排序, 给推荐 + 逐条依据** ★
· ★**★不许替老板拍优先级序 / 不许替老板拍型号★** ⇒ ★**明确写「本单只交证据 + 按 A5 建议序的推荐, 最终拍板 = 老板」** ★
· ★**★必须给降级方案★** (★至少 2 条, 且必须覆盖「★没有同封装且带 RCB 的在售型号★」这个最坏情形★): 例如 ① 换封装 (★改板 ⇒ 板那一趟必须排进去★) ② 外部反灌保护 (★加 MOS / 肖特基 / 理想二极管, 要算压降与静态功耗★) ③ 接受无 RCB + 改拓扑/记缺口 + 写明触发条件 ④ 换 SoM/电池方案 (代价最大, 但要写进对比) ★
· ★**每条降级方案要带: 改了什么 · 代价 (面积/静态电流/压降/工艺/延期) · 适用条件 · 出处或推算依据** ★

★★**③ 机器门禁 (★本单必须留一个能自动复核的东西★)** ★★
· ★**新建** `SW/tools/check_load_switch_selection.py` ⇒ ★**至少查 6 条**: ★
  ① 候选数 ≥3 (★或存在「官方在售型号总数只有 N 个」的白名单说明★)
  ② ★**八条判据逐条非空** (★不许有空格/「待查」/「TBD」★) + 每条都有出处
  ③ 证据等级只能取 ★**[官网]/[实测]/[媒体]/[推算]/[0数据]** 五者之一 (★其它词一律红★)
  ④ ★**每个候选的 RCB 判定字段非空** (有/无/查不到 三选一)
  ⑤ ★**结论若是「没有同封装带 RCB 的在售型号」⇒ 必须同时存在 ≥2 条降级方案★**
  ⑥ ★**ISS-234 点名的 `TPS22991RAA` 必须在册** (★不许把前人的候选悄悄删掉★) + ★**网表 L50 的 `[待选型]` 判据串与矩阵八条判据逐条对得上 (★不许矩阵与判据串各说各话★)**
· ★**rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**必须支持 `--selftest`, ★≥5 条反向用例** (★建议: 删一条判据 ⇒ 红 · 把证据等级改成非法词 ⇒ 红 · 把候选砍到 2 个 ⇒ 红 · 删掉降级方案 ⇒ 红 · 把某候选的 RCB 判定清空 ⇒ 红 · 删掉 TPS22991RAA ⇒ 红★) ★
· ★**★反向用例必须自证「它真的改到了目标」★** (★ISS-227 同款教训★) ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**新建** `SW/LOAD_SWITCH_SELECTION_FACTS.md` (★候选矩阵 + RCB 专项 + 建议 + 降级方案 + 出处表★)
2. ★**新建** `SW/tools/check_load_switch_selection.py` (★门禁 + `--selftest`★)
3. ★**新建** `HANDOFF/2026-11-16_sw-lead_ISS172_负载开关选型证据矩阵.md` (★B1~B6 六块齐全★)
4. `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写: 只加 artifact/claim/answer; ★**不许删改别人的 key**★)
· ★**★不许落表 (不许改网表/脚表/BOM/板)★** ⇒ ★**网表 L50 的 `[待选型]` 串要等老板拍完再由落表批次改 ⇒ 本单只交证据** ★

★★**⑤ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 SW/tools/check_load_switch_selection.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 且 ≥5/5**
· `python3 SW/tools/check_shutdown_semantics.py` ⇒ **rc=0** (★ISS-234 的门禁, 不许被你打红★) · `--selftest` ⇒ rc=0
· `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** · `python3 SW/tools/demo_timing_check.py` ⇒ rc=0 · `python3 SW/tools/demo_e2e_budget.py` ⇒ rc=0
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· ★**`md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb` ⇒ 逐字节不变 (34132f7e… / b21b743a… / c195a117… / 611b869e…)** ★
· ★**零外发** (★没发任何邮件/询价/问询/采购, 没联系任何供应商★) · ★**实物 [实测] = 0 条** · ★**没碰 PCB 布线/布局/板框** · ★**没改 `state/issue_log.yaml`** (★verify_by = main★) · ★**没写别人的分片** ★

★★**⑥ 边界提醒 (★并发实况·10:5x 实测★)** ★★
· ★**hw-lead 名额在跑 ISS-237 (P2 屏口径收死) ⇒ 它在动 `HW/STEP1_PARTS_SPEC.md` / `HW/PART_ALTERNATIVES_REGISTRY.md` / `HW/check_step1_parts_spec.py` ⇒ ★**你一个 HW/ 文件都不许碰 (★连新建文件都不许: 那是 HW 的地界★)** ★
· ★**mech-lead 名额在跑 ISS-238 (走鹃旧口径 C1) ⇒ ★**你一个 MECH/ 文件都不许碰** ★
· ★**`HW/POWER_SHUTDOWN_V3.md` 只许读, 不许改** (★它是老板/项目总工的判据文档★) · ★**`SW/SHUTDOWN_SEMANTICS_SPEC.md` (ISS-234 交卷件) 只许读, 不许改** ★
"""


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {it.get("id"): it for it in issues}

    # ---------------- 新开 ISS-238 (mech-lead) ----------------
    assert "ISS-238" not in by_id, "ISS-238 已存在, 不重复开"
    issues.append({
        "id": "ISS-238",
        "title": TITLE_238,
        "severity": "high",
        "source_blocker": None,
        "desc": DESC_238,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": BRIEF_238,
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-16 10:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 10:4x 自己实跑** "
            "(全仓 47 个 check 脚本逐个实跑, 用正确入口 `bash state/pcbnew_py.sh …`; "
            "MECH/display_biosafety_v2_check.py rc=1 ⇒ C1 活动口径=5, 违规行 MECH_BUDGET.md:71/94/849/880/944; "
            "脚本 L40 MARKER 只认单一字符串 + 逐行读那 5 行原文 ⇒ 4 假阳性 + 1 真漏标) ★\n"
            "★**该红灯不在 daily_check 链上 ⇒ 巡检看不见 = 隐形红 (ISS-213 同款)** ★\n"
            "★**本单是主线内 (结构/判据侧), 一条 PCB 布线/布局都不碰** ★\n"
            "★**受保护脚本 `MECH/display_biosafety_v2_check.py` (md5 29c77fc3…) 不许直接改 ⇒ 判据侧放宽只交提案给 main** ★\n"
            "★**零外发** · ★**没替老板拍任何东西** ★"
        ),
        "dispatched_at": None,
    })

    # ---------------- ISS-172: main → sw-lead (改派 + 补 brief) ----------------
    it172 = by_id.get("ISS-172")
    assert it172 is not None, "ISS-172 不存在"
    assert it172.get("status") == "open", "ISS-172 状态不是 open: %s" % it172.get("status")
    old_owner = it172.get("owner")
    it172["owner"] = "sw-lead"
    it172["title"] = TITLE_172
    it172["task_brief"] = BRIEF_172
    it172["severity"] = "high"
    it172["note"] = (it172.get("note") or "") + (
        "\n2026-11-16 10:5x (cron 775d9893 继续执行后继计划) ★**改派 main → sw-lead**★ "
        "(★依据 = main 本轮 10:4x 逐行实读 `HW/netlist_v1.csv` L50/L442 + `HW/POWER_SHUTDOWN_V3.md` §2 + 决策页 §A5★) "
        "⇒ ★**理由: 这单的活是【自己查官方资料做证据矩阵】(★老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料★), "
        "不是 main 坐等拍板, 也不是 PCB 类 ⇒ 适合 sw-lead (★ISS-228 同型: 硬件选型/官方口径侧自查★)** ★\n"
        "★**ISS-234 交卷给的是【推荐 TPS22991RAA + 缺口名】; 本单补的是【缺口做实: 哪些原厂在售型号带 RCB + 官方参数 + 同封装能否换料 + 降级方案】** ★\n"
        "★**拍板仍在老板 (§A5: 先拍优先级序, 不是拍型号) ⇒ 本单不许代拍** ★ "
        "★**本单不许落表 (不改网表/脚表/BOM/板)** ★"
    )

    # 备份 + 原子写
    bak = os.path.join(HERE, "issue_log.yaml.bak_20261116_1050_open_iss238_reassign_iss172")
    shutil.copy2(LOG, bak)
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))

    # 派活备料
    atomic_write(os.path.join(HERE, "tasks", "advance_iss238.md"), BRIEF_238)
    atomic_write(os.path.join(HERE, "tasks", "advance_iss172.md"), BRIEF_172)

    print("✅ ISS-238 已开 (owner=mech-lead, status=open, due=2026-11-19)")
    print("✅ ISS-172 改派 %s → sw-lead (status 仍 open, 待 advance.py --apply --only 标 fixing)" % old_owner)
    print("   备份: %s" % bak)
    print("   备料: state/tasks/advance_iss238.md / state/tasks/advance_iss172.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
