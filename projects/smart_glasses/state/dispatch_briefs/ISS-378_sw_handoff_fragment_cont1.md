# ISS-378 · sw-lead · ★★cont1 收尾: 只补交卷页 + 分片 ★★ (★两件重产物已在盘·★main 已独立复跑过那道闸·★6 分钟的活★)

★**你的活只剩两件 (★★别重跑任何扫描·★别重建页·★别重建闸★★)** ★

★**★已在盘 (直接用, 零改动·★main 已独立验过★)**:
① `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (55,076 B @11-24 02:45) ⇒ **一个字都不许改**
② `SW/tools/check_debug_header_fw_impact.py` (37,515 B @11-24 02:45) ⇒ ★**main 已独立复跑: 裸跑 rc=0 (W0~W8 九条全绿·含 W7 板三项指纹 + W8 零挂链) + `--selftest` rc=0 (14/14 反向用例全过·末行 ALL TESTS PASS) ⇒ 这道闸是好的, 别碰它** ★
③ `logs/iss378/` 3 份闸日志 + `logs/iss378_official_facts_check.log` ⇒ 直接引用, 别重跑

★**你要做的两件 ★**:
1. ★**交卷页**: ★**新建** `HANDOFF/2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md` ⇒ ★**B1~B6 六段齐全, 且【六个 `##` 标题必须含 gate_check 要的关键词】(★这是上一批单踩过的坑·★一次写对·★别交完再被挑★)★ ★
   - `## B1 结论摘要` (★含「结论」★) · `## B2 验收标准自评` (★含「验收标准自评 / 自评 / 验收标准」★) · `## B3 证据分级` (★含「证据分级 / 证据等级 / 证据」★) · `## B4 接口取值声明` (★含「接口取值 / 接口声明 / interface_claims」★) · `## B5 未决项与卡点` (★含「阻塞 / 卡点 / 未决 / 待办」★) · `## B6 自证复现命令` (★含「复现 / 复现命令 / 自证」★)
   ★**★gate_check 的判据是「全文标题里出现该关键词即可」⇒ 标题里带上关键词即可, 正文不用改★** ★
   ★**内容照抄你已落的那份清单页的事实与代价 (★逐网 19 行表 + 三条救砖链 + JTAG_TDI 三条路线代价 + SoC/SoM 两侧 JTAG 自查证★)·★不代拍** ★
   ★**★§B5 必须写明: 「上一趟 cont1 被 16 分钟墙掐死 (★主产物已在盘★)⇒ 本趟只补交卷页与分片」★** ★
2. ★**分片登记**: `state/fragments/sw.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent sw-lead` (★禁止 `open(p,"w")`★)·写前写后各记一次 md5·★期间若被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」·不许静默覆盖★** ★

★**交卷前必跑 (★原样输出贴进交卷页 B6·★你不用重跑扫描·但这四条必跑★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 SW/tools/check_debug_header_fw_impact.py
python3 SW/tools/check_debug_header_fw_impact.py --selftest
python3 state/merge.py          # rc=0
python3 state/gate_check.py      # rc=0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
```
★**★时间提醒 (★16 分钟墙·★上一趟就是被它掐死的★)**: ★**先写交卷页 (占大头) ⇒ 再写分片 ⇒ 最后贴 rc ⇒ 三步做完就收工·别加戏·别重跑扫描·别重建页/闸★** ★
★**边界 (★一条不许越·★与上一趟相同★)**: ★**零写板** (md5 / mtime / size 三项不变) · 零落表 (★网表/脚表/BOM/落表台账/原理图 11 个/`issue_log.yaml` 一字不改★) · 零改既有闸 (★那 3 道 SW 闸 + `check_demo_panel_spec`/`timing_check`/`check_shutdown_semantics`/`check_pcb_nets`/`gate_check`/`merge`/`frag_write`/`check_sch_erc`/`check_sch_pinfull` 一字不改★) · 零改既有页面正文 (★`SW/SW_MD5_BASELINE_LEDGER.md` 那 13 处是 R6/R7 的判决源·一个字都不许动★) · ★**零挂链** (★不许挂 `state/gate_check.py`★) · 零外发 · 不代老板拍板 · 不自签 `state/issue_log.yaml` ★
★**收工后回卷**: ★交卷摘要 + 必跑命令的 rc + 两件交付物路径 + 边界自证 + 要 main 裁的事 (★逐条写清「要谁回答什么」★) ★
