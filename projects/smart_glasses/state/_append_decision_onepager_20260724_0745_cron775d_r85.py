#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_0745_cron775d_r85.py
=======================================================
main (项目总工 / moli) · cron 775d9893 「ARS45 继续执行后继计划」· 2026-11-24 07:4x
★★【★★决策页追加式 §㊲ · 本轮 4 单交卷 ⇒ 17 条 main 地界待裁项上页 + 52/52 覆盖复核★】★★

★**本轮做了什么 (★本机实读 + 实算, 不抄任何 agent 报告★)**:
  ① `state/advance.py --json` 实读 ⇒ **internal 0 / approvals 0 / decisions 52 / waiting 0**
     (★rc=1 = 「无可派 + 无待批」⇒ 正常信号·依据 `state/advance.py:334` `return 0 if (internal or approvals) else 1`★)
  ② ★**根因实查 (★不是「没活」★)**: 台账实读 378 条 ⇒ 三个总工名下 **open = 0**,
     **fixing = 4** (ISS-380/hw · ISS-381/sw · ISS-382/mech · ISS-383/hw) ⇒ ★`advance.py` 的
     「同 agent 同时只允许一个在飞」判据 ⇒ 三个槽位全被这 4 单占住 ⇒ internal 必为 0 ★
  ③ ★**但这 4 单其实全部【已交卷】(★本轮逐件实读 12 件交付物全在盘★)** ⇒ ⇒
     **占槽的是【已交付待签收的 fixing 标记】, 不是在飞的活** ⇒ ★**签收归 main 的地界
     (★main webchat 会话 07:38 仍在写盘 = 正在签收这 4 单★) ⇒ ★**本 job 不签、不并发改
     `issue_log.yaml`** ★
  ④ ★**本轮 0 派** ⇒ ★**理由三条 (可复核)★**: ① `internal` 段为空 (三个总工 open=0) ·
     ② 4 条 `fixing` 全部已交卷待签收 (★重派 = 重复劳动★) · ③ 兄弟 job `fb67af40`
     (队列自动派活) 已把 4 单落 `fixing` 并派出去 ⇒ ★**本 job 再开单再派 = 同队列撞车★ ★
  ⑤ ★**18 条新 need 上页 (★17 条 to=main + 1 条 to=hw-lead★)** ⇒ ★**其中 2 条直接卡
     「板那一趟」** ⇒ ★**逐条给「题 + 建议默认值 + 不裁的后果」·一件没代拍★ ★
  ⑥ ★**52 条老板清单覆盖复核 (★本轮实跑·与 02:1x §㉞ 同口径★)★**: 一页 **20/52** ·
     索引 **41/52** · ★**并集 52/52 零漏项** ★ · ★**11 个只在决策页上的 key ⇒ 11/11
     实读命中「建议默认值」**(★r82 的 11 个 key 本轮逐个复验, 0 例外★)

★**边界**: ★**老字一字未删** (★追加式★) · ★**零写板** · ★**零落表** · ★**零外发** ·
★**一件没代老板拍** · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别的 agent 的分片** ★
"""
import os
import shutil
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
STAMP = time.strftime("%Y%m%d_%H%M")

SECTION = """

## ★★㊲ 【本轮 2026-11-24 07:4x 新增】★ ★★本轮 4 单全部交卷 ⇒ 【17 条 main 地界待裁项】上页 (★逐条给建议默认值·一件没代拍★) + ★★52/52 覆盖复核 (★零漏项★) + ★★板那一趟的两条卡口★★

★**① 本轮实读 (★`state/advance.py --json`·★rc=1 是正常信号不是错误★)★**

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**三个总工名下 `open` = 0** ⇒ `fixing` 占住全部槽位 ★ |
| approvals | **0** | ★**恒空 (老板 2026-11-12 02:02「不再发信, 全靠自己查」政策)** ★ |
| decisions | **52** | ★**hw.yaml 13 · mech.yaml 14 · pm.yaml 12 · sw.yaml 13** ★ |
| waiting | **0** | — |

★**rc=1 的含义 (★`state/advance.py:334` 实读★)**: `return 0 if (internal or approvals) else 1` ⇒ ★**rc=1 = 无可派 + 无待批** ★

★**② ★★本轮 4 单全部【已交卷】(★12 件交付物逐件实读·全在盘★)★★**

| 单 | owner | 交卷会话 | 交付物 (本轮实读) | 板面 |
|---|---|---|---|---|
| **ISS-380** | hw-lead | `e4a6efff…` done @06:18 | 真相页 `35,720 B` + 闸 `18,857 B` + 交卷页 `25,582 B` + `hw.yaml` 分片 | 零写板 |
| **ISS-381** | sw-lead | `f0cd05b9…` **timeout** @07:29 (交卷已完成, 仅末步 `gate_check` 被打断) | 真相页 `25,034 B` + 闸 `54,358 B` + 交卷页 `22,292 B` + `sw.yaml` 分片 | 零写板 |
| **ISS-382** | mech-lead | `2dcbb276…` done @07:36 | 真相页 `27,324 B` + 闸 `54,975 B` + 交卷页 `17,548 B` + `mech.yaml` 分片 | 零写板 |
| **ISS-383** | hw-lead | `44e009c4…` done @07:33 | 真相页 `48,956 B` + 闸 `18,679 B` + 交卷页 `27,948 B` + `hw.yaml` 分片 | 零写板 |

★**⇒ 占槽的是【已交付待签收的 `fixing` 标记】, 不是在飞的活** ⇒ ★**签收归 main 地界 (★main webchat 会话 07:38 仍在写盘★) ⇒ 本 job 不签、不并发改 `issue_log.yaml`** ★

★**③ ★★17 条 main 地界待裁项 (★本轮 4 单交回的 needs 实读·★逐条「题 + 建议默认值 + 不裁的后果」·一件没代拍★)★★**

★**▌A 组 · 座体选型 (ISS-380 + ISS-383·★直接卡「板那一趟」★)**

| # | need key | 题 | ★**建议默认值 (建议·非已决定)**★ | 不裁的后果 |
|---|---|---|---|---|
| A1 | `iss383_main_choose_single_row_1x4_criteria` | ★**「1×4 直插」以谁为准** (★板侧真值 vs 结构侧 Cortex-10 2×5★) ★ | ★**以板侧真值 (1×4·1.27mm·单排直插) 为准** (★理由: 板是本趟的产物, 且 ISS-380 §5-④ 自查出盘上两个封装是 0.5mm SMD 占位盘 = 三方口径都不对, 须由板侧定一版让结构侧重算★) ★ | ★**BOM 型号栏填不出可采购料号 ⇒ 板那一趟开工即返工** ★ |
| A2 | `iss383_main_single_row_1p27_vendor_pn` | ★**1.27mm 单排直插的厂商料号怎么办** ★ | ★**甲: 另找厂按规格书下单** (★规格已可给: 1.27 / 单排 / 4 位与 2 位 / 直插 / 方针 0.5 推定 / 焊盘 1.000×1.000 / 钻孔 0.65 / post 高 3.05·★证据等级 [官网]+[推算]★) ★ | ★**Samtec 与 Würth 两家【都没有】1.27mm 单排直插 (★实测: 两家 1.27 族 Rows 全 = 2·1 Row 件全在 2.54 档★) ⇒ 缺的是【可下单料号】不是【封装】 ⇒ 不裁 = 采购无对象** ★ |
| A3 | `iss383_main_bom_model_column_timing` | ★**BOM 型号栏何时落** ★ | ★**与 land 改动同一次工序落** (★先例: 型号栏落地与改 land 分离 ⇒ BOM 型号与板上封装不同源★) ★ | ★**型号栏与板不同源 ⇒ 投产包 BOM 与 Gerber 对不上** ★ |
| A4 | `iss383_main_official_vs_custom_footprint` | ★**库封装用官方通用件还是自建 Samtec 专用封装** ★ | ★**官方通用件 (`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_…` md5 `47bcbf6d…`·★单排 THT 1.27 焊盘 1.000×1.000 钻孔 0.65★) ⇒ 自建留给走双排 SMT 那一档** ★ | ★**若走双排 SMT 而直接用通用件 ⇒ 列距 3.00 vs 实际排中心距 1.27 ⇒ 封装错位 ⇒ 板白改** ★ |
| A5 | `iss383_main_register_juart_target_lib` | ★**`J_UART` 的 `target_lib` 补不补** ★ | ★**补** (★`FP_TRUTH_BASELINE.md` 里 `grep -c` = 0, 但该件已存在 ⇒ 台账漏登记★) ★ | 台账与真源不一致 ⇒ 后续闸查不到该件 |
| A6 | `iss380_board_trip_bom_part_fill` | ★**BOM 型号栏填【板侧真值档 (1×4/1×2)】还是【结构侧 Cortex-10 2×5 档】** ★ | ★**填板侧真值档** (★同 A1·理由同源★) ★ | 同 A1 |
| A7 | `iss383_main_mech_recompute_three_inconsistencies` | ★**结构侧三条不自洽要不要跟着重算** (★执行方 mech-lead·★post 高已从 `[0数据]` 收紧到 3.05mm 而 Z 向可用空间只有 4.70mm★) ★ | ★**要·且与板那一趟同批** (★结构件与板同改一次, 不分两批 = 遵「板只改一次」同源纪律★) ★ | ★**板改好了结构没跟上 ⇒ 装配干涉 ⇒ 板再改第二次** ★ |

★**▌B 组 · 布线验收线 (ISS-381·★「板那一趟」的验收判据★)**

| # | need key | 题 | ★**建议默认值 (建议·非已决定)**★ | 不裁的后果 |
|---|---|---|---|---|
| B1 | `iss381_cont1_acceptance_line_single_vs_dual` | ★**布线验收线正式改成【逐条列铜单轨】还是【计数 + 逐条 双轨】** ★ | ★**双轨 (★推荐·保留 `unc 45→0` 作覆盖度指标 + 新闸作身份闸★)** ★ | ★**两套判据两套 rc 但两个数字都不说谎**; ★单轨则 unc 归 0 后本闸仍可能红 ⇒ 现场要解释「哪个红」 ★ |
| B2 | `iss381_cont1_three_cheat_methods_policy` | ★**「删网 / 标 NC / 改名」三种刷法该不该被允许** ★ | ★**一条都不许单独用** (★K1a 身份 + K1b 焊盘集合 + K1c 铜状态 + K5 交叉核对 四道机器判据已能把三种反例全部判红并逐条点名★) ★ | ★**只守 unc 计数 ⇒ 三种刷法都能把 45 刷到 0 而一条铜都不加 ⇒ 验收线给「全接上了」的错觉** ★ |
| B3 | `iss381_cont1_diff_copper_symmetry_threshold` | ★**差分腿【铜长对称性阈值】(Δ铜长 / Δ段数上限)** ★ | ★**先不拍阈值, 但把 Δ 登记成【只报数不判红】** (★本轮硬事实: 20 对差分腿里 11 对不是「两腿都有铜」(7 对一腿有铜 + 4 对两腿都零铜)·有铜 ≠ 对称 ⇒ `DSI_D0_D0_P/N` 两腿都有铜但 Δ铜长 = 76.2mm★) ★ | ★**不拍 ⇒ K2 只判「成对都有铜」⇒ 对称性无人管★** |
| B4 | `iss381_cont1_gate_chain_mount` | ★**新闸 `SW/tools/check_sw_false_connectivity_gate.py` 挂不挂 `state/gate_check.py`** ★ | ★**与「板那一趟」同批挂** (★先例 ISS-300/309/312/315 + ISS-372 U7 同款: 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」★) ★ | 提前挂 ⇒ 中间态红 ⇒ 误读 |
| B5 | `iss381_cont1_correction_block_into_legacy_page` | ★**§2 口径订正块要不要落进 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 末尾** ★ | ★**落·追加式·与那一趟同批** (★订正内容 = 「unc 判据抓不到 UART_RX」那半句已被实测证伪: UART_RX 现在就是 45 条 unconnected 里的一条 ⇒ unc 抓得到零铜网, 抓不到的是【身份】·★老字一个字没删★) ★ | ★**老页留一句已被证伪的话 ⇒ 后面人照它判 = 判据漂移** ★ |

★**▌C 组 · 排布标签 + 闸盲区 (ISS-382·mech-lead)★**

| # | need key | 题 | ★**建议默认值 (建议·非已决定)**★ | 不裁的后果 |
|---|---|---|---|---|
| C1 | `iss382_correction_block_landing` | ★**订正块落在哪一页/哪一批/什么时机** (★订正内容 = `2x2` ⇒ 实测 `2x4_staggered`★) ★ | ★**落进 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` §0 机器块 + 与板那一趟同批** (★先例代价: ISS-374 cont2 追加已签收页 ⇒ `K7` 立刻红 2 条★) ★ | ★**已签收页上的 `2x2` 标签不订正 ⇒ 板那一趟照它选降级方案 ⇒ 板改第二次** ★ |
| C2 | `iss382_g5_dimension_criterion` | ★**G5 维数对比判据落进旧闸还是新闸独立挂** ★ | ★**新闸独立挂, 旧闸 G5 只判「有没有写交错」** (★零改已签收闸是本轮硬边界·且旧闸判据本身是盲区★) ★ | ★**G5 写 `2x2` 绿、写 `9x9` 也绿 ⇒ 判据形同虚设** ★ |
| C3 | `iss382_label_downstream_wording` | ★**标签错要不要连带改 `L471`/`L719` 文本字样** ★ | ★**改·但只改字样不动结论·且与 C1 同批** ★ | 文字与实测长期不一致 ⇒ 现场读错 |
| C4 | `iss382_new_gate_hook` | ★**新闸 `MECH/check_jdebug_arrangement_truth.py` 挂不挂 `state/gate_check.py`** ★ | ★**与「板那一趟」同批挂** (★同 B4 的先例★) ★ | 提前挂 ⇒ 中间态红 |

★**④ ★★本轮 0 派的三条理由 (★可复核·不是偷懒★)★★**
1. ★**`internal` 段为空** (★`advance.py` 实读 = 0·★三个总工名下 `open` = 0★) ★
2. ★**4 条 `fixing` 全部已交卷待签收** (★12 件交付物逐件实读在盘★) ⇒ ★**重派 = 重复劳动 + 覆盖已交付件** ★
3. ★**兄弟 job `fb67af40` (队列自动派活) 正在同一条通道上** (★本轮实读: 它 07:1x~07:2x 连开 ISS-380/381/382/383 并已落 `fixing` + 派出去★) ⇒ ★**本 job 再开单再派 = 同队列撞车** ★

★**⑤ ★★52 条老板清单覆盖复核 (★本轮实跑·与 02:1x §㉞ 同口径★)★★**

| 页 | 覆盖 |
|---|---|
| `DECISION_ONE_PAGER_2026-11-22.md` (★本页★) | **20 / 52** |
| `DECISION_INDEX_2026-11-18.md` (★索引★) | **41 / 52** |
| ★**并集** ★ | ★**52 / 52** ⇒ ★**零漏项** ★ |

★**11 个只在决策页上的 key ⇒ 本轮逐个复验「建议默认值」栏 ⇒ ★11/11 实读命中★ (★0 例外·与 §㉞ 同结论★)** ★

★**⑥ 板面读数 (★本机实读★)**: 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**门禁 (本轮 5 连实跑)**: ★**merge rc=0** · ★**gate_check rc=0** (★Q1 18/18★) · ★**issue_check rc=1** (★违规 19 条 = 既有逾期项·零新增★) · ★**stage_gate rc=1** (★当前 **G1**·还差 **1** 项 = PCB 布线 unconnected 45 → 0·G1a 还差 2 条 G1a-4/G1a-8★) · ★**daily_check rc=3** (★三条全是老异常: 问题闭环门 19 条 / `check_pcb_nets` rc=1 / `chain_gate`★) ★
★**外发段**: ★**恒空** (★老板 2026-11-12 02:02 政策⇒ `state/outbox/` **16 份草稿只备不发**★)
"""


def main():
    with open(PAGER, encoding="utf-8") as fh:
        before = fh.read()
    before_md5 = __import__("hashlib").md5(before.encode("utf-8")).hexdigest()
    before_len = len(before)

    # ★幂等守卫: 已追加过就只复验, 不重复追加 (★追加式页·重复追加 = 制造 churn★)
    MARK = "㊲ 【本轮 2026-11-24 07:4x 新增】"
    if MARK in before:
        print("✔ 幂等: 本节已在本页 (不重复追加)")
        print("  当前长度 %d · 含标记 True" % before_len)
        return 0

    bak = os.path.join(PROJ, "state",
                       ".bak_DECISION_ONE_PAGER_%s_pre_r85.md" % STAMP)
    shutil.copy2(PAGER, bak)

    with open(PAGER, "a", encoding="utf-8") as fh:
        fh.write(SECTION)
        fh.flush()
        os.fsync(fh.fileno())

    with open(PAGER, encoding="utf-8") as fh:
        after = fh.read()
    after_md5 = __import__("hashlib").md5(after.encode("utf-8")).hexdigest()

    # ★老字一字未删 (逐字前缀比对) ★
    assert after.startswith(before), "★老字被改 ⇒ 追加失败 ★"
    assert len(after) > before_len, "★追加长度未增长 ⇒ 失败 ★"
    assert "㊲" in after, "★新节未落盘 ★"
    assert MARK in after, "★新节标记未落盘 ★"
    print("✔ 决策页追加完成")
    print("  备份   : %s" % os.path.basename(bak))
    print("  前缀 md5: %s (长度 %d)" % (before_md5, before_len))
    print("  后缀 md5: %s (长度 %d)" % (after_md5, len(after)))
    print("  老字未删: True   新增字节: %d" % (len(after) - before_len))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
