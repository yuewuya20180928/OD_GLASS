# ISS-375 · sw-lead · 「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的**物理针序契约**（pin1 朝向 / JTAG 线序）+ JTAG 链 SoM 侧真相 · ★★cont1 续做 (★上一趟 23:16~23:23 被掐·沙盒半成品在盘·三件交付物零★)★★ · 纯分析 + 文档 + 新建闸 + 沙盒预演 · 零写板

★★**这是 cont1 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-23 23:16:44 派) 的子会话 `agent:sw-lead:subagent:0d87082c` (sessionId 570e20e2) 于 23:23:11 被掐死 (★sessions_list: status=timeout + abortedLastRun=true + runtimeMs=387,911 ≈ 6.5 分钟·★promptError = "This operation was aborted"·**externalAbort=false**·非上下文溢出 ⇒ 不是逻辑错★)** ⇒ ★**三件交付物一件没落** (★`SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` 不存在 · `SW/tools/check_debug_pin_order_contract.py` 不存在 · 交卷页不存在 · `state/fragments/sw.yaml` 里 `iss375` 命中 = 0★)** ⇒ ★**⇒ 本单 = 续做, 不是从零★**

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract.md` ★

---

## ★★一 已在盘的 (★不要重跑·直接用★) ★★

★**① 沙盒骨架 (★在盘·可复用·**不要重写**★)**★: `tmp/iss375_sbx/` = `iss375_build.py` (★单轮一个进程的建场脚本★) + `iss375_measure.py` (★逐 pad 读数★) + `iss375_run.sh` (★四轮驱动★) + `s1_jdebug_rot90.kicad_pcb` (★已建好·md5 `a353f674…`★) + `s2_jdebug_rot270.kicad_pcb` (★**见 ③ = 没建**) ★

★**② 四份读数在盘**: `logs/iss375/` = `meas_J_DEBUG_demo_mainboard.json` (★S0 = 现役板·**这份的 net 是对的**★) + `meas_J_UART_demo_mainboard.json` (★现役 `J_UART`·net 对★) + `meas_J_DEBUG_s1_jdebug_rot90.json` (★rot90·**net 全空**·见 ③★) + `meas_J_DEBUG_t_s2.json` (★rot270·**net 全空**·但**针序已证**·见 ④★) + `iss375_sandbox_raw.log` ★

★**③ ★★沙盒有一个真缺陷, 你必须先修它, 否则测出来的 net 全是错的★★**: ★**`tmp/iss375_sbx/iss375_build.py` 里 `p.SetNetCode(code[...])` 写在 `b.Add(fp)` 【之前】 ⇒ `SetNetCode` 对一个还没挂到板上的封装【是空操作】⇒ net code 静默丢失** ★ ⇒ ★**实测证据 (★我本机 00:3x 实读盘上文件★)**: ★`logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json` 里四个 pad 的 `"net"` 字段全是 `""` ★ ⇒ ★**修法 = 把 `SetNetCode` 挪到 `b.Add(fp)` 【之后】★** (★修完实测: pad1 net=`JTAG_TCK` / pad2=`JTAG_TMS` / pad3=`JTAG_TDI` / pad4=`JTAG_TDO`★) ★⇒ ★**你这一趟的第一件事就是把 builder 修对 + 重建 S1/S2 (★S2 那块板现在 md5 = `611b869e13518c3c027…` = **跟真板逐字节相同 ⇒ rot270 那块板压根没建出来**·跑脚本时死在了 S1 之后★)★**

★**④ ★★两件事已经在盘上【证完了】, 不许重做★ (★省下的时间全部投到交付物上★)★★**:

| 事项 | 盘上证据 (★我本机实读★) |
|---|---|
| ★**rot90 ⇒ pad1 在 X 最小端 (顺排)** ★ | `logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json`: pad`1` X=`141.0450` / pad`2` X=`142.3150` / pad`3` X=`143.5850` / pad`4` X=`144.8550` ⇒ TCK→TDO 从小到大 |
| ★**rot270 ⇒ pad1 在 X 最大端 (逆排) = rot90 的镜像** ★ | `logs/iss375/meas_J_DEBUG_t_s2.json`: pad`4` X=`141.0450` / pad`3` X=`142.3150` / pad`2` X=`143.5850` / pad`1` X=`144.8550` (★origin=`[144.855, 56.6]`·orient=`-90.0`★) ⇒ **两个候选互为逆序** |
| ★**官方 land 自带 pin1 极性标记 (pad1 = `thru_hole rect`, 其余 = `thru_hole circle`)** ★ | `logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json` 里 pad`1` `"shape": "RECT"` 而 pad2/3/4 `"shape": "CIRCLE"` ⇒ ★**换官方 land 后板面【第一次】出现 pin1 方形标记 ⇒ 「哪端是 pin1」从网表约定变成实物事实 ⇒ 选错 = 排线插反 = JTAG 救砖链不通** ★ |
| ★**现状板面没有 pin1 标记** ★ | `logs/iss375/meas_J_DEBUG_demo_mainboard.json`: 四个 pad 全 `"shape": "RECT"` + `"attr": "SMD"` + 0.275×0.900 ⇒ 现状全 SMD 无标记 |

★**⑤ 官方 land 文件在盘 (★读它·不抄文档★)**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` (★pad1 `thru_hole rect` (at 0 0) size 1×1 drill 0.65 · pad2 circle (at 0 1.27) · pad3 (at 0 2.54) · pad4 (at 0 3.81)·局部轴向 = Y★) ★

★**⑥ JTAG 链 SoM 侧的真相 (★我本机 00:3x 实读·四份件都在盘★)★**:
- ★`HW/netlist_v1.csv` 第 388/390/392/394 行 = `JTAG_TCK_SOC`/`JTAG_TMS_SOC`/`JTAG_TDI_SOC`/`JTAG_TDO_SOC` ⇒ ★**四条网的 SoM 侧端点全部是 `SoC_NC`** ★
- ★`HW/PCB/FET3572C_PIN_TABLE.csv` (★官方 399 行脚表★) ⇒ `grep -ic JTAG` = **0** ⇒ ★**官方脚表里没有 JTAG 同名信号** ★ ⇒ `HW/PCB/SOM_PIN_MAPPING.md` 第 48-51 行的结论成立
- ★⇒ ★**「那一趟选哪个 pin1 朝向」救不了这条链** (★它今天就是断的·S3 救砖路径不通·`SW/FLASH_AND_VERSION.md` 的 4 级救砖里 S3 = JTAG 是除返厂外唯一的软救砖路径★)★

---

## ★★二 你这一趟要交的东西 (★三件 + 交卷页 + 分片★) ★★

★**① ★新建★ 一页 `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (★本单产出物★)** ⇒ ★**必须含**: §0 一句话结论 + 三问回答 · §1 ★**物理针序契约表** (★逐件 `J_DEBUG` 1×4 / `J_UART` 1×2 各一行: 现状 pad1 在哪 + 现状有无极性标记 + 官方 land 的 pin1 标记形状 + **两个候选落点各自 pin1 在哪 + 四线物理线序 (顺排/逆排) + 要挪原点多少** + **裁决建议 (带代价·不代拍: 选 rot 90 还是 rot 270 + 为什么·归 main 裁**) + **落点写死值 (那一趟要用的: 原点坐标 + 旋转角 + pin1 在哪一端)**★) · §2 JTAG 链的 SoM 侧真相 (★四线 `SoC_NC` 逐条实读 + 脚表 399 行依据 + **「不落地」还是「信号不存在」这两句差别很大·按脚表实读判·不许混着写**★) · §3 与既有裁决的关系 (★`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 ISS-344 终裁 vs 网表现状 ⇒ 三条路的代价: ① 改裁决口径 ② 改网表 (★脚表里没有 JTAG 同名信号 ⇒ 这条路当前走不通★) ③ 改 SoM 选型 (★放弃 S3 救砖路径·只剩 S4 返厂★) ⇒ 每条给「要谁回答什么」★) · §4 证据等级 + 边界自证 ★

★**② ★新建★ 一条闸 `SW/tools/check_debug_pin_order_contract.py` (★本单产出物★)** ⇒ 判据 D0~D8 (★至少 8 条·每条 fail-closed★): D0 官方 land 的 pad1 形状 = 盘上 `.kicad_mod` 实读 (★不许写死「pad1 是 rect」★) · D1 现状板面 pad1 位置由脚本实读板得出 (★不许写死「现状是顺排」★) · D2 两个候选的 pad→X 序**用 KiCad 自己的 `FOOTPRINT.SetOrientationDegrees` 算** (★不许手算旋转矩阵★) ⇒ **算出的两序必须互为逆序, 不是互等, 否则红** · D3 页 §1 必须同时给出两个候选 + 裁决 + 落点写死值 (★只给一个候选 ⇒ 红★) · D4 页里写的 pin1 朝向必须与 D2 算出来的一致 (★不一致 ⇒ 红★) · D5 网表侧 JTAG 四线的 SoM 侧端点必须实读 (★不许把 `SoC_NC` 写死成常量★) · D6 `HW/PCB/SOM_PIN_MAPPING.md` 里 JTAG 四行的结论不得与页 §2 表述冲突 · D7 板指纹三项未动 · D8 证据等级五级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链 (★自证 `grep -c check_debug_pin_order_contract state/gate_check.py` == 0★) ⇒ ★**必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」·其中 ≥3 条针对「镜像」这个本单核心★: ① 把页里的 rot 90 改成 rot 270 ⇒ D3/D4 红 ② 把 D2 的算式改成手算常数 ⇒ D2 红 ③ 把网表里的 `SoC_NC` 改成别的 ⇒ D5 红★)★**

★**③ 沙盒预演 (★只落 `tmp/iss375_sbx/` + `logs/iss375/`★)**: ★**S0/S1/S2/S3 四轮, 但你只需要把 S1/S2 两块板【用修好的 builder】重建出来** (★S0 的读数已在盘且 net 是对的·S3 的针序已在盘上证完了·**不要重跑 S3**★) ⇒ ★**你这一趟真正要产出的是: 修完 builder 后 rot90 / rot270 两块板【带着正确 net】的逐 pad 读数 (★pad 号 / 形状 / net / X / Y / bbox / 铜箔包络 / fab 外框 / courtyard★)★** ★

★**④ 交卷页 `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` (★本单产出物★)**: ★**B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★** ⇒ ★**§B5 要写明「上一趟 23:23 被掐 + 本趟从已落沙盒续做 + 修了一个 net code 真缺陷」** ★

★**⑤ 分片 `state/fragments/sw.yaml`**: ★**只走 `state/frag_write.py` (★写前写后各记一次 md5·期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」·不许静默覆盖★)★** ⇒ ★**登记: 产出物 (★那页 + 那闸 + 交卷页★) + 3 条 `interface_claims` (★rot90 的 pad→X 序 / rot270 的 pad→X 序 / pin1 标记形状★) + 1 条 `needs_from` (★要 main 裁「pin1 朝向选哪条」·**key 要唯一**★) + 1 条 `needs_from` (★要 main 裁「JTAG 四线 SoM 侧不落地 ⇒ ISS-344 终裁怎么改」★) ★

---

## ★★三 边界 (★一条不许越·与原任务书相同★) ★★

★**零写板** (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★`HW/netlist_v1.csv` md5 `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` md5 `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` md5 `5b9993992405904a60ac96a020b375d8` 一律只读★) ★
★**零改既有闸** (★`SW/tools/timing_check.py` · `SW/tools/check_onepass_sw_release.py` · `SW/tools/check_fp_truth_read.py` · `SW/tools/check_sw_zero_copper_grade_consistency.py` · `HW/check_pcb_nets.py` · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** (★`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (★含 ISS-344 终裁块★) · `SW/FLASH_AND_VERSION.md` · `SW/SW_MD5_BASELINE_LEDGER.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) · `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` · `HW/PCB/SOM_PIN_MAPPING.md` · `HW/PCB/FP_TRUTH_BASELINE.md` —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动**★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §3/§4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/sw.yaml`** ★
★**沙盒只落 `tmp/iss375_sbx/` + `logs/iss375/`** ★
★**不代老板拍板** · **不代 main 拍** (★「pin1 朝向选哪条」与「JTAG 分组裁决怎么改」都是 main 的裁决权 ⇒ 你只给两条路的代价与机器判据★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查·查不到写降级方案·不许写「等原厂回信」**★) ★
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
md5sum HW/PCB/demo_mainboard.kicad_pcb                            # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                   # 必须 2026-11-06 07:07:17.362193413 4940213
```
★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「上一趟 23:23 被掐 + 本趟从已落沙盒续做」** ★
★**收工后回卷 (★按老规矩★)**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」★)★ ★

---

## ★★五 你必须自己复算、**不许抄**的数 (★我已算过一遍, 但你要自己重跑并贴你的输出★) ★★

1. ★**修好 builder 之后 rot90 那块板的四个 pad 的 net 与 X** (★期望: pad1/`JTAG_TCK`/141.0450 · pad2/`JTAG_TMS`/142.3150 · pad3/`JTAG_TDI`/143.5850 · pad4/`JTAG_TDO`/144.8550★) —— ★**这四个 net 是本单的核心, 你必须自己看到它们非空** ★
2. ★**rot270 那块板同一组读数** (★期望: pad1 在 X 最大端 144.8550 · 四个 pad 的 X 集合与 rot90 逐字相同 · pad→X 序互为逆序★)
3. ★**两块的铜箔 X 宽 / fab 外框 / courtyard** (★三个数在两个候选下必须逐字相同 ⇒ 这才是「几何等价 ⇒ 纯针序问题」的证明★)
4. ★**官方 land 的 pad1 形状** (★读盘上 `.kicad_mod`: pad1 `thru_hole rect` vs 其余 `thru_hole circle`★)
5. ★**网表侧 JTAG 四线的 SoM 侧端点** (★`HW/netlist_v1.csv` 第 388/390/392/394 行逐条实读 ⇒ 四行是不是都指向 `SoC_NC`★)
6. ★**官方脚表里 JTAG 命中数** (★`HW/PCB/FET3572C_PIN_TABLE.csv` ⇒ `grep -ic JTAG` ⇒ 0★)

★**★主命令 (★本机实测存在, 你自己再验一遍★) ★★**:

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

# 官方 land 的 pad 形状 (★读盘上 .kicad_mod, 不抄文档★)
grep -nE '\(pad "|thru_hole|drill|fp_rect' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod | head -20

# 网表侧 JTAG 四线 (★本机实读★)
sed -n '388,395p' HW/netlist_v1.csv

# 脚表 399 行里有没有 JTAG (★官方脚表实读★)
grep -icE "JTAG" HW/PCB/FET3572C_PIN_TABLE.csv

# 已有裁决 (★读, 不改★)
grep -nE "JTAG_TDI|必需|可悬空" SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | head -8
```

★**★最后一句纪律 (★main 2026-11-24 00:4x 追加★)★★**: ★**上一趟死在【沙盒建到一半】+【net code 设错顺序】这两件事上, 所以这一趟的顺序是硬要求: 【先修 builder → 重建 S1/S2 → 先把读数落盘到 `logs/iss375/` → 再写页 → 再写闸 → 最后交卷页 + 分片】★** ⇒ ★**不许把「重活」和「交付物」放同一趟的最后一步才写 (★子会话有一条约 16 分钟的硬墙★) ⇒ ★**第一个工具调用就应该是改 builder 或落读数, 不是写文档** ★** ★**并且: 你算出来的数如果和我上面给的不一样, 【以你本机复算的为准】, 但你必须在交卷页里写清差在哪、为什么差** ★
