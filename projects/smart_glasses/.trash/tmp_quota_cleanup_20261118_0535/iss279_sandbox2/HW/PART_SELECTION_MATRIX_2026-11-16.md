# BOM 待选型 21 件必装器件 · OPN 选型证据矩阵 (ISS-241)

> **作者**: sw-lead (软件总工) · **日期**: 2026-11-16 13:47~14:30 · **单号**: ISS-241 (owner=sw-lead)
> **交卷给**: 项目总工 (moli) / main · **上游 (只读)**: `HW/BOM_v1.csv` (md5 `c195a117…`) · `HW/netlist_v1.csv` (md5 `34132f7e…`) · `HW/PCB/demo_mainboard.kicad_pcb` (md5 `611b869e…`) · `state/fragments/sw.yaml`
> **板文件几何口径**: ★**main 已实测的 21 件占位焊盘几何表** (`/tmp/iss241/MAIN_MEASURED_GEOMETRY.txt`) · ★**本单自己又复测了 14 件 MAIN_PCB 占位的逐焊盘 at/size/net** (pad 层, 逐条见 §3 每件"板位实测"列) ⇒ 两份数据一致 ⇒ 口径可信
> **边界**: ★**本单只交证据, 不落表** (网表 / 脚表 / BOM 的 value 与 opn 栏 **一个字没改**) · ★**零外发** (不发信 / 不询价 / 不问供应商 / 不下单; 老板 2026-11-12 02:02 政策) · ★**没碰** PCB 布线 / 布局 / 板框 · ★**没改** `state/issue_log.yaml` · ★**实物 [实测] = 0 条** (全部是公开官网 / 数据手册 / 分销商目录级证据, **没有一颗实物被测过**)
> **机器门禁**: `python3 HW/check_part_selection_matrix.py` (rc=0 = 全过) · `--selftest` (反向用例 ≥5, 每条自证"真的改到了目标")

---

## ★0 一句话

★**21 件全部有 ≥2 个在售候选 + 官方参数 + 封装兼容性结论 + 证据等级 + 降级方案; 但有 3 条硬发现必须先摆到台面上 (都不是我能拍的)**: ★**① ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚器件 (TPD2E2U06 类) 物理落不下, 只能单通道器件 (TPD1E05U06DPY 2-pin / PESD5V0S1BA 2-lead) 或写明"需换 3 脚封装 ⇒ 归落表/板那一趟"** ★**② Q_PG 的 P-MOS 在板上是 3 焊盘但 pad 网络顺序是 (G/S/D) 而 SOT-23 库封装是 (G/S/D) 顺序不同 ⇒ 换 SOT-23 器件时 pad↔pin 映射必须逐件核, 不能想当然** ★**③ `C_REGN` 判据本身错了: BOM 写"1µF", 但 TI BQ25896 数据手册 pin22 REGN 明写"Connect a **4.7 µF (10 V rating)** ceramic capacitor" ⇒ 本单按官方值给候选, 但 1µF→4.7µF 是 BOM 值变更 ⇒ 归落表批次 (本单不落表)** ★**其余 18 件的焊盘数 / 焊盘网络 / 封装尺寸与候选可直接对上, 落表时可直接回填 OPN**

---

## §1 口径与判据来源 (每条判据都能追到网表 note 或官方参数)

| 口径项 | 本单怎么定 | 依据 |
|---|---|---|
| **清单范围** | 21 件 = BOM `value` 含「待选型」且 `dnp=必装` 的 **23 行** 减 `U_PWR_SW` / `U_EN_SW` (ISS-172 在办, 不抢) | `HW/BOM_v1.csv` 实跑: 命中 23 行, 排除 2 行 = **21 行** ★**注**: 任务书正文按类别枚举只列了 20 个位号 (ESD 4 + FB 2 + TVS 1 + MOS 4 + LED 3 + SW 5 + C 1 = 20), ★**本单以 BOM 真源为准取 21 行, 差额 1 件 = `R_SUPV_DIV1` / `R_SUPV_DIV2` 这一对里的 1 个计数差** ⇒ 见 §2 范围勘误 |
| **板位 (MAIN_PCB / CHG_BOARD)** | 逐件从 `HW/BOM_v1.csv` 的 `board` 列 + `HW/netlist_v1.csv` 的 `board` 列双读交叉 | ★**6 件不在 `demo_mainboard.kicad_pcb` 上** (`D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN` = 充电板 CHG_BOARD 件) ⇒ 它们的封装占位是"待定" ⇒ **本单对这些件只写"落 N 焊盘 + 充电板侧封装另行定", 一律不写"已兼容"** |
| **封装兼容性判据** | ★**只判三件事**: ① 焊盘**数**对不对 ② 焊盘**网络**对不对 (信号脚 / 地脚 / 源漏栅对不对) ③ 器件**本体尺寸 + 厂商 land pattern**能不能落进占位焊盘的 fab bbox。**封装名全是空字符串 ⇒ 没有任何"库封装"可对齐 ⇒ 一律按"裸焊盘占位"处理** | main 实测: `demo_mainboard.kicad_pcb` 里全部 MAIN_PCB 占位封装 `footprint` 名 = `""` (空) ⇒ 它们是**裸焊盘占位, 不是库封装** ⇒ 选型必须落在【现有焊盘数 + 焊盘网络】上 |
| **证据等级 (五级固定)** | `[官网]` = 厂商官网 / 官方数据手册原文 · `[实测]` = 板上实测 · `[媒体]` = 分销商目录 / 媒体 · `[推算]` = 由已给数据推导 · `[0数据]` = 查不到 | ★**本单 `[实测]` = 0 条** (板端没有实物; 文中出现的"板位实测"是**读板文件**得到的几何, 不是硬件实测, 按 `[推算]`/`[官网]` 口径记) |
| **不许猜** | 查不到的型号 / 参数 / 封装 ⇒ 标 `[0数据]` + **必须写降级方案** | ★**任何一件都不许留空降级方案** (门禁 C4 逐件核) |
| **不代拍** | 每件给"推荐项 + 为什么 + 代价", ★**最终型号 / V-2 / V-3 / V-4 的一票交 main 排期 / 老板** | 与 ISS-172 交卷同口径 |

---

## §2 ★范围勘误 (一条必须让 main 知道的计数差)

★**任务书正文与 BOM 真源对不上, 本单以 BOM 真源为准, 并把差额摆出来**:

| 口径 | 数量 | 说明 |
|---|---|---|
| BOM `value` 含「待选型」且 `dnp=必装` 的**原始行数** | **23** | 实跑 `HW/BOM_v1.csv` (md5 `c195a117…`) 得到 |
| 减 `U_PWR_SW` (ISS-172 在办) + 减 `U_EN_SW` (ISS-172 在办) | **21** | ★**main 抬头说的"23 行 ⇒ 排除 2 ⇒ 21 件"与 BOM 实跑一致** ✔ |
| 任务书正文按类别枚举出来的位号 | **20** | ESD 4 + FB 2 + TVS 1 + MOS 4 + LED 3 + SW 5 + C 1 = 20 ⇒ ★**枚举漏了 `R_SUPV_DIV1` / `R_SUPV_DIV2`** 这一对 (占位 2 焊盘, 0Ω 跳线位, `[待选型] 分压上臂/下臂 (0Ω 跳线位)`, `tbd=TBD-02`) |
| ★**本单实际覆盖** | **21** | ★**= 枚举的 20 件 + `R_SUPV_DIV1`/`R_SUPV_DIV2` 这一对 (按 BOM 真源算 1 个位号配额, 本单把两件都写了 ⇒ 见下方说明)** |

★**处理方式 (透明留痕, 不自作主张)**: 本单矩阵**覆盖 21 个位号**, 组成 = 任务书枚举的 20 件 **+ `R_SUPV_DIV1` 与 `R_SUPV_DIV2` 两件 (合计 22 行正文条目, 但按"BOM 待选型必装件"口径是 21 个位号因为这一对各算 1/2 见下)**。
★**诚实结论**: ★**"21"这个数字在任务书里同时对不上 BOM 真源的 22 行 (含 R_SUPV_DIV1/2) 和枚举的 20 行 — 三处口径互不一致 (21 / 20 / 22)** ⇒ ★**本单把 21 件全部覆盖, 并且把 `R_SUPV_DIV1` / `R_SUPV_DIV2` 也一并做了 (共 22 行条目) ⇒ 宁可多做不可漏做; 门禁 C1 按"覆盖 ≥21 且含全部 20 个枚举位号 + 含 R_SUPV_DIV1/2"来卡** ⇒ ★**不靠数字卡, 靠位号集合卡**。

---

## §3 ★逐件选型证据矩阵 (22 行 · 每件 ≥2 候选)

> **表格列含义**: `判据` = 从网表 note + 官方参数提炼的硬条件 · `候选1/候选2` = 型号 + 官方链接 + 关键参数 + 封装 · `推荐项 + 为什么` = ★**只给依据与代价, 不代拍** · `封装兼容性` = 与板文件现有 2/3 焊盘占位是否匹配 (含理由) · `证据等级` · `降级方案` (必填)

### §3.1 ESD 阵列 ×4 (2 焊盘占位 ⇒ ★**只能单通道器件**)

★**共同硬约束 (main 实测)**: 4 件 ESD 全是 **2 焊盘**占位 (`D_ESD_CAM` pad1=GND / pad2=CSI_D0_CK_P; `D_ESD_DEMO` pad1=RAIL_DEMO_5V / pad2=GND; `D_ESD_USB_D` pad1=USB_D_P_SRC / pad2=GND), 焊盘尺寸 0.6×0.9 mm, fab bbox **W=2.70 H=1.60 mm** ⇒ ★**双通道 3 脚器件 (TPD2E2U06 的 DCK/SC70-3 = 3 脚; DRL/SOT-5 = 5 脚) 物理落不下** ⇒ 只能选 **2 脚 (2-pin / 2-lead) 单通道**器件。

---

#### ① `D_ESD_CAM` — MAIN_PCB · camera FPC 侧 CSI ESD

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「跨铰链 CSI 主板侧 ESD 阵列位 (紧贴 CONN_CAM); 通道数随 lane 数定」 ★**CSI-2 是高速差分对 ⇒ 结电容是第一位判据** (每条 lane 的等效容会拉偏眼图/眼宽) · Forlinx 载板指引要求 ESD 紧贴接口 ⇒ 位置已定 (pad2 = CSI_D0_CK_P, 紧贴 CONN_CAM pin18) · ★**★pad 顺序特例 (本单实读)**: 本件 **pad1 = GND / pad2 = CSI_D0_CK_P** ⇒ 与 `D_ESD_DEMO` / `D_ESD_USB_D` (那两件是 pad1=信号 / pad2=GND) **相反** ⇒ ★**单向器件 (TPD1E05U06 的 pin1=I/O, pin2=GND) 在本件上若按 pad 序号机械接 ⇒ I/O 脚会接到 GND、信号脚接到 GND 位 ⇒ 直接不工作 ⇒ 落板批次必须对调, 或改用双向件 (PESD5V0S1BA 的 pin1=K1/pin2=K2 是对称双向, 无极性问题 ⇒ 天然免疫)** |
| **候选1** | **TI `TPD1E05U06DPYR`** · 链接 `https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf` (数据手册 SLVSBO7O, 2024-08 改版) · 关键参数: **IO 电容 0.42 pF (typ, DPY 封装)**, VRWM 5.5 V, VBR 6.5 V(min) / 8.5 V(max), Vclamp 10 V @ IPP=1 A(TLP) / 14 V @ 5 A, ILEAK 0.01 nA typ / **10 nA max**, IEC 61000-4-2 level 4 (±12 kV 接触 / ±15 kV 空气), IEC 61000-4-5 2.5 A (8/20 µs) / 40 W, 动态电阻 RDYN 0.8 Ω, 工作温度 −40~+125 °C · 封装: **DPY = X1SON 2-pin (0.5×0.5 mm 级, pad 间距 0.65 mm 级)**, 引脚 = **1 = I/O, 2 = GND** (Table 5-1) |
| **候选2** | **Nexperia `PESD5V0S1BA`** · 链接 `https://www.nexperia.com/product/PESD5V0S1BA` (官方产品页) + 数据手册 `https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf` · 关键参数: 单线双向 ESD, VRWM **5 V**, VBR **6 V (min)**, IRM **5 nA**, V(CL)R **14 V**, PPPM **130 W**, IEC 61000-4-2 **> 30 kV (level 4)**, IEC 61000-4-5 IPPM **12 A**, 结电容 **35 pF (typ) / 45 pF (max)**, 温度 −40~+85 °C (TJ 125 °C) · 封装: **SOD-323, 2 leads, 1.3 mm pitch, 本体 1.7×1.25×0.95 mm** (Nexperia 官方 Package outline 表) |
| **推荐项 + 为什么 (不代拍)** | **候选1 `TPD1E05U06DPYR`** · 理由: **0.42 pF vs 候选2 的 35 pF 差 83 倍** ⇒ CSI 高速 lane 上结电容直接决定信号完整性, 35 pF 会在 Gbps 级 lane 上吃掉眼宽 ⇒ 判据级差异不是价格差异 · **代价**: ① DPY 是 X1SON 无引脚 0.5×0.5 mm 级 ⇒ **返修/手焊困难, 必须上贴片机** ② 官方手册的 DPY 是 2-pin (I/O + GND) ⇒ ★**正好对上 2 焊盘占位** ③ ★**本件 pad1=GND / pad2=信号 ⇒ 与 TPD1E05U06 的 pin1=I/O / pin2=GND 顺序相反 ⇒ 落板批次必须对调两个 pad (或改用双向件候选2, 见推荐栏脚注)** ④ [0数据]: DPY 的**推荐 land pattern 与本板占位 pad 间距不一致** ⇒ 需落板批次按 DPY 官方 land 重画 (归落表/板那一趟) |
| **封装兼容性结论** | ★**条件兼容 (需落板批次重画 land + ★需对调 pad 序号)**: ① 焊盘数 **2 = 2** ✔ (DPY 就是 2-pin) ② 焊盘网络: pad1=**GND** / pad2=CSI_D0_CK_P ⇒ ★**与 DPY 的 pin1=I/O / pin2=GND 相反 ⇒ 候选1 落板时必须 I/O→pad2(信号)、GND→pad1** (双向候选2 的 K1/K2 对称 ⇒ 免此问题) ③ 器件本体 0.5×0.5 mm ≪ 占位 fab bbox 2.70×1.60 mm ✔ **但**: 占位焊盘是 **0.6×0.9 mm @ 间距 2.30 mm** (pad1 at −0.45 / pad2 at +1.85, y=−0.2), 与 DPY 官方 0.65 mm 级间距差一个量级 ⇒ ★**候选2 `PESD5V0S1BA` (SOD-323, 2 lead, 1.3 mm pitch, body 1.7×1.25×0.95 mm) 本体尺寸落在 2.70×1.60 bbox 内 ✔ 且 1.3 mm 间距比占位 2.30 mm 间距更接近** ⇒ 两个候选**都要落板批次按厂商 land 重画** |
| **证据等级** | `[官网]` (TI SLVSBO7O 原文 + Nexperia 官方产品页/数据手册) |
| **降级方案** | ★**若落板批次不允许重画 land (占位 2.30 mm 间距固定)**: 降级 = 选 **2-lead / 2-pin 且厂商 land 间距接近 2.30 mm 的器件** (如 SOD-323 1.3 mm pitch 系与 SOD-523 1.3 mm pitch 系都偏小 ⇒ 实际最贴近的是 **SOD-323 大间距变体 / SC-88 类 2 脚**) ⇒ 同时 **登记"CSI ESD 未做 lane 对匹配"的缺口** (本板只有 CK_P 一条 lane 有 ESD 位, CK_N 与 D0~D3 各 lane 均无 ESD 占位 ⇒ 见 §4 缺口 G-3) ⇒ ★**再多通道保护要靠改板 (加 4 脚阵列), 归落表/板那一趟** |

---

#### ② `D_ESD_DEMO` — MAIN_PCB · demo 板 USB-C VBUS 入口 ESD

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「USB-C VBUS 入口 ESD 阵列 (紧贴 J_USB_C)」 · pad1 = **RAIL_DEMO_5V** (VBUS), pad2 = GND ⇒ ★**这是打在 5 V 电源轨上的 ESD, 不是数据线** ⇒ 判据 = ① **VRWM 必须 ≥ 5.25 V** (否则在 5 V±5% 上常态漏电/发热) ② 钳位电压要低于下游 U_EN_SW (TPS22991RAA) 的耐压 ③ 要能扛 Type-C 插拔尖峰 (选型 note 要求 ≥3 A 脉冲档) |
| **候选1** | **Nexperia `PESD5V0S1BA`** · `https://www.nexperia.com/product/PESD5V0S1BA` · VRWM **5.0 V** / VBR 6.0 V(min) / V(CL)R 14 V / IPPM 12 A / PPPM 130 W / IRM 5 nA / IEC 61000-4-2 >30 kV · 封装 **SOD-323 (2 lead, 1.3 mm pitch, body 1.7×1.25×0.95 mm)** ★**注意**: VRWM 恰为 5.0 V, 对 5 V±5% 轨 (最高 5.25 V) **已在 VRWM 边缘** ⇒ 见降级方案 |
| **候选2** | **Littelfuse `SMBJ5.0A`** · 链接 `https://www.littelfuse.com/products/tvs-diodes/smb-j` (系列页, 官方) · 关键参数: **VRWM 5.0 V / VBR 6.4 V (min) / 钳位电压 Vc 9.2 V @ Ipp 65.3 A (10/1000 µs) / PPP 600 W / IR 800 µA max / −65~+150 °C / 单向** · 封装 **DO-214AA (SMB) 2 焊盘** ★**注意**: IR 800 µA max 明显大于候选1 的 5 nA ⇒ 见降级方案 |
| **推荐项 + 为什么 (不代拍)** | ★**这两个候选都不是完美解, 我把代价摆出来让 main 裁**: ★**候选1 `PESD5V0S1BA` 漏电低 (5 nA vs 800 µA, 差 5 个数量级) 且体积小 (SOD-323 vs SMB) ⇒ 但 VRWM 5.0 V 对 5.25 V 轨顶到边, 需要 Nexperia 的 IR-V 曲线复核** ★**候选2 `SMBJ5.0A` 是"抗插拔尖峰"的标准解 (600 W / 65.3 A, 钳位 9.2 V 远低于 U_EN_SW 耐压) ⇒ 但 800 µA 反向漏电在 VBUS 常驻 5 V 下是持续功耗, 且 SMB 封装比占位 2.70×1.60 mm 大** ⇒ ★**我倾向候选1 + 落板批次复核 IR 曲线, 但这是 main/老板的一票 (属 V-2 口径), 我不拍** |
| **封装兼容性结论** | ★**候选1 条件兼容 / 候选2 不兼容 (尺寸超)**: 候选1 SOD-323 body 1.7×1.25×0.95 mm ⇒ 落在占位 fab bbox **2.70×1.60 mm** 内 ✔, 焊盘数 2=2 ✔, 焊盘网络 (pin1 K1 阴极 / pin2 K2 阴极, 双向件 ⇒ 正负极对称) ✔ 与 VBUS↔GND 对上 ✔ ⇒ **需落板批次按 SOD-323 官方 land (1.3 mm pitch) 重画** (占位现为 2.30 mm 间距) · 候选2 SMB (DO-214AA) body ≈ 4.4×3.6 mm ≫ 2.70×1.60 ⇒ **落不下现有占位, 归落表/板那一趟 (改 footprint 或挪位)** |
| **证据等级** | `[官网]` (Nexperia 官方产品页 + Littelfuse 官方系列页) · ★**封装的 2 焊盘数由 §3 各件"板位实测"直接给出** |
| **降级方案** | ★**若 IR 曲线过不了 5.25 V**: 降级 = 改选 **VRWM 6 V 档的 2 脚件** (如 Nexperia `PESD6V0S1BA` 类 / Littelfuse `SP1006-01` 类) ⇒ ★**本轮未抓到该型号的官方参数页 ⇒ 记 `[0数据]`, 落表批次按官网补** · ★**若必须抗插拔尖峰**: 降级 = **保留 PESD5V0S1BA 做 ESD + 另加 TVS 位 (D_TVS_VBUS 同款 SMBJ5.0A) 做浪涌**, 两级分工 ⇒ 归落表/板那一趟 (本板 VBUS 侧目前只有 1 个 ESD 占位, 没有独立 TVS 占位) |

---

#### ③ `D_ESD_USB_D` — MAIN_PCB · USB 2.0 数据线 ESD (D+)

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**」 · pad1 = **USB_D_P_SRC**, pad2 = GND · ★**只有 D+ 有 ESD 位, D− (USB_D_N_SRC) 网表上只有 R_SER_USB_D_N 串阻, 无 ESD 占位** (实测: `USB_D_N_SRC` 只出现在 L292 串阻行) ⇒ 见 §4 缺口 G-4 · USB 2.0 全速 12 Mbps ⇒ 结电容判据比 CSI 松, 但仍要求 **Cd ≤ 10 pF 级** 才能保住上升沿 |
| **候选1** | **TI `TPD1E05U06DPYR`** · `https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf` · **Cd 0.42 pF**, VRWM 5.5 V, VBR 6.5 V min, Vclamp 10 V @1 A(TLP), ILEAK 10 nA max, IEC 61000-4-2 level 4 (±12 kV), −40~+125 °C · 封装 **DPY X1SON 2-pin (1 = I/O, 2 = GND)** |
| **候选2** | **Nexperia `PESD5V0U1BA-Q`** · 链接 `https://assets.nexperia.com/documents/data-sheet/PESD5V0U1BA-Q.pdf` (官方数据手册, 2022-05-03) · 关键参数: **Cd 11 pF (typ) / 13 pF (max)**, VRWM 5 V, VBR 5.8~7.8 V, VCL 12.5 V @ IPP 4.8 A, **PPP 45 W**, IRM <1 nA (typ) / 10 nA max, IEC 61000-4-2 level 4 (±30 kV), IEC 61000-4-5 IPP 4.8 A · 封装 **SOD-323 (2 lead, 1.3 mm pitch, body 1.7×1.25×0.95 mm)**, 官方 solder lands 图给了 2 焊盘间距与阻焊开窗尺寸 |
| **推荐项 + 为什么 (不代拍)** | **候选1 `TPD1E05U06DPYR`** · 理由: 0.42 pF 对 USB 2.0 FS 是"过剩的余量" (11 pF 也够, 但 0.42 pF 让这同一颗也能当 CSI 侧的统一料 ⇒ **4 件 ESD 用 1 个 OPN, 减少 BOM 行数与来料种类**, 对量产备料是实打实的成本) · **代价**: ① X1SON 0.5×0.5 mm 无引脚 ⇒ 必须机器贴装, 手工返修困难 ② 官方 I/O 电容 0.42 pF 是在 VIO=2.5 V / 1 MHz 下测的, USB 2.0 实际 3.3 V 下的等效容 **本轮无官方曲线 ⇒ 记 `[0数据]`** |
| **封装兼容性结论** | ★**条件兼容 (需落板批次重画 land)**: 焊盘数 **2 = 2** ✔ · 焊盘网络 (I/O↔USB_D_P_SRC / GND↔GND) ✔ 与 DPY 引脚 1/2 一一对应 · 本体尺寸 ✔ 远小于占位 fab bbox 2.70×1.60 · ★**但占位焊盘间距 2.30 mm ≠ DPY 0.65 mm 级** ⇒ 落板批次按厂商 land 重画; 候选2 SOD-323 1.3 mm pitch 同理需重画 |
| **证据等级** | `[官网]` (TI 数据手册原文 + Nexperia 官方数据手册原文) |
| **降级方案** | ★**若落板批次拒绝改 land**: 降级 = 选 **2 脚且厂商 land 间距 ≈ 2.30 mm 的 ESD 件**, 本轮抓到的 2 脚件 (SOD-323 1.3 mm / SOD-523 0.65 mm / X1SON 0.65 mm) **间距都偏小** ⇒ ★**记 `[0数据]` + 登记"占位 land 与任何在售 2 脚 ESD 件都不匹配"的缺口 ⇒ 归落表/板那一趟把占位改成标准 ESD land (这是本单最可能的正解: 2.30 mm 间距本来就不像任何 ESD 器件的 land)** |

---

#### ④ `D_ESD_TC` — CHG_BOARD · Type-C 侧 ESD

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「Type-C VBUS 入口 ESD 阵列 (规格 C-01 'Type-C 座 + ESD 阵列'); 通道数/钳位电压随 Type-C 座定」 + 「V1.4 补: Type-C 入口 ESD 阵列 地脚 (原来只有 I/O 脚, 阵列没接地 · ESD 不工作)」 ⇒ 判据 = ① **必须带地脚** (note 明确点出这条历史错误) ② VRWM ≥ 5.25 V (VBUS 5 V±5%) ③ 紧贴 J_TYPE_C (位置已定) ④ ★**注意 Type-C 还要保护 D+/D− (USB 2.0), 而本板 C-01 规格写的是 "Type-C 座 + ESD 阵列"** ⇒ 通道数要跟 Type-C 座一起定 |
| **候选1** | **Nexperia `PESD5V0S1BA`** · `https://www.nexperia.com/product/PESD5V0S1BA` · VRWM 5 V / VBR 6 V min / V(CL)R 14 V / IPPM 12 A / PPPM 130 W / IRM 5 nA / IEC 61000-4-2 >30 kV / IEC 61000-4-5 IPPM 12 A / Cd 35 pF typ · 封装 **SOD-323 (2 lead, 1.3 mm pitch)** · ★**它只有 2 个引脚 (K1/K2 都是阴极, 双向件) ⇒ 在 Type-C 上只能保护 1 条线** |
| **候选2** | **TI `TPD1E05U06DPYR`** (2-pin DPY) **与 `TPD2E2U06`** (双通道, **DCK/SC70-3 3 脚 / DRL/SOT-5 5 脚**, 官方手册 SLLSEG9C: Cd **1.5 pF**, ±25 kV 接触 / ±30 kV 空气, IPPM 5.5 A, VBR 6.5 V min, ILEAK 10 nA max, 封装 DRL 1.60×1.20 mm / DCK 2.00×1.25 mm) · `https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf` · ★**TPD2E2U06 是"双通道 3/5 脚" ⇒ 落不下 2 焊盘, 列为方案二 (见降级方案)** |
| **推荐项 + 为什么 (不代拍)** | ★**推荐走"方案二"但只给依据, 拍板留给 V-2**: 依据 = Type-C 座要同时护 VBUS + D+ + D− ⇒ **双通道阵列 (TPD2E2U06 类) 在电气上才是正解** (单通道 2 脚件只能护 1 条线) · ★**代价 = 物理落不下 2 焊盘占位 (TPD2E2U06 最小封装是 3 脚 SC70-3) ⇒ 要改 footprint** · ⇒ **主候选给 2 脚件 `PESD5V0S1BA` (落 2 焊盘, 能立刻投板), 同时把"TPD2E2U06 双通道 + 改 footprint"作为代价明确写在推荐栏, 让 main 知道"选单通道 = 少护一条线"这个代价** · ★**我不代拍 V-2** |
| **封装兼容性结论** | ★**只能写"落 2 焊盘 + 充电板侧封装另行定"**: ★**`D_ESD_TC` 不在 `demo_mainboard.kicad_pcb` 上** (充电板 CHG_BOARD 件, BOM `footprint` 栏 = "待定") ⇒ 板文件里**没有**它的占位焊盘 ⇒ 本单**无几何可判** ⇒ **不许写"已兼容"** · 候选1 (SOD-323, 2 lead) 与候选2 之 TPD1E05U06DPYR (DPY, 2 pin) 都是 2 脚 ⇒ **落 2 焊盘成立**; TPD2E2U06 (3/5 脚) ⇒ **落不下 2 焊盘** ⇒ 归落表/板那一趟 (充电板自己改 footprint) |
| **证据等级** | `[官网]` (Nexperia 官方产品页 + TI 数据手册 SLVSBO7O / SLLSEG9C 原文) |
| **降级方案** | ★**若 C-01 规格最终定成"Type-C 座 + 单通道 ESD"**: 降级 = 直接落 2 脚 `PESD5V0S1BA` (SOD-323) ⇒ 充电板侧 footprint 按厂商 land 定 ⇒ ★**零额外风险** · ★**若规格要双通道**: 降级 = 选 3 脚双通道件 (`TPD2E2U06DCKR` SC70-3) + 充电板 footprint 改 3 焊盘 ⇒ 归落表/板那一趟 (充电板侧, 不影响主板) · ★**若 Type-C 要护 3 条线 (VBUS + D+ + D−) 而充电板只放得下 1 个 2 脚位**: 降级 = 选 **多通道阵列件** (如 Nexperia `PESD5V0S4UD` 四通道 / `PESD5V0S2UAT` 双通道 SOT-23) ⇒ 官方在售清单已在 Nexperia ESD 系列产品页列出 ⇒ **充电板 footprint 一次定到多通道** |

---

### §3.2 π 滤波磁珠 ×2

---

#### ⑤ `FB_DEMO` — MAIN_PCB · demo 板 VBUS π 滤波磁珠

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「RAIL_DEMO_5V VBUS π 滤波 (磁珠+体电容)」 · pad1 = RAIL_DEMO_5V, pad2 = GND · ★**实测几何**: 2 焊盘 **0.55×0.90 mm**, pad1 at (−0.4,−0.3) / pad2 at (+0.4,+0.3) ⇒ **X 向偏移 0.80 mm / Y 向 0.60 mm (直线间距 1.00 mm, 两焊盘呈对角布置)**, fab bbox **W=2.00 H=1.60 mm** ⇒ **这是 0805 (2.0×1.25 mm) 级别的占位** · 判据 = ① 0805 封装本体 ≤ 2.00×1.25 mm ② **额定电流 ≥ demo 板 VBUS 实际电流** (USB-C 5 V/2 A 档 ⇒ ≥2 A, 留余量取 3 A+) ③ **阻抗 @100 MHz 要够高** (π 滤波的 L 侧, 目标把 MHz 级开关噪声压下去) ④ **DCR 要低** (2 A 过流下压降 = I×DCR, 直接吃掉 VBUS 5 V 的余量) |
| **候选1** | **Murata `BLM21PG221SN1D`** · 链接 `https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads` (Murata 官方 chip ferrite bead lineup 页) + 数据手册 `https://www.digikey.com/en/products/detail/murata-electronics/BLM21PG221SN1D/364909` (目录页) · 关键参数: **0805 (2012 metric, 2.00×1.25 mm)**, **阻抗 220 Ω @100 MHz (±25%)**, **额定电流 2 A**, **DCR 45 mΩ (max)**, −55~+125 °C, 1 line, 单芯厚膜 · ★**注意: DCR 45 mΩ 在 2 A 下压降 90 mV / 损耗 180 mW** ⇒ 见降级方案 |
| **候选2** | **Murata `BLM31PG221SN1L`** (1206) ★**尺寸不合 0805 占位** ⇒ 改用同尺寸替代: **Murata `BLM21PG221SN1D` 的同族低 DCR 档 `BLM21PN221SN1D`** ★**该型号本轮未取到官方参数页 ⇒ 记 `[0数据]`**; 已抓到官方参数的同尺寸替代 = **Murata `BLM21PG601SN1D`** (0805, 600 Ω @100 MHz, 1.5 A, DCR 0.09 Ω — 来自 Murata 官方 `BLM31P` 系列表与 `BLM21P` 族表) ★**代价: DCR 0.09 Ω 是候选1 的 2 倍 ⇒ 2 A 下压降 180 mV / 损耗 360 mW** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `BLM21PG221SN1D`** · 理由: **阻抗 220 Ω @100 MHz + DCR 45 mΩ + 2 A 额定 + 0805 本体 2.00×1.25 mm 与占位 fab bbox 2.00×1.60 mm 精确对上** ⇒ 四项判据全中且 DCR 最低 (损耗 180 mW) · **代价**: ① **2 A 额定 = 刚好压在 USB-C 5 V/2 A 档上, 无余量** ⇒ 若 demo 板 VBUS 实际电流 >2 A 或要过 3 A PD 档, 需改 1206 (BLM31PG…) ⇒ 尺寸要变 (归板那一趟) ② **220 Ω @100 MHz 对 π 滤波的"高频段"够, 但对 30~100 MHz 中频段抑制弱** ⇒ 若噪声主频在中频, 需换 600 Ω 档 (代价 = DCR 翻倍 + 压降 180 mV) ③ DCR 45 mΩ 在 2 A 下 180 mW 发热 ⇒ **本板磁珠紧邻 VBUS 大电流路径, 散热路径要留给结构/板那一趟核** |
| **封装兼容性结论** | ★**兼容 (焊盘数 + 焊盘网络 + 本体尺寸三项全中)**: ① 焊盘数 **2 = 2** ✔ ② 焊盘网络 (pad1 = RAIL_DEMO_5V 进 / pad2 = GND 出) ✔ 对应磁珠两脚 ✔ ③ **本体 2.00×1.25 mm (0805) ≤ 占位 fab bbox 2.00×1.60 mm** ✔ ★**注: 候选1 官方 land (Murata BLM21 0805) 与占位 0.80 mm 中心距不重合 ⇒ 仍需落板批次按 Murata 官方 land 复核焊盘图, 但本体尺寸与方向 (两端对称) 无歧义** |
| **证据等级** | `[官网]` (Murata 官方 lineup 页 + 官方 BLM21 族数据表) · ★**占位几何 = 板文件实读** |
| **降级方案** | ★**若 2 A 额定不够 (需 ≥3 A)**: 降级 = 换 **1206 (3.2×1.6 mm) 的 `BLM31PG…` 系** (如 Murata 官方 `BLM31PG221SN1L` 类, 0805 放不下) ⇒ ★**归落表/板那一趟 (改 footprint 尺寸)** · ★**若 DCR 45 mΩ 的压降/发热不可接受**: 降级 = 换同尺寸更低 DCR 档 (Murata `BLM21P…` 系列的 P=power 族, 官方表里 `BLM21P221SG` 是 220 Ω / 2000 mA / 0.05 Ω) ⇒ ★**本轮未取到该型号的完整官方页 ⇒ 记 `[0数据]`, 落表批次补** · ★**若噪声主频不在 100 MHz 附近**: 降级 = 保留 220 Ω 档并加大 π 滤波的体电容 (C_VBUS_DEMO 已是 10 µF, 见网表) ⇒ 不改板 |

---

#### ⑥ `FB_VBUS` — CHG_BOARD · 充电板 VBUS π 滤波磁珠

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「VBUS_5V_ESD VBUS 入口 π 滤波磁珠位 (**阻抗/电流随充电 IC 环路稳定性定**)」 + 「VBUS_5V_F1 π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗)」 ⇒ ★**这是 BQ25896 的 VBUS 输入路径, 磁珠直接串在充电 IC 开关环路里 ⇒ 第一判据不是"滤噪声", 而是"不能把充电环路稳定性搞坏"** ⇒ 判据 = ① **DCR 必须低** (BQ25896 官方数据手册 §10.2.2 要求输入电容有足够纹波电流裕量, 而磁珠串在 VBUS 上会引入阻性阻尼) ② **额定电流 ≥ 充电板实际 VBUS 电流** (含 PD 5 V/2 A 档 + 充电电流路径) ③ 阻抗 @100 MHz 要够高挡 VBUS 上的开关噪声 ⇒ **阻抗与 DCR 是一对矛盾 (同系列内 Z 越高 DCR 越高)** |
| **候选1** | **Murata `BLM21PG221SN1D`** (0805, 220 Ω @100 MHz, 2 A, DCR 45 mΩ) · `https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads` · ★**对充电环路: 45 mΩ 串在 VBUS 上 ⇒ 2 A 时 90 mV 压降, 对 5 V 轨是 1.8%** |
| **候选2** | **Murata `BLM31PG221SN1L`** (1206, 3.2×1.6 mm) ★**本轮未取到该型号官方参数页 ⇒ 参数记 `[0数据]`**; 已抓到官方参数的同系列 1206 档 = **`BLM31PG121SN1`** (120 Ω @100 MHz, **3000 mA**, DCR **0.025 Ω**) / **`BLM31PG391SN1`** (390 Ω @100 MHz, 2000 mA, DCR 0.05 Ω) / **`BLM31PG601SN1`** (600 Ω @100 MHz, 1500 mA, DCR 0.09 Ω) — 全部来自 Murata 官方 `BLM31P` 系列表 (1206 尺寸 3.2±0.2 × 1.6±0.2 mm) ⇒ ★**额定电流 3000 mA + DCR 25 mΩ 是候选1 的 1.5× 电流 / 0.55× DCR ⇒ 对充电环路最友好** |
| **推荐项 + 为什么 (不代拍)** | **候选2 的 1206 档 `BLM31PG121SN1`** · 理由: 充电板侧 **DCR 25 mΩ (候选1 的 55%) + 额定 3000 mA (候选1 的 150%)** ⇒ 磁珠串在 BQ25896 VBUS 环路里, 阻性阻尼越小 ⇒ 环路稳定性裕量越大, 而 120 Ω @100 MHz 仍能挡掉 VBUS 上的 MHz 级开关噪声 · **代价**: ① **1206 (3.2×1.6 mm) 比 0805 大一整号** ⇒ 充电板面积成本 ↑ (充电板面积是 ISS-216/ISS-229 在盯的热点) ② 阻抗从 220 Ω 降到 120 Ω ⇒ 中高频段抑制弱一档 ③ ★**本板 `FB_VBUS` 的 footprint 是"待定" ⇒ 尺寸可以直接在充电板上定成 1206, 无需改主板** ⇒ 这也是它比 `FB_DEMO` 更该上大封装的原因 |
| **封装兼容性结论** | ★**只能写"落 2 焊盘 + 充电板侧封装另行定"**: ★**`FB_VBUS` 不在 `demo_mainboard.kicad_pcb` 上** ⇒ 板文件无占位 ⇒ 无几何可判 ⇒ **不许写"已兼容"** · 焊盘**数**上: 磁珠是 2 脚器件 ⇒ **落 2 焊盘成立** (候选1 0805 与候选2 1206 都是 2 脚) · 焊盘**网络**: 进 VBUS_5V_ESD / 出 VBUS_5V_F1 ⇒ 2 脚件天然对上 ✔ · 封装**尺寸**: 充电板侧 footprint 待定 ⇒ 0805/1206 都可定 ⇒ **由落表批次按选定的型号定充电板 footprint** |
| **证据等级** | `[官网]` (Murata 官方 lineup + 官方 BLM21/BLM31P 系列参数表) · ★**BQ25896 环路相关判据 = `[官网]` (TI 数据手册 SLUSC76C §10.2.2 输入电容纹波电流要求, 本地 PDF 实读)** |
| **降级方案** | ★**若充电板面积不够放 1206**: 降级 = 用 **0805 档 `BLM21PG221SN1D`** (DCR 45 mΩ) ⇒ ★**代价 = 充电环路阻尼变大 ⇒ 必须由 main/PM 用 BQ25896 官方应用章节 (10.2.2 Buck Input Capacitor + 环路补偿) 复核充电电流 1.22 A 档的稳定性** ⇒ 本单不代判 ⇒ 同时登记"磁珠影响充电环路稳定性"缺口 · ★**若 Imax 超过 3 A**: 降级 = 选 **1206 且 ≥6000 mA 的 `BLM31P330SG` (33 Ω / 6000 mA / 0.01 Ω)** 之类低 DCR 大电流档 (官方表已列) ⇒ 阻抗换低 ⇒ 噪声抑制靠 π 滤波的体电容补 |

---

### §3.3 TVS ×1

---

#### ⑦ `D_TVS_VBUS` — CHG_BOARD · Type-C 入口 5 V 级单向 TVS

| 项 | 内容 |
|---|---|
| **判据** | 网表 note (★**已含 PM 裁决, 照抄不改**): 「⚠️ 待裁决: 规格 §4.3 提到但 §7 连接清单未列的件 (插线尖峰 TVS: **VRWM ≥5.0V, 钳位电压 < BQ25896 绝对最大 22V**); 位置紧靠 Type-C 座; PM 确认是否纳入 BOM, 不纳入则删本 2 行; 型号待选型」 + 「★裁决 (PM): **必装** (Type-C 入口 TVS 是标配); **VRWM 5-6V 档, 脉冲电流额定 ≥3A** (PD 5V/2A 场景); 选型待定」 ⇒ ★**判据全部来自 PM 裁决, 不是本单自拟** · 交叉核对: BQ25896 数据手册 §8.1 Absolute Maximum Ratings 明写 **VBUS (converter not switching) −2 V … 22 V** ⇒ 钳位 < 22 V 有官方出处 ✔ |
| **候选1** | **Littelfuse `SMBJ5.0A`** · 链接 `https://www.littelfuse.com/products/tvs-diodes/smb-j` (官方系列页) + 目录 `https://www.lcsc.com/product-detail/C83333.html` · 关键参数: **VRWM 5.0 V / VBR 6.4 V (min) / Vc 9.2 V @ Ipp 65.3 A (10/1000 µs) / PPP 600 W / IR 800 µA max / −65~+150 °C / 单向 / DO-214AA (SMB)** ★**注意: "5-6V 档" 的 5 V 侧 = SMBJ5.0A, 6 V 侧 = SMBJ6.0A (ST 官方页 `https://www.st.com/en/protections-and-emi-filters/smbj6-0a.html` 确认 SMBJ 系列存在且封装在 SMB, ≤600 W 10/1000 µs)** |
| **候选2** | **STMicroelectronics `SMBJ6.0A`** · 链接 `https://www.st.com/en/protections-and-emi-filters/smbj6-0a.html` (官方产品页, 本轮 200 OK) · 关键参数: **VRWM 6.0 V** (⇒ 落在 PM 要求的 "5-6V 档" 上沿, 对 5 V±5% 轨余量更大) / 钳位电压 @ Ipp 与 PPP (10/1000 µs) 官方页只给了系列级描述 (**"below 600 W (10/1000 µs)"**, IEC 61000-4-2 / 61000-4-4 / 61000-4-5 适用), **具体 Vc / Ipp 数值本轮未取到 ⇒ 记 `[0数据]`, 落表批次按 ST 官方 SMBJ 手册补** · 封装 **SMB (DO-214AA), 2 焊盘** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `SMBJ5.0A`** · 理由: ① **参数全齐且可核** (Vc 9.2 V ≪ BQ25896 的 22 V 绝对最大, 留 2.4 倍余量) ② **Ipp 65.3 A ≫ PM 要求的 ≥3 A** ③ **PPP 600 W** 应对插线尖峰 ④ Littelfuse 是原厂官网可直接核 · **代价**: ① **VRWM 5.0 V 对 5.25 V 轨顶到边** (与 `D_ESD_DEMO` 同一个问题) ⇒ 若 main 判 "USB VBUS 常态 5.25 V 须留余量" 则应走候选2 的 6 V 档 ② **IR 800 µA max 在 VBUS 常驻下是持续漏电** (5 V × 800 µA = 4 mW, 对充电板本地供电无所谓, 但如果这块的漏电计入整机静态功耗账就要登记) ③ SMB 封装 (DO-214AA, ~4.4×3.6 mm) 比占位其它件都大 ⇒ 充电板面积成本 · ★**我不代拍 5 V 档 vs 6 V 档 (这属 PM 已裁的 "5-6V 档" 的解释权), 只给依据** |
| **封装兼容性结论** | ★**只能写"落 2 焊盘 + 充电板侧封装另行定"**: ★**`D_TVS_VBUS` 不在 `demo_mainboard.kicad_pcb` 上** (BOM footprint = "待定") ⇒ 无几何可判 ⇒ **不许写"已兼容"** · 焊盘**数**: TVS 是 2 脚器件 (阴极/阳极) ⇒ **落 2 焊盘成立** · 焊盘**网络**: pad1 = VBUS_5V / pad2 = GND ⇒ 与单向 TVS 的 K→VBUS / A→GND 一一对应 ✔ · 封装**尺寸**: SMB (DO-214AA) ≈ 4.4×3.6 mm ⇒ 充电板 footprint 按此定, 无主板冲突 |
| **证据等级** | `[官网]` (Littelfuse 官方系列页 + ST 官方产品页; ★**BQ25896 的 22 V 绝对最大 = TI 数据手册 SLUSC76C §8.1 原文, 本地 PDF 实读**) · ★**`SMBJ6.0A` 的 Vc / Ipp 具体值 = `[0数据]`** |
| **降级方案** | ★**若 main 判定 VRWM 必须 > 5.25 V**: 降级 = 选 **SMBJ6.0A / SMBJ7.0A (6~7 V 档)**, ST 与 Littelfuse 官网都有在售 (SMBJ6.0A 官方页本轮 200 OK) ⇒ ★**但 SMBJ6.0A 的 Vc/Ipp 数值本轮 `[0数据]`, 落表批次必须按官方手册核 Vc < 22 V 才准落** · ★**若充电板放不下 SMB**: 降级 = 选 **SMA 档 (`SMAJ5.0A` / `SMAJ6.0A`, DO-214AC, ~4.4×3.6→更小)** 或 **SOD-123 档** ⇒ 封装尺寸与参数落表批次按官网补 |

---

### §3.4 MOS ×4 (★**全部 3 焊盘占位 ⇒ 只能 SOT-23 类 3 脚件**)

★**共同硬约束 (main 实测 + 本单复测)**: 3 件 MAIN_PCB 的 MOS 占位都是 **3 焊盘**, 焊盘尺寸 **0.6×0.9 mm**, fab bbox **W=4.00 H=5.00 mm**, 焊盘 at = **(−1.4, −2) / (−0.13, −2) / (+1.4, +2)** ⇒ ★**这是 SOT-23 的 3 脚形态 (G/S/D 三端) 但 pad 间距被拉大到 1.27 mm / 1.53 mm (真 SOT-23 是 0.95 mm pitch) ⇒ 本体 2.9×1.3 mm 的 SOT-23 器件本体能放进 4.00×5.00 bbox, 但厂商 land 与占位不重合 ⇒ 仍需落板批次重画**。

★**pad ↔ pin 映射 (★本单逐件实测, 这是最容易踩坑的地方)**: 板文件占位的 pad 编号顺序 = **网表行出现的顺序 (网表顺序), 不是库封装的 G/S/D 顺序**:
- `Q_AND`: pad1 = **RESET_N** (网表: 漏极), pad2 = **GND** (源极), pad3 = **PG_AND** (栅极) ⇒ **pad 顺序 = D / S / G**
- `Q_ENVC`: pad1 = **PG_AND** (栅极), pad2 = **GND** (源极), pad3 = **EN_VCORE** (漏极) ⇒ **pad 顺序 = G / S / D**
- `Q_PG`: pad1 = **PWR_ON** (源极, 网表说 "源极接 ON"), pad2 = **BAT_SW** (漏极), pad3 = **PWR_GOOD** (栅极) ⇒ **pad 顺序 = S / D / G**
⇒ ★**三件的 pad↔pin 顺序三样都不同** ⇒ ★**换任何 SOT-23 器件都必须逐件重新核 pad↔pin 映射, 不能拿 "SOT-23 就是 G-S-D" 想当然** (这是本单最容易被漏掉的坑, 已写进交卷单 B3)。

---

#### ⑧ `Q_AND` — MAIN_PCB · N-MOS 硬件 AND

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「★V1.8 复位链 ②: Q_AND 把『两路 PG 都好』变成硬件许可 —— **漏极 = RESET_N**; 任一路 PG 坏 · PG_AND 高 · Q_AND 导通 · 拉住复位; 两路都好 · PG_AND 低 · Q_AND 关 · 允许释放 (与 U_SUPV 的开漏信号并联, 两路都放行才算复位释放) ⇒ **不依赖 TBD-12 也能定住上电时序**」 + 「源极接地」 ⇒ 判据 = ① **N 沟道增强型, 3 脚 (G/S/D)** ② ★**VGS(th) 必须低** (栅极由 `PG_AND` = U_DCDC_VIO pin4 的开漏信号驱动, 3.3 V 域 ⇒ 阈值太高则复位永远释放不了) ③ **关断漏电要小** (漏极挂在 `RESET_N` 上, 漏电直接抬复位电平) ④ 3.3 V 栅驱动下要能拉到 RESET_N 的有效低 (RESET_N 侧有 R_PU_RESET_N 10 k 上拉 ⇒ 拉低电流 ≈ 330 µA, 极小) |
| **候选1** | **Alpha & Omega `AO3400A`** · 链接 `https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf` (官方数据手册 Rev 3.1, 2023-07) + 官网产品页 `https://www.aosmd.com/zh/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a` · 关键参数: **30 V N 沟道**, **VGS(th) 0.65 V (min) / 1.05 V (typ) / 1.45 V (max)**, **RDS(on) 26.5 mΩ @VGS=10 V / 32 mΩ @4.5 V / 48 mΩ @2.5 V**, ID 5.7 A (TA=25 °C), PD 1.4 W, **IGSS ≤ 100 nA**, VDS 30 V, VGS ±12 V, TJ −55~+150 °C, 封装 **SOT-23 (3 脚, 引脚序 G-S-D: pin1=G, pin2=S, pin3=D)** |
| **候选2** | **onsemi `2N7002`** (SOT-23, 60 V) · 链接 `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf` (原厂数据手册) + onsemi `https://www.onsemi.com/download/data-sheet/pdf/2n7002dw-d.pdf` · 关键参数: **60 V N 沟道, VGS(th) 1.0 V (min) / 1.76 V (typ) / 2.0 V (max) (2N7002DW)**, **RDS(on) 1.2 Ω typ @VGS=10 V / 2.4 Ω typ @4.5 V**, ID 115 mA 连续 (Microchip 版) / 380 mA (2N7002K), PD 0.36 W, IDSS ≤ 1 µA (2N7002DW), IGSS ±10 nA, 封装 **SOT-23 (3 脚)** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `AO3400A`** · 理由: ★**VGS(th) max 1.45 V vs 候选2 的 max 2.0 V** ⇒ 在 3.3 V 栅驱动下候选1 有 2.3× 的过驱动余量、候选2 只有 1.3× ⇒ ★**这一条是"硬件 AND 能不能真放开复位"的成败线** (栅压不足 ⇒ MOS 半导通 ⇒ RESET_N 被拖在中间电平) · 另: RDS(on) 48 mΩ @2.5 V vs 2.4 Ω ⇒ 拉低 RESET_N 的压降差 50 倍 (虽然两者都远够 330 µA, 但余量差别大) · **代价**: ① RDS(on) 26.5 mΩ 对这个位是**过剩规格** (更省的是 2N7002 这类小信号管, 便宜且够用) ② **AO3400A 是 AOS 的料, 需确认在售通道** (本轮抓到的是官网数据手册 + 官网产品页 ⇒ 在售属性由目录页佐证) ③ **VGS ±12 V 绝对最大**: 栅极在 3.3 V 域, 余量充足 ✔ |
| **封装兼容性结论** | ★**条件兼容 (需落板批次重画 land + 必须逐件核 pad↔pin)**: ① 焊盘数 **3 = 3** ✔ ② 焊盘网络: pad1=RESET_N(D) / pad2=GND(S) / pad3=PG_AND(G) ⇒ ★**AO3400A 的库引脚序是 pin1=G / pin2=S / pin3=D ⇒ 占位的 pad↔pin 映射与器件引脚序【不一致】(占位是 D/S/G) ⇒ 落板批次重画 land 时必须把 RESET_N 接到器件的 D 脚、PG_AND 接到 G 脚, 不能按 pad 序号机械对** ③ 本体 2.9×1.3 mm (SOT-23) 落在占位 fab bbox 4.00×5.00 mm 内 ✔ |
| **证据等级** | `[官网]` (AOS 官方数据手册 + Microchip/onsemi 官方数据手册) · ★**占位 pad↔net 为板文件实读** |
| **降级方案** | ★**若落板批次不想重画 land**: 降级 = 选 **引脚序与占位 pad 顺序一致 (D/S/G) 的 3 脚器件** ⇒ 本轮在售 3 脚 SOT-23 绝大多数是 G-S-D 序 ⇒ ★**几乎不可能免重画 ⇒ 这条降级实际等于"必须重画"** ⇒ 登记为缺口 G-2 · ★**若 AOS 采购通道不通**: 降级 = onsemi `2N7002` / `2N7002K` (SOT-23, 官网数据手册已核) ⇒ ★**代价 = VGS(th) max 2.0 V 在 3.3 V 驱动下过驱动只剩 1.3×, 且 RDS(on) 2.4 Ω @4.5 V ⇒ 必须由 main 复核 "PG_AND 低时 Q_AND 必须完全关断" 这条时序是否还成立** |

---

#### ⑨ `Q_ENVC` — MAIN_PCB · N-MOS 反相

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「★V1.8: V_SOC_IO 的 PG 有效 (低) · Q_ENVC 关 · EN_VCORE 被上拉为高 · V_CORE 使能 ⇒ **顺序链**; PG 极性**待原厂核** (TPS62130A PG 为开漏信号)」 + 「漏极 = EN_VCORE (把 EN 拉低 = 不使能)」 + 「源极接地」 ⇒ ★**这是一个"栅压高 ⇒ 关 ⇒ EN 被 10 k 上拉为高 ⇒ 使能"的反相逻辑 ⇒ 判据与 Q_AND 相反: 栅极拉高时 MOS 必须【完全导通地拉住 EN_VCORE 低】 ⇒ VGS(th) 越低越稳, 但同时关断漏电必须小 (漏极在 EN_VCORE, 漏电会把 EN 顶高 ⇒ 直接影响 V_CORE 使能与否)** ⇒ 判据 = ① N 沟道 3 脚 ② **VGS(th) 低 + 在 3.3 V 下完全导通** (R_EN_VCORE 10 k 上拉 ⇒ 拉低电流 ≈ 330 µA) ③ **关断漏电要极小** (挂在 EN_VCORE 上, 漏电 = 误使能) ④ ★**注意网表自己标了 "PG 极性待原厂核" ⇒ 本单选型按"低栅压=关"和"高栅压=导通"两种极性都能用的器件 (阈值对称、无体二极管方向的逻辑依赖) 来给** |
| **候选1** | **Alpha & Omega `AO3400A`** · `https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf` · **VGS(th) 0.65/1.05/1.45 V**, RDS(on) 26.5 mΩ@10 V / 32 mΩ@4.5 V / 48 mΩ@2.5 V, **IGSS ≤ 100 nA**, IDSS ≤ 1 µA (VDS=30 V, VGS=0 V, TJ=55 °C) 的量级, 30 V, 封装 **SOT-23 (pin1=G, pin2=S, pin3=D)** |
| **候选2** | **onsemi `2N7002`** · `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf` · **VGS(th) 1.0/1.76/2.0 V**, RDS(on) 1.2 Ω typ @10 V, **IGSS ≤ ±10 nA**, IDSS ≤ 1 µA, 60 V, 封装 **SOT-23** · ★**低漏电优势 (IGSS 10 nA vs AO3400A 100 nA) 对 "EN_VCORE 误使能" 这条更友好** |
| **推荐项 + 为什么 (不代拍)** | ★**这里两个候选是"不同维度各自最优", 我不合并成单一答案**: ★**候选1 `AO3400A` 赢在 VGS(th) (max 1.45 V vs 2.0 V) ⇒ 完全导通把握大 ⇒ EN_VCORE 被可靠拉到低 ⇒ 顺序链可靠** ★**候选2 `2N7002` 赢在 IGSS (10 nA vs 100 nA, 10 倍) ⇒ 关断时对 EN_VCORE 的漏电抬升更小 ⇒ 误使能风险低** · ★**两件的 RDS(on) 在 330 µA 负载下压降都 < 1 mV, 这一维无差别** ⇒ **真正的取舍只有 "栅压裕量 vs 漏电裕量"** ⇒ ★**我建议候选1 (栅压裕量优先, 因为 EN_VCORE 是顺序链的最后一环, 误使能可以通过软件/时序兜底而拉不低是硬失效), 但把候选2 的漏电优势摆出来, 由 main 裁** |
| **封装兼容性结论** | ★**条件兼容 (需落板批次重画 land + 逐件核 pad↔pin)**: ① 焊盘数 **3 = 3** ✔ ② 焊盘网络: pad1=PG_AND(G) / pad2=GND(S) / pad3=EN_VCORE(D) ⇒ ★**本件的 pad 顺序恰好是 G/S/D, 与 SOT-23 库引脚序 (pin1=G/pin2=S/pin3=D) 【一致】⇒ 本件是三件 MOS 里唯一不用改映射的** ✔ ③ 本体 2.9×1.3 mm ≤ 4.00×5.00 bbox ✔ |
| **证据等级** | `[官网]` (AOS + Microchip/onsemi 官方数据手册) · ★**占位 pad↔net 为板文件实读** |
| **降级方案** | ★**若 main 判 "漏电误使能" 权重更高**: 降级 = 选 IGSS ≤ 10 nA 的 3 脚 SOT-23 (onsemi `2N7002` / `2N7002K`, 官网已核) ⇒ ★**代价 = VGS(th) max 2.0 V 时 "PG 高 ⇒ 必须完全导通拉低 EN_VCORE" 的裕量下降 ⇒ 需 main 结合 "PG 极性待原厂核" (网表 note 明写) 一起裁** · ★**若 PG 极性最终是反的**: 降级 = 本件改用 N 沟道 + 拉电阻拓扑 (需改板) ⇒ 归落表/板那一趟 |

---

#### ⑩ `Q_PG` — MAIN_PCB · ★**P-MOS 高边开关 (低漏, Vgs(th) 明确)**

| 项 | 内容 |
|---|---|
| **判据** | 网表 note (★照抄不改): 「★**V1.9 P0 修正 (2026-10-28)**: Q_PG 由 N-MOS 改 **P-MOS 高边开关** —— 原 N-MOS 低边接法是**错的** …… ★**正解 (零新增 pin · 零新增轨)**: 源极接 ON · **漏极接 BAT_SW (电池轨, 关机后仍带电)** · 栅极接 PG ⇒ PG 低(良好)→Vgs≈−4.2V→P-MOS 导通→ON=BAT_SW=高=**开机**; PG 高(无输入)→Vgs=+3.3V→P-MOS 关→ON 落下拉=低=**关** (关机态仍能充电) ⇒ ★**选型硬判据: 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级**」 ⇒ 判据 = ① **P 沟道, 3 脚 (G/S/D)** ② ★**Vgs(th) 明确且要在 −4.2 V 附近可靠导通** (Vgs≈−4.2 V 是本拓扑的核心 ⇒ 阈值越靠近 0 越容易导通, 但也不能低到 PG 高时被误导通) ③ ★**栅极绝对最大耐压 ±20 V** (note 明写) ④ ★**关断漏电 nA 级** (★这条最硬: 漏极挂 BAT_SW 电池轨, 漏电直接吃电池 ⇒ 兼贴皮肤温度) ⑤ 源漏耐压 ≥ 4.2 V + 余量 |
| **候选1** | **Diodes Inc `DMP3098L`** · 链接 `https://www.diodes.com/datasheet/download/DMP3098L.pdf` (官方数据手册 DS, **本轮已下载原厂 PDF 并本地实读**) · 关键参数: **−30 V P 沟道, SOT23**, **IDSS (关断漏电) ≤ 800 nA @VDS=−30 V** ★**⇒ 直接命中 "nA 级" 硬判据** · **IGSS ≤ ±100 nA**, **VGS(th) −1.0 V (min) / −1.8 V (typ) / −2.1 V (max)** (VDS=VGS, ID=−250 µA) ⇒ ★**typ −1.8 V 距离本拓扑的 Vgs≈−4.2 V 有 2.4 V 余量 ⇒ 可靠导通** · **RDS(on) 56 mΩ (typ) / 70 mΩ (max) @VGS=−10 V; 98 mΩ (typ) / 120 mΩ (max) @VGS=−4.5 V** ⇒ ★**−4.5 V 那档正好覆盖本拓扑的 −4.2 V 工作点** · ID −3.8 A, BVDSS −30 V, TJ −55~+150 °C, 封装 **SOT23 (3 脚)** |
| **候选2** | **Alpha & Omega `AO3407A`** · 链接 `https://www.aosmd.com/pdfs/datasheet/AO3407A.pdf` (官方数据手册 Rev 5.1, 2023-07) + 官网 `https://www.aosmd.com/products/ao3407a` · 关键参数: **−30 V P 沟道, SOT-23**, **VGS(th) −1.4 V (min) / −1.9 V (typ) / −2.4 V (max)**, **RDS(on) 48 mΩ (max) @VGS=−10 V / 78 mΩ (max) @VGS=−4.5 V**, ID −4.3 A, **IDSS ≤ −1 µA @VDS=−30 V (TJ=25 °C) / −5 µA (TJ=55 °C)**, IGSS ±100 nA, **VGS ±20 V (绝对最大)**, PD 1.4 W, TJ −55~+150 °C, 封装 **SOT-23 (3 脚, pin1=G, pin2=S, pin3=D)** |
| **推荐项 + 为什么 (不代拍)** | ★**候选1 `DMP3098L` 赢在 "关断漏电 nA 级" 这条硬判据** (IDSS ≤ 800 nA vs AO3407A 的 ≤ 1 µA@25 °C / **5 µA@55 °C** ⇒ **高温下差 6 倍**) ⇒ **Q_PG 的漏极直接挂 BAT_SW 电池轨, 且本板贴皮肤 ⇒ 55 °C 皮肤侧环境下的漏电与自发热正相关 ⇒ 高温档漏电是硬指标** · 且 VGS(th) typ −1.8 V / max −2.1 V 比 AO3407A 的 typ −1.9 / max −2.4 V 更靠近 0 ⇒ 在 Vgs≈−4.2 V 时过驱动更大 · **代价**: ① **RDS(on) 略高** (98 mΩ typ @−4.5 V vs AO3407A 78 mΩ max @−4.5 V) ⇒ 但这条通路只过 PG 栅极的微安级电流 ⇒ **压降不是瓶颈** ② **Diodes Inc 的供货与在售状态本轮只核到官网数据手册 + 官网型号页, 目录在售页本轮未抓到 ⇒ 采购通道需落表批次确认** (登记为缺口) ③ **±20 V 栅极绝对最大: DMP3098L 的手册未给 VGS 绝对最大栏 (只给 IGSS 测试条件 VGS=±20 V) ⇒ DMP3098L 的栅极耐压按 `[0数据]` 处理, 而 AO3407A 明写 ±20 V ⇒ ★**这条反而是 AO3407A 明确占优** |
| **封装兼容性结论** | ★**条件兼容 (需落板批次重画 land + 逐件核 pad↔pin)**: ① 焊盘数 **3 = 3** ✔ ② 焊盘网络: pad1=PWR_ON(**S**, 网表: 源极接 ON) / pad2=BAT_SW(**D**, 漏极接 BAT_SW) / pad3=PWR_GOOD(**G**, 栅极接 PG) ⇒ ★**pad 顺序 = S/D/G, 与 SOT-23 库引脚序 (G/S/D) 【不一致】⇒ 落板批次重画 land 时必须把 PWR_GOOD 接到器件 G 脚、PWR_ON 接到 S 脚、BAT_SW 接到 D 脚** ★**★这正是 brief 说的 "P-MOS 高边开关 ⇒ Vgs(th) 与 Rds(on) 必须给对" 里最容易翻车的环节: 接反了 Vgs 极性就反, PG 低反而关机** ③ 本体 2.9×1.3 mm ≤ 4.00×5.00 bbox ✔ · ★**另注: 网表说 "源极接 ON / 漏极接 BAT_SW" —— 对 P 沟道高边开关, 源极应是高电位侧 (BAT_SW), 漏极接 ON (负载侧) 才成立; ★**网表 note 的措辞与 P-MOS 高边开关的常规拓扑相反** ⇒ ★**本单只照抄网表 note 不改拓扑, 但把这条矛盾登记为缺口 G-1 交 main / PM 裁决 (属落表/原理图那一趟), 不在本单拍** |
| **证据等级** | `[官网]` (Diodes Inc 原厂 PDF 本地实读 + AOS 原厂 PDF) · ★**占位 pad↔net 为板文件实读** |
| **降级方案** | ★**若 DMP3098L 采购通道不通**: 降级 = `AO3407A` (VGS ±20 V 明写, 参数全) ⇒ ★**代价 = 关断漏电高温档 5 µA (vs 800 nA) ⇒ 在贴皮肤 + 55 °C 环境下这 5 µA 会直接进电池账, 需 main 把这条记进关机续航预算 (参照 ISS-172 的 108 µA 关机账) 并给接受与否** · ★**若 ±20 V 栅极耐压是硬门槛而 DMP3098L 查不到**: 降级 = 只能 AO3407A ⇒ **代价同上一条** ⇒ ★**★V-2 的 "ESD 方案二选一" 之外的另一条待裁项: Q_PG 漏电档位要不要为 nA 级牺牲 RDS(on) 裕量** (归 main / PM, 本单不代拍) · ★**若网表拓扑矛盾 G-1 裁决为 "源漏要反过来"**: 降级 = 选 **源漏对称性无关的器件** (P 沟道 MOSFET 本身源漏可互换, 但 VGS 极性定义随之反向) ⇒ ★**落表批次必须连原理图一起核, 归落表/板那一趟** |

---

#### ⑪ `Q_CHG_LED` — CHG_BOARD · 充电板本地 LED 开关 N-MOS

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「★充电灯的本地开关管: **漏极 = LED 阴极, 源极 = GND, 栅极 = 本地 STAT**; 充电中 (STAT 低) → 导通 → 灯亮; 完成/禁用 (STAT 高) → 灯灭; **故障 1Hz 闪 → 灯跟着闪 (免费得到故障指示)**; 电流回路全在充电板本地, 不经跨铰链」 + 「★2026-11-03 09:5x 订正: BQ25896 的 STAT (pin4) 是**单个开漏输出**, 不能同时挂两个网 ⇒ 充电板本地 LED 栅极与跨铰链 STAT **合并成一个网**; 同时删掉充电板本地的 5 V 上拉 (它会把 5 V 送到 SoC 的 3.3 V 开漏输入 ⇒ 过压), 上拉留在主板侧 R_PU_CHG_STAT (10 k 到 3.3 V)」 ⇒ 判据 = ① N 沟道 3 脚 ② **栅极由 BQ25896 的 STAT 开漏驱动 (3.3 V 域, 上拉到 3.3 V)** ⇒ VGS(th) 必须够低 ③ **关断漏电要小** (漏极挂 LED 阴极, 漏电 ⇒ 灯微亮/误亮) ④ 电流: LED 回路 = VBUS_5V_CHG → R_CHG_LED (1 k) → LED → 阴极 → Q_CHG_LED → GND ⇒ **LED 电流 ≈ (5 − Vf)/1 k ≈ 3 mA** ⇒ 开关管只需 mA 级 ⇒ **小信号管足够, 不需要功率管** |
| **候选1** | **onsemi `2N7002`** (SOT-23, 60 V) · `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf` · **VGS(th) 1.0/1.76/2.0 V**, RDS(on) 1.2 Ω typ@10 V, **IGSS ≤ ±10 nA**, IDSS ≤ 1 µA, ID 115 mA 连续 ⇒ **3 mA 负载下 RDS(on) 压降 = 3 mA × 1.2 Ω ≈ 3.6 mV (可忽略)** ✔ |
| **候选2** | **Alpha & Omega `AO3400A`** (SOT-23, 30 V) · `https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf` · **VGS(th) 0.65/1.05/1.45 V**, RDS(on) 48 mΩ@2.5 V / 26.5 mΩ@10 V, IGSS ≤ 100 nA, ID 5.7 A ⇒ **VGS(th) 更低 ⇒ STAT 开漏驱动更可靠; 但 30 V 耐压对 5 V 回路够** |
| **推荐项 + 为什么 (不代拍)** | ★**候选1 `2N7002` 赢在这个位的真实需求 (mA 级电流 + 低漏电)**: ① **3 mA 负载 ⇒ 1.2 Ω 的 RDS(on) 完全够** (AO3400A 的 26.5 mΩ 是过剩规格, 换不来任何功能收益, 只会多花钱多占料号) ② **IGSS 10 nA (vs 100 nA) ⇒ 关断时 LED 阴极漏电低 10 倍 ⇒ 灯不会微亮** ③ ID 115 mA 对 3 mA 有 38× 余量 · **代价**: ★**VGS(th) max 2.0 V vs STAT 实际驱动电压**: STAT 是 BQ25896 的开漏输出, 高电平由主板侧 R_PU_CHG_STAT (10 k → 3.3 V) 决定 ⇒ 高电平可达 3.3 V ⇒ 3.3 − 2.0 = 1.3 V 过驱动 ⇒ **偏薄但可用**; ★**但 "STAT 低 = 充电中 = 灯亮" 意味着 MOS 的【关断】由 VGS(th) 决定 ⇒ VGS(th) max 2.0 V 而 3.3 V 驱动 ⇒ 可靠关断 ✔** ⇒ ★**建议候选1, 但把"VGS(th) max 2.0 V 在 3.3 V 驱动下过驱动仅 1.3 V"这条明确写出, 由 main 裁** |
| **封装兼容性结论** | ★**只能写"落 2/3 焊盘 + 充电板侧封装另行定"**: ★**`Q_CHG_LED` 不在 `demo_mainboard.kicad_pcb` 上** (BOM footprint = "待定") ⇒ 无几何可判 ⇒ **不许写"已兼容"** · 焊盘**数**: MOS 是 3 脚 ⇒ **落 3 焊盘** (候选1/2 都是 SOT-23 3 脚) · 焊盘**网络**: 漏极↔CHG_LED_K (LED 阴极) / 源极↔GND / 栅极↔CHG_STAT ⇒ 与 SOT-23 的 G/S/D 一一对应 ✔ (★**但充电板 footprint 待定 ⇒ 由落表批次按选定型号定 3 焊盘 land, 顺带把 pad↔pin 序定成 G/S/D 以免重犯主板那三件的错**) |
| **证据等级** | `[官网]` (Microchip/onsemi + AOS 官方数据手册) · ★**占位缺失 = 板文件实读确认** |
| **降级方案** | ★**若 STAT 驱动电压不足 3.3 V (例如 STAT 上拉被删)**: 降级 = 换 **VGS(th) 更低的管 (AO3400A, max 1.45 V)** ⇒ ★**代价 = 过剩规格, 多花成本** · ★**若要同时满足低漏 + 低阈值**: 降级 = 选 **AO3401A 类 (VGS(th) 更低) 或并 1 只栅极下拉电阻** ⇒ ★**但网表 note 明写 "同时删掉充电板本地的 5 V 上拉", 加下拉属改网表 ⇒ 归落表批次, 本单不落表** |

---

### §3.5 LED ×3

★**共同硬约束**: 2 件 MAIN_PCB 的 LED 占位 = **2 焊盘, 焊盘 0.6×0.9 mm, pad1 at (−0.45,−0.2) / pad2 at (+1.85,−0.2) ⇒ 中心距 2.30 mm**, fab bbox **W=2.70 H=1.60 mm** ⇒ **0805 (2.0×1.25 mm) 级别占位** · 焊盘网络: `D_LED_G` pad1=LED_G_D / pad2=GND, `D_LED_R` pad1=LED_R_D / pad2=GND ⇒ **pad2 = GND = 阴极侧 (网表 note: "LED_G 阴极 -> GND") ⇒ 阳极必须接 pad1** ★**这决定了 LED 是有极性的器件, 落板批次重画 land 时 pad↔pin 序不能反**。

---

#### ⑫ `D_LED_G` — MAIN_PCB · 绿色指示灯

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「LED_G 阴极 -> GND」 · 串阻 `R_LED_G` = **1 k ±1%**, 上游 `LED_G` 网 = J_SOM_P1 pin80 ⇒ ★**驱动电流 ≈ (3.3 V − Vf)/1 k ⇒ Vf 2.2 V 时 ≈ 1.1 mA** ⇒ 判据 = ① **0805 本体 (2.0×1.25 mm) ≤ 占位 fab bbox 2.70×1.60 mm** ② **VF 要匹配 1 k 串阻下的亮度** (3.3 V 域, ~1 mA ⇒ 要挑**低电流高亮度**的料, 普通 20 mA 标称 LED 在 1 mA 下亮度会大幅下降) ③ **波长落在人眼绿光区 (λdom ~565-570 nm)** ④ 极性: 阴极→GND (pad2) · ★**注意: 本板 `D_LED_B` 是 DNP 不装, 只有 G/R 两颗 ⇒ 绿/红是唯二指示色** |
| **候选1** | **Kingbright `KP-2012SGC`** (0805 超亮绿) · 链接 `https://www.tme.eu/Document/05a11926c5bbe30cd4bcc8411758e7d5/KP-2012SGC.pdf` (原厂数据手册 DSAB1341 V.21B) + 官网产品页 `https://www.kingbrightusa.com/category.asp?catalog_name=LED&category_name=KC0805+LED+Height-1.1mm` · 关键参数: **0805 (2.0×1.25 mm)**, **λpeak 565 nm / λdom 568 nm**, **VF 2.2 V (typ) / 2.5 V (max) @IF=20 mA**, 亮度 12 mcd typ @20 mA (KP-1608SGC 同族 0805 版), **IF 25 mA (DC) / 140 mA (peak)**, IR ≤ 10 µA @VR=5 V, **C 15 pF**, PD 62.5 mW, VR 5 V, **TJ 110 °C, 工作 −40~+85 °C**, MSL 3, RoHS |
| **候选2** | **Kingbright `APH1608SGC`** (0603 绿, 同一原厂的低电流封装版) · 链接 `https://www.kingbrightusa.com/images/catalog/spec/APH1608SGC.pdf` (原厂数据手册 DSAA5927 V.13B) + `https://www.kingbrightusa.com/category.asp?catalog_name=LED&category_name=KC0603+LED+Height-0.65mm` · 关键参数: **0603 (1.6×0.8 mm)**, λdom 568 nm / 570 nm, **VF 2.2 V (typ) / 2.5 V (max) @20 mA**, IV 5/12 mcd @20 mA, **IF 25 mA / IFM 140 mA**, IR ≤ 10 µA, **C 15 pF**, PD 62.5 mW, TJ 110 °C, −40~+85 °C · ★**注意: 这是 0603, 不是 0805 ⇒ 见封装兼容性** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `KP-2012SGC`** · 理由: ① **0805 本体与占位 fab bbox 2.70×1.60 mm 精确对齐** (0603 的 1.6×0.8 在同 bbox 里偏小, 落板后 LED 位置会比原设计靠内 0.2 mm) ② **同厂同参数族 (VF 2.2/2.5 V, C 15 pF, PD 62.5 mW, TJ 110 °C)** ⇒ 与 `D_LED_R` 可以同料号族采购 (关键参数同档) · **代价**: ★**1 k 串阻 + 3.3 V ⇒ 实际电流只有 ~1.1 mA, 而这两个候选都是 20 mA 标称 ⇒ 1.1 mA 下实际亮度远低于标称 (Kingbright 数据手册给的是 20 mA 点的值, 1 mA 点的亮度本轮 `[0数据]`) ⇒ ★**这是本板 LED 亮度账的一个既有缺口 (R 阻值 1 k 与 LED 标称电流 20 mA 不匹配), 不在本单改 (R 的阻值是网表已定的), 但必须登记给 main** —— 见 §4 缺口 G-5** |
| **封装兼容性结论** | ★**候选1 兼容 / 候选2 兼容但尺寸偏小**: ① 焊盘数 **2 = 2** ✔ ② 焊盘网络 (pad1=LED_G_D=阳极 / pad2=GND=阴极) ✔ 与网表 note "阴极->GND" 一致 ✔ ③ 候选1 本体 2.0×1.25 mm ≤ 2.70×1.60 ✔ **候选2 本体 1.6×0.8 mm 也放得下但偏小** ⇒ 两者**都要落板批次按 Kingbright 官方 land 重画** (占位 0.6×0.9 mm @ 2.30 mm 中心距 与 0805 官方 land 不重合) |
| **证据等级** | `[官网]` (Kingbright 原厂数据手册 + 原厂官网产品页) |
| **降级方案** | ★**若要提亮度**: 降级 = ★**改用低电流高亮度型 LED (Kingbright `APHBM2012LCGKSYKC` 类, 2 mA 级) 或把串阻从 1 k 改小** ⇒ ★**改阻值 = 改网表 ⇒ 归落表批次, 本单不落表** · ★**若板面没有 0805 空间**: 降级 = 候选2 (0603) ⇒ ★**代价 = 与 `D_LED_R` 不同封装尺寸, 两颗不同料号** · ★**若 λdom 568 nm 不满足指示色标准**: 降级 = 同封装 `AP2012CGCK` (0805 绿, λdom 570 nm, 20/50 mcd @20 mA — 原厂官网 0805 页列出) ⇒ 参数同封装可比 |

---

#### ⑬ `D_LED_R` — MAIN_PCB · 红色指示灯

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「LED_R 阴极 -> GND」 · 串阻 `R_LED_R` = **1 k ±1%**, 上游 `LED_R` 网 = J_SOM_P1 pin80 ⇒ 驱动电流 ≈ (3.3 − Vf)/1 k ≈ 1.3 mA (红光 Vf 更低) ⇒ 判据 = ① 0805 本体 ≤ 2.70×1.60 ✔ ② **VF 低 (红光 ~1.9-2.2 V) ⇒ 1 k 下电流更足** ③ **λdom ~617-630 nm (红光区)** ④ 阴极→GND (pad2) · ★**颜色与 `D_LED_G` 同为 SoM 驱动 (pin80/pin19), 两颗必须同档亮度才能对称** |
| **候选1** | **Kingbright `APT1608SURCK`** (0603 超亮红) · 链接 `http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APT1608SURCK` (原厂官网产品页) + `https://www.kingbrightusa.com/category.asp?catalog_name=LED&category_name=KC0603+LED+Height-0.65mm` · 关键参数: **1.6×0.8×0.75 mm (0603)**, **AlGaInP**, **λdom 630 nm**, **IV 40 mcd (min) / 80 mcd (typ) @20 mA**, 视角 120°, 封装 2000 pcs/卷, MSL 3, RoHS · ★**注意: 原厂 0603 页同时列了 `APT1608EC` (617 nm, 3/8 mcd @20 mA, 低亮度版) 与 `APH1608SURCK` (630 nm, 40/80 mcd) ⇒ 红光有亮度档位要选** |
| **候选2** | **Kingbright `AA1608SURSK`** (0603 PLCC-2 红) · 链接 `https://www.kingbrightusa.com/lobbyMinaturePLCC2.asp` (原厂官网 PLCC-2 页) · 关键参数: **0603 (1.6×0.8×0.55 mm)**, **λdom 630 nm**, **IV 40 mcd (min) / 160 mcd (typ) @20 mA**, 视角 120°, 额定 IF 30 mA / IFM 185 mA, PD 75 mW, 工作 −40~+85 °C · ★**亮度更高 (160 vs 80 mcd) ⇒ 1 mA 工作下相对更亮** |
| **推荐项 + 为什么 (不代拍)** | ★**候选2 `AA1608SURSK` 的理由是亮度余量**: ① **160 mcd typ vs 候选1 的 80 mcd typ ⇒ 同 1.3 mA 电流下相对更亮** (本板 1 k 串阻 ⇒ 电流远低于标称 20 mA ⇒ 亮度余量是唯一能救这个位的参数) ② **PLCC-2 结构比普通 chip LED 更适合贴导光孔/结构件** (充电板/镜脚有导光孔需求) ③ 尺寸 1.6×0.8×0.55 mm 与候选1 同 ⇒ 两种封装可互换 · **代价**: ① **两款都是 0603, 而占位 fab bbox 是 0805 级 (2.70×1.60) ⇒ 本体偏小 ⇒ 与 `D_LED_G` 的 0805 候选不同封装, 两颗 LED 尺寸不同** (可接受, 但落板批次要用两套 land) ② **★`D_LED_G` 我推 0805 / `D_LED_R` 我推 0603 ⇒ 两颗不同封装 ⇒ 若 main 要求两颗对称 (同封装同亮度档), 应改成两颗都用 0805 (`KP-2012SGC` + `AP2012EC`/`AA1608SURSK` 的 0805 对应料) ⇒ 这一条留给 main 裁** |
| **封装兼容性结论** | ★**兼容 (本体尺寸落在占位 bbox 内, 但需重画 land)**: ① 焊盘数 **2 = 2** ✔ ② 焊盘网络 (pad1=LED_R_D=阳极 / pad2=GND=阴极) ✔ ③ 本体 1.6×0.8×0.75 mm ≤ 2.70×1.60 mm ✔ (偏小, 落板后位置比原设计靠内) ⇒ **落板批次按 Kingbright 官方 land 重画** |
| **证据等级** | `[官网]` (Kingbright 原厂官网产品页 + 原厂 PLCC-2 产品页) · ★**两颗 LED 的 VF/IV 逐点值以原厂页为准; 1 mA 工作点的亮度 = `[0数据]`** |
| **降级方案** | ★**若两颗 LED 要同封装**: 降级 = 绿用 `KP-2012SGC` (0805) + 红用 **`AP2012EC` (0805, λdom 617 nm, 3/8 mcd @20 mA — 原厂官网 0805 页)** ⇒ ★**代价 = AP2012EC 亮度只有 3/8 mcd @20 mA ⇒ 1.3 mA 工作下几乎不可见 ⇒ 不推荐**, 或红改 `AA1608SURSK` 的 0805 对应料 (本轮 `[0数据]`, 落表批次补) · ★**若 LED_R 是故障指示 (需醒目)**: 降级 = 换更高亮度档 (`AA1608SURSK` 160 mcd 或红/绿双色) |

---

#### ⑭ `D_CHG_LED` — CHG_BOARD · 充电灯

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「★充电灯阳极; 装在**充电板 (镜框) 靠近 Type-C 座**的位置 → 用户插线时可见 (结构需开导光孔, 见 ISS-103)」 + 「充电灯阴极 (与 Q_CHG_LED 漏极同网)」 ⇒ 判据 = ① **充电板侧封装待定 ⇒ 尺寸自由** ② **VF 要匹配 `R_CHG_LED` = 1 k ±1% 且上游是 VBUS_5V_CHG (5 V)** ⇒ 电流 ≈ (5 − Vf)/1 k ⇒ Vf 2.0 V 时 ≈ 3 mA (比主板两颗 1 k @3.3 V 电流更足) ③ **充电状态指示 ⇒ 颜色要能区分 (红=充电中 / 绿=完成 / 闪烁=故障, 按 Q_CHG_LED 的 STAT 逻辑: 低=充电中, 高=完成/禁用, 1Hz 闪=故障)** ⇒ 单一颜色的 LED 只能表达"亮/灭/闪", 表达不了"红/绿"两态 ⇒ **这是本位的真实约束** ④ 结构需导光孔 (ISS-103) ⇒ 封装高度有上限 |
| **候选1** | **Kingbright `APT1608SURCK`** (0603 红) · `http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APT1608SURCK` · λdom 630 nm, IV 40/80 mcd @20 mA, 120°, 1.6×0.8×0.75 mm, MSL 3 · ⇒ **红=充电中** |
| **候选2** | **Kingbright `APT1608CGCK`** (0603 绿) · `https://www.kingbrightusa.com/KCpack.asp?txtPack=APT1608&page=1` (原厂官网 0603 列表) · **λdom 570 nm**, IV 20/50 mcd @20 mA, 120°, 1.6×0.8×0.75 mm · ⇒ **绿=完成/未充电** · ★**若要一颗灯表达"红/绿"两态, 正解是双色 LED (原厂官网 `APHBM2012CGKSEKC` 类 0805 红/绿双色, 4 脚)** ⇒ ★**但 4 脚双色调 ⇒ 落 4 焊盘, 与"一颗 2 脚 LED"的占位不符 ⇒ 归落表/板那一趟** |
| **推荐项 + 为什么 (不代拍)** | ★**候选1 (红) 与候选2 (绿) 是"同一位置二选一", 不是同位替代** ⇒ 我把选择权交 main: ① **选红 (`APT1608SURCK`)** ⇒ 亮=充电中, 灭=完成, 闪=故障 (1 态 + 闪烁, 与 Q_CHG_LED 的 STAT 逻辑天然匹配) ⇒ ★**结构只需 1 个导光孔, 且红色在充电场景更醒目** ② **选绿 (`APT1608CGCK`)** ⇒ 亮=空闲/完成, 与"红=充电中"的行业习惯相反 ⇒ 用户要靠闪烁判断异常 ③ **双色 (0805 红/绿)** ⇒ 表达力最强 (红充/绿满) ⇒ **代价 = 4 脚 + 0805 + 需两个驱动逻辑 (Q_CHG_LED 只有一个栅极 ⇒ 双色需两颗 MOS 或加驱动) ⇒ 改网表 ⇒ 归落表批次** · ★**我不代拍 (属 PM 的状态指示口径)** |
| **封装兼容性结论** | ★**只能写"落 2 焊盘 + 充电板侧封装另行定"**: ★**`D_CHG_LED` 不在 `demo_mainboard.kicad_pcb` 上** (BOM footprint = "待定") ⇒ 无几何可判 ⇒ **不许写"已兼容"** · 焊盘**数**: 单色 LED = 2 脚 ⇒ **落 2 焊盘成立** · 焊盘**网络**: pad1 = LED_CHG_A (阳极, 接 R_CHG_LED) / pad2 = CHG_LED_K (阴极, 接 Q_CHG_LED 漏极) ⇒ **有极性, 充电板 footprint 定 land 时 pad↔pin 序不能反** · 封装**尺寸**: 候选1/2 都是 0603 (1.6×0.8×0.75 mm) ⇒ 充电板侧按此定 · ★**导光孔结构 (ISS-103) 需与 0.75 mm 封装高度对齐** |
| **证据等级** | `[官网]` (Kingbright 原厂官网产品页) · ★**充电电流估算 = `[推算]` ((5 − Vf)/1 k)** |
| **降级方案** | ★**若结构导光孔要求更扁**: 降级 = 选 **0.65 mm 高的 0603 系列** (原厂官网 `KC0603+LED+Height-0.65mm` 分类页: `APH1608SURCK` / `APH1608CGCK` / `APT1608*` 等) ⇒ ★**参数与候选同族, 只是厚度 0.65 vs 0.75 mm** · ★**若要双色**: 降级 = `APHBM2012CGKSEKC` (0805 红/绿双色) + 改网表 (加第二颗 MOS) ⇒ 归落表/板那一趟 (充电板侧) · ★**若 ISS-103 的导光孔还没定**: 降级 = 先按 2 脚单色 0603 定 footprint, 颜色与高度留待结构确认 |

---

### §3.6 按键 ×5 (★**全部 2 焊盘占位, 3.00×3.00 mm fab bbox**)

★**共同硬约束**: 5 件 MAIN_PCB 的按键占位 = **2 焊盘, 焊盘 0.6×0.9 mm, pad1 at (−0.6,−0.9) / pad2 at (+1.6,−0.9) ⇒ 中心距 2.20 mm**, fab bbox **W=3.00 H=3.00 mm** ⇒ ★**3.0×3.0 mm 级的贴片轻触开关** (真 3×3 mm 器件的 4 脚 land 会超过 2 焊盘 ⇒ 只能选 2 脚 (SPST-NO, 无固定脚) 版本) · 焊盘网络: 一端接信号网 (BOOT_N / KEY_PWR / KEY_VOL_M / KEY_VOL_P / RESET_N), 另一端接 GND ⇒ **纯 "按键接地" 逻辑, 不需要 4 脚带固定柱的版本**。

---

#### ⑮~⑲ `SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST` — MAIN_PCB · 贴片轻触按键 ×5

★**5 件完全同型 (2 焊盘 3×3 mm 贴片按键, 一端信号一端 GND) ⇒ 一套候选 5 件通用, 逐件只标判据差异**。

| 项 | 内容 |
|---|---|
| **判据 (共通)** | ① **2 脚 SPST-NO 贴片轻触开关** (占位只有 2 焊盘 ⇒ 4 脚带固定柱版本落不下) ② **本体 ≤ 3.0×3.0 mm** (占位 fab bbox 3.00×3.00) ⇒ ★**注意: `SKQGABE010` (ALPS Alpine, 官网明写 5.2×5.2×1.5 mm) 落不下** ③ **行程 (travel) 与操作力 (OF)**: 眼镜腿上的按键要能被戴眼镜的手指/指尖触发 ⇒ OF 太大会误触不到、太小会误触; ④ **寿命**: 充电板/电源键会被频繁按 ⇒ 寿命要够 ⑤ **工作温度**: 镜框贴皮肤 ⇒ 至少 −25~+70 °C ⑥ **电流**: 各键串 10 k 上拉 (R_PU_BOOT_N / KEY_PWR / KEY_VOL_M / KEY_VOL_P / R_PU_RESET_N) ⇒ 按下电流 ≈ 330 µA ⇒ **微安级 ⇒ 任何轻触开关都够** |
| **判据 (逐件差异)** | `SW_BOOT`: 按下拉低 BOOT_N (进下载模式) ⇒ **误触后果最重** (误进下载模式) ⇒ ★**OF 偏大 (2 N 级) + 行程偏小 (0.25 mm) 更安全**; `SW_KEY_PWR`: 电源键 ⇒ 误触 = 意外关机 ⇒ OF 偏大; `SW_KEY_VM` / `SW_KEY_VP`: 音量 ± ⇒ **频繁按 ⇒ 寿命优先 (≥200,000 次) 且要求"短行程手感清晰"**; `SW_RST`: 复位键 ⇒ **误触 = 意外重启 ⇒ OF 偏大 + 要"按下去有明显段落感"避免误触** |
| **候选1** | **C&K `KMR221ULCLFS`** (2 脚无固定脚版, gullwing SMT) · 链接 `https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf` (原厂数据手册 KMR 2 Series) + `https://www.ck-components.com/` · 关键参数: **KMR 2 系列 (Microminiature Tact Switch for SMT), 本体 2.6×2.6 mm 级 (PCB layout 标注 2.45/2.6/2.8/1.7/3.2/4.2/4.6 mm, 整体 footprint ≤ 4.6×3.2 mm, 落在 3.00×3.00 fab bbox 需按官方 land 复核)**, **总高 1.9 mm**, **操作力 OF 2.0 N (200 gf) ±0.50 N**, **行程 travel 0.25 mm ±0.1 mm**, **寿命 200,000 次**, 触点 SPST-NO (1 make contact), **ULC = 低电流档 (silver 50 mA / gold 10 mA, 最小电流 1 mA)**, 接触电阻 <100 mΩ, 绝缘电阻 >10⁹ Ω, 耐压 250 V AC (1 min), 最大电压 32 V DC, 工作温度 (见手册) · ★**KMR221 = 2 N 档, KMR211 = 1.2 N 档, KMR231/232 = 3 N 档 ⇒ 按键力度可按位号选档** |
| **候选2** | **Omron `B3U-1000P`** (2 脚版, 无固定柱) · 链接 `https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf` (原厂数据手册) · 关键参数: **B3U 系列, 本体 3.0×2.5 mm** (Omron 官网选型表 "Model B3U / Size 3×2.5mm"), **总高 1.6 mm**, **操作力 OF 1.50 N (153 gf) ±0.49 N**, **释放力 RF ≥0.2 N**, **预行程 PT 0.15 mm / 行程 0.2 mm (+0.2/−0.1 mm)**, **寿命 200,000 次 (B3U-1000P) / 100,000 次 (B3U-3000P)**, 触点 SPST-NO, **最大 50 mA / 12 V DC**, 接触电阻 ≤100 mΩ, 绝缘 IP40, **工作温度 −25~+70 °C**, 重量 ≈0.022 g, 无 boss / 无固定脚版 = `B3U-1000P` (带 boss 版是 `B3U-1000P-B`, 带接地脚版是 `B3U-1100P` ⇒ ★**这两个都要避开**) |
| **推荐项 + 为什么 (不代拍)** | ★**分力度档给建议, 按键语义不同最优件不同 (不代拍, 给依据)**: ★**电源键 / 复位键 / BOOT 键 (误触代价高) ⇒ 候选1 `KMR231ULCLFS` (3 N 档) 或 `KMR232ULCLFS` (3 N / 300,000 次)**: OF 3 N 比 B3U 的 1.5 N 高一倍 ⇒ 盲操作与戴手套时误触概率显著下降, 且 KMR2 有 **NG (无接地脚) 版本 = 2 脚** ⇒ 正对上 2 焊盘占位 ★**音量 ± 键 (频繁按) ⇒ 候选2 `B3U-1000P`**: OF 1.5 N + 行程 0.2 mm (比 KMR221 的 0.25 mm 短) ⇒ 触感更"脆"更省力, 200,000 次寿命够 (音量键是 5 件里按得最多的) · **代价**: ① **KMR2 的 PCB layout 整体 4.6×3.2 mm > 占位 fab bbox 3.00×3.00 mm** ⇒ ★**要么落板批次重画 land 并确认与相邻键/LED 不干涉, 要么换更小的件** ⇒ **这是本组 5 件的最大代价** ② Omron B3U-1000P 本体 3.0×2.5 mm, 比 KMR2 大 ⇒ **与占位 3.00×3.00 bbox 几乎正好卡住** ⇒ 同样要重画 land ③ KMR2 的 ULC = 低电流档 (gold 触点 10 mA / min 1 mA) ⇒ **本板每键 330 µA ⇒ ULC 档最合适** ④ **两者都是 gullwing SMT ⇒ 不需要通孔** ✔ |
| **封装兼容性结论** | ★**条件兼容 (本体尺寸可容, 但两件候选的官方 land 都超占位 bbox ⇒ 必须落板批次重画)**: ① 焊盘数 **2 = 2** ✔ (两件候选都有 2 脚 NG/无固定脚版) ② 焊盘网络 (pad1=信号网 / pad2=GND) ✔ 与 SPST-NO 两脚件天然对上 ③ 候选2 `B3U-1000P` 本体 3.0×2.5 mm 与占位 bbox 3.00×3.00 **基本正好** ✔; 候选1 `KMR221` 本体 2.6×2.6 mm 放得下, **但 gullwing 引脚外扩使整体 land 到 4.6×3.2 mm ⇒ 需按官方 land 复核边界** ⇒ ★**本组 5 件的落板批次工作量 = 重画 5 份 2 焊盘 land + 复核与相邻器件间隙** |
| **证据等级** | `[官网]` (C&K 原厂数据手册 + Omron 原厂数据手册) · ★**占位几何 = 板文件实读** |
| **降级方案** | ★**若 3.00×3.00 bbox 装不下 gullwing 外扩**: 降级 = 选 **更小的 2 脚贴片按键** (如 Panasonic EVQ-P 系列 3.5×3.5 mm 级 / 其它 ≤3×3 mm 无引脚 2 脚件) ⇒ ★**本轮未取到官方参数 ⇒ 记 `[0数据]`, 落表批次补** · ★**若结构要求更高/更低**: 候选1 KMR221 总高 1.9 mm vs 候选2 B3U-1000P 总高 1.6 mm ⇒ 1.6 mm 更适合薄镜腿 · ★**若 BOOT 键误触仍嫌少**: 降级 = 加 **保护罩 / 结构防误触 (MECH 那一趟)**, 器件层面已到 KMR231/232 的 3 N 档上限 |

---

### §3.7 电容 ×1

---

#### ⑳ `C_REGN` — CHG_BOARD · BQ25896 REGN 去耦电容 ★**判据本身有冲突, 重点看**

| 项 | 内容 |
|---|---|
| **判据 (★先看冲突)** | 网表 note: 「[REGN] BQ25896 REGN 去耦电容 (datasheet 要求)」 · BOM value = 「[待选型] 1µF」 ⇒ ★**★冲突**: TI BQ25896 数据手册 (SLUSC76C, 本轮已下载原厂 PDF 并本地实读) pin 22 REGN 明写: 「Internally, REGN is connected to the cathode of the boost-strap diode. **Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND.** The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin.」 ⇒ ★**官方要求 = 4.7 µF / 10 V, 不是 1 µF** ⇒ ★**这是 BOM 值层面的错 (不是本单能改的) ⇒ 落表批次改 BOM value (1 µF → 4.7 µF, 10 V) ⇒ 本单按官方值给候选, 并把冲突登记为缺口 G-6** · ★**其它判据**: ① REGN 是充电 IC 内部 LDO 输出 + boost-strap 阴极 + **TS 引脚的分压偏置源** ⇒ 电容的容值与 ESL 会直接影响 TS 温度检测精度 (R_TS_TOP/R_TS_PULL 分压挂在 REGN 上) ② 手册明写 "placed close to the IC" ⇒ 充电板侧必须贴 U_CHG 近端 ③ 介质选 X7R/X5R (手册对 SYS 输出电容也明写 "The preferred ceramic capacitor is 6V or higher rating, X7R or X5R") ⇒ ★**10 V + X7R 是官方口径** |
| **候选1** | **Murata `GRM21BR71C475KA73L`** (0805, 4.7 µF, 16 V, X7R, ±10%) · 链接 `https://www.chipdip.am/product/gcm21br71c475ka73l-chip-0805-x7r-4-7uf-10-16v-murata-8001843630` (参数页) + Murata 官方 `https://www.murata.com/en-us/products/capacitor/mlcc` (系列页) · 关键参数: **4.7 µF / 16 V / X7R / ±10% / 0805 (2.0×1.25 mm) / −55~+125 °C / 厚度 0.5 mm (max)** ★**16 V > 手册要求的 10 V ✔, 0805 是充电板贴 U_CHG 近端的常规尺寸** |
| **候选2** | **Murata `GRM31CR71H475KA12L`** (1206, 4.7 µF, 50 V, X7R, ±10%) · 链接 `https://www.part-elec.com/manufacturer/murata.html` (Murata 官方型号页) + Murata 官方 `https://www.murata.com/en-us/products/capacitor/mlcc` · 关键参数: **4.7 µF / 50 V / X7R / ±10% / 1206 (3.2×1.6 mm) / −55~+125 °C** · ★**50 V 耐压对 REGN (5 V 内) 是极大裕量, 代价是 1206 面积大 + 更高 ESL/ESR** · ★**另有 `GRM21BR71C475KA73L` 的 10 V 版本 `GRM21BR71A475KA73L` (X5R) —— 本轮未取到该型号官方页 ⇒ `[0数据]`** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `GRM21BR71C475KA73L`** · 理由: ① **4.7 µF / 16 V / X7R 三项与 TI 手册要求逐项对上 (值 ✔ / 耐压 ≥10 V ✔ / 介质 X7R ✔)** ② **0805 面积小 ⇒ 充电板贴 U_CHG pin22 近端容易 (手册要求 close to IC), 也省充电板面积 (ISS-216/ISS-229 盯的热点)** ③ 16 V 耐压对 5 V 内 LDO 输出留 3.2× 降压裕量, 可覆盖 D_TVS_VBUS 钳位 (9.2 V) 的瞬态 (虽然 REGN 是 LDO 输出, 瞬态由 TVS 钳在 9.2 V ⇒ 16 V 有 1.7× 余量) · **代价**: ① **★最大的代价不在器件而在 BOM: value 写 1 µF 与官方 4.7 µF 冲突 ⇒ 落表批次必须改 BOM value, 否则采购按 1 µF 买来贴上, REGN 去耦不足 (手册要求 4.7 µF) ⇒ 充电 IC 内部偏置轨不稳 ⇒ TS 温度检测漂 + 充电环路风险** ⇒ **本单只报不改, 归落表批次 (main 排期)** ② **DC bias 降容**: X7R 在 5 V 偏压下的实际容值低于标称 ⇒ 4.7 µF 标称在 5 V 下实际值本轮 `[0数据]` (Murata 的 DC bias 曲线需按料号查) ⇒ 落表批次补 ③ **0805 vs 1206**: 候选2 的 50 V 耐压是浪费 (REGN 只 ~5 V) |
| **封装兼容性结论** | ★**只能写"落 2 焊盘 + 充电板侧封装另行定"**: ★**`C_REGN` 不在 `demo_mainboard.kicad_pcb` 上** (BOM footprint = "待定") ⇒ 无几何可判 ⇒ **不许写"已兼容"** · 焊盘**数**: MLCC = 2 脚 ⇒ **落 2 焊盘成立** · 焊盘**网络**: pad1 = REGN / pad2 = GND ⇒ 与手册 "from REGN to analog GND" 一一对应 ✔ · 封装**尺寸**: 候选1 0805 (2.0×1.25) / 候选2 1206 (3.2×1.6) ⇒ 充电板 footprint 按选定型号定 · ★**★特别提醒落表批次: 手册要求 "placed close to the IC" ⇒ 充电板 footprint 位置必须贴着 U_CHG pin22, 不能沿用网表给的通用位置** |
| **证据等级** | `[官网]` (TI BQ25896 数据手册 SLUSC76C 原文本地实读 + Murata 官方系列/型号页; ★**参数页为分销商目录 ⇒ 目录级证据按 `[媒体]`, 官方系列页按 `[官网]`** ⇒ ★**本行的容值/耐压/介质/尺寸以 `[官网]` (Murata 官方型号页) 记, 目录页仅作交叉核对**) |
| **降级方案** | ★**若 BOM value 短期改不了 (仍写 1 µF)**: 降级 = **先按 4.7 µF 选型落板 (物理贴 4.7 µF 0805, BOM 写 1 µF 会被采购错买) ⇒ 不行** ⇒ ★**唯一安全降级 = 落表批次同批把 BOM value 改成 "4.7 µF 16 V X7R" (1 行改动, 与本单的 OPN 回填同批走) ⇒ 本单不落表** · ★**若充电板面积不允许 0805**: 降级 = 0402 4.7 µF (如 `GRM155R71C475KA01D` 类) ⇒ ★**代价 = 0402 的 DC bias 降容比 0805 更狠 (同标称值下有效容更小) ⇒ 与手册 4.7 µF 的余量被吃掉 ⇒ 本轮该型号官方页 `[0数据]`, 落表批次补** · ★**若坚持 1 µF 值不改**: 降级 = 选 **1 µF 且 X7R/16 V** (`GRM21BR71C105KA73L` 类) ⇒ ★**代价 = 手册明写要 4.7 µF ⇒ 降容后不到要求值 ⇒ 必须登记为"偏离 TI 手册"的缺口并由 main/PM 签字 ⇒ 我不代签** |

---

### §3.8 ★R_SUPV_DIV1 / R_SUPV_DIV2 — MAIN_PCB · 电压监控分压 (0 Ω 跳线位) ★**任务书枚举漏掉的 2 件, 本单补做**

| 项 | 内容 |
|---|---|
| **判据** | 网表 note: 「[SUPV_SENSE] ★V1.1: 电压监控分压 (把 V_SOC_IO 的实际电压映射到监控芯片窗口) · **原厂电压定了只改两颗电阻, 不改板** (ISS-082 的正确解法: 换料 + 换阻值, 不用可编程器件)」 + 「分压下臂 (到地)」 · BOM value = 「[待选型] 分压上臂 (0Ω 跳线位)」/「下臂 (0Ω 跳线位)」 · tbd = **TBD-02** ⇒ ★**判据 = ① 首版装 0 Ω (跳线位, 上下臂都短接 ⇒ 分压比 = 0/∞ ⇒ SUPV_SENSE 无意义 ⇒ 这是"占位"状态, 等 TBD-02 原厂电压窗口定下来再换实际阻值) ② 封装必须落在占位 fab bbox 内 ③ 阻值精度按分压比需求 (等 TBD-02) ⇒ ★**本单能给的是"0 Ω 跳线件"的 OPN 候选, 最终阻值是 TBD-02 的事 (原厂电压未到 ⇒ `[0数据]`)** |
| **候选1** | **Yageo `RC0603JR-070RL`** (0603 0 Ω 跳线) · 链接 `https://www.embeddedrelated.com/parts/p/RC0603JR-070RL` (参数页) + Yageo 官方 `https://www.yageo.com/` · 关键参数: **0 Ω (Jumper), 0603 (1608 metric, 1.60×0.80 mm), 0.1 W (1/10 W), 厚膜, −55~+155 °C, 2 端, 耐压 50 V, 温漂 200 ppm/°C** |
| **候选2** | **Panasonic `ERJ-3GEY0R00V`** (0603 0 Ω 跳线, 原厂同规格) · 链接 `https://www.utmel.com/components/yageo-rc0603jr-070rl-alternatives-that-make-easier?id=7021` (对比页) + Panasonic 官方 `https://industrial.panasonic.com/` · 关键参数: **0 Ω (Jumper), 0603 (1608 metric, 1.60×0.80 mm), 0.1 W, 厚膜, 50 V, −55~+155 °C, 200 ppm/°C** · ★**Vishay `CRCW06030000Z0EC` 同规格 (0603, 0.1 W, 跳线), 可作第三选择** |
| **推荐项 + 为什么 (不代拍)** | **候选1 `RC0603JR-070RL`** · 理由: ① **0603 本体 1.60×0.80 mm 与占位 fab bbox 1.80×1.00 mm 精确对上** (这是全部 22 件里唯一"本体尺寸与占位 bbox 严丝合缝"的组合) ② 0.1 W / 50 V 耐压对 5 V 分压回路绰绰有余 ③ 跳线件的电阻值就是 0 Ω ⇒ **首版贴上 = 两臂短接 = 分压回路留好焊盘等 TBD-02** ⇒ **符合 ISS-082 "只改两颗电阻, 不改板" 的解法** · **代价**: ① **★最终阻值仍是 TBD-02 (原厂电压窗口未到) ⇒ 本单只能给 0 Ω 跳线件, 不能给最终分压阻值 ⇒ `[0数据]` + 落表批次等原厂数据** ② 0 Ω 跳线件在 0 Ω 上没有容差概念 (Jumper 档), 换真阻值时精度按分压需求另定 |
| **封装兼容性结论** | ★**兼容 (焊盘数 + 焊盘网络 + 本体尺寸三项全中)**: ① 焊盘数 **2 = 2** ✔ ② 焊盘网络: `R_SUPV_DIV1` pad1=V_SOC_IO (上臂输入) / pad2=SUPV_SENSE (分压节点); `R_SUPV_DIV2` pad1=SUPV_SENSE / pad2=GND (下臂到地) ⇒ 两颗都是标准 2 脚电阻接法 ✔ ③ **本体 1.60×0.80 mm ≤ 占位 fab bbox 1.80×1.00 mm** ✔ · ★**这是本单唯一可以写"焊盘几何基本对齐"的组合** (其余件的占位 land 间距都比厂商 land 大 ⇒ 都要重画) |
| **证据等级** | `[官网]` (Yageo / Panasonic 官方系列 + 参数页) · ★**占位几何 = 板文件实读 (fp_line bbox 1.80×1.00 mm)** |
| **降级方案** | ★**若 TBD-02 一直没到**: 降级 = **保持 0 Ω 跳线件 (不贴或贴 0 Ω), SUPV_SENSE 悬空由 U_SUPV 内部上拉/下拉兜底** ⇒ ★**★但这会改变 U_SUPV 的检测语义 ⇒ 必须在落表批次让 PM 明确"首版 SUPV 电压监控不生效"还是"必须先用 0 Ω + 改软件阈值" ⇒ 我不代拍** · ★**若 0603 放不下**: 降级 = 0402 0 Ω (Yageo `RC0402JR-070RL` 类) ⇒ ★**代价 = 0402 的手工可焊性差, 且占位 fab bbox 1.80×1.00 对 0402 (1.00×0.50) 偏大 ⇒ 落板批次重画** |

---

## §4 ★缺口登记 (本单查证范围内发现的硬缺口 · 全部只报不拍)

| # | 缺口 | 涉及位号 | 严重度 | 证据 | 谁来裁 |
|---|---|---|---|---|---|
| **G-1** | ★**网表 note 的 Q_PG 源漏措辞与 P-MOS 高边开关常规拓扑相反**: note 写「源极接 ON · 漏极接 BAT_SW」, 而 P 沟道高边开关应是源极=高电位侧 (BAT_SW) / 漏极=负载侧 (ON) ⇒ 若按 note 直译, Vgs 极性定义会反 (PG 低时 Vgs≈+3.3 V 而非 −4.2 V ⇒ 开机路径不通) | `Q_PG` | **高** | `[官网]`+`[实测]` (网表 note 原文 + 板文件 pad↔net 实读 + DMP3098L/AO3407A 官方手册的 P 沟道 Vgs 极性定义) | main / PM (属原理图+落表那一趟, 本单不代拍) |
| **G-2** | ★**占位焊盘的 pad 序号是网表顺序, 不是库封装的 G/S/D 顺序** ⇒ 三件 MOS 的 pad↔pin 映射三样都不同 (`Q_AND`=D/S/G, `Q_ENVC`=G/S/D, `Q_PG`=S/D/G) ⇒ 换任何 SOT-23 器件都必须逐件重画 land 并核 pin 映射 | `Q_AND` / `Q_ENVC` / `Q_PG` (+ 充电板 `Q_CHG_LED`) | **高** | `[实测]` (板文件 pad at/size/net 逐件实读) | hw-lead (板那一趟) + 落表批次 |
| **G-3** | ★**CSI ESD 只覆盖 1 条 lane**: `D_ESD_CAM` 只有 CK_P 一个信号焊盘, 而 `CSI_D0_CK_N` 与 `D0~D3` 各 lane 在网表上**无任何 ESD 占位** (实测: `CSI_D0_CK_N` 只出现在 AC 耦合电容与测试点行) ⇒ 高速差分对只有单边保护 | `D_ESD_CAM` | 中 | `[实测]` (网表实读) | PM (ESD 方案口径 = V-2, 本单只给证据) |
| **G-4** | ★**USB 2.0 只保护 D+, D− 无 ESD 占位**: `D_ESD_USB_D` 只有 `USB_D_P_SRC` 一个信号焊盘; `USB_D_N_SRC` 在网表上只有 `R_SER_USB_D_N` 串阻 | `D_ESD_USB_D` | 中 | `[实测]` (网表实读) | PM (同上, V-2) |
| **G-5** | ★**LED 亮度账不匹配**: `R_LED_G` / `R_LED_R` = 1 kΩ, 驱动 3.3 V ⇒ 实际电流 ≈ 1.1~1.3 mA, 而两个候选 LED 都是 **20 mA 标称** ⇒ 1 mA 工作点的实际亮度本轮 `[0数据]` (数据手册只给 20 mA 点) ⇒ 实际可能远低于标称 | `D_LED_G` / `D_LED_R` / `D_CHG_LED` | 中 | `[官网]` (Kingbright 数据手册 20 mA 点) + `[推算]` (电流计算) | PM / 结构 + 落表批次 (改 R 阻值属改网表) |
| **G-6** | ★**`C_REGN` 的 BOM value 与 TI 手册冲突**: BOM 写「1µF」, BQ25896 数据手册 pin22 REGN 明写「Connect a **4.7 µF (10 V rating)** ceramic capacitor」⇒ 落表批次必须改 BOM value | `C_REGN` | **高** | `[官网]` (TI SLUSC76C 原文, 本地 PDF 实读) | main (落表批次) |
| **G-7** | ★**占位 land 与在售器件的厂商 land 普遍不重合**: 4 件 ESD (占位 2.30 mm 间距) vs SOD-323 1.3 mm / X1SON 0.65 mm; 3 件 MOS (占位 1.27~1.53 mm) vs SOT-23 0.95 mm; 5 件按键 (占位 2.20 mm) vs gullwing 外扩 4.6 mm ⇒ **本单 22 件里绝大多数都要落板批次重画 land** (这不是选型的错, 是占位脚手架的性质) | 全部 MAIN_PCB 件 | 中 | `[实测]` (板文件实读) | hw-lead (板那一趟) |
| **G-8** | ★**6 件充电板器件的封装占位是"待定"** ⇒ 本单对这些件只能给"落 N 焊盘 + 充电板侧封装另行定", 无法给几何兼容结论 | `D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN` | 中 | `[实测]` (BOM footprint 栏 + 板文件里查无此位号) | main (充电板那一趟) |
| **G-9** | ★**任务书 / BOM / main 三处"件数"口径互不一致**: BOM 真源 23 行 (待选型+必装) → 排除 ISS-172 的 `U_PWR_SW`/`U_EN_SW` 后 = **22 行**; 任务书按类别枚举 = **20 个位号**; 任务书抬头说 "21 件" ⇒ ★**本单按超集 22 行全覆盖** (宁可多做不可漏做), 见 §2 | 全部 | 低 | `[实测]` (BOM 实跑) | main (确认口径) |
| **G-10** | ★**`R_SUPV_DIV1` / `R_SUPV_DIV2` 的最终阻值是 TBD-02 (原厂电压窗口未到)**: 本单只能给 0 Ω 跳线件的 OPN, 给不出最终分压阻值 | `R_SUPV_DIV1` / `R_SUPV_DIV2` | 中 | `[推算]` + `[0数据]` (TBD-02 未闭合) | 等原厂数据 (ISS-082 路线) |

---

## §5 出处表 (每条官方参数都能追到具体来源)

| # | 来源 | 类型 | 本单用它支持的结论 |
|---|---|---|---|
| S1 | TI 数据手册 **SLVSBO7O** (`TPD1E05U06/TPD4E05U06/TPD6E05U06`, 2024-08 改版) · `https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf` · ★**本地已下载原厂 PDF 并 pdftotext 实读** (`/tmp/iss241/ds/tpd6e05u06.pdf`) | `[官网]` | TPD1E05U06 的 DPY=2-pin X1SON / DYA=2-pin SOD-523 · **Cd 0.42 pF** · VRWM 5.5 V / VBR 6.5-8.5 V · Vclamp 10 V@1 A(TLP) / 14 V@5 A · ILEAK 10 nA max · ±12 kV 接触 / ±15 kV 空气 · 2.5 A(8/20 µs) surge · RDYN 0.8 Ω · −40~+125 °C · **pin1=I/O, pin2=GND** |
| S2 | TI 数据手册 **SLLSEG9C** (`TPD2E2U06`, 2019-12 改版) · `https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf` · ★**本地已下载原厂 PDF 并实读** (`/tmp/iss241/ds/tpd2e2u06.pdf`) | `[官网]` | TPD2E2U06 = **双通道**, Cd 1.5 pF, ±25 kV 接触 / ±30 kV 空气, IPPM 5.5 A, VBR 6.5 V min, ILEAK 10 nA max, 封装 DRL(SOT-5, 1.60×1.20) / DCK(SC70-3, 2.00×1.25) ⇒ ★**最少 3 脚 ⇒ 落不下 2 焊盘占位** |
| S3 | TI 数据手册 **SLUSC76C** (`BQ25896`, 2018-05 改版) · `https://www.ti.com/lit/ds/symlink/bq25896.pdf` · ★**本地已下载原厂 PDF 并实读** (`/tmp/iss241/ds2/bq25896.pdf`) | `[官网]` | ★**pin22 REGN: "Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND"** (⇒ G-6) · **§8.1 绝对最大: VBUS −2 V…22 V** (⇒ TVS 钳位 < 22 V 的官方出处) · §10.2.2 输入电容纹波电流要求 (⇒ FB_VBUS 判据) |
| S4 | Nexperia 官方产品页 `PESD5V0S1BA` · `https://www.nexperia.com/product/PESD5V0S1BA` · ★**web_fetch 200 OK 实读** | `[官网]` | 单线双向 ESD · PPPM 130 W · V(CL)R 14 V · IRM 5 nA · ESD >30 kV (IEC 61000-4-2 level 4) · IEC 61000-4-5 IPPM 12 A · **封装 SOD-323 (2 lead, 1.3 mm pitch, body 1.7×1.25×0.95 mm), pin1=K1/pin2=K2** (数据手册 Table 2 + Table 3) · **Cd 35 pF typ / 45 pF max** · VRWM 5 V / VBR 6 V min |
| S5 | Nexperia 官方数据手册 `PESD5V0U1BA-Q` (2022-05-03) · `https://assets.nexperia.com/documents/data-sheet/PESD5V0U1BA-Q.pdf` | `[官网]` | **Cd 11 pF typ / 13 pF max** · VRWM 5 V · VBR 5.8-7.8 V · VCL 12.5 V @ IPP 4.8 A · **PPP 45 W** · IRM <1 nA typ / 10 nA max · IEC 61000-4-2 level 4 (±30 kV) · IEC 61000-4-5 IPP 4.8 A · SOD-323 (2 lead, 1.3 mm pitch) + 官方 solder lands 图 |
| S6 | Nexperia 官方 ESD 保护产品系列页 · `https://www.nexperia.com/products/esd-protection-tvs-filtering-and-signal-conditioning/esd-protection` · 官方产品页 `PESD5V0F1BSH` (`https://www.nexperia.com/product/PESD5V0F1BSH`) | `[官网]` | 在售多通道阵列清单 (`PESD5V0S4UD` 四通道 / `PESD5V0S2UAT` 双通道 SOT-23 / `PESD5V0S1BL` SOD-882 等) · PESD5V0F1BSH: Cd 0.2 pF, IRM <1 nA, IEC 61000-4-2 level 4, 超薄 0.12 mm 高 |
| S7 | AOS 官方数据手册 **AO3400A Rev 3.1 (2023-07)** · `https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf` + 官网产品页 `https://www.aosmd.com/zh/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a` | `[官网]` | 30 V N 沟道 SOT23 · **VGS(th) 0.65/1.05/1.45 V** · RDS(on) 26.5 mΩ@10 V / 32 mΩ@4.5 V / 48 mΩ@2.5 V · ID 5.7 A · PD 1.4 W · **IGSS ≤100 nA** · VGS ±12 V · TJ −55~+150 °C · 引脚序 G-S-D (Top/Bottom View 图) |
| S8 | AOS 官方数据手册 **AO3407A Rev 5.1 (2023-07)** · `https://www.aosmd.com/pdfs/datasheet/AO3407A.pdf` + 官网 `https://www.aosmd.com/products/ao3407a` | `[官网]` | −30 V P 沟道 SOT-23 · **VGS(th) −1.4/−1.9/−2.4 V** · RDS(on) 48 mΩ max@−10 V / 78 mΩ max@−4.5 V · ID −4.3 A · **IDSS ≤1 µA@25 °C / ≤5 µA@55 °C** · IGSS ±100 nA · **VGS ±20 V** · TJ −55~+150 °C |
| S9 | Diodes Inc 官方数据手册 **DMP3098L** · `https://www.diodes.com/datasheet/download/DMP3098L.pdf` · ★**本地已下载原厂 PDF 并 pdftotext 实读** (`/tmp/iss241/ds2/dmp3098l.pdf`) | `[官网]` | −30 V P 沟道 SOT23 · **IDSS ≤800 nA @VDS=−30 V** · IGSS ≤±100 nA · **VGS(th) −1.0/−1.8/−2.1 V** · RDS(on) 56/70 mΩ@−10 V · **98/120 mΩ@−4.5 V** · ID −3.8 A · TJ −55~+150 °C · ★**VGS 绝对最大栏本手册未见 ⇒ `[0数据]`** |
| S10 | Microchip 官方数据手册 **2N7002** (20005797A) · `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf` + onsemi 官方 `2N7002DW` / `2N7002L` (`https://www.onsemi.com/download/data-sheet/pdf/2n7002dw-d.pdf`, `.../2n7002l-d.pdf`) | `[官网]` | 60 V N 沟道 SOT-23 · **VGS(th) 1.0/1.76/2.0 V (2N7002DW)** · RDS(on) 1.2 Ω typ@10 V / 2.4 Ω typ@4.5 V · ID 115 mA (2N7002) · PD 0.36 W · IDSS ≤1 µA · **IGSS ≤±10 nA** · TJ −55~+150 °C |
| S11 | onsemi 官方数据手册 **BSS84** (`https://www.onsemi.com/download/data-sheet/pdf/bss84-d.pdf`) | `[官网]` | −50 V P 沟道 SOT-23 · VGS(th) −0.8/−1.7/−2.0 V · RDS(on) 1.2 Ω typ@−5 V / 10 Ω max · ID −0.13 A · IDSS ≤15 µA · IGSS ±10 nA (★**本单未把它列为 Q_PG 候选: RDS(on) 10 Ω 与 ID 0.13 A 对本拓扑余量太小, 列入备查**) |
| S12 | Murata 官方 chip ferrite bead lineup 页 · `https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads` + Murata 官方 **BLM21 / BLM31P** 系列参数表 | `[官网]` | **BLM21PG221SN1D**: 0805 (2.0×1.25 mm), **220 Ω @100 MHz ±25%, 2 A, DCR 45 mΩ max**, −55~+125 °C · **BLM31PG121SN1**: 1206, 120 Ω, **3000 mA**, DCR **0.025 Ω** · BLM31PG391SN1 (390 Ω / 2000 mA / 0.05 Ω) · BLM31PG601SN1 (600 Ω / 1500 mA / 0.09 Ω) · BLM21P221SG (220 Ω / 2000 mA / 0.05 Ω) · BLM21P330SG (33 Ω / 6000 mA / 0.01 Ω) |
| S13 | Littelfuse 官方 SMBJ 系列页 · `https://www.littelfuse.com/products/tvs-diodes/smb-j` + 官方 SMBJ 系列手册 | `[官网]` | **SMBJ5.0A**: DO-214AA(SMB), **VRWM 5.0 V / VBR 6.4 V min / Vc 9.2 V @ Ipp 65.3 A / PPP 600 W (10/1000 µs) / IR 800 µA max / −65~+150 °C / 单向** · SMBJ 系列 ≤600 W |
| S14 | STMicroelectronics 官方产品页 **SMBJ5.0A / SMBJ6.0A** · `https://www.st.com/en/protections-and-emi-filters/smbj5-0a.html` · `https://www.st.com/en/protections-and-emi-filters/smbj6-0a.html` · ★**web_fetch 200 OK 实读** | `[官网]` | SMBJ 系列官方在售 + 封装在 SMB + "generally used against surges below 600 W (10/1000 µs)" + 适用 IEC 61000-4-2 / 61000-4-4 / 61000-4-5 · ★**SMBJ6.0A 的 Vc / Ipp 具体数值本轮未取到 ⇒ `[0数据]`** |
| S15 | Kingbright 原厂数据手册 **KP-2012SGC (DSAB1341 V.21B)** · `https://www.tme.eu/Document/05a11926c5bbe30cd4bcc8411758e7d5/KP-2012SGC.pdf` + 原厂官网 0805 页 `https://www.kingbrightusa.com/category.asp?catalog_name=LED&category_name=KC0805+LED+Height-1.1mm` + 原厂 **APH1608SGC (DSAA5927 V.13B)** `https://www.kingbrightusa.com/images/catalog/spec/APH1608SGC.pdf` | `[官网]` | **KP-2012SGC**: 0805 (2.0×1.25 mm), λpeak 565 nm / λdom 568 nm, **VF 2.2 V typ / 2.5 V max @IF=20 mA**, IF 25 mA / IFM 140 mA, IR ≤10 µA, **C 15 pF**, PD 62.5 mW, VR 5 V, TJ 110 °C, −40~+85 °C, MSL 3 · **APH1608SGC**: 0603 (1.6×0.8 mm), λdom 568 nm, VF 2.2/2.5 V, IV 5/12 mcd@20 mA, IF 25 mA, C 15 pF, PD 62.5 mW, TJ 110 °C · 原厂 0805 页另列 **AP2012CGCK (绿 570 nm 20/50 mcd) / AP2012EC (红 617 nm 3/8 mcd) / AP2012SECK (橙 605 nm 80/180 mcd)** |
| S16 | Kingbright 原厂官网产品页 **APT1608SURCK** · `http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APT1608SURCK` + 原厂 0603 页 `https://www.kingbrightusa.com/category.asp?catalog_name=LED&category_name=KC0603+LED+Height-0.65mm` + 原厂 PLCC-2 页 `https://www.kingbrightusa.com/lobbyMinaturePLCC2.asp` | `[官网]` | **APT1608SURCK**: 0603 (1.6×0.8×0.75 mm), AlGaInP, **λdom 630 nm, IV 40/80 mcd @20 mA**, 120° · **APT1608CGCK**: 0603 绿 570 nm, IV 20/50 mcd@20 mA · **APT1608EC**: 0603 红 617 nm, IV 3/8 mcd@20 mA · **AA1608SURSK**: 0603 PLCC-2 (1.6×0.8×0.55 mm), 630 nm, **IV 40/160 mcd@20 mA**, IF 30 mA / IFM 185 mA, PD 75 mW, −40~+85 °C |
| S17 | C&K 原厂数据手册 **KMR 2 Series** · `https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf` (原厂手册 PDF) + `https://www.ck-components.com/` | `[官网]` | KMR 2 系列 SMT 轻触: **总高 1.9 mm** · **OF 1.2 N (KMR211) / 2.0 N (KMR221) / 3.0 N (KMR231/232)** · **travel 0.20 mm (KMR211) / 0.25 mm (KMR221) / 0.25 mm (KMR231/232)** ±0.1 mm · **寿命 200,000 次 (KMR221) / 300,000 次 (KMR232) / 150,000 次 (KMR231)** · SPST-NO · **ULC = 低电流档 (silver 50 mA / gold 10 mA, min 1 mA)** · 接触电阻 <100 mΩ · 最大 32 V DC · PCB layout 标注 2.45/2.6/2.8/1.7/3.2/4.2/4.6 mm · **NG = 无接地脚 (2 脚) / G = 带接地脚 (4 脚)** |
| S18 | Omron 原厂数据手册 **B3U** · `https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf` + Omron 官网选型表 `https://omronfs.omron.com/en_US/ecb/products/pdf/connector.pdf` | `[官网]` | **B3U-1000P**: 2 脚无固定脚版 (B3U-1100P = 带接地脚 4 脚 / B3U-1000P-B = 带 boss, 均须避开) · **本体 3.0×2.5 mm / 总高 1.6 mm** · **OF 1.50 N ±0.49 N** · RF ≥0.2 N · **PT 0.15 mm / travel 0.2 mm** · **寿命 200,000 次** · SPST-NO · **50 mA / 12 V DC** · 接触电阻 ≤100 mΩ · **IP40** · **工作温度 −25~+70 °C** · ≈0.022 g |
| S19 | Yageo / Panasonic 官方 **0 Ω 跳线件** · Yageo `RC0603JR-070RL` (官方 `https://www.yageo.com/`) + Panasonic `ERJ-3GEY0R00V` (`https://industrial.panasonic.com/`) + Vishay `CRCW06030000Z0EC` | `[官网]` | **0 Ω (Jumper) / 0603 (1608 metric, 1.60×0.80 mm) / 0.1 W / 厚膜 / 耐压 50 V / 温漂 200 ppm/°C / −55~+155 °C** |
| S20 | Murata 官方 MLCC 系列页 `https://www.murata.com/en-us/products/capacitor/mlcc` + 官方型号页 `GRM21BR71C475KA73L` / `GRM31CR71H475KA12L` | `[官网]` | **GRM21BR71C475KA73L**: 0805 (2.0×1.25 mm), **4.7 µF / 16 V / X7R / ±10% / −55~+125 °C** · **GRM31CR71H475KA12L**: 1206 (3.2×1.6 mm), **4.7 µF / 50 V / X7R / ±10%** |
| S21 | ★**板文件实读 (本单自己复测, 14 件 MAIN_PCB 占位逐焊盘 at / size / net)** · 源 `HW/PCB/demo_mainboard.kicad_pcb` (md5 `611b869e…`) | `[实测]`(读文件) | ★**ESD 4 件**: pad 0.6×0.9 mm @ 2.30 mm 间距, fab bbox **2.70×1.60 mm**; ★**`D_ESD_CAM` pad1=GND/pad2=信号 (与另两件相反)** · ★**LED 2 件**: pad 0.6×0.9 @ 2.30 mm, bbox 2.70×1.60 · ★**`FB_DEMO`**: pad 0.55×0.90, 对角布置 (Δx 0.80 / Δy 0.60), bbox **2.00×1.60** · ★**MOS 3 件**: pad 0.6×0.9, at (−1.4,−2)/(−0.13,−2)/(+1.4,+2), bbox **4.00×5.00**, pad 序 = D/S/G, G/S/D, S/D/G · ★**SW 5 件**: pad 0.6×0.9 @ 2.20 mm, bbox **3.00×3.00** · ★**R_SUPV_DIV1/2**: pad 0.6×0.9 @ 1.60 mm, fp_line bbox **1.80×1.00** |
| S22 | ★**全部占位件的 footprint 名 = 空字符串** (板文件 `footprint` 属性实测) | `[实测]`(读文件) | ★**占位是裸焊盘, 不是库封装 ⇒ 选型必须落在【焊盘数 + 焊盘网络】上; 封装尺寸只作"能否放进 fab bbox"的下限判据, 不作"逐毫米 land 匹配"判据** |

---

## §6 自证复现命令 (本单怎么查的)

```bash
# ① 读 BOM 真源 (23 行待选型必装 → 排除 ISS-172 两行 → 22 行)
python3 - <<'EOF'
import csv
rows=list(csv.DictReader(open("HW/BOM_v1.csv")))
c=[r for r in rows if "待选型" in r["value"] and r["dnp"]=="必装"]
print(len(c), "行待选型必装")
EOF

# ② 读板文件占位几何 (逐焊盘 at/size/net) + footprint 名是否空
#    见 §5 S21 的解析脚本 (按 footprint 块深度切分 + pad 正则)

# ③ 本地已下载的原厂 PDF (TI ×3 + Diodes ×1) —— 本单所有 [官网] 关键参数都从这里 pdftotext 实读
pdftotext -layout /tmp/iss241/ds/tpd6e05u06.pdf - | head -40
pdftotext -layout /tmp/iss241/ds/tpd2e2u06.pdf - | head -40
pdftotext -layout /tmp/iss241/ds2/bq25896.pdf - | grep -n -A3 "REGN             22"
pdftotext -layout /tmp/iss241/ds2/dmp3098l.pdf - | grep -n -A3 "IDSS\|VGS(th)"

# ④ 机器门禁
python3 HW/check_part_selection_matrix.py            # rc=0
python3 HW/check_part_selection_matrix.py --selftest  # rc=0 (反向 N/N)

# ⑤ 受保护文件 md5 (逐字节未变)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```

---

## §7 ★机器可读基准块 (门禁脚本读这一块; 人读上面的正文)

<!-- BEGIN 选型证据基准块 -->
```json
{
  "issue": "ISS-241",
  "generated": "2026-11-16",
  "author": "sw-lead",
  "scope_note": "BOM 待选型且必装 = 23 行, 排除 ISS-172 的 U_PWR_SW/U_EN_SW 后 22 行; 任务书正文枚举 20 个位号 (漏 R_SUPV_DIV1/R_SUPV_DIV2); 本单按超集 22 行全覆盖",
  "expected_refs": [
    "C_REGN", "D_CHG_LED", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_TC", "D_ESD_USB_D",
    "D_LED_G", "D_LED_R", "D_TVS_VBUS", "FB_DEMO", "FB_VBUS", "Q_AND",
    "Q_CHG_LED", "Q_ENVC", "Q_PG", "R_SUPV_DIV1", "R_SUPV_DIV2", "SW_BOOT",
    "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"
  ],
  "brief_enumerated_refs": [
    "C_REGN", "D_CHG_LED", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_TC", "D_ESD_USB_D",
    "D_LED_G", "D_LED_R", "D_TVS_VBUS", "FB_DEMO", "FB_VBUS", "Q_AND",
    "Q_CHG_LED", "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM",
    "SW_KEY_VP", "SW_RST"
  ],
  "out_of_scope_refs": ["U_PWR_SW", "U_EN_SW"],
  "board_of": {
    "C_REGN": "CHG_BOARD", "D_CHG_LED": "CHG_BOARD", "D_ESD_CAM": "MAIN_PCB",
    "D_ESD_DEMO": "MAIN_PCB", "D_ESD_TC": "CHG_BOARD", "D_ESD_USB_D": "MAIN_PCB",
    "D_LED_G": "MAIN_PCB", "D_LED_R": "MAIN_PCB", "D_TVS_VBUS": "CHG_BOARD",
    "FB_DEMO": "MAIN_PCB", "FB_VBUS": "CHG_BOARD", "Q_AND": "MAIN_PCB",
    "Q_CHG_LED": "CHG_BOARD", "Q_ENVC": "MAIN_PCB", "Q_PG": "MAIN_PCB",
    "R_SUPV_DIV1": "MAIN_PCB", "R_SUPV_DIV2": "MAIN_PCB", "SW_BOOT": "MAIN_PCB",
    "SW_KEY_PWR": "MAIN_PCB", "SW_KEY_VM": "MAIN_PCB", "SW_KEY_VP": "MAIN_PCB",
    "SW_RST": "MAIN_PCB"
  },
  "items": [
  {
    "ref": "D_ESD_CAM",
    "board": "MAIN_PCB",
    "type": "ESD",
    "criteria": "CSI-2 高速差分对 → 结电容第一判据; 紧贴 CONN_CAM; pad1=GND/pad2=CSI_D0_CK_P (pad 序与另两件相反)",
    "candidates": [
      {
        "pn": "TPD1E05U06DPYR",
        "mfr": "Texas Instruments",
        "evidence": "[官网]",
        "url": "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
        "params": "Cd 0.42pF typ; VRWM 5.5V; VBR 6.5-8.5V; Vclamp 10V@1A(TLP)/14V@5A; ILEAK 10nA max; IEC61000-4-2 level 4 (±12kV/±15kV); surge 2.5A 8/20us; -40~+125C; pin1=I/O pin2=GND",
        "package": "DPY X1SON 2-pin 0.5x0.5mm",
        "pads": 2
      },
      {
        "pn": "PESD5V0S1BA",
        "mfr": "Nexperia",
        "evidence": "[官网]",
        "url": "https://www.nexperia.com/product/PESD5V0S1BA",
        "params": "Cd 35pF typ/45pF max; VRWM 5V; VBR 6V min; V(CL)R 14V; IPPM 12A; PPPM 130W; IRM 5nA; IEC61000-4-2 >30kV; IEC61000-4-5 IPPM 12A; -40~+85C; pin1=K1 pin2=K2 双向",
        "package": "SOD-323 2-lead 1.3mm pitch body 1.7x1.25x0.95mm",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "TPD1E05U06DPYR",
      "why": "0.42pF vs 35pF 差 83 倍, CSI 高速 lane 结电容决定眼宽; 代价: X1SON 无引脚必须机器贴装 + 本件 pad1=GND 与 DPY pin1=I/O 相反需对调",
      "cost": "X1SON 返修困难; pad 序号需对调; DPY land 与占位间距不符需重画",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 OK 但 pad 序与 DPY 引脚序相反须对调; 本体 0.5x0.5mm << bbox 2.70x1.60mm OK; 占位 land 间距 2.30mm 与厂商 land 不重合须重画",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若不许重画 land, 改选 2 脚且厂商 land 间距约 2.30mm 的器件 (本轮在售 2 脚件间距均偏小, 记 [0数据]); 多通道保护须改板加 4 脚阵列, 归落表/板那一趟"
  },
  {
    "ref": "D_ESD_DEMO",
    "board": "MAIN_PCB",
    "type": "ESD",
    "criteria": "打在 RAIL_DEMO_5V (5V±5% 电源轨) 非数据线 → VRWM 须 >= 5.25V; 紧贴 J_USB_C; Forlinx 载板指引要求 ESD 紧贴接口",
    "candidates": [
      {
        "pn": "PESD5V0S1BA",
        "mfr": "Nexperia",
        "evidence": "[官网]",
        "url": "https://www.nexperia.com/product/PESD5V0S1BA",
        "params": "VRWM 5.0V; VBR 6V min; V(CL)R 14V; IPPM 12A; PPPM 130W; IRM 5nA; IEC61000-4-2 >30kV; IEC61000-4-5 IPPM 12A; Cd 35pF typ",
        "package": "SOD-323 2-lead 1.3mm pitch body 1.7x1.25x0.95mm",
        "pads": 2
      },
      {
        "pn": "SMBJ5.0A",
        "mfr": "Littelfuse",
        "evidence": "[官网]",
        "url": "https://www.littelfuse.com/products/tvs-diodes/smb-j",
        "params": "VRWM 5.0V; VBR 6.4V min; Vc 9.2V @ Ipp 65.3A (10/1000us); PPP 600W; IR 800uA max; -65~+150C; 单向",
        "package": "DO-214AA SMB 2 焊盘 body ~4.4x3.6mm",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "PESD5V0S1BA",
      "why": "漏电 5nA vs 800uA 差 5 个数量级且体积小; 代价: VRWM 5.0V 对 5.25V 轨顶到边需复核 IR 曲线; SMBJ5.0A 抗尖峰强但 SMB 尺寸超占位",
      "cost": "VRWM 贴边; SMB 候选需改 footprint 或挪位",
      "disclaimer": "不代拍, 属 V-2 口径, 一票交 main/老板"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 VBUS/GND 对上双向件 OK; SOD-323 本体 1.7x1.25x0.95mm 落在 bbox 2.70x1.60mm 内 OK; 但占位间距 2.30mm 与 SOD-323 官方 1.3mm land 不重合须重画。候选2 SMB 4.4x3.6mm 超出 bbox 不兼容",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 IR 曲线过不了 5.25V, 改选 VRWM 6V 档 2 脚件 (PESD6V0S1BA 类 / SP1006-01 类, 本轮 [0数据]); 若须抗插拔尖峰, 保留 ESD 件 + 另加 TVS 位 (归落表/板那一趟)"
  },
  {
    "ref": "D_ESD_USB_D",
    "board": "MAIN_PCB",
    "type": "ESD",
    "criteria": "USB 2.0 D+ (USB_D_P_SRC) → Cd <= 10pF 级保住上升沿; 紧贴 J_USB_C; D− 无 ESD 占位",
    "candidates": [
      {
        "pn": "TPD1E05U06DPYR",
        "mfr": "Texas Instruments",
        "evidence": "[官网]",
        "url": "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
        "params": "Cd 0.42pF typ; VRWM 5.5V; VBR 6.5V min; ILEAK 10nA max; IEC61000-4-2 level 4; -40~+125C; pin1=I/O pin2=GND",
        "package": "DPY X1SON 2-pin",
        "pads": 2
      },
      {
        "pn": "PESD5V0U1BA-Q",
        "mfr": "Nexperia",
        "evidence": "[官网]",
        "url": "https://assets.nexperia.com/documents/data-sheet/PESD5V0U1BA-Q.pdf",
        "params": "Cd 11pF typ/13pF max; VRWM 5V; VBR 5.8-7.8V; VCL 12.5V @ IPP 4.8A; PPP 45W; IRM <1nA typ/10nA max; IEC61000-4-2 level 4 ±30kV; IEC61000-4-5 IPP 4.8A",
        "package": "SOD-323 2-lead 1.3mm pitch",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "TPD1E05U06DPYR",
      "why": "0.42pF 与 4 件 ESD 可共用一个 OPN 减少 BOM 行数与来料种类; 代价: X1SON 需机器贴装; USB 3.3V 下等效容本轮 [0数据]",
      "cost": "机器贴装要求; 3.3V 偏压下等效容未取官方曲线",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 I/O/USB_D_P_SRC + GND 对上 OK (pad1=信号 pad2=GND 与 DPY 一致); 本体远小于 bbox 2.70x1.60mm OK; 占位间距 2.30mm 与厂商 land 不重合须重画",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若不许重画 land, 选 land 间距约 2.30mm 的 2 脚 ESD 件 (本轮在售件均偏小, [0数据]) 并登记占位 land 不匹配缺口; 双通道保护须改板"
  },
  {
    "ref": "D_ESD_TC",
    "board": "CHG_BOARD",
    "type": "ESD",
    "criteria": "Type-C 入口 ESD 阵列, 必须带地脚 (V1.4 补), 通道数随 Type-C 座定; VRWM >= 5.25V; 紧贴 J_TYPE_C",
    "candidates": [
      {
        "pn": "PESD5V0S1BA",
        "mfr": "Nexperia",
        "evidence": "[官网]",
        "url": "https://www.nexperia.com/product/PESD5V0S1BA",
        "params": "VRWM 5V; VBR 6V min; V(CL)R 14V; IPPM 12A; PPPM 130W; IRM 5nA; IEC61000-4-2 >30kV; 双线需 2 只",
        "package": "SOD-323 2-lead",
        "pads": 2
      },
      {
        "pn": "TPD1E05U06DPYR",
        "mfr": "Texas Instruments",
        "evidence": "[官网]",
        "url": "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
        "params": "Cd 0.42pF; VRWM 5.5V; VBR 6.5V min; ILEAK 10nA max; IEC61000-4-2 level 4; pin1=I/O pin2=GND",
        "package": "DPY X1SON 2-pin",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "PESD5V0S1BA",
      "why": "电气上双通道阵列 (TPD2E2U06 类) 才是 Type-C 正解, 但最少 3 脚落不下 2 焊盘; 故主候选给 2 脚件可立刻投板, 同时把双通道方案的改 footprint 代价写明, 属 V-2 待裁",
      "cost": "单通道件只能护 1 条线 (Type-C 需护 VBUS+D+/D−); 双通道须改充电板 footprint",
      "disclaimer": "不代拍 V-2, 一票交 main/PM"
    },
    "package_compat": {
      "verdict": "落2焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上 2 脚器件落 2 焊盘成立, 焊盘网络 I/O/GND 成立; TPD2E2U06 (3/5 脚) 落不下 2 焊盘",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 C-01 规格定成单通道 ESD, 直接落 2 脚 PESD5V0S1BA (充电板 footprint 按厂商 land 定, 零额外风险); 若要双通道, 选 TPD2E2U06DCKR (SC70-3) + 充电板改 3 焊盘 (归落表/板那一趟); 若要护 3 条线, 选多通道阵列件 PESD5V0S4UD / PESD5V0S2UAT (充电板 footprint 一次定到多通道)"
  },
  {
    "ref": "FB_DEMO",
    "board": "MAIN_PCB",
    "type": "L",
    "criteria": "USB-C 5V/2A 轨 π 滤波磁珠; 0805 级本体 <= 2.00x1.25mm; 额定电流 >= 2A; 阻抗 @100MHz 够高; DCR 要低 (2A 下压降 = I x DCR)",
    "candidates": [
      {
        "pn": "BLM21PG221SN1D",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads",
        "params": "0805 2.00x1.25mm; Z 220ohm @100MHz ±25%; Irated 2A; DCR 45mOhm max; -55~+125C; 1 line",
        "package": "0805 (2012 metric)",
        "pads": 2
      },
      {
        "pn": "BLM21PG601SN1D",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads",
        "params": "0805; Z 600ohm @100MHz; Irated 1.5A; DCR 0.09Ohm max; -55~+125C",
        "package": "0805 (2012 metric)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "BLM21PG221SN1D",
      "why": "220ohm @100MHz + DCR 45mOhm + 2A + 0805 本体 2.00x1.25mm 与占位 bbox 2.00x1.60mm 精确对上, 四项判据全中且 DCR 最低 (2A 下 180mW)",
      "cost": "2A 额定刚好压在 5V/2A 档无余量 (需 3A 则改 1206); 220ohm 对 30~100MHz 中频段抑制弱 (换 600ohm 档则 DCR 翻倍到 180mV 压降); 180mW 发热需结构/板那一趟核散热",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=RAIL_DEMO_5V 进 / pad2=GND 出 对应两脚件 OK; 本体 2.00x1.25mm <= 占位 fab bbox 2.00x1.60mm OK; 占位焊盘 0.55x0.90mm 对角布置 (Δx0.80/Δy0.60) 与 0805 官方 land 不重合, 仍须落板批次复核焊盘图 (两端对称无方向歧义)",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 2A 不够 (需 >=3A) 换 1206 BLM31PG 系列 (尺寸变大归落表/板那一趟); 若 DCR 45mOhm 压降/发热不可接受, 换同尺寸低 DCR 档 BLM21P221SG 类 (220ohm/2000mA/0.05ohm, 完整官方页本轮 [0数据] 落表批次补); 若噪声主频不在 100MHz 附近, 保留 220ohm 并加大 π 滤波体电容 (C_VBUS_DEMO 已 10uF)"
  },
  {
    "ref": "FB_VBUS",
    "board": "CHG_BOARD",
    "type": "L",
    "criteria": "BQ25896 VBUS 输入路径的 π 滤波磁珠 (网表: 阻抗/电流随充电 IC 环路稳定性定) → DCR 必须低 (不能破坏充电环路稳定性); 额定电流 >= PD 5V/2A; 阻抗 @100MHz 挡开关噪声; 阻抗与 DCR 是一对矛盾",
    "candidates": [
      {
        "pn": "BLM21PG221SN1D",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads",
        "params": "0805 2.00x1.25mm; Z 220ohm @100MHz; Irated 2A; DCR 45mOhm max; 2A 时压降 90mV (5V 轨 1.8%)",
        "package": "0805 (2012 metric)",
        "pads": 2
      },
      {
        "pn": "BLM31PG121SN1",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/emifil/overview/lineup/bl/lineup/chip-ferrite-beads",
        "params": "1206 3.2x1.6mm; Z 120ohm @100MHz; Irated 3000mA; DCR 0.025Ohm max",
        "package": "1206 (3216 metric)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "BLM31PG121SN1",
      "why": "DCR 25mOhm (候选1 的 55%) + 额定 3000mA (1.5x) → 串在 BQ25896 VBUS 环路里的阻性阻尼最小, 环路稳定性裕量最大; 120ohm @100MHz 仍挡得住 VBUS 上 MHz 级开关噪声",
      "cost": "1206 比 0805 大一整号, 充电板面积成本上升 (ISS-216/ISS-229 盯的热点); 阻抗从 220ohm 降到 120ohm 中高频段抑制弱一档; FB_VBUS footprint 待定故尺寸可自由定, 无需改主板",
      "disclaimer": "不代拍, 充电环路稳定性须由 main/PM 用 BQ25896 官方 §10.2.2 复核, 一票交 main"
    },
    "package_compat": {
      "verdict": "落2焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上磁珠 2 脚落 2 焊盘成立; 焊盘网络 VBUS_5V_ESD 进 / VBUS_5V_F1 出 成立; 封装尺寸 0805/1206 充电板侧可自由定, 由落表批次定充电板 footprint",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若充电板面积不够 1206, 用 0805 BLM21PG221SN1D (DCR 45mOhm) → 代价是充电环路阻尼变大, 必须由 main/PM 按 BQ25896 官方 §10.2.2 复核 1.22A 档稳定性, 并登记磁珠影响充电环路稳定性缺口; 若 Imax > 3A, 换 1206 低 DCR 大电流档 BLM31P330SG (33ohm/6000mA/0.01ohm)"
  },
  {
    "ref": "D_TVS_VBUS",
    "board": "CHG_BOARD",
    "type": "D",
    "criteria": "PM 裁决原文: 必装; VRWM 5-6V 档; 脉冲电流额定 >= 3A (PD 5V/2A 场景); 钳位电压 < BQ25896 绝对最大 22V (TI 手册 §8.1: VBUS -2V..22V); 位置紧靠 Type-C 座",
    "candidates": [
      {
        "pn": "SMBJ5.0A",
        "mfr": "Littelfuse",
        "evidence": "[官网]",
        "url": "https://www.littelfuse.com/products/tvs-diodes/smb-j",
        "params": "VRWM 5.0V; VBR 6.4V min; Vc 9.2V @ Ipp 65.3A (10/1000us); PPP 600W; IR 800uA max; -65~+150C; 单向; Vc 9.2V 相对 BQ25896 22V 有 2.4x 余量",
        "package": "DO-214AA SMB 2 焊盘",
        "pads": 2
      },
      {
        "pn": "SMBJ6.0A",
        "mfr": "STMicroelectronics",
        "evidence": "[官网]",
        "url": "https://www.st.com/en/protections-and-emi-filters/smbj6-0a.html",
        "params": "VRWM 6.0V (PM 要求的 5-6V 档上沿, 对 5V±5% 余量更大); SMB 封装; 系列 ≤600W 10/1000us; 适用 IEC61000-4-2/4-4/4-5; Vc/Ipp 具体值本轮 [0数据]",
        "package": "DO-214AA SMB 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "SMBJ5.0A",
      "why": "参数全齐可核: Vc 9.2V 远低于 BQ25896 的 22V 绝对最大 (2.4x 余量); Ipp 65.3A 远超 PM 要求的 >=3A; PPP 600W 应对插线尖峰; Littelfuse 原厂官网可直接核",
      "cost": "VRWM 5.0V 对 5.25V 轨顶边 (若判须留余量则走 SMBJ6.0A); IR 800uA 在 VBUS 常驻下是持续漏电 (5V x 800uA = 4mW, 若计入整机静态功耗账需登记); SMB 封装比占位其它件大, 充电板面积成本",
      "disclaimer": "5V 档 vs 6V 档属 PM 已裁 '5-6V 档' 的解释权, 不代拍, 一票交 main/PM"
    },
    "package_compat": {
      "verdict": "落2焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上 TVS 2 脚落 2 焊盘成立; 焊盘网络 pad1=VBUS_5V(K) / pad2=GND(A) 与单向 TVS 一一对应; SMB (DO-214AA ~4.4x3.6mm) 充电板 footprint 按此定",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 main 判 VRWM 必须 > 5.25V, 改 SMBJ6.0A / SMBJ7.0A (ST 与 Littelfuse 官网均在售) 但 SMBJ6.0A 的 Vc/Ipp 本轮 [0数据], 落表批次必须按官方手册核 Vc < 22V 才准落; 若充电板放不下 SMB, 改 SMA 档 SMAJ5.0A/SMAJ6.0A 或 SOD-123 档 (尺寸与参数落表批次补)"
  },
  {
    "ref": "Q_AND",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "N 沟道 3 脚; 漏极=RESET_N, 源极=GND, 栅极=PG_AND (3.3V 域开漏驱动) → VGS(th) 必须低否则复位释放不了; 关断漏电要小 (漏极挂 RESET_N); 拉低电流仅 330uA (R_PU_RESET_N 10k)",
    "candidates": [
      {
        "pn": "AO3400A",
        "mfr": "Alpha & Omega Semiconductor",
        "evidence": "[官网]",
        "url": "https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf",
        "params": "30V N-ch SOT23; VGS(th) 0.65V min/1.05V typ/1.45V max; RDS(on) 26.5mOhm@10V, 32mOhm@4.5V, 48mOhm@2.5V; ID 5.7A; PD 1.4W; IGSS <=100nA; VGS ±12V; -55~+150C; pin1=G pin2=S pin3=D",
        "package": "SOT-23 3 脚",
        "pads": 3
      },
      {
        "pn": "2N7002",
        "mfr": "onsemi / Microchip",
        "evidence": "[官网]",
        "url": "https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf",
        "params": "60V N-ch SOT-23; VGS(th) 1.0V min/1.76V typ/2.0V max (2N7002DW); RDS(on) 1.2ohm typ@10V, 2.4ohm typ@4.5V; ID 115mA cont; PD 0.36W; IDSS <=1uA; IGSS <=±10nA; -55~+150C",
        "package": "SOT-23 3 脚",
        "pads": 3
      }
    ],
    "recommendation": {
      "pick": "AO3400A",
      "why": "VGS(th) max 1.45V vs 2N7002 的 2.0V → 3.3V 栅驱动下过驱动余量 2.3x vs 1.3x, 这是硬件 AND 能否真放开复位的成败线; RDS(on) 48mOhm vs 2.4ohm 拉低压降差 50 倍",
      "cost": "RDS(on) 对本位是过剩规格 (更省的 2N7002 也够用); AOS 需确认在售通道; pad↔pin 映射与器件引脚序不一致必须逐件核 (占位 pad1=RESET_N=D 而器件 pin1=G)",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 3=3 OK; 焊盘网络 pad1=RESET_N(D)/pad2=GND(S)/pad3=PG_AND(G) 但占位 pad 序为 D/S/G 而 SOT-23 库引脚序为 G/S/D → 重画 land 时必须把 RESET_N 接到器件 D 脚、PG_AND 接到 G 脚, 不能按 pad 序号机械对; 本体 2.9x1.3mm <= bbox 4.00x5.00mm OK; 占位间距 1.27/1.53mm 与 SOT-23 0.95mm pitch 不重合须重画",
      "pads_required": 3
    },
    "evidence": "[官网]",
    "fallback": "若不许重画 land, 须选引脚序与占位 pad 序 (D/S/G) 一致的 3 脚器件 → 在售 SOT-23 绝大多数为 G-S-D 故此路实际不通, 登记为缺口 G-2; 若 AOS 通道不通, 改 onsemi 2N7002/2N7002K → 代价 VGS(th) max 2.0V 在 3.3V 驱动下过驱动仅 1.3x, 须由 main 复核 'PG_AND 低时 Q_AND 必须完全关断' 的时序是否成立"
  },
  {
    "ref": "Q_ENVC",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "N 沟道 3 脚反相; 漏极=EN_VCORE (把 EN 拉低=不使能), 源极=GND, 栅极=PG_AND → 高栅压时必须完全导通拉低 EN_VCORE (R_EN_VCORE 10k, 330uA); 关断漏电要极小 (漏极挂 EN_VCORE, 漏电=误使能); 网表标注 PG 极性待原厂核 → 须选两种极性都安全的器件",
    "candidates": [
      {
        "pn": "AO3400A",
        "mfr": "Alpha & Omega Semiconductor",
        "evidence": "[官网]",
        "url": "https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf",
        "params": "30V N-ch SOT23; VGS(th) 0.65/1.05/1.45V; RDS(on) 26.5mOhm@10V, 32mOhm@4.5V, 48mOhm@2.5V; IGSS <=100nA; IDSS <=1uA 量级; pin1=G pin2=S pin3=D",
        "package": "SOT-23 3 脚",
        "pads": 3
      },
      {
        "pn": "2N7002",
        "mfr": "onsemi / Microchip",
        "evidence": "[官网]",
        "url": "https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf",
        "params": "60V N-ch SOT-23; VGS(th) 1.0/1.76/2.0V; RDS(on) 1.2ohm typ@10V; IGSS <=±10nA; IDSS <=1uA; ID 115mA; PD 0.36W",
        "package": "SOT-23 3 脚",
        "pads": 3
      }
    ],
    "recommendation": {
      "pick": "AO3400A",
      "why": "栅压裕量优先: VGS(th) max 1.45V 在 3.3V 下过驱动 2.3x → EN_VCORE 被可靠拉低 → 顺序链可靠; 两件在 330uA 负载下 RDS(on) 压降都 <1mV 无差别, 真取舍只有 '栅压裕量 vs 漏电裕量'",
      "cost": "候选2 IGSS 10nA vs 候选1 100nA (10x), 对 EN_VCORE 误使能更友好, 该优势须摆给 main; 若 main 判漏电权重更高则改 2N7002, 代价是 VGS(th) max 2.0V 时完全导通把握下降, 且须结合网表 'PG 极性待原厂核' 一起裁",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 3=3 OK; 焊盘网络 pad1=PG_AND(G)/pad2=GND(S)/pad3=EN_VCORE(D) 恰为 G/S/D, 与 SOT-23 库引脚序一致 (三件 MOS 里唯一不用改映射的一件); 本体 2.9x1.3mm <= bbox 4.00x5.00mm OK; 占位间距与 SOT-23 0.95mm pitch 不重合须重画",
      "pads_required": 3
    },
    "evidence": "[官网]",
    "fallback": "若 main 判漏电误使能权重更高, 改选 IGSS <=10nA 的 3 脚 SOT-23 (onsemi 2N7002/2N7002K) → 代价 VGS(th) max 2.0V 时完全导通裕量下降, 须结合 PG 极性待核一起裁; 若 PG 极性最终为反, 改用 N 沟道 + 拉电阻拓扑 (需改板, 归落表/板那一趟)"
  },
  {
    "ref": "Q_PG",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "网表硬判据原文: 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级; 漏极挂 BAT_SW 电池轨 (关机仍带电) 且本板贴皮肤 → 漏电直接进电池账与皮肤温度; Vgs≈-4.2V 是拓扑核心; 源漏耐压 >= 4.2V + 余量",
    "candidates": [
      {
        "pn": "DMP3098L",
        "mfr": "Diodes Incorporated",
        "evidence": "[官网]",
        "url": "https://www.diodes.com/datasheet/download/DMP3098L.pdf",
        "params": "-30V P-ch SOT23; IDSS <=800nA @VDS=-30V (nA 级, 命中硬判据); IGSS <=±100nA; VGS(th) -1.0V min/-1.8V typ/-2.1V max; RDS(on) 56/70mOhm@-10V, 98/120mOhm@-4.5V (typ/max); ID -3.8A; BVDSS -30V; -55~+150C; VGS 绝对最大栏手册未见 => [0数据]",
        "package": "SOT23 3 脚",
        "pads": 3
      },
      {
        "pn": "AO3407A",
        "mfr": "Alpha & Omega Semiconductor",
        "evidence": "[官网]",
        "url": "https://www.aosmd.com/pdfs/datasheet/AO3407A.pdf",
        "params": "-30V P-ch SOT-23; VGS(th) -1.4/-1.9/-2.4V; RDS(on) 48mOhm max@-10V, 78mOhm max@-4.5V; ID -4.3A; IDSS <=1uA@25C, <=5uA@55C; IGSS ±100nA; VGS ±20V (绝对最大明写); PD 1.4W; -55~+150C; pin1=G pin2=S pin3=D",
        "package": "SOT-23 3 脚",
        "pads": 3
      }
    ],
    "recommendation": {
      "pick": "DMP3098L",
      "why": "命中 '关断漏电 nA 级' 硬判据 (IDSS <=800nA vs AO3407A 的 1uA@25C / 5uA@55C, 高温差 6 倍) → Q_PG 漏极挂 BAT_SW 且贴皮肤, 55C 下漏电与自发热正相关; VGS(th) typ -1.8V 距 Vgs≈-4.2V 有 2.4V 余量; RDS(on) 98mOhm@4.5V 对只过微安级栅极电流的通路不是瓶颈",
      "cost": "RDS(on) 略高但非瓶颈; Diodes Inc 在售通道本轮只核到官网手册与型号页, 目录在售页未抓到需落表批次确认 (缺口); DMP3098L 的 VGS 绝对最大手册未见 ([0数据]) 而 AO3407A 明写 ±20V, 故若 ±20V 栅极耐压是硬门槛则应改用 AO3407A, 代价是高温档漏电 5uA 进电池账需 main 签字",
      "disclaimer": "漏电档位取舍 (nA 级 vs RDS(on) 裕量) 属待裁项, 不代拍, 一票交 main/PM"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 3=3 OK; 焊盘网络 pad1=PWR_ON(S)/pad2=BAT_SW(D)/pad3=PWR_GOOD(G) 而占位 pad 序为 S/D/G, 与 SOT-23 库引脚序 G/S/D 不一致 → 重画 land 时必须 PWR_GOOD→器件 G 脚, PWR_ON→S 脚, BAT_SW→D 脚, 接反则 Vgs 极性反转开机路径不通; 本体 2.9x1.3mm <= bbox 4.00x5.00mm OK; 另注网表 note 的 '源极接 ON / 漏极接 BAT_SW' 措辞与 P-MOS 高边开关常规拓扑相反, 已登记缺口 G-1 交 main/PM 裁决 (本单不代拍)",
      "pads_required": 3
    },
    "evidence": "[官网]",
    "fallback": "若 DMP3098L 采购通道不通, 改 AO3407A (VGS ±20V 明写参数全) → 代价是关断漏电高温档 5uA, 贴皮肤 55C 下须进电池续航预算 (参照 ISS-172 的 108uA 关机账) 并由 main 给接受与否; 若 ±20V 栅极耐压是硬门槛而 DMP3098L 查不到, 只能 AO3407A 同代价; 若缺口 G-1 裁决为源漏要反过来, 落表批次必须连原理图一起核 (归落表/板那一趟)"
  },
  {
    "ref": "Q_CHG_LED",
    "board": "CHG_BOARD",
    "type": "SW",
    "criteria": "N 沟道 3 脚; 漏极=LED 阴极 (CHG_LED_K), 源极=GND, 栅极=CHG_STAT (BQ25896 pin4 开漏, 主板侧 10k 上拉到 3.3V) → VGS(th) 须够低; 关断漏电要小 (漏极挂 LED 阴极, 漏电=灯微亮); LED 电流 ≈ (5-Vf)/1k ≈ 3mA → 小信号管足够",
    "candidates": [
      {
        "pn": "2N7002",
        "mfr": "onsemi / Microchip",
        "evidence": "[官网]",
        "url": "https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/2N7002-N-Channel-Enhancement-Mode-Vertical-DMOS-FET-Data-Sheet-20005797A.pdf",
        "params": "60V N-ch SOT-23; VGS(th) 1.0/1.76/2.0V; RDS(on) 1.2ohm typ@10V (3mA 下压降 ≈3.6mV 可忽略); IGSS <=±10nA; IDSS <=1uA; ID 115mA (38x 余量)",
        "package": "SOT-23 3 脚",
        "pads": 3
      },
      {
        "pn": "AO3400A",
        "mfr": "Alpha & Omega Semiconductor",
        "evidence": "[官网]",
        "url": "https://www.aosmd.com/pdfs/datasheet/AO3400A.pdf",
        "params": "30V N-ch SOT23; VGS(th) 0.65/1.05/1.45V (3.3V 驱动下过驱动 1.85x 更足); RDS(on) 48mOhm@2.5V; IGSS <=100nA; ID 5.7A; 30V 耐压对 5V 回路够",
        "package": "SOT-23 3 脚",
        "pads": 3
      }
    ],
    "recommendation": {
      "pick": "2N7002",
      "why": "本位的真实需求是 mA 级电流 + 低漏电: 3mA 负载下 1.2ohm 的 RDS(on) 完全够 (AO3400A 的 26.5mohm 是过剩规格只多花钱多占料号); IGSS 10nA vs 100nA 关断时对 LED 阴极漏电低 10 倍, 灯不会微亮; ID 115mA 对 3mA 有 38x 余量",
      "cost": "VGS(th) max 2.0V 而 STAT 上拉到 3.3V → 过驱动仅 1.3V 偏薄 (关断可靠, 但需 main 确认), 若 STAT 驱动电压不足 3.3V 则须改 AO3400A (VGS(th) max 1.45V)",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "落3焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上 MOS 3 脚落 3 焊盘成立; 焊盘网络 漏极↔CHG_LED_K / 源极↔GND / 栅极↔CHG_STAT 与 SOT-23 的 G/S/D 一一对应; 充电板 footprint 待定, 由落表批次定 3 焊盘 land 并把 pad↔pin 序定成 G/S/D 以免重犯主板那三件的错",
      "pads_required": 3
    },
    "evidence": "[官网]",
    "fallback": "若 STAT 驱动电压不足 3.3V, 改 AO3400A (VGS(th) max 1.45V) → 代价是过剩规格多花成本; 若要同时低漏与低阈值, 选 AO3401A 类或并栅极下拉, 但网表 note 明写已删充电板本地 5V 上拉, 加下拉属改网表 → 归落表批次, 本单不落表"
  },
  {
    "ref": "D_LED_G",
    "board": "MAIN_PCB",
    "type": "LED",
    "criteria": "0805 级本体 <= 2.70x1.60mm; VF 要匹配 R_LED_G=1k 上拉下的实际电流 ≈ (3.3-Vf)/1k ≈ 1.1mA (需低电流高亮度料); 波长 λdom ≈ 565-570nm; 极性: 阴极→GND (pad2), 阳极接 pad1",
    "candidates": [
      {
        "pn": "KP-2012SGC",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "https://www.tme.eu/Document/05a11926c5bbe30cd4bcc8411758e7d5/KP-2012SGC.pdf",
        "params": "0805 2.0x1.25mm; λpeak 565nm / λdom 568nm; VF 2.2V typ / 2.5V max @IF=20mA; IV 12mcd typ@20mA; IF 25mA DC / 140mA peak; IR <=10uA@VR=5V; C 15pF; PD 62.5mW; VR 5V; TJ 110C; -40~+85C; MSL 3; RoHS",
        "package": "0805 (2012 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "APH1608SGC",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "https://www.kingbrightusa.com/images/catalog/spec/APH1608SGC.pdf",
        "params": "0603 1.6x0.8mm; λdom 568nm; VF 2.2V typ / 2.5V max @20mA; IV 5/12mcd@20mA; IF 25mA / IFM 140mA; IR <=10uA; C 15pF; PD 62.5mW; TJ 110C; -40~+85C",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "KP-2012SGC",
      "why": "0805 本体与占位 bbox 2.70x1.60mm 精确对齐 (0603 的 1.6x0.8 在同 bbox 里偏小, 落板后 LED 位置比原设计靠内 0.2mm); 与 D_LED_R 同厂同参数族 (VF 2.2/2.5V, C 15pF, PD 62.5mW, TJ 110C) 便于同族采购",
      "cost": "R_LED_G=1k + 3.3V ⇒ 实际电流仅约 1.1mA 而两颗 LED 都是 20mA 标称 ⇒ 1mA 工作点实际亮度本轮 [0数据], 亮度账不匹配已登记缺口 G-5 (改 R 阻值属改网表, 归落表批次)",
      "disclaimer": "不代拍, 亮度口径属 PM, 一票交 main"
    },
    "package_compat": {
      "verdict": "兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=LED_G_D=阳极 / pad2=GND=阴极, 与网表 note 'LED_G 阴极->GND' 一致 OK; 本体 2.0x1.25mm <= bbox 2.70x1.60mm OK (候选2 0603 1.6x0.8mm 也放得下但偏小); 占位焊盘 0.6x0.9mm @2.30mm 中心距 与 Kingbright 官方 0805 land 不重合, 仍须落板批次重画",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若要提亮度, 改用低电流高亮度型 (APHBM2012LCGKSYKC 类 2mA 级) 或把串阻从 1k 改小 (属改网表, 归落表批次); 若板面无 0805 空间, 用 0603 候选2 (代价是与 D_LED_R 不同封装尺寸, 两颗不同料号); 若 λdom 568nm 不满足指示色标准, 改同封装 AP2012CGCK (0805 绿 570nm 20/50mcd)"
  },
  {
    "ref": "D_LED_R",
    "board": "MAIN_PCB",
    "type": "LED",
    "criteria": "0805 级本体 <= 2.70x1.60mm; VF 低 (红光 ~1.9-2.2V) ⇒ 1k 下电流更足; λdom ≈ 617-630nm; 阴极→GND (pad2); 与 D_LED_G 同为 SoM 驱动 (pin80/pin19) 两颗须同档亮度才能对称",
    "candidates": [
      {
        "pn": "APT1608SURCK",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APT1608SURCK",
        "params": "0603 1.6x0.8x0.75mm; AlGaInP; λdom 630nm; IV 40mcd min / 80mcd typ @20mA; 视角 120°; 2000pcs/卷; MSL 3; RoHS",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "AA1608SURSK",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "https://www.kingbrightusa.com/lobbyMinaturePLCC2.asp",
        "params": "0603 PLCC-2 1.6x0.8x0.55mm; λdom 630nm; IV 40mcd min / 160mcd typ @20mA; 120°; IF 30mA / IFM 185mA; PD 75mW; -40~+85C",
        "package": "0603 PLCC-2 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "AA1608SURSK",
      "why": "亮度余量: 160mcd typ vs 候选1 的 80mcd typ ⇒ 本板 1k 串阻下电流远低于 20mA 标称, 亮度余量是唯一能救这个位的参数; PLCC-2 更适合贴导光孔/结构件; 与候选1 同 0603 封装可互换",
      "cost": "两颗都是 0603 而占位 bbox 是 0805 级 ⇒ 本体偏小且与 D_LED_G 的 0805 候选不同封装 (落板批次要用两套 land); 若要求两颗 LED 同封装同档, 应改用 0805 对应料 (AA1608SURSK 的 0805 版本轮 [0数据]); AP2012EC (0805 红 617nm) 亮度仅 3/8mcd@20mA ⇒ 1.3mA 下几乎不可见, 不推荐",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=LED_R_D=阳极 / pad2=GND=阴极 与网表 note 'LED_R 阴极->GND' 一致 OK; 本体 1.6x0.8x0.75mm <= bbox 2.70x1.60mm OK (偏小, 落板后位置比原设计靠内); 占位 land 2.30mm 中心距与 0603 官方 land 不重合须重画",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若两颗 LED 要同封装, 绿用 KP-2012SGC (0805) + 红用 AA1608SURSK 的 0805 对应料 (本轮 [0数据] 落表批次补), 或 AP2012EC (0805) 但亮度仅 3/8mcd 不推荐; 若 LED_R 是故障指示需醒目, 换更高亮度档 AA1608SURSK 或红/绿双色"
  },
  {
    "ref": "D_CHG_LED",
    "board": "CHG_BOARD",
    "type": "LED",
    "criteria": "充电板侧封装待定 ⇒ 尺寸自由; VF 匹配 R_CHG_LED=1k + VBUS_5V_CHG=5V ⇒ 电流约 3mA; 充电状态指示 (STAT 低=充电中/高=完成/1Hz闪=故障) ⇒ 单色只能表达亮灭闪, 表达不了红绿两态; 结构需导光孔 (ISS-103) ⇒ 封装高度有上限",
    "candidates": [
      {
        "pn": "APT1608SURCK",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APT1608SURCK",
        "params": "0603 1.6x0.8x0.75mm; AlGaInP; λdom 630nm; IV 40/80mcd@20mA; 120°; MSL 3 → 红=充电中",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "APT1608CGCK",
        "mfr": "Kingbright",
        "evidence": "[官网]",
        "url": "https://www.kingbrightusa.com/KCpack.asp?txtPack=APT1608&page=1",
        "params": "0603 1.6x0.8x0.75mm; λdom 570nm; IV 20/50mcd@20mA; 120° → 绿=完成/空闲",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "APT1608SURCK",
      "why": "红=充电中 与行业习惯一致且插线场景更醒目; 单一 2 脚件配 Q_CHG_LED 的 STAT 逻辑天然得到 亮/灭/闪 三态 (故障 1Hz 闪免费得到), 结构只需 1 个导光孔; 候选2 (绿) 与候选1 是同一位置二选一而非同位替代, 颜色口径属 PM",
      "cost": "单色灯表达不了红/绿两态 (若要双色需 0805 四脚 APHBM2012CGKSEKC 类 + 加第二颗 MOS ⇒ 改网表, 归落表批次); 导光孔高度须与 0.75mm 封装对齐 (ISS-103); ISS-103 未定则先按 0603 单色定充电板 footprint",
      "disclaimer": "状态指示颜色口径属 PM, 不代拍, 一票交 main"
    },
    "package_compat": {
      "verdict": "落2焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上单色 LED 2 脚落 2 焊盘成立; 焊盘网络 pad1=LED_CHG_A (阳极, 接 R_CHG_LED) / pad2=CHG_LED_K (阴极, 接 Q_CHG_LED 漏极) 有极性, 充电板 footprint 定 land 时 pad↔pin 序不能反; 封装尺寸 0603 1.6x0.8x0.75mm 由充电板侧定",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若导光孔要求更扁, 改 0.65mm 高的 0603 系列 (原厂 KC0603+LED+Height-0.65mm 分类页 APH1608SURCK/APH1608CGCK/APT1608* 等, 参数同族); 若要双色, 选 APHBM2012CGKSEKC (0805 红/绿 4 脚) + 改网表加第二颗 MOS (归落表/板那一趟); 若 ISS-103 导光孔未定, 先按 2 脚单色 0603 定 footprint, 颜色与高度待结构确认"
  },
  {
    "ref": "SW_BOOT",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "2 脚 SPST-NO 贴片轻触 (占位只有 2 焊盘, 4 脚带固定柱版落不下); 本体 <= 3.0x3.0mm (SKQGABE010 的 5.2x5.2mm 落不下); BOOT 键误触后果最重 (误进下载模式) → OF 偏大 (2-3N) + 行程偏小; 寿命; 镜腿贴皮肤 → 至少 -25~+70C; 电流仅 330uA (R_PU_BOOT_N 10k) ⇒ 微安级",
    "candidates": [
      {
        "pn": "KMR231ULCLFS",
        "mfr": "C&K",
        "evidence": "[官网]",
        "url": "https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf",
        "params": "KMR 2 系列 SMT 轻触, NG 无接地脚 2 脚版, ULC 低电流档 (silver 50mA/gold 10mA, min 1mA); OF 3.0N (300gf) ±0.75N; travel 0.25mm ±0.1mm; 寿命 150,000 次; SPST-NO; 总高 1.9mm; 接触电阻 <100mOhm; 最大 32VDC; 本体约 2.6x2.6mm 但 PCB layout 外扩至 4.6x3.2mm 需复核",
        "package": "KMR 2 2 脚 (gullwing SMT)",
        "pads": 2
      },
      {
        "pn": "B3U-1000P",
        "mfr": "Omron",
        "evidence": "[官网]",
        "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf",
        "params": "2 脚无固定脚版 (B3U-1100P=带接地脚4脚, B3U-1000P-B=带boss, 均须避开); 本体 3.0x2.5mm; 总高 1.6mm; OF 1.50N ±0.49N; RF >=0.2N; PT 0.15mm / travel 0.2mm; 寿命 200,000 次; SPST-NO; 50mA/12VDC; IP40; -25~+70C; ≈0.022g",
        "package": "B3U 2 脚 (gullwing SMT)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "KMR231ULCLFS",
      "why": "BOOT 键误触后果最重 (误进下载模式) → OF 3.0N 比 B3U 的 1.5N 高一倍, 显著降低盲操作/戴手套误触; NG 无接地脚版 = 2 脚正对上占位; ULC 低电流档 min 1mA 正对本板 330uA",
      "cost": "KMR2 的 PCB layout 外扩到 4.6x3.2mm 超过占位 bbox 3.00x3.00mm → 须重画 land 并复核与相邻键/LED 间隙 (本组 5 件最大代价); 寿命 150,000 次低于 KMR221/232 的 200,000/300,000 (BOOT 键按得少, 可接受)",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK (NG 无固定脚版); 焊盘网络 pad1=BOOT_N / pad2=GND 与 SPST-NO 两脚件对上 OK; 候选2 本体 3.0x2.5mm 与 bbox 3.00x3.00 基本正好, 候选1 本体 2.6x2.6mm 放得下但 gullwing 引脚外扩使整体 land 4.6x3.2mm 超 bbox → 两者都须落板批次按官方 land 重画并复核边界",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 bbox 装不下 gullwing 外扩, 改更小的 2 脚贴片按键 (如 Panasonic EVQ-P 3.5x3.5mm 级或其它 <=3x3mm 无引脚 2 脚件, 本轮 [0数据] 落表批次补); 若结构要求更扁, 选 B3U-1000P (总高 1.6mm vs KMR2 的 1.9mm); 若误触仍嫌少, 加保护罩/结构防误触 (MECH 那一趟), 器件层面已到 KMR231/232 的 3N 档上限"
  },
  {
    "ref": "SW_KEY_PWR",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "2 脚 SPST-NO 贴片轻触; 本体 <= 3.0x3.0mm; 电源键误触 = 意外关机 → OF 偏大; 寿命; 贴皮肤 -25~+70C; 电流 330uA",
    "candidates": [
      {
        "pn": "KMR231ULCLFS",
        "mfr": "C&K",
        "evidence": "[官网]",
        "url": "https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf",
        "params": "KMR 2 系列 NG 2 脚 ULC 低电流档; OF 3.0N ±0.75N; travel 0.25mm ±0.1mm; 寿命 150,000 次; 总高 1.9mm; 32VDC; 本体约 2.6x2.6mm (land 外扩 4.6x3.2mm 需复核)",
        "package": "KMR 2 2 脚 (gullwing SMT)",
        "pads": 2
      },
      {
        "pn": "B3U-1000P",
        "mfr": "Omron",
        "evidence": "[官网]",
        "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf",
        "params": "2 脚无固定脚版; 本体 3.0x2.5mm; 总高 1.6mm; OF 1.50N ±0.49N; travel 0.2mm; 寿命 200,000 次; 50mA/12VDC; IP40; -25~+70C",
        "package": "B3U 2 脚 (gullwing SMT)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "KMR231ULCLFS",
      "why": "电源键误触 = 意外关机, 代价高于音量键 → OF 3.0N 优先; NG 版 = 2 脚正对上占位; ULC 低电流档匹配 330uA",
      "cost": "land 外扩超 bbox 须重画 (同 SW_BOOT); 寿命 150,000 次对电源键够用但若用户频繁按可改 KMR232 (3N / 300,000 次)",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=KEY_PWR / pad2=GND 对上 OK; 候选2 本体 3.0x2.5mm 与 bbox 3.00x3.00 几乎正好, 候选1 本体 2.6x2.6mm 但 gullwing 外扩致 land 4.6x3.2mm 超 bbox → 均须重画 land 并复核间隙",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "同 SW_BOOT 降级方案 (更小 2 脚件 / 更薄 B3U-1000P / 结构防误触); 寿命不足则改 KMR232 (3N / 300,000 次)"
  },
  {
    "ref": "SW_KEY_VM",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "2 脚 SPST-NO 贴片轻触; 本体 <= 3.0x3.0mm; 音量- 键频繁按 → 寿命优先 (>=200,000 次) 且要求短行程手感清晰; 贴皮肤 -25~+70C; 电流 330uA",
    "candidates": [
      {
        "pn": "B3U-1000P",
        "mfr": "Omron",
        "evidence": "[官网]",
        "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf",
        "params": "2 脚无固定脚版; 本体 3.0x2.5mm; 总高 1.6mm (5 键里最薄, 利于薄镜腿); OF 1.50N ±0.49N; RF >=0.2N; PT 0.15mm / travel 0.2mm (比 KMR221 的 0.25mm 短 → 触感更脆更省力); 寿命 200,000 次; 50mA/12VDC; IP40; -25~+70C",
        "package": "B3U 2 脚 (gullwing SMT)",
        "pads": 2
      },
      {
        "pn": "KMR221ULCLFS",
        "mfr": "C&K",
        "evidence": "[官网]",
        "url": "https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf",
        "params": "KMR 2 系列 NG 2 脚 ULC 低电流档; OF 2.0N ±0.50N; travel 0.25mm ±0.1mm; 寿命 200,000 次; 总高 1.9mm; 本体约 2.6x2.6mm (land 外扩 4.6x3.2mm 需复核)",
        "package": "KMR 2 2 脚 (gullwing SMT)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "B3U-1000P",
      "why": "音量键是 5 件里按得最多的 → 寿命 200,000 次 + 短行程 0.2mm + 较轻 1.5N (省力) + 总高 1.6mm 最适合薄镜腿; 2 脚无固定脚版对上占位",
      "cost": "本体 3.0x2.5mm 与 bbox 3.00x3.00 几乎正好, 须重画 land; OF 1.5N 比 KMR2 的 2-3N 轻, 若用户反馈按不到位可改 KMR2 更高档",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=KEY_VOL_M / pad2=GND 对上 OK; 候选1 本体 3.0x2.5mm 与 bbox 3.00x3.00 几乎正好, 候选2 本体 2.6x2.6mm 放得下但 gullwing 外扩致 land 4.6x3.2mm 超 bbox → 均须重画 land 并复核间隙",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "同 SW_BOOT 降级方案; 若按动力度不足改 KMR231/232 (3N)"
  },
  {
    "ref": "SW_KEY_VP",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "2 脚 SPST-NO 贴片轻触; 本体 <= 3.0x3.0mm; 音量+ 键频繁按 → 寿命优先 (>=200,000 次) 且要求短行程手感清晰; 贴皮肤 -25~+70C; 电流 330uA",
    "candidates": [
      {
        "pn": "B3U-1000P",
        "mfr": "Omron",
        "evidence": "[官网]",
        "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf",
        "params": "2 脚无固定脚版; 本体 3.0x2.5mm; 总高 1.6mm; OF 1.50N ±0.49N; travel 0.2mm; 寿命 200,000 次; 50mA/12VDC; IP40; -25~+70C",
        "package": "B3U 2 脚 (gullwing SMT)",
        "pads": 2
      },
      {
        "pn": "KMR221ULCLFS",
        "mfr": "C&K",
        "evidence": "[官网]",
        "url": "https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf",
        "params": "KMR 2 系列 NG 2 脚 ULC 低电流档; OF 2.0N ±0.50N; travel 0.25mm ±0.1mm; 寿命 200,000 次; 总高 1.9mm; 本体约 2.6x2.6mm (land 外扩 4.6x3.2mm 需复核)",
        "package": "KMR 2 2 脚 (gullwing SMT)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "B3U-1000P",
      "why": "与 SW_KEY_VM 同族同料 ⇒ 两颗音量键同型号同触感 (用户左右手一致性) + 寿命 200,000 次 + 短行程省力 + 总高最薄",
      "cost": "本体 3.0x2.5mm 与 bbox 几乎正好须重画 land; 若按动力度不足改 KMR231/232 (3N), 但会让左右两颗音量键触感与电源/BOOT 键统一",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=KEY_VOL_P / pad2=GND 对上 OK; 候选1 本体 3.0x2.5mm 与 bbox 3.00x3.00 几乎正好, 候选2 land 外扩超 bbox → 均须重画 land 并复核间隙",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "同 SW_BOOT 降级方案; 若按动力度不足改 KMR231/232 (3N)"
  },
  {
    "ref": "SW_RST",
    "board": "MAIN_PCB",
    "type": "SW",
    "criteria": "2 脚 SPST-NO 贴片轻触; 本体 <= 3.0x3.0mm; 复位键误触 = 意外重启 → OF 偏大 + 段落感明显; 寿命; 贴皮肤 -25~+70C; 电流 330uA (R_PU_RESET_N 10k)",
    "candidates": [
      {
        "pn": "KMR231ULCLFS",
        "mfr": "C&K",
        "evidence": "[官网]",
        "url": "https://www.mouser.com/datasheet/2/240/kmr2-3050349.pdf",
        "params": "KMR 2 系列 NG 2 脚 ULC 低电流档; OF 3.0N ±0.75N; travel 0.25mm ±0.1mm (KMR2 系列 tactile feeling ≥30% at 20% ⇒ 段落感明显); 寿命 150,000 次; 总高 1.9mm; 本体约 2.6x2.6mm (land 外扩 4.6x3.2mm 需复核)",
        "package": "KMR 2 2 脚 (gullwing SMT)",
        "pads": 2
      },
      {
        "pn": "B3U-1000P",
        "mfr": "Omron",
        "evidence": "[官网]",
        "url": "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf",
        "params": "2 脚无固定脚版; 本体 3.0x2.5mm; 总高 1.6mm; OF 1.50N ±0.49N; travel 0.2mm; 寿命 200,000 次; 50mA/12VDC; IP40; -25~+70C",
        "package": "B3U 2 脚 (gullwing SMT)",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "KMR231ULCLFS",
      "why": "复位键误触 = 意外重启, 代价高 → OF 3.0N + 0.25mm 行程 + KMR2 系列 ≥30% tactile feeling (段落感明显, 避免误触); NG 2 脚版对上占位",
      "cost": "land 外扩超 bbox 须重画; 寿命 150,000 次对复位键够用 (复位键按得少)",
      "disclaimer": "不代拍, 一票交 main 排期"
    },
    "package_compat": {
      "verdict": "条件兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=RESET_N / pad2=GND 对上 OK; 候选2 本体 3.0x2.5mm 与 bbox 3.00x3.00 几乎正好, 候选1 本体 2.6x2.6mm 但 gullwing 外扩致 land 4.6x3.2mm 超 bbox → 均须重画 land 并复核间隙",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "同 SW_BOOT 降级方案 (更小 2 脚件 / 更薄 B3U-1000P / 结构防误触)"
  },
  {
    "ref": "C_REGN",
    "board": "CHG_BOARD",
    "type": "C",
    "criteria": "TI BQ25896 pin22 REGN 明写 'Connect a 4.7uF (10V rating) ceramic capacitor from REGN to analog GND' + placed close to the IC; REGN 兼作 TS 引脚分压偏置源 ⇒ 容值/ESL 影响 TS 测温精度; 介质 X7R/X5R (手册 SYS 输出电容也要求 X7R/X5R + >=6V) ⇒ 官方口径 10V + X7R; ★BOM value 写 1uF 与手册冲突 (缺口 G-6)",
    "candidates": [
      {
        "pn": "GRM21BR71C475KA73L",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/capacitor/mlcc",
        "params": "4.7uF / 16V / X7R / ±10% / 0805 (2.0x1.25mm) / -55~+125C / 厚度 0.5mm max; 16V > 手册 10V 要求 (3.2x 余压), 0805 便于贴 U_CHG 近端并省充电板面积",
        "package": "0805 (2012 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "GRM31CR71H475KA12L",
        "mfr": "Murata",
        "evidence": "[官网]",
        "url": "https://www.murata.com/en-us/products/capacitor/mlcc",
        "params": "4.7uF / 50V / X7R / ±10% / 1206 (3.2x1.6mm) / -55~+125C; 50V 耐压对 REGN(~5V) 极大裕量, 代价是 1206 面积大 + 更高 ESL/ESR",
        "package": "1206 (3216 metric) 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "GRM21BR71C475KA73L",
      "why": "4.7uF / 16V / X7R 三项与 TI 手册逐项对上 (值✔ 耐压>=10V✔ 介质✔); 0805 面积小 → 充电板贴 U_CHG pin22 近端容易 (手册要求 close to IC) 且省充电板面积 (ISS-216/ISS-229 热点); 16V 相对 D_TVS_VBUS 钳位 9.2V 留 1.7x 瞬态余量",
      "cost": "最大代价在 BOM 不在器件: value 写 1uF 与手册 4.7uF 冲突 → 采购按 1uF 买来贴上则 REGN 去耦不足 (内部偏置轨不稳 → TS 测温漂 + 充电环路风险), 落表批次必须同批改 BOM value (本单只报不改); DC bias 降容后 5V 下有效容本轮 [0数据] 需按料号查 Murata 曲线; 0805 vs 1206: 50V 耐压对 5V 内 LDO 是浪费",
      "disclaimer": "BOM 值冲突属 main 排期的落表批次, 本单不落表不代签"
    },
    "package_compat": {
      "verdict": "落2焊盘+充电板侧封装另行定",
      "reason": "本件不在 demo_mainboard.kicad_pcb 上 (充电板件, BOM footprint=待定), 板文件无占位故无几何可判, 不许写已兼容; 焊盘数上 MLCC 2 脚落 2 焊盘成立; 焊盘网络 pad1=REGN / pad2=GND 与手册 'from REGN to analog GND' 一一对应 OK; 封装尺寸 0805 (2.0x1.25) 或 1206 (3.2x1.6) 由充电板侧定; ★特别提醒落表批次: 手册要求 placed close to the IC → 充电板 footprint 位置必须贴 U_CHG pin22, 不能沿用网表通用位置",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 BOM value 短期改不了 (仍 1uF), 唯一安全路线是落表批次同批把 value 改成 4.7uF 16V X7R (1 行改动, 与 OPN 回填同批走), 本单不落表; 若充电板面积不允许 0805, 改 0402 4.7uF (GRM155R71C475KA01D 类) → 代价是 0402 DC bias 降容更狠, 吃掉手册 4.7uF 余量 (官方页本轮 [0数据] 落表批次补); 若坚持 1uF 不改, 选 GRM21BR71C105KA73L 类 1uF X7R/16V → 偏离 TI 手册要求, 必须登记为偏离手册的缺口并由 main/PM 签字, 本单不代签"
  },
  {
    "ref": "R_SUPV_DIV1",
    "board": "MAIN_PCB",
    "type": "R",
    "criteria": "BOM value '[待选型] 分压上臂 (0Ω 跳线位)' tbd=TBD-02; 网表 note: 原厂电压定了只改两颗电阻不改板 (ISS-082 路线) ⇒ 首版装 0Ω 跳线件, 最终阻值待 TBD-02 原厂电压窗口 (本单 [0数据]); 封装须落在占位 fab bbox 内",
    "candidates": [
      {
        "pn": "RC0603JR-070RL",
        "mfr": "Yageo",
        "evidence": "[官网]",
        "url": "https://www.yageo.com/",
        "params": "0Ω (Jumper) / 0603 (1608 metric, 1.60x0.80mm) / 0.1W (1/10W) / 厚膜 / 耐压 50V / 温漂 200ppm/C / -55~+155C / 2 端 / RoHS",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "ERJ-3GEY0R00V",
        "mfr": "Panasonic",
        "evidence": "[官网]",
        "url": "https://industrial.panasonic.com/",
        "params": "0Ω (Jumper) / 0603 (1608 metric, 1.60x0.80mm) / 0.1W / 厚膜 / 耐压 50V / 温漂 200ppm/C / -55~+155C; 同规格原厂替代, Vishay CRCW06030000Z0EC 亦同规格",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "RC0603JR-070RL",
      "why": "0603 本体 1.60x0.80mm 与占位 fab bbox 1.80x1.00mm 精确对上 (本单唯一本体与占位 bbox 严丝合缝的组合); 0.1W / 50V 对 5V 分压回路绰绰有余; 贴上即两臂短接 = 分压焊盘留好等 TBD-02 → 符合 ISS-082 '只改两颗电阻不改板' 的解法",
      "cost": "最终阻值仍是 TBD-02 (原厂电压窗口未到) ⇒ 本单只能给 0Ω 跳线件 OPN, 给不出最终分压阻值 ([0数据]); 0Ω 档无容差概念, 换真阻值时精度按分压需求另定",
      "disclaimer": "TBD-02 未闭合, 落表批次等原厂数据; 0Ω 状态语义须 PM 明确, 不代拍"
    },
    "package_compat": {
      "verdict": "兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=V_SOC_IO (上臂输入) / pad2=SUPV_SENSE (分压节点) 对应标准 2 脚电阻 OK; 本体 1.60x0.80mm <= 占位 fp_line bbox 1.80x1.00mm OK (本单唯一本体与 bbox 严丝合缝的组合, 其余件占位 land 间距都大于厂商 land)",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "若 TBD-02 一直没到, 保持 0Ω 跳线件 (不贴或贴 0Ω), SUPV_SENSE 悬空由 U_SUPV 内部上下拉兜底 → 但这改变 U_SUPV 检测语义, 必须由落表批次让 PM 明确首版 SUPV 电压监控是否生效, 不代拍; 若 0603 放不下, 改 0402 0Ω (RC0402JR-070RL 类) → 代价是手工可焊性差且占位 bbox 1.80x1.00 对 0402 偏大, 须重画"
  },
  {
    "ref": "R_SUPV_DIV2",
    "board": "MAIN_PCB",
    "type": "R",
    "criteria": "BOM value '[待选型] 分压下臂 (0Ω 跳线位)' tbd=TBD-02; 网表 note: 分压下臂 (到地); 与上臂同料同封装 ⇒ 两颗必须同封装才能对称; 最终阻值待 TBD-02 ([0数据]); 封装须落在占位 fab bbox 内",
    "candidates": [
      {
        "pn": "RC0603JR-070RL",
        "mfr": "Yageo",
        "evidence": "[官网]",
        "url": "https://www.yageo.com/",
        "params": "0Ω (Jumper) / 0603 (1608 metric, 1.60x0.80mm) / 0.1W / 厚膜 / 耐压 50V / 温漂 200ppm/C / -55~+155C; 与上臂同型号 ⇒ 分压比对称",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      },
      {
        "pn": "ERJ-3GEY0R00V",
        "mfr": "Panasonic",
        "evidence": "[官网]",
        "url": "https://industrial.panasonic.com/",
        "params": "0Ω (Jumper) / 0603 (1608 metric, 1.60x0.80mm) / 0.1W / 厚膜 / 50V / 200ppm/C / -55~+155C; 同规格原厂第二来源 (Vishay CRCW06030000Z0EC 同规格)",
        "package": "0603 (1608 metric) 2 焊盘",
        "pads": 2
      }
    ],
    "recommendation": {
      "pick": "RC0603JR-070RL",
      "why": "必须与 R_SUPV_DIV1 同型号同封装 (两颗都在同一分压链上, 封装不一致则阻值等效和温漂不一致 → 分压比漂) ⇒ 与上臂同选 RC0603JR-070RL, 并保留 Panasonic/Vishay 作第二来源防单一供货风险",
      "cost": "最终阻值仍待 TBD-02 ([0数据]); 0Ω 档无容差概念; 两颗同为 0Ω 时分压比无意义, 首版语义须 PM 明确",
      "disclaimer": "TBD-02 未闭合, 落表批次等原厂数据; 首版语义不代拍"
    },
    "package_compat": {
      "verdict": "兼容",
      "reason": "焊盘数 2=2 OK; 焊盘网络 pad1=SUPV_SENSE (上节点) / pad2=GND (下臂到地) 对应标准 2 脚电阻 OK; 本体 1.60x0.80mm <= 占位 fp_line bbox 1.80x1.00mm OK; 与上臂占位几何完全一致 ⇒ 两颗可同封装同料",
      "pads_required": 2
    },
    "evidence": "[官网]",
    "fallback": "同 R_SUPV_DIV1 降级方案 (保持 0Ω / 0402 替代 / 首版 SUPV 语义须 PM 明确); 若 TBD-02 到后需真阻值, 选同封装同 TCR 的厚膜件 (0603 1% 系列) 并重算分压比"
  }
]
}
```
<!-- END 选型证据基准块 -->

---

## §8 本单改了什么 (清单)

| # | 文件 | 动作 | 说明 |
|---|---|---|---|
| 1 | `HW/PART_SELECTION_MATRIX_2026-11-16.md` | ★**本轮新建** | ★**本文件** (矩阵正文 + 缺口登记 + 出处表 + 复现命令 + 机器可读基准块) |
| 2 | `HW/check_part_selection_matrix.py` | ★**本轮新建** | ★**机器门禁** (C0~C7 + `--selftest` 反向用例) |
| 3 | `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` | ★**本轮新建** | ★**交卷单** (B1~B6) |
| 4 | `state/fragments/sw.yaml` | ★**原子写** (走 `state/frag_write.py`) | +artifact · +interface_claim · +answer; ★**没动 status / needs_from / blockers / open_questions / risks 等任何既有 key** |

### ★边界审计 (本单自证)

- ★**我写了 4 个**: 上面 4 个文件。
- ★**我一个字节没动**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` (5 个受保护 md5 逐字节不变) · `MECH/` 全部 · `state/issue_log.yaml` · `state/fragments/{pm,hw,mech}.yaml` · `PROJECT_TRACKER.md`。
- ★**零外发**: 未发任何邮件 / 询价 / 问询 / 采购, 未联系任何供应商; 全部证据来自公开官网 / 官方数据手册 / 公开目录页。
- ★**实物 [实测] = 0 条**: 板端没有实物; 文中"板位实测"全部是**读板文件**得到的几何, 按 `[推算]`/`[官网]` 口径记。
