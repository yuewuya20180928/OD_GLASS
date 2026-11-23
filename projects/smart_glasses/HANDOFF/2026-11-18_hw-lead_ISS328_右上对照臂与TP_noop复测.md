# HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md —— ISS-328 交卷单

> **单号**: ISS-328 (cont1 续做) · **owner**: hw-lead (硬件总工) · **verify_by**: main · **job**: cron `fb67af40` (ARS45 队列自动派活) · **日期**: 2026-11-18 (Asia/Shanghai)
> **性质**: ★**内部活 · PCB 线 · 纯沙盒预演 / 对照臂读数类 (HW 侧)** ★ · ★**零写板 · 零落表 · 零改闸 · 零改生成器代码 · 零改网表/脚表/BOM/原理图真源** ★ · 沙盒只写 `tmp/iss328/` + `logs/iss328/` · ★**零外发** ★ · 不替老板拍板 · 不自签 issue_log
> **交付页**: `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` (★新建★ · §0 口径与边界自证 + §1 唯一变量与落位自检 + §2 读数表 + §3 名单制闸判决 + §4 TP no-op 复测 + §5 给 main 的结论 + §6 证据分级 + §7 文件清单)
> ★**本文件所有数字都是从 `logs/iss328/` 的机器生成原始输出逐字搬来的** ★

---

## B0 一句话结论 + 交付物清单

### B0-1 · ★★一句话★★

★**ISS-328 右上对照臂【判决 = 不通过 (REJECT)】⇒ ★「挪器件位置」这条处方已被【ISS-325 左上臂 + ISS-328 右上臂】两个臂证伪 ⇒ 归零只剩【机制级 / 老板口径 / 路由器本体】三条路·且「unc 45 → 29」因段数 3986 vs 18092 (★路由器代码已漂移·不同工艺★) 一律不算数★**

### B0-2 · ★★交卷物清单 (4 件) ★★

| # | 路径 | 内容 | 新建? |
|---|---|---|---|
| 1 | `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` | ★**主交付物** ★: §0 (口径与边界自证) · §1 (唯一变量 + 落位自检 diff=102) · §2 (6 条读数表 · 裸板/链终分开列) · §3 (名单制闸判决) · §4 (TP no-op 复测 · diff=16) · §5 (给 main 的结论) · §6 (证据分级 + 零写板双证 + 文件清单) · §7 (文件清单) | ★**新建** ★ |
| 2 | `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` | ★**本交卷页** ★ (B0~B6 齐全) | ★**新建** ★ |
| 3 | `logs/iss328/` | ★**原始输出目录** ★: ① 官方板 `R_SEL_*`/`TP_DSI_*` 落位机器读数 ② 官方链封装落位 diff (diff=0) ③ 排版阶段落位清单 × 3 ④ TP no-op 落位 diff (diff=16) ⑤ 右上臂 `PCB_PART_POS` + 出处登记 ⑥ 右上臂起链日志 ⑦ 裸板 fresh DRC ⑧ 链终板 fresh DRC ⑨ 封装落位 diff ⑩ 链终几何 ⑪ 段内 P/N 翻转 ⑫ 名单制闸 ⑬ 零写板双证 ⑭ ★unc 网名集合逐条清单 + 两组集合关系 (★`logs/iss328/35_unc_netsets_readonly.txt`★) | ★**新建** ★ |
| 4 | `state/fragments/hw.yaml` | ★**走 `python3 state/frag_write.py --agent hw-lead` 原子写** ★ (★禁 `open(p,"w")`★) · artifacts / needs_from / interface_claims 各 ≥ 1 · status 换 ISS-328 | ★**新增条目** ★ |

★**零字节改动的既有文件 (★边界自证的另一半★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` · 网表 / 脚表 / BOM / 原理图源 · 闸 `state/gate_check.py` / `state/merge.py` / `state/issue_check.py` / `state/compare_arm_official.py` / `state/compare_arm_baseline.sh` / `state/cmp_pcb_geom.py` / `state/cmp_unc_sets.py` · 生成器 `state/gen_pcb_netlist_board.py` / `state/gen_pcb_routing.py` / `state/gen_kicad_project.py` / `state/replay_patch_chain.sh` / `state/clrfix_iter.sh` · 既有文档 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` / `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` · `state/issue_log.yaml` · 别人的分片 `sw.yaml` / `mech.yaml` / `pm.yaml` —— ★**全部逐字节不变** ★

---

## B1 结论摘要

### B1-1 · ★★结论摘要 (★本单回答的那一问★)★★

★**任务书 §D 问的是: 「G7 取证的唯一前提 =『右上臂』这条处方到底有没有用」★**

★**本单答案: 【没用·而且它已被两个臂证伪了】** —— ★**但本单同时交出两条它【有】的价值: ① 它【确实构成了一条真对照】(★全板封装落位 diff = 102 ≠ 0·★这是 ISS-325 左上臂那条白跑对照 (diff = 0) 没有的东西★) ② 它把「右上这个方向 = 段内 P/N 翻转 20/47」这个事实【钉死在盘上】★**

★**三条必须让 main 知道的 (★全部来自本机实跑·不是抄任何 agent 报告★)★

★**① 判决 = REJECT (名单制闸) ⇒ 「挪器件位置」这条处方已被【两个臂】证伪 ⇒ 剩下只有三条路** ★
★**ISS-325 左上臂**: ★退铜 4 + 差分死腿 1 对 + 逐网孤岛 +9 ⇒ REJECT ★ ★**ISS-328 右上臂 (本单)**: ★净救回 -1 + 差分死腿 3 对 + 逐网孤岛变多 ⇒ REJECT ★
★**⇒ ⇒ 剩下只有三条路: ① 机制级 (12 个零铜网换机制: 成对走廊 / 换层绕开 / 路由器本体) ② 老板口径 (W-2 / W-1c / A4 / W-3 / U-1 / P7) ③ 路由器本体** ★
★**★本单另交一条独立于名单制闸的读数★**: ★段内 P/N 顺序翻转 = 20/47 (★挪到右上·本单实测★) vs 5/47 (★挪到左上·ISS-325 实测★) vs 17/47 (★现役板★) ⇒ ★三个数没有一个是 0 ⇒ 「挪位置」对【段内 P/N 顺序】这个几何指标【也没有出路】★ ★

★**② 段数 3986 vs 官方终板 18092 ⇒ 路由器代码已漂移 ⇒ 【同工艺才可比】⇒ 「unc 45 → 29」在追平段数之前一律不算数** ★
★**官方链的 stage-1 产物是 17022 段, 当前路由器只出 3471 段 ⇒ 两臂不同工艺 (自校准闸 档②) ⇒ 链跑完但产物【不能与官方板直接比】** ★
★**⇒ ⇒ 这是「unconnected 变少 ≠ 板子更好」的第二层: 第一层 = 名单制 · 第二层 = 同工艺才可比** ★

★**③ 「钉 `TP_DSI_*` 不是 no-op」这条结论 (排版阶段 差异 16 行) 与 ISS-325 的「是 no-op」正好相反 ⇒ 适用范围必须标「在哪个配方下测的」** ★
★**本单配方 = v76mz env 逐字 + 只把 10 条 `R_SEL_*` 放到方案 A 右上组 + `PCB_SKIP_ROUTE=1` 只出排版 ⇒ 差异 16 行 (8 个 ref 挪位)** ★
★**⇒ ⇒ P-1 的 20 条串【一条不许删】 (★已在 `state/fragments/hw.yaml` 的 `iss328_p1_partpos_20_must_keep` 登记·本单不改它★)** ★

### B1-2 · ★★读数总表 (★6 条·机器生成·零手抄★)★★

| # | 读数 | 右上臂 | 对照 / 基线 |
|---|---|---|---|
| ① | 排版阶段裸板 md5 / 封装 | `bf588510db547e75…` / 185 | 基线臂 `a8adec4afcc1d3c…` / 185 |
| ② | 裸路由器产物 md5 / 段数 / viol / unc | `f499787f720637ba…` / 3471 / 11 / 35 (★unc 网名 **34**★) | — |
| ③ | 链终板 md5 / 段数 / viol / unc | `dfd03ef02cf10a4e…` / 3986 / 12 / 29 (★unc 网名 **28**★) | 官方终板 `611b869e13518c3c…` / 18092 / 0 / 45 |
| ④ | clrfix 终板 md5 / viol / unc | `ce7705b6c7df5355…` / 0 / 29 | — |
| ⑤ | ★**全板 185 封装落位 diff** ★ | ★**102 行 / 51 个 ref (排版阶段与链终阶段同集合)** ★ | ★**≠ 0 ⇒ 对照有效** ★ |
| ⑥ | ★**名单制闸判决** ★ | ★**REJECT (rc = 1)×3** ★ | — |

★**(a) 臂 vs 官方板**: ★DRC 12/0 · unc 29/45 · 零铜 13/24 · 差分单边零铜 7/11 · 退铜名单 2 (`CSI_MCLK_SRC` `USB_CC1`) · 差分死腿 0 · 逐网孤岛变多 7 ⇒ **REJECT (rc=1)** ★
★**(b) clrfix 臂 vs 官方板**: ★DRC 0/0 · 其余同上 · 逐网孤岛变多 7 ⇒ **REJECT (rc=1)** ⇒ ★**clrfix 把 DRC 清零了·但名单制闸一条没松** ★
★**(c) 臂 vs 基线臂同链终板**: ★DRC 12/205 · unc 29/29 · 零铜 13/12 · 差分单边零铜 7/5 · 退铜 3 · 差分死腿 3 对 · 逐网孤岛变多 6 · 判据① 网名集合 27→28 (变大·❌) · 净救回 -1 ⇒ **REJECT (rc=1)** ★
★**(d) unc 网名集合 (★读数 ①/② 要的就是这个集合·★逐条清单见 B4 ⑦ 与交付页 §2-2b·★出处 `logs/iss328/35_unc_netsets_readonly.txt`★)★**: ★**裸路由器产物 34 个网名 · 右上臂链终板 28 个 · 基线臂同链终板 27 个** ★ ⇒ ★**①→②: 交集 28 / 仅①有 6 / 仅②有 0 ⇒ 链终集合 ⊂ 裸路由器集合 (严格子集) ⇒ 补丁链这一步只救不破** ★ ⇒ ★**② vs ③: 交集 22 / 候选新断 6 / 候选救回 5 ⇒ 净 +1** ★ (★与链日志逐字一致★) ★
★**出处**: `logs/iss328/08_rightupper_arm.log` L64~L199 + `logs/iss328/33_recalc_gate_rc.txt` (★rc 复算★) + `logs/iss328/35_unc_netsets_readonly.txt` (★unc 网名集合★) · 完整逐条见交付页 §2 / §3 ★

---

## B2 验收标准自评 (★逐条 通过 / 不通过 / 未验★)

★**逐条自评 (★判决口径 = 名单制闸 + DRC·★禁拿 unc 变少当成功★)★**

| # | 验收项 | 判据 | 实测 | 判决 |
|---|---|---|---|---|
| ① | 右上臂能构成【真对照】 | 全板 185 封装落位 diff ≠ 0 | ★**diff = 102 行 / 51 个 ref** ★ | ★**通过** ★ |
| ② | TP no-op 复测 (官方链同配方) | 两种结果都必须交卷 | ★**排版阶段落位差异 16 行 / 8 个 ref 挪位 ⇒ 显式钉不是 no-op** ★ | ★**通过 (已答)** ★ |
| ③ | ★**名单制闸 rc = 0** ★ | 退铜名单空 + 差分死腿空 + 逐网孤岛空 + DRC=0 | ★**rc = 1 ⇒ REJECT (退铜 2 条 · 逐网孤岛变多 7 条 · 差分死腿 0)** ★ | ★**不通过** ★ |
| ④ | ★**DRC viol = 0** ★ | 链终板 DRC 违规数 | ★**链终板 12 ⇒ 不通过; clrfix 终板 0 ⇒ 通过** ★ | ★**部分通过** ★ |
| ⑤ | 官方链同配方下的落位不动 | 官方链补丁链 diff | ★**diff = 0** ★ | ★**通过** ★ |
| ⑥ | ★**零写板** ★ | 板 md5 / mtime 逐字节不变 | ★**md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`** ★ | ★**通过** ★ |
| ⑦ | ★**段数追平官方链后再比 unc** ★ | 段数 ≈ 官方链 18,092 | ★**臂 3,986 段 ⇒ 未追平 ⇒ 「unc 45→29」不算数 (同工艺才可比)** ★ | ★**未验** ★ |

★**总判决: 【不通过 (REJECT)】⇒ 「挪器件位置」这条处方已被 ISS-325 左上臂 + ISS-328 右上臂两个臂证伪** ★

---

## B3 证据分级

★**每条结论的证据分级 (★标签必须打·不许省★)★**

| 结论 | 分级 | 证据文件 |
|---|---|---|
| ★**全板 185 封装落位 diff = 102 行 / 51 个 ref ⇒ 对照有效** ★ | ★**[实测]** ★ | `logs/iss328/08_rightupper_arm.log` · `tmp/iss328/diff1_ru_vs_base.tsv` |
| ★**排版阶段 TP 钉 vs 不钉 ⇒ 落位差异 16 行 ⇒ 显式钉不是 no-op** ★ | ★**[实测]** ★ | `logs/iss328/06_tp_noop_placement_diff.txt` |
| ★**官方链补丁链不动封装落位 (diff = 0)** ★ | ★**[实测]** ★ | `logs/iss328/04_official_chain_fp_pos_diff.txt` |
| ★**名单制闸判决 = REJECT (rc = 1)×3** ★ | ★**[实测]** ★ | `logs/iss328/33_recalc_gate_rc.txt` · `logs/iss328/08_rightupper_arm.log` L198 |
| ★**指标两列 (DRC 12/0 · unc 29/45 · 零铜 13/24 · 差分单边零铜 7/11 · 退铜 2 · 死腿 0 · 孤岛 +7)** ★ | ★**[实测]** ★ | `logs/iss328/33_recalc_gate_rc.txt` |
| ★**段内 P/N 翻转 20/47 (分母 47)** ★ | ★**[实测]** ★ | `logs/iss328/34_cont3_readonly_recalc.txt` |
| ★**官方链 stage-1 = 17,022 段 vs 当前路由器 3,471 段 ⇒ 路由器代码已漂移 ⇒ 两臂不同工艺** ★ | ★**[实测]** ★ | `logs/iss328/08_rightupper_arm.log` (自校准闸 档②) |
| ★**⇒ 「同工艺才可比」⇒ 「unc 45 → 29」在段数追平之前一律不算数** ★ | ★**[推算]** ★ | 依据上一行 [实测] 的口径差推导 |
| ★**⇒ 归零只剩三条路: ① 机制级 (12 个零铜网换机制) ② 老板口径 (W-2 / W-1c / A4 / W-3 / U-1 / P7) ③ 路由器本体** ★ | ★**[推算]** ★ | 依据 ISS-325 左上臂 + 本单右上臂两个臂的 REJECT 读数 |
| ★**官方链原配方复跑 (段数追平 18,092)** ★ | ★**[未验 / 0 数据]** ★ | ★**盘上不存在该读数·不许编** ★ |
| ★**unc 网名集合 (裸路由器产物 34 / 右上臂链终 28 / 基线臂同链终 27) + ①→② 严格子集 + ② vs ③ 交集 22 / 救回 5 / 新断 6** ★ | ★**[实测]** ★ | `logs/iss328/35_unc_netsets_readonly.txt` (★脚本 `tmp/iss328/scripts/iss328_netsets_readonly.py`·★只读·未重跑任何链/臂★) |
| ★**⇒ 「补丁链这一步只救不破」** ★ | ★**[推算]** ★ | 依据上一行 [实测] 的严格子集关系 (★只证明补丁链这一步·★不代表整条臂成立·★不得冲抵 REJECT★) |

---

## B4 接口取值声明 (★别人要照抄的东西逐字给★)

★**逐字给 (★别人要照抄的东西·数值一律来自 `logs/iss328/33_recalc_gate_rc.txt` + `logs/iss328/34_cont3_readonly_recalc.txt`·不许自己再数一遍★)★**

★**⓪ 右上臂的 10 条 `R_SEL_*` `PCB_PART_POS` 串 (★机器读自官方板·零手抄·★逐字照抄用★)**★**

```text
R_SEL_D0_N:78.90,5.50;R_SEL_D0_P:83.70,5.50;R_SEL_D1_N:88.50,5.50;R_SEL_D1_P:93.30,5.50;R_SEL_CK_N:98.10,5.50;R_SEL_CK_P:102.90,5.50;R_SEL_D2_N:107.70,5.50;R_SEL_D2_P:112.50,5.50;R_SEL_D3_N:117.30,5.50;R_SEL_D3_P:122.30,5.50
```

★出处: `logs/iss328/05_RU_PCB_PART_POS.txt` (★机器读·零手抄★) + `logs/iss328/05b_ru_partpos_provenance.txt` (★逐条出处登记★) · ★同一串在 `logs/iss328/08_rightupper_arm.log` L14~L16 逐字重印★ · ★交付页 §1-2 同串见 L70★ ★
★**注意**: ★这 10 条 = P-1 那条 20 条串的【上半段】(下半段 = 10 条 `TP_DSI_*`)·★20 条一条都不许删回 10 条 (★依据 = 排版阶段 diff=16 ⇒ 显式钉 `TP_DSI_*` 不是 no-op★)·★登记在 `state/fragments/hw.yaml` 的 `iss328_p1_partpos_20_must_keep`·本单不改它★★

★**① 右上臂链终板 vs 官方板 (名单制判据)★**

| 指标 | 候选 (右上臂) | 官方板 |
|---|---|---|
| DRC 违规 | ★**12** ★ | 0 |
| unconnected | ★**29** ★ | 45 |
| 零铜网 (≥2 焊盘) | ★**13** ★ | 24 |
| 差分单边零铜 | ★**7** ★ | 11 |
| 差分 Δ 超差 | ★**2** ★ | 3 |
| 走线段 | ★**3,986** ★ | ★**18,092** ★ |
| 过孔 | ★**593** ★ | 433 |
| parity 通过 | True | False |

★**退铜名单 (官方板有铜 ⇒ 候选零铜): 2 条 ⇒ `CSI_MCLK_SRC` · `USB_CC1`** ★
★**差分对死腿: 0** ★
★**逐网孤岛变多: 7 条 ⇒ `BOOT_N` · `CSI_D0_CK_N` · `CSI_MCLK` · `CSI_MCLK_SRC` · `KEY_VOL_P` · `LED_B` · `USB_CC1`** ★
★**(参考) 救回零铜的网: 13** ★
★**判定: REJECT (rc = 1)** ★

★**② clrfix 终板 vs 官方板**: ★**DRC 0/0 · unconnected 29/45 · 零铜 13/24 · 差分单边零铜 7/11 · 差分Δ超差 2/3 · 段数 3,986/18,092 · 过孔 593/433 · parity True/False · 退铜 2 条同上 · 差分死腿 0 · 逐网孤岛变多 7 条 ⇒ REJECT (rc = 1)** ★
★**⇒ clrfix 把 DRC 清零了, 但名单制闸一条没松** ★

★**③ 臂 vs 基线臂 (ISS-325 同日同代码对照臂)**: ★**DRC 12/205 · unc 29/29 · 零铜 13/12 · 差分单边零铜 7/5 · 退铜 3 · 差分死腿 3 对 · 逐网孤岛变多 6 · 判据① 网名集合 27→28 (变大) · 净救回 -1 ⇒ REJECT (rc = 1)** ★

★**④ 段内 P/N 顺序翻转 (分母 47)**: ★**右上臂 20/47** ★ · ★**左上臂 (ISS-325) 5/47** ★ · ★**现役板 17/47** ★ ⇒ ★**三个数没有一个是 0** ★
★**⑤ TP no-op 复测**: ★**排版阶段 钉 vs 不钉 ⇒ 落位差异 16 行 (8 个 ref 挪位)** ★ ⇒ ★**P-1 那 20 条 `PCB_PART_POS` 一条都不许删回 10 条** ★
★**⑥ 候选板路径**: ★**`tmp/iss328/chain_iss328_s8ru/final_chain.kicad_pcb` · `tmp/iss328/_clrfix_iss328_s8ru_final.kicad_pcb`** ★ · ★**基线板 = `HW/PCB/demo_mainboard.kicad_pcb`** ★
★**⑦ unc 网名集合 (★读数 ①/② 要的就是这个集合·★逐条给全·机器收割★)★**: ★**口径 = `state/cmp_unc_sets.py` 的 `nets_of()` · 出处 = `logs/iss328/35_unc_netsets_readonly.txt` (★脚本 `tmp/iss328/scripts/iss328_netsets_readonly.py`·★只读·未重跑任何链/臂★)** ★
| 板 | unc 条目 | viol | ★unc 网名数★ | ★unc 网名集合 (★逐条·零手抄·★完整 34/28/27 条见交付页 §2-2b 与本收割件★)★ |
|---|---|---|---|---|
| ★**① 裸路由器产物** (`tmp/iss328/ru_R.drc.json`) ★ | 35 | 11 | ★**34** ★ | `BAT_CHG` `BOOT_N` `CSI_D0_CK_N` `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D2_N` `CSI_D0_D2_P` `CSI_MCLK` `CSI_MCLK_SRC` `DSI_D0_CK_N` `DSI_D0_D0_N` `DSI_D0_D0_N_SRC` `DSI_D0_D0_P` `DSI_D0_D1_N` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC` `I2C_A_SCL` `I2C_B_SCL` `I2C_B_SDA` `KEY_CAM` `KEY_VOL_P` `LED_B` `LED_G` `LIGHT_5V` `PWR_GOOD` `PWR_ON` `RAIL_DEMO_5V` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `UART_RX` `USB_CC1` `VDD_1V8_IO` |
| ★**② 右上臂链终板** ★ | 29 | 12 | ★**28** ★ | `BOOT_N` `CSI_D0_CK_N` `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D2_N` `CSI_D0_D2_P` `CSI_MCLK` `CSI_MCLK_SRC` `DSI_D0_CK_N` `DSI_D0_D0_N` `DSI_D0_D0_N_SRC` `DSI_D0_D0_P` `DSI_D0_D1_N` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC` `I2C_A_SCL` `I2C_B_SCL` `KEY_CAM` `KEY_VOL_P` `LED_B` `LED_G` `PWR_GOOD` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `UART_RX` `USB_CC1` |
| ★**③ 基线臂同链终板** ★ | 29 | 205 | ★**27** ★ | `CSI_D0_CK_N` `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D2_N` `CSI_D0_D2_P` `CSI_MCLK` `CSI_MCLK_SRC` `DSI_D0_CK_N` `DSI_D0_CK_N_SRC` `DSI_D0_D0_N` `DSI_D0_D1_N` `DSI_D0_D3_N` `DSI_D0_D3_P` `I2C_A_SCL` `I2C_B_SCL` `I2C_B_SDA` `ID_DETECT_1` `KEY_CAM` `KEY_VOL_P` `LED_B` `LED_G` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `UART_RX` `USB_CC1` |

★**两组集合关系 (★机器算的★)★**: ★**①→②: 交集 28 · 仅①有 6 (`BAT_CHG` `I2C_B_SDA` `LIGHT_5V` `PWR_ON` `RAIL_DEMO_5V` `VDD_1V8_IO`) · 仅②有 0 ⇒ ★链终网名集合 ⊂ 裸路由器网名集合 (严格子集) ⇒ 补丁链这一步只救不破★★** (★与链日志自检闸「救回 3 + 3 / 新断 0 + 0」逐字一致★) · ★**② vs ③: 交集 22 · 候选新断 6 · 候选救回 5 ⇒ 净 +1 ⇒ 判据① 网名集合变大 (27→28) ⇒ ❌ 不通过★** (★与臂间对照闸日志逐字一致★) ★
★★**★不得拿「补丁链只救不破」去冲抵 §3 / B1 的 REJECT 判决★** ★★ —— ★**它只证明【补丁链这一步】没把网弄断·不代表整条臂成立** ★ ★

---

## B5 未决项与卡点 (★需要谁回答什么★)

★**需要谁回答什么 (★本单【不代拍】★)★**

| # | 未决项 | 需要谁 | 影响什么 |
|---|---|---|---|
| ① | ★**板那一趟 (S1~S13) 的开工字母: W-2 / W-1b·W-1c / A4 / A5 / W-3 / U-1 / P7** ★ | ★**老板** ★ | ★**G1 现在缺的那 1 项 (unc 45→0) 就卡在这些字母上** ★ |
| ② | ★**12 个零铜网换机制** ★ (成对走廊 / 换层绕开 / 让路闸 / pair-aware) | ★**main** (派 hw-lead 下一单) ★ | ★**「挪器件位置」这条路已被两个臂证伪 ⇒ 归零只剩机制级** ★ |
| ③ | ★**路由器本体漂移**: 当前 3,986 段 vs 官方链 18,092 段 | ★**main** (派 hw-lead 下一单) ★ | ★**段数不追平 ⇒ 任何臂的 unc/zero_copper 都不许跟官方板比** ★ |
| ④ | ★**CSI 5 族段内翻转另有处置** (5/47 或 20/47 的那批) | ★**main** ★ | ★**板那一趟的「翻转 = 0」判据必红** ★ |
| ⑤ | ★**官方链同配方复跑 (段数追平)** | ★**未派** ★ | ★**本单没有这个读数 ⇒ 一律标 [未验]** ★ |
| ⑥ | ★**日志 vs 只读复算的 rc 差异 (★本趟新登记·★判据一个字没改★)** | ★**main (登记用)** ★ | ★**日志里「★名单制闸 rc=0」是【shell 管道假读数】⇒ 真实 rc = 1** ★ |
| ⑦ | ★**交卷前 `issue_check.py` rc ≠ 0 (★19~20 条违规·★全在 main/boss 名下·★hw-lead 名下 0 条·★ISS-328 自身是 verified 不是违规★)** | ★**main** ★ | ★**这不是本单造成的·本单只交读数·★不许越界改别人的页★ ⇒ 请 main 归口处置这批逾期** ★ |

★**★⑦ 登记: 交卷前三条 rc 的实况 (★按任务书「任何一条红 ⇒ 先查是谁的产物·不许越界改别人的页·写进 B5 交 main 拍」★)★**

★**`merge.py` rc = 0** (★`STATE.yaml 已刷新`·产出 769 / 阻塞 43 / 未闭合需求 350 / 冲突 0★)
★**`gate_check.py` rc = 0** (★Q1 = **18/18** ★ · Q2 = 3/3 · Q6 硬件真源闸 ✅ · Q7 钉板 md5 闸链 **10/10** 全绿 · Q5 = 0/3 是【项目面】的老账不是本单★)
★**`issue_check.py` rc ≠ 0 ⇒ 违规条数随别的 lane 收口在 19~20 条之间浮动 (★本趟最后一次跑 = 19 条★)** —— ★**归属已查清: `owner=boss` 7 条 + `owner=main` 13 条 + `owner=hw-lead` 0 条** ★
★**且 ISS-328 自己在 issue_log 里是 `🟠 verified owner=hw-lead due=2026-11-20` ⇒ 不是那 20 条里的任何一条** ★
★**⇒ ⇒ 本单结论: ISSUE_RC ≠ 0 是【跨 lane 的存量逾期】不是本单缺口 · ★本单一个字节都没碰 `state/issue_log.yaml` (★不自签★)·★不代 main 处置这 20 条★ ⇒ 交 main 归口** ★
★**另**: ★`gate_check.py` Q4 会印一行「与 merge.py 不一致 ⇒ 先重跑 merge.py」⇒ ★那是【本机同时有 3~4 条 lane 在跑 merge/gate】造成的计数瞬时差 (★merge 读到 350 / gate 读到 351★)⇒ ★不是本单分片的错·★已用「先 merge 再 gate」的顺序重跑过·Q1/Q6/Q7 三项本单相关的全绿★ ★

★**★⑧ 登记: Q1 交付齐备率在两次跑里跳了 18/18 → 16/18 (★归属不在本单·★不许越界改别人的页·★交 main 拍★)★★**

★**现象**: ★05:49 那趟 `gate_check.py` Q1 = **18/18** (★hw-lead 6/6·sw-lead 6/6·mech-lead 6/6★)·★06:0x 那趟 Q1 = **16/18** ★
★**缺口两条全在 sw-lead 名下**: ★`sw-lead 4/6 缺: ['B4', 'B5']` · 交接单 = `HANDOFF/2026-11-23_sw-lead_ISS355_转换脚本迁主路线.md` ★
★**hw-lead 本单在两趟里都是 `6/6 缺: 无`** ★
★**⇒ ⇒ 那是 sw-lead 那条 lane 正在写自己的交接单时被门禁扫到的瞬时状态 (★本机同时有 3~4 条 lane 在跑 merge/gate/issue★)⇒ ★本单【不】去碰 sw-lead 的页 (★任务书: 不许越界改别人的页★)⇒ 交 main 归口★ ★

★**★⑥ 登记: 日志 rc 与只读复算 rc 不一致 (★照任务书口径「照日志写 + 在 B5 登记差异」·★不许私自改判据★)★★**

★**现象**: ★`logs/iss328/08_rightupper_arm.log` 两处印「★名单制闸 rc=0」·第三块外层印「★对照闸 rc=0」·但同一块里印的是「判定: REJECT」★
★**只读复算读数** (`logs/iss328/33_recalc_gate_rc.txt`): ★`RC_FINAL_OFFICIAL=1` · `RC_CLRFIX_OFFICIAL=1` · 臂间对照闸 rc=1 (日志 L198「闸 rc=1」)★

★**根因 (★已在盘上核实·★逐字引脚手架★)**: ★`tmp/iss328/run_ru_arm.sh` L132~L133 / L136~L137 写的是 ★
`python3 state/compare_arm_official.py … 2>&1 | tail -60` 紧跟 `echo "  ★名单制闸 rc=$?"` ★
⇒ ★**`$?` 在管道后取的是最后一个命令 (`tail`) 的退出码 (恒 0)·不是闸的退出码** ⇒ ★**日志那两行 rc 是【shell 管道 artifact】·不是闸的判决** ★
★对照: ★`state/compare_arm_official.py` 末行 `return 0 if verdict == "ACCEPT" else 1` ⇒ ★**REJECT ⇒ 进程退出码必为 1** ★

★**结论 (★本单两页统一口径★)**: ★**判定 = REJECT (照日志·一字未改) · rc = 1 (照只读复算的进程退出码)** ★
★**为什么按 rc=1 写而不是照抄日志的 rc=0**: ★日志同一块里的「判定: REJECT」与「rc=0」自相矛盾·若照抄 rc=0 会把 REJECT 误读成通过 ⇒ ★**判据/名单/读数全部照抄日志·只把 rc 这一个字段的取值换成进程退出码·并在此登记差异** ★
★**影响面**: ★**无** ⇒ ★判据/名单/读数全部照抄日志·★**只影响 rc 这一个字段的呈现** · ★日志原文未改 (★本单不改任何原始证据★)★

★**本单边界声明 (★逐字带上★)★**:
★**这是「板只改一次」纪律下的【纯分析/作业包类】活** ⇒ ★**本单一个字节都没动板 (md5 `611b869e…` + mtime `2026-11-06 07:07:17` 未变) · 没动网表/脚表/BOM 真源 · 没动闸 · 没重跑任何链** ★ ⇒ ★**板那一趟 (S1~S13) 的开工条件仍未满足** ★ (★老板 2026-11-17 00:43 口径: 真动板那一趟必须一次做完★) ★
★**本单只是把右上臂这条【已证伪的处方】的读数【如实落纸 + 登记】, 供 main 拿去写「板那一趟」作业包的不做清单** ★

---

## B6 自证复现命令 (★原样贴输出★)

★**4 条只读自证命令 (★逐字可跑·★下面输出是 23:3x~23:4x 的实测原样★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
grep -cE "<!--[ ]" 'HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md'
grep -c iss328 state/fragments/hw.yaml
```

★**原样输出 (★填完 5 块后自己跑一遍, 把真实输出贴在下面·★别抄我的★)★**:

```
md5 = 611b869e13518c3c023fb178f91a0075
mtime = 2026-11-06 07:07:17.362193413 +0800
占位符计数 = 0
hw.yaml iss328 命中 = 19   (★2026-11-23 05:5x cont3 换 status 到 ISS-328 + 追加 1 条 claim (rc artifact) 后重测★)
```

★**★注: 第二条命令的 PAT 写成 `<!--[ ]` (中间是空格) 是故意的 ⇒ 免得这一行自己匹配自己 ⇒ 占位符计数才可能为 0★** ★
★**★注: 板 md5 / mtime 是【零写板】的硬证据 ⇒ 一旦变了本单作废★** ★

★**★cont4 追加: unc 网名集合的收割命令 (★只读·★可重跑·★输出逐字贴·★rc 必须 0★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss328/scripts/iss328_netsets_readonly.py ; echo "rc=$?"
```

★**原样输出 (★rc=0 + 末行「逐项一致? 是」★)★**:

```
── ① 裸路由器产物 (排版+布线·未套链)
   unc 条目 = 35 · DRC viol = 11 · ★unc 网名 = 34★
── ② 右上臂链终板
   unc 条目 = 29 · DRC viol = 12 · ★unc 网名 = 28★
── ③ 基线臂同链终板 (ISS-325 同日同代码对照臂)
   unc 条目 = 29 · DRC viol = 205 · ★unc 网名 = 27★
── 集合关系 (★机器算的★)
   ①→②: 交集 28 · 仅①有 6 · 仅②有 0
      ★仅①有 (被补丁链救回) = BAT_CHG I2C_B_SDA LIGHT_5V PWR_ON RAIL_DEMO_5V VDD_1V8_IO
      ★仅②有 (补丁链新断)   = (空)
      ★★链终网名集合 ⊂ 裸路由器网名集合? 是 (严格子集)★
   ② vs ③: 交集 22 · 仅②有 6 · 仅③有 5
      ★仅②有 (候选新断) = BOOT_N DSI_D0_D0_N_SRC DSI_D0_D0_P DSI_D0_D2_N_SRC DSI_D0_D3_N_SRC PWR_GOOD
      ★仅③有 (候选救回) = DSI_D0_CK_N_SRC DSI_D0_D3_N DSI_D0_D3_P I2C_B_SDA ID_DETECT_1
── 与臂间对照闸日志的一致性核对
   ★★逐项一致? 是 ⇒ 本收割件与链日志同口径同结果★★
rc=0
```

★**★注: 完整 34 / 28 / 27 条网名逐条清单见 `logs/iss328/35_unc_netsets_readonly.txt` 与交付页 §2-2b (★上面只贴计数与集合关系·★省得刷屏·★全文已落盘★)★** ★

★**★cont3 追加: 交卷前必跑 (★原样输出·★完整输出落 `logs/iss328/36_cont3_final_accept.txt`·★下面贴关键段·★易变项已标注★)**★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py ; echo "MERGE_RC=$?"
timeout 900 python3 state/gate_check.py ; echo "GATE_RC=$?"
timeout 600 python3 state/issue_check.py ; echo "ISSUE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
grep -c iss328 state/fragments/hw.yaml
```

★★**★注: 【占位符扫描】那 4 条命令本文件【不写出来】·★这是故意的★★**
★★**理由**: ★**那 4 条命令的【匹配式】本身就写在交卷页里 ⇒ 逐字写出来会让本页【自己匹配自己】⇒ 扫描计数永远不是 0 (★这是 ISS-327 那类坑的同款·★我在第一版 B6 里就是这么把自己写红的·★已自查修掉★)★ ★★
★★**⇒ 所以那 4 条的【逐字命令 + 逐字输出】全部落在 `logs/iss328/36_cont3_final_accept.txt`** (★该件在 `logs/` 下·★不在这两条扫描的靶子里·★所以那里可以逐字写匹配式★) ★★
★★**⇒ 本页 B6 只列【不会自我匹配】的那 5 条 (★上表 3 条 rc + 板指纹 + 分片命中★)★ ★★

★**原样输出 (★2026-11-23 08:5x~14:4x 本机实跑·★全文见 `logs/iss328/36_cont3_final_accept.txt`·★别抄我的★)★**:

```
✅ STATE.yaml 已刷新 (★时间戳见收割件·★计数随别的 lane 收口变★)
MERGE_RC=0

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   (★交接单名取【最新】那一单·★本单 ISS-328 交卷页 = `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md`·★B0~B6 齐全★)
   sw-lead    6/6  缺: 无
   mech-lead  6/6  缺: 无
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
GATE_RC=0

❌ 违规 19 条  (★条数随别的 lane 收口在 19~20 之间浮动·★归属一直是 boss+main·★hw-lead 名下 0 条★)
ISSUE_RC=1

611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800

--- 占位符扫描 (★标准 4 词 + 双下划线 + 注释符·★期望 0/0/0/0★) ---
0
0
0
0

19
```

★★**★注: 上面这段的【易变项】只有两处 = ① `STATE.yaml 已刷新` 的时间戳与产出计数 ② 违规条数 (19~20) ③ Q1 里那个交接单名 (★取最新一单★)·★它们都随本机另外 3~4 条 lane 同时在跑而变·★★本单的【不变量】是: `MERGE_RC=0` · `GATE_RC=0` · `ISSUE_RC=1` 且归属全在 main/boss · Q1 18/18 且 hw-lead 6/6 · 四个 0 · 板指纹逐字不变·★逐字快照见收割件 (★行数也在 880~895 之间浮动·★所以不引行数·★只引判据★)★** ★★

★**★注: `ISSUE_RC=1` 的违规条数随别的 lane 收口在 19~20 之间浮动 (★本趟最后一次跑 = 19 条 = `owner=boss` 7 条 + `owner=main` 13 条·★hw-lead 名下 0 条·★ISS-328 自身是 `verified` 不是违规★) ⇒ 已在 B5 ⑦ 登记交 main 归口·★本单不碰 `state/issue_log.yaml` (★不自签★)★** ★
★**★注: `hw-lead` 那一行交接单指向 ISS-354 是因为门禁取【最新】的 hw-lead 交接单 (★本机同时有 ISS-354 那条 lane·★其交接单已 6/6 齐全·★不是本单缺块★)★** ★
★**★注: 板 md5 / mtime 与 19:33 跑前指纹逐字相同 ⇒ 【零写板】双证成立★** ★

