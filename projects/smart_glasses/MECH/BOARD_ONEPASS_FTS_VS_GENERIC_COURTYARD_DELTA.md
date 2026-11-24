# BOARD_ONEPASS · FTS(厂件) vs 通用 KiCad 库件 · 对照物差集与判决链重算

> ISS-393 · mech-lead(结构总工) · 2026-11-24 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 不代拍
> 本页只【登记差集 + 出逐字订正建议】; 落不落归 main/boss。

## §0 一句话结论

**换厂件 (Samtec FTS) 之后, MECH 3D 判决链上【没有一个数会变】—— 变的是【陈述判决时用的对照物】;
被「把通用库件数当成厂件数」这条前提错误污染的结论, 只有 `OI-12` 一条 (「判据偏紧 0.5200」), 它【作废】;
其余判决链数值在现行「罩铜箔」口径下逐字不变, 因为 `C_copper` 只看焊盘, 钻孔 `0.65→0.71` 不进铜箔包络。**

★**口径前提 (★本单最值钱的一句★)**: 已签收闸 `MECH/check_debug_seat_3d_fit.py` L890/L891 的公式里
`margin_cover = (H_housing - C_copper)/2` ⇒ **「罩座体本体」根本不在公式里 ⇒ 现在生效的口径 = 【罩铜箔】**
⇒ 「罩座体本体」是【待 main/boss 裁的候选口径】, 不是现状 ⇒ **本单不代拍**。

## §1 两本对照账 (判决链消费的每一个几何量)

| # | 几何量 | 现在的出处 | 换厂件后的新值 | 差 | 证据等级 |
|---|---|---|---|---|---|
| 1 | 座体宽 X (4 位) | 通用库件 `F.Fab 5.0800` | 厂件 `5.0800` | `0.0000` | [官网]+[实测] |
| 2 | 座体宽 X (2 位) | 通用库件 `F.Fab 2.5400` (含笔画 `2.6400`) | 厂件 `2.5400` | `0.0000` (几何) | [官网]+[实测] |
| 3 | 座体深 Y (跨排距) | 通用库件 `F.Fab 2.1000` | 厂件 `2.1600` | **库件窄 `0.0600`** | [官网]+[实测] |
| 4 | 绝缘体高 Z | 通用库件无 → `[0数据]` | 厂件 `0.8600` | n/a | [官网] |
| 5 | 柱高 | 通用库件无 → `[0数据]` | 厂件 `3.05` | n/a | [官网] |
| 6 | 铜箔包络 X (4 位) | 焊盘 `1.00×1.00` @1.27 ⇒ `4.8100` | `4.8100` | `0.0000` 不变 | [实测] |
| 7 | 铜箔包络 X (2 位) | 焊盘 `1.00×1.00` @1.27 ⇒ `2.2700` | `2.2700` | `0.0000` 不变 | [实测] |
| 8 | 钻孔 Ø | 通用库件 `0.65` | 厂件 `0.71` | **`0.0600`** (不进铜箔包络) | [实测]+[官网] |
| 9 | 通用库件 `F.CrtYd` X (4/2 位) | `6.0900` / `3.5500` | 厂件无 courtyard | n/a | [实测] |
| 10 | 通用库件 `F.Fab` Y (4/2 位) | `2.1000` | 厂件 `2.1600` | `0.0600` | [实测] |

★**判据侧 / 事实侧分开登记**: ★**事实侧** = `[官网]`(厂件真值) + `[实测]`(本机通用 KiCad 库件) ·
★**判据侧** = `[推算]`(由事实侧按已签收闸的公式算出的余量/需求数) ⇒ 逐量见 §6 `dimensions[*].source` 与 `class`。

★**口径不一致 (本页 §1 第 2 行注脚)**: `F.Fab` 的 `fp_line` 笔画宽 = `0.1` ⇒
**「含笔画外廓」= 几何尺寸 + 0.1000 · 「不含笔画」= 几何尺寸** ⇒
`2.5400 + 0.1000 = 2.6400` · `2.1000 + 0.1000 = 2.2000`
⇒ **同一层 (`F.Fab`) 两种口径 ⇒ 「J_UART 座体本体上限 2.6400 × 2.2000」这个数是【口径产物】, 几何真值只有 `2.5400 × 2.1000`**。

## §2 重算清单 (A 不变 / B 变了 / C 待 main 拍)

★**两套口径的对照 (★防误读·两套不矛盾★)★**: 本节是★**决策链口径**★ (★A 11 / B 8 / C 5 条★);
§6 机器块是★**全量口径**★ (★A 32 / B 12 / C 6★) ⇒ 多出来的是【库件自身的量 (courtyard/`F.Fab`/钻孔) · 本单新引入的厂件量 (绝缘体高/柱高) · C 类候选口径量】。

★**判据公式 (★已签收闸 `MECH/check_debug_seat_3d_fit.py` L890-L891 逐字★)★**:
`M = max(H_housing, C_copper)` 逐轴取大 · `margin_open = (O_opening − M)/2` · **`margin_cover = (H_housing − C_copper)/2`**
· `worst = margin − TOL['fdm_part']` · 过阈 iff `worst ≥ CRIT`。
★**`CRIT = 2 × TOL['fdm_part'] = 0.6000` · `TOL['fdm_part'] = 0.3000` · 每边判据余量 `CRIT+TOL = 0.9000`** ★
(★真身 `MECH/service_port_check.py` L126-L127 · `[实测]`★)

### ★A 类 · 换厂件后【一个数都不用动】(11 个) ★

| 量 | 现值 | 为什么不变 |
|---|---|---|
| 铜箔包络 X (4 位) | `4.8100` | ★**铜箔包络只由焊盘 (`1.000×1.000` @ `1.27` 跨距 `3.81`) 决定, 钻孔不进铜箔包络** ★ ⇒ 孔 `0.65→0.71` 不动它 |
| 铜箔包络 X (2 位) | `2.2700` | 同上 (`1.27 + 1.000`) |
| 铜箔包络 Y | `1.0000` | 同上 (焊盘宽 `1.000`) |
| 清空区 X 需求 (J_DEBUG) | `6.6100` | 只吃铜箔 `4.8100 + 2×0.9000` |
| 清空区 X 需求 (J_UART) | `4.0700` | 只吃铜箔 `2.2700 + 2×0.9000` |
| 清空区 Y 需求 (现状口径) | `2.8000` | 只吃铜箔 `1.0000 + 2×0.9000` |
| 罩开口 Y | `4.6000` | 结构件自身规格, 与厂件无关 |
| `CRIT` / `TOL['fdm_part']` / 每边余量 | `0.6000` / `0.3000` / `0.9000` | 判据常量, 不吃零件 |
| 罩住余量 X (J_UART) / 最坏 | `0.1350` / `-0.1650` | 只吃【清空区 X `2.5400` − 铜箔 `2.2700`】 |
| 开口余量 X (J_DEBUG) / 罩住余量 Y / 最坏 | `2.6950` / `0.7700` / `0.4700` | 只吃铜箔与开口 |

★**⇒ 结论: 现行「罩铜箔」口径下, 判决链上【没有一个数会变】★**
(★**成立条件**: 板上焊盘保持 `1.000×1.000` —— 这是 HW ISS-387 `OI-387-1` 已登记、归 main 拍的那一条★)

### ★B 类 · 换厂件后【变了】(8 个) ★

| 量 | 现值 | 厂件真值 | 差 | 被谁消费 |
|---|---|---|---|---|
| 座体深 Y | `2.1000` (通用库件 `F.Fab`) | `2.1600` | `+0.0600` | `D-6` / `U-7` |
| 座体本体上限 (J_DEBUG) | `5.0800 × 2.1000` | `5.0800 × 2.1600` | Y `+0.0600` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L69 (`D-6`) |
| 座体本体上限 (J_UART) | `2.6400 × 2.2000` | `2.5400 × 2.1600` | X `−0.1000` / Y `−0.0400` | 同上 L90 (`U-7`) ★**原值是「含笔画」口径产物, 见 §1 注脚** ★ |
| 每边让位 (F.Fab 口径, J_UART) | `0.7150` | `0.7650` | `+0.0500`/边 | 罩住余量自证 |
| 钻孔 Ø | `0.65` | `0.71` | `+0.0600` | ★**只影响板, 不进铜箔包络 ⇒ 不进判决链** ★ |
| 绝缘体高 Z | `[0数据]` | `0.8600` | 新增 | `OI-11` (`h` 三档) |
| 柱高 | `[0数据]` | `3.05` | 新增 | 装配高度链 |
| ★**`OI-12`「判据偏紧 `0.5200`」** ★ | `0.5200` | ★**作废**★ | — | ★**对照物错** (`6.0900` 是通用库件 courtyard, 不是厂件 keepout) ⇒ **结论无效** ★ |

### ★C 类 · 卡在 main/boss 还没拍的路口 (5 条 · 只摆代价, 不代拍) ★

| # | 路口 | 现状 | 若改判据的代价 |
|---|---|---|---|
| C-1 | 罩住判据管到【铜箔】还是管到【座体本体】 | 管铜箔 (公式里根本没有座体本体项) | 改口径 ⇒ X 需求 `6.8800`/`4.3400` (各缺 `0.2700`) · Y 需求 `3.9600` (缺 `1.1600`) ⇒ **两件结构件都返工** (见 §4) |
| C-2 | `OI-12` 过不过严 | 结论已作废 (对照物错) | 需重裁: 是「判据偏严」还是「对照物用错」? ⇒ 两种口径的代价差一整轮结构件返工 |
| C-3 | `OI-13`「接受零余量」 | 现状口径下【几何成立但零制造余量】 | 座体口径下【装不下, 差 `1.1600`】⇒ 该选项【消失】 |
| C-4 | `OI-14` 目标值取多少 | 未裁 | 不裁 ⇒ 出件无唯一目标 |
| C-5 | 座体真实高 `h` 走哪一档 (`0.90`/`2.54`/`4.00`) | 未裁 | ★**厂件 `Z=0.8600` 是【连接器元器件的绝缘体高】, 与「罩/座体结构件」的 `h` 是两个主体 ⇒ 顶替会把罩高压得更红 ⇒ 禁掉** ★ |

## §3 前提错误的扩散面 (全仓实跑扫描)

★**扫描命令 (★本机实跑·2026-11-24·结果入 §6 `spread_sites`★)**:
`grep -rn "官方" MECH/ HW/ --include=*.md --include=*.py` ⇒ 命中后按
★**ISS-390 已签收闸 `MECH/check_fts_seat_body_geometry.py` L104-L116 的 13 条 `FORBIDDEN_MARKERS` 词表★** 精确匹配。
★**扫描范围排除项 (★显式声明·不许静默★)**: `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (★它以 `old`/`new` 数据对形式【引用】旧措辞, 属登记面★)
与 `MECH/check_fts_seat_body_geometry.py` (★词表本体★) ⇒ **真扩散面 = 18 处**。

★**机制 (★本单最值钱的一句★)**: MECH 现有语境里「官方」= ★**KiCad 官方通用库件**★ (★闸源码 L188 逐字: 「从官方 .kicad_mod 解析 pad」★),
而 ISS-390 以后「厂件」= ★**Samtec FTS**★ ⇒ **同一个词指两样东西 ⇒ 「通用库件数」被写成了「厂件官方数」⇒ 前提错误**。

| # | 文件:行 | 误认点 (★库件图元被说成厂件官方图★) | 建议新措辞 (★通用库件→厂件 两栏分写★) |
|---|---|---|---|
| S-01 | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` **L26** | 正文: 通用库件 `F.Fab 5.0800` / `F.CrtYd 6.0900` 被称作厂件官方 land | 通用 KiCad 库件 `PinHeader_1x04_P1.27mm_Vertical` 的 `F.Fab`/`F.CrtYd`; 厂件 FTS 座体本体 `5.0800 × 2.1600` |
| S-02 | 同上 **L114** | 正文 | 同 S-01 |
| S-03 | 同上 **L168** | 表格行: 通用库件 `F.Fab 5.0800` / `F.CrtYd 6.0900` 出处栏 | 同 S-01 |
| S-04 | 同上 **L193** | `OI-12` 行 ⇒ ★**对照物错 ⇒ 该结论作废** ★ | 同 S-02 (补: 厂件 FTS 无 courtyard 图元 ⇒ 该对照物不存在) |
| S-05 | 同上 **L854** | 机器块 `DP-5.basis` 字符串 | 同 S-01 |
| S-06 | 同上 **L897** | 机器块 `OI-12` 字符串 | 同 S-04 |
| S-07 | `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` **L69** | `D-6` 行: 通用库件 `F.Fab` `5.0800 × 2.1000` ⇒ 厂件真值应为 `5.0800 × 2.1600` | 厂件 `FTS-104-01-F-S` 座体本体 `5.0800 × 2.1600` `[官网]`; 通用 KiCad 库件 `F.Fab` `5.0800 × 2.1000` (不含笔画) |
| S-08 | 同上 **L90** | `U-7` 行: 通用库件 `F.Fab` `2.6400 × 2.2000` ⇒ 厂件真值 `2.5400 × 2.1600` | 厂件 `FTS-102-01-F-S` 座体本体 `2.5400 × 2.1600` `[官网]`; 通用 KiCad 库件 `F.Fab` `2.5400 × 2.1000` (不含笔画口径) |
| S-09 | 同上 **L114** | 正文 | 同 S-01 |
| S-10 | 同上 **L143** | 表格行: 通用库件 `F.CrtYd` 板向 X | 同 S-01 |
| S-11 | 同上 **L149** | 把通用库件包络说成 IPC 规范 | 通用 KiCad 库件的 `F.CrtYd` 是【库件包络】, 不是厂件 keepout |
| S-12 | 同上 **L154** | 判据需求与通用库件包络的比较写成「还小」 | 通用 KiCad 库件 `F.CrtYd` `6.0900` |
| S-13 | 同上 **L513** | 机器块 `D-6.current_text` | 同 S-07 (通用 KiCad 库件 `F.Fab` 口径要分开写) |
| S-14 | 同上 **L594** | 机器块 `U-7.current_text` | 同 S-08 (通用 KiCad 库件 `F.Fab` 口径要分开写) |
| S-15 | 同上 **L634** | 机器块 `OI-12.structural_answer` ⇒ 「硬差额 … 每边 `0.6400`」 | ★**作废**: 通用库件 `F.CrtYd` 口径 ⇒ 该硬差额不存在 |
| S-16 | `MECH/check_debug_seat_3d_fit.py` **L848** | ★**闸源码字符串** ★: 通用库件 `F.Fab 5.0800` / `F.CrtYd 6.0900` 被称作厂件官方 land | 同 S-01 |
| S-17 | 同上 **L879** | ★**闸源码 `OI-12` 字符串** ★ ⇒ ★**对照物错 ⇒ 该结论作废** ★ | 同 S-04 |
| S-18 | `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` **L190** | ★**跨域传播** ★: HW 页引用 `OI-12` 同一误认措辞 | 归 hw-lead / main, 本单只登记 |

★**边界自证**: ★**本单【没有】修这 18 处活副本里的任何一处** ★
(★`MECH/check_debug_seat_3d_fit.py` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 三件逐字节未动 ★)
⇒ ★**只登记 + 只出逐字订正建议, 落不落归 main** ★ (★`diff`/`md5` 见交卷页 B6★)

## §4 Y 向缺 1.1600 的完整复算 (★独立复算·不抄 ISS-390★)

★**常量 (★实读 `MECH/service_port_check.py` L126-L127★)**: `TOL['fdm_part'] = 0.3000` · `CRIT = 2×0.3000 = 0.6000`
· 每边判据余量 `CRIT + TOL = 0.9000` · `2 × 0.9000 = 1.8000` `[实测]`

### ★路径 ① 【罩铜箔】= 现在生效的口径 (★公式里根本没有座体本体项★) ★

| 步 | 算式 | 值 |
|---|---|---|
| 铜箔 Y 包络 (只由焊盘 `1.000` 宽决定) | `C_copper.y` | `1.0000` |
| 清空区 Y 需求 (罩铜箔) | `1.0000 + 2 × 0.9000` | `2.8000` |
| 罩开口 Y 最多可容的清空区 Y | `4.6000 − 2 × 0.9000` | `2.8000` |
| ⇒ Y 向缺口 | `2.8000 − 2.8000` | ★**`0.0000` (恰好卡死)** ★ |
| 开口余量 → 最坏余量 | `(4.6000 − 2.8000)/2 = 0.9000` → `0.9000 − 0.3000 = 0.6000` | `0.6000 = CRIT` ⇒ ★**压线过阈** ★ |

★**⇒ 现状: 「零制造余量」但【几何上成立】⇒ `OI-13`(接受零余量) 这个选项【存在】★**

### ★路径 ② 【罩座体本体】= 候选口径 (★若 main/boss 裁「判据也管座体本体」·只摆后果·不代拍★) ★

| 步 | 算式 | 值 | 判定 |
|---|---|---|---|
| 厂件座体深 Y | 官网 `.085 2.16 REF` | `2.1600` | `[官网]` |
| 清空区 Y 需求 (罩座体) | `2.1600 + 2 × 0.9000` | `3.9600` | — |
| 罩开口 Y 最多可容 | `4.6000 − 2 × 0.9000` | `2.8000` | — |
| ⇒ Y 向缺口 | `3.9600 − 2.8000` | ★**`1.1600`** ★ | ★**红 (装不下)** ★ |
| 罩开口 Y 需放大到 | `3.9600 + 2 × 0.9000` | ★**`≥ 5.7600`** ★ (现 `4.6000`, `+1.1600`) | 红 |
| X 需求 (J_DEBUG, 罩座体) | `5.0800 + 1.8000` | `6.8800` | ★**红 (缺 `0.2700`)** ★ |
| X 需求 (J_UART, 罩座体) | `2.5400 + 1.8000` | `4.3400` | ★**红 (缺 `0.2700`)** ★ |

★**哪个数一动就顶死另一个 (★代价核心★)★**:
① Y 与 X **各自独立** —— 放大罩开口 Y 到 `5.7600` 只解 Y, 不解 X 的 `0.2700`; 放大清空区 X 只解 X, 不解 Y ⇒ ★**两件结构件必须同批改** ★
② 现状口径下若不要「零余量」, 开口 Y 需 `≥ 5.6000` (★闸 `DP-4` 逐字★); 座体口径下需 `≥ 5.7600` ⇒ ★**两条路差 `0.1600`** ★
③ 罩开口 Y 放大 `1.1600` ⇒ 罩体卡位中心与壁厚要重画 ⇒ **与镜脚内腔/PCB 其它件是否干涉 = 结构件布局问题, 本单 `[0数据]` 未查** ⇒ ★**出件前必须重跑罩体布局核对** ★
④ ★**`OI-11` 的 `h` 三档 (`0.90`/`2.54`/`4.00`) 是【罩/座体结构件】的量, 而本单 `Z = 0.8600` 是【连接器元器件的绝缘体高】⇒ 两个主体 ⇒ 顶替会把罩高压得更红 ⇒ 禁掉** ★

★**⇒ `OI-13` 为什么消失 (★自复算★)**: 「接受零余量」= 接受【恰好压线】⇒ 只能救「差 `0.0000`」;
但座体口径下差的是 `1.1600` ⇒ ★**不是余量小, 是装不下 ⇒ 选项【消失】(不存在“再多挤一点就行”的解)** ★

## §5 降级方案 (官网图已到手 ⇒ 主力路径 + 单板样卡尺复核动作)

★**主力路径 (★不挂外部依赖★)★**: 厂件几何一律用已到手的官网机械/营销图
`tmp/iss393_sbx/fts-1xx-xx-x-sx-mkt.pdf` (★md5 `69d9415867cd642d6a6e07c6b755516b` · 文字层逐字: `(NO OF POS x .0500 [1.27])` ·
`.085 2.16 REF` · `.034 0.86 REF` · `.050 1.27 REF` · `-01: .120 [3.05] POST`★) ⇒ `5.0800`/`2.5400`/`2.1600`/`0.8600`/`3.05` `[官网]`。

★**唯一缺口 (★降级动作必须项·不是可选项★)★**: ★**`REF` 是基准尺寸, 图纸未给公差带** ⇒ 座体深 `2.1600` 与绝缘体高 `0.8600` 的实际公差未知 ★
⇒ **降级动作 = 落 FTS 时先打一块单板样 (★只一块, 不是整批★) + 卡尺量三个量**:

| 量 | 卡尺量法 | 量完填回哪一格 | 何时 / 谁 |
|---|---|---|---|
| ① 座体宽 X (跨排, 4 位件) | 卡尺跨两端面, 读外廓 | §1 表第 1 行 + §6 `dimensions.factory_seat_body_x_4pos.measured` | ★**板只改一次那一趟投板前** · mech-lead 收样后量 |
| ② 座体深 Y | 卡尺跨前后壁, 读外廓 | §1 表第 3 行 + §6 `dimensions.factory_seat_body_y.measured` | 同上 |
| ③ 绝缘体高 Z | 卡尺或塞尺读座面到 pin 座台面 | §1 表第 4 行 + §6 `dimensions.factory_insulator_height_z.measured` | 同上 |

★**量完的处理规则 (★先定好·免得量完再争★)★**:
① 若 |实测 − `2.1600`| ≤ `0.0500` ⇒ 直接用 `2.1600` 入账; 否则**以实测为准并回写 §6**;
② `Z` 的实测只用于**装配高度链** (镜脚内腔), ★**不许顶替 `OI-11` 的结构件 `h` 三档** (★主体不同, 见 §4-④★);
③ 柱高 `3.05` 若要进镜脚内腔高度预算, 走 §4-③ 的布局核对。

★**零挂起措辞自证**: 本页 ★**无任何「等外部方给结论」类措辞** ★
(★禁语清单不在本页复制, 见新闸 `MECH/check_fts_vs_generic_courtyard_delta.py` 的 `PENDING` 词表, 由闸逐条扫本页★)
⇒ ★**所有缺口都已落到【自己可执行的量具动作】或【自己算的数】上** ★

## §6 机器块 (--emit 可解析)

```json
{
  "schema": "mech.fts.vs.generic.courtyard.delta.v1",
  "issue": "ISS-393",
  "agent": "mech-lead",
  "updated": "2026-11-24",
  "dimensions": {
    "copper_env_x_4pos": {
      "value": "4.8100",
      "source": "derived",
      "old_value": "4.8100",
      "old_source": "derived",
      "class": "A",
      "note": "铜箔包络只由焊盘 1.000x1.000 @1.27 跨距 3.81 决定; 钻孔 0.65->0.71 不进铜箔包络; 厂件官方 land 图只给孔位不给焊盘直径 => 保持 1.000 即不变",
      "evidence": "[实测]+[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L847"
    },
    "copper_env_x_2pos": {
      "value": "2.2700",
      "source": "derived",
      "old_value": "2.2700",
      "old_source": "derived",
      "class": "A",
      "note": "同上 (1.27 + 1.000)",
      "evidence": "[实测]+[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L853"
    },
    "copper_env_y": {
      "value": "1.0000",
      "source": "derived",
      "old_value": "1.0000",
      "old_source": "derived",
      "class": "A",
      "note": "同上 (焊盘宽 1.000)",
      "evidence": "[实测]+[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L491"
    },
    "required_clearance_x_debug": {
      "value": "6.6100",
      "source": "derived",
      "old_value": "6.6100",
      "old_source": "derived",
      "class": "A",
      "note": "只吃铜箔 4.8100 + 2 x 0.9000; 座体口径不生效",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L846-L847"
    },
    "required_clearance_x_uart": {
      "value": "4.0700",
      "source": "derived",
      "old_value": "4.0700",
      "old_source": "derived",
      "class": "A",
      "note": "只吃铜箔 2.2700 + 2 x 0.9000",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L852-L853"
    },
    "required_clearance_y_copper": {
      "value": "2.8000",
      "source": "derived",
      "old_value": "2.8000",
      "old_source": "derived",
      "class": "A",
      "note": "只吃铜箔 1.0000 + 2 x 0.9000",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L838-L839"
    },
    "cover_opening_y": {
      "value": "4.6000",
      "source": "derived",
      "old_value": "4.6000",
      "old_source": "derived",
      "class": "A",
      "note": "结构件自身规格, 与厂件外形无关",
      "evidence": "[实测]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L839"
    },
    "crit": {
      "value": "0.6000",
      "source": "derived",
      "old_value": "0.6000",
      "old_source": "derived",
      "class": "A",
      "note": "CRIT = 2 x TOL['fdm_part'], 不吃零件",
      "evidence": "[实测]",
      "consumed_by": "MECH/service_port_check.py L126-L127"
    },
    "tol_fdm_part": {
      "value": "0.3000",
      "source": "derived",
      "old_value": "0.3000",
      "old_source": "derived",
      "class": "A",
      "note": "同上",
      "evidence": "[实测]",
      "consumed_by": "MECH/service_port_check.py L126"
    },
    "required_margin_per_side": {
      "value": "0.9000",
      "source": "derived",
      "old_value": "0.9000",
      "old_source": "derived",
      "class": "A",
      "note": "CRIT + TOL",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L809"
    },
    "cover_margin_x_uart": {
      "value": "0.1350",
      "source": "derived",
      "old_value": "0.1350",
      "old_source": "derived",
      "class": "A",
      "note": "只吃清空区 X 2.5400 与铜箔 2.2700",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L799"
    },
    "worst_margin_x_uart": {
      "value": "-0.1650",
      "source": "derived",
      "old_value": "-0.1650",
      "old_source": "derived",
      "class": "A",
      "note": "0.1350 - TOL 0.3000",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L799"
    },
    "open_margin_x_debug": {
      "value": "2.6950",
      "source": "derived",
      "old_value": "2.6950",
      "old_source": "derived",
      "class": "A",
      "note": "只吃铜箔与开口",
      "evidence": "[推算]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L3"
    },
    "cover_margin_y": {
      "value": "0.7700",
      "source": "derived",
      "old_value": "0.7700",
      "old_source": "derived",
      "class": "A",
      "note": "只吃铜箔与清空区",
      "evidence": "[推算]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L27"
    },
    "worst_margin_y": {
      "value": "0.4700",
      "source": "derived",
      "old_value": "0.4700",
      "old_source": "derived",
      "class": "A",
      "note": "0.7700 - TOL 0.3000",
      "evidence": "[推算]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L27"
    },
    "courtyard_allowance_per_side": {
      "value": "0.6400",
      "source": "generic_library",
      "old_value": "0.6400",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用库件 F.CrtYd 6.0900 与铜箔 4.8100 之差的一半; 该数是库件口径, 不进生效公式",
      "evidence": "[实测]+[推算]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L634"
    },
    "clearance_x_debug_candidate_1": {
      "value": "1.7750",
      "source": "derived",
      "old_value": "1.7750",
      "old_source": "derived",
      "class": "A",
      "note": "现状竞争值, 与厂件无关",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L37"
    },
    "clearance_x_debug_candidate_2": {
      "value": "4.0850",
      "source": "derived",
      "old_value": "4.0850",
      "old_source": "derived",
      "class": "A",
      "note": "现状竞争值, 与厂件无关",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L37"
    },
    "clearance_x_debug_candidate_3": {
      "value": "4.8100",
      "source": "derived",
      "old_value": "4.8100",
      "old_source": "derived",
      "class": "A",
      "note": "现状竞争值 (= 铜箔宽), 与厂件无关",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L37"
    },
    "smd_variant_copper_x": {
      "value": "1.9200",
      "source": "derived",
      "old_value": "1.9200",
      "old_source": "derived",
      "class": "A",
      "note": "SMD 变体分支的数, 本单不换变体",
      "evidence": "[实测]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L861"
    },
    "uart_max_copper_x_no_change": {
      "value": "0.7400",
      "source": "derived",
      "old_value": "0.7400",
      "old_source": "derived",
      "class": "A",
      "note": "2.5400 - 2 x 0.9000",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L860"
    },
    "opening_y_min_current_caliber": {
      "value": "5.6000",
      "source": "derived",
      "old_value": "5.6000",
      "old_source": "derived",
      "class": "A",
      "note": "现状口径下若不要零余量: 2.8000 + 2 x 0.9000",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L866-L867"
    },
    "lib_courtyard_x_4pos": {
      "value": "6.0900",
      "source": "generic_library",
      "old_value": "6.0900",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.CrtYd 图元 (rot 90 后板向 X); 厂件无此图元",
      "evidence": "[实测]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L848/L879"
    },
    "lib_courtyard_x_2pos": {
      "value": "3.5500",
      "source": "generic_library",
      "old_value": "3.5500",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.CrtYd 退包络",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L143"
    },
    "lib_courtyard_y": {
      "value": "3.1000",
      "source": "generic_library",
      "old_value": "3.1000",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.CrtYd 另一轴",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L26"
    },
    "lib_fab_x_4pos": {
      "value": "5.0800",
      "source": "generic_library",
      "old_value": "5.0800",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画); 与厂件同值属巧合",
      "evidence": "[实测]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L848"
    },
    "lib_fab_y_4pos": {
      "value": "2.1000",
      "source": "generic_library",
      "old_value": "2.1000",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69"
    },
    "lib_fab_x_2pos": {
      "value": "2.5400",
      "source": "generic_library",
      "old_value": "2.5400",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90"
    },
    "lib_fab_y_2pos": {
      "value": "2.1000",
      "source": "generic_library",
      "old_value": "2.1000",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90"
    },
    "lib_fab_x_2pos_incl_stroke": {
      "value": "2.6400",
      "source": "generic_library",
      "old_value": "2.6400",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 含笔画口径 (笔画宽 0.1) => 口径产物",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L113/L118"
    },
    "lib_fab_y_incl_stroke": {
      "value": "2.2000",
      "source": "generic_library",
      "old_value": "2.2000",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件 F.Fab 含笔画口径 => 口径产物",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90"
    },
    "lib_drill": {
      "value": "0.6500",
      "source": "generic_library",
      "old_value": "0.6500",
      "old_source": "generic_library",
      "class": "A",
      "note": "通用 KiCad 库件默认钻孔; 落厂件须改 0.71 但不进铜箔包络",
      "evidence": "[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L272"
    },
    "seat_body_x_4pos": {
      "value": "5.0800",
      "source": "factory",
      "old_value": "5.0800",
      "old_source": "generic_library",
      "class": "B",
      "note": "数值巧合不变 (通用库件 F.Fab 与厂件 N x 1.27 同值) => 掩盖了 X 方向的错; 出处改为厂件官网",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)"
    },
    "seat_body_x_2pos": {
      "value": "2.5400",
      "source": "factory",
      "old_value": "2.5400",
      "old_source": "generic_library",
      "class": "B",
      "note": "库件几何 2.5400 (含笔画 2.6400) -> 厂件 2.5400; 若沿用含笔画口径则差 0.1000",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)"
    },
    "seat_body_y": {
      "value": "2.1600",
      "source": "factory",
      "old_value": "2.1000",
      "old_source": "generic_library",
      "class": "B",
      "note": "通用库件 F.Fab 深 2.1000 -> 厂件官网 .085 2.16 REF",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69/L90"
    },
    "insulator_height_z": {
      "value": "0.8600",
      "source": "factory",
      "old_value": "0.0000",
      "old_source": "missing",
      "class": "B",
      "note": "库件无绝缘体高 => 厂件 .034 0.86 REF; 主体是连接器元器件, 不许顶替结构件 h 三档",
      "evidence": "[官网]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L876 (OI-11)"
    },
    "post_height": {
      "value": "3.0500",
      "source": "factory",
      "old_value": "0.0000",
      "old_source": "missing",
      "class": "B",
      "note": "库件无柱高 => 厂件 -01: .120 [3.05] POST",
      "evidence": "[官网]",
      "consumed_by": "装配高度链 (本单未消费)"
    },
    "factory_drill": {
      "value": "0.7100",
      "source": "factory",
      "old_value": "0.6500",
      "old_source": "generic_library",
      "class": "B",
      "note": "落厂件须改孔 0.65 -> 0.71; 不进铜箔包络 => 不进判决链",
      "evidence": "[官网]+[实测]",
      "consumed_by": "HW/check_fts_land_drill_same_batch.py"
    },
    "seat_body_limit_x_debug": {
      "value": "5.0800",
      "source": "factory",
      "old_value": "5.0800",
      "old_source": "generic_library",
      "class": "B",
      "note": "座体本体上限 (J_DEBUG): X 不变, Y 由 2.1000 -> 2.1600",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)"
    },
    "seat_body_limit_y_debug": {
      "value": "2.1600",
      "source": "factory",
      "old_value": "2.1000",
      "old_source": "generic_library",
      "class": "B",
      "note": "座体本体上限 (J_DEBUG) 的 Y 项",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)"
    },
    "seat_body_limit_x_uart": {
      "value": "2.5400",
      "source": "factory",
      "old_value": "2.6400",
      "old_source": "generic_library",
      "class": "B",
      "note": "座体本体上限 (J_UART) 的 X 项; 原值是含笔画口径产物",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)"
    },
    "seat_body_limit_y_uart": {
      "value": "2.1600",
      "source": "factory",
      "old_value": "2.2000",
      "old_source": "generic_library",
      "class": "B",
      "note": "座体本体上限 (J_UART) 的 Y 项; 原值是含笔画口径产物",
      "evidence": "[官网]+[实测]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)"
    },
    "allowance_per_side_uart_fab": {
      "value": "0.7650",
      "source": "derived",
      "old_value": "0.7150",
      "old_source": "derived",
      "class": "B",
      "note": "F.Fab 口径每边让位 (4.0700 - 2.6400)/2 -> (4.0700 - 2.5400)/2",
      "evidence": "[推算]",
      "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)"
    },
    "oi12_gap": {
      "value": "0.0000",
      "source": "derived",
      "old_value": "0.5200",
      "old_source": "derived",
      "class": "B",
      "note": "OI-12 '判据偏紧 0.5200' 作废: 对照物 6.0900 是通用库件 courtyard, 不是厂件 keepout",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L848/L879"
    },
    "required_clearance_x_debug_body": {
      "value": "6.8800",
      "source": "derived",
      "old_value": "6.6100",
      "old_source": "derived",
      "class": "C",
      "note": "候选口径(罩座体本体): 厂件 FTS 座体宽 X 5.0800 (与通用 KiCad 库件同值属巧合) + 2 x 0.9000 => 6.8800 => 缺 0.2700",
      "evidence": "[推算]",
      "consumed_by": "候选口径, 未生效"
    },
    "required_clearance_x_uart_body": {
      "value": "4.3400",
      "source": "derived",
      "old_value": "4.0700",
      "old_source": "derived",
      "class": "C",
      "note": "候选口径(罩座体本体): 厂件 FTS 座体宽 X 2.5400 (通用 KiCad 库件含笔画口径是 2.6400) + 2 x 0.9000 => 4.3400 => 缺 0.2700",
      "evidence": "[推算]",
      "consumed_by": "候选口径, 未生效"
    },
    "required_clearance_y_body": {
      "value": "3.9600",
      "source": "derived",
      "old_value": "2.8000",
      "old_source": "derived",
      "class": "C",
      "note": "候选口径(罩座体本体): 厂件座体深 Y 2.1600 + 2 x 0.9000 => 3.9600 => 缺 1.1600 => 装不下",
      "evidence": "[推算]",
      "consumed_by": "候选口径, 未生效"
    },
    "opening_y_min_body_caliber": {
      "value": "5.7600",
      "source": "derived",
      "old_value": "4.6000",
      "old_source": "derived",
      "class": "C",
      "note": "候选口径下罩开口 Y 需 >= 3.9600 + 2 x 0.9000 = 5.7600 (现状口径下只需 5.6000, 差 0.1600)",
      "evidence": "[推算]",
      "consumed_by": "候选口径, 未生效"
    },
    "max_housing_y_fits_opening": {
      "value": "2.8000",
      "source": "derived",
      "old_value": "2.8000",
      "old_source": "derived",
      "class": "C",
      "note": "罩开口 Y 4.6000 最多可容 H_y 2.8000 (两口径同值) => 座体口径下装不下",
      "evidence": "[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L839"
    },
    "seat_body_height_h_choice": {
      "value": "0.0000",
      "source": "missing",
      "old_value": "0.0000",
      "old_source": "missing",
      "class": "C",
      "note": "结构件 h 三档 0.90/2.54/4.00 待裁; 厂件 Z 0.8600 是元器件绝缘体高, 主体不同, 不许顶替",
      "evidence": "[0数据]+[推算]",
      "consumed_by": "MECH/check_debug_seat_3d_fit.py L876 (OI-11)"
    }
  },
  "delta_by_class": {
    "A_unchanged": [
      {
        "key": "copper_env_x_4pos",
        "value": "4.8100",
        "why_unchanged": "铜箔包络只由焊盘 1.000x1.000 @1.27 跨距 3.81 决定; 钻孔 0.65->0.71 不进铜箔包络; 厂件官方 land 图只给孔位不给焊盘直径 => 保持 1.000 即不变",
        "evidence": "[实测]+[推算]"
      },
      {
        "key": "copper_env_x_2pos",
        "value": "2.2700",
        "why_unchanged": "同上 (1.27 + 1.000)",
        "evidence": "[实测]+[推算]"
      },
      {
        "key": "copper_env_y",
        "value": "1.0000",
        "why_unchanged": "同上 (焊盘宽 1.000)",
        "evidence": "[实测]+[推算]"
      },
      {
        "key": "required_clearance_x_debug",
        "value": "6.6100",
        "why_unchanged": "只吃铜箔 4.8100 + 2 x 0.9000; 座体口径不生效",
        "evidence": "[推算]"
      },
      {
        "key": "required_clearance_x_uart",
        "value": "4.0700",
        "why_unchanged": "只吃铜箔 2.2700 + 2 x 0.9000",
        "evidence": "[推算]"
      },
      {
        "key": "required_clearance_y_copper",
        "value": "2.8000",
        "why_unchanged": "只吃铜箔 1.0000 + 2 x 0.9000",
        "evidence": "[推算]"
      },
      {
        "key": "cover_opening_y",
        "value": "4.6000",
        "why_unchanged": "结构件自身规格, 与厂件外形无关",
        "evidence": "[实测]"
      },
      {
        "key": "crit",
        "value": "0.6000",
        "why_unchanged": "CRIT = 2 x TOL['fdm_part'], 不吃零件",
        "evidence": "[实测]"
      },
      {
        "key": "tol_fdm_part",
        "value": "0.3000",
        "why_unchanged": "同上",
        "evidence": "[实测]"
      },
      {
        "key": "required_margin_per_side",
        "value": "0.9000",
        "why_unchanged": "CRIT + TOL",
        "evidence": "[推算]"
      },
      {
        "key": "cover_margin_x_uart",
        "value": "0.1350",
        "why_unchanged": "只吃清空区 X 2.5400 与铜箔 2.2700",
        "evidence": "[推算]"
      },
      {
        "key": "worst_margin_x_uart",
        "value": "-0.1650",
        "why_unchanged": "0.1350 - TOL 0.3000",
        "evidence": "[推算]"
      },
      {
        "key": "open_margin_x_debug",
        "value": "2.6950",
        "why_unchanged": "只吃铜箔与开口",
        "evidence": "[推算]"
      },
      {
        "key": "cover_margin_y",
        "value": "0.7700",
        "why_unchanged": "只吃铜箔与清空区",
        "evidence": "[推算]"
      },
      {
        "key": "worst_margin_y",
        "value": "0.4700",
        "why_unchanged": "0.7700 - TOL 0.3000",
        "evidence": "[推算]"
      },
      {
        "key": "courtyard_allowance_per_side",
        "value": "0.6400",
        "why_unchanged": "通用库件 F.CrtYd 6.0900 与铜箔 4.8100 之差的一半; 该数是库件口径, 不进生效公式",
        "evidence": "[实测]+[推算]"
      },
      {
        "key": "clearance_x_debug_candidate_1",
        "value": "1.7750",
        "why_unchanged": "现状竞争值, 与厂件无关",
        "evidence": "[推算]"
      },
      {
        "key": "clearance_x_debug_candidate_2",
        "value": "4.0850",
        "why_unchanged": "现状竞争值, 与厂件无关",
        "evidence": "[推算]"
      },
      {
        "key": "clearance_x_debug_candidate_3",
        "value": "4.8100",
        "why_unchanged": "现状竞争值 (= 铜箔宽), 与厂件无关",
        "evidence": "[推算]"
      },
      {
        "key": "smd_variant_copper_x",
        "value": "1.9200",
        "why_unchanged": "SMD 变体分支的数, 本单不换变体",
        "evidence": "[实测]"
      },
      {
        "key": "uart_max_copper_x_no_change",
        "value": "0.7400",
        "why_unchanged": "2.5400 - 2 x 0.9000",
        "evidence": "[推算]"
      },
      {
        "key": "opening_y_min_current_caliber",
        "value": "5.6000",
        "why_unchanged": "现状口径下若不要零余量: 2.8000 + 2 x 0.9000",
        "evidence": "[推算]"
      },
      {
        "key": "lib_courtyard_x_4pos",
        "value": "6.0900",
        "why_unchanged": "通用 KiCad 库件 F.CrtYd 图元 (rot 90 后板向 X); 厂件无此图元",
        "evidence": "[实测]"
      },
      {
        "key": "lib_courtyard_x_2pos",
        "value": "3.5500",
        "why_unchanged": "通用 KiCad 库件 F.CrtYd 退包络",
        "evidence": "[实测]"
      },
      {
        "key": "lib_courtyard_y",
        "value": "3.1000",
        "why_unchanged": "通用 KiCad 库件 F.CrtYd 另一轴",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_x_4pos",
        "value": "5.0800",
        "why_unchanged": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画); 与厂件同值属巧合",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_y_4pos",
        "value": "2.1000",
        "why_unchanged": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_x_2pos",
        "value": "2.5400",
        "why_unchanged": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_y_2pos",
        "value": "2.1000",
        "why_unchanged": "通用 KiCad 库件 F.Fab 几何外廓 (不含笔画)",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_x_2pos_incl_stroke",
        "value": "2.6400",
        "why_unchanged": "通用 KiCad 库件 F.Fab 含笔画口径 (笔画宽 0.1) => 口径产物",
        "evidence": "[实测]"
      },
      {
        "key": "lib_fab_y_incl_stroke",
        "value": "2.2000",
        "why_unchanged": "通用 KiCad 库件 F.Fab 含笔画口径 => 口径产物",
        "evidence": "[实测]"
      },
      {
        "key": "lib_drill",
        "value": "0.6500",
        "why_unchanged": "通用 KiCad 库件默认钻孔; 落厂件须改 0.71 但不进铜箔包络",
        "evidence": "[实测]"
      }
    ],
    "B_changed": [
      {
        "key": "seat_body_x_4pos",
        "old_value": "5.0800",
        "new_value": "5.0800",
        "delta": 0.0,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)",
        "note": "数值巧合不变 (通用库件 F.Fab 与厂件 N x 1.27 同值) => 掩盖了 X 方向的错; 出处改为厂件官网",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_x_2pos",
        "old_value": "2.5400",
        "new_value": "2.5400",
        "delta": 0.0,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)",
        "note": "库件几何 2.5400 (含笔画 2.6400) -> 厂件 2.5400; 若沿用含笔画口径则差 0.1000",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_y",
        "old_value": "2.1000",
        "new_value": "2.1600",
        "delta": 0.06000000000000005,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69/L90",
        "note": "通用库件 F.Fab 深 2.1000 -> 厂件官网 .085 2.16 REF",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "insulator_height_z",
        "old_value": "0.0000",
        "new_value": "0.8600",
        "delta": 0.86,
        "consumed_by": "MECH/check_debug_seat_3d_fit.py L876 (OI-11)",
        "note": "库件无绝缘体高 => 厂件 .034 0.86 REF; 主体是连接器元器件, 不许顶替结构件 h 三档",
        "evidence": "[官网]"
      },
      {
        "key": "post_height",
        "old_value": "0.0000",
        "new_value": "3.0500",
        "delta": 3.05,
        "consumed_by": "装配高度链 (本单未消费)",
        "note": "库件无柱高 => 厂件 -01: .120 [3.05] POST",
        "evidence": "[官网]"
      },
      {
        "key": "factory_drill",
        "old_value": "0.6500",
        "new_value": "0.7100",
        "delta": 0.05999999999999994,
        "consumed_by": "HW/check_fts_land_drill_same_batch.py",
        "note": "落厂件须改孔 0.65 -> 0.71; 不进铜箔包络 => 不进判决链",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_limit_x_debug",
        "old_value": "5.0800",
        "new_value": "5.0800",
        "delta": 0.0,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)",
        "note": "座体本体上限 (J_DEBUG): X 不变, Y 由 2.1000 -> 2.1600",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_limit_y_debug",
        "old_value": "2.1000",
        "new_value": "2.1600",
        "delta": 0.06000000000000005,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L69 (D-6)",
        "note": "座体本体上限 (J_DEBUG) 的 Y 项",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_limit_x_uart",
        "old_value": "2.6400",
        "new_value": "2.5400",
        "delta": -0.10000000000000009,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)",
        "note": "座体本体上限 (J_UART) 的 X 项; 原值是含笔画口径产物",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "seat_body_limit_y_uart",
        "old_value": "2.2000",
        "new_value": "2.1600",
        "delta": -0.040000000000000036,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)",
        "note": "座体本体上限 (J_UART) 的 Y 项; 原值是含笔画口径产物",
        "evidence": "[官网]+[实测]"
      },
      {
        "key": "allowance_per_side_uart_fab",
        "old_value": "0.7150",
        "new_value": "0.7650",
        "delta": 0.050000000000000044,
        "consumed_by": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L90 (U-7)",
        "note": "F.Fab 口径每边让位 (4.0700 - 2.6400)/2 -> (4.0700 - 2.5400)/2",
        "evidence": "[推算]"
      },
      {
        "key": "oi12_gap",
        "old_value": "0.5200",
        "new_value": "0.0000",
        "delta": -0.52,
        "consumed_by": "MECH/check_debug_seat_3d_fit.py L848/L879",
        "note": "OI-12 '判据偏紧 0.5200' 作废: 对照物 6.0900 是通用库件 courtyard, 不是厂件 keepout",
        "evidence": "[推算]"
      }
    ],
    "C_pending_main": [
      {
        "key": "required_clearance_x_debug_body",
        "current_value": "6.6100",
        "candidate_value": "6.8800",
        "question": "候选口径(罩座体本体): 厂件 FTS 座体宽 X 5.0800 (与通用 KiCad 库件同值属巧合) + 2 x 0.9000 => 6.8800 => 缺 0.2700",
        "decision_owner": "main/boss",
        "evidence": "[推算]"
      },
      {
        "key": "required_clearance_x_uart_body",
        "current_value": "4.0700",
        "candidate_value": "4.3400",
        "question": "候选口径(罩座体本体): 厂件 FTS 座体宽 X 2.5400 (通用 KiCad 库件含笔画口径是 2.6400) + 2 x 0.9000 => 4.3400 => 缺 0.2700",
        "decision_owner": "main/boss",
        "evidence": "[推算]"
      },
      {
        "key": "required_clearance_y_body",
        "current_value": "2.8000",
        "candidate_value": "3.9600",
        "question": "候选口径(罩座体本体): 厂件座体深 Y 2.1600 + 2 x 0.9000 => 3.9600 => 缺 1.1600 => 装不下",
        "decision_owner": "main/boss",
        "evidence": "[推算]"
      },
      {
        "key": "opening_y_min_body_caliber",
        "current_value": "4.6000",
        "candidate_value": "5.7600",
        "question": "候选口径下罩开口 Y 需 >= 3.9600 + 2 x 0.9000 = 5.7600 (现状口径下只需 5.6000, 差 0.1600)",
        "decision_owner": "main/boss",
        "evidence": "[推算]"
      },
      {
        "key": "max_housing_y_fits_opening",
        "current_value": "2.8000",
        "candidate_value": "2.8000",
        "question": "罩开口 Y 4.6000 最多可容 H_y 2.8000 (两口径同值) => 座体口径下装不下",
        "decision_owner": "main/boss",
        "evidence": "[推算]"
      },
      {
        "key": "seat_body_height_h_choice",
        "current_value": "0.0000",
        "candidate_value": "0.0000",
        "question": "结构件 h 三档 0.90/2.54/4.00 待裁; 厂件 Z 0.8600 是元器件绝缘体高, 主体不同, 不许顶替",
        "decision_owner": "main/boss",
        "evidence": "[0数据]+[推算]"
      }
    ]
  },
  "spread_sites": [
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 26,
      "marker": "官方 land 自己的",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): 2. ★**要让两件的罩住轴真正过阈, 清空区 X 宽需求**: `J_DEBUG` ≥ `6.6100` (铜箔 `4.8100` + 2 × `0.9000`) · `J_UART` ≥ `4.0700` (铜箔 `2.2700` + 2 × `0.9000`) ⇒ ★**注意 `6.6100` 比官方 land ",
      "id": "S-01",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900; 厂件 FTS 座体本体 5.0800 x 2.1600 (厂件无 courtyard 图元)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 114,
      "marker": "官方 land 自己的",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): 2. ★**要让罩住轴真正过阈, 清空区 X 宽必须 ≥ `4.8100 + 2 × 0.9000 = 6.6100`** ⇒ ★**★注意: 官方 land 自己的 `F.Fab` 旋转后是 `5.0800` X、`F.CrtYd` 是 `6.0900` X ⇒ 判据要求的 `6.6100` 比 courtyard ",
      "id": "S-02",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900; 厂件 FTS 座体本体 5.0800 x 2.1600 (厂件无 courtyard 图元)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 168,
      "marker": "官方 land 自己的",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | 官方 land 自己的 `F.Fab` `5.0800` X / `F.CrtYd` `6.0900` X (rot 90 后) | ★`[实测]` ★ | ISS-371 §0.1 (★解析 `.kicad_mod` 实读★) |",
      "id": "S-03",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900 (rot 90 后)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 193,
      "marker": "官方 land 的 `F.CrtYd`",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | ★**OI-12** ★ | ★**罩住判据对 THT 排针是否过严** (★判据要求清空区 `6.6100` > 官方 land 的 `F.CrtYd` `6.0900`) ★ | ★**main + boss 回答: 「⑤ 这条『铜箔必须被清空区罩住、每边 ≥ `CRIT`』对 THT 排针是不是过严?」** ",
      "id": "S-04",
      "new_text": "厂件 FTS 无 courtyard 图元 => OI-12 的对照物不存在 => 结论作废 (通用 KiCad 库件 F.CrtYd 6.0900 不是厂件 keepout)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 854,
      "marker": "官方 land 的 F.Fab",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"basis\": \"官方 THT 真 land 铜箔 X 4.8100 + 2 x (CRIT + TOL) 1.8000 = 6.6100; 而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200\",",
      "id": "S-05",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900; 厂件 FTS 座体本体 5.0800 x 2.1600 (厂件无 courtyard 图元)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "line": 897,
      "marker": "官方 1x4 THT 的 F.CrtYd",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"OI-12\": \"罩住判据 (座体必须清空区 vs 铜箔 每边 >= CRIT + TOL) 对 THT 排针是否过严 ⇒ to=main + boss (★事实: 官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200★)\"",
      "id": "S-06",
      "new_text": "厂件 FTS 无 courtyard 图元 => OI-12 的对照物不存在 => 结论作废 (通用 KiCad 库件 F.CrtYd 6.0900 不是厂件 keepout)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 69,
      "marker": "官方 1×4 THT 座体本体",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | `D-6` | ★**座体选型 / keepout** ★ | `[0数据]` (本机无厂商 keepout 图纸) ; 官方 1×4 THT 座体本体 (`F.Fab`) X `5.0800` × `2.1000` — `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L1",
      "id": "S-07",
      "new_text": "厂件 FTS-104-01-F-S 座体本体 5.0800 x 2.1600 [官网]; 通用 KiCad 库件 F.Fab 5.0800 x 2.1000 (不含笔画)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 90,
      "marker": "官方 1×2 THT 座体本体",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | `U-7` | ★**座体选型 / keepout** ★ | `[0数据]` (本机无厂商 keepout 图纸) ; 官方 1×2 THT 座体本体 (`F.Fab`) `2.6400` × `2.2000` — `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L118`",
      "id": "S-08",
      "new_text": "厂件 FTS-102-01-F-S 座体本体 2.5400 x 2.1600 [官网]; 通用 KiCad 库件 F.Fab 2.5400 x 2.1000 (不含笔画口径)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 114,
      "marker": "官方 land 自己的",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): 3. ★**要过罩住判据的清空区 X 宽需求 = 铜箔 `4.8100` + 2 × `0.9000` = `6.6100`** ⇒ ★**比官方 land 自己的 `F.CrtYd` `6.0900` 还大 `0.5200`** ⇒ `OI-12` (归 main + boss, 本单 §5 答) ★",
      "id": "S-09",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900; 厂件 FTS 座体本体 5.0800 x 2.1600 (厂件无 courtyard 图元)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 143,
      "marker": "官方 land 的 `F.CrtYd`",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | 官方 land 的 `F.CrtYd` (板向 X) | `6.0900` (★**真 `F.CrtYd` 图元**★) | `3.5500` (★**本封装无 `F.CrtYd` 图元, 是 `GetBoundingBox` 退包络**★) | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CL",
      "id": "S-10",
      "new_text": "通用 KiCad 库件 F.CrtYd (板向 X) 6.0900 / 退包络 3.5500",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 149,
      "marker": "IPC 的 courtyard",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): ★**⇒ 结构侧的答复 (★只摆事实与两条路, 不代裁★)★**: ★**这条判据要的不是「座体放得下」, 而是「座体 + 每边 `0.9000` 的空气带」; IPC 的 courtyard 给的是器件本体加倒角, 本来就不含装配空气带 ⇒ 对 THT 排针说它「过严」在口径上站得住 ⇒ 但它在数字上是【硬差额 `0",
      "id": "S-11",
      "new_text": "通用 KiCad 库件的 F.CrtYd 是库件包络, 不是厂件 keepout",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 154,
      "marker": "比 courtyard `6.0900` 还小",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): | ★**路 B — 判据改口径 (名义余量)** ★ | 「名义余量 ≥ `CRIT`」(不扣 `TOL`) | `J_DEBUG` `6.0100` · `J_UART` `3.4700` | `J_DEBUG` `(6.0100 − 5.0800)/2 = 0.4650` · `J_UART` `(3.4700 ",
      "id": "S-12",
      "new_text": "通用 KiCad 库件 F.CrtYd 6.0900",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 513,
      "marker": "官方 1x4 THT 座体本体",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"current_text\": \"[0数据] 无厂商 keepout 图纸; 官方 1x4 THT 座体本体 F.Fab X 5.0800 x 2.1000\",",
      "id": "S-13",
      "new_text": "厂件 FTS-104-01-F-S 座体本体 5.0800 x 2.1600 [官网]; 通用 KiCad 库件 F.Fab 5.0800 x 2.1000 (不含笔画)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 594,
      "marker": "官方 1x2 THT 座体本体",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"current_text\": \"[0数据] 无厂商 keepout 图纸; 官方 1x2 THT 座体本体 F.Fab 2.6400 x 2.2000\",",
      "id": "S-14",
      "new_text": "厂件 FTS-102-01-F-S 座体本体 2.5400 x 2.1600 [官网]; 通用 KiCad 库件 F.Fab 2.5400 x 2.1000 (不含笔画)",
      "status": "registered"
    },
    {
      "file": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md",
      "line": 634,
      "marker": "官方 land courtyard",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"structural_answer\": \"硬差额: 判据要求每边 0.9000, 官方 land courtyard 只给每边 0.6400 (J_DEBUG F.CrtYd 6.0900 vs 铜箔 4.8100; J_UART 退包络 3.5500 vs 铜箔 2.2700) => 每边差 0.2600, 清空区",
      "id": "S-15",
      "new_text": "通用 KiCad 库件 F.CrtYd 口径下的差额, 不等于厂件 keepout 口径 => 硬差额不成立, OI-12 结论作废",
      "status": "registered"
    },
    {
      "file": "MECH/check_debug_seat_3d_fit.py",
      "line": 848,
      "marker": "官方 land 的 F.Fab",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200\",",
      "id": "S-16",
      "new_text": "通用 KiCad 库件 PinHeader_1x04_P1.27mm_Vertical 的 F.Fab 5.0800 / F.CrtYd 6.0900; 厂件 FTS 座体本体 5.0800 x 2.1600 (厂件无 courtyard 图元)",
      "status": "registered"
    },
    {
      "file": "MECH/check_debug_seat_3d_fit.py",
      "line": 879,
      "marker": "官方 1x4 THT 的 F.CrtYd",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): \"(★事实: 官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200★)\",",
      "id": "S-17",
      "new_text": "厂件 FTS 无 courtyard 图元 => OI-12 的对照物不存在 => '判据偏紧 0.5200' 结论作废 (通用 KiCad 库件 F.CrtYd 6.0900 不是厂件 keepout)",
      "status": "registered"
    },
    {
      "file": "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md",
      "line": 190,
      "marker": "官方 land courtyard",
      "text": "通用 KiCad 库件原文(误认, 待 main 落订正): - ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` ★**OI-5** (清空区 X 三档 `1.7750` / `4.0850` / `4.8100`) 与 ★**OI-12** (`6.6100` vs 官方 land courtyard `6.0900` ⇒ 「偏紧」结论的对",
      "id": "S-18",
      "new_text": "通用 KiCad 库件 F.CrtYd 6.0900 (不是厂件 courtyard); 厂件 FTS 无 courtyard",
      "status": "registered"
    }
  ],
  "y_direction_gap": {
    "caliber_copper": {
      "body_y": "2.1600",
      "required_clearance_y": "2.8000",
      "max_housing_y_fits": "2.8000",
      "gap": "0.0000",
      "worst_margin": "0.6000",
      "verdict": "恰好卡死 (零制造余量) 但几何成立 => OI-13 选项存在"
    },
    "caliber_seat_body": {
      "body_y": "2.1600",
      "required_clearance_y": "3.9600",
      "max_housing_y_fits": "2.8000",
      "gap": "1.1600",
      "worst_margin": "-0.3000",
      "cover_opening_y_min": "5.7600",
      "verdict": "装不下 (差一截, 不是压线) => OI-13 选项消失"
    },
    "gap_formula": "gap = (body_y + 2 x (CRIT + TOL)) - (cover_opening_y - 2 x (CRIT + TOL)) = 3.9600 - 2.8000 = 1.1600",
    "crit": "0.6000",
    "tol_fdm_part": "0.3000",
    "margin_per_side": "0.9000"
  },
  "degradation": {
    "primary_path": "官网机械/营销图 (Samtec FTS) 文字层逐字值",
    "pdf": "tmp/iss393_sbx/fts-1xx-xx-x-sx-mkt.pdf",
    "pdf_md5": "69d9415867cd642d6a6e07c6b755516b",
    "pdf_text_layer": [
      "(NO OF POS x .0500 [1.27])",
      ".085 2.16 REF",
      ".034 0.86 REF",
      ".050 1.27 REF",
      "-01: .120 [3.05] POST"
    ],
    "gap": "REF 尺寸未给公差带 => 座体深 Y 2.1600 / 绝缘体高 Z 0.8600 的实际公差未知",
    "fallback_action": "落 FTS 时先打一块单板样 (只一块) + 卡尺量三个量: 座体宽 X / 座体深 Y / 绝缘体高 Z",
    "measure_fill_back": [
      "dimensions.seat_body_x_4pos.measured",
      "dimensions.seat_body_y.measured",
      "dimensions.insulator_height_z.measured"
    ],
    "when": "板只改一次那一趟投板前",
    "who": "mech-lead 收样后量, hw-lead 提供样件与读数记录",
    "rule": "|实测 - 2.1600| <= 0.0500 则直接用 2.1600, 否则以实测为准并回写 §6",
    "forbidden_wording_source": "MECH/check_fts_vs_generic_courtyard_delta.py 的 PENDING 词表 (本页不复制禁语原文)"
  },
  "consumed_quantities": {
    "0.0000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190"
    ],
    "0.0100": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76"
    ],
    "0.1350": [
      "check_debug_seat_3d_fit.py:799",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:22",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814"
    ],
    "0.1650": [
      "check_debug_seat_3d_fit.py:799",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814"
    ],
    "0.2100": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20"
    ],
    "0.3000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20"
    ],
    "0.3100": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20"
    ],
    "0.3625": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:640"
    ],
    "0.4700": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:27",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:143",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847"
    ],
    "0.5200": [
      "check_debug_seat_3d_fit.py:848",
      "check_debug_seat_3d_fit.py:879",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:193",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:897"
    ],
    "0.6000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864"
    ],
    "0.6625": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109"
    ],
    "0.7250": [
      "check_debug_seat_3d_fit.py:740",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:640"
    ],
    "0.7300": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824"
    ],
    "0.7400": [
      "check_debug_seat_3d_fit.py:859",
      "check_debug_seat_3d_fit.py:860",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:180",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:180",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:873",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:874"
    ],
    "0.7700": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:27",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:143",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847"
    ],
    "0.7750": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:162"
    ],
    "0.7900": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76"
    ],
    "0.9000": [
      "check_debug_seat_3d_fit.py:809",
      "check_debug_seat_3d_fit.py:839",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:162",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:162",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:167",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:178",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:180",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847"
    ],
    "1.0000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:84",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:163",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:163",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847"
    ],
    "1.0300": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824"
    ],
    "1.0900": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20"
    ],
    "1.4950": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115"
    ],
    "1.5175": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:22",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:50",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:627"
    ],
    "1.5300": [
      "check_debug_seat_3d_fit.py:856",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:865"
    ],
    "1.7750": [
      "check_debug_seat_3d_fit.py:37",
      "check_debug_seat_3d_fit.py:731",
      "check_debug_seat_3d_fit.py:849",
      "check_debug_seat_3d_fit.py:872",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:22",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:103",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:162",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:178",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:855",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:894"
    ],
    "1.7950": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115"
    ],
    "1.8000": [
      "check_debug_seat_3d_fit.py:847",
      "check_debug_seat_3d_fit.py:853",
      "check_debug_seat_3d_fit.py:860",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:874"
    ],
    "1.8175": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108"
    ],
    "1.9200": [
      "check_debug_seat_3d_fit.py:861",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:180",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:874"
    ],
    "10.2000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115"
    ],
    "14.6900": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824"
    ],
    "17.9650": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93"
    ],
    "18.8900": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93"
    ],
    "18.9350": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93"
    ],
    "19.0350": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93"
    ],
    "2.2700": [
      "check_debug_seat_3d_fit.py:798",
      "check_debug_seat_3d_fit.py:799",
      "check_debug_seat_3d_fit.py:800",
      "check_debug_seat_3d_fit.py:853",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:84",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:163",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864"
    ],
    "2.3950": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115"
    ],
    "2.5250": [
      "check_debug_seat_3d_fit.py:740",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:640"
    ],
    "2.5400": [
      "check_debug_seat_3d_fit.py:799",
      "check_debug_seat_3d_fit.py:799",
      "check_debug_seat_3d_fit.py:856",
      "check_debug_seat_3d_fit.py:860",
      "check_debug_seat_3d_fit.py:860",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:22",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:76",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:84",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:84",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:180",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:865",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:874",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:874"
    ],
    "2.6950": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115"
    ],
    "2.8000": [
      "check_debug_seat_3d_fit.py:839",
      "check_debug_seat_3d_fit.py:866",
      "check_debug_seat_3d_fit.py:866",
      "check_debug_seat_3d_fit.py:880",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:27",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:27",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:143",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:143",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:181",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:194",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:884",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:884",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:898"
    ],
    "3.0350": [
      "check_debug_seat_3d_fit.py:738",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:627"
    ],
    "3.4700": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864"
    ],
    "4.0700": [
      "check_debug_seat_3d_fit.py:800",
      "check_debug_seat_3d_fit.py:852",
      "check_debug_seat_3d_fit.py:853",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:93",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:94",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:167",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:179",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:814",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:863",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:864"
    ],
    "4.0850": [
      "check_debug_seat_3d_fit.py:37",
      "check_debug_seat_3d_fit.py:872",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:103",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:894"
    ],
    "4.6000": [
      "check_debug_seat_3d_fit.py:839",
      "check_debug_seat_3d_fit.py:839",
      "check_debug_seat_3d_fit.py:866",
      "check_debug_seat_3d_fit.py:867",
      "check_debug_seat_3d_fit.py:880",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:27",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:143",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:181",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:181",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:194",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:847",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:884",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:885",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:898"
    ],
    "4.8100": [
      "check_debug_seat_3d_fit.py:37",
      "check_debug_seat_3d_fit.py:734",
      "check_debug_seat_3d_fit.py:738",
      "check_debug_seat_3d_fit.py:740",
      "check_debug_seat_3d_fit.py:846",
      "check_debug_seat_3d_fit.py:847",
      "check_debug_seat_3d_fit.py:872",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:3",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:20",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:103",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:163",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:178",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:190",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:627",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:640",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:853",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:894"
    ],
    "4.8350": [
      "check_debug_seat_3d_fit.py:738",
      "check_debug_seat_3d_fit.py:849",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:178",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:627",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:855"
    ],
    "5.0800": [
      "check_debug_seat_3d_fit.py:848",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:168",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854"
    ],
    "5.6000": [
      "check_debug_seat_3d_fit.py:867",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:181",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:181",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:194",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:885"
    ],
    "6.0900": [
      "check_debug_seat_3d_fit.py:848",
      "check_debug_seat_3d_fit.py:879",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:168",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:193",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:897"
    ],
    "6.6100": [
      "check_debug_seat_3d_fit.py:738",
      "check_debug_seat_3d_fit.py:740",
      "check_debug_seat_3d_fit.py:846",
      "check_debug_seat_3d_fit.py:847",
      "check_debug_seat_3d_fit.py:879",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:26",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:108",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:109",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:114",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:115",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:167",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:178",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:193",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:627",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:640",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:853",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:854",
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:897"
    ],
    "67.2000": [
      "BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:824"
    ]
  },
  "excluded_quantities": {
    "0.0100": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.1650": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.2100": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.3100": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.3625": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.6625": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.7250": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.7300": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.7750": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "0.7900": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.0300": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.0900": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.4950": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.5175": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.5300": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.7950": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.8000": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "1.8175": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "10.2000": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "14.6900": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "17.9650": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "18.8900": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "18.9350": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "19.0350": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关",
    "2.3950": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "2.5250": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "3.0350": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "3.4700": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "4.8350": "派生余量/差额: 由本表已有量 (铜箔/清空区/开口/判据余量) 直接相减得到, 不引入新对照物",
    "67.2000": "落点绝对坐标, 随清空区中心移动, 与厂件外形无关"
  },
  "criterion_source": "MECH/check_debug_seat_3d_fit.py L890-L891; CRIT/TOL 真身 MECH/service_port_check.py L126-L127"
}
```
