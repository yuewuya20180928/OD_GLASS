# ISS-320 · mech-lead · ★★cont1 续做说明★★ (★子会话被父 run 连带 abort · 不是从零重做★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-320
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 10:4x** ★
> ★**性质**: 内部活 · 受限文本订正类 (★MECH 域 33 行 / 19 个 MECH 活文件·含 9 个脚本★) · 零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**原任务书全文 (★一个字不许删★)**: `state/dispatch_briefs/ISS-320_mech_cell_model_rename_apply.md` (★逐字也存 `state/issue_log.yaml` 的 ISS-320.task_brief★)

---

## ★0 · main 10:4x 本机实读的事实 (★你上一趟做了什么 / 没做什么★)

★**子会话 `agent:mech-lead:subagent:4f567584-...` 09:17:03 起 · 09:24:27 死 (status=timeout · errorMessage="This operation was aborted")** ⇒ **死因 = 父 cron run 结束把子会话连带 abort (不是你的错)** ★

### ★**已经在盘上的 (★直接用★)** ★
- `MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md` (7,076 B) — ★**★main 09:1x 先落的台账骨架 (33 行清单 + 分类)★** ★
- `logs/iss320/cell_model_scan_BEFORE.txt` + `cell_model_scan_raw_FULL.txt` + `md5_BEFORE.txt` + `md5_BEFORE_tables.txt` + `mech_gates_BEFORE.txt` + `script_gates_BEFORE.txt` — ★**★你上一趟跑的 BEFORE 快照 (★不要重跑 BEFORE, 直接用这几份★)★** ★
- ★**★main 09:17 已经把【HW 域的 3 行】改完了 (★MECH 域之外的活, 不用你再碰★)★**:
  `HW/POWER_BUDGET_V3.md` L27/L259 (md5 `988e5eb…` → `94f1dfd6…`) + `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L1046 (md5 `642ef9b1…` → `28b54fd8…`) ⇒ ★**自证 = 改后文件 == 「改前内容做一次全量替换」的期望版本, 逐字节相同; 每行「除型号名外」的数字序列逐位相同★** ★

### ★**还没落盘的 (★本趟要干的活★)** ★
- ★**MECH 域一个字没改**: main 10:0x 实测 `grep -rl "ICP582035PR-01" MECH/` 命中 **23 个文件** (★含 `MECH/print/__pycache__/*.pyc` ⇒ **.pyc 不许碰**★) ⇒ ★**你要改的是 ISS-319 查清的【33 行 / 19 个活文件】(口径行 23 + 脚本行 10)★** ★
- ★**交卷页 `HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md` 还是 main 09:1x 落的骨架 (1,430 B) ⇒ B0~B6 六节全是「★待回填★」** ★
- ★**`state/fragments/mech.yaml` 一个字没写** (★mtime 还是 08:46:20 · status 段仍写 ISS-319★) ★

---

## ★1 · 本趟的最小可接受交卷线 (★时间不够就交到这个程度, 但必须交★)

1. ★**★台账 `MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md` 逐行回填★**: 33 行每行给「改前逐字 → 改后逐字 → 改了哪一行 → 自证 (数字指纹逐位相同) ⇒ 逐行落盘, 不许攒到最后一起写** ★
2. ★**★只准改型号名 `ICP582035PR-01` → `ICP422339PR`★** ⇒ ★**尺寸/重量/容量常量 (4.60 / 23.50 / 40.50 / 340mAh 等) 一个数字不许动** ★ ⇒ ★**11 行留证/对照行一行都不许碰** ★
3. ★**改完的 BEFORE/AFTER 双证**: 每个改过的文件给 md5 + 改前后全文 (★放 `logs/iss320/`★) + ★**逐行数字序列相同 = True** 的机器判读数★ ★
4. ★**交卷页 B0~B6 齐全 + 占位符 = 0 + 分片写完 (★经 `state/frag_write.py --agent mech-lead` 原子写·禁 `open(p,"w")`★)★** ★
5. ★**MECH 域七道闸复跑 rc=0**: `board_frame_feasibility.py` · `check_onepass_mech_sync.py` · `check_onepass_struct_crosscheck.py` · `check_onepass_mech_release.py` · `check_board_frame_coords.py` · `check_mech_verdict_freshness.py` · `service_port_check.py` ★

---

## ★2 · ★★纪律 (★本轮针对实测死亡模式的硬约束★★) ★★

- ★**先落纸 —— 每改完一个文件就把那一行回填进台账, 宁可交半成品台账, 不许一行不落** ★ (★上一趟就是「只跑了 BEFORE 快照就死了」⇒ 成果全丢★)
- ★**零写板**: 板 md5 必须 = `611b869e13518c3c023fb178f91a0075` + mtime = `2026-11-06 07:07:17.362193413` ★
- ★**零落表** (★网表/脚表/BOM 一律不许动★) · ★**零重生成** (★不许跑 `gen_*`·不许重出 Gerber/投产包★) · ★**零改闸** ★
- ★**`.pyc` / `__pycache__` 不许碰** (★二进制, 改了算越界★)
- ★**零外发**: ★**不许发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
- ★**证据分级** [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 (★电芯规格本身必须是 [官网]·renata.com 实读·别用转述★)
- ★**不许替老板拍板** · ★**不许自签 issue_log**

---

## ★3 · 交卷前必跑 (★原样贴进回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
for g in MECH/board_frame_feasibility.py MECH/check_onepass_mech_sync.py MECH/check_onepass_struct_crosscheck.py \
         MECH/check_onepass_mech_release.py MECH/check_board_frame_coords.py MECH/check_mech_verdict_freshness.py \
         MECH/service_port_check.py; do timeout 180 python3 $g >/dev/null 2>&1; echo "$g rc=$?"; done
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb               # 必须 = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|待回填" HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md   # 必须 = 0
grep -rc "iss320" state/fragments/mech.yaml               # 必须 >= 1 (★分片写了没有★)
```
