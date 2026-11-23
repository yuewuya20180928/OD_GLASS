# ISS-378 · sw-lead · 「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的**固件影响面清单** + ★**ISS-344 与「SoM 侧无 JTAG 引出」的板侧口径冲突收敛 (官网自查证)** ★ · 纯分析 + 文档 + 新建闸 · 零写板 · 零落表

★★**开单依据 (★main 2026-11-24 02:2x~02:5x 本机实读 + 实算 · 不抄任何 agent 报告★)★★**:
★**① 触发事件**: ★**ISS-375 (sw-lead) 已于 2026-11-24 02:4x 由 main 独立复核签收 verified** (★签收闸 `state/_apply_20260724_0235_cronfb67_sign_iss374_375.py` 自跑验收线, fail-closed, 全绿才签; 自测 10/10 ★) ⇒ ★**sw-lead 槽位真空出来** ★
★**② 队列实读**: ★**`python3 state/advance.py --json` ⇒ `internal: []`** (★三个总工名下零 open 可派 ⇒ 队列对 sw 这条线【真断线】★) ⇒ ★**本单 = 新开** ★
★**③ 本单正题 (★两件·都在 ISS-375 的交卷页里点名要 main 回答·本单只做「事实与代价」, 不代拍★)★**:
★**A. 固件影响面**: ★**ISS-375 已把「换 land 后的物理针序契约」钉死 (`rot 90` / `rot 270` 两候选几何逐字相同), 但【固件侧到底受不受影响】至今没人答** ⇒ ★**板只改一次 ⇒ 改板之前必须知道: 哪些固件代码 / 哪些网名映射会跟着变, 哪些一个字都不用动** ★
★**B. ★★板侧口径冲突 (★最高优先级·因为它直接决定「板要对着一个不再变的网表画」★)★★**: ★**ISS-344 的口径把 `JTAG_TDI` 列进 8 条「必需」单端脚 (`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` §7-4 / `ISS344-CORR` 块), 而 ISS-375 实测 `JTAG_TDI_SOC` 的 SoM 侧端点此刻就是 `SoC_NC`** ⇒ ★**「必需」与「SoM 侧不存在」直接对撞 ⇒ 板画之前必须把这一条收敛掉 (改口径 / 改网表 / 换 SoM 三选一 + 代价)** ★

---

## ★★一 你这一趟要交的东西 (★三件 + 交卷页 + 分片★) ★★

★**① ★新建★ 一页 `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (★本单产出物★)** ⇒ ★**必须含**:
1. ★**§0 一句话结论 + 范围**: ★**两块排针换 land 对固件的影响到底有多大 (★一句话: 固件侧受影响的是【网名→pad 号】映射还是【物理针序/救砖线序】, 两者必须分开说★) + 本页只做影响面与代价, ★**不改一行固件本体、不改网表真源** ★
2. ★**§1 逐网影响表 (★主表★)**: ★**板面上与 `J_DEBUG` / `J_UART` 相关的每一条网逐条一行** ⇒ ★**字段**: ★`网名` / ★`两端节点` / ★`当前落在哪颗件哪个 pad` / ★`固件侧当前用法 (★按 SW 侧代码/文档实读, 不许猜★)` / ★`换 land 后是否变化` / ★`变化性质 (★无 / 仅物理针序 / 需改代码★)` / ★`若需改: 改哪个文件的哪一行 (★只写行号与函数名, 一行都不许改★)` / ★`证据等级` / ★`来源 (文件:行号)` ⇒ ★**相关网至少覆盖**: ★`JTAG_TCK` / `JTAG_TMS` / `JTAG_TDI` / `JTAG_TDO` / `UART_TX` / `UART_RX` / `BOOT_N` / `KEY_*` / `RST*` / ★**USB 侧 (`USB_CC1`/`USB_CC2` 等) 若与排针同束也要列** ⇒ ★**以板面 + 网表实读为准, 比我列的这份全或多都可以, 少不行** ★
3. ★**§2 救砖链 (★这一节是硬需求★)**: ★**三条链 (USB / UART / JTAG) 各自: 现状能不能救 / 换 land 后还能不能救 / 断了会死在哪一步 / 降级路径是什么** ⇒ ★**必须给出「最坏情况下只剩哪条链」的一句话结论** ⇒ ★**只登记不代拍**
4. ★**§3 ★★`JTAG_TDI` 冲突收敛 (★本单最重要的一节★)★★**: ★**三条路逐条给代价 (★不许代拍·交 main 裁★)★**:
   - ★**① 改口径**: ★**把 `JTAG_TDI` 从「必需」里移出 (或标成板侧 NC) ⇒ 代价 = 板侧 `J_DEBUG` 四根只剩两根有主控侧对端 ⇒ 救砖能力降级 + 口径页要改 (★`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 要追加式订正, ★那件事归 main, 你只给代价★)**
   - ★**② 改网表**: ★**板要对着一个不再变的网表画 ⇒ 改网表是「改板那一趟」的前置条件, 不是免费选项 ⇒ 代价 = 脚表/网表要动 + 固件要跟改 + 可能牵连其它零铜网**
   - ★**③ 换 SoM**: ★**放弃 S3 救砖 (板载 SoM 侧救砖) ⇒ 只剩 S4 返厂 ⇒ 代价 = 返厂周期 + 产线依赖**
   ⇒ ★**每条给: 依据 + 代价 + 牵连面 + 需要谁拍** ⇒ ★**★★并给「我的建议」但标明不代拍★★**
5. ★**§4 ★官方自查证 (★自己查 · 不许等外部回复★)**: ★**查 SoC 与 SoM 两侧到底有没有 JTAG 引出** ⇒ ★**证据等级**: ★`[官网]` (★官方 datasheet / 厂商官网★) / ★`[实测]` (★本机可复现★) / ★`[媒体]` / ★`[推算]` / ★`[0数据]` ⇒ ★**★本机已经有的官网级素材 (★你要自己实读, 不要抄我这几行字★)★**: ★**① `HW/RK3572_PIN_TABLE/rk3572_pins.csv` (★由官方 `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` / `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` 解析而来★) ⇒ ★`grep -i jtag` 命中 4 行, 全是 ★`JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1` ⇒ ★**SoC 侧只有 TCK/TMS, 没有 TDI/TDO 的 mux 名** ★ ★**② `HW/PCB/FET3572C_PIN_TABLE.csv` (★SoM 模块对外引脚表, 399 数据行★) ⇒ ★`grep -ic jtag` = 0 ⇒ ★**模块侧没有 JTAG 引出** ★ ★**③ `HW/PCB/SOM_PIN_MAPPING.md` (★SoM 映射页★) + `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` (★官方事实页★) + `HW/rk3572_official_facts_check.py` (★官方事实闸★) ⇒ ★**都要实读** ★ ⇒ ★**★你自己必须把这两条 grep 跑出来 + 逐行实读那 4 行 + 交叉核对 `HW/netlist_v1_pins.csv` 里 `JTAG_TDI_SOC` 的 SoM 侧端点, 然后写清结论 (★结论若与我上面写的不同, ★**以你本机实读为准**, 但必须在页里写清差在哪、为什么差★)★** ⇒ ★**查不到 ⇒ 写 `[0数据]` + 降级方案 (必须项) ⇒ ★**零外发: 不许发邮件/询价/问原厂/等回信 ⇒ 一律自己查 (可再上网查官网, 但结论要标 `[官网]` 并给 URL 与查证日期)** ★
6. ★**§5 未决项 (★只登记不代拍★)**: ★**逐条写清「要谁回答什么」★** ★**§6 复跑命令 + §7 边界自证★**

★**★与已签收件的关系 (★不许破坏留证链★)★★**:
★**`SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (★ISS-375·已签收 verified★) 与 `SW/tools/check_debug_pin_order_contract.py` (★已签收★) ⇒ ★**你一个字都不许改★** ⇒ ★**只许引用 (★引用时写清来源页 + 行号★)** ★
★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (★§7-4 / `ISS344-CORR` 块★) 是既有口径页 ⇒ ★**只许【追加式】引用与指出冲突, ★**不许改正文 / 不许删老字 / 不许自己把口径改掉** ⇒ ★**要不要落订正块归 main★** ★
★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` ⇒ ★**只读, 一个字都不许改★** ★

★**② ★新建★ 一条闸 `SW/tools/check_debug_header_fw_impact.py` (★本单产出物★)** ⇒ 判据 **W0~W8** (★每条 fail-closed·每条带反向用例★):

| # | 判据 | ★**不许写死的**★ |
|---|---|---|
| W0 | ★**§1 逐网影响表逐行与网表/脚表实读一致 (★自己从 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 重新读, 不许抄表★)** ★ | |
| W1 | ★**每行必须有「变化性质」三分类 (无 / 仅物理针序 / 需改代码) 且不许留空** ★ | |
| W2 | ★**「需改代码」的行必须给出 文件 + 行号 + 函数名, 且 ★**闸必须核实那个文件确实存在、那行确实存在** (★不许写空话★)** ★ | ★不许写「大概在某处」 ★ |
| W3 | ★**§2 三条救砖链 (USB / UART / JTAG) 必须都在页上, 且必须有一句「最坏只剩哪条链」的结论** ★ | |
| W4 | ★**§3 三条路 (①改口径 / ②改网表 / ③换 SoM) 必须三条都在页上, 每条都要有代价 ⇒ 少一条 ⇒ 红** ★ | ★防「只写自己 favorite 那条」 ★ |
| W5 | ★**★SoC / SoM 两侧 JTAG 的事实必须【由闸自己跑 grep 实测出来】(★不许抄页上的数★) ★** + ★**结论必须同时出现「TCK/TMS」与「TDI/TDO」两个方向 (★有则写有, 无则写无, 不许含糊★)** ★ | ★**这是本闸最核心的一条** ★ |
| W6 | ★**证据等级五级白名单 + ★**零挂起措辞 (★不许出现「等原厂回信 / 待外部确认 / 等外部回复」★) + ★**查不到处必须同时出现 `[0数据]` 与「降级方案」** ★ | |
| W7 | ★**零写板 + 零落表自证** (★板 md5/mtime/size 三项 == 基线★ + ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` md5 == 基线★) ★ | |
| W8 | ★**零挂链** ⇒ ★**自证: `grep -c check_debug_header_fw_impact state/gate_check.py` == 0** ★ | ★挂不挂归 main★ ★ |

★**★必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」★)★★**
★**★其中至少 3 条必须专打这三种病 (★都是本项目反复出的病★)★★**:
★**① 把 §3 的三条路删掉一条 ⇒ W4 必红 ★**
★**② 把 §3 里的 SoM 侧结论从「无 JTAG 引出」改成「有 JTAG 引出」⇒ W5 必红 (★证明闸真在跑 grep, 不是抄页★) ★**
★**③ 把一条「需改代码」的行里的文件名写成一个不存在的文件 ⇒ W2 必红 ★**

★**③ ★新建★ 一页交卷页 `HANDOFF/2026-11-24_sw-lead_ISS378_排针换land固件影响面与JTAG口径冲突.md` (★本单产出物★)** ⇒ ★**B1 结论摘要 / B2 验收标准自评 (逐条 通过/不通过/未验) / B3 证据分级 / B4 接口取值声明 (interface_claims) / B5 未决项与卡点 (★要谁回答什么★) / B6 自证复现命令 (★必跑命令原样输出★) + 边界自证** ⇒ ★**占位符 = 0**

★**④ 分片**: ★**写 `state/fragments/sw.yaml` (★必须走 `python3 state/frag_write.py`·★禁止 `open(p,"w")`★)** ⇒ ★**本单条目 = 产出物 + interface_claims + needs_from + status(phase=fixing·★不落 open★)**

---

## ★★二 边界 (★违反即红★) ★★

★**① 零写板** ★**② 零落表** (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` 一个字都不许改★) ★**③ 零改既有闸 / 零改已签收页 / 零改既有口径页正文** ★**④ 零改固件本体** (★只许写「改哪一行」的清单, 一行都不许改★) ★**⑤ 零挂链** (★新闸不许进 `state/gate_check.py`★) ★**⑥ 零外发** (★不发邮件/询价/问询/采购; 不许等外部回复★) ★**⑦ 不代拍** (★`JTAG_TDI` 冲突的终裁归 main / 老板, 你只给三条路 + 代价 + 建议★) ★**⑧ 沙盒只落 `tmp/iss378_sbx/` + `logs/iss378/`** ★**⑨ 不改别人的分片** ★**⑩ 未拍板不许进 `state/issue_log.yaml` (★不许自签台账★)**

## ★★三 必跑命令 (★全部 rc 要贴进交卷页 B6★) ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_debug_header_fw_impact.py             # rc=0
python3 SW/tools/check_debug_header_fw_impact.py --selftest  # rc=0 · 末行 ALL TESTS PASS
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py  # rc=0 (★既有闸·只跑不改·证明零漂移★)
grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv | head -10    # ★自己实读, 不许抄我这几行★
grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv                     # ★自己实读★
python3 state/merge.py                                         # rc=0
python3 state/gate_check.py                                    # rc=0 · Q1 18/18
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-378_sw_debug_header_fw_impact.md  # rc=0
grep -c check_debug_header_fw_impact state/gate_check.py        # 必须输出 0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv  # 必须与基线一致
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                # 必须 2026-11-06 07:07:17.362193413 / 4940213
```
★**★注意 (★本机环境事实★)**: ★**`/tmp` 用户配额已打满 ⇒ 任何把门禁输出重定向到 `/tmp` 的写法会出假读数 (rc=120 / 0 字节) ⇒ 全部改落项目盘 `state/.verify/` 或 `logs/iss378/`★**

## ★★四 你这一趟【不许做】的事 ★★
★**不许动板** ★**不许改网表/脚表/BOM** ★**不许改固件本体** ★**不许改已签收件 (ISS-375 的页与闸)** ★**不许改 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 正文** ★**不许外发任何邮件/询价/问询** ★**不许等外部回复** ★**不许代拍 `JTAG_TDI` 冲突的终裁** ★**不许自签台账** ★**不许挂链**
