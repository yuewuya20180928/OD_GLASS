★★★★【main 2026-11-23 00:5x · ★★PCB 线 · 板只改一次那一趟的「板侧项全集」漏项补齐 · 纯分析 + 文档订正 + 机器闸 · 零写板 ★★】★★★★
★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 32 条板侧项里【没有「排针 land 0.50→1.27mm (E-1)」这一条】 ⇒ 那一趟做完, 实物排针照样装不进 ★**

★**派活方 = 项目总工 (main) · 2026-11-23 00:5x · cron fb67af40 (队列自动派活)★★**
★**来源 = main 2026-11-17 18:45 已拍死的 E-1 (★`state/fragments/pm.yaml` → `needs_from` → key `main_e1_e2_board_side_rulings_20261117` → `decision`/`decided_at` = 2026-11-17 18:45 / decided_by main★)★★**
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 事实 (★main 本机实读 + 实跑, 不抄任何 agent 报告★)

★**① main 已拍死的 E-1 (pm.yaml `main_e1_e2_board_side_rulings_20261117` 的 `decision` 原文逐字) ★**:
★**「E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画」** ★ + ★**「⇒ 板那一趟的板改清单 = Q_PG 三根线重画 + D_ESD_USB_D 2→3 脚并挪到 ≤3.0mm + 位号 _1 后缀 + C_VBUS_GND 下板 + R4/R9 落表 + **E-1 排针 land 重画** ⇒ 板 md5 只变一次」** ★
★⇒ ★**E-1 归 main 拍 (★不是老板★) · 已拍死 · 板上 land 实测 pitch 0.50 vs BOM/网表 1.27 (Δ0.77) ⇒ 实物排针落不进 ⇒ 必须改 land ★**

★**② 作业包 §0.2 的「板侧改动清单 ③」已经写了它 (main 实读 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 第 47 行原文) ★**:
★**「③ `J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★)」** ★
★⇒ ★**作业包知道它 · 但下面那个「全集页」不知道它 ★**

★**③ ★★本单的病根: 「板侧项全集」页漏了这一条 ★★ (main 本机实读 + 实跑) ★**:
- 权威全集页 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★它自己的定位: 「这一页是『板只改一次』那一趟 (S1~S13) 的**板侧项全集** ⇒ **任何一项只在交卷单里、没进这一页 = 当场红**」★)
- ★**该页 JSON 块 32 条 item 的 id 全集 = `B01_REF_SUFFIX` `B02_C_VBUS_GND` `B03_ULDO_S28_PAD3` `B04_R_SUPV_DIV_DNP` `B05_U_EN_SW_VALUE` `B06_TPS7A20_VALUE` `B07_ESD_USB_D_3PIN` `B08_ESD_USB_D_NEAR` `B09_ESD_USB_D_MINUS` `B10_Q_AND_LAND` `B11_Q_PG_LAND` `B12_Q_ENVC_LAND` `B13_ESD_CAM_PAD` `B14_S6_20_COORDS` `B15_SVC_PORT_SPLIT` `B16_LED_G_OPTO` `B17_DNP_43` `B18_J_CHG_DISAMB` `B19_BAT_DET` `B20_LAND_8ROWS` `B21_C_REGN_4U7` `B22_CHG_BOARD_FP` `B23_ESD_TC_4PAD` `B24_Q_PG_PART` `B25_UNCONNECTED` `B26_BASELINE` `B27_CHAINGATE` `B28_RELEASE` `B29_WRITEBACK` `B30_LED_BRIGHTNESS` `B31_P7_TARGET` `B32_V2_NET_RENAME` ★**
- ★**main 实跑判定 (★把 32 条 item 的 JSON 整体序列化后逐个 marker 找★)**: ★`1.27` → **不在** ★ · ★`pitch` → **不在** ★ · ★`排针` → **不在** ★ · ★`E-1` → **不在** ★ · ★`0.50` → **不在** ★ ⇒ ★**这一项在全集页里彻底不存在 (不是措辞不同, 是整条缺失) ★**
- ★**⇒ 覆盖度闸 `HW/check_onepass_preflight_coverage.py` 判不出它 ★**: 该闸 P4 的判据是「26 个**板侧标记**每个都必须在清单里出现」+「每条的 `source_iss` 必须在来源单全集里」★ —— ★**它查的是「有没有这个位号」, 不是「这一趟到底有几项板改」⇒ 一条【不带新位号】的板改 (这里是【同一个 `J_DEBUG`/`J_UART` 的 land pitch 从 0.50 改成 1.27】) ⇒ 天生查不出 ★**
- ★**⇒ 后果 (★main 的读法★)**: ★**P4 绿灯 = 假绿** ★ ⇒ ★**那一趟按全集页做, 排针 land 不会被重画 ⇒ 实物 1.27mm 排针装不进 ⇒ 板白做 (★而且是「板 md5 只变一次」铁律被破的那一种: 补做 = 板 md5 变第二次 = 留证链/Gerber/投产包/盖章全白跑一遍★)★★**

★**④ 同一缺陷在作业包里的第二个影子 (main 实读 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 第 332 行 / 第 348 行) ★**:
- ★**第 332 行 (`C-SEAT-1` = `J_DEBUG`): 「★**④ 待拍板标记**: ★**待 main→老板 (E-1 三选一: ① 改 land 到 1.27 ② 改选型到 2.54 (清空区 X 139.0025..146.8975, 单边间隙 1.1525) ③ 取消座体改治具探针)** ★」 + 「★**⑤ 状态**: ★**待拍 (会改板)** ★」 ★**
- ★**第 348 行 (`C-SEAT-2` = `J_UART`): 同样「待 main→老板 (E-1 三选一, 与 `J_DEBUG` 同拍)」+「待拍 (会改板)」 ★**
- ★★**⇒ 而 pm.yaml 里 E-1 main 已于 2026-11-17 18:45 拍死 (「按 1.27mm 定 + 板 land 并进那一趟重画」) ⇒ 这两处的「待 main→老板」是【过期状态】★★ ⇒ ★**它会把这张作业包指向一个【已经不存在的问题】⇒ 而 E-1 三选一的第 ① 项恰好就是 main 已拍的那一项 ⇒ 等于把已决项重新挂回老板拍板面 ⇒ 白占老板一个回函位 + 那一趟开工前才发现「到底改不改 land」没人拍★★**

★**⑤ 板面读数 (main 实读, ★这两个数是本单判据的地基★) ★**:
- ★**`J_DEBUG` (1×4 排针 · JTAG): 板读 land pattern pitch 0.50 / 4 脚 / 铜箔 X 142.0625..143.8375 × Y 56.1500..57.0500 (1.7750 × 0.9000) ★**
- ★**`J_UART` (1×2 排针 · UART): 板读 pitch 0.50 / 2 脚 / 铜箔 X 18.5025..19.2775 × Y 68.1500..69.0500 (0.7750 × 0.9000) ★**
- ★**BOM/网表写的是 1.27mm 排针 (★`HW/BOM_v1.csv:71` = `J_DEBUG` / `:77` = `J_UART`; 网表 P8 区同串★) ⇒ Δ pitch 0.77 ★**

★**⑥ 结构侧后果已经算过 (main 实读作业包第 326 行 / 第 342 行原文, ★这是 MECH 侧已交付的口径, 本单只引用不重算★) ★**:
- ★**`J_DEBUG` 改 land 到 1.27 ⇒ 必须清空区 X 宽度 1.7750 ⇒ 4.0850, 单边间隙 X 4.2125 ⇒ 3.0575 (★最坏 2.7575, 仍 ≥ `CRIT` 0.60★), 开口 X 与 Y 一字不变, 三档 h 全过, SoM 承载区零影响 ★**
- ★**`J_UART` 改 land 到 1.27 ⇒ 结构侧零连带改动 (★开口 X/Y 全不变, 三档 h 全过★) ★**

★**⑦ 为什么这条【不】依赖老板拍板 (★老板那 9 件还在队列里, 本单不许拿它当阻塞项★) ★**:
★**E-1 = 排针 pitch 1.27 vs 板读 0.50 ⇒ 实物落不进 ⇒ 这是【已由 main 拍死的规格事实】(2026-11-17 18:45) ⇒ 不是「要不要改产品」的问题, 是「板 land 要不要跟 BOM 对齐」的问题 ⇒ main 已拍「要」 ⇒ ★**本单现在就能做 (只做【清单补齐 + 状态订正 + 机器闸】, 不动板) ★**

---

## §1 本单要交付什么 (★三件, 不许跑题★)

★**① `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 追加一条 item (★E-1 排针 land 重画★)** ★
- ★**id = `B33_PIN_LAND_1P27` (★若与既有 id 风格不合, 你可改名, 但★**不许与既有 32 条重名**★) ★
- ★**`source_iss` = `ISS-290` (★E-1 的来源单 = ISS-290「E-1 / E-2 两条板侧取舍」⇒ ★**你必须同时把 `ISS-290` 加进 `HW/check_onepass_preflight_coverage.py` 的 `SOURCES` 集合**, 否则 P4 判你「来源不明」⇒ ★**这是本单唯一允许你改那个闸脚本的地方, 改的是 `SOURCES` (加一个成员), 不是判据方向★)★★
- ★**`title` = 「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」 ★**
- ★**`step` = `S6` (★排针 land 属封装 land 改 ⇒ 与 `B05_U_EN_SW_VALUE`/`B06_TPS7A20_VALUE`(S3 板封装属性)、`B10_Q_AND_LAND`/`B11_Q_PG_LAND`/`B13_ESD_CAM_PAD`(S6 land 序) 同族 ⇒ 归 S6★) ★**
- ★**`current_state` = ★**必须是 [实测] 且与盘面逐字一致**★: `J_DEBUG` 板读 pitch 0.50 / 4 脚 / 铜箔 X 142.0625..143.8375 × Y 56.1500..57.0500; `J_UART` 板读 pitch 0.50 / 2 脚 / 铜箔 X 18.5025..19.2775 × Y 68.1500..69.0500; BOM/网表写 1.27mm ⇒ Δ pitch 0.77 ⇒ 实物落不进 (★main 已实读, 你要用自己的命令复现一遍, 把命令与原样输出贴进 §B6★) ★
- ★**`action` = 「★**那一趟把 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch 从 0.50 改成 1.27 (★E-1·main 2026-11-17 18:45 已拍死·**归 main 不归老板**★) ⇒ 与 S4 的 ESD 挪位、S6 的 `Q_PG`/`Q_AND` land 重画**同一次布局里做完** ⇒ ★**板 md5 只许变一次**★」 ★**
- ★**`criterion` = ★**必须是一条真命令 (P3 会验脚本文件在盘) 且期望值可自证**★ ⇒ 建议落一条**只读**探针 (★不许写盘★) + 期望读数「`J_DEBUG` land pitch = 1.27 / `J_UART` land pitch = 1.27」 ★**
- ★**`blocked_by` = `-` (★E-1 已由 main 拍死 ⇒ **不是**「老板 (W-2)」★) ★**
- ★**`evidence` = `[实测]` ★**

★**② 作业包两处「过期待拍板」状态订正 (★追加式, 老字一字不删★) ★**
- ★**`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 第 332 行 (`C-SEAT-1`) 与第 348 行 (`C-SEAT-2`): 现在的「④ 待拍板标记: 待 main→老板 (E-1 三选一…)」+「⑤ 状态: 待拍 (会改板)」 ★**⇒ ★**追加一段订正 (★不删老行★): 「★**E-1 已由 main 2026-11-17 18:45 拍死 (★`pm.yaml` key `main_e1_e2_board_side_rulings_20261117`★) = 按 1.27mm 排针定 + 板 land 并进那一趟重画 ⇒ ★**「待拍」状态作废, 不再占老板拍板面**★」 ★**
- ★**⇒ 本单必须让那两处的状态与 pm.yaml 一致 (★「已拍·进那一趟」★), 而不是「待拍」 ★**

★**③ 把覆盖度闸的盲区补上 (★不许放宽判据方向★) ★**
- ★**问题 (main 实读 `HW/check_onepass_preflight_coverage.py` 的 `MARKERS` / `SOURCES` / `check_P4`) ★**: P4 查的是「位号在不在清单里」+「来源单在不在全集里」★ ⇒ ★**一条【不带新位号】的板改 (同一 `J_DEBUG`/`J_UART` 的 land pitch 改) 天生查不出 ⇒ 本单就是 P4 的一个【假绿样本】★**
- ★**你必须做: 给 P4 加一条判据 = 「★**作业包 §0.2 ③ 的板侧改动清单, 每一条都必须在清单页有对应 item**★」 ★**
  - ★**这条判据要能机器读出作业包 §0.2 那一行的 7 项 (★① `Q_PG` 三根线重画 ② `D_ESD_USB_D` 2→3 脚+挪到 ≤3.0mm ③ 排针 land 0.50→1.27 ④ 位号 `_1` 后缀 ⑤ `C_VBUS_GND` 下板 ⑥ R4/R9 落表 ⑦ `corner_radius` 死参数清掉★) ★**
  - ★**⇒ 你必须先自己实读作业包那一行的原文, 再写解析 (★不许把 7 项写死成一个常量数组糊弄过去 ⇒ 那样下次作业包改了闸不会红★) ★**
  - ★**★**判定口径 (main 已想清, 你照做) ★**★**: ① `Q_PG` 三根线重画 ⇒ 命中 `B11_Q_PG_LAND` ✓ · ② `D_ESD_USB_D` ⇒ 命中 `B07_ESD_USB_D_3PIN`(+`B08`/`B09`) ✓ · ③ 排针 land ⇒ ★**命中你新加的 `B33_PIN_LAND_1P27`** ✓ · ④ 位号 `_1` 后缀 ⇒ 命中 `B01_REF_SUFFIX` ✓ · ⑤ `C_VBUS_GND` 下板 ⇒ 命中 `B02_C_VBUS_GND` ✓ · ⑥ R4/R9 落表 ⇒ ★**命中 `B09_ESD_USB_D_MINUS` 那一族 (★R4/R9 是 `HW/check_netlist_selfconsistency.py` 里的**规则号**, 不是位号 ★ ⇒ 你要实读那个脚本确认 R4/R9 对应哪一条板改, 再决定命中哪条 item★) ⇒ **不许凭空猜** ★ · ⑦ `corner_radius` 死参数清掉 ⇒ ★**这是 E-2 = 【零板改】⇒ 它【本就不该】在「板侧项全集」里 (★它不碰板 md5★) ⇒ 你的新判据必须能区分「板改项」与「零板改项」⇒ ★**建议: 新判据只覆盖「会改板 md5 的项」, ⑦ 单独排除并写明理由 (★E-2 零板改 ⇒ 不进板侧项全集, 出处 `pm.yaml` 同一 key 的 decision)★ ★
  - ★**★**方向纪律 (★本项目铁律★)★★: ★**只许【加严】不许【放宽】** ★ ⇒ ★**P1/P2/P3/P4/P5/P6 六条现有判据一条都不许改弱** ★ ⇒ ★**P4 的 26 个 MARKERS 一个都不许删** ★ ⇒ ★**SOURCES 只许【加成员】不许【减成员】** ★
  - ★**★**反向用例 (★本项目的硬规矩: 闸必须有反向用例, 否则是装饰★)★★: ★**你必须证明「新判据真的能抓住本单这类漏项」** ⇒ ★**沙盒副本上把新加的那条 item 从清单页 JSON 块里删掉 ⇒ 新判据必须判红并点名「③ 排针 land 缺对应 item」★ ⇒ ★**再把 `ISS-290` 从 `SOURCES` 里去掉 ⇒ P4 旧判据也必须判红 (证明 SOURCES 那一路也没白加)★ ⇒ ★**两条例外都验证完, 恢复原件 ⇒ 判绿** ★
  - ★**★**沙盒纪律 (★本项目铁律★)★★: ★**反向用例必须在 `tmp/` 副本上做 (★用 `WP_CHECKLIST` env 指向副本 —— `HW/check_onepass_preflight_coverage.py` 与 `HW/check_workpack_state_values.py` 都支持这个 env 覆盖, main 已实跑验证过覆盖有效★) ⇒ ★**真件 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 与真件闸脚本一个字节都不许在反向用例里被动** ★

---

## §2 边界 (★违反任一条 = 本单不成立★)

★**① 零写板**: `HW/PCB/demo_mainboard.kicad_pcb` md5 必须仍 = `611b869e13518c3c023fb178f91a0075`, mtime 仍 = `2026-11-06 07:07:17.362193413` ★ ⇒ ★**本单【不许】碰板** ★
★**② 零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三件 md5 逐字节不变; ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节不许碰** ★
★**③ 零改 `MECH/` 任何文件** (★结构侧开口/清空区口径是 MECH 域, 本单只引用不重算不修改★); ★**零改 `state/fragments/pm.yaml`** (★那是 main 的分片★); ★**零改 `state/fragments/mech.yaml` / `state/fragments/sw.yaml`** (★别人的分片★) ★
★**④ 只改 3 个文件**: ★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★追加式·老字一字不删★) + ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★追加式·老字一字不删★) + ★`HW/check_onepass_preflight_coverage.py` (★只许加严 + `SOURCES` 加 `ISS-290`★) ⇒ ★**新建交付物另算 (交卷页 + logs 目录) ★**
★**⑤ 不许改判据方向**: 上面 §1③ 的方向纪律 (★只许加严不许放宽★) ★
★**⑥ 不许代拍**: ★**E-1 已经 main 拍死了 (2026-11-17 18:45) ⇒ 你只是【把状态对齐 + 把项补进全集】, 不是重新拍一遍★** ⇒ ★**不许再提出 E-1 的「三选一」⇒ 不许改 ①②③ 三个选项的措辞 ★**
★**⑦ 不许外发**: ★**零邮件 / 零询价 / 零问询 / 零采购 ★** ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★** ⇒ ★**没有「批一句可以发」这个选项 ★**
★**⑧ 不许替老板拍板**: ★**本单【不新增】任何老板拍板项 ★** ⇒ ★**尤其: 不许把 E-1 重新挂回老板拍板面 (★那正是本单要修的过期状态★) ★**
★**⑨ 引用零假引用**: 交卷页里引用的每个 `HW/*` / `MECH/*` / `state/*` / `logs/*` 文件必须逐个在盘 ⇒ ★**交卷前自检一次, 输出贴进 §B6 ★**
★**⑩ 板那一趟的其余项一件都不许动** (★`B01`~`B32` 全部保持原样, 不许顺手改任何现状值★) ★

---

## §3 交卷物 (★N 件, 缺一件即不算交卷★)

★**① 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS343_板侧项全集漏项补齐.md` (★**新建**★) ⇒ ★**B1 结论摘要 / B2 验收标准逐条自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 ★**六块齐全 (★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 就是这 6 块 + 证据分级标签 `[实测]/[官方]/[推算]/[0数据]`★) ⇒ ★**先落骨架再填内容 (★先 write 六个标题, 再逐块填·★不许一次性 write 大段★) ★**
★**② 清单页 + 作业包的追加式订正 (★落在真件, 老字一字不删★) ⇒ 交卷页里给出 ★**老前缀 md5 前后对比 + `diff` 输出★ (★证明只增不删★) ★
★**③ 闸脚本的加严 + 两条反向用例读数 (★落在 `logs/iss343/`) ★**
★**④ `state/fragments/hw.yaml` 登记 (★**只走 `python3 state/frag_write.py --agent hw-lead`★·零重复 key★) ⇒ ★**`grep -c iss343 state/fragments/hw.yaml` ≥ 3 ★**
★**⑤ `logs/iss343/` 原始输出 (★机器生成的命令输出, 一条命令能复现★) ★**

★**★必跑命令 (★全部是本机实存路径, `state/check_brief_commands.py --brief-file` 已验 rc=0★)★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 HW/check_onepass_preflight_coverage.py ; echo "COV_RC=$?"
TMPDIR=$PWD/tmp python3 HW/check_onepass_preflight_coverage.py --selftest ; echo "COV_SELFTEST_RC=$?"
TMPDIR=$PWD/tmp python3 HW/check_workpack_state_values.py ; echo "WPVAL_RC=$?"
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
```

★**★交卷前必须跑 (§2 边界自证 + 主线闸) ★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"     # ★rc 必须 0★
TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"   # ★rc 必须 0 且 Q1 = 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 state/frag_write.py --agent hw-lead --show | head -5
```
★**★回复 ≤ 500 字 + 4 行读数 (`COV_RC` / `COV_SELFTEST_RC` / `GATE_RC` / `BOARD_MD5`) + 反向用例是否判红★★**

---

## §4 交卷时必须回答 main 的 3 个问题

★**① 「§0③ 的『不在』你用自己的命令复现了吗? 原文 + 原样输出是什么?」 ★**
★**② 「§1③ 的 R4/R9 到底对应哪条板改? 你实读了 `HW/check_netlist_selfconsistency.py` 的哪几行?」 ★**
★**③ 「你加的新判据, 反向用例删掉新 item 后判红了吗? 点名了哪一条?」 ★**

★**★额外纪律 (★派活方统一加, 一条都不许少★)★★**:
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ★**
★**② 只写本任务允许的文件, 不碰别人的 (★特别是 `state/fragments/pm.yaml` = main 的分片★) ★**
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 (★本单主要是 `[实测]` + `[推算]`★) ★**
★**④ 不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项 ★**
★**⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复 ★**
