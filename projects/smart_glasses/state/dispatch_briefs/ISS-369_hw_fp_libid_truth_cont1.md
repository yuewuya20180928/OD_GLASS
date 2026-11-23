# ISS-369 · hw-lead · ★「板那一趟」板面 186 封装库名写盘作业包 · ★★cont1 续做 (★上一趟 20:52 被 abort·读数全在盘·交付物零★)★★

★**这是 cont1 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-23 20:10 派) 的子会话在 20:52:45 被 abort, 死因 = `abortedLastRun=true` + 最后一句「The diff on a 4.9 MB file is slow. Let me wait for it.」⇒ 死在【4.9 MB 板文件整体 diff 卡住】那一刻** ★

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-369_hw_fp_libid_truth.md` ★

---

## ★★一 已在盘的 (★不要重跑·直接用★) ★★

| 东西 | 路径 | 大小 | 状态 |
|---|---|---|---|
| 板面 186 封装清单 | `tmp/iss369/board_inventory.json` | 365,613 B | ★**在盘·直接用**★ |
| 板面逐封装实测 | `tmp/iss369/board_probe_real.json` | 131,758 B | ★**在盘·直接用**★ |
| 分桶 | `tmp/iss369/buckets.json` | 5,336 B | ★**在盘**★ |
| 候选 96 件 | `tmp/iss369/cand96.json` | 18,232 B | ★**在盘**★ |
| 96 件等价性对照 | `tmp/iss369/equiv96.json` | 35,467 B | ★**在盘**★ |
| 库索引 | `tmp/iss369/lib_index.json` | — | ★**在盘**★ |
| 上一轮读数 | `tmp/iss369/iss364_recheck.json` · `tmp/iss369/mech/` | — | ★**在盘**★ |
| 基线 md5 | `logs/iss369/00_baseline_md5.txt` · `logs/iss369/00_baseline_pre.md5.txt` | 1,365 / 486 B | ★**在盘**★ |
| 沙盒读数 | `logs/iss369/10_sandbox_readings.json` · `11_sandbox_bodies.txt` · `12_sandbox_bytediff.json` | — | ★**在盘**★ |

★**⇒ 你要补的只剩【三件交付物】**: ★**① `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` ② ★新建 `HW/check_fp_libid_truth.py` (★本单产出·交卷时才有·★别当成现成命令跑★) ③ 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md`** ⇒ ★**别再对 4.9 MB 板文件做整体 diff (★那正是上一趟的死因★) ⇒ 要比就逐封装比 (★`tmp/iss369/board_probe_real.json` 里已有逐个实测★)** ★

## ★★二 main 已核实的订正 (★照这个写, 不要重新论证★) ★★

★**① KiCad 10 官方库 = 155 个 `.pretty` 库目录 / 15,468 个 `.kicad_mod` 封装文件** (★main 2026-11-23 本机实跑·`ls -d .../*.pretty | wc -l` 与 `find ... -name '*.kicad_mod' | wc -l`★) ⇒ ★**别再写「15,777 个 .pretty 目录」★ (★单位写错·★而且真数是 15,468 个封装文件, 155 个库目录★)** ★
★**② 库封装名是 metric 后缀命名** (★本机实测·★旧名按字面找不到文件★): `Resistor_SMD:R_0402_1005Metric` · `Capacitor_SMD:C_0402_1005Metric` · `Capacitor_SMD:C_0603_1608Metric` · `Capacitor_SMD:C_0805_2012Metric` · `LED_SMD:LED_0805_2012Metric` · `Inductor_SMD:L_0805_2012Metric` · `Button_Switch_SMD:SW_SPST_B3S-1000` (★**无裸 `SW_SPST`**) · ★**例外**: `Diode_SMD:D_SOD-323` / `D_SOD-123` 裸名在盘 ★ ⇒ ★**⇒ 你交的目标 `lib:name` 必须逐个 `test -f` 验【封装文件】在盘 (★不是只验库目录★), 并把 md5 写进表里** ★
★**③ C4 读数基线 = 158** (★`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ C4 占位脚号 158 个·★ISS-361 四桶: TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158★) ⇒ ★**沙盒证明的判据 = 换 land + 写库名后 C4 【仍是 158】⇒ 即【写库名这一腿对 C4 贡献 = 0】(★这与 ISS-361 实测的「腿A 对 C4 贡献 = 0」一致★) ⇒ 别写成「换 land 会让 C4 降下来」** ★
★**④ 靶子件数对账**: 靶内 **77** (ISS-356 已有目标 lib:name) + 缺口 **13** (ISS-361 已逐件补) = **90** 件 ⇒ ★**你页里 §4 那两张表 (90 + 96) 的件数必须与这个对账口径一致, 并写清 96 与 90 的差在哪 (★别自己另立口径★)** ★

## ★★三 边界 (★一条不许越·与原任务书相同★) ★★

★**零写板** (板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`) · ★**零落表** · ★**零改既有闸 / 零改既有页面正文** · ★**零外发** (★老板 2026-11-11 19:31 + 11-12 02:02 ⇒ 全靠自己查资料·缺口写降级方案·不许写「等原厂回信」★) · ★**不代老板拍板** · ★**只写自己的分片 `state/fragments/hw.yaml` (只走 `state/frag_write.py`·写前写后各记一次 md5·期间被别人改过 ⇒ 停下并在交卷页写明, 不许静默覆盖)** · ★**新建的闸不许挂 `state/gate_check.py`** (★挂链是 main 的地界·你只交脚本与路径 + 建议★) · ★**沙盒只落 `tmp/iss369/` + `logs/iss369/`** · ★**不自签 `state/issue_log.yaml`** ★

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 HW/check_fp_libid_truth.py
python3 HW/check_fp_libid_truth.py --selftest
python3 state/merge.py          # rc=0
python3 state/gate_check.py      # rc=0 · Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```
★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「上一趟 20:52 被 abort + 本趟从已落读数续做」** ★
★**收工后回卷**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★
