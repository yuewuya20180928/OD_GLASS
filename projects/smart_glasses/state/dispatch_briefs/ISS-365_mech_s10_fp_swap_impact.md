# ISS-365 · mech-lead · 「板那一趟」S10 换封装真值 · MECH 侧影响面

★★**题**: ★**「板只改一次」那一趟要把 90 件的占位 land 换成官方封装 ⇒ 这一跳对 MECH 侧的几何判据【漂不漂、漂几条、漂了怎么重算】⇒ 查清并做成【一页 + 一道机器闸 + 一份沙盒实测】** ★★
★★**类别**: ★**纯分析 + 新建闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发** ★★

---

## ★★〇 · main 的本机实读 (★2026-11-23 16:1x · 全部数字本机可复跑 · 不抄任何 agent 报告★) ★★

★**① 病灶 (★本单为什么现在必须存在★)**: ★**MECH 侧「板只改一次」那一趟的几何判据 (净空 / 开口 / 20 个 S6 落位 / 座体三方对照) 全部是按【当前板上的自绘占位 land】算出来的** ⇒ ★**而那一趟 S10 要把 90 件换成官方封装 ⇒ 器件 fab 外框 / 焊盘中心距 / 本体尺寸都会变** ⇒ ★**⇒ 现有那些「最小净距 4.6500」「必须清空区 X 139.0025..146.8975」之类的数, 在换封装之后【是不是还成立, 本机没有一条闸会知道】** ⇒ ★**★⇒ 不查清 ⇒ 那一趟改完板才发现结构装不下 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★

★**② ★★最硬的一条交集 (★main 本机实算 · `logs/iss361/04_recon.json` + `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:S6_TARGETS` 块★)★**:
- ★**S6 的 20 个目标落位 = 10 个 `R_SEL_*` + 10 个 `TP_DSI_*`** (★实测名单: `R_SEL_D0_N/P` `R_SEL_D1_N/P` `R_SEL_CK_N/P` `R_SEL_D2_N/P` `R_SEL_D3_N/P` + `TP_DSI_D0_N/P` `D1` `CK` `D2` `D3`·帧 `B160x100`★)
- ★**★那 10 个 `R_SEL_*` 全部落在 S10 的 90 件集合里** (★90 = 靶内 77 + 缺口 13·两者都在 C4-158 里★) ⇒ ★**★⇒ 它们正是「换官方 land」要动的那批 ⇒ ★**⇒ 而 MECH 侧 §9「20 个目标落位 × MECH 保留区」的最小净距结论, 用的就是这些件【当前占位 fab 外框 1.80×1.00 mm · 中心距 1.60 mm】** ⇒ ★**⇒ ★★这就是 MECH 侧在 S10 这一跳上的真缺口: 那 4.6500 的净距结论, 换封装后必须重算, 而没人算过★★** ★
- ★**10 个 `TP_DSI_*` 落在 TP 42 桶 (豁免) ⇒ 不受影响** (★负结论也要写出来·省下一轮重复劳动★) ★

★**③ 座体类器件不受影响 (★负结论 · 同样要有机器证据★)**: ★**`J_DEBUG` / `J_UART` / `J_USB_C` / `J_CHG` / `J_SOM_P1..P4` 与那 90 件的交集 = ∅** (★`J_SOM_P1`/`J_SOM_P3` 的 BOM `type=NET` ⇒ 进不了「必装 ∩ 非 NET/TP」★) ⇒ ★**⇒ MECH §10 的座体三方对照 / 开口尺寸 / 排针 pitch 结论【不受 S10 影响】** ⇒ ★**⇒ 本单要把这条负结论【机器化】(脚本自己算交集), 免得下一轮又重查一遍** ★

★**④ 90 件里真正碰 MECH 侧开口/光孔/键位/ESD 位置的件 (★逐条给依据★)**:
- ★**`D_LED_G`**: ★**结构光孔有/无 = 老板项 (★`MECH/BOARD_ONEPASS_MECH_SYNC.md` §4.3★)** ⇒ ★**它在 90 件里 (换官方 land ⇒ 光孔/落位要跟着核) ⇒ 你只登记, 不代拍** ★
- ★**`D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_USB_D`**: ★**ESD 结构位置要求 = 距连接器 ≤3.0 mm · 共面接地 · 封装 ≤0.5 mm 高 (★ISS-085 登记在 `MECH/` 分片★)** ⇒ ★**换封装后封装高度/本体尺寸变 ⇒ 这条要求还成立吗? 你算, 不代拍** ★
- ★**`D_ESD_USB_D` 2→3 脚随老板 W-1/W-2 分叉** ⇒ ★**两个分支各自的 pad 数/尺寸 ⇒ 两个分支各自对结构的要求, 都要列** ★
- ★**5 只按键 (`SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST`)**: ★**官方 `SW_Push_1P1T_NO_CK_KMR2` 有 4 个物理焊盘 (焊盘号 1,1,2,2) + 更大本体; 现占位 = 3.450×3.100 mm** ⇒ ★**换封装 ⇒ 结构键孔/键帽间隙/相邻键间距全部要重核** ⇒ ★**并给两条路 (★加 2 个具名脚 vs 改选 2 焊盘封装·代价按动力度 3N → 1.5N★) 的结构后果** ★
- ★**`FB_DEMO`**: ★**现占位 = 斜置 2 land @对角 1.000 mm (★本体 bbox 2.100×1.700★); 官方 0805 = 正置 @2.124 mm** ⇒ ★**⇒ 本体变大 ⇒ 若它在某个开口/净空附近 ⇒ 要重算** ★
- ★**`Q_AND` / `Q_ENVC` / `Q_PG`**: ★**3 焊盘件, 现占位 bbox 4.100×5.100 mm ⇒ 官方 SOT-23 本体 ⇒ 高/宽都变** ⇒ ★**⇒ 高件 ⇒ 与镜框腔体/屏蔽罩的关系要重核** ★

★**⑤ MECH 侧现有三道闸现在全绿 (★main 本机实跑·16:2x★)**: ★**`python3 MECH/check_onepass_struct_crosscheck.py` ⇒ rc=0 (N1~N6 全过) · `python3 MECH/check_onepass_mech_sync.py` ⇒ rc=0 (M1~M5 全过) · `python3 MECH/check_board_frame_coords.py` ⇒ rc=0 (四项全过)** ⇒ ★**⇒ 它们【读的是当前板】⇒ 换封装后它们会自动重判 ⇒ ★**⇒ 本单要做的正是: 【提前把这个重判的结果算出来】, 别等那一趟改完板才发现** ★

★**⑥ 沙盒怎么跑 (★main 实读过源码·别踩坑★)**: ★**`MECH/check_onepass_mech_sync.py` 有 `--root` 参数 (★默认 PROJ★) ⇒ 直接 `--root` 指向沙盒根即可** ⇒ ★**但 `MECH/check_onepass_struct_crosscheck.py` 【没有】 `--root` ⇒ 它靠 `PROJ = HERE/..` ⇒ ★**⇒ 沙盒做法: 把 `MECH/` 整个目录 + `HW/PCB/demo_mainboard.kicad_pcb`(副本) + 它要读的那几张表, 复制到 `tmp/iss365_sbx/` 下 ⇒ 跑 `tmp/iss365_sbx/MECH/check_onepass_struct_crosscheck.py` ⇒ 它自动把 PROJ 指向沙盒根** ⇒ ★**★真闸脚本一个字节不许改 (★只改沙盒副本★)★** ★

★**⑦ MECH 侧台账 (★你要在其上作业, 不许重写它★)**: ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` (★ISS-278 · 8 字段板侧输入表 + §9 的 20 落位交叉核对 + §10 的座体/开口段★) · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★ISS-290 · §2 保留区全集 + §3 20 落位逐条明细 + §4 座体三方对照 + §5.6「必须在那一趟一起改」清单 E-1~E-6 + §6 贴角口径 + §7 机器块★) · `MECH/BOARD_GEOM_30MM.md` (★结构侧权威表·60×30 口径★) · `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md`** ★

---

## ★★一 · 本单交付物 (★3 件 · 不许扩项★) ★★

### ★★① 第 1 件 · 一页: ★**新建** `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` ★★

★**必须包含 (★逐条·不许少★)**:
- ★**§0 口径与读数** ★: 上面 ①②③⑤ 六条 (★每个数字能被 §三 的某条命令复现, 不许抄 main 的转述★) ★
- ★**§1 敏感度总表 (★逐件·★只列与 MECH 侧有关的件, 不许把 90 件全抄进来★)★**: ★**`ref` / 现占位几何 (★读板·`[实测]`★) / 目标封装几何 (★读 `.kicad_mod` 的 fab 外框 + 本体 + 焊盘数·`[实测]`★) / Δ (★外框 Δ / 本体 Δ / 焊盘数 Δ★) / 它碰 MECH 侧的哪一条 (★保留区 / 开口 / 光孔 / 键位 / ESD 位置 / S6 落位 / 腔体高度★) / 判定 (★不受影响 / 需重算 / 需老板拍★) / 重算后的数 (★你实算的, 不许抄旧结论★) / 证据等级 / 降级方案** ★
- ★**§2 ★那 10 个 `R_SEL_*` 的专项 (★本单的正题★)**: ★**逐个算「换官方 land 后 (★fab 外框 / 中心距 / 本体★) 对 MECH 保留区与相邻落位的净距」** ⇒ ★**给出「换封装前后的净距两列 + Δ」** ⇒ ★**★并回答一个问题: 换封装后这 10 个落位【还要不要重排】? 只给依据 + 代价, 不代拍** ★
- ★**§3 负结论 (★机器证据★)**: ★**座体类 6 组 + 10 个 `TP_DSI_*` 与 90 件的交集 = ∅ ⇒ 不受 S10 影响** (★交集由脚本算, 不许手写★) ★
- ★**§4 两条分支的结构后果**: ★**K2 (`D_ESD_USB_D` 2 vs 3 脚) · K3 (5 只按键 加 2 脚 vs 改选 2 焊盘封装) ⇒ 各自对结构的要求 + 代价 + 会红哪道 MECH 闸** ★ (★只登记, 不代拍★) ★
- ★**§5 「必须在那一趟一起改」清单的追加建议**: ★**基于 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §5.6 的 E-1~E-6 追加 E-7+ (★例: E-7 = 10 个 `R_SEL_*` 换封装后净距重算·E-8 = 5 只按键本体变化后的键孔要求·E-9 = `D_LED_G` 光孔·E-10 = ESD 封装高度★)** ⇒ ★**★建议, 不许改那两份既有页 (★老字零改动·追加建议写在本单自己的页里★)★** ★
- ★**§6 降级方案 (★逐件必填·一件不空·三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★)** ★
- ★**§7 未决项与卡点** ★: ★**哪些要老板拍 (★`D_LED_G` 光孔有/无 · W-1/W-2 · 键 3N vs 1.5N·你只登记不代拍★) ★

### ★★② 第 2 件 · 一条机器闸: ★**新建** `MECH/check_onepass_s10_fp_swap_impact.py` ★★

★**判据 (★内容级·**不挂 md5**·沿用 `MECH/check_onepass_mech_sync.py` 的做法★)**:
- ★**M0** 基准块存在且是合法 JSON (★同款 BEGIN/END 块★) ★
- ★**M1** ★**90 件集合由脚本自己算出来** ★: ★**读 `HW/BOM_v1.csv` + 读板 + 读 `HW/FP_TRUTH_BASELINE.md` §2 靶子 + 读 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2 缺口 ⇒ 算出 77 + 13 = 90** ⇒ ★**页里写的 ≠ 脚本实算 ⇒ 红** ★
- ★**M2** ★**10 个 `R_SEL_*` 落在 90 件集合里 (★脚本实算交集, 不许手写★)** ⇒ ★**这是 §2 专项的机器前提** ★
- ★**M3** 负结论可证: ★**座体类 6 组 ref + 10 个 `TP_DSI_*` 与 90 件的交集 = ∅ (★脚本实算★) ⇒ 不为空即红** ★
- ★**M4** §1 逐件字段齐全 (★`ref` / 现占位几何 / 目标几何 / Δ / 判定 / 重算后的数 / 证据等级 / 降级方案★) ⇒ ★**漏件即红 + 点名 ref** ★
- ★**M5** ★**几何一致性**: ★**每件页里写的「目标 fab 外框 / 本体 / 焊盘数」== 脚本从该 `.kicad_mod` 实测出来的值** ⇒ ★**对不上即红 (★抓的是「抄错几何」★)** ★
- ★**M6** 证据等级全在五级白名单 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★ ⇒ 写 `[官方]` = 红★) + 降级方案逐件非空 ★
- ★**M7** 正文无挂起措辞 (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★) ★

★**`--selftest` 反向用例 ≥7 条, 每条自证「红的是目标那一条, 其余仍绿」**: ★**① 删掉 §1 里某一行 (★挑 `R_SEL_CK_P`★) ⇒ M4 红 · ② 把某行目标 fab 外框改错 ⇒ M5 红 · ③ 清空某行降级方案 ⇒ M6 红 · ④ 把某行证据等级写成 `[官方]` ⇒ M6 红 · ⑤ 正文塞「等原厂回信」⇒ M7 红 · ⑥ 篡改 §1 的 90 这个数 ⇒ M1 红 · ⑦ 在 §2 里改一个 `R_SEL_*` 的落位坐标 (★不在 90 件集合里·就该红★) ⇒ M2 红 · ⑧ 手工往「座体类不受影响」名单里塞一个 `J_USB_C` ⇒ M3 红** ★

★**★沙盒一律落项目盘 `tmp/iss365_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满★)★**

### ★★③ 第 3 件 · 交卷页 + 分片 + 留证 ★★
- ★**交卷页** `HANDOFF/2026-11-23_mech-lead_ISS365_S10换封装对MECH侧影响面.md` (★B1~B6 六段齐全 + 20 条验收逐条判定 + 落盘文件清单 + 沙盒留证路径★) ★
- ★**分片** `state/fragments/mech.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ ★**写前后各记一次 md5 基线·期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖** ★
- ★**留证** `logs/iss365/` (★基线 md5 / 实算脚本 / 90 件与 10 件 `R_SEL_*` 的交集读数 / 沙盒前后三道 MECH 闸的输出 / selftest 全量输出 / 闸复跑输出★) ★
- ★**★留证里必须有【沙盒重判实测】那一件**: ★**在 `tmp/iss365_sbx/` 的板副本上按 §1/§2 把受影响的件换成官方 land ⇒ 跑三道 MECH 闸 (★沙盒副本★) ⇒ 前后输出并排 ⇒ 写清「哪几条判据漂了 / 漂了多少 / 漂了之后要重算什么」** ★

---

## ★★二 · 边界 (★逐条·不许越★) ★★

★**零写板** ★ (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B ⇒ **开工前 + 交卷后各打一次双证**★) ★
★**零落表** ★ (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸** ★ (★`MECH/check_onepass_struct_crosscheck.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节不许改★) ★
★**零改既有页面正文** ★ (★`MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` · `MECH/BOARD_GEOM_30MM.md` · `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_FRAME_CALIBER.md` ★**老字一字不许删·不许改·只在交卷页里写建议**★) ★
★**零挂链** ★ (★新闸交脚本但不挂进 `state/gate_check.py` —— 挂链是 main 的机制地界★) ★
★**零外发 / 零采购 / 零联系供应商** ★ (★不发邮件·不询价·不问询·不下采购单★) ★
★**不替老板拍板** ★ (★`D_LED_G` 光孔有/无 · `D_ESD_USB_D` 2 vs 3 脚 (★W-1/W-2★) · 按键 3N vs 1.5N ⇒ 你只登记缺口 + 给依据 + 给代价·**不许代选**★) ★
★**不写别人的分片** ★ (★只写 `state/fragments/mech.yaml`★) ★
★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★
★**证据分级必标** ★ (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★ ★

---

## ★★三 · 必跑命令 (★全部真实存在·2026-11-23 16:2x main 本机实测过★) ★★

```bash
python3 MECH/check_onepass_struct_crosscheck.py   # 结构侧交叉核对闸 · rc=0 (N1~N6 全过·★main 实跑过★)
python3 MECH/check_onepass_mech_sync.py           # MECH 侧板侧输入闸 · rc=0 (M1~M5 全过·★main 实跑过★)
python3 MECH/check_board_frame_coords.py          # 板框坐标闸 · rc=0 (四项全过·★main 实跑过★)
python3 MECH/check_demo_struct_truth.py           # 结构真值闸 (★main 未实跑 rc·你跑并写进留证★)
bash state/pcbnew_py.sh state/check_pcb_nets.py   # C4 的 158 件读数 (★必须带 KiCad python★)
python3 HW/check_fp_truth_coverage_gap.py         # 缺口闸 · rc=0 (★main 实跑过★) ⇒ 缺口 13 件
python3 MECH/check_onepass_s10_fp_swap_impact.py  # ★本单新建★
python3 MECH/check_onepass_s10_fp_swap_impact.py --selftest
python3 state/merge.py                           # rc 必须 0
python3 state/gate_check.py                      # rc 必须 0 · Q1 必须 18/18
python3 state/check_brief_commands.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② 90 件集合 == 脚本实算 ③ 10 个 `R_SEL_*` ⊂ 90 件 (脚本实算) ④ 座体类 + `TP_DSI_*` 与 90 件交集 = ∅ (脚本实算) ⑤ §1 逐件字段齐全 + 漏件点名 ⑥ 每件目标几何 == 脚本从 `.kicad_mod` 实测 ⑦ 证据等级全在五级白名单 ⑧ 降级方案逐件非空 ⑨ 正文零挂起措辞 ⑩ §2 那 10 个 `R_SEL_*` 的换封装前后净距两列 + Δ 齐全 ⑪ §2 回答「要不要重排」+ 依据 + 代价 ⑫ §3 负结论有机器证据 ⑬ §4 两条分支 (K2/K3) 的结构后果 + 代价齐全 ⑭ §5 的 E-7+ 追加建议齐全 ⑮ 沙盒在项目盘 `tmp/iss365_sbx/` ⑯ **沙盒给出三道 MECH 闸换封装前后的并排输出 + 漂了哪几条 + 要重算什么** ⑰ 板 md5/mtime 逐字节未变 ⑱ 网表/脚表/BOM md5 逐字节未变 ⑲ 既有闸脚本一个字节未改 + `merge.py` rc=0 + `gate_check.py` rc=0 且 Q1 18/18 ⑳ 分片只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss365/` 留证在盘
