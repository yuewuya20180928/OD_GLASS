# ISS-325 · hw-lead · ★★【cont2 续做 · 收割 + 收卷】★★

> ★**这是第二次续做, 不是从零重做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:5x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main · ★**单号**: ISS-325 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · PCB 线 · 纯沙盒预演 / 作业包 / 判据设计类 (HW 侧)** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改生成器代码** ★

---

## ★★★【★★重大状态变化: ★★两条臂已经跑完了★★】★★★

★**上一趟 (14:1x) 派的是「cont1 · 等臂跑完收割」, 但 ★**那一趟的会话在 14:2x 被父 run 连带 abort** ★ ⇒ ★**⇒ ★★好消息: 两条臂在 abort 之后【自己跑完了】★★** ★

★**main 14:4x~14:5x 本机实读 (★不抄任何 agent 报告★)**:

| 项 | ★**左上臂 (iss325_s8lu)** ★ | ★**同日对照臂 (iss325_s8ctl)** ★ |
|---|---|---|
| 裸板 | ★`/tmp/iss325_s8lu_R.kicad_pcb` md5 `3bfb30edfd7c64aafb9e908bc9dc0d57` (★2,712,620 B · 14:21★) | ★`/tmp/iss325_s8ctl_R.kicad_pcb` md5 `902ea02ac5f8e10310aa528687eaaad7` (★2,712,620 B · 14:28★) |
| 裸板 DRC | ★`/tmp/iss325_s8lu_R.drc.json` (★14:21★) ⇒ **viol 6 / unc 37 / unc 网名 31** | ★`/tmp/iss325_s8ctl_R.drc.json` (★14:28★) ⇒ **viol 6 / unc 37 / unc 网名 31** |
| 链终板 | ★`/tmp/chain_iss325_s8lu/final_chain.kicad_pcb` md5 `27b51bd5039a4f4b1d108cc1355b4463` · 3666 段 (★14:36★) | ★`/tmp/chain_iss325_s8ctl/final_chain.kicad_pcb` md5 `cc13d3ce5539ab714ee320c8cbb62e6b` (★14:36★) |
| 链终 DRC | ★`/tmp/chain_iss325_s8lu/final_board.drc.json` ⇒ **viol 6 / unc 29 / unc 网名 27** ★(5 clearance + 1 copper_sliver) | ★`/tmp/chain_iss325_s8ctl/final_board.drc.json` ⇒ **viol 6 / unc 29 / unc 网名 27** ★(5 clearance + 1 copper_sliver) |
| 段内 P/N 翻转 | ★**同段总数 47 / 翻转 5** ★ | ★**同段总数 47 / 翻转 5** ★ |

★**★★⇒ ⇒ ★★main 逐条核对后发现的【最重要的一件事】★★**:
★**★两臂的 20 个器件落位【逐个完全相同】★** (★main 用 pcbnew 逐个读 `GetPosition()` 实测★):
★`R_SEL_D3_P`(5.50,3.0) · `R_SEL_D3_N`(7.95,3.0) · `R_SEL_D2_P`(13.10,3.0) · `R_SEL_D2_N`(15.55,3.0) · `R_SEL_CK_P`(20.70,3.0) · `R_SEL_CK_N`(23.15,3.0) · `R_SEL_D1_P`(28.30,3.0) · `R_SEL_D1_N`(30.75,3.0) · `R_SEL_D0_P`(35.90,3.0) · `R_SEL_D0_N`(38.35,3.0) · `TP_DSI_D3_P`(5.50,6.20) · `TP_DSI_D3_N`(7.95,6.20) · `TP_DSI_D2_P`(13.10,6.20) · `TP_DSI_D2_N`(15.55,6.20) · `TP_DSI_CK_P`(20.70,6.20) · `TP_DSI_CK_N`(23.15,6.20) · `TP_DSI_D1_P`(28.30,6.20) · `TP_DSI_D1_N`(30.75,6.20) · `TP_DSI_D0_P`(35.90,6.20) · ★**`TP_DSI_D0_N`(41.55,3.00)** ★
★**⇒ ⇒ 两臂的【唯一变量】(★显式多钉 10 个 `TP_DSI_*`★) 在【落位结果上完全没有生效】⇒ ⇒ 两臂的 unc 网名集合【逐条相同】(★main 集合比对: 裸板 31 == 31 · 链终 27 == 27 · 差集两边都为空★) ⇒ ⇒ ★**「左上臂 vs 同日对照臂」这个对照【没有构成对照】** ★**

★**★★机制解释 (★main 读源码找到的, 你要自己复核并写进交付页★)★★**:
★**`state/gen_pcb_netlist_board.py` L1057~L1063 的「测试点贴伙伴件」规则**: ★**`TP_DSI_*` 默认就跟着它的伙伴件 `R_SEL_*` 走 ⇒ ★**当 `R_SEL_*` 被钉到左上 (x 5.50..38.35, y 3.00) 时, `TP_DSI_*` 自动就落在同一 x 那一列的 y=6.20** ⇒ ★**⇒ 对照臂 (只钉 10 个 `R_SEL_*`, 不钉 `TP_DSI_*`) 的 `TP_DSI_*` 落位【与】左上臂【自动产生的】落位【完全一致】⇒ ⇒ ★**「显式钉 TP」这条处方【是冗余的】★★ ★
★**★⇒ ⇒ 本单原来的核心论点「显式钉死 TP_DSI_* ⇒ 能消掉段内交叉」★【被这次实跑证伪了】★★** ⇒ ★**⇒ 交付页 §7 的结论必须按【实测】重写, 不许再写「左上布局 ⇒ 翻转 17 → 5」那种【只拿 best23 板比现役板】的结论 ★**

★**★★★⇒ ⇒ ★★★【★本单现在的正事 ★】★★★**:
★**★① 把这个【证伪】写成交付页里最有价值的一段 (★这是比「归零可达不可达」更硬的结论★) ★**
★**② 把 4 处 `__XXX__` 占位符用【臂的实测读数】填掉 ★**
★**③ 补 §9 · 补交卷页 B1/B2/B4/B5 · 补写分片 (★分片已经写了 25 处, 但要核一遍是不是完整★) ★**

---

## ★② 收割臂读数的命令 (★臂已跑完, 直接收割, 绝不许重跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 裸板 + 链终板 + DRC (★都已经在盘上了·直接读★)
ls -la /tmp/iss325_s8lu_R.kicad_pcb /tmp/iss325_s8ctl_R.kicad_pcb \
       /tmp/iss325_s8lu_R.drc.json /tmp/iss325_s8ctl_R.drc.json \
       /tmp/chain_iss325_s8lu/final_chain.kicad_pcb /tmp/chain_iss325_s8ctl/final_chain.kicad_pcb \
       /tmp/chain_iss325_s8lu/final_board.drc.json /tmp/chain_iss325_s8ctl/final_board.drc.json
# ② 三方 fresh DRC 汇总 (★臂脚本自带的测量脚本·★argv 口径你必须先读脚本再跑★)
bash logs/iss325/scripts/iss325_measure.sh
# ③ 名单制闸 (★三条都要抄出来·不许只写「通过/不通过」★)
python3 state/compare_arm_official.py --self-test
python3 state/compare_arm_official.py /tmp/chain_iss325_s8lu/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
python3 state/compare_arm_official.py /tmp/chain_iss325_s8ctl/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
# ④ ★★同工艺基线对照 (★不是 vs 官方板!★ 见下§②-1★)
bash state/compare_arm_baseline.sh /tmp/chain_iss325_s8lu/final_chain.kicad_pcb
# ⑤ 网名集合三层口径
python3 state/cmp_unc_sets.py /tmp/chain_iss325_s8lu/final_board.drc.json /tmp/chain_iss325_s8ctl/final_board.drc.json
# ⑥ 段内 P/N 顺序翻转 (★两臂都要·main 已实测都是 47/5·你要自己复现一遍★)
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8lu_R.kicad_pcb lu
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8ctl_R.kicad_pcb ctl
# ⑦ 零铜 / 有铜未连通 机制表
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py <板> <板.drc.json>
```

### ★★②-1 ★★一条必须写进交付页的判据警告 (★main 实读发现的★)★★

★**`/tmp/chain_iss325_s8lu/final_chain.kicad_pcb.chain.json` 里, 生成器自己写了一句话** ★:
> ★**「★这块板是【官方补丁链的产物】⇒ ★★**不是独立候选臂**; ★★**要当候选臂比, 必须与【同链基线】比 (★`state/compare_arm_baseline.sh`★)」** ★

★**★⇒ ⇒ 「左上臂 vs 官方板」这个比较【本身是错的】★** ⇒ ★**★`state/compare_arm_baseline.sh` 的文件头白纸黑字写着: 「官方板的 stage-1 是 17022 段 (★历史 promote 累积★), 而当前路由器的产物只有 13407 段 ⇒ ★**两边不在同一条工艺线上 ⇒ 比出来的差异全是【工艺差】不是【臂的优劣】**」⇒ ⇒ **基线必须也用当前路由器跑 + 套同一条已校准的补丁链** ★ ★
★**★⇒ ⇒ 你必须用 `state/compare_arm_baseline.sh` 做对照, 不许用 `compare_arm_official.py <臂> <官方板>` 当「臂的功劳」证据★** ★
★**★⇒ ⇒ 而且 ★**本单的两臂【连同链基线都没比】(它们互相就是彼此的对照, 但两臂落位相同⇒ 对照无效)⇒ ⇒ ★**你必须自己判断: 要么找一个真正同链基线, 要么如实写「本单的两臂互为对照但落位相同 ⇒ 【没有有效对照】⇒ 本单只提供【单臂绝对读数】, 不提供【臂间差值】」★★ ★

---

## ★③ 必须补完的 4 件 (★与臂无关, 现在就能做★)

### ★③-1 · ★★交付页那 4 处 `__XXX__` 占位符 ★★

★**main 本轮实读**: ★**`HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` 里仍有 4 处 `__FLIP__` / `__TOTAL__` / `__UNC__` / `__ZEROREACH__`** ★
★**★而且 ★★标准占位符扫描抓不到它们★★** ⇒ ★**main 实测 `grep -cE "🔄|待填|PLACEHOLDER|施工中"` = **0** ★⇒ 但 `grep -oE "__[A-Z_]+__"` = **4** ★ ⇒ ★**★交卷自证第 ⑨ 条会判「通过」⇒ 交卷页必须如实写一句「标准扫描对 `__XXX__` 无效 ⇒ 本单额外自查了 `__[A-Z_]+__`」★★ ★

★**★这 4 处现在该填什么 (★main 已读上下文 + 臂的实测读数★)**:

| 位置 | ★现状★ | ★★该填成★★ |
|---|---|---|
| §8-1 第 481 行 | ★`段内 P/N 顺序翻转 = __FLIP__ / __TOTAL__` ★ | ★**左上臂 5 / 47** ★ ★**但必须同时写上「★同日对照臂也是 5 / 47 ⇒ 两臂无差值 ⇒ 该处方在这一对臂上没有净效应★」★** ★ |
| §8-2 第 18 行 | ★`左上布局臂 = unc __UNC__` ★ | ★**裸板 unc 37 · 链终 unc 29** (★两个数都给 + 标明哪个是裸板哪个是链终★) ★ |
| §8-2 第 18 行 | ★`【挪器件】单独能不能归零 = __ZEROREACH__` ★ | ★**「不能」+ 依据**: ★**两臂 unc 网名集合逐条相同 (裸板 31 == 31 / 链终 27 == 27) ⇒ 【挪器件】这一处方对 unc 没有任何净效应; 且 §7-3 的 15 条零铜与 11 条两边都不通依然在** ★ |
| §8-2 第 18 行 | (★同一句里的第三个 `__XXX__`★) | ★**逐个定位·不许留空★** ★ |

★**★★铁律: ★★这 4 处的值必须来自【臂的实跑读数】, 不许从 §6-2 的 `best_unc23_clrfix` 读数 (5/47) 或任何历史板抄过来★★** ⇒ ★**★而且 ★★§6-2 那张表本身要加一句限定: 它量的是【盘上已有的 best23 板 vs 现役板】, 不是【本单两臂之间的差】⇒ 两者不是一回事, 不许混用★★ ★**

### ★③-2 · ★★交付页补 §9 (★证据分级与零写板双证与文件清单★)

★**main 本轮实读: `grep -c "^## §9"` = **0** ⇒ 交卷页 B0-2 自己写的「§0 … §9」里 ★**§9 根本不存在** ★** ⇒ **补上**
★**★好消息: ★★`logs/iss325/scripts/gen_sec9.py` (★14,477 B·★main 实读·它会幂等地重写 §9 段★) 已经写好了 ⇒ ★★你只要跑它, 不要手写 §9★ ★**
```bash
python3 logs/iss325/scripts/gen_sec9.py --pre-proof logs/iss325/08_zero_write_proof_pre.txt \
                                         --post-proof logs/iss325/08_zero_write_proof_post.txt
```
★**★它里面已经把「4 个生成器产物的边界自证」写进去了 (落 `logs/iss325/22_gen_products_boundary.txt`) ⇒ ★★跑完必查那个文件在不在★ ★

### ★③-3 · ★★交卷页补 B1 / B2 / B4 / B5 (★现在只有 B0 / B3 / B6★)★★

★**★这是门禁链 `state/gate_check.py` 的 Q1「6 项必填验收块」★★** ⇒ ★**main 本轮实跑 `gate_check.py --json` ⇒ ★**Q1 = 15/18, 掉的那 3 格就是本单 (hw-lead: 缺 [B2] 验收标准自评 · 缺 [B4] 接口取值声明 · 缺 [B5] 未决项与卡点) ★** ⇒ ⇒ ★**⇒ 本单补完 B1/B2/B4/B5, Q1 就能回到 18/18 ⇒ ★**这条闸现在就在红着等你补, 不是装饰★ ★

| 块 | ★**内容 (★照 `state/gate_check.py` 的 `REQUIRED_BLOCKS` 口径★)** |
|---|---|
| ★**B1** ★ | ★**结论摘要 (★一句话★)** ★ |
| ★**B2** ★ | ★**验收标准自评 (★逐条「通过 / 不通过 / 未验」★)** ★ —— ★**不许只写一句「全部通过」★** ⇒ ★**每个验收项单独一行 + 判定 + 依据读数★** ★ |
| ★**B3** | ★**证据分级** ★ (★**已有·本轮不用动★**) |
| ★**B4** ★ | ★**接口取值声明 (★`interface_claims`★)** ★ ⇒ ★**照 §4 那几条逐字给 (★网名 / 坐标 / 数值 / 判据来源★)** ★ |
| ★**B5** ★ | ★**未决项与卡点 (★需要谁回答什么★)** ★ ⇒ ★**照 §7-5 逐条列 (★归 main + 老板的 7 条 need·一条不许漏★) ⇒ ★**并且加上本轮新发现的两条 (★见 §③-5★)** ★ |
| ★**B6** | ★**自证复现命令** ★ (★**已有·本轮不用动★**) |

### ★③-4 · ★★核一遍分片 (★已写 25 处·但要核完整性★)

★**main 本轮实读: `grep -c "iss325" state/fragments/hw.yaml` = **25** ★ ⇒ ★**★上一趟确实写了分片 (★hw-lead 在 abort 前抢在前面写了★) ⇒ 你要核的是: needs / artifacts / interface_claims 三类是否齐全, 以及内容有没有跟上本轮新读数 (★尤其 `iss325_s8_zero_reachability` / `iss325_s8_csi_side_zero_effect` 这两条 need 的值★)** ★

### ★③-5 · ★★把本轮新发现的两条 need 交出去 (★交 main + 老板·不代拍★)★★

★**★这两条是本轮实跑【证伪】出来的, 价值高于任何「归零可达不可达」的推算★** ★

| ★**need key** ★ | ★**内容** ★ | ★**建议默认值** ★ |
|---|---|---|
| ★**`iss325_s8_tp_pin_noop_proven`** ★ | ★**「显式钉死 `TP_DSI_*`」这条处方【被证伪】: 生成器 L1057~L1063 的「TP 贴伙伴件」规则让 `TP_DSI_*` 自动跟着 `R_SEL_*` 走 ⇒ 对照臂 (不钉 TP) 与左上臂 (钉 TP) 的 20 个器件落位【逐个完全相同】⇒ unc 网名集合也逐条相同 (裸板 31==31 / 链终 27==27) ⇒ ★**该处方对 unc 无净效应**★** ⇒ **ISS-322 §3-8 里「只钉 R_SEL 不钉 TP 等于给路由器埋雷」这个判断, 与本次实跑矛盾, 需要老板/工程裁决** ★ | ★**建议: 从 ISS-322 §3-8 处方里删掉「必须显式钉 TP_DSI_*」这一条 (★它已被证明是冗余的★), 只保留「钉 R_SEL_* 到左上」★ ⇒ **代价 = ISS-322 作业包 §3-S6 的 `PCB_PART_POS` 串要改** ★ | 
| ★**`iss325_s8_no_valid_control`** ★ | ★**「本单两臂互为对照但落位相同 ⇒ 【没有有效对照】⇒ 本单只提供【单臂绝对读数】(链终 unc 29 / 段内翻转 5), 不提供【臂间差值】」⇒ **后果: 「左上布局」这条处方对 unc 的净效应, 至今【没有任何实测】** ⇒ G7 (老板拍板) 手上其实【没有】这个处方的实测证据** ★ | ★**建议: 要拿到净效应, 必须补一个【真正有落位差异】的对照臂 (★例如把 `R_SEL_*` 挪到右上, 与现役板同侧 ⇒ 那才有差值★) —— **但那是【新的沙盒臂】, 归 main 决定要不要跑 (★不在本单范围★)** ★ | 

★**★★这两条 need 的登记走 `state/frag_write.py --agent hw-lead --add-need`★★ (★**禁 `open(p,"w")`**★)

---

## ★④ 边界自证: 4 个生成器产物被臂写回了 (★如实登记, 不许恢复★)★★

★**★现象 (★main 本轮实读·mtime 一直在动★)**: ★**`HW/PCB/STACKUP.md` · `LAYOUT_RULES.md` · `GEN_SELF_CHECK.txt` · `_frame_reference.kicad_pcb` —— 14:42:52 那一次是本单的臂写的** ★
★**★根因链 (★main 逐段读过源码★)**: ★**`state/replay_patch_chain.sh` L240 → `state/check_pcb_drc.py` → 它的 C5 自检 → `state/gen_kicad_project.py` → 该脚本无条件写这 4 个文件 (L256 / L286 / L303 / L369)** ★
★**★内容实情 (★main 实测★)**: ★**`STACKUP.md` 除首行时间戳外与 11-17 08:34 的旧副本逐字相同** (`diff <(tail -n +2 旧) <(tail -n +2 新)` ⇒ 无差异) ⇒ ★**⇒ 是生成器产物, 内容等价, 只有时间戳变 ⇒ 不是语义改动 ⇒ 板/网表/脚表/BOM 一个字节未动** ★
★**★你必须做 (★两条, 缺一不可★)**:
1. ★**在交卷页 §9 的「边界自证」里如实写**: ★**「本单的臂经 `replay_patch_chain.sh` → `check_pcb_drc.py` → `gen_kicad_project.py` 重写了 `HW/PCB/` 下 4 个生成器产物; ★**除时间戳外内容逐字相同** ⇒ **板面/网表/脚表/BOM 一个字节未动**」 ★**
2. ★**★顺手查一件事并如实报 (★这是本项目的老账★)★**: ★**`state/gen_kicad_project.py` 是不是每次跑 `check_pcb_drc.py` 都会无条件重写这 4 个文件? ⇒ ⇒ 如果是 ⇒ ★**`state/daily_check.py` 每天的巡检都在动这 4 个文件** ⇒ **这是【复发型缺陷】⇒ 你只要【如实登记】(交给 main 判断要不要修), 不许去改 `gen_kicad_project.py`** ★ ★

★**★★绝对不许做的事★★**: ★**不许把这 4 个文件手动「恢复」回去 (★那叫擦产物·且下一次巡检又会被改·治不了根★)** ★ · ★**不许改 `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh` (★零改生成器代码★)** ★

---

## ★⑤ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
python3 state/compare_arm_official.py --self-test      # 必须 rc=0 · ALL TESTS PASS
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

## ★⑥ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** ★ · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_official.py` / `state/compare_arm_baseline.sh` / `state/cmp_unc_sets.py` / `state/merge.py` / `state/issue_check.py` 只读★) · ★**零改生成器代码** (★`state/gen_pcb_netlist_board.py` / `state/gen_pcb_routing.py` / `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh` 只读★) · ★**零改既有文档正文** (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 只读 ⇒ §8 只给逐字改法·不动原文★) · ★**沙盒只写 `tmp/iss325/` + `logs/iss325/`** ★ · ★**只写 `state/fragments/hw.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★G7 归 main + 老板★) · ★**不自签 `state/issue_log.yaml`** ★

---

## ★⑦ 纪律 (★这项目的老教训·今天连踩两遍★)

★**① ★★绝对不许重跑那两条臂 (★已经跑完了·产物在 /tmp 上·重跑 = 白烧一小时 + 覆盖已有产物★)★★** · ★**② 交卷单第一件事就是 `write` 建骨架** ★ · ★**③ 长任务一律 `nohup ... > logs/iss325/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**④ 单条 `exec` ≤ ~120 秒** ★ · ★**⑤ 每 10 分钟至少一次写盘** (★★★上一趟两趟都被 abort ⇒ ★**这趟务必先把【交卷页骨架 + §9 + B1/B2/B4/B5 + 4 处占位符】这些【与臂无关的活】做完, 再去处理【证伪结论】那部分★ ⇒ ★**这样就算又被 abort, 本单也已经交得出去★) ★** · ★**⑥ 分片写完 `grep` 校验** · ★**⑦ ★★先做 §③ 那 4 件, 再写 §7 的证伪结论★★**
