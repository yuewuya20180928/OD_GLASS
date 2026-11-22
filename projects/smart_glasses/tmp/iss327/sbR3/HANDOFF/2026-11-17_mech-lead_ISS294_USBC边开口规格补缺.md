# ISS-294 · mech-lead 交卷单 —— `J_USB_C` 结构边开口规格补缺 (E-6 的 MECH 半边)

- **单号**: ISS-294 · **owner**: mech-lead · **verify_by**: main
- **派活**: 项目总工 main/moli · 2026-11-17 16:5x · job cron `fb67af40` (ARS45 队列自动派活)
- **性质**: ★**内部活 · MECH 侧规格补缺 + 机器闸类** ★ ⇒ **零写板 · 零落表 · 零改 `HW/`·`SW/` · 零外发 · 不自签 issue_log**
- **来由**: ★**ISS-290 §5.6 的 E-6 —— `J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做) ⇒ 本单接 E-6 的 MECH 那一半** ★
- **一句话**: ★**补第三条开口 `PORT_OPEN_USBC` (板边缺口) + 把两道闸的「恰好两条」改成【期望 id 集合 + 任意两条矩形不许完全相同】(合并禁令不但没松, 还多了一条「不许把 USB-C 并进检修口/调试口」)** ★

---

## ★B0 · 交付物清单 (4 件) ★

| # | 交付物 | 状态 |
|---|---|---|
| 1 | ★**本交卷单** `HANDOFF/2026-11-17_mech-lead_ISS294_USBC边开口规格补缺.md` ★ | ✅ |
| 2 | ★**规格页** `MECH/BOARD_ONEPASS_MECH_SYNC.md` (追加式: §5 机器块 `openings[]` 加第三条 + §2.1 逐条表加一行 + §10.1 `J_USB_C` 行 verdict + §3.1/§3.4 给 hw-lead 的输入 + 新增 §11.1~§11.7) ★ | ✅ |
| 3 | ★**两道闸** `MECH/check_onepass_mech_sync.py` (M2/M3) + `MECH/check_onepass_struct_crosscheck.py` (N3/N4) ★ | ✅ 主跑 rc=0 · `--selftest` rc=0 |
| 4 | ★**分片** `state/fragments/mech.yaml` (走 `state/frag_write.py` 原子写 ⇒ `grep` 校验通过) ★ | ✅ |

★**附产物 (可复算)**: ★**`logs/iss294/compute_iss294.py` → `logs/iss294/compute_iss294.json`** (本单几何自算) ★· ★**`logs/iss294/check_sync_projection.py`** (§5 机器块 ⇄ §2 逐条表 对账自证) ★

---

## ★§0 一条必须先说的【事实偏差】(★main 16:3x 盘面描述与实盘不一致, 我按实盘处理并写清依据★) ★

> ★**任务书 §①-2 写: 「`MECH/check_onepass_struct_crosscheck.py` L544~L548 的 `len(openings) != 2` + `sorted(ids) != [...]`」—— 实盘上这两条断言读的是【`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (ISS-290 的交卷物) 的机器块】, 不是 `MECH/BOARD_ONEPASS_MECH_SYNC.md`** ★
> ★**证据**: `MECH/check_onepass_struct_crosscheck.py` 里 `SPEC_REL = os.path.join("MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")` (★`read_spec(root)` 读它★); 该页的 `openings[]` 里有 `PORT_OPEN_DEBUG` / `PORT_OPEN_UART` 两条 + `tiers` (★h 三档★) + `must_clear[]` 两条 + `zones[]` + `s6_rows[]` + `connectors[]` —— ★**这些键在 `MECH_SYNC` 的机器块里一个都没有** ★
> ★**而任务书同时要求**: ★**「不许改 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 里 ISS-290 已登记的 `USB-C-BODY` 禁入区条目」+ 额外纪律 ⑥「`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 一个字节都不许动」** ★
> ⇒ ★**两条要求叠在一起 ⇒ 第三条开口只能登记在 `MECH_SYNC` 的机器块里, 而 N3 必须跨页读它** ★
> ★**本单的处理办法 (零漂移, 加固而不是绕过)**:
> ① ★**N3 的期望 id 集合 = {PORT_OPEN_DEBUG, PORT_OPEN_UART, PORT_OPEN_USBC}, 跨两页拼**: ISS-290 页的两条 (★原样, 那页一个字节没动★) + `MECH_SYNC` 页的第三条 ★
> ② ★**合并禁令改成【任意两条开口的矩形不许完全相同】(跨页一起比)** ⇒ 合并成一条 / 把 USB-C 并进另两条 ⇒ 照样红 ★
> ③ ★**新增 N3b: 两页的老开口必须逐字一致** (★同一份规格不许分叉★) + ★**N3b2: 机器块内部 `rect` 与 `tiers["2.54"].open_rect` 不许分叉** ★
> ④ ★**N4 的必清空区 2 ⇒ 3 条**: ISS-290 页的两条 (原样) + `MC_USBC` (从 `MECH_SYNC` 页读) ★
> ⇒ ★**结果: N3/N4 查到的开口从 2 条变成 3 条, 而且三条分别逐档验 (输出里可见「第三条逐档核 60 次」), N3 判据只变严, 没变松** ★

---

## ★B1 · 规格页补第三条开口 (★`MECH/BOARD_ONEPASS_MECH_SYNC.md`★) ★

### ★B1-1 · 板读事实 (★本单自算: `logs/iss294/compute_iss294.py` → `.json`★) ★

| 项 (帧: `B160x100`) | 值 | 证据级 |
|---|---|---|
| ★**`J_USB_C` 位置 / 封装** ★ | (140.000, 5.250), rot 0, `GCT USB4105-16P` (自绘, 原厂图纸 Rev B3) | ★`[实测]` 板读 |
| ★**座体 `F.Fab`** ★ | X 135.680..144.320 × Y 0.000..6.400 (8.640 × 6.400) ⇒ ★**Y 下沿 = 0.000 = 板边** ★ | ★`[实测]` 板读 |
| ★**座体 `F.CrtYd`** ★ | X 135.180..144.820 × Y **−0.500**..6.900 (9.640 × 7.400) ⇒ ★**座体自己的 courtyard 就越过板边 0.500** ★ | ★`[实测]` 板读 |
| ★**两个壳体固定孔 (NPTH)** ★ | (134.220, 2.625) 与 (145.780, 2.625); pad Ø0.650, ★**drill Ø0.762** ★ ⇒ 物理孔外缘 X 133.839..146.161 | ★`[实测]` 板读 |
| ★**16 个信号焊盘** ★ | 单排 pitch 0.50, 焊盘 0.30 × 1.15, Y 中心 5.250 ⇒ 铜箔 Y 4.675..5.825; 焊盘行中心跨度 7.50 | ★`[实测]` + ★`[官网 转引]` (GCT USB4105 Rev B3: 焊料尾总长 8.34±0.06 与 7.50+2×0.42 互证) |
| ★**必须清空区 (座体 ∪ 固定孔)** ★ | X 133.895..146.105 × Y 0.000..6.400 (12.210 × 6.400) | ★`[实测]` + `[推算]` |
| ★**结构净距余量** ★ | `CRIT` 0.60 + `TOL.fdm_part` 0.30 = **0.900 / 边** (沿用既有判据常量, 零新造) | ★`[实测]` 阈值来源 `MECH/check_board_frame_coords.py` |
| ★**边开口 (板边缺口)** ★ | ★**X 132.995..147.005 × Y 0.000..7.300 (宽 14.010, 深 7.300)** ★ | ★`[推算]` |
| ★**单边净距** ★ | X 0.900 / Y 0.900 ⇒ ★**最坏 0.600 = CRIT (刚好过)** ★; 到 drill 外缘 (133.839) 的净距 **0.844** ≥ CRIT ✓ | ★`[推算]` |
| ★**周边无冲突** ★ | 该开口矩形内除 `J_USB_C` 外★**无别的封装** (186 封装逐个查) | ★`[实测]` 板读 |
| ★**S6 的 20 个目标落位** ★ | 压该开口 **0** 条; 最小净距 **8.795** (`R_SEL_D3_P`) | ★`[实测]` |

### ★B1-2 · 为什么「边开口」跟另两条不是同一种开口 (★本单最关键的一条语义★) ★

| 项 (帧: `B160x100`) | ★**另两条 (检修口 / 调试口)** ★ | ★**第三条 (USB-C 边开口)** ★ |
|---|---|---|
| 几何类别 | ★**罩住一个器件的【洞】** ★ —— 四边都在板内 | ★**板【边界】上的【缺口】** ★ —— ★**另一侧是板外** ★ |
| 插头从哪进 | 从板内某个方向 (器件上方 / 侧方) | ★**从板外沿板面插进板边** ★ (USB 是 demo 板【唯一的供电 + 数据入口】) |
| 开口 Y 的取法 | ★**居中于器件中心**: Y = [cy − OPEN_Y_eff/2, cy + OPEN_Y_eff/2] ★ | ★**不居中**: 下沿【锚在板边线 Y = 0.000】, 深度 = 座体平面尺寸 + 净距 ⇒ ★**板面矩形不随 h 变**; 随 h 变的是【Z 向窗口】★ |
| 为什么不能照抄另两条 | —— | ★**① 另两条的开口宽 `OPEN_X` = 10.20 是「罩排针」的定档宽; USB-C 两个壳体固定孔在 X 134.220 / 145.780 (外缘 133.895..146.105) ⇒ 开口至少 12.210 宽 ⇒ 10.20 装不下 ⇒ `open_x_spec` 对本条【不适用】** ★ ★**② 另两条的 Y 居中公式对「下沿 = 板边」的缺口【物理上不成立】(缺口没有中心)** ★ |
| 判据怎么写 | ★**M3 逐档: 居中矩形 + 单调 + 落框 + 不压 SoM + 最坏净距 ≥ CRIT** ★ | ★**M3 逐档 (边开口分支): 下沿必须锚在板边线 + X 必须 = (座体 `F.Fab` ∪ 两个固定孔外缘) ± (CRIT+TOL) + Y 深度 = max(座体 Y 深度, `OPEN_Y_eff(h)`) + (CRIT+TOL)** ★ |

### ★B1-3 · h 三档 (★座体真实高 h 仍是 `[0数据]` ⇒ 不许把 2.54 当事实★) ★

| h 档 (帧: `B160x100`) | `OPEN_Y_eff(h)` | 边开口板面矩形 | 说明 |
|---|---|---|---|
| 0.90 | 4.60 | X 132.995..147.005 × Y 0.000..7.300 | 缺口深度由座体平面尺寸 6.400 支配 ⇒ 7.300 |
| 2.54 | 4.60 | X 132.995..147.005 × Y 0.000..7.300 | ★**2.54 是现行假设, 不是事实** ★ |
| 4.00 | 5.80 | X 132.995..147.005 × Y 0.000..7.300 | 深度仍由 6.400 支配 ⇒ 7.300 |

★**⇒ 三档板面矩形同值, 这不是偷懒, 是物理结论**: ★**缺口在板面内的深度由座体的【平面尺寸】(Y 深 6.400) 支配, 不由座体【高度】h 支配 ⇒ 随 h 变的是【Z 向窗口】(结构件在插头进出方向留的净空高) = `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80** ★
★**座体高参照**: ★**BOM `HW/BOM_v1.csv:76` (`J_TYPE_C` 同族) 记「主体高 3.50 mm」[实测]; `J_USB_C` 自身的座体高仍是 `[0数据]` (GCT USB4105 图纸文本里同时出现 3.31 与 3.50 两个高度数, 未看图不能判定哪个是座高) ⇒ 若按 3.50 取, `OPEN_Y_eff(3.50)` = 5.30 ⇒ 三档的 4.00 档 (5.80) 已覆盖 ✓** ★

### ★B1-4 · 立柱 / 螺钉头外扩三档 (★固定方式未定 ⇒ 缺口 X 还可能更宽★) ★

| 螺钉头 / 立柱外径 D (帧: `B160x100`) | 每侧外扩 (D − 0.65)/2 | 边开口 X | 边开口宽 | 依据 |
|---|---|---|---|---|
| 2.60 | 0.975 | 132.020..147.980 | 15.960 | ★`[官网 转引]` GCT USB4105 Rev B3 图纸壳体柱尺寸「2x 2.60」★ (★柱宽与孔径哪一项是横向宽需看图 ⇒ 保守取用★) |
| 3.00 | 1.175 | 131.820..148.180 | 16.360 | ★`[推算]` M2 立柱外径常见值 (★`[0数据]`: 未选型★) |
| 3.80 | 1.575 | 131.420..148.580 | 17.160 | ★`[推算]` M2 螺钉头外径常见值 (★`[0数据]`: 未选型★) |

★**⇒ 代价**: ★**缺口每侧多让 1 mm, 结构件在这条边上少一条 14 × 2 mm 的承力带** ⇒ **结构件强度/刚度的取舍, 归 main→老板** ★

### ★B1-5 · 机器块第三条 (★字段照 `PORT_OPEN_DEBUG` 的 15 个字段一条不缺★) ★

★**`openings[]` 第三条 (逐字)**: ★
```json
{
  "id": "PORT_OPEN_USBC",
  "role": "USB-C 边开口",
  "covers": "J_USB_C",
  "frame": "B160x100",
  "body_w": 8.640,
  "body_w_source": "板读 (J_USB_C 座体 F.Fab X 135.680..144.320 ⇒ 宽 8.640; 两个壳体固定孔 @ X 134.220 / 145.780 ⇒ 外缘 133.895..146.105)",
  "rect": {"x0": 132.995, "x1": 147.005, "y0": 0.000, "y1": 7.300},
  "x0_range": [132.995, 133.895],
  "y0_range_at_h_ref": [0.000, 0.000],
  "cl_x": 0.900, "cl_y": 0.900, "worst_cl_x": 0.600, "worst_cl_y": 0.600,
  "som_hits": 0,
  "evidence": "[实测](板读 F.Fab / F.CrtYd / 焊盘 / NPTH drill)+[推算](净距与开口宽)+[0数据](座体真实高 h)",
  "tiers": { "0.90": {...}, "2.54": {...}, "4.00": {...} }
}
```
★**字段口径说明 (逐条, 防「自创字段名」质疑)**: ★
- ★**15 个标准字段一个不缺、一个名字不改** (照 `PORT_OPEN_DEBUG` 逐字) ★
- ★**`tiers` 是【既有字段名】不是自创** —— ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 的两条开口早就在用 `tiers` (h 三档 + `open_rect` + `must_clear` + `clearance_*` + `pass_crit`) ★ ⇒ 本单沿用同一套 schema, 好处是 N3 的「逐档分别验」循环不用改就能把第三条验进去** ★
- ★**`x0_range` = [132.995, 133.895]**: 语义 = 【开口左边界 → 必须清空区左边界】的区间 (另两条是「开口左边界 → 铜箔左边界」, 同口径: 开口边到最左必清实体) ★
- ★**`y0_range_at_h_ref` = [0.000, 0.000]**: ★**这正是边开口与另两条的本质差别** —— 另两条的 Y 下沿离实体还有 1.150 余量, ★**边开口的下沿 = 必须清空区下沿 = 板边线 0.000 ⇒ 零余量 (板边就是开口边) ★ ★**【另两条是洞, 边开口是缺口】★

### ★B1-6 · §5 机器块 ⇄ §2 逐条表 【两处逐字对得上】的自证 ★

★**自证方式**: ★**`python3 logs/iss294/check_sync_projection.py`** (★只读规格页: ① `openings[]` 第三条的 15 个字段齐全且非空 + `tiers` 三档 + `rect` 与 `tiers["2.54"].open_rect` 自洽 ② `items[]` 的 `MECH-PORT-USBC` 8 字段齐全 ③ §2 逐条表那一行格数 = 8 + 第 1 格是 id、第 2 格是 source_iss ④ 12 个关键几何数在 §2 表 / `items[]` / `openings[]` 三处【按数值】一致★) ★

```
★【ISS-294 · §5 机器块 ⇄ §2 逐条表 对账】★
  openings[] 条数 = 3 → ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USBC']
  PORT_OPEN_USBC 缺字段 = 无 · 空字段 = 无
  tiers = ['0.90', '2.54', '4.00'] (h 三档)
  rect {'x0': 132.995, 'x1': 147.005, 'y0': 0.0, 'y1': 7.3} vs tiers['2.54'].open_rect {'x0': 132.995, 'y0': 0.0, 'x1': 147.005, 'y1': 7.3} ⇒ 一致
  must_clear (h_ref 档) = {'x0': 133.895, 'y0': 0.0, 'x1': 146.105, 'y1': 6.4}
  items[MECH-PORT-USBC] 缺字段 = 无 · 空字段 = 无
  §2 表行格数 = 8 (★要求 8★)
  §2 表第 1 格 = ★`MECH-PORT-USBC` ★ · 第 2 格 = ISS-294
  关键几何数 12 个在 §2 表 / items[] / openings[] 三处一致 ⇒ 一致

结论: ✅ 两处逐字对得上
rc=0
```

---

## ★B2 · 两道闸改成【集合 + 两两不相同】(★★合并禁令不许松★) ★

### ★B2-1 · 改了什么 (逐条, 附新判据原文) ★

| 位置 | 改前 | 改后 |
|---|---|---|
| ★**`MECH/check_onepass_mech_sync.py` M2** ★ | ★**`if len(openings) != 2: errs.append("M2 开口必须【两条】(检修口 / 调试口) ...")`** ★ | ★**期望 id 集合断言**: `if sorted(ids) != sorted(EXPECTED_OPENING_IDS)` ⇒ 期望 = `{PORT_OPEN_DEBUG, PORT_OPEN_UART, PORT_OPEN_USBC}` (★恰好三条, 一条不少一条不多★) + ★**id 重复即红** (合并成一条 ⇒ 重复) ★ |
| ★**M2b** ★ | ★**`if len(rows) == 2:` 只比那两条** ★ | ★**改成两两循环**: 任意两条开口的矩形不许完全相同 ⇒ ★**合并成一条 / 把 USB-C 并进检修口·调试口 ⇒ 照样红** ★ |
| ★**M2c** ★ | ★**`conns` 从【全部 openings】算 ⇒ `if len(conns) == 2:` 才复算** ★ | ★**`conns` 改成只取 `merged_opening.covers` 点名的那些座体** ⇒ ★**★不然多一条开口 (USB-C) 就会把「恰好两条」的判据悄悄跳过 ⇒ 合并禁令的复算反而失效 (防线变松) ★★** ⇒ 现在 `len(refs) < 2` 或读不到座体 ⇒ 直接红 (fail closed) ★ |
| ★**M3** ★ | 只有【罩器件的洞】那一种规则 | ★**加【边开口分支】**: ① 下沿必须锚在板边线 ② X 必须 = (座体 `F.Fab` ∪ 两个壳体固定孔外缘) ± (CRIT+TOL) ③ Y 深度 = max(座体 Y 深度, `OPEN_Y_eff(h)`) + (CRIT+TOL) ④ 逐档: 物理合理性 (0 < h ≤ 座体盒高 6.400) + 单调 + 落框 + 不压 SoM + 最坏单边净距 (X 向与 Y 向) ≥ CRIT ⑤ 声明矩形必须覆盖该档算出来的矩形 ⑥ 声明矩形 == h_ref 档算出来的矩形 ★**另两条走的还是老规则, 一行没改** ★ |
| ★**`MECH/check_onepass_struct_crosscheck.py` N3** ★ | ★**`if len(openings) != 2:` + `if sorted(ids) != ["PORT_OPEN_DEBUG", "PORT_OPEN_UART"]:`** ★ | ★**跨页拼三条 (ISS-290 页两条 + MECH_SYNC 页第三条) ⇒ 期望 id 集合断言 = 三条 + id 重复即红 + 任意两条矩形不许完全相同 (跨页一起比) + 三条逐档分别验 + 新增 N3b (两页老开口逐字一致) + N3b2 (机器块内部 `rect` 与 `tiers["2.54"].open_rect` 不许分叉)** ★ |
| ★**N4** ★ | 必清空区恰好 2 条 | ★**必清空区 2 ⇒ 3 条** (ISS-290 页 2 条原样 + `MC_USBC` = 座体 ∪ 两个固定孔外缘, 从 MECH_SYNC 页读) ⇒ 20 个 S6 目标位到它净距 ≥ CRIT ★ |

★**★★一条不许破的纪律 (追加式) ★★**: ★**另两条开口 (`PORT_OPEN_DEBUG` / `PORT_OPEN_UART`) / `merged_opening` 块 / `consts` 里任何一个数 / 老 `items[]` —— 一个字没改** ★ (★只加第三条 + 只加闸的判据★)

### ★B2-2 · 反向用例 (★全部在沙盒副本上做, 真件一个字节不许碰★) ★

★**做法**: 照 `MECH/check_onepass_struct_crosscheck.py --selftest` 现成的沙盒机制 (`make_sandbox` + `_edit_spec_json`; ★本单另加 `_edit_spec2_json` 改 `MECH_SYNC` 页★) ★

#### ★M2 闸 (`MECH/check_onepass_mech_sync.py --selftest`) ★

```
  [基线] M1=OK M2=OK M3=OK M4=OK M5=OK
  [OK ] ① 改检修口矩形一个角 (y0 66.300 ⇒ 52.000) ⇒ M2 红: 是 · md5 f30531bd ⇒ 576a44cc (确实改了: True) · M2 命中=[('PORT_OPEN_DEBUG', 0), ('PORT_OPEN_UART', 23), ('PORT_OPEN_USBC', 0)]
  [OK ] ② 把两条开口合并成一个 ⇒ M2/M3 红: 是 · md5 f30531bd ⇒ 57fe8d1d (确实改了: True) · M2 错误 4 条 / M3 错误 1 条
  [OK ] ③ 抽掉正文表头的帧标签 ⇒ M1 红: 是 · 命中模式: True · md5 f30531bd ⇒ e114de79 (确实改了: True) · M1 错误 5 条
  [OK ] ④ 抽掉机器块里的 frame 字段 ⇒ M1 红: 是 · md5 f30531bd ⇒ 77e1c86c (确实改了: True) · M1 错误 1 条
  [OK ] ⑤ 把 h 三档之一改到不合理 (4.00 ⇒ 40.00) ⇒ M3 红: 是 · md5 f30531bd ⇒ a55685db (确实改了: True) · M3 错误 5 条
  [OK ] ⑥ 把判据命令改成不存在的脚本 ⇒ M4 红: 是 · md5 f30531bd ⇒ 124f9b3a (确实改了: True) · M4 错误 13 条
  [OK ] ⑦ 改受保护件 (HW/PCB/demo_mainboard.kicad_pcb) ⇒ M5 红: 是 · md5 611b869e ⇒ 9ca97cf9 (确实改了: True) · M5 错误 1 条
  [OK ] ⑨ 把机器块里的 PORT_OPEN_USBC 删掉 ⇒ M2 红: 是 · 命中集合断言: 是 · md5 f30531bd ⇒ e71761b7 (确实改了: True) · M2 错误 1 条
  [OK ] ⑩ 把 PORT_OPEN_USBC 改名成 PORT_OPEN_USB_C ⇒ M2 红: 是 · 命中集合断言: 是 · md5 f30531bd ⇒ 71129e91 (确实改了: True) · M2 错误 1 条
  [OK ] ⑪ 把边开口的矩形改成跟调试口完全一样 ⇒ M2b 红 (合并禁令): 是 · 命中合并禁令: 是 · md5 f30531bd ⇒ 4ec488ee (确实改了: True) · M2 错误 1 条
  [OK ] ⑫ 正向对照 (三条齐全且互不相同) ⇒ 绿: 是 · 开口集合 ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USBC']
  [OK ] ⑧ 自检跑完, 真件 5 件 md5 仍逐字节不变: 是 · demo_mainboard.kicad_pcb=611b869e · demo_mainboard.kicad_pro=3e504d2b
【自检结论】✅ 全抓到
rc=0
```

★**任务书要求的 4 条一一对应**: ★**① 删掉 `PORT_OPEN_USBC` ⇒ 红 = 第 ⑨ 条 ② 改 id 成 `PORT_OPEN_USB_C` ⇒ 红 = 第 ⑩ 条 ③ 矩形改成跟 `PORT_OPEN_DEBUG` 完全一样 ⇒ 红 = 第 ⑪ 条 (★命中合并禁令 M2b★) ④ 正向对照三条齐全且互不相同 ⇒ rc=0 = 第 ⑫ 条** ★

#### ★N3 闸 (`MECH/check_onepass_struct_crosscheck.py --selftest`) ★

```
  [基线] N1=OK N2=OK N3=OK N4=OK N5=OK N6=OK
  [OK ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 是 · md5 cb5c2439 ⇒ c488944c (确实改了: True) · N2 错误 2 条
  [OK ] ② 把 S6 目标位 R_SEL_D1_N 挪进调试口开口 ⇒ N3 红: 是 · md5 cb5c2439 ⇒ 08cee563 (确实改了: True) · N3 错误 3 条
  [OK ] ③ 抽掉 §3 表里 TP_DSI_CK_P 的帧标签 ⇒ N1 红: 是 · 命中: True · md5 bd66ee4d ⇒ 54ddb0bd (确实改了: True) · N1 错误 1 条
  [OK ] ④ 把两条开口合并成一条 ⇒ N3 红: 是 · md5 bd66ee4d ⇒ 95201109 (确实改了: True) · 开口条数 4 · N3 错误 6 条
  [OK ] ⑤ 把规格页 CRIT 改小 (0.60 ⇒ 0.10) ⇒ N4 红: 是 · md5 bd66ee4d ⇒ f6812123 (确实改了: True) · N4 错误 1 条
  [OK ] ⑤b 把规格页 CRIT 改大 (0.60 ⇒ 60.00) ⇒ N4 红 (净距不足): 是 · md5 bd66ee4d ⇒ bb91d2f6 (确实改了: True) · N4 错误 1 条
  [OK ] ⑥ 清空 §4 里 J_DEBUG 行的【结构占位要求】⇒ N5 红: 是 · md5 bd66ee4d ⇒ 7db8143c (确实改了: True) · N5 错误 1 条
  [OK ] ⑦ 篡改受保护板文件 ⇒ N6 红: 是 · md5 611b869e ⇒ 590f9d52 (确实改了: True) · N6 错误 1 条
  [OK ] ⑨ 把边开口规格页里的 PORT_OPEN_USBC 删掉 ⇒ N3 红: 是 · md5 f30531bd ⇒ f45d471c (确实改了: True) · 开口集合 ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART'] · N3 错误 1 条
  [OK ] ⑩ 把 PORT_OPEN_USBC 改名成 PORT_OPEN_USB_C ⇒ N3 红: 是 · md5 f30531bd ⇒ 504230e4 (确实改了: True) · 开口集合 ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USB_C'] · N3 错误 1 条
  [OK ] ⑪ 把边开口的矩形改成跟调试口完全一样 ⇒ N3 红 (合并禁令): 是 · 命中合并禁令: 是 · md5 f30531bd ⇒ c2dabbd1 (确实改了: True) · N3 错误 1 条
  [OK ] ⑫ 正向对照 (三条齐全且互不相同) ⇒ 绿: 是 · 开口集合 ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USBC'] · 第三条逐档核 60 次
  [收尾] 真件 N6 = OK (自检跑完真件 md5 仍逐字节不变)
【自检结果】0 条问题
rc=0
```

### ★B2-3 · ★**「第三条被验到」的直接证据** (★不许只看「三条都在 ids 里」就交卷★) ★

★**M2 闸 (M3 逐档输出)**:
```
  M2 三条开口不压 SoM  ✅ 绿  (期望 id 集合 ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USBC'])
      · PORT_OPEN_USBC     USB-C 边开口 罩 J_USB_C                rect=(132.995, 147.005, 0.0, 7.3) ⇒ 压 SoM 焊盘 0
  M3 座体高度参数式 . ✅ 绿  (公式 OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h + 1.80))
      · PORT_OPEN_USBC     h=0.90  eff=4.60  rect=(132.995, 147.005, 0.0, 7.3) 落框=True 压SoM=0 最坏间隙Y=0.600
      · PORT_OPEN_USBC     h=2.54  eff=4.60  rect=(132.995, 147.005, 0.0, 7.3) 落框=True 压SoM=0 最坏间隙Y=0.600
      · PORT_OPEN_USBC     h=4.00  eff=5.80  rect=(132.995, 147.005, 0.0, 7.3) 落框=True 压SoM=0 最坏间隙Y=0.600
```
★**N3 闸 (逐档核了几次, 写在输出里)**:
```
  N3 三条开口 (分别验) ... ✅ 绿  (开口 3 条: ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART', 'PORT_OPEN_USBC'])
      · PORT_OPEN_DEBUG    h 三档 ['0.90', '2.54', '4.00'] ⇒ 目标位逐档核 60 次
      · PORT_OPEN_UART     h 三档 ['0.90', '2.54', '4.00'] ⇒ 目标位逐档核 60 次
      · PORT_OPEN_USBC     h 三档 ['0.90', '2.54', '4.00'] ⇒ 目标位逐档核 60 次
```
★**⇒ 第三条确实进了逐档循环 (3 档 × 20 个目标位 = 60 次), 不是挂在 ids 里好看的** ★

---

## ★B3 · 回归 (★别的闸一条不许红★) ★

```
=== 1) check_onepass_mech_sync.py ===            rc=0
=== 2) check_onepass_struct_crosscheck.py ===     rc=0
=== 3) check_demo_struct_truth.py ===             rc=0
=== 4) check_board_frame_coords.py ===            rc=0
=== 5) state/merge.py ===                         rc=0
      ✅ STATE.yaml 已刷新 (2026-11-17T17:29:33+08:00)
         产出 516 | 阻塞 43 (高危 33) | 未闭合需求 297 | 冲突 0 | 健康度 red
=== 6) state/gate_check.py ===                    rc=0
      【Q1 交付齐备率】 18/18 个必填验收块齐全
      【Q2 证据分级率】 3/3 个总工的交付做了证据分级
=== 7) state/issue_check.py ===                   rc=0
      ✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)
```
★**两道闸的自检**: ★**`check_onepass_mech_sync.py --selftest` ⇒ rc=0 (12 条反向用例全抓到)** ★ · ★**`check_onepass_struct_crosscheck.py --selftest` ⇒ rc=0 (12 条反向用例全抓到)** ★

### ★B3-1 · 零写板 / 零落表 自证 (★md5 + mtime 双重★) ★

```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb     ★基线一致
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro     ★基线一致
37f62ac3f0b81d92ca7d48fdea717f07  HW/netlist_v1.csv                   ★基线一致
a4270120454aedf7a23c92cd8985c8a6  HW/netlist_v1_pins.csv              ★基线一致
5d02bece9477ffce5fbe0193c7d5cce4  HW/BOM_v1.csv                       ★基线一致
板 mtime = 2026-11-06 07:07:17.362193413 +0800                          ★未变
```
★**★一个必须写清的副作用 (★ISS-289 交卷单自己发现的那个坑, 本单也踩到了并如实报★)**: ★**跑 `MECH/check_demo_struct_truth.py` (★它 subprocess 调 `MECH/hw_cross_review_check.py` → `HW/check_pcb_generator_defaults.py★) 会重新生成 `HW/PCB/` 下 4 个辅助文件 (`_frame_reference.kicad_pcb` / `STACKUP.md` / `GEN_SELF_CHECK.txt` / `LAYOUT_RULES.md`, 本单跑到时 mtime = 2026-11-17 17:26:59)** ★ ⇒ ★**判「有没有偷改板」必须看【官方板那两个文件的 md5 + mtime】, 不能看目录 —— 上面那两个官方文件逐字节未变** ★

---

## ★§4 · 归 main → 老板拍的 (★本单只交几何 + 代价 + 建议, 不代拍★) ★

| # (帧: `B160x100`) | 事实 | 代价 A (按本单登记值) | 代价 B (按 §B1-4 外扩) | 谁拍 |
|---|---|---|---|---|
| 1 | ★**缺口 X 最小合法值 = 132.995..147.005 (宽 14.010), 最坏单边净距 0.600 = CRIT 刚好过** ★ | 缺口窄 ⇒ 承力带多 | ★**每侧多让 0.975..1.575 ⇒ 这条边少 14 × 2 mm 的带** ★ | ★**main → 老板** ★ |
| 2 | ★**缺口 Y 向深度 7.300 是按【结构件内壁与板边齐平】的最坏假设算的; 内壁外移 t ⇒ 深度可缩到 t** ★ | 深度 7.300 (保守) | 深度缩到 ~2.000 ⇒ 内腔让出 5 mm | ★**main → 老板** (结构方案) ★ |
| 3 | ★**Z 向窗口 (插头过孔净空高) = `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80, 不在板面坐标里 ⇒ 本页只能登记不能验** ★ | 板面矩形照 §B1-3 | Z 向窗口跟结构件外形一起定 | ★**main → 老板** ★ |
| 4 | ★**给 hw-lead 的第三条开口输入已在 §3.1 / §3.4 写好 (零改板 ⇒ 不占「板只改一次」那一趟), 但必须在结构件开模前定** ★ | — | — | ★**main** ★ |

★**分片已登记 (★`state/fragments/mech.yaml`, 走 `state/frag_write.py` 原子写 + `grep` 校验★)**: ★**`iss294_usbc_edge_opening_size_and_z_window` (to: main)** ★ + ★**`iss294_iss290_page_verdict_divergence` (to: main)** ★

---

## ★§5 · 顺带发现的三件事 (★不越界, 只登记, 本单一个字节不许动★) ★

| # | 发现 | 依据 | 本单的处理 |
|---|---|---|---|
| 1 | ★**口径分叉**: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 的 `J_USB_C` 行 verdict 仍写「可装 / 结构侧缺一条边开口规格」 —— ★**那是 ISS-290 的交卷物, 本单一个字节不许动** ★ ⇒ 本单已把 `MECH_SYNC` §10.1 那行改成「可装 / 边开口规格已补 (X 132.995..147.005 @ 板边 Y=0 · h 三档 · 固定孔清空区 X 133.895..146.105)」 | ★`[实测]` 两页逐字读 | ★**登记 need 给 main** (要不要让 ISS-290 那行补一句「已由 ISS-294 补」) ★ |
| 2 | ★**既有回归 (与本单无关, 但它挡了 `--selftest` rc=0)**: `MECH/check_onepass_mech_sync.py --selftest` 第 ⑦ 条反向用例篡改 `HW/BOM_v1.csv`, ★**但 ISS-286 把 `CFC.PROTECTED` 改成「板 + `.kicad_pro`」两件 (网表/脚表/BOM 归台账管) ⇒ 沙盒里根本没有那个文件 ⇒ 自检直接崩 `FileNotFoundError`** ★ ⇒ ★**这条反向用例从未真正跑过** ★ | ★`[实测]` 沙盒拷贝清单 `rels = [SPEC_REL] + list(CFC.PROTECTED.keys())` | ★**改成篡改 M5 真正查的板文件** (★与 `check_onepass_struct_crosscheck.py` 第 ⑦ 条同做法★) ⇒ ★**语义与目的不变 (改受保护件 ⇒ M5 必须红), 而且这条用例现在真的能跑** ★ |
| 3 | ★**`J_USB_C` 的 NPTH 实际 drill = Ø0.762, 而 pad `size` = Ø0.650** (★pad 比 drill 小 ⇒ 没有环形铜, 物理孔就是 Ø0.762★) ⇒ 本单的必须清空区按 pad 口径算 (133.895..146.105), drill 口径的外缘是 133.839..146.161, ★**差 0.056 / 边, 已含在 0.900 的净距里 (到 drill 外缘的实际净距 0.844 ≥ CRIT 0.60 ✓)** ★ | ★`[实测]` 板读 (`size 0.65 0.65` + `drill 0.762`) | ★**登记在 §B1-1 的表里; 不改板 (板上是 ISS-292 的地盘)** ★ |

---

## ★§6 · 边界自证 (★违反就是不合格★) ★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | 板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` 双重不变 (§B3-1) ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三件 md5 与基线逐字节相同 (§B3-1) ★ |
| ★**零改 `HW/` 与 `SW/`** ★ | ★**本单只读了板/网表/BOM; 没写过 `HW/` 与 `SW/` 任何文件** ★ (`HW/PCB/` 下 4 个辅助文件的 mtime 变动是 `MECH/check_demo_struct_truth.py` 的既有副作用, 见 §B3-1 的说明) ★ |
| ★**零改 ISS-290 的交卷物** ★ | ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 一个字节没动** (含 `USB-C-BODY` 禁入区条目) ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_board_frame_coords.py` / `MECH/check_demo_struct_truth.py` / `MECH/board_port_opening_s6_check.py` 一个字节没动** ⇒ 阈值 (CRIT 0.60 / TOL 0.30 / OPEN_X 10.20 / EDGE_KEEPOUT 0.80) 零漂移 ★ |
| ★**追加式** ★ | 另两条开口 / `merged_opening` / `consts` / 老 `items[]` 一个字没改 (§B2-1) ★ |
| ★**零外发** ★ | ★**没发任何邮件 / 询价 / 问询 / 采购** ⇒ ★**缺口自己网上查** (GCT USB4105 数据表 PDF 已下载到 `logs/iss294/USB4105.pdf` + `pdftotext` 抽文本) + 标证据等级 + 查不到写 `[0数据]` (★立柱/螺钉头外径 / 座体真实高★) ★ |
| ★**不替老板拍板** ★ | 结构开口尺寸 / 立柱外径 / Z 向窗口 = 只列事实与代价, 归 main→老板 (§§4) ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead` (原子写) ⇒ 没写别人的分片 (`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰)** ★ |
| ★**分片写完 `grep` 校验** ★ | ★**`grep -c "iss294" state/fragments/mech.yaml` ⇒ 6 (2 条 need + 4 处 artifact 摘要 + 状态) ; `grep -c "已转出" ⇒ 1** ★ |

★**★ISS-290 那条 need 的处置 (★只有我能写自己分片, main 不越界★)★**: ★**`iss290_onpass_must_change_list_to_hw` 已标【已转出】(依据: main 16:0x 已转 hw-lead 的 ISS-292 任务书「⑬ 追加」节 · pm.yaml 已回写答案) ⇒ ★**没有自作主张关掉它**, 只在分片里写清依据; 顺带写明「E-6 的 MECH 半边已由 ISS-294 接手并交卷」** ★

---

## ★§7 · 为什么这一单必须赶在「板只改一次」那一趟之前 ★

★**USB-C 是 demo 板【唯一的供电 + 数据入口】(BOM 行 78 / 网表行 419: `RAIL_DEMO_5V` 与 `NET_USB_D_P/N_TYPEC` 都从 `J_USB_C` 来) ⇒ 结构件没有这条边开口 ⇒ 实物插头根本插不进去 ⇒ 板装上了也用不了** ★
★**⇒ 本单把这条边开口规格补齐, 让结构件能在开模前拿到「缺口 X 范围 + 深度 + Z 向窗口」三个数; ★**结构开口尺寸的最终拍板归 main→老板, 本单只交几何 + 代价 + 建议** ★
★**⇒ 板侧零影响 (本单零改板 ⇒ 不占「板只改一次」那一趟)** ★

---

## ★§8 · 复现命令 (★一条一条贴, 全部本机真跑过★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 logs/iss294/compute_iss294.py            # 几何自算 → logs/iss294/compute_iss294.json
python3 logs/iss294/check_sync_projection.py      # §5 机器块 ⇄ §2 逐条表 对账 (rc=0)
python3 MECH/check_onepass_mech_sync.py           # rc=0 (M1~M5)
python3 MECH/check_onepass_mech_sync.py --selftest   # rc=0 (12 条反向用例)
python3 MECH/check_onepass_struct_crosscheck.py   # rc=0 (N1~N6)
python3 MECH/check_onepass_struct_crosscheck.py --selftest   # rc=0 (12 条反向用例)
python3 MECH/check_demo_struct_truth.py           # rc=0
python3 MECH/check_board_frame_coords.py          # rc=0
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py   # 全 rc=0 (Q1 18/18)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**零外发** ★
