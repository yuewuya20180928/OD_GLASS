# ISS-251 · MECH 侧三处老账收口（mech-lead · 2026-11-16 19:4x 续做轮）

> **交卷人**: mech-lead（结构总工 · 带散热）🔩 · **落盘**: 2026-11-16 19:4x (Asia/Shanghai)
> **单号**: ISS-251（MECH 侧三处老账收口 · **续做重派**）
> **上一轮怎么死的**: 会话 `agent:mech-lead:subagent:6348eece-…` 19:19:42 起 → **19:29:40 被 runTimeout 掐断**（runtime 596s, abortedLastRun=true）⇒ transcript 末条 = exec 返回「Aborted」⇒ **它在改文档的半路上被掐**（那一轮只改了 `MECH/SERVICE_PORT_ISS092.md`，mtime 19:25:58；**交卷层 + 新门禁一件没落** ⇒ 等于白干）。
> **本轮只补缺口**: 三处老账**上一轮已落 2 处半**（本轮只核对 + 补出处/行号，**不重复改**）⇒ 本轮补的是 **① 逐条订正表 ② 新机器门禁 ③ 交卷单 ④ 分片 ⑤ 并发说明一行**。

---

## B1. 结论摘要（一句话）

**三处老账的口径全部对齐并机器化固化**: **A** 充电耗散 = **buck 0.45-0.57 W（代表值 0.50 W）** · **B** 金属热路 k = **201 W/m·K**（6063-T6 官方保守侧）· **C** 检修口 = **60×30 板 + 套 A 基准（P2 Y=15.00 / S2 Y=20.00）**; 本轮 **0 个 MECH/HW 文件改动**（三处口径本轮只核对不重复改），新建 1 个口径门禁（**rc=0 17/17**，`--selftest` **rc=0 13/13** 反向用例四类全抓到），交卷层三件（**订正表 + 门禁 + 分片**）一次补齐 ⇒ **上一轮"改了文档没交卷"的坑补上了**。

---

## B2. 验收标准自评（逐条 通过/不通过/未验）

| # | 验收项 | 自评 | 实测输出 / rc |
|---|---|---|---|
| A1 | `python3 MECH/verify_budget.py` | ✅ **通过** | **rc=0** · 「✅ 门禁绿: 全部数值对拍一致 + 充电耗散口径 = buck (非线性 0.8W)」 |
| A2 | `python3 MECH/check_budget_caliber.py`（**本轮新建**） | ✅ **通过** | **rc=0** · 「检查项 **17** | 通过 **17** | 红 **0**」 |
| A3 | `python3 MECH/check_budget_caliber.py --selftest` | ✅ **通过** | **rc=0** · 「反向用例: **13/13** 抓到了」（四类全覆盖，见附 A-末） |
| A4 | `python3 MECH/service_port_check.py` | ✅ **通过** | **rc=0** · 「【结论】**54/54** 项一致 | FAIL **0** 项」 |
| A5 | `python3 MECH/check_demo_struct_truth.py` | ⚠️ **不属本单（并发落表）** | **rc=2** · 「【结论】**21/23** 组检查通过 | FAIL **2** 组」= **[FAIL] G5b**（受保护文件 md5 逐字节未变: 板/.kicad_pro + 4 个 check 脚本 + 网表/脚表）+ **[FAIL] C21**（真源变更台账对账: 锚点 ↔ 落表台账 ↔ 盘上真源 三方一致）; 根因 = `HW/netlist_v1.csv` 盘上 md5 **`16ac89f77c25a3f61834cc7ebcd78a7f`** ≠ 脚本锚点 `611c3ba3…` ⇒ **hw-lead 的 ISS-249 落表造成的 md5 变化，不是我的失败，我一个字节没碰 HW/，也没碰这个受保护脚本**（详见 **附 B 并发说明**） |
| A6 | `python3 state/merge.py && python3 state/gate_check.py` | ✅ **通过** | **rc=0** · **Q1 18/18** |
| A7 | 受保护脚本逐字节不变 | ✅ **通过** | `md5sum` ⇒ `check_demo_struct_truth.py` **fa9b59e593a13408ad9505d986276f63**（基线 `fa9b59e5…` ✅）· `service_port_check.py` **9b24bf985764880f0105aee677fba6a8** · `hinge_usb_check.py` **3425bc141508de8a35f34c7cf7b803e8** ⇒ **本轮 0 改动** |
| A8 | 三处老账逐条订正表（旧值→新值 + 文件 + 行号 + 证据等级 + 依据出处） | ✅ **通过** | **附 A** · A 组 7 条 / B 组 6 条 / C 组 9 条 |
| A9 | 分片写入（必须走 `state/frag_write.py` 原子写） | ✅ **通过** | `python3 state/frag_write.py --agent mech-lead …` ⇒ 「✅ mech.yaml 已原子更新」+ **5 artifact / 5 claim / 4 need** |
| A10 | 边界审计（不碰 HW/、不碰受保护脚本、不改 `PROJECT_TRACKER.md` §0、不自签 `issue_log.yaml`、零外发、不替老板拍板） | ✅ **通过** | 本轮**新增/改动文件只有 3 个**（本单新增 2 + 分片 1），**HW/ 零改动**（`netlist_v1.csv` md5 保持 `16ac89f7…`，由 hw-lead 落表，不是本单） |
| A11 | `MECH/check_budget_caliber.py --selftest` 反向用例覆盖四类 | ✅ **通过** | ① 改回旧口径 **4 条** · ② 改数字 **4 条** · ③ 删依据出处 **2 条** · ④ 改文档数字 **3 条** = **13 条，全抓到** |
| A12 | 新门禁只判口径、不越界到别的域 | ✅ **通过** | 门禁只读 `MECH/verify_budget.py` / `MECH_BUDGET.md` / `SERVICE_PORT_ISS092.md` / `ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` 四个文件的**文本锚点**; **不重算** `verify_budget.py` 的数值对拍、**不碰** `HW/`、**不碰** 三个受保护脚本 |

**自评口径**: 12 条里 **11 条通过 + 1 条（A5）明确判为「非本单并发落表」**; **没有任何一条写"应该能过"** —— 每条都贴了实跑 rc。

---

## B3. 证据分级（实测/官方/推算/0数据）

| 结论 | 证据等级 | 依据出处（可点开） |
|---|---|---|
| 板上充电拓扑 = **开关型 buck**（不是线性充电 IC） | **[实测]**（网表实读） | `HW/netlist_v1.csv` P10 实读 `U_CHG / SW / L_CHG / C_BST / PMID` ⇒ 开关型变换器; 5V→3.7-4.2V 时 D<1 ⇒ 降压档 |
| 充电器件 = **BQ25896** · K_ILIM 320/355/390 A·Ω · η 0.90 | **[官网]** | TI BQ25896 datasheet（脚本 `MECH/verify_budget.py` L80-84 逐条列输入） |
| 充电耗散 **0.45-0.57 W**（代表值 **0.50 W**）= Pin − Pout + P_DCR | **[推算]**（三档复算 0.46/0.52/0.57 W） | `MECH/verify_budget.py` L86-89 + `MECH_BUDGET.md` L597/L698-699 |
| 旧口径 **(5−4.2)V × 1A = 0.8 W**（线性充电 IC）**已判死** | **[文档核对]** | `MECH_BUDGET.md` L604-605（标「已判死 (历史沿革, 不再是活口径)」）; `MECH/verify_budget.py` L15-17 头注 |
| 铝 6063-T6 **k = 201 W/m·K**（官方保守侧） | **[官网]** | Hydro EN AW-6063 `Hydro 6063_Rev.4 – 03/2023` + Aalco 6063-T6 datasheet + Kaiser 6063 Rev. 05/06 **三家官网互证**（`MECH/verify_budget.py` L97-111 附三条 URL; `MECH_BUDGET.md` L707/L1017/L1092; `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` L40/L230） |
| 旧 **k = 237**（项目内乐观值）只留追溯 | **[文档核对]** | `MECH/verify_budget.py` L112（`K_AL_6063_T6_LEGACY` + 「只留追溯」）; `MECH_BUDGET.md` L519/L707/L875/L1017/L1092 全部标「旧口径 / 已订正」 |
| 同几何热阻 **R 1.641 → 1.935 K/W** · ΔT **+0.82 → +0.97 K** · A_min **4.2194 → 4.9751 mm²** ⇒ **2.0×2.0 铝条仍不合格** | **[推算]** | `MECH/verify_budget.py` L116-122 |
| 检修口板宽口径 = **60×30**（板长 60 / 板宽 30 / 板厚 1.0 / 6 层） | **[官方]**（板框）+ **[文档核对]** | `MECH/BOARD_GEOM_30MM.md` §1（板框）/ §3（PIN-SET-2 套 A 孔心）; ISS-206 已确认 `HW/pcb60x30_check.py` 同值 |
| 夹具基准 = **套 A**（P1 8.00/15.00 · P2 52.00/**15.00** · S1 8.00/10.00 · S2 52.00/**20.00**） | **[官方]** | `MECH/BOARD_GEOM_30MM.md` §3 表 + §4 仲裁（套 B 已否决） |
| §5.1 V PCB 段 = 需求 **36.00** / 余 **+2.00** / 最坏 **+1.40**（单边口径 +1.70） | **[推算]**（公差栈） | `MECH/SERVICE_PORT_ISS092.md` L19/L200/L201; 镜脚截面锁死值 H 7.30 / V 38.00 / L 130.00 **一毫米不动** |
| ★**焊盘阵列 Y 起点 9.50（开口 Y 8.67..13.27）仍按旧 15mm 板基准** | **[0数据]**（最终值未定）+ 已如实标注 | `MECH/SERVICE_PORT_ISS092.md` L89 明写「本行 Y 仍是旧 15mm 板基准 ⇒ 本单不改这两个数」+ 登记 need `iss251_mech_service_port_pad_y_migrate` |
| 实物 | **[0数据]** | **0 件打印 / 0 台样机**; 镜脚末端 V 净高、座体型号、磁铁拉脱力、麦克风磁场敏感度、IP 全无实测 |

---

## B4. 接口取值声明（interface_claims）

| key | value | 说明 |
|---|---|---|
| `iss251_mech_charge_dissipation_caliber` | **buck 0.45-0.57 W（代表值 0.50 W）** | 板上器件 BQ25896（开关型 buck）; 旧线性 0.8 W 已判死; 三处同源: `MECH/verify_budget.py` L86/L89 + `MECH_BUDGET.md` L597 + 机器门禁锚点 `check_demo_struct_truth.py` `anchors.thermal.p_buck_w=0.50` |
| `iss251_mech_al_k_caliber` | **201 W/m·K（6063-T6 官方保守侧）** | 活口径 201（Hydro/Aalco/Kaiser 三家官网互证）; 237 只留追溯; **只改口径不改结论**（热路仍必须金属 / 打印件仍出局 / 2.0×2.0 铝条仍不合格） |
| `iss251_mech_service_port_board_caliber` | **60×30 板 · 套 A（P2 Y=15.00 / S2 Y=20.00）** | §1 PCB 行 60 (L) × 30 (V) × 1.0 (6 层); 夹具基准复用套 A **不新增基准孔**; ★焊盘阵列 Y 起点 9.50 仍按旧基准（受保护脚本不许动 ⇒ need） |
| `iss251_mech_caliber_gate_contract` | **rc=0 17/17 · --selftest rc=0 13/13** | 本单新建门禁的契约（交卷后不变）: `python3 MECH/check_budget_caliber.py` ⇒ rc=0 且 17/17; `--selftest` ⇒ rc=0 且 13/13 反向用例全抓到; **只判口径**, 不重复 `verify_budget.py` 的数值对拍, 不碰 HW/ 与三个受保护脚本 |
| `iss251_mech_protected_md5` | **fa9b59e5 / 9b24bf98 / 3425bc14** | 本轮 0 个受保护文件改动: `check_demo_struct_truth.py` **fa9b59e5…**（基线一致）/ `service_port_check.py` **9b24bf98…** / `hinge_usb_check.py` **3425bc14…** ⇒ 含夹具基准 Y / 焊盘阵列 Y / `pcb_thk` 常量一律没动 |

---

## B5. 未决项与卡点（需要谁回答什么）

| # | key | to | 卡点（逐条写清） |
|---|---|---|---|
| N1 | `iss251_mech_service_port_pad_y_migrate` | **main**（会同 hw-lead） | ★**检修口 C 处唯一未迁项** ⇒ `MECH/service_port_check.py` 里的 ① 夹具基准常量 `p2_y`/`s2_y`（现仍是旧 15mm 板口径 7.50/12.50）② J_DEBUG **焊盘阵列 Y**（现 Y 9.50..10.77 ⇒ 开口 Y 8.67..13.27 是按旧基准算的）③ `pcb_thk` ⇒ 三处都要迁到 30mm 板**套 A** 口径（P2 52.00/15.00 · S2 52.00/20.00）⇒ 迁完后 §5.1 开口 Y 与 P-5 最近距离 **3.23mm / 8.53mm** 都要重算 ⇒ ★**这三条常量在受保护脚本里，本单一个字没碰**（等 main 定版后由 main/hw-lead 落，或 main 授权我改并重基线 md5）⇒ 现状已如实标注在 `SERVICE_PORT_ISS092.md` L5/L89/L281/L322 |
| N2 | `iss251_mech_demo_truth_gate_red_concurrent` | **main** | ★**并发说明（不是本单失败，本单不许修）** ⇒ `MECH/check_demo_struct_truth.py` 现在 **21/23 · FAIL 2 组 = G5b / C21**，原因是 `HW/netlist_v1.csv` 盘上 md5 `16ac89f7…` ≠ 锚点 `611c3ba3…` ⇒ **那是 hw-lead 的 ISS-249 落表造成的 md5 变化** ⇒ 要 main 派 hw-lead 把 G5b/C21 的 md5 锚点重锚到 ISS-249 的现值（或 main 授权重基线）⇒ 在那之前该闸的 rc 必须是 2（21/23），**别当成绿** |
| N3 | `iss251_mech_owner_decisions_pending` | **main / 老板** | ★**只列选项 + 量化代价，一个字没代拍** ⇒ (a) **d 值**（遮挡计算用）15/18/20 mm: d=15 时集热背板 `W_rim` 门槛 **22.15 mm @0.468 W**（余量最小），d↑ ⇒ 门槛上移但集热面积/质量更贵 ⇒ (b) **u8 端件截面**: 现状 2.0×2.0 = **4.0 mm² 不合格**（R = 73.84 K/W > 70 判据），最小合格 **4.975 mm²** ⇒ **2.5×2.0 = 5.0 mm²**（R = 69.65 K/W，**只余 0.35 K/W**）⇒ (c) **集热面材质/面积**: 铝 6063-T6（k=201）vs 铜（k≈400，同截面 R 减半，质量约 +78%）⇒ (d) **板长**（60 现行 vs 更长）⇒ (e) **板厚档位**（1.0 mm 现行 / 0.8 mm 已作废）⇒ 依据见 `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` §2.5/§2.6 + `MECH_BUDGET.md` §2.3.1 |
| N4 | `iss251_mech_handoff_review` | **main** | ISS-251 交卷待 main 复核: 本交卷单（B1-B6 + 附 A 订正表 + 附 B 并发说明）+ 新门禁 `MECH/check_budget_caliber.py` + 分片 `state/fragments/mech.yaml`（走 `frag_write.py` 原子写，**5 artifact / 5 claim / 4 need**）⇒ 本轮 **0 个 MECH/HW 文件改动**（三处老账口径上一轮/早前已落，本轮只核对 + 补出处/行号）· 受保护 3 脚本 md5 逐字节不变 · 零外发 · **不自签 `state/issue_log.yaml`**（verify 留给 main）· 不替老板拍板 ⇒ **请 main 跑 verify** |

---

## B6. 自证复现命令（原样贴，rc 是实跑的）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/verify_budget.py                       # rc=0  (buck 口径已对拍)
python3 MECH/check_budget_caliber.py                # rc=0  (本轮新建 · 17/17)
python3 MECH/check_budget_caliber.py --selftest     # rc=0  (反向用例 13/13 全抓到)
python3 MECH/service_port_check.py                  # rc=0  (54/54 · FAIL 0)
python3 MECH/check_demo_struct_truth.py             # rc=2  (21/23 · FAIL 2 = G5b/C21 ⇒ 并发落表, 非本单)
python3 state/merge.py && python3 state/gate_check.py   # rc=0  (Q1 18/18)
md5sum MECH/check_demo_struct_truth.py MECH/service_port_check.py MECH/hinge_usb_check.py
# fa9b59e593a13408ad9505d986276f63  MECH/check_demo_struct_truth.py   ← 基线 fa9b59e5… 逐字节不变
# 9b24bf985764880f0105aee677fba6a8  MECH/service_port_check.py
# 3425bc141508de8a35f34c7cf7b803e8  MECH/hinge_usb_check.py
```

★**本单新增物只有 3 个文件**: `MECH/check_budget_caliber.py`（新门禁）+ 本交卷单 + `state/fragments/mech.yaml`（原子写）⇒ **三处老账的文档本轮一个字没改**（已落 ⇒ 只核对 + 补出处/行号）。

---

## 附 A. 三处逐条订正表（旧值 → 新值 + 文件 + 行号 + 证据等级 + 依据出处）

> 标注规则: **★已落 (出处: 行号)★** = 盘上已经是新值（注明是**哪一单/哪一轮**落的）· **★本轮补 (行号)★** = 本轮新写上去的。

### A 组 — 充电耗散口径（线性 0.8 W → buck 0.45-0.57 W，代表值 0.50 W）

| # | 旧值 → 新值 | 文件 | 行号 | 状态 | 证据等级 | 依据出处 |
|---|---|---|---|---|---|---|
| A-1 | 拓扑口径: 线性充电 IC → **开关型 buck** | `MECH/verify_budget.py` | **L77** `CHG_TOPOLOGY = "buck"` | ★**已落 (ISS-216 · 2026-11-16 02:34)** | [实测 网表 P10] | 网表实读 `U_CHG/SW/L_CHG/C_BST/PMID` ⇒ 开关型变换器 |
| A-2 | 耗散区间: 无 → **0.45-0.57 W** | `MECH/verify_budget.py` | **L86** `P_CHARGE_LO, P_CHARGE_HI = 0.45, 0.57` | ★**已落 (ISS-216)** | [推算] | 三档复算 0.46/0.52/0.57 W（IIN 0.82/0.91/1.00 A） |
| A-3 | 代表值: 0.8 W → **0.50 W** | `MECH/verify_budget.py` | **L89** `P_CHARGE = 0.50` | ★**已落 (ISS-216)** | [推算] | = ISS-213 机器门禁锚点 `anchors.thermal.p_buck_w` ⇒ 文档/脚本/门禁三处同一个数 |
| A-4 | 头注: 无口径声明 → 旧 0.8 W 线性公式**已判死** + 新口径写明 | `MECH/verify_budget.py` | **L14-19**（头注）+ **L31**（变更记） | ★**已落 (ISS-216)** | [文档核对] | 脚本自身头注 |
| A-5 | 文档 §2.1 峰值充电行: 线性 0.8 W @ 1A / MPS 料 → **开关型 buck BQ25896 / 0.45-0.57 W（代表值 0.50 W）/ Pin − Pout + P_DCR** | `MECH/MECH_BUDGET.md` | **L597** | ★**已落 (ISS-216 · 10:52)** | [推算]+[实测 器件/拓扑]+[官网 器件] | TI BQ25896 datasheet; 网表 P10 实读 |
| A-6 | 旧口径行: 无标注 → **「旧口径已判死 (历史沿革, 不再是活口径)」** | `MECH/MECH_BUDGET.md` | **L604-605** | ★**已落 (ISS-216)** | [文档核对] | 原文线性公式 (5−4.2)V × 1A = 0.8 W + MPS MP26029/MP2710/MP2721 全部作废 |
| A-7 | 耗散逐条输入 + 三档复算 + 旧行作废声明 | `MECH/MECH_BUDGET.md` | **L698-700**（0.45/0.57 + 0.46/0.52/0.57 复算 + 旧 75.1/136.2/151.2 °C 作废） | ★**已落 (ISS-216)** | [推算] | VBUS 5.0/η 0.90/R_ILIM 390 Ω/K_ILIM 320/355/390/R_DCR 50 mΩ/VBAT 3.70-4.20 V |
| A-8 | ★**旧口径残留兜底**: 旧线性标记只许出现在已判死/作废的行 | `MECH/verify_budget.py`（C7/C8）+ **`MECH/check_budget_caliber.py` A6** | verify_budget **L404-419**; 新门禁 **A6** | ★**本轮补 (新门禁 A6)** | [机器判定] | 本单新建门禁把这条**从"脚本自查"升级成"独立机器门禁"** |

### B 组 — 金属热路 k 口径（237 → 201 W/m·K，6063-T6 官方保守侧）

| # | 旧值 → 新值 | 文件 | 行号 | 状态 | 证据等级 | 依据出处 |
|---|---|---|---|---|---|---|
| B-1 | 活常量: k=237 → **k=201.0 W/m·K** | `MECH/verify_budget.py` | **L111** `K_AL_6063_T6 = 201.0` | ★**已落 (ISS-219 · 2026-11-16 02:34)** | [官网] | Hydro / Aalco / Kaiser 三家官网互证 |
| B-2 | 旧值留档: 无 → **237 只留追溯** | `MECH/verify_budget.py` | **L112** `K_AL_6063_T6_LEGACY = 237.0`（注释「只留追溯, 不许当活口径用」） | ★**已落 (ISS-219)** | [官网·已订正] | 同上 |
| B-3 | 热阻: R 1.641 → **R 1.935 K/W**; ΔT +0.82 → **+0.97 K**; A_min 4.2194 → **4.9751 mm²** | `MECH/verify_budget.py` | **L116-122**（`R_AL_201` / `A_MIN_R70_201` / 注释「2.0×2.0 铝条仍不合格」） | ★**已落 (ISS-219)** | [推算] | R = L/(k·A)，同几何 L=70 mm / A=180 mm² |
| B-4 | 文档 §1.9.3 k 口径行: 「k 口径 (旧口径 237 已订正) → **201**」 | `MECH/MECH_BUDGET.md` | **L519** | ★**已落 (ISS-219 · 10:52)** | [官网] | 同 B-1 三家互证 |
| B-5 | 文档四处 k 值统一 201 | `MECH/MECH_BUDGET.md` | **L707**（§2.3.1 端件热路 + 三家互证出处）· **L875**（§3 重量注）· **L1017**（材料选型表）· **L1092**（量产工艺表） | ★**已落 (ISS-219)** | [官网]+[推算] | 同 B-1; 每处都标「旧口径 237 只留追溯 / 已于 ISS-219 订正」 |
| B-6 | 模板表 A/B/C: 现口径列 **201** / 旧口径列 237 标「已订正, 只留追溯」 | `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` | **L40**（201 现口径 + 三家互证）· **L41**（237 旧口径·已订正）· **L45**（口径订正说明）· **L55-56**（A_min 4.219 / 4.975）· **L230**（证据表） | ★**已落 (ISS-219 · 06:23)** | [官网]+[推算] | 同 B-1 |
| B-7 | ★**237 漂回兜底**: 文档里 237 只许出现在已订正/旧口径行 | `MECH/verify_budget.py`（C11）+ **`MECH/check_budget_caliber.py` B4** | verify_budget **L420-431**; 新门禁 **B4** | ★**本轮补 (新门禁 B4)** | [机器判定] | 新门禁 B3+B4+B6 三条合起来守住「活口径 201 + 出处不丢」 |

### C 组 — 检修口文档板宽口径（15 mm → 60×30 现行板）

| # | 旧值 → 新值 | 文件 | 行号 | 状态 | 证据等级 | 依据出处 |
|---|---|---|---|---|---|---|
| C-1 | 旧 15 mm 板 → **现行 60×30**（板长 60 / 板宽 30 / 板厚 1.0 / 6 层） | `MECH/SERVICE_PORT_ISS092.md` | **L36** §1 边界表 PCB 行 | ★**已落 (ISS-206; 上一轮 19:25 复核)** | [官方]+[文档核对] | `MECH/BOARD_GEOM_30MM.md` §1; `fit_check.py` 的 `pcb_l=50` 与板厚 0.8 均作废 |
| C-2 | §5.1 V PCB 段: 旧口径 (+17.00) → **需求 36.00 / 余 +2.00 / 最坏 +1.40（单边口径 +1.70）** | `MECH/SERVICE_PORT_ISS092.md` | **L200**（V PCB 段）· **L201**（V + 检修口） | ★**已落 (ISS-206; 上一轮 19:25 复核)** | [推算 公差栈] | 板宽 30 + 走线槽 6.0 = 36.00; 镜脚 V 38.00 锁死不动 |
| C-3 | §0 结论 #3 的余量叙述: 旧 → **余量 0.95 / 2.00 / 14.50 一字不改** | `MECH/SERVICE_PORT_ISS092.md` | **L19** | ★**已落 (上一轮 19:25)** | [推算] | 镜腿三条锁死尺寸链 H 7.30 / V 38.00 / L 130.00 |
| C-4 | 夹具基准: 旧 15 mm 板基准 (P2 Y=7.50 / S2 Y=12.50) → **套 A (P2 52.00/15.00 · S2 52.00/20.00)** | `MECH/SERVICE_PORT_ISS092.md` | **L22**（§0 结论 #6）· **L281**（§7 P-5 夹具基准孔）· **L322**（§9 冲突复核 #11） | ★**已落 (上一轮 19:25)** | [官方] | `MECH/BOARD_GEOM_30MM.md` §3 套 A 表 + §4 仲裁（套 B 已否决）; ISS-206 已确认 `HW/pcb60x30_check.py` 同值 |
| C-5 | 旧 15 mm 口径全部显式标作废/已订正 | `MECH/SERVICE_PORT_ISS092.md` | **L4**（板宽 15 已作废）· **L34**（`BOARD_WIDTH_15MM.md` 只留追溯 + 来源指针改指现行权威表）· **L36**（板宽 15 / 板厚 0.8 作废）· **L83**（Y 0..30; 原 15 mm 板口径已作废）· **L192**（基线行: `board_width_15mm_check.py` 口径已作废）· **L281/L322**（旧 7.50/12.50 下是 1.00/1.03 mm，已作废） | ★**已落 (上一轮 19:25)** | [文档核对] | ISS-206 订正 |
| C-6 | ISS-251 口径订正范围声明（本件只订文档，不碰脚本常量） | `MECH/SERVICE_PORT_ISS092.md` | **L5** | ★**已落 (上一轮 19:25)** | [文档核对] | 明写「`service_port_check.py` 的夹具基准常量 / 焊盘阵列 Y / `pcb_thk` 本单一个字节没改」+ need `iss251_mech_service_port_pad_y_migrate` |
| C-7 | ★**唯一未迁项如实标注**（不是漏改）：开口 Y 8.67..13.27 仍按旧 15 mm 板基准（焊盘阵列 Y 起点 9.50 未迁） | `MECH/SERVICE_PORT_ISS092.md` | **L89** | ★**已落 (上一轮 19:25) · 本轮核对无漏** | [0数据]（最终值未定） | 本单**不改**（受保护脚本地界）⇒ 登记 need N1 |
| C-8 | ★**本轮补: 机器门禁把 C 组钉住**（板 60×30 / 套 A 基准 / §5.1 余量 / 旧 15 mm 只许标死 / 出处指针不丢） | `MECH/check_budget_caliber.py` | **C1-C5** | ★**本轮补** | [机器判定] | rc=0 17/17; 反向用例 4 条覆盖 C 组 |
| C-9 | ★**本轮补: 交卷层三件**（订正表 = 本表 / 新门禁 / 分片） | `HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md` · `MECH/check_budget_caliber.py` · `state/fragments/mech.yaml` | 本文件 / 新建 / 原子写 | ★**本轮补** | [机器判定] | 上一轮被 runTimeout 掐在改文档半路上 ⇒ 交卷层一件没落; 本轮补齐 |

### 附 A-末 · 新门禁反向用例清单（`--selftest` rc=0 · 13/13 全抓到）

| 类 | # | 变异 | 期望红组 | 实测 |
|---|---|---|---|---|
| ① 改回旧口径 | 1 | 脚本 `CHG_TOPOLOGY` buck → linear | A1 | ✅ A1 |
| ① 改回旧口径 | 2 | 文档 §2.1 行退回「线性充电 IC / 0.8 W @ 1A」（未标作废） | A6 | ✅ A5+A6 |
| ① 改回旧口径 | 3 | 文档 `k=**201**` → `k=**237**` | B3 | ✅ B3 |
| ① 改回旧口径 | 4 | 检修口板口径 60×30 → 50×15 | C1 | ✅ C1 |
| ② 改数字 | 5 | 脚本 `P_CHARGE` 0.50 → 0.55 | A3 | ✅ A3 |
| ② 改数字 | 6 | 脚本区间 0.45-0.57 → 0.30-0.60 | A4 | ✅ A4 |
| ② 改数字 | 7 | 脚本 `K_AL_6063_T6` 201.0 → 237.0 | B1 | ✅ B1 |
| ② 改数字 | 8 | 检修口夹具基准 P2 Y 15.00 → 7.50 | C2 | ✅ C2 |
| ③ 删依据出处 | 9 | 脚本里 Aalco 互证出处两行删掉 | B6 | ✅ B6 |
| ③ 删依据出处 | 10 | 检修口文档 `BOARD_GEOM_30MM.md §3` 指针全删 | C5 | ✅ C5 |
| ④ 改文档数字 | 11 | §2.1 行区间 0.45-0.57 → 0.80-0.90 | A5 | ✅ A5 |
| ④ 改文档数字 | 12 | §5.1 V PCB 段 +2.00/+1.40 → +17.00（旧 15 mm 板口径） | C3 | ✅ C3+C4 |
| ④ 改文档数字 | 13 | 文档里未标注的 237 残留（拿掉旧口径/只留追溯标注） | B4 | ✅ B4 |

★**反向用例只在内存里做文本变异，不写盘上真文件**（`--selftest` 不碰任何真文件）。

---

## 附 B. 并发说明（红线一行）

★**`MECH/check_demo_struct_truth.py` 的 G5b / C21 现在是红的（21/23 · FAIL 2 组）—— 原因是 `HW/netlist_v1.csv` 盘上 md5 `16ac89f77c25a3f61834cc7ebcd78a7f` ≠ 锚点 `611c3ba3…`，那是 hw-lead 的 ISS-249 落表造成的 md5 变化，不是本单（mech-lead）的失败，本单不许去修它（HW/ 与该受保护脚本本轮一个字节没碰）；该闸在 main 派 hw-lead 重锚 G5b/C21 之前 rc 必须保持 2。**

（附实测原文: `[FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)` · `[FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)` · 本单受保护 3 脚本 md5 复核 = `fa9b59e5… / 9b24bf98… / 3425bc14…` **逐字节不变** ⇒ **红的只可能是网表/脚表那一对，不是我的三个脚本**。）

---

## 附 C. 本轮边界自审（逐条）

| 边界 | 自审 |
|---|---|
| 不许碰 `HW/`（网表/脚表/BOM/板/`.kicad_pro` 一个字节不许动） | ✅ 本轮 **HW/ 零改动**; `HW/netlist_v1.csv` md5 仍是 `16ac89f7…`（那是 hw-lead 的 ISS-249，不是本单） |
| 不许碰板 / PCB 布线 / 布局 | ✅ 未碰; 本单只判文档口径 |
| 不许改 `MECH/check_demo_struct_truth.py` / `MECH/service_port_check.py` / `MECH/hinge_usb_check.py`（含夹具基准 Y / 焊盘阵列 Y / `pcb_thk`） | ✅ 三件 md5 逐字节不变（fa9b59e5… / 9b24bf98… / 3425bc14…）; 新门禁只**读**这三个文件里该读的文本锚点，不写 |
| 不许改 `PROJECT_TRACKER.md` §0 | ✅ 未碰 `PROJECT_TRACKER.md` |
| 不许自签 `state/issue_log.yaml` | ✅ 未碰; **verify 留给 main**（need N4） |
| 零外发 | ✅ 全程本地文件读写, 未发任何邮件/消息/公开内容 |
| 不替老板拍板（d 值 15/18/20 · u8 端件截面 · 集热面材质/面积 · 板长 · 板厚档位） | ✅ 五项**只列选项 + 量化代价**, 拍板权留给 main/老板（need N3） |
| 先落盘骨架再填内容 | ✅ 本单**第一分钟**就把交卷单骨架写到盘上（708 bytes 空表），再逐块填; 每补一块立刻写盘 |
| 每改完一处立刻写盘 + 订正表记一行 | ✅ 本轮新增/改动仅 3 个文件, 逐条登记在附 A（C-8 / C-9 / B-7 / A-8） |
