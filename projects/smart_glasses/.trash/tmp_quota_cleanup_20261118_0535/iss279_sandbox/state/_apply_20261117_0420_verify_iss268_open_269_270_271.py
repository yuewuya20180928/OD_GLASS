#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0420_verify_iss268_open_269_270_271.py
★main (moli) 2026-11-17 04:2x (cron fb67af40 队列自动派活)★
★① ISS-268 (hw-lead · 作业包 v3 §0 两行口径订正) 独立复验后落 `verified` ★
★② 新开 ISS-269 (hw-lead · 生成器三坑 X-3/X-4/B-2) + ISS-270 (sw-lead · 外部依赖自查) + ISS-271 (mech-lead · 板侧开口 S6 认领 + LED 位置约束) ★

★★**为什么是这三步 (★main 本轮 04:1x~04:2x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**advance.py --json = internal[] / approvals[] / waiting[] 全空** ⇒ 根因 = ★**hw-lead 名额被 ISS-268 占着 (fixing) + sw-lead / mech-lead 名下 open = 0 (队列真空)**★
  (★sessions_list 实测: hw-lead 会话 `e9f24cfc` status=**done** · abortedLastRun=false ⇒ ★**不是真在飞, 是"交完卷没人落账"的僵尸 fixing**★)
· ⇒ 本轮先复验并落账 ISS-268 (★放掉 hw-lead 名额★), 再自己挖活开三单 (★三个总工各一条, 不撞"一个 agent 同时一个写会话"铁律★)
· ★**ISS-268 复验全绿 (main 04:1x 实跑)**: §0 两处追加式订正注记在盘 + §0.1 拍板码映射权威表在盘 ·
  `state/merge.py` rc=0 (产出 406 · 阻塞 43 · 未闭合 235 · 冲突 0) · `state/gate_check.py` rc=0 (Q1 18/18 · Q2 3/3 · Q6 ✅) ·
  交卷单 `HANDOFF/2026-11-17_hw-lead_ISS268_板只改一次作业包v3_§0两行口径订正.md` B1~B6 六块齐全 ·
  受保护 5 件 md5 逐字节未变 (板 611b869e / 网表 e06c1dd6 / 脚表 287e7861 / BOM 94642d07 / .kicad_pro 3e504d2b) ★
· ★**本单自己挖的三条活 (依据全是盘上实读, 行号可复核)** ★
  ① ISS-269 (hw-lead): ★**「板只改一次」那三个会让那一趟白做的生成器坑** ★ —— `state/gen_pcb_netlist_board.py:591` 层数默认 **6** (盘上板 8 铜层) ·
     生成器里 `grep -c DNP` = **0** (43 个 DNP 位号零标记) · `value_of` 取 CSV 第一行 (板上 `U_EN_SW` Value 陈旧) ⇒ ★**在动板前先在生成器侧修掉 + 做成机器闸** ★
  ② ISS-270 (sw-lead): ★**老板 2026-11-12 02:02「不再发信, 全靠自己查资料」的第 ② 半 (义务: 挂着等外部的必须换成自己查 + 证据等级 + 降级方案) 在 SW 侧落地** ★
     —— `state/fragments/sw.yaml` 里 5 条仍写着「干等原厂 / 等外部回复 / 待确认」(SW-FW-B4 / fw_s2_test_gear / model_toolchain_q9_addendum / ars45_art_galaxy_sdk / reset_release_policy) ★
  ③ ISS-271 (mech-lead): ★**板那一趟的 MECH 侧两个"无人认领"** ★ —— ① 检修口/调试口开口没挂进作业包 S6 (★ISS-267 交卷单 B5 第 3 条点名的★)
     ② `D_LED_G` 物理位置 (S8 布线归零的卡点, 走线 93.49mm ⇒ 要么挪 LED 要么改网表) ★

★★**本轮共同边界** ★★
零外发 (老板 2026-11-12 02:02) · 零写板 · 零落表 · 零改网表/脚表/BOM · 零改判据阈值 · 零开新布线臂 (ISS-265 明令) ·
不写别人的分片 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-17"

BRIEF_269 = open(os.path.join(HERE, "dispatch_briefs",
                               "ISS-269_hw_gen_three_landmines.md"), encoding="utf-8").read()
BRIEF_270 = open(os.path.join(HERE, "dispatch_briefs",
                               "ISS-270_sw_external_dep_selfcheck.md"), encoding="utf-8").read()
BRIEF_271 = open(os.path.join(HERE, "dispatch_briefs",
                               "ISS-271_mech_port_s6_ledg_constraint.md"), encoding="utf-8").read()

VERIFY_268 = (
    "★main 2026-11-17 04:1x 独立复验 (★本机实跑, 不采信自述★) ★\n"
    "· ★**订正真的在盘上**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0 两处追加式订正注记在位 ⇒\n"
    "  ① 第 16 行「★订正注记 (★ISS-268 · 2026-11-17 03:4x · 追加式 · 上一行老字一字未删★)★」⇒ 权威映射 **A1 = V-3 (BAT_DET 分压链) · A2 = V-4 (R_ILIM 档位) · A3 = V-2 (USB ESD 落表方式 + W-1 架构轴)** (★老字「A1 (V-2 …) · A2 (V-3 …) · A3 (V-4 …)」保留未删★);\n"
    "  ② 第 15 行「★订正注记 … 上一行把 S4 算成了自由步 ⇒ 错★」⇒ 自由步集合 = **S1/S2/S3/S6/S7/S9/S10/S11/S12/S13 (10 步)**, **S4 不在里面 (卡 W-1/W-2)** · S8 也不在里面 (卡 P7/A1/W-4/mech);\n"
    "  ③ §0.1「拍板码映射权威表」在位 (★三行映射 + 五处权威出处 + 落表器 fail-closed 说明: 白名单互不相交 ⇒ 错位标签一律 rc=2 零写盘★) ★\n"
    "· ★**交卷单在盘**: `HANDOFF/2026-11-17_hw-lead_ISS268_板只改一次作业包v3_§0两行口径订正.md` (37.5 KB · 03:48) ⇒ **B1~B6 六块齐全** (★B2 验收标准逐条自评 · B3 证据分级 · B4 接口声明 · B5 未决项 · B6 自证复现命令★) ★\n"
    "· ★**门禁实跑**: `python3 state/merge.py` ⇒ rc=0 (★STATE.yaml 2026-11-17T04:13:18+08:00 刷新 · 产出 406 · 阻塞 43 (高危 33) · 未闭合需求 235 · **冲突 0** · 健康度 red★);\n"
    "  `python3 state/gate_check.py` ⇒ rc=0 (★**【Q1 交付齐备率】18/18** · 【Q2 证据分级率】3/3 · **【Q6 硬件真源闸】✅ 通过 (rc=0)**★) ★\n"
    "· ★**受保护 5 件 md5 逐字节未变 (main 04:1x 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ **零写板 · 零落表成立** ★\n"
    "· ★**作业包 md5 因本单追加而变**: 旧 `23ac29f2…` (37.5 KB) → 新 **`ddbf4b3e7e838fdc912cf9c2a1d6dec2`** (41.6 KB) ⇒ ★**ISS-266 正文里记的旧 md5 已陈旧 ⇒ 已在本轮落账里订正 (ISS-266 note) + 新基线写进 ISS-269 的 §8.1 任务书★ ★\n"
    "· ★**交卷报告自己点名的两条附带观察 (只登记, 不影响本单 verified)**: ① 作业包 §2 仍写「产品板 60×15」(★与 ISS-118 的 30 冲突, 已由 ISS-267 独立实测「60×30 套A 全绿 / 60×15 孔位不成立」佐证★) ② `land_v_values.py` 的 `A3_EXTRA` 只认 `1` 开头 ⇒ **V-2 架构③ (2 脚双向件) 没有独立落表码** ⇒ ★**两条归 main 排期, 不影响本单结论** ★"
)


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {it.get("id"): it for it in issues}

    # ---------------- ISS-268: 落 verified ----------------
    it268 = by_id["ISS-268"]
    assert it268.get("status") == "fixing", "ISS-268 状态不是 fixing (实际 %s)" % it268.get("status")
    it268["status"] = "verified"
    it268["verify_by"] = "main"
    it268["verify_date"] = TODAY
    it268["verify_result"] = VERIFY_268
    it268["fix_ref"] = ("HW/PCB/BOARD_ONEPASS_WORKPACKET.md (§0 两处追加式订正注记 + §0.1 拍板码映射权威表 · "
                        "新 md5 ddbf4b3e7e838fdc912cf9c2a1d6dec2) · "
                        "HANDOFF/2026-11-17_hw-lead_ISS268_板只改一次作业包v3_§0两行口径订正.md · "
                        "state/fragments/hw.yaml (frag_write.py 原子写)")
    it268["note"] = (it268.get("note") or "") + (
        "\n2026-11-17 04:2x (cron fb67af40 队列自动派活) ★**main 独立复验后落 verified** ★ "
        "(★实测: §0 两处追加式订正在盘 + §0.1 权威表在盘 · merge rc=0 · gate_check rc=0 Q1 18/18 · "
        "受保护 5 件 md5 逐字节未变 611b869e/e06c1dd6/287e7861/94642d07/3e504d2b★) "
        "★**hw-lead 名额由此释放** ⇒ 本轮同时新开 ISS-269 (生成器三坑) 给它 ★"
    )

    # ---------------- ISS-266: 订正作业包 md5 陈旧 ----------------
    it266 = by_id["ISS-266"]
    it266["note"] = (it266.get("note") or "") + (
        "\n★**2026-11-17 04:2x 订正 (main)**: ★**本单正文里记的作业包 md5 `23ac29f2…` 已陈旧** ★ ⇒ "
        "ISS-268 追加式订正后现值 = **`ddbf4b3e7e838fdc912cf9c2a1d6dec2`** (41.6 KB) ⇒ ★**以现值为准** ★ "
        "(★老字一字未删·留痕★)"
    )

    # ---------------- 新开三单 ----------------
    new_items = [
        {
            "id": "ISS-269",
            "title": ("★★★[★新主线·PCB 侧·生成器侧·内部活] ★★★**「板只改一次」那三个会让那一趟白做的生成器坑** "
                      "(★X-3: `gen_pcb_netlist_board.py:591` 层数默认 **6** 而盘上板是 **8 铜层** ⇒ 重出板会掉层★ · "
                      "★X-4: 生成器里 DNP 零命中 ⇒ **43 个 DNP 位号零标记**★ · "
                      "★B-2: `value_of` 取 CSV 第一行 ⇒ 板上 `U_EN_SW` 的 Value 陈旧★) "
                      "⇒ 生成器侧先修掉 + 独立机器闸 (★零写板·零落表·零改网表真源★)"),
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 04:1x 本机实读 (★行号可复核, 不是抄任何交卷报告★) ★\n"
                     "★**① X-3**: `state/gen_pcb_netlist_board.py:591` ⇒ `board.SetCopperLayerCount(int(os.environ.get(\"PCB_LAYERS\", 6)))` "
                     "⇒ ★**默认 6 层**; 盘上板实测 = **8 铜层 / 160.10×100.10mm / 186 封装** ⇒ ★**重跑不传 `PCB_LAYERS=8` ⇒ 板掉层** ★ "
                     "(★`HW/PCB/STACKUP.md` 自己记着 11-06 同型事故 ⇒ 复发型缺陷★) ★\n"
                     "★**② X-4**: `grep -c \"DNP\\|dnp\" state/gen_pcb_netlist_board.py` = **0** ⇒ ★**生成器没有 DNP 概念** ⇒ "
                     "43 个 DNP 位号零标记 (★`HW/check_netlist_contradiction_r3.py` FINDINGS 里的 F3★) ⇒ ★**S7 能不能做取决于生成器有没有这个特性** ★\n"
                     "★**③ B-2**: `state/gen_pcb_netlist_board.py:579-587` ⇒ `value_of` 只在 `if ref and ref not in value_of` 时写入 ⇒ "
                     "★**取该 ref 第一次出现那一行的 value** ⇒ 同 ref 多行 (本体型号行 + 各脚行) 时拿到的是脚行描述 ⇒ "
                     "板上 `U_EN_SW` 的 Value 陈旧 (★ISS-266 交卷单 B-2: 本体行在 `HW/netlist_v1.csv:442`, `value_of` 取第一行 `:440`★) ★\n"
                     "★**为什么现在做**: ★**板只改一次** ⇒ 那一趟必须一次产出正确的板 ⇒ 生成器的默认值/取值规则/缺失特性必须在动板前钉死 ★\n"
                     "★**交付**: ① 新闸 `HW/check_pcb_generator_defaults.py` (C1 层数默认 == 盘上板实测层数 · C2 DNP 支持 · C3 Value 取值规则 · `--selftest` ≥4 反向用例) "
                     "② 三处修复 (X-3 默认改 8 · X-4 加 DNP 支持 (★DNP 真源先自己查; 查不到 ⇒ 走 `PCB_DNP_LIST` 降级 + 登记 need, **不许自己编真源**★) · B-2 改本体行优先) "
                     "③ 沙盒复现 (`PCB_OUT=/tmp/...` ⇒ 字段级差异清单; **不许写盘上板**) ④ 交卷单 B1~B6 + 分片 (frag_write.py) + 作业包 §8.1 追加式 ★\n"
                     "★**类别**: 内部活 · 生成器/代码侧 · 零写板 · 零落表 · 零改网表/脚表/BOM ⇒ **不是老板级拍板** ★"),
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 04:2x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 04:1x 本机实读** ★ "
                     "(★X-3: `gen_pcb_netlist_board.py:591` 默认 6 层 vs 盘上板 8 铜层 · X-4: 生成器 DNP 零命中 · "
                     "B-2: `value_of` 取第一行 ⇒ `U_EN_SW` Value 陈旧★) ★\n"
                     "★**本轮 advance.py internal 段为空** (★hw-lead 名额被 ISS-268 僵尸 fixing 占着 + sw-lead/mech-lead 名下 open = 0 ⇒ 队列真空★) "
                     "⇒ ★**本单是 main 自己挖的活** (★任务书 `state/dispatch_briefs/ISS-269_hw_gen_three_landmines.md`★) ★\n"
                     "★**零写板 · 零落表 · 零改网表真源 · 零开新布线臂** (★ISS-265 明令: lane 交叉还是 45 之前不许再开臂★) ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_269,
        },
        {
            "id": "ISS-270",
            "title": ("★★[★主线内·SW 侧·政策落地·内部活] ★★**老板 2026-11-12 02:02「不再发信, 全靠自己查资料」的第 ② 半"
                      "在 SW 侧落地** ⇒ ★**SW 侧还挂着 5 条「干等原厂 / 等外部回复 / 待确认」** ★ "
                      "(★SW-FW-B4 · fw_s2_test_gear · model_toolchain_q9_addendum · ars45_art_galaxy_sdk · reset_release_policy★) "
                      "⇒ 逐条换成【自己查的结果 + 证据等级 + 降级方案】(★不许把外部依赖挂着当阻塞项★)"),
            "severity": "medium",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 04:2x 实读 `state/fragments/sw.yaml` (★行号可复核★) ★\n"
                     "★**E-1** id `SW-FW-B4` (:986-993 · needs_from main/hw-lead · waiting_since 2026-10-26): 「S2 无板先验 L2 层器材未定 "
                     "(逻辑分析仪 + USB 协议分析仪 + SPI-NOR 空板) ⇒ P1 (BOOT 电平/时序) 与 P3 (BOOT 态 VID:PID) **只能干等原厂**」 ★\n"
                     "★**E-2** key `fw_s2_test_gear` (:1143-1151 · to=main): 「没有它们, P1/P3 只能等原厂」 ★\n"
                     "★**E-3** key `model_toolchain_q9_addendum` (:1230-1236): 「③ 或等原厂提供'许可由原厂承担'的预编译模型」 ★\n"
                     "★**E-4** key `ars45_art_galaxy_sdk` (:1237-1243 · waiting_on=vendor): 「Art.Galaxy 工具链包 + 手册 ⇒ 提供形式 (docker 镜像? SDK? 需授权/NDA?)」 "
                     "⇒ ★**替代已经实测存在**: `rknn3-toolkit 1.2.0` @ `/home/yuewuya/miniconda3/envs/rknn3` (★ISS-263 实测 `config('rk3572')` rc=0 · 产物 md5 `97a34fff…` 三次一致★) ★\n"
                     "★**E-5** key `reset_release_policy` (:2153): value 里写「PG源DNP待确认」 ⇒ ★**那不是外部依赖, 是落表真源问题** ★\n"
                     "★**本单要落的一条判定口径 (进交卷单)**: ★**\"外部依赖\" = 只有外部方能回答的; 凡本仓库 / 公开资料 / 本机实跑能回答的, 一律不是外部依赖** ★\n"
                     "★**交付**: ① 新文档 `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` (每条: 原文 + 自己查了什么 + 结论 + 证据等级 + **降级方案 (必须项)** + 还需要谁做什么) "
                     "② `state/fragments/sw.yaml` 5 处**追加式**改写 (★老字不删 · 走 frag_write.py★) ③ 交卷单 B1~B6 + 分片 ④ E-1 的「板到手即跑」命令清单 (★本机没板 ⇒ 标 [推算] 未实测★) ★\n"
                     "★**类别**: 内部活 · 政策落地 + 口径收口 · 零外发 · 零采购 · 零写板 · 零落表 ⇒ **不是老板级拍板** ★"),
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 04:2x (cron fb67af40 队列自动派活) 新开 ★**依据 = 老板 2026-11-12 02:02 政策第 ② 半 (义务侧) + "
                     "main 本轮 04:2x 实读 sw.yaml 的 5 条挂账** ★ ⇒ ★**任务书 `state/dispatch_briefs/ISS-270_sw_external_dep_selfcheck.md`** ★\n"
                     "★**sw-lead 名下本轮无 open 队列 (真空)** ⇒ 本单是本轮给 sw-lead 的活 ★\n"
                     "★**零外发 · 零采购 · 零写板 · 零落表 · 零改既有 SW 文档的既有结论** ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_270,
        },
        {
            "id": "ISS-271",
            "title": ("★★[★主线内·MECH 侧·板侧认领·内部活] ★★**板那一趟 (S1~S13) 的 MECH 侧两个「无人认领」** ★ "
                      "① ★**检修口/调试口开口没挂进作业包 S6** (★ISS-267 交卷单 B5 第 3 条点名的★) "
                      "② ★**`D_LED_G` 物理位置** (★S8 布线归零卡点 · `LED_G_D` 走线 93.49mm ⇒ 要么挪 LED 要么改网表 · 归谁 = mech + 老板★) "
                      "⇒ ① 出板侧开口 S6 规格页 (机算 · 板框三套 × 开口可行性) ② 出 LED 位置的机械约束条件 (★只给条件, 不定坐标★)"),
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 04:2x 实读 + ISS-267 交卷单原文 (★行号可复核★) ★\n"
                     "★**① 开口无人认领**: ISS-267 交卷单 B5 第 3 条原文 ⇒ 「作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md:301`/`:310` 仍写产品板 60×15 (与 ISS-118 的 30 冲突), "
                     "`:164`/`:289` 里 MECH 侧只认领了 `D_LED_G` ⇒ ★**检修口开口在「板只改一次」那一趟里无人认领**, 建议把本单 §1/§3 挂进 S6」 ★ "
                     "⇒ ★**实测: 作业包 §3 的 S6 一节里确实没有「开口」这一项** ⇒ 照这样跑那一趟会漏掉 ★\n"
                     "★**② `D_LED_G`**: `HW/PCB/LAYOUT_FIX_SPEC.md:244` 归谁列 = **mech + 老板**; `LED_G_D` 走线 **93.49mm** "
                     "(`R_LED_G.2`@7.5,62.6 ↔ `D_LED_G.1`@100.8,56.6) ⇒ ★**要么挪 LED, 要么改网表** ★ "
                     "⇒ ★**S8 卡点表把它列为「唯一可能让整趟做完仍然投不了板」的步之一** (作业包 `:307`) ★\n"
                     "★**交付**: ① 新规格页 `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (§1 开口约束 ★引用既有结论★ · §2 `jd_y0` 区间 (★`--json` 实测★) · "
                     "§3 板框三套 (160×100 台架板 / 60×30 套A / 60×15) × 开口可行性判定 (★脚本实算★) · §4 X 向待定型号的区间 (★`[0数据]`/`[推算]`★) · §5 给 hw-lead 的 S6 认领句) "
                     "② `D_LED_G`: 先答「结构侧有没有既有规定」(★查不到写 `[0数据]`★) + 板侧候选位置的机械约束条件 (★只给条件与坐标空间, 不定坐标★) + ★**自己实算一遍 93.49mm**★ "
                     "③ 交卷单 B1~B6 + 分片 (frag_write.py) ★\n"
                     "★**类别**: 内部活 · 板侧规格页 + 机算 · 零写板 · 只许新增 MECH 文件 · 零落表 ⇒ **不是老板级拍板** ★"),
            "owner": "mech-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 04:2x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 04:2x 实读 + ISS-267 交卷单 B5 第 3 条** ★ "
                     "⇒ ★**任务书 `state/dispatch_briefs/ISS-271_mech_port_s6_ledg_constraint.md`** ★\n"
                     "★**mech-lead 名下本轮无 open 队列 (真空; 三个 deferred 单都随 MECH 全线暂缓到整机阶段, 不动)** ⇒ 本单是本轮给 mech-lead 的活 ★\n"
                     "★**边界**: 只许新增 MECH 文件 · 零改既有 MECH 三脚本 (md5 逐字节不变) · 零写板 · 零落表 · 不许改作业包 (那是 hw-lead 的文件) ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_271,
        },
    ]

    for it in new_items:
        assert it["id"] not in by_id, "%s 已存在" % it["id"]
        issues.append(it)

    bak = os.path.join(HERE, "issue_log.yaml.bak_20261117_0420_verify268_open269_270_271")
    shutil.copy2(LOG, bak)
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))

    for iid, brief in (("iss269", BRIEF_269), ("iss270", BRIEF_270), ("iss271", BRIEF_271)):
        atomic_write(os.path.join(HERE, "tasks", "advance_%s.md" % iid), brief)

    print("✅ ISS-268 落 verified (verify_by=main, verify_date=%s)" % TODAY)
    print("✅ ISS-266 note 追加: 作业包 md5 陈旧订正 (23ac29f2… → ddbf4b3e…)")
    print("✅ 新开 3 条: ISS-269 (hw-lead) / ISS-270 (sw-lead) / ISS-271 (mech-lead) — status=open")
    print("   备份: %s" % bak)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
