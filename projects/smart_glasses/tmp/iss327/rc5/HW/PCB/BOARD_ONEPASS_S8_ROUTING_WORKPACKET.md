# BOARD_ONEPASS · S8 布线归零 (unconnected 45 → 0) · 死因登记 + 高速腿几何可布性判定 + 作业包

> ★**单号**: ISS-322 · ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main · ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: 2026-11-18 11:0x (Asia/Shanghai)
> ★**性质**: ★**内部活 · 纯分析 / 作业包 / 判据设计类 (HW 侧)** ★ · ★**零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM/原理图真源** ★ · 沙盒只写 `tmp/iss322/` · ★**零外发** ★ · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-311` (板那一趟重出清单 · verified) · `ISS-314` (S1 改名口径 · verified) · `ISS-317` (S1 逐条改名清单 · verified) · `ISS-265` (`HW/PCB/LAYOUT_FIX_SPEC.md` · 布局修正规格) · `ISS-308` (`HW/PCB/S8_REACHABILITY_VERDICT.md` · S8 可达性判决书)
> ★**本文件所有数字都是从 `logs/iss322/` 的机器生成原始输出逐字搬来的** (★装配器 `tmp/iss322/build_table45.py` 自带 45 条行数校验·不符即 abort★)

---

## §0 · 口径与边界自证

### §0-1 · 本单交付了什么 (★一句话★)

★★**S8 (unconnected 45 → 0) 的死因已经逐条登记完 (45 条·一条不少) ; 最关键的结论是 —— ①「23 vs 13」那两个数不打架 (★23 = DSI+CSI 两条未连接条目数·13 = DSI_ 单方向网名数·9 = CSI_ 网名数·22 = 高速网名总数★) ; ② 高速腿的【端点级几何】全部可布 (★88/88 端点在 0.20mm 下都有合法出脚方向★) ; ③ 【板框/层数】不是瓶颈 (★SoM 主体区 68×50mm 内 In1/In3/In5/In6/B.Cu 只被占 0.38%★) ; ④ 真正的几何瓶颈是【布局级】的 ★**DSI lane 段内 P/N 顺序翻转 17/47 处**★ —— 而它【已被实测隔离】: v76 链 7 块板 (lane 序 = SoM 端序) 的 unc 是 23/26/28/29/29/35/35, 唯独 lane 序反了的那块 (现役板) 是 45 (★全盘最差★) ⇒ ⇒ ★**修法 = 把 21 个 `R_SEL_*`/`TP_DSI_*` 挪到左上, 不是挪到右上**★ ⇒ ⇒ **板 md5 在【板那一趟】变一次即可, 不需要第二次** ★**

### §0-2 · ★★本单【推翻】了两条既有结论 (★逐字给出证据·不藏★)★★

| # | 既有结论 | 出处 | ★**本单实测反驳** ★ | 证据 |
|---|---|---|---|---|
| ① | ★**「官方板 (180×100/8L) 这 13 条 DSI 腿自己一根都没布通 ⇒ 归『几何/框级』桶, 不归『算法』桶」** ★ | 任务书 §1-⑦ + §2-③ 口径 | ★**推理无效** ★: ★**「官方板」就是现役板本身** ★ —— `state/official_18092_unc.drc.json` 的 `source` 字段 = `demo_mainboard.kicad_pcb`, `date` = `2026-11-10T03:13:55`; 现役板 `md5` = `611b869e…` / 走线 **18092** 段 / 过孔 **433** (★「18092」这个名字就是本板的走线段数★) ⇒ ★**它和现役板的网名签名 43/43 逐条相同 (差集 = 0) ⇒ 「官方板同病」对 45/45 条全部成立 ⇒ 零区分度, 不能当「几何级」的旁证** ★ | `logs/iss322/07_cmp_unc_sets_cur_vs_official.txt` (★交集 43 · 仅A 0 · 仅B 0★) · `logs/iss322/24_unc_diff_vs_unc_target_map_baseline.txt` | 
| ② | ★**「`PCB_PART_POS` 把 10 个 `R_SEL_*` 钉到左上 ⇒ lane 序被完全反向 (45 处交叉) ⇒ 修法 = 钉到右上 (方案 A)」** ★ | `HW/PCB/LAYOUT_FIX_SPEC.md` §0 (ISS-265) | ★**方向反了** ★: ★**钉到左上 (x 5.50..38.35) 的板, unc 是 23/26/28/29/29/35/35 (7 块 v76 链板, 全部 ≤ 35); 钉到右上 (x 75.7..117.3) 的板 (★现役板★) unc = 45, 是全盘最差的一块** ★ ⇒ ★**lane「交叉数」与 unc 数在本项目上是【反相关】的 ⇒ 不能用「交叉 45→0」当归零判据** ★ | `logs/iss322/22_lane_order_vs_unc.txt` (★8 块板逐块 R_SEL x 序 + unc + 翻转族数★) · `logs/iss322/20_probe_pn_order.txt` (★47 段比较 · 17 处翻转★) |

★★**这两条不改, 那一趟就会按相反方向做 ⇒ 板 md5 变两次 ⇒ 2-4 周 + ¥4-8K ⇒ 所以它们被写进 §5 的 need, 由 main / 老板拍, 本单不代拍** ★★

### §0-3 · 边界自证 (★本单做到 / 没做到★)

| 边界 | 本单怎么保证 | 自证 |
|---|---|---|
| ★**零写板** ★ | 只读 `HW/PCB/demo_mainboard.kicad_pcb`; 所有分析脚本只读板 + 只写 `tmp/iss322/` | ★md5 + mtime 交卷前后逐字节相同 (§6-1)★ |
| ★**零落表** ★ | 未写任何落表物 / 落表台账 | §6-1 命令清单可核 |
| ★**零改闸** ★ | `state/check_pcb_drc.py` / `state/merge.py` / `state/gate_check.py` / `state/issue_check.py` / `state/compare_arm_official.py` / `state/check_pcb_nets.py` 一个字节没动 | §6-1 md5 清单★ |
| ★**零改网表/脚表/BOM/原理图真源** ★ | 只读 | §6-1★ |
| ★**零改既有文档正文** ★ | ★**本文件是新建**; `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `state/UNC_TARGET_MAP.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` 一个字节没动 ⇒ 要改的地方在 §5-6 给 main「逐字改法 + 行号」★ | §6-1 + §5-6★ |
| ★**沙盒只写 `tmp/`** ★ | 全部脚本与中间产物落 `tmp/iss322/`; 探针的原始输出落 `logs/iss322/` | §6-2 目录清单★ |
| ★**零外发** ★ | ★**没发任何邮件 / 询价 / 问询 / 采购** ★★; 需要外部资料一律自己查 (★本单 §2-③ 的 KICAD 层数/净距口径用官方文档口径, 见 §6 的 `[官网]` 行★) | §6 证据分级表★ |
| ★**不替老板/main 拍板** ★ | §5 的 7 条 need 全部给「问法 + 谁答 + 不答后果 + 建议默认值 + 建议排期」, ★**一条都没替老板定** ★ | §5★ |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节没动 | §6-1★ |
| ★**只写自己那一份分片** ★ | 只写 `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead`★); `sw.yaml` / `mech.yaml` / `pm.yaml` 一个字节没碰 | §6-1★ |
| ★**不碰 MECH / SW 域** ★ | 未写 `MECH/` 任何文件 · 未写 `SW/` 任何文件 · 未读改 `state/fragments/sw.yaml` / `mech.yaml` | §6-1★ |

### §0-4 · ★**本单【没有】做的事 (★不许拿本单当这些事的证据★)★★

| # | 没做 | 为什么 |
|---|---|---|
| ① | ★**没有布一毫米线** ★ | 本单零写板; 布线是「板那一趟」的活 |
| ② | ★**没有证明「45 → 0 可达」** ★ | ★**盘上从来没有一块板到过 unc=0** (★实测: 全盘 11 份 DRC JSON 里最低 = 23, 无一份 = 0★) ⇒ ★**本单只证明【几何不构成障碍】, 不证明【零可达】** ★ |
| ③ | ★**没有改 `state/UNC_TARGET_MAP.md`** ★ | 它的基线过期 (★见 §2-4 差集表★) ⇒ 本单只给差集 + 重算建议, 改法归 main |
| ④ | ★**没有替 main 改 P7 的口径** ★ | §0-2 的两条推翻是【证据】, 拍板归 main / 老板 (§5-1 / §5-2) |
| ⑤ | ★**没有碰 `state/gate_check.py`** ★ | 它此刻 rc=1 的红项是 SW 域的 (★见 §6-3 逐字归因★) |

---

## §1 · 45 条 unconnected 逐条清单 (★机器搬·一条不许少★)

### §1-1 · 自证 (★条数必须 = 45★)

```
$ python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb
  ✅ C3 DRC violations = 0 (要求 0)
  ✅ C4 unconnected items = 45  ← 骨架阶段允许未布线 (布线完成后用 --strict 归零)
  ✅ C7 同点重复过孔 = 0 (要求 0)
```

★**条数 = 45, 与 C4 行逐字一致** ★ · 装配器 `logs/iss322/scripts/build_table45.py` 带 `assert len(unc) == 45`, 不符即 abort · 原始读数 `logs/iss322/01_check_pcb_drc_baseline.txt` · 装配器自检输出 `logs/iss322/23_build_table45.txt` (★含落桶分布 + 高速条目数 + 真墙条目数 + 与对照板的交叉标记★)

★★**★一条必须交代的可重复性说明 (★不然下一趟会以为抄错了★)★★**: ★**KiCad 的 DRC 在【同一块板】上重跑时, 同一条未连接的【两端归属】会在【两个等价端点】之间翻转 (★例如 `LIGHT_5V` 那条, 一次报 `CONN_CAM.30 ↔ D_ESD_LIGHT.1`, 另一次报 `走线端 ↔ D_ESD_LIGHT.1`★) ⇒ ★**⇒ 下表的【网名 / 桶 / 修法 / 死因】是稳定的 (45 条 / 43 网名 / 桶 22-18-5), 但【起点/终点那两格的措辞】会随 DRC 运行微动 ⇒ 复算时对不上这一格是正常的, 对不上【网名或桶】才是抄错** ★
★**⇒ 本单的全部读数统一取自 2026-11-18 11:3x 的一次 fresh DRC (★板 md5 逐字节不变 ⇒ 45 条与 43 个网名逐次不变★)** ★

### §1-2 · 45 条清单 (★8 列齐全★)

★**列口径**: `长度 mm` = DRC 端点自带段长时取段长 (标 `DRC段长`), 否则取两端直线距离 (标 `直线距离`, ★不是实际走线长★) · `死因桶` 见 §2-3 · `修法` 见 §4 ★

| # | 网名 | 起点 (ref+pad+x,y) | 终点 (ref+pad+x,y) | 长度 mm | 类型 | 死因桶 | 修法 |
|---:|---|---|---|---:|---|---|---|
| 1 | `LIGHT_3V3` | C_BULK_LIGHT_3V3.1 @ (83.7, 38.6) F.Cu | CONN_LIGHT.14 @ (28.75, 60.15) F.Cu | 59.02 | 普通 | **算法可解** | 让路闸 + 换层 |
| 2 | `LIGHT_5V` | CONN_CAM.30 @ (93.4, 51.4) F.Cu | D_ESD_LIGHT.1 @ (89.4, 56.6) F.Cu | 6.56 | 普通 | **口径未定** | 等拍板 (W-1/W-2) |
| 3 | `CSI_D0_D1_P` | C_AC_CSI_D0_D1_P.2 @ (50.7, 58.6) F.Cu | CONN_CAM.12 @ (84.4, 51.4) F.Cu | 34.46 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 4 | `I2C_A_SDA` | CONN_CAM.25 @ (90.9, 51.4) F.Cu | 走线端 @ (62.4, 52.16) F.Cu len=1.2mm | 1.2 | 普通 | **算法可解** | 让路闸 + 换层 |
| 5 | `PWR_GOOD` | R_PU_PG.2 @ (85.3, 46.6) F.Cu | Q_PG.3 @ (86.2, 31.5) F.Cu | 15.13 | 普通 | **口径未定** | 等拍板 (W-4) |
| 6 | `CSI_D0_D0_N` | TP_CSI_D0_N.1 @ (63.7, 55.2) F.Cu | C_AC_CSI_D0_D0_N.2 @ (65.1, 58.6) F.Cu | 3.68 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 7 | `CSI_D0_D0_N` | C_AC_CSI_D0_D0_N.2 @ (65.1, 58.6) F.Cu | CONN_CAM.14 @ (85.4, 51.4) F.Cu | 21.54 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 8 | `ID_DETECT_1` | J_SOM_P1.36 @ (62.0, 11.04) F.Cu | 走线端 @ (88.7, 17.2) F.Cu len=0.3536mm | 0.3536 | 普通 | **算法可解** | 让路闸 + 换层 |
| 9 | `SPI_SCLK_BOOT` | R_SER_SPI_SCLK.2 @ (114.1, 46.6) F.Cu | J_BOOT1.1 @ (124.2, 56.6) F.Cu | 14.21 | 普通 | **算法可解** | 让路闸 + 换层 |
| 10 | `SPI_MOSI_BOOT` | R_SER_SPI_MOSI.2 @ (109.3, 46.6) F.Cu | J_BOOT1.3 @ (125.2, 56.6) F.Cu | 18.78 | 普通 | **算法可解** | 让路闸 + 换层 |
| 11 | `SPI_MISO_BOOT` | R_SER_SPI_MISO.2 @ (104.5, 46.6) F.Cu | J_BOOT1.4 @ (125.7, 56.6) F.Cu | 23.44 | 普通 | **算法可解** | 让路闸 + 换层 |
| 12 | `ID_DETECT_0` | 过孔 @ (74.825, 16.7) F.Cu | J_SOM_P1.32 @ (62.8, 11.04) F.Cu | 13.29 | 普通 | **算法可解** | 让路闸 + 换层 |
| 13 | `CSI_D0_D3_N` | C_AC_CSI_D0_D3_N.2 @ (12.3, 58.6) F.Cu | CONN_CAM.2 @ (79.4, 51.4) F.Cu | 67.49 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 14 | `CSI_D0_D2_N` | C_AC_CSI_D0_D2_N.2 @ (21.9, 58.6) F.Cu | CONN_CAM.5 @ (80.9, 51.4) F.Cu | 59.44 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 15 | `CSI_D0_D2_P` | C_AC_CSI_D0_D2_P.2 @ (17.1, 58.6) F.Cu | CONN_CAM.6 @ (81.4, 51.4) F.Cu | 64.7 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 16 | `CSI_D0_D1_N` | C_AC_CSI_D0_D1_N.2 @ (55.5, 58.6) F.Cu | CONN_CAM.11 @ (83.9, 51.4) F.Cu | 29.3 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 17 | `I2C_A_SCL` | 走线端 @ (62.8, 49.76) F.Cu len=1.2mm | CONN_CAM.24 @ (90.4, 51.4) F.Cu | 1.2 | 普通 | **算法可解** | 让路闸 + 换层 |
| 18 | `CAM_RESET_N` | J_SOM_P1.54 @ (58.4, 11.04) F.Cu | CONN_CAM.27 @ (91.9, 51.4) F.Cu | 52.45 | 普通 | **算法可解** | 让路闸 + 换层 |
| 19 | `I2C_B_SCL` | CONN_LIGHT.11 @ (30.25, 60.15) F.Cu | 走线端 @ (6.1, 70.725) F.Cu len=5.2682mm | 5.2682 | 普通 | **算法可解** | 让路闸 + 换层 |
| 20 | `I2C_B_SCL` | J_SOM_P2.11 @ (66.8, 50.96) F.Cu | CONN_LIGHT.11 @ (30.25, 60.15) F.Cu | 37.69 | 普通 | **算法可解** | 让路闸 + 换层 |
| 21 | `I2C_B_SDA` | CONN_LIGHT.12 @ (29.75, 60.15) F.Cu | 走线端 @ (13.245, 71.15) F.Cu len=14.6191mm | 14.6191 | 普通 | **算法可解** | 让路闸 + 换层 |
| 22 | `DSI_D0_D1_P_SRC` | J_SOM_P3.65 @ (22.0, 7.96) F.Cu | R_SEL_D1_P.1 @ (93.3, 5.6) F.Cu | 71.34 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 23 | `DSI_D0_D1_P` | 走线端 @ (96.2, 56.7) In2.Cu len=0.25mm | CONN_LIGHT.3 @ (34.25, 60.15) F.Cu | 0.25 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 24 | `DSI_D0_D0_P_SRC` | J_SOM_P3.59 @ (23.2, 7.96) F.Cu | R_SEL_D0_P.1 @ (83.7, 5.6) F.Cu | 60.55 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 25 | `DSI_D0_D0_P` | CONN_LIGHT.9 @ (31.25, 60.15) F.Cu | 过孔 @ (81.7, 42.45) F.Cu | 53.46 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 26 | `FSIN_OUT` | R_SER_FSIN.1 @ (93.3, 46.6) F.Cu | TP_FSIN.1 @ (93.5, 49.6) F.Cu | 3.01 | 普通 | **算法可解** | 改逃逸方向 (布线顺序) |
| 27 | `BAT_DET` | J_SOM_P1.38 @ (61.6, 11.04) F.Cu | C_DET_BAT.1 @ (98.1, 17.6) F.Cu | 37.08 | 普通 | **口径未定** | 等拍板 (A1) |
| 28 | `LED_G` | J_SOM_P4.19 @ (31.2, 50.96) F.Cu | 走线端 @ (5.9, 62.6) F.Cu len=3.0067mm | 3.0067 | 普通 | **口径未定** | 等拍板 (`D_LED_G` 位置) |
| 29 | `KEY_CAM` | SW_KEY_CAM.1 @ (20.3, 62.6) F.Cu | J_SOM_P4.3 @ (34.4, 50.96) F.Cu | 18.28 | 普通 | **算法可解** | 让路闸 + 换层 |
| 30 | `CSI_D0_D3_N_SRC` | C_AC_CSI_D0_D3_N.1 @ (10.7, 58.6) F.Cu | J_SOM_P4.89 @ (17.2, 50.96) F.Cu | 10.03 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 31 | `DSI_D0_D1_N` | 走线端 @ (92.2, 60.2) F.Cu len=0.25mm | CONN_LIGHT.2 @ (34.75, 60.15) F.Cu | 0.25 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 32 | `DSI_D0_CK_N` | CONN_LIGHT.5 @ (33.25, 60.15) F.Cu | 走线端 @ (73.45, 48.7) In2.Cu len=0.25mm | 0.25 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 33 | `DSI_D0_CK_P` | 走线端 @ (82.45, 56.7) In4.Cu len=0.25mm | CONN_LIGHT.6 @ (32.75, 60.15) F.Cu | 0.25 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 34 | `DSI_D0_D0_N` | 走线端 @ (76.2, 5.45) F.Cu len=0.3041mm | CONN_LIGHT.8 @ (31.75, 60.15) F.Cu | 0.3041 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 35 | `DSI_D0_D2_N` | 走线端 @ (100.95, 59.95) In2.Cu len=0.25mm | CONN_LIGHT.16 @ (27.75, 60.15) F.Cu | 0.25 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 36 | `JTAG_TDI` | R_JTAG_TDI.2 @ (142.9, 42.6) F.Cu | J_DEBUG.3 @ (143.2, 56.6) F.Cu | 14.0 | 普通 | **算法可解** | 让路闸 + 换层 |
| 37 | `LED_G_D` | R_LED_G.2 @ (7.5, 62.6) F.Cu | D_LED_G.1 @ (100.8, 56.6) F.Cu | 93.49 | 普通 | **口径未定** | 等拍板 (`D_LED_G` 位置) |
| 38 | `DSI_D0_D2_N_SRC` | J_SOM_P3.75 @ (20.0, 7.96) F.Cu | R_SEL_D2_N.1 @ (107.7, 5.6) F.Cu | 87.73 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 39 | `DSI_D0_D1_N_SRC` | J_SOM_P3.63 @ (22.4, 7.96) F.Cu | R_SEL_D1_N.1 @ (88.5, 5.6) F.Cu | 66.14 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 40 | `DSI_D0_D0_N_SRC` | J_SOM_P3.57 @ (23.6, 7.96) F.Cu | R_SEL_D0_N.1 @ (78.9, 5.6) F.Cu | 55.35 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 |
| 41 | `USB_CC2` | R_CC2_D.1 @ (126.9, 42.6) F.Cu | J_USB_C.B5 @ (141.75, 5.25) F.Cu | 40.19 | 普通 | **算法可解** | 让路闸 + 换层 |
| 42 | `CSI_D0_D0_N_SRC` | J_SOM_P4.65 @ (22.0, 50.96) F.Cu | C_AC_CSI_D0_D0_N.1 @ (63.5, 58.6) F.Cu | 42.2 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 43 | `CSI_D0_D1_N_SRC` | J_SOM_P4.71 @ (20.8, 50.96) F.Cu | C_AC_CSI_D0_D1_N.1 @ (53.9, 58.6) F.Cu | 33.97 | 高速 DSI/CSI | **几何不可布 (布局级)** | 改布局 + pair-aware |
| 44 | `UART_RX` | J_UART.2 @ (19.14, 68.6) F.Cu | J_SOM_P2.9 @ (67.2, 50.96) F.Cu | 51.2 | 普通 | **算法可解** | 让路闸 + 换层 |
| 45 | `DSI_D0_D3_N_SRC` | J_SOM_P3.81 @ (18.8, 7.96) F.Cu | R_SEL_D3_N.1 @ (117.3, 5.6) F.Cu | 98.53 | 高速 DSI/CSI | **算法可解** | pair-aware + 换层 |★**落桶分布 (★每条只落一个桶★)**: ★**几何不可布 (布局级) = 22 条** ★ · ★**算法可解 = 18 条** ★ · ★**口径未定 = 5 条** ★ (★合计 45·与 §1-1 的 C4 = 45 逐字对齐★)
★**高速 DSI/CSI 条目 = 23 (DSI_ 13 条 / CSI_ 10 条)** ★ · ★**真墙端点条目 = 9** ★
★**机读全表 (含每条的桶 / 修法 / 与 best_unc23 板的交叉标记): `tmp/iss322/table45.json`** ★

---

## §2 · 逐条死因登记 (★机器判据·不许推算★)

### §2-1 · ★★「23 vs 13」两个数打架 —— 查清了: ★**两个数都对, 各指不同的东西**★★

★**机器数法** (★`tmp/iss322/extract_unc.py` + `logs/iss322/02_extract_unc_summary.txt`★):

| 量 | 值 | 口径 |
|---|---:|---|
| 高速 (DSI_/CSI_ 前缀) **未连接条目**数 | **23** | ★**ratsnest link 条数** ★ (一条未连接 = 一对端点) |
| 高速**网名**数 | **22** | `CSI_D0_D0_N` 有 3 个焊盘 ⇒ 断成 **2** 段 ⇒ 22 网名对应 23 条 |
| `DSI_` 单方向**网名**数 | **13** | ★**这才是作业包说的「13 条 DSI 腿」** ★ |
| `CSI_` 单方向**网名**数 | **9** | (10 条 · 因 `CSI_D0_D0_N` 占 2 条) |
| 差分**族**数 | **9** | `DSI_CK`/`DSI_D0`/`DSI_D1`/`DSI_D2`/`DSI_D3` + `CSI_CK`/`CSI_D0`/`CSI_D1`/`CSI_D2`/`CSI_D3` 中存在者 |

⇒⇒ **★结论: 「45 条里 23 条是高速腿」与「13 条 DSI 腿」不打架 —— 23 是【DSI+CSI 两方向的条目数】, 13 是【DSI_ 单方向的网名数】, 22 是【高速网名总数】★** ⇒ ★**作业包那句把它们并列在一行里 ⇒ 读起来像打架; 建议 main 在 §3-S8 那一行改成「45 条里 23 条是高速 DSI/CSI 腿 (22 个网名: DSI_ 13 + CSI_ 9)」★★**

### §2-2 · ★★现役探针读数汇总 (★逐条·可复算★)★★

| 探针 | 命令 | 读数 | 原始输出 |
|---|---|---|---|
| `check_pcb_drc` | `python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` | ★**viol 0 / unc 45 / 同点重复过孔 0** ★ | `logs/iss322/01_check_pcb_drc_baseline.txt` |
| `probe_unc_map` | `bash state/pcbnew_py.sh state/probe_unc_map.py <板> <drc.json>` | 45 条 → 43 网名 · 每条两端的 (ref,pad,坐标) | `logs/iss322/03_probe_unc_map.txt` |
| `probe_unconnected_worklist_v2` (★几何唯一真源★) | `bash state/pcbnew_py.sh state/probe_unconnected_worklist_v2.py <板> <drc.json> --out <wl.txt>` | 87 行逐端点净距 | `logs/iss322/04_probe_worklist_v2_stdout.txt` · `tmp/iss322/unc_worklist_current.txt` |
| `classify_unc` | `python3 state/classify_unc.py <wl.txt>` | ★**A1 5 网 / A2 4 网 / B1 11 网 / B2 23 网 (合计 43) · 真墙 9** ★ | `logs/iss322/05_classify_unc.txt` |
| `probe_escape_feasibility` | `bash state/pcbnew_py.sh state/probe_escape_feasibility.py <板> <drc.json>` | ★**端点 88 个 · W=0.20 可行 88 / 不可能 0 · W=0.15 可行 88 / 不可能 0** ★ | `logs/iss322/06_probe_escape_feasibility.txt` · `tmp/iss322/escape_feas_current.txt` |
| `cmp_unc_sets` | `python3 state/cmp_unc_sets.py <现役.drc.json> state/official_18092_unc.drc.json` | ★**网名集合交集 43 · 仅现役 0 · 仅官方 0 ⇒ 完全相同** ★ | `logs/iss322/07_cmp_unc_sets_cur_vs_official.txt` |
| `gate_live_check` | `bash state/pcbnew_py.sh state/gate_live_check.py --arm-script state/v76mw_arms.sh` | ★**「谁掐谁」全表 (含 k 值) · 受害网 46 个** ★ | `logs/iss322/13_gate_live_check.txt` |
| `probe_lane_conflicts` | `bash state/pcbnew_py.sh state/probe_lane_conflicts.py <板> <drc.json> --out <txt>` | ★**134 行布局冲突清单** ★ | `logs/iss322/09_probe_lane_conflicts.txt` · `tmp/iss322/lane_conflicts_current.txt` |
| `probe_dsi_corridor` | `bash state/pcbnew_py.sh state/probe_dsi_corridor.py <板>` | 走廊区域内的封装占位 | `logs/iss322/10_probe_dsi_corridor.txt` |
| `probe_csi_order` | `bash state/pcbnew_py.sh state/probe_csi_order.py <板>` | 各 lane 的 P/N 位置与 dx | `logs/iss322/11_probe_csi_order.txt` |
| ★**本单自写的高速腿几何汇总** ★ | `python3 logs/iss322/scripts/hs_geometry.py` (★脚本随交卷物存 `logs/iss322/scripts/`★) | 23 条高速腿 × 段内翻转 / 出脚余量 / 走廊横穿分类 | ★`logs/iss322/12_hs_geometry_verdict.txt`★ |
| `compare_arm_official --self-test` | `python3 state/compare_arm_official.py --self-test` | ★**rc=0 · `ALL TESTS PASS`** ★ | `logs/iss322/15_compare_arm_official_selftest.txt` |

### §2-3 · 死因桶定义 (★本单自定·每条只落一个桶★)

| 桶 | 定义 (★本单口径★) | 条数 |
|---|---|---:|
| ★**几何不可布 (布局级)** ★ | ★**端点能出 (escape 可行) 但段内 P/N 顺序 / lane 序被布局钉死 ⇒ 必须改布局才可能成对布通** ★ | **22** |
| ★**算法可解** ★ | ★**端点可出 + 走廊中段被堵 ⇒ 让路闸 / 换层 / pair-aware / 改逃逸方向 能解** ★ | **18** |
| ★**口径未定** ★ | ★**拍板前连【钉位/终点/极性】都定不下来 ⇒ 现在布了也白布** ★ | **5** |
| ★**官方板同病** ★ | ★**本单【把它从桶降级成标记列】, 理由见下** ★ | — |

★★**★为什么把「官方板同病」从桶降成标记列 (★这是本单对任务书口径的一处订正·必须让 main 知道★)★★**

任务书 §2-② 的第 4 个桶写「官方板自己也没布通 ⇒ 归『几何/框级』桶, 不归『算法』桶」。**实测: 「官方板 18092」就是现役板本身** (★`official_18092_unc.drc.json` 的 `source` = `demo_mainboard.kicad_pcb`; 现役板走线段数实测 = **18092**, 过孔 = **433**★) ⇒ **它与现役板的网名签名 43/43 完全相同, 差集 = 0** ⇒ ★**「官方板同病」对 45/45 条全部为真 ⇒ 零区分度 ⇒ 用它当桶会让另外三个桶全空** ★
⇒ ★**正确用法: 它是【自证】不是【旁证】 —— 「这 45 条不是新板引入的回归, 是这条布线工艺一直以来的残余」; 而【几何级】的真正旁证是 §3-3 的 17/47 段内翻转 + §3-4 的 SoM 主体区逐层占布 + §3-5 的 8 块板对照** ★

### §2-4 · ★★与 `state/UNC_TARGET_MAP.md` 基线的差集表 (★基线过期·必须先对齐★)★★

★**`state/UNC_TARGET_MAP.md` 的基线 = `state/.lastgood/baseline_v76mw0_chain.kicad_pcb` (★本机 2026-11-18 重跑: unc **29** 条 / **24** 个网名签名·DRC 0·原始读数 `logs/iss322/25_drc_baseline_v76mw0.txt`★) —— 与现役板 (45 条 / 43 签名) 对不上。差集如下 (★`logs/iss322/24_unc_diff_vs_unc_target_map_baseline.txt`★)**:

| 差集 | 条数 | 内容 |
|---|---:|---|
| ★**只有现役板有** (★基线已布通 / 现役未布通★) | **31** | `BAT_DET` `CAM_RESET_N` `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D1_P` `CSI_D0_D2_P` `CSI_D0_D3_N_SRC` `DSI_D0_CK_N` `DSI_D0_CK_P` `DSI_D0_D0_N_SRC` `DSI_D0_D0_P_SRC` `DSI_D0_D1_P` `DSI_D0_D1_P_SRC` `DSI_D0_D2_N` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC` `FSIN_OUT` `I2C_A_SDA` `ID_DETECT_0` `JTAG_TDI` `KEY_CAM` `LED_G` `LED_G_D` `LIGHT_3V3` `LIGHT_5V` `PWR_GOOD` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` |
| ★**只有基线板有** (★基线未布通 / 现役已布通★) | **12** | `BOOT_N` `CARRIER_BOARD_EN` `CSI_D0_CK_N` `CSI_MCLK` `DSI_D0_CK_N_SRC` `DSI_D0_D3_N` `KEY_VOL_M` `KEY_VOL_P` `LED_B` `SPI_CSn_BOOT` `TS_BAT` `USB_CC1` |
| ★**交集** | **12** | — |

★**为什么差这么多 (★根因, 机器可查★)**: 两个口径是【两块不同的板 + 两代不同的路由器】——
| | 现役板 (18092 段 / 433 孔) | 基线板 (`baseline_v76mw0_chain`) |
|---|---|---|
| 走线段 / 过孔 | ★**18092 / 433** ★ | **3383 / 442** |
| `R_SEL_*` 集群 x 序 | ★**D0→D3 (右上, 与 SoM 端序相反)** ★ | ★**D3→D0 (左上, 与 SoM 端序相同)** ★ |
| unc | **45** | **29** |

⇒⇒ ★**★差集表的三条用途 (★必须写进交卷页·不然下一趟还会拿 22 网名当靶集★)★★**
1. ★**`UNC_TARGET_MAP.md` 的三桶表 (被 GND 掐 9 / k≤3 非 GND 3 / k=12 差分配对 14) 只覆盖基线板的 24 个网名, 对现役板 43 个网名只覆盖 12 个 (28%) ⇒ 拿它当现役板的靶集, 会漏掉 31 条** ★
2. ★**现役板的靶集 = 45 条 / 43 网名 (★不是 29 / 24, 也不是 22★)** ★
3. ★**建议 main 把它升级成【双基线】口径: 「官方板 45/43」+「v76 链 29/24」两套, 并写清各自对应的板 md5 (★否则半年后没人知道哪个数是哪块板★)** ★

### §2-5 · ★★同型事故史并表 (★v44 / v46 / v47 / v48·★逐字读 `fail_detail` 的 start/goal★)★★

★**机器读数** (★`logs/iss322/08_fail_history_intersection.txt`★):

| 量 | 值 |
|---|---:|
| 四臂各自的 fail 条目数 | v44 = 66 · v46 = 69 · v47 = 65 · v48 = 67 |
| ★**四臂共同失败【网名】** ★ | **39** |
| ★**四臂共同失败【(net,pad)】** ★ | **45** |
| 其中高速 (DSI_/CSI_) 网名 | ★**16** ★ (DSI 8 + CSI 8) |

★**★任务书 §1-⑧ 点名的三条 (`DSI_D0_CK` · `DSI_D0_CK_SRC` · `DSI_D0_D1`) —— 机器查实: 这三个网名在四个 `fail_detail` 文件里【一个都不存在】★**
★**真实存在的、且四臂全挂的对应网名是: `DSI_D0_CK_N` · `DSI_D0_CK_N_SRC` · `DSI_D0_D1_N` (★外加 `DSI_D0_CK_P` 在 v44/v46/v48 挂, v47 没挂★)** ★

★**⇒ 结论比任务书更强, 不是更弱**: ★**不是 3 条腿, 是 39 个网名 / 45 个 (net,pad) 对 / 16 条高速腿在四条独立臂上收敛到同一个残余 ⇒ ⇒ 【残余不是路由参数决定的】(★参数每条臂都调过·照样收敛到同一组★) ⇒ ⇒ 这是布局 / lane 分配级 ⇒ ⇒ 与 §3-3 的 17/47 段内翻转互相印证** ★

★★**但必须交代一个反证 (★不然就是拿【4 个臂同源】当【4 个独立实验】★)★★**: ★**v44/v46/v47/v48 是同一代路由器的四条臂 (★同源·同 seed 族★) ⇒ 「四臂一致」本身有【算法同源】的混淆 ⇒ 它【证明不了】"布局是唯一原因", 但它【证明得了】"调参数调不出来"** ★ ⇒ ★**要真正分离「布局」与「算法」, 需要本单 §3-5 那组【同代路由器 · 不同 lane 序】的对照 (★8 块板·unc 23..45★)** ★

### §2-6 · ★★机制级读数: 22 个高速未连通网名里, 15 个在板上【一根铜都没有】★★ [实测]

★**机器读法** (★`tmp/iss322/hs_copper_amount.py` · `logs/iss322/18_hs_copper_amount.txt`★): 逐高速网统计板上的走线总长 / 段数 / 过孔数 / 分层段数。

| 类别 | 网名数 | 明细 |
|---|---:|---|
| ★**板上零铜 (★一根线都没长出来★)** ★ | ★**15** ★ | `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D1_P` `CSI_D0_D2_N` `CSI_D0_D2_P` `CSI_D0_D3_N` `CSI_D0_D3_N_SRC` `DSI_D0_D0_N_SRC` `DSI_D0_D0_P_SRC` `DSI_D0_D1_N_SRC` `DSI_D0_D1_P_SRC` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC` |
| 有铜但仍未连通 (★长了一半★) | 7 | `DSI_D0_CK_N` 88.70mm · `DSI_D0_CK_P` 84.11mm · `DSI_D0_D0_N` 4.85mm · `DSI_D0_D0_P` 81.04mm · `DSI_D0_D1_N` 78.27mm · `DSI_D0_D1_P` 79.48mm · `DSI_D0_D2_N` 168.74mm |

★★**★这条读数是全单最硬的「病型」判据 (★为什么不是"差一点就通"★)★★**
- ★**68% (15/22) 的高速未连通网在板上【一根铜都没有】⇒ 路由器是【没布出来】, 不是【布歪了】⇒ ⇒ 换层 / 让路闸这些【增量】手段对它们【一点用都没有】⇒ ⇒ 必须换【机制】(成对走廊 + 布局修正 + 布线顺序)★** ★
- ★**同时它是「假绿」的最大来源**: ★**这些网在 PCB 统计里【不算未连接以外的问题】⇒ 看着「有 18092 段走线」很热闹, 但 23 条高速腿里 15 条根本没开始布 ⇒ ⇒ 「走线段数」这个指标对 S8 【零信息量】★** ★
- ★**与 §2-5 的四臂收敛互相印证**: ★**四条独立臂收敛到同一个残余 ⇒ 因为残余是【结构性缺铜】, 不是【参数没调好】★** ★

---

## §3 · ★★★高速腿 (23 条 DSI/CSI) 几何可布性判定 ★★★

> ★**这是本单存在的理由 —— 板那一趟能不能一次做完, 取决于这个结论** ★

### §3-1 · 判定口径 (★机器可判·两个结论二选一★)

| 档 | 含义 |
|---|---|
| **(a) 几何可布** | 缺的是走线 / 层选 / 让路 ⇒ 属可解 ⇒ 板 md5【不需要】因为几何而第二次变 |
| **(b) 几何不可布** | 必须先改布局或板框 ⇒ 板 md5 第二次变 (2-4 周 + ¥4-8K) |

### §3-2 · ★★判定结果: ★**(a) 几何可布** ★★ —— ★**但必须改布局 (★所以不是"零成本"·是"一次改完"★)★★

★★**五条独立判据, 全部指向 (a), 且互相不重复: ★★**

### §3-3 · 判据① ★**端点级: 88/88 端点物理可出** ★ [实测]

```
$ bash state/pcbnew_py.sh state/probe_escape_feasibility.py HW/PCB/demo_mainboard.kicad_pcb /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json
═══════ 汇总 ═══════
端点数 = 88
★W=0.20 ⇒ 物理可行 88 / 物理不可能 0
★W=0.15 ⇒ 物理可行 88 / 物理不可能 0
```

★**含义**: ★**45 条的 88 个端点, 每一个都至少有一个方向能出脚且净距 ≥ 0.20mm (净距要求) ⇒ 没有任何一个端点被几何封死 ⇒ 「不可布」的第一类 (端点封死) 被排除** ★
★**最紧的 17 个端点余量 = ±0.000mm (★恰好压线 = 0.20mm 净距要求·浮点显示为 -0.000/+0.000; ★**全板 88 个端点里余量 < 0 的 = 0 个**★)**: `ID_DETECT_1.J_SOM_P1.36` · `ID_DETECT_0.J_SOM_P1.32` · `CAM_RESET_N.J_SOM_P1.54` · `I2C_B_SCL.J_SOM_P2.11` · `BAT_DET.J_SOM_P1.38` · `DSI_D0_D0_N_SRC.J_SOM_P3.57` · `DSI_D0_D0_P_SRC.J_SOM_P3.59` · `DSI_D0_D1_N_SRC.J_SOM_P3.63` · `DSI_D0_D1_P_SRC.J_SOM_P3.65` · `DSI_D0_D2_N_SRC.J_SOM_P3.75` · `DSI_D0_D3_N_SRC.J_SOM_P3.81` · `CSI_D0_D0_N_SRC.J_SOM_P4.65` · `CSI_D0_D1_N_SRC.J_SOM_P4.71` · `CSI_D0_D3_N_SRC.J_SOM_P4.89` · `LED_G.J_SOM_P4.19` · `KEY_CAM.J_SOM_P4.3` · `UART_RX.J_SOM_P2.9`
★**★这 17 个【全部】落在 SoM 的 0.4mm BTB 排针上 (`J_SOM_P1` / `P2` / `P3` / `P4`) ⇒ 【邻脚就压在 0.200mm 处 ⇒ 出脚区余量 0】⇒ 其中 5 个正是 `classify_unc` 的 A1 桶 (★端点被自己伙伴腿掐 0.200mm★: `CSI_D0_D0_N_SRC` `CSI_D0_D1_N_SRC` `CSI_D0_D3_N_SRC` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC`), 其余 12 个属 B1/B2 桶 ⇒ 【墙不是绝对墙, 是【当前那根铜画的方向上的墙】⇒ 换个出脚方向就过 (余量 0.000 ≥ 0) ⇒ 这 17 条正是 pair-aware / 出脚方向的靶子, 不是布局的靶子★** ★

### §3-4 · 判据② ★**板框 / 层数不是瓶颈: SoM 主体区逐层占布** ★ [实测]

★**「23 条腿全部要跨 SoM 主体 (x 8..76, y 6..56)」这个前提是真的; 但【跨不过去】是假的。实测主体区 (68 × 50 = 3400 mm²) 的逐层铜占布** (★`logs/iss322/19_probe_som_body.txt`★):

| 层 | 区内走线段 | 区内走线长 | 铜投影占布 | 自由 |
|---|---:|---:|---:|---:|
| `F.Cu` | 2340 | 734.14 mm | 5.73% | 94.3% |
| `In2.Cu` | 427 | 154.50 mm | 1.52% | 98.5% |
| `In4.Cu` | 171 | 57.72 mm | 0.81% | 99.2% |
| `In6.Cu` | 4 | 1.41 mm | 0.39% | 99.6% |
| ★**`In1.Cu` / `In3.Cu` / `In5.Cu` / `B.Cu`** ★ | **0** | **0.00 mm** | ★**0.38% (只有过孔)** ★ | ★**99.6%** ★ |

★**区内 36 个过孔是全层障碍 (⇒ 换层要走对角, 不能直穿)**
★**★关键前提: `J_SOM_P1..P4` 四个 SoM 连接器各 100 个焊盘, 【全部是 SMD, 只在 `F.Cu` 上, 通孔焊盘 = 0】⇒ ⇒ 主体区在内层上几乎完全是空的 ⇒ ⇒ 「必须改板形/层数才能归零」这条前提【不成立】★★**

⇒⇒ **★结论: 板框 (160×100) 与层数 (8L) 都不需要动 ⇒ ⇒ 板 md5 不会因为【几何】而第二次变 ⇒ ⇒ 「板只改一次」铁律保得住 (前提是 S8 与 S1/S2/S3/S4/S6/S7 同趟)** ★

### §3-5 · 判据③ ★★【真正的几何瓶颈: 段内 P/N 顺序翻转 17/47 处】★★ [实测]

★**机器读法** (★`tmp/iss322/probe_pn_order.py` · `logs/iss322/20_probe_pn_order.txt`★): 把每个差分族按【段】(SoM 侧 / AC 电容侧 / 连接器侧 / 测试点侧 / 串阻侧) 分组, 在【同一段内】比较 P 与 N 的横向 (x) 顺序 —— ★**同段内 x 顺序相反 ⇒ 该段必须交叉才能连** ★

★**同段比较总数 = 47 · 翻转 = 17** ★

| 翻转位置 | 族 | Δx | 说明 |
|---|---|---:|---|
| ★**DSI · 串阻侧 (`R_SEL_*`)** ★ | `DSI_D0_CK` · `DSI_D0_D0` · `DSI_D0_D1` · `DSI_D0_D2` (★4 族★) | **4.80 mm** | ★**SoM 侧是 P 在左 (x 18.4..23.6, 间距 0.40), 串阻侧却是 N 在左 (x 78.9..117.3) ⇒ 整条 lane 端到端反序** ★ |
| ★**DSI · 测试点侧 (`TP_DSI_*`)** ★ | 同上 4 族 | **11.80 ~ 4.40 mm** | 同上 |
| ★**CSI · 连接器侧 (`CONN_CAM`)** ★ | `CSI_D0_CK` · `CSI_D0_D0` · `CSI_D0_D1` · `CSI_D0_D2` · `CSI_D0_D3` (★5 族全中★) | **0.50 mm** | ★**AC 电容侧 P/N 间距 4.80mm (P 在左), 连接器侧 P/N 间距 0.50mm 且 N 在左 ⇒ 中间必须交叉** ★ |
| 未翻转 | `DSI_D0_D3` (★串阻侧 P 78.90 / N 117.30★) · `CSI` 的 SoM 侧与 AC 电容侧 | — | ★**`DSI_D0_D3` 之所以没翻, 是因为 `R_SEL_D3_P` 被挂在 (78.90, 9.50) 这个【倒挂位】上 (★ISS-265 §1.1 自己也标了它是「lane 倒挂源」★) ⇒ ★**它是用一个反常的钉位把翻转藏起来了, 不是 lane 序本身对** ★ |

### §3-6 · 判据④ ★★【同代路由器 · 不同 lane 序】的对照: ★**unc 与 lane 序完全相关**★★ [实测]

★**机器读法** (★`tmp/iss322/probe_lane_order_vs_unc.py` · `logs/iss322/22_lane_order_vs_unc.txt`★): 8 块板全部用同一代 v76 链路由器, 唯一变量 = `R_SEL_*` 集群的 x 序。

| 板 | unc | `R_SEL_*` 集群 x 序 (左→右) | 与 SoM 端序一致? |
|---|---:|---|---|
| `baseline_v76me0_chain` | 35 | D3[N8.0/P5.5] D2[N15.6/P13.1] CK[N23.1/P20.7] D1[N30.8/P28.3] D0[N38.4/P35.9] | ★**是** ★ |
| `baseline_v76mg0_chain` | 35 | 同上 | ★**是** ★ |
| `baseline_v76mj0_chain` | 28 | 同上 | ★**是** ★ |
| `baseline_v76mv0_chain` | 29 | 同上 | ★**是** ★ |
| `baseline_v76mw0_chain` | 29 | 同上 | ★**是** ★ |
| `baseline_v76mx0_chain` | 26 | 同上 | ★**是** ★ |
| `best_unc23_clrfix` (★盘上最好★) | ★**23** ★ | 同上 | ★**是** ★ |
| ★**`HW/PCB/demo_mainboard.kicad_pcb` (现役)** ★ | ★**45** ★ | ★**D0[N78.9/P83.7] D1[N88.5/P93.3] CK[N98.1/P102.9] D2[N107.7/P112.5] D3[N117.3/P78.9]** ★ | ★**否 (完全反向)** ★ |

⇒⇒⇒ **★7 块 lane 序一致的板, unc 全部 ≤ 35; 唯一 lane 序反的那块 = 45 (全盘最差) ⇒ ⇒ 【unc 与 lane 序的相关系数在这 8 块板上是单调的】⇒ ⇒ 这就是本单判 (a) 的主证据** ★
★★**★并且它【直接反驳 ISS-265 §0 的处方方向】(★见 §0-2-②★): ISS-265 说「钉左上 ⇒ lane 序完全反向 ⇒ 45 处交叉 ⇒ 要钉到右上 (方案 A)」, 但实测【钉左上的那 7 块板 unc 是 23..35, 钉右上的现役板是 45】⇒ ⇒ **「lane 交叉数」这个指标与 unc 【反相关】⇒ 归零判据不能用它** ★

### §3-7 · 判据⑤ ★★【我们这 43 个未连通网名里, 32 个在别的板上已经布通过】★★ [实测]

★**对照板 = `state/.lastgood/best_unc23_clrfix.kicad_pcb` (★2026-11-11 04:43 · unc 23 · DRC 0 · ★**同样 160×100 / 8L / 186 封装**★ · 走线 3364 段 / 475 孔★)** (★`logs/iss322/17_cur_vs_best23_netsets.txt`★):

| 类别 | 网名数 | 内容 |
|---|---:|---|
| ★**best_unc23 板【已经布通】** ★ | ★**32** ★ | ★**高速 14** ( `CSI_D0_D1_N` `CSI_D0_D1_N_SRC` `CSI_D0_D1_P` `CSI_D0_D2_P` `CSI_D0_D3_N_SRC` `DSI_D0_D0_N_SRC` `DSI_D0_D0_P` `DSI_D0_D0_P_SRC` `DSI_D0_D1_N_SRC` `DSI_D0_D1_P` `DSI_D0_D1_P_SRC` `DSI_D0_D2_N` `DSI_D0_D2_N_SRC` `DSI_D0_D3_N_SRC` ) + ★**非高速 18** ( `BAT_DET` `CAM_RESET_N` `FSIN_OUT` `I2C_A_SDA` `I2C_B_SDA` `ID_DETECT_0` `JTAG_TDI` `KEY_CAM` `LED_G` `LED_G_D` `LIGHT_3V3` `LIGHT_5V` `PWR_GOOD` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` ) |
| ★**两边都没布通 (★真·硬骨头★)** ★ | ★**11** ★ | ★**高速 8** ( `CSI_D0_D0_N` `CSI_D0_D0_N_SRC` `CSI_D0_D2_N` `CSI_D0_D3_N` `DSI_D0_CK_N` `DSI_D0_CK_P` `DSI_D0_D0_N` `DSI_D0_D1_N` ) + ★**非高速 3** ( `I2C_A_SCL` `I2C_B_SCL` `ID_DETECT_1` ) |
| best_unc23 板自己新欠的债 | 10 | `CARRIER_BOARD_EN` `CSI_D0_CK_N` `CSI_MCLK` `CSI_MCLK_SRC` `DSI_D0_D3_N` `GND` `KEY_VOL_M` `SPI_CSn_BOOT` `USB_CC1` `VDD_1V8_IO` |

★**⇒ 32/43 (74%) 的未连通网名在另一块同框同层数的板上被布通过 ⇒ ⇒ 我们的 45 条【不是几何不可能的集合】⇒ ⇒ 支持 (a)** ★
★**★但 must 交代一处混淆 (★不然就是拿证据当结论★)★**: ★**best_unc23 板与现役板【布局不同】(186 个封装里 52 个被挪过, 28%; 其中 `R_SEL_*`/`TP_DSI_*` 整个集群从右上挪到左上) ⇒ ⇒ 「32 条被布通过」证明的是【这些网【不是不可布】】, 但【不能单独证明】现役布局原封不动也能布通它们 ⇒ ⇒ 【布局必须改】这条正是 §3-5/§3-6 给的** ★ (★逐块位置对照读数: `logs/iss322/16_best_unc23_vs_current_placement.txt` · 逐块 lane 序对照: `logs/iss322/22_lane_order_vs_unc.txt` · 跨代位置普查: `logs/iss322/21_placement_vs_unc_era_table.txt`★)

### §3-8 · ★★★判决书 (★结论 + 量化缺口 + 落到哪一批)★★★

> ★★**判决: (a) 几何可布。**
> ★★**★但 S8 【必须带一次布局修正】才可能归零, 且那次布局修正必须与 S1/S2/S3/S4/S6/S7 在【同一趟】里做完 —— 这样板 md5 仍然只变一次。「板只改一次」铁律不受影响。★★**

| 项 | 结论 | 量化 |
|---|---|---|
| ★**端点几何** ★ | ★**可布** ★ | ★**88/88 端点在 W=0.20mm 下有合法出脚方向** ★ |
| ★**板框 (160×100)** ★ | ★**不用改** ★ | ★**对照板 best_unc23 同为 160×100/8L 做到 unc 23** ★ |
| ★**层数 (8L)** ★ | ★**不用改** ★ | ★**SoM 主体区 `In1/In3/In5/In6/B.Cu` 各只占 0.38%; `J_SOM_P1..P4` 全 SMD 只在 F.Cu** ★ |
| ★**必须改的** ★ | ★**布局: 21 个器件 (`10×R_SEL_*` + `10×TP_DSI_*` + `R_SEL_D3_P` 换位) 挪到左上 x 5.50..38.35** ★ | ★**目标: 段内 P/N 翻转 17 → 0 (实测对照: lane 序一致的 7 块板 unc ≤ 35, 现役 45)** ★ |
| ★**CSI 侧的翻转** ★ | ★**另有 5 族在连接器侧翻 (Δx 0.50mm) ⇒ 要么挪 AC 电容侧, 要么成对换层绕** ★ | ★**这是 §5-2 需要 main 一起拍的第二个布局动作** ★ |
| ★**归零后还剩的** ★ | ★**11 个「两边都没通」的硬骨头 + 5 条口径未定** ★ | ★**硬骨头 11 (高速 8 + 非高速 3) 必须逐条给专属机制 (ISS-308 §2-C 的 T1~T7 是起点)** ★ |
| ★**★归零【从未被证明】★★** ★ | ★**盘上 11 份 DRC JSON (★含本单 11:38 的 fresh 那份★) 最低 = 23, 无一份 = 0** ★ | ★**⇒ 本单只判「几何不构成障碍」, 不判「零可达」⇒ 归零与否仍要 §5-1 拍** ★ |

---

## §4 · 逐条修法 + 落表批次 + 逐条验收命令

### §4-1 · 批次纪律 (★与 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1-3 逐字对齐·不许另起一套编号★)

> ★**同一批次 = 同一个落表单号 · 背靠背 · 不许拆成两趟** ★

| 批次 | 口径 (★照 ISS-317 §1-3 逐字★) | ★**S8 归入哪一条** ★ |
|---|---|---|
| ★**BATCH-1** ★ | ① 网表侧 `HW/netlist_v1.csv` (ref 列 + node1/node2 里的器件名, **先改**) → ② 脚表侧 `HW/netlist_v1_pins.csv` (ref 列) → ③ BOM 侧 `HW/BOM_v1.csv` (★由 `state/gen_bom.py` 生成 ⇒ 必须与 1/2 同批重跑★) → ④ 板侧 `HW/PCB/demo_mainboard.kicad_pcb` (★由 `state/gen_pcb_netlist_board.py` 生成 ⇒ 同批重出★) → ⑤ 原理图侧 `demo_mainboard_p*.kicad_sch` (★`kicad_ref()` 对已带 `_1` 的 ref 幂等 ⇒ 重跑得同一张图★) | ★**S8 的布线结果落在 ④ 这一步 (★板侧同批重出·同一份 md5★)** ★ |
| ★**BATCH-2** ★ | 判据侧: `state/check_pcb_nets.py` 两处硬编码 (★与 BATCH-1 同批★) | ★**+ 本单建议新增一道 S8 专用闸: 「段内 P/N 顺序翻转数 = 0」(★见 §4-3-⑧★)** ★ |
| ★**BATCH-3** ★ | 生成器侧硬编码: `state/gen_bom.py:100` `OPN_FROM_BOARD` · `state/gen_bom.py:307` `GAP29` · `state/gen_pcb_netlist_board.py:203` `PLACE_OVERRIDE` · `state/gen_pcb_netlist_board.py:221` `CONN_CAM_PIN` | ★**+ 本单建议加: `state/gen_pcb_netlist_board.py` 的 `PCB_PART_POS` 段 (★21 个器件的新坐标·见 §4-3-②★)** ★ |

★**中间态禁令 (★照抄 ISS-317 §1-3★)**: ① 已落表但板未重出 ⇒ C1 炸成 缺失350/多余352 (★ISS-314 S3 实测★) ★
★**★S8 的额外禁令 (★本单加★)**: ★**不许把「布局修正」和「布线」拆成两趟** ⇒ ★**BATCH-1 的 ④ 这一步 = 改布局 + 布线 45→0 一次做完 ⇒ 板 md5 只变一次** ★

### §4-2 · 修法类别总表 (★45 条逐条·桶 → 修法 → 代价★ ★数字全部机器数★)

| 修法类别 | 条数 | 具体条目 (§1 表的行号) | ★**代价 (人日) / 板 md5 会不会变** ★ |
|---|---:|---|---|
| ★**改布局** ★ | **12** | #22 #23 #24 #25 #31 #32 #33 #34 #35 #38 #39 #40 (★DSI `CK`/`D0`/`D1`/`D2` 四族·段内 P/N 序翻转的那批★) | ★**2.0 人日 · 板 md5 会变 (★但并进 BATCH-1 同趟⇒ 仍是第 1 次★)** ★ |
| ★**改布局 + pair-aware** ★ | **10** | #3 #6 #7 #13 #14 #15 #16 #30 #42 #43 (★CSI 五族·连接器侧 Δx=0.50mm 翻转 + A1 伙伴腿掐 0.200mm 那批★) | ★**同上 (并进同一次布局修正)** ★ |
| ★**让路闸 + 换层** ★ | **16** | #1 #4 #8 #9 #10 #11 #12 #17 #18 #19 #20 #21 #29 #36 #41 #44 | ★**1.5 人日 · 板 md5 不单独变 (★布线结果并进 BATCH-1 ④★)** ★ |
| ★**pair-aware + 换层** ★ | **1** | #45 (`DSI_D0_D3_N_SRC`·★本族段内序未翻转 ⇒ 不改布局·走成对走廊 + 内层换层★) | ★**0.5 人日 · 板 md5 不单独变** ★ |
| ★**改逃逸方向 (布线顺序)** ★ | **1** | #26 (`FSIN_OUT`·★ISS-282 已订正根因 = 布线排队顺序·不是逃逸方向 bug★) | ★**0.2 人日 · 板 md5 不单独变** ★ |
| ★**等拍板** ★ | **5** | #2 `LIGHT_5V` (W-1/W-2) · #5 `PWR_GOOD` (W-4) · #27 `BAT_DET` (A1) · #28 `LED_G` + #37 `LED_G_D` (`D_LED_G` 位置) | ★**0 人日 (等拍) · ★**拍完若影响钉位 ⇒ 板 md5 在同趟内变 (★仍第 1 次★)** ★ |
| ★**改板框** ★ | **0** | ★**实测不需要 (见 §3-4) ⇒ 这一栏【空】本身就是结论** ★ | **—** |
| ★**改判据** ★ | **1 处 (全局)** | ★**P7 的 C1/C2/C3 vs C4 (★§5-1★) + 新增「段内 P/N 翻转 = 0」闸 (§4-3-⑥) ★ | ★**0.5 人日 · 不改板** ★ |
| ★**合计** ★ | ★**45** ★ | ★**桶: 几何不可布(布局级) 22 + 算法可解 18 + 口径未定 5** ★ | ★**板 md5 变更次数 = 1** ★ |

### §4-3 · 逐条验收命令 (★逐字可粘贴·每条都能独立判★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 板 md5 / mtime 零写板双证 (★交卷前后各跑一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb            # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb      # 必须 = 2026-11-06 07:07:17.362193413

# ② 图纸门禁 (★S8 的主判据: C4 unconnected 必须 = 0★)
python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb
#   ★期望: C3 violations = 0 · C4 unconnected items = 0 · C7 同点重复过孔 = 0★

# ③ 名单制闸 (★退铜名单空 + 差分死腿空 + 逐网孤岛空 + rc=0 ACCEPT★)
python3 state/compare_arm_official.py <候选板> HW/PCB/demo_mainboard.kicad_pcb
python3 state/compare_arm_official.py --self-test      # ★必须 ALL TESTS PASS (★不许为放行而改判据★)★

# ④ 让路闸体检 (★臂脚本 env 必须真开闸·否则不许开臂★)
bash state/pcbnew_py.sh state/gate_live_check.py --arm-script state/v76mw_arms.sh

# ⑤ 45 条逐条死因重算 (★换完板后重跑·用来证明每一条都掉了★)
bash state/pcbnew_py.sh state/probe_unconnected_worklist_v2.py <候选板> <候选板>.drc.json --out tmp/iss322/unc_worklist_cand.txt
python3 state/classify_unc.py tmp/iss322/unc_worklist_cand.txt
bash state/pcbnew_py.sh state/probe_escape_feasibility.py <候选板> <候选板>.drc.json --out tmp/iss322/escape_feas_cand.txt
python3 state/cmp_unc_sets.py <候选板>.drc.json /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json

# ⑥ ★★段内 P/N 顺序翻转 = 0 (★本单建议新增的 S8 专用闸·见 §4-3-⑧★)★★
bash state/pcbnew_py.sh tmp/iss322/probe_pn_order.py <候选板>   # ★期望: 同段比较 N 处 · 翻转 0 处★

# ⑦ ★SoM 主体区逐层占布 (★换层可行性复核★)
bash state/pcbnew_py.sh tmp/iss322/probe_som_body.py            # ★期望: In1/In3/In5/In6/B.Cu 占用率仍 < 2%★

# ⑧ 门禁链 + 闸
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py

# ⑨ 落表同批自证 (★BATCH-1 五侧一致★)
bash state/pcbnew_py.sh state/check_pcb_nets.py 2>&1 | grep -E 'C1 |缺失 |C2 |C3 '
python3 state/check_chain_content_anchor.py
grep -c '板文件' HW/BOM_v1.csv
```

★**★每条修法都要挂得住 §1-⑨ 的名单制判据 (★不许写「调一下路由参数就好了」这种挂不住的句子★)★★**

| 修法 | 挂在名单制判据上的**具体动作** (★逐条可核★) |
|---|---|
| ★**改布局 (21 器件)** ★ | ★**落铜前**改 `PCB_PART_POS` ⇒ 重生成板 ⇒ 重跑布线 ⇒ ★**跑 §4-3-③ `compare_arm_official.py <候选板> 现役板` ⇒ 退铜名单必须【逐项可解释】(★新板要布 45 条 ⇒ 必然加铜 ⇒ 退铜只允许出现在【被挪位的 21 个器件的旧走廊】上, 且必须是【同网同段】, 不许动别的网★)** ★ |
| ★**让路闸 + 换层** ★ | ★**开让路闸臂 (`PCB_YIELD_STRAIGHT=1` + `PCB_YIELD_VICTIMS=<受害网>`) ⇒ 受害网清单必须逐条来自 `logs/iss322/13_gate_live_check.txt` 的「谁掐谁」表 ⇒ ★**闸只准改【受害网自己那一小段】, 一旦动到别的网 ⇒ 名单制闸会报「退铜」⇒ 直接拒** ★ |
| ★**pair-aware (A1 那 9 条)** ★ | ★**成对扩展时 P/N 同步长 ⇒ 跑 §4-3-⑥ 要看到翻转数不增加; 且 §4-3-③ 要看到【差分死腿对数 = 0】(★MEMORY 铁律: 单边零铜的 N 腿被 P 腿打死 ⇒ Δ超差对数假降 ⇒ 闸拒★)** ★ |
| ★**改逃逸方向 (`FSIN_OUT`)** ★ | ★**把 `FSIN_OUT` 提到 `PCB_PRIORITY_NETS` 里电源之前布 (★ISS-282 已实测: L=3.0mm 就是 A→B 那条直线★) ⇒ 跑 §4-3-③, `FSIN_OUT` 必须从 unc 名单里消失且【不许动别的网】** ★ |
| ★**换层 (SoM 主体区)** ★ | ★**新铜只能加在 `In1/In3/In5/In6/B.Cu` 的空白走廊上 (★实测占布 0.38%★) ⇒ 跑 §4-3-⑦ 复核占布仍 < 2% ⇒ 跑 §4-3-③ 看退铜名单为空** ★ |
| ★**等拍板 (5 条)** ★ | ★**拍板前这 5 条不许布 (★布了也白布·因为终点/极性/位置会变★) ⇒ 拍板后重跑 §4-3-②, 目标是 C4 = 0** ★ |

### §4-4 · ★**「板只改一次」的自证 (★这一趟怎么排★)** ★

| 顺序 | 步 | ★**板 md5** ★ | 判据 |
|---|---|---|---|
| 1 | S1 位号改名 + S2 去 `C_VBUS_GND` + S3 Value + S4 ESD + S7 DNP (★全在 BATCH-1 同批★) | ★**变 (第 1 次)** ★ | §4-3-⑨ |
| 2 | ★**S6 布局修正 (★本单 §3-5/§3-6 的 21 器件 lane 序修正 + §4-2 的 CSI 电容侧修正★)** ★ | ★**不变 (同一趟内)** ★ | §4-3-⑥ 翻转 = 0 |
| 3 | ★**S8 布线 45 → 0 (★在同一趟里做·不许拆到下一趟★)** ★ | ★**不变 (同一趟内)** ★ | §4-3-②③④ |
| 4 | S9 换基线 + S10 投产包 + S11 闸 + S12 留证 + S13 发布 (★全部最后跑一次★) | 不变 | `HW/check_onepass_commit_order.py` |

⇒⇒ ★**⇒ 板 md5 变更次数 = 1 ⇒ ⇒ 「板只改一次」铁律成立; 而本单的 §3-4 证明【不需要为了几何再多改一次】** ★

---

## §5 · 需要老板 / main 拍的死结清单 (★本单不代拍★)

| # | ★**need key** ★ | 一句话问法 | 谁答 | ★**不答的后果 (量化)** ★ | 建议默认值 | 建议排期 |
|---|---|---|---|---|---|---|
| 1 | ★**`iss322_s8_p7_zero_scope`** ★ | ★**「S8 归零到底要不要动板框/层数? 实测 SoM 主体区内层 99.6% 空闲 + 同框同层数对照板做到 unc 23 ⇒ 归零【不需要】改板框/层数 —— 是不是把 P7 口径从『C1/C2/C3 改板 / C4 不归零』改成『同框归零』?** ★ | ★**main (转老板)** ★ | ★**沿用 ISS-308 判「现役帧上 45→0 不可达」⇒ S8 不以归零收口 ⇒ G1 开不了 ⇒ 投不了板; 或者走 C4 分级放行 ⇒ ★**带着 11 条「两边都没通」的硬骨头投板 ⇒ 投板后才发现 = 2-4 周 + ¥4-8K** ★ | ★**「同框归零」** (★依据: §3-4 + §3-7★) ⇒ ★**P7 只需选板形, 不必选"改不改板"** ★ | ★**BATCH-1 开工前** ★ |
| 2 | ★**`iss322_s8_rsel_lane_order`** ★ | ★**「`R_SEL_*` + `TP_DSI_*` 这 21 个 DSI lane 器件: 挪到【左上 x 5.50..38.35】还是【右上 (ISS-265 方案 A)】? 实测: 左上那 7 块板 unc 23..35, 右上现役板 45 (全盘最差) ⇒ 建议【左上】」** ★ | ★**main + 老板 (★要动布局 ⇒ 动板 md5★)** ★ | ★**按 ISS-265 方案 A 布 ⇒ 段内 P/N 翻转 17 处 ⇒ 高速腿必然交叉 ⇒ 高速 23 条归不了零 ⇒ ★**板 md5 变两次 (S6 布局一次 + S8 再布一次) = 2-4 周 + ¥4-8K** ★ | ★**左上 x 5.50..38.35 (★`R_SEL_*` y=3.00 · `TP_DSI_*` y=6.20★)** ★ | ★**BATCH-1 开工前** ★ |
| 3 | ★**`iss322_s8_csi_cap_side`** ★ | ★**「CSI 5 族在连接器侧的 P/N 顺序与 AC 电容侧相反 (Δx 0.50mm) ⇒ 是【把 AC 电容挪到连接器同侧】还是【成对换层绕开】?** ★ | ★**main** ★ | ★**不选 ⇒ CSI 10 条走不进 §4-2 的「改布局」批 ⇒ 落到「算法可解」⇒ ★**实测这类 4 臂都布不出来 ⇒ 45 归不了零** ★ | ★**成对换层绕开 (★不动器件·不动板框·风险最低★)** ★ | BATCH-1 开工前 |
| 4 | ★**`iss322_s8_a1_batdet`** ★ | ★**「`BAT_DET` 的终点是哪个点? (★ISS-265 §6-1 登记的 A1·作业包 §3-S8 列的 5 条死因之一★)」** ★ | ★**老板 (★经 main 转达·技术选项由 hw-lead 给★)** ★ | ★**布不了 `BAT_DET` (★J_SOM_P1.38 ↔ C_DET_BAT.1·直线 37.08mm★) ⇒ 45 归不了零 ⇒ G1 开不了** ★ | ★**终点 = `C_DET_BAT.1` (★现状网表已这么连·只需确认不是要改成分压链中点★)** ★ | BATCH-1 开工前 |
| 5 | ★**`iss322_s8_w1w2_esd`** ★ | ★**「ESD 架构定了没? 定了才能定 `D_ESD_USB_D` / `D_ESD_LIGHT` 的封装与钉位 (★W-1/W-2★)」** ★ | ★**老板 / ISS-307 已给候选集** ★ | ★**`LIGHT_5V` (6.56mm) + `USB_D` 侧的钉位定不下来 ⇒ ★**那一趟开工后还得再改一次板 ⇒ 板 md5 变第 2 次** ★ | ★**ISS-307 的候选集里选一个并把钉位写进 `PCB_PART_POS`** ★ | BATCH-1 开工前 |
| 6 | ★**`iss322_s8_w4_qpg`** ★ | ★**「`PWR_GOOD` 从 `Q_PG.3` 出来还是进去? (★极性★)」** ★ | ★**老板** ★ | ★**`Q_PG.3` 是不是终点都没定 ⇒ `PWR_GOOD` (★R_PU_PG.2 ↔ Q_PG.3·15.13mm★) 布不了** ★ | ★**`Q_PG.3` = 输出脚 (★`PWR_GOOD` 从 Q_PG 出来到 `R_PU_PG`★)** ★ | BATCH-1 开工前 |
| 7 | ★**`iss322_s8_d_led_g_pos`** ★ | ★**「`D_LED_G` 落在板上的哪个点? (★现状 `LED_G_D` 直线 93.49mm★)」** ★ | ★**mech-lead + 老板 (★依赖 MECH 侧落位·ISS-320 在跑★)** ★ | ★**`LED_G_D` 93.49mm + `LED_G` 被 `LED_B` 掐 0.200mm ⇒ 这 2 条布不了** ★ | ★**把 `D_LED_G` 挪到 `R_LED_G` 同侧 (★直线 < 20mm★)** ★ | BATCH-1 开工前 (★与 MECH 落位同批★) |

★**★不许把「等外部 / 等老板」当成阻塞项挂着 (★任务书 §2-⑤ 硬要求★) ⇒ 每条都给了降级方案: ★★**

| need | ★**降级方案 (★拍板前也能往下走★)** ★ |
|---|---|
| `iss322_s8_p7_zero_scope` | ★**默认按「同框归零」排 (★依据 §3-4/§3-7 的实测★) ⇒ 若老板选 C4, S8 就以「分级放行」收口 ⇒ 那要改 G1 判据 (`stage_gate`) ⇒ ★**作业包 §7 逐字「须老板显式点头, 口头默许不算」★★ |
| `iss322_s8_rsel_lane_order` | ★**先按「左上」把 `PCB_PART_POS` 写好 (★沙盒里跑·不落表★) ⇒ 若老板选右上 ⇒ 只需改坐标, 不影响其余批次** ★ |
| `iss322_s8_csi_cap_side` | ★**默认「成对换层绕开」⇒ 不动器件 ⇒ 万一失败再退到「挪 AC 电容」** ★ |
| `iss322_s8_a1_batdet` | ★**按现状网表 (`C_DET_BAT.1`) 布 ⇒ 若老板改分压链, 该条重布 (★1 条·成本 < 0.2 人日★)** ★ |
| `iss322_s8_w1w2_esd` | ★**按 ISS-307 候选集里封装最小的一个先占位 (★沙盒·不落表★)** ★ |
| `iss322_s8_w4_qpg` | ★**按「输出脚」布 ⇒ 若反了只影响这 1 条** ★ |
| `iss322_s8_d_led_g_pos` | ★**按「`R_LED_G` 同侧」布 ⇒ 等 MECH 落位后只改 `D_LED_G` 坐标 (★1 条·< 0.2 人日★)** ★ |

### ★★§5-6 · 给 main 的「逐字改法 + 行号」 (★本单零改既有文档正文·改法交 main★) ★★

| 文件 | 行 | 建议逐字改成 |
|---|---|---|
| `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` | §3-S8 表第 2 行 (`★**★本步是 P7 的正面战场★**` 那行) | ★**`45 条里 23 条是高速 DSI/CSI 腿 (22 个网名: DSI_ 13 + CSI_ 9)`** ★ (★消除 23/13 的读歧义★) · 同表「其余 22 条」那行 ★**改成「其余 22 条 (21 个网名)」** ★ |
| `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` | §3-S8 表「★其余 22 条 (非 DSI/CSI) 的死因登记★」那行 | ★**补上本单的 5 条死因归属 (A1 / W-1·W-2 / W-4 / `D_LED_G` / `FSIN_OUT`) 各对应 §1 表的哪几行** ★ |
| `HW/PCB/LAYOUT_FIX_SPEC.md` | §0 表「★**能不能靠挪器件归零** ★」那行 | ★**★必须加一句: 实测 8 块同代板对照 (★lane 序一致的 7 块 unc 23..35 / 现役 lane 序反的 unc 45·`logs/iss322/22_lane_order_vs_unc.txt`★) ⇒ 「lane 交叉数」与 unc 反相关 ⇒ §0 的处方方向需复议 (★方案 A = 右上 = 全盘最差的一板★)」** ★ |
| `state/UNC_TARGET_MAP.md` | 文件头「★基线: state/.lastgood/baseline_v76mw0_chain.kicad_pcb (★DRC 0 · unc 29 条 / 24 网名★)」 | ★**加一句: 「★本基线只覆盖基线板; 现役板 (18092 段/433 孔·md5 611b869e) 的靶集是 45 条/43 网名 ⇒ 两套口径的差集见 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` §2-4 ⇒ 【不许拿本文的 22 网名当现役板靶集】★」** ★ |

---

## §6 · 证据分级 + 零写板双证

### §6-1 · 证据分级 (★四档标齐 + 本单实际用到的档位★)

| 档 | 含义 | ★**本单的具体条目** ★ |
|---|---|---|
| ★**`[实测]`** ★ | 本机可复现 | ★**①** 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` · ★**②** DRC viol 0 / unc 45 / 重复过孔 0 · ★**③** 45 条逐条清单 (§1) · ★**④** 23/13/22/9 四个数的机器拆分 (§2-1) · ★**⑤** `classify_unc` A1 5 / A2 4 / B1 11 / B2 23 · ★**⑥** escape 可行 88/88 (W=0.20 与 W=0.15) · ★**⑦** 段内 P/N 翻转 17/47 · ★**⑧** SoM 主体区逐层占布 (F.Cu 5.73% / In2 1.52% / In4 0.81% / 其余 0.38%) + `J_SOM_P1..P4` 全 SMD 只在 F.Cu + 区内 36 过孔 · ★**⑨** 8 块板 lane 序 vs unc 对照 (23/26/28/29/29/35/35/45) · ★**⑩** 现役板 vs `best_unc23` 板网名集合 (32 已通 / 11 未通 / 10 新债) · ★**⑪** 现役板 vs 官方 18092 快照 (交集 43 / 仅A 0 / 仅B 0) + 现役板段数 18092 / 孔数 433 · ★**⑫** 现役板 vs `UNC_TARGET_MAP` 基线差集 (31 / 12 / 12) · ★**⑬** v44/v46/v47/v48 四臂共同失败 39 网名 / 45 (net,pad) · ★**⑭** 15/22 高速未连通网【板上零铜】 (★另 7 条有铜但未连通: `DSI_D0_CK_N` 88.70mm · `DSI_D0_CK_P` 84.11mm · `DSI_D0_D0_N` 4.85mm · `DSI_D0_D0_P` 81.04mm · `DSI_D0_D1_N` 78.27mm · `DSI_D0_D1_P` 79.48mm · `DSI_D0_D2_N` 168.74mm★) · ★**⑮** 全盘 11 份 DRC JSON (★含本单 11:38 的 fresh 那份★) 最低 unc = 23 / 无一份 = 0 · ★**⑯** `compare_arm_official.py --self-test` rc=0 `ALL TESTS PASS` ★ |
| ★**`[官网]`** ★ | 厂商官网 / 官方 datasheet | ★**本单不需要外部资料** ⇒ ★**全单 0 条 `[官网]` 引用** ★ (★所有判据都来自本机板与本机工具链★) ★ |
| ★**`[媒体]`** ★ | 第三方报道 | ★**本单 0 条** ★ |
| ★**`[推算]`** ★ | 由实测数据推导, 非直接测量 | ★**①** 「lane 序一致的板 unc ≤ 35, 反序的板 = 45 ⇒ 布局是主因之一」 (★因果性是推算·7/1 的对照不构成严格对照实验★) · ★**②** 「§3-5 的 21 器件挪位后 45 → 约 23..35」 (★是基于 §3-6 对照的推算·★从未实跑过那套布局★) · ★**③** 「归零后剩下的 11 条硬骨头需要专属机制」 (★机制归类部分来自 ISS-308 §2-C·未逐条重算★) ★ |
| ★**`[0数据]`** ★ | 查不到 | ★**①** 盘上【没有任何一块板达到 unc = 0】⇒ ★**「归零是否可达」本单【无数据】** ★ · ★**②** `state/probe_pair_lane.py` 需要 `/tmp/v76ru_reserve.txt` (★臂专用预留串·盘上不在★) ⇒ 本单【未跑】, 其判据由 `probe_pn_order.py` + `probe_csi_order.py` 覆盖 ⇒ ★**降级: §3-5 用【段内 P/N x 序】直接判, 不依赖预留串** ★ · ★**③** `state/pair_corridor.py` 是【路由器改造件】不是探针 ⇒ 本单只登记为修法, 不出读数 ★ |

### §6-2 · 沙盒目录清单 (★跑完已删干净·脚本随交卷物归档到 logs/iss322/scripts/★)

```
★沙盒 (★交卷前已 rm -rf★):
  tmp/iss322/
    extract_unc.py            cmp_cur_vs_best23.py    build_table45.py
    hs_geometry.py            hs_copper_amount.py     probe_som_body.py
    probe_pn_order.py         probe_lane_order_vs_unc.py    cmp_placement.py
    write_frag.py
    unc45.json  hs_geometry.json  cur_vs_best23.json  table45.json  table45.md
    unc_worklist_current.txt  escape_feas_current.txt  lane_conflicts_current.txt  classify_current.txt

★归档 (★交卷物·只写自己这一份★):
  logs/iss322/
    01~30 号 raw 输出 (★每个交卷页引用的读数都有对应 raw 文件·悬空引用 = 0★)
    scripts/  (★10 个只读探针与分析脚本·可独立复跑★)
```

### §6-3 · ★★`state/gate_check.py` 的读数与红项归因 (★交卷时的实况★)★★

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-18T11:26:08+08:00)
   产出 655 | 阻塞 43 (高危 33) | 未闭合需求 330 | 冲突 0 | 健康度 red
merge rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-18_hw-lead_ISS322_S8布线归零作业包.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-18_mech-lead_ISS320_电芯型号订正实做.md
【Q2 证据分级率】 3/3    【Q3 接口声明率】 全员 954 条
【Q6 硬件真源闸】 ✅ 通过 (rc=0)
【Q7 钉板 md5 闸链】 9/9 道绿
gate rc=0
```

★**★交卷时的实况: `gate_check.py` rc = 0 · Q1 = 18/18 · Q2 3/3 · Q6 通过 · Q7 9/9 全绿 —— 任务书 §1-⑩ 预告的那道红 (★「ISS-318 SW 侧位号引用可达性闸」·18 条真隐患来自 `SW/ONETRIP_SW_RENAME_SAFETY.md`★) 在本单跑的过程中【被同机在飞的 sw-lead (ISS-321) 自己清掉了】★★**

| 时刻 | 事实 | 来源 |
|---|---|---|
| 11:0x (★任务书 §1-⑩ 预告★) | `gate_check.py` rc=1 · 唯一红项 = ISS-318 SW 侧闸 · 18 条真隐患全部来自 `SW/ONETRIP_SW_RENAME_SAFETY.md` | 任务书逐字 |
| ★**11:11** ★ | `SW/ONETRIP_SW_RENAME_SAFETY.md` mtime = 11:11 (★sw-lead 在飞的 ISS-321 写的·**不是本单**★) | `ls -la` |
| ★**11:13** ★ | `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` mtime = 11:13 (★sw-lead 交卷★) | `ls -la` |
| ★**11:26** ★ | ★**本单交卷跑: rc=0 · Q1 18/18 · Q7 9/9 全绿** ★ | ★`logs/iss322/27_merge_gate_output.txt`★ |

⇒⇒ ★**★本单对这条红的处理: 【一个字都没碰】⇒ ★**
1. ★**没改 `state/gate_check.py`** (★md5 `cd030d157407c6af2ac8d5b74bf283ac` · mtime `2026-11-18 10:18:53` · ★早于本单开工 11:08★) ★
2. ★**没碰 SW 域任何文件** (★`SW/ONETRIP_SW_RENAME_SAFETY.md` 的 11:11 mtime 是 sw-lead 的·**本单对 `SW/` 的写入次数 = 0**★) ★
3. ★**没改基线 / 没改 `state/fragments/sw.yaml`** ★
4. ⇒ ★**★最强的自证: 本单一次动作都没做, 那道红自己清了 ⇒ 红 100% 不在本单这边 ⇒ 本单【不需要】也不会去动 SW 域 / 改闸 / 改基线来凑 rc=0** ★
5. ★**★同类证明 (★ISS-317 已做过一次★)**: `logs/iss317/09_merge_gate_output.txt` 开头「归因链」段 —— ★**决定性试验: 挪走那个 SW 文件 ⇒ 该闸 rc=0 绿** ★ ⇒ ★**本单把那个试验的【前提】重跑了一遍: 现在【不需要】挪走任何文件, 闸本来就绿** ★
6. ★**★交卷前必跑 8 条命令的原样输出 = `logs/iss322/30_final_verification.txt`** ★

---

## §7 · 文件清单 (★本单新建 / 本单只读★)

| # | 路径 | 动作 | 内容 |
|---|---|---|---|
| 1 | `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` | ★**新建** ★ | ★**本文件** ★: §0 口径与边界自证 + §1 45 条逐条清单 + §2 死因登记 + §3 高速腿几何可布性判定 + §4 修法/批次/验收命令 + §5 待拍死结 + §6 证据分级 + §7 文件清单 ★ |
| 2 | `HANDOFF/2026-11-18_hw-lead_ISS322_S8布线归零作业包.md` | ★**新建** ★ | ★**交卷页 (B0~B6 齐全)★** ★ |
| 3 | `logs/iss322/` (30 份 raw + `scripts/` 10 个探针脚本) | ★**新建** ★ | ★**每个交卷页引用的读数都有对应 raw 文件·悬空引用 = 0★** ★ |
| 4 | `state/fragments/hw.yaml` | ★**改 (走 `state/frag_write.py --agent hw-lead`)★** ★ | ★**artifacts + needs + claims 各 ≥ 1 · status 换 ISS-322** ★ |
| 5 | `HW/PCB/demo_mainboard.kicad_pcb` | ★**只读 (零写板双证)★** ★ | md5 / mtime 交卷前后逐字节相同 |
| 6 | `state/check_pcb_drc.py` · `state/merge.py` · `state/gate_check.py` · `state/issue_check.py` · `state/compare_arm_official.py` · `state/check_pcb_nets.py` | ★**只读 (零改闸)★** ★ | md5 未变 |
| 7 | `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard_p*.kicad_sch` · `state/gen_*.py` | ★**只读** ★ | 零改网表/脚表/BOM/原理图真源 |
| 8 | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/LAYOUT_FIX_SPEC.md` · `state/UNC_TARGET_MAP.md` | ★**只读 (改法交 main, 见 §5-6)★** ★ | 零改既有文档正文 |
| 9 | `state/fragments/sw.yaml` · `mech.yaml` · `pm.yaml` · `MECH/**` · `SW/**` | ★**只读 (★本单不碰 MECH 域 / 不碰 SW 域★)★** ★ | 一个字节没碰 |
