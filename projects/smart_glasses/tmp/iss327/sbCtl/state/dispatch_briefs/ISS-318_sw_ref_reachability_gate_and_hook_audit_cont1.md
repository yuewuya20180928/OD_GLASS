# ISS-318 · sw-lead · ★★cont1 续做说明★★ (★僵尸 fixing 重派 · 不是从零重做★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-318
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 09:1x** ★
> ★**原任务书全文 (★一个字不许删★)**: `state/dispatch_briefs/ISS-318_sw_ref_reachability_gate_and_hook_audit.md` (12,860 B)
> ★**性质不变**: ★**内部活 · 判据新建 + 判据修复类 · 零写板 · 零落表 · 零改 `state/gate_check.py` · 零改既有判据方向 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · ★为什么有这张 cont1 (★main 09:1x 本机实读, 不抄任何 agent 报告★) ★

★**上一趟子会话**: `agent:sw-lead:subagent:9a69ba4d-c4e2-413d-bc47-5652ce5743f1` (taskName `queue_iss318`)
⇒ ★**08:39:23 起 · 08:56:05 死** ★ · ★**runtimeMs=1001857 · status=failed (末尾两条 toolResult = 「Aborted」)★** ★
⇒ ★**死因 = 父 cron run 结束时子会话被连带 abort (★与 ISS-308 / ISS-309 同一个死法★) ⇒ 不是 sw-lead 的错, 是派活机制的错** ★

★**⇒ 上一趟 = 僵尸 fixing**:
- ★**交卷页只有骨架**: `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md` = ★**906 B**, 末尾写着 ★**「(施工中 · 逐条回填)」⇒ 没交卷★**
- ★**sw 分片没更新**: `state/fragments/sw.yaml` mtime `07:51:05` · status 段仍写 ISS-315 ⇒ `grep -c iss318` = 0
- ⇒ ⇒ **sw-lead 整个被挡 (★advance.py 的 in_flight 规则★)** ★
- ★**★而且这张骨架页已经把 Q1 齐备率顶住了**: ★**`state/gate_check.py` 的 Q1 现在写「sw-lead 用了【回退】⇒ 最新一份 ISS318 缺块, 按老的 ISS315 计分」⇒ ⇒ 交卷页不补齐, 齐备率就一直算老的** ★

★**★但上一趟的成果【已经在盘上】(★main 09:1x 本机实读 + 本机实跑核对★) ⇒ ★**本单按【续做, 不是从零重做】处理** ★ ★

| 在盘成果 | 路径 (★实读 size + mtime★) | ★main 09:1x 本机实跑的结论★ |
|---|---|---|
| ★**★新闸本体 (★已经合格★)** ★ | `SW/tools/check_sw_ref_reachability.py` (41,350 B · 08:50) | ★**裸跑 rc=0** (★判决「✔ 绿: SW 侧引用的位号全部可达, 真隐患在基线内」★) · ★**`--selftest` ⇒ 反向用例 7/7 通过** ★ |
| ★**闸的实跑输出** ★ | `logs/iss318/ref_reachability_run.txt` (18,945 B) | ★逐条列出 107 个唯一标识符的分类与判决★ |
| ★**R3 现状基线清单** ★ | `logs/iss318/r3_baseline_table.md` (9,308 B) | ★**扫描面 40 份 `SW/*.md` · 107 个唯一标识符 · 板位号 186 / 网表位号 293 / 网名 654 ⇒ 现在有 3 条位号引用对不上 (= 闸的允许上限 `BASELINE_COUNT`=3)** ★ |
| ★**挂链前体检** ★ | `logs/iss318/healthcheck_with_tmpdir.txt` (2,768 B) | ★**★关键坑: 三道 selftest 闸【必须不带 `--selftest` 裸跑】⇒ 带了 ⇒ rc=2 usage 错误★** (见 §1) ★ |
| ★**板那一趟留痕义务实测** ★ | `logs/iss318/probe_landing_trace_board_trip.py` (7,213 B) + `.txt` (4,849 B) | ★E-0~E-3 四场景: 现状绿 / 假单号红 / 补留痕绿 / 假单号红★ |
| ★**缺件** ★ | — | ★**md5 前后对照** · ★**占位符扫描** · ★**交卷页正文** · ★**sw 分片更新** ★ |

---

## ★1 · ★★main 09:1x 实跑出来的三条硬结论 (★你必须独立复核, 但别再从零推一遍★) ★★

★**① 新闸已经能用 (★main 09:1x 本机实跑·不是抄你的报告★)** ★
```
python3 SW/tools/check_sw_ref_reachability.py            → rc=0   (判决「✔ 绿」)
python3 SW/tools/check_sw_ref_reachability.py --selftest  → rc=0   (反向用例 7/7)
```
★**--selftest 的 7 条里最值钱的是这三条 (★main 已逐条读过输出★)** ★
```
RC-2 期望=red  破坏板文件里一个 SW 文档引用的位号 ⇒ rc=1 (红项: 改名漂移:C_DET_BAT) ★不是巧合自证★
RC-3 期望=red  破坏网表里一个 SW 文档引用的位号       ⇒ rc=1 (红项: 改名漂移:R_ILIM)   ★不是巧合自证★
RC-4/RC-5       板文件/网表读不到 ⇒ rc=2 (fail-closed: 输入文件不存在) ★不是巧合自证★
RC-6/RC-7 期望=green  板改名 + SW 文档同步改成新名 ⇒ 绿 ★正向对照: 闸没被写成永远红★
```
★**⇒ 这闸能抓「板改了 · SW 文档没跟着改」= ISS-318 立这道闸的本意 ⇒ 本单不用再重做闸本体, 只需把它收进交卷页★**

★**② 挂链的最大坑: 三道 selftest 闸【不带 `--selftest` 裸跑】(★main 09:1x 实读 `logs/iss318/healthcheck_with_tmpdir.txt`★)** ★
```
check_landing_trace_obligation.py                      裸跑 rc=0 (0.14s)  |  --selftest rc=0 (0.55s)  ★支持 --selftest★
check_demo_panel_spec_r6_hardprot_iss315_selftest.py   裸跑 rc=0 (1.28s)  |  带 --selftest ⇒ rc=2 (usage 错误) ★
check_demo_panel_spec_r6_chainjudge_selftest.py         裸跑 rc=0 (0.66s)  |  带 --selftest ⇒ rc=2 (usage 错误) ★
check_demo_panel_spec_r6_selftest.py                    裸跑 rc=0 (0.92s)  |  带 --selftest ⇒ rc=2 (usage 错误) ★
```
★**⇒ 挂闸写法里【必须】把这三道闸写成【裸跑】(★它们本来就是 selftest 脚本, 裸跑就是跑全部反向用例★)⇒ ⇒ 否则挂上去 day-1 就红** ★
★**⇒ 另一条坑**: ★**挂闸时必须带 `TMPDIR` (★`--tmpdir` / 环境变量★) ⇒ 不设 TMPDIR 时这几道闸会在仓根留垃圾目录★** ★

★**③ 留痕义务的方向已经验过 (★`logs/iss318/probe_landing_trace_board_trip.txt`·E-0~E-3★)** ★
```
E-0 现状盘面 (不加任何东西)                ⇒ 义务条数 3 · 红项 0 ⇒ 绿
E-1 台账加板的变更行 (真单号 ISS-302) · issue_log 没留痕 ⇒ 义务条数 4 · 红项 1 ⇒ 红
E-2 同 E-1 + issue_log 补了【文件名 + 新 md5】留痕            ⇒ 红项 0 ⇒ 绿
E-3 台账加板的变更行 (假单号 ISS-9900)                        ⇒ 红项 1 ⇒ 红
```
★**⇒ 「板那一趟」的单号留痕义务【现在是生效的】⇒ ⇒ 板那一趟开工前, 单号 + 新 md5 必须落进 `state/issue_log.yaml` ⇒ 否则那条闸红 (★这是留痕红, 不是技术红★)** ★

---

## ★2 · ★续做清单 (★按这个顺序做, 先交卷再完美★) ★

★**★① 先把交卷页从 906 B 骨架补成完整交卷页 (★这一条就是本单的主要工作量★)★**
- `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md` (★就地补齐, 别另开新文件★)
- ★**B0 一句话 + 交付物清单 / B1 结论摘要 / B2 验收标准自评(逐条 通过|不通过|未验) / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 (★B0~B6 齐全·少一块 Q1 就走回退★)★**
- ★**★交卷页必须写清这三件事 (★是 main 要拿它做决定的★)★**
  1. ★**新闸现在判绿** ⇒ SW 侧 95 处位号引用【当前全部可达】, 现在只有 ★**3 条**对不上 (= `BASELINE_COUNT` 上限) ⇒ **逐条列出这 3 条** (★从 `logs/iss318/r3_baseline_table.md` 里取★) + 处置建议 (★改文档 / 加白名单 / 判定为本来就对不上★) ★
  2. ★**挂闸的逐字写法 (★挂闸是 main 的机制地界·本单只交写法, 一个字节都不许改 `state/gate_check.py`★)★**
     ⇒ ★**给出可直接抄进 `EXTRA_GATES` 的行 (★含: 三道 selftest 闸写成【裸跑】· `TMPDIR` 怎么设 · 每道闸的 rc/耗时/会不会假红★)★**
     ⇒ ★**并写清「板那一趟」开工前它会不会因为留痕红 (★见 §1 ③★)」★**
  3. ★**ISS-315 交 main 拍的 5 条 need 里, 「挂闸」那条 (N-3) 现在有了逐字答案 ⇒ ⇒ 交 need 给 main (★key + 一句话问法 + 不拍的后果★)★**

★**② 补 `logs/iss318/` 的缺件**
- ★**md5 前后对照** (★板 / 网表 / 脚表 / BOM / `SW/SW_MD5_BASELINE_LEDGER.md` / `state/gate_check.py` / 既有判据脚本 全部不许动 ⇒ 交卷前后逐字节相同★) ★
- ★**占位符扫描** (`grep -cE "🔄|待填|PLACEHOLDER" <交卷页>` ⇒ 0) ★
- ★**闸的 `--selftest` 7/7 原始输出另存** (★不要覆盖 `logs/iss318/ref_reachability_run.txt`·另起文件名★) ★

★**③ sw 分片更新**
- ★**用 `state/frag_write.py --agent sw-lead` 原子写 `state/fragments/sw.yaml`** (★禁止 `open(p,"w")`★) ⇒ status 段换成 ISS-318 的交卷摘要 + 新增 artifact + need ★
- ★**`hw.yaml` / `mech.yaml` / `pm.yaml` / `state/issue_log.yaml` 一个字节不许碰** ★

★**④ 交卷前必跑 (★输出原样贴进回复★)**
```
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
                                                       # ★注意: 交卷页补齐前 Q1 会写「sw-lead 用了回退」⇒ 补齐后再跑才看得到 18/18★
python3 SW/tools/check_sw_ref_reachability.py            # rc=0
python3 SW/tools/check_sw_ref_reachability.py --selftest  # rc=0 (7/7)
python3 SW/tools/check_demo_panel_spec.py                # rc=0 (既有判据不许变红)
python3 SW/tools/check_demo_panel_spec_r6_selftest.py    # rc=0 (★裸跑·带 --selftest 会 rc=2★)
md5sum HW/PCB/demo_mainboard.kicad_pcb                   # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb             # 必须 = 2026-11-06 07:07:17.362193413
```

★**⑤ 时间预算纪律 (★这一趟的教训★)**
★**上一趟 16 分钟被父 run 连带 abort ⇒ ⇒ 【先落纸再干活】**: 每完成 §2 的一条就把结论回填进交卷页 (★哪怕是「未验, 原因 X」★) ⇒ ★**宁可交半成品页, 不许一页纸都不落** ★

---

## ★3 · ★边界 (★硬★) ★
- ★**零写板** (板 `HW/PCB/demo_mainboard.kicad_pcb` 一个字节不许动) ★
- ★**零落表** (不许改 `HW/netlist_v1*.csv` / `HW/BOM_v1.csv` / 任何 `.kicad_sch`) ★
- ★**零改 `state/gate_check.py`** (★挂闸是 main 的机制地界·本单只交逐字写法★) ★
- ★**零改既有判据方向** (★`check_demo_panel_spec.py` / `check_onepass_sw_sync.py` / `check_landing_trace_obligation.py` / 三道 selftest 脚本 一律不许改★) ★
- ★**零改 SW 侧既有文档正文** (★那 95 处位号引用【现在不动】·本单只出闸★) ★
- ★**零改 `SW/SW_MD5_BASELINE_LEDGER.md`** (★它就是判据的锚点账★) ★
- ★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** · ★**不许改 `state/issue_log.yaml`** ★

---

## ★4 · ★交卷格式 ★
- 交卷页 `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md` (★B0~B6 齐全★)
- `logs/iss318/` 原始输出 (★每个读数都要有对应原始输出文件★)
- `state/fragments/sw.yaml` (★只改自己那一份★)
