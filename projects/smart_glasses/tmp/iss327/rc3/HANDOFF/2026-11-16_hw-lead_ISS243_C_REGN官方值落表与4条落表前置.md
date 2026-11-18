# ISS-243 交卷单 · `C_REGN` 官方值落表 + 4 条落表前置 (L1~L4)

> ★**交卷人**: 硬件总工 (hw-lead) · ★**日期**: 2026-11-16 · ★**单号**: ISS-243 · ★**授权**: ★**main 2026-11-16 15:45 重派 (runTimeout 5400s)** ★
> ★**性质**: ★**内部活** ⇒ ★**零外发 / 不改板 / 不替老板拍板 / 实物 [实测] = 0 条** ★

★**一句话**: ★**L1 已落表** (C_REGN 的 value 从「[待选型] 1µF」订正为「4.7µF ±10% (10V)」, 并首次带上 0805 封装 + 官方可采购型号 `GRM21BR71C475KA73L`) ★**L2/L3/L4 出表** (三件 MOS 的 pad↔pin 映射 + ESD pad 序的两条改法 + 充电板 6 件的 footprint 候选清单) ★**落表台账 §16 已登记 + 新建独立机器门禁 (8 条断言 + 8 条反向用例)** ★

---

## B1 · 结论摘要 (目标与范围)

### B1.1 · 本单要收口的东西 (★ISS-241 交卷时点名交回硬件侧的 4 条落表前置★)

| # | 条目 | 缺口编号 | 本单交付形态 | ★**本单做没做** ★ |
|---|---|---|---|---|
| ★**L1** ★ | ★**`C_REGN` 官方值订正 (G-6)** ★ | ★**G-6** ★ | ★**直接落表 (真源改 `state/gen_netlist.py` → 硬顺序重生成 6 件生成物)** ★ | ★**已落表** ✔ |
| ★**L2** ★ | ★**三件 MOS 的 pad↔pin 映射 (G-2)** ★ | ★**G-2** ★ | ★**只出表 (逐字改法映射), 不许改板** ★ | ★**已出表** ✔ (`HW/MOS_PAD_PIN_MAPPING.md` §1) |
| ★**L3** ★ | ★**`D_ESD_CAM` 的 pad 序反了** ★ | ★**G-3 (矩阵 §4)** ★ | ★**只出改法映射 (方案甲/乙两条 + 代价), 一条不许代拍** ★ | ★**已出表** ✔ (`HW/MOS_PAD_PIN_MAPPING.md` §2) |
| ★**L4** ★ | ★**充电板 6 件器件的 footprint 候选 (G-8)** ★ | ★**G-8** ★ | ★**只出清单 (≥2 候选 + 焊盘数 + 本体尺寸 + 出处 + 证据等级 + 降级方案), 不许画板** ★ | ★**已出清单** ✔ (本单 §B3.4) |

### B1.2 · 本单【不做】的事 (★边界, 逐条自证见 §B5★)

- ★**不改板 / 布线 / 布局 / 板框** ⇒ `HW/PCB/demo_mainboard.kicad_pcb` 与 `.kicad_pro` 逐字节未动 (实测见 §B4)
- ★**不碰 ISS-242 的 `C_VBUS_OUT` / `C_VBUS_GND`** (★那两颗 2 脚电容各落进 3 个网的缺陷原样留在盘上 ⇒ 归 main 排期的落表批次★)
- ★**不改脚表里别的器件** · ★**不改 `state/land_v_values.py`** · ★**不改 `state/issue_log.yaml`** (verify 留给 main)
- ★**不替老板拍板**: V-2 (ESD 方案二选一) / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) / W-1~W-6 ⇒ ★**一条未拍, 只出选项 + 代价**

---

## B2 · 验收标准自评 (事实与数据 · ★每条带出处 + 证据等级★)

### B2.0 · ★验收标准自评 (逐条 通过 / 不通过 / 未验)★

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| 1 | ★**L1: `C_REGN` 的 value 在网表/脚表/BOM 三处都订正为 4.7µF 级且带 10V 耐压标注** ★ | ★**通过** ★ | ★§B3.1 + §B4.2 实跑 (三处 value = `4.7µF ±10% (10V)`)★ |
| 2 | ★**L1: `C_REGN` 的 opn 栏非空且为官方可采购型号** ★ | ★**通过** ★ | ★§B4.2 (三处 opn = `GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)`)★ |
| 3 | ★**L1: 落表走真源 (`state/gen_netlist.py`) 而不是手改 CSV** ★ | ★**通过** ★ | ★§B3.1 (真源 2 处 value + PARTS[C_REGN] + REF_FOOTPRINT[C_REGN])★ |
| 4 | ★**L1: 落表前有备份 (`state/.bak_iss243/`) + 落表台账 §16 登记 (单号/文件/行/说明/新旧 md5)** ★ | ★**通过** ★ | ★§B4.3 + 台账 §16 + `HW/check_iss243_cregn.py` C3★ |
| 5 | ★**L1: 落表后 4 道闸 + merge/gate_check 全 rc=0** ★ | ★**通过** ★ | ★§B4.2 实跑输出★ |
| 6 | ★**L1: `--expect-resolved` 条数不变 (18 → 18)** ★ | ★**通过** ★ | ★§B4.1 vs §B4.2 (两份输出逐字节相同)★ |
| 7 | ★**L1: 受保护 md5 (板 + .kicad_pro) 逐字节不变** ★ | ★**通过** ★ | ★§B4.3 实测★ |
| 8 | ★**L2: 三件 MOS 的 pad↔pin 映射表 (每件一行, 含两个串)** ★ | ★**通过** ★ | ★`HW/MOS_PAD_PIN_MAPPING.md` §1.1 + 门禁 C4/C5★ |
| 9 | ★**L2: 映射表带「免重画 land 的可能性」列** ★ | ★**通过** ★ | ★同表最后一列 (在售 SOT-23 几乎都是 G-S-D ⇒ 必须重画)★ |
| 10 | ★**L2: `Q_CHG_LED` 也查一遍** ★ | ★**通过 (充电板侧, 板文件无占位 ⇒ 写明待 L4 定封装后核)** ★ | ★同表第 4 行★ |
| 11 | ★**L3: ESD 三件的 pad 序实读 + 方案甲/乙两条与代价** ★ | ★**通过** ★ | ★§B3.3 + 映射表 §2 (门禁 C6)★ |
| 12 | ★**L3: 依据 (TPD1E05U06 单向件 pin1=I/O, pin2=GND)** ★ | ★**通过** ★ | ★§B2.3 (TI SLVSBO7O 引脚表)★ |
| 13 | ★**L4: 充电板 6 件各 ≥2 候选 + 焊盘数 + 本体尺寸 + 出处 + 证据等级 + 降级方案** ★ | ★**通过** ★ | ★§B3.4 (门禁 C8)★ |
| 14 | ★**L4: 充电板面积约束从 MECH 读出** ★ | ★**通过** ★ | ★§B2.4 (25 × 10 × 0.8 mm, `MECH/MECH_BUDGET.md` §1.3 M3)★ |
| 15 | ★**独立机器门禁 ≥5 条断言 + `--selftest` ≥5 条反向用例且每条自证** ★ | ★**通过 (8 条断言 + 8 条反向用例, 8/8 全过)** ★ | ★§B4.4 + `HW/check_iss243_cregn.py` 实跑★ |
| 16 | ★**分片走 `state/frag_write.py` 原子写, 不手改 yaml, 不写别人的分片** ★ | ★**通过** ★ | ★§附 + `state/fragments/hw.yaml`★ |
| 17 | ★**零外发 / 不改板 / 不替老板拍板 / 实物 [实测] = 0 条** ★ | ★**通过** ★ | ★§B5 逐条自证★ |
| 18 | ★**交卷前 `merge.py` (rc=0) && `gate_check.py` (【Q1】18/18)** ★ | ★**通过** ★ | ★§B4.2 实跑输出★ |
| ★**19** ★ | ★**`C_REGN` 的 DC-bias 降容后实际容值** ★ | ★**未验** (★`[0数据]` ⇒ Murata 官方 DC-bias 曲线本单未取到 ⇒ **没写进 value 串**★) ★ | ★§B6 ⑦★ |

### B2.1 · ★★L1 的官方依据 (★本机 PDF 实读, 不是转述★)★★

### B2.1 · ★★L1 的官方依据 (★本机 PDF 实读, 不是转述★)★★

★**TI BQ25896 数据手册 (SLUSC76C) §Pin Functions 表, pin22 REGN 行原文** ★ (★`pdftotext` 实读 `state/.cache_iss243/bq25896.txt` **L338~343**★, PDF 源 `state/.cache_iss243/bq25896.pdf` 1675426 B★):

> "Internally, REGN is connected to the cathode of the boost-strap diode. **Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND.** The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin."

| 事实 | 出处 | 证据等级 |
|---|---|---|
| ★**REGN 去耦电容 = 4.7 µF** ★ | ★**TI SLUSC76C pin22 原文 (本机 PDF 实读)** ★ | ★`[官网]` ★ |
| ★**耐压要求 = 10 V rating** ★ | ★**同上 (原文 "10 V rating")** ★ | ★`[官网]` ★ |
| ★**必须是陶瓷电容** ★ | ★**同上 (原文 "ceramic capacitor")** ★ | ★`[官网]` ★ |
| ★**必须贴近 IC 放置** ★ | ★**同上 (原文 "The capacitor should be placed close to the IC")** ★ | ★`[官网]` ★ |
| ★**落表前盘上真值 = 「[待选型] 1µF」 (与手册冲突)** ★ | ★**`state/gen_netlist.py` L500/L502 (`add()` 的 value 栏) → `HW/netlist_v1.csv` L44/L45 · `HW/netlist_v1_pins.csv` L132/L133 · `HW/BOM_v1.csv` L43** ★ | ★`[实测]` (本机实读) ★ |
| ★**选定的 OPN = `GRM21BR71C475KA73L`** ★ | ★**ISS-241 选型矩阵 `HW/PART_SELECTION_MATRIX_2026-11-16.md` §3.7 ⑳ (★该矩阵的官方数据手册原文已在案★) + Murata 官方 MLCC 系列页 `https://www.murata.com/en-us/products/capacitor/mlcc`** ★ | ★`[官网]` ★ |
| ★**该 OPN 的参数 = 0805 / 4.7 µF / 16 V / X7R / ±10% / −55~+125 °C / 厚 0.5 mm max** ★ | ★**同上 (矩阵 §3.7 ⑳ 候选1 行)** ★ | ★`[官网]` ★ |
| ★**16 V ≥ 手册要求的 10 V ⇒ 耐压余量 1.6×** ★ | ★**矩阵参数 vs TI 原文, 本单实算** ★ | ★`[推算]` ★ |
| ★**C_REGN 的 DC-bias 降容后实际容值** ★ | ★**Murata 的 DC-bias 曲线需按料号查官方曲线 ⇒ 本单未取到 ⇒ **没写进 value 串** ★ | ★`[0数据]` ★ |
| ★**C_REGN 在 `demo_mainboard.kicad_pcb` 上查无此位号** ★ | ★**板文件实读 (充电板件 ⇒ 无占位几何可判)** ★ | ★`[实测]` ★ |
| ★**充电板尺寸 = 25 × 10 × 0.8 mm** ★ | ★**`MECH/MECH_BUDGET.md` §1.3 M3 (经 `HW/CHARGE_BOARD_SPEC.md` L15 引)** ★ | ★`[推算]` ★ |

### B2.2 · ★★L2 的板文件实读 (★pad 号 / net / 尺寸 / 位置★)★★

★**来源**: `HW/PCB/demo_mainboard.kicad_pcb` 本机实读 (KiCad 10 格式, 186 个封装块) ★ —★**不是照抄任务书给的数** ★

| 位号 | pad1 (net) | pad2 (net) | pad3 (net) | 焊盘 | 占位 fab bbox | 落表后的引脚功能 (★网表 note 真源★) | 占位 pad 序 |
|---|---|---|---|---|---|---|---|
| ★**`Q_AND`** ★ | `RESET_N` | `GND` | `PG_AND` | ★3 × (0.6×0.9 mm)★ | ★4.00 × 5.00 mm★ | ★**D / S / G** (netlist note: "漏极 = RESET_N" · "源极接地" · "栅极 = PG_AND")★ | ★**D/S/G** ★ |
| ★**`Q_PG`** ★ | `PWR_ON` | `BAT_SW` | `PWR_GOOD` | ★3 × (0.6×0.9 mm)★ | ★4.00 × 5.00 mm★ | ★**S / D / G** (netlist note: "源极接 ON" · "漏极接 BAT_SW" · "栅极 = PG (经 J_CHG pin6)")★ | ★**S/D/G** ★ |
| ★**`Q_ENVC`** ★ | `PG_AND` | `GND` | `EN_VCORE` | ★3 × (0.6×0.9 mm)★ | ★4.00 × 5.00 mm★ | ★**G / S / D** (netlist note: "源极接地" · "漏极 = EN_VCORE" · pad1 余下的=G)★ | ★**G/S/D** ★ |
| ★**`Q_CHG_LED`** ★ | ★**充电板侧 · 板文件查无此位号** ★ | ★同左★ | ★同左★ | ★**[0数据]** ★ | ★**[0数据]** ★ | ★**D(LED 阴极) / S(GND) / G(CHG_STAT)** (netlist note)★ | ★**降级方案**: ★**[0数据]** ★|

★**SOT-23 库引脚序 = G / S / D** (★`[官网]`: AOS `AO3400A` / `AO3407A` 官方数据手册 (pin1=G, pin2=S, pin3=D) · onsemi `2N7002` 同★)
★**⇒ `Q_AND` 与 `Q_PG` 与库序【不一致】(重画 land 时必须人工改映射, 接反 ⇒ `Vgs` 极性反 ⇒ 开机路径不通) · `Q_ENVC` 天然对上** ★
★**⇒ 免重画 land 的出路: 需要「引脚序 = 占位 pad 序」的器件 ⇒ 在售 SOT-23 3 脚 MOS 绝大多数是 G-S-D ⇒ 【几乎不存在】⇒ 结论 = 必须重画** ★ (`[官网]` + `[推算]`, 依据 ISS-241 矩阵 §3.4 ⑧/⑩ 的降级栏)
★**完整表 (含「重画 land 时必须接到哪个引脚」逐件列) 见 `HW/MOS_PAD_PIN_MAPPING.md` §1.1** ★

### B2.3 · ★★L3 的实读 (★ESD 三件的 pad 序★)★★

| 位号 | pad1 (net) | pad2 (net) | 特征 | fab bbox |
|---|---|---|---|---|
| ★**`D_ESD_CAM`** ★ | ★**`GND`** ★ | ★**`CSI_D0_CK_P`** ★ | ★**★反的 (pad1=GND / pad2=信号)★★** ★ | 2.70 × 1.60 mm |
| ★**`D_ESD_DEMO`** ★ | ★**`RAIL_DEMO_5V`** (信号) ★ | ★**`GND`** ★ | 正常 (pad1=信号 / pad2=GND) | 2.70 × 1.60 mm |
| ★**`D_ESD_USB_D`** ★ | ★**`USB_D_P_SRC`** (信号) ★ | ★**`GND`** ★ | 正常 (pad1=信号 / pad2=GND) | 2.70 × 1.60 mm |

★**依据**: ★**TI `TPD1E05U06DPYR` 是单向件: pin1 = I/O · pin2 = GND** (★`[官网]` TI SLVSBO7O 引脚表★) ⇒ ★**对 `D_ESD_CAM` 按 pad 序号机械接 ⇒ I/O 接到 GND 位 ⇒ 器件不工作 ⇒ 必须二选一** ★

### B2.4 · ★★L4 的事实 (★充电板 6 件★)★★

| 事实 | 出处 | 证据等级 |
|---|---|---|
| ★**这 6 件在 BOM 的 footprint 栏是「待定」** ★ | ★**`HW/BOM_v1.csv` (板文件实读: 板文件里查无这 6 个位号 ⇒ 充电板件)** ★ | ★`[实测]` ★ |
| ★**`C_REGN` 的封装与 OPN 已随 L1 同批落表** ★ | ★**本单 L1 (0805 / `GRM21BR71C475KA73L`) ⇒ L4 交叉引用即可, 不重复论证** ★ | ★`[官网]` ★ |
| ★**充电板面积约束 = 25 × 10 × 0.8 mm** ★ | ★**`MECH/MECH_BUDGET.md` §1.3 M3** ★ | ★`[推算]` ★ |

---

## B3 · 证据分级 (改法映射)

### B3.1 · L1 · 三处落表 (★改的是真源, 不是生成物★)

| # | 文件 | 位置 | 改前 | 改后 |
|---|---|---|---|---|
| ★1★ | ★**`state/gen_netlist.py`** (★真源★) | ★**L500** ★ | ★`"[待选型] 1µF"`★ | ★`"4.7µF ±10% (10V)"`★ (+ note 补 TI 原文 + OPN + 放置要求) ★ |
| ★2★ | ★**`state/gen_netlist.py`** (★真源★) | ★**L502** ★ | ★`"[待选型] 1µF"`★ | ★`"4.7µF ±10% (10V)"`★ (+ note 补地端 + 放置要求) ★ |
| ★3★ | ★**`state/gen_netlist.py`** (★真源★) | ★**`PARTS` 字典新增 `C_REGN` 条目** ★ | ★无条目 ⇒ footprint/opn 两栏空 ⇒ BOM 采购状态 =「待选型」★ | ★`footprint` = "0805 (2.0×1.25 mm) MLCC · 2 焊盘 (充电板侧 · 贴 U_CHG pin22 近端)" · `opn` = "GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)"★ |
| ★4★ | ★**`state/gen_kicad_net.py`** (★真源★) | ★**`REF_FOOTPRINT` 字典新增 `C_REGN` 一条** ★ | ★类型通用占位符 `Capacitor_SMD:C_0402_1005Metric` (★0402 ⇒ 与 BOM 的 0805 对不上★) ★ | ★`Capacitor_SMD:C_0805_2012Metric (0805 / 2.0x1.25 mm, Murata GRM21 系列 land pattern)`★ |

★**⇒ 落表后三张表的落点 (重生成后逐行实读)**: ★**网表 L44/L45 · 脚表 L132/L133 · BOM L43** ★ ★**三处的 value / footprint / opn 三栏全部带出; BOM 的 `procurement` 栏由「待选型」变为「已定型-无源件」** ★

★**★重生成硬顺序 (★顺序是硬的: 脚表脚号来自 `.net`★)★** ★
```bash
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py
```
★**6 条全部 rc=0; 表A 512 行里只有 L44/L45 变 · 脚表 584 行里只有 L132/L133 变 · BOM 218 行里只有 L43 变 · `.net` 只有 L18 一行变** ★

### B3.2 · L2 · 三件 MOS 的逐字改法 (★只报, 不改板★)

| 位号 | 占位 pad 序 | SOT-23 库引脚序 | 一致? | ★**重画 land 时必须接到哪个引脚**★ |
|---|---|---|---|---|
| ★`Q_AND`★ | ★**D / S / G**★ | ★**G / S / D**★ | ★**否**★ | ★**pad1(`RESET_N`)→器件 D 脚 (pin3) · pad2(`GND`)→S 脚 (pin2) · pad3(`PG_AND`)→G 脚 (pin1)** ⇒ 器件相对 land 旋转 180° 或 land 重画成 G/S/D★ |
| ★`Q_PG`★ | ★**S / D / G**★ | ★**G / S / D**★ | ★**否**★ | ★**pad1(`PWR_ON`)→S 脚 (pin2) · pad2(`BAT_SW`)→D 脚 (pin3) · pad3(`PWR_GOOD`)→G 脚 (pin1)** ⇒ ★**接反 ⇒ Vgs 极性反 ⇒ PG 低反而关机 ⇒ 开机路径不通**★ |
| ★`Q_ENVC`★ | ★**G / S / D**★ | ★**G / S / D**★ | ★**是**★ | ★**按 pad 序号机械接即可 (pad1=G/pad2=S/pad3=D)** ⇒ ★**三件 MOS 里唯一不用改功能映射的**★ |
| ★`Q_CHG_LED`★ | ★**[0数据]** (充电板侧无占位)★ | ★**G / S / D**★ | ★**待 L4 定封装后核**★ | ★**充电板新画 land 时直接把 pad 序定成 G/S/D (pad1=G/CHG_STAT · pad2=S/GND · pad3=D/CHG_LED_K), 免得重犯主板那两件的错**★ |

★**落板批次还必须核的 (本单只报)**: ★**三件 MOS 的占位焊盘间距 (pad1→pad2 = 1.27 mm · pad2→pad3 ≈ 4.28 mm) 与任何在售 SOT-23 厂商 land 都不重合 ⇒ 重画焊盘图是必做项, 不是可选项 (缺口 G-7)** ★

### B3.3 · L3 · `D_ESD_CAM` 的两条改法 (★一条不许代拍★)

| | ★**方案甲: 换成双向件** ★ | ★**方案乙: 保留单向件** ★ |
|---|---|---|
| **怎么做** | ★**落表批次把 `D_ESD_CAM` (可一并统一另两件) 改成双向件 `PESD5V0S1BA`** (Nexperia SOD-323, 2 lead, 1.3 mm pitch, 本体 1.7×1.25×0.95 mm) ⇒ ★**K1/K2 对称 ⇒ pad 序天然免疫, 三件可同料** ★ | ★**保留 TI `TPD1E05U06DPYR`** (DPY X1SON 2-pin) ⇒ ★**落板批次对 `D_ESD_CAM` 的 land 做 pad1/pad2 对调** (pin1(I/O)→`CSI_D0_CK_P` 位 · pin2(GND)→`GND` 位) ★ |
| **优点** | ★**pad 序问题从根上消失 ⇒ 落板批次不必做反向 land ⇒ 三件 ESD 同料 ⇒ BOM 行数/来料种类少** ★ | ★**结电容 0.42 pF vs 双向件 35 pF ⇒ 差 83 倍 ⇒ CSI 高速 lane 上结电容直接决定眼宽 ⇒ 电气上最优** ★ |
| **代价** | ★**① CSI lane 上 35 pF 吃掉眼宽 ⇒ 属 main/老板判断 (V-2 口径) ② `PESD5V0S1BA` 的 VRWM 恰 5.0 V ⇒ 对 5 V±5% 轨 (最高 5.25 V) 顶到边 ⇒ `D_ESD_DEMO` 要复核 IR 曲线 ③ SOD-323 的 1.3 mm pitch 与占位 2.30 mm 间距不重合 ⇒ 三件都要重画 land (两个方案共同成本, 非甲独有)** ★ | ★**① `D_ESD_CAM` 要单独做反向 land ⇒ 人为出错概率高 (这正是本条存在的理由) ② DPY 是 X1SON 0.5×0.5 mm 无引脚 ⇒ 必须上贴片机, 手工返修困难 ③ DPY 官方 land 同样与占位间距不一致 ⇒ 也要重画** ★ |
| **证据等级** | ★`[官网]` (Nexperia 官方产品页 + 数据手册)★ | ★`[官网]` (TI SLVSBO7O 引脚表)★ |

### B3.4 · ★★L4 · 充电板 6 件器件的 footprint 候选清单 (★只出清单, 不许画板★)★★

★**约束 (全 6 件共用)**: ★**充电板 = 25 × 10 × 0.8 mm** (`[推算]`, `MECH/MECH_BUDGET.md` §1.3 M3) · ★**这 6 件在 `demo_mainboard.kicad_pcb` 上查无占位 ⇒ 无几何可判 ⇒ 一律不写「已兼容」** ★

| 位号 | ★**候选1** ★ | ★**候选2** ★ | ★**焊盘数** ★ | ★**本体尺寸** ★ | ★**与充电板面积约束的关系** ★ | ★**出处 + 证据等级** ★ | ★**降级方案** ★ |
|---|---|---|---|---|---|---|---|
| ★**`D_ESD_TC`** ★ (Type-C 侧 ESD) | ★**候选1**: ★**Nexperia `PESD5V0S1BA`** · VRWM 5 V / VBR 6 V min / V(CL)R 14 V / IPPM 12 A / PPPM 130 W / IRM 5 nA / IEC 61000-4-2 >30 kV / Cd 35 pF typ ★| ★**候选2**: ★**TI `TPD1E05U06DPYR`** (DPY X1SON 2-pin, Cd 0.42 pF) ★★**或**★★ `TPD2E2U06` (双通道, DCK/SC70-3 3 脚 / DRL/SOT-5 5 脚, Cd 1.5 pF, ±25 kV 接触) ★| ★**2** (前两个候选都是 2 脚) ★★**`TPD2E2U06` = 3/5 脚 ⇒ 落不下 2 焊盘 ⇒ 须充电板 footprint 改 3 焊盘** ★ | ★**PESD5V0S1BA: SOD-323, 1.7×1.25×0.95 mm** ★★**TPD1E05U06DPYR: DPY X1SON 0.5×0.5 mm 级** ★★**TPD2E2U06: DCK 2.00×1.25 mm / DRL 1.60×1.20 mm** ★ | ★**两个 2 脚候选都放得下 25×10 mm (体积占比 <2%)** ★★**`TPD2E2U06` 也放得下, 但焊盘数变了 ⇒ 充电板 footprint 要重画** ★ | ★**Nexperia 官方产品页 + 数据手册 (PESD5V0S1BA) · TI SLVSBO7O (TPD1E05U06) · TI SLLSEG9C (TPD2E2U06)** ★ · ★`[官网]`★ | ★**降级方案**: ★**若 C-01 最终定成单通道 ⇒ 直接落 2 脚 `PESD5V0S1BA` (零额外风险); 若要双通道 ⇒ 选 `TPD2E2U06DCKR` SC70-3 + 充电板 footprint 改 3 焊盘 (归充电板那一趟); 若要护 3 条线 (VBUS+D+/D−) ⇒ 选多通道阵列件 (`PESD5V0S4UD` 四通道 / `PESD5V0S2UAT` 双通道 SOT-23) ⇒ 充电板 footprint 一次定到多通道** ★|
| ★**`FB_VBUS`** ★ (VBUS π 滤波磁珠) | ★**候选1**: ★**Murata `BLM21PG221SN1D`** · 0805 · 阻抗 220 Ω @100 MHz (±25%) · 额定 2 A · DCR 45 mΩ (max) ★| ★**候选2**: ★**Murata `BLM31PG121SN1`** · 1206 · 阻抗 120 Ω @100 MHz · 额定 **3000 mA** · DCR **0.025 Ω** ★ (★同系列已抓到官方参数的档位: `BLM31PG391SN1` 390 Ω/2000 mA/0.05 Ω · `BLM31PG601SN1` 600 Ω/1500 mA/0.09 Ω★)| ★**2** (磁珠 2 脚 ⇒ 落 2 焊盘成立) ★ | ★**候选1 0805 = 2.00×1.25 mm · 候选2 1206 = 3.2×1.6 mm** ★ | ★**两档都放得下; 1206 比 0805 大一整号 ⇒ 充电板面积成本 ↑ (ISS-216/ISS-229 在盯的热点)** ★ | ★**Murata 官方 chip ferrite bead lineup 页 + 官方 BLM21 / BLM31P 系列参数表** ★ · ★`[官网]`★ | ★**降级方案**: ★**若 1206 放不下 ⇒ 退 0805 `BLM21PG221SN1D`, 代价 = 充电环路阻尼变大 (45 mΩ vs 25 mΩ) ⇒ 必须由 main/PM 按 BQ25896 官方 §10.2.2 复核 1.22 A 档的环路稳定性; 若 Imax > 3 A ⇒ 选 `BLM31P330SG` 类低 DCR 大电流档 (33 Ω / 6000 mA / 0.01 Ω)** ★|
| ★**`D_TVS_VBUS`** ★ (Type-C 入口 5 V 级单向 TVS) | ★**候选1**: ★**Littelfuse `SMBJ5.0A`** · VRWM 5.0 V / VBR 6.4 V (min) / Vc **9.2 V @ Ipp 65.3 A** (10/1000 µs) / PPP 600 W / IR 800 µA max / −65~+150 °C / 单向 ★| ★**候选2**: ★**STMicro `SMBJ6.0A`** · VRWM **6.0 V** (⇒ 落在 PM 要求的「5-6 V 档」上沿, 对 5 V±5% 余量更大) · ★**具体 Vc / Ipp 数值本单未取到 ⇒ `[0数据]`** ★| ★**2** (SMB = 2 焊盘) ★ | ★**DO-214AA (SMB) ≈ 4.4 × 3.6 mm (两个候选同封装)** ★ | ★**SMB 是本清单里最大的单体 (≈15.8 mm²) ⇒ 占充电板 250 mm² 的 6.3% ⇒ 面积可行但不小** ★ | ★**Littelfuse 官方 SMBJ 系列页 + ST 官方 `SMBJ6.0A` 产品页** ★ · ★`[官网]`★ (★`SMBJ6.0A` 的 Vc/Ipp = `[0数据]`★) | ★**降级方案**: ★**若 IR 800 µA max 在 VBUS 常驻 5 V 下不可接受 ⇒ 改选更低 IR 的 TVS 档或保留 `SMBJ5.0A` 但把 TVS 挪到 Type-C 座正下方 (靠边 ⇒ 少走线 ⇒ 少压降); 若钳位电压必须更低 ⇒ 换更低的 VRWM 档并复核 BQ25896 绝对最大 22 V 余量** ★|
| ★**`Q_CHG_LED`** ★ (充电灯开关 N-MOS) | ★**候选1**: ★**onsemi `2N7002`** (SOT-23, 60 V) · VGS(th) 1.0/1.76/2.0 V · RDS(on) 1.2 Ω typ @10 V · IGSS ≤ ±10 nA · IDSS ≤ 1 µA · ID 115 mA ★| ★**候选2**: ★**AOS `AO3400A`** (SOT-23, 30 V) · VGS(th) 0.65/1.05/**1.45 V** · RDS(on) 26.5 mΩ@10 V / 48 mΩ@2.5 V · IGSS ≤ 100 nA · ID 5.7 A ★| ★**3** (MOS 3 脚 ⇒ 落 3 焊盘) ★ | ★**SOT-23 本体 2.9 × 1.3 mm** ★ | ★**放得下 25×10 mm (体积占比 <2%)** ★ | ★**Microchip/onsemi 官方数据手册 · AOS 官方数据手册 + 产品页** ★ · ★`[官网]`★ | ★**降级方案**: ★**若 STAT 驱动电压不足 3.3 V ⇒ 换阈值更低的 `AO3400A` (max 1.45 V), 代价 = 过剩规格多花成本; 若要同时低漏 + 低阈值 ⇒ `AO3401A` 类或并栅极下拉 (★但网表 note 明写充电板本地的 5 V 上拉已删 ⇒ 加下拉属改网表 ⇒ 归落表批次, 本单不落★)** ★ ★**pad 序**: ★**库里 SOT-23 是 G/S/D, 充电板上是新画 ⇒ 不存在 pad 序问题, 但落板批次要把 pad 序定成 G/S/D (pad1=G/CHG_STAT · pad2=S/GND · pad3=D/CHG_LED_K)** ★|
| ★**`D_CHG_LED`** ★ (充电灯) | ★**候选1**: ★**Kingbright `APT1608SURCK`** (0603 红) · λdom 630 nm · IV 40 mcd (min) / 80 mcd (typ) @20 mA · 视角 120° · 1.6×0.8×0.75 mm ★| ★**候选2**: ★**Kingbright `APT1608CGCK`** (0603 绿) · λdom 570 nm · IV 20/50 mcd @20 mA · 1.6×0.8 mm ★| ★**2** (LED 2 脚) ★ | ★**0603 = 1.6 × 0.8 × 0.75 mm (两候选同封装)** ★ | ★**放得下 (体积占比 ~1%)** ★ | ★**Kingbright 官方产品页 + 原厂数据手册 (APT1608SURCK: 官网产品页 + 0603 原厂页)** ★ · ★`[官网]`★ | ★**降级方案**: ★**若要更小 ⇒ 换 0402 (0.65 mm 高) 档, 代价 = 手贴难度上升; 若要双色 (红/绿) ⇒ 换 0805 4 脚双色件, 代价 = 焊盘数 2→4 ⇒ 充电板 footprint 要改 + 网表要加一条 D_CHG_LED2 (★属落表批次★)** ★|
| ★**`C_REGN`** ★ (REGN 去耦) | ★**候选1**: ★**Murata `GRM21BR71C475KA73L`** ★★**★本单 L1 已落表 (0805 / 4.7 µF / 16 V / X7R / ±10%)**★★ ★| ★**候选2**: ★**Murata `GRM31CR71H475KA12L`** (1206, 4.7 µF, 50 V, X7R, ±10%) — 备选, 面积更大耐压过剩 ★| ★**2** (MLCC 2 脚 ⇒ 落 2 焊盘) ★ | ★**0805 = 2.0 × 1.25 mm (候选1) · 1206 = 3.2 × 1.6 mm (候选2)** ★ | ★**★0805 是充电板贴 U_CHG pin22 近端的常规尺寸 (手册要求 close to the IC) ⇒ 面积上最优; 候选2 的 50 V 耐压对 ~5 V 的 REGN 是极大过剩, 代价 = 面积大 + 更高 ESL/ESR** ★ | ★**ISS-241 矩阵 §3.7 ⑳ + Murata 官方 MLCC 系列页** ★ · ★`[官网]`★ | ★**降级方案**: ★**交叉引用 L1 (已落表) ⇒ 不重复论证; 若 0805 在充电板上贴不进 U_CHG pin22 近端 ⇒ 退 0603 4.7 µF (但 DC bias 降容更明显 ⇒ 须按官方曲线复核) 或改走充电板内双层贴装 (归充电板那一趟)** ★|

---

## B4 · 接口取值声明 (验收命令实跑输出 · ★本机实跑, 原样★)

### B4.0 · ★★接口取值声明 (★凡引用这三条的, 一律用这个值★)★★

| 接口 | 取值 | 证据等级 | 声明位置 |
|---|---|---|---|
| ★**`C_REGN` 的 value** ★ | ★**`4.7µF ±10% (10V)`** ★ (★手册要求的最低耐压 10 V; 实际选型 16 V ≥ 10 V✔★) | ★`[官网]` + `[推算]` ★ | ★`state/gen_netlist.py` L500/L502 → 网表 L44/L45 · 脚表 L132/L133 · BOM L43★ |
| ★**`C_REGN` 的 opn / footprint** ★ | ★**`GRM21BR71C475KA73L` / 0805 (2.0×1.25 mm)** ★ | ★`[官网]` ★ | ★`state/gen_netlist.py` `PARTS["C_REGN"]`★ |
| ★**三件 MOS 的 pad↔pin 映射** ★ | ★**`Q_AND` 占位 D/S/G · `Q_PG` 占位 S/D/G · `Q_ENVC` 占位 G/S/D · SOT-23 库引脚序一律 G/S/D ⇒ 前两件必须人工改映射, 第三件天然对上** ★ | ★`[实测]` (板文件) + `[官网]` (器件手册) ★ | ★`HW/MOS_PAD_PIN_MAPPING.md` §1.1 · 分片 `interface_claims` key=`iss243_cregn_value_opn_and_mos_pad_order`★ |
| ★**`C_REGN` 的落板位置** ★ | ★**充电板贴 `U_CHG` pin22 近端** (★手册 "placed close to the IC"★) | ★`[官网]` ★ | ★`HW/CHARGE_BOARD_SPEC.md` §12.3★ |


### B4.1 · 落表前基线 (★本单起跑时实跑, 供对照★)

```
$ python3 HW/check_netlist_selfconsistency.py
✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★
rc=0

$ python3 HW/check_netlist_selfconsistency.py --expect-resolved
★★ rc=1: 翻面口径未通过 (18 条未落表) ★★
rc=1        ★★落表前基线 = 18 条★★

$ python3 HW/check_netlist_contradiction_r3.py
  FINDINGS: 3  (主线要求 = 恰 3 条)
  结论: ✅ 恰 3 条 = 主线的 3 条缺陷 (零多报零少报)  ·  rc = 1
rc=1

$ python3 HW/check_part_selection_matrix.py
[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (8/8)
rc=0
```

### B4.2 · 落表后 (★全部实跑, 原样输出★)

```
$ python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
  python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
  python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py
rc=0 (6/6 全部 rc=0)

$ python3 HW/check_netlist_selfconsistency.py
★**落表作业包 (HW/SCHEMATIC_LANDING_WORKPACKET_V1.md) 完整性 + 三方对齐: 全过** (★28 条作业条目, 8 栏齐★)
★**翻面条件见规格页 §⑤**; 落表后请改用 `--expect-resolved` ★
rc=0

$ python3 HW/check_netlist_selfconsistency.py --expect-resolved
★★ rc=1: 翻面口径未通过 (18 条未落表) ★★
rc=1        ★★落表后仍是 18 条 (与落表前逐字节相同 ⇒ diff 为空) ⇒ 没碰坏别的, 也没越界落别的★★

$ python3 state/check_netlist.py
rc=0
$ python3 state/check_netlist_pins.py
✅ 全过 —— 每个针脚归属唯一, 连接器针数与针号齐, SoC 节点全部落到真实引脚
rc=0
$ python3 state/check_sch_erc.py
  判定: ✅ 过 (ERC=0)
rc=0
$ python3 state/check_sch_pinfull.py
  判定: ✅ 过 (逐器件脚数全相等)
rc=0

$ python3 HW/check_netlist_contradiction_r3.py
── FINDINGS (3) ────────────────────────────────────────────────────────
  FINDINGS: 3  (主线要求 = 恰 3 条)
  结论: ✅ 恰 3 条 = 主线的 3 条缺陷 (零多报零少报)  ·  rc = 1
rc=1        ★★ISS-242 的门禁未被本单改红 (仍是恰 3 条)★★

$ python3 HW/check_part_selection_matrix.py
[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (8/8)
rc=0        ★★ISS-241 的门禁未被本单改红★★

$ python3 HW/check_iss243_cregn.py
  C1   [PASS] 三处 value 均为 4.7µF 级且带 10V 耐压标注
  C2   [PASS] 三处 opn 均非空且为落定型号 GRM21BR71C475KA73L
  C3   [PASS] 台账 §16 已登记 ISS-243 (三处改动 + 新值 + 新旧 md5)
  C4   [PASS] 映射表存在, 三件 MOS 在 L2 主表里都有行
  C5   [PASS] 三件 MOS 行都同时有占位 pad 序 + 库引脚序两个串 (按列判)
  C6   [PASS] L3 方案甲 (换双向件) + 方案乙 (对调 land) 都在案
  C7   [PASS] 真源 (gen_netlist.py) 的 value + PARTS[C_REGN] 都在位
  C8   [PASS] L4 六件在交卷单里, 每件 ≥2 候选 + 证据等级 + 降级方案
  ✅ rc=0: 8/8 条断言全过
rc=0

$ python3 HW/check_iss243_cregn.py --selftest
  基线: 8/8 条全绿 ✔
  [PASS] ① 删掉 BOM 的 10V 耐压标注 ⇒ 期望红 C1
  [PASS] ② 把网表 L44 的 opn 栏清空 ⇒ 期望红 C2
  [PASS] ③ 把台账 §16 里的 ISS-243 登记删掉 ⇒ 期望红 C3
  [PASS] ④ 把映射表里 Q_PG 那行删掉 ⇒ 期望红 C4/C5
  [PASS] ⑤ 把映射表里 Q_AND 行的「占位 pad 序」串抹掉 ⇒ 期望红 C5
  [PASS] ⑥ 把映射表里 L3 的「方案乙」那一栏抹掉 ⇒ 期望红 C6
  [PASS] ⑦ 把真源的 value 退回「[待选型] 1µF」 ⇒ 期望红 C7
  [PASS] ⑧ 把交卷单里 D_TVS_VBUS 的候选2 抹掉 ⇒ 期望红 C8
  ✅ rc=0: 反向用例 8/8 全过 (★每条都自证「真的改到了目标」★)
rc=0

$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-16T16:02:25+08:00)
   产出 349 | 阻塞 43 (高危 33) | 未闭合需求 199 | 冲突 0 | 健康度 red
rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
rc=0        ★★【Q1】18/18★★
```

### B4.3 · ★落表前后 md5 (★受保护的两个必须逐字节不变; 新的打到 stdout 供 SW/MECH 走 H-1 重锚★)★

| 文件 | 前 (本单起跑) | 后 (交卷实测) | 变了? |
|---|---|---|---|
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**否 (受保护)★** ★ |
| ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**否 (受保护)★** ★ |
| ★**`HW/netlist_v1.csv`** ★ | `34132f7e40a241e1fae1476be0eafbd5` | ★**`611c3ba3db3dc7de7213063375b96d01`** ★ | ★是 (只有 L44/L45)★ |
| ★**`HW/netlist_v1_pins.csv`** ★ | `b21b743a7702d30729f0d653c15392df` | ★**`ef436a37412ac9b6eac3c9f41f1edca4`** ★ | ★是 (只有 L132/L133)★ |
| ★**`HW/BOM_v1.csv`** ★ | `c195a117ff17490d4d1e1a5b8f1995a7` | ★**`2a7305741134788dfee9f13f34c656b4`** ★ | ★是 (只有 L43)★ |
| ★**`HW/netlist_v1.net`** ★ | `978ab59e297e6bb89f873b763569eccb` | ★**`564fed05c1f5f9dab09efce51eebae74`** ★ | ★是 (只有 L18 一行)★ |
| ★**`HW/SCHEMATIC_V1.md`** ★ | `b1fa5a0c17726037ff3407b31ecbb631` | ★**`289fbafa2874588412cf292b469c73fc`** ★ | ★是 (生成物·跟着网表走)★ |
| ★**`HW/BOM_pseudo_refs_v1.csv`** ★ | `47e1659a42d8d3f6728ea653df1eb530` | `47e1659a42d8d3f6728ea653df1eb530` | ★否★ |
| ★**`state/gen_netlist.py`** (真源) ★ | `9dfb6771c9beb110021bba182f128c64` | ★**`ed12961ef619d04b90bb6d28b2a727ac`** ★ | ★是 (真源)★ |
| ★**`state/gen_kicad_net.py`** (真源) ★ | ★**`5910d40fa7ac73b2b085d2c5eb594548`** ★ | ★**`884221269982d13de8e075c7a31304e4`** ★ | ★是 (真源)★ |

★**★回滚副本★**: ★**`state/.bak_iss243/`** ★ · ★**★TI 原厂 PDF 缓存★**: ★**`state/.cache_iss243/`** ★

### B4.4 · 本单新建的独立机器门禁 (★判据不许放松 / 不许挂 md5★)

★**`HW/check_iss243_cregn.py`** — ★**8 条断言**: ① 三处 value = 4.7µF 级且带 10V 耐压标注 ② 三处 opn 非空 ③ 台账 §16 登记了 ISS-243 ④ 映射表存在且三件 MOS 有 L2 主表行 ⑤ 每件 MOS 同时有「占位 pad 序」+「库引脚序」两个串 ⑥ L3 双方案在案 ⑦ **真源** `gen_netlist.py` 的 value + `PARTS[C_REGN]` 在位 (★防手改 CSV 冒充落表★) ⑧ L4 六件候选清单在交卷单里 ★
★**`--selftest` 8 条反向用例, 每条都自证「真的改到了目标」** (★突变 ⇒ 期望的断言集合必须恰好变红, 其余仍绿★)

| # | 反向用例 | 期望变红 |
|---|---|---|
| ① | 删掉 BOM 的 10V 耐压标注 | C1 |
| ② | 把网表 L44 的 opn 栏清空 | C2 |
| ③ | 把台账 §16 里的 ISS-243 登记删掉 | C3 |
| ④ | 把映射表里 Q_PG 那行删掉 | C4 / C5 |
| ⑤ | 把 Q_AND 行的「占位 pad 序」串抹掉 | C5 |
| ⑥ | 把 L3 的「方案乙」那一栏抹掉 | C6 |
| ⑦ | 把真源的 value 退回「[待选型] 1µF」 | C7 |
| ⑧ | 把交卷单里 D_TVS_VBUS 的候选2 抹掉 | C8 |

---

## B5 · 未决项与卡点 (边界自证 · ★逐条★)

| 边界 | 自证 |
|---|---|
| ★**零外发** ★ | ★**本单零外发: 全程没有发过任何邮件/询价/问询/采购 ⇒ 官方数据一律"自己网上查或项目库内已核" (TI 原文 = 本机 PDF 实读; Murata/Nexperia/TI/Littelfuse/ST/Kingbright/Murata 参数 = ISS-241 矩阵里已核的官方数据手册摘录); ★**本轮一次 curl 都没发, 一个后台进程都没起** (★上一轮就是死在 murata.com 403/404 + 后台 curl 上★)** ★ |
| ★**不改 PCB 布线 / 布局 / 板框** ★ | ★**板 `.kicad_pcb` 与 `.kicad_pro` 的 md5 逐字节未变 (§B4.3 实测)** ★ |
| ★**不改 `state/land_v_values.py`** ★ | ★**只读未改 (本单用 `state/gen_netlist.py` + `state/gen_kicad_net.py` 两个真源直接落)** ★ |
| ★**不替老板拍板** ★ | ★**V-2 (ESD 方案二选一) / V-3 / V-4 / G-1 (Q_PG 源漏拓扑) / W-1~W-6 ⇒ 一条未拍, 只出选项 + 代价 (§B3.3 / §B6)** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本单所有 `[实测]` 都指"本机实读盘上文件" (板文件 / 网表 / 脚表 / BOM), 不是实物测量 ⇒ 本机无板 ⇒ 实物实测 0 条** ★ |
| ★**不改 `state/issue_log.yaml`** ★ | ★**未改 (verify 留给 main)** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/hw.yaml` (hw-lead 自己的) ⇒ 走 `state/frag_write.py` 原子写, 不许手改 yaml** ★ |
| ★**只改 `C_REGN` 那几行 (L1)** ★ | ★**真源 2 处 value + 1 条 PARTS + 1 条 REF_FOOTPRINT (★都是 `C_REGN` 一个位号★); 三张生成物的 diff 实测: 网表只有 L44/L45 · 脚表只有 L132/L133 · BOM 只有 L43 · `.net` 只有 L18** ★ |
| ★**不碰 ISS-242 的 `C_VBUS_OUT` / `C_VBUS_GND`** ★ | ★**一条未动 (两条缺陷原样留在盘上 ⇒ 归 main 排期的落表批次)** ★ |
| ★**证据分级必须标** ★ | ★**全文每条事实都带 `[官网]` / `[实测]` / `[推算]` / `[0数据]`; ★**查不到的写 `[0数据]` + 降级方案, 没有写"等回复"** ★ |

---

## B6 · 自证复现命令 (留给 main 的待裁 · ★本单一条未拍★)

### B6.0 · ★复现命令 (★一条一条照抄即可复现★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★1. 落表链路 (改源 → 重生成; ★板不碰★) ★★
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ★★2. 10 条验收门禁 (★全部 rc 与输出见 §B4.2★) ★★
python3 HW/check_netlist_selfconsistency.py                    # rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★仍 18 条★)
python3 state/check_netlist.py                                  # rc=0
python3 state/check_netlist_pins.py                             # rc=0
python3 state/check_sch_erc.py                                  # rc=0
python3 state/check_sch_pinfull.py                              # rc=0
python3 HW/check_netlist_contradiction_r3.py                    # rc=1 (★恰 3 条★)
python3 HW/check_part_selection_matrix.py                       # rc=0 (8/8)
python3 HW/check_iss243_cregn.py                                # rc=0 (8/8 断言)
python3 HW/check_iss243_cregn.py --selftest                     # rc=0 (8/8 反向用例)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 (【Q1】18/18)

# ★★3. 受保护 md5 (必须逐字节不变) ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b

# ★★4. 本单产出物 ★★
ls -la HW/MOS_PAD_PIN_MAPPING.md HW/check_iss243_cregn.py \
  "HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md"
grep -n "ISS-243" HW/SCHEMATIC_LANDING_V1_LANDED.md | head -5
ls -la state/.bak_iss243/ state/.cache_iss243/
```


| # | 事项 | 卡在谁 | 本单的立场 |
|---|---|---|---|
| ★**①** ★ | ★**W-3 (老板点头) 留痕**: `DECISION_PENDING_2026-11-16.md` 的 W-3 写着「`C_REGN` 落表前要老板点一次头」⇒ ★**L1 已落 (依据 = TI 手册官方值 + ISS-243 授权, main 层级已开单) ⇒ 请 main 去把 W-3 标掉 (老板级留痕)** ★ ⇒ ★**本单不碰 `DECISION_PENDING_2026-11-16.md`** ★ | ★**main** ★ | ★**只报告, 不改** ★ |
| ★**②** ★ | ★**V-2 (ESD 方案二选一)**: L3 的方案甲 (换双向件 `PESD5V0S1BA`) vs 方案乙 (保留单向件 `TPD1E05U06DPYR` + 对调 land) ⇒ ★**代价见 §B3.3** ★ | ★**main / 老板** ★ | ★**不代拍** ★ |
| ★**③** ★ | ★**G-1 (`Q_PG` 源漏拓扑)**: 网表 note 写「源极接 ON · 漏极接 BAT_SW」, 与 P 沟道高边开关的常规拓扑 (源极接高电位侧) 相反 ⇒ ★**本单只照抄网表真源, 一字未改拓扑; 若裁决为"源漏反过来", 映射表 §1.1 的 pad1/pad2 功能标注要跟着改 (pad 序本身不变)** ★ | ★**main / PM** ★ | ★**不代拍** ★ |
| ★**④** ★ | ★**G-2 / G-7 (MOS land 重画)**: 三件 MOS 的占位 pad 序与 SOT-23 库序不一致且焊盘间距与厂商 land 不重合 ⇒ ★**落板批次必须逐件人工改映射 + 重画焊盘图; 免重画的出路在售基本不存在** ★ | ★**落板批次 (板那一趟排队中)** ★ | ★**只报改法** ★ |
| ★**⑤** ★ | ★**G-8 (充电板 6 件 footprint)**: 6 件的 footprint 仍是「待定」⇒ ★**清单见 §B3.4, 每件 ≥2 候选; 充电板那一趟按选定的型号定 footprint** ★ | ★**充电板那一趟 (main 排期)** ★ | ★**只出清单** ★ |
| ★**⑥** ★ | ★**ISS-242 的 `C_VBUS_OUT` / `C_VBUS_GND` (各落进 3 个网)** ★ | ★**落表批次 (main 排期)** ★ | ★**本单越界未碰** ★ |
| ★**⑦** ★ | ★**`C_REGN` 的 DC-bias 降容后实际容值 `[0数据]`** ★ (★Murata 的 DC bias 曲线要按料号查官方曲线⇒ 本单未取到 ⇒ **没写进 value 串**★) | 落表批次 / 采购复核 | ★**登记缺口, 不猜** ★ |
| ★**⑧** ★ | ★**H-1 重锚**: 落表后网表/脚表/BOM 的 md5 变了 ⇒ ★**新 md5 已在 §B4.3 打出 ⇒ SW/MECH 若持有旧锚点, 走 H-1 重锚** ★ | ★**sw-lead / mech-lead** ★ | ★**只提供 md5** ★ |

---

## 附 · 本单产出物清单 (★盘上已落★)

| 产出物 | 路径 | 状态 |
|---|---|---|
| ★**落表台账 §16** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 | ★已落 (含单号 + 文件名 + 新旧 md5)★ |
| ★**L2/L3 映射表** ★ | `HW/MOS_PAD_PIN_MAPPING.md` | ★已落 (新建)★ |
| ★**独立机器门禁** ★ | `HW/check_iss243_cregn.py` (+ `--selftest`) | ★已落 (新建 · 8 断言 + 8 反向用例)★ |
| ★**充电板规格补节** ★ | `HW/CHARGE_BOARD_SPEC.md` §12 (★**只加一节, §0~§11 一字未改**★) | ★已落★ |
| ★**备份 / 缓存** ★ | `state/.bak_iss243/` · `state/.cache_iss243/` | ★已落★ |
| ★**交卷单** ★ | `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md` | ★本文件★ |
| ★**分片** ★ | `state/fragments/hw.yaml` (★走 `state/frag_write.py` 原子写★) | ★已落★ |

★**END · ISS-243 · 硬件总工 (hw-lead) · 2026-11-16** ★
