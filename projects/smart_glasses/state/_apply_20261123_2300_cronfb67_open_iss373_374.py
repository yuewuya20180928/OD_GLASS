#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 23:0x · 新开 ISS-373 / ISS-374 并落 `fixing`** ★

★**为什么开单 (★本机实读·不是猜★)★**:
  ① `python3 state/advance.py --json` ⇒ ★**internal: []** (三个总工名下零 `open` 可派)
  ② ★**本轮 22:4x~22:5x main 把 ISS-369 / ISS-371 签收了 ⇒ 那两个槽位【真空出来了】** ★
     (★`state/issue_log.yaml` 实读: ISS-369 → verified · ISS-371 → verified · ISS-372 仍 fixing 且
      `HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md` 已在盘 + sw.yaml 命中 17 ⇒ sw-lead 那一格是**真在飞**★)
     ⇒ ★**⇒ hw-lead / mech-lead 两个槽位空着、名下零 open 项 ⇒ 队列对这两条线是真断的 (不是被占满, 是没活)** ★
  ③ ★**两件活都有本机实算出来的真依据 (★全部可复跑·不是编的·不抄任何 agent 报告★)★**:
     · ★**ISS-373 (hw-lead)**: 「S10 那一趟换几件」在全项目同时活着【四套口径】:
         ① `MECH/check_onepass_s10_fp_swap_impact.py` 实跑 ⇒ 90 (77 + 13)
         ② `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.3 (ISS-369) ⇒ 90 / 96 / 186 / 158
         ③ `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6 (ISS-367) ⇒ ★**同一页里「90」与「91」并存** ★
         ④ `MECH/check_onepass_s10_led_spec_sync.py --compute` 实跑 ⇒ ★**`swap_all90_n: 91` (变量名叫 all90、值是 91)** ★
       ★**main 本机实算 (用 ① 与 ③ 各自的真函数) ⇒ C4=158 · iss356=78 · inter=77 · gap=13 ·
         `iss - inter - gap` = `['J_DEBUG']` (★恰好一件★) ⇒ **90 = inter + gap · 91 = iss + gap** ★**
       ★**⇒ 而 `J_DEBUG` 恰恰是那一趟【另一条腿要换 land】的那件** ★
       (★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (ISS-290 · step S6) 原文:
         「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm」+ 期望读数「J_DEBUG land pitch = 1.27」★)
       ★**⇒ 而 ISS-369 表 B 那行写「不写库名」的理由正是「本件不在 90 件换 land 名单里 ⇒ 本趟不动它的 land」★★
       ★**⇒ 若那一趟换 91 件 ⇒ 按 ISS-369 自己的 §2.3 (换 land 必须同时写库名) ⇒ 「写 94 / 不写 92」两个数也要跟着变** ★
       ★★**⇒ 这一件在「那一趟」换不换 land, 两条路的结构后果完全不同 ⇒ 是「板 md5 会不会变第二次」的开关** ★★
     · ★**ISS-374 (mech-lead)**: `J_UART` 这颗 1×2 排针在【同一条板侧项 B33】里, 结构侧真相【至今零覆盖】:
         ★**本机实读**: `grep -c J_UART MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ **0** (ISS-371 只做了 1×4 那颗) ★
         ★**本机实读板面**: J_UART = 2 pad · pitch 0.50 · pad 0.275×0.900 · 铜箔 X **18.5025..19.2775 (宽 0.7750)** ★
         ★**本机实读官方 land**: `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ pad1 `thru_hole rect` (0 0) size 1 1 ·
           pad2 `thru_hole circle` (0 1.27) size 1 1 ⇒ 摆成板上 X 向 1×2 后 ★**铜箔 X 宽 = 1.27 + 1.0 = 2.2700** ★
         ★**本机实读座体必须清空区** (`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5): X **17.620..20.160 (宽 2.5400)** ★
         ★★**⇒ main 本机实算: 每边余量 (2.5400 − 2.2700) / 2 = 0.1350 < `CRIT` 0.60 ⇒ 铜箔进清空区** ★★
           (★现状每边 0.8825 ⇒ Δ −0.7475★ ⇒ ★**方向与 `J_DEBUG` 那颗【相反】** (★J_DEBUG 仍过 CRIT·余量 3.99×·ISS-371 已算★)★)
         ★★**⇒ 那一趟若照 B33 把 J_UART 也换成官方 land ⇒ 结构件装不上 ⇒ 要么结构件返工, 要么板 md5 变第二次** ★★
  ④ ★**两条都是 PCB 线的【纯分析 + 作业包 + 新建闸 + 沙盒预演】⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① (先派纯分析/作业包类)★**

★**★防撞车 (★铁律⑩-i: 先落 `fixing` 再 spawn★)★**:
  ★**status 直接落 `fixing` ⇒ 兄弟 job 775d9893 读的是同一个字段 ⇒ 它看到 fixing 就不会再派 ⇒ 零撞车窗口** ★
  ★**issue_log 写回用【文本追加】(★不是全文件 yaml 重排·★实测全文件重排会把已签收单的 verify_result 折行重排·属 churn★)⇒ 前 367 条逐条逐字节不变** ★
  ★**dispatch_log 同样文本追加 ⇒ 前 381 条逐条逐字节不变** ★

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
STAMP = "20261123_2300_cronfb67_open_iss373_374"

BRIEF373 = "ISS-373_hw_s10_swapsite_set_truth.md"
BRIEF374 = "ISS-374_mech_juart_1p27_clearance_truth.md"

B373 = open(os.path.join(HERE, "dispatch_briefs", BRIEF373), encoding="utf-8").read()
B374 = open(os.path.join(HERE, "dispatch_briefs", BRIEF374), encoding="utf-8").read()

TITLE373 = (
    "★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 换件集合的【唯一真源】+ 一条「集合口径」机器闸·纯分析+作业包+新建闸+沙盒预演·零写板] ★★"
    "【★main 2026-11-23 22:4x~23:0x 本机实算★: 「S10 那一趟换几件」在全项目同时活着【四套口径】—— "
    "① `MECH/check_onepass_s10_fp_swap_impact.py` 实跑 ⇒ 90 (靶内 77 + 缺口 13) · "
    "② `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.3 (ISS-369) ⇒ 90 / 96 / 186 / 158 · "
    "③ `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6 (ISS-367) ⇒ ★**同一页里「90」与「91」并存** ★ · "
    "④ `MECH/check_onepass_s10_led_spec_sync.py --compute` 实跑 ⇒ ★**`swap_all90_n: 91` (变量名叫 all90、值是 91)** ★ "
    "⇒ ★★main 本机实算 (用 ① 与 ③ 各自的真函数): C4=158 · iss356=78 · inter=77 · gap=13 · "
    "`iss - inter - gap` = `['J_DEBUG']` (★**恰好一件★) ⇒ **90 = inter + gap · 91 = iss + gap** ★★ "
    "⇒ ★★而 `J_DEBUG` 恰恰是那一趟【另一条腿要换 land】的那件 ★★ (★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 "
    "`B33_PIN_LAND_1P27` (ISS-290 · step S6) 原文「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm」+ "
    "期望读数「J_DEBUG land pitch = 1.27」★) ⇒ ★★而 ISS-369 表 B 那行写「不写库名」的理由正是"
    "「本件不在 90 件换 land 名单里 ⇒ 本趟不动它的 land」★★ ⇒ ★★**若那一趟换 91 件 ⇒ 按 ISS-369 自己的 §2.3 "
    "(换 land 必须同时写库名) ⇒ 「写 94 / 不写 92」两个数也要跟着变** ★★ "
    "⇒ ★**这一件换不换 land, 两条路的结构后果完全不同 ⇒ 是「板 md5 会不会变第二次」的开关** ★ "
    "⇒ ★★**本单 = ① 一页集合真源 (四套口径逐条对表 + `J_DEBUG` 四条腿的完整账 + 两条路各自的联动手算式) "
    "② 一条「集合口径」机器闸 (L0~L8 · 集合算法自算不许写死 90/91 · 差集必须恰为 1 件 · 页里两个数都要在) "
    "③ 沙盒 S0/S1/S2 三轮 (90 件 vs 91 件各换一次, 报 C1~C4 + 段数/过孔/零铜网/单边零铜对 + `J_DEBUG` 换完的实测 land pitch/铜箔宽/fab) "
    "④ 未决项只登记不代拍 (★「`J_DEBUG` 那一趟换不换 land」归 main 裁★)** ★ "
    "★【纯分析 + 作业包 + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★"
)

DESC373 = (
    "★**main 2026-11-23 22:4x~23:0x 本机实读 + 本机实算 (★不抄任何 agent 报告·全部可复跑★)★** ⇒ "
    "★**① 四套口径的逐条实读★**: "
    "① `MECH/check_onepass_s10_fp_swap_impact.py` 实跑输出「靶内 = 77 件 + 缺口 = 13 件 ⇒ S10 要换官方 land 的集合 = 90 件」· "
    "② `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.3「本单对象 (表 A) = 90 · 其余 (表 B) = 96 · 板面封装总数 = 186 · C4 占位脚号件数 = 158」· "
    "③ `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6 标题写「若那一趟把 90 件全换」但表格行写「AFTER (全部 91 件靶子都换) ⇒ 2200」"
    "且 §4.2 写「91 件靶子全换 ⇒ 块数 2183→2200」 ⇒ ★**同一页两个数** ★ · "
    "④ `python3 MECH/check_onepass_s10_led_spec_sync.py --compute` 实跑 JSON 末尾 `\"swap_n\": 25, \"swap_all90_n\": 91` "
    "⇒ ★**脚本自己算出来是 91, 变量名却叫 swap_all90** ★ "
    "★**② main 本机实算 (★只读 import 两道真闸自己的函数·不改任何文件★)★**: "
    "`bom=cov.load_bom('HW/BOM_v1.csv')` · `c4=set(cov.netlist_placeholder('HW/netlist_v1.csv'))` · "
    "`iss=set(mech.read_iss356_targets(root))` · `gap=cov.coverage_gap(bom,c4)` · `inter=iss&c4` "
    "⇒ 实测输出 **C4=158 · iss356=78 · inter=77 · gap=13** · `iss-inter-set(gap)` = **`['J_DEBUG']`** (★**恰好一件★**) "
    "⇒ **90 = inter + gap · 91 = iss + gap** ★ "
    "★**③ `J_DEBUG` 这 1 件的完整账 (★四条腿★)★**: ① 不在 C4 158 里 (★实算★) · ② 在 ISS-356 靶子 78 里 (★实算★) "
    "⇒ ★**这正是 90 vs 91 的那 1 件差** ★ · ③ `B33_PIN_LAND_1P27` 要不要动它的 land ⇒ ★**要** ★ · "
    "④ ISS-369 表 B 写「不写库名」的理由 ⇒ ★**「本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land」** ★ "
    "⇒ ★**④ 的前提与 ③ 冲突** ★ "
    "★**④ 两条路各自的联动手 (★只给算式不代拍★)★**: 若换 91 件 ⇒ 按 ISS-369 §2.3 (换 land 必须同时写库名·同一封装块 ①②③④ 同一次做完"
    "⇒ 板 md5 只变一次) ⇒ 「写 94 / 不写 92」两个数要变; 若换 90 件 ⇒ `B33` 的期望读数「J_DEBUG land pitch = 1.27」永远达不到 "
    "⇒ ★**实物 1.27mm 排针仍然落不进 ⇒ 板要么改第二次, 要么实物报废** ★ "
    "★**⑤ 为什么这必须是机器判据而不是文档措辞★**: 「板只改一次」= 板 md5 只许变 1 次 "
    "(★`HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-1/INV-3★) ⇒ ★**「换几件」只要开工当天还有第二种口径, "
    "就必然有人按错的那份布局 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ "
    "★**本单零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动) · "
    "零落表 (网表/脚表/BOM 只读) · 零改既有闸 · 零改既有页面正文 (只新写一页 + 一条闸) · 零挂链 · 零外发 · 不代老板拍板** ★"
)

TITLE374 = (
    "★★[★新主线·PCB 线·结构侧·「板那一趟」`J_UART` 排针 land 改 1.27mm 的结构侧净距真相 (ISS-371 的姊妹件·同一条 `B33` 板侧项)·纯分析+文档订正(追加式)+新建闸+沙盒预演·零写板] ★★"
    "【★main 2026-11-23 22:4x~23:0x 本机实算★: ISS-371 (2026-11-23 22:4x 刚被 main 签收 verified) 交付了 `J_DEBUG` 这颗 1×4 排针的结构侧净距真相"
    "(一页 + 一条闸 `MECH/check_jdebug_1p27_clearance.py` · 本机 22:5x 实跑 rc=0 · 7/7 全绿), ★**但 `J_UART` 那颗 1×2 排针在同一条板侧项里结构侧一个字都没有**★ "
    "—— ★**① 同一条项点了两件★**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (ISS-290 · step S6) 原文"
    "「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」+ 期望读数"
    "「J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27」 ⇒ ★**「换 1.27」板上落两件, 结构侧真相只做了一件**★ · "
    "★**② ISS-371 的真相页对 `J_UART` 零覆盖★**: 本机实跑 `grep -c J_UART MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ **0** (★不是「提了一句」, 是整颗件没进这一页★) · "
    "★**③ ISS-371 的闸也只认 1×4 那颗★**: 该闸常量 `THT_MOD_NAME = PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ ★**`J_UART` 那颗件的 land 改了, 这条闸不会红**★ "
    "⇒ ★★**main 本机实算 (★读板 + 读盘上 `.kicad_mod` + 算★)★**: `J_UART` 现状 = 2 pad · pitch 0.50 · pad 0.275×0.900 · "
    "铜箔 X **18.5025..19.2775 (宽 0.7750)** · fab 6.000×4.000 · net UART_TX/UART_RX ⇒ "
    "官方 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` 实读 = pad1 `thru_hole rect` (0 0) size 1 1 · pad2 `thru_hole circle` (0 1.27) size 1 1 "
    "⇒ 摆成板上 X 向 1×2 后 ★**铜箔 X 宽 = 1.27 + 1.0 = 2.2700**★ · "
    "座体必须清空区 (★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 本机实读★) X **17.620..20.160 (宽 2.5400)** ⇒ "
    "★★**每边余量 (2.5400 − 2.2700)/2 = 0.1350 < `CRIT` 0.60 (★`MECH/service_port_check.py` L127 真身★) ⇒ 铜箔进座体必须清空区**★★ "
    "(★现状每边 0.8825 ⇒ Δ −0.7475★ ⇒ ★**方向与 `J_DEBUG` 那颗【相反】** (★J_DEBUG 仍过 CRIT·余量 3.99×·ISS-371 已算★)★) "
    "⇒ ★★**⇒ 那一趟若照 `B33` 把 `J_UART` 也换成官方 land ⇒ 结构件装不上 ⇒ 要么改结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑**★★ "
    "⇒ ★★**本单 = ① 一页 `J_UART` 真相 (与 `J_DEBUG` 并排对照 · 现状/官方THT/官方SMD降级 三档量差 · 两个后果分开写 · 降级方案给代价不代拍) "
    "② 一条 `J_UART` 专用闸 (J0~J8 · 官方land几何自算不许写死 · 两件方向结论必须并排出现 ⇒ 防「拿一颗的结论套另一颗」· ≥8 条反向用例含 2 条针对该病根) "
    "③ 沙盒 S0/S1/S2/S3 四轮 (含 S3 反向对照轮: `J_DEBUG` 也换一次 ⇒ 证明两件方向确实不同, 若算出一样则停下报告不许硬写「过」)** ★ "
    "★【纯分析 + 文档订正(追加式) + 新建闸 + 沙盒预演类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 (含 ISS-371 已签收件) · 零挂链 · 零外发 · 不代老板拍板】★★"
)

DESC374 = (
    "★**main 2026-11-23 22:4x~23:0x 本机实读 + 本机实算 (★不抄任何 agent 报告·全部可复跑★)★** ⇒ "
    "★**① 本机实读板面 (★`bash state/pcbnew_py.sh` · KiCad 10.0.8★)★**: "
    "`J_UART` = 2 pads · lib_id `''` · pad centers X [18.64, 19.14] Y [68.6, 68.6] · **pitch 0.5** · "
    "pad1/pad2 size 0.275 × 0.900 · net UART_TX / UART_RX ⇒ ★**现状铜箔 X = 18.5025..19.2775 (宽 0.7750)**★ "
    "★**② 本机实读官方 land (★读盘上 `.kicad_mod`, 不抄文档★)★**: "
    "`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ "
    "`(pad \"1\" thru_hole rect (at 0 0) (size 1 1))` · `(pad \"2\" thru_hole circle (at 0 1.27) (size 1 1))` · "
    "`fp_rect -1.55 -1.14 .. 1.55 2.41` ⇒ ★**摆成板上 X 向 1×2 直排 (转 90°/270°) 后铜箔 X 宽 = 跨距 1.27 + pad 宽 1.0 = 2.2700**★ "
    "★**③ 本机实读座体必须清空区 (★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5★)★**: "
    "UART 检修口 必须清空区 X **17.620..20.160 (宽 2.5400)** × Y 67.330..69.870 · 开口 X 13.790..23.990 × Y 66.300..70.900 · "
    "现页的「单边间隙 X 3.830 / 最坏 3.530」是按【现状铜箔 0.7750】算的 "
    "★**④ main 本机实算 (★不是抄★)★**: 每边余量 = (2.5400 − 2.2700)/2 = **0.1350** ⇒ 现状 (2.5400 − 0.7750)/2 = **0.8825** ⇒ Δ **−0.7475** · "
    "★**`CRIT` = 0.60 (★`MECH/service_port_check.py` L127 `CRIT = 2 * TOL[\"fdm_part\"]`·`TOL[\"fdm_part\"]`=0.30·真身取值不许写死★)** ⇒ "
    "★★**0.1350 < 0.60 ⇒ 铜箔进座体必须清空区 (每边越界 0.4650)**★★ ⇒ "
    "★★**方向与 `J_DEBUG` 那颗【相反】** (★J_DEBUG 换官方 1×4 THT 后单边间隙 2.6950 · 最坏 2.3950 · 仍过 CRIT · 余量 3.99×·ISS-371 已算★)**★★ "
    "★**⑤ ⇒ 后果 (★两句必须分开写★)★**: ★**事实句** = 若那一趟按 `B33` 把 `J_UART` 也换成官方 land ⇒ 每边余量 0.1350 ⇒ 铜箔进座体必须清空区 ⇒ 结构件装不上; "
    "★**判据句** = 方向本身仍可救 (★降级候选: ① 座体必须清空区 X 宽从 2.5400 放宽到 ≥ 2.2700 + 2×0.60 = 3.4700 (★动结构件 ⇒ 归 mech-lead 结构侧页 + 老板口径★) "
    "② 换官方 SMD 变体 (`PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left` / `_SMD_Pin1Right`·几何另算·不许拿 THT 的数套用) "
    "③ `J_UART` 改选型/改座体 ④ `J_UART` 那颗那一趟不换 land (★要动 `B33` ⇒ 归 main★) ⇒ 每条给代价, 不许代拍★)** ★ "
    "★**⑥ 本单与 ISS-371 的关系 (★不许重复发明·也不许改它的地界★)★**: "
    "`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 `MECH/check_jdebug_1p27_clearance.py` 是 ISS-371 的交付物 (★已被 main 签收 verified★) "
    "⇒ ★**本单一个字都不许改** ★ (★改已签收件 = 破坏留证链★) ⇒ ★**只新建 `J_UART` 自己的一页一闸** ★ "
    "★**⑦ 沙盒四轮 (★真板零改动★)★**: S0 基线 · S1 `J_UART` 换官方 1×2 THT · S2 `J_UART` 换官方 1×2 SMD 变体 · "
    "★**S3 反向对照轮: `J_DEBUG` 也换一次 ⇒ 证明两颗件方向确实不同 (若算出一样 ⇒ 说明算法与 ISS-371 不一致 ⇒ 停下报告, 不许硬写一个「过」的结论)** ★ "
    "★**本单零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动) · "
    "零落表 (网表/脚表/BOM 只读) · 零改既有闸 · 零改既有页面正文 (含 ISS-371 已签收件) · 零挂链 · 零外发 · 不代老板拍板** ★"
)

NEW = [
    {
        "id": "ISS-373",
        "title": TITLE373,
        "severity": "high",
        "source_blocker": "ISS-369",
        "source_agent": "main",
        "desc": DESC373,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss367_mech_s10_swap_set_count_to_main"],
        "task_brief": B373,
        "note": (
            "★2026-11-23 23:0x cron fb67af40 新开并【直接落 fixing】"
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★)"
            " ★ **开单依据**: ① `state/advance.py --json` 实跑 ⇒ internal: [] (三个总工名下零 open 可派) "
            "② ★**本轮 22:4x~22:5x main 把 ISS-369 / ISS-371 签收了 ⇒ hw-lead / mech-lead 两个槽位【真空出来了】** "
            "⇒ ★**名下零 open 项 ⇒ 队列对这两条线是真断的 (不是被占满, 是没活)** "
            "③ ★**本机实算出来的真依据 (★全部可复跑·不抄任何 agent 报告★)★**: "
            "「S10 那一趟换几件」全项目同时活着四套口径 ⇒ main 用两道真闸自己的函数实算 ⇒ "
            "C4=158 · iss356=78 · inter=77 · gap=13 · `iss-inter-gap` = `['J_DEBUG']` ⇒ 90 = inter+gap · 91 = iss+gap; "
            "★**而 `J_DEBUG` 恰恰是那一趟另一条腿 (`B33_PIN_LAND_1P27`) 要换 land 的那件** ⇒ "
            "★**换 90 还是 91 直接决定「板 md5 会不会变第二次」** ★ "
            "④ 本单 = 纯分析 + 作业包 + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① "
            "★ **任务书全文**: `state/dispatch_briefs/ISS-373_hw_s10_swapsite_set_truth.md` "
            "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★)"
        ),
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-374",
        "title": TITLE374,
        "severity": "high",
        "source_blocker": "ISS-371",
        "source_agent": "main",
        "desc": DESC374,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss356_jdebug_mech_clearance_recheck"],
        "task_brief": B374,
        "note": (
            "★2026-11-23 23:0x cron fb67af40 新开并【直接落 fixing】"
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★)"
            " ★ **开单依据**: ① `state/advance.py --json` 实跑 ⇒ internal: [] "
            "② ★**本轮 22:4x~22:5x main 把 ISS-369 / ISS-371 签收了 ⇒ hw-lead / mech-lead 两个槽位【真空出来了】** "
            "⇒ ★**名下零 open 项 ⇒ 队列对这两条线是真断的** "
            "③ ★**本机实算出来的真依据 (★全部可复跑·不抄任何 agent 报告★)★**: "
            "`J_UART` 这颗 1×2 排针在【同一条板侧项 `B33_PIN_LAND_1P27`】里, 结构侧真相至今零覆盖 "
            "(★`grep -c J_UART MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` = 0★) ⇒ "
            "main 本机实算: 现状铜箔宽 0.7750 ⇒ 换官方 1×2 THT 后 **2.2700** ⇒ 对座体必须清空区 2.5400 ⇒ "
            "★★**每边余量 0.1350 < CRIT 0.60 ⇒ 铜箔进清空区**★★ ⇒ "
            "★★**方向与姊妹件 `J_DEBUG` 相反** (★J_DEBUG 仍过 CRIT·余量 3.99×★) ⇒ "
            "★**那一趟若照 B33 换 ⇒ 结构件装不上 ⇒ 要么结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑** ★ "
            "④ 本单 = 纯分析 + 文档订正(追加式) + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① "
            "★ **任务书全文**: `state/dispatch_briefs/ISS-374_mech_juart_1p27_clearance_truth.md` "
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

        # ---------- issue_log: 文本追加 (★不全文件 yaml 重排·避免 churn★) ----------
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

        # ---------- dispatch_log: 文本追加 ----------
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
                "at": "2026-11-23 23:0x",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: "
                        "★**开单 + 直接落 fixing + spawn** (★铁律⑩-i 先落 fixing 再 spawn⇒兄弟 job 读同一字段⇒零撞车窗口★)"
                        " · ★**开单依据 = 本轮 22:4x~22:5x main 签收 ISS-369/ISS-371 后两个槽位真空 + 名下零 open 项 "
                        "⇒ 队列对这两条线真断线** ★"),
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
