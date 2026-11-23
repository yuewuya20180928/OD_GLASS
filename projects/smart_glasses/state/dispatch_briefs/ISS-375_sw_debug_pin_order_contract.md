# ISS-375 · sw-lead · 「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的**物理针序契约**（pin1 朝向 / JTAG 线序）· 纯分析 + 文档 + 新建闸 + 沙盒预演 · 零写板

★★**题**: ★**把「那一趟把 `J_DEBUG` 换官方 land 时, pin1 到底朝哪边 / JTAG 四线物理线序是什么」这条【没有任何页面记录】的空白, 收成【一份可查的物理针序契约 + 一条机器闸】** ★★

---

## ★★一 背景 (★main 2026-11-23 22:4x~23:1x 本机实读 + 本机实算 · **不抄任何 agent 报告** · 每条都可复跑★) ★★

★**主线背景**: ★**「板只改一次」那一趟 = 板 md5 只许变 1 次** ⇒ ★**「那一趟要做的每一个决定, 都必须在开工前写死** ★★ ⇒ ★**这一条【现在还没写死】** ★

★★**★ISS-371 (★2026-11-23 22:4x 刚被 main 签收 verified★) 自己已经点到这条, 但只点到一半 ★★**:

★本机实读 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §5.1 (★未决项表第 1 行★) 原文:

> ★**① 居中解 rot 90° ⇒ 原点 (141.0450, 56.6000) ; ② 居中解 rot 270° ⇒ 原点 (144.8550, 56.6000)** ★ · ★**两条都过 `CRIT` ; 但 ① 与 ② 的 pin1 朝向相反 (JTAG 线序要跟 hw-lead 对齐)** ★ · 且两条都要求原点从 (144.30, 58.00) 挪掉 ⇒ **板那一趟必须写死** ★ · ★归 **main → hw-lead** ★

★**★⇒ 也就是说: ★**「两条落点几何上都过, 但 pin1 朝向相反」这个事实已经被写下来了, 而且那一行自己写着「板那一趟必须写死」⇒ ★**可是全项目【没有任何一处】记录了「pin1 朝向」到底该取哪一条、以及为什么★** ★★

★★**★main 本机实算 (★为什么这不是措辞问题, 是「两个都合法但只能选一个」的问题★)★★**:

★**★① 官方 land 的 pin1 有形状标记 ★** ⇒ ★本机实读 `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ ★**pad "1" = `thru_hole rect` (★方形 = 行业标准的 pin1 标记★) · pad "2"/"3"/"4" = `thru_hole circle`** ★ ⇒ ★**官方件自带 pin1 极性标记 ⇒ 「哪端是 pin1」是【实物可见的】, 选错 ⇒ 排线插反 ⇒ JTAG 救砖链直接不通** ★

★**★② 现状板面【完全没有 pin1 极性标记】★** ⇒ ★本机实跑 `bash state/pcbnew_py.sh` 读板: ★**`J_DEBUG` 4 个 pad 全是 `shape=1` (RECT) / 全 SMD / 全 0.275×0.900** ⇒ ★**四个长得一模一样 ⇒ 现状【没有】pin1 标记 ⇒ 「pin1 在哪」这件事今天是【靠网表约定】, 不是靠实物** ★ ⇒ ★**⇒ 换官方 land 之后, 板面【第一次】出现 pin1 方形标记 ⇒ 那一刻「哪端是 pin1」就从约定变成了实物事实 ⇒ 选错就是实物插反** ★

★**★③ 两个候选落点的 pin1 朝向【相反】—— main 本机实跑 pcbnew 验过 ★★** ⇒ ★★**不是手算, 是用 KiCad 自己的 FOOTPRINT 变换在真 board 上验的★**:

```bash
# ★main 2026-11-23 23:0x 本机实跑 (★KiCad 10.0.8·真板只读·不写盘★)
bash state/pcbnew_py.sh -c "
import pcbnew
b = pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb')
f = [x for x in b.GetFootprints() if x.GetReference()=='J_DEBUG'][0]
for rot in (0, 90, 270):
    f.SetOrientationDegrees(rot)
    out = sorted([(p.GetPadName(), p.GetNetname(), round(pcbnew.ToMM(p.GetPosition().x),4)) for p in f.Pads()], key=lambda t: t[2])
    print('rot', rot, out)
"
```

★**★实测输出 (★main 23:0x 原样·你可自己重跑核★)★★**:

```
rot   0 -> [('1','JTAG_TCK',142.2), ('2','JTAG_TMS',142.7), ('3','JTAG_TDI',143.2), ('4','JTAG_TDO',143.7)]
rot  90 -> pad abs X 全部 = 142.9      ← ★四个 pad 挤到同一 X ⇒ 排针【变成竖排】★
rot 270 -> pad abs X 全部 = 145.7      ← ★同上★
```

★**★⇒ main 23:0x 再用官方 land 的局部坐标 (pad1=(0,0) · pad2=(0,1.27) · pad3=(0,2.54) · pad4=(0,3.81)·★轴向 = 局部 Y★) 复算★**: ★**rot 90 ⇒ 局部 +Y 映射到板 +X ⇒ pad1 在【X 最小端】· pad4 在【X 最大端】· ★**顺排 (TCK→TDO 从小到大)★**; rot 270 ⇒ 局部 +Y 映射到板 −X ⇒ **pad1 在【X 最大端】· ★**逆排 (TDO→TCK 从小到大)★** ★★

★**★⇒ 结论 (★main 的话★): ★**两个候选落点【几何完全对称、都过所有判据】, 但物理上是【镜像的两个排针】⇒ ★**「pin1 朝向」这件事【必须选一条】, 而全项目没写 ⇒ 那一趟开工时谁都可以随手挑一个 ⇒ 挑错 ⇒ 实物排线插反 ⇒ JTAG 救砖链不通 ⇒ ★**这块板就再也没有 S3 级救砖路径了 (★`SW/FLASH_AND_VERSION.md` 的 4 级救砖里 S3 = JTAG 是【除返厂换板外】唯一的软救砖路径★)** ★★

★**★④ 而且这条链现在【本来就是断的】—— 这是更狠的一半 ★★** ⇒ ★本机实读 `HW/netlist_v1_pins.csv` 第 202-205 行 + `HW/netlist_v1.csv` 第 388-395 行:

| 板侧排针脚 | 网 | 网表另一端 | ★**另一端是什么**★ |
|---|---|---|---|
| `J_DEBUG.pin1` | `JTAG_TCK` | `R_JTAG_TCK` | `JTAG_TCK_SOC` ⇒ ★**`SoC_NC`** ★ |
| `J_DEBUG.pin2` | `JTAG_TMS` | `R_JTAG_TMS` | ⇒ ★**`SoC_NC`** ★ |
| `J_DEBUG.pin3` | `JTAG_TDI` | `R_JTAG_TDI` | ⇒ ★**`SoC_NC`** ★ |
| `J_DEBUG.pin4` | `JTAG_TDO` | `R_JTAG_TDO` | ⇒ ★**`SoC_NC`** ★ |

★**⇒ `JTAG_*_SOC` 四条网的 SoM 侧端点【全部是 `SoC_NC`】(★`HW/netlist_v1.csv` 实读: `SoC_NC` 出现在 11 行, 四条 JTAG_*_SOC 全在其中★) ⇒ ★★**JTAG 链在 SoM 那一头【没落到任何 SoM 引脚上】★★** ⇒ ★★**而 `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行对四条 JTAG 信号的结论是: 「逐针表里没有同名/后缀相同的信号 ⇒ 要么是 RK3572 内部命名不同, 要么该信号在 FET3576-C 上不存在」⇒ `[实测]` 依据在 `HW/PCB/FET3572C_PIN_TABLE.csv` 的 399 行官方脚表★ ⇒ ★★**`JTAG_TDI` 在 SoM 侧【根本没有对应引脚】** ★★ ⇒ ★★**⇒ 这一条【与 ISS-338 的 JTAG 分组裁决直接冲突】**: ★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁把 `JTAG_TDI` 判为「★**必需**★ (★进 S8 布线目标 · ★**板侧不许标 NC / no-connect**★)」, ★**而网表侧它此刻就是 `SoC_NC`★ ★★

★★**⇒ 本单的题 (★三件事一件不许少★)★★**:

1. ★**把「pin1 朝向」写成一条【可查、可机器判的物理针序契约】** (★含官方 land 的方形 pad-1 标记 / 两个候选落点的镜像关系 / 选哪一条 + 为什么 / 那一趟的写死位置★) ⇒ ★**这是 hw-lead 落点裁决的【前置输入】, 也是装配与救砖的唯一依据** ★
2. ★**把「JTAG 链在 SoM 侧到底通不通」查清并落成机器判据** ⇒ ★**四线 `SoC_NC` + 脚表 399 行里没有 JTAG 同名信号 ⇒ 这条【救砖路径今天就是断的】⇒ 那一趟改 pin1 朝向【救不了它】⇒ 必须让这件事在【开工前】被看见, 而不是等板做完才发现** ★
3. ★**把这条与 ISS-338/ISS-344 裁决的关系说清 (★只登记 + 给代价, 不代拍 ★)** ⇒ ★**「`JTAG_TDI` 判为必需 且 板侧不许标 NC」这条裁决, 与「网表里它此刻就是 `SoC_NC`」这条事实, 【对不上】⇒ ★**谁对谁错、怎么改、要改哪一处 (网表 / 裁决 / 脚表映射), 代价多大 ⇒ 你算清并列出, 交 main 裁** ★★

---

## ★★二 你这一单要交的东西 (★三件 + 交卷页 + 分片★) ★★

### ★★① ★**新建★ 一页 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (★本单产出物★) ★★

★**必须含 (★每个数字带复跑命令★)**:

1. ★**§0 一句话结论 + 三问回答** (★仿 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §0 体例★)
2. ★**§1 物理针序契约表** (★核心交付物★): ★**逐件**给 `J_DEBUG` (1×4) 与 `J_UART` (1×2) 各一行 ★
   - 现状板面 pad1 在哪 (★X 最小端还是最大端★) + 现状有没有极性标记 (★实测: 全 RECT 无标记★)
   - 官方 land 的 pin1 标记形状 (★实测: `thru_hole rect` vs 其余 `circle`★)
   - ★**两个候选落点 (rot 90 / rot 270) 各自 pin1 在哪 + 四线物理线序 (顺排/逆排) + 各自要挪原点多少** ★
   - ★**★裁决建议 (★带代价·不代拍★): 选 rot 90 还是 rot 270, 以及为什么 (★判据: ① 现状是顺排 (TCK 在 X 最小端) ⇒ 换 land 后【尽量保持顺排】⇒ rot 90 ② 但若 fp 库命名/装配惯例要求 pin1 在 X 最大端 ⇒ rot 270 ③ 两条的净距/几何【完全等价】⇒ 选哪条都不影响结构 ⇒ **所以这不是结构问题, 是「装配与救砖的线序契约」问题** ⇒ 归 main 裁** ★)**
   - ★**落点写死值 (★那一趟要用的★): 原点坐标 + 旋转角 + pin1 在哪一端** ★
3. ★**§2 JTAG 链的 SoM 侧真相**: ★**四线 `SoC_NC` 的逐条实读 (★网表行号 + 脚表 399 行依据★) + `SOM_PIN_MAPPING.md` 第 48-51 行的原话 + `FET3572C_PIN_TABLE.csv` 的实读结论 ⇒ ★**「JTAG 链在 SoM 侧不落地」这条事实怎么表述才不夸大 (★是「SoM 侧未连」还是「信号在该模块上不存在」★—— ★**这两句差别很大, 你要按脚表实读判, 不许混着写**)★**
4. ★**§3 与既有裁决的关系 (★只登记 + 给代价·不代拍★)**: ★**`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁 vs 网表现状 ⇒ 三条路的代价 (★① 改裁决口径 (JTAG_TDI 降级为「悬空候选」·与脚表一致) ② 改网表 (`SoC_NC` → 某个真 SoM 脚·★但脚表里没有 JTAG 同名信号 ⇒ 这条路当前【走不通】★ ⇒ 代价 = 要先定 SoM 侧的 JTAG 引出方案) ③ 改 SoM 选型/换板 (JTAG 不引出 ⇒ 放弃 S3 救砖路径·只剩 S4 返厂)★ ⇒ ★**每条给「要谁回答什么」★)**
5. ★**§4 证据等级 + 边界自证** (★板指纹三项未动 + 既有闸/既有页面 md5 未动 + 零写板 + 零落表 + 零外发★)

### ★★② ★**新建★ 一条闸 `SW/tools/check_debug_pin_order_contract.py` (★本单产出物★) ★★

★**判据 (★至少 D0~D8 · 每条 fail-closed · 每条带反向用例★)**:

| # | 判据 | ★**不许写死的**★ |
|---|---|---|
| D0 | ★**官方 land 的 pad1 形状必须与盘上 `.kicad_mod` 实读一致** (★自己解析·不许写死「pad1 是 rect」★) ⇒ ★**rect 标记是行业标准的 pin1 标记 ⇒ 这条不许放过** ★ | ★不许把 pad1 形状写死成常量 ★ |
| D1 | ★**现状板面 `J_DEBUG`/`J_UART` 的 pad1 位置 (X 最小端/最大端) 由脚本实读板得出** ⇒ ★**不许写死「现状是顺排」★** ★ | |
| D2 | ★**两个候选落点的 pad→X 序必须由脚本用 KiCad 自己的变换算出来** (★`bash state/pcbnew_py.sh` + `FOOTPRINT.SetOrientationDegrees` ⇒ ★**不许手算旋转矩阵**) ★⇒ ★**算出的两个序必须【互为逆序】, 不是互等 ⇒ 否则红** ★ | ★不许手算旋转★ |
| D3 | ★**页 §1 的针序契约表必须同时给出两个候选 + 裁决 + 落点写死值** ⇒ ★**只给一个候选 ⇒ 红** (★防"只写了一种就当定案"★) ★ | |
| D4 | ★**页里写的 pad1 朝向必须与 D2 算出来的一致** ⇒ ★**不一致 ⇒ 红** (★防页与闸各说各话★) ★ | |
| D5 | ★**网表侧 JTAG 四线的 SoM 侧端点必须实读** ⇒ ★**页里写的 `SoC_NC` 结论必须与网表实读逐条相等** ⇒ ★**网表变了而页没改 ⇒ 红** ★ | ★不许把 `SoC_NC` 写死成常量 ★ |
| D6 | ★**`HW/PCB/SOM_PIN_MAPPING.md` 里 JTAG 四行的结论必须与页 §2 的表述不冲突** (★不许页里说「不落地」而映射页说「已落地」★) ★ | |
| D7 | ★**板面零写板自证** (★md5 / mtime / size 三项 == `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ | |
| D8 | ★**证据等级五级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链** (★自证: `grep -c check_debug_pin_order_contract state/gate_check.py` == 0★) ★ | ★挂不挂归 main★ |

★**★必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」★)★**
★**★其中至少 3 条反向用例必须针对「镜像」这个本单核心 (★防"两个候选被当同一个"★)★★**:
★**① 把页里的 rot 90 改成 rot 270 ⇒ D3/D4 红 ② 把 D2 的算式改成手算常数 ⇒ D2 红 ③ 把网表里的 `SoC_NC` 改成别的 ⇒ D5 红 ★**

### ★★③ 沙盒预演 (★只落 `tmp/iss375_sbx/` + `logs/iss375/`★) ★★

★**用 `bash state/pcbnew_py.sh` (★本机 KiCad 10.0.8★) 在【板副本】上做, 真板零改动★**:

| 轮次 | 板副本 | ★**要报的数** ★ |
|---|---|---|
| ★**S0** ★ | 不换 (★基线★) | ★`J_DEBUG`/`J_UART` 实测: pad 数 / 逐 pad X / 逐 pad 形状 / 逐 pad net / 有无 pin1 极性标记 ★ |
| ★**S1** ★ | ★**`J_DEBUG` 换官方 1×4 THT land · rot 90 @ (141.0450, 56.6000)** ★ | ★**换完实测**: 逐 pad 绝对 X + 逐 pad 形状 (★pad1 是不是 rect★) + 逐 pad net (★TCK/TMS/TDI/TDO 各落在哪端★) + 铜箔 X 宽 + fab 外框 + ★**pad→X 序与 S0 是否同向** ★ |
| ★**S2** ★ | ★**`J_DEBUG` 换官方 1×4 THT land · rot 270 @ (144.8550, 56.6000)** ★ | ★同上 ★★**并与 S1 逐项对照: 几何是否完全等价 (铜箔/fab/间隙) + 针序是否【互为逆序】** ★★ |
| ★**S3** ★ | ★**`J_UART` 换官方 1×2 THT land** (★两个朝向各一次★) | ★同上 (★2 脚: pad1 = UART_TX / pad2 = UART_RX · 官方 1×2 land 的 pad1 也是 `thru_hole rect`★) ★ |

★**★S1↔S2 的对照是本单最有价值的产出 ★★** ⇒ ★**你要把「几何完全等价」与「针序互为逆序」这两件事【分别】用数证明, 而不是笼统一句「差不多」** ★

★**★沙盒纪律 (★一条不许破★)★★**: ★**副本只落 `tmp/iss375_sbx/`** · ★**不许写真板** (★板 md5 开工前/交卷后各打一次★) · ★**不许跑会重铸随机 UUID 的门禁去"验"板** (★`state/check_sch_pinfull.py` / `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 重铸 UUID ⇒ 任何 md5 比对都失效 ⇒ **板 md5 只能在你自己的脚本前后打, 不能跑完门禁再打**★) ★

---

## ★★三 边界 (★一条不许越★) ★★

★**零写板** (★真板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 一律只读★) ★
★**零改既有闸** (★`SW/tools/timing_check.py` · `SW/tools/check_onepass_sw_release.py` · `SW/tools/check_fp_truth_read.py` · `SW/tools/check_sw_zero_copper_grade_consistency.py` · `HW/check_pcb_nets.py` · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** (★`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (★含 ISS-344 终裁块★) · `SW/FLASH_AND_VERSION.md` · `SW/SW_MD5_BASELINE_LEDGER.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) · `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` · `HW/PCB/SOM_PIN_MAPPING.md` · `HW/PCB/FP_TRUTH_BASELINE.md` —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动** ★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §3/§4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/sw.yaml`** (★**只走 `state/frag_write.py`** ★· 写前写后各记一次 md5 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」· 不许静默覆盖★) ★
★**沙盒只落 `tmp/iss375_sbx/` + `logs/iss375/`** ★
★**不代老板拍板** · **不代 main 拍** (★「pin1 朝向选哪条」与「JTAG 分组裁决怎么改」都是 main 的裁决权 ⇒ 你只给两条路的代价与机器判据★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查资料** · **不许发任何邮件/询价/问询** · **不许写「等原厂回信」** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案★) ★
★**不自签 `state/issue_log.yaml`** (★台账由 main 签收★) ★
★**零推 GitHub** (★由独立的 5 小时同步 job 负责★) ★

---

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

python3 SW/tools/check_debug_pin_order_contract.py               # 新闸 ⇒ rc=0
python3 SW/tools/check_debug_pin_order_contract.py --selftest     # 新闸自测 ⇒ rc=0 (末行 ALL TESTS PASS)
python3 SW/tools/timing_check.py                                  # rc=0 (★既有闸必须仍绿·零漂移自证★)
python3 SW/tools/check_sw_zero_copper_grade_consistency.py        # rc=0 (★既有闸必须仍绿★)
python3 state/merge.py                                            # rc=0
python3 state/gate_check.py                                       # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                             # rc=0
grep -c check_debug_pin_order_contract state/gate_check.py        # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                            # ⇒ 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                   # ⇒ 2026-11-06 07:07:17.362193413 4940213
```

★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「要 main 裁的事」逐条 (★要谁回答什么★), 其中第 1 条必须是「那一趟 `J_DEBUG` 的 pin1 朝向选 rot 90 还是 rot 270」★**

★**★收工后回卷 (★按老规矩★)★★**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★**

---

## ★★五 你必须自己复算、**不许抄**的数 (★main 已算过一遍, 但你要自己重跑并贴你的输出★) ★★

1. ★**现状 `J_DEBUG`/`J_UART` 逐 pad 的 X / 形状 / 属性 (SMD 还是 THT) / net** (★`bash state/pcbnew_py.sh` 实读板★)
2. ★**官方 1×4 与 1×2 land 的 pad1 形状** (★`thru_hole rect` vs 其余 `circle` ★· 读盘上 `.kicad_mod`★)
3. ★**两个候选落点下, 四个 pad 的绝对 X 序** (★用 KiCad 自己的 `FOOTPRINT.SetOrientationDegrees` + `SetPosition` 在真 board 上算 ⇒ ★**不许手算旋转矩阵★**) ★⇒ ★**两序必须互为逆序** ★
4. ★**S1↔S2 的几何等价性**: 铜箔 X 宽 / fab 外框 / 单边间隙 —— ★**三个数在两个候选下必须逐字相同** (★**这才是「几何等价 ⇒ 纯针序问题」的证明**) ★
5. ★**网表侧 JTAG 四线的 SoM 侧端点** (★`HW/netlist_v1.csv` 第 388/390/392/394 行逐条实读★) ⇒ ★**四行是不是都指向 `SoC_NC`★**
6. ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 里有没有 JTAG 同名信号** (★399 行官方脚表实读★) ⇒ ★**没有 ⇒ `SOM_PIN_MAPPING.md` 第 48-51 行的结论成立** ★

★**★主命令 (★本机实测存在, 你自己再验一遍★)★★**:

```bash
# 板面逐 pad 实读 (★本机 KiCad 10.0.8★)
bash state/pcbnew_py.sh -c "
import pcbnew
b = pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb')
for r in ('J_DEBUG','J_UART'):
    f=[x for x in b.GetFootprints() if x.GetReference()==r][0]
    print(r)
    for p in sorted(f.Pads(), key=lambda p: pcbnew.ToMM(p.GetPosition().x)):
        print('   pad',p.GetPadName(),'X=%.4f'%pcbnew.ToMM(p.GetPosition().x),'shape',p.GetShape(),'net',p.GetNetname())
"

# 官方 land 的 pad1 形状 (★读盘上 .kicad_mod, 不抄文档★)
grep -nE '\(pad "|thru_hole|smd |\(at ' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod | head -20

# 网表侧 JTAG 四线 (★本机实读★)
sed -n '388,395p' HW/netlist_v1.csv

# 脚表 399 行里有没有 JTAG (★官方脚表实读★)
grep -icE "JTAG" HW/PCB/FET3572C_PIN_TABLE.csv

# 已有的裁决 (★读, 不改★)
grep -nE "JTAG_TDI|必需|可悬空" SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | head -8

# 现有未决项 (★ISS-371 §5.1 已点到但没写死★)
grep -nE "5\.1|pin1 朝向" MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md | head -5
```

★**★最后一句纪律 (★main 2026-11-23 23:1x 追加★)★★**: ★**ISS-371 已经把「两个落点几何都过、但 pin1 朝向相反」写下来了, 却把它归给了 main→hw-lead 而【没有写死】⇒ ★**⇒ 你这一单的价值不在于多一页文档, 而在于【把「pin1 朝向」与「JTAG 链在 SoM 侧通不通」这两件事, 在那一趟开工之前变成机器判据 + 一条写死的落点契约】★ ★ ⇒ ★★**并且: 你算出来的数如果和我上面给的不一样, 【以你本机复算的为准】, 但你必须在交卷页里写清差在哪、为什么差** ★★ ★
