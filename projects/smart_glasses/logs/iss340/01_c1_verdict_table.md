# ISS-340 · C1 五条「网表侧 vs 板侧」差异归属判定表 (cont1)

- 任务书: `state/dispatch_briefs/ISS-340_hw_c1_divergence_attribution.md` · 派活方: 项目总工 (main) · cron fb67af40 · 2026-11-22 22:1x
- 执行: hw-lead (cont1 · 接管被 `openclaw:prompt-error: This operation was aborted` 掐死的子会话 cdc10bd9)
- 性质: ★**PCB 线 · 纯分析 + 新建判别闸 · 零写板**★
- 板: `HW/PCB/demo_mainboard.kicad_pcb` · md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · ★**本单不得动 (前后双证见 `logs/iss340/04_board_fingerprint.txt`)★**
- 判别闸: `HW/check_board_netlist_divergence_gate.py` (本单新建 · 只读 · 自己跑出 C1 三类差异)
- 一页口径: `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` (本单新建)
- 证据分级: **[实测]** = 本机实跑/本机实读原文 · **[推算]** = 由实测值推导

## 0. 归桶口径 (照抄任务书, 不自创)

- **A = 网表侧错** → 改网表就够, ★**板 md5 一个字节都不用动**★
- **B = 板侧错** → 必须动板, 进板那一趟 B-清单 (那一趟一次做完)
- **C = 等老板拍板** → 进待拍板页 (★本单**不代拍**, 只列 need key + 题★)

## 0.1 差异清单是**算出来的** (不是照抄任务书)

判别闸自跑 (★独立实现: 网表→焊盘映射 + 板文件文本解析 + C1 三类差异★, 不 import `state/check_pcb_nets.py`):
**网表推出焊盘 480 / 板上焊盘 833 (带网 482, NC 351) ⇒ C1 差异 = 缺失 0 · 多余 2 · 同号异网 3 ⇒ 合计 5 条**
⇒ 与 `state/check_pcb_nets.py` (★`bash state/pcbnew_py.sh state/check_pcb_nets.py`★) 的读数**逐项一致** ⇒ 两套独立实现互为交叉验证。

---

## 1. 五条差异逐条判定

| # | 差异 (ref.pad → 网表应/板实) | 归桶 A/B/C | 证据 (网表文件+行号+内容 / 板上 pad+有没有铜+铜长mm) | 后果 (板那一趟要动什么 / 板 md5 动不动) |
|---|---|---|---|---|
| 1 | `C_VBUS_GND` pad1 (多) | **C** | **网表侧 [实测]** `HW/netlist_v1.csv:10` 原文 = `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,...,C-01,CHG_BOARD,,` ⇒ **`board` 列 = `CHG_BOARD`** ⇒ 被生成器 `BOARD_FILTER="MAIN_PCB"` 过滤 ⇒ **MAIN_PCB 的 want 集合里没有 C_VBUS_GND** (`:12` 同)。**板上 [实测·板文件解析]** 该封装仍在: pad1 实际网 = `GND` · **有铜 = 是** · **直连铜(走线段)长 = 1.069 mm (3 段)** · 该网总走线 = 197.966 mm · 焊盘内过孔 = 0 · 该网有铜区 (GND zone) = 是 | **等老板拍 `boss_c_vbus_gnd_reserve_pad_20261117`** (★`state/fragments/pm.yaml:744` · 无 `decision`/`decided_at` ⇒ 未拍板★) ⇒ **拍之前不许开工**。拍「留位」⇒ 改 `HW/netlist_v1.csv:10` 与 `:12` 的 `board` 列 `CHG_BOARD`→`MAIN_PCB` + 重生成脚表/BOM ⇒ **A 侧动作, 板 md5 不用动, Gerber 不用重出**; 拍「下板」⇒ 板那一趟 S2/B-1 重跑生成器即自动消失 ⇒ **B 侧动作, 板 md5 要动, Gerber 重出一次** |
| 2 | `C_VBUS_GND` pad2 (多) | **C** | **网表侧 [实测]** `HW/netlist_v1.csv:12` 的 `board` 列 = `CHG_BOARD` (同第 1 条的过滤机理)。**板上 [实测·板文件解析]** pad2 实际网 = `VBUS_5V_CHG` · **有铜 = 是 (焊盘自身有铜面)** · **直连铜长 = 0.000 mm (0 段)** · **该网总走线 = 0.000 mm** · 焊盘内过孔 = 0 · 该网有铜区 = 否 ⇒ ★**`VBUS_5V_CHG` 在这块板上根本没有一根走线铜 ⇒ pad2 是纯悬空焊盘 (充电链在充电板, 本板不布这个网)—— 这是「它本就不属于 MAIN_PCB」的板侧旁证** ★[实测+推算] | 与第 1 条**同一个 need key, 一并拍** ⇒ 拍「留位」⇒ A 侧改网表两行 (板不动); 拍「下板」⇒ B 侧板那一趟删封装 (板要动, Gerber 重出) |
| 3 | `Q_PG` pad1 (同号异网) | **B** | **网表侧 [实测]** `HW/netlist_v1.csv:59` = `P1,PWR_GOOD,Q_PG,J_CHG pin6,Q_PG,DMP3098L (...P-MOS SOT-23...)`; `:60` net=`BAT_SW`; `:61` net=`PWR_ON` ⇒ 三行 `node1` 都是 `Q_PG` (无脚号 ⇒ 占位脚序) ⇒ **网表侧脚序 = 占位1=`PWR_GOOD` / 2=`BAT_SW` / 3=`PWR_ON`**。`:59` 的 note 自带裁决原文: 「★**ISS-283 · G-1 裁决 (2026-11-17 09:49 老板拍板「写法 A」)**★: DMP3098L 厂商引脚序 ★**1=G / 2=S / 3=D**★ ⇒ ★**pad1 = 栅极 G = PWR_GOOD**★ · pad2 = 源极 S = BAT_SW · pad3 = 漏极 D = PWR_ON★ ⇒ ★**板上 `Q_PG` land 仍按旧接法画 (pad1→PWR_ON / pad3→PWR_GOOD) ⇒ 板那一趟必须重画这 3 根线**★」 ⇒ **网表侧 = 已拍的一侧 ⇒ 板侧 = 旧接法**。**板上 [实测·板文件解析]** pad1 实际网 = `PWR_ON` · **有铜 = 是** · **直连铜长 = 1.010 mm (4 段)** · 该网总走线 = 84.224 mm · 焊盘内过孔 = 0 · 无铜区。**独立复核 [实测]** `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §③-2 写的板读数 (pad1=`PWR_ON` / pad2=`BAT_SW` / pad3=`PWR_GOOD`) **与本闸读数一致**; 目标网 `PWR_GOOD` 被 `J_CHG pad6` / `R_PU_PG pad2` / `TP_PG pad1` 佐证 | **板那一趟重画 `Q_PG` 的 3 根线** (pad1→`PWR_GOOD`, pad2=`BAT_SW` 不动, pad3→`PWR_ON`) ⇒ **单端低速/电源域 ⇒ 不触及高速/差分铜** (`PWR_GOOD` 网表原文写明「阻抗 单端」) ⇒ **必须重跑 DRC + 重出 Gerber** ⇒ **板 md5 要动** |
| 4 | `Q_PG` pad3 (同号异网) | **B** | **网表侧 [实测]** `HW/netlist_v1.csv:61` = `P1,PWR_ON,Q_PG,U_PWR_SW pin2,Q_PG,...` ⇒ **pad3 应当 = `PWR_ON`**。**板上 [实测·板文件解析]** pad3 实际网 = `PWR_GOOD` · **有铜 = 是** · **直连铜长 = 0.567 mm (2 段)** · 该网总走线 = 62.772 mm · 焊盘内过孔 = 0 · 无铜区; 目标网 `PWR_ON` 被 `U_PWR_SW pad2` / `R_PD_ON pad1` / `J_SOM_P3 pad88` 佐证 | 与第 3 条**同一次重画** (不额外增加工作量, 不许拆两趟) ⇒ **板 md5 要动** |
| 5 | `D_ESD_USB_D` pad1 (同号异网) | **B** | **网表侧 [实测]** (列序 `page,net,node1,node2,ref,...`): `:291` = `P6,USB_D_P_SRC,J_SOM_P1 pin92,R_SER_USB_D_P,NET_USB_D_P_SRC,...` · `:417` = `P1,NET_USB_D_P_TYPEC,D_ESD_USB_D,NET_USB_D_P_TYPEC,D_ESD_USB_D,TPD1E05U06DPYR (TI 单通道 ESD...)` (evidence `[官方]`, note「USB-C 入口 ESD 阵列 (紧贴 J_USB_C) —— Forlinx 载板指引要求 ESD 紧贴接口」) · `:431` = `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,...` ⇒ **`D_ESD_USB_D` pad1 应当落 `NET_USB_D_P_TYPEC`** (串阻的 Type-C 侧)。**板上 [实测·板文件解析]** 名为 `USB_D_P_SRC` 的网共 3 个焊盘 = `R_SER_USB_D_P` pad1 / `D_ESD_USB_D` pad1 / `J_SOM_P1` 的 USB_D_P 脚 (板文件行 5786 / 13016 / 18683) ⇒ ★**只有 `D_ESD_USB_D.pad1` 错** ★(另两个在网表里本来就挂 `USB_D_P_SRC` ⇒ 与板一致 ⇒ **不用动**★)。pad1 实际网 = `USB_D_P_SRC` · **有铜 = 是** · **直连铜长 = 0.566 mm (2 段)** · 该网总走线 = 65.088 mm · 焊盘内过孔 = 0 · 无铜区; 目标网 `NET_USB_D_P_TYPEC` 被 `R_SER_USB_D_P` pad2 / `TP_USB_D_P` pad1 / `J_USB_C` padA6 / padB6 佐证 | **板那一趟把 `D_ESD_USB_D.pad1` 从 `USB_D_P_SRC` 挪到 `NET_USB_D_P_TYPEC`** ⇒ ★**必须与 S4 的 B-3 (2→3 脚封装) / B-4 (挪到 `J_USB_C` ≤3.0 mm) / B-5 (D− 侧补 ESD) 合并成同一次原子操作** ★(换封装 ⇒ 挪位置 ⇒ 布线重跑) ⇒ ★**不是「单独挪一根 stub」这么轻** ★ ⇒ **要重跑 DRC + 重出 Gerber** ⇒ **板 md5 要动** |

---

## 2. 桶计数 (5 条差异口径, 不含关联待拍项)

- **A 桶 = 0 条** ⇒ ★**现在没有任何一条差异能靠改网表消掉 ⇒ 「板 md5 不用动」的那部分, 要等 C 桶拍完才可能出现** ★
- **B 桶 = 3 条** (`Q_PG` pad1 / `Q_PG` pad3 / `D_ESD_USB_D` pad1) ⇒ 全部是**同号异网**, 全部集中在「重画 / 挪线」⇒ **不触及高速时序** (★但第 5 条所在的网是 90Ω 受控阻抗差分对成员, 见 §4 修正★) ⇒ **必须重跑 DRC + 重出 Gerber**
- **C 桶 = 2 条** (`C_VBUS_GND` pad1 / pad2) ⇒ **同一个 need key** ⇒ **不代拍**

## 3. 关联的队列外待拍项 (不计入上面 5 条, 只登记)

- ★**W-4 `Q_PG.3` 极性** ★: 板那一趟卡点表 (`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §6-S8) 与 `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-4 都把它列为**卡老板项**, 且作业包 §4 把它列为「其余 22 条 unc 的死因之一」⇒ ★**它不改变第 3/4 条的归桶** ★(脚序互换已由 ISS-283 G-1 拍板「写法 A」, `.3` 极性是另一问) ★, ★**但它必须与 C 桶同批拍** ★⇒ 否则 Q_PG 那 3 根线要重画第二遍。
  ★**口径订正 [实测]**: `state/fragments/pm.yaml` 里的 `boss_w4_q_pg_topology_20261117` (`:626`) **已于 2026-11-17 09:49 拍板** (写法 A) ⇒ ★**盘上 pm.yaml 登记表里没有「`.3` 极性」这条 open 项** ★⇒ 本闸的 C 桶只认得 `boss_c_vbus_gnd_reserve_pad_20261117`; `.3` 极性属**板那一趟卡点表侧**的待拍项, 本单只登记不代拍。
- ★**W-1b/W-1c + W-2** ★ (pm.yaml `boss_esd_model_axis_pending_20261117` `:681`, ★**未拍板**★): D+ 那颗 ESD 的真 OPN 型号 + D− 侧要不要补 ESD ⇒ ★**它不改变第 5 条的归桶** (pad1 网名改动已落表 ⇒ 板未跟 ⇒ B) ★, ★**但第 5 条所在的 S4 整步卡在它** ★⇒ 按 INV-4, 它不落地, S4 不许动板。

## 4. 本轮对任务书 §-3 三条底稿的复跑结论 (★逐条交代★)

| 底稿 | 复跑结论 |
|---|---|
| 事实 1 (`C_VBUS_GND` 多余 2 条) | ★**已复跑, 与底稿一致** ★ —— `:10` / `:12` 的 `board` 列确实 = `CHG_BOARD`; 板上确实留着 2 个 pad。★**新增实测**: pad1 有 1.069 mm 直连铜 + GND 铜区, 而 **pad2 直连铜 0.000 mm 且 `VBUS_5V_CHG` 在本板总走线 0.000 mm ⇒ pad2 是纯悬空焊盘** ⇒ 这是「它本就不属于 MAIN_PCB」的板侧旁证 (底稿没写这一层) |
| 事实 2 (`Q_PG` 同号异网 pad1/pad3) | ★**已复跑, 与底稿一致** ★ —— net 列依次 = `PWR_GOOD` / `BAT_SW` / `PWR_ON`, 脚序走占位; 板实 pad1=`PWR_ON` / pad2=`BAT_SW` / pad3=`PWR_GOOD` ⇒ **pad1↔pad3 对调**成立, 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §③-2 的板读数逐脚一致。★**口径订正**: 底稿说「另有一条队列外待拍项 `W-4 Q_PG.3` 极性」—— 盘上 pm.yaml 的 `boss_w4_q_pg_topology_20261117` **已拍板** (2026-11-17 09:49), 未拍的是**板那一趟卡点表侧的 `.3` 极性** ⇒ 归桶不变 (仍是 B), 但**待拍项的位置要写对** (见 §3) |
| 事实 3 (`D_ESD_USB_D` pad1 同号异网) | ★**已复跑, 与底稿一致** ★ —— `:291` / `:417` / `:431` 三行确认; ★**上一趟说的「3 处都要改」确实是错的** ★: `R_SER_USB_D_P` pad1 与 `J_SOM_P1` 的 USB_D_P 脚在网表里本来就挂 `USB_D_P_SRC` ⇒ 与板一致 ⇒ **不用动**。★**但底稿的「单端低速 ⇒ 不触及高速/差分铜」这一句要修正** ★: `:291` 的 note 写明「★**差分阻抗 90Ω ±15% 受控阻抗**★」⇒ ★**`USB_D_P_SRC` / `NET_USB_D_P_TYPEC` 是 90Ω 受控阻抗差分对的成员网** ★ ⇒ USB 2.0 FS 单端 12 Mbit/s ⇒ **不涉及时序/长度敏感** (这半句成立), ★**但挪这根 stub 时不许破坏 D+/D− 匹配与过孔对称 ⇒ DRC 必须带差分对规则跑** ★。★**另一处修正**: 板那一趟已计划把 `D_ESD_USB_D` 换成 3 脚封装并挪到 `J_USB_C` ≤3.0 mm (S4 的 B-3/B-4/B-5) ⇒ ★**这条不是「1 个焊盘 + 1 根 stub」的轻量动作, 必须与 S4 合并成一次原子操作** ★ |

## 4.1 ★★本单对「ISS-340 立项时 main 写的 3 条候选对应」的复核结论 (★证实 1 条 / 推翻 2 条★) ★★

ISS-340 的 issue 条目 (★`state/issue_log.yaml` 的 ISS-340 `desc` 字段★) 与任务书 §-3 事实 3 写了 main 的候选对应:
`C_VBUS_GND` ↔ `boss_c_vbus_gnd_reserve_pad_20261117` · `Q_PG` ↔ `boss_shutdown_semantics_and_loadswitch_20261117` + 队列外 `W-4 Q_PG.3 极性` · `D_ESD_USB_D` ↔ `iss260_boss_a3_arch_and_model` / `boss_esd_model_axis_pending_20261117`。
★**本单逐条复核 (live `state/fragments/pm.yaml` 实读, 2026-11-22)★**:

| main 的候选对应 | 复核结论 | 依据 [实测] |
|---|---|---|
| `C_VBUS_GND` ↔ `boss_c_vbus_gnd_reserve_pad_20261117` | ★**证实** ★ ⇒ **C 桶, 不代拍** | 该 key 在 live pm.yaml `:744` · `to: boss` · **无 `decision`/`decided_at` ⇒ 未拍板**; item 原文写明「留位还是下板」+「不拍的代价 = 那一趟收工时 S2 必假红, 两个数互卡」 |
| `Q_PG` ↔ `boss_shutdown_semantics_and_loadswitch_20261117` (+ `W-4 Q_PG.3 极性`) | ★**推翻 (主对应不成立)** ★ ⇒ **第 3/4 条维持 B 桶** | ★**该 key 的 item 原文 (`:733`) 谈的是「A4/A5 = 关机语义 + 负载开关选型追认 (`TPS22991RAA` 已落)」⇒ 那是 `U_EN_SW` 的事, 全文【没有出现 `Q_PG`】★; 而 `Q_PG` 的 pad1↔pad3 脚序 = ★**写法 A 已于 2026-11-17 09:49 老板拍板并已落表** ★(`:59`/`:61` 的 note 带裁决原文) ⇒ 板只是没跟 ⇒ **板那一趟重画 = B**。★`W-4 .3` 极性另立**关联待拍项** (队列外, 见 §3) ★, **不改第 3/4 条的归桶** ★ |
| `D_ESD_USB_D` ↔ `iss260_boss_a3_arch_and_model` / `boss_esd_model_axis_pending_20261117` | ★**推翻 (主对应不成立)** ★ ⇒ **第 5 条维持 B 桶** | ★**ESD 架构轴 A3 = V-2 = 1 (2 脚单通道) 已于 2026-11-17 09:49 老板拍板并已落表** ★(pm.yaml `:596` 的 item + `:598` 的 decision) ⇒ ★**`D_ESD_USB_D` pad1 的网名改动就是那次落表的内容** ★(pm.yaml `:599`-`:602` 明写: 「V-2 的落表动作 = 把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改掉 ⇒ ★**板那一趟必须同趟改 `D_ESD_USB_D` pad1 的网名 (漏改 ⇒ 网表与板对不上)**★」) ⇒ ★**网表侧 = 已拍的一侧, 板未跟 ⇒ B 桶** ★。★**key 名也失效**: `iss260_boss_a3_arch_and_model` 在 live pm.yaml 里【不存在】(只在 `state/.lastgood/hw.yaml` 与旧文本里) ⇒ 现存 open key `boss_esd_model_axis_pending_20261117` (`:681`) 只管 ★**① W-1b/W-1c 真 OPN 型号 + ② W-2 D− 侧要不要补 ESD** ★ ⇒ 它管的是 ★**S4 的封装/位置** ★, ★**不管 pad1 的网归属** ★ ⇒ 降为**关联待拍项** (见 §3) ★ |

★**净结论**: ★5 条差异 ⇒ **A 桶 0 条 / B 桶 3 条 / C 桶 2 条 (同一个 key)** ★; ★main 的 3 条候选对应 = **1 证实 + 2 推翻** ★ ⇒ ★**真正卡老板的只剩「C_VBUS_GND 留/不留」这一个真待拍项** ★(另加 3 个关联项: W-4 `.3` 极性 / W-1b·W-1c 型号轴 / W-2 D− 侧补不补) ⇒ ★**板那一趟的开工前置因此比立项时写的少 2 项★**

## 5. 板那一趟开工前必须先落哪几条

- ★**必须先落 (C 桶, 拍板前置)**: `boss_c_vbus_gnd_reserve_pad_20261117` (C_VBUS_GND pad1+pad2 留位 / 下板) —— ★**没拍之前板那一趟不许开工** ★(拍「留位」⇒ A 侧改网表两行 + 重生成脚表/BOM; 拍「下板」⇒ 板那一趟新增一条板侧动作)
- ★**必须先落 (与 B 桶同批拍, 否则要重画第二遍)**: ① **W-4 `Q_PG.3` 极性** (⇒ 影响 Q_PG 那 3 根线能不能一次画对) ② **W-1b/W-1c + W-2** (⇒ S4 的封装修正会连带改写 pad1 的网归属 ⇒ `D_ESD_USB_D.pad1` 不能先单独挪)
- ★**必须先落 (A 桶前置条件)**: 无 —— A 桶当前为空; 唯一可能产生 A 桶条目的, 就是 C 桶拍成「留位」之后对 `HW/netlist_v1.csv:10` / `:12` 的 `board` 列改写 + 重生成脚表/BOM (★改网表也要在板那一趟【之前】做完, 否则 BOM/脚表与板不一致★)

## 6. 零写板声明

- 本单**未**写入 `HW/PCB/demo_mainboard.kicad_pcb`: md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / 4940213 bytes ⇒ 前后双证见 `logs/iss340/04_board_fingerprint.txt`
- 本单**未**改 `HW/netlist_v1.csv` (md5 `6aee500e60ba0732f83a9cf557ba90ab`) / 原理图 / BOM / 脚表 ⇒ **A 桶修法只写在本页与 `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` 里**
- 本单**未**写 `state/issue_log.yaml` (由 main 签收) · **未**改任何既有闸
