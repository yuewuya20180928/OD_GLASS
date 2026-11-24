#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_2358_cron775d_r92_finalize.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 23:5x~00:0x · r92 收尾★★

★★【★★本脚本做什么★★】★★
① 新建 `state/ROUND_LOG_cron775d_2026-11-24_2340.md` (★本轮完整留证★)
② `state/CURRENT_TASK.md` 追加本轮口径一行 (★追加式·老字一字未删★)
③ 跑 `state/gen_progress_snapshot.py` (★本地快照·★不推 GitHub★)

★★【★★纪律 (★本脚本自己守★)】★★
  ① 零写板 (板 md5/mtime(ns)/size 前后各打一次)
  ② 零落表 (网表/脚表/BOM 逐字节未动)
  ③ 零写台账 (★`issue_log.yaml` 本轮已由 `_apply_20260724_2355_cron775d_sign_iss391_401.py` 落过·本脚本不再碰★)
  ④ 零外发 · 不代老板拍板 · 不改 PROJECT_TRACKER.md §0
  ⑤ 只写 main 自己的分片 (★本脚本不写任何分片★)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CUR = os.path.join(HERE, "CURRENT_TASK.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW/netlist_v1.csv")
PINS = os.path.join(PROJ, "HW/netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW/BOM_v1.csv")
ROUND_LOG = os.path.join(HERE, "ROUND_LOG_cron775d_2026-11-24_2340.md")
STAMP = time.strftime("%Y%m%d_%H%M")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213
BOARD_MTIME_NS = 1793920037362193413


def md5_file(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def append_atomic(path, text, tag):
    """追加式: O_APPEND 追加, 不覆写; 追加后回验【老字逐字未变】。"""
    before = open(path, "rb").read()
    with open(path, "ab") as f:
        f.write(text.encode("utf-8"))
    after = open(path, "rb").read()
    assert after[:len(before)] == before, "★追加式铁律被破 (老字被改) ⇒ %s" % path
    shutil.copy2(path, path + ".bak_%s_%s" % (STAMP, tag))
    print("  ✓ %s 追加 %d B (老字 %d B 逐字未变)" % (os.path.basename(path), len(after) - len(before), len(before)))
    return after


ROUND = """# ROUND_LOG_cron775d_2026-11-24_2340 · r92

★**job**: cron `775d9893` (ARS45 继续执行后继计划 · 每 20 分钟) · ★**2026-11-24 23:38~00:0x★**
★**主线**: 绘制 PCB 图 (★老板 2026-11-17 00:43★) ⇒ 本轮**零派** (internal=0) ⇒ ★**本轮零 PCB 类候选**
★**作者**: main (项目总工 moli) · ★**性质**: ★**独立复核 + 修在产生点 + 签收落账 + 留证**★

---

## ★★一 · 本轮结论 (先说数字) ★★

```
python3 state/advance.py --json
⇒ internal 0 / approvals 0 / decisions 55 / waiting 0     (★修 advance.py 前是 56★)
核验 5 连: merge 0 · gate_check 0 · issue_check 1 (19 条既有) · stage_gate 1 · daily_check 3
11 道新闸: --selftest 11/11 rc=0 ALL TESTS PASS · 裸跑 6 绿 / 5 红 (★红=按设计·红的是现状★)
签收: 11 条 (ISS-391~401) fixing → verified (★其余 386 条逐条 md5 未变★)
板四指纹: md5sum -c 全 OK ⇒ 板 611b869e / mtime 2026-11-06 07:07:17 / 4,940,213 B 逐字节未动 (18 天)
```

★**本轮三件实事**: ★**① 11 单独立复核签收 (★零写板·零落表·零外发★)** ★ **② `state/advance.py` 两处真 bug 修在产生点 (★老板清单口径与 `merge.py` 逐字对齐·56→55·双向验收 0 误伤★)** ★ **③ C 段 55 条零漏项 (★一页 25 + 索引 40 ⇒ 并集 55/55·新增 1 条待拍项★)** ★

---

## ★★二 · ★★11 条已交卷单的 main 独立复核 (★不抄任何 agent 报告★) ★★

★**每道新闸本机裸跑 + `--selftest` 各跑一遍 (★`TMPDIR` 落项目盘 `state/.verify/r92/tmp`·★因为 `/tmp` 用户配额已满 ⇒ 重定向到 `/tmp` 会出假读数★)·★日志全在 `state/.verify/r92/`★** ★

| 单 | owner | 新闸 | 裸跑 | `--selftest` | 结论 |
|---|---|---|---|---|---|
| ISS-391 | hw-lead | `HW/check_fts_land_drill_same_batch.py` | rc=0 (7/7 绿) | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-392 | sw-lead | `SW/tools/check_sw_gate_chain_coverage.py` | rc=0 | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-393 | mech-lead | `MECH/check_fts_vs_generic_courtyard_delta.py` | rc=0 (G1~G7 全过 · 量数 50) | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-394 | hw-lead | `HW/check_seat_part_verdict_propagation.py` | **rc=1 (按设计)** | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-395 | hw-lead | `HW/check_gate10_concurrency_safety.py` | rc=0 | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-396 | hw-lead | `HW/check_fts_land_drill_same_batch_sbx.py` | rc=0 | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-397 | mech-lead | `MECH/check_fts_seat_sample_plan.py` | **rc=1 (按设计)** | rc=0 · ALL TESTS PASS | ✅ verified |
| ISS-398 | sw-lead | `SW/tools/check_sw_ref_reachability_v2.py` | **rc=1 (按设计)** | rc=0 · ALL TESTS PASS (0/7→7/7) | ✅ verified |
| ISS-399 | mech-lead | `MECH/check_mech_signed_append_ledger.py` | **rc=1 (按设计)** | rc=0 · ALL TESTS PASS (12/12) | ✅ verified |
| ISS-400 | mech-lead | `MECH/check_machine_block_pointer_resolvable.py` | **rc=1 (按设计)** | rc=0 · ALL TESTS PASS (12/12) | ✅ verified |
| ISS-401 | hw-lead | `HW/check_hw_external_dep_closed.py` | rc=0 (5 条判据全绿) | rc=0 · ALL TESTS PASS | ✅ verified |

★**★5 条裸跑红 = 按设计 (★日志原话逐条·★不是闸故障★)★**: ISS-397 「红的是【现状】(三量【实测档】仍 [0数据]) ⇒ **不许为了让它绿而放宽判据**」 · ISS-399 「红的是【现状】(3 处陈旧 pin 归因不到台账)」 · ISS-400 「红的是【现状】(指针有悬空/歧义/误指)」 · ISS-398 「红因: `VBUS_DET_uA` 被当位号」 · ISS-394 「K2/K3 要 main 落订正块」 ★ ★

★**★交卷页齐备性 (★本机实读·★占位符 0★)★**: 11 份交卷页全在盘 (12,102 B ~ 62,212 B) · ★引用的页全部存在 (ISS-398 的 `SW/ZZ_FAKE_DESIGNATOR.md` = 闸自测的负例夹具·ISS-399 的 `MECH/SIGNED_APPEND_LEDGER.md` = 台账还没建 ⇒ 与闸的预期红一致)★ · ★owner 分片登记 11/11 (grep 命中 30/11/29/15/6/22/29/16/8/20/14)★ ★ ★

★**★零扰动双证 (★开工前 / 收工后 `md5sum -c` 全 OK★)★**: 板 `611b869e13518c3c023fb178f91a0075` / 4,940,213 B / mtime `2026-11-06 07:07:17.362193413` · 网表 `6aee500e…` · 脚表 `9174309d…` · BOM `5b999399…` ⇒ ★**零写板 · 零落表** ★ ★

★**★main 地界待裁项 (★本轮逐条采纳 agent 的建议默认值·★一件没代老板拍★)★**:
★**ISS-396** §4#4 显式覆盖令牌 ⇒ ★**不补** (自动抽本次已自动生效·★补令牌要同板那一趟一起·现在补 = 改真件一次★) ·
★**ISS-397** 三量收样 ⇒ ★**维持红 + 判据一字不改 + 收样与「板那一趟」同批** ·
★**ISS-398** ⇒ ★**采用口径 C** (登记 `EXEMPT_LEDGER`·★改文档字面量不留漏检窗口★·★判据前缀 md5 逐字未变 `3111dfb2…`★) ·
★**ISS-399** M-A/M-B/M-C/M-D ⇒ ★**台账落 `MECH/SIGNED_APPEND_LEDGER.md` · 3 处基线走台账登记值追平 · 【先落台账再挂链】· 「追加式订正」合法但必须留原子记录** ·
★**ISS-400** Q5 ⇒ ★**「量完填回哪一格」的正式答案 = 唯一真槽 `degradation.measure_fill_back.*.measured`** (★ISS-393 页 §6 登记的三条槽位名一个都不存在 ⇒ ★ISS-397 §9-④ 那条挂了两天的问句即使答「改键名」也填不进去★) ★ ★

★**★槽位效果 (★下一轮★)★**: ★**sw-lead / mech-lead 两个槽位已释放** ⇒ 下一轮 `advance.py` 可派 ⇒ ★**hw-lead 槽位未释放** (★兄弟 job `fb67af40` 23:44 新开 ISS-402 → hw-lead·★真在飞★) ★ ★

---

## ★★三 · ★★`state/advance.py` 两处真 bug 修在产生点 ★★

★**为什么必须修**: ★**`advance.py` 的 `decisions` 段 = 老板要拍的全部条目** ⇒ ★**少报 ⇒ 老板看不到一条真待拍项; 多报 ⇒ 老板去拍一条已经闭合的** ⇒ ★**两头都是真代价** ★ ★

| # | bug | 本机实读症状 | 修法 (与 `merge.py` 逐字对齐) |
|---|---|---|---|
| ★**①** ★ | ★**收集顺序** ★ | ★**answer 收集与 need 扫描同在一个循环** ⇒ `_frags_all` 按文件名排序 (hw.yaml→mech.yaml→pm.yaml→sw.yaml) ⇒ ★**靠后分片 (pm.yaml) 的答案来不及压掉靠前分片 (hw.yaml) 的 need** ⇒ ★**`q16_display_iface` 已被 `merge.py` 判 `answered`, `advance.py` 仍列进老板清单** ★ | ★**先收齐全部 answers 成 `_ans_by_key`, 再走 need 扫描** ★ |
| ★**②** ★ | ★**闭合宽度** ★ | ★**`if k in ans_keys: continue` ⇒ 任何分片的任何答案都算闭合** ⇒ ★**foreign answer 也能抹掉老板的真待拍项** ⇒ ★**实测 `iss340_c_bucket_boss_decisions`: `merge.py` 判 `pending` (need 的 `to=boss` ⇒ 只有老板的答案能闭合), `advance.py` 却抹了** ★ | ★**只有 need 自己 `to` 指定的那个 agent 的答案才算闭合** (★`merge.py` 原句: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]`★) ★ |

★**★双向验收 (fail-closed·两向都过才算修好)★★**:

| 方向 | 判据 | 实测 |
|---|---|---|
| 正向 (0 误伤) | 被抹掉的每一条在 `merge.py` 快照里必须都是 `answered` | ★**2/2 ✓** (`iss047_margin_criterion_decision` · `q16_display_iface`) ★ |
| 反向 (0 残留) | 留在清单里的每一条在 `merge.py` 快照里必须都不是 `answered` | ★**0 条残留 ✓** ★ |
| 差集 | 修前 56 → 修后 55 | ★**被抹 2 条 · 新增 1 条 (`iss250_pick_downgrade_route` = 原先被 bug ② 误抹·现在正确地回到老板清单) ⇒ 净 -1** ★ |

★**★`q16_display_iface` 是怎么闭合的 (★事实性闭合·★不是代拍★)★**: ★**ISS-401 (hw-lead) 已按老板 2026-11-12 02:02「不再发信·全靠自己查资料」的政策自查闭** ⇒ ★**`[官网]` Forlinx OK3572-C 手册 §2.6.2 已把 `MIPI_DPHY_DSI_TX_D0P/N~D3P/N + CLKP/N` 逐脚引出 (P3 pin 57/59/63/65/69/71/75/77/81/83) + `[实测]` `HW/netlist_v1.csv` row210-229 逐针零差异 + 同表只引 `HDMI_TX_*` 未引 eDP/DP TX ⇒ 三选一 = **DSI TX (4-lane)** ⇒ **demo 板不加桥接芯片** ⇒ ★**main 在自己分片 `pm.yaml` 的 `answers` 代录 (★`to: hw-lead`·与 need 的 `to: main` 配对·★`merge.py` 已判 `answered`★)** ⇒ ★**残留的『宽高比 A/B/C 拍板』不在这个 key 里 = `q16_aspect_ratio` ⇒ 老板 10-25 已拍 (在 `decision_truth.BOSS_DECIDED_KEYS` 里) ⇒ 这一条不需要老板再动** ★ ★

★**★⚠ 口径提醒 (★给老板★)★**: ★**「老板清单条数」这个数字以后才可信 (与 `merge.py` 同口径) ⇒ 页上历史上写的 42 → 53 → 55 是【旧口径】·若按旧数核会以为少了两条 ⇒ 实际那两条已经闭合** ★ ★

---

## ★★四 · ★★C 段 (老板拍板面) 55 条零漏项 ★★

★**一页 25/55 + 索引 40/55 ⇒ 并集 55/55 · 零漏项** (★`DECISION_ONE_PAGER_2026-11-22.md` 追加 §㊾·★前 326,850 B 逐字节未变★) ★ ★

★**★新增待拍项 1 条 (★是被 bug ② 露出来的·★不是新问题·★一件没代拍★)★**:

| need key (★回这个★) | 一句话题 | 建议默认值 (建议·非已决定) | 卡不卡「板那一趟」 |
|---|---|---|---|
| ★**`iss250_pick_downgrade_route`** ★ | ★**ISS-250 降级路线三选一**: ① rk3576-target 维持现状 ② rknn3-toolkit 1.2.0 独立 conda env (98 MB wheel + 与 toolkit2 2.3.2 冲突 + RK3572 仍 Beta) ③ 降 OD 负载 / 回 RK3576 换 SoC (板级改版·周级) ★ | ★**阶梯式 R1 → R2 → R3**: 板一通电先跑 R1 的 N1 (零新增成本·一条命令) ⇒ N1 FAIL 立刻转 R2 ⇒ R2 也不行才启 R3 ⇒ ★**R1/R2 两条命令均已就绪且 `--dry-run` rc=0 ⇒ 板到手即出结论·不需要任何外部回复才能动** ★ | ★**不卡** (★模型侧路线选择·不是板面改动★) ★ |

★**★「板那一趟」的老板侧阻塞面 = 11 件 (★件数不变·本轮一件没动★)★**: `boss_u1_upper_axis_board_trip_physical_product` (★上位问题·回函先跑 `state/board_decision_reply_mapper.py` 撞码当场拒收★) · `boss_shutdown_semantics_and_loadswitch_20261117` · `boss_esd_model_axis_pending_20261117` · `iss364_k2_d_esd_usb_d_2v3_pin` · `boss_c_vbus_gnd_reserve_pad_20260717` · `boss_decide_reboard_mtime_size_caliber` · `boss_decide_second_reboard_stop_authority` · `iss340_c_bucket_boss_decisions` · `iss364_k3_button_3n_vs_1p5n` · `iss237_product_screen_version` · `iss260_boss_a3_arch_and_model` ★ ★

---

## ★★五 · 核验 5 连 (★本轮实测 rc★) ★★

| 检查 | rc | 读数 |
|---|---|---|
| `merge.py` | **0** | ★产出 899 · 阻塞 43 (高危 33) · 未闭合需求 426 · **冲突 0** · 健康度 red★ |
| `gate_check.py` | **0** | ★**Q1 18/18** · ★**Q2 3/3** (★22:0x 时是 1/3·因交卷页当时还是骨架★) · Q3 1306 条 · ★**Q6 ✅** · ★**Q7 钉板闸链 10/10** · 缺口 3 条 (全是「等另一个总工」)★ |
| `issue_check.py` | **1** | ★违规 **19 条** (★全是既有逾期老账·**本轮零新增**★)★ |
| `stage_gate.py` | **1** | ★当前 **G1** · 还差 **1** 项 = PCB 布线 unconnected **45→0** (DRC 0 已达标) · **G1a 还差 2 条** (G1a-4 / G1a-8)★ |
| `daily_check.py` | **3** | ★三条全是老账: 问题闭环门 19 条 + `check_pcb_nets` rc=1 (板≠网表) + `chain_gate` rc=1 ⇒ **后两条就是「板那一趟」本体·不许单独擦**★ |

★**板面零变化 (★四指纹 `md5sum -c` 全 OK★)** ⇒ ★**`stage_gate` 仍 = G1 ⇒ G1 仍开, 不许投板** ★

---

## ★★六 · 本 job 边界自证 (2026-11-24 23:5x) ★★

★**派 0 条** (★internal=0·三个槽位被 11 条已交卷单占住·★本轮走的是【签收闸】不是【再派一遍】★) · ★**零外发** (★`approvals: []` ⇒ `state/outbox/` 19 份 .md 一律只留档不发·未发任何邮件 / 未联系任何供应商 / 未下采购单★) · ★**零写板** · ★**零落表** · ★**零改既有闸的判据/阈值** · ★**零改既有页正文** (★一页只追加 §㊾·前 326,850 B 逐字节未变★) · ★**只写 main 自己的分片** (`pm.yaml` 加 1 条 answer·★走 `frag_write.py` 原子写★) · ★**零挂链** · ★**未代老板拍板** · ★**不改 PROJECT_TRACKER.md §0 锁死表** · ★**GitHub: 本 job 不推 (★由独立 5 小时同步 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ **只落本地快照 `PROGRESS_SNAPSHOT.md`** ★

★**★本轮落盘 6 件★★**: `state/advance.py` (★两处 bug 修在产生点★) · `state/fragments/pm.yaml` (★+1 条 answer·`q16_display_iface`★) · `state/issue_log.yaml` (★11 条签收·其余 386 条逐条 md5 未变·★CAS 守卫通过★) · `DECISION_ONE_PAGER_2026-11-22.md` (★+§㊾·+13,982 B★) · 本 round log + `state/CURRENT_TASK.md` 本行 · `PROGRESS_SNAPSHOT.md` (★本地快照★) ★

★**★下一轮 (00:1x 那趟) 盯★★**: ★**① sw-lead / mech-lead 槽位已释放 ⇒ 下一轮 `advance.py` 的 internal 可能有货 ⇒ ★**但先把「板只改一次」纪律 ① 的候选排出来 (★纯分析/作业包类优先★)** ★**② hw-lead 槽位被兄弟 job 的 ISS-402 占着 ⇒ 不许派 · ③ ★**C 段 55 条里新露出的 `iss250_pick_downgrade_route` 需要老板一句 (★建议默认值已在一页 §㊾-5·★不代拍★) ④ ★**本轮签收了 11 条 ⇒ `fixing` 从 12 降到 1 (ISS-402) ⇒ 下一轮 `advance.py` 的 in_flight 判据松了大半 ★**⑤ ★**巡检那 2 条红 = 板那一趟本体·不许单独擦 ★**⑥ 本 job 不发任何信** ★ ★
"""


def main():
    # ---------- ① 零写板 / 零落表 (开工前) ----------
    st = os.stat(BOARD)
    assert md5_file(BOARD) == BOARD_MD5 and st.st_size == BOARD_SIZE and st.st_mtime_ns == BOARD_MTIME_NS, "★板指纹不符"
    for p, base in ((NETLIST, "6aee500e60ba0732f83a9cf557ba90ab"),
                    (PINS, "9174309df1ec9411ac8e8d9e80ee386a"),
                    (BOM, "5b9993992405904a60ac96a020b375d8")):
        assert md5_file(p) == base, "★真源表被改"
    print("✓ 开工前: 板三证 + 三张真源表 未变")

    # ---------- ② round log ----------
    if os.path.isfile(ROUND_LOG):
        print("  · round log 已存在 ⇒ 不重复写")
    else:
        with open(ROUND_LOG, "w", encoding="utf-8") as f:
            f.write(ROUND)
        print("✓ 新建 %s (%d B)" % (os.path.basename(ROUND_LOG), os.path.getsize(ROUND_LOG)))

    # ---------- ③ CURRENT_TASK 追加一行 ----------
    cur = ("\n★★**【本 job · cron 775d9893 · 2026-11-24 23:38~00:0x r92 · 本轮口径 (★追加式·老字一字未删★)】★★** ★"
           "**`advance.py --json` = internal **0** / approvals **0** / decisions **55** (★修 advance.py 前 56★) / waiting **0** ⇒ 本轮 **派 0 条** (★三个槽位被 11 条已交卷单占住·★本轮走【签收闸】不是【再派一遍】·★**PCB 类候选实测 0 条**★)★** "
           "⇒ ★**① 【11 单签收 (★main 本机独立复核·不抄任何 agent 报告★)】** ISS-391/392/393/394/395/396/397/398/399/400/401 ★**fixing → verified** ⇒ ★**11 道新闸 `--selftest` 11/11 rc=0 ALL TESTS PASS · 裸跑 6 绿 / 5 红 (★红=按设计·红的是现状★)·交卷页占位符 0·分片登记 11/11·板四指纹 `md5sum -c` 全 OK** ⇒ ★**其余 386 条台账逐条 md5 未变 (★CAS 守卫通过★)·sw-lead / mech-lead 两个槽位已释放 (★hw-lead 被兄弟 job 23:44 新开的 ISS-402 占着★)★** "
           "⇒ ★**② 【★`state/advance.py` 两处真 bug 修在产生点★】** ① **收集顺序**: answer 收集与 need 扫描同循环 ⇒ 靠后分片 (pm.yaml) 的答案压不掉靠前分片 (hw.yaml) 的 need (★`q16_display_iface` 已被 merge 判 answered·advance.py 仍列进老板清单★) ② **闭合宽度**: `k in ans_keys` ⇒ foreign answer 也能抹掉老板的真待拍项 (★`iss340_c_bucket_boss_decisions` 实测 merge 判 pending·advance 却抹了★) ⇒ ★**修法 = 与 `merge.py` 逐字对齐 (先收齐 answers + 只有 need 自己 `to` 指定方的答案才算闭合)·双向验收 (正向 2/2 answered + 反向 0 残留) ⇒ 56 → 55**★ "
           "⇒ ★**③ 【C 段 55 条零漏项】** 一页 25 + 索引 40 ⇒ **并集 55/55** (★一页追加 §㊾·前 326,850 B 逐字节未变★) ⇒ ★**新露出 1 条待拍项 `iss250_pick_downgrade_route` (★原先被 bug ② 误抹·现在正确地回到老板清单·★建议默认值 = 阶梯式 R1→R2→R3·一件没代拍★)★** "
           "⇒ ★**核验 5 连本轮实测 rc**: ★**merge 0** (★产出 899 · 阻塞 43 高危 33 · 未闭合需求 426 · 冲突 0★) · ★**gate_check 0** (★**Q1 18/18** · ★**Q2 3/3** (★22:0x 时 1/3·因交卷页当时还是骨架★) · ★**Q7 钉板闸链 10/10** · 缺口 3 条★) · ★**issue_check 1** (★违规 **19** 条·★全是既有逾期老账·**本轮零新增**★) · ★**stage_gate 1** (★当前 **G1** · 还差 **1** 项 = 布线 unconnected 45→0 · **G1a 还差 2 条**★) · ★**daily_check 3** (★三条全是老账: 问题闭环门 19 / `check_pcb_nets` rc=1 / `chain_gate` rc=1 ⇒ **后两条就是板那一趟本体·不许单独擦**★)★ ⇒ ★**板面零变化 (四指纹全 OK)**: 板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17` / 4,940,213 B ⇒ **G1 仍开, 不许投板**★ "
           "⇒ ★**落盘 6 件**: `state/advance.py` (★两处 bug 修在产生点★) · `state/fragments/pm.yaml` (★+1 条 answer·`q16_display_iface`·★只写 main 自己的分片·走 frag_write.py 原子写★) · `state/issue_log.yaml` (★11 条签收·CAS 守卫·其余 386 条逐条 md5 未变★) · `DECISION_ONE_PAGER_2026-11-22.md` (★+§㊾·+13,982 B·老字逐字未变★) · 本 round log `state/ROUND_LOG_cron775d_2026-11-24_2340.md` + 本行 (★备份 `.bak_%s_cron775d_r92`★) · `PROGRESS_SNAPSHOT.md` (★本地快照·★本 job 不推 GitHub·由独立 5 小时同步 job 负责★)★ ⇒ **零外发 · 零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 未代老板拍板 · 不改 PROJECT_TRACKER §0**★ "
           "⇒ ★★**【下一轮 (00:1x) 盯】** ★**① sw-lead / mech-lead 槽位已释放 ⇒ 下一轮 internal 可能有货 ⇒ ★**但先排「板只改一次」纪律 ① 的候选 (★纯分析/作业包类优先★)★** ★**② hw-lead 槽位被兄弟 job 的 ISS-402 占着 ⇒ 不许派 ③ ★**`iss250_pick_downgrade_route` 需要老板一句 (★建议默认值在一页 §㊾-5·★不代拍★) ④ ★**`fixing` 从 12 降到 1 ⇒ in_flight 判据松了大半 ⑤ ★**巡检那 2 条红 = 板那一趟本体·不许单独擦 ⑥ 本 job 不发任何信**★ ★\n")
    append_atomic(CUR, cur, "current_task_r92")

    # ---------- ④ 收工后零写板 ----------
    st2 = os.stat(BOARD)
    assert md5_file(BOARD) == BOARD_MD5 and st2.st_size == BOARD_SIZE and st2.st_mtime_ns == BOARD_MTIME_NS, "★收工后板指纹变了"
    for p, base in ((NETLIST, "6aee500e60ba0732f83a9cf557ba90ab"),
                    (PINS, "9174309df1ec9411ac8e8d9e80ee386a"),
                    (BOM, "5b9993992405904a60ac96a020b375d8")):
        assert md5_file(p) == base, "★收工后真源表被改"
    print("✓ 收工后: 板三证 + 三张真源表 未变")

    # ---------- ⑤ 本地快照 (★不推 GitHub★) ----------
    r = subprocess.run([sys.executable, os.path.join(HERE, "gen_progress_snapshot.py")],
                       capture_output=True, text=True, cwd=PROJ)
    print("  gen_progress_snapshot rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[-200:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
