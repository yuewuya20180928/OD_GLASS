#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开单: ISS-199 (hw-lead) + ISS-200 (mech-lead) —— 2026-11-12 01:4x 队列自动派活 job

★★**为什么开这两单 (★实测, 不是推测★)** ★★:
· ISS-136 (J_CHG pin map 订正 + 接进 gate_check) **刚被我验收签字** (★main 独立复核: rc=0 · Q1 18/18 ·
  Q6 真源闸在跑 · 板/网表/pins 一字未变 · §5.2 逐脚对拍网表一致★)
  ⇒ ★**它定的口径 = 「网表是唯一真源, 文档是它的镜像」** ★
· ★**但它只改了 `HW/CHARGE_BOARD_SPEC.md` §5.2 一张表 (★它的地界★) ⇒ 我今晚扫全树, 发现 J_CHG pin map
  在别处还有 4 套并行的旧口径** ★★:
  - HW 侧 (4 处): `HW/CHARGE_BOARD_SPEC.md` §5.1 过铰链线表 (第 3/4/5/8/9 行) + §7 的 P10 csv 镜像块
    + `HW/J_CHG_SELECTION.md` (第 30 行 C-2 行 + 第 196 行) + `HW/POWER_SHUTDOWN_V3.md` (第 129 行)
    ⇒ **ISS-199 (hw-lead)**
  - 结构侧 (2 处): `MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块 (第 283-291 行, ★还是 1×6@1.27mm 的老座★)
    + `state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map` (第 1848-1851 行)
    ⇒ **ISS-200 (mech-lead)**
· ★**实测佐证**: `grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ **0** ⇒ ★**`TS_RTN` 这个网在网表里已经完全不存在了** ★

★★**★为什么这不能靠"提醒大家注意"解决 (★方法论, 值得记★)** ★★:
· ★**同一个接口有 5 套 pin map ⇒ 每套都能被单独引用 ⇒ 引用者不知道自己引的是哪一套** ★
· ⇒ ★**真解法 = 全部收敛到唯一真源 (网表), 且【收敛这件事本身要能被机器查出来】**
  ⇒ ★**ISS-136 已经把"规格表 vs 网表"变成一道会红的闸 (Q6)** ★
  ⇒ ★**但 Q6 只查 §5.2 一张表 ⇒ 其余 4 处不在闸的覆盖里 ⇒ 这 4 处必须收敛, 收完还要把覆盖范围扩大** ★

★★**★一条关键的上下游关系 (★实测, 差点踩坑★)** ★★:
· ★**`state/gen_netlist.py` (第 1347-1356 行) 的 P10 充电板页数据来自 `state/p10_rows.json`**
  ⇒ ★**`state/p10_rows.json` 才是真上游, `HW/CHARGE_BOARD_SPEC.md` §7 那块 csv 只是它的镜像副本** ★
· ★**我实测 `state/p10_rows.json` (2026-11-03 09:23) 已经是网表口径** (★TS_BAT→J_CHG pin8 ·
  PWR_GOOD→pin6 · CHG_STAT→pin5 · pin9/10 留空不接 (I2C 不跨铰链)★)
  ⇒ ★**所以 §7 那块是【过期副本】, 照 p10_rows.json 改它 ⇒ 网表不会变** ★
  ⇒ ★**`state/p10_rows.json` 一个字都不许动 (md5 c2dc73fe…)** ★

★★**落盘纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (width=200, ★实测当前文件就是这个排版★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只新增 ISS-199 / ISS-200 两条, 一条旧记录都不许改** ★
⑤ 不动任何子总工的分片 · 不动板/网表/原理图/BOM

★★**边界**: 板/网表/原理图/BOM 一个字节不动 · 不发邮件 · 不联系供应商/原厂 · 不替老板拍板
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
TODAY = "2026-11-12"
WIDTH = 200  # ★实测: 当前文件就是 advance.py --apply 用 width=200 写的★

TRUTH = (
    "`pin1/2=BAT_CHG` · `pin3/4=GND` · `pin5=CHG_STAT` · `pin6=PWR_GOOD` · "
    "**`pin7=NC`** · **`pin8=TS_BAT`** · **`pin9/10=HINGE_RSV`**"
)

BRIEF_199 = """★**目标**: 把 HW 侧**还剩下的 4 处 J_CHG pin map 第二口径**全部收敛到网表真源 ⇒ ★**同一个接口不许再有第 5 套 pin map** ★

★**为什么现在做 (★main 2026-11-12 01:4x 实测, 不是推测★)**
· ★**ISS-136 刚交卷并被我验收签字** (★main 独立复核: `HW/check_bq25896_pinout.py` rc=0 ·
  `state/gate_check.py` rc=0 (【Q1】18/18 + 【Q6 硬件真源闸】✅ 在跑) · 板/网表/pins 一字未变 ·
  §5.2 那张表我逐脚对拍过网表一致★)
  ⇒ ★**它定的口径 = 「网表是唯一真源, 文档是它的镜像」** ★
· ★**但它只改了 `HW/CHARGE_BOARD_SPEC.md` §5.2 一张表 (★那是它的地界★) ⇒ 我今晚扫全树, HW 侧还有 4 处在用旧口径** ★★:
  ① `HW/CHARGE_BOARD_SPEC.md` §5.1 过铰链线表 (第 399/402/403/406/407 行) ——
     ★**第 3 行写 "VBUS_DET 中点 → J_CHG pin8" · 第 4 行 "CHG_STAT → pin6" · 第 5 行 "PWR_GOOD → pin7" ·
     第 8 行 "TS → pin5" · 第 9 行 "BQ25896 I2C → J_CHG pin9/pin10"** ★ ⇒ 与网表错位
     (★**另**: 第 400 行那条 "2026-11-02 订正 (ISS-136)" 注记本身也已过期 —— 它还写着 "pin7=VBUS_DET / pin10=TS 专用回流"★)
  ② `HW/CHARGE_BOARD_SPEC.md` §7 的 P10 csv 镜像块 (第 549-584 行里 J_CHG 跨铰链那些行) ——
     ★**同一套旧 pin map 又抄了一遍** ★
  ③ `HW/J_CHG_SELECTION.md` 第 30 行 (C-2 行) + 第 196 行 —— ★**pin7=VBUS_DET · pin10=TS 专用回流** ★
  ④ `HW/POWER_SHUTDOWN_V3.md` 第 129 行 —— ★**"TS 专用回流 (J_CHG pin10 + R_TS_PULL/R_NTC_BAT 下端改接 TS_RTN)"** ★
· ★**实测佐证**: `grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ **0** ⇒ ★**`TS_RTN` 这个网在网表里已经完全不存在了**
  (2026-11-03 撤除) ⇒ ★**凡是还把它当"当前口径"写的地方, 都是过期口径** ★

★**真源 (★我已逐脚对拍过网表; 你不要照抄题单, 自己再复算一遍并写清依据★)**
★**""" + TRUTH + """** ★
★**依据**: `HW/netlist_v1.csv` 逐脚 net 名 ★ + `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 已定版) ★
★**★一条容易踩的坑 (★别删错★)**: ★**`VBUS_DET` 本身没废** —— 它在网表里还有 **9 处**, 是**主板本地**的分压网
(`VBUS_DET_D` / `_D1` / `_D2`, SoM 检测脚) ⇒ ★**过期的是「VBUS_DET 跨铰链走 J_CHG pin7/pin8」这句话, 不是 VBUS_DET 这个网** ★
⇒ ★**订正时只改"走哪一脚 / 是否跨铰链", 不许把 VBUS_DET 本地分压的描述一起删掉** ★

★**★一条关键的上下游关系 (★实测, 差点踩坑★)**: ★**`state/gen_netlist.py` (第 1347-1356 行) 的 P10 页数据来自
`state/p10_rows.json`** ⇒ ★**`state/p10_rows.json` 才是真上游, §7 那块 csv 只是它的镜像副本** ★
· ★**我实测 `state/p10_rows.json` 已经是网表口径** (★TS_BAT→J_CHG pin8 · PWR_GOOD→pin6 · CHG_STAT→pin5 ·
  pin9/10 留空不接 (I2C 不跨铰链)★) ⇒ ★**所以 §7 那块是【过期副本】, 照 `state/p10_rows.json` 改它 ⇒ 网表不会变** ★
· ⇒ ★**`state/p10_rows.json` 一个字都不许动 (md5 `c2dc73fe1e9fbd8edec68828dec81c36`)** ★

★**做法**
① ★**先自己复算**: 把上面 4 处的原文抄出来 + 逐脚对拍网表 (★§7 那块对着 `state/p10_rows.json` 对拍★)
   ⇒ 写清"每处哪里错、错在哪一脚"
② ★**按网表真源订正那 4 处** (★**只改 pin map / 跨铰链归属的说法; 不许改判据阈值、不许改几何数字、不许重写整章**★)
③ ★**§5.1 那个"2026-11-02 订正"注记本身也要改** (★它现在还在传播 pin7=VBUS_DET / pin10=TS 专用回流★)
④ ★**每处订正后加一句注记**: 注明"★已按网表真源订正 (ISS-199 · 2026-11-12)★" ⇒ ★**别让人再以为这是当前口径** ★

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 HW/check_bq25896_pinout.py     # rc=0 (★真源闸, 不许变红★)
python3 state/gate_check.py            # rc=0, 【Q1】必须 18/18
python3 state/merge.py                 # rc 必须 0
grep -n "TS_RTN" HW/CHARGE_BOARD_SPEC.md HW/J_CHG_SELECTION.md HW/POWER_SHUTDOWN_V3.md
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb state/p10_rows.json
```
★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ·
`state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36` ⇒ ★**三者必须一字未变** ★
★**`grep TS_RTN` 的期望**: ★**允许剩下【历史沿革说明】与【已订正注记】里的提及, 但不许有【当前口径断言】里的 TS_RTN** ★
⇒ ★**逐行看, 说不清哪一行属于哪一类 = 没做完** ★

★**交卷 ≤ 20 行** (结论先行 + ★**逐处列出"改前 → 改后"** + 你的复算依据 + 逐条复现命令输出)

★**边界 (不许越)**
· ★**只写**: `HW/CHARGE_BOARD_SPEC.md` (★**只许动 §5.1 那张表 + §5.1 那条订正注记 + §7 的 P10 csv 镜像块里 J_CHG 跨铰链相关的行**★)
  + `HW/J_CHG_SELECTION.md` (★**只许动第 30 行与第 196 行的 pin map**★) + `HW/POWER_SHUTDOWN_V3.md` (★**只许动第 129 行**★)
  + `HANDOFF/` 下交卷报告 + ★**必要时** `state/fragments/hw.yaml` (走 `state/frag_write.py`; ★只许新增条目, 不许删改别人的 key★)
· ★**不许碰**: `HW/CHARGE_BOARD_SPEC.md` §5.2 (第 409-426 行, ★**ISS-136 已定版, 一个字都不许动**★)
  · §5.2 下面那张 ISS-112 历史快照对照表 (第 430-446 行, ★**已加注记, 不许再动**★)
  · `HW/CHARGE_BOARD_SPEC.md` 第 144 行那条 §2.2 的 PGND/TS_RTN 记述 (★**超出本单地界, 只报不改**★)
  · `state/p10_rows.json` (★**真上游, 已是对的, 不许动**★) · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv`
  · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · `HW/check_bq25896_pinout.py` (★**含它的历史注释**★)
  · 任何 `state/gen_*.py` · `MECH/` 下任何文件 (★**那是 ISS-200 的地界**★) · `PROJECT_TRACKER.md` §0
  · **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**★)
· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标
"""

BRIEF_200 = """★**目标**: 把**结构侧**的 J_CHG pin map 旧口径收敛到网表真源 ⇒ ★**结构侧的接口契约不许和网表对着干** ★

★**为什么现在做 (★main 2026-11-12 01:4x 实测, 不是推测★)**
· ★**ISS-136 (hw-lead) 刚交卷并被我验收签字** ⇒ ★**口径已定: 网表是唯一真源, 文档是它的镜像** ★
· ★**hw-lead 按纪律把结构侧那处旧口径登记成 need 转给我 (它不许代改你的地界)**, 我今晚扫全树, 结构侧有 2 处还在用旧口径:
  ① ★**`state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map`** (第 1848-1851 行)
     —— ★**现值 = `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=VBUS_DET,8=TS,9=RSV,10=TS_RTN`** ★
     ⇒ ★**其中 pin7 与 pin10 与网表对不上** ★
  ② ★**`MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块** (第 283-291 行)
     —— ★**它整块还是 1×6 @1.27mm 的老座口径**: "网表 pin1=SYS / 2=VBUS_DET / 3=BAT_DET / 4=CHG_STAT /
     5=PWR_GOOD / 6=GND" ★ ⇒ ★**而且它下面 5 条结论 (防呆 / 载流 / "J_CHG 没有电池脚" / 检测线跨铰链) 全是从这个老 6 脚 map 推出来的** ★
· ★**实测佐证**: `grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ **0** ⇒ ★**`TS_RTN` 这个网在网表里已经完全不存在了** ★

★**真源 (★我已逐脚对拍过网表; 你不要照抄题单, 自己再复算一遍并写清依据★)**
★**""" + TRUTH + """** ★
★**依据**: `HW/netlist_v1.csv` 逐脚 net 名 ★ + `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 已定版) ★
★**★别把 `VBUS_DET` 这个网整个删掉**: 它在网表里还有 9 处, 是**主板本地**的分压网 (`VBUS_DET_D` / `_D1` / `_D2`)
⇒ ★**过期的是「它跨铰链走 J_CHG pin7/pin8」这句话** ★

★**做法**
① ★**先自己复算**: 把上面 2 处的原文抄出来 + 逐脚对拍网表 ⇒ 写清"每处哪里错、错在哪一脚"
② ★**订正 `state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map`**:
   ★**value / note / ref 三件都要改** ⇒ ★**value 写成上表那套逐脚口径; note 里那句 "pin10 = TS 专用回流 (偏差 0.44-0.99°C → <0.01°C)"
   必须改掉** (★`TS_RTN` 在网表里 0 次出现★) ⇒ ★**ref 指到 `HW/netlist_v1.csv` + `HW/CHARGE_BOARD_SPEC.md` §5.2** ★
   ★★★**写法纪律 (★容易踩坑★)**: ★**`state/frag_write.py --add-claim` 是【追加】不是【改写】** ⇒ ★**它会把 `j_chg_pin_map` 变成两条
   (★key 重复 ⇒ 合并时判成口径冲突★) ⇒ ★**你必须照 `MECH/_frag_update_iss092.py` 的范式写 `MECH/_frag_update_iss200.py`:
   `from frag_write import update_fragment` → 在 `interface_claims` 列表里**按 key 定位后替换那一条** → 原子写回**
   (★**禁 `open(p,"w")`**★) ★★★
③ ★**订正 `MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块**:
   · ★**pin map 那几行 ⇒ 改成现行 10p 逐脚口径** ★
   · ★**凡结论是从老 6 脚 map 推出来的 (防呆 / 载流 / "J_CHG 没有电池脚" / 检测线跨铰链) ⇒ 一律改成现行口径,
     或明确标注 "★旧 6 脚口径, 已作废 (ISS-085 已改 1×10p@0.5mm)★" ★**不许留着一半新一半旧让人误读** ★
   · ★**不许改任何结构几何数字** (pitch / 座体尺寸 / 板宽 / 铰链尺寸 一律不动) ★
④ ★**若你发现结构侧还有别的文档残留旧 pin map ⇒ 只报给我, 不许顺手改** (★越界就是错★)

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 state/merge.py                 # rc 必须 0 (★冲突 0★)
python3 state/gate_check.py            # rc=0, 【Q1】必须 18/18
grep -n "TS_RTN" MECH/USB_HINGE_STRUCTURE.md state/fragments/mech.yaml
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb state/p10_rows.json
```
★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ·
`state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36` ⇒ ★**三者必须一字未变** ★
★**`grep TS_RTN` 的期望**: ★**只许剩【历史沿革说明】里的提及, 不许有【当前口径断言】里的 TS_RTN** ★
★**另外自查**: ★**`state/fragments/mech.yaml` 里 `j_chg_pin_map` 必须仍然只有【一条】 (★不许出现 key 重复★)** ★

★**交卷 ≤ 20 行** (结论先行 + ★**逐处列出"改前 → 改后"** + 你的复算依据 + 逐条复现命令输出 + ★**明确写"改完了"还是"要 main 裁决"** ★)

★**边界 (不许越)**
· ★**只写**: `state/fragments/mech.yaml` (★**只许动 `interface_claims.j_chg_pin_map` 这一条 + 新增 need/artifact 条目**★)
  + `MECH/USB_HINGE_STRUCTURE.md` (★**只许动 §5.2 的 `J_CHG` 块**★) + `MECH/_frag_update_iss200.py` (你自己的分片更新脚本)
  + `HANDOFF/` 下交卷报告
· ★**不许碰**: `HW/` 下任何文件 (★**那是 ISS-199 的地界**★) · `state/p10_rows.json` · `HW/netlist_v1.csv`
  · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · 任何 `state/gen_*.py` · `state/issue_log.yaml`
  (★**改 issue 状态是 main 的活**★) · `PROJECT_TRACKER.md` §0 · **别人的分片** · ★**MECH 侧其它任何结构几何数字** ★
· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标
"""


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc["issues"]

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要新增的两条, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc, width=%d) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)" % WIDTH)
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        existing = {x.get("id") for x in issues}
        for iid in ("ISS-199", "ISS-200"):
            if iid in existing:
                print("★%s 已存在 ⇒ 拒绝写 (防重复开单)" % iid)
                return 2

        issues.append({
            "id": "ISS-199",
            "title": ("★★J_CHG pin map 在 HW 侧还有 4 处第二口径 (ISS-136 只改了 §5.2 一张表) ⇒ "
                      "§5.1 过铰链线表 + §7 的 P10 csv 镜像块 + `J_CHG_SELECTION.md` ×2 + `POWER_SHUTDOWN_V3.md` ×1 "
                      "全部与网表漂移 ⇒ 按「网表=唯一真源」收敛"),
            "severity": "medium",
            "owner": "hw-lead",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-14",
            "status": "open",
            "task_brief": BRIEF_199,
        })
        issues.append({
            "id": "ISS-200",
            "title": ("★★J_CHG pin map 在结构侧还有 2 处第二口径 ⇒ `state/fragments/mech.yaml` 的 "
                      "`interface_claims.j_chg_pin_map` (pin7=VBUS_DET / pin10=TS_RTN) + "
                      "`MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块 (整块还是 1×6@1.27mm 老座) ⇒ 收敛到网表真源"),
            "severity": "medium",
            "owner": "mech-lead",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-13",
            "status": "open",
            "task_brief": BRIEF_200,
        })

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        atomic_write(LOG, out)
        print("✅ 新开 ISS-199 (hw-lead · due 11-14) + ISS-200 (mech-lead · due 11-13)")
        print("   issue_log.yaml %d B → %d B (只新增两条, 其余一字未动)" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
