# ISS-290 · mech-lead 任务书 —— ★★「板那一改一次」那一趟的【结构侧最后一道交叉核对】★★ (★纯分析 + 机器闸 · 零写板★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 14:3x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-290 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页 + 机器闸类** ★ ⇒ ★**零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本** ★ ⇒ ★**符合老板 2026-11-17 00:43「PCB 类先派纯分析/作业包类」纪律** ★
> ★**优先级 (★时间不够就按这个顺序砍★)**: ★**① > ② > ③** ★ ★**① 和 ② 都不许砍** ★

---

## ① 病灶 (★main 本机实读, 行号/路径可复核★)

### ★1.1 「板只改一次」那一趟的 S6 落位, 从来没跟 MECH 侧的保留区核过 ★

★**S6 目标落位 (机器可读, 只读)**: `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:S6_TARGETS` JSON 块 ⇒ ★**20 个 distinct ref, 每条带 `frame` 字段, 全部 = `B160x100`** ★
★**现状 (★hw-lead ISS-274 实测★)**: ★**20 个里 19 个【已经在目标位】⇒ 真实位移只有 `R_SEL_D3_P` 一处** (78.90, 9.50) → (122.30, 5.50) ★ ⇒ ★**但「钉 20 个」这个动作要一次做完 (S6 重出板 ⇒ 20 个位号全被钉)** ★
★**hw-lead 侧的闸查了什么**: `python3 HW/check_board_frame_caliber.py` ⇒ ★**帧标签齐 / 20 条与文档串逐字一致 / 缺位 0 / 重叠 0 / 出界 0** ★ ⇒ ★**但【没查结构保留区】** ★

★**MECH 侧的保留区 (你 ISS-276 / ISS-278 已经出了, 机器可读)**: `MECH/BOARD_ONEPASS_MECH_SYNC.md` (★§1 帧声明 + §5 机器块★) + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (★§3b 两条开口 / §4b 座体高度参数式 / §6b LED 两假设 / §7b 连接器对照表★) ⇒ 至少含:
- ★**SoM 承载区**: ★**焊盘实体 53.80 × 46.78 / 封装外形 56.70 × 46.78** ★ (★hw-lead ISS-274 实测 + 你 ISS-276 独立复算一致★ ⇒ ★**位置必须你自己读板取, 不许抄结论★**★)
- ★**检修口开口 (罩 `J_UART`)**: X 13.790..23.990 × Y 66.300..70.900 (h = 2.54 档) ★
- ★**调试口开口 (罩 `J_DEBUG`)**: X 137.850..148.050 × Y 54.300..58.900 (h = 2.54 档) ★
- ★**两条「座体必须清空区」**: 检修口 X 17.620..20.160 × Y 67.330..69.870 · 调试口 X 142.063..143.838 × Y 55.330..57.870 ★
- ★**`D_LED_G` 可放行空间 (两假设)**: 假设 A: X 6.940..8.250 × Y 63.700..67.900 · 假设 B: 整高自由带 X 1.550..3.450 + X 72.540..73.660 ★

★**⇒ 问题在这里**: ★**两边各自绿, 合起来可能撞** ★ ⇒ ★**ISS-274 的 C 判据不碰结构保留区 · 你的 M1~M5 闸不碰 S6 目标落位 ⇒ 两边之间那段【没人验】★** ⇒ ⇒ ★**那一趟 S6 一跑就撞 ⇒ 板 md5 变第二次 ⇒ Gerber / 投产包 / 留证链 / 盖章 / 发布全白跑 ⇒ ★这正是「板只改一次」最怕的那种撞★ ★**

### ★1.2 座体类器件: 选型写 1.27mm 排针, 板上 land pattern 是 0.50mm ⇒ ★**装不进** ★

★**你 ISS-278 §7b.2 已经查出来 (原样)**: ★**`J_DEBUG` 排针间距: BOM/网表写 1.27 mm (`HW/BOM_v1.csv:71` / 网表 P8 行规格串「1×4 1.27mm 排针 (JTAG)」) ⇒ 板读 land pattern 是 0.50 mm ⇒ Δ 0.77 ⇒ 会 ⇒ 改板** ★
★**`J_UART` 同款**: ★**BOM/网表 1.27 mm ⇒ 板读 0.50 mm ⇒ Δ 0.77** ★
★**⇒ 问题在这里**: ★**这不是「差一点点」, 是【选型的实物排针根本落不进 0.50 间距的 land pattern】★** ⇒ ★**要么改板 (land 改 1.27) · 要么改选型 (换成 0.5 间距的件 —— 市场上 1×N 排针常规间距是 2.54mm, 不是 0.5mm ⇒ 改选型这条路等于改 BOM + 网表) ⇒ 两条路都会动到那一趟的东西** ★
★**⇒ 而【改 land 到 1.27mm】会连带改结构侧**: ★**排针跨度从 1.50 mm 变 3.81 mm ⇒ 座体占位变 ⇒ 必须清空区变 ⇒ 开口宽度/间隙要重算 ⇒ ★**这正是你的活** ★**

### ★1.3 `board.corner_radius_mm` = 3.0, 但 Edge.Cuts 是 4 条直角线 (0.0) ⇒ 贴角 keep-out 口径失真

★**你 ISS-278 §7b 已经登记**: ★**`board_corner_radius_mm` MECH 期望 3.0 / 落表板实测 0.00 (Edge.Cuts = 4 条直角 `gr_line`) ⇒ Δ 3.000 ⇒ 会 ⇒ 贴角器件的 keep-out 按 3.0 圆角算 ⇒ 算出来的可用区比实际小/错** ★ (★归 hw-lead★)
★**⇒ 本单要交**: ★**一个明确口径 (★以板实测为准还是改板框加圆角★) + 两种口径下的贴角可用区差值** ★ ⇒ ★**只列事实与代价, 不代拍** ★

---

## ② 你要交的东西 (★一句话★)

★**把「板那一趟」在结构侧最后两个没人交叉验过的接口, 一次验完, 落成【一份表 + 一道闸 + 一份「必须在那一趟一起改」的清单】★** ★

★**交卷物 (5 件)** ★

1. ★**新建** `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★机器可读★):
   - ★**§1 坐标系声明 (置顶)**: ★**本文一切坐标 = 现役台架板帧 `B160x100`** ★ (★Edge.Cuts 实读 160.10 × 100.10 / 8 铜层 / 186 封装★) ⇒ ★**`F30A`(60×30) 与 `P60x15`(60×15) 的数一律不可代入** ★
   - ★**§2 MECH 侧保留区全集 (逐条)**: ★**字段固定 6 项** ★ ⇒ `id` / `source_iss` / `type` (★禁入 / 必清空 / 可放行 / 口径★) / `geometry` (★矩形或框, 写清是哪两个角★) / `physical_reason` (★为什么这是禁区, 一句话★) / `evidence` (★[实测] / [推算] / [0数据]★) ⇒ ★**§2 里的几何必须自己从板/脚表重算一遍, 不许照抄任何交卷单的数 (★包括不许抄本任务书里的数★)★** ★
   - ★**§3 ★S6 的 20 个目标落位 × 保留区 逐个核对表★** ⇒ ★**每条 S6 目标位一行** ★ ⇒ 字段: `ref` / `target_x` / `target_y` / `footprint_extent` (★该 ref 在板上的封装外形范围, 实读★) / `hit_zones` (★落进哪个保留区, 无则空★) / `verdict` (★通过 / 冲突 / 需净距★) / `min_clearance_mm` / `evidence`
   - ★**§4 ★座体类器件三方对照表★** ⇒ ★**对象至少含 `J_DEBUG` / `J_UART` / `J_USB_C` / `J_CHG` / `J_SOM_P1` / `J_SOM_P2` / `J_SOM_P3` / `J_SOM_P4`** ★ ⇒ 每行: 位号 / ★**BOM·网表规格串 (pitch + 脚数 + 座体外形)** ★ / ★**板上 land pattern 实测 (pitch + 脚数 + 铜箔外形)** ★ / ★**结构占位要求 (座体宽/高/开孔)** ★ / `verdict` (★可装 / **装不进 ⇒ 必须改封装** / [0数据]★) / ★**改板连带影响 (开口尺寸 / 必须清空区 / 净距 / SoM 承载区)** ★ / `evidence`
   - ★**§5 「改板 vs 改选型」两条路的代价对照 + ★「必须在那一趟一起改」清单★** ⇒ ★**只列事实与代价, 不代拍** ★ ⇒ ★**清单必须写成【可直接进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的条目格式】(★每条带: 标题 / 现状 [实测] / 改法 / 判据命令 / 归谁改★)★** ★
   - ★**§6 `corner_radius` 口径**: ★**3.0 vs 0.0 的两种口径下贴角可用区差值 + 建议** ★
   - ★**§7 机器可读 JSON 块 (放全文最后)**
2. ★**新建** `MECH/check_onepass_struct_crosscheck.py` (★机器闸★):
   - **N1** ★**帧标签**: ★**S6 的 20 个目标位逐个带帧标签, 且帧 = `B160x100`** ★ (★漏标一条 / 错帧 ⇒ 红★)
   - **N2** ★**SoM 承载区零冲突**: ★**20 个目标位 (按目标位原点 + 该 ref 的 footprint 外形) 与 SoM 承载区 (焊盘实体 + 封装外形) 零冲突** ★
   - **N3** ★**两条开口**: ★**20 个目标位不得落在检修口开口 / 调试口开口矩形内 —— 两条分别验, 不许合并验** ★
   - **N4** ★**必清空区净距**: ★**20 个目标位到两条「座体必须清空区」的最小净距 ≥ CRIT** ★ ⇒ ★**CRIT 必须取你自己既有 MECH 判据里的那个值 (0.60), 不许新造一个★** ★
   - **N5** ★**座体三方对照表完整**: ★**§4 表里每个 `J_*` 行的四个字段 (BOM 规格 / 板读 land / 结构占位 / verdict) 都不许为空** ★ ⇒ ★**不许用「待定」糊过去** ★
   - **N6** ★**受保护 5 件 md5 逐字节不变** (★板 / `.kicad_pro` / 网表 / 脚表 / BOM★)
   - `--selftest` ★**反向用例 ≥ 5 条** (★每条自证真改到目标★): ★**① 把某个 S6 目标位挪进 SoM 承载区 ⇒ N2 红 ② 把某个目标位挪进调试口开口 ⇒ N3 红 ③ 抽掉一个帧标签 ⇒ N1 红 ④ 把两条开口合并成一条 ⇒ N3 红 ⑤ 把 CRIT 改小 ⇒ N4 红 ⑥ 清空 §4 某行一个字段 ⇒ N5 红 ⑦ 改受保护件 ⇒ N6 红** ★
3. ★**追加式订正** `MECH/BOARD_ONEPASS_MECH_SYNC.md` (★**老字一字不删不改成★**):
   - ★**新增 §9「S6 目标落位 × MECH 保留区 交叉核对」** ★ ⇒ ★**含一句「给 hw-lead 的 S6 落位约束句 (现役板坐标版)」★** ★
   - ★**新增 §10「座体类器件三方对照摘要 + 排针 pitch 1.27 vs 0.50 的结构后果」** ★ ⇒ ★**含「改 land 到 1.27」后开口/必须清空区/净距怎么变 (实测算)★** ★
4. ★**交卷单** ★**新建** `HANDOFF/2026-11-17_mech-lead_ISS290_结构侧最后一道交叉核对.md` ⇒ **B1~B6 六块齐全** (★B1 结论摘要 · B2 验收标准逐条自评 · B3 反向自证贴实跑原始输出 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令★) ⇒ ★**B3 必贴 §3 的 20 行逐个核对表原始输出** ★
5. ★**分片** ★**走** ★**`python3 state/frag_write.py --agent mech-lead`** ★ (★**禁止 `open(p,"w")`** ★): 登记 ★**2 条 claim** (★交叉核对已立 + 闸已立★) + ★**artifact** ×3 + ★**1 条 need 给 main** (★「§5 那份『必须在那一趟一起改』清单 ⇒ 请 main 转 hw-lead 并入 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`; ★其中『排针 pitch 1.27 vs 0.50』与『corner_radius 3.0 vs 0.0』两条会改板 ⇒ 必须排在『板只改一次』之前定★」★) + ★**status** (phase=delivered · progress_pct=100)

---

## ③ 验收命令 (★本机实跑, rc 原样贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_struct_crosscheck.py                # rc=0 (★新建★)
python3 MECH/check_onepass_struct_crosscheck.py --selftest     # rc=0 (★新建★, ≥5 条)
python3 MECH/check_onepass_mech_sync.py                        # rc=0 (★ISS-278 的闸, 不许被改红★)
python3 MECH/check_board_frame_coords.py                       # rc=0 (★ISS-276 的闸★)
python3 MECH/check_board_frame_coords.py --selftest            # rc=0
python3 MECH/board_port_opening_s6_check.py --json             # rc=0 (★现值别改★)
python3 MECH/check_demo_struct_truth.py                        # rc=0 (★ISS-273 成果, 只读★)
python3 HW/check_board_frame_caliber.py                        # rc=0 (★ISS-274 的闸, 只读★)
python3 HW/check_board_frame_caliber.py --selftest             # rc=0
python3 HW/check_onepass_preflight_coverage.py                 # rc=0 (★只读, 不许改 HW/★)
python3 state/merge.py                                         # rc=0
python3 state/gate_check.py                                    # rc=0 (★Q1 18/18★)
python3 state/issue_check.py                                   # rc=0
```

★**受保护 5 件 (跑前跑后 md5 逐字节相同, 原样贴进交卷单)**: ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★

---

## ④ 边界 (★逐条自证, 写进交卷单 B2★)

- ★**零写板** (★板 md5 + mtime 双重自证★) ⇒ ★**不许跑 `state/gen_pcb_netlist_board.py`, 不许跑任何布线臂 (S8 不碰), 不许碰 `HW/PCB/demo_mainboard.kicad_pcb`** ★
- ★**零落表** (★网表 / 脚表 / BOM 三个 md5 前后不变★) ⇒ ★**不许碰 `HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★
- ★**零改 `HW/`** (★一个字不许改★) ⇒ ★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `HW/PCB/BOARD_FRAME_CALIBER.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` 一律只读** ★
- ★**零改既有 MECH 判据脚本** (★只许新建 `MECH/check_onepass_struct_crosscheck.py`★) ⇒ ★**不许改 `MECH/check_onepass_mech_sync.py` / `MECH/check_board_frame_coords.py` / `MECH/check_demo_struct_truth.py` / `MECH/board_port_opening_s6_check.py`** ★
- ★**零改生成器** (`state/gen_pcb_netlist_board.py` / `state/gen_kicad_sch.py` 一律只读)
- ★**零改决策页 / 零改 issue_log / 不自签 verified** (★verify_by = main★)
- ★**零外发** (★不许发邮件 / 不许联系供应商 / 不许下采购单★)
- ★**只写自己的分片** (★`state/fragments/mech.yaml`★) ⇒ ★**不许写 `hw.yaml` / `sw.yaml` / `pm.yaml`** ★
- ★**实物 [实测] = 0 条** (★本机无量具/无打印机 ⇒ 任何需要实物才能定的量, 一律标 `[0数据]` 并给降级路径, 不许编★)
- ★**并发提示 (★必读★)**: ★**hw-lead 的 ISS-287 与 sw-lead 的 ISS-288 此刻正在飞 ⇒ `HW/` 与 `SW/` 那边随时有人写 ⇒ 你只读它们, 只写 `MECH/` + `HANDOFF/` + 你自己的分片 ⇒ 跑验收前若某个 `HW/` 闸红了, 先看是不是别人刚改的, 不要替别人改** ★

---

## ⑤ 你要回答 main 的三个问题 (★写进交卷单 B4★)

1. ★**S6 那 20 个目标落位, 与 MECH 保留区到底有没有冲突? 有几条? 哪几条? 最小净距多少?** ★ ⇒ ★**如果零冲突, 就把「零冲突」变成一道机器闸 (N2/N3/N4) 钉住, 以后任何一次布局改动自动重判** ★
2. ★**`J_DEBUG` / `J_UART` 的 1.27mm 排针: 改 land 到 1.27mm 的话, 两条开口 / 两条必须清空区 / 间隙各变成多少? 落在 h 三档里还过不过?** ★ ⇒ ★**给出「改 land」的结构后果 (实测算), 别只说「会冲突」** ★
3. ★**`corner_radius` 3.0 vs 0.0: 贴角可用区按哪个口径算? 两种口径差多少?** ★ ⇒ ★**给建议 + 代价, 不代拍** ★
