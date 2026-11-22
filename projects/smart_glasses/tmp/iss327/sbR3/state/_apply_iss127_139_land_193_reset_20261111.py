#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
落账 (2026-11-11 20:0x, 项目总工 main) —— ★**三件事, 一份原子写** ★

★**① ISS-127 (mech-lead) 交卷 ⇒ main 独立验收签字 (verified/pass)**
  交卷 = `HANDOFF/2026-11-11_mech-lead_ISS127_H链量产几何解.md` (19:30) + `MECH/iss127_h_chain_check.py`
         (19:29:38) + `MECH/ISS127_H_CHAIN_SOLUTION.md` (19:33) + `MECH/DFM_REVIEW.md` (19:29) + 分片
  ★**我独立重跑 (不采信自述)**:
    `python3 MECH/iss127_h_chain_check.py`              ⇒ **rc=0**
    `python3 MECH/iss127_h_chain_check.py --self-test`  ⇒ **rc=0** (含反向用例: 退回现状拉出方向 ⇒ 红 /
      判据与公差放宽到 0 ⇒ 仍红 / 人为加 0.50 损失 ⇒ 红 / L 向脱模 ⇒ 比现状更红 ⇒ 被否决 /
      链② α=1.5°+石墨+t=1.22 ⇒ 红 / 电池座壁厚 ×3 ⇒ 重量账红 / 金属舱块 ⇒ 判死)
    `python3 MECH/fit_check_v3_30mm.py`                ⇒ **rc=0**
    `python3 MECH/skeleton_section_check.py`           ⇒ **rc=0**
    `python3 state/merge.py`                            ⇒ **rc=0 (冲突 0)**
  ★**核心结论 (它自己的)**: 根因不是「余量紧张」是「**拉出方向选错**」—— 脱模斜度只吃**垂直于拉出方向**
    的截面, 现状 P=V (主腔深 38.00) ⇒ H 链被吃 Δ=2·38·tanα=1.327 ⇒ **−0.577**; ★**把拉出方向换成 H**
    ⇒ H 链脱模项 Δ=0 ⇒ 三档 α (皮纹 0.5°/通用 1.0°/光面 1.5°) **全部**过 0.40 判据
    (0.750, 计皮肤盖自身后 0.736/0.722/0.708) ⇒ ★**几何可行了** ★
  ★**诚实边界 (它自己写明的, 我认可)**: 全部 [推算] (本机打印/量测不可达) · 量产公差带/斜度/收缩率
    **未按牌号锁定** ⇒ ★**这不是"已量产可行", 是"几何上做得到 + 尺子已立"** ★
  ★**顺带新发现 (它查出来的, 我核过)**: 现状 P0 在 α=1.5°+含石墨+t=1.22 ⇒ **0.190 破线**
    ⇒ ★**链② 在光面 1.5° 下也破 ⇒ 这条 DFM 评审从来没核过** ⇒ 属"没藏账"★

★**② ISS-139 (sw-lead) 交卷 ⇒ main 独立验收签字 (verified/pass)**
  交卷 = `HANDOFF/2026-11-11_sw-lead_ISS139_ISP_tuning立项.md` (19:18) + `SW/tools/iq_coverage_check.py`
         (19:15:47) + `SW/ISP_TUNING_INITIATION_PLAN.md` (19:17) + 分片
  ★**我独立重跑 (不采信自述)**:
    `python3 SW/tools/iq_coverage_check.py`             ⇒ **rc=0 (16/16 通过, 0 失败)**
    `python3 SW/tools/iq_coverage_check.py --self-test` ⇒ **rc=0 (正向 16/16 + 反向 4/4 全被抓住)**
    `python3 state/merge.py`                            ⇒ **rc=0 (冲突 0)**
  ★**核心结论 (它自己的)**: rkaiq 公开 iqfiles 里 ★**ar0234 / ov04c10 都没有 IQ 文件** ⇒ ★**这笔账躲不掉
    ⇒ ISP tuning 必须自己排** ⇒ 它把"要问模组厂/服务商的问题清单"列出来了 ★
  ★**它的机检表是实读的**: ★**J2:ov04c10=0** (实测: 文件 0, 目录 0) · J3:isp-gen-dirs
    (['isp20','isp21','isp32','isp32_lite','isp3x']) · J5:attested-subset (本机既有记录 9 个带目录归属的文件,
    快照缺失 0) ⇒ ★**用的是本机快照 `HW/_os_snapshots/rkaiq_iqfiles.json`, 没联网重抓当新证据** ★
  ★**边界**: 只出方案 + 只起草问题清单, ★**一封都没发 / 没联系任何外部** (★外发一律经项目总工★) ★

★**③ ISS-193 (hw-lead) ⇒ 状态复位 fixing → open + brief 重写 (★这一条是本轮最重要的发现★)**
  ★**为什么必须复位 (★main 2026-11-11 19:1x~20:0x 逐条实测, 不是推测★)**:
  · 会话 `agent:hw-lead:subagent:32d6fc57-...` 17:09:23 起跑 ⇒ ★**19:10:18 结束** (runtimeMs 7252523 ≈ **120.9 分钟**)
  · ★**末条 = `stopReason: "length"`** ⇒ ★**撞【输出 token 上限】被掐断** ⇒ ★**不是被 scope 驳回** ⇒
    ★**它没交卷**: ★**无** `HANDOFF/*ISS193*` (实测 `ls HANDOFF/` 只有 ISS191/ISS189/ISS192/ISS139/ISS127 那几份)
    · ★**无** BOM 回填 (`HW/BOM_v1.csv` md5 `3ad04e1a…` **仍是 11-05 那份, 一字未动**)
    · ★**无** `state/fragments/hw.yaml` 写入 (实测 mtime 仍 **10:38**)
  ⇒ ★**`status=fixing` 成了【假标记】** ⇒ ★**这是 ISS-181 / ISS-192 同一个病 (第 3 次出现)**:
    `advance.py` 的 in_flight 判据 = 「owner 名下已有 status==fixing 的 issue ⇒ 本轮跳过该 agent」
    ⇒ ★**hw-lead 的名额被一条【已经死掉】的单永久占住** ⇒ ★**A 段连续多轮为空** ★

  ★**★而且这一轮我发现了它【为什么炸】+【它本来也做不对】(★这是本轮最值钱的部分★)★**:
  ★**炸因 (实测)**: 它的 brief 要求"逐个查 29 个器件的真实脚数" ⇒ 它就在 KiCad 官方符号库里
    ★**一个个 grep / 逐个 cat 整个 .kicad_sym 文件** ⇒ ★**上下文被符号库文件撑爆**
    ⇒ ★**实测它 120.9 分钟里跑了几十次 exec, 全在翻符号库** ⇒ ★**一条脚数都没落盘** ★
    ★**⇒ 同一个错不能再犯第二次: 重派必须【自带答案】, 不许让 agent 去"查"** ★
  ★**★更关键: 它的 brief【验收判据本身就错了】(★main 沙盒实测★)★**:
    ★**brief 说"给 BOM 定 opn/封装 ⇒ 脚数自动补齐" ⇒ ★**但 gap 文档的脚数【根本不是从 BOM 读的】**!
    ★**实测 (沙盒, 不落盘)**: 我把 BOM 里 J_USB_C 的 opn 填成 "GCT USB4105-16P …" 重跑生成器
      ⇒ ★**产物里 J_USB_C 的"真实脚数"仍然是 `[0数据]`** ⇒ ★**填 BOM 的 opn 对 [0数据] 数量【零效果】** ★★
    ★**真正决定 [0数据] 的是【生成器里的三张查找表】**: `SPEC_PINS` / `OPN_KICAD` / `PREFIX_KICAD`
      ⇒ ★**实测 (沙盒)**: 我在 `PREFIX_KICAD` 里加一条 `SW_` ⇒ ★**重跑后 [0数据] 从 29 降到 23**
      (SW_BOOT/SW_KEY_CAM/SW_KEY_PWR/SW_KEY_VM/SW_KEY_VP/SW_RST 6 个全填上了) ⇒ ★**机制确认** ★
    ⇒ ★**★所以原来的 brief 是【做无用功】: 它花 120 分钟去查符号库, 就算查对了, 改的也是 BOM,
      而 BOM 改了 [0数据] 也不动 ⇒ 验收判据 `[0数据]` 永远降不下来 ⇒ 白干** ★★
  ★**⇒ 本单重派时 brief 必须【三改】**: ①**判据改掉** (★不许再说"填 BOM 的 opn"★ ⇒ ★**改成"往生成器的
    SPEC_PINS / OPN_KICAD / PREFIX_KICAD 三张表里加条目"★) ②**候选答案【我先算好塞进去】**
    (★不许让 agent 再去翻符号库★) ③**兜底口径**: 查不到的**不许猜**, ★**保留 [0数据] 并写进
    `PIN_REALITY_GAP.md` §5.2 的"仍缺"清单 ⇒ 这正是 E-02 那一封信要问原厂的内容** ★
  ★**★同时我实测到两个【会导致假数的坑】, 必须在 brief 里点名★★**:
    ★**坑①**: KiCad 官方库里 ★**大量符号用 `extends` 继承父符号** (实测 AO3401A / BSS138 / 2N7002 /
      SMAJ5.0A / SM6T18A / USBLC6-2SC6 / CSD16406 全是) ⇒ ★**它们自己文件里 0 个 `(pin` 行** ⇒
      ★**`kicad_pins()` 正则 `\(pin\s+\w+\s+\w+\s*\(at` 数出来 = 0** ⇒ ★**⇒ 指向这种符号 = 脚数 0 = 假数!**
      ⇒ ★**⇒ 候选表里只给【实测 pins>0 且 extends=False】的符号** ★
    ★**坑②**: `CHG_GND_STAR` (单点汇流位) / `X1` (晶振焊盘位, 不装) / `BT_432243` (电池座)
      ★**这三个不是"器件"** ⇒ ★**表里 3 行全是同一个网 (GND)** ⇒ ★**它们真实脚数【不是器件脚数】,
      填任何数都是编** ⇒ ★**⇒ 只能保留 [0数据] 并注明"非器件/焊盘位"** ★

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** ⇒ 通过才写
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ ★**只改 ISS-127 / ISS-139 / ISS-193 这三条的字段** ⇒ 别的 187 条一个字节不动

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
  不下采购单 · ★**不改 `PROJECT_TRACKER.md`** ★
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"

# ── ① ISS-127 验收签字 ────────────────────────────────────────────────────────
V127 = (
    "2026-11-11 20:0x 项目总工亲核通过 (verify_by=main ≠ owner=mech-lead)。★**先说结论口径**: 本单 "
    "'verified' = ★**几何上【做得到】+ 尺子【已立】**, ★**不等于**量产件已实测合格 (★本机打印/量测不可达 ⇒ "
    "全部 [推算]★) —— 这是诚实边界, 不是本单缺陷。★**我独立重跑 (不采信自述)**: "
    "`python3 MECH/iss127_h_chain_check.py` rc=0 · `--self-test` rc=0 (★反向用例全被抓住: 退回现状拉出方向⇒红 / "
    "判据与公差放宽到0⇒仍红 / 人为加0.50损失⇒红 / L向脱模⇒比现状更红⇒被否决 / 链② α=1.5°+石墨+t=1.22⇒红 / "
    "电池座壁厚×3⇒重量账红 / 金属舱块⇒判死★) · `python3 MECH/fit_check_v3_30mm.py` rc=0 · "
    "`python3 MECH/skeleton_section_check.py` rc=0 · `python3 state/merge.py` rc=0 (冲突 0) ⇒ ★**全绿**。★"
    "**核心结论 (它自己写对的)**: 根因不是『余量紧张』是『**拉出方向选错**』—— 脱模斜度只吃**垂直于拉出方向**"
    "的截面, 现状 P=V (主腔深 38.00) ⇒ H 链被吃 Δ=2·38·tanα=1.327 ⇒ **−0.577** ⇒ ★**把拉出方向换成 H** ⇒ "
    "H 链脱模项 Δ=0 ⇒ 三档 α (皮纹0.5°/通用1.0°/光面1.5°) **全部**过 0.40 判据 (0.750, 计皮肤盖自身后 "
    "0.736/0.722/0.708) ⇒ ★**几何不可行 ⇒ 几何可行, 通了** ★。★**推荐 P1**: 镜腿壳 H 向分型 (皮肤盖+内胆) + "
    "电池座=独立 0.5mm CNC 嵌件 (热隔离, 不与骨架共体) + 石墨裁到 SoC 带 ⇒ ★**重量账内 (金属+石墨净减) + 零件 "
    "4件/侧 + 模具2套/侧** ★。★**它顺带查出一条 DFM 评审从来没核过的新账**: 现状 P0 在 α=1.5°+含石墨+t=1.22 ⇒ "
    "**0.190 破线** ⇒ ★**链② 在光面下也破** ⇒ 没藏账。★**未闭合 (它自己写明, 我认可)**: 量产公差带/斜度/"
    "收缩率**未按牌号锁定** (DFM §6 needs_from #1/#3) ⇒ ★**这一条仍需老板拍板 / 需原厂数据** ★。"
    "★**板/网表/原理图 md5 全未变** (611b869e… / c78f9912… / 3e504d2b…) ⇒ ★**签字通过** ★"
)

# ── ② ISS-139 验收签字 ────────────────────────────────────────────────────────
V139 = (
    "2026-11-11 20:0x 项目总工亲核通过 (verify_by=main ≠ owner=sw-lead)。★**我独立重跑 (不采信自述)**: "
    "`python3 SW/tools/iq_coverage_check.py` rc=0 (★**16/16 通过, 0 项失败**) · `--self-test` rc=0 (★正向 16/16 + "
    "反向 4/4 全被抓住: 注入 ar0234cs IQ⇒J1/J2 变红 / 删全部 imx415⇒J1 变红 / 删 isp3x 目录⇒J3/J3b 变红 / "
    "删一个 attested 文件⇒J5 变红★) · `python3 state/merge.py` rc=0 (冲突 0) ⇒ ★**全绿**。★**核心结论**: "
    "rkaiq 公开 iqfiles 里 ★**ar0234 / ov04c10 都没有 IQ 文件** (★实测 J2:ov04c10=0 —— 文件 0, 目录 0★) ⇒ "
    "★**这笔账躲不掉 ⇒ ISP tuning 必须自己排** ⇒ 本单把它变成【可排期/可询价/可验收】的立项, 并列出要问模组厂/"
    "服务商的清单。★**机检表是实读的** (★J3:isp-gen-dirs = ['isp20','isp21','isp32','isp32_lite','isp3x'] · "
    "J5:attested-subset 本机既有记录 9 个带目录归属的文件, 快照缺失 0 个★) ⇒ ★**用的是本机快照 "
    "`HW/_os_snapshots/rkaiq_iqfiles.json`, 没联网重抓当新证据** ★。★**边界 (我核过)**: 只出方案 + 只起草"
    "问题清单 ⇒ ★**一封都没发 / 没联系任何模组厂或服务商** (★外发一律经项目总工★) ⇒ ★**签字通过** ★"
)

# ── ③ ISS-193 复位 + brief 重写 ───────────────────────────────────────────────
NOTE_193 = (
    "\n\n★2026-11-11 20:0x 项目总工**状态复位 (fixing → open) + brief 重写** (★**实测: 上一轮是被【输出 token "
    "上限】掐断的, 不是被 scope 驳回★)**。★**事实**: 会话 `agent:hw-lead:subagent:32d6fc57-...` 17:09:23 起跑 ⇒ "
    "★**19:10:18 结束** (runtimeMs 7252523 ≈ **120.9 分钟**) ⇒ ★**末条 `stopReason: \"length\"`** ⇒ ★**撞输出 "
    "token 上限** ⇒ ★**它没交卷**: ★**无** `HANDOFF/*ISS193*` · ★**无** BOM 回填 (`HW/BOM_v1.csv` md5 "
    "`3ad04e1a…` 仍 11-05 那份) · ★**无** `state/fragments/hw.yaml` 写入 (mtime 仍 10:38) ⇒ ★**`status=fixing` "
    "成了【假标记】** ⇒ ★**这是 ISS-181 / ISS-192 同一个病 (第 3 次出现)** ⇒ ★**hw-lead 的名额被一条已经死掉的"
    "单永久占住 ⇒ A 段连续多轮为空**。★**★本轮我还查到了它【为什么炸】+【它本来也做不对】★★** (★沙盒实测★): "
    "① **炸因**: brief 要求『逐个查 29 个器件的真实脚数』⇒ 它就去 KiCad 官方符号库一个个 grep / 整文件 cat ⇒ "
    "★**上下文被符号库撑爆, 120.9 分钟一条脚数都没落盘** ⇒ ★**同一个错不许再犯第二次: 重派必须【自带答案】**; "
    "② **★它的验收判据本身就错了★**: brief 说『给 BOM 定 opn/封装 ⇒ 脚数自动补齐』, ★**但 gap 文档的脚数【根本"
    "不是从 BOM 读的】** ⇒ ★**实测: 把 BOM 里 J_USB_C 的 opn 填成 'GCT USB4105-16P …' 重跑生成器 ⇒ 产物里 "
    "J_USB_C 的真实脚数【仍然是 `[0数据]`】⇒ ★**填 BOM 的 opn 对 [0数据] 数量零效果** ⇒ ★**真正决定 "
    "[0数据] 的是【生成器里的三张查找表】`SPEC_PINS` / `OPN_KICAD` / `PREFIX_KICAD`** ⇒ ★**实测: 加一条 "
    "`SW_` 前缀 ⇒ [0数据] 从 29 降到 23** ⇒ ★**⇒ 它就算查对了符号、改的也是 BOM, 验收判据永远降不下来 = "
    "白干 120 分钟** ⇒ ★**⇒ 本单重派时 brief 三改 (判据改掉 / 候选答案我先算好塞进去 / 查不到的保留 [0数据] "
    "并写进 §5.2 的『仍缺』清单 —— 那正是 E-02 要问原厂的内容★)**。★**★顺带实测到两个会导致【假数】的坑, "
    "已写进新 brief★★**: (a) ★**KiCad 官方库里大量符号用 `extends` 继承父符号** (实测 AO3401A / BSS138 / "
    "2N7002 / SMAJ5.0A / SM6T18A / USBLC6-2SC6 全是) ⇒ ★**它们自己文件里 0 个 `(pin` 行 ⇒ `kicad_pins()` "
    "数出来 = 0 ⇒ ★**指向这种符号 = 脚数 0 = 假数**; (b) `CHG_GND_STAR` (单点汇流位) / `X1` (晶振焊盘位, "
    "不装) / `BT_432243` (电池座) ★**这三个不是器件** (表里 3 行全是同一个网 GND) ⇒ ★**填任何数都是编** ⇒ "
    "★**只能保留 [0数据] 并注明『非器件/焊盘位』**。"
)

BRIEF_193 = """★**目标 (★与上一轮【根本不同】—— 上一轮 120.9 分钟撞 token 上限, 一条没落★)**: ★**把
   `HW/PCB/PIN_REALITY_GAP.md` 里 29 个 `[0数据]` 的【真实脚数】填掉能填的** ⇒ ★**本轮的判据是【改生成器的
   三张查找表】, 不是改 BOM** ⇒ ★**本单【不许去翻 KiCad 符号库】** (★答案我已算好塞在下面★)。

★**★① 机制 (★main 2026-11-11 20:0x 沙盒实测, 不是推测★ —— 这条最要紧, 搞错就白干★)**:
   ★**gap 文档的"真实脚数"【不是从 BOM 读的】** ⇒ ★**你往 `HW/BOM_v1.csv` 的 `opn` 列填东西, 对
   `[0数据]` 的数量【零效果】** (★实测: 填了 J_USB_C 的 opn 后重跑, 它仍是 `[0数据]`★)
   ⇒ ★**真正决定脚数的是 `state/gen_kicad_sch.py` 里的三张查找表 (按顺序查)**:
     ① `SPEC_PINS`     (精确 ref → 脚数)          —— 例: `J_CHG: 10` / `U_CHG: 24`
     ② `PARTIAL_PINS`  (100 球位座这类"部分用到"的)
     ③ `OPN_KICAD`     (精确 ref → (KiCad 符号文件, 来源说明))
     ④ `PREFIX_KICAD`  (前缀 → (KiCad 符号文件, 来源说明))  ★**例: `('R_', 'Device.kicad_symdir/R.kicad_sym', …)`**
   ⇒ ★**★所以本单的动作 = 往这几张表里加条目 ★** ⇒ ★**验收也只看这几张表 + 重跑产物** ★

★**★② 候选答案我已算好 (★你直接用, 不许再去 grep 符号库 — 上一轮就是死在翻符号库★)**:
   ★**先用这张表 (★符号路径 = `state/gen_kicad_sch.py` 里 `KICAD_SYM` 下的相对路径 = 
   `/home/yuewuya/kicad/squashfs-root/usr/share/kicad/symbols/` 下的相对路径★)**:
   | ref | 建议符号 (★★已实测 pins 数★) | 建议脚数 | 依据 |
   |---|---|---|---|
   | `Q1` | `Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym` | 3 | KiCad 官方库 N-MOS 通用符号 (★G/D/S★) |
   | `Q_AND` | `Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym` | 3 | 同上 |
   | `Q_ENVC` | `Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym` | 3 | 同上 |
   | `Q_CHG_LED` | `Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym` | 3 | 同上 |
   | `Q_PG` | `Transistor_FET.kicad_symdir/Q_PMOS_GDS.kicad_sym` | 3 | KiCad 官方库 P-MOS 通用符号 |
   | `SW_BOOT` `SW_KEY_CAM` `SW_KEY_PWR` `SW_KEY_VM` `SW_KEY_VP` `SW_RST` | `Switch.kicad_symdir/SW_Push.kicad_sym` | 2 | KiCad 官方库按键符号 (★2 脚★) |
   | `FB_DEMO` `FB_VBUS` | `Device.kicad_symdir/FerriteBead.kicad_sym` | 2 | KiCad 官方库磁珠符号 |
   | `U_BATPROT` | `Battery_Management.kicad_symdir/BQ297xy.kicad_sym` | 6 | ★**BOM opn 已是 BQ2970** ⇒ 同系列符号 |
   | `U_EN_SW` `U_PWR_SW` | `Power_Management.kicad_symdir/AP22913CN4.kicad_sym` | 4 | ★**BOM opn 已是 TPS22991RAA (UQFN-4)** ⇒ 同类 4 脚负载开关符号 |
   | `U_SUPV` | `Power_Supervisor.kicad_symdir/TPS3808DBV.kicad_sym` | 6 | ★**网表 value 已写 TPS3808G01** ⇒ 同系列电压监控符号 |
   | `U_LDO_S28` | `Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym` | 5 | ★**与已填的 `U_LDO_L18`/`U_LDO_L33` 等同一张表, 直接照抄★** |
   | `J_USB_C` | `Connector.kicad_symdir/USB_C_Receptacle_USB2.0_16P.kicad_sym` | 17 | ★**BOM opn 已是 GCT USB4105-16P (16P 座)** ⇒ KiCad 同款 16P 座符号 (16 信号 + 1 壳) |
   | `D_TVS_VBUS` | `Diode.kicad_symdir/ZPYxx.kicad_sym` | 2 | 5V 单向 TVS = 2 脚 |
   | `D_ESD_CAM` `D_ESD_DEMO` `D_ESD_LIGHT` `D_ESD_TC` `D_ESD_USB_D` | `Power_Protection.kicad_symdir/SP0503BAHT.kicad_sym` | 4 | ESD/TVS 阵列 (★4 脚★) |
   ★**★三个不许填的 (★填了就是编★)★**:
   | `CHG_GND_STAR` | ★**不许填** | — | ★**不是器件** (单点汇流位, 表里 3 行全是同一个网 GND) ⇒ 保留 `[0数据]` + 注"非器件" |
   | `X1` | ★**不许填** | — | ★**不是器件** (晶振焊盘位, 不装) ⇒ 保留 `[0数据]` + 注"焊盘位/不装" |
   | `BT_432243` | ★**不许填** | — | ★**不是器件** (电池座, 本机无对应符号) ⇒ 保留 `[0数据]` + 注"电池座, 待选型" |
   ★**⇒ 你必须【自己复核每个候选符号的脚数】, 但【不许用"grep 整个符号库"的方式】 ⇒ ★**只许用上面这张表里
   给出的路径, 逐个 `grep -c '(pin ' <那一个文件>` 数一次 (★★`extends` 的符号会数出 0 ⇒ 那是假数, 不许用★)** ★

★**★③ 两个会把数字搞假的坑 (★上一轮没测出来, 本轮实测★)★★**:
   ★**坑① `extends`**: KiCad 官方库里 ★**大量符号用 `extends` 继承父符号** (实测 `AO3401A` / `BSS138` /
      `2N7002` / `SMAJ5.0A` / `SM6T18A` / `USBLC6-2SC6` 全是) ⇒ ★**它们自己文件里 0 个 `(pin` 行** ⇒
      `kicad_pins()` 的正则 `\(pin\s+\w+\s+\w+\s*\(at` 数出来 = **0** ⇒ ★**⇒ 指向这种符号 = 脚数 0 = 假数!**
      ⇒ ★**⇒ 只许用【实测 pins>0 且该文件里没有 `extends`】的符号** (★上表里给出的都满足, 你复核时确认这一条★)
   ★**坑② `SPEC_PINS` 有两份拷贝**: `state/check_netlist_pins.py` 里一份, `state/gen_kicad_sch.py` 里一份
      (★★实测当前两份内容一致★) ⇒ ★**你要改的是【生成器那份】(`state/gen_kicad_sch.py`), 因为 gap 文档只读它★**
      ⇒ ★**改完顺带核一下两份是否还一致 (不一致就在交卷报告里点出来, 别自己动另一份)** ★

★**★④ 验收 (★判据改了 —— 上一轮的判据是错的★)★**:
```
python3 state/gen_kicad_sch.py --pin-gap     # ★**重跑产物 (★真命令, 不是不存在的 state/gen_pin_reality_gap.py★)
grep -c '\\[0数据\\]' HW/PCB/PIN_REALITY_GAP.md   # ★**目标: 29 → 尽量低 (★下表给的上限≈10★); 剩余的必须是【表里那三个非器件】**
python3 state/merge.py                        # rc 必须 0 (冲突 0)
python3 state/gate_check.py                   # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★**板 611b869e… / 网表 c78f9912… / pins 4814617e… / BOM 3ad04e1a… 必须一字未变** ★
```
   ★**★不许改 BOM ★** (★改了对 [0数据] 零效果, 只会把 BOM 和真源脱节★) ⇒ ★**本单只许改
   `state/gen_kicad_sch.py` 的那三张查找表 + 重跑出的 `HW/PCB/PIN_REALITY_GAP.md`** ★
   ★**★落盘纪律 (★上一轮的另一个教训★)★**: ★**每填完一批 (★建议每 5 个★)就立刻重跑 `--pin-gap` 看一次
   `[0数据]` 数量 ⇒ ★**不许攒到最后一起写** ⇒ ★**宁可交一半, 也不要交零** (★上一轮交零的直接原因就是攒到最后★)** ★
   ★**交卷 ≤ 25 行** (结论先行; 逐条给复现命令与实测输出; ★**列清你填了哪些 / 留了哪些 / 为什么留★**)。

★**边界 (不许越)**
· ★**只写**: `state/gen_kicad_sch.py` (★**只许动那三张查找表 + 必要的注释, 不许动生成逻辑 / 画图逻辑★**)
  + ★**重跑生成的** `HW/PCB/PIN_REALITY_GAP.md` + `HANDOFF/` 下交卷报告
  + ★**必要时** `state/fragments/hw.yaml` (走 `state/frag_write.py`; ★**只许新增条目, 不许删改别人的 key★**)。
· ★**不许碰**: `HW/BOM_v1.csv` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` ·
  `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` (★**除
  `state/gen_kicad_sch.py` 那三张表本身★**) · `PROJECT_TRACKER.md` §0 · **别人的分片** ·
  `state/issue_log.yaml` (★**改 issue 状态是 main 的活★**)。
· ★**不许联系供应商/原厂/服务商** (★外发一律经项目总工★) · ★**不许发任何邮件** ★
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**任何统计数必须同时给口径** (哪块板 / 哪个口径 / 何时)。
· ★**不许猜脚数**: ★**查不到就保留 `[0数据]` 并写进 §5.2 的"仍缺"清单 ⇒ 那正是 E-02 那封信要问原厂的内容** ★
· ★**不要改板**: demo 板 (160×100) 实测 **MountingHole = 0** ⇒ ★**那是布局类, 按老板 11-11 10:07 口径【不派】**
  ⇒ ★**本单不许碰它**。
"""


def main() -> int:
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        doc = yaml.safe_load(raw)
        items = list(doc.get("issues") or [])
        before = {it.get("id"): dict(it) for it in items}

        # ---- 自证 ①: yaml 往返必须逐字节相同 (通过才许写) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("❌ yaml 往返不一致 ⇒ 放弃写盘 (★不能保证只改目标字段★)")
            return 2

        touched = []
        for it in items:
            iid = it.get("id")
            if iid == "ISS-127":
                it["status"] = "verified"
                it["verify_result"] = V127
                it["verify_at"] = "2026-11-11 20:0x"
                it["verify_by"] = "main"
                it["fix_ref"] = "HANDOFF/2026-11-11_mech-lead_ISS127_H链量产几何解.md"
                touched.append(iid)
            elif iid == "ISS-139":
                it["status"] = "verified"
                it["verify_result"] = V139
                it["verify_at"] = "2026-11-11 20:0x"
                it["verify_by"] = "main"
                it["fix_ref"] = "HANDOFF/2026-11-11_sw-lead_ISS139_ISP_tuning立项.md"
                touched.append(iid)
            elif iid == "ISS-193":
                it["status"] = "open"
                it["task_brief"] = BRIEF_193
                it["note"] = (it.get("note") or "") + NOTE_193
                it.pop("dispatched_at", None)
                touched.append(iid)

        if sorted(touched) != ["ISS-127", "ISS-139", "ISS-193"]:
            print("❌ 目标不全: %s" % touched)
            return 2

        # ---- 自证 ②: 非目标 issue 必须逐字段不变 ----
        after = {it.get("id"): it for it in items}
        if len(after) != len(before):
            print("❌ issue 总数变了 ⇒ 放弃写盘")
            return 2
        for k, b in before.items():
            if k in ("ISS-127", "ISS-139", "ISS-193"):
                continue
            if after[k] != b:
                print("❌ 非目标 issue 发生变化: %s ⇒ 放弃写盘" % k)
                return 2

        # ---- 原子写 ----
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        dfd = os.open(HERE, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)

        print("✅ issue_log.yaml 已落盘 (原子写, 锁内重读)")
        print("   - ISS-127 → verified (main 亲核签字, 独立重跑 4 条 rc=0)")
        print("   - ISS-139 → verified (main 亲核签字, 独立重跑 2 条 rc=0)")
        print("   - ISS-193 → open (假 fixing 标记复位) + brief 重写 (判据改掉 / 候选答案自带 / 兜底口径)")
        print("   - 别的 %d 条 issue 一个字节未动 ✔" % (len(before) - 3))
        return 0
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)


if __name__ == "__main__":
    sys.exit(main())
