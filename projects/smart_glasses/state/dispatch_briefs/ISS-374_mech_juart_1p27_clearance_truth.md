# ISS-374 · mech-lead · 「板那一趟」`J_UART` 排针 land 改 1.27mm 的结构侧净距真相（ISS-371 的姊妹件·同一条 `B33` 板侧项）· 纯分析 + 文档订正(追加式) + 新建闸 + 沙盒预演 · 零写板

★★**题**: ★**把 `J_UART` 这颗**和 `J_DEBUG` 同一条板侧项、同一个改动、但【结构侧真相至今是空白】的排针, 补成和 ISS-371 同规格的一页 + 一条闸** ★★

---

## ★★一 背景 (★main 2026-11-23 22:4x~23:0x 本机实读 · **不抄任何 agent 报告** · 每条都可复跑★) ★★

★**ISS-371 (★2026-11-23 22:4x 刚被 main 签收 verified★) 交付了什么**: ★**`J_DEBUG` 这颗 1×4 排针的结构侧净距真相** ⇒ ★一页 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` + ★一条闸 `MECH/check_jdebug_1p27_clearance.py` (★本机 22:5x 实跑 rc=0 · 7/7 全绿★) ★

★★**★但 `J_UART` 那颗 1×2 排针, 在同一个板侧项里, 结构侧【一个字都没有】★★**:

| 项 | `J_DEBUG` (1×4) | ★`J_UART` (1×2) ★ |
|---|---|---|
| ★**在不在那一趟的板侧改动清单里** ★ | ★**在** ★ | ★**在** ★ |
| ★**ISS-371 的真相页覆盖了吗** ★ | ★**覆盖** ★ | ★★**零覆盖** ★ |
| ★**ISS-371 的闸覆盖了吗** ★ | ★**覆盖** ★ | ★★**零覆盖** ★ |

★★**★本机实读证据 (★三条·每条都可复跑★)★★**:

★**① 同一条板侧项同时点了两件** ⇒ ★本机实读 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (★ISS-290 · step S6★) 原文: 「★**`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm** (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」★ ★+ 期望读数「★J_DEBUG land pitch = 1.27 / **J_UART land pitch = 1.27**★」★ ⇒ ★**「换 1.27」这个动作, 板上落两件, 而结构侧真相只做了一件** ★

★**② ISS-371 的真相页里 `J_UART` 出现 0 次** ⇒ ★本机实跑 `grep -c "J_UART" MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ⇒ ★**0** ★ ⇒ ★**不是"提了一句", 是【整颗件没进这一页】★**

★**③ ISS-371 的闸也只认 1×4 那颗** ⇒ ★本机实读 `MECH/check_jdebug_1p27_clearance.py` 的常量: `THT_MOD_NAME = "PinHeader_1x04_P1.27mm_Vertical.kicad_mod"` / `SMD_MOD_NAME = "PinHeader_1x02..."` 附近 ★ ⇒ ★**它连 `J_UART` 这颗件的**存在都不检查 ⇒ 那颗件的 land 改了, 这条闸【不会红】**** ★

★★**★为什么这不是"少写一页"而是"结构件会装不上" (★main 本机实算★)★★**:

★**★本机实读 `J_UART` 的板面现状 (★`bash state/pcbnew_py.sh` · KiCad 10.0.8★)★★**:

```
J_UART  npads 2  libid ''
   pad centers X [18.64, 19.14]  Y [68.6, 68.6]
   pitch 0.5
   pad 1 size 0.275 x 0.9  net UART_TX
   pad 2 size 0.275 x 0.9  net UART_RX
```

★**★⇒ 现状铜箔 X 宽 = 0.7750 mm (★`18.5025..19.2775`★)★★**

★**★本机实读【座体必须清空区】(★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 ★)★★**: ★**UART 检修口: 必须清空区 X `17.620..20.160` (★宽 `2.5400`★) × Y `67.330..69.870`; 开口 X `13.790..23.990` × Y `66.300..70.900`; ★**单边间隙 X 3.830 / Y 1.030 (最坏 3.530 / 0.730 ≥ 0.60)**★ ⇒ ★**这个 `3.830` 是按【现状铜箔 0.7750】算的**★

★★**★★main 本机实算: 换成官方 1×2 THT land 之后会怎样 (★不是抄, 是本机读 `.kicad_mod` + 算★)★★**:

★**官方 land (★本机盘上路径★)**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ ★本机实读: `pad "1" thru_hole rect (at 0 0) size 1 1` · `pad "2" thru_hole circle (at 0 1.27) size 1 1` · `fp_rect -1.55 -1.14 .. 1.55 2.41` ★

★**⇒ 摆成板上 X 向 1×2 直排 (转 90°/270°) 后: 铜箔 X 宽 = 跨距 `1.27` + pad 宽 `1.0` = `2.2700` ★**

★★**⇒ main 本机实算的两条数 (★你要自己重跑并贴你的输出★)★★**:

| 项 | 现状 (0.50 pitch + 0.275 pad) | ★换官方 1×2 THT 之后★ | Δ |
|---|---|---|---|
| 铜箔 X 宽 | `0.7750` | ★**`2.2700`** ★ | ★**+1.4950** ★ |
| ★**对座体必须清空区 X 宽 `2.5400` 的每边余量** ★ | `0.8825` | ★★**`0.1350`** ★★ | ★**−0.7475** ★ |
| ★**判据 `CRIT`** ★ | — | ★**`0.60`** (★`MECH/service_port_check.py` L127 `CRIT = 2 * TOL["fdm_part"]`★) ★ | — |

★★**⇒ ★★main 本机实算的读数: 每边余量 `0.1350` ⇒ 【远低于 `CRIT` 0.60】⇒ ★★`J_UART` 换官方 THT land 之后, 铜箔会【进座体必须清空区】(★每边越界 `0.4650`★)⇒ ★★这和 `J_DEBUG` 的结论【方向相反】(★`J_DEBUG` 那颗: 方向仍过 `CRIT`, 余量 3.99×★)⇒ ★★`J_UART` 这颗是【另一颗性质不同的件】, 不能拿 `J_DEBUG` 的结论套过去** ★★ ⇒ ★★**那一趟若照 `B33` 把 `J_UART` 也换成官方 land ⇒ 结构件装不上 ⇒ 要么改结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑** ★★

★**★⇒ 这就是本单的题: ★**`J_UART` 这颗件的结构侧真相至今是【空白】, 而它按官方 land 算出来的方向【和它的姊妹件相反】⇒ 必须现在算清、写成一页、做成一条闸, 别等那一趟开工当天才发现** ★★

---

## ★★二 你这一单要交的东西 (★三件 + 交卷页 + 分片★) ★★

### ★★① ★**新建★ 一页 `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (★本单产出物★) ★★

★**必须含 (★每个数字带复跑命令★)**:

1. ★**§0 口径与读数**: ★**`J_UART` 与 `J_DEBUG` 并排对照表** (★颗数 / 现状 land pitch / 现状 pad 尺寸 / 现状铜箔 X 宽 / 官方 land 封装真值 / 官方 THT 铜箔 X 宽 / 座体必须清空区 X 宽 / 每边余量 / `CRIT` / 方向结论★) ⇒ ★**★两件必须并排摆在一起, 让"两件方向相反"这件事一眼看得见★★**
2. ★**§1 官方 1×2 THT land 实读** (★读盘上 `.kicad_mod`, 不许抄文档★): ★**封装真值 + 两个 pad 的 shape/size/坐标 + fab `fp_rect` + 环宽 `[0数据]` 记清★** ⇒ ★**`J_UART` 的 SMD 降级变体也要单列实测** (★`PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` / `_SMD_Pin1Right.kicad.mod` ⇒ ★这两个也在盘上, 各自几何不同★ ⇒ 不许拿 THT 的数套用★)
3. ★**§2 量差表**: ★**现状 / 官方 THT / 官方 SMD 变体 三档 × 每一项** (★铜箔 X 宽 · 铜箔 Y 宽 · 每边余量 · 最坏余量(★`TOL["fdm_part"]` = 0.30★) · fab 外框 · 判据 `CRIT` · 过/不过★) ★
4. ★**§3 两个后果**:
   - ★**后果句**: ★**若那一趟按 `B33` 把 `J_UART` 也换成官方 land ⇒ 每边余量 0.1350 < CRIT 0.60 ⇒ 铜箔进座体必须清空区 ⇒ 结构件装不上** ★
   - ★**判据句**: ★**方向本身仍可救** ⇒ ★**给降级方案 + 代价** (★★候选你自己查: ① 座体必须清空区 X 宽从 2.5400 放宽到 ≥ `2.2700 + 2×0.60 = 3.4700` (★那要动结构件 ⇒ 归 mech-lead 的结构侧页 + 老板口径★) ② 换 SMD 变体 (★几何另算★) ③ `J_UART` 这颗改选型/改座体 ④ 降级: `J_UART` 这颗【那一趟不换 land】(★但那要动 `B33` ⇒ 归 main★) ⇒ ★**每条给代价, 不许代拍★**)
   - ★**★★两句必须分开写, 不许混成一句 "OK / 合格" ★★★** (★这是 ISS-371 立下的口径纪律, 你继承★)
5. ★**§4 未决项**: ★只登记不代拍★ ⇒ ★**逐条写清「要谁回答什么」★** ⇒ ★**至少要含: ★**① 座体必须清空区要不要放宽到 3.4700 (★结构件 + 老板口径★) ② 那一趟 `J_UART` 换不换 land (★归 main·★与 ISS-373 同一件事的两条腿, 你只给结构侧代价, 不代 main 裁★) ③ 座体真实型号仍未定 (★`ISS-267 F-8` · `[0数据]`·★开口 Y 的一切数等真实型号定版后重算★)****
6. ★**§5 复跑命令** + ★**§6 边界自证**

★**★与 ISS-371 的关系 (★不许重复发明·也不许改它的地界★)★★**:
★**`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 `MECH/check_jdebug_1p27_clearance.py` 是 ISS-371 的交付物 ★★你一个字都不许改★ ★(★它们已被 main 签收 verified·★改已签收件 = 破坏留证链★)★★ ⇒ ★**你要么【新建 `J_UART` 自己的一页一闸】, 要么【在你自己那一页里追加式引用 `J_DEBUG` 的数】⇒ 但【不许改 ISS-371 那两件】★**

### ★★② ★**新建★ 一条闸 `MECH/check_juart_1p27_clearance.py` (★本单产出物★) ★★

★**判据 (★至少 J0~J8 · 每条 fail-closed · 每条带反向用例★)**:

| # | 判据 | ★**不许写死的**★ |
|---|---|---|
| J0 | ★**官方 1×2 THT land 几何必须与盘上 `.kicad_mod` 实读一致** (★自己解析·不许写死 `2.2700`★) ★ | ★不许把 2.2700 写死成常量 ★ |
| J1 | ★**§2 三档量差表逐格与 J0 实算一致** (★现状 / THT / SMD 变体★) ★ | ★不许拿 THT 的数套 SMD 变体★ |
| J2 | ★**座体必须清空区 X 宽必须 ≥ 铜箔 X 宽 (不许越界)** + ★**越界事实必须被显式记账** ★ | ★`CRIT` 从 `MECH/service_port_check.py` 取, 不许写死★ |
| J3 | ★**每边余量对称且 ≥ `CRIT`** (★从真身取 `CRIT`·不许写死★) + ★**最坏余量 (FDM ±0.30) 也要判** ★ | |
| J4 | ★**SMD 降级变体几何独立实测并单列** (★`Pin1Left` 与 `Pin1Right` 两个变体各自算★) ★ | |
| J5 | ★**`J_DEBUG` / `J_UART` 两件方向结论必须并排出现在页里** ⇒ ★**只写一颗 ⇒ 红** (★★防"拿一颗的结论套另一颗"★★) ★ | |
| J6 | ★**板面零写板自证** (★md5 / mtime / size 三项 == `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ | |
| J7 | ★**证据等级五级白名单** + ★**零挂起措辞** + ★**判据句/事实句分开** + ★**`.kicad_mod` md5 台账** ★ | |
| J8 | ★**零挂链** ⇒ ★**自证: `grep -c check_juart_1p27_clearance state/gate_check.py` == 0** ★ | ★**挂不挂归 main★ ★ |

★**★必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」★)★★**
★**★其中至少 2 条反向用例必须针对 ISS-371 那个病根 (★"拿一颗件的结论套另一颗"★)★★**:
★**① 把 `J_UART` 那一页删掉/改名 ⇒ J5 红、其余仍绿 ② 把 `J_UART` 的 THT 铜箔宽改成 `J_DEBUG` 的 `4.8100` ⇒ J1/J2 红 (★证明闸真在读 `J_UART` 自己的数, 不是抄 `J_DEBUG` 的★)★**

### ★★③ 沙盒预演 (★只落 `tmp/iss374_sbx/` + `logs/iss374/`★) ★★

★**用 `bash state/pcbnew_py.sh` (★本机 KiCad 10.0.8★) 在【板副本】上做, 真板零改动★**:

| 轮次 | 板副本 | ★**要报的数** ★ |
|---|---|---|
| ★**S0** ★ | 不换 (★基线★) | ★`J_UART` 实测: land pitch / pad 尺寸 / 铜箔 X 宽 / fab 外框 / 净名 (★`UART_TX`/`UART_RX`★)★ |
| ★**S1** ★ | ★**`J_UART` 换官方 1×2 THT land** (★`PinHeader_1x02_P1.27mm_Vertical.kicad_mod`★) | ★**换完实测 land pitch (期望 1.27) / 铜箔 X 宽 / fab 外框** + ★**与座体必须清空区 `17.620..20.160` 的每边余量** ★ |
| ★**S2** ★ | ★**`J_UART` 换官方 1×2 SMD 变体** (★`Pin1Left`★) | ★同上 + ★**两件净名是否保住** (★pad↔net 按焊盘号继承·★不许替老板做 pad 序对调★) ★ |
| ★**S3** ★ | ★**反向对照: `J_DEBUG` 也换一次** | ★**证明两颗件的方向结论确实不同 (★`J_DEBUG` 过 / `J_UART` 不过·★若你算出一样 ⇒ 说明你算错了, 停下查★)** ★ |

★**★S3 那一轮是本单的自检轮: ★**如果你算出来 `J_UART` 也过 `CRIT`, 那就说明你的算法和 ISS-371 不一致 ⇒ ★**停下报告, 不许硬写一个 "过" 的结论** ★★**

★**★沙盒纪律 (★一条不许破★)★★**: ★**副本只落 `tmp/iss374_sbx/`** · ★**不许写真板** (★板 md5 开工前/交卷后各打一次★) · ★**不许跑会重铸随机 UUID 的门禁去"验"板** (★`state/check_sch_pinfull.py` / `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 重铸 UUID ⇒ 任何 md5 比对都失效 ⇒ **板 md5 只能在你自己的脚本前后打, 不能跑完门禁再打**★) ★

---

## ★★三 边界 (★一条不许越★) ★★

★**零写板** (★真板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 一律只读★) ★
★**零改既有闸** (★`MECH/check_jdebug_1p27_clearance.py` (★ISS-371 已签收件★) · `MECH/check_onepass_s10_fp_swap_impact.py` · `MECH/check_onepass_s10_led_spec_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_board_frame_coords.py` · `MECH/service_port_check.py` · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** (★`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) · `MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动** ★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/mech.yaml`** (★**只走 `state/frag_write.py`** ★· 写前写后各记一次 md5 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」· 不许静默覆盖★) ★
★**沙盒只落 `tmp/iss374_sbx/` + `logs/iss374/`** ★
★**不代老板拍板** · **不代 main 拍** (★「那一趟 `J_UART` 换不换 land」是 main 的裁决权 ⇒ 你只给结构侧代价与判据★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查资料** · **不许发任何邮件/询价/问询** · **不许写「等原厂回信」** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案★) ★
★**不自签 `state/issue_log.yaml`** (★台账由 main 签收★) ★
★**零推 GitHub** (★由独立的 5 小时同步 job 负责★) ★

---

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

python3 MECH/check_juart_1p27_clearance.py                    # 新闸 ⇒ rc=0
python3 MECH/check_juart_1p27_clearance.py --selftest          # 新闸自测 ⇒ rc=0 (末行 ALL TESTS PASS)
python3 MECH/check_jdebug_1p27_clearance.py                    # ★ISS-371 那条闸必须仍然 rc=0 (零漂移自证)★
python3 MECH/check_onepass_s10_fp_swap_impact.py               # rc=0
python3 MECH/check_onepass_s10_led_spec_sync.py                # rc=0
python3 state/merge.py                                         # rc=0
python3 state/gate_check.py                                    # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                          # rc=0
grep -c check_juart_1p27_clearance state/gate_check.py         # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                         # ⇒ 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                # ⇒ 2026-11-06 07:07:17.362193413 4940213
```

★**交卷页**: `HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「要 main 裁的事」逐条 (★要谁回答什么★)★**

★**★收工后回卷 (★按老规矩★)★★**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★**

---

## ★★五 你必须自己复算、**不许抄**的数 (★main 已算过一遍, 但你要自己重跑并贴你的输出★) ★★

1. ★**`J_UART` 现状**: land pitch `0.5` · pad `0.275 × 0.900` · ★**铜箔 X `18.5025..19.2775` (宽 `0.7750`)**★ · fab `6.000 × 4.000` · net `UART_TX`/`UART_RX` ★
2. ★**官方 1×2 THT land 实读**: `PadHeader_1x02...` ⇒ ★**pad1 `thru_hole rect` (at 0 0) size 1 1** · ★**pad2 `thru_hole circle` (at 0 1.27) size 1 1** · fab `fp_rect -1.55 -1.14 .. 1.55 2.41` ★ ⇒ ★**摆成板上 X 向 1×2 后铜箔 X 宽 = 1.27 + 1.0 = `2.2700`** ★
3. ★**座体必须清空区 X `17.620..20.160` (宽 `2.5400`)** ⇒ ★**每边余量 = (2.5400 − 2.2700) / 2 = `0.1350`** ⇒ ★**`CRIT` = `0.60` ⇒ 差 `0.4650`** ★
4. ★**现状每边余量 = (2.5400 − 0.7750) / 2 = `0.8825`** ⇒ ★**Δ = `−0.7475`** ★
5. ★**S3 反向对照**: `J_DEBUG` 换官方 1×4 THT 后 ★**过** (★余量 `2.6950` · 3.99×·★ISS-371 已算·你要自己复算一遍★)★ vs `J_UART` 换官方 1×2 THT 后 ★**不过** ⇒ ★**两件方向相反** ★

★**★主命令 (★本机实测存在, 你自己再验一遍★)★★**:

```bash
# 板面读数 (★本机 KiCad 10.0.8★)
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s pitch=%.4f libid=%r'%(r,(lambda c:c[1]-c[0])(sorted(set(round(pcbnew.ToMM(p.GetPosition().x),4) for p in [f for f in b.GetFootprints() if f.GetReference()==r][0].Pads()))),[f for f in b.GetFootprints() if f.GetReference()==r][0].GetFPIDAsString()) for r in ('J_DEBUG','J_UART')))"

# 官方 land 实读 (★读盘上 .kicad_mod, 不抄文档★)
grep -nE '\(pad |drill|fp_rect|\(at ' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod

# CRIT 真身 (★不许写死★)
grep -nE 'CRIT|TOL\["fdm_part"\]' MECH/service_port_check.py

# 座体必须清空区 + 开口 (★本机实读★)
grep -nE '17\.620|20\.160|2\.54|座体' MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md

# 板侧项 (★证明 J_DEBUG 与 J_UART 在同一条项里★)
grep -nE 'B33_PIN_LAND_1P27|J_DEBUG.*J_UART' HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
```

★**★最后一句纪律 (★main 2026-11-23 23:0x 追加★)★★**: ★**ISS-371 证明了一件事: ★**「同一个板侧项里的两颗件, 结构侧结论可以【完全相反】**★ ⇒ ★**⇒ 你这一单的价值不在于多一页文档, 而在于【让「`J_UART` 这颗件的每边余量 0.1350 < CRIT 0.60」这条事实, 在那一趟开工之前就变成机器判据, 而不是等结构件装不上才发现** ★★ ⇒ ★★**并且: 你算出来的数如果和我上面给的不一样, 【以你本机复算的为准】, 但你必须在交卷页里写清差在哪、为什么差** ★★ ★
