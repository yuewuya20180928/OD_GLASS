# ISS-375 · sw-lead · 「板那一趟」`J_DEBUG`/`J_UART` 排针换 land 后的**物理针序契约**（pin1 朝向 / JTAG 线序）· ★★cont2 续做 (★上一趟 01:11~01:17 被掐·**页+闸已落·闸有 bug·交卷页/分片零**★)★★ · 纯分析 + 文档 + 新建闸 · 零写板

★★**这是 cont2 续做派活 (★不是从零重开★)** ⇒ ★**上一趟 (2026-11-24 01:11:01 派) 的子会话 `agent:sw-lead:subagent:4c87e4ad` (sessionId 27ce95b4) 于 01:17:17 被掐死 (★status=timeout + abortedLastRun=true + runtimeMs=574,213 ≈ 9.6 分钟·promptError="This operation was aborted"·**externalAbort=false** ⇒ 非外部 abort·非上下文溢出★)** ⇒ ★**⇒ 本单 = 【只补剩下的三件】, 不是从零★**

★**原任务书全文 (★判据/边界/交付物定义全部仍有效·必读★)**: `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract.md` ★
★**cont1 任务书 (★已交付部分的事实来源·必读★)**: `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract_cont1.md` ★

---

## ★★一 已在盘的 (★不要重做·直接用★) ★★

★**① 真相页已落**: `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (★32,392 B @ 2026-11-24 01:15★) ⇒ ★**★这一页你【不许重写】, 只允许【追加式订正】★** ★

★**② 新闸已落**: `SW/tools/check_debug_pin_order_contract.py` (★37,257 B @ 01:16★) ⇒ ★**★它有一个【真 bug】(★见 §二 ①·★main 本机实跑复现★) ⇒ 你要修它, 不是重写它★** ★

★**③ ★★沙盒读数已落盘, 而且 ★【net-code 那个真缺陷已经修好了】★★**: `logs/iss375/` 8 份 ⇒ ★**main 本机实读复核 (★00:5x/01:2x 两次实读★)★**:

| 文件 | main 实读结果 |
|---|---|
| `meas_J_DEBUG_s1_jdebug_rot90.json` | ★**pad1=`JTAG_TCK` (RECT) / pad2=`JTAG_TMS` (CIRCLE) / pad3=`JTAG_TDI` (CIRCLE) / pad4=`JTAG_TDO` (CIRCLE)** ⇒ ★**net 非空 ⇒ SetNetCode 顺序 bug 已修** ★ |
| `meas_J_DEBUG_s2_jdebug_rot270.json` | ★**pad4=`JTAG_TDO` / pad3=`JTAG_TDI` / pad2=`JTAG_TMS` / pad1=`JTAG_TCK`(RECT) ⇒ 逆排** ★ |
| `meas_J_UART_s3a_juart_rot90.json` | ★**pad1=`UART_TX` (RECT) / pad2=`UART_RX` (CIRCLE)** ★ |
| `meas_J_UART_s3b_juart_rot270.json` | ★**已落 (★main 未逐字读·你自己读★)** ★ |
| `meas_J_DEBUG_demo_mainboard.json` / `meas_J_UART_demo_mainboard.json` | ★**S0 基线 (net 对)** ★ |
| `iss375_sandbox_raw.log` / `meas_J_DEBUG_t_s2.json` | ★**上一趟 cont0 的旧读数 (★`t_s2` 那份是【rot270 假板】测的·已被 s2 取代·别用★)** ★ |

★**⇒ ★★所以: rot90 ⇒ pad1 在 X 最小端 (顺排 TCK→TDO) / rot270 ⇒ pad1 在 X 最大端 (逆排) / 两候选互为镜像 / 官方 land pad1=RECT 其余=CIRCLE (⇒ 换官方 land 后板面【第一次】出现 pin1 方形标记) / 现状板面全 SMD 全 RECT (无标记) —— ★★这六条已经在盘上证完了, 你【不要重跑沙盒】★★ ★**

★**④ ★★只差这三件 (★你的全部工作量★)★★**: ★**① 修闸的 bug (★§二 ①★) ② 新建交卷页 `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` (★B1~B6 六段齐全★) ③ 分片 `state/fragments/sw.yaml` 登记 (★只走 `state/frag_write.py`★) ★**

---

## ★★二 ★★你必须先修的那个 bug (★main 01:2x 本机实跑复现★) ★★

★**★症状**: ★**`python3 SW/tools/check_debug_pin_order_contract.py` 报 `AttributeError: 'SwigPyObject' object has no attribute 'FootprintLoad'` ⇒ rc≠0 ⇒ 闸全红** ★
★**★根因 (★main 实跑定位到行★)**: ★**闸里 `run_pcbnew()` 把代码写成临时 `.py` 再用 `bash state/pcbnew_py.sh <script>` 跑 (★这个入口本身是对的★) ⇒ 但它生成的那段代码里 `pcbnew.FootprintLoad(LAND_DIR, FP[ref])` 【解析失败】** ★
★**★★main 本机实测出的对照 (★两条命令·★你自己再验一遍★)★★**:
```bash
# (a) 直接跑一个脚本文件 ⇒ 【成功】
bash state/pcbnew_py.sh /tmp/t_fp.py   # 里面只 import pcbnew + pcbnew.FootprintLoad(LAND_DIR, "PinHeader_1x04_P1.27mm_Vertical")
# ⇒ main 实跑输出: FootprintLoad OK: PinHeader_1x04_P1.27mm_Vertical | pads: 4

# (b) 先 LoadBoard 再 FootprintLoad ⇒ 【也成功】
bash state/pcbnew_py.sh /tmp/t_fp2.py  # 先 shutil.copyfile + pcbnew.LoadBoard(dst) + b.Remove(old) 再 FootprintLoad
# ⇒ main 实跑输出: AFTER-LoadBoard FootprintLoad OK: PinHeader_1x04_P1.27mm_Vertical
```
★**⇒ 两条路都成功 ⇒ ★**问题不在 `FootprintLoad` 本身, 而在【闸生成的脚本的运行环境/入口与上面两条不同】** ★ ⇒ ★**★★修法 (★给你三个方向, ★你自己定位并修, ★★修完必须能复跑出 rc=0★)★★**:
- ★**方向 1**: ★**★别在闸里 `subprocess.Popen(["bash", PCBNEW_SH, script])` 里 spawn ★⇒ ★**改成在闸自己进程内 `import pcbnew` 是不行的 (★闸是普通 python3·pcbnew 只在 KiCad 自带 python 里有★) ⇒ ⇒ **唯一正解 = 让闸整体跑在 KiCad 自带 python 下**: ★**★把闸改成【用 `bash state/pcbnew_py.sh` 跑它自己】(★即闸是一个被 pcbnew_py.sh 执行的脚本, 而不是它去 spawn pcbnew_py.sh★) ⇒ 这就与 (a) 完全同构了** ★**★(★★这一条 main 认为是正解·★但你自己跑一遍确认·★别只信我★)★★**
- ★**方向 2**: ★**若闸必须留在普通 python3 下 ⇒ 子进程要显式带上 `PYTHONPATH` / `LD_LIBRARY_PATH` (★`state/pcbnew_py.sh` 里就是设这两个·★抄它★) ⇒ ★**并把 `FootprintLoad` 换成【直接读 `.kicad_mod` 文本解析 pad 几何】(★★推荐·★零 pcbnew 依赖·★最快★) ⇒ `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` 的 §0.1 就是这么读的★) ★
- ★**方向 3**: ★**把 `pcbnew.FootprintLoad` 换成 `pcbnew.FootprintLoad` 之外的等价读法** (★如 `pcbnew.PCB_IO_MGR`… ★不必★)

★**★★硬要求 (★main 验收会看★)★★**: ★**① 修完 `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` 必须 rc=0 且 D0~D8 全绿 ② `--selftest` 必须 rc=0 且末行 `ALL TESTS PASS` ③ 闸的 D0/D2 判据仍必须真读官方 land 的 pad1 形状 (★不许因为「绕开 pcbnew」就把判据改成读自己写死的数★) ④ 修闸的过程【不许碰板】★ ★

---

## ★★三 边界 (★一条不许越·与原任务书相同★) ★★

★**零写板** (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★`HW/netlist_v1.csv` md5 `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` md5 `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` md5 `5b9993992405904a60ac96a020b375d8` 一律只读★) ★
★**零改既有闸** (★`SW/tools/timing_check.py` · `SW/tools/check_onepass_sw_release.py` · `SW/tools/check_fp_truth_read.py` · `SW/tools/check_sw_zero_copper_grade_consistency.py` · `HW/check_pcb_nets.py` · `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ⇒ ★**★你只许改【你自己这一单的闸】`SW/tools/check_debug_pin_order_contract.py`★** ★
★**零改既有页面正文** (★`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` (★含 ISS-344 终裁块★) · `SW/FLASH_AND_VERSION.md` · `SW/SW_MD5_BASELINE_LEDGER.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收件★) · `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` · `HW/PCB/SOM_PIN_MAPPING.md` · `HW/PCB/FP_TRUTH_BASELINE.md` —— ★**本单只许【追加式订正】你自己那一页, 其余既有页面一个字都不许动**★ ⇒ ★**要订正别的既有页面 ⇒ 写成「追加式订正块」放进你自己那一页的 §3/§4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/sw.yaml`** (★**只走 `python3 state/frag_write.py --agent sw-lead`** ★· 写前写后各记一次 md5 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」· 不许静默覆盖★) ★
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
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py         # 新闸 ⇒ rc=0 (★修完这条才过★)
bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py --selftest   # rc=0 (末行 ALL TESTS PASS)
python3 SW/tools/timing_check.py                                  # rc=0 (★既有闸必须仍绿·零漂移自证★)
python3 SW/tools/check_sw_zero_copper_grade_consistency.py        # rc=0 (★既有闸必须仍绿★)
python3 state/merge.py                                            # rc=0
python3 state/gate_check.py                                       # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                             # rc=0
grep -c check_debug_pin_order_contract state/gate_check.py        # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                            # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                   # 必须 2026-11-06 07:07:17.362193413 4940213
```
★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS375_调试排针物理针序契约与JTAG链SoM侧真相.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「cont1 被掐 + 本趟从已落页/闸/读数续做 + 修了闸的一个真 bug」** ★
★**收工后回卷 (★按老规矩★)**: ★交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」★)★ ★

---

## ★★五 ★★你这一趟有一条约 16 分钟的硬墙 (★实测: 之前三趟续做会话都被掐在这一带·★上一趟还因为【父 run 收尾连带】被掐在 9.6 分钟★) ⇒ ★★顺序必须严格照这个来, 每一步都先落盘★★ ★★

1. ★**① 先修闸 (★§二★) ⇒ 跑 `bash state/pcbnew_py.sh SW/tools/check_debug_pin_order_contract.py` 拿到 rc=0** ★
2. ★**② 跑 `--selftest` 拿 rc=0 + 末行 `ALL TESTS PASS`** ★
3. ★**③ 新建交卷页 (★B1~B6★) 并落盘** ★
4. ★**④ 分片登记 (★`state/frag_write.py`★) 并落盘** ★
5. ★**⑤ 最后跑一遍 §四 那 11 条命令, 把输出贴进交卷页 B6** ★

★**★第一个工具调用 = 修闸 (★不是读文档·不是读你已有的页★) ★★** ★**★并且: ★★若你跟 main 给的数对不上, 【以你本机复算的为准】, 但必须在交卷页里写清差在哪、为什么差★★ ★**
