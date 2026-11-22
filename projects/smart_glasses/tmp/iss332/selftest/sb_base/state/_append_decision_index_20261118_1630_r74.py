#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 §M 到 DECISION_INDEX_2026-11-18.md (追加式: 老字逐字不改)
   ★ 本 job = cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 16:3x · r74
   ★ 纪律: 先备份 → 追加 → 校验老字逐字未变 (前缀 md5 比对)
"""
import hashlib, os, re, shutil, sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
IDX = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")
BAK = IDX + ".bak_20261118_1630_r74"
LOG = os.path.join(PROJ, "logs/cron775d_20261118_1617")


def grab(fn, pat, default="?"):
    p = os.path.join(LOG, fn)
    if not os.path.exists(p):
        return default
    txt = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(pat, txt)
    return m.group(0).strip() if m else default


merge_sum = grab("01_merge.log", r"产出 \d+.*")
q1 = grab("02_gate_check.log", r"【Q1[^】]*】[^\n]*")
q2 = grab("02_gate_check.log", r"【Q2[^】]*】[^\n]*")
q3 = grab("02_gate_check.log", r"【Q3[^】]*】[^\n]*")
q4 = grab("02_gate_check.log", r"【Q4[^】]*】[^\n]*")
q7 = grab("02_gate_check.log", r"【Q7[^】]*】[^\n]*")
gaps = grab("02_gate_check.log", r"缺口清单[^\n]*")
issue_tail = grab("03_issue_check.log", r"[^\n]*问题闭环门[^\n]*")
stage = grab("04_stage_gate.log", r"当前[^\n]*")
stage_gaps = grab("04_stage_gate.log", r"G1a[^\n]*")
daily = grab("05_daily_check.log", r"巡检[^\n]*")

SEC = f"""

---

## §M · ★★【r74 · 2026-11-18 16:17~16:35 · 追加式】★★ · ★★**ISS-325 收尾带出 6 条 to=main 板级轴 ⇒ main 逐条裁掉 + ★★给老板的三条硬事实 (G7 这一票【不构成解锁】)★★** ★★

> ★**追加时刻**: 2026-11-18 16:3x · ★**追加人**: 项目总工 (moli) · cron `775d9893` (ARS45 继续执行后继计划)
> ★**依据**: ★**`state/fragments/hw.yaml` (★16:07 本机实读 · ISS-325 交回的 6 条 `iss325_s8_*` need · 全部 `to=main`★)** + ★**`logs/iss325/09_threeway_fresh_drc.txt` + `logs/iss325/10_compare_arm_official_lu_vs_official.txt` + `logs/iss325/10c_compare_arm_official_ctl_vs_lu.txt` (★★main 16:2x 本机逐行实读, 未抄 agent 报告★★)** + ★**`HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` §7** ★
> ★**本节追加时 §A~§L 的老字一个字未删未改** ★ · ★**性质**: ★**只加读数 + 只裁 main 的机制/口径/用法地界 · 不新增老板拍板项 · 不改任何一条建议默认值 · 不替老板拍任何一条** ★

### ★M-1 · ★拍板面复核 (★机器核, 一条未动★)★

- ★**`advance.py --json` (★16:1x 实读★)**: ★**internal = 0 · approvals = 0 · decisions = 40 · waiting = 0** ★ (★`advance.py` rc=1 = 「本轮无可派」的正常信号, 不是崩溃★)
- ★**决策页覆盖**: ★**40/40 条逐 key 在本页命中 (漏 0)** ★ ⇒ ★**本轮拍板面一条未增未减未改** ★
- ★**今日 (2026-11-18) 到期仍 3 条**: ★**`iss324_d_led_g_placement_decision`** (建议默认 = 假设 B「无光孔 · 位置不动 · 零板面动作」) · ★**`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice`** (SoM 载板形态) · ★**`boss_dled_g_expose_decision_20261117`** (D_LED_G 是否外露) ★
- ★**逾期 28 条 / 无 due 9 条 / 剩 0 天 3 条** (★28+3+9 = 40 全覆盖★)

### ★M-2 · ★★★【本轮新增台面】ISS-325 交回的 6 条 `to=main` 板级轴 ⇒ main 逐条裁掉 (★6 条全部闭合, 一条没上老板拍板面★)★★★ ★★

★★**为什么这 6 条以前老板看不见**: ★**它们 `to=main` ⇒ `advance.py` 的 decisions 段读不到 ⇒ 老板在队列里一条都看不到 ⇒ 本节把它们提到台面上 + ★**逐条写清「这一条是否要老板拍」** ★★

| # | need key | ★**main 裁 (2026-11-18 16:2x)** ★ | ★**要不要老板拍** ★ |
|---|---|---|---|
| 1 | `iss325_s8_zero_reachability` | ★**接受【归零拆两问】口径** ★ ⇒ (a) 布局单独归零 = 【不能 · 已实测】(左上臂 unc=29 + 名单制闸 REJECT) (b) 机制+口径+CSI 侧一起 = 【留给 G6/G7 + ISS-308】 ★ ⇒ ★**归零的验收口径 = unc = 0 【且】 名单制闸 rc = 0 (两个都要)** ★ | ★**要 (但不是这一条要) —— 要的是 G6/G7, 这一条 main 已裁完** ★ |
| 2 | `iss325_s8_csi_side_zero_effect` | ★**采信【挪位对 CSI 5 族零作用】** ★ ⇒ 处置 = 【成对换层绕开】(不动器件·不动板框·风险最低) 列为建议默认值, ★**必须与「器件挪左上」同趟做掉** ★ ⇒ ★**main 裁的判据口径: 作业包 §4-3-⑥ 的「翻转 = 0」改成「翻转 ≤ 5 + CSI 5 族另有处置」** ★ | ★**要 (G7 + 板框 U-1) · main 不代拍** ★ |
| 3 | `iss325_s8_iss322_table_unc_stale` | ★**正式标注 ISS-322 §3-6 那张 8 块板 unc 表 = 【历史记录】, 不许当可复现先验** ★ ⇒ 一切引用改用 `logs/iss325/09b_hist_boards_fresh_drc.txt` + `09_threeway_fresh_drc.txt` ⇒ ★**「unc 与 lane 序单调相关」降级为【趋势】** ★ | ★**不要** (main 已裁) ★ |
| 4 | `iss325_s8_tp_pin_noop_proven` (★16:1x 那版 key = `iss325_s8_tp_dsi_pin_is_noop`, hw-lead 16:21 改写分片时改的名, main 按新 key 重发了一份同义裁决★) | ★**采信【显式钉那 10 个 `TP_DSI_*` 是 no-op】** ★ ⇒ 「21 器件」变量塌缩成「10 器件」 ⇒ ★**ISS-265 / LAYOUT_FIX_SPEC §1.2「只钉 R_SEL 的另一半 = 给路由器埋雷」这句话对今天的生成器【作废】** ★ | ★**不要** (main 已裁) ★ |
| 5 | `iss325_s8_gen_products_mtime` | ★**登记为【机制缺陷 · 同型复发】(ISS-280 于 11-17 08:50 已披露过一次, 至今未修)** ★ ⇒ 每天的 daily_check / chain_gate 都在改 4 个生成器产物的 mtime (内容除首行时间戳外逐字节相同) ⇒ ★**修复排期 = 板那一趟开工前, 做法 = 写盘前内容比对 (修在产生点)** ★ | ★**不要** (main 已裁 · 本轮不动共享生成器, 理由见 §M-5) ★ |
| 6 | `iss325_s8_no_valid_control` (★16:1x 那版 key = `iss325_s8_arm_pair_not_a_control`, 同上改名★) | ★**采信【两臂逐项相同 ⇒ 对照失效】** ★ ⇒ ★**G7 用法规则 (main 写死): 可用 = 三块板的逐条读数本身; 不可用 = 任何「左上布局带来了多少」的因果归因 (含「29 vs 45」)** ★ | ★**要 (G7 的用法) · 但规则本身 main 已定** ★ |

★**⇒ 落账**: ★**6 条 answer 写进 `state/fragments/pm.yaml` (★main 自己的分片 · 走 `state/frag_write.py` 原子写 · `answers` 52 → **60** 条 ★· 未写 hw/mech/sw 任何分片★)** ★ ⇒ ★**实测 `STATE.yaml` 6/6 条 `state=answered` (★need 在 hw.yaml `to=main` ⇒ 只有 pm.yaml 里同 key 的 answer 能闭合它★)** ★ ⇒ ★**留痕: 16:21 hw-lead 改写分片时把其中 2 条 need 改了名 ⇒ main 按新 key 重发同义裁决 2 条 ⇒ 旧 key 的 2 条 answer 成为孤儿 (★merge 提示『answers 的 key 没有对应 needs_from』★) · ★**不影响任何闭合, 已在 round log 登记** ★** ⇒ ★**needs 从 `pending` 变 `answered` (★merge 配对机制: need 在 hw.yaml `to=main` ⇒ 只有 pm.yaml 里同 key 的 answer 能闭合它★)** ★

### ★M-3 · ★★★【给老板的三条硬事实 —— 全部 main 16:2x 本机逐行实读, 不是抄交卷报告】★★★ ★★

★★**① 「左上布局」这条路今天过不了名单制闸 ⇒ ★**不能按原样落板** ★★ ⇒ ★**G7 的问题已经变了: 从「左上还是右上」变成「左上【之后】还要做什么才能过闸」⇒ ★**G7 这一票【不构成解锁】** ★★

★**实读 (`logs/iss325/10_compare_arm_official_lu_vs_official.txt` · 左上臂 vs 官方板)**: ★**DRC 违规 0 → 6 (恶化) · unc 45 → 29 · 零铜网 24 → 12 · 差分单边零铜 11 → 5 · 差分 Δ 超差 3 → 1** ★ ⇒ 但 ★**退铜名单 4 (`CSI_MCLK_SRC` `DSI_D0_CK_N_SRC` `LED_B` `USB_CC1`) + 差分对死腿 1 对 (`DSI_D0_CK_P_SRC`/`DSI_D0_CK_N_SRC`) + 逐网孤岛变多 9 个网 ⇒ 判定 REJECT** ★
★**⇒ 所以「unc 45 → 29」不是纯收益**: ★**这 16 条净改善里, 有一部分是「把『长了一半』重新打回『零铜』」的记账效应** ★ (★名单制闸自己算: 救回零铜的网 16 / 新欠 退铜 4 + 死腿 1 对 + 孤岛 9★) ★

★★**② 处方里的「21 器件」实际只有「10 器件」在起作用 ⇒ ★**那 10 行 `TP_DSI_*` 显式钉位是 no-op** ★★ (★根因 = `state/gen_pcb_netlist_board.py` L1042~L1060「测试点贴着伙伴件放」规则 ⇒ TP 自动跟随 R_SEL_*) ★ ⇒ ★**⇒ ISS-265 / LAYOUT_FIX_SPEC §1.2 那句「只钉 R_SEL 的另一半 = 给路由器埋雷」对今天的生成器是错的** ★ ⇒ ★**⇒ 那个处方本项目历史上已经跑过 8 次以上** ★

★★**③ 这两条臂【没构成对照】⇒ ★**任何「左上布局带来了多少」的因果归因本单给不了** ★★ (★main 实读 `logs/iss325/10c_compare_arm_official_ctl_vs_lu.txt`: 左上臂 vs 同日对照臂 = DRC 6/6 · unc 29/29 · unc 网名 27/27 · 零铜网 12/12 · 差分单边零铜 5/5 · 走线段 3666/3666 · 过孔 505/505 · 退铜 0 · 死腿 0 · 孤岛变多 0 ⇒ ★**逐项相同 ⇒ 变体落在 no-op 量上 ⇒ 对照天然失效**★) ★ ⇒ ★**⇒ G7 只准引用「逐条读数」+「左上臂过不了名单制闸」, 不准引用「29 vs 45」当功劳** ★ ⇒ ★**⇒ 若板那一趟还要做布局修正, 必须先定【一个生成器真会读的量】再开工** ★

★**⇒ 一句话给老板**: ★**这一趟 (板只改一次) 的 S8 不能只靠「挪器件」⇒ 布局只解决 12/17 处段内交叉; 要归零, 得同时动【机制】(12 个零铜网要换机制: 成对走廊 / 换层绕 / 让路闸 / pair-aware) + 【口径】(5 条待拍: A1 `BAT_DET` · W-1/W-2 `LIGHT_5V` · W-4 `PWR_GOOD` · `D_LED_G` 位置 · `FSIN_OUT`) + 【CSI 5 族换层绕】三样** ★ ★★**⇒ 所以 §A 那 4 个字母 + G6/G7/G8 的方向【没变】, 变的是【它们要解决的是哪几样】** ★

### ★M-4 · ★★本轮 main 的落账清单 (★全部 main 自己的地界★)★★

| 项 | 内容 |
|---|---|
| ★**`state/fragments/pm.yaml`** ★ | ★**+8 条 answer (52 → 60; 其中 6 条闭合 need + 2 条是改名前的同义重发) · 走 `state/frag_write.py` 原子写 · 备份 `pm.yaml.bak_20261118_1625_r74_main_answers`** ★ |
| ★**`DECISION_INDEX_2026-11-18.md`** ★ | ★**追加本节 §M (追加式 · 老字逐字未改 · 备份 `.bak_20261118_1630_r74`)** ★ |
| ★**`state/CURRENT_TASK.md` + `state/ROUND_LOG_775d_2026-11-18_1617.md`** ★ | ★**本轮记录 (老行保留作留痕)** ★ |
| ★**`PROGRESS_SNAPSHOT.md`** ★ | ★**本地快照 (本 job 不推 GitHub)** ★ |
| ★**没动的** ★ | ★**零写板 · 零落表 · 零改闸 · 零改 `state/issue_log.yaml` (★兄弟 job fb67af40 正在签 ISS-325/326/327 · 此刻写 issue_log 有并发覆盖风险★) · 零改别的 agent 的分片 · 零外发 · 不改 `PROJECT_TRACKER.md` §0** ★ |

### ★M-5 · ★★在飞状态 + 板面双证 + 本轮五门 rc + ★★本轮待派两条 (★为什么没开单★)★★

★**在飞 (★16:1x `sessions_list` 实读★)**: ★**① ISS-325 → hw-lead** (S8 左上布局沙盒预演 · ★会话 `bda6f342` cont1 在跑 · runtimeMs ≈ 1.39M ms★) · ★**② ISS-326 → mech-lead** (S1 改名 MECH 侧体检 · ★会话 `7a6ef3e1` 16:12:52 结束 status=done · ★issue 仍 `fixing` ⇒ 落地签字归兄弟 job★) · ★**③ ISS-327 → sw-lead** (改名后 SW 闸链复活验证 · ★会话 `2973946e` / `244a8206` 在跑★) ⇒ ★**铁律「一个 agent 同时只能一个写会话」⇒ 本 job 派 0 条** ★

★**板面双证 (★16:2x `md5sum` + `stat` 实读★)**: ★**板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未变 (12 天)** ★ · ★**网表 / 脚表 / BOM 未变** ★ ⇒ ★**G1 仍开, 不许投板** ★

★**本轮五门原样 rc (★16:2x~16:3x 本机实跑·日志落 `logs/cron775d_20261118_1617/`★)**:

| 脚本 | rc | 读数 |
|---|---|---|
| ★`merge.py` ★ | ★**0** ★ | ★{merge_sum}★ |
| ★`gate_check.py` ★ | ★**0** ★ | ★{q1} ★ · ★{q2} ★ · ★{q3} ★ · ★{q4} ★ · ★{q7} ★ · ★{gaps}★ |
| ★`issue_check.py` ★ | ★**0** ★ | ★{issue_tail} ★ |
| ★`stage_gate.py` ★ | ★**1** ★ | ★{stage} ★ · ★{stage_gaps} ★ |
| ★`daily_check.py` ★ | ★**3** ★ | ★{daily} ★ |

★**★★【本轮待派两条 · 为什么没开单】★★** ⇒ ★**① 【重跑一对真能构成对照的臂】(变体必须落在生成器真会读的量上 · 这是 G7 取证的唯一前提)** · ★**② 【生成器写盘前内容比对守卫】(修 `gen_kicad_project.py` 的无条件写盘 · 板那一趟开工前做)** ⇒ ★**本轮【没有开单】= 因为兄弟 job fb67af40 此刻正在签 ISS-325/326/327 (改 `state/issue_log.yaml`), 此刻并发写 issue_log 有覆盖风险 ⇒ ★**下一轮 (兄弟 job 空闲时) 由 main 开单, owner=hw-lead, 零写板 · 零落表 · 纯沙盒** ★ ⇒ ★**这两条已写进 `state/CURRENT_TASK.md` 的下一轮待办, 不靠记忆** ★

### ★M-6 · ★★本节自检 (★机器复核, 不是自述★)★★

- ★**拍板面: 40 条一条未动** ★ (★`advance.py --json` 逐 key 在本页命中 40/40★)
- ★**6 条 answer 全部落 `pm.yaml` 且 `STATE.yaml` 里 6/6 = `answered`** ★ (★`answers` 52 → 60 · 6 条 need 全闭合★)
- ★**板 md5 / mtime 未变** ★ (★`611b869e13518c3c023fb178f91a0075` · `2026-11-06 07:07:17.362193413`★)
- ★**本 job 零外发 · 零写板 · 零落表 · 零改闸 · 零改 issue_log · 零写别的 agent 的分片** ★
- ★**GitHub: 本 job 不推** ★ (★统一由独立 job「ARS45 GitHub 同步 (每 5 小时 · 有进展才推)」负责★) ⇒ ★**只落本地快照 `PROGRESS_SNAPSHOT.md`** ★
"""

with open(IDX, encoding="utf-8") as f:
    old = f.read()
old_md5 = hashlib.md5(old.encode("utf-8")).hexdigest()
if not os.path.exists(BAK):
    shutil.copy2(IDX, BAK)
with open(IDX, "a", encoding="utf-8") as f:
    f.write(SEC)
with open(IDX, encoding="utf-8") as f:
    new = f.read()
pre_ok = new.startswith(old)
print(f"old_md5={old_md5} | 老字逐字未变(前缀比对)={pre_ok} | 追加字节={len(new.encode())-len(old.encode())}")
sys.exit(0 if pre_ok else 1)
