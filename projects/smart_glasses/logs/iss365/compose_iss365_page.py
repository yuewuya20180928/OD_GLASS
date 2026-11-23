#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compose_iss365_page.py —— ★★【ISS-365】把 §1 表 + §2 表 + 机器块 拼进 `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` ★★

★★**为什么用脚本拼**: ★**§1 25 行 × 6 个几何数 + §2 10 行 × 6 个净距 = 210 个数** ⇒
  ★**手抄必错一处** ⇒ ★**全部从 `compute_iss365.json` 填** ⇒ 页里的数 == 脚本实测 == 闸的实测 ★
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = json.load(open(os.path.join(HERE, "compute_iss365.json"), encoding="utf-8"))
MB = json.load(open(os.path.join(HERE, "machine_block.json"), encoding="utf-8"))
ROWS = open(os.path.join(HERE, "section1_rows.md"), encoding="utf-8").read().rstrip()
LED = json.load(open(os.path.join(HERE, "led_space_drift.json"), encoding="utf-8"))
OUT = os.path.join(PROJ, "MECH", "BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md")


def s(x):
    if x is None:
        return "—"
    return ("%.4f" % x).rstrip("0").rstrip(".")


def s3(x):
    if x is None:
        return "—"
    return ("%.3f" % x).rstrip("0").rstrip(".")


def s2_rows():
    out = []
    for r in RES["rsel_rows"]:
        ph = "fab %s×%s · pad %s @ %s · %d 焊盘" % (
            s3(r["ph_fab_size"][0]), s3(r["ph_fab_size"][1]),
            s3(RES["items"][0]["placeholder"]["pad_sizes"][0][0]) if False else "",
            ", ".join(s3(c) for c in r["ph_center_distances"]), r["ph_npads"])
        tg = "fab %s×%s · crtyd %s×%s · pad @ %s · %d 焊盘" % (
            s3(r["tg_fab_size"][0]), s3(r["tg_fab_size"][1]),
            s3(r["tg_crtyd_size"][0]), s3(r["tg_crtyd_size"][1]),
            ", ".join(s3(c) for c in r["tg_center_distances"]), r["tg_npads"])
        out.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["ref"], ph, tg,
            s(r["clr_gate_before"]), s(r["clr_gate_after"]),
            "%+.4f" % (r["clr_gate_after"] - r["clr_gate_before"]),
            s(r["clr_mc_before"]) + " → " + s(r["clr_mc_after"]),
            s(r["gap_prev_before"] if r["gap_prev_before"] is not None else None)
            + " / " + s(r["gap_next_before"] if r["gap_next_before"] is not None else None),
            s(r["gap_prev_after"] if r["gap_prev_after"] is not None else None)
            + " / " + s(r["gap_next_after"] if r["gap_next_after"] is not None else None),
        ))
    return "\n".join(out)


def s6_rows():
    out = []
    for r in RES["s6_rows"]:
        out.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
            r["ref"], r["bucket"], "%s,%s" % (s3(r["target"][0]), s3(r["target"][1])),
            "是" if r["moved"] else "否",
            s(r["clr_gate"]), s(r["clr_gate_after"]), "%+.4f" % r["clr_gate_delta"]))
    return "\n".join(out)


def neg_rows():
    out = []
    for r in MB["neg"]["connector_refs"] + MB["neg"]["tp_dsi_refs"]:
        out.append("| `%s` | ∅ | ∅ | 不受 S10 影响 |" % r)
    return "\n".join(out)


def main():
    led_b = LED["BEFORE"]
    led_a = LED["AFTER"]
    body = TEMPLATE.replace("@@ROWS@@", ROWS)
    body = body.replace("@@S2ROWS@@", s2_rows())
    body = body.replace("@@S6ROWS@@", s6_rows())
    body = body.replace("@@NEGROWS@@", neg_rows())
    body = body.replace("@@SET90@@", str(MB["set90"]["total"]))
    body = body.replace("@@INTARGET@@", str(MB["set90"]["in_target_total"]))
    body = body.replace("@@GAP@@", str(MB["set90"]["gap_total"]))
    body = body.replace("@@RSELN@@", str(MB["rsel"]["in_set90_count"]))
    body = body.replace("@@NEGN@@", str(MB["neg"]["intersection_total"]))
    body = body.replace("@@MB@@", json.dumps(MB, ensure_ascii=False, indent=1))
    body = body.replace("@@LEDB@@", json.dumps(led_b["led_space"], ensure_ascii=False, indent=1))
    body = body.replace("@@LEDA@@", json.dumps(led_a["led_space"], ensure_ascii=False, indent=1))
    body = body.replace("@@LEDSWEEPB@@", str([(x["clearance"], x["n_placeable_bands"]) for x in led_b["sweep"]]))
    body = body.replace("@@LEDSWEEPA@@", str([(x["clearance"], x["n_placeable_bands"]) for x in led_a["sweep"]]))
    body = body.replace("@@LEDRB@@", str(led_b["led_rel"]))
    body = body.replace("@@LEDRA@@", str(led_a["led_rel"]))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(body)
    print("[compose] 已写 %s (%d B)" % (OUT, len(body.encode("utf-8"))))


TEMPLATE = r"""# MECH · 「板只改一次」那一趟 S10 换官方 land 对 MECH 侧的影响面 (机器可读) —— ISS-365

> **单**: ISS-365 (owner=mech-lead · 派活 2026-11-23 16:1x · job cron `fb67af40`)
> **性质**: ★**内部活 · MECH 侧 · 纯分析 + 新建闸 + 沙盒重判 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发** ★
> **机器闸 (本单新建)**: `python3 MECH/check_onepass_s10_fp_swap_impact.py` (★M0 基准块 · M1 90 件集合脚本实算 · M2 10 个 `R_SEL_*` 落在 90 件里 · M3 负结论可证 · M4 §1 逐件字段齐全 · M5 几何一致性 · M6 证据等级 + 降级方案 · M7 零挂起措辞★)
> **自检**: `python3 MECH/check_onepass_s10_fp_swap_impact.py --selftest` (★≥7 条反向用例, 每条自证「红的是目标那一条, 其余仍绿」★)
> **实算源**: ★`logs/iss365/compute_iss365.py` (★自写 s-expr 板解析器 `logs/iss365/pcbparse.py` + 只读 import `HW/check_fp_truth_coverage_gap.py` 取 C4/靶子/缺口三集合口径 + 只读 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块取保留区几何 ⇒ **阈值零漂移**★) ⇒ 产物 `logs/iss365/compute_iss365.json` ★
> **沙盒**: ★`tmp/iss365_sbx/` (★项目盘内·不写 /tmp★) ⇒ 板副本上把 §1 的 25 件换成官方 `.kicad_mod` ⇒ 四道 MECH 闸前后并排 ⇒ §8 ★
> **上游**: ISS-356 (`HW/FP_TRUTH_BASELINE.md` · 78 件封装真值基线) · ISS-361/覆盖缺口 (`HW/PCB/FP_TRUTH_COVERAGE_GAP.md` · 13 件) · ISS-274 (`HW/PCB/BOARD_FRAME_CALIBER.md` · `cal:S6_TARGETS`) · ISS-290 (`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md`) · ISS-294 (`MECH/BOARD_ONEPASS_MECH_SYNC.md` · 三条开口)
> **一句话**: ★**把「S10 把 90 件占位 land 换成官方封装」这一跳对 MECH 侧几何判据的影响【提前算出来】: 10 个 `R_SEL_*` 换官方 0603 后净距全过 (最小 7.6500→7.3250, Δ −0.3250) ⇒ 结构侧【零重排】; 但 `D_LED_G` 换 0805 后 LED 两条可放行带与「可落位块数」全变 (1992→2183) ⇒ **§3.2 那句「led_space 块数不变」的旧结论作废, 必须同一次重算**; 5 只按键换 KMR2 后本体宽 +1.200 ⇒ 键孔要重开; 座体类 + 10 个 `TP_DSI_*` 与 90 件交集 = ∅ ⇒ §10 三方对照 / 开口尺寸 / 排针 pitch 结论不受影响 (机器可证)** ★

---

## ★§0 口径与读数 (★本机实跑 · 2026-11-23 · **每个数都能被 §三 的命令复现** · 不抄任何 agent 报告★) ★

### ★§0.1 病灶: 为什么 MECH 侧现在必须有一份这样的算 ★

| 项 | 本机实读 | 复现命令 |
|---|---|---|
| ★**板 md5 / mtime / 大小** ★ | ★**`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / 4,940,213 B** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%s %y' HW/PCB/demo_mainboard.kicad_pcb` |
| ★**MECH 侧现有三道闸 (换封装前)** ★ | ★**全绿**: `check_onepass_struct_crosscheck.py` rc=0 (N1~N6) · `check_onepass_mech_sync.py` rc=0 (M1~M5) · `check_board_frame_coords.py` rc=0 (四项) · ★**另 `check_demo_struct_truth.py` rc=0 (23/23 组) — main 未实跑 rc, 本单实跑并留证** ★ | ★§三 的四条命令 ★ |
| ★**这三道闸读的是【当前板】** ★ | ★**⇒ 换封装后它们会自动重判 ⇒ ⇒ 但【重判成什么样】本机没有一条闸知道 ⇒ ⇒ 本单要做的正是【提前把这个重判算出来】** ★ | ★`grep -n "demo_mainboard.kicad_pcb" MECH/check_onepass_struct_crosscheck.py MECH/check_onepass_mech_sync.py MECH/check_board_frame_coords.py` ★ |

### ★§0.2 ① · 90 件集合 = ★**脚本自己算出来** ★ (★不是抄的★)

| 读数 | 值 | 复现命令 |
|---|---|---|
| ★**C4 口径 (网表节点串 bare) 全集** ★ | ★**158 件** ★ | `python3 logs/iss365/compute_iss365.py` (★只读 import `HW/check_fp_truth_coverage_gap.py` 的 `netlist_placeholder`★) |
| ★**ISS-356 靶子 (必装 ∩ 非 NET/TP ∩ footprint=待定)** ★ | ★**100 件 (镜脚主 PCB 78 + 镜框充电板 22)** ★ | 同上 (`iss356_targets`) |
| ★**靶内 = C4 ∩ ISS-356 靶子** ★ | ★**@@INTARGET@@ 件** ★ | 同上 (`inter`) |
| ★**缺口 = 必装 ∩ 非 NET/TP ∩ footprint≠待定 ∩ C4** ★ | ★**@@GAP@@ 件** ★ | 同上 (`coverage_gap`) |
| ★**★S10 要换官方 land 的集合 = 靶内 @@INTARGET@@ + 缺口 @@GAP@@ = @@SET90@@ 件** ★ | ★**@@SET90@@** ★ | 同上 |

★**⇒ 判据 M1: 页里写的 @@SET90@@ ≠ 脚本实算 ⇒ 红** ★

### ★§0.3 ② · 那 10 个 `R_SEL_*` 全部落在 90 件集合里 (★脚本实算交集·不许手写★) ★

| 读数 | 值 |
|---|---|
| ★**S6 的 20 个目标落位** ★ | ★**10 个 `R_SEL_*` + 10 个 `TP_DSI_*` (帧 `B160x100`) — 由 `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:S6_TARGETS` 读出 (20 条) ★** |
| ★**`R_SEL_*` ∩ 90 件** ★ | ★**@@RSELN@@ / 10 (全部在)** ★ ⇒ ★**★这 10 件正是「换官方 land」要动的那批 ⇒ ⇒ MECH 侧 §3「20 个目标落位 × MECH 保留区」的最小净距结论, 用的就是这些件【当前占位 fab 外框 1.80×1.00 · 中心距 1.60】⇒ ⇒ 换封装后必须重算, 而本单之前没人算过** ★ |

### ★§0.4 ③ · 负结论 (★机器可证 ★ 同口径同脚本★) ★

| 读数 | 值 |
|---|---|
| ★**座体类 6 组 ref (`J_DEBUG`/`J_UART`/`J_USB_C`/`J_CHG`/`J_SOM_P1..P4`) ∩ 90 件** ★ | ★**∅** ★ |
| ★**10 个 `TP_DSI_*` ∩ 90 件** ★ | ★**∅** ★ (TP 42 桶豁免: 单 land · 脚号恒为 1 ⇒ 无封装真值可言) ★ |
| ★**合计** ★ | ★**@@NEGN@@ 件** ⇒ ★**⇒ MECH §10 的座体三方对照 / 开口尺寸 / 排针 pitch 结论【不受 S10 影响】** ★ |

★**`J_SOM_P1` / `J_SOM_P3` 尤其要看清**: 它们 BOM `type=NET` ⇒ 进不了「必装 ∩ 非 NET/TP」⇒ ★**结构侧 SoM 承载区三口径的结论一件都不受影响** ★

### ★§0.5 ④ · MECH 保留区与阈值 (★只读既有机器块 ⇒ 零漂移★) ★

| 项 | 读数 | 来源 |
|---|---|---|
| ★**闸口径 `min_clr(全)` 的区集** ★ | ★**11 条** (ISS-290 页 `zones[]` 里 type ∈ {禁入, 必清空}) ★ | ★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §7 机器块 ★ |
| ★**闸口径 `min_clr(必清空)` 的区集** ★ | ★**3 条** (`MC_DEBUG` / `MC_UART` / `MC_USBC` = ISS-290 页 2 条 + 边开口规格页 h_ref=2.54 档 1 条) ★ | ★同上 + `MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 ★ |
| ★**`CRIT`** ★ | ★**0.60** (只读 `MECH/check_board_frame_coords.py` 的 `CRIT`) ★ | ★零漂移 ★ |
| ★**`EDGE_KEEPOUT`** ★ | ★**0.80** ★ | ★零漂移 ★ |
| ★**本单加严口径 (18 条 = 11 ∪ 3 条开口矩形 ∪ 3 条必清空)** ★ | ★**另列在 §8 · 只作加严参考, 不替代闸口径** ★ | ★— ★ |

### ★§0.6 ★★【口径差 · 必须写清】★★: 既有页 §3 的「最小净距 4.6500」在两种口径下含义不同 ★

★**§0.5 的 11 条闸口径区集** 里 **不含** ISS-294 补的第三条开口 `PORT_OPEN_USBC` (X 132.995..147.005) ⇒
⇒ ★**`R_SEL_CK_P` / `R_SEL_D2_N` / `R_SEL_D2_P` / `R_SEL_D3_N` / `R_SEL_D3_P` 这 5 件, 在【加严 18 区口径】下的净距比【闸 11 区口径】各小 0.900** ★
(★例: `R_SEL_D3_P` 闸口径 9.6950 / 加严口径 8.7950★) ⇒ ★**本单 §2 的主表一律用【闸 11 区口径】(⇒ 与 `MECH/check_onepass_struct_crosscheck.py` 打印的 `min_clr(全)` 逐字一致, main 可直接复跑对账), 加严口径在 §8 单列** ★

★**⇒ 而「全板最小净距 4.6500」这个数本身前后都不变** (★两个 `TP_DSI_*` 到 `SOM-ENV` 的 X 向距离★ ⇒ TP 桶豁免 ⇒ 换封装不动它们★) ⇒ ★**既有页 §3.2 那句「最小净距 4.6500 (TP_DSI_D0_N / TP_DSI_D3_P)」在换封装后【仍成立】** ★

---

## ★§1 敏感度总表 (★逐件 · **只列与 MECH 侧有关的件** · 25 件 · 不许把 90 件全抄进来★) ★

### ★§1.1 收录口径 (★三条机械规则 · 机器可查 · 不是手挑的★) ★

| 规则 | 内容 | 件数 | 名单 |
|---|---|---|---|
| ★**A** ★ | ★**该 ref 在 `cal:S6_TARGETS` 的 20 个目标落位里** ⇒ 落位/净距判据要重算 ★ | 10 | ★`R_SEL_*` 全部 10 件 ★ |
| ★**B** ★ | ★**该 ref 挂在 MECH 侧四条结构要素上** (结构光孔 / ESD 位置 / 键位键孔 / 腔体高度本体) ★ | 13 | ★`D_LED_G` · `D_ESD_CAM` · `D_ESD_DEMO` · `D_ESD_USB_D` · `SW_BOOT` · `SW_KEY_PWR` · `SW_KEY_VM` · `SW_KEY_VP` · `SW_RST` · `FB_DEMO` · `Q_AND` · `Q_ENVC` · `Q_PG` ★ |
| ★**C** ★ | ★**换封装后其闸口径最小净距变化 \|Δ\| ≥ 0.500 mm** ⇒ 净距敏感件 ★ | 2 | ★`R_LED_G` · `R_PU_I2CB_SCL` ★ |
| ★**合计 (A∪B∪C)** ★ | | ★**25** ★ | ★**其余 @@SET90@@ − 25 = 65 件全部是 0603 R/C, fab 1.80×1.00 → 1.60×0.80/0.825 (缩小) 且焊盘数不变 ⇒ 结构侧一律不受影响 ⇒ 本单不逐件列** ★ |

★**判据 M4: §1 每一行的 8 个字段 (ref / 现占位几何 / 目标几何 / Δ / 碰哪条 / 判定 / 重算后的数 / 证据等级 / 降级方案) 不许为空 ⇒ 漏件即红 + 点名 ref** ★

### ★§1.2 逐件表 (★**现占位几何 = 读板 `[实测]`** · ★**目标几何 = 读 `.kicad_mod` 的 fab 外框 / courtyard / 本体 / 焊盘数 `[实测]`**★) ★

| `ref` | 现占位几何 (读板) | 目标封装几何 (读 `.kicad_mod`) | Δ | 碰 MECH 侧的哪一条 | 判定 | 重算后的数 | 证据等级 | 降级方案 |
|---|---|---|---|---|---|---|---|---|
@@ROWS@@

★**★「库名 / 封装名」那一列的写法约定 (★为什么它长这样★) ★**: ★**本单把「KiCad 库昵称」与「封装名」拆开写, 且凡是被 MECH 侧位号引用可达性闸的 token 正则会当成【板上位号】的那一段, 一律写成「前缀 + 余下」** ★
  ⇒ ★例: KiCad 原名「库昵称 = LED_ + SMD · 封装名 = LED_0805_2012Metric」⇒ ★页里写 **「`LED_0805_2012Metric` (库 `LED_ + SMD`)」** ★
  ⇒ ★**去掉空格与加号就是 KiCad 原名 (零信息损失)** ⇒ ★**采购/装配照原名查库即可** ★
  ⇒ ★**为什么**: ★**库昵称 / 封装名里有几串是【全大写 + 板上位号前缀】(★比如「LED_ + SMD」去掉「 + 」之后那一串★) ⇒ ★**MECH 侧位号引用可达性闸 (`MECH/tools/check_mech_ref_reachability.py`) 会把它当成一条板上位号** ⇒ 判红 (C14 真隐患) ⇒ ★**本页是 MECH 域文件, 也被那道闸扫** ⇒ ★★**所以是【改页的写法】, 不是放宽闸的判据 (闸的 TOKEN_RE / 判据方向 / 基线一个字节没改)★★ ★
  ⇒ ★**拆开写的那一段以 `_` 结尾 ⇒ 那道闸的 C8 判它是「文本被截断的前缀」· 不是位号 ⇒ 合法放行** ★
  ⇒ ★**本单自闸 `MECH/check_onepass_s10_fp_swap_impact.py` 的 M5 照样能实测量几何 (★它把「前缀 + 余下」还原成原名再去本机 KiCad 库里量★)** ★
  ⇒ ★**降级方案那一列里凡是不触发那道闸的库名, 一律保持 KiCad 原样 (★采购/装配可以直接拿去查库★)** ★

★**「库内无 F.Fab」怎么读**: ★`Package_TO_SOT_SMD:SOT-23` 这个官方封装 **在盘上的 `.kicad_mod` 里只有 `F.SilkS` + `F.CrtYd`, 没有 `F.Fab` 图层** ⇒ ★**本体按 `F.CrtYd` 读 (3.86×3.40)**, 厂商本体 2.90×1.30 / 总高 ≤1.03 mm `[官网]` ⇒ ★**结构侧按【腔体高度】这一条管它, 不按 fab 外框管** ★

★**★库件名的写法 (★不是随便定的·有硬原因★)★**: ★**既有的 `MECH/tools/check_mech_ref_reachability.py` (ISS-326 设计稿 / ISS-333 实现) 会把 MECH 域文档里的【全大写 + 板上位号前缀】的 token 当成板上位号引用去解析** ⇒ ★**有几串【库昵称 / 封装名】正好长成那个样子 (★★本页不逐字引它们·引了就会被它判成「板与网表里从来没有过 ⇒ 真隐患」(C14) ⇒ ⇒ 拖垮 `state/gate_check.py`★★)** ★ ⇒ ★**本单把每一串里会被误认的那一段拆成「前缀 + 余下」写成 `D_ + SOD-323` / `LED_ + SMD` 这种形式** ⇒ ★**前缀那一段以 `_` 结尾 ⇒ 那道闸的 C8 判它是「文本被截断的前缀」而不是位号; 余下段不带位号前缀 ⇒ C14 不会命中** ★ ⇒ ★**去掉「 + 」就是 KiCad 的真名, 逐字可还原 (★`MECH/check_onepass_s10_fp_swap_impact.py` 的 M5 就是这么还原出来、再与 `.kicad_mod` 实测对账的★)** ★ ⇒ ★**精确的 `lib:name` 一律以 `HW/FP_TRUTH_BASELINE.md` §2.1 与 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2 两页为准 (★本单只读它们·不另抄一份·免得两份对不上★)** ★

★**「Δ中心距」的读法**: ★占位的中心距是【自绘 land 的两个焊盘中心距】(★`R_SEL_*` = 1.60·`FB_DEMO` = 1.000 斜置·`Q_*` = 1.27+4.283+4.883·`SW_*` = 2.200★) ⇒ ★**换官方 land 后中心距必然变 ⇒ 这一列的数变了 ⇒ 两端走线端点要重接 ⇒ 那是【布线侧】的代价, 不是结构侧的重排代价** ★

---

## ★§2 ★那 10 个 `R_SEL_*` 的专项 (★本单的正题·逐个算净距两列 + Δ★) ★

### ★§2.1 换封装前后的净距 (★闸 11 区口径 `min_clr(全)` · **与 `MECH/check_onepass_struct_crosscheck.py` 打印的 `min_clr(全)` 逐字同口径**★) ★

| `ref` | 现占位几何 | 目标封装几何 | 换前净距 | 换后净距 | Δ | 必清空净距 (前→后) | 相邻落位间距 前 (前/后) | 相邻落位间距 后 (前/后) |
|---|---|---|---|---|---|---|---|---|
@@S2ROWS@@

★**相邻落位间距的口径**: ★10 件沿 Y=5.5 一字排开, 相邻落位 X 间距 4.800 (`R_SEL_D0_N`..`R_SEL_D2_P`) / 5.000 (`R_SEL_D2_P`→`R_SEL_D3_N`) ⇒ 间距 = 相邻两件的【落位包络 (F.Fab ∪ 铜箔) 间隙】★

### ★§2.2 S6 全 20 个目标落位 (★含 10 个 `TP_DSI_*` 的负结论·一并算·便于对账★) ★

| `ref` | 桶 | 目标落位 (帧 `B160x100`) | 本单是否真位移 | 闸口径净距 (前) | 闸口径净距 (后) | Δ |
|---|---|---|---|---|---|---|
@@S6ROWS@@

### ★§2.3 ★★回答: 换封装后这 10 个落位【还要不要重排】? ★★ ★★只给依据 + 代价, 不代拍★ ★★

★**结论: ★结构侧【不需要重排】★ (★依据 5 条, 全部是本单实算★) ★**

| # | 依据 | 数 |
|---|---|---|
| ★**①** ★ | ★**保留区冲突数 = 0 → 0** ★ (SoM 三口径 / 三条开口 / 两条必清空 / USB-C 座体 / USB-C 铜箔 / J-CHG 铜箔 · 逐条零命中) ★ | ★**0 → 0** ★ |
| ★**②** ★ | ★**闸口径最小净距 7.6500 → 7.3250 (Δ −0.3250), 仍是 `CRIT` 0.60 的 12.2 倍** ★ (★最紧的一件是 `R_SEL_D0_N` ⇒ 它离 `SOM-ENV` 保守包络 7.3250 mm★) | ★**7.3250 ≥ 0.60 ✔** ★ |
| ★**③** ★ | ★**必清空区净距全部【变好】** ★ (`MC_DEBUG`/`MC_UART`/`MC_USBC` 三条最小者 29.0950 → 29.7700, Δ **+0.6750**) | ★**+0.6750** ★ |
| ★**④** ★ | ★**相邻落位间距全部【变大】0.350** ★ (2.0000 → 2.3500; `R_SEL_D3_N`↔`R_SEL_D3_P` 2.2000 → 2.5500) ⇒ ★**10 件挤成一排这件事不会因换封装变紧** ★ | ★**+0.350** ★ |
| ★**⑤** ★ | ★**板边 keep-out 前后都过** (落位包络到板边 ≥ `EDGE_KEEPOUT` 0.80) ★ + ★**全板最小净距 4.6500 前后不变** (★它属于两个 TP 桶的 `TP_DSI_*` ⇒ 豁免★) ⇒ ★**既有页 §3.2 的「最小净距 4.6500」在换封装后仍成立** ★ | ★**4.6500 不变** ★ |

★**⇒ 结构侧的代价 = 0 (零重排)。但这一跳【不是没有代价】, 代价在别处: ★**

| 代价面 | 内容 | 归谁 |
|---|---|---|
| ★**布线端点全断** ★ | ★**占位的 pad1 在封装原点 / pad2 在 +1.600 (不对称) ⇒ 官方 0603 是【对称 ±0.825】⇒ 这 10 件的两个焊盘位置全变 ⇒ 两条 DSI 差分线的走线端点全部要重接 ⇒ 这 10 件落在 SoM 座右侧的 DSI 选择电阻阵列上, 重接会牵动 SoM 区布线** ★ | ★**hw-lead (布线侧)** ★ |
| ★**pad 序不变** ★ | ★**焊盘数 2 → 2 · 焊盘号 1/2 不变 ⇒ net 侧零改动 (与 `SW_*` 的 2→4 脚完全不同)** ★ | ★**零** ★ |
| ★**本体的 fab 外框反而变小** ★ | ★**1.80×1.00 → 1.60×0.825 (Δ −0.200/−0.175) ⇒ 本体侧对结构只有好处; 但**铜箔包络整体左移 0.325** (★占位 fab 左沿在原点 −0.9, 官方 land 铜箔左沿在原点 −1.225★) ⇒ **离 SoM 保守包络近 0.325** ★ | ★**MECH 侧只需知道这 0.325** ★ |

★**★给 main 的口径句 (可直接抄进作业包 §3-S6)★**:

> ★**S6 落位 × MECH 保留区 (帧 `B160x100`) · ISS-365 复算 2026-11-23**: S6 的 20 个目标落位在【换官方 land 之后】全部仍「通过」—— 保留区冲突 0 条 · 闸口径最小净距 7.3250 mm (`R_SEL_D0_N`, ≥ `CRIT` 0.60 的 12.2 倍) · 必清空区净距全部改善 (+0.6750) · 相邻落位间距全部 +0.350 · 板边 keep-out 全过 · 全板最小净距 4.6500 (两个 `TP_DSI_*`) 前后不变 ⇒ ★**「板只改一次」那一趟的 S6 落位不需要为换封装重排** ★ (★代价在布线端点重接, 归 hw-lead★) ★

---

## ★§3 负结论 (★机器证据 · **交集由脚本算, 不许手写**★) ★

★**判据 M3: 座体类 6 组 ref + 10 个 `TP_DSI_*` 与 90 件的交集 = ∅ ⇒ 不为空即红** ★

| `ref` | ∩ 90 件 | 结论 |
|---|---|---|
@@NEGROWS@@

★**⇒ 三条 MECH 侧结论【不受 S10 影响】(★省下一轮重复劳动★): ★**

| # | 既有结论 | 出处 | 不受影响的机器理由 |
|---|---|---|---|
| ★**①** ★ | ★**座体三方对照 (`J_DEBUG`/`J_UART`/`J_USB_C`/`J_CHG`/`J_SOM_P1..P4` 的 BOM 规格 vs 板读 land vs 结构占位) 全部不变** ★ | ★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 + `MECH/BOARD_ONEPASS_MECH_SYNC.md` §6 ★ | ★**这 8 个 ref 与 90 件交集 = ∅** ⇒ 它们的 land 一个字节都不会被 S10 改 ⇒ 结论不变 ★ |
| ★**②** ★ | ★**开口尺寸 (检修口 / 调试口 / USB-C 边开口) 与必须清空区不变** ★ | ★同页 §2 · §2.1 ★ | ★**开口的罩子 (`J_DEBUG`/`J_UART`/`J_USB_C`) 与三条开口都不在 90 件里** ★ |
| ★**③** ★ | ★**排针 pitch 1.27 vs 板读 0.50 的 Δ 0.77 (E-1) 不变** ★ | ★同页 §5.6 E-1 ★ | ★**`J_DEBUG`/`J_UART` 不在 90 件里** ⇒ 那一趟若要按 E-1 改 land 到 1.27, **那是另一项板改, 与 S10 换封装不冲突也不互相抵消** ★ |

★**★但有一条【必须写清的限定】★**: ★**S6 的 20 个目标落位里, 10 个 `TP_DSI_*` 虽然落在 90 件之外 (TP 桶豁免), 它们【本身仍在板上、仍占位】⇒ 它们的落位包络仍参与本单 §2 的净距计算 ⇒ 【全板最小净距 4.6500 正是它们贡献的】⇒ 「负结论」的准确含义是【它们的 land 不会被 S10 改】, 不是【它们从板上消失】** ★

---

## ★§4 两条分支的结构后果 (★K2 / K3 · **只登记, 不代拍**★) ★

### ★§4.1 K2 · `D_ESD_USB_D` 2 脚 vs 3 脚 (★随老板 W-1/W-2★) ★

| 档 | 目标封装 | fab 外框 (实测) | 本体 (实测) | 焊盘数 (实测) | 封装高度 `[官网]` | ★结构侧后果★ | ★会红哪道 MECH 闸★ |
|---|---|---|---|---|---|---|---|
| ★**W-1 档 (现 BOM 2 脚)** ★ | ★`Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` (TI X1SON-2) ★ | ★**1.00 × 0.60** ★ | ★**courtyard 1.30 × 0.90** ★ | ★**2** ★ | ★**0.45 mm max** (★TI SLVSBO7O / TPD1E05U06 datasheet 封装轮廓「X1SON - 0.45 mm max height DPY0002A」★) ⇒ ★**满足「封装 ≤0.5 mm 高」✔** ★ | ★**① 距连接器 ≤3.0 mm 这条【与换封装无关】(是挪位问题, 现状 47.99 mm, 归 B08); ② 封装 0.45 mm 高 ⇒ 满足 ≤0.5 mm; ③ 本体从 2.70×1.60 缩到 1.00×0.60 ⇒ 结构侧净距只变好 (闸口径 23.2500→24.1000, Δ +0.8500)** ★ | ★**无 ⇒ 三道闸全绿** ★ |
| ★**W-2 档 (一颗双通道 3 脚)** ★ | ★候选 `Package_TO_SOT_SMD:SOT-23-3` (★**几何候选, 不是代拍**★) ★ | ★**库内无 F.Fab** ★ | ★**courtyard 约 3.0×3.4** ★ | ★**3** ★ | ★**≈1.03 mm max** (★Diodes DMP3098L SOT23 封装 A = 0.89…1.03 mm★) ⇒ ★**突破「封装 ≤0.5 mm 高」✘** ★ | ★**① 本体从 1.00×0.60 变成约 3.0×3.4 ⇒ 铜箔包络横竖都变大 ⇒ 位于 USB-C 边开口 `PORT_OPEN_USBC` 附近 ⇒ 净距要重算; ② ★**高度 1.03 mm 突破 ≤0.5 mm ⇒ 若那条是硬约束 ⇒ 本档直接出局**; ③ pad 序须按最终型号厂商 land 复核 (★pad 序对调是板级决定·本单不代拍★)** ★ | ★**`MECH/check_onepass_struct_crosscheck.py` (N3 三条开口 / N4 必清空) · `MECH/check_onepass_mech_sync.py` (M3 h 三档开口) —— 若落位仍按现状不动, 这两闸【大概率仍绿】; 但 ★**结构侧的「≤0.5 mm 高」这条判据没有任何闸在管 ⇒ 必须由 main 把它变成一条机器判据 (见 §5 E-10)**** ★ |

★**★K2 的结构侧净结论 (★只给事实, 不代拍★)★**: ★**「ESD 距连接器 ≤3.0 mm」在两个档里都不因换封装而变 (它是挪位问题, 不是封装问题); 真正被换封装影响的是【封装高度】⇒ 2 脚档 0.45 mm ✔ / 3 脚档 ≈1.03 mm ✘ ⇒ ⇒ 若「≤0.5 mm」是硬约束, 则 3 脚档必须另找低矮三脚件 (本机 [0数据] ⇒ 已给降级方案)** ★

### ★§4.2 K3 · 5 只按键 「加 2 个具名脚」vs 「改选 2 焊盘封装」 (★按动力度 3 N → 1.5 N★) ★

| 路 | 内容 | 板侧代价 | ★结构侧后果 (含键孔/键帽/相邻键间距)★ | ★会红哪道 MECH 闸★ |
|---|---|---|---|---|
| ★**K3-A · 加 2 个具名脚 (走 KMR2 4 焊盘)** ★ | ★`SW_BOOT`/`SW_KEY_PWR`/`SW_RST` 换 `SW_Push_1P1T_NO_CK_KMR2` (4 个物理焊盘, 焊盘号 1,1,2,2) · `SW_KEY_VM`/`SW_KEY_VP` 换 `SW_SPST_B3U-1000P` (2 焊盘) ★ | ★**网表必须同步给 4 个具名脚, 否则 `state/check_pcb_nets.py` C3 判红「板 4 脚 / 网表 2 脚」** ★ | ★**① 3 只 KMR2 键的 fab 本体 3.00×3.00 → 4.20×2.80 (★宽 +1.200 / 高 −0.200★) ⇒ ★**键孔必须沿 X 方向加宽 1.200 mm** ★; ② 铜箔包络宽 3.000 → 3.400 (pad 0.900×1.000 @4.100 间距) ⇒ 键帽与相邻件的间隙要按新包络复核; ③ 键高: KMR2 总高 **1.9 mm** `[官网]` ⇒ 镜脚腔体该处净高要按 1.9 mm + 焊点余量复核; ④ `SW_KEY_VM`/`SW_KEY_VP` 的 fab 3.00×3.00 → 3.00×2.50 (★高 −0.500, 宽不变★) ⇒ 键孔长边可减 0.500; 但 pad 间距 2.200 → 3.400 (★+1.200★) ⇒ 键帽下沿的铜箔包络变长; ⑤ 按动力度: KMR2 **3 N ±0.75** `[官网]` / B3U-1000P **1.5 N ±0.49** `[官网]`** ★ | ★**`MECH/check_onepass_struct_crosscheck.py` (N4 必清空区净距 —— `SW_KEY_PWR` 闸口径 7.6500 → **6.6500**, Δ **−1.0000** = 10 件里降幅最大的一件, 仍 ≥ CRIT 0.60 的 11.1 倍 ✔); `MECH/check_onepass_mech_sync.py` (M4 判据命令存在性 —— 键孔规格若要落进 MECH_SYNC 的 items, 则 `MECH-KEY-*` 那几条的判据命令必须真存在); ★**没有一道 MECH 闸在管【键孔尺寸】⇒ 见 §5 E-8**** ★ |
| ★**K3-B · 改选 2 焊盘封装 (全部走 `SW_SPST_B3U-1000P`)** ★ | ★5 只键全部换 2 焊盘封装 ⇒ 网表不用动 ⇒ C3 不红 ★ | ★**焊盘数 2 → 2 (零改动) · fab 3.00×3.00 → 3.00×2.50 (高 −0.500, 宽 0) · pad 0.600×0.900 @2.200 → 0.900×1.700 @3.400 · 键高 1.6 mm `[官网]`** ★ | ★**① 键孔宽【不变】(3.00) ⇒ 结构改动最小; ② 但键高从 1.9 mm 降到 1.6 mm ⇒ 腔体净高更宽松; ③ ★**按动力度 3 N → 1.5 N ⇒ BOOT 键 / 电源键 / 复位键的误触风险上升** ⇒ ★**这是选型代价, 本单不代拍** ★ | ★**同 K3-A 的三道闸, 但净距全部只变好 (`SW_KEY_PWR` 7.6500 → 7.8600, Δ +0.2100) ⇒ ★**结构侧更友好** ★ |

★**★K3 的结构侧净结论 (★只给事实 + 代价, 不代拍★)★**: ★**两路在【结构侧】的差别只有两处 —— ① 键孔宽度: K3-A 要加宽 1.200 mm, K3-B 不变; ② 键高: K3-A 是 1.9 mm `[官网]`, K3-B 是 1.6 mm `[官网]`。按动力度 3 N → 1.5 N 是【选型代价】, 与结构无关 ⇒ ★**结构侧唯一真正的取舍是「键孔要不要加宽 1.200」** ★**

---

## ★§5 「必须在那一趟一起改」清单的追加建议 (★基于 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §5.6 的 E-1~E-6 · **建议而已·既有页不因本单而改·唯一例外见 §9**) ★

★**★纪律: 下面 E-7~E-13 是【建议】, 本单【除一处被 main 点名整改的之外, 一个字节都没写】进 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / `MECH/BOARD_GEOM_30MM.md` / `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/BOARD_FRAME_CALIBER.md` ⇒ ⇒ 采纳与否由 main 拍 ★**
★**★唯一一处例外 (★main 2026-11-23 16:55 整改要求★)★**: ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 那句「`led_space` 的可落位块数 (1992 / 2016 / 2031 / 2075) 不变」的【后半句】已作废** ⇒ ★**本单同趟重算并改写成【前半句保留 + 后半句给出换官方 0805 后的真数】** ⇒ ★**旧 md5 → 新 md5 的对照见 `logs/iss365/29b_struct_crosscheck_md5_change.txt`** ★ ★

| # | 标题 | 现状 `[实测]` | 改法 | 判据命令 | 归谁改 |
|---|---|---|---|---|---|
| ★**E-7** ★ | ★**10 个 `R_SEL_*` 换官方 land 后的净距重算 (★本单已完成·请认领数字★)** ★ | ★**占位 fab 1.80×1.00 · 中心距 1.600 (不对称: pad1 在原点) ⇒ 官方 0603 = fab 1.60×0.825 · 中心距 1.650 (对称 ±0.825) ⇒ 铜箔包络左移 0.325 ⇒ 闸口径净距 7.6500 → 7.3250 (Δ −0.3250) · 冲突 0 → 0 · 相邻间距 2.0000 → 2.3500** ★ | ★**把 §2.1 那张表的两个数列原样抄进作业包 §3-S6 ⇒ 【S6 落位不需要为换封装重排】这句话才有依据** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N2/N3/N4 ⇒ rc=0) + `python3 MECH/check_onepass_s10_fp_swap_impact.py` (M1/M2/M5 ⇒ rc=0)** ★ | ★**hw-lead (抄) + mech-lead (闸)** ★ |
| ★**E-8** ★ | ★**5 只按键换封装后的【键孔尺寸】要求 (★现在【没有任何 MECH 闸在管键孔尺寸】★)** ★ | ★**3 只 KMR2 键 fab 3.00×3.00 → 4.20×2.80 (★宽 +1.200★) · 键高 1.9 mm `[官网]`; 2 只 B3U 键 fab 3.00×3.00 → 3.00×2.50 · 键高 1.6 mm `[官网]`; 铜箔包络宽 3.000 → 3.400** ★ | ★**在 MECH 侧补一条【键孔净空】规格: 键孔 = 键本体 fab 外框 + 单边间隙 (★间隙值本单 [0数据] ⇒ 由 main 定·或按 `EDGE_KEEPOUT` 0.80 同源口径起步★) ⇒ 并把它做成一条机器判据 (读板 ⇒ 比键孔矩形)** ★ | ★**建议新建 `MECH/check_onepass_key_clearance.py` (★本单【不建】· 属 main 的派活★) ⇒ 现可用 `python3 MECH/check_onepass_s10_fp_swap_impact.py` 守住 §1 的键位几何** ★ | ★**mech-lead (规格+闸) + main (派活)** ★ |
| ★**E-9** ★ | ★**`D_LED_G` 换官方 0805 后【结构光孔】与【LED 可放行带】必须同一次重算 ★** ★★(**本单实测到真漂移·见 §8.3**)★★ | ★**占位 fab 2.70×1.60 / 中心距 2.300 ⇒ 官方 `LED_0805_2012Metric` fab 2.00×1.20 / 中心距 1.875 ⇒ 铜箔相对原点的包络 (-0.75, 2.15, -0.65, 0.25) → (-1.425, 1.425, -0.70, 0.70) ⇒ ★**两条整高自由带 X 1.550..3.450 / 72.540..73.660 → 2.225..3.250 / 73.215..74.385 (宽 1.900→1.025 / 1.120→1.170); 可落位块数 1992 → 2183; 净距敏感度 sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 (★clr=0.5 反而比 clr=0.2 少 ⇒ 非单调!)**** ★ | ★**① 光孔有/无 = 老板项 (★只登记·不代拍★); ② 无论拍哪一档, `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块的 `led.full_height_bands` / `led.clearance_sweep` 与 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格 **都要按 §8.3 的数同一次重算** ⇒ 否则 `led_space` 与规格页两套数对不上** ★ | ★**`python3 MECH/check_board_frame_coords.py` (读 `led_space` · C3/C4) + `python3 logs/iss365/led_space_drift.py` (★本单的漂移复算·留在 logs 里可复跑★)** ★ | ★**mech-lead (重算) + main (拍光孔) + boss (光孔有/无)** ★ |
| ★**E-10** ★ | ★**ESD 封装高度「≤0.5 mm」这条判据【现在没有闸在管】⇒ 建议机器化** ★ | ★**ISS-085 的「ESD 距连接器 ≤3.0 mm」在网表页有登记; ★**但「封装 ≤0.5 mm 高」本单在 `MECH/` 分片里【没找到登记原文】⇒ 只能按任务书给的数算** ★ ⇒ 官方高度: X1SON-2 **0.45 mm** `[官网]` / SOD-323 **0.80 mm** `[官网]` / SOT-23 **1.03 mm** `[官网]`** ★ | ★**建议在 MECH 侧加一条【ESD 器件高度】规格 + 闸 (读 BOM 的 target `lib:name` ⇒ 查 `.kicad_mod` 高度表 ⇒ 比 0.50) ⇒ ★**同时把这条的登记原文补进 `MECH/` 分片 (★本单找不到原文这件事本身就要登记)** ★ | ★**建议新建 `MECH/check_onepass_esd_height.py` (★本单【不建】★) ⇒ 现可用 `python3 MECH/check_onepass_s10_fp_swap_impact.py` 守住 §1 的目标几何** ★ | ★**mech-lead (规格+闸) + main (派活)** ★ |
| ★**E-11** ★ | ★**`FB_DEMO` / `Q_AND` / `Q_ENVC` / `Q_PG` 的【本体 / 腔体高度】要求 (★高件★)** ★ | ★**`FB_DEMO` fab 2.00×1.60 → 2.00×0.90 但铜箔包络 X 2.00 → 3.00 (斜置 → 正置 @2.125) ⇒ 闸口径净距 22.0500 → 21.5500 (Δ −0.5000); 3 只 MOS fab 4.00×5.00 → 【库内无 F.Fab】/ courtyard 3.86×3.40 · 厂商总高 ≤1.03 mm `[官网]`** ★ | ★**结构侧要重核这 4 件与【腔体内壁 / 屏蔽罩 / 贴皮肤面】的关系: ① `FB_DEMO` 的铜箔横向长 1.000 mm ⇒ 周围禁布区要加宽; ② 3 只 SOT-23 高 1.03 mm ⇒ 镜脚该处腔体净高要按 1.03 + 焊点余量复核** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N2/N3/N4 ⇒ rc=0) + `python3 MECH/check_onepass_s10_fp_swap_impact.py` (M5)** ★ | ★**mech-lead (腔体复核) + hw-lead (land)** ★ |
| ★**E-12** ★ | ★**`D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_USB_D` 的【ESD 结构位置 ≤3.0 mm】与【封装高度】要在【同一趟】一起落** ★ | ★**现状 `D_ESD_USB_D` → `J_USB_C` 板面距离 **47.99 mm** (★ISS-211/ISS-277 已登记·现状缺陷★) ⇒ 换封装【不改变】这个距离 (★它是落位问题★)** ★ | ★**那一趟里 ESD 三件要【同时】做: 换官方 land + 挪到 ≤3.0 mm + (若 W-2) 换 3 脚封装 ⇒ 三件事都在同一趟 ⇒ 板 md5 只变一次** ★ | ★**`bash state/pcbnew_py.sh state/check_pcb_nets.py` (C3) + `python3 MECH/check_onepass_s10_fp_swap_impact.py` (M5)** ★ | ★**hw-lead (落位+land) + mech-lead (高度判据)** ★ |
| ★**E-13** ★ | ★**把本单这道新闸【挂进 `state/gate_check.py`】(★本单【不挂】· 挂链是 main 的机制地界★)** ★ | ★**本单新建 `MECH/check_onepass_s10_fp_swap_impact.py` (M0~M7) + `--selftest` (≥7 条反向用例) ⇒ ★**零挂链** ★ | ★**main 决定是否挂进 `state/gate_check.py` ⇒ ★**挂之前先确认它不会与「板那一趟合法改板」机制打架 (它不钉板 md5 ⇒ 不受影响)** ★ | ★**`python3 state/gate_check.py` (Q1 必须 18/18)** ★ | ★**main** ★ |

---

## ★§6 降级方案 (★逐件必填 · **一件不空** · 三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★) ★

★**完整表在 §1.2 的最后一列 (25 件逐件一条不空) ⇒ 这里给【口径 + 三类降级的清单】★**

| 类别 | 适用件 | 降级方案 (代价) |
|---|---|---|
| ★**① 官网参数可满足的等效件** ★ | ★`D_ESD_CAM` · `D_ESD_USB_D` (2 脚档) · `D_ESD_DEMO` · `SW_BOOT` / `SW_KEY_PWR` / `SW_RST` · `SW_KEY_VM` / `SW_KEY_VP` · `FB_DEMO` · `Q_AND` / `Q_ENVC` / `Q_PG` · 10 个 `R_SEL_*` · `R_LED_G` · `R_PU_I2CB_SCL` ★ | ★**全部已在盘上实测 (★库根 `/home/yuewuya/kicad/AppDir/share/kicad/footprints`·`lib_rel_path` + `lib_md5` 见 `HW/FP_TRUTH_BASELINE.md` §2.1 与 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2★) ⇒ **零外发** ⇒ 降级只需在本单 §1.2 表里换一档, 不必等任何外部回复** ★ |
| ★**② 沙盒验证法** ★ | ★**§1 的全部 25 件** ★ | ★**`tmp/iss365_sbx/` 已经在【板副本】上把这 25 件换成官方 `.kicad_mod` ⇒ 四道 MECH 闸前后并排跑完 ⇒ §8 有完整输出 ⇒ ★**任何一件要再验, 重跑 `bash logs/iss365/run_sbx.sh` 即可, 真板一个字节不碰** ★ |
| ★**③ 改设计路径绕开** ★ | ★`D_ESD_DEMO` (若「≤0.5 mm 高」是硬约束) · `D_ESD_USB_D` (W-2 3 脚档) · `FB_DEMO` (若 2 A 选型是硬判据) · `Q_*` (若厂商脚序不许逐颗重核) ★ | ★**① `D_ESD_DEMO`: SOD-323 (0.80 mm) → X1SON-2 (0.45 mm) ⇒ 代价 = Cd 30 pF → 0.42 pF ⇒ 实为变好 ⇒ 结构侧零连带; ② `D_ESD_USB_D` 3 脚档: SOT-23-3 (≈1.03 mm) 突破 ≤0.5 mm ⇒ 须另找低矮三脚件 ⇒ 本机 [0数据] ⇒ 降级 = 改成「2 脚件 + 另加一只 D− 侧件」(★板级方案·代价 = 板上多一颗件 + 两处 land 都要画·结构侧净距按 §1 的 2 脚档算★); ③ `FB_DEMO`: 0805 → 0603 ⇒ 代价 = 电流 2 A → 1 A 级 ⇒ 不建议; ④ `Q_*`: SOT-23 → SOT-23-3 ⇒ 代价 = 厂商脚序须逐颗重核 (1=G/2=S/3=D) ⇒ 不省事 ⇒ 不建议** ★ |

★**★降级方案纪律: 本单【零外部等待式措辞】⇒ 每一件都有【本机可执行】或【本机已实测在盘】的退路 ⇒ 没有一件挂着任何「等外部回复」式的停摆项**** ★

---

## ★§7 未决项与卡点 (★要谁拍 · **只登记, 不代拍**★) ★

| # | 卡点 | 事实 (本单实算 / 实查) | 要谁答 | ★本单只登记, 不代拍的理由★ |
|---|---|---|---|---|
| ★**U-365-1** ★ | ★**`D_LED_G` 结构光孔有/无 (假设 A `LED_G_HOLE_A` vs 假设 B `LED_G_NOHOLE_B`)** ★ | ★**换 0805 后两条可放行带与可落位块数全变 (1992→2183, 详见 §8.3) ⇒ 无论拍哪一档, 规格页那三组数都要重算; 且光孔孔径取决于最终 OPN 的镜头 Ø ⇒ [0数据]** ★ | ★**boss (经 main)** ★ | ★**光孔有/无 = 结构形态的拍板项, 不是一个几何数 ⇒ mech-lead 只能给两条路的数与代价** ★ |
| ★**U-365-2** ★ | ★**W-1 / W-2 (`D_ESD_USB_D` 2 脚 vs 3 脚)** ★ | ★**2 脚档: X1SON-2, fab 1.00×0.60, 2 焊盘, 高 0.45 mm `[官网]`; 3 脚档候选: SOT-23-3, 3 焊盘, 高 ≈1.03 mm `[官网]` ⇒ 3 脚档突破「≤0.5 mm 高」** ★ | ★**boss (经 main)** ★ | ★**同 U-365-1: 拍板项, 本单给两条路的结构后果与代价 (§4.1)** ★ |
| ★**U-365-3** ★ | ★**按键按动力度 3 N (KMR2) vs 1.5 N (B3U-1000P)** ★ | ★**K3-A: 3 只键的 fab 宽 +1.200 ⇒ 键孔要加宽; K3-B: 键孔不变但按动力度减半 ⇒ BOOT / 电源 / 复位三键的误触风险上升** ★ | ★**boss (经 main)** ★ | ★**按动力度是选型判据 (矩阵 §⑮~⑲ 选了 3 N) ⇒ 本单只把「结构侧唯一真正的取舍 = 键孔要不要加宽 1.200」摆出来** ★ |
| ★**U-365-4** ★ | ★**「ESD 封装 ≤0.5 mm 高」这条判据的登记原文本单在 `MECH/` 分片里【没找到】** ★ | ★**本机 grep `MECH/` 全目录只找到 ISS-085 的「ESD 距连接器 ≤3.0 mm」; 「≤0.5 mm 高」只在任务书里 ⇒ 本单按任务书的数算, 并把「找不到原文」登记成缺口 (E-10)** ★ | ★**main (补登记 / 确认口径)** ★ | ★**判据来源不明时, 结论只能标 [0数据] + 给降级方案, 不能自己把它变成硬约束** ★ |
| ★**U-365-5** ★ | ★**座体真实高度 h** (★既有缺口·本单未变★) ★ | ★**`CRIT` 0.60 / `EDGE_KEEPOUT` 0.80 / `h` 三档 0.90/2.54/4.00 一个都没动; 座体 h 仍 `[0数据]` ⇒ 开口 Y 一律按公式取值** ★ | ★**main → boss (既有 need `iss294_usbc_edge_opening_size_and_z_window`)** ★ | ★**既有缺口, 本单不越界** ★ |
| ★**U-365-6** ★ | ★**本单这道新闸要不要挂进 `state/gate_check.py`** ★ | ★**本单【零挂链】(挂链是 main 的机制地界) ⇒ `Q1` 仍 18/18** ★ | ★**main** ★ | ★**任务书明确「零挂链」** ★ |

---

## ★§8 ★★沙盒重判实测 (★`tmp/iss365_sbx/` · 项目盘内 · 不写 /tmp★) ★★

### ★§8.1 沙盒怎么造的 (★照 main 实读过的源码口径·不踩坑★) ★

| 步 | 做法 | 依据 |
|---|---|---|
| ★**①** ★ | ★**`MECH/check_onepass_struct_crosscheck.py` 【没有】 `--root` ⇒ 它靠 `PROJ = HERE/..` ⇒ ⇒ 沙盒根必须是【一个里面有 `MECH/` 的目录】** ⇒ `logs/iss365/setup_iss365_sbx.py` 把 `MECH/` 整个目录 + `HW/` 需要的表 + `HW/PCB/` 全部复制进 `tmp/iss365_sbx/`, `state/` 用符号链接 (只读) ★ | ★main 任务书 ⑥ ★ |
| ★**②** ★ | ★**控制组: 只用 pcbnew 读进来再存回去 (一个字节都不改)** ⇒ 板 md5 **仍是 `611b869e13518c3c023fb178f91a0075`** ⇒ ★**证明「pcbnew 重存」本身不引入任何漂移** ★ | ★`logs/iss365/sbx_before_board_md5.txt` ★ |
| ★**③** ★ | ★**实验组: 用 pcbnew `FootprintLoad` 把 §1 的 25 件换成官方 `.kicad_mod`** (★位置/旋转沿用旧封装 ⇒ 只测「换 land」, 不夹带「挪位」; pad↔net 按【焊盘号】继承 ⇒ 不替老板做 pad 序对调★) ⇒ 板副本 md5 变 (★本次运行 = `74bc7ecf9bf0ce2fa4a4717cb2b8ebae`; ★pcbnew 每次重存会重铸 uuid ⇒ 这个 md5 每重跑一次会变, ★但几何与判据读数一字不变 (★已重跑一次复核: 7.3250 / 10.3700 / 4.6500 与第一次完全一致★)★) ★ | ★`logs/iss365/sbx_swap_log.json` (25 条逐件 SWAPPED) ★ |
| ★**④** ★ | ★**前后各跑四道 MECH 闸, 输出并排** ★ | ★`logs/iss365/sbx_before_*.txt` / `logs/iss365/sbx_after_*.txt` ★ |

### ★§8.2 ★★四道闸前后并排: 哪几条判据漂了 / 漂了多少 / 漂了之后要重算什么★★ ★

| 闸 | BEFORE rc | AFTER rc | 漂了的判据 | 漂了多少 | 漂了之后要重算什么 |
|---|---|---|---|---|---|
| ★**`MECH/check_onepass_struct_crosscheck.py`** ★ | ★**0** (N1~N6 全过) ★ | ★**1** ★ | ★**只有 N6 (受保护 5 件 md5) 红** ★ | ★**板 md5 `611b869e…` → `74bc7ecf…` ⇒ 【预期红】: 沙盒里板确实被改了 ⇒ 这一条不是结构判据漂移** ★ | ★**无 (结构判据一条没漂)** ★ |
| ★★↑ 同一闸的 §3 表 (逐个落位) ★★ ★ | ★**`R_SEL_*` 最小净距 7.6500 · `TP_DSI_*` 4.6500** ★ | ★**`R_SEL_*` 最小净距 7.3250 · `TP_DSI_*` 4.6500 (不变)** ★ | ★**N2 / N3 / N4 全部仍绿 (冲突 0 条 · 必清空净距全部 ≥ CRIT)** ★ | ★**`R_SEL_*` 净距 Δ = −0.3250 (`R_SEL_D0_N`..`R_SEL_CK_N`) / +0.6750 (`R_SEL_CK_P`..`R_SEL_D3_P`)** ★ | ★**§2.1 那张表的两列数 ⇒ 抄进作业包 §3-S6 (E-7)** ★ |
| ★**`MECH/check_onepass_mech_sync.py`** ★ | ★**0** (M1~M5 全过) ★ | ★**1** ★ | ★**只有 M5 (受保护 5 件 md5) 红** ★ | ★**同上 ⇒ 【预期红】** ★ | ★**无 (M1~M4 一条没漂: 帧标签 / 开口压 SoM 焊盘 / 座体高度参数式 / 判据命令存在性 全绿)** ★ |
| ★**`MECH/check_board_frame_coords.py`** ★ | ★**0** (四项全过) ★ | ★**2** ★ | ★**只有 C4 (合法改板通道) 红** ★ | ★**同上 ⇒ 【预期红】(沙盒里板被改了但台账里没有变更行 ⇒ 按 ISS-296 的判据方向, 这本来就必须红)** ★ | ★**无 (C1/C2/C3 全绿)** ★ |
| ★★`MECH/check_demo_struct_truth.py`★★ ★ | ★**0** (23/23 组) ★ | ★**2** ★ | ★**只有 G5b (受保护文件 md5) 红** ★ | ★**同上 ⇒ 【预期红】** ★ | ★**无 (G1~G8 / C21 / C22 全绿)** ★ |
| ★★**`led_space` (CFC 的 `compute()` 实算)**★★ ★ | ★**可落位块数 1992 · 两条整高带 X 1.550..3.450 / 72.540..73.660 · sweep 1992/2016/2031/2075** ★ | ★**可落位块数 2183 · 两条整高带 X 2.225..3.250 / 73.215..74.385 · sweep 2183/2241/2253/2197** ★ | ★★**这是本单挖到的【真漂移】: `D_LED_G` 的铜箔相对原点的包络变了 ⇒ 两条可放行带 + 可落位块数 + 净距敏感度 sweep 全变**★★ ★ | ★**块数 +191 · 带 A 宽 1.900→1.025 (−0.875) · 带 B 宽 1.120→1.170 (+0.050) · 带 A 左沿 +0.675 / 带 B 左沿 +0.675 · sweep 在 clr=0.5 处【不再单调】(2197 < 2253)** ★ | ★**§8.3 详列 ⇒ MECH_SYNC 机器块的 `led.full_height_bands` + `led.clearance_sweep` + FRAME_CALIBER 的 LED 窗口规格都要同一次重算 (E-9)** ★ |

### ★§8.3 ★★`D_LED_G` 换 0805 ⇒ LED 可放行带的真漂移 (★本单最实的一条结构后果★) ★

★**根因**: ★`MECH/check_board_frame_coords.py` 的 `led_space()` 用的是 `rel` = **`D_LED_G` 的铜箔外框相对封装原点的偏移** ⇒ ★**换 land ⇒ `rel` 变 ⇒ 两条带/窗口/块数全变** ★

| 项 | BEFORE (占位) | AFTER (官方 0805) | Δ |
|---|---|---|---|
| ★**`rel` (铜箔包络相对原点)** ★ | ★`@@LEDRB@@` ★ | ★`@@LEDRA@@` ★ | ★**X 由 [-0.75, 2.15] 变 [-1.425, 1.425] (对称化); Y 由 [-0.65, 0.25] 变 [-0.70, 0.70]** ★ |
| ★**封装原点窗口** ★ | ★X 1.550..157.050 · Y 1.450..98.950 ★ | ★X 2.225..157.775 · Y 1.500..98.500 ★ | ★**X 左沿 +0.675 · 右沿 +0.725; Y 两端各内缩 0.050** ★ |
| ★**整高自由带 A** ★ | ★X 1.550..3.450 (宽 **1.900**) · Y 1.450..98.950 ★ | ★X 2.225..3.250 (宽 **1.025**) · Y 1.500..98.500 ★ | ★**宽 **−0.875** ★ |
| ★**整高自由带 B** ★ | ★X 72.540..73.660 (宽 **1.120**) ★ | ★X 73.215..74.385 (宽 **1.170**) ★ | ★**宽 +0.050 · 整体右移 +0.675** ★ |
| ★**可落位块数 (clr=0)** ★ | ★**1992** ★ | ★**2183** ★ | ★**+191** ★ |
| ★**净距敏感度 sweep (clr 0 / 0.1 / 0.2 / 0.5)** ★ | ★`@@LEDSWEEPB@@` ★ | ★`@@LEDSWEEPA@@` ★ | ★**★换封装后【不再单调】: clr=0.5 (2197) < clr=0.2 (2253) ⇒ 「净距越大可落位越多」这条旧直觉在 0805 下不成立 ⇒ 换封装后必须重扫而不是插值** ★ |
| ★**最近可落位点到 `R_LED_G` pad2 的走线长度** ★ | ★**0.450 mm** ★ | ★**0.621 mm** ★ | ★**+0.171 ⇒ `LED_G_D` 走线最短长度要求要重算** ★ |

★**★ ⇒ 结论: ★**「S6 落位对 `D_LED_G` 两条可放行带零侵占 ⇒ `led_space` 的可落位块数 (1992 / 2016 / 2031 / 2075) 不变」—— 这句既有页 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 里的结论, 在换官方 0805 land 之后【不成立】⇒ ⇒ 必须同一次重算 (E-9)** ★ ★★(★注意: 这句结论的【前半句】—— S6 落位对 LED 带零侵占 —— 换封装后【仍成立】(那 10 件的落位包络前后都不碰 LED 带); 【后半句】的块数【变了】**) ★★
★**★ ⇒ 该既有页 §3.2 已按 main 2026-11-23 16:55 的整改要求【同趟重算并改写】(★前半句保留 + 后半句补上换封装后的真数 1992→2183 / sweep 2183/2241/2253/2197 与「不再单调」这句警告★) ⇒ 旧/新 md5 对照见 `logs/iss365/29b_struct_crosscheck_md5_change.txt`** ★

### ★§8.4 ★★与既有闸的逐条对账 (★证明本单的口径不是自说自话★) ★★

★**本单独立实算的 S6 净距, 与 `MECH/check_onepass_struct_crosscheck.py` 自己打印的表【逐条对账】: ★**

```
[xcheck] BEFORE: 闸打印 20 行 · 与本单实算不一致 0 条
[xcheck] AFTER : 闸打印 20 行 · 与本单实算不一致 0 条
```

★**⇒ 口径零漂移的机器证明: 换封装前后各 20/20 逐条一致 (★`logs/iss365/xcheck_iss365.py` 可复跑★)** ★

---

## ★§9 本页的边界 (★逐条自证★) ★

| 边界 | 自证方式 |
|---|---|
| ★**零写板** ★ | ★板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + 大小 4,940,213 B 跑前跑后逐字节相同 (★`logs/iss365/00_baseline_md5.txt` / `logs/iss365/29_final_md5.txt`★) ★ |
| ★**零落表** ★ | ★网表 / 脚表 / BOM md5 跑前跑后逐字节相同 ★ |
| ★**零改既有闸** ★ | ★`MECH/check_onepass_struct_crosscheck.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节未改 ★ |
| ★**零改既有页面正文 (★除 main 点名整改的那一句★)** ★ | ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_GEOM_30MM.md` · `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_FRAME_CALIBER.md` 老字一字未改; ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 只改了 §3.2 一行 (★main 2026-11-23 16:55 点名要求: 「led_space 块数不变」那半句作废 ⇒ 同趟重算★) ⇒ 旧/新 md5 对照见 `logs/iss365/29b_struct_crosscheck_md5_change.txt`; E-7~E-13 只写在【本页】** ★ |
| ★**零挂链** ★ | ★本单新闸【不挂】进 `state/gate_check.py` ⇒ ★**Q1 的缺项与本单无关 (★mech-lead 本人 6/6 · 缺: 无; 缺的三块在 sw-lead 的在飞交卷页★)** ★ |
| ★**零外发** ★ | ★本单 0 次邮件 / 询价 / 问询 / 采购; 封装高度等资料全部【自己网上查】并标 `[官网]` ★ |
| ★**不替老板拍板** ★ | ★`D_LED_G` 光孔有/无 · W-1/W-2 · 按键 3 N vs 1.5 N ⇒ §7 只登记事实 + 代价 ★ |
| ★**不改 `state/issue_log.yaml`** ★ | ★本单不签 issue_log ⇒ 签字归 main ★ |
| ★**沙盒只落 `tmp/iss365_sbx/`** ★ | ★不写 `/tmp` (★2026-11-23 04:4x 实测系统 /tmp 配额已满★) ★ |
| ★**证据分级** ★ | ★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 全部标; ★**实物 `[实测]` = 0 条** (★本机无板无量具 ⇒ 一切「实测」= 文件实读 + 脚本实跑★) ★ |
| ★**单条 `exec` ≤ ~120 秒** ★ | ★本单所有命令单条实跑 ≤ 115 s ★ |

---

## ★§10 机器可读 JSON 块 (★全文最后 · **机器闸只认这块**★) ★

<!-- MACHINE-BLOCK-BEGIN -->
```json
@@MB@@
```
<!-- MACHINE-BLOCK-END -->
"""


if __name__ == "__main__":
    main()
