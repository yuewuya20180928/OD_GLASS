# 板那一趟 · 布线验收线的「零假连通」口径页 (SW)

> ★**ISS-381 cont1 · sw-lead · 2026-11-24 07:2x–07:4x (Asia/Shanghai) · 零写板 · 零落表 · 零改既有闸 · 零挂链 · 零外发** ★
> ★**本页 = 新建页 · 不改任何既有页面正文** (`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 一字未动) ★
> ★**机器闸**: `SW/tools/check_sw_false_connectivity_gate.py` (★本单新建 · ★**零挂进 `state/gate_check.py`** · 挂不挂归 main★) ★

---

## §0 · 一句话结论

★**`unc 45 → 0` 是【计数】判据, 它能证明"板上没剩下 ratsnest 悬空连接", 但它【不能证明】"那 23 条必需网逐条真接上了" ⇒ ⇒ 「45→0 全绿」与「必需网逐条真接上」是两件事 ⇒ ⇒ 布线验收线必须写成【逐条列铜 (网名 + 期望焊盘集合 + 铜段数 + 铜长)】而不是【只守 unc 计数】, 因为【删焊盘 / 标 NC / 改名】三种刷法都能把 45 刷到 0 而【一条铜都不加】。** ★

★**本单同时订正 main 的 need 口径一处误述**: 「unc 判据抓不到 UART_RX」这半句**已被本机实测证伪** —— `UART_RX` 现在就是那 45 条 unconnected 里的一条 (逐网计数 = 1 项) ⇒ ★**零铜且 pad≥2 的网【必然】贡献 ≥1 条 unc item** ⇒ ★**真洞不是「unc 抓不到它」, 而是「unc 只数条数、不认身份」** (详见 §2)。 ★

★**当前板面事实 [实测]**: 23 条必需网 **【全部零铜】** (铜段数 0 / 铜长 0.0 mm) · 焊盘集合 **23/23 与脚表一致** · `FSIN_OUT` 零铜且不在必需表 ⇒ ★**板那一趟要做的正是把这 23 条逐条接上, 而验收线必须逐条点名, 不能只看 45 这个数**。 ★

---

## §1 · 板面真值 (★7 行 · 全部本机实跑 · 证据等级 [实测]★)

| # | 项 | 实测值 | 复现命令 |
|---|---|---|---|
| 1 | 板指纹 | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ **19 天逐字节未动** | `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` |
| 2 | `UART_RX` 铜箔清单 | **0 段走线 · 0 过孔 · 2 个焊盘** (`J_UART.2` + `J_SOM_P2.9`) ⇒ 整网零铜 | `python3 SW/tools/check_sw_false_connectivity_gate.py --print-net UART_RX` (★本单新建闸的只读查询口★) |
| 3 | 零铜网全集 (pad≥2 口径) | **24 条** = 15 条高速差分腿 (`CSI_D0_*` / `DSI_D0_*`) + 8 条单端脚 + 1 条可悬空 (`FSIN_OUT`) | `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb` (§① 目标名单) |
| 4 | 分级自检 | 必需 `23` (期望 23) · 可悬空 `1` (期望 1) · 待定 `0` (期望 0) ⇒ **一致 ✔** | 同上 (脚本末尾 `★分级自检`) |
| 5 | `UART_TX` 对照 | **3 焊盘 · 230 段走线 · 4 过孔 · 铜长 69.202 mm** ⇒ 日志抓取链完整 (★★派活材料写的是「234 段走线 · 0 过孔」, 本单三个独立解析器一致读出 230 段 / 4 过孔 ⇒ 以实测为准, ★差额 4 疑似派活材料把过孔并进了段数★★) | `python3 SW/tools/check_sw_false_connectivity_gate.py --print-net UART_TX` |
| 6 | DRC 现状 | `N' = 45` (本板自己跑 DRC 得出) · DRC violations = `0` | `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb` (§② 汇总) |
| 7 | 零铜网 vs unconnected | **「24 条零铜网」与「45 条 unconnected」是两个口径, 不许互相替代** | 同上 (脚本每次都打这一句) |

★**期望焊盘集合的来源 = `HW/netlist_v1_pins.csv` (脚表真源)**, 过滤 `board ∈ {空, MAIN_PCB}` (★`CHG_BOARD` 行的 `J_TYPE_C.B5` / `R_CC2.1` 属充电板, 不是主板焊盘·故不计入★), 脚号归一 (`pin54` → `54`) ⇒ ★**期望集合从脚表读, 不是从板面读** (★否则就是「用板面证明板面」★)。 ★

---

## §2 · ★口径订正块 (追加块 · 老字一个字不许删)★

> ★**本块是本单最核心的一段** ★
> ★**订正对象**: `state/fragments/pm.yaml` · `iss379_q6_uart_rx_zero_copper` 里的一句 「★**它现在是 0 段铜 · 「0→0」不违反 unc 判据 ⇒ unc 45→0 全绿【不代表】这条网通了★**」 ★
> ★**老字保留在原处, 本页只做【追加订正】, 不去改 main 的分片正文** ★

### §2.1 · 成立的那半句 (保留)

★**`UART_RX` 全网 0 段走线 0 过孔, 只有 `J_UART.2` + `J_SOM_P2.9` 两个焊盘 ⇒ 它在板上【一寸铜都没有】⇒ 【现在就没接】⇒ 这是【独立于 land 换装的缺口】。 (证据等级 [实测]) ★

### §2.2 · ★被证伪的那半句 (追加订正)★

★**main 原文**: 「「0→0」不违反 unc 判据 ⇒ 【unc 判据抓不到它】」 ★
★**本机实测证伪**: `UART_RX` **现在就是那 45 条 unconnected 里的一条** (DRC JSON `unconnected_items` 逐网计数: `UART_RX` → **1 项**; 同批还有 `FSIN_OUT` 1 · `JTAG_TDI` 1 · `LED_G_D` 1 · `USB_CC2` 1 · `SPI_SCLK_BOOT` 1 · `SPI_MOSI_BOOT` 1 · `SPI_MISO_BOOT` 1 · 15 条差分腿各 1~2 项)。 ⇒ ★**2 个焊盘 0 铜 ⇒ 恰好产生 1 条 ratsnest 连接 ⇒ 它【是】被 unc 数的** ⇒ ★**「0→0 不违反 unc 判据」不成立**。 ★

★**一般化 (推算, 由实测归纳)**: ★**零铜且 pad≥2 的网, 必然贡献 ≥1 条 unc item** (两个焊盘之间必有一条 ratsnest) ⇒ ★**unc 判据【不是】抓不到零铜网, 它【抓得到】—— 抓不到的是【身份】**。 ★

### §2.3 · ★★所以真洞是这句话 (本单的交卷结论)★★

> ★★**`unc 45 → 0` 是一条【计数】判据 ⇒ 它【不能证明是哪 23 条必需网被接上了】⇒ ⇒ 「45→0 全绿」与「必需网逐条真接上」是两件事 ⇒ ⇒ 若只守 unc 计数, 下列三种刷法都能把 45 刷到 0 而【一条铜都不加】。** ★★

★**复现**: `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb` (§② 逐条 unconnected 网名) ★

### §2.4 · ★★端到端决定性实验 (★本单沙盒实跑 · 追加块 · 证据等级 [实测]★)★★

★**上面 §2.2 的「证伪」是【读数层】的; 这一段是【实验层】的 —— 直接把「计数 ≠ 身份」这句话跑出来。** ★

★**实验设计**: ★**从真板复制一份沙盒副本** (`tmp/iss381_sbx/cheat/cheat4_nc_all_24.kicad_pcb`) ⇒ ★**把 23 条必需网 + 1 条可悬空的【全部焊盘】的 net 清成 0 (= 标 no-connect)** ⇒ ★**一个 segment / 一个 via 都没动 ⇒ 【一条铜都不加】** ⇒ ★**然后跑 KiCad DRC 读 unc 条数, 并用本单新建的闸跑 post 相** ★

| 读数 | 真板 (基线) | 沙盒副本 (24 条网全标 NC) | 差 |
|---|---|---|---|
| ★**unconnected items (unc 计数)** ★ | **45** (43 个网名) | **20** (19 个网名) | ★**−25 条** ★ |
| ★**DRC violations** ★ | 0 | 0 | — |
| ★**23 条必需网的铜段数** ★ | ★**全 0** ★ | ★**全 0 (一条铜都没加!)** ★ | ★**0** ★ |
| ★**23 条必需网的铜长** ★ | ★**全 0.0 mm** ★ | ★**全 0.0 mm** ★ | ★**0.0 mm** ★ |
| ★**那 24 条网各自的 unc 计数** ★ | 各 ≥1 (共 25 项) | ★**各 0 (全部消失)** ★ | ★**−25** ★ |
| ★**闸 (post 相) 判定** ★ | 红 · 逐条点名 23 条 | ★**红 · 点名 `UART_RX`: 「K1a: 板面查不到该网 (身份缺失)」** ★ | ★**判红且点名** ★ |

★**⇒ 这就是本单最硬的一条事实**: ★**unc 计数在【一条铜都不加】的前提下被刷掉了 25 条 (45 → 20) ⇒ 计数口径被骗; 而同一时刻, 23 条必需网的铜段数仍是 0 / 铜长仍是 0.0 mm ⇒ 逐条口径把它们一条不落地点名 ⇒ ⇒ 「45→0 全绿」与「必需网逐条真接上」【确证】是两件事。** ★

★**复现 (★两条命令·★都在项目盘内跑·★真板零写★)**: ★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss381_sbx/e2e_count_vs_identity.py     # ★决定性实验 (45 → 20 · 铜 +0)★
python3 tmp/iss381_sbx/e2e_cheat_proof.py            # ★三刷法端到端 (真板副本层) 全被抓住并点名★
```
★**日志**: `logs/iss381/e2e_count_vs_identity.txt` · `logs/iss381/e2e_cheat_proof.txt` ★

---

## §3 · ★逐条列铜表 (布线验收线的正样)★

★**证据等级: 本段全部为 [实测]** (★板面读数取自已落盘探针读数·期望集合取自脚表★) ★
★**覆盖全部 23 条必需网, 一条不许漏**; ★**`FSIN_OUT` 单列为「可悬空」一行, 不许混进必需表**。 ★
★**「期望焊盘集合」从脚表读 · 「板面实际焊盘集合 / 铜段数 / 铜长」从 `tmp/iss381_sbx/board_nets.json` 读 (★上一趟已落盘的读数, 本趟不重跑探针★) · 另与 `tmp/iss381_sbx/board_nets_pcbnew.json` (pcbnew API 口径) 交叉核对一致 (★K2★)。 ★

| # | 网名 | 分级 | 期望焊盘集合 (脚表 `HW/netlist_v1_pins.csv`, board∈{空,MAIN_PCB}) | 板面实际焊盘集合 | 实际铜段数 | 实际铜长 mm | 差在哪 | 判定 (post 相 = 板那一趟验收线) |
|---|---|---|---|---|---|---|---|---|
| 1 | `CAM_RESET_N` | 必需·单端脚 | CONN_CAM.27 J_SOM_P1.54 | CONN_CAM.27 J_SOM_P1.54 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 2 | `CSI_D0_D0_N` | 必需·差分腿 | CONN_CAM.14 C_AC_CSI_D0_D0_N.2 TP_CSI_D0_N.1 | CONN_CAM.14 C_AC_CSI_D0_D0_N.2 TP_CSI_D0_N.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D0_P | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 3 | `CSI_D0_D0_N_SRC` | 必需·差分腿 | C_AC_CSI_D0_D0_N.1 J_SOM_P4.65 | C_AC_CSI_D0_D0_N.1 J_SOM_P4.65 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D0_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 4 | `CSI_D0_D1_N` | 必需·差分腿 | CONN_CAM.11 C_AC_CSI_D0_D1_N.2 | CONN_CAM.11 C_AC_CSI_D0_D1_N.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D1_P | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 5 | `CSI_D0_D1_N_SRC` | 必需·差分腿 | C_AC_CSI_D0_D1_N.1 J_SOM_P4.71 | C_AC_CSI_D0_D1_N.1 J_SOM_P4.71 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D1_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 6 | `CSI_D0_D1_P` | 必需·差分腿 | CONN_CAM.12 C_AC_CSI_D0_D1_P.2 | CONN_CAM.12 C_AC_CSI_D0_D1_P.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D1_N | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 7 | `CSI_D0_D2_N` | 必需·差分腿 | CONN_CAM.5 C_AC_CSI_D0_D2_N.2 | CONN_CAM.5 C_AC_CSI_D0_D2_N.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D2_P | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 8 | `CSI_D0_D2_P` | 必需·差分腿 | CONN_CAM.6 C_AC_CSI_D0_D2_P.2 | CONN_CAM.6 C_AC_CSI_D0_D2_P.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D2_N | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 9 | `CSI_D0_D3_N` | 必需·差分腿 | CONN_CAM.2 C_AC_CSI_D0_D3_N.2 | CONN_CAM.2 C_AC_CSI_D0_D3_N.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D3_P | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 10 | `CSI_D0_D3_N_SRC` | 必需·差分腿 | C_AC_CSI_D0_D3_N.1 J_SOM_P4.89 | C_AC_CSI_D0_D3_N.1 J_SOM_P4.89 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: CSI_D0_D3_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 11 | `DSI_D0_D0_N_SRC` | 必需·差分腿 | J_SOM_P3.57 R_SEL_D0_N.1 | J_SOM_P3.57 R_SEL_D0_N.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D0_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 12 | `DSI_D0_D0_P_SRC` | 必需·差分腿 | J_SOM_P3.59 R_SEL_D0_P.1 | J_SOM_P3.59 R_SEL_D0_P.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D0_N_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 13 | `DSI_D0_D1_N_SRC` | 必需·差分腿 | J_SOM_P3.63 R_SEL_D1_N.1 | J_SOM_P3.63 R_SEL_D1_N.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D1_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 14 | `DSI_D0_D1_P_SRC` | 必需·差分腿 | J_SOM_P3.65 R_SEL_D1_P.1 | J_SOM_P3.65 R_SEL_D1_P.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D1_N_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 15 | `DSI_D0_D2_N_SRC` | 必需·差分腿 | J_SOM_P3.75 R_SEL_D2_N.1 | J_SOM_P3.75 R_SEL_D2_N.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D2_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 16 | `DSI_D0_D3_N_SRC` | 必需·差分腿 | J_SOM_P3.81 R_SEL_D3_N.1 | J_SOM_P3.81 R_SEL_D3_N.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔); 差分对: DSI_D0_D3_P_SRC | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 17 | `JTAG_TDI` | 必需·单端脚 | J_DEBUG.3 R_JTAG_TDI.2 | J_DEBUG.3 R_JTAG_TDI.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 18 | `LED_G_D` | 必需·单端脚 | D_LED_G.1 R_LED_G.2 | D_LED_G.1 R_LED_G.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 19 | `SPI_MISO_BOOT` | 必需·单端脚 | J_BOOT1.4 R_SER_SPI_MISO.2 | J_BOOT1.4 R_SER_SPI_MISO.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 20 | `SPI_MOSI_BOOT` | 必需·单端脚 | J_BOOT1.3 R_SER_SPI_MOSI.2 | J_BOOT1.3 R_SER_SPI_MOSI.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 21 | `SPI_SCLK_BOOT` | 必需·单端脚 | J_BOOT1.1 R_SER_SPI_SCLK.2 | J_BOOT1.1 R_SER_SPI_SCLK.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 22 | `UART_RX` | 必需·单端脚 | J_SOM_P2.9 J_UART.2 | J_SOM_P2.9 J_UART.2 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |
| 23 | `USB_CC2` | 必需·单端脚 | J_USB_C.B5 R_CC2_D.1 | J_USB_C.B5 R_CC2_D.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (无走线/无过孔) | **红** (零铜 ⇒ 不满足「铜段数≥1 且 铜长>0」) |

★**可悬空 (单列, 不许混进必需表)**

| # | 网名 | 分级 | 期望焊盘集合 | 板面实际焊盘集合 | 实际铜段数 | 实际铜长 mm | 差在哪 | 判定 |
|---|---|---|---|---|---|---|---|---|
| F1 | `FSIN_OUT` | 可悬空 | R_SER_FSIN.1 TP_FSIN.1 | R_SER_FSIN.1 TP_FSIN.1 | 0 | 0.0 | 焊盘集合一致; 零铜 (板侧标 NC 是板那一趟动作) | **绿** (零铜且不在必需表 ⇒ 合 K3) |

### §3.1 · 差分腿成对子表 (★K2 的「成对都有铜」只看这一层, 不自造 Δ 阈值★)

★**来源**: `tools/diff_pair_audit.py` 的 `PAIRS` (22 对) · 与 `HW/check_s8_target_list.py` 的 `pair_partner` 同源。 ★
★**板面现状 [实测]**: 15 条必需差分腿 **全部零铜**; 20 对差分腿里 **11 对尚不是「两腿都有铜」** —— 其中 **7 对是「一腿有铜、一腿零铜」的不对称** (`CSI_D0_D0_P_SRC/N_SRC` · `CSI_D0_D0_P/N` · `CSI_D0_D1_P_SRC/N_SRC` · `CSI_D0_D3_P_SRC/N_SRC` · `CSI_D0_D3_P/N` · `DSI_D0_D2_P_SRC/N_SRC` · `DSI_D0_D3_P_SRC/N_SRC`), **4 对是两腿都零铜** (`CSI_D0_D1_P/N` · `CSI_D0_D2_P/N` · `DSI_D0_D0_P_SRC/N_SRC` · `DSI_D0_D1_P_SRC/N_SRC`) ⇒ ★**这是板那一趟要一起解决的**。 ★

| 差分对 | P 腿 铜段/铜长 mm | N 腿 铜段/铜长 mm | 成对都有铜? |
|---|---|---|---|
| `CSI_D0_CK_P_SRC` / `CSI_D0_CK_N_SRC` | 88 / 32.2 | 103 / 32.2 | ✔ 两腿都有铜 |
| `CSI_D0_CK_P` / `CSI_D0_CK_N` | 229 / 62.9 | 198 / 62.9 | ✔ 两腿都有铜 |
| `CSI_D0_D0_P_SRC` / `CSI_D0_D0_N_SRC` | 151 / 44.4 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `CSI_D0_D0_P` / `CSI_D0_D0_N` | 165 / 41.2 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `CSI_D0_D1_P_SRC` / `CSI_D0_D1_N_SRC` | 116 / 32.8 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `CSI_D0_D1_P` / `CSI_D0_D1_N` | **0 / 0.0** | **0 / 0.0** | ✘ 两腿都零铜 |
| `CSI_D0_D2_P_SRC` / `CSI_D0_D2_N_SRC` | 49 / 14.0 | 31 / 14.0 | ✔ 两腿都有铜 |
| `CSI_D0_D2_P` / `CSI_D0_D2_N` | **0 / 0.0** | **0 / 0.0** | ✘ 两腿都零铜 |
| `CSI_D0_D3_P_SRC` / `CSI_D0_D3_N_SRC` | 46 / 15.0 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `CSI_D0_D3_P` / `CSI_D0_D3_N` | 301 / 81.1 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `DSI_D0_CK_P_SRC` / `DSI_D0_CK_N_SRC` | 330 / 83.8 | 312 / 83.8 | ✔ 两腿都有铜 |
| `DSI_D0_CK_P` / `DSI_D0_CK_N` | 299 / 84.1 | 297 / 88.7 | ✔ 两腿都有铜 |
| `DSI_D0_D0_P_SRC` / `DSI_D0_D0_N_SRC` | **0 / 0.0** | **0 / 0.0** | ✘ 两腿都零铜 |
| `DSI_D0_D0_P` / `DSI_D0_D0_N` | 300 / 81.0 | 18 / 4.8 | ✔ 两腿都有铜 (★铜长严重不对称 76.2mm · 阈值未裁·见 §5-①★) |
| `DSI_D0_D1_P_SRC` / `DSI_D0_D1_N_SRC` | **0 / 0.0** | **0 / 0.0** | ✘ 两腿都零铜 |
| `DSI_D0_D1_P` / `DSI_D0_D1_N` | 311 / 79.5 | 300 / 78.3 | ✔ 两腿都有铜 (★Δ1.2mm★) |
| `DSI_D0_D2_P_SRC` / `DSI_D0_D2_N_SRC` | 372 / 95.8 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `DSI_D0_D2_P` / `DSI_D0_D2_N` | 617 / 168.7 | 608 / 168.7 | ✔ 两腿都有铜 |
| `DSI_D0_D3_P_SRC` / `DSI_D0_D3_N_SRC` | 250 / 66.3 | **0 / 0.0** | ✘ **不对称** (N 腿零铜) |
| `DSI_D0_D3_P` / `DSI_D0_D3_N` | 252 / 142.2 | 402 / 142.2 | ✔ 两腿都有铜 |

★**本闸 (K2) 只判「成对都有铜」, 不判 Δ铜长 / Δ段数** ⇒ ★**Δ 阈值 main 未裁 (见 §5-①), 本单不代拍**。 ★

---

## §4 · 三种刷法逐条给机器判据 (★不许写「应该能防」这种没有判据的句子★)

★**证据等级: 本段 = [实测] (三种反例在本单新建的闸里实跑, 判红结果见下表与 `--selftest` 输出) + [推算] (代价推导) ★**

| # | 刷法 | ★计数口径 (unc 45→0) 会怎么被骗★ | ★逐条口径 (本闸) 怎么抓住 —— 机器判据★ |
|---|---|---|---|
| ① | ★**删网 / 删焊盘**: 把某条必需网的 pad 从板上删掉 | ★ratsnest 消失 ⇒ unc 计数下降 ⇒ 45 可以被刷到 0 ⇒ ★**但这条网从此【不在板上】/ 少一个焊盘** ★ | ★**K1a 身份**: 名单里的网名必须在板面存在 ⇒ 查不到 ⇒ **红, 点名该网 + 写清「板面查不到」**。★ **K1b 焊盘集合**: 脚表期望的每个焊盘必须在板面 ⇒ 少一个 ⇒ **红, 点名该网 + 写清「缺哪个焊盘」**。 ★ |
| ② | ★**标 NC / no-connect**: 把必需网的 pad 标成不连 | ★unc 不再报 ⇒ 计数下降 ⇒ 45 可以被刷到 0 ⇒ ★**但这条网从此【被声明为不接】** ★ | ★**K1c 铜状态**: 必需网必须 `铜段数 ≥ 1` 且 `铜长 > 0` ⇒ NC 的网铜段数仍是 0 ⇒ **红, 点名该网 + 写清「零铜」**。★ **K3**: 可悬空名单里的网若混进必需表 ⇒ **红**。 ★ |
| ③ | ★**改名 / 拆网**: 必需网被改名成别的网名 | ★老网名消失、新网名不在必需名单里 ⇒ 计数下降 ⇒ 45 可以被刷到 0 ⇒ ★**但必需名单上那条【依然是零铜】** ★ | ★**K1a 身份**: K1 拿【名单里的网名】去板面查 ⇒ 查不到 ⇒ **红, 点名「名单里这条在板面查不到」**。★ **K5 交叉核对**: 板上多出的网名逐个点名。 ★ |

★**「零假连通」闸 (K4) 的命门**: ★**构造一个「unc 归零但必需网仍无铜」的反例 ⇒ 闸必须判红并点名** ⇒ 本闸用【合成字典 + 纯判定函数】实现 (★不必真去改板★), 三种刷法各一个反例, 见 `SW/tools/check_sw_false_connectivity_gate.py --selftest` (★末行 `ALL TESTS PASS`★)。 ★

★**★本单额外做了【真板副本层】的端到端验证 (★比合成字典更硬★)★**: ★**把真板复制到沙盒, 逐个施加三种刷法, 再用 `SW/tools/check_sw_false_connectivity_gate.py --board <沙盒副本> --phase post` 实跑** ⇒ ★**三种刷法全部被抓住并点名** ★

| 刷法 | 沙盒副本 | 闸 rc | 闸点名的行 |
|---|---|---|---|
| ① 删焊盘 | `tmp/iss381_sbx/cheat/cheat1_delete_pad.kicad_pcb` | **1** (红) | ★**`UART_RX` ⇒ K1b: 缺期望焊盘 (1 个): `J_UART.2`; K1c: 零铜 ⇒ 这条网【没接】** ★ |
| ② 标 NC | `tmp/iss381_sbx/cheat/cheat2_nc.kicad_pcb` | **1** (红) | ★**`UART_RX` ⇒ K1a: 板面查不到该网 (身份缺失)** ★ |
| ③ 改名 / 拆网 | `tmp/iss381_sbx/cheat/cheat3_rename.kicad_pcb` | **1** (红) | ★**`UART_RX` ⇒ K1a: 板面查不到该网 (身份缺失)** ★ |

★**⇒ 三种刷法在【真板文件层】也一条不落地被抓住并点名** ⇒ ★**闸不是只在合成字典上绿** ⇒ 证据等级 [实测] (★`logs/iss381/e2e_cheat_proof.txt`★)。 ★

---

## §5 · 未决项 (★只登记 · 不代拍 · 不代 main 裁决★)

| # | 要谁回答什么 | 本单给了什么事实 | 证据等级 |
|---|---|---|---|
| ① | ★**to=main**: 差分腿**铜长对称性阈值** (Δ铜长 / Δ段数上限) 裁不裁 · 裁多少 —— `iss334_need4a` 一线只裁了分级, 没裁对称性 | ★本闸 K2 **只判「成对都有铜」**, 不自造 Δ 阈值; §3.1 已把 20 对的实测 Δ 铜长全部列出 (★最大一对: `DSI_D0_D0_P/N` Δ=76.2mm, 两腿都有铜但严重不对称⇒ **有铜 ≠ 对称**★) | [实测] (板面读数) / [推算] (归纳) |
| ② | ★**to=main**: 「删网 / 标 NC / 改名」三种刷法**该不该被允许** (★例: `FSIN_OUT` 已被明确登记为「板侧标 NC 是板那一趟动作」⇒ 说明项目里**已有**先例允许 NC★) | ★本单给三条机器判据 (K1a/K1b/K1c/K5) + 三条刷法的代价 (计数可被骗 ⇒ unc 计数单独用 = 假连通); ★**本单不裁「允不允许」** | [实测] (刷法构造与判红结果) |
| ③ | ★**to=main**: 新闸 `SW/tools/check_sw_false_connectivity_gate.py` **挂不挂 `state/gate_check.py`** | ★**本单零挂链** (`grep -c check_sw_false_connectivity_gate state/gate_check.py` ⇒ 0) ⇒ 挂链是 main 的地界; ★**先例**: ISS-300/309/312/315 + ISS-372 U7 同款 —— 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」 | [实测] (grep 输出) / [推算] (先例归纳) |
| ④ | ★**to=main**: 本页 §2 的口径订正块**要不要落进 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 末尾** | ★**本单零碰既有页面正文** (该页 md5 `0f4bf6c083f25cea6cda240a91170049` 开工前后逐字相同) ⇒ 落不落归 main | [实测] (md5 对照) |
| ⑤ | ★**to=main**: 「板那一趟」的布线验收线正式改成【**逐条列铜**】还是【**计数 + 逐条 双轨**】 | ★**选项 A (逐条列铜单轨)**: 23 条必需网逐条有铜 + 焊盘集合一致 + 差分成对 ⇒ 假连通空间最小 ⇒ ★代价: 板那一趟每加/减一条网都要改名单, 且 **unc 计数降到 0 之后本闸仍然红** (因为还有别的网悬空)。★**选项 B (双轨)**: 保留 unc 45→0 作【覆盖度指标】, 另加本闸作【身份闸】 ⇒ ★代价: 两套判据两套 rc, 现场要解释「哪个红」⇒ 但两个数字都不说谎。★**本单给两个选项 + 代价, 不代拍** | [推算] (代价推导) / [实测] (两套判据的实跑结果) |

★**另: 本页 §3 的「期望焊盘集合」口径有一处需要 main 知悉 (不构成未决项)**: 脚表 `HW/netlist_v1_pins.csv` 里 `USB_CC2` 同时存在 `J_TYPE_C.B5` / `R_CC2.1` 两行 (`board=CHG_BOARD`) 与 `J_USB_C.B5` / `R_CC2_D.1` 两行 (`board=MAIN_PCB`) ⇒ ★**本闸只认 `board ∈ {空, MAIN_PCB}` 的行 ⇒ 期望集合 = `J_USB_C.B5 R_CC2_D.1` ⇒ 与板面完全一致** ⇒ ★**主板侧无差异; 充电板侧的 `J_TYPE_C` / `R_CC2` 不进主板闸**。 ★

---

## §6 · 复跑命令 (★每个数都能自己跑出来★)

★**证据等级: 本段 = [实测] (★下列命令均在本机实跑过·rc 已贴进交卷页★) ★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── §1 板面真值 ──
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb      # ★含 N' / violations / 分级自检 / 逐条 unc 网名

# ── §2 口径订正 (UART_RX 是不是被 unc 数的) ──
python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb | grep -E 'N'"'"' = |UART_RX|violations'

# ── §3 逐条列铜表 ──
python3 SW/tools/check_sw_false_connectivity_gate.py --print-table       # ★23 必需 + 1 可悬空, 逐条列铜★
python3 SW/tools/check_sw_false_connectivity_gate.py --print-net UART_RX
python3 SW/tools/check_sw_false_connectivity_gate.py --print-net UART_TX

# ── 闸本身 ──
python3 SW/tools/check_sw_false_connectivity_gate.py                      # ★默认 --phase pre (基线相) ⇒ rc=0
python3 SW/tools/check_sw_false_connectivity_gate.py --phase post         # ★板那一趟验收相 ⇒ 今天的板 rc=1, 逐条点名★
python3 SW/tools/check_sw_false_connectivity_gate.py --selftest           # ★末行 ALL TESTS PASS

# ── §6 复跑命令 (★每个数都能自己跑出来★) ──
# ★端到端决定性实验 (★沙盒副本·真板零写·★只在项目盘内跑★) ★
python3 tmp/iss381_sbx/e2e_count_vs_identity.py   # ★unc 45 → 20 而铜 +0.0mm★
python3 tmp/iss381_sbx/e2e_cheat_proof.py          # ★三刷法在真板副本层全被抓住并点名★

# ── 零挂链 / 零改既有闸 ──
grep -c check_sw_false_connectivity_gate state/gate_check.py             # ⇒ 0
md5sum HW/check_s8_target_list.py HW/check_board_comparable_gate.py \
       state/compare_arm_official.py \
       SW/tools/check_sw_zero_copper_grade_consistency.py \
       SW/tools/check_onepass_sw_release.py \
       SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md
```

★**板面读数的原始来源 (★上一趟已落盘 · 本趟不重跑探针★)**: `tmp/iss381_sbx/board_nets.json` (自写 s-expr 解析器口径) · `tmp/iss381_sbx/board_nets_pcbnew.json` (pcbnew API 口径) ⇒ ★**两份互为对照, 由 K2 强制一致**。 ★

---

## §7 · 边界自证 (★零写板 · 零落表 · 零改既有闸 · 零挂链 · 零外发★)

★**证据等级: 本段 = [实测] (★开工前后两次 md5 对照·结果逐条贴出★) ★**

| 边界 | 自证方式 | 结果 |
|---|---|---|
| ★零写板★ | 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 开工前后对照 `logs/iss381/baseline_fingerprints.txt` | ★**逐字相同** (开工前 / 交卷后两次实测输出见 `logs/iss381/boundary_proof.txt`) ★ |
| ★零落表★ | `HW/netlist_v1.csv` `6aee500e…` / `HW/netlist_v1_pins.csv` `9174309d…` / `HW/BOM_v1.csv` `5b999399…` 前后对照 | ★**逐字相同** ★ |
| ★零改既有闸★ | 5 个既有闸 md5 (`2fefaaea…` / `386cda8f…` / `1471bce6…` / `58a3aa44…` / `4d7ce982…`) 前后对照 | ★**逐字相同** ★ |
| ★零改既有页面正文★ | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` md5 `0f4bf6c083f25cea6cda240a91170049` 前后对照 | ★**逐字相同** ★ |
| ★零挂链★ | `grep -c check_sw_false_connectivity_gate state/gate_check.py` | ★**0**★ |
| ★零外发★ | 本单**未发出任何邮件 / 询价 / 问询 / 采购**; 厂商资料一律自己查 + 标证据等级 | ★**零外发**★ |
| ★不自签 issue_log / 不写别人的分片★ | `state/issue_log.yaml` mtime `2026-11-24 07:19:15` (★早于本单任何写入★) · 只写 `state/fragments/sw.yaml` (走 `state/frag_write.py --agent sw-lead` 的原子写) · `hw.yaml` / `mech.yaml` / `pm.yaml` 三个 md5 本单未动 | ★**合规** ★ |
| ★沙盒只落 tmp/iss381_sbx/ + logs/iss381/★ | 未写系统 `/tmp`; 未用 `cp -al` 造副本 (★L-24 硬规矩★) | ★**合规** ★ |

---

> ★**证据等级约定**: `[实测]` = 本机实跑读数 (可按 §6 复现) · `[推算]` = 由实测归纳 · `[官网]`/`[媒体]` = 外部来源 · `[0数据]` = 无数据 ★
> ★**本页不含任何未标等级的断言** (由闸 K6 强制) ★
