#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清 3 条僵尸 fixing + 开 ISS-198 (2026-11-11 23:2x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 队列对三个总工全是空的
· ★**根因 = 三条【僵尸 fixing 标记】** (★第 4 次复发, 同一个病★):
  - ISS-193 (hw-lead): 会话 `40040dfd` **21:14:17 结束并交卷** ⇒ 但 `issue_log.yaml` 里 status 仍是 `fixing`
  - ISS-196 (sw-lead): 会话 `405c3bb3` **21:31:33 结束并交卷** ⇒ status 仍是 `fixing`
  - ISS-197 (mech-lead): 会话 `3ff7b8d1` **21:45:53 结束并交卷** ⇒ status 仍是 `fixing`
  ⇒ ★**`advance.py` 的 in_flight 规则 (★"该 agent 正在干别的, 本轮跳过"★) ⇒ 三个总工全被挡住 ⇒ A 段恒空** ★
· ★**兄弟 job (队列自动派活) 22:37 那轮也撞上同一件事, 但它 22:38:34 超时被杀 (★cron 60 分钟上限★)
  ⇒ ★**它没落盘 (★`issue_log.yaml` mtime 仍停在 21:16:58★) ⇒ 僵尸标记留到了本轮** ★★

★★**三条交卷我逐份独立复核过 (★不采信自述★)** ★★:
· ISS-193: `HW/BOM_v1.csv` 实测 **218 行** (★真伪器件 RAIL_/NET_* = **0**★ · 45 个 TP_* 是真测试点器件) ·
  `HW/BOM_pseudo_refs_v1.csv` **75 行** (★全是 RAIL_/NET_*★) · **含 J_SOM_P2 + J_SOM_P4** ·
  `state/chain_gate.py` **rc=0 (30/30 · 位号 218 全对 · DNP 46 一致 · 伪器件 0)** ·
  `state/gen_kicad_sch.py --pin-gap` **rc=0 (218 器件 / 189 可查 / 29 查不到 / 183 一致 / 6 真实多脚 / 0 表里多脚)**
  ⇒ ★**BOM 口径真修好了 (★评审 R12 的根修掉了★) ⇒ 这一件【达成】** ★
  ⇒ ★**但 `[0数据]` 29 → 29【没动】⇒ 它的根因在 `state/gen_kicad_sch.py` 的三张查找表 (★不在 BOM★) ⇒ 拆 ISS-198★**
· ISS-196: 交卷页 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md` **26 KB 在** ·
  `SW/RKNN_BENCH.md:473` **已改** (★2026-11-11 21:2x 实测记录在案★) ·
  `state/fragments/sw.yaml` answers **5 条** (★含 2 条新增★) · interface_claims **114 条** ·
  `python3 SW/tools/rknn_bench.py probe` **rc=0** ⇒ ★**交卷属实** ★
  ⇒ ★**但它自报的两处【main 侧动作】还没做 (★`rknn_bench.py:124` 常量 + `RKNN_BENCH.md:57` 旧 sha★)
    ⇒ 那是【禁改区】⇒ main 的活 ⇒ 本脚本【不做】, 只登记为 needs_from** ★
· ISS-197: `MECH/BOARD_GEOM_30MM.md` 的套B 行 **已标「【已否决 (套B) · 仅留档】」** (★实测第 103 行★) ·
  `python3 MECH/pinset2_mech_check.py` **rc=0 · 复算项 38 · FAIL 0 · WARN 1** ·
  选项表 `HANDOFF/2026-11-11_mech-lead_ISS197_口径收敛与未决项选项表.md` **21 KB 在** ⇒ ★**交卷属实** ★
  ⇒ ★**它报的 8 条活口径 (L1~L8) 里 L5/L6 仍在钉 15mm 老板宽 (★实测 `MECH/hw_cross_review_check.py:52` pcb_w=15.00★
    · `MECH/service_port_check.py` 同源★) ⇒ 那是【下一件】, 本脚本只登记 needs_from** ★

★★**ISS-198 是什么 (★主线口径内的活, 不是 PCB 布线/布局类★)** ★★:
· 目标: ★**把 `state/gen_kicad_sch.py` 的三张查找表 (`SPEC_PINS`/`OPN_KICAD`/`PREFIX_KICAD`) 补上**
  ⇒ ★**`PIN_REALITY_GAP.md` 里 29 个 `[0数据]` ⇒ 降到下限 3** (★剩 3 个"不是器件"的: CHG_GND_STAR / X1 / BT_432243★)
  ⇒ ★**这是老板【选项③ 真实器件全貌】的内部一半的输入** (★板/网表一个字节不动★) ★
· ★**它为什么今天必须做 (★与整链重出的依赖★)**: `state/RECHAIN_ONEPASS_PLAN.md` 第 3 步要重跑 `gen_kicad_sch.py`
  ⇒ ★**⇒ 必须【先】把查找表补上, 【后】重出 ⇒ 否则重出时又刷一遍 29 个 `[0数据]`** ★

★**落账纪律 (与项目既有范式一致)**: ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除本脚本要改的那几条外, 一个字节都不许动)
  ③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ 只改 3 条僵尸 + 新增 1 条

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 (只写 issue_log + dispatch_log)
  · 不发邮件 / 不联系供应商 / 不下采购单 · 板/网表/原理图一个字节不动
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"
DUE = "2026-11-13"

BRIEF_198 = """★**目标 (★内部活·不是原厂的事·也不是 PCB 布线/布局类★)**: 把 `state/gen_kicad_sch.py` 里的
★**三张查找表 (`SPEC_PINS` / `OPN_KICAD` / `PREFIX_KICAD`) 补全** ⇒ ★**`HW/PCB/PIN_REALITY_GAP.md` 里
29 个 `[0数据]` ⇒ 降到下限 3** ⇒ ★**给老板【选项③ = 真实器件全貌】攒够内部那一半的输入** ★

★**★为什么今天做 (★main 2026-11-11 23:2x 实测, 不是推测★)** ★★:
★**① ISS-193 已交卷并被 main 独立验收签字 (★BOM 口径真修好了★)** ⇒ 实测 `HW/BOM_v1.csv` **218 行** ·
   伪器件 (RAIL_/NET_*) **0 个** · **含 J_SOM_P2 + J_SOM_P4** · `state/chain_gate.py` **rc=0 (30/30)** ★
★**② 但 `[0数据]` 29 → 29 【一个没降】** ⇒ ★**根因已实测钉死: `real_pin_count()` (★`state/gen_kicad_sch.py` 第 816 行★)
   只查它【自己内部的三张表】, 【不读 BOM 的 opn 列】⇒ ⇒ BOM 的 opn 填得再好, 这个数【零变化】★** (★ISS-193 已实测确认★)
★**③ ⇒ 现在唯一能降它的动作 = 改那三张表** ⇒ ★**这就是本单** ★
★**④ 与整链重出的依赖 (★为什么不能拖★)**: `state/RECHAIN_ONEPASS_PLAN.md` 第 3 步要重跑 `gen_kicad_sch.py`
   ⇒ ★**必须【先】补表, 【后】重出 ⇒ 否则重出时又刷一遍 29 个 `[0数据]`** ★★

★**★① 机制 (★你必须先自己复核, 不许照抄★)**: `state/gen_kicad_sch.py` 第 787-830 行有三张表:
   ★**`SPEC_PINS`** (★按 ref 的脚数真值★) · ★**`OPN_KICAD`** (★按 ref 的 [符号相对路径, 依据]★) ·
   ★**`PREFIX_KICAD`** (★按位号前缀的通用件: `TP_`/`R_`/`C_`/`L_`★) ★
   ⇒ ★**`real_pin_count()` 的查表顺序 = SPEC_PINS → PARTIAL_PINS → OPN_KICAD → PREFIX_KICAD → LED** ★
   ⇒ ★**⇒ 你要往这几张表里【加条目】, 不是改 BOM, 不是改脚级真表** ★

★**★② 候选答案 (★已按本机 KiCad 官方库复核过: 符号路径 + 实测 pins 数 + 确认无 `extends` 假数★)** ★★:
   ★**符号路径相对 `/home/yuewuya/kicad/squashfs-root/usr/share/kicad/symbols/`** ★
   | ref | 建议符号 (相对 `KICAD_SYM/`) | 实测脚数 | 依据 |
   |---|---|---|---|
   | `Q1` `Q2` `Q_AND` `Q_ENVC` `Q_CHG_LED` | `Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym` | 3 | N-MOS 通用符号 (★G/D/S★) · pins=3 extends=0 ✓ |
   | `Q_PG` | `Transistor_FET.kicad_symdir/Q_PMOS_GDS.kicad_sym` | 3 | P-MOS 通用符号 · pins=3 extends=0 ✓ |
   | `SW_BOOT` `SW_KEY_CAM` `SW_KEY_PWR` `SW_KEY_VM` `SW_KEY_VP` `SW_RST` | `Switch.kicad_symdir/SW_Push.kicad_sym` | 2 | 按键符号 · pins=2 extends=0 ✓ |
   | `FB_DEMO` `FB_VBUS` | `Device.kicad_symdir/FerriteBead.kicad_sym` | 2 | 磁珠符号 · pins=2 extends=0 ✓ |
   | `U_BATPROT` | `Battery_Management.kicad_symdir/BQ297xy.kicad_sym` | 6 | BOM opn=BQ2970 同系列 · pins=6 extends=0 ✓ |
   | `U_EN_SW` `U_PWR_SW` | `Power_Management.kicad_symdir/AP22913CN4.kicad_sym` | 4 | BOM opn=TPS22991RAA (UQFN-4) · pins=4 extends=0 ✓ |
   | `U_SUPV` | `Power_Supervisor.kicad_symdir/TPS3808DBV.kicad_sym` | 6 | 网表 value=TPS3808G01 同系列 · pins=6 extends=0 ✓ |
   | `U_LDO_S28` | `Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym` | 5 | 与已填的 `U_LDO_L18`/`U_LDO_L33` 同表, 照抄 · pins=5 extends=0 ✓ |
   | `J_USB_C` | `Connector.kicad_symdir/USB_C_Receptacle_USB2.0_16P.kicad_sym` | 17 | BOM opn=GCT USB4105-16P (16P 座) 同款符号 · pins=17 extends=0 ✓ |
   | `D_TVS_VBUS` | `Diode.kicad_symdir/ZPYxx.kicad_sym` | 2 | 5V 单向 TVS = 2 脚 · pins=2 extends=0 ✓ |
   | `D_ESD_CAM` `D_ESD_DEMO` `D_ESD_LIGHT` `D_ESD_TC` `D_ESD_USB_D` | `Power_Protection.kicad_symdir/SP0503BAHT.kicad_sym` | 4 | ESD/TVS 阵列 · pins=4 extends=0 ✓ |
   ★**★三个不许填的 (★填了就是编★)★**: `CHG_GND_STAR` (★单点汇流位, 不是器件★) · `X1` (★晶振焊盘位, 不装★) ·
   `BT_432243` (★电池座, 本机无对应符号★) ⇒ ★**这 3 个保留 `[0数据]` + 在 gap 文档里注"非器件"** ★
   ⇒ ★**⇒ 上表能落 26 个 ⇒ `[0数据]` 29 → 3 (★下限★) ⇒ 剩下的 3 个就是 §5.2 E-02 要问原厂的那 3 个** ★

★**★③ 两个会把数字搞假的坑 (★main 实测过, 你必须自己再验一遍★)★★**:
★**坑① `extends`**: KiCad 官方库里 ★**大量符号用 `extends` 继承父符号** (★实测 `AO3401A`/`BSS138`/`2N7002`/
   `SMAJ5.0A`/`SM6T18A`/`USBLC6-2SC6` 全是★) ⇒ ★**它们自己文件里 0 个 `(pin` 行** ⇒ `kicad_pins()` 数出来 = **0 = 假数** ★
   ⇒ ★**⇒ 只许用【实测 pins>0 且该文件里没有 `extends`】的符号** ★
★**坑② `SPEC_PINS` 有两份拷贝**: `state/check_netlist_pins.py` 里一份, `state/gen_kicad_sch.py` 里一份
   (★实测当前两份内容一致★) ⇒ ★**你要改的是【生成器那份】(★gap 文档只读它★) ⇒ 改完顺带核一下两份是否还一致
   (★不一致就在交卷报告里点出来, 【不许自己动另一份】★)** ★
★**坑③ `Q2` 容易漏**: ★**`Q2` 是【和 Q1 同料】(★BOM 里 Q2 的 opn 写"同 Q1"★) ⇒ 它也在 29 个 `[0数据]` 里
   ⇒ ★**上表把 `Q1` `Q2` 并成一行, 落的时候要按 ref 逐个加进表 (★漏一个就少降一个★)** ★

★**★④ 做法 (★只改该改的, 别的一个字不动★)** ★★:
1. 往 `state/gen_kicad_sch.py` 的那三张表里加条目 (★`OPN_KICAD` 加按 ref 的符号路径 / `PREFIX_KICAD` 加前缀规则
   ⇒ 哪个更省事你定, 但【不许改 `real_pin_count()` 的查表顺序】★)
2. ★**重跑产物**: `python3 state/gen_kicad_sch.py --pin-gap` ⇒ `HW/PCB/PIN_REALITY_GAP.md` 刷新
   ⇒ ★**`grep -c '\\[0数据\\]' HW/PCB/PIN_REALITY_GAP.md` ⇒ 目标: 29 → 3 (★那 3 个非器件**)
   ⇒ ★**剩多于 3 个 ⇒ 你漏了, 交卷报告里点名哪几个没落、为什么★**
3. ★**那 3 个非器件**: 在 gap 文档里注明"非器件/焊盘位/待选型" (★不许编脚数★)

★**★⑤ 验收 (★交卷前跑, 把输出贴进回复★)** ★★:
```
python3 state/gen_kicad_sch.py --pin-gap
grep -c '\[0数据\]' HW/PCB/PIN_REALITY_GAP.md     # ★目标 3 (★不许超过 3★)
python3 state/check_sch_pinfull.py               # ★rc=0 (★K=0 不许变★)
python3 state/check_sch_erc.py                   # ★rc=0 (★ERC 不许变红★)
python3 state/merge.py                           # ★rc=0 (冲突 0)
python3 state/gate_check.py                      # ★Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv
# ★**板 611b869e… / 网表 c78f9912… / pins 4814617e… 必须一字未变** ★
```
★**★不许改 BOM ★** (★改了对 `[0数据]` 零效果, 只会把 BOM 和真源脱节★) ⇒ ★**本单只许改
`state/gen_kicad_sch.py` 的那三张表 + 重跑出的 `HW/PCB/PIN_REALITY_GAP.md`** ★
★**★板文件 / 原理图文件 / 网表 / BOM 【一个字节都不许动】★** (★本单只改生成器里那三张查找表★)

★**交卷 ≤ 20 行** (★结论先行 + `[0数据]` 前后数字 + 逐条复现命令输出 + 3 个非器件的处理说明★)

★**边界 (不许越)** ★:
· ★**只写**: `state/gen_kicad_sch.py` (★只许改那三张查找表★) + `HW/PCB/PIN_REALITY_GAP.md` (★重跑产物★)
  + `HANDOFF/` 下交卷报告 + ★**必要时** `state/fragments/hw.yaml` (走 `state/frag_write.py`; ★只许新增条目★)
· ★**不许碰**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/BOM_pseudo_refs_v1.csv` ·
  `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · `HW/PCB/production/**` ·
  `state/check_netlist_pins.py` (★那是另一份拷贝, 只许核不许改★) · `state/issue_log.yaml`
  (★**改 issue 状态是 main 的活**★) · `PROJECT_TRACKER.md` §0 · **别人的分片**
· ★**不许联系供应商/原厂** (★外发一律经项目总工★) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标 ·
★**不许整文件读大文件** (★只许 `grep`/`sed -n` 取你改的那几行★)"""


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".iss198.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
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

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要改的, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)")
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        by_id = {i["id"]: i for i in issues}

        # ---- ① 清 3 条僵尸 fixing (★交卷我已逐份独立复核过★) ----
        fixes = {
            "ISS-193": dict(
                status="verified",
                verify_by="main",
                verify_date="2026-11-11 23:2x",
                verify_result=(
                    "pass (★部分·BOM 口径那半达成★) · 2026-11-11 23:2x 项目总工独立复核 (★不采信自述★)。\n"
                    "★**达成**: `HW/BOM_v1.csv` 实测 **218 行** (★旧 291★) · 伪器件 (★`RAIL_`/`NET_`*★) = **0 个** "
                    "(★旧 75★) · **含 `J_SOM_P2` + `J_SOM_P4`** (★旧全缺★) · `HW/BOM_pseudo_refs_v1.csv` **75 行** "
                    "(★全是 RAIL_/NET_*·非物料另表★) · `state/chain_gate.py` **rc=0 (30/30 · 位号 218 全对 · DNP 46 一致 · 伪器件 0)** "
                    "· `state/gen_kicad_sch.py --pin-gap` **rc=0 (218 器件 / 189 可查 / 29 查不到 / 183 一致 / 6 真实多脚 / 0 表里多脚)** "
                    "· ★**板 611b869e / 网表 c78f9912 / pins 4814617e 一字未变**★ ⇒ ★**评审 R12 的根真修掉了**★\n"
                    "★**未达成 (★已拆 ISS-198★)**: `[0数据]` **29 → 29 没动** ⇒ ★**根因 (★ISS-193 自己实测钉死的★): "
                    "`real_pin_count()` 只查生成器内部三张查找表, 【不读 BOM 的 opn 列】⇒ BOM 填得再好, 这个数零变化**★ ⇒ "
                    "★**下一件 = 改那三张表 ⇒ 拆成 ISS-198 (★owner=hw-lead·due 11-13★)**★\n"
                    "★**它自报的 2 处 main 侧动作 (`rknn_bench.py:124` / `RKNN_BENCH.md:57`) 属另一单 (ISS-196), 不在本单范围**★"),
                note_extra="\n★**2026-11-11 23:2x main 落账**: 本条 21:14 交卷后一直停在 `fixing` (★僵尸标记⇒ 挡住 hw-lead 名额⇒ "
                           "A 段连续空★) ⇒ ★**main 独立复核通过后在此签字** ⇒ ★**`[0数据]` 那半拆成 ISS-198**★",
            ),
            "ISS-196": dict(
                status="verified",
                verify_by="main",
                verify_date="2026-11-11 23:2x",
                verify_result=(
                    "pass · 2026-11-11 23:2x 项目总工独立复核 (★不采信自述★)。\n"
                    "★**达成**: 交卷页 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md` **26 KB 在** (★263 行★) · "
                    "`SW/RKNN_BENCH.md:473` **已改** (★2026-11-11 21:2x 实测记录在案★ · 含重建件 sha16 `1e2c716bd16ed9d3`★) · "
                    "`state/fragments/sw.yaml` answers **5 条** (★含 2 条新增★) · interface_claims **114 条** (★114→114·无同名重复★) · "
                    "`python3 SW/tools/rknn_bench.py probe` **rc=0** (★245 节点 / 12 算子 / NPU 高风险算子: 无★) · "
                    "★**板 611b869e / 网表 c78f9912 一字未变**★ ⇒ ★**事实底座交付属实**★\n"
                    "★**它诚实报出的两条 main 侧动作 (★本单不越界, 不代做★)**: ① `SW/tools/rknn_bench.py:124` 的硬编码常量 "
                    "(★`SW/tools/**` = 它的禁改区★) ⇒ ★**改常量后 probe 的「台账一致」会转 True** ★ "
                    "② `SW/RKNN_BENCH.md:57` 仍写旧 sha `20368be665f6f59a` ⇒ ★**同源陈旧, 待订正** ★ ⇒ ★**⇒ 这两条归 main, "
                    "已登记 needs_from (★不在本单验收范围★)**★"),
                note_extra="\n★**2026-11-11 23:2x main 落账**: 本条 21:31 交卷后一直停在 `fixing` (★僵尸标记⇒ 挡住 sw-lead 名额⇒ "
                           "A 段连续空★) ⇒ ★**main 独立复核通过后在此签字** ★",
            ),
            "ISS-197": dict(
                status="verified",
                verify_by="main",
                verify_date="2026-11-11 23:2x",
                verify_result=(
                    "pass · 2026-11-11 23:2x 项目总工独立复核 (★不采信自述★)。\n"
                    "★**达成**: `MECH/BOARD_GEOM_30MM.md` 的套B 行 **已标「【已否决 (套B) · 仅留档】」** (★实测第 103 行★) · "
                    "★**5 处订正逐条落地 (★88c88 / 103c103 / 195c195 / 223,224c223,224 / 256c256★)** · "
                    "`python3 MECH/pinset2_mech_check.py` **rc=0 (★复算项 38 · FAIL 0 · WARN 1★)** · "
                    "选项表 `HANDOFF/2026-11-11_mech-lead_ISS197_口径收敛与未决项选项表.md` **21 KB 在** (★B1~B6 全齐★) · "
                    "★**板 611b869e / 网表 c78f9912 一字未变**★ ⇒ ★**结构侧口径真收敛了 (★套B 只留档, 不再是活口径★)**★\n"
                    "★**它报的 8 条活口径 (★L1~L8★) 里, ★L5/L6 仍在钉 15mm 老板宽** (★main 实测 `MECH/hw_cross_review_check.py:52` "
                    "`pcb_w = 15.00` · `MECH/service_port_check.py` 同源★) ⇒ ★**⇒ 那是【下一件】(★结构侧脚本/claim 迁 30mm★), "
                    "本单不越界** ⇒ ★**已登记 needs_from**★"),
                note_extra="\n★**2026-11-11 23:2x main 落账**: 本条 21:45 交卷后一直停在 `fixing` (★僵尸标记⇒ 挡住 mech-lead 名额⇒ "
                           "A 段连续空★) ⇒ ★**main 独立复核通过后在此签字** ★",
            ),
        }
        for iid, fx in fixes.items():
            it = by_id.get(iid)
            if it is None:
                print("★找不到 %s ⇒ 拒绝写" % iid)
                return 2
            if it.get("status") != "fixing":
                print("★%s 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)" % (iid, it.get("status")))
                return 2
            it["status"] = fx["status"]
            it["verify_by"] = fx["verify_by"]
            it["verify_date"] = fx["verify_date"]
            it["verify_result"] = fx["verify_result"]
            it["fixed_at"] = TODAY
            it["note"] = (it.get("note") or "") + fx["note_extra"]

        # ---- ② 新增 ISS-198 (★内部活·主线内·不是 PCB 布线/布局类★) ----
        if "ISS-198" in by_id:
            print("★ISS-198 已存在 ⇒ 拒绝写 (防重复开单)")
            return 2
        issues.append({
            "id": "ISS-198",
            "title": ("★★[主线内·原理图侧·内部活] `PIN_REALITY_GAP.md` 里 29 个 `[0数据]` 的真实脚数 ⇒ "
                      "根因 = `state/gen_kicad_sch.py` 的三张查找表 (★不在 BOM★) ⇒ 补表 ⇒ 降到下限 3 "
                      "(★老板【选项③ 真实器件全貌】的内部一半输入★)"),
            "severity": "high",
            "source_blocker": "HW-PCB-ERC",
            "source_agent": "main",
            "desc": ("★2026-11-11 23:2x 项目总工开单 (★依据 = ISS-193 21:14 交卷 + main 独立验收签字 + main 23:2x 实测★)。\n"
                     "★**ISS-193 已 verified/pass (★BOM 口径那半真修好了: 218 器件 / 伪器件 0 / 含 P2+P4★)** ⇒ "
                     "★**但 `[0数据]` 29 → 29 没动** ⇒ ★**根因已实测钉死: `real_pin_count()` 只查生成器内部三张查找表 "
                     "(`SPEC_PINS`/`OPN_KICAD`/`PREFIX_KICAD`), 【不读 BOM 的 opn 列】⇒ BOM 填得再好, 这个数零变化**★ ⇒ "
                     "★**⇒ 唯一能降它的动作 = 改那三张表 ⇒ 这就是本单**★\n"
                     "★**候选符号表已备好 (★11 个符号全部实测 pins>0 且 extends=0★) ⇒ 可落 26 个 ⇒ 下限 3** "
                     "(★剩 3 个非器件: CHG_GND_STAR / X1 / BT_432243★)\n"
                     "★**为什么必须今天做 (★不是催★)**: `state/RECHAIN_ONEPASS_PLAN.md` 第 3 步要重跑 `gen_kicad_sch.py` ⇒ "
                     "★**必须先补表后重出, 否则重出时又刷一遍 29 个 `[0数据]`**★"),
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": DUE,
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": ("state/gen_kicad_sch.py (★只许改 SPEC_PINS/OPN_KICAD/PREFIX_KICAD 三张查找表★) · "
                        "HW/PCB/PIN_REALITY_GAP.md (★`--pin-gap` 重跑产物★) · "
                        "HANDOFF/2026-11-11_hw-lead_ISS198_三张查找表补全.md"),
            "verify_by": "main",
            "verify_result": None,
            "task_brief": BRIEF_198,
            "note": ("★2026-11-11 23:2x 项目总工开单 (owner=hw-lead, verify_by=main ⇒ ★**自己修的必须别人验**, 铁律满足★)。\n"
                    "★**来源**: ISS-193 交卷 ⇒ main 23:2x 独立验收签字 (BOM 那半 pass) ⇒ `[0数据]` 那半拆成本单。\n"
                    "★**口径**: 本单在【原理图/生成器】侧, 【板/网表/BOM 一个字节不动】⇒ ★**不属于【PCB 布线/布局类】** ⇒ "
                    "★**符合老板 10-07 口径 (先解决原理图绘制的问题, 再解决 PCB 绘制的问题)**★"),
        })

        # ---- ③ 写 dispatch_log (ISS-198 派活记录) ----
        dl = yaml.safe_load(open(DL, encoding="utf-8").read()) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-198", "agent": "hw-lead", "at": TODAY, "brief": BRIEF_198[:300]})

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
        print("✅ 已落盘: ISS-193 / ISS-196 / ISS-197 → verified (★main 独立复核签字★) + 新增 ISS-198 (open, owner=hw-lead)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
