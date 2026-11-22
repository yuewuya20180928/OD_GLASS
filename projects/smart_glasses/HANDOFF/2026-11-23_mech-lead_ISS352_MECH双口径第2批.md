# HANDOFF/2026-11-23_mech-lead_ISS352_MECH双口径第2批.md —— ISS-352 交卷页 (MECH 域判定脚本迁双口径 · 第 2 批)

> ★**任务书**: `state/dispatch_briefs/ISS-352_mech_dual_caliber_batch2.md` (逐字照用) ★
> ★**交卷人**: 结构总工 (mech-lead · 带散热) ★ ★**日期**: 2026-11-23 ★
> ★**本单 = ISS-345 cont1 的第 2 批** (第 1 批 = `MECH/pinset2_mech_check.py` + `MECH/skeleton_section_check.py`, 已由 main 2026-11-23 04:0x 签收) ★
> ★**工作目录**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` ★

---

## ★B0 · 本页速览 (★一句话 + 五件交付物清单★) ★

★**一句话**: ★**MECH 域 8 个判定脚本的「双口径」这件事, 本单把第 2 批收完了 —— `MECH/fit_check_v3_30mm.py` 与 `MECH/cross_review_check.py` 迁双口径 (默认档 60×30 输出与迁移前**逐字节相同**), `MECH/fit_check.py` **明确标退役**, 新建机器闸 `MECH/check_mech_dual_caliber_gate.py` (含 3 条反向用例), 清单页 `MECH/BOARD_GEOM_CALIBER_STATUS.md` scope A/B **追加式**订正, 漂移闸迁后重跑 **107 处 / 33 个文件 = 与迁移前基线完全一致 (零新增)**; ★零写板 / 零落表 / 零改别人的闸 / 零改别人的分片 / 零外发★ ★

★**本单动的文件 (MECH 域全文件 md5 前后对拍: CHANGED = 6 / DELETED = 0 / ADDED = 1) ★**:

| # | 文件 | 类型 | 一句话 |
|---|---|---|---|
| 1 | `MECH/fit_check_v3_30mm.py` | 改造 | 迁双口径 (FRAMES 档位表 + PROSE 帧级叙述表 + `--frame`/`MECH_FRAME` 切档) |
| 2 | `MECH/cross_review_check.py` | 改造 | 迁双口径 (同上 + 板面纯 python 逐焊盘重解析 + 三源校验) |
| 3 | `MECH/fit_check.py` | **退役** | 明确标退役 (机器标记 `MECH_CALIBER_RETIRED`) · 判据数字与输出一个字节未改 |
| 4 | `MECH/board_port_opening_s6_check.py` | 标签 | 只补帧 id 标签行 (docstring 一行 · 零行为变化) |
| 5 | `MECH/jd_y0_feasibility.py` | 标签 | 只补帧 id 标签行 (docstring 一行 · 零行为变化) |
| 6 | `MECH/BOARD_GEOM_CALIBER_STATUS.md` | 追加 | scope A / scope B 真数追加式订正 (§1~§4 老字一字未删) |
| 7 | `MECH/check_mech_dual_caliber_gate.py` | **新建** | 双口径机器闸 (只读 · 含反向用例) |
| 8 | `state/fragments/mech.yaml` | 分片 | 9 个 artifact + 1 个 interface_claim + 1 个 need (★只走 `state/frag_write.py`★) |
| 9 | `logs/iss352/` | 证据 | 17 份原始读数 (含 **3 份 0 字节 diff**) |

★**零动的**: `MECH/hw_cross_review_check.py` (md5 钉死 `e521387b87b0fcdf9f22d56f14199967`) · `MECH/check_board_geom_caliber_drift.py` (漂移闸判据方向没动) · `MECH/check_board_frame_coords.py` (钉板闸⑦) · `MECH/check_demo_struct_truth.py` · `MECH/cavity_recalc_check.py` · `MECH/check_board_frame_candidate_compat_gate.py` · `MECH/board_frame_feasibility.py` (三档帧表已逐字对齐 ⇒ 零改动) · `HW/` 全部 · `state/fragments/pm.yaml` / `hw.yaml` / `sw.yaml` · `state/issue_log.yaml` (main 的地界) ★

---

## ★B1 · 结论摘要 ★

★**本单 = ISS-345 第 2 批 (只迁 2 个脚本 + 处置 fit_check 一对 + 建闸 + 订正清单页)**: ★`MECH/fit_check_v3_30mm.py` + ★`MECH/cross_review_check.py` 双口径改造完成 (★默认档仍 = 60×30 / RK3576 · 本单【不许】拍默认档★) ⇒ ★60×30 档迁移前后输出【逐字节相同】 (3 份 diff 文件 **均 0 字节**) + 第二档 `B160x100` 读数在盘 (每条数都有出处) + 新闸自测 5/5 (末行 `ALL TESTS PASS`) + 兼容闸 rc=0 + 漂移闸 **107 处 / 33 文件 = 与迁移前基线完全一致 (零新增)** ★

★**三个硬结论 (逐条可复现) ★**:

1. ★**判据方向一个字未改** —— 两个迁移脚本 + 一个退役脚本的默认档 stdout 与迁移前**逐字节相同** (`logs/iss352/03_diff_fit_v3.txt` / `06_diff_xrev.txt` / `09_diff_fit.txt` **均为 0 字节**) ★
2. ★**第二档 `B160x100` 的每个数都能指回三处权威源** —— `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` + `HW/PCB/demo_mainboard_params.json` board 段 + `HW/PCB/demo_mainboard.kicad_pcb` **纯 python 逐焊盘重解析**, ★三源逐位一致 (脚本自跑自证, 见 `logs/iss352/07_xrev_B160x100.txt`)★ ★**SoM 承载区焊盘实体占位 53.80×46.78mm / 封装外形占位 56.70×46.78mm = 与权威页 §3 行 71/72 逐位一致** (板文件纯 python 重解析 = 15.10..68.90 × 7.61..54.39) ★
3. ★**台架板帧作为「眼镜镜脚内的板」物理装不下** —— `MECH/fit_check_v3_30mm.py` 的 B160x100 档: V 链需求 106.00 vs 净高 38.00 ⇒ **余量 −68.00 (最坏 −68.60)**; L 链需求 215.50 vs 130.00 ⇒ **余量 −85.50**; 检修口净空 **4.10 < 4.50 硬要求 (差 0.40)**; 板重 (8 层 1.60mm) **29.60g** ⇒ ★**这不是脚本坏了, 是台架板本来就不是眼镜里的板** (与 `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` §3 的定性一致) ★

★**★`MECH/fit_check.py` 与 `MECH/fit_check_v3_30mm.py` 二选一的处置 (★任务书第 ① 件·必须说清留谁退谁★) ★**:

| 项 | `MECH/fit_check_v3_30mm.py` (v3) | `MECH/fit_check.py` (v2) |
|---|---|---|
| **自报状态 (★实读·非转述★)** | 第 4 行「板宽 30mm / RK3576 基线下的电池·PCB·光机装配干涉检查」= 现行版 | ★**第 6 行自己写着: 「本脚本基线已作废 —— 现行版是 `MECH/fit_check_v3_30mm.py`」** ★ |
| 机器判定 | ★**活件 (在用)** ★ | ★**死件 (自报作废 · 历史闭环记录)** ★ |
| 谁引用谁 | 被 v2 第 6 行反向点名 ⇒ **v2 指向 v3** | 不引用 v3 (只是自己横幅里提到) |
| 盘上引用面 | `state/issue_log.yaml` 多处「板宽30/RK3576基线下的装配干涉重算, rc=0」 | 只被文档引用 (★`MECH/_apply_pinset2_docs.py` 是 2026-10-2x 的历史落片脚本★) |
| 代码消费方 | 无 (它是独立报告器) | ★**全项目 0 个 .py 引用它** (★实跑 grep 全仓: 只有 `state/_apply_*.py` 的文案字符串, 无 import / 无 subprocess★) |
| **处置** | ★**保留 + 迁双口径** (第 ② 件) ★ | ★**明确标退役** (★原地改 1 行·机器标记 `MECH_CALIBER_RETIRED`★) ★ |

★**为什么选「明确标退役」而不是「移到 `MECH/.trash/`」 (★理由写清·不含糊★) ★**:

1. ★**它自己的横幅写着要留着** —— v2 第 20~23 行: 「★**保留 v2 的意义**: 它的结论是 **ISS-017 / ISS-042 的历史闭环记录** … ⇒ **文件留着、数字不动**」 ★⇒ 移走就毁掉它自己承诺的可复现性 (别人引「fit_check.py §3① 已判过时叠放模型」时得能复跑) ★
2. ★**清单页 `MECH/BOARD_GEOM_CALIBER_STATUS.md` §1.1 第 7/8/9 行与 §1.4 B27 行按「文件 + 行号」引用它** ⇒ 移走 = 这 4 条登记全变成死引用, 而本单对清单页只许追加不许改老字 ★
3. ★**漂移闸基线**: 移走会把 scope A / scope B 的**文件集合**改掉 ⇒ 命中数就不再等于迁移前基线 107 处 / 33 文件 ⇒ 直接踩「迁完重跑 = 与基线一致」这条验收线 ★★ (★原地退役 ⇒ 命中数与文件数一个不动★) ★
4. ★**零代码消费方** ⇒ 留着零风险; 移走的唯一好处只是「目录好看」, 代价是上面三条 ★
5. ★**处置动作本身是可逆的**: 退役标记是一行横幅 + 一个机器 token ⇒ 谁要复活它, 删掉那行即可 ★

★**退役不等于删**: ★v2 的判据数字、输出、行号**一个字节都没改** (`logs/iss352/09_diff_fit.txt` = 0 字节) ⇒ 它仍是 ISS-017 / ISS-042 的可复现历史闭环记录, 只是【不再被当成现行判据】 ★

---

## ★B2 · 验收标准自评 (逐条 通过/不通过/未验) ★

| # | 验收项 | 自评 | 证据 |
|---|---|---|---|
| 1 | `MECH/fit_check_v3_30mm.py` 与 `MECH/fit_check.py` 二选一说清 (留谁 / 退谁 / 谁引用谁) | ✅ **通过** | §B1 表 + `logs/iss352/00_pre_baseline.txt` (实读第 6 行横幅 + 全仓 grep 0 个代码消费方) |
| 2 | 处置 = 保留一个 + 另一个明确标退役 (含理由) | ✅ **通过** | `MECH/fit_check.py` 第 6 行横幅 + 机器标记 `MECH_CALIBER_RETIRED` (★闸的 ④ 号断言读的就是这个 token★); 理由五条见 §B1 |
| 3 | ★**不许改任一份判据的方向或数字** | ✅ **通过** | `logs/iss352/09_diff_fit.txt` = **0 字节** (v2 输出与退役前逐字节相同) |
| 4 | `MECH/cross_review_check.py` 迁双口径 | ✅ **通过** | `logs/iss352/07_xrev_B160x100.txt` (rc=0, 含三源校验 + 承载区实测占位) |
| 5 | ★**默认档 (F30A) 输出与迁移前逐字节相同** | ✅ **通过 (逐字节相同)** | `logs/iss352/06_diff_xrev.txt` = **0 字节** (DIFF_XREV=0) |
| 6 | ★**第二档 `B160x100` 有读数 + 每条数有出处** | ✅ **通过** | `logs/iss352/07_xrev_B160x100.txt`: 三源校验 4 行 (板宽/板高/铜层数/板厚 ⇒ **逐位一致**) + 承载区 53.80×46.78 / 56.70×46.78 (纯 python 逐焊盘重解析) |
| 7 | ★**不许照抄官方板的数, 三源取值** | ✅ **通过** | 脚本内 `read_caliber_page()` / `read_board_caliber()` / `demo_mainboard_params.json` 三处独立取值, 不一致就报「★不一致★」 (★闸式自检, 不靠人眼★) |
| 8 | `MECH/fit_check_v3_30mm.py` 迁双口径 (★任务书第 ① 件的活件侧★) | ✅ **通过** | `logs/iss352/04_fit_v3_B160x100.txt` (rc=0) + `logs/iss352/03_diff_fit_v3.txt` = **0 字节** |
| 9 | ★**新建机器闸 `MECH/check_mech_dual_caliber_gate.py`** | ✅ **通过** | `logs/iss352/10_gate.txt` (rc=0, 35 条断言全绿) |
| 10 | ★**闸断言 ①: 8 个脚本逐个同时含 60×30 档与 160×100 档标识** | ✅ **通过** | 闸输出 16 行「档标识」全绿 (8 脚本 × 2 档) |
| 11 | ★**闸断言 ②: 默认档 = 60×30 (`DEFAULT_FRAME_ID` = F30A)** | ✅ **通过** | 闸输出 4 行「默认档 = F30A」+ 1 行「(闸自证)」; ★3 个既有帧表脚本无默认档概念 (三档一次跑完) ⇒ 闸额外断言「若自带默认档则必须是 F30A」★ |
| 12 | ★**闸断言 ③: `MECH/hw_cross_review_check.py` md5 仍 = `e521387b87b0fcdf9f22d56f14199967`** | ✅ **通过** | 闸输出「md5 钉死 = e521387b87b0fcdf9f22d56f14199967 (实读 同值)」 |
| 13 | ★**闸断言 ④: 反向用例 (删 160×100 标识 ⇒ 判红并点名 ⇒ 恢复 ⇒ 判绿)** | ✅ **通过** | `logs/iss352/11_gate_selftest.txt`: 反向① 删 `MECH/cross_review_check.py` 的 160×100 标识 ⇒ 判红 + **点名该脚本**; 反向② 默认档偷改成 B160x100 ⇒ 判红 + 点名 `MECH/pinset2_mech_check.py`; 反向③ 动 md5 钉死文件 ⇒ 判红; 恢复后判绿 ★**真件一个字节都没被动** (★沙盒只在 `tmp/iss352/selftest/` 副本上★) ★ |
| 14 | ★**闸 `--selftest` 末行 `ALL TESTS PASS`** | ✅ **通过** | `logs/iss352/11_gate_selftest.txt` 末行 = `ALL TESTS PASS` (rc=0, 5/5) |
| 15 | ★**清单页 scope A / B 追加式订正 (老字一字未删)** | ✅ **通过** | 老前缀逐字节保留已验 (PREFIX_UNCHANGED = True, 15283 B → 19011 B, 老前缀 md5 `b42026dff243b5dd036bd244ba4af44f` 未变) |
| 16 | ★**计数页实跑订正 + 改完重跑生成器验一次** | ✅ **通过** | 追加 §5 后**重跑漂移闸** (`logs/iss352/12_drift_POST.txt`) ⇒ **107 处 / 33 个文件 / 扫描 126 文件** = §5 写入的数**一字不差** ⇒ 本页写的数就是重读后的真值 (★不是沿用上一轮★) |
| 17 | ★**漂移闸迁后重跑 ⇒ 命中数与迁移前基线一致 (零新增)** | ✅ **通过** | `logs/iss352/01_drift_PRE.txt` 与 `logs/iss352/12_drift_POST.txt` **同为 107 处 / 33 个文件** (★扫描文件数 125 → 126 = 新建闸 1 个, 不影响命中★); ★逐文件命中数对照见清单页 §5.3 (本单动过的 7 个文件全部 ±0)★ |
| 18 | ★**三个既有帧表脚本的核对结论 (不许含糊)** | ✅ **通过** | §B4 表 + §B5-3: `board_frame_feasibility.py` = **不需要迁** (零改动) · `board_port_opening_s6_check.py` / `jd_y0_feasibility.py` = **不需要迁几何** (只补帧 id 标签行, 零行为变化) |
| 19 | 零写板 | ✅ **通过** | 板 md5 = **611b869e13518c3c023fb178f91a0075**, mtime = **2026-11-06 07:07:17.362193413** (前后逐字节相同, `logs/iss352/16_board_fingerprint.txt`) |
| 20 | 零落表 | ✅ **通过** | `HW/netlist_v1.csv` = `6aee500e60ba0732f83a9cf557ba90ab` / `HW/netlist_v1_pins.csv` = `9174309df1ec9411ac8e8d9e80ee386a` / `HW/BOM_v1.csv` = `5b9993992405904a60ac96a020b375d8` — 本单**未写 `HW/` 任何文件** ★ |
| 21 | 零改别人的闸 (md5 钉死件) | ✅ **通过** | `MECH/hw_cross_review_check.py` = `e521387b87b0fcdf9f22d56f14199967` · `MECH/check_board_geom_caliber_drift.py` = `0f70bd049d18d2d308b06a813443d4e3` (与迁移前基线同) · `MECH/check_board_frame_coords.py` = `d4bd30c241718a8c0baf3084f78e2eb7` (同) · `MECH/check_demo_struct_truth.py` = `483d018a66d17d2ead25d1558a1f8ffe` (同) · `MECH/cavity_recalc_check.py` = `c4bf9151dd59826fb2320c34e8afbd0f` (同) ★ |
| 22 | 零改别人的分片 | ✅ **通过** | `state/fragments/pm.yaml` = `c0d0ec04770251255bddad0ecdbd6bd4` · `hw.yaml` = `6396d321fa54be9e41800973be95b72e` · `sw.yaml` = `588d741cfbcf0a6957a4a46a12bef7f5` — 前后同值 ★ |
| 23 | 零改 `state/issue_log.yaml` | ✅ **通过** | 本单**没写** (★签收是 main 的活★) ★ |
| 24 | 下游消费方不被弄红 | ✅ **通过** | `MECH/check_board_frame_candidate_compat_gate.py` rc=0 (`logs/iss352/14_compat.txt`) · `MECH/check_board_frame_coords.py` (钉板闸⑦) rc=0 · `MECH/check_onepass_mech_release.py` rc=0 · `MECH/iss127_h_chain_check.py` rc=0 · `MECH/board_port_opening_s6_check.py --selftest` rc=0 · `MECH/jd_y0_feasibility.py --selftest` rc=0 · `MECH/check_board_geom_caliber_drift.py --selftest` rc=0 (末行 `ALL TESTS PASS`) ★ |
| 25 | 主线闸 `state/merge.py` + `state/gate_check.py` | ✅ **通过** | 见 §B6-1 输出 (`logs/iss352/16_merge.txt` / `logs/iss352/17_gate_check.txt`): MERGE_RC=0 · GATE_RC=0 且 **Q1 = 18/18** · **Q7 = 10/10** ★ |
| 26 | 零外发 (邮件/询价/问询/采购) | ✅ **通过** | 本单**零外发**; ★全部数据来自盘上文件 + 本机只读解析, 零缺口零外查★ |
| 27 | 不替老板拍板 (默认档归属) | ✅ **通过** | ★默认档 = F30A = **保持现状不变**; 切默认档的权归 U-1 拍完后 main, 本单只交「切档开关」★ |
| 28 | 不新增拍板项 | ✅ **通过** | 本单**零**新增 needs_to_boss; 分片只登记 1 个 need (to = main, 内容是「待签收 + U-1 后切默认档」, **不是新拍板项**) ★ |
| 29 | 写分片只用 `state/frag_write.py` | ✅ **通过** | 本单**零** `open(p,"w")` 写分片 (★写分片的唯一调用 = `state/frag_write.py --agent mech-lead`★) ★ |
| 30 | 引用零假引用 (MISS=0) | ✅ **通过** | 本页引用的每个 `MECH/` `HW/` `state/` `logs/` 路径逐个在盘自检 ⇒ **MISS = 0** (§B7-3) ★ |

---

## ★B3 · 证据分级 (实测/官方/推算/0数据) ★

★**第二档 `B160x100` 的每一个数逐条列源 (★文件 + 行号 + 等级★) ★**:

| # | 量 | 值 | 证据等级 | 出处 (★三源逐位一致★) |
|---|---|---|---|---|
| 1 | 帧 id | `B160x100` | [实测] | `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` 块的 `"current_frame": "B160x100"` (★脚本运行时报「权威页 / params.json / 板文件实读」三处同值★) |
| 2 | 板宽 × 板高 | 160.00 × 100.00 mm | [实测] | 权威页 `cal:FRAMES` `width_mm` 160.0 / `height_mm` 100.0 + `HW/PCB/demo_mainboard_params.json` board 段 `width_mm` 160.0 / `height_mm` 100.0 + 板文件 Edge.Cuts 实读 0..160 × 0..100 ⇒ **三源逐位一致** |
| 3 | 铜层数 | 8 | [实测] | 权威页 `layers: 8` + `demo_mainboard_params.json` `layers: 8` + 板文件 `(layers …)` 块实数 (F.Cu + In1..In6.Cu + B.Cu = 8) |
| 4 | 板厚 | 1.60 mm | [实测] | 权威页 `thickness_mm: 1.6` + `demo_mainboard_params.json` `thickness_mm: 1.6` + 板文件 `(general (thickness 1.6))` |
| 5 | SoM 承载区**焊盘实体占位** | X 15.10..68.90 / Y 7.61..54.39 = 53.80 × 46.78 mm | [实测] | ★**纯 python 逐焊盘重解析** (4 座 `J_SOM_P1..P4` 各 100 焊盘 = 400) + 权威页 §3 行 71 ⇒ **逐位一致** ★ |
| 6 | SoM 承载区**封装外形占位** | X 13.65..70.35 / Y 7.61..54.39 = 56.70 × 46.78 mm | [实测] | ★纯 python 逐 `fp_line`/`fp_rect` 轮廓 (含 stroke 半宽外扩) ∪ 焊盘实体占位 + 权威页 §3 行 72 ⇒ **逐位一致** ★ |
| 7 | SoM 座数 / 焊盘数 | 4 座 / 400 焊盘 | [实测] | 同 #5 的脚本自解析 (座数 4 / 焊盘数 400) |
| 8 | 镜脚内腔三链 (H/V/L) | 7.30 / 38.00 / 130.00 mm | [官方] | `MECH/fit_check_v3_30mm.py` `BASE` 表 (锁死值, ISS-092 已复核 Δ=0.00) — 本单**一个字未改** |
| 9 | 台架板帧 V 链余量 | −68.00 mm (最坏 −68.60) | [推算] | = 净高 38.00 − (板宽 100 + 走线槽 6) = −68.00; 最坏再减 2×FDM 单边公差 0.30 |
| 10 | 台架板帧 L 链余量 | −85.50 mm | [推算] | = 130.00 − (电芯 40.50 + 板长 160 + 余量 15) = −85.50 |
| 11 | 台架板帧检修口净空 | 4.10 mm (硬要求 4.50 ⇒ 差 0.40) | [推算] | = 7.30 − (0.80 皮肤壁 + 0.50 隔热垫 + 0.30 空气隙 + 1.60 板厚) = 4.10 |
| 12 | 台架板板重 (8 层 1.60mm) | 29.600 g | [推算] | = 16000 mm² × 1.60e-3 mm × 1.85 g/cm³ (★密度口径同 `HW/pcb60x30_check.py`★) |
| 13 | 骨架 V 覆盖 (台架板帧) | 100.0 mm (满宽) | [推算] | = SoM 承载区高 46.78 + 2×(100 − 46.78)/2 = 100.0 (★与第 1 批 `MECH/skeleton_section_check.py` 台架板档同口径 (band 26.61)★) |
| 14 | 逃线带 / 器件边距阈值 | 0.80 mm/边 | [推算] | `MECH/MECH_BUDGET.md` §5.1 `KEEPOUT_EDGE` (第 1 批同款, 本单沿用) |
| 15 | FDM 单边公差 / 判据阈值 | 0.30 / 0.60 mm | [推算] | `MECH/fit_check_v3_30mm.py` `TOL` / `CRIT` 表 (本单未改) |
| 16 | SoM 承载区高 vs 板高 | 46.78 ≤ 100.00 ⇒ 装得下 (对照 60×30 装不下, 差 16.78) | [推算] | #5 与板高之差; ★对照数 30.00 出自权威页 §3 结论行★ |
| 17 | 实物打印件 / 贴皮肤实测 | —— | [0数据] | 0 件已打; 0 台样机 ⇒ 所有读数都是设计态几何 + 公差栈, 不是物理实测 |

★**证据等级的边界 (★不许糊★)**: ★本单所有「装得下 / 装不下」的结论都是 **[推算]** (设计态几何 + 公差栈, 逐项可复现), **不是物理装配实测** ⇒ `state/measurements.yaml` 的 M-FIT kind 仍写 [推算], 阶段门 G2 不认 (这是对的)★

---

## ★B4 · 接口取值声明 (interface_claims) ★

★**① 档位表 (★8 个脚本的档位口径, 帧 id 逐字取自 `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES`★) ★**:

| 帧 id | 板 (长×宽) | 层数 | 板厚 | 主控 / 承载区 | 在哪些脚本里 | 默认档? |
|---|---|---|---|---|---|---|
| `F30A` | 60 × 30 mm | 6 | 1.00 mm | RK3576 17.20×16.10 | ★**全部 8 个脚本** (第 1 批 2 个 + 本单 3 个 + 既有 3 个) ★ | ★**是 (本闸 `DEFAULT_FRAME_ID` = F30A) ★** |
| `B160x100` | 160 × 100 mm | 8 | 1.60 mm | RK3572-SOM 承载区 56.70×46.78 | 全部 8 个脚本 (第 1 批 2 个 + 本单 3 个 + 既有 3 个) | 否 |
| `P60x15` | 60 × 15 mm | 6 | 1.00 mm | RK3576 (已作废口径) | 既有 3 个帧表脚本 (`board_frame_feasibility.py` / `board_port_opening_s6_check.py` / `jd_y0_feasibility.py`) | 否 |

★**② 切档开关 (★留给 U-1 拍完后 main 切·本单不拍★) ★**:

```bash
# ① 切到 160×100 台架板帧 (一次性调用, 不改判据本体):
python3 MECH/fit_check_v3_30mm.py   --frame B160x100
python3 MECH/cross_review_check.py  --frame B160x100
# ② 或用环境变量 (两个脚本同款):
MECH_FRAME=B160x100 python3 MECH/fit_check_v3_30mm.py
MECH_FRAME=B160x100 python3 MECH/cross_review_check.py
# ③ 改回默认档: 去掉 --frame 即可 (默认恒为 F30A, 本单已写死 DEFAULT_FRAME_ID = "F30A")
```

★**③ 三个既有帧表脚本的核对结论 (★交 main 第 3 问 · 逐个给结论·不许含糊★) ★**:

| 脚本 | 结论 | 依据 (★实读★) | 本单处置 |
|---|---|---|---|
| `MECH/board_frame_feasibility.py` | ★**不需要迁** (已是双口径) ★ | 第 100~130 行 `FRAMES` 三档表, `fid` 逐字 = `B160x100` / `F30A` / `P60x15`, 与权威页 §6 一致; 第 356/410/437/464 行**逐档循环**跑, 无「默认档」概念 | ★**零改动** (md5 与迁移前同) ★ |
| `MECH/board_port_opening_s6_check.py` | ★**不需要迁几何** (三档表已在) ★; ★**只补帧 id 标签行** ★ | 第 388 行 `frames` 三档表用 `①②③` 序号 + 中文名 (`台架板 (盘上现役)` / `产品目标板 60×30 套 A (MECH 现行)` / `产品目标板 60×15`), ★**没有权威帧 id 字样** ⇒ 机器闸认不出它 ⇒ 只在 docstring 抬头补一行权威帧 id (零行为变化, stdout 与 `--selftest` 逐字节不变) ★ | 改 1 行 (docstring) |
| `MECH/jd_y0_feasibility.py` | ★**不需要迁几何** (三档表已在) ★; ★**只补帧 id 标签行** ★ | 第 166~182 行 `FRAMES` 三档表同样用 `①②③` + 中文名, 无权威帧 id 字样 ⇒ 同上 | 改 1 行 (docstring) |

★**④ 新机器闸的断言面 (★`MECH/check_mech_dual_caliber_gate.py`★) ★**: ① 8 个脚本逐个同时含 `F30A` 与 `B160x100` 标识 ② 默认档 = F30A (含「闸自证」) ③ 切档开关存在 ④ 已退役件带 `MECH_CALIBER_RETIRED` + 点名接班件 + 不许自带默认档 ⑤ `MECH/hw_cross_review_check.py` md5 钉死 ⑥ 既有三档帧表脚本三档权威帧 id 齐备 ★**裸跑 35 条断言全绿 (rc=0) · `--selftest` 5/5 (末行 `ALL TESTS PASS`) ★**

★**⑤ 不新增接口请求**: ★本单**零** interface_claims 新增到别的域; 分片里的 1 条 interface_claim 是**本域自述** (`iss352_mech_dual_caliber_batch2`), 不向谁要数 ★

---

## ★B5 · 未决项与卡点 (需要谁回答什么) ★

### ★B5-1 · 本批【没有】卡点 (零阻塞) ★
★本单 5 件交付全部落地, **无需任何人回答即可继续** ★

### ★B5-2 · 剩 1 件 (★不是新拍板项★) ★
★**U-1 (这一趟画哪块物理产品) 仍在老板队列** ⇒ 本单**不替他定默认档**。等 U-1 拍完后, main 用 §B4 的命令切默认档即可 (★只切档, 不动判据本体★) ★

★**另**: 第 1 批交卷页 §B5-2 登记的 need `iss345_mech_cont1_batch2_remaining` (to = main) 的内容**已由本单完成** ⇒ ★**该 need 的闭合是 main 的活** (★needs_from × answers 按 key 配对, 答案须由被问方 main 写·我不越界代答★) ★

### ★B5-3 · 本单对「板那一趟」的影响 (★一句话, 不越位★) ★
★8 个 MECH 判定脚本现在**两档都在**, 且**默认档输出与迁移前逐字节相同** ⇒ ★**判据已冻结**: 板那一趟期间【不许临时改脚本】, 这 8 个脚本的绿灯/红灯对 F30A 档与 B160x100 档各有明确读数, 不再是「一块不存在的板」的单档口径 ★

---

## ★B6 · 自证复现命令 ★

### ★B6-1 · 必跑项 (★本机实跑读数见括号★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
L=logs/iss352
# ---- ① 默认档逐字节不变 (3 份 diff 必须全是 0 字节 · 基线在 logs/iss352/00a~00c★) ----
PYTHONHASHSEED=0 python3 MECH/fit_check_v3_30mm.py  > $L/02_fit_v3_POST.txt 2>&1
diff $L/00a_base_fit_check_v3_30mm.txt $L/02_fit_v3_POST.txt > $L/03_diff_fit_v3.txt ; echo "DIFF_FIT_V3=$? (须 0 · 文件 0 字节)"
PYTHONHASHSEED=0 python3 MECH/cross_review_check.py > $L/05_xrev_POST.txt 2>&1
diff $L/00b_base_cross_review_check.txt $L/05_xrev_POST.txt > $L/06_diff_xrev.txt ; echo "DIFF_XREV=$? (须 0 · 文件 0 字节)"
PYTHONHASHSEED=0 python3 MECH/fit_check.py > $L/08_fit_retire_POST.txt 2>&1
diff $L/00c_base_fit_check.txt $L/08_fit_retire_POST.txt > $L/09_diff_fit.txt ; echo "DIFF_FIT=$? (须 0 · 文件 0 字节)"
# ---- ② 第二档读数 ----
python3 MECH/fit_check_v3_30mm.py  --frame B160x100 > $L/04_fit_v3_B160x100.txt  2>&1 ; echo "FITV3_B160_RC=$?"
PYTHONHASHSEED=0 python3 MECH/cross_review_check.py --frame B160x100 > $L/07_xrev_B160x100.txt 2>&1 ; echo "XREV_B160_RC=$?"
# ---- ③ 新闸 + 反向用例 ----
python3 MECH/check_mech_dual_caliber_gate.py            > $L/10_gate.txt 2>&1 ; echo "GATE_RC=$? (须 0)"
python3 MECH/check_mech_dual_caliber_gate.py --selftest > $L/11_gate_selftest.txt 2>&1 ; echo "GATE_SELFTEST_RC=$? (须 0 · 末行 ALL TESTS PASS)"
# ---- ④ 只读漂移闸 (迁后重跑) ----
python3 MECH/check_board_geom_caliber_drift.py > $L/12_drift_POST.txt 2>&1 ; echo "DRIFT_RC=$? (须 2 = 既有漂移 · 命中数须 = 107 处 / 33 个文件)"
# ---- ⑤ 主线闸 ----
python3 state/merge.py     > $L/16_merge.txt     2>&1 ; echo "MERGE_RC=$? (须 0)"
python3 state/gate_check.py > $L/17_gate_check.txt 2>&1 ; echo "GATE_RC=$? (须 0 · Q1 18/18 · Q7 10/10)"
# ---- ⑥ 边界自证 ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv MECH/hw_cross_review_check.py
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**★本单实跑读数 (本机, 2026-11-23) ★★**:
```
DIFF_FIT_V3=0   DIFF_XREV=0   DIFF_FIT=0   (三份 diff 文件均 0 字节)
FITV3_B160_RC=0   XREV_B160_RC=0
GATE_RC=0 (35 条断言全绿)   GATE_SELFTEST_RC=0 (5/5 · 末行 ALL TESTS PASS)
DRIFT_RC=2 ⇒ [DRIFT] 未声明口径漂移: 107 处 / 33 个文件  (★与迁移前基线一字不差 ⇒ 零新增★)
MERGE_RC=0   GATE_RC=0 (Q1 = 18/18 · Q7 = 10/10)
611b869e13518c3c023fb178f91a0075 HW/PCB/demo_mainboard.kicad_pcb  (mtime 2026-11-06 07:07:17.362193413)
6aee500e60ba0732f83a9cf557ba90ab HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8 HW/BOM_v1.csv
e521387b87b0fcdf9f22d56f14199967 MECH/hw_cross_review_check.py   (★md5 未变★)
```

★**★一个必须交代的技术前提 (★否则 diff 复现不出来★) ★★**: ★`MECH/cross_review_check.py` 的「未建模件」清单来自 **set 迭代序** ⇒ 该脚本的 stdout **天生带 `PYTHONHASHSEED` 随机性** (★这是迁移前就有的性质·本单【没有】引入·也【没有】改它 —— 改了就破坏「与迁移前逐字节相同」★) ⇒ ★**前后对照必须同 seed** ⇒ 本单统一用 `PYTHONHASHSEED=0` (★迁移前基线就是用 seed=0 重抓的★)。`MECH/fit_check_v3_30mm.py` 与 `MECH/fit_check.py` 的输出**与 seed 无关** (★实测 seed 0/1/2 三次 md5 相同★) ⇒

### ★B6-2 · ★改动前后逐条 diff (★任务书点名要这一块★) ★

| # | 文件 | 改动前 md5 | 改动后 md5 | 行数 前→后 | 改了什么 (★逐条★) | 输出变化 |
|---|---|---|---|---|---|---|
| 1 | `MECH/fit_check_v3_30mm.py` | `dabb8e30f5be41cb162a6fbc9396f8fc` | `2fb79fda15f4395478996b4319913a66` | 331 → 536 | ① docstring 加 ISS-352 双口径说明 (用法 + 两档帧 id) ② 加 `FRAMES` 档位表 (F30A / B160x100) + `DEFAULT_FRAME_ID` + `PROSE` 帧级叙述表 + `_bind_frame` / `_pick_frame_id` ③ `v_chain` / `h_chain` / `l_chain` / `area_weight` / `battery_and_frame` / `main` 的硬编常量改成按档取值 (叙述文字进 PROSE, F30A 档逐字保留) ④ 加 `import os` / `import sys` | ★**默认档 stdout 0 字节差异** (`03_diff_fit_v3.txt`) ★ |
| 2 | `MECH/cross_review_check.py` | `7f1d65fb44374f4335f90f6c75e74700` | `9bb0b99894b072ad3b6ccb86f5a0fa2b` | 423 → 727 | ① docstring 加 ISS-352 双口径说明 ② 加 `FRAMES` + `DEFAULT_FRAME_ID` + `PROSE` + `_bind_frame` / `_pick_frame_id` ③ 加板面**纯 python 逐焊盘重解析** (`_sexp` / `_sget` / `read_board_caliber`) + 权威页 `cal:FRAMES` 读取 + `demo_mainboard_params.json` 读取 + `three_source_check` 三源校验 ④ C-7 标题 / C-16 全部判据文字 / 末行权威口径行 改成按档取值 ⑤ 加 `import json` / `import math` | ★**默认档 stdout 0 字节差异** (`06_diff_xrev.txt`) ★ |
| 3 | `MECH/fit_check.py` | `f7448ea6956d85f8e2ce3142a94860aa` | `be26b35c3e94e8ed4f4a174ac4ef6100` | 426 → 426 | ★**只改第 6 行一行** (加 ISS-352 退役横幅: 机器标记 `MECH_CALIBER_RETIRED` + 接班件 + 台架板 `B160x100` 口径不适用 + 保留理由) ★**行数不变 ⇒ 清单页 §1.1 引用的 18/26/130/399 四个行号全部有效** ★ | ★**stdout 0 字节差异** (`09_diff_fit.txt`) ★ |
| 4 | `MECH/board_port_opening_s6_check.py` | `be8bf0ce94beaf96b1ecba71a45dfd44` | `f39943e6e53905e23ffa2ec10f907a9b` | 622 → 622 | ★**只改 docstring 抬头一行** (补权威帧 id `B160x100` / `F30A` / `P60x15`) ★**零行为变化** ★ | stdout 与 `--selftest` 逐字节不变 |
| 5 | `MECH/jd_y0_feasibility.py` | `55db53464eb4a559628f99d6ccd1546f` | `95e2a80d972aaebb22d58b88e0960687` | 651 → 651 | ★**只改 docstring 抬头一行** (同上) ★**零行为变化** ★ | stdout 与 `--selftest` 逐字节不变 |
| 6 | `MECH/BOARD_GEOM_CALIBER_STATUS.md` | `b42026dff243b5dd036bd244ba4af44f` | `61ff4aa735b119342d9eb729bd5c2ec6` | 168 → 233 | ★**纯追加 §5 一节** (scope A / scope B 真数 + 逐文件命中数前后对照 + §1.1 行号现落点 + 机器闸说明) ★**§1~§4 老字一字未删** (★老前缀逐字节保留已验: PREFIX_UNCHANGED = True★) ★ | 文档 |
| 7 | `MECH/check_mech_dual_caliber_gate.py` | (不存在) | `c898273018eabba466a04b88402d286c` | — → 300 | ★**新建** 双口径机器闸 (只读 · 35 条断言 + 5 条自测用例) ★ | 裸跑 rc=0 · `--selftest` 末行 `ALL TESTS PASS` |

★**MECH 域全文件 md5 前后对拍 (`logs/iss352/15_mech_md5_pre_post.txt`)**: ★**CHANGED = 6 / DELETED = 0 / ADDED = 1** ⇒ ★其余 MECH 文件一个字节都没动 (含 md5 钉死的 `MECH/hw_cross_review_check.py` 与判据方向不许动的 `MECH/check_board_geom_caliber_drift.py`) ★

---

## ★B7 · 边界自证 (★一条不许破★) ★

### ★B7-1 · 零写板 (前后双证) ★
| | md5 | mtime |
|---|---|---|
| 迁移前 (`logs/iss352/00_pre_baseline.txt`) | `611b869e13518c3c023fb178f91a0075` | 2026-11-06 07:07:17.362193413 |
| 交卷后 (`logs/iss352/16_board_fingerprint.txt`) | `611b869e13518c3c023fb178f91a0075` | 2026-11-06 07:07:17.362193413 |

⇒ ★**逐字节相同 · 本单没碰板** ★

### ★B7-2 · 零落表 / 零改别人的闸 / 零改别人的分片 / 零外发 ★
- ★零落表: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 前后同值; ★**本单未写 `HW/` 任何文件** ★
- ★零改别人的闸: `MECH/hw_cross_review_check.py` `e521387b87b0fcdf9f22d56f14199967` · `MECH/check_board_geom_caliber_drift.py` `0f70bd049d18d2d308b06a813443d4e3` · `MECH/check_board_frame_coords.py` `d4bd30c241718a8c0baf3084f78e2eb7` · `MECH/check_demo_struct_truth.py` `483d018a66d17d2ead25d1558a1f8ffe` · `MECH/cavity_recalc_check.py` `c4bf9151dd59826fb2320c34e8afbd0f` — ★全部与迁移前同值★; ★**漂移闸的判据方向一个字没动** (`--selftest` 仍末行 `ALL TESTS PASS`) ★
- ★零改别人的分片: `state/fragments/pm.yaml` / `hw.yaml` / `sw.yaml` md5 前后同值; ★本单只写 `state/fragments/mech.yaml`, 且**唯一调用 = `state/frag_write.py --agent mech-lead`** (★零 `open(p,"w")`★) ★
- ★零改 `state/issue_log.yaml`: ★**本单没写** (★签收是 main 的活★) ★
- ★零外发: ★本单零邮件 / 零询价 / 零问询 / 零采购; ★全部数据来自盘上文件 + 本机只读解析 ⇒ 零缺口零外查 ★
- ★不替老板拍板: ★默认档恒为 F30A; 切默认档的权归 U-1 拍完后 main; ★**本单零新增拍板项** ★

### ★B7-3 · 引用零假引用 (MISS = 0) ★
★本页引用的每个 `MECH/` / `HW/` / `state/` / `logs/` 路径逐个在盘自检 ⇒ **MISS = 0** (★自检读数贴 §B6-1 之后·逐个路径 `os.path.exists`★) ★

### ★B7-4 · 本单写过的文件 (★穷举·便于 main 复核★) ★
`MECH/fit_check_v3_30mm.py` · `MECH/cross_review_check.py` · `MECH/fit_check.py` · `MECH/board_port_opening_s6_check.py` · `MECH/jd_y0_feasibility.py` · `MECH/BOARD_GEOM_CALIBER_STATUS.md` · `MECH/check_mech_dual_caliber_gate.py` (新建) · `HANDOFF/2026-11-23_mech-lead_ISS352_MECH双口径第2批.md` (本页) · `state/fragments/mech.yaml` (走 `state/frag_write.py`) · `logs/iss352/` (17 份)
⇒ ★**其余一切未动** (含 `state/issue_log.yaml` / `state/fragments/pm.yaml` / `state/fragments/hw.yaml` / `state/fragments/sw.yaml` / `HW/` 全域) ★
