【ISS-328 · hw-lead · ★★收卷单 (cont3) · ★★只做【收割 + 填实】· 一个字节都不许重新生成★★】

★**派活人**: 项目总工 (main / cron `fb67af40` · 2026-11-18 21:5x)
★**性质**: ★**内部活 · PCB 线 · 纯收割 / 填实类 (HW 侧)** ★ · ★**零写板 · 零重跑链 · 零落表 · 零改闸 · 零改生成器代码** ★ · 只读沙盒产物 + 只写【交付页 + 交卷页 + 自己的分片】 · ★**零外发** ★ · 不替老板拍板 · 不自签 `state/issue_log.yaml`
★**任务书全文 (前两趟 · 仍然有效)**: `state/dispatch_briefs/ISS-328_hw_rightupper_control_arm_cont1.md` (9,257 B · 起链那趟) · `state/dispatch_briefs/ISS-328_hw_rightupper_control_arm_cont2.md` (7,885 B)

---

## ★★★【① 为什么派这一条 (★21:5x 本机实跑读数·不抄任何 agent 报告★)★★★

| ★项★ | ★21:5x 本机实跑★ | ★判★ |
|---|---|---|
| ★后台链★ | ★**`logs/iss328/08_rightupper_arm.log` L209 = 「=== ISS-328 S8 右上臂 全流程结束 2026-11-18 21:37:23 ===」★** · ★**21:5x `ps` 实读: 无 `state/gen_pcb_netlist_board.py` / 无 `compare_arm_official` 进程 ⇒ 全退** ★ | ★**链已停 ⇒ 上一轮那条「链没停就不许碰」的约束已解除 ⇒ 现在重派安全** ★ |
| ★链的读数★ | ★**全在盘** ★: `logs/iss328/08_rightupper_arm.log` (209 行) + `logs/iss328/06_tp_noop_placement_diff.txt` + `logs/iss328/07_probe_placement.log` + `tmp/iss328/` 沙盒产物 | ★**读数够用·一个数都不用重跑** ★ |
| ★在盘但没填 ①★ | ★**`HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` (14,973 B · 19:41:44) ⇒ 12 处占位符还在** ★: ★L113 `<!-- SEC2_READINGS -->` · L117 `<!-- SEC2_BARE_VS_CHAIN -->` · L121 `<!-- SEC2_FP_DIFF -->` · L125 `<!-- SEC2_GEOM -->` · L129 `<!-- SEC2_PN -->` · L142 `<!-- SEC3_OFFICIAL -->` · L146 `<!-- SEC3_BASELINE -->` · L150 `<!-- SEC3_VERDICT -->` · L224 `<!-- SEC5_CONCLUSION -->` · L236 `<!-- SEC6_EVIDENCE -->` · L240 `<!-- SEC6_INTEGRITY -->` · L246 `<!-- SEC7_FILES -->` ★ | ★**缺** ★ |
| ★在盘但没填 ②★ | ★**`HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` (3,667 B · 19:32:30) ⇒ 7 处占位符还在** ★: ★L14 `<!-- B0_ONE -->` · L31 `<!-- B1_SUMMARY -->` · L37 `<!-- B2_ACCEPTANCE -->` · L43 `<!-- B3_EVIDENCE -->` · L49 `<!-- B4_INTERFACE -->` · L55 `<!-- B5_OPEN -->` · L61 `<!-- B6_REPRO -->` ★ | ★**缺** ★ |
| ★分片★ | ★`grep -c iss328 state/fragments/hw.yaml` = 8 处 (status/artifacts/needs_from/interface_claims 都在) ★ ★**但 status 段还停在 cont1 的中途口径 (还没写名单制闸判决)** ★ | ★**要更新 status + 补判决 need** ★ |
| ★板面★ | ★**零变化**: `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` (★21:5x main 实读★) ★ | ★**不许动** ★ |

★**★⇒ 所以这一趟 = 【收割 + 填实】· 不是再跑一遍★**: ★**链已经跑完了 (21:37:23) · 读数已经落在盘上了 · 只差把 19 处占位符填成真读数** ★

---

## ★★★【② ★★这一趟只干三件 (★不许重跑链·不许重跑任何板·不许新造数★)★★】★★★

### ★★★【第 ① 件: 填交付页 12 处占位符 (★`HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md`★)】★★★

| ★占位符★ | ★必须写什么★ | ★读数从哪来 (★行号是锚点·自己去读原文★)★ |
|---|---|---|
| ★`SEC2_READINGS` (L113)★ | ★**§2-1 读数总表 (★6 条·机器生成·零手抄★)** ★ | ★`logs/iss328/08_rightupper_arm.log` 的名单制闸表 (L60~L90 附近) ★ |
| ★`SEC2_BARE_VS_CHAIN` (L117)★ | ★**裸板 (排版阶段) vs 链终板 两级都要列 (★不许只列一级★)** ★ | ★同日志 L15~L40 (裸板 违规=11 · unc=35 · 段数 3471 → 链终段数 3986 · unc 28/29) ★ |
| ★`SEC2_FP_DIFF` (L121)★ | ★**全板 185 封装落位 diff = 102 (★≠0 ⇒ 对照有效·这与 ISS-325 的 diff=0 白跑正好相反★)** ★ | ★`logs/iss328/07_probe_placement.log` L30 「★差异行数 = 102」 + `logs/iss328/06_tp_noop_placement_diff.txt` 末段附注 ★ |
| ★`SEC2_GEOM` (L125)★ | ★**链终几何 (★`state/cmp_pcb_geom.py` 口径★)** ★ | ★日志里的几何差异定位块 (★只有【仅B】的几条就是它的输出·★照抄·不许自己重跑★) ★ |
| ★`SEC2_PN` (L129)★ | ★**段内 P/N 顺序翻转 (★ISS-325 口径·分母 47★)** ★ | ★日志对应块 ★ |
| ★`SEC3_OFFICIAL` (L142)★ | ★**右上臂 vs 官方板 的名单制闸全表 + 判定** ★ | ★日志 L60~L95 (第一块 判定: REJECT) ★ |
| ★`SEC3_BASELINE` (L146)★ | ★**右上臂 vs ★基线臂同链终板★ 的臂间对照闸** ★ | ★日志第二/第三块 (L191 判定: REJECT · L198 闸 rc=1) ★ |
| ★`SEC3_VERDICT` (L150)★ | ★**判决 = 通过 / 不通过 · ★不许软着陆★** ★ | ★★**main 21:5x 实读: 三个名单制闸块全是 REJECT ⇒ 判决 = 不通过 (REJECT)★** ★ |
| ★`SEC5_CONCLUSION` (L224)★ | ★**给 main 的结论 (★这一单要回答的那一問★)** ★ | ★见下面 ④ 三条口径 ★ |
| ★`SEC6_EVIDENCE` (L236)★ | ★**本单证据清单 (★每条带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 标签·★照 §6-1 四档口径★)** ★ | ★`logs/iss328/` 全清单 + `tmp/iss328/` 沙盒产物 ★ |
| ★`SEC6_INTEGRITY` (L240)★ | ★**零写板双证 + 零改闸/零改生成器/零改既有文档 体检表** ★ | ★日志里跑前/跑后两行 md5 + mtime (★611b869e13518c3c023fb178f91a0075 · 2026-11-06 07:07:17.362193413★) + 工具指纹 sha256 (★L11~L13★) ★ |
| ★`SEC7_FILES` (L246)★ | ★**文件清单 (★路径逐字等于磁盘★)** ★ | ★`logs/iss328/` 15 件 + `tmp/iss328/` 沙盒 + 两份文档 + 分片 ★ |

### ★★★【第 ② 件: 填交卷页 7 处占位符 (★`HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md`★)】★★★
★**B0 一句话结论 / B1 结论摘要 / B2 验收标准自评 (★逐条 通过 / 不通过 / 未验★) / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 (★原样贴输出★)** ★
★**★B4 至少要逐字给出这三条「别人要照抄的东西」★**: ★**① 右上臂的 10 条 `R_SEL_*` `PCB_PART_POS` 串 (★机器读自官方板·零手抄★)★** ★**② 「显式钉 `TP_DSI_*` 在【排版阶段】是不是 no-op」这一问的【确定答案 + 适用配方】★** ★**③ 名单制闸的三块判决 (臂 vs 官方 / clrfix 臂 vs 官方 / 臂 vs 基线臂) 各自 rc★**
★**★B5 必须写清 (★main 21:5x 实读·你不代拍·只交事实与建议★)★**: ★**① 判决 REJECT ⇒ 「挪器件位置」这条处方已被 ISS-325 左上臂 + ISS-328 右上臂【两个臂】证伪** ★ · ★**② 段数 3986 vs 官方终板 18092 ⇒ 路由器代码已漂移 ⇒ 【同工艺才可比】⇒ 「unc 45→29」在追平段数之前一律不算数** ★ · ★**③ TP no-op 这条结论与 ISS-325 的结论【正好相反】⇒ 适用范围必须标「在哪个配方下测的」★** ★

### ★★★【第 ③ 件: 分片 (★必须走 `state/frag_write.py`·★禁 `open(p,"w")`★)】★★★】
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent hw-lead --show      # ★先看自己现有分片长什么样★
python3 state/frag_write.py --agent hw-lead --add-artifact 'path=HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md summary="ISS-328 右上对照臂交付页 (★§0~§7·19 处占位符已填实★)" kind=doc' --add-artifact 'path=HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md summary="ISS-328 交卷页 B0~B6 齐全"' --status 'phase=done progress_pct=100 health=green summary="ISS-328 右上对照臂: 判决 REJECT (名单制闸) ⇒ 挪器件位置这条处方被 ISS-325/ISS-328 两个臂证伪; 段数 3986 vs 官方 18092 ⇒ 同工艺才可比 ⇒ unc 45→29 不算数"'
```
★**★写完必须复核**: ★`grep -c "iss328" state/fragments/hw.yaml` 必须 ≥ 1 ★ · ★**另: 把「名单制闸判决」这条 need 的 key 写清楚 (★别与 `iss328_ru_arm_gate_verdict` 重复加同 key·★用 `frag_write.py` 的更新语义·★不要自己造重复 key★)** ★

---

## ★★★【③ ★★读数从哪来 (★逐条给行号锚点·一个数都不许重跑★)★★】★★★

★**主证据文件: `logs/iss328/08_rightupper_arm.log` (209 行) ★**

| ★行号★ | ★内容★ |
|---|---|
| ★L11~L13★ | ★工具指纹 sha256 (`gen_pcb_routing.py` / `gen_pcb_netlist_board.py` / `replay_patch_chain.sh`) ⇒ 零改生成器代码的自证 ★ |
| ★L14~L16★ | ★右上臂 `PCB_PART_POS` 串 (★机器读·零手抄★) ★ |
| ★L17★ | ★路由产物 md5 `f499787f720637babb874d6e367d750f` · 段数 = 3471 ★ |
| ★L20~L38★ | ★链各级段数与自检闸读数 (3471 → 3847 → 3986) · 终板 unc 29 / 违规 12 ★ |
| ★L32★ | ★**「段数 = 3986 (★官方终板 = 18092 ⇒ 不等于就不算数)」** ★ |
| ★L41~L45★ | ★★★**自校准闸 档②: 官方链的 stage-1 产物是 17022 段, 当前路由器只出 3471 段 ⇒ 路由器代码已漂移 ⇒ 两臂不同工艺 ⇒ 链跑完但产物不能与官方板直接比** ★ ★★**这条是本单最值钱的一条·必须原样进 B1/B5★** ★ |
| ★L60~L95★ | ★名单制闸 第一块 (链终板 vs 官方板) 的全表 + 退铜名单 + 孤岛名单 + **L91 判定: REJECT** ★ |
| ★L96~L130★ | ★名单制闸 第二块 (clrfix 终板 vs 官方板) 的全表 + **L122 判定: REJECT** ★ |
| ★L131~L199★ | ★臂间对照闸 (候选 vs 基线臂同链终板) 的全表 + **L191 判定: REJECT** + **L198 闸 rc=1** ★ |
| ★L200~L207★ | ★几何差异定位 (★仅B 的那几条★) + **L205 「两板【不等价】⇒ 复现未成功 ⇒ 别拿去跟官方板比」** + L206 对照闸 rc=0 ★ |
| ★L208~L209★ | ★真板 md5 / mtime (跑后) + 「全流程结束 2026-11-18 21:37:23」 ★ |

★**旁证文件 (★只读·不许改·不许重跑★)**:
- ★`logs/iss328/06_tp_noop_placement_diff.txt` ⇒ ★**TP 显式钉 vs 不钉 (排版阶段) 落位差异行数 = 16 ⇒ 显式钉 `TP_DSI_*` 【不是】 no-op ⇒ P-1 的 20 条串一条不许删回 10 条** ★ + 末段附注「起链硬前置 (右上臂 vs 基线臂 全板封装落位 diff) = 102 (必须 ≠ 0)」 ★
- ★`logs/iss328/07_probe_placement.log` L30 ⇒ 「★差异行数 = 102」 ★
- ★`logs/iss328/05_RU_PCB_PART_POS.txt` + `logs/iss328/05b_ru_partpos_provenance.txt` ⇒ 右上臂 10 条 `R_SEL_*` 坐标 + 出处登记 ★
- ★`logs/iss328/01_official_RSEL_TP_pos.tsv` / `01_official_RSEL_TP_pos.tsv.partpos.txt` / `02_official_s1_all_fp_pos.txt` / `03_official_final_all_fp_pos.txt` / `04_official_chain_fp_pos_diff.txt` ⇒ 官方板侧读数 (★官方链补丁链不动封装落位 ⇒ diff = 0★) ★
- ★`logs/iss328/31_md5_pre.txt` (19:33) · `logs/iss328/32_gen_products_md5_pre.txt` (19:35) · `logs/iss328/32b_gen_products_mtime_pre.txt` (19:35) ⇒ 跑前指纹 ★
- ★沙盒产物 (★只读): ★`tmp/iss328/chain_iss328_s8ru/final_chain.kicad_pcb` (链终板) + `tmp/iss328/chain_iss328_s8ru/final_board.drc.json` (它的 fresh DRC) + `tmp/iss328/_clrfix_iss328_s8ru_final.kicad_pcb` (clrfix 终板, DRC=0) + `tmp/iss328/_clrfix_iss328_s8ru_final.kicad_pcb.drc.json` + `tmp/iss328/ru_R.gen.log` (链凭据) + `tmp/iss328/diff1_ru_vs_base.tsv` + `tmp/iss328/diff2_tp_vs_notp.tsv` + `tmp/iss328/pos_ru.tsv` / `pos_base.tsv` / `pos_rutp.tsv` ★

★**★★可选复算 (★【可做可不做】·★日志里三块判决表已经全打印了 ⇒ ★默认直接照抄日志★)★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/compare_arm_official.py --help          # ★先看参数形态★
python3 state/compare_arm_official.py tmp/iss328/chain_iss328_s8ru/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
python3 state/compare_arm_official.py tmp/iss328/_clrfix_iss328_s8ru_final.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
```
★**★硬约束 (★防止这一趟又被拖死★)★**: ★**最多跑这两条 + 一次 `--help`·★不许跑第四次** ★ · ★**★官方板那一侧的 DRC json 盘上没有 (★`tmp/iss328/` 里只有链终板 / clrfix 终板两份 DRC json·★`find tmp/iss328 -name '*official*'` = 0 件★)⇒ 若脚本要它 ⇒ ★**不许去生成 (★生成 DRC 要跑 kicad·慢·★还会往沙盒写新文件⇒违反「只读沙盒」★)⇒ 直接照抄日志里那三块表格 (★日志已经把候选板 + 官方板两列全打印了)★** ★ · ★**复算结果与日志不一致 ⇒ 照日志写 + 在 B5 登记差异 (★不许私自改判据★)★** ★ · ★**不许跑 `state/gen_pcb_netlist_board.py` / `state/replay_patch_chain.sh` / `state/clrfix_iter.sh` / `tmp/iss328/run_ru_arm.sh`·★那四条是【重跑链】★**

---

## ★★★【④ 边界 (★违反就是不合格★)★★★】★★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** (★main 21:5x 实测过·★变了一律不合格★) ★
- ★★**零重跑链** (★本单最要紧的一条★): ★**不许跑 `state/gen_pcb_netlist_board.py` · `state/replay_patch_chain.sh` · `state/clrfix_iter.sh` · `tmp/iss328/run_ru_arm.sh` · 不许重新生成任何板 · 不许重新排版·不许重新布线·不许重新清 DRC★** ⇒ ★**读数全部从 `logs/iss328/` + `tmp/iss328/` 引** ★
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动·★也不许自己签 `state/issue_log.yaml`★)
- ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_official.py` / `state/check_pcb_drc.py` / `state/cmp_pcb_geom.py` / `state/cmp_unc_sets.py` 一律只读★) · ★**零改生成器代码** (★`state/gen_pcb_netlist_board.py` / `state/gen_pcb_routing.py` / `state/gen_kicad_project.py` / `state/clrfix_iter.sh` / `state/replay_patch_chain.sh`★) · ★**零改既有文档正文** (★含 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` (★那是 ISS-325 的交付页★) · `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` · `HW/PCB/LAYOUT_FIX_SPEC.md`★) · ★**零改 `state/fragments/sw.yaml` / `state/fragments/mech.yaml`** ★
- ★**只写**: ★`HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` (占位符) · `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` (占位符) · `state/fragments/hw.yaml` (分片) · `logs/iss328/` (★可新增收割件·★不许覆盖已有 15 件原始证据·★新文件名必须带新后缀★) ★
- ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★只给选项 + 代价 + 建议★) · ★**不自签 `state/issue_log.yaml`** ★
- ★★**文档纪律 (★别踩 SW 侧那类坑★)★★**: ★**凡在文档里写「形状像位号但盘上不存在」的 token ⇒ 要么打断 token 正则, 要么写进 `logs/iss328/` 不进 `HW/PCB/`·★SW 侧 ISS-327 就栽在这上面 (★11 份真件文档被改成假位号·闸当场判成新增真隐患⇒全项目门禁变红·★本单别学它★)★** ★
- ★★**抗上下文护栏 (★这一趟活不多·别展开·★上一轮就死在【把链当自己的活重跑】上★)★★**: ★**不许通读交付页全文再贴回对话 ⇒ 用 `grep -n` 定位 ★ · ★**单次 write ≤ 3000 字 ⇒ 先写骨架再 `edit` 逐块补** ★ · ★**不许重跑已在盘的复现 (★除非上面那两条【可选复算】·★最多两次★)** ★ · ★**回复控制在 ~800 字以内** ★

---

## ★★★【⑤ 交卷前必跑 (★原样输出贴进交卷页 B6·★期望值写在后面★·★gate_check 慢·★只跑一次·★加 timeout★)★★★】★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py    ; echo "MERGE_RC=$?"     # ★rc 必须 0
timeout 900 python3 state/gate_check.py ; echo "GATE_RC=$?"   # ★rc 必须 0
timeout 600 python3 state/issue_check.py ; echo "ISSUE_RC=$?"  # ★rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb   # ★必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # ★必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md"   # ★必须 0
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md"   # ★必须 0
grep -c "<!-- " "HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md"   # ★必须 0 (★标准占位符扫描查不到 <!-- --> 这种·必须单独查★)
grep -c "<!-- " "HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md"   # ★必须 0
grep -c iss328 state/fragments/hw.yaml   # ★必须 ≥ 1
```
★**★`grep -c "<!-- "` 那两条是本单的核心验收项 (★19 处占位符一个都不许剩★)★**

★**★交卷前必跑的最后一句 (★原样贴进回复·★不许省略★)★**:
```bash
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
```
★**★三条都 rc=0 才算交卷合格·★任何一条红 ⇒ 先查是谁的产物 (★Q1/Q7 的缺口清单里有归属·★不许越界改别人的页·★写进 B5 交 main 拍★)★**

---

## ★★★【⑥ ★★三条必须让 main 知道的 (★main 21:5x 实跑读数·你照抄进 B1/B5·★你不代拍★)★★】★★★

1. ★★**判决 = REJECT (名单制闸) ⇒ 「挪器件位置」这条处方已被【两个臂】证伪** ★★ ⇒ ★**ISS-325 左上臂: 退铜 4 + 差分死腿 1 对 + 逐网孤岛 +9 ⇒ REJECT** ★ ★**ISS-328 右上臂: 净救回 -1 + 差分死腿 3 对 + 逐网孤岛变多 ⇒ REJECT** ★ ⇒ ★**⇒ 剩下只有三条路: ① 机制级 (12 个零铜网换机制) ② 老板口径 (W-2 / W-1c / A4 / W-3 / U-1 / P7) ③ 路由器本体** ★
2. ★★**段数 3986 vs 官方终板 18092 ⇒ 路由器代码已漂移 ⇒ 【同工艺才可比】⇒ 「unc 45→29」在追平段数之前一律不算数** ★★ ⇒ ★**这是「unconnected 变少 ≠ 板子更好」的第二层: 第一层 = 名单制 · 第二层 = 同工艺才可比** ★
3. ★★**「钉 `TP_DSI_*` 不是 no-op」这条结论 (排版阶段 差异 16 行) 与 ISS-325 的「是 no-op」正好相反** ★★ ⇒ ★**⇒ 以后凡是 no-op 结论, 必须标「在哪个配方下测的」** ★ ★**⇒ P-1 的 20 条串一条不许删 (★这条已经在 `state/fragments/hw.yaml` 的 `iss328_p1_partpos_20_must_keep` 里登记·★本单不许改它★)★**
