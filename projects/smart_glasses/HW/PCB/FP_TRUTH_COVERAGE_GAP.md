# HW/PCB · ISS-361 · 「板那一趟」封装真值覆盖缺口 (C4-158 与 ISS-356-100 的机器可读差集)

> ★**单号**: ISS-361 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯分析 / 文档 / 机器闸 · ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 零采购 · 不代老板拍板**★
> ★**本单只做 1 件**: 把「板上占位脚号器件」与「已有封装真值基线」这两个集合之间的缺口查清, 做成【一页 + 一条机器闸】, 让那一趟的封装收口判据从【一句话】变成【可数 · 可点名 · 可机器判】★
> ★**本页所有数字均由生成器 `logs/iss361/build_fp_truth_coverage_gap.py` 从真源实算生成★ ⇒ 零转述误差; 复跑命令见 §0 表每行的「怎么复跑」栏。
> ★**配套机器闸**: `HW/check_fp_truth_coverage_gap.py` (G0~G7 + `--selftest` 反向用例) · ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS361_封装真值覆盖缺口.md`

<!-- BEGIN ISS361 封装真值覆盖缺口基准块 -->
```json
{
 "issue": "ISS-361",
 "owner": "hw-lead",
 "doc": "HW/PCB/FP_TRUTH_COVERAGE_GAP.md",
 "gate": "HW/check_fp_truth_coverage_gap.py",
 "note": "★本块由 logs/iss361/build_fp_truth_coverage_gap.py 从真源实算生成; 闸 G0 校验它是合法 JSON, G1 校验 counts 与脚本实算逐项相等★",
 "counts": {
  "c4_total": 158,
  "iss356_total": 100,
  "iss356_main_board": 78,
  "iss356_charge_board": 22,
  "inter_total": 77,
  "diff_total": 81,
  "gap_total": 13,
  "board_footprints": 186
 },
 "buckets": {
  "tp": 42,
  "dnp": 26,
  "in_target": 77,
  "gap": 13
 },
 "gap_refs": [
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
<!-- END ISS361 封装真值覆盖缺口基准块 -->

## §0 口径与读数 (本机实跑, 2026-11-23)

★**三个口径各写清「哪个脚本产出 · 怎么复跑」★。★**每行数字都能被本表某一行的命令复现**★ —— 不用任何 agent 的转述。

| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |
|---|---|---|---|---|
| 1 | ISS-356 封装真值基线的靶子 | ★**100**★ (镜脚主 PCB 78 + 镜框充电板 22) | `HW/check_fp_truth_baseline.py` 的 `load_targets()`: 必装 ∩ 非 NET/TP ∩ `footprint=='待定'` | `python3 HW/check_fp_truth_baseline.py` |
| 2 | 板上占位脚号器件 (C4) | ★**158**★ | `state/check_pcb_nets.py` 的 C4 口径: 网表节点串是 **bare** (无 `pin<N>` / 无 USB-IF 物理脚名) ⇒ 焊盘号按行序占位 | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |
| 3 | C4 ∩ ISS-356 靶子 | ★**77**★ | 两集合求交 (本单生成器 `logs/iss361/build_fp_truth_coverage_gap.py`) | `python3 logs/iss361/build_fp_truth_coverage_gap.py` (重跑即重算) |
| 4 | C4 − ISS-356 靶子 | ★**81**★ | 差集 (同上) | 同上 |
| 5 | ★那 81 件的成分 (逐件归因)★ | ★**TP 42 + DNP 26 + 缺口 13**★ | ★**分桶优先级: TP 优先**★ (⇒ `TP_BAT`/`TP_LED_B` 两件 `dnp=DNP` 但 `type=TP` ⇒ 归 TP 桶); DNP 次之; 其余归缺口桶 | 同上 |
| 6 | ★那 13 件的 BOM `footprint` 栏长什么样★ | ★**不是 `待定`, 而是描述串**★ (★实测 20 行是 `★板文件封装: N 焊盘 (…)`★, 其中恰好 13 行落在「必装 ∩ 非 NET/TP」口径内 ⇒ **就是本单那 13 件**) | 读 `HW/BOM_v1.csv` 的 `footprint` 栏 | `python3 -c "import csv;print([r['footprint'] for r in csv.DictReader(open('HW/BOM_v1.csv',encoding='utf-8')) if r['footprint'].startswith('★板文件封装:')])" |
| 7 | ★那 13 件在 `HW/FP_TRUTH_BASELINE.md` 里有没有目标 `lib:name`★ | ★**12 件没有 / 1 件有**★ (`CHG_GND_STAR` 有 `TestPoint:TestPoint_Pad_D1.0mm`, 在 §2.2 靶外同族登记里) | 读 `HW/FP_TRUTH_BASELINE.md` 逐件搜 `lib:name` | `grep -n 'CHG_GND_STAR' HW/FP_TRUTH_BASELINE.md` |
| 8 | 板面封装库名的真实状态 | ★**186 个封装 · `GetFPIDAsString()` 唯一值 = `''`**★ ⇒ 板是【自绘通用占位】, 不是「库名写错」 | `bash state/pcbnew_py.sh -c "…GetFPIDAsString()…"` | 同左 (KiCad python; 纯文本口径见 `logs/iss361/zz_board_probe.py`) |
| 9 | ★ISS-354 §V-3 的 5 个 ref 与本单 13 件的关系★ | ★**零重叠**★ (`Q1`/`Q2`/`U_BATPROT`/`U_LDO_S28`/`U_SUPV` 全 `dnp='DNP'` 且全不在 C4-158 里) ⇒ **ISS-354 与 ISS-356 两套名单都不覆盖这 13 件**★ | 两集合求交 | `python3 logs/iss361/zz_parse.py` |
| 10 | ★有没有任何一道闸查「BOM `footprint` 栏 vs 板面封装」的一致性★ | ★**没有**★ ⇒ `state/check_pcb_nets.py` 里 `footprint` 出现 ★**0**★ 次; `HW/check_netlist_selfconsistency.py` 只查**个别 ref** 的板面属性 (`d3_board_value`/`d4_esd_pads`/`d4_esd_pad1_net`…) ⇒ ★**那 13 件没有任何一件被现有闸覆盖**★ | `grep -c footprint state/check_pcb_nets.py` → 0 | 同左 |
| 11 | ★C4-158 里脚数 ≥3 的 (脚号顺序真会出事的)★ | ★**4 件**: `Q_AND`(3) · `Q_ENVC`(3) · `Q_PG`(3) · `X1`(3·DNP) ⇒ ★**其中 3 件落在本单的缺口 13 件里**★ (前 3 件正是 B10/B11/B12 三条 P0 land 改项), `X1` 归 DNP 桶 | 读 `HW/netlist_v1_pins.csv` 逐 ref 数脚 | `python3 logs/iss361/zz_netstyle.py` |
| 12 | ★**【本单新增】C4 的计数由【网表节点命名】决定, 与板面 land 无关**★ | ★**沙盒实测**: 只把网表 5 个 bare 节点串改成具名 `pinN` ⇒ C4 从 ★**158 → 153**★ (掉 5 件); ★**板面 land 改动完全不进 C4 的计算输入**★ ⇒ ★**ISS-356 的 78 件 land 全部做完, C4 读数仍是 158**★ | ★C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自 `HW/netlist_v1.csv`, **板在它之后才被读**★ | `python3 logs/iss361/zz_c4_causality.py` (真网表零改动, 副本跑完即删) |
| 13 | ★**【本单新增】4 焊盘 gullwing 封装落 2 脚网表器件 ⇒ C3 当场红**★ | ★**沙盒实测**: 把 `SW_BOOT` 从 2 焊盘改成 4 焊盘后跑 `state/check_pcb_nets.py` ⇒ C3 判红「★ SW_BOOT: 板 4 脚 / 网表 2 脚 ★」⇒ ★**只改板不改网表 ⇒ 这道闸红**★ | 板副本落 `tmp/iss361/`, 跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py <副本>` | `python3 logs/iss361/zz_sandbox_4pad.py` + 上条命令 (真板 md5 未变) |
| 14 | ★**【本单新增】`FB_DEMO` 在那一趟的两份文件里 0 命中**★ | `WORKPACKET.md` 出现 ★**0**★ 次 · `PREFLIGHT.md` 出现 ★**0**★ 次 (其余 12 件都出现过) ⇒ ★**没人排它的 land 重画**★ ⇒ 见 §5 K4 | 逐件搜两个文件 | `grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_*.md` |

★**§0 的 14 行读数全部复现自同一批真源文件, 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 开工前后逐字节未变**★。

## §1 三集合的机器可读差集

★**三个集合**: ① `C4-158` 板上占位脚号器件 · ② `ISS356-100` 已有封装真值基线的靶子 · ③ `DIFF-81` 差集 (★**本单的对象**★)。

```
C4-158  (板上占位脚号器件)
  = 靶内 77  (C4 ∩ ISS356-100, ★已有 lib:name★)
  + TP   42  (type=='TP'       ⇒ ISS-356 口径显式排除)
  + DNP  26  (dnp=='DNP'       ⇒ ISS-356 口径显式排除)
  + 缺口 13  (★真器件 · 必装 · 非 NET/TP · footprint!='待定'★ ⇒ **被那一个条件挡在门外**)
  = 77 + 42 + 26 + 13 = ★158★

DIFF-81 = C4-158 − ISS356-100
  = TP 42 + DNP 26 + 缺口 13 = ★81★
```

★**`ISS356-100` 靶子名单的独立复核**: 本单生成器**独立读 `HW/FP_TRUTH_BASELINE.md` 的 §2 表 (78 行) 与 §4.1 表 (22 行)** ⇒ 并集 100 件; ★**与 BOM 实算的 100 件逐件相等**★ (集合级相等, 不是只对个数)。

### §1.1 `C4-158` 全名单 (ref + 归属桶 + 占位脚数)

| # | ref | 归属桶 | 占位脚数 |
|---|---|---|---|
| 1 | `BT_432243` | DNP | 2 |
| 2 | `C_BULK_LIGHT_1V8` | DNP | 2 |
| 3 | `C_BULK_SENSOR_AVDD` | DNP | 2 |
| 4 | `C_BULK_SENSOR_CORE` | DNP | 2 |
| 5 | `C_BULK_SENSOR_VDD_IO` | DNP | 2 |
| 6 | `C_BULK_V_CORE` | DNP | 2 |
| 7 | `C_BULK_V_SOC_IO` | DNP | 2 |
| 8 | `C_HF_LIGHT_1V8` | DNP | 2 |
| 9 | `C_HF_SENSOR_AVDD` | DNP | 2 |
| 10 | `C_HF_SENSOR_CORE` | DNP | 2 |
| 11 | `C_HF_SENSOR_VDD_IO` | DNP | 2 |
| 12 | `C_HF_V_CORE` | DNP | 2 |
| 13 | `C_HF_V_SOC_IO` | DNP | 2 |
| 14 | `C_KEY_CAM` | DNP | 1 |
| 15 | `C_SUPV` | DNP | 2 |
| 16 | `C_XTAL_IN` | DNP | 2 |
| 17 | `C_XTAL_OUT` | DNP | 2 |
| 18 | `D_ESD_LIGHT` | DNP | 2 |
| 19 | `D_LED_B` | DNP | 2 |
| 20 | `R_ID_JMP0` | DNP | 2 |
| 21 | `R_ID_JMP1` | DNP | 2 |
| 22 | `R_LED_B` | DNP | 2 |
| 23 | `R_NTC_BAT` | DNP | 1 |
| 24 | `R_TS_PULL` | DNP | 2 |
| 25 | `SW_KEY_CAM` | DNP | 2 |
| 26 | `X1` | DNP | 3 |
| 27 | `TP_BAT` | TP | 1 |
| 28 | `TP_BAT_CHG` | TP | 1 |
| 29 | `TP_BOOT` | TP | 1 |
| 30 | `TP_CSI_CK_N` | TP | 1 |
| 31 | `TP_CSI_CK_P` | TP | 1 |
| 32 | `TP_CSI_D0_N` | TP | 1 |
| 33 | `TP_CSI_D0_P` | TP | 1 |
| 34 | `TP_DSI_CK_N` | TP | 1 |
| 35 | `TP_DSI_CK_P` | TP | 1 |
| 36 | `TP_DSI_D0_N` | TP | 1 |
| 37 | `TP_DSI_D0_P` | TP | 1 |
| 38 | `TP_DSI_D1_N` | TP | 1 |
| 39 | `TP_DSI_D1_P` | TP | 1 |
| 40 | `TP_DSI_D2_N` | TP | 1 |
| 41 | `TP_DSI_D2_P` | TP | 1 |
| 42 | `TP_DSI_D3_N` | TP | 1 |
| 43 | `TP_DSI_D3_P` | TP | 1 |
| 44 | `TP_FSIN` | TP | 1 |
| 45 | `TP_I2CA_SCL` | TP | 1 |
| 46 | `TP_I2CA_SDA` | TP | 1 |
| 47 | `TP_I2CB_SCL` | TP | 1 |
| 48 | `TP_I2CB_SDA` | TP | 1 |
| 49 | `TP_ID` | TP | 1 |
| 50 | `TP_JTAG` | TP | 1 |
| 51 | `TP_KEY_PWR` | TP | 1 |
| 52 | `TP_KEY_VM` | TP | 1 |
| 53 | `TP_KEY_VP` | TP | 1 |
| 54 | `TP_LED_B` | TP | 1 |
| 55 | `TP_LED_G` | TP | 1 |
| 56 | `TP_LED_R` | TP | 1 |
| 57 | `TP_LIGHT_3V3` | TP | 1 |
| 58 | `TP_MCLK` | TP | 1 |
| 59 | `TP_PG` | TP | 1 |
| 60 | `TP_PG_VCORE` | TP | 1 |
| 61 | `TP_PG_VIO` | TP | 1 |
| 62 | `TP_RESET` | TP | 1 |
| 63 | `TP_SYS` | TP | 1 |
| 64 | `TP_UART` | TP | 1 |
| 65 | `TP_USB_D_N` | TP | 1 |
| 66 | `TP_USB_D_P` | TP | 1 |
| 67 | `TP_VCORE` | TP | 1 |
| 68 | `TP_VIO` | TP | 1 |
| 69 | `CHG_GND_STAR` | 缺口 | 1 |
| 70 | `D_ESD_CAM` | 缺口 | 2 |
| 71 | `D_ESD_DEMO` | 缺口 | 2 |
| 72 | `D_ESD_USB_D` | 缺口 | 2 |
| 73 | `FB_DEMO` | 缺口 | 2 |
| 74 | `Q_AND` | 缺口 | 3 |
| 75 | `Q_ENVC` | 缺口 | 3 |
| 76 | `Q_PG` | 缺口 | 3 |
| 77 | `SW_BOOT` | 缺口 | 2 |
| 78 | `SW_KEY_PWR` | 缺口 | 2 |
| 79 | `SW_KEY_VM` | 缺口 | 2 |
| 80 | `SW_KEY_VP` | 缺口 | 2 |
| 81 | `SW_RST` | 缺口 | 2 |
| 82 | `C_AC_CSI_D0_CK_N` | 靶内 | 2 |
| 83 | `C_AC_CSI_D0_CK_P` | 靶内 | 2 |
| 84 | `C_AC_CSI_D0_D0_N` | 靶内 | 2 |
| 85 | `C_AC_CSI_D0_D0_P` | 靶内 | 2 |
| 86 | `C_AC_CSI_D0_D1_N` | 靶内 | 2 |
| 87 | `C_AC_CSI_D0_D1_P` | 靶内 | 2 |
| 88 | `C_AC_CSI_D0_D2_N` | 靶内 | 2 |
| 89 | `C_AC_CSI_D0_D2_P` | 靶内 | 2 |
| 90 | `C_AC_CSI_D0_D3_N` | 靶内 | 2 |
| 91 | `C_AC_CSI_D0_D3_P` | 靶内 | 2 |
| 92 | `C_BULK_LIGHT_3V3` | 靶内 | 2 |
| 93 | `C_BULK_VDD_1V8_IO` | 靶内 | 2 |
| 94 | `C_BULK_VDD_3V3_IO` | 靶内 | 2 |
| 95 | `C_DET_BAT` | 靶内 | 2 |
| 96 | `C_DET_VBUS_D` | 靶内 | 2 |
| 97 | `C_HF_LIGHT_3V3` | 靶内 | 2 |
| 98 | `C_HF_VDD_1V8_IO` | 靶内 | 2 |
| 99 | `C_HF_VDD_3V3_IO` | 靶内 | 2 |
| 100 | `C_KEY_PWR` | 靶内 | 1 |
| 101 | `C_KEY_VM` | 靶内 | 1 |
| 102 | `C_KEY_VP` | 靶内 | 1 |
| 103 | `C_RST` | 靶内 | 2 |
| 104 | `C_SW_IN` | 靶内 | 2 |
| 105 | `C_SW_OUT` | 靶内 | 2 |
| 106 | `C_TEMP` | 靶内 | 2 |
| 107 | `C_VBUS_DEMO` | 靶内 | 2 |
| 108 | `D_LED_G` | 靶内 | 2 |
| 109 | `D_LED_R` | 靶内 | 2 |
| 110 | `R_BAT_DET_1` | 靶内 | 2 |
| 111 | `R_BAT_DET_2` | 靶内 | 1 |
| 112 | `R_CC1_D` | 靶内 | 2 |
| 113 | `R_CC2_D` | 靶内 | 2 |
| 114 | `R_EN_VCORE` | 靶内 | 2 |
| 115 | `R_JTAG_TCK` | 靶内 | 2 |
| 116 | `R_JTAG_TDI` | 靶内 | 2 |
| 117 | `R_JTAG_TDO` | 靶内 | 2 |
| 118 | `R_JTAG_TMS` | 靶内 | 2 |
| 119 | `R_KEY_CAM` | 靶内 | 2 |
| 120 | `R_KEY_PWR` | 靶内 | 2 |
| 121 | `R_KEY_VM` | 靶内 | 2 |
| 122 | `R_KEY_VP` | 靶内 | 2 |
| 123 | `R_LED_G` | 靶内 | 2 |
| 124 | `R_LED_R` | 靶内 | 2 |
| 125 | `R_PD_ON` | 靶内 | 2 |
| 126 | `R_PG_PULL` | 靶内 | 2 |
| 127 | `R_PU_BOOT_N` | 靶内 | 2 |
| 128 | `R_PU_I2CA_SCL` | 靶内 | 2 |
| 129 | `R_PU_I2CA_SDA` | 靶内 | 2 |
| 130 | `R_PU_I2CB_SCL` | 靶内 | 2 |
| 131 | `R_PU_I2CB_SDA` | 靶内 | 2 |
| 132 | `R_PU_ID0` | 靶内 | 2 |
| 133 | `R_PU_ID1` | 靶内 | 2 |
| 134 | `R_PU_PG` | 靶内 | 2 |
| 135 | `R_PU_RESET_N` | 靶内 | 2 |
| 136 | `R_SEL_CK_N` | 靶内 | 2 |
| 137 | `R_SEL_CK_P` | 靶内 | 2 |
| 138 | `R_SEL_D0_N` | 靶内 | 2 |
| 139 | `R_SEL_D0_P` | 靶内 | 2 |
| 140 | `R_SEL_D1_N` | 靶内 | 2 |
| 141 | `R_SEL_D1_P` | 靶内 | 2 |
| 142 | `R_SEL_D2_N` | 靶内 | 2 |
| 143 | `R_SEL_D2_P` | 靶内 | 2 |
| 144 | `R_SEL_D3_N` | 靶内 | 2 |
| 145 | `R_SEL_D3_P` | 靶内 | 2 |
| 146 | `R_SER_CSI_MCLK` | 靶内 | 2 |
| 147 | `R_SER_FSIN` | 靶内 | 2 |
| 148 | `R_SER_RESET_N` | 靶内 | 2 |
| 149 | `R_SER_SPI_CSn` | 靶内 | 2 |
| 150 | `R_SER_SPI_MISO` | 靶内 | 2 |
| 151 | `R_SER_SPI_MOSI` | 靶内 | 2 |
| 152 | `R_SER_SPI_SCLK` | 靶内 | 2 |
| 153 | `R_SER_USB_D_N` | 靶内 | 2 |
| 154 | `R_SER_USB_D_P` | 靶内 | 2 |
| 155 | `R_SUPV_DIV1` | 靶内 | 2 |
| 156 | `R_SUPV_DIV2` | 靶内 | 2 |
| 157 | `R_VBUS_DET_D1` | 靶内 | 2 |
| 158 | `R_VBUS_DET_D2` | 靶内 | 2 |

### §1.2 `ISS356-100` 全名单 (ref + 板面归属)

| # | ref | 板面归属 | 在 C4 里? |
|---|---|---|---|
| 1 | `C_AC_CSI_D0_CK_N` | 镜脚主 PCB | ★是★ |
| 2 | `C_AC_CSI_D0_CK_P` | 镜脚主 PCB | ★是★ |
| 3 | `C_AC_CSI_D0_D0_N` | 镜脚主 PCB | ★是★ |
| 4 | `C_AC_CSI_D0_D0_P` | 镜脚主 PCB | ★是★ |
| 5 | `C_AC_CSI_D0_D1_N` | 镜脚主 PCB | ★是★ |
| 6 | `C_AC_CSI_D0_D1_P` | 镜脚主 PCB | ★是★ |
| 7 | `C_AC_CSI_D0_D2_N` | 镜脚主 PCB | ★是★ |
| 8 | `C_AC_CSI_D0_D2_P` | 镜脚主 PCB | ★是★ |
| 9 | `C_AC_CSI_D0_D3_N` | 镜脚主 PCB | ★是★ |
| 10 | `C_AC_CSI_D0_D3_P` | 镜脚主 PCB | ★是★ |
| 11 | `C_BAT` | 镜框充电板 | 否 |
| 12 | `C_BST` | 镜框充电板 | 否 |
| 13 | `C_BULK_LIGHT_3V3` | 镜脚主 PCB | ★是★ |
| 14 | `C_BULK_VDD_1V8_IO` | 镜脚主 PCB | ★是★ |
| 15 | `C_BULK_VDD_3V3_IO` | 镜脚主 PCB | ★是★ |
| 16 | `C_DET_BAT` | 镜脚主 PCB | ★是★ |
| 17 | `C_DET_VBUS_D` | 镜脚主 PCB | ★是★ |
| 18 | `C_HF_LIGHT_3V3` | 镜脚主 PCB | ★是★ |
| 19 | `C_HF_VDD_1V8_IO` | 镜脚主 PCB | ★是★ |
| 20 | `C_HF_VDD_3V3_IO` | 镜脚主 PCB | ★是★ |
| 21 | `C_KEY_PWR` | 镜脚主 PCB | ★是★ |
| 22 | `C_KEY_VM` | 镜脚主 PCB | ★是★ |
| 23 | `C_KEY_VP` | 镜脚主 PCB | ★是★ |
| 24 | `C_PMID` | 镜框充电板 | 否 |
| 25 | `C_RST` | 镜脚主 PCB | ★是★ |
| 26 | `C_SW_IN` | 镜脚主 PCB | ★是★ |
| 27 | `C_SW_OUT` | 镜脚主 PCB | ★是★ |
| 28 | `C_SYS` | 镜框充电板 | 否 |
| 29 | `C_TEMP` | 镜脚主 PCB | ★是★ |
| 30 | `C_VBUS_DEMO` | 镜脚主 PCB | ★是★ |
| 31 | `C_VBUS_IC` | 镜框充电板 | 否 |
| 32 | `D_CHG_LED` | 镜框充电板 | 否 |
| 33 | `D_ESD_TC` | 镜框充电板 | 否 |
| 34 | `D_LED_G` | 镜脚主 PCB | ★是★ |
| 35 | `D_LED_R` | 镜脚主 PCB | ★是★ |
| 36 | `D_TVS_VBUS` | 镜框充电板 | 否 |
| 37 | `FB_VBUS` | 镜框充电板 | 否 |
| 38 | `J_DEBUG` | 镜脚主 PCB | 否 |
| 39 | `L_CHG` | 镜框充电板 | 否 |
| 40 | `Q_CHG_LED` | 镜框充电板 | 否 |
| 41 | `R_BAT_DET_1` | 镜脚主 PCB | ★是★ |
| 42 | `R_BAT_DET_2` | 镜脚主 PCB | ★是★ |
| 43 | `R_CC1` | 镜框充电板 | 否 |
| 44 | `R_CC1_D` | 镜脚主 PCB | ★是★ |
| 45 | `R_CC2` | 镜框充电板 | 否 |
| 46 | `R_CC2_D` | 镜脚主 PCB | ★是★ |
| 47 | `R_CE` | 镜框充电板 | 否 |
| 48 | `R_CHG_LED` | 镜框充电板 | 否 |
| 49 | `R_EN_VCORE` | 镜脚主 PCB | ★是★ |
| 50 | `R_ILIM` | 镜框充电板 | 否 |
| 51 | `R_JTAG_TCK` | 镜脚主 PCB | ★是★ |
| 52 | `R_JTAG_TDI` | 镜脚主 PCB | ★是★ |
| 53 | `R_JTAG_TDO` | 镜脚主 PCB | ★是★ |
| 54 | `R_JTAG_TMS` | 镜脚主 PCB | ★是★ |
| 55 | `R_KEY_CAM` | 镜脚主 PCB | ★是★ |
| 56 | `R_KEY_PWR` | 镜脚主 PCB | ★是★ |
| 57 | `R_KEY_VM` | 镜脚主 PCB | ★是★ |
| 58 | `R_KEY_VP` | 镜脚主 PCB | ★是★ |
| 59 | `R_LED_G` | 镜脚主 PCB | ★是★ |
| 60 | `R_LED_R` | 镜脚主 PCB | ★是★ |
| 61 | `R_OTG` | 镜框充电板 | 否 |
| 62 | `R_PD_ON` | 镜脚主 PCB | ★是★ |
| 63 | `R_PG_PULL` | 镜脚主 PCB | ★是★ |
| 64 | `R_PSEL` | 镜框充电板 | 否 |
| 65 | `R_PU_BOOT_N` | 镜脚主 PCB | ★是★ |
| 66 | `R_PU_CHG_STAT` | 镜框充电板 | 否 |
| 67 | `R_PU_I2CA_SCL` | 镜脚主 PCB | ★是★ |
| 68 | `R_PU_I2CA_SDA` | 镜脚主 PCB | ★是★ |
| 69 | `R_PU_I2CB_SCL` | 镜脚主 PCB | ★是★ |
| 70 | `R_PU_I2CB_SDA` | 镜脚主 PCB | ★是★ |
| 71 | `R_PU_ID0` | 镜脚主 PCB | ★是★ |
| 72 | `R_PU_ID1` | 镜脚主 PCB | ★是★ |
| 73 | `R_PU_PG` | 镜脚主 PCB | ★是★ |
| 74 | `R_PU_RESET_N` | 镜脚主 PCB | ★是★ |
| 75 | `R_PU_SCL` | 镜框充电板 | 否 |
| 76 | `R_PU_SDA` | 镜框充电板 | 否 |
| 77 | `R_SEL_CK_N` | 镜脚主 PCB | ★是★ |
| 78 | `R_SEL_CK_P` | 镜脚主 PCB | ★是★ |
| 79 | `R_SEL_D0_N` | 镜脚主 PCB | ★是★ |
| 80 | `R_SEL_D0_P` | 镜脚主 PCB | ★是★ |
| 81 | `R_SEL_D1_N` | 镜脚主 PCB | ★是★ |
| 82 | `R_SEL_D1_P` | 镜脚主 PCB | ★是★ |
| 83 | `R_SEL_D2_N` | 镜脚主 PCB | ★是★ |
| 84 | `R_SEL_D2_P` | 镜脚主 PCB | ★是★ |
| 85 | `R_SEL_D3_N` | 镜脚主 PCB | ★是★ |
| 86 | `R_SEL_D3_P` | 镜脚主 PCB | ★是★ |
| 87 | `R_SER_CSI_MCLK` | 镜脚主 PCB | ★是★ |
| 88 | `R_SER_FSIN` | 镜脚主 PCB | ★是★ |
| 89 | `R_SER_RESET_N` | 镜脚主 PCB | ★是★ |
| 90 | `R_SER_SPI_CSn` | 镜脚主 PCB | ★是★ |
| 91 | `R_SER_SPI_MISO` | 镜脚主 PCB | ★是★ |
| 92 | `R_SER_SPI_MOSI` | 镜脚主 PCB | ★是★ |
| 93 | `R_SER_SPI_SCLK` | 镜脚主 PCB | ★是★ |
| 94 | `R_SER_USB_D_N` | 镜脚主 PCB | ★是★ |
| 95 | `R_SER_USB_D_P` | 镜脚主 PCB | ★是★ |
| 96 | `R_STAR_PGND` | 镜框充电板 | 否 |
| 97 | `R_SUPV_DIV1` | 镜脚主 PCB | ★是★ |
| 98 | `R_SUPV_DIV2` | 镜脚主 PCB | ★是★ |
| 99 | `R_VBUS_DET_D1` | 镜脚主 PCB | ★是★ |
| 100 | `R_VBUS_DET_D2` | 镜脚主 PCB | ★是★ |

### §1.3 `DIFF-81` 全名单 (ref + 归因)

| # | ref | 归属桶 | 被 ISS-356 口径排除的原因 (逐件归因) |
|---|---|---|---|
| 1 | `BT_432243` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 2 | `CHG_GND_STAR` | 缺口 | ★`dnp=='必装'` + `type=='CONN'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 3 | `C_BULK_LIGHT_1V8` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 4 | `C_BULK_SENSOR_AVDD` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 5 | `C_BULK_SENSOR_CORE` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 6 | `C_BULK_SENSOR_VDD_IO` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 7 | `C_BULK_V_CORE` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 8 | `C_BULK_V_SOC_IO` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 9 | `C_HF_LIGHT_1V8` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 10 | `C_HF_SENSOR_AVDD` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 11 | `C_HF_SENSOR_CORE` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 12 | `C_HF_SENSOR_VDD_IO` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 13 | `C_HF_V_CORE` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 14 | `C_HF_V_SOC_IO` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 15 | `C_KEY_CAM` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 16 | `C_SUPV` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 17 | `C_XTAL_IN` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 18 | `C_XTAL_OUT` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 19 | `D_ESD_CAM` | 缺口 | ★`dnp=='必装'` + `type=='D'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 20 | `D_ESD_DEMO` | 缺口 | ★`dnp=='必装'` + `type=='D'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 21 | `D_ESD_LIGHT` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 22 | `D_ESD_USB_D` | 缺口 | ★`dnp=='必装'` + `type=='D'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 23 | `D_LED_B` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 24 | `FB_DEMO` | 缺口 | ★`dnp=='必装'` + `type=='L'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 25 | `Q_AND` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 26 | `Q_ENVC` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 27 | `Q_PG` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 28 | `R_ID_JMP0` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 29 | `R_ID_JMP1` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 30 | `R_LED_B` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 31 | `R_NTC_BAT` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 32 | `R_TS_PULL` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 33 | `SW_BOOT` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 34 | `SW_KEY_CAM` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |
| 35 | `SW_KEY_PWR` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 36 | `SW_KEY_VM` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 37 | `SW_KEY_VP` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 38 | `SW_RST` | 缺口 | ★`dnp=='必装'` + `type=='SW'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ ★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象 |
| 39 | `TP_BAT` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 40 | `TP_BAT_CHG` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 41 | `TP_BOOT` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 42 | `TP_CSI_CK_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 43 | `TP_CSI_CK_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 44 | `TP_CSI_D0_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 45 | `TP_CSI_D0_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 46 | `TP_DSI_CK_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 47 | `TP_DSI_CK_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 48 | `TP_DSI_D0_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 49 | `TP_DSI_D0_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 50 | `TP_DSI_D1_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 51 | `TP_DSI_D1_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 52 | `TP_DSI_D2_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 53 | `TP_DSI_D2_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 54 | `TP_DSI_D3_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 55 | `TP_DSI_D3_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 56 | `TP_FSIN` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 57 | `TP_I2CA_SCL` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 58 | `TP_I2CA_SDA` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 59 | `TP_I2CB_SCL` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 60 | `TP_I2CB_SDA` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 61 | `TP_ID` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 62 | `TP_JTAG` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 63 | `TP_KEY_PWR` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 64 | `TP_KEY_VM` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 65 | `TP_KEY_VP` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 66 | `TP_LED_B` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 67 | `TP_LED_G` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 68 | `TP_LED_R` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 69 | `TP_LIGHT_3V3` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 70 | `TP_MCLK` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 71 | `TP_PG` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 72 | `TP_PG_VCORE` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 73 | `TP_PG_VIO` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 74 | `TP_RESET` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 75 | `TP_SYS` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 76 | `TP_UART` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 77 | `TP_USB_D_N` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 78 | `TP_USB_D_P` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 79 | `TP_VCORE` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 80 | `TP_VIO` | TP | ★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点 |
| 81 | `X1` | DNP | ★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件 |

## §2 ★那 13 件逐件表 (全部字段齐全)

★**字段口径照 `HW/FP_TRUTH_BASELINE.md` §2 那张表同款** ★ (ref / type / value / 必装-DNP / 现占位族 / 目标 `lib:name` / 库文件实存路径 + md5 / 焊盘数-网络核对结论 / 候选 OPN / 证据等级 / 是否触发布局布线改动 / 降级方案)。★**13 件全部逐件写全, 无一件省略**★。

| ref | type | value | 必装/DNP | 现占位族 (板面实测) | 目标 `lib:name` | 库文件实存路径 + md5 | 焊盘数 / 网络核对结论 (实测) | 候选 OPN | 证据等级 | 是否触发布局/布线改动 | 降级方案 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `CHG_GND_STAR` | CONN | 单点汇流位 | 必装 | 1 焊盘 (1) · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 0.000 mm | `TestPoint:TestPoint_Pad_D1.0mm` | `TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` md5 `cea8eb3ba9b799767624661848b00243` | 焊盘数 1=1 一致; 1=GND | [0数据] · 非器件 (单点汇流位, 1 脚 GND) ⇒ 无型号可填, 按本行目标 lib:name 回填同封装件 | [实测] · [0数据] | ★是★ · pad 形状/尺寸变 (0.600×0.900 矩形 → 1.000 圆形) ⇒ 该 land 重定义; ★**只有 1 个 land, 不新增第 2 个**★ (网表只有 1 脚 GND ⇒ 见 §5 K1) | 若落表批次要把它当可拆件 ⇒ 改用 2 焊盘件 (例 `Diode_SMD:D_SOD-323` md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = 新增第 2 脚 + 网表加 GND 以外的第二个网 ⇒ 与单点汇流位的功能定义冲突 ⇒ 不建议 |
| `D_ESD_CAM` | D | TPD1E05U06DPYR | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2=2 一致; 1=GND / 2=CSI_D0_CK_P | TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4) | [实测] · [官网] | ★是 (强制)★ · ① 中心距 2.300 → 0.700 mm, pad 0.600×0.900 → 0.300×0.500 ⇒ 整块 land 重画; ② ★**pad 序与器件相反**: 板 pad1=GND/pad2=CSI_D0_CK_P, 而 TPD1E05U06DPYR 是 1=I/O 2=GND ⇒ 必须把 pad1/pad2 的网对调 (= 那一趟 B13_ESD_CAM_PAD 的内容) | 若 TI X1SON-2 封装在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 无第二档 ⇒ 改用 2 脚 SOD-323 单通道件 `Diode_SMD:D_SOD-323` (md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = Cd 0.42pF → 45pF ⇒ CSI-2 高速线上不可用 (Cd 45pF 会吃掉眼图裕量) ⇒ 不建议 |
| `D_ESD_DEMO` | D | PESD5V0S1BA | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Diode_SMD:D_SOD-323` | `Diode_SMD.pretty/D_SOD-323.kicad_mod` md5 `bce0278c9b9af83e2de3cd130e6c04ed` | 焊盘数 2=2 一致; 1=RAIL_DEMO_5V / 2=GND | PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV) | [实测] · [官网] | ★是 (强制)★ · 中心距 2.300 → 2.100 mm, pad 0.600×0.900 → 0.600×0.450 ⇒ land 重画; ★pad 序无须对调★ (PESD5V0S1BA 是双向件, 1/2 谁接信号谁接地皆可) | 若 SOD-323 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Diode_SMD:D_SOD-323F` (SOD-323 带引脚变体) ⇒ 代价 = 焊接方式变 ⇒ 钢网要改 ⇒ 不建议; 或改小封装 `Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm` (md5 `c57a4058f16cf35599c2b748b9434350`) ⇒ 代价 = 手工贴装 + 板面更挤 ⇒ 不建议 |
| `D_ESD_USB_D` | D | TPD1E05U06DPYR | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 2.70×1.60 mm · 中心距 2.300 mm | `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` | `Package_SON.pretty/Texas_DPY0002A_0.6x1mm_P0.65mm.kicad_mod` md5 `0edfa97bd7bd277f3c05acf2bee23892` | 焊盘数 2=2 一致; 1=NET_USB_D_P_TYPEC / 2=GND | [0数据] · ★现行 BOM opn 是 2 脚 TPD1E05U06DPYR, 但那一趟 B07 要求它变 3 脚 ⇒ 最终型号/封装随 W-1/W-2 拍板而变 ⇒ 本栏的 lib:name 只代表【现行 BOM opn 那一档】 | [实测] · [0数据] | ★是 (强制)★ · ① 中心距 2.300 → 0.700 mm ⇒ land 重画; ② ★**还要把 2 个 land 变 3 个** (那一趟 B07_ESD_USB_D_3PIN) ⇒ 网表 + 板面同改; ③ ★**还要挪位**: 距 J_USB_C 现 47.99 mm ⇒ 目标 ≤3.0 mm (B08_ESD_USB_D_NEAR) ⇒ 布线要重跑; ④ 网名 NET_USB_D_P_TYPEC 三处同步 (B32) | ★3 脚档的候选封装随 W-1/W-2 分叉★ ⇒ 若拍「一颗双通道 3 脚」⇒ 候选 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`, 3 焊盘) ⇒ 代价 = ★**pad 序须按最终型号厂商 land 复核**★ (本栏 SOT-23-3 只是几何候选, 不是代拍); 若拍「两颗单通道」⇒ 本行保持 2 脚 X1SON-2 + 另加一只 2 脚件 (D− 侧) ⇒ 代价 = 板上多一颗件 + 两处 land 都要画 ⇒ 仍在本趟内可完成 |
| `FB_DEMO` | L | BLM21PG221SN1D | 必装 | 2 焊盘 (1/2) · 0.550×0.900 mm · fab 外框 2.00×1.60 mm · 中心距 1.000 mm | `Inductor_SMD:L_0805_2012Metric` | `Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod` md5 `4e67ede5911eab38accb2ef9e57de79c` | 焊盘数 2=2 一致; 1=RAIL_DEMO_5V / 2=GND | BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max) | [实测] · [官网] | ★是 (强制)★ · ★**占位是斜置 2 land (对角 1.000 mm), 官方 0805 是正置 @2.124 mm**★ ⇒ 位置 + 朝向 + pad 尺寸 (0.550×0.900 → 0.875×1.200) 全变 ⇒ land 重画 ⇒ 两端走线端点要重接 | 若 Murata 0805 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Inductor_SMD:L_0805_2012Metric` 唯一档 ⇒ 改用更小 0603 (如 `Inductor_SMD:L_0603_1608Metric`) ⇒ 代价 = 电流 2A 降额到 1A 级 (BLM21PG 2000mA 是选型硬判据) ⇒ 不建议 |
| `Q_AND` | SW | AO3400A | 必装 | 3 焊盘 (1/2/3) · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3=3 一致; 1=RESET_N / 2=GND / 3=PG_AND | AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V) | [实测] · [官网] | ★是 (强制)★ · ★**几何全变 + 脚序反**★: 占位 3 land 是 L 形 (pad1/pad2 水平相邻 @1.270 mm, pad3 斜置 @4.883 mm), 官方 SOT-23 是 pad1/pad2 上下相邻 @1.900 mm + pad3 对侧 @1.876 mm ⇒ 三个 land 全部重定位; ★★且 pad↔net 须对调★★ (板 pad1=RESET_N=漏极 D / pad2=GND=源极 S / pad3=PG_AND=栅极 G, 而 AO3400A 官方脚序是 1=G / 2=S / 3=D) ⇒ ★**不改 ⇒ AND 门不成立**★ (= 那一趟 B10_Q_AND_LAND 的内容) | 若 SOT-23 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_TO_SOT_SMD:SOT-23` 唯一档 ⇒ 换 SOT-23 的 TO-236 变体 (`Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ ★**代价 = 厂商脚序可能不同, 必须逐颗重核 1=G/2=S/3=D**★ ⇒ 不省事, 不建议 |
| `Q_ENVC` | SW | AO3400A | 必装 | 3 焊盘 (1/2/3) · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3=3 一致; 1=PG_AND / 2=GND / 3=EN_VCORE | AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V) | [实测] · [官网] | ★是 (强制)★ · 几何全变 (占位 L 形 → 官方 SOT-23 上下+对侧) ⇒ 三个 land 全部重定位; ★pad↔net 无须对调★ (板 pad1=PG_AND=栅极 G / pad2=GND=源极 S / pad3=EN_VCORE=漏极 D = 官方 1=G / 2=S / 3=D ⇒ 天然对上, 是三件 MOS 里唯一不用换序的) | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `Q_PG` | SW | DMP3098L | 必装 | 3 焊盘 (1/2/3) · 0.600×0.900 mm · fab 外框 4.00×5.00 mm · 中心距 4.883 mm | `Package_TO_SOT_SMD:SOT-23` | `Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod` md5 `f8754f4dc2887bbe66484114fa63ee44` | 焊盘数 3=3 一致; 1=PWR_GOOD / 2=BAT_SW / 3=PWR_ON | DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA) | [实测] · [官网] | ★是 (强制)★ · 几何全变 (同 Q_AND) ⇒ 三个 land 全部重定位; ★pad↔net 无须对调★ (板 pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD, 而 DMP3098L 官方脚序 1=G / 2=S / 3=D ⇒ ⇒ 板面现接法是 G/S/D 反着接 ⇒ ★**必须改接线**: 板面 pad1(PWR_ON) 要变成 pad3(PWR_ON), 板面 pad3(PWR_GOOD) 要变成 pad1(PWR_GOOD)★ (= 那一趟 B11_Q_PG_LAND 的内容) | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `SW_BOOT` | SW | BOOT 按键 | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4=2 一致; 1=BOOT_N / 2=GND | KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) ★按 HW/PART_SELECTION_MATRIX_2026-11-16.md §⑮ 的 pick (BOOT 键误触后果最重 ⇒ 3N 档) | [实测] · [官网] | ★是 (强制)★ · ★**这是本单 13 件里唯一会改【焊盘个数】的一件**★: 占位 2 land @2.200 mm (0.600×0.900) ⇒ 官方 KMR2 是 ★**4 个物理焊盘 (焊盘号 1,1,2,2)**★ @4.100×2.600 mm (0.900×1.000) ⇒ 板面从 2 land 变 4 land ⇒ ★**网表也必须同步给 4 个具名脚, 否则 `state/check_pcb_nets.py` C3 判红「板 4 脚 / 网表 2 脚」**★ (沙盒已实测, 见 §0 表第 12 行) ⇒ 本单零落表 ⇒ 只登记 | ★若不改网表 ⇒ 只能选 2 land 的按键封装★ ⇒ 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` (md5 `749f20c5ab898069ade01682274c7bbf`, 2 焊盘 @3.400 mm, 本体 3.0×2.5mm) ⇒ 代价 = 按动力度 1.5N vs KMR2 的 3.0N ⇒ BOOT 键误触风险上升 (矩阵 §⑮ 选 3N 的理由就是防误触) ⇒ ★**这是选型代价, 不是本单能拍的**★; 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, C&K KXT3) ⇒ 代价 = 同上, 且本体 3.5×2.0 |
| `SW_KEY_PWR` | SW | 按键 | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4=2 一致; 1=KEY_PWR / 2=GND | KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) ★按矩阵 §⑯ 的 pick (电源键 ⇒ 误触 = 意外关机 ⇒ OF 偏大) | [实测] · [官网] | ★是 (强制)★ · 同 SW_BOOT: 2 land @2.200 mm ⇒ 官方 KMR2 4 个物理焊盘 (1,1,2,2) @4.100×2.600 mm ⇒ 板面 2 land 变 4 land ⇒ ★网表必须同步 4 个具名脚, 否则 C3 判红★ (沙盒已实测) | 同 SW_BOOT: 不改网表则只能选 2 land 封装 (`SW_SPST_B3U-1000P` md5 `749f20c5ab898069ade01682274c7bbf` / `SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 按动力度降到 1.5N ⇒ 电源键误触风险上升 ⇒ ★不代拍★ |
| `SW_KEY_VM` | SW | 按键 | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2=2 一致; 1=KEY_VOL_M / 2=GND | B3U-1000P (Omron B3U 2 脚 gullwing SMT 无固定脚无 boss · 本体 3.0×2.5mm · OF 1.5N · travel 0.2mm · 寿命 200,000 次) ★按矩阵 §⑰ 的 pick (音量键频繁按 ⇒ 寿命优先 + 短行程) | [实测] · [官网] | ★是 (强制)★ · 2 land ⇒ 仍是 2 land (★**焊盘个数不变 ⇒ C3 不受影响★**) 但中心距 2.200 → 3.400 mm、pad 0.600×0.900 → 0.900×1.700、fab 外框 3.00×3.00 → 3.00×2.50 mm ⇒ land 重画 + 两端走线端点要重接; ★注意 fab 外框 3.0mm 高仍放得进现占位 3.0×3.0★ | 若 B3U-1000P 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Button_Switch_SMD:SW_SPST_B3U-1000P` 唯一档 ⇒ 改 KXT3 (`Button_Switch_SMD:SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, 本体 3.5×2.0mm) ⇒ 代价 = 宽度 3.5 > 占位 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议 |
| `SW_KEY_VP` | SW | 按键 | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_SPST_B3U-1000P` | `Button_Switch_SMD.pretty/SW_SPST_B3U-1000P.kicad_mod` md5 `749f20c5ab898069ade01682274c7bbf` | 焊盘数 2=2 一致; 1=KEY_VOL_P / 2=GND | B3U-1000P (Omron B3U 2 脚 gullwing SMT 无固定脚无 boss · 本体 3.0×2.5mm · OF 1.5N · travel 0.2mm · 寿命 200,000 次) ★按矩阵 §⑱ 的 pick (与 SW_KEY_VM 同族同料 ⇒ 左右手感一致) | [实测] · [官网] | ★是 (强制)★ · 同 SW_KEY_VM: 2 land ⇒ 2 land (C3 不受影响), 中心距 2.200 → 3.400 mm ⇒ land 重画 | 同 SW_KEY_VM ⇒ 退到 KXT3 (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ 邻键间隙复核 ⇒ 不建议 |
| `SW_RST` | SW | 复位按键 | 必装 | 2 焊盘 (1/2) · 0.600×0.900 mm · fab 外框 3.00×3.00 mm · 中心距 2.200 mm | `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` | `Button_Switch_SMD.pretty/SW_Push_1P1T_NO_CK_KMR2.kicad_mod` md5 `460d6f7d3529096429408f78ed206fe7` | 焊盘数 4=2 一致; 1=RESET_N / 2=GND | KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) ★按矩阵 §⑲ 的 pick (复位键 ⇒ 误触 = 意外重启 ⇒ OF 偏大 + 段落感) | [实测] · [官网] | ★是 (强制)★ · 同 SW_BOOT: 2 land @2.200 mm ⇒ 官方 KMR2 4 个物理焊盘 (1,1,2,2) @4.100×2.600 mm ⇒ 板面 2 land 变 4 land ⇒ ★网表必须同步 4 个具名脚, 否则 C3 判红★ (沙盒已实测) | 同 SW_BOOT: 不改网表则只能选 2 land 封装 ⇒ 代价 = 按动力度降到 1.5N ⇒ 复位键误触风险上升 ⇒ ★不代拍★ |

★**「现占位族」栏的 fab 外框与中心距全部由本单生成器从板文件实算 (endpoint 口径, 与 `HW/FP_TRUTH_BASELINE.md` §2 表自己写的 4.00×5.00 / 2.70×1.60 / 3.00×3.00 逐个对得上)★; 「焊盘数 / 网络核对结论」栏的 pad↔net 映射由板文件实读, 与 `bash state/pcbnew_py.sh` 的 pcbnew 读数 13/13 逐件一致**★。

## §3 对「板那一趟」判据的影响 (★建议, 不是已改★)

★**本单不改 `state/board_trip_baseline_20260723.txt`** —— 那是 main 的地界, 老字一字不删★。★**下面是建议, 供 main 采纳后自己落**★。

### §3.1 那条判据为什么现在【不可能满足】 (两条独立的原因)

`state/board_trip_baseline_20260723.txt` 的「那一趟的验收口径」写着:

> ★**C4 的 158 个占位脚号必须随 ISS-356 的封装真值基线收敛** (⇒ 不许在那一趟里再留占位)★

★**这条判据有两条彼此独立的不可能** —— 只堵住一条, 那一趟照样交不出能下单的板:★

**原因一 (覆盖不足)**: ISS-356 的基线只覆盖 `ISS356-100` 件, 与 C4-158 只交 ★**77**★ 件 ⇒ ★**81 件根本没有目标 `lib:name`**★ ⇒ 用 ISS-356 的基线永远凑不齐 158。

**原因二 (机制错位) ★这一条更根本, 而且是本单新挖出来的★**:

★**C4 数的不是「板面 land 是不是官方封装」, 而是「网表节点串是不是 bare」** ★ —— §0 表第 12 行的沙盒实验: 只改网表节点命名, C4 从 158 掉到 153; ★**板面 land 一个字节没动**★。反过来, ★**把 ISS-356 那 100 件的 land 全部换成官方封装, C4 读数仍是 158**★。

★⇒ **「随封装真值基线收敛」这句话在机制上就不成立**: 换封装动不了 C4 的计数, ★**只有网表节点串具名 (bare → `pin<N>`) 才动得了**★ ⇒ ★**那一趟若只换 land 不具名脚, 这条判据无论怎么写都还是红的**★。

### §3.2 建议改成【分桶判据】 (四桶, 目标值之和 = ★158★)

★**把一条不可能的「158 全收敛」换成四条各自可数的桶判据**★ —— 每桶给一个可数的目标值, ★**四桶之和恰好 = 158**★ (⇒ 任何一件都逃不掉, 也任何一件都不重复算)。

| 桶 | 件数 (= 目标值) | 这桶是什么 | ★须做: land 换官方封装★ | ★须做: 网表节点具名脚★ | 判据出处 |
|---|---|---|---|---|---|
| **TP** | ★**42**★ | `type=='TP'` 的测试点 (★单 land, 焊盘号恒为 1 ⇒ **脚号无歧义**) | ★否★ (测试点不是器件, 无「封装真值」可言) | ★否★ (1 个 land, 焊盘号 1 恒定) | ISS-356 §5.2 U8 已登记「另一批落表范围」 |
| **DNP** | ★**26**★ | `dnp=='DNP'` 的不装件 | ★否★ (首版不贴 ⇒ land 可留占位) | ★**建议否**★ (不装 ⇒ 脚序无装配影响) | ISS-356 §5.2 U8 / ISS-354 §9-6-5 的 DNP 口径 |
| **靶内** | ★**77**★ | C4 ∩ ISS-356 靶子 (★**已有目标 `lib:name`**★) | ★**是**★ (77 件, 用 ISS-356 §2 表那一列) | ★**是**★ (77 件) | ISS-356 §2 (78 件里有 77 件在 C4) |
| **缺口** | ★**13**★ | ★**本单 §2 的对象**★ (真器件 · 必装 · 非 NET/TP) | ★**是**★ (13 件, 用本单 §2) | ★**是**★ (13 件) | ★**本单 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2**★ |
| ★**合计**★ | ★**158**★ | | ★**90**★ | ★**90**★ | |

★**⇒ 建议的新判据 (给 main 的落表稿, 本单不落)**:★

> ★**C4 的 158 件分四桶收口: TP 42 + DNP 26 豁免 (单 land / 不装 ⇒ 脚号与封装真值均无意义); 靶内 77 + 缺口 13 = ★90 件★必须在那一趟同时完成【换官方 land】+【网表节点具名脚】, 二者缺一即红** ★ ⇒ ★**C4 读数的目标值 = 158 − 90 = 68**★ (⇒ 实测该值即达标) ⇒
> ★**并且: 那 90 件的 land 必须是本页 §2 / ISS-356 §2 给的目标封装, 不是「随便换个官方封装」** ★ ⇒ ★**建议加一道判据: 板面每个封装都能在本页 §2 或 ISS-356 §2 找到同 ref 的目标 `lib:name` 行** ★

★**本单把这条判据变成了机器可判** ★ —— `HW/check_fp_truth_coverage_gap.py` 的 G1 (三集合件数自洽, 数字由脚本实算) + G2 (缺口 13 件逐件齐全) + G7 (四桶目标值之和 = 158) 就是它的可执行形式。

## §4 降级方案 (★逐件必填, 一件不空★)

★**口径**: 查不到 ⇒ ★**官网参数可满足的等效件** / ★**沙盒验证法** / ★**改设计路径绕开** ⇒ ★**三选一写清代价**★。★**每件都给了「已实测在盘的等效件 + 代价」, 零外部等待式措辞**★。

| ref | 查不到的点 | 降级方案 (三选一 + 代价) |
|---|---|---|
| `CHG_GND_STAR` | 型号 (它是单点汇流位, 非器件) + §5 K1 的表格自相矛盾 | 若落表批次要把它当可拆件 ⇒ 改用 2 焊盘件 (例 `Diode_SMD:D_SOD-323` md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = 新增第 2 脚 + 网表加 GND 以外的第二个网 ⇒ 与单点汇流位的功能定义冲突 ⇒ 不建议 |
| `D_ESD_CAM` | ★pad↔net 序 (器件 1=I/O 2=GND, 板是反的) ⇒ 靠改 land 一并解决, 不靠查料★ | 若 TI X1SON-2 封装在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 无第二档 ⇒ 改用 2 脚 SOD-323 单通道件 `Diode_SMD:D_SOD-323` (md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = Cd 0.42pF → 45pF ⇒ CSI-2 高速线上不可用 (Cd 45pF 会吃掉眼图裕量) ⇒ 不建议 |
| `D_ESD_DEMO` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 SOD-323 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Diode_SMD:D_SOD-323F` (SOD-323 带引脚变体) ⇒ 代价 = 焊接方式变 ⇒ 钢网要改 ⇒ 不建议; 或改小封装 `Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm` (md5 `c57a4058f16cf35599c2b748b9434350`) ⇒ 代价 = 手工贴装 + 板面更挤 ⇒ 不建议 |
| `D_ESD_USB_D` | ★**最终是 2 脚还是 3 脚 (老板 W-1/W-2 未拍)** ⇒ 目标封装随分支变 | ★3 脚档的候选封装随 W-1/W-2 分叉★ ⇒ 若拍「一颗双通道 3 脚」⇒ 候选 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`, 3 焊盘) ⇒ 代价 = ★**pad 序须按最终型号厂商 land 复核**★ (本栏 SOT-23-3 只是几何候选, 不是代拍); 若拍「两颗单通道」⇒ 本行保持 2 脚 X1SON-2 + 另加一只 2 脚件 (D− 侧) ⇒ 代价 = 板上多一颗件 + 两处 land 都要画 ⇒ 仍在本趟内可完成 |
| `FB_DEMO` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 Murata 0805 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Inductor_SMD:L_0805_2012Metric` 唯一档 ⇒ 改用更小 0603 (如 `Inductor_SMD:L_0603_1608Metric`) ⇒ 代价 = 电流 2A 降额到 1A 级 (BLM21PG 2000mA 是选型硬判据) ⇒ 不建议 |
| `Q_AND` | ★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★ | 若 SOT-23 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_TO_SOT_SMD:SOT-23` 唯一档 ⇒ 换 SOT-23 的 TO-236 变体 (`Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ ★**代价 = 厂商脚序可能不同, 必须逐颗重核 1=G/2=S/3=D**★ ⇒ 不省事, 不建议 |
| `Q_ENVC` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `Q_PG` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议 |
| `SW_BOOT` | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | ★若不改网表 ⇒ 只能选 2 land 的按键封装★ ⇒ 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` (md5 `749f20c5ab898069ade01682274c7bbf`, 2 焊盘 @3.400 mm, 本体 3.0×2.5mm) ⇒ 代价 = 按动力度 1.5N vs KMR2 的 3.0N ⇒ BOOT 键误触风险上升 (矩阵 §⑮ 选 3N 的理由就是防误触) ⇒ ★**这是选型代价, 不是本单能拍的**★; 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, C&K KXT3) ⇒ 代价 = 同上, 且本体 3.5×2.0 |
| `SW_KEY_PWR` | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | 同 SW_BOOT: 不改网表则只能选 2 land 封装 (`SW_SPST_B3U-1000P` md5 `749f20c5ab898069ade01682274c7bbf` / `SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 按动力度降到 1.5N ⇒ 电源键误触风险上升 ⇒ ★不代拍★ |
| `SW_KEY_VM` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 若 B3U-1000P 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Button_Switch_SMD:SW_SPST_B3U-1000P` 唯一档 ⇒ 改 KXT3 (`Button_Switch_SMD:SW_SPST_CK_KXT3` md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, 本体 3.5×2.0mm) ⇒ 代价 = 宽度 3.5 > 占位 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议 |
| `SW_KEY_VP` | 无 (库内档位已实测在盘) ⇒ 只有「换料」的代价 | 同 SW_KEY_VM ⇒ 退到 KXT3 (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ 邻键间隙复核 ⇒ 不建议 |
| `SW_RST` | ★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★ | 同 SW_BOOT: 不改网表则只能选 2 land 封装 ⇒ 代价 = 按动力度降到 1.5N ⇒ 复位键误触风险上升 ⇒ ★不代拍★ |

## §5 未决项与卡点 (★需要谁回答什么★)

| # | 卡点 | 事实 | 本单实测/依据 | 要谁答 |
|---|---|---|---|---|
| K1 | ★`CHG_GND_STAR` 在 `HW/FP_TRUTH_BASELINE.md` §2.2 表格里有两处自相矛盾★ | 同一行的「焊盘数 / 网络核对结论」栏写『焊盘数 1=1 一致』, 而「是否触发布局/布线改动」栏写『官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘 ⇒ 该器件接地脚与走线全新增』; 同页表格下方的正文又写『`CHG_GND_STAR` 的情况与另 2 件不同 … 1 个 land 是对的』。 | ★本单实测: KiCad 官方 `TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` 只有 ★**1 个**★焊盘 (pad "1" smd circle 1.0×1.0 mm, md5 `cea8eb3ba9b799767624661848b00243`) ⇒ ★**表格那一栏是错的, 照它改板会给 CHG_GND_STAR 加一个不存在的第 2 个 land**★。 | ★该页老字本单一字未改★ ⇒ 请 main 决定由谁订正该单元格 (本单只登记) |
| K2 | ★`D_ESD_USB_D` 的最终封装随老板 W-1/W-2 分叉★ | 本单 §2 该行给的是【现行 BOM opn (2 脚 TPD1E05U06DPYR) 那一档】的 lib:name; 那一趟 B07 却要求它变 3 脚。 | 两个分支的候选封装本单都已实测在盘 (3 脚档 `Package_TO_SOT_SMD:SOT-23-3` md5 `2cbbd67323e26100c49cafb6a9a881db` / 2 脚档 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 `0edfa97bd7bd277f3c05acf2bee23892`) ⇒ 但**哪一档生效是老板 W-1/W-2 的拍板项, 本单不代拍**。 | ★请老板拍 W-1/W-2 (见 §5 K2 的上游: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §5 第 5 条)★ |
| K3 | ★5 只按键换 KMR2 ⇒ 网表要同步给 4 个具名脚★ | 官方 `SW_Push_1P1T_NO_CK_KMR2` 有 4 个物理焊盘 (焊盘号 1,1,2,2), 而现行网表这 5 只只有 2 个脚。 | ★沙盒实测 (板副本, 真板 md5 未变): 把 SW_BOOT 改成 4 焊盘后跑 `state/check_pcb_nets.py` ⇒ C3 判红「★ SW_BOOT: 板 4 脚 / 网表 2 脚 ★」⇒ ★**那一趟若只改板不改网表, 这道闸当场红**★。 | ★请 main 决定: (a) 落表批次给这 5 只加 2 个具名脚 (⇒ 脚表也要加行) 或 (b) 改选 2 焊盘按键封装 (⇒ 按动力度 3N → 1.5N 的选型代价, 见 §2 各行降级方案)★ |
| K4 | ★`FB_DEMO` 在那一趟的两份文件里 0 命中 ⇒ 没人排它★ | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 里 `FB_DEMO` 各出现 0 次 (其余 12 件都出现过)。 | ★本单实测它的占位是【斜置 2 land @对角 1.000 mm】, 官方 0805 是【正置 @2.124 mm】⇒ ★**不改封装它就装不上**★, 而那一趟的清单里没有它 ⇒ 漏掉 ⇒ 板出来是坏的。 | ★请 main 把它并进那一趟的 land 重画清单 (本单只登记, 不代改既有页)★ |
| K5 | ★本单只给【封装真值】, 不给【料号】⇒ 13 件的 BOM `opn` 栏仍多为空★ | 13 件里 `CHG_GND_STAR` + 5 只按键 的 BOM `opn` 栏是 `[0数据]`; 其余 7 件的 opn 栏已有具体型号。 | ★封装的判定 (库文件在盘 + md5 + 焊盘数 + 几何) 本单全部给全; ★**但哪颗料**是选型批次的事★ ⇒ 落表批次可按本行目标 lib:name 回填同封装等效件 (ISS-356 §2 同一套路)。 | ★无阻塞项, 只是提醒: 本单 §2 的『候选 OPN』栏是候选不是决定★ |

### §5.1 本单的自我限定 (不越界的地方, 逐条)

1. ★**零写板** ★ —— 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / 4,940,213 B 开工前后逐字节未变; 本单唯一动过板的动作是**在 `tmp/iss361/` 的副本上**做沙盒实验, 副本跑完即删。
2. ★**零落表** ★ —— `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 原理图 一字未改; 本单 §2 的「目标 `lib:name`」是**给落表批次用的目标值**, 不是已落的值。
3. ★**零改既有闸** ★ —— `HW/check_fp_truth_baseline.py` / `HW/check_onepass_preflight_coverage.py` / `HW/check_preflight_regen_idempotent.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一个字节未改。
4. ★**零改既有页面正文** ★ —— `HW/FP_TRUTH_BASELINE.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `state/board_trip_baseline_20260723.txt` 老字一字不删; §3 的判据改动是**建议**, 落在本单自己的页里。
5. ★**零外发 / 零采购 / 零联系供应商** ★ —— 本单没发任何邮件/表单/询价, 没下单, 没问询。
6. ★**不替老板拍板** ★ —— `D_ESD_USB_D` 的 2 脚 vs 3 脚 (W-1/W-2) 只登记候选与代价 (§5 K2); 按键的 3N vs 1.5N 只登记代价 (§2 各行降级方案), ★**两个都没代选**★。
7. ★**只写 `state/fragments/hw.yaml`** ★ —— 走 `state/frag_write.py`, 写前后各记一次 md5 基线。
8. ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★。
9. ★**证据分级必标** ★ —— 全页用五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` (★**本单全页 0 处用第六种写法 (把官网级证据写成「官方」那一种)**★ ⇒ 闸 G5 实跑确认)。

### §5.2 复跑命令 (自证)

```bash
# ① 本单生成器 (重算页面里每个数字)
python3 logs/iss361/build_fp_truth_coverage_gap.py
# ② 本单机器闸 (正常跑)
python3 HW/check_fp_truth_coverage_gap.py
# ③ 本单机器闸 (反向用例自证)
python3 HW/check_fp_truth_coverage_gap.py --selftest
# ④ 三个口径的原始读数 (ISS-356 基线闸)
python3 HW/check_fp_truth_baseline.py
# ⑤ 三个口径的原始读数 (C4 ⇒ 必须走 KiCad python, 裸 python3 会 ModuleNotFoundError: pcbnew)
bash state/pcbnew_py.sh state/check_pcb_nets.py
# ⑥ 沙盒: 板面 4 焊盘 ⇒ C3 判红 (真板零改动)
python3 logs/iss361/zz_sandbox_4pad.py && bash state/pcbnew_py.sh state/check_pcb_nets.py tmp/iss361/sandbox_4pad_button.kicad_pcb
# ⑦ 沙盒: 只改网表节点命名 ⇒ C4 计数掉 (真网表零改动)
python3 logs/iss361/zz_c4_causality.py
# ⑧ 板/网表/脚表/BOM 的 md5 复核
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

