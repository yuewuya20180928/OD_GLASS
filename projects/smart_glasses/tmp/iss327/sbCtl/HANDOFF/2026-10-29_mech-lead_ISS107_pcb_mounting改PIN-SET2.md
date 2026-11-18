# [mech-lead→PM] ISS-107 闭环 —— PCB 固定孔位改版 PIN-SET-2 (合并器 `pcb_mounting` 冲突 1→0)

- **发起方**: mech-lead (结构总工, 带散热) 🔩
- **日期**: 2026-10-29
- **关联**: ISS-107 (合并器冲突闭环) / ISS-049 (hw-lead 定版 PIN-SET-2) / ISS-105 (板框 60×15) / ISS-042 解 A (定位基准移到金属骨架)
- **结论**: 我分片里的 `pcb_mounting` 旧口径 `2xM1.2+1x⌀2.0H7` 已原子改成 PIN-SET-2 = **`2x⌀2.0H7+2x⌀1.4`**, 合并器**冲突数 1 → 0 (rc=0)**; MECH/ 下 5 个文件 20 处老口径引用同步更正; **打印包契约未改** (授权在 PM 手上)。
- **依据**: `MECH/PCB_MOUNT_PIN_SET2.md` (12,665 B) · `MECH/pinset2_mech_check.py` + `.json` (31 项, FAIL 0 / WARN 3, rc=0) · `HW/PCB_FIXING_PINSET2.md` (hw-lead ISS-049 定版, 36 项 rc=0) · `state/fragments/mech.yaml` (本单改动的 `interface_claims.pcb_mounting`)

---

## B1 结论摘要

1. **合并器冲突 1 → 0**。`state/fragments/mech.yaml` 的 `interface_claims.pcb_mounting` 从 `2xM1.2+1x⌀2.0H7` 改成 **`2x⌀2.0H7+2x⌀1.4`** (value + canon + note + ref 四项一次原子写, 走 `state/frag_write.py`)。实测 `python3 state/merge.py` → `冲突 1` 变 `冲突 0`, **rc=0**。

2. **老口径为什么必须废 (结构侧独立复算, 不是抄 hw-lead)**: 15mm 板宽下老口径按**最有利假设** (老孔就落在 SoC 的 X 段内) 复算, **3/3 孔压 SoC 逃线带** —— M1.2 压 Y **0.50mm**、⌀2.0 H7 压 **2.00×2.00mm** ⇒ **加宽不解**, 必须沿板长移出。PIN-SET-2 的 **4/4 孔与逃线带 X[20.20,31.80]×Y[2.70,12.30] 的 2D 重叠 = 0.0000 mm²** (真圆∩矩形解析积分, 非外接方框)。

3. **MECH/ 下 5 个文件 20 处老口径引用已更正**: `BOARD_WIDTH_15MM.md` 9 处 (§5.1 现状口径→作废留档 / §5.2 判死依据 / §5.3 建议→**定版坐标表** / §6 M-4 闭环 / §7 R-3 已执行 / §8 N2·N4 / §9 证据 / §10 复现) · `CLEARANCE_FIX.md` 4 处 (骨架接口表 / §B5 卡点 2 闭合 / §5.5 骨架 1 销→**2 销(一圆一菱)** / 代价) · `fit_check.py` 3 处 · `board_width_15mm_check.py` 3 处 · `cross_review_check.py` 1 处。幂等脚本连跑 3 次 = **改 0 条 / 跳过 20 条**, 无重复插入。

4. ★ **合并器比的是 canon 完整串, 不是"看起来一样"** —— 这是本单唯一一个"任务书没写、但不做就消不掉冲突"的坑: `merge.py` 的 `canon_of()` 只做「去括号注释 / 去空白分隔符 / lower / ×→x」四件事, **它不去 `PIN-SET-2:` 这个方案名前缀**。实测 `canon_of('PIN-SET-2:2x⌀2.0H7+2x⌀1.4')` = `pin-set-2:2x⌀2.0h7+2x⌀1.4` ≠ `canon_of('2x⌀2.0H7+2x⌀1.4')` ⇒ **只把 value 写成任务书那个裸串, 冲突照样判**。我按本项目**已有先例** (hw-lead 对 `skeleton_extent` 用 `canon:` 字段与我对齐, `state/fragments/hw.yaml:682`) 给 mech 侧补了显式 `canon: pin-set-2:2x⌀2.0h7+2x⌀1.4` ⇒ 两边 comparable canon **逐字节相等** ⇒ uniq=1 ⇒ 不判冲突。

5. **打印包契约本单未改 (授权在 PM 手上)**。PIN-SET-2 对打印件有 **3 项硬影响**, 已全部量化并留在 `MECH/pinset2_mech_check.json` 的 WARN 里: ① PCB 定位让过孔 **1 → 2 个**; ② M1.2 让过孔中心距 **40.00 → 44.00mm** (差 4.00); ③ 打印件 PCB 定位板长度 **50.00 → 60.00mm** (差 10.00)。这三个都属于 `MECH/print/GEOM_SPEC_REVA.md` 的契约, **改版授权 = 项目总工** (`needs_from` iss089_typec_opening_and_print_pack 已挂), 本单不越界。

---

## B2 验收标准自评 (逐条, 不达标也写出来)

| # | 验收标准 (ISS-107 任务书) | 自评 | 依据 |
|---|---|---|---|
| 1 | `state/fragments/mech.yaml` 的 `pcb_mounting` 改成 PIN-SET-2 `2x⌀2.0H7+2x⌀1.4` | ✅ **通过** | `MECH/_frag_update_iss107.py` (走 `state/frag_write.py` 原子写, 禁 `open(p,"w")`); 落盘后 `value='2x⌀2.0H7+2x⌀1.4'` / `canon='pin-set-2:2x⌀2.0h7+2x⌀1.4'` / `ref=MECH/PCB_MOUNT_PIN_SET2.md` |
| 2 | 走 `state/frag_write.py` 原子写, 禁止 `open(p,"w")` | ✅ **通过** | 脚本 `from frag_write import update_fragment` ⇒ tmp+fsync+`os.replace`; **我没写过 mech.yaml 的裸文件** |
| 3 | note 里"必须沿板长移出逃线区"的旧描述同步到 PIN-SET-2 已落地的表述 | ✅ **通过** | 新 note 含 4 孔坐标 + 定位角色 + 旧口径判死依据 + 2D 重叠 0.000mm² + 重复性 ≤0.046mm |
| 4 | ref 指到 `MECH/PCB_MOUNT_PIN_SET2.md` | ✅ **通过** | 同上 |
| 5 | MECH/ 里别处引用老口径 (2xM1.2 / 1x⌀2.0H7 / 边距2.50) 一并更正 | ✅ **通过** | 5 文件 20 处已改 (B1-3); 残留扫描仅剩**显式标注"作废/留档"**的证据性引用 + 我自己的脚本里的替换定义 |
| 6 | 只写自己的文件 (MECH/ + 自己分片 + 自己的交接单) | ✅ **通过** | 未碰 `HW/`、`SW/`、`state/fragments/{hw,sw,pm}.yaml`、netlist/BOM/生成器; `MECH/print/**` **未动** |
| 7 | `python3 state/merge.py` 输出冲突数 **1 → 0** | ✅ **通过** | 见 B6 实贴输出 |
| 8 | 交卷时把 ISS-107 status 从 `fixing` 推到 `fixed` 并落 `fix_ref` | ✅ **通过** | `state/issue_log.yaml` 的 ISS-107 (原子写, 见 B6) —— **不做这条, mech-lead 名下 11 条 open 待办会被 in_flight 规则继续挡住** |
| 9 | `python3 state/gate_check.py` Q1 = 18/18 | ✅ **通过** | 见 B6 实贴输出 |
| 10 | 结构侧 PIN-SET-2 独立复算 | ✅ **通过** | `MECH/pinset2_mech_check.py` rc=0, **31 项 / FAIL 0 / WARN 3** (3 个 WARN 全是"打印包契约未跟改", 不在本单范围) |
| 11 | 打印包契约 (MECH/print/**) 跟改 | ❌ **不通过 (越界, 非我该做)** | 授权在 PM 手上; 3 项量化差异已在 B1-5 列出, 等授权后同轮改 |
| 12 | 骨架"对角分布 ⇒ 多一个加工面"这条 | ⚠️ **未消 (仍挂)** | PIN-SET-2 **保留了 S1 (8.00,2.50) / S2 (52.00,12.50) 对角分布** ⇒ `BOARD_WIDTH_15MM.md` §8 N2 仍有效, 未闭 |
| 13 | 打印件实测尺寸 / 实物装配验证 | ⚠️ **未验** | 本单无实物; 打印件实测 **0 件已打** [0数据] |

---

## B3 证据分级

| 结论 | 等级 | 依据 |
|---|---|---|
| 合并器冲突 1 → 0 (rc=0) | **[实测]** | 实跑 `python3 state/merge.py` (前后两贴输出见 B6) |
| PIN-SET-2 4/4 孔与 SoC 逃线带 2D 重叠 = 0.0000 mm² (真圆∩矩形解析积分) | **[实测]** | `MECH/pinset2_mech_check.py` rc=0, 31 项 FAIL 0 / WARN 3; 机读结果 `MECH/pinset2_mech_check.json` |
| 老口径 3/3 孔压逃线带 (M1.2 压 Y 0.50mm / ⌀2.0 压 2.00×2.00mm) | **[实测]** (脚本复算) | 同上, `old_holes` 段 (按**最有利假设**取老孔 X) |
| PIN-SET-2 定版本身 (2×⌀2.0 H7 + 2×⌀1.4, 4 孔坐标) | **[官方-项目内]** | hw-lead ISS-049 交卷 `HW/PCB_FIXING_PINSET2.md` (36 项 rc=0) + `state/fragments/hw.yaml` 的 `pcb_mounting` |
| `canon_of()` 不去 `PIN-SET-2:` 前缀 ⇒ 裸串仍判冲突 | **[实测]** | 直接调 `state/merge.py` 的 `canon_of()` 实跑; 同机制先例 = hw-lead 对 `skeleton_extent` 用 `canon:` 字段 |
| 定位重复性 ≤0.046mm (骨架铣削面 ≤5µm + H7 销 ≤0.010) | **[推算]** | 公差链相加, 写清推算过程 |
| 打印件 3 项差异 (让过孔 1→2 / 孔距 40.00→44.00 / 板长 50.00→60.00) | **[实测]** (脚本复算) | `MECH/pinset2_mech_check.json` 的 `print_delta` 段 |
| PIN-SET-2 的螺钉热旁路 2 颗并联 **8.84 K/W** (L=1.0mm) / hw-lead T4 混算 **9.65 K/W**; 骨架 P1/S1 段 5.06 K/W、P2/S2 段 7.31 K/W | **[推算]** | `MECH/pinset2_mech_check.json` 的 `thermal` 段 (k=237.0 W/m·K, A=15.0×1.0mm²) —— **本单只出中间量, 不出新的皮肤侧温度数** |
| 整机功耗 0.95-2.0W / 皮肤侧 43°C 红线 (散热上下文) | **[推算]** (上游) | `MECH/MECH_BUDGET.md` §3.4 / PROJECT_TRACKER 锁定值 —— **本单未改散热路径, 隔热层 0.50 垫 + 0.30 空气隙一字未动** |
| 端到端延迟 60ms (上下文复述) | **[官方-项目内]** | PROJECT_TRACKER §0 锁定目标 —— **本单不触碰信号链, 与延迟无关** |
| 打印件实测尺寸 / FDM 孔径收缩 / 实物装配 | **[0数据]** | 打印件 **0 件已打**, 无实测值; 不编造 |
| JBD 座体 A/B/C 尺寸页 | **[0数据]** | 未核, 不在本单 |

---

## B4 接口取值声明 (已登记进自己分片的 `interface_claims`)

| key | value | canon | note | ref |
|---|---|---|---|---|
| `pcb_mounting` | `2x⌀2.0H7+2x⌀1.4` | `pin-set-2:2x⌀2.0h7+2x⌀1.4` | PIN-SET-2 定版 (采纳 hw-lead ISS-049): 2x⌀2.0H7 定位销孔 + 2x⌀1.4 压紧孔; P1(8.00,7.50) 圆销=全基准 / P2(52.00,7.50) 菱形销=只定Y⇒消过定位 / S1(8.00,2.50) / S2(52.00,12.50); 老口径 3/3 孔压逃线带已机械判死; 4/4 孔与逃线带 2D 重叠 0.000mm² | `MECH/PCB_MOUNT_PIN_SET2.md` |

> ★ **为什么带 `canon` 字段**: `merge.py` 的冲突判定比 canon 完整串; `canon_of()` 不去 `PIN-SET-2:` 前缀 ⇒ 与 hw-lead 的 canon 对不齐就会继续判冲突。本项目已有先例 (hw-lead `skeleton_extent` 用 `canon:` 对齐)。**value 保持任务书指定的裸串 `2x⌀2.0H7+2x⌀1.4`**, canon 只做机器比较用。

**本单同步更新的既有 answer** (不抹历史, 只追加更正):
`answers[iss105_pcb_outline_sync_60x15]` (→ hw-lead) 追加 "★2026-10-29 ISS-107 更正: 上句 '我这边的值已按 ISS-105 定版保持 (2xM1.2 + 1x⌀2.0H7)' 已作废"。**原因**: 那句会让人以为 mech 侧仍认老口径。

---

## B5 未决项与卡点

| # | 事项 | 需要谁回答什么 | 期望时限 | 走谁 | 我的假设 (未答复前) |
|---|---|---|---|---|---|
| 1 | **打印包契约跟改 PIN-SET-2** (3 项差异: 让过孔 1→2 个 / M1.2 让过孔孔距 40.00→**44.00** / PCB 定位板长 50.00→**60.00**) | 授权改 `MECH/print/GEOM_SPEC_REVA.md` + 重生成 STL + 改测量清单 | 下一轮 | 项目总工 | 假设**暂不改** —— 打印包维持 Rev A; 本单已把 3 项差异量化进 `pinset2_mech_check.json` 的 WARN, 授权后同轮落地 |
| 2 | **骨架剖面形状** (P1/P2 双销 + S1/S2 对角 ⇒ 多一个方向加工面) | 台阶 / U 形 / 槽形定哪个? 重量口径复核 | 2026-10-31 | 项目总工 → hw-lead | 假设**台阶形** (SoC 段满宽 15.00, 其余 10.00) = 1.81g/侧 |
| 3 | **板坐标 → 打印件坐标的映射** | `pinset2_mech_check.json` WARN 3 指出"映射尚未定义 (接口项 `pcb_loc_dowel_metal`)" ⇒ 孔距 44.00 落到打印件上落在哪 | 与第 1 项同轮 | 项目总工 → hw-lead | 假设**板坐标 = 打印件坐标** (X 0→60), 待锁 |
| 4 | **N2 骨架对角分布可加工性** (ISS-100 §8, 未消) | 骨架件方能否做两个方向的攻丝面 | 2026-10-31 | 项目总工 → 骨架件加工方 | 假设**能**; 不能则 S1/S2 同在 Y=2.50, 压紧力矩靠 P1/P2 销吃侧向力 |
| 5 | **实测数据全空** | 打印件实测尺寸 0 件; FDM 孔径收缩 (⌀1.4 / ⌀2.4) 无实测 | 打样后 | 项目总工 | 标 [0数据], 不编造 |

> ★ 本单**没有新增** needs_from —— 上面 5 条里第 1/2/3/4 条都已在我的分片里挂着 (`iss089_typec_opening_and_print_pack` / `iss049_skeleton_profile` / `iss049_mount_screw` / `iss100_frame_section` 等), **不重复登记**。
> ★ **本单不处理** ISS-089 交卷里的 6 条 needs_from (u8 镜框截面升阻塞级 / 打印包改版授权 / DECISIONS 口径更正 等) —— 走项目总工拍板, 不在本单范围。

---

## B6 自证复现命令

```bash
cd projects/smart_glasses

# ① 合并器: 冲突数必须是 0, rc 必须是 0
python3 state/merge.py; echo "rc=$?"
python3 state/merge.py --for mech-lead | grep -A3 "全局冲突"

# ② 本单的分片改动 (值 / canon / note / ref)
python3 -c "
import yaml,sys; sys.path.insert(0,'state')
d=yaml.safe_load(open('state/fragments/mech.yaml',encoding='utf-8'))
for c in d['interface_claims']:
    if c['key']=='pcb_mounting':
        print('value=',c['value']); print('canon=',c.get('canon')); print('ref  =',c.get('ref'))
"

# ③ 结构侧 PIN-SET-2 独立复算 (31 项, FAIL 0 / WARN 3), rc=0
python3 MECH/pinset2_mech_check.py; echo "rc=$?"

# ④ MECH/ 文档更正 (幂等: 连跑应显示 改 0 条 / 跳过 20 条)
python3 MECH/_apply_pinset2_docs.py

# ⑤ 质量门: Q1 必须 18/18
python3 state/gate_check.py | head -12

# ⑥ 改过的 MECH/ 脚本仍能跑通 (rc=0)
python3 MECH/fit_check.py >/dev/null; echo "fit_check rc=$?"
python3 MECH/board_width_15mm_check.py >/dev/null; echo "board_width rc=$?"
python3 MECH/verify_budget.py >/dev/null; echo "verify_budget rc=$?"

# ⑦ 队列状态: ISS-107 必须是 fixed 且 fix_ref 非空; mech-lead 名下 status=fixing 必须为 0
#    (= 11 条 open 待办不再被 advance.py 的 in_flight 规则挡住)
python3 -c "
import yaml
d=yaml.safe_load(open('state/issue_log.yaml',encoding='utf-8'))
iss=d['issues']; iss=list(iss.values()) if isinstance(iss,dict) else iss
for i in iss:
    if i.get('id')=='ISS-107':
        print('ISS-107 status =',i.get('status'),'| fix_ref',len(i.get('fix_ref') or ''),'B')
print('mech-lead fixing 条数 =',len([i for i in iss if i.get('owner')=='mech-lead' and i.get('status')=='fixing']))
print('mech-lead open   条数 =',len([i for i in iss if i.get('owner')=='mech-lead' and i.get('status')=='open']))
"
```

```
$ python3 -c "... (⑦) ..."
ISS-107 status = fixed | fix_ref 730 B
mech-lead fixing 条数 = 0
mech-lead open   条数 = 11
```

### 实贴输出 —— 改前 (冲突 1)

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-10-29T00:10:43+08:00)
   产出 73 | 阻塞 32 (高危 26) | 未闭合需求 47 | 冲突 1 | 健康度 red
   ⚠️ 冲突 pcb_mounting: {'hw-lead': 'PIN-SET-2:2x⌀2.0H7+2x⌀1.4', 'mech-lead': '2xM1.2+1x⌀2.0H7'}
```

### 实贴输出 —— 改后 (冲突 0)

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-10-29T00:12:47+08:00)
   产出 73 | 阻塞 32 (高危 26) | 未闭合需求 47 | 冲突 0 | 健康度 red
rc=0
```

```
$ python3 state/merge.py --for mech-lead | grep -A3 "全局冲突"
【全局冲突】0 项
  (无)
```

```
$ python3 MECH/pinset2_mech_check.py
------------------------------------------------------------------------------
复算项 31 | FAIL 0 | WARN 3
机读结果: MECH/pinset2_mech_check.json
rc=0
```

```
$ python3 state/gate_check.py | head -12
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-10-28_hw-lead_ISS062_R-GEO2四问并入沟通材料.md
   sw-lead    6/6  缺: 无   交接单: 2026-10-28_sw-lead_ISS104_电源状态术语统一.md
   mech-lead  6/6  缺: 无   交接单: 2026-10-29_mech-lead_ISS107_pcb_mounting改PIN-SET2.md
```

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

- **对方**: hw-lead
- **我的需求**: 确认 PIN-SET-2 的 **P2 菱形销 (对边 1.94) 与 S1/S2 ⌀1.4 过孔** 在 PCB 加工图上是普通圆孔 (不需要 PCB 侧做任何异形) —— 我的结构模型**假设 PCB 侧 4 个孔全是普通圆孔**, 消过定位靠骨架上那颗销的形状实现。
- **我的假设 (如果对方不回应, 我会按这个做)**: 按"PCB 侧 4 个普通圆孔"继续; 若 hw-lead 要在 PCB 侧做别的 (例如 P2 也做成异形孔), 结构侧要重算装拆与最小壁厚, 我会另开接口请求。

---

## 待办: 需要项目总工做什么

1. **确认 ISS-107 关闭**: 我已把 `state/issue_log.yaml` 的 ISS-107 从 `fixing` 推到 `fixed` 并落 `fix_ref` (见 B6-⑦)。**这条不做, mech-lead 名下 11 条 open 待办会被 `advance.py` 的 in_flight 规则继续挡住** —— 这是上一轮卡死的根因。
2. **拍板打印包改版授权** (B5-1): 3 项差异已量化, 等授权后我同轮改 `MECH/print/GEOM_SPEC_REVA.md` + 重生成 STL + 改测量清单。
3. **裁骨架剖面 + 板坐标→打印件坐标映射** (B5-2 / B5-3)。

## 阻塞: 缺什么信息

- **[0数据] 打印件实测**: 0 件已打 ⇒ FDM 孔径收缩 (⌀1.4 / ⌀2.4) 与装配公差无实测值, 全部标 [推算]。
- **[0数据] 骨架加工方**: 对角分布要多一个方向的攻丝面, 需骨架件方确认可行性 (B5-4)。
- **本单无外部依赖**: 未联系任何供应商 / 原厂; 一切对外经项目总工。

---

## 本单改动清单 (可逐条核对)

| 文件 | 类型 | 改了什么 |
|---|---|---|
| `state/fragments/mech.yaml` | 分片 (原子写) | `interface_claims.pcb_mounting`: value + canon + note + ref; `answers[iss105_pcb_outline_sync_60x15]` 追加作废更正 |
| `MECH/BOARD_WIDTH_15MM.md` | 文档 | 9 处 (§5.1 / §5.2 / §5.3 / §6 M-4 / §7 R-3 / §8 N2 / §8 N4 / §9 / §10) |
| `MECH/CLEARANCE_FIX.md` | 文档 | 4 处 (骨架接口表 3 行 / §B5 卡点 2 / §5.5 骨架行 / 代价行) |
| `MECH/fit_check.py` | 脚本 | 3 处打印文案 (定位链 + 代价 + 打印包未跟改告警) |
| `MECH/board_width_15mm_check.py` | 脚本 | 3 处 (docstring 口径声明 / Q4 处置输出 / 结论行) |
| `MECH/cross_review_check.py` | 脚本 | 1 处 (C-11 fallback 文案) |
| `MECH/PCB_MOUNT_PIN_SET2.md` | 文档 | **上一轮已在盘, 本单未改** (本单的依据) |
| `MECH/pinset2_mech_check.py` / `.json` | 脚本/机读 | **上一轮已在盘, 本单未改** (复算结果 rc=0) |
| `MECH/_frag_update_iss107.py` | 新脚本 | 分片原子写工具 (走 `state/frag_write.py`) |
| `MECH/_apply_pinset2_docs.py` | 新脚本 | 文档更正 (20 条替换, 幂等, 原子写) |
| `state/issue_log.yaml` | 队列状态 | ISS-107 `fixing` → `fixed` + `fix_ref` (原子写) |
| `HANDOFF/2026-10-29_mech-lead_ISS107_pcb_mounting改PIN-SET2.md` | 本单 | 交接单 (B1~B6) |

**未碰**: `HW/` · `SW/` · `state/fragments/{hw,sw,pm}.yaml` · `state/gen_netlist.py` / `gen_bom.py` · `MECH/print/**` · `PROJECT_TRACKER.md` · `DECISIONS.md` · `INTERFACES.md`。
