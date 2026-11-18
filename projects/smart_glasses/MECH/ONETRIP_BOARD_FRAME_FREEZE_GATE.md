# MECH/ONETRIP_BOARD_FRAME_FREEZE_GATE.md —— 「板只改一次」那一趟的【板框冻结闸 U-1】一页说明 (mech-lead)

> **交卷人**: 结构总工 (mech-lead) · **日期**: 2026-11-19 · **单号**: ISS-336 · **单据**: ISS-316 §2-4 的设计稿
> **决策依据**: 决策码 **M-B18** 的 (a) 项 = **路 B = 做成机器闸** (main 2026-11-18 09:4x 裁)
> **本文件只讲一件事**: `MECH/check_board_frame_freeze_gate.py` 这条闸的**七条判据怎么落**、**阈值从哪来**、**红了怎么办**。

---

## 0. 一句话

「板框冻结了没有」以前只有一句人话 ⇒ 谁都能在作业包里宣称已冻结 ⇒ 板那一趟可以在 U-1 未拍时开工 ⇒ **板 md5 第二次变 ⇒ Gerber / 投产包 / 留证链全部作废重做 (ISS-319 §D-2-1 逐字: 2-4 周 + ¥4-8K)**。
本闸把 ISS-316 §2-4 的 **C1~C7 七条判据**做成一条可跑的机器闸 + 一套 **6 条反向用例**自测。

★**本闸不代老板拍 U-1**: 板框三选一 (B160x100 / F30A / P60x15) 只「列档 + 判红原因 + 谁拍」★

---

## 1. ★★今天这闸【应该红】还是【应该绿】★★ (★K-6 的诚实判断★)

| | 今天的读数 | 为什么 |
|---|---|---|
| **C1~C6** | ✅ **全绿** | 判的是**现行几何口径的自洽性** (60×30 / 1.00mm / 6 层 / 套 A ⇒ F30A 在 36 档里 `can_open == true`) ⇒ **与「拍没拍」无关**, 今天的盘面本来就自洽 |
| **C7** | ❌ **红** | need `proto_pcb_freeze_gate` 在分片侧**零条闭合记录** ⇒ 板框三选一仍待老板拍 ⇒ **今天红 = U-1 还没拍, 正确** |

★**这是【如实报告病灶】, 不是闸坏了** ★

⇒ **红线的归属必须分清 (★交卷页 §B5 同款★)**:
- **C7 红** = **等老板拍 U-1** (★不是本单的活★) —— 本单交的是「机器判据」, 不是「U-1 的答案」。
- **C1~C6 红** = **本单的活** —— 现行几何口径本身不自洽 ⇒ 是结构侧的错, 得改口径。

★**C2 是唯一一条「将来会红」的**: 认领句一落表 (帧 id = F30A), 它就会拿 `cal:FRAMES.current_frame` (= 今天的 `B160x100`) 对账 ⇒ **认领句与台账不同步 ⇒ C2 立刻红** ⇒ 这就是 RC-5 那条反向用例要抓的东西 (★见 §4★)。

---

## 2. ★C1~C7 逐条 ⇒ 代码里哪一段★

| 判据 | 内容 (ISS-316 §2-4 逐字) | 判红条件 | 代码位置 |
|---|---|---|---|
| **C1** | 帧 id ∈ `cal:FRAMES` 的三套之内, 且**非空** | 空 / 拼错 / 第四个值 | `judge()` C1 段 → `_find_frame_id()` |
| **C2** | 帧 id == `cal:FRAMES.current_frame` | 不一致 (认领句写 F30A 但 current_frame 仍是 B160x100) | `judge()` C2 段 (★只在**有认领句**时才判★) |
| **C3** | 板厚 ∈ 允许板厚集 | 缺板厚 / 板厚 = 1.22 / 1.60 / 非数字 | `judge()` C3 段 (★允许集 = 36 档 `cavity_ok` 现推★) |
| **C4** | 层数 ∈ 层数档集 | 缺层数 / 非数字 / 其它值 | `judge()` C4 段 (★层数档集 = `LAYER_TIERS` 现读★) |
| **C5** | 孔位 = PIN-SET-2 套 A 四孔, 且**该帧上四孔全部成立** (`holes.all_fit == true`) | 孔位口径错 / 帧上是 `P60x15` (套 A 不成立) | `judge()` C5 段 (★只看**帧**, 与板厚/层数无关★) |
| **C6** | 该 (帧, 板厚, 层数) 组合在 36 档里 `can_open == true` 且 `red_reasons == []` | `B160x100` 任一档 / `F30A` 的 1.22 与 1.60 / `P60x15` 任一档 | `judge()` C6 段 |
| **C7** | `proto_pcb_freeze_gate` **已闭合**, 且该记录的答案里**逐字含帧 id + 板厚 + 层数** (★不许是「板框已定」这种空话★) | need 没闭合 / 闭合了但答案里没有这三个数 | `read_claim()` + `judge()` C7 段 (★真源见 §3★) |

★**rc 约定**: `rc=0` = 七条全绿; `rc=2` = 至少一条判红, 并**逐条打印判红原因** (措辞与 `board_frame_feasibility.red_reasons` 同款)★

---

## 3. ★C7 的真源 (★ISS-316 §2-4 的一处订正·★本机实读确认★)★

★**ISS-316 §2-4 原写**: 「`proto_pcb_freeze_gate` 在 `state/issue_log.yaml` 里有闭合记录」。
★**本机实读纠正**: `state/issue_log.yaml` 的顶层**只有 `_schema` / `_owners_legal` / `issues` 三项** ⇒ **零条 need 闭合记录** ⇒ 那句话指向**盘上不存在的字段** (★ISS-281 §3-S10 那一类病★)。

⇒ **真源 = 分片侧**:

| 读哪份文件 | 读哪个字段 | 怎么匹配 |
|---|---|---|
| ① `state/fragments/mech.yaml` (need 的登记所在分片, owner=mech-lead) | `needs_closed[]` 里 `key == "proto_pcb_freeze_gate"` 的那条 (字段: key / iss / closed_at / closed_by / cls / action / reason / evidence / evidence_level / answer_key / answer_ref) | **闭合** = 该条命中, **或** `answers[]` 里同 key 的一条命中 (merge 口径: needs_from × answers 按 key 配对) |
| ② `state/fragments/pm.yaml` (main 的分片) | `answers[]` 里 `key == "proto_pcb_freeze_gate"` 的那条的 `value` | 同上 (★main 答 ⇒ 配对闭合★) |

★**答案正文的取值回落顺序** (逐字) ★:
`mech answers[NEED_KEY].value` → `needs_closed.answer_key` 对应的 `answers.value` → `pm.yaml 同 key 的 answers.value` → `needs_closed.evidence + .reason`

★**内容口径**: 答案正文里**逐字**含【帧 id + 板厚 + 层数】三个数 ⇒ 答案只有一句「板框已定」⇒ 一个都没有 ⇒ **判红**。

★**一条命令看全部口径**: `python3 MECH/check_board_frame_freeze_gate.py --print-c7-source` (★本机实测输出存 `logs/iss336/c7_source_proof.log`★)

---

## 4. ★阈值来源表 (★代码里没有第二份阈值表★)★

| 判据用到的集 | 值 | **出处 (全部现读)** |
|---|---|---|
| 允许板厚集 (C3) | `{0.80, 1.00}` | `board_frame_feasibility` 36 档的 `cavity_ok` **现推** (= 盖板内腔 ≥ `BASE['cavity_req']`) ⇒ **不是抄的阈值表** |
| 层数档集 (C4) | `{4, 6, 8}` | `MECH/board_frame_feasibility.py` `LAYER_TIERS` (只读 import) |
| 板厚档全集 (36 档枚举) | `{0.80, 1.00, 1.22, 1.60}` | `MECH/board_frame_feasibility.py` `THICKNESS_TIERS` (只读 import) |
| 盖板内腔判据 | `4.50 mm` | `MECH/service_port_check.py` `BASE['cavity_req']` |
| 余量判据 CRIT | `0.60 mm` | `MECH/service_port_check.py` `CRIT = 2 × TOL['fdm_part']` |
| 镜脚内腔 cav_h/cav_v/cav_l | `7.30 / 38.00 / 130.00 mm` | `MECH/service_port_check.py` `BASE` |
| 帧 id 三套 + 现役帧 | `B160x100 / F30A / P60x15` · `current_frame = B160x100` | `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` (只读) |
| 孔位口径 | PIN-SET-2 套 A (P1 8,15 / P2 52,15 / S1 8,10 / S2 52,20) | `MECH/board_frame_feasibility.py` `PIN_SET_A` |
| 零漂移对拍 | BASE / TOL / CRIT **逐项相等** | `board_frame_feasibility` 转手的值 vs `service_port_check.py` 原件 (★独立只读 import 两次★) |

★**自证 (K-5)**: 沙盒里把 `service_port_check.py` 的 `cavity_req` 4.50 改成 4.30 ⇒ 允许板厚集**当场**从 `{0.80,1.00}` 变成 `{0.80,1.00,1.22}` ⇒ **闸的读数跟着变 ⇒ 它真的在读, 不是抄的** (★见 `MECH/check_board_frame_freeze_gate_selftest.py` 的 THR-1 用例★)。

---

## 5. ★反向用例表 (★ISS-316 §2-5 的 RC-1~RC-6 逐条复现★)★

★全部跑在**沙盒副本**上 (`tmp/iss336/selftest/`), **真件一个字节不碰** (★自测脚本自己跑前后 md5 对拍, 12 件受保护文件★)★

| # | 变体 | 必须判红 | 自测实测 |
|---|---|---|---|
| **RC-1** | 只拍了帧 id, 板厚没拍 (写「板框用 60×30」, 不写板厚) | **C3** (板厚缺失) | ✅ C3 红 (★另 C6/C7 也红 = fail-closed 连锁: 板厚缺 ⇒ 组合不可定位★) |
| **RC-2** | 帧 id 与板厚都写了, 板厚写的是 **1.22** (离判红只差 0.02) | **C3 + C6** | ✅ C3 + C6 红 (理由逐字: `盖板内腔 4.48 < 4.50 (余 -0.02)`) |
| **RC-3** | 帧 id 写 `P60x15` (几何全绿, 人眼最容易上当) | **C5** (套 A 孔位不成立) | ✅ C5 + C6 红 (★ISS-316 §2-4 的 C6 判红条件逐字含「P60x15 任一档」⇒ 必然双红★) |
| **RC-4** | 帧 id 写 `B160x100` (现役帧 ⇒ 默认最容易不写出来) | **C6** | ✅ C6 红 (理由逐字: `V 链 余 -68.00 / 最坏 -68.60 < 0.60` + `L 链 余 -85.50 < 0.60`) |
| **RC-5** | 认领句写 `F30A`, 但 `cal:FRAMES.current_frame` 还停在 `B160x100` (两处各写各的, 谁都没错, 合起来错) | **C2** | ✅ C2 红 (★其余五条全绿 ⇒ 精准命中★) |
| **RC-6** | need key 闭合了, 但答案只有一句「板框已定」 (空转闭合) | **C7** | ✅ C7 红 (★另 C1/C3/C4 也红 = fail-closed 连锁: 连帧 id/板厚/层数都解析不出来★) |
| **正向对照** | 帧 = `F30A`, 板厚 = 1.00, 层数 = 6, 孔位 = 套 A | **七条全绿 ⇒ rc=0** | ✅ 全绿 |

★**另外三条自证 (本单加的)★**:
- **SRC-1 / SRC-2**: C7 真源自证 —— 一条真闭合记录 (含三个数) ⇒ **命中**; 同一位置换成「板框已定」⇒ **不命中**。
- **SRC-3**: 闭合记录落在 **main 的 `pm.yaml` answers** (merge 配对口径) ⇒ **也算闭合**。
- **THR-1**: 沙盒改 `cavity_req` ⇒ 允许板厚集跟着变 ⇒ **阈值是现读的**。

★**跑法**: `python3 MECH/check_board_frame_freeze_gate_selftest.py --selftest` ⇒ **11/11 与预期一致 ⇒ rc=0**★

---

## 6. ★「闸红了怎么办」★

| 红了哪条 | 含义 | 谁去办 |
|---|---|---|
| **C7 红** (need 没闭合) | **U-1 还没拍** ⇒ 板框三选一 (B160x100 / F30A / P60x15) 未定 | **老板拍板** (★板框是老板级★) → main 汇总 → 落一条**含帧 id + 板厚 + 层数**的闭合记录 → 闸转绿 |
| **C7 红** (闭合了但答案里没三个数) | **空转闭合** ⇒ 「板框已定」这种空话不算冻结 | 补答案正文 (★见 §7 落表格式★) |
| **C2 红** | 认领句与 `cal:FRAMES.current_frame` 不同步 (★两处各写各的★) | main 拍完 U-1 ⇒ **认领句与台账必须一起改** |
| **C3 / C4 红** | 板厚 / 层数 取值非法 (或缺失) | 结构侧复核 ⇒ 板厚只允许 `{0.80, 1.00}`, 层数只允许 `{4,6,8}` |
| **C5 红** | 该帧上套 A 四孔不成立 (★例: `P60x15` ⇒ P1 板外 1.00 · P2 板外 1.00 · S2 板外 5.70★) | 结构侧换框或改孔位口径 |
| **C6 红** | 该 (帧, 板厚, 层数) 组合在 36 档里**不能开** (★理由逐字抄 `red_reasons`★) | 结构侧复核几何 |

★**一条纪律**: **红了不许改阈值去凑绿** —— 阈值全部现读, 改阈值就是改事实, 得走口径变更流程 ★

---

## 7. ★★U-1 拍完之后, 这闸怎么变绿 (★落表格式说明·★给 main + 老板★)★★

★**必须落三处, 缺一处闸就还红**★:

| # | 落哪 | 落什么 | 判据 |
|---|---|---|---|
| ① | `state/fragments/mech.yaml` → `needs_closed[]` | 一条 `key: proto_pcb_freeze_gate` 的闭合记录 (`closed_at` / `closed_by` / `cls` / `action` / `reason` / `evidence` / `evidence_level` / `answer_key` / `answer_ref`) | **C7 的「已闭合」** |
| ② | `state/fragments/mech.yaml` → `answers[]` (或 `pm.yaml` → `answers[]`) | 一条 `key: proto_pcb_freeze_gate` 的 `value`, **正文里逐字含【帧 id + 板厚 + 层数】** | **C7 的「含三个数」** |
| ③ | `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` | `current_frame` 改成**认领的那个帧 id** (★F30A 就要改成 `F30A`★) | **C2** |

★**推荐的答案正文格式 (★照抄即可·★一行三个数, 机器逐字可读★)** ★
```
U-1 板框冻结: 帧 id = F30A; 板厚 = 1.00 mm; 层数 = 6; 孔位口径 = PIN-SET-2 套 A。
```

★**落完之后自检**: `python3 MECH/check_board_frame_freeze_gate.py` ⇒ **七条全绿 ⇒ rc=0** ★

---

## 8. ★边界 (★本闸管什么 / 不管什么★)★

| | 归属 |
|---|---|
| 「板框**冻结了没有**」 | ★**本闸** (C1~C7)★ |
| 「结构侧能不能出 Gerber」 | ★**不是本闸** ⇒ 那是 `MECH/check_onepass_mech_release.py` 的事 (★两道闸不许混★) |
| 「坐标组有没有带帧标签 / 开口压没压 SoM 座」 | ★**不是本闸** ⇒ 那是 `MECH/check_board_frame_coords.py` 的事 |
| 「板框三选一谁拍」 | ★**不是本闸** ⇒ 老板拍 (★本闸只列档 + 判红原因★) |

★**本闸零副作用**: 只读 `service_port_check.py` / `board_frame_feasibility.py` / `BOARD_FRAME_CALIBER.md` / `state/fragments/{mech,pm}.yaml` ⇒ **零写盘 / 零写板 / 零落表 / 零改既有闸** ★
