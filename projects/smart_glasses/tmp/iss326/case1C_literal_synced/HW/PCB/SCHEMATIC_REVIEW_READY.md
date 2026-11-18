# 原理图评审就绪说明 (SCHEMATIC_REVIEW_READY)

> ★**一句话结论**: 原理图已从"**1 张 2471mm 长的巨图**"改成"**11 页 KiCad 层级图 (1 页封面 + 10 页功能页, 每页一个 CSV page)**",
> ★**每页内容都装得进 A2 纸** ⇒ ★**PDF 每页完整 ⇒ 老板/评审现在能看全图了**★;
> ★**连通性零改动**: 163 网 / 513 脚, 与 `HW/netlist_v1.csv` ★**逐脚零差异**★;
> ★**板子文件一字未动**: md5 仍 `611b869e13518c3c023fb178f91a0075`, fresh DRC 仍 **0 违规**★。
>
> 交卷: hw-lead (硬件总工) · 2026-11-11 11:0x · 证据分级: [实测] / [官方] / [推算] / [0数据]

---

## 1. 之前为什么看不全 (★先复现问题, 再谈修法★)

| 项 | 改前 | 改后 | 证据 |
|---|---|---|---|
| PDF 页数 | **1 页** | **11 页** (1 封面 + 10 功能页) | [实测] `pdfinfo` |
| 图纸纸型 | A2 (1683.79×1190.52 pt) | A2 (每页同) | [实测] `pdfinfo` |
| 图纸内容包围盒 | x (−13..524) / y (−23..2422) mm | 每页 (见 §3 表) | [实测] 直接量 `.kicad_sch` 坐标 |
| 内容高度 vs 纸高 | **2471 mm vs 420 mm ⇒ PDF 只截到 17.0%** | 每页 ≤ 350 mm ⇒ **100%** | [实测] |
| 内容宽度 vs 纸宽 | 557 mm vs 594 mm ⇒ **横向 107% (也超)** | 每页 ≤ 490 mm ⇒ 100% | [实测] |

⇒ ★**改前 PDF 只看得到顶部 17%, 底部 83% 的原理图根本不存在于 PDF 里**★ (这跟老板看到的现象对得上)。

---

## 2. 改了什么 (★只动原理图, 板子/网表表一律没动★)

**做法 = 生成器分 sheet (不是改图纸尺寸)**, 理由: 改纸型只能救"一张"图, 评审仍是 2471mm 长的巨图, 缩屏看不清;
★**一页一功能块才是工程惯例, 评审按页走**★。

| 改了什么 | 说明 | 证据 |
|---|---|---|
| `state/gen_kicad_sch.py` | ★**按 CSV 的 `page` 列 (P1..P10) 把器件分到 10 个 sheet**★; 每页自动选纸型/行列, 保证内容 ≤ 纸张 | [实测] 生成器自检 C1~C11 全过 |
| `HW/PCB/demo_mainboard.kicad_sch` | 改成★**根页 (封面/目录)**: 10 个 sheet 块 + 标题栏 | [实测] |
| `HW/PCB/demo_mainboard_p1..p10.kicad_sch` | ★**新增 10 个子页** (多 sheet 必然要的文件; 页名 = CSV 的 P1..P10) | [实测] |
| ★**标签: 局部标签 → 全局标签 (global_label)**★ | ★**这是多 sheet 的成败关键**: 局部标签是★**页内作用域**★ ⇒ 同一个 `GND` 在 P1 和 P7 上会被当成★**两个不同的网**★ ⇒ 跨页的 GND 会被拆成 10 个网 ⇒ 网表对不上; 全局标签是全设计作用域, ★**网名原样保留 (不加 `/P1/` 前缀)**★ | [实测] 原型 + 正式图: 导出网表 GND 一个网, 163 个网全对 |
| `HW/PCB/production/doc/demo_mainboard-sch.pdf` | ★**重新导出** (旧文件是 1 页的旧版, 不重导老板打开还会看到 17% 的老图)★ | [实测] 11 页 |
| `HW/PCB/production/doc/demo_mainboard-kicad.net` / `-bom.xml` / `sch_svg/*.svg` | 同一套导出命令重跑 (原理图侧产物, 板侧产物未动) | [实测] 网表 163 网 / BOM 291 器件 / SVG 11 个 |

### ★**没动的东西 (逐项自证)★

| 文件 | md5 / mtime | 判定 |
|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | md5 **`611b869e13518c3c023fb178f91a0075`** (未变) · mtime 2026-11-06 07:07 | ★**PCB 一字未动**★ |
| `HW/PCB/demo_mainboard.kicad_pro` | md5 `3e504d2be83152e337949723e909be1b` · mtime **2026-11-04 23:47** (未变) | ★**这次**没走"改图纸尺寸"那条路 ⇒ **.kicad_pro 一个字节都没改** ⇒ ★**board setup constraints (min track width 0.15 / clearance 等 DRC 规则源) 绝对没漂**★ |
| `HW/PCB/demo_mainboard.kicad_prl` | mtime 2026-11-03 00:07 (未变) | ✓ |
| `HW/netlist_v1.csv` | md5 `c78f991283cc82d56c8e3dd31657c785` · mtime 2026-11-05 10:57 (未变) | ★**网表表一个字未改**★ |
| `HW/netlist_v1_pins.csv` | md5 `4814617e22b567d76164e56bc5e39dc8` · mtime 2026-11-08 23:23 (未变) | ✓ |

---

## 3. 现在有几页 / 每页多少器件 / 每页内容尺寸 vs 纸张尺寸

★**PDF 页 ↔ 原理图页 对照表 (★PDF 页 1 = 封面, PDF 页 2..11 = 功能页 P1..P10★)**★

| PDF 页 | 原理图页 | 名称 | 器件数 | 列×行 | ★内容包围盒 mm (含网名标签)★ | 纸张 mm | 占纸 (实测) |
|---|---|---|---|---|---|---|---|
| 1 | — | 封面/目录 | — | — | (60,56)-(345,388) | 594×420 | 48%×79% |
| 2 | P1 | 电源树 | 83 | 10×9 | (13,25)-(492,348) | 594×420 | 81%×77% |
| 3 | P2 | SoC 主控 | 14 | 10×2 | (18,31)-(485,88) | 594×420 | 79%×13% |
| 4 | P3 | 启动存储 | 9 | 9×1 | (19,31)-(453,52) | 594×420 | 73%×5% |
| 5 | P4 | 显示双出口 | 25 | 10×3 | (11,31)-(485,135) | 594×420 | 80%×25% |
| 6 | P5 | MIPI-CSI 传感器 | 23 | 10×3 | (11,31)-(488,146) | 594×420 | 80%×27% |
| 7 | P6 | 高速差分与连接器 | 6 | 6×1 | (15,31)-(293,52) | 594×420 | 47%×5% |
| 8 | P7 | 板级接口与测试点 | 72 | 10×8 | (16,31)-(490,303) | 594×420 | 80%×65% |
| 9 | P8 | 时钟·复位·调试 | 40 | 10×4 | (17,31)-(491,160) | 594×420 | 80%×31% |
| 10 | P9 | 跨铰链界面 | 1 | 1×1 | (16,31)-(55,53) | 594×420 | 7%×5% |
| 11 | P10 | 充电板(镜框) | 18 | 10×2 | (15,31)-(483,89) | 594×420 | 79%×14% |

- 器件合计 = **291** (= 网表器件数), 网 = **163**, 脚 = **513** ⇒ ★**器件不重不漏**★ [实测]
- "占纸" = ★**用 `pdftotext -bbox` 在 `--exclude-drawing-sheet` 版 PDF 上量到的实际文字包围盒 / 纸张尺寸**★ [实测]
  (为什么要另导一版: 开着图框时每页都被图框撑满 97%×96%, 量不出内容)
- ★**每页内容都 < 纸张 ⇒ 没有截断**★ [实测]
- 器件归属规则: ★**一个器件只能在一张 sheet 上 (它的脚必须在一起) ⇒ 取它在 CSV 里第一次出现的那一页**★;
  9 个跨页器件 (J_TYPE_C / J_CHG / U_CHG / D_ESD_TC / R_TS_TOP / U_DCDC_VCORE / U_DCDC_VIO / TP_BAT_CHG / CHG_GND_STAR) 落在首现页 [实测]

---

## 4. PDF 怎么导出 / 在哪看

```bash
cd <项目根>
# ★正式交付件 (已生成, 11 页)★
HW/PCB/production/doc/demo_mainboard-sch.pdf

# ★重导的命令 (与 state/gen_production_pack.sh 里用的是同一条)★
bash state/kicad.sh sch export pdf -o HW/PCB/production/doc/demo_mainboard-sch.pdf \
     HW/PCB/demo_mainboard.kicad_sch
# ★要单独量内容包围盒 (去掉图框)★
bash state/kicad.sh sch export pdf --exclude-drawing-sheet -o /tmp/ns.pdf HW/PCB/demo_mainboard.kicad_sch
pdfinfo HW/PCB/production/doc/demo_mainboard-sch.pdf | grep Pages   # ⇒ Pages: 11
```

★**评审建议顺序**: PDF p1 (封面/目录, 10 个功能页的清单) → p2 (P1 电源树, ★器件最多, 建议重点看★) →
p8 (P7 板级接口, 72 个) → 其余按需。每页都在 A2 纸上, ★**放大看是矢量, 位号/值/网名都可读**★ [实测: 150dpi 裁切图已人工核对, 无标签重叠/无截断]。

---

## 5. 闸门 (★交卷前逐条跑, 贴 rc 与关键输出★)

| # | 命令 | rc | 关键输出 |
|---|---|---|---|
| ① | `python3 state/check_sch_erc.py` | **0** | `ERC 违规数 = 0 (报告自称 0) · 分类 {}` ⇒ ✅ 过 (ERC=0) |
| ② | `python3 state/check_sch_loadable.py` | **0** | `C1 括号平衡 深度=0` · `C2 KiCad 能加载并导出网表 rc=0 · 339281 B` · `C3 能导出 PDF rc=0 · 708845 B` ⇒ ✅ 全过 |
| ③ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` | **0** | `✅ 全过 —— 板子与网表**逐焊盘**等价 (脚号/脚数/网络全对)` |
| ④ | `python3 state/gen_kicad_sch.py --parity` (★自己写的比对脚本★) | **0** | `网表 CSV: 163 个网 / 513 个脚` · `导出结果: 163 个网 / 513 个脚` · `✅ 网名集合一致` · `✅ 逐脚零差异 (513 个 (ref,pin) 全部相等)` · `✅ 每个网的引脚集合一致` ⇒ ★**图 = 网表**★ |
| ⑤ | `bash state/pcbnew_py.sh state/check_pcb_drc.py` (fresh) | **0** | `✅ C3 DRC violations = 0` · `C4 unconnected items = 45 (骨架阶段允许)` · `C7 同点重复过孔 = 0` · `C6 生产文件齐 — Gerber 32 个` |
| ⑥ | `python3 state/merge.py` | **0** | `✅ STATE.yaml 已刷新 (2026-11-11T10:57:51+08:00)` |
| ⑦ | `python3 state/gen_kicad_sch.py` (生成器自检) | **0** | `C1..C11 全过` (含 C8 11 个文件括号全平 / C9+C11 每页内容 ≤ 纸张) |

★**⑤ 的"改前改后"说明**: ★**这次没走"改 .kicad_pro 图纸尺寸"那条路 ⇒ .kicad_pro md5 `3e504d2be83152e337949723e909be1b`、mtime 2026-11-04 23:47 全程未变 ⇒ 板 DRC 规则源零漂移 ⇒ DRC 数字必然与改前一致 (0 违规 / 45 未连接)**★;
**且板文件本身 md5 仍 `611b869e13518c3c023fb178f91a0075` (字节级未变) ⇒ DRC 结果在数学上不可能变化** ★。

---

## 6. 遗留项清单 (★本轮**没有**动, 请老板拍板★)

### ① ★★位号规范 (KiCad "annotation errors") — ★★本轮只做影响面初评, 没动★★

**现状 [实测]**: 291 个器件里 ★**255 个在 KiCad 的 BOM 里带 "?" 后缀 (KiCad 判它"未标注")**★; 只有 36 个 (Q1/Q2/X1/C_*_1V8/R_CC1…) 不带。
⇒ KiCad 一旦有人点 "Annotate", 它会★**重排位号**★ ⇒ ★**直接改坏 网表 → BOM → 板 → 投产包 整条链**★。

**影响面初评 (★改位号要动哪些文件 / 会不会改板 md5★)**:

| 序 | 文件 | 为什么必须跟着改 | 会不会改板 md5 |
|---|---|---|---|
| 1 | `state/gen_netlist.py` (★器件表 = 唯一真源★) | 位号是**在这里定义的**, 不改源头 = 下游全漂 | — |
| 2 | `HW/netlist_v1.csv` | 513 行里的 `ref` 列 | — |
| 3 | `HW/netlist_v1_pins.csv` | 584 行里的 `ref` 列 | — |
| 4 | `HW/BOM_v1.csv` | `gen_bom.py` 从网表机械生成 | — |
| 5 | `HW/PCB/demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` | 符号的 `Reference` 属性 + 层级实例里的 `(reference ...)` | — |
| 6 | ★**`HW/PCB/demo_mainboard.kicad_pcb`**★ | ★**186 个封装的 `(property "Reference" ...)` = 板上丝印位号**★ | ★**会改 (md5 变)**★ |
| 7 | ★**`HW/PCB/production/*`**★ | ★**Gerber 丝印层 / CPL 坐标 / 装配 PDF / IPC-2581 / 3D STEP / D356 裸板测试网表 —— 全部含位号, 全部要重出**★ | ★**会改**★ |
| 8 | `HW/PCB/demo_mainboard_params.json` / `PCB_NETLIST_FILL.txt` 等生成器产物 | 位号透传 | — |
| 9 | 文档/日志 (`PINOUT_FOOTPRINT_SPEC.md`、`SOM_PIN_*.md`、`issue_log.yaml` …) | ★**抽样: 一个位号平均散在 19~112 个文件里**★ ⇒ ★**人工漏改 = 文档与图不一致**★ | — |

**结论 (★hw-lead 的判断★)**: ★**改位号 = 板子要重出 ⇒ md5 会变 ⇒ 整条链要重跑并重新过 5 道闸 (ERC/loadable/parity/pcb_nets/DRC) + 整包投产资料重出**★ ⇒
★**这是"投板前必须做、投板后做就是 2-4 周 + 板费"的活**★。连通性不变 (纯改名), 所以**风险可控**, 但**必须单独立项、单独请老板拍板**, ★**不要在评审时顺手改**★。

**hw-lead 建议 [推算]**: ★**先评审、后改名**★ ——
① 本轮把位号当作**临时位号 (占位)** 在评审中用功能名沟通 (如 `RAIL_VBUS_5V` → "VBUS_5V 轨");
② ★**评审意见收齐后**, 一次性做"位号规范化 + 整链重出", 然后再进投产包。
⇒ ★**这样老板今天就能评审图, 又不会在评审中途被 KiCad 偷偷改掉位号**★。

### ② 其它遗留 (不阻塞评审)

| 项 | 现状 | 判定 |
|---|---|---|
| 封装 (Footprint) | 全部 `TBD` | ★**本来就 TBD** (器件选型/封装未落), 与本轮无关; ★**投板前必须补齐**★ |
| 器件 Value | 取自 CSV `value` 列 (含中文说明, 如 `★22p@0.5mm (HIROSE FH12-22S…)`) | ★**这是给评审人看的说明, 挺好; 但 BOM 不该带这些长文本**★ (我们的 `HW/BOM_v1.csv` 另有一套) |
| P9 页只有 1 个器件 | `D_ESD_CAM` (其余 4 个跨页器件首现页在 P1) | ★**不是漏画**★ (C10 校验: 291 个器件无重无漏); ★**P9 是"跨铰链界面", 跨页器件归首现页是刻意规则**★ |
| `RAIL_*` / `NET_*` 这类"伪位号" | 它们是**单点汇流位** (一个 net 一个符号), 不是真器件 | ★**改名时要区分"真器件"和"伪位号"**: 伪位号改成 `R99/R100…` 会让 BOM 多出假料号★ ⇒ 建议**伪位号保留**、只改真器件的位号 |

---

## 7. 投产包里的原理图源文件 (★2026-11-11 11:0x 补投产包缺口★)

> ★**一句话结论**: 投产包以前**一份原理图源文件都没有** (只有 PDF/SVG/netlist/BOM/Gerber) ⇒ 板厂★**"能看不能改"**★,
> ★而且 10 个子页只活在 `HW/PCB/` 里 —— 拿到投产包的人根本不知道它们是原理图的一部分**★;
> 现在 `doc/sch_src/` 里 ★**12 个源文件 (11 个 .kicad_sch + 1 个 .kicad_pro) 齐了, 并且被 `chain_gate` 锁成闸**★
> (★**缺 / 多 / 内容是旧的 —— 三种情况都会让 chain_gate 变红 rc=1**★)。

### 7.1 之前缺的是什么 (★先复现问题★)

| 项 | 补之前 | 补之后 | 证据 |
|---|---|---|---|
| 投产包里的原理图**源文件** | ★**0 个**★ | ★**12 个**★ | [实测] `ls HW/PCB/production/doc/sch_src/ \| wc -l` |
| 投产包里的原理图**渲染件** | PDF 1 份 + SVG 11 份 (★**改不了**★) | 不变 | [实测] |
| 板厂拿到包后能干什么 | ★**只能看** (要改脚位/阻值 ⇒ 回我们这改 ⇒ 又一轮 2-4 周 + ¥4-8K)★ | ★**能看也能改**★ | [推算] |

### 7.2 文件清单 (★12 个, 与 `HW/PCB/` 下源文件**逐字节一致**★)

| # | 文件 | 作用 | md5 (与源文件一致) | 字节 |
|---|---|---|---|---|
| 1 | `demo_mainboard.kicad_sch` | ★**根页** (封面/目录) + 层级入口 | `a062cd4805cc23ccedd90337c212e7c1` | 26657 |
| 2 | `demo_mainboard_p1.kicad_sch` | P1 电源树 (83 器件) | `c533ff97baabc2ab70d81da1a5f6157b` | 202315 |
| 3 | `demo_mainboard_p2.kicad_sch` | P2 SoC 主控 | `ef848e94af51e30dabfe6d8eded09c21` | 45702 |
| 4 | `demo_mainboard_p3.kicad_sch` | P3 启动存储 | `789b84a3e67b2ee1e76e86d1a6773df6` | 33342 |
| 5 | `demo_mainboard_p4.kicad_sch` | P4 显示双出口 | `1a38ccc32691ddd589a9509982dee618` | 62124 |
| 6 | `demo_mainboard_p5.kicad_sch` | P5 MIPI-CSI 传感器 | `55d8d37b12fbe13c7636ab8f0b1e88e2` | 61468 |
| 7 | `demo_mainboard_p6.kicad_sch` | P6 高速差分与连接器 | `2ec77ffd6f6d37e1029c1657f0873944` | 29114 |
| 8 | `demo_mainboard_p7.kicad_sch` | P7 板级接口与测试点 (72 器件) | `235b4f5d266ca01292136497c13a3779` | 122866 |
| 9 | `demo_mainboard_p8.kicad_sch` | P8 时钟·复位·调试 | `1f3e16bdf0743e4846beff86296fc8c6` | 85020 |
| 10 | `demo_mainboard_p9.kicad_sch` | P9 跨铰链界面 | `3428ab0f3f2199c3693dd54f7b9520c5` | 22616 |
| 11 | `demo_mainboard_p10.kicad_sch` | P10 充电板(镜框) | `06e8b8148b4c69a066d58347b221e1ef` | 54039 |
| 12 | ★**`demo_mainboard.kicad_pro`**★ | ★**KiCad 工程文件** (见 7.3)★ | `3e504d2be83152e337949723e909be1b` | 9971 |

★**拷法**: `cp -p` (★**保留原 mtime**★ ⇒ 副本时间戳 = 源文件时间戳, 不会把"快照时间"冒充"设计时间"★)。
★**源文件一个字没改**: `HW/PCB/demo_mainboard*.kicad_sch` 与 `.kicad_pro` 的 md5 与 §2 表格完全一致 ⇒ ★**只拷不改**★。

### 7.3 ★为什么 `.kicad_pro` 必带 (★不是"顺手拷一个", 是承重件★)

`.kicad_pro` 是 ★**KiCad 的工程文件**★ —— 下面这些东西★**只存在它里面**, `.kicad_sch` 里一个都没有★:

| `.kicad_pro` 里的字段 | 装的是什么 | 丢了会怎样 | 证据 |
|---|---|---|---|
| `schematic.top_level_sheets` | ★**根页索引**: `[{filename: "demo_mainboard.kicad_sch", ...}]`★ | ★**11 个文件的层级里, KiCad 不知道哪个是根页**★ ⇒ 开出来层级断了 / 找不到子页 | [实测] JSON 解析 |
| `board.design_settings.rules` | ★**DRC 数值约束源**: `min_track_width 0.2` · `min_copper_edge_clearance 0.5` · `min_hole_to_hole 0.25` · `min_through_hole_diameter 0.3` · `min_via_diameter 0.5` · `min_via_annular_width 0.1` · `min_text_height 0.8` 等 20 条 | ★**板厂拿默认规则重跑 DRC ⇒ 出来的结论不是我们的结论**★ | [实测] JSON 解析 |
| `board.design_settings.rule_severities` | ★**33 条 DRC 严重度覆盖**★ (`missing_courtyard: ignore` · `footprint_type_mismatch: ignore` · `track_not_centered_on_via: ignore` … 其余 30 条降为 warning) | ★**我们故意 ignore 的项会被报成 error ⇒ 假警报; 我们故意降为 warning 的项会变成 error ⇒ 淹没真问题**★ | [实测] JSON 解析 |
| `net_settings.classes[0]` | Default 网络类: `track_width 0.2` / `clearance 0.2` / `diff_pair_width 0.2` / `diff_pair_gap 0.25` / `via_diameter 0.6` / `via_drill 0.3` | ★**差分线宽/间距/过孔全部回到 KiCad 默认 (0.2/0.25 是我们定的)**★ | [实测] JSON 解析 |
| `pcbnew.page_layout_descr_file` · `schematic.drawing` | 图纸设置 / 标注比例 | 出图格式漂 | [实测] JSON 解析 |

⇒ ★**一句话: 11 个 `.kicad_sch` 是"图", `.kicad_pro` 是"图的坐标系 + 尺子"; 没有尺子, 图照样能看, 但改出来的板不受我们规则约束**★。

### 7.4 `chain_gate` 怎么验它 (★闸, 不是一次性动作★)

★**改在 `state/chain_gate.py` (只加检查项, 已有判定逻辑与退出码口径未动)★**:

| 判据 | 代码位置 | 红了代表什么 |
|---|---|---|
| ① ★**12 个源文件进必需产物清单**★ | `PROD_REQUIRED` 加了 12 条 `doc/sch_src/...` ⇒ 环⑤ 准入从 18 项变 ★**30 项**★ | ★**投产包少了任一源文件 ⇒ 环⑤ ❌ ⇒ rc=1**★ |
| ② ★**自检: 文件名集合必须与 `HW/PCB/` 一一对应**★ | `expected_sch_src_files()` ★**动态扫** `HW/PCB/*.kicad_sch` + `demo_mainboard.kicad_pro`★ ⇒ 与 `sch_src/` 里的集合**完全相等** | ★**多一个/少一个都红**★ —— ★**防"加了旧的、漏了新的"**★ (新加了 p11 子页却没进投产包 ⇒ 门禁自己发现)★ |
| ③ ★**自检: 内容必须与源文件一致 (md5)**★ | `check_sch_src_pack()` 逐个比 md5 | ★**拿旧文件冒充新文件 ⇒ 红**★ |
| ④ 修法直给 | chain_gate 底部失败提示加了 ★**③ `cp -p HW/PCB/demo_mainboard*.kicad_sch HW/PCB/demo_mainboard.kicad_pro HW/PCB/production/doc/sch_src/`**★ | 红了不用猜怎么修 |

★**反向用例 (★必须红, 不许只跑一次绿就交卷★) —— 三种破法都试过★**:

| # | 破法 | 期望 | 实测 |
|---|---|---|---|
| 1 | ★**挪走 `demo_mainboard_p7.kicad_sch`**★ | 红 | ★**rc=1**★ · `⑤ ❌ · 29/30 必备产物齐全 · 缺: ★原理图源文件 子页 P7` + `原理图源文件与 HW/PCB/ **没有一一对应**: 缺 1 个` |
| 2 | ★**目录里多放一个 `README.txt`**★ | 红 | ★**rc=1**★ · `多 1 个 (例 ['README.txt'])` |
| 3 | ★**拿 p9 盖掉 p8 (装旧内容)**★ | 红 | ★**rc=1**★ · `内容与源不一致 1 个 (例 ['demo_mainboard_p8.kicad_sch'])` ★(★文件在, 所以①看不出来, 是②③抓到的★)★ |
| 4 | 全部恢复 | 绿 | ★**rc=0**★ · `30/30 必备产物齐全 · ★原理图源文件: 12 个源文件齐全 · 与 HW/PCB/ 一一对应 · 内容 md5 全一致 (11 个 .kicad_sch + 1 个 .kicad_pro)` |

### 7.5 ★★一个必须知道的坑 (★下次重跑投产包的人必看★★)

`state/gen_production_pack.sh` 第 25 行是 ★**`rm -rf "$OUT"`**★ ⇒ ★**重跑投产包生成会把 `doc/sch_src/` 一起删掉**★。
⇒ 好消息: ★**chain_gate 会立刻变红**★ (这正是闸该干的活) ⇒ 修法: 重跑后补上那 12 个文件 (§7.4 判据④给了现成命令)。
⇒ ★**待老板拍板**: ★**要不要把"拷 sch_src"这一步直接写进 `state/gen_production_pack.sh`**★ —— ★**本轮纪律外, 我没动它**★;
★★**hw-lead 建议写进去**★★: 否则每次重跑投产包都要人工补一次, ★**而人工补的那一次就是漏的那一次**★ (板厂拿到一个缺源文件的包, 是我们不知道的静默失败)。
⇒ ★★**【已拍板并已修】 boss 2026-11-11 11:1x 批准 ⇒ 已写进生成脚本 ⇒ 见 §7.7 (本坑已填)★★**★

### 7.6 本轮顺手修的一处陈旧红 (★证据: 零漂移★)

★**进本轮时 `chain_gate` 本来就是 rc=1**★: `投产包比 原理图 旧` —— ★**Gerber 是 11-09 04:10 出的, 原理图是 11-11 10:56 改的**★ (上一轮分页时只重出了原理图侧的产物)。
⇒ 修法: ★**跑 `bash state/gen_production_pack.sh` 重出整个投产包**★ (★**只读 PCB, 不碰板文件**★)。
⇒ ★**零漂移自证**★: 重出前后 ★**93 个文件逐个 md5 比对**★ ⇒ ★**61 个投产包文件**剥掉时间戳/生成日期字段后★**逐字节相同 (0 个有差异)**★;
★**`demo_mainboard.kicad_pcb` md5 仍 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` 仍 `3e504d2be83152e337949723e909be1b` · 网表/原理图 11 个文件 md5 全部未变**★ ⇒ ★**重出只刷新了时间戳, 一个字节的设计内容都没动**★ [实测]。

### 7.7 ★★`doc/sch_src/` 的唯一写入口 = `state/gen_production_pack.sh` (★2026-11-11 11:2x 第四件·老板批准★)★

> ★**一句话结论**: ★**"人工补"这一步根本不存在了**★ ——
> 以前 `doc/sch_src/` 是**人工拷**的 ⇒ ★**人工补的那一次就是漏的那一次**★ (板厂拿到一个缺源文件的包 = 我们不知道的静默失败);
> 现在 ★**投产包里 `sch_src/` 的唯一权威 = 生成脚本**★ ⇒ ★**人工塞的任何东西, 下次重出必被冲掉**★ [实测]。

#### 7.7.1 改了脚本哪几行 (★只改 `state/gen_production_pack.sh`, 一个文件★)

| # | 行号 | 改了什么 | 为什么 |
|---|---|---|---|
| 1 | ★**11-14**★ | 文件头注释加 `doc/sch_src/` 产出说明 + ★**"唯一权威 = 本脚本"**★ | 让人 (和未来的 agent) 知道这个目录是谁产的 |
| 2 | ★**26**★ | `mkdir -p "$OUT"/{gerbers,drill,pos,assembly,3d,doc/sch_svg,★**doc/sch_src**★}` | ★**先建目录** ⇒ 后面拷贝不用判断存在与否 |
| 3 | ★**82-113**★ (★新增一整块★) | ★**新增 `step "原理图源文件归档"` 块★** | ★**拷贝发生在"产生点"**★ ⇒ 不依赖任何人工步骤 |
| 3a | ★**95-96**★ | ★**`rm -rf "$SCH_SRC_DIR"` + `mkdir -p` (本块自带清空)★** | ★★**"唯一权威"这条不变量写在这一块里**, 不靠脚本开头第 25 行那个 `rm -rf "$OUT"` (70 行外) 撑着 ★★ ⇒ 人工塞的东西必被清掉 |
| 3b | ★**97-102**★ | ★**`for f in HW/PCB/*.kicad_sch` + `cp -p`★** | ★**动态扫目录, 不写死 12 个文件名**★ ⇒ 将来加 p11/p12 子页**自动跟上** (★已用沙箱实测, 见 7.7.3★) |
| 3c | ★**103-111**★ | ★**`PRO_FILE="${SCH%.kicad_sch}.kicad_pro"` + `cp -p` (缺了则 rc_all=1)★** | `.kicad_pro` 是承重件 (见 7.3) ⇒ ★**缺了必须响亮失败, 不许静默过**★ |
| 3d | ★**112-113**★ | ★**日志打出"拷了 N 个" + 文件名清单**★ | 交卷要看的那一行 |

★**拷法 `cp -p` (保留 mtime) 的实测**★: `demo_mainboard.kicad_sch` / `_p7` / `.kicad_pro` 三个副本的 mtime 与源文件 ★**纳秒级完全相同**★ (例: 根页 `2026-11-11 10:56:54.563551690` ⇒ 副本同) [实测] ⇒ ★**归档件时间戳 = 设计时间, 不是"打包时间"**★。

#### 7.7.2 反向用例输出 (★必须红过才敢交卷★)

| # | 破法 | 期望 | 实测 |
|---|---|---|---|
| 1 | ★**人工塞 `README.txt` + 假 `demo_mainboard_p11.kicad_sch` 进 `sch_src/`**★ | 闸红 | ★**rc=1**★ · `⑤ 投产资料包 ❌` + `原理图源文件与 HW/PCB/ **没有一一对应**: 多 2 个 (例 ['README.txt', 'demo_mainboard_p11.kicad_sch'])` |
| 2 | ★**跑 `bash state/gen_production_pack.sh`**★ | ★**两个都被冲掉**★ | ★**rc=0**★ · 日志 `拷了 12 个原理图源文件 → doc/sch_src/ (11 个 .kicad_sch + 1 个 .kicad_pro)` · ★**`README.txt` 不存在了**★ · ★**`demo_mainboard_p11.kicad_sch` 不存在了**★ · 文件数 14 ⇒ **12**★ |
| 3 | ★**再跑 `python3 state/chain_gate.py`**★ | 回绿 | ★**rc=0**★ · `30/30 必备产物齐全 · ★原理图源文件: 12 个源文件齐全 · 与 HW/PCB/ 一一对应 · 内容 md5 全一致 (11 个 .kicad_sch + 1 个 .kicad_pro)` |

★**⇒ 结论 (不是推测, 是上面三步跑出来的)**: ★**投产包里 `sch_src/` 的唯一权威 = 生成脚本**★ ——
★**人工塞的东西会被下次重出冲掉**★, ★**人工补这一步在流程上已经不存在了**★。

#### 7.7.3 ★动态扫目录真的"自动跟上"吗 (★沙箱实测, 不污染真树★)

在 `/home/yuewuya/dyntest/` 沙箱里 ★**抠出真脚本那一段拷贝代码原样跑**★ (只换路径), 造一个**新的 `demo_mainboard_p11.kicad_sch`**★:
⇒ 日志打 `拷了 13 个原理图源文件 → doc/sch_src/ (12 个 .kicad_sch + 1 个 .kicad_pro)` ⇒ ★**p11 自动跟上了**★ [实测]。
★**两个 glob 集合逐个比过**: `chain_gate.expected_sch_src_files()` (Python glob) 与 pack 脚本的 shell glob ⇒ ★**12 个文件, 集合完全相等, 差集为空**★ [实测] ⇒ ★**闸的期望与脚本的产出永远一致**★ (★两边都是动态扫, 谁都不用改★)。

#### 7.7.4 交卷前逐条跑 (★全部 rc 贴出来★)

| # | 命令 | rc | 关键输出 |
|---|---|---|---|
| ① | `bash state/gen_production_pack.sh` | ★**0**★ | ★**`拷了 12 个原理图源文件 → doc/sch_src/ (11 个 .kicad_sch + 1 个 .kicad_pro)`**★ + 12 个文件名清单 |
| ② | `python3 state/chain_gate.py` | ★**0**★ | `30/30 必备产物齐全 · ★原理图源文件: 12 个源文件齐全 · 与 HW/PCB/ 一一对应 · 内容 md5 全一致` |
| ③ | `python3 state/check_sch_erc.py` | ★**0**★ | `ERC 违规数 = 0 · 判定: ✅ 过` |
| ④ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` | — | ★**`611b869e13518c3c023fb178f91a0075`**★ (★**PCB 一字未动**★) |
| ⑤ | `ls HW/PCB/production/doc/sch_src/ \| wc -l` | — | ★**12**★ |
| ⑥ | `python3 state/merge.py` | ★**0**★ | `✅ STATE.yaml 已刷新` |

★**源文件零漂移**: `.kicad_pcb` `611b869e…` · `.kicad_pro` `3e504d2b…` · `.kicad_sch` `a062cd48…` · `netlist_v1.csv` `c78f9912…` · `BOM_v1.csv` `3ad04e1a…` · ★**sch_src 12 个与源文件 12/12 逐字节一致**★ [实测]。

---

## 8. 一句话交卷

★**原理图现在能评审了**: **11 页 A2 层级图, 每页内容都装得进纸 (最大 480×322 mm), PDF 每页完整 (改前只截到 17%)**★;
★**连通性没动**: 163 网 / 513 脚 与 `HW/netlist_v1.csv` 逐脚零差异, ERC 0, 板子 md5 `611b869e…` + fresh DRC 0 违规**★;
★**唯一待老板拍板**: 位号规范 (255/291 个位号 KiCad 判"未标注") — 建议"先评审、后一次性改名 + 整链重出", 别在评审中途动**★;
★**本轮追加**: 投产包里的**原理图源文件已补齐 (12 个) 并被 `chain_gate` 锁成闸** (缺/多/旧 三种破法都实测会红 rc=1) —— ★**板厂现在"能看也能改"**★ (见 §7);
★★**第四件 (11:2x)**: ★**"人工补"这一步已经不存在了**★ —— 拷 `sch_src` 的活写进了 ★**`state/gen_production_pack.sh`**★ (★**投产包里 `sch_src/` 的唯一权威 = 生成脚本**★; 人工塞的东西下次重出必被冲掉, ★**动态扫目录 ⇒ 将来加子页自动跟上**★) —— 见 §7.7。

---

## 9. ★★评审从这里开始 ★★ (★第五件 · 2026-11-11 11:3x★)

> ### ★**老板/评审人请从这里进**: ★**`HW/PCB/REVIEW_CHECKLIST_P2.md`** ★★
>
> ★**一句话**: ★**机器能查的都闭环了 (ERC 0 · 逐脚零差异 · DRC 0 · 投产包 30/30), 剩下只能靠人 ⇒ 这份清单把"人要看的"整理成了 16 条带实测数据的条目 + §4 的拍板表**★

| 要找什么 | 去哪 |
|---|---|
| ★**★"评审从哪开始"★**★ | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §0** ★★ |
| ★**PDF 在哪 + 怎么看** | ★**`HW/PCB/production/doc/demo_mainboard-sch.pdf`** (11 页 A2, md5 `4002c15666ec15da603b26e5935b99cf`); ★**重导命令在 REVIEW_CHECKLIST_P2.md §0**★ |
| ★**★页码对照表 (哪页是哪块)★**★ | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §1.8** ★★ (★本文件 §3 的同一张表, 权威版在清单里★) |
| ★**机器已经验过什么 (带命令)** | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §1** ★★ (11 条, 每条带 rc + 关键输出) |
| ★**★要人看的 16 条 (主体)★**★ | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §2** ★★ (每条 = 看什么 / 第几页 / 判定标准 / 现在的事实+来源 / 谁来定) |
| ★**已知遗留 + 要老板拍板** | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §3** ★★ (位号规范 · GND 130→66 那次事故的教训 · 本轮新挖出的 N1~N8) |
| ★**★拍板表 (老板填)**★ | ★**`HW/PCB/REVIEW_CHECKLIST_P2.md` §4** ★★ |
| ★**PDF 上看不清的脚, 这里有** | ★**`HW/netlist_v1_pins.csv`** (584 行 = 器件真实脚表) ★★ |

### ★★评审前必读的一条 (★2026-11-11 11:3x 实测★)★★

★★**"ERC 0 + 逐脚零差异 + DRC 0" 三个绿灯都真实, 但它们验的是『网名和脚序对不对』, 不是『器件画全了没』**★★
⇒ ★**原理图上多脚器件的脚只画了一部分**: **169/291 个器件的图上符号脚数 ≠ `HW/netlist_v1_pins.csv` 里的真实脚数** (J_USB_C 图上 4 脚 vs 真实 14 · J_SOM_P1 1 vs 10 · J_SOM_P3 8 vs 19 · CONN_CAM 19 vs 31 · CONN_LIGHT 11 vs 22 · U_CHG 10 vs 24) ⇒
★★**J_SOM_P2 / J_SOM_P4 在 11 张 sheet 上一个符号都没有 (23 个 SoM 球位在图上不存在)**, ★**163 个网里有 31 个 (含全部 20 根 MIPI 差分 + JTAG 4 根 + SPI 4 根) 图上只有伪位号 `NET_*`/`RAIL_*` 挂着, 没有任何真实器件的脚**★★
⇒ ★**⇒ 今天的 PDF 可以评审电源/阻容/测试点, 但 ★**评审不了接口对边 (camera/屏幕的差分线在图上一根都不在器件脚上)****★ ⇒ ★**建议: 先补图 (改 `state/gen_kicad_sch.py` 的 `parse_rows`), 补完再让老板逐页过** ★★
★**详细条目 = REVIEW_CHECKLIST_P2.md §2 的 R1 / R2** ★★

### ★**本轮 (第五件) 的纪律自证**★

| 项 | 结果 |
|---|---|
| ★**只写了两个文件**★ | `HW/PCB/REVIEW_CHECKLIST_P2.md` (新建) · `HW/PCB/SCHEMATIC_REVIEW_READY.md` (★**只加本节 §9**★) |
| ★**没动**★ | ★**任何生成器 / 原理图 / PCB / 网表 / 生产包 / 闸脚本**★ |
| ★**板子 md5**★ | ★**`611b869e13518c3c023fb178f91a0075`** (★一字未动★)★ |
| ★**五个 rc**★ | ① `check_sch_erc.py` rc=0 · ② `check_sch_loadable.py` rc=0 · ③ `chain_gate.py` rc=0 · ④ `md5sum` = `611b869e…` · ⑤ `merge.py` rc=0 |
