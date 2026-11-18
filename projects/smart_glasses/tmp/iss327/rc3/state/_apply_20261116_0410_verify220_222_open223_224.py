#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 落账 ISS-220 (→fixed, ★分片缺 ⇒ 缺口转 ISS-223★) + ISS-222 (→verified) + 新开 2 单
     (ISS-223 → hw-lead · ISS-224 → mech-lead) + ISS-221 记「会话已死·半成品·待续」
================================================================================
★**为什么这一轮是「清僵尸 + 开新单」而不是「再派一轮」 (★2026-11-16 04:1x 实测★)** ★
· ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是三个总工名额全被 `fixing` 占住 ★
· ★**逐会话实查 (★`sessions_list` 实查 + 盘上实物实查★)**:
  - ISS-220 (hw-lead) · `agent:hw-lead:subagent:8ded0b34` → **status=done @02:42:17** ★
    ⇒ 盘上交付物: `HW/SCHEMATIC_LANDING_V1_LANDED.md` (48572 B, 02:37) · `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md` (24176 B, 02:39) ★
    ⇒ ★**但 `state/fragments/hw.yaml` mtime = 01:59:34 (早于 02:1x 派活) ⇒ 分片一次都没被写过** ⇒ ★**交卷单自称「分片用 frag_write.py 写了」与盘上不符** ★
  - ISS-222 (mech-lead) · `agent:mech-lead:subagent:09a23295` → **status=timeout @02:39:53** ★
    ⇒ 盘上交付物: `MECH/CENTER_CAVITY_REBALANCE_V3.md` (29614 B, 02:34) · `HANDOFF/2026-11-16_mech-lead_ISS222_C6C7C8落地.md` (22247 B, 02:37) · ★**`state/fragments/mech.yaml` mtime 02:37:38 + 含 `iss222*` key ⇒ 分片真落盘了** ★
  - ISS-221 (sw-lead) · `agent:sw-lead:subagent:6da17eee` → **status=timeout @02:28:20** ★
    ⇒ 盘上**半成品**: `SW/tools/demo_e2e_budget.py` (33823 B, 02:22) · `SW/tools/demo_timing_check.py` (02:26 已改) ★
    ⇒ ★**交接单缺 + `state/fragments/sw.yaml` mtime 01:58 (没写) ⇒ 未交卷** ★
· ⇒ ★**本 job 的活 = ①main 独立复核 (自己跑门禁 + 自己 md5 + 自己查分片) ⇒ 落账 ②把 ISS-221 的半成品续上 ③开出下一批主线单** ★

★★**主线口径 (★老板 2026-11-11 10:07: 先解决原理图绘制的问题, PCB 布线/布局类一律不派★)** ★★
★★**本轮新开的 2 条 = 原理图/网表落表侧 + 结构门禁侧 ⇒ 没有一条是 PCB 布线/布局类** ★★
★★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 本脚本不碰 `state/outbox/` ★★
★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 (除 main 自己的 pm.yaml 走 frag_write.py) / 任何真源文件 / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0410_verify220_222_open223_224"

TODAY = "2026-11-16"
DUE = "2026-11-19"

# ==================================================================
# ① 落账: ISS-220 → fixed (★分片缺, 缺口转 ISS-223★) / ISS-222 → verified
# ==================================================================
VERIFY = {
    "ISS-220": (
        "★main 独立复核 (★2026-11-16 04:1x, 只看盘上实物 + 自己跑门禁 + 自己 md5 + 自己查分片★):\n"
        "  · HW/check_netlist_selfconsistency.py → rc=0 (★现状守卫 + 作业包完整性 28 条 + 三方对齐 全过★)\n"
        "  · HW/check_netlist_selfconsistency.py --selftest → rc=0 (★自检 19/19 通过 ⇒ 门禁不是假绿★)\n"
        "  · HW/check_netlist_selfconsistency.py --expect-resolved → rc=1 (★「未落表条数 50 → 29」= 落表实效, rc=1 是预期★)\n"
        "  · state/check_netlist.py → rc=0 · state/check_netlist_pins.py → rc=0 · state/check_sch_erc.py → rc=0\n"
        "  · 交付物在盘: HW/SCHEMATIC_LANDING_V1_LANDED.md (48572 B, 02:37) · HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md (24176 B, 02:39)\n"
        "  · ★**板 md5 `611b869e13518c3c023fb178f91a0075` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` 逐字节未变** (★板一个字节没碰★)\n"
        "  · 网表 md5 `c78f9912…` → `13f59a43…` / 脚表 `4814617e…` → `a600afae…` ⇒ ★**落表本职工作, 允许★**\n"
        "  · ★**EXPECT 锚点 154 → 160 (+6 条正向锚点, 一条未减) + R1~R11 判据代码一个字没改** ⇒ ★**「不许靠删条目/改判据凑绿」这条守住了** ★\n"
        "★**main 已复核的关键结论**: ① 6 组真源改动真落进盘 (d1 / d6 / d10 方向修正 / d11+#5 / #1 字段基建 / #7+#8) ② 其余 22 条全部 BLOCKED 并写明卡在 V-1~V-6 或「板只改一次」那一趟 ③ 6 条 V-x 一条没代拍 ★\n"
        "★★★**但本单只落 `fixed` 不落 `verified` —— 理由 = 交付物 ④ (分片) 实测【没落盘】**: ★**`state/fragments/hw.yaml` mtime = 2026-11-16 01:59:34 (早于 02:1x 派活) ⇒ 一次都没被写过** ★\n"
        "  · ★**交卷单 A4 行自称「通过 · 分片用 `state/frag_write.py` 的 `update_fragment()` 写的」与盘上不符** ★\n"
        "  · ★**hw.yaml 里 `iss220` 命中 0 条** (★交卷单自报的 3 个 key: `iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value` 一个都不在盘上★) ⇒ ★**3 条跨模块口径声明没进台账 ⇒ merge/gate 看不到它们** ★\n"
        "  · ★**`state/.lastgood/hw.yaml` 同样 0 条 ⇒ 不是被 merge 覆盖, 是从来没写过** ★\n"
        "⇒ ★**记账缺口转 ISS-223 交付物 ① (补落这 3 条) ⇒ 本单落表工作本身 main 复核通过, 分片补齐后由 main 再落 `verified`** ★",
        "2026-11-16 04:1x",
    ),
    "ISS-222": (
        "★main 独立复核通过 (★2026-11-16 04:1x, 只看盘上实物 + 自己跑门禁 + 自己 md5 + 自己查分片★):\n"
        "  · MECH/cavity_recalc_check.py → rc=0 (★20/20★ · 含 C18/C19/C20 三条新增断言全绿)\n"
        "  · MECH/cavity_recalc_check.py --selftest → rc=0 (★18/18 反向用例全抓到 ⇒ 门禁不是假绿★)\n"
        "  · MECH/verify_budget.py → rc=0 (★53/53 项与文档一致 + 口径自检 12/12★ · 充电耗散仍 = buck 口径, 阈值一个没松)\n"
        "  · MECH/verify_budget.py --selftest → rc=0 (11/11 反向用例全抓到)\n"
        "  · MECH/print/verify_pack.py → rc=0 (46/46) · MECH/print/verify_pack_revb.py → rc=0\n"
        "  · 交付物在盘: MECH/CENTER_CAVITY_REBALANCE_V3.md (29614 B, 02:34) · HANDOFF/2026-11-16_mech-lead_ISS222_C6C7C8落地.md (22247 B, 02:37) · ★**`state/fragments/mech.yaml` mtime 02:37:38 且含 `iss222*` key ⇒ 分片真落盘了** ★\n"
        "  · md5 逐字节未变: 4 个受保护 check 脚本全部一致 (hw_cross_review `e521387b…` / service_port `9b24bf98…` / hinge_usb `3425bc14…` / display_biosafety `29c77fc3…`)\n"
        "★**main 已复核的关键结论**: ① C-8 自己实算出 t_s = 8.8388 mm (45° 平板轴向投影) ⇒ 串联器件区 14.6388 ⇒ 三档余量 -2.64/0.36/2.36 ⇒ ★**并排化后三档全活** ② C-7 净可外露集热面 = **3432 mm²** (名义 3600 的 95.3%) ⇒ 铝背板路径 47.77 °C ✅ / 打印件 53.6 °C ❌ ⇒ W_rim ≥ 23.3 mm ③ C-6 分光件 M6 = 平板 11×11×1.5 + 棱镜 2×9×9×5 / 0.9697 cc / W4 3.68-7.36 g ⇒ DOC_WEIGHT (50.78, 75.36) ★\n"
        "★**但 `MECH/check_demo_struct_truth.py` 现在是 rc=2 (FAIL 3 组: G1 / G1b / G5b) —— 这 3 组不是本单造成的**: ★**根因 = ISS-220 的落表 (网表 02:32 改) 让 `PIN-MISMATCH` 由 FAIL 变 PASS (FAIL 17 → 16) ⇒ 门禁的「红灯保护锚点」对不上旧值** ⇒ ★**本单的交卷单自己也写明了这一点 (自述「这 3 组 FAIL 不是本单造成的」)⇒ main 实测复核确认** ★\n"
        "⇒ ★**这 3 组是【锚点过期】不是【红灯被调没】: `hw_cross_review_check.py` md5 `e521387b…` 逐字节未变 (门禁本身没被碰) · PIN-MISMATCH 由 P9 页与网表 pin 数【真不一致】变【真一致】(ISS-220 落了 d6: P9 页 CONN_LIGHT 21p→22p / CONN_CAM 18p→31p / 跨铰链 4 组→1 组) ⇒ 是修复, 不是调没** ★\n"
        "⇒ ★**锚点重基线化已开 ISS-224 (结构侧) 承接: 重锚 G1/G1b/G5b + 在定性表里把 PIN-MISMATCH 标成「已修复」留痕 + 加一条「网表/脚表 md5 变了必须在落表台账里查到来源, 否则红」的新断言** ★",
        "2026-11-16 04:1x",
    ),
}

FIX_REF = {
    "ISS-220": "HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md",
    "ISS-222": "HANDOFF/2026-11-16_mech-lead_ISS222_C6C7C8落地.md",
}

NOTE_TAIL_220 = (
    "\n★**2026-11-16 04:1x 落 `fixed` (不是 verified)**: 子会话 status=done @02:42:17 ⇒ ★**main 不采信状态位, 只看盘上实物 + 自己跑门禁 + 自己 md5 + 自己查分片** ⇒ "
    "★**落表工作本身 (交付物 ①②③⑤ + 交接单) main 复核通过** ⇒ ★**唯交付物 ④ (分片) 实测没落盘** (★hw.yaml mtime 01:59:34 · `iss220` 命中 0 条 · .lastgood 同样 0 条★) ⇒ "
    "★**缺口转 ISS-223 交付物 ① (补落 3 条分片声明) ⇒ 补齐后由 main 再落 `verified`** ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 (★补分片由 hw-lead 自己做★) · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★"
)

NOTE_TAIL_222 = (
    "\n★**2026-11-16 04:1x 落 `verified`**: 子会话 status=timeout @02:39:53 (★超时是在交卷之后★) ⇒ ★**main 不采信状态位, 只看盘上实物 + 自己跑门禁 + 自己 md5 + 自己查分片** ⇒ "
    "★**4 件交付物全在盘 (含分片 `iss222*` key 已落) + 门禁全绿 ⇒ 落 `verified`** ★\n"
    "★**`MECH/check_demo_struct_truth.py` 现为 rc=2 (G1/G1b/G5b 三组) ⇒ 根因 = ISS-220 落表让 `PIN-MISMATCH` 真修复 (FAIL 17→16) ⇒ 【锚点过期】不是【红灯被调没】 ⇒ 锚点重基线化由 ISS-224 承接** ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★"
)

# ==================================================================
# ② ISS-221: 记「会话已死·半成品在盘·待续」 (status 仍 fixing)
# ==================================================================
NOTE_221 = (
    "\n★**2026-11-16 04:1x 本 job 实查**: 子会话 `agent:sw-lead:subagent:6da17eee` → **status=timeout @02:28:20** (★死了★) ⇒ 盘上**半成品**: "
    "`SW/tools/demo_e2e_budget.py` (33823 B, 02:22) + `SW/tools/demo_timing_check.py` (02:26 已改) ⇒ ★**交接单缺 + `state/fragments/sw.yaml` mtime 01:58 (没写) ⇒ 未交卷** ⇒ "
    "★**本 job 已把同一单重新派给 sw-lead (续做, taskName=advance_iss221_resume), status 仍 `fixing` ⇒ 不是新单, 是续做** ★"
)

# ==================================================================
# ③ 新开 ISS-223 → hw-lead (原理图落表第 2 批 + 分片补落 + V-3 可判化)
# ==================================================================
TITLE_223 = (
    "★★[主线内·原理图/网表侧·内部活] ISS-220 收尾 (补落 3 条分片声明) + 落表第 2 批 "
    "(★V-1 已由项目总工裁: USB 串阻 = 22Ω±1% ⇒ d5 + 补差A 值迁移 20 条★) + 修 ISS-217 作业包 F-1~F-5 五处 "
    "+ V-3 的 RK3572 SARADC_VIN5 官方参数自查 (★把 BAT_DET 分压比从「拍不了」变成「可拍」★)"
)

DESC_223 = (
    "★**ISS-220 (11-16 02:37 交卷, 本 job 04:1x 落 `fixed`) 把作业包 28 条里 6 组真落进了盘 (未落表条数 50 → 29)**, "
    "★**但交付物 ④ (分片) 实测没落盘** ⇒ 3 条跨模块口径声明 (`iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value`) 至今不在台账里 ⇒ "
    "★**本单第一件事就是把它补上** ★\n"
    "★**本单第二件事 = 落表第 2 批**: ★**V-1 已由项目总工 (main) 裁 = 【USB 串阻 = 22Ω ±1% 外部串阻】** ⇒ "
    "★**依据 (全部 [实测], 不是拍脑袋★)**: ① 板 `HW/PCB/demo_mainboard.kicad_pcb` 里 `R_SER_USB_D_P = 22Ω ±1%` / `R_SER_USB_D_N = 22Ω ±1%` (★板上就是 22Ω★) "
    "② 网表器件行 L431/L432 = `22Ω ±1%` (Type-C 侧) 而 NET 行 L291/L292 = `90Ω ±10%` (★那是差分阻抗, 被塞进了串阻字段★) "
    "③ 门禁 `HW/check_netlist_selfconsistency.py` 的 EXPECT = 「NET 行 value 含 22Ω」⇒ ★**取 0Ω 就得改门禁 EXPECT ⇒ 那叫放松判据, 不许★** "
    "⇒ ★**V-1 落 = 22Ω (零 BOM 变化 · 零板费 · 零拓扑变化) + 差分阻抗 90Ω 留在 ISS-220 已拆好的 `z_diff` 字段** ⇒ ★**d5 (R5 那 8 条红) + 补差A 的值迁移 (A 组 20 条) 一起落** ★\n"
    "★**本单第三件事 = 修 ISS-217 作业包自身的 F-1~F-5 五处** (★ISS-220 实测查出: 作业包有 5 处与真源对不上 ⇒ 不修就没法落第 3 批★) ★\n"
    "★**本单第四件事 = 把 V-3 (BAT_DET 分压比) 从「拍不了」变成「可拍」**: ★**ISS-211 已查出 SoM ADC 参数缺失 (P1_38 = SARADC_VIN5, 1.8V 域) ⇒ 分压比不能只凭直觉选** ⇒ "
    "★**本单要自己查 RK3572 官方 datasheet 的 SARADC_VIN5 输入漏电流 / 满量程 / 输入电容, 出可拍依据 + 推荐值 (★不许代拍★)** ★\n"
    "★**本单不许碰板 / PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★) ⇒ ★**B-1~B-6 板侧同步项只更新状态, 不许动板** ★ "
    "★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★"
)

BRIEF_223 = (
    "★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: ★**(A)** 把 ISS-220 漏掉的 3 条分片声明补落盘; ★**(B)** 落表第 2 批 = V-1 已裁的那批 (d5 + 补差A 值迁移); "
    "★**(C)** 修作业包 F-1~F-5; ★**(D)** 把 V-3 变可拍 (官方参数自查) ★ ⇒ 出 ★**(1) 落表记录 · (2) 真源改动 + 重生成网表/脚表 · (3) 门禁未落表条数前后对比 · (4) 交接单 + 分片** ★ ⇒ ★**零外发** ★\n\n"
    "★★**为什么是现在 (★main 2026-11-16 04:1x 实测, 不是推测★)** ★★\n"
    "· ★**ISS-220 已把 6 组落进盘 (未落表条数 50 → 29)**, 但 ★**交付物 ④ 分片实测 0 条** (`hw.yaml` mtime 01:59:34 早于派活 · `iss220` 命中 0) ⇒ 3 条口径声明下游看不见 ★\n"
    "· ★**V-1 已裁 = 22Ω** (依据全 [实测]: 板 `R_SER_USB_D_P/N = 22Ω±1%` + 网表器件行 L431/L432 `22Ω±1%` + 门禁 EXPECT「NET 行 value 含 22Ω」) ⇒ ★**d5 那 8 条红现在能落** ★\n"
    "· ★**ISS-220 查出的 F-1~F-5 是作业包自身的病** ⇒ 不修, 第 3 批还会撞同样的坑 ★\n"
    "· ★**V-3 卡在 SoM ADC 参数缺失** ⇒ 现在不是「不值得拍」, 是「拍不了」⇒ 本单去把它变成可拍 ★\n\n"
    "★★**交付物 (6 件, 少一件即无效) ★★\n"
    "① ★**补落 ISS-220 的 3 条分片声明** ★ ⇒ keys `iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value` ⇒ "
    "★**必须走 `python3 state/frag_write.py --agent hw-lead` (原子写)★** ⇒ 交卷贴 `state/fragments/hw.yaml` 的 mtime 前/后 + 3 个 key 的命中行 (★不许手改 YAML★) ★\n"
    "② ★**落表第 2 批 (V-1 = 22Ω)** ★ ⇒ 只许改: `HW/SCHEMATIC_V1_SPEC.json` (B-21/B-22 的 `imp` ⇒ `22Ω ±1%`) + `state/gen_netlist.py` (若取值优先级还要微调) + "
    "★**补差A 的值迁移: A 组 20 条 `imp` 清空 · 差分阻抗搬进 `z_diff` (100Ω±10%) · B-21/B-22 的 `z_diff` = 90Ω±15%**★ ⇒ 改完 `python3 state/gen_netlist.py` 重生成网表/脚表 ⇒ ★**不许手工编辑生成产物 (CSV)★** ★\n"
    "③ ★**门禁前后对比** ★ ⇒ `python3 HW/check_netlist_selfconsistency.py --expect-resolved` 的「未落表条数」★**落表前 = 29 ⇒ 落表后 = N (贴两次输出)★** ⇒ "
    "★**不许靠删条目 / 改判据 / 改 EXPECT 锚点达成 ⇒ EXPECT 锚点组 d1..d11 一个不许减, R1~R11 判据代码一个字不许改** ★\n"
    "④ ★**修作业包 F-1~F-5 五处** ★ ⇒ 逐条给出改法并改 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (★作业包是 hw-lead 自己的产物, 本单可改★): "
    "F-1 d2 的真源是 `DEMO_DNP` 白名单 (不是 `add()` 的 dnp 参数) · F-2 d10 的 J_CHG 行真源是 `state/p10_rows.json` (作业包把文件归属写错了) · "
    "F-3 补差A 清空 A 组 `imp` 须与 `state/check_netlist.py` 判据 5 同趟改 (否则判据覆盖 20 行 → 0 行) · F-4 d10 的方向修正连带作废「皮肤侧 42.14°C / 不能再抬电流」这条结论 (它是按 0.822 算的) · "
    "F-5 #5 的白名单↔§7 双向对账在现状下不可能过 (§7 与网表是两个版本: 16 个位号网表里没有, 15 个 CHG_BOARD 位号不在 §7 里) ⇒ ★**每条都要写明「改了什么 + 为什么现在能改 / 还差什么」** ★\n"
    "⑤ ★**V-3 可判化** ★ ⇒ 自己查 ★**RK3572 官方 datasheet**★ 里 SARADC_VIN5 (1.8V 域) 的 **输入漏电流 / 满量程 / 输入电容** ⇒ 出 V-3 (2.0M+1.2M vs 2.0M+1.0M) 的 "
    "★**误差算式 + 可拍依据 + 推荐值 + 降级方案**★ ⇒ ★**不许代拍 (拍板权在 main/老板)★** ⇒ 查不到就写 [0数据] + 降级 ★\n"
    "⑥ ★**板侧同步清单更新** (★只更新状态, 不许动板★) ⇒ B-1~B-6 六项逐条标: 因本批落表而变化的 / 仍等 V-2 与「板只改一次」那一趟的 ⇒ "
    "★**交接单 `HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/hw.yaml` (★走 `state/frag_write.py` 原子写★)** ★\n\n"
    "★★**边界 (★违反一条即本单无效★) ★★\n"
    "· ★**不许改** `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` / ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★) ★\n"
    "· ★**不许代拍** V-2 (ESD 方案与型号 = 老板级选型) / V-3 (本单只出依据) / V-4 (R_ILIM 档位 = 老板待拍, 已在 `DECISION_PENDING_2026-11-16.md` §3) / V-5 (结构侧堆叠口径) ⇒ ★**V-1 已由 main 裁 = 22Ω, 可直接落** ★\n"
    "· ★**不许改判据阈值 / EXPECT 锚点** (★不许为了让门禁变绿而放松★) ★\n"
    "· ★**不许改** `MECH/` 下任何文件 / `SW/` 下任何文件 / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 ★\n"
    "· ★**开工前先给每个要改的真源文件留 `.bak_iss223` 副本** ⇒ 交卷贴每个真源文件的 md5 前/后对照 ★\n"
    "· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★\n"
    "· ★**本单实物 [实测] = 0 条** (板不在本机) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★\n"
    "· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★\n\n"
    "★★**交卷前必须实跑并把输出原样贴进回复 ★★\n"
    "```\n"
    "python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫 + 作业包完整性 + 三方对齐)\n"
    "python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例全抓到, 19/19 或更多)\n"
    "python3 HW/check_netlist_selfconsistency.py --expect-resolved   # ★rc=1 是预期 (还有 BLOCKED 条目) ⇒ 必须贴 29 → N 的前后对比\n"
    "python3 state/check_netlist.py                                  # rc=0 (全过)\n"
    "python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)\n"
    "python3 state/check_sch_erc.py                                  # rc=0 (ERC 违规数 = 0)\n"
    "python3 state/check_sch_pinfull.py                              # rc=0 (图上脚数 = 表里脚数)\n"
    "python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18\n"
    "```\n"
    "★**落表若导致上面某条门禁变红 ⇒ 不许放松门禁, 也不许回退已落表的条目来凑绿 ⇒ 交卷报红并说明原因 (★main 复核)**★"
)

# ==================================================================
# ④ 新开 ISS-224 → mech-lead (门禁锚点再基线化)
# ==================================================================
TITLE_224 = (
    "★★[主线内·结构侧·内部活] `MECH/check_demo_struct_truth.py` 三组失配的再基线化: ISS-220 落表让 `PIN-MISMATCH` 由 FAIL 变 PASS (= 真修复, FAIL 17→16) "
    "+ 网表/脚表 md5 随落表变 ⇒ G1/G1b/G5b 旧锚点失效 ⇒ 重锚 + 留痕 + 保住「不许把红灯调没」不变量 + 把「受保护 md5」升级成「真源 md5 + 落表台账核对」"
)

DESC_224 = (
    "★**main 2026-11-16 04:1x 实测**: `python3 MECH/check_demo_struct_truth.py` → **rc=2, 17/20 组通过, FAIL 3 组 (G1 / G1b / G5b)** ★\n"
    "· ★**根因 = ISS-220 (hw-lead) 的落表**, 不是结构侧缺陷: 落表把 `state/gen_schematic_pages.py` 的 P9 页正文改了 (★d6: CONN_LIGHT 21p→22p / CONN_CAM 18p@0.5→31p@0.3 / 跨铰链 4 组→1 组★) ⇒ "
    "★**P9 正文声明与网表实际 pin 数从此一致 ⇒ `PIN-MISMATCH` 由 FAIL 变 PASS ⇒ FAIL 名单 17 → 16 ⇒ 门禁的「不许把红灯调没」锚点 (G1/G1b) 对不上旧值** ★\n"
    "· ★**G5b 同因**: 受保护 md5 锚点钉的是旧网表/脚表 (`c78f9912…` / `4814617e…`), 而 ISS-220 落表后是 `13f59a43…` / `a600afae…` ⇒ 门禁读着旧数 ★\n"
    "· ★**关键鉴别 (★main 实测, 不是推测★)**: `MECH/hw_cross_review_check.py` md5 `e521387b87b0fcdf9f22d56f14199967` ★**逐字节未变** ⇒ ★**门禁本身没被碰过 ⇒ 是【锚点过期】不是【红灯被调没】** ★\n"
    "★**本单要做的 = 重锚 + 留痕 + 把机制升级 (不许只是改个数让它变绿)**: ★**「不许把红灯调没」这条不变量必须活下来** ★\n"
    "★**本单不许改 `HW/` 下任何文件 / 不许碰 PCB 布线布局 / 不许改判据阈值 / 不许把那 16 条 FAIL 修绿** ⇒ ★**零外发** ★"
)

BRIEF_224 = (
    "★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**`MECH/check_demo_struct_truth.py` 的 3 组失配 (G1/G1b/G5b) 重新基线化, 并把「红灯保护」机制从「钉死一组旧数」升级成「钉死真源 + 与落表台账对账」**★ ⇒ "
    "出 ★**(1) 重锚后的门禁 · (2) 定性表里的修复留痕 · (3) 新增的「不许悄悄换真源」断言 + 反向用例 · (4) 交接单 + 分片** ★ ⇒ ★**零外发** ★\n\n"
    "★★**为什么是现在 (★main 2026-11-16 04:1x 实测, 不是推测★)** ★★\n"
    "· ★**main 实跑 `MECH/check_demo_struct_truth.py` → rc=2 · 17/20 组通过 · FAIL 3 组 (G1 / G1b / G5b)** ★\n"
    "· ★**main 实查 FAIL 名单变化**: 定性表 54 行里 17 条 ❌FAIL, 现在脚本实跑只出 **16 条 FAIL** ⇒ ★**少的那一条 = `PIN-MISMATCH` (定性表第 05 行)** ★\n"
    "· ★**main 实查根因**: `MECH/hw_cross_review_check.py` md5 `e521387b…` 逐字节未变 ⇒ 门禁没被碰 ⇒ ★**是 ISS-220 落表把 P9 页与网表的 pin 数【真不一致】修成了【真一致】(d6) ⇒ 修复, 不是调没** ★\n"
    "· ★**G5b 同因**: 网表 md5 `c78f9912…`→`13f59a43…` / 脚表 `4814617e…`→`a600afae…` ⇒ 锚点过期 ★\n"
    "· ⇒ ★**当前状态是「门禁读着旧数」⇒ 项目铁律: 门禁读旧数 = 假红/假绿 ⇒ 必须重锚, 但重锚必须留痕, 不许静默改数** ★\n\n"
    "★★**交付物 (5 件, 少一件即无效) ★★\n"
    "① ★**G1 / G1b 重锚 + 留痕** ★ ⇒ 把 FAIL 名单锚点从 17 改成 16, 并且 ★**在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 的定性表里把第 05 行 `PIN-MISMATCH` 从 ❌FAIL 改成 ✅PASS, "
    "同时写明「★已由 ISS-220 落表修复 (2026-11-16 02:32)★ · 依据 d6: P9 页正文 CONN_LIGHT 21p→22p / CONN_CAM 18p@0.5→31p@0.3 / 跨铰链 4 组→1 组」** ⇒ "
    "★**这一行不许从表里删掉 (删掉 = 把一次真修复抹了)★** ★\n"
    "② ★**G6 去处表同步** ★ ⇒ 「17 条 FAIL 的逐条去处」表 ⇒ 16 条 + **新增一节「已修复 (留痕)」**, 把 `PIN-MISMATCH` 记进去 ⇒ ★**不许只把 17 改成 16 而没人知道少的那条是谁** ★\n"
    "③ ★**G5b 重锚 + 升级 (★本单的核心★)** ★ ⇒ 把网表/脚表 md5 锚点更新为落表后的 `13f59a43dbd35dc6cb16e897c8c891ab` / `a600afae493f5a7a6c55f46ad35ac89c` ⇒ "
    "★**并新增一条断言 (C21 或同号)**: 「网表/脚表 md5 与锚点不一致时, 必须能在 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (ISS-220 落表记录) 或 `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` 里查到该次变更的来源与落表单号, 否则红」** ⇒ "
    "★**这条新断言才是「不许悄悄换真源」的真机制 ⇒ 只改 md5 锚点等于把门禁再废一次** ★ ⇒ 配套加反向用例 (改坏 md5 锚点 / 改坏落表单号 ⇒ 必须变红) ★\n"
    "④ ★**反向用例扩项** ★ ⇒ ① 把 `PIN-MISMATCH` 改回 FAIL (改 P9 页或改网表) ⇒ 必须变红 ② 把网表 md5 改回旧值 ⇒ 必须变红 ③ 删掉「已修复」留痕 ⇒ 必须变红 ⇒ ★**`--selftest` 必须全抓到** ★\n"
    "⑤ ★**交接单 `HANDOFF/2026-11-16_mech-lead_ISS224_门禁锚点再基线.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/mech.yaml` (★走 `state/frag_write.py` 原子写★)** ★\n\n"
    "★★**边界 (★违反一条即本单无效★) ★★\n"
    "· ★**不许改判据阈值** (★皮肤 43 °C / 端件 60 °C / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00 / 板框四数 一个不许动★) ★\n"
    "· ★**不许把那 16 条 FAIL 修绿** (★本单只重锚 + 留痕 + 升级机制, 一条红灯都不许消★) ⇒ ★**6 个 PCB 类 id 仍按老板 2026-11-11 10:07 口径排队等原理图定稿** ★\n"
    "· ★**不许改** `HW/` 下任何文件 (★网表/脚表/板/原理图/BOM 一个字节不许动★) / ★**不许碰 PCB 布线 / 布局 / 板框** ★\n"
    "· ★**不许改** `MECH/hinge_usb_check.py` / `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` / `MECH/display_biosafety_v2_check.py` (★4 个受保护脚本 md5 必须逐字节不变★) ★\n"
    "· ★**不许改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` (★那是老板的页面★) / `state/outbox/` / 别人的分片 ★\n"
    "· ★**实物 [实测] = 0 条** (本机跨网段不可达 / 无切片器 / 无量具) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★\n"
    "· ★**零外发** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★\n"
    "· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★\n\n"
    "★★**交卷前必须实跑并把输出原样贴进回复 ★★\n"
    "```\n"
    "python3 MECH/check_demo_struct_truth.py          # rc=0 (★20/20 或更多组全过·FAIL 0 组★)\n"
    "python3 MECH/check_demo_struct_truth.py --selftest # rc=0 (★反向用例全抓到★)\n"
    "python3 MECH/cavity_recalc_check.py               # rc=0 (★ISS-222 的 20/20 不许被改红★)\n"
    "python3 MECH/cavity_recalc_check.py --selftest    # rc=0\n"
    "python3 MECH/verify_budget.py                      # rc=0 (★阈值一个没松★)\n"
    "python3 MECH/hw_cross_review_check.py              # rc=0 (★54 项分布不许被本单改动★)\n"
    "python3 MECH/print/verify_pack.py                  # rc=0\n"
    "python3 MECH/print/verify_pack_revb.py             # rc=0\n"
    "python3 state/merge.py && python3 state/gate_check.py # rc=0 且 【Q1 交付齐备率】 18/18\n"
    "```"
)

NEW_ISSUES = [
    {
        "id": "ISS-223",
        "title": TITLE_223,
        "severity": "high",
        "source_blocker": "ISS-220",
        "desc": DESC_223,
        "owner": "hw-lead",
        "task_brief": BRIEF_223,
        "note": (
            "2026-11-16 04:1x 本 job (775d9893) 新开 ★**依据 1 = ISS-220 交卷的 ④ 分片实测 0 条** (★hw.yaml mtime 01:59:34 早于派活 · `iss220` 命中 0 · .lastgood 同样 0★) ⇒ "
            "★**3 条跨模块口径声明至今不在台账里** ⇒ 落 ISS-220 `fixed` 而非 `verified`, 缺口转本单交付物 ①** ★\n"
            "★**依据 2 = V-1 (USB 串阻) 已由项目总工裁 = 22Ω ±1%** (★依据全 [实测]: 板 `R_SER_USB_D_P/N = 22Ω±1%` + 网表器件行 L431/L432 `22Ω±1%` + 门禁 EXPECT「NET 行 value 含 22Ω」★) ⇒ "
            "★**d5 (R5 那 8 条红) + 补差A 值迁移 (A 组 20 条) 现在可落 ⇒ 落表第 2 批** ★\n"
            "★**依据 3 = ISS-220 交卷查出的 F-1~F-5 (作业包自身与真源对不上)** ⇒ 不修则第 3 批还会撞同样的坑 ★\n"
            "★**依据 4 = V-3 卡在 SoM ADC 参数缺失 (ISS-211 查出 P1_38 = SARADC_VIN5 / 1.8V 域)** ⇒ 本单去查 RK3572 官方 datasheet 把它变可拍 ★\n"
            "★**本单属原理图主线内部活, 不碰 PCB 布线/布局/板框 (老板 10:07 口径) ⇒ 可派** ★\n"
            "★**hw-lead 名额的上一条 ISS-220 已于本轮 04:1x 落 `fixed` ⇒ 名额空出来 ⇒ 本单是第 6 轮** ★"
        ),
    },
    {
        "id": "ISS-224",
        "title": TITLE_224,
        "severity": "high",
        "source_blocker": "ISS-222",
        "desc": DESC_224,
        "owner": "mech-lead",
        "task_brief": BRIEF_224,
        "note": (
            "2026-11-16 04:1x 本 job (775d9893) 新开 ★**依据 = main 本轮实跑 `MECH/check_demo_struct_truth.py` → rc=2 · FAIL 3 组 (G1/G1b/G5b)** ★\n"
            "★**根因 = ISS-220 (hw-lead) 的落表**, 不是结构侧缺陷 (★main 实查 `hw_cross_review_check.py` md5 `e521387b…` 逐字节未变 ⇒ 门禁没被碰 ⇒ 【锚点过期】不是【红灯被调没】★) ★\n"
            "★**且这是【真修复】**: ISS-220 落的 d6 把 P9 页与网表的 pin 数改一致了 ⇒ `PIN-MISMATCH` 由 FAIL 变 PASS ⇒ FAIL 17 → 16 ★\n"
            "★**本单不是「把数改绿」, 是「重锚 + 留痕 + 把『受保护 md5』升级成『真源 md5 + 落表台账核对』」** ⇒ ★**项目铁律: 门禁读旧数 = 假红/假绿** ★\n"
            "★**本单属结构侧内部活, 不碰 PCB 布线/布局/板框 (老板 10:07 口径) ⇒ 可派** ★\n"
            "★**mech-lead 名额的上一条 ISS-222 已于本轮 04:1x 落 `verified` ⇒ 名额空出来 ⇒ 本单是第 8 轮** ★\n"
            "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★"
        ),
    },
]


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ① 落账
        for iid, (vres, vdate) in VERIFY.items():
            hit = by_id.get(iid)
            if hit is None:
                print("⚠ %s 不存在 ⇒ 跳过" % iid)
                continue
            if hit.get("status") not in ("fixing", "fixed"):
                print("⚠ %s status=%s (不是 fixing/fixed) ⇒ 不动" % (iid, hit.get("status")))
                continue
            hit["status"] = "fixed" if iid == "ISS-220" else "verified"
            hit["fixed_at"] = TODAY
            hit["verify_date"] = vdate
            hit["verify_result"] = vres
            hit["fix_ref"] = FIX_REF.get(iid) or hit.get("fix_ref")
            hit["note"] = (hit.get("note") or "") + (NOTE_TAIL_220 if iid == "ISS-220" else NOTE_TAIL_222)
            print(" - %s fixing → %s (main 独立复核)" % (iid, hit["status"]))

        # ② ISS-221 记续做
        hit = by_id.get("ISS-221")
        if hit is not None and "2026-11-16 04:1x 本 job 实查" not in (hit.get("note") or ""):
            hit["note"] = (hit.get("note") or "") + NOTE_221
            print(" - ISS-221 记「会话已死·半成品·已重新派活续做」(status 仍 fixing)")

        # ③ 新开
        for spec in NEW_ISSUES:
            iid = spec["id"]
            if iid in by_id:
                print("⚠ %s 已存在 ⇒ 幂等跳过" % iid)
                continue
            issues.append({
                "id": iid,
                "title": spec["title"],
                "severity": spec["severity"],
                "source_blocker": spec["source_blocker"],
                "desc": spec["desc"],
                "owner": spec["owner"],
                "reporter": "main",
                "raised": TODAY,
                "due": DUE,
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "note": spec["note"],
                "task_brief": spec["task_brief"],
                "dispatched_at": None,
            })
            print(" + 新开 %s → %s (status=open, 等 advance.py --apply 落 fixing 再 spawn)" % (iid, spec["owner"]))

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
