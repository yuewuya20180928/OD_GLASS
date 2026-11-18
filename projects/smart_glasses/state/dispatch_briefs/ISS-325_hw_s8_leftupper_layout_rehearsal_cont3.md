# ISS-325 · hw-lead · ★★【cont3 续做 · 收尾】★★

> ★**第三次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 15:2x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main · ★**单号**: ISS-325 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · PCB 线 · 纯沙盒预演 / 作业包 / 判据设计类 (HW 侧)** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改生成器代码** ★

---

## ★★★【★★上一趟 (15:0x) 已经做完了什么 · 这一趟只补什么 ★★★】★★★

★**★上一趟 (cont2) 干成了很多, 但会话在 15:28 被超时掐掉 ⇒ 你的活是从【已完成的位置】继续, 不是从头来★ ★**

★**★main 15:2x 本机实读 (★不抄 agent 报告★) —— 上一趟的成果** ★:

| 项 | ★读数★ | ★**状态** ★ |
|---|---|---|
| ★交付页 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` ★ | ★**60,381 B** (★13:24 时是 42,815 B★) · mtime **15:02** ★ | ★**已补 §9** (`grep -c "^## §9"` = **1**) ★ |
| ★★`__XXX__` 占位符★ | ★**0 处** (★`grep -oE "__[A-Z_]+__" \| wc -l` = 0★) ★ | ★**★4 处已全部填掉** ★ |
| ★分片 `state/fragments/hw.yaml` ★ | `iss325` 命中 **25** ★ | ★**已写** ★ |
| ★交卷页 `HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md` ★ | ★**9,135 B · mtime 13:24** (★**没动过**★) ★ | ★**★还是只有 B0 / B3 / B6 三块 ★★** ★ |
| ★`logs/iss325/scripts/gen_sec9.py` ★ | 15,013 B | ★**已写好·§9 就是它生成的** ★ |

★**★★⇒ ⇒ 【这一趟只剩 3 件】★★**:
★**① ★§3-3 的数据格还没填★** (★main 实读: §3-3 下面仍是那句「§3-3 的数据格在本单交卷时由 `logs/iss325/scripts/iss325_measure.sh` 填入」★ ⇒ **这是【一句待办说明】, 不是读数**★) ★
★**② ★交卷页 B1 / B2 / B4 / B5 还没补★** (★mtime 还是 13:24★) ⇒ ★**★这是门禁链 `gate_check.py` 的 Q1 现在还红着的那 3 格★** ★
★**③ ★§2-3 / §3-2 / §6-2 / §7 的「证伪」改写还没落★** (★上一趟 agent 临死前说的最后一句是「Now the core rewrite: §7 (falsification), plus §3-2/§3-3/§6-2/§2-3 corrections」⇒ ★**⇒ 它正要干这件事就被掐了★ ⇒ **这一趟从这儿接着干**★) ★

★**★★⇒ ⇒ 【★所以这一趟的活很少, 你有充足时间跑完所有闸链再交卷★】★★**

---

## ★★① §3-3 的数据格: ★★臂的读数 main 已经实测好了, 你直接抄进交付页并复核一遍★★

★**★main 15:2x 本机实跑的读数 (★★你必须自己 fresh 复测一遍再写进交付页·不许只抄 main 的数字★)★★**:

| 板 | md5 | viol | unc | unc 网名 | 段内翻转 |
|---|---|---|---|---|---|
| ★**左上臂** 裸板 ★`/tmp/iss325_s8lu_R.kicad_pcb` ★ | ★`3bfb30edfd7c64aafb9e908bc9dc0d57` ★ | ★**6** ★ | ★**37** ★ | ★**31** ★ | ★**5 / 47** ★ |
| ★**对照臂** 裸板 ★`/tmp/iss325_s8ctl_R.kicad_pcb` ★ | ★`902ea02ac5f8e10310aa528687eaaad7` ★ | ★**6** ★ | ★**37** ★ | ★**31** ★ | ★**5 / 47** ★ |
| ★**左上臂** 链终 ★`/tmp/chain_iss325_s8lu/final_chain.kicad_pcb` ★ | ★`27b51bd5039a4f4b1d108cc1355b4463` ★ (★3666 段★) | ★**6** ★ (★5 clearance + 1 copper_sliver★) | ★**29** ★ | ★**27** ★ | — |
| ★**对照臂** 链终 ★`/tmp/chain_iss325_s8ctl/final_chain.kicad_pcb` ★ | ★`cc13d3ce5539ab714ee320c8cbb62e6b` ★ | ★**6** ★ (★同上★) | ★**29** ★ | ★**27** ★ | — |
| ★**现役板** (★对照参照·★不是臂★) ★ | ★`611b869e13518c3c023fb178f91a0075` ★ | ★**0** ★ | ★**45** ★ | ★**43** ★ | ★**17 / 47** ★ |
| ★**盘上最好板** `best_unc23_clrfix` (★参照·★不是臂★) ★ | ★`52ccbd207e0796c92426ba7e81863c5a` ★ | ★**0** ★ | ★**23** ★ | ★**21** ★ | ★**5 / 47** ★ |

★**★★复测命令 (★照这些跑, 别自己另发明★)★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
bash logs/iss325/scripts/iss325_measure.sh          # ⇒ 落 logs/iss325/09_threeway_fresh_drc.txt
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8lu_R.kicad_pcb lu
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8ctl_R.kicad_pcb ctl
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py <板> <板.drc.json>
```

---

## ★★② ★★§2-3 / §3-2 / §6-2 / §7 的「证伪」改写 (★本单最值钱的一段·★上一趟没写完★)★★

★**★★main 15:2x 实测出的核心事实 (★你要复核并写进交付页★)★★**:

### ★★②-1 ★★两臂的落位【逐个完全相同】★★
★**main 用 pcbnew 逐个读 `GetPosition()` 实测 (★20 个器件·两臂逐条比对★)**:
★`R_SEL_D3_P`(5.50,3.0) · `R_SEL_D3_N`(7.95,3.0) · `R_SEL_D2_P`(13.10,3.0) · `R_SEL_D2_N`(15.55,3.0) · `R_SEL_CK_P`(20.70,3.0) · `R_SEL_CK_N`(23.15,3.0) · `R_SEL_D1_P`(28.30,3.0) · `R_SEL_D1_N`(30.75,3.0) · `R_SEL_D0_P`(35.90,3.0) · `R_SEL_D0_N`(38.35,3.0) · `TP_DSI_D3_P`(5.50,6.20) · `TP_DSI_D3_N`(7.95,6.20) · `TP_DSI_D2_P`(13.10,6.20) · `TP_DSI_D2_N`(15.55,6.20) · `TP_DSI_CK_P`(20.70,6.20) · `TP_DSI_CK_N`(23.15,6.20) · `TP_DSI_D1_P`(28.30,6.20) · `TP_DSI_D1_N`(30.75,6.20) · `TP_DSI_D0_P`(35.90,6.20) · ★**`TP_DSI_D0_N`(41.55,3.00)** ★
★**★⇒ ⇒ 两臂的【唯一变量】(★显式多钉 10 个 `TP_DSI_*`★) 在【落位结果上完全没有生效】★★**
★**★⇒ ⇒ unc 网名集合【逐条相同】(★main 集合比对: 裸板 31 == 31 · 链终 27 == 27 · 差集两边都为空★) ⇒ ⇒ 「左上臂 vs 同日对照臂」这个比较【没有构成对照】★★ ★

### ★★②-2 ★★机制 (★你要自己复核这段源码★)★★
★**`state/gen_pcb_netlist_board.py` L1057~L1063 的「测试点贴伙伴件」规则**: ★**`TP_DSI_*` 默认就跟着它的伙伴件 `R_SEL_*` 走 ⇒ ★**当 `R_SEL_*` 被钉到左上 (x 5.50..38.35, y 3.00) 时, `TP_DSI_*` 自动就落在同一 x 那一列的 y=6.20** ⇒ ★**⇒ 对照臂 (只钉 10 个 `R_SEL_*`, 不钉 `TP_DSI_*`) 的 `TP_DSI_*` 落位【与】左上臂【自动产生的】落位【完全一致】⇒ ⇒ ★**「显式钉 TP」这条处方【是冗余的】★★ ★
★**★★⇒ ⇒ 本单原来的核心论点「显式钉死 TP_DSI_* ⇒ 能消掉段内交叉」★【被这次实跑证伪了】★★** ⇒ ★**⇒ §7 的结论必须按【实测】重写** ★

### ★★②-3 ★★要改的四处 (★上一趟 agent 自己也点了这四处★)★★
| 位置 | ★**现在写的是什么** ★ | ★**要改成什么** ★ |
|---|---|---|
| ★**§2-3** ★ | ★「`PCB_PART_POS` 的 `TP_DSI_*` 10 条: 对照臂=无 / 左上臂=+10 条 (★这就是唯一变量★)」 ★ | ★**★必须加一句: 【这个「唯一变量」在落位上完全没生效】⇒ 两臂落位逐条相同 ⇒ 【本对照无效】★** ★ |
| ★**§3-2** ★ | ★四方对照表里左上臂/对照臂两行的数字写着 `§3-3` ★ | ★**填上真实读数 (★§①那张表★) + 加一列/一行说明「两臂数值相同」** ★ |
| ★**§3-3** ★ | ★还是那句「由 `iss325_measure.sh` 填入」的待办 ★ | ★**填上真实读数** ★ |
| ★**§6-2** ★ | ★「左上布局把翻转从 17 降到 5」(★那张表量的是【盘上已有的 best23 板 vs 现役板】★) ★ | ★**★必须加限定: 它量的是【best23 板 vs 现役板】, 不是【本单两臂之间的差】⇒ 两者不是一回事, 不许混用★** ★ |
| ★**§7** ★ | ★「左上布局」这条处方【单独】不足以归零 ★ | ★**★核心改写: 【本单两臂【没有有效对照】⇒ 「左上布局」对 unc 的净效应【至今没有任何实测】⇒ 而「显式钉 TP_DSI_*」这条处方【被实跑证伪】(落位没生效)】★★ ⇒ ★**⇒ 归零必须【拆成两问】: ① 布局能不能归零 = 【仍然没有任何实测】★ ② 机制 + 口径一起上能不能归零 = 【不判·留给 G7】★ ★ |

### ★★②-4 ★★★【一条判据警告 (臂自己写的)】★★★ ★
★**`/tmp/chain_iss325_s8lu/final_chain.kicad_pcb.chain.json` 里生成器自己写了**: ★**「★这块板是【官方补丁链的产物】⇒ ★★**不是独立候选臂**; ★★**要当候选臂比, 必须与【同链基线】比 (★`state/compare_arm_baseline.sh`★)」** ★
★**★⇒ ⇒ 「左上臂 vs 官方板」这个比较【本身是错的】★★** ⇒ ★**★`state/compare_arm_baseline.sh` 的文件头白纸黑字写着: 「官方板的 stage-1 是 17022 段 (★历史 promote 累积★), 而当前路由器的产物只有 13407 段 ⇒ ★**两边不在同一条工艺线上 ⇒ 比出来的差异全是【工艺差】不是【臂的优劣】**」⇒ ⇒ **基线必须也用当前路由器跑 + 套同一条已校准的补丁链** ★ ★
★**★★⇒ ⇒ 你必须跑 `bash state/compare_arm_baseline.sh /tmp/chain_iss325_s8lu/final_chain.kicad_pcb` 做同链基线对照, 不许拿 `compare_arm_official.py <臂> <官方板>` 当「臂的功劳」证据★ ★**
★**★⇒ ⇒ 而且本单两臂【连同链基线都没比】(它们互为对照但落位相同⇒ 对照无效) ⇒ ⇒ ★**你必须自己判断: 要么找一个真正同链基线, 要么如实写「本单两臂互为对照但落位相同 ⇒ 【没有有效对照】⇒ 本单只提供【单臂绝对读数】, 不提供【臂间差值】」★★ ★

---

## ★★③ 交卷页补 B1 / B2 / B4 / B5 (★★这是本单最后的大块★)★★

★**★交卷页 mtime 还是 13:24 (★上一趟没碰过★) ⇒ ★**交卷页只有 B0 / B3 / B6 三块, 缺 B1 / B2 / B4 / B5**** ★
★**★这是门禁链 `state/gate_check.py` 的 Q1「6 项必填验收块」★★** ⇒ ★**main 本轮实跑 `gate_check.py --json` ⇒ ★**Q1 = 15/18, 掉的那 3 格就是本单 (hw-lead: 缺 [B2] 验收标准自评 · 缺 [B4] 接口取值声明 · 缺 [B5] 未决项与卡点) ★** ⇒ ⇒ ★**⇒ 本单补完 B1/B2/B4/B5, Q1 就能回到 18/18 ⇒ ★**这条闸现在就在红着等你补, 不是装饰★ ★

| 块 | ★**内容 (★照 `state/gate_check.py` 的 `REQUIRED_BLOCKS` 口径★)** |
|---|---|
| ★**B1** ★ | ★**结论摘要 (★一句话★)** ★ ⇒ ★**一句话必须包含本轮的核心结论: 「两臂落位相同 ⇒ 对照无效 ⇒ 显式钉 TP_DSI_* 被证伪」★★ ★ |
| ★**B2** ★ | ★**验收标准自评 (★逐条「通过 / 不通过 / 未验」★)** ★ —— ★**不许只写一句「全部通过」★** ⇒ ★**每个验收项单独一行 + 判定 + 依据读数★** ★ |
| ★**B3** | ★**证据分级** ★ (★**已有·本轮不用动★**) |
| ★**B4** ★ | ★**接口取值声明 (★`interface_claims`★)** ★ ⇒ ★**照 §4 那几条逐字给 (★网名 / 坐标 / 数值 / 判据来源★)** ★ |
| ★**B5** ★ | ★**未决项与卡点 (★需要谁回答什么★)** ★ ⇒ ★**照 §7-5 逐条列 (★归 main + 老板的 7 条 need·一条不许漏★) ⇒ ★**并加上本轮新发现的两条 (★见 §④★)** ★ |
| ★**B6** | ★**自证复现命令** ★ (★**已有·本轮不用动★**) |

---

## ★★④ ★★交 2 条新 need (★本轮实跑【证伪】出来的, 价值高于任何推算★)★★

| ★**need key** ★ | ★**内容** ★ | ★**建议默认值** ★ |
|---|---|---|
| ★**`iss325_s8_tp_pin_noop_proven`** ★ | ★**「显式钉死 `TP_DSI_*`」这条处方【被证伪】: 生成器 L1057~L1063 的「TP 贴伙伴件」规则让 `TP_DSI_*` 自动跟着 `R_SEL_*` 走 ⇒ 对照臂 (不钉 TP) 与左上臂 (钉 TP) 的 20 个器件落位【逐个完全相同】⇒ unc 网名集合也逐条相同 (裸板 31==31 / 链终 27==27) ⇒ ★**该处方对 unc 无净效应**★** ⇒ **ISS-322 §3-8 里「只钉 R_SEL 不钉 TP 等于给路由器埋雷」这个判断, 与本次实跑矛盾, 需要老板/工程裁决** ★ | ★**建议: 从 ISS-322 §3-8 处方里删掉「必须显式钉 TP_DSI_*」这一条 (★它已被证明是冗余的★), 只保留「钉 R_SEL_* 到左上」★ ⇒ **代价 = ISS-322 作业包 §3-S6 的 `PCB_PART_POS` 串要改** ★ |
| ★**`iss325_s8_no_valid_control`** ★ | ★**「本单两臂互为对照但落位相同 ⇒ 【没有有效对照】⇒ 本单只提供【单臂绝对读数】(链终 unc 29 / 段内翻转 5), 不提供【臂间差值】」⇒ **后果: 「左上布局」这条处方对 unc 的净效应, 至今【没有任何实测】** ⇒ G7 (老板拍板) 手上其实【没有】这个处方的实测证据** ★ | ★**建议: 要拿到净效应, 必须补一个【真正有落位差异】的对照臂 (★例如把 `R_SEL_*` 挪到右上, 与现役板同侧 ⇒ 那才有差值★) —— **但那是【新的沙盒臂】, 归 main 决定要不要跑 (★不在本单范围★)** ★ |

★**★★登记走 `python3 state/frag_write.py --agent hw-lead --add-need` (★**禁 `open(p,"w")`**★) · ★**写完 `grep -c "iss325" state/fragments/hw.yaml` 复核★ ★**

---

## ★⑤ 边界自证: 4 个生成器产物被臂写回了 (★如实登记, 不许恢复★)★★

★**★现象 (★main 本轮实读★)**: ★**`HW/PCB/STACKUP.md` · `LAYOUT_RULES.md` · `GEN_SELF_CHECK.txt` · `_frame_reference.kicad_pcb` 的 mtime 在动 (★本轮 15:00 后是 14:42:52 那一批 + 本轮又动过★)** ★
★**★根因链 (★main 逐段读过源码★)**: ★**`state/replay_patch_chain.sh` L240 → `state/check_pcb_drc.py` → 它的 C5 自检 → `state/gen_kicad_project.py` → 该脚本无条件写这 4 个文件 (L256 / L286 / L303 / L369)** ★
★**★内容实情 (★main 实测★)**: ★**`STACKUP.md` 除首行时间戳外与 11-17 08:34 的旧副本逐字相同** ⇒ ★**⇒ 是生成器产物, 内容等价, 只有时间戳变 ⇒ 不是语义改动 ⇒ 板/网表/脚表/BOM 一个字节未动** ★
★**★你必须做 (★两条, 缺一不可★)**:
1. ★**在交卷页 §9 的「边界自证」里如实写** (★★§9 是 `logs/iss325/scripts/gen_sec9.py` 生成的 ⇒ ★**改生成脚本, 别手改§9★** ★) ★**「本单的臂经 `replay_patch_chain.sh` → `check_pcb_drc.py` → `gen_kicad_project.py` 重写了 `HW/PCB/` 下 4 个生成器产物; ★**除时间戳外内容逐字相同** ⇒ **板面/网表/脚表/BOM 一个字节未动**」 ★**
2. ★**★顺手查一件事并如实报 (★这是本项目的老账★)★**: ★**`state/gen_kicad_project.py` 是不是每次跑 `check_pcb_drc.py` 都会无条件重写这 4 个文件? ⇒ ⇒ 如果是 ⇒ ★**`state/daily_check.py` 每天的巡检都在动这 4 个文件** ⇒ **这是【复发型缺陷】⇒ 你只要【如实登记】(交给 main 判断要不要修), 不许去改 `gen_kicad_project.py`** ★ ★

★**★★绝对不许做的事★★**: ★**不许把这 4 个文件手动「恢复」回去 (★那叫擦产物·且下一次巡检又会被改·治不了根★)** ★ · ★**不许改 `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh`** ★

---

## ★⑥ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
python3 state/compare_arm_official.py --self-test      # 必须 rc=0 · ALL TESTS PASS
bash state/compare_arm_baseline.sh /tmp/chain_iss325_s8lu/final_chain.kicad_pcb
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb            # 必须 = 2026-11-06 07:07:17.362193413
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★占位符: 标准扫描 + ★★额外的 `__XXX__` 扫描 (★本单教训★) ★★
grep -cE "🔄|待填|PLACEHOLDER|施工中" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md   # 期望 0
grep -oE "__[A-Z_]+__" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md | wc -l          # ★期望 0★
grep -cE "🔄|待填|PLACEHOLDER|施工中" "HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md"   # 期望 0
grep -c "iss325" state/fragments/hw.yaml                                        # 期望 >= 1
grep -c "^## §9" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md                        # 期望 1
grep -oE "^## B[0-9]" "HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md" | wc -l   # 期望 6
```

★**★交卷前 ★★`gate_check.py` 的 Q1 必须回到 18/18★★** ⇒ ★**这是本单补 B1/B2/B4/B5 的验收判据 (★main 本轮实跑实测 = 15/18, 缺的那 3 格就是本单★)** ★

---

## ★⑦ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** ★ · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_official.py` / `state/compare_arm_baseline.sh` / `state/cmp_unc_sets.py` / `state/merge.py` / `state/issue_check.py` 只读★) · ★**零改生成器代码** (★`state/gen_pcb_netlist_board.py` / `state/gen_pcb_routing.py` / `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh` 只读★) · ★**零改既有文档正文** (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 只读 ⇒ §8 只给逐字改法·不动原文★) · ★**沙盒只写 `tmp/iss325/` + `logs/iss325/`** ★ · ★**只写 `state/fragments/hw.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★G7 归 main + 老板★) · ★**不自签 `state/issue_log.yaml`** ★

---

## ★⑧ 纪律 (★★这一趟的活很少, 别再被掐★)★★

★**① ★★绝对不许重跑那两条臂 (★已经跑完·产物在 /tmp 上·重跑 = 白烧一小时 + 覆盖已有产物★)★★** · ★**② ★★先写交卷页骨架, 再填内容 (★上一趟死在「改写 §7」的中途·交卷页一个字没动★)★★** · ★**③ 长任务一律 `nohup ... > logs/iss325/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**④ 单条 `exec` ≤ ~120 秒** · ★**⑤ 每 10 分钟至少一次写盘** · ★**⑥ 分片写完 `grep` 校验** · ★**⑦ ★★§9 是 `logs/iss325/scripts/gen_sec9.py` 生成的 ⇒ 要改 §9 就改那个脚本, 不要手改交付页的 §9 (★否则重跑脚本会覆盖你的手改★)★★ ★**
