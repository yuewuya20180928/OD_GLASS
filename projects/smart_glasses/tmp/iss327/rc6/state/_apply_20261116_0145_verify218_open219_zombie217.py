#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 清 1 个僵尸 fixing (ISS-217) + 落 1 个 verified (ISS-218) + 新开 1 单 (ISS-219 → mech-lead)
=========================================================================================
★**为什么这次要落账 (★2026-11-16 01:3x~01:5x 队列自动派活 job fb67af40 实测★)** ★
· ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是三个总工名额全被 `fixing` 占住 ★
· ★**逐个会话实查 (★`sessions_list` + `subagents list` 双查 + 读 transcript★)**:
  - ISS-215 (sw-lead) · `agent:sw-lead:subagent:580cc849` (db9aa514) → **status=running** ★
    (★00:42:33 起跑, 01:39 时 transcript 仍在长 ⇒ **真在飞 ⇒ 本轮不碰 sw-lead**★)
  - ISS-217 (hw-lead) · `agent:hw-lead:subagent:67ddec52` (1ec42e28) → **status=done 但 aborted** ★
    (★01:14:18 起跑, **01:29:39 被中止** (transcript 末行 = `prompt-error: This operation was aborted`)★)
    ⇒ ★**交付物 0 件**: `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 不存在 · `HANDOFF/...ISS217...md` 不存在
    ⇒ ★**`HW/check_netlist_selfconsistency.py` 的 mtime = 01:03:42 < 01:14:18 ⇒ 不是本会话碰的** (ISS-214 的产物)
    ⇒ ⇒ ★**僵尸 fixing ⇒ 回滚 open 重派** (★不采信"会话跑完了"这个状态位, 只看盘上实物★)
  - ISS-218 (mech-lead) · `agent:mech-lead:subagent:bd1e28db` (74016a46) → **status=done** (★01:30:29 交卷★)
    ⇒ ★**交付物 4 件全在盘上 + 门禁全绿 (main 自己实跑, 见 VERIFY_218★)** ⇒ ★**落 verified, 放出 mech-lead 名额** ★
· ★**放出的 mech-lead 名额 ⇒ 从 ISS-209/ISS-218 交卷里那 3 条"只报不改、已登记 need 给 main"的冲突开出第 2 轮重排单** ★
  (★兄弟 job 的口径: 开单是派活 job 的活★)

★★**ISS-219 属【原理图主线允许的结构类活】(★老板 2026-11-11 10:07 口径: PCB 布线/布局类一律排队等原理图定稿★)** ★
★★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 (板/网表/脚表/原理图/BOM) / outbox
"""
import datetime as dt
import fcntl
import hashlib
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0145_verify218_open219_zombie217"

TODAY = "2026-11-16"


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


PROTECTED = [
    "MECH/hinge_usb_check.py",
    "MECH/service_port_check.py",
    "MECH/hw_cross_review_check.py",
    "MECH/display_biosafety_v2_check.py",
    "HW/netlist_v1.csv",
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
]
MD5_BLOCK = "\n".join("· ★`%s` ★**`%s`**" % (p, md5(os.path.join(PROJ, p))) for p in PROTECTED)

# ==================================================================
# ① ISS-218 → verified (main 独立复核)
# ==================================================================
VERIFY_218 = """pass · 2026-11-16 01:4x 项目总工独立复核 (★不采信自述, 只看盘上实物 + 自己跑门禁★)
★**① 交付物 4 件 (main 自己 stat 盘上实物)** [实测]: `MECH/print/PRINT_COUPON_TIER3_SPEC.md` (26,398 B · 01:27) · `MECH/print/frame_typec_coupon_tier3_revb.stl` (21,684 B · 01:30) · `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` (15,146 B · 01:27) · `HANDOFF/2026-11-16_mech-lead_ISS218_打印包第三档与热路重量模板.md` (16,893 B · 01:28 · **B1~B6 六块齐全**★) + 分片 `state/fragments/mech.yaml` 已写 (★`iss218_mech_*` 四条 need 全部 to main★)
★**② 机器门禁 (main 自己跑的, 不是抄 agent 的输出)** [实测]: `python3 MECH/print/verify_pack_revb.py` → **rc=0** (★尺寸判据 100% 一致 + STL 逐点互验 100% 一致 ⇒ 模型层闭环, 可直接下片★) · `--selftest` → **rc=0 · 反向用例 8/8 全抓** (含反向5 判据 CRIT 0.60→0.30 松判据 / 反向7 金属档公差 0.05→0.50 / 反向8 实体按 9.50 造) · `python3 MECH/print/verify_pack.py` → **rc=0 (46/46 · Rev A 未变红)** · `python3 MECH/verify_budget.py` → **rc=0** (★充电耗散口径 = buck, 不是线性 0.8W★) · `python3 MECH/check_demo_struct_truth.py` → **rc=0 (20/20 组; ★6 个 PCB 类 id 仍是 FAIL = 正确状态, 排队等原理图定稿★)
★**③ 受保护文件 md5 逐字节未变** [实测] (★main 自己 md5sum 实跑★): `MECH/hinge_usb_check.py` **3425bc141508de8a35f34c7cf7b803e8** · `MECH/service_port_check.py` **9b24bf985764880f0105aee677fba6a8** · `MECH/hw_cross_review_check.py` **e521387b87b0fcdf9f22d56f14199967** · `MECH/display_biosafety_v2_check.py` **29c77fc3fc823048b1d96c9500d28dd7** · `MECH/check_demo_struct_truth.py` **700c4e3638cb7779df297cc8b0607884** · 网表 **c78f991283cc82d56c8e3dd31657c785** · 脚表 **4814617e22b567d76164e56bc5e39dc8** · 板 **611b869e13518c3c023fb178f91a0075** · `.kicad_pro` **3e504d2be83152e337949723e909be1b**
★**④ 关键数值复核** [推算]: FDM 10.50×4.80 与 金属·CNC 10.25×4.55 最坏单边 0.63/0.62 ≥ 判据 0.60 ✓ (两档现候选 0.13/0.02 · 0.38/0.32 仍不合格 ⇒ "两档并行"确为假二选一 ✓); 端件金属热路反解 A ≥ 4.98 mm² ⇒ 2.0×2.0 铝条 R=87.1 ❌ ⇒ 3.0×3.0 = 1.70 g 达标 ✓; 项目内 k=237 比官方 201 乐观 18% ⇒ 结论方向不变 ✓
★**⑤ 边界实测**: 未碰 `HW/` 任何文件 · 未碰 PCB 布线/布局/板框 · §3 现有重量 **0 改动/不预扣** · 判据阈值一个没松 · 零外发 · 实物 [实测] = 0 条
★**⑥ 会话状态说明 (★如实记★)**: 子会话 `agent:mech-lead:subagent:bd1e28db` (74016a46) **status=done** (★01:30:29 交卷★)
★**⑦ 未决**: 打印/切片/量测执行方 (本机跨网段不可达) · 端件截面 u8 排期拍板 · 6063 k 口径 237→201 ⇒ ★**已开 ISS-219 承接 (C-6 分光件放大 + C-7 散热出路 + C-C/X-3 口径 + k 口径统一)★**"""

# ==================================================================
# ② ISS-217 僵尸 fixing ⇒ 回滚 open (重派用)
# ==================================================================
ZOMBIE_217 = (
    "2026-11-16 01:4x 队列自动派活 job (fb67af40) **僵尸 fixing 清理**: 首次派活的子会话 "
    "`agent:hw-lead:subagent:67ddec52` (1ec42e28) 于 **01:14:18 起跑, 01:29:39 被中止** "
    "(★transcript 末行 = `openclaw:prompt-error: This operation was aborted`★) ⇒ ★**盘上交付物 0 件**: "
    "`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 不存在 · `HANDOFF/2026-11-16_hw-lead_ISS217_*.md` 不存在 · "
    "`HW/check_netlist_selfconsistency.py` mtime=01:03:42 (★早于本会话 01:14:18 ⇒ 是 ISS-214 的产物, 本会话没碰过★)★ "
    "⇒ ★**status 由 fixing 回滚为 open 并重派** (★上一轮的调研结论可作参考, 但一切以本轮实读为准★)"
)

# ==================================================================
# ③ 新开 ISS-219 → mech-lead
# ==================================================================
TITLE_219 = (
    "★★[主线内·结构侧·内部活] 镜框正中区第 2 轮重排: C-6 分光件按 A_e≤62mm² 放大 (光束 8.885 ⇒ 平板对角 15.39 / 棱镜 ≥9×9×5) "
    "+ C-7 面板 468mW vs 腔体 50°C (81.20°C ⇒ 需 4669mm² 散热面 ⇒ 金属热路方案) "
    "+ C-C/X-3 鼻梁热路径 54.33°C 与「不进皮肤热路径」口径修正 "
    "+ 铝 6063 k=237→201 官方保守口径统一 + 机器门禁 (不改 HW·不碰 PCB 布线布局·不预扣 §3 重量)"
)

DESC_219 = (
    "★**ISS-209 (11-15 交卷, 已 verified) 把正中区腔体按眼盒硬约束重算了第 1 轮**, 交卷里明写三条「只报不改、已登记 need 给 main」的冲突: "
    "C-6 (分光件要承的光束口径 2.9→8.885mm ⇒ 45° 平板严格口径需对角 15.39mm, 现 §1.3 M6 的 14×10×6 差 1.25mm 不够; 转向棱镜 8×8×5 装不下 8.885 ⇒ 需 ≥9×9×5; 体积 0.79→0.97cc, 重量 W4 3–6→3.68–7.36g) · "
    "C-7 (面板 468mW ⇒ 正中区腔体节点 81.20/77.43/75.24°C vs X-3 红线 50°C ⇒ 超 25.24–31.20°C; 保 50°C 需被动散热面 ≈4668.9mm² = u8 未定值 1000mm² 的 4.67 倍 ⇒ 加厚只贡献 6–12% ⇒ 必须金属热路) · "
    "C-C (鼻梁区热路径 12.0mm · R_bridge 400 K/W ⇒ 若 SoC+面板 1.018W 进镜框 ⇒ 鼻梁接触面 54.33/52.75/51.83°C ⇒ 超 43°C 红线 8.83–11.33°C ⇒ PCB/SoC 不进镜框正中; 且 X-3 那句「光学件不进皮肤热路径」在 468mW 下不成立 ⇒ 需加限定语) "
    "★**这三条至今只停在「只报」状态, 没有一条落成可执行规格** ⇒ 本单把它们收成【第 2 轮重排】★ "
    "★**外加 ISS-218 交卷时点的最后一笔账**: `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` §④ 建议下一轮把 `MECH/MECH_BUDGET.md` §3 的铝 6063 k=237 改成官方保守值 201 并同步 `verify_budget.py` ⇒ 本单一起做掉 (只改口径, 不改结论)★"
)

NOTE_219 = (
    "2026-11-16 01:5x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-209 交卷里那 3 条「只报不改、已登记 need 给 main」的冲突 (C-6 / C-7 / C-C+X-3) "
    "+ ISS-218 交卷 need `iss218_mech_alu_k_201_vs_237` (k=237→201 口径统一建议)★** "
    "⇒ ★**mech-lead 名额的上一条 ISS-218 已于本轮 01:4x 落 verified ⇒ 名额空出来 ⇒ 本单是第 4 轮**★ "
    "★**本单属结构类内部活, 不碰 PCB 布线/布局/板框 (老板 2026-11-11 10:07 口径) ⇒ 可派**★"
)

BRIEF_219 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**镜框正中区腔体做完第 2 轮重排** ★ ⇒ ★**4 条必做 + 1 个机器门禁 + 1 份交接单**★ ⇒ ★**本单不许改 `HW/` 下任何文件 / 不许碰 PCB 布线布局 / 不许改任何判据阈值 / 不许预扣 §3 现有重量 / 不许替老板拍 u8**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 01:3x~01:5x 实测, 不是推测★)** ★★
· ★**ISS-209 (11-15 交卷, 已 verified) 的交卷件里明写三条"只报不改、已登记 need 给 main"的冲突 (C-6 / C-7 / C-C+X-3)** ⇒ ★**它们至今仍停在"只报"状态, 没有一条落成可执行规格 ⇒ 镜框正中区就永远差这最后一段** ★
· ★**这三条不是老板级拍板, 是结构侧自己能算完的活** (几何 + 热 + 重量账) ⇒ ★**不接 = 三条永远挂着, 而它们卡着整机可行性** ★
· ★**ISS-218 (11-16 01:30 交卷, 本轮刚落 verified) 顺手把 ISS-216 的最后一笔账也点了**: `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` §④ 写明"建议下一轮把 §3 改成 201 (保守侧) 并同步 `verify_budget.py`" ⇒ ★**这条也一并做掉 (只改一个常数 + 一处文档 + 一条口径自检)** ★
· ★**仍属【原理图主线允许的结构类活】** (★老板 2026-11-11 10:07 口径: PCB 布线/布局类一律排队等原理图定稿 ⇒ 本单不碰 PCB 布线/布局/板框★) ⇒ ★**不与 demo 板画图抢产能** ★

★★**★① 输入件 (★都已 verified, 不许重复定性, 不许推翻, 直接用★)** ★★
· ★**`MECH/CENTER_CAVITY_RECALC.md`** ★= ISS-209 交卷件 (★参数化余量预算表 + §2.4 冲突 C-6 + §2.5 冲突 C-7 + §2.3 C-C 鼻梁热路径 + §4 降级方案 + §5 边界★) + 机器门禁 `MECH/cavity_recalc_check.py` (rc=0 12 项 · `--selftest` 9/9)
· ★**`MECH/MECH_BUDGET.md`** ★= §1.4.5 正中区旧数 11.8 (已标作废) · §1.7 X-1~X-6 (★硬约束: A_e ≤ 62 mm² · d = 15–20 mm · 腔体 ≤50 °C · 面板结温 ≤60 °C · 被动散热面 ≥0.5 W · 不得密闭腔 · 阈值 0.1234/1500/4000/0.011 rad 一个字不许改★) · §1.7.1 C-1~C-7 冲突表 · §3 重量表 (★本单不许预扣★)
· ★**`MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md`** ★= ISS-218 交卷件 (★u8 ∈ {30,33,35,38,40} 五情景 × 表A/表B/表C + k=237 与 k=201 两套值 + 硬指标 R_热路 ≤ 70 K/W★)
· ★**`MECH/verify_budget.py`** ★= ISS-216 交卷件 (★P_CHARGE 0.50 W buck 口径 + §8 口径自检 C1~C10 + `--selftest` 10/10★)

★★**★2. 必做① C-6 · 分光件按眼盒 A_e ≤ 62 mm² 放大 (★几何, 结构侧自己能算完★)** ★★
· ★**现状 (ISS-209 §2.4 已算好, 直接用, 不许重推)**: 光束口径 **2.9 mm** (走鹃Ⅱ 出瞳, 器件已作废) → **8.885 mm** (A_e=62) ⇒ 45° 平板所需对角 **12.57 mm** (宽松式) / **15.39 mm** (严格矩形包含口径) ⇒ ★**现 §1.3 M6 的 14×10×6 平板 (对角 14.14) 差 1.25 mm 不够** ⇒ 转向棱镜 8×8×5 **装不下 8.885 mm 光束** ⇒ **需 ≥ 9×9×5** ⇒ 体积 0.79 → **0.97 cc (+0.18)** · 重量 W4 **3–6 g → 3.68–7.36 g (+0.68~+1.36 g)** ★
· ★**你要出的**: ★**分光件新规格 (平板 + 2 只转向棱镜: 尺寸/材料/镀膜占位) + 重量与体积账 + 与"正中区轴向预算 T = d+3.0 = 18/21/23 mm (d=15/18/20)"的相容性检查 + 与 X-1 眼盒 62 mm² 的一致性检查**★ ⇒ ★**输出必须按 u8 ∈ {30,33,35,38,40} 参数化 (不许只给一个数)** ★ ⇒ ★**不许改 §1.3 M6 那一行 (只报不改 ⇒ 由 main 裁)** ★

★★**★3. 必做② C-7 · 面板 468 mW vs 腔体 50 °C ⇒ 出金属热路方案 (★出候选, 不代拍整机架构★)** ★★
· ★**现状 (ISS-209 §2.5)**: 正中区腔体节点 **81.20 / 77.43 / 75.24 °C** (d=15/18/20) vs X-3 红线 **50 °C** ⇒ 超 **31.20 / 27.43 / 25.24 °C** ⇒ 保 50 °C 所需被动散热面 **≈ 4668.9 mm²** (u8 未定值 1000 mm² 的 **4.67 倍**) ⇒ ★**加厚只贡献 6–12%** ⇒ ★**必须靠金属热路把热导到铰链侧/端件** ★
· ★**你要出的**: ★**2~3 条可落地的散热出路候选** (★例: 金属热路条 + 导热界面材料 (TIM) + 铰链侧/端件集热面★) ⇒ ★**每条必须给: 所需散热面/截面尺寸 · R_热路 (K/W) · ΔT @0.468 W 与 @0.50 W · 重量代价 (g) · 与 X-3「不得密闭腔 + 散热面 ≥0.5 W」的相容性 · 失败时的降级方案**★ ⇒ ★**必须与 ISS-218 的硬指标 R_热路 ≤ 70 K/W 对拍 (同一把尺)**★ ⇒ ★**不许把腔体红线 50 °C / 43 °C / 62 mm² / 判据 0.1234·1500·4000 改松** ★

★★**★4. 必做③ C-C + X-3 口径修正 (★鼻梁侧热路径★)** ★★
· ★**现状 (ISS-209 §2.3)**: 鼻梁区热路径 **12.0 mm** · R_bridge **400 K/W** ⇒ 若 SoC 0.55 W + 面板 0.468 W = **1.018 W** 进镜框 ⇒ 鼻梁接触面 **54.33 / 52.75 / 51.83 °C** ⇒ 超 43 °C 红线 **8.83–11.33 °C** ⇒ ★**加厚救不了 (路径长度不变)** ⇒ 保 43 °C 需 R_bridge **≥ 454.8 K/W** (仅面板) / **≥ 1101.2 K/W** (含 SoC) ⇒ ★**结构侧结论: PCB/SoC 不进镜框正中** ★
· ★**★同时修掉一句"口径本身不成立"的话★**: X-3 写「光学件在镜框, **不进皮肤热路径**」, 但按 468 mW 算 ★**仅面板**就让鼻梁接触面到 **43.89 / 43.16 / 42.74 °C** (d=15/18/20) ⇒ **d=15/18 档已破 43 °C 红线 0.89 / 0.16 °C** ⇒ ★**这句要么加限定语, 要么补热断要求 (R_bridge ≥ 454.8 K/W)** ★ ⇒ ★**你在 §1.7 X-3 那一行加一句"限定语 + 依据", 不许删原句、不许改 50/60/43/0.5 W 任何阈值** ★

★★**★5. 必做④ k = 237 → 201 的口径统一 (★ISS-218 §④ 明确建议, 本单一起做掉★)** ★★
· ★**现状**: `MECH/MECH_BUDGET.md` §2.4/§3 与 `MECH/verify_budget.py` 用的铝 6063 **k = 237 W/m·K** 比 **6063-T6 官方 201** (★[官网] ★你自己在厂商官网/官方 datasheet 上查一遍, 把来源 URL 与版本写进规格页, 不许凭记忆★) **乐观 18%** ⇒ 同几何 R **1.641 → 1.935 K/W** ⇒ ★**结论方向一条没变 (金属热路仍然必须 · 打印件 1944 K/W 仍然出局) ⇒ 只改口径, 不改结论** ★
· ★**你要改的**: ★**`MECH/MECH_BUDGET.md` 里 k=237 的那几行 → 201 (并注明来源 [官网]) + `MECH/verify_budget.py` 的常数同步 + `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` 的"项目内口径"表述同步 + 一条"不许漂回 237"的口径自检** ★ ⇒ ★**不许顺手改任何结论数字 (阈值/重量/温度/体积 一个都不许动)** ★

★★**★6. 机器门禁 (★要能自动复核, 不许只写文档★)** ★★
· ★**扩 `MECH/cavity_recalc_check.py`** (★只增不改: 既有 12 项 + `--selftest` 9 条一条不许删★) ⇒ ★**加 5 项判据: ① C-6 分光件新规格 vs 光束口径 8.885 相容 ② C-7 散热出路候选的 R_热路 / ΔT / 散热面对拍 (含 k=201) ③ 鼻梁 R_bridge 反解值 (454.8 / 1101.2) 对拍 ④ X-3 限定语在位 ⑤ k=201 口径不许漂回 237** ★ ⇒ ★**`--selftest` 每个新增判据都要有反向用例 (自己改坏必须变红)** ★
· ★**既有基线必须仍全绿 (★本单不许把它们弄红★)**: `MECH/verify_budget.py` rc=0 + `--selftest` 10/10 · `MECH/check_demo_struct_truth.py` rc=0 20/20 · `MECH/print/verify_pack.py` rc=0 46/46 · `MECH/print/verify_pack_revb.py` rc=0 + `--selftest` 8/8 · `MECH/hw_cross_review_check.py` rc=0 · ★**受保护脚本 md5 逐字节不变** ★

★★**★7. 交付物 (★就这四件, 不许多写, 不许改别人的地界★)** ★★
· ★**新建** `MECH/CENTER_CAVITY_REBALANCE_V2.md` ★= 第 2 轮重排 (★C-6 分光件规格 + C-7 散热出路 2~3 条 + C-C/X-3 处置 + k=201 口径订正 + 参数化表 (u8 五情景) + 降级方案 + 边界★)
· 扩 `MECH/cavity_recalc_check.py` ★= 上面 5 项判据 + 反向用例
· ★**新建** `HANDOFF/2026-11-16_mech-lead_ISS219_正中区第2轮重排与k口径.md` ★= B1~B6 齐全 (≤25 行)
· `state/fragments/mech.yaml` ★= ★**走 `python3 state/frag_write.py` 原子写** (★禁止 `open(p,"w")`★): +artifacts +claims (★只增不改既有 key 的值★) +needs (★已登记的 C-6/C-7/C-C/X-3 四条 need 各写一条 answer 闭环, 仍未决的另开 need 给 main★)

★★**★8. 验收命令 (★交卷前自己实跑, 原样贴进交卷★)** ★★
```
python3 MECH/cavity_recalc_check.py                # rc=0 (既有 12 + 新增全过)
python3 MECH/cavity_recalc_check.py --selftest      # rc=0 (既有 9 条不许删 + 新增反向全抓到)
python3 MECH/verify_budget.py                       # rc=0
python3 MECH/verify_budget.py --selftest            # rc=0 (10/10)
python3 MECH/check_demo_struct_truth.py             # rc=0 (20/20)
python3 MECH/print/verify_pack.py                   # rc=0
python3 MECH/print/verify_pack_revb.py              # rc=0
python3 MECH/print/verify_pack_revb.py --selftest   # rc=0 (8/8)
python3 MECH/hw_cross_review_check.py               # rc=0
python3 state/merge.py                              # rc=0
python3 state/gate_check.py                         # rc=0, 【Q1】18/18
md5sum MECH/hinge_usb_check.py MECH/service_port_check.py MECH/hw_cross_review_check.py MECH/display_biosafety_v2_check.py HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```
★**受保护 md5 期望值 (★必须逐字节一致, ★以你开工前自己跑出来的为准, 并把开工前/交卷后两个值都贴出来★)**:
__MD5_BLOCK__

★★**★9. 边界 (★违反一条即交卷无效★)** ★★
· ★**不许改**: `HW/` 下任何文件 (网表/脚表/BOM/板/`.kicad_pro`/SPEC.json/CHARGE_BOARD_SPEC/EMC_PRECHECK) · 任何 `state/gen_*.py` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · `SW/` 任何文件 · 任何别的总工的分片 · ★**4 个受保护 check 脚本** (hinge_usb_check / service_port_check / hw_cross_review_check / display_biosafety_v2_check)
· ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★)
· ★**不许改判据阈值**: 50 °C / 60 °C / 43 °C / 62 mm² / 0.60 / 0.1234 / 1500 / 4000 / 0.011 rad / R_热路 ≤ 70 K/W 一个都不许动
· ★**不许预扣 §3 现有重量** (u8 未定 ⇒ 只出参数化模板, 不改现有重量数)
· ★**不许替老板拍**: u8 端件截面 / 整机屏路线 / 波导归属 / FOV / 板长方案取舍 / 充电板是否留 / 整机形态
· ★**零外发**: 不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**凡要查资料 ⇒ 自己在厂商官网/官方 datasheet 上查 + 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + 查不到必须写降级方案 ⇒ 没有"批一句可以发"这个选项★**
· ★**本单实物 [实测] = 0 条** (板/样件不在本机) ⇒ 标 [实测] 的一律是"本机脚本/本机文件实读", 不是"实物测过"
· ★**不许自己改 issue_log 状态** (★verify_by=main, 干活的人不许自签★)""".replace("__MD5_BLOCK__", MD5_BLOCK)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {it.get("id"): it for it in issues}
    applied = []

    # ---------- ① ISS-218 → verified (幂等: 兄弟 job 775d9893 已于 01:4x 落过 ⇒ 不重复落账) ----------
    it = by_id["ISS-218"]
    if it["status"] == "fixing":
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_result"] = VERIFY_218
        it["verify_date"] = TODAY
        it["fix_ref"] = [
            "MECH/print/PRINT_COUPON_TIER3_SPEC.md",
            "MECH/print/frame_typec_coupon_tier3_revb.stl",
            "MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md",
            "HANDOFF/2026-11-16_mech-lead_ISS218_打印包第三档与热路重量模板.md",
        ]
        it["note"] = (it.get("note") or "") + "\n\n★2026-11-16 01:4x main 独立复核落 verified (★会话 status=done · 01:30:29 交卷 · 交付物 4 件在盘上 · 门禁 main 自己实跑全绿 · 受保护 md5 逐字节未变★)"
        applied.append("ISS-218 → verified")
    else:
        applied.append("ISS-218 已是 %s (★兄弟 job 775d9893 于 01:4x 落的 ⇒ 幂等跳过, 不覆盖它的 verify_result★)" % it["status"])

    # ---------- ② ISS-217 僵尸 fixing → open ----------
    it = by_id["ISS-217"]
    assert it["status"] == "fixing", "ISS-217 状态不是 fixing: %s" % it["status"]
    it["status"] = "open"
    it["dispatched_at"] = None
    it["note"] = (it.get("note") or "") + "\n\n" + ZOMBIE_217
    applied.append("ISS-217 → open (僵尸 fixing 回滚, 待重派)")

    # ---------- ③ 新开 ISS-219 ----------
    assert "ISS-219" not in by_id, "ISS-219 已存在"
    new = {
        "id": "ISS-219",
        "title": TITLE_219,
        "severity": "high",
        "source_blocker": "ISS-209",
        "desc": DESC_219,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": NOTE_219,
        "task_brief": BRIEF_219,
        "dispatched_at": None,
    }
    issues.append(new)
    applied.append("ISS-219 新开 → mech-lead (open)")

    shutil.copy2(LOG, BAK)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)

    print("备份: %s" % BAK)
    for a in applied:
        print("  - %s" % a)
    print("issue 总数: %d" % len(issues))


if __name__ == "__main__":
    main()
