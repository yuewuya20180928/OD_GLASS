# ★BOARD_ONEPASS_GENERATOR_VALUE_DRIFT · 「板那一趟」生成器重跑 ⇒ Value 漂移逐条清账 + `C_VBUS_GND` 掉板机理 ★

> ★**单号**: ISS-402 · ★**执笔**: 硬件总工 (hw-lead) · ★**日期**: 2026-11-24 · ★**性质**: ★**纯查证 + 纯分析·零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍** ★
> ★**项目根**: `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` · ★**对应机器闸**: `HW/check_generator_value_drift_closed.py` (★零挂链★) · ★**对应交卷页**: `HANDOFF/2026-11-24_hw-lead_ISS402_生成器重跑Value漂移26处清账与闸.md` ★
> ★**本页只给【代价账 + 逐条台账】; 三条路线选哪条 / `C_VBUS_GND` 留不留 / 26 处各以谁为准 ⇒ ★**全部留给 main / 老板**, 本页【一条都不代拍】★**

---

## §0 · 一句话结论

★**本机现读三方真源 (板 / 网表 / BOM) 实测: 「板面 Value ≠ 重跑生成器会写上的 Value」共 ★**26 处**★ (★13 处「板面被写成脚级功能串」+ ★**13 处**★「板面那句在网表里根本不存在」★) + ★**`C_VBUS_GND` 一件在网表侧被 `BOARD_FILTER="MAIN_PCB"` 过滤掉 ⇒ 重跑即掉板 (186 → 185 封装)**★ ⇒ ⇒ ★**这 26 处 + 这 1 件, 到今天为止只以散文形式记在 `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` 里, 没有任何机器闸钉住 ⇒ 本页把它们做成【逐条可查的台账 + 一道 fail-closed 的机器闸】★** ★

★**三条路线的代价账在 §4 (甲/乙/丙); 「板那一趟」该怎么用这张表在 §5; 机器块在 §6 (26 行 + `cvbus_gnd` + `routes` + `decisions`, ★`decisions` 逐项 `not_decided_here`★)★**

---

## §1 · 背景与口径出处

### §1.1 · 为什么这件事必须在「板那一趟」之前钉死

★**「板只改一次」铁律**: 板 md5 全生命周期只许变 **1** 次 ⇒ ★**凡会改网表真源 / 会改板面 Value / 会让某件从板上掉下来的动作, 必须与「板那一趟」同批做完** ⇒ ★**任何一处漏改 = 板 md5 第二次变 = Gerber / 投产包 / 留证链 / 盖章 / 发布全部白跑 (2-4 周 + ¥4-8K 返工)** ★
★**口径出处 (本机实读, md5 见 §1.4)**: `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` §2 `INV-1` / §3 / §5 · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S2 / §3-S3 / §3-S7 · 台账 `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` §1 基线区 (★`baseline_md5: 611b869e13518c3c023fb178f91a0075`★) ★

### §1.2 · 散文记过一次 ≠ 闭环

★**2026-11-17 的 ISS-287 交卷页 §D** 实测出「官方板与沙盒生成板 位号/封装名/数量全同, 但 **26 处 Value 不同**」, 并在 §结论 1 写明 `S-2` = 26 处 Value 差异 / `S-3` = `C_VBUS_GND` 只在官方板 ⇒ 重跑会掉 · ★**但那 4 条 need 到今天仍是 open** (`state/fragments/hw.yaml`: `iss287_cvbus_gnd_board_only` / `iss287_tmp_write_through` / `iss287_26_value_diff` 各只出现 1 次且无 answers)· ★**且全仓没有任何机器闸读它** (★`grep -rn "26 处 Value"` 只命中 ISS-287 交卷页 + 一条 open need + 一份 `_apply_*.py`★) ⇒ ⇒ ★**「板那一趟」的执行者只读作业包 + 提交顺序页, 【读不到】这 26 处 ⇒ 重跑 ⇒ 静默覆盖 ⇒ 那时才发现 = 板改第二次** ★ ⇒ ★**本单把散文变成台账 + 闸** ★

### §1.3 · ★「网表侧 Value」的严格定义 (★本单最关键的口径, 机器可复算★)★

★**「网表侧 Value」= ★**「现在重跑 `state/gen_pcb_netlist_board.py` 会写到板上的那一句字」**★ ⇒ 口径拆解 (★逐条给盘上源码行号★):

| 步 | 口径 | 盘上源码出处 |
|---|---|---|
| ① | ★**板级过滤**: `keep = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]` · `BOARD_FILTER = "MAIN_PCB"` ⇒ ★**513 行进板 404 行** ★ | ★`state/gen_pcb_netlist_board.py:247` + `:112` ★ |
| ② | ★**取值规则** = ★**本体行优先** (该 ref 的 `type` ∉ {`NET`,`""`} 的**第一条**行) · ★**逐字截断 40 字符** ★ | ★`state/gen_pcb_netlist_board.py:596-627` (`pick_board_values`) + 调用点 `:654` ★ |
| ③ | ★**占位兜底**: ref 不在 `value_of` 里 ⇒ `"SoM BTB %s (100pin, 部分已分配)" % ref.split("_")[-1]` ★ | ★`state/gen_pcb_netlist_board.py:656-658` ★ |
| ④ | ★**特殊路径封装自带写死 Value (不走 `value_of`)** ★ | ★`J_SOM_P1..P4` → `state/som_btb_footprint.py:88-89` · `CONN_LIGHT` → `state/display_fpc_footprint.py:83` · `J_USB_C` → `state/usb_c_footprint.py:74` · `U_TEMP` → `state/tmp117_footprint.py:63` ★ |
| ⑤ | ★**生成器完全【不画】的位号 ⇒ 重跑会掉板** ★ | ★`state/gen_pcb_netlist_board.py:690-699` (跳过 `J_SOM_*` / `CONN_LIGHT` / `J_USB_C` 走 ④) + `:816` 附近的通用排布循环 ★ |

★**板面 Value 的读法 (★两种方法都跑了, 逐条互校★)**: ★**方法甲** = `bash state/pcbnew_py.sh` 起 pcbnew 读 `(property "Value" …)` · ★**方法乙** = 自写 s-表达式扫描器 (`tmp/iss402/read_board_sexpr.py`, ★不 import pcbnew ⇒ 两法互相独立★)⇒ ★**交叉核对结果: `refs_common=186 / value_diff=0 / pos_diff=0 / pad_diff=0 / padnet_equal=186` ⇒ 两法读数逐条相同** ★ (★原样输出: `logs/iss402/two_methods_cross_check.txt`★)

★**为什么必须把 ④ 单独拎出来**: ★**若只按 ②③ 算 (不认特殊路径的写死 Value), 会多算出 9 处假差异** (`J_SOM_P1` / `J_SOM_P2` / `J_SOM_P4` / `J_CHG` / `CONN_LIGHT` / `J_USB_C` / `U_TEMP` + 2 处 `J_SOM_P*` 的节点串占位) ⇒ ★**本单第一版实算就是 35 条, 补上 ④ 之后 = 26 条** ⇒ ★**这 9 条在 ISS-287 的 26 里【本来就没有】, 两边集合逐条相同 (★见 §2 脚注★)★ ★

### §1.4 · 本单现读的三份真源 (★指纹自证★)

| 真源 | 路径 | md5 | size | mtime |
|---|---|---|---|---|
| ★现役板 (★只读★) ★ | `HW/PCB/demo_mainboard.kicad_pcb` | ★`611b869e13518c3c023fb178f91a0075` ★ | ★`4940213` ★ | ★`2026-11-06 07:07:17.362193413` ★ |
| ★网表真源 ★ | `HW/netlist_v1.csv` | ★`6aee500e60ba0732f83a9cf557ba90ab` ★ | `143198` | `2026-11-18 00:21:08.701116490` |
| ★BOM 真源 ★ | `HW/BOM_v1.csv` | ★`5b9993992405904a60ac96a020b375d8` ★ | `44881` | `2026-11-18 00:21:08.953119601` |
| ★脚级表 (BOM 的输入) ★ | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `146055` | `2026-11-23 19:19:15.443437584` |

★**★板 (11-06) 比网表 (11-18) 早 12 天 ⇒ 「板上那 26 处旧值」的根因 = ★**板是 11-06 那版网表生成的, 网表在 11-17 / 11-18 两次落表后已经变了**★ ⇒ ★**这不是「板画错了」, 是「板比台账旧」** ★ (★落表链证据: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 · 链头 ISS-302 · 2026-11-18 00:3x · 逐条登记 L1451~L1455★) ★

★**本单引用的既有页 (★md5 开工前后逐字相同★)**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` = `00b0ea5bae70b7f663b55b9b80014d03` · `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` = `106ba9e041123e08bf22bac4a91dd356` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` = `192873f6c977b376c28785824a82f9f1` · `HW/PCB/LAYOUT_FIX_SPEC.md` = `a35b6fb064512d16e8e6e40c697f980b` · `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` = `072dece8167c589fa3dc0c441bdadab1` ★

---

## §2 · ★**26 处逐条清账表**★ (★台账 = 本单的机器可查核心★)

★**列口径**: ★**板面 Value** = 板文件 `(property "Value" …)` 逐字 · ★**网表侧 Value** = §1.3 定义 (= 重跑生成器会写上的字) · ★**BOM 侧 Value** = `HW/BOM_v1.csv` 的 `value` 列逐字 · ★**差异类型** = ★**本单自定分类 (★不照抄 ISS-287 的 12/14★)★** · ★**证据等级**: 第 3/4/5/6/9 列 = `[实测]` (★盘面逐字读出★), 第 7/8 列 = `[推算]` (★我的判断★) ★

★**★差异类型 (★自定 · 机器可算·判据写在括号里★)★**:
- ★**A·板面=网表脚级功能串 (13 处)** ★ := 板面 Value ★**逐字等于**该 ref 在网表里某个 `type=NET` 行的 value ★ ⇒ ⇒ ★**板面记的是【某个脚的功能】, 不是器件身份** ★
- ★**C·板面=网表里不存在的串 (13 处)** ★ := 板面 Value ★**在该 ref 的任何一行网表 value 里都找不到** ★ ⇒ ⇒ ★**板上是 11-06 那版网表的旧选型值, 现网表已没有这句** ★

| # | 位号 | 板面 Value (逐字) | 网表侧 Value (逐字) | BOM 侧 Value (逐字) | 差异类型 (★自定分类★) | 是否影响电气语义 (★[推算]★ 选型/封装/网络归属 三问逐条答) | 落表归属 (★[推算]★) | 证据等级 |
|---|---|---|---|---|---|---|---|---|
| 1 | `CONN_CAM` | `GND` | `★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 ` | `GND` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★ | [实测] |
| 2 | `D_ESD_CAM` | `ESD 阵列 [待选型]` | `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · C` | `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 3 | `D_ESD_DEMO` | `ESD 阵列 [待选型] (USB 2.0)` | `PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-32` | `PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 4 | `D_ESD_USB_D` | `ESD 阵列 [待选型] (USB 2.0 双通道)` | `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · C` | `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 5 | `FB_DEMO` | `π 滤波磁珠 [待选型]` | `BLM21PG221SN1D (Murata 0805 · 220Ω@100MH` | `BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 6 | `Q_AND` | `[待选型] N-MOS (硬件 AND)` | `AO3400A (AOS N-MOS SOT-23 · VGS(th) max ` | `AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 7 | `Q_ENVC` | `[待选型] N-MOS (反相)` | `AO3400A (AOS N-MOS SOT-23 · VGS(th) max ` | `AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 8 | `Q_PG` | `[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)` | `DMP3098L (Diodes Inc P-MOS SOT-23 · −30V` | `DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 9 | `R_BAT_DET_1` | `1M ±1%` | `100k ±1%` | `100k ±1%` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 10 | `R_BAT_DET_2` | `1M ±1%` | `60k ±1%` | `60k ±1%` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 11 | `R_LED_G` | `1k ±1%` | `55Ω ±1%` | `55Ω ±1%` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 12 | `R_LED_R` | `1k ±1%` | `68Ω ±1%` | `68Ω ±1%` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 13 | `R_SUPV_DIV1` | `[待选型] 分压上臂 (0Ω 跳线位)` | `0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板` | `0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 14 | `R_SUPV_DIV2` | `[待选型] 分压下臂 (0Ω 跳线位)` | `0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板` | `0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板` | C·板面=网表里不存在的串 | 选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 15 | `U_DCDC_VCORE` | `EN 输入 (高 = 使能)` | `TPS62130A` | `EN 输入 (高 = 使能)` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★ | [实测] |
| 16 | `U_DCDC_VIO` | `EN 输入 (高 = 使能)` | `TPS62130A` | `EN 输入 (高 = 使能)` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★ | [实测] |
| 17 | `U_EN_SW` | `EN 输入 (高=放行底板)` | `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=G` | `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 18 | `U_LDO_IO18` | `EN (pin3)` | `TPS7A20-18` | `TPS7A20-18` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 19 | `U_LDO_IO33` | `EN (pin3)` | `TPS7A20-33` | `TPS7A20-33` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 20 | `U_LDO_L18` | `EN (pin3)` | `TPS7A20-18` | `TPS7A20-18` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 21 | `U_LDO_L33` | `EN (pin3)` | `TPS7A20-33` | `TPS7A20-33` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 22 | `U_LDO_S12` | `EN (pin3)` | `TPS7A20-12` | `TPS7A20-12` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 23 | `U_LDO_S18B` | `EN (pin3)` | `TPS7A20-18` | `TPS7A20-18` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 24 | `U_LDO_S28` | `GND (pin2)` | `TPS7A20-28` | `TPS7A20-28` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 25 | `U_PWR_SW` | `VIN (输入)` | `TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GN` | `TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |
| 26 | `U_SUPV` | `CT 脚 (阈值/延时选择)` | `[待选型] 电压监控 + 复位 (TPS3808G01 类)` | `[待选型] 电压监控 + 复位 (TPS3808G01 类)` | A·板面=网表脚级功能串 | 选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定) | ★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) | [实测] |

★**★脚注 (★与 ISS-287 的交叉核对·不是抄·是独立算完后比★)★**: ★**本单独立算出的 26 条, 与 ISS-287 §D 列出的 26 条【集合逐条相同】(★`mine-only = []` / `iss287-only = []`★)** ⇒ ★**两边的条数与位号互证** ★; ★**但本单的【差异类型分类】与 ISS-287 的 12/14 不同 (★本单 = 13/13, 判据是【板面这句在网表里以什么身份出现】★)⇒ ★**两边分类数不同、位号集合相同 ⇒ 是分类口径不同, 不是数据打架** ★

---

## §3 · ★`C_VBUS_GND` 的掉板机理 (★三处存在性 + 机理·代码 + 数据钉死★)★

### §3.1 · 三处存在性 (★逐条给本机证据★)

| 处 | 在不在 | 逐字证据 | 证据等级 |
|---|---|---|---|
| ★**网表 (board 列)** ★ | ★**在, 但 board 列 = `CHG_BOARD`** ★ | ★`HW/netlist_v1.csv:10` = `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,"π 滤波后级**对地**电容…",C-01,CHG_BOARD,,` ★ · ★`:12` = `P1,VBUS_5V_CHG,C_VBUS_GND,VBUS_5V_CHG,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,"π 滤波后级对地电容的信号端…",C-01,CHG_BOARD,,` ★ (★**两行的 board 列都是 `CHG_BOARD`**★) | ★`[实测]` ★ |
| ★**板面** ★ | ★**在 (实物封装)** ★ | ★`HW/PCB/demo_mainboard.kicad_pcb:8170` = `(footprint ""` · ★`:8172` = `(at 107.7 42.5)` · ★`:8174` = `(property "Reference" "C_VBUS_GND"` · ★`:8185` = `(property "Value" "[待选型] 100µF"` · ★`:8259` = `(pad "1" smd rect` + ★`:8263` = `(net "GND")` · ★`:8267` = `(pad "2" smd rect` + ★`:8271` = `(net "VBUS_5V_CHG")` ★ | ★`[实测]` ★ |
| ★**BOM** ★ | ★**在, board 列 = `镜框充电板`, dnp = `DNP`** ★ | ★`HW/BOM_v1.csv:51` = `C_VBUS_GND,1,[待选型] 100µF,C,DNP,镜框充电板,P1,[推算],,待定,,待定,待定,DNP-不装,方案A/B 二选一或预留位; 板上有位置但首版不贴` ★ | ★`[实测]` ★ |

### §3.2 · ★**掉板机理 (★钉死★)**★

★**它为什么会掉? ⇒ 不是「本来不在网表里」, 也不是「board 列写成了别的」, 而是 ★**网表两行的 `board` 列 = `CHG_BOARD` ⇒ 被生成器的板级过滤剔掉**★ ⇒ 生成板里根本没有这个位号 ⇒ 重跑即掉。** ★

| 步 | 事实 | 证据 |
|---|---|---|
| ① | ★**它在网表里 (2 行), 但两行的 `board` 列都不是 `MAIN_PCB`** ★ | ★`HW/netlist_v1.csv:10` / `:12` 的 board 列 = `CHG_BOARD` ★ |
| ② | ★**生成器按 board 列过滤** ⇒ 该 ref 【不在 want 集合里】 ★ | ★`state/gen_pcb_netlist_board.py:247` `keep = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]` + `:112` `BOARD_FILTER = "MAIN_PCB"` · ★**实测打印: 「[板级过滤] MAIN_PCB: 404/513 行进板」** ★ |
| ③ | ★**它也不在节点串里 (器件宇宙里没有它)** ⇒ 连占位兜底 `:656-658` 都不会碰它 ⇒ 生成器【连封装都不画】 ★ | ★**本机实测**: `C_VBUS_GND` 在 404 条 MAIN_PCB 行的 `node1`/`node2` 里出现 **0** 次; 且它的 `ref` 不在 MAIN_PCB 行的 ref 列里 ⇒ ★**它既不是「网表里的件」也不是「节点串里的件」** ★ |
| ④ | ★**但现役官方板上有它的实物封装 (2 焊盘, 带网)** ★ ⇒ ★**板比生成器多这一件** ★ | ★板面 `:8170`~`:8271` (见 §3.1) · ★**实测: 官方板 186 封装 / 生成板 185 封装 ⇒ 差 1 = `C_VBUS_GND`** ★ |
| ⑤ | ★**后果**: 重跑生成器 ⇒ ★**板上这件消失 (186 → 185)** ★ ⇒ ⇒ ★**并且 `check_pcb_nets` 的 C1「多余」从 2 变 0** ★ | ★**本机实测 `bash state/pcbnew_py.sh state/check_pcb_nets.py` (rc=1, 既有红项) ⇒ 输出逐字: 「★多: `C_VBUS_GND pad1 = GND`」/「★多: `C_VBUS_GND pad2 = VBUS_5V_CHG`」** ★ |

★**★所以它「掉板」= ★**【板比网表多一件, 而重跑会把板重建成【网表口径】⇒ 那一件自然消失】**★ ⇒ ★**不是 bug, 是「板是旧货」的直接后果** ★

### §3.3 · 与 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S2 的因果关系 (★是不是同一件事的两面?★)

★**是同一件事的两面, 但【执行方式】不同 ⇒ 两者的关系必须写清, 否则「板那一趟」会重复做或漏做**: ★
- ★**§3-S2 (B-1)** 的口径 = ★**「`C_VBUS_GND` 从 demo 主 PCB 拿掉」**, 改法栏写 ★**「不手改板 —— 板生成器按 board 列过滤 ⇒ 重跑 S6 即自动消失」**, 改哪个真源栏写 ★**「不用改网表 —— `HW/netlist_v1.csv:10` 与 `:12` 两行的 board 列已经是 `CHG_BOARD`」**, 量化判据 = ★**`C1: 缺失 0 · 多余 0 · 同号异网 0` (现状 多余 2)**, 卡在谁栏 = ★**「没人」** ★
- ★**ISS-287 的 S-3** 的口径 = ★**「重跑生成器 ⇒ 这颗会从板上消失」** ★

★**⇒ 二者【不是两件事】, 是【同一件事的「目标」与「副作用」】**: ★**S2 = 「必须拿掉」这个动作 + 它的验收判据 (C1 多余 0)★; S-3 = 「重跑生成器时它会自己掉」这个技术事实★ ⇒ ★**若「板那一趟」走【重跑】(路线乙/丙), S2 的动作【自动达成】(零额外动作); 若走【不重跑】(路线甲), S2 的动作【必须手工做】(从板上删这个封装) ⇒ ⇒ ★**这两条路线下 S2 的【工作量】完全不同 ⇒ 「板那一趟」任务书必须把 S2 写清楚走哪条臂** ★ ★

★**★但本单【不代拍】留还是留★**: ★**§3-S2 的纸面口径是「拿掉」(卡在谁 = 没人), 而 need `boss_c_vbus_gnd_reserve_pad_20261117` (★留位与否·老板域★) 已登记 ⇒ ★**纸面口径与已登记的待拍项之间存在张力 ⇒ 这是 main / 老板的地界, 本单只把机理与两边的口径逐字摆出来, 一句都不代拍** ★

---

## §4 · 三条路线的代价账 (★**不代拍**·只算账★)

> ★**共同前提**: 板 md5 全生命周期只许变 1 次 ⇒ ★**任何一条路线下的【板侧改动 + 落表 + 重跑 + 布线 + 留证】必须【同趟一次做完】** ⇒ ★**下面三条路线的代价栏里, 凡是会碰网表真源 / 板面 / 封装几何的, 都必须在同一趟里收口, 不许分两趟** ★

### §4.A · ★路线甲 · 不重跑生成器 (★只改现有板上的目标项★)★

| 维度 | 账 |
|---|---|
| ★**做什么** ★ | ★**在现役官方板上直接改目标项 (改 `Value` 属性 / 改封装 / 挪位置 / 删封装)**, ★**不跑 `state/gen_pcb_netlist_board.py`** ★ |
| ★**这 26 处 Value** ★ | ★**原样保留** (★一个字都不动★) ⇒ ★**板面与网表 / BOM 的三方不一致【持续存在】** ★ |
| ★**`C_VBUS_GND`** ★ | ★**不会自己掉** ⇒ ★**§3-S2 的动作必须【手工做】(从板上删这个 2 焊盘封装)** ★ |
| ★**DNP 标记** ★ | ★**不会打上 (现状板上零标记)** ⇒ ★**若这一趟需要 DNP 标记, 得手工补 40 个位号** ★ |
| ★**★做不到的事 (★硬代价★)** ★ | ★**「换封装」这一类目标项做不到** ★ (★换封装 = 换几何 = 改板; ★而通用 `make_footprint` 画的封装与真实器件差得远 —— 见 ISS-369 的写盘作业包★) ⇒ ★**凡目标项要换封装, 路线甲只能靠【手写/脚本改板】, 落在「板那一趟」的范围外 ⇒ 要么不做, 要么单开一趟 ⇒ 单开一趟 = 板 md5 第二次变 = 破铁律** ★ |
| ★**其它代价** ★ | ★**板面 Value / 网表 / BOM 三方永久不一致 ⇒ 贴片厂若照板面字选料, 13 处会装错件 (类型 C 那 13 处: 板面 `1M ±1%` vs BOM `100k ±1%` 这类【直接冲突】)** ★ ⇒ ★**投板前必须有人工/脚本兜底 (★比如把 BOM 随板交付并写明「以 BOM 为准」★)** ★ |
| ★**谁拍** ★ | ★**main / 老板** ★ (★**本单不代拍**★) ★ |

### §4.B · ★路线乙 · 重跑生成器 (★26 处 Value 全被覆盖成生成器口径★)★

| 维度 | 账 |
|---|---|
| ★**做什么** ★ | ★**跑 `state/gen_pcb_netlist_board.py` 重生成板** (★`PCB_ALLOW_OFFICIAL=1` 才能写正式板★) ★ |
| ★**这 26 处 Value** ★ | ★**全被覆盖成生成器口径** ⇒ ★**13 处脚级功能串 → 器件身份串** (★`EN (pin3)` → `TPS7A20-18` 这类★) + ★**13 处旧选型串 → 现网表的新选型串** (★`1M ±1%` → `100k ±1%` 这类★) ⇒ ★**板面终于与网表本体行一致** ★ |
| ★**★`C_VBUS_GND` 掉板** ★ | ★**掉 (186 → 185 封装)** ⇒ ★**§3-S2 自动达成** ★ (★代价 = ★**如果最终裁决是「留位」, 这一步是不可逆的板面删除 ⇒ 必须先拍**★) ★ |
| ★**★DNP 标记一次性被打上** ★ | ★**本机实测 `HW/check_netlist_contradiction_r3.py` ⇒ R3-A4 逐字: 「MAIN_PCB且DNP **51** 颗 · 在板上 **40** 颗 · 零标记 **40** 颗 ⇒ ❌ 红」 ⇒ ★**重跑 ⇒ 板上一次性多出 40 个 DNP 标记 (现状零标记)** ★ ⇒ ★**这是【第一次】有 DNP 标记 ⇒ 贴片坐标会从「当必装」变成「当不装」 ⇒ 电池座 / 电池保护 / 2 颗 MOS 这类件【首版就不贴了】** ★ |
| ★**封装 / 布线** ★ | ★**全部重排 + 布线全废** ⇒ ★**那一趟的工程量 = 全板重做** ⇒ ★**板 md5 变 1 次, 但那一趟必须一次做完 (漏一处 = 第二次变 = 2-4 周 + ¥4-8K)** ★ |
| ★**其它代价** ★ | ★**重跑会把 §3-S2 / §3-S3 / §3-S4 的【板侧改动】全部【顺带做掉】(因为生成器是按网表重画) ⇒ ★**但也意味着【那些改动的前置拍板必须全部到位】, 否则等于在没拍板的情况下把板改了** ★ ⇒ ★**路线乙的前置条件比路线甲多得多** ★ |
| ★**谁拍** ★ | ★**main / 老板** ★ (★**本单不代拍**★) ★ |

### §4.C · ★路线丙 · 重跑 + 事先把 26 处补成生成器口径 / 补落表 (★网表真源要动的路线★)★

| 维度 | 账 |
|---|---|
| ★**做什么** ★ | ★**先把 26 处的口径【事先定死并落表】, 再重跑生成器** ⇒ ★**网表真源可能改动 (`HW/netlist_v1.csv:value` / `HW/netlist_v1_pins.csv:value` + 重生成 `HW/BOM_v1.csv`)** ★ |
| ★**★落表代价 (★核心代价★)** ★ | ★**网表真源改动 ⇒ 这一批落表本身就是「板那一趟」的一部分** ⇒ ★**落表批次 (★下一批 · 单号待 main 分配★) 必须与「板那一趟」同批, 不许先落表后跑板** ⇒ ★**落表一次 = 网表 md5 变一次 ⇒ 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 要加一条链 (★含 §16.2 新旧 md5 前后对照★) ⇒ ★**`HW/landing_md5.py` 的注册表会跟着变 ⇒ 以 md5 为基线的闸要重锚 (★SW / MECH 两边走 H-1 重锚★)** ★ ⇒ ★**落表本身也有「一次」纪律 (★落表后必须扫一遍所有以真源 md5 为基线的闸与自测, 不许只改基线数字★)** ★ |
| ★**落表内容取决于裁决** ★ | ★**若裁决 = 以网表为准** ⇒ ★**零落表** (板面刷成生成器口径就够) ⇒ ★**路线丙 ≡ 路线乙 + 「零落表」那部分, 只多出「事先把裁决写清」的动作** ★ · ★**若裁决 = 以板面为准** ⇒ ★**必须把那 26 句写回网表本体行 + 脚级表 + 重生成 BOM** ⇒ ★**落表量 = 26 条 value 改写 + BOM 重生成 + 台账加链 + 全链 md5 重锚** ★ |
| ★**★不许做的事 (★血案级★)** ★ | ★**【不许分两趟】**: ★**落表一趟 + 重跑一趟 = 板 md5 变两次 = 铁律破** ⇒ ★**落表 + 重跑 + 布线 + 留证必须同趟** ★ |
| ★**谁拍** ★ | ★**main / 老板** ★ (★**本单不代拍**★) ★ |

### §4.0 · ★三条路线的代价对照 (★一页看完★)★

| 维度 | ★甲 · 不重跑★ | ★乙 · 重跑★ | ★丙 · 重跑 + 落表★ |
|---|---|---|---|
| ★**26 处 Value** ★ | ★原样保留 (三方不一致持续) ★ | ★全被覆盖成生成器口径 ★ | ★**取决于裁决** (以网表为准=覆盖 · 以板为准=写回网表) ★ |
| ★**`C_VBUS_GND`** ★ | ★**不会掉** ⇒ 要手工删 ★ | ★**掉 (186→185)** ★ | ★**掉** (同乙) ★ |
| ★**DNP 标记** ★ | ★不打 (要打就手工补 40 个) ★ | ★**一次性打 40 个** ★ | ★**一次性打 40 个** ★ |
| ★**换封装类目标项** ★ | ★**做不到** (只能手改板 ⇒ 破「一次」) ★ | ★**做得到** (重画) ★ | ★**做得到** ★ |
| ★**网表真源** ★ | ★不动 ★ | ★不动 ★ | ★**可能动 ⇒ 落表批次进「板那一趟」** ★ |
| ★**板 md5 变更次数** ★ | 1 (手工改板) ★ | 1 (重跑 + 重布线) ★ | 1 (落表 + 重跑 + 重布线, 必须同趟) ★ |
| ★**谁拍** ★ | ★main / 老板 ★ | ★main / 老板 ★ | ★main / 老板 ★ |

---

## §5 · ★「板那一趟」该怎么用这张表 (★逐条: 落哪一步 / 谁落 / 落之前要谁点头★)★

| # | ★动作★ | ★落哪一步 (作业包 §3)★ | ★谁落★ | ★落之前要谁点头★ | ★判据 (机器可查)★ |
|---|---|---|---|---|---|
| 1 | ★**把 26 处 Value 逐条处置口径定死** (★每处以谁为准: 板面 / 网表 / BOM★) | ★**§3-S3** (★现状只覆盖 8 处: `U_EN_SW` + 7 颗 TPS7A20 ⇒ ★**另外 18 处不在它的验收判据里**★) ★ | ★**main / 老板拍 ⇒ hw-lead 落表** ★ | ★**main / 老板** ★ | ★**本闸 D1: 每条差异都必须在 §2 登记 (★本单已完成登记; 处置口径待裁★)** ★ |
| 2 | ★**`C_VBUS_GND` 留还是不留** | ★**§3-S2** (B-1) ★ | ★**main / 老板拍 ⇒ hw-lead 执行** ★ | ★**main / 老板** (★已登记 `boss_c_vbus_gnd_reserve_pad_20261117`★) ★ | ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ **C1 多余 0** ★ |
| 3 | ★**DNP 标记要不要在那一趟打** (★现状零标记; 重跑会打 40 个★) | ★**§3-S7** (B-17) ★ | ★**main / 老板拍 ⇒ hw-lead 执行** ★ | ★**main / 老板** ★ | ★`python3 HW/check_netlist_contradiction_r3.py` ⇒ **R3-A4 零标记 = 0** ★ |
| 4 | ★**三条路线选哪条** (★甲/乙/丙★) | ★**任务书总则** (★`BOARD_ONEPASS_COMMIT_ORDER.md` §3 的 A 类步清单★) ★ | ★**main / 老板** ★ | ★**main / 老板** ★ | ★**本闸 D5: 三条路线的代价账齐 ⇒ 才允许进「板那一趟」** ★ |
| 5 | ★**每一条处置完后, 板面 / 网表 / BOM 三方必须一致** | ★**§3-S3 + §3-S7 同趟** ★ | ★**hw-lead** ★ | ★**路线已拍** ★ | ★**本闸 D1+D2: 板面实测值 == 台账登记值 == 网表侧口径** ★ |
| 6 | ★**落表批次与「板那一趟」同批** (★若裁决 = 以板面为准★) | ★**§3-S3 + 台账 §16.2** ★ | ★**hw-lead (需 main 派单号)★** ★ | ★**main** ★ | ★**`HW/landing_md5.py` 注册表 + `HW/check_onepass_commit_order.py` rc=0** ★ |

★**★给「板那一趟」任务书的一句硬约束 (★本单实测结论★)** ★
> ★**「板那一趟」开工前, 必须先跑 `python3 HW/check_generator_value_drift_closed.py` (★本闸★) 与 `bash state/pcbnew_py.sh state/check_pcb_nets.py` (★看 C1 的「多余」数★) ⇒ ★**这两道读数决定「那一趟」走哪条臂; 任何一条红 ⇒ 不许开工** ★**

---

## §6 · ★机器块 (★机器可解析★)★

> ★**用法**: `python3 HW/check_generator_value_drift_closed.py` ⇒ ★**本块被 `HW/check_generator_value_drift_closed.py` 逐字段回算** ★
> ★**`decisions` 逐项 `not_decided_here` ⇒ ★**一条都不代拍** ★

```yaml
generator_value_drift:
  board_md5: "611b869e13518c3c023fb178f91a0075"
  board_mtime: "2026-11-06 07:07:17.362193"
  board_size: 4940213
  netlist_md5: "6aee500e60ba0732f83a9cf557ba90ab"
  bom_md5: "5b9993992405904a60ac96a020b375d8"
  row_count: 26
  rows:
    - ref: "CONN_CAM"
      board_value: "GND"
      netlist_value: "★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 "
      bom_value: "GND"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★"
      evidence_level: "[实测]"
    - ref: "D_ESD_CAM"
      board_value: "ESD 阵列 [待选型]"
      netlist_value: "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · C"
      bom_value: "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "D_ESD_DEMO"
      board_value: "ESD 阵列 [待选型] (USB 2.0)"
      netlist_value: "PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-32"
      bom_value: "PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "D_ESD_USB_D"
      board_value: "ESD 阵列 [待选型] (USB 2.0 双通道)"
      netlist_value: "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · C"
      bom_value: "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "FB_DEMO"
      board_value: "π 滤波磁珠 [待选型]"
      netlist_value: "BLM21PG221SN1D (Murata 0805 · 220Ω@100MH"
      bom_value: "BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "Q_AND"
      board_value: "[待选型] N-MOS (硬件 AND)"
      netlist_value: "AO3400A (AOS N-MOS SOT-23 · VGS(th) max "
      bom_value: "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "Q_ENVC"
      board_value: "[待选型] N-MOS (反相)"
      netlist_value: "AO3400A (AOS N-MOS SOT-23 · VGS(th) max "
      bom_value: "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "Q_PG"
      board_value: "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)"
      netlist_value: "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V"
      bom_value: "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_BAT_DET_1"
      board_value: "1M ±1%"
      netlist_value: "100k ±1%"
      bom_value: "100k ±1%"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_BAT_DET_2"
      board_value: "1M ±1%"
      netlist_value: "60k ±1%"
      bom_value: "60k ±1%"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_LED_G"
      board_value: "1k ±1%"
      netlist_value: "55Ω ±1%"
      bom_value: "55Ω ±1%"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_LED_R"
      board_value: "1k ±1%"
      netlist_value: "68Ω ±1%"
      bom_value: "68Ω ±1%"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_SUPV_DIV1"
      board_value: "[待选型] 分压上臂 (0Ω 跳线位)"
      netlist_value: "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板"
      bom_value: "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "R_SUPV_DIV2"
      board_value: "[待选型] 分压下臂 (0Ω 跳线位)"
      netlist_value: "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板"
      bom_value: "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板"
      diff_type: "C·板面=网表里不存在的串"
      affects_electrical: "选型=★是★(板面这句与 BOM 型号【直接冲突】⇒ 照板面字选料会装错件) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · ★板面那句在网表里【根本没有】★ ⇒ 若裁决=以网表为准 ⇒ 零落表(只刷板面) · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value(该 ref 本体行) + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_DCDC_VCORE"
      board_value: "EN 输入 (高 = 使能)"
      netlist_value: "TPS62130A"
      bom_value: "EN 输入 (高 = 使能)"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★"
      evidence_level: "[实测]"
    - ref: "U_DCDC_VIO"
      board_value: "EN 输入 (高 = 使能)"
      netlist_value: "TPS62130A"
      bom_value: "EN 输入 (高 = 使能)"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配) · ★BOM 侧当前取的是脚级表口径(BOM value == 脚功能串) ⇒ 三方一致须连脚级表一起改★"
      evidence_level: "[实测]"
    - ref: "U_EN_SW"
      board_value: "EN 输入 (高=放行底板)"
      netlist_value: "TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=G"
      bom_value: "TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_IO18"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-18"
      bom_value: "TPS7A20-18"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_IO33"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-33"
      bom_value: "TPS7A20-33"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_L18"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-18"
      bom_value: "TPS7A20-18"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_L33"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-33"
      bom_value: "TPS7A20-33"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_S12"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-12"
      bom_value: "TPS7A20-12"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_S18B"
      board_value: "EN (pin3)"
      netlist_value: "TPS7A20-18"
      bom_value: "TPS7A20-18"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_LDO_S28"
      board_value: "GND (pin2)"
      netlist_value: "TPS7A20-28"
      bom_value: "TPS7A20-28"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_PWR_SW"
      board_value: "VIN (输入)"
      netlist_value: "TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GN"
      bom_value: "TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
    - ref: "U_SUPV"
      board_value: "CT 脚 (阈值/延时选择)"
      netlist_value: "[待选型] 电压监控 + 复位 (TPS3808G01 类)"
      bom_value: "[待选型] 电压监控 + 复位 (TPS3808G01 类)"
      diff_type: "A·板面=网表脚级功能串"
      affects_electrical: "选型=★是★(板面这句【不是器件身份串】⇒ 贴片/装配侧拿不到料号) · 封装=★否★(Value 字段不进封装几何) · 网络归属=★否★(焊盘网络由网表 node1/node2 决定)"
      landing_owner: "★裁决前零动作★ · 网表本体行的 value 已是器件身份串 ⇒ 网表真源【不用改】· 若裁决=以网表为准 ⇒ 板面随『板那一趟 S3』刷成生成器口径 ⇒ 零落表 · 若裁决=以板面为准 ⇒ 须落表 netlist_v1.csv:value + netlist_v1_pins.csv:value ⇒ 重生成 BOM ⇒ 属『板那一趟』同批落表(下一批 · 单号待 main 分配)"
      evidence_level: "[实测]"
  cvbus_gnd:
    in_netlist: true
    netlist_board_col: "CHG_BOARD"
    on_board: true
    on_board_pos: "107.7 42.5"
    on_board_pads: "[{\"num\": \"1\", \"net\": \"GND\"}, {\"num\": \"2\", \"net\": \"VBUS_5V_CHG\"}]"
    drop_reason: "网表 board 列 = CHG_BOARD ⇒ 生成器 BOARD_FILTER=MAIN_PCB 过滤掉 ⇒ 生成板无此封装; 现役官方板上有实物封装 @ (107.7, 42.5) ⇒ 重跑即掉板"
    evidence_level: "[实测]"
  routes:
    A: "路线甲(不重跑生成器·只改现有板上的目标项) | 代价: 这 26 处 Value 原样保留 ⇒ 板面与网表/BOM 三方不一致持续存在; 且「换封装」类目标项(ISS-369 写盘作业包)做不到 ⇒ 换封装必须改几何 = 改板 | 谁拍: main/老板 | 本单不代拍"
    B: "路线乙(重跑生成器·26 处 Value 全被覆盖成生成器口径) | 代价: 13 处脚功能串被换成器件身份串 + 13 处旧选型串被换成新选型串; C_VBUS_GND 掉板(186→185); 40 个位号一次性被打上 DNP 标记(现状零标记); 封装全部重排 + 布线全废 ⇒ 板 md5 变一次但那一趟必须一次做完 | 谁拍: main/老板 | 本单不代拍"
    C: "路线丙(重跑 + 事先把 26 处补成生成器口径/补落表) | 代价: 网表真源要动 ⇒ 落表批次属于『板那一趟』同批; 若裁决=以板面为准则 netlist_v1.csv:value + netlist_v1_pins.csv:value + BOM 三件同批落表; 落表 + 重跑 + 布线 + 留证必须同趟 ⇒ 任何一处漏改 = 板 md5 第二次变 | 谁拍: main/老板 | 本单不代拍"
  decisions:
    route_choice: "not_decided_here"
    value_authority_26_rows: "not_decided_here"
    cvbus_gnd_keep_or_remove: "not_decided_here"
    dnp_mark_batch_size: "not_decided_here"
    landing_batch_id: "not_decided_here"
```

★**★机器块字段说明 (★与本闸 D1~D7 一一对应★)★**:

| 键 | 含义 | 对应判据 |
|---|---|---|
| `board_md5` / `board_mtime` / `board_size` | ★现役板三项指纹 (★自证★) ★ | D7 (★闸运行前后逐字相同★) |
| `netlist_md5` / `bom_md5` | ★网表 / BOM 指纹 (★自证★) ★ | D2 (★台账过期即红★) |
| `rows[]` | ★**26 行**: `ref` / `board_value` / `netlist_value` / `bom_value` / `diff_type` / `affects_electrical` / `landing_owner` / `evidence_level` ★ | D1 / D2 / D3 |
| `row_count` | ★行数 = **26** ★ | D1 (★台账行数必须 == 实测差异条数★) |
| `cvbus_gnd` | ★`in_netlist` / `netlist_board_col` / `on_board` / `on_board_pos` / `on_board_pads` / `drop_reason` / `evidence_level` ★ | D4 |
| `routes` | ★`A` / `B` / `C` 三条路线各一段 (★代价 + 适用条件 + 谁拍★) ★ | D5 |
| `decisions` | ★**逐项 `not_decided_here`** ★ | D6 (★零代拍★) |

★**★机器闸的 rc 口径 (★开工前 rc=1 · 收工后 rc=0 · 一句一句说清·不留给猜★)** ★
> ★**开工前 (真相页未建)** ⇒ `python3 HW/check_generator_value_drift_closed.py` ⇒ ★**rc=1** ★ (★红的是现状: 26 处未登记★) ⇒ ★**原样输出留证: `logs/iss402/gate_baseline_red.txt`★ ★
> ★**收工后 (本页已建 · 26 处逐条登记)** ⇒ ★**rc=0** ★ ⇒ ★**原样输出留证: `logs/iss402/gate_run_green.txt`★ ★
> ★**为什么收工后是绿的 (★逻辑自洽性·不是放水★)**: ★**D1 的判据是「每条实测差异都必须登记」⇒ 登记齐了 D1 就该绿★; ★**而 D6 明令「页里不许出现任何替 main / 老板拍板的措辞」(★禁词清单 = 闸源码里的 `D6_FORBIDDEN` 常量★) ⇒ ★**页永远不许写「已拍/定了」这类字★ ⇒ 若把 rc=1 绑在「处置已决」上, 本闸将【永远红】⇒ 逻辑自相矛盾★** ⇒ ★**故 rc 绑在「登记齐 + 值对得上 + 机理在页 + 三条路线齐 + 零代拍措辞 + 零挂链零写板」上 ⇒ 这是 D1~D7 的字面判据, 本单未加严也未放松★** ★
> ★**★「那一趟」开工前的正确用法 (★★不是「跑绿就开工」★★)**: ★**闸绿 = 「26 处已被登记成台账」; ★★『这 26 处到底以谁为准』由 §4 三条路线的裁决决定 ⇒ ★★裁决没拍之前, 不许开工 (★裁决归 main / 老板·本单不代拍★)★★** ★

---

## ★§7 · 边界自证 (★本单零破界★)★

| 边界 | 自证 |
|---|---|
| ★**零写板** ★ | ★`HW/PCB/demo_mainboard.kicad_pcb` 的 md5 / mtime / size 开工前后逐字相同 (★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ |
| ★**零落表** ★ | ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三份 md5 开工前后逐字相同 ★ |
| ★**零改既有闸判据** ★ | ★跑过的既有闸 (★`HW/check_workpack_state_values.py` / `HW/check_onepass_commit_order.py` / `HW/check_board_frame_caliber.py` / `HW/check_preflight_regen_idempotent.py` / `state/check_pcb_nets.py` / `state/check_pcb_drc.py` / `HW/check_netlist_contradiction_r3.py`★) md5 开工前后逐字相同 ★ |
| ★**零改既有页正文** ★ | ★§1.4 列出的 5 份既有页 md5 开工前后逐字相同 ★ |
| ★**零挂链** ★ | ★`grep -c check_generator_value_drift_closed state/gate_check.py` = **0** ★ |
| ★**零外发** ★ | ★未发任何邮件 / 询价 / 问询 / 采购; `state/outbox/` 未动 ★ |
| ★**不代拍** ★ | ★§4 三条路线 / `C_VBUS_GND` 留不留 / 26 处各以谁为准 ⇒ ★**机器块 `decisions` 逐项 `not_decided_here`** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★一个字都没写 ★ |
| ★**不写别人分片** ★ | ★只写 `state/fragments/hw.yaml` ★ |
| ★**沙盒只落项目盘** ★ | ★沙盒 `tmp/iss402/` + 留证 `logs/iss402/` ⇒ ★**未往系统 `/tmp` 写**; ★**沙盒一律 `shutil.copy2` / 只读解析, 未硬链接真件 (★L-24 血案★)★ ★ |
