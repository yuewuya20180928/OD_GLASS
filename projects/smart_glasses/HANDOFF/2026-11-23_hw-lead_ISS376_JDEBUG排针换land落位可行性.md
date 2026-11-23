# HANDOFF · ISS-376 · `J_DEBUG` 换官方 1×4 P1.27 THT land 的落位可行性

- **单号**: ISS-376 (hw-lead) · **交卷轮次**: cont2 (cont1 于 2026-11-24 01:17:12 被掐, 本趟从已落扫描脚本续做)
- **交付人**: hw-lead (硬件总工) · **交卷时间**: 2026-11-24 03:1x (Asia/Shanghai)
- **上游**: ISS-373 (2026-11-23 23:38 交卷 / 2026-11-24 00:5x 已签收 **verified**) 的续单
- **真相页**: `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md`
- **本单闸**: `HW/check_jdebug_land_fit.py`
- **证据等级**: **L5-实测+复核** (盘上 `.kicad_mod` + 真板 `pcbnew 10.0.8` 实读 + 277,248 个候选落位穷举 + 闸逐格复算 48,598 格)

---

## B1 任务与结论摘要

**题**: ISS-373 已实测把「那一趟换 91 件」卡死在一个具体物理点上 —— 官方 1.27mm 4×THT land **放不进 `J_DEBUG` 现位** (4 个 0.65 钻孔与板面既有过孔冲突 ⇒ DRC `hole_to_hole` 由 0 变 4)。本单的任务是把「**挪哪 / 挪多大 / 挪完还剩什么**」三个问题**用机器算出来**, 交 main 裁「换不换 land」。

**本单结论 (三条, 全部本机实测)**:

1. **现位确实放不下** —— 孔净距实测重现 ISS-373 的两个数: pad1 `0.1271` (要求 ≥ `0.25`) / pad3 `0.0000` (原始 `-0.3542`, 孔心距 `0.1208` ⇒ 两孔直接叠在 via 上)。**逐位一致**。
2. **挪得下, 但至少要挪 5.7009 mm** —— 本机穷举 **3 朝向 × 92,416 个候选落位 = 277,248** 个落位 (网格 0.1 mm, X `134.0..159.5`, Y `42.0..78.0`)。**≤5.0 mm 半径内三个朝向全部 0 格可行** ⇒ 「小幅微调就能塞进去」这条路被实测否掉。最小位移落点 = **rot 90, `(150.0000, 57.9000)`, 位移 `5.7009` mm, 余量 `2.3254`**。
3. **挪完那一个过孔都不用动** —— 最小位移落点处 `n_via_viol = 0` / `n_cu_viol = 0` (四个 THT 孔与板面既有过孔/既有 THT 孔的孔净距全部 ≥ `0.25`, 铜箔不碰既有异网铜箔, courtyard 不压别的器件, 板边余量 `2.3254`)。**代价只落在 3 件**: ① 旧 4 焊盘空出 ⇒ **6 段**走线端点脱网要重接 ② 排针本体横移 `5.7009` mm (机械开口待 mech-lead 答) ③ 换不换 land (90 件 vs 91 件) 待 main 裁。

**★本单顺手挖出一条 main 任务书里没写的硬约束**: 官方 land 的四个 pad 在盘上是**沿局部 Y 一列**, 所以:
- **rot 0** (pad 沿 +Y): 铜箔包络 **X `1.0000` × Y `4.8100`**
- **rot 90 / 270** (pad 沿 ±X): 铜箔包络 **X `4.8100` × Y `1.0000`**
⇒ main 给的「铜箔 X 宽 `4.8100`」**只对 rot 90/270 成立**; 且 **rot 0 / rot 270 把沿板 X 的 JTAG pin 顺序翻转** (`JTAG_TDO → JTAG_TDI → JTAG_TMS → JTAG_TCK`), **只有 rot 90 与现位同序** ⇒ rot 90 恰好也是位移最小的那一档。

---

## B2 验收标准自评 + 数值结论 (全部带复跑命令, 见真相页 §5)

### B2.1 官方 land 盘上实读 (`.kicad_mod` 自己解析, 不写死)

| pad | 类型 | 形状 | 局部坐标 | 尺寸 | 钻孔 |
|---|---|---|---|---|---|
| 1 | thru_hole | rect | `(0.0, 0.0)` | `1.0 × 1.0` | `0.65` |
| 2 | thru_hole | circle | `(0.0, 1.27)` | `1.0 × 1.0` | `0.65` |
| 3 | thru_hole | circle | `(0.0, 2.54)` | `1.0 × 1.0` | `0.65` |
| 4 | thru_hole | circle | `(0.0, 3.81)` | `1.0 × 1.0` | `0.65` |

- `F.CrtYd` = `(-1.55, -1.14) .. (1.55, 4.95)` ⇒ `3.10 × 6.09`
- `F.Fab` = `(-1.16, -0.81) .. (1.05, 4.445)` ⇒ `2.21 × 5.255`
- 局部 Y 跨度 `3.81` · 单 pad 铜箔宽 `1.00`
- **旋转后真实 courtyard bbox (相对 pad1 原点, 由 `FOOTPRINT.SetOrientationDegrees` 在真板上实算)**:
  - rot 0: X `-1.595..1.595`, Y `-1.185..4.995`
  - rot 90: X `-1.185..4.995`, Y `-1.595..1.595`
  - rot 270: X `-4.995..1.185`, Y `-1.595..1.595`
  ⇒ ★**courtyard 不对称, 不能拿「对称的 half-width/half-height」糊弄** (本单修的第二个真 bug, 见 B5)

### B2.2 三朝向 pad 绝对坐标 (★`SetOrientationDegrees` 实算, 不手算旋转矩阵★)

| 朝向 | pad1 | pad2 | pad3 | pad4 | 轴 | 沿板 X 的 net 顺序 |
|---|---|---|---|---|---|---|
| rot 0 | `(144.3000, 58.0000)` | `(144.3000, 59.2700)` | `(144.3000, 60.5400)` | `(144.3000, 61.8100)` | +Y | JTAG_TCK → JTAG_TDI → JTAG_TDO → JTAG_TMS |
| rot 90 | `(144.3000, 58.0000)` | `(145.5700, 58.0000)` | `(146.8400, 58.0000)` | `(148.1100, 58.0000)` | +X | **JTAG_TCK → JTAG_TMS → JTAG_TDI → JTAG_TDO (与现位同序)** |
| rot 270 | `(144.3000, 58.0000)` | `(143.0300, 58.0000)` | `(141.7600, 58.0000)` | `(140.4900, 58.0000)` | -X | JTAG_TDO → JTAG_TDI → JTAG_TMS → JTAG_TCK (**翻转**) |

### B2.3 现位冲突表 (rot 90 · 孔净距要求 ≥ `0.25`)

| pad | 绝对坐标 | 钻孔 | net | 冲突对象 | 对方坐标 | 孔心距 | 孔净距 | 夹到 0 | 差 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `(144.3000, 58.0000)` | 0.65 | JTAG_TCK | via **JTAG_TDO** | `(143.7000, 57.9500)` | `0.6021` | `0.1271` | `0.1271` | `0.1229` |
| 2 | `(145.5700, 58.0000)` | 0.65 | JTAG_TMS | — | — | — | 最差 `0.9059` | — | 0 |
| 3 | `(146.8400, 58.0000)` | 0.65 | JTAG_TDI | via **XTAL_OUT** | `(146.9500, 57.9500)` | `0.1208` | **`-0.3542`** | **`0.0000`** | `0.6042` |
| 4 | `(148.1100, 58.0000)` | 0.65 | JTAG_TDO | — | — | — | 最差 `0.6861` | — | 0 |

rot 0 另有 pad2 对 via `JTAG_TDO` 孔净距 `0.1969` (差 `0.0531`) ⇒ **rot 0 也是 2 处违规**; rot 270 另有 pad2 对 via `JTAG_TDO` 孔净距 `0.1969` ⇒ 同样 2 处。⇒ **三个朝向在现位都放不下**。

### B2.4 落位可行域 (★区间, 不是一个点★)

| 朝向 | 可行格数 | X 区间 | Y 区间 | 最优点 | 余量 | 最小位移落点 | 位移 | 余量 |
|---|---|---|---|---|---|---|---|---|
| rot 0 | **23,285** | `134.0000..157.9000` | `46.0000..78.0000` | `(149.0000, 70.0000)` | `9.4550` | `(150.0000, 54.1000)` | `6.9065` | `2.0968` |
| rot 90 | **12,787** | `134.0000..154.5000` | `46.0000..78.0000` | `(148.0000, 70.0000)` | `7.0550` | **`(150.0000, 57.9000)`** | **`5.7009`** | `2.3254` |
| rot 270 | **12,526** | `134.0000..158.3000` | `46.0000..78.0000` | `(151.9000, 70.9000)` | `6.9650` | `(153.9000, 57.9000)` | `9.6005` | `2.4154` |

**离现位各半径内的可行格数**:

| 朝向 | ≤1mm | ≤2mm | ≤3mm | ≤5mm | ≤6mm | ≤7mm | ≤8mm | ≤10mm |
|---|---|---|---|---|---|---|---|---|
| rot 0 | 0 | 0 | 0 | **0** | 5 | 130 | 846 | 2,431 |
| rot 90 | 0 | 0 | 0 | **0** | 4 | 268 | 1,113 | 2,864 |
| rot 270 | 0 | 0 | 0 | **0** | 0 | 0 | 0 | 24 |

> ★**≤5.0 mm 一栏全是 0** ⇒ 这是本单最有价值的一个数。

### B2.5 板面 DRC 判据 (`.kicad_pro` 实读, 闸不写死)

`min_hole_to_hole=0.25` · `min_hole_clearance=0.25` · `min_through_hole_diameter=0.3` · `min_via_diameter=0.5` · `min_via_annular_width=0.1` · `min_track_width=0.2` · 铜箔净距判据取 `0.2` (netclass 空 ⇒ 取板默认)

---

## B3 证据分级 + 代价账 (挪完还剩什么 · 只算不拍)

| 连带项 | 量 | 依据 |
|---|---|---|
| 需挪/让开的**过孔** | **0 个** | B2.4 最小位移落点处 `n_via_viol=0` / `n_cu_viol=0` |
| 需挪/让开的**走线** | 落位侧新铜箔不碰既有异网走线 | 同上 |
| 旧 `J_DEBUG` 焊盘端点相连走线 | **6 段** (`JTAG_TDO`×4 / `JTAG_TCK`×1 / `JTAG_TMS`×1), 端点坐标 `(142.2000, 56.6000)` / `(142.7000, 56.6000)` / `(143.2000, 56.6000)` / `(143.7000, 56.6000)` ⇒ 换 land 后端点脱网, **必须重接** | 真相页 §3.1 逐条带坐标 (共 18 条) |
| 4 条 JTAG 走线脱网 | ISS-373 实测: `JTAG_TDO` 63 段被连通性重建改归 `JTAG_TCK` ⇒ 新落位后端点全部要重接 | ISS-373 S1/S2b (已签收件, 本单不重做) |
| 排针 pin 顺序 | rot 90 与现位同序; **rot 0 / rot 270 翻转** | B2.2 |
| 开口净宽 (结构侧) | rot 90 铜箔包络 X `4.8100` ⇒ 清空区 X 宽须 ≥ `4.8100`; 方向侧账 ISS-371 已判过 `CRIT 0.60` 过 ⇒ 落位横移不动这个结论 | ISS-371 已签收件 |
| **板面既有对象 (落位邻域内, 12 个过孔)** | `XTAL_OUT` `(142.2000, 53.2000)` / `(146.9500, 57.9500)` · `JTAG_TDO` `(143.7000, 57.9500)` / `(142.4500, 54.7000)` · `JTAG_TCK` `(138.7000, 54.7000)` · `JTAG_TMS` `(145.2000, 54.9500)` / `(147.2000, 54.4500)` · `XTAL_IN` `(141.2000, 58.9500)` ⇒ 全部 via 直径 `0.6000` / 钻孔 `0.3000` | 真相页 §3.1 完整 18 条清单 |

**★与 §2 可行域的关系**: **存在一个「一个都不用挪」的落点吗? —— 存在**, 但前提是**接受 5.7009 mm 的横移** (rot 90)。**代价只落在 3 件**, 不落在「拆板重做」。

---

## B4 接口取值声明 + 未决项 (★要谁回答什么 · 本单不代拍★)

| # | 要谁回答什么 | 本单给的输入 | 谁裁 |
|---|---|---|---|
| U1 | **「那一趟换不换 land (90 件 vs 91 件)」** | 落位侧代价账 = B2 + B3: 换 land ⇒ 必须横移 ≥ `5.7009` mm + 重接 6 段走线 + (若选 rot 0/270) 翻转 pin 顺序; 不换 ⇒ 维持现位 | **main** |
| U2 | **要不要挪 `XTAL_OUT` / `JTAG_TDO` 过孔** | **不需要** —— `5.7009` mm 外的可行落点处过孔一个都不碰 (`n_via_viol=0`) | main (可直接否掉) |
| U3 | **「挪落位」会不会把调试口罩开口挤掉** | 几何量: 排针本体沿 X 横移 `5.7009` mm, 落点 `(150.0000, 57.9000)`; rot 90 铜箔包络 X `4.8100` × Y `1.0000`; `F.Fab` `2.21 × 5.255`; `F.CrtYd` `3.10 × 6.09`; 清空区 X 宽须 ≥ `4.8100` | **mech-lead** |
| U4 | **rot 0 / rot 270 翻转沿板 X 的 JTAG pin 顺序 ⇒ 与 ISS-375 pin order 契约是否冲突** | B2.2 顺序表 | **sw-lead** |
| U5 | **落位横移后旧 4 焊盘位置的铜皮/走线要不要拆** | B3 清单第 13~18 条 (6 段走线, 端点坐标已给) | main + 板侧 |

**★追加式订正块 (由 main 决定要不要往既有页面落; 本单未碰任何既有页面正文)**:
- 给 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (ISS-371): 其「官方 land 装现位」的前提已被本单实测否掉 (现位放不下, `0.1271` / `0.0000`) ⇒ 建议追加「本 land 需横移 ≥ `5.7009` mm 才有落位, 见 `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md`」。
- 给 `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` (ISS-373): 其「换 91 件」的物理死结**可绕开** ⇒ 建议追加「死结可绕开: 横移 ≥ `5.7009` mm 即零过孔改动」。

---

## B5 过程说明 (★cont1 被掐 + 本趟从已落脚本续做 + 修了两个真 bug★)

1. **本单是 ISS-373 交卷后开的续单** (ISS-373 已签收 **verified**)。任务书: `state/dispatch_briefs/ISS-376_hw_jdebug_land_fit.md`; 本轮续做任务书: `state/dispatch_briefs/ISS-376_hw_jdebug_land_fit_cont2.md`。
2. **cont1 被掐**: 2026-11-24 01:13:40 派的子会话 `agent:hw-lead:subagent:ea28af80` (sessionId `1d527598`) 于 **01:17:12** 被掐死 (`sessions_list` status=timeout + `abortedLastRun=true` + `runtimeMs=410,495` ≈ 6.8 min, `promptError="This operation was aborted"`, **externalAbort=false** ⇒ 非外部 abort / 非上下文溢出)。
3. **本趟从已落扫描脚本续做** —— **没有重写扫描脚本**: 沿用 cont1 已落的 `tmp/iss376_sbx/tools/scan_land_fit.py` (起手 27,422 B @ 01:16), 只改它。
4. **★修了 cont1 留下的那个真 bug (落盘炸的)★**: cont1 的 `logs/iss376/scan_land_fit.json` 只落了半截 (1,154 B), 炸点 = `json.dump` 报 `TypeError: Object of type set is not JSON serializable` (根因 = `out["mod"]["pad_drill"]` 存的是 `set`)。修法 = 落盘前把 `set` 转 `sorted list`, 并加 `default=` 兜底。修完重跑 ⇒ JSON **完整落盘**。
5. **★本趟又挖出并修了第二个真 bug (几何的, 比第一个更要命)★**: 原扫描脚本把旋转后的 courtyard 当成**以原点对称**的矩形 (`cw=±1.55 / ch=±3.045`), 但官方 land 的 `F.CrtYd` 是**不对称**的 (局部 X `±1.55`, Y `-1.14..+4.95`) ⇒ rot 90/270 的 courtyard **既错位又错尺寸**, rot 0 的 Y 向也错位 `1.905` mm ⇒ **板边余量与 courtyard 互斥判据全部失真**。修法 = 把官方 land 装到真板上用 `FOOTPRINT.SetOrientationDegrees` + `GetCourtyard(F.CrtYd).BBox()` **实算**每个朝向的真实 courtyard 相对原点 bbox, 扫描与闸两边都改成用这个真值。修完重跑 ⇒ **rot 0 的可行域从 23,646 格变成 23,285 格, rot 90 从 19,207 变成 12,787 格, rot 270 从 7,008 变成 12,526 格** ⇒ **这个 bug 直接改写了可行域, 不是小数点问题**。
6. **★本趟还发现并堵上了「只试一个窗口就下结论」的病根★**: cont1 的扫描窗口 (X `138.0..152.0`, Y `50.0..66.0`) 把可行域**在窗口边界上截断了** (rot 0/90 的域贴着 X=152.0)。本趟把窗口扩到 X `134.0..159.5` / Y `42.0..78.0` (每朝向 92,416 候选), 并给每个连通域打 `touches_grid_edge` 标记; 域仍被窗口截断的方向 (X 下侧 / Y 上侧) **在真相页与本页都标注为「被扫描窗口截断·非真边界」**, 不当作真边界。
7. **闸 (新写, 不挂链)**: `HW/check_jdebug_land_fit.py` L0~L8 全部 fail-closed; L2 **逐格复算 48,598 格 + 边界环 2,954 格**; `--selftest` **11 条反向用例**, 其中 **2 条专打「只试一个落点就宣布可行/不可行」** (把可行区声明改成单点 / 干脆不给可行区声明 ⇒ L5 红), 每条都自证「红的是目标那一条, 其余仍绿」。
8. **status**: `state/issue_log.yaml` **未动** (不自签); 分片 `state/fragments/hw.yaml` 的 `status.phase` 保持 **`fixing`** (未落 `open` ⇒ 兄弟 job 看不见 ⇒ 撞车窗口 0)。
9. **边界自证**: 见 B6。
10. **★cont2 被 gateway reload 掐 (2026-11-24 04:10)★**: cont2 的子会话在 **04:10** 被 gateway reload 打断 (系统提示「Your previous turn was interrupted by a gateway reload」)。**打断发生在【三件交付物已全部落盘 + 分片已登记】之后**, 故本趟 (04:1x~04:2x) = **不重做扫描、不重写页、不重写闸**, 只做: ① 复跑全部必跑命令验证交付物仍绿 ② 把本趟原样输出补进 B6.7 ③ 复核分片登记 (key 唯一) ④ 复核边界零越。⇒ **本机零写板, 交付物字节级未改** (`HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` / `HW/check_jdebug_land_fit.py` 本趟一个字未动, 只有本页交卷页在 B5/B6.7 追加)。

---

## B6 验收线逐条判定 + 必跑命令输出 + 落盘清单 + 沙盒留证路径

### B6.1 验收线逐条判定

| # | 验收线 | 判定 | 依据 |
|---|---|---|---|
| 1 | 官方 land 几何 (pad 坐标/形状/钻孔/fab/courtyard) 由闸自己解析 `.kicad_mod` 复核 | ✅ PASS | L0 PASS |
| 2 | DRC 孔约束从 `.kicad_pro` 实读, 不写死 | ✅ PASS | L1 PASS |
| 3 | §2 可行域表**逐格**与闸自己实算一致 | ✅ PASS (48,598 格 + 边界环 2,954 格) | L2 PASS |
| 4 | §1 现位冲突表逐条可复算 | ✅ PASS | L3 PASS |
| 5 | 三朝向坐标由 `FOOTPRINT.SetOrientationDegrees` 实算 | ✅ PASS | L4 PASS |
| 6 | §2 给出**区间**而不是一个点 | ✅ PASS | L5 PASS |
| 7 | §3 代价清单每条带坐标 | ✅ PASS (18 条) | L6 PASS |
| 8 | 板面零写板自证 (md5/mtime/size) | ✅ PASS | L7 PASS |
| 9 | 证据等级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链 | ✅ PASS | L8 PASS |
| 10 | `--selftest` ≥8 条反向用例 (≥2 条针对「只试一个落点」) | ✅ PASS (**11 条**, 其中 2 条针对该病根) | ALL TESTS PASS |
| 11 | 交卷页 B1~B6 六段齐全 | ✅ PASS | 本页 |
| 12 | 分片 `state/fragments/hw.yaml` 登记 (3 产出物 + 3 claims + 1 need, key 唯一) | ✅ PASS (md5 `5063f493…` → `6d31bc82…`) | `state/frag_write.py --agent hw-lead` |
| 13 | 既有闸零漂移 (ISS-373 / ISS-369) | ✅ PASS (rc=0) | B6.2 命令 3/4 |
| 14 | 零挂链 (`grep -c` ⇒ `0`) | ✅ PASS | B6.2 命令 8 |

### B6.2 必跑命令 (★原样输出★)

<!-- MUSTRUN:BEGIN -->
```text
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ export TMPDIR=$PWD/tmp
### 1) 新闸
$ python3 HW/check_jdebug_land_fit.py
========================================================================
[gate] ISS-376 J_DEBUG 落位可行性闸 · L0~L8
========================================================================
  L0   PASS  官方 land 几何与盘上 .kicad_mod 实读一致 (pad 4 个 / crtyd / fab / 钻孔 / 铜箔跨度)
  L1   PASS  DRC 孔约束与 .kicad_pro 实读一致 (min_hole_to_hole=0.25 min_hole_clearance=0.25)
  L2   PASS  可行域逐格复算一致: 复算 48598 格 + 边界环 2954 格 (rot 0/90/270)
  L3   PASS  现位冲突表逐条可复算 (rot 90 · 4 pad)
  L4   PASS  三朝向 (rot 0/90/270) pad 偏移与 FOOTPRINT.SetOrientationDegrees 实算一致
  L5   PASS  §2 给出的是可行区 (每朝向声明『区间』+ >=2 格 + bbox 与逐行表一致), 不是单点
  L6   PASS  §3 代价清单 18 条全部带坐标 + why
  L7   PASS  板零写板自证通过 (md5/mtime/size 三项 == 611b869e…/2026-11-06 07:07:17.362193413/4940213)
  L8   PASS  证据等级白名单 / 零挂起措辞 / 判据句事实句分区 / 零挂链 自证通过
------------------------------------------------------------------------
[gate] 9 条判据, 红 0 条 ⇒ rc=0
GATE GREEN
rc=0

### 2) 新闸自测
$ python3 HW/check_jdebug_land_fit.py --selftest
[selftest] 基线 L0~L8 全绿
  PASS  C1 篡改 LAND pad 钻孔 ⇒ L0 红                             ⇒ 红 L0, 其余仍绿
  PASS  C2 篡改 RULES min_hole_to_hole ⇒ L1 红                  ⇒ 红 L1, 其余仍绿
  PASS  C3 篡改可行域某格余量 ⇒ L2 红                                  ⇒ 红 L2, 其余仍绿
  PASS  C4 篡改现位冲突表孔净距 ⇒ L3 红                                 ⇒ 红 L3, 其余仍绿
  PASS  C5 篡改 rot90 pad 偏移 ⇒ L4 红                            ⇒ 红 L4, 其余仍绿
  PASS  C6 ★只试一个落点★ rot90 区间声明改单点 ⇒ L5 红                     ⇒ 红 L5, 其余仍绿
  PASS  C7 ★只试一个落点★ rot0 不给区间声明 ⇒ L5 红                       ⇒ 红 L5, 其余仍绿
  PASS  C8 §3 代价条目去掉坐标 ⇒ L6 红                                ⇒ 红 L6, 其余仍绿
  PASS  C9 §3 代价条目 why 写空 ⇒ L6 红                             ⇒ 红 L6, 其余仍绿
  PASS  C10 篡改页面板指纹 ⇒ L7 红                                   ⇒ 红 L7, 其余仍绿
  PASS  C11 页面注入挂起措辞 ⇒ L8 红                                  ⇒ 红 L8, 其余仍绿
[selftest] 11/11 条反向用例通过
ALL TESTS PASS
rc=0

### 3) ISS-373 闸
$ python3 HW/check_onepass_s10_swap_set_truth.py
========================================================================
  ISS-373 · 「板那一趟」S10 换件集合唯一真源 · 机器闸
========================================================================
  集合自算: C4=158 / 靶子=78 / 靶子∩C4=77 / 缺口=13 ⇒ 90 件口径 90 件 / 91 件口径 91 件
  差集 (脚本自己算): ['J_DEBUG']
  ✅ L0
  ✅ L1
  ✅ L2
  ✅ L3
  ✅ L4
  ✅ L5
  ✅ L6
  ✅ L7
  ✅ L8
------------------------------------------------------------------------
✅ 全绿 —— 「那一趟换几件」的两套口径与差集, 页里写的数与脚本实算逐项相等
rc=0

### 4) ISS-369 闸
$ python3 HW/check_fp_libid_truth.py
【ISS-369 板面库封装名写盘闸】
  [PASS] L0 :: 基准块存在且是合法 JSON
  [PASS] L1 :: 板面 186 · C4 158 · 靶内 77 + 缺口 13 = 90 · 其余 96 (★脚本实算·页里写的与实算一致★)
  [PASS] L2 :: §1.3 逐个实测表 186 件 + §3.1 表 90 件 + §3.2 表 96 件 == 板面 186 件 (★不多不少·逐件相等★)
  [PASS] L3 :: 90 + 96 行字段全非空 (★几何 Δ / 具名脚清单 / 降级方案 / 理由 一项不许空★)
  [PASS] L4 :: 94 处 lib:name 的 .kicad_mod 全部实测在盘 + md5 一致 (★查的是封装文件, 不是只查库目录★)
  [PASS] L5 :: 94 件要写库名的件: 目标焊盘数 / fab 外框 / 中心距 == 脚本从 .kicad_mod 实测; 4 件「只写库名·零几何改动」的逐焊盘等价在容差内 (pos≤0.05 size≤0.05 cen≤0.10 fab≤0.35 mm)
  [PASS] L6 :: 90 + 96 行证据等级全 ∈ 五级白名单 (无 [官方])
  [PASS] L7 :: 正文无「等回复/等原厂回信/待供应商确认/待外部回复/等原厂/等确认」类挂起措辞
  [PASS] L8 :: 沙盒五轮 C4 全 = 158 且 S0/S1/S2/S3/S4 的 C1/C2/C3/C4 成对相同 ⇒ ★写库名这一腿对 C4 的贡献 = 0★
  事实: 板面封装=186 · C4=158 · 靶内=77 + 缺口=13 = 90 · 其余=96 · 板 md5=611b869e13518c3c023fb178f91a0075
  容差: pos≤0.05 mm · size≤0.05 mm · cen≤0.10 mm · fab≤0.35 mm
ALL CHECKS PASS
rc=0

### 5) merge
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-24T02:24:58+08:00)
   产出 807 | 阻塞 43 (高危 33) | 未闭合需求 332 | 冲突 0 | 健康度 red
rc=0

### 6) gate_check
$ python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS373_S10换件集合唯一真源与口径闸.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1127 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    444 条
   sw-lead    325 条
   mech-lead  358 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 118/501  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 236 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 43/268 | 我答 81 条(有效 31) | 产出 314 | 阻塞 7
   sw-lead    被答 29/82 | 我答 71 条(有效 6) | 产出 278 | 阻塞 15
   mech-lead  被答 46/151 | 我答 84 条(有效 21) | 产出 200 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 332 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 332)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 1/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']
   sw-lead    5/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)', 'FCCSP 球间距(pitch)']
   mech-lead  2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 205 条需求确实还没人答 (等另一个总工)
   · sw-lead: 39 条需求确实还没人答 (等另一个总工)
   · mech-lead: 88 条需求确实还没人答 (等另一个总工)

==========================================================================
rc=0

### 7) brief cmds
$ python3 state/check_brief_commands.py
── 查了 9 条待办单的 task_brief, 有问题的 0 条
rc=0

### 8) 零挂链
$ grep -c check_jdebug_land_fit state/gate_check.py
0
rc=1

### 9) 板 md5
$ md5sum HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
rc=0

### 10) 板 mtime/size
$ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213
rc=0

### 11) brief guard
$ python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-376_hw_jdebug_land_fit_cont2.md
rc=0


```
<!-- MUSTRUN:END -->

### B6.3 落盘清单

| 路径 | 类别 | 说明 |
|---|---|---|
| `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` | **新写** | 真相页 §0~§6 (含 LAND/RULES/NETMAP/ORIENT/INPLACE/FEAS/COST/BOARD/EVID 九个机器块) |
| `HW/check_jdebug_land_fit.py` | **新写** | 新闸 L0~L8 + `--selftest` 11 条反向用例 |
| `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` | **新写** | 本交卷页 B1~B6 |
| `state/fragments/hw.yaml` | **改** (仅本单自己的分片) | 3 产出物 + 3 `interface_claims` + 1 `needs_from` + `status.phase=fixing` |
| `tmp/iss376_sbx/tools/scan_land_fit.py` | **改** (本单自己的沙盒脚本) | 修 `set` 落盘 bug + 修 rotated-courtyard bug + 扩窗口 + 增量落盘 |
| `tmp/iss376_sbx/mkpage.py` | **新写** (沙盒) | 真相页生成器 (机器块由脚本从证据 JSON 生成, 不手抄) |
| `tmp/iss376_sbx/run_all.sh` | **新写** (沙盒) | B6.2 的 11 条命令复跑脚本 |
| `logs/iss376/*_v2.txt` (7 个) | **新写** (留证) | 2026-11-24 04:1x 续做复跑的原始输出 (闸 / 自测 / ISS-373 闸 / ISS-369 闸 / merge / gate_check / brief cmds) |

### B6.4 沙盒留证路径

- `logs/iss376/scan_land_fit.json` —— **全量扫描结果 + 逐格可行清单 + sha256 绑定** (真相页 `FEAS` 块绑的就是它)
- `logs/iss376/scan_land_fit.txt` —— 扫描 trace
- `logs/iss376/scan_stdout3.txt` —— **本趟最终一次**扫描 stdout (含 `[S1-1b]` 旋转后真实 courtyard bbox 行)
- `logs/iss376/scan_stdout.txt` —— cont1 那次半截运行的 stdout (留证)
- `logs/iss376/gate_run.txt` / `logs/iss376/gate_selftest_run.txt` —— 闸与自测的完整输出
- `logs/iss376/gate_check_run.txt` —— `state/gate_check.py` 完整输出 (Q1 18/18)
- `logs/iss376/must_run.txt` —— B6.2 十一条命令的完整输出
- `tmp/iss376_sbx/tools/scan_land_fit.py` —— 扫描脚本 (可复跑)
- `tmp/iss376_sbx/gate_board_dump.py` + `gate_board_dump.json` —— 闸的板面数据提取件 (只读真板)

### B6.5 边界自证

| 边界 | 自证 | 判定 |
|---|---|---|
| 零写板 | 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` —— 开工前与交卷后各打一次, 三项一致 | ✅ |
| 零落表 | `HW/netlist_v1.csv` `6aee500e60ba0732f83a9cf557ba90ab` / `HW/netlist_v1_pins.csv` `9174309df1ec9411ac8e8d9e80ee386a` / `HW/BOM_v1.csv` `5b9993992405904a60ac96a020b375d8` —— **只读**, md5 未变 | ✅ |
| 零改既有闸 | 只新写 `HW/check_jdebug_land_fit.py`; `HW/check_onepass_s10_swap_set_truth.py` / `HW/check_fp_libid_truth.py` / `HW/check_onepass_preflight_coverage.py` / `HW/check_pcb_nets.py` / `MECH/check_jdebug_1p27_clearance.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` **一字未改** | ✅ |
| 零改既有页面正文 | 只新写这一页 + 一条闸; 对既有页面的订正写成 §4.1 追加式订正块, 由 main 决定是否落 | ✅ |
| 零挂链 | `grep -c check_jdebug_land_fit state/gate_check.py` ⇒ **`0`** | ✅ |
| 只写自己的分片 | 只走 `python3 state/frag_write.py --agent hw-lead`; md5 写前 `5063f493d52fb7fb9b3fd1eb663ed36b` / 写后 `6d31bc8205d1644ded179b89fde4c278` (期间无他人改动痕迹) | ✅ |
| 沙盒 | 只落 `tmp/iss376_sbx/` + `logs/iss376/` | ✅ |
| 不代拍 | 换不换 land / 要不要挪过孔 / 开口挤不挤 / pin 顺序 ⇒ 分别登记给 main / main / mech-lead / sw-lead (§4) | ✅ |
| 零外发 | 全部数据本机实读 (`.kicad_mod` + 真板 + 本机 KiCad 10.0.8), 无外发, 无「等原厂回信」 | ✅ |
| 不自签 issue_log | `state/issue_log.yaml` **未动** | ✅ |
| 零推 GitHub | 未推 | ✅ |
| status | 分片 `status.phase` = **`fixing`** (未落 `open`) | ✅ |

### B6.6 ★与 main 给的数的差异 (★以本机复算为准★)

| 项 | main 给的 | 本机复算 | 差在哪 / 为什么 |
|---|---|---|---|
| 现位 pad1 孔净距 | `0.1271` | `0.1271` | **完全一致** |
| 现位 pad3 孔净距 | `0.0000` | `0.0000` (原始 `-0.3542`) | **一致**; 差在 main 报的是「夹到 0」的值, 本机同时给原始值 `-0.3542` 与夹 0 值 `0.0000` (孔心距 `0.1208` ⇒ 两孔直接重叠) |
| 新 land 铜箔 X 宽 | `4.8100` | rot 90/270 = `4.8100`; **rot 0 = `1.0000`** | main 的 `4.8100` = `3×1.27+1.00`, 只对应 **pad 沿 X 排**的朝向; 盘上 `.kicad_mod` 的四个 pad 是**沿局部 Y 一列**, 故 rot 0 朝向 X 包络只有 `1.0000` (Y 包络才是 `4.8100`)。**rot 0 与 rot 90 的铜箔包络互换** |
| 现位铜箔 X 宽 | `1.7750` | `1.7750` | 一致 |
| 官方 land fab | `2.21 × 5.255` | `2.21 × 5.255` | 一致 |
| 官方 land crtyd | `3.10 × 6.09` | `3.10 × 6.09` | 一致 |
| 可行域 | (未给) | rot 0 `23,285` / rot 90 `12,787` / rot 270 `12,526` 格 (网格 0.1 mm, X `134.0..159.5`, Y `42.0..78.0`) | 本单新算 |
| 最小位移 | (未给) | **rot 90 `5.7009` mm** | 本单新算 |

★**另有两处 main 任务书未提、本单挖出并已写进真相页的项**: ① **rot 0 / rot 270 翻转沿板 X 的 JTAG pin 顺序** (只有 rot 90 同序); ② 官方 land 的 `F.CrtYd` **不对称** ⇒ 旋转后必须实算 bbox, 不能按对称矩形算 (cont1 的脚本就是按对称算错的, 改写后可行域格数从 `23,646/19,207/7,008` 变成 `23,285/12,787/12,526`)。

★**cont1 收尾复核 (2026-11-24 03:2x)**: `python3 state/gate_check.py` ⇒ **RC=0** · 【Q1 交付齐备率】**18/18** (hw-lead **6/6** 缺: 无) —— 本趟只改本页 B2 / B3 / B4 三个块标题的字, 正文/小节/表格/数字未动。

### B6.7 ★本趟 (2026-11-24 04:1x~04:2x · gateway reload 后续做) 复跑输出 ★原样★

★**本趟只做验证, 不重做扫描** —— 三件交付物本趟**一个字未改** (真相页 + 闸), 只有本页追加 B5 第 10 条 + 本节。

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb   # 开工前 + 交卷后各打一次
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213

$ python3 HW/check_jdebug_land_fit.py          # ⇒ rc=0
  L0   PASS  官方 land 几何与盘上 .kicad_mod 实读一致 (pad 4 个 / crtyd / fab / 钻孔 / 铜箔跨度)
  L1   PASS  DRC 孔约束与 .kicad_pro 实读一致 (min_hole_to_hole=0.25 min_hole_clearance=0.25)
  L2   PASS  可行域逐格复算一致: 复算 48598 格 + 边界环 2954 格 (rot 0/90/270)
  L3   PASS  现位冲突表逐条可复算 (rot 90 · 4 pad)
  L4   PASS  三朝向 (rot 0/90/270) pad 偏移与 FOOTPRINT.SetOrientationDegrees 实算一致
  L5   PASS  §2 给出的是可行区 (每朝向声明『区间』+ >=2 格 + bbox 与逐行表一致), 不是单点
  L6   PASS  §3 代价清单 18 条全部带坐标 + why
  L7   PASS  板零写板自证通过 (md5/mtime/size 三项 == 611b869e…/2026-11-06 07:07:17.362193413/4940213)
  L8   PASS  证据等级白名单 / 零挂起措辞 / 判据句事实句分区 / 零挂链 自证通过
[gate] 9 条判据, 红 0 条 ⇒ rc=0
GATE GREEN

$ python3 HW/check_jdebug_land_fit.py --selftest    # ⇒ rc=0
[selftest] 基线 L0~L8 全绿
  PASS  C1 篡改 LAND pad 钻孔 ⇒ L0 红          ⇒ 红 L0, 其余仍绿
  PASS  C2 篡改 RULES min_hole_to_hole ⇒ L1 红   ⇒ 红 L1, 其余仍绿
  PASS  C3 篡改可行域某格余量 ⇒ L2 红           ⇒ 红 L2, 其余仍绿
  PASS  C4 篡改现位冲突表孔净距 ⇒ L3 红          ⇒ 红 L3, 其余仍绿
  PASS  C5 篡改 rot90 pad 偏移 ⇒ L4 红           ⇒ 红 L4, 其余仍绿
  PASS  C6 ★只试一个落点★ rot90 区间声明改单点 ⇒ L5 红   ⇒ 红 L5, 其余仍绿
  PASS  C7 ★只试一个落点★ rot0 不给区间声明 ⇒ L5 红      ⇒ 红 L5, 其余仍绿
  PASS  C8 §3 代价条目去掉坐标 ⇒ L6 红           ⇒ 红 L6, 其余仍绿
  PASS  C9 §3 代价条目 why 写空 ⇒ L6 红          ⇒ 红 L6, 其余仍绿
  PASS  C10 篡改页面板指纹 ⇒ L7 红               ⇒ 红 L7, 其余仍绿
  PASS  C11 页面注入挂起措辞 ⇒ L8 红             ⇒ 红 L8, 其余仍绿
[selftest] 11/11 条反向用例通过
ALL TESTS PASS

$ python3 HW/check_onepass_s10_swap_set_truth.py    # ⇒ rc=0 (ISS-373 零漂移)
✅ 全绿 —— 「那一趟换几件」的两套口径与差集, 页里写的数与脚本实算逐项相等

$ python3 HW/check_fp_libid_truth.py                 # ⇒ rc=0 (ISS-369 零漂移)
  事实: 板面封装=186 · C4=158 · 靶内=77 + 缺口=13 = 90 · 其余=96 · 板 md5=611b869e13518c3c023fb178f91a0075
ALL CHECKS PASS

$ python3 state/merge.py                            # ⇒ rc=0
✅ STATE.yaml 已刷新 (2026-11-24T04:20:13+08:00)
   产出 814 | 阻塞 43 (高危 33) | 未闭合需求 347 | 冲突 0 | 健康度 red

$ python3 state/gate_check.py                       # ⇒ rc=0
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q7 钉板 md5 闸链】 10/10 道绿

$ python3 state/check_brief_commands.py             # ⇒ rc=0
── 查了 7 条待办单的 task_brief, 有问题的 0 条

$ grep -c check_jdebug_land_fit state/gate_check.py
0
```

★**本趟另两条留证**: `logs/iss376/gate_run_v2.txt` / `gate_selftest_v2.txt` / `gate_check_v2.txt` / `iss373_gate_v2.txt` / `iss369_gate_v2.txt` / `merge_v2.txt` / `brief_cmds_v2.txt` —— 上述 7 段输出的原始文件。

★**分片登记复核 (本趟)** ★: `state/fragments/hw.yaml` 现状 md5 = `3865d05e845f75ec50f0034a0f682acb` (mtime 04:17)。★**该文件在 cont2 交卷 (md5 `6d31bc82…`) 之后被【同 agent 的并发续做】改过 (04:15~04:17, 落的是 ISS-369 `W-2` 口径补正一条 `interface_claim` + `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` 一处订正) ⇒ ★**本单因此【没有再跑一次 `--add-*`】**: `state/frag_write.py` 的增量语义是**纯 append 不做 key upsert**, 重跑同 key 会产生**重复 key** ⇒ 违反本单「key 要唯一」判据。⇒ 现状复核: ISS-376 的 **3 个 artifact 路径各 1 条** · **3 条 `interface_claims` (`iss376_jdebug_current_land_conflict` / `iss376_jdebug_land_fit_region` / `iss376_jdebug_optimal_landing`) 全字段唯一** · **1 条 `needs_from` (`iss376_land_swap_90_vs_91_decision` → main) key 唯一** ⇒ **登记齐备且无重复**, 无需再写, 故本趟对 `state/fragments/hw.yaml` **零写入** (不静默覆盖他人的并发写入)。

---

**交卷人**: hw-lead · **交卷状态**: 交付完成 (cont2 收尾 + 04:1x 续做验证), 等 main 裁 U1 / U2; U3 等 mech-lead; U4 等 sw-lead。
