# MECH · 「板只改一次」那一趟的 MECH 侧板侧输入清单 (机器可读) —— ISS-278

> **单**: ISS-278 (owner=mech-lead · 派活 2026-11-17 07:3x · cron `fb67af40`)
> **性质**: ★**内部活 · MECH 侧 · 纯分析 + 规格页订正 + 机器闸类 · 零写板 · 零落表 · 零改既有 MECH 判据脚本** ★
> **机器闸**: `python3 MECH/check_onepass_mech_sync.py` (★M1 帧标签 / M2 两条开口各自不压 SoM 座 / M3 座体高度参数式自洽 / M4 判据命令真存在 / M5 受保护 5 件 md5 逐字节不变★)
> **自检**: `python3 MECH/check_onepass_mech_sync.py --selftest` (★≥5 条反向用例, 每条自证真改到目标★)
> **实算源**: `logs/iss278/compute_iss278.py` (★只读 import `MECH/check_board_frame_coords.py` + `MECH/board_port_opening_s6_check.py` ⇒ 阈值零漂移★) ⇒ 产物 `logs/iss278/compute_iss278.json`
> **上游**: ISS-276 (★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · 坐标系归一 · 本页不重做, 只在其上补 4 条★) · ISS-271 / ISS-267 / ISS-273 / ISS-274
> **一句话**: ★**把「板只改一次」那一趟要用的 MECH 侧输入收成【一份规格 + 一道闸】: 检修口/调试口拆成两条独立规格 · 座体高度参数化 + 三档假设 · LED 光孔两假设 + 降级 · 连接器参数对照表** ★

---

## ★§1 坐标系声明 (★置顶 · 本页一切数都挂在这句下面★)

> ★★**本页一切坐标 = 现役台架板 160×100 坐标**★★
> ★**帧 id = `B160x100`** ★ — ★**帧 id 的唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 的 JSON 块 `cal:FRAMES` (★ISS-274 · hw-lead 出★) ⇒ 本页帧 id 与那个权威表【逐字对齐】, 两边不得各用一套** ★
> ★**帧 id 三件套**: `B160x100` = 160×100 台架板帧 (★现役板 · 本页口径★) · `F30A` = 60×30 套A 帧 (`MECH/BOARD_GEOM_30MM.md`) · `P60x15` = 60×15 帧
> ★**基准 = `HW/PCB/demo_mainboard.kicad_pcb` 的 `Edge.Cuts` 中心线包围盒: X 0.00..160.00 × Y 0.00..100.00 ⇒ 160.00 × 100.00 mm** ★
> ★**(`Edge.Cuts` 描边宽 0.10 ⇒ 笔画外缘 = 160.10 × 100.10; 落件坐标一律按中心线 0..160 / 0..100 记★)** ★
> ★**与 `MECH/BOARD_GEOM_30MM.md` 的 `F30A`(60×30 套A) 坐标【不是同一套】⇒ 两套数不可互相代入** ★ (★与 ISS-274 / ISS-276 同源口径★)
> ★**与 `MECH/BOARD_GEOM_30MM.md` 的 RK3576 老基线 —— 本页只【引用】, 一个字不改 (归 main 裁决)★** ★

### ★§1.1 本页与 ISS-276 归一页的关系 (★别再搞混★)

| 项 | 属于哪一页 | 能不能互相代入 |
|---|---|---|
| ★**帧声明 + 帧 id + 基准框** | ISS-276 归一页 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §1 | ★**逐字一致** (本页 §1 是它的引用, 不是另一套) ★ |
| ★**两条开口的可放行空间 (§3b) / 座体高度参数化 (§4b) / LED 两假设 (§6b) / 连接器对照表 (§7b)** | ★**本页 (ISS-278)** ★ | —— |
| ★**ISS-271 交的两个旧矩形 (60×30 套A 坐标)** | 帧: `F30A` | ★**否 —— 照字面抄进现役板 = 开工即撞 SoM 座 (56 / 10 个焊盘)★** ★ |

★**⇒ 本页不是重做 ISS-276, 是在它之上补 4 条 + 加一道覆盖度闸** ★

### ★§1.2 证据分级 (★本页每个结论都带级★)

| 证据级 | 本页的含义 |
|---|---|
| ★`[实测]` ★ | ★**盘上文件实读 + 脚本实跑** (读 `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard_params.json` / 网表 / BOM 读到才写) ★ |
| ★`[推算]` ★ | ★**设计态几何 + 公差栈** (由 `[实测]` 的输入 + 既有闸脚本常量推导) ★ |
| ★`[0数据]` ★ | ★**本机查不到 ⇒ 本页不给数, 只给参数式 + 三档 + 降级方案** ★ |
| ★`[官网]` / ★`[媒体]` ★ | ★**本页 0 条** (★本单零外发、零询价、零问询; 缺口一律自己网上查, 查不到写 `[0数据]`★) ★ |
| ★**实物 `[实测]` = 0 条** | ★**本机无板、无实物 ⇒ 本页一切「实测」= 文件实读 + 脚本实跑** ★ |

---

## ★§2 逐条表 (★MECH 侧板侧输入 · 8 字段固定★)

> ★**字段口径**: `id` = 条目号 · `source_iss` = 来源单 · `title` = 标题 · `current_state` = 现状 (**必带证据等级**) · `spec` = 那一趟要用的规格值/参数式 · `criterion` = 判据命令 + 期望 rc/值 (**必须是本机真命令**) · `blocked_by` = 阻塞前置 + 谁拍 · `evidence` = 证据清单 ★
> ★**机器可读 JSON 块在 §5 (★同一份数据的机器版; 改数必须两处一起改, 机器闸 M1~M5 会查§)** ★

### ★§2.1 开口两条 + 合并禁令 + 座体高度 (★帧: 160×100 台架板★)

| id | source_iss | title | current_state (帧: 160×100 台架板) | spec | criterion | blocked_by | evidence |
|---|---|---|---|---|---|---|---|
| ★`MECH-PORT-DEBUG` ★ | ISS-278 | ★**调试口开口 (罩 `J_DEBUG`)** ★ | ★**盘上实物 `J_DEBUG` @ (144.30, 58.00), 4 焊盘 (1×4 @0.50), 铜箔 X 142.063..143.838 × Y 56.150..57.050** ★ | ★**开口 (h=2.54 档) = X 137.850..148.050 × Y 54.300..58.900** ★ · 左下角可放行 X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330] · 座体宽 1.775 (板读铜箔宽) · 单边间隙 X 4.2125 / Y 1.0300 (最坏 3.9125 / 0.7300 ≥ CRIT 0.60) ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0; M2 调试口压 `J_SOM_P1..P4` 焊盘数 = 0** ★ | ★**无 (可直接抄进作业包)** ★ | ★`[实测]` (板读) + `[推算]` (间隙) ★ |
| ★`MECH-PORT-UART` ★ | ISS-278 | ★**检修口开口 (罩 `J_UART`)** ★ | ★**盘上实物 `J_UART` @ (20.74, 70.00), 2 焊盘 (1×2 @0.50), 铜箔 X 18.502..19.277 × Y 68.150..69.050** ★ | ★**开口 (h=2.54 档) = X 13.790..23.990 × Y 66.300..70.900** ★ · 左下角可放行 X0 ∈ [13.790, 17.620] · Y0 ∈ [66.300, 67.330] · 座体宽 2.540 (★MECH 现行模型硬编; 板读铜箔宽只有 0.775★) · 单边间隙 X 3.8300 / Y 1.0300 (最坏 3.5300 / 0.7300 ≥ 0.60) ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0; M2 检修口压 `J_SOM_P1..P4` 焊盘数 = 0** ★ | ★**无** ★ | ★`[实测]` (板读) + `[推算]` (间隙) + ★`[0数据]` (座体真实宽高) ★ |
| ★`MECH-PORT-USBC` ★ | ISS-294 | ★**USB-C 边开口 (罩 `J_USB_C` · 板边缺口 · 插头从板边进出)** ★ | ★**`J_USB_C` @ (140.000, 5.250); 座体 `F.Fab` X 135.680..144.320 × Y 0.000..6.400 (8.640 × 6.400) ⇒ **Y 下沿 = 0.000 = 板边**; `F.CrtYd` X 135.180..144.820 × Y −0.500..6.900; 两个 NPTH @ (134.220, 2.625) / (145.780, 2.625), pad Ø0.65 / **drill Ø0.762**; 插头面与板边齐平 (`state/usb_c_footprint.py` 定位口径)** ★ | ★**边开口 (板边缺口, ★**另一侧是板外** ⇒ 不许按「罩住器件的洞」写★) = X 132.995..147.005 × Y 0.000..7.300** ★ · ★**必须清空区 = 座体 `F.Fab` ∪ 两个固定孔外缘 = X 133.895..146.105 × Y 0.000..6.400** ★ · 单边净距 X 0.900 / Y 0.900 (最坏 0.600 = CRIT, ★**刚好过**★) · ★**缺口 Y 向深度由座体平面尺寸支配 (6.400 + 0.900 = 7.300) ⇒ 不随 h 变; 三档 (0.90/2.54/4.00) 板面矩形同值, 随 h 变的是 Z 向窗口 `OPEN_Y_eff(h)` = 4.60/4.60/5.80** ★ · 立柱/螺钉头外扩三档见 §11.4 | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0** (M2 集合断言 = 恰好三条 + M2b 任意两条矩形不许完全相同 + M3 边开口逐档验) ★**+ `python3 MECH/check_onepass_struct_crosscheck.py` ⇒ rc=0** (N3 三条分别验, 第三条 `PORT_OPEN_USBC` 逐档进循环 + N4 `MC_USBC` 净距) | ★**结构开口尺寸 = 归 main→boss 拍** (★本单只交几何 + 代价 + 建议, 不代拍★); ★**立柱/螺钉头外径 = `[0数据]`** (固定方式未定 ⇒ 缺口 X 还须按 §11.4 三档外扩) | ★`[实测]` (板读 `F.Fab`/`F.CrtYd`/焊盘/NPTH + `state/usb_c_footprint.py` 定位口径) + `[推算]` (净距与开口宽) + `[0数据]` (座体真实高 h / 立柱外径) |
| ★`MECH-PORT-NOMERGE` ★ | ISS-278 | ★**两条开口【必须分开】(合并几何上不可能)** ★ | ★**`J_DEBUG` ↔ `J_UART` ΔX = 123.56 / ΔY = −12.00 / 直线 = 124.141345 mm** ★ | ★**合并开口禁止**: 两座体必须清空区并集宽 **126.2175 mm** vs 开口宽 10.20 ⇒ 单边间隙 **(10.20 − 126.2175)/2 = −58.00875** ⇒ ★**缺口 116.0175 mm** ★ ⇒ ★**判红 (不是「还没想好」, 是几何不成立)** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0; 机器块 `merged_opening.forbidden = true` 且 `gap_mm` = 116.0175** ★ | ★**无 (机械事实)** ★ | ★`[实测]` ★ |
| ★`MECH-BODY-H` ★ | ISS-278 | ★**座体真实高度参数化 (★不许把 2.54 当事实★)** ★ | ★**座体真实高度 = `[0数据]`** ★ (★本机无实物, 打印/量测全部 `[0数据]`★) ⇒ ★**现行 `BASE['jd_body_h']` = 2.54 是假设, 不是事实** ★ | ★**开口 Y 公式: `OPEN_Y_eff(h) = max(4.60, h + 2×(0.60 + 0.30)) = max(4.60, h + 1.80)`; 开口 Y = [cy − OPEN_Y_eff/2, cy + OPEN_Y_eff/2]** ★ · ★**h 三档: h_lo = 0.90 (座体不可能低于焊盘铜箔高) · h_ref = 2.54 (现行假设) · h_hi = 4.00 (板自己给连接器占的 `F.Fab` 盒高)★** · ★**代入结果: h=0.90 ⇒ 开口 Y 仍 4.60 (间隙 1.8500) · h=2.54 ⇒ 4.60 (间隙 1.0300) · h=4.00 ⇒ 5.80 (间隙 0.9000, 最坏 0.6000 = CRIT 刚好过); 三档全部落板框内 + 压 SoM 焊盘数 = 0** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0; M3 三档逐档: 开口 Y 单调 + 落板框内 + 不压 SoM** ★ | ★**座体型号/高度定版 = 归 hw-lead 选型 + boss 拍; ★本机不可得 ⇒ 降级方案 = 【参数式 + 三档 + 板那一趟按公式取值】(★不许挂成「等外部回复」★)** ★ | ★`[0数据]` (h) + `[推算]` (三档代入) + ★`[实测]` (档位上下界的物理锚点: 铜箔高 0.90 / `F.Fab` 盒高 4.00) ★ |

### ★§2.2 LED 光孔两假设 + 走线 + 连接器参数 (★帧: 160×100 台架板★)

| id | source_iss | title | current_state (帧: 160×100 台架板) | spec | criterion | blocked_by | evidence |
|---|---|---|---|---|---|---|---|
| ★`MECH-LED-G` ★ | ISS-278 | ★**`D_LED_G` 落位空间 + 有/无结构光孔两假设** ★ | ★**`D_LED_G` @ (101.25, 56.80) · `R_LED_G` @ (5.90, 62.50) · `LED_G_D` 走线 93.492727 mm (Δx 93.30 / Δy −6.00)** ★ · ★**结构光孔位置 = `[0数据]`** ★ | ★**假设 A (有结构光孔)**: 光孔把 LED 钉死 ⇒ 可放行空间 = 最近落位带 **X 6.940..8.250 × Y 63.700..67.900** (且 LED 中心 X 必须 = 光孔中心 X) ⇒ `LED_G_D` **0.450~0.965 mm** (净距 0.00/0.10/0.20/0.50 四档); ★**板面落位要改** ★ · ★**假设 B (无结构光孔)**: LED 位置只受电气+机械约束 ⇒ 可放行空间 = 整高自由带 **X 1.550..3.450 (宽 1.900)** + **X 72.540..73.660 (宽 1.120)**, Y 1.450..98.950, 可落位块 1992/2016/2031/2075 (净距 0.00/0.10/0.20/0.50) ⇒ `LED_G_D` 可压到 0.450~0.965, 但**现状 93.492727 也合法** ⇒ ★**板面落位不用改** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0; §5 机器块 `led.hypothesis_hole` / `led.hypothesis_nohole` 两份空间齐全** ★ | ★**结构光孔有/无 = 归 main→boss 拍 (★只列事实与代价, 本单不代拍★)** ★ | ★`[实测]` (板读坐标/走线) + ★`[推算]` (两假设空间) + ★`[0数据]` (光孔位置/有无) ★ |
| ★`MECH-LED-GD-NET` ★ | ISS-278 | ★**`LED_G_D` 走线长度 (根因 = 排版规则, 不是单个坐标)** ★ | ★**93.492727 mm (现状, 实测)** ★ · 根因 = `R_LED_G` 被放进 X = 5.90 的「左侧 I2C 上拉列」, `D_LED_G` 被放进 Y = 56.80 的「LED 行」 ⇒ 两件分居板子两端 | ★**目标: `LED_G_D` < 1 mm** ⇒ 净距 0.00 ⇒ 0.450 / 0.10 ⇒ 0.559 / 0.20 ⇒ 0.680 / 0.50 ⇒ 0.965 (★四档都能压进 1 mm★) ⇒ 省 92.53~93.04 mm ★ | ★**`python3 MECH/board_port_opening_s6_check.py --json` ⇒ rc=0 (★现值别改★) + `python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0** ★ | ★**最终 `D_LED_G` 坐标 = 归 hw-lead (PCB 布局); 本单只给空间与条件** ★ | ★`[实测]` + `[推算]` ★ |
| ★`MECH-CONN-PARAMS` ★ | ISS-278 | ★**连接器占位参数对照表 (`demo_mainboard_params.json` vs 落表板)** ★ | ★**params 与落表板【对不上】** ★ (★详见 §7b 对照表: 位号名 / 脚数 / 间距 / 位置 全部有差★) | ★**MECH 期望的连接器占位参数 = 见 §7b 对照表「MECH 期望值」列** ★ (★**以落表板实读为真源**; params 那一列是【要改成什么】, 不是【现状】★) | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0 (M4 判据命令真存在) + `python3 state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md` ⇒ rc=0** ★ | ★**归 hw-lead 改 `HW/PCB/demo_mainboard_params.json` (★ISS-277 同批在做板侧清单★) ⇒ ★**转 main 转交; 本单一个字不许改 `HW/`** ★ | ★`[实测]` (板读 + params 读) ★ |
| ★`MECH-LED-BRIGHT-G5` ★ | ISS-278 | ★**亮度档 G-5 (★改了 ⇒ 板要改第二次★)** ★ | ★**绿灯亮度档 = `[0数据]`** ★ · 现状 `R_LED_G` 与 `D_LED_G` 已在板上 (★`[实测]`★) | ★**不改 ⇒ 零板面动作** ★ · ★**改 ⇒ 改串阻值 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位 ⇒ 【板要改第二次】** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0 (登记在案即可, 本单不代拍)** ★ | ★**归 main→boss 拍** ★ | ★`[0数据]` (亮度档) + ★`[实测]` (现状器件在板) ★ |
| ★`MECH-LED-HOLE` ★ | ISS-278 | ★**结构光孔有/无 (板面落位的前置条件)** ★ | ★**结构光孔 = `[0数据]`** ★ | ★**两种假设的可放行空间见 `MECH-LED-G` 条 (假设 A / 假设 B)** ★ ⇒ ★**在拍板之前, 板那一趟只能按假设 B 落位 (不挪 `D_LED_G`), 假设 A 一旦成立就要挪 ⇒ 所以这条必须排在「板只改一次」之前拍** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0** ★ | ★**归 main→boss 拍** ★ | ★`[0数据]` ★ |

---

## ★§3 MECH → HW 的输入清单 (★hw-lead 那一趟要按什么值画★)

> ★**本节的每一条都会直接变成 hw-lead 落在板上的坐标/封装 ⇒ 必须【可直接被抄进作业包】⇒ 规格 + 判据 + 证据等级, 三样齐全** ★
> ★**本节一个字都没写进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★那是 hw-lead 的文件★); hw-lead 同批在做 ISS-281 (会动那个文件) ⇒ 两边各写各的, 只交叉引用** ★

### ★§3.1 给 hw-lead 的开口输入 (★帧: 160×100 台架板★)

| # | hw-lead 那一趟要按什么值画 | 本机实测依据 (帧: 160×100 台架板) |
|---|---|---|
| ★1 ★ | ★**调试口开口 = X 137.850..148.050 × Y 54.300..58.900 (罩 `J_DEBUG`)** ★ | ★**板读 `J_DEBUG` @ (144.30, 58.00) · 4 焊盘 1×4 @0.50 · 铜箔宽 1.775** ★ |
| ★2 ★ | ★**检修口开口 = X 13.790..23.990 × Y 66.300..70.900 (罩 `J_UART`)** ★ | ★**板读 `J_UART` @ (20.74, 70.00) · 2 焊盘 1×2 @0.50** ★ |
| ★3 ★ | ★**两条必须分开画, 不许合并成一个矩形** ★ | ★**ΔX 123.56 / 直线 124.141345 mm ⇒ 合并缺口 116.0175 mm ⇒ 几何不成立** ★ |
| ★4 ★ | ★**开口 Y 按公式取值, 不要写死 4.60**: `OPEN_Y_eff(h) = max(4.60, h + 1.80)` (★h = 座体真实高★) ★ | ★**h = `[0数据]`; 三档代入见 §4.2 表** ★ |
| ★5 ★ | ★**开口定档宽 10.20 (X) 不许改** ★ | ★**`MECH/SERVICE_PORT_ISS092.md` §4.1 (帧无关, 两套坐标通用)** ★ |
| ★6 ★ | ★**两条开口压住 `J_SOM_P1..P4` 焊盘数必须 = 0 (两条分别验)** ★ | ★**SoM 承载区 保守包络 X 13.650..70.350 × Y 7.610..54.390 (板读, 400 焊盘)** ★ |
| ★7 ★ | ★**USB-C 边开口 (罩 `J_USB_C`, 板边缺口) = X 132.995..147.005 × Y 0.000..7.300; 必须清空区 = X 133.895..146.105 × Y 0.000..6.400 (座体 `F.Fab` ∪ 两个固定孔外缘)** ★ | ★**板读 `J_USB_C` 座体 `F.Fab` X 135.680..144.320 × Y 0.000..6.400 (Y 下沿 = 板边) + 两个 NPTH @ X 134.220 / 145.780 (外缘 133.895..146.105)** ★ |

### ★§3.2 给 hw-lead 的 LED 输入 (★帧: 160×100 台架板★)

| # | hw-lead 那一趟要按什么值画 | 本机实测依据 (帧: 160×100 台架板) |
|---|---|---|
| ★7 ★ | ★**`D_LED_G` 落位窗口 = 整高自由带 X 1.550..3.450 (宽 1.900) + X 72.540..73.660 (宽 1.120), Y 1.450..98.950** ★ | ★**板读 + 净距 0 口径实算 (`MECH/check_board_frame_coords.py` 的 `led_space`)** ★ |
| ★8 ★ | ★**`D_LED_G` 若要与 `R_LED_G` 相邻 ⇒ 最近落位带 X 6.940..8.250 × Y 63.700..67.900 (封装原点窗口)** ★ | ★**同上班读; 走线 0.450~0.965 mm (净距 0.00~0.50)** ★ |
| ★9 ★ | ★**`LED_G_D` 网两端 = `R_LED_G`.2 (7.50, 62.60) ↔ `D_LED_G`.1 (100.80, 56.60)** ★ | ★**板读 (现状 93.492727 mm)** ★ |
| ★10 ★ | ★**若结构光孔成立 ⇒ `D_LED_G` 中心 X 必须 = 光孔中心 X (★光孔 = `[0数据]` ⇒ 板那一趟按「不挪」画, 挪要等拍板★)** ★ | ★**`[0数据]`** ★ |

### ★§3.3 给 hw-lead 的连接器占位输入 (★帧: 160×100 台架板★)

| # | hw-lead 那一趟要按什么值画 | 本机实测依据 (帧: 160×100 台架板) |
|---|---|---|
| ★11 ★ | ★**`J_DEBUG` = 1×4 @0.50 排针, 铜箔 1.775 × 0.900, 位置 (144.30, 58.00)** ★ | ★**板读 (铜箔 X 142.063..143.838 × Y 56.150..57.050)** ★ |
| ★12 ★ | ★**`J_UART` = 1×2 @0.50 排针, 铜箔 0.775 × 0.900, 位置 (20.74, 70.00)** ★ | ★**板读 (铜箔 X 18.502..19.277 × Y 68.150..69.050)** ★ |
| ★13 ★ | ★**`J_USB_C` = Type-C 16p 座 @ (140.000, 5.250)** ★ | ★**板读** ★ |
| ★14 ★ | ★**SoM 承载区 = `J_SOM_P1..P4` 四组各 100 焊盘, 保守包络 X 13.650..70.350 × Y 7.610..54.390** ★ | ★**板读** ★ |
| ★15 ★ | ★**`HW/PCB/demo_mainboard_params.json` 的连接器/SoM 段与上表对不上 (★位号名 / 脚数 / 间距 / 位置 全有差★) ⇒ ★**以本表为准, params 要改由 hw-lead 改** ★ | ★**§7b 对照表 (params 读 + 板读, 逐项差值)** ★ |

### ★§3.4 认领句 (★给 hw-lead 抄进作业包 §3-S6 · 帧: 160×100 台架板版★)

★**S6-开口 (MECH 认领 · ISS-278 · 帧: `B160x100`)** ★

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 帧声明 | ★**§3-S6 里一切开口/窗口坐标 = 帧: `B160x100` (160×100 台架板)** (Edge.Cuts 中心线 0.00..160.00 × 0.00..100.00) ⇒ **不得与帧: `F30A` (60×30 套A) 的数混用** ★ ⇒ ★**帧 id 的唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES`; 本句已与它逐字对齐** ★ |
| ★**调试口开口 (罩 `J_DEBUG`)** ★ | ★**开口 X 137.850..148.050 × Y 54.300..58.900 (h=2.54 档); 左下角可放行 X0 ∈ [137.850, 142.063] · Y0 ∈ [54.300, 55.330]; 座体宽 1.775 (板读); 单边间隙 X 4.2125 / Y 1.0300 (最坏 3.9125 / 0.7300 ≥ 0.60)** ★ |
| ★**UART 检修口开口 (罩 `J_UART`)** ★ | ★**开口 X 13.790..23.990 × Y 66.300..70.900 (h=2.54 档); 左下角可放行 X0 ∈ [13.790, 17.620] · Y0 ∈ [66.300, 67.330]; 座体宽 2.540 (MECH 模型); 单边间隙 X 3.8300 / Y 1.0300 (最坏 3.5300 / 0.7300 ≥ 0.60)** ★ |
| ★**开口 Y 的公式 (★不许写死★)** ★ | ★**`OPEN_Y_eff(h) = max(4.60, h + 1.80)`; 开口 Y = [cy − OPEN_Y_eff/2, cy + OPEN_Y_eff/2]; h 三档 = 0.90 / 2.54 / 4.00** ★ |
| ★**两条必须分开** ★ | ★**`J_DEBUG` (144.30, 58.00) 与 `J_UART` (20.74, 70.00) 的 ΔX = 123.56 mm ⇒ 一个开口罩不住两个 ⇒ S6 必须拆成两条; 合并缺口 116.0175 mm ⇒ 几何不成立, 不是「还没想好」** ★ |
| ★**USB-C 边开口 (罩 `J_USB_C`)** ★ | ★**板边缺口 (★**另一侧是板外** ⇒ 插头从板边进出★) = X 132.995..147.005 × Y 0.000..7.300 · 必须清空区 = X 133.895..146.105 × Y 0.000..6.400 (座体 `F.Fab` ∪ 两个固定孔外缘) · ★**这条不许用 `OPEN_X` 10.20** (10.20 装不下两个壳体固定孔的 12.210) · ★**也不许用「Y 居中于器件中心」的公式** (缺口下沿锚在板边线 Y = 0.000)** ★ |
| ★**ISS-271 警语 (★与 `HW/PCB/BOARD_FRAME_CALIBER.md` §2.1 同口径★)** ★ | ★**ISS-271 交的那两个矩形 (检修口开口 X 47.00..60.00 × Y 1.665..11.730 · `D_LED_G` 首选窗口 X 33.00..47.71 × Y 1.60..28.40) 属帧: `F30A` (60×30 套A) ⇒ 【不可当 S6 坐标用】; 若要在 §3-S6 里提到它们 ⇒ 必须整段带 `F30A` 帧标 + 这句警语, 不许只抄数字** ★ |
| SoM 避让 | ★**两个开口窗口压住 `J_SOM_P1..P4` 焊盘数必须 = 0 (机器闸 `MECH/check_onepass_mech_sync.py` M2, 两条分别验)** ★ |
| `D_LED_G` 窗口 | ★**整高自由带 X 1.550..3.450 + X 72.540..73.660 (Y 1.450..98.950); 最近落位带 X 6.940..8.250 × Y 63.700..67.900; ★**`LED_G_D` 现状 93.492727 mm, 搬到 `R_LED_G` 旁边 ⇒ < 1 mm (净距 0.00~0.50 任一档)** ★ |
| 不可动 | ★**`CRIT` 0.60 / `cavity_req` 4.50 / `cav_v` 38.00 / `duct_v` 6.00 一个都不许改; ★**座体真实高度 = `[0数据]` ⇒ 开口 Y 一切数按公式取值, 不许把 2.54 当事实** ★ |
| 真源 | ★**帧: 160×100 台架板 的数 = `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (ISS-276) + `MECH/BOARD_ONEPASS_MECH_SYNC.md` (ISS-278) + 机器复算 `python3 MECH/check_onepass_mech_sync.py`; 帧: `F30A` (60×30 套A) 的旧数 = `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` §1~§4 (ISS-271) + `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` §1/§3 (ISS-267)** ★ | ★**不代拍** ★ |

---

## ★§4 归 main / 老板拍的清单 (★只列事实与代价, 不代拍★)

> ★**下面每一条都【不是】我能拍的 ⇒ 只给「事实 + 代价 + 若不拍的后果」; 拍板是 main→老板的活** ★

### ★§4.1 亮度档 G-5 (★改了 ⇒ 板要改第二次★)

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 事实 | ★**绿灯亮度档 = `[0数据]`** ★; 现状 `R_LED_G` + `D_LED_G` 已在板上 (★`[实测]`★) |
| 代价 A (不改) | ★**零板面动作** ★; 但 `LED_G_D` 现状 93.492727 mm 保留, 或按 §3.2 第 8 条挪到 `R_LED_G` 旁边 (⇒ 走线 < 1 mm) |
| 代价 B (改) | ★**改串阻值 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位 ⇒ 【板要改第二次】** ★ ⇒ ★**必须排在「板只改一次」之前拍** ★ |
| 谁拍 | ★**main → 老板** ★ |

### ★§4.2 座体高度 h 的确认途径 (★本机量不到 ⇒ 写清降级路径, 不许挂成等外部回复★)

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 事实 | ★**座体真实高度 h = `[0数据]`** ★; 本机**无实物** ⇒ 打印/量测全部 `[0数据]` ⇒ ★**物理上量不到** ★ |
| ★**降级方案 (★正面样板: 查不到就写降级, 不写「等回复」★)** ★ | ★**① 参数式: `OPEN_Y_eff(h) = max(4.60, h + 1.80)`; ② 三档假设: h_lo = 0.90 / h_ref = 2.54 / h_hi = 4.00; ③ 板那一趟【按公式取值】而不是按猜测定死** ★ |
| 三档代入结果 (帧: 160×100 台架板) | ★**h = 0.90 ⇒ 需求 2.70 / 取 4.60 (未涨) / 单边间隙 1.8500 (最坏 1.5500) / 调试口 Y 54.300..58.900 / 检修口 Y 66.300..70.900 / 落框 ✅ / 压 SoM = 0** ★ |
| ★**同上** ★ | ★**h = 2.54 ⇒ 需求 4.34 / 取 4.60 (未涨) / 单边间隙 1.0300 (最坏 0.7300) / Y 同上 / 落框 ✅ / 压 SoM = 0** ★ |
| ★**同上** ★ | ★**h = 4.00 ⇒ 需求 5.80 / 取 5.80 (★涨了★) / 单边间隙 0.9000 (最坏 0.6000 = CRIT 刚好过) / 调试口 Y 53.700..59.500 / 检修口 Y 65.700..71.500 / 落框 ✅ / 压 SoM = 0** ★ |
| 结论 | ★**三档全部可放行 ⇒ 开口 Y 不是「押注」, 是「带区间」** ★ ⇒ ★**h 定版只是把区间收成一个数, 不改结构口径** ★ |
| 谁拍 / 怎么拍 | ★**hw-lead 选型 + boss 拍型号** ★; ★**本单不需要它就能开那一趟** ★ |

### ★§4.3 结构光孔有 / 无 (★决定了 `D_LED_G` 板面落位要不要动★)

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 事实 | ★**`D_LED_G` 出光侧结构光孔位置 = `[0数据]`** ★; 板读 `D_LED_G` @ (101.25, 56.80), `R_LED_G` @ (5.90, 62.50) ⇒ `LED_G_D` 走线 **93.492727 mm** (★`[实测]`★) |
| 代价 A (有光孔) | ★**`D_LED_G` 必须挪到光孔正下方 ⇒ 板面落位要改** ★; 挪到最近落位带 ⇒ 走线 0.450~0.965 mm (净距 0.00~0.50) ⇒ ★**这一挪要赶在「板只改一次」之前** ★ |
| 代价 B (无光孔) | ★**`D_LED_G` 不用挪** ⇒ 板面落位零改动; 走线 93.492727 mm 保留, 或主动挪到最近落位带 (≤ 0.965 mm) ⇒ ★**挪不挪是 hw-lead 的布局活, 不强制** ★ |
| 谁拍 | ★**main → 老板 (结构件要不要开这个孔)** ★ |

### ★§4.4 连接器参数不符 (★归 hw-lead, 转 main 转交★)

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 事实 | ★**`HW/PCB/demo_mainboard_params.json` 的连接器/SoM 段与落表板实测对不上 (★位号名 / 脚数 / 间距 / 位置 全部有差, 逐项见 §7b★)** ★ |
| 会不会影响那一趟 | ★**会 —— 但只要 hw-lead 这一趟【以落表板实读为准】画, 就不会撞; 若照 params 那几列画, 会画错 (JTAG 位号/位置、UART 脚数/间距/位置、USB-C 位号/位置、SoM 位号/尺寸/位置 全错)** ★ |
| 归谁改 | ★**hw-lead 改 `HW/PCB/demo_mainboard_params.json`** (★ISS-277 同批在做板侧清单★) ⇒ ★**本单一个字不许改 `HW/`** ★ |
| 谁转交 | ★**main 转 hw-lead** ★ (★已登记为 `state/fragments/mech.yaml` 的 need, key = `iss278_mech_to_hw_board_inputs`★) ★

---

## ★§5 机器块 (★`MECH/check_onepass_mech_sync.py` 读这一块; 改数必须同步改 §2 表★)

<!-- MACHINE-BLOCK-BEGIN -->

```json
{
 "issue": "ISS-278",
 "agent": "mech-lead",
 "updated": "2026-11-17",
 "frame_default": "B160x100",
 "frames_allowed": [
  "B160x100",
  "F30A",
  "P60x15"
 ],
 "consts": {
  "open_x_spec": 10.2,
  "open_y_spec": 4.6,
  "crit": 0.6,
  "tol_fdm_part": 0.3,
  "edge_keepout": 0.8,
  "body_h_ref": 2.54,
  "body_h_ref_is_fact": false,
  "h_tiers": [
   0.9,
   2.54,
   4.0
  ],
  "open_y_formula": "OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h+1.80)",
  "open_y_formula_note": "h = 座体真实高度 = [0数据] => 开口 Y 一律按公式取值, 不许把 2.54 当事实"
 },
 "openings": [
  {
   "id": "PORT_OPEN_DEBUG",
   "role": "调试口",
   "covers": "J_DEBUG",
   "frame": "B160x100",
   "body_w": 1.775,
   "body_w_source": "板读 (J_DEBUG 焊盘铜箔宽 1.775)",
   "rect": {
    "x0": 137.85,
    "x1": 148.05,
    "y0": 54.3,
    "y1": 58.9
   },
   "x0_range": [
    137.85,
    142.063
   ],
   "y0_range_at_h_ref": [
    54.3,
    55.33
   ],
   "cl_x": 4.2125,
   "cl_y": 1.03,
   "worst_cl_x": 3.9125,
   "worst_cl_y": 0.73,
   "som_hits": 0,
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "PORT_OPEN_UART",
   "role": "检修口",
   "covers": "J_UART",
   "frame": "B160x100",
   "body_w": 2.54,
   "body_w_source": "MECH 现行模型硬编 2.54 (板读铜箔宽只有 0.775)",
   "rect": {
    "x0": 13.79,
    "x1": 23.99,
    "y0": 66.3,
    "y1": 70.9
   },
   "x0_range": [
    13.79,
    17.62
   ],
   "y0_range_at_h_ref": [
    66.3,
    67.33
   ],
   "cl_x": 3.83,
   "cl_y": 1.03,
   "worst_cl_x": 3.53,
   "worst_cl_y": 0.73,
   "som_hits": 0,
   "evidence": "[实测]+[推算]+[0数据]"
  },
  {
   "id": "PORT_OPEN_USBC",
   "role": "USB-C 边开口",
   "covers": "J_USB_C",
   "frame": "B160x100",
   "body_w": 8.64,
   "body_w_source": "板读 (J_USB_C 座体 F.Fab X 135.680..144.320 ⇒ 宽 8.640; 两个壳体固定孔 @ X 134.220 / 145.780 ⇒ 外缘 133.895..146.105)",
   "rect": {
    "x0": 137.85,
    "y0": 54.3,
    "x1": 148.05,
    "y1": 58.9
   },
   "x0_range": [
    132.995,
    133.895
   ],
   "y0_range_at_h_ref": [
    0.0,
    0.0
   ],
   "cl_x": 0.9,
   "cl_y": 0.9,
   "worst_cl_x": 0.6,
   "worst_cl_y": 0.6,
   "som_hits": 0,
   "evidence": "[实测](板读 F.Fab / F.CrtYd / 焊盘 / NPTH drill)+[推算](净距与开口宽)+[0数据](座体真实高 h)",
   "tiers": {
    "0.90": {
     "open_rect": {
      "x0": 137.85,
      "y0": 54.3,
      "x1": 148.05,
      "y1": 58.9
     },
     "must_clear": {
      "x0": 133.895,
      "y0": 0.0,
      "x1": 146.105,
      "y1": 6.4
     },
     "clearance_x": 0.9,
     "clearance_y": 0.9,
     "worst_clearance_x": 0.6,
     "worst_clearance_y": 0.6,
     "pass_crit": true
    },
    "2.54": {
     "open_rect": {
      "x0": 137.85,
      "y0": 54.3,
      "x1": 148.05,
      "y1": 58.9
     },
     "must_clear": {
      "x0": 133.895,
      "y0": 0.0,
      "x1": 146.105,
      "y1": 6.4
     },
     "clearance_x": 0.9,
     "clearance_y": 0.9,
     "worst_clearance_x": 0.6,
     "worst_clearance_y": 0.6,
     "pass_crit": true
    },
    "4.00": {
     "open_rect": {
      "x0": 137.85,
      "y0": 54.3,
      "x1": 148.05,
      "y1": 58.9
     },
     "must_clear": {
      "x0": 133.895,
      "y0": 0.0,
      "x1": 146.105,
      "y1": 6.4
     },
     "clearance_x": 0.9,
     "clearance_y": 0.9,
     "worst_clearance_x": 0.6,
     "worst_clearance_y": 0.6,
     "pass_crit": true
    }
   }
  }
 ],
 "merged_opening": {
  "id": "PORT_OPEN_MERGED",
  "frame": "B160x100",
  "forbidden": true,
  "covers": "J_DEBUG+J_UART",
  "content_w": 126.2175,
  "open_w": 10.2,
  "cl_x": -58.00875,
  "gap_mm": 116.0175,
  "separation_dx": 123.56,
  "separation_dy": -12.0,
  "separation_straight": 124.141345,
  "evidence": "[实测]"
 },
 "led": {
  "id": "LED_G_WINDOW",
  "frame": "B160x100",
  "ref": "D_LED_G",
  "res_ref": "R_LED_G",
  "net": "LED_G_D",
  "current_origin": [
   101.25,
   56.8
  ],
  "current_res_origin": [
   5.9,
   62.5
  ],
  "current_net_len_mm": 93.492727,
  "full_height_bands": [
   {
    "x0": 1.55,
    "x1": 3.45,
    "y0": 1.45,
    "y1": 98.95
   },
   {
    "x0": 72.54,
    "x1": 73.66,
    "y0": 1.45,
    "y1": 98.95
   }
  ],
  "nearest_band": {
   "x0": 6.94,
   "x1": 8.25,
   "y0": 63.7,
   "y1": 67.9
  },
  "hypothesis_hole": {
   "id": "LED_G_HOLE_A",
   "title": "有结构光孔 (光孔把 LED 钉死)",
   "frame": "B160x100",
   "space": {
    "x0": 6.94,
    "x1": 8.25,
    "y0": 63.7,
    "y1": 67.9
   },
   "space_kind": "封装原点可放行窗口",
   "net_len_range_mm": [
    0.45,
    0.965
   ],
   "board_change": "要改 (D_LED_G 必须挪到光孔正下方)",
   "evidence": "[实测]+[推算]+[0数据]"
  },
  "hypothesis_nohole": {
   "id": "LED_G_NOHOLE_B",
   "title": "无结构光孔 (LED 位置只受电气+机械约束)",
   "frame": "B160x100",
   "space": {
    "x0": 1.55,
    "x1": 3.45,
    "y0": 1.45,
    "y1": 98.95
   },
   "space_kind": "封装原点可放行窗口 (整高自由带; 另有一条 X 72.540..73.660)",
   "net_len_range_mm": [
    0.45,
    0.965
   ],
   "board_change": "不用改 (现状 93.492727 也合法)",
   "evidence": "[实测]+[推算]"
  },
  "clearance_sweep": [
   {
    "clr": 0.0,
    "n_placeable": 1992,
    "corner_len_mm": 0.45
   },
   {
    "clr": 0.1,
    "n_placeable": 2016,
    "corner_len_mm": 0.559
   },
   {
    "clr": 0.2,
    "n_placeable": 2031,
    "corner_len_mm": 0.68
   },
   {
    "clr": 0.5,
    "n_placeable": 2075,
    "corner_len_mm": 0.965
   }
  ]
 },
 "connectors": [
  {
   "key": "usb_c_ref",
   "mech_expected": "J_USB",
   "board_actual": "J_USB_C",
   "delta": "位号名不符",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "usb_c_position_mm",
   "mech_expected": [
    5.5,
    22.5
   ],
   "board_actual": [
    140.0,
    5.25
   ],
   "delta": "dX -134.500 / dY +17.250",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "uart_ref",
   "mech_expected": "J_UART",
   "board_actual": "J_UART",
   "delta": "一致",
   "affects_onpass": false,
   "owner": "-"
  },
  {
   "key": "uart_pins",
   "mech_expected": 4,
   "board_actual": 2,
   "delta": "差 2 脚",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "uart_pitch_mm",
   "mech_expected": 2.54,
   "board_actual": 0.5,
   "delta": "差 2.04",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "uart_position_mm",
   "mech_expected": [
    49.0,
    6.0
   ],
   "board_actual": [
    20.74,
    70.0
   ],
   "delta": "dX -28.260 / dY +64.000",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "jtag_ref",
   "mech_expected": "J_JTAG",
   "board_actual": "J_DEBUG",
   "delta": "位号名不符",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "jtag_pins",
   "mech_expected": 5,
   "board_actual": 4,
   "delta": "差 1 脚",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "jtag_pitch_mm",
   "mech_expected": 2.54,
   "board_actual": 0.5,
   "delta": "差 2.04",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "jtag_position_mm",
   "mech_expected": [
    52.0,
    13.0
   ],
   "board_actual": [
    144.3,
    58.0
   ],
   "delta": "dX -92.300 / dY +45.000",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "som_ref",
   "mech_expected": "U_SOM_RK3572",
   "board_actual": "J_SOM_P1..P4 (4 x 100 pads)",
   "delta": "位号+拓扑都不符",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "som_width_mm",
   "mech_expected": 40.0,
   "board_actual": 56.6,
   "delta": "差 16.60 (座体 F.Fab 并集)",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "som_height_mm",
   "mech_expected": 24.0,
   "board_actual": 46.2,
   "delta": "差 22.20 (座体 F.Fab 并集)",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "som_position_mm",
   "mech_expected": [
    33.0,
    26.0
   ],
   "board_actual": [
    42.0,
    31.0
   ],
   "delta": "dX -9.000 / dY -5.000 (四组阵心)",
   "affects_onpass": true,
   "owner": "hw-lead"
  },
  {
   "key": "board_width_mm",
   "mech_expected": 160.0,
   "board_actual": 160.0,
   "delta": "一致",
   "affects_onpass": false,
   "owner": "-"
  },
  {
   "key": "board_height_mm",
   "mech_expected": 100.0,
   "board_actual": 100.0,
   "delta": "一致",
   "affects_onpass": false,
   "owner": "-"
  },
  {
   "key": "board_thickness_mm",
   "mech_expected": 1.6,
   "board_actual": 1.6,
   "delta": "一致",
   "affects_onpass": false,
   "owner": "-"
  },
  {
   "key": "board_layers",
   "mech_expected": 8,
   "board_actual": 8,
   "delta": "一致",
   "affects_onpass": false,
   "owner": "-"
  },
  {
   "key": "board_corner_radius_mm",
   "mech_expected": 3.0,
   "board_actual": 0.0,
   "delta": "差 3.000 (Edge.Cuts 是 4 条直角 gr_line, 无圆角)",
   "affects_onpass": true,
   "owner": "hw-lead"
  }
 ],
 "items": [
  {
   "id": "MECH-PORT-DEBUG",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "调试口开口 (罩 J_DEBUG)",
   "current_state": "盘上实物 J_DEBUG @ (144.30, 58.00), 4 焊盘 1x4 @0.50, 铜箔 X 142.063..143.838 x Y 56.150..57.050 [实测]",
   "spec": "开口 (h=2.54 档) = X 137.850..148.050 x Y 54.300..58.900; 左下角 X0 in [137.850, 142.063] y Y0 in [54.300, 55.330]; 座体宽 1.775; 间隙 X 4.2125 / Y 1.0300",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (M2 调试口压 J_SOM_P1..P4 焊盘数 = 0)",
   "blocked_by": "无",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "MECH-PORT-UART",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "检修口开口 (罩 J_UART)",
   "current_state": "盘上实物 J_UART @ (20.74, 70.00), 2 焊盘 1x2 @0.50, 铜箔 X 18.502..19.277 x Y 68.150..69.050 [实测]",
   "spec": "开口 (h=2.54 档) = X 13.790..23.990 x Y 66.300..70.900; 左下角 X0 in [13.790, 17.620] y Y0 in [66.300, 67.330]; 座体宽 2.540; 间隙 X 3.8300 / Y 1.0300",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (M2 检修口压 J_SOM_P1..P4 焊盘数 = 0)",
   "blocked_by": "无",
   "evidence": "[实测]+[推算]+[0数据]"
  },
  {
   "id": "MECH-PORT-USBC",
   "source_iss": "ISS-294",
   "frame": "B160x100",
   "title": "USB-C 边开口 (罩 J_USB_C · 板边缺口 · 插头从板边进出)",
   "current_state": "J_USB_C @ (140.000, 5.250); 座体 F.Fab X 135.680..144.320 x Y 0.000..6.400 (8.640 x 6.400); F.CrtYd X 135.180..144.820 x Y -0.500..6.900; 2x NPTH @ (134.220, 2.625) / (145.780, 2.625) Ø0.65 (pad) / Ø0.762 (drill); 插头面与板边齐平 (state/usb_c_footprint.py 定位口径) [实测]",
   "spec": "边开口 (板边缺口, 另一侧是板外) = X 132.995..147.005 x Y 0.000..7.300; 必须清空区 = 座体 F.Fab ∪ 两个固定孔外缘 = X 133.895..146.105 x Y 0.000..6.400; 单边净距 X 0.900 / Y 0.900 (最坏 0.600 = CRIT); 缺口 Y 向深度由座体平面尺寸支配 (6.400 + 0.900 = 7.300) 不随 h 变 => h 三档 (0.90/2.54/4.00) 板面矩形同值, 随 h 变的是 Z 向窗口 OPEN_Y_eff(h) = 4.60/4.60/5.80; 立柱/螺钉头外扩三档见 §11.4",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (M2 集合断言三条 + M2b 任意两条矩形不许相同 + M3 边开口逐档验) + python3 MECH/check_onepass_struct_crosscheck.py => rc=0 (N3 三条分别验 + N4 MC_USBC 净距)",
   "blocked_by": "结构开口尺寸 = 归 main→boss 拍 (本单只交几何 + 代价 + 建议, 不代拍); 立柱/螺钉头外径 = [0数据] (固定方式未定)",
   "evidence": "[实测]+[推算]+[0数据]"
  },
  {
   "id": "MECH-PORT-NOMERGE",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "两条开口必须分开 (合并几何上不可能)",
   "current_state": "J_DEBUG <-> J_UART dX 123.56 / dY -12.00 / 直线 124.141345 mm [实测]",
   "spec": "合并开口禁止: 必须清空区并集宽 126.2175 vs 开口宽 10.20 => 单边间隙 -58.00875 => 缺口 116.0175 mm => 判红",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (merged_opening.forbidden = true, gap_mm = 116.0175)",
   "blocked_by": "无",
   "evidence": "[实测]"
  },
  {
   "id": "MECH-BODY-H",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "座体真实高度参数化 (不许把 2.54 当事实)",
   "current_state": "座体真实高度 = [0数据] (本机无实物); BASE['jd_body_h'] = 2.54 是假设不是事实 [0数据]",
   "spec": "OPEN_Y_eff(h) = max(4.60, h + 1.80); 开口 Y = [cy - OPEN_Y_eff/2, cy + OPEN_Y_eff/2]; h 三档 0.90 / 2.54 / 4.00 => 三档全部落框内 + 压 SoM = 0",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (M3 三档逐档自洽)",
   "blocked_by": "座体型号定版 = hw-lead 选型 + boss 拍; 本机不可得 => 降级 = 参数式 + 三档 + 按公式取值",
   "evidence": "[0数据]+[推算]"
  },
  {
   "id": "MECH-LED-G",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "D_LED_G 落位空间 + 有/无结构光孔两假设",
   "current_state": "D_LED_G @ (101.25, 56.80); R_LED_G @ (5.90, 62.50); LED_G_D 走线 93.492727 mm; 结构光孔位置 = [0数据]",
   "spec": "假设 A (有光孔): 空间 X 6.940..8.250 x Y 63.700..67.900, 走线 0.450~0.965, 板面落位要改; 假设 B (无光孔): 整高带 X 1.550..3.450 (+ X 72.540..73.660) x Y 1.450..98.950, 走线 0.450~0.965, 板面不用改",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (led.hypothesis_hole / led.hypothesis_nohole 两份空间齐全)",
   "blocked_by": "结构光孔有/无 = 归 main -> boss 拍",
   "evidence": "[实测]+[推算]+[0数据]"
  },
  {
   "id": "MECH-LED-GD-NET",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "LED_G_D 走线长度 (根因 = 排版规则)",
   "current_state": "93.492727 mm (实测); 根因 = R_LED_G 被放进 X=5.90 左侧上拉列, D_LED_G 被放进 Y=56.80 LED 行",
   "spec": "目标 < 1 mm: 净距 0.00 -> 0.450 / 0.10 -> 0.559 / 0.20 -> 0.680 / 0.50 -> 0.965",
   "criterion": "python3 MECH/board_port_opening_s6_check.py --json => rc=0 (现值别改) + python3 MECH/check_onepass_mech_sync.py => rc=0",
   "blocked_by": "最终 D_LED_G 坐标 = 归 hw-lead (PCB 布局)",
   "evidence": "[实测]+[推算]"
  },
  {
   "id": "MECH-CONN-PARAMS",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "连接器占位参数对照表 (params vs 落表板)",
   "current_state": "HW/PCB/demo_mainboard_params.json 的连接器/SoM 段与落表板实测对不上 (位号名/脚数/间距/位置 全有差)",
   "spec": "以落表板实读为真源 (见 connect[] 段 board_actual 列); params 那一列是要改成什么, 不是现状",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (M4 判据命令真存在) + python3 state/check_brief_commands.py --brief-file MECH/BOARD_ONEPASS_MECH_SYNC.md => rc=0",
   "blocked_by": "归 hw-lead 改 HW/PCB/demo_mainboard_params.json (ISS-277 同批在做板侧清单) => 转 main 转交; 本单零改 HW/",
   "evidence": "[实测]"
  },
  {
   "id": "MECH-LED-BRIGHT-G5",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "亮度档 G-5 (改了 => 板要改第二次)",
   "current_state": "绿灯亮度档 = [0数据]; 现状 R_LED_G + D_LED_G 已在板上 [实测]",
   "spec": "不改 => 零板面动作; 改 => 改串阻值 => 改网表 => 改 BOM => 改板面落位 => 板要改第二次",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0 (登记在案, 本单不代拍)",
   "blocked_by": "归 main -> boss 拍; 必须排在「板只改一次」之前",
   "evidence": "[0数据]+[实测]"
  },
  {
   "id": "MECH-LED-HOLE",
   "source_iss": "ISS-278",
   "frame": "B160x100",
   "title": "结构光孔有/无 (板面落位的前置条件)",
   "current_state": "结构光孔 = [0数据]",
   "spec": "两种假设的可放行空间见 MECH-LED-G 条 (假设 A / 假设 B); 拍板之前板那一趟只能按假设 B 落位 (不挪 D_LED_G)",
   "criterion": "python3 MECH/check_onepass_mech_sync.py => rc=0",
   "blocked_by": "归 main -> boss 拍",
   "evidence": "[0数据]"
  }
 ]
}
```

<!-- MACHINE-BLOCK-END -->

★**机器块口径**: `openings[]` 每条 = 一条独立开口规格 (★**两条, 不许合并**★) · `merged_opening` = 合并禁令 + 缺口量化 · `led.hypothesis_hole` / `led.hypothesis_nohole` = 两假设各一份空间 · `connectors[]` = §7b 对照表的机器版 (★`mech_expected` = 要改成什么 · `board_actual` = 现状真源★) · `items[]` = §2 逐条表的机器版 (8 字段) · ★**`criterion` 里的命令必须在本机真实存在 (机器闸 M4 会逐条查)** ★

---

## ★§6 本页的边界 (★自证口径★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**板 / `.kicad_pro` / 网表 / 脚表 / BOM 五件 md5 跑前跑后逐字节相同 (机器闸 M5)** ★ |
| ★**M5 口径 (★2026-11-17 ISS-278 续做修订·实测发现的真缺口★)** ★ | ★**本闸的 M5 原先只查 `CFC.PROTECTED` ⇒ 只查 2 件 (板 / `.kicad_pro`)**: ★★ISS-286 在 12:44 把 `PROTECTED` 从 5 件改成 2 件 (网表/脚表/BOM 改归【落表台账】管) ⇒ 本闸覆盖面被【悄悄削掉一半】★ ⇒ ★**现在 M5 分两段, 5 件一件都不少** ★: ★**M5a 硬基线 2 件** (板 / `.kicad_pro`, 基线写死) + ★**M5b 台账管理 3 件** (网表 / 脚表 / BOM, 判决源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` 链头, ★**照 ISS-286 的 C4 同构口径, fail-closed 六条: 台账读不到 / 查不到登记 / 链头取不准 / 链头无单号 / 链断 / 有孤儿记录 ⇒ 一律判红★**) ★ ⇒ ★**合法落表 (链头前移) ⇒ 绿; 偷改真源不更新台账 ⇒ 红** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_demo_struct_truth.py` / `MECH/service_port_check.py` / `MECH/board_port_opening_s6_check.py` / `MECH/jd_y0_feasibility.py` / `MECH/verify_budget.py` 一个字不许动 ⇒ 本单的新闸是【新建】文件 `MECH/check_onepass_mech_sync.py`** ★ |
| ★**零改 HW** ★ | ★**`HW/` 零字节写入** ★ |
| ★**零改 `MECH/BOARD_GEOM_30MM.md`** ★ | ★**它是「另一套基线」的事实登记 ⇒ 本页只【引用】** ★ |
| ★**零改别人的交卷单** ★ | ★**ISS-276 的交卷单 / 归一页一个字不许改 (只在归一页【追加式】订正 §3b/§4b/§6b/§7b/§8)** ★ |
| ★**零外发** ★ | ★**不发邮件 / 不询价 / 不问询 / 不采购 ⇒ 查不到就写 `[0数据]` + 降级方案** ★ |
| ★**证据分级** ★ | ★**每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`; 本页 `[官网]`/`[媒体]` = 0 条, 实物 `[实测]` = 0 条** ★ |
| ★**不替老板拍板** ★ | ★**座体高度 h / 结构光孔有否 / 亮度档 G-5 = 只列事实与代价, 归 main→老板** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`** ★ |


---

# ★★【ISS-290 追加段】★★ · 2026-11-17 · owner=mech-lead · cron `775d9893`

> ★**本段是【追加】, 本页 §1~§6 的老字一个字没删、没改、没动** ★
> ★**帧声明 (★本追加段一切坐标 = 帧: `B160x100` (160×100 台架板)· 与本页 §1 逐字对齐★)** ★
> ★**来由**: ★**「板只改一次」那一趟, 结构侧最后两个【没人交叉验过】的接口 —— ① S6 的 20 个目标落位 × MECH 保留区 (hw-lead 的闸不查结构保留区, 本页的 M1~M5 闸不碰 S6 目标落位 ⇒ 两边各自绿, 合起来可能撞) · ② 座体类器件三方对照 (BOM/网表 1.27 mm 排针 vs 板读 0.50 mm land ⇒ 实物排针落不进)** ★
> ★**本页新增**: §9 (S6 落位 × MECH 保留区 交叉核对) · §10 (座体三方对照摘要 + 排针 pitch 1.27 vs 0.50 的结构后果) ★
> ★**本页的数全部自算** (★实算脚本 `logs/iss290/compute_iss290.py` · 自写 s-expr 板解析器 `logs/iss290/pcbparse.py` · 只读 import `MECH/check_board_frame_coords.py` 取阈值 ⇒ 阈值零漂移★) ⇒ ★**不许照抄任何交卷单的数** ★
> ★**新闸**: `python3 MECH/check_onepass_struct_crosscheck.py` (N1 帧标签 / N2 SoM 承载区零冲突 / N3 两条开口分别验 / N4 必清空区净距 ≥ CRIT / N5 座体三方对照表四字段齐全 / N6 受保护 5 件 md5 逐字节不变) · 自检 `--selftest` 8 条反向用例全抓到 ★
> ★**零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本 · 零外发 · 不自签 issue_log (verify_by=main)** ★

---

## ★§9 S6 目标落位 × MECH 保留区 交叉核对 (★帧: `B160x100`★) ★

### ★§9.1 核对对象 (★两边各自绿、谁都没验的那段缝★) ★

| 侧 (★帧: `B160x100`★) | 闸 | 查什么 | ★**不查什么 (★就是那道缝★)** ★ |
|---|---|---|---|
| ★**HW 侧** ★ | `HW/check_board_frame_caliber.py` (ISS-274) | ★**帧标签齐 / 20 条与文档串逐字一致 / 缺位 0 / 重叠 0 / 出界 0** ★ | ★**结构保留区 (SoM 承载区 / 两条开口 / 两条必须清空区) 一律不查** ★ |
| ★**MECH 侧 (本页 M1~M5)** ★ | `MECH/check_onepass_mech_sync.py` (ISS-278) | ★**帧标签 / 两条开口各自不压 SoM 座 / 座体高度参数式自洽 / 判据命令真存在 / 受保护 5 件 md5** ★ | ★**S6 的 20 个目标落位一个都不碰** ★ |
| ★**本单补的缝** ★ | ★**`MECH/check_onepass_struct_crosscheck.py`** ★ | ★**S6 20 个目标落位 × MECH 保留区逐个核对 (N1~N4)** ★ | —— |

### ★§9.2 核对结论 (★本单自算★) ★

| 项 | 结论 (帧: 160×100 台架板) | 证据级 |
|---|---|---|
| ★**冲突条数** ★ | ★**0 条 (20/20 全部「通过」)** ★ —— 禁入区命中 0 (SoM 三口径 + 两条开口, h 三档逐档) · 必清空区净距不足 0 · 占位冲突 0 (186 封装逐个查) · `D_LED_G` 可放行带侵占 0 | ★`[实测]` 板读 + `[推算]` 复算 ★ |
| ★**最小净距** ★ | ★**4.6500 mm** (★`TP_DSI_D0_N` / `TP_DSI_D3_P` 的落位包络到 SoM 保守包络的 X 向距离★) | ★`[推算]` ★ |
| ★**真实位移** ★ | ★**20 个里只有 `R_SEL_D3_P` 真位移: 板上 (78.900, 9.500) ⇒ 目标 (122.300, 5.500)** ★; 其余 19 个板上已在目标位 | ★`[实测]` 板读 ★ |
| ★**SoM 承载区三口径 (本单自算)** ★ | ★**焊盘铜箔并集 X 15.100..68.900 × Y 7.610..54.390 (53.80 × 46.78) · 座体 `F.Fab` 并集 X 13.700..70.300 × Y 7.900..54.100 (56.60 × 46.20) · 保守包络 X 13.650..70.350 × Y 7.610..54.390 (56.70 × 46.78)** ★ | ★`[实测]` 板读 (400 焊盘逐 pad 外框并集) ★ |
| ★**两条开口 (本单自算, 与本页 §5 一致)** ★ | ★**调试口 X 137.850..148.050 × Y 54.300..58.900 · 检修口 X 13.790..23.990 × Y 66.300..70.900 (h = 2.54 档)** ★ | ★`[实测]` + `[推算]` ★ |
| ★**两条必须清空区 (本单自算)** ★ | ★**调试口 X 142.0625..143.8375 × Y 55.330..57.870 · 检修口 X 17.620..20.160 × Y 67.330..69.870 (h = 2.54 档)** ★ | ★`[实测]` + `[推算]` ★ |
| ★**逐行表** ★ | ★**`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3 (20 行, 每行 `ref` / `frame` / `target_x` / `target_y` / `footprint_extent` / `hit_zones` / `verdict` / `min_clearance_mm` / `evidence`)** ★ | —— |

### ★§9.3 ★给 hw-lead 的 S6 落位约束句 (★现役板坐标版 · 可直接抄进作业包 §3-S6★) ★

★**S6-落位 (MECH 交叉核对认领 · ISS-290 · 帧: `B160x100`)** ★

| 项 | 内容 (帧: 160×100 台架板) |
|---|---|
| 帧声明 | ★**§3-S6 里一切落位/开口/窗口坐标 = 帧: `B160x100` (160×100 台架板)** (Edge.Cuts 中心线 0.000..160.000 × 0.000..100.000) ⇒ **不得与帧: `F30A` (60×30 套A) 的数混用** ★ ⇒ ★**帧 id 的唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES`** ★ |
| ★**S6 落位约束 (20 条)** ★ | ★**S6 的 20 个目标落位 (封装原点) 必须同时满足: ① 落位包络 (F.Fab 外形 ∪ 焊盘铜箔) 不压 SoM 承载区 (焊盘铜箔并集 X 15.100..68.900 × Y 7.610..54.390 · 座体 `F.Fab` 并集 X 13.700..70.300 × Y 7.900..54.100 · 保守包络 X 13.650..70.350 × Y 7.610..54.390); ② 不落进调试口开口 (X 137.850..148.050 × Y 54.300..58.900) 与检修口开口 (X 13.790..23.990 × Y 66.300..70.900) —— ★**两条分别验, 不许合并验**★; ③ 到两条座体必须清空区 (调试口 X 142.0625..143.8375 × Y 55.330..57.870 · 检修口 X 17.620..20.160 × Y 67.330..69.870) 的净距 ≥ 0.60; ④ 不侵占 `D_LED_G` 可放行带 (X 1.550..3.450 / X 72.540..73.660 × Y 1.450..98.950); ⑤ 器件距板边 ≥ 0.80** ★ |
| ★**现状 (本单自算)** ★ | ★**20 条落位对上述 5 条全部满足 —— 冲突 0 条, 最小净距 4.6500 mm ⇒ 「钉 20 个」这个动作【不会撞】** ★ |
| ★**但仍要跑闸** ★ | ★**S6 每次重出板后必须跑 `python3 MECH/check_onepass_struct_crosscheck.py` ⇒ N1~N6 全绿才准出 Gerber** ★ |
| ★**不可动** ★ | ★**`CRIT` 0.60 / `EDGE_KEEPOUT` 0.80 / `OPEN_X` 10.20 / `h` 三档 0.90/2.54/4.00 一个都不许改; ★**座体真实高度 h = `[0数据]` ⇒ 开口 Y 一律按公式取值, 不许把 2.54 当事实** ★ |
| 真源 | ★**帧: `B160x100` 的数 = `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (ISS-290) + 本页 §5 (ISS-278) + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (ISS-276); 帧: `F30A` 的旧数 = `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` §1~§4 (ISS-271) + `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` §1/§3 (ISS-267)** ★ | ★**不代拍** ★ |

---

## ★§10 座体类器件三方对照摘要 + 排针 pitch 1.27 vs 0.50 的结构后果 (★帧: `B160x100`★) ★

### ★§10.1 三方对照摘要 (★完整 9 行在 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4★) ★

| 位号 (★帧: `B160x100`★) | ① BOM · 网表规格串 | ② 板读 land pattern | ③ 结构占位要求 | `verdict` |
|---|---|---|---|---|
| ★`J_DEBUG` ★ | ★**BOM `HW/BOM_v1.csv:71` = 「1×4 1.27mm 排针 (JTAG)」· 网表 P8 行同串** ★ | ★**pitch 0.50 · 4 脚 · 铜箔 X 142.0625..143.8375 × Y 56.1500..57.0500 (1.7750 × 0.9000)** ★ | ★**座体宽 1.7750 · 开孔 X 137.850..148.050 × Y 54.300..58.900 · 必须清空区 X 142.0625..143.8375 × Y 55.330..57.870** ★ | ★**装不进 ⇒ 必须改封装** ★ |
| ★`J_UART` ★ | ★**BOM `HW/BOM_v1.csv:77` = 「1×2 1.27mm 排针 (UART)」· 网表 P8 行同串** ★ | ★**pitch 0.50 · 2 脚 · 铜箔 X 18.5025..19.2775 × Y 68.1500..69.0500 (0.7750 × 0.9000)** ★ | ★**座体宽 2.5400 (MECH 模型) · 开孔 X 13.790..23.990 × Y 66.300..70.900 · 必须清空区 X 17.620..20.160 × Y 67.330..69.870** ★ | ★**装不进 ⇒ 必须改封装** ★ |
| ★`J_USB_C` ★ | ★**BOM `HW/BOM_v1.csv:78` = 「Type-C 16p 座」· footprint 备注 GCT USB4105-16P (16 焊盘 @0.50mm + 2×Ø0.65 @±5.78)** ★ | ★**pitch 0.50 · 16 信号 + 2 NPTH · 铜箔 X 133.8950..146.1050 × Y 2.3000..5.8250 · 座体 F.Fab X 135.680..144.320 × Y 0.000..6.400** ★ | ★**座体 8.64 × 6.40 · 高 3.50 · ★**Y 下沿 = 板边 ⇒ 结构件必须开边口 (★**ISS-294 已补这条边开口规格**★)** ★ | ★**边开口 = X 132.995..147.005 × Y 0.000..7.300 (板边缺口) · 必须清空区 = X 133.895..146.105 × Y 0.000..6.400 (座体 `F.Fab` ∪ 两个固定孔外缘) · h 三档 0.90/2.54/4.00 (随 h 变的是 Z 向窗口 `OPEN_Y_eff(h)` = 4.60/4.60/5.80)** ★ | ★**可装 / ★边开口规格已补 (X 132.995..147.005 @ 板边 Y=0 · h 三档 · 固定孔清空区 X 133.895..146.105)★** ★ |
| ★`J_CHG` ★ | ★**BOM `HW/BOM_v1.csv:70` = 「跨铰链 1.5A (双 pin 并联)」; ★**网表同名 `J_CHG` 的 value 串 = 「1×10p@0.5mm 排线座」且 11 行全部 board=HINGE ⇒ 同名不同物** ★ | ★**pitch 0.50 · 2 脚 · 铜箔 X 133.0625..133.8375 × Y 56.1500..57.0500** ★ | ★**跨铰链载流焊盘对 · 板面禁压别的件** ★ | ★**口径需澄清** ★ |
| ★`J_SOM_P1` / `J_SOM_P3` ★ | ★**BOM 值 = 网络语义 (「1M+1M 分压 + 100nF」/「EN 输出」) ⇒ 没有连接器型号** ★ | ★**pitch 0.40 · 100 脚 (2×50) · 铜箔 19.8000 × 3.7800** ★ | ★**SoM 承载区四组之一** ★ | ★**口径需澄清 (以板读 land 为真源)** ★ |
| ★`J_SOM_P2` / `J_SOM_P4` ★ | ★**BOM = 「Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm」· opn 同** ★ | ★**pitch 0.40 · 100 脚 (2×50) · 铜箔 19.8000 × 3.7800** ★ | ★**SoM 承载区四组之一** ★ | ★**可装 (三方一致)** ★ |

### ★§10.2 ★排针 pitch 1.27 vs 0.50: 「改 land 到 1.27」的结构后果 (★实测算· 帧: `B160x100`· 本单自算★) ★

| 项 (★帧: `B160x100`★) | 现状 (板读, pitch 0.50) | 改 land 到 1.27 | Δ | 过 `CRIT` 0.60 |
|---|---|---|---|---|
| ★**`J_DEBUG` 铜箔宽** ★ | 1.7750 (X 142.0625..143.8375) | ★**4.0850 (X 140.9075..144.9925)** ★ | +2.3100 | —— |
| ★**`J_DEBUG` 必须清空区 X** ★ | 142.0625..143.8375 (宽 1.7750) | ★**140.9075..144.9925 (宽 4.0850, 由铜箔口径支配)** ★ | +2.3100 | —— |
| ★**`J_DEBUG` 开口 X** ★ | 137.850..148.050 | ★**137.850..148.050 (一字不变)** ★ | 0 | —— |
| ★**`J_DEBUG` 单边间隙 X** ★ | 4.2125 (最坏 3.9125) | ★**3.0575 (最坏 2.7575)** ★ | −1.1550 | ★**✅** ★ |
| ★**`J_DEBUG` 开口左下角可放行宽** ★ | 4.2125 | ★**3.0575** ★ | −1.1550 | —— |
| ★**`J_UART` 铜箔宽** ★ | 0.7750 (X 18.5025..19.2775) | ★**1.5450 (X 18.1175..19.6625)** ★ | +0.7700 | —— |
| ★**`J_UART` 必须清空区 X** ★ | 17.620..20.160 (宽 2.5400, **座体口径支配**) | ★**17.620..20.160 (一字不变)** ★ | **0** | —— |
| ★**`J_UART` 开口 X / 单边间隙 X / 左下角可放行宽** ★ | 13.790..23.990 / 3.8300 / 3.8300 | ★**全部不变** ★ | 0 | ★**✅** ★ |
| ★**Y 向 (h 三档 0.90 / 2.54 / 4.00)** ★ | —— | ★**全部不变 (pitch 与 Y 无关)** ★ | 0 | ★**✅ 三档全过 (h=4.00 档最坏 0.6000 刚好过)** ★ |
| ★**SoM 承载区** ★ | —— | ★**零影响 (位置不动)** ★ | 0 | —— |

★**⇒ 一句话结论 (结构后果, 实算)**: ★**「改 land 到 1.27」只动 `J_DEBUG` 一处 —— 必须清空区 X 宽度 1.7750 ⇒ 4.0850, 单边间隙 4.2125 ⇒ 3.0575 (最坏 2.7575, 仍 ≥ CRIT 0.60), 调试口开口左下角可放行带 4.2125 ⇒ 3.0575 mm; `J_UART` 因为座体口径 (2.5400) 支配 ⇒ 结构侧零连带改动; 两条开口的 X 与 Y 全不变; h 三档全过; SoM 承载区零影响** ★
★**⇒ 对「板只改一次」的意义**: ★**只要「改 land 到 1.27」与「S6 落位」放在同一趟 ⇒ 板 md5 变更次数仍是 1** ★ ⇒ ★**但这两条都【会改板】⇒ 必须在那一趟之前拍完 (归 main→老板 / hw-lead)** ★

### ★§10.3 另两条会改板的口径 (★同样必须在「板只改一次」之前定★) ★

| # (★帧: `B160x100`★) | 项 | 现状 `[实测]` | 结构后果 | 代价 |
|---|---|---|---|---|
| ★1 ★ | ★**`corner_radius` 3.0 vs 0.0** ★ | ★**板读 `Edge.Cuts` = 4 条直角 `gr_line` ⇒ 实测 R = 0.00; `HW/PCB/demo_mainboard_params.json` 写 `corner_radius_mm: 3.0` ⇒ Δ 3.000; ★**且 `state/gen_pcb_netlist_board.py` 的 `add_outline()` 只画 4 条直线, 根本不读这个参数 ⇒ 是个没人用的死参数** ★ | ★**按 R=3.0 口径算出来的贴角可用区比实板小: 单角 7.8400 ⇒ 0.2041 mm² (−7.6359), 四角合计 −30.5436 mm²; 板框面积 −7.7257 mm²; 整板可用面积合计 −38.2693 mm² (偏保守 ⇒ 不会撞, 但白丢面积)** ★ | ★**口径改板读 = 零板改 · 零结构改 (只改 params 一个数); 改板框加圆角 = 改生成器 + 板重出 + 贴角器件重排** ★ |
| ★2 ★ | ★**`J_USB_C` 边开口缺口** ★ | ★**座体 `F.Fab` Y 下沿 = 0.000 = 板边 ⇒ 插头从板边进出; 现有 MECH 规格 (检修口 / 调试口两条) 里没有这条边开口** ★ | ★**必须补一条结构边开口 (X 135.680..144.320 @ 板边 Y = 0) 并算进必须清空区 + 闸 (N3 加第三条开口)** ★ | ★**不改板; 结构开口尺寸归 main→boss 拍** ★ |

### ★§10.4 「必须在那一趟一起改」清单 (★帧: `B160x100`· 完整版在 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §5.6★) ★

| 条目 (★帧: `B160x100`★) | 标题 | 现状 `[实测]` | 改法 | 判据命令 | 归谁改 |
|---|---|---|---|---|---|
| ★**E-1** ★ | ★**排针 pitch 1.27 vs 0.50 (`J_DEBUG` / `J_UART`)** ★ | BOM/网表 1.27 vs 板读 0.50 (Δ 0.77) | ★**三选一: ① 改 land 到 1.27 (结构后果见 §10.2) · ② 改选型到 2.54 (`J_DEBUG` 必须清空区 X 139.0025..146.8975, 单边间隙 1.1525) · ③ 取消座体改治具探针** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py`** ★ | hw-lead + mech-lead + main |
| ★**E-2** ★ | ★**`corner_radius` 3.0 vs 0.0** ★ | 板读 R=0.00 vs params 3.0 | ★**① 口径改板读 (零板改) · ② 改板框加 3.0 圆角 (改生成器 + 板重出)** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` + `python3 MECH/check_board_frame_coords.py`** ★ | hw-lead + mech-lead + main |
| ★**E-3** ★ | ★**`J_CHG` 同名不同物** ★ | 主板 2 脚 vs 网表 HINGE 10p | ★**① 主板侧改名并同步 BOM/网表 (触落表, 须 main 批准) · ② 保持同名但把 BOM board 栏写清 (零落表)** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N5)** ★ | hw-lead + main |
| ★**E-4** ★ | ★**`J_SOM_P1` / `J_SOM_P3` 的 BOM 规格串只有网络语义** ★ | BOM 值 = 网络语义 | ★**改成与 `P2`/`P4` 同口径 (DF40C-100DS-0.4V(51)) —— 触落表; 或先在 §4 表里以板读 land 为真源登记 (已登记)** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N5)** ★ | hw-lead + main |
| ★**E-5** ★ | ★**SoM 承载区三口径写进作业包** ★ | 53.80 × 46.78 / 56.60 × 46.20 / 56.70 × 46.78 | ★**原样抄进作业包 §3-S6 (连帧标), 注明「判冲突用保守包络」** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N2)** ★ | hw-lead + mech-lead |
| ★**E-6** ★ | ★**`J_USB_C` 补一条结构边开口规格** ★ | 座体贴板边, 现有规格没有 | ★**补开口规格 + 必须清空区 + 闸 (N3 加第三条)** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py`** ★ | mech-lead + main |

### ★§10.5 本追加段的边界 (★自证口径★) ★

| 边界 (★帧: `B160x100`★) | 怎么自证 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**板 / `.kicad_pro` / 网表 / 脚表 / BOM 五件 md5 跑前跑后逐字节相同 (机器闸 N6)** ★ |
| ★**零改 `HW/`** ★ | ★**只读 `HW/PCB/BOARD_FRAME_CALIBER.md` / `demo_mainboard.kicad_pcb` / `demo_mainboard_params.json` / `BOM_v1.csv` / `netlist_v1.csv` / `netlist_v1_pins.csv`** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_onepass_mech_sync.py` / `MECH/check_board_frame_coords.py` / `MECH/check_demo_struct_truth.py` / `MECH/board_port_opening_s6_check.py` 一个字节不许动 ⇒ 新闸是【新建】文件 `MECH/check_onepass_struct_crosscheck.py`** ★ |
| ★**零改生成器** ★ | ★**`state/gen_pcb_netlist_board.py` 只读** ★ |
| ★**追加式 (老字一字不删不改)** ★ | ★**本段只 append, §1~§6 的内容与字节未动** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本机无板、无量具、无打印机 ⇒ 一切「实测」= 文件实读 + 脚本实跑** ★ |
| ★**不代拍** ★ | ★**选型 / 座体高度 h / 圆角口径 / 结构开口尺寸 = 只列事实与代价, 归 main→老板** ★ |

---

# ★★【ISS-294 追加段】★★ · 2026-11-17 · owner=mech-lead · cron `fb67af40`

> ★**本段是【追加】, 本页 §1~§6 与 ISS-290 追加段 (§9/§10) 的老字一个字没删、没改、没动** ★
> ★**帧声明 (★本追加段一切坐标 = 帧: `B160x100` (160×100 台架板)· 与本页 §1 逐字对齐★)** ★
> ★**来由**: ★**ISS-290 §5.6 的 E-6 —— `J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做) ⇒ 本单接 E-6 的 MECH 那一半** ★
> ★**一句话**: ★**补第三条开口 `PORT_OPEN_USBC` (板边缺口) + 把两道闸的「恰好两条」改成【期望 id 集合 + 任意两条矩形不许完全相同】(★合并禁令不许松★)** ★
> ★**零写板 · 零落表 · 零改 `HW/` 与 `SW/` · 零改既有 MECH 判据脚本 · 零外发 · 不自签 issue_log (verify_by=main)** ★

## ★§11.1 为什么「边开口」跟另两条不是同一种开口 (★本单最关键的一条语义★)

| 项 (帧: `B160x100`) | ★**另两条 (检修口 / 调试口)** ★ | ★**第三条 (USB-C 边开口)** ★ |
|---|---|---|
| 几何类别 | ★**罩住一个器件的【洞】** ★ —— 四边都在板内 | ★**板【边界】上的【缺口】** ★ —— ★**另一侧是板外** ★ |
| 插头/探针从哪进 | 从板内某个方向 (器件上方 / 侧方) | ★**从板外沿板面插进板边** ★ (USB 是 demo 板【唯一的供电 + 数据入口】) |
| 开口 Y 的取法 | ★**居中于器件中心**: Y = [cy − OPEN_Y_eff/2, cy + OPEN_Y_eff/2] ★ | ★**不居中**: 下沿【锚在板边线 Y = 0.000】, 深度 = 座体平面尺寸 + 净距 ⇒ ★**板面矩形不随 h 变**; 随 h 变的是【Z 向窗口】★ |
| 为什么不能照抄另两条 | —— | ★**① 另两条的开口宽 `OPEN_X` = 10.20 是「罩排针」的定档宽; USB-C 两个壳体固定孔在 X 134.220 / 145.780 (外缘 133.895..146.105) ⇒ 开口至少 12.210 宽 ⇒ 10.20 装不下 ⇒ `open_x_spec` 对本条【不适用】** ★ ★**② 另两条的 Y 居中公式对「下沿 = 板边」的缺口【物理上不成立】(缺口没有中心)** ★ |
| 判据怎么写 | ★**M3 逐档: 居中矩形 + 单调 + 落框 + 不压 SoM + 最坏净距 ≥ CRIT** ★ | ★**M3 逐档 (边开口分支): 下沿必须锚在板边线 + X 必须 = (座体 `F.Fab` ∪ 两个固定孔外缘) ± (CRIT+TOL) + Y 深度 = max(座体 Y 深度, `OPEN_Y_eff(h)`) + (CRIT+TOL)** ★ |

## ★§11.2 几何自算 (★本单自算 · 帧: `B160x100` · 脚本 `logs/iss294/compute_iss294.py` → `logs/iss294/compute_iss294.json`★)

| 项 (帧: `B160x100`) | 值 | 证据级 |
|---|---|---|
| ★**`J_USB_C` 位置 / 封装** ★ | (140.000, 5.250), rot 0, `GCT USB4105-16P` (自绘, 原厂图纸 Rev B3) | ★`[实测]` 板读 |
| ★**座体 `F.Fab`** ★ | X 135.680..144.320 × Y 0.000..6.400 (8.640 × 6.400) ⇒ ★**Y 下沿 = 0.000 = 板边** ★ | ★`[实测]` 板读 |
| ★**座体 `F.CrtYd`** ★ | X 135.180..144.820 × Y **−0.500**..6.900 (9.640 × 7.400) ⇒ ★**座体自己的 courtyard 就越过板边 0.500** ★ | ★`[实测]` 板读 |
| ★**两个壳体固定孔 (NPTH)** ★ | (134.220, 2.625) 与 (145.780, 2.625); pad Ø0.650, ★**drill Ø0.762** ★ ⇒ 物理孔外缘 X 133.839..146.161 | ★`[实测]` 板读 (drill 口径) |
| ★**16 个信号焊盘** ★ | 单排 pitch 0.50, 焊盘 0.30 × 1.15, Y 中心 5.250 ⇒ 铜箔 Y 4.675..5.825; 焊盘行中心跨度 7.50 | ★`[实测]` 板读 + ★`[官网 转引]` GCT USB4105 Rev B3 (焊料尾总长 8.34±0.06 与 7.50 + 2×0.42 互证) |
| ★**必须清空区 (座体 ∪ 固定孔)** ★ | X 133.895..146.105 × Y 0.000..6.400 (12.210 × 6.400) | ★`[实测]` 板读 + `[推算]` |
| ★**结构净距余量** ★ | `CRIT` 0.60 + `TOL.fdm_part` 0.30 = **0.900 / 边** (沿用既有判据常量, 零新造) | ★`[实测]` 阈值来源 `MECH/check_board_frame_coords.py` |
| ★**边开口 (板边缺口)** ★ | ★**X 132.995..147.005 × Y 0.000..7.300 (宽 14.010, 深 7.300)** ★ | ★`[推算]` |
| ★**单边净距** ★ | X 0.900 / Y 0.900 ⇒ ★**最坏 0.600 = CRIT (刚好过)** ★; 到 drill 外缘 (133.839) 的净距 **0.844** ≥ CRIT ✓ | ★`[推算]` |
| ★**周边无冲突** ★ | 该开口矩形内除 `J_USB_C` 外★**无别的封装** (186 封装逐个查) | ★`[实测]` 板读 |
| ★**S6 的 20 个目标落位** ★ | 压该开口 **0** 条; 最小净距 **8.795** (`R_SEL_D3_P`) | ★`[实测]` |

## ★§11.3 h 三档 (★帧: `B160x100` · 座体真实高 h 仍是 `[0数据]` ⇒ 不许把 2.54 当事实★)

| h 档 (帧: `B160x100`) | `OPEN_Y_eff(h)` | 边开口板面矩形 | 说明 |
|---|---|---|---|
| 0.90 | 4.60 | X 132.995..147.005 × Y 0.000..7.300 | 缺口深度由座体平面尺寸 6.400 支配 ⇒ 7.300 |
| 2.54 | 4.60 | X 132.995..147.005 × Y 0.000..7.300 | ★**2.54 是现行假设, 不是事实** ★ |
| 4.00 | 5.80 | X 132.995..147.005 × Y 0.000..7.300 | 深度仍由 6.400 支配 ⇒ 7.300 |

★**⇒ 三档板面矩形同值, 这不是偷懒, 是物理结论**: ★**缺口在板面内的深度由座体的【平面尺寸】(Y 深 6.400) 支配, 不由座体【高度】h 支配 ⇒ 随 h 变的是【Z 向窗口】(结构件在插头进出方向留的净空高) = `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80** ★
★**Z 向窗口是本单【无法在板面矩形里表达】的一条 (★它不在板面坐标里★) ⇒ 已登记 need 给 main→boss (见 §11.5)** ★
★**座体高参照**: ★**BOM `HW/BOM_v1.csv:76` (`J_TYPE_C` 同族) 记「主体高 3.50 mm」[实测]; `J_USB_C` 自身的座体高仍是 `[0数据]` (GCT USB4105 图纸文本里同时出现 3.31 与 3.50 两个高度数, 未看图不能判定哪个是座高) ⇒ 若按 3.50 取, `OPEN_Y_eff(3.50)` = 5.30 ⇒ 三档的 4.00 档 (5.80) 已覆盖 ✓** ★

## ★§11.4 立柱 / 螺钉头外扩三档 (★帧: `B160x100` · 固定方式未定 ⇒ 缺口 X 还可能更宽★)

| 螺钉头 / 立柱外径 D (帧: `B160x100`) | 每侧外扩 (D − 0.65)/2 | 边开口 X | 边开口宽 | 依据 |
|---|---|---|---|---|
| 2.60 | 0.975 | 132.020..147.980 | 15.960 | ★`[官网 转引]` GCT USB4105 Rev B3 图纸壳体柱尺寸「2x 2.60」★ (★柱宽与孔径哪一项是横向宽需看图 ⇒ 保守取用★) |
| 3.00 | 1.175 | 131.820..148.180 | 16.360 | ★`[推算]` M2 立柱外径常见值 (★`[0数据]`: 未选型★) |
| 3.80 | 1.575 | 131.420..148.580 | 17.160 | ★`[推算]` M2 螺钉头外径常见值 (★`[0数据]`: 未选型★) |

★**⇒ 代价**: ★**缺口每侧多让 1 mm, 结构件在这条边上少一条 14 × 2 mm 的承力带** ⇒ **这是结构件强度/刚度的取舍, 归 main→老板** ★
★**⇒ 本单在机器块里登记的是【不含立柱/螺钉头】的最小合法值 (X 132.995..147.005) ⇒ 等固定方式定了, 缺口 X 按本表取用, 并同步改机器块与两道闸的复算值** ★

## ★§11.5 归 main → 老板拍的四条 (★本单只交几何 + 代价 + 建议, 不代拍★)

| # (帧: `B160x100`) | 事实 | 代价 A (按本单登记值) | 代价 B (按 §11.4 外扩) | 谁拍 |
|---|---|---|---|---|
| 1 | ★**缺口 X 最小合法值 = 132.995..147.005 (宽 14.010), 最坏单边净距 0.600 = CRIT 刚好过** ★ | 缺口窄 ⇒ 承力带多 | ★**缺口每侧多让 0.975..1.575 ⇒ 结构件这条边少 14 × 2 mm 的带** ★ | ★**main → 老板** ★ |
| 2 | ★**缺口 Y 向深度 7.300 是按【结构件内壁与板边齐平】的最坏假设算的; 若内壁外移 t, 深度可缩到 t** ★ | 深度 7.300 (保守) | 深度缩到 2.000 左右 ⇒ 结构件内腔让出 5 mm | ★**main → 老板** (结构方案) ★ |
| 3 | ★**Z 向窗口 (插头过孔净空高) = `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80, 不在板面坐标里, 本页只能登记不能验** ★ | 板面矩形照 §11.3 | Z 向窗口跟结构件外形一起定 ⇒ 归结构方案 | ★**main → 老板** ★ |
| 4 | ★**口径分叉: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 的 `J_USB_C` 行 verdict 仍写「可装 / 结构侧缺一条边开口规格」(那是 ISS-290 的交卷物, 本单一个字节不许动) ⇒ 本页 §10.1 已改成「边开口规格已补」** ★ | 两页口径分叉 | 让 ISS-290 那行加一句「已由 ISS-294 补」⇒ 两页一致 | ★**main** ★ |

## ★§11.6 两道闸改了什么 (★合并禁令不许松★)

| 闸 (帧: `B160x100`) | 改前 | 改后 (★追加式, 另两条开口的老判据一个字没删★) |
|---|---|---|
| ★**`MECH/check_onepass_mech_sync.py` M2** ★ | ★**`len(openings) != 2` (条数断言) + M2b 只比两条** ★ | ★**期望 id 集合断言 = {PORT_OPEN_DEBUG, PORT_OPEN_UART, PORT_OPEN_USBC} (恰好三条, 一条不少一条不多) + M2b 改成【任意两条矩形不许完全相同】(合并成一条 / 把 USB-C 并进另两条 ⇒ 照样红) + M2c 合并缺口复算改成只取 `merged_opening.covers` 点名的两条 (★不然第三条会把 `len(conns) == 2` 悄悄跳过 ⇒ 防线反而松了★)** ★ |
| ★**`MECH/check_onepass_mech_sync.py` M3** ★ | 只有【罩器件的洞】那一种规则 | ★**加【边开口分支】: 下沿必须锚在板边线 + X 必须 = (座体 `F.Fab` ∪ 两个固定孔外缘) ± (CRIT+TOL) + Y 深度 = max(座体 Y 深度, `OPEN_Y_eff(h)`) + (CRIT+TOL) + 逐档单调/落框/不压 SoM/最坏净距 ≥ CRIT; 另两条走的还是老规则** ★ |
| ★**`MECH/check_onepass_struct_crosscheck.py` N3** ★ | ★**`len(openings) != 2` + `sorted(ids) != [DEBUG, UART]`** ★ | ★**期望 id 集合断言 = 三条 (ISS-290 页的两条 + MECH_SYNC 页的第三条) + 任意两条矩形不许完全相同 + 三条逐档分别验 (第三条逐档进循环) + 加 N3b: 两页的老开口必须逐字一致 (同一份规格不许分叉)** ★ |
| ★**`MECH/check_onepass_struct_crosscheck.py` N4** ★ | 必清空区 2 条 | ★**必清空区 2 ⇒ 3 条 (加 `MC_USBC` = 座体 ∪ 两个固定孔外缘), 20 个 S6 目标位到它净距 ≥ CRIT** ★ |

## ★§11.7 本段边界 (★自证口径★)

| 边界 (帧: `B160x100`) | 怎么自证 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**板 / `.kicad_pro` / 网表 / 脚表 / BOM 五件 md5 + 板 mtime 跑前跑后逐字节相同 (机器闸 M5 / N6)** ★ |
| ★**零改 `HW/` 与 `SW/`** ★ | ★**只读板与网表; `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 一个字节不许动** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_board_frame_coords.py` / `MECH/check_demo_struct_truth.py` / `MECH/board_port_opening_s6_check.py` 一个字节不许动** ★ |
| ★**追加式** ★ | ★**另两条开口 (`PORT_OPEN_DEBUG` / `PORT_OPEN_UART`) / `merged_opening` / `consts` / 另两条 `items[]` 一个字没改** ★ |
| ★**不代拍** ★ | ★**结构开口尺寸 / 立柱外径 / Z 向窗口 = 只列事实与代价, 归 main→老板** ★ |
| ★**零外发** ★ | ★**不发邮件 / 不询价 / 不问询 / 不采购; 查不到就写 `[0数据]` + 降级** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |

---

# ★★【ISS-278 续做追加段】★★ · 2026-11-17 17:5x · owner=mech-lead

> ★**来由**: ★**2026-11-17 08:22:12 网关重载把 08:14 那一派整段截断 ⇒ 本单主体由 09:13~09:30 那一趟补完并交卷;
> ★**17:4x 这一趟是【续做验收】** ⇒ 实跑任务书 §③ 全部验收命令 ⇒ ★**发现两处真问题** ★
> ★**① 我的新闸 M5 覆盖面被悄悄削掉一半 (本单可自修 ⇒ 已修)** ★
> ★**② `MECH/check_demo_struct_truth.py --selftest` 现在 rc=1 (★根因在别处 ⇒ 本单不许改那个脚本 ⇒ 升级给 main★)** ★

## ★§12.1 ★机器闸 M5 的覆盖面缺口与订正 (★本单可自修 ⇒ 已修★) ★

> ★**帧: 全部台账管理口径 (★与坐标无关★)** ★

### ★§12.1.1 缺口是怎么发现的 (★实测, 不是推算★) ★

| 环节 | 事实 | 证据级 |
|---|---|---|
| 任务书 §③ 要求 | ★**「M5 受保护 5 件 md5 逐字节不变 (板 / `.kicad_pro` / 网表 / 脚表 / BOM)」** ★ | ★`[实测]` (任务书原文) ★ |
| 本闸原先的实现 | ★**`for rel, base in CFC.PROTECTED.items()`** ⇒ ★**只查 `CFC.PROTECTED` 里有的件** ★ | ★`[实测]` (本机实读 `MECH/check_onepass_mech_sync.py`) ★ |
| ★**`CFC.PROTECTED` 现在的内容** ★ | ★**只有 2 件** (板 `611b869e…` / `.kicad_pro` `3e504d2b…`) ⇒ ★**网表 / 脚表 / BOM 三件不在里面** ★ | ★`[实测]` (本机实读 `MECH/check_board_frame_coords.py` L78-81) ★ |
| 为什么会缩 | ★**ISS-286 (★2026-11-17 12:44★) 把 `PROTECTED` 从 5 件改成 2 件** —— 网表/脚表/BOM 改由【落表台账】管 (★病根 = 判决源选错了 ⇒ 修法落在取值来源上★) ★ | ★`[实测]` (ISS-286 注释原文) ★ |
| ⇒ **净效果** | ★**本闸的 M5 覆盖面从 5 件悄悄缩成 2 件 = 任务书 §③ 要求的「M5 受保护 5 件」没兑现** ⇒ ★**3 件真源一度【没人管】** ★ | ★`[推算]` (由上两条实读直接得出) ★ |

### ★§12.1.2 订正后的 M5 (★5 件一件都不少·分两段★) ★

| 段 | 管哪几件 | 判决源 | fail-closed 条件 (★一条不许放宽★) |
|---|---|---|---|
| ★**M5a** ★ | ★**板 / `.kicad_pro` (2 件)** ★ | ★**基线写死** (`611b869e…` / `3e504d2b…`) ★ | ★**与基线不等 ⇒ 红; 文件缺失 ⇒ 红** ★ |
| ★**M5b** ★ | ★**网表 / 脚表 / BOM (3 件)** ★ | ★**落表台账链头** (`HW/SCHEMATIC_LANDING_V1_LANDED.md`) ★ | ★**① 台账读不到 ② 台账里查不到任何登记 ③ 链头取不准 ④ 链头无落表单号 ⑤ 链断了/不唯一 ⑥ 台账里有记录不在链上 (孤儿) ⇒ 任意一条成立 ⇒ 判红; 另: 盘上 md5[:12] ≠ 链头 ⇒ 判红** ★ |

★**⇒ 净效果 (★这才是 M5 该有的行为★)**: ★**合法落表 (台账链头前移) ⇒ 绿; 偷改真源而不更新台账 ⇒ 红; 台账本身坏掉 ⇒ 红 (不许静默判绿)** ★
★**⇒ 与 ISS-286 的 C4 同构** (★只读 import `CFC.ledger_state` / `CFC.ledger_records` / `CFC.LEDGER_CANON` ⇒ 阈值与口径零漂移★) ⇒ ★**本单一个字不改既有 MECH 判据脚本** ★

### ★§12.1.3 自证 (★新增反向用例 ⑦b★) ★

| 用例 | 动作 | 期望 | 本机实跑 |
|---|---|---|---|
| ★**⑦b (★新增★)** ★ | ★**偷改台账管理件 (`HW/netlist_v1.csv`) 而台账不更新** ★ | ★**M5b 必须红** ★ | ★**✅ 命中 M5b 断言 · md5 `37f62ac3` ⇒ `61e3019d` (确实改了: True)** ★ |
| ★**⑧ (★已修★)** ★ | ★**自检跑完, 真件 5 件 md5 仍逐字节不变** ★ | ★**5 件一件不少** ★ | ★**✅ `demo_mainboard.kicad_pcb=611b869e` / `demo_mainboard.kicad_pro=3e504d2b` / `netlist_v1.csv=37f62ac3` / `netlist_v1_pins.csv=a4270120` / `BOM_v1.csv=5d02bece`** ★ |

★**⇒ 附带修掉的一处自证虚标**: ★**⑧ 原先只遍历 `CFC.PROTECTED` ⇒ 实查 2 件却在打印里宣称「5 件」** ⇒ ★**现在实查件数与宣称件数一致, 且少于 5 件直接判红** ★

## ★§12.2 ★受保护 5 件的 md5 基线变更留档 (★不是本单改的★) ★

> ★**帧: 与坐标无关 (★真源台账口径★)** ★

★**★ 任务书 §③ 给的基线 (★2026-11-17 07:2x main 实测★) vs 本机现值 (★17:4x 实读★) ★★ ★

| 件 | 任务书基线 (★07:2x★) | 本机现值 (★17:4x★) | 谁改的 | 本单有没有参与 |
|---|---|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | ★**`611b869e13518c3c023fb178f91a0075`** ★ | —— | ★**没动** ★ |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | ★**`3e504d2be83152e337949723e909be1b`** ★ | —— | ★**没动** ★ |
| `HW/netlist_v1.csv` | `e06c1dd633566aa44732762c2ff99d1c` | ★**`37f62ac3f0b81d92ca7d48fdea717f07`** ★ | ★**ISS-283 (hw-lead) 12:30 的授权落表** ★ | ★**没动** ★ |
| `HW/netlist_v1_pins.csv` | `287e7861a0d1007748d92d9fbecdd490` | ★**`a4270120454aedf7a23c92cd8985c8a6`** ★ | ★**ISS-283 (hw-lead) 12:30 的授权落表** ★ | ★**没动** ★ |
| `HW/BOM_v1.csv` | `94642d07a69e8d60dd2af57f69b93607` | ★**`5d02bece9477ffce5fbe0193c7d5cce4`** ★ | ★**ISS-283 (hw-lead) 12:30 的授权落表** ★ | ★**没动** ★ |

★**⇒ 三件台账管理件的现值与落表台账链头【逐字对上】** (★链头 `37f62ac3f0b8` / `a4270120454a` / `5d02bece9477`, 落表单号 = `ISS-283`, 链长 10 / 8 / 7, 记录 10 / 10 / 10★) ⇒ ★**这是【合法落表】, 不是「真源被偷改」** ⇒ ★**M5b 判绿是对的** ★
★**⇒ 本单 (ISS-278) 的「零写板 / 零落表」自证不受影响**: ★**板与 `.kicad_pro` 两件逐字节不变 (硬基线) ★; 三件台账管理件的变更发生在 12:30, 早于本趟 17:4x 续做, 且由 ISS-283 授权落表 + 台账链头对上 ⇒ 与本单无关** ★
★**⇒ 但任务书 §③ 那五个「基线 md5」现在已经过时** ⇒ ★**本单不擅自改任务书 (★那是 main 的文件★) ⇒ 升级给 main (★见交卷单 B5.5★)** ★

## ★§12.3 ★`MECH/check_demo_struct_truth.py --selftest` rc=1 (★根因不在本单 ⇒ 不许本单改★) ★

> ★**帧: 与坐标无关 (★台账行格式口径★)** ★

### ★§12.3.1 现象 ★

| 项 | 实测 |
|---|---|
| 命令 | `python3 MECH/check_demo_struct_truth.py --selftest` |
| 现值 | ★**rc=1** ★ (任务书 §③ 期望 rc=0) |
| 报错 | ★**`AssertionError: 没找到台账最新记录那一行`** (在 `break_head_ticket()` 里) ★ |
| 该脚本是否被本单动过 | ★**没有** —— md5 `6972b867c8243bc971408f972dc7727e` 与 08:26 基准逐位相同 ⇒ ★**属任务书 §④「零改既有 MECH 判据脚本」点名不许动的件** ★ |

### ★§12.3.2 根因 (★本机实跑定位, 已复现★) ★

`break_head_ticket()` 的作用是: ★**在落表台账里找到「链头那一行」, 把它的单号改坏 ⇒ 验证反向用例 R5a 必红** ★
它的命中条件是 ★**三样同时成立**: ★**(a) 该行含 `head[:12]` ② (b) 该行以 `|` 开头 ③ (c) 该行含 `ISS-`** ★

★**⇒ ISS-283 12:30 的落表行格式变了 ⇒ 三条同时不成立** ★:

| 台账行 | 格式 | 含 `head[:12]`? | 以 `|` 开头? | 含 `ISS-`? | 命中 |
|---|---|---|---|---|---|
| ★**L1069 (ISS-257 旧格式)** ★ | `\| ★**ISS-257** ★ \| ★**`HW/netlist_v1.csv`** (表A) ★ \| … \| `e06c1dd6…` \|` | ✗ (那是旧链头) | ✔ | ★**✔** ★ | ★**当时能命中** ★ |
| ★**L1371 (ISS-283 新格式)** ★ | `\| ★**`HW/netlist_v1.csv`** ★ \| `87f2f792…` \| `37f62ac3…` \| ★**是**★ \|` | ★**✔** ★ | ★**✔** ★ | ★**✗ (单号挪到了别的行★)** ★ | ★**命中不了 ⇒ assert 炸** ★ |

★**⇒ 本机实跑验证 (★只读沙盒, 真台账一个字节不碰★)**: ★**把 L1371 这一行补上 `ISS-283` 后, 同一段命中逻辑 `hit` 从 0 变成 1 ⇒ 根因确认** ★

### ★§12.3.3 结论与归属 (★本单只登记, 不代修★) ★

| 项 | 结论 |
|---|---|
| 是不是本单造成的 | ★**不是** ★ —— ① 本单 09:29 跑时 rc=0; ② 12:30 的台账改写是 ISS-283 的授权落表; ③ 本单没碰那个脚本 (md5 未变) |
| 本单能不能修 | ★**不能** —— 那个脚本属任务书 §④ 点名「零改既有 MECH 判据脚本」; 且根因在【台账行格式】不在脚本逻辑 |
| 代价 | ★**`MECH/check_demo_struct_truth.py --selftest` 现在 rc=1 ⇒ 任务书 §③ 那一条验收命令红** ⇒ ★**本单交卷单必须如实写清, 不许假装它绿** ★ |
| 建议修法 (★只列, 不代拍★) ★ | ★**① 改台账行格式 (让 ISS-283 的行也带单号) —— 但那是台账的写法契约, 归落表链; ② 或改 `break_head_ticket()` 的命中条件 (★三选一改成【含 head[:12] + 以 `|` 开头】即可, 不必强求同一行含 ISS-★) —— 那是 `MECH/check_demo_struct_truth.py`, 属 MECH 侧但本单边界不许动** ★ |
| 归谁 | ★**升级给 main** (★见交卷单 B5.5 + 分片 need★) ⇒ ★**本单不自签 `state/issue_log.yaml`, 不代 main 派单** ★ |

## ★§12.4 本续做段的边界 (★自证口径★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板 / 零落表** ★ | ★**板 / `.kicad_pro` 两件硬基线逐字节不变; 三件台账管理件的变更发生在 12:30 (ISS-283 授权落表), 早于本趟, 与本单无关** ★ |
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_demo_struct_truth.py` / `MECH/check_board_frame_coords.py` / `MECH/service_port_check.py` / `MECH/board_port_opening_s6_check.py` / `MECH/jd_y0_feasibility.py` / `MECH/verify_budget.py` 六个 md5 与 08:26 基准逐位相同 ⇒ 本趟只改【自己新建的】`MECH/check_onepass_mech_sync.py`** ★ |
| ★**零改 HW / SW** ★ | ★**`HW/` 与 `SW/` 零字节写入 (只读)** ★ |
| ★**追加式** ★ | ★**本页 §1~§11 (含 ISS-278 主体 + ISS-290 + ISS-294 三段) 一个字没删没改; 本续做段 = §12 追加在末尾** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本机无板; 一切「实测」= 文件实读 + 脚本实跑** ★ |

## ★★§ISS-295-订正覆盖表 · 「板只改一次」结构侧输入认领全表同步 (★帧: `B160x100` · mech-lead · 2026-11-17 · ISS-295★)★★

> ★**本节是【追加】**: ★**本页 §1~§6 / ISS-290 追加段 / ISS-294 追加段 / ISS-278 续做追加段 的老字一个字没删、没改、没动** ★
> ★**本节干什么**: ★**ISS-295 给「板只改一次」那一趟发了一份结构侧输入认领全表 (`MECH/BOARD_ONEPASS_MECH_CLAIMS.md`); 本节把本页里【已被 ISS-294 推翻的老结论】逐条列出并【逐字】覆盖 ⇒ 防止有人只 grep 老行就拿走错结论** ★
> ★**闸**: ★**`python3 MECH/check_mech_verdict_freshness.py` ⇒ rc=0** ★ (★判据 = 逐字短语命中, 零行号依赖★)

★**现状句 (★两页必须逐字一致·不许各写各的★)**:

★**【现状句 · ISS-295 · 帧 `B160x100`】USB-C 边开口规格已补: 开口 `PORT_OPEN_USBC` = X 132.995..147.005 @ 板边 Y = 0 · 必须清空区 X 133.895..146.105 · h 三档 0.90/2.54/4.00 · Z 向窗口 `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80** ★

★**老结论逐条覆盖表 (★老字保留作历史留痕; 每一处都必须被本节逐字引用; ★本表只是【引用】, 不许当成现状★)**:

| ★hit id★ | ★老结论所在小节 (帧 `B160x100`)★ | ★逐字锚点 (★留痕原样·不许改写★)★ | ★老结论说过什么 (★逐字·已过期·不再作数★)★ | ★处理 (★ISS-295 做了什么★)★ |
|---|---|---|---|---|
| ★MS-1★ | ★§10.3 另两条会改板的口径★ | 现有 MECH 规格 (检修口 / 调试口两条) 里没有这条边开口 | ★「`J_USB_C` 边开口缺口 … 现有 MECH 规格 (检修口 / 调试口两条) 里没有这条边开口」★ | ★★**已过期** ⇒ ISS-294 已补第三条开口 `PORT_OPEN_USBC` (X 132.995..147.005 @ 板边 Y = 0 · 必须清空区 X 133.895..146.105); 老字保留作历史留痕 ⇒ **引用本节, 不引用本行** ★★ |
| ★MS-2★ | ★ISS-294 追加段 · 来由★ | `J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做) | ★「`J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做) ⇒ 本单接 E-6 的 MECH 那一半」★ | ★★**已过期** ⇒ E-6 的 MECH 半边已由 ISS-294 做完 (规格 + 两道闸的 id 集合断言); 本行是【当时来做这件事的来由】, 不是现状 ★★ |
| ★MS-3★ | ★§11.5 归 main → 老板拍的四条 · 第 4 条★ | verdict 仍写「可装 / 结构侧缺一条边开口规格」 | ★「`J_USB_C` 行 verdict 仍写「可装 / 结构侧缺一条边开口规格」 ⇒ 两页口径分叉」★ | ★★**已过期** ⇒ CROSSCHECK 那页已由本节的覆盖表 + 该页自己的 ISS-295 订正覆盖节覆盖 ⇒ **两页现状句现在逐字一致**; 本行保留作【分叉曾经存在过】的留痕 ★★ |

★**★本节的纪律 (★自证口径★)**:

| 项 | 口径 |
|---|---|
| ★**追加式** ★ | ★**老字一个字没删、没改、没动; 本节只【追加】** ★ |
| ★**机器块不许动** ★ | ★**§7 机器块的 `openings[]` / `rect` / `tiers` / `verdict` 一个字节不许改; XC-4 的老字是【机器块里的历史留痕】** ★ |
| ★**不代拍** ★ | ★**开口尺寸 / Z 向窗口 / 立柱外径 / 座体真实高 h = 只列事实与代价, 归 main→老板** ★ |
| ★**闸** ★ | ★**`python3 MECH/check_mech_verdict_freshness.py` ⇒ rc=0; `--selftest` ⇒ rc=0 (★反向用例 ≥4 条·沙盒副本上跑★)** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本机无板、无量具、无打印机 ⇒ 一切「实测」= 文件实读 + 脚本实跑** ★ |

## ★★§ISS-296-收工清单 · 「板只改一次」改完板以后【同一次】必须做完的重锚动作 (★强制项★)★★

> ★**本节是【追加】**: ★**本页 §1~§6 / ISS-278 续做段 / ISS-290 追加段 / ISS-294 追加段 / ISS-295 订正覆盖表 —— 老字一个字没删、没改、没动** ★
> ★**性质**: ★**收工清单 = 板那一趟【改完板以后】必须【同一次】做完的那一组事** ★
> ★**单号**: ISS-296 (mech-lead · 2026-11-17 20:1x · 内部活 · 零写板 · 零落表) ★
> ★**闸**: ★**`python3 MECH/check_board_frame_coords.py`** + ★**`python3 MECH/check_demo_struct_truth.py`** ⇒ 两道闸现在都有【合法改板】通道 ★
> ★**同源探针**: ★**`python3 logs/iss296/probe_ledger_reading_same_source.py`** ⇒ `IDENTICAL: True` (★MECH 侧台账解析器 vs SW 侧 ISS-284 定版闸的解析器 · 同一份台账读出逐字相同的链头/链/产出单号★) ★

### ★★M0 · 为什么这一节必须先落在板那一趟【之前】 ★

★★**「板只改一次」那一趟授权板合法改一次 ⇒ 板 md5 会合法地变一次** ★
⇒ ★**凡是【把板 md5 写死成基线】的闸, 那一趟当天全部红** ★
⇒ ⇒ ★**而收工验收时的假红, 历史上【每一次】都被误读成「板改坏了」** ★
⇒ ⇒ ★**有人去「改板凑绿」⇒ ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
⇒ ⇒ ★**最坏 = 把 `C_VBUS_GND` 装回板上 (ISS-289 交卷单自己点名的 2-4 周 + ¥4-8K)** ★
⇒ ★**所以: 合法改板通道必须【赶在开工前】落地, 而且它【本身一个字节都不碰板】** ★

### ★★M1 · 落表台账那一行必须长什么样 (★★这是给 main 的接口格式★★) ★

★**格式契约 (★main 立的口径 · ISS-275 §1⑧★)**: ★**每受管文件一行 = 「单号 | 文件名 | 改前 md5 | 改后 md5」四项同行** ★

| 单号 | 文件 | 前 | 后 | 变了? |
|---|---|---|---|---|
| ★**ISS-XXX** ★ | ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`<新板 md5>`** ★ | ★**是 (合法改板·板只改一次)** ★ |
| ★**ISS-XXX** ★ | ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**否 (逐字节不变)** ★ |

★**三条硬要求 (★MECH 侧两道闸按这三条读★)**:
1. ★**板与 `.kicad_pro` 必须成对两行, 同一个单号** ⇒ ★**只写一行 ⇒ 判红** ★ (★`.kicad_pro` 真没变时也要写「否 (逐字节不变)」那一行★)
2. ★**一行不许同时写两件两值** ⇒ ★**一行两件两值 = 歧义行 ⇒ MECH 侧当它【不算变更行】⇒ 判红** ★
3. ★**单号必须出现在【行内】或【该行所属的小节标题】里** ⇒ ★**行内优先; 行内没有就继承所属小节标题的单号** ★ (★两处都没有 ⇒ 判红: 四项不齐★)

★**MECH 侧两条闸读这一行的判据 (★判据只许变严, 不许放松★)**:
| 序 | 判据 | 不满足时 |
|---|---|---|
| ① | ★**保护基线自证** ★ 闸里写死的基线 md5 必须能在台账里与该文件【同行】查到 | ★**只改闸里的基线而台账没记 ⇒ 判红** ★ |
| ② | ★**台账里没有变更行** ⇒ 盘上 md5 必须 == 基线 (★纯 md5 硬保护★) | ★**手改板 ⇒ 判红** ★ |
| ③ | ★**台账里有变更行** ⇒ 链头唯一 / 链不断 / 链头有单号 (★fail-closed 三条★) + 链头那一行四项齐全且与链头逐字对上 + ★**保护基线必须留在链尾**★ + ★**盘上 md5 必须 == 台账链头**★ | ★**取不准 ⇒ 一律判红** ★ |
| ④ | ★**同组受保护件成对覆盖** ★ 一次合法改板必须覆盖同组全部件 | ★**只来一条 ⇒ 判红** ★ |

### ★★M2 · 收工后【同一次】必须做完的重锚清单 (★MECH 侧 · 强制项★) ★

| # | 动作 | 判据 / 复现命令 | 不做的后果 |
|---|---|---|---|
| ★**M2-1** ★ | ★**板 / `.kicad_pro` 那两个写死基线【不许手改】** ⇒ ★**走合法改板路径 (M1 那两行)** ★ | ★**`python3 MECH/check_board_frame_coords.py` (C4) + `python3 MECH/check_demo_struct_truth.py` (G5b) ⇒ rc=0** ★ | ★**手改基线 = 悄悄换真源 ⇒ 判红; 不改 ⇒ 假红** ★ |
| ★**M2-2** ★ | ★**ISS-286 已经台账化的那三件 (网表 / 脚表 / BOM) 的链头** ⇒ 板那一趟若再落表 ⇒ ★**链头要同一次前移** ★ | ★**同一次跑 `python3 MECH/check_board_frame_coords.py` (C4 的台账管理三件)** ★ | ★**链头不前移 ⇒ 盘上 ≠ 链头 ⇒ 判红 (★本单要求【证明】它跟上了 ⇒ 就是这条命令的输出★)** ★ |
| ★**M2-3** ★ | ★**三条开口的几何复算**: ★**`PORT_OPEN_DEBUG`** ★ / ★**`PORT_OPEN_UART`** ★ / ★**`PORT_OPEN_USBC`** ★ 的 rect + 固定孔清空区 + ★**`J_USB_C` 座体 `F.Fab`** ★ | ★**`python3 MECH/check_onepass_struct_crosscheck.py` + `python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0** ★ | ★**板边 / 落位一变 ⇒ 三条开口的净距判定全部过期** ★ |
| ★**M2-4** ★ | ★**S6 那 20 个落位坐标 (`PCB_PART_POS` 串) 复算** (★真实位移只有 `R_SEL_D3_P` 一处, 但整串都要重出★) ⇒ ★**落位 / 禁入区 / 承区判定同一次复算** ★ | ★**同上两条闸 (ISS-290 的 N2/N3/N4 净距核对)** ★ | ★**落位坐标与板不一致 ⇒ 承区判定建立在旧坐标上** ★ |
| ★**M2-5** ★ | ★**E-1 的排针 land 重画 (1.27mm) 之后, 必须复验净距, 不许压 SoM 座** ★ (★main 18:4x 裁决★) | ★**`python3 MECH/check_onepass_struct_crosscheck.py` (N2/N3/N4)** ★ | ★**6 个焊盘的走线本来就要重布 ⇒ 同一次做完; 压 SoM 座 = 不可装** ★ |
| ★**M2-6** ★ | ★**帧标 id 统一** (`B160x100` vs `160x100-bench` vs `60x30-setA` / `F30A`) ★**—— 本单【只登记, 不代裁】** ★ | ★**待 main → 老板 (U-274-6)★** | ★**id 不统一 = 后期坐标漂移** ★ |

### ★★M3 · 收工那天【全仓 9 道钉板 md5 的闸】都要绿 (★不许只修 MECH 两道★) ★

★**全仓清单 (★机器生成·可复核★)**: ★**`state/board_md5_pinned_gates.md`** ★ (★生成脚本 `state/_gen_board_md5_pinned_gates.py` · 机器可读 JSON `state/board_md5_pinned_gates.json`★) ★

| # | 闸文件 | 归口 | 「合法改板」通道状态 (2026-11-17 20:1x) |
|---|---|---|---|
| 1 | `HW/check_fsin_rootcause.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 2 | `HW/check_g1a7_selection_landed.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 3 | `HW/check_onepass_commit_order.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 4 | `HW/check_onepass_preflight_coverage.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 5 | `HW/check_pin_function_labels.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 6 | `HW/check_workpack_state_values.py` | ★**hw-lead** ★ (ISS-297) | ★**已建 (ISS-297)★** ★ |
| 7 | ★**`MECH/check_board_frame_coords.py`** ★ | ★**mech-lead** ★ (★**ISS-296 本单**★) | ★**★已建 (C4)★** ★ |
| 8 | ★**`MECH/check_demo_struct_truth.py`** ★ | ★**mech-lead** ★ (★**ISS-296 本单**★) | ★**★已建 (G5b)★** ★ |
| 9 | `SW/tools/check_onepass_sw_sync.py` | ★**sw-lead** ★ (ISS-298) | ★**已建 (★ISS-284 口径★)** ★ |

★★**【ISS-296 cont2 · 2026-11-17 20:5x · mech-lead · 改数留痕】** ★★上面 M3 表里 ★**第 1~6 行 (HW 6 道) 的「合法改板」通道状态单元格**: ★**旧值 「待建」 ⇒ 新值 「已建 (ISS-297)」** ★ ★
★★**依据**: ★**`HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` §2 (★hw-lead 20:1x 交卷·6 道 HW 闸全部接上通道★) ⇒ 6 道各自 `--selftest` 通道用例 10/10 通过 (★`check_fsin_rootcause.py` 25/25 · `check_g1a7_selection_landed.py` 21/21 · `check_onepass_commit_order.py` 21/21 · `check_onepass_preflight_coverage.py` 21/21 · `check_pin_function_labels.py` 通道 10/10 ★★(该闸另有 18 条 ISS-257 起的既有失效, 属别单范畴, 本页不代裁)★★ · `check_workpack_state_values.py` 20/20★)★ ★
★★**本单只改这 6 个单元格的文字, M3 表其余 3 行 (§7/§8 MECH 两道 + §9 SW 那道) 一个字节没动, 本节其余段落 (M0/M1/M2/M4/M5) 一个字节没动** ★
★★**改前副本留证**: ★**`logs/iss296/msync_before_iss296_cont2.md` (96,970 B · 20:57)** ★ ⇒ ★**老字逐字可对 ★**
★★**注意 (★给 main 的语义★)**: ★**「已建」= 通道已接上, ≠ 收工那天 9 道一定同时绿** ⇒ ★**第 5 道 `HW/check_pin_function_labels.py` 现在主模式仍 rc=1 (18 条既有缺陷·改前也是 rc=1) ⇒ 收工那天那 9 道要【同一次】全绿, 这一道的前置债在 hw-lead 那边, 不在 MECH 侧★** ★

★★**⇒ 收工那天: 9 道闸必须【同一次】全绿; 只绿 MECH 两道 = 一半收工清单等于没写** ★
★★**口径已被证明可行 (★不是猜的★)**: ★**`SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后【已不再硬钉板 md5】⇒ 全仓清单里根本找不到它** ★
⇒ ★**⇒ 「不硬钉」不是靠删断言, 是靠判决源换成【落表台账 + 合法改板记录】** ★

### ★★M4 · 本节【不代拍】的三条 (★归 main → 老板★) ★

| # | 待拍项 | 本单只做到哪一步 | 归谁 |
|---|---|---|---|
| ★**1** ★ | ★**帧标 id 统一** (`B160x100` / `160x100-bench` / `60x30-setA` / `F30A` 指同一批帧) ★ | ★**只登记 need, 一个 id 没改** ★ | ★**main → 老板 (U-274-6)** ★ |
| ★**2** ★ | ★**结构开口最终尺寸 + Z 向窗口** (`iss294_usbc_edge_opening_size_and_z_window`) ★ | ★**只登记 need, 一个尺寸没定** ★ | ★**main → 老板** ★ |
| ★**3** ★ | ★**落表批次 / 那一趟的单号** | ★**接口格式给了 (M1), 单号留给「出板那一趟」** ★ | ★**main** ★ |

### ★★M5 · 本节的边界 (★自证口径★) ★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | ★**板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` 双重自证 (交卷单 B4)** ★ |
| ★**零落表** ★ | ★**网表 / 脚表 / BOM 三个 md5 逐字节不变; 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本单零写入** ★ |
| ★**追加式** ★ | ★**本页 §1~§6 + ISS-278 / ISS-290 / ISS-294 / ISS-295 各段老字一字没删没改; 本节只追加** ★ |
| ★**只动 MECH 侧两道闸** ★ | ★**`MECH/check_board_frame_coords.py` + `MECH/check_demo_struct_truth.py`; 其余 MECH 脚本一个都没动** ★ |
| ★**不改别人的闸** ★ | ★**`MECH/check_onepass_mech_sync.py` / `MECH/check_onepass_struct_crosscheck.py` / `MECH/check_mech_verdict_freshness.py` 一个字节没动 (只跑做回归)** ★ |
| ★**不改 SW 侧** ★ | ★**`SW/tools/check_demo_panel_spec.py` 的 R6 逻辑一个字没动 (只读它的形状 + 在探针里读它的解析器)** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本机无板、无量具 ⇒ 一切「实测」= 文件实读 + 脚本实跑** ★ |
