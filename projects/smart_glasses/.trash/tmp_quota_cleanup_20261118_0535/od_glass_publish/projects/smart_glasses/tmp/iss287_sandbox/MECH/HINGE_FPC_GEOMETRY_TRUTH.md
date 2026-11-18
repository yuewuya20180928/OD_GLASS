# MECH/HINGE_FPC_GEOMETRY_TRUTH.md —— 跨铰链 FPC 几何口径收口页 (ISS-240)

> **交卷人**: 结构总工 (mech-lead, 带散热) · **日期**: 2026-11-16 · **单号**: ISS-240
> **本单性质**: ★**内部活 · 不是 PCB 布线/布局 · 不是老板级拍板**★ —— 只做「口径收口 + 文档补标 + 改法映射 + 新机器门禁」, **不出结构方案, 不改网表/脚表/BOM/板, 不改任何受保护脚本**。
> **本单 [实测] 条数 = 0** (无样机): 全部数 = **[推算]**, 输入是网表/脚表/裁定块的**实测值** (脚本现场解析所得), 不是实物量测。
> **零外发**: 未发邮件 / 未联系供应商 / 未下采购单。

---

## 0 一句话结论 (先看这里)

★**跨铰链 FPC 几何不是一个"三选一"的问题, 是一个【架构口径已经变了】的问题** ★

1. ★**老板 2026-11-02 19:25 指示② (PROJECT_TRACKER.md §0 锁死表第 44 行, 已定不是待拍板)**: demo 硬件形态 = 主板一块板 + sensor/屏幕各画成模组 + FPC 软排短距连到主板 ⇒ ★**跨铰链取消** ★ ⇒ ★**铰链区 FPC 几何账整块对 demo 板不适用** ★
2. ★**网表已经按它落了**: `HW/netlist_v1.csv` board 栏实测 = MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15; ★**`J_CHG` board=HINGE · `CONN_CAM` board=MAIN_PCB · `CONN_LIGHT` board=MAIN_PCB · `J_USB_C` board=MAIN_PCB · `J_TYPE_C` board=CHG_BOARD** ★ ⇒ ★**demo 板真跨铰链链路 = 1 条 (J_CHG)**, `MECH/hinge_usb_check.py` 的 `CROSS_LINKS` 后三条 (CONN_USB / CONN_CAM / CONN_LIGHT) ★**按现网表都不跨铰链** ★
3. ⇒ ★**25.00 与 31.50 都不是 demo 板的现行值** —— 两个数都是拿**4 条跨铰链链路**算的, 其中 3 条在 demo 板不跨铰链; ★**且 25.00 与"真源按各自 pitch 算出来的 25.30"是两个完全不同的构成** (16p@0.5+20p@0.5+4p@0.5+10p@0.5 vs 31p@0.3+22p@0.5+10p@0.5) ⇒ ★**25.00 是【两个不同的错凑出的巧合】, 不是从真源推出来的数** ★
4. ⇒ ★**demo 板现行口径 = 只算 J_CHG**: 高度占位 **10p×0.5 = 5.00 mm** ⇒ vs 净高 38.00 ⇒ ★**余 33.00 mm**; 径向占位 **R_min 3.00 + 1×(0.20+0.15) = 3.35 mm** ⇒ vs 铰链段前后内净空 5.40 ⇒ ★**余 2.05 mm** ★
5. ⇒ ★**本单只交「映射 + 门禁」, 不替 main 改 G7 判据, 不改任何 claim 的 value** (改受保护脚本/判据 = H-1 重基线 = main 的活) ★

---

## 1 基线常量 (每一格都写出处; 本页所有数都能自己重算)

| 常量 | 值 | 出处 | 证据 |
|---|---|---|---|
| 镜脚根部净高 (垂直可用) | **38.00 mm** | `MECH/MECH_BUDGET.md` L1124 (腔体净高锁死) | `[官方-项目内]` |
| ~~镜脚根部净高 37.0~~ | **已作废** | 37.0 = 旧叠放模型算式 22+12+3 (`MECH/hinge_usb_check.py` GEOM 注释) | `[推算]` |
| 镜脚前后厚需求 | **7.00 mm** | `MECH/MECH_BUDGET.md` L135 / L137 | `[官方-项目内]` |
| 打印件单壁 | **0.80 mm** | `MECH/MECH_BUDGET.md` §5.4 (FDM 最小可靠壁) | `[官方-项目内]` |
| 铰链段前后内净空 | **7.00 − 2×0.80 = 5.40 mm** | 上两行相减 | `[推算]` |
| 跨铰链 FPC 弯折半径 R_min | **3.00 mm** | `MECH/MECH_BUDGET.md` §1.3 M9 / `MECH/hinge_usb_check.py` GEOM `bend_R_mm` | `[官方-项目内]` |
| FPC 成品厚 t | **0.20 mm** | `MECH/hinge_usb_check.py` GEOM `fpc_t_mm` (4 层 0.5mm pitch 通用值) | `[推算]` |
| FPC 嵌套间隙 gap | **0.15 mm** | `MECH/hinge_usb_check.py` GEOM `fpc_gap_mm` (靠导槽定位) | `[推算]` |
| **径向算式** | **径向占位 = R_min 3.00 + N × (t 0.20 + gap 0.15) = 3.00 + N×0.35** | 同上 | `[推算]` |
| **垂直算式** | **垂直(高度)占位 = Σ(每颗座的触点数 × 该座自己的 pitch)** | ★**每颗座用自己的 pitch —— 一刀切全 0.5mm 是错的** ★ | `[推算]` |
| FPC 带宽口径 (次级) | 触点区 + 2×0.50 走线边距 **每条** | `MECH/hinge_usb_check.py` §2 注释 / `MECH/hw_cross_review_check.py` §1 STK-FPC | `[推算]` |
| 主板板宽 (现行) | **30.00 mm** | `MECH/BOARD_GEOM_30MM.md` L34 (老板 10-29 19:16 拍板 ≤30mm) | `[官方·决策]` |
| ~~主板板宽 12 mm~~ | **已作废** | 12mm 板宽时代口径, 现行 30.00 | `[推算]` |

### 1.1 网表/脚表实测 (本单自己跑, 不照抄)

| 项 | 实测值 | 怎么跑出来的 |
|---|---|---|
| `CONN_CAM` 声明 | **31p @ 0.3mm** | `HW/netlist_v1.csv` L290 = 「★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50))」, board=**MAIN_PCB** |
| `CONN_LIGHT` 声明 | **22p @ 0.5mm** | `HW/netlist_v1.csv` L237 = 「★22p@0.5mm (HIROSE FH12-22S-0.5SH(55)...)」, board=**MAIN_PCB**; 脚表 `HW/netlist_v1_pins.csv` count(CONN_LIGHT)=**22** |
| `J_CHG` 声明 | **1×10p @ 0.5mm** | `HW/netlist_v1.csv` L38 (另 L412/L497 同串) = 「1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)」, board=**HINGE**; 逐脚行 10 脚 (必装 7 / DNP 3) |
| `CONN_USB` | ★**网表 0 命中** ★ (全表只有 L291 一处 note 提到 "跨铰链则经 CONN_USB") | `grep CONN_USB HW/netlist_v1.csv` → 1 命中且在 note 列; 逐脚行 0 条 |
| 逐脚计数 (本单现场解析) | CONN_CAM **31** / CONN_LIGHT **22** / J_CHG **10** / CONN_USB **0** | 解析 `node1/node2` 列的 `REF pinN` 形态 |
| board 栏分布 | **MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15** (总 513 行) | 逐行统计 `board` 列 |
| board=HINGE 的行 | 全部属 **J_CHG** (11 行) + `RAIL_BAT_CHG` 1 + `NET_BAT_PROT` 1 + `NET_CHG_STAT` 1 + `NET_PWR_GOOD` 1 | 同上 |
| ⇒ **demo 板真跨铰链链路** | **1 条: J_CHG** | board==HINGE 的连接器只有 J_CHG |

---

## 2 T1 —— 三(+一)口径对照表 (★每个数都写算式, 不许只给结果★)

> ★**口径行定义**:
> · **R1 脚本收敛版** = `MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS` 硬编码 16/20/4/10, **四条链路的 pitch 一律取 `ffc_pitch_mm` = 0.5**
> · **R2 脚本声明版** = 网表里**声明**的 pin 数 (31/22/0/10), **pitch 一律取 0.5** (camera 错按 0.5 算)
> · **R3 网表真源 pitch 口径** = 网表里**有座的**三颗 (camera/display/J_CHG), **每颗座用自己的 pitch**, 暂不看 board 栏 (= 整机阶段的问法)
> · **R4 demo 板真跨铰链口径** = **board==HINGE 才算跨铰链** ⇒ **只有 J_CHG** ⇒ ★**这才是 demo 板现行值** ★

| 口径 | CONN_CAM | CONN_LIGHT | CONN_USB | J_CHG | **合计** | **余量 vs 净高 38.00** | FPC 带宽口径 (次级) | 适用性 |
|---|---|---|---|---|---|---|---|---|
| **R1 脚本收敛版** | 16 × 0.5 = **8.00** | 20 × 0.5 = **10.00** | 4 × 0.5 = **2.00** | 10 × 0.5 = **5.00** | **25.00** | 38.00 − 25.00 = **13.00** | 25.00 + 4×1.0 = 29.00 → 余 9.00 | ★**对 demo 不适用** (4 条链路里 3 条不跨铰链) ★ |
| **R2 脚本声明版** | 31 × 0.5 = **15.50** | 22 × 0.5 = **11.00** | 0 × 0.5 = **0.00** | 10 × 0.5 = **5.00** | **31.50** | 38.00 − 31.50 = **6.50** | 31.50 + 4×1.0 = 35.50 → 余 2.50 | ★**对 demo 不适用**; ★**且 camera 按 0.5 算本身就是错的** (真值 31×0.3 = 9.30) ★ |
| **R3 网表真源 pitch** | 31 × **0.3** = **9.30** | 22 × 0.5 = **11.00** | — (网表 0 命中) | 10 × 0.5 = **5.00** | **25.30** | 38.00 − 25.30 = **12.70** | 25.30 + 3×1.0 = 28.30 → 余 9.70 | ★**整机阶段口径** (★与 `MECH/rebase_20261106.py` §2 "触点区合计 25.30" **逐位一致** = 交叉验证 ✓★) ★ |
| **R4 demo 真跨铰链** ★**现行** ★ | — (board=MAIN_PCB) | — (board=MAIN_PCB) | — (网表 0 命中) | 10 × 0.5 = **5.00** | **5.00** | 38.00 − 5.00 = **33.00** | 5.00 + 1×1.0 = 6.00 → 余 32.00 | ★**demo 板现行口径** (老板 11-02 19:25 指示② + 网表 board 栏) ★ |

### 2.1 ★R1 的 25.00 与 R3 的 25.30 = 两个完全不同的构成 ⇒ 巧合, 不是推导 ★

```
R1 (脚本收敛版):  16 × 0.5 = 8.00
                + 20 × 0.5 = 10.00
                +  4 × 0.5 = 2.00
                + 10 × 0.5 = 5.00
                --------------- = 25.00        ← 构成: 16p@0.5 + 20p@0.5 + 4p@0.5 + 10p@0.5
R3 (网表真源):    31 × 0.3 = 9.30
                + 22 × 0.5 = 11.00
                + 10 × 0.5 = 5.00
                --------------- = 25.30        ← 构成: 31p@0.3 + 22p@0.5 + 10p@0.5

两者差 0.30 mm, 但【脚数构成完全不同】(16/20/4/10 vs 31/22/10) ⇒
★ 一旦 camera 换 pitch (0.3→0.5) / 换料, 或 display 座按 ISS-237 之外再变, 25.00 不会跟着变 ⇒
★ 25.00 不是从真源推出来的数, 是【两个不同的错凑出的巧合】 ★
```

### 2.2 旧口径一律留痕 (★一个不许删★)

> ★**行号索引 = ISS-240 补标完成后的实测行号 (★用本单门禁自己的 `legacy_hits` 口径逐行扫出来的, 不是手写估的★)★**
> ★**正文行数 = 512 (标注前后都是 512 ⇒ 只加不删, 一个实测原文都没删)** ★

| 旧数 | 现在写在哪 (★2026-11-16 实测行号★) | 状态 |
|---|---|---|
| **40p** (CONN_CAM / CONN_LIGHT 规划口径) | `MECH/USB_HINGE_STRUCTURE.md` **13 处**: L16/L75/L90/L91/L98/L100/L123/L320/L324/L325/L335/L346/L347 | ★**已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)** ★ |
| **16p** (CONN_CAM 收敛建议) | **9 处**: L16/L120/L325/L346/L359/L362/L418/L434/L445 | ★**已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)** ★ —— ★**注意: Type-C 的 16p (USB2.0-only 母座) 不作废, 与此无关** (L309/L314/L420 三处属此类) ★ |
| **20p** (CONN_LIGHT 收敛建议) | **9 处**: L16/L120/L337/L346/L359/L362/L418/L434/L446 | ★**已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)** ★ |
| **26p @0.4** (CONN_LIGHT 桥接方案) | **6 处**: L16/L337/L347/L359/L418/L446 | ★**已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)** ★ |
| **12 mm 板宽** | **7 处**: L204/L276/L325/L327/L337/L418/L464 | ★**已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)** ★ —— 现行板宽 30.00 (`MECH/BOARD_GEOM_30MM.md` L34) |
| **25.00** (铰链区堆叠旧值) | **8 处**: L16/L120/L127/L362/L403/L434/L462/L494 | ★**已作废 (依据 老板 2026-11-02 19:25 指示② · demo 硬件形态: 跨铰链取消)** ★ (对 demo 不适用; 整机阶段留作追溯) |
| **31.50** (声明版堆叠旧值) | **10 处**: L15/L119/L123/L125/L127/L346/L403/L433/L462/L494 | 同上 ★**已作废 (架构变了, 不是数错了)** ★ |
| **49.62** (上游 40p 规划堆叠旧值) | **2 处**: L123/L346 | 同上 ★**已作废** ★ |
| **4.40** (铰链区径向旧值 · N=4) | **6 处**: L17/L108/L110/L432/L461/L494 | 同上 ★**已作废** ★ —— ★**现行 demo 径向 = 3.35 (余 2.05) / 整机 3 条 = 4.05 (余 1.35)** ★ |
| **94 pin** (4 条链路声明口径合计) | **6 处**: L14/L92/L96/L279/L317/L458 | ★**已作废 (依据 老板 2026-11-02 19:25 指示②)** ★ —— ★**L279/L317 里的 "8.94" 是 USB-C 物理尺寸, 不是 94 pin (误命中, 不作废)** ★ |

> ★**分片侧同源旧值**: `state/fragments/mech.yaml` 的 `mech_hinge_stack_fixed_mm` = 25.00 / `mech_hinge_stack_declared_mm` = 49.62 / `mech_hinge_radial_mm` = 4.40 / `mech_hinge_links_count` = `0(demo)` ⇒ ★**处置见 §4 的 M-04 / M-07 / M-08 / M-09 (★本单一个字没改, 一票交 main★)** ★
> ★**判定口径**: 本单新门禁 `MECH/check_hinge_fpc_truth.py` 的 **G4** 逐行扫正文, ★**真·旧口径裸命中 = 0 行** ★ (Type-C 16p 按豁免处理, 见上表)

---

## 3 T2 —— 径向账 (铰链区前后向占位)

> 算式: **径向占位 = R_min 3.00 + N × (t 0.20 + gap 0.15) = 3.00 + N×0.35**; **余量 = 铰链段前后内净空 5.40 − 径向占位**

| N | 用哪条链路清单 | 算式 | 径向占位 | 余量 | 出处 |
|---|---|---|---|---|---|
| **N = 4** | 脚本 `CROSS_LINKS` 旧口径 (J_CHG / CONN_USB / CONN_CAM / CONN_LIGHT) | 3.00 + 4×0.35 | **4.40** | 5.40 − 4.40 = **1.00** | `MECH/hinge_usb_check.py` §2 + 文档 §9 `mech_hinge_radial_mm`=4.40 |
| **N = 3** | 网表里有座的 3 颗 (J_CHG / CONN_CAM / CONN_LIGHT), **暂不看 board 栏** | 3.00 + 3×0.35 | **4.05** | 5.40 − 4.05 = **1.35** | ★与 `MECH/rebase_20261106.py` §2 "拓扑B 径向余 1.35mm" **逐位一致** = 交叉验证 ✓ ★ |
| **N = 1** ★**demo 现行** ★ | **board==HINGE ⇒ 只有 J_CHG** | 3.00 + 1×0.35 | **3.35** | 5.40 − 3.35 = **2.05** | 网表 board 栏 (L38/L412/L497) + 老板 11-02 19:25 指示② |

★**三档都 > 0 ⇒ 径向在任何口径下都不是几何否决项** ★ (结论方向不随口径变, 只是余量从 1.00 → 1.35 → 2.05 递增) ★

### 3.1 ★口径差异登记 (本单自己复算出来的, 任务书给的数对不上公式) ★

| 项 | 任务书给的 N=3 值 | 本单按任务书**自带的公式**复算 | 差额来源 |
|---|---|---|---|
| N=3 径向占位 | 3.75 mm | ★**4.05 mm** (3.00 + 3×0.35) ★ | 3.75 只在 "3.00 + 3×0.20 + **1**×0.15" (间隙只算 1 道而非 3 道) 下成立 |
| N=3 余量 | 1.65 mm | ★**1.35 mm** (5.40 − 4.05) ★ | 差 0.30 = 2 道间隙 ×0.15 |

⇒ ★**两个数都列出来, 差额写清来源; 结论方向不变 (都 > 0); 哪一版作数归 main 裁** ★ (本单不替 main 定这个口径)

---

## 4 T3 —— 逐条改法映射 (★只报不改, 一票交 main★)

> **格式**: 文件:行号 · 现在写的 · 应改成什么 · 为什么能改 (依据哪个文件哪一行) · 还差什么 · 归谁改 (本单 / main 排期 / 不许动)

| # | 文件:行号 | 现在写的 | 应改成什么 | 为什么能改 (依据) | 还差什么 | 归谁改 |
|---|---|---|---|---|---|---|
| **M-01** | `MECH/hinge_usb_check.py` `CROSS_LINKS` (L~104) | `["J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"]` (4 条) | ★**按 board 栏取**: 跨铰链 = `board == "HINGE"` ⇒ demo 只有 `J_CHG`; 或显式分列 "demo 口径 (1 条)" / "整机口径 (3~4 条)" 两套 ★ | 网表 board 栏实测 (J_CHG=HINGE · CONN_CAM/CONN_LIGHT=MAIN_PCB · CONN_USB 网表 0 命中) + 老板 11-02 19:25 指示② (`PROJECT_TRACKER.md` §0 锁死表第 44 行) | ★**老板/PM 裁「整机阶段 USB 是否仍跨铰链」+「demo 充电链留不留」** ★ | ★**main 排期** (受保护脚本 ⇒ H-1 重基线, 本单不许碰) ★ |
| **M-02** | `MECH/hinge_usb_check.py` `GEOM["ffc_pitch_mm"]` (L~88) + §2 声明版算式 | 跨铰链 FPC **一律 0.5mm** ⇒ 声明版 31p 按 0.5 算 = 31.50 | ★**每颗座用自己的 pitch** (camera 0.3 / display 0.5 / J_CHG 0.5) ⇒ 声明版 31.50 → **25.30** ★ | 网表 L290 (`31p@0.3mm`) / L237 (`22p@0.5mm`) / L38 (`1×10p@0.5mm`) | 无 (可直接改), 但**同 M-01 走 H-1** | ★**main 排期** ★ |
| **M-03** | `MECH/hinge_usb_check.py` `RECOMMENDED_PINS` (L~107-117) | `CONN_CAM:16 / CONN_LIGHT:20 / CONN_USB:4 / J_CHG:10` (ISS-206 裁 2 老口径) | ★**降级为「历史建议」或删除**; 现行真源 = 31/22/10 (各自 pitch) ⇒ 25.00 不再是任何现行值 ★ | ISS-237 (`HW/STEP1_PARTS_SPEC.md` §0) + 网表/脚表实测 | 同 M-01 | ★**main 排期** ★ |
| **M-04** | `MECH/check_demo_struct_truth.py` G7 (L585-593) | 判据文字「ISS-206 裁 2 的 16p/20p/4p/10p」, 断言 `mech_hinge_stack_fixed_mm == "25.00"` | ★**三档处置见下方 M-04a/b/c** ★ —— ★**这是假绿, 不是小偏差** (钉着一个已被 11-02 指示② + 网表落表作废的架构) ★ | `PROJECT_TRACKER.md` §0 锁死表第 44 行 + 网表 board 栏 | ★**PM 裁** (改判据 = H-1 重基线) | ★**main 排期** ★ |
| **M-05** | `MECH/cavity_recalc_check.py` C9 (L1230-1233) | `re.search(r"key:\s*mech_hinge_stack_fixed_mm\s*\n\s*value:\s*'?25\.00'?")` | 同 M-04 三档 (它同样钉死 25.00) | 同上 | 同上 | ★**main 排期** (受保护, md5 在 MD5_EXPECTED 清单里 ⇒ 本单不许碰) ★ |
| **M-06** | `state/fragments/mech.yaml` claim `mech_hinge_stack_fixed_mm` = `25.00` | 25.00 | ★**不许本单改 value** (G7 + C9 同时钉着) ⇒ 本单**只加**两条新 claim: `mech_hinge_stack_truth_mm` = `25.30` (整机口径, 真源重算) / `mech_hinge_stack_demo_mm` = `5.00` (demo 口径) ★ | 同上 + 本单 T1 R3/R4 | 同 M-04 | ★**本单只加不改** (已加, 见 §5) ★ |
| **M-07** | `state/fragments/mech.yaml` claim `mech_hinge_links_count` = `0(demo)` | 0(demo) (11-02 demo 形态 ⇒ 跨铰链取消) | ★**拆 key**: `mech_hinge_links_count_demo` = **1** (board==HINGE ⇒ J_CHG) + `mech_hinge_links_count_product` = **待裁** (3 或 4) ⇒ 现状一个 key 装两种语义 = 合并器检不出的同域不一致 ★ | 网表 board 栏 | 同 M-01 | ★**main 排期** (本单只登记 need) ★ |
| **M-08** | `state/fragments/mech.yaml` claim `mech_hinge_radial_mm` = `4.40` | 4.40 | 同 M-06 处置 (demo 口径 = **3.35**; 整机 3 条 = **4.05**) | 同上 | 同 M-04 | ★**main 排期** ★ |
| **M-09** | `state/fragments/mech.yaml` claim `mech_hinge_stack_declared_mm` = `49.62` | 49.62 (上游 40p 规划口径) | 标注为已作废 + 现行声明版 (真源 pitch) = **25.30** | ISS-237 + 网表 | 同 M-04 | ★**main 排期** ★ |
| **M-10** | `MECH/USB_HINGE_STRUCTURE.md` L14 (C-1) 「跨铰链链路是 **4 条**, 不是上游预留的 3 条 … 声明口径合计 **94 pin**」 | 4 条 / 94 pin | ★**加作废标注** (demo 口径 = 1 条) + **补现行口径行** ★ | 老板 11-02 19:25 指示② + 网表 board 栏 | 无 | ★**本单已做** (只加不删) ★ |
| **M-11** | `MECH/USB_HINGE_STRUCTURE.md` **L90** 「`CONN_CAM` (40p)」 | 40p | ★**加作废标注** + **补现行行 = 31p / 0.3mm (Radxa Camera 4K · 座 HIROSE FH35C-31S-0.3SHW(50) · ISS-237 裁定)** ★ | 网表 L290 + `HW/STEP1_PARTS_SPEC.md` §0 (ISS-237) + 脚表 count=31 | 无 | ★**本单已做** ★ |
| **M-12** | `MECH/USB_HINGE_STRUCTURE.md` **L91** 「`CONN_LIGHT` (40p*) · 21 用到 / 9 必装」 | 40p* / 21 / 9 | ★**加作废标注** + **补现行行 = 22p / 0.5mm (Waveshare 2.8inch · ISS-237 裁定) · 脚表实测 22/22 全必装** ★ | 网表 L237 + 脚表 count(CONN_LIGHT)=22 + ISS-237 | 无 | ★**本单已做** ★ |
| **M-13** | `MECH/USB_HINGE_STRUCTURE.md` **L96** 「`CONN_LIGHT` 的 pin 数在网表值列**没有写**」 | 网表未声明 | ★**加作废标注** + **订正为「网表 L237 已写明 22p@0.5mm (HIROSE FH12-22S-0.5SH(55))」** ★ | 网表 L237 | 无 | ★**本单已做** ★ |
| **M-14** | `MECH/USB_HINGE_STRUCTURE.md` L310/L316/L320/L321/L333/L342/L343/L414/L430/L440 等仍写 16p/20p/26p/40p/12mm 板宽 / `mech_conn_light_pins` = 20p@0.5mm 的行 | 见 §2.2 留痕表 | ★**逐行核一遍: 该加作废标记的加, 该补现行口径的补** (★**只加不删, 一个实测原文不许改**★) ★ | ISS-237 + 网表/脚表 + 老板 11-02 19:25 指示② | 无 | ★**本单已做** ★ |
| **M-15** | `MECH/USB_HINGE_STRUCTURE.md` §9 镜像 claim 行 (`mech_hinge_stack_declared_mm` / `mech_hinge_stack_fixed_mm` / `mech_hinge_radial_mm` / `mech_hinge_links_count` / `mech_conn_cam_pins` / `mech_conn_light_pins`) | 31.50 / 25.00 / 4.40 / 4 / 16p@0.5mm / 20p@0.5mm | ★**加作废标注** + **补现行口径行** (demo 5.00/3.35/1 条; 整机 25.30/4.05) ⇒ ★**镜像必须与分片 claim 一致, 否则又是一处第二口径** ★ | 同 M-06/M-08 + 网表 | 同 M-04 | ★**本单已做 (补行) / 旧行处置归 main** ★ |
| **M-16** | `HW/STEP1_PARTS_SPEC.md` §0 (ISS-237 裁定块) | camera 31p/0.3mm · display 22p/0.5mm | ★**不动** —— 这是本单认定的**几何真源** ★ | 老板 11-11 19:31 裁决 + 脚表实测 | — | ★**不许动** ★ |
| **M-17** | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` | 现值 | ★**不动** (改了打断 MECH C21 三方对账与 SW R6 锚点) ★ | — | — | ★**不许动** ★ |
| **M-18** | `MECH/rebase_20261106.py` §2 (已算出 25.30 / 径向余 1.35) | 25.30 / 1.35 | ★**不动** —— 它是本单 T1-R3 / T2-N=3 的**交叉验证源** ★ | 网表现场解析 | — | ★**不许动** ★ |

### 4.1 M-04/M-05/M-06/M-08 的三档处置 (★一票交 main, 本单不拍★)

| 档 | 内容 | 代价 | main 的倾向 |
|---|---|---|---|
| **(a)** | 把 claim + G7/C9 改成「**demo 口径 = J_CHG 单链 (高度 5.00 / 径向 3.35)**」 | ★**丢 25.00 的留痕** (整机阶段可能仍有效) | — |
| **(b)** | 保留 25.00, **明确标注它 = 整机阶段旧架构口径 (4 条链), demo 不适用** | 25.00 继续被 G7 字面钉着, 但语义已标清 | ★**推荐** ★ |
| **(c)** | **两个都留** (demo 口径 + 整机口径分列) ⇒ **拆 claim key** (`mech_hinge_stack_demo_mm` / `mech_hinge_stack_fixed_mm`) | 需同时改 G7/C9 的判据文字 + 分片 key ⇒ H-1 重基线 | ★**推荐** ★ (main 倾向: (c), 因为 25.00 对【整机阶段】仍可能有效, 直接删会丢留痕) |

★**本单只交映射 + 推荐 (b)/(c), 不改 G7 判据, 不改任何 claim 的 value** ★

---

## 5 T4 —— 真值单一事实源声明 (★写死★)

> ★**跨铰链 FPC 几何真源 = `HW/STEP1_PARTS_SPEC.md` §0 裁定块 (ISS-237 · 2026-11-16) + `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 实测计数 + 网表 board 栏 (跨铰链判据)** ★
>
> ⇒ ★**结构侧任何占位数都必须能从它推出来** ★ —— 推不出来的数 = 硬编码的旧口径 = 本单要收掉的对象。
>
> **三件真源各自的职责**:
> 1. ★**针数与 pitch** = `HW/STEP1_PARTS_SPEC.md` §0 (ISS-237) ⇒ camera **31p/0.3mm** · display **22p/0.5mm**; 脚表 `count(CONN_CAM)=31` / `count(CONN_LIGHT)=22` 交叉验证
> 2. ★**哪些链路真跨铰链** = `HW/netlist_v1.csv` 的 **board 栏** ⇒ `board == "HINGE"` ⇒ demo = **J_CHG 1 条** (CONN_USB 网表 0 命中)
> 3. ★**架构裁定** = `PROJECT_TRACKER.md` §0 锁死表第 44 行 (老板 2026-11-02 19:25 指示②) + 第 43 行 (指示①) ⇒ demo 跨铰链取消 ⇒ ★**铰链区 FPC 几何账整块对 demo 板不适用** ★
>
> **作废依据 (统一一句)**: ★`【已作废 (依据 ISS-237 / 老板 2026-11-11 19:31 以实际接插件针数为准)】`★ —— 用于**针数/pitch/板宽**类旧数;
> ★`【已作废 (依据 老板 2026-11-02 19:25 指示② · demo 硬件形态: 跨铰链取消)】`★ —— 用于**铰链区堆叠/径向**类旧数 (架构变了, 不是数错了)。
>
> **纪律**: ★**删掉 = 失去「当初为什么这么算」的留痕** ★ ⇒ 本单对 `MECH/USB_HINGE_STRUCTURE.md` **只加不删**; 旧口径一律标「已作废」并**保留原字** ★

---

## 6 机器可读块 (★新门禁 `MECH/check_hinge_fpc_truth.py` 读这一块★)

<!-- MACHINE:BEGIN -->
```yaml
canonical_cross_hinge_links:      # board == HINGE 才算跨铰链 (demo 板)
  - ref: J_CHG
    pins: 10
    pitch_mm: 0.5
    board: HINGE
    netlist_line: 38
fpc_seats_all:                    # 网表里所有 FPC 座 (不论 board), 供"整机口径"复算
  - ref: CONN_CAM
    pins: 31
    pitch_mm: 0.3
    board: MAIN_PCB
    netlist_line: 290
  - ref: CONN_LIGHT
    pins: 22
    pitch_mm: 0.5
    board: MAIN_PCB
    netlist_line: 237
  - ref: J_CHG
    pins: 10
    pitch_mm: 0.5
    board: HINGE
    netlist_line: 38
computed:                         # 本单自己重算 (算式见 T1 / T2)
  demo_stack_mm: 5.0              # 10 × 0.5
  demo_radial_mm: 3.35            # 3.00 + 1 × (0.20+0.15)
  demo_stack_margin_mm: 33.0      # 38.00 − 5.00
  demo_radial_margin_mm: 2.05     # 5.40 − 3.35
  product_stack_mm: 25.3          # 31×0.3 + 22×0.5 + 10×0.5
  product_radial_mm: 4.05         # 3.00 + 3 × (0.20+0.15)
  product_stack_margin_mm: 12.7   # 38.00 − 25.30
  product_radial_margin_mm: 1.35  # 5.40 − 4.05
legacy:
  script_declared_stack_mm: 31.5  # 31×0.5 + 22×0.5 + 0×0.5 + 10×0.5 (camera 错按 0.5)
  script_recommended_stack_mm: 25.0  # 16×0.5 + 20×0.5 + 4×0.5 + 10×0.5
  script_declared_radial_mm: 4.4  # 3.00 + 4×0.35
  protected_script: MECH/hinge_usb_check.py
  protected_script_md5: 3425bc141508de8a35f34c7cf7b803e8
legacy_divergences:               # 每一处"已知不一致"必须登记 (否则门禁自己失效没人知道)
  - key: script_cross_links_vs_netlist_board
    detail: 脚本 CROSS_LINKS 4 条 (J_CHG/CONN_USB/CONN_CAM/CONN_LIGHT); 网表 board==HINGE 只有 J_CHG, CONN_USB 网表 0 命中
    owner: main
    action: M-01 (改受保护脚本 = H-1 重基线)
  - key: mech_hinge_stack_fixed_mm_25_00
    detail: claim 25.00 = 16+20+4+10 @0.5 的构成, 与真源 25.30 = 31@0.3+22@0.5+10@0.5 构成不同 (差 0.30mm) ⇒ 巧合
    owner: main
    action: M-04a/b/c 三档处置 (推荐 b 或 c)
  - key: n3_radial_3_75_vs_4_05
    detail: 任务书写 N=3 径向 3.75 / 余 1.65; 按同书公式 (3.00+N×0.35) 复算 = 4.05 / 1.35 (3.75 只在间隙只算 1 道时成立)
    owner: main
    action: 裁哪一版作数 (结论方向不变)
claims:
  mech_hinge_stack_fixed_mm: "25.00"   # 现状 (main 未裁; G7 + C9 字面钉着)
  mech_hinge_stack_truth_mm: "25.30"   # 本单新增 (整机口径, 真源重算)
  mech_hinge_stack_demo_mm: "5.00"     # 本单新增 (demo 口径, board==HINGE)
```
<!-- MACHINE:END -->

---

## 7 本单边界自证

| 项 | 自证 |
|---|---|
| 零外发 | 未发邮件 / 未联系供应商 / 未下采购单 / 未发任何问询函 |
| 实物 [实测] | ★**0 条** —— 本单所有数 = [推算], 输入是网表/脚表/裁定块的**实测值** ★ |
| 不碰 PCB | 未碰布线/布局/板框 (`HW/PCB/*` 只读) |
| 未改网表/脚表/BOM/板 | 11 个受保护 md5 实测逐字节未变 (见交卷单 B5) |
| 未改受保护脚本 | `hinge_usb_check.py` / `service_port_check.py` / `hw_cross_review_check.py` / `display_biosafety_v2_check.py` / `check_demo_struct_truth.py` / `cavity_recalc_check.py` / `DISPLAY_BIOSAFETY_CRITERIA_V2.md` 全部只读 |
| 未改 `PROJECT_TRACKER.md` §0 | 只读 (锁死表第 43/44 行作依据) |
| 未写别人的分片 | 只写 `state/fragments/mech.yaml` (经 `state/frag_write.py` 原子写) |
| 未自签 issue_log | `state/issue_log.yaml` 未动 (status 留给 main 落 verified) |
| 不替老板拍板 | ★未代拍 V-2 / V-3 / V-4; M-04 的三档处置只交 main ★ |
| 文档只加不删 | `MECH/USB_HINGE_STRUCTURE.md` 本单只加标注与新行, **旧字一个没删** (改前行数 506 ⇒ 改后只增不减) |
