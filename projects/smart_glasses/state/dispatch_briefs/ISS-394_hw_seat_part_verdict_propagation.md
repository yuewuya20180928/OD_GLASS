# ISS-394 · hw-lead · HW 侧【「座体选型结论」只写在 issue_log 里, 没落到板侧真值页 / BOM 型号栏 / 闸的输入面 ⇒ 那一条被推翻的结论现在是【活的】】⇒ 把它变成机器可判

★**本单性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板那一趟·HW 侧选型结论传播自守层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单为什么必须做 (★main 本机实跑 · 不抄任何 agent 报告★) ★★**

★**① 板那一趟要填 BOM 型号栏 (`J_DEBUG` 行 71 / `J_UART` 行 77) ⇒ 型号栏此刻是 `待定` ⇒ 谁填、填什么, 决定了【板那一趟到底装哪颗件】★**
★★**② ★★而 `state/fragments/hw.yaml` 里那条【还没答】的 need `iss380_board_trip_bom_part_fill` (★`to=main`·`state` 未标已决★) 问的却是: 「★`J_DEBUG`/`J_UART` 按板侧真值档 (★`FTSH-104-01-F-DV` / `FTSH-102-01-F-DV`★) 还是 Cortex-10 2×5 档 (`FTSH-105-01-L-DV-K`) ?」⇒ ★★**这个问题里【没有一个选项是对的】 ⇒ 它【只能被答错】★** ★★**
★**③ ★★而 main 早在 2026-11-24 08:3x 就已经把那两个料号【推翻】了 (★main 本机实查厂商官网单品页标题 + Mouser/DigiKey 参数表★)**: ★**`FTSH-104-01-F-DV` 官网单品页标题逐字 = 「.050in/1.27mm Micro Header Strip, 8 Pin, 2 Row, SMT」+ DigiKey「Number of Positions 8 / Number of Rows 2 / Surface Mount」⇒ 【8 脚双排贴片】, 不是板侧要的单排直插★** ★
★★**④ ★★⇒ ★★**「推翻」这件事只写在 `state/issue_log.yaml` 的 `note_addendum` 里 (★main 签收 ISS-380 时写的★) ⇒ ★★**它没有落到任何一个【板那一趟会读的文件】上** ⇒ ⇒ ★★**板那一趟开工的人读的是 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`, 而那一页上 D-1 / U-1 至今仍写着「首选候选」★** ⇒ ⇒ ★**真相与活页面【不一致】⇒ 那一趟若照那一页填 BOM ⇒ 装上一颗 8 脚双排贴片 ⇒ 排针插不进 ⇒ 【板改两次】** ★★
★**⑤ ★★main 本机实读, 「活副本」不止一处, 至少 4 处 (★逐条给了行号★)**: ★★**(甲)** `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` L18 / L62 / L67 / L73 / L112 —— ★**D-1 / U-1 仍标「首选候选」, 且该页【零个「推翻 / 订正 / §㊳」字样】⇒ 读不到任何推翻痕迹★** · ★★**(乙)** `state/fragments/hw.yaml` L5271-5272 —— ★**那条【已闭】的 need `iss377_oi10_vendor_part_numbers` 的答案原文仍写「J_DEBUG 首选 Samtec `FTSH-104-01-F-DV` (1×4 1.27mm 直插)」⇒ 【一个已被推翻的结论被标成「已闭」⇒ 下游任何读分片的人都拿它当既成事实】★** · ★★**(丙)** `state/fragments/hw.yaml` L4346-4347 —— ★**那条【未答】的 need 问的选项【全是错的】⇒ 只能被答错★** · ★★**(丁)** `HW/check_debug_uart_seat_alignment.py` L397 —— ★**一个【已签收闸】的源码里, 把 `Samtec FTSH-104-01-F-DV` 硬编码成【BOM 型号栏的真源样本】⇒ 那道闸的 selftest 现在【教人填一颗被推翻的料号】★★**
★**⑥ ★★⇒ ★★**结论: 【推翻是「正确的」, 但它【没传播】⇒ 「板只改一次」那一趟的读数面【仍是错的】★ ⇒ 本单要做的不是再查一遍料号 (★ISS-380/383/387 已经查过三轮了★), 而是 ★**把「一条结论被推翻后, 它的活副本必须被点名」这件事变成机器可判**★**

---

## ★★一 · 本单的地界事实 (★main 本机实跑 · 逐条给了出处·★数字都可复现★) ★★

### ★★① `J_DEBUG` / `J_UART` 的 BOM 型号栏此刻是 `待定` (★main 本机实读 `HW/BOM_v1.csv`★) ★★

★**main 本机实跑命令**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -n '^J_DEBUG\|^J_UART' HW/BOM_v1.csv
```
★**读数 (逐字)**: ★★`J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,...` ★★
★★`J_UART,1,1×2 1.27mm 排针 (UART),CONN,可选,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,...` ★★
★**⇒ 型号栏两列都是 `待定` ⇒ 【这一趟还没落表】⇒ 现在纠正, 成本 = 改文档; 等落表后再纠正, 成本 = 【板改两次】★★**

### ★★② 活副本 ①: 型号真相页的 D-1 / U-1 仍标「首选候选」, 且该页零推翻痕迹 ★★

★**main 本机实跑命令**:
```bash
grep -n "FTSH" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md
grep -c "㊳\|推翻\|订正" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md
```
★**读数**: ★**FTSH 命中 6 行 (L18 / L62 / L63 / L67 / L73 / L112)** · ★**「推翻/订正/§㊳」命中 = `0`** ★
★★**L62 逐字 (截)**: `| D-1 | **Samtec** | **\`FTSH-104-01-F-DV\`** | ... | ★**排距 ✓ 脚数 ✓ (4 脚候选) · 直插 ✓** ⇒ ★**首选候选** | ... | ★**单排 1×4 的排布需在官网单品页二次确认 ⇒ 标 \`[推算]\`** |` ★★
★★**★★注意这一行的病: 它把【家族页】的推断 (`1.27 mm 直插 THT · 垂直 · 2~50 pins/row`) 当成了【这颗具体料号】的规格 ⇒ 而官网单品页标题写的是「8 Pin, 2 Row, SMT」⇒ 【家族属性被安到了具体件上】⇒ 「首选候选」这个结论【是靠一条家族页推出来的】★★**

### ★★③ 活副本 ②: `hw.yaml` 里那条【已闭】的 need 答案原文仍指向被推翻的料号 ★★

★**main 本机实跑命令**:
```bash
grep -n "iss377_oi10_vendor_part_numbers" state/fragments/hw.yaml
sed -n '5269,5276p' state/fragments/hw.yaml
```
★**读数 (逐字)**: ★**`value: 'OI-10 已闭: J_DEBUG 首选 Samtec FTSH-104-01-F-DV (1×4 1.27mm 直插), J_UART 首选 Samtec FTSH-102-01-F-DV (1×2 1.27mm 直插); 另有 Cortex-10 2×5 档 FTSH-105-01-L-DV-K 与 Würth 61300411121 / ...'` ★★ · `ref: HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` ★
★★**⇒ 「已闭」+ 「首选」+ 指向一个已被推翻的料号 ⇒ 这是本单最危险的一条: 【它不是【未决】, 它是【已决且决错了】】★★**

### ★★④ 活副本 ③: `hw.yaml` 里那条【未答】的 need, 选项全是错的 ★★

★**main 本机实跑命令**:
```bash
grep -n "iss380_board_trip_bom_part_fill" state/fragments/hw.yaml
```
★**读数 (逐字)**: ★**`item: '板那一趟的 BOM 型号栏: J_DEBUG/J_UART 按板侧真值档 (FTSH-104-01-F-DV / FTSH-102-01-F-DV) 还是 Cortex-10 2×5 档 (FTSH-105-01-L-DV-K)? 另: 结构侧那三条不自洽点 (脚数 / 相对位置 / 座体真实高度) 谁去重算?'` ★★ · `to: main` · `answers: None` ★
★★**⇒ 三个选项: ① 双排贴片 (已被推翻) ② 双排贴片 2×5 (脚数与排布都不对) ⇒ 【没有一个满足板侧真值「1×4 / 1×2 · 单排 · 直插」】⇒ 【这条 need 现在只能被答错】★★**

### ★★⑤ 活副本 ④: 一个【已签收闸】的源码里, 硬编码了被推翻的料号当【真源样本】 ★★

★**main 本机实跑命令**:
```bash
grep -n "FTSH" HW/check_debug_uart_seat_alignment.py
sed -n '393,400p' HW/check_debug_uart_seat_alignment.py
```
★**读数 (逐字)**: ★★**L397**: `"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTSH-104-01-F-DV,")` ★★
★★**它的用途 (L394-399 逐字)**: ★**「K3 反向: BOM 真源被落表 (型号栏被填上料号)」⇒ ★★它把「填上 `Samtec FTSH-104-01-F-DV`」当成【BOM 被落表】的【正样本】⇒ ★★**这道闸的 selftest 现在【在教人填一颗被推翻的料号】★★ ⇒ ★**它自己不红 (它判的是「有没有新料号冒出来」, 不是「这颗料号对不对」) ⇒ 这是【闸判绿 + 事实错】的又一处★★**

### ★★⑥ 对照组: 同一族已经有【一道把族别钉死】的闸 (`HW/check_fts_single_row_land_truth.py` K4) ⇒ 【本单不是从零造, 是把已有的命门复制到另一族/另一面】 ★★

★**main 本机实跑命令**:
```bash
grep -n "FTSH" HW/check_fts_single_row_land_truth.py | head
python3 HW/check_fts_single_row_land_truth.py ; echo "rc=$?"
```
★**读数**: ★**L21/L29-30/L454/L463-477 都在打「FTSH 是双排, 族不同, 不许顶替 FTS」· L83 `FTSH_RE = re.compile(r"FTSH", re.I)`** ★
★★**★⇒ 命门在【FTS 那一族】已经钉死了 (★且 ISS-387 已 verified★) ⇒ ★★**缺的是【另一族那一面】: 「`FTSH` 这个族本身被用作单排直插首选」这件事, 至今【没人判红】★ ⇒ 本单要补的就是这一格 ★★**

### ★★⑦ 对照组 ②: ISS-380 那道闸 (`HW/check_debug_uart_seat_truth.py`) 现在【裸跑 rc=0 全绿 6/6】⇒ 【它也不抓这条】 ★★

★**main 本机实跑命令**:
```bash
python3 HW/check_debug_uart_seat_truth.py ; echo "rc=$?"
```
★**读数**: ★**`[GRN ] K0~K5` + `RESULT: K0~K5 全绿 (6/6)` + `rc=0`** ★
★★**main 本机实读它的 `k1` 源码 (L218-244)**: ★★它只查三件事 —— ①§2 候选行有没有像样的完整料号 ②有没有官网 URL ③有没有证据等级 ★★**⇒ 它【不查那颗料号对不对】⇒ D-1 那行【三样都有】⇒ 照样绿 ★★ ⇒ ★★**「有 URL 有等级」不等于「料号对」⇒ 这就是那道闸的盲区★★**

### ★★⑧ 正确的方向已经有人在盘上查到了 (★你本单要独立复核, 不许只抄★) ★★

★**main 本机实读 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` (★ISS-387 已 verified★)**:
★**L14**: ★**`FTS-104-01-F-S` = 4 位 / 1 排 / 直插 / 排距 1.27 mm, `FTS-102-01-F-S` = 2 位 / 1 排 / 直插 / 排距 1.27 mm —— 两个料号都真实存在、都在售、都是【单排直插】** ★
★**L235 / L236**: ★**`J_DEBUG` (行 71) ⇒ `FTS-104-01-F-S` (Samtec · 4 位 1 排 直插 · 1.27 mm) + land = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` + ★**孔径改 `0.71`** + ★**偏离 D-1/D-2/D-3 登记** · `J_UART` (行 77) ⇒ `FTS-102-01-F-S` + land = `PinHeader_1x02_P1.27mm_Vertical` + 孔径改 `0.71`** ★
★★**★⇒ 【正确方向已经查清并落在盘上】⇒ 本单【不是要你再查一遍料号】⇒ 本单要查的是【这条正确结论有没有传到那 4 处活副本】⇒ ★★**

---

## ★★二 · 本单要交 4 件 (★就这 4 件·不要顺手多跑别的★) ★★

### ★★① 新建真相页: `HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md` (★新建★) ★★

★**必须含这 6 节 (§0~§5), 每节都要有实测读数, 不许写「应该」**:

| § | 内容 | 必须含 |
|---|---|---|
| ★**§0** ★ | ★**一句话结论** ★ | ★**「选型结论已被推翻, 但推翻只写在 `state/issue_log.yaml` 的 `note_addendum` 里 ⇒ 活页面/分片/闸源码 三处仍在说旧话 ⇒ 板那一趟的读数面是错的」★** |
| ★**§1** ★ | ★**被推翻的结论是什么 (★附证据等级 + 出处★)** ★ | ★**`FTSH-104-01-F-DV` = 「8 Pin, 2 Row, SMT」· `FTSH-102-01-F-DV` = 「4 Pin, 2 Row, SMT」⇒ 【双排贴片】· 证据等级 `[官网]` (厂商官网单品页标题) + `[媒体]` (DigiKey 参数表) · ★**且必须注明: 这是 ISS-380 交卷页 §2 的「家族属性被安到具体件上」的病根**★** |
| ★**§2** ★ | ★**活副本清账表 (★逐条给文件 + 行号 + 逐字原文 + 它错在哪★)** ★ | ★**4 条: (甲) 型号真相页 L18/L62/L67/L73/L112 · (乙) `hw.yaml` L5271-5272 已闭答案 · (丙) `hw.yaml` L4346-4347 未答 need · (丁) `check_debug_uart_seat_alignment.py` L397 硬编码样本 · ★**每条都要写清【谁有权改它】(= main) + 【改成什么】(你只给草案, 不代落)**★** |
| ★**§3** ★ | ★**正确结论现状 (★你本单要独立复核, 不许只抄 ISS-387★)** ★ | ★**`FTS-104-01-F-S` / `FTS-102-01-F-S` 单排直插 + 官网证据 + 官网 CAD 链接拿不到时的降级方案 · 必含: 【座体高/尾长/总长 仍是 `[0数据]` 吗?】(★ISS-387 L43 自己写的是 `[媒体]` 查 DigiKey ⇒ 你要独立复核到底有没有拿到官网一手值★) ★** |
| ★**§4** ★ | ★**那 4 处各自【改了会引发什么】+ 代价 (★只摆代价, 不代拍★)** ★ | ★**尤其: (乙) 那条是【已闭】的 ⇒ 改它要不要重开 need? (丁) 那处在一个【已签收闸】的源码里 ⇒ 改它算不算动已签收件? ⇒ ★★**这两条的地界判断是 main 的, 你只摆选项 + 代价 + 你能查到的先例★★** |
| ★**§5** ★ | ★**复跑命令 (★原样可粘贴★)** ★ | ★**§6 里那些命令逐条列出来★** |
| ★**§6** ★ | ★**机器块 (★`--emit` 可解析★)** ★ | ★**至少 15 键: `refuted_parts` / `refuted_reason` / `correct_parts` / `live_copies` (每条含 file/line/quote/kind) / `unanswered_need_key` / `board_md5` / `netlist_md5` / `pins_md5` / `bom_md5` / `evidence_grades` / `degradation_plan` / `not_decided_here` (★**全部 `not_decided_here`★) 等 ★ |

### ★★② 新建机器闸: `HW/check_seat_part_verdict_propagation.py` (★新建★) ★★

★**判据 K0~K6 (每条 fail-closed + 每条至少一条反向用例)**:

| # | 判据 | 必须查到什么 |
|---|---|---|
| ★**K0** ★ | ★**板三项 + 三张表三项指纹未动 (★`md5` / `mtime` / `size` 都要比★)** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` / `mtime=2026-11-06 07:07:17.362193413` / `size=4940213` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★**⇒ 任何一条动了就判红**★ |
| ★**K1** ★ | ★**被推翻的料号【不许再以「首选候选」身份活在任何活副本里】 ★** | ★**扫 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` + `state/fragments/hw.yaml` + `HW/check_debug_uart_seat_alignment.py` ⇒ ★**凡出现 `FTSH-104-01-F-DV` / `FTSH-102-01-F-DV` 且【同句/同行】含「首选」或 `1×4`/`1×2` + 「直插」的组合 ⇒ 判红并点名文件+行号★** ★**★⇒ 注意: 本单【新建的真相页】自己会提到这两个料号 (那是【记账】, 不是【当首选】) ⇒ 你的匹配式必须能区分【记账语境】与【当首选语境】⇒ ★★**你自己写闸时就要处理掉这个自指问题, 并在交卷页写明你怎么处理的★**★★** |
| ★**K2** ★ | ★**任何「已闭」的 need, 其答案不许指向被推翻的料号 ★** | ★**扫 `state/fragments/hw.yaml` 的 `answers` ⇒ ★**`state=answered`/有 `answers[]` 且答案文本含被推翻的料号 + 「首选」⇒ 判红★** |
| ★**K3** ★ | ★**任何「未答」的 need, 它的选项里必须至少有一个【满足板侧真值档】的选项 ★** | ★**扫 `needs_from` 里 `to=main` 且无 `answers` 的项 ⇒ ★**若某条 need 的 `item` 同时提到 `J_DEBUG`/`J_UART` 且列出的候选料号【全部】不满足「1×4/1×2 · 单排 · 直插」⇒ 判红 (★现状【必然红】⇒ 这是【本单要暴露的现状】, 不是你的闸故障★ ⇒ ★★**你要在交卷页写明【K3 正向跑是红的, 因为现状就是这样; 等 main 落完订正块它才转绿】★★** ⇒ **不许为了让它绿而放宽判据**) ★ |
| ★**K4** ★ | ★**正确结论必须被登记 (且带证据等级) ★** | ★**`FTS-104-01-F-S` / `FTS-102-01-F-S` 必须在你的真相页机器块里 + 各自带 `[官网]`/`[媒体]` 等级 ⇒ ★**且 `not_decided_here` 必须全为 `not_decided_here` ⇒ 你不许代拍选型★** |
| ★**K5** ★ | ★**证据等级 + 零挂起 + 零挂链 + 判据句与事实句分开 (★照本仓既有闸的同款写法★)** ★ | ★**`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 五级白名单 · 「等原厂回信 / 待外部确认」等挂起措辞一律判红 (★口径: ★**本项目已定「不再外发, 全靠自己查」⇒ 挂起措辞一律当病★) · ★**`grep -c check_seat_part_verdict_propagation state/gate_check.py` = 0 (零挂链) · 判据句与事实句分开★★** |
| ★**K6** ★ | ★**既有件零扰动自证 ★** | ★**开工前/交卷后逐字比对: ★**板三项 + 三张表 + `HW/check_fts_single_row_land_truth.py` + `HW/check_debug_uart_seat_truth.py` + `HW/check_debug_uart_seat_alignment.py` + `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` + `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md` + `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` ★**—— ★★**这 3 个闸和这 3 个页都是【已签收件】⇒ 你【一个字都不许改】⇒ 你的新闸只读它们★★** |

★**`--selftest` 要求**: ★**≥10 条反向用例, 每条自证「红的是目标那一条、其余仍绿」** · ★**末行必须逐字 `ALL TESTS PASS`** · ★**其中至少 3 条专打 K1/K2/K3 的漏项** (★例: 把 K1 的匹配式放宽成「文件里出现 FTSH 就红」⇒ 必须被你的用例抓住 ⇒ 否则说明你的闸会误报自己新建的记账页★)

### ★★③ 交卷页: `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` (★新建★) ★★

★**B1~B6 六段, 六个 `##` 标题必须命中 `state/gate_check.py` 认的关键词**:
★**B1** 结论 (★一句话 + 4 处活副本逐条一句话★) · ★**B2** 真相页 (★路径 + 指纹 + 规模 + §0~§6★) · ★**B3** 新闸 (★路径 + 指纹 + 规模 + K0~K6 + `--selftest` 用例数★) · ★**B4** 边界自证 (★板三项指纹 + 三张表 + 既有 6 件零扰动 + 零挂链 + 零外发 + 不代拍 + 不写别人的分片★) · ★**B5** 要 main 回话的 (★每条带代价, 只登记不代拍★) · ★**B6** 必跑命令原样输出 (★含正向跑的实际读数 + ★★**K3 正向红是预期, 要写明为什么是预期★**★)**

### ★★④ 分片: `state/fragments/hw.yaml` ★★

★**必须走 `python3 state/frag_write.py --agent hw-lead` (★禁止 `open(p,"w")`★)**:
★**产出物 ≥3 条** (真相页 + 新闸 + 交卷页) · ★**`interface_claims` ≥4 条** (★每条含: 被推翻的料号 / 正确的料号 / 落表影响面 (J_DEBUG 行 71 / J_UART 行 77) / 改孔动作 (★`0.65 → 0.71`·★与 ISS-391 交叉引用★)★) · ★**`needs_from` ≥5 条 `to=main`** (★★**其中必须包含一条: 「那 4 处活副本分别由谁改 / 什么时机改 / (丁) 那处在已签收闸的源码里, 动它算不算动已签收件」—— ★★这三条地界你只摆代价, 不代拍★) ★**
★**写完 `grep` 复验条目唯一 (★不许出现重复 key★)**

---

## ★★三 · 边界 (★违反就是不合格★) ★★

| # | ★**不许** ★ | 说明 |
|---|---|---|
| ★**1** ★ | ★**不许写板 / 改板** ★ | ★**板 `611b869e…` 的 md5 / mtime / size 逐字节未动 ★** |
| ★**2** ★ | ★**不许落表** ★ | ★**`HW/BOM_v1.csv` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 逐字节未动 ⇒ ★**BOM 型号栏还是 `待定` (★那是 main 那一趟的事★)★** |
| ★**3** ★ | ★**不许改既有页面正文** ★ | ★**尤其 ★★`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` / `..._ALIGNMENT.md` / `..._FTS_SINGLE_ROW_LAND_TRUTH.md` ★★ —— ★★**你只【登记】那 4 处该怎么改, 【不许自己改】★** |
| ★**4** ★ | ★**不许改既有闸** ★ | ★**尤其 ★★`HW/check_fts_single_row_land_truth.py` / `HW/check_debug_uart_seat_truth.py` / `HW/check_debug_uart_seat_alignment.py` ★★ —— ★★**K4 的命门已经在那道闸里, 你不许动它; 你只【新建】另一面的闸★** |
| ★**5** ★ | ★**不许挂链** ★ | ★**`grep -c check_seat_part_verdict_propagation state/gate_check.py` = 0 ⇒ 挂不挂是 main 的地界 ★** |
| ★**6** ★ | ★**不许外发** ★ | ★**零邮件 / 零询价 / 零问询 / 零采购 ⇒ `state/outbox/` 不动 ⇒ ★**查不到就写 `[0数据]` + 降级方案★** |
| ★**7** ★ | ★**不许代拍** ★ | ★**选型 / 落表 / 改页 / 改已签收闸 / 改那 4 处, 五条全是 main 的地界 ⇒ 你只摆代价 ★** |
| ★**8** ★ | ★**不许写别人的分片** ★ | ★**只写 `state/fragments/hw.yaml` (走 `frag_write.py`)★** |
| ★**9** ★ | ★**不许碰 MECH / SW 的文件** ★ | ★**MECH 侧判决链重算 = ISS-393 (mech-lead 在飞) · SW 侧 = ISS-392 (sw-lead 在飞) ⇒ 你的只写 `HW/` + `HANDOFF/` + `hw.yaml` ★** |
| ★**10** ★ | ★**不许重查料号** ★ | ★**选型本身 ISS-380/383/387 已查过三轮 ⇒ 你只【独立复核 §3 那一句】, 其余照抄盘上已签收件即可 (★但要标 `[实测]` 说清是你复核的★)★** |

---

## ★★四 · 交卷前必跑 (★原样输出贴进交卷页 B6 · 期望值写在后面★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 新闸正向跑 (★K3 红是【预期】, 其余绿★)
python3 HW/check_seat_part_verdict_propagation.py            # rc=1 ★预期★ · K0~K2/K4~K6 绿 · K3 红(现状即如此)

# ② 新闸自测
python3 HW/check_seat_part_verdict_propagation.py --selftest  # rc=0 · 末行逐字 ALL TESTS PASS · ≥10 条反向用例

# ③ 既有闸逐条复跑 (★必须与开工前读数【逐字相同】, 证明你没动它们★)
python3 HW/check_fts_single_row_land_truth.py             # rc=0 · 读数不变
python3 HW/check_debug_uart_seat_truth.py                 # rc=0 · 读数不变
python3 HW/check_debug_uart_seat_alignment.py             # rc=0 · 读数不变

# ④ 板三项 + 三张表零扰动
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n mtime=%y size=%s' HW/PCB/demo_mainboard.kicad_pcb

# ⑤ 零挂链
grep -c check_seat_part_verdict_propagation state/gate_check.py    # 0

# ⑥ 分片 (★只走 frag_write.py★)
python3 state/frag_write.py --agent hw-lead

# ⑦ 收尾
python3 state/merge.py                                  # rc=0
python3 state/gate_check.py                             # rc=0 · 【Q1 交付齐备率 18/18】
```

★**★收尾硬要求 (★照抄本仓既有单的口径★)★**: ★**`merge.py` 的 rc 必须 0** · ★**`gate_check.py` 的 rc 必须 0 且 【Q1 交付齐备率】必须 18/18** ★★**⇒ 你交卷页 B6 里要把这两条的【原样输出】贴进去 (★失败就不许交卷★)★★**

---

## ★★五 · 一句话 (★本单到底在回答什么★) ★★

★★**★「一颗已经被推翻的料号, 现在还以『首选』的身份活在 4 处文件里 (真相页 / 已闭答案 / 未答 need 的选项 / 一个已签收闸的 selftest 样本) ⇒ 板那一趟 whoever 照着填 BOM, 就会装错件 ⇒ 板改两次」⇒ ★★**本单把「一条结论被推翻后, 它的活副本必须被点名并被改掉」这件事变成机器可判 (K1/K2/K3 三条判据), 并把「正确结论 (FTS-104-01-F-S / FTS-102-01-F-S) 现在传到了哪」清成一张账 ★★** ★

---

## ★★六 · 额外纪律 (★本 job 固定抬头, 原文照抄★) ★★

★① ★**写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`)** ★
★② ★**只写本任务允许的文件, 不碰别人的** ★
★③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★
★④ ★**不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
★⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
