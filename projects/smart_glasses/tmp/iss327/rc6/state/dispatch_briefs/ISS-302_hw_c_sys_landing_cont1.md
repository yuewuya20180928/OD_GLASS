# ISS-302 · cont1 续做 (★2026-11-18 00:5x · cron fb67af40 重派僵尸 fixing★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-302
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 落表链侧 · 收尾 paperwork · 零写板** ★
> ★**外发**: ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)

---

## ★① 为什么是 cont1 (★main 00:4x~00:5x 本机实跑, 不抄任何 agent 报告★)

★**上一趟子会话已死**:
- `agent:hw-lead:subagent:ae23ed17` (sessionId `c3e684e9`) · 00:16:54 → **00:26:26** · runtime 568 s
- status = **timeout** · abortedLastRun = **true** ⇒ ★**死在「交卷单刚建好骨架、还没填」那一刻** ★
- ⇒ `state/issue_log.yaml` 里 ISS-302 的 status 卡在 **fixing** ⇒ ★**僵尸 fixing** (advance.py 的 in_flight 规则会把 hw-lead 整个挡住)

★**★主体其实【已经做完了】★★ (main 本机实测盘面):
| 项 | 实测 |
|---|---|
| ★**落表脚本** ★ | `state/_apply_iss302_csys_landing.py` (11,811 B · mtime **00:21**) ★ |
| ★**网表 L498/L499/L500** ★ | `SYS_CHG` / `C_SYS` 三行 **DNP → 必装** + ★**追加式订正** (★老字逐字留痕 + PM 老裁决『VSYS 脚不接 (NC)』标已作废 + 换成 ★**TI bq25896 SLUSC76C §7 逐字『Connect a 20uF closely to the SYS pin.』**★) ★ |
| ★**BOM** ★ | `HW/BOM_v1.csv` L48 = `C_SYS` · 1 · **20µF X7R 6.3V** · **必装** · 镜框充电板 · P10 ★ |
| ★**三件产物重生成** ★ | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` mtime 全 = **2026-11-18 00:21:08** ⇒ md5 由 `37f62ac3…`→`6aee500e…` / `a4270120…`→`9174309d…` / `5d02bece…`→`5b999399…` ★ |
| ★**落表台账** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 (★L1437 起★) + `<!--ISS302_ROWS-->` L1451~L1455 ★ |
| ★**板零变化** ★ | `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · mtime 仍 **2026-11-06 07:07:17.362193413** ★ |

★**⇒ 所以本单只剩【3 件 paperwork】** ★:
1. ★**交卷单 `HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md` = 778 B 骨架** ⇒ ★**B1 / B2 / B3 / B4 / B5 / B6 / §⑦ 七个块全是 `(待填)`** ⇒ ★**要填实** ★
2. ★**分片 `state/fragments/hw.yaml` 里 `grep -c iss302` = 0** ⇒ ★**一条都没写** ⇒ ★**要写 claim / answer / artifact + status** ★
3. ★**闸复跑的现场 rc 没有落盘** ⇒ ★**要跑一遍并把原样 rc 写进交卷单 B4** ★

---

## ★② ★★本单【不许】再动的东西 (★最关键的一条★)★★

★**落表已经做完了 ⇒ 本单是【收尾单】不是【落表单】** ⇒ ★**下列文件一个字节都不许再改**:
- ★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` ★ (★再跑一次生成器也可能把 mtime 弄花 ⇒ 不许★)
- ★`state/p10_rows.json` (★落表真源★) · `state/_apply_iss302_csys_landing.py` ★
- ★`HW/SCHEMATIC_LANDING_V1_LANDED.md` (★台账已写 §19 + ISS302_ROWS ⇒ 不许再动★)
- ★`HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` (★零写板★)

★**★也不许动这两道闸 (★它们红了, 但【不归本单】, 是本单落表【合法造成】的 ⇒ 另开单跟★)**:
- ★`HW/check_pin_function_labels.py` (★ISS-299 的重锚成果: 5 个基线一致 + 3 个基线在台账里可查 ✔ ⇒ **不许再重锚**★)
- ★`HW/check_workpack_state_values.py` / `MECH/check_onepass_struct_crosscheck.py` (★红的根因见 ★④ ⇒ 归 **ISS-304** / **ISS-303**★)

---

## ★③ 要交的三件 (★每件都能独立验收★)

### ★B1 · 交卷单填实 (★`HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md`★)
七个块都要有实打实的内容, **不许留 `(待填)`**:
- ★**B1 依据** = ★TI bq25896 datasheet **SLUSC76C §7** 逐字『Connect a 20uF closely to the SYS pin.』★ + 证据等级 **[官网]** + 台账 §19 的位置 ★
- ★**B2 改动清单** = ★网表 L498/L499/L500 三行的 dnp→必装 + 追加式订正 + BOM L48 一行 + ★**落表前后 md5 对照表** ★
- ★**B3 落表台账痕迹 + 锚点重锚记录** = ★台账 §19 · `<!--ISS302_ROWS-->` L1451~L1455 · ★**并说明「谁需要重锚」**(★`HW/check_workpack_state_values.py` 3 条 / `MECH/check_onepass_struct_crosscheck.py` N6 3 条 ⇒ 分别归 ISS-304 / ISS-303★) ★
- ★**B4 闸复跑现场 rc** = ★原样贴 (★见 ★④ 的表 + 自己的复跑日志路径★) ★
- ★**B5 板零变化自证** = ★板 + `.kicad_pro` 的 md5 + mtime (★双证★) + 三件落表产物的 md5 (★变了是【本单该有的】, 要说清楚★) ★
- ★**B6 分片 + 边界自证** = ★`grep -c iss302` 的值 + 边界逐条 ★
- ★**§⑦ 本单让哪些闸变红 / 哪些被前移 / 哪些纹丝不动** = ★如实写 (★红的两道闸要说清【是本单合法落表造成】且【已另开 ISS-303 / ISS-304 跟】★) ★

★**★真判据 (★main 实测的坑★)**: ★`python3 state/check_report_placeholders.py < <交卷单>` **抓不到 `🔄 待填` / `★(…填入…)★` 这种形态** ⇒ ★**真判据是 `grep -cE "🔄|待填"` 必须 = 0** ★ ⇒ ★**自己写完自己跑一遍** ★

### ★B2 · 分片 (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★)
★**写完必须 `grep -c iss302 state/fragments/hw.yaml` 校验 (★目标 ≥ 5★)** ⇒ ★**要写: ① claim (落表本体) ② claim (零写板自证) ③ answer (给 main 的 2 条: 两道闸变红分别归谁) ④ artifact (交卷单) ⑤ status (phase=delivered · progress_pct=100 · health=绿)★**
★**不许用 `open(p,"w")` 直接写 yaml** ★

### ★B3 · 闸复跑 + 日志落盘
★**跑完把原样 rc 写进交卷单 B4 + 日志落 `logs/iss302/` (★目录自己建★)** ★

---

## ★④ ★★main 00:5x 本机实跑的闸现状 (★18 道逐条, 原样 rc★)★★

★**你要复跑一遍并把自己那份原样贴进 B4 (★以下是我 00:5x 的读数, 不是最终结论★)**:

| 闸 | rc | 读数 | 归谁 |
|---|---|---|---|
| ★`HW/check_pin_function_labels.py` ★ | **1** | ★15 条缺陷 = ★**既有缺陷基线** (脚表功能串号) + ★「5 个基线全部一致 + 3 个基线在落表台账里可查 ✔」⇒ ★**本单落表没打断它**★ | ★既有基线 (★下一批落表里修★) ⇒ **不许动它** ★ |
| ★`HW/check_pin_function_labels.py --selftest` ★ | 0 | — | — |
| ★`HW/check_step1_parts_spec.py` ★ | 0 | 8/8 | — |
| ★`HW/check_onepass_preflight_coverage.py` ★ | 0 | — | — |
| ★`HW/check_g1a7_selection_landed.py` ★ | 0 | — | — |
| ★`HW/check_onepass_commit_order.py` ★ | 0 | — | — |
| ★`HW/check_workpack_state_values.py` ★ | **1** | ★3 条: `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER` ⇒ ★**作业包/清单页里的现值没跟上盘面**★ | ★**ISS-304** (★不是本单★) ★ |
| ★`HW/check_fsin_rootcause.py` ★ | 0 | — | — |
| ★`SW/tools/check_demo_panel_spec.py` ★ | 0 | — | — |
| ★`SW/tools/timing_check.py` ★ | 0 | — | — |
| ★`SW/tools/check_onepass_sw_sync.py` ★ | 0 | — | — |
| ★`MECH/check_onepass_mech_release.py` ★ | **1** | ★汇总 6 道闸 = ★**绿 5 / 红 1** ⇒ 红的那道 = `MECH/check_onepass_struct_crosscheck.py` ★ | ★**ISS-303** (★不是本单★) ★ |
| ★`MECH/check_mech_verdict_freshness.py` ★ | 0 | — | — |
| ★`MECH/check_onepass_mech_sync.py` ★ | 0 | — | — |
| ★`MECH/check_onepass_struct_crosscheck.py` ★ | **1** | ★3 条 N6 受保护件被改: 网表 `37f62ac3…`→`6aee500e…` / 脚表 `a4270120…`→`9174309d…` / BOM `5d02bece…`→`5b999399…` ⇒ ★**这台闸只认硬基线, 不认【合法落表跳】**★ | ★**ISS-303** (★不是本单★) ★ |
| ★`MECH/check_demo_struct_truth.py` ★ | 0 | — | — |
| ★`MECH/check_board_frame_coords.py` ★ | 0 | — | — |
| ★`state/gate_check.py` ★ | **1** | ★Q1 18/18 ✔ · ★**Q7 钉板 md5 闸链 = 8/9 绿** ⇒ ★红的是「钉板闸⑥ 作业包现状值闸」★ ⇒ ★**板那一趟不许开工** ★ | ★**ISS-304** (★不是本单★) ★ |
| ★`state/issue_check.py` ★ | 0 | — | — |

★**★关键纪律**: ★**上表里红的 4 道闸, 本单【不许】靠"改判据"或"改基线常量"去消红** ⇒ ★**那是 ISS-303 / ISS-304 的活** ⇒ ★**本单只如实记录「本单合法落表 ⇒ 这几道闸转红, 已另开单跟」** ★

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 + `.kicad_pro` md5/mtime 逐字节不变★) · ★**零落表** (★★本单落表已完成 ⇒ 网表/脚表/BOM/台账/`state/p10_rows.json` 一个字节不许再动★) ★
· ★**不许动别人的闸** (★`HW/check_pin_function_labels.py` / `HW/check_workpack_state_values.py` / `MECH/*` 一律不许改★) ★
· ★**不许放宽任何判据 / 不许改任何基线常量** ★ · ★**零外发** (★没有"批一句可以发"这个选项★) ★
· ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** (★签字是 main 的活★) · ★**只写自己那一份分片** (★`hw.yaml`; `mech.yaml`/`sw.yaml`/`pm.yaml` 一个字节不许碰★) ★
· ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★) · ★**实物 `[实测]` = 0 条** (★本机无板无量具 ⇒ 不许编★)

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★骨架已在盘, 778 B ⇒ 直接逐节填★)** ★
· ★**长任务一律 `nohup ... > logs/iss302/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★
· ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
· ★**★上一趟就是被掐死的 (★568 s 超时★) ⇒ ★★本趟一开工就先把骨架填成【有内容】, 别留到最后一起写★★** ★

★**交卷前必跑 (★rc 原样贴进回复★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$?"     # ★Q1 必须 18/18; ★Q7 现在是 8/9 (钉板闸⑥红 = ISS-304) ⇒ 原样写, 不许掩饰★
python3 state/issue_check.py; echo "rc=$?"
grep -cE "🔄|待填" HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md   # ★必须 0★
grep -c iss302 state/fragments/hw.yaml                            # ★必须 ≥ 5★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```
