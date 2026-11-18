# ISS-318 · R3 现状基线清单 —— 「哪些引用现在就对不上」的完整表

- 生成时间: 2026-11-18 (本机 `yuewuya-RedmiBook-14` · Asia/Shanghai)
- 命令: `python3 SW/tools/check_sw_ref_reachability.py --dump-classification`
- 扫描面: 40 份 `SW/*.md` · 抽出 107 个唯一标识符
- 板位号 186 个 · 网表位号 293 个 · 网名 654 个

## ★结论: 现在有 **3 条**位号引用对不上 (= 闸的允许上限 `BASELINE_COUNT` = 3)

## A · 「本来就该对不上」(★不是位号 ⇒ 不进 R1★)

| token | 分类 | 命中规则 | 理由 |
|---|---|---|---|
| `CHG_BOARD` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `CHG_STAT` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `C_User_Hardware_Manual` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `L_B` | DOC_INTERNAL | C10 | 前缀 `L_` ∈ 物理量命名空间 (本项目板上无该前缀位号) |
| `L_eye` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `PWR_CTRL` | NET_NAME | C11 | 前缀 `PWR_` ∈ 电源轨名/逻辑信号名命名空间 |
| `PWR_GOOD` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `PWR_ON` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `R_BAT_DET_` | DOC_INTERNAL | C8 | 以 `_` 结尾 ⇒ 文本被截断的前缀 |
| `R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION` | DOC_INTERNAL | C4 | 盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引) |
| `R_SUPV_DIV` | DOC_INTERNAL | C12 | 是 ≥2 个 live 位号的严格前缀 (R_SUPV_DIV1, R_SUPV_DIV2) ⇒ 文档对一组件的统称 |
| `R_conv` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `R_on` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `R_skin_path` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `R_th` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |
| `SW_BRIGHTNESS_API_ANCHORS` | DOC_INTERNAL | C5 | 盘上某 .md 里有 `# BEGIN/END <token>` ⇒ 文档锚点 |
| `SW_BRIGHTNESS_CONTROL_POLICY` | DOC_INTERNAL | C4 | 盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引) |
| `SW_BRIGHTNESS_POLICY_ANCHORS` | DOC_INTERNAL | C5 | 盘上某 .md 里有 `# BEGIN/END <token>` ⇒ 文档锚点 |
| `SW_MD5_ANCHORS` | DOC_INTERNAL | C5 | 盘上某 .md 里有 `# BEGIN/END <token>` ⇒ 文档锚点 |
| `SW_MD5_BASELINE_LEDGER` | DOC_INTERNAL | C4 | 盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引) |
| `SW_REQUIREMENTS` | DOC_INTERNAL | C4 | 盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引) |
| `SW_SYNC_NETLIST` | DOC_INTERNAL | C6 | 盘上某 .py 把它当环境变量键用 ⇒ 判据/夹具的键名 |
| `SW_TIMING_REVIEW` | DOC_INTERNAL | C4 | 盘上有一份同名文档 ⇒ 文档自己的编号 (文档互引) |
| `U_DCDC` | DOC_INTERNAL | C12 | 是 ≥2 个 live 位号的严格前缀 (U_DCDC_VCORE, U_DCDC_VIO) ⇒ 文档对一组件的统称 |
| `U_LS` | DOC_INTERNAL | C9 | 每次出现都紧跟在 `|` 之后 ⇒ 判据正文里的 grep pattern |
| `VBUS_5V_CHG` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `VBUS_5V_F1` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `VBUS_DET` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `VBUS_DET_D` | NET_NAME | C3 | 它是【电源轨名 / 逻辑信号名】, 本来就不是位号 |
| `VBUS_DET_uA` | DOC_INTERNAL | C7 | 后缀含小写字母 ⇒ 物理量符号 (不是位号) |

## B · 「真隐患」(★形状像位号 · 板/网表里从来没有过 ⇒ 进 R1★)

| token | 分类 | 出现次数 | 首个位置 | 归类 | 理由 |
|---|---|---|---|---|---|
| `CONN_USB` | DESIGNATOR_MISSING | 5 | `SW/SW_TIMING_REVIEW.md:60` | 基线内·已登记 | ★真隐患·已登记★: SW/SW_TIMING_REVIEW.md L60/L272 明写「CONN_USB 已不在网表 ⇒ 对象消失 ⇒ 推翻」 ⇒ ★它是【历史件】的遗留引用·文档自己已经知道它没了·但引用还留在文档里★ |
| `TP_INT` | DESIGNATOR_MISSING | 12 | `SW/BOARD_ONEPASS_SW_SYNC.md:43` | 基线内·已登记 | ★真隐患·但已登记★: SW/BOARD_ONEPASS_SW_SYNC.md §SW06 明写「TP_INT (触控中断) 在网表和板上都不存在 ⇒ SW 侧不许按『有触控中断』写代码」⇒ ★它是一个【被文档自己点名的空洞】★ ⇒ 板那一趟若决定接触控, 必须同批落表 + 落位 + 布线, 否则 SW 侧引用永远是空的★ |
| `TP_TEMP` | DESIGNATOR_MISSING | 1 | `SW/SW_TIMING_REVIEW.md:374` | 基线内·已登记 | ★真隐患·未登记★: SW/SW_TIMING_REVIEW.md §CR-7 (EVT 上电段) 要求「TP_TEMP 热电偶对照标定」 ⇒ ★板上 42 个 TP_* 里没有 TP_TEMP (只有 TP_USB_D_N / TP_KEY_PWR / TP_RESET 等)★ ⇒ ★EVT 测温校准步骤依赖一个不存在的测试点 ⇒ 这就是本闸今天就抓得到的真隐患★ |

## C · 「改名漂移」(★建闸日是位号 · 现在解析不到 ⇒ 板改名之后才会出现★)

当前条数 = **0** (★S1 改名之前必然是 0★)

| —— | —— | —— |

## D · 「真位号·现在解析得到」(★R1 通过的部分·共 74 条·完整表见 `--dump-classification`)

| token | 在哪 |
|---|---|
| `BT_432243` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:74` |
| `CONN_CAM` | `SW/RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md:248` |
| `CONN_LIGHT` | `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md:65` |
| `C_DET_BAT` | `SW/SW_TIMING_REVIEW.md:7` |
| `C_DET_VBUS_D` | `SW/SW_TIMING_REVIEW.md:197` |
| `C_REGN` | `SW/SW_MD5_BASELINE_LEDGER.md:88` |
| `C_RST` | `SW/SW_TIMING_REVIEW.md:93` |
| `C_SW_IN` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:94` |
| `C_SW_OUT` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:94` |
| `C_VBUS_DEMO` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:141` |
| `C_VBUS_GND` | `SW/BOARD_ONEPASS_SW_SYNC.md:44` |
| `C_VBUS_OUT` | `SW/SW_MD5_BASELINE_LEDGER.md:87` |
| `D_CHG_LED` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `D_ESD_DEMO` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:141` |
| `D_ESD_USB_D` | `SW/BOARD_ONEPASS_SW_SYNC.md:45` |
| `D_LED_B` | `SW/BOARD_ONEPASS_SW_SYNC.md:41` |
| `D_LED_G` | `SW/BOARD_ONEPASS_SW_SYNC.md:26` |
| `D_LED_R` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `FB_DEMO` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:141` |
| `J_CHG` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:93` |
| `J_SOM_P1` | `SW/ADC_CALIBER_TABLE.md:13` |
| `J_SOM_P2` | `SW/SW_TIMING_REVIEW.md:92` |
| `J_SOM_P3` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:40` |
| `J_TYPE_C` | `SW/SW_TIMING_REVIEW.md:274` |
| `J_USB_C` | `SW/BOARD_ONEPASS_SW_SYNC.md:45` |
| `Q_AND` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `Q_CHG_LED` | `SW/BOARD_ONEPASS_SW_SYNC.md:41` |
| `Q_ENVC` | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md:51` |
| `Q_PG` | `SW/LOAD_SWITCH_SELECTION_FACTS.md:195` |
| `R_BAT_DET_1` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:304` |
| `R_BAT_DET_2` | `SW/SW_TIMING_REVIEW.md:7` |
| `R_CE` | `SW/SW_TIMING_REVIEW.md:324` |
| `R_EN_VCORE` | `SW/SW_TIMING_REVIEW.md:82` |
| `R_ILIM` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:245` |
| `R_PD_ON` | `SW/LOAD_SWITCH_SELECTION_FACTS.md:97` |
| `R_PG_PULL` | `SW/SW_TIMING_REVIEW.md:23` |
| `R_PU_BOOT_N` | `SW/BOARD_ONEPASS_SW_SYNC.md:42` |
| `R_PU_CHG_STAT` | `SW/SW_TIMING_REVIEW.md:58` |
| `R_PU_I2CA_SCL` | `SW/SW_TIMING_REVIEW.md:130` |
| `R_PU_I2CB_SCL` | `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md:121` |
| `R_PU_PG` | `SW/SW_TIMING_REVIEW.md:58` |
| `R_PU_RESET_N` | `SW/BOARD_ONEPASS_SW_SYNC.md:76` |
| `R_SER_RESET_N` | `SW/SW_TIMING_REVIEW.md:92` |
| `R_SER_USB_D_P` | `SW/SW_TIMING_REVIEW.md:275` |
| `R_SUPV_DIV1` | `SW/SW_TIMING_REVIEW.md:55` |
| `R_SUPV_DIV2` | `SW/SW_TIMING_REVIEW.md:122` |
| `R_VBUS_DET_D1` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:141` |
| `R_VBUS_DET_D2` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:141` |
| `SW_BOOT` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `SW_KEY_PWR` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `SW_KEY_VM` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `SW_KEY_VP` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `SW_RST` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `TP_BOOT` | `SW/SW_TIMING_REVIEW.md:97` |
| `TP_KEY_PWR` | `SW/BOARD_ONEPASS_SW_SYNC.md:43` |
| `TP_PG_VCORE` | `SW/SW_TIMING_REVIEW.md:68` |
| `TP_PG_VIO` | `SW/SW_TIMING_REVIEW.md:68` |
| `TP_RESET` | `SW/BOARD_ONEPASS_SW_SYNC.md:43` |
| `TP_USB_D_N` | `SW/BOARD_ONEPASS_SW_SYNC.md:43` |
| `U_BATPROT` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:75` |
| `U_CHG` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:60` |
| `U_DCDC_VCORE` | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md:51` |
| `U_DCDC_VIO` | `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md:51` |
| `U_EN_SW` | `SW/LOAD_SWITCH_SELECTION_FACTS.md:1` |
| `U_LDO_IO18` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:52` |
| `U_LDO_IO33` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:51` |
| `U_LDO_L18` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:54` |
| `U_LDO_L33` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:53` |
| `U_LDO_S12` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:55` |
| `U_LDO_S18B` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:56` |
| `U_LDO_S28` | `SW/SHUTDOWN_SEMANTICS_SPEC.md:57` |
| `U_PWR_SW` | `SW/LOAD_SWITCH_SELECTION_FACTS.md:1` |
| `U_SUPV` | `SW/BOARD_ONEPASS_SW_SYNC.md:40` |
| `U_TEMP` | `SW/SW_TIMING_REVIEW.md:40` |
