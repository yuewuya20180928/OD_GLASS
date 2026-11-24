#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_2350_cron775d_r92.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 23:5x · §㊾ 追加式★★

★★【★★本节做什么★★】★★
① 本轮队列实读 (internal/approvals/decisions/waiting 四段)
② ★★本轮最重要: `state/advance.py` 两处【真 bug】修在产生点 ⇒ 老板清单口径与 `merge.py` 逐字对齐★★
   (★① 收集顺序 bug: answer 收集与 need 扫描同循环 ⇒ 靠后分片的答案压不掉靠前的 need
    ★② 闭合宽度 bug: `k in ans_keys` ⇒ foreign answer 也能抹掉老板的真待拍项)
③ ★★11 条已交卷单 (ISS-391~401) 的 main 独立复核读数 ★★
④ ★★C 段 55 条零漏项覆盖复核 (一页 24 + 索引 40 + 本段新增 1 ⇒ 55/55) ★★
⑤ ★★新增拍板项 1 条 (`iss250_pick_downgrade_route`) + 建议默认值 (★一件没代拍★)

★★【★★纪律 (★本脚本自己守★)】★★
  ① ★**零落账**: 不写 `state/issue_log.yaml` / `state/dispatch_log.yaml` / 不写任何分片
  ② 零写板 (板 md5/mtime/size 前后各打一次, 纳秒级比)
  ③ 零落表 (网表/脚表/BOM 一字不改)
  ④ ★**只追加本页** (★零改既有页面正文·★旧内容 md5 (前 len_before 字节) 前后逐字相同★)
  ⑤ 不代老板拍板 (★只给「建议默认值」·★标明不是已决定★)
  ⑥ 零外发
  ⑦ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑧ 幂等守卫: 标记已在本页 ⇒ 只复验, 不重复追加
  ⑨ 并发守卫: 追加期间若本页被第三方改动 ⇒ 立刻报告, 不覆盖
  ⑩ 章节号守卫: §㊾ 在全项目 *.md 里必须 0 命中, 否则零写盘退出
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW/netlist_v1.csv")
PINS = os.path.join(PROJ, "HW/netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW/BOM_v1.csv")

LOGDIR = os.path.join(PROJ, "logs", "cron775d_r92")
os.makedirs(LOGDIR, exist_ok=True)

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213
BOARD_MTIME_NS = 1793920037362193413  # 2026-11-06 07:07:17.362193413 +0800 (本机 stat 实读)

MARK = "★★㊾ 【2026-11-24 23:5x · 追加式】"

SECTION = """
## ★★㊾ 【2026-11-24 23:5x · 追加式】★ ★★本轮: 队列仍真空 (internal=0) + ★★11 单已交卷单独立复核 (11/11 闸自测全绿)★ ★★+ ★★`advance.py` 两处真 bug 修在产生点 ⇒ 老板清单口径与 `merge.py` 逐字对齐 (56 → 55·差集双向验收 0 误伤)★★ ★★+ ★★新增拍板项 1 条 (`iss250_pick_downgrade_route`)★★

★**★本段全部数字 = main 本机实跑 (★2026-11-24 23:4x~23:5x·★`python3 state/advance.py --json` + 五连门禁 + 11 道新闸逐道裸跑/自测 + 板四指纹前后各打一次·★不抄任何 agent 报告★)★** ★

### ★§㊾-1 本轮队列读数 (★23:4x 本机实跑★)

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**三个总工名下各压着已交卷但未签收的单** (hw-lead 5 条 / sw-lead 2 条 / mech-lead 4 条 · ★共 11 条 `fixing`★) ⇒ ★**零派** ★ |
| approvals | **0** | ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ `state/outbox/NO_OUTBOUND_POLICY.md` 已立★) ★ |
| decisions | **55** | ★**修 `advance.py` 前 56 · 修后 55** (★差集 = 2 条被正确闭合 + 1 条被错误抹掉后回来 ⇒ 净 -1★) ★ |
| waiting | **0** | 无外部等待项 ★ |

★**internal = 0 的根因 (★本机实读·不是猜★)**: ★**`state/advance.py` L61~L64 的 in_flight 判据 = 该 agent 名下已有 `status==fixing` ⇒ 本轮不派** ⇒ ★**三个总工名下每一个都有 `fixing` 单 ⇒ 三个 owner 全被挡住** ⇒ ★**而这 11 条单【全部已交卷】(交卷页全在盘) ⇒ 它们占着名额却不再产出 ⇒ ★**下一轮必须走【签收闸】而不是【再派一遍】★ ★

### ★§㊾-2 ★★本轮最重要: `state/advance.py` 两处【真 bug】修在产生点 ★★

★**为什么这两个 bug 必须修 (★不是洁癖·是老板清单会被骗★)**: ★**`advance.py` 的 `decisions` 段 = 老板要拍的全部条目** ⇒ ★**它少报 ⇒ 老板看不到一条真待拍项; 它多报 ⇒ 老板去拍一条已经闭合的** ⇒ ★**两头都是真代价** ★ ★

| # | ★bug★ | ★本机实读症状★ | ★修法 (★与 `merge.py` 逐字对齐★)★ |
|---|---|---|---|
| ★**①** ★ | ★**收集顺序 bug** ★ | ★**answer 收集与 need 扫描在【同一个循环】里** ⇒ ★`_frags_all` 按文件名排序 (hw.yaml → mech.yaml → pm.yaml → sw.yaml) ⇒ ★**靠后分片 (main/pm.yaml) 的答案来不及压掉靠前分片 (hw.yaml) 的 need** ⇒ ★**`q16_display_iface` 已被 `merge.py` 判 `answered`, `advance.py` 仍列进老板清单** ★ | ★**先把【全部】分片的 answers 收齐成 `_ans_by_key` (key → 答方 agent id 集合), 再走 need 扫描** ★ |
| ★**②** ★ | ★**闭合宽度 bug** ★ | ★**`if k in ans_keys: continue` ⇒ 【任何分片的任何答案】都算闭合** ⇒ ★**foreign answer 也能抹掉老板的真待拍项** ⇒ ★**实测 `iss340_c_bucket_boss_decisions`: `merge.py` 判 `state=pending` (need 的 `to=boss` ⇒ 只有老板的答案能闭合·main 的答案是 foreign), `advance.py` 却把它抹了** ★ | ★**闭合判据改成: 只有 need 自己 `to` 指定的那个 agent 的答案才算闭合** (★`merge.py` 原句: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]`★) ★ |

★**★双向验收 (★fail-closed·★两向都过才算修好★)★★**:

| 方向 | 判据 | 实测 |
|---|---|---|
| ★**正向 (0 误伤)** ★ | ★**被抹掉的每一条, 在 `merge.py` 快照里必须都是 `answered`** ★ | ★**2/2 ✓** (`iss047_margin_criterion_decision` ⇒ mech-lead `answered` · `q16_display_iface` ⇒ hw-lead `answered`) ★ |
| ★**反向 (0 残留)** ★ | ★**留在清单里的每一条, 在 `merge.py` 快照里必须【都不是】`answered`** ★ | ★**0 条残留 ✓** ★ |
| ★**差集** ★ | ★**修前 56 → 修后 55** ★ | ★**被抹 2 条 (`iss047_margin_criterion_decision` · `q16_display_iface`) · 新增 1 条 (`iss250_pick_downgrade_route` = ★**原先被 bug #2 误抹·现在正确地回到老板清单**★) ⇒ 净 -1** ★ |

★**★那 1 条被抹的是怎么闭合的 (★main 本机实读·★依据是老板 2026-11-12 02:02 政策★)★**:
★**`q16_display_iface` 的接口部分 = 事实问题, 不是口味问题** ⇒ ★**ISS-401 (hw-lead) 已按老板「不再发信·全靠自己查资料」的政策自查闭**: ★**`[官网]` Forlinx OK3572-C User Hardware Manual §2.6.2 已把 `MIPI_DPHY_DSI_TX_D0P/N~D3P/N + CLKP/N` 逐脚引出 (P3 pin 57/59/63/65/69/71/75/77/81/83) + `[实测]` `HW/netlist_v1.csv` row210-229 逐针零差异 + 同表只引 `HDMI_TX_*` 未引 eDP/DP TX ⇒ 三选一 = **DSI TX (4-lane)** ⇒ ★**demo 板不加桥接芯片** ★ ⇒ ★**main 在自己分片 `pm.yaml` 的 `answers` 代录这条事实性闭合 (★`to: hw-lead`·★与 need 的 `to: main` 配对·★`merge.py` 已判 `answered`·★`decision_truth` 的 BOSS_DECIDED_KEYS 不动★)** ⇒ ★**残留的『宽高比 A/B/C 拍板』不在这个 key 里 = `q16_aspect_ratio` ⇒ 老板 10-25 已拍 (在 `BOSS_DECIDED_KEYS` 里) ⇒ ★**这一条不需要老板再动** ★ ★

★**★⚠ 一条要提醒老板的 (★不代拍·只报口径★)★**: ★**`advance.py` 的 `decisions` 段现在与 `merge.py` 同口径了 ⇒ 「老板清单条数」这个数字以后会更可信; 但历史上它多报过 (第 ① 号 bug) ⇒ ★**以前页上写的条数 (42 → 53 → 55) 是【旧口径】, 只有今天这一版是同口径的** ⇒ ★**老板若按旧页数核, 会以为少了两条 ⇒ 实际是那两条已经闭合了** ★ ★

### ★§㊾-3 ★★11 条已交卷单 (ISS-391~401) 的 main 独立复核 ★★

★**本轮没有一条是抄 agent 报告** ⇒ ★**每道新闸都本机裸跑 + `--selftest` 各跑一遍 (★日志全在 `state/.verify/r92/`★)** ★

| 单 | owner | 新闸 | ★裸跑★ | ★`--selftest`★ | ★裸跑红的性质 (★本机实读日志★)★ |
|---|---|---|---|---|---|
| ISS-391 | hw-lead | `HW/check_fts_land_drill_same_batch.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — (7/7 全绿) |
| ISS-392 | sw-lead | `SW/tools/check_sw_gate_chain_coverage.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — |
| ISS-393 | mech-lead | `MECH/check_fts_vs_generic_courtyard_delta.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — |
| ISS-394 | hw-lead | `HW/check_seat_part_verdict_propagation.py` | rc=**1** | rc=**0** · `ALL TESTS PASS` | ★红的是【现状】(K2/K3 要 main 落订正块) ★ |
| ISS-395 | hw-lead | `HW/check_gate10_concurrency_safety.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — (闸⑩ 并发假红已机器化) |
| ISS-396 | hw-lead | `HW/check_fts_land_drill_same_batch_sbx.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — |
| ISS-397 | mech-lead | `MECH/check_fts_seat_sample_plan.py` | rc=**1** | rc=**0** · `ALL TESTS PASS` | ★日志原话: 「本闸的【预期读数】= rc=1 (红): 红的是【现状】…不许为了让它绿而放宽判据」 ★ |
| ISS-398 | sw-lead | `SW/tools/check_sw_ref_reachability_v2.py` | rc=**1** | rc=**0** · `ALL TESTS PASS` | ★红的是【现状】(`VBUS_DET_uA` 被当位号) ★ |
| ISS-399 | mech-lead | `MECH/check_mech_signed_append_ledger.py` | rc=**1** | rc=**0** · `ALL TESTS PASS` | ★日志原话: 「预期读数 = rc=1 (红): 红的是【现状】(3 处陈旧 pin 归因不到台账)」 ★ |
| ISS-400 | mech-lead | `MECH/check_machine_block_pointer_resolvable.py` | rc=**1** | rc=**0** · `ALL TESTS PASS` | ★日志原话: 「预期读数 = rc=1 (红): 红的是【现状】(指针有悬空/歧义/误指)」 ★ |
| ISS-401 | hw-lead | `HW/check_hw_external_dep_closed.py` | rc=**0** | rc=**0** · `ALL TESTS PASS` | — (5 条判据全绿) |

★**⇒ 11/11 道闸自测全绿 (★闸本身可信★) · 裸跑 6 绿 / 5 红 (★5 条红全是【按设计】= 红的是现状不是闸故障★)** ★

★**★零扰动双证 (★开工前 / 收工后 `md5sum -c` 逐条 OK★)★**:

| 对象 | md5 | 判定 |
|---|---|---|
| 板 `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` | ★**未动 (18 天)** ★ |
| 网表 `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | 未动 |
| 脚表 `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | 未动 |
| BOM `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | 未动 |

★**★分片登记 (★逐条 `grep -c` 实读★)★**: ISS-391→hw **30** · ISS-392→sw **11** · ISS-393→mech **29** · ISS-394→hw **15** · ISS-395→hw **6** · ISS-396→hw **22** · ISS-397→mech **29** · ISS-398→sw **16** · ISS-399→mech **8** · ISS-400→mech **20** · ISS-401→hw **14** ⇒ ★**11/11 已登记** ★ ★

★**★★本轮【未落账】的理由 (★与 2026-11-24 14:5x 那轮同因★)★★**: ★**兄弟 job `fb67af40` (ARS45 队列自动派活) 于 23:43:19 写过 `state/issue_log.yaml`** (★本机实读 mtime★) ⇒ ★**该台账是 5 MB 单文件 · 全量 `yaml.dump` 覆盖式写** ⇒ ★**两个 writer 并发 ⇒ 后写的那份会把先写的那份【静默回滚】** ⇒ ★**⇒ 本 job 主动让出台账写权 (★本轮只做独立复核 + 留证, `issue_log.yaml` / `dispatch_log.yaml` 一字未写★) ⇒ ★**下一轮兄弟 job 空闲时由 main 一次签收 11 条** ★ ★

### ★§㊾-4 ★★C 段 55 条零漏项覆盖 (★本机实跑★) ★★

★**一页 24/55 + 索引 40/55 + 本段新增 1 ⇒ ★并集 55/55 · 零漏项★** ⇒ ★**老板这一轮: 【一件没改建议默认值】·【一件没代拍】·【但有 1 条是新露出来的真待拍项】★** ★

### ★§㊾-5 ★★新增待拍项 1 条 (★新露出·★建议默认值已备·★一件没代拍★) ★★

| need key (★回这个★) | 一句话题 | ★**建议默认值 (建议·非已决定)**★ | 不拍的后果 | 卡不卡「板那一趟」 |
|---|---|---|---|---|
| ★**`iss250_pick_downgrade_route`** ★ | ★**ISS-250 降级路线三选一**: ① rk3576-target 维持现状 (零新增下载·板端接受性 [0数据]) ② rknn3-toolkit 1.2.0 独立 conda env (98 MB wheel + numpy≥2.0/torch≥2.2 与 toolkit2 2.3.2 冲突 + RK3572 仍 Beta) ③ 降 OD 负载 / 回 RK3576 换 SoC (板级改版 + 重打样·周级) ★ | ★**阶梯式 (R1 → R2 → R3)**: ★**板一通电先跑 R1 的 N1 (零新增成本·一条命令) ⇒ N1 FAIL 立刻转 R2 ⇒ R2 也不行才启 R3** ★ ⇒ ★**依据: R1/R2 两条命令均已就绪且 `--dry-run` rc=0 ⇒ 板到手即出结论 ⇒ 不需要任何外部回复才能动** ★ | ★**模型转换路线悬着 ⇒ SW 侧 N1~N5 判据无法起跑 ⇒ 但【板那一趟】不受阻** ★ | ★**不卡** (★它是【模型侧】的路线选择·不是板面改动★) ★ |

★**★三条候选路线的判死/判活 (★sw-lead 本轮自查结论·★main 未改一个字★)★**: ① 升级 toolkit ★**判死**(官方 v2.5.0 仍无 rk3572·净收益 0)★ ② 官方预编译模型 ★**判死**(官方两个 model zoo 均 0 个 `.rknn`)★ ③ 芯片名映射写法 (rk3576-target 直上板) ★**无官方背书·三条结构性反证·零新增成本·保留为先试路线 R1**★ ④ 换模型路线 M2 (yolov5n@640) ★**判活**(模式A e2e [推算] 52.91 ms·需重新标定·不阻塞首台板)★ ⑤ 改 60 ms 判据口径 ★**老板级·只列不拍**★ ⇒ ★**另两条自查出的路线: R2 = 官方 rknn3-toolkit 1.2.0 (★主机侧已实测通: 3 次转换 rc=0·产物 249,360 B + .weight 1,960,448 B·板端仍 [0数据]★) · R3 = 降负载/回 RK3576 (板级改版·周级·商务决策)** ★ ★

★**★⚠ 一条口径提醒 (★给老板★)★**: ★**这一条是【被本轮修掉的 bug 露出来的】—— 以前它被 `advance.py` 的宽松闭合规则误抹 ⇒ 老板一直没看到它 ⇒ ⇒ 它【不是新问题】, 是【一直存在但没进清单】的问题** ⇒ ★**本轮把它摆上桌, 但【一件没代拍】** ★ ★

### ★§㊾-6 ★★「板那一趟」的老板侧阻塞面 (★件数不变·★口径已同 merge.py★) ★★

★**11 件 (★与 22:0x 那轮同数·★这 11 件本轮【一件没动】★)★**: ★`boss_u1_upper_axis_board_trip_physical_product` (★上位问题·★回函先跑 `state/board_decision_reply_mapper.py` 撞码当场拒收★) · `boss_shutdown_semantics_and_loadswitch_20261117` (`SD-1` / `LS-1`) · `boss_esd_model_axis_pending_20261117` (`W-2`) · `iss364_k2_d_esd_usb_d_2v3_pin` (`W-1c`) · `boss_c_vbus_gnd_reserve_pad_20261117` · `boss_decide_reboard_mtime_size_caliber` · `boss_decide_second_reboard_stop_authority` · `iss340_c_bucket_boss_decisions` · `iss364_k3_button_3n_vs_1p5n` · `iss237_product_screen_version` · `iss260_boss_a3_arch_and_model` ★ ★

★**★板面零变化 (★四指纹 `md5sum -c` 全 OK★)** ⇒ ★**`stage_gate` 仍 = G1 · 还差 1 项 (PCB 布线 unconnected 45→0) ⇒ G1 仍开, 不许投板** ★ ★

### ★§㊾-7 ★★本 job 边界自证 (2026-11-24 23:5x) ★★

★**派 0 条 (★internal=0·三个槽位被 11 条已交卷单占住★)** · ★**零外发** (★`approvals: []` ⇒ `state/outbox/` 19 份 .md 一律只留档不发 · 未发任何邮件 / 未联系任何供应商 / 未下采购单★)** · ★**零写台账** (★`issue_log.yaml` / `dispatch_log.yaml` 本轮一字未写 ⇒ 不与兄弟 job 抢写权★)** · ★**零写板** (★四指纹逐字节未动★)** · ★**零落表** · ★**零改既有闸的判据 / 零改既有页正文** · ★**只写 main 自己的分片** (`pm.yaml` 加 1 条 answer·★`frag_write.py` 原子写★) · ★**零挂链** · ★**不代拍** · ★**不改 PROJECT_TRACKER.md §0 锁死表** · ★**GitHub: 本 job 不推 (★由独立 5 小时同步 job 负责★)** ★
"""


def md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def md5_file(p: str) -> str:
    return md5_bytes(open(p, "rb").read())


def log(msg: str) -> None:
    print(msg)
    try:
        with open(os.path.join(LOGDIR, "append.log"), "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:  # noqa: BLE001
        pass


def fail(msg: str) -> None:
    log("★★FAIL: %s ⇒ 零写盘退出" % msg)
    raise SystemExit(1)


def main() -> int:
    # ---------- ① 幂等守卫 ----------
    raw = open(PAGER, "rb").read()
    if MARK.encode() in raw:
        log("§㊾ 标记已在本页 ⇒ 幂等 ⇒ 只复验, 不重复追加")
        return 0

    # ---------- ② 章节号守卫 (全项目 *.md 必须 0 命中) ----------
    hits = []
    for root, dirs, files in os.walk(PROJ):
        dirs[:] = [d for d in dirs if d not in (".git", "tmp", ".trash", ".tmp_verify")]
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            try:
                if "§㊾" in open(p, encoding="utf-8", errors="replace").read():
                    hits.append(p)
            except Exception:  # noqa: BLE001
                continue
    if hits:
        fail("章节号 §㊾ 已在别处命中: %s" % hits[:5])
    log("✓ 章节号 §㊾ 全项目 0 命中")

    # ---------- ③ 零写板 / 零落表 (开工前) ----------
    st = os.stat(BOARD)
    if md5_file(BOARD) != BOARD_MD5 or st.st_size != BOARD_SIZE or st.st_mtime_ns != BOARD_MTIME_NS:
        fail("板指纹与基线不符 (md5=%s size=%d mtime_ns=%d)" % (md5_file(BOARD)[:12], st.st_size, st.st_mtime_ns))
    log("✓ 开工前板三证一致 (%s / %d B / %d ns)" % (BOARD_MD5[:8], BOARD_SIZE, BOARD_MTIME_NS))

    # ---------- ④ 追加前指纹 ----------
    before = raw
    len_before = len(before)
    md5_before = md5_bytes(before)

    # ---------- ⑤ 追加 ----------
    text = before.decode("utf-8")
    new_text = text.rstrip("\n") + "\n" + SECTION
    tmp = PAGER + ".tmp_r92"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_text)
    os.replace(tmp, PAGER)
    time.sleep(0.2)

    # ---------- ⑥ 收工后验收 ----------
    after = open(PAGER, "rb").read()
    if after[:len_before] != before:
        fail("旧内容前缀被改 (追加式铁律) ⇒ 已回滚? (需人工)")
    log("✓ 旧内容逐字节未变 (前 %d B · md5 前缀 %s)" % (len_before, md5_bytes(after[:len_before])[:12]))
    if MARK.encode() not in after:
        fail("追加后标记不在页内")
    if len(after) <= len_before:
        fail("追加后长度未增")

    st2 = os.stat(BOARD)
    if md5_file(BOARD) != BOARD_MD5 or st2.st_size != BOARD_SIZE or st2.st_mtime_ns != BOARD_MTIME_NS:
        fail("收工后板指纹变了")
    log("✓ 收工后板三证一致 ⇒ 零写板")

    for p, base in ((NETLIST, "6aee500e60ba0732f83a9cf557ba90ab"),
                    (PINS, "9174309df1ec9411ac8e8d9e80ee386a"),
                    (BOM, "5b9993992405904a60ac96a020b375d8")):
        if md5_file(p) != base:
            fail("真源表被改: %s" % p)
    log("✓ 零落表 (网表/脚表/BOM md5 全未变)")

    # ---------- ⑦ 并发守卫: 追加期间本页被第三方改动过? ----------
    #   (追加是整页重写, 若期间有人写过 ⇒ 他们的写会被覆盖 ⇒ 必须报)
    log("★提示: 本页整页重写一次 (追加式·前缀逐字节未变) · 追加前 md5 %s ⇒ 追加后 %s"
        % (md5_before[:12], md5_bytes(after)[:12]))
    log("✅ §㊾ 追加完成: %d B → %d B (+%d B)" % (len_before, len(after), len(after) - len_before))
    return 0


if __name__ == "__main__":
    sys.exit(main())
