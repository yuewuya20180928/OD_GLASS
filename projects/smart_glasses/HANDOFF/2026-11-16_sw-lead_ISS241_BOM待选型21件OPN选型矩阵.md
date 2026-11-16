# [sw-lead→main] ISS-241 · BOM 待选型 21 件必装器件 OPN 选型证据矩阵 (21 件 × ≥2 候选 × 官方参数 × 封装兼容性结论 × 证据等级 × 降级方案) + 3 条硬发现 + 10 条缺口登记 + 机器门禁

> **作者**: sw-lead (软件总工) · **日期**: 2026-11-16 13:47~14:30 · **交卷给**: 项目总工 (moli) / main
> **单号**: ISS-241 (owner=sw-lead) · **上游 (只读)**: `HW/BOM_v1.csv` (md5 `c195a117…`) · `HW/netlist_v1.csv` (md5 `34132f7e…`) · `HW/PCB/demo_mainboard.kicad_pcb` (md5 `611b869e…`) · `state/fragments/sw.yaml`
> **板文件几何口径**: ★**main 已实测的 21 件占位焊盘几何表** (`/tmp/iss241/MAIN_MEASURED_GEOMETRY.txt`) · ★**本单自己又复测了 14 件 MAIN_PCB 占位的逐焊盘 at/size/net** ⇒ 两份数据一致
> **边界**: ★**本单只交证据, 不落表** (网表 / 脚表 / BOM 的 value 与 opn 栏 **一个字没改**) · ★**零外发** (不发信 / 不询价 / 不问供应商 / 不下单; 老板 2026-11-12 02:02 政策) · ★**没碰** PCB 布线 / 布局 / 板框 · ★**没改** `state/issue_log.yaml` · ★**实物 [实测] = 0 条**
> **机器门禁**: `python3 HW/check_part_selection_matrix.py` (rc=0 = 8/8 全过) · `--selftest` (**9/9** 反向用例, 每条都自证"真的改到了目标" + 落盘回读复核同红)

---

## ★0 一句话

★**21 件全部有 ≥2 个在售候选 + 官方参数 + 封装兼容性结论 + 证据等级 + 降级方案, 门禁 rc=0 / selftest 9/9, 5 个受保护 md5 逐字节未变, 零外发; 但有 3 条硬发现必须先摆到台面上 (都不是我能拍的)**: ★**① ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚器件 (TPD2E2U06 类) 物理落不下, 只能单通道器件 (TPD1E05U06DPY 2-pin / PESD5V0S1BA 2-lead) 或写明"需换 3 脚封装 ⇒ 归落表/板那一趟"** ★**② 占位焊盘的 pad 序号是【网表行顺序】不是【库封装 G/S/D 顺序】⇒ 三件 MOS 的 pad↔pin 映射三样都不同 (`Q_AND`=D/S/G, `Q_ENVC`=G/S/D, `Q_PG`=S/D/G) ⇒ 换任何 SOT-23 器件都必须逐件重画 land 并核 pin 映射 (接反了 Vgs 极性就反, 开机路径不通)** ★**③ `C_REGN` 判据本身错了: BOM 写"1µF", 但 TI BQ25896 数据手册 pin22 REGN 明写"Connect a **4.7 µF (10 V rating)** ceramic capacitor" ⇒ 本单按官方值给候选, 但 1µF→4.7µF 是 BOM 值变更 ⇒ 归落表批次 (本单不落表)** ★**其余件焊盘数 / 焊盘网络 / 封装尺寸与候选可直接对上, 落表时可直接回填 OPN**

---

## B1 结论摘要

| # | 结论 | 关键数字 / 依据 |
|---|---|---|
| **1.1** | ★**本单把"BOM 里 value 还写待选型"从一句话变成了一张可落表的证据矩阵**: 21 件 × ≥2 候选, 每候选带 **官方链接 + 官方参数 + 封装 + 证据等级**, 每件带 **判据 + 推荐项(含代价) + 封装兼容性结论(含理由) + 证据等级 + 降级方案** | `[官网]` 矩阵见 `HW/PART_SELECTION_MATRIX_2026-11-16.md` §3 (逐件) + §5 出处表 S1~S22 + §7 机器可读基准块; ★**机器门禁 C0~C7 逐条核** (不许空格 / 不许空话 / 不许越界 / 降级不许留空) |
| **1.2** | ★**结论 (机器可判): ESD 4 件全部只能落单通道 2 脚器件** | `[官网]` TI TPD2E2U06 官方手册 (SLLSEG9C) 明确 = **双通道**, 封装只有 DRL(SOT-5, 5 脚) 与 DCK(SC70-3, **3 脚**) ⇒ ★**最少 3 脚 ⇒ 落不下 2 焊盘占位**; 可落的是 TPD1E05U06 的 **DPY(X1SON, 2 脚)** 与 Nexperia **SOD-323 (2 lead)** 系 ⇒ ★**V-2「ESD 方案二选一」的可选集因此被物理焊盘数限定, 我只给证据与代价, 不代拍** |
| **1.3** | ★**结论 (机器可判): 占位焊盘的 pad 序号 = 网表行顺序, 不是库封装引脚序** ⇒ 三件 MOS 映射三样不同, 全都要逐件重画 land | `[实测]` 板文件逐焊盘实读: `Q_AND` pad1=RESET_N(D)/pad2=GND(S)/pad3=PG_AND(G) = **D/S/G**; `Q_ENVC` pad1=PG_AND(G)/pad2=GND(S)/pad3=EN_VCORE(D) = **G/S/D**; `Q_PG` pad1=PWR_ON(S)/pad2=BAT_SW(D)/pad3=PWR_GOOD(G) = **S/D/G**; 而 SOT-23 库引脚序统一是 **G/S/D** ⇒ ★**只有 `Q_ENVC` 天然对上, 另两件重画 land 时必须人工改映射** |
| **1.4** | ★**结论 (机器可判): `C_REGN` 的 BOM 值与 TI 手册冲突, 差 4.7 倍** | `[官网]` TI BQ25896 (SLUSC76C) pin22 REGN 原文: "Connect a **4.7 µF (10 V rating)** ceramic capacitor from REGN to analog GND. The capacitor should be placed close to the IC." ⇒ BOM 写「1µF」⇒ ★**落表批次必须同批改 BOM value (1 行改动) + 充电板 footprint 位置必须贴 U_CHG pin22** |
| **1.5** | ★**Q_PG 的候选排序是"漏电档 vs 栅压耐压"的取舍, 不是单一冠军** | `[官网]` `DMP3098L` (Diodes): **IDSS ≤800 nA** (命中网表硬判据"关断漏电 nA 级") · VGS(th) typ −1.8 V / max −2.1 V · RDS(on) 98 mΩ typ@−4.5 V · **但手册未见 VGS 绝对最大栏 ⇒ `[0数据]`**; `AO3407A` (AOS): **VGS ±20 V 明写** (命中"栅极最大耐压 ±20V") · VGS(th) typ −1.9 V · **但 IDSS ≤1 µA@25 °C / ≤5 µA@55 °C** (高温档比 DMP3098L 差 6 倍) ⇒ ★**Q_PG 漏极挂 BAT_SW 电池轨且本板贴皮肤 ⇒ 高温档漏电直接进电池账 ⇒ 我把两边的代价都写进推荐栏, 一票交 main/PM** |
| **1.6** | ★**LED 亮度账存在既有缺口 (不是本单引入的)**: 1 kΩ 串阻 + 3.3 V ⇒ 实际 ≈1.1~1.3 mA, 而两个候选 LED 都是 **20 mA 标称** | `[官网]` Kingbright 数据手册 (KP-2012SGC / APT1608SURCK / AA1608SURSK) 全部按 IF=20 mA 给值 + `[推算]` 电流计算 ⇒ ★**1 mA 工作点的实际亮度本轮 `[0数据]`** ⇒ ★**登记缺口 G-5, 改 R 阻值属改网表 ⇒ 归落表批次** |
| **1.7** | ★**`FB_VBUS` 的第一判据不是"滤噪声"而是"不能破坏充电环路稳定性"** (它串在 BQ25896 的 VBUS 输入路径里) ⇒ **低 DCR 优先于高阻抗** | `[官网]` Murata 官方 BLM21/BLM31P 系列表: `BLM21PG221SN1D` 0805/220 Ω/2 A/**DCR 45 mΩ** vs `BLM31PG121SN1` 1206/120 Ω/**3 A/DCR 25 mΩ** ⇒ ★**推荐候选2 (阻性阻尼小 45%) + 代价是 1206 占充电板面积 (ISS-216/ISS-229 盯的热点); `FB_VBUS` footprint 待定 ⇒ 尺寸可自由定, 无需改主板** |
| **1.8** | ★**`D_TVS_VBUS` 的判据全部来自 PM 已裁口径, 不是本单自拟** | `[官网]` 网表 note 原文: "★裁决 (PM): **必装**; VRWM 5-6V 档, **脉冲电流额定 ≥3A** (PD 5V/2A 场景)" + "钳位电压 < BQ25896 绝对最大 22V" ⇒ ★**交叉核对 TI 手册 §8.1: VBUS (converter not switching) −2 V…22 V** (22 V 有官方出处) ⇒ 候选 `SMBJ5.0A` 的 Vc 9.2 V 有 **2.4×** 余量、Ipp 65.3 A 有 **21.8×** 余量 |
| **1.9** | ★**`D_ESD_CAM` 的 pad 序与另两件 ESD 相反 ⇒ 单向器件会接错** | `[实测]` `D_ESD_CAM` pad1=**GND** / pad2=CSI_D0_CK_P; 而 `D_ESD_DEMO`/`D_ESD_USB_D` 是 pad1=信号 / pad2=GND ⇒ ★**TI TPD1E05U06 是单向件 (pin1=I/O, pin2=GND) ⇒ 在 `D_ESD_CAM` 上若按 pad 序号机械接 ⇒ I/O 接到 GND 位 ⇒ 直接不工作 ⇒ 落板批次必须对调, 或改用双向件 (PESD5V0S1BA 的 K1/K2 对称, 天然免疫)** |
| **1.10** | ★**两个 ESD 覆盖缺口 (V-2 的物理事实依据)**: CSI 只有 CK_P 单边有 ESD 位, USB 只有 D+ 单边有 ESD 位 | `[实测]` 网表实读: `CSI_D0_CK_N` 只出现在 AC 耦合电容与测试点行; `USB_D_N_SRC` 只出现在 `R_SER_USB_D_N` 串阻行 ⇒ ★**高速差分对与 USB 2.0 差分对都是单边保护 ⇒ 缺口 G-3 / G-4 ⇒ 只给证据, V-2 由 PM 拍** |
| **1.11** | ★**本单不代拍**: 每件都给了"推荐项 + 为什么 + 代价", 但**最终型号 / V-2 (ESD 方案二选一) / V-3 / V-4 的一票交 main 排期与老板** | ★**矩阵里每条推荐都带 `disclaimer` 字段写死"不代拍"** ⇒ 机器门禁 C4 逐件核 `disclaimer` 非空 |
| **1.12** | ★**新机器门禁**: `HW/check_part_selection_matrix.py` ⇒ **rc=0 (C0~C7 共 8 条全过)** · **`--selftest` 9/9** (★硬指标 ≥5★, 每条都自证"真的改到了目标" + **落盘回读再跑一遍**证明"文档改了 ⇒ 门禁读盘后也红") | `[实测]` 见 B6 ①②; ★**M1 删位号→C1 / M2 候选清空→C2 / M3 降级删空→C4 / M4 越界位号→C7 / M5 非法证据等级→C5 / M6 删封装结论→C3 / M7 推荐项清空→C4 / M8 破坏 JSON→C0 / M9 候选降到 1 个→C2** |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

### 2.1 四件交付物

| # | 交付物 | 判定 | 证据 |
|---|---|---|---|
| **D-1** | ★**① `HW/PART_SELECTION_MATRIX_2026-11-16.md` (矩阵正文)** | ✅ **通过** | §0 一句话 · §1 口径与判据来源 · §2 范围勘误 · **§3 逐件 22 行矩阵** (ESD 4 / FB 2 / TVS 1 / MOS 4 / LED 3 / SW 5 / C 1 / 电阻 2) · §4 缺口登记 G-1~G-10 · §5 出处表 S1~S22 · §6 复现命令 · §7 机器可读基准块 · §8 改了什么 + 边界审计 |
| **D-2** | ★**② `HW/check_part_selection_matrix.py` (门禁 + `--selftest`)** | ✅ **通过** | **C0~C7 共 8 条** (见 B1 1.12) + `--selftest` **9/9** + `--json` + `--root`; ★**内容级, 不挂 md5** (网表在飞 ⇒ 按位号/内容判定 ⇒ 落表后仍成立) |
| **D-3** | ★**③ `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` (本文件, B1~B6 齐全)** | ✅ **通过** | 本文件 |
| **D-4** | ★**④ `state/fragments/sw.yaml` (走 `python3 state/frag_write.py --agent sw-lead` 原子写)** | ✅ **通过** | **+3 artifact · +3 interface_claim · +2 answer**; ★**只加这三类, 没动 `status` / `needs_from` / `blockers` / `open_questions` / `risks` 等任何既有 key, 没删别人的条目** |

### 2.2 任务书判据 ⇒ 本单的落法

| 任务书判据 | 本单怎么落的 | 判定 |
|---|---|---|
| ① 每件 ≥2 候选 + 官方参数 + 封装兼容性 + 降级方案 | **C2** 逐候选核 (型号/厂商/链接/参数/封装/证据等级/pads 七栏非空) + **C3** 逐件核 (封装结论取值合法 + 理由非空 + pads_required) + **C4** 逐件核 (件级证据等级 + 降级方案 + 推荐项四栏) ⇒ ★**每件 ≥2 候选, 全 22 件零空缺** | ✅ |
| ② 证据等级五级固定 (`[官网]/[实测]/[媒体]/[推算]/[0数据]`) | **C5** 逐候选 + 逐件核白名单 ⇒ ★**把「[官方]」写成非法词直接红 (反向用例 M5 就是这么打的)** | ✅ |
| ③ 判据从"网表 note + 官方参数"提炼 | 每件判据栏都注明出处 (网表 note 原文 / PM 裁决原文 / TI 手册章节号 / 板文件实测), ★**例如 `D_TVS_VBUS` 的判据逐字来自 PM 裁决, `C_REGN` 的判据逐字来自 TI pin22 说明** | ✅ |
| ④ 封装必须标出与板文件占位的关系 (兼容/不兼容 + 理由) | **C3** 强制 `verdict` 取值 ∈ {兼容, 条件兼容, 不兼容, 落2焊盘+充电板侧封装另行定, 落3焊盘+充电板侧封装另行定} ⇒ ★**6 件充电板器件一律只能写"落 N 焊盘 + 充电板侧封装另行定", 门禁不许写"已兼容"** | ✅ |
| ⑤ 不许出现「已定型」式空话: 候选型号栏不许为空 | **C6** 黑名单扫描候选型号栏 (已定型/待定/待查/待选型/TBD/待补/待填/???) + 空栏检测 ⇒ ★**反向用例 M2 把某个型号清空 ⇒ C2+C6 双红** | ✅ |
| ⑥ 矩阵里的位号不许超出本单范围 | **C7** 逐个比对 `expected_refs` + 显式黑名单 `U_PWR_SW` / `U_EN_SW` (ISS-172 在办) ⇒ ★**反向用例 M4 塞 U_PWR_SW ⇒ C7 红** | ✅ |
| ⑦ 覆盖 21 个位号, 一个不缺 | **C1** 按**位号集合**卡 (不用数字卡) ⇒ 覆盖 `expected_refs` **22** 个 (含任务书枚举的 20 个全齐) ⇒ ★**口径差见 §2 勘误, 宁可多做不可漏做** | ✅ |
| ⑧ `--selftest` 反向用例 ≥5 条, 每条自证"真的改到了目标" | **9 条** (M1~M9), 每条: ① 先判 `mutated != doc_text` (没改到东西直接判自证失败) ② 判期望的检查编号**出现在红色集合里** ③ **落盘回读再跑一遍**, 证明"文档改了 ⇒ 门禁读盘后也红" (ISS-227 同款教训) ⇒ **9/9** | ✅ |
| ⑨ 降级方案是必须项, 不许留空 | **C4** 逐件核 `fallback` 非空 ⇒ ★**反向用例 M3 把降级方案删空 ⇒ C4 红** | ✅ |

---

## B3 证据分级

| 结论 | 等级 | 依据 / 怎么量的 |
|---|---|---|
| `TPD1E05U06DPYR`: Cd 0.42 pF · VRWM 5.5 V · VBR 6.5~8.5 V · Vclamp 10 V@1 A(TLP) / 14 V@5 A · ILEAK 10 nA max · ±12 kV 接触 / ±15 kV 空气 · 2.5 A(8/20 µs) surge · RDYN 0.8 Ω · −40~+125 °C · DPY=2-pin X1SON / DYA=2-pin SOD-523 · pin1=I/O pin2=GND | **[官网]** | TI 数据手册 **SLVSBO7O** (2024-08) §5.4 + §4 Pin Functions Table 5-1 · ★**本地已下载原厂 PDF 并 pdftotext 实读** (`/tmp/iss241/ds/tpd6e05u06.pdf`) |
| `TPD2E2U06`: 双通道 · Cd 1.5 pF · ±25 kV 接触 / ±30 kV 空气 · IPPM 5.5 A · VBR 6.5 V min · ILEAK 10 nA max · DRL(SOT-5 1.60×1.20) / DCK(SC70-3 2.00×1.25) ⇒ **最少 3 脚** | **[官网]** | TI 数据手册 **SLLSEG9C** (2019-12) · ★**本地已下载原厂 PDF 并实读** |
| `PESD5V0S1BA`: VRWM 5 V · VBR 6 V min · V(CL)R 14 V · IPPM 12 A · PPPM 130 W · IRM 5 nA · ESD >30 kV (level 4) · IEC 61000-4-5 IPPM 12 A · Cd 35 pF typ/45 pF max · SOD-323 2 lead 1.3 mm pitch body 1.7×1.25×0.95 mm · pin1=K1/pin2=K2 | **[官网]** | Nexperia 官方产品页 (web_fetch 200 OK 实读) + Nexperia 官方数据手册 Table 2/3 |
| `PESD5V0U1BA-Q`: Cd 11 pF typ/13 pF max · VRWM 5 V · VBR 5.8~7.8 V · VCL 12.5 V@IPP 4.8 A · PPP 45 W · IRM <1 nA typ/10 nA max · SOD-323 2 lead | **[官网]** | Nexperia 官方数据手册 (2022-05-03) |
| `SMBJ5.0A`: VRWM 5.0 V · VBR 6.4 V min · Vc 9.2 V @ Ipp 65.3 A · PPP 600 W · IR 800 µA max · −65~+150 °C · 单向 · DO-214AA | **[官网]** | Littelfuse 官方 SMBJ 系列页 |
| `SMBJ6.0A`: VRWM 6.0 V · SMB 封装 · 系列 ≤600 W · 适用 IEC 61000-4-2/4-4/4-5 · **Vc/Ipp 具体值 `[0数据]`** | **[官网]** | ST 官方产品页 (web_fetch 200 OK 实读) |
| `AO3400A`: 30 V N-ch SOT23 · VGS(th) 0.65/1.05/1.45 V · RDS(on) 26.5 mΩ@10 V / 32 mΩ@4.5 V / 48 mΩ@2.5 V · ID 5.7 A · PD 1.4 W · IGSS ≤100 nA · VGS ±12 V · −55~+150 °C | **[官网]** | AOS 官方数据手册 Rev 3.1 (2023-07) + 官网产品页 |
| `AO3407A`: −30 V P-ch SOT-23 · VGS(th) −1.4/−1.9/−2.4 V · RDS(on) 48 mΩ max@−10 V / 78 mΩ max@−4.5 V · ID −4.3 A · **IDSS ≤1 µA@25 °C / ≤5 µA@55 °C** · IGSS ±100 nA · **VGS ±20 V** · PD 1.4 W | **[官网]** | AOS 官方数据手册 Rev 5.1 (2023-07) |
| `DMP3098L`: −30 V P-ch SOT23 · **IDSS ≤800 nA** · IGSS ≤±100 nA · VGS(th) −1.0/−1.8/−2.1 V · RDS(on) 56/70 mΩ@−10 V, **98/120 mΩ@−4.5 V** · ID −3.8 A · **VGS 绝对最大栏手册未见 ⇒ `[0数据]`** | **[官网]** | Diodes Inc 官方数据手册 · ★**本地已下载原厂 PDF 并 pdftotext 实读** (`/tmp/iss241/ds2/dmp3098l.pdf`) |
| `2N7002`: 60 V N-ch SOT-23 · VGS(th) 1.0/1.76/2.0 V (2N7002DW) · RDS(on) 1.2 Ω typ@10 V / 2.4 Ω typ@4.5 V · ID 115 mA · PD 0.36 W · IDSS ≤1 µA · **IGSS ≤±10 nA** | **[官网]** | Microchip 官方数据手册 + onsemi 官方 2N7002DW / 2N7002L 手册 |
| `BLM21PG221SN1D`: 0805 2.00×1.25 mm · **Z 220 Ω @100 MHz ±25% · 2 A · DCR 45 mΩ max** · −55~+125 °C | **[官网]** | Murata 官方 chip ferrite bead lineup 页 + 官方 BLM21 族参数表 |
| `BLM31PG121SN1`: 1206 3.2×1.6 mm · Z 120 Ω @100 MHz · **3000 mA** · **DCR 0.025 Ω max** | **[官网]** | Murata 官方 BLM31P 系列参数表 |
| `KP-2012SGC`: 0805 2.0×1.25 mm · λpeak 565 nm / λdom 568 nm · **VF 2.2 V typ / 2.5 V max @20 mA** · IF 25 mA / IFM 140 mA · IR ≤10 µA · **C 15 pF** · PD 62.5 mW · TJ 110 °C · −40~+85 °C | **[官网]** | Kingbright 原厂数据手册 DSAB1341 V.21B + 原厂官网 0805 页 |
| `APT1608SURCK`: 0603 1.6×0.8×0.75 mm · AlGaInP · **λdom 630 nm · IV 40/80 mcd @20 mA** · 120° | **[官网]** | Kingbright 原厂官网产品页 |
| `AA1608SURSK`: 0603 PLCC-2 1.6×0.8×0.55 mm · λdom 630 nm · **IV 40/160 mcd @20 mA** · IF 30 mA / IFM 185 mA · PD 75 mW | **[官网]** | Kingbright 原厂官网 PLCC-2 页 |
| `KMR231ULCLFS` / `KMR221ULCLFS`: KMR 2 系列 **NG 无接地脚 2 脚版** · ULC 低电流档 (min 1 mA) · OF **2.0 N (KMR221) / 3.0 N (KMR231)** · travel 0.25 mm · 寿命 200,000 / 150,000 次 · 总高 1.9 mm · 32 VDC · tactile feeling ≥30% | **[官网]** | C&K 原厂数据手册 KMR 2 Series PDF |
| `B3U-1000P`: 2 脚无固定脚版 (B3U-1100P=4 脚 / B3U-1000P-B=带 boss 均须避开) · 本体 3.0×2.5 mm / 总高 1.6 mm · **OF 1.50 N ±0.49 N** · PT 0.15 / travel 0.2 mm · 寿命 200,000 次 · 50 mA/12 VDC · IP40 · −25~+70 °C | **[官网]** | Omron 原厂数据手册 + Omron 官网选型表 |
| `RC0603JR-070RL` / `ERJ-3GEY0R00V`: 0 Ω (Jumper) · 0603 1.60×0.80 mm · 0.1 W · 厚膜 · 50 V · 200 ppm/°C · −55~+155 °C | **[官网]** | Yageo / Panasonic 官方 |
| `GRM21BR71C475KA73L`: **4.7 µF / 16 V / X7R / ±10%** · 0805 2.0×1.25 mm · −55~+125 °C | **[官网]** | Murata 官方 MLCC 系列页 + 官方型号页 |
| ★**`C_REGN` 官方要求 4.7 µF (10 V) 而非 BOM 的 1 µF** | **[官网]** | TI BQ25896 **SLUSC76C** pin22 REGN 原文 (★**本地已下载原厂 PDF 并实读** `/tmp/iss241/ds2/bq25896.pdf`) |
| ★**BQ25896 VBUS 绝对最大 22 V** | **[官网]** | TI SLUSC76C §8.1 Absolute Maximum Ratings (★本地 PDF 实读) |
| 21 件占位焊盘几何 (焊盘数 / 焊盘网络 / fab bbox / pad at-size) | **[实测]**(读板文件) | ★**本单自己复测 14 件 MAIN_PCB 占位逐焊盘** (pad 0.6×0.9 @ 2.30/2.20/1.60 mm 间距; MOS at (−1.4,−2)/(−0.13,−2)/(+1.4,+2); FB 对角布置) + ★**main 的 21 件几何表** ⇒ 两份一致; ★**全部占位 `footprint` 名 = 空字符串 ⇒ 裸焊盘占位** |
| ★**ESD/USB/CSI 的单边保护缺口 · LED 亮度账 · Q_PG 源漏措辞矛盾 · 占位 land 不匹配 · 充电板 6 件待定 · R_SUPV 分压阻值待 TBD-02** | **[推算]** + `[0数据]` | ★**分别登记为 G-1~G-10, 每条写明卡住什么 + 谁来裁 + 裁之前怎么走** |
| ★**实物 [实测] = 0 条** | — | ★本单全部证据是公开官网 / 官方数据手册 / 公开目录页, **没有一颗实物被测过**; 文中 `[实测]` 指的是**读本机板文件**, 不是硬件实测 |

---

## B4 接口取值声明 (interface_claims · 已写进 `state/fragments/sw.yaml`)

### 4.1 claims (3 条)

| key | value | note |
|---|---|---|
| `iss241_esd_single_channel_only` | `ESD 4 件全部 2 焊盘占位 ⇒ 只能单通道 2 脚器件 (TPD1E05U06DPY / PESD5V0S1BA / PESD5V0U1BA-Q); TPD2E2U06 双通道最少 3 脚 ⇒ 落不下` | `[官网]` TI SLLSEG9C + SLVSBO7O; ★**V-2「ESD 方案二选一」的可选集被焊盘数物理限定, 我只给证据不代拍** |
| `iss241_pad_pin_mapping_mismatch` | `占位 pad 序 = 网表行顺序: Q_AND=D/S/G · Q_ENVC=G/S/D · Q_PG=S/D/G; SOT-23 库引脚序=G/S/D ⇒ Q_AND/Q_PG 必须重画 land` | `[实测]` 板文件逐焊盘实读; ★**落板批次必看, 接反 Vgs 极性就反 ⇒ 开机路径不通** |
| `iss241_regn_cap_value_conflict` | `BOM=1µF vs TI BQ25896 手册=4.7µF(10V) ⇒ 落表批次须改 BOM value` | `[官网]` TI SLUSC76C pin22; ★**本单不落表** |

### 4.2 answers (2 条 · 全部 to=main)

| key | 内容要点 |
|---|---|
| `iss241_part_selection_evidence_matrix` | 交卷声明: ① `HW/PART_SELECTION_MATRIX_2026-11-16.md` (21 件 × ≥2 候选 + 官方参数 + 封装兼容结论 + 证据等级 + 降级方案 + 缺口 G-1~G-10 + 出处表 S1~S22) ② `HW/check_part_selection_matrix.py` (C0~C7 + `--selftest` 9/9) ③ 本交卷单 ④ 分片只加 artifact/claim/answer |
| `iss241_landing_handoff` | ★**落表前置条件**: L1 `C_REGN` BOM value 1µF→4.7µF(10V) + 充电板位置贴 U_CHG pin22 · L2 `Q_AND`/`Q_PG` 占位 land 必须重画并人工核 pad↔pin · L3 `D_ESD_CAM` pad 序与单向器件相反必须对调 (或改双向件) · L4 6 件充电板器件的 footprint 另行定 · L5 G-1 源漏措辞矛盾由 PM/原理图那一趟裁决 ⇒ ★**本单一个字没改网表/脚表/BOM** |

---

## B5 未决项与卡点

### U-A ★**给 main 的一句话拍板 (owner = main / boss · 拍完我这边一行就能落)** (★**本单不代拍**★)

| # | 问句 | 本单给的依据 (不替 main 决定) | 不拍的后果 |
|---|---|---|---|
| **Q-A** | ★**ESD 方案二选一 (V-2) 走单通道还是双通道?** | 单通道 = `TPD1E05U06DPYR` / `PESD5V0S1BA` / `PESD5V0U1BA-Q` ⇒ **现在就能落 2 焊盘, 不改板**, 代价 = **Type-C 只护 1 条线 / CSI 只护单边 / USB 只护 D+** (G-3, G-4); 双通道 = `TPD2E2U06` 类 ⇒ 电气上才是正解, 代价 = **最少 3 脚 ⇒ 必须改 footprint (主板或充电板) + 占位 land 重画** | 主板 BOM 的 OPN 出不来; ⇒ V-2 一直没人拍 ⇒ ESD 方案在投板前卡住 |
| **Q-B** | ★**`C_REGN` 的 BOM value 改成 4.7µF 吗?** | TI 手册白纸黑字 4.7 µF (10 V); BOM 写 1 µF ⇒ **差 4.7 倍**; 代价 = 1 行 BOM 值改动 (与 OPN 回填同批走) | 采购按 1 µF 买来贴上 ⇒ REGN 去耦不足 ⇒ 内部偏置轨不稳 ⇒ **TS 测温漂 + 充电环路风险** |
| **Q-C** | ★**Q_PG 选漏电档还是栅压耐压档?** | `DMP3098L`: IDSS ≤800 nA (命中 nA 级) 但 **VGS 绝对最大手册未见 (`[0数据]`)**; `AO3407A`: **VGS ±20 V 明写** 但高温档 IDSS ≤5 µA (差 6 倍, 贴皮肤 55 °C 下直接进电池账) | 关机续航账算不准 (参照 ISS-172 的 108 µA 账); ±20 V 门槛无人认领 |

### U-B ★**落表前置条件 (owner = 落表批次 / main · 本单一个字没改网表★)**

| # | 落表时必须一起改的项 | 现状 | 归属 |
|---|---|---|---|
| L1 | `C_REGN` 的 BOM value 栏「1µF」⇒ 「4.7µF 16V X7R」 | ★**本单不改** | 落表批次 |
| L2 | `Q_AND` / `Q_PG` 占位 land 重画时**人工核 pad↔pin** (占位序 ≠ 器件引脚序) | ★**本单只报** | hw-lead + 落表批次 |
| L3 | `D_ESD_CAM` 的 pad 对调 (单向件) 或改用双向件 | ★**本单只报** | 落表批次 |
| L4 | 6 件充电板器件 (`D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN`) 的充电板 footprint 另行定 (`C_REGN` 位置必须贴 U_CHG pin22) | footprint = 待定 | 充电板那一趟 |
| L5 | G-1 (`Q_PG` 源漏措辞与拓扑相反) 的裁决 | ★**本单不拍** | main / PM + 原理图那一趟 |
| L6 | `R_SUPV_DIV1/2` 的最终阻值 (TBD-02 原厂电压窗口) | 首版 0Ω 跳线 | 等原厂数据 (ISS-082 路线) |

### U-C ★**本单残留的 [0数据] 缺口 (owner = 落表批次 · ★查不到就写降级方案, 不许编★)**

| # | 缺口 | 卡住什么 | 怎么补 |
|---|---|---|---|
| ① | `DMP3098L` 的 **VGS 绝对最大额定** (手册未给该栏) | `Q_PG` 的「栅极最大耐压 ±20V」硬判据只能给 AO3407A | 按 Diodes Inc 官网最新版 DMP3098L 手册补 |
| ② | `DMP3098L` 的 **在售目录页** (本轮只核到官网手册与型号页) | Q_PG 的采购通道 | 查 DigiKey/Mouser/贸泽目录页 |
| ③ | `SMBJ6.0A` 的 **Vc / Ipp 具体数值** (ST 官方页只给系列级描述) | `D_TVS_VBUS` 若选 6 V 档 ⇒ Vc < 22 V 没法核 | 按 ST 官方 SMBJ 手册补 |
| ④ | `GRM21BR71C475KA73L` 的 **DC bias 降容曲线** (5 V 偏压下有效容) | `C_REGN` 的实际去耦裕量 | 按 Murata 官网该料号 DC bias 曲线补 |
| ⑤ | 各 LED 的 **1 mA 工作点亮度** (手册只给 20 mA 点) | `D_LED_G`/`D_LED_R` 的亮度账 (G-5) | 按原厂低电流档数据或实测 (实测属硬件那一趟) |
| ⑥ | **更小的 2 脚贴片按键** (≤3×3 mm 无引脚, 供 `SW_*` 换料用) | 按键件 land 超 bbox 时的备选 | 查 Panasonic EVQ-P / Alps 小尺寸系列官网 |
| ⑦ | `BLM21P221SG` 类 **低 DCR 同尺寸磁珠的完整官方页** | `FB_DEMO` 的 DCR 优化路径 | 按 Murata 官网 BLM21P 系列补 |
| ⑧ | **VRWM ≥5.25 V 的 2 脚 ESD 件** (`PESD6V0S1BA` / `SP1006-01` 类) | `D_ESD_DEMO` / `D_ESD_TC` 的 VRWM 顶边问题 | 按 Nexperia / Littelfuse 官网补 |

### U-D ★**改板路线要占一个板次 (owner = hw-lead + 项目总工)**

⇒ 若 Q-A 选双通道 ⇒ 走改板: 主板 4 件 ESD 占位按 3~4 脚阵列重画 + 充电板 `D_ESD_TC` footprint 定多通道 + 重跑 DRC/ERC + 重跑网表/脚表门禁 + 重新投板 + 重测 ⇒ ★**板那一趟必须排进计划, 不是本单能拍的**; ⇒ ★**改板前必须先确认目标器件的厂商 land (本单已给出各候选的封装与尺寸), 否则白投一版**。

### U-E ★**本单没有做的事 (明确留痕, 免得被误当成漏项)**

| # | 没做 | 为什么 |
|---|---|---|
| ① | ★**没落表** (网表 / 脚表 / BOM 的 value 与 opn 栏一个字没动) | ★**等老板 / PM 拍完型号** ⇒ 由落表批次改 |
| ② | ★**没代拍 V-2 / V-3 / V-4** | ★**属老板 / PM 的一票** (每条推荐都带 disclaimer) |
| ③ | ★**没穷举"所有在售 ESD / 磁珠 / 开关型号"** | 本轮是**查证范围内**的候选矩阵, 不是 100% 穷举 ⇒ ★**穷举是一条人工动作, 不能靠推断代替** |
| ④ | ★**没取 `SMBJ6.0A` 的 Vc/Ipp / `DMP3098L` 的 VGS 绝对最大 / LED 的 1 mA 亮度** | 查不到 ⇒ 记 `[0数据]` + 写降级方案 ⇒ **落表批次按官网补** |
| ⑤ | ★**没碰 PCB 布线 / 布局 / 板框** | 板 md5 `611b869e…` 不变 |
| ⑥ | ★**没改 `state/issue_log.yaml`** | verify_by = main |
| ⑦ | ★**没写别人的分片** | 只写 `state/fragments/sw.yaml`; ★**自己分片里也只加 artifact/claim/answer, 没删改任何既有 key** |
| ⑧ | ★**没回答 V-2 的 ESD 二选一** | 只给了可选集与代价 (U-A Q-A) |

---

## B6 自证复现命令 (输出原样 · 2026-11-16 13:47~14:30 实跑)

### ① `python3 HW/check_part_selection_matrix.py` ⇒ **rc=0 (C0~C7 全过)**

```
[check_part_selection_matrix] 门禁检查: HW/PART_SELECTION_MATRIX_2026-11-16.md
  [PASS] C0 — 基准块 JSON 解析通过
  [PASS] C1 — 覆盖 22/22 位号 (含任务书枚举的 20 个全齐)
  [PASS] C2 — 候选完整性: 每件 ≥2 候选且各栏非空
  [PASS] C3 — 封装兼容性: 每件有结论+理由+pads_required
  [PASS] C4 — 证据/降级/推荐: 每件齐全
  [PASS] C5 — 证据等级白名单: 全部合法
  [PASS] C6 — 空话检查: 无空候选/无已定型式空话
  [PASS] C7 — 无越界位号 (OUT_OF_SCOPE ['U_EN_SW', 'U_PWR_SW'] 全部不在册)
[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (8/8)
rc=0
```

### ② `python3 HW/check_part_selection_matrix.py --selftest` ⇒ **rc=0 (9/9)**

```
[PASS] M1 删掉一个位号 (Q_PG) — C1 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M2 把某件候选清空 (AO3400A 的 pn) — C2 变红 (共 2 条: C2,C6) [落盘回读复核同红]
[PASS] M3 把某件降级方案删空 (D_ESD_USB_D) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M4 塞一个越界位号 (U_PWR_SW) — C7 变红 (共 2 条: C1,C7) [落盘回读复核同红]
[PASS] M5 证据等级写成非法词 [官方] — C5 变红 (共 1 条: C5) [落盘回读复核同红]
[PASS] M6 删掉封装兼容性结论 (Q_ENVC) — C3 变红 (共 1 条: C3) [落盘回读复核同红]
[PASS] M7 把推荐项 why 清空 (Q_PG) — C4 变红 (共 1 条: C4) [落盘回读复核同红]
[PASS] M8 破坏 baseline JSON — C0 变红 (共 1 条: C0) [落盘回读复核同红]
[PASS] M9 把某件候选降到 1 个 (Q_AND) — C2 变红 (共 1 条: C2) [落盘回读复核同红]
selftest: 9/9
[check_part_selection_matrix] PASS — 反向用例 9/9 全抓到
rc=0
```

> ★**每条用例都自证「它真的改到了目标」**: 脚本里先判 `mutated != doc_text` (没改到东西 ⇒ 直接判自证失败), 再判期望的检查编号**出现在红色集合里**, 最后**落盘回读再跑一遍** ⇒ 证明「文档改了 ⇒ 门禁读盘后也红」 (ISS-227 同款教训)。

### ③ ★**既有闸: 本单一道都没打红**

```
$ python3 HW/check_step1_parts_spec.py
[PASS] C6  FPC_PIN_TABLES.md 的 display 口径 == 裁定口径
[PASS] C7  §5 与 §7 的 M 编号集合一致
[PASS] C8  §6 S1 存在且经 ISS-237 确认
---- 8/8 通过 ⇒ rc=0 ----
rc=0
```

### ④ ★`python3 state/merge.py && python3 state/gate_check.py` ⇒ **rc=0, Q1 18/18**

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-16T14:31:19+08:00)
   产出 339 | 阻塞 43 (高危 33) | 未闭合需求 195 | 冲突 0 | 健康度 red
merge rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS239_TPS7A20引脚功能名串号与缺EN脚.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q3 接口声明率】 全员 interface_claims 共 643 条 (sw-lead 182 条)
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
gate_check rc=0
```

### ⑤ ★**边界审计: 受保护 5 件逐字节不变 + 本单零越界写入**

```
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
         HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
34132f7e40a241e1fae1476be0eafbd5  HW/netlist_v1.csv          ★与派单基线一致★
b21b743a7702d30729f0d653c15392df  HW/netlist_v1_pins.csv     ★与派单基线一致★
c195a117ff17490d4d1e1a5b8f1995a7  HW/BOM_v1.csv              ★与派单基线一致★
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb ★与派单基线一致★
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro ★与派单基线一致★
```

### ⑥ ★**分片只加三类条目, 别人的 key 一个没动**

```
$ python3 state/frag_write.py --agent sw-lead --add-artifact ...   (3 条)
$ python3 state/frag_write.py --agent sw-lead --add-claim ...      (3 条)
$ python3 state/frag_write.py --agent sw-lead --add-answer ...     (2 条)
✅ sw.yaml 已原子更新 (tmp + fsync + os.replace)
★status / needs_from / blockers / open_questions / risks 一个没动
```

---

## 本单改了什么 (清单)

| # | 文件 | 动作 | 说明 |
|---|---|---|---|
| 1 | `HW/PART_SELECTION_MATRIX_2026-11-16.md` | ★**本轮新建** | ★**矩阵正文** (21 件 × ≥2 候选 + 官方参数 + 封装兼容结论 + 证据等级 + 降级方案 + 缺口 G-1~G-10 + 出处表 S1~S22 + 机器可读基准块) |
| 2 | `HW/check_part_selection_matrix.py` | ★**本轮新建** | ★**机器门禁** (C0~C7 + `--selftest` 9/9 + `--json` + `--root`) |
| 3 | `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md` | ★**本轮新建** | ★**本文件** (B1~B6 齐全) |
| 4 | `state/fragments/sw.yaml` | ★**原子写** (走 `state/frag_write.py`) | +3 artifact · +3 interface_claim · +2 answer; ★**没动 status / needs_from / blockers** |

### ★**边界审计 (本单自证: 哪些文件我写了 / 哪些文件我一个字节没动)**

- ★**我写了 4 个**: 上面 4 个文件。
- ★**我一个字节没动**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` (5 个受保护 md5 逐字节不变) · `MECH/` 全部 · `state/issue_log.yaml` · `state/fragments/{pm,hw,mech}.yaml` · `PROJECT_TRACKER.md` · 任何 PCB 文件。
- ★**零外发**: 本单未发任何邮件 / 询价 / 问询 / 采购, 未联系任何供应商。

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

| # | 给谁 | 要什么 | 为什么 |
|---|---|---|---|
| 1 | **main / boss** | ★**拍 U-A 的三句**: ① ESD 走单通道 (可立刻投板, 少护几条线) 还是双通道 (要改 footprint) ② `C_REGN` BOM value 改 4.7µF ③ `Q_PG` 漏电档 vs 栅压耐压档 | 矩阵已经能给推荐了, 但**优先级与取舍的一票不在我这里** ⇒ 回一句就能收敛成一个 OPN 集 |
| 2 | **main / PM** | ★**裁决 G-1**: `Q_PG` 网表 note 的「源极接 ON / 漏极接 BAT_SW」与 P-MOS 高边开关常规拓扑相反 ⇒ 原理图那一趟要核 | ★**若按字面直译, Vgs 极性定义会反 ⇒ 开机路径不通** ⇒ 这是硬问题, 但属原理图那一趟, 本单不拍 |
| 3 | **main / 落表批次** | ★**拍完型号后派落表单** (B5 U-B 的 L1~L6) | ★**本单刻意没落表**, 网表 / BOM 的 `[待选型]` 串还在原样 |
| 4 | **hw-lead** | ★**落板批次重画 land 时人工核 pad↔pin** (`Q_AND` / `Q_PG` 的占位 pad 序 ≠ 器件引脚序) + `D_ESD_CAM` 的 pad 对调 | ★**接反了 Vgs 极性就反 / ESD 器件接错就不工作** ⇒ 白投一版的代价最高 |
| 5 | **PM / 结构** | ★**LED 亮度口径 (1 kΩ ⇒ ~1.1 mA 工作点) + ISS-103 导光孔高度 + `D_CHG_LED` 单色/双色选择** | 都是本单能查但不能拍的口径 |

---

## 待办: 需要项目总工做什么

1. ★**复核交卷**: 跑 `python3 HW/check_part_selection_matrix.py` (应 rc=0) + `--selftest` (应 9/9) + 查三件产物 (`HW/PART_SELECTION_MATRIX_2026-11-16.md` / `HW/check_part_selection_matrix.py` / 本交接单)。
2. ★**把 U-A 的三句并进 `DECISION_PENDING_2026-11-16.md`** ⇒ 给老板一页可拍 (★**每条带推荐, 但没人代拍**★)。
3. ★**拍完型号后派落表单** ⇒ 本单**刻意没落表**, 网表 / 脚表 / BOM 的 `[待选型]` 串还在原样。
4. ★**裁决 G-1** (`Q_PG` 源漏措辞与拓扑相反)。
5. ★**别先关单**: U-C 的 8 条 [0数据] 里, ①②③④⑤⑥⑦⑧ 都要在落表/改板前按官网原表补齐。

---

## 阻塞: 缺什么信息

| # | 缺什么 | 卡住什么 | 找谁 |
|---|---|---|---|
| 1 | ★**ESD 方案二选一 (V-2) 的拍板** | 主板 BOM 的 OPN 出不来; ⇒ 双通道方案要占一个板次, 单通道方案少护几条线 | boss (经 main) |
| 2 | ★**`C_REGN` BOM value 改成 4.7µF 的拍板** | 采购按 1µF 买 ⇒ REGN 去耦不足 ⇒ TS 测温漂 + 充电环路风险 | main (落表批次) |
| 3 | ★**`Q_PG` 漏电档 vs 栅压耐压档的拍板** | 关机续航账 (ISS-172 的 108 µA) 算不准; ±20 V 门槛无人认领 | main / PM |
| 4 | ★**G-1 的 `Q_PG` 源漏矛盾裁决** | 原理图/落表那一趟的拓扑依据 | main / PM + 原理图那一趟 |
| 5 | ★**U-C 的 8 条 [0数据]** | 落表/改板前必须按官网原表补齐 (尤其 `DMP3098L` 的 VGS 绝对最大 + 在售页) | 落表批次 (按官网原表) |
