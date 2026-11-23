# MECH/BOARD_GEOM_CALIBER_STATUS.md —— 结构侧权威表口径状态页 (漂移清单 + 现役真值指向 + 条件式处理方案)

> ★**性质**: 纯分析 + 口径状态声明页 · ★**零写板 · 零改既有 MECH 数据 · 零落表 · 零外发** ★
> ★**派活**: 项目总工 (main / moli) · ISS-342 (队列自动派活 · cron fb67af40) · 2026-11-22 ★
> ★**来源**: ISS-341 交回 main 的卡点表 C6 (★`HANDOFF/2026-11-22_mech-lead_ISS341_板那一趟画哪块板相容性判定.md` §B5-1 第 6 行★) ★
> ★**交卷人**: 结构总工 (mech-lead · 带散热) ★
> ★**机器闸**: `python3 MECH/check_board_geom_caliber_drift.py` (只读漂移检测闸) · `--selftest` (≥3 条, 末行 `ALL TESTS PASS`) ★
> ★**配套订正**: `MECH/BOARD_GEOM_30MM.md` 表头【追加式】订正 (老字一个没删) ★

---

## ★§1 · 漂移清单 (机器可判 · 逐行) ★

### ★§1.0 · 扫描范围与统计口径 (★两个 scope, 别混★) ★

**★ scope A (★任务书指定口径: `grep -rln RK3576 MECH/`★)**:
- ★**扫描命令 (本机实跑)**: `grep -rln RK3576 MECH/` ⇒ ★**24 个文件命中** ★ (★原 21 · ★本轮新增 3 个 = 本页自产 `MECH/BOARD_GEOM_CALIBER_STATUS.md` + 本单自产闸 `MECH/check_board_geom_caliber_drift.py` + 该闸的编译缓存 `MECH/__pycache__/check_board_geom_caliber_drift.cpython-314.pyc`·★main 2026-11-23 00:1x 实读订正★) ★
- ★**不计入处置范围 (2 类, 共 5 个文件)**: ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md.bak_20261117_1813_iss295` (1 个 .bak)** ★ + ★**`MECH/__pycache__/check_board_frame_candidate_compat_gate.cpython-314.pyc` / `fit_check_v3_30mm.cpython-314.pyc` / `skeleton_section_check.cpython-314.pyc` / `check_board_geom_caliber_drift.cpython-314.pyc` (4 个编译缓存·★第 4 个是本轮新闸自己的缓存·main 2026-11-23 00:1x 实读订正★)** ★ ⇒ ★**`.bak` 与 `__pycache__` 一律不计入处置范围 (备份/编译产物, 改它们无意义且污染可复现性)** ★
- ★**scope A 真数 (需判的文档与脚本) = 24 − 5 = 19 个文件** ★ (★原 17 · ★新增 2 件 = 本页 + 漂移闸, ★两者都已在 §1.4 scope B 表里登记为【自指噪声】(B04 / B25) ⇒ 无遗漏★) (★§1.1 主表 25 行全部覆盖这 19 个文件, 无遗漏★)
- ★**漂移类型图例**: ①自称现行板框 · ②绑 RK3576 · ③绑 60×30 · ④绑旧板宽 12/15mm · ⑤其它 ★
- ★**处置图例**: **该订正** (本单已做或须有人做) · **该标作历史** (加定性段/横幅, 不逐个改数字) · **不动** (本单零改动) ★

**★ scope B (★机器闸全量扫描: 过期口径词 × 现行口径词, 不限 RK3576★)**:
- ★**命令**: `python3 MECH/check_board_geom_caliber_drift.py` ⇒ ★**扫描 125 个文件 / 命中 107 处 / 33 个文件** ★ (★原 95 处 · ★增量 = 本轮自产的 2 件 (本页 + 漂移闸) 的自指命中·★main 2026-11-23 00:1x 实读订正★) (★rc=2 ★因为确实有漂移★)
- ★**scope B 比 scope A 宽**: 它把**只写 60×30 / 旧板宽 12·15mm 但不写 RK3576** 的行也抓出来 (例: `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` 的「MECH 现行框 60×30 套 A」· `MECH/board_frame_feasibility.py` 的「产品板 60×30 套 A (MECH 现行)」) ⇒ ★**这些同样是静默投毒源, 必须登记** ★
- ★**scope B 的 33 个文件 = scope A 的 19 个 (内含) + scope A 之外的 14 个** ⇒ ★**两个 scope 的并集 = 33 个文件 (清单见 §1.4)** ★

### ★§1.1 · 主表 (17 个文件 · 逐行) ★

| # | 文件 | 行号 | 原文摘录 (≤30 字) | 漂移类型 | 处置 | 依据 (行号) |
|---|---|---|---|---|---|---|
| 1 | `MECH/BOARD_GEOM_30MM.md` | **17** | 「本表是结构侧 (MECH) 对 60×30mm **现行板**的唯一权威几何口径」 | ①③ | **该订正** (★追加式表头声明, 老字未删★) | `MECH/BOARD_GEOM_30MM.md:17` + 新增 `:2-13` 声明段 |
| 2 | `MECH/BOARD_GEOM_30MM.md` | **33** | 「板宽 30mm / 板长 60mm / 板厚 1.00mm (6 层) —— **现行板框**」 | ①③ | **该标作历史** (老行保留留档, 已由表头声明覆盖) | `MECH/BOARD_GEOM_30MM.md:33` |
| 3 | `MECH/BOARD_GEOM_30MM.md` | **34** | 「主控 RK3576 (FCCSP698L, 17.20×16.10mm) —— **现行 SoC**」 | ② | **该标作历史** (同上) | `MECH/BOARD_GEOM_30MM.md:34` |
| 4 | `MECH/BOARD_GEOM_30MM.md` | **54** | 「## 2. SoC 占位与逃线带 (RK3576)」 | ② | **不动** (帧 `F30A` 的几何推导, 留档) | `MECH/BOARD_GEOM_30MM.md:54` |
| 5 | `MECH/BOARD_GEOM_30MM.md` | **217-222** | 「该迁 (驱动判定) / 标作废 (不迁)」影响面表 | ③④⑤ | **不动** (★它自己已把 12/15mm 判死并留档★) | `MECH/BOARD_GEOM_30MM.md:217-222` |
| 6 | `MECH/cross_review_check.py` | **417** | 「结构侧权威几何口径: BOARD_GEOM_30MM.md (板 60×30 / RK3576 / 套 A)」 | ①②③ | **该订正** (★脚本自报权威表口径 = 静默投毒源; 本单只登记, 未改★) | `MECH/cross_review_check.py:417` |
| 7 | `MECH/fit_check.py` | **26** | 「权威几何口径: BOARD_GEOM_30MM.md (板 60×30 / RK3576 / 套 A)」 | ①②③ | **该订正** (★同上; 本单只登记, 未改★) | `MECH/fit_check.py:26` |
| 8 | `MECH/fit_check.py` | **18 / 130 / 399** | 「已经是按 30mm / 板长 60 / RK3576 重写过的**现行版**」 | ②③ | **该标作历史** (v2 基线已死, 文件头已带横幅) | `MECH/fit_check.py:18,130,399` |
| 9 | `MECH/fit_check.py` | **77** | 「"pcb_w": 12.00 …… **作废值**」 | ④ | **不动** (★已自标作废★) | `MECH/fit_check.py:77` |
| 10 | `MECH/fit_check_v3_30mm.py` | **4 / 11 / 105 / 208 / 303** | 「板宽 30mm / **RK3576** 基线下的……检查」 | ②③ | **该标作历史** (★绿灯/红灯对现役板不成立★) | `MECH/fit_check_v3_30mm.py:4,11,105,208,303` |
| 11 | `MECH/skeleton_section_check.py` | **7 / 302** | 「现按 60×30 板 + RK3576」「迁版: 60×15 / RK3588 ⇒ 60×30 / RK3576」 | ②③④ | **该标作历史** (驱动重量账, 结论不适用于现役板) | `MECH/skeleton_section_check.py:7,302` |
| 12 | `MECH/skeleton_section_check.py` | **53-55** | 「PCB_L=60.00 / PCB_W=30.00 / PCB_T=1.00」 | ③ | **该标作历史** (★板框常量硬编, 改它 = 改判定★) | `MECH/skeleton_section_check.py:53-55` |
| 13 | `MECH/pinset2_mech_check.py` | **4 / 13 / 27 / 67 / 69** | 「独立复算 (板框 60×30 / RK3576 / PIN-SET-2 套 A)」 | ②③ | **该标作历史** (★38 项复算对现役板不成立★) | `MECH/pinset2_mech_check.py:4,13,27,67,69` |
| 14 | `MECH/pinset2_mech_check.py` | **61-63** | 「PCB_L = 60.00 / PCB_W = 30.00」 | ③ | **该标作历史** | `MECH/pinset2_mech_check.py:61-63` |
| 15 | `MECH/pinset2_mech_check.json` | **11 / 366** | 「"name": "RK3576」「60×30/RK3576 下实测只压 2/3」 | ②③ | **该标作历史** (★机读产物, 随脚本走★) | `MECH/pinset2_mech_check.json:11,366` |
| 16 | `MECH/print/README.md` | **15** | 「主控 \| ARS45 \| **RK3576** (FCCSP698L 16.1×17.2)」 | ② | **该标作历史** (Rev B 打印包基线, 不是现役板) | `MECH/print/README.md:15` |
| 17 | `MECH/print/MEASURE_CHECKLIST.md` | **5** | 「基线已改为 板宽 30 / 板长 60 / RK3576 ⇒ Rev A 已过期」 | ②③ | **该标作历史** (打印包基线, 与现役板无关) | `MECH/print/MEASURE_CHECKLIST.md:5` |
| 18 | `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` | **102 / 263** | 「F-2 现役板与另两套是两种物理产品」/「D-1-4 MECH 域板框真源」 | ④⑤ | **不动** (★第 102 行已正确★); 第 263 行指向的 `MECH_BUDGET.md` 见 §1.2 | `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md:102,263` |
| 19 | `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` | **60 / 88 / 135** | 「F30A = 另一种物理产品 (RK3576 SoC 直上板)」 | ②⑤ | **不动** (★ISS-341 机器判定页, 口径已正确★) | `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md:60,88,135` |
| 20 | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | **21** | 「与 BOARD_GEOM_30MM.md 的 RK3576 **老基线** —— 只引用, 一个字不改」 | ②⑤ | **不动** (★已自称「老基线」★) | `MECH/BOARD_ONEPASS_MECH_SYNC.md:21` |
| 21 | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | **20** | 「与 BOARD_GEOM_30MM.md 的 RK3576 **老基线** —— 只引用, 一个字不改」 | ②⑤ | **不动** (★同上★) | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md:20` |
| 22 | `MECH/check_board_frame_candidate_compat_gate.py` | **495 / 846 / 849 / 858** | 「rk3576_hits」「结构侧权威表的主控口径 = …… 而本表仍是 RK3576 口径」 | ⑤ | **不动** (★这个闸【已经能检出】本漂移, 是本单的正向证据★) | `MECH/check_board_frame_candidate_compat_gate.py:495,846,849,858` |
| 23 | `MECH/_apply_iss017_frag.py` | **79 / 103 / 120** | 「60x30=1800mm² ⇒ RK3576 装得下」「Rev B 按板宽 30 / 板长 60 / RK3576」 | ②③ | **不动** (★历史落片脚本, 改它 = 改历史闭环记录★) | `MECH/_apply_iss017_frag.py:79,103,120` |
| 24 | `MECH/_apply_iss017_measurements.py` | **31 / 43** | 「Rev B 按板宽 30mm/板长 60mm/RK3576/PIN-SET-2 重做」 | ②③ | **不动** (历史落片脚本) | `MECH/_apply_iss017_measurements.py:31,43` |
| 25 | `MECH/_frag_rebase_20261106.py` | **202 / 250** | 「板框 60×30 = 1800mm²: RK3576 基线」「HW/pcb60x30_check.json sec4_holes (RK3576)」 | ②③ | **不动** (历史 rebase 脚本) | `MECH/_frag_rebase_20261106.py:202,250` |

> ★**表注**: 上表 25 行覆盖 §1.0 的 **17 个文件全部** (★行 1-5 同属 `BOARD_GEOM_30MM.md`, 行 8/9 同属 `fit_check.py`, 行 10 同属 `fit_check_v3_30mm.py`, 行 11/12 同属 `skeleton_section_check.py`, 行 13/14 同属 `pinset2_mech_check.py`★); ★**每个文件至少 1 行, 无遗漏** ★

### ★§1.2 · 补充表 · ④类漂移 (旧板宽 12/15mm · 不在 RK3576 grep 命中集内) ★

| # | 文件 | 行号 | 原文摘录 (≤30 字) | 漂移类型 | 处置 | 依据 (行号) |
|---|---|---|---|---|---|---|
| S1 | `MECH/MECH_BUDGET.md` | **89** | 「ARS45 主控 PCB …… **60 × 15 × 1.0** …… 板重 0.48→1.67g」 | ④ | **该订正** (★MECH 域【空间预算主表】仍挂作废板宽 15; 本单只登记, 交 main★) | `MECH/MECH_BUDGET.md:89` + `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md:263` |
| S2 | `MECH/verify_budget.py` | **155** | 「("ARS45 主 PCB", 5.0, 7.0, "[推算]")」 | ④ | **该订正** (★整机质量预算按旧板算; 与 S1 同源★) | `MECH/verify_budget.py:155` + `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md:262` |
| S3 | `MECH/BOARD_WIDTH_15MM.md` | **245** | 「本节是"老口径为什么必须废掉"的留档, **不是现行口径**」 | ④ | **不动** (★已自标作废★) | `MECH/BOARD_WIDTH_15MM.md:245` |
| S4 | `MECH/board_width_15mm_check.py` | **14 / 233** | 「现行口径 = PIN-SET-2 …… 现行口径复算见 pinset2_mech_check.py」 | ④ | **不动** (★已指向现行复算, Q4 段自标留档★) | `MECH/board_width_15mm_check.py:14,233` |

### ★§1.3 · 处置汇总 (逐类条数) ★

| 处置 | 条数 | 代表 |
|---|---|---|
| ★**该订正** ★ | **6 条** | #1 (本单已做: 表头追加式声明) · #6 · #7 (脚本自报权威表口径 ⇒ 静默投毒源, **本单只登记未改**) · S1 · S2 · (追加式声明段本身) |
| ★**该标作历史** ★ | **10 条 / 8 个文件** | #2 · #3 · #8 · #10 · #11 · #12 · #13 · #14 · #15 · #16 · #17 |
| ★**不动** ★ | **13 条 / 9 个文件** | #4 · #5 · #9 · #18 · #19 · #20 · #21 · #22 · #23 · #24 · #25 · S3 · S4 |
| ★**scope B 新增文件 (16 个) 处置** ★ | **全部登记为「该标作历史 / 该订正」, 本单零改动** | 见 §1.4 ★ |
| ★**零写板 / 零改老数 / 零落表 / 零改别人分片** ★ | **本单全部** | 见交卷页 `HANDOFF/2026-11-22_mech-lead_ISS342_结构侧权威表口径漂移.md` §B7 |

★**处置原则 (一句话)**: ★**凡是【自称现行】的 (①) 一律该订正; 凡是【绑死 RK3576 / 60×30 的历史计算器】一律该标作历史 (加定性段, 不逐个改数字 —— 改了就是把「一块不存在的板」重建成「看起来像现役板」); 凡是【已经自称老口径 / 已经指向真源】的一律不动** ★

### ★§1.4 · scope B 机器闸全量扫描的命中文件 (33 个, 逐个列全 · 无省略★) ★

★**机器读数 (本机实跑, 2026-11-22 · ★计数于 2026-11-23 00:1x 订正★)**: `python3 MECH/check_board_geom_caliber_drift.py` ⇒ ★**扫描文件 125 · 命中 107 处 (★原 95·自指增量★) · 33 个文件 · rc=2** ★

| # | 文件 | 命中处数 | 该文件里的典型漂移原句 (≤30 字) | 处置 |
|---|---|---|---|---|
| B01 | `MECH/BOARD_FRAME_DECISION_INPUT.md` | 4 | 「② 产品板 60×30 套 A (MECH 现行)」 | 该标作历史 (★它自己已注明「本域现行权威口径」是旧口径, 但没写它已过期★) |
| B02 | `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` | 3 | 「板框最终拍 B160x100 / F30A / P60x15 哪一个」 | 不动 (★是三选一的选项页, 不是自称现行★) |
| B03 | `MECH/BOARD_GEOM_30MM.md` | 4 | 「本表是结构侧对 60×30mm 现行板的唯一权威几何口径」 | **该订正 (本单已做: 表头追加式声明)** |
| B04 | `MECH/BOARD_GEOM_CALIBER_STATUS.md` | 5 | (本页引用漂移原句 ⇒ 自指噪声) | 不动 (★自指噪声; 可用 `--whitelist` 从命令行去掉★) |
| B05 | `MECH/BOARD_ONEPASS_MECH_SYNC.md` | 2 | 「帧 id 三件套: B160x100 / F30A / P60x15」 | 不动 (已带帧标) |
| B06 | `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | 1 | 「帧 id 三件套: B160x100 / F30A / P60x15」 | 不动 (已带帧标) |
| B07 | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | 3 | 「帧: 60×30 套A (BOARD_GEOM_30MM.md §1/§3)」 | 不动 (已带帧标 + 已写「物理上装不进」) |
| B08 | `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` | 5 | 「② 产品目标板 60×30 套 A (MECH 现行)」 | 该标作历史 (★ISS-271/276 已确认它是另一形态★) |
| B09 | `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` | 5 | 「F30A 在 BOARD_GEOM_30MM.md 里绑的是 RK3576」 | 不动 (★ISS-341 机器判定页, 口径已正确★) |
| B10 | `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` | 6 | 「板框 ② 产品板 60×30 (MECH 现行)」 | **该订正 (★★「MECH 现行」四字 = 最毒的投毒源之一★★)** |
| B11 | `MECH/DFM_REVIEW.md` | 1 | 「全部尺寸链按板宽 30mm / 板长 60mm」 | 该标作历史 |
| B12 | `MECH/HW_CROSS_REVIEW.md` | 1 | 「主 PCB 60×15」 | **该订正 (④类 · 旧板宽 15)** |
| B13 | `MECH/MECH_NEEDS_TRIAGE.md` | 3 | 「现行套 A (BOARD_GEOM_30MM.md §3 …)」 | 该标作历史 |
| B14 | `MECH/ONETRIP_BOARD_FRAME_FREEZE_GATE.md` | 2 | 「判的是现行几何口径的自洽性 (60×30 / 1.00mm / 6 层)」 | 该标作历史 (★冻结闸自洽性判定, 不等于现役★) |
| B15 | `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` | 2 | 「D_LED_G 首选窗口 … 属帧 F30A」 | 不动 (已带帧标) |
| B16 | `MECH/SERVICE_PORT_ISS092.md` | 3 | 「本文 §5.1 表的板宽口径已是现行 60×30」 | 该标作历史 |
| B17 | `MECH/_apply_iss017_measurements.py` | 1 | 「fit_check_v3_30mm.py (板宽 30mm / RK3576 基线 …)」 | 不动 (历史落片脚本) |
| B18 | `MECH/_frag_rebase_20261106.py` | 1 | 「板框 60×30 = 1800mm²: RK3576 基线」 | 不动 (历史 rebase 脚本) |
| B19 | `MECH/_frag_update_iss229.py` | 1 | 「PCB_OUTLINE_60x15.md 里还有三处旧口径的数」 | 不动 (已自称旧口径) |
| B20 | `MECH/board_frame_feasibility.py` | 3 | 「产品板 60×30 套 A (MECH 现行)」 | **该订正 (脚本常量里的「MECH 现行」)** |
| B21 | `MECH/board_port_opening_s6_check.py` | 3 | 「产品目标板 60×30 套 A (MECH 现行)」 | **该订正 (同上)** |
| B22 | `MECH/check_board_frame_candidate_compat_gate.py` | 2 | 「结构侧权威表的主控口径 = … 而本表仍是 RK3576 口径」 | 不动 (★这个闸【已经能检出】本漂移★) |
| B23 | `MECH/check_board_frame_coords.py` | 4 | 「60×30 套A 坐标; 现役板是 160×100 台架板」 | 不动 (已并列两套 + 反向用例) |
| B24 | `MECH/check_board_frame_freeze_gate.py` | 2 | 「现行口径自洽: 60×30 / 1.00mm / 6 层 / 套 A」 | 该标作历史 |
| B25 | `MECH/check_board_geom_caliber_drift.py` | 9 | (本闸自己的 selftest 合成夹具 ⇒ 自指噪声) | 不动 (★自指噪声; 可用 `--whitelist` 从命令行去掉★) |
| B26 | `MECH/cross_review_check.py` | 2 | 「结构侧权威几何口径: BOARD_GEOM_30MM.md (60×30 / RK3576)」 | **该订正 (脚本自报权威表口径 = 静默投毒源)** |
| B27 | `MECH/fit_check.py` | 4 | 「权威几何口径: BOARD_GEOM_30MM.md (板 60×30 / RK3576)」 | **该订正 (同上)** |
| B28 | `MECH/fit_check_v3_30mm.py` | 2 | 「板宽 30mm / RK3576 基线下的装配干涉检查」 | 该标作历史 (★绿灯/红灯对现役板不成立★) |
| B29 | `MECH/hinge_usb_check.py` | 1 | 「用 MECH_BUDGET 已锁死的结构基线 (… 板宽 12mm …)」 | 该订正 (④类 · 12mm) |
| B30 | `MECH/hw_cross_review_check.py` | 1 | 「主 PCB 板宽 = 30.00mm (现行 60×30 板)」 | 该标作历史 |
| B31 | `MECH/jd_y0_feasibility.py` | 3 | 「产品目标板 60×30 (套 A, MECH 现行口径)」 | **该订正 (脚本常量里的「MECH 现行口径」)** |
| B32 | `MECH/pinset2_mech_check.py` | 1 | 「迁到现行板 (60×30 / RK3576 / 套 A)」 | 该标作历史 (★38 项复算对现役板不成立★) |
| B33 | `MECH/service_port_check.py` | 1 | 「主 PCB 板宽 = 30.00mm (现行 60×30 板)」 | 该标作历史 |

> ★**表注**: ★**本表 33 行 = scope B 命中文件全集 (机器读数: 95 处 / 33 个文件), 逐个列全无省略** ★
> ★**★其中最该先动的 5 个 (「自称 MECH 现行」四字 = 最毒的投毒源)★**: ★**B10 `DEBUG_PORT_LAYOUT_CONSTRAINTS.md` · B20 `board_frame_feasibility.py` · B21 `board_port_opening_s6_check.py` · B26 `cross_review_check.py` · B27 `fit_check.py` · B31 `jd_y0_feasibility.py` (共 6 个) —— 本单【零改动】, 全部登记给 main** ★
> ★**自指噪声 2 处 (B04 本页 / B25 闸自身夹具)**: ★**不是漂移, 是「引用了漂移原句」⇒ 用 `--whitelist` 从命令行传入行段即可去掉; 默认白名单只含 §3 追加声明段** ★

---

## ★§2 · 现役真值指向 (一行一条 · 必须写文件路径) ★

- ★**板框真值**: ★**现役板 = 160×100mm / 8 铜层 / 1.60mm / 186 封装** ⇒ ★**权威页 = `HW/PCB/BOARD_FRAME_CALIBER.md`** ★ (★该页 §1.1 已登记「MECH 权威表主控没跟着换」; 板框/层数/板厚/封装数 = 死值, 不许互相代入★)
- ★**三候选判决**: ★**`MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md`** (★ISS-341 机器判定, 已签收★) ⇒ ★**`B160x100` = 改现役板一次 (S1~S13 坐标继续有效) · `F30A` 60×30 与 `P60x15` 60×15 = 重画一块新板 (现役板 186 封装 / 45 条未连接 / S1~S13 全作废)★★**
- ★**主控口径**: ★**现役主控 = RK3572 (SoM 直插, 4 组 100 脚座 `J_SOM_P1..P4`, 承载区 53.80×46.78mm)** ⇒ ★**「RK3576 = 现行 SoC」这句是死的** ★ (★出处 `HW/PCB/BOARD_FRAME_CALIBER.md` §1.1 + `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` §1.2★)
- ★**坐标帧唯一权威**: ★**`HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES`** ⇒ ★**`B160x100` (现役) / `F30A` (60×30 套A) / `P60x15` (60×15), 三套坐标不可互相代入** ★
- ★**物理不可行性判据**: ★**现役 SoM 承载区高 46.78mm > 30 (60×30 板宽, 差 −16.78) 且 > 15 (60×15, 差 −31.78) ⇒ 「60×30 + RK3576」这一整条口径对现役板【不成立】** ★
- ★**本域漂移清单页**: ★**`MECH/BOARD_GEOM_CALIBER_STATUS.md`** (★本页★)
- ★**只读漂移检测闸**: ★**`MECH/check_board_geom_caliber_drift.py`** ★
- ★**旧表 (历史留档)**: ★**`MECH/BOARD_GEOM_30MM.md`** (★2026-11-11 口径, 已加表头状态声明★)

---

## ★§3 · 条件式处理方案 (★两种老板答案分别怎么走 · ★不许替老板拍★) ★

### ★§3.1 · 若第一问 = 台架板 (160×100) ★

- ★**`MECH/BOARD_GEOM_30MM.md` 整张降为「历史口径 · 对应另一种物理产品 (F30A = RK3576 SoC 直上板)」** ★
- ★**本单已做的表头声明 = 终态, 不必再改数据** ⇒ ★**老字继续留着 (留档价值: ISS-017/042/192 的复算可复现)** ★
- ★**下游脚本 (`pinset2_mech_check.py` / `skeleton_section_check.py` / `fit_check*.py`) 的绿灯/红灯对现役板【一律不成立】** ⇒ ★**该迁到 160×100 口径 (★本单只登记 need, 不迁脚本★) ★**
- ★**本单【不】因这一答案再动一个字** ★

### ★§3.2 · 若第一问 = 产品内板 60×30 ★

- ★**该档的主控形态【未定】(第二问没到): RK3572-SOM 直插 还是 RK3576-SoC 直上** ★
- ★**60×30 这一档与 RK3572 【不自洽】**: ★**承载区高 46.78 > 板宽 30, 差 −16.78 ⇒ 物理装不下** ★ ⇒ ★**若第二问答「RK3572-SOM 直插」⇒ 60×30 这一档必须重算 (承载区根本放不进去); 若答「RK3576-SoC 直上」⇒ 本表的历史口径反而是那一档的自洽口径** ★
- ★**本单的表头声明【仍然成立】** —— ★**它只声明「60×30 / RK3576 不是现役板框」, 不主张「60×30 不存在」** ⇒ ★**数据要不要重算, 等第二问 + C5 那一档开出来再说** ★
- ★**本单【不】替第二问预设答案, 也【不】把第二问挂成本单的阻塞项** ★

### ★§3.3 · 两个答案共同成立的部分 (★本单已经做完的部分★) ★

- ★**口径状态声明** (哪张表过期了、现役真值在哪) ⇒ ★**对两个答案都成立, 因为「60×30 / RK3576 = 现行板框」这句话【现在】就是错的** ★
- ★**漂移清单** ⇒ ★**对两个答案都成立 (清单是【现状陈述】, 不是【方案选择】)** ★
- ★**只读漂移检测闸** ⇒ ★**对两个答案都成立 (它只报「哪里还写着旧口径」, 不判「该写哪套」)** ★

---

## ★§4 · 一句写死的话 (★免得被当成拍板★) ★

> ★★**「本单只声明口径状态 (哪张表过期了、现役真值在哪), 不决定这一趟画哪块板 —— 那是老板的第一问。」** ★★

★**附**: ★**本单【不代拍】第一问 (台架板 160×100 vs 产品内板 60×30), 也不代拍第二问 (RK3572-SOM 直插 vs RK3576-SoC 直上); 本页全文没有任何一处把「这一趟画哪块板」当成已决** ★

---

## ★§5 · ★ISS-352 第 2 批 · scope A / scope B 真数【追加式】订正 (2026-11-23 · mech-lead) ★

★**性质**: 追加式订正 —— ★**§1 ~ §4 的老字一个字都没删**(★本节之前的内容逐字节保留★) ★
★**本节的每一个数 = 迁完之后【本机实跑重读】的真值** (★不是沿用上一轮的数·迁完文件集合变了必须重读★) ★
★**迁完的范围**: ISS-345 第 1 批 2 脚本 (`pinset2_mech_check.py` / `skeleton_section_check.py`) ·
第 2 批 3 脚本 (`fit_check_v3_30mm.py` / `cross_review_check.py` + `fit_check.py` 退役标记) ·
既有帧表脚本 2 个只补帧 id 标签行 (`board_port_opening_s6_check.py` / `jd_y0_feasibility.py`) ·
新建机器闸 1 个 (`check_mech_dual_caliber_gate.py`) ★
★**扫描口径 (与 §1.0 同款)**: scope A = `grep -rln RK3576 MECH/`; scope B = `python3 MECH/check_board_geom_caliber_drift.py` (域 MECH · 跳过 `.bak` / `__pycache__` / `.git` / `*.pyc`) ★

### ★§5.1 · scope A (grep RK3576) 本轮真数 ★

| 项 | 本轮实跑真值 | 与 §1.0 老数的差 | 差的原因 (逐条可查) |
|---|---|---|---|
| 命中文件数 | **24** | **±0** | ★命中文件集合与迁移前基线**逐个文件比对完全一致** (差集为空)★ |
| 不计入处置范围 (`.bak` + `__pycache__/*.pyc`) | **6 个** | **+1** | 新增编译缓存 `MECH/__pycache__/pinset2_mech_check.cpython-314.pyc` (第 1 批跑兼容闸时被 `check_board_frame_candidate_compat_gate.py` import 产生) |
| ★**scope A 真数 (需判的文档与脚本)** ★ | **18** | **−1** | = 24 − 6; ★老数 19 的分母用的是 5 个不计入文件 (当时盘上还没有第 5 个 .pyc)★ |

★**不计入的 6 个 (逐个列全)**: `MECH/BOARD_ONEPASS_MECH_SYNC.md.bak_20261117_1813_iss295` (1 个 .bak) +
`MECH/__pycache__/check_board_frame_candidate_compat_gate.cpython-314.pyc` /
`MECH/__pycache__/check_board_geom_caliber_drift.cpython-314.pyc` /
`MECH/__pycache__/fit_check_v3_30mm.cpython-314.pyc` /
`MECH/__pycache__/pinset2_mech_check.cpython-314.pyc` /
`MECH/__pycache__/skeleton_section_check.cpython-314.pyc` (5 个编译缓存) ★

### ★§5.2 · scope B (漂移闸全量扫描) 本轮真数 ★

| 项 | 本轮实跑真值 | 与 §1.0 老数的差 | 差的原因 |
|---|---|---|---|
| 扫描文件数 | **126** | **+1** | 新增 `MECH/check_mech_dual_caliber_gate.py` (本单新建) |
| ★**命中处数** ★ | **107** | ★**±0** ★ | ★**零新增漂移命中**★ (rc=2 = 迁移前既有状态, 预期) |
| 命中文件数 | **33** | **±0** | 命中文件集合未变 |

★**新闸自己 0 命中 (设计如此)**: 闸里每一条含过期口径词的行都自带「历史 / 作废 / 不可混用」标记 ⇒ 漂移闸不把它算成未声明漂移 (★实测: 漂移输出里 `MECH/check_mech_dual_caliber_gate.py` 的命中行数 = **0**★) ★

### ★§5.3 · 本单动过的文件 · 逐个命中数前后对照 (★零新增★) ★

| 文件 | 本单处置 | 命中处数 (前 → 后) | 差 |
|---|---|---|---|
| `MECH/fit_check_v3_30mm.py` | 迁双口径 (FRAMES + PROSE + 切档) | 2 → 2 | ±0 |
| `MECH/fit_check.py` | ★**明确标退役** (机器标记 `MECH_CALIBER_RETIRED`) | 4 → 4 | ±0 |
| `MECH/cross_review_check.py` | 迁双口径 (FRAMES + PROSE + 三源校验) | 2 → 2 | ±0 |
| `MECH/board_port_opening_s6_check.py` | 只补帧 id 标签行 (零行为变化) | 3 → 3 | ±0 |
| `MECH/jd_y0_feasibility.py` | 只补帧 id 标签行 (零行为变化) | 3 → 3 | ±0 |
| `MECH/board_frame_feasibility.py` | ★**零改动** (三档帧表已逐字对齐权威页) ★ | 3 → 3 | ±0 |
| `MECH/check_mech_dual_caliber_gate.py` | ★**新建机器闸** ★ | — → 0 | 新增 0 命中 |

### ★§5.4 · §1.1 主表里「行号」引用的现落点 (★老字仍留着·新落点列在下表★) ★

| 文件 | §1.1 老引用行 | 现落点 | 说明 |
|---|---|---|---|
| `MECH/cross_review_check.py` | 388 (C-16 标题) | **165** | 文字逐字保留, 只是搬进了帧级叙述表 |
| `MECH/cross_review_check.py` | 417 (权威口径行) | **171** | 同上 |
| `MECH/fit_check_v3_30mm.py` | 4 / 11 / 105 / 208 / 303 | **命中行 4 / 7 (未变)** | 新增内容插在文件头之后 ⇒ 命中行号不变 |
| `MECH/fit_check.py` | 18 / 26 / 130 / 399 | **18 / 26 / 130 / 399 (未变)** | ★退役横幅是【原地改一行】(行数不变) ⇒ 老行号全部有效★ |

### ★§5.5 · 机器闸 (★以后单口径脚本进不了「板只改一次」那一趟★) ★

- ★**闸**: `MECH/check_mech_dual_caliber_gate.py` (只读 · 零写盘) ★
- ★**它断言**: ① 8 个脚本逐个同时含 60×30 档 (`F30A` · 历史产品板口径) 与 160×100 档 (`B160x100`) 标识 ② 默认档 = F30A ③ 切档开关存在 ④ 已退役件带退役标记且不许自带默认档 ⑤ `MECH/hw_cross_review_check.py` md5 仍 = `e521387b87b0fcdf9f22d56f14199967` ⑥ 闸自身默认档自证 ★
- ★**反向用例**: `--selftest` 5/5 (3 条反向: 删 160×100 标识 ⇒ 判红并点名 / 默认档偷改 ⇒ 判红并点名 / 动 md5 钉死文件 ⇒ 判红 · + 1 条恢复后判绿) ⇒ ★沙盒只在 `tmp/iss352/selftest/` 副本上做, 真件一个字节都没被动过★ ★
- ★**配套判据**: `MECH/fit_check.py` 已标退役 (机器标记 `MECH_CALIBER_RETIRED`) ⇒ 现行装配余量判据一律引 `MECH/fit_check_v3_30mm.py` (帧 `F30A`) 与 `MECH/BOARD_GEOM_30MM.md` (历史留档表) ★

## ★§6 · ISS-345 全单闭环 · scope A / scope B 计数口径澄清 (2026-11-23 · mech-lead) ★

> ★**性质**: 追加式澄清 —— ★**§1 ~ §5 的老字一个字都没删**(★本节之前的内容逐字节保留★) ★
> ★**本节的每一个数 = 本机实跑重读的真值** (★不是沿用上一轮的数★) ★
> ★**本节要澄清的事**: ★**§5 写的 scope A 数 (24 原始命中 / 18 真数) 和 §1.0 写的数 (24 原始命中 / 19 真数) 都不是错, 而是【读的盘面档位不同】** ⇒ ★**scope A 的「原始命中数」不是一个稳定量, 稳定的是「真数」** ★

### ★§6.1 · 为什么会差 1 (★根因★) ★

★**派生物 `MECH/pinset2_mech_check.json` 是【最后一次跑的那一档】的产物** (★该脚本第 957 行 `open(OUT_JSON, "w")` 每次跑都重写它★) ⇒ ★**它自己就是一个口径载体**:

| 盘面状态 (最后一跑的档) | JSON 里的 SoC 名 | JSON 里的**历史口径词**命中 | `grep -rln RK3576 MECH/` 原始命中 | scope A 真数 (排除 `.pyc`+`.bak`) |
|---|---|---|---|---|
| ★**60×30 套A 档 (F30A · 历史产品板口径 · 不可混用)** ★ | `RK3576` (历史口径) | ★**2** ★ | ★**25** ★ | ★**19** ★ |
| ★**160×100 台架板档 (B160x100 · 现役)** ★ | `RK3572-SOM` | ★**0** ★ | ★**24** ★ | ★**18** ★ |

★**⇒ 所以「原始命中 24 还是 25」取决于读数时【最后一跑的是哪一档】; 而「真数」在两档下也不一样 (19 vs 18) ⇒ ★**两个数都必须在报数时声明盘面档位** ★**

★**★实测 (★本机三次跑, 三次不同 md5 ⇒ 结论不是猜的★) ★**: `logs/iss345/42_json_frame_dependence.txt`
```
① 60×30 档   ⇒ json md5 = 293738023d3855826edaf5a8914c4865 · 历史口径词命中 2 · scope A 原始命中 25
② 160×100 档 ⇒ json md5 = 0831e5582b667721f958e51e0ef96128 · 历史口径词命中 0 · scope A 原始命中 24
③ 60×30 档   ⇒ json md5 = 293738023d3855826edaf5a8914c4865 · 历史口径词命中 2 · scope A 原始命中 25
```
★**★§5 写的 24 / 18 = 读的是【160×100 档态盘面】时的数 (★当时 JSON 停在该档态★) ★**
★**★本节写的 25 / 19 = 读的是【60×30 档态盘面】时的数 (★JSON 已复原成 60×30 态★) ★**
★**★⇒ 【两者都对】, 但【口径不同】; 以后报数必须带盘面档位 ★**

### ★§6.2 · 本轮重读真值 (★口径: 60×30 档态盘面 + 显式排除 `.pyc` + `.bak`★) ★

| scope | 指标 | ★**本轮重读真值**★ | §1.0 老数 (main 00:1x) | 差 | 差的原因 (逐条可查) |
|---|---|---|---|---|---|
| A | `grep -rln RK3576 MECH/` **原始命中** | ★**25** ★ | 24 | ★**+1** ★ | ★派生物 JSON 在 60×30 档态含历史口径词 ×2 ⇒ 进命中集 (★迁前基线 `tmp/iss345_base/scopeA_pre.txt` 也含它★) ★ |
| A | 不计入处置范围 (`.bak` + `__pycache__/*.pyc`) | ★**6** ★ (1 `.bak` + 5 `.pyc`) | 5 | ★**+1** ★ | ★新增编译缓存 `MECH/__pycache__/pinset2_mech_check.cpython-314.pyc` (★跑兼容闸时被 import 产生★) ★ |
| A | ★**scope A 真数 (需判的文档与脚本)** ★ | ★**19** ★ | 19 | ★**±0** ★ | ★**文件集合与迁前基线 `tmp/iss345_base/scopeA_pre.txt` 逐个文件对拍 = 完全一致 (diff 空) ⇒ 零新增 / 零消失** ★ |
| B | 漂移闸扫描文件数 | ★**126** ★ | 125 | ★**+1** ★ | ★新建闸 `MECH/check_mech_dual_caliber_gate.py` (★ISS-352 第2批新建·本单新建闸已签收★) ★ |
| B | ★**命中处数** ★ | ★**107** ★ | 107 | ★**±0** ★ | ★**零新增未声明漂移** (★rc=2 = 迁移前既有状态, 预期★) ★ |
| B | 命中文件数 | ★**33** ★ | 33 | ★**±0** ★ | ★命中文件集合未变 ★ |

★**读数落盘**: `logs/iss345/41_scopeAB_REREAD.txt` (scope A 全清单 + 三个计数) · `logs/iss345/21_drift_CLOSURE.txt` (漂移闸原始输出) · `logs/iss345/28_scopeA_CLOSURE.txt` (scope A 分类计数)

### ★§6.2.1 · ★★签收闸的同款副作用 (★本轮实测★) ★★

★**★`state/_apply_20260723_0520_main_sign_iss345.py` 内部会实跑 `python3 MECH/pinset2_mech_check.py --frame B160x100` (★验「第二档有读数」那一条★) ⇒ ★**签收闸一跑, 派生物 JSON 就被改写成第二档态 ⇒ scope A 原始命中 25 → 24** ★ ⇒ ★**签收后必须再跑一次默认档复原** ★ (★实测见 `logs/iss345/49_signgate_side_effect.txt`: 跑签收闸前 25 → 跑完 24 → 复原后 25★) ★

### ★§6.3 · ★★以后报 scope A 的推荐口径 (★交 main 裁, 本单不擅自改扫描器★) ★★

★**推荐**: ★**统一报「真数」+ 显式排除清单 (`.pyc` / `.bak`), 并在报数行里注明【盘面档位】** ★ ⇒ ★**不要单独报「原始命中数」** (★它会被扫描器自己和派生物自己污染 —— 本项目已踩两次: `HW/__pycache__` 一次 · 派生物 JSON 这一次★) ★
★**★本单【不擅自改】扫描器口径 (`MECH/check_board_geom_caliber_drift.py` 一个字节未动) 也【不擅自改】派生物写盘行为 —— 两件都归 main 裁★** ★
★**★本单【未拍默认档】**: 默认档恒为 F30A (60×30 套A 帧 · 历史产品板口径), 与迁移前逐字节相同 ⇒ ★**判据方向未动 = 判据已冻结, 可进「板那一趟」** ★
