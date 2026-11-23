# ISS-379 · hw-lead · 「板那一趟」`J_UART` (1×2) 换官方 P1.27 THT land 的**落位可行性**穷举 · 纯分析 + 真相页 + 新建闸 · 零写板 · 零落表

★★**本单 = ISS-376 (`J_DEBUG` 1×4) 的对称件**★★ —— ★**E-1 判定: `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch `0.50 → 1.27` 要在【同一趟】做完** (★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 判据栏 + `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 第 ③ 行★) ⇒ ★**ISS-376 只算了 `J_DEBUG` 那一半 ⇒ `J_UART` 这一半至今没人算过** ⇒ ★**「板只改一次」⇒ 这一半必须现在算清楚, 不能等画板时才发现放不下** ★

★★**main 已替你实测好的事实 (2026-11-24 03:4x 本机实读 · 可复跑 · ★别重查★)★★:

| 项 | 实测值 |
|---|---|
| 现位形态 | `J_UART` = ★**2 个 SMD 焊盘** (pad attr=1 · 无孔) · 尺寸 `0.275 × 0.900` · ★**pitch = 0.50**★ |
| 现位 pad 绝对坐标 | ★**pad1 `(18.6400, 68.6000)`** / ★**pad2 `(19.1400, 68.6000)`** (沿 X 一排) ★ |
| 封装原点 / crtyd bbox | `(20.7400, 70.0000)` / `(17.6900, 67.9500) - (23.7900, 72.0500)` |
| 现位网络 | ★**pad1 = `UART_TX` (netcode 129) · pad2 = `UART_RX` (netcode 130)** ⇒ ★**只有 2 个脚, 顺序 = 1:TX / 2:RX** ★ |
| 目标 land (★官方 KiCad 10 库 · **已在盘**★) | `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod` (★3,074 B · ★**不用去网上找这个件★**) ⇒ 同目录备用候选: `PinHeader_1x02_P1.27mm_Horizontal.kicad_mod` / `PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` / `PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Right.kicad_mod` |
| 现位周边 5 个邻居 (crtYd bbox · 实读) | `U_TEMP` (10.995, 69.225)-(13.545, 71.775) · `TP_UART` (19.990, 74.250)-(21.490, 75.750) · `R_PU_I2CB_SDA` (26.690, 67.950)-(29.540, 69.050) · `C_RST` (31.490, 67.950)-(34.340, 69.050) · `SW_KEY_CAM` (19.350, 61.950)-(22.800, 65.050) |
| 板面判据 | ★**自己从 `HW/PCB/demo_mainboard.kicad_pro` 读, 不许写死**★ (★ISS-376 实测过 `min_copper_edge_clearance` = `0.5` · 孔净距判据 = `0.25`·★本单自己复跑一遍并写清读到的原文★) |

★★**同族可复用的方法与模板 (★照抄口径, 别重写方法★)★★**: 真相页 `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` (★131,169 B · ★**只准按需 grep 定位读, 不许整文件读进上下文★**) · 闸 `HW/check_jdebug_land_fit.py` (★45,476 B · 同上★) · 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS376_JDEBUG排针换land落位可行性.md` (★30,109 B★)
★**ISS-376 的三个坑, 直接继承 (★别再踩一遍★)★**: ① 官方 land 的 `F.CrtYd` ★**不对称** ⇒ ★**旋转后必须实算 bbox, 不许按对称矩形算** (★ISS-376 cont1 就是按对称算错的, 可行域格数从 `23,646/19,207/7,008` 修正为 `23,285/12,787/12,526`★) ② ★**rot 0 与 rot 90 的铜箔包络会互换** (★1×4 实测 rot0 X 宽 `1.0000` / rot90 X 宽 `4.8100` ⇒ ★**1×2 也必须实算, 不许类推★**) ③ ★**用 `SetOrientationDegrees` 实算绝对坐标, 不许手算旋转矩阵** ★

★★**你要交四件 (★顺序很重要 · 有墙 · 先落重的★)★★

1. ★**新建** 真相页 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` ⇒ 必须含:
   - §1 ★**官方 land 实读** (★从 `.kicad_mod` 解析: pad 数 / 孔径 / 孔位 / `F.Fab` / `F.CrtYd` / `F.CrtYd` 是否对称★)
   - §2 ★**三朝向 (rot 0 / 90 / 270) 的 pad 绝对坐标表** (★`SetOrientationDegrees` 实算★) + 每朝向的铜箔包络 / 孔位 / 清空区包络
   - §3 ★**现位冲突表**: 官方 1×2 land 装现位会撞谁 (★过孔净距 ≥ `0.25` / 铜到铜 / 铜到板边 ≥ `0.5` / 与上列 5 个邻居的 crtyd 间隙★) ⇒ ★**逐条给数, 不许写「可能冲突」**
   - §4 ★**落位可行域**: 网格 `0.1 mm` 扫描 (★起步范围 X `10.0..30.0` / Y `64.0..78.0` · 不够自己扩并在页上写清扩到哪★) × 3 朝向 ⇒ ★**给可行域区间 + 最小位移 + 落点坐标 + 余量** (★对照 ISS-376 的口径: 最小位移 `5.7009 mm` / 落点 `(150.0000, 57.9000)` / 余量 `2.3254`·★你的是 `J_UART` 的数, 不许套用★)
   - §5 ★**代价账**: 挪了以后要重接哪几段走线 / 要不要挪过孔 (★端点坐标给出来★) · ★**能不能一个过孔都不挪**
   - §6 ★**pin 顺序契约**: 1×2 只有 2 个脚 ⇒ rot 0 / rot 90 / rot 270 各自的 pad1 在哪 ⇒ ★**`UART_TX` / `UART_RX` 对焊盘的映射会不会翻转** ⇒ ★**只管 `J_UART` 这半边, 不许替 sw-lead 回答 `J_DEBUG` 那半边 (那是 ISS-378 的地界)★**
   - §7 未决项 (★要 main 裁什么 / 要 mech-lead 答什么 / 要 sw-lead 答什么, 各一条一行, 写清「要谁回答什么」★)
2. ★**新建** 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md` ⇒ ★**六个 `##` 标题必须逐字含这些关键词 (★gate_check 靠标题命中, 一次写对★)★**: `## B1 结论摘要` · `## B2 验收标准自评` · `## B3 证据分级` · `## B4 接口取值声明` · `## B5 未决项与卡点` · `## B6 自证复现命令` ⇒ ★**§B1 第一句必须是一句「一句话结论」(能放 / 不能放 + 最小位移 + 落点)★**
3. ★**新建** 闸 `HW/check_juart_land_fit.py` ⇒ 判据 **K0~K8** (★每条 fail-closed · 每条一条反向用例 · `--selftest` 末行必须是 `ALL TESTS PASS`★) ⇒ ★★**闸不许挂进 `state/gate_check.py`** (★挂链是 main 的地界 · 你只交脚本 + 路径 + 建议★)★★
4. ★**分片登记** `state/fragments/hw.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent hw-lead`** (★禁止 `open(p,"w")`★) · 写前写后各记一次 md5 · ★**期间若被别人改过 ⇒ 停下并在 §B5 写明「已停止」, 不许静默覆盖** ★

★★**必跑命令 (★原样把输出贴进 §B6★)★★
```bash
python3 state/merge.py
python3 state/gate_check.py
★本单新建的闸自跑: python3 HW/check_juart_land_fit.py
★本单新建的闸自测: python3 HW/check_juart_land_fit.py --selftest
bash state/pcbnew_py.sh -c "<你自己的只读板面查询>"
md5sum HW/PCB/demo_mainboard.kicad_pcb
```
★**`merge` rc 必须 0 · `gate_check` rc 必须 0 且 Q1 必须 18/18 · 新闸 rc 必须 0 · `--selftest` 末行 `ALL TESTS PASS` · 板 md5 必须仍是 `611b869e13518c3c023fb178f91a0075`** ★

★★**边界 (★一条不许越·★与 ISS-376 同款★)★★
- ★**零写板** ★: 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ ★**开工前与交卷后各打一次, 三项一致** ⇒ ★**板一个字节都不许动** ★
- ★**零落表** ★: 网表 / 脚表 / BOM ★**只读** ★
- ★**零改既有闸 / 零改既有页面正文** ★: `HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ★**一个字都不许动** ⇒ ★**要订正就写成【追加式订正块】交 main 决定** ★
- ★**零挂链** ★: `state/gate_check.py` 不许改 ⇒ ★**闸只交脚本 + 路径 + 建议** ★
- ★**零外发** ★: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 (★降级方案是必须项★)** ⇒ ★**没有「等原厂回信」这个选项** ★
- ★**证据等级固定五级** ★: `[官网]` (厂商官网 / 官方 datasheet) / `[实测]` (本机可复现) / `[媒体]` / `[推算]` / `[0数据]` (查不到) ★
- ★**不代拍** ★: 换不换 land / 挪不挪 / 挪到哪 / pin 顺序要不要改 / 开口会不会被挤 ⇒ ★**分别登记给 main / main / mech-lead / sw-lead, 本单只给事实与代价** ★
- ★**不自签 `state/issue_log.yaml`** ★
- ★**沙盒只落** ★ `tmp/iss379/` + `logs/iss379/` ★

★★**时间提醒 (★有墙 · 上一趟 16 分钟被掐死 · ISS-376 cont1 与 ISS-377 cont1 都栽在这★)★★
★**顺序 = ①真相页 (≤8 分钟) → ②交卷页 (≤4 分钟) → ③新闸 (≤6 分钟) → ④分片 + 贴 rc ⇒ 四步做完就收工 · 不许加戏 · 不许整文件读大文件 (131 KB / 93 KB 的页只准 grep 定位读)★** ★

★★**收工后回卷** ★: 交卷摘要 + 必跑命令的 rc + 四件交付物路径 + 边界自证 + 要 main 裁的事 (★逐条写清「要谁回答什么」★) ★
