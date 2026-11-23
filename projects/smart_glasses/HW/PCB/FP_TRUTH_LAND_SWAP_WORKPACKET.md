# HW/PCB · ISS-364 · 「板那一趟」S10 换封装真值 · 90 件逐件作业包 + C4 目标 68 可达性

> ★**单号**: ISS-364 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯分析 / 作业包 / 新建闸 / 沙盒预演 · ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 零采购 · 不代老板拍板**★
> ★**本单只做 3 件**: ① 本页 (90 件逐件可执行作业包) · ② 一条机器闸 `HW/check_fp_truth_land_swap.py` (L0~L8 + `--selftest`) · ③ 交卷页 + 分片 + 留证 (见 §9)
> ★**本页所有数字由生成器 `logs/iss364/build_land_swap_workpacket.py` 从真源实算生成** ⇒ 零转述误差; 每个数字的复跑命令见 §0 表的「怎么复跑」栏。
> ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS364_C4目标68可达性与90件换封装作业包.md` · ★**留证**: `logs/iss364/` · ★**沙盒**: `tmp/iss364_sbx/`

<!-- BEGIN ISS364 换封装作业包基准块 -->
```json
{
 "issue": "ISS-364",
 "owner": "hw-lead",
 "doc": "HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md",
 "gate": "HW/check_fp_truth_land_swap.py",
 "note": "★本块由 logs/iss364/build_land_swap_workpacket.py 从真源实算生成; 闸 L0 校验它是合法 JSON, L1 校验 counts 与脚本实算逐项相等, L8 校验 §0 的机制读数与 §2 的具名脚总条数==脚本实算★",
 "counts": {
  "c4_total": 158,
  "iss356_total": 100,
  "iss356_main": 78,
  "iss356_chg": 22,
  "inter_total": 77,
  "diff_total": 81,
  "gap_total": 13,
  "board_footprints": 186,
  "target_total": 90,
  "legb_named_pins": 182,
  "legb_rename_cmds": 196,
  "legb_addrow_cmds": 4
 },
 "buckets": {
  "tp": 42,
  "dnp": 26,
  "in_target": 77,
  "gap": 13
 },
 "c4_target": 68,
 "sandbox": {
  "s0_c4": 158,
  "s1_legA_only_c4": 158,
  "s2_legB_only_c4": 68,
  "s3_legA_legB_c4": 68,
  "s4_legA_legB_k3b_c4": 68,
  "legA_delta_c4": 0,
  "legB_delta_c4": -90
 },
 "target_refs": [
  "C_AC_CSI_D0_CK_N",
  "C_AC_CSI_D0_CK_P",
  "C_AC_CSI_D0_D0_N",
  "C_AC_CSI_D0_D0_P",
  "C_AC_CSI_D0_D1_N",
  "C_AC_CSI_D0_D1_P",
  "C_AC_CSI_D0_D2_N",
  "C_AC_CSI_D0_D2_P",
  "C_AC_CSI_D0_D3_N",
  "C_AC_CSI_D0_D3_P",
  "C_BULK_LIGHT_3V3",
  "C_BULK_VDD_1V8_IO",
  "C_BULK_VDD_3V3_IO",
  "C_DET_BAT",
  "C_DET_VBUS_D",
  "C_HF_LIGHT_3V3",
  "C_HF_VDD_1V8_IO",
  "C_HF_VDD_3V3_IO",
  "C_KEY_PWR",
  "C_KEY_VM",
  "C_KEY_VP",
  "C_RST",
  "C_SW_IN",
  "C_SW_OUT",
  "C_TEMP",
  "C_VBUS_DEMO",
  "D_LED_G",
  "D_LED_R",
  "R_BAT_DET_1",
  "R_BAT_DET_2",
  "R_CC1_D",
  "R_CC2_D",
  "R_EN_VCORE",
  "R_JTAG_TCK",
  "R_JTAG_TDI",
  "R_JTAG_TDO",
  "R_JTAG_TMS",
  "R_KEY_CAM",
  "R_KEY_PWR",
  "R_KEY_VM",
  "R_KEY_VP",
  "R_LED_G",
  "R_LED_R",
  "R_PD_ON",
  "R_PG_PULL",
  "R_PU_BOOT_N",
  "R_PU_I2CA_SCL",
  "R_PU_I2CA_SDA",
  "R_PU_I2CB_SCL",
  "R_PU_I2CB_SDA",
  "R_PU_ID0",
  "R_PU_ID1",
  "R_PU_PG",
  "R_PU_RESET_N",
  "R_SEL_CK_N",
  "R_SEL_CK_P",
  "R_SEL_D0_N",
  "R_SEL_D0_P",
  "R_SEL_D1_N",
  "R_SEL_D1_P",
  "R_SEL_D2_N",
  "R_SEL_D2_P",
  "R_SEL_D3_N",
  "R_SEL_D3_P",
  "R_SER_CSI_MCLK",
  "R_SER_FSIN",
  "R_SER_RESET_N",
  "R_SER_SPI_CSn",
  "R_SER_SPI_MISO",
  "R_SER_SPI_MOSI",
  "R_SER_SPI_SCLK",
  "R_SER_USB_D_N",
  "R_SER_USB_D_P",
  "R_SUPV_DIV1",
  "R_SUPV_DIV2",
  "R_VBUS_DET_D1",
  "R_VBUS_DET_D2",
  "CHG_GND_STAR",
  "D_ESD_CAM",
  "D_ESD_DEMO",
  "D_ESD_USB_D",
  "FB_DEMO",
  "Q_AND",
  "Q_ENVC",
  "Q_PG",
  "SW_BOOT",
  "SW_KEY_PWR",
  "SW_KEY_VM",
  "SW_KEY_VP",
  "SW_RST"
 ]
}
```
<!-- END ISS364 换封装作业包基准块 -->

## §0 口径与读数 (★本机实跑, 2026-11-23 · 每个数字都能被本表某一行的命令复现★)

| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |
|---|---|---|---|---|
| 1 | ★**病灶**: 那一趟的验收判据写着「实测 C4 == 68」, 而 C4 的 158 个占位脚号能不能真的收到 68 此前【没有任何沙盒证明】★ | ★**能·且只有一条路能**★ ⇒ 沙盒实跑: ★**腿 B 单独 ⇒ C4 68 → 158**★; ★**腿 A 单独 ⇒ C4 仍是 158**★ | 本单沙盒 `logs/iss364/sandbox_legAB.py` (★C1~C4 读数由 `state/check_pcb_nets.py` 的**真代码**给出·只把 `NET` 常量指向副本·零复制★) | `bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |
| 2 | ★**C4 占位脚号器件**★ | ★**158**★ | `state/check_pcb_nets.py` 的 C4 口径: 网表节点串是 **bare** (无 `pin<N>` / 无 USB-IF 物理脚名) ⇒ 焊盘号按行序占位 | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |
| 3 | ★**ISS-356 封装真值靶子**★ | ★**100**★ (镜脚主 PCB 78 + 镜框充电板 22) | `HW/check_fp_truth_baseline.py` 的 `load_targets()`: 必装 ∩ 非 NET/TP ∩ `footprint=='待定'` | `python3 HW/check_fp_truth_baseline.py` |
| 4 | ★**交集 / 差集 / 缺口**★ | ★**交集 77 · 差集 81 · 缺口 13**★ | 两集合求交/求差 (本单生成器 `logs/iss364/build_iss364_data.py`) | `python3 logs/iss364/build_iss364_data.py` |
| 5 | ★**四桶 (机器跑出来的)**★ | ★**TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158**★ ⇒ ★**豁免 68 (TP+DNP) + 要收口 90**★ ⇒ ★**C4 目标 = 158 − 90 = 68**★ | 分桶优先级: TP 优先 ⇒ DNP 次之 ⇒ 其余归缺口 (★与 ISS-361 同口径★) | 同上 |
| 6 | ★**本单的对象**★ | ★**90 件 = 靶内 77 + 缺口 13**★ (★与基线《订正一》的「90 件」同数★) | 交集 + 缺口 并集 (本单生成器) | `python3 logs/iss364/build_iss364_data.py` |
| 7 | ★**两条腿的区别 (决定闸不许判什么)**★ | ★**C4 数的是「网表节点串是不是 bare」, 不是「land 是不是官方封装」**★ ⇒ 沙盒实测: ★**腿 A 单独 ⇒ ΔC4 = +0**★ (板面 90 件 land 全换官方封装, C4 读数一字不动) ⇒ ★**腿 B 单独 ⇒ ΔC4 = -90**★ (板面零改动) ⇒ ★**⇒ 腿 B 才是本单的真命门**★ | ★C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自 `HW/netlist_v1.csv`, **板在它之后才被读**★ | `bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |
| 8 | ★**板面封装的真实状态 (决定闸不许判什么)**★ | ★**板面 186 个封装的库名全空**★ (★`GetFPIDAsString()` 唯一值 = `''`★) ⇒ ★**板是【自绘通用占位】, 不是「库名写错」**★ ⇒ ★**新建的闸不许判「板面 lib:name == 台账的 lib:name」 (★恒无意义·哑弹★) ⇒ 必须判几何**★ | `bash state/pcbnew_py.sh` 读 `GetFPIDAsString()`; 纯文本口径见 `logs/iss361/zz_board_probe.py` | 同左 |
| 9 | ★**板侧那 5 条差异 (本单要把它们跟 90 件绑在一张表上)**★ | ★**C1 读数: 缺 0 · 多 2 · 同号异网 3**★ ⇒ 多余 2 = `C_VBUS_GND` pad1/pad2 · 同号异网 3 = `Q_PG` pad1/pad3 对调 + `D_ESD_USB_D` pad1 错★ ⇒ ★**本单另挖出第 6 条 (`R_PU_PG` pad1/pad2 与脚表真值相反) — C1 看不见 (电阻对称) 但腿 A 必须改**★ | `state/check_pcb_nets.py` 的 C1 段 + 板面读数 | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |
| 10 | ★**腿 B 作业包的规模**★ | ★**具名脚 182 只 (= 90 件脚数之和) · 改名指令 196 条 · 补行指令 4 条 = 合计 200 条**★ | ★**具名脚真值已经在 `HW/netlist_v1_pins.csv` 的 `pin` 栏里 (★按表头名定位·不写死列号★)★ ⇒ 本单只是把它**落到 `HW/netlist_v1.csv` 的 node1/node2 栏** | 本单生成器 `logs/iss364/analyze_legB.py` | `python3 logs/iss364/analyze_legB.py` |
| 11 | ★**沙盒可达性 (四条腿的组合)**★ | ★**S0 C4=158 · S1 腿A单独 C4=158 (Δ+0) · S2 腿B单独 C4=68 (Δ-90) · S3 腿A+腿B C4=68 · S4 腿A+腿B 且 K3 走 (b) 路 C4=68**★ ⇒ ★**C4 目标 68 是可达的, 且【只有腿 B 能到】**★ | 板副本 + 网表副本落 `tmp/iss364_sbx/`, C1~C4 读数由真闸代码给出 | `bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py` |
| 12 | ★**沙盒之外零改动 (指纹双证)**★ | 板 md5 `611b869e13518c3c023fb178f91a0075` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` | 开工前后各打一次 | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` |

★**§0 的 12 行读数全部复现自同一批真源文件; 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 开工前后逐字节未变**★。

★**「fab 外框」栏的口径 (★本页与机器闸 L5 用同一个定义★)**: ★**`F.Fab` 层上 `fp_line` / `fp_rect` 的包围盒**★。★**本机实测: 有些官方封装在 `F.Fab` 层根本没有外框** ★ (★`Package_TO_SOT_SMD:SOT-23` 与 `TestPoint:TestPoint_Pad_D1.0mm` 实测 = 0.00×0.00 ⇒ 它们的外框只画在 `F.CrtYd`/`F.SilkS` 上★) ⇒ ★**那种情况本页写 `0.00×0.00 mm` 并附 `[F.Fab 层无外框; CrtYd 包围盒 W×H mm]`, Δ 栏写「Δfab 不适用」** ★ ⇒ ★**⇒ 90 件的 Δfab 有 4 件不适用 (全是目标封装 F.Fab 层本身无外框·不是本单漏测)**★。

## §1 逐件 90 行表 (一 ref 一行 · 12 字段固定)

★**「现占位几何」栏读板 (★`HW/PCB/demo_mainboard.kicad_pcb` 纯文本解析·[实测]★); 「目标几何」栏读 `.kicad_mod` 本身 (★**不照抄台账** — 台账只给 `lib:name` + md5, 没给几何★)**★。

| ref | 桶 | 现占位几何 [实测] | 目标 `lib:name` | `.kicad_mod` 实存路径 + md5 | 目标几何 [实测] | 几何 Δ | pad↔net 序要改哪几条 | 要重接的 net 名单 | 腿 B 具名脚清单 (bare → `pinN`) | 证据等级 | 降级方案 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `C_AC_CSI_D0_CK_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_CK_N_SRC`, `CSI_D0_CK_N` | C_AC_CSI_D0_CK_N → C_AC_CSI_D0_CK_N pin1 (net `CSI_D0_CK_N_SRC`); C_AC_CSI_D0_CK_N → C_AC_CSI_D0_CK_N pin2 (net `CSI_D0_CK_N`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_CK_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_CK_P_SRC`, `CSI_D0_CK_P` | C_AC_CSI_D0_CK_P → C_AC_CSI_D0_CK_P pin1 (net `CSI_D0_CK_P_SRC`); C_AC_CSI_D0_CK_P → C_AC_CSI_D0_CK_P pin2 (net `CSI_D0_CK_P`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D0_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D0_N_SRC`, `CSI_D0_D0_N` | C_AC_CSI_D0_D0_N → C_AC_CSI_D0_D0_N pin1 (net `CSI_D0_D0_N_SRC`); C_AC_CSI_D0_D0_N → C_AC_CSI_D0_D0_N pin2 (net `CSI_D0_D0_N`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D0_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D0_P_SRC`, `CSI_D0_D0_P` | C_AC_CSI_D0_D0_P → C_AC_CSI_D0_D0_P pin1 (net `CSI_D0_D0_P_SRC`); C_AC_CSI_D0_D0_P → C_AC_CSI_D0_D0_P pin2 (net `CSI_D0_D0_P`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D1_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D1_N_SRC`, `CSI_D0_D1_N` | C_AC_CSI_D0_D1_N → C_AC_CSI_D0_D1_N pin1 (net `CSI_D0_D1_N_SRC`); C_AC_CSI_D0_D1_N → C_AC_CSI_D0_D1_N pin2 (net `CSI_D0_D1_N`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D1_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D1_P_SRC`, `CSI_D0_D1_P` | C_AC_CSI_D0_D1_P → C_AC_CSI_D0_D1_P pin1 (net `CSI_D0_D1_P_SRC`); C_AC_CSI_D0_D1_P → C_AC_CSI_D0_D1_P pin2 (net `CSI_D0_D1_P`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D2_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D2_N_SRC`, `CSI_D0_D2_N` | C_AC_CSI_D0_D2_N → C_AC_CSI_D0_D2_N pin1 (net `CSI_D0_D2_N_SRC`); C_AC_CSI_D0_D2_N → C_AC_CSI_D0_D2_N pin2 (net `CSI_D0_D2_N`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D2_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D2_P_SRC`, `CSI_D0_D2_P` | C_AC_CSI_D0_D2_P → C_AC_CSI_D0_D2_P pin1 (net `CSI_D0_D2_P_SRC`); C_AC_CSI_D0_D2_P → C_AC_CSI_D0_D2_P pin2 (net `CSI_D0_D2_P`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D3_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D3_N_SRC`, `CSI_D0_D3_N` | C_AC_CSI_D0_D3_N → C_AC_CSI_D0_D3_N pin1 (net `CSI_D0_D3_N_SRC`); C_AC_CSI_D0_D3_N → C_AC_CSI_D0_D3_N pin2 (net `CSI_D0_D3_N`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D3_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `CSI_D0_D3_P_SRC`, `CSI_D0_D3_P` | C_AC_CSI_D0_D3_P → C_AC_CSI_D0_D3_P pin1 (net `CSI_D0_D3_P_SRC`); C_AC_CSI_D0_D3_P → C_AC_CSI_D0_D3_P pin2 (net `CSI_D0_D3_P`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_LIGHT_3V3` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `LIGHT_3V3`, `GND` | C_BULK_LIGHT_3V3 → C_BULK_LIGHT_3V3 pin1 (net `LIGHT_3V3`); C_BULK_LIGHT_3V3 → C_BULK_LIGHT_3V3 pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_VDD_1V8_IO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `VDD_1V8_IO`, `GND` | C_BULK_VDD_1V8_IO → C_BULK_VDD_1V8_IO pin1 (net `VDD_1V8_IO`); C_BULK_VDD_1V8_IO → C_BULK_VDD_1V8_IO pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_VDD_3V3_IO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `VDD_3V3_IO`, `GND` | C_BULK_VDD_3V3_IO → C_BULK_VDD_3V3_IO pin1 (net `VDD_3V3_IO`); C_BULK_VDD_3V3_IO → C_BULK_VDD_3V3_IO pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_DET_BAT` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `BAT_DET`, `GND` | C_DET_BAT → C_DET_BAT pin1 (net `BAT_DET`); C_DET_BAT → C_DET_BAT pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_DET_VBUS_D` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `GND`, `VBUS_DET_D` | C_DET_VBUS_D → C_DET_VBUS_D pin1 (net `GND`); C_DET_VBUS_D → C_DET_VBUS_D pin2 (net `VBUS_DET_D`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_LIGHT_3V3` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `LIGHT_3V3`, `GND` | C_HF_LIGHT_3V3 → C_HF_LIGHT_3V3 pin1 (net `LIGHT_3V3`); C_HF_LIGHT_3V3 → C_HF_LIGHT_3V3 pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_VDD_1V8_IO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `VDD_1V8_IO`, `GND` | C_HF_VDD_1V8_IO → C_HF_VDD_1V8_IO pin1 (net `VDD_1V8_IO`); C_HF_VDD_1V8_IO → C_HF_VDD_1V8_IO pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_VDD_3V3_IO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `VDD_3V3_IO`, `GND` | C_HF_VDD_3V3_IO → C_HF_VDD_3V3_IO pin1 (net `VDD_3V3_IO`); C_HF_VDD_3V3_IO → C_HF_VDD_3V3_IO pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_KEY_PWR` | 靶内 | 焊盘 1 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.20×-0.20 mm · Δ中心距 +1.550 mm | 无 | `KEY_PWR`, `GND` | C_KEY_PWR → C_KEY_PWR pin1 (net `KEY_PWR`); ★补行★ C_KEY_PWR pin2 (net `GND`) | [实测]+[推算] | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_KEY_VM` | 靶内 | 焊盘 1 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.20×-0.20 mm · Δ中心距 +1.550 mm | 无 | `KEY_VOL_M`, `GND` | C_KEY_VM → C_KEY_VM pin1 (net `KEY_VOL_M`); ★补行★ C_KEY_VM pin2 (net `GND`) | [实测]+[推算] | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_KEY_VP` | 靶内 | 焊盘 1 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 0.000 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +1 · Δfab -0.20×-0.20 mm · Δ中心距 +1.550 mm | 无 | `KEY_VOL_P`, `GND` | C_KEY_VP → C_KEY_VP pin1 (net `KEY_VOL_P`); ★补行★ C_KEY_VP pin2 (net `GND`) | [实测]+[推算] | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_RST` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `RESET_N_SOC`, `GND` | C_RST → C_RST pin1 (net `RESET_N_SOC`); C_RST → C_RST pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_SW_IN` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `BAT_SW`, `GND` | C_SW_IN → C_SW_IN pin1 (net `BAT_SW`); C_SW_IN → C_SW_IN pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_SW_OUT` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `SYS`, `GND` | C_SW_OUT → C_SW_OUT pin1 (net `SYS`); C_SW_OUT → C_SW_OUT pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_TEMP` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `VDD_3V3_IO`, `GND` | C_TEMP → C_TEMP pin1 (net `VDD_3V3_IO`); C_TEMP → C_TEMP pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_VBUS_DEMO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Capacitor_SMD:C_0603_1608Metric` | `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` md5 `0641b49cd03997f007054fc64a50c3e3` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.550 mm | Δ焊盘数 +0 · Δfab -0.20×-0.20 mm · Δ中心距 -0.050 mm | 无 | `RAIL_DEMO_5V`, `GND` | C_VBUS_DEMO → C_VBUS_DEMO pin1 (net `RAIL_DEMO_5V`); C_VBUS_DEMO → C_VBUS_DEMO pin2 (net `GND`) | [实测] | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `D_LED_G` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `LED_SMD:LED_0805_2012Metric` | `LED_SMD.pretty/LED_0805_2012Metric.kicad_mod` md5 `7616eddd0b9951dec0bf5bdfc3df0a77` | 焊盘数 2 · fab 外框 2.00×1.20 mm · 中心距 1.875 mm | Δ焊盘数 +0 · Δfab -0.70×-0.40 mm · Δ中心距 -0.425 mm | 无 | `LED_G_D`, `GND` | D_LED_G → D_LED_G pin1 (net `LED_G_D`); D_LED_G → D_LED_G pin2 (net `GND`) | [实测]+[官网] | 若 0805 绿无官网现货 ⇒ 换同封装 0805 绿等效件 (Kingbright AP2012 系列); 若要两颗同封装 ⇒ 两颗都改 0805 (ISS-241 §⑬ 已把"对称性"留给 main, 本单沿用不代裁) ⇒ 代价 = 红件 OPN 要重查 + 亮度账 (G-5) 重算 |
| `D_LED_R` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `LED_SMD:LED_0603_1608Metric` | `LED_SMD.pretty/LED_0603_1608Metric.kicad_mod` md5 `ac369a6895f54b78d16871a76dc9d08e` | 焊盘数 2 · fab 外框 1.60×0.80 mm · 中心距 1.575 mm | Δ焊盘数 +0 · Δfab -1.10×-0.80 mm · Δ中心距 -0.725 mm | 无 | `LED_R_D`, `GND` | D_LED_R → D_LED_R pin1 (net `LED_R_D`); D_LED_R → D_LED_R pin2 (net `GND`) | [实测]+[官网] | 若 0603 PLCC-2 红无官网现货 ⇒ 换同封装 0603 PLCC-2 等效件; 注意 PLCC-2 与普通 0603 chip 的引脚几何不同 ⇒ 落板批次按原厂 land 重画 (ISS-241 §⑬ 已记) |
| `R_BAT_DET_1` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `BAT_DET`, `BAT` | R_BAT_DET_1 → R_BAT_DET_1 pin1 (net `BAT_DET`); R_BAT_DET_1 → R_BAT_DET_1 pin2 (net `BAT`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_BAT_DET_2` | 靶内 | 焊盘 1 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 0.000 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +1 · Δfab -0.20×-0.18 mm · Δ中心距 +1.650 mm | 无 | `BAT_DET`, `GND` | R_BAT_DET_2 → R_BAT_DET_2 pin1 (net `BAT_DET`); ★补行★ R_BAT_DET_2 pin2 (net `GND`) | [实测]+[推算] | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `R_CC1_D` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `GND`, `USB_CC1` | R_CC1_D → R_CC1_D pin1 (net `GND`); R_CC1_D → R_CC1_D pin2 (net `USB_CC1`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_CC2_D` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `USB_CC2`, `GND` | R_CC2_D → R_CC2_D pin1 (net `USB_CC2`); R_CC2_D → R_CC2_D pin2 (net `GND`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_EN_VCORE` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `EN_VCORE`, `VDD_1V8_IO` | R_EN_VCORE → R_EN_VCORE pin1 (net `EN_VCORE`); R_EN_VCORE → R_EN_VCORE pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TCK` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `JTAG_TCK_SOC`, `JTAG_TCK` | R_JTAG_TCK → R_JTAG_TCK pin1 (net `JTAG_TCK_SOC`); R_JTAG_TCK → R_JTAG_TCK pin2 (net `JTAG_TCK`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TDI` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `JTAG_TDI_SOC`, `JTAG_TDI` | R_JTAG_TDI → R_JTAG_TDI pin1 (net `JTAG_TDI_SOC`); R_JTAG_TDI → R_JTAG_TDI pin2 (net `JTAG_TDI`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TDO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `JTAG_TDO_SOC`, `JTAG_TDO` | R_JTAG_TDO → R_JTAG_TDO pin1 (net `JTAG_TDO_SOC`); R_JTAG_TDO → R_JTAG_TDO pin2 (net `JTAG_TDO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TMS` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `JTAG_TMS_SOC`, `JTAG_TMS` | R_JTAG_TMS → R_JTAG_TMS pin1 (net `JTAG_TMS_SOC`); R_JTAG_TMS → R_JTAG_TMS pin2 (net `JTAG_TMS`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_CAM` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `KEY_CAM`, `VDD_3V3_IO` | R_KEY_CAM → R_KEY_CAM pin1 (net `KEY_CAM`); R_KEY_CAM → R_KEY_CAM pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_PWR` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `KEY_PWR`, `VDD_3V3_IO` | R_KEY_PWR → R_KEY_PWR pin1 (net `KEY_PWR`); R_KEY_PWR → R_KEY_PWR pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_VM` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `KEY_VOL_M`, `VDD_3V3_IO` | R_KEY_VM → R_KEY_VM pin1 (net `KEY_VOL_M`); R_KEY_VM → R_KEY_VM pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_VP` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `KEY_VOL_P`, `VDD_3V3_IO` | R_KEY_VP → R_KEY_VP pin1 (net `KEY_VOL_P`); R_KEY_VP → R_KEY_VP pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_LED_G` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `LED_G`, `LED_G_D` | R_LED_G → R_LED_G pin1 (net `LED_G`); R_LED_G → R_LED_G pin2 (net `LED_G_D`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_LED_R` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `LED_R`, `LED_R_D` | R_LED_R → R_LED_R pin1 (net `LED_R`); R_LED_R → R_LED_R pin2 (net `LED_R_D`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PD_ON` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `PWR_ON`, `GND` | R_PD_ON → R_PD_ON pin1 (net `PWR_ON`); R_PD_ON → R_PD_ON pin2 (net `GND`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PG_PULL` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `PG_AND`, `VDD_1V8_IO` | R_PG_PULL → R_PG_PULL pin1 (net `PG_AND`); R_PG_PULL → R_PG_PULL pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_BOOT_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `BOOT_N`, `VDD_1V8_IO` | R_PU_BOOT_N → R_PU_BOOT_N pin1 (net `BOOT_N`); R_PU_BOOT_N → R_PU_BOOT_N pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CA_SCL` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `I2C_A_SCL`, `VDD_1V8_IO` | R_PU_I2CA_SCL → R_PU_I2CA_SCL pin1 (net `I2C_A_SCL`); R_PU_I2CA_SCL → R_PU_I2CA_SCL pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CA_SDA` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `I2C_A_SDA`, `VDD_1V8_IO` | R_PU_I2CA_SDA → R_PU_I2CA_SDA pin1 (net `I2C_A_SDA`); R_PU_I2CA_SDA → R_PU_I2CA_SDA pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CB_SCL` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `I2C_B_SCL`, `VDD_3V3_IO` | R_PU_I2CB_SCL → R_PU_I2CB_SCL pin1 (net `I2C_B_SCL`); R_PU_I2CB_SCL → R_PU_I2CB_SCL pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CB_SDA` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `I2C_B_SDA`, `VDD_3V3_IO` | R_PU_I2CB_SDA → R_PU_I2CB_SDA pin1 (net `I2C_B_SDA`); R_PU_I2CB_SDA → R_PU_I2CB_SDA pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_ID0` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `ID_DETECT_0`, `VDD_3V3_IO` | R_PU_ID0 → R_PU_ID0 pin1 (net `ID_DETECT_0`); R_PU_ID0 → R_PU_ID0 pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_ID1` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `ID_DETECT_1`, `VDD_3V3_IO` | R_PU_ID1 → R_PU_ID1 pin1 (net `ID_DETECT_1`); R_PU_ID1 → R_PU_ID1 pin2 (net `VDD_3V3_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_PG` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | pad1: VDD_3V3_IO → PWR_GOOD; pad2: PWR_GOOD → VDD_3V3_IO | `VDD_3V3_IO`, `PWR_GOOD` | R_PU_PG → R_PU_PG pin2 (net `VDD_3V3_IO`); R_PU_PG → R_PU_PG pin1 (net `PWR_GOOD`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_RESET_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `RESET_N`, `VDD_1V8_IO` | R_PU_RESET_N → R_PU_RESET_N pin1 (net `RESET_N`); R_PU_RESET_N → R_PU_RESET_N pin2 (net `VDD_1V8_IO`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_CK_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_CK_N_SRC`, `DSI_D0_CK_N` | R_SEL_CK_N → R_SEL_CK_N pin1 (net `DSI_D0_CK_N_SRC`); R_SEL_CK_N → R_SEL_CK_N pin2 (net `DSI_D0_CK_N`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_CK_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_CK_P_SRC`, `DSI_D0_CK_P` | R_SEL_CK_P → R_SEL_CK_P pin1 (net `DSI_D0_CK_P_SRC`); R_SEL_CK_P → R_SEL_CK_P pin2 (net `DSI_D0_CK_P`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D0_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D0_N_SRC`, `DSI_D0_D0_N` | R_SEL_D0_N → R_SEL_D0_N pin1 (net `DSI_D0_D0_N_SRC`); R_SEL_D0_N → R_SEL_D0_N pin2 (net `DSI_D0_D0_N`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D0_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D0_P_SRC`, `DSI_D0_D0_P` | R_SEL_D0_P → R_SEL_D0_P pin1 (net `DSI_D0_D0_P_SRC`); R_SEL_D0_P → R_SEL_D0_P pin2 (net `DSI_D0_D0_P`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D1_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D1_N_SRC`, `DSI_D0_D1_N` | R_SEL_D1_N → R_SEL_D1_N pin1 (net `DSI_D0_D1_N_SRC`); R_SEL_D1_N → R_SEL_D1_N pin2 (net `DSI_D0_D1_N`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D1_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D1_P_SRC`, `DSI_D0_D1_P` | R_SEL_D1_P → R_SEL_D1_P pin1 (net `DSI_D0_D1_P_SRC`); R_SEL_D1_P → R_SEL_D1_P pin2 (net `DSI_D0_D1_P`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D2_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D2_N_SRC`, `DSI_D0_D2_N` | R_SEL_D2_N → R_SEL_D2_N pin1 (net `DSI_D0_D2_N_SRC`); R_SEL_D2_N → R_SEL_D2_N pin2 (net `DSI_D0_D2_N`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D2_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D2_P_SRC`, `DSI_D0_D2_P` | R_SEL_D2_P → R_SEL_D2_P pin1 (net `DSI_D0_D2_P_SRC`); R_SEL_D2_P → R_SEL_D2_P pin2 (net `DSI_D0_D2_P`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D3_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D3_N_SRC`, `DSI_D0_D3_N` | R_SEL_D3_N → R_SEL_D3_N pin1 (net `DSI_D0_D3_N_SRC`); R_SEL_D3_N → R_SEL_D3_N pin2 (net `DSI_D0_D3_N`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D3_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `DSI_D0_D3_P_SRC`, `DSI_D0_D3_P` | R_SEL_D3_P → R_SEL_D3_P pin1 (net `DSI_D0_D3_P_SRC`); R_SEL_D3_P → R_SEL_D3_P pin2 (net `DSI_D0_D3_P`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_CSI_MCLK` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `CSI_MCLK_SRC`, `CSI_MCLK` | R_SER_CSI_MCLK → R_SER_CSI_MCLK pin1 (net `CSI_MCLK_SRC`); R_SER_CSI_MCLK → R_SER_CSI_MCLK pin2 (net `CSI_MCLK`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_FSIN` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `FSIN_OUT`, `FSIN` | R_SER_FSIN → R_SER_FSIN pin1 (net `FSIN_OUT`); R_SER_FSIN → R_SER_FSIN pin2 (net `FSIN`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_RESET_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `RESET_N`, `RESET_N_SOC` | R_SER_RESET_N → R_SER_RESET_N pin1 (net `RESET_N`); R_SER_RESET_N → R_SER_RESET_N pin2 (net `RESET_N_SOC`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_CSn` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `SPI_CSn`, `SPI_CSn_BOOT` | R_SER_SPI_CSn → R_SER_SPI_CSn pin1 (net `SPI_CSn`); R_SER_SPI_CSn → R_SER_SPI_CSn pin2 (net `SPI_CSn_BOOT`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_MISO` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `SPI_MISO`, `SPI_MISO_BOOT` | R_SER_SPI_MISO → R_SER_SPI_MISO pin1 (net `SPI_MISO`); R_SER_SPI_MISO → R_SER_SPI_MISO pin2 (net `SPI_MISO_BOOT`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_MOSI` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `SPI_MOSI`, `SPI_MOSI_BOOT` | R_SER_SPI_MOSI → R_SER_SPI_MOSI pin1 (net `SPI_MOSI`); R_SER_SPI_MOSI → R_SER_SPI_MOSI pin2 (net `SPI_MOSI_BOOT`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_SCLK` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `SPI_SCLK`, `SPI_SCLK_BOOT` | R_SER_SPI_SCLK → R_SER_SPI_SCLK pin1 (net `SPI_SCLK`); R_SER_SPI_SCLK → R_SER_SPI_SCLK pin2 (net `SPI_SCLK_BOOT`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_USB_D_N` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `USB_D_N_SRC`, `NET_USB_D_N_TYPEC` | R_SER_USB_D_N → R_SER_USB_D_N pin1 (net `USB_D_N_SRC`); R_SER_USB_D_N → R_SER_USB_D_N pin2 (net `NET_USB_D_N_TYPEC`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_USB_D_P` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `USB_D_P_SRC`, `NET_USB_D_P_TYPEC` | R_SER_USB_D_P → R_SER_USB_D_P pin1 (net `USB_D_P_SRC`); R_SER_USB_D_P → R_SER_USB_D_P pin2 (net `NET_USB_D_P_TYPEC`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SUPV_DIV1` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `V_SOC_IO`, `SUPV_SENSE` | R_SUPV_DIV1 → R_SUPV_DIV1 pin1 (net `V_SOC_IO`); R_SUPV_DIV1 → R_SUPV_DIV1 pin2 (net `SUPV_SENSE`) | [实测]+[官网] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SUPV_DIV2` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `SUPV_SENSE`, `GND` | R_SUPV_DIV2 → R_SUPV_DIV2 pin1 (net `SUPV_SENSE`); R_SUPV_DIV2 → R_SUPV_DIV2 pin2 (net `GND`) | [实测]+[官网] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_VBUS_DET_D1` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `RAIL_DEMO_5V`, `VBUS_DET_D` | R_VBUS_DET_D1 → R_VBUS_DET_D1 pin1 (net `RAIL_DEMO_5V`); R_VBUS_DET_D1 → R_VBUS_DET_D1 pin2 (net `VBUS_DET_D`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_VBUS_DET_D2` | 靶内 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 1.80×1.00 mm · 中心距 1.600 mm | `Resistor_SMD:R_0603_1608Metric` | `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` md5 `fa9f0fce044a12e2a675c087b781ae3d` | 焊盘数 2 · fab 外框 1.60×0.82 mm · 中心距 1.650 mm | Δ焊盘数 +0 · Δfab -0.20×-0.18 mm · Δ中心距 +0.050 mm | 无 | `VBUS_DET_D`, `GND` | R_VBUS_DET_D2 → R_VBUS_DET_D2 pin1 (net `VBUS_DET_D`); R_VBUS_DET_D2 → R_VBUS_DET_D2 pin2 (net `GND`) | [实测] | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `CHG_GND_STAR` | 缺口 | 焊盘 1 · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 0.000 mm | `TestPoint:TestPoint_Pad_D1.0mm` | `TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` md5 `cea8eb3ba9b799767624661848b00243` | 焊盘数 1 · fab 外框 0.00×0.00 mm · 中心距 0.000 mm · ★[F.Fab 层无外框; CrtYd 包围盒 0.00×0.00 mm]★ | Δ焊盘数 +0 · Δfab 不适用(★目标 F.Fab 层无外框·本机实测★) · Δ中心距 +0.000 mm | 无 | `GND` | CHG_GND_STAR → CHG_GND_STAR pin1 (net `GND`) | [实测] · [0数据] | 若落表批次要把它当可拆件 ⇒ 改用 2 焊盘件 (例 `Diode_SMD:D_SOD-323` md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = 新增第 2 脚 + 网表加 GND 以外的第二个网 ⇒ 与单点汇流位的功能定义冲突 ⇒ 不建议 |
| `D_ESD_CAM` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2 · fab 外框 1.00×0.60 mm · 中心距 0.700 mm | Δ焊盘数 +0 · Δfab -1.70×-1.00 mm · Δ中心距 -1.600 mm | 无 | `GND`, `CSI_D0_CK_P` | D_ESD_CAM → D_ESD_CAM pin1 (net `GND`); D_ESD_CAM → D_ESD_CAM pin2 (net `CSI_D0_CK_P`) | [实测] · [官网] | 若 TI X1SON-2 封装在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 无第二档 ⇒ 改用 2 脚 SOD-323 单通道件 `Diode_SMD:D_SOD-323` (md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = Cd 0.42pF → 45pF ⇒ CSI-2 高速线上不可用 (Cd 45pF 会吃掉眼图裕量) ⇒ 不建议 |
| `D_ESD_DEMO` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Diode_SMD:D_SOD-323` | `Diode_SMD.pretty/D_SOD-323.kicad_mod` md5 `bce0278c9b9af83e2de3cd130e6c04ed` | 焊盘数 2 · fab 外框 1.80×1.40 mm · 中心距 2.100 mm | Δ焊盘数 +0 · Δfab -0.90×-0.20 mm · Δ中心距 -0.200 mm | 无 | `RAIL_DEMO_5V`, `GND` | D_ESD_DEMO → D_ESD_DEMO pin1 (net `RAIL_DEMO_5V`); D_ESD_DEMO → D_ESD_DEMO pin2 (net `GND`) | [实测] · [官网] | 若 SOD-323 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Diode_SMD:D_SOD-323F` (SOD-323 带引脚变体) ⇒ 代价 = 焊接方式变 ⇒ 钢网要改 ⇒ 不建议; 或改小封装 `Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm` (md5 `c57a4058f16cf35599c2b748b9434350`) ⇒ 代价 = 手工贴装 + 板面更挤 ⇒ 不建议 |
| `D_ESD_USB_D` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2 · fab 外框 1.00×0.60 mm · 中心距 0.700 mm | Δ焊盘数 +0 · Δfab -1.70×-1.00 mm · Δ中心距 -1.600 mm | pad1: USB_D_P_SRC → NET_USB_D_P_TYPEC | `USB_D_P_SRC`, `GND` | D_ESD_USB_D → D_ESD_USB_D pin1 (net `NET_USB_D_P_TYPEC`); D_ESD_USB_D → D_ESD_USB_D pin2 (net `GND`) | [实测] · [0数据] | ★3 脚档的候选封装随 W-1/W-2 分叉★ ⇒ 若拍「一颗双通道 3 脚」⇒ 候选 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`, 3 焊盘) ⇒ 代价 = ★**pad 序须按最终型号厂商 land 复核**★ (本栏 SOT-23-3 只是几何候选, 不是代拍); 若拍「两颗单通道」⇒ 本行保持 2 脚 X1SON-2 + 另加一只 2 脚件 (D− 侧) ⇒ 代价 = 板上多一颗件 + 两处 land 都要画 ⇒ 仍在本趟内可完成 |
| `FB_DEMO` | 缺口 | 焊盘 1+2 · 0.550×0.900 mm · fab 外框 2.00×1.60 mm · 中心距 1.000 mm | `Inductor_SMD:L_0805_2012Metric` | `Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod` md5 `4e67ede5911eab38accb2ef9e57de79c` | 焊盘数 2 · fab 外框 2.00×0.90 mm · 中心距 2.125 mm | Δ焊盘数 +0 · Δfab +0.00×-0.70 mm · Δ中心距 +1.125 mm | 无 | `RAIL_DEMO_5V`, `GND` | FB_DEMO → FB_DEMO pin1 (net `RAIL_DEMO_5V`); FB_DEMO → FB_DEMO pin2 (net `GND`) | [实测] · [官网] | 若 Murata 0805 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Inductor_SMD:L_0805_2012Metric` 唯一档 ⇒ 改用更小 0603 (如 `Inductor_SMD:L_0603_1608Metric`) ⇒ 代价 = 电流 2A 降额到 1A 级 (BLM21PG 2000mA 是选型硬判据) ⇒ 不建议 |
| `Q_AND` | 缺口 | 焊盘 1+2+3 · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.00×0.00 mm · 中心距 2.102 mm · ★[F.Fab 层无外框; CrtYd 包围盒 3.86×3.40 mm]★ | Δ焊盘数 +0 · Δfab 不适用(★目标 F.Fab 层无外框·本机实测★) · Δ中心距 -2.781 mm | 无 | `RESET_N`, `GND`, `PG_AND` | Q_AND → Q_AND pin1 (net `RESET_N`); Q_AND → Q_AND pin2 (net `GND`); Q_AND → Q_AND pin3 (net `PG_AND`) | [实测] · [官网] | 若 SOT-23 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_TO_SOT_SMD:SOT-23` 唯一档 ⇒ 换 SOT-23 的 TO-236 变体 (`Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ ★**代价 = 厂商脚序可能不同, 必须逐颗重核 1=G/2=S/3=D**★ ⇒ 不省事, 不建议 |
| `Q_ENVC` | 缺口 | 焊盘 1+2+3 · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.00×0.00 mm · 中心距 2.102 mm · ★[F.Fab 层无外框; CrtYd 包围盒 3.86×3.40 mm]★ | Δ焊盘数 +0 · Δfab 不适用(★目标 F.Fab 层无外框·本机实测★) · Δ中心距 -2.781 mm | 无 | `PG_AND`, `GND`, `EN_VCORE` | Q_ENVC → Q_ENVC pin1 (net `PG_AND`); Q_ENVC → Q_ENVC pin2 (net `GND`); Q_ENVC → Q_ENVC pin3 (net `EN_VCORE`) | [实测] · [官网] | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `Q_PG` | 缺口 | 焊盘 1+2+3 · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3 · fab 外框 0.00×0.00 mm · 中心距 2.102 mm · ★[F.Fab 层无外框; CrtYd 包围盒 3.86×3.40 mm]★ | Δ焊盘数 +0 · Δfab 不适用(★目标 F.Fab 层无外框·本机实测★) · Δ中心距 -2.781 mm | pad1: PWR_ON → PWR_GOOD; pad3: PWR_GOOD → PWR_ON | `PWR_ON`, `BAT_SW`, `PWR_GOOD` | Q_PG → Q_PG pin1 (net `PWR_GOOD`); Q_PG → Q_PG pin2 (net `BAT_SW`); Q_PG → Q_PG pin3 (net `PWR_ON`) | [实测] · [官网] | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `SW_BOOT` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.20×2.80 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.20×-0.20 mm · Δ中心距 +2.201 mm | 无 | `BOOT_N`, `GND` | SW_BOOT → SW_BOOT pin1 (net `BOOT_N`); SW_BOOT → SW_BOOT pin2 (net `GND`) | [实测] · [官网] | ★若不改网表 ⇒ 只能选 2 land 的按键封装★ ⇒ 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` (md5 `749f20c5ab898069ade01682274c7bbf`, 2 焊盘 @3.400 mm, 本体 3.0×2.5mm) ⇒ 代价 = 按动力度 1.5N vs KMR2 的 3.0N ⇒ BOOT 键误触风险上升 (矩阵 §⑮ 选 3N 的理由就是防误触) ⇒ ★**这是选型代价, 不是本单能拍的**★; 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, C&K KXT3) ⇒ 代价 = 同上, 且本体 3.5×2.0 |
| `SW_KEY_PWR` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.20×2.80 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.20×-0.20 mm · Δ中心距 +2.201 mm | 无 | `KEY_PWR`, `GND` | SW_KEY_PWR → SW_KEY_PWR pin1 (net `KEY_PWR`); SW_KEY_PWR → SW_KEY_PWR pin2 (net `GND`) | [实测] · [官网] | 同 SW_BOOT: 不改网表则只能选 2 land 封装 (`SW_SPST_B3U-1000P` md5 `749f20c5ab898069ade01682274c7bbf` / `SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 按动力度降到 1.5N ⇒ 电源键误触风险上升 ⇒ ★不代拍★ |
| `SW_KEY_VM` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2 · fab 外框 3.00×2.50 mm · 中心距 3.400 mm | Δ焊盘数 +0 · Δfab +0.00×-0.50 mm · Δ中心距 +1.200 mm | 无 | `KEY_VOL_M`, `GND` | SW_KEY_VM → SW_KEY_VM pin1 (net `KEY_VOL_M`); SW_KEY_VM → SW_KEY_VM pin2 (net `GND`) | [实测] · [官网] | 若 B3U-1000P 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Button_Switch_SMD:SW_SPST_B3U-1000P` 唯一档 ⇒ 改 KXT3 (`Button_Switch_SMD:SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, 本体 3.5×2.0mm) ⇒ 代价 = 宽度 3.5 > 占位 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议 |
| `SW_KEY_VP` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2 · fab 外框 3.00×2.50 mm · 中心距 3.400 mm | Δ焊盘数 +0 · Δfab +0.00×-0.50 mm · Δ中心距 +1.200 mm | 无 | `KEY_VOL_P`, `GND` | SW_KEY_VP → SW_KEY_VP pin1 (net `KEY_VOL_P`); SW_KEY_VP → SW_KEY_VP pin2 (net `GND`) | [实测] · [官网] | 同 SW_KEY_VM ⇒ 退到 KXT3 (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ 邻键间隙复核 ⇒ 不建议 |
| `SW_RST` | 缺口 | 焊盘 1+2 · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4 · fab 外框 4.20×2.80 mm · 中心距 4.401 mm | Δ焊盘数 +2 · Δfab +1.20×-0.20 mm · Δ中心距 +2.201 mm | 无 | `RESET_N`, `GND` | SW_RST → SW_RST pin1 (net `RESET_N`); SW_RST → SW_RST pin2 (net `GND`) | [实测] · [官网] | 同 SW_BOOT: 不改网表则只能选 2 land 封装 ⇒ 代价 = 按动力度降到 1.5N ⇒ 复位键误触风险上升 ⇒ ★不代拍★ |

★**12 字段逐件齐全, 无一件省略; 「几何 Δ」「腿 B 具名脚清单」「降级方案」三栏一件不空**★。

## §2 腿 B 的具名脚作业包 (★本单的真命门★)

★**为什么腿 B 是真命门**: §0 第 7 行的沙盒实测 ⇒ ★**换 land 不动 C4, 具名脚才动 C4**★ ⇒ ★**那一趟若只换 land 不具名脚, 「C4 == 68」这条验收条件无论如何都还是红的**★。

★**定位口径 (★不许写死列号★)**: 真脚表 `HW/netlist_v1_pins.csv` 的 `footprint` 在**第 11 栏**、`opn` 在**第 12 栏**; 网上那张表 `HW/netlist_v1.csv` 的 `footprint` 在**第 14 栏**、`opn` 在**第 15 栏** ⇒ ★**本单的作业包一律按【表头名】定位, 不按列号**★。

### §2.1 逐件作业表 (90 件 · 一 ref 一行)

| ref | 桶 | 具名脚数 (本件) | 网表里哪一栏 (按表头名定位) | bare 节点串 (原样) → 目标节点串 (逐脚) | 补行指令 | 改完之后 C4 会变成什么 |
|---|---|---|---|---|---|---|
| `C_AC_CSI_D0_CK_N` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N pin1` (net `CSI_D0_CK_N_SRC`); `C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N pin2` (net `CSI_D0_CK_N`) | 无 | ★**C_AC_CSI_D0_CK_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_CK_P` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_CK_P` → `C_AC_CSI_D0_CK_P pin1` (net `CSI_D0_CK_P_SRC`); `C_AC_CSI_D0_CK_P` → `C_AC_CSI_D0_CK_P pin2` (net `CSI_D0_CK_P`) | 无 | ★**C_AC_CSI_D0_CK_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D0_N` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D0_N` → `C_AC_CSI_D0_D0_N pin1` (net `CSI_D0_D0_N_SRC`); `C_AC_CSI_D0_D0_N` → `C_AC_CSI_D0_D0_N pin2` (net `CSI_D0_D0_N`) | 无 | ★**C_AC_CSI_D0_D0_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D0_P` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D0_P` → `C_AC_CSI_D0_D0_P pin1` (net `CSI_D0_D0_P_SRC`); `C_AC_CSI_D0_D0_P` → `C_AC_CSI_D0_D0_P pin2` (net `CSI_D0_D0_P`) | 无 | ★**C_AC_CSI_D0_D0_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D1_N` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D1_N` → `C_AC_CSI_D0_D1_N pin1` (net `CSI_D0_D1_N_SRC`); `C_AC_CSI_D0_D1_N` → `C_AC_CSI_D0_D1_N pin2` (net `CSI_D0_D1_N`) | 无 | ★**C_AC_CSI_D0_D1_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D1_P` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D1_P` → `C_AC_CSI_D0_D1_P pin1` (net `CSI_D0_D1_P_SRC`); `C_AC_CSI_D0_D1_P` → `C_AC_CSI_D0_D1_P pin2` (net `CSI_D0_D1_P`) | 无 | ★**C_AC_CSI_D0_D1_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D2_N` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D2_N` → `C_AC_CSI_D0_D2_N pin1` (net `CSI_D0_D2_N_SRC`); `C_AC_CSI_D0_D2_N` → `C_AC_CSI_D0_D2_N pin2` (net `CSI_D0_D2_N`) | 无 | ★**C_AC_CSI_D0_D2_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D2_P` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D2_P` → `C_AC_CSI_D0_D2_P pin1` (net `CSI_D0_D2_P_SRC`); `C_AC_CSI_D0_D2_P` → `C_AC_CSI_D0_D2_P pin2` (net `CSI_D0_D2_P`) | 无 | ★**C_AC_CSI_D0_D2_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D3_N` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D3_N` → `C_AC_CSI_D0_D3_N pin1` (net `CSI_D0_D3_N_SRC`); `C_AC_CSI_D0_D3_N` → `C_AC_CSI_D0_D3_N pin2` (net `CSI_D0_D3_N`) | 无 | ★**C_AC_CSI_D0_D3_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_AC_CSI_D0_D3_P` | 靶内 | 2 | `node1 / node2` | `C_AC_CSI_D0_D3_P` → `C_AC_CSI_D0_D3_P pin1` (net `CSI_D0_D3_P_SRC`); `C_AC_CSI_D0_D3_P` → `C_AC_CSI_D0_D3_P pin2` (net `CSI_D0_D3_P`) | 无 | ★**C_AC_CSI_D0_D3_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_BULK_LIGHT_3V3` | 靶内 | 2 | `node1 / node2` | `C_BULK_LIGHT_3V3` → `C_BULK_LIGHT_3V3 pin1` (net `LIGHT_3V3`); `C_BULK_LIGHT_3V3` → `C_BULK_LIGHT_3V3 pin2` (net `GND`) | 无 | ★**C_BULK_LIGHT_3V3 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_BULK_VDD_1V8_IO` | 靶内 | 2 | `node1 / node2` | `C_BULK_VDD_1V8_IO` → `C_BULK_VDD_1V8_IO pin1` (net `VDD_1V8_IO`); `C_BULK_VDD_1V8_IO` → `C_BULK_VDD_1V8_IO pin2` (net `GND`) | 无 | ★**C_BULK_VDD_1V8_IO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_BULK_VDD_3V3_IO` | 靶内 | 2 | `node1 / node2` | `C_BULK_VDD_3V3_IO` → `C_BULK_VDD_3V3_IO pin1` (net `VDD_3V3_IO`); `C_BULK_VDD_3V3_IO` → `C_BULK_VDD_3V3_IO pin2` (net `GND`) | 无 | ★**C_BULK_VDD_3V3_IO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_DET_BAT` | 靶内 | 2 | `node1` | `C_DET_BAT` → `C_DET_BAT pin1` (net `BAT_DET`); `C_DET_BAT` → `C_DET_BAT pin2` (net `GND`) | 无 | ★**C_DET_BAT 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_DET_VBUS_D` | 靶内 | 2 | `node1` | `C_DET_VBUS_D` → `C_DET_VBUS_D pin1` (net `GND`); `C_DET_VBUS_D` → `C_DET_VBUS_D pin2` (net `VBUS_DET_D`) | 无 | ★**C_DET_VBUS_D 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_HF_LIGHT_3V3` | 靶内 | 2 | `node1 / node2` | `C_HF_LIGHT_3V3` → `C_HF_LIGHT_3V3 pin1` (net `LIGHT_3V3`); `C_HF_LIGHT_3V3` → `C_HF_LIGHT_3V3 pin2` (net `GND`) | 无 | ★**C_HF_LIGHT_3V3 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_HF_VDD_1V8_IO` | 靶内 | 2 | `node1 / node2` | `C_HF_VDD_1V8_IO` → `C_HF_VDD_1V8_IO pin1` (net `VDD_1V8_IO`); `C_HF_VDD_1V8_IO` → `C_HF_VDD_1V8_IO pin2` (net `GND`) | 无 | ★**C_HF_VDD_1V8_IO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_HF_VDD_3V3_IO` | 靶内 | 2 | `node1 / node2` | `C_HF_VDD_3V3_IO` → `C_HF_VDD_3V3_IO pin1` (net `VDD_3V3_IO`); `C_HF_VDD_3V3_IO` → `C_HF_VDD_3V3_IO pin2` (net `GND`) | 无 | ★**C_HF_VDD_3V3_IO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_KEY_PWR` | 靶内 | 2 | `node1` | `C_KEY_PWR` → `C_KEY_PWR pin1` (net `KEY_PWR`); ★补行★ net `GND` · node1 `C_KEY_PWR pin2` · node2 `GND` | net `GND` (脚表 pin2) | ★**C_KEY_PWR 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_KEY_VM` | 靶内 | 2 | `node1` | `C_KEY_VM` → `C_KEY_VM pin1` (net `KEY_VOL_M`); ★补行★ net `GND` · node1 `C_KEY_VM pin2` · node2 `GND` | net `GND` (脚表 pin2) | ★**C_KEY_VM 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_KEY_VP` | 靶内 | 2 | `node1` | `C_KEY_VP` → `C_KEY_VP pin1` (net `KEY_VOL_P`); ★补行★ net `GND` · node1 `C_KEY_VP pin2` · node2 `GND` | net `GND` (脚表 pin2) | ★**C_KEY_VP 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_RST` | 靶内 | 2 | `node1` | `C_RST` → `C_RST pin1` (net `RESET_N_SOC`); `C_RST` → `C_RST pin2` (net `GND`) | 无 | ★**C_RST 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_SW_IN` | 靶内 | 2 | `node1` | `C_SW_IN` → `C_SW_IN pin1` (net `BAT_SW`); `C_SW_IN` → `C_SW_IN pin2` (net `GND`) | 无 | ★**C_SW_IN 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_SW_OUT` | 靶内 | 2 | `node1` | `C_SW_OUT` → `C_SW_OUT pin1` (net `SYS`); `C_SW_OUT` → `C_SW_OUT pin2` (net `GND`) | 无 | ★**C_SW_OUT 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_TEMP` | 靶内 | 2 | `node1` | `C_TEMP` → `C_TEMP pin1` (net `VDD_3V3_IO`); `C_TEMP` → `C_TEMP pin2` (net `GND`) | 无 | ★**C_TEMP 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `C_VBUS_DEMO` | 靶内 | 2 | `node1` | `C_VBUS_DEMO` → `C_VBUS_DEMO pin1` (net `RAIL_DEMO_5V`); `C_VBUS_DEMO` → `C_VBUS_DEMO pin2` (net `GND`) | 无 | ★**C_VBUS_DEMO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `D_LED_G` | 靶内 | 2 | `node1 / node2` | `D_LED_G` → `D_LED_G pin1` (net `LED_G_D`); `D_LED_G` → `D_LED_G pin2` (net `GND`) | 无 | ★**D_LED_G 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `D_LED_R` | 靶内 | 2 | `node1 / node2` | `D_LED_R` → `D_LED_R pin1` (net `LED_R_D`); `D_LED_R` → `D_LED_R pin2` (net `GND`) | 无 | ★**D_LED_R 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_BAT_DET_1` | 靶内 | 2 | `node1 / node2` | `R_BAT_DET_1` → `R_BAT_DET_1 pin1` (net `BAT_DET`); `R_BAT_DET_1` → `R_BAT_DET_1 pin2` (net `BAT`) | 无 | ★**R_BAT_DET_1 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_BAT_DET_2` | 靶内 | 2 | `node1 / node2` | `R_BAT_DET_2` → `R_BAT_DET_2 pin1` (net `BAT_DET`); ★补行★ net `GND` · node1 `R_BAT_DET_2 pin2` · node2 `GND` | net `GND` (脚表 pin2) | ★**R_BAT_DET_2 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_CC1_D` | 靶内 | 2 | `node1 / node2` | `R_CC1_D` → `R_CC1_D pin1` (net `GND`); `R_CC1_D` → `R_CC1_D pin2` (net `USB_CC1`) | 无 | ★**R_CC1_D 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_CC2_D` | 靶内 | 2 | `node1 / node2` | `R_CC2_D` → `R_CC2_D pin1` (net `USB_CC2`); `R_CC2_D` → `R_CC2_D pin2` (net `GND`) | 无 | ★**R_CC2_D 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_EN_VCORE` | 靶内 | 2 | `node1 / node2` | `R_EN_VCORE` → `R_EN_VCORE pin1` (net `EN_VCORE`); `R_EN_VCORE` → `R_EN_VCORE pin2` (net `VDD_1V8_IO`) | 无 | ★**R_EN_VCORE 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_JTAG_TCK` | 靶内 | 2 | `node1 / node2` | `R_JTAG_TCK` → `R_JTAG_TCK pin1` (net `JTAG_TCK_SOC`); `R_JTAG_TCK` → `R_JTAG_TCK pin2` (net `JTAG_TCK`) | 无 | ★**R_JTAG_TCK 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_JTAG_TDI` | 靶内 | 2 | `node1 / node2` | `R_JTAG_TDI` → `R_JTAG_TDI pin1` (net `JTAG_TDI_SOC`); `R_JTAG_TDI` → `R_JTAG_TDI pin2` (net `JTAG_TDI`) | 无 | ★**R_JTAG_TDI 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_JTAG_TDO` | 靶内 | 2 | `node1 / node2` | `R_JTAG_TDO` → `R_JTAG_TDO pin1` (net `JTAG_TDO_SOC`); `R_JTAG_TDO` → `R_JTAG_TDO pin2` (net `JTAG_TDO`) | 无 | ★**R_JTAG_TDO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_JTAG_TMS` | 靶内 | 2 | `node1 / node2` | `R_JTAG_TMS` → `R_JTAG_TMS pin1` (net `JTAG_TMS_SOC`); `R_JTAG_TMS` → `R_JTAG_TMS pin2` (net `JTAG_TMS`) | 无 | ★**R_JTAG_TMS 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_KEY_CAM` | 靶内 | 2 | `node1 / node2` | `R_KEY_CAM` → `R_KEY_CAM pin1` (net `KEY_CAM`); `R_KEY_CAM` → `R_KEY_CAM pin2` (net `VDD_3V3_IO`) | 无 | ★**R_KEY_CAM 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_KEY_PWR` | 靶内 | 2 | `node1 / node2` | `R_KEY_PWR` → `R_KEY_PWR pin1` (net `KEY_PWR`); `R_KEY_PWR` → `R_KEY_PWR pin2` (net `VDD_3V3_IO`) | 无 | ★**R_KEY_PWR 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_KEY_VM` | 靶内 | 2 | `node1 / node2` | `R_KEY_VM` → `R_KEY_VM pin1` (net `KEY_VOL_M`); `R_KEY_VM` → `R_KEY_VM pin2` (net `VDD_3V3_IO`) | 无 | ★**R_KEY_VM 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_KEY_VP` | 靶内 | 2 | `node1 / node2` | `R_KEY_VP` → `R_KEY_VP pin1` (net `KEY_VOL_P`); `R_KEY_VP` → `R_KEY_VP pin2` (net `VDD_3V3_IO`) | 无 | ★**R_KEY_VP 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_LED_G` | 靶内 | 2 | `node1 / node2` | `R_LED_G` → `R_LED_G pin1` (net `LED_G`); `R_LED_G` → `R_LED_G pin2` (net `LED_G_D`) | 无 | ★**R_LED_G 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_LED_R` | 靶内 | 2 | `node1 / node2` | `R_LED_R` → `R_LED_R pin1` (net `LED_R`); `R_LED_R` → `R_LED_R pin2` (net `LED_R_D`) | 无 | ★**R_LED_R 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PD_ON` | 靶内 | 2 | `node1` | `R_PD_ON` → `R_PD_ON pin1` (net `PWR_ON`); `R_PD_ON` → `R_PD_ON pin2` (net `GND`) | 无 | ★**R_PD_ON 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PG_PULL` | 靶内 | 2 | `node1` | `R_PG_PULL` → `R_PG_PULL pin1` (net `PG_AND`); `R_PG_PULL` → `R_PG_PULL pin2` (net `VDD_1V8_IO`) | 无 | ★**R_PG_PULL 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_BOOT_N` | 靶内 | 2 | `node1 / node2` | `R_PU_BOOT_N` → `R_PU_BOOT_N pin1` (net `BOOT_N`); `R_PU_BOOT_N` → `R_PU_BOOT_N pin2` (net `VDD_1V8_IO`) | 无 | ★**R_PU_BOOT_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_I2CA_SCL` | 靶内 | 2 | `node1 / node2` | `R_PU_I2CA_SCL` → `R_PU_I2CA_SCL pin1` (net `I2C_A_SCL`); `R_PU_I2CA_SCL` → `R_PU_I2CA_SCL pin2` (net `VDD_1V8_IO`) | 无 | ★**R_PU_I2CA_SCL 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_I2CA_SDA` | 靶内 | 2 | `node1 / node2` | `R_PU_I2CA_SDA` → `R_PU_I2CA_SDA pin1` (net `I2C_A_SDA`); `R_PU_I2CA_SDA` → `R_PU_I2CA_SDA pin2` (net `VDD_1V8_IO`) | 无 | ★**R_PU_I2CA_SDA 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_I2CB_SCL` | 靶内 | 2 | `node1 / node2` | `R_PU_I2CB_SCL` → `R_PU_I2CB_SCL pin1` (net `I2C_B_SCL`); `R_PU_I2CB_SCL` → `R_PU_I2CB_SCL pin2` (net `VDD_3V3_IO`) | 无 | ★**R_PU_I2CB_SCL 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_I2CB_SDA` | 靶内 | 2 | `node1 / node2` | `R_PU_I2CB_SDA` → `R_PU_I2CB_SDA pin1` (net `I2C_B_SDA`); `R_PU_I2CB_SDA` → `R_PU_I2CB_SDA pin2` (net `VDD_3V3_IO`) | 无 | ★**R_PU_I2CB_SDA 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_ID0` | 靶内 | 2 | `node1 / node2` | `R_PU_ID0` → `R_PU_ID0 pin1` (net `ID_DETECT_0`); `R_PU_ID0` → `R_PU_ID0 pin2` (net `VDD_3V3_IO`) | 无 | ★**R_PU_ID0 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_ID1` | 靶内 | 2 | `node1 / node2` | `R_PU_ID1` → `R_PU_ID1 pin1` (net `ID_DETECT_1`); `R_PU_ID1` → `R_PU_ID1 pin2` (net `VDD_3V3_IO`) | 无 | ★**R_PU_ID1 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_PG` | 靶内 | 2 | `node1 / node2` | `R_PU_PG` → `R_PU_PG pin2` (net `VDD_3V3_IO`); `R_PU_PG` → `R_PU_PG pin1` (net `PWR_GOOD`) | 无 | ★**R_PU_PG 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_PU_RESET_N` | 靶内 | 2 | `node1 / node2` | `R_PU_RESET_N` → `R_PU_RESET_N pin1` (net `RESET_N`); `R_PU_RESET_N` → `R_PU_RESET_N pin2` (net `VDD_1V8_IO`) | 无 | ★**R_PU_RESET_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_CK_N` | 靶内 | 2 | `node1 / node2` | `R_SEL_CK_N` → `R_SEL_CK_N pin1` (net `DSI_D0_CK_N_SRC`); `R_SEL_CK_N` → `R_SEL_CK_N pin2` (net `DSI_D0_CK_N`) | 无 | ★**R_SEL_CK_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_CK_P` | 靶内 | 2 | `node1 / node2` | `R_SEL_CK_P` → `R_SEL_CK_P pin1` (net `DSI_D0_CK_P_SRC`); `R_SEL_CK_P` → `R_SEL_CK_P pin2` (net `DSI_D0_CK_P`) | 无 | ★**R_SEL_CK_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D0_N` | 靶内 | 2 | `node1 / node2` | `R_SEL_D0_N` → `R_SEL_D0_N pin1` (net `DSI_D0_D0_N_SRC`); `R_SEL_D0_N` → `R_SEL_D0_N pin2` (net `DSI_D0_D0_N`) | 无 | ★**R_SEL_D0_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D0_P` | 靶内 | 2 | `node1 / node2` | `R_SEL_D0_P` → `R_SEL_D0_P pin1` (net `DSI_D0_D0_P_SRC`); `R_SEL_D0_P` → `R_SEL_D0_P pin2` (net `DSI_D0_D0_P`) | 无 | ★**R_SEL_D0_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D1_N` | 靶内 | 2 | `node1 / node2` | `R_SEL_D1_N` → `R_SEL_D1_N pin1` (net `DSI_D0_D1_N_SRC`); `R_SEL_D1_N` → `R_SEL_D1_N pin2` (net `DSI_D0_D1_N`) | 无 | ★**R_SEL_D1_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D1_P` | 靶内 | 2 | `node1 / node2` | `R_SEL_D1_P` → `R_SEL_D1_P pin1` (net `DSI_D0_D1_P_SRC`); `R_SEL_D1_P` → `R_SEL_D1_P pin2` (net `DSI_D0_D1_P`) | 无 | ★**R_SEL_D1_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D2_N` | 靶内 | 2 | `node1 / node2` | `R_SEL_D2_N` → `R_SEL_D2_N pin1` (net `DSI_D0_D2_N_SRC`); `R_SEL_D2_N` → `R_SEL_D2_N pin2` (net `DSI_D0_D2_N`) | 无 | ★**R_SEL_D2_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D2_P` | 靶内 | 2 | `node1 / node2` | `R_SEL_D2_P` → `R_SEL_D2_P pin1` (net `DSI_D0_D2_P_SRC`); `R_SEL_D2_P` → `R_SEL_D2_P pin2` (net `DSI_D0_D2_P`) | 无 | ★**R_SEL_D2_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D3_N` | 靶内 | 2 | `node1 / node2` | `R_SEL_D3_N` → `R_SEL_D3_N pin1` (net `DSI_D0_D3_N_SRC`); `R_SEL_D3_N` → `R_SEL_D3_N pin2` (net `DSI_D0_D3_N`) | 无 | ★**R_SEL_D3_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SEL_D3_P` | 靶内 | 2 | `node1 / node2` | `R_SEL_D3_P` → `R_SEL_D3_P pin1` (net `DSI_D0_D3_P_SRC`); `R_SEL_D3_P` → `R_SEL_D3_P pin2` (net `DSI_D0_D3_P`) | 无 | ★**R_SEL_D3_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_CSI_MCLK` | 靶内 | 2 | `node1 / node2` | `R_SER_CSI_MCLK` → `R_SER_CSI_MCLK pin1` (net `CSI_MCLK_SRC`); `R_SER_CSI_MCLK` → `R_SER_CSI_MCLK pin2` (net `CSI_MCLK`) | 无 | ★**R_SER_CSI_MCLK 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_FSIN` | 靶内 | 2 | `node1 / node2` | `R_SER_FSIN` → `R_SER_FSIN pin1` (net `FSIN_OUT`); `R_SER_FSIN` → `R_SER_FSIN pin2` (net `FSIN`) | 无 | ★**R_SER_FSIN 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_RESET_N` | 靶内 | 2 | `node1 / node2` | `R_SER_RESET_N` → `R_SER_RESET_N pin1` (net `RESET_N`); `R_SER_RESET_N` → `R_SER_RESET_N pin2` (net `RESET_N_SOC`) | 无 | ★**R_SER_RESET_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_SPI_CSn` | 靶内 | 2 | `node1 / node2` | `R_SER_SPI_CSn` → `R_SER_SPI_CSn pin1` (net `SPI_CSn`); `R_SER_SPI_CSn` → `R_SER_SPI_CSn pin2` (net `SPI_CSn_BOOT`) | 无 | ★**R_SER_SPI_CSn 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_SPI_MISO` | 靶内 | 2 | `node1 / node2` | `R_SER_SPI_MISO` → `R_SER_SPI_MISO pin1` (net `SPI_MISO`); `R_SER_SPI_MISO` → `R_SER_SPI_MISO pin2` (net `SPI_MISO_BOOT`) | 无 | ★**R_SER_SPI_MISO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_SPI_MOSI` | 靶内 | 2 | `node1 / node2` | `R_SER_SPI_MOSI` → `R_SER_SPI_MOSI pin1` (net `SPI_MOSI`); `R_SER_SPI_MOSI` → `R_SER_SPI_MOSI pin2` (net `SPI_MOSI_BOOT`) | 无 | ★**R_SER_SPI_MOSI 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_SPI_SCLK` | 靶内 | 2 | `node1 / node2` | `R_SER_SPI_SCLK` → `R_SER_SPI_SCLK pin1` (net `SPI_SCLK`); `R_SER_SPI_SCLK` → `R_SER_SPI_SCLK pin2` (net `SPI_SCLK_BOOT`) | 无 | ★**R_SER_SPI_SCLK 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_USB_D_N` | 靶内 | 2 | `node1 / node2` | `R_SER_USB_D_N` → `R_SER_USB_D_N pin1` (net `USB_D_N_SRC`); `R_SER_USB_D_N` → `R_SER_USB_D_N pin2` (net `NET_USB_D_N_TYPEC`) | 无 | ★**R_SER_USB_D_N 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SER_USB_D_P` | 靶内 | 2 | `node1 / node2` | `R_SER_USB_D_P` → `R_SER_USB_D_P pin1` (net `USB_D_P_SRC`); `R_SER_USB_D_P` → `R_SER_USB_D_P pin2` (net `NET_USB_D_P_TYPEC`) | 无 | ★**R_SER_USB_D_P 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SUPV_DIV1` | 靶内 | 2 | `node1 / node2` | `R_SUPV_DIV1` → `R_SUPV_DIV1 pin1` (net `V_SOC_IO`); `R_SUPV_DIV1` → `R_SUPV_DIV1 pin2` (net `SUPV_SENSE`) | 无 | ★**R_SUPV_DIV1 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_SUPV_DIV2` | 靶内 | 2 | `node1 / node2` | `R_SUPV_DIV2` → `R_SUPV_DIV2 pin1` (net `SUPV_SENSE`); `R_SUPV_DIV2` → `R_SUPV_DIV2 pin2` (net `GND`) | 无 | ★**R_SUPV_DIV2 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_VBUS_DET_D1` | 靶内 | 2 | `node1` | `R_VBUS_DET_D1` → `R_VBUS_DET_D1 pin1` (net `RAIL_DEMO_5V`); `R_VBUS_DET_D1` → `R_VBUS_DET_D1 pin2` (net `VBUS_DET_D`) | 无 | ★**R_VBUS_DET_D1 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `R_VBUS_DET_D2` | 靶内 | 2 | `node1 / node2` | `R_VBUS_DET_D2` → `R_VBUS_DET_D2 pin1` (net `VBUS_DET_D`); `R_VBUS_DET_D2` → `R_VBUS_DET_D2 pin2` (net `GND`) | 无 | ★**R_VBUS_DET_D2 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `CHG_GND_STAR` | 缺口 | 1 | `node1 / node2` | `CHG_GND_STAR` → `CHG_GND_STAR pin1` (net `GND`) | 无 | ★**CHG_GND_STAR 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `D_ESD_CAM` | 缺口 | 2 | `node1 / node2` | `D_ESD_CAM` → `D_ESD_CAM pin1` (net `GND`); `D_ESD_CAM` → `D_ESD_CAM pin2` (net `CSI_D0_CK_P`) | 无 | ★**D_ESD_CAM 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `D_ESD_DEMO` | 缺口 | 2 | `node1` | `D_ESD_DEMO` → `D_ESD_DEMO pin1` (net `RAIL_DEMO_5V`); `D_ESD_DEMO` → `D_ESD_DEMO pin2` (net `GND`) | 无 | ★**D_ESD_DEMO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `D_ESD_USB_D` | 缺口 | 2 | `node1` | `D_ESD_USB_D` → `D_ESD_USB_D pin1` (net `NET_USB_D_P_TYPEC`); `D_ESD_USB_D` → `D_ESD_USB_D pin2` (net `GND`) | 无 | ★**D_ESD_USB_D 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `FB_DEMO` | 缺口 | 2 | `node1` | `FB_DEMO` → `FB_DEMO pin1` (net `RAIL_DEMO_5V`); `FB_DEMO` → `FB_DEMO pin2` (net `GND`) | 无 | ★**FB_DEMO 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `Q_AND` | 缺口 | 3 | `node1` | `Q_AND` → `Q_AND pin1` (net `RESET_N`); `Q_AND` → `Q_AND pin2` (net `GND`); `Q_AND` → `Q_AND pin3` (net `PG_AND`) | 无 | ★**Q_AND 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `Q_ENVC` | 缺口 | 3 | `node1` | `Q_ENVC` → `Q_ENVC pin1` (net `PG_AND`); `Q_ENVC` → `Q_ENVC pin2` (net `GND`); `Q_ENVC` → `Q_ENVC pin3` (net `EN_VCORE`) | 无 | ★**Q_ENVC 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `Q_PG` | 缺口 | 3 | `node1` | `Q_PG` → `Q_PG pin1` (net `PWR_GOOD`); `Q_PG` → `Q_PG pin2` (net `BAT_SW`); `Q_PG` → `Q_PG pin3` (net `PWR_ON`) | 无 | ★**Q_PG 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `SW_BOOT` | 缺口 | 2 | `node1` | `SW_BOOT` → `SW_BOOT pin1` (net `BOOT_N`); `SW_BOOT` → `SW_BOOT pin2` (net `GND`) | 无 | ★**SW_BOOT 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `SW_KEY_PWR` | 缺口 | 2 | `node1` | `SW_KEY_PWR` → `SW_KEY_PWR pin1` (net `KEY_PWR`); `SW_KEY_PWR` → `SW_KEY_PWR pin2` (net `GND`) | 无 | ★**SW_KEY_PWR 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `SW_KEY_VM` | 缺口 | 2 | `node1` | `SW_KEY_VM` → `SW_KEY_VM pin1` (net `KEY_VOL_M`); `SW_KEY_VM` → `SW_KEY_VM pin2` (net `GND`) | 无 | ★**SW_KEY_VM 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `SW_KEY_VP` | 缺口 | 2 | `node1` | `SW_KEY_VP` → `SW_KEY_VP pin1` (net `KEY_VOL_P`); `SW_KEY_VP` → `SW_KEY_VP pin2` (net `GND`) | 无 | ★**SW_KEY_VP 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |
| `SW_RST` | 缺口 | 2 | `node1` | `SW_RST` → `SW_RST pin1` (net `RESET_N`); `SW_RST` → `SW_RST pin2` (net `GND`) | 无 | ★**SW_RST 出 C4 的 158 名单 ⇒ 本件 ΔC4 = −1** ★ ⇒ ★**90 件全做完 ⇒ C4 158 − 90 = 68** ★ |

★**具名脚总条数 = 182**★ (★= 90 件脚数之和·脚本实算★) ⇒ ★**全部落完 ⇒ C4 = 158 − 90 = 68**★。

### §2.2 指令全清单 (200 条: 改名 196 + 补行 4) · ★逐条可执行★

| # | ref | 动作 | 网表 CSV 行号 | 栏 (表头名) | 原值 | 改成 | 该脚所在网 |
|---|---|---|---|---|---|---|---|
| 1 | `C_AC_CSI_D0_CK_N` | 改名 | 252 | `node2` | `C_AC_CSI_D0_CK_N` | `C_AC_CSI_D0_CK_N pin1` | `CSI_D0_CK_N_SRC` |
| 2 | `C_AC_CSI_D0_CK_N` | 改名 | 253 | `node1` | `C_AC_CSI_D0_CK_N` | `C_AC_CSI_D0_CK_N pin2` | `CSI_D0_CK_N` |
| 3 | `C_AC_CSI_D0_CK_P` | 改名 | 250 | `node2` | `C_AC_CSI_D0_CK_P` | `C_AC_CSI_D0_CK_P pin1` | `CSI_D0_CK_P_SRC` |
| 4 | `C_AC_CSI_D0_CK_P` | 改名 | 251 | `node1` | `C_AC_CSI_D0_CK_P` | `C_AC_CSI_D0_CK_P pin2` | `CSI_D0_CK_P` |
| 5 | `C_AC_CSI_D0_D0_N` | 改名 | 256 | `node2` | `C_AC_CSI_D0_D0_N` | `C_AC_CSI_D0_D0_N pin1` | `CSI_D0_D0_N_SRC` |
| 6 | `C_AC_CSI_D0_D0_N` | 改名 | 257 | `node1` | `C_AC_CSI_D0_D0_N` | `C_AC_CSI_D0_D0_N pin2` | `CSI_D0_D0_N` |
| 7 | `C_AC_CSI_D0_D0_P` | 改名 | 254 | `node2` | `C_AC_CSI_D0_D0_P` | `C_AC_CSI_D0_D0_P pin1` | `CSI_D0_D0_P_SRC` |
| 8 | `C_AC_CSI_D0_D0_P` | 改名 | 255 | `node1` | `C_AC_CSI_D0_D0_P` | `C_AC_CSI_D0_D0_P pin2` | `CSI_D0_D0_P` |
| 9 | `C_AC_CSI_D0_D1_N` | 改名 | 260 | `node2` | `C_AC_CSI_D0_D1_N` | `C_AC_CSI_D0_D1_N pin1` | `CSI_D0_D1_N_SRC` |
| 10 | `C_AC_CSI_D0_D1_N` | 改名 | 261 | `node1` | `C_AC_CSI_D0_D1_N` | `C_AC_CSI_D0_D1_N pin2` | `CSI_D0_D1_N` |
| 11 | `C_AC_CSI_D0_D1_P` | 改名 | 258 | `node2` | `C_AC_CSI_D0_D1_P` | `C_AC_CSI_D0_D1_P pin1` | `CSI_D0_D1_P_SRC` |
| 12 | `C_AC_CSI_D0_D1_P` | 改名 | 259 | `node1` | `C_AC_CSI_D0_D1_P` | `C_AC_CSI_D0_D1_P pin2` | `CSI_D0_D1_P` |
| 13 | `C_AC_CSI_D0_D2_N` | 改名 | 264 | `node2` | `C_AC_CSI_D0_D2_N` | `C_AC_CSI_D0_D2_N pin1` | `CSI_D0_D2_N_SRC` |
| 14 | `C_AC_CSI_D0_D2_N` | 改名 | 265 | `node1` | `C_AC_CSI_D0_D2_N` | `C_AC_CSI_D0_D2_N pin2` | `CSI_D0_D2_N` |
| 15 | `C_AC_CSI_D0_D2_P` | 改名 | 262 | `node2` | `C_AC_CSI_D0_D2_P` | `C_AC_CSI_D0_D2_P pin1` | `CSI_D0_D2_P_SRC` |
| 16 | `C_AC_CSI_D0_D2_P` | 改名 | 263 | `node1` | `C_AC_CSI_D0_D2_P` | `C_AC_CSI_D0_D2_P pin2` | `CSI_D0_D2_P` |
| 17 | `C_AC_CSI_D0_D3_N` | 改名 | 268 | `node2` | `C_AC_CSI_D0_D3_N` | `C_AC_CSI_D0_D3_N pin1` | `CSI_D0_D3_N_SRC` |
| 18 | `C_AC_CSI_D0_D3_N` | 改名 | 269 | `node1` | `C_AC_CSI_D0_D3_N` | `C_AC_CSI_D0_D3_N pin2` | `CSI_D0_D3_N` |
| 19 | `C_AC_CSI_D0_D3_P` | 改名 | 266 | `node2` | `C_AC_CSI_D0_D3_P` | `C_AC_CSI_D0_D3_P pin1` | `CSI_D0_D3_P_SRC` |
| 20 | `C_AC_CSI_D0_D3_P` | 改名 | 267 | `node1` | `C_AC_CSI_D0_D3_P` | `C_AC_CSI_D0_D3_P pin2` | `CSI_D0_D3_P` |
| 21 | `C_BULK_LIGHT_3V3` | 改名 | 126 | `node2` | `C_BULK_LIGHT_3V3` | `C_BULK_LIGHT_3V3 pin1` | `LIGHT_3V3` |
| 22 | `C_BULK_LIGHT_3V3` | 改名 | 127 | `node1` | `C_BULK_LIGHT_3V3` | `C_BULK_LIGHT_3V3 pin2` | `GND` |
| 23 | `C_BULK_VDD_1V8_IO` | 改名 | 156 | `node2` | `C_BULK_VDD_1V8_IO` | `C_BULK_VDD_1V8_IO pin1` | `VDD_1V8_IO` |
| 24 | `C_BULK_VDD_1V8_IO` | 改名 | 157 | `node1` | `C_BULK_VDD_1V8_IO` | `C_BULK_VDD_1V8_IO pin2` | `GND` |
| 25 | `C_BULK_VDD_3V3_IO` | 改名 | 146 | `node2` | `C_BULK_VDD_3V3_IO` | `C_BULK_VDD_3V3_IO pin1` | `VDD_3V3_IO` |
| 26 | `C_BULK_VDD_3V3_IO` | 改名 | 147 | `node1` | `C_BULK_VDD_3V3_IO` | `C_BULK_VDD_3V3_IO pin2` | `GND` |
| 27 | `C_DET_BAT` | 改名 | 184 | `node1` | `C_DET_BAT` | `C_DET_BAT pin1` | `BAT_DET` |
| 28 | `C_DET_BAT` | 改名 | 185 | `node1` | `C_DET_BAT` | `C_DET_BAT pin2` | `GND` |
| 29 | `C_DET_VBUS_D` | 改名 | 437 | `node1` | `C_DET_VBUS_D` | `C_DET_VBUS_D pin1` | `GND` |
| 30 | `C_DET_VBUS_D` | 改名 | 438 | `node1` | `C_DET_VBUS_D` | `C_DET_VBUS_D pin2` | `VBUS_DET_D` |
| 31 | `C_HF_LIGHT_3V3` | 改名 | 128 | `node2` | `C_HF_LIGHT_3V3` | `C_HF_LIGHT_3V3 pin1` | `LIGHT_3V3` |
| 32 | `C_HF_LIGHT_3V3` | 改名 | 129 | `node1` | `C_HF_LIGHT_3V3` | `C_HF_LIGHT_3V3 pin2` | `GND` |
| 33 | `C_HF_VDD_1V8_IO` | 改名 | 158 | `node2` | `C_HF_VDD_1V8_IO` | `C_HF_VDD_1V8_IO pin1` | `VDD_1V8_IO` |
| 34 | `C_HF_VDD_1V8_IO` | 改名 | 159 | `node1` | `C_HF_VDD_1V8_IO` | `C_HF_VDD_1V8_IO pin2` | `GND` |
| 35 | `C_HF_VDD_3V3_IO` | 改名 | 148 | `node2` | `C_HF_VDD_3V3_IO` | `C_HF_VDD_3V3_IO pin1` | `VDD_3V3_IO` |
| 36 | `C_HF_VDD_3V3_IO` | 改名 | 149 | `node1` | `C_HF_VDD_3V3_IO` | `C_HF_VDD_3V3_IO pin2` | `GND` |
| 37 | `C_KEY_PWR` | 改名 | 313 | `node1` | `C_KEY_PWR` | `C_KEY_PWR pin1` | `KEY_PWR` |
| 38 | `C_KEY_PWR` | ★补行★ | (新增) | `node1` | (新增一行) | `net=GND` · `node1=C_KEY_PWR pin2` · `node2=GND` | `GND` |
| 39 | `C_KEY_VM` | 改名 | 323 | `node1` | `C_KEY_VM` | `C_KEY_VM pin1` | `KEY_VOL_M` |
| 40 | `C_KEY_VM` | ★补行★ | (新增) | `node1` | (新增一行) | `net=GND` · `node1=C_KEY_VM pin2` · `node2=GND` | `GND` |
| 41 | `C_KEY_VP` | 改名 | 318 | `node1` | `C_KEY_VP` | `C_KEY_VP pin1` | `KEY_VOL_P` |
| 42 | `C_KEY_VP` | ★补行★ | (新增) | `node1` | (新增一行) | `net=GND` · `node1=C_KEY_VP pin2` · `node2=GND` | `GND` |
| 43 | `C_RST` | 改名 | 380 | `node1` | `C_RST` | `C_RST pin1` | `RESET_N_SOC` |
| 44 | `C_RST` | 改名 | 381 | `node1` | `C_RST` | `C_RST pin2` | `GND` |
| 45 | `C_SW_IN` | 改名 | 52 | `node1` | `C_SW_IN` | `C_SW_IN pin1` | `BAT_SW` |
| 46 | `C_SW_IN` | 改名 | 53 | `node1` | `C_SW_IN` | `C_SW_IN pin2` | `GND` |
| 47 | `C_SW_OUT` | 改名 | 54 | `node1` | `C_SW_OUT` | `C_SW_OUT pin1` | `SYS` |
| 48 | `C_SW_OUT` | 改名 | 55 | `node1` | `C_SW_OUT` | `C_SW_OUT pin2` | `GND` |
| 49 | `C_TEMP` | 改名 | 179 | `node1` | `C_TEMP` | `C_TEMP pin1` | `VDD_3V3_IO` |
| 50 | `C_TEMP` | 改名 | 180 | `node1` | `C_TEMP` | `C_TEMP pin2` | `GND` |
| 51 | `C_VBUS_DEMO` | 改名 | 424 | `node1` | `C_VBUS_DEMO` | `C_VBUS_DEMO pin1` | `RAIL_DEMO_5V` |
| 52 | `C_VBUS_DEMO` | 改名 | 425 | `node1` | `C_VBUS_DEMO` | `C_VBUS_DEMO pin2` | `GND` |
| 53 | `D_LED_G` | 改名 | 304 | `node2` | `D_LED_G` | `D_LED_G pin1` | `LED_G_D` |
| 54 | `D_LED_G` | 改名 | 305 | `node1` | `D_LED_G` | `D_LED_G pin2` | `GND` |
| 55 | `D_LED_R` | 改名 | 301 | `node2` | `D_LED_R` | `D_LED_R pin1` | `LED_R_D` |
| 56 | `D_LED_R` | 改名 | 302 | `node1` | `D_LED_R` | `D_LED_R pin2` | `GND` |
| 57 | `R_BAT_DET_1` | 改名 | 181 | `node1` | `R_BAT_DET_1` | `R_BAT_DET_1 pin1` | `BAT_DET` |
| 58 | `R_BAT_DET_1` | 改名 | 182 | `node2` | `R_BAT_DET_1` | `R_BAT_DET_1 pin2` | `BAT` |
| 59 | `R_BAT_DET_2` | 改名 | 181 | `node2` | `R_BAT_DET_2` | `R_BAT_DET_2 pin1` | `BAT_DET` |
| 60 | `R_BAT_DET_2` | 改名 | 183 | `node1` | `R_BAT_DET_2` | `R_BAT_DET_2 pin1` | `BAT_DET` |
| 61 | `R_BAT_DET_2` | 改名 | 184 | `node2` | `R_BAT_DET_2` | `R_BAT_DET_2 pin1` | `BAT_DET` |
| 62 | `R_BAT_DET_2` | ★补行★ | (新增) | `node1` | (新增一行) | `net=GND` · `node1=R_BAT_DET_2 pin2` · `node2=GND` | `GND` |
| 63 | `R_CC1_D` | 改名 | 426 | `node1` | `R_CC1_D` | `R_CC1_D pin1` | `GND` |
| 64 | `R_CC1_D` | 改名 | 428 | `node2` | `R_CC1_D` | `R_CC1_D pin2` | `USB_CC1` |
| 65 | `R_CC2_D` | 改名 | 429 | `node2` | `R_CC2_D` | `R_CC2_D pin1` | `USB_CC2` |
| 66 | `R_CC2_D` | 改名 | 430 | `node1` | `R_CC2_D` | `R_CC2_D pin2` | `GND` |
| 67 | `R_EN_VCORE` | 改名 | 68 | `node1` | `R_EN_VCORE` | `R_EN_VCORE pin1` | `EN_VCORE` |
| 68 | `R_EN_VCORE` | 改名 | 69 | `node1` | `R_EN_VCORE` | `R_EN_VCORE pin2` | `VDD_1V8_IO` |
| 69 | `R_EN_VCORE` | 改名 | 70 | `node2` | `R_EN_VCORE` | `R_EN_VCORE pin1` | `EN_VCORE` |
| 70 | `R_EN_VCORE` | 改名 | 73 | `node2` | `R_EN_VCORE` | `R_EN_VCORE pin1` | `EN_VCORE` |
| 71 | `R_JTAG_TCK` | 改名 | 388 | `node2` | `R_JTAG_TCK` | `R_JTAG_TCK pin1` | `JTAG_TCK_SOC` |
| 72 | `R_JTAG_TCK` | 改名 | 389 | `node1` | `R_JTAG_TCK` | `R_JTAG_TCK pin2` | `JTAG_TCK` |
| 73 | `R_JTAG_TDI` | 改名 | 392 | `node2` | `R_JTAG_TDI` | `R_JTAG_TDI pin1` | `JTAG_TDI_SOC` |
| 74 | `R_JTAG_TDI` | 改名 | 393 | `node1` | `R_JTAG_TDI` | `R_JTAG_TDI pin2` | `JTAG_TDI` |
| 75 | `R_JTAG_TDO` | 改名 | 394 | `node2` | `R_JTAG_TDO` | `R_JTAG_TDO pin1` | `JTAG_TDO_SOC` |
| 76 | `R_JTAG_TDO` | 改名 | 395 | `node1` | `R_JTAG_TDO` | `R_JTAG_TDO pin2` | `JTAG_TDO` |
| 77 | `R_JTAG_TMS` | 改名 | 390 | `node2` | `R_JTAG_TMS` | `R_JTAG_TMS pin1` | `JTAG_TMS_SOC` |
| 78 | `R_JTAG_TMS` | 改名 | 391 | `node1` | `R_JTAG_TMS` | `R_JTAG_TMS pin2` | `JTAG_TMS` |
| 79 | `R_KEY_CAM` | 改名 | 324 | `node2` | `R_KEY_CAM` | `R_KEY_CAM pin1` | `KEY_CAM` |
| 80 | `R_KEY_CAM` | 改名 | 326 | `node1` | `R_KEY_CAM` | `R_KEY_CAM pin2` | `VDD_3V3_IO` |
| 81 | `R_KEY_PWR` | 改名 | 309 | `node2` | `R_KEY_PWR` | `R_KEY_PWR pin1` | `KEY_PWR` |
| 82 | `R_KEY_PWR` | 改名 | 311 | `node1` | `R_KEY_PWR` | `R_KEY_PWR pin2` | `VDD_3V3_IO` |
| 83 | `R_KEY_PWR` | 改名 | 363 | `node2` | `R_KEY_PWR` | `R_KEY_PWR pin1` | `KEY_PWR` |
| 84 | `R_KEY_VM` | 改名 | 319 | `node2` | `R_KEY_VM` | `R_KEY_VM pin1` | `KEY_VOL_M` |
| 85 | `R_KEY_VM` | 改名 | 321 | `node1` | `R_KEY_VM` | `R_KEY_VM pin2` | `VDD_3V3_IO` |
| 86 | `R_KEY_VM` | 改名 | 365 | `node2` | `R_KEY_VM` | `R_KEY_VM pin1` | `KEY_VOL_M` |
| 87 | `R_KEY_VP` | 改名 | 314 | `node2` | `R_KEY_VP` | `R_KEY_VP pin1` | `KEY_VOL_P` |
| 88 | `R_KEY_VP` | 改名 | 316 | `node1` | `R_KEY_VP` | `R_KEY_VP pin2` | `VDD_3V3_IO` |
| 89 | `R_KEY_VP` | 改名 | 364 | `node2` | `R_KEY_VP` | `R_KEY_VP pin1` | `KEY_VOL_P` |
| 90 | `R_LED_G` | 改名 | 303 | `node2` | `R_LED_G` | `R_LED_G pin1` | `LED_G` |
| 91 | `R_LED_G` | 改名 | 304 | `node1` | `R_LED_G` | `R_LED_G pin2` | `LED_G_D` |
| 92 | `R_LED_G` | 改名 | 361 | `node2` | `R_LED_G` | `R_LED_G pin1` | `LED_G` |
| 93 | `R_LED_R` | 改名 | 300 | `node2` | `R_LED_R` | `R_LED_R pin1` | `LED_R` |
| 94 | `R_LED_R` | 改名 | 301 | `node1` | `R_LED_R` | `R_LED_R pin2` | `LED_R_D` |
| 95 | `R_LED_R` | 改名 | 360 | `node2` | `R_LED_R` | `R_LED_R pin1` | `LED_R` |
| 96 | `R_PD_ON` | 改名 | 56 | `node1` | `R_PD_ON` | `R_PD_ON pin1` | `PWR_ON` |
| 97 | `R_PD_ON` | 改名 | 57 | `node1` | `R_PD_ON` | `R_PD_ON pin2` | `GND` |
| 98 | `R_PG_PULL` | 改名 | 62 | `node1` | `R_PG_PULL` | `R_PG_PULL pin1` | `PG_AND` |
| 99 | `R_PG_PULL` | 改名 | 63 | `node1` | `R_PG_PULL` | `R_PG_PULL pin2` | `VDD_1V8_IO` |
| 100 | `R_PU_BOOT_N` | 改名 | 367 | `node2` | `R_PU_BOOT_N` | `R_PU_BOOT_N pin1` | `BOOT_N` |
| 101 | `R_PU_BOOT_N` | 改名 | 384 | `node2` | `R_PU_BOOT_N` | `R_PU_BOOT_N pin1` | `BOOT_N` |
| 102 | `R_PU_BOOT_N` | 改名 | 385 | `node1` | `R_PU_BOOT_N` | `R_PU_BOOT_N pin2` | `VDD_1V8_IO` |
| 103 | `R_PU_I2CA_SCL` | 改名 | 167 | `node2` | `R_PU_I2CA_SCL` | `R_PU_I2CA_SCL pin1` | `I2C_A_SCL` |
| 104 | `R_PU_I2CA_SCL` | 改名 | 169 | `node1` | `R_PU_I2CA_SCL` | `R_PU_I2CA_SCL pin2` | `VDD_1V8_IO` |
| 105 | `R_PU_I2CA_SDA` | 改名 | 168 | `node2` | `R_PU_I2CA_SDA` | `R_PU_I2CA_SDA pin1` | `I2C_A_SDA` |
| 106 | `R_PU_I2CA_SDA` | 改名 | 170 | `node1` | `R_PU_I2CA_SDA` | `R_PU_I2CA_SDA pin2` | `VDD_1V8_IO` |
| 107 | `R_PU_I2CB_SCL` | 改名 | 231 | `node2` | `R_PU_I2CB_SCL` | `R_PU_I2CB_SCL pin1` | `I2C_B_SCL` |
| 108 | `R_PU_I2CB_SCL` | 改名 | 233 | `node1` | `R_PU_I2CB_SCL` | `R_PU_I2CB_SCL pin1` | `I2C_B_SCL` |
| 109 | `R_PU_I2CB_SCL` | 改名 | 235 | `node1` | `R_PU_I2CB_SCL` | `R_PU_I2CB_SCL pin2` | `VDD_3V3_IO` |
| 110 | `R_PU_I2CB_SDA` | 改名 | 232 | `node2` | `R_PU_I2CB_SDA` | `R_PU_I2CB_SDA pin1` | `I2C_B_SDA` |
| 111 | `R_PU_I2CB_SDA` | 改名 | 234 | `node1` | `R_PU_I2CB_SDA` | `R_PU_I2CB_SDA pin1` | `I2C_B_SDA` |
| 112 | `R_PU_I2CB_SDA` | 改名 | 236 | `node1` | `R_PU_I2CB_SDA` | `R_PU_I2CB_SDA pin2` | `VDD_3V3_IO` |
| 113 | `R_PU_ID0` | 改名 | 193 | `node2` | `R_PU_ID0` | `R_PU_ID0 pin1` | `ID_DETECT_0` |
| 114 | `R_PU_ID0` | 改名 | 195 | `node1` | `R_PU_ID0` | `R_PU_ID0 pin2` | `VDD_3V3_IO` |
| 115 | `R_PU_ID0` | 改名 | 359 | `node2` | `R_PU_ID0` | `R_PU_ID0 pin1` | `ID_DETECT_0` |
| 116 | `R_PU_ID1` | 改名 | 197 | `node2` | `R_PU_ID1` | `R_PU_ID1 pin1` | `ID_DETECT_1` |
| 117 | `R_PU_ID1` | 改名 | 199 | `node1` | `R_PU_ID1` | `R_PU_ID1 pin2` | `VDD_3V3_IO` |
| 118 | `R_PU_PG` | 改名 | 191 | `node1` | `R_PU_PG` | `R_PU_PG pin2` | `VDD_3V3_IO` |
| 119 | `R_PU_PG` | 改名 | 358 | `node2` | `R_PU_PG` | `R_PU_PG pin1` | `PWR_GOOD` |
| 120 | `R_PU_RESET_N` | 改名 | 366 | `node2` | `R_PU_RESET_N` | `R_PU_RESET_N pin1` | `RESET_N` |
| 121 | `R_PU_RESET_N` | 改名 | 377 | `node1` | `R_PU_RESET_N` | `R_PU_RESET_N pin1` | `RESET_N` |
| 122 | `R_PU_RESET_N` | 改名 | 378 | `node1` | `R_PU_RESET_N` | `R_PU_RESET_N pin2` | `VDD_1V8_IO` |
| 123 | `R_SEL_CK_N` | 改名 | 213 | `node2` | `R_SEL_CK_N` | `R_SEL_CK_N pin1` | `DSI_D0_CK_N_SRC` |
| 124 | `R_SEL_CK_N` | 改名 | 214 | `node1` | `R_SEL_CK_N` | `R_SEL_CK_N pin2` | `DSI_D0_CK_N` |
| 125 | `R_SEL_CK_P` | 改名 | 211 | `node2` | `R_SEL_CK_P` | `R_SEL_CK_P pin1` | `DSI_D0_CK_P_SRC` |
| 126 | `R_SEL_CK_P` | 改名 | 212 | `node1` | `R_SEL_CK_P` | `R_SEL_CK_P pin2` | `DSI_D0_CK_P` |
| 127 | `R_SEL_D0_N` | 改名 | 217 | `node2` | `R_SEL_D0_N` | `R_SEL_D0_N pin1` | `DSI_D0_D0_N_SRC` |
| 128 | `R_SEL_D0_N` | 改名 | 218 | `node1` | `R_SEL_D0_N` | `R_SEL_D0_N pin2` | `DSI_D0_D0_N` |
| 129 | `R_SEL_D0_P` | 改名 | 215 | `node2` | `R_SEL_D0_P` | `R_SEL_D0_P pin1` | `DSI_D0_D0_P_SRC` |
| 130 | `R_SEL_D0_P` | 改名 | 216 | `node1` | `R_SEL_D0_P` | `R_SEL_D0_P pin2` | `DSI_D0_D0_P` |
| 131 | `R_SEL_D1_N` | 改名 | 221 | `node2` | `R_SEL_D1_N` | `R_SEL_D1_N pin1` | `DSI_D0_D1_N_SRC` |
| 132 | `R_SEL_D1_N` | 改名 | 222 | `node1` | `R_SEL_D1_N` | `R_SEL_D1_N pin2` | `DSI_D0_D1_N` |
| 133 | `R_SEL_D1_P` | 改名 | 219 | `node2` | `R_SEL_D1_P` | `R_SEL_D1_P pin1` | `DSI_D0_D1_P_SRC` |
| 134 | `R_SEL_D1_P` | 改名 | 220 | `node1` | `R_SEL_D1_P` | `R_SEL_D1_P pin2` | `DSI_D0_D1_P` |
| 135 | `R_SEL_D2_N` | 改名 | 225 | `node2` | `R_SEL_D2_N` | `R_SEL_D2_N pin1` | `DSI_D0_D2_N_SRC` |
| 136 | `R_SEL_D2_N` | 改名 | 226 | `node1` | `R_SEL_D2_N` | `R_SEL_D2_N pin2` | `DSI_D0_D2_N` |
| 137 | `R_SEL_D2_P` | 改名 | 223 | `node2` | `R_SEL_D2_P` | `R_SEL_D2_P pin1` | `DSI_D0_D2_P_SRC` |
| 138 | `R_SEL_D2_P` | 改名 | 224 | `node1` | `R_SEL_D2_P` | `R_SEL_D2_P pin2` | `DSI_D0_D2_P` |
| 139 | `R_SEL_D3_N` | 改名 | 229 | `node2` | `R_SEL_D3_N` | `R_SEL_D3_N pin1` | `DSI_D0_D3_N_SRC` |
| 140 | `R_SEL_D3_N` | 改名 | 230 | `node1` | `R_SEL_D3_N` | `R_SEL_D3_N pin2` | `DSI_D0_D3_N` |
| 141 | `R_SEL_D3_P` | 改名 | 227 | `node2` | `R_SEL_D3_P` | `R_SEL_D3_P pin1` | `DSI_D0_D3_P_SRC` |
| 142 | `R_SEL_D3_P` | 改名 | 228 | `node1` | `R_SEL_D3_P` | `R_SEL_D3_P pin2` | `DSI_D0_D3_P` |
| 143 | `R_SER_CSI_MCLK` | 改名 | 270 | `node2` | `R_SER_CSI_MCLK` | `R_SER_CSI_MCLK pin1` | `CSI_MCLK_SRC` |
| 144 | `R_SER_CSI_MCLK` | 改名 | 271 | `node1` | `R_SER_CSI_MCLK` | `R_SER_CSI_MCLK pin2` | `CSI_MCLK` |
| 145 | `R_SER_FSIN` | 改名 | 356 | `node2` | `R_SER_FSIN` | `R_SER_FSIN pin1` | `FSIN_OUT` |
| 146 | `R_SER_FSIN` | 改名 | 400 | `node2` | `R_SER_FSIN` | `R_SER_FSIN pin2` | `FSIN` |
| 147 | `R_SER_FSIN` | 改名 | 401 | `node1` | `R_SER_FSIN` | `R_SER_FSIN pin1` | `FSIN_OUT` |
| 148 | `R_SER_RESET_N` | 改名 | 377 | `node2` | `R_SER_RESET_N` | `R_SER_RESET_N pin1` | `RESET_N` |
| 149 | `R_SER_RESET_N` | 改名 | 379 | `node1` | `R_SER_RESET_N` | `R_SER_RESET_N pin2` | `RESET_N_SOC` |
| 150 | `R_SER_SPI_CSn` | 改名 | 203 | `node2` | `R_SER_SPI_CSn` | `R_SER_SPI_CSn pin1` | `SPI_CSn` |
| 151 | `R_SER_SPI_CSn` | 改名 | 204 | `node1` | `R_SER_SPI_CSn` | `R_SER_SPI_CSn pin2` | `SPI_CSn_BOOT` |
| 152 | `R_SER_SPI_MISO` | 改名 | 207 | `node2` | `R_SER_SPI_MISO` | `R_SER_SPI_MISO pin1` | `SPI_MISO` |
| 153 | `R_SER_SPI_MISO` | 改名 | 208 | `node1` | `R_SER_SPI_MISO` | `R_SER_SPI_MISO pin2` | `SPI_MISO_BOOT` |
| 154 | `R_SER_SPI_MOSI` | 改名 | 205 | `node2` | `R_SER_SPI_MOSI` | `R_SER_SPI_MOSI pin1` | `SPI_MOSI` |
| 155 | `R_SER_SPI_MOSI` | 改名 | 206 | `node1` | `R_SER_SPI_MOSI` | `R_SER_SPI_MOSI pin2` | `SPI_MOSI_BOOT` |
| 156 | `R_SER_SPI_SCLK` | 改名 | 201 | `node2` | `R_SER_SPI_SCLK` | `R_SER_SPI_SCLK pin1` | `SPI_SCLK` |
| 157 | `R_SER_SPI_SCLK` | 改名 | 202 | `node1` | `R_SER_SPI_SCLK` | `R_SER_SPI_SCLK pin2` | `SPI_SCLK_BOOT` |
| 158 | `R_SER_USB_D_N` | 改名 | 292 | `node2` | `R_SER_USB_D_N` | `R_SER_USB_D_N pin1` | `USB_D_N_SRC` |
| 159 | `R_SER_USB_D_N` | 改名 | 432 | `node1` | `R_SER_USB_D_N` | `R_SER_USB_D_N pin2` | `NET_USB_D_N_TYPEC` |
| 160 | `R_SER_USB_D_P` | 改名 | 291 | `node2` | `R_SER_USB_D_P` | `R_SER_USB_D_P pin1` | `USB_D_P_SRC` |
| 161 | `R_SER_USB_D_P` | 改名 | 431 | `node1` | `R_SER_USB_D_P` | `R_SER_USB_D_P pin2` | `NET_USB_D_P_TYPEC` |
| 162 | `R_SUPV_DIV1` | 改名 | 404 | `node2` | `R_SUPV_DIV1` | `R_SUPV_DIV1 pin1` | `V_SOC_IO` |
| 163 | `R_SUPV_DIV1` | 改名 | 405 | `node1` | `R_SUPV_DIV1` | `R_SUPV_DIV1 pin2` | `SUPV_SENSE` |
| 164 | `R_SUPV_DIV2` | 改名 | 405 | `node2` | `R_SUPV_DIV2` | `R_SUPV_DIV2 pin1` | `SUPV_SENSE` |
| 165 | `R_SUPV_DIV2` | 改名 | 406 | `node1` | `R_SUPV_DIV2` | `R_SUPV_DIV2 pin2` | `GND` |
| 166 | `R_VBUS_DET_D1` | 改名 | 434 | `node1` | `R_VBUS_DET_D1` | `R_VBUS_DET_D1 pin1` | `RAIL_DEMO_5V` |
| 167 | `R_VBUS_DET_D1` | 改名 | 435 | `node1` | `R_VBUS_DET_D1` | `R_VBUS_DET_D1 pin2` | `VBUS_DET_D` |
| 168 | `R_VBUS_DET_D2` | 改名 | 435 | `node2` | `R_VBUS_DET_D2` | `R_VBUS_DET_D2 pin1` | `VBUS_DET_D` |
| 169 | `R_VBUS_DET_D2` | 改名 | 436 | `node1` | `R_VBUS_DET_D2` | `R_VBUS_DET_D2 pin2` | `GND` |
| 170 | `CHG_GND_STAR` | 改名 | 165 | `node2` | `CHG_GND_STAR` | `CHG_GND_STAR pin1` | `GND` |
| 171 | `CHG_GND_STAR` | 改名 | 166 | `node1` | `CHG_GND_STAR` | `CHG_GND_STAR pin1` | `GND` |
| 172 | `CHG_GND_STAR` | 改名 | 415 | `node1` | `CHG_GND_STAR` | `CHG_GND_STAR pin1` | `GND` |
| 173 | `D_ESD_CAM` | 改名 | 163 | `node1` | `D_ESD_CAM` | `D_ESD_CAM pin1` | `GND` |
| 174 | `D_ESD_CAM` | 改名 | 413 | `node2` | `D_ESD_CAM` | `D_ESD_CAM pin2` | `CSI_D0_CK_P` |
| 175 | `D_ESD_CAM` | 改名 | 414 | `node1` | `D_ESD_CAM` | `D_ESD_CAM pin1` | `GND` |
| 176 | `D_ESD_DEMO` | 改名 | 420 | `node1` | `D_ESD_DEMO` | `D_ESD_DEMO pin1` | `RAIL_DEMO_5V` |
| 177 | `D_ESD_DEMO` | 改名 | 421 | `node1` | `D_ESD_DEMO` | `D_ESD_DEMO pin2` | `GND` |
| 178 | `D_ESD_USB_D` | 改名 | 417 | `node1` | `D_ESD_USB_D` | `D_ESD_USB_D pin1` | `NET_USB_D_P_TYPEC` |
| 179 | `D_ESD_USB_D` | 改名 | 418 | `node1` | `D_ESD_USB_D` | `D_ESD_USB_D pin2` | `GND` |
| 180 | `FB_DEMO` | 改名 | 422 | `node1` | `FB_DEMO` | `FB_DEMO pin1` | `RAIL_DEMO_5V` |
| 181 | `FB_DEMO` | 改名 | 423 | `node1` | `FB_DEMO` | `FB_DEMO pin2` | `GND` |
| 182 | `Q_AND` | 改名 | 65 | `node1` | `Q_AND` | `Q_AND pin1` | `RESET_N` |
| 183 | `Q_AND` | 改名 | 66 | `node1` | `Q_AND` | `Q_AND pin2` | `GND` |
| 184 | `Q_AND` | 改名 | 67 | `node1` | `Q_AND` | `Q_AND pin3` | `PG_AND` |
| 185 | `Q_ENVC` | 改名 | 71 | `node1` | `Q_ENVC` | `Q_ENVC pin1` | `PG_AND` |
| 186 | `Q_ENVC` | 改名 | 72 | `node1` | `Q_ENVC` | `Q_ENVC pin2` | `GND` |
| 187 | `Q_ENVC` | 改名 | 73 | `node1` | `Q_ENVC` | `Q_ENVC pin3` | `EN_VCORE` |
| 188 | `Q_PG` | 改名 | 59 | `node1` | `Q_PG` | `Q_PG pin1` | `PWR_GOOD` |
| 189 | `Q_PG` | 改名 | 60 | `node1` | `Q_PG` | `Q_PG pin2` | `BAT_SW` |
| 190 | `Q_PG` | 改名 | 61 | `node1` | `Q_PG` | `Q_PG pin3` | `PWR_ON` |
| 191 | `SW_BOOT` | 改名 | 386 | `node1` | `SW_BOOT` | `SW_BOOT pin1` | `BOOT_N` |
| 192 | `SW_BOOT` | 改名 | 387 | `node1` | `SW_BOOT` | `SW_BOOT pin2` | `GND` |
| 193 | `SW_KEY_PWR` | 改名 | 310 | `node1` | `SW_KEY_PWR` | `SW_KEY_PWR pin1` | `KEY_PWR` |
| 194 | `SW_KEY_PWR` | 改名 | 312 | `node1` | `SW_KEY_PWR` | `SW_KEY_PWR pin2` | `GND` |
| 195 | `SW_KEY_VM` | 改名 | 320 | `node1` | `SW_KEY_VM` | `SW_KEY_VM pin1` | `KEY_VOL_M` |
| 196 | `SW_KEY_VM` | 改名 | 322 | `node1` | `SW_KEY_VM` | `SW_KEY_VM pin2` | `GND` |
| 197 | `SW_KEY_VP` | 改名 | 315 | `node1` | `SW_KEY_VP` | `SW_KEY_VP pin1` | `KEY_VOL_P` |
| 198 | `SW_KEY_VP` | 改名 | 317 | `node1` | `SW_KEY_VP` | `SW_KEY_VP pin2` | `GND` |
| 199 | `SW_RST` | 改名 | 382 | `node1` | `SW_RST` | `SW_RST pin1` | `RESET_N` |
| 200 | `SW_RST` | 改名 | 383 | `node1` | `SW_RST` | `SW_RST pin2` | `GND` |

★**合计 200 条** (改名 196 + 补行 4) ⇒ ★**脚数自洽: 具名脚 182 只 + 补行 4 只 = 改名覆盖 178 只** ★ ⇒ ★**没有一件漏, 也没有一件多**★。

★**三条落表时的坑 (★本单实跑踩出来的★)**:

1. ★**只改 MAIN_PCB 行的 bare 节点串** ★ —— `state/check_pcb_nets.py` 的 C4 口径**先按 `board` 列过滤** ⇒ ★**跨板行 (CHG_BOARD) 的同名裸端不参与占位脚号编号** ⇒ ★**改了它对 C4 一点用都没有, 反而会让「行序 ↔ 焊盘号」的对应关系错位**★。★**本单实跑登记了 1 件存在跨板同名裸端: `R_PU_PG` (行 190 · node2 · PWR_GOOD)**★ (★该行本单只登记, 不改★)。
2. ★**具名脚必须按【脚表真值】编号, 不能按【网表行序】编号** ★ —— 本单实跑: `R_PU_PG` 的 MAIN_PCB 行序是 `VDD_3V3_IO`(行 191) 在前、`PWR_GOOD`(行 358) 在后 ⇒ ★**按行序编号会得到 pin1=VDD_3V3_IO, 而脚表真值是 pin1=PWR_GOOD**★ ⇒ ★**两者对 `R_PU_PG` / `Q_PG` 两件会给出【相反的板面接线】**★ ⇒ ★**⇒ 具名脚一律取 `HW/netlist_v1_pins.csv` 的 `pin` 栏; 这两件的板面 pad↔net 必须在腿 A 里同时对调**★。
3. ★**4 件的 GND 脚在网表里根本没有以节点形态出现 (脚表里有)** ★ —— `C_KEY_PWR` / `C_KEY_VM` / `C_KEY_VP` / `R_BAT_DET_2`: ★**脚表 `pin` 栏有 `2` (net=GND), 但 `HW/netlist_v1.csv` 里该器件的 GND 端是写在 `node2` 槽里的网名 `GND` (不是节点串) ⇒ 网表侧只推出 1 个脚** ★ ⇒ ★**光改名不够, 必须补 4 行** ★ ⇒ ★**补行后网表推出 2 个脚, 才与官方 2 焊盘 land 对上 (否则 C2/C3 红)** ★。

## §3 板侧那 5 条差异的并表 (★本单把它们跟 90 件绑在一张表上·不许漏★)

| # | 板侧差异 (C1 基线读数) | 在 90 件清单的哪一行 | 换 land 时怎么一起改 | 改完 `check_pcb_nets.py` 的 C1 会变成什么 |
|---|---|---|---|---|
| 1 | 多余: `C_VBUS_GND` pad1 = GND | ★**不在 90 件清单里** ★ (★BOM `dnp=DNP` · `board=镜框充电板` · 网表 3 行全是 `board=CHG_BOARD` ⇒ **不进 C4 的 MAIN_PCB 口径**) | ★**本单不改它** ★ —— 换 land 动不到它 (它不在 90 件里); ★**它的 2 个 pad 是充电板侧的件, 而 C1 的网表侧只按 MAIN_PCB 过滤** ★ ⇒ ★**⇒ 换完 land 后它仍然是 C1 的「多余 2」** ★ | ★**仍 多 2** ★ (沙盒 S3/S4 实测: `★多: C_VBUS_GND pad1 = GND` / `pad2 = VBUS_5V_CHG`) ⇒ ★**要清掉它只能靠「留位 / 下板」的拍板 (老板 B 类), 不在 S10 换封装这一趟的射程内** ★ |
| 2 | 多余: `C_VBUS_GND` pad2 = VBUS_5V_CHG | 同上 | 同上 | 同上 |
| 3 | 错: `Q_PG` pad1 应为 PWR_GOOD 实际 PWR_ON | ★**在第 85 行 (`Q_PG`·缺口桶)·§1 的 `Q_PG` 行 行** ★ | ★**换 land 时同时把 pad1 的网改成 PWR_GOOD** ★ (★器件 DMP3098L 官方脚序 1=G/2=S/3=D ⇒ pad1=栅极=PWR_GOOD★) ⇒ ★**★不改 ⇒ 板面把栅极接到 PWR_ON, 开机路径直接不通 (ISS-283 G-1 裁决「写法 A」)★★ | ★**同号异网 3 → 0** ★ (沙盒 S3/S4 实测: 错 0) |
| 4 | 错: `Q_PG` pad3 应为 PWR_ON 实际 PWR_GOOD | ★**在第 85 行 (`Q_PG`·缺口桶)·§1 的 `Q_PG` 行 行** ★ | ★**换 land 时同时把 pad3 的网改成 PWR_ON** ★ (★= 漏极 D·负载侧★) | ★**同号异网 3 → 0** ★ |
| 5 | 错: `D_ESD_USB_D` pad1 应为 NET_USB_D_P_TYPEC 实际 USB_D_P_SRC | ★**在第 81 行 (`D_ESD_USB_D`·缺口桶)·§1 的 `D_ESD_USB_D` 行 行** ★ | ★**换 land 时把 pad1 的网改成 NET_USB_D_P_TYPEC** ★ (★= TypeC 侧那一段; 现在的 USB_D_P_SRC 是 SoC 侧·中间隔着 `R_SER_USB_D_P`★) ⇒ ★**★不改 ⇒ ESD 泄放路径接在错误的一侧, 等于没接★★ | ★**同号异网 3 → 0** ★ (沙盒 S3/S4 实测: 错 0) |

★**★本单另挖出的第 6 条 (★C1 看不见, 但腿 A 必须一起改★)★**:

| # | 差异 | 在 90 件清单的哪一行 | 换 land 时怎么一起改 | 改完 C1 会变成什么 |
|---|---|---|---|---|
| 6 | ★**`R_PU_PG` pad1 = VDD_3V3_IO / pad2 = PWR_GOOD, 而脚表真值是 pin1 = PWR_GOOD / pin2 = VDD_3V3_IO ⇒ 【板面 pad↔net 与脚表真值相反】** ★ | ★**在第 53 行 (`R_PU_PG`·靶内桶)·§1 的 `R_PU_PG` 行 行** ★ | ★**换 land 时把 pad1/pad2 的网对调** ★ (★10k 上拉: PWR_GOOD 开漏上拉 ⇒ 电阻两端对调不影响电气功能, **所以 C1 看不见**★ ⇒ ★**但腿 B 的具名脚是按脚表真值编号的 ⇒ 不对调就会得到【板脚号与网表脚号相反】**★) | ★**C1 读数不变 (本来就绿)** ★ ⇒ ★**但 C1 绿 ≠ 对** ★ ⇒ ★**★腿 A 不对调 ⇒ 那一趟的板子上下拉电阻脚位是反的★★ |

★**沙盒四轮的 C1 读数 (★真闸代码跑出来的★)**:

| 轮次 | 板 | 网表 | C1 读数 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|
| S0 基线 | 真板 | 真表 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482 | — | — | ★**158**★ |
| ↳ 失败项 | | | C1 焊盘级不等价 (缺0/多2/错3/非法NC0) | | | |
| S1 腿A单独 | 板副本(腿A) | 真表 | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 486 | — | — | ★**158**★ |
| ↳ 失败项 | | | C1 焊盘级不等价 (缺0/多6/错2/非法NC0); C3 焊盘数不符 7 个 | | | |
| S2 腿B单独 | 真板 | 网表副本(腿B) | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 484 / 板上(带网) 482 | — | — | ★**68**★ |
| ↳ 失败项 | | | C1 焊盘级不等价 (缺4/多2/错5/非法NC0); C2 针号/针数不符 4 个: ['C_KEY_PWR', 'C_KEY_VM', 'C_KEY_VP', 'R_BAT_DET_2']; C3 焊盘数不符 4 个 | | | |
| S3 腿A+腿B | 板副本(腿A) | 网表副本(腿B) | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 484 / 板上(带网) 486 | — | — | ★**68**★ |
| ↳ 失败项 | | | C1 焊盘级不等价 (缺0/多2/错0/非法NC0); C3 焊盘数不符 3 个 | | | |
| S4 腿A+腿B·K3走(b) | 板副本(腿A) | 网表副本(腿B) | ❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 484 / 板上(带网) 486 | — | — | ★**68**★ |
| ↳ 失败项 | | | C1 焊盘级不等价 (缺0/多2/错0/非法NC0) | | | |

## §4 两条只登记不代拍的分支 (★原样继承 ISS-361 §5, 本单不代拍★)

### §4.1 K2 · `D_ESD_USB_D` 最终 2 脚还是 3 脚 (★随老板 W-1/W-2 分叉★)

| 路 | 候选封装 (实测在盘) | 板面 land 数 | 网表脚数 | 会红哪道闸 | 代价 |
|---|---|---|---|---|---|
| (a) 2 脚档 | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 2 | 2 (脚表已有) | ★**C1/C2/C3 全绿** ★ (★沙盒 S3 实测: 本件不在 C1/C3 失败项里★) | ★**泄放路径要另算** ★ (一颗双通道件只覆盖 2 根线) + ★**该件离 `J_USB_C` 现在的 47.99 mm 要缩到 ≤3.0 mm (那一趟 B08) ⇒ 布线要重跑** ★ |
| (b) 3 脚档 | `Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db` | 3 | ★**3 (脚表 + 网表都要补第 3 脚)** ★ | ★**C3 红「板 3 脚 / 网表 2 脚」★ ★ 直到脚表与网表补齐第 3 脚 | ★**pad 序须按最终型号厂商 land 逐颗复核** ★ (★本栏只是几何候选, 不是代拍★) |

★**★不代拍** ★ —— 哪一档生效是老板 W-1/W-2 的拍板项。★**本单只登记候选封装 + 各自代价 + 各自会红哪道闸** ★。

### §4.2 K3 · 5 只按键 (`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`) 的 2 脚 vs 4 焊盘

★**事实**: 官方 `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` 有 ★**4 个物理焊盘 (焊盘号 1,1,2,2)**★, 而网表这 5 只只有 2 个脚 ⇒ ★**板面从 2 land 变 4 land**★。

| 路 | 做法 | 板面 land 数 | 网表脚数 | 会红哪道闸 | 代价 |
|---|---|---|---|---|---|
| (a) 网表给这 5 只加 2 个具名脚 | 脚表 `HW/netlist_v1_pins.csv` 加行 (★**`pin` 栏要加**★) + `HW/netlist_v1.csv` 的 node 串补具名脚 | 4 | 4 | ★**C3 绿** ★ (★若只改板不改网表 ⇒ ★**C3 红「板 4 脚 / 网表 2 脚」**★★) | ★**脚表 + 网表两处都要动** ★ + ★**KMR2 的 4 个焊盘号是 1,1,2,2 ⇒ 脚表只能记 2 个 pin (1/2) ⇒ 板面同号多脚** ★ |
| (b) 改选 2 焊盘按键封装 | 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` md5 `749f20c5ab898069ade01682274c7bbf` (2 焊盘 @3.400 mm) 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c` (2 焊盘 @3.250 mm) | 2 | 2 | ★**C3 绿** ★ (★沙盒 S4 实测: K3 走 (b) 路时 C3 不符 = 0★) | ★**按动力度 3N → 1.5N ⇒ 误触风险上升** ★ (★矩阵 §⑮~⑲ 选 3N 的理由就是防误触★) ⇒ ★**★这是选型代价, 不是本单能拍的** ★ |

★**★不代拍** ★ —— ★**本单只给两条路 + 代价 + 各自会红哪道闸** ★。

★**★沙盒把 K3 的代价量化了 (★这是本单新增的读数★)★**:

- ★**S3 (腿 A 全做, 含那 3 只换 KMR2 4 焊盘) ⇒ `C3 焊盘数不符 3 个`** ★ (★= `SW_BOOT` / `SW_KEY_PWR` / `SW_RST` 三只★) ⇒ ★**⇒ K3 走 (a) 路但网表没补脚 ⇒ 那道闸当场红** ★。
- ★**S4 (腿 A 全做, 但那 3 只按键不换 land = K3 走 (b) 路) ⇒ `C3 焊盘数不符 0 个`** ★ ⇒ ★**⇒ C4 目标 68 在 K3 走 (b) 路时【连 C3 都能一起绿】** ★。
- ★**⇒ 无论 K3 走哪条路, C4 目标 68 都成立 (C4 只看网表节点串)** ★。

## §5 两条漏件的并入建议 (★只给建议 + 机器判据, 零改既有页★)

### §5.1 `FB_DEMO` (★ISS-361 §5 K4 已登记·本单并进去★)

| 项 | 实测 |
|---|---|
| 那一趟两份文件里的命中数 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` **0** 次 · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` **0** 次 (★其余 12 件都出现过: `CHG_GND_STAR` 7/0 · `D_ESD_CAM` 2/6 · `D_ESD_DEMO` 2/0 · `D_ESD_USB_D` 19/15 · `Q_AND` 4/9 · `Q_ENVC` 2/7 · `Q_PG` 16/18 · `SW_BOOT` 7/3 · `SW_KEY_PWR` 8/3 · `SW_KEY_VM` 8/3 · `SW_KEY_VP` 8/3 · `SW_RST` 8/3★) |
| 现占位几何 [实测] | ★**斜置 2 land @对角 1.000 mm**★ (fab 2.00×1.60 mm · pad 0.550×0.900 mm) |
| 官方 0805 目标几何 [实测] | ★**正置 @2.125 mm**★ (fab 2.00×0.90 mm · pad 0.875×1.200 mm) |
| 结论 | ★**不改封装它就装不上** ★ ⇒ ★**必须并进那一趟的 land 重画清单** ★ |
| ★**本单的建议 (★不改那两份文件★)** ★ | ★**① 把它并进那一趟的 land 重画清单; ② 机器判据建议: `grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 `grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的命中数都须 ≥ 1** ★ |
| ★**机器判据为什么这样写** ★ | ★**不是「文件里有这个词就算过」—— 是「两份文件里都排上了它」** ★ (★本单实测: 13 件里只有它两份都是 0★) |

### §5.2 `CHG_GND_STAR` (★ISS-361 §5 K1 已登记·本单并进去·零改基线页★)

| 项 | 实测 |
|---|---|
| 自相矛盾的那一格 | `HW/FP_TRUTH_BASELINE.md` §2.2 靶外同族登记表里该行的「是否触发布局/布线改动」栏写 ★**「板面只有 1 个 land, 官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘 ⇒ 该器件接地脚与走线全新增」**★ |
| 同页正文怎么说的 | 同页正文写 ★**「`CHG_GND_STAR` 的情况与另 2 件不同: 它在网表里只有 1 个脚 (GND) ⇒ 1 个 land 是对的」**★ ⇒ ★**同一页两处打架** ★ |
| 官方封装实测 | ★**`TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` 只有 1 个焊盘**★ (pad "1" smd circle 1.0×1.0 mm, md5 `cea8eb3ba9b799767624661848b00243`) ⇒ ★**★那一格是错的, 照它改板会给 CHG_GND_STAR 加一个不存在的第 2 个 land**★ |
| ★**本单的建议 (★零改基线页★)** ★ | ★**① 把 §2.2 那一格的「官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘」订正为「官方封装 1 焊盘 (实测 md5 `cea8eb3ba9b799767624661848b00243`), 板面 1 个 land 即为正确, 不新增」; ② 机器判据建议: 该行「焊盘数 / 网络核对结论」栏的 `1=1` 与目标封装的实测焊盘数必须一致** ★ |
| 为什么零改基线页 | ★**`HW/FP_TRUTH_BASELINE.md` 是 ISS-356 的签收页 ⇒ 改了它 ISS-356 的签收脚本会红** ★ ⇒ ★**⇒ 本单只登记 + 给订正建议 + 给机器判据, 一个字不动** ★ |

## §6 降级方案 (★逐件必填 · 一件不空 · 三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★)

★**口径**: ★**查不到 ⇒ 三选一写清代价**★ ⇒ ★**每件都给了「已实测在盘的等效件 + 代价」, 零外部等待式措辞**★。

| ref | 桶 | 查不到的点 | 降级方案 (三选一 + 代价) |
|---|---|---|---|
| `C_AC_CSI_D0_CK_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_CK_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D0_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D0_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D1_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D1_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D2_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D2_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D3_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_AC_CSI_D0_D3_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_LIGHT_3V3` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_VDD_1V8_IO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_BULK_VDD_3V3_IO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_DET_BAT` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_DET_VBUS_D` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_LIGHT_3V3` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_VDD_1V8_IO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_HF_VDD_3V3_IO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_KEY_PWR` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_KEY_VM` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_KEY_VP` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `C_RST` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_SW_IN` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_SW_OUT` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_TEMP` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `C_VBUS_DEMO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该容值/耐压/介质官网无现货 ⇒ 换同容值同耐压 0603 X7R 等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→0.96mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `D_LED_G` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0805 绿无官网现货 ⇒ 换同封装 0805 绿等效件 (Kingbright AP2012 系列); 若要两颗同封装 ⇒ 两颗都改 0805 (ISS-241 §⑬ 已把"对称性"留给 main, 本单沿用不代裁) ⇒ 代价 = 红件 OPN 要重查 + 亮度账 (G-5) 重算 |
| `D_LED_R` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 PLCC-2 红无官网现货 ⇒ 换同封装 0603 PLCC-2 等效件; 注意 PLCC-2 与普通 0603 chip 的引脚几何不同 ⇒ 落板批次按原厂 land 重画 (ISS-241 §⑬ 已记) |
| `R_BAT_DET_1` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_BAT_DET_2` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若该件首版不装 ⇒ BOM 标 DNP 但板面仍须补第 2 land (否则将来转必装时装不上); 若整批取消 ⇒ land 与走线一起删 ⇒ 板 md5 再变一次 (⇒ 与"板只改一次"冲突 ⇒ 建议保留 land) |
| `R_CC1_D` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_CC2_D` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_EN_VCORE` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TCK` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TDI` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TDO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_JTAG_TMS` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_CAM` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_PWR` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_VM` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_KEY_VP` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_LED_G` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_LED_R` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PD_ON` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PG_PULL` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_BOOT_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CA_SCL` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CA_SDA` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CB_SCL` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_I2CB_SDA` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_ID0` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_ID1` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_PG` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_PU_RESET_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_CK_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_CK_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D0_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D0_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D1_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D1_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D2_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D2_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D3_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SEL_D3_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_CSI_MCLK` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_FSIN` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_RESET_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_CSn` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_MISO` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_MOSI` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_SPI_SCLK` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_USB_D_N` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SER_USB_D_P` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SUPV_DIV1` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_SUPV_DIV2` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_VBUS_DET_D1` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `R_VBUS_DET_D2` | 靶内 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 0603 该阻值/精度官网无现货 ⇒ 换同阻值同精度 0603 厚膜等效件 (封装不变 ⇒ 板面零改动); 若必须缩到 0402 ⇒ land 中心距 1.60→1.02mm ⇒ 该 net 走线端点要重画 ⇒ 代价大 |
| `CHG_GND_STAR` | 缺口 | ★型号 (它是单点汇流位, 非器件) + §5.2 那一格的自相矛盾★ | 若落表批次要把它当可拆件 ⇒ 改用 2 焊盘件 (例 `Diode_SMD:D_SOD-323` md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = 新增第 2 脚 + 网表加 GND 以外的第二个网 ⇒ 与单点汇流位的功能定义冲突 ⇒ 不建议 |
| `D_ESD_CAM` | 缺口 | ★pad↔net 序 (器件 1=I/O 2=GND, 板是反的) ⇒ 靠改 land 一并解决, 不靠查料★ | 若 TI X1SON-2 封装在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 无第二档 ⇒ 改用 2 脚 SOD-323 单通道件 `Diode_SMD:D_SOD-323` (md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = Cd 0.42pF → 45pF ⇒ CSI-2 高速线上不可用 (Cd 45pF 会吃掉眼图裕量) ⇒ 不建议 |
| `D_ESD_DEMO` | 缺口 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 SOD-323 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Diode_SMD:D_SOD-323F` (SOD-323 带引脚变体) ⇒ 代价 = 焊接方式变 ⇒ 钢网要改 ⇒ 不建议; 或改小封装 `Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm` (md5 `c57a4058f16cf35599c2b748b9434350`) ⇒ 代价 = 手工贴装 + 板面更挤 ⇒ 不建议 |
| `D_ESD_USB_D` | 缺口 | ★**最终是 2 脚还是 3 脚 (老板 W-1/W-2 未拍)** ⇒ 目标封装随分支变 | ★3 脚档的候选封装随 W-1/W-2 分叉★ ⇒ 若拍「一颗双通道 3 脚」⇒ 候选 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`, 3 焊盘) ⇒ 代价 = ★**pad 序须按最终型号厂商 land 复核**★ (本栏 SOT-23-3 只是几何候选, 不是代拍); 若拍「两颗单通道」⇒ 本行保持 2 脚 X1SON-2 + 另加一只 2 脚件 (D− 侧) ⇒ 代价 = 板上多一颗件 + 两处 land 都要画 ⇒ 仍在本趟内可完成 |
| `FB_DEMO` | 缺口 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 Murata 0805 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Inductor_SMD:L_0805_2012Metric` 唯一档 ⇒ 改用更小 0603 (如 `Inductor_SMD:L_0603_1608Metric`) ⇒ 代价 = 电流 2A 降额到 1A 级 (BLM21PG 2000mA 是选型硬判据) ⇒ 不建议 |
| `Q_AND` | 缺口 | ★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★ | 若 SOT-23 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_TO_SOT_SMD:SOT-23` 唯一档 ⇒ 换 SOT-23 的 TO-236 变体 (`Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ ★**代价 = 厂商脚序可能不同, 必须逐颗重核 1=G/2=S/3=D**★ ⇒ 不省事, 不建议 |
| `Q_ENVC` | 缺口 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `Q_PG` | 缺口 | ★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★ | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `SW_BOOT` | 缺口 | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | ★若不改网表 ⇒ 只能选 2 land 的按键封装★ ⇒ 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` (md5 `749f20c5ab898069ade01682274c7bbf`, 2 焊盘 @3.400 mm, 本体 3.0×2.5mm) ⇒ 代价 = 按动力度 1.5N vs KMR2 的 3.0N ⇒ BOOT 键误触风险上升 (矩阵 §⑮ 选 3N 的理由就是防误触) ⇒ ★**这是选型代价, 不是本单能拍的**★; 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, C&K KXT3) ⇒ 代价 = 同上, 且本体 3.5×2.0 |
| `SW_KEY_PWR` | 缺口 | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | 同 SW_BOOT: 不改网表则只能选 2 land 封装 (`SW_SPST_B3U-1000P` md5 `749f20c5ab898069ade01682274c7bbf` / `SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 按动力度降到 1.5N ⇒ 电源键误触风险上升 ⇒ ★不代拍★ |
| `SW_KEY_VM` | 缺口 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 B3U-1000P 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Button_Switch_SMD:SW_SPST_B3U-1000P` 唯一档 ⇒ 改 KXT3 (`Button_Switch_SMD:SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, 本体 3.5×2.0mm) ⇒ 代价 = 宽度 3.5 > 占位 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议 |
| `SW_KEY_VP` | 缺口 | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 同 SW_KEY_VM ⇒ 退到 KXT3 (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ 邻键间隙复核 ⇒ 不建议 |
| `SW_RST` | 缺口 | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | 同 SW_BOOT: 不改网表则只能选 2 land 封装 ⇒ 代价 = 按动力度降到 1.5N ⇒ 复位键误触风险上升 ⇒ ★不代拍★ |

★**90 件逐件非空**★ (★§1 表的「降级方案」栏与本表同源·同一段文字★)。

## §7 未决项与卡点 (★只登记, 不代拍★)

| # | 卡点 | 事实 | 本单实测/依据 | 要谁答 |
|---|---|---|---|---|
| K1 | ★**`D_ESD_USB_D` 最终 2 脚还是 3 脚** ★ | 现行 BOM opn 是 2 脚 TPD1E05U06DPYR, 那一趟 B07 要求它变 3 脚 | ★**两个分支的候选封装本单都已实测在盘** ★ (3 脚档 `Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db` / 2 脚档 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 `0edfa97bd7bd277f3c05acf2bee23892`) ⇒ ★**沙盒实测: 走 2 脚档时 C1/C2/C3 全绿; 走 3 脚档时 C3 红「板 3 脚 / 网表 2 脚」** ★ | ★**老板 W-1/W-2** ★ |
| K2 | ★**5 只按键 3N vs 1.5N** ★ | 官方 `SW_Push_1P1T_NO_CK_KMR2` 有 4 个物理焊盘 (1,1,2,2), 网表这 5 只只有 2 个脚 | ★**沙盒量化: 走 (a) 路而网表不补脚 ⇒ C3 红 3 件; 走 (b) 路 ⇒ C3 绿** ★ (★代价: 按动力度 3N → 1.5N★) | ★**老板 (选型代价)** ★ |
| K3 | ★**`D_LED_G` 落位** ★ | `D_LED_G` 在靶内桶, 目标 `lib:name` 与几何本单已给全 (★ fab 外框 2.70×1.60 → 2.00×1.20 mm, 中心距 2.300 → 1.875 mm ⇒ land 要重画★) | ★**落位 (装在哪、朝哪边) 是结构与外观的事, 不是封装真值的事** ★ ⇒ 本单只给封装与几何 | ★**老板 / 结构总工** ★ |
| K4 | ★**`C_VBUS_GND` 的 2 个多余焊盘** ★ | C1 基线的「多余 2」就是它; ★**它的 BOM `dnp=DNP` · `board=镜框充电板` ⇒ 不在 90 件清单里, 也不进 C4 的 MAIN_PCB 口径** ★ | ★**沙盒 S3/S4 实测: 做完腿 A + 腿 B 它仍然是 C1 的「多 2」** ★ ⇒ ★**⇒ 要清掉它只能靠「留位 / 下板」的拍板, 不在 S10 这一趟的射程内** ★ | ★**老板 (B 类)** ★ |
| K5 | ★**`FB_DEMO` 没人排** ★ | 那一趟的两份文件里命中数 0/0 | ★**§5.1 已给并入建议 + 机器判据 (两份文件命中数都须 ≥ 1)** ★ | ★**main** ★ |
| K6 | ★**`CHG_GND_STAR` 基线页那一格自相矛盾** ★ | 一格写「官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘」, 同页正文写「1 个 land 是对的」 | ★**官方 `TestPoint_Pad_D1.0mm` 实测只有 1 个焊盘** ★ ⇒ ★**§5.2 已给订正建议 + 机器判据** ★ | ★**main (基线页签收方)** ★ |
| K7 | ★**90 件的料号 (OPN) 不是本单的活** ★ | 13 件里 `CHG_GND_STAR` + 5 只按键 的 BOM `opn` 栏是 `[0数据]`; 其余 7 件已有具体型号; 靶内 77 件的 BOM opn 栏多为空 | ★**封装的判定 (库文件在盘 + md5 + 焊盘数 + 几何) 本单全部给全; 哪颗料是选型批次的事** ★ | ★**无阻塞 (落表批次按本单目标 `lib:name` 回填同封装等效件)** ★ |

## §8 沙盒可达性证明 (★C4 从 158 变到多少 · 腿 A / 腿 B 各自的贡献 · 能不能到 68★)

★**沙盒一律落项目盘 `tmp/iss364_sbx/`** ★ (★**不许写 /tmp**: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)。

| 轮次 | 板 | 网表 | ★**C4**★ | ΔC4 | C1 失败项 | C2 失败项 | C3 失败项 |
|---|---|---|---|---|---|---|---|
| S0 基线 | 真板 | 真表 | ★**158**★ | 0 | C1 焊盘级不等价 (缺0/多2/错3/非法NC0) | — | — |
| S1 腿A单独 | 板副本 (90 件换官方 land) | 真表 | ★**158**★ | 0 | C1 焊盘级不等价 (缺0/多6/错2/非法NC0) | — | C3 焊盘数不符 7 个 |
| S2 腿B单独 | 真板 | 网表副本 (200 条具名指令) | ★**68**★ | ★**-90**★ | C1 焊盘级不等价 (缺4/多2/错5/非法NC0) | C2 针号/针数不符 4 个: ['C_KEY_PWR', 'C_KEY_VM', 'C_KEY_VP', 'R_BAT_DET_2'] | C3 焊盘数不符 4 个 |
| S3 腿A+腿B | 板副本 (90 件换官方 land) | 网表副本 (200 条具名指令) | ★**68**★ | ★**-90**★ | C1 焊盘级不等价 (缺0/多2/错0/非法NC0) | — | C3 焊盘数不符 3 个 |
| S4 腿A+腿B·K3走(b) | 板副本 (87 件换官方 land, 3 只按键不换) | 网表副本 | ★**68**★ | ★**-90**★ | C1 焊盘级不等价 (缺0/多2/错0/非法NC0) | — | — |

★**结论 (★逐条回答派活书的要求★)**:

1. ★**C4 从 158 变到 68** ★ ⇒ ★**目标 68 是【可达】的** ★ —— ★**实测值就是 68, 不是估的** ★。
2. ★**腿 A (换官方 land) 贡献 ΔC4 = +0** ★ ⇒ ★**零** ★ ⇒ ★**换 land 动不了 C4** ★ (★机制: C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自网表, 板在它之后才被读★)。
3. ★**腿 B (网表节点具名) 贡献 ΔC4 = -90** ★ ⇒ ★**它就是那条唯一有效的杠杆** ★。
4. ★**两条腿缺一不可, 但作用点不同** ★ —— ★**腿 A 不做 ⇒ C1 错 2 (`R_PU_PG`/`Q_PG` 的 pad↔net) 和 C3 错 7 (4 件 1→2 land + 3 只按键 2→4 land); 腿 B 不做 ⇒ C1 错 5 + C2/C3 错 4** ★ ⇒ ★**⇒ 那条「须【换官方 land 90 件 + 网表节点具名 90 件】」的验收条件, 两条腿缺一都交不出绿板** ★。
5. ★**做完之后还剩什么 (★差在哪、为什么★)** ★ —— ★**C1 只剩「多 2」, 就是 `C_VBUS_GND` 的 2 个充电板侧焊盘** ★ (★K4: 它 `dnp=DNP` · `board=镜框充电板` ⇒ 不在 90 件清单里, 也不进 C4 的 MAIN_PCB 口径 ⇒ ★**换 land 与具名脚都够不着它**★ ⇒ ★**要清掉只能靠「留位 / 下板」的拍板**★)** ★ ⇒ ★**其余 (缺 0 / 同号异网 0) 全绿** ★。

★**沙盒留证路径**: `tmp/iss364_sbx/board_legA.kicad_pcb` · `tmp/iss364_sbx/board_legA_k3b.kicad_pcb` · `tmp/iss364_sbx/netlist_v1_legB.csv` · `logs/iss364/20_sandbox_readings.json` · `logs/iss364/21_sandbox_bodies.txt`

## §9 复跑命令 + 本单的边界

```bash
# ① 本单生成器 (重算页面里每个数字)
python3 logs/iss364/build_iss364_data.py
python3 logs/iss364/analyze_legB.py
python3 logs/iss364/build_land_swap_workpacket.py
# ② 沙盒可达性证明 (★必须带 KiCad python★)
bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py
# ③ 本单机器闸 (正常跑 / 反向用例自证)
python3 HW/check_fp_truth_land_swap.py
python3 HW/check_fp_truth_land_swap.py --selftest
# ④ 既有闸复跑 (一个字节没改)
python3 HW/check_fp_truth_baseline.py
python3 HW/check_fp_truth_coverage_gap.py
python3 HW/check_onepass_preflight_coverage.py
python3 HW/check_onepass_s10_manifest.py
# ⑤ C4 的原始读数 (★必须带 KiCad python·裸 python3 会 ModuleNotFoundError: pcbnew★)
bash state/pcbnew_py.sh state/check_pcb_nets.py
# ⑥ 板/网表/脚表/BOM 的 md5 复核
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**本单的边界 (逐条, 不越界)**: ① ★**零写板** ★ (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 开工前后逐字节未变; 本单唯一动过板的动作是**在 `tmp/iss364_sbx/` 的副本上**做沙盒实验); ② ★**零落表** ★ (网表/脚表/BOM/原理图一字未改; §2 的「目标节点串」是**给落表批次用的目标值**, 不是已落的值); ③ ★**零改既有闸** ★; ④ ★**零改既有页面正文** ★ (§3/§4/§5 的改动全是**建议**, 落在本单自己的页里); ⑤ ★**零外发 / 零采购 / 零联系供应商** ★; ⑥ ★**不替老板拍板** ★ (K1/K2 只登记代价); ⑦ ★**零挂链** ★ (新闸交脚本但不挂进 `state/gate_check.py`); ⑧ ★**证据分级必标** ★ (五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`)。

