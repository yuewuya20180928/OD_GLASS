# HW/NETLIST_REV2_SPEC.md —— 网表改版规格 (按真实器件, ISS-162)

| 项 | 内容 |
|---|---|
| 触发 | 老板 2026-11-02 22:37「**必须得硬件自己画图**」+ 19:29 判据收敛 + ISS-158 三件选型结果 |
| 目的 | ★**把网表从"按早期假设的器件"改成"按真实在售器件"** ⇒ 主板的 FPC 座/供电树/GPIO 才画得对 ⇒ ⇒ **这是板子能投的唯一前提** |
| ★**执行纪律** | ★**本规格已包含全部事实与针位表 —— 执行时【不许再查任何资料、不许再问器件】**; 只做"照抄改网表 + 跑命令 + 重出板子" |
| 真源 | `state/gen_netlist.py` + `HW/SCHEMATIC_V1_SPEC.json` ⇒ ★**不要手改 `HW/netlist_v1.csv` (生成物)** |
| 器件依据 | `HW/STEP1_PARTS_SPEC.md` (ISS-158, 已验收) · `HW/PCB/FET3576C_PIN_TABLE.csv` (399 行逐针表) · `HW/PCB/panel_simple_dsi_template.dtsi` (面板 init) |

---

## 0. ★★ 三个必须先知道的结论（会改电源树）

### ① ★ camera 模组是**模组级供电**，不是 sensor 芯片级三轨
Radxa Camera 4K 的 31 针里 **pin28/29 = VCC3.3V, pin30/31 = VCC5V** ⇒ **模组内部自己稳压** ⇒
⇒ ★★**主板的 `SENSOR_CORE` / `SENSOR_VDD_IO` / `SENSOR_AVDD` 三条轨 + 三颗 TPS7A20 + 六个去耦位 ⇒ 全部转 DNP（删掉）** ⇒
★**这是对 2026-11-02 19:5x 那次"三轨按 IMX415 datasheet 重核"的推翻** —— 那三条轨是**芯片级**的，模组已经在板内做完了。
⇒ ★**留下的轨**: **5V** (camera 模组) + **3.3V** (SOM + 屏模组 VDD/VCCIO)。

### ② ★ CSI 是 **4-lane**（原来 D2/D3 是 DNP 预留位）
pin2/3=MDN4/MDP4, 5/6=MDN3/MDP3, 11/12=MDN2/MDP2, 14/15=MDN1/MDP1, 17/18=MCN/MCP ⇒
⇒ ★**`CSI_D0_D2/D3` 两组从 DNP 改必装** ⇒ ★**带宽校核**: 1920×1080@60 RAW10 = 1.244Gbps ⇒ 4-lane ⇒ 每 lane 311Mbps ≪ 2.5Gbps/lane ✔

### ③ ★★ **底板电源必须由 `CARRIER_BOARD_EN` 使能（F13）**
FET3572-C/FET3576-C 的 **pin87 = `CARRIER_BOARD_EN`**（SOM 输出, 控制底板上电）+ **pin91/93/95/97 = `VCC_DCIN`（5-13V 输入）**
⇒ ★**主板不能把 5V 直连各路 LDO** ⇒ ★**底板主电源开关由 `CARRIER_BOARD_EN` 驱动** ⇒
Forlinx 原文警告：底板早于核心板上电 ⇒ "通电瞬间电流过大，设备无法启动，**甚至对处理器造成不可逆转的损坏**"
⇒ ★**这一条与 F1(EN 悬空) 同级 ⇒ 漏到投板后 = 板子起不来** ⇒ ★**必须落进网表**（推荐做法：主板 3.3V/5V 轨的负载开关/EN 接 `CARRIER_BOARD_EN`，或至少在 note 里写死"底板上电受 CARRIER_BOARD_EN 控制"）

---

## 1. ★ A1 段（现在就能做，不依赖 SOM 逐针表）

### 1.1 `CONN_CAM` → **31p / 0.3mm**（HIROSE **FH35C-31S-0.3SHW(50)**，翻盖式 ZIF, 上下双面触点, 兼容 0.2mm 厚 FPC, 横向插拔；机械 10.9×4.2×0.9mm）

**逐针针位表（照抄，一针不许错）**：
| 针 | 定义 | 针 | 定义 | 针 | 定义 | 针 | 定义 |
|---|---|---|---|---|---|---|---|
| **1** | GND | **2** | **MDN4** | **3** | **MDP4** | **4** | GND |
| **5** | **MDN3** | **6** | **MDP3** | **7** | GND | **8** | NC |
| **9** | NC | **10** | GND | **11** | **MDN2** | **12** | **MDP2** |
| **13** | GND | **14** | **MDN1** | **15** | **MDP1** | **16** | GND |
| **17** | **MCN** (CLK-) | **18** | **MCP** (CLK+) | **19** | GND | **20** | **MCLK** |
| **21** | GND | **22** | NC | **23** | NC | **24** | **SCL** |
| **25** | **SDA** | **26** | NC | **27** | **RESET** | **28** | **VCC3.3V** |
| **29** | **VCC3.3V** | **30** | **VCC5V** | **31** | **VCC5V** | | |

**信号 → 主板侧**（依据 Radxa CM5 overlay dts，实测）：
- `MDN1..MDP4 + MCN/MCP` → SoC **CSI 4-lane D-PHY**（`data-lanes = <1 2 3 4>`）⇒ ★**D2/D3 改必装**
- `MCLK` → SoC `MIPI_CAMERAOUT` / xvclk（`clocks = <&cru CLK_MIPI_CAMARAOUT_M1>`）
- `SCL/SDA` → **I2C_A**（★上拉 **3.3V / 2.2k** 已是现状, 保持）
- `RESET` → ★**新增 net** `CAM_RESET_N` ⇒ SoC GPIO（参考 dts: `gpio1 RK_PB3`, 低有效）
- ★**PWDN** → ★**新增 net** `CAM_PWDN` ⇒ SoC GPIO（参考 dts: `gpio1 RK_PA7`, 高有效）★**现网表没有 ⇒ 必须加**
- `VCC3.3V`(28,29) / `VCC5V`(30,31) → 主板 3.3V / 5V 轨 ⇒ ★**注意 3.3V 与 5V 各两针**（载流 ⇒ 两针都接）

### 1.2 `CONN_LIGHT` → **40p / 0.5mm**（贴板翻盖式, 型号待定, FH12-40S-0.5SH 一类）

逐针针位表见 `HW/STEP1_PARTS_SPEC.md` §3.1（★**执行时从该文件读, 不要手抄**）；要点：
- `MIPI_0N/0P … MIPI_3N/3P` → **DSI 4-lane**（★我们本来就是 4-lane ✔）
- `VDD`(2,31,32…) = **3.3V** · `VCCIO`(3) = **1.8~3.3V**（★**用 3.3V**）
- `Reset`(5) → ★**新增 net** `DSI_RESET_N` ⇒ SoC GPIO
- `TP_SCL`(28) / `TP_SDA`(27) → **I2C_B**（DDC）
- 其余 GND/NC 按表

### 1.3 ★ 电源树改版
| 轨 | 处理 |
|---|---|
| `SENSOR_CORE` / `SENSOR_VDD_IO` / `SENSOR_AVDD` + 三颗 TPS7A20 + 六个去耦 | ★**全部转 DNP 并注明"模组自带稳压, 芯片级三轨不需要"** |
| **5V 轨** | USB-C 5V ⇒ ★**直接给 camera 模组 pin30/31**（含限流/保护沿用既有设计） |
| **3.3V 轨** | 5V→3.3V LDO ⇒ SOM + 屏模组 VDD/VCCIO；★**3.3V 轨的主开关受 `CARRIER_BOARD_EN` 控制（见 §0③）** |
| `CARRIER_BOARD_EN` | ★**新增 net**（从 SOM 座引出 ⇒ **A2 段**才有源；★**A1 段先在网表里立 net + note, A2 段再挂到 SOM 座**） |

### 1.4 ★ camera 模组参数写进 note
`1080p60 = 1944×1097 (2/2 行 binning, 0x3020=0x01, 12bit)` · `VTS 0x0C5D→0x062E` · `SCCB 0x1a` · `FOV D88.2/H75/V59`

---

## 2. ★ A2 段（等 SOM 逐针表 —— 已拿到！）

★**逐针表已有**: `HW/PCB/FET3576C_PIN_TABLE.csv`（399 行, 列 = num, ball, gpio_or_type, vol, signal, net_or_desc, extra1..3）★**FET3572-C 与 FET3576-C 引脚兼容 ⇒ 直接用它**

### 2.1 SOM 座
- **4×100pin / 0.4mm BTB**（SOM 68×50mm, 四角 2.2mm 安装孔, 1.6mm 10 层沉金, DXF 另下）
- ⇒ ★**主板上的座 = 4 组 100 脚 0.4mm** ⇒ ★**焊盘必须按 0.4mm 间距排 ⇒ 焊盘宽度 ≤0.18mm（否则 clearance 不过）**
- ⇒ SoC 侧节点（`SoC[RK3572].*`）★**全部改挂到 SOM 座**（用表里的 `signal` / `net_or_desc` 两列）

### 2.2 电源与时序（F13）
- `pin87 CARRIER_BOARD_EN` ⇒ **底板主电源使能**（§0③）
- `pin91/93/95/97 VCC_DCIN` = **5-13V 输入** ⇒ ★**USB-C 5V 在范围内 ✔（datasheet: 5~13V, typ 12V）**
- `pin88 PWRON_L` ⇒ 开机按键 ⇒ ★**新增 net** `PWRON_L` ⇒ SoC 侧按手册 §3.5.2
- `pin50 USB_HUB_RST_3V3` / Boot 按 `SARADC_VIN0_BOOT` (§3.5.3) / UART Debug 按 §3.5.5（★**串 100Ω + 建议保留 Q1/Q2 隔离 + ESD 紧贴**）

---

## 3. ★ 验收链（每一步都要贴 rc）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && python3 state/gen_netlist_pins.py
python3 state/check_netlist.py        # 31 条判据, 全过, 不许放松判据
python3 state/check_kicad_net.py      # 5 条
python3 state/gen_bom.py
# 图纸必须跟着重出并重验:
state/pcbnew_py.sh state/gen_pcb_netlist_board.py
python3 state/check_pcb_nets.py       # 板子↔网表逐点等价 (必须 0 缺失 0 多余)
python3 state/check_pcb_drc.py        # DRC 必须 0
state/kicad.sh pcb export gerbers --output HW/PCB/gerbers/ HW/PCB/demo_mainboard.kicad_pcb
state/kicad.sh pcb export drill --output HW/PCB/gerbers/ --format excellon HW/PCB/demo_mainboard.kicad_pcb
```

★**若 `check_pcb_nets.py` 报缺失/多余** ⇒ 说明网表与板子不同步 ⇒ **以网表为准重跑生成器**（不要手改板文件）。

---

## 4. ★ 写入范围

**可改**: `state/gen_netlist.py` + `HW/SCHEMATIC_V1_SPEC.json` + 其生成物 (`HW/netlist_v1.csv` / `.net` / `netlist_v1_pins.csv` / `BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` + `HW/PCB/gerbers/`) + `state/fragments/hw.yaml` (原子写) + `HW/STEP1_PARTS_SPEC.md` (补 P3 文件信息)
★**不可改**: `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `state/check_pcb_drc.py` / `state/check_pcb_nets.py` / `state/gen_pcb_netlist_board.py` / `state/daily_check.py` / `HW/PCB/FET3576C_PIN_TABLE.csv` / `HW/PCB/panel_simple_dsi_template.dtsi`

---

## 5. ★ 交卷要求

**分段交卷**（★**宁可交半成品, 不要交 0 产出** —— 同类任务已连续 3 次 0 产出）:
- **A1 段**: §1 全部（CONN_CAM 31p + CONN_LIGHT 40p + 三条 sensor 轨转 DNP + 5V/3.3V + 三个新 GPIO/EN net + CSI 4-lane）⇒ 跑完 §3 的命令链 ⇒ **两个门禁必须绿**
- **A2 段**: §2 全部（SOM 座 400 脚 + SoC 节点改挂 + CARRIER_BOARD_EN + PWRON_L + Boot/UART）

★**回执必须含**: 改了哪几行 + 每处「旧 → 新」+ §3 每个命令的 rc + 两个门禁的输出 + A1/A2 各自完成度 + 没做的写 [待办]
