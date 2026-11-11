# RESET P0 修复方案页 (ISS-191) —— ★只出方案, 不落表 / 不改板★

> ★**本文件的性质**: 方案 + 影响面 + 验收判据。**本轮没有任何一行网表 / 原理图 / 板 / 投产包被改动**
> (★实测: 方案页写完后 `HW/netlist_v1.csv` md5 与 `HW/PCB/demo_mainboard.kicad_pcb` md5 仍与下表一字不变★)
> ★**拍板人是老板**: 本页只给【推荐 + 默认值 + 后果】, **不替老板拍**。
> ★**owner=sw-lead / verify_by=main** ⇒ 本单只交方案; 真正的落表改动随 `state/RECHAIN_ONEPASS_PLAN.md` 的整链重出一次做完。

## 0. 锚点 (★全部实测, 复现命令见 B5★)

| 项 | 值 | 口径 |
|---|---|---|
| `HW/netlist_v1.csv` md5 | `c78f991283cc82d56c8e3dd31657c785` | ★本方案页写完后复核仍为此值 (一字未变)★ |
| 网表规模 | **514 行 = 1 表头 + 513 数据行** / 132825 B | `wc -l` + `wc -c` |
| 网表位号 universe | **291 个 ref** (513 数据行按 ref 聚合) | [实测] |
| 整颗 DNP 位号数 | **56 / 291** (口径: 该 ref 的**所有行**都是 DNP) | [实测] |
| 行级 dnp 自相矛盾的 ref | **7 / 291** (`J_TYPE_C` `U_CHG` `J_CHG` `U_DCDC_VCORE` `Q_ENVC` `U_DCDC_VIO` `RAIL_BOARD_5V`) | [实测] |
| `HW/netlist_v1_pins.csv` md5 | `4814617e22b567d76164e56bc5e39dc8` (584 行, 脚级) | [实测] |
| 官方板 md5 | `611b869e13518c3c023fb178f91a0075` | ★本方案页写完后复核仍为此值★ |
| 板 | 186 个封装位号 / DRC **0** / unc **45** / Gerber **32** 个 | [实测] `state/check_pcb_drc.py` |
| 原理图 | ERC **0** / 脚数完整性 K=**0** (universe=218 器件, 584 脚) | [实测] `check_sch_erc.py` / `check_sch_pinfull.py` |

★**行号口径**: 下文 `L<n>` = `HW/netlist_v1.csv` 的**文件行号** (表头是 L1 ⇒ 数据行 L2~L514), 与 `timing_check.py` 打印的 `line_no` 同口径 (它按 CSV 物理行计)。

---

## B1 结论与推荐

### B1-1 故障链 (★逐行, 行级口径★)

```
PG_AND 网 (6 行, 全部逐行读出):
  L62  R_PG_PULL   → U_DCDC_VCORE pin4   dnp=必装   ← 10k 上拉的"挂点行"
  L63  R_PG_PULL   → RAIL_VDD_1V8_IO      dnp=必装   ← ★上拉电阻本体行 (挂在 1.8V 常供电轨)
  L64  NET_PG_AND  → U_DCDC_VCORE pin4   dnp=必装   ← 两路 PG 并联的"汇总行"
  L67  Q_AND      → U_DCDC_VIO pin4      dnp=必装   ← ★Q_AND 栅极挂在 PG_AND
  L71  Q_ENVC     → U_DCDC_VIO pin4      dnp=**DNP** ★★PG_AND 上唯一一行 DNP★★
  L402 TP_PG_VCORE→ U_DCDC_VCORE pin4    dnp=必装
  L403 TP_PG_VIO  → U_DCDC_VIO pin4      dnp=必装
RESET_N 网 (5 行):
  L65  Q_AND 漏极 → NET_RESET_N          dnp=必装   ← ★Q_AND 把 RESET_N 拉到 GND
  L366 TP_RESET / L377 NET_RESET_N / L382 SW_RST → 必装
  L409 U_SUPV pin1 → NET_RESET_N         dnp=**DNP** ← 监督器不参与拉复位
```

**[实测]** `timing_check.py --only F1_reset_rc` 读出的关键事实:
- `q_and_in_netlist True` · `pg_and_state.dnp_rows ['Q_ENVC']` · `q_and_gate_row_dnp 必装` · `pullup_row_dnp 必装`
- `pg_source_devices = {U_DCDC_VCORE: dnp=必装, device_ic_row_dnp=DNP, U_DCDC_VIO: 同}` ⇒ ★**行级口径下两路 PG 的"连接行"全是必装 ⇒「PG 源器件 DNP」不成立**★
- ★**器件级补注**: `U_DCDC_VCORE` (L79) / `U_DCDC_VIO` (L86) 的 **IC 行 dnp=DNP** ⇒ **两颗 DC-DC 实物不装 ⇒ 它们的 PG 脚根本不在板上** ⇒ PG_AND 上**没有任何实装器件能把它拉低** ★
- `reset_n_state.dnp_rows ['U_SUPV']` ⇒ ★**真正拉低 RESET_N 的只有 `Q_AND` 与 `SW_RST`**★

**[推算] 故障链** ⇒ `PG_AND` 只剩 `R_PG_PULL` 10k 上拉到 1.8V ⇒ 恒高 ⇒ `Q_AND` 栅极 1.8V ⇒ 导通 ⇒ 漏极把 `RESET_N` 钉在 ≈0V ⇒ **SoM 恒在复位 ⇒ 首台板不启动**。
★**且不能赌阈值**: `Q_AND` 的 BOM value = `[待选型] N-MOS (硬件 AND)`、footprint/opn 均为 `待定` ⇒ **Vgs(th) 无官方数据 [0数据]** ⇒ 不能靠"也许 1.8V 拉不导通"过关。

### B1-2 三条改法对比 (★ISS-190 §7-2 原文三条★)

| # | 改法 (原文) | 是否依赖 SoM 球位 TBD-01 | ★对"首台板不启动"这条故障链有没有用★ | 代价 / 副作用 |
|---|---|---|---|---|
| ① | 把 `Q_ENVC` 从 `PG_AND` 上摘掉 / 或让 `Q_ENVC` 必装 | **否** | ★**否 (两个子项都否)** ★ —— 见 B1-3 | 见 B1-3 |
| **②** | **把 `Q_AND` 改 DNP** (复位回到纯 RC + 按键, 与 SoM 内部复位并存) | **否** | ★**是 (唯一直接切断故障链的一条)** ★ | 失去"PG 进复位链"的互锁 (但两颗 DC-DC 本来就不装 ⇒ 现状下这条互锁只会把板按住, 不会放行) |
| ③ | 等 SoM 球位 TBD-01 落地后再把真实 PG 接进复位链 | **是** | 现在无解 (要等外部) | ★**不可用于首台板** ⇒ 出局 ★ |

### B1-3 为什么否掉 ① 的两个子项 (★用反向用例证明, 不是推理★)

**[实测] 反向用例 RC1** (`/tmp/iss191_rev/netlist_RC1_qenvc_populated.csv`: 只把 **L71** `Q_ENVC`@PG_AND 由 `DNP` 改成 `必装`, 其余一行不动):
```
pg_and.dnp_rows           : []            ←→  ['Q_ENVC']
pg_and.all_rows_populated : True          ←→  False
pg_and.q_envc_row_dnp     : '必装'        ←→  'DNP'
pg_and.q_and_gate_row_dnp : '必装'   ★不变★   ←→  '必装'
reset_n.q_and_drain_row_dnp: '必装'  ★不变★
```
⇒ ★**让 `Q_ENVC` 必装只让"PG_AND 上有 DNP 行"这条判据变绿, `Q_AND` 栅极恒高 / RESET_N 恒低这条故障链一点没动** ★
⇒ 且 **电气更糟**: `Q_ENVC` 栅极=PG_AND(恒高) ⇒ `Q_ENVC` 导通 ⇒ 漏极把 `EN_VCORE` 拉到 0 (L73) ⇒ 若将来两颗 DC-DC 装上, **V_CORE 永远使不上能** ⇒ 把一个 P0 换成另一个 P0。

**[推算] "把 `Q_ENVC` 从 `PG_AND` 上摘掉" 子项的问题**: `L71` 的 note 写的是 `[PG_VIO] ... V_SOC_IO 的 PG`, 但网表里**根本没有 `PG_VIO` 这条网** ⇒ 要"摘掉"就得新建一条 `PG_VIO` 并把 `U_DCDC_VIO pin4` 从 `PG_AND` 迁走 ⇒ ★**同一个引脚不能同时挂两条网** ⇒ 会破坏 `L64` 的"两路 PG 并联"设计意图, 还要重画 `L402/L403` 两个 PG 测试点的归属 ⇒ 改动面比 ② 大得多, 而**收益 = 0** (它不碰 `Q_AND`)。

### B1-4 ★推荐★

> ★**推荐: ② —— 把 `Q_AND` 整颗改 DNP (三行同改: L65 / L66 / L67) ★**
> ★**默认执行口径 = 「② + ① 的一个无害子集」**:
>   · **必做**: `Q_AND` 三行 `dnp` 由 `必装` → `DNP` (表 A L65/L66/L67 + 表 B `Q_AND.1/.2/.3`)
>   · **建议同批 (消歧, 零电气代价)**: `Q_ENVC` 三行 (L71/L72/L73) 统一为 `DNP` ⇒ 消除"BOM 说要买、网表 PG_AND 那行说不装"的口径差 (★`Q_ENVC` 的用途是 V1.8 的 V_CORE 顺序链, 而顺序链的两颗 DC-DC 都不装 ⇒ 该链本就是死的 ⇒ 统一 DNP 与现状自洽★)
>   · **可选 (要老板点头, 影响功耗)**: `R_PG_PULL` 两行 (L62/L63) 也改 DNP ⇒ 省掉 180 µA 常流 (见 B3-4)
> ★**明确不做**: ① 的"让 `Q_ENVC` 必装"子项 (B1-3 已证无效且更糟) ★

**理由 (三条)**:
1. ★**唯一直接切断故障链**: `Q_AND` 漏极是 RESET_N 上唯一的"硬件常拉低" (U_SUPV 是 DNP) ⇒ 去掉它, RESET_N 只剩 10k 上拉 + RC + 按键 ⇒ 首台板能启动。[实测+推算]
2. ★**不依赖任何外部答复**: 不等 TBD-01 / 不等原厂 ⇒ 首台板就能投板试; ③ 反过来至少要等一轮外发回信。[实测]
3. ★**与"SoM 自带 PMIC"的既有结论自洽**: 网表 L409 的 note 已经写明 Forlinx 官方载板复位电路 = **按键 + 100nF + ESD, 无监督器** ⇒ 方案 ② 正是把主板复位链还原成这个参考电路, 而不是发明新东西。[实测: 网表 note 原文]

### B1-5 ★推荐方案的复位时序行为推演 (★assert / deassert / 掉电★)

> 基础: `R_PU_RESET_N` 10k 上拉 → `RAIL_VDD_1V8_IO` (=1.8V, 源 `U_LDO_IO18` TPS7A20-18, **L155 必装** ⇒ 1.8V 轨在首台板上真实存在 ✔);
> `R_SER_RESET_N` 1k 串联 + `C_RST` 100nF 对地; `SW_RST` 按键到 GND。
> ★**RC 参数一个都没动** ⇒ 释放时间常数与今天完全一样 ⇒ ★**改 Q_AND 不影响 RC 口径★**。

| 事件 | 行为 | 数字 | 证据 |
|---|---|---|---|
| **assert (复位拉低)** | 按下 `SW_RST` ⇒ `RESET_N` 经 `R_SER` 1k 被拉低 ⇒ 戴维南等效 `R_th = 10k‖1k = 909 Ω`, `V_th = 1.8×1/11 = 0.164 V` ⇒ 从 1.8V 落到 0.7·VDD(=1.26V) 需 `909Ω×100nF×ln(1.636/1.096)` | **≈36 µs** (工具口径 `tau_assert_us = 100.0` = 1k×100nF, 工具取的是 R_SER·C, 偏保守) | [推算] (公式在 B5 可复算) / [实测] 工具读数 `tau_assert_us 100.0` |
| **deassert (复位释放)** | 1.8V 轨上来 ⇒ 10k 上拉 ⇒ 经 1k+100nF ⇒ `τ_release = (10k+1k)×100nF` | **τ = 1.1 ms**; 越过 0.7·VDD 需 `τ·ln(1/0.3)` = **1.324 ms** ⇒ SoM 在上电后 ~1.3ms 脱复位 | [实测] `tau_release_ms 1.1` / `t_reach_0p7vdd_ms 1.324` |
| **掉电 (power-down)** | 1.8V 轨塌 ⇒ `RESET_N` 的上拉源消失 ⇒ 随轨下落到 0 ⇒ **自动进复位** | 复位链不依赖 `Q_AND`、不依赖 SoM 球位 ⇒ 掉电方向**行为确定** | [推算] |
| **对比现状 (Q_AND 装)** | `PG_AND` 恒高 ⇒ `Q_AND` 导通 ⇒ `RESET_N` ≈ 0 ⇒ **永远等不到 deassert** | 首台板不启动 | [实测+推算] |

★**首台板复位链变成 "RC + 按键" 之后, `RESET_N` 上还剩谁在拉 (★行级★)**:
`SW_RST` (L382, 必装) 拉低 · `R_PU_RESET_N`/`R_SER_RESET_N`/`C_RST` (必装) 拉高 · `TP_RESET` (L366, 必装) 测点 · `U_SUPV` pin1 (L409, **DNP**, 不参与) · **`Q_AND` (L65, 改后 DNP, 不参与)** ⇒ ★**拉低者只剩按键一个 ⇒ 无条件常拉低 = 0 个** ★

### B1-6 后果 (★诚实的代价★)

| 得到 | 失去 |
|---|---|
| 首台板可启动 (RESET_N 不再被硬件钉死) | ★**"PG 好了才放复位" 的硬件互锁** —— 但两颗 DC-DC 都是 DNP ⇒ **这条互锁在首台板上从来只起"按住"作用, 从来没起过"放行"作用** ⇒ 现状下它 100% 是负收益 |
| RESET_N = 纯 RC + 按键, 与 Forlinx 官方载板参考电路一致 | 若将来换 SoM / 装上 DC-DC, 需要把 PG 链重新接进来 —— 那正是 ③ 的工作, 与本次改动不冲突 (可后做) |
| BOM 少 1 颗 (`Q_AND`) | 少一个"硬件 AND"备料行 (BOM value 本来就是 `[待选型]`, 型号还没定 ⇒ 现在不占采购成本) |

---

## B2 行级改动清单

### B2-1 必改的网表行 (★表 A = `HW/netlist_v1.csv` / 表 B = `HW/netlist_v1_pins.csv`★)

| # | 表 | 行 | ref | net / pin | 现状 dnp | ★改成★ | 为什么 |
|---|---|---|---|---|---|---|---|
| C-1 | A | **L65** | `Q_AND` | RESET_N (漏极) | 必装 | **DNP** | 拔掉唯一把 RESET_N 硬件拉低的器件 |
| C-2 | A | **L66** | `Q_AND` | GND (源极) | 必装 | **DNP** | ★**必须同改**: `timing_check.py` 的 `populated("Q_AND")` 是"**IC/SW 行里出现任一 `dnp=必装` 就算装**" ⇒ **只改 L67 器件级仍显示"装"** (★反向用例 RC3 实测: `q_and_in_netlist` 仍 `True`, `reset_n.q_and_drain_row_dnp` 仍 `必装`★) |
| C-3 | A | **L67** | `Q_AND` | PG_AND (栅极) | 必装 | **DNP** | 拔掉"栅极恒高 ⇒ 导通"这条通路 |
| C-4 | B | `Q_AND.1` | `Q_AND` | RESET_N | 必装 | **DNP** | 脚级表与表 A 同步 (584 行的脚级真源) |
| C-5 | B | `Q_AND.2` | `Q_AND` | GND | 必装 | **DNP** | 同上 |
| C-6 | B | `Q_AND.3` | `Q_AND` | PG_AND | 必装 | **DNP** | 同上 |

★**建议同批 (消歧, 零电气代价)★:

| # | 表 | 行 | ref | 现状 | 改成 | 为什么 |
|---|---|---|---|---|---|---|
| C-7 | A | **L71** | `Q_ENVC` | DNP | **DNP (不变, 但 note 要改)** | ★**它已经是 DNP** ⇒ 真正的动作是**把 L72/L73 也改 DNP**, 让三行一致 ⇒ BOM 才会记 DNP (BOM 口径 = ref 级: **任一行必装 ⇒ 整个位号记必装**) ★ |
| C-8 | A | **L72** | `Q_ENVC` | 必装 | **DNP** | 同上 (三行统一) |
| C-9 | A | **L73** | `Q_ENVC` | 必装 | **DNP** | 同上 |
| C-10~11 | B | `Q_ENVC.1/.2/.3` | `Q_ENVC` | DNP/必装/必装 | **DNP/DNP/DNP** | 脚级表同步 |

★**可选 (需老板点头, 影响常流功耗)★:

| # | 表 | 行 | ref | 现状 | 改成 | 收益 / 代价 |
|---|---|---|---|---|---|---|
| C-12 | A | **L62** | `R_PG_PULL` | 必装 | DNP (可选) | 改后 PG_AND 上只剩两个测试点 ⇒ 网变成纯测试网 |
| C-13 | A | **L63** | `R_PG_PULL` | 必装 | DNP (可选) | ★省 180 µA 常流 (1.8V/10k) ⇒ 电池侧 0.666 mW / 420mAh 电池 ≈ **97 天** [推算] ★ ★**代价: 将来若接真实 PG, 这个上拉要回来** ⇒ 与 ③ 绑定, 建议 ③ 落地前不要动 ★ |

### B2-2 连带要动的文件 (★按 `state/RECHAIN_ONEPASS_PLAN.md` 的 12 步对齐★)

| 序 | 文件 | 动作 | ★预期变化★ | 为什么 |
|---|---|---|---|---|
| 1 | `HW/netlist_v1.csv` | 改 3~6 行 dnp (+ note) | 行数**不变** (514/513), md5 **变** | 源头 |
| 2 | `HW/netlist_v1_pins.csv` | 改 3~6 行 dnp | 584 行**不变**, md5 **变** | 脚级真源 (原理图生成器读它) |
| 3 | `HW/BOM_v1.csv` | **重出** (`state/gen_bom.py`) | 291 数据行**不变**; `Q_AND` 行 dnp `必装→DNP` (+`Q_ENVC`); ★**DNP 位号数 56→57** (口径: ref 级, 所有行都 DNP) ★ | BOM 的 dnp 口径 = ref 级 (`gen_bom.py:117-125`: 任一行必装 ⇒ 整个位号记必装) ⇒ ★**只改一行 ⇒ BOM 会跟网表打架** ⇒ 这就是 C-2 必须同改的原因 ★ |
| 4 | `HW/PCB/demo_mainboard.kicad_sch` (+ `p1..p10` 分页) | **重出** (`state/gen_kicad_sch.py`) | ★符号会多一行 `(dnp yes)` (三脚全 DNP) + 脚标写 `DNP` + 染红 (`gen_kicad_sch.py:32/317/352`)★ ⇒ **ERC 仍 0, 脚数 K 仍 0** | 原理图必须表达"这颗不贴" |
| 5 | `HW/PCB/demo_mainboard.kicad_pcb` | 重出 (`state/gen_pcb_netlist_board.py`) | ★**几何/铜/焊盘应逐字节不变** (见 B3)★ ⇒ 只有 `ref_designator_rename` 会改它 (186 个封装位号 + 丝印) | 见 B3 |
| 6 | `HW/PCB/gerbers/` (canonical, 32 个) | **重出** | 内容不变 (若板没变) | 与板一致 |
| 7 | `HW/PCB/production/gerbers/` (32) | 重出 (复制) | 同上 | |
| 8 | `HW/PCB/production/drill/` | 重出 | 同上 | |
| 9 | `HW/PCB/production/pos/demo_mainboard-pos.csv` | 重出 | **186 行不变**; ★`Q_AND` 仍留在 CPL 里 (与现状一致: ★BOM 记 DNP 却仍在 pos 里的位号 = **41/56**★ ⇒ 这是本项目既有做法 ⇒ 不新增产线风险) | P&P |
| 10 | `HW/PCB/production/assembly/demo_mainboard-ipc2581.xml` | 重出 | 装配文件重出 | 装配 |
| 11 | `HW/PCB/production/assembly/demo_mainboard-assembly-{top,bottom}.pdf` | 重出 | 装配图 | |
| 12 | `HW/PCB/production/3d/demo_mainboard.step` | 重出 | 3D | |
| 13 | `HW/PCB/production/doc/demo_mainboard.d356` | 重出 | 网表 IPC-D356 | |
| 14 | `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` | 重出 | ★KiCad 侧 BOM: `(dnp yes)` 的符号会被排除 ⇒ **`Q_AND` 行会消失** (现状 `U_SUPV` 已不在里面) ⇒ ★**这正是我们要的 (KiCad BOM 与我们的 BOM 口径终于一致)**★ | |
| 15 | `HW/PCB/production/doc/` 其余 (`kicad.net` / `board-stats.txt` / `*.pdf` / `Edge_Cuts.dxf` / `sch_src/` 12 个 / `sch_svg/`) | 重出 | — | 投产包完整性 (`chain_gate.py` 要 30/30) |
| 16 | ★**`SW/tools/timing_check.py`** ★ | ★**改 5 条回归断言 (★本单无权改★)** ★ | 见 B5-3 | ★**不改 ⇒ 落表后 SELFTEST 会红 5 条 ⇒ 闸会挡★ |
| 17 | `state/*.py|sh` 里引用旧 md5 的地方 | 换基线 | ★7 处 (RECHAIN 计划第 7 步)★ | 旧 md5 命中数必须 = 0 |

---

## B3 对 unc / DRC 的预期影响

### B3-1 结论: **只改 dnp ⇒ unc 45 不变 / DRC 0 不变 / 板 md5 不变**

| 论据 | 内容 | 证据 |
|---|---|---|
| ① **板生成器根本不读 dnp** | `grep -c -i "dnp" state/gen_pcb_netlist_board.py` = **0** ⇒ 生成器的输出**不可能**随 dnp 列变化 | [实测] |
| ② **板文件本身不编码 DNP** | `grep -c "attr " HW/PCB/demo_mainboard.kicad_pcb` = **0** ⇒ 没有任何封装带 `exclude_from_pos_files` / `exclude_from_bom` ⇒ **DNP 在本项目是 BOM 级约定, 不是板级属性** | [实测] |
| ③ **焊盘集合不变** | `Q_AND` 的封装仍是 3 个 SMD 焊盘 (pad1=RESET_N, pad2=GND, pad3=PG_AND), 位置/层/网络不变 ⇒ ★**铜箔、线宽、走线、孔 一模一样 ⇒ unc 45 与 DRC 0 必然不变** ★ | [实测] 读 `demo_mainboard.kicad_pcb` Q_AND 封装块 (行 7587~7701) |
| ④ **拓扑不变** | `dnp` 列不参与网络连接 ⇒ `PG_AND`/`RESET_N` 两条网的节点集合不变 ⇒ ★**unc 的 45 条未布线项一条不多一条不少** ★ | [推算] (由①③得) |
| ⑤ **参考先例** | ★**BOM 记 DNP 却仍在 CPL 里的位号 = 41/56** (口径: BOM 里 dnp=DNP 的 56 个 ref, 与 pos 里 186 个 ref 求交) ⇒ 本项目**已经在用 "DNP 只写进 BOM, CPL 靠作业指导书剔除" 这套办法** ⇒ `Q_AND` 走同一条路 ⇒ **不新增产线风险** ★ | [实测] |

### B3-2 ★例外: `ref_designator_rename` 会改 unc / DRC 吗★

★**会改板 md5, 但预期 unc/DRC 数值不变** —— 改名**只动位号字符串与丝印**, 不动铜/焊盘/网络 ⇒
- DRC: 0 → 0 (几何零变化) ⇒ ★**但 `gen_pcb_netlist_board.py` 重跑时会重新布局/布线, 若路由器非确定性, 数字可能漂 ⇒ 必须以重跑后的实测为准, 不得沿用旧读数** ★
- unc: 45 → 预期 45 (★**唯一确定性的闸 = 板 md5 必须换新 + DRC 必须仍 0** ★)
- ★**丝印**会随 ref 改名变长/变短 ⇒ 丝印与焊盘重叠风险**可能变** ⇒ ★**[0数据] 未测**: 改名后 silk-over-pad 是否有新增 ⇒ 须由第 5 步的 fresh DRC 判定 ★

### B3-3 原理图侧影响 (ERC / 脚数)

| 闸 | 现状 | 落表后预期 | 口径 |
|---|---|---|---|
| `check_sch_erc.py` | ERC **0** rc=0 | 仍 **0** (DNP 脚不参与 ERC) | [实测] 现状 / [推算] 预期 |
| `check_sch_pinfull.py` (判据口径 = 表侧**含** DNP 行) | 图上 584 脚 / 表里 584 脚, **K=0** (universe=218 器件) | 仍 **K=0**, 脚数仍 584/584 (★**只改 dnp 不增删行 ⇒ 行数不变**★) | [实测] 现状 / [推算] 预期 |
| 同上 (对照口径 = 表侧**去** DNP 行) | 图上 584 / 表里 **467** / 不一致 **50** 器件; 表里 DNP 行 **117** | ★**表里 DNP 行 117→120 (C-1~C-3 三行)**; ★**表里(去DNP) 脚数 467→464**; ★**不一致器件 50→51** (`Q_AND` 变成"图上 3 脚 / 表里 0 脚") ★ | [推算] (公式: 584−120=464; `Q_AND` 3 脚从一致变不一致 ⇒ +1 器件) |

### B3-4 功耗影响 (★唯一一个"改不改都有代价"的点★)

| 场景 | 常流 | 功耗 | 口径 |
|---|---|---|---|
| 现状 (`Q_AND` 装, PG_AND 恒高) | `R_PG_PULL` 10k 挂 1.8V ⇒ **180 µA** | 1.8V 侧 **0.324 mW** / 电池 3.7V 侧 **0.666 mW** | [推算] I = 1.8V/10kΩ = 180 µA |
| 推荐方案后 (不额外动 `R_PG_PULL`) | **180 µA 不变** | 同上 | ⇒ ★**推荐方案本身不省也不多花这 180 µA** ★ |
| 若同批把 `R_PG_PULL` 也改 DNP (可选 C-12/13) | **0 µA** | 0 | ⇒ 420 mAh 电池 ÷ 180 µA = **2333 h ≈ 97 天** [推算] |
| `Q_AND` 本身 | 现状: 栅极 1.8V + 漏极 0V ⇒ **恒导通 ⇒ 灌 1.8V/10k = 180 µA 经 Q_AND 通道到 GND** (≈ 再加 180 µA) | ★**推荐方案把这一路也去掉** ⇒ 复位链上的常流从 ~360 µA 降到 180 µA (只剩 R_PG_PULL) ★ | [推算] |

---

## B4 与 `ref_designator_rename` 合并成一次整链重出的可行性

> ★**依据**: `state/RECHAIN_ONEPASS_PLAN.md` (★**本单只读, 未改★**) 的 12 步 + §5 的三个选项。
> ★**老板 11-11 的方案是 ②「A + B + C 一次整链重出」** (A=原理图补脚 / B=位号改名 / C=ISS-191 本单) —— ★**本单不替老板拍, 只把"能不能合并"这件事的结论和代价摆出来** ★

### B4-1 结论: ★**可以合并, 且技术上零冲突 —— 但有一个前置次序约束★**

| 项 | 判断 |
|---|---|
| **文件交集** | ★**0** ★: 本单只动 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 的 **dnp 列**; `ref_designator_rename` 动 **ref 列** ⇒ **同表不同列 ⇒ 可同批改** ⇒ ⇒ **一次落表, 一次重出** |
| **依赖次序** | ★**必须 "先改 dnp + ref (同一次落表), 再重出"** ⇒ ★**不许先重出一次板再改 dnp 再重出一次** (那就变成两次改板 = 两批历史读数作废, 正是要避免的) ★ |
| **互不干扰的证据** | ★板生成器 `grep -c -i dnp` = **0** ⇒ ★**生成器对 dnp 列无感** ⇒ 改名与改 dnp **不会互相踩** ★ (★**前提: 生成器确实逐行读 ref 与 dnp 两列 ⇒ 是**) ★ |

### B4-2 ★哪些可以同批做 (逐条★)

| # | 改动 | 能不能同批 | 理由 |
|---|---|---|---|
| 1 | `Q_AND` 三行 dnp → DNP (C-1~C-3) | ★**能** ★ | 改 dnp 列 |
| 2 | `Q_ENVC` 三行 dnp 统一 → DNP (C-7~C-10) | ★**能** ★ | 同上; ★**与 `iss190_netlist_q_envc_dnp_mismatch` 那条 need 是同一件事 ⇒ 可一次结掉** ★ |
| 3 | `ref_designator_rename` (186 个封装位号 + 丝印 + BOM) | ★**能** ★ | 改 ref 列; 与①同表不同列 |
| 4 | `U_EN_SW` 补 IC 行 (ISS-190 副产物 6) | ★**能, 但建议单独一批** ★ | ★**它改的是"行数"**(网表 513→514 数据行) ⇒ ★**会撞掉"网表锚点 md5/行数"这类断言, 排查成本高** ⇒ ★**建议与改名+本单分两批, 或排在最前面单独做** ★ |
| 5 | `R_PG_PULL` 也改 DNP (可选 C-12/13) | ★**能** ★ | 同 1; ★但需老板单独点头 (省 180 µA) ★ |
| 6 | 原理图补脚 (A, hw-lead 6b 在跑) | ★**不能与本单同批** ★ | ★**6b 正在改 `state/gen_kicad_sch.py` + `HW/PCB/demo_mainboard*.kicad_sch` ⇒ 与"重出原理图"这一步撞车 ⇒ 必须等 6b 收工** ★ |

### B4-3 12 步里的落点 (★只标位置, 不改那个文件★)

| 步 | 做什么 | ★本单的落点★ |
|---|---|---|
| 1 | 网表表改名 + P0 改动落表 | ★**本单全部落在这里** (dnp 列 + ref 列, 一次落) ★ |
| 2 | 核表 (`check_netlist.py` + `check_netlist_pins.py` + `check_kicad_net.py`) | ★本单改动后必须三个 rc=0 ★ |
| 3 | 重出原理图 | ★`Q_AND` 符号会变 `(dnp yes)`; ★**必须等 6b 收工** ★ |
| 4 | 逐脚零差异复核 | ★584 脚, 零差异 ★ |
| 5 | 重出板 | ★几何预期不变; ★**fresh DRC 必须 0** ★ |
| 6 | 重出 BOM | ★`Q_AND` 记 DNP; ★**DNP 位号数 56→57** (口径: ref 级, 291 个 ref 中所有行都 DNP 的个数) ★ |
| 7 | 换基线 (旧 md5 → 新 md5) | ★网表表 2 个 + 板 1 个 md5 ⇒ 引用处全改, 旧 md5 命中数 = 0 ★ |
| 8 | 重出投产包 | ★30/30 必备产物 + 原理图源 12 个 ★ |
| 9~12 | 留证链/盖印/发布/巡检/推送 | 不变 |

### B4-4 代价 (★引用 RECHAIN §4, 只报不改★)

- ★**合并的收益**: 板 md5 只换 **一次** ⇒ 历史留证链快照只作废 **一批** (不是两批); 留证链/Gerber/投产包/盖印/发布闸只重跑 **一遍** (2~4 小时) ★
- ★**不合并的代价**: 改两次板 = 两次全套重跑 + 两批历史读数作废 ⇒ ★**本单明说: 合并是老板的决定, 但技术上零冲突, 我建议合并** ★
- ★**本单自己带来的增量**: **≈ 0** (只多改 3~6 行 dnp) ⇒ ★**几乎不增加合并成本 ⇒ 没有理由单独开一轮改板** ★

---

## B5 验收判据 (★每条都给"命令 + 期望输出"★)

### B5-1 ★现状基线 (本方案页写完即复核, ★本单不改任何东西★)

| # | 命令 | 期望输出 (★2026-11-11 15:2x 实测★) |
|---|---|---|
| V1 | `python3 SW/tools/timing_check.py --only F1_reset_rc` | `tau_release_ms 1.1` · `tau_assert_us 100.0` · `t_reach_0p7vdd_ms 1.324` · `netlist_annotation_ms 100.0` · `annotation_error_ratio 90.9` · `q_and_in_netlist True` · `pg_pullup_ohm 10000.0` · `pg_and_state.dnp_rows ['Q_ENVC']` · `q_and_gate_row_dnp 必装` · `q_envc_row_dnp DNP` · `pullup_row_dnp 必装` · `pg_sources_all_populated True` · `reset_n_state.dnp_rows ['U_SUPV']` · `q_and_drain_row_dnp 必装` · `sw_rst_row_dnp 必装` · `u_supv_pin1_row_dnp DNP` · `NETLIST_ANCHOR: netlist_md5 c78f991283cc82d56c8e3dd31657c785 / netlist_lines_total 514 / netlist_data_rows 513` |
| V2 | `python3 SW/tools/timing_check.py` | **`SELFTEST 55/55 通过, rc=0`** |
| V3 | `md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb` | `c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv` / `611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb` ★**两个都必须一字不变**★ |
| V4 | `python3 state/merge.py` | `rc=0` · `冲突 0` |
| V5 | `python3 state/gate_check.py` | `【Q1 交付齐备率】 18/18` |
| V6 | `python3 state/check_pcb_drc.py` | `DRC violations = 0` · `unconnected items = 45` · `Gerber 32 个` · `全过` |
| V7 | `python3 state/check_sch_erc.py` | `ERC 违规数 = 0` · rc=0 |
| V8 | `python3 state/check_sch_pinfull.py` | `图上 584 脚 / 表里 584 脚 · K=0 (universe=218)` · rc=0 |

### B5-2 ★落表后的验收判据 (★等老板拍板后随整链重出一起验★)

| # | 命令 | 期望输出 |
|---|---|---|
| A1 | `python3 SW/tools/timing_check.py --only F1_reset_rc` | ★`q_and_in_netlist` ⇒ **False**; ★`pg_and_state.q_and_gate_row_dnp` ⇒ **DNP**; ★`reset_n_state.q_and_drain_row_dnp` ⇒ **DNP**; ★`reset_n_state.dnp_rows` ⇒ **含 `Q_AND`**; ★`tau_release_ms` ⇒ **仍 1.1** (★RC 没动★); ★`tau_assert_us` ⇒ 仍 100.0; ★`t_reach_0p7vdd_ms` ⇒ 仍 1.324 ★ |
| A2 | `python3 SW/tools/timing_check.py` | ★**SELFTEST 必须 rc=0** ⇒ ★**前提: 先按 B5-3 改掉那 5 条断言** ★ |
| A3 | `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb` | ★三个 md5 **全部换新** (★网表表 2 个 + 板 1 个★) ⇒ ★**旧 md5 命中数必须 = 0** (`grep -rn 611b869e13518c3c023fb178f91a0075 .` ) ★ |
| A4 | `python3 state/check_pcb_drc.py` | `DRC violations = 0` · `unconnected items = 45` (★**若不是 45, 说明改板时动了几何 ⇒ 必须停, 不许往下走**★) |
| A5 | `python3 state/check_sch_erc.py` | `ERC 违规数 = 0` · rc=0 |
| A6 | `python3 state/check_sch_pinfull.py` | `K=0 (universe=218)` · 图上 584 / 表里 584 · ★**对照口径**: 表里(去DNP) **464** 脚 / 不一致 **51** 器件 / 表里 DNP 行 **120** ★ |
| A7 | `python3 state/gen_bom.py` | rc=0 · ★**DNP 位号数 56 → 57** (口径: ref 级, 291 个 ref 中所有行都 DNP 的个数)★ · ★**BOM 里 `Q_AND` 行 dnp = DNP** ★ |
| A8 | `python3 state/merge.py` | rc=0 · 冲突 0 |
| A9 | `python3 state/gate_check.py` | Q1 = 18/18 |
| A10 | `python3 state/chain_gate.py` | rc=0 (投产包 30/30) |

### B5-3 ★落表时必须同步改的 5 条断言 (★在 `SW/tools/timing_check.py` 里★ —— ★**本单无权改, 留给落表的人★**)

**[实测]** 我把推荐方案 (Q_AND 三行全 DNP) 打到 `/tmp` 副本上跑全量自检 ⇒ 精确红 **5 条**:

| # | 断言原文 (缩写) | 为什么必须改 |
|---|---|---|
| ① | `网表锚点: 现行网表 = 513 数据行 / md5 c78f991283cc82d56c8e3dd31657c785` | 网表 md5 换了 ⇒ 锚点要换成新值 (★行数仍 513★) |
| ② | `F1 复评: PG 已进复位链 (Q_AND + R_PG_PULL 10k)` | ★**这条判据的立论基础消失了** ⇒ 要改成"Q_AND 已 DNP ⇒ PG 不再进复位链 (本版)" ★ |
| ③ | `★F1 实读: PG_AND 上真正 DNP 的是 Q_ENVC (行级)` | `dnp_rows` 会变成 `['Q_AND','Q_ENVC']` ⇒ 断言要跟着改 |
| ④ | `★F1 实读: RESET_N 上谁在拉 —— Q_AND 必装 / SW_RST 必装 / U_SUPV pin1 DNP` | `q_and_drain_row_dnp` 变 DNP ⇒ 断言要改成"拉低者只剩 SW_RST" |
| ⑤ | `REV-8 反向: 把 PG_AND 上 Q_AND 那行改成 DNP ⇒ 栅极接在 PG_AND 上的 Q_AND 判据必须变红` | ★**前提消失** (基线已经是 DNP) ⇒ 要重新设计这条反向用例 (★建议改成"把 `Q_AND` 三行改回必装 ⇒ 栅极恒高判据必须变红"★) |

★**建议 (给落表的人)**: 顺手把 ② 的正向判据改成 ★"**RESET_N 上拉低者只有 SW_RST 一个**"★ —— 这才是本次修复真正要锁住的不变量, 比"PG 在不在链上"更贴近首台板能不能启动。

### B5-4 ★本单自证用的反向用例 (★已在 `/tmp` 跑过, 真网表一字未动★)

| 用例 | 副本 | 改了什么 | 结论翻转 |
|---|---|---|---|
| **RC1** | `/tmp/iss191_rev/netlist_RC1_qenvc_populated.csv` | L71 `Q_ENVC` DNP→必装 | ★`dnp_rows []` / `all_rows_populated True` / ★**`q_and_gate_row_dnp` 仍 `必装` ⇒ 故障链不变 ⇒ ① 的"必装"子项无效** ★ |
| **RC2** | `.../netlist_RC2_net_pg_and_dnp.csv` | L64 `NET_PG_AND` 必装→DNP | ★`pg_sources_all_populated True→False` + 两路 `U_DCDC_*` 报 DNP ⇒ 证明**行级口径读的是那一行, 不是器件级** ★ |
| **RC3** | `.../netlist_RC3_q_and_dnp_gate_only.csv` | **只**改 L67 (栅极行) | ★`q_and_gate_row_dnp`→DNP, ★**但 `q_and_in_netlist` 仍 True / `q_and_drain_row_dnp` 仍 必装** ⇒ ★**证明"必须三行同改"** ★ |
| **RC4** | `.../netlist_RC4_q_and_dnp_all3.csv` | L65+L66+L67 全 DNP (= 推荐方案) | ★`q_and_in_netlist`→**False** · `reset_n.q_and_drain_row_dnp`→**DNP** · `reset_n.dnp_rows`→`['Q_AND','U_SUPV']` ★⇒ **拉低 RESET_N 的只剩按键** ★ |

★**复核方式 (main 可独立跑)**:
```
python3 SW/tools/timing_check.py --netlist /tmp/iss191_rev/netlist_RC4_q_and_dnp_all3.csv --only F1_reset_rc
```
★**注意**: `RC4` 跑全量自检会红 5 条 (★正是 B5-3 那 5 条★) ⇒ 这本身也是"落表前先改断言"的证明。

---

## B6 边界与未决项

### B6-1 本单的边界 (★硬声明★)

- ★**本轮只出方案页**: `HW/PCB/RESET_P0_FIX_PLAN.md` (本页) + `HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md` + `state/fragments/sw.yaml` (经 `state/frag_write.py` 写) —— ★**这 3 处是本单唯一动过的文件** ★
- ★**没动**: `HW/netlist_v1*.csv` / `HW/PCB/demo_mainboard*` / `state/gen_*.py` / `SW/tools/timing_check.py` / `SW/SW_TIMING_REVIEW.md` / `state/issue_log.yaml` / `PROJECT_TRACKER.md` / `MECH/**` / 其它 `HW/**` ★
- ★**没做**: 不落表、不改板、不改原理图、不重出投产包、**不联系供应商/原厂** ★
- ★**没替老板拍板**: 本页只给推荐 + 默认值 + 后果; ★**落表的时机由老板在 `state/RECHAIN_ONEPASS_PLAN.md` §5 拍** ★

### B6-2 未决项 (★要老板拍 / 要外部答复★)

| # | 未决 | 找谁 | ★标 [0数据] 的部分★ | 我的默认建议 |
|---|---|---|---|---|
| U1 | ★**拍板: 走 ② (`Q_AND` 三行 DNP) 还是 ① 或 ③** | **老板** | — | ★**②** (B1-4) ★ |
| U2 | ★**拍板: `Q_ENVC` 三行是否同批统一 DNP** | 老板 / hw-lead | — | ★**同批统一 DNP** (消口径差) ★ |
| U3 | ★**拍板: `R_PG_PULL` 是否也改 DNP (省 180 µA)** | 老板 | ★**[0数据]**: SoM 内部复位对"PG 链"的实际要求未知 | ★**先不动** (③ 落地前不要动) ★ |
| U4 | ★**SoM 是否提供 PG 输出 (球位 + 极性) + RESET 释放要求 + 内部上电顺序** | **项目总工外发原厂** (★我不外发★) | ★**[0数据]**: TBD-01 / TBD-12 全部未回 | ★**等外部**; ★**本方案不依赖它** ★ |
| U5 | ★**SoM 内部 RESET 的释放时序要求 (SoC 要多久才认复位释放)** | 原厂 (同上) | ★**[0数据]** | ★**未知** ⇒ 但复位链释放只要 1.324 ms, 属常规量级, 不构成风险 ★ |
| U6 | ★**`Q_AND` 的型号 / Vgs(th) / 封装** | hw-lead + 采购 | ★**[0数据]**: BOM value = `[待选型]`, footprint/opn = `待定` | ★**正因为没有官方数据, 才好决策**: ★**不能赌阈值 ⇒ 必须做 ②** ★ |
| U7 | ★**`U_EN_SW` 没有器件行 ⇒ BOM/装配单会漏这颗开关** (ISS-190 §7-6, **本单再提醒一次**) | hw-lead | ★**[0数据]**: 该颗的封装/OPN 虽在网表 pin 行里写了 `TPS22991RAA`, 但**没有 IC 行** ⇒ BOM 里它只是一条 `type=NET` 的网络行 ⇒ ★**按器件口径会漏** ★ | ★**与本单无交集 (它不在复位链上)**; ★**但它影响"关机/负载开关"那一支** ⇒ ★**建议与改名同批、但**排在 dnp 改动之前单独做**, 因为它改行数 ⇒ 会撞掉"网表锚点行数"类断言 ★ |
| U8 | ★**ISS-190 交接单正文里的旧表述** (`§1.2 / §1.3 / §3` 仍写 "PG 源器件 U_DCDC_VCORE/U_DCDC_VIO 都是 DNP") | sw-lead (我) / main | — | ★**已被行级口径推翻** ⇒ 本页以行级口径为准; ★**该表述的订正属于 `SW/SW_TIMING_REVIEW.md`, **本单无权改** ⇒ 留给落表那一批 ★ |

### B6-3 ★口径声明 (★凡给出统计数, 必带口径★)

| 数 | 值 | ★口径★ |
|---|---|---|
| 网表数据行 | 513 (总 514 行含表头) | ★物理行, 表头算第 1 行★ |
| 位号 universe | 291 | ★513 数据行按 ref 去重★ |
| 整颗 DNP 位号 | 56 | ★ref 级: 该 ref 的**所有行** dnp 都是 DNP★ (★不是"行级 DNP 行数"★ ⇒ 行级 DNP 行数另算, B5-3 的 120 是**脚级**口径) |
| 行级 dnp 矛盾 ref | 7 | ★同一 ref 在不同行上 dnp 不同★ |
| 板封装位号 | 186 | ★`(property "Reference" ...)` 去重★ = pos/CPL 的 186 行 = 一致 |
| BOM DNP 位号 | 56 | ★`HW/BOM_v1.csv` 里 dnp=DNP 的行数 (★与上面的 56 是**同一个数**, 因为 BOM 的口径也是 ref 级 ⇒ ★自洽★) ★ |
| DNP 却仍在 CPL 的位号 | 41 | ★口径: BOM 记 DNP 的 56 个 ref ∩ pos 的 186 个 ref★ |
| unc / DRC | 45 / 0 | ★`state/check_pcb_drc.py` 的当前读数 (骨架阶段, 非 strict)★ |

---

## 附: 证据分级索引

| 级别 | 本页里的内容 |
|---|---|
| **[实测]** | `timing_check.py --only F1_reset_rc` 全部读数 · SELFTEST 55/55 · md5 ×2 · merge/gate/DRC/ERC/pinfull 的 rc 与数字 · 网表逐行内容 (L62/L63/L64/L65/L66/L67/L71/L72/L73/L79/L86/L402/L403/L409/L366/L377/L382) · `Q_AND` 封装 3 焊盘与网络 · `gen_pcb_netlist_board.py` 里 dnp 命中数 = 0 · 板里 `attr` 命中数 = 0 · BOM 口径代码 (`gen_bom.py:117-125`) · RC1~RC4 四个反向用例的字段翻转 |
| **[官方]** | 无 (本单没引用任何厂商 datasheet 数值; ★凡器件级常数本单都标了 [0数据]★) |
| **[推算]** | 故障链 (栅极恒高⇒导通⇒RESET_N 被钉低) · assert 36 µs (戴维南) · 180 µA / 0.324 mW / 0.666 mW / 97 天 · unc 与 DRC 不变的推论 · 对照口径的 464/51/120 预测 |
| **[0数据]** | SoM PG 球位与极性 (TBD-01/TBD-12) · `Q_AND` 型号/Vgs(th)/封装 · SoC 复位释放要求 · 改名后丝印重叠风险 |
