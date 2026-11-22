#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main 独立验收签字 + 新开两单 (2026-11-15 22:2x)
=============================================================
★背景: 兄弟 job 21:5x 派出 ISS-207(sw-lead) / ISS-208(mech-lead) / ISS-174(hw-lead)
  ⇒ sw-lead / mech-lead 两条 22:07~22:14 交卷完成 (会话 status=done), 但 brief 不许子 agent
  改 issue_log ⇒ 停在 fixing ⇒ ★僵尸 fixing 第 15 次复发 ⇒ A 段恒空 ⇒
  main 独立复核 (只看盘上实物, 不采信自述) ⇒ 落 verified ⇒ 两个名额释放
  ⇒ 补位开 ISS-209 (mech-lead · 正中区腔体重排) + ISS-210 (sw-lead · 60ms 判据链)
★铁律: 干活的人不许自签 ⇒ verify_by=main
★不碰: PROJECT_TRACKER.md §0 / 任何分片 (含 mech.yaml 的 U-3 订正 ⇒ 交 mech-lead 自己在 ISS-209 里改)
       / 任何真源文件 (板/网表/脚表/原理图) / outbox
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

# ============ ① main 独立复核结论 (全部是本轮 main 自己跑出来的数字) ============

VERIFY = {
    "ISS-207": (
        "pass · 2026-11-15 22:1x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 板端验证包可执行**: `bash SW/tools/rk3572_target_smoke.sh --dry-run` **rc=0** (★脚本自报『本机无板 ⇒ 板端结论一律 [0数据]』★)\n"
        "★**② 重建路径可执行**: `bash SW/tools/rk3572_model_rebuild.sh --dry-run` **rc=0** (5/5 步命令序列全列出)\n"
        "★**③ 产物 + 身份锚落盘**: `SW/artifacts/models/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` = **4,989,367 B** + `.sha256` sidecar + `.meta.json` ⇒ "
        "★**main 自己跑 `sha256sum -c` ⇒ `...rknn: OK`** (★不是抄它的数, 是现场校验的★)\n"
        "★**④ 交付件 4 个齐全**: `SW/RK3572_TARGET_COMPAT_V2.md` (23,741 B) · `SW/tools/rk3572_target_smoke.sh` (28,192 B) · `SW/tools/rk3572_model_rebuild.sh` (9,709 B) · "
        "`HANDOFF/2026-11-15_sw-lead_ISS207_rk3572target与验证包.md` (3,569 B)\n"
        "★**⑤ 核心结论复核 (main 自己查过盘上真源, 与交卷一致)**: 最新 rknn-toolkit2 = **v2.5.0** (2026-10-20) 官方 8 系列 **无 RK3572** ⇒ 只能 `target_platform='rk3576'` ⇒ "
        "★**『升级就有 rk3572 target』不存在** ★⇒ RK3572 BSP runtime 认不认 rk3576-target 产物 = 官方无此口径 ⇒ 只能板端 `load_rknn` 回答 ⇒ 命题判 (b)\n"
        "★**⑥ 受保护文件 md5 全部未变 (main 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · "
        "`.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**本单没碰板/没碰网表/没碰脚表/没碰原理图**★\n"
        "★**⑦ 残留 (★不藏账★)**: R1 = 板端 `load_rknn` 结论仍 **[0数据]** (★板不在本机, 包已就绪★) ⇒ ★**这一条不是本单能闭的** ⇒ ★**已并进本轮新开的 ISS-210 (sw-lead · 端到端 60ms 判据链)**: "
        "把『板到手 ⇒ 30 分钟出 60ms 生死判定』与『板永不到 ⇒ 降级结论』两条路都写死 ⇒ ★**本单到此收口**★\n"
        "★**⑧ 零外发**: `state/outbox/` 本轮未增删, 零邮件 / 零询价 / 零采购 / 零供应商接触"
    ),
    "ISS-208": (
        "pass · 2026-11-15 22:1x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 机器门禁**: `python3 MECH/display_biosafety_v2_check.py` **rc=0** ⇒ **5/5 全过** ⇒ C1 旧文档 5 份 **活动口径 = 0** / 历史沿革 31 (逐文件 0/23 · 0/3 · 0/1 · 0/3 · 0/1) · "
        "C2 结构真源 `MECH/MECH_BUDGET.md` 命中 **12/12** 关键词 (含数值 62 mm²) · C3 V2 判据 6 条关键量 **12/12** · C4 定性表 **33 行** (分布 21/6/3/2/1) · C5 判据文件 md5 一致 (未改动)\n"
        "★**② 反向用例**: `python3 MECH/display_biosafety_v2_check.py --selftest` **rc=0 ⇒ 6/6** (★塞活动口径 / 删 62 / 删 0.1234 / 破坏 33 行表 / 篡改判据文件 五种破坏全被抓★) ⇒ ★**闸是真的, 不是装饰**★\n"
        "★**③ main 自己 grep 复核 `走鹃`**: 旧 5 份文档合计 **31 处** (MECH_BUDGET 23 · PROTOTYPE_PLAN 3 · SOC_CARRIER_EVAL 1 · STRUCT_REVIEW_ISS065 3 · CLEARANCE_FIX 1) ⇒ ★**活动口径 0**★; "
        "另两份新件 (DISPLAY_BIOSAFETY_CRITERIA_V2 4 · JBD_ROLE_NARROWING 12) = 历史语境; CLOSEOUT 自身 40 处 = 定性表原文引用\n"
        "★**④ 交付件齐全**: `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` (145 行 / 69 个表格行) · `MECH/display_biosafety_v2_check.py` · `HANDOFF/2026-11-15_mech-lead_ISS208_走鹃旧口径收口与眼盒约束落地.md` (4,119 B)\n"
        "★**⑤ 硬约束落位复核 (main 自己看盘)**: `MECH/MECH_BUDGET.md` §1.7 **X-1 = A_e ≤ 62 mm² (≈8×7.7 mm)** + **X-2 = d = 15–20 mm** 在位; §1.7.1 **C-1** 记着 ★**正中区 ≥11.8 mm 旧数已作废 ⇒ 差 3.2 mm (d=15) ~ 8.2 mm (d=20)**★ ⇒ "
        "★**62 mm² 一个字没改 (只引用 V2, 未自行放宽/收紧) ⇒ 符合任务书**★\n"
        "★**⑥ 受保护文件 md5 未变**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785`\n"
        "★**⑦ 残留 (★4 条 need 仍待 main 裁, 不藏账★)**: U-1 裁6 方案取舍 (老板级) / U-2 逃线带重算挂哪单 / ★**U-3 = 分片 `mech_hinge_stack_fixed_mm` 仍 24.00 vs 文档 25.00 ⇒ 由 mech-lead 改自己的分片 (已在 ISS-209 里点名)**★ / U-4 ISS-202+203 八条 need 请 main 在 pm.yaml 落 answer\n"
        "★**⑧ ★本单挖出的下一件硬活 = 正中区腔体重排**★**: X-2 原文写着 ★**『下一单必须重排正中区腔体, 不许沿用 11.8 mm』**★ ⇒ ★**main 已据此开 ISS-209 → mech-lead (结构侧, 不碰 PCB)**★\n"
        "★**⑨ 零外发**: outbox 未增删, 零邮件 / 零询价 / 零采购"
    ),
}

NOTE_VERIFY = (
    "\n★**【2026-11-15 22:1x 项目总工 (main) 独立验收签字】** ★\n"
    "★**僵尸 fixing 第 15 次复发, 本轮清 2 条**: 兄弟 job 21:5x 派出的两个会话 (sw-lead ISS-207 会话 `1d62fb36` / mech-lead ISS-208 会话 `69ec40ff`) "
    "★**22:07~22:14 全部 status=done 且交卷完整** ⇒ 但 brief 不许子 agent 改 issue_log ⇒ 停在 `fixing` ⇒ ★**sw-lead / mech-lead 明明闲着却进不了 A 段候选**★ ⇒ "
    "★**main 独立复核 (只看盘上实物) 全部通过 ⇒ 本单转 verified ⇒ 两个名额释放**★ ⇒ ★**同轮补位开 ISS-209 (mech-lead) / ISS-210 (sw-lead)**★\n"
)

# ============ ② 新开两单 (brief 全文 = advance.py 直接用的 task_brief) ============

BRIEF_209 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**镜框正中区光学腔体按 ISS-208 刚落的眼盒硬约束重排**★ (★`A_e ≤ 62 mm²` + 评估距离 `d = 15–20 mm`★) ⇒ 出 ★**参数化余量预算表 + 冲突量化 + 一个能自动复核的机器门禁**★ ⇒ ★**只出参数化占位预算, 不许替老板定波导/屏路线/FOV**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-15 22:1x 实测, 不是推测★)** ★★
· ★**ISS-208 (你 22:0x 交卷) 自己写下的下一件活**: `MECH/MECH_BUDGET.md` §1.7 **X-2** 原文 ★**『下一单必须重排正中区腔体, 不许沿用 11.8 mm』**★ ⇒ ★**那一单就是本单** ★
· ★**硬约束已落结构真源 (你刚落的, 现在要用它)**: ★**X-1 = 出瞳眼盒面积 `A_e ≤ 62 mm²` (≈8×7.7 mm)** ★ · ★**X-2 = 评估距离 `d = 15–20 mm` (同类公开 18 mm) ⇒ 轴向净空 = d** ★ ⇒ ★**§1.7.1 C-1 已把冲突量算出来了: 旧数「正中区 ≥11.8 mm」差 ★**3.2 mm (d=15) ~ 8.2 mm (d=20)**★** ★
· ★**这个差值不是纸面问题, 它压着三件东西**: ★**① 整机第一厚度约束 (正中区 ≥11.8 mm 是整机最厚处, 不是镜脚) ⇒ 镜框做不成「薄片式」**★ · ★**② 整机重量 W9 (9–14 g) 按 ~140×40×40 mm 算的, 正中区加厚到 12 mm ⇒ 重量上限要重核 (★W9 的 9–14 g 是【下限】不是上限★)**★ · ★**③ 鼻梁区皮肤温度 (ISO 13732-1 43°C 红线, §3 W9 注记: 把 PCB 挪到镜框 = 把热搬到鼻梁)**★ ⇒ ★**这三件都在你 (结构) 的地界里, 只有你能算** ★
· ★**V2 已把做法写死了 (你刚引用的)**: ★**占位件必须 FOV 可变 ⇒ 眼盒是硬约束不是待定项** ★ ⇒ ★**所以本单的正确定法是【参数化占位重排】, 不是【等屏/等波导定下来再说】** ★

★★**① 参数化重排表 (★本单最要紧的一件★)** ★★
· ★**维度 (至少这三组, 你可以补)**: ★**`d ∈ {15, 18, 20}` mm** (评估距离) × ★**`A_e ∈ {25, 40, 62}` mm²** (眼盒面积) ⇒ ★**9 行都要有** ★
· ★**每行必须给**: ★**耦合光学轴向占用 + 分光件轴向占用 + 装配余量 ⇒ 正中区轴向厚度预算 (mm)**★ · ★**与现行上沿/正中区目标 (10–12 mm) 的差值 (mm, 允许为负 ⇒ 那就是超差)**★ · ★**与 §1.4.5 旧数 11.8 mm 的差值**★ · ★**判定 (可行 / 超差 / 待定)**★ · ★**证据等级 + 出处 (V2 C-4/C-5 + X-1/X-2 + §1.4.5, ★只引用不许改数★)** ★
· ★**★不许手算★**: 每个差值必须由脚本算出来 (★用 §1.7 的公式与已落盘的数, 不许在文档里写一个没来源的 mm 数★) ★
· ★**出瞳面 ±3 mm 装配公差带 (V2 §3 ⑤ 降级方案) 要占一行**, 说明它在 9 行里占多少 (★别让它被 9 行淹没★)
· ★**★不许做这两个决定★**: ★**① 不许定波导归属 / 屏路线 / FOV (老板 11-04 已拍板「屏幕暂时先不用视崖 ⇒ 整机屏路线与显示架构暂缓到整机阶段」⇒ 你只做参数化占位, 不许反推供应商)**★ · ★**② 不许放宽或收紧 62 mm² 与 d=15–20 mm 这两个数 (★它们是 V2 判据, 你只许引用与落位★)**

★★**② 冲突量化 (★只报不改 + 登记 need★)** ★★
· ★**把冲突算成数 (mm / mm² / g), 别写成形容词**: ★**正中区厚度需求 vs 现行目标差多少**★ · ★**若厚度超差 ⇒ 镜框重量按 §3 的密度假设重核, 差多少 g**★ · ★**若 PCB 要挪到镜框 ⇒ 鼻梁区热路径多长 (mm) / 对 43°C 红线的余量影响**★
· ★**若发现与既有结构数冲突 (除 11.8 mm 外还有别的)** ⇒ ★**只报不改 + 登记 need 给 main** ⇒ ★**冲突量必须算出来** ★
· ★**★顺带把 U-3 收掉 (★你自己的分片, 你自己改★)**: ★**`state/fragments/mech.yaml` 的 `mech_hinge_stack_fixed_mm` 仍写 24.00, 文档已是 25.00 (ISS-206 裁 2 定的 16p/20p/4p/10p) ⇒ 走 `state/frag_write.py` 把这个 claim 的值改成 25.00**★ ⇒ ★**不许手改 yaml, 不许改别的 key** ★

★★**③ 机器门禁 (★本单必须留一个能自动复核的东西★)** ★★
· ★**新建** `MECH/cavity_recalc_check.py` ⇒ 至少查: ①**§1.7 X-1/X-2 在结构真源里在位 (关键词 + 数值 62 / 15 / 20)** ★ ②**参数表行数与维度齐全 (9 行, d×A_e 各覆盖)** ★ ③**冲突量与脚本算出来的一致 (d=15 ⇒ 3.2 mm · d=20 ⇒ 8.2 mm)** ★ ④**判据文件 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` 未被改动 (md5)** ★
· ★**rc=0 = 全过; 任何一条不过 ⇒ rc=1 并点名是哪一条** ⇒ ★**必须支持 `--selftest` (★至少 5 个用例: 改坏一行参数表 / 删掉 62 / 改坏冲突量 / 篡改判据文件 / 删一行表 ⇒ 全都要被抓★)** ★
· ★**不许改** `MECH/hinge_usb_check.py` · `MECH/service_port_check.py` · `MECH/hw_cross_review_check.py` · `MECH/display_biosafety_v2_check.py` (★md5 一个都不许变★)

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**新建** `MECH/CENTER_CAVITY_RECALC.md` (★参数表 + 冲突量化 + 出处 + 降级方案 + 边界★)
2. ★**新建** `MECH/cavity_recalc_check.py` (★门禁 + `--selftest`★)
3. ★**新建** `HANDOFF/2026-11-15_mech-lead_ISS209_正中区腔体重排.md` (★≤25 行, B1~B6 六块齐全★)
4. `state/fragments/mech.yaml` (★走 `state/frag_write.py` 原子写: 只加 artifact/claim/answer + ★**U-3 那个 claim 值的订正**★; 不许删改别人的 key★)

★★**⑤ 验收标准 (★机械可判, 不许含糊★)** ★★
· `python3 MECH/cavity_recalc_check.py` ⇒ **rc=0** 且逐项 PASS
· `python3 MECH/cavity_recalc_check.py --selftest` ⇒ **rc=0**, **≥5/5** 用例
· `MECH/CENTER_CAVITY_RECALC.md` 的参数表 ★**9 行齐全 (3 d × 3 A_e)**, 每行有 ★**差值 mm + 判定 + 证据等级 + 出处**★
· 冲突量与 §1.7.1 C-1 ★**逐字一致 (d=15 ⇒ 3.2 mm · d=20 ⇒ 8.2 mm)**, 且由脚本算出
· `MECH/MECH_BUDGET.md` 的 ★**62 mm² / 11.8 mm / 10–12 mm / 判据阈值一字不许改**★ (★本单只许新增段落★)
· `state/fragments/mech.yaml` 的 `mech_hinge_stack_fixed_mm` = **25.00**
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv` ⇒ ★**与交卷前逐字一致 (611b869e… / c78f9912…)** ★

★★**⑥ 边界 (★不许越界★)** ★★
· ★**不许改板 / 网表 / 脚表 / 原理图 / 任何 `state/gen_*.py`** ★
· ★**不许碰 PCB 布线 / 布局 / 逃线层数** ★ (★老板 11-11 10:07: 先原理图, 再 PCB★)
· ★**不许替老板拍板 (波导归属 / 屏路线 / FOV / 整机形态)** ★ ⇒ ★**只出参数 + 冲突 + 出路候选** ★
· ★**不许外发 / 询价 / 采购 / 下单** ⇒ ★**外部依赖一律自己网上查 + 标 [官网]/[媒体]/[推算]/[0数据] + 查不到就写降级方案** ★
· ★**实物 [实测] = 0 条** (★本机无实板/无实物★) ⇒ 几何数一律标 [推算] 并给出处 ⇒ ★**不许把推算冒充实测** ★
· ★**不许改 `PROJECT_TRACKER.md` §0 锁死表 / 不许写别的 agent 的分片** ★

★★**⑦ 自证命令 (★交卷前跑, 输出原样贴进交卷件★)** ★★
```
python3 MECH/cavity_recalc_check.py
python3 MECH/cavity_recalc_check.py --selftest
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv
```

★★**⑧ 任务书没把话说满 (★按项目铁律★)** ★★
★**本单至少要交 ①②③④ 四样** (参数表 / 冲突量化 / 机器门禁 / 交卷件) ⇒ ★**但你可以补充我没要求、而你觉得关键的** (★例如: 出瞳面 ±3 mm 可调带的装配公差怎么落到压框 · 鼻梁区 43°C 与腔体加厚的耦合 · 重量上限重核的算法 · 参数化占位件怎么做到「FOV 可变 + 可换压框」★) ⇒ ★**超出的部分我照收, 这正是我看重的** ★
"""

BRIEF_210 = """★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: 把 ★**「RK3572 上端到端 60ms 硬指标生死判定」**★ 从 ★**「等一块板」**★ 改成 ★**「板到手 ⇒ 30 分钟出结论」+「板永不到 ⇒ 降级结论也写死」**★ 的 ★**一条完整可执行判据链**★ ⇒ ★**绝不外发, 查不到就写降级方案** ★

★★**为什么是现在 (★main 2026-11-15 22:1x 实测, 不是推测★)** ★★
· ★**前两块已经拼好了, 就差中间那一块**: ★**ISS-207 (sw-lead, 22:0x 交卷, main 已独立验收签字)** 交出 ★**板端验证包** (`SW/tools/rk3572_target_smoke.sh` N1~N5 + `SW/tools/rk3572_model_rebuild.sh` + PC 侧产物 + sha256 sidecar) ★ · ★**ISS-124 (sw-lead, 21:3x 交卷, main 已独立验收签字)** 交出 ★**ISP 段反解** (★模式A 最多 **15.10 ms** · 模式B **17.33 ms** · 现占 8.00 ms ⇒ 余量 **+7.09 / +9.33 ms**★) ⇒ ★**⇒ 两块拼起来, 判据链中间断了一节** ★
· ★**断点 (★main 实测, 不是推测★)**: ★**`SW/DEMO_OD_TIMING_SPEC.md` §2 的 11 段接力表里【没有 ISP 段打点】**★ ⇒ ★**板端就算跑起来, 也取不到 ISP 段的数** ⇒ ★**⇒ 11 段表不补, ISS-129 (老板 T2 翻案条款: 纯 NPU S5 > 20.33ms ⇒ 60ms 不可保) 在板到手时依然判不了** ★
· ★**板不可达这件事不许再当阻塞项** (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 外部依赖一律换成【自己查的结果 + 证据等级 + 降级方案】★) ⇒ ★**本单的价值 = 把【等板】换成【板来之前就把判据链备好 + 板永不到的降级结论也写死】** ★

★★**① 补 ISP 段打点 (★本单最要紧的一件·改在产生点★)** ★★
· ★**改 `SW/DEMO_OD_TIMING_SPEC.md` §2 的 11 段接力表 ⇒ 变成 12 段**: ★**新增 ISP 段**, ★**六列必须齐全 (段 / 打点名 / 谁做 / 什么时刻开始 / 什么时刻结束 / 取哪个时间戳 / 含什么 / 不含什么)**** ★
· ★**同时补 §3.1 的「每段必须报的字段」表** ⇒ 加上 ISP 段的字段 (★纯硬件耗时 + SDK 总耗时 两个数, 跟其它段同口径★)
· ★**★口径纪律 (★踩过的坑, 别再踩★)**: ★**ISP 段必须报【纯硬件耗时】与【SDK 总耗时】两个数, 不许合并成一个数** ★ · ★**12M Pixel 是【单帧分辨率上限】不是【每秒能力】, 不许用它推 MP/s** ★ (★ISS-124 已钉死这两条★) ⇒ ★**ISP 段的时间来源与其它段不同 (ISP 驱动/帧统计), 你要写清取哪个时间戳、为什么★**
· ★**不许改** `SW/ISP_CAPABILITY_RESEARCH.md` / `.json` / `SW/tools/isp_budget_solve.py` (★那是 ISS-124 已验证件, 只引用★) · ★**不许改** 其它 10 段的既有数字 (★本单只许新增第 12 段 + 补字段表一行★)

★★**② 把 ISP 判据固化进机器 (★不许只是文档里的一段话★)** ★★
· ★**改** `SW/tools/timing_check.py` ⇒ 把 ★**ISP 段判据 (模式A: ISP 段 avg ≤ 15.10 ms)**★ 变成 ★**可执行判据** (★从实测输入算出 PASS/FAIL + 数值 + 差多少★)
· ★**改完 `python3 SW/tools/timing_check.py` 必须 rc=0 且 SELFTEST 全过** (★现状 55/55 ⇒ ★**不许低于 55**★) ⇒ ★**若加判据必须同时加自测用例 (反向用例: ISP 超 15.10 ms 必被抓)★** ★
· ★**不许调松 60ms 硬指标, 不许调 ISP 判据阈值** (★15.10 ms 来自 ISS-124 的反解, 60 ms 是老板锁死项★) ⇒ ★**若发现阈值与实测口径对不上 ⇒ 报出来, 不许自己改★**

★★**③ 判据链文档 (★板到手怎么跑·板不到怎么判·两条路都写死★)** ★★
· ★**新建** `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` ⇒ 六段: ★**① 前置 (P1~P6, 直接引 ISS-207 v2, 不许重写) ② 板端 11+1 段打点 (含新 ISP 段) ③ N1~N5 (rknn 加载/精度/纯 NPU/温度与供电) ④ 60ms 硬指标判定 (模式A/B, ★用【框龄 age】模型, ★不许把环节相加——那是我们自己的铁律★) ⑤ 三条出路 (★降 OD 负载 640×480@30 / 换更小模型 / 回到 RK3576★) + 各自代价 ⑥ 板永不到时的降级结论** ★
· ★**第 ⑥ 段必须有**: ★**用 RK3576 实测链 (纯 NPU 15.4~17.4 ms, 模式A 55~57 ms) + RK3572 = 4/6 TOPS ⇒ 纯 NPU [推算] 23.1~26.1 ms ⇒ 模式A [推算] 62.7~65.7 ms**★ ⇒ ★**明确写清哪一段是 [实测] / 哪一段是 [推算] / 哪一段是 [0数据] (板端)** ★ ⇒ ★**并给出「若板永远不来 ⇒ 60ms 生死判定怎么裁」的老板级选项清单 (只列, 不代决)** ★
· ★**不许出现「等板子回来」这种无判据的挂起表述** ⇒ ★**每一步要么有可执行命令, 要么有明确的 [0数据] 标注 + 降级方案** ★

★★**④ 交付物 (★只写这些, 一个字不多★)** ★★
1. ★**改** `SW/DEMO_OD_TIMING_SPEC.md` (★§2 加第 12 段 + §3.1 加字段行★)
2. ★**改** `SW/tools/timing_check.py` (★加 ISP 判据 + 加自测用例★)
3. ★**新建** `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`
4. ★**新建** `HANDOFF/2026-11-15_sw-lead_ISS210_60ms判据链.md` (★≤25 行, B1~B6 六块齐全★)
5. `state/fragments/sw.yaml` (★走 `state/frag_write.py` 原子写: 只加 artifact/answer/claim; 不许删改别人的 key★)

★★**⑤ 验收标准 (★机械可判★)** ★★
· `python3 SW/tools/timing_check.py` ⇒ **rc=0**, **SELFTEST ≥55/55**
· `SW/DEMO_OD_TIMING_SPEC.md` §2 段表 ★**12 行 (原 11 + ISP 段)** ★ 且 ISP 段六列齐全 (★可 grep 判★)
· `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` ★**六段齐全**, 每步都有可执行命令或明确 [0数据] 标注
· ★**15.10 / 17.33 / 7.09 / 9.33 四个数与 `SW/ISP_CAPABILITY_RESEARCH.md` / `.json` 逐字一致** ⇒ ★**不许另发明一套数★**
· `bash SW/tools/rk3572_target_smoke.sh --dry-run` ⇒ **rc=0 仍绿** (★不许把 ISS-207 交的东西跑坏★)
· `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 且 ★**【Q1】18/18**★
· `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv` ⇒ ★**与交卷前逐字一致 (611b869e… / c78f9912…)** ★

★★**⑥ 边界 (★不许越界★)** ★★
· ★**不许改板 / 网表 / 脚表 / 原理图 / 任何 `state/gen_*.py`** ★
· ★**不许碰 PCB 布线 / 布局** ★ (★老板 11-11 10:07 口径★)
· ★**不许改 `SW/ISP_CAPABILITY_RESEARCH.md` / `.json` / `SW/tools/isp_budget_solve.py` / `SW/RK3572_TARGET_COMPAT_V2.md`** (★已验证件, 只引用★)
· ★**不许外发 / 询价 / 采购 / 下单 / 联系任何供应商** ⇒ ★**外部依赖一律自己网上查 + 标证据等级 + 查不到就写降级方案** ★
· ★**实物 [实测] = 0 条** (★板不在本机★) ⇒ 板端结论一律 [0数据] ⇒ ★**不许编板端数据** ★
· ★**不许替老板拍板 (60ms 生死怎么裁 / 换不换芯片 / 降不降帧)** ⇒ ★**只出判据链 + 出路清单 + 代价** ★
· ★**不许改 `PROJECT_TRACKER.md` §0 锁死表 / 不许写别的 agent 的分片** ★

★★**⑦ 自证命令 (★交卷前跑, 输出原样贴进交卷件★)** ★★
```
python3 SW/tools/timing_check.py
bash SW/tools/rk3572_target_smoke.sh --dry-run
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv
```

★★**⑧ 任务书没把话说满 (★按项目铁律★)** ★★
★**本单至少要交 ①~⑤ 五样** ⇒ ★**但你可以补充我没要求、而你觉得关键的** (★例如: 板端 thermal_zone0 温度与降频对 60ms 的影响怎么进判据 · 640×480@30 降载模式下的新预算 · rk3576-target 产物在 RK3572 上的兼容风险到底压在哪一环 · 判据链要不要做成一个脚本而不是一份文档★) ⇒ ★**超出的部分我照收** ★
"""

NEW = {
    "ISS-209": {
        "id": "ISS-209",
        "title": "★★[主线内·结构侧·内部活] 正中区光学腔体按眼盒 A_e ≤ 62 mm² + d=15–20mm 重排 (★ISS-208 §1.7 X-2 自己点名的下一单★)",
        "severity": "high",
        "source_blocker": "ISS-208",
        "source_agent": "main",
        "desc": "★**ISS-208 (22:0x 交卷) 在 `MECH/MECH_BUDGET.md` §1.7 X-2 写下: 『下一单必须重排正中区腔体, 不许沿用 11.8 mm』** ⇒ "
                 "★**§1.7.1 C-1 已算出差 3.2 mm (d=15) ~ 8.2 mm (d=20)** ⇒ ★**本单 = 那『下一单』** ⇒ ★**只出参数化余量预算 + 冲突量化 + 机器门禁** "
                 "⇒ ★**不许替老板定波导/屏路线/FOV (老板 11-04 已拍板暂缓到整机阶段)** ⇒ ★**结构侧, 不碰 PCB**",
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-15",
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-15 22:2x main 新开 (★僵尸 fixing 第 15 次复发清理后, mech-lead 名额空出来 ⇒ 补位★) ⇒ ★**依据 = ISS-208 自己登记的『下一单』+ §1.7 X-1/X-2 硬约束** ⇒ "
                "★**本单顺带收掉 ISS-206 的 U-3 (分片 `mech_hinge_stack_fixed_mm` 24.00 → 25.00, 由 mech-lead 改自己的分片)** ★",
        "dispatched_at": None,
        "task_brief": BRIEF_209,
    },
    "ISS-210": {
        "id": "ISS-210",
        "title": "★★★[demo 头号卡点·自己查版·续] ISS-129/155 收口: 端到端 60ms 生死判定链 (补 ISP 段打点 + 判据固化 + 板永不到时的降级结论)",
        "severity": "high",
        "source_blocker": "ISS-129",
        "source_agent": "main",
        "desc": "★**ISS-207 (板端验证包) + ISS-124 (ISP 反解) 两块已交卷并独立验收签字** ⇒ ★**断点 = `SW/DEMO_OD_TIMING_SPEC.md` §2 的 11 段表没有 ISP 段打点** ⇒ "
                 "★**板端即使跑起来也取不到 ISP 段 ⇒ ISS-129 (T2 翻案条款 纯 NPU S5 > 20.33ms) 在板到手时依然判不了** ⇒ ★**本单 = 把『等板』换成『板到手 30 分钟出结论 + 板永不到也有降级结论』** ⇒ ★**软件/规格侧, 不碰 PCB**",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-15",
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-15 22:2x main 新开 (★僵尸 fixing 第 15 次复发清理后, sw-lead 名额空出来 ⇒ 补位★) ⇒ ★**依据 = ISS-207/ISS-124 两块已验证件之间的断点 (main 实测 `SW/DEMO_OD_TIMING_SPEC.md` 无 ISP 段)** ⇒ "
                "★**本单不要求板子在本机 ⇒ 板端结论一律 [0数据] + 降级方案** ★",
        "dispatched_at": None,
        "task_brief": BRIEF_210,
    },
}

CROSS_REF = {
    "ISS-133": "\n★**【2026-11-15 22:2x main】** 状态不变 (★老板 11-04 拍板「整机屏路线与显示架构暂缓到整机阶段」★ ⇒ 本单仍暂缓) ⇒ "
               "★**但 ISS-208 (22:0x verified) 新落的眼盒硬约束 (A_e ≤ 62 mm² + d=15–20mm) 逼出了『正中区腔体必须重排』这一件 ⇒ 已拆成子单 ISS-209 → mech-lead (★参数化重排, 不定屏/波导路线★)** ★",
    "ISS-129": "\n★**【2026-11-15 22:2x main】** 本单仍 open (★板不可达 ⇒ 实测这半闭不了★) ⇒ ★**但『板到手怎么判』这一半已拆成子单 ISS-210 → sw-lead** (★补 ISP 段打点 + 60ms 判据链 + 板永不到时的降级结论★) ⇒ "
               "★**⇒ 本单不再是一句『等板』, 而是『等 ISS-210 把判据链备好 + 等板』** ★",
    "ISS-155": "\n★**【2026-11-15 22:2x main】** 拆块① = ISS-207 (sw-lead, 22:1x 已 verified: rknn-toolkit2 最新 v2.5.0 无 rk3572 target ⇒ 只能 rk3576-target + 板端验证包 + PC 侧产物) ⇒ "
               "★**拆块② = ISS-210 (sw-lead, 22:2x 派出): 板端加载结论 + 端到端 60ms 判据链 + 降级结论** ⇒ ★**『等板』不再是本单的阻塞表述** ★",
}


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {i.get("id"): i for i in issues}
    out = []

    # ① 独立验收签字
    for iid, res in VERIFY.items():
        it = by_id.get(iid)
        assert it is not None, "%s 不存在" % iid
        assert it.get("status") == "fixing", "%s status=%s 非 fixing" % (iid, it.get("status"))
        assert it.get("verify_by") == "main", "%s verify_by 非 main" % iid
        it["status"] = "verified"
        it["verify_result"] = res
        it["verify_date"] = "2026-11-15 22:1x"
        it["fixed_at"] = "2026-11-15"
        it["note"] = (it.get("note") or "") + NOTE_VERIFY
        out.append("%s → verified (main 独立复核)" % iid)

    # ② 交叉引用
    for iid, txt in CROSS_REF.items():
        it = by_id.get(iid)
        if it is None:
            continue
        it["note"] = (it.get("note") or "") + txt

    # ③ 新开两单
    for iid, rec in NEW.items():
        if iid in by_id:
            raise SystemExit("%s 已存在, 拒绝重复开单" % iid)
        issues.append(rec)
        out.append("%s → %s 新开 (status=open)" % (iid, rec["owner"]))

    log["issues"] = issues
    bak = LOG + ".bak_20261115_2220_verify_209_210"
    shutil.copy2(LOG, bak)
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("备份:", bak)
    for line in out:
        print(" -", line)


if __name__ == "__main__":
    main()
