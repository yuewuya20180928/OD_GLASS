# ISS-293 · sw-lead · 【cont1 续做】· ★★本单改【续做】, 不许从零重做★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 17:4x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-293 · ★**零外发** ★
> ★**原任务书全文 = `state/dispatch_briefs/ISS-293_sw_adc_fullscale_caliber_review_sync.md` (★18821 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ⇒ ★**第一条 (必做)**: 先 cat 那份原文 ★
> ★**本文件 = cont1 追加节 (★与原任务书【合起来】才是完整任务书★)**

---

## ★⓪ 上一趟的会话死了 (★不是活干完★)

★`agent:sw-lead:subagent:d5e931dd-ebd6-4945-93da-c32b47897429` (sessionId `cfd5aeac`) ★**17:05:53 → 17:18:06 · runtime 733s · status=failed** ★
⇒ ★**交卷单停在骨架**: `HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md` = **935 B** (★交付物清单已列, 但 7 项进度里只勾了「读任务书全文」; B1 / B2 / 反向用例 / 回归 / 分片 全未勾★)
⇒ ★**分片也没写完**: `state/fragments/sw.yaml` 里 `grep -c iss293` = **1** (★只有那条 need `iss293_sw_m7r6_sync_to_main`; artifacts / interface_claim / status 三块全没写★)

## ★★但大块已经在盘上了 ⇒ 不许重做 ★★

★以下全部是 ★**main 2026-11-17 17:4x 本机实跑 (★自己实跑, 不抄任何 agent 报告★)** ★:

| 件 | 盘上实测 | main 实跑结果 |
|---|---|---|
| `SW/SW_TIMING_REVIEW.md` | ★**90918 B** (mtime 17:11:55) ⇒ B1 文档订正【已落盘】★ | ★闸 29/29 全 ✔ ⇒ 文档侧达标★ |
| `SW/tools/check_timing_review_adc_sync.py` | ★**20595 B** (mtime 17:11:12) ⇒ B2 新闸【已落盘】★ | ★`python3 SW/tools/check_timing_review_adc_sync.py` ⇒ ★**rc=0 · 29/29 项通过** ★ |
| 同上 `--selftest` | — | ★**rc=0 · SELFTEST 4/4 通过** (★case1_revert_fs_pct / case2_revert_chain / case3_revert_populated 三条都变红 + case4_baseline 正向对照绿; 真件读回 90918 B 未变★) ★ |

★**⇒ 本趟真正的活只有 4 件 (★只有这 4 件★) ★**

### ★F1 · 交卷单填满 (★现在 = 935 B 骨架★)

★`HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md` ★**B0~B6 七块全部要填** ★
⇒ ★每块内容必须贴【★**本趟自己实跑的原样 rc**★】, ★不许抄上一趟、不许抄 main 的读数★ ⇒ ★占位符残留 grep 必须 **0** ★

### ★F2 · B1 逐条对账表 (★只补漏, 不许整份重写文档★)

★把下面 8 条逐条对到文档里 (★main 已实测 29/29 绿 ⇒ 大概率已齐, 你只需核对 + 把对账表写进交卷单★):

| # | 文档里必须有的现值 |
|---|---|
| 1 | 判决对象 = `BAT_DET` 的明文 (带订正标记) |
| 2 | 满量程 `1.8` (V) |
| 3 | LSB `0.439` (mV) |
| 4 | 漏电偏移 `2.1%FS` |
| 5 | `R_th` = `37500` (Ω) |
| 6 | 建立时间 `33.791` (ms) |
| 7 | BAT_DET 三颗**必装** 的明文 |
| 8 | ★**活结论里不再残留 3.3V 口径旧数 / ADC ❌ 行 / 「三颗全 DNP」** ★ |

★**若某一处实际漏了 ⇒ 只补那一处 (追加式, 老字不删) ⇒ 补完重跑 `python3 SW/tools/check_timing_review_adc_sync.py` 必须仍 rc=0★**

### ★F3 · 回归命令 ★**你自己跑一遍**★ 并把原样 rc 贴进交卷单

★(★main 只替你验了闸本身; 回归要你自己跑, 不许抄 main 的 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_timing_review_adc_sync.py; echo "rc=$?"
python3 SW/tools/check_timing_review_adc_sync.py --selftest; echo "rc=$?"
python3 SW/tools/timing_check.py; echo "rc=$?"
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**期望**: 闸 rc=0 · selftest rc=0 (4/4) · `timing_check.py` rc=0 · `check_demo_panel_spec.py` rc=0 · merge rc=0 · gate_check rc=0 (★**Q1 18/18**★) · 受保护 5 件 md5 逐字 = 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★
★**板 mtime 也必须仍是 `2026-11-06 07:07:17` (★零写板双重自证★)★**

### ★F4 · 分片补完 (★走原子写★)

★`state/fragments/sw.yaml` 现在 `grep -c iss293` = **1** ⇒ ★**artifacts (3 件: 文档 / 新闸 / 交卷单) + interface_claim + status 三块全都没写** ★
⇒ ★**必须走 `python3 state/frag_write.py --agent sw-lead` 原子写** (★★禁止 `open(p,"w")`★★) ⇒ 写完 `grep -c iss293 state/fragments/sw.yaml` 必须 **≥ 4** ⇒ ★并把你那条已有 need (`iss293_sw_m7r6_sync_to_main`) 保留 (★不许删★)★

---

## ★★边界 (★不许越★) ★★

- ★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表 / 脚表 / BOM 一个字节不许动★)
- ★**不许改 `SW/tools/timing_check.py`** (★那是 ISS-288 的闸, 本单不许碰★)
- ★**不许改 `SW/tools/check_demo_panel_spec.py`** (★ISS-275 已跑通的链头逻辑不许动★)
- ★**不许改 `SW/SW_REQUIREMENTS.md`** (★需求真源是 PM 域 ⇒ 你只登记 need, 不自改★)
- ★**不许动 `HW/` 与 `MECH/` 的任何文件与分片** (★只写 `state/fragments/sw.yaml`★)
- ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ **没有「批一句可以发」这个选项**★)
- ★**不自签 issue_log** (★签字是 main 的活★)
- ★**长任务一律 `nohup ... > logs/iss293/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★

## ★★交卷时必须贴进回复的三样 ★★

1. ★**F3 那 6 条命令的原样 rc** ★
2. ★`grep -c iss293 state/fragments/sw.yaml` 的原样输出 ★
3. ★**交卷单 B0~B6 七块的占位符残留 grep 结果 (必须 0)** ★
