# BOARD_TRIP_NETLIST_DIVERGENCE.md —— 板那一趟前的「板 ↔ 网表差异归属」权威口径 (ISS-340)

- 出处: `state/dispatch_briefs/ISS-340_hw_c1_divergence_attribution.md` · 执行: hw-lead (cont1) · 2026-11-22
- 判别闸: `HW/check_board_netlist_divergence_gate.py` (★自己跑出 C1 三类差异 + 逐条归桶, 只读★)
- 判定表 (逐条证据): `logs/iss340/01_c1_verdict_table.md`
- 基准板: `HW/PCB/demo_mainboard.kicad_pcb` · md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · ★本单零写板★
- 网表: `HW/netlist_v1.csv` · 闸入口对照: `state/check_pcb_nets.py` (★独立实现, 两套读数一致: 缺失 0 / 多余 2 / 同号异网 3★)

---

## §1 · 5 条差异总表 (★自跑结果: C1 缺失 0 · 多余 2 · 同号异网 3 = 5 条★)

| # | 差异 | 网表侧实际 | 板侧实际 | 归桶 | 证据 | 后果 |
|---|---|---|---|---|---|---|
| 1 | `C_VBUS_GND` pad1 (多余) | ★**网表里没有 MAIN_PCB 侧的 C_VBUS_GND** ⇒ `HW/netlist_v1.csv:10` 该行 `board` 列 = `CHG_BOARD` (被 `BOARD_FILTER=MAIN_PCB` 过滤) | 板上仍有封装: pad1 = `GND`, 直连铜 1.069 mm (3 段), 该网总走线 197.966 mm, 有 GND 铜区 | **C** | [实测] 网表 `:10` 原文 `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,...,C-01,CHG_BOARD,,` · [实测·板文件解析] pad1 实际网 `GND` · [实测] need key `boss_c_vbus_gnd_reserve_pad_20261117` (`state/fragments/pm.yaml:744`, **无 decision/decided_at ⇒ 未拍板**) | 等老板拍「留位 / 下板」; ★拍之前不许开工★ (拍「留位」⇒ 走 §2 的条件性 A; 拍「下板」⇒ 板那一趟 S2/B-1 自动收掉) |
| 2 | `C_VBUS_GND` pad2 (多余) | 同上, `HW/netlist_v1.csv:12` 的 `board` 列 = `CHG_BOARD` | 板上 pad2 = `VBUS_5V_CHG`, ★直连铜 0.000 mm · 该网总走线 0.000 mm · 无过孔 · 无铜区 ⇒ **该网在板上根本没有走线铜, pad2 是纯悬空焊盘**★ | **C** | 同 #1 (同一个 need key) · [实测·板文件解析] pad2 实际网 `VBUS_5V_CHG` | 同 #1 ⇒ **同一个决策, 一并拍** |
| 3 | `Q_PG` pad1 (同号异网) | `HW/netlist_v1.csv:59` ⇒ net = `PWR_GOOD` (占位脚序 1) · ★写法 A 已拍 (ISS-283 · G-1 裁决 · 老板 2026-11-17 09:49, 已落表 12:30:23)★ | 板上 pad1 = `PWR_ON` ⇒ **旧接法**, 直连铜 1.010 mm (4 段), 该网总走线 84.224 mm | **B** | [实测] 网表 `:59` note 写明「DMP3098L 引脚序 1=G / 2=S / 3=D ⇒ pad1=G=`PWR_GOOD`」+「板上 `Q_PG` land 仍按旧接法画 ⇒ 板那一趟必须重画这 3 根线」 · [实测] `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §③-2 独立复核: 板 pad1=`PWR_ON`/pad2=`BAT_SW`/pad3=`PWR_GOOD` (与本闸读数一致) · 目标网 `PWR_GOOD` 被 `J_CHG pad6` / `R_PU_PG pad2` / `TP_PG pad1` 佐证 | **板那一趟重画 `Q_PG` 的 3 根线** (pad1→`PWR_GOOD`, pad2=`BAT_SW` 不动, pad3→`PWR_ON`) ⇒ 单端低速/电源域 ⇒ **不触及高速/差分铜** ⇒ **要重跑 DRC + 重出 Gerber** ⇒ 板 md5 变 |
| 4 | `Q_PG` pad3 (同号异网) | `HW/netlist_v1.csv:61` ⇒ net = `PWR_ON` (占位脚序 3) | 板上 pad3 = `PWR_GOOD` ⇒ **旧接法**, 直连铜 0.567 mm (2 段), 该网总走线 62.772 mm | **B** | 同 #3 (同一次重画, 不额外增加工作量) | 同 #3 |
| 5 | `D_ESD_USB_D` pad1 (同号异网) | `HW/netlist_v1.csv:417` ⇒ net = `NET_USB_D_P_TYPEC` (串阻的 Type-C 侧); ★该网名是**已落表**的改动 (V-2 落表记录: 「把 `D_ESD_USB_D` pad1 的网名由 `USB_D_P_SRC` 改掉 ⇒ 板那一趟必须同趟改, 漏改 ⇒ 网表与板对不上」)★ | 板上 pad1 = `USB_D_P_SRC`, 直连铜 0.566 mm (2 段), 该网总走线 65.088 mm | **B** | [实测] 网表 `:417` evidence `[官方]` + note「USB-C 入口 ESD 阵列 (紧贴 J_USB_C) — Forlinx 载板指引要求 ESD 紧贴接口」 · [实测] `USB_D_P_SRC` 网在板上共 3 个焊盘 (`R_SER_USB_D_P` pad1 / `D_ESD_USB_D` pad1 / `J_SOM_P1` USB_D_P 脚), ★其中另 2 个与网表一致 ⇒ 只有 `D_ESD_USB_D.pad1` 错*★ · 目标网 `NET_USB_D_P_TYPEC` 被 `R_SER_USB_D_P` pad2 / `TP_USB_D_P` pad1 / `J_USB_C` padA6 / padB6 佐证 | **板那一趟把 `D_ESD_USB_D.pad1` 从 `USB_D_P_SRC` 挪到 `NET_USB_D_P_TYPEC`** ⇒ **与 S4 的 B-3/B-4/B-5 合并成同一次原子操作** (换 3 脚封装 + 挪到 ≤3.0 mm) ⇒ **要重跑 DRC + 重出 Gerber** ⇒ 板 md5 变 |

★**一句话结论**★: **A 桶 0 条 · B 桶 3 条 · C 桶 2 条 (同一个 need key)** ⇒ ★**现在没有任何一条差异能靠改网表消掉 ⇒ 「板 md5 不用动」的那部分要等 C 桶拍完才可能出现★**

---

## §2 · A 桶 (网表侧错 ⇒ 改网表就够, ★**板 md5 一个字节都不用动**★)

**当前 A 桶 = 0 条。** ★没有任何一条现存差异是「只改网表就能消掉」的★ ⇒ 本节列的是**条件性 A 桶** (= C 桶第 1/2 条拍成「留位」时才成立的那一条)。

### 条件性 A-1 (★仅当 `boss_c_vbus_gnd_reserve_pad_20261117` 拍成「留位」时成立★)

| 项 | 内容 |
|---|---|
| 改哪个文件 | `HW/netlist_v1.csv` |
| 改哪一行 | ★**`:10`** (net=`GND`) 与 ★**`:12`** (net=`VBUS_5V_CHG`) 两行的 ★**`board` 列**★ |
| 改成什么 | `CHG_BOARD` ⇒ **`MAIN_PCB`** |
| 要不要重生成脚表 | ★**要** ★(网表 md5 变 ⇒ 脚表/BOM 必须跟着重生成, 否则落表链头脱链)★ |
| 要不要重生成 BOM | ★**要** ★(`HW/netlist_v1.csv` 的 board 列进 BOM ⇒ 186 件那一档)★ |
| 要不要重出 Gerber | ★**不要** ★(板不动 ⇒ `HW/PCB/demo_mainboard.kicad_pcb` md5 保持 `611b869e…` ⇒ Gerber 不用重出; ⇒ ★这才是「板只改一次」能守住的那部分★)★ |
| 落点顺序 | ★**必须落在板那一趟【之前】** ★(铁律: 见页尾) ★——网表/脚表/BOM 改完之后, 板那一趟重跑生成器时看到的才是留位版★ |

### 条件性 A-2 (★仅当老板拍成「下板」时成立★ —— 但**不是** A 桶, 是 B 桶路径★)

- `HW/netlist_v1.csv` **不用改** (`:10` / `:12` 的 `board` 列本来就是 `CHG_BOARD`) ⇒ ★**网表侧零动作**★
- 板那一趟 S6 重跑生成器时按 `BOARD_FILTER="MAIN_PCB"` 自动把它剔掉 ⇒ 板 md5 变 ⇒ **Gerber 要重出** (收工件数 185)
- 代价: 失去一个 π 滤波电容的预留焊盘 (demo 板 Type-C 供电 · 不装电池 · 充电链在充电板 ⇒ 这颗电容在 demo 上无用途)

---

## §3 · B 桶 (板侧错 ⇒ ★**必须动板, 进板那一趟一次做完**★)

| 条 | 板那一趟要动什么 | 触及不触及高速/差分铜 | 要不要重跑 DRC + 重出 Gerber |
|---|---|---|---|
| #3 `Q_PG` pad1 | 重画 `Q_PG` 的 3 根线之一: pad1 的网 `PWR_ON` ⇒ **`PWR_GOOD`**; ★同批把 pad3 改成 `PWR_ON` (见 #4); pad2 = `BAT_SW` **不动**★ | ★**不触及** ★—— `PWR_GOOD` 网表原文写明「阻抗 单端」(开漏 PG 信号), `PWR_ON` 是负载使能轨 ⇒ 单端低速/电源域 | ★**要** ★ |
| #4 `Q_PG` pad3 | 同一次重画: pad3 的网 `PWR_GOOD` ⇒ **`PWR_ON`**; ★与 #3 是同一颗器件的同一次操作, 不许拆两趟★ | ★**不触及** ★ | ★**要** ★ |
| #5 `D_ESD_USB_D` pad1 | 把 `D_ESD_USB_D.pad1` 从 `USB_D_P_SRC` 挪到 **`NET_USB_D_P_TYPEC`** (串阻的 Type-C 侧) ⇒ ★**必须与 S4 的 B-3 (2→3 脚封装) / B-4 (挪到 `J_USB_C` ≤3.0 mm) / B-5 (D− 侧补 ESD) 合并成同一次原子操作**★ (换封装 ⇒ 挪位置 ⇒ 布线重跑 ⇒ 三条同一个操作) | ★**不触及高速时序, 但这是 90Ω 受控阻抗差分对的成员网** ★——`HW/netlist_v1.csv:291` 原文「差分阻抗 90Ω ±15% 受控阻抗」; USB 2.0 FS 单端 12 Mbit/s ⇒ 不涉及时序/长度敏感, ★**但挪这根 stub 时不许破坏 D+/D− 匹配与过孔对称 ⇒ DRC 必须带差分对规则跑**★ | ★**要** ★ |

### 与「板那一趟」其它已知项的关系 (★只增不改, 不新增板改项★)

| 板那一趟已知项 | 与本桶的关系 |
|---|---|
| ★**位号改名 (186 个 `_1`)** ★ (`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S1) | ★**无关** ★—— 不同器件、不同动作; ★但两者同在一趟 ⇒ 板 md5 仍只变一次★ |
| ★**B-1 ~ B-5 / B-8 板侧同步** ★ (§3-S2/S3/S4/S5) | ★**#5 就是 B-3/B-4/B-5 的对象 (S4)** ★ ⇒ 本桶不新增项, 只把判据写死; ★#1/#2 (C_VBUS_GND) 属 B-1 (S2), 但归 C 桶 ⇒ 见 §4★ |
| ★**布局修正 (ISS-265 方案 A)** ★ (§3-S6) | ★**#3/#4 = S6 追加行 `B11_Q_PG_LAND`** ★ (ISS-283 §③-2) ⇒ 已登记在 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §③-2 ⇒ 本桶只补铜长/风险口径 |
| ★**布线 45 → 0 (S8)** ★ | ★**板那一趟的「那三项板改 (Q_PG / ESD / 排针 land)」会动走线 ⇒ 必须与 S8 同一次做完** ★ (作业包 §1-⑥) ⇒ ★#3/#4/#5 **不许**单独动板 |
| ★**Gerber / 投产包重出** ★ | ★**必须重出一次** ★ —— B 桶 3 条都动板 ⇒ 板 md5 变一次 ⇒ Gerber 只重出这一次; ★漏重出 = 拿旧 Gerber 投板 = 2-4 周 + ¥4-8K★ |
| ★**`HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md`** | ★**INV-1** (板 md5 全项目只许变 1 次 ⇒ 全部 A 类步同趟) · ★**INV-2** (B 类步最后一次) · ★**INV-4** (老板 W-1/W-2/P7/A1/W-4 落地前不许跑 B 类步) ⇒ ★**#5 所在的 S4 卡在老板 W-1b/W-1c/W-2 (见 §4) ⇒ #5 不得先动** ★ |

---

## §4 · C 桶 (等老板拍板 ⇒ ★只列 need key + 题, **不代拍**★)

★**本单对 ISS-340 立项时 main 写的 3 条候选对应 (C_VBUS_GND↔`boss_c_vbus_gnd_reserve_pad_20261117` · Q_PG↔`boss_shutdown_semantics_and_loadswitch_20261117`+W-4 · D_ESD_USB_D↔`iss260_boss_a3_arch_and_model`/`boss_esd_model_axis_pending_20261117`) 的复核 = ★1 证实 / 2 推翻★** ★(逐条依据见 `logs/iss340/01_c1_verdict_table.md` §4.1)★ ⇒ ★**Q_PG 的写法 A 已拍并落表、D_ESD_USB_D 的 ESD 架构轴 A3=V-2=1 也已拍并落表 ⇒ 这两条是【板没跟】, 不是【在等老板】★★ ⇒ ★**真正卡老板的只剩下面这 1 个真待拍项** ★

| 条 | need key | 一句话题 | 现状 (★只列, 不给倾向性结论★) |
|---|---|---|---|
| #1 + #2 (`C_VBUS_GND` pad1/pad2, 同一个 key) | ★**`boss_c_vbus_gnd_reserve_pad_20261117`** ★ (`state/fragments/pm.yaml:744` · ★无 `decision`/`decided_at` ⇒ 未拍板★) | ★**`C_VBUS_GND` 这个预留位: 留还是不留?** ★ (★留位 ⇒ 186 件 + 改网表 board 列 + 重生成脚表/BOM, 板 md5 不用动; 下板 ⇒ 185 件 + 板那一趟 S2/B-1 自动收掉, Gerber 重出一次★) | ★**口径冲突 (必须由老板拍一次才收口)** ★: 作业包 §3-S2 (B-1) 与 main 2026-11-17 18:45 的板改清单都已把「`C_VBUS_GND` 下板 (186→185)」写死, ★而 pm.yaml 这条 need key 仍未拍 ⇒ 两个数互卡 ⇒ 谁都有动机「改板凑绿」⇒ 最坏 = 把它装回板上 = 2-4 周 + ¥4-8K★ ⇒ ★**本单不代拍, 只登记** ★ |
| ★**关联待拍项 (不在本 5 条之内)** ★ | ★**W-4 `Q_PG.3` 极性** ★ (板那一趟卡点表 §6 / `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-4 / 作业包 §1-⑤) | ★**`PWR_GOOD` 这条 `Q_PG.3` 的极性没定** ★ (★注: pm.yaml 的 `boss_w4_q_pg_topology_20261117` **已于 2026-11-17 09:49 拍过「写法 A」**; ★剩下的 `.3` 极性是另一问, 盘上 pm.yaml 登记表里没有它的 open 条目★) | ★**它不改变 #3/#4 的归桶** (脚序互换已拍, 极性是另一问) ★, ★但它被作业包 §4 列为「其余 22 条 unc 的死因之一」⇒ 布不通 ⇒ ★**必须与本桶同批拍, 否则 Q_PG 那 3 根线要重画第二遍** ★ |
| ★**关联待拍项 (不在本 5 条之内)** ★ | ★**W-1b/W-1c + W-2** ★ ⇒ pm.yaml `boss_esd_model_axis_pending_20261117` (`:681`, ★未拍板★) | ★**D+ 那颗 ESD 的真 OPN 型号 / D− 侧要不要补 ESD** ★ | ★**它不改变 #5 的归桶** (pad1 网名改动已落表 ⇒ 板未跟 ⇒ B) ★, ★但 #5 所在的 S4 整步卡在它 ⇒ 按 INV-4, ★它不落地, #5 不许动板★ ★(⇒ S4 的封装修正会连带改写 pad1 的网归属 ⇒ #5 必须与 S4 同批, 不许先单独挪 stub★)★ |

---

## ★铁律 (页尾)★

★**板只改一次 ⇒ A 桶的修复必须落在板那一趟【之前】; B 桶必须落在那一趟【之内】; C 桶没拍板之前不许开工**★

★**本单 (ISS-340) 的位置**: ★纯分析 + 新建判别闸 ⇒ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 前后不变) + **零改网表/原理图/BOM/脚表** + **零落表** + **零改既有闸** ⇒ ★§2 的 A 桶修法只写在本页与 `logs/iss340/01_c1_verdict_table.md`, 不动任何真源★ ★
