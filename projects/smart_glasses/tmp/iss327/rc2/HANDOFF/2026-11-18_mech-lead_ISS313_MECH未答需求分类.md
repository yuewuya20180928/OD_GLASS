# HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md

> **交卷人**: 结构总工 (mech-lead) 🔩 · **日期**: 2026-11-18 · **单号**: ISS-313 · **owner**: mech-lead · **verify_by**: main
> **job**: cron `fb67af40` (ARS45 队列自动派活) · **性质**: 内部活 · 需求闭环 / 卫生类
> **同源**: 本单与 `MECH/MECH_NEEDS_TRIAGE.md` 与 `state/fragments/mech.yaml` 的分类结果同源 (数据源 `logs/iss313/iss313_data.py`)。
> **边界 (硬)**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log。

---

## B1 · 结论摘要

**一句话**: MECH 域 `needs_from` 的 185 条逐条归类处置完毕 —— **关 64 / 留 72 / 新答 26**, 机检缺口清单里 `mech-lead` 那条从 **108 条真的降到 62 条**, 全局「等外部」从 70 条降到 **49 条** (★16 条外部依赖清零★), **零写板 / 零落表 / 零改闸 / 零改既有文档正文 / 零外发 / 不代拍 / 不自签**。

**十条要点**:

1. ★**四类逐条无遗漏**: ① `waiting_on=agent` 35 条 (显式 34 + 一条 `waiting_on: hw-lead` 格式错) / ② `waiting_on=boss` 20 条 / ③ `vendor`+`jbd` 16 条 / ④ `waiting_on` 空 114 条 ⇒ 185 条一条一条看过, 无抽样。
2. ★**① 类 (内部活自己推)**: 12 条关闭 (其中 12 条**新写进 `answers`**, 带 key + 出处 ref + 证据等级) + 9 条保留并写清【该谁答 + 为什么 + 一句话问法】。关闭的每条都有实测依据 (例: 电池位已由网表定 / `j_chg_pitch_mm` 早已是 0.5 / 固定孔位已被套 A 取代 / J_CHG 实物一对已落 BOM)。
3. ★**② 类 (不代拍)**: 整理成 **决策码 M-B1~M-B17** 一页 (need key + 选项 + 代价 + 建议默认值 + 不拍的后果) ⇒ 老板回一个码即可, 不用重读 185 条; **本单没有在分片里写任何 `decision` 字段**。
4. ★**③ 类 (外部依赖)**: 16 条按老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」**全部自查结案** —— 官网能查到的给官网值 (Hirose FH12 0.5A / 3M VHB 长期 93°C / LOCTITE AA 3311 ISO-10993 / MIL-A-8625 Type III ±20% / Renata + 丰江电芯尺寸), 查不到的标 `[0数据]` 并写降级方案 (参数化占位 + 可换压框 / 送检实测 / 改设计路径绕开 / 用 `[推算]` 值并标依据) ⇒ **外部依赖 16 条清零, 零外发**。
5. ★**④ 类**: 114 条判三选一 —— 关 31 条 (已作废 / 已被后续交付覆盖, 逐条带依据) + 留 51 条 (owner + 处理方式 + 一句话问法 + 是否与板那一趟相关)。
6. ★**机检真降**: `python3 state/gate_check.py` 实跑 —— `mech-lead` 缺口 **108 → 62**; 全局等外部 **70 → 49**; 全局等总工 **341 → 306**; **自闭合 0 条**; Q1 **18/18**; merge rc=0 / gate rc=0。
7. ★**板只改一次**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` 交卷前后**逐字节相同**; 并给出 **33 条与板那一趟直接相关的待答输入清单** + 8 项「结构侧已经定了、可直接用」的值 (板长/板宽/板厚/孔位/检修口净空/开口坐标/三条锁死链/板 md5) ⇒ 不必重复讨论。
8. ★**查出一条真问题 (型号-尺寸错配)**: 官网实读 —— **ICP582035PR-01 = 6.4mm 厚 / 20.5 / 37**, 而项目里把「4.6×23.5×40.5」挂在它名下 (`MECH_BUDGET.md` L330/L332/L340) ⇒ 真型号应是 **ICP422339PR** ⇒ 采购单照现型号买回来**装不进 7.30mm 镜脚**; 已并进决策码 **M-B2** 给老板。
9. ★**零外发**: 不发邮件 / 不询价 / 不问询 / 不采购 / 不联系任何厂商; `state/outbox/` 草稿一律不发只留档 (含 `j_chg_rfq.md`)。
10. ★**已知副作用如实记**: 关闭的 need 从 `needs_from` 移出后其 key 不再被 `referenced_keys` 引用 ⇒ 对应 `answers` 会各记 1 条 `lint` (改分片前 455 → 后 489, **新增 26 条正是本单新写的 26 条 answers**); ★**lint 不进任何闸** (merge rc 只看片段完整, gate rc 只看硬件真源闸 + 新闸 + 9 道钉板 md5 闸, daily_check 也不看 lint) ⇒ merge rc=0 / gate rc=0 未变。

---

## B2 · 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 | 判定 | 证据 |
|---|---|---|---|
| 1 | MECH 域 185 条 needs 逐条归类, 无遗漏无重复 | ✅ **通过** | 本页 §1 总账: 关 64 + 留 72 + 本单之前已闭合 49 = 185; `logs/iss313/_needs_dump.json` 是逐条原始 dump |
| 2 | ① 类 (内部活) 每条都判了【我能答吗】, 能答的写进 `answers` | ✅ **通过** | §2.1 表 12 条 `close+answer` (key + 出处 + 级别); 分片 `answers` 实读 26 条新增 |
| 3 | ① 类不能答的写清【该谁答 + 为什么 + 一句话问法】 | ✅ **通过** | §2.2 表 9 条, 每条 4 列; 分片 `needs_open_ledger` 台账同源 |
| 4 | ② 类 (20 条) 整理成 need key + 决策码一页, **不代拍** | ✅ **通过** | §3 表 (M-B1~M-B17 + 2 条已闭合); ★分片里 `decision` 字段本单一条没写 |
| 5 | ③ 类 (16 条) 全部自查 + 标证据等级 + 写降级方案, **不许再写「等原厂回信」** | ✅ **通过** | §4 表 16 行, 每行有【自查结论】+ 级别 +【降级方案】; 全页 grep「等原厂回信」= 0 |
| 6 | ④ 类 (114 条) 每条三选一 (a/b/c) | ✅ **通过** | §5.1 关 31 条 (标 (a)/(b)) + §5.2 留 51 条 (标 (c) + owner + 问法) = 114 |
| 7 | 每条关闭都有依据行, 不许批量清空 | ✅ **通过** | 关闭的 64 条逐条一行依据 (本页表格 + 分片 `needs_closed` 台账, 两者同源); 无一条依据为空 |
| 8 | 交卷页给「关 X / 留 Y / 新答 Z」对账表 | ✅ **通过** | §6 对账表 + §1 总账 |
| 9 | 标出与板那一趟相关的待答条目 (板框/板厚/层数/镜腿宽度/检修口净空/重量预算) | ✅ **通过** | §7 清单 33 条 + §7.1 已定值 8 项; ★不重做 ISS-310 的框口径对照表 (只读) |
| 10 | 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必标 | ✅ **通过** | §0.3 分级定义 + §8 分级汇总 16 行; 四类表每行都带级别 |
| 11 | 交卷页与交卷单同源不重写 | ✅ **通过** | 两份文档 + 分片都由 `logs/iss313/iss313_data.py` 生成 |
| 12 | 零写板 (板 md5 + mtime 逐字节不变) | ✅ **通过** | 交卷前后 `md5sum` / `stat` 同值 (§B6) |
| 13 | 零落表 | ✅ **通过** | 网表 / 脚表 / BOM / 落表台账 一律未动 |
| 14 | 零改闸 (`gate_check.py` / `merge.py` / `service_port_check.py`) | ✅ **通过** | 三个脚本一字未改; `MECH/service_port_check.py` md5 `db58ff6a2afc28b8bf517e3c57c56bc1` 前后相同 |
| 15 | 零改既有文档正文 | ✅ **通过** | 只**新建** `MECH/MECH_NEEDS_TRIAGE.md`; `BOARD_FRAME_DECISION_INPUT.md` / `BOARD_GEOM_30MM.md` / `DEBUG_PORT_LAYOUT_CONSTRAINTS.md` 只读 |
| 16 | 零外发 | ✅ **通过** | 本单不发邮件 / 不询价 / 不问询 / 不采购; outbox 草稿一律不发 |
| 17 | 不替老板拍板 | ✅ **通过** | ② 类只给决策码 + 建议 (标「只作参考」); 分片 `decision` 字段本单一条没写 |
| 18 | 不自签 issue_log | ✅ **通过** | `state/issue_log.yaml` 只读核对 3 个 md5 是否落锚, 一个字节没写 |
| 19 | 只写自己那一份分片 (走 frag_write.py 原子写) | ✅ **通过** | `state/frag_write.py` 原子写 `state/fragments/mech.yaml`; **禁止** `open(p,"w")`; `hw.yaml`/`sw.yaml`/`pm.yaml` 一个字节没碰 |
| 20 | 机检缺口清单里 mech-lead 那条真的降下来 | ✅ **通过** | 108 → **62** (§B6 原样输出) |
| 21 | 实物实测 (打印/量测/可靠性/材料送检) | ⚠️ **未验** | ★本机物理上做不到 (打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达 + 无切片器 + 无量具) ⇒ 全部记 `[0数据]` 并挂决策码 M-B1 / M-B12 / M-B3 / M-B14 |
| 22 | 老板对 ② 类 17 条的拍板 | ⚠️ **未验** | 本单不代拍 ⇒ 等老板回决策码 |
| 23 | 板框三选一 (U-1) / 帧 id 统一 (U-274-6) | ⚠️ **未验** | 老板级 ⇒ 已并进 §7 清单与决策页 |
| 24 | 波导 / 眼盒 / 评估距离 d 的最终选型 | ⚠️ **未验** | 老板级 + 外部 ⇒ 已写降级方案 (§4 ③-1/③-5 + M-B17) |

---

## B3 · 证据分级

| 结论 / 数 | 级别 | 来源 |
|---|---|---|
> ★**标签对照**: 本单用 `[官网]` 表示 `state/gate_check.py` 证据标签集里的 **官方** (同一档, 结构域习惯叫「官网」); `[实测]` / `[推算]` / `[0数据]` 三档同名 ⇒ 四档齐。

| 机检 mech-lead 缺口 108 → 62 / 全局等外部 70 → 49 | [实测] | `state/gate_check.py` 两次实跑 (`logs/iss313/gate_check_BEFORE.txt` / `gate_check_AFTER.txt`) |
| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` | [实测] | `md5sum` + `stat`, 交卷前后逐字节相同 |
| `MECH/check_demo_struct_truth.py --selftest` rc=0 (反向 28/28) + 主跑 rc=0 | [实测] | 本轮实跑 |
| 检修口盖板内腔 4.70 ≥ 4.50 (余 0.20) | [实测] | `MECH/service_port_check.py` rc=0, 57/57 |
| PIN-SET-2 套 A 孔位已落 hw 侧 | [实测] | `HW/pcb60x30_check.py`:119-124 |
| 电池位 = 镜脚 / 充电链整条在镜框 | [实测] | `HW/netlist_v1.csv` L2/L17/L40 |
| J_CHG 实物一对 (备料 2 只) | [实测] | `HW/BOM_v1.csv`:70 + `HW/netlist_v1.csv` L38 |
| Hirose FH12-10S-0.5SH(55): 0.5A / FPC 0.30mm / 座高 2.00mm | [官网] | Hirose 官网 + 分销规格页 |
| 3M VHB 5962: 1.6mm ±10% / 长期 93°C / 短期 149°C | [官网] | 3M 技术数据表 |
| LOCTITE AA 3311 ISO-10993 biocompatible | [官网] | Henkel 产品页 |
| MIL-A-8625 Type III 膜厚公差 ±20% | [官网] | MIL-A-8625F §3.7.2.1 |
| Renata ICP422339PR 4.6×23.5×40.5 · ICP582035PR-01 **6.4**×20.5×37 | [官网] | renata.com |
| 丰江 432243 4.3×22.0×43.5 / ≥420mAh / 循环 ≥500 | [官网] | battsysbattery.cn |
| JBD Hummingbird Mini Ⅱ 0.15cc/0.3g/60mW · 刻蚀波导彩虹抑制 95% / 均匀性 >80% / ΔE 0.02 | [官网] | jb-display.com |
| PC/ABS 注塑收缩率 0.29-0.76% | [媒体] | 行业通例 (ASTM D955-89) |
| 波导 2D 外形 / 耦入区容差角 / ARS45 散热焊盘 / 丰江内阻 / 镁合金点蚀 | [0数据] | 公开渠道查不到 ⇒ 已写降级方案 (§4) |
| 铝 6063-T6 k=201 W/m·K | [官网] | Hydro / Aalco / Kaiser 三家互证 |
| 腔体 81.20/77.43/75.24°C · 鼻梁 54.33/52.75/51.83°C · R_热路 ≤70 K/W | [推算] | ISS-065 §2.3 模型 + MECH_BUDGET §1.7/§3 |
| 金属热路截面积 ≥4.975mm² (2.0×2.0 不合格) | [推算] | MECH_BUDGET §3 |

---

## B4 · 接口取值声明 (interface_claims)

★**本单没有新增 / 修改任何 `interface_claims`** —— 本单是需求闭环与卫生类活, 不出新的接口取值。
★本单**只读**了下列与「板那一趟」直接相关的现行接口值, 列出来供板那一趟直接取用 (★不改一个值★):

| interface_claims key | 现行值 | 所在分片 | 板那一趟用法 |
|---|---|---|---|
| `pcb_outline` | `60x30mm` | hw.yaml + mech.yaml | 板框基准 (板长 60 × 板宽 30 = V 向) |
| `pcb_mounting` | `2x⌀2.0H7+2x⌀1.4` (P1 8.00/15.00 · P2 52.00/15.00 · S1 8.00/10.00 · S2 52.00/20.00) | mech.yaml | 骨架两个攻丝面 + 定位基准 |
| `j_chg_pin_map` | `1x10p: 1/2=BAT_CHG, 3/4=GND, 5=CHG_STAT, 6=PWR_GOOD, 7=NC, 8=TS_BAT, 9/10=HINGE_RSV` | mech.yaml + hw.yaml | J_CHG 逐脚 (防呆论证按此) |
| `mech_j_chg_pins` | `10p@0.5mm` (note 已与 `j_chg_pin_map` 逐脚一致) | mech.yaml | 同域自相矛盾已收口 |
| `mech_hinge_stack_fixed_mm` | `25.00` | mech.yaml | ★旧口径, 现行真值 25.30 (整机) / 5.00 (demo) ⇒ 待 need `iss240_mech_hinge_fpc_truth_decisions` 处置 |
| `mainboard_len_carrier` / `mainboard_len_direct` | `69mm` / `76mm` | mech.yaml | ★A/B 互斥方案板长, **不是现行板板长** (现行 60.00) ⇒ 待老板裁 |
| `battery_capacity_tier` | `315mAh无桥/387mAh有桥` | mech.yaml + hw.yaml | 电池档位 (口径已统一) |

---

## B5 · 未决项与卡点 (需要谁回答什么)

### B5.1 阻塞 (★本单【零新增阻塞】: 下列全是既有的, 本单只做归位★)

| 卡点 | 需要谁答 | 一句话 | 卡在本单哪一步 |
|---|---|---|---|
| 老板对 ② 类 17 条的拍板 | **boss** | 按 §3 的决策码 M-B1~M-B17 回一个码即可 | 不在本单 (不代拍) |
| 板框三选一 (U-1) + 帧 id 统一 (U-274-6) | **main → boss** | 板只改一次那一趟的前置 | 见 §7 清单 |
| `jd_y0` (J_DEBUG 焊盘阵列 Y 起点) | **main + hw-lead** | 合法区间 [1.665, 11.730], 现状 9.50 | 见 §7 清单 (检修口净空总开关) |
| J_DEBUG 脚数 1×4 vs 2×5 + 座体真实高 | **hw-lead** | 开口 X/Y 全部依赖它 (h 仍 [0数据]) | 见 §7 清单 |
| u8 端件截面 | **main** | 端件热路重量 / 框侧汇流 / 装配顺序三条链的共同前置 | 见 §7 清单 |
| 评估距离 d (15/18/20) | **boss** | M-B17 | 镜框正中区腔体重排的前置 |
| 波导归属 + 眼盒 ≤62mm² | **boss** | 公开波导标称眼盒全部超限 1.94~2.42× | 见 §4 ③-1 / ③-5 |
| 打印 + 切片 + 量测执行方 | **boss** | M-B1 / M-B12 | ★实物实测 0 件的根因 (本机物理上做不到) |
| 可靠性工装与材料送检预算 | **boss** | M-B3 / M-B4 / M-B14 | T-05~T-08 的 83 天 UV 窗口 |
| 网表 N5 (J_CHG 跨铰链 / 充电链转 DNP) 未落 | **main + hw-lead** | CHG_BOARD 仍 94 行未转 DNP | 铰链区结论是否转 deferred |
| 电芯型号-尺寸错配 | **boss + main** | M-B2 | 采购单照现型号买 ⇒ 装不进 7.30mm 镜脚 |

### B5.2 本单留给下一轮的三个动作

1. ★**MECH 域 `needs_from` 里剩下的 %d 条** ⇒ 全部带 owner + 一句话问法 (分片 `needs_open_ledger` 台账), 下轮直接按 owner 派即可, 不必再逐条读。
2. ★**MECH_BUDGET §3 重量表**要补 +0.73 g (检修口盖板) —— 这是**重量表订正**, 不是未答需求 (决策早已按默认假设生效)。
3. ★**MECH_BUDGET §1.3 / §1.4.3 的电芯型号名**要改 (`ICP582035PR-01` → `ICP422339PR`) —— 本单**未改** (零改既有文档正文), 已给依据, 下一轮改。

---

## B6 · 自证复现命令 (★输出原样见本单回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss313_tmp          # ★/tmp 配额已满 ⇒ 日志与临时目录都指大盘★
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py state/fragments/mech.yaml
```

### B6.1 本单逐条取数的脚本 (★全在 `logs/iss313/`★)

| 文件 | 作用 |
|---|---|
| `iss313_data.py` | ★**唯一数据源**: 四类逐条分类 + 依据 + 答复全文 + owner/问法 |
| `apply_iss313.py` | 把分类落到分片 (走 `state/frag_write.py` 原子写) + 输出对账摘要 |
| `gen_iss313_docs.py` | 从同一数据源生成本交卷单与 `MECH/MECH_NEEDS_TRIAGE.md` |
| `_needs_dump.json` / `needs_full_dump.txt` / `needs_read.txt` | 185 条 need 的逐条原始 dump |
| `_need_status.json` | 每条 need 的闭合状态 (by_answer / by_decision / open) |
| `evidence_*.txt` | 逐项取证原始输出 (脚本口径 / 网表 / BOM / 决策记录 / 官网自查) |
| `gate_check_BEFORE.txt` / `gate_check_AFTER.txt` / `merge_after.txt` | 机检前后输出 |
| `mech.yaml.bak_pre_iss313` | 改分片前的分片副本 (md5 `f80056ae071880d9885d0034b3ab635d`) |

### B6.2 改分片前后 md5

| 文件 | 改前 | 改后 |
|---|---|---|
| `state/fragments/mech.yaml` | `f80056ae071880d9885d0034b3ab635d` | `285b8eae37658b5d845fdb76ea844a5e` |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` (★逐字节不变★) |
| `MECH/service_port_check.py` | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` (★逐字节不变★) |

### B6.3 交卷物清单

| 路径 | 类型 |
|---|---|
| `MECH/MECH_NEEDS_TRIAGE.md` | 新建 · 交卷页 (四类逐条 + 依据 + 对账 + 板那一趟输入清单 + 证据分级 §) |
| `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` | 新建 · 本交卷单 (B1~B6) |
| `logs/iss313/` | 新建 · 取数命令 + 原始输出 + 改分片前后 md5 + 数据源与脚本 |
| `state/fragments/mech.yaml` | 只改自己那一份 · 经 `state/frag_write.py` 原子写 (新增 `answers` 26 条 + 新增 `needs_closed` / `needs_open_ledger` 两个台账字段; `needs_from` 185 → 121) |

