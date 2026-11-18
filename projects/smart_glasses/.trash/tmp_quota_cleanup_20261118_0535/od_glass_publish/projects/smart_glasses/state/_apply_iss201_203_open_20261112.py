#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开单: ISS-201 (sw-lead) + ISS-202 / ISS-203 (mech-lead) —— 2026-11-12 02:0x 队列自动派活 job

★★**为什么开这三单 (★全部实测, 不是推测★)** ★★:
· ★**队列空了**: `python3 state/advance.py --json` ⇒ `internal` = **0 条** ⇒
  · sw-lead 名下 **一条 open 都没有** (★它的 17 条全是 verified/fixed★) ⇒ ★**sw-lead 完全断线** ★
  · mech-lead 名下唯一一条 ISS-200 **status=fixing**, 而它的会话 **01:5x 已经交卷结束** ⇒
    ★**会话已死但单还挂在 fixing ⇒ 这是"空占位"** ⇒ ★**下一轮 advance.py 的 in_flight 规则会一直挡着 mech-lead** ★
  · hw-lead 名下 ISS-195 = **fixing 且会话 dc510f7c 正在跑** ⇒ ★**真在飞, 不动它** ★
· ⇒ ★**本 job 的职责就是"让内部待办不断线" ⇒ 空占位必须解开, 断线的 agent 必须接上新活** ★

★★**ISS-201 (sw-lead) 为什么是它 (★ISS-196 交卷时明确交回 main 的两处补丁, 我 02:0x 亲自复跑过★)** ★★:
· ★**ISS-196 交卷报告 §3.4 A/B + §4.5 U2/U5 明写: "改完 B 之后 probe 会立刻打出「台账一致: True」", 且它把补丁交回 main** ★
  (见 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md`) ⇒ ★**这是一个已经论证完、只差三处编辑的活** ★
· ★**我 02:0x 实测的现状 (⇒ 派活前我把数字全部核过一遍)**: ★
  · `python3 SW/tools/rknn_bench.py probe` ⇒ `sha16 = 1e2c716bd16ed9d3 (台账一致: False )` ★
  · `python3 SW/tools/model_asset_check.py` ⇒ `MOD-YOLOV5S-640-ARS45-SRC` 行 **C2 ❌ 大小 / C3 ❌ sha**; 汇总 `资产 13 条 · FAIL 11`; **rc = 1** ★
  · 磁盘实物实测 = `yolov5s-sim.onnx` **29,365,856 B / 1e2c716bd16ed9d3** · `yolov5n-sim.onnx` **7,931,774 B / dfb5d060ca36fc27** ★
  ⇒ ★**台账登的是原件, 磁盘上是重建件 ⇒ 台账在冒充原件 ⇒ 这就是 ISS-196 §3.4 A 要解决的"假绿"** ★

★★**ISS-202 / ISS-203 (mech-lead) 为什么是它们 (★都是 ISS-200 与 ISS-197 交卷时"只报不改"、登记成 need 交回 main 的活★)** ★★:
· ★**ISS-202** = ISS-200 交卷时登记的两条 need (`iss200_mech_doc_residual_old_pinmap` / `iss200_mech_frag_mech_j_chg_pins_note`)
  ⇒ ★**结构侧 J_CHG 口径还有 5 处 (4 处文档 + 1 条 claim note) 没收敛** ★
· ★**ISS-203** = ISS-197 交卷时登记的 L1/L5/L6 ⇒ ★**`MECH/hw_cross_review_check.py:52` 与 `MECH/service_port_check.py:44`
  的 `pcb_w` 还钉在 15.00, 而现行板宽 = 30.00** ⇒ ★**它俩现在打的分说的不是现行板子 (ISS-192 同型问题的残留)** ★

★★**落盘纪律 (与项目既有范式一致)**: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (width=200) ③ 原子写 (tmp → fsync → os.replace → fsync(dir))
④ ★**只新增 3 条, 一条旧记录都不许改** ⑤ 不动任何子总工的分片 · 不动板/网表/原理图/BOM

★★**边界**: 板/网表/原理图/BOM 一个字节不动 · 不发邮件 · 不联系供应商/原厂 · 不替老板拍板 · ★**本 job 不许调 message 工具** ★
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
WIDTH = 200  # ★实测: 当前文件就是这个排版★

TRUTH = (
    "**`pin1/2=BAT_CHG`** · **`pin3/4=GND`** · **`pin5=CHG_STAT`** · **`pin6=PWR_GOOD`** · "
    "**`pin7=NC`** · **`pin8=TS_BAT`** · **`pin9/10=HINGE_RSV`**"
)

BRIEF_201 = """★**目标**: 把**模型资产台账 ↔ 磁盘实物 ↔ 工具硬编码常量**这条链收敛成一套 ⇒ ★**`probe` 必须打出「台账一致: True」, 且台账登记的是【重建件】而不是冒充原件** ★

★**为什么现在做 (★main 2026-11-12 02:0x 实测, 不是推测★)**
· ★**ISS-196 (你上一单) 交卷时把两处补丁明确交回给了 main (它自己的地界不许改)**: ★**§3.4 A/B + §4.5 U2/U5** ★
  (★见 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md`★) ⇒ ★**它已经把"为什么是这两处"论证完了, 你不用重推, 直接按它落** ★
· ★**我今天 02:0x 亲自复跑了一遍, 现状逐字如下 (⇒ 你要修的就是这三处, 不多不少)** ★★:
  ① ★**`python3 SW/tools/rknn_bench.py probe` 实测输出**:
     `[probe] 模型: /home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx sha16 = 1e2c716bd16ed9d3 (台账一致: False )` ★
     (★同页还打印: 节点数 245 / 12 类算子 / 输入 [1,3,640,640] / 输出 3 个 / NPU 高风险算子: 无★)
  ② ★**`python3 SW/tools/model_asset_check.py` 实测**: `MOD-YOLOV5S-640-ARS45-SRC` 那一行 ⇒
     ★**C1 ✅ 文件存在 (29365856 B)** · ★**C2 ❌ 大小 29365856 B (台账 29337706 B)** · ★**C3 ❌ sha256[:16] 1e2c716bd16ed9d3 (台账 20368be665f6f59a)** ★
     ⇒ 汇总行实测 = `资产 13 条 · FAIL 11 · WARN 9 · 重复组 1` · **退出码 rc = 1** ★
  ③ ★**磁盘实物实测 (sha256 + 字节数, 我自己算的)**:
     · `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` = **29,365,856 B / sha256[:16] = `1e2c716bd16ed9d3`** ★
     · `~/Public/radxa_yolo/acuity_pipeline/model/yolov5n-sim.onnx` = **7,931,774 B / sha256[:16] = `dfb5d060ca36fc27`** ★
     ⇒ ★**两个文件都跟台账登记的对不上 (台账写的是 29,337,706 B / `20368be665f6f59a`) ⇒ 这两个是【重建件】, 台账还停留在原件上** ★
· ★**铁律 (来自 `SW/MODEL_ASSETS.md` §1.4, 你必须照它办)**: ★**R-1 唯一 ID** (同一内容不得有两个 ID) ·
★**R-2 版本只认 sha256** (文件名里的 v2/clean/final 一律不作数) · ★**R-3 必填字段** (来源路径 / 大小 / sha256 / 许可 / 格式与格式版本 / 状态 / 角色 / 备注) ★
· ★**且 `SW/MODEL_ASSETS.md` §1.2 开头明写: 台账与脚本 `MANIFEST` 必须逐字段一致, 改一个必须改另一个 (脚本自检会 diff 大小/sha256)** ★

★**做法 (三处, 有先后顺序, 别搞反)**
**A. 登记重建件 (台账 + 脚本两处同步)**
  · ★**`SW/MODEL_ASSETS.md` §1.2 的台账表** 与 ★**`SW/tools/model_asset_check.py` 的 `MANIFEST`** ⇒ ★**两处必须逐字段一致** ★
  · 两个重建件都要登记 (★yolov5s-sim 与 yolov5n-sim 是两个不同的文件, 两个不同的 sha★)
  · 字段按 R-3 填全: 路径 / 大小 / sha256[:16] / 许可 / 格式与格式版本 / 状态 / 角色 / 备注
  · ★**原 ID `MOD-YOLOV5S-640-ARS45-SRC` 那一行的 state 必须改掉** —— ★**它登的路径和重建件是同一个路径, 不改状态就等于让台账冒充原件** ★
  · ★**★坑 (别踩)**: ★**脚本头注释 (第 96-100 行) 的状态词表只有 `candidate` / `active` / `reference` / `quarantined` / `licensing-hold` ⇒ `missing` 不是现成词** ★
    ⇒ 你要么按脚本自己的规则选词并把理由写进台账, 要么新增 `missing` 并在 ①脚本头注释词表 ②台账 §1 说明 ③脚本自检/反向用例 **三处同时加** ★
    ⇒ ★**不许拿 `quarantined` 顶替** (★quarantined = 已判死的坏模型, 与"原件丢失、路径被重建件占用"不是一回事★) ★
**B. 改工具硬编码常量 (一行)**
  · ★**`SW/tools/rknn_bench.py:124`** ⇒ `ONNX_MODEL_SHA16 = "20368be665f6f59a"` ⇒ ★**改成 `"1e2c716bd16ed9d3"`** ★
  · ★**它是模块级硬编码常量, 无 env / 无配置文件可覆盖 (ISS-196 §3.5 实测: 全文件 `os.environ` / `getenv` 命中 0)** ★
  · ★**判定式在同文件第 705 行**: `st["model_sha16_matches_ledger"] = (st["model_sha16"] == ONNX_MODEL_SHA16)` ⇒ ★**它比的是【磁盘实物 sha】, 不是台账** ★
  · ★**★顺序铁律: 必须先做 A 再做 B** ⇒ ★**只改常量不登记台账 = 假绿** (★ISS-196 §3.4 A 已明写这一点★) ★
**C. 订正文档里那一行**
  · ★**`SW/RKNN_BENCH.md:57`** ⇒ 现值 `| sha256[:16] | `20368be665f6f59a` —— **与台账一致** ✔ | [实测] |` ⇒ ★**已过期, 按 A 的定稿订正** ★
  · ★**同文件第 473 行 ISS-196 已经订正成实测真值 ⇒ 你不要重复改它, 最多追加一行 11-12 的复跑记录** ★

★**许可字段 (不许猜)**
· 两个重建件的许可用 ★**`python3 SW/tools/license_probe.py --onnx <路径> --json`** 实测 ⇒ ★**测不出来就写 `unknown` + 登记一条 need 给 main, 不许猜、不许沿用原件的 AGPL 结论** ★
· ★**`SW/MODEL_LICENSE.md` 是许可溯源档案, 只读, 不许改** ★

★**★交付集口径不许变 (★这是台账治理的命门★)**
· ★**`state` ∈ {`candidate`, `active`} 才算【交付集】** (★脚本头注释第 96-97 行★) ⇒
· ★**你新登记的重建件不许因为"文件现在能用"就进交付集** —— ★**转换链第 3 段 (ONNX→NPU 厂商格式) + 板端精度都还是 [0数据]** ★
· ⇒ ★**本单前后, 交付集条目数不许变多** ⇒ ★**交卷时把这个数字写出来 (改前 / 改后)** ★

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 SW/tools/rknn_bench.py probe          # ★期望: "台账一致: True"★ (★我 02:0x 实测是 False★)
python3 SW/tools/model_asset_check.py          # ★期望: 重建件那几行的 C1/C2/C3 全 ✅★
python3 state/merge.py                        # rc 必须 0
python3 state/gate_check.py                   # rc=0, 【Q1】必须 18/18
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```
★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ⇒ ★**两者必须一字未变** ★
★**★关于 `model_asset_check.py` 的整体 rc (★别自欺★)**: ★**其它资产还有一堆 C1「文件不存在」的 FAIL (实测 FAIL 11)★**
⇒ ★**你只要保证【重建件相关的行】全绿; 若整体 rc 仍为 1 ⇒ 如实把剩余 FAIL 明细列出来 (说明哪些与本单无关), 不许去改别人的行来凑 rc=0** ★

★**★★反向用例 (★交卷前必跑, 这是本单的判据, 不是装饰★)★★**
① 把 `ONNX_MODEL_SHA16` **临时**改回 `"20368be665f6f59a"` ⇒ ★**`probe` 必须打回 "台账一致: False"** ⇒ 立刻恢复 ⇒ 必须打回 True
   ⇒ ★**这证明它真在读磁盘文件, 不是把结果写死** ★
② 把台账里新 ID 的 sha 十六进制**临时**改一位 ⇒ ★**`model_asset_check.py` 必须报该行 C3 FAIL** ⇒ 立刻恢复
   ⇒ ★**这证明台账↔实物是真比对** ★
⇒ ★**两条的输出都要贴进回复** ★

★**交卷 ≤ 20 行** (结论先行 + ★**逐处列出"改前 → 改后"** + 你的实测依据 + 逐条复现命令输出 + ★**交付集条目数改前/改后** ★)

★**边界 (不许越)**
· ★**只写**: `SW/MODEL_ASSETS.md` (★只许动 §1.2 台账表 + §1 说明里与状态词表相关的句子★)
  + `SW/tools/model_asset_check.py` (★只许动 `MANIFEST` + 头注释状态词表 + 你新增的自检/反向用例★)
  + `SW/tools/rknn_bench.py` (★只许动第 124 行常量 + 它上面那两行注释★)
  + `SW/RKNN_BENCH.md` (★只许动第 57 行 + 必要时第 473 行追加一行复跑记录★)
  + `state/fragments/sw.yaml` (走 `state/frag_write.py`; ★只许新增 artifact / need, 不许删改别人的 key★)
  + `HANDOFF/` 下交卷报告
· ★**不许碰**: `HW/` 下任何文件 (★板 / 网表 / 原理图 / BOM★) · `SW/MODEL_LICENSE.md` · `SW/tools/` 下别的脚本
  · `SW/RKNN_BENCH.md` 除第 57 / 473 行以外的内容 · `state/issue_log.yaml` (★改 issue 状态是 main 的活★)
  · `PROJECT_TRACKER.md` §0 · **别人的分片** · ★**不许动磁盘上那两个 `.onnx` 文件本体** ★
· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标
"""

BRIEF_202 = """★**目标**: 把**结构侧剩下的 J_CHG 旧口径 (4 处文档 + 1 条分片 claim 的 note)** 收敛到网表真源 ⇒ ★**同一个接口不许再有第 3 套 pin map** ★

★**为什么现在做 (★main 2026-11-12 02:0x 实测, 不是推测★)**
· ★**ISS-200 昨天 01:5x 刚交卷** ⇒ ★**它把 `MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块 + `state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map` 这两处收敛了** ★
· ★**但它按纪律【只报不改】, 把结构侧剩下的 5 处登记成 need 交回给 main** ⇒ ★**那两条 need 的键名就在你的分片里**:
  ★**`iss200_mech_doc_residual_old_pinmap`** 与 ★**`iss200_mech_frag_mech_j_chg_pins_note`** ⇒ ★**本单就是把那两条 need 做掉** ★
· ★**实测佐证 (我 02:0x 自己跑过)**: ★**`grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ 0** ⇒ ★**`TS_RTN` 这个网在网表里已经完全不存在了 (2026-11-03 撤除)** ★

★**真源 (★我已逐脚对拍过网表; 你不要照抄题单, 自己再复算一遍并写清依据★)**
★**""" + TRUTH + """** ★
★**依据**: ★**`HW/netlist_v1.csv` 逐脚 net 名** ★ + ★**`HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 已定版)** ★
★**★别把 `VBUS_DET` 这个网整个删掉**: 它在网表里还有 9 处, 是**主板本地**的分压网 ⇒ ★**过期的是「它跨铰链走 J_CHG pin7/pin8」这句话** ★

★**本单要改的 5 处 (★全部在结构侧地界内★)**
① ★**`MECH/USB_HINGE_STRUCTURE.md` §5.1 那张表** 的 J_CHG 行 ⇒ ★**现值写「6 (1×6 @1.27) / 触点区宽 6.35 mm / 座体宽 8.35 mm」= 老 6 脚口径** ★
② ★**同文件 §5.3 C-4** ⇒ ★**现值仍写「J_CHG → 8p @0.5」, 现行是 1×10p @0.5mm** ★
③ ★**同文件 §5.3 C-1 尾巴** ⇒ ★**现值仍写「SYS 单触点载流下降 → 用 2 脚并联解决」, 现行跨铰链载流是 BAT_CHG, SYS 根本不跨铰链** ★
④ ★**同文件 F-5 / F-6 的「SYS ↔ GND 反插短接」措辞** ⇒ ★**那是老 6 脚口的防呆结论** ★
   (★**ISS-200 交卷时实测的反插真相**: 180° 翻转 = pin i ↔ pin 11-i ⇒ BAT_CHG 落到 HINGE_RSV = 断路不短接;
     真实风险是 ★**GND(pin3) ↔ TS_BAT(pin8)** + ★**CHG_STAT(pin5) ↔ PWR_GOOD(pin6)**★) ★
⑤ ★**`state/fragments/mech.yaml` 的另一条 claim `mech_j_chg_pins` 的 note** ⇒
   ★**现值仍断言「pin8=TS · pin9=RSV · pin10=TS 专用回流」⇒ pin10 这一句现在是错的 (现行 pin10 = HINGE_RSV)** ★
   ⇒ ★**注意: `interface_claims.j_chg_pin_map` 那一条 ISS-200 已经改好了 ⇒ 你只许动 `mech_j_chg_pins` 这一条, 不许把上一单改好的那条改回去** ★

★**做法**
① ★**先自己复算**: 把上面 5 处的原文抄出来 + 逐脚对拍网表 ⇒ 写清"每处哪里错、错在哪一脚"
② ★**订正那 4 处文档** (★**只改 pin map / 跨铰链归属 / 防呆措辞; 不许改任何结构几何数字 (pitch / 座体尺寸 / 板宽 / 铰链尺寸 一律不动)★**)
③ ★**订正分片里 `mech_j_chg_pins` 的 note** (★**走 `state/frag_write.py`, 禁 `open(p,"w")`★)
   ★★★**写法纪律 (★容易踩坑★)**: ★**`state/frag_write.py --add-claim` 是【追加】不是【改写】** ⇒ ★**它会让 `mech_j_chg_pins` 变成两条 (★key 重复 ⇒ 合并时判成口径冲突★)** ★
   ⇒ ★**你必须照 `MECH/_frag_update_iss200.py` 的范式写 `MECH/_frag_update_iss202.py`:
   `from frag_write import update_fragment` → 在 `interface_claims` 列表里**按 key 定位后替换那一条** → 原子写回** ★
④ ★**每处订正后加一句注记**: 注明"★已按网表真源订正 (ISS-202 · 2026-11-12)★" ⇒ ★**别让人再以为这是当前口径** ★
⑤ ★**若你发现结构侧还有别的残留 ⇒ 只报给我, 不许顺手改** (★越界就是错★)

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 state/merge.py                 # rc 必须 0 (★冲突 0★)
python3 state/gate_check.py            # rc=0, 【Q1】必须 18/18
grep -n "TS_RTN" MECH/USB_HINGE_STRUCTURE.md state/fragments/mech.yaml
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```
★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ⇒ ★**两者必须一字未变** ★
★**`grep TS_RTN` 的期望**: ★**只许剩【历史沿革说明】与【已订正注记】里的提及, 不许有【当前口径断言】里的 TS_RTN** ★ ⇒ ★**逐行看, 说不清哪一行属于哪一类 = 没做完** ★
★**另外自查**: ★**`state/fragments/mech.yaml` 里 `j_chg_pin_map` 与 `mech_j_chg_pins` 必须各仍然只有【一条】 (★不许出现 key 重复★)** ★

★**交卷 ≤ 20 行** (结论先行 + ★**逐处列出"改前 → 改后"** + 你的复算依据 + 逐条复现命令输出)

★**边界 (不许越)**
· ★**只写**: `MECH/USB_HINGE_STRUCTURE.md` (★**只许动上面 ①-④ 那 4 处**★)
  + `state/fragments/mech.yaml` (★**只许动 `interface_claims.mech_j_chg_pins` 这一条 + 新增 need/artifact 条目**★)
  + ★**新建** `MECH/_frag_update_iss202.py` (你自己的分片更新脚本) + `HANDOFF/` 下交卷报告
· ★**不许碰**: `HW/` 下任何文件 (★**那是 ISS-199 的地界**★) · `MECH/USB_HINGE_STRUCTURE.md` §5.2 (★**ISS-200 已定版, 一个字都不许动**★)
  · `state/p10_rows.json` (★**真上游, 已是对的**★) · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv`
  · `HW/PCB/demo_mainboard.kicad_pcb` · 任何 `state/gen_*.py` · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**★)
  · `PROJECT_TRACKER.md` §0 · **别人的分片** · ★**MECH 侧其它任何结构几何数字** ★
· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标
"""

BRIEF_203 = """★**目标**: 把**结构侧两个还在给「15mm 板」打分的机械复核器**迁到**现行 60×30 板** ⇒ ★**现在的绿灯/红灯说的不是现行板子, 这是假判据** ★

★**为什么现在做 (★main 2026-11-12 02:0x 实测, 不是推测★)**
· ★**ISS-197 (你上一单) 交卷时全仓扫出 8 条「活口径」(L1~L8), 其中 L5 / L6 就是本单** ⇒ ★**它当时只报不改, 登记成 need 交回给 main** ★
· ★**我 02:0x 亲自 grep 复核了 (逐行原文)**:
  · ★**`MECH/hw_cross_review_check.py:52` ⇒ `"pcb_w": 15.00,   # 主 PCB 板宽 [决策 10-27]`** ★
  · ★**`MECH/service_port_check.py:44` ⇒ `"pcb_w": 15.00,   # 老板拍板 15mm`** ★
  ⇒ ★**两个脚本的板宽常量还钉在 15mm** ★
· ★**现行板宽 = 30.00mm (权威表 `MECH/BOARD_GEOM_30MM.md` §2: 「板宽 Y = 30.00mm · 老板 10-29 19:16 拍板」)** ★
  ⇒ ★**`hw_cross_review_check.py` 的 `pcb_w` 驱动着 54 项判定 (★我 02:0x 自己跑过: 汇总「PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 (共 54 项)」, rc=0★)** ★
  ⇒ ★**ISS-197 当时给的口径是: 迁到 30mm 后 V 链余量会从 17.00 掉到 2.00 ⇒ 会翻红** ⇒ ★**这个数你要自己复算, 不许照抄** ★
· ★**同域还有 2 条活 claim 是旧板长口径** (★ISS-197 交卷时登记为 L1★): ★**`state/fragments/mech.yaml` 的 `interface_claims.mainboard_len_carrier` = 69mm · `mainboard_len_direct` = 76mm** (★现行板长 = 60.00mm★) ★

★**做法**
① ★**先自己复算**: 把两个脚本里**所有**引用 `BASE["pcb_w"]` 的判定项列出来 (★`MECH/hw_cross_review_check.py` 里至少第 195 / 197 / 225 / 228 / 229 / 242 / 250 / 261 / 271 行★)
   ⇒ 写清"★哪几项会因 15 → 30 而改判、改成什么★"
② ★**把两个脚本的 `pcb_w` 迁到 30.00, ★同时把注释里「老板拍板 15mm / [决策 10-27]」一起改掉** (★否则下一个人照注释又走回 15mm★)
③ ★**逐项输出「改前 → 改后 + 为什么」** (★不许只说"迁完了"★)
④ ★**★判据不许为了变绿而放宽★** ⇒ ★**任何阈值 (余量 / 间距 / keepout / 判废线) 一律不许动** ★
   ⇒ ★**若迁到 30mm 后某项真的 FAIL ⇒ 那是真 FAIL, 如实留在输出里, 并登记 need 给 main** (★不许降级成 WARN/说明来凑绿★) ★
⑤ ★**那 2 条板长 claim (`mainboard_len_carrier` / `mainboard_len_direct`) 的值不许你自己拍** ⇒
   ★**板长以 `MECH/BOARD_GEOM_30MM.md` §2 为准; 若这两条 claim 的含义与该表不一致 ⇒ 只报给我, 不许改值** ★

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 MECH/hw_cross_review_check.py      # rc=0, ★汇总行必须逐项列出改前/改后★
python3 MECH/service_port_check.py          # rc=0
python3 state/merge.py                      # rc 必须 0
python3 state/gate_check.py                 # rc=0, 【Q1】必须 18/18
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
```
★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` ⇒ ★**两者必须一字未变** ★
★**★反向用例 (交卷前必跑)★**: 把 `pcb_w` **临时**改回 15.00 ⇒ ★**汇总读数必须回到迁移前那一版 (PASS 14 / FAIL 17 / 条件通过 8 / 说明 15, 共 54 项)★**
⇒ 立刻恢复 ⇒ 必须回到迁移后的读数 ⇒ ★**这证明它真在读这个常量, 不是把结果写死** ★

★**交卷 ≤ 20 行** (结论先行 + ★**逐项「改前 → 改后」** + 你的复算依据 + 逐条复现命令输出 + ★**明确写"改完了"还是"要 main 裁决"** ★)

★**边界 (不许越)**
· ★**只写**: `MECH/hw_cross_review_check.py` (+ 它自己生成的产物) + `MECH/service_port_check.py` (+ 它自己生成的产物)
  + `state/fragments/mech.yaml` (走 `state/frag_write.py`; ★只许新增 need / artifact, 不许删改别人的 key★)
  + `HANDOFF/` 下交卷报告
· ★**不许碰**: `MECH/BOARD_GEOM_30MM.md` (★**结构侧权威表, 只许引用不许改★)
  · `MECH/pinset2_mech_check.py` (★**ISS-192 已迁过并定版, 不许动★**) · `MECH/USB_HINGE_STRUCTURE.md` (★那是 ISS-202 的地界★)
  · `HW/` 下任何文件 (★板 / 网表 / 原理图 / BOM★) · 任何 `state/gen_*.py` · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**★)
  · `PROJECT_TRACKER.md` §0 · **别人的分片** · ★**任何几何阈值数字** ★
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

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要新增的三条, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc, width=%d) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)" % WIDTH)
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        existing = {x.get("id") for x in issues}
        for iid in ("ISS-201", "ISS-202", "ISS-203"):
            if iid in existing:
                print("★%s 已存在 ⇒ 拒绝写 (防重复开单)" % iid)
                return 2

        issues.append({
            "id": "ISS-201",
            "title": ("★★★[demo OD 关键路径·台账治理] 模型资产台账登的是【原件】, 磁盘上是【重建件】 ⇒ "
                      "`probe` 永远打「台账一致: False」⇒ ISS-196 交卷时交回 main 的两处补丁 (rknn_bench.py:124 常量 + "
                      "MODEL_ASSETS/model_asset_check 台账登记重建件新 ID) + RKNN_BENCH.md:57 的旧 sha ⇒ 收敛成一套"),
            "severity": "medium",
            "owner": "sw-lead",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-13",
            "status": "open",
            "task_brief": BRIEF_201,
        })
        issues.append({
            "id": "ISS-202",
            "title": ("★★J_CHG pin map 在结构侧还有 5 处第二口径 (ISS-200 只改了 §5.2 + `j_chg_pin_map` 一条) ⇒ "
                      "`MECH/USB_HINGE_STRUCTURE.md` §5.1 表 + §5.3 C-4 + §5.3 C-1 尾巴 + F-5/F-6 防呆措辞 + "
                      "`mech.yaml` 的 `mech_j_chg_pins` note (仍写 pin10=TS 专用回流) ⇒ 收敛到网表真源"),
            "severity": "medium",
            "owner": "mech-lead",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-14",
            "status": "open",
            "task_brief": BRIEF_202,
        })
        issues.append({
            "id": "ISS-203",
            "title": ("★★★[假判据·ISS-197 遗留 L1/L5/L6] 结构侧两个机械复核器还钉在 15mm 板宽 ⇒ "
                      "`MECH/hw_cross_review_check.py:52` 与 `MECH/service_port_check.py:44` 的 `pcb_w` ⇒ "
                      "迁到现行 60×30 (板宽 30.00, `MECH/BOARD_GEOM_30MM.md` §2) ⇒ 现在的绿灯说的不是现行板子"),
            "severity": "medium",
            "owner": "mech-lead",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-14",
            "status": "open",
            "task_brief": BRIEF_203,
        })

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        atomic_write(LOG, out)
        print("✅ 新开 ISS-201 (sw-lead · due 11-13) + ISS-202 / ISS-203 (mech-lead · due 11-14)")
        print("   issue_log.yaml %d B → %d B (只新增三条, 其余一字未动)" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
