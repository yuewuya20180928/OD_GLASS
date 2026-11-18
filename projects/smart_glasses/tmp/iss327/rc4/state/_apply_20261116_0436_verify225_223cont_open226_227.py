#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 落账 ISS-225 (→verified) + ISS-223 (续做登记) + 新开 2 单
     (ISS-226 → sw-lead · ISS-227 → mech-lead)
================================================================================
★**为什么这一轮是「清僵尸 + 续做 + 开新单」 (★2026-11-16 04:36 实测★)** ★
· ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是两个总工名额被 `fixing` 占住 ★
· ★**逐会话实查 (`sessions_list` + 盘上实物 mtime/md5 实查)**:
  - ISS-225 (sw-lead) · `agent:sw-lead:subagent:b2423369` → **status=done @04:28:37** ★
    ⇒ 盘上 4 件交付物齐全 (SW/SW_MD5_BASELINE_LEDGER.md 04:28 · check_demo_panel_spec.py 04:21
      · HANDOFF/2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md 04:28 · fragments/sw.yaml 04:28) ★
    ⇒ main 04:36 实跑: `check_demo_panel_spec.py` rc=0 (R1~R7 全过, R6 已升级成三方对账)
      + `--selftest` rc=0 (**16/16**) ⇒ ★**可落 verified** ★
  - ISS-223 (hw-lead) · `agent:hw-lead:subagent:359d0e98` → **status=timeout @04:20:44** ★
    ⇒ ★**半成品, 树处于「源与产物脱节」状态** ★:
      · 已落: `HW/SCHEMATIC_V1_SPEC.json` (04:15:47, B-21/B-22 imp ⇒ 22Ω ±1%)
             · `state/gen_netlist.py` (04:21:43, conn_row() 已支持 imp/z_diff 优先级)
             · `state/check_netlist.py` (04:24:51, 比对源改成 `imp or z_diff`)
      · 未落: `HW/netlist_v1.csv` / `_pins.csv` mtime **仍 02:32** ⇒ **网表/脚表没重生成**
             · `state/fragments/hw.yaml` mtime **01:59:34** + `iss220` 命中 **0** ⇒ 3 条声明没补落
             · `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` mtime **02:35** ⇒ F-1~F-5 没修
             · `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` **不存在** ⇒ 交接单没写
             · V-3 SARADC 官方参数自查 **没做**
    ⇒ ★**所以 ISS-223 保持 `fixing`, 但要续做 (同一个 agent 续同一个单, 不占第二个名额)** ★
    ⇒ ★**本轮 main 实测的 2 条红 (交给续做的人收)**:
      `python3 HW/check_netlist_selfconsistency.py` → **rc=1**
      ★[d5_spec_b21_imp] 判据 'spec.connections[id=B-21].imp == 90Ω ±10%' 不成立 (实际 '22Ω ±1%')
      ★[d5_spec_b22_imp] 判据 'spec.connections[id=B-22].imp == 90Ω ±10%' 不成立 (实际 '22Ω ±1%')
      ⇒ ★**根因 = 规格页 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 d5 判据单元格还写着 V-1 裁前的旧值** ★
      ⇒ ★**★预警 (main 提前算出来的)**: 重生成网表后 `d5_a291_value` / `d5_a292_value`
        (网表 291/292 行 value == 90Ω ±10%) **也会变红** ⇒ ★**必须同趟改 4 个判据单元格**
        (90Ω ±10% ⇒ 22Ω ±1%) ⇒ 否则落表会把红从 2 条变 4 条 ★
★★**主线口径 (★老板 2026-11-11 10:07: 先解决原理图绘制的问题, PCB 布线/布局类一律不派★)** ★★
★★**本轮 3 条 = 原理图/网表落表续做 (hw) + 软件/光生物安全判据侧 (sw) + 结构热路口径侧 (mech)** ★★
★★**⇒ 没有一条是 PCB 布线 / 布局 / 板框类** ★★
★★**零外发** (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 本脚本不碰 `state/outbox/` ★★
★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0436_verify225_223cont_open226_227"

TODAY = "2026-11-16"
DUE = "2026-11-19"

# ==================================================================
# ① 落账: ISS-225 → verified (★main 独立复核, 非抄交卷报告★)
# ==================================================================
VERIFY = {
    "ISS-225": (
        "★main 2026-11-16 04:36 独立复核 (★只跑盘上门禁 + 自己查 mtime/md5 + 自己查分片, 不抄交卷报告★):\n"
        "  · `python3 SW/tools/check_demo_panel_spec.py` → **rc=0** ★(R1 demo 屏规格真源 / R2 整机口径只在占位区 /"
        " R3 pipeline spec 已重锚 / R4 整机路线占位带标 / R5 逐处定性表 22+16=38 处完整 /"
        " ★**R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致** / ★**R7 已修复 (留痕) 在场**★) ⇒ ★**R6 这次不是「md5 相等」, 是三方对账** ★\n"
        "  · `python3 SW/tools/check_demo_panel_spec.py --selftest` → **rc=0, ★16/16 通过** ★(REV-12 落表单号改坏 /"
        " REV-13 删台账两行 / REV-14 删锚点块 fail-closed / REV-15 删留痕节 ⇒ 4 条新反向用例全被抓到) ★\n"
        "  · 交付物 4/4 在盘: `SW/SW_MD5_BASELINE_LEDGER.md` (18984 B, 04:28) · `SW/tools/check_demo_panel_spec.py`"
        " (33571 B, 04:21) · `HANDOFF/2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md` (29029 B, 04:28) ·"
        " `state/fragments/sw.yaml` (204885 B, **04:28** ⇒ 真落盘) ★\n"
        "  · 分片命中: `iss225_sw_md5_baseline_ledger` / `iss225_reanchor_sw_md5_after_iss223` 两个 key **都在盘上** ★\n"
        "  · ★**板/网表/脚表/.kicad_pro 逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075` ·"
        " 网表 `13f59a43dbd35dc6cb16e897c8c891ab` · 脚表 `a600afae493f5a7a6c55f46ad35ac89c` ·"
        " `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★ ⇒ ★**本单零越界** ★\n"
        "★**main 的复核结论**: ★**本单不是「补锅」, 是「把这类恒红收口成机制」** ★\n"
        "  · 原红 (R6 = 盘上 md5 ≠ 锚点 md5) 是 **ISS-220 落表打破旧基线** 造成的 ⇒ ★**锚点过期, 不是红灯被调没** ★\n"
        "  · 现在 R6 = ★**三方对账**★ (锚点 ↔ 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` ↔ 盘上真源)"
        " ⇒ ★**「只改 md5 锚点 = 悄悄换真源」这条路被堵死了** ★\n"
        "  · R7 = 已修复留痕必须在场 ⇒ ★**「红灯被调没」这条路也被堵死了** ★\n"
        "  · ★**下一批落表会按设计让 R6 再红一次 (锚点过期) ⇒ 那是机制在工作, 不是故障** ⇒"
        " 重锚走台账 §4 的 H-1 流程 (改 §1 entries[].md5/prev_md5/by 三项 + 落表台账位置 + §3 留痕) ★\n"
        "★**遗留 (已登记 need `iss225_reanchor_sw_md5_after_iss223`, 不在本单范围)**: ISS-223 落表第 2 批改网表后"
        " ⇒ 需派 sw-lead 走 H-1 重锚 (★那是下一轮的单, 因为新 md5 现在还没定★)",
        "2026-11-16 04:36",
    ),
}

# ==================================================================
# ② ISS-223: 保持 fixing, 但追加「续做登记」(★会话 timeout, 半成品★)
# ==================================================================
CONT_223_NOTE = (
    "\n\n★★★ ★**2026-11-16 04:36 续做登记 (main 实测, 非推测) — 本单会话 `agent:hw-lead:subagent:359d0e98`"
    " status=timeout @04:20:44 ⇒ 半成品, 树处于「源与产物脱节」状态** ★★★\n"
    "★**已落 (main 04:36 查 mtime 实测)**: `HW/SCHEMATIC_V1_SPEC.json` (04:15:47 ⇒ B-21/B-22 `imp` 已改 `22Ω ±1%`)"
    " · `state/gen_netlist.py` (04:21:43 ⇒ `conn_row()` 已支持 `imp`/`z_diff` 取值优先级 + 同趟 note 栏输出)"
    " · `state/check_netlist.py` (04:24:51 ⇒ 比对源改成 `imp or z_diff`, 与生成器同源) ★\n"
    "★**未落 (main 04:36 查 mtime 实测)**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` mtime **仍 02:32:07** ⇒"
    " ★**网表/脚表根本没重生成** (⇒ 源已改、产物没重生成 ⇒ md5 仍是旧值 `13f59a43…`/`a600afae…`) ★"
    " · `state/fragments/hw.yaml` mtime **仍 01:59:34** + `iss220` 命中 **0** ⇒ ★**3 条声明没补落** ★"
    " · `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` mtime **仍 02:35** ⇒ ★**F-1~F-5 没修** ★"
    " · `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` **不存在** ⇒ 交接单没写"
    " · V-3 (RK3572 SARADC_VIN5 官方参数自查) **没做** ★\n"
    "★**main 04:36 实跑的门禁现状 (交给续做的人收)**: `HW/check_netlist_selfconsistency.py` → ★**rc=1, 2 条红**★\n"
    "  · ★[d5_spec_b21_imp] 判据 'spec.connections[id=B-21].imp == 90Ω ±10% (与 MIPI 不同模板!)' 不成立 (实际 '22Ω ±1%')\n"
    "  · ★[d5_spec_b22_imp] 判据 'spec.connections[id=B-22].imp == 90Ω ±10%' 不成立 (实际 '22Ω ±1%')\n"
    "  · ⇒ ★**根因 = 规格页 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L376/L378 那两个判据单元格还写着 V-1 裁前的旧值** ★\n"
    "  · ⇒ ★**★预警 (main 提前算出来的)**: ★**重生成网表后 `d5_a291_value` / `d5_a292_value` (L366/L368, 网表 291/292 行"
    " value == 90Ω ±10%) 也会变红** ⇒ ★**必须同趟把规格页这 4 个判据单元格 (90Ω ±10% ⇒ 22Ω ±1%) 一起改** ★"
    " ⇒ ★**否则落表会把红从 2 条变成 4 条** ★ ⇒ ★**这不是「改判据凑绿」, 是「d5 的判据本体要跟着落表走」** ★\n"
    "  · ★**其余门禁当前全绿 (main 04:36 实跑)**: `state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 ·"
    " `SW/tools/demo_timing_check.py` rc=0 · `MECH/check_demo_struct_truth.py` rc=0 (23/23) ·"
    " `SW/tools/check_demo_panel_spec.py` rc=0 (R1~R7, ISS-225 已把它升级成三方对账) ★\n"
    "★**落表后必须同趟做的三件事 (顺序不许搞反, 缺一件就出事)**: ① 重生成网表/脚表 ⇒ md5 变"
    " ② ★**落表记录 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` + 本单交接单) 里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项**"
    " (⇒ MECH 闸 C21 / SW 闸 R6 的三方对账靠这个, 缺一项 = 门禁假红)"
    " ③ ★**把「MECH 闸要改哪条锚点」在交接单里点名写出 (本单不许改 `MECH/`, 锚点由 mech-lead 下一轮重锚)** ★"
    " ⇒ ★**落表后 MECH 闸 G5b+C21 与 SW 闸 R6 会按设计变红 (锚点过期), 那不是故障, 是机制在工作** ★\n"
    "★**状态 = 保持 `fixing`, 续做 (同一个 agent 续同一个单, 不占第二个名额)** ★"
)

# ==================================================================
# ③ 新开 2 单
# ==================================================================
ISS226_BRIEF = """★★**目标 (★内部活·软件/光生物安全判据侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
把 ★**光生物安全的「出瞳白场辐亮度最大值」在 SW 侧亮度控制策略里变成一个可判的量** ★
⇒ 面板蓝光通道辐亮度占白场辐亮度 ★**上限 25% (保守)**★, 名义值 ★**8.26%**★
⇒ 交付: ★**(1) SW 侧亮度控制策略文档 · (2) 亮度 API 上可标定的蓝通道占比量 · (3) 机器门禁 + 反向用例 · (4) 交接单 + 分片** ★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 04:36 实查分片, 不是推测★)** ★★
· ★**这是 ISS-134 从结构侧跨域登记给 SW 侧的 need** (`state/fragments/mech.yaml` 的 `iss134_sw_blue_drive_ratio_cap`, to=sw-lead, ★**至今 open**★) ⇒ ★**它不是 main 编的活, 是项目里本来就挂着、没人接的单** ★
· ★**它不依赖任何在飞单** ⇒ 落在本轮 (sw-lead 名额刚被 ISS-225 验收放出来) ⇒ ★**不占主线的时间窗** ★

★★**依据 (★全部来自项目内已有材料, 不许编数★)** ★★
· ★**上限 25% (保守) / 名义 8.26%** ★ ⇒ 依据 = DCI-P3 蓝基色 x=0.150 y=0.060 的 Y_B=0.0798 / 红 0.3850 / 绿 0.5017, ★**等辐射功率下算**★ ⇒ ★**8.26% = 0.0798 / (0.0798+0.3850+0.5017)** ★
· ★**为什么与 SW 有关** ★ ⇒ ★**光生物安全的输入量 = 出瞳白场辐亮度的最大值**★, 而 ★**亮度控制策略 (蓝光主通道占空 / 码值上限) 直接决定这个最大值落在哪** ★
· ★**越限的后果链 (照抄, 不许改写语义)** ★ ⇒ L_eye > 1500 cd/m2 ⇒ ★**掉出 IEC 62471 Exempt (RG0) 进 RG1**★ (L_B 100..10000 W/(m2*sr)) ⇒ ★**需要用户信息 / 标签说明**★ (★**不是禁视警示, 那个要到 RG2 才有**★)
· ★**判定与测量的真源在结构侧** ★ ⇒ `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3.2 与 §3.6 ⇒ ★**SW 侧只需保证亮度控制策略里有这条上限, 并在亮度 API 上留一个可标定的蓝通道占比量** ★

★★**交付物 (4 件, 少一件即无效) ★★
① ★**SW 侧亮度控制策略文档 (新建)** ★ ⇒ 写清: ① 上限 25% (保守) 的来源与 ★**名义 8.26% 的算式**★ ② ★**越限后果链 (1500 cd/m2 ⇒ RG0→RG1 ⇒ 用户信息/标签)**★ ③ ★**SW 侧要保证的东西 = 「亮度控制策略里有这条上限」**★ ④ ★**降级方案**★ (板端不可达 ⇒ 全部标 [推算]/[0数据]; ★**不许拿任何未实测的辐亮度数当实测**★)
② ★**亮度 API 上的可标定蓝通道占比量** ★ ⇒ ★**只定义接口/字段与标定方法, 不许填任何编出来的实测值** ★ ⇒ ★**板端数据 = [0数据]** ★
③ ★**机器门禁 (新建脚本 + `--selftest` 反向用例)** ★ ⇒ 断言: ★**(a) 上限 25% / 名义 8.26% 这两个数不许被改小**★ ★**(b) 越限后果链那三段不许被删**★ ★**(c) 亮度 API 的蓝通道占比量不许被摘掉**★ ⇒ ★**反向用例至少 4 条 (改小上限 / 删后果链 / 删 API 量 / 改名义值) 必须全红** ★ ⇒ ★**门禁不许靠「把判据删掉」变绿** ★
④ ★**交接单 (新建) `HANDOFF/2026-11-16_sw-lead_ISS226_蓝光通道占比上限与亮度API.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写★)** ★ ⇒ ★**交卷贴分片 mtime 前/后** ★

★★**边界 (★违反一条即本单无效★)** ★★
· ★**不许改** `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (★结构侧地界, 只读引用★) · 不许改 `HW/` · 不许改 `state/issue_log.yaml` · 不许改 `PROJECT_TRACKER.md` §0 · 不许碰 `state/outbox/` · 不许碰别人的分片
· ★**不许改判据数值** (25% / 8.26% / 1500 cd/m2 / Y_B=0.0798 / 红 0.3850 / 绿 0.5017 ★**一个不许动**★)
· ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★)
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★
· ★**本单实物 [实测] = 0 条** (板不在本机) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」
· ★**不许自签 issue_log** (★status 留给 main 落 verified★)
· ★**⚠️ 本单不许改 `SW/tools/check_demo_panel_spec.py` 与 `SW/SW_MD5_BASELINE_LEDGER.md`** (★那是 ISS-225 的产物, md5 受保护 ⇒ 你一改就会把 R6 三方对账搞红★) ⇒ ★**你要新写脚本, 就新写, 别改旧的** ★

★★**交卷前必须实跑并把输出原样贴进回复 ★★
```
python3 SW/tools/<你的新脚本>.py              # rc=0 (门禁全过)
python3 SW/tools/<你的新脚本>.py --selftest   # rc=0 (反向用例全抓到)
python3 SW/tools/check_demo_panel_spec.py     # rc=0 (★ISS-225 的门禁不许被你改红★)
python3 state/merge.py && python3 state/gate_check.py   # rc=0 且 【Q1 交付齐备率】 18/18
```
★**若上面某条门禁变红 ⇒ 不许放松门禁, 也不许回退别的东西来凑绿 ⇒ 交卷报红并说明原因 (★main 复核)**★"""

ISS227_BRIEF = """★★**目标 (★内部活·结构/热路口径侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 ISS-222 产物里那处「物理口径错」修正掉**: ★**P3 把镜框上沿 120×30 打印件顶面当成了与铝条同温的集热面** ★
⇒ ★**改正 = 集热面必须是铝制背板 (打印件顶面根本不参与散热)** ★ ⇒ 重算三档 ⇒ 落进门禁 ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 04:36 实查分片 + 实跑, 不是推测★)** ★★
· ★**这是 ISS-222 交卷时自己登记的 need** (`state/fragments/mech.yaml` 的 `iss222_mech_c7b_sink_is_metal_not_print`, to=main, ★**至今 open**★) ⇒ ★**它不在任何在飞单的范围里** ★
· ★**mech-lead 的名额刚空出来 (ISS-224 已于 04:07 落 verified)** ⇒ ★**这条与 ISS-223 落表互不依赖** ★ ⇒ ★**不占主线的时间窗** ★
· ★**为什么必须修**: ISS-222 的 C-7 结论「只有 P3 三档全达标 (45.95-46.63 °C)」★**是建立在「打印件顶面 = 集热面」这个错口径上的** ★ ⇒ ★**口径一改, 结论就翻 ⇒ 不改 = 带着错数往后传** ★

★★**依据 (★数字全部来自项目内已有实算, 不许自己另算一套★)** ★★
· ★**错在哪**: ISS-219 的 P3 把 ★**镜框上沿 120×30 打印件顶面**★ 当成 ★**与铝条同温**★ 的集热面 (口径内算得 46.63 °C ✅) ★
  ⇒ ★**但打印件 PA-CF k=0.2 沿上沿方向的热阻 = 3610 K/W (70 mm 段, 96.96 mm² 截面)**★ ⇒ ★**远离铝条的部分几乎不参与散热** ★
  ⇒ ★**顶面有效热导 R = 398.9 K/W vs 同面积直接对流 47.6 K/W (★差 8.4 倍★)**★ ⇒ ★**实算腔体 53.60 °C ❌ (超 50 °C 红线 3.60 °C, d=15 u8=30)** ★
· ★**三条降级路径 (都有数, 不许拍脑袋)** ★:
  (a) ★**铝制集热背板 120×30×1.0**★ ⇒ ★**不是【可选降级】, 是 P3 成立的【必要条件】**★ ⇒ 装上: ★**47.77 °C @0.468 W / 48.65 °C @0.50 W ✅, P_max 0.5496 W, +9.72 g = 2.70 mg/mm²**★
  (b) ★**面板降到 0.415 W 时打印件方案仍 51.49 °C ❌**★ ⇒ ★**降功耗单独做不成立, 必须与 (a) 同做** ★
  (c) ★**端件整条金属化 11.34-22.68 g 换 600-800 mm² = 14.18-37.80 mg/mm²**★ ⇒ ★**贵 5.3-14.0 倍且面积仍差 3-7 倍, 腔体 61.64-64.60 °C ❌**★ ⇒ ★**不可接受 (有数)** ★
· ⇒ ★**要你做的 = 把 P3 的集热面从「打印件顶面」改成「铝制集热背板 120×30×1.0, 与铝条同温」, 然后重算三档 (d=15/18/20) 的腔体温度** ★

★★**交付物 (4 件, 少一件即无效) ★★
① ★**口径修正落进 `MECH/CENTER_CAVITY_REBALANCE_V3.md`** (★ISS-222 的产物, 你自己的地界★) ⇒ ★**C-7b 独立成节**★, 写清 ★**旧口径 (打印件顶面当集热面) → 新口径 (铝制背板) → 数字前后对比**★ ⇒ ★**旧数不许删, 留成「已修正 (留痕)」** ★
② ★**三档重算 (d=15 / 18 / 20) + u8 口径写清** ★ ⇒ ★**每个数标证据等级** ★ (★本单实物 [实测] = 0 条 ⇒ 只允许 [推算]★) ⇒ ★**不许把 53.60 °C 这个错口径数悄悄换掉而不留痕** ★
③ ★**机器门禁 (扩 `MECH/cavity_recalc_check.py` + `--selftest`)** ★ ⇒ ★**新增断言: 「打印件顶面不许被当成集热面」(机械判据 = 集热面材质字段必须是铝/金属, 打印件 ⇒ 红)**★ ⇒ ★**反向用例 ≥3 条 (把集热面材质改回打印件 / 删掉 C-7b 节 / 改 50 °C 判据 ⇒ 全红)** ★ ⇒ ★**判据阈值 (50 °C / k=201 / P3 几何 120×30) 一个不许动** ★ ⇒ ★**门禁不许靠删断言变绿** ★
④ ★**交接单 (新建) `HANDOFF/2026-11-16_mech-lead_ISS227_C7b集热面口径修正.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写★)** ★ ⇒ ★**交卷贴分片 mtime 前/后** ★

★★**边界 (★违反一条即本单无效★)** ★★
· ★**不许改** `HW/` 任何文件 · 不许改 `SW/` 任何文件 · 不许改 `state/issue_log.yaml` · 不许改 `PROJECT_TRACKER.md` §0 · 不许碰 `state/outbox/` · 不许碰别人的分片
· ★**不许改** `MECH/hinge_usb_check.py` / `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` / `MECH/display_biosafety_v2_check.py` (★4 个受保护脚本, md5 逐字节不许变★) ⇒ ★**你只许改 `MECH/cavity_recalc_check.py` 与 `MECH/CENTER_CAVITY_REBALANCE_V3.md`** ★
· ★**不许改判据阈值** (50 °C / k=201 / P3 几何 120×30 / 皮肤 43 °C / 端件 60 °C ⇒ ★**一个不许动**★) ⇒ ★**改的是【假设/口径】, 不是【阈值】** ★
· ★**不许代拍老板级项**: ★**集热面最终做成什么材质 / u8 端件截面 / 面板功耗档 / 整机形态 ⇒ 一律只列选项 + 量化代价, 不许拍** ★ ⇒ ★**拍板权在 main / 老板** ★
· ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★)
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★
· ★**本单实物 [实测] = 0 条** (板不在本机)
· ★**不许自签 issue_log** (★status 留给 main 落 verified★)

★★**交卷前必须实跑并把输出原样贴进回复 ★★
```
python3 MECH/cavity_recalc_check.py            # rc=0 (含新增的 C-7b 断言)
python3 MECH/cavity_recalc_check.py --selftest  # rc=0 (反向用例全抓到)
python3 MECH/check_demo_struct_truth.py         # rc=0 (★ISS-224 刚重锚的门禁不许被你改红★)
python3 MECH/verify_budget.py                  # rc=0
python3 state/merge.py && python3 state/gate_check.py   # rc=0 且 【Q1 交付齐备率】 18/18
```
★**若上面某条门禁变红 ⇒ 不许放松门禁, 也不许回退别的东西来凑绿 ⇒ 交卷报红并说明原因 (★main 复核)**★"""

NEW_ISSUES = [
    {
        "id": "ISS-226",
        "title": "★★[主线内·软件/光生物安全判据侧·内部活] 光生物安全的「出瞳白场辐亮度最大值」在 SW 侧亮度控制策略里可判化: 蓝光通道占比上限 25% (名义 8.26%) 落进策略 + 亮度 API 蓝通道占比可标定量 + 机器门禁 + 反向用例",
        "severity": "high",
        "source_blocker": "ISS-134",
        "desc": "★**这是 ISS-134 从结构侧跨域登记给 SW 侧的 need** (`state/fragments/mech.yaml` 的 `iss134_sw_blue_drive_ratio_cap`, to=sw-lead, ★**至今 open**★) ⇒ ★**项目里本来就挂着、没人接的单** ★\n"
                "★**要做的**: ★**光生物安全的输入量 = 出瞳白场辐亮度的最大值**, 而 ★**亮度控制策略 (蓝光主通道占空 / 码值上限) 直接决定这个最大值落在哪** ★ ⇒ SW 侧要保证 ★**亮度控制策略里有「面板蓝光通道辐亮度占白场辐亮度上限 25% (保守)」这条上限** ★, 并 ★**在亮度 API 上留一个可标定的蓝通道占比量** ★\n"
                "★**名义值 8.26%** = DCI-P3 蓝基色 x=0.150 y=0.060 的 Y_B=0.0798 / 红 0.3850 / 绿 0.5017 (★等辐射功率下算★) ★\n"
                "★**越限后果**: L_eye > 1500 cd/m2 ⇒ ★**掉出 IEC 62471 Exempt (RG0) 进 RG1** (L_B 100..10000 W/(m2*sr)) ⇒ ★**需要用户信息 / 标签说明** (★不是禁视警示, 那要到 RG2 才有★) ★\n"
                "★**判定与测量的真源在结构侧**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` §3.2 与 §3.6 ⇒ ★**SW 侧只读引用, 不许改** ★\n"
                "★**本单不依赖任何在飞单** ⇒ 落在本轮 (sw-lead 名额刚被 ISS-225 验收放出来) ★",
        "owner": "sw-lead",
        "task_brief": ISS226_BRIEF,
        "note": "2026-11-16 04:36 本 job (775d9893) 新开 ★**依据 = main 本轮实查分片: `state/fragments/mech.yaml` 的 `iss134_sw_blue_drive_ratio_cap` (to=sw-lead) 至今 open** ★\n"
                "★**这是项目里本来就挂着的跨域 need, 不是 main 现编的活** ★ ⇒ ★**它不依赖任何在飞单 ⇒ 不占主线时间窗** ★\n"
                "★**sw-lead 名额的上一条 ISS-225 本轮 04:36 落 verified (main 实跑 rc=0 + selftest 16/16) ⇒ 名额放出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (结构侧地界) · 不改 `HW/` · 不改 ISS-225 的 `check_demo_panel_spec.py` 与 `SW_MD5_BASELINE_LEDGER.md` (受保护 md5) · 判据数值 (25% / 8.26% / 1500 cd/m2) 一个不许动 · 零外发 · 板端 [实测] = 0 条 · 不自签 issue_log ★",
    },
    {
        "id": "ISS-227",
        "title": "★★[主线内·结构/热路口径侧·内部活] ISS-222 产物的 C-7b 物理口径错修正: P3 把「镜框上沿 120×30 打印件顶面」当成与铝条同温的集热面 (R 398.9 vs 47.6 K/W, 差 8.4 倍 ⇒ 实算腔体 53.60 °C ❌) ⇒ 集热面改铝制背板 + 三档重算 + 门禁 + 留痕",
        "severity": "high",
        "source_blocker": "ISS-222",
        "desc": "★**ISS-222 交卷时自己登记的 need** (`state/fragments/mech.yaml` 的 `iss222_mech_c7b_sink_is_metal_not_print`, to=main, ★**至今 open**★) ⇒ ★**不在任何在飞单的范围里** ★\n"
                "★**错在哪**: ISS-219 的 P3 把 ★**镜框上沿 120×30 打印件顶面**★ 当成 ★**与铝条同温**★ 的集热面 (口径内算得 46.63 °C ✅) ★\n"
                "· ★**打印件 PA-CF k=0.2 沿上沿方向热阻 = 3610 K/W (70 mm 段, 96.96 mm² 截面)**★ ⇒ ★**远离铝条的部分几乎不参与散热** ★\n"
                "· ★**顶面有效热导 R = 398.9 K/W vs 同面积直接对流 47.6 K/W (★差 8.4 倍★)**★ ⇒ ★**实算腔体 53.60 °C ❌ (超 50 °C 红线 3.60 °C, d=15 u8=30)** ★\n"
                "★**降级路径 (都有数)**: (a) ★**铝制集热背板 120×30×1.0 不是【可选降级】, 是 P3 成立的【必要条件】**★ ⇒ 47.77 °C @0.468 W / 48.65 @0.50 W ✅ · P_max 0.5496 W · +9.72 g = 2.70 mg/mm² ; (b) 面板降到 0.415 W 时打印件方案仍 51.49 °C ❌ ⇒ 必须与 (a) 同做 ; (c) 端件整条金属化 11.34-22.68 g 换 600-800 mm² = 14.18-37.80 mg/mm² (贵 5.3-14.0 倍, 腔体 61.64-64.60 °C ❌) ⇒ 不可接受 (有数) ★\n"
                "★**为什么要修**: ISS-222 的 C-7 结论「只有 P3 三档全达标 (45.95-46.63 °C)」★**建立在那个错口径上** ★ ⇒ ★**口径一改结论就翻 ⇒ 不改 = 带错数往后传** ★",
        "owner": "mech-lead",
        "task_brief": ISS227_BRIEF,
        "note": "2026-11-16 04:36 本 job (775d9893) 新开 ★**依据 = main 本轮实查分片: `state/fragments/mech.yaml` 的 `iss222_mech_c7b_sink_is_metal_not_print` (to=main) 至今 open** ★\n"
                "★**它不在任何在飞单的范围里 ⇒ 与 ISS-223 落表互不依赖 ⇒ 不占主线时间窗** ★\n"
                "★**mech-lead 名额的上一条 ISS-224 已于 04:07 落 verified ⇒ 名额空着 ⇒ 本单接档** ★\n"
                "★**⚠️ 下一轮若 ISS-223 落表 ⇒ MECH 闸 G5b + C21 会按设计变红 (锚点过期) ⇒ 那时再派 mech-lead 走重锚 (本单不许碰 MECH 锚点, 免得与落表抢)** ★\n"
                "★**边界**: 不改 `HW/` / `SW/` · 不改 4 个受保护脚本 (hinge_usb_check / service_port_check / hw_cross_review_check / display_biosafety_v2_check) · 判据阈值 (50 °C / k=201 / P3 几何 120×30) 一个不许动 · 只许改 `MECH/cavity_recalc_check.py` + `MECH/CENTER_CAVITY_REBALANCE_V3.md` · 不代拍老板级项 (集热面最终材质 / u8 / 功耗档) · 零外发 · 不自签 issue_log ★",
    },
]


def main() -> int:
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if os.path.exists(LOG):
            shutil.copy2(LOG, BAK)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f) or {}
        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}
        changed = []

        # ① 落账 verified
        for iid, (vres, vdate) in VERIFY.items():
            it = by_id.get(iid)
            if not it:
                print("!! 找不到", iid)
                continue
            it["status"] = "verified"
            it["verify_result"] = vres
            it["verify_date"] = vdate
            it["verify_by"] = "main"
            changed.append(f"{iid} → verified (main 04:36 独立复核)")

        # ② ISS-223 续做登记 (保持 fixing)
        it223 = by_id.get("ISS-223")
        if it223:
            it223["note"] = (it223.get("note") or "") + CONT_223_NOTE
            it223["status"] = "fixing"       # ★保持: 续做同一个单, 不占第二个名额★
            it223["verify_result"] = None
            it223["verify_date"] = None
            changed.append("ISS-223 → 保持 fixing + 追加续做登记 (会话 timeout, 半成品)")

        # ③ 新开 2 单 (status=open ⇒ 交给 advance.py --apply 标 fixing)
        for spec in NEW_ISSUES:
            if spec["id"] in by_id:
                print("!! 已存在, 跳过", spec["id"])
                continue
            new = {
                "id": spec["id"],
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
            }
            issues.append(new)
            changed.append(f"{spec['id']} → {spec['owner']} 新开 (open, 待 advance.py --apply 标 fixing)")

        log["issues"] = issues
        with open(LOG, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        fcntl.flock(lk, fcntl.LOCK_UN)

    print("★已落盘 (备份 %s):" % os.path.basename(BAK))
    for c in changed:
        print("   ·", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
