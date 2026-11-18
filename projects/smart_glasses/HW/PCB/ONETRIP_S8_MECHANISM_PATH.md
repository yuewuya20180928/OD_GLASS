# ONETRIP S8 · 机制级「换机制」路线 (ISS-334)

> 单号: **ISS-334** · 角色: **硬件总工 (hw-lead)** · 日期: **2026-11-18**
> 文档性质: ★**纯分析 + 作业包** ★ — 零写板 / 零落表 / 零改闸 / 零改生成器代码 / 零外发
> 本文件是 ISS-334 本单**新建件**, **不修改任何既有文档正文**。
> ★本单回答的唯一问题: ★**官方板上「≥2 焊盘但一根铜都没有」的 24 个网, 死因分别是什么, 换什么机制才可能救回来** ★

---

## §0 口径与边界自证

### §0-1 边界承诺表 (★本单实测自证★)

| 边界项 | 本单承诺 | 核验方式 / 证据 |
|---|---|---|
| ★**零写板** ★ | `HW/PCB/demo_mainboard.kicad_pcb` 字节不动 | md5 恒为 `611b869e13518c3c023fb178f91a0075` · mtime 恒为 `2026-11-06 07:07:17.362193413` (★交卷前后各读一次★) |
| ★**零落表** ★ | 网表 / 脚表 / BOM / 原理图真源一个字节不许动 | 本单只写 `HW/PCB/ONETRIP_S8_MECHANISM_PATH.md` · `HW/PCB/BOARD_ONEPASS_S8_MECHANISM_ACTIONS.md` · `HANDOFF/2026-11-18_hw-lead_ISS334_机制级换机制路线.md` · `state/fragments/hw.yaml` (走 `frag_write.py`) |
| ★**零改闸** ★ | `state/gate_check.py` / `state/compare_arm_official.py` / `state/check_pcb_drc.py` / `state/check_pcb_nets.py` 一律只读 | 只以 `--self-test` / 只读模式调用 (§6 逐字命令) |
| ★**零改生成器代码** ★ | `state/gen_*.py` / `state/patch_*.py` / `state/fix_*.py` 只许读 | 本单只读不写 (§0-3 指纹表) |
| ★**沙盒只写 `tmp/iss334/`** ★ | 沙盒产物一律落 `tmp/iss334/` · 机器原始输出落 `logs/iss334/` | §0-4 清单 |
| ★**零外发** ★ | 不发邮件 / 询价 / 问询 / 采购 | 老板 2026-11-11 19:31 + 2026-11-12 02:02 明令不再发信 ⇒ **没有「批一句可以发」这个选项** |
| ★**不替老板 / main 拍板** ★ | 每条 need 给「问法 + 谁答 + 不答后果 + 建议默认值 + 建议排期」 | §5 一条都不自己定 |
| ★**不自签 `state/issue_log.yaml`** ★ | 本单零写入 issue_log | 只走 `state/frag_write.py --agent hw-lead` |

### §0-2 ★本单为什么是「机制级」而不是「布局级」★

| ★已死的两条处方★ | ★判决 (★出处★) | ★对本单的含义★ |
|---|---|---|
| ★ISS-325 左上臂 (挪 `R_SEL_*` 到左上) ★ | ★**REJECT**: 退铜 4 + 差分死腿 1 对 + 逐网孤岛 +9 | `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` §7 |
| ★ISS-328 右上臂 (挪 `R_SEL_*` 到右上) ★ | ★**REJECT**: 退铜 2 + 逐网孤岛 +7 + 段数 3,986 vs 官方 18,092 ⇒ **不可比** | `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` §3 |

⇒ ★**「挪器件位置」两个方向都死了** ⇒ 归零只剩三条路: **(a) 机制级 (本单)** / **(b) 老板口径 (W-2 / W-1c / A4 / W-3 / U-1 / P7 等那 8 个字母)** / **(c) 路由器本体**。
⇒ ★**本单 = (a) 的前三件: 清单 + 归类 + 臂设计 + 作业包** ★

### §0-3 ★工具指纹 (★零改生成器代码的自证★)

★本单全程只读这些文件, 指纹 (sha256 前 16 位) 交卷时复比:

| 文件 | 用途 (只读) |
|---|---|
| `state/gen_pcb_routing.py` | 路由器本体 (★桶 C 的修在产生点的位置★) |
| `state/pair_corridor.py` | 成对走廊机制 (★桶 A★) |
| `state/analyze_escape_dirs.py` · `state/probe_escape_feasibility.py` | 出脚方向可行性 (★桶 B 的判据工具★) |
| `state/patch_astar_gated.py` · `state/fix_unconnected_astar.py` · `state/fix_board_rip_guarded.py` | A* 补线三件 (★桶 C★) |
| `state/compare_arm_official.py` · `state/pair_copper_table.py` · `state/check_pcb_drc.py` | 名单制闸 + 逐对铜长 + DRC (★只读★) |

### §0-4 ★本单机器原始输出清单 (★`logs/iss334/` + `tmp/iss334/`★)

| 文件 | 内容 |
|---|---|
| `logs/iss334/01_check_pcb_drc.log` | ★官方板 fresh DRC 门禁 (rc=0 · viol 0 · unc 45) ★ |
| `logs/iss334/00_official_drc_fresh.json` | ★fresh DRC JSON (viol 0 / unc 45) ★ |
| `logs/iss334/02_pair_copper_table.txt` | ★逐对铜长 (22 对) ★ |
| `logs/iss334/03_worklist.log` + `tmp/iss334/01_worklist.md` | ★官方板未连接工作表 (三类分法) ★ |
| `logs/iss334/04_zero_copper_probe.log` + `tmp/iss334/02_zero_copper_nets.{md,json}` | ★零铜网 0 号清单 (本单自写只读探针) ★ |
| `logs/iss334/05_escape_feasibility.log` + `tmp/iss334/03_escape_feasibility.txt` | ★出脚方向可行性 (88 端点) ★ |
| `logs/iss334/07_escape_dirs.log` + `tmp/iss334/04_escape_dirs.{txt,json}` | ★出脚方向分配 CSP (冲突图 + 可满足性) ★ |
| `logs/iss334/06_astar_try.log` + `tmp/iss334/05_astar_try.kicad_pcb` | ★A* 补线实测 (粗网格 + margin 0.20 档) ★ |
| `logs/iss334/08_astar_officialenv.log` + `tmp/iss334/06_astar_officialenv.kicad_pcb` | ★A* 补线实测 (官方同配方 GRID=0.125 / margin 0.0625) ★ |

---

## §1 零铜网 0 号清单 (★fresh 机器读数 · 2026-11-18 23:59~2026-11-19 00:1x 本机实跑★)

### §1-1 口径 (★逐字对齐名单制闸的零铜定义★)

★**零铜网** := ★**该网在板上的焊盘数 ≥ 2 且该网的走线段数 = 0** ★
★这是 ★**`state/compare_arm_official.py` 里 `zero_copper` 指标的逐字定义** (`pad_cnt[net] >= 2 and net_seg.get(net, 0) == 0`) ⇒ ★**本单不另造口径** ★
★**空网名 (KiCad net 0) 不计** —— ★官方闸用 `(net "名")` 正则解析, net 0 写成 `(net 0 "")` ⇒ 天然不计入; 本单探针按 pcbnew 取名会把 net 0 取成空串 ⇒ ★**已显式剔除** ★

★**基线读数 (fresh)** ★:

| 项 | 读数 | 出处 |
|---|---|---|
| 官方板 md5 / mtime | `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` | §0-1 |
| DRC violations | **0** | `logs/iss334/01_check_pcb_drc.log` |
| DRC unconnected items | **45** | 同上 |
| 走线段 / 过孔 | **18,092 段 / 433 孔** | `tmp/iss334/02_zero_copper_nets.md` 首行 |
| 焊盘 / 网名 | 834 / 137 | 同上 |
| ★**零铜网 (pad≥2 且 段=0, 剔空网名)** ★ | ★**24 个** ★ | 同上 |
| ★其中落在 DRC 未连接网里★ | ★**24 / 24 (100%)** ★ | 同上 |
| 官方板未连接网总数 | 43 网 (整网无铜 24 · 局部未通 17 · 端点缝 2) | `tmp/iss334/01_worklist.md` 汇总行 |
| ★差分对腿状态 (22 对)★ | 双边有铜 11 · ★**N 边零铜 7** ★ · ★**双边零铜 4** ★ | `logs/iss334/02_pair_copper_table.txt` |

### §1-2 ★零铜网 0 号清单 (★24 条 · 端点含 ref+pad+坐标+层★)★

| 网名 | 焊盘 | 段 | 过孔 | 铜长 mm | 类别 | 端点 (ref.pad @ 坐标 层) | 差分伙伴腿状态 |
|---|---|---|---|---|---|---|---|
| `CAM_RESET_N` | 2 | 0 | 0 | 0.00 | 整网无铜 | CONN_CAM.27 @ (91.90, 51.40) F.Cu; J_SOM_P1.54 @ (58.40, 11.04) F.Cu | — (非差分腿) |
| `CSI_D0_D0_N` | 3 | 0 | 0 | 0.00 | 整网无铜 | TP_CSI_D0_N.1 @ (63.70, 55.20) F.Cu; CONN_CAM.14 @ (85.40, 51.40) F.Cu; C_AC_CSI_D0_D0_N.2 @ (65.10, 58.60) F.Cu | `CSI_D0_D0_P` = 41.217mm ⇒ 伙伴腿有铜 (41.217mm) |
| `CSI_D0_D0_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_SOM_P4.65 @ (22.00, 50.96) F.Cu; C_AC_CSI_D0_D0_N.1 @ (63.50, 58.60) F.Cu | `CSI_D0_D0_P_SRC` = 44.366mm ⇒ 伙伴腿有铜 (44.366mm) |
| `CSI_D0_D1_N` | 2 | 0 | 0 | 0.00 | 整网无铜 | CONN_CAM.11 @ (83.90, 51.40) F.Cu; C_AC_CSI_D0_D1_N.2 @ (55.50, 58.60) F.Cu | `CSI_D0_D1_P` = 0.000mm ⇒ ★双边零铜 |
| `CSI_D0_D1_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_SOM_P4.71 @ (20.80, 50.96) F.Cu; C_AC_CSI_D0_D1_N.1 @ (53.90, 58.60) F.Cu | `CSI_D0_D1_P_SRC` = 32.832mm ⇒ 伙伴腿有铜 (32.832mm) |
| `CSI_D0_D1_P` | 2 | 0 | 0 | 0.00 | 整网无铜 | C_AC_CSI_D0_D1_P.2 @ (50.70, 58.60) F.Cu; CONN_CAM.12 @ (84.40, 51.40) F.Cu | `CSI_D0_D1_N` = 0.000mm ⇒ ★双边零铜 |
| `CSI_D0_D2_N` | 2 | 0 | 0 | 0.00 | 整网无铜 | CONN_CAM.5 @ (80.90, 51.40) F.Cu; C_AC_CSI_D0_D2_N.2 @ (21.90, 58.60) F.Cu | `CSI_D0_D2_P` = 0.000mm ⇒ ★双边零铜 |
| `CSI_D0_D2_P` | 2 | 0 | 0 | 0.00 | 整网无铜 | CONN_CAM.6 @ (81.40, 51.40) F.Cu; C_AC_CSI_D0_D2_P.2 @ (17.10, 58.60) F.Cu | `CSI_D0_D2_N` = 0.000mm ⇒ ★双边零铜 |
| `CSI_D0_D3_N` | 2 | 0 | 0 | 0.00 | 整网无铜 | CONN_CAM.2 @ (79.40, 51.40) F.Cu; C_AC_CSI_D0_D3_N.2 @ (12.30, 58.60) F.Cu | `CSI_D0_D3_P` = 81.117mm ⇒ 伙伴腿有铜 (81.117mm) |
| `CSI_D0_D3_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | C_AC_CSI_D0_D3_N.1 @ (10.70, 58.60) F.Cu; J_SOM_P4.89 @ (17.20, 50.96) F.Cu | `CSI_D0_D3_P_SRC` = 15.019mm ⇒ 伙伴腿有铜 (15.019mm) |
| `DSI_D0_D0_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D0_N.1 @ (78.90, 5.60) F.Cu; J_SOM_P3.57 @ (23.60, 7.96) F.Cu | `DSI_D0_D0_P_SRC` = 0.000mm ⇒ ★双边零铜 |
| `DSI_D0_D0_P_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D0_P.1 @ (83.70, 5.60) F.Cu; J_SOM_P3.59 @ (23.20, 7.96) F.Cu | `DSI_D0_D0_N_SRC` = 0.000mm ⇒ ★双边零铜 |
| `DSI_D0_D1_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D1_N.1 @ (88.50, 5.60) F.Cu; J_SOM_P3.63 @ (22.40, 7.96) F.Cu | `DSI_D0_D1_P_SRC` = 0.000mm ⇒ ★双边零铜 |
| `DSI_D0_D1_P_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D1_P.1 @ (93.30, 5.60) F.Cu; J_SOM_P3.65 @ (22.00, 7.96) F.Cu | `DSI_D0_D1_N_SRC` = 0.000mm ⇒ ★双边零铜 |
| `DSI_D0_D2_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D2_N.1 @ (107.70, 5.60) F.Cu; J_SOM_P3.75 @ (20.00, 7.96) F.Cu | `DSI_D0_D2_P_SRC` = 95.787mm ⇒ 伙伴腿有铜 (95.787mm) |
| `DSI_D0_D3_N_SRC` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SEL_D3_N.1 @ (117.30, 5.60) F.Cu; J_SOM_P3.81 @ (18.80, 7.96) F.Cu | `DSI_D0_D3_P_SRC` = 66.275mm ⇒ 伙伴腿有铜 (66.275mm) |
| `FSIN_OUT` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_SER_FSIN.1 @ (93.30, 46.60) F.Cu; TP_FSIN.1 @ (93.50, 49.60) F.Cu | — (非差分腿) |
| `JTAG_TDI` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_JTAG_TDI.2 @ (142.90, 42.60) F.Cu; J_DEBUG.3 @ (143.20, 56.60) F.Cu | — (非差分腿) |
| `LED_G_D` | 2 | 0 | 0 | 0.00 | 整网无铜 | R_LED_G.2 @ (7.50, 62.60) F.Cu; D_LED_G.1 @ (100.80, 56.60) F.Cu | — (非差分腿) |
| `SPI_MISO_BOOT` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_BOOT1.4 @ (125.70, 56.60) F.Cu; R_SER_SPI_MISO.2 @ (104.50, 46.60) F.Cu | — (非差分腿) |
| `SPI_MOSI_BOOT` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_BOOT1.3 @ (125.20, 56.60) F.Cu; R_SER_SPI_MOSI.2 @ (109.30, 46.60) F.Cu | — (非差分腿) |
| `SPI_SCLK_BOOT` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_BOOT1.1 @ (124.20, 56.60) F.Cu; R_SER_SPI_SCLK.2 @ (114.10, 46.60) F.Cu | — (非差分腿) |
| `UART_RX` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_UART.2 @ (19.14, 68.60) F.Cu; J_SOM_P2.9 @ (67.20, 50.96) F.Cu | — (非差分腿) |
| `USB_CC2` | 2 | 0 | 0 | 0.00 | 整网无铜 | J_USB_C.B5 @ (141.75, 5.25) F.Cu; R_CC2_D.1 @ (126.90, 42.60) F.Cu | — (非差分腿) |

### §1-3 ★一句话结论 (★零铜网 N 个 = 哪几个网名★)

★★**零铜网 = 24 个** ★★ = 
`CAM_RESET_N` · `CSI_D0_D0_N` · `CSI_D0_D0_N_SRC` · `CSI_D0_D1_N` · `CSI_D0_D1_N_SRC` · `CSI_D0_D1_P` · `CSI_D0_D2_N` · `CSI_D0_D2_P` · `CSI_D0_D3_N` · `CSI_D0_D3_N_SRC` · `DSI_D0_D0_N_SRC` · `DSI_D0_D0_P_SRC` · `DSI_D0_D1_N_SRC` · `DSI_D0_D1_P_SRC` · `DSI_D0_D2_N_SRC` · `DSI_D0_D3_N_SRC` · `FSIN_OUT` · `JTAG_TDI` · `LED_G_D` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` · `UART_RX` · `USB_CC2`

★★**这 24 个网 = 24 根"一根铜都没有的差分腿或单端网" ⇒ 它们连铜都不存在 ⇒ 让路闸 / 挪器件 / 换层绕行 对它们【一点用都没有】(让路闸只能让别的网让路, 不能凭空长铜) ⇒ ★必须换机制★** ★

### §1-4 ★零铜网的两个子集 (★归桶用★)

| 子集 | 数量 | 网名 | 机器判据 |
|---|---|---|---|
| ★**A 子集: 差分腿且【伙伴腿官方有铜】** ★ | **7** | `CSI_D0_D0_N` · `CSI_D0_D0_N_SRC` · `CSI_D0_D1_N_SRC` · `CSI_D0_D3_N` · `CSI_D0_D3_N_SRC` · `DSI_D0_D2_N_SRC` · `DSI_D0_D3_N_SRC` | `logs/iss334/02_pair_copper_table.txt` 里该对 P 腿铜长 > 0 而 N 腿 = 0.000 |
| ★**B 子集: 差分腿且【伙伴腿也零铜】(整对没布出来)** ★ | **8** | `CSI_D0_D1_N` · `CSI_D0_D1_P` · `CSI_D0_D2_N` · `CSI_D0_D2_P` · `DSI_D0_D0_N_SRC` · `DSI_D0_D0_P_SRC` · `DSI_D0_D1_N_SRC` · `DSI_D0_D1_P_SRC` | 同表两腿均 0.000 |
| ★**C 子集: 非差分单端网** ★ | **9** | `CAM_RESET_N` · `FSIN_OUT` · `JTAG_TDI` · `LED_G_D` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` · `UART_RX` · `USB_CC2` | 不在 22 对差分清单内 |

★★**注意 (★这一点决定了 ISS-325/ISS-328 为什么必然失败★)**: ★**24 个零铜网里, 有 15 个是差分腿 (A 7 + B 8), 9 个是单端网** ⇒
★**"挪 `R_SEL_*` 器件位置" 只碰得到 B 子集里的 `DSI_D0_D0_*_SRC` / `DSI_D0_D1_*_SRC` (4 个) 和 A 子集里的 `DSI_D0_D2_N_SRC` / `DSI_D0_D3_N_SRC` (2 个)** ⇒
★★**剩下 18 个零铜网 (`CSI_*` 9 个 + `CONN_CAM`/`CONN_LIGHT` 侧 + 9 个单端网) 跟 `R_SEL_*` 的位置毫无关系 ⇒ ⇒ 布局级处方从原理上就不可能覆盖 24 个里的 18 个** ★★

---

## §2 逐网死因归类 (★三桶 · 每条零铜网只归一个桶★)

### §2-1 ★归桶规则 (★判据全部来自机器读数, 不许写「看起来像」★)

★**机器读数 1 (出脚可行性)**: `state/probe_escape_feasibility.py` 对官方板 **88 个端点**逐个算「4 方向 × 4 长度 × 2 线宽」的出脚直道净距余量
⇒ ★**W=0.20 ⇒ 物理可行 88 / 88 · W=0.15 ⇒ 物理可行 88 / 88 · 物理不可能 0** ★ (`tmp/iss334/03_escape_feasibility.txt` 汇总)
⇒ ★**结论 1: 没有任何一个端点是「几何上完全走不出去」** ★

★**机器读数 2 (出脚方向分配 CSP)**: `state/analyze_escape_dirs.py` ⇒ ★**出脚方向分配机制几何可行性 = 可行** ★ (`tmp/iss334/04_escape_dirs.txt` 末行)
⇒ ★**结论 2: 不是「方向分配不出来」** ★

★**机器读数 3 (A* 补线实测 · 官方同配方)**: `PCB_GRID=0.125 PCB_HALO_MARGIN=0.0625` 下跑 `state/fix_unconnected_astar.py` ⇒
★★**补上 0 条 / 未成 45 条** ★★ (`logs/iss334/08_astar_officialenv.log`) ⇒ ★**产物板 md5 与官方板逐字节相同 (零铜没落) ★★
⇒ ★**结论 3: 路由器本体在【成品板】上对这 45 条全都找不到路** ★

★**机器读数 4 (逐对铜长)**: 22 对里 ★**11 对至少一腿零铜 (7 个 N 边零铜 + 4 个双边零铜)** ★ (`logs/iss334/02_pair_copper_table.txt`)

★**由此得到的三桶判据 (★按顺序判定, 命中即停 ⇒ 每条网只归一个桶★)** ★:

| 顺序 | 桶 | 判据 (★机器可复核★) |
|---|---|---|
| 1 | **A 成对走廊** | 该网是差分腿 **且** 伙伴腿在官方板上有铜 (铜长 > 0) ⇒ 走廊被占 |
| 2 | **B 换层绕开** | 非 A **且** 该网**最紧端点**的最优出脚余量 **≤ +0.30mm** ⇒ 出脚被几何钉死 (4 个方向都没余量) |
| 3 | **C 路由器本体** | 非 A **且** 非 B ⇒ 出脚余量 ≥ +0.30mm 而 A* 仍找不到路 ⇒ 是搜索失败 |

★**阈值 +0.30mm 的来历 (★不是拍脑袋★)**: 出脚探针的余量 = ★**实测净距 − 板规则净距 0.20mm** ★; 官方板路由器网格步长 0.125mm
⇒ ★**余量 ≤ +0.30mm ⇒ 可选出脚格 ≤ 2 个 ⇒ 路由器在该端点没有自由度 ⇒ 归 B; 余量 ≥ +0.30mm ⇒ 端点不是瓶颈 ⇒ 归 C** ★

### §2-2 ★逐网归类表 (★24 条 · 全表机器生成 · `tmp/iss334/gen_sec2.py`★)★

| 网名 | 桶 | 归桶依据 (机器读数 + 出处) | 最小可试机制 (逐字) | 反向用例 (什么读数能证明这条路不通) |
|---|---|---|---|---|
| `CAM_RESET_N` | **B** | 最紧端点 J_SOM_P1.54 的最优出脚余量仅 **0.025mm** (阻挡物 `J_SOM_P1.52` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="CAM_RESET_N"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `CSI_D0_D0_N` | **A** | 差分腿且**伙伴腿官方有铜 41.217mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 CONN_CAM.14 的最优出脚余量 0.075mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair CSI_D0_D0_P CSI_D0_D0_N` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `CSI_D0_D0_N_SRC` | **A** | 差分腿且**伙伴腿官方有铜 44.366mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 J_SOM_P4.65 的最优出脚余量 0.025mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair CSI_D0_D0_P_SRC CSI_D0_D0_N_SRC` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `CSI_D0_D1_N` | **B** | 最紧端点 CONN_CAM.11 的最优出脚余量仅 **0.075mm** (阻挡物 `F.Cu` @ 0.275mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="CSI_D0_D1_N"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `CSI_D0_D1_N_SRC` | **A** | 差分腿且**伙伴腿官方有铜 32.832mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 J_SOM_P4.71 的最优出脚余量 0.025mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair CSI_D0_D1_P_SRC CSI_D0_D1_N_SRC` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `CSI_D0_D1_P` | **B** | 最紧端点 CONN_CAM.12 的最优出脚余量仅 **0.075mm** (阻挡物 `F.Cu` @ 0.275mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="CSI_D0_D1_P"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `CSI_D0_D2_N` | **B** | 最紧端点 CONN_CAM.5 的最优出脚余量仅 **0.087mm** (阻挡物 `CONN_CAM.4` @ 0.287mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="CSI_D0_D2_N"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `CSI_D0_D2_P` | **B** | 最紧端点 CONN_CAM.6 的最优出脚余量仅 **0.087mm** (阻挡物 `CONN_CAM.5` @ 0.287mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="CSI_D0_D2_P"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `CSI_D0_D3_N` | **A** | 差分腿且**伙伴腿官方有铜 81.117mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 CONN_CAM.2 的最优出脚余量 0.087mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair CSI_D0_D3_P CSI_D0_D3_N` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `CSI_D0_D3_N_SRC` | **A** | 差分腿且**伙伴腿官方有铜 15.019mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 J_SOM_P4.89 的最优出脚余量 0.025mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair CSI_D0_D3_P_SRC CSI_D0_D3_N_SRC` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `DSI_D0_D0_N_SRC` | **B** | 最紧端点 J_SOM_P3.57 的最优出脚余量仅 **0.025mm** (阻挡物 `J_SOM_P3.55` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="DSI_D0_D0_N_SRC"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `DSI_D0_D0_P_SRC` | **B** | 最紧端点 J_SOM_P3.59 的最优出脚余量仅 **0.025mm** (阻挡物 `J_SOM_P3.61` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="DSI_D0_D0_P_SRC"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `DSI_D0_D1_N_SRC` | **B** | 最紧端点 J_SOM_P3.63 的最优出脚余量仅 **0.025mm** (阻挡物 `J_SOM_P3.65` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="DSI_D0_D1_N_SRC"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `DSI_D0_D1_P_SRC` | **B** | 最紧端点 J_SOM_P3.65 的最优出脚余量仅 **0.025mm** (阻挡物 `J_SOM_P3.63` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="DSI_D0_D1_P_SRC"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `DSI_D0_D2_N_SRC` | **A** | 差分腿且**伙伴腿官方有铜 95.787mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 J_SOM_P3.75 的最优出脚余量 0.025mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair DSI_D0_D2_P_SRC DSI_D0_D2_N_SRC` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `DSI_D0_D3_N_SRC` | **A** | 差分腿且**伙伴腿官方有铜 66.275mm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); 该腿端点 J_SOM_P3.81 的最优出脚余量 0.025mm ⇒ 几何不是瓶颈 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb --pair DSI_D0_D3_P_SRC DSI_D0_D3_N_SRC` | ① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; ② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通 |
| `FSIN_OUT` | **B** | 最紧端点 TP_FSIN.1 的最优出脚余量仅 **0.3mm** (阻挡物 `F.Cu` @ 0.5mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="FSIN_OUT"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `JTAG_TDI` | **B** | 最紧端点 J_DEBUG.3 的最优出脚余量仅 **0.088mm** (阻挡物 `J_DEBUG.2` @ 0.288mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="JTAG_TDI"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `LED_G_D` | **C** | 最紧端点 D_LED_G.1 的出脚余量 **0.525mm** (阻挡物 `F.Cu` @ 0.725mm) ⇒ 几何宽松; 但 A* 补线实测 (官方同配方 GRID=0.125 / margin 0.0625) **补上 0 条** ⇒ 是搜索失败不是几何卡死 (`logs/iss334/08_astar_officialenv.log`) | `bash state/pcbnew_py.sh state/fix_unconnected_astar.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/C_<net>/astar.kicad_pcb --max-dist 90` | ① 打印「补上 0 条 / 未成 N 条」且名单含该网 ⇒ A* 补线不通; ② 放大 A* 预算 (PCB_ABUDGET_MULT) 20× 后仍 0 ⇒ 不是预算 ⇒ 必须在产生点改 `state/gen_pcb_routing.py` |
| `SPI_MISO_BOOT` | **B** | 最紧端点 J_BOOT1.4 的最优出脚余量仅 **0.087mm** (阻挡物 `J_BOOT1.3` @ 0.287mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="SPI_MISO_BOOT"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `SPI_MOSI_BOOT` | **B** | 最紧端点 J_BOOT1.3 的最优出脚余量仅 **0.087mm** (阻挡物 `J_BOOT1.2` @ 0.287mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="SPI_MOSI_BOOT"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `SPI_SCLK_BOOT` | **B** | 最紧端点 J_BOOT1.1 的最优出脚余量仅 **0.162mm** (阻挡物 `J_BOOT1.2` @ 0.362mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="SPI_SCLK_BOOT"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `UART_RX` | **B** | 最紧端点 J_SOM_P2.9 的最优出脚余量仅 **0.025mm** (阻挡物 `F.Cu` @ 0.225mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="UART_RX"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |
| `USB_CC2` | **B** | 最紧端点 J_USB_C.B5 的最优出脚余量仅 **0.075mm** (阻挡物 `J_USB_C.A8` @ 0.275mm) ⇒ 出脚被几何钉死 (`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`) | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="USB_CC2"` | ① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; ② 出脚探针在 4 个方向上**都**读出余量 ≤ +0.3mm ⇒ 几何真卡死 ⇒ 换层绕开也不通 |

★桶计数: A=7 · B=16 · C=1 · 合计=24
★A 桶名单: CSI_D0_D0_N, CSI_D0_D0_N_SRC, CSI_D0_D1_N_SRC, CSI_D0_D3_N, CSI_D0_D3_N_SRC, DSI_D0_D2_N_SRC, DSI_D0_D3_N_SRC
★B 桶名单: CAM_RESET_N, CSI_D0_D1_N, CSI_D0_D1_P, CSI_D0_D2_N, CSI_D0_D2_P, DSI_D0_D0_N_SRC, DSI_D0_D0_P_SRC, DSI_D0_D1_N_SRC, DSI_D0_D1_P_SRC, FSIN_OUT, JTAG_TDI, SPI_MISO_BOOT, SPI_MOSI_BOOT, SPI_SCLK_BOOT, UART_RX, USB_CC2
★C 桶名单: LED_G_D

### §2-3 ★三桶小结 (★每桶的"最小可试机制"一句话★)★

| 桶 | 条数 | ★最小可试机制 (逐字)★ | ★能证伪它的读数★ |
|---|---|---|---|
| **A 成对走廊** | **7** | `bash state/pcbnew_py.sh state/pair_corridor.py <板> <DRC.json> --out <新板> --pair <P> <N>` (★逐段成对扩展 · P/N 同步规划一条走廊★) | 该命令打印「没找到成对路径 ⇒ 不落铜」 |
| **B 换层绕开** | **16** | `PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS="<网名>"` (★窄版直行 · 只让该网出脚先直行★) | 该网在新裸板 DRC 里**仍**出现于 `unconnected_items` |
| **C 路由器本体** | **1** | `bash state/pcbnew_py.sh state/fix_unconnected_astar.py <板> <DRC.json> --out <新板> --max-dist 90` (★用路由器自己的 A★ 补最后一段★) | 打印「补上 0 条 / 未成 N 条」且名单含该网 |

★★**三条必须一起说的实话 (★别把桶当 relieves★)★★:
1. ★**桶 C 只有 1 条 (LED_G_D)** —— 因为 ★**"几何卡死"这个前提在官方板上是假的**: 88/88 端点物理可行 + 出脚方向分配 CSP 可行 + 最紧端点余量 ≥ +0.30mm ⇒ ★**几乎所有零铜网的真病都是"路由器搜不到路", 不是"几何走不出去"** ★
2. ★**桶 B 的 16 条里, 阻挡物绝大多数是【同排邻脚】或【net-0 未分配铜】(例: `J_SOM_P4.69` @0.225mm · `J_BOOT1.3` @0.287mm · `J_UART.1` @0.363mm)⇒ ⇒ 这是【同排排距/出脚方向】问题, 不是【差分走廊】问题** ★
3. ★**"官方板优先布了 P 腿却没布 N 腿"这个现象 (7 条) 在【零铜网】里不是唯一的**: `DSI_D0_D0_P_SRC/N_SRC` 与 `DSI_D0_D1_P_SRC/N_SRC` 两对是**双边零铜** ⇒ ★**说明连"先布 P 再布 N"都没发生 ⇒ 整对根本没进布线流程** ★ ⇒ ⇒ 这 4 条属于 B 桶 (出脚几何) 而**不是** A 桶, ★A 桶不能扩大到它们★ ★

---

## §3 候选臂设计 (★只设计 + 判据 · 本单不跑长链★)

### §3-1 ★★★起跑线的选择 (★这一条决定所有臂可比不可比·ISS-328 的死因就在这★)★★★

★**机器读数 (★本单实跑★)** ★:

| 板 | 走线段 | 过孔 | 出处 |
|---|---|---|---|
| ★官方板 `HW/PCB/demo_mainboard.kicad_pcb` ★ | **18,092** | **433** | `logs/iss334/01_check_pcb_drc.log` + §1-1 |
| ★官方 stage-1 `/tmp/chain_offverify/s1_straight.kicad_pcb` ★ | **17,022** | — | `/tmp/chain_offverify/chain.log` 第 30 行「⇒ 17022 段」 |
| ★当前生成器产物 (`/tmp/chain_v76mg1/s1_straight.kicad_pcb`) ★ | **2,492** | — | `/tmp/chain_v76mg1/chain.log` 第 32 行「⇒ 2492 段」 |
| ★当前链终板 (`/tmp/chain_v76mg1/final_chain.kicad_pcb`) ★ | **3,304** | 471 | 本单实测 |
| ★ISS-325 对照臂终板 ★ | 3,666 | 505 | 本单实测 |

★★**链自己的自校准闸已经写死了这句话 (★`/tmp/chain_v76mg1/chain.log` L120~L122★)** ★★:
> 「⚠️ 自校准闸(档②): 输入是【路由产物】 ⇒ ★**链已跑完但产物不能与官方板直接比**」
> 「★原因: ★官方链的 stage-1 产物是 17022 段, 当前路由器只出 2488 段 ⇒ ★路由器代码已漂移 ⇒ ★两臂不同工艺」
> 「⇒ ★段数 3304 (★官方终板 18092) · ★**只能用【四把尺子】对已晋级臂比, 不能拿这块直接对比官方**」

⇒ ★★★**本单结论 (★所有臂的起跑线由此定死★)** ★★★:
1. ★**起跑线 = 官方 stage-1 `/tmp/chain_offverify/s1_straight.kicad_pcb` (17,022 段)** ⇒ 只有从这条线起跑, 终板才与官方板【同工艺可比】★
2. ★**官方板可被完整复现**: `python3 state/cmp_pcb_geom.py /tmp/chain_offverify/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb` ⇒ ★**rc=0 · 走线几何集合 17,980 条完全相同 · 过孔 433 个完全相同 · 铜皮 5 区完全相同** ★ ⇒ ★**官方板不是"不可复现的黑盒", 官方 stage-1 在机器上** ★
3. ★**任何从"当前生成器"起跑的臂 (2,492 段级) 都【不可比】** ⇒ ★**ISS-328 右上臂 3,986 段的 REJECT 判据是对的, 根因也在这里** ★
4. ★**生成器级 env (ESC_* / PAIR_* / W_MIN) 只在生成器里 ⇒ ★在官方 stage-1 线上【用不了】** ⇒ ⇒ ★**桶 B 的 env 级臂【不可比】, 桶 B 必须重铸为成品板级机制** ★

### §3-2 ★共通作业骨架 (★每条臂都照这一段跑·逐字★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
ARM=<臂名>                       # ★臂名见下表
mkdir -p tmp/iss334/arms/$ARM
cp /tmp/chain_offverify/s1_straight.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb
# ★★机制步骤: 见 §3-3 / §3-4 / §3-5 各臂的"机制步骤"★★
# ★★链 (★只写 /tmp/chain_<tag>/ · 不碰 HW/PCB★):
PCB_CHAIN_LOOSE_MARGIN=0.0625 bash state/replay_patch_chain.sh \
    tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb $ARM
FINAL=/tmp/chain_$ARM/final_chain.kicad_pcb
# ★★收尾 (边际净距收窄·不动官方板):
bash state/clrfix_iter.sh $FINAL $FINAL.drc.json --max 5 --tag $ARM
```

★**判据命令 (★三条都要跑·缺一条不算数·逐字★)** ★:

```bash
# ★① 名单制闸 (★唯一晋级判据·rc=0 才算可晋级★)
python3 state/compare_arm_official.py $FINAL HW/PCB/demo_mainboard.kicad_pcb ; echo "GATE_RC=$?"
# ★② DRC (★要求 viol=0·rc=0★)
python3 state/check_pcb_drc.py $FINAL ; echo "DRC_RC=$?"
# ★③ unc / 零铜网 / 单边零铜对 三计数 (★★只能当辅助·"变少"不算成功★★)
python3 state/pair_copper_table.py $FINAL > tmp/iss334/arms/$ARM/pair_copper.txt
bash state/kicad.sh pcb drc --output tmp/iss334/arms/$ARM/final.drc.json \
     --severity-error --severity-warning --format json $FINAL >/dev/null 2>&1
python3 - <<'PY'
import json
d = json.load(open("tmp/iss334/arms/$ARM/final.drc.json", encoding="utf-8"))
print("unc =", len(d.get("unconnected_items") or []),
      "viol =", len(d.get("violations") or []))
PY
# ★④ 同工艺自检 (★段数/过孔必须与官方同量级·见 §3-6★)
grep -c "(segment" $FINAL ; grep -c "(via" $FINAL
# ★⑤ 未连接【网名集合】比较 (★"同工艺"要看集合不看条数★)
python3 state/cmp_unc_sets.py tmp/iss334/arms/$ARM/final.drc.json logs/iss334/00_official_drc_fresh.json
```

---

### §3-3 ★桶 A 候选臂 · `A1_pair_corridor` (+ 对照臂 `A0_control`)★

| 项 | ★候选臂 `A1_pair_corridor` ★ | ★对照臂 `A0_control` ★ |
|---|---|---|
| ★桶 / 覆盖网 ★ | A 桶 7 条 (见 §2-2) | 同 7 条 (作为"没上机制"的读数) |
| ★起跑线 ★ | `/tmp/chain_offverify/s1_straight.kicad_pcb` (17,022 段) | **逐字相同** |
| ★唯一变量 ★ | ★**在链之前插一步成对走廊** ★ | ★**不插** ★ |
| ★机制步骤 (逐字) ★ | `for P_N in "CSI_D0_D0_P CSI_D0_D0_N" "CSI_D0_D0_P_SRC CSI_D0_D0_N_SRC" "CSI_D0_D1_P_SRC CSI_D0_D1_N_SRC" "CSI_D0_D3_P CSI_D0_D3_N" "CSI_D0_D3_P_SRC CSI_D0_D3_N_SRC" "DSI_D0_D2_P_SRC DSI_D0_D2_N_SRC" "DSI_D0_D3_P_SRC DSI_D0_D3_N_SRC"; do set -- $P_N; bash state/pcbnew_py.sh state/pair_corridor.py tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.drc.json --out tmp/iss334/arms/$ARM/pc_$1.kicad_pcb --pair $1 $2; done` | ★**无** ★ |
| ★预期耗时 ★ | ★每对 ≈ 3~6 min (实测单对 ≈ 2 min · 见 §4-3) ⇒ ★7 对 ≈ 25~45 min★ + 链 ≈ 2 h | 链 ≈ 2 h |
| ★产物落点 ★ | `tmp/iss334/arms/A1_pair_corridor/` + `/tmp/chain_A1_pair_corridor/` | `tmp/iss334/arms/A0_control/` + `/tmp/chain_A0_control/` |
| ★判据命令 ★ | §3-2 的 ①②③④⑤ (逐字) | 同 |
| ★失败回退 ★ | 任一对打印「没找到成对路径 ⇒ 不落铜」⇒ ★**该对不再上臂** ⇒ 改走 §3-4/§3-5 的机制 ⇒ ★A1 整臂判 REJECT★ | 同 |
| ★对照有效性自检 ★ | ★`python3 state/cmp_pcb_geom.py /tmp/chain_A1_pair_corridor/final_chain.kicad_pcb /tmp/chain_A0_control/final_chain.kicad_pcb` ⇒ ★**必须 rc=1 (不等价)**★ | ★`python3 state/cmp_pcb_geom.py /tmp/chain_A0_control/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb` ⇒ ★**必须 rc=0 (复现官方)**★ |
| ★可比性自检 ★ | §3-6 (段数/过孔 ∈ 官方 ±10%) | 同 |

★★**★A1 臂的已知拦路虎 (★§4-3 实测·本单已踩到★)★★**: ★**现状的 `state/pair_corridor.py` 在官方板上跑完 = 零新增铜 (与官方板几何等价) ★★
⇒ ★**A1 的机制步骤开跑前, 必须先让 pair_corridor 能产出【≥2 格】的路径 (★现状只走 1 格退化路径·`--` 见 §4-3 日志)★ ⇒ ⇒ 这是【工具层修改】⇒ ⇒ 进 §5 need (★本单零改生成器/工具代码·不许自己动手★)** ★

### §3-4 ★桶 B 候选臂 · `B1_fine_grid` (+ 对照臂 `B0_control`)★

| 项 | ★候选臂 `B1_fine_grid` ★ | ★对照臂 `B0_control` ★ |
|---|---|---|
| ★桶 / 覆盖网 ★ | B 桶 16 条 | 同 16 条 (作为"没上机制"的读数) |
| ★起跑线 ★ | `/tmp/chain_offverify/s1_straight.kicad_pcb` (17,022 段) | **逐字相同** |
| ★唯一变量 ★ | ★**链的 A* 步网格 0.125 → 0.0625** ★ | ★**网格 0.125 (官方原值)** ★ |
| ★机制步骤 (逐字) ★ | ★`cp state/replay_patch_chain.sh tmp/iss334/arms/B1_fine_grid/chain.sh` ★ + ★**把 `step_nostub "$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125 "$_LOOSE_MARGIN"` 里的 `0.125` 改成 `0.0625`** ★ + ★`bash tmp/iss334/arms/B1_fine_grid/chain.sh tmp/iss334/arms/B1_fine_grid/s0_official_s1.kicad_pcb B1_fine_grid` ★ | ★**同样的 cp + 同样的一处字面改 0.125 → 0.125 (即不改)★** ★`bash tmp/iss334/arms/B0_control/chain.sh tmp/iss334/arms/B0_control/s0_official_s1.kicad_pcb B0_control` ★ |
| ★预期耗时 ★ | ★网格步长减半 ⇒ 格数 ×4 ⇒ ★**≈ 4× 内存/时间**★ ⇒ ★链 ≈ 4~8 h (★裸板步也要 ×4★) | 链 ≈ 2 h |
| ★产物落点 ★ | `tmp/iss334/arms/B1_fine_grid/` + `/tmp/chain_B1_fine_grid/` | `tmp/iss334/arms/B0_control/` + `/tmp/chain_B0_control/` |
| ★判据命令 ★ | §3-2 的 ①②③④⑤ (逐字) | 同 |
| ★失败回退 ★ | 若 B1 终板 **16 条 B 桶网在 `pair_copper_table.py` 里仍全是 0.000** ⇒ ★**细网格救不了 ⇒ B 桶的药方证伪** ★ ⇒ 升级到 §3-5 的产生点改法 | 同 |
| ★对照有效性自检 ★ | ★`cmp_pcb_geom.py B1终板 B0终板` ⇒ ★**必须 rc=1** ★ | ★`cmp_pcb_geom.py B0终板 官方板` ⇒ ★**必须 rc=0 (复现官方)** ★ |
| ★可比性自检 ★ | §3-6 | 同 |

★★**★B 桶的 env 级臂为什么被否 (★硬事实, 不是判断★)★★**: ★`PCB_ESC_STRAIGHT` / `PCB_ESC_STRAIGHT_NETS` / `PCB_ESC_CLR_FIX` / `PCB_ESC_ROWNORM` / `PCB_ESC_ROWNORM2` / `PCB_PAIR_LAYERSEL` / `PCB_W_MIN` / `PCB_LAYERS` 全部只存在于 ★**生成器 `state/gen_pcb_routing.py`** ★
⇒ ★**当前生成器只出 2,492 段 (官方 stage-1 = 17,022 段) ⇒ 从当前生成器起跑的臂, 终板 ≈ 3,304 段 ⇒ 与官方板【不同工艺】⇒ ★`compare_arm_official.py` 的读数【不算数】(★这正是 ISS-328 右上臂被判"不可比"的同一机制★)** ★
⇒ ⇒ ★**B 桶要真能上, 前置条件是"把生成器恢复到官方 stage-1 的产出口径" ⇒ 这是 §5 的 need-1** ★

---

### §3-5 ★桶 C 候选臂 · `C1_rip_guarded` (+ 对照臂 `C0_control`)★

| 项 | ★候选臂 `C1_rip_guarded` ★ | ★对照臂 `C0_control` ★ |
|---|---|---|
| ★桶 / 覆盖网 ★ | C 桶 (`LED_G_D`) + ★**A/B 两桶的 23 条一并受益 (★C 机制作用在路由器本体·不限桶★)** ★ | 同 |
| ★起跑线 ★ | `/tmp/chain_offverify/s1_straight.kicad_pcb` (17,022 段) | **逐字相同** |
| ★唯一变量 ★ | ★**链之前插一步"保分支 rip-and-replace"** ★ | ★**不插** ★ |
| ★机制步骤 (逐字) ★ | `bash state/pcbnew_py.sh state/fix_board_rip_guarded.py tmp/iss334/arms/$ARM/s0_official_s1.kicad_pcb tmp/iss334/arms/$ARM/s0_official_s1.drc.json --out tmp/iss334/arms/$ARM/s1_ripguarded.kicad_pcb --max-dist 90 --rip 8` ★(★环境: `PCB_RIPUP_ALIVE=1 PCB_RIPUP_ESC=1 PCB_GRID=0.125 PCB_HALO_MARGIN=0.0625`★) | ★**无** ★ |
| ★预期耗时 ★ | ★该步 ≈ 20~40 min + 链 ≈ 2 h ★ | 链 ≈ 2 h |
| ★产物落点 ★ | `tmp/iss334/arms/C1_rip_guarded/` + `/tmp/chain_C1_rip_guarded/` | `tmp/iss334/arms/C0_control/` + `/tmp/chain_C0_control/` |
| ★判据命令 ★ | §3-2 的 ①②③④⑤ (逐字) + ★`python3 state/pair_copper_table.py` 对比 `LED_G_D` 铜长 ★ | 同 |
| ★失败回退 ★ | 若 rip 步打印「孤岛数变多 ⇒ 回滚」⇒ ★**该机制对官方 stage-1 不安全 ⇒ 整臂停, 不许把回滚后的板当候选★** | 同 |
| ★对照有效性自检 ★ | ★`cmp_pcb_geom.py C1终板 C0终板` ⇒ ★**必须 rc=1** ★ | ★`cmp_pcb_geom.py C0终板 官方板` ⇒ ★**必须 rc=0 (复现官方)** ★ |
| ★可比性自检 ★ | §3-6 | 同 |

★★**★C 桶的"修在产生点"版本 (`C2_production_fix`) ★★**: ★**MEMORY 铁律: 修在产生点, 不许在产物上擦** ★
⇒ ★**C1 / C2 的区别**: C1 是在【成品板】上补 (★擦在产物上·只当读数·不当结论★); C2 才是正解 = ★**改 `state/gen_pcb_routing.py` 的 A* 使它能对"整网无铜"的网做【整网重布】** ★
⇒ ★**C2 需要改生成器代码 ⇒ ★本单零改生成器代码 ⇒ C2 只出规格, 不实施 ⇒ 进 §5 need-2** ★
⇒ ★**C2 的规格要点 (给改的人用)★**: ① 触发条件 = ★**该网在板上 segment 数 = 0 且焊盘数 ≥ 2** ★ (★与 `compare_arm_official.py` 的零铜定义逐字一致★) ② 修法 = ★**A* 从焊盘格起步, 而不是从"已有铜的端点"起步** ★ ③ 守卫 = ★**落铜后逐网孤岛数不得变多 (沿用 `state/rip_guard.island_count_model`) + 差分腿不得打死** ★ ④ 只加铜不删铜 ⇒ ★**不可能把网打成零铜** ★

### §3-6 ★★★对照有效性自检 + 可比性自检 (★ISS-325/ISS-328 的血泪·必做★)★★★

#### §3-6-1 ★对照有效性自检 (★对照臂必须【真能构成对照】·否则整臂作废★)★

★**ISS-325 的教训 (★原文★)**: 左上臂两臂 **185 个封装落位 diff = 0** ⇒ ★**对照天然失效 ⇒ 整趟白跑** ★
★**本单的改法**: ★**本单的变量是【布线 env / 工具步骤】, 不是器件坐标 ⇒ 封装落位【本来就该相同】⇒ 落位 diff = 0 不是失效信号★; ★该看的 diff 是【铜的落位】** ★

| 自检项 | 命令 (逐字) | 通过判据 | 不过怎么办 |
|---|---|---|---|
| ★① 对照臂能不能复现官方 ★ | `python3 state/cmp_pcb_geom.py /tmp/chain_<对照臂>/final_chain.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb` | ★**rc=0 (几何等价)** ★ | ★**rc=1 ⇒ 对照臂作废 ⇒ 候选臂的读数一律不算数 ⇒ 停** ★ |
| ★② 候选臂与对照臂是不是真的不同 ★ | `python3 state/cmp_pcb_geom.py /tmp/chain_<候选臂>/final_chain.kicad_pcb /tmp/chain_<对照臂>/final_chain.kicad_pcb` | ★**rc=1 (几何不等价)** ★ | ★**rc=0 ⇒ 候选臂作废 (机制没生效) ⇒ 不许把它的读数当功劳 ⇒ 停** ★ |
| ★③ 铜量读数确实动了 ★ | `python3 state/pair_copper_table.py` 对比两臂 | ★**至少 1 个网的铜长变了** ★ | 两臂铜长逐条相同 ⇒ 同 ② |
| ★④ 闸到底生不生效 ★ | `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script tmp/iss334/arms/<臂名>/arm.sh` | ★**返回 ≠ 0 (闸在该臂上生效)** ★ | ★**返回 0 ⇒ 闸在这个臂上不生效 ⇒ 不许开臂** ★ |

#### §3-6-2 ★可比性自检 (★段数/过孔必须与基线同量级·ISS-328 的死因★)★

| 项 | 官方基线 | ★合格区间 (官方 ±10%) ★ | 不过怎么办 |
|---|---|---|---|
| 走线段数 | **18,092** | ★**16,283 ~ 19,901** ★ | ★低于 16,283 ⇒ **与官方不同工艺 (ISS-328: 3,986 段 ⇒ 不可比) ⇒ 该臂全部读数不算数** ★ |
| 过孔数 | **433** | ★**390 ~ 476** ★ | 同上 |
| ★未连接网名集合 ★ | 43 网 | ★`python3 state/cmp_unc_sets.py` 的【网名集合】交集 ≥ 40 ★ | ★交集差得多 ⇒ 不是同一批网 ⇒ 不可比 ★ |
| ★零铜网数 ★ | 24 | ★**只能变少, 不能变多** ★ | ★变多 ⇒ 该臂把别的网打死了 ⇒ 名单制闸必红 ★ |

---

## §4 沙盒预演读数 (★本单实跑·只写 tmp/iss334/ ★官方板逐字节未动★)

★**沙盒纪律**: ★**只写 `tmp/iss334/`**; ★**官方板 md5 / mtime 交卷前后各读一次**; ★**没跑官方补丁链 (≈2 h)**; ★**没跑 `state/replay_patch_chain.sh`** ★

### §4-1 预演 ① · A* 补线 (★粗网格档 · 对照用·证明"读数对 env 敏感"★)

| 项 | 读数 |
|---|---|
| 命令 | `bash state/pcbnew_py.sh state/fix_unconnected_astar.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/05_astar_try.kicad_pcb --max-dist 90` |
| env | 脚本默认 (★网格 0.25 · `PCB_HALO_MARGIN=0.20`★) |
| ★读数 ★ | ★**补上 0 条 / 未成 45 条** (★理由串: 「A\* 找不到路 / stub 净距不过」★) ★ |
| 产物板 | ★**md5 = `611b869e13518c3c023fb178f91a0075` = 官方板逐字节相同 (零铜没落)** ★ |
| 出处 | `logs/iss334/06_astar_try.log` |

### §4-2 预演 ② · A* 补线 (★官方同配方档 · **★桶 C 的决定性读数★**)★

| 项 | 读数 |
|---|---|
| 命令 | `env PCB_LAYERS=8 PCB_GRID=0.125 PCB_HALO_MARGIN=0.0625 PCB_VIA_HALO_MARGIN=0.0 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_EXEMPT_R=0.0 bash state/pcbnew_py.sh state/fix_unconnected_astar.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/06_astar_officialenv.kicad_pcb --max-dist 90` |
| ★读数 ★ | ★**障碍图 1283×803 格 (0.12mm) · 已灌入成品板铜 18,525 图元 · 补上 0 条 / 未成 45 条** ★ |
| 产物板 | ★**md5 = `611b869e13518c3c023fb178f91a0075` = 官方板逐字节相同** ★ |
| ★★结论 ★★ | ★★**把网格从 0.25 收到 0.125 (4× 细) + 把 margin 从 0.20 收到官方同档 0.0625, 路由器的 A\* 仍然一条都补不出来 ⇒ ★"是搜索分辨率不够"这个假设被证伪 ⇒ 剩下的就是【A\* 搜索本身】/【障碍图本身】的问题** ★★ |
| ★★更硬的旁证 (★官方链自己的日志★) ★★ | ★★`/tmp/chain_offverify/chain.log` L41~L47: 在**官方 stage-1 (17,022 段)** 上跑链的 A\* (grid 0.125 · margin 0.0625) ⇒ ★**补上 6 条 / 未成 48 条**, 且失败理由串是干净的 ★**「A\* 找不到路」** (★不是 stub 净距不过★) ★★ |
| ★★交叉命中 ★★ | ★★那 48 条失败名单里 ★**14 个**正是本单的零铜网: `CAM_RESET_N` · `CSI_D0_D0_N` · `CSI_D0_D1_N` · `CSI_D0_D1_P` · `CSI_D0_D2_N` · `CSI_D0_D2_P` · `CSI_D0_D3_N` · `CSI_D0_D3_N_SRC` · `DSI_D0_D0_P_SRC` · `DSI_D0_D1_P_SRC` · `FSIN_OUT` · `SPI_MISO_BOOT` · `SPI_MOSI_BOOT` · `SPI_SCLK_BOOT` (★名单落盘: `tmp/iss334/10_official_stage_astar_failed.txt`★) ★★ |
| 出处 | `logs/iss334/08_astar_officialenv.log` + `/tmp/chain_offverify/chain.log` |

### §4-3 预演 ③ · 桶 A 机制 (★成对走廊 · **★撞墙★**)★

| 项 | 读数 |
|---|---|
| 命令 | `bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_CSI_D0_D0/pair_corridor.kicad_pcb --pair CSI_D0_D0_P CSI_D0_D0_N` |
| ★日志读数 ★ | ★`P 焊盘 3 个 · N 焊盘 3 个` · ★`第 0 段: P P_pad0 (1 格) · N N_pad0 (1 格)` · ★`── 结果: ★**部分完成**: P 1/3 · N 1/3` · ★`── 落铜成功: P 1 段 / N 1 段` ★ |
| ★★★实测结论 (★不轻信日志那句"落铜成功"★) ★★★ | ★**段数: 18,092 → 18,092 (没变) · 过孔: 433 → 433 (没变) · `pair_copper_table.py` 里 `CSI_D0_D0_N` 仍 = 0.000mm** ★ |
| ★几何判据 (★机器·不是目测★) ★ | `python3 state/cmp_pcb_geom.py HW/PCB/demo_mainboard.kicad_pcb tmp/iss334/arms/A_CSI_D0_D0/pair_corridor.kicad_pcb` ⇒ ★**rc=0 · 两板几何等价 (17,980 条走线 + 433 过孔 + 5 铜皮全同)** ★ |
| ★★★结论 ★★★ | ★★★**`state/pair_corridor.py` 在官方板上跑完 = 【零新增铜】** ★★★ ⇒ ★**它只走通了 1 格的退化路径 (★= 焊盘自己那一格★) ⇒ `_emit_path` 对 1 格路径不落段 ⇒ "落铜成功"这句日志是【假阳性】** ★ |
| ⇒ 对 §3 的影响 ★ | ★**A1 臂开跑前必须先修 `pair_corridor.py` 让它能产出 ≥2 格的路径** ⇒ ★工具层修改 ⇒ §5 need-3** ★ |
| 出处 | `logs/iss334/10_pair_corridor_A_demo.log` |

---

## §5 need 列表 (★交 main / 老板拍 · 本单一条都不自己定★)

| # | ★need (问法)★ | ★谁答★ | ★不答后果★ | ★建议默认值 (供拍·不是决定)★ | ★建议排期★ |
|---|---|---|---|---|---|
| ★need-1 ★ | ★**生成器漂移怎么处理**: 「★当前 `state/gen_pcb_routing.py` 只出 2,492 段, 官方 stage-1 是 17,022 段 (★链的自校准闸 L120~L122 已明写'路由器代码已漂移'★) ⇒ ★**官方板已不能由现生成器复现** ⇒ ★**env 级臂 (B 桶) 的终板必与官方板不同工艺 ⇒ 不可比** ★⇒ ★**问: 是先把生成器恢复到官方 stage-1 的产出口径 (★要 diff 出漂移点★), 还是接受现生成器产物另立新基线?」 ★ | **main + boss** | ★**B 桶 16 条零铜网没有任何可比的臂可开 ⇒ 板那一趟会再踩一次 ISS-328 的"不可比"坑 (3,986 段 vs 18,092 段)** ★ | ★**先立新基线**: 用现生成器跑一次全链 (≈2 h) 定一个"新官方线", 把 24 个零铜网在新线上重新读一遍; ★**旧官方板只在"成品板级机制" (A/C) 上继续用** ★ | ★板那一趟的 A 步之前 ★ |
| ★need-2 ★ | ★**是否授权改产生点**: 「★**MEMORY 铁律: 修在产生点, 不许在产物上擦** ★⇒ ★C 桶的正解 = 改 `state/gen_pcb_routing.py` 的 A★, 让它能对【整网无铜】(segment=0 且 pad≥2) 的网做整网重布 (★触发条件与 `compare_arm_official.py` 的零铜定义逐字一致★) + 孤岛守卫 + 差分腿保护 + 只加铜不删铜 ⇒ ★**问: 授权不授权动 `gen_pcb_routing.py`?」 ★ | **main (代码授权) + boss (要不要动路由器)** | ★**C 桶只能靠"擦在产物上" (C1) ⇒ 违反铁律; 且 C1 实测过: A★ 在官方成品板上补 0 条 (网格收到 0.125 仍 0 条)** ★ | ★**授权**, 但必须带四条护栏 (只加铜不删铜 / 孤岛数不得变多 / 差分腿不得打死 / 改完先跑 `state/compare_arm_official.py --self-test`)** ★ | ★板那一趟的 D 步 ★ |
| ★need-3 ★ | ★**工具假阳性要不要修**: 「★`state/pair_corridor.py` 在官方板上跑完打印『落铜成功: P 1 段 / N 1 段』, 但**段数 18,092→18,092、`CSI_D0_D0_N` 仍 0.000mm、两板几何等价** ⇒ **那 1 段是 1 格退化路径·根本没落铜** ⇒ ★**问: 授权不授权修这个工具 (至少把 1 格路径的假阳性判成失败, 再谈续段)?」 ★ | **main** | ★**A 桶 7 条零铜差分腿没有可用机制 ⇒ 桶 A 直接空转** ★ | ★**授权先修假阳性判定 (小改)**, 再看续段是否值得做; ★**修完先在 `tmp/` 复跑一次单对, 段数必须 ≥ 18,093 才算修好** ★ | ★A1 臂开跑前 ★ |
| ★need-4 ★ | ★**24 个零铜网要不要按"必需性"分级**: 「★24 条里 ★**15 条是高速差分腿 (CSI/DSI)· 9 条是单端低速脚** (`CAM_RESET_N` · `FSIN_OUT` · `JTAG_TDI` · `LED_G_D` · `SPI_*_BOOT` ×3 · `UART_RX` · `USB_CC2`) ⇒ ★**问: 这 9 条单端脚里, 有没有本来就不必布的 (调试脚 / BOOT 模式脚 / 状态指示脚) ⇒ 若可悬空, 它们就不该进'必须救回'名单** ★⇒ ★**谁给这 9 条定必需性?」 ★ | ★**boss (产品口径) + sw-lead (固件是否真的用) + main (汇总)** ★ | ★**板那一趟会为了救一条调试脚去动高速差分走廊 ⇒ 风险不对称** ★ | ★**分级**: 必需 = 15 条差分腿 + `USB_CC2` + `UART_RX`; 可悬空 = `JTAG_TDI` / `SPI_*_BOOT` / `LED_G_D` / `FSIN_OUT` / `CAM_RESET_N` (★**具体以 sw-lead 的固件引用为准·本单不代拍**★) ★ | ★板那一趟之前 ★ |
| ★need-5 ★ | ★**名单制闸拿谁做对比对象**: 「★`compare_arm_official.py` 只能配官方板 (18,092 段) 才有意义; 而现生成器链的终板是 3,304 段 ⇒ ★**问: 板那一趟的臂, 一律要求先满足『段数 ∈ 16,283~19,901』再进闸, 还是允许拿同工艺基线 (3,304 段) 做闸?** ★ | ★**main** ★ | ★**拿不可比的板去过闸 ⇒ 闸的结论无效 (★ISS-328 就是这么死的★)** ★ | ★**本单建议: 臂一律与官方板比, 但必须先过 §3-6-2 的段数/过孔区间自检; 达不到区间的臂, 只能与同工艺基线比, 且结论只能写"同工艺内变好"** ★ | ★板那一趟的 A 步 ★ |
| ★need-6 ★ | ★**老板口径那 8 个字母要不要并进机制级路线**: 「★(b) 路线 = 老板口径 (★W-2 / W-1c / A4 / W-3 / U-1 / P7 …★) ⇒ ★**问: 机制级三桶 (A/B/C) 全是【布线机制·不动器件选型与拓扑】⇒ 与老板口径是否冲突? 要不要等口径落定再合并?** ★ | ★**boss** ★ | ★**机制级做出来的板可能与老板口径打架 ⇒ 白做** ★ | ★**本单建议: 机制级只做"不改拓扑、不改器件选型"的臂 (三桶都是布线层机制) ⇒ 与口径并行不冲突; 口径落定后再合并出最终板** ★ | ★板那一趟之前 ★ |

---

## §6 复现命令 (★逐字 · 本单全部机器读数的出处★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★① 官方板 md5 / mtime (★零写板自证·交卷前后各跑一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
# ★② fresh DRC 门禁 (★rc=0 · viol 0 · unc 45★)
PCB_DOC_OUT=$(pwd)/tmp/iss334/genout timeout 900 python3 state/check_pcb_drc.py \
    HW/PCB/demo_mainboard.kicad_pcb
# ★③ fresh DRC JSON (★落到 logs/ 以便引用★)
cp /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json logs/iss334/00_official_drc_fresh.json
# ★④ 逐对铜长 (★22 对·N 边零铜 7 + 双边零铜 4★)
python3 state/pair_copper_table.py HW/PCB/demo_mainboard.kicad_pcb
# ★⑤ 未连接三类工作表 (★整网无铜 24 · 局部未通 17 · 端点缝 2★)
bash state/pcbnew_py.sh state/probe_unconnected_worklist.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json --out tmp/iss334/01_worklist.md
# ★⑥ 零铜网 0 号清单 (★本单自写只读探针·定义对齐名单制闸★)
bash state/pcbnew_py.sh tmp/iss334/probe_zero_copper_nets.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json --out tmp/iss334/02_zero_copper_nets.md
# ★⑦ 出脚方向可行性 (★88 端点·物理可行 88/88★)
bash state/pcbnew_py.sh state/probe_escape_feasibility.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json --out tmp/iss334/03_escape_feasibility.txt
# ★⑧ 出脚方向分配 CSP (★几何可行性 = 可行★)
bash state/pcbnew_py.sh state/analyze_escape_dirs.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json --out tmp/iss334/04_escape_dirs.txt \
    --json tmp/iss334/04_escape_dirs.json
# ★⑨ A* 补线 · 官方同配方 (★补上 0 条 / 未成 45 条·产物 md5 = 官方板★)
env PCB_LAYERS=8 PCB_GRID=0.125 PCB_HALO_MARGIN=0.0625 PCB_VIA_HALO_MARGIN=0.0 \
    PCB_SKIP_PAD_CELLS=1 PCB_PAIR_EXEMPT_R=0.0 \
    bash state/pcbnew_py.sh state/fix_unconnected_astar.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json --out tmp/iss334/06_astar_officialenv.kicad_pcb \
    --max-dist 90
# ★⑩ 桶 A 机制沙盒 (★落铜"成功"但零新增铜·几何等价★)
bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb \
    logs/iss334/00_official_drc_fresh.json \
    --out tmp/iss334/arms/A_CSI_D0_D0/pair_corridor.kicad_pcb --pair CSI_D0_D0_P CSI_D0_D0_N
python3 state/cmp_pcb_geom.py HW/PCB/demo_mainboard.kicad_pcb \
    tmp/iss334/arms/A_CSI_D0_D0/pair_corridor.kicad_pcb
# ★⑪ 官方板可复现性 (★几何等价 rc=0★) + 同工艺基线读数
python3 state/cmp_pcb_geom.py /tmp/chain_offverify/final_chain.kicad_pcb \
    HW/PCB/demo_mainboard.kicad_pcb
grep -c "(segment" /tmp/chain_offverify/s1_straight.kicad_pcb \
             /tmp/chain_v76mg1/s1_straight.kicad_pcb \
             /tmp/chain_v76mg1/final_chain.kicad_pcb
# ★⑫ 闸的自测 (★本单只跑 --self-test·不动闸★)
python3 state/compare_arm_official.py --self-test
```

★★**本单【没跑】的 (★原因 + 预计耗时 + 下一轮跑★)** ★★:

| 没跑的 | 原因 | 预计耗时 | 下一轮 |
|---|---|---|---|
| ★官方补丁链 `state/replay_patch_chain.sh` 全链 ★ | ★**任务书明令不许跑 (≈2 h)·且会落盘到 `/tmp/chain_*`** ★ | ≈2 h/臂 | 板那一趟 (§4 作业包) |
| ★`B1_fine_grid` / `A1_pair_corridor` / `C1_rip_guarded` 三条臂 ★ | ★**都是长链臂; 本单只出设计与判据** ★ | A1 ≈ 2.5 h · B1 ≈ 4~8 h · C1 ≈ 2.5 h | 板那一趟 |
| ★A★ 在【官方 stage-1 (17,022 段)】上的补线读数 ★ | ★**预演 ③ 已在跑 (沙盒·只写 tmp·官方板零触碰·结果见 §4-4) ★** | ≈12 min | 本轮内 |

---
### §4-4 预演 ④ · A★ 补线 (★跑在【官方 stage-1 (17,022 段)】上 · **★决定性★**)★

| 项 | 读数 |
|---|---|
| 命令 | `env PCB_LAYERS=8 PCB_GRID=0.125 PCB_HALO_MARGIN=0.0625 PCB_VIA_HALO_MARGIN=0.0 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_EXEMPT_R=0.0 bash state/pcbnew_py.sh state/fix_unconnected_astar.py /tmp/chain_offverify/s1_straight.kicad_pcb /tmp/chain_offverify/s1_straight.kicad_pcb.drc.json --out tmp/iss334/arms/C_astar_s1/astar_s1.kicad_pcb --max-dist 90` |
| ★读数 ★ | ★**障碍图 1283×803 格 (0.12mm) · 已灌入成品板铜 17,430 图元 · 补上 0 条 / 未成 54 条** ★ |
| 产物板 | ★**md5 = `8b33af5181e8d80ef471c6d1f59298e6` = 输入 stage-1 逐字节相同 (零铜没落)** ★ |
| ★★★结论 (★本单最硬的一条读数★) ★★★ | ★★★**A★ 在【官方链最早的板 (stage-1, 17,022 段)】上就已经补不出任何一条** ★★★ ⇒ ★**"是链后面几步把路堵死了"这个假设被证伪** ⇒ ★**⇒ 24 个零铜网从第一张板起就没被 A★ 找到过路 ⇒ ★**真病在【路由器本体 / 障碍图构造】, 不在【后处理顺序】** ★★★ ⇒ ★**桶 C 成立, 且 C1 (擦在产物上) 注定无效 ⇒ 只有 C2 (修在产生点) 有戏** ★ |
| 出处 | `logs/iss334/11_astar_on_official_s1.log` |


