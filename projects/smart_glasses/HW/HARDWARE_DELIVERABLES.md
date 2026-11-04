# 硬件成果物总目录 · demo 主板 (RK3572 SOM + IMX415 camera + MIPI-DSI 屏)

> 出品: 项目总工 (moli) · 2026-11-04 19:3x · 老板指示「我要尽快看到原理图和 pcb 图及 bom 等和硬件成果物相关的所有资料」
> ★**一键重生成**: `bash state/gen_production_pack.sh` ⇒ 全部产物在 `HW/PCB/production/`
> ★**唯一真源链**: `state/gen_netlist.py` → `HW/netlist_v1.csv` → (原理图 / PCB / BOM / Gerber 全部由它派生)

---

## 0. 一分钟看懂现状

| 项 | 状态 |
|---|---|
| 原理图 (KiCad 可打开) | ✅ **2026-11-04 19:4x 才修好** —— 生成器少写一个右括号 ⇒ KiCad 报 "Failed to load schematic" ⇒ **从 10-27 起一直是坏的**；已修 + 加门禁 `state/check_sch_loadable.py` |
| PCB 图 (KiCad 工程文件) | ✅ `HW/PCB/demo_mainboard.kicad_pcb` · 188 器件 / 835 焊盘 / 6 层 / 160×100mm |
| BOM | ✅ `HW/BOM_v1.csv` (294 行) ★**2026-11-04 19:2x 修了一个真 bug** (ref 级 DNP 判定 ⇒ Q_ENVC / RAIL_BOARD_5V 被误判"不装" ⇒ 备料会漏买) |
| Gerber / 钻孔 / 坐标 / 装配 / 3D / 网表 | ✅ 全部已出 (49 个文件, 7.9MB) |
| ★**PCB 布线** | ❌ **未布线** —— unconnected items = **353** ⇒ ★**现在这份 Gerber 不能下单** ⇒ ISS-181 (hw-lead 在跑) |
| ★**网表 4 处缺陷** | ❌ `R_SER_USB_D_P` (2 脚电阻落 3~4 网 + D+ 与 Type-C 短接) / `C_DET_VBUS_D` (1 脚) / `FB_DEMO` (3 脚) / `C_VBUS_DEMO` (3 脚) ⇒ ISS-181 前置单已在修 |
| 网表↔板一致性 | ✅ **逐焊盘等价 487/487** (缺失 0 / 多余 0 / 同号异网 0) |
| DRC | ✅ 0 违规 (unconnected 353 属骨架态) |
| 阶段门 | **当前关 = G1「原理图/PCB 定稿」**, 缺口 1 项 = 未布线 |

---

## 1. 原理图 (Schematic)

| 成果物 | 路径 | 说明 |
|---|---|---|
| ★**KiCad 原理图 (源)** | `HW/PCB/demo_mainboard.kicad_sch` | 457KB · 296 个符号 / 525 个引脚 / 525 个网名标签 · 连通性靠**网名**建立 (connectivity-first, 不画线) |
| ★**原理图 PDF (人看)** | `HW/PCB/production/doc/demo_mainboard-sch.pdf` | 607KB · A2 |
| **原理图 SVG** | `HW/PCB/production/doc/sch_svg/demo_mainboard.svg` | 5.5MB (矢量, 可放大看) |
| **KiCad 导出网表** | `HW/PCB/production/doc/demo_mainboard-kicad.net` | 303KB · ★**KiCad 自己从图里读出来的网表** ⇒ 可与 CSV 互证 |
| **KiCad 导出 BOM** | `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` | 与我们的 BOM 交叉核对用 |
| **人读网表摘要** | `HW/PCB/demo_mainboard_sch.net` | |
| **原理图自检** | `HW/PCB/SCH_SELF_CHECK.txt` | C1~C6 (符号数/引脚数/网名集合/无重名/属性齐全) |
| ★**可加载门禁 (新)** | `state/check_sch_loadable.py` | 括号平衡 + **KiCad 真能加载** + 能出 PDF ⇒ ★**以后原理图坏了立刻报红** |
| 原理图规格 (真源) | `HW/SCHEMATIC_V1_SPEC.json` | 12 条连接段 + meta |

## 2. PCB (Layout)

| 成果物 | 路径 | 说明 |
|---|---|---|
| ★**KiCad PCB (源)** | `HW/PCB/demo_mainboard.kicad_pcb` | 188 器件 / 835 焊盘 · 6 层 · 160×100mm |
| **叠层 / 阻抗** | `HW/PCB/STACKUP.md` | L1 信号 / **L2 GND 完整平面** / L3 信号+局部电源 / L4 电源平面 / L5 信号 / **L6 GND 完整平面**; 1.6mm; ENIG; MIPI 100Ω / USB 90Ω / 单端 50Ω |
| **布线规则** | `HW/PCB/LAYOUT_RULES.md` | 差分对内间距固定 / 对间距 ≥3× 线宽 / L2-L6 不得在差分下方被分割 / MCLK 与时钟对分开走 / LDO 的 RC 紧贴 EN / AC 耦合紧贴 FPC 座 ≤5mm |
| ★**Gerber (30 个)** | `HW/PCB/gerbers/` · 副本 `HW/PCB/production/gerbers/` | F/B 铜 + 4 内层 + 阻焊 + 丝印 + 粘贴 + 外形 + **job 文件** (`.gbrjob`) |
| **钻孔 (Excellon)** | `HW/PCB/production/drill/` | PTH / NPTH `.drl` + **钻孔图 PDF** |
| **坐标文件 CPL** | `HW/PCB/production/pos/demo_mainboard-pos.csv` | 双面 / mm / KiCad 原生格式 |
| **装配 (IPC-2581)** | `HW/PCB/production/assembly/demo_mainboard-ipc2581.xml` | 1.0MB · 投板给厂的标准装配文件 |
| **装配图 PDF** | `HW/PCB/production/assembly/demo_mainboard-assembly-{top,bottom}.pdf` | 丝印 + Fab + 外形 |
| **PCB 图 PDF** | `HW/PCB/production/doc/demo_mainboard-pcb-{all,top,bottom}.pdf` | 全层 / 顶层 / 底层 |
| **3D 模型 STEP** | `HW/PCB/production/3d/demo_mainboard.step` | ⚠️ 只有 8.9KB ⇒ **封装 3D 模型基本没有** (库缺), 不影响投板 |
| **外形 DXF** | `HW/PCB/production/doc/demo_mainboard-Edge_Cuts.dxf` | 机械外形 |
| **裸板测试网表** | `HW/PCB/production/doc/demo_mainboard.d356` | IPC-D-356 (制板厂做裸板测试用) |
| **板统计** | `HW/PCB/production/doc/board-stats.txt` | 层数 / 焊盘 / 线长 / 面积等 |

## 3. BOM 与物料

| 成果物 | 路径 | 说明 |
|---|---|---|
| ★**BOM (唯一口径)** | `HW/BOM_v1.csv` | 294 行 (位号/值/类型/DNP/板级/页/证据等级/封装/OPN/容差/替代料/采购状态/备注) · 镜脚主 PCB 251 / 镜框充电板 41 / 跨铰链 4 |
| **BOM 生成器** | `state/gen_bom.py` | 真源 = 网表 ⇒ 重跑不漂 · 自检: 位号集合 / qty / 采购状态 / DNP 数 / 板级归属 |
| **三件主料规格 (已验收)** | `HW/STEP1_PARTS_SPEC.md` | P1 camera = Radxa Camera 4K (IMX415, 31p/0.3mm) · P2 display = Radxa Display 8HD/10FHD (40p/0.5mm) · P3 SOM = Forlinx FET3572-C (68×50mm, 4×100pin BTB) |
| **封装/针位真源表** | `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` (46KB) · `HW/PCB/FPC_PIN_TABLES.md` · `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行) | 含 TMP117 官方 6 脚 WSON-6 封装几何、22p display 座、相机 31p 座 |
| **选型依据** | `HW/PART_ALTERNATIVES_REGISTRY.md` (54KB) · `HW/OPEN_SOURCE_AVAILABILITY.md` · `HW/CORE_MODULE_SELECTION.md` | 7 类物料 33 个候选行 / 53 个可点链接 |
| **显示件小屏选型** | `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` · `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` | demo 屏 = Waveshare 2.8" (2-lane, 官方逐针表) |

## 4. 网表与门禁 (可追溯)

| 成果物 | 路径 | 说明 |
|---|---|---|
| ★**网表 (真源)** | `HW/netlist_v1.csv` (133KB) · `HW/netlist_v1_pins.csv` (脚级) | 10 页 (P1 电源 / P2 I2C / P3 启动存储 / P4 显示 / P5 CSI / P6 高速差分 / P7 板级接口 / P8 时钟复位 / P9 跨铰链 / P10 充电板) |
| **网表规格** | `HW/NETLIST_REV2_SPEC.md` | |
| **I2C 地址表** | `HW/I2C_ADDR_TABLE.md` | 两条总线全表 + datasheet 出处 + 冲突结论 (IMX415 0x1a / TMP117 0x48 / BQ25896 0x6b / 屏模组 MCU 0x45) |
| **PCB↔网表等价门禁** | `state/check_pcb_nets.py` | **逐焊盘**比对 ⇒ 脚位对调必被抓 (旧门禁只看 (ref,net) 集合 ⇒ 假绿) |
| **DRC 门禁** | `state/check_pcb_drc.py` | 布完线加 `--strict` ⇒ unconnected 必须 0 |
| **网表/脚级/槽位门禁** | `state/check_netlist.py` · `check_netlist_pins.py` (含 C9 I2C 地址唯一) · `check_schematic_slots.py` · `check_kicad_net.py` | |
| ★**原理图可加载门禁 (新)** | `state/check_sch_loadable.py` | KiCad 真能打开才算过 |
| **设计自检报告** | `HW/PCB/GEN_SELF_CHECK.txt` · `HW/PCB/PCB_NETLIST_FILL.txt` | |

## 5. 设计与合规文档

| 成果物 | 路径 |
|---|---|
| **demo 板硬件形态定案** | `HW/DEMO_BOARD_HW_DECISION.md` (11-02 19:4x 老板四条指示的落账) |
| **画板计划 / 图纸规划** | `HW/PCB_DRAWING_PLAN.md` |
| **硬件拆解与分工** | `HW/HARDWARE_BREAKDOWN.md` |
| **接口表 / 顶层接口** | `HW/INTERFACE_TABLE.md` · `HW/PCB/SOM_PIN_ASSIGNMENT.md` · `SOM_PIN_MAPPING.md` |
| **EMC 预检** | `HW/EMC_PRECHECK.md` (67KB) |
| **ERC/DRC 投板清单** | `HW/ERC_DRC_CHECKLIST.md` · `HW/EVT_RELIABILITY_TEST_ITEMS.md` |
| **SoM 自带能力 (别重复做)** | `HW/PCB/SOM_BUILTIN_CAPABILITY.md` |

---

## 6. ★还没做完的 (诚实清单)

| 项 | 状态 | 谁在做 |
|---|---|---|
| **PCB 布线 (353 unconnected ⇒ 不能下单)** | ❌ 进行中 | hw-lead (ISS-181) |
| **网表 4 处缺陷** (R_SER_USB_D_P / C_DET_VBUS_D / FB_DEMO / C_VBUS_DEMO) | ❌ 进行中 | hw-lead (ISS-181 前置单) |
| **KiCad annotation 提示** (伪位号 RAIL_*/NET_*/CHG_* 不是标准 designator) | ⚠️ 提示级 | 不影响连通性 (网表 parity 判据保证); 投板前若要 KiCad ERC 零告警, 需改成网名标记 |
| **封装 3D 模型** | ⚠️ 缺 (STEP 只 8.9KB) | 不影响投板; 装配/结构仿真会受影响 |
| **BOM 的封装/OPN/容差/替代料** | ⚠️ 多数 `待定` (不许编) | 随选型推进逐项落 |
| **SoM 400 焊盘的 pin1 排向** | ❌ 无定论 (ISS-169) | 实物核对 (两排做反 ⇒ 100 个网络全对调) |
| **22p display 座针序** | ⚠️ 须买线后万用表核 | 实物核对 |

---

## 7. 下一步 (按优先级)

1. **ISS-181 布线** (最高优先级, 老板 19:10 指示) ⇒ unconnected 353 → 0 ⇒ DRC strict 过 ⇒ Gerber 重出 ⇒ **可投板**
2. **网表 4 缺陷修完** ⇒ 重新生成原理图/PCB/BOM/Gerber ⇒ 4 门禁全绿
3. **投板前放行清单**: `HW/ERC_DRC_CHECKLIST.md` 逐条签 + Gerber 复核 + 坐标文件复核 + 3D/装配图确认
4. **投板** (等老板一句"下单" —— 报价/工期我备好再报)
