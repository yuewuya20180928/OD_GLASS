# ISS-276 · MECH 侧 · 坐标系归一 (帧: 60×30 套A ⇒ 帧: 160×100 台架板) + ISS-273 三条 need 收口

> **派活人**: 项目总工 (main / moli) · **派活时刻**: 2026-11-17 06:1x · **job**: cron `fb67af40` (ARS45 队列自动派活)
> **owner**: mech-lead (结构总工 · 带散热) · **单性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页订正类 · 零写板 · 零落表 · 零改既有 MECH 判据脚本 · 零改 HW** ★
> **不是老板级拍板** ★ — 台账格式契约的最终落点 / 台账自身要不要加锚 = ★**只给建议与代价, 归 main 拍** ★
> **实测口径**: ★**本机无板 ⇒ 实物 `[实测]` = 0 条; 本单全部「实测」= 文件实读 + 脚本实跑** ★

---

## ★0 一句话

★**ISS-271 交的两个窗口 (检修口开口 X 47.00..60.00 / `D_LED_G` 首选窗口 X 33.00..47.71) 是【帧: 60×30 套A 坐标】, 照字面抄进现役 160×100 台架板的 §3-S6 = 开口压住 `J_SOM_P1` 56 个焊盘、LED 窗口压住 `J_SOM_P3` 10 个焊盘 ⇒ 本单把这两个窗口【归一到现役板坐标系】(两个开口 + 两个 LED 落位带, 压 SoM 焊盘全 = 0), 并把 ISS-273 留下的三条 need 一次收掉** ★

---

## B1 结论摘要

★**B1-1 · 坐标系声明 (置顶)** ★
- ★**帧 id = `B160x100`** ★ — ★**帧 id 的唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 的 JSON 块 `cal:FRAMES` (★ISS-274 · hw-lead 出 · 2026-11-17 06:5x 本机实读★) ⇒ 本页/本闸的帧 id 与那个权威表【逐字对齐】, 两边不得各用一套** ★
- ★**帧 id 三件套**: `B160x100` = 160×100 台架板帧 (现役板) · `F30A` = 60×30 套A 帧 · `P60x15` = 60×15 帧 ★
- ★**帧: 160×100 台架板 = `HW/PCB/demo_mainboard.kicad_pcb` 的 `Edge.Cuts` 中心线包围盒 X 0.00..160.00 × Y 0.00..100.00 ⇒ 160.00 × 100.00 mm** ★ `[实测]`
- ★**笔画外缘 = 160.10 × 100.10 (线宽 0.10 ⇒ 半宽 0.05/边); 落件坐标一律按中心线记** ★
- ★**与 `MECH/BOARD_GEOM_30MM.md` 的 帧: `F30A` (60×30 套A) 坐标【不是同一套】⇒ 两套数不可互相代入** ★

★**B1-1b · ★与 hw-lead 的 ISS-274 互核 (★2026-11-17 06:5x 本机实读, 结论: 两边是同一套的两个视角, 不是各写一套★)** ★
| 核项 | `HW/PCB/BOARD_FRAME_CALIBER.md` (hw-lead) | 本单 (mech-lead) | 一致? |
|---|---|---|---|
| 帧 id | `B160x100` / `F30A` / `P60x15` | ★**已按它改名对齐** ★ | ✅ |
| 板框口径 | 160.00 × 100.00 名义 / 包围盒 160.10 × 100.10 / 8 层 / 1.60mm / 186 封装 | 同 | ✅ |
| ISS-271 检修口开口 X 47.00..60.00 × Y 1.665..11.730 | 归 `F30A` 帧 · 压 `J_SOM_P1` **56** 焊盘 · 不可当现役帧用 | 同 | ✅ |
| ISS-271 `D_LED_G` 窗口 X 33.00..47.71 × Y 1.60..28.40 | 归 `F30A` 帧 · 压 `J_SOM_P3` **10** 焊盘 · 不可当现役帧用 | 同 | ✅ |
| 「ISS-267/271 判红 ≠ 现役板不能用」 | 明写 | 明写 | ✅ |

★**⇒ hw-lead 的闸 `HW/check_board_frame_caliber.py` 实跑 rc=0, 其 C5 复现的压焊盘数 (10 / 56) 与本单 C3 逐字相同 ⇒ 两个闸互为交叉验证** ★
★**⇒ 本单 §5 的 S6 认领句已按 hw-lead §2.1 的写法补上「ISS-271 警语」一条 (帧: `F30A` + 不可当 S6 坐标用) ⇒ hw-lead 抄进 §3-S6 时, 他的闸 (e) 不会红** ★

★**B1-2 · SoM 承载区实测 (三个口径都登记, 免得又被当成一个数)** ★ `[实测]`
| 口径 | X | Y | 合计 |
|---|---|---|---|
| 焊盘铜箔并集 | 15.100..68.900 | 7.610..54.390 | 53.80 × 46.78 mm |
| 座体 `F.Fab` 外框并集 | 13.700..70.300 | 7.900..54.100 | 56.60 × 46.20 mm |
| ★**保守包络 (座体 ± 0.05 笔画半宽)** ★ | ★**13.650..70.350** ★ | ★**7.610..54.390** ★ | ★**56.70 × 46.78 mm** ★ |

- ★**⇒ Y 向 46.78 mm > 30.00 (60×30 板宽) 且 > 15.00 (60×15 板宽) ⇒ 现役 SoM 承载区【物理上装不进】60×30 / 60×15** ★
- ★**⇒ 现役板与 60×30 / 60×15 是两种物理产品 (SoM 承载区 vs SoC 直上板) ⇒ 坐标、孔位、夹具基准一个都不通用** ★

★**B1-3 · 两个旧矩形喂进现役板 (★量化, 与任务书给的数一致★)** ★ `[实测]`
| 帧: **60×30 套A** 的旧矩形 | 喂进帧: **160×100 台架板** 后压住 | 明细 |
|---|---|---|
| 检修口/调试口开口 X 47.000..60.000 × Y 1.665..11.730 | ★**56 个** ★ | 全在 `J_SOM_P1` ⇒ 28 列 × 2 行 |
| `D_LED_G` 首选窗口 X 33.000..47.710 × Y 1.600..28.400 | ★**10 个** ★ | 全在 `J_SOM_P3` ⇒ 5 列 (X 33.200..34.800) × 2 行 |

★**B1-4 · ★合并开口 (MECH 现行模型) 在帧: 160×100 台架板 上【几何不成立】—— 不是「紧」, 是差 116.017 mm** ★ `[推算]`
- 两连接器座体必须清空区并集宽 = **126.218 mm** (`J_UART` 座体 X 17.620..20.160 ↔ `J_DEBUG` 座体 X 142.063..143.838)
- 开口定档 10.20 mm ⇒ 单边间隙 = (10.20 − 126.218)/2 = **−58.009 mm** ⇒ **判红**
- ⇒ **现役板上必须把开口拆成两个独立窗口** (调试口罩 `J_DEBUG` / UART 罩 `J_UART`), 或者明确声明「台架板不做结构检修口, 只做探针可达区」

★**B1-5 · ★归一后的两个开口 (帧: 160×100 台架板) —— 压 SoM 焊盘全 = 0** ★ `[实测]`+`[推算]`
| 窗口 | 必须清空区 | 开口 (居中解) | 左下角可放行区间 | 单边间隙 (最坏) | 压 SoM 焊盘 |
|---|---|---|---|---|---|
| 调试口 (罩 `J_DEBUG`) | X 142.063..143.838 × Y 55.330..57.870 | ★**X 137.850..148.050 × Y 54.300..58.900** ★ | X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330] | X 4.213 / Y 1.030 (3.913 / 0.730) | ★**0** ★ |
| UART 检修口 (罩 `J_UART`) | X 17.620..20.160 × Y 67.330..69.870 | ★**X 13.790..23.990 × Y 66.300..70.900** ★ | X0 ∈ [13.790, 17.620] · Y0 ∈ [66.300, 67.330] | X 3.830 / Y 1.030 (3.530 / 0.730) | ★**0** ★ |

★**B1-6 · `J_DEBUG` ↔ `J_UART` 的间距 (ISS-267 F-7 的量化)** ★ `[实测]`
- ★**ΔX = 123.56 mm** ★ — ★**★ISS-267 F-7 与任务书里写的「123.6mm」是 ΔX, 不是直线距离; 直线 = 124.141 mm (ΔY = −12.00)★** ★
- ⇒ **⇒ 「必须清空区 7.62 × 2.54」在帧: 160×100 台架板 上不成立 (前提是两者相邻) ⇒ 不得抄进 §3-S6** ★

★**B1-7 · `LED_G_D` 走线根因 (★实算, 与 ISS-271 的 93.49 对得上★)** ★ `[实测]`
- ★**`R_LED_G`.2 (7.50, 62.60) ↔ `D_LED_G`.1 (100.80, 56.60) ⇒ Δx 93.30 / Δy −6.00 ⇒ 直线 93.492727 mm (文档 93.49 ⇒ 差 +0.002727)** ★
- ★**根因 = 排版器按「功能排」落位, 不按「网络邻近」落位**: `R_LED_G` 进了 X = 5.90 的左侧 I2C 上拉列 (同列 `C_AC_CSI_D0_D3_P` / `R_PU_I2CB_SCL` / `TP_LED_G`), `D_LED_G` 进了 Y = 56.80 的 LED 行 (同排 `D_LED_B` / `D_ESD_LIGHT` / `D_LED_R` / `BT_432243` / `SW_RST` / `J_BOOT1` / `J_CHG`) ⇒ 两件分居板两端 ⇒ 93.49 mm 横跨全板 ★

★**B1-8 · ★`D_LED_G` 可放行空间 (帧: 160×100 台架板) —— 只给空间, 不定坐标** ★ `[实测]`+`[推算]`
- 判据: 零重叠 + 器件距板边 0.80 + 不压 SoM 座 + 不压两个开口窗口; 器件占位 = 落地封装铜箔 2.900 × 0.900 (相对封装原点 X −0.75..+2.15 / Y −0.65..+0.25)
- ★**整高自由带 (封装原点 X) = 1.550..3.450** ★ + 72.540..73.660 ⇒ 两条带都**不压** SoM 焊盘 (0 个)
- ★**最近落位带 (封装原点可放行窗口) = X 6.940..8.250 · Y 63.700..67.900** ★ (即 `R_LED_G` 右手边那一块)
- ★**净距敏感度 (给 hw-lead 的取舍表)**: 器件间铜箔净距 0.00 / 0.10 / 0.20 / 0.50 mm ⇒ 最近落位原点 (8.250, 63.700) / (8.150, 63.800) / (8.050, 63.900) / (8.420, 64.200) ⇒ **`LED_G_D` 直线长 = 0.450 / 0.559 / 0.680 / 0.965 mm ⇒ 相对现状 93.492727 省 92.5..93.0 mm** ★
- ⇒ ★**「把 `D_LED_G` 搬到 `R_LED_G` 旁边」这一件事就把跨板 93.49 mm 变成 <1 mm; 但这是【排版规则】问题 (要不要按网络邻近分组), 不是【单个器件坐标】问题 ⇒ 归 hw-lead 拍** ★

★**B1-9 · 机器闸 (`MECH/check_board_frame_coords.py`, 新建) rc=0 四项全过** ★
- ★**C1 帧标签**: 机器块每个窗口必须带 `frame:` 且 frame 必须已声明; 正文里每个坐标行 (≥2 个带小数点的数) 必须能追到帧来源 (本行 / 本表的表头 / 上面最近的标题或引用块) ⇒ **漏标一条即红** ★
- ★**C2 归一后窗口不压 SoM 座**: 读板 ⇒ §3/§4 的四个窗口 ⇒ **压住 `J_SOM_P1..P4` 焊盘数必须 = 0** (实测全 0) ★
- ★**C3 两套坐标不可代入 (负向断言)**: 旧的两个 60×30 矩形喂进现役板坐标 ⇒ **必须报出「压住了 56 / 10 个 SoM 焊盘」而不是静默通过** ★
- ★**C4 受保护 5 件 md5 前后逐字节不变** (板 / `.kicad_pro` / 网表 / 脚表 / BOM) ★
- ★**`--selftest` 七条反向用例全抓到** (①改窗口一角 ②抽帧标签 ③窗口挪进 SoM 区 ④a旧矩形当新坐标喂 ④b旧矩形挪开 ⇒ C3 报 N=0 ⑤改受保护件 ⑥真件跑完自检仍逐字节不变) ★

★**B1-10 · ISS-273 三条 need 收口** ★
| key | 收口方式 | 结果 |
|---|---|---|
| ★**`iss273_h1_anchor_single_source`** (main 开的, to=mech-lead) | ★**用 main 开的原 key 补一条 answer (写在 mech.yaml, to=main)** ★ | ★**`state/fragments/pm.yaml` 那条 pending need ⇒ `state=answered` / answers=1 / foreign=0 ★** |
| `iss273_mech_ledger_format_contract` (mech 开, to=main) | answer 原文写在 mech.yaml (to=main) | ★**merge 规则: 只有【被问的那个 agent】的 answer 才闭合 ⇒ 该 need 仍 `pending`, 我的 answer 落在 `foreign_answers` 位 ⇒ 需 main 代录进 pm.yaml 或给 need 加 `decision` 字段** ★ |
| `iss273_mech_ledger_itself_anchor` (mech 开, to=main) | 同上 | 同上 |

★**B1-11 · 两条台账口径的建议 (★只给建议与代价, 不代 main 拍★)** ★
- **格式契约落点**: ★**建议写进【HW 侧落表作业包模板】** ★ (台账住在 HW/ 且由 hw-lead 写 ⇒ 契约跟着生产者走; MECH 侧只读, 解析器已按现值写好)
- **台账自身要不要加 md5 锚**: ★**建议【不加在台账本体上】** ★ —— 理由: ★**锚与台账在同一个可写集合里, 改台账的人顺手就能改锚 ⇒ 加锚堵不住「悄悄换真源」** ★; ★**代价: ①每落一次表就得重锚一次 ⇒ 绕回 H-1 担心的「一落表就红」老循环 ②锚的存放点成为新的单点 ⇒ 与现在台账的单点问题同构 ③锚一变 ⇒ 门禁脚本要跟着重基线 (ISS-273 已经改过一次 4ae5827e…→6972b867…)** ★ ⇒ ★**改用【每条落表记录必须链式相接 (本条改前 md5 = 上一条改后 md5)】+ 保留现有「断链/链头不唯一/取不准一律判红」来堵 ⇒ 洞由【链的完整性】堵, 不是由【再加一层可写锚】堵** ★; ★**若 main 仍决定加锚, MECH 侧能接的唯一形态 = 锚写在【只读侧】(MECH 自己的只读副本 / issue_log 受保护段), 不写在台账旁边** ★

★**B1-12 · 边界自证 (★逐条★)** ★
| 边界 | 自证 |
|---|---|
| ★**零写板 / 零落表** ★ | 板 / `.kicad_pro` / 网表 / 脚表 / BOM 五件 md5 跑前跑后逐字节相同 (`611b869e…` / `3e504d2b…` / `e06c1dd6…` / `287e7861…` / `94642d07…`) ⇒ 机器闸 C4 也逐字节核过 |
| ★**零改既有 MECH 判据脚本** ★ | `check_demo_struct_truth.py` **6972b867c8243bc971408f972dc7727e** · `service_port_check.py` db58ff6a… · `board_port_opening_s6_check.py` be8bf0ce… · `jd_y0_feasibility.py` 55db5346… ⇒ **一字未动**; 新闸是【新建】文件 |
| ★**零改 `MECH/BOARD_GEOM_30MM.md`** ★ | md5 `5757774f817595649240fbe0d45b1b77` ⇒ 一字未动 (归一页只【引用】它) |
| ★**零改 HW** ★ | `HW/` 零字节写入; `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (hw-lead 的文件) 一个字没动 |
| ★**零外发** ★ | 不发邮件 / 不询价 / 不问询 / 不采购 ⇒ 缺口一律 `[0数据]` + 降级方案 |
| ★**证据分级** ★ | 每条结论标 `[实测]` / `[推算]` / `[0数据]`; ★**实物 `[实测]` = 0 条** ★ |
| ★**不替老板拍板** ★ | 台账格式契约落点 / 台账加锚 / 开口最终坐标 / `D_LED_G` 最终坐标 = **只给建议与代价** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | 只走 `state/frag_write.py --agent mech-lead` |
| ★**不写别人的分片** ★ | 只写 `state/fragments/mech.yaml`; ★**配对闭合靠【answer 的 key 与 main 开的 key 一致】, 不是靠改 main 的分片** ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收项 | 判定 | 实据 |
|---|---|---|---|
| 1 | 新建 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (坐标系归一页) | ✅ **通过** | §1 坐标系声明置顶 · §2 SoM 承载区 · §3 开口 · §4 LED · §5 S6 认领句 · §6 边界 |
| 2 | 归一页里声明「两套坐标不可互相代入」 | ✅ **通过** | §1.1 结论 1 + §6.1; C3 机器化证明 |
| 3 | 归一页登记现役 SoM 承载区实测占位 | ✅ **通过** | §2 三口径表 + 四个位号表 |
| 4 | 开口的可放行空间 = **实算, 不抄 60×30 的数** | ✅ **通过** | §3.4/§3.5 全部由 `check_board_frame_coords.py --compute` 从板文件算出; 旧矩形只作 C3 负向登记 |
| 5 | 开口与 SoM 座的避让关系 | ✅ **通过** | §3.4/§3.5「压住 SoM 焊盘 = 0」; C2 机检 |
| 6 | 写明 `J_DEBUG`@144.30,58.00 / `J_UART`@20.74,70.00 相距 123.6 mm 对开口位置的影响 | ✅ **通过** (★**并订正了口径: 123.6 = ΔX, 直线 = 124.141★**) | §3.2 + §3.6 |
| 7 | `D_LED_G` 的可放行空间 + 走线两端坐标 + 根因 | ✅ **通过** | §4.1 / §4.2 (含净距敏感度表) |
| 8 | §4 只给空间与约束条件, **不定坐标** | ✅ **通过** | §4.2/§4.3 只给带与条件; 明写「最终坐标 = hw-lead 的活」 |
| 9 | §5 给 hw-lead 的 S6 认领句 (现役板坐标版) + 帧声明必须与 `HW/PCB/BOARD_FRAME_CALIBER.md` 一致 | ✅ **通过** | §5 全表; 明写「两边不得各用一套; 不一致 ⇒ 停手回报 main」 |
| 10 | 追加式订正 `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (老字一字不删) | ✅ **通过** | 追加段含帧声明 + 订正 ① (点名 B5 第 ① 条) + 订正 ② (两种物理产品); ★**前 558 行逐字节未动 (已用 `head -c` md5 比对核过)** ★ |
| 11 | 新建 `MECH/check_board_frame_coords.py` (C1~C4) | ✅ **通过** | 四项全绿, rc=0 |
| 12 | C1 帧标签: 漏标一条即红 | ✅ **通过** | selftest ② (抽掉一张表的表头帧标签 ⇒ C1 红, 错误 1 条) |
| 13 | C2 归一后窗口压 SoM 焊盘数 = 0 | ✅ **通过** | 实测四个窗口全 0; selftest ① / ③ 两条反向用例都红了 |
| 14 | C3 两套坐标不可代入 (负向断言) | ✅ **通过** | 报出 56 / 10; selftest ④a (旧矩形当新坐标喂 ⇒ C2 抓到 56) + ④b (旧矩形挪开 ⇒ C3 报 0 且红) |
| 15 | C4 受保护 5 件 md5 前后逐字节不变 | ✅ **通过** | 四项全过; selftest ⑤ (改 `.kicad_pro` ⇒ C4 红) |
| 16 | `--selftest` 反向用例 ≥ 5 条, 每条自证真改到目标 | ✅ **通过** | ★**实跑 7 条** ★ (① ② ③ ④a ④b ⑤ ⑥), 每条都打印了改动前后的 md5 与命中数 |
| 17 | 用 main 开的 key `iss273_h1_anchor_single_source` 补 answer, 闭合 pm.yaml 那条 | ✅ **通过** | `state=answered` / answers=1 / foreign=0 |
| 18 | 回答 `iss273_mech_ledger_format_contract` (给现值 + 落点建议) | ✅ **通过** (★**need 本身仍 pending, 见 B1-10 与 B5-1★**) | answer 原文已在 mech.yaml; 状态需 main 代录才翻绿 |
| 19 | 回答 `iss273_mech_ledger_itself_anchor` (给建议 + 代价, 不代拍) | ✅ **通过** (★**同上★**) | 同上 |
| 20 | 交卷单 B1~B6 六块齐全 | ✅ **通过** | 本文件 |
| 21 | 分片登记 2 claim + 3 artifact + 1 need(to hw-lead) + status | ✅ **通过** | `state/fragments/mech.yaml` |
| 22 | 验收命令全绿 (`board_port_opening_s6_check --json` / `jd_y0_feasibility --selftest` / `check_demo_struct_truth` ×2 / `check_board_frame_coords` ×2 / `merge.py` / `gate_check.py`) | ✅ **通过** | ★**全部 rc=0; `gate_check.py` Q1 = 18/18** ★ |
| 23 | ★**已知现状 `bash state/pcbnew_py.sh state/check_pcb_nets.py` rc=1** ★ | ★**未验改善 (本来就不归本单)** ★ | ★**跑后仍 rc=1 (`板子与网表不等价`); 本单零写板 ⇒ 没有让它更糟; ★**板多 2 个带网焊盘 (F1 落表引起) 的历史成因不变** ★ |
| 24 | 零实物 | ✅ **通过** | ★**实物 `[实测]` = 0 条** ★ |

---

## B3 反向自证 (★实跑原始输出★)

> ★**原始日志全文: `logs/iss276/acceptance_01_all.log`** ★

### ★B3.1 新闸 (`MECH/check_board_frame_coords.py`) 四项 ★
```
$ python3 MECH/check_board_frame_coords.py
rc=0
--- C1 --- ✅ 过
--- C2 --- ✅ 过
--- C3 --- ✅ 过
--- C4 --- ✅ 过
【结论】✅ 四项全过
   已声明帧: ['B160x100', 'F30A']
   窗口→帧: [('port_open_debug_bench', 'B160x100'), ('port_open_uart_bench', 'B160x100'),
             ('led_window_g_bench_hard', 'B160x100'), ('led_window_g_bench_recommended', 'B160x100'),
             ('legacy_port_open_60x30', 'F30A'), ('legacy_led_window_60x30', 'F30A')]
   SoM 焊盘总数 (P1..P4): 400
   窗口 'port_open_debug_bench'    X 137.850..148.050 × Y 54.300..58.900 ⇒ 压住 SoM 焊盘 = **0**
   窗口 'port_open_uart_bench'     X 13.790..23.990  × Y 66.300..70.900 ⇒ 压住 SoM 焊盘 = **0**
   窗口 'led_window_g_bench_hard'  X 1.550..3.450    × Y 1.450..98.950  ⇒ 压住 SoM 焊盘 = **0**
   窗口 'led_window_g_bench_recommended' X 6.940..8.250 × Y 63.700..67.900 ⇒ 压住 SoM 焊盘 = **0**
   旧矩形 'legacy_port_open_60x30' (帧 F30A) 喂进现役板坐标 ⇒ 压住 SoM 焊盘 = **56**
       {'J_SOM_P1': 56, 'J_SOM_P2': 0, 'J_SOM_P3': 0, 'J_SOM_P4': 0}
   旧矩形 'legacy_led_window_60x30' (帧 F30A) 喂进现役板坐标 ⇒ 压住 SoM 焊盘 = **10**
       {'J_SOM_P1': 0, 'J_SOM_P2': 0, 'J_SOM_P3': 10, 'J_SOM_P4': 0}
   ✅ HW/PCB/demo_mainboard.kicad_pcb 基线 611b869e13518c3c023fb178f91a0075 ⇒ 现值 611b869e13518c3c023fb178f91a0075
   ✅ HW/PCB/demo_mainboard.kicad_pro 基线 3e504d2be83152e337949723e909be1b ⇒ 现值 3e504d2be83152e337949723e909be1b
   ✅ HW/netlist_v1.csv 基线 e06c1dd633566aa44732762c2ff99d1c ⇒ 现值 e06c1dd633566aa44732762c2ff99d1c
   ✅ HW/netlist_v1_pins.csv 基线 287e7861a0d1007748d92d9fbecdd490 ⇒ 现值 287e7861a0d1007748d92d9fbecdd490
   ✅ HW/BOM_v1.csv 基线 94642d07a69e8d60dd2af57f69b93607 ⇒ 现值 94642d07a69e8d60dd2af57f69b93607
```

### ★B3.2 反向用例七条 (★每条自证真改到目标★) ★
```
$ MECH_SANDBOX_DIR=<workspace>/tmp/iss276_sandbox/selftest python3 MECH/check_board_frame_coords.py --selftest
rc=0
  [基线] C1=OK C2=OK C3=OK C4=OK
  [OK ] ① 改窗口一个角 (x0 137.850 ⇒ 13.650) ⇒ C2 红: 是 · md5 c0704e41 ⇒ 2ca37cad ·
         C2 命中数=[('port_open_debug_bench', 100), ...]
  [OK ] ② 抽掉一张表的表头帧标签 ⇒ C1 红: 是 · md5 c0704e41 ⇒ 34af35b6 · C1 错误 1 条
  [OK ] ③ 把窗口挪进 SoM 区 (x0 20.000 / y0 8.000) ⇒ C2 红: 是 · md5 c0704e41 ⇒ 895c0547 ·
         C2 命中数=[('port_open_debug_bench', 352), ...]
  [OK ] ④a 把旧 60×30 矩形当现役板坐标喂 ⇒ C3 报出压住焊盘数 [('legacy_led_window_60x30', 10)] ·
         C2 抓到旧矩形压住 SoM **56** 个 (C2 红=True) · 改动生效=True · md5 c0704e41 ⇒ aa04d646
  [OK ] ④b 把旧矩形挪到不压 SoM 处 ⇒ C3 红=True · 报出 [('legacy_port_open_60x30', 0),
         ('legacy_led_window_60x30', 10)] · 改动生效=True · md5 c0704e41 ⇒ 76434f2d
  [OK ] ⑤ 改受保护件 (.kicad_pro 追加 1 字节) ⇒ C4 红: 是 · md5 3e504d2b ⇒ 5d7e7c4a · C4 错误 1 条
  [OK ] ⑥ 真件 5 件 md5 跑完自检后仍逐字节不变: 是
【自检结论】✅ 一致
```
★**★ 自证要点 (★为什么这七条不是摆设★)** ★
- ★**② 证明 C1 真的在读帧标签**: 抽掉的只是**一张表的表头**那一处, 若 C1 写成「整节继承」或把「帧:」这种空标签也算数, 这条就不会红 ⇒ ★**C1 的词表里只收「能指名道姓说出是哪一套坐标」的词, 「帧:」这种光有标签没名字的不算** ★
- ★**④b 证明 C3 的数是从板算的, 不是写死的**: 把旧矩形挪到不压 SoM 的位置 ⇒ C3 报 **N = 0** 且判红 ⇒ ★**若 C3 的 56/10 是硬编码, 这条不会红** ★
- ★**⑥ 证明自检没有碰真件**: 自检全程在 `workspace/tmp` 的沙盒副本上跑, 跑完真件 5 件 md5 仍与基线逐字节相同

### ★B3.3 既有闸脚本全绿 (★一个都没改★) ★
```
$ python3 MECH/board_port_opening_s6_check.py --json        rc=0
$ python3 MECH/jd_y0_feasibility.py --selftest              rc=0   [自检] ✅ 一致
$ python3 MECH/check_demo_struct_truth.py                   rc=0   【结论】23/23 组检查通过 | FAIL 0 组
$ python3 MECH/check_demo_struct_truth.py --selftest        rc=0   反向用例: 21/21 抓到了
$ python3 state/merge.py                                    rc=0   ✅ STATE.yaml 已刷新 · 未闭合需求 266
$ python3 state/gate_check.py                               rc=0   【Q1 交付齐备率】 18/18 个必填验收块齐全
```

### ★B3.4 受保护件 md5 跑前跑后 (★逐字节★) ★
```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
```
★**受保护 MECH 既有判据脚本 (★一字不许动, 跑前跑后 md5 相同★)** ★
```
6972b867c8243bc971408f972dc7727e  MECH/check_demo_struct_truth.py
db58ff6a2afc28b8bf517e3c57c56bc1  MECH/service_port_check.py
be8bf0ce94beaf96b1ecba71a45dfd44  MECH/board_port_opening_s6_check.py
55db53464eb4a559628f99d6ccd1546f  MECH/jd_y0_feasibility.py
5757774f817595649240fbe0d45b1b77  MECH/BOARD_GEOM_30MM.md
```

### ★B3.5 ISS-273 三条 need 的状态实测 (★`state/merge.py` 之后读 `STATE.yaml`★)** ★
```
[main]     key=iss273_h1_anchor_single_source to=mech-lead state=answered answers=1 foreign=0   ★闭合★
[mech-lead] key=iss273_mech_ledger_format_contract to=main state=pending answers=0 foreign=1  ★需 main 代录★
[mech-lead] key=iss273_mech_ledger_itself_anchor       to=main state=pending answers=0 foreign=1  ★需 main 代录★
```

---

## B4 接口取值声明 (interface_claims)

| key | value | note | ref |
|---|---|---|---|
| `iss276_mech_bench_frame_caliber` | ★**现役 160×100 台架板坐标系归一页已立: 一切坐标 = Edge.Cuts 中心线 0..160 × 0..100 (160.00 × 100.00; 笔画外缘 160.10 × 100.10) ⇒ 与 `MECH/BOARD_GEOM_30MM.md` 的 60×30 套A 坐标【不是同一套】, 两套数不可互相代入** ★ | ★**ISS-276; 零写板/零落表/零改既有 MECH 判据脚本; 机器闸 = `MECH/check_board_frame_coords.py` (新建, C1~C4)** ★ | `HANDOFF/2026-11-17_mech-lead_ISS276_MECH侧坐标系归一与三条need收口.md` |
| `iss276_mech_iss273_three_needs_closed` | ★**ISS-273 留下的三条已收口: (1) 用 main 开的原 key `iss273_h1_anchor_single_source` 补 answer (to=main) ⇒ pm.yaml 那条 pending need 闭合; (2) `iss273_mech_ledger_format_contract` 给出 MECH 侧看到的格式契约现值 (单号|文件名|改前md5|改后md5 四项同行, `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5/§18.4) + 落点建议【HW 侧落表作业包模板】; (3) `iss273_mech_ledger_itself_anchor` 给出建议与代价【不建议加在台账本体上; 要加只接【只读侧】锚】(只给建议, 不代 main 拍)** ★ | ★**三条 answer 全部写在 `state/fragments/mech.yaml`, key 与 main 开的 key 逐字一致 ⇒ merge.py 按 key 配对** ★ | 同上 |

★**另在 `state/fragments/mech.yaml` 新增 1 条 need 给 hw-lead (★见 B5-2★)** ★

---

## B5 未决项与卡点 (★需要谁回答什么★)

| # | 未决 / 卡点 | 找谁 | ★**为什么本单不代拍** ★ |
|---|---|---|---|
| ★**B5-1** ★ | ★**两条 mech→main 的 need (`iss273_mech_ledger_format_contract` / `iss273_mech_ledger_itself_anchor`) 的 answer 原文我已写进 `state/fragments/mech.yaml`, 但 `state/merge.py` 的配对规则是「只有【被问的那个 agent】的 answer 才闭合」⇒ 这两条仍 `pending`, 我的 answer 落在 `foreign_answers` 位** ★ | ★**main** ★ | ★**闭合动作 = 把这两条 key 的 answer 落到 `state/fragments/pm.yaml` (或给 need 加 `decision` 字段) —— 那是 main 的分片, 我一个字不许改** ★ |
`| ★**B5-2** ★ | ★**S6 认领句已改成帧: `B160x100` (160×100 台架板) 版本 ⇒ 请与 `HW/PCB/BOARD_FRAME_CALIBER.md` (ISS-274 同批, hw-lead 出) 对齐后再收进 §3-S6** ★ — ★**★2026-11-17 06:5x 已实读互核: 帧 id / 板框口径 / 两个旧矩形的归属与危害计数 (56 / 10) 逐条一致 ⇒ 帧声明已对齐, 可以直接收**★ ⇒ ★**唯一还差的 = 把 §3-S6 的「检修口/调试口开口」一条拆成两条 (见 B5-3), 那是 main 的裁决** ★ | ★**hw-lead** ★ | ★**作业包是 hw-lead 的文件, 本单零字节写入; S6 条目怎么写 = hw-lead 的活** ★ |`
| ★**B5-3** ★ | ★**S6 条目怎么拆**: 「检修口/调试口开口」在帧: 160×100 台架板 上必须拆成两条 (调试口 / UART 检修口), 因为两者 ΔX = 123.56 mm ⇒ 一个开口罩不住 | ★**main 拍 + hw-lead 执行** ★ | ★**拆条方式影响 §3-S6 的结构, 属 main 的裁决** ★ |
| ★**B5-4** ★ | ★**开口 Y 的一切数建立在「座体高 2.54」假设上 (ISS-267 F-8) ⇒ 真实座体型号/高度 = [0数据]** ★ | ★**hw-lead (选型) + mech (复核)** ★ | ★**选型不在 MECH 地界** ★ |
| ★**B5-5** ★ | ★**`D_LED_G` 的出光面 / 结构侧光孔位置 = [0数据]** ★ ⇒ 板侧坐标必须与结构侧光孔对齐, 结构侧该数目前没有 | ★**mech (下一单) + hw-lead** ★ | ★**本单是台架板坐标归一, 结构侧光孔要单独给** ★ |
| ★**B5-6** ★ | ★**排版器要不要按网络邻近分组** (`LED_G_D` 93.49 → <1 mm) | ★**hw-lead** ★ | ★**这是排版规则问题, 不在 MECH 地界; MECH 侧只给净距敏感度表** ★ |
| ★**B5-7** ★ | ★**台账格式契约的最终落点 / 台账自身要不要加锚** | ★**main 拍** ★ | ★**我给的是建议与代价 (B1-11), 不代拍** ★ |
| ★**B5-8** ★ | ★**`HW/PCB/demo_mainboard_params.json` 的连接器参数与落表板对不上** (`uart_position_mm` 写 (49.0, 6.0) / `uart_pins` 4 / `jtag_ref` 写 `J_JTAG` · `jtag_position_mm` (52.0, 13.0) / `jtag_pins` 5 ⇒ 落表板实为 `J_UART`@(20.74,70.00) 2 脚 + `J_DEBUG`@(144.30,58.00) 4 脚) ⇒ ★**这个 params JSON 不是现役板的真源** ★ | ★**hw-lead (建议)** ★ | ★**HW/ 文件不是我的地界, 本单只做登记, 不改** ★ |
| ★**B5-9** ★ | ★**`bash state/pcbnew_py.sh state/check_pcb_nets.py` 仍 rc=1** (板子与网表不等价; 板多 2 个带网焊盘 = F1 落表引起) | ★**hw-lead / main (已知历史债)** ★ | ★**与本单无关; 本单零写板 ⇒ 没有让它更糟** ★ |

★**★ 三个不许搞混的 (★本轮踩出来的★)** ★
1. ★**「帧: 60×30 套A 坐标」≠「帧: 160×100 台架板 坐标」** ★ ⇒ 两个物理产品 (SoC 直上板 vs SoM 承载区) ⇒ 坐标不可互相代入 ⇒ **本单的归一就是为了让别人不必再踩这一脚**
2. ★**「ISS-267/271 判红」≠「现役板开不了工」** ★ ⇒ 它们判红的是【60×30 / 60×15 装不下检修口】, 不是【160×100 台架板不能用】⇒ 本单归一后的开口是另一道几何题, 两句不许并成一句
3. ★**「answer 的 key 写对」才是闭合** ★ ⇒ 我在 mech.yaml 写 answer ⇒ merge.py 按 key 配对 ⇒ key 与 main 开的差一个字就【不闭合】⇒ **本单用的是 `iss273_h1_anchor_single_source` 这个原 key** ★ ⇒ 已 `grep` + 读 `STATE.yaml` 双重确认 (`state=answered`)

---

## B6 自证复现命令 (★main 可原样跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ---- ① 新闸 (本单新建) ----
python3 MECH/check_board_frame_coords.py                  # rc=0 (C1/C2/C3/C4 四项全过)
python3 MECH/check_board_frame_coords.py --compute        # 帧: 160×100 台架板 的全部实算数
python3 MECH/check_board_frame_coords.py --json           # 机器可读
MECH_SANDBOX_DIR=/home/yuewuya/.openclaw/workspace/tmp/iss276_selftest \
  python3 MECH/check_board_frame_coords.py --selftest     # rc=0 (反向用例 7 条全抓到)

# ---- ② 既有闸 (一个都没改, 跑前跑后 md5 相同) ----
python3 MECH/board_port_opening_s6_check.py --json        # rc=0
python3 MECH/jd_y0_feasibility.py --selftest              # rc=0
python3 MECH/check_demo_struct_truth.py                   # rc=0 (23/23)
python3 MECH/check_demo_struct_truth.py --selftest        # rc=0 (21/21)

# ---- ③ 分片 + 门禁 ----
python3 state/merge.py                                    # rc=0
python3 state/gate_check.py                               # rc=0 (Q1 18/18)

# ---- ④ 受保护件 md5 (跑前跑后必须逐字节相同) ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# 期望: 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b /
#       e06c1dd633566aa44732762c2ff99d1c / 287e7861a0d1007748d92d9fbecdd490 /
#       94642d07a69e8d60dd2af57f69b93607

# ---- ⑤ 受保护 MECH 既有判据脚本 md5 (一字不许动) ----
md5sum MECH/check_demo_struct_truth.py MECH/service_port_check.py \
       MECH/board_port_opening_s6_check.py MECH/jd_y0_feasibility.py \
       MECH/BOARD_GEOM_30MM.md
# 期望: 6972b867c8243bc971408f972dc7727e / db58ff6a2afc28b8bf517e3c57c56bc1 /
#       be8bf0ce94beaf96b1ecba71a45dfd44 / 55db53464eb4a559628f99d6ccd1546f /
#       5757774f817595649240fbe0d45b1b77

# ---- ⑥ ISS-273 三条 need 的闭合状态 ----
python3 -c "
import yaml
st=yaml.safe_load(open('STATE.yaml',encoding='utf-8'))
for dom in ('main','mech-lead'):
    for n in st['domains'][dom].get('needs_from',[]):
        if n.get('key','').startswith('iss273'):
            print(dom, n['key'], 'to='+str(n['to']), n['state'],
                  'answers=%d foreign=%d'%(len(n.get('answers') or []), len(n.get('foreign_answers') or [])))
"
# 期望: main iss273_h1_anchor_single_source to=mech-lead answered answers=1 foreign=0
#       mech-lead iss273_mech_ledger_format_contract to=main pending answers=0 foreign=1
#       mech-lead iss273_mech_ledger_itself_anchor to=main pending answers=0 foreign=1
```

★**★ 已知现状 (不必修, 但写清★)**: ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` 现在 rc=1 (板多 2 个带网焊盘 = F1 落表引起) ⇒ ★**与本单无关; 本单只需保证没让它更糟 (已保证: 板 md5 逐字节不变)** ★

---

## ★附 A · 交卷物清单 (6 件 + 1 件追加订正) ★

| # | 交卷物 | 类型 | 说明 |
|---|---|---|---|
| 1 | ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`** ★ | 新建 | 坐标系归一页: §1 坐标系声明 (置顶) · §1.1 两套坐标物理对照 · §1.2 机器块 · §2 SoM 承载区实测 · §3 开口 (两个窗口 + 合并开口不可行 + 123.56 mm 的影响) · §4 `D_LED_G` (走线根因 + 可放行空间 + 净距敏感度 + 约束条件) · §5 给 hw-lead 的 S6 认领句 · §6 边界与证据分级 |
| 2 | ★**`MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md`** ★ | 追加订正 | 追加段含帧声明 + 订正 ① (点名 B5 第 ① 条「逐字抄进 §3-S6」对现役板不成立 ⇒ 已改为引用归一页) + 订正 ② (两种物理产品) + 机器闸用法; ★**老字一字未删** ★ |
| 3 | ★**`MECH/check_board_frame_coords.py`** ★ | 新建 (机器闸) | C1 帧标签 / C2 不压 SoM 座 / C3 负向断言 / C4 受保护 5 件 md5; `--compute` / `--json` / `--selftest` (7 条反向用例); ★**只读 import `board_port_opening_s6_check.py` 取 `BASE`/`TOL`/`CRIT`/`OPEN_X`/`OPEN_Y` ⇒ 阈值零漂移; 不改任何既有脚本** ★ |
| 4 | ★**`HANDOFF/2026-11-17_mech-lead_ISS276_MECH侧坐标系归一与三条need收口.md`** ★ | 新建 (交卷单) | 本文件, B1~B6 六块齐全 |
| 5 | ★**`state/fragments/mech.yaml`** ★ | 分片 (原子写) | 2 claim + 3 answer (ISS-273 三条) + 3 artifact + 1 need (to hw-lead) + status; ★**全部走 `state/frag_write.py --agent mech-lead`, 禁止 `open(p,"w")`** ★ |
| 6 | ★**`logs/iss276/acceptance_01_all.log`** ★ | 新建 (原始日志) | 全部验收命令的 rc 与原始输出 |
| ★**+1** ★ | ★**`HANDOFF/2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md`** ★ | ★**追加订正 (超出清单, 主动补的)** ★ | ★**理由: 那句「逐字抄进 §3-S6 就行」的原话在 ISS-271 的【交卷单】第 37 行, 不在 §1~§5 工作包正文里 ⇒ 只订正工作包 = 订正不到原话 ⇒ 本单追加了一段订正把那一句点名作废; ★**追加式, 前 37 行逐字节未动 (已用 md5 比对核过)★** ★ |

---

## ★附 B · 与任务书/既有文档的三处口径差异 (★我实读的数与它们不一致, 我按实读的写并留痕★) ★

| # | 任务书/既有文档给的 | ★**我实读的 (本单采用)** ★ | 差在哪 |
|---|---|---|---|
| 1 | Edge.Cuts = **160.10 × 100.10 mm** | ★**中心线 160.00 × 100.00; 笔画外缘 160.10 × 100.10** ★ | 两者都对, 只是口径不同: 160.10 是中心线 + 线宽 0.1 的笔画外缘; ★**落件坐标按中心线 0..160 / 0..100** ★; `HW/PCB/demo_mainboard_params.json` 板段写的也是 `160.0 / 100.0` ⇒ 中心线口径与参数文件一致 |
| 2 | SoM 承载区 = X **13.65..70.35 (56.70mm)** × Y 7.61..54.39 (46.78mm) | ★**X = 焊盘铜箔 15.100..68.900 (53.80) / 座体 F.Fab 13.700..70.300 (56.60) / 保守包络 13.650..70.350 (56.70) —— 三个口径都登记** ★ | 任务书给的 X 是【座体 ± 0.05 笔画半宽】的保守包络, Y 是【焊盘铜箔】; ★**Y 向 46.78 与任务书完全一致; 结论 (装不进 60×30 / 60×15) 不受影响 (铜箔 46.78 / 座体 46.20, 两个都 > 30)** ★ |
| 3 | `J_DEBUG` ↔ `J_UART` 相距 **123.6 mm** | ★**ΔX = 123.56 mm; 直线 = 124.141 mm** ★ | 123.6 = ΔX (ISS-267 F-7 那个数也是 ΔX); ★**两者都够判「罩不住」, 但报数要说清是哪一个** ★ |

★**⇒ 这三处都不影响任何结论方向, 我按实读值写并留痕, ★不擅自改既有文档里的数 (那是 main/hw-lead 的口径裁决)** ★

★**★ 附 B.1 · 与 hw-lead 的 ISS-274 的互核 (★2026-11-17 06:5x 本机实读★)** ★
- ★**hw-lead 的 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 的 JSON 块 `cal:FRAMES` 自称「三套坐标帧的机器标识的唯一权威表」⇒ 本单把本页机器块里的帧 id 从自造名 (`160x100-bench` / `60x30-setA`) 【改成逐字对齐它的 `B160x100` / `F30A` / `P60x15`】★ ⇒ **两边不是各用一套** ★
- ★**⇒ 改完后本单的机器闸 `MECH/check_board_frame_coords.py` 四项仍全绿、七条反向用例仍全抓到 (已重跑)** ★
- ★**⇒ 两个闸互为交叉验证**: hw-lead 的 `HW/check_board_frame_caliber.py` C5 实跑报出的压焊盘数 = `J_SOM_P3` 10 / `J_SOM_P1` 56 ⇒ **与本单 C3 的 10 / 56 逐字相同** ★
- ★**⇒ 本单 §5 已按 hw-lead §2.1 的写法补上「ISS-271 警语」一条 (帧: `F30A` + 不可当 S6 坐标用) ⇒ hw-lead 抄进 §3-S6 时他的闸 (e) 不会红** ★

---

## ★附 C · 施工日志 (★逐条追加, 不攒到最后★) ★

- `2026-11-17 06:3x` ★**骨架先落**: 交卷单骨架 (本文件) + `state/frag_write.py --agent mech-lead` 登记 2 条 claim + status=in_progress ⇒ ★**防 gateway reload 打掉零交卷物** ★
- `2026-11-17 06:4x` ★**本机实读**: 板文件 (186 封装 / 400 个 SoM 焊盘 / Edge.Cuts / `J_DEBUG`/`J_UART`/`D_LED_G`/`R_LED_G` 的铜箔外框) · `HW/netlist_v1_pins.csv` 的 `LED_G_D` 网定义 · `HW/PCB/demo_mainboard_params.json` 板段 · `.kicad_pro` 的 DRC 规则 (`min_clearance` 0.0 / `min_copper_edge_clearance` 0.5 / `zones.min_clearance` 0.5) ⇒ ★**基线 md5 五件已记 (跑前)** ★
- `2026-11-17 06:4x` ★**建机器闸**: `MECH/check_board_frame_coords.py` (新建) ⇒ 先出 C1 红 (漏帧标签 40+ 处) ⇒ ★**按 C1 的判据反过来把归一页改到「每个坐标组都有主」** ★ ⇒ 四项全绿
- `2026-11-17 06:5x` ★**建归一页 + 追加订正**: `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (新建) · `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (追加段) · ★**ISS-271 交卷单也追加了一段订正 (原话在第 37 行, 只订工作包订不到)** ★
- `2026-11-17 06:5x` ★**修自己闸里的两个符号错**: 障碍阻挡区间写成了 `(bx0 − rel[0], bx1 − rel[1])` (应 `(bx0 − rel[1], bx1 − rel[0])`) ⇒ ★**改正后 LED 可放行空间从「1992 条碎带」变成「2 条整高带 + 一条干净的最近落位带 X 6.940..8.250」** ★ ⇒ ★**这两个错是我自己写的, 已改; 不是既有脚本的问题 (既有脚本一个字没动)★ ★
- `2026-11-17 06:5x` ★**闭合 ISS-273 三条**: `state/frag_write.py --agent mech-lead` 三次 `--add-answer` ⇒ ★**`iss273_h1_anchor_single_source` 实测 `state=answered`; 另两条落在 `foreign_answers` 位 (merge 配对规则: 只有被问的那个 agent 的 answer 才闭合) ⇒ 归 main 代录** ★
- `2026-11-17 06:5x` ★**验收全跑**: 8 条命令全 rc=0 · `gate_check.py` Q1 18/18 · 五件受保护 md5 逐字节不变 · 受保护 MECH 既有脚本 md5 不变 ⇒ ★**原始输出落 `logs/iss276/acceptance_01_all.log`** ★
- `2026-11-17 06:5x` ★**分片登记收尾**: 3 artifact + 1 need (to hw-lead) + status(phase=delivered, progress_pct=100) ★

★**★ 本单到此为止: 零写板 · 零落表 · 零改既有 MECH 判据脚本 · 零改 HW · 零改 `MECH/BOARD_GEOM_30MM.md` · 零外发 · 零实物 · 不替老板拍板 · 不自签 issue_log · 不写别人的分片 ★** ★
