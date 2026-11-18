【ISS-328 · hw-lead · ★★cont1 续做 (★上一趟 17:0x~17:2x 中途断线·★成果已在盘上·★不要重跑已完成的部分★)★★】

★**★本单 = 续做, 不是从零重做★** ⇒ ★**开工第一件事: 读下面 §A「已在盘上的成果」, 直接从 §B「还差什么」接上★ ★**

---

## ★A · 已在盘上的成果 (★17:0x~17:2x 那一趟跑出来的·★全部不许重跑★)★

★**① 【第 ② 件 TP no-op 复测 = 已答完, 有确定结论】★★**
- ★**证据**: `logs/iss328/06_tp_noop_placement_diff.txt` + `logs/iss328/07_probe_placement.log` ★
- ★**[实测] 结论**: ★**「钉 10 条 `TP_DSI_*`」vs「不钉」在【排版阶段】全板封装落位【不一样】 ⇒ 差异行数 = 16** (逐条明细: `TP_DSI_D0_P` / `TP_DSI_D1_N` / `TP_DSI_D1_P` / `TP_DSI_D2_N` / `TP_DSI_D2_P` / `TP_DSI_D3_N` / `TP_DSI_D3_P` / `TP_ID` 共 8 个 ref 各挪了位) ★
- ★**⇒ ⇒ 显式钉 `TP_DSI_*` 在【排版阶段】不是 no-op ⇒ ⇒ main 的 P-1「§3-S6 那条 20 条 `PCB_PART_POS` 串删回 10 条」= ★**维持「一条都不许删」** ★** (★依据已从「演练链 no-op」升级为「排版阶段实测 diff=16」★) ⇒ ★**这一件的结论你已经拿到了, 本单只要把它写进交付页 §4 + 交卷页 B1, 不许重跑那两条排版臂★ ★**
- ★**另一条同批实测 (★也在 `logs/iss328/04_official_chain_fp_pos_diff.txt`★)**: ★**官方链补丁链 (combo margin 0.20 + loose margin 0.0625 两步共补 1070 段铜) 全板 186 个封装落位【逐个完全没动】(差异行数 = 0)** ⇒ ★**⇒ no-op 这个问题发生在【排版阶段】, 与补丁链无关 ⇒ ★**官方链同配方这一问已经答完** ★ ★**

★**② 【第 ① 件的硬前置 = 已过 (对照有效性自检通过)】★★**
- ★**证据**: `tmp/iss328/diff1_ru_vs_base.tsv` (★全板 185 封装 `ref/x/y/rot` 逐行比★) ⇒ ★**右上臂 vs 基线臂 落位差异行数 = 102 ⇒ ≠ 0 ⇒ 对照【有效】★★
- ★**基线臂 = `state/iss325_s8_control_v76mz_arms.sh` (ISS-325 同日同代码对照臂, 已在盘) ⇒ ★**只许拿它比, 禁止拿官方板比 (那是另一条产线·老教训) ★ ★**

★**③ 【三块排版阶段板 + 坐标 + 脚本都在盘】★★**
| ★件★ | ★路径★ | ★说明★ |
|---|---|---|
| ★右上臂坐标串★ | `logs/iss328/05_RU_PCB_PART_POS.txt` (★机器读自官方板·零手抄★) + `logs/iss328/05b_ru_partpos_provenance.txt` (★出处逐条登记★) | ★10 条 `R_SEL_*` @ 右上 x78.90..122.30 y5.50 (★帧 = `B160x100`·照 ISS-274★) ★ |
| ★排版阶段三块板★ | `tmp/iss328/bare_base.kicad_pcb` / `bare_ru.kicad_pcb` / `bare_rutp.kicad_pcb` (★各带 `.gen.log` + `.report.txt`·★三块判定都是「板子与网表 100% 一致」★) | ★★**不许重跑**★★ |
| ★臂脚本★ | `tmp/iss328/run_ru_arm.sh` (★后台长跑版·只写 `tmp/iss328/`★) · `tmp/iss328/iss328_s8_rightupper_arms.sh` (★前台版★) | ★★**先读它们, 不要重写★**★ |
| ★落位探针★ | `tmp/iss328/probe_placement.sh` + `tmp/iss328/dump_fp_pos.py` + `tmp/iss328/build_ru_partpos.py` | ★★**已经用过了, 只在需要复核时再跑★**★ |
| ★官方板坐标实测★ | `logs/iss328/01_official_RSEL_TP_pos.tsv` + `02_official_s1_all_fp_pos.txt` + `03_official_final_all_fp_pos.txt` | ★**只读**★ |

---

## ★B · 还差什么 (★本单真正要干的活·★就这三件★)★★

### ★B-1 · 起链跑右上臂, 收链终读数 (★唯一一件重活★) ★
★**做法**: ★**直接用 `tmp/iss328/run_ru_arm.sh` (★它已经处理好路径改写 ⇒ 链/clrfix/对照脚本全部只写 `tmp/iss328/`★) ⇒ ★**后台 nohup 起 (★链 + clrfix 迭代很慢·别在前台等★) ⇒ 边跑边落骨架 (★见 ★B-3 的纪律★) ⇒ 跑完收割读数★ ★**

★**逐条要贴的读数 (★照抄 ISS-325 的读数口径·★不许自创口径★)**:
1. ★**裸板** (排版阶段) DRC viol 数 + unc 条数 + unc 网名集合 ★
2. ★**链终板** DRC viol 数 + unc 条数 + unc 网名集合 ★
3. ★**全板 185 封装落位 diff** (右上臂 vs ★**基线臂同链终板**★ ⇒ ★**禁拿官方板比★) ★
4. ★**链终几何**: 走线段数 / 过孔数 / 铜皮区数 (★`state/cmp_pcb_geom.py` 的口径★) ★
5. ★**段内 P/N 顺序翻转数** (★ISS-325 的口径: 分母 47★) ★
6. ★**名单制闸 rc** (★`state/compare_arm_official.py` / `state/compare_arm_baseline.sh` 那套: 退铜名单 + 差分死腿 + 逐网孤岛★) ★

★**判据 (★照抄, 不许自创★)**:
- ★**成功 = 名单制闸 rc=0 (退铜名单空 + 差分死腿空 + 逐网孤岛空) + DRC viol = 0** ★
- ★★**禁止拿「unc 条数变少」当成功** (★老教训: unc 变少 ≠ 板更好·best23 板 unc 最低但名单制闸 REJECT·见 MEMORY 铁律★) ★★
- ★**「右上臂也是 REJECT」本身就是有价值的读数 ⇒ ★**失败也要交卷, 不许硬凑★ ★**

### ★B-2 · 写两页交付物 (★主交付页 + 交卷页·★结构照 ISS-325 的那一对·★别自创章节★) ★
| ★#★ | ★路径★ | ★要求★ |
|---|---|---|
| 1 | ★**`HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md`** (★新建★) | ★§0 口径与边界自证 + §1 唯一变量与落位自检 (★含 diff=102 这条硬前置★) + §2 读数表 (★B-1 那 6 条·裸板/链终分开列★) + §3 名单制闸判决 + §4 TP no-op 复测 (★含 §A-① 的结论与 diff=16 明细★) + §5 给 main 的结论 (★含「P-1 维持 20 条一条不删」★) + §6 证据分级 + §7 文件清单 ★ |
| 2 | ★**`HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md`** (★新建·★中文名照 ISS-325 的交卷页命名法★) | ★**B0~B6 齐全** (★B1 结论摘要 / B2 验收标准自评·逐条「通过/不通过/未验」/ B3 证据分级·带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 标签 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令·原样贴输出★) ⇒ ★**不许留「(施工中)」占位符** ★ |

### ★B-3 · 写分片 + 交卷前自证 (★纪律★) ★
- ★**分片**: ★**必须走 `python3 state/frag_write.py --agent hw-lead`** (★禁止 `open(p,"w")`★) ⇒ ★写 3 条 artifact (`logs/iss328/` 目录 / 交付页 / 交卷页) + 若干 need/claim ★
- ★★★**先落骨架, 再干活** (★★今天血买来的纪律: ★**ISS-326 连挂两趟都死在「超长 write」上·★开工 1 分钟内先把交付页骨架 + 交卷页骨架 + 分片落盘, 后面只做 edit 增量★**★) ⇒ ★**一次 write 不超过 ~6000 字·分块 edit 补★★
- ★★**沙盒纪律**: ★**沙盒里凡要【写】的文件一律真拷贝; 写前 `assert not os.path.islink(path)`** (★sw-lead 11-18 14:39 因为软链写穿过一次真件★) ★
- ★**交卷前必跑 (原样输出贴进交卷页 B6)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0
python3 state/issue_check.py   # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md "HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md"   # 必须 0 0
grep -c "iss328" state/fragments/hw.yaml   # 必须 >= 1
find tmp/iss328 -type l | wc -l   # 必须 0
```

---

## ★C · 边界 (★违反就是不合格★) ★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** ★(★官方板只许在「板那一趟」改一次·本单是沙盒预演·G1 仍开★) ★
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动★) · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_*.py` / `state/check_*.py` 一个字不许改★) · ★**零改生成器代码** (★`state/gen_*.py` 只读★) · ★**零改既有文档正文** (★本单只许新建上面那两页; ★`HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 附录 R / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` 只读★) ★
- ★**沙盒只写 `tmp/iss328/` + `logs/iss328/`** · ★**只写 `state/fragments/hw.yaml`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ ★**没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
- ★**不许跑 `state/gen_production_pack.sh`** (★会重出投产包·本单不需要★) · ★**不许写 `HW/PCB/PCB_NETLIST_FILL.txt`** (★臂脚本已把 `PCB_REPORT` 指向 `tmp/iss328/`★)

---

## ★D · 一句话 (★本单到底在回答什么★) ★
★**G7 取证的唯一前提 = 「右上臂」这条处方到底有没有用 ⇒ 本单给它第一条【真能构成对照】的读数 ⇒ ★**无论 REJECT 还是 ACCEPT, 都是 boss 要的那一条读数★ ★**
