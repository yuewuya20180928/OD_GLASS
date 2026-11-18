# SW/BOARD_ONEPASS_SW_SYNC.md · 「板只改一次」那一趟的【SW 侧板侧输入收口】

> ★**派活**: `state/dispatch_briefs/ISS-279_sw_board_side_input_sync.md` (项目总工 2026-11-17 07:5x / 08:1x 续做) ★
> ★**本单性质**: ★**内部活 · SW 侧 · 纯分析 + 作业包订正 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零改既有判据阈值** ★
> ★**机器闸**: `python3 SW/tools/check_onepass_sw_sync.py` (★W1~W6 + `--selftest` ★) ★
> ★**配套**: 板侧孪生页 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★ISS-277 · hw-lead ★) · 板侧作业包 = `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★S1~S13 ★) · SW 侧 md5 台账 = `SW/SW_MD5_BASELINE_LEDGER.md` ★
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** ★ (★hw-lead 在飞 ISS-277 · mech-lead 在飞 ISS-278 ⇒ 三边各写各的, 只交叉引用★) ★

★**一句话口径**: ★**这一页是「板只改一次」那一趟 (S1~S13) 对 SW 侧的全部影响清单** ⇒ ★**那一趟的板面动作一旦落地, SW 侧的判据/文档/台账会跟着漂哪几处, 这一页提前写清** ★
★**为什么必须有这一页**: ★**板侧项全集已经在 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 里了 (31 条), 但那份是【板侧视角】; SW 侧那条腿 (`sw-lead` / `跨域` / `全域` 在 ISS-277 任务书里命中 0 次) 至今没人认领** ⇒ ★**板侧清单再全, 也答不了「SW 侧的判据/文档/台账会漂哪几处」** ★

---

## §1 · 一句话口径 + 坐标帧声明 (★三条帧互不混用 ★)

★**口径**: ★**「板只改一次」那一趟 = 已经定了要改板 (位号改名 + B-1~B8 板侧同步 + 布局修正 + 布线 45→0)** ⇒ ★**本页不是论证要不要改板, 是让 SW 侧在【已经决定要改】的前提下【提前看得见后果】** ★
★**⇒ 净效果 = 提前可见 + 可判, 不是提前动手** ★ (★本单一个字节没写板 / 没落表 / 没改任何既有判据★)

| 帧 id | 含义 | 本页用在哪 |
|---|---|---|
| ★**`B160x100`** ★ | ★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★ | ★**本页所有涉及板面坐标/位号的项一律用它** ★ |
| `F30A` | 60×30 套A 帧 | ★**只作对照, 不可代入** ★ |
| `P60x15` | 60×15 帧 | ★**只作对照, 不可代入** ★ |

★**权威帧表** = `HW/PCB/BOARD_FRAME_CALIBER.md` §6 (★ISS-274 · hw-lead★) · ★**机器闸** = `python3 HW/check_board_frame_caliber.py` ★
★**⇒ 本页与 `F30A` / `P60x15` 不可混用** ★ (★实测教训: ISS-271 的 `D_LED_G_1` 窗口与检修口开口是 60×30 帧, 照字面抄进 160×100 帧 = 开工即撞 SoM 座★)

★**★本单的坐标系 = SW 侧只读板面, 只取三个量: ★① 位号 ★② 网名 ★③ md5 / 焊盘数 / 距离 (★不产出任何新坐标★)★** ★

---

## §2 · 逐条表 (★每条固定 9 个字段 · ★★8 条一条不许漏★★)

★**字段**: `id` / `source_iss` (★来源单号, 多来源用 `+` 连接★) / `title` / `current_state` (★现状实测值, 必带 `[实测]`/`[推算]`/`[0数据]`★) / `action` (★那一趟要做什么★) / `criterion` (★判据命令 + 期望 rc/期望值, 必须是真命令★) / `step` (★归属步, 必须 ∈ S1~S13★) / `blocked_by` (★阻塞前置 / 谁拍★) / `evidence` (★证据等级★)

| id | source_iss | title | step | blocked_by | current_state (★实测值 ★) | criterion (★真命令 ★) |
|---|---|---|---|---|---|---|
| ★**`SW01_PCB_MD5`** ★ | ★ISS-266+ISS-275 ★ | ★**板 md5 硬保护值 (台账 §1 `hard_protected[0]`) ⇒ 那一趟改板当天 SW R6 必红** ★ | ★**S9** ★ | ★**main→老板** (★机制取舍: `hard_protected` 怎么合法跟上 = §4 三方案★) ★ | ★**[实测]** 盘上板 md5 = `611b869e13518c3c023fb178f91a0075` · 台账 §1 `hard_protected[0].md5` 钉的是同一个值 · R6 对该件走【纯 md5 比对独立分支】(`SW/tools/check_demo_panel_spec.py` L459~L472) ⇒ 盘上 ≠ 锚点即红, **无链头机制可依赖** ⇒ 那一趟改板当天必红 (★ISS-275 只把「台账管的那两个文件」换成链头判决源, 硬保护两件不在链头机制里★) ★ | ★`python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (★R6 硬保护段: 盘上板 md5 == 台账 `hard_protected[0].md5`★) ★ |
| ★**`SW02_KICAD_PRO_MD5`** ★ | ★ISS-266+ISS-275 ★ | ★**`.kicad_pro` md5 硬保护值 (台账 §1 `hard_protected[1]`) ⇒ S3/S4 动了封装属性就会跟着红** ★ | ★**S9** ★ | ★**main→老板** (★同 SW01★) ★ | ★**[实测]** 盘上 `.kicad_pro` md5 = `3e504d2be83152e337949723e909be1b` · 台账 §1 `hard_protected[1].md5` 钉的是同一个值 · R6 同走【纯 md5 比对独立分支】 ⇒ 作业包 §4「全程」行明写「除板 + `.kicad_pro` (若 S3/S4 动了封装属性) 外逐字节不变」 ⇒ **那一趟它极可能变** ★ | ★`python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (★R6 硬保护段: 盘上 `.kicad_pro` md5 == 台账 `hard_protected[1].md5`★) ★ |
| ★**`SW03_LAND8_DNP`** ★ | ★ISS-244+ISS-266 ★ | ★**8 个落表残项位号的 value/dnp 一变, SW 侧 `timing_check.py` F1 断言的期望值就得跟着定** ★ | ★**S10** ★ | ★**落表批次** (★8 行的选型/footprint 归 ISS-241 / ISS-244★) ★ | ★**[实测]** 落表残项 **8 行** (`D_CHG_LED_1` / `D_LED_G_1` / `D_LED_R_1` / `SW_BOOT_1` / `SW_KEY_PWR_1` / `SW_KEY_VM_1` / `SW_KEY_VP_1` / `SW_RST_1`) 在脚表里**都有 2 行** ⇒ **不是缺脚, 是 value 仍写「待选型」+ land 要同批重画** · SW 侧 `SW/tools/timing_check.py:922` 的 `sw_rst_row_dnp` (读 `SW_RST_1` 的 DNP 状态) + `:1491` 的断言「RESET_N 上谁在拉 = Q_AND_1 必装 / SW_RST_1 必装 / U_SUPV_1 pin1 DNP」⇒ **这 8 行落表后 DNP 状态变 ⇒ 这条断言的期望值要跟着定** ★ | ★`python3 SW/tools/timing_check.py` ⇒ **rc=0** (★71/71★) ⇒ 落表后 F1 的期望值必须与落表后脚表一致 ★ |
| ★**`SW04_CHG_LED_REF`** ★ | ★ISS-234+ISS-244 ★ | ★**充电灯位号口径有两套 (网表 `D_CHG_LED_1` vs SW 关机语义页 `Q_CHG_LED_1`) ⇒ 那一趟落表前必须对齐** ★ | ★**S10** ★ | ★**落表批次** (★SW 侧镜像页改动随落表同批; 零落表可先改 SW 侧口径★) ★ | ★**[实测]** 网表/脚表里充电灯**本体**位号 = `D_CHG_LED_1`, 其 `board` 列 = `CHG_BOARD` ⇒ **不在 demo 主 PCB 装机范围** (★板上没有 `D_CHG_LED_1` 这个封装; 板上有 `D_LED_G_1` / `D_LED_R_1` / `D_LED_B_1` 三颗★) · 而 `SW/SHUTDOWN_SEMANTICS_SPEC.md` 写的充电灯位号是 `Q_CHG_LED_1` (★该页实测: `D_CHG_LED_1 0 次 · Q_CHG_LED_1 6 次`★) ⇒ ★**两个位号口径必须在本单对齐** ★ | ★`python3 SW/tools/check_shutdown_semantics.py` ⇒ **rc=0** (★R1~R7 全过 · 口径页 / HW 文档 / SW 镜像 / 网表四方一致★) ★ |
| ★**`SW05_KEY_NETNAMES`** ★ | ★ISS-244+ISS-266 ★ | ★**5 颗按键的板侧网络名 ≠ 位号 ⇒ SW 侧代码/断言一律按网名** ★ | ★**S10** ★ | ★**落表批次** (★5 键属那 8 行里★) ★ | ★**[实测]** 脚表实测映射: `SW_BOOT_1`→`BOOT_N` · `SW_KEY_PWR_1`→`KEY_PWR` · `SW_KEY_VM_1`→`KEY_VOL_M` · `SW_KEY_VP_1`→`KEY_VOL_P` · `SW_RST_1`→`RESET_N` (★每颗 **2 pad** = 信号 + GND★) · SW 侧 `SW/tools/timing_check.py:1264` 的 `nl.rail_of("R_PU_BOOT_N_1")` (★F5 上拉轨域★) + `:1491` 的 RESET_N 拉低链实读 ⇒ **那 8 行落表后, 这两条断言的期望值会变** ★ | ★`python3 SW/tools/timing_check.py` ⇒ **rc=0** (★71/71★) ⇒ F1/F5 期望值必须与落表后脚表一致 ★ |
| ★**`SW06_TP_INT`** ★ | ★ISS-266+ISS-279 ★ | ★**`TP_INT` (触控中断) 在网表和板上都不存在 ⇒ SW 侧不许按「有触控中断」写代码** ★ | ★**S8** ★ | ★**老板/PM** (★demo 板要不要接触控中断★) + ★**hw-lead** (★板侧落点★) ★ | ★**[实测]** `TP_INT` 命中数: 网表 **0** · 脚表 **0** · 板 **0** ⇒ **这条线根本没画** (★板上同族测试点是 `TP_USB_D_N_1` / `TP_KEY_PWR_1` / `TP_RESET_1` 等, 没有 `TP_INT`★) · ISS-174 已 verified 说「pin26 没接到 SoM 任何脚」, 但那是在【整机屏】口径下 ⇒ **demo 板这一趟要不要接, 是【板侧输入】问题** ★ | ★`grep -c TP_INT HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb` ⇒ **命中数 = 0** (★板侧现状★) ; SW 侧: ★`python3 SW/tools/check_onepass_sw_sync.py` ⇒ **rc=0** (★W5 现状探针·三件都 0★) ★ |
| ★**`SW07_C_VBUS_GND`** ★ | ★ISS-266+ISS-279 ★ | ★**`C_VBUS_GND_1` 两个多余焊盘 (充电板件留在 demo 主 PCB) ⇒ 那 2 个焊盘一拿掉, SW 侧 USB 前提判据跟着变** ★ | ★**S2** ★ | ★**-** (★没人卡; 板侧 S6 重出即自动消失★) ★ | ★**[实测]** 板上 `C_VBUS_GND_1` **仍在**, 两个带网焊盘挂的是 **pad1 = GND / pad2 = VBUS_5V_CHG** ⇒ 板↔网表 `check_pcb_nets.py` 报 C1「**多余 2**」 · 网表里 `C_VBUS_GND_1` 两行的 `board` 列**已经是** `CHG_BOARD` ⇒ **它物理在充电板, 不在 demo 主 PCB** ⇒ ★**那 2 个焊盘一拿掉, SW 侧的 USB 枚举 / S2 救砖链路前提判据跟着变** ★ | ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ **C1 缺失 0 · 多余 0 · 同号异网 0** (★现状: **多余 2**★) ⇒ 那一趟之后 SW 侧 USB 前提判据按「多余 0」写 ★ |
| ★**`SW08_ESD_USB_D`** ★ | ★ISS-266+ISS-279 ★ | ★**`D_ESD_USB_D_1` 只有 2 焊盘 + 距 `J_USB_C_1` 47.99 mm ⇒ SW 侧 USB 前提判据跟着变** ★ | ★**S4** ★ | ★**W-1/W-2** (★老板: 一颗双通道 vs 两颗单通道★) ⇒ **S4 是第一个真正卡在老板的步** ★ | ★**[实测]** 板面 `D_ESD_USB_D_1` → `J_USB_C_1` 板面距离 = **47.99 mm** (★规格页 §①(4) 引的就是这个数; 要求 ≤ 3.0 mm★) · `D_ESD_USB_D_1` 在脚表里**只有 2 行** (pad1 = `USB_D_P_SRC` / pad2 = `GND`) ⇒ **USB D− 那条路上 ESD 位号数 = 0** · 网表里 `D_ESD_USB_D_1` 的 dnp = 必装 ★ | ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ **R4** (★D− 侧 ESD ≥1 且 `D_ESD_USB_D_1` 焊盘数 = 3★) / **R9** (★`D_ESD_USB_D_1` ↔ `J_USB_C_1` 中心距 ≤ 3.0 mm★) 转绿 ⇒ SW 侧 USB 前提判据按「R4/R9 绿」写 ★ |

### §2.1 · 归属步分布 (★每条都有归属, 不许有步没人管★)

| 步 | 条数 | 条目 |
|---|---|---|
| ★**S2** ★ | 1 | ★`SW07_C_VBUS_GND` ★ |
| ★**S4** ★ | 1 | ★`SW08_ESD_USB_D` ★ |
| ★**S8** ★ | 1 | ★`SW06_TP_INT` ★ |
| ★**S9** ★ | 2 | ★`SW01_PCB_MD5` · `SW02_KICAD_PRO_MD5` ★ |
| ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` ★ |

★**★SW 侧只在这 5 步上有话说 (★其余 8 步 SW 侧零影响 —— 不是漏了, 是实测出来的「SW 侧判据/文档/台账不动」★)★** ★
★**★本单不要求 S1~S13 每步都被 SW 侧覆盖 (★那是板侧 `HW/check_onepass_preflight_coverage.py` P2 的口径, 板侧页已覆盖 13/13★) ⇒ 本页 W2 只管「每条 `step` 必须是 S1~S13 里的一个」** ★

### §2.2 · 三条不许搞混的 (★与任务书 §⑥ 同口径★)

1. ★**「板那一趟会改板」是【已定的事】** ⇒ ★**本页不许出现「建议暂缓改板」这类不属于 SW 地界的话** ★
2. ★**「R6 红了」有两种**: ★**① 锚点过期 (合法落表后没跟) ⇒ 假红 ⇒ 已由 ISS-275 切断** ★ · ★**② 盘被换了 (含**合法改板**) ⇒ 真红** ★ ⇒ ★**本页只处理 ②, 而且必须把「合法改板」与「偷换真源」分开** ★
3. ★**SW 侧不是「板侧的附属」** ⇒ ★**SW 侧对板的要求 (8 残项的 DNP 期望值 / 触控中断要不要接 / 充电灯位号口径) 是【SW→板 的输入】, 写进 §3 交 main 转 hw-lead** ★ ⇒ ★**不是让 SW 去改板** ★

---

## §3 · SW→板 输入清单 (★交 main 转 hw-lead · ★★一个字不许改 HW/★★)

★**职**: ★**SW 侧希望板侧怎么做的, 逐条写清 (含「SW 侧判据期望值随板侧怎么变」)** ★ ⇒ ★**这一节是【给板侧的输入】, 不是【给 SW 的任务】★ ★

| # | SW→板 的请求 | SW 侧判据期望值随板侧怎么变 | 卡在谁 |
|---|---|---|---|
| ★**1** ★ | ★**板改完那一刻, 板侧必须一次性给 SW 侧三样东西: ① 新板 md5 ② 新 `.kicad_pro` md5 ③ 那次落表的单号/台账位置** ★ ⇒ ★**缺一样 SW 侧就没法合法重锚 (R6 必红)** ★ | ★**R6 硬保护段**: 从「盘上 ≠ 台账 `hard_protected` ⇒ 红」变成「盘上 == 台账重锚后的值 ⇒ 绿」★ ⇒ ★**重锚的合法性由 ③ 单号背书, 不是由「值改了」背书** ★ | ★**main→老板** (★走 §4 三方案之一★) |
| ★**2** ★ | ★**8 个落表残项位号 (`D_CHG_LED_1`/`D_LED_G_1`/`D_LED_R_1`/`SW_BOOT_1`/`SW_KEY_PWR_1`/`SW_KEY_VM_1`/`SW_KEY_VP_1`/`SW_RST_1`) 的 value + dnp 状态一次定死, 落表单号必须同时给 SW 侧** ★ | ★**`timing_check.py` F1** 的 `sw_rst_row_dnp` / `q_and_drain_row_dnp` / `u_supv_pin1_row_dnp` 期望值 (★现在写死 `必装`/`必装`/`DNP`★) ⇒ ★**按落表后真值改期望值, 不许改判据逻辑** ★ | ★**落表批次** |
| ★**3** ★ | ★**5 颗按键的网名 (`BOOT_N`/`KEY_PWR`/`KEY_VOL_M`/`KEY_VOL_P`/`RESET_N`) 不许改成位号** ★ ⇒ ★**网名是 SW 侧代码与断言的唯一锚** ★ | ★**`timing_check.py` F5** 的 `nl.rail_of("R_PU_BOOT_N_1")` / `R_PU_RESET_N_1` 轨域判定 ⇒ ★**网名一改 ⇒ SW 侧两条断言直接失效** ★ | ★**落表批次** |
| ★**4** ★ | ★**充电灯位号口径: `D_CHG_LED_1` = 充电灯**本体** (board=CHG_BOARD, 不装 demo 板) · `Q_CHG_LED_1` = 充电灯**驱动 MOS** (board=CHG_BOARD) ⇒ SW 侧关机语义页与网表对齐** ★ | ★**`check_shutdown_semantics.py`** 的 R1~R7 四方一致 (口径页 / HW 文档 / SW 镜像 / 网表) ⇒ ★**口径不统一 ⇒ R3/R4 必红** ★ | ★**落表批次** (★SW 侧镜像页可先改, 零落表★) |
| ★**5** ★ | ★**`TP_INT` 那一趟要不要接, 请给明确答案**: 接 ⇒ 必须同批落表 + 落位 + 布线 (⇒ 进 S8 布线归零那一批) · 不接 ⇒ SW 侧按「无触控中断」写 ★ | ★**SW 侧代码不得引用任何 `TP_INT` 网名**; 若接 ⇒ SW 侧新增一条「触控中断到达 ⇒ 唤醒」路径的判据 (★现在没有这条判据★) ★ | ★**老板/PM + hw-lead** |
| ★**6** ★ | ★**`C_VBUS_GND_1` 两个多余焊盘在 S6 重出后自动消失 (板生成器按 `board` 列过滤)** ⇒ 请不要手改板 ★ | ★**SW 侧 USB 枚举 / S2 救砖链路前提判据**: 从「VBUS 前级对地电容在 demo 板上」改成「不在 (在充电板)」⇒ ★**期望值按「多余 0」写** ★ | ★**没人** |
| ★**7** ★ | ★**`D_ESD_USB_D_1` 必须同批换 3 脚封装 + 挪到 `J_USB_C_1` 旁 ≤ 3.0 mm + D− 补 ESD (B-3/B-4/B-5 是一个原子操作)** ★ | ★**SW 侧 USB 前提判据**: 按「R4/R9 绿」写 (★ESD 紧贴入口 = USB 枚举可靠性前提★) ⇒ ★**现在 SW 侧没有这条前提判据, 那一趟后要补** ★ | ★**W-1/W-2 (老板)** |
| ★**8** ★ | ★**板侧自己的闸 (`state/check_pcb_drc.py` / `state/check_pcb_nets.py` / `state/chain_gate.py`) 必须先绿, SW 侧才认这次改板** ★ | ★**SW 侧 R6 的合法重锚判据**: 「板侧闸绿 + 落表单号齐全」= 可重锚的充分条件 ⇒ ★**没这两样 ⇒ SW 侧一律红 (这正是要挡的「偷换真源」)** ★ | ★**没人** |
| ★**9** ★ | ★**板侧不许顺手改 SW 侧语义 (位号 / 网名 / dnp / 关机灯口径) ⇒ 那些一律走落表台账** ★ | ★**SW 侧任何断言的期望值变更都必须挂在【落表单号】上** ⇒ ★**板侧私改 ⇒ SW 侧红, 这是对的** ★ | ★**落表批次** |

★**一句话给板侧**: ★**SW 侧对那一趟只有一个要求 —— 「改了什么, 挂在哪个单号下, 新旧 md5 是多少」三样说清楚** ★ ⇒ ★**说得清, SW 侧就有合法路径跟上; 说不清, SW 侧就只能二选一: 恒红 或 挖坑** ★

---

## §4 · 「板改过一次, SW 侧怎么合法跟上」设计页 (★★★本单最核心的一节★★★)

### §4.1 · 病灶 (★本机实读 · 2026-11-17 08:0x★)

| 项 | 盘上实测 | 出处 |
|---|---|---|
| SW 台账 `hard_protected` 钉死的板 md5 | `611b869e13518c3c023fb178f91a0075` | `SW/SW_MD5_BASELINE_LEDGER.md` §1 `hard_protected[0]` |
| SW 台账 `hard_protected` 钉死的 `.kicad_pro` md5 | `3e504d2be83152e337949723e909be1b` | 同上 `hard_protected[1]` |
| R6 对这两个件的判法 | ★**纯 md5 比对** ⇒ `got != want` 即红 | `SW/tools/check_demo_panel_spec.py` L459~L472 (★**硬保护段走的是独立分支, 不经过台账链头**★) |
| `source_ledger.entries[]` 只管 | `HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` **两个文件** | 同上 §1 `source_ledger` |

★**⇒ 三条推论 (★本机实跑验证, 见交卷单 B3★)**:
1. ★**板 md5 变 ⇒ SW R6 必红** (★纯 md5 比对, 无链头机制可依赖★) ★
2. ★**而「板那一趟」合法地就要改板** ⇒ ★**改完板 = SW 侧恒红** ★
3. ★**而现在没有任何一条台账链覆盖「板改过」这件事** ⇒ ★**⇒ SW 侧此刻无路可走: 要么门禁恒红 (假红), 要么有人手改 `hard_protected` 里的 md5 —— 而手改 md5 正是 ISS-273 / ISS-275 两单花大力气堵掉的那个「悄悄换真源」漏洞** ★

### §4.2 · 三条方案 (★只列 + 代价 + 判据口径 · ★★不代拍★★)

| 方案 | 做法 | 「悄悄换真源」还能不能抓住 | 盘面变了会不会假绿 | 代价 | 谁拍 |
|---|---|---|---|---|---|
| ★**①** ★ | ★**给板也建链头**: 把板 / `.kicad_pro` 登记进 `source_ledger`, 改板也要在落表台账留记录 (★四项同行口径: 单号 | 文件名 | 改前 md5 | 改后 md5★) ★ | ★**能** (★盘上 ≠ 链头 ⇒ 红, 与网表同构★) ★ | ★**不会假绿** (★链头取不准一律判红, 与 ISS-275 同款 fail-closed★) ★ | ★**板那一趟要多写一条落表记录** + ★**R6 硬保护段要改成链头判据 (判据逻辑变更, 不是阈值变更)★** ★ | ★**main→老板** ★ |
| ★**②** ★ | ★**保留纯 md5, 但把「合法改板」做成一个显式的、由单号背书的动作**: 改板那一趟的单号 + 新旧 md5 都留痕, 闸认这个单号 ★ | ★**能, 但要求「改 md5 必须同时改单号字段」⇒ 半自动** ★ | ★**可能假绿** (★若单号字段与 md5 字段可各自独立编辑, 就出现「改了 md5 没改单号」的缝 ⇒ 必须做成【一个字段, 两个值】, 且单号必须在落表台账里查得到★) ★ | ★**多一个字段要维护** + ★**台账与锚点两处都要写 (同 ISS-275 的老问题)★** ★ | ★**main→老板** ★ |
| ★**③** ★ | ★**拆成两层**: 板 md5 只判「有没有变」不判「对不对」, 真正的判据交给板侧自己的闸 (`state/check_pcb_drc.py` + `state/check_pcb_nets.py` + `state/chain_gate.py`) ★ | ★**SW 侧不再抓偷换 ⇒ 抓偷换的责任转移给板侧闸** ★ | ★**★跨域判据漂移风险★★** (★SW 侧只知道「变了」不知道「变了是不是合法」⇒ 板侧闸若被人放宽, SW 侧无从察觉★) ★ | ★**必须写清谁负责什么** (★SW 侧 = 变更检测 · 板侧 = 变更正确性★) + ★**跨域闸互相引用的维护成本** ★ | ★**main→老板** ★ |

### §4.3 · 三条方案都要守的红线 (★逐条写死 · ★★改方案也不许动★★)

1. ★**不许把「改 md5」变成「随手改一下就绿」** ⇒ ★**任何方案都要留下「谁在哪个单号下改的」的证据** ★ ⇒ ★**证据必须可机器查 (落表台账里查得到那个单号 + 那一行四项齐全)★ ★
2. ★**不许为了不红而放宽「盘上 ≠ 链头 ⇒ 红」这条** ⇒ ★**合法落表 / 合法改板 只应让【链头自动前移】, 不是让判据变松** ★ ⇒ ★**判据阈值一条都不许动** ★
3. ★**不许把「取不准」放宽成「取最近一条」** ⇒ ★**fail-closed 那条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条都不许动** ★ ⇒ ★**ISS-275 的 R6 判据逻辑原样继承** ★

### §4.4 · 我的口径 (★是「代价陈述」, 不是「拍板」★)

★**若被迫排序, 三条方案的【机制代价】从低到高 = ② < ① < ③** —— ★**① 改的是判决源形态 (R6 硬保护段), 代价集中在「一处判据逻辑变更 + 一次落表记录」; ③ 把正确性判据整体外移, 跨域漂移风险最大且不可回退** ★
★**⇒ 但【谁拍】不由本单定** ★ ⇒ ★**★这是机制取舍, 不是我能定的 ⇒ 交 main→老板★** ★
★**本单只做一件事: 把三条方案的「做法 / 抓不抓得住偷换 / 会不会假绿 / 代价 / 谁拍」写清, 并把「假绿风险」这一列补上 (★任务书模板里没有这一列, 但不给这一列就没法比较★)** ★

### §4.5 · 判据口径 (★三条方案各自的 R6 写法 · ★不实现, 只写口径★)

| 方案 | R6 硬保护段应该判什么 | 合法改板的判别形态 |
|---|---|---|
| 现状 (★今天★) | ★**盘上 md5 == 锚点 `hard_protected[].md5`** ★ | ★**无合法路径 (⇒ 那一趟落地当天必红)** ★ |
| ① | ★**盘上 md5 == 落表台账里该文件的链头** ★ (★与网表/脚表同款★) | ★**链头自动前移 ⇒ 绿** ★ |
| ② | ★**盘上 md5 == 锚点值 且 锚点那条的单号在落表台账里查得到** ★ | ★**单号 + 新旧 md5 留痕 ⇒ 绿** ★ |
| ③ | ★**盘上 md5 == 锚点值** (★不变★) + ★**板侧闸 (`check_pcb_drc`/`check_pcb_nets`/`chain_gate`) 绿** ★ | ★**板侧闸绿 ⇒ 绿** ★ |

★**★不管选哪条, SW 侧这一趟的【第一步】都一样: 板侧改板之前, 必须先拿到那三样东西 (新 md5 ×2 + 落表单号) ⇒ 拿不到 = 那一趟落地当天 SW 侧无路可走** ★ ★

---

## §5 · 证据分级

| 结论 | 证据等级 | 怎么量的 |
|---|---|---|
| 板 / `.kicad_pro` / 网表 / 脚表 / BOM 五个 md5 现值 | ★**`[实测]`** ★ | ★**本机 `md5sum` (2026-11-17 08:2x)** ★ |
| R6 对硬保护两件走纯 md5 分支 (不经过链头) | ★**`[实测]`** ★ | ★**本机实读 `SW/tools/check_demo_panel_spec.py` L459~L472 + 沙盒实跑 (改板 md5 ⇒ R6 变红)** ★ |
| 8 个落表残项位号在脚表里都有 2 行 | ★**`[实测]`** ★ | ★**本机 `csv.DictReader` 实读 `HW/netlist_v1_pins.csv`** ★ |
| 5 颗按键的网名映射 | ★**`[实测]`** ★ | ★**本机实读脚表 (pin1 行的 net 列)** ★ |
| `TP_INT` 在网表/脚表/板上命中 0 次 | ★**`[实测]`** ★ | ★**本机 `grep -c`** ★ |
| `C_VBUS_GND_1` 多余 2 焊盘 (pad1=GND / pad2=VBUS_5V_CHG) | ★**`[实测]`** ★ | ★**本机 `bash state/pcbnew_py.sh state/check_pcb_nets.py`** ★ |
| `D_ESD_USB_D_1` → `J_USB_C_1` 板面距离 47.99 mm | ★**`[实测]`** ★ | ★**本机 `python3 HW/check_netlist_selfconsistency.py`** ★ |
| 那一趟落地当天 SW 侧会红 | ★**`[推算]`** ★ | ★**机制推演 (纯 md5 比对 + 板必变) + 沙盒实跑复现 (★见交卷单 B3★)** ★ |
| 板与屏的实物行为 | ★**`[0数据]`** ★ | ★**板与屏不在本机 ⇒ 实物 [实测] = 0 条** ★ |

---

## §6 · 机器可读 JSON 块 (★★闸读它 · ★★本块放最后 ★★)

★**格式**: `schema` = `board-onepass-sw-sync/v1` · `frame` = `B160x100` · `items[]` 每条固定 9 个字段 ★
★**★不许改格式**: 闸 `SW/tools/check_onepass_sw_sync.py` 按这 9 个字段判 (★缺一个即红 ★) ★

```json
{
  "schema": "board-onepass-sw-sync/v1",
  "frame": "B160x100",
  "items": [
    {
      "id": "SW01_PCB_MD5",
      "source_iss": "ISS-266+ISS-275",
      "title": "板 md5 硬保护值 (台账 §1 hard_protected[0]) ⇒ 那一趟改板当天 SW R6 必红",
      "current_state": "[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_protected[0].md5 钉的是同一个值 · R6 对该件走【纯 md5 比对独立分支】(SW/tools/check_demo_panel_spec.py L459~L472) ⇒ 盘上 ≠ 锚点即红, 无链头机制可依赖 ⇒ 那一趟改板当天必红 (ISS-275 只把「台账管的那两个文件」换成链头判决源, 硬保护两件不在链头机制里)",
      "action": "那一趟改板【之前】先走 SW 台账 §4 的合法重锚路径 (方案 ①②③ 三选一, 归 main→老板拍); 板改完后把新 md5 落到【落表台账 + SW 台账锚点】同一处, 不许事后手改 hard_protected 的 md5",
      "criterion": "python3 SW/tools/check_demo_panel_spec.py ⇒ rc=0 (R6 硬保护段: 盘上板 md5 == 台账 hard_protected[0].md5)",
      "step": "S9",
      "blocked_by": "main→老板 (机制取舍: hard_protected 怎么合法跟上, 归 §4 三方案)",
      "evidence": "[实测]"
    },
    {
      "id": "SW02_KICAD_PRO_MD5",
      "source_iss": "ISS-266+ISS-275",
      "title": ".kicad_pro md5 硬保护值 (台账 §1 hard_protected[1]) ⇒ S3/S4 动了封装属性就会跟着红",
      "current_state": "[实测] 盘上 .kicad_pro md5 = 3e504d2be83152e337949723e909be1b · 台账 §1 hard_protected[1].md5 钉的是同一个值 · R6 同走【纯 md5 比对独立分支】⇒ 作业包 §4「全程」行明写「除板 + .kicad_pro (若 S3/S4 动了封装属性) 外逐字节不变」 ⇒ 那一趟它极可能变",
      "action": "同 SW01: 那一趟之前先定重锚路径; .kicad_pro 的 md5 与板的 md5 必须【同批】重锚 (不许只重锚一个)",
      "criterion": "python3 SW/tools/check_demo_panel_spec.py ⇒ rc=0 (R6 硬保护段: 盘上 .kicad_pro md5 == 台账 hard_protected[1].md5)",
      "step": "S9",
      "blocked_by": "main→老板 (机制取舍: 同 SW01)",
      "evidence": "[实测]"
    },
    {
      "id": "SW03_LAND8_DNP",
      "source_iss": "ISS-244+ISS-266",
      "title": "8 个落表残项位号的 value/dnp 一变, SW 侧 timing_check.py F1 断言的期望值就得跟着定",
      "current_state": "[实测] 落表残项 8 行 (D_CHG_LED_1 / D_LED_G_1 / D_LED_R_1 / SW_BOOT_1 / SW_KEY_PWR_1 / SW_KEY_VM_1 / SW_KEY_VP_1 / SW_RST_1) 在脚表里都有 2 行 ⇒ 不是缺脚, 是 value 仍写「待选型」+ land 要同批重画 · SW 侧 SW/tools/timing_check.py:922 的 sw_rst_row_dnp (读 SW_RST_1 的 DNP 状态) + :1491 的断言「RESET_N 上谁在拉 = Q_AND_1 必装 / SW_RST_1 必装 / U_SUPV_1 pin1 DNP」 ⇒ 这 8 行落表后 DNP 状态变 ⇒ 这条断言的期望值要跟着定",
      "action": "落表批次把 8 行的 value/dnp 一次定死; SW 侧在同批把 timing_check.py F1 的期望值按【落表后真值】改 (改的是期望值, 不是判据逻辑); 判据方向不许反转",
      "criterion": "python3 SW/tools/timing_check.py ⇒ rc=0 (71/71) ⇒ 落表后 F1 的期望值必须与落表后脚表一致",
      "step": "S10",
      "blocked_by": "落表批次 (8 行的选型/footprint 归 ISS-241 / ISS-244)",
      "evidence": "[实测]"
    },
    {
      "id": "SW04_CHG_LED_REF",
      "source_iss": "ISS-234+ISS-244",
      "title": "充电灯位号口径有两套 (网表 D_CHG_LED_1 vs SW 关机语义页 Q_CHG_LED_1) ⇒ 那一趟落表前必须对齐",
      "current_state": "[实测] 网表/脚表里充电灯本体位号 = D_CHG_LED_1, 其 board 列 = CHG_BOARD ⇒ 不在 demo 主 PCB 装机范围 (板上没有 D_CHG_LED_1 这个封装; 板上有 D_LED_G_1 / D_LED_R_1 / D_LED_B_1 三颗) · 而 SW/SHUTDOWN_SEMANTICS_SPEC.md 写的充电灯位号是 Q_CHG_LED_1 (该页实测: D_CHG_LED_1 0 次 · Q_CHG_LED_1 6 次) ⇒ 两个位号口径必须在本单对齐",
      "action": "SW 侧把口径写成【D_CHG_LED_1 = 充电灯本体 / Q_CHG_LED_1 = 充电灯驱动 MOS】并在 SW 侧镜像页统一; 板侧那一趟不要碰 CHG_BOARD 的器件 (demo 板不装)",
      "criterion": "python3 SW/tools/check_shutdown_semantics.py ⇒ rc=0 (R1~R7 全过 · 口径页 / HW 文档 / SW 镜像 / 网表 四方一致)",
      "step": "S10",
      "blocked_by": "落表批次 (SW 侧镜像页改动随落表同批; 零落表可先改 SW 侧口径)",
      "evidence": "[实测]"
    },
    {
      "id": "SW05_KEY_NETNAMES",
      "source_iss": "ISS-244+ISS-266",
      "title": "5 颗按键的板侧网络名 ≠ 位号 ⇒ SW 侧代码/断言一律按网名",
      "current_state": "[实测] 脚表实测映射: SW_BOOT_1→BOOT_N · SW_KEY_PWR_1→KEY_PWR · SW_KEY_VM_1→KEY_VOL_M · SW_KEY_VP_1→KEY_VOL_P · SW_RST_1→RESET_N (每颗 2 pad = 信号 + GND) · SW 侧 SW/tools/timing_check.py:1264 的 nl.rail_of(\"R_PU_BOOT_N_1\") (F5 上拉轨域) + :1491 的 RESET_N 拉低链实读 ⇒ 那 8 行落表后, 这两条断言的期望值会变",
      "action": "SW 侧代码/脚本一律用网名 (BOOT_N / KEY_PWR / KEY_VOL_M / KEY_VOL_P / RESET_N); 落表后 SW 侧断言的期望值按【落表后真值】同步 (不改判据逻辑); 板侧 land 重画不许把网名换成位号",
      "criterion": "python3 SW/tools/timing_check.py ⇒ rc=0 (71/71) ⇒ F1/F5 期望值必须与落表后脚表一致",
      "step": "S10",
      "blocked_by": "落表批次 (5 键属那 8 行里)",
      "evidence": "[实测]"
    },
    {
      "id": "SW06_TP_INT",
      "source_iss": "ISS-266+ISS-279",
      "title": "TP_INT (触控中断) 在网表和板上都不存在 ⇒ SW 侧不许按「有触控中断」写代码",
      "current_state": "[实测] TP_INT 命中数: 网表 0 · 脚表 0 · 板 0 ⇒ 这条线根本没画 (板上同族测试点是 TP_USB_D_N_1 / TP_KEY_PWR_1 / TP_RESET_1 等, 没有 TP_INT) · ISS-174 已 verified 说「pin26 没接到 SoM 任何脚」, 但那是在【整机屏】口径下 ⇒ demo 板这一趟要不要接, 是【板侧输入】问题",
      "action": "SW 侧: 按【无触控中断】写代码与判据 (不得引用任何 TP_INT 网名); 板侧: 这一趟若要接, 必须同批落表 + 落位 + 布线 (⇒ 进 S8 布线归零那一批), 否则 SW 侧按无处理",
      "criterion": "grep -c TP_INT HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb ⇒ 命中数 = 0 (板侧现状) ; SW 侧: python3 SW/tools/check_onepass_sw_sync.py ⇒ rc=0 (W5 现状探针 · 三件都 0)",
      "step": "S8",
      "blocked_by": "老板/PM (demo 板要不要接触控中断) + hw-lead (板侧落点)",
      "evidence": "[实测]"
    },
    {
      "id": "SW07_C_VBUS_GND",
      "source_iss": "ISS-266+ISS-279",
      "title": "C_VBUS_GND_1 两个多余焊盘 (充电板件留在 demo 主 PCB) ⇒ 那 2 个焊盘一拿掉, SW 侧 USB 前提判据跟着变",
      "current_state": "[实测] 板上 C_VBUS_GND_1 仍在, 两个带网焊盘挂的是 pad1 = GND / pad2 = VBUS_5V_CHG ⇒ 板↔网表 check_pcb_nets.py 报 C1「多余 2」 · 网表里 C_VBUS_GND_1 两行的 board 列已经是 CHG_BOARD ⇒ 它物理在充电板, 不在 demo 主 PCB ⇒ 那 2 个焊盘一拿掉, SW 侧的 USB 枚举 / S2 救砖链路前提判据跟着变",
      "action": "板侧: 重出板时按 board 列过滤 ⇒ 该封装自动消失 (不许手改板); SW 侧: 随板面变化同步【USB 枚举 / S2 救砖链路】前提判据 (VBUS 前级电容在不在 ⇒ 判据期望值跟着定)",
      "criterion": "bash state/pcbnew_py.sh state/check_pcb_nets.py ⇒ C1 缺失 0 · 多余 0 · 同号异网 0 (现状: 多余 2) ⇒ 那一趟之后 SW 侧 USB 前提判据按「多余 0」写",
      "step": "S2",
      "blocked_by": "-",
      "evidence": "[实测]"
    },
    {
      "id": "SW08_ESD_USB_D",
      "source_iss": "ISS-266+ISS-279",
      "title": "D_ESD_USB_D_1 只有 2 焊盘 + 距 J_USB_C_1 47.99 mm ⇒ SW 侧 USB 前提判据跟着变",
      "current_state": "[实测] 板面 D_ESD_USB_D_1 → J_USB_C_1 板面距离 = 47.99 mm (规格页 §①(4) 引的就是这个数; 要求 ≤ 3.0 mm) · D_ESD_USB_D_1 在脚表里只有 2 行 (pad1 = USB_D_P_SRC / pad2 = GND) ⇒ USB D− 那条路上 ESD 位号数 = 0 · 网表里 D_ESD_USB_D_1 的 dnp = 必装",
      "action": "板侧: 那一趟把 D_ESD_USB_D_1 换 3 脚封装 + 挪到 J_USB_C_1 旁 ≤ 3.0 mm + D− 补 ESD (B-3/B-4/B-5 必须同趟); SW 侧: 同步【USB 侧前提判据】(ESD 在不在 USB 入口 ⇒ SW 侧 USB 枚举/复位前提判据的期望值跟着定)",
      "criterion": "python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ R4 (D− 侧 ESD ≥1 且 D_ESD_USB_D_1 焊盘数 = 3) / R9 (D_ESD_USB_D_1 ↔ J_USB_C_1 中心距 ≤ 3.0 mm) 转绿 ⇒ SW 侧 USB 前提判据按「R4/R9 绿」写",
      "step": "S4",
      "blocked_by": "W-1/W-2 (老板: 一颗双通道 vs 两颗单通道) ⇒ S4 是第一个真正卡在老板的步",
      "evidence": "[实测]"
    }
  ]
}
```
