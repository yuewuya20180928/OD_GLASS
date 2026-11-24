# ISS-386 · mech-lead · 「板只改一次」那一趟的 `J_DEBUG` + `J_UART` 两连接器【座体 / 开口 / 清空区 三件合到一件答】(★纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍★)

★**本单 = 纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 为什么开这个单 (★main 2026-11-24 08:3x 本机实读 + 实算 · 不抄任何 agent 报告★) ★★

★① `python3 state/advance.py --json` 实跑 (2026-11-24 08:1x) ⇒ ★**`internal: []`** ⇒ 三个总工名下零 open 可派 ⇒ ★**但台账实读: mech-lead `open 0` / `fixing 0` / `verified 67`** ⇒ ★**mech-lead 槽位真空 ⇒ 队列对 MECH 这条线真断线** ★

★② ★**本单的触发源 = `state/fragments/pm.yaml` 里一条【一直没人答】的 need** (★`iss379_q4_mech_opening_and_clearance` · ★`since: 2026-11-24`): ★**它是 main 2026-11-24 06:0x 转给 mech-lead 的两问, ★原文写明「两问都要 mech-lead 答, 且必须在「板那一趟」开工前答完」** ★ ⇒ ★**它至今没被接走** ★

★③ ★**这两问是什么 (main 本机实读 need 原文转述 · 不代裁★)**: ★**① `J_UART` 落点横移会不会挤掉 UART 罩开口 / 座体必须清空区? ② 官方 THT land 铜箔 X 宽 `2.2700` vs 座体必须清空区宽 `2.5400` ⇒ 每边余量 `0.1350` < `CRIT` `0.60` ⇒ 结构红灯 ⇒ 「板那一趟」的结构件怎么办** ★

★④ ★**main 本机实读到的【板侧那半已经交付】(⇒ 你不用重算板侧铜)**:
★**板侧候选落点三个 (★`HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` §2.3 实读★)**: ★**rot 270 pad1 `(18.6000, 68.6000)` 余量 `0.2750` (最小 pad1 位移 `0.0400` mm) · rot 90 pad1 `(18.4000, 68.4000)` 余量 `0.1155` (最小 pad1 位移 `0.2441` mm) · rot 90 pad1 `(18.3000, 68.6000)` 余量 `0.0447`** ★ ⇒ ★**这三个是【互斥】的, ★**main 已在 ISS-379 签收裁决里明确「落点本单不定 (前提没落)」★ ⇒ ★★**你【不许替 main 挑一个落点】★★** ★

★⑤ ★**main 本机实读到的【两连接器的现有真相数 (★你只读, 不许改★)】**:

| 项 | `J_DEBUG` (1×4) | `J_UART` (1×2) | 出处 (main 实读) |
|---|---|---|---|
| ★罩开口 (居中解)★ | ★**X `137.850..148.050` × Y `54.300..58.900`** ★ | ★**X `13.790..23.990` × Y `66.300..70.900`** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L183-L184 / L196-L197 |
| ★座体必须清空区 (高 2.54 假设)★ | ★**X `142.063..143.838` × Y `55.330..57.870`** ★ | ★**X `17.620..20.160` × Y `67.330..69.870`** ★ | 同上 L183 / L196 |
| ★现状铜箔宽 (板读)★ | `1.7750` | `0.7750` | 同上 L159 |
| ★官方 THT land 铜箔宽 (沿针排轴)★ | ★**`4.8100`** (★`3.81 + 1.00`★) | ★**`2.2700`** (★`1.27 + 1.00`★) | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L29 / `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` |
| ★**换 THT 后罩住余量 (现状清空区口径)**★ | ★**每边超 `1.5175`** ★ | ★**每边余 `0.1350`** ★ | `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` L88 / L90 |

★⑥ ★**★main 本机实读出的【这条 need 自己点明的「板侧已交付 / 3D 那半是 mech-lead 的域」】★**: ★**need 原文写「板侧这半已交付 · ★3D 那半是 mech-lead 的域」· 并把板侧给的三个候选 copper bbox 直接写进了 need (★rot 270 方案 copper X `16.8700..19.1400` · rot 90 方案 copper X `18.1400..20.4100`★)** ★ ⇒ ★**★⇒ 你【不许重算板侧铜】, 你要判的是【这三个 bbox 对 3D 座体 / 开口放不放得下】★ ★**

★⑦ ★**★main 本机实读出的【本单真正的难点 —— 三条 must 不许你跳过】★★**:
- ★**A · `J_DEBUG` 的「必须清空区 X 宽」在仓里有【三个数】 (`1.7750` 现状铜箔宽 / `4.0850` 现页四处 / `4.8100` 官方 THT 真 land) ⇒ 没有单一真源 ⇒ ★**结构件按哪个出件, 决定它会不会当场干涉 (★每边超 `1.5175` vs `0.3625`, ★**差 4.18 倍**★)** ★ ⇒ ★**★main 在 ISS-377 已登记 `OI-5` 问「以哪一个为准」· ★**它至今未答**★★ ⇒ ★★**你【不许替 main 答】, 但你【必须把三个数各算一遍】把「按每个数出件 ⇒ 会怎样」摊成表, 供 main 一句话定死**★★** ★
- ★**B · `J_DEBUG` 与 `J_UART` 换 THT 后是【一红一绿】, 而两者的判据方向【相反】 (`J_DEBUG` 走「开口余量」`2.6950` 过阈 · `J_UART` 走「罩住余量」`0.1350` 不过阈) ⇒ ★**main 在 ISS-379 签收裁决里明确要求「把 J_DEBUG + J_UART 两连接器的座体/开口/清空区【合到一件】答 · 别分两票 · 同批改的板两个答案不能互相矛盾」** ★ ⇒ ★★★**⇒ 你【必须】把两件放在【同一张同源表】里一起答, 不许分成两页各自绿** ★★★ ★
- ★**C · `J_UART` 的落点是【互斥三选一】且 main 已挂起 ⇒ ★**你的结论必须对【三个候选都成立】, 不许只对其中一个算 ⇒ ★**这是「与板那一趟同批」的必要条件 (板框上位问题一落甲, 三个坐标才全有效)** ★

★⑧ ★**本单【不重复谁】**: ★**ISS-374 (mech-lead) 已 verified** ⇒ ★**J_UART 侧 `1.27mm` 净距真相已交付** ★ · ★**ISS-377 (mech-lead) 已 verified** ⇒ ★**「同源化」判据 (`M = max(H_housing, C_copper)` → 开口余量/罩住余量 → 最坏 = 余量 − `TOL["fdm_part"]` → ≥ `CRIT`) + 9 颗连接器表已交付** ★ · ★**ISS-382 (mech-lead) 已 verified** ⇒ ★**`J_DEBUG` 排布标签 (`2x2` vs 实测 `2x4_staggered`) 已订正 + `G5` 维数盲区新闸已建** ★ · ★**ISS-379 (hw-lead) 已 verified** ⇒ ★**板侧三个候选落点已交付 (只读)** ★ · ★**⇒ ★**你要做的是【把上面这些已签收的件【合到一件】重新组织成【那一趟能直接用的答案】, 不是重算它们** ★**

---

## ★★二 · 权威源 (★只读·已签收·你只许引用不许改★) ★★

| 事实 | 权威出处 | 你要取什么 |
|---|---|---|
| ★**同源判据链 (口径真身)** ★ | `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` §1 (★ISS-377 已 verified★) | ★**④ 开口余量 `(O − M)/2` · ⑤ 罩住余量 `(H − C)/2` · ⑥ 最坏 = 余量 − `TOL["fdm_part"]` · ⑦ 判据: 最坏 ≥ `CRIT`** ★ |
| ★**`CRIT` / `TOL` 真身 (不许写死)** ★ | `MECH/service_port_check.py` **L126-L127** (★`TOL = {"fdm_part": 0.30, "fdm_feat": 0.25}` · `CRIT = 2 * TOL["fdm_part"]` = 0.60★) | ★**从源码读, 不许在页里写死 0.60/0.30** ★ |
| ★**开口 / 清空区 真身** ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.4 (`J_DEBUG`) / §3.5 (`J_UART`) + L72 机器块 | ★**开口矩形 + 必须清空区矩形 + 帧 id (`B160x100`)★** |
| ★**官方 land 铜箔宽** ★ | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` §0.1 (★解析 `.kicad_mod` 实算 ⇒ `4.8100`★) + `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (`2.2700`) | ★**两个铜箔包络 (含 Y 宽)★** |
| ★**板侧三个候选落点 + 各自 copper bbox** ★ | `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` §2.3 (★ISS-379 已 verified★) | ★**三候选的 (朝向, pad1 绝对坐标, 余量) + 板侧算好的 copper bbox★** |
| ★**排布真值 (J_DEBUG 是 2×4)** ★ | `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` (★ISS-382 已 verified★) + `MECH/check_jdebug_arrangement_truth.py` | ★**`arrangement` = `2x4_staggered` (★不是 `2x2`★) + 现有 SMD/THT 变体实测** ★ |
| ★**三份真值页同源对照** ★ | `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` (★ISS-295 已 verified★) + `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块 | ★**认领句原文 + 机器块 `openings[]` 的取法** ★ |

★**复现命令 (main 本机跑过, rc=0)**:
```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_struct_crosscheck.py      # rc=0
python3 MECH/check_onepass_mech_sync.py               # rc=0
python3 MECH/check_jdebug_arrangement_truth.py        # rc=0
python3 MECH/check_jdebug_1p27_clearance.py           # rc=0
python3 MECH/check_juart_1p27_clearance.py            # rc=0
python3 MECH/check_board_frame_coords.py --compute    # ★自己复跑一次看参数
```

---

## ★★三 · 你要交什么 (★交卷物 4 件 · 逐字可执行·不许含糊★) ★★

★**★★① ★新建★ `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` — 一页把两连接器合到一件答** ★★
- §0 ★**一句话结论**: ★**「`J_DEBUG` 与 `J_UART` 换官方 P1.27 THT land 后, 两颗件的 3D 净距判决【方向相反】(`J_DEBUG` 走开口余量过阈 / `J_UART` 走罩住余量不过阈); `J_DEBUG` 的清空区 X 宽有三个竞争值 (`1.7750`/`4.0850`/`4.8100`) ⇒ 按哪个出件决定每边超 `1.5175` 还是 `0.3625`; `J_UART` 三个候选落点的 3D 放得下判定逐候选给出」** ★
- §1 ★**★同源主表 (★命门: 两连接器必须同表·不许分两页·不许分两票★)★**: ★**每行 = 「位号 | 档位 (现状 / 官方 THT) | 铜箔包络 X/Y | 座体必须清空区 X/Y | 开口 X/Y | 口径来源 | 开口余量 | 罩住余量 | 最坏余量 (FDM ±0.30) | `CRIT` | 过/不过 | 证据等级 | 出处页+行号」** ★ ⇒ ★**★两件同表·同判据·同 `TOL`/`CRIT` 取法★** ⇒ ★★**这一节是本单的核心交付: 它证明「两件不互相矛盾」★ ★**
- §2 ★**`J_UART` 三个候选落点的 3D 放得下判定 (逐候选)**: ★**对板侧给的三个候选 (★rot 270 `(18.6000, 68.6000)` / rot 90 `(18.4000, 68.4000)` / rot 90 `(18.3000, 68.6000)`★), 逐个算**: ★**该候选的 copper bbox 是否落在 罩开口 `X 13.790..23.990 × Y 66.300..70.900` 内 + 是否落在 座体必须清空区 `X 17.620..20.160 × Y 67.330..69.870` 内 + 两边余量各是多少 + 判过/不过** ★ ⇒ ★★★**★三个候选必须【全部】给结论, 不许只算一个 (★C 条: 落点互斥且 main 已挂起, ★**结论要对三个都成立**)★★★ ★** ⇒ ★**★并且要写明: 这三个候选的坐标挂在【帧 `B160x100`】上 ⇒ ★**若上位问题落乙, 三个坐标全部作废** ★ ⇒ ★**★你的结论必须写成【与帧无关的形式】(★例: 「只要 copper bbox 的 X 跨度 ≤ 开口 X 宽且 中心落在清空区内 ⇒ 放得下」), 而不是把坐标钉死在 160×100 上★ ★**
- §3 ★**`J_DEBUG` 的清空区 X 宽三值各算一遍 (★供 main 一句话定死 `OI-5`★)**: ★**按 `1.7750` / `4.0850` / `4.8100` 三个数各算一遍「换官方 THT 后罩住余量 + 每边超出量 + 结构件要不要返工」⇒ 摆成一张三行表 + 每行的代价** ⇒ ★★**★你【不许说「应该用 4.8100」】(★那是 main/老板的裁决权·★你只摆事实与代价)★★ ★ ⇒ ★**★同时给降级方案 (★像 `DP-1` 那种「取最坏值」的路) ⇒ 查不到就 `[0数据]` + 降级方案, 不许挂「等原厂回信」★ ★**
- §4 ★**两件【合到一件】的一致性核对**: ★**逐条列: 「`J_DEBUG` 的结论有没有隐含要求 `J_UART` 也改 / 反之」⇒ 若有一处互相矛盾, 点名指出** ★ ⇒ ★★★**★这一节直接兑现 main 的「别分两票·同批改的板两个答案不能互相矛盾」★★ ★**
- §5 ★**证据分级表**: ★**每行标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ⇒ ★**本单主体 = `[实测]` (本机实读页 + 实跑闸 + 板读 `logs/iss377/board_connectors.json`) + `[推算]` (余量推导) + `CRIT`/`TOL` 是 `[实测]` (源码 L126-L127)** ★
- §6 ★**未决项 + 要谁回答什么**: ★**★`OI-5` (`J_DEBUG` 清空区 X 宽以哪个数为准) ⇒ to=main** ★ · ★**★`J_UART` 落点三选一 ⇒ to=main (★它已被 ISS-379 裁决挂起, ★**你【不许】重开这个裁决★, 只登记依赖)★★** ★ · ★**★`J_DEBUG` 座体真实高 h 仍是 `[0数据]` ⇒ 按 Z 向保守上界 `4.70` 参数化 (★与 ISS-380 §3.3-② 同源★)** ★
- ★★**机器块**: ★**一行 `debug_seat_3d_fit:` + `j_debug_clearance_x_candidates` (三值数组) + `j_uart_candidates` (三候选 × 开口/清空区判定) + `criterion` (`CRIT` / `TOL` 取法声明) + `frame_id` (`B160x100`)** ★★ ⇒ ★**格式照 `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` 的机器块写法 (★自己先读那份页怎么写的★)**

★**★★② ★新建★ `MECH/check_debug_seat_3d_fit.py` — 新闸 (★本单【不许改既有闸】·只新建★)** ★★
- ★**它要抓什么**: ★**把上面 §1 同源主表 + §2 三候选判定做成机器判据, 并守两条不变量**: ★**① 两连接器必须【同表】且【同判据】(★`CRIT`/`TOL` 取法一致) ⇒ 不一致就红 ② `J_UART` 的三个候选【必须全部】有判决 (★少一个就红)** ★
- ★**★它【不许】误伤 (★本闸最容易写错的地方·★盯死★)★★**:
  - ★**★① 落点选择权【不在你这里】⇒ 闸【不许】判「哪个候选最好」⇒ 它只判「三个候选是否都被判了 + 判定是否自洽」⇒ ★**反向用例必须含: 「把三个候选删成一个 ⇒ 必须变红」** ★★ ★
  - ★**★② 帧依赖必须被显式处理 ⇒ 闸要判「结论是否写明了帧 id + 是否声明了坐标随上位问题作废」⇒ ★**反向用例必须含: 「把结论里的帧 id 改成别的 ⇒ 必须变红」** ★★ ★
  - ★**★③ `CRIT`/`TOL` 必须从 `MECH/service_port_check.py` 源码读, 不许写死 ⇒ ★**反向用例必须含: 「把源码里的 `TOL["fdm_part"]` 改掉 ⇒ 闸读数必须跟着变」** ★★ ⇒ ★★**这一条证明你的闸不是装饰★ ★★
- ★**判据清单 (自己定, 但至少要有这几条)**: ★**① 两连接器同表 (行数/字段一致) ② `J_UART` 三候选齐全 ③ 每行余量 = 公式实算, 与机器块逐字相等 ④ 最坏余量 = 余量 − `TOL["fdm_part"]` ⑤ 判决与实算不相反 (★不许把不过写成过★) ⑥ `CRIT`/`TOL` 取法声明存在且与源码一致 ⑦ 帧 id 声明存在 ⑧ 证据等级齐全 ⑨ 零挂链** ★
- ★**★`--selftest` 至少 10 条反向用例**: ★**每条 = 「把表/页/源码改坏 ⇒ 闸必须 rc=1 且点名」** ⇒ ★**必须含上面三条命门** ⇒ ★**末行必须打印 `ALL TESTS PASS`** ★
- ★**★零挂链**: ★**闸写好 + 自测过即可, ★**不许**把它挂进 `state/gate_check.py` (★挂链是 main 的地界·★先例同款: ISS-300/309/312/315/372/379/381/382/383 全同款★)★ ⇒ ★**页里要写明「本闸零挂链」+ `grep -c check_debug_seat_3d_fit state/gate_check.py` = 0 的实测** ★

★**★★③ 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md` (★新建★) · B1~B6 齐全** ★★
- ★**B1 结论摘要 · B2 验收标准自评 (逐条 通过/不通过/未验) · B3 证据分级 · B4 接口取值声明 · B5 未决项与卡点 (需要谁回答什么) · B6 自证复现命令** ★
- ★**B2 必须逐条判**: ★**两连接器是否在同一张同源表里 (逐行列, 不许写「已合并」这种空话) · `J_UART` 三个候选是否全部有判决 (逐个列) · `J_DEBUG` 三个清空区候选值是否各算了一遍 · §4 一致性核对是否有结论 · ★**`J_UART` 落点【有没有被你偷偷挑掉一个】** (★这一条不许糊过去·★门禁不查这个, ★只有人查) · 网表/脚表/BOM md5 前后逐字相同 (零落表) · 板三项指纹逐字相同 (零写板) · 既有闸 md5 未变 · 既有页正文未变 · 新闸裸跑 rc=0 · 新闸 `--selftest` 末行 ALL TESTS PASS · `grep -c check_debug_seat_3d_fit state/gate_check.py` = 0** ★

★**★★④ 分片 `state/fragments/mech.yaml` (★只走 `state/frag_write.py`★)** ★★
- ★**产出物 3 条** (★真相页 + 新闸 + 交卷页★) · ★**`interface_claims` ≥ 5 条** (★逐条写清: 同源表两件各轴余量 / 三候选各自判定 / 三清空区候选值各自后果 / 帧依赖声明★) · ★**`needs_from` 里写「谁要答什么」** ⇒ ★**★`OI-5` ⇒ to=main (★**你不许自己答**)★** ⇒ ★★**不许把没查到的东西写成「等原厂回信」★ ⇒ ★**查不到 ⇒ `[0数据]` + 降级方案** ★

---

## ★★四 · 必跑命令 (★rc 实测·★全部真实存在·★main 本机跑过★) ★★

```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_debug_seat_3d_fit.py                # rc=0  新闸裸跑 (★新建·交卷时才存在★)
python3 MECH/check_debug_seat_3d_fit.py --selftest     # rc=0  末行 ALL TESTS PASS (★新建★)
python3 MECH/check_onepass_struct_crosscheck.py        # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_onepass_mech_sync.py                # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_jdebug_arrangement_truth.py         # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_jdebug_1p27_clearance.py            # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_juart_1p27_clearance.py             # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_board_frame_coords.py --compute     # rc=0  帧坐标机器复算
python3 MECH/check_mech_verdict_freshness.py           # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0  【Q1 18/18】
python3 state/check_brief_commands.py                   # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv MECH/service_port_check.py MECH/check_onepass_struct_crosscheck.py
grep -c check_debug_seat_3d_fit state/gate_check.py   # ★必须 = 0 (零挂链)
```

★**★基线 (★main 本机实跑·★交卷后必须逐字相同·★别把别人的红当成你的★)★★: ★**`python3 MECH/check_connector_clearance_caliber.py` rc=1 (★那是【基线】·★K7 本来就红 2 条·★前后逐字相同即可·★不是你的锅★)** ★ · ★**其余上面列的既有闸 rc 全 0** ★ · ★**`python3 state/gate_check.py` rc=0 (Q1 18/18)** ★

★**★板指纹 (★零写板·★开工前后各打一次·★纳秒级比★)★★**: ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★

---

## ★★五 · 边界 (★一个字节都不许越★) ★★

★**① 零写板** ⇒ ★**`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 逐字节不变 (★三项指纹开工前后各打一次★)** ★
★**② 零落表** ⇒ ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 逐字节不变** ★
★**★★③ 零改已签收件 (★本单最容易越界的一条·★盯死★)★★** ⇒ ★**★下列文件全是【已签收 / 已被 main 独立复核】的件, ★**一个字都不许动**★**: ★**`MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` (ISS-377) · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (ISS-374) · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (ISS-371) · `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` (ISS-382) · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (ISS-276) · `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` (ISS-295) · `MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/service_port_check.py` (★`CRIT`/`TOL` 真身★)** ★ ⇒ ★**★它们全是【只读引用】★ ⇒ ★**★订正一律进你的【新页】, 不许回头改老页★ ★**
★**④ 零改既有闸** ⇒ ★**上面 §四 列的 8 个既有闸 md5 逐字节不变 (★`CRIT`/`TOL` 只许【读】, 不许改★)** ★
★**⑤ 零写 HW / SW 地界** ⇒ ★**`HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (ISS-379) / `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md` (ISS-383) 只读** ★
★**⑥ 零外发** ⇒ ★**★不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有「批一句可以发」这个选项**★ ★**
★**⑦ 不代拍** ⇒ ★★★**★① `J_DEBUG` 的「必须清空区 X 宽」以哪个数为准 (`OI-5`) ⇒ ★**你只摆三行事实 + 代价, 不许在页里写「应采用 X」**★ ★★★ **② `J_UART` 的落点三选一 ⇒ ★**已被 main 挂起, ★**你【不许】重开裁决, 只登记依赖**★ ★★★ **③ `J_DEBUG` 座体真实高 h = `[0数据]` ⇒ 按 Z 向保守上界 `4.70` 参数化, ★**不许猜高度**★ ★★★ ★**
★**⑧ 不自签 `state/issue_log.yaml`** ⇒ ★**签收归 main** ★
★**⑨ 只写本任务允许的文件** ⇒ ★**别写别人的分片 (`state/fragments/hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许动)** ★
★**⑩ 沙盒** ⇒ ★**只落 `tmp/iss386_sbx/` + `logs/iss386/`; ★**不许用 `cp -al` (★本项目吃过硬链接的亏★)** ★

---

## ★★六 · 交卷前的最后一道 (★按顺序做·★每件落盘后再做下一件★) ★★

★**① 先落真相页骨架** (★空壳也要先落盘·★宁可先落骨架再填★) ★**② 再落新闸 + 跑通 `--selftest`** ★**③ 再回头填真相页 + 跑闸** ★**④ 再落交卷页 (B1~B6)** ★**⑤ 最后写分片** ★**⑥ 跑 `python3 state/merge.py` (rc=0) + `python3 state/gate_check.py` (rc=0, Q1 18/18) + 把两行输出原样贴进回复** ★

★**★最后提醒 (★项目硬规矩 L-13★)★**: ★**你的第一个动作就是把那两份新文件 (真相页 + 新闸) 的骨架写出来落盘, 不许「想清楚了再一次性写」** ⇒ ★**本项目的墙在 12~16 分钟, 攒着写 = 零交卷** ★
