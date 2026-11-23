# ISS-372 · sw-lead · ★「板那一趟」SW 侧板 md5 引用面清账 + 清单自守 · ★★cont1 续做 (★上一趟 21:30 failed·扫描已落·三件交付物零★)★★

★**这是 cont1 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-23 21:2x 派) 的子会话于 21:30:28 failed (★sessions_list status=failed·transcript 末写 21:30:28·**没有更新的续跑 sessionId** ⇒ 按 main 的「三与」判据 = 真死·不是假死★)** ★

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-372_sw_board_md5_rebase_readiness.md` ★

---

## ★★一 已在盘的 (★不要重跑·直接用★) ★★

| 东西 | 路径 | 大小 | 状态 |
|---|---|---|---|
| SW 域 md5 引用全扫 | `logs/iss372/01_scan_sw_md5_refs.txt` | 37,048 B (21:25) | ★**在盘·直接用**★ |
| 逐行版 | `logs/iss372/02_scan_sw_md5_refs_lines.txt` | 14,863 B (21:27) | ★**在盘**★ |
| 原理图 11 份 md5 实验 | `logs/iss372/03_exp1_sch_md5.txt` | 7,480 B | ★**在盘**★ |
| 11 份清单 | `logs/iss372/04_sch_md5_11files.txt` | 757 B | ★**在盘**★ |
| 实验脚本 | `tmp/iss372/exp1_sch_md5.py` · `tmp/iss372/exp2_reboard.py` · `tmp/iss372/tree/` | — | ★**在盘**★ |

★**⇒ 你要补的只剩【三件交付物】**: ★**① `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` ② 新建闸 `SW/tools/check_sw_board_md5_rebase_readiness.py` ③ 交卷页 `HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md` + `state/fragments/sw.yaml` 分片登记** ★

## ★★二 main 已核实的订正 (★照这个写·不要重新论证★) ★★

★**① 「11 份原理图 md5 不能当锚点」的机理 (★ISS-249 实测·★你页里要写清机理, 不要只写结论★)★**: ★**`state/check_sch_pinfull.py` 与 `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 跑这两道门禁就会【重铸随机 UUID】⇒ 任何门禁跑完 md5 都变 ⇒ 只能当【归一化 UUID+时间戳后是否同图】的判据 (★ISS-249 实测 11/11 SAME★)** ⇒ ★**⇒ 这就是「那张 11-17 生成的钉板 md5 清单」为什么会在今天失效的根因** ★
★**② 「57 处硬写旧板 md5」分三类处置方式完全相反 (★判据锚 / 规格页引用 / 历史留证★) ⇒ ★**不许全仓 sed 替换一遍** ⇒ ★**历史留证那几处一个字都不许动** ★
★**③ 新造的 2 道 SW 闸 (ISS-363 / ISS-370) 既没进那张清单, 也没有合法改板通道 ⇒ 改板当天它们必红 (F5 / G8 判据·★本机实读确认★) ⇒ 红的真含义是「板被换了」⇒ 现场极可能误读成「改板凑绿」⇒ 板 md5 变第二次** ⇒ ★**你交的自守闸要能提前抓住「清单过期」这件事, 而不是等改板当天才红** ★
★**④ 板 md5 基线**: `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**你页里引用它必须逐字一致** ★

## ★★三 边界 (★一条不许越·与原任务书相同★) ★★

★**零写板** · ★**零落表** (★网表 / 脚表 / BOM / 落表台账 / 原理图 11 个 / `issue_log.yaml` 一字不改★) · ★**零改既有闸** (★那 3 道 SW 闸 + `check_demo_panel_spec` / `timing_check` / `check_shutdown_semantics` / `check_pcb_nets` / `gate_check` / `merge` / `frag_write` / `check_sch_erc` / `check_sch_pinfull` 一字不改★) · ★**零改既有页面正文** (★`SW/SW_MD5_BASELINE_LEDGER.md` 那 13 处是 R6/R7 的判决源·一个字都不许动★) · ★**零改 `state/` 下的 `board_md5_pinned_gates.json` / `.md`** (★main 的域·只给「刷新后应有的内容」并登记 need★) · ★**零挂链** (★你新建的闸不许挂 `state/gate_check.py`★) · ★**只写自己的分片 `state/fragments/sw.yaml` (只走 `state/frag_write.py`·写前写后各记一次 md5·期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」·不许静默覆盖★)** · ★**沙盒只落 `tmp/iss372/` + `logs/iss372/`** · ★**不代老板拍板** · ★**零外发** (★老板 2026-11-11 19:31 + 11-12 02:02⇒ 全靠自己查资料·查不到写降级方案·不许写「等原厂回信」★) · ★**不自签 `state/issue_log.yaml`** ★

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 SW/tools/check_sw_board_md5_rebase_readiness.py
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest
python3 state/merge.py          # rc=0
python3 state/gate_check.py      # rc=0 · Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```
★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「上一趟 21:30 failed + 本趟从已落扫描续做」** ★
★**收工后回卷**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (★逐条写清「要谁回答什么」★)★ ★
