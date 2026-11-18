# ISS-277 · hw-lead 任务书 —— ★★「板只改一次」那一趟的【板侧漏项覆盖度收口 + 机器闸】★★ (★纯分析 + 作业包订正类 · 零写板★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 07:3x · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
>
> ★**本单性质**: ★**内部活 · PCB 线 · 纯分析 + 作业包订正 + 机器闸类** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零改既有判据阈值** ★ ⇒ ★**不是老板级拍板** ★
>
> ★**为什么这一单现在必须做**: ★**老板 2026-11-17 00:43 新主线 = 绘制 PCB 图** ★ ⇒ 「板只改一次」那一趟 (S1~S13) 就是正面战场 ⇒ ★**但本单【一行板都不写】** ★ —— 本单只做一件事: ★**把「那一趟要做的板侧项」收成【一份机器可读清单 + 一道覆盖度闸】, 让任何一项在交卷单里被发现却没进作业包的情况【当场红】** ★ ⇒ ★**否则漏做一项 = 板 md5 变第二次 = 留证链 / Gerber / 投产包 / 盖章全白跑一遍** ★

---

## ① 病灶 (★main 本机实读, 不抄任何交卷报告★)

### ★1.1 作业包是 11-17 01:2x 的 v3, 而那之后又出了 6 个单★

★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` = ★**v3 (ISS-266, 2026-11-17 01:2x)** ★ · 381 行 · 已有 §3 S1~S13 + §4 每步的闸 + §5 md5 基线 + §6 卡点 + §7 P7 + §8.1 三坑已修。

★**但 11-16 22:25 ~ 11-17 07:0x 这段窗口里又出了 6 个单, 各自发现了板侧项, 而作业包没有随之更新, 也没有任何一道闸检查「作业包是否覆盖了全部板侧待办项」** ★

| 单号 | 交卷时刻 | 板侧发现 | 作业包里有吗 |
|---|---|---|---|
| ISS-241 | 11-16 22:25 后 | ★**F-1** `D_ESD_CAM` 器件脚接反 (CSI lane 无 ESD) · ★**F-2** `Q_AND` pad 序 D/S/G vs 库 G/S/D (AND 变 OR) · ★`D_ESD_TC` = SP0503BAHT (SOT-143-4 ⇒ 充电板 footprint 得给 4 焊盘) | ★**没有** (§3-S4 只写了 USB ESD 三件) |
| ISS-244 | 11-17 00:0x | ★**三条实物级 P0**: `Q_PG` 角色错 (开不了机) · `Q_AND` 栅漏对调 · `D_ESD_CAM` 接反 | ★**没有** |
| ISS-247 | 11-17 00:2x | ★**F2** `J_CHG` 位号消歧 (只登记不做) · ★**F3** 板侧 43 颗 DNP 零标记 | ★F3 ≈ §3-S7 (43 位号) ⇒ 要核对; ★**F2 没有** |
| ISS-274 | 11-17 06:5x | ★**S6 真实位移只有 `R_SEL_D3_P` 一处** (20 distinct 不是 21) · 坐标帧声明 | ★**已并入** (追加式订正) ⇒ 本单只核对 |
| ISS-276 | 11-17 07:0x | 检修口/调试口开口 **必须拆成两条** (合并不可行) · 座体真实高度 **[0数据]** · `D_LED_G` 光孔 **[0数据]** | ★**没有** (MECH 侧刚出, HW 侧未收) |
| ISS-239 | 11-17 05:2x | ★`U_LDO_S28.pin3` A/B 两案 ⇒ **若走 A 案, 板必须补 pad3** | ★**没有** |

⇒ ★**⇒ 结论: 「板侧项」现在散在 ≥6 份交卷单 + 2 个闸 + 1 份作业包里, 没有任何一处是【全集】, 也没有任何一道闸能发现「某项只在交卷单里、没进作业包」⇒ ⇒ 那一趟漏做一项 = 板改第二次, 这条路今天仍然开着** ★

### ★1.2 现状基线 (★main 07:0x~07:2x 本机实跑/实读★)

| 项 | 实测 | 读法 |
|---|---|---|
| 板 | Edge.Cuts **160.10 × 100.10** · 8 层 · 186 封装 · md5 `611b869e…` | `bash state/pcbnew_py.sh` 读板 |
| unconnected | **45** (需 0) | `python3 state/check_pcb_drc.py` |
| DRC 违规 | **0** | 同上 |
| 板↔网表焊盘级 | 网表 480 / 板上带网 482 · 缺失 0 · 同号异网 0 · ★**多余 2: `C_VBUS_GND` pad1=GND / pad2=VBUS_5V_CHG** ★ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ ★**rc=1 (既有状态, 本单不负责修)** ★ |
| 网表侧未落表 | **18 条** (V-3 13 + V-4 1 + 板侧 4) | `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1 ★**不变** ★ |
| Gerber | **32 个齐** | `python3 state/check_pcb_drc.py` / `state/gen_production_pack.sh` 现状 |
| 落表残项 | **8 行**: `D_CHG_LED`/`D_LED_G`/`D_LED_R`/`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST` ⇒ ★**其中 4 键 + 2 LED 的 land 必须同批重画** ★ | ISS-244 §7 实读 |

★**注意**: ★**作业包 §3-S2 (B-1) 写的是「`C_VBUS_GND` 从 demo 主 PCB 拿掉」, 而实测是【这 2 个焊盘现在挂在 `GND` 与 `VBUS_5V_CHG` 两个网上】★ ⇒ ⇒ **只写「拿掉器件」是不够的, 还要写清「这两个焊盘当下各挂什么网」** ⇒ 本单要把这一类「只写了动作、没写现状」的行补齐 ★

---

## ② 你要交的东西 (★一句话★)

★**把「板只改一次」那一趟的板侧项收成【一份机器可读清单 + 一道覆盖度闸】, 并把散落的新发现逐条并回作业包 ⇒ 任何一项只在交卷单里而没进作业包 = 当场红** ★

★**交卷物 (5 件)** ★

1. ★**新建** `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` —— ★**板侧项全集 (机器可读)** ★:
   - §1 ★**一句话口径** + ★**坐标帧声明** (★全部 = 现役帧 `B160x100` = ISS-274 `HW/PCB/BOARD_FRAME_CALIBER.md` 的帧 ★ · 与 `F30A`/`P60x15` 不可混用★)
   - §2 ★**逐条表 (机器可读 JSON 块放最后)**: ★**每条字段固定 9 项** ★ ⇒ `id` / `source_iss` (来源单号) / `title` / `current_state` (★现状实测值, ★必带 `[实测]`/`[推算]`/`[0数据]` 证据等级★) / `action` (那一趟要做什么) / `criterion` (★**判据命令 + 期望 rc/期望值, 必须是真命令★) / `step` (★归属步, 必须 ∈ S1~S13★) / `blocked_by` (★阻塞前置 / 谁拍★) / `evidence` (证据等级)
   - §3 ★**新发现并入表**: ★**把 §1.1 那张表里的 6 个单逐条映射进清单**, ★并标明哪几条是「作业包已有 (只核对)」/「作业包缺 (本单补)」★
   - §4 ★**归属步分布表**: S1~S13 每步各覆盖几条 ⇒ ★**没有一项的步不许留空** ★
   - §5 ★**归老板/归 main 拍的清单** (★只列, 不代拍★): ★`U_LDO_S28.pin3` A/B 案 (★A 案 ⇒ 板须补 pad3★) · ★LED 亮度档 G-5 (★亮度档一改 ⇒ 改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位 ⇒ 排在那一趟之后 = 板要改第二次★) · ★P7 画哪一块 (160×100 台架板 vs 产品板)★ · ★`D_ESD_TC` 4 焊盘 footprint 方案★
   - §6 ★**机器可读 JSON 块** (★闸要读它, 格式自己定但要稳★)
2. ★**订正** `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★**追加式, 老字一字不删★**):
   - ★**新增 §3-S0「板侧漏项并入表 (ISS-277)」** ★ ⇒ 把清单里「作业包缺」的那几条**逐条**并到对应步 (★S2 / S4 / S6 / S7 / S10 / S13★) ⇒ **每条写「并入哪一步 + 现状 + 判据」**
   - ★**§4 每步的闸**: 补上并入项对应的闸行 (★命令 + 期望 rc★)
   - ★**§1 现状基线**: 追加今天实测的 §1.5 段 (★unconnected=45 / DRC=0 / Gerber 32 / 焊盘级多余 2 的实情 / 8 行落表残项 / 18 条未落表不变★) ⇒ ★**只追加, 不许改老基线行** ★
3. ★**新建** `HW/check_onepass_preflight_coverage.py` —— ★**覆盖度机器闸** ★:
   - **P1** ★**清单可解析**: JSON 块能解析 + ★**每条 9 个字段齐全** (★缺一个字段即红★)
   - **P2** ★**归属步合法**: `step` ∈ S1~S13 + ★**S1~S13 每步至少被覆盖一次** (★不许有步没人管★)
   - **P3** ★**判据命令真存在**: ★**清单里每条 `criterion` 的命令必须在本机真实存在 (★照 `python3 state/check_brief_commands.py` 的口径★)** ⇒ ★**不许把不存在的命令写进清单** ★
   - **P4** ★★**覆盖度 (★本单核心判据★)**: ★**从 6 份来源交卷单里 grep 出板侧项标记** (★`F-1` / `F-2` / `D_ESD_CAM` / `Q_AND` / `Q_PG` / `D_ESD_TC` / `U_LDO_S28.pin3` / `J_CHG` / 8 行残项的 8 个位号 等★) ⇒ ★**每一项都必须在清单里出现** ⇒ ★**漏一条即红** ★ ⇒ ★**同时反向: 清单里不许有来源不明的项** (★每条必须带 `source_iss`★)
   - **P5** ★**现状一致**: ★**清单里标 `[实测]` 的现状值必须与盘面实测一致** ⇒ ★**改了盘面没改清单 = 清单过期 = 当场红** (★这是防止「清单又变成第二份过期文档」的关键★)
   - **P6** ★**受保护 5 件 md5 逐字节不变** (板 / `.kicad_pro` / 网表 / 脚表 / BOM)
   - `--selftest` ★**反向用例 ≥ 6 条** ★ (★每条都要自证「真的改到了目标那一处」★): ★**① 清单里删掉一条 ⇒ P4 红 ② 改一条现状值 ⇒ P5 红 ③ 抽掉一个字段 ⇒ P1 红 ④ 把归属步改成 S99 ⇒ P2 红 ⑤ 判据命令写成不存在的 ⇒ P3 红 ⑥ 改受保护 5 件之一 ⇒ P6 红** ★
4. ★**交卷单** ★**新建** `HANDOFF/2026-11-17_hw-lead_ISS277_板侧漏项覆盖度收口.md` —— **B1~B6 六块齐全** (★B1 结论摘要 · B2 验收标准逐条自评 · B3 反向自证贴实跑原始输出 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令★) ⇒ ★**B3 必贴 P4 覆盖度闸「漏项 ⇒ 红」的实跑输出** ★
5. ★**分片** ★**走** ★**`python3 state/frag_write.py --agent hw-lead`** ★ (★**禁止 `open(p,"w")`** ★): 登记 ★**2 条 claim** (★板侧项全集清单已立 + 覆盖度闸已立★) + ★**artifact** ×3 (★清单页 / 新闸 / 交卷单★) + ★**1 条 need 给 main** (★「§5 那几条归老板/归 main 拍的清单, 请 main 排期; 其中 `U_LDO_S28.pin3` A 案 ⇒ 板须补 pad3, 与『板只改一次』直接冲突, 必须先拍★」★) + ★**status** (phase=delivered · progress_pct=100)

---

## ③ 验收命令 (★本机实跑, rc 原样贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_onepass_preflight_coverage.py             # rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest  # rc=0 (反向 ≥6 条)
python3 HW/check_board_frame_caliber.py                    # rc=0 (★ISS-274 的闸, 不许被改红★)
python3 HW/check_board_frame_caliber.py --selftest         # rc=0
python3 HW/check_step1_parts_spec.py                       # rc=0 (ISS-237 的闸)
python3 HW/check_part_selection_matrix.py                  # rc=0
python3 HW/check_iss247_f1_landed.py                       # rc=0
python3 HW/check_land_row_anchors.py                       # rc=0 (310/310)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★仍 18 条, 不许变★)
bash state/pcbnew_py.sh state/check_pcb_nets.py            # ★rc=1 (既有状态: 多余 2 焊盘)★
python3 state/check_pcb_drc.py                             # rc=0 (unconnected=45 · DRC=0)
python3 state/merge.py                                     # rc=0
python3 state/gate_check.py                                # rc=0 (Q1 18/18)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv   # 5 件逐字节不变
```

★**基线 md5 (★2026-11-17 07:2x main 实测★)**:
`611b869e13518c3c023fb178f91a0075` (板) · `3e504d2be83152e337949723e909be1b` (`.kicad_pro`) · `e06c1dd633566aa44732762c2ff99d1c` (网表) · `287e7861a0d1007748d92d9fbecdd490` (脚表) · `94642d07a69e8d60dd2af57f69b93607` (BOM)

★**已知现状 (不必修, 但交卷单要写清)**:
- ★`bash state/pcbnew_py.sh state/check_pcb_nets.py` **rc=1** (板多 2 个带网焊盘 = F1 落表引起) ⇒ **既有状态, 本单不负责修**, 但 **P6 要保证本单没让它更糟** ★
- ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` **rc=1** (18 条未落表) ⇒ **既有状态, 本单不许把它变成 0 也不许让它变多** ★
- ★`python3 HW/check_pin_function_labels.py` **rc=1** (15 条 = 14 串号 + 1 缺脚, ★`--expect-known` 才 rc=0★) ⇒ **既有状态 (ISS-239 的已知缺陷), 本单不负责修** ★

---

## ④ 边界 (★逐条自证★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | 板 + `.kicad_pro` md5 跑前跑后逐字节相同 (★**板 md5 只许在「板只改一次」那一趟变一次**★) |
| ★**零落表** ★ | 网表 / 脚表 / BOM md5 逐字节不变 ⇒ ★**并且 18 条未落表一条不许变** ★ |
| ★**零改判据阈值** ★ | `state/check_pcb_drc.py` / `state/check_pcb_nets.py` / `state/compare_arm_official.py` / `HW/check_board_frame_caliber.py` / `HW/check_step1_parts_spec.py` 一字未动 |
| ★**零开新布线臂** ★ | 不跑任何臂脚本 (★`state/` 下那些以 `v` 开头 + `arms` 结尾的臂脚本 (几十个) ★ ⇒ **一个都不许新开** ★) |
| ★**零改 MECH / SW 文件** ★ | `MECH/` 与 `SW/` 零字节写入 (★MECH 侧本轮 ISS-278 在动, 两边各写各的, 只交叉引用★) |
| ★**不许改别人的交卷单** ★ | 只写自己的交卷单 + 作业包追加式订正 ⇒ ★**ISS-239/241/244/247/274/276 的交卷单一个字不许改** ★ |
| ★**零外发** ★ | 不发邮件 / 不询价 / 不问询 / 不采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ ★**查不到就写 `[0数据]` + 降级方案** ★ |
| ★**证据分级** ★ | 每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |
| ★**不替老板拍板** ★ | ★**§5 那几条只列事实与代价** ★ (★`U_LDO_S28.pin3` A/B · 亮度档 G-5 · P7 · `D_ESD_TC` 4 焊盘★) |
| ★**不自签 `state/issue_log.yaml`** ★ | 只走 `state/frag_write.py --agent hw-lead` |
| ★**不改 `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md`** ★ | 只读 |

---

## ⑤ 三条不许搞混的 (★本轮踩出来的★)

1. ★**「清单」≠「第二份过期文档」** ★ ⇒ ★**所以必须有 P5 (现状值必须与盘面实测一致) ⇒ 盘面变了清单不跟 = 当场红** ★ ⇒ ★**只写一份清单不写闸 = 白做** ★
2. ★**「覆盖度」只查清单是自欺** ★ ⇒ ★**所以必须 P4 从【来源交卷单】反向 grep 出板侧项标记 ⇒ 每条都必须在清单里** ★ ⇒ ★**这样「只在交卷单里、没进清单」的漏项才会被抓住** ★
3. ★**「板只改一次」最怕的不是做错, 是漏做** ★ ⇒ ★**漏做一项 ⇒ 板 md5 变第二次 ⇒ 留证链 / Gerber / 投产包 / 盖章全白跑** ★ ⇒ ★**所以本单的价值不在「清单好看」, 在「漏项当场红」** ★
