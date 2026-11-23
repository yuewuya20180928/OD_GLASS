# ISS-371 · mech-lead · 「板那一趟」`J_DEBUG` 排针 land 改 1.27mm 后的结构侧净距真相 · 纯分析 + 文档订正 + 新建闸 + 沙盒预演

★★**题**: ★**把「`J_DEBUG` 排针 land 从 pitch 0.50 改到 1.27」这条**板侧已拍板**的改动, 用【本机 KiCad 官方真 land】重算一遍结构侧净距, 并查清【现有三页 + 机器块里的数到底对不对、差在哪、差多少】—— 然后把错的地方**追加式**订正掉, 并做成一条机器闸防止再漂回去** ★★
★★**类别**: ★**纯分析 + 文档订正(追加式) + 新建闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板** ★★

---

## ★★〇 · main 的本机实读 (★2026-11-23 20:4x~20:5x · 全部数字本机可复跑 · 不抄任何 agent 报告★) ★★

★**本单的由来 = 一条至今没人答的跨域 need**: `state/fragments/hw.yaml` → `needs_from` → key `iss356_jdebug_mech_clearance_recheck` · `to: mech-lead` · `since: 2026-11-23` · ★**至今未闭合** (全 4 个分片的 answers 集合里零命中) ★ ★**这条 need 的原话要点 (逐字照抄·不加工★)**:

> ★**ISS-356 D3 引出的结构净距口径差 (MECH 域, 本单只报量差)★**: `J_DEBUG` 的板侧 land 改动 (0.50 → 1.27mm pitch) 已由 E-1 拍死并登记在 ISS-343 的 `B33_PIN_LAND_1P27` ⇒ 本单不重复做, 只给封装真值 `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` (4 通孔 @1.27, pad 1.0×1.0, 实测在盘) ★ ⇒ ★**但量差要核**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §C-SEAT-1 的清空区是按 1.27 pitch + **0.275mm 宽 pad** 算的 (X 宽 4.0850mm), 而官方 THT 排针 pad 宽 **1.0mm** ⇒ 铜箔净宽 **4.81mm** ⇒ 差 **0.725mm** ⇒ ★**请按官方 land 核清空区/开口/座体净距是否还过 (单边间隙与 `CRIT` 0.60 的关系)**★ ⇒ 若改用 SMD 变体 (`PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left`) 则 land 变 2×2 交错而非 1×4 直排 ⇒ 结构尺寸要重算 (本单已把这条列为降级方案)★

★**⇒ 本单 = 把这条 need 做掉** (它本来就是派给 mech-lead 的) ★

### ★★〇.1 · 本机实测: 官方真 land 的焊盘几何 (★不是抄文档, 是读盘上 `.kicad_mod`★) ★★

★**官方 THT 变体 (★本单的主对象★)**: `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ★**本机实测在盘** (库根 `/home/yuewuya/kicad/AppDir/share/kicad/footprints` · ★与 `HW/check_fp_truth_baseline.py` / `HW/check_fp_truth_land_swap.py` 用的是同一个 `LIBROOT_DEFAULT`★) ★

```
pad1 thru_hole size=1 1 drill=0.65 at=0    0
pad2 thru_hole size=1 1 drill=0.65 at=0    1.27
pad3 thru_hole size=1 1 drill=0.65 at=0    2.54
pad4 thru_hole size=1 1 drill=0.65 at=0    3.81
fp_rect  start=-1.55 -1.14  end=1.55 4.95     ← fab 外形
```

★**⇒ 铜箔 X 宽 = 3×1.27 (跨距 3.81) + 1.0 (pad 宽) = ★4.8100mm★** (★不是 4.0850★)
★**⇒ 钻孔 Ø0.65 ⇒ 环宽 = (1.0 − 0.65)/2 = 0.1750mm** (★★本仓【无任何环宽判据】—— `HW/iss121_mic_magnet_check.py` 只查到 `min_hole_clearance=0.25`, 那不是环宽 ⇒ 环宽这一项是 [0数据]★)
★**⇒ fab 外形 = 3.10 (X) × 6.09 (Y)** (★X 宽 3.10 > 铜箔 4.81 的 Y 向口径另算★)

★**官方 SMD 变体 (★降级方案·本单要一并给口径★)**: `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` ★**本机实测在盘** ★

```
pad1 smd size=3 0.65 at=-1.5 -1.905
pad2 smd size=3 0.65 at= 1.5 -0.635
pad3 smd size=3 0.65 at=-1.5  0.635
pad4 smd size=3 0.65 at= 1.5  1.905
fp_rect  start=-3.5 -3.04  end=3.5 3.04     ← fab 外形 7.00 × 6.08
```

★**⇒ 2×2 交错 (不是 1×4 直排) ⇒ 铜箔 X 跨距 = 3.0 (中心距) + 3.0 (pad 长) = 6.00 ⇒ fab 7.00 × 6.08** ★★**⇒ 这条 land 的【任何】结构尺寸都跟现页口径不可比 ⇒ 降级方案必须整段重算, 不能套用现页数字** ★

### ★★〇.2 · 本机实测: 板面现状 `J_DEBUG` (★读板文件本体·不是抄页★) ★★

```
footprint ""            ← ★★lib_id 空 ⇒ 自绘占位, 不是官方 land★★
(at 144.3 58)  layer F.Cu
Reference "J_DEBUG"    Value "1×4 1.27mm 排针 (JTAG)"
F.Fab 外形 (fp_line): -3 -2 .. 3 2   ⇒ 6.00 × 4.00
pad1 smd rect (at -2.1 -1.4) (size 0.275 0.9)   ← ★★pad 宽只有 0.275★★
pad2 smd rect (at -1.6 -1.4) (size 0.275 0.9)
pad3 smd rect (at -1.1 -1.4) (size 0.275 0.9)
pad4 smd rect (at -0.6 -1.4) (size 0.275 0.9)
net: JTAG_TCK / JTAG_TMS / JTAG_TDI / JTAG_TDO
```

★**⇒ 板面是【SMD 占位 (0.275×0.9) + pitch 0.50】, 而官方 1.27 land 是【THT (1.0×1.0) + pitch 1.27】⇒ ★★换 land 同时是【换型 SMD→THT】+ 【换封装真值】+ 【换 pitch】三件事捆在一起★** ★
★**⇒ 板面 fab 外形 6.00×4.00 是【占位自绘】的, 跟官方 THT 的 3.10×6.09 也不一样 ⇒ 开口/座体口径同样要重核** ★

### ★★〇.3 · 本机实测: 现有四处的数 (★现存口径到底写了什么★) ★★

| 位置 | 现写内容 | 本机实读行号 |
|---|---|---|
| `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §C-SEAT-1 | 清空区 X 宽 **1.7750 ⇒ 4.0850** · 单边间隙 X **4.2125 ⇒ 3.0575** (最坏 2.7575) · 「仍 ≥ CRIT 0.60」 | L326 |
| `MECH/BOARD_ONEPASS_MECH_SYNC.md` | 同上 (机器块口径) | L561-L565 · L572 |
| `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` | 同上 (§C-OPEN-1 · `body_w` 1.775) | L50 · L58 · L133 |
| `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | 同上 (§4 表 + **机器块** `clearance_x: 3.0575` / `worst_clearance_x: 2.7575` / `placeable_width: 3.0575` / `delta_clearance_x: -1.155`) | L175 · L205 · L211 · L216 · L241-L242 · 机器块 L1917-L1927 |

★**⇒ 四处写的是同一个数 (4.0850 / 3.0575 / 2.7575) ⇒ ★★它们是【同一处推导的四个副本】⇒ 一个地方错 ⇒ 四处一起错 ⇒ ★★这正是「同一处推导四处复制」的结构性病灶★** ★
★**⇒ 而 4.0850 的来历本机可反推: 4.0850 = 3.81 (跨距) + 0.275 (★沿用了板面占位 SMD pad 的 0.275 宽★) ⇒ ★★它算的是「把 SMD 占位的 0.275 宽 pad 搬到 1.27 pitch 上」, 不是「官方 THT land 的 1.0 宽 pad」★ ★

### ★★〇.4 · 本机实测: 按官方 THT land 真值重算 (★居中解·板面不动·只换 land★) ★★

★**输入 (★全部来自 §〇.1/§〇.2/§〇.3★)**: 板面 `J_DEBUG` 铜箔 X 中心 = (142.0625+143.8375)/2 = **142.9500** · 开口 X = **137.850 .. 148.050** (`PORT_OPEN_DEBUG` · `CRIT` = 0.60 = `MECH/service_port_check.py` 的 `2 × TOL["fdm_part"]` · `TOL["fdm_part"]=0.30`)

```
现状 (pitch 0.50 · SMD 0.275 宽):
  铜箔 X 142.0625..143.8375 (宽 1.7750)  ⇒ 单边间隙 X 4.2125 / 4.2125 (对称) ⇒ 最坏 3.9125

现页口径 (pitch 1.27 · 沿用 0.275 宽 pad):
  铜箔 X 140.9075..144.9925 (宽 4.0850)  ⇒ 单边间隙 X 3.0575 / 3.0575 (对称) ⇒ 最坏 2.7575  ⇒ ≥ 0.60 过

★官方 THT 真值 (pitch 1.27 · pad 1.0 宽):
  铜箔 X 140.5450..145.3550 (宽 4.8100)  ⇒ 单边间隙 X 2.6950 / 2.6950 (对称) ⇒ 最坏 2.3950  ⇒ ≥ 0.60 过
  ★⇒ 结论【方向不变】(仍过 CRIT, 余量 3.99×) ★
  ★⇒ 但【数全错】: 单边间隙 3.0575 ⇒ 2.6950 (Δ −0.3625) · 最坏 2.7575 ⇒ 2.3950 (Δ −0.3625) ★
  ★⇒ ★★致命的一条: 清空区宽仍按 4.0850 留 ⇒ 最外侧焊盘每边【超出清空区 0.3625mm】★★
     ⇒ 铜箔直接进清空区 ⇒ 【结构侧清空区必须同时改到 4.8100】★ ★
```

★**⇒ ★★main 的本机实算结论 (★可复跑, 不抄任何 agent 报告★)★★**: ★**「过 CRIT」这个结论在官方 THT land 下【依然成立】, 但现页的每一个数都偏乐观 0.3625mm; 且清空区宽度必须从 4.0850 改到 4.8100, 否则铜箔越界 0.3625mm/边** ★ ★
★**⇒ ★★这正是「板只改一次」最怕的那一类: 板改完了才发现结构侧清空区少留了 0.3625 ⇒ 要么改结构件 (⇒ 返工) 要么改板 (⇒ ★★板 md5 变第二次 ⇒ 整趟白跑★)★** ★
★**⇒ 所以本单必须在板那一趟【开工前】把这个数算准** ★

### ★★〇.5 · 本机实测: 判据常量与闸链现状 (★你只能读, 不许改★) ★★

| 事实 | 值 / 位置 | 本机实读 |
|---|---|---|
| `CRIT` | **0.60** = `2 × TOL["fdm_part"]` | `MECH/service_port_check.py` L126-L127 |
| 开口 Y 口径 | `OPEN_Y_eff(h) = max(4.60, h + 1.80)` · h = `[0数据]` | `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L63 |
| 板面 `J_DEBUG` 位置 | (144.30, 58.00) · 铜箔 X 142.0625..143.8375 × Y 56.1500..57.0500 | 板文件实测 |
| MECH 域既有闸 (★你改页后它们必须仍绿★) | `MECH/check_onepass_mech_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_board_frame_coords.py` · `MECH/check_mech_dual_caliber_gate.py` · `MECH/check_onepass_s10_led_spec_sync.py` · `MECH/check_onepass_s10_fp_swap_impact.py` | ★本机实跑 ★**7 道全 rc=0** ★ |
| 环宽判据 | ★**本仓无任何环宽判据 ⇒ [0数据]★** | `grep -rni "annular\|环宽"` 只命中 `state/gen_pcb_routing.py` 的过孔注释 |

---

## ★★一 · 本单要交什么 (★3 件 · 不许扩项★) ★★

### ★★① ★**新建** 一页: `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ★★

★**必含 (每节都要带复跑命令 + 证据等级)★**:

- ★**§0 口径与读数** (★每行带「哪个脚本产出·怎么复跑」★): 官方 THT land 几何 (§〇.1 全部逐行) + 官方 SMD 变体几何 + 板面占位几何 (§〇.2) + 现有四处口径 (§〇.3 带行号) + `CRIT` 来源行号
- ★**§1 逐条量差表** (★这是本单的正题·必须逐行可核★): 三档口径 (现状 / 现页 0.275 假设 / 官方 THT 真值) × 每一项 (铜箔 X 宽 · 必须清空区 X · 单边间隙 X 左/右 · 最坏 · ≥`CRIT` 余量 · 开口 X 是否不变 · fab 外形) ★**每格写清「谁算的·依据哪一行」**
- ★**§2 差额的三个后果** (★逐条给结论 + 代价★):
  - ① 结论方向 (★仍过 `CRIT` · 余量多少★)
  - ② ★★清空区宽度必须 4.0850 ⇒ **4.8100** ★★ (★否则每边越界 0.3625★)
  - ③ 开口 X / 开口 Y 口径是否要动 (★自己实算, 别猜★)
- ★**§3 降级方案 (SMD 变体) 的结构后果**: 2×2 交错 ⇒ 铜箔 X 跨距 6.00 · fab 7.00×6.08 ⇒ ★**逐项说明现页口径哪一条完全不可比·哪些要整段重算**★ (★不许只写「要重算」三个字★)
- ★**§4 换型这件事本身 (SMD 占位 ⇒ THT) 的结构后果**: ★**本机实测板面是 SMD 0.275×0.9 占位, 官方是 THT 1.0×1.0 ⇒ 环宽 = (1.0−0.65)/2 = 0.1750mm ⇒ 本仓无环宽判据 ⇒ 标 [0数据]·不许编一个环宽下限★**
- ★**§5 未决项 (★只登记·不代拍·每条给两条路的代价★)**: 换 land 的落点坐标 (★是否仍 (144.30, 58.00)·自己实算·不许假设★) · `h` 三档对开口 Y 的影响 · 环宽下限 (★[0数据]·谁去问★) · **S4 的 `D_ESD_USB_D` 2→3 脚 (W-1/W-2) 会不会改这块地** (★只登记★)
- ★**§6 证据分级表**: 每条结论标 `[实测]` / `[推算]` / `[0数据]` (★不许出现「可能」「大概」这种无档措辞★)

★**★只允许【追加式】改既有页 (★老字一字不许删·不许改★)★**: ★**你在 §1/§2 里给出的表, 要以【追加块】的形式写进 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 与 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 的文件末尾 (★照本仓既有惯例: 追加式订正 + 老字保留 + 机器块同步加字段而不是改旧字段的值★)★**
★**★绝对不许改 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` (★那是别人的域 ★ HW 那份是 hw-lead 的作业包·MECH_CLAIMS 那份的 §C-OPEN-1 是既有正文★)⇒ 你只登记「它们也带着同一组错数」, 改由 main 拍★** ★
★**★机器块 (`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 的 JSON 块) 你可以加新字段 (如 `jdebug_1p27_*`), ★★但旧字段 (`clearance_x` / `worst_clearance_x` / `placeable_width` / `delta_clearance_x` / `delta_w_clear`) ★★一个都不许改值★ ★ ⇒ 改完之后 §〇.5 那 7 道 MECH 闸必须仍全 rc=0 (★`check_onepass_s10_fp_swap_impact.py` 与 `check_mech_verdict_freshness.py` 读这个块·你加字段不能把它们的既有判据打红★) ★

### ★★② ★**新建** 机器闸: `MECH/check_jdebug_1p27_clearance.py` ★★

★**判据 (★自证型·不许靠注释说绿★)**:

| # | 判据 | 要点 |
|---|---|---|
| G1 | ★**官方 THT land 的焊盘几何必须与 `.kicad_mod` 实读一致** | ★自己解析 `.kicad_mod` (不许写死 4.8100)· 解析出 pad 数/pitch/pad 宽 ⇒ 算出铜箔 X 宽 ★ |
| G2 | ★**§1 那一页声明的三档宽度与 G1 实算逐项一致** | 不一致 ⇒ 红 |
| G3 | ★**必须清空区宽 ≥ 铜箔 X 宽 (不许越界)** | ★这一条是本单的核心判据: 留 4.0850 而铜箔 4.8100 ⇒ 红 ★ |
| G4 | ★**单边间隙 X (左/右) 对称且 ≥ `CRIT` 0.60** | `CRIT` 从 `MECH/service_port_check.py` 取 (★不许写死 0.60★) · 不对称 ⇒ 红 |
| G5 | ★**降级方案 (SMD 变体) 的几何必须也实测一遍并单列** | 不许拿 THT 的数套用 |
| G6 | ★**板面零写板自证** (板 md5/mtime/size 三项) | ★基线 `611b869e13518c3c019` 口径见 §〇· 漂移 ⇒ 红 ★ |
| G7 | ★**证据等级五级白名单 + 正文零挂起措辞** | ★照 `MECH/check_onepass_s10_led_spec_sync.py` 的现成判据形状 ★ |

★**★`--selftest` 反向用例 ≥ 6 条 · 每条必须自证「红的集合 == {目标那一条}」(★多红一条即判该用例 FAIL★)★** ★建议至少含: ①把 §1 里的清空区宽改小 0.001 ⇒ G3 红 ②把单边间隙改到 0.59 ⇒ G4 红 ③把左右间隙改成不等 ⇒ G4 红 ④把 §1 的 4.8100 改成 4.0850 ⇒ G2 红 ⑤在沙盒里把板改一个字节 ⇒ G6 红 ⑥把证据等级写成第六级 ⇒ G7 红 ★
★**★沙盒纪律: 沙盒一律落项目盘 `tmp/iss371_sbx/` (★不许写 `/tmp` — ★★2026-11-23 04:4x 实测系统 `/tmp` 配额已满, 写 `/tmp` 会让闸拿到假读数★)★★ ★

### ★★③ 交卷页 + 分片 + 留证 ★★

- ★**交卷页**: `HANDOFF/2026-11-23_mech-lead_ISS371_JDEBUG排针1.27净距真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★)
- ★**分片**: `state/fragments/mech.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ 写前写后各记一次 md5 基线 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」· 不许静默覆盖
- ★**留证**: `logs/iss371/` (★基线 md5 / 实算脚本 / 沙盒三档对照读数 / selftest 全量输出 / 7 道 MECH 闸复跑输出★) (★≥10 件★)
- ★**★必须回答 `iss356_jdebug_mech_clearance_recheck` 这条 need (★在 `mech.yaml` 的 `answers` 里用同 key 记答案★)★** —— ★★否则这条 need 会永远挂着, 下一个 agent 还得重查一遍★ ★

---

## ★★二 · 边界 (★逐条·不许越★) ★★

| 边界 | 要求 |
|---|---|
| ★**零写板** | 板 md5 必须仍 `611b869e13518c3c019` 口径下 = `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413` · size 仍 4940213 · ★**开工前 + 交卷后各打一次双证★** · 换 land 只许在 `tmp/` 副本上做 |
| ★**零落表** | `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · 原理图 · `state/issue_log.yaml` 一字不改 |
| ★**零改既有闸** | §〇.5 那 7 道 MECH 闸 + `state/check_pcb_nets.py` + `state/gate_check.py` + `state/merge.py` + `state/frag_write.py` 一字不改 |
| ★**零改既有页面正文** | `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` ★**只许文件末尾追加块**★ · `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★**一个字都不许动**★ |
| ★**零挂链** | ★**本单新建的闸也不许挂** ★(`state/gate_check.py` 的 `EXTRA_GATES` 一行都不许动) |
| ★**只写自己的分片** | 只写 `state/fragments/mech.yaml` (只走 `frag_write.py`) |
| ★**不代老板拍板** | `h` 三档 · 环宽下限 · 落点坐标 · S4 的 ESD 2→3 脚 (W-1/W-2) ⇒ ★**只登记 + 给两条路的代价**★ |
| ★**零外发 / 零采购** | ★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ★★本单不许发任何邮件/询价/问询 ★ |
| ★**不自签 issue_log** | 不许改 `state/issue_log.yaml` 的任何字段 (★签收归 main★) |

---

## ★★三 · 必跑命令 (★全部真实存在 · main 2026-11-23 20:5x 本机实测过★) ★★

```bash
# ★板双证 (开工前 + 交卷后各一次)★
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ★官方 land 实读 (★不许写死常数★)★
ls -l /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod
grep -E '\(pad |fp_rect' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod

# ★判据常量真身★
grep -n 'CRIT\|TOL' MECH/service_port_check.py

# ★7 道 MECH 既有闸 (★你追加块之后必须仍全绿★)★
python3 MECH/check_onepass_mech_sync.py            # rc=0
python3 MECH/check_onepass_struct_crosscheck.py    # rc=0
python3 MECH/check_demo_struct_truth.py            # rc=0
python3 MECH/check_board_frame_coords.py           # rc=0
python3 MECH/check_mech_dual_caliber_gate.py       # rc=0
python3 MECH/check_onepass_s10_led_spec_sync.py    # rc=0
python3 MECH/check_onepass_s10_fp_swap_impact.py   # rc=0

# ★本单新建的闸 (★交卷时它还不存在·本单产出★)★
python3 MECH/check_jdebug_1p27_clearance.py            # rc=0
python3 MECH/check_jdebug_1p27_clearance.py --selftest  # rc=0 (反向用例全过)

# ★门禁三件套★
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0 (Q1 = 18/18)
python3 state/frag_write.py --agent mech-lead --show    # rc=0
```

★**★本单不许用 `bash state/pcbnew_py.sh state/check_pcb_nets.py` 改任何东西 (★那会写板副本的缓存★); 你要读板就读文件本体 (★`state/check_pcb_nets.py` 现在 rc=1 是老账·与你无关·你只需在交卷页如实记一句「未运行·零写板」即可★) ★**

---

## ★★四 · 交卷格式 (★照本仓惯例★) ★★

★**交卷页 B1~B6 六段 (★标题关键词要能被 `state/gate_check.py` 的 Q1 认出来★)★**: B1 结论 · B2 交付物 · B3 沙盒预演 · B4 接口取值/声明 · B5 边界自证 · B6 必跑命令输出 (★原文贴, 不许只写「全过」★)
★**★`state/gate_check.py` 的 Q1 判「B4 标题必须含 `接口取值` / `接口声明` / `interface_claims` / `接口请求` 之一」★ ★⇒ 你的 B4 标题就照抄这个词★ ★
★**★`state/gate_check.py` 的 Q1 还判「交卷页占位符 = 0」⇒ 交卷页里不许留 `TBD` / `待填` / `???` ★★**
★**★必跑命令的输出必须原样贴进 B6 (★rc 数字 + 关键行★), 并贴进 `logs/iss371/` ★**

---

## ★★五 · 一句话总结 (★你要回答的那个问题★) ★★

★**「`J_DEBUG` 改 1.27 之后, 结构侧清空区到底该留多宽、单边间隙还过不过 `CRIT` 0.60?」** ★
★**main 的本机实算已经指向答案 (★你必须独立复算一遍并自证, 不许直接抄★): 方向不变 (仍过 CRIT), 但清空区必须 4.0850 ⇒ 4.8100、单边间隙 3.0575 ⇒ 2.6950, 且现页四处 (含机器块) 全部偏乐观 0.3625mm; 而降级方案 (SMD 2×2 交错) 的几何与现页口径完全不可比, 必须整段重算** ★
★**★⇒ 这条数必须【在板那一趟开工前】定死 ⇒ 否则铜箔越界 0.3625 ⇒ 要么改结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑 ⇒ ★★这正是「板只改一次」铁律要防的那一类★ ★**
