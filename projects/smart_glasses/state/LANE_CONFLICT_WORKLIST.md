# LANE_CONFLICT_WORKLIST.md —— ★★45 条未连接的【布局冲突工作单】★★ (★2026-11-09 18:4x)

> ★**这份文件的用途**: ★**把"45 条的病根 = 走廊被占"从【诊断】变成【可执行的工作单】**
> ⇒ ★**工具**: ★**`state/probe_lane_conflicts.py`** (★纯几何, ★只读, ★不改板)
> ⇒ ★**用法**: ★**`bash state/pcbnew_py.sh state/probe_lane_conflicts.py HW/PCB/demo_mainboard.kicad_pcb /tmp/_drc45.json --out <txt>`**

---

## 1. ★★**判据 (★全是几何, ★零猜测)** ★★

1. ★**走廊 = 两焊盘中心之间的直线** (★该网要连上, 必须走这条路)
2. ★**横穿 = 异网铜段与该走廊【真正相交】** (★不是"靠近")
3. ★**挪得动吗 = 把第二个焊盘【垂直于走廊】平移 d, 重测是否还有横穿** ⇒ 给出**最小可行位移**

★**⇒ 输出的每一行都是"【哪个网】的【哪两个焊盘】之间, 被【谁】横穿, 挪【多少】能解"** ★

---

## 2. ★★**★可执行子集 (★挪 0.3~2mm 就能解 ⇒ 优先做这些)★★** ★★

| 网 | 焊盘A | 焊盘B | 走廊长 | 横穿它的网 | ★最小可行挪动 |
|---|---|---|---|---|---|
| ★**FSIN_OUT** | R_SER_FSIN.1 | TP_FSIN.1 | 3.01 | VDD_3V3_IO, V_SOC_IO | ★**0.5mm 左** ★ |
| ★**LIGHT_5V** | D_ESD_LIGHT.1 | CONN_CAM.30 | 6.56 | BAT_SW, DSI_D0_D0_P, DSI_D0_D1_N | ★**0.5mm 右** ★ |
| ★**LIGHT_5V** | D_ESD_LIGHT.1 | CONN_CAM.31 | 6.88 | 同上 | ★**1.0mm 右** ★ |
| ★**PWR_GOOD** | Q_PG.3 | TP_PG.1 | 6.55 | DSI_D0_CK_N/P, DSI_D0_D0_P | ★**0.5mm 左** ★ |
| ★**PWR_GOOD** | Q_PG.3 | R_PU_PG.2 | 15.13 | DSI_D0_D0_P, LIGHT_1V8, LIGHT_3V3 | ★**0.3mm 右** ★ |
| ★**PWR_GOOD** | TP_PG.1 | R_PU_PG.2 | 18.00 | DSI_D0_CK_N/P, DSI_D0_D0_P | ★**0.5mm 右** ★ |
| ★**I2C_A_SCL** | TP_I2CA_SCL.1 | R_PU_I2CA_SCL.1 | 3.01 | RESET_N, VDD_3V3_IO | ★**0.3mm 左** ★ |
| ★**I2C_A_SDA** | R_PU_I2CA_SDA.1 | TP_I2CA_SDA.1 | 3.01 | RESET_N, VDD_3V3_IO | ★**0.3mm 左** ★ |
| ★**I2C_B_SDA** | TP_I2CB_SDA.1 | R_PU_I2CB_SDA.1 | 16.62 | UART_TX | ★**0.3mm 左** ★ |
| ★**I2C_B_SDA** | U_TEMP.6 | R_PU_I2CB_SDA.1 | 14.62 | UART_TX | ★**0.3mm 左** ★ |
| ★**ID_DETECT_0** | R_PU_ID0.1 | R_ID_JMP0.1 | 4.80 | GND | ★**0.3mm 左** ★ |
| ★**ID_DETECT_1** | R_PU_ID1.1 | R_ID_JMP1.1 | 4.80 | DSI_D0_CK_P, DSI_D0_D1_N, GND | ★**0.5mm 右** ★ |
| ★**KEY_CAM** | C_KEY_CAM.1 | SW_KEY_CAM.1 | 9.60 | VDD_3V3_IO | ★**0.3mm 右** ★ |
| ★**KEY_CAM** | R_KEY_CAM.1 | SW_KEY_CAM.1 | 4.80 | VDD_3V3_IO | ★**0.3mm 右** ★ |
| ★**KEY_CAM** | SW_KEY_CAM.1 | J_SOM_P4.3 | 18.28 | CSI_D0_D0_P_SRC, CSI_D0_D1_P_SRC, DSI_D0_D3_P | ★**0.8mm 左** ★ |
| ★**LED_G** | R_LED_G.1 | J_SOM_P4.19 | 27.85 | CSI_D0_D0_P_SRC, CSI_D0_D1_P_SRC, CSI_D0_D2_N_SRC | ★**0.5mm 右** ★ |
| ★**LED_G** | TP_LED_G.1 | J_SOM_P4.19 | 29.06 | 同上 | ★**1.5mm 右** ★ |
| ★**CSI_D0_D3_N_SRC** | C_AC_CSI_D0_D3_N.1 | J_SOM_P4.89 | 10.03 | CSI_D0_D2_N_SRC, CSI_D0_D2_P_SRC, CSI_D0_D3_P_SRC | ★**0.5mm 右** ★ |
| ★**CSI_D0_D0_N** | TP_CSI_D0_N.1 | C_AC_CSI_D0_D0_N.2 | 3.68 | CSI_D0_CK_N/P, CSI_D0_D0_P | ★**2.0mm 左** ★ |
| ★**BAT_DET** | R_BAT_DET_2.1 | R_BAT_DET_1.1 | 4.80 | BAT, DSI_D0_D2_N, KEY_PWR | ★**1.5mm 左** ★ |
| ★**USB_CC2** | J_USB_C.B5 | R_CC2_D.1 | 40.19 | LIGHT_1V8, SENSOR_AVDD, SENSOR_CORE | ★**0.3mm 右** ★ |
| ★**JTAG_TDI** | R_JTAG_TDI.2 | J_DEBUG.3 | 14.00 | JTAG_TDO, JTAG_TMS, TS_BAT | ★**2.0mm 右** ★ |
| ★**DSI_D0_D1_N_SRC** | R_SEL_D1_N.1 | J_SOM_P3.63 | 66.14 | DSI_D0_CK_N_SRC/P_SRC, DSI_D0_D0_P | ★**0.8mm 左** ★ |
| ★**DSI_D0_D1_P_SRC** | R_SEL_D1_P.1 | J_SOM_P3.65 | 71.34 | 同上 | ★**1.0mm 右** ★ |
| ★**DSI_D0_D0_N_SRC** | R_SEL_D0_N.1 | J_SOM_P3.57 | 55.35 | DSI_D0_CK_N_SRC/P_SRC, DSI_D0_D3_P_SRC | ★**1.5mm 左** ★ |
| ★**DSI_D0_D0_P_SRC** | R_SEL_D0_P.1 | J_SOM_P3.59 | 60.55 | 同上 | ★**2.0mm 左** ★ |
| ★**DSI_D0_D1_N** | CONN_LIGHT.2 | TP_DSI_D1_N.1 | 60.56 | CSI_MCLK, CSI_MCLK_SRC, DSI_D0_CK_N | ★**2.0mm 左** ★ |
| ★**DSI_D0_D1_P** | CONN_LIGHT.3 | TP_DSI_D1_P.1 | 65.22 | BAT_DOUT, CSI_MCLK, CSI_MCLK_SRC | ★**1.5mm 左** ★ |
| ★**DSI_D0_CK_N** | TP_DSI_CK_N.1 | R_SEL_CK_N.2 | 76.87 | BAT_CELL_P, BAT_GATE, BAT_PROT_CELL | ★**1.5mm 右** ★ |
| ★**I2C_A_SCL** | R_PU_I2CA_SCL.1 | J_SOM_P2.31 | 16.22 | CSI_D0_CK_N/P, CSI_D0_D0_P | ★**1.0mm 左** ★ |
| ★**I2C_A_SCL** | TP_I2CA_SCL.1 | J_SOM_P2.31 | 18.37 | 同上 | ★**1.5mm 左** ★ |
| ★**I2C_A_SDA** | R_PU_I2CA_SDA.1 | J_SOM_P2.33 | 19.54 | 同上 | ★**1.5mm 左** ★ |
| ★**I2C_A_SDA** | J_SOM_P2.33 | TP_I2CA_SDA.1 | 21.32 | 同上 | ★**0.8mm 左** ★ |
| ★**I2C_B_SCL** | TP_I2CB_SCL.1 | CONN_LIGHT.11 | 26.73 | GND, VDD_3V3_IO | ★**1.5mm 左** ★ |
| ★**I2C_B_SCL** | U_TEMP.1 | CONN_LIGHT.11 | 21.29 | GND, VDD_3V3_IO | ★**1.5mm 左** ★ |
| ★**LIGHT_3V3** | C_HF_LIGHT_3V3.1 | U_LDO_L33.1 | 33.35 | EN_VCORE, PWR_GOOD, RESET_N | ★**2.0mm 左** ★ |
| ★**DSI_D0_CK_P** | R_SEL_CK_P.2 | TP_DSI_CK_P.1 | 76.98 | BAT_CELL_P, BAT_DET, BAT_DOUT | ★**3.0mm 右** ★ |

---

## 3. ★★**★为什么这份工作单可信 (★三条独立印证)★★** ★★

1. ★★★**★⇒ `FSIN_OUT` 这条是【我独立推出来的那个例子】**: ★**走廊 3.01mm · 被 `VDD_3V3_IO` + `V_SOC_IO` 横穿 · 挪 0.5mm 可解** ⇒ ★★**与昨晚"FSIN_OUT 两焊盘几乎同 x ⇒ 垂线必经 x=93.45 ⇒ VDD_3V3_IO 横穿"的推导【完全吻合】** ⇒ ★★**⇒ 工具算出来的和手推出来的一致** ★★★ ★★★
2. ★★★★**★⇒ rip 修不动的网, 全都在这份清单里**: ★**`LIGHT_5V` · `PWR_GOOD` · `I2C_A_SCL` · `I2C_A_SDA` · `LED_G`** ⇒ ★★**⇒ rip 为什么失败, 现在有了统一解释: 【它们的走廊本身被横穿】⇒ ★★**⇒ 这解释了 42 个候选网里 39 个"仍不通"** ★★★★ ★★★
3. ★★★★**★⇒ 【A2 桶 4 条】也都在清单里** (★`I2C_A_SCL` / `I2C_A_SDA` / `LED_G` / `DSI_D0_D1_P`) ⇒ ★★**⇒ 之前判定"A2 此路不通(rip)", 现在有了解释: ★★**不是 rip 弱, 是走廊被占** ⇒ ★★**⇒ 【挪 0.3~0.5mm】就能解, 不用动路由器** ★★★★ ★★★

---

## 4. ★★**下一步建议 (★按 ROI 排)★★** ★★

| # | 动作 | 依据 |
|---|---|---|
| ★**1** | ★**先做【0.3~0.8mm】那一档的挪动** (★约 12 条, ★如 `TP_I2CA_SCL` / `TP_I2CA_SDA` / `TP_I2CB_SDA` / `R_PU_ID0` / `SW_KEY_CAM` / `TP_FSIN` / `Q_PG` / `D_ESD_LIGHT` …) | ★**位移最小 · 改动最可控** ★★ |
| ★**2** | ★**每次挪完必须【出臂 + 套已校准链 + vs `baseline_v76_chain`】** | ★**⇒ 不看"某条通了"这种局部读数, ★看【同把尺子下的端到端】** ★★ |
| ★**3** | ★★**挪动时【必须同时查"被挪的器件自己有没有占别人走廊"】** ★★ | ★★**★实测教训: ★★**"挪 R_SEL 后 unc 58 更差" (★v56) ⇒ ★★**因为它挪完占住了别人的走廊** ⇒ ★★**⇒ 必须用 `probe_lane_conflicts.py` 【在挪完之后】重测, ★而不是想当然** ★★ ★★ |
| ★**4** | ★**别先动"挪 3mm 内无解"的那批** (★如 `LIGHT_3V3` 的长走廊) | ★**长走廊被几十条铜穿过 ⇒ 挪一个焊盘解决不了 ⇒ 要么挪两个, 要么这条路不通** ★★ |

★**★数据出处**: ★**`state/probe_lane_conflicts.py` 跑官方板 + `/tmp/_drc45.json` (★45 条 unc) ⇒ 输出 `/tmp/_lane_conflicts.txt` (★全量 129 条冲突, ★本文件取的是【可执行子集】)** ★
★**★纪律**: ★**本文件只是【施工单】, ★板面零改动 (★官方板 md5 `611b869e` 未动) ⇒ ★真正挪动需另起臂 + 走晋级闸** ★

---

## 5. ★★★**★⚠️ 必读: 官方板与臂臂的【布局基础不同】⇒ ★★**部分位移【不能直接套用】** ★★★** ★★

> ★★★★**★实测 (★2026-11-09 19:2x, ★官方板 vs `v76_R` 逐器件对比)**: ★★**`R_SEL_*` 全家 10 个 + `Q_PG`/`TP_PG`/`R_PU_ID0`/`R_PU_ID1`/`R_BAT_DET1`/`R_BAT_DET2` 共 16 个器件, 在官方板上是【排版器自动放】(★y=5.5 那排), 在 v76 臂里是【手动钉位】(★y=3.0 那排) ⇒ ★★**两边布局基础不同 ⇒ ★★**这些器件的位移【不可】直接套到臂上** ★★★★ ★★
> ★★**位移【可直接套用】的 19 个** (★两边位置逐位一致)★: ★`C_AC_CSI_D0_D0_N` · `C_AC_CSI_D0_D3_N` · `C_KEY_CAM` · `J_DEBUG` · `J_USB_C` · `R_CC2_D` · `R_JTAG_TDI` · `R_KEY_CAM` · `R_LED_G` · `R_PU_I2CA_SCL` · `R_PU_I2CA_SDA` · `R_PU_PG` · `R_SER_FSIN` · `SW_KEY_CAM` · `TP_CSI_D0_N` · `TP_FSIN` · `TP_I2CA_SCL` · `TP_I2CB_SDA` · `TP_LED_G` ★★
> ★★**位移【不可直接套用】的 16 个**: ★`R_SEL_CK_N/P` · `R_SEL_D0_P/N` · `R_SEL_D1_P/N` · `R_SEL_D2_P/N` · `R_SEL_D3_P/N` · `Q_PG` · `TP_PG` · `R_PU_ID0` · `R_PU_ID1` · `R_BAT_DET_1` · `R_BAT_DET_2` ★★
> ★★★**★⇒ 这本身也解释了今晚的一条老结论**: ★★**MEMORY 里 [挪 R_SEL 后 unc 58 更差 (v56)] ⇒ ★★**现在看: R_SEL 在官方板与臂上位置本就不同 ⇒ ★★**[在官方板上算的挪动]套到臂上 = 挪错位置 ⇒ ★★**这就是 v56 变差的可能机制之一** ⇒ ★★**⇒ 在臂上挪之前, 必须先在【臂的板】上重算冲突清单** ★★★★ ★★

### ★★**★第一批的正确流程 (★按序, ★每步都有判据)★★** ★★
| 步 | 动作 | 判据 |
|---|---|---|
| ★**1** | ★**在 `v76_R` (★臂的板) 上跑 `probe_lane_conflicts.py`** | ★★**得到【臂自己的】冲突清单** (★与官方板的不同!) ★★ |
| ★**2** | ★**挑 0.3~0.8mm、器件 ≤2 焊盘、且【两板位置一致】的条目** | ★**避开 16 个位置不一致的器件** ★★ |
| ★**3** | ★**生成 `PCB_PART_POS` 钉位串 (★`plan_part_moves.py`)** | ★**★钉位串里每个 ref 只能出现一次 (★第一批要人工去重)** ★★ |
| ★**4** | ★**出臂 ⇒ 套已校准链 ⇒ vs `baseline_v76_chain`** | ★★**端到端读数 (★不只看某条通了) ★★ |
| ★**5** | ★**挪完重跑 `probe_lane_conflicts.py` (★在臂的板上)** | ★★**★冲突总数没变大** ⇒ ★★**没占掉别人的走廊 (★v56 教训) ★★ |

---

## 6. ★★★**★⚠️ 【加害者】vs 【受害方】: ★★**不要挪加害者** ★★★** ★★

> ★★★★**★实测 (★臂 `v76_R` 的 269 条冲突按[横穿者]统计) ★★★★ ★★★
> | 横穿者 | 作为横穿者的冲突数 | 性质 |
> |---|---|---|
> | ★`BAT` | ★**85** | ★**电源主干** ★
> | ★`CSI_D0_CK_N` | ★**79** | ★**差分主干** ★
> | ★`BAT_SW` | ★**52** | 电源 |
> | ★`CSI_D0_CK_P` | ★**51** | 差分主干 |
> | ★`CSI_D0_CK_N_SRC` | ★**50** | 差分主干 |
> | ★`CSI_D0_D0_P_SRC` | ★**42** | 差分主干 |
> | ★`BAT_CELL_N` / `BAT_CELL_P` | 36 / 36 | 电源 |
> | ★`GND` | 21 | 平面 |

> ★★★★**★⇒ 结论 (★这一条会决定第一批挪谁)**: ★★★
> · ★★**这些是【加害者】: 它们的铜【主动横穿】别人的走廊 ⇒ ⇒ 别人绕不开** ★★
> · ★★★**★⇒ 【挪它们不解决别人的问题】(★它们自己多半是通的) ⇒ ★★**反而会把主干/电源挪乱 ⇒ ⇒ ★★**第一批【绝对不要动】BAT / CSI_D0_CK_* / BAT_SW / BAT_CELL_* / GND 这类** ★★★ ★★★
> · ★★**要动的是【受害方】: 自己的走廊被别人横穿的网** ⇒ ★★**⇒ 第一批 12 个里 `C_KEY_CAM`/`SW_KEY_CAM`/`R_LED_B`/`D_ESD_LIGHT`/`R_JTAG_TDI`/`TP_FSIN` 等都是受害方 ⇒ ★★**方向对** ★★
> · ★★★**★⇒ 兄弟提的[VDD_3V3_IO / PG_AND 单独开施工单] ⇒ ★★**实测它给的两个数不准 (★VDD_3V3_IO 19 条 / PG_AND 0 条) ⇒ ★★**真正的头号加害者是 BAT / CSI_D0_CK_N ⇒ ★★**该单独看的是【这些主干自己的走廊】, 而不是挪它们** ★★★ ★★★
