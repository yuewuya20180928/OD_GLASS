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
  "frames_allowed": ["B160x100", "F30A", "P60x15"],
  "consts": {
    "open_x_spec": 10.20,
    "open_y_spec": 4.60,
    "crit": 0.60,
    "tol_fdm_part": 0.30,
    "edge_keepout": 0.80,
    "body_h_ref": 2.54,
    "body_h_ref_is_fact": false,
    "h_tiers": [0.90, 2.54, 4.00],
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
      "rect": {"x0": 137.850, "x1": 148.050, "y0": 54.300, "y1": 58.900},
      "x0_range": [137.850, 142.063],
      "y0_range_at_h_ref": [54.300, 55.330],
      "cl_x": 4.2125,
      "cl_y": 1.0300,
      "worst_cl_x": 3.9125,
      "worst_cl_y": 0.7300,
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
      "rect": {"x0": 13.790, "x1": 23.990, "y0": 66.300, "y1": 70.900},
      "x0_range": [13.790, 17.620],
      "y0_range_at_h_ref": [66.300, 67.330],
      "cl_x": 3.8300,
      "cl_y": 1.0300,
      "worst_cl_x": 3.5300,
      "worst_cl_y": 0.7300,
      "som_hits": 0,
      "evidence": "[实测]+[推算]+[0数据]"
    }
  ],
  "merged_opening": {
    "id": "PORT_OPEN_MERGED",
    "frame": "B160x100",
    "forbidden": true,
    "covers": "J_DEBUG+J_UART",
    "content_w": 126.2175,
    "open_w": 10.20,
    "cl_x": -58.00875,
    "gap_mm": 116.0175,
    "separation_dx": 123.56,
    "separation_dy": -12.00,
    "separation_straight": 124.141345,
    "evidence": "[实测]"
  },
  "led": {
    "id": "LED_G_WINDOW",
    "frame": "B160x100",
    "ref": "D_LED_G",
    "res_ref": "R_LED_G",
    "net": "LED_G_D",
    "current_origin": [101.25, 56.80],
    "current_res_origin": [5.90, 62.50],
    "current_net_len_mm": 93.492727,
    "full_height_bands": [
      {"x0": 1.550, "x1": 3.450, "y0": 1.450, "y1": 98.950},
      {"x0": 72.540, "x1": 73.660, "y0": 1.450, "y1": 98.950}
    ],
    "nearest_band": {"x0": 6.940, "x1": 8.250, "y0": 63.700, "y1": 67.900},
    "hypothesis_hole": {
      "id": "LED_G_HOLE_A",
      "title": "有结构光孔 (光孔把 LED 钉死)",
      "frame": "B160x100",
      "space": {"x0": 6.940, "x1": 8.250, "y0": 63.700, "y1": 67.900},
      "space_kind": "封装原点可放行窗口",
      "net_len_range_mm": [0.450, 0.965],
      "board_change": "要改 (D_LED_G 必须挪到光孔正下方)",
      "evidence": "[实测]+[推算]+[0数据]"
    },
    "hypothesis_nohole": {
      "id": "LED_G_NOHOLE_B",
      "title": "无结构光孔 (LED 位置只受电气+机械约束)",
      "frame": "B160x100",
      "space": {"x0": 1.550, "x1": 3.450, "y0": 1.450, "y1": 98.950},
      "space_kind": "封装原点可放行窗口 (整高自由带; 另有一条 X 72.540..73.660)",
      "net_len_range_mm": [0.450, 0.965],
      "board_change": "不用改 (现状 93.492727 也合法)",
      "evidence": "[实测]+[推算]"
    },
    "clearance_sweep": [
      {"clr": 0.00, "n_placeable": 1992, "corner_len_mm": 0.450},
      {"clr": 0.10, "n_placeable": 2016, "corner_len_mm": 0.559},
      {"clr": 0.20, "n_placeable": 2031, "corner_len_mm": 0.680},
      {"clr": 0.50, "n_placeable": 2075, "corner_len_mm": 0.965}
    ]
  },
  "connectors": [
    {"key": "usb_c_ref", "mech_expected": "J_USB", "board_actual": "J_USB_C", "delta": "位号名不符", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "usb_c_position_mm", "mech_expected": [5.5, 22.5], "board_actual": [140.000, 5.250], "delta": "dX -134.500 / dY +17.250", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "uart_ref", "mech_expected": "J_UART", "board_actual": "J_UART", "delta": "一致", "affects_onpass": false, "owner": "-"},
    {"key": "uart_pins", "mech_expected": 4, "board_actual": 2, "delta": "差 2 脚", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "uart_pitch_mm", "mech_expected": 2.54, "board_actual": 0.50, "delta": "差 2.04", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "uart_position_mm", "mech_expected": [49.0, 6.0], "board_actual": [20.740, 70.000], "delta": "dX -28.260 / dY +64.000", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "jtag_ref", "mech_expected": "J_JTAG", "board_actual": "J_DEBUG", "delta": "位号名不符", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "jtag_pins", "mech_expected": 5, "board_actual": 4, "delta": "差 1 脚", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "jtag_pitch_mm", "mech_expected": 2.54, "board_actual": 0.50, "delta": "差 2.04", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "jtag_position_mm", "mech_expected": [52.0, 13.0], "board_actual": [144.300, 58.000], "delta": "dX -92.300 / dY +45.000", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "som_ref", "mech_expected": "U_SOM_RK3572", "board_actual": "J_SOM_P1..P4 (4 x 100 pads)", "delta": "位号+拓扑都不符", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "som_width_mm", "mech_expected": 40.0, "board_actual": 56.60, "delta": "差 16.60 (座体 F.Fab 并集)", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "som_height_mm", "mech_expected": 24.0, "board_actual": 46.20, "delta": "差 22.20 (座体 F.Fab 并集)", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "som_position_mm", "mech_expected": [33.0, 26.0], "board_actual": [42.000, 31.000], "delta": "dX -9.000 / dY -5.000 (四组阵心)", "affects_onpass": true, "owner": "hw-lead"},
    {"key": "board_width_mm", "mech_expected": 160.0, "board_actual": 160.0, "delta": "一致", "affects_onpass": false, "owner": "-"},
    {"key": "board_height_mm", "mech_expected": 100.0, "board_actual": 100.0, "delta": "一致", "affects_onpass": false, "owner": "-"},
    {"key": "board_thickness_mm", "mech_expected": 1.6, "board_actual": 1.6, "delta": "一致", "affects_onpass": false, "owner": "-"},
    {"key": "board_layers", "mech_expected": 8, "board_actual": 8, "delta": "一致", "affects_onpass": false, "owner": "-"},
    {"key": "board_corner_radius_mm", "mech_expected": 3.0, "board_actual": 0.0, "delta": "差 3.000 (Edge.Cuts 是 4 条直角 gr_line, 无圆角)", "affects_onpass": true, "owner": "hw-lead"}
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
| ★**零改既有 MECH 判据脚本** ★ | ★**`MECH/check_demo_struct_truth.py` / `MECH/service_port_check.py` / `MECH/board_port_opening_s6_check.py` / `MECH/jd_y0_feasibility.py` / `MECH/verify_budget.py` 一个字不许动 ⇒ 本单的新闸是【新建】文件 `MECH/check_onepass_mech_sync.py`** ★ |
| ★**零改 HW** ★ | ★**`HW/` 零字节写入** ★ |
| ★**零改 `MECH/BOARD_GEOM_30MM.md`** ★ | ★**它是「另一套基线」的事实登记 ⇒ 本页只【引用】** ★ |
| ★**零改别人的交卷单** ★ | ★**ISS-276 的交卷单 / 归一页一个字不许改 (只在归一页【追加式】订正 §3b/§4b/§6b/§7b/§8)** ★ |
| ★**零外发** ★ | ★**不发邮件 / 不询价 / 不问询 / 不采购 ⇒ 查不到就写 `[0数据]` + 降级方案** ★ |
| ★**证据分级** ★ | ★**每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`; 本页 `[官网]`/`[媒体]` = 0 条, 实物 `[实测]` = 0 条** ★ |
| ★**不替老板拍板** ★ | ★**座体高度 h / 结构光孔有否 / 亮度档 G-5 = 只列事实与代价, 归 main→老板** ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★**只走 `state/frag_write.py --agent mech-lead`** ★ |
| ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`** ★ |
