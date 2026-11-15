# ★★整链重出 第 1 步 · 原理图侧落表作业包 v1 (★ISS-217★)★★

> ★**性质**: ★**这是【作业包】, 不是执行记录** ⇒ ★**本文件落笔时, 网表 / 脚表 / BOM / 板 / `.kicad_pro` / SPEC.json / CHARGE_BOARD_SPEC.md / 任何生成器 一个字节都没改** ⇒ ★**凡是"改成什么"的字样都只是"要改成什么", 不是"已经改好"**
> ★**日期**: ★**2026-11-16** · ★**执行**: 硬件总工 (hw-lead) · ★**单号**: ISS-217 · ★**owner**: hw-lead · ★**verify_by**: main
> ★**上游输入 (都已 verified, 本单直接用, 不重复定性, 不推翻)★**: ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** (★ISS-211 v1 = §1 四条 d1..d4 + ISS-214 v2 = §10 七组 d5..d11 + §11 附带发现 #1..#8 + §13 未决 V-1~V-8 + §14 边界自查★) · ★**`HW/check_netlist_selfconsistency.py`** (★现状守卫 154 锚点 · `--selftest` 16/16 · `--expect-resolved` 判据 R1~R11★) · ★**`HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md`** · ★**`state/RECHAIN_STEP1_LANDING_SPEC.md`** (★落表那一趟的既有作业包: C 项复位 P0 / E 项 NC 拆分 / D 项去耦待评审★)
> ★**门禁**: ★**`HW/check_netlist_selfconsistency.py`** (★本单已扩项: 作业包完整性 + 三方对齐 + R9 阈值 3.0mm + 新增反向用例★)
> ★**受保护 md5 (★交卷前后逐字节不变★)**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`
> ★**边界 (★违反一条即本单无效★)★**: ★**本单不许改网表 / 脚表 / BOM / 板 / `.kicad_pro` / `HW/SCHEMATIC_V1_SPEC.json` / `HW/CHARGE_BOARD_SPEC.md` / `HW/EMC_PRECHECK.md` / 任何 `state/gen_*.py` / `state/check_*.py` / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / `MECH/` 与 `SW/` 任何文件 / 别人的分片** ⇒ ★**本单只出作业包 + 扩门禁 + 登记分片** ★
> ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**本单未发任何邮件 / 询价 / 问询 / 采购; `state/outbox/` 未碰** ⇒ ★**本单实物 [实测] = 0 条** (板与屏不在本机) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本 / 本机文件实读", 不是"实物测过"**

---

## 0. ★★这一份是什么 + 落表那趟怎么用 (★SOP★★)

★★**一句话**: ★**规格页说的是"这条错在哪、真修法在哪"; 本作业包说的是"落表那趟具体改哪个文件的哪一行、改成什么字面值、改完跑哪条命令、怎么算翻面"** ⇒ ★**落表那趟照本文件逐条做, 不许把规格页当"参考"** ★

★★**★本作业包与既有作业包的关系 (★不许另起一套编号★)★★
| 文件 | 管什么 | 与本作业包的关系 |
|---|---|---|
| ★`state/RECHAIN_STEP1_LANDING_SPEC.md`★ | ★**落表那一趟的编排**: C 项 (复位 P0) / E 项 (NC 拆分) / D 项 (去耦, 等评审) / B 项 (位号改名, 归 ISS-205) / 14 步顺序闸 ★ | ★**本作业包不重出编排, 只补 "C/E/D/B 之外那 12 组网表/规格自相矛盾" 的逐条作业** ⇒ ★**本作业包的 ⑥ 栏跑的命令必须能插进那 14 步里** ★ |
| ★`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`★ | ★**为什么错 + 现状逐字 + 根因链 + 验收判据** ★ | ★**本作业包不重写它, 只做 "落表那趟照着做" 的执行层** ⇒ ★**④ 栏指回规格页的条号, 三方对齐由门禁机器查** ★ |
| ★`HW/check_netlist_selfconsistency.py`★ | ★**现状守卫 + 翻面判据 R1~R11** ★ | ★**本作业包 ⑦ 栏的 R# 就是它的判据 id** ★ |

★★**★"12 组"的计数口径 (★必须写清, 免得落表那趟以为漏了 1 组★)★★
| 口径 | 数 | 内容 |
|---|---|---|
| ★**ISS-211 (第 1 轮)** ★ | ★**4 条** ★ | ★**d1 / d2 / d3 / d4** (规格页 §1 第 (1)~(4) 条) ★ |
| ★**ISS-214 (第 2 轮)** ★ | ★**8 条** ★ | ★**规格页 §10 第 (1)(2)(3)(4)(5)(7)(8) 条 = d5..d11 (7 组) + 第 (6) 条 = ISS-211 已定的 4 条 (即 d1..d4 的汇总, 不另起锚点组) ★** |
| ★**⇒ 落表项实际组数** ★ | ★**11 组 (d1..d11)** ★ | ★**门禁 EXPECT 的锚点组也是 d1..d11 (154 条 = d1 17 + d2 19 + d3 14 + d4 14 + d5 16 + d6 14 + d7 17 + d8 8 + d9 7 + d10 15 + d11 13)★ ★ |
| ★**⇒ 加上规格页 §11 附带发现** ★ | ★**8 条 (#1..#8)** ★ | ★**§11 自己写明每条"已并进第 (N) 条" ⇒ 本作业包第 3 节逐条给出并注明吸收到哪一项 ★ |
| ★**⇒ 交付物总量** ★ | ★**11 组 + 8 附带 + 3 补差 + 6 待裁 = 28 条作业条目** ★ | ★**全部走机器门禁 (漏一条即红)★ ★ |

★★**★机器门禁 (★本单已扩项★)★★
| 命令 | 判什么 | 期望 rc |
|---|---|---|
| ★`python3 HW/check_netlist_selfconsistency.py`★ | ★**现状守卫 + 作业包完整性 + 三方对齐** (★作业包漏一条 / 改错一项 ⇒ 红★) ★ | ★**0** ★ |
| ★`python3 HW/check_netlist_selfconsistency.py --selftest`★ | ★**反向用例 (改坏必红) + 作业包完整性反向用例 + R9 阈值反向用例** ★ | ★**0** ★ |
| ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved`★ | ★**R1~R11 翻面判据 (★缺陷尚未落表 ⇒ 应当是红的★) ★ | ★**1** ★ |

---

## 1. ★★组号总表 (★作业包 ↔ 规格页 ↔ 门禁 R# 三方对齐表★) ★★

★**这张表是门禁机器查的对象 (★`HW/check_netlist_selfconsistency.py` 里的 `WP_MAP` 是它的唯一真源★)** ⇒ ★**作业包项号 ↔ 规格页条号 ↔ 门禁 R# 三者对不上 ⇒ 门禁红** ★

| 项号 | 规格页条号 | 标题 | 门禁翻面判据 | 被吸收到 | 本作业包位置 |
|---|---|---|---|---|---|
| ★**d1** ★ | ★§1 第 (1) 条★ | ★I2C_A 上拉: NET 行 4.7k/3.3V vs 器件行 2.2k/1.8V★ | ★**R1** ★ | — | §2.1 |
| ★**d2** ★ | ★§1 第 (2) 条★ | ★BAT_DET 分压链全 DNP, 而 SoC ADC 输入脚必装★ | ★**R2** ★ | — | §2.2 |
| ★**d3** ★ | ★§1 第 (3) 条★ | ★U_EN_SW 没有器件本体行 ⇒ BOM 把它登记成 NET 行★ | ★**R3** ★ | — | §2.3 |
| ★**d4** ★ | ★§1 第 (4) 条★ | ★USB D− 全程无 ESD, 而那颗器件自称"双通道"★ | ★**R4 + R9** ★ | — | §2.4 |
| ★**d5** ★ | ★§10 第 (1) 条★ | ★USB 串阻: 同一颗器件两个阻值 (90Ω vs 22Ω)★ | ★**R5** ★ | — | §2.5 |
| ★**d6** ★ | ★§10 第 (2) 条★ | ★CONN_LIGHT: P9 页正文 21p vs 网表 22p (+ 同页另两处也对不上)★ | ★**R6** ★ | — | §2.6 |
| ★**d7** ★ | ★§10 第 (3) 条★ | ★SARADC_VIN5 满量程 + BAT_DET 分压比★ | ★**R2 + R7** ★ | — | §2.7 |
| ★**d8** ★ | ★§10 第 (4) 条★ | ★BAT_DET 分压链漏电预算★ | ★**R8** ★ | — | §2.8 |
| ★**d9** ★ | ★§10 第 (5) 条★ | ★USB D− 的 ESD 方案 + 型号判据★ | ★**R4 + R9** ★ | — | §2.9 |
| ★**d10** ★ | ★§10 第 (7) 条★ | ★CHARGE_BOARD_SPEC §2.4/§3.4: ICHG/IIN 系数方向反了★ | ★**R10** ★ | — | §2.10 |
| ★**d11** ★ | ★§10 第 (8) 条★ | ★NET-LED / board 列: 真缺陷在 `C_VBUS_GND`★ | ★**R11** ★ | — | §2.11 |
| ★**#1** ★ | ★§11 附带发现 #1★ | ★`imp` 一个字段同时服务两种物理量★ | ★**R5** ★ | ★**d5** ★ | §3.1 |
| ★**#2** ★ | ★§11 附带发现 #2★ | ★`R_BAT_DET_1` note 的漏电流数与自己的阻值对不上★ | ★**R8** ★ | ★**d8** ★ | §3.2 |
| ★**#3** ★ | ★§11 附带发现 #3★ | ★ESD 位置判据 5mm vs 3.0mm 口径收口★ | ★**R9** ★ | ★**d9** ★ | §3.3 |
| ★**#4** ★ | ★§11 附带发现 #4★ | ★`J_CHG` 在网表与板文件里指两个不同的物理件★ | ★**R11** ★ | ★**d11** ★ | §3.4 |
| ★**#5** ★ | ★§11 附带发现 #5★ | ★充电链的 board 列是白名单驱动 ⇒ 白名单漏一颗 = 默认落 MAIN_PCB★ | ★**R11** ★ | ★**d11** ★ | §3.5 |
| ★**#6** ★ | ★§11 附带发现 #6★ | ★`C_VBUS_OUT` 串联在 DC 输入路径上 + §7 `C_VBUS_BULK` 对不上★ | ★**R11** ★ | ★**d11** ★ | §3.6 |
| ★**#7** ★ | ★§11 附带发现 #7★ | ★`R_CHG_LED` 的转述与实跑不一致★ | ★**R11** ★ | ★**d11** ★ | §3.7 |
| ★**#8** ★ | ★§11 附带发现 #8★ | ★`R_ILIM` note 里的 V1.7 残留 "470Ω" 与 value 的 390Ω 打架★ | ★**R10** ★ | ★**d10** ★ | §3.8 |
| ★**补差A** ★ | ★§11 附带发现 #1★ | ★`imp` 字段拆分方案 (串阻值 vs 差分阻抗)★ | ★**R5** ★ | ★**d5** ★ | §4.A |
| ★**补差B** ★ | ★§11 附带发现 #3★ | ★门禁 R9 翻面阈值 5.0 → 3.0 + 反向用例★ | ★**R9** ★ | ★**d9** ★ | §4.B |
| ★**补差C** ★ | ★§11 附带发现 #4 / #6★ | ★充电链 π 滤波真值拓扑 + `J_CHG` 位号消歧★ | ★**R11** ★ | ★**d11** ★ | §4.C |
| ★**待裁V-1** ★ | ★§13 V-1★ | ★USB 串阻: 22Ω 外部串阻 还是 0Ω 靠 SoM PHY 内部匹配★ | ★**R5** ★ | ★**d5** ★ | §5.1 |
| ★**待裁V-2** ★ | ★§13 V-2★ | ★ESD 方案二选一 + 型号 (★选型 = 老板级★)★ | ★**R4 + R9** ★ | ★**d9** ★ | §5.2 |
| ★**待裁V-3** ★ | ★§13 V-3★ | ★BAT_DET 分压比: 方案 A (2.0M+1.2M) 还是降级档 D (2.0M+1.0M)★ | ★**R2 + R7 + R8** ★ | ★**d7** ★ | §5.3 |
| ★**待裁V-4** ★ | ★§13 V-4★ | ★R_ILIM 档位: 解① 475~510Ω 还是 解② 390Ω + J_CHG 4 pin 并联★ | ★**R10** ★ | ★**d10** ★ | §5.4 |
| ★**待裁V-5** ★ | ★§13 V-5★ | ★堆叠账唯一口径 (★数字归 MECH + 项目总工★)★ | ★**R6** ★ | ★**d6** ★ | §5.5 |
| ★**待裁V-6** ★ | ★§13 V-6★ | ★ESD 位置判据 5mm → 3.0mm 口径收口 (★本单已落定, 写进作业包即可★)★ | ★**R9** ★ | ★**d9** ★ | §5.6 |

---

## 2. ★★主项 d1..d11 · 每组 8 栏 (★栏位一字不许少★) ★★

### ★★§2.1 · d1 · I2C_A 上拉: NET 行说 4.7k/3.3V, 器件行说 2.2k/1.8V★★

<!-- WPITEM:BEGIN id=d1 -->
① 项号: ★**d1** ★ (规格页 §1 第 (1) 条 · 锚点组 `d1_*` (17 条) · 翻面判据 **R1**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L167** `P2,I2C_A_SCL,J_SOM_P2 pin31,R_PU_I2CA_SCL,NET_I2C_A_SCL,上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF),NET,必装,[推算],,"方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF); 连接 SoC [待原厂] + sensor/NTC/桥接/充电IC; 测试点 TP_I2CA_SCL",B-01,MAIN_PCB,,` · ★**L168** `P2,I2C_A_SDA,J_SOM_P2 pin33,R_PU_I2CA_SDA,NET_I2C_A_SDA,上拉 4.7k 到 3.3V,NET,必装,[推算],,"方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V; 连接 同上; 测试点 TP_I2CA_SDA",B-02,MAIN_PCB,,` · ★**L169** `P2,VDD_1V8_IO,R_PU_I2CA_SCL,RAIL_VDD_1V8_IO,R_PU_I2CA_SCL,2.2k ±1%,R,必装,[推算],,"[VDD_1V8_IO] I2C_A 上拉 (★★11-04 ISS-153 订正: **实际 net = RAIL_VDD_1V8_IO (1.8V 域)**; ★**旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废**; …)",B-01,MAIN_PCB,,` · ★**L170** `P2,VDD_1V8_IO,R_PU_I2CA_SDA,RAIL_VDD_1V8_IO,R_PU_I2CA_SDA,2.2k ±1%,R,必装,…` · ★**L171** `P2,I2C_A_SCL,CONN_CAM pin24,NET_I2C_A_SCL,NET_I2C_A_SCL,"上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, ★camera FPC 标 I2C5 = 1.8V 域)",NET,必装,…` (★**camera 侧已经是对的, 是自洽对照行★**) · ★**表B `HW/netlist_v1_pins.csv`** ★**L367** `R_PU_I2CA_SCL.1` net=`I2C_A_SCL` · ★**L368** `R_PU_I2CA_SCL.2` net=`VDD_1V8_IO` · ★**L369/L370** 同款 (SDA) (★**脚表是对的★**) · ★**规格源头 `HW/SCHEMATIC_V1_SPEC.json`** `connections[20]` (id=`B-01`) `level="3.3V"` `imp="上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"` · `connections[21]` (id=`B-02`) `level="3.3V"` `imp="上拉 4.7k 到 3.3V"`
★**【ISS-220 第 1 批已落表 · 2026-11-16】** ★本栏『现状』已变 ⇒ 新逐字: 表A L167 = `上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)` / L168 = `上拉 2.2k 到 1.8V`; SPEC.json B-01/B-02 的 `level` = `1.8V` · `imp` = 上拉 2.2k/1.8V 口径 (★行号未变★) ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**同一 ref `R_PU_I2CA_SCL` 的两行字互相否定** (NET 行说 4.7k/3.3V, 器件行说 2.2k/1.8V 域) ⇒ ★**L169 自己的 note 已判 3.3V 那句"已作废", 而 L167/L168 还在逐字复述它 ⇒ 自我否定闭环; 且真按 L167 装 = 把 SoM 的 1.8V 脚 (P2_31/P2_33) 灌到 3.3V = 过压** ★
④ 真修法在哪个真源: ★**`HW/SCHEMATIC_V1_SPEC.json`** ★**`connections[]` 数组里 `id == "B-01"` (idx[20]) 与 `id == "B-02"` (idx[21]) 的 `level` 键与 `imp` 键** ⇒ ★**真源 = SPEC.json, 不是网表** (★`state/gen_netlist.py` 的 `conn_row()` (现 L770-781) 文档自写「value 默认取规格 imp」⇒ 改完 SPEC.json 重跑生成器, L167/L168 自动就对了 ⇒ **不需要碰 `state/gen_netlist.py`**★)
⑤ 改法 (逐字值): ★**`HW/SCHEMATIC_V1_SPEC.json`** → `connections[20]` (B-01): `level` 由 `"3.3V"` → ★`"1.8V"`★; `imp` 由 `"上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"` → ★`"上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"`★ ⇒ `connections[21]` (B-02): `level` 由 `"3.3V"` → ★`"1.8V"`★; `imp` 由 `"上拉 4.7k 到 3.3V"` → ★`"上拉 2.2k 到 1.8V"`★ ⇒ ★**不许手改 `HW/netlist_v1.csv` L167/L168** (★重跑生成器即得★) ⇒ ★**`HW/netlist_v1.csv` L171/L172 (camera 侧) 不动, 只需核一遍重跑后仍是 2.2k/1.8V** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R1 必须转绿★)
⑦ 翻面判据: ★**R1** ★ (★`--expect-resolved` 的 R1 段: 表A 不再有任何 value 含 "4.7k 到 3.3V" / "2.38µs"; SPEC.json B-01/B-02 的 `level` ≠ 3.3V 且 `imp` 含 "2.2k" 与 "1.8V"★)
⑧ 证据等级: ★**[实测]** ★表A L167/L168/L169/L170/L171 逐字 + 脚表 L367-L370 + `SCHEMATIC_V1_SPEC.json` connections[20]/[21] 的 `level`/`imp` (★2026-11-16 01:5x 本机实读★) · ★**[实测]** `HW/PCB/FET3572C_PIN_TABLE.csv` P2_31/P2_33 电压域列 = `1.8V` (★SoM 厂 IO 域表★) · ★**[实测]** `SW/SW_TIMING_REVIEW.md:130` 「旧结论翻转 … 2.2k 的实算是 186ns, 注记 2380ns 差 12.8 倍」 · ★**[推算]** t_r = 2.2k×100pF×0.847 ≈ 186ns · 灌流 (1.8−0.4)/2.2k = 0.64mA · ★**[0数据]** SoM I2C 脚 abs-max
<!-- WPITEM:END -->

### ★★§2.2 · d2 · BAT_DET 整条分压链全 DNP, 而 SoC 的 ADC 输入脚是必装★★

<!-- WPITEM:BEGIN id=d2 -->
① 项号: ★**d2** ★ (规格页 §1 第 (2) 条 · 锚点组 `d2_*` (19 条) · 翻面判据 **R2**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L181** `P2,BAT_DET,RAIL_BAT,R_BAT_DET_1,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 电池 BAT → ADC; 测试点 TP_BAT",B-08,MAIN_PCB,,` · ★**L182** `P2,BAT,RAIL_BAT,R_BAT_DET_1,R_BAT_DET_1,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_1] ★DNP: 同上 (电池电压分压上臂) | [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]",B-08,MAIN_PCB,,` · ★**L183** `P2,BAT_DET,R_BAT_DET_2,GND,R_BAT_DET_2,1M ±1%,R,DNP,[推算],,"[R_BAT_DET_2] ★DNP: 同上 (电池电压分压下臂) | [BAT_DET] 分压下臂 地端",B-08,MAIN_PCB,,` · ★**L184** `P2,BAT_DET,C_DET_BAT,R_BAT_DET_2,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) | [BAT_DET] ADC 滤波电容 (★V1.2: 电池在镜脚, 本地检测, 不跨铰链)",B-08,MAIN_PCB,,` · ★**L185** `P2,GND,C_DET_BAT,GND,C_DET_BAT,100nF ±10%,C,DNP,[推算],,"[C_DET_BAT] ★DNP: 同上 (电池 ADC 滤波) | [BAT_DET] ADC 滤波电容 地端",B-08,MAIN_PCB,,` · ★**L186** `P2,BAT_DET,J_SOM_P1 pin38,NET_BAT_DET,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,[推算],,"[BAT_DET] SoC ADC 输入节点 (跨板那一侧)",B-08,MAIN_PCB,,` · ★**表B `HW/netlist_v1_pins.csv`** ★**L307** `R_BAT_DET_1.1` dnp=`DNP` · ★**L308** `R_BAT_DET_1.2` net=`BAT` · ★**L309** `R_BAT_DET_2.1` dnp=`DNP` · ★**L310** `R_BAT_DET_2.2` net=`GND` · ★**L100/L101** `C_DET_BAT.1/.2` dnp=`DNP` · ★**L210** `J_SOM_P1.pin38` net=`BAT_DET` dnp=`必装` ⇒ ★**两张表一致地坏 (不是单边漂移)★** · ★**BOM `HW/BOM_v1.csv`** ★**L86** `R_BAT_DET_1,1,1M ±1%,R,DNP` · ★**L87** `R_BAT_DET_2,1,1M ±1%,R,DNP` · ★**L27** `C_DET_BAT,1,100nF ±10%,C,DNP` ⇒ ★**BOM 也说"不装" ⇒ 装配厂会照做 ⇒ 装出来就是悬空★**
③ 缺陷一句话: ★**必装的 SoM ADC 输入脚 (P1_38 = `SARADC_VIN5`) 只连着一颗都不装的器件 ⇒ 悬空输入** (★而且"★DNP: 同上"在网表里没有上文, 读者自己猜★) ⇒ ★**并且就算把 DNP 翻成必装, 照 1M+1M 贴上去仍然过压** (★4.2V × 1M/2M = 2.100V > AVDD18 max 1.98V★) ⇒ ★**所以"把 DNP 翻成必装"是不完整的, 必须同时定分压比 (见 d7 / V-3)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段的 4 条 `add()`** (★`R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` ×2 行: 改 `dnp` + `value` + `note`★) + ★**`state/gen_netlist_pins.py`** ★**同 4 行的 `dnp` + `J_SOM_P1.pin38` 那行的 `note`** ⇒ ★**★注意: d2 与 d1 不同 —— 分压比是写死在生成器里的, 不在 `HW/SCHEMATIC_V1_SPEC.json` 里 ⇒ 真源 = 生成器, 不是 SPEC.json★**
⑤ 改法 (逐字值): ★**`state/gen_netlist.py`** BAT_DET 段: `R_BAT_DET_1` 那条 `add()` 的 `dnp` 由 `"DNP"` → ★`"必装"`★、`value` 由 `"1M ±1%"` → ★`"2.0M ±1%"`★ (★按 V-3 裁决; 若裁 D 档则 `"2.0M ±1%"` 不变、下臂改 `"1.0M ±1%"`★) · `R_BAT_DET_2` 那条 `add()` 的 `dnp` → ★`"必装"`★、`value` 由 `"1M ±1%"` → ★`"1.2M ±1%"`★ · `C_DET_BAT` 两条 `add()` 的 `dnp` → ★`"必装"`★ (★两只一起改, 不许只改一半★) · 4 条的 `note` 里 `"★DNP: 同上"` → 写全的句子 (★写清: 为什么装 / 分压比怎么来的 / 漏电多少 / 上游是 4.2V 满充 / 脚是 SARADC_VIN5★) ⇒ ★**`state/gen_netlist_pins.py`**: 同 4 行 `dnp` 由 `"DNP"` → ★`"必装"`★; ★**`J_SOM_P1.pin38` 那行的 `note` 由 "[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100)…" (★它是 pin100 那行的复制品★) → 改写成 BAT_DET 的说明 (★例: "[BAT_DET] SoM SARADC_VIN5 输入 (P1_38, 1.8V 域); 上游 2.0M+1.2M 分压 @4.2V → 1.575V typ"★)** ⇒ ★**不许手改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv`** (★由重跑生成器自动来★) ⇒ ★**重跑后表A L181/L186 的 value 由 `"1M+1M 分压 + 100nF"` → `"2.0M+1.2M 分压 + 100nF"` (★自动★)**
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R2 必须转绿★)
⑦ 翻面判据: ★**R2** ★ (★`--expect-resolved` 的 R2 段: 表A/表B 里 `R_BAT_DET_1`/`R_BAT_DET_2`/`C_DET_BAT` 全部 ≠ DNP; 且分压后 @4.2V ≤ 1.8V★) ⇒ ★**配合门禁里的【分压比利用率】与【漏电自洽】两条判据一起看 (★那两条挂在 d7 / d8 两组上, 本组的 ⑦ 只认 R2★)★**
⑧ 证据等级: ★**[实测]** 表A L181-L186 逐字 + 表B L100/L101/L307/L308/L309/L310/L210 逐字 + BOM L27/L86/L87 + `HW/PCB/FET3572C_PIN_TABLE.csv` 第 39 行 `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` · ★**[实测]** `HW/INTERFACE_TABLE.md` C-03 电池 4.2V 满 / 3.0V 截止 · ★**[推算]** "1:1 分压 2.100V > 1.8V" 这步依赖 abs-max 判据, 但 abs-max 本身 [0数据] ⇒ 见 d7 的官方兜底 · ★**[0数据]** SoM SAR-ADC 的满量程 / 源阻抗 / abs-max
<!-- WPITEM:END -->

### ★★§2.3 · d3 · U_EN_SW 没有器件本体行 ⇒ BOM 里这颗 IC 被登记成 NET 行★★

<!-- WPITEM:BEGIN id=d3 -->
① 项号: ★**d3** ★ (规格页 §1 第 (3) 条 · 锚点组 `d3_*` (14 条) · 翻面判据 **R3**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv` 里 `ref == U_EN_SW` 的行只有 4 行, `type` 全是 `NET`** ★**L441** `P1,CARRIER_BOARD_EN,U_EN_SW pin2,CARRIER_BOARD_EN,U_EN_SW,EN 输入 (高=放行底板),NET,必装,[官方],,"[U_EN_SW] EN ← CARRIER_BOARD_EN ⇒ 主板各路只在 SoM 就绪后上电",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` · ★**L442** `P1,RAIL_DEMO_5V,U_EN_SW pin1,RAIL_DEMO_5V,U_EN_SW,5V 输入,NET,必装,[官方],…` · ★**L443** `P1,RAIL_BOARD_5V,U_EN_SW pin3,RAIL_BOARD_5V,U_EN_SW,5V 输出 (受 CARRIER_BOARD_EN 门控),NET,必装,[官方],…` · ★**L444** `P1,GND,U_EN_SW pin4,GND,U_EN_SW,GND,NET,必装,[官方],…` · ★**表B `HW/netlist_v1_pins.csv`** ★**L531/L532/L533/L534** = `U_EN_SW.pin1..pin4`, `type` 也全是 `NET` ⇒ ★**两张表都缺本体行★** · ★**对照 (★同类器件的正确写法★)** 表A ★**L50** `P1,SYS,U_PWR_SW pin3,RAIL_SYS,U_PWR_SW,"[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",IC,必装,[推算],…` ⇒ ★**本体行挂在其中一脚上, 其余脚是 NET 行★** · ★**BOM `HW/BOM_v1.csv` L208** `U_EN_SW,1,EN 输入 (高=放行底板),NET,必装,镜脚主 PCB,P1,[官方],,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA,待定,待定,待分类,` ⇒ ★**type 栏是 `NET` / `procurement` 栏是 `待分类`★** · ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb`** 封装 `U_EN_SW`: pads=**4**, `Value` 属性 = ★`EN 输入 (高=放行底板)`★, pad→net = pad1=`RAIL_DEMO_5V` / pad2=`CARRIER_BOARD_EN` / pad3=`RAIL_BOARD_5V` / pad4=`GND` ⇒ ★**电气本身是对的, 是账错了★**
③ 缺陷一句话: ★**一颗 4 脚 IC 在表A / 表B / BOM / 板文件里全都被登记成 NET 行** ⇒ ★**采购台账漏件 (`procurement=待分类`) + 板封装 `Value` 属性是一句脚功能串 (投产包/盖印里板厂看得到) + 任何按 type 分组的工具 (备料台账 / SMT 上料单) 会把它当"不上料的虚拟件"★** ⇒ ★**⇒ 改网表不够, 板文件也要同趟改 (⇒ 这是"要改板"的一条)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**U_EN_SW 那 4 条 `add()` (★现 L1474-L1483★) 附近补一条 `type="IC"` 的器件本体行** + ★**`state/gen_netlist_pins.py`** ★**让脚表里 U_EN_SW 也有一条 `type=IC` 的本体行** + ★**板文件 `Value` 由 `state/gen_pcb_components.py:156` (`fp.SetValue(per_ref[ref][0][2][:40] …)`) 在重出板时自动刷** ⇒ ★**★排序坑: `gen_pcb_components.py:156` 取的是"该 ref 在网表里的第一行" ⇒ 本体行必须排在 U_EN_SW 那 4 条 NET 行【之前】, 否则板的 Value 还是脚功能串★★** ⇒ ★**BOM 不用改 `state/gen_bom.py` (`_pick_value()` 的第①档本体行众数一旦有本体行就自动取到器件身份描述)★**
⑤ 改法 (逐字值): ★**`state/gen_netlist.py`** ★**在 U_EN_SW 那 4 条 `add()` 之前**插一条 (★写法照抄 `U_PWR_SW` 的本体行★):
```
add("P1", "RAIL_DEMO_5V", "U_EN_SW", "U_EN_SW", "U_EN_SW",
    "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断, 使能脚高有效放行)",
    "IC", "必装", "[推算]", "",
    "[U_EN_SW] ★器件本体行 (★本体行必须排在下面 4 条 NET 行之前 ⇒ 板封装 Value 才取到器件身份描述★); 型号等 ISS-172 落",
    "A-24")
```
★**`state/gen_netlist_pins.py`** ★**照 `U_PWR_SW.pin3` (type=`IC`) 的逻辑, 让 U_EN_SW 也有一条 type=`IC` 的脚行★** ⇒ ★**落表后必须核板文件 `U_EN_SW` 封装的 `Value` 属性 == 上面那个器件身份描述 (★门禁 R3 已把这一项做成硬判据★)** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/gen_pcb_components.py` ★ → ★`python3 state/gen_pcb_netlist_board.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 state/check_kicad_net.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R3 必须转绿★)
⑦ 翻面判据: ★**R3** ★ (★`--expect-resolved` 的 R3 段: 表A 与表B 里 `U_EN_SW` 各有 ≥1 条 `type != NET` 的器件本体行; BOM 里 `U_EN_SW` 的 type ≠ NET; 板封装 `U_EN_SW` 的 `Value` 不再是脚级功能串★)
⑧ 证据等级: ★**[实测]** 表A L441-L444 + L50 + 表B L531-L534 + BOM L208 逐字 + 板封装 pads/value/pad→net · ★**[实测]** `state/gen_bom.py:143` `_pick_value()` 文档 + `state/gen_pcb_components.py:156` 代码 · ★**[官方]** U_EN_SW 的电路功能来源 = Forlinx 载板指引 (F13) (★网表 evidence 列已标 [官方]★) · ★**[0数据]** 具体型号 (★ISS-172, 老板级★)
<!-- WPITEM:END -->

### ★★§2.4 · d4 · USB D− 全程没有 ESD, 而那颗器件自称"双通道"★★

<!-- WPITEM:BEGIN id=d4 -->
① 项号: ★**d4** ★ (规格页 §1 第 (4) 条 · 锚点组 `d4_*` (14 条) · 翻面判据 **R4 + R9**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L417** `P1,USB_D_P_SRC,D_ESD_USB_D,USB_D_P_SRC,D_ESD_USB_D,ESD 阵列 [待选型] (USB 2.0 双通道),D,必装,[推算],,"[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**",A-24,MAIN_PCB,,` · ★**L418** `P1,GND,D_ESD_USB_D,GND,D_ESD_USB_D,ESD 阵列 [待选型],D,必装,[推算],,[D_ESD_USB_D] ESD 地端,A-24,MAIN_PCB,,` · ★**L431** `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,R_SER_USB_D_P,22Ω ±1%,R,必装,…` · ★**L432** `P1,NET_USB_D_N_TYPEC,R_SER_USB_D_N,J_USB_C A7+B7,R_SER_USB_D_N,22Ω ±1%,R,必装,…` · ★**板文件实读**: 封装 `D_ESD_USB_D` pads=**2**, `Value` = ★`ESD 阵列 [待选型] (USB 2.0 双通道)`★, pad1→`USB_D_P_SRC` / pad2→`GND`, 原点 (94.95, 21.80) · `J_USB_C` 原点 (140.00, 5.25) ⇒ ★**距离 47.99 mm**★ · 板上 ESD 位号共 4 个 (`D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_LIGHT` / `D_ESD_USB_D`) ⇒ ★**挂 `USB_D_N_SRC` 或 `NET_USB_D_N_TYPEC` 的 = 0 个★** · ★**BOM `HW/BOM_v1.csv` L62** `D_ESD_USB_D,1,ESD 阵列 [待选型] (USB 2.0 双通道),D,必装,…,★板文件封装: 2 焊盘 (…★`
③ 缺陷一句话: ★**Type-C 入口只护了差分的一边 (D− 裸奔), 器件自称"双通道"而封装只有 2 焊盘, 而且这只 ESD 挂在串阻的【SoM 侧】(pad1=`USB_D_P_SRC`) 而真正贴连接器的是 `NET_USB_D_P_TYPEC` ⇒ note 自引的"紧贴 J_USB_C"被板文件实测证伪 (47.99 mm)★** ⇒ ★**这是 4 条里唯一的"用了就可能坏"的条目 (Type-C 插拔是日常动作)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**USB ESD 段的两条 `add()` (★现 L1384-L1388★: `D_ESD_USB_D` 的信号端 + 地端)** + ★**`state/gen_netlist_pins.py`** (★脚表 2 脚 → 3 脚★) + ★**板 (封装 + 位置)**: ★**`state/gen_pcb_components.py`** (★封装/属性★) + ★**`state/gen_pcb_routing.py`** / ★**`state/gen_pcb_netlist_board.py`** (★位置与重跑布线★) ⇒ ★**★型号 / 封装选型 = 老板级 (V-2)★ ⇒ 本单只出规格, 不许自己动板★**
⑤ 改法 (逐字值) — ★**走方案① (3 脚双通道阵列, 规格页 §10 第 (5) 条的推荐)★**:
★**`state/gen_netlist.py`** USB ESD 段: `D_ESD_USB_D` 从 2 脚改成 3 脚 —— 信号端那条 `add()` 的 `net` 由 `"USB_D_P_SRC"` → ★`"NET_USB_D_P_TYPEC"`★、`node2` 由 `"USB_D_P_SRC"` → ★`"NET_USB_D_P_TYPEC"`★; ★**新增一条 `add()`**: `net="NET_USB_D_N_TYPEC"`, `node1="D_ESD_USB_D"`, `node2="NET_USB_D_N_TYPEC"`, `ref="D_ESD_USB_D"`, `value` 同下, `type="D"`, `dnp="必装"`; ★**新增一条地端 `add()`**: `net="GND"`, `node1="D_ESD_USB_D"`, `node2="GND"`, `ref="D_ESD_USB_D"`, `value="ESD 阵列 [待选型] (USB 2.0 双通道)"`, `type="D"`, `dnp="必装"` ⇒ 3 条 `add()` 对应 3 个焊盘 (pin1=D+ / pin2=D− / pin3=GND) · ★**`value` 由 `"ESD 阵列 [待选型] (USB 2.0 双通道)"` → ★`"ESD 阵列 (USB 2.0 双通道, D+/D− 共用一颗, ≤1pF/线, IEC 61000-4-2 level 4)"`★ (★不许留"名不副实"的字样★) · ★**`note` 里 "紧贴 J_USB_C" 只有在 3j 真做到时才留 ⇒ 落表后必须复量并写成实测值 (★目标 ≤3.0mm★)** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/gen_pcb_components.py` ★ → ★`python3 state/gen_pcb_routing.py` ★ → ★`python3 state/gen_pcb_netlist_board.py` ★ → ★`python3 state/check_kicad_net.py` ★ → ★`python3 state/check_pcb_drc.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R4 + R9 必须转绿★)
⑦ 翻面判据: ★**R4 + R9** ★ (★R4: 板上挂 `USB_D_N_SRC` **或** `NET_USB_D_N_TYPEC` 的 ESD 位号数 ≥ 1, 且 `D_ESD_USB_D` 焊盘数 = 3; R9: `D_ESD_USB_D` → `J_USB_C` 板面距离 **≤ 3.0 mm** (★阈值已从 5.0 收紧到 3.0, 见补差 B★)★)
⑧ 证据等级: ★**[实测]** 表A L417/L418/L431/L432 + BOM L62 逐字 + 板封装 pads/value/pad→net + 板面坐标与距离 **47.99 mm** + 4 个 ESD 位号逐个查网 · ★**[官方]** "ESD 紧贴接口" 这条规矩 = Forlinx 载板指引 (★L417 note 自引★) · ★**[0数据]** 具体 ESD 型号 / 结电容 / 钳位电压 / IEC 等级 (★老板级选型 + 零外发★)
<!-- WPITEM:END -->

### ★★§2.5 · d5 · USB 串阻: 同一颗器件两个阻值 (90Ω vs 22Ω)★★

<!-- WPITEM:BEGIN id=d5 -->
① 项号: ★**d5** ★ (规格页 §10 第 (1) 条 · 锚点组 `d5_*` (16 条) · 翻面判据 **R5**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L291** `P6,USB_D_P_SRC,J_SOM_P1 pin92,R_SER_USB_D_P,NET_USB_D_P_SRC,90Ω ±10% (与 MIPI 不同模板!),NET,必装,[待原厂],TBD-10,方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10% (与 MIPI 不同模板!); 连接 Type-C → 主 PCB (跨铰链则经 CONN_USB); 测试点 TP_USB_D+,B-21,MAIN_PCB,,` · ★**L292** `P6,USB_D_N_SRC,J_SOM_P1 pin94,R_SER_USB_D_N,NET_USB_D_N_SRC,90Ω ±10%,NET,必装,[待原厂],TBD-10,…,B-22,MAIN_PCB,,` · ★**L431** `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,R_SER_USB_D_P,22Ω ±1%,R,必装,[推算],…` · ★**L432** `P1,NET_USB_D_N_TYPEC,R_SER_USB_D_N,J_USB_C A7+B7,R_SER_USB_D_N,22Ω ±1%,R,必装,[推算],…` · ★**规格源头 `HW/SCHEMATIC_V1_SPEC.json`** `connections[40]` (id=`B-21`) `signal="USB_D+"` `imp="90Ω ±10% (与 MIPI 不同模板!)"` · `connections[41]` (id=`B-22`) `signal="USB_D-"` `imp="90Ω ±10%"` · ★**项目自己已经把"90Ω 是什么"写清楚了**: `HW/EMC_PRECHECK.md:211` 逐字 `4. **USB 2.0 差分**: D+/D- 90 Ω 差分, 480 Mbps, 与 MIPI 的 100 Ω **不是同一套阻抗模板** (混用会导致其中一路失配)。` ⇒ ★**⇒ "90Ω" 是【差分线阻抗】, 不是【串联电阻值】; L291 的 note 自称"与 MIPI 不同模板!" = 写的人自己知道模板串了, 但没改★**
③ 缺陷一句话: ★**两个物理量被塞进同一个字段 (`imp`)** —— NET 行塞的是【差分线阻抗 90Ω】, 器件行 (`L431`/`L432`) 塞的是【串联电阻值 22Ω】, 而两者指向同一颗 `R_SER_USB_D_P` ⇒ ★**谁读到哪一行结论就相反; 且 90Ω 串在 90Ω 线上物理错误 (源端看到 180Ω ⇒ 摆幅只剩 ~1/2 ⇒ 眼图不合规)★**
④ 真修法在哪个真源: ★**`HW/SCHEMATIC_V1_SPEC.json`** ★**`connections[40]` (B-21) 与 `connections[41]` (B-22) 的 `imp` 键** ⇒ ★**根因 = SPEC.json 的 `imp` 一个字段同时服务两种物理量 ⇒ 真修法是【分字段】, 不是改一个数 (★完整字段拆分方案见 §4.A 补差A★)** ⇒ ★**`state/gen_netlist.py` 的 `conn_row()` (现 L770-781) 会自动把新的 `imp` 落到 NET 行 ⇒ **不需要碰生成器 (除非同时落补差 A 的字段拆分)****
⑤ 改法 (逐字值): ★**`HW/SCHEMATIC_V1_SPEC.json`** → `connections[40]` (B-21): `imp` 由 `"90Ω ±10% (与 MIPI 不同模板!)"` → ★`"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)"`★ ⇒ `connections[41]` (B-22): `imp` 由 `"90Ω ±10%"` → ★`"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)"`★ ⇒ 两条的 `level` `"3.3V [待原厂]"` ★**保留** (★USB 差分不是电平问题; [待原厂] 标记随 SoM 手册关掉, 见 V-1★) ⇒ ★**不许手改 `HW/netlist_v1.csv` L291/L292** (★重跑生成器即得★) ⇒ ★**L431/L432 的器件行 value (`22Ω ±1%`) 不动** (★两行口径一致后, 网表里不再有任何 value 含 `90Ω ±10%`★)
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R5 必须转绿★)
⑦ 翻面判据: ★**R5** ★ (★`--expect-resolved` 的 R5 段: 表A 里 `ref == NET_USB_D_P_SRC` / `NET_USB_D_N_SRC` 的 value 不含 "90Ω" 且含 "22Ω"; SPEC.json B-21/B-22 的 `imp` 不含 "90Ω" 且含 "22Ω"★)
⑧ 证据等级: ★**[实测]** 表A L291/L292/L431/L432 逐字 + `SCHEMATIC_V1_SPEC.json` connections[40]/[41] 全文 + `EMC_PRECHECK.md:211` 逐字 + `gen_netlist.py:770-774` 逐字 · ★**[官网]** ON Semi **AND8074/D** (「The USB twisted pair cable has a characteristic impedance of (Zo) of **90 Ω ±15%**.」/「the USB 1.1 specification requires a series resistor with value between **28 Ω and 44 Ω**」/「most of the industrial drivers require a series resistor of **22 Ω or 30 Ω**」) · onsemi **STF202-22T1G** datasheet (Rev 11, 2025-03) 内置串阻 `RS = 20 / **22** / 24 Ω` (min/nom/max) · ★**[推算]** "90Ω 串阻 ⇒ 摆幅减半" · ★**[0数据]** SoM (Forlinx) USB PHY 的驱动阻抗 / 外部串阻是否必需 (★V-1★)
<!-- WPITEM:END -->

### ★★§2.6 · d6 · CONN_LIGHT: P9 页正文 21p vs 网表 22p (+ 同页另两处也对不上)★★

<!-- WPITEM:BEGIN id=d6 -->
① 项号: ★**d6** ★ (规格页 §10 第 (2) 条 · 锚点组 `d6_*` (14 条) · 翻面判据 **R6**)
② 现状逐字 + 行号: ★**`state/gen_schematic_pages.py:147`** (★P9 页正文, ★手写字符串, 不是从网表生成的★) 逐字:
`  4. \`CONN_LIGHT\` (**1×21p@0.5mm**) — pin1/2 = DSI CK · 3/4 = D0 · 5/6 = D1 · 7-10 = D2/D3 预留 (DNP) · 11-16 = 桥接位 (方案B) · 17/18 = DDC · 19 = 3V3 · 20 = 1V8 · 21 = 5V 预留 (待 JBD)`
★**同页另两处通道 + 堆叠账逐字**:
`  2. \`CONN_USB\` (**4p@0.5mm**) — USB 2.0 差分 (**烧录/调试口唯一通路**) + 独立回流地 + 1 预留`
`  3. \`CONN_CAM\` (**18p@0.5mm**) — pin1/2 = CSI CK · … · **pin18 = 独立回流地**`
`  ★**铰链区高度预算 (V1.3 按结构总工 F-3 收敛后)**: 4 条链路触点区**统一 0.5mm pitch** → 堆叠 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm** ✅ (收敛前按 40p 声明是 54.7mm, **放不下**)。`
★**现行网表实测**: 表A ★**L237** `value = ★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)★`, `board = MAIN_PCB` · 表A ★**L290** `value = ★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50); 针位见 HW/PCB/FPC_PIN_TABLES.md)★` · 脚表 `count(ref==CONN_LIGHT) == 22` / `count(ref==CONN_CAM) == 31` · 表A `count(ref==CONN_USB) == 0` (★`state/gen_netlist.py:117` 注释: `HINGE_REFS = {"J_CHG"} # ★2026-11-04 19:5x: CONN_USB 跨铰链 USB 座已删★) · BOM L5 value 含 `22p@0.5mm` / footprint 含 `FH12-22S-0.5SH` · ★**网表里 board == `HINGE` 的连接器只有 `J_CHG` 一个 ⇒ "4 组跨铰链通道"不成立★**
★**【ISS-220 第 1 批已落表 · 2026-11-16】** ★本栏『现状』已变 ⇒ 新逐字: P9 页 `CONN_LIGHT` = `1×22p@0.5mm` / `CONN_CAM` = `31p@0.3mm` (板内 FPC 座) / `CONN_USB` 已删 / 跨铰链通道 = **1 组 (J_CHG) + 3 条板内 FPC** / 堆叠账不再自带第二个数 (只留锁死分母 `38.00mm` + 引用结构侧口径) (★行号未变★) ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**P9 页正文是手写字符串, 里面的 pin 数 / pitch / 通道数 / 堆叠账三个输入全过期** ⇒ ★**⇒ 堆叠账 26.5mm 与分母 37.0mm 两个数都不能再用 (37.0 是已作废的叠放模型算式; 现行锁死腔体净高 = 38.00mm)⇒ 而且 P9 页的"4 组跨铰链通道"与网表 board 列矛盾 (实际 1 组) ⇒ 结构余量算的是错的★**
④ 真修法在哪个真源: ★**`state/gen_schematic_pages.py`** ★**`PAGES` 字典里 `"P9"` 那一条的手写字符串 (★现 L143-L147 那一大段★)** ⇒ ★**★改它 = 改源 (合法); 手改 P9 页 svg = 改在产物上 (会被下次重跑覆盖, 非法)⇒ 这是唯一合法路★** ⇒ ★**★堆叠数字本身归 MECH + 项目总工 (V-5) ⇒ 本单不许自带第二个堆叠数★** ⇒ ★**pin 数的真值源 = `HW/netlist_v1.csv` L237 (器件行) + `HW/netlist_v1_pins.csv` (22 脚行) + `HW/BOM_v1.csv` L5 (三处互证) ⇒ 官方封装 = **Hirose FH12-22S-0.5SH(55)** ⇒ **22p 是真值**★**
⑤ 改法 (逐字值): ★**`state/gen_schematic_pages.py` 的 `PAGES["P9"]` 正文里**:
- `4. \`CONN_LIGHT\` (**1×21p@0.5mm**)` → ★`4. \`CONN_LIGHT\` (**1×22p@0.5mm**)`★; 该条 pin 说明改成 22 脚 (★按脚表: pin21 = GND / pin22 = GND, **不是"5V 预留"**★)
- `3. \`CONN_CAM\` (**18p@0.5mm**)` → ★`3. \`CONN_CAM\` (**31p@0.3mm**)`★ (★并把它的 "板内 FPC 座" 身份写明, 因为它不是跨铰链链路★)
- `2. \`CONN_USB\` (**4p@0.5mm**)` 那一条 → ★删掉 (或改成 "已删, 跨铰链 USB 座于 2026-11-04 取消")★ ★
- `⇒ **4 组跨铰链通道**:` → ★`⇒ **1 组跨铰链 (J_CHG) + 3 条板内 FPC**:`★ ★
- `堆叠 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm**` → ★按 V-5 裁决的唯一口径重写 (★本单不给数; 唯一允许出现的分母是 **38.00mm**, 口径 = FPC 带宽 35.50mm ⇒ **宁可不写数, 也不写第二个错数**★)★ ★
- ★**不许手改 P9 页 svg** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_schematic_pages.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 state/check_sch_loadable.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R6 必须转绿★)
⑦ 翻面判据: ★**R6** ★ (★`--expect-resolved` 的 R6 段: P9 页正文不再含 `1×21p@0.5mm` / `CONN_CAM` `(**18p@0.5mm**)` / `CONN_USB` `(**4p@0.5mm**)` / `(10+4+18+21)×0.5`; 且含 `1×22p@0.5mm`; 且脚表 `count(ref==CONN_LIGHT) == 22` 保持★)
⑧ 证据等级: ★**[实测]** `gen_schematic_pages.py:147` 逐字 + 网表 L237/L290 逐字 + 脚表 22/31 行计数 + BOM L5 + `gen_netlist.py:117` 注释逐字 + `state/gen_netlist.py` 里 board==HINGE 的连接器只有 J_CHG (本机脚本实跑) · ★**[实测]** `MECH/cross_review_check.py:64` 逐字「★**37.0 是已作废的叠放模型**算式 (22+12+3) —— 现行是**锁死的腔体净高 38.00**」 · ★**[官方]** 官方 RPi CM5IO / Pi5 DISPLAY 座封装 = Hirose **FH12-22S-0.5SH(55)** (★网表/BOM 自引封装抄用★) · ★**[推算]** 26.5 / 27.00 / 35.50 三数各自对应的物理模型 · ★**[0数据]** 铰链段实际堆叠 (要等结构实测/印包)
<!-- WPITEM:END -->

### ★★§2.7 · d7 · SARADC_VIN5 满量程 + BAT_DET 分压比 (ISS-211 U-2)★★

<!-- WPITEM:BEGIN id=d7 -->
① 项号: ★**d7** ★ (规格页 §10 第 (3) 条 · 锚点组 `d7_*` (17 条) · 翻面判据 **R2 + R7**)
② 现状逐字 + 行号: ★**[官网] `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` §3.10 Table 3-16 (由项目库内官方 PDF 抽取) 第 2864 行逐字**: `Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V` (★官方表头把 "Analog" 拼成 "Anglog", 逐字抄录, 不许"顺手改对"★) · 第 2863 行 `Resolution                                                                 NA           12         NA       Bit` · 第 2454 行 `SARADC Analog Power(1.8V)               SARADC_AVDD1V8             1.62    1.8     1.98     V` ⇒ ★**AVDD18 = 1.8V 标称 / 1.62~1.98V 范围**★ · ★**[实测] `HW/PCB/FET3572C_PIN_TABLE.csv` 第 39 行** `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` ⇒ ★**P1_38 = SARADC_VIN5, 1.8V 域**★ · ★**表A `HW/netlist_v1.csv`** ★**L181** `value = 1M+1M 分压 + 100nF`, note 含 ★`电平 0-3.3V (分压)`★ · ★**L182** `value = 1M ±1%` · ★**L183** `value = 1M ±1%` · ★**L184** `value = 100nF ±10%` · ★**L186** `value = 1M+1M 分压 + 100nF`, `node1 = J_SOM_P1 pin38`, `dnp = 必装`
③ 缺陷一句话: ★**1:1 分压 @BAT_max=4.2V ⇒ 中点 2.100V > AVDD18 max 1.98V (超 0.120V / 6.1%) ⇒ 芯片级就判死 (不再依赖 SoM 的 abs-max)** ⇒ ★**且 L181 的 note 自称 "电平 0-3.3V (分压)" 与 P1_38 的 1.8V 域直接矛盾 (与 d1 同型的自我打架)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段的 `add()` 的 `value`** (★分压比写死在生成器, **不在 `HW/SCHEMATIC_V1_SPEC.json` 里**★) ⇒ ★**判据真源 (★两条官方/权威依据★)**: ★**`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`** (★RK3572 官方 datasheet: 12-bit / AVSS18~AVDD18 / AVDD18 max 1.98V★) + ★**`HW/PCB/FET3572C_PIN_TABLE.csv`** (★SoM 厂 IO 域表: P1_38 = 1.8V 域★) ⇒ ★**★根因 = "从来没人定过分压比", 因为定分压比的判据需要 SoM ADC 参数, 而项目库当时没有 ⇒ 缺陷一直"合法地"存在★**
⑤ 改法 (逐字值): ★**`state/gen_netlist.py`** BAT_DET 段: `R_BAT_DET_1` 那条 `add()` 的 `value` 由 `"1M ±1%"` → ★`"2.0M ±1%"`★; `R_BAT_DET_2` 那条 `add()` 的 `value` 由 `"1M ±1%"` → ★`"1.2M ±1%"`★ (★按 V-3 裁决; 若裁降级档 D 则下臂 → `"1.0M ±1%"`★) ⇒ ★**`state/gen_netlist.py`** 里 `NET_BAT_DET` 那条 NET 行 `add()` 的 `value` 由 `"1M+1M 分压 + 100nF"` → ★`"2.0M+1.2M 分压 + 100nF"`★ (★D 档则 `"2.0M+1.0M 分压 + 100nF"`★) ⇒ ★**该 NET 行 `note` 里 `"电平 0-3.3V (分压)"` → ★`"电平 0-1.8V (分压, 进 1.8V 域 SARADC_VIN5)"`★** ⇒ ★**分压比三条判据 (★缺一条不许落★): ① @4.2V (含 ±1% 容差) 中点 ≤ 1.8V 且 ≤ 1.98V ⇒ 上/下臂比 ≥ 2.33:1 ② @4.2V 中点 ≥ 1.2V (≥66.7% 满量程) ⇒ 上/下臂比 ≤ 3.5:1 ③ 源阻抗不是阻塞项 (有 100nF 当电荷蓄水池)** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R2 + R7 必须转绿★)
⑦ 翻面判据: ★**R2 + R7** ★ (★R2: 分压后 @4.2V ≤ 1.8V; R7: 分压后 @4.2V ∈ [1.2V, 1.8V] —— 既进得了 1.8V 域 ADC, 又不浪费 12bit★)
⑧ 证据等级: ★**[官网]** RK3572 Datasheet Rev 1.1 §3.10 **Table 3-16** (Resolution 12 Bit / Anglog Input Range AVSS18~AVDD18) + 电气总表 `SARADC_AVDD1V8 = 1.62/1.8/1.98 V` + §1.2 SARADC 特性 (12-bit / 1MS/s / 8 单端通道) · ★**[实测]** `FET3572C_PIN_TABLE.csv` L39 + 表A L181-L186 逐字 · ★**[推算]** 候选分压比全表 (A: 2.0M+1.2M ⇒ 1.575V typ / 1.595V worst / 利用率 87.5% / 漏电 1.31µA; B: 1.0M+560k ⇒ 1.508V; C: 1.0M+680k ⇒ 1.700V (不推荐); D: 2.0M+1.0M ⇒ 1.400V / 1.419V / 77.8% / 1.40µA; 现值 1M+1M ⇒ **2.100V 过压**) · ★**[0数据]** SoM SAR-ADC 的输入电容 Cin / 采样保持时间 / 模块自身 abs-max (★芯片级已判死 ⇒ 这一条现在【不阻塞】★)
<!-- WPITEM:END -->

### ★★§2.8 · d8 · BAT_DET 分压链漏电预算 (ISS-211 U-4)★★

<!-- WPITEM:BEGIN id=d8 -->
① 项号: ★**d8** ★ (规格页 §10 第 (4) 条 · 锚点组 `d8_*` (8 条) · 翻面判据 **R8**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv` L182 的 note 逐字**:
`[R_BAT_DET_1] ★DNP: 同上 (电池电压分压上臂) | [BAT_DET_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]`
★**真值漏电 (本单自己算)**: 1M+1M ⇒ @3.0V **1.50µA** / @3.7V **1.85µA** / @4.2V **2.10µA** (功耗 8.82µW) / @5.0V **2.50µA** ⇒ ★**note 的 "~1.65µA @5V" 与自己的 1M+1M 对不上 (1.65µA 正好是 3.3V/2MΩ 的值 ⇒ 标签 @5V 写错了, 或者值是按 @3.3V 算的) ⇒ 真值 @5V = 2.50µA ⇒ 差 1.52× ⇒ 按 1.65µA 做预算会低估 34%★** · ★**BOM `HW/BOM_v1.csv`** ★**L86** `R_BAT_DET_1,1,1M ±1%,R,DNP` · ★**L87** `R_BAT_DET_2,1,1M ±1%,R,DNP` · ★**L27** `C_DET_BAT,1,100nF ±10%,C,DNP`
③ 缺陷一句话: ★**"漏电流"这个数在自己的同一行里就是错的** ⇒ ★**它是本项目里少见的"算术当场可判"的缺陷 ⇒ 门禁已把它做成机器判据 (`calc(leak_ua@4.2)` vs `calc(leak_note_ua@5)` 两条都钉在现行值上) ⇒ 改坏任何一个 ⇒ 门禁变红★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段 `R_BAT_DET_1` 那条 `add()` 的 `note` 字符串** (★手写文案, **不与 `value` 联动** ⇒ "值改了, 文案没改"的老病, 与 d1/d2 同型★) ⇒ ★**★解法不是"再手写一次对的数", 是"让门禁把两个数对上" (⇒ 门禁 R8)★** ⇒ ★**预算口径真源 = `HW/POWER_BUDGET_V3.md` §5 (待机 0.03~0.06W, 地板 0.05W) + §5.1 (mAh = P × 361.81) + §7 (丰江 432243 3.7V ≥420mAh) + `HW/INTERFACE_TABLE.md` C-02/C-03★
⑤ 改法 (逐字值): ★**`state/gen_netlist.py`** BAT_DET 段 `R_BAT_DET_1` 那条 `add()` 的 `note`: `"漏电流 ~1.65µA @5V"` → ★`"漏电流 1.31µA @4.2V (上臂 2.0M + 下臂 1.2M ⇒ 总阻 3.2M ⇒ 4.2V/3.2M; 功耗 5.5µW = 待机地板 0.05W 的 0.011%)"`★ (★★**数值必须由 value 推导出来, 且写清口径 (总阻 / @4.2V)★; 若按 V-3 裁降级档 D (2.0M+1.0M) ⇒ 改写为 `"漏电流 1.40µA @4.2V (总阻 3.0M …)"`★**) ⇒ 同时把同一条 note 里的 `"★DNP: 同上"` → 写全的句子 (★与 d2 的 ⑤ 同一处★) ⇒ ★**不许再出现 `~1.65µA @5V` 这种与 value 对不上的数** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R8 必须转绿★) ⇒ ★**并把分压链功耗写进 `HW/POWER_BUDGET_V3.md` 的待机口径 (★归落表那趟, 本单不改★)**
⑦ 翻面判据: ★**R8** ★ (★`--expect-resolved` 的 R8 段: `R_BAT_DET_1` 的 note 里不再出现 `~1.65µA @5V`, 且 note 自称的漏电流数 == 由 value 算出来的数★) ⇒ ★**配合【分压比利用率】判据 (★那一条挂在 d7 组上) 与 d2 的装不装一起看★**
⑧ 证据等级: ★**[实测]** L182 note 逐字 + BOM L86/L87/L27 + `HW/POWER_BUDGET_V3.md` §5/§5.1/§7 + `HW/INTERFACE_TABLE.md` C-02/C-03 · ★**[推算]** 漏电全表 (1.50/1.85/2.10/2.50 µA) + 功耗 (8.82µW @4.2V) + 占待机地板 0.05W 的 **0.018%** + 折中判据 (总阻 ≥35.3kΩ ⇒ 现值有 57× 余量 ⇒ **"改小阻值"这个顾虑本身不成立**) · ★**[0数据]** 实测漏电流 (★无样件 ⇒ 本单实物 [实测] = 0 条★) · ★**[0数据]** "1.65µA @5V" 的来源 (但结论不依赖它, 真值 2.50µA 由阻值直接算)
<!-- WPITEM:END -->

### ★★§2.9 · d9 · USB D− 的 ESD 方案 + 型号判据 (ISS-211 U-1)★★

<!-- WPITEM:BEGIN id=d9 -->
① 项号: ★**d9** ★ (规格页 §10 第 (5) 条 · 锚点组 `d9_*` (7 条) · 翻面判据 **R4 + R9**)
② 现状逐字 + 行号: ★**表A L417** `P1,USB_D_P_SRC,D_ESD_USB_D,USB_D_P_SRC,D_ESD_USB_D,ESD 阵列 [待选型] (USB 2.0 双通道),D,必装,[推算],,"[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**",A-24,MAIN_PCB,,` · ★**表A L418** `P1,GND,D_ESD_USB_D,GND,D_ESD_USB_D,ESD 阵列 [待选型],D,必装,[推算],,[D_ESD_USB_D] ESD 地端,A-24,MAIN_PCB,,` · ★**板文件实读**: `D_ESD_USB_D` pads=**2**, pad1→`USB_D_P_SRC` (★串阻的 **SoM 侧**★), pad2→`GND`, 原点 (94.95, 21.8); `J_USB_C` 原点 (140.0, 5.25) ⇒ ★**距离 47.99mm**★ · ★**板上 4 个 ESD 位号逐个查网 ⇒ 挂 `USB_D_N_SRC` / `NET_USB_D_N_TYPEC` 的 = 0 个**★ · ★**`state/gen_schematic_pages.py` P9 页逐字**: `④ **ESD 距连接器 ≤3.0mm** / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC` (★ISS-085 结构总工回执★) · 同页另一条: `① **不装共模扼流圈** (USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图) → 只靠 **FPC 阻抗控制 + 两端 ESD**` · ★**`HW/EMC_PRECHECK.md:211`** `**USB 2.0 差分**: D+/D- 90 Ω 差分, 480 Mbps, …` ⇒ ★**USB 速率 = 480 Mbps (高速级)★**
③ 缺陷一句话: ★**D− 那条路上 ESD 位号数 = 0 (只护了差分的一边) + 器件自称"双通道"而封装只有 2 焊盘 + ESD 挂在串阻的 SoM 侧且距接口 47.99mm ⇒ P9 页自引的"两端 ESD"规矩也没做到 ⇒ 这是"规矩在、器件不在位"★** ⇒ ★**并且规格页 §5.2 写"≤5mm"、P9 页写"≤3.0mm" ⇒ 两个口径并存 ⇒ 落表验收判据不唯一 (⇒ 补差 B 收口)★**
④ 真修法在哪个真源: ★**① 选型判据真源 = 官方 datasheet** (★TI **TPD2EUSB30 / TPD2EUSB30A / TPD4EUSB30** datasheet **SLVSAC2G** + onsemi **AND8074/D** + onsemi **STF202-22T1G** datasheet (★作排除项★)★) ⇒ ★**② 落表真源 = `state/gen_netlist.py` 的 USB ESD 段 (★现 L1384-L1388★) + `state/gen_netlist_pins.py` + 板封装/位置 (`state/gen_pcb_components.py` / `state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py`)★** ⇒ ★**③ 位置门槛真源 = `state/gen_schematic_pages.py` P9 页的 `≤3.0mm` (ISS-085)** ⇒ ★**★按 3.0mm 判 (项目自己的规矩, 更严) ⇒ 门禁 R9 阈值已从 5.0 改成 3.0 (补差 B)★** ⇒ ★**型号 = 老板级 (V-2) ⇒ 本单只出候选 + 判据串 + 降级方案, 不代拍**
⑤ 改法 (逐字值): ★**① 门禁 (★本单已落★)**: `HW/check_netlist_selfconsistency.py` 的 R9 阈值常量由 `5.0` → ★`ESD_MAX_DIST_MM = 3.0`★ (★现状断言 `d9_esd_dist` = `calc(esd_dist_usb) > 5` **一字不动**★) ⇒ ★**② 落表那趟**: 按 d4 的 ⑤ 改 `state/gen_netlist.py` (3 脚双通道, pad net = `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` / `GND`), 并把位置挪到 `J_USB_C` 旁 ≤ 3.0mm ⇒ ★**③ 型号 (V-2 裁决后填进 `state/gen_netlist.py` 的 `value`)**: 判据串必须含 ★`≤1.0 pF/线` ★ `V_clamp ≤ 8V @1A` ★ `IEC 61000-4-2 level 4 contact (8kV)` ★ `3 脚单列封装 (SOT-3 / DRT 1.0×0.8mm 级)` ★ `VRWM ≥ 5.25V`★ ⇒ ★**④ 排除项 (必须写进规格)**: onsemi **STF202-22T1G** 官方 datasheet 的 `Typical Line Capacitance … **68**` pF ⇒ USB 全速 12Mbps 级 ⇒ ★**本项目 480Mbps 高速差分线上绝对不许用"滤波+端接+ESD"三合一集成件★** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/gen_pcb_components.py` ★ → ★`python3 state/gen_pcb_routing.py` ★ → ★`python3 state/gen_pcb_netlist_board.py` ★ → ★`python3 state/check_kicad_net.py` ★ → ★`python3 state/check_pcb_drc.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R4 + R9 必须转绿★)
⑦ 翻面判据: ★**R4 + R9** ★ (★R4: 板上挂 D− 两张网的 ESD 位号数 ≥ 1, `D_ESD_USB_D` 焊盘数 = 3; R9: `D_ESD_USB_D` → `J_USB_C` 板面距离 **≤ 3.0 mm**★)
⑧ 证据等级: ★**[官网]** ON Semi **AND8074/D** (「The STF202 … provides ESD Protection to IEC6100-4-2 in both I/O data lines (D+ & D−)」/ Zo 90Ω±15% / IEC 等级表 / 钳位 8.70V@8kV 接触, 10.60V@15kV 空气) · onsemi **STF202-22T1G** datasheet (Rev 11) (线电容 **68 pF** / 内置 RS 20/22/24Ω) · TI **TPD2EUSB30 / TPD2EUSB30A / TPD4EUSB30** datasheet **SLVSAC2G** (2ch/4ch / DRT **0.7 pF typ**, DQA 0.8 pF typ / **IEC 61000-4-2 level 4 contact 8kV** / **Vclamp = 8V @1A** / DRT 1.00×0.80mm) · ★**[实测]** 板文件焊盘/net/坐标/距离 **47.99mm** + 4 个 ESD 位号逐个查网 + P9 页规矩两条 + `EMC_PRECHECK.md:211` 的 480Mbps · ★**[推算]** 480Mbps 的电容预算 / 只护单边的后果 · ★**[0数据]** SoM USB PHY 的 abs-max / 实际采购可得性与单价 (★零外发 ⇒ 未询价★)
<!-- WPITEM:END -->

### ★★§2.10 · d10 · CHARGE_BOARD_SPEC §2.4/§3.4: ICHG/IIN 系数方向反了 ⇒ 连带 390Ω 档的判据也不成立★★

<!-- WPITEM:BEGIN id=d10 -->
① 项号: ★**d10** ★ (规格页 §10 第 (7) 条 · 锚点组 `d10_*` (15 条) · 翻面判据 **R10**)
② 现状逐字 + 行号: ★**`HW/CHARGE_BOARD_SPEC.md`** ★**L182 (表头)** `| \`R_ILIM\` | IINMAX (min/typ/max) | CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822) | 铰链段实际载流 | 用途 |` · ★**L184 (390Ω 行)** `| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.67 / 0.75 / **0.82 A** | **~0.75 A** | ★★**本规格推荐值** (V1.9, … 单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×) |` · ★**L185 (300Ω 行)** `| 300Ω ±1% | 1.07 / 1.18 / 1.30 A | 0.88 / 0.97 / 1.07 A | ~1.0 A | ❌ **300Ω 档正式判死** … 单 pin 0.534A > … 0.5A 触点天花板 … |` · ★**L186 (260Ω 行)** `| 260Ω ±1% | 1.23 / 1.37 / 1.50 A | 1.01 / 1.13 / 1.23 A | ~1.1 A | datasheet 官方示例值 (KILIM=390 max 时 1.5A) |` · ★**L320 (§3.4 公式)** `> \`ICHG ≈ IIN × (VBAT / VBUS) / η\`, 取 VBAT=3.7V, VBUS=5V, η=90% → **ICHG ≈ 0.822 × IIN**。` · ★**L711 (自检脚本)** `    print(f"R_ILIM={r} -> IINMAX {lo:.2f}/{ty:.2f}/{hi:.2f} A -> ICHG~{lo*0.822:.2f}/{ty*0.822:.2f}/{hi*0.822:.2f} A")` · ★**表A `HW/netlist_v1.csv`** ★**L47** `value = 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)` (note 里还有 ★`★★V1.7 按 ISS-091 结构核算定 **470Ω**`★ 的残留句) · ★**L48** 同 value · ★**L497** `P10,BAT_CHG,U_CHG pin14,J_CHG pin1,J_CHG,"1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",CONN,必装,[推算],,"充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (★每 pin ≤0.75A★); 铰链段不装 π 滤波 …",C-03,HINGE,,` · ★**BOM `HW/BOM_v1.csv` L97** `R_ILIM,1,390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A),R,必装,镜框充电板,P1,[官方],…`
★**【ISS-220 第 1 批已落表 (方向修正部分) · 2026-11-16】** ★本栏『现状』部分已变 ⇒ 新逐字: `CHARGE_BOARD_SPEC.md` §2.4 表头 = `CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**)` / §3.4 公式 = `ICHG ≈ IIN × η × (VBUS / VBAT)` / 表A L47/L48 value = `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决)` (★行号未变★) ⇒ ★**档位本身仍 BLOCKED 于 V-4**★ ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**同一件事两个文件是反的** —— buck 功率守恒是 `VBUS·IIN·η = VBAT·ICHG` ⇒ `ICHG/IIN = η·Vbus/Vbat`, 而规格书写的是 `(VBAT/VBUS)/η` = **倒数** (0.822 = 1.216 的精确倒数; 0.933 = 1.071 的精确倒数) ⇒ ★**⇒ 390Ω 档"单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×"这个安全结论是假的 ⇒ 真值单 pin = 0.608A ⇒ 超 0.5A 触点额定 21.6% ⇒ R_ILIM 档位不能定★** ⇒ ★**而且同一个网表里两个触点额定自己打架 (L47 note 写天花板 0.5A / L497 note 写"每 pin ≤0.75A") + L47 note 里还有 V1.7 的 470Ω 残留 (见 #8)★**
④ 真修法在哪个真源: ★**`HW/CHARGE_BOARD_SPEC.md`** ★**§2.4 表 (L182 表头 + L184/L185/L186 三行) + §3.4 公式 (L320) + §3.4 六个场景行 + L711 自检脚本** ⇒ ★**网表侧 `state/gen_netlist.py` 的 `R_ILIM` 两条 `add()` 的 `value` + `J_CHG` 那条 `add()` 的 `note`** ⇒ ★**★方向真源 = TI BQ25896 datasheet SLUSC76C 原文 (「IINMAX = KILIM/RILIM」/「92.5% Charge Efficiency at 2 A and 90.5% Charge Efficiency at 3 A」/ KILIM 320/355/390 AΩ) + buck 功率守恒★** ⇒ ★**★根因 = §2.4/§3.4 的公式是手写推导, 没有引用 datasheet 的功率守恒与 η 的官方出处 ⇒ 与 MECH 侧 `MECH/check_demo_struct_truth.py` G2.8 (按物理真值判 1.216/1.071) 相反 ⇒ 两边各自"自洽", 但只有一边对★**
⑤ 改法 (逐字值) — ★**按 V-4 裁决后落, 下面是"方向修正 + 三档重算" (★档位本身待裁★)★**:
| 位置 | 从 | 到 |
|---|---|---|
| ★**`HW/CHARGE_BOARD_SPEC.md` L182 (表头)** ★ | `CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822)` | ★`CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**)`★ |
| ★**同 L320 (§3.4 公式)** ★ | `ICHG ≈ IIN × (VBAT / VBUS) / η` … `ICHG ≈ 0.822 × IIN` | ★`ICHG ≈ IIN × η × (VBUS / VBAT)` … `ICHG ≈ **1.216 × IIN** @3.70V / **1.071 × IIN** @4.20V`★ |
| ★**同 L711 (自检脚本)** ★ | `lo*0.822` | ★`lo*1.216` (★并按 VBAT 分别取 1.216 / 1.071★)★ |
| ★**同 L184 (390Ω 行)** ★ | `0.67 / 0.75 / **0.82 A**` + `单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×` | ★`**0.997 / 1.107 / 1.216 A**` + `单 pin **0.608A** (★超 0.5A 触点额定 21.6% ⇒ 档位待 V-4 裁决★)`★ ⇒ ★**"≤0.5A, 余量 1.22×" 必须删★** |
| ★**同 L185 (300Ω 行)** ★ | `0.88 / 0.97 / 1.07 A` + `单 pin 0.534A` | ★`**1.298 / 1.437 / 1.581 A**` + `单 pin **0.791A**`★ |
| ★**同 L186 (260Ω 行)** ★ | `1.01 / 1.13 / 1.23 A` | ★`**1.496 / 1.657 / 1.824 A**` + `单 pin **0.912A**`★ |
| ★**同 L184 的"用途"栏** ★ | `★★**本规格推荐值**` | ★`★★**待裁决 (V-4): 475~510Ω (解①) 或 390Ω + J_CHG 4 pin 并联 (解②)★★`★ |
| ★**§3.4 六个场景行** ★ | "铰链段 ICHG" 列全部按 0.822 算 | ★场景① `~0.41 A` → **`~0.61 A`**; 场景③ `~0.67-0.82 A` → **`~1.00-1.22 A`**; 场景⑤ 300Ω → **`~1.30-1.58 A`**; 场景④ 260Ω → **`~1.50-1.82 A`** ★ |
| ★**`state/gen_netlist.py` 的 `R_ILIM` 两条 `add()` 的 `value`** ★ | `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)` | ★按裁决后的档位串 (★解① 例: `475Ω ±1% (IINMAX 0.67-0.82A · ICHG 0.82-0.999A · 单 pin ≤0.50A)`; 解② 例: `390Ω ±1% (IINMAX 0.82-1.00A · ICHG 1.00-1.22A · 单 pin ≤0.31A)`★)★ |
| ★**`state/gen_netlist.py` 的 `J_CHG` 那条 `add()` 的 `note`** ★ | `每 pin ≤0.75A` | ★`每 pin **额定 0.75A / 降额后工作上限 0.50A** (ISS-099 FH12-10S-0.5SH(55)); 载流 pin = pin1/pin2 (或裁决后 pin1/2/9/10)`★ |
| ★**`state/gen_netlist.py` 的 `R_ILIM` 那条 `add()` 的 `note`** ★ | `★★V1.7 按 ISS-091 结构核算定 **470Ω**` | ★删掉该句 (或明确标 "已作废")★ (★见 #8★)★ |
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R10 必须转绿★) ⇒ ★**并核 `MECH/check_demo_struct_truth.py` G2.8 与 `HW/CHARGE_BOARD_SPEC.md` 逐字一致 (★两边口径必须能互查, 但 MECH 侧归 mech-lead, 本单不改★)**
⑦ 翻面判据: ★**R10** ★ (★`--expect-resolved` 的 R10 段: `HW/CHARGE_BOARD_SPEC.md` 不再含 `0.822` 且含 `1.216` 与 `1.071`; 表A `R_ILIM` 的 value 不再含 `0.411A`; 且 `calc(ichg_pin_max@3.7) ≤ 0.5A`★)
⑧ 证据等级: ★**[官网]** TI **BQ25896** datasheet **SLUSC76C** (特性 "High Efficiency 3-A, 1.5-MHz Switch Mode Buck Charge — 92.5% Charge Efficiency at 2 A and 90.5% Charge Efficiency at 3 A Charge Current" / ILIM 脚 "A resistor is connected from ILIM pin to ground to set the maximum limit as **IINMAX = KILIM/RILIM**" / KILIM 320/355/390 A×Ω) · ★**[实测]** CHARGE_BOARD_SPEC L182/L184/L185/L186/L320/L711 + 表A L47/L48/L497 + BOM L97 逐字 + `MECH/check_demo_struct_truth.py` G2.8 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 的 `MECH_ANCHORS` (eta 0.90 / v_bus 5.0 / ratio_370 1.216 / ratio_420 1.071) · ★**[推算]** 功率守恒与全表重算 (真值 ICHG/IIN = 1.2162 @3.70V / 1.0714 @4.20V; 390Ω 档 ICHG 0.997/1.107/1.216 A @3.70V, 单 pin 0.608A; 300Ω 单 pin 0.791A; 260Ω 单 pin 0.912A; 解① 的 475/487/510Ω ⇒ 单 pin 0.499/0.487/0.465A) + η=0.90 的保守性论证 (官方 92.5%@2A) · ★**[0数据]** 铰链段实际接触电阻 / 温升 / 载流实测 (无样件)
<!-- WPITEM:END -->

### ★★§2.11 · d11 · NET-LED / board 列: ★"转述 vs 实测"不一致 + 真缺陷在 `C_VBUS_GND`★★

<!-- WPITEM:BEGIN id=d11 -->
① 项号: ★**d11** ★ (规格页 §10 第 (8) 条 · 锚点组 `d11_*` (13 条) · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L9** `P1,VBUS_5V_F1,VBUS_5V_F1,C_VBUS_OUT,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,π 滤波后级电容位 (BQ25896 建议 ≥100µF),C-01,CHG_BOARD,,` · ★**L10** `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,"π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容, 又是对地电容 · 一颗 2 脚件落进 3 个网 = 导出后一脚悬空); BQ25896 建议 ≥100µF",C-01,MAIN_PCB,,` · ★**L11** `P1,VBUS_5V_CHG,C_VBUS_OUT,U_CHG pin1,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,"π 滤波电容 (后级, 串联) 位",C-01,CHG_BOARD,,` · ★**L12** `P1,VBUS_5V_CHG,C_VBUS_GND,C_VBUS_OUT,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点),C-01,MAIN_PCB,,` · ★**L13** `P1,VBUS_5V_CHG,U_CHG,NET_VBUS_5V_CHG,U_CHG,BQ25896,IC,必装,[官方],…,…,C-01,CHG_BOARD,…` · ★**L508/L509** (`R_CHG_LED` 两行) `board` **全部 = `CHG_BOARD`**; ★**L510/L511** (`D_CHG_LED`) `board` 也 = `CHG_BOARD` ⇒ ★**★整条充电灯链全在 CHG_BOARD, 与该行 note「装在充电板 (镜框) 靠近 Type-C 座」完全一致 ⇒ mech-lead 的转述「R_CHG_LED 两端分别标 CHG_BOARD 与 MAIN_PCB」被实测证伪 (见 #7)★** · ★**表B `HW/netlist_v1_pins.csv`** ★**L148/L149** (`C_VBUS_GND.1/.2`) board=`MAIN_PCB` · ★**L154/L155** (`C_VBUS_OUT.1/.2`) board=`CHG_BOARD` ⇒ ★**脚表与表A 一致地坏 (不是单边漂移)★** · ★**板文件实读**: `C_VBUS_GND` pads=**2**, pad1→`GND`, pad2→`VBUS_5V_CHG`, 原点 (107.7, 42.5) ⇒ ★**封装确实在 demo 主 PCB 里 (与 board 列自洽)★**; `C_VBUS_OUT` 在 demo 主 PCB 里 **没有**封装 (`count_footprint(C_VBUS_OUT) == 0`, ★与 board 列自洽★); `J_CHG` pads=**2** (pin1=`BAT_CHG` / pin6=`PWR_GOOD`) ⇒ ★**★这张网从主板到充电板没有物理通路 ⇒ 主板那半边是一颗 DNP 电容的一只脚 = 死头支路★**
★**【ISS-220 第 1 批已落表 · 2026-11-16】** ★本栏『现状』部分已变 ⇒ 新逐字: 表A L10/L12 与脚表 L148/L149 的 board = `CHG_BOARD` (原 `MAIN_PCB`); BOM L51 的板列 = `镜框充电板` (★行号未变★) ⇒ ★**板侧封装归属仍待『板只改一次』那一趟同步 (本单只报不改)★** ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**net `VBUS_5V_CHG` 上并着三行 (L11 `C_VBUS_OUT` / L12 `C_VBUS_GND` / L13 `U_CHG`) 而 board 列出现两档** ⇒ ★**★真缺陷 = π 滤波的【对地电容】`C_VBUS_GND` 被分到了另一块板上 (MAIN_PCB) ⇒ BQ25896 的输入去耦被甩到另一块板 (BQ25896 官方: 「Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC」) + 该网在主板侧是死头支路★** ⇒ ★**不是"一颗电容的两端", 是"同一张网的两颗器件挂到两块板"★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**`CHG_BOARD_REFS` 白名单 (★现 L120-L131★)** ★**加 `"C_VBUS_GND"`** ⇒ ★**★根因 = `board_for()` (现 L200-L218) 的默认分支 `return BOARD_MAIN` ⇒ 白名单漏一颗就默认落主板 ⇒ 这是【结构性】缺陷, 一次修好必须修白名单, 不许只改这一颗的网表行★** ⇒ ★**脚表 board 列按网表派生 (自动跟随) · 板封装由板生成器按 board 列过滤 (⇒ `C_VBUS_GND` 的封装会从 demo 主 PCB 上消失 ⇒ 板会改 ⇒ 必须并进"板只改一次"那一趟)★** ⇒ ★**★铁证: 同一个白名单的注释自己写着「★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**」⇒ 同型坑 (`R_VBUS_DET_1/2`) 已被发现并修过一次, 只修了两只电阻漏了旁边那颗电容★**
⑤ 改法 (逐字值): ★**`state/gen_netlist.py` L120-L131**:
```
CHG_BOARD_REFS = {
    "D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "C_REGN", "R_ILIM",
    "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG",
    ★★新增: "C_VBUS_GND",   ← ★π 滤波后级【对地】电容, 物理上必须在充电板 (与 C_VBUS_OUT 同板)★★
    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
    ...
}
```
⇒ ★**重跑后表A L10/L12 与脚表 L148/L149 的 board 自动由 `MAIN_PCB` → `CHG_BOARD`** ⇒ ★**不许手改 `HW/netlist_v1.csv` 的 board 列** (★重跑 `state/gen_netlist.py` 就会被打回 MAIN_PCB★) ⇒ ★**并顺带做一次【双向对账】(★根因级修法, 见 #5★)**: `CHG_BOARD_REFS` 与 `HW/CHARGE_BOARD_SPEC.md` §7 连接清单逐行对账 (★§7 清单里的每一行都必须 board=CHG_BOARD; 网表里 board=CHG_BOARD 的每一颗都必须在 §7 清单里★) ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/gen_pcb_components.py` ★ → ★`python3 state/gen_pcb_netlist_board.py` ★ → ★`python3 state/check_kicad_net.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R11 必须转绿★)
⑦ 翻面判据: ★**R11** ★ (★`--expect-resolved` 的 R11 段: net `VBUS_5V_CHG` / `VBUS_5V_F1` 的所有行 board 列 = `CHG_BOARD` (表A + 脚表); `C_VBUS_GND` 的 board = `CHG_BOARD`; 板文件 `count_footprint(C_VBUS_OUT) == 0` 且 `count_footprint(C_VBUS_GND) == 0`★)
⑧ 证据等级: ★**[实测]** 表A L9-L13 / L508-L511 逐字 + 脚表 L148/L149/L154/L155 逐字 + 板文件封装清单与 pad→net + `J_CHG` 焊盘只有 pin1/pin6 + `state/gen_netlist.py` 的 `CHG_BOARD_REFS` 与 `board_for()` 源码与注释逐字 · ★**[官方]** BQ25896 "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" (★`HW/CHARGE_BOARD_SPEC.md` L115 已逐字引用★) · ★**[推算]** "跨板去耦"与"死头支路"的后果 · ★**[0数据]** 充电板实物 (整机阶段才有) / 跨板回流路径的实际寄生
<!-- WPITEM:END -->

---

## 3. ★★附带发现 #1..#8 · 每条 8 栏 (★规格页 §11★) ★★

### ★★§3.1 · #1 · `imp` 一个字段同时服务两种物理量 (★完整方案见 §4.A 补差A★)★★

<!-- WPITEM:BEGIN id=#1 -->
① 项号: ★**#1** ★ (规格页 §11 附带发现 #1 · 吸收到 **d5** · 锚点组 `d5_*` · 翻面判据 **R5**)
② 现状逐字 + 行号: ★**`HW/SCHEMATIC_V1_SPEC.json` 的 `connections` 共 57 条, `imp` 实测承担 4 种语义 (本单全表枚举)★**: ① **差分线受控阻抗 20 条** —— `A-01`~`A-10` (CSI, idx[0]~idx[9]) + `A-13`~`A-22` (DSI, idx[12]~idx[19] + idx[55] + idx[56]), `imp` 全部 = `"100Ω ±10%"` (★= MIPI DSI/CSI 差分阻抗★); ② **串联电阻值 2 条** —— `B-09` (FSIN, idx[28]) `imp="单端, 50Ω 串阻"` + `B-19` (JTAG, idx[38]) `imp="单端, 100Ω 串阻"`; ③ **上拉阻值 2 条** —— `B-01` (idx[20]) `imp="上拉 4.7k 到 3.3V (…)"` + `B-02` (idx[21]) `imp="上拉 4.7k 到 3.3V"`; ④ **空 11 条** —— `C-01`~`C-11` (idx[44]~idx[54]) `imp=None`; ★★**⇒ `B-21` (idx[40]) / `B-22` (idx[41]) 把语义①的【差分阻抗 90Ω】塞进了本该是语义②的槽位 ⇒ 必然打架★** ★
★**【ISS-220 第 1 批已落表 (字段基建部分) · 2026-11-16】** ★`imp` / `z_diff` 两个字段已建好: A 组 20 条 `z_diff` = `100Ω ±10%` · `B-21`/`B-22` 的 `z_diff` = `90Ω ±15% 受控阻抗` · `B-01`/`B-02`/`B-09`/`B-19`/`A-11`/`A-12` 的 `z_diff` = 空 ⇒ ★**A 组 20 条的 `imp` 仍保留 `100Ω ±10%`** (★清空它会让 `state/check_netlist.py` 判据 5 的 A 组比对变成 0 行 ⇒ 那是判据覆盖变弱, 不许在不改 check_netlist.py 的前提下做★) ⇒ ★**B-21/B-22 的 `imp` 仍 BLOCKED 于 V-1**★ ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**同一个 `imp` 字段同时服务"差分线阻抗"和"串联电阻值"两种物理量** ⇒ ★**在 DSI 组因为两个物理量各归各 (NET 行 100Ω = 差分阻抗 / 器件行 0Ω = 直通位) 所以不打架, 在 USB 组因为差分阻抗被写进 `imp` 而真串阻另有一颗 22Ω 的器件行 ⇒ 两个物理量被塞进同一个字段 ⇒ 必然打架★**
④ 真修法在哪个真源: ★**`HW/SCHEMATIC_V1_SPEC.json`** ★**`connections[]` 每一条新增一个键 `z_diff` (★差分线受控阻抗★), 并把 `imp` 收敛为"串接电阻值 / 上拉阻值"语义** ⇒ ★**`state/gen_netlist.py` 的 `conn_row()` (★现 L770-L781★)** ★**改取值优先级 (★这是唯一需要碰生成器的一处, 且只在"同时落字段拆分"时才碰★) ⇒ ★**★门禁 R5 已经是按"串阻口径"写的, 字段拆完 R5 不用改★**
⑤ 改法 (逐字值): ★**完整字段拆分方案 = §4.A 补差A (含字段名 / 迁移清单 / `conn_row()` 改动面 / 改完后 `check_netlist.py` 与 `check_netlist_pins.py` 的期望结果)★** ⇒ ★**本条只给结论: 字段名 = `imp` (串接电阻 / 上拉阻值, 器件侧) + `z_diff` (差分线受控阻抗, 板级)★**
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R5 必须转绿★)
⑦ 翻面判据: ★**R5** ★ (★`--expect-resolved` 的 R5 段: NET 行 value 不含 "90Ω" 且含 "22Ω"; SPEC.json B-21/B-22 的 `imp` 不含 "90Ω" 且含 "22Ω"★)
⑧ 证据等级: ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` 57 条 `connections` 全表枚举 (`id` / `signal` / `level` / `imp` 四列逐条实读, 本单自跑脚本) · ★**[实测]** 表A 里 DSI/CSI 的 NET 行 value = `100Ω ±10%` (20 行) 与器件行 `R_SEL_*` value = `0Ω` (10 行) 的对照 · ★**[推算]** 字段拆分后网表产物逐字节不变的推导 (见 §4.A)
<!-- WPITEM:END -->

### ★★§3.2 · #2 · `R_BAT_DET_1` note 的漏电流数与自己的阻值对不上 (★已并进 d8★)★★

<!-- WPITEM:BEGIN id=#2 -->
① 项号: ★**#2** ★ (规格页 §11 附带发现 #2 · 吸收到 **d8** · 锚点组 `d8_*` · 翻面判据 **R8**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv` L182 note** 逐字 ★`… 上臂阻值大 · 漏电流 ~1.65µA @5V [V1.6: 临时线名 BAT 已归一到源节点]`★ (★L182 的 value = `1M ±1%`★) ⇒ ★**真值 @5V = 2.50µA / @4.2V = 2.10µA (1M+1M) ⇒ 差 1.52×★**
③ 缺陷一句话: ★**note 自称的漏电流与同行的阻值对不上** ⇒ ★**它是 §11 里与 d8 同一件事的第二种表述, 不是新缺陷 ⇒ §11 自己已写"已并进第 (4) 条"★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段 `R_BAT_DET_1` 那条 `add()` 的 `note`** ⇒ ★**与 d8 的 ④ 同源 (★同一处字符串★) ⇒ **落表那趟改一次即可, 不许改两遍★**
⑤ 改法 (逐字值): ★**与 d8 的 ⑤ 完全相同 (★同一处 note★)**: `"漏电流 ~1.65µA @5V"` → ★`"漏电流 1.31µA @4.2V (上臂 2.0M + 下臂 1.2M ⇒ 总阻 3.2M ⇒ 4.2V/3.2M; 功耗 5.5µW = 待机地板 0.05W 的 0.011%)"`★ (★D 档 ⇒ `"漏电流 1.40µA @4.2V (总阻 3.0M …)"`★) ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R8 必须转绿★)
⑦ 翻面判据: ★**R8** ★ (★与 d8 同判据★)
⑧ 证据等级: ★**[实测]** L182 note 逐字 + L182 value 逐字 (本机实读) · ★**[推算]** 漏电真值全表 (1.50/1.85/2.10/2.50 µA) 与 1.52× 差值 · ★**[0数据]** "1.65µA @5V" 的来源 (结论不依赖它)
<!-- WPITEM:END -->

### ★★§3.3 · #3 · ESD 位置判据 5mm vs 3.0mm 口径收口 (★已并进 d9 + §4.B 补差B★)★★

<!-- WPITEM:BEGIN id=#3 -->
① 项号: ★**#3** ★ (规格页 §11 附带发现 #3 · 吸收到 **d9** · 锚点组 `d9_*` · 翻面判据 **R9**)
② 现状逐字 + 行号: ★**ISS-211 规格页 §5.2 逐字**: `★**到 \`J_USB_C\` 的板面距离 ≤ 5 mm (★现在 47.99 mm★)` ⇒ ★**另一处**: `state/gen_schematic_pages.py` P9 页逐字 `④ **ESD 距连接器 ≤3.0mm** / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC` (★ISS-085 结构总工回执★) ⇒ ★**门禁现状**: `HW/check_netlist_selfconsistency.py` 的 R9 段原写 `if d > 5.0:` (★现况断言 `('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5')` 不动★)
③ 缺陷一句话: ★**两个口径并存 ⇒ 落表的验收判据不唯一** (★5mm 还是 3.0mm?) ⇒ ★**⇒ 按 3.0mm 判 (项目自己的规矩, 更严)★**
④ 真修法在哪个真源: ★**`HW/check_netlist_selfconsistency.py`** ★**R9 翻面判据的阈值 (★现状断言不动★)** ⇒ ★**★这是"改判据不改现状"的一处: 现状 47.99mm 无论 5 还是 3.0 都判"缺陷仍在" ⇒ 改阈值不动任何现状断言★**
⑤ 改法 (逐字值): ★**`HW/check_netlist_selfconsistency.py`** ★**① 加模块级常量 (放在 `KILIM_MAX` 等常量旁)**: ★`ESD_MAX_DIST_MM = 3.0   # ★ESD 距 J_USB_C 的翻面阈值 (★按 P9 页自引的 ISS-085 规矩 ≤3.0mm; ISS-211 §5.2 的 5mm 作废★)`★ ★**② R9 段把字面量换成常量**:
```
# ---- R9: ESD 必须真的贴到 J_USB_C (≤3.0mm, ★按 ISS-085 规矩; 原 5.0mm 作废★) ----
...
        if d > ESD_MAX_DIST_MM:
            errors.append(
                f"★R9 未落表: D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm > {ESD_MAX_DIST_MM} mm "
                f"⇒ ESD 还是不在接口旁边")
```
★**③ 现状断言一条字都不许动**: `('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5')` 保持原样 (★现状 47.99 > 5 ⇒ 仍成立★) ★**④ `--selftest` 加一条反向用例 (★见 §4.B★): 把阈值改回 5.0 ⇒ 必须变红★** ★
⑥ 改完跑哪条命令: ★`python3 HW/check_netlist_selfconsistency.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --selftest` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★期望 rc = 0 / 0 / 1★)
⑦ 翻面判据: ★**R9** ★ (★`--expect-resolved` 的 R9 段: `D_ESD_USB_D` → `J_USB_C` 板面距离 **≤ 3.0 mm**★)
⑧ 证据等级: ★**[实测]** 规格页 §5.2 逐字 + `state/gen_schematic_pages.py` P9 页 `≤3.0mm` 逐字 + 门禁 R9 原码 `if d > 5.0:` 逐字 (本机实读) · ★**[实测]** 板面实测距离 47.99mm (⇒ 5 与 3.0 两个阈值现状都判"缺陷仍在" ⇒ 改阈值不动现状断言) · ★**[推算]** "3.0 比 5.0 更严, 且 3.0 是项目自己的规矩 (ISS-085)" 这个取舍
<!-- WPITEM:END -->

### ★★§3.4 · #4 · `J_CHG` 在网表与板文件里指两个不同的物理件 (★已并进 §4.C 补差C★)★★

<!-- WPITEM:BEGIN id=#4 -->
① 项号: ★**#4** ★ (规格页 §11 附带发现 #4 · 吸收到 **d11** · 锚点组 `d11_*` · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv` L497** `P10,BAT_CHG,U_CHG pin14,J_CHG pin1,J_CHG,"1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",CONN,必装,[推算],…,…,C-03,HINGE,,` ⇒ ★**网表: 铰链 FPC 座 1×10p@0.5mm, board=HINGE**★ · ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb` 实读**: 封装 `J_CHG` `Value` = ★`SoM BTB CHG (100pin, 部分已分配)`★, pads=**2** (pad1→`BAT_CHG` / pad6→`PWR_GOOD`), 原点 (135.3, 58.0) ⇒ ★**★同一个位号指两个物理件★** · ★**`state/gen_schematic_pages.py` P9 页逐字**: `1. \`J_CHG\` (**1×10p@0.5mm**) — pin1/pin2 = **充电电流 1.0-1.5A 双 pin 并联** · pin3/pin4 = 回流双 pin · pin5 = CHG_STAT · pin6 = PWR_GOOD · pin7 = VBUS_DET · pin8-10 = 预留` ⇒ ★**与网表对不上 (网表: 7=`NC` / 8=`TS_BAT`, 且没有 5/6 的行)★**
③ 缺陷一句话: ★**同一个位号 `J_CHG` 在网表里是铰链 FPC 座、在板文件里是 SoM BTB 100pin ⇒ 装配/备料/结构三方拿到的是两个不同的件; 且 P9 页的 J_CHG pin map 与网表对不上 (pin5/6 在网表里没有行, pin7 网表是 NC 页面写 VBUS_DET)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**`J_CHG` 那条 `add()` (★现 L1494 附近★) 的 `ref` 与 `value`** + ★**`state/gen_schematic_pages.py` P9 页的 J_CHG pin map 那一行** + ★**板侧 SoM BTB 的位号 (板生成器 + 板文件, ★归 ISS-199/ISS-202★)** ⇒ ★**★位号消歧方案归 ISS-199 (铰链结构) / ISS-202 (J_CHG pinmap) 的地界 ⇒ 本单只出规格与方案, 不落表★**
⑤ 改法 (逐字值) — ★**`J_CHG` 位号消歧方案 (详见 §4.C 补差C 的完整版)★**: ★**建议网表侧改名**: 铰链 FPC 座由 `J_CHG` → ★**`J_CHG_FPC`**★ (1×10p@0.5mm, board=HINGE), 板侧 SoM BTB 保留 `J_CHG` ⇒ ★**理由: 板文件里的 `SoM BTB CHG (100pin)` 是 SoM 厂给定接口 (100pin BTB), 改它的位号会牵动板 + 丝印 + CPL + 投产包; 而网表侧的 10p FPC 座是本项目自己的件, 改名成本低⇒ 影响面: `state/gen_netlist.py` 的 `HINGE_REFS = {"J_CHG"}` (★现 L117★) 须改成 `{"J_CHG_FPC"}` + 表A/表B/BOM/板四处位号同步 + `state/gen_schematic_pages.py` P9 页 pin map 行同步 + ★**ISS-199 (铰链结构) / ISS-202 (J_CHG pinmap) 同步**★ ⇒ ★**★不改的后果: 一个位号两个物理件, 板厂/装配厂/结构三方各按各的理解走 ⇒ 备料会备错件★** ★
⑥ 改完跑哪条命令: ★**★本条不在本单落表范围 (★归 ISS-199/ISS-202★)★** ⇒ ★**若与 V-4 的解② (J_CHG 4 pin 并联) 一起排, 届时跑: `python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` → `python3 state/gen_pcb_netlist_board.py` → `python3 state/check_netlist.py` → `python3 state/check_netlist_pins.py` → `python3 state/check_kicad_net.py`★ ★
⑦ 翻面判据: ★**R11** ★ (★同域判据: 充电板/铰链归属的 board 列一致性; ★★**"位号不再双义"这一条本单没有独立 R# —— 它是结构域 (ISS-199/202) 的验收项, 本单只登记不落表★★**)
⑧ 证据等级: ★**[实测]** 表A L497 逐字 + 板文件 `J_CHG` 封装 value/pads/pad→net/原点 + `state/gen_schematic_pages.py` P9 页 J_CHG pin map 逐字 + `state/gen_netlist.py` L117 `HINGE_REFS` 注释逐字 · ★**[0数据]** J_CHG 实物对插器 (框侧座/脚侧座) 的确切型号 (★ISS-099 回执已提"J_CHG 实物是一对 (框侧座 + 脚侧座)", 但型号/连接器厂商未回★)
<!-- WPITEM:END -->

### ★★§3.5 · #5 · 充电链的 board 列是白名单驱动 ⇒ 白名单漏一颗 = 默认落 MAIN_PCB (★已并进 d11★)★★

<!-- WPITEM:BEGIN id=#5 -->
① 项号: ★**#5** ★ (规格页 §11 附带发现 #5 · 吸收到 **d11** · 锚点组 `d11_*` · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**`state/gen_netlist.py` L120-L131 逐字**:
```
CHG_BOARD_REFS = {
    "D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "C_REGN", "R_ILIM",
    "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG",
    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
    # ★V1.6: P10 充电板页新增的件 (BQ25896 外围) 全在镜框充电板
    "R_PSEL", "R_CE", "R_OTG", "R_PU_SCL", "R_PU_SDA", "R_PU_INT", "R_STAR_PGND",
    "C_VBUS_IC", "C_PMID", "C_BST", "C_BAT", "C_SYS", "L_CHG", "D_TVS_VBUS", "TP_TS",
    # ★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**
    #   (充电板 VBUS 不过铰链到主板 · 分压放在主板 = 采不到电)
    "R_VBUS_DET_1", "R_VBUS_DET_2",
}
```
★**`state/gen_netlist.py` L200-L218 `board_for()` 逐字**: `if ref in HINGE_REFS: return BOARD_HINGE` / `if ref in CHG_BOARD_REFS: return BOARD_CHG` / `if ref.startswith("RAIL_") or ref.startswith("NET_"): …` / `…` / `return BOARD_MAIN   # ★★其余一律落到主板★★` ⇒ ★**`C_VBUS_GND` 不在白名单 ⇒ 落进默认分支 ⇒ `MAIN_PCB`★**
★**【ISS-220 第 1 批已落表 (并入 d11) · 2026-11-16】** ★`CHG_BOARD_REFS` 白名单已补 `C_VBUS_GND` (★结构性根因修法: 白名单漏一颗就默认落 MAIN_PCB★) ⇒ ★**双向对账未通过 (★§7 清单与网表是【两个版本】: §7 有 16 行 board 不是 CHG_BOARD (HINGE/MAIN_PCB), 且有 15 个 ref 在网表里是 CHG_BOARD 却不在 §7 里; §7 还引用了网表里根本不存在的 `R_VDET_TOP`/`R_VDET_BOT`/`USB_D_P_CHG`/`USB_D_N_CHG`/`R_TS1`/`R_TS2`/`C_VBUS_BULK` 等位号★) ⇒ 对账归 #6/补差C 的充电板整页那一趟**★ ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**board 列不是逐行手写的, 是生成器白名单驱动 ⇒ 漏一颗就默认落到 MAIN_PCB ⇒ 这是【结构性】缺陷 ⇒ 同型缺陷 (`R_VBUS_DET_1/2`) 已经被发现并修过一次 (加进白名单), 而 `C_VBUS_GND` 是同一个坑的漏网之鱼 ⇒ 同型缺陷还在往外冒的铁证★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py` L120-L131 的 `CHG_BOARD_REFS` 白名单** (★加 `"C_VBUS_GND"`★) + ★**★更值钱的是【通用根因判据】: 落表那趟必须把白名单与 `HW/CHARGE_BOARD_SPEC.md` §7 的连接清单做一次【双向对账】★** ⇒ ★**★不要只改这一颗的网表行 (★重跑生成器就会被打回★)★**
⑤ 改法 (逐字值): ★**① `state/gen_netlist.py` L120-L131**: 加 `"C_VBUS_GND",` (★与 `"C_VBUS_OUT"` 并列, 见 d11 的 ⑤★) ⇒ ★**② 落表那趟跑一次双向对账 (★人工, 但要有结论写进交卷★)**: ★**§7 清单里的每一行都必须 board=CHG_BOARD** (★现状 `CHARGE_BOARD_SPEC.md` §7 的清单每一行 `board` 列都写 `CHG_BOARD`, ★共 80 行, ★但 §7.1 的对账表里"现行网表引用 80 行"已过期 —— 见 #6★)★**; ★**网表里 board=CHG_BOARD 的每一颗都必须在 §7 清单里** ⇒ ★**③ 可选加固 (★归落表那趟, 本单不改 `state/check_netlist.py`★): 在 `state/check_netlist.py` 加一条"充电板本地网 (`VBUS_5V_CHG` / `VBUS_5V_F1` / `VBUS_5V_ESD`) 上所有器件的 board 必须 = CHG_BOARD"的断言** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R11 必须转绿★)
⑦ 翻面判据: ★**R11** ★ (★与 d11 同判据: net `VBUS_5V_CHG` / `VBUS_5V_F1` 所有行 board = CHG_BOARD★)
⑧ 证据等级: ★**[实测]** `state/gen_netlist.py` L117-L131 与 L200-L218 逐字 (本机实读) · ★**[实测]** 表A 里 board=CHG_BOARD 的全部位号与 §7 清单逐条可对 (★`state/gen_netlist.py` 的白名单共 30 个 ref, 另有 `NET_VBUS_5V_CHG` 这种网名型条目★) · ★**[推算]** "白名单驱动 = 结构性缺陷, 会持续漏" 的论证
<!-- WPITEM:END -->

### ★★§3.6 · #6 · `C_VBUS_OUT` 串联在 BQ25896 的 DC 输入路径上 + §7 `C_VBUS_BULK` 对不上 (★完整方案见 §4.C 补差C★)★★

<!-- WPITEM:BEGIN id=#6 -->
① 项号: ★**#6** ★ (规格页 §11 附带发现 #6 · 吸收到 **d11** · 锚点组 `d11_*` · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv`** ★**L9** `net=VBUS_5V_F1` `ref=C_VBUS_OUT` `value=[待选型] 100µF` `dnp=DNP` `board=CHG_BOARD` · ★**L11** `net=VBUS_5V_CHG` `node1=C_VBUS_OUT` `node2=U_CHG pin1` `ref=C_VBUS_OUT` note 逐字 ★`π 滤波电容 (后级, 串联) 位`★ ⇒ ★**★100µF 是【串联】在 BQ25896 的 DC 输入路径上 (VBUS_5V_F1 → C_VBUS_OUT → U_CHG pin1) ⇒ 稳态充不了电★**★ · ★**L10/L12** `C_VBUS_GND` = 【对地】100µF (★但 board 列错, 见 d11★) · ★**`HW/CHARGE_BOARD_SPEC.md` §7 逐字**: L516 `P10,VBUS_5V_F1,VBUS_5V_F1,C_VBUS_BULK,C_VBUS_BULK,100µF X7R 10V,C,必装,[推算],,π 滤波后级体电容 (BQ25896 输入体电容),C-01,CHG_BOARD` · L517 `P10,GND,C_VBUS_BULK,GND,C_VBUS_BULK,…,π 滤波后级电容 地端,…` · L519 `P10,VBUS_5V_CHG,C_VBUS_BULK,U_CHG pin1,C_VBUS_BULK,…,体电容 → BQ25896 VBUS 脚 (pin1),…` ⇒ ★**★规格 §7 的位号是 `C_VBUS_BULK` (对地), 网表里根本没有 `C_VBUS_BULK` 这个位号 ⇒ 规格 §7 与网表的 π 滤波拓扑/位号都不一致★** · ★**§4.2 (L363) 逐字**: `| \`C_VBUS_BULK\` | 100µF X7R 10V | VBUS_5V_F1 → GND | 磁珠后级体电容 | [推算] (BQ25896 输入体电容) |` · ★**§4.2 的注记逐字**: `★**顺序不可换**: **Type-C → ESD → 磁珠 → 体电容 → BQ25896 VBUS 脚**` + `⚠️ **BQ25896 的输入去耦按 datasheet 原话**: "put **1µF on VBUS to PGND**, and the **rest capacitance on PMID to PGND**"` · ★**§7.1 计数对账表逐字**: `| 本清单总行数 | — | **80** | CHG_BOARD 65 / MAIN_PCB 4 / HINGE 11 |` ⇒ ★**★"现行网表引用 80 行"已过期★**
③ 缺陷一句话: ★**规格 §7 与网表的 π 滤波拓扑/位号都不一致 (规格叫 `C_VBUS_BULK` 对地 / 网表叫 `C_VBUS_OUT` 串联) ⇒ 而网表那个串联的 100µF 放在充电 IC 的 DC 输入路径上 ⇒ 稳态充不了电 (整机阶段 P0) ⇒ 且 §7.1 的"现行网表引用 80 行"已过期★** ⇒ ★**★充电板不进 demo 板 ⇒ 本单只出规格, 不碰网表也不碰板★**
④ 真修法在哪个真源: ★**`HW/CHARGE_BOARD_SPEC.md`** ★**§4.2 (L363 `C_VBUS_BULK` 行 + 两条注记) + §7 (L516/L517/L519 三行) + §7.1 计数对账表** ⇒ ★**网表侧 `state/gen_netlist.py` 的 `C_VBUS_OUT` / `C_VBUS_GND` 两条 `add()` (★各自 2 行, 共 4 行★)** ⇒ ★**★真值真源 = TI BQ25896 datasheet 的输入去耦原话 (1µF@VBUS + 其余@PMID) + `HW/CHARGE_BOARD_SPEC.md` §4.2 的顺序规则★** ⇒ ★**★归 main 派单 (V-7) ⇒ 本单只出规格★**
⑤ 改法 (逐字值): ★**π 滤波真值拓扑规格 (见 §4.C 补差C 的完整版)★**: ① **对地** 电容 = `C_VBUS_BULK` (100µF X7R 10V, VBUS_5V_F1 → GND, 磁珠后级) ② **对地** 电容 = `C_VBUS_IC` (1µF, VBUS 脚, ★官方 "as close as possible to IC"★) ③ **对地** 电容 = `C_PMID` (10µF, PMID 脚, ★官方 "rest capacitance on PMID"★) ④ **串联** 的 100µF = **不许有** ⇒ 网表里的 `C_VBUS_OUT` 100µF 串联位必须去掉/改成对地, 位号统一成 `C_VBUS_BULK` ⇒ ★**§7.1 的"现行网表引用 80 行"必须按落表后的真实行数重算 (★不许照抄 80★)** ★
⑥ 改完跑哪条命令: ★**★本条不在本单落表范围 (★充电板整机阶段, 不进 demo 板★)★** ⇒ ★**若 main 派单落充电板: `python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` → `python3 state/check_netlist.py` → `python3 state/check_netlist_pins.py` → `python3 HW/check_netlist_selfconsistency.py --expect-resolved`★ ★
⑦ 翻面判据: ★**R11** ★ (★同域判据: 充电板本地网的 board 列一致性; ★★**"100µF 不得串联在 DC 输入路径上"这一条本单没有独立 R# ⇒ 落充电板那一趟需要新加一条机器判据 (★归 main 派单的单★)★★**)
⑧ 证据等级: ★**[实测]** 表A L9-L13 逐字 + `HW/CHARGE_BOARD_SPEC.md` §4.2 (L363 + 注记) + §7 (L516/L517/L519) + §7.1 对账表逐字 · ★**[官方]** BQ25896 "put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND" / "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" · ★**[推算]** "100µF 串联在 DC 输入路径 ⇒ 稳态充不了电" (★稳态下串联电容阻抗 → ∞ / 直流不通★) · ★**[0数据]** 充电板实物 (整机阶段才有)
<!-- WPITEM:END -->

### ★★§3.7 · #7 · `R_CHG_LED` 的转述与实跑不一致 (★已并进 d11★)★★

<!-- WPITEM:BEGIN id=#7 -->
① 项号: ★**#7** ★ (规格页 §11 附带发现 #7 · 吸收到 **d11** · 锚点组 `d11_*` · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**转述 (mech-lead ISS-213 的 need 原话)**: 「**网表 board 列标错 —— R_CHG_LED 两端分别标 CHG_BOARD 与 MAIN_PCB**」 ⇒ ★**★本单实测 (2026-11-16 01:5x, 本机实读)★**: 表A **L508** `P10,VBUS_5V_CHG,R_CHG_LED,U_CHG pin1,R_CHG_LED,1k ±1% (按 LED Vf 定),R,必装,[推算],,"★V1.9 充电灯 … 电阻把 **VBUS 供电** 接到 LED 阳极 …",C-01,CHG_BOARD,,` · **L509** `P10,LED_CHG_A,R_CHG_LED,D_CHG_LED,R_CHG_LED,1k ±1% (按 LED Vf 定),R,必装,…,C-01,CHG_BOARD,,` · **L510** (`D_CHG_LED`) `board=CHG_BOARD` · **L511** (`Q_CHG_LED`) `board=CHG_BOARD` ⇒ ★**★整条充电灯链全在 CHG_BOARD, 与该行 note「装在充电板 (镜框) 靠近 Type-C 座」完全一致 ⇒ 转述的这半句【不成立】★★**
★**【ISS-220 第 1 批已核验 · 2026-11-16】** ★核验命令实跑: 表A 里 `R_CHG_LED`/`D_CHG_LED`/`Q_CHG_LED` 的 board **全部 = `CHG_BOARD`** ⇒ ★**转述的『R_CHG_LED 两端分属两块板』被证伪, 本条一个字都没改 (别改坏它)★** ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**转述与实跑不一致 (T1 被证伪) ⇒ 照转述改会去动一个根本没坏的 `R_CHG_LED` (把 CHG_BOARD 改成 MAIN_PCB 才是真的改坏)⇒ "别人的转述不能当事实用" 是本项目反复吃过亏的地方★**
④ 真修法在哪个真源: ★**★无 (本条不落表)★** ⇒ ★**落表那趟必须按【本单实跑】的行号与 board 值改, 不按转述改 ⇒ 真源 = `state/gen_netlist.py` 的 `R_CHG_LED` / `D_CHG_LED` / `Q_CHG_LED` 段 (★确认没有被误改 board 列即可★)**
⑤ 改法 (逐字值): ★**★不改 (本条没有要改的地方)★** ⇒ ★**唯一动作: 落表那趟核一遍 `state/gen_netlist.py` 里 `R_CHG_LED` / `D_CHG_LED` / `Q_CHG_LED` 的 `add()` 没有把 board 弄成 MAIN_PCB (★现状是对的, 别改坏★)★** ⇒ ★**★把这条写进作业包是为了防"照转述改"★★ ★
⑥ 改完跑哪条命令: ★**★本条不落表 ⇒ 无★** ⇒ ★**核验命令 (只读)**: ★`python3 -c "import csv;rows=list(csv.reader(open('HW/netlist_v1.csv',encoding='utf-8')));print([(r[0],r[4],r[12]) for r in rows[1:] if r[4] in ('R_CHG_LED','D_CHG_LED','Q_CHG_LED')])"` ★ ⇒ ★**期望: 全部 `CHG_BOARD`★**
⑦ 翻面判据: ★**R11** ★ (★同域判据; ★★**"R_CHG_LED 的 board 保持 CHG_BOARD" 是 R11 的反向保护 (不许被改成 MAIN_PCB)★★**)
⑧ 证据等级: ★**[实测]** 表A L508-L511 逐字 (board 列逐条实读) · ★**[实测]** 转述原文 (mech-lead ISS-213 的 need) 与 main (2026-11-16 00:1x) 的实跑转述的逐条对照 (★T1 证伪 / T2 全对 / T3 描述不准: `C_VBUS_OUT` 与 `C_VBUS_GND` 是【两颗不同的电容】, 不是一颗的两端★) · ★**[推算]** "照转述改会改坏一个没坏的件" 的后果
<!-- WPITEM:END -->

### ★★§3.8 · #8 · `R_ILIM` note 里的 V1.7 残留 "470Ω" 与 value 的 390Ω 打架 (★已并进 d10★)★★

<!-- WPITEM:BEGIN id=#8 -->
① 项号: ★**#8** ★ (规格页 §11 附带发现 #8 · 吸收到 **d10** · 锚点组 `d10_*` · 翻面判据 **R10**)
② 现状逐字 + 行号: ★**表A `HW/netlist_v1.csv` L47 的 note 开头逐字**: `★"[IINLIM] ★★V1.7 按 ISS-091 结构核算定 **470Ω**: BQ25896 的 IINLIM 复位默认 **2048mA** [官方] (不装 = 铰链吃 ~1.68A); 结构总工核算 (MECH/HINGE_POWER_CALC.md, 可跑): **300Ω · ICHG 1.07A · 充电时皮肤侧 47.1°C 超 ISO 13732-1 的 43°C 红线** (加厚铜箔到 2oz 也只能到 45.2°C, 救不了); 470Ω · 0.68A · 39.9°C (充电 ~35min); 680Ω · 0.47A · 37.3°C. ★★★**V1.8 改 (老板 10-28 拍板『边戴边充不允许』)**: …"` ⇒ ★**而 L47 的 value = `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)`** ⇒ ★**★同一条 note 里两个档位 (470Ω 与 390Ω)★**
★**【ISS-220 第 1 批已落表 (并入 d10) · 2026-11-16】** ★`R_ILIM` 的 note 里 V1.7 那段 470Ω 残留已改成 `★★V1.7 (470Ω) 已作废 (V1.8 起改 390Ω; ★V1.9 终值待 V-4 裁决)★★` ⇒ ★**note 里不再有两个档位并排**★ ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**同一条 note 里残留了已被 V1.8 推翻的 V1.7 档位 "470Ω" ⇒ 读者不知道哪个是终值 (而 note 末尾还有 V1.9 又重复了一次 390Ω)★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**`R_ILIM` 那条 `add()` 的 `note` 字符串** ⇒ ★**与 d10 的 ④ 同源 (★同一处 note★)**
⑤ 改法 (逐字值): ★**把 V1.7 那句删掉, 或明确标"已作废"★**: ★`★★V1.7 按 ISS-091 结构核算定 **470Ω**: … 470Ω · 0.68A · 39.9°C (充电 ~35min); 680Ω · 0.47A · 37.3°C.`★ → ★`★★V1.7 (470Ω) 已作废 (V1.8 起改 390Ω, V1.9 终值见 V-4 裁决)★`★ ⇒ ★**或整段删除, 二选一, 不许留着两个档位并排★** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R10 必须转绿★)
⑦ 翻面判据: ★**R10** ★ (★同 d10: 规格页不再含 0.822 且含 1.216/1.071; 表A `R_ILIM` 的 value 不再含 "0.411A"; 单 pin ≤0.5A★) ⇒ ★★**"note 里不再出现 470Ω" 这一条目前没有独立 R# ⇒ 落表那趟建议顺手在 `state/check_netlist.py` 加一条 note 不含 "470Ω" 的断言 (★归落表那趟, 本单不改 check_netlist.py★)★★**
⑧ 证据等级: ★**[实测]** 表A L47 note 开头逐字 + L47 value 逐字 (本机实读) · ★**[推算]** "两个档位并排 ⇒ 读者无法判断终值" 的后果 · ★**[0数据]** V1.7 的 470Ω 当时是不是真做过 (★note 里保留了推导过程, 但推导本身有 470/680/300 三个候选⇒ 真值只有 V1.9 的 390Ω★)
<!-- WPITEM:END -->

---

## 4. ★★3 项补差 (★规格页 §11 里【还没被规格覆盖】的那几条★) ★★

### ★★§4.A · 补差A · `imp` 一个字段混着用 ⇒ 字段拆分方案 (★对应 #1 / d5★)★★

<!-- WPITEM:BEGIN id=补差A -->
① 项号: ★**补差A** ★ (规格页 §11 附带发现 #1 · 吸收到 **d5** · 锚点组 `d5_*` · 翻面判据 **R5**)
② 现状逐字 + 行号: ★**见 §3.1 #1 的 ② 栏 (57 条 connections 全表枚举)★** ⇒ ★**`imp` 现在承担 4 种语义: 差分线阻抗 20 条 / 串联电阻值 2 条 / 上拉阻值 2 条 / 空 11 条; `B-21`/`B-22` 把差分阻抗塞进串阻槽位★** · ★**落表侧现状**: `state/gen_netlist.py` L770-L781 的 `conn_row()`:
```python
def conn_row(by_id, cid, page, net, n1, n2, ref, value=None, note_extra=""):
    """把规格里的一条连接展开成 netlist 的 NET 行。
    value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)。"""
    c = by_id[cid]
    v = value if value is not None else (c.get("imp") or c.get("level") or "")
    ev = ev_of(c.get("level") or c.get("volt") or "", "[推算]")
    tbd = tbd_for((c.get("signal") or "") + " " + (c.get("conn") or ""))
    note = (f"方向 {c.get('dir','')}; 电平 {c.get('level','')}; 阻抗 {c.get('imp','')}; "
            f"连接 {c.get('conn','')}; 测试点 {c.get('tp','')}")
    if note_extra:
        note = f"[{net}] {note_extra}; " + note
    add(page, net, n1, n2, ref, v, "NET", dnp_of(c.get("dnp", "")), ev, tbd, note, cid)
```
★**【ISS-220 第 1 批已落表 (字段基建部分) · 2026-11-16】** ★`z_diff` 字段已加进 57 条 connections · `conn_row()` 的 2 行已改 (`imp` → `z_diff` → `level` 优先级) ⇒ ★**净效果 = 网表产物逐字节不变 (A 组 20 条 NET 行仍 `100Ω ±10%`, B 组 4 条仍原值, C 组 11 条仍落 `level`)★** ⇒ ★**B-21/B-22 的 `imp` 迁移 (22Ω 串阻 vs 0Ω) 仍 BLOCKED 于 V-1**★ ⇒ 逐条见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★
③ 缺陷一句话: ★**NET 行的"阻抗"与器件行的"阻值"在 DSI 组是两个不同的物理量 (NET 行 100Ω = MIPI 差分阻抗 / 器件行 0Ω = 直通位), 在 USB 组却被塞进同一个字段 (`imp`) ⇒ 两个物理量混用 ⇒ 同一颗器件出现两个阻值 (d5) ⇒ 模板必须分字段, 不是改一个数★**
④ 真修法在哪个真源: ★**① `HW/SCHEMATIC_V1_SPEC.json`** ★**`connections[]` 每一条新增键 `z_diff`** ⇒ ★**② `state/gen_netlist.py`** ★**`conn_row()` (★现 L770-L781★) 的取值优先级与 note 模板** ⇒ ★**③ `HW/check_netlist_selfconsistency.py`** ★**R5 的判据 (★不需要改, 拆完 R5 仍然按"串阻口径"判★) + EXPECT 里 `d5_spec_b21_imp` / `d5_spec_b22_imp` 的现状断言 (★落表那趟改★)**
⑤ 改法 (逐字值) — ★**★字段拆分方案 (完整版)★**:
★★**① 字段名 (建议)★★
| 字段 | 语义 | 单位 | 谁用 |
|---|---|---|---|
| ★**`imp`** ★ | ★**串接电阻 / 上拉电阻的【器件侧】阻值** (★"这颗电阻多大"★) ★ | Ω (可带 ±%) | ★**器件行 `value`; NET 行 value (当该段是串阻位时) ★** |
| ★**`z_diff`** ★ | ★**差分线受控阻抗** (★"这根差分对的线阻抗多少"★, 板级) ★ | Ω (可带 ±%) | ★**NET 行 value (当该段是差分对时) + note 的"阻抗"栏 ★** |
| ★**`level`** ★ | ★**电平 (不变)** ★ | V | 不变 |
| ★**`imp_note`** ★ | ★**(可选) 补充说明, 例如 "源端匹配" / "磁珠后级体电容" / "直通位" ★ | 文本 | ★**`conn_row()` 的 note 追加, 用来承载"这句串阻/阻抗是干什么的"★**

★★**② 哪些连接填哪个 (逐条清单)★★
| 组 | id | 现状 `imp` | 拆完后 | `z_diff` |
|---|---|---|---|---|
| ★A (CSI) ★ | `A-01`~`A-10` (idx[0]~idx[9]) | `100Ω ±10%` | ★`imp` → ★**清空** (器件侧无串阻) ★ | ★`100Ω ±10%` (★不动★) ★ |
| ★A (DSI) ★ | `A-13`~`A-22` (idx[12]~idx[19] + idx[55] + idx[56]) | `100Ω ±10%` | ★`imp` → ★**清空** ★ | ★`100Ω ±10%` (★不动★) ★ |
| ★B (单端串阻) ★ | `B-09` (FSIN, idx[28]) | `单端, 50Ω 串阻` | ★**保留** (串阻语义) ★ | ★**清空** ★ |
| ★B (单端串阻) ★ | `B-19` (JTAG, idx[38]) | `单端, 100Ω 串阻` | ★**保留** ★ | ★**清空** ★ |
| ★B (上拉) ★ | `B-01` / `B-02` (idx[20]/idx[21]) | `上拉 4.7k 到 3.3V …` | ★**保留** (上拉语义; ★落表同时按 d1 改成 2.2k/1.8V★) ★ | ★**清空** ★ |
| ★B (USB) ★ | `B-21` / `B-22` (idx[40]/idx[41]) | `90Ω ±10% …` | ★**改成串阻值** (★按 d5: `22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)`★) ★ | ★**新增 `90Ω ±15% 受控阻抗`** ★ |
| ★C (充电/电源页) ★ | `C-01`~`C-11` (idx[44]~idx[54]) | `None` | ★**不动** ★ | ★**不动** ★ |

★★**③ `state/gen_netlist.py` 的 `conn_row()` 改动面 (★只有 2 行, 极小★)★★
```
-    v = value if value is not None else (c.get("imp") or c.get("level") or "")
+    v = value if value is not None else (c.get("imp") or c.get("z_diff") or c.get("level") or "")
```
```
-            f"方向 {c.get('dir','')}; 电平 {c.get('level','')}; 阻抗 {c.get('imp','')}; "
+            f"方向 {c.get('dir','')}; 电平 {c.get('level','')}; 阻抗 {c.get('imp') or c.get('z_diff','')}; "
```
⇒ ★**★改动面评估: `conn_row()` 在 `state/gen_netlist.py` 里被调用 22 次; 改这 2 行 ⇒ ① A 组 20 条 NET 行的 value 仍是 `100Ω ±10%` (★因为 `imp` 清空后由 `z_diff` 顶上 ⇒ 产物逐字节不变★) ② B 组 4 条 (B-09/B-19/B-01/B-02) 不变 (★`imp` 保留, 且 `imp` 优先于 `z_diff`★) ③ B-21/B-22 的 value 变成 d5 定的串阻串 ④ C 组 11 条 `imp=None` 且 `z_diff=None` ⇒ 仍落到 `level` ⇒ 不变 ⇒ ★**⇒ 净效果 = 只有 B-21/B-22 两条的 NET 行 value 变了, 其余 20 条 A 组与 4 条 B 组产物逐字节不变****
⇒ ★**★`state/gen_netlist.py` 里另外 22 处 `conn_row()` 调用点【一个字都不用改】⇒ 改动面 = 2 行 / 1 个文件★★**

★★**④ 迁移清单 (哪几行要改, 逐条)★★
| # | 文件 | 定位 | 改什么 |
|---|---|---|---|
| 1 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[0]`~`connections[9]` (A-01~A-10) | ★新增 `"z_diff": "100Ω ±10%"`; `imp` 改为 `""` ★ |
| 2 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[12]`~`connections[19]` + `connections[55]` + `connections[56]` (A-13~A-22) | ★同上 ★ |
| 3 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[40]` (B-21) | ★`imp` → `"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)"`; 新增 `"z_diff": "90Ω ±15% 受控阻抗"` ★ |
| 4 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[41]` (B-22) | ★同上 ★ |
| 5 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[28]` (B-09) / `connections[38]` (B-19) / `connections[20]`/`[21]` (B-01/B-02) | ★**只加一个显式的 `"z_diff": ""` (可省略, 但显式写出来便于机器判"这个槽位是空的")** ★ |
| 6 | ★`state/gen_netlist.py`★ | `conn_row()` L774 与 L777 | ★**2 行改法见上 ③** ★ |
| 7 | ★`HW/check_netlist_selfconsistency.py`★ | `EXPECT` 的 `d5_spec_b21_imp` / `d5_spec_b22_imp` | ★**现状断言在落表那趟改成落表后的 `imp` (★门禁 R5 不用改★) ★** |
| 8 | ★`HW/check_netlist_selfconsistency.py`★ | `EXPECT` 的 `d1_spec_b01_imp` / `d1_spec_b02_imp` | ★**落表那趟按 d1 改成 2.2k/1.8V 口径 (★与字段拆分互不冲突★) ★** |

★★**⑤ 改完后 `python3 state/check_netlist.py` 与 `python3 state/check_netlist_pins.py` 应该是什么结果★★
| 命令 | 期望 rc | 期望输出 | 为什么 |
|---|---|---|---|
| ★`python3 state/check_netlist.py`★ | ★**0** ★ | ★**"✅ 全过 — 原理图 V1.1 可进交叉评审"** ★ | ★**该脚本的判据 5 是 "A 组阻抗必须与规格逐字一致" ⇒ A 组 20 条 NET 行的 value 仍是 `100Ω ±10%`, 与 `z_diff` 逐字一致 ⇒ 判据仍成立 (★拆字段不改变任何 A 组产物★) ★** |
| ★`python3 state/check_netlist_pins.py`★ | ★**0** ★ | ★**"✅ 全过 —— 每个针脚归属唯一, 连接器针数与针号齐, SoC 节点全部落到真实引脚"** ★ | ★**脚表不含 `imp` 字段, 拆分对它零影响; 但 ★**B-21/B-22 的 NET 行 value 变了 ⇒ 脚表派生出来的 note/value 若含该串会跟着变 ⇒ 这属于预期, 不影响"脚行归属唯一"这条判据**** |
| ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved`★ | ★**1 (落表前)** ★ → ★**0 (落表后)** ★ | — | ★**R5 ★** |
| ★**落表后的 md5 变化预期** ★ | — | — | ★**★只有 `HW/netlist_v1.csv` 的 L291/L292 两行 value 变 (90Ω → 22Ω 串阻串), 且 `HW/netlist_v1_pins.csv` 的对应 note 随之变; 脚表其余行、BOM、板的**其他部分**不变 ⇒ md5 必然变, 但变化范围可逐行核对****

⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R5 必须转绿★) ⇒ ★**★若同时落 d1 (B-01/B-02) ⇒ `check_netlist.py` 的 A 组/B 组阻抗判据仍全过 (★A 组 `imp` 清空后由 `z_diff` 顶上, B-01/B-02 的 `imp` 保留且已改成 2.2k/1.8V 口径★★) ★**
⑦ 翻面判据: ★**R5** ★ (★`--expect-resolved` 的 R5 段: NET 行 value 不含 "90Ω" 且含 "22Ω"; SPEC.json B-21/B-22 的 `imp` 不含 "90Ω" 且含 "22Ω"★) ⇒ ★**★"字段真的拆开了"这一条目前没有独立 R# ⇒ 落表那趟建议在 `state/check_netlist.py` 加一条"A 组 20 条必须有 `z_diff` 且 `imp` 为空"的断言 (★归落表那趟, 本单不改 check_netlist.py★)★★**
⑧ 证据等级: ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` 57 条 connections 全表枚举 (本单自跑) + `state/gen_netlist.py` L770-L781 逐字 + `conn_row()` 调用点 22 处 (本机 grep 计数) + 表A 20 条 A 组 NET 行 value 逐条实读 · ★**[推算]** "改动面 = 2 行 / 1 个文件, 且 A 组 20 条产物逐字节不变" 的推导 · ★**[实测]** `state/check_netlist.py` 与 `state/check_netlist_pins.py` 的当前 rc=0 与输出原文 (本机实跑)
<!-- WPITEM:END -->

### ★★§4.B · 补差B · 门禁 R9 的翻面阈值 5.0 → 3.0 + 反向用例 (★对应 #3 / d9★)★★

<!-- WPITEM:BEGIN id=补差B -->
① 项号: ★**补差B** ★ (规格页 §11 附带发现 #3 · 吸收到 **d9** · 锚点组 `d9_*` · 翻面判据 **R9**)
② 现状逐字 + 行号: ★**`HW/check_netlist_selfconsistency.py` 现 R9 段逐字**:
```
    # ---- R9: ESD 必须真的贴到 J_USB_C (≤5mm) ----
    import math as _math
    xy = _board_ref_xy(_path(root, "board"))
    if "J_USB_C" in xy and "D_ESD_USB_D" in xy:
        a, b = xy["J_USB_C"], xy["D_ESD_USB_D"]
        d = _math.hypot(a[0] - b[0], a[1] - b[1])
        if d > 5.0:
            errors.append(
                f"★R9 未落表: D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm > 5 mm "
                f"⇒ ESD 还是不在接口旁边")
```
★**现状断言 (不动) 逐字**: `('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5'),` ★**另一处口径**: `state/gen_schematic_pages.py` P9 页 `④ **ESD 距连接器 ≤3.0mm**` (ISS-085) ★**规格页 §5.2 口径**: `≤ 5 mm` ⇒ ★**★两个口径并存 ⇒ 落表验收判据不唯一★**
③ 缺陷一句话: ★**ISS-211 §5.2 写 ≤5mm, 而 `state/gen_schematic_pages.py` P9 页自引的 ISS-085 结构总工回执写 ≤3.0mm ⇒ 按 3.0mm 判 (项目自己的规矩, 更严) ⇒ 门禁的翻面阈值必须从 5.0 改成 3.0★**
④ 真修法在哪个真源: ★**`HW/check_netlist_selfconsistency.py`** ★**R9 翻面判据的阈值** ⇒ ★**★只改【翻面判据】, 【现状断言】不动 (★现状 47.99mm 无论 5 还是 3.0 都判"缺陷仍在"★) ★** ⇒ ★**★真正的做法是: 把阈值收进一个【有名字的常量】, 让它可被反向用例读到并验证, 而不是散落的字面量★★**
⑤ 改法 (逐字值): ★**① 在 `HW/check_netlist_selfconsistency.py` 的常量区 (★`ETA_BUCK` / `VBUS_CHG` / `KILIM_MAX` 旁, 现 L111-L113★) 加一行**:
```
ESD_MAX_DIST_MM = 3.0    # ★ESD 距 J_USB_C 的【翻面】阈值 (★按 state/gen_schematic_pages.py P9 页
                         #   自引的 ISS-085 结构总工回执『ESD 距连接器 ≤3.0mm』; ISS-211 §5.2 的
                         #   5mm 口径作废 ⇒ 按项目自己的规矩取更严的 3.0)★
```
★**② R9 段把字面量换成常量 (★只改这一处★)**:
```
    # ---- R9: ESD 必须真的贴到 J_USB_C (≤3.0mm, ★ISS-085 口径; 原 5.0mm 作废★) ----
    ...
        if d > ESD_MAX_DIST_MM:
            errors.append(
                f"★R9 未落表: D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm > {ESD_MAX_DIST_MM} mm "
                f"⇒ ESD 还是不在接口旁边")
```
★**③ 现状断言一条字都不许动**: `('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5')` 保持原样 ★
★**④ `--selftest` 加一条反向用例 (★本单已落, 见 ⑥ 的说明与 `HW/check_netlist_selfconsistency.py` 里的 `m_esd_threshold_5mm` 用例★)**: ★**做法 = 把板上的 `D_ESD_USB_D` 挪到距 `J_USB_C` **4.0 mm** 处 (★4.0 落在 3.0 与 5.0 之间 ⇒ 正好能区分两个阈值★) ⇒ 真实脚本 (阈值 3.0) 必须报 R9 未落表; 再把脚本副本里的常量改回 `5.0` ⇒ 同一块板必须【不】报 R9 ⇒ ★**⇒ 两条断言同时成立 = "阈值真被读到 3.0 而不是 5.0" 被证明; 谁把常量改回 5.0 ⇒ 第二条断言立刻失败 ⇒ 变红****
⑥ 改完跑哪条命令: ★`python3 HW/check_netlist_selfconsistency.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --selftest` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★期望 rc = 0 / 0 / 1★)
⑦ 翻面判据: ★**R9** ★ (★`--expect-resolved` 的 R9 段: `D_ESD_USB_D` → `J_USB_C` 板面距离 **≤ 3.0 mm**★)
⑧ 证据等级: ★**[实测]** 门禁 R9 原码逐字 (本机实读 L1037-L1050) + `EXPECT` 里 `d9_esd_dist` 逐字 + `state/gen_schematic_pages.py` P9 页 `≤3.0mm` 逐字 + 规格页 §5.2 `≤ 5 mm` 逐字 + 板面实测 47.99mm · ★**[实测]** 新增反向用例跑通 (本机实跑 `--selftest` ⇒ 17/17 全过, ★原 16 条一条没删★) · ★**[推算]** "4.0mm 是能区分 3.0 与 5.0 的判别距离" 的构造
<!-- WPITEM:END -->

### ★★§4.C · 补差C · 充电链 π 滤波拓扑真值规格 + `J_CHG` 位号消歧方案 (★对应 #4 / #6 / d11★)★★

<!-- WPITEM:BEGIN id=补差C -->
① 项号: ★**补差C** ★ (规格页 §11 附带发现 #4 / #6 · 吸收到 **d11** · 锚点组 `d11_*` · 翻面判据 **R11**)
② 现状逐字 + 行号: ★**π 滤波侧**: 表A L9 (`C_VBUS_OUT` = `VBUS_5V_F1` ↔ `C_VBUS_OUT`, board=CHG_BOARD) + L11 (`C_VBUS_OUT` = `C_VBUS_OUT` ↔ `U_CHG pin1`, note 逐字 `π 滤波电容 (后级, 串联) 位`) ⇒ ★**100µF 串联在 DC 输入路径上**; L10/L12 `C_VBUS_GND` = 对地 100µF 但 board 列 = `MAIN_PCB` (★见 d11★); `HW/CHARGE_BOARD_SPEC.md` §7 用的是 `C_VBUS_BULK` (对地) 而网表里没有这个位号; §7.1 对账表 `| 本清单总行数 | — | **80** | CHG_BOARD 65 / MAIN_PCB 4 / HINGE 11 |` ⇒ ★**"现行网表引用 80 行"已过期★** · ★**`J_CHG` 侧**: 表A L497 = `1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)` board=`HINGE`; 板文件 `J_CHG` = `SoM BTB CHG (100pin, 部分已分配)` pads=2 (pin1=`BAT_CHG` / pin6=`PWR_GOOD`) ⇒ ★**同一个位号指两个物理件★**; P9 页 J_CHG pinmap 逐字 `pin1/pin2 = **充电电流 1.0-1.5A 双 pin 并联** · pin3/pin4 = 回流双 pin · pin5 = CHG_STAT · pin6 = PWR_GOOD · pin7 = VBUS_DET · pin8-10 = 预留` ⇒ ★**与网表对不上 (网表: 7=`NC` / 8=`TS_BAT`, 且没有 5/6 的行)★**
③ 缺陷一句话: ★**① π 滤波拓扑: 网表把 100µF 放在【串联】位 (稳态充不了电), 规格 §7 用的是【对地】位号 `C_VBUS_BULK` (网表里根本没有这个位号) ⇒ 拓扑与位号两处不一致; ② `J_CHG` 一个位号指两个物理件 (网表 = 铰链 FPC 10p / 板 = SoM BTB 100pin) ⇒ 装配/备料/结构三方各按各的理解走 ⇒ 会备错件★**
④ 真修法在哪个真源: ★**π 滤波侧**: ★**`HW/CHARGE_BOARD_SPEC.md`** ★**§4.2 (L363 `C_VBUS_BULK` 行 + 两条注记) + §7 (L516/L517/L519) + §7.1 对账表** + ★**`state/gen_netlist.py`** ★**`C_VBUS_OUT` / `C_VBUS_GND` 两条 `add()`** ⇒ ★**`J_CHG` 侧**: ★**`state/gen_netlist.py`** ★**`J_CHG` 那条 `add()` 的 `ref` + `HINGE_REFS` (★现 L117★) + `state/gen_schematic_pages.py` P9 页 pin map 行** ⇒ ★**★真值真源 = TI BQ25896 datasheet 的输入去耦原话 ("put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND") + `HW/CHARGE_BOARD_SPEC.md` §4.2 的顺序规则 (Type-C → ESD → 磁珠 → 体电容 → BQ25896 VBUS 脚)★** ⇒ ★**★充电板不进 demo 板 ⇒ 本单只出规格, 不碰网表也不碰板 (★归 V-7 / ISS-199 / ISS-202★)★**
⑤ 改法 (逐字值) — ★**π 滤波真值拓扑规格 (完整版)★**:
| # | 位号 (建议) | 值 | 连接 (对地/串联) | 容量判据 | 依据 |
|---|---|---|---|---|---|
| ★1 ★ | ★`FB_VBUS`★ | ★磁珠, 额定 **≥2A**, DCR ≤50mΩ, Z@100MHz 100-600Ω★ | ★**串联** (USB_VBUS_RAW → VBUS_5V_ESD → VBUS_5V_F1)★ | ★**必须排在 ESD 之后** (ESD 要直接泄放到地, 走线越短钳位越准) ★ | ★`HW/CHARGE_BOARD_SPEC.md` §4.2 逐字★ |
| ★2 ★ | ★`C_VBUS_IN`★ | ★10µF X7R 25V★ | ★**对地** (VBUS_5V_ESD → GND)★ | ★磁珠前级体电容 ★ | ★同 §4.2★ |
| ★3 ★ | ★`C_VBUS_BULK`★ | ★100µF X7R 10V★ | ★**对地** (VBUS_5V_F1 → GND)★ | ★**BQ25896 输入体电容, 放在磁珠后级 / 上游** (★官方: 其余容值放 PMID, 故 100µF 放 VBUS 脚上游; 上电浪涌由内部 RBFET 承受★) ★ | ★同 §4.2 + BQ25896 原话★ |
| ★4 ★ | ★`C_VBUS_IC`★ | ★1µF X7R 25V★ | ★**对地** (VBUS 脚 pin1 → PGND)★ | ★**官方强制**: "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" ⇒ **必须贴 IC** ★ | ★BQ25896 原话 (★`CHARGE_BOARD_SPEC.md` L115 已逐字引用★)★ |
| ★5 ★ | ★`C_PMID`★ | ★10µF X7R 25V★ | ★**对地** (PMID → PGND)★ | ★**官方强制**: "the rest capacitance on PMID to PGND" ⇒ **不可省** ★ | ★BQ25896 原话 ★ |
| ★6 ★ | ★`C_BST` / `C_REGN` / `C_SYS` / `D_TVS_VBUS` ★ | 47nF / 4.7µF / 20µF / TVS | 按 §7 清单 | 各自官方口径 | ★§7★ |
| ★**✘** ★ | ★**串联 100µF (网表现状 `C_VBUS_OUT`)** ★ | — | ★**✘ 不许有**★ | ★**★100µF 电容串在 BQ25896 的 DC 输入路径上 ⇒ 稳态直流不通 ⇒ 充不了电 (整机阶段 P0)★ ⇒ 网表里的 `C_VBUS_OUT` 串联位必须去掉, 位号统一成 `C_VBUS_BULK` (对地)★** | ★**[推算] 直流串联电容阻抗 → ∞★** |

⇒ ★**★π 拓扑一句话 (落表那趟照抄)★**: ★**`Type-C → D_ESD_TC → FB_VBUS → {C_VBUS_BULK(100µF 对地) + C_VBUS_IC(1µF 对地, 贴 IC)} → U_CHG pin1 (VBUS)`; `U_CHG pin23 (PMID) → {C_PMID(10µF 对地)}`; 全链【没有串联电容】★**

⇒ ★**`J_CHG` 位号消歧方案 (完整版)★**:
| 项 | 内容 |
|---|---|
| ★**现状冲突** ★ | ★网表 `J_CHG` = 铰链 FPC 座 `1×10p@0.5mm` (board=HINGE, 框侧座+脚侧座一对, ISS-099 回执); 板文件 `J_CHG` = `SoM BTB CHG (100pin, 部分已分配)` (只有 2 个焊盘: pin1=BAT_CHG / pin6=PWR_GOOD) ★ |
| ★**方案 (建议)** ★ | ★**网表侧改名: 铰链 FPC 座 `J_CHG` → `J_CHG_FPC`; 板侧 SoM BTB 保留 `J_CHG`** ★ |
| ★**理由** ★ | ★① 板文件里的 SoM BTB (100pin) 是 SoM 厂给定接口 ⇒ 改它的位号要牵动板 + 丝印 + CPL + 投产包 + 盖印; ② 网表侧的 10p FPC 座是本项目自己的件, 改名成本低 (只动网表/脚表/BOM + 生成器白名单) ★ |
| ★**改哪些地方** ★ | ★① `state/gen_netlist.py` 的 `J_CHG` 那条 `add()` 的 `ref`/`value`; ② `state/gen_netlist.py` L117 `HINGE_REFS = {"J_CHG"}` → `{"J_CHG_FPC"}`; ③ `state/gen_netlist_pins.py` 的引用; ④ 表A/表B/BOM 的位号; ⑤ 板 (脚侧那一侧; 框侧 SoM BTB 不动); ⑥ `state/gen_schematic_pages.py` P9 页 J_CHG pin map 那一行; ⑦ `HW/CHARGE_BOARD_SPEC.md` §7 里的 `J_CHG` 行 (★C-03 那几行★) ★ |
| ★**对 ISS-199 / ISS-202 的影响** ★ | ★① ISS-199 (铰链结构): 结构侧要按 `J_CHG_FPC` 开孔与固定; ② ISS-202 (J_CHG pinmap): ★**P9 页的 pin map (5=CHG_STAT / 6=PWR_GOOD / 7=VBUS_DET) 与网表对不上 (网表 7=NC / 8=TS_BAT, 且没有 5/6 的行) ⇒ 改位号那一趟必须一并把 pin map 逐脚对齐网表★; ③ ★**V-4 的解② (J_CHG 载流 pin 从 2 只加到 4 只 pin1/2/9/10) 若被选中 ⇒ 改名与加 pin 必须同一趟, 否则白改两遍★** |
| ★**降级方案** ★ | ★**若结构/主板侧来不及改位号 ⇒ 先在网表 note 里写死一句话消歧**: ★`"[J_CHG] ★★本位号在网表 = 铰链 FPC 座 1×10p@0.5mm; 板文件里的 J_CHG 是 SoM BTB 100pin (SoM 厂给定接口) ⇒ 两者不是同一个件; 改名方案待 ISS-199/202"★ ⇒ ★**但这只是权宜: 板厂/装配厂仍会看到同一个位号 ⇒ 最终必须改名★** ★ |
| ★**★不许做的事** ★ | ★**不许把板侧的 SoM BTB 改名去迁就网表 (板是 SoM 厂接口, 改名牵动盖印/投产包)⇒ 也不许两处都叫 `J_CHG` 继续下去 ⇒ 这条不做, 备料会备错件★** ★

⑥ 改完跑哪条命令: ★**★本条不在本单落表范围 (★充电板整机阶段 + ISS-199/202 地界★)★** ⇒ ★**若 main 派单落充电板 π 滤波**: ★`python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` → `python3 state/check_netlist.py` → `python3 state/check_netlist_pins.py` → `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ ⇒ ★**若走 ISS-199/202 的改名**: ★`python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` → `python3 state/gen_pcb_components.py` → `python3 state/gen_pcb_netlist_board.py` → `python3 state/check_netlist.py` → `python3 state/check_netlist_pins.py` → `python3 state/check_kicad_net.py`★ ★
⑦ 翻面判据: ★**R11** ★ (★同域判据: 充电板本地网 board 列一致性 + 板侧封装归属; ★★**"π 滤波不得有串联 100µF" 与 "J_CHG 位号不再双义" 这两条本单没有独立 R# ⇒ 落表那趟需要新加机器判据 (★归 main 派单的单 + ISS-199/202★)★★**)
⑧ 证据等级: ★**[实测]** 表A L9-L13 / L497 逐字 + 脚表 L148/L149/L154/L155 + 板文件 `J_CHG` / `C_VBUS_GND` / `C_VBUS_OUT` 封装实读 + `HW/CHARGE_BOARD_SPEC.md` §4.2 (L363) / §7 (L516/L517/L519) / §7.1 逐字 + `state/gen_netlist.py` L117 (`HINGE_REFS`) 逐字 + P9 页 J_CHG pin map 逐字 · ★**[官网]** BQ25896 "put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND" / "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" · ★**[推算]** "100µF 串联 ⇒ 稳态充不了电" + "白名单驱动 ⇒ 同型缺陷会持续漏" + 改名影响面清单 · ★**[0数据]** J_CHG 对插器 (框侧座 + 脚侧座) 的确切型号 / 充电板实物
<!-- WPITEM:END -->

---

## 5. ★★6 条待裁确认单 (★V-1 ~ V-6 · 一句话可勾选 · 不许代拍★) ★★

★★**★本节只出"勾选单 + 默认值 + 备选 + 代价 + 落表后影响哪几行" ⇒ 签字权在项目总工 / 老板, 本单一律不代拍★**
★★**★V-7 / V-8 不在本单 6 条里 (★V-7 = main 派单的充电板整机阶段单; V-8 = ISS-199/202 地界) ⇒ 见 §4.C 补差C 的规格与 §6 的 need 登记★★**

### ★★§5.1 · 待裁V-1 · USB 串阻: 22Ω 外部串阻 还是 0Ω 靠 SoM PHY 内部匹配?★★

<!-- WPITEM:BEGIN id=待裁V-1 -->
① 项号: ★**待裁V-1** ★ (规格页 §13 V-1 · 吸收到 **d5** · 锚点组 `d5_*` · 翻面判据 **R5**)
② 现状逐字 + 行号: ★**表A L431/L432** 器件行 `R_SER_USB_D_P` / `R_SER_USB_D_N` 的 value = ★`22Ω ±1%`★ (★现行网表已经按 22Ω 装★) · ★**表A L291/L292** NET 行 value = ★`90Ω ±10% (与 MIPI 不同模板!)` / `90Ω ±10%`★ (★错的那些★) · ★**规格页 §13 V-1 逐字**: 「★**USB 串阻最终取 22Ω 外部串阻, 还是 0Ω (靠 SoM PHY 内部匹配)?** ★」· ★**`HW/EMC_PRECHECK.md:211`** `D+/D- 90 Ω 差分, 480 Mbps` ⇒ ★**线阻抗口径已定, 只差串阻这一档★**
③ 缺陷一句话: ★**不是缺陷, 是【纯工程取舍】—— 外部串阻取 22Ω 还是 0Ω, 决定 SoM PHY 的驱动匹配与眼图余量, 而 SoM (Forlinx) 手册项目库里没有 ⇒ 必须有人拍★**
④ 真修法在哪个真源: ★**`HW/SCHEMATIC_V1_SPEC.json`** ★**`connections[40]` (B-21) / `connections[41]` (B-22) 的 `imp` 键** ⇒ ★**★改一个字段就行, 但取 22 还是 0 要拍★ (★规格页 §13 原话★) ★** ⇒ ★**器件侧的 `R_SER_USB_D_P` / `R_SER_USB_D_N` 两条 `add()` (★`state/gen_netlist.py`★) 的 `value` 随裁决同步★
⑤ 改法 (逐字值): ★**☐ 默认值: 外部串阻 `22Ω ±1%`** (★推荐★) ⇒ `connections[40]/[41]` 的 `imp` = ★`"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)"`★ · ★**☐ 备选: `0Ω` (靠 SoM PHY 内部匹配)** ⇒ `imp` = ★`"0Ω 直通位 (靠 SoM PHY 内部匹配; ★★待 SoM 手册确认★★)"`★ ⇒ ★**不管选哪个, `z_diff` = `90Ω ±15% 受控阻抗` 都要补上 (★见 §4.A★)★** · ★**落表后影响哪几行**: ★**表A L291/L292 (NET 行 value, 由生成器自动) + L431/L432 (器件行 value, 按裁决写 `22Ω ±1%` 或 `0Ω ±1%`) + SPEC.json connections[40]/[41] 的 `imp` + 脚表对应 4 行的 value/note + BOM `R_SER_USB_D_P` / `R_SER_USB_D_N` 两行★**
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★
⑦ 翻面判据: ★**R5** ★ (★NET 行 value 不含 "90Ω" 且含 "22Ω"; ★**若裁 0Ω ⇒ R5 的"含 22Ω"这一条要同步改成"含 0Ω 或 22Ω" ⇒ 落表那趟改 EXPECT★** ★)
⑧ 证据等级: ★**[实测]** 表A L291/L292/L431/L432 + `SCHEMATIC_V1_SPEC.json` connections[40]/[41] + `EMC_PRECHECK.md:211` 逐字 · ★**[官网]** ON Semi **AND8074/D** (USB 1.1 规范要求串阻 28~44Ω; 工业主流 22Ω 或 30Ω) · onsemi **STF202-22T1G** datasheet (内置 RS nom 22Ω ⇒ 官方也有 22Ω 的现成件) · ★**[推算]** "90Ω 串在 90Ω 线上 ⇒ 摆幅减半" ⇒ **无论裁 22 还是 0, 90Ω 那个错值都必须清掉** · ★**[0数据]** SoM USB PHY 的驱动阻抗 / 外部串阻是否必需 / abs-max ⇒ **这是本条唯一的外部依赖, 但不阻塞落表 (⇒ 降级: 先按 22Ω 落, SoM 手册到手后只核对"驱动阻抗"一条, 不用重算分压比/阻抗****
<!-- WPITEM:END -->

### ★★§5.2 · 待裁V-2 · ESD 方案二选一 + 型号 (★选型 = 老板级, 本单不代拍★)★★

<!-- WPITEM:BEGIN id=待裁V-2 -->
① 项号: ★**待裁V-2** ★ (规格页 §13 V-2 · 吸收到 **d9** · 锚点组 `d9_*` · 翻面判据 **R4 + R9**)
② 现状逐字 + 行号: ★**表A L417** `D_ESD_USB_D` value = ★`ESD 阵列 [待选型] (USB 2.0 双通道)`★, `type=D`, `dnp=必装`, net=`USB_D_P_SRC` (★串阻的 SoM 侧★) · ★**L418** 地端 · ★**板文件**: pads=**2**, pad1→`USB_D_P_SRC` / pad2→`GND`, 原点 (94.95, 21.8) ⇒ 距 `J_USB_C` (140.0, 5.25) ★**47.99 mm**★ · ★**板上挂 `USB_D_N_SRC` / `NET_USB_D_N_TYPEC` 的 ESD 位号 = 0 个★** · ★**规格页 §13 V-2 逐字**: 「★**ESD 方案二选一 (① 3 脚双通道阵列 / ② 2 只单通道) + 型号 (≤1pF/线 / Vclamp ≤8V / IEC level 4) + ★★D− 侧选型★★** ★」
③ 缺陷一句话: ★**不是缺陷, 是【选型】—— 老板级; 本单只给"官网参数满足的候选 + 判据串 + 查不到的降级方案", 不许代拍★**
④ 真修法在哪个真源: ★**① 型号写进 `state/gen_netlist.py`** ★**USB ESD 段的 `value` (★落表那趟填★)** + ★**② 封装进板封装库 (★`state/gen_pcb_components.py` 的 footprint 表★)** + ★**③ 方案二选一影响网表行数: 方案① = 3 条 `add()` (一只 3 脚件) / 方案② = 4 条 `add()` (两只 2 脚件) ⇒ ★**两条路的【共同底线】不变: ESD 必须从 `USB_D_P_SRC` (SoM 侧) 挪到 `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` (Type-C 侧), 否则等于没护★**
⑤ 改法 (逐字值) — ★**★官网参数满足判据的候选 + 判据串 + 降级方案 (不代拍)★**:
★★**候选 (官网参数直接满足判据, 本单已逐条核对)★★
| 候选 | 通道 | 结电容/线 | Vclamp | IEC 61000-4-2 | 封装 | 官方依据 |
|---|---|---|---|---|---|---|
| ★**TI TPD2EUSB30** ★ | ★**2ch (D1+/D1−)** ★ | ★**0.7 pF typ** (DRT) ★ | ★**8 V @ 1 A** ★ | ★**level 4 contact (8 kV)** ★ | ★**SOT-3 (DRT) 1.00×0.80 mm** ★ | ★TI datasheet **SLVSAC2G** ★ |
| ★**TI TPD2EUSB30A** ★ | 2ch | 0.7 pF typ | 8 V @ 1 A | level 4 contact | SOT-3 / DQA 0.8 pF typ | TI SLVSAC2G |
| ★**TI TPD4EUSB30** ★ | ★**4ch (D+/D−/VBUS/1 备用)** ★ | 0.8 pF typ (DQA) | 8 V @ 1 A | level 4 contact (★air 9 kV★) | DQA 2.5×1.0 mm | TI SLVSAC2G |
| ★**onsemi STF202-22T1G** ★ | — | ★**68 pF** ★ | — | — | — | ★**✘ 排除项 (见下)★** ★

★★**判据串 (6 条, 缺一条不许选型; 落表时逐字写进 `value`)★★
`ESD 阵列 (USB 2.0 双通道, D+/D− 共用一颗, ≤1.0pF/线, V_clamp ≤8V@1A, IEC 61000-4-2 level 4 contact 8kV, SOT-3 3脚)`

★★**★排除项 (必须写进规格, 防止下一次又选错)★★
⇒ ★**onsemi STF202-22 这类"滤波 + 端接 + ESD"三合一集成件, 在本项目里被明确排除** ⇒ ★**[官网] STF202-22T1G datasheet (Rev 11, 2025-03) 的 `Typical Line Capacitance (pF) … **68**` (25℃, 1 MHz) ⇒ 68 pF 是 USB 【全速 12 Mbps】 级量级 ⇒ 用在 480 Mbps 高速差分线上会直接毁眼图 ⇒ ★**选型必须看"线电容"而不是只看"IEC 等级"★** ⇒ ★**(但它的内置串阻 RS = 20/22/24Ω 恰恰是 V-1 的官方旁证 ⇒ 两个官方件指向同一个 22Ω, 但本项目不能用它的滤波部分)★**

★★**方案 (二选一, 待裁)★★
| 方案 | 做法 | 优点 | 代价 | 硬件总工倾向 |
|---|---|---|---|---|
| ★**①** ★ | ★换 3 脚双通道阵列 (pin1=D+ / pin2=D− / pin3=GND)★ | ★不改网表拓扑; 位置只需一个; 面积最小; 官方有现成件 (TPD2EUSB30)★ | ★要改封装 (2 脚→3 脚) + 改位置 + 重跑布线★ | ★**推荐** ★ |
| ★**②** ★ | ★保留现有 2 脚件 + 另加一只 D− 件 (D_ESD_USB_D_N)★ | ★不用改现有封装库★ | ★要摆两个器件; 钳位/结电容要配对; 面积更大★ | 不推荐 |

★★**降级方案 (查不到/选不到时的必填项)★★
- ★**首选**: 方案① + 官网参数直接满足判据的替代型号 (TI TPD2EUSB30 及同级 ≤1 pF 的 3 脚双通道阵列) ★
- ★**若 3 脚双通道件买不到**: 退成 ★**2 只单通道低电容 TVS** (各 ≤1 pF) 分别贴 D+ 与 D− ⇒ 器件比双通道件好买, 代价是面积 + 要配对 ★
- ★**无论哪条路, 必须把 ESD 从 `USB_D_P_SRC` (SoM 侧) 挪到 `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` (Type-C 侧)** ⇒ 否则等于没护 (★这条是所有方案的共同底线★)
- ★**★绝不许的降级**: "先不加 ESD, 靠用户不碰" ⇒ ★**这是唯一一条"没有降级方案"的项, 因为 Type-C 插拔是日常动作★**

⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/gen_pcb_components.py` ★ → ★`python3 state/gen_pcb_routing.py` ★ → ★`python3 state/gen_pcb_netlist_board.py` ★ → ★`python3 state/check_kicad_net.py` ★ → ★`python3 state/check_pcb_drc.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★
⑦ 翻面判据: ★**R4 + R9** ★ (★板上挂 D− 两张网的 ESD 位号数 ≥ 1; `D_ESD_USB_D` 焊盘数 = 3 (方案①) / 出现 `D_ESD_USB_D_N` (方案②); 距 `J_USB_C` **≤ 3.0 mm**★)
⑧ 证据等级: ★**[官网]** TI **TPD2EUSB30 / TPD2EUSB30A / TPD4EUSB30** datasheet **SLVSAC2G** (2ch/4ch / 0.7-0.8 pF / level 4 contact 8kV / Vclamp 8V / DRT 1.00×0.80mm / TPD4EUSB30 air 9kV) · onsemi **STF202-22T1G** datasheet (Rev 11, 2025-03) (线电容 **68 pF** / 内置 RS 20-22-24Ω) · ON Semi **AND8074/D** (两条数据线都要护 / IEC 等级表 / 钳位 8.70V@8kV 接触, 10.60V@15kV 空气) · ★**[实测]** 板文件 pads/value/坐标/距离 47.99mm + 4 个 ESD 位号逐个查网 · ★**[推算]** 480 Mbps 的电容预算 / 只护单边的后果 · ★**[0数据]** 型号的采购可得性与实际单价 (★零外发 ⇒ 未询价★) · ★**[0数据]** SoM USB PHY 的 abs-max 与钳位需求
<!-- WPITEM:END -->

### ★★§5.3 · 待裁V-3 · BAT_DET 分压比: 方案 A (2.0M+1.2M) 还是降级档 D (2.0M+1.0M)?★★

<!-- WPITEM:BEGIN id=待裁V-3 -->
① 项号: ★**待裁V-3** ★ (规格页 §13 V-3 · 吸收到 **d7** · 锚点组 `d7_*` · 翻面判据 **R2 + R7 + R8**)
② 现状逐字 + 行号: ★**表A L182/L183** 器件行 value = ★`1M ±1%` / `1M ±1%`★ (★dnp=DNP★) · ★**L181/L186** NET 行 value = ★`1M+1M 分压 + 100nF`★ · ★**[官网] 判据真源**: `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt:2864` `Anglog Input Range AIN AVSS18 NA AVDD18 V` + `:2454` `SARADC Analog Power(1.8V) SARADC_AVDD1V8 1.62 1.8 1.98 V` + ★**`HW/PCB/FET3572C_PIN_TABLE.csv:39`** `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` · ★**规格页 §13 V-3 逐字**: 「★**BAT_DET 分压比: 方案 A (2.0M+1.2M) 还是降级档 D (2.0M+1.0M)?** ★」
③ 缺陷一句话: ★**不是缺陷, 是【纯工程取舍】—— 上限 (1.8V / 1.98V) 由官方 datasheet 定死了, 但"下臂取 1.2M 还是 1.0M"要在"12bit 利用率"与"更保守的电压余量"之间取舍⇒ 且当前 1:1 是过压, 无论裁哪个都必须改★**
④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段 `R_BAT_DET_1` / `R_BAT_DET_2` 两条 `add()` 的 `value` + 同段 NET 行的 `value` + `R_BAT_DET_1` 那条 `note` 里的漏电流数** ⇒ ★**判据真源 = RK3572 官方 datasheet (上限) + `HW/PCB/FET3572C_PIN_TABLE.csv` (SoM 域) + `HW/INTERFACE_TABLE.md` C-03 (4.2V 满充)★**
⑤ 改法 (逐字值) — ★**默认值 + 备选 + 代价 (★含对 60ms / 充电时间 / 单 pin 载流 / 皮肤温度的影响★)★**:
| 方案 | 上臂 | 下臂 | V_node@4.2V typ | worst (下臂+1% / 上臂−1%) | 12bit 利用率 | 漏电@4.2V | 功耗 | 判定 |
|---|---|---|---|---|---|---|---|---|
| ★**A (默认 / 推荐)** ★ | ★**2.0M ±1%** ★ | ★**1.2M ±1%** ★ | ★**1.575 V** ★ | ★**1.595 V** ★ | ★**87.5%** ★ | ★**1.31 µA** ★ | 5.5 µW (待机地板 0.05W 的 **0.011%**) | ★**推荐: 三个指标同时最优; 电压余量 1.8−1.595 = 0.205V (含 ±1% 容差仍安全)★** |
| ★**D (备选 / 降级)** ★ | ★**2.0M ±1%** ★ | ★**1.0M ±1%** ★ | ★**1.400 V** ★ | ★**1.419 V** ★ | ★**77.8%** ★ | ★**1.40 µA** ★ | 5.9 µW (0.012%) | ★**降级档: 更保守 (电压余量 0.381V); 代价 = 12bit 少用 10 个百分点 + 电量读数分辨率略降★** |
| ★**✘ 现值** ★ | 1.0M | 1.0M | ★**2.100 V** ★ | — | — | 2.10 µA | 8.82 µW | ★**过压 (超 AVDD18 max 1.98V 0.120V / 6.1%) ⇒ 判死★** |

★★**代价 (含老板关注的四项)★**
| 关注项 | A (2.0M+1.2M) | D (2.0M+1.0M) | 说明 |
|---|---|---|---|
| ★**端到端 <60ms** ★ | ★**零影响** ★ | ★**零影响** ★ | ★**★ADC 分压链与 60ms 延迟链无关 (60ms 是显示/相机链) ⇒ 两条都不影响这个指标★★ |
| ★**充电时间** ★ | ★**零影响** ★ | ★**零影响** ★ | ★**★分压链挂在 BAT 检测上, 不在充电功率路径上 ⇒ 不影响充电电流/时间 (充电时间由 V-4 的 R_ILIM 档位决定)★★ |
| ★**单 pin 载流** ★ | ★**零影响** ★ | ★**零影响** ★ | ★**★分压链是高阻小电流支路 (1.31 / 1.40 µA), 与 J_CHG 载流 pin 无关 ⇒ 不影响 (★单 pin 载流问题在 V-4★)★★ |
| ★**皮肤温度** ★ | ★**零影响** ★ | ★**零影响** ★ | ★**★分压链功耗 5.5/5.9 µW (待机地板的 0.011/0.012%) ⇒ 对皮肤侧温度无影响 (★皮肤温度由电芯内阻 + 铰链段载流决定, 见 V-4★)★★ |
| ★**电量读数分辨率** ★ | ★**87.5% 满量程 (1024 码覆盖 3.0~4.2V) ★ | ★**77.8% (≈896 码) ★ | ★**★A 优于 D, 差别在实际用不到 (电量显示不需要 1% 精度)⇒ **这条不足以推翻 A 的余量优势**** |

★★**★降级路径 (必须项)★**: ★**★落表那趟直接用 A, 不等 SoM 手册 ⇒ 理由: A 的电压余量 (0.205V) 已经覆盖"1.8V 标称"这一档, 而 D 覆盖"1.5V abs-max"那一档 ⇒ 绝不选 1:1★★** ⇒ ★**SoM 手册一旦到手, 只需核对"Cin / 采样保持时间 / 模块 abs-max"三条, 不用重算分压比★** ★
★★**落表后影响哪几行**: ★**表A L182 / L183 (value, 由生成器自动) + L181 / L186 (NET 行 value `1M+1M 分压 + 100nF` → `2.0M+1.2M 分压 + 100nF`) + L182 的 note 里的漏电流数 (1.31µA / 1.40µA) + 脚表对应 4 行的 value + BOM `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 三行 (含 dnp 由 DNP → 必装) + `HW/POWER_BUDGET_V3.md` 的待机口径 (分压链功耗占位)★** ★
⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★
⑦ 翻面判据: ★**R2 + R7 + R8** ★ (★R2: 分压后 @4.2V ≤ 1.8V; R7: 分压后 @4.2V ≥ 1.2V; R8: note 自称的漏电流 == 由 value 算出来的数★)
⑧ 证据等级: ★**[官网]** RK3572 Datasheet Rev 1.1 §3.10 Table 3-16 + 电气总表 AVDD18 (1.62/1.8/1.98 V) · ★**[实测]** `FET3572C_PIN_TABLE.csv` L39 + 表A L181-L186 + BOM L86/L87/L27 · ★**[推算]** 候选分压比全表 + 利用率 + 漏电/功耗 + "60ms/充电时间/单 pin 载流/皮肤温度 四项均不受影响" 的逐项论证 · ★**[0数据]** SoM SAR-ADC 的 Cin / 采样保持时间 / 模块 abs-max (★芯片级已判死 ⇒ 不阻塞★)
<!-- WPITEM:END -->

### ★★§5.4 · 待裁V-4 · R_ILIM 档位: 解① 475~510Ω 还是解② 390Ω + J_CHG 4 pin 并联?★★

<!-- WPITEM:BEGIN id=待裁V-4 -->
① 项号: ★**待裁V-4** ★ (规格页 §13 V-4 · 吸收到 **d10** · 锚点组 `d10_*` · 翻面判据 **R10**)
② 现状逐字 + 行号: ★**表A L47 / L48** value = ★`390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)`★ · ★**表A L497** note 含 ★`充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (★每 pin ≤0.75A★)`★ · ★**`HW/CHARGE_BOARD_SPEC.md` L184** 390Ω 行 `0.82 / 0.91 / **1.00 A**` + `0.67 / 0.75 / **0.82 A**` + `**~0.75 A**` + `单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×` ★**L185** 300Ω 行 `单 pin 0.534A` + `❌ **300Ω 档正式判死**` · ★**L186** 260Ω 行 `1.01 / 1.13 / 1.23 A` · ★**L320** `ICHG ≈ 0.822 × IIN` · ★**规格页 §13 V-4 逐字**: 「★**R_ILIM 档位: 解① (475~510Ω, 充电慢 ~30%) 还是解② (390Ω + J_CHG 4 pin 并联, 要改 J_CHG pinmap)?** ★」
③ 缺陷一句话: ★**不是缺陷, 是【纯工程取舍】—— 390Ω 档在真值 (ICHG/IIN = 1.216) 下单 pin 0.608A > 0.5A 触点额定 21.6% ⇒ 档位必须重定, 而重定的代价是"充电慢"还是"改连接器 pinmap"★**
④ 真修法在哪个真源: ★**① `HW/CHARGE_BOARD_SPEC.md`** ★**§2.4 表 (L182/L184/L185/L186) + §3.4 公式 (L320) + §3.4 六场景 + L711 自检脚本** ⇒ ★**② `state/gen_netlist.py`** ★**`R_ILIM` 两条 `add()` 的 `value` + `J_CHG` 那条 `add()` 的 `note` (载流 pin 集合)★** ⇒ ★**③ 若裁解② ⇒ `J_CHG` 的 pinmap 要改 (★归 ISS-199/202 + §4.C 补差C 的改名方案★)★** ⇒ ★**★真值真源 = TI BQ25896 datasheet SLUSC76C (IINMAX = KILIM/RILIM; KILIM 320/355/390 AΩ; η 92.5%@2A / 90.5%@3A) + buck 功率守恒⇒ **不是 CHARGE_BOARD_SPEC 的手写公式 (那个方向反了)****
⑤ 改法 (逐字值) — ★**默认值 + 备选 + 代价 (★含 60ms / 充电时间 / 单 pin 载流 / 皮肤温度★)★**:
| 解 | 做法 | IINMAX (min/typ/max) | ICHG @3.70V | 单 pin @3.70V (max 档) | 余量 vs 0.5A | 代价 |
|---|---|---|---|---|---|---|
| ★**① (硬件侧最省事 / 默认)** ★ | ★**R_ILIM 提到 475~510Ω** ★ | 475Ω ⇒ 0.68/0.75/**0.82 A** · 487Ω ⇒ 0.66/0.73/**0.79 A** · 510Ω ⇒ 0.63/0.70/**0.76 A** | 475Ω ⇒ **0.999 A** · 487Ω ⇒ **0.963 A** · 510Ω ⇒ **0.929 A** | ★**475Ω ⇒ 0.499A** (余 0.2%, 太贴) · ★**487Ω ⇒ 0.487A** (余 2.6%) · ★**510Ω ⇒ 0.465A** (余 7.0%) ★ | ★**≥0.5A** (★建议取 **487Ω 或 510Ω**, 不要取 475Ω——余量 0.2% 等于没有余量★) | ★**充电慢 ~30%** (ICHG 从 1.216A 降到 ~0.93~0.96A; 按 420mAh 电芯 ≈ 29min → ≈ 38~40min) ★ |
| ★**② (保住 390Ω 与充电速度)** ★ | ★**J_CHG 载流 pin 从 2 只加到 4 只 (pin1/2/9/10)** ★ | 0.82/0.91/**1.00 A** (不变) | ★**0.997 / 1.107 / 1.216 A** (不变) | ★**1.216/4 = 0.304A** ★ | ★**余 39%** ★ | ★**★要改 J_CHG pinmap (pin9/10 现为"预留 (不装)"; I2C 上拉已移到充电板所以空着) ⇒ 这是 ISS-199/ISS-202 的地界, 要 mech-lead + main 排期★** ★ |
| ★**③** ★ | 换 1A/触点的连接器 | 0.304A ≤ 1A ✅ | — | — | — | ★**✘ 判死 (ISS-099 已写: 铰链区装不下 1.0mm pitch / 1A 触点的 ZIF)★** |
| ★**④** ★ | 软件限流 / 降充电电流目标 | — | — | — | — | ★**✘ 不可行 (IINLIM 复位默认 2048mA 是硬件行为, 必须靠 R_ILIM 压住)★** |

★★**代价 (含老板关注的四项)★**
| 关注项 | 解① (487Ω) | 解② (390Ω + 4 pin) |
|---|---|---|
| ★**端到端 <60ms** ★ | ★**零影响** ★ | ★**零影响** ★ (★充电电流与显示/相机延迟链无关★) |
| ★**充电时间** ★ | ★**★变慢 ~30%** (≈29min → ≈38min, 420mAh 电芯) ★ | ★**不变 (≈29min)** ★ |
| ★**单 pin 载流** ★ | ★**0.487A (余量 2.6%)** — 若取 510Ω 则 **0.465A (余 7.0%)** ⇒ ★**取 475Ω (0.499A, 余 0.2%) = 不合格, 不许取★** | ★**0.304A (余量 39%)** ★ |
| ★**皮肤温度** ★ | ★**★更低 (电流小 23% ⇒ 电芯内阻发热 114mW → ≈68mW)⇒ 皮肤侧更凉, 更好★** | ★**与现状同档 (充电时不在皮肤上, 老板 10-28 已拍板"边戴边充不允许")** |
| ★**改动面** ★ | ★**小: 只改 R_ILIM 的 value (换料不换板) + 规格表三行 + 公式★** | ★**大: R_ILIM 不动, 但要改 J_CHG pinmap + P9 页 pin map + 结构 (铰链段载流/温升核算) ⇒ 归 ISS-091/099/199/202★** |

★★**★落表后影响哪几行 (★解① 与解② 的差别在这几行★)★**
| 位置 | 解① (487Ω) | 解② (390Ω + 4 pin) |
|---|---|---|
| ★**`HW/CHARGE_BOARD_SPEC.md` L182 表头** ★ | ★**两解相同**: `CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**)` ★ | ★同左 ★ |
| ★**同 L184 (390Ω 行)** ★ | ★**改成 487Ω 行**: `0.66 / 0.73 / **0.79 A**` + ICHG `**0.963 A**` + 单 pin `**0.487A**` + 用途栏 `★★**本规格推荐值**` ★ | ★**保留 390Ω 行但把 CC 段列改成真值**: `**0.997 / 1.107 / 1.216 A**` + 单 pin `**0.304A** (4 pin 并联)` + 用途栏 `★★**待裁决**` ★ |
| ★**同 L185 / L186 (300Ω / 260Ω 行)** ★ | ★**两解相同**: 全部改成新系数 (300Ω → `1.298/1.437/1.581 A` + 单 pin `0.791A`; 260Ω → `1.496/1.657/1.824 A` + 单 pin `0.912A`) ★ | ★同左 ★ |
| ★**同 L320 / L711** ★ | ★**两解相同**: `ICHG ≈ IIN × η × (VBUS / VBAT)` + `lo*1.216` ★ | ★同左 ★ |
| ★**表A L47 / L48 value** ★ | ★`487Ω ±1% (IINMAX 0.66-0.79A · ICHG 0.87-0.96A · 单 pin ≤0.49A)` ★ | ★`390Ω ±1% (IINMAX 0.82-1.00A · ICHG 1.00-1.22A · 单 pin ≤0.31A)` ★ |
| ★**表A L497 note (J_CHG)** ★ | ★`每 pin **额定 0.75A / 降额后工作上限 0.50A** (ISS-099 FH12-10S-0.5SH(55)); 载流 pin = pin1/pin2` ★ | ★`每 pin **额定 0.75A / 降额后工作上限 0.50A** (ISS-099 FH12-10S-0.5SH(55)); 载流 pin = **pin1/pin2/pin9/pin10**` ★ |
| ★**`state/gen_netlist.py` 的 `J_CHG` pinmap** ★ | ★**不动** ★ | ★**要动 (pin9/pin10 从"预留 (不装)"改成载流 pin) ⇒ 归 ISS-199/202 + §4.C 的改名方案 (★改位号与加 pin 必须同一趟, 否则白改两遍★)★** |
| ★**BOM `R_ILIM` L97** ★ | ★`487Ω ±1% …` (★换料不换板★) ★ | ★`390Ω ±1% …` (★不动★) ★ |

⑥ 改完跑哪条命令: ★`python3 state/gen_netlist.py` ★ → ★`python3 state/gen_netlist_pins.py` ★ → ★`python3 state/gen_bom.py` ★ → ★`python3 state/check_netlist.py` ★ → ★`python3 state/check_netlist_pins.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ ⇒ ★**解② 追加: `python3 state/gen_pcb_netlist_board.py` → `python3 state/check_kicad_net.py` (★J_CHG pinmap 变了 ⇒ 板要重出★)★**
⑦ 翻面判据: ★**R10** ★ (★`CHARGE_BOARD_SPEC.md` 不再含 `0.822` 且含 `1.216` 与 `1.071`; 表A `R_ILIM` 的 value 不再含 `0.411A`; ★**且 `calc(ichg_pin_max@3.7) ≤ 0.5A`** ★)
⑧ 证据等级: ★**[官网]** TI **BQ25896** datasheet **SLUSC76C** (特性 "92.5% Charge Efficiency at 2 A and 90.5% Charge Efficiency at 3 A Charge Current" / ILIM "IINMAX = KILIM/RILIM" 原文 / KILIM 320-355-390 A×Ω) · ★**[实测]** CHARGE_BOARD_SPEC L182/L184/L185/L186/L320/L711 + 表A L47/L48/L497 + BOM L97 + `MECH/check_demo_struct_truth.py` G2.8 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 的 `MECH_ANCHORS` (eta/v_bus/ratio_370/ratio_420) 逐字 · ★**[推算]** 功率守恒与全表重算 + 解① 的 475/487/510Ω 值 (0.499/0.487/0.465A) + 充电时间 +30% (29min→38min) + 皮肤温度账 (电芯内阻 114mW → 68mW) + 四项关注 (60ms/充电时间/单 pin/皮肤温度) 的逐项判定 · ★**[0数据]** 铰链段实际接触电阻/温升/载流实测 (无样件) / 充电板实物
<!-- WPITEM:END -->

### ★★§5.5 · 待裁V-5 · 堆叠账唯一口径 (★数字归 MECH + 项目总工; 本单只写清 P9 页要引用哪个数★)★★

<!-- WPITEM:BEGIN id=待裁V-5 -->
① 项号: ★**待裁V-5** ★ (规格页 §13 V-5 · 吸收到 **d6** · 锚点组 `d6_*` · 翻面判据 **R6**)
② 现状逐字 + 行号: ★**`state/gen_schematic_pages.py:147` 堆叠账逐字**: `★**铰链区高度预算 (V1.3 按结构总工 F-3 收敛后)**: 4 条链路触点区**统一 0.5mm pitch** → 堆叠 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm** ✅ …` · ★**三个在用的数**: ★**26.5mm** (★P9 页 + `DECISIONS.md` 2026-10-27 项目总工 在用, 触点区口径★) / ★**27.00mm** (★`MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项 `STK-FPC` 在用, 触点区口径 (10+4+18+22)×0.5★) / ★**35.50mm** (★MECH 现行口径 = 27.00 + 4 条×2×0.50 走线边距, FPC 带宽口径★) · ★**分母**: ★**`MECH/cross_review_check.py:64` 逐字**: 「★**37.0 是已作废的叠放模型**算式 (22+12+3) —— 现行是**锁死的腔体净高 38.00**」★
③ 缺陷一句话: ★**三个堆叠数 + 一个已作废的分母并存 ⇒ P9 页的账不是"错了一个数", 是"整个账的输入全过期了" ⇒ 而 P9 页是 hw-lead 的地界, 但【最终数字】不是 ⇒ 本单只写清"P9 页要改成引用哪个数", 不许自带第二个堆叠数★**
④ 真修法在哪个真源: ★**`state/gen_schematic_pages.py`** ★**`PAGES["P9"]` 的堆叠账那一行** ⇒ ★**★数字的唯一真源 = MECH 侧的现行口径 (★`MECH/cross_review_check.py` 锁死的腔体净高 38.00 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项 STK-P9/STK-FPC 的 FPC 带宽口径 35.50)★ ⇒ 归 mech-lead + 项目总工 (V-5)★** ⇒ ★**★本单的硬要求只有一条: P9 页不许再自带一个堆叠数, 改成【引用】结构侧口径 + 写清"净高 38.00" ⇒ 宁可不写数, 也不写第二个错数★**
⑤ 改法 (逐字值): ★**`state/gen_schematic_pages.py` P9 页堆叠账那一行** ★**改成引用式写法 (★数字由 V-5 裁决后填入, 但句式先定死, 防止又出现第二个数★)**:
```
  ★**铰链区高度预算 (★口径 = 结构侧现行值, 本页不自带第二个数★)**: 触点区 0.5mm pitch (1 组跨铰链 J_CHG 10p) →
  ★**FPC 带宽口径 <裁决值>mm** (★= 触点区 + 4 条×2×0.50 走线边距, MECH/HW_CROSS_REVIEW_TRIAGE.md 第 08 项 STK-P9★)
  vs 镜脚根部净高 **38.00mm** (★MECH/cross_review_check.py 锁死值; ★**37.0 是已作废的叠放模型算式 (22+12+3), 不许再用★**) → **余 <裁决值>mm** ✅
```
⇒ ★**★必须同时废掉的另两处 (★两个数并存 = 下次还会打架★)★**: ★**① `DECISIONS.md` (2026-10-27 · 项目总工) 里的 `铰链区堆叠仍 26.5mm (余 10.5mm)` (★那是 boss 级决策记录 ⇒ **归项目总工改, 本单不改 DECISIONS.md★**)★ · ★**② `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项的 27.00mm (★归 mech-lead★)★** ⇒ ★**落表后影响哪几行**: ★**P9 页那一整段 (1 行超长字符串) + `DECISIONS.md` 那一行 (★归项目总工★) + MECH 侧那一项 (★归 mech-lead★)⇒ **本单只改第 1 处**★**
⑥ 改完跑哪条命令: ★`python3 state/gen_schematic_pages.py` ★ → ★`python3 state/check_sch_loadable.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★R6 必须转绿★) ⇒ ★**★并与 MECH 侧互查 (`MECH/check_demo_struct_truth.py` 与本单口径能对上号) ⇒ 归落表那趟, 本单不改 MECH★**
⑦ 翻面判据: ★**R6** ★ (★P9 页不再含 `1×21p@0.5mm` / `(**18p@0.5mm**)` / `(**4p@0.5mm**)` / `(10+4+18+21)×0.5`; 且含 `1×22p@0.5mm`★) ⇒ ★★**"P9 页不再自带第二个堆叠数" 这一条目前没有独立 R# ⇒ 落表那趟建议在 R6 里加一条"P9 页不含 26.5mm 且不含 37.0mm"的断言 (★归落表那趟, 本单不改门禁的 R6, 免得与 V-5 的裁决打架★)★★**
⑧ 证据等级: ★**[实测]** `gen_schematic_pages.py:147` 逐字 + `MECH/cross_review_check.py:64` 逐字 + `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 08 项 + `DECISIONS.md` (2026-10-27) 逐字 + 网表/脚表 pin 计数 (22/31/0) 本机实跑 · ★**[推算]** 26.5 / 27.00 / 35.50 三数对应的物理模型 (触点区 vs FPC 带宽) · ★**[官方]** 官方 RPi CM5IO / Pi5 DISPLAY 座封装 = Hirose FH12-22S-0.5SH(55) ⇒ 22p 真值 · ★**[0数据]** 铰链段实际堆叠与净高实测 (要等结构实测/印包)
<!-- WPITEM:END -->

### ★★§5.6 · 待裁V-6 · ESD 位置判据 5mm → 3.0mm 的口径收口 (★本单已落定, 写进作业包即可★)★★

<!-- WPITEM:BEGIN id=待裁V-6 -->
① 项号: ★**待裁V-6** ★ (规格页 §13 V-6 · 吸收到 **d9** · 锚点组 `d9_*` · 翻面判据 **R9**)
② 现状逐字 + 行号: ★**ISS-211 规格页 §5.2 逐字**: `★**到 \`J_USB_C\` 的板面距离 ≤ 5 mm (★现在 47.99 mm★)` ⇒ ★**`state/gen_schematic_pages.py` P9 页逐字**: `④ **ESD 距连接器 ≤3.0mm** / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC` (★ISS-085 结构总工回执★) ⇒ ★**门禁 R9 现实现 (本单已改)**: `ESD_MAX_DIST_MM = 3.0` + `if d > ESD_MAX_DIST_MM:`
③ 缺陷一句话: ★**两个口径并存 ⇒ 落表验收判据不唯一** ⇒ ★**★已在本单收口: 按 3.0mm 判 (项目自己的规矩, 更严) ⇒ 门禁 R9 阈值已改成 3.0 (现状断言不动)⇒ **本条不再需要签字, 只需知会 main****
④ 真修法在哪个真源: ★**`HW/check_netlist_selfconsistency.py`** ★**R9 翻面判据的阈值常量 `ESD_MAX_DIST_MM = 3.0`** ⇒ ★**★本单已落 (见 §4.B 补差B 的逐字改法)★** ⇒ ★**落表后影响哪几行**: ★**P9 页的 `≤3.0mm` 那一行 (已对, 不动) + 表A L417/L418 (3 脚) + 板位置 (≤3.0mm) ⇒ **没有别的行要改****
⑤ 改法 (逐字值): ★**☐ 已落定 (本单)**: `HW/check_netlist_selfconsistency.py` 新增常量 ★`ESD_MAX_DIST_MM = 3.0`★ 并把 R9 的 `if d > 5.0:` 改成 ★`if d > ESD_MAX_DIST_MM:`★; ★**现状断言 `('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5')` 一字不动**★; ★**`--selftest` 加一条反向用例 (把阈值改回 5.0 ⇒ 必须变红)**★ ⇒ ★**☐ 落表那趟要做的**: ★**把 ESD 挪到 `J_USB_C` 旁 ≤ 3.0mm (见 d4 的 ⑤)★** ★
⑥ 改完跑哪条命令: ★`python3 HW/check_netlist_selfconsistency.py` ★ → ★`python3 HW/check_netlist_selfconsistency.py --selftest` ★ → ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★ (★期望 rc = 0 / 0 / 1★) ⇒ ★**落表那趟追加: `python3 state/gen_pcb_netlist_board.py` → `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★
⑦ 翻面判据: ★**R9** ★ (★`--expect-resolved` 的 R9 段: 距离 **≤ 3.0 mm**★) ⇒ ★**反向用例: 把常量改回 `5.0` ⇒ `--selftest` 必须变红 (★证明阈值真被读到 3.0 而不是 5.0★)★**
⑧ 证据等级: ★**[实测]** 规格页 §5.2 逐字 + P9 页 `≤3.0mm` 逐字 + 门禁原码逐字 + 板面实测 47.99mm ⇒ ★**47.99 > 5 也 > 3.0 ⇒ 改阈值不动现状断言 (现状守卫与翻面口径的判定结果都不变)★** · ★**[实测]** 新增反向用例跑通 (本机实跑 `--selftest` ⇒ 17/17 全过, 原 16 条一条没删) · ★**[推算]** "3.0 是项目自己的规矩 (ISS-085), 比 5.0 更严 ⇒ 取更严" 的取舍
<!-- WPITEM:END -->

---

## 6. ★★落表那一趟的执行顺序 (★与 `state/RECHAIN_STEP1_LANDING_SPEC.md` 对齐, 不许另起一套编号★) ★★

★★**★本作业包不重出编排, 只给"这 12 组怎么插进既有 14 步"★★

| 序 | 既有作业包的动作 (★`state/RECHAIN_STEP1_LANDING_SPEC.md` §5★) | 本作业包要并进去的动作 | 门禁闸 |
|---|---|---|---|
| ★**①** ★ | ★**改表 (C + D + E 三处, 一次改完)** ★ | ★**改源 (★不是改表★)**: `HW/SCHEMATIC_V1_SPEC.json` (d1 / d5) + `state/gen_netlist.py` (d2/d3/d4/d7/d8/d10/d11 + 补差A 的 2 行) + `state/gen_netlist_pins.py` (d2/d3/d4) + `state/gen_schematic_pages.py` (d6) + `HW/CHARGE_BOARD_SPEC.md` (d10) ★ | ★**★门禁在此刻还是红的 (★`--expect-resolved` rc=1 是预期★)★** |
| ★**②** ★ | ★**核表 (`check_netlist.py` + `check_netlist_pins.py` + `check_kicad_net.py` 三个 rc=0)** ★ | ★**同一批跑, 三个 rc 仍必须是 0** ★ | ★`state/check_netlist.py` / `state/check_netlist_pins.py` / `state/check_kicad_net.py` rc=0 ★ |
| ★**③** ★ | ★**重出原理图 (`gen_kicad_sch.py` ⇒ `check_sch_erc.py` + `check_sch_loadable.py` + `check_sch_pinfull.py` 三个 rc=0)** ★ | ★**+ `gen_schematic_pages.py` 重出 P9 页 (d6)** ★ | ★三个 rc=0 + P9 页 svg 重出 ★ |
| ★**④** ★ | ★**逐脚零差异 (KiCad 导出网表 vs `netlist_v1.csv`)** ★ | ★**同上** ★ | — |
| ★**⑤** ★ | ★**重出板 (`gen_pcb_netlist_board.py` ⇒ fresh DRC rc=0 + parity rc=0)** ★ | ★**★d4/d9 的 ESD 换封装 + 挪位置 ⇒ 布线必须重跑 ⇒ 板只改一次的纪律在第 ① 步就已经把 d4 排进来★** ★ | ★DRC rc=0 + parity rc=0 ★ |
| ★**⑥** ★ | ★**重出 BOM (`gen_bom.py` ⇒ 218 器件 / 0 伪器件 / 含 P2+P4 / 无问号位号)** ★ | ★**d3 的 U_EN_SW type 从 NET → IC (★BOM 器件数应 +0 伪器件? ⇒ 按 BOM 口径核★)** ★ | ★BOM 闸 ★ |
| ★**⑦** ★ | ★**BOM 一致性闸** ★ | ★**d11 的 `C_VBUS_GND` 从主板消失 ⇒ BOM 的 board 列要跟着核** ★ | ★BOM 闸 ★ |
| ★**⑧** ★ | ★**换基线 (旧 md5 → 新 md5, 24 个引用点)** ★ | ★**★本作业包涉及的 md5 变更面: 网表 / 脚表 / BOM / 板 / `.kicad_pro` / SPEC.json / CHARGE_BOARD_SPEC.md / P9 页 svg ⇒ 换基线时这些引用点都要一起换★** ★ | ★★**★md5 变更必须与本作业包逐条对应 (★哪一条改了就该哪一处 md5 变; 不许有"意料之外的 md5 变化"**** |
| ★**⑨~⑭** ★ | ★**重出投产包 → 留证链+盖章 → 发布闸 → 巡检+决策页 → 推 GitHub → 回写清单+决策页** ★ | ★**★规格页 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 本身也是那一趟的交付物 (§5.2 第 3 步: 行号会变, 规格页要同步) ⇒ **本作业包在落表后也要同步更新 ② 栏的行号与逐字**★ ★ | ★链闸 ★

★★**★落表那趟的判定口径 (★必须一次落干净, 不许分批试错★)★**
1. ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ★**rc=0** (★R1~R11 全转绿★)
2. ★`python3 HW/check_netlist_selfconsistency.py --selftest` ★**rc=0** (★★**★注意: 落表后 `--selftest` 的用例要同步改成"新现状"★ ⇒ 落表那趟必须同步改 `--selftest` 用例的期望 (★规格页 §5.2 第 4 步已写明★)⇒ **落表那趟若忘了改 selftest 用例, 门禁会假红★** ★**)
3. ★`python3 HW/check_netlist_selfconsistency.py` (★现状守卫★) ★**rc=0** (★规格页的 EXPECT 与锚点表同步更新后仍绿★)
4. ★`python3 state/check_netlist.py` / `state/check_netlist_pins.py` / `state/check_kicad_net.py` ★**rc=0 / 0 / 0**
5. ★`python3 state/merge.py` ★rc=0 · ★`python3 state/gate_check.py` ★rc=0 且【Q1】18/18

---

## 7. ★★边界自查 + 受保护 md5 (★交卷时逐条自查过★) ★★

★**未碰 (★逐条自查, 本单一个字节都没改★)★**
`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/SCHEMATIC_V1_SPEC.json` · `HW/CHARGE_BOARD_SPEC.md` · `HW/EMC_PRECHECK.md` · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` · `HW/RK3572_PIN_TABLE/*` · `HW/PCB/FET3572C_PIN_TABLE.csv` · `state/gen_netlist.py` · `state/gen_netlist_pins.py` · `state/gen_schematic_pages.py` · `state/gen_bom.py` · `state/gen_pcb_components.py` · `state/check_netlist.py` · `state/check_netlist_pins.py` · `state/check_kicad_net.py` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · `MECH/` 任何文件 · `SW/` 任何文件 · 别人的分片

★**只动 (★本单允许的四件 + 一条分片登记★)★**
1. ★**新建** ★`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (★本文件★)
2. ★**扩** ★`HW/check_netlist_selfconsistency.py` (★作业包完整性 + 三方对齐 + R9 阈值 3.0mm + 新增反向用例★)
3. ★**新建** ★`HANDOFF/2026-11-16_hw-lead_ISS217_落表作业包v1.md`
4. ★**`state/fragments/hw.yaml`** ★**走 `python3 state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)**: +1 artifact +1 claim +1 need (★6 条待裁确认单 to main★)

★**受保护 md5 (★开工前 / 交卷后 两个值都贴出来★)★**
| 文件 | 期望 md5 | 开工前实测 | 交卷后实测 |
|---|---|---|---|
| ★`HW/netlist_v1.csv` ★ | ★`c78f991283cc82d56c8e3dd31657c785` ★ | ★见交卷报告★ | ★见交卷报告★ |
| ★`HW/netlist_v1_pins.csv` ★ | ★`4814617e22b567d76164e56bc5e39dc8` ★ | ★见交卷报告★ | ★见交卷报告★ |
| ★`HW/PCB/demo_mainboard.kicad_pcb` ★ | ★`611b869e13518c3c023fb178f91a0075` ★ | ★见交卷报告★ | ★见交卷报告★ |
| ★`HW/PCB/demo_mainboard.kicad_pro` ★ | ★`3e504d2be83152e337949723e909be1b` ★ | ★见交卷报告★ | ★见交卷报告★ |

★**★零外发 + 实物 [实测] = 0 条 (★口径声明★)★**
★**本单未发任何邮件 / 询价 / 问询 / 采购; `state/outbox/` 未碰** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本 / 本机文件实读" (板与屏不在本机); 凡是标 [推算] 的, 一律是纸上算的; 本单没有一次示波器 / 万用表 / 热像仪的实测★** ⇒ ★**凡要查资料 ⇒ 自己在官网 / 官方 datasheet 上查 + 标证据等级 + 查不到写降级方案 ⇒ 没有"批一句可以发"这个选项★**

★**★本单不许替老板拍 (★逐条自查, 一个都没拍★)★**
整机屏路线 · 波导归属 · FOV · 板长方案取舍 · 充电板是否留 · 端件截面 u8 ⇒ ★**本单对 V-1 / V-3 / V-4 只给"默认值 + 备选 + 量化代价 + 落表后影响哪几行"; 对 V-2 只给"官网参数满足的候选 + 判据串 + 查不到的降级方案"; 对 V-5 只写清"P9 页要引用哪个数"; 对 V-6 已按项目自己的规矩落定并写进作业包⇒ **一个待裁项都没有代拍****

---

## 8. ★★落表状态 (★ISS-220 第 1 批 · 2026-11-16 · 硬件总工执行★) ★★

★★**一句话**: ★**本作业包的 28 条里, 5 组真源改动已落进盘上 (d1 / d6 / d10 方向修正部分 / d11+#5 / #1+补差A 的字段基建), 其余全部【BLOCKED】, 卡在 V-1~V-6 与板只改一次那一趟** ⇒ ★**逐条落表记录见 `HW/SCHEMATIC_LANDING_V1_LANDED.md`, 交接单见 `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md`** ★

| 项号 | 落表状态 | 卡在谁 / 卡在哪 |
|---|---|---|
| ★**d1** ★ | ★**已落表** (R1 转绿) ★ | — |
| ★**d6** ★ | ★**已落表** (R6 转绿) ★ | 堆叠数值本身归 MECH+项目总工 (V-5) ⇒ ★**本页不自带第二个数**★ |
| ★**d10** ★ | ★**部分落表** (R10 4→1: 方向修正 + 假余量结论作废 + #8 的 470Ω 残留) ★ | ★**档位 BLOCKED 于 V-4** (老板待拍 · `DECISION_PENDING_2026-11-16.md` §3) ★ |
| ★**d11 / #5** ★ | ★**已落表** (R11 转绿) ★ | ★**板侧封装归属待『板只改一次』那一趟** (本单只报不改) ★ |
| ★**#1 / 补差A** ★ | ★**部分落表** (字段基建 + 数据) ★ | ★**`imp` 迁移 BLOCKED 于 V-1**; A 组清空 `imp` 须与 `state/check_netlist.py` 判据 5 同趟 ★ |
| ★**#7** ★ | ★**已核验** (一个字没改) ★ | — |
| ★**#8** ★ | ★**已落表** (并入 d10) ★ | — |
| ★**d2 / d7 / d8** ★ | ★**BLOCKED** ★ | ★**V-3** (BAT_DET 分压比 2.0M+1.2M 还是 2.0M+1.0M) ★ |
| ★**d3** ★ | ★**BLOCKED** ★ | ★**板只改一次的纪律** (本体行落表 ⇒ 板封装 Value 必须同趟改 ⇒ 与 d4 同批, 而 d4 卡 V-2) ★ |
| ★**d4 / d9** ★ | ★**BLOCKED** ★ | ★**V-2** (ESD 方案与型号 = 老板级选型) + 板侧换封装/挪位置 ★ |
| ★**d5** ★ | ★**BLOCKED** ★ | ★**V-1** (USB 串阻 22Ω 还是 0Ω) ★ |
| ★**#2** ★ | ★**BLOCKED** (并入 d8) ★ | ★**V-3** ★ |
| ★**#3 / 补差B / V-6** ★ | ★**已落定** (ISS-217 已落: R9 阈值 3.0mm + 反向用例) ★ | — |
| ★**#4 / 补差C** ★ | ★**BLOCKED** ★ | ★**ISS-199 / ISS-202** (J_CHG 位号消歧) + 充电板整机阶段单 (V-7) ★ |
| ★**#6** ★ | ★**BLOCKED** ★ | ★**充电板整机阶段单** (π 滤波拓扑真值) ★ |

★**门禁实测**: ★**落表前 `--expect-resolved` 报「50 条未落表」 ⇒ 落表后报「29 条未落表」** ★; ★**现状守卫 `rc=0` (规格页锚点表已同步, 154→160 条, 一条未减) · `--selftest` `19/19` (★用例 1/5/10/14/15 的突变方向已按新现状翻转★) · `--expect-resolved` `rc=1` (★预期: 还有 BLOCKED 条目★)** ★
