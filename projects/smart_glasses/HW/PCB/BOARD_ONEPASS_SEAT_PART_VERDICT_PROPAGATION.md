# 「座体选型结论」传播自守层真相页 (ISS-394 · hw-lead · 2026-11-24)

> ★**触发源**: ★**main 2026-11-24 08:3x 签收 ISS-380 时推翻了两个「首选候选」料号** (`FTSH-104-01-F-DV` / `FTSH-102-01-F-DV` ⇒ 官网单品页标题写的是【双排贴片】, 不是板侧要的【单排直插】) ⇒ ★**但那个「推翻」只写在 `state/issue_log.yaml` 的 `note_addendum` 里** ⇒ ★**它没有落到任何一个【「板只改一次」那一趟会读的文件】上** ⇒ ⇒ ★**真相与活页面【不一致】⇒ 那一趟 whoever 照着活页面填 BOM 型号栏 ⇒ 装上一颗 8 脚双排贴片 ⇒ 排针插不进 ⇒ 【板改两次】** ★
>
> ★**本单性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★
>
> ★**本单不许重查料号**: ★**选型本身 ISS-380 / 383 / 387 已查过三轮** ⇒ ★**本单只【独立复核 §3 那一句】+ 把「一条结论被推翻后, 它的活副本必须被点名」变成机器可判** ★

---

## §0 一句话结论

★★**选型结论已被推翻, 但推翻只写在 `state/issue_log.yaml` 的 `note_addendum` 里 ⇒ 活页面 / 分片 / 已签收闸源码 五处仍在说旧话 ⇒ 板那一趟的读数面是错的**★★

★**一句话展开**: ★**`FTSH-104-01-F-DV` / `FTSH-102-01-F-DV` 被 main 推翻 (2026-11-24 08:3x) · 本单本机独立复核成立 (§1) ⇒ 但 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` L18/L62/L67/L73/L112 仍写「首选候选」· `state/fragments/hw.yaml` L5271-5272 那条【已闭】答案仍写「首选」· 同文件 L4346-4347 那条【未答】need 的选项【全是错的】· 同文件 L8097 的 `interface_claims.note` 仍写「首选」· `HW/check_debug_uart_seat_alignment.py` L397 仍把被推翻的料号当【BOM 真源样本】⇒ ⇒ **5 处活副本 ⇒ BOM 型号栏此刻还是 `待定` ⇒ 现在纠正成本 = 改文档; 等落表后再纠正 = 装错件 = 【板改两次】** ★**

★**本单交三件 + 一份分片**: ★**① 本页 (新建) · ② `HW/check_seat_part_verdict_propagation.py` (新建闸 K0~K6) · ③ `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` (交卷页 B1~B6) · ④ `state/fragments/hw.yaml` 分片登记 (只走 `state/frag_write.py`)** ★

---

## §1 被推翻的结论是什么 (★附证据等级 + 出处★)

### §1.1 被推翻的料号与它们的真实规格

| 料号 | 官网单品页标题 (逐字) | 真实规格 | 证据等级 | 本单复现方式 |
|---|---|---|---|---|
| ★**`FTSH-104-01-F-DV`** ★ | ★**`.050in/1.27mm Micro Header Strip, 8 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post - FTSH-104-01-F-DV`** ★ | ★**8 位 / 双排 / 贴片 (SMT)** ★ ⇒ ★**与板侧真值「1×4 单排直插」在【脚数 / 排布 / 型态】三格全错** ★ | ★`[官网]` ★ | ★**本机 2026-11-24 15:0x `curl` 实抓** `https://www.samtec.com/products/ftsh-104-01-f-dv` ⇒ HTTP `200` · `161297` B · 落 `tmp/iss394_sbx/ftsh104.html` · `<title>` 逐字见上 ⇒ ★`[实测]` (本机实抓) ★ |
| ★**`FTSH-102-01-F-DV`** ★ | ★**`.050in/1.27mm Micro Header Strip, 4 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post - FTSH-102-01-F-DV`** ★ | ★**4 位 / 双排 / 贴片 (SMT)** ★ ⇒ ★**与板侧真值「1×2 单排直插」在【脚数 / 排布 / 型态】三格全错** ★ | ★`[官网]` ★ | ★**本机直抓 `https://www.samtec.com/products/ftsh-102-01-f-dv` ⇒ 连试 2 次 HTTP `429` (Cloudflare 1015 限流) ⇒ 降级读【盘上已签收页 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md` L47 的逐字记录 + 官网 URL】⇒ ★`[实测]` (本机复读已签收件) + ★`[官网]` (该记录所引官网标题) ★ |

★**第二来源 (分销参数表)**: ★**DigiKey `FTSH-104-01-F-DV` 参数表逐字「Number of Positions 8 / Number of Rows 2 / Surface Mount」+ 「CONN HEADER SMD 8POS」** ⇒ 与官网标题一致 ⇒ ★`[媒体]` ★
★**本机本轮直抓 DigiKey / Mouser 的实测**: ★**DigiKey ⇒ HTTP `403` (Cloudflare challenge 「Just a moment...」) · Mouser ⇒ HTTP `200` 但正文是「Access Denied ... we believe you are using automation tools」⇒ ⇒ ★**本轮本机【没有独立复现】分销参数表** ⇒ ★**该条按 ISS-383 已签收页的记录引用, 证据等级 `[媒体]`, 并标「本机本轮未复现 (分销站反爬)」** ★

### §1.2 病根: ★**「家族属性被安到具体件上」** ★

★**ISS-380 §2 的 D-1 / U-1 那一行 (L62 / L73) 的证据栏写的是**: ★**`[官网]` (家族页明确 "1.27mm · SMT 与 THT 两种 · 垂直与直角")** ⇒ ★**那一栏的 URL 是 `https://www.samtec.com/products/ftsh` (★**家族页★)** ⇒ ★**家族页给的是【族属性】(1.27 mm · SMT 与 THT 两种 · 垂直与直角 · 2~50 pins/row) ⇒ 而【具体料号的脚数 / 排布 / 型态】必须回【单品页】查 ⇒ ★**家族页【证不了】单排 1×4 这件事 ⇒ ⇒ ★**「首选候选」这个结论【是靠一条家族页推出来的】⇒ 这是本条被推翻的病根** ★**

★**同页 L18 那一行也有同一处病**: ★**`Samtec FTSH-1xx-01-F-DV` (1.27 mm 直插排针家族)** ⇒ ★**它把「FTSH 家族 = 直插排针家族」当成了事实陈述 ⇒ 而本单 §1.1 实测: ★**FTSH 家族在 1.27 mm 下有双排直插 (`-D`) / 双排垂直贴片 (`-DV`) / 双排水平贴片 (`-DH`) / 混装 (`-MT`) 四种, 单排直插【不在该族】** ★

### §1.3 推翻记录现在只在哪 (★活页面里零痕迹★)

| 位置 | 内容 | 读数 |
|---|---|---|
| ★**`state/issue_log.yaml` L22010 (`ISS-380` 的 `note_addendum`)** ★ | ★**main 2026-11-24 08:3x 的推翻原文 (逐字摘)** ★ | ★**「① ★**§2 的 D-1 / U-1 两个「首选候选」判定被推翻** —— `FTSH-104-01-F-DV` 官网单品页标题 =「.050in/1.27mm Micro Header Strip, **8 Pin, 2 Row, SMT**」... ⇒ ★**§2.3 结论 2-1「唯一同时满足三要素的候选是 D-1」不成立** ⇒ ★**这两个料号不得当 1×4/1×2 单排直插件落表**」** ★ |
| ★**`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`** ★ | ★**推翻痕迹 = 0** ★ | ★**本机实跑 `grep -c "㊳\|推翻\|订正" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` ⇒ `0`** ★`[实测]` ★ |

★**⇒ ★**那条「推翻」是【对的】, 但它【没传播】⇒ 板那一趟的读数面【仍然是错的】★★ ★

---

## §2 活副本清账表 (★逐条给文件 + 行号 + 逐字原文 + 它错在哪 + 谁有权改 + 改成什么★)

★**本表是「记账」表 —— 本页提到被推翻的两个料号, 全部是【记账语境】(记「它被推翻了」), 不是【当首选】⇒ ★**本页自己被闸 K1 扫到时, 每一处都带明确的证伪标记 ⇒ 详见 §6.1 的自指处理说明** ★

| # | 文件 | 行 | 逐字原文 (截) | 它错在哪 | ★谁有权改★ | ★改成什么 (草案 · 不代落)★ |
|---|---|---|---|---|---|---|
| ★**(甲)** ★ | ★**`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`** ★ | ★**L18** ★ | ★`` `J_DEBUG` 侧查实 **Samtec FTSH-1xx-01-F-DV** (1.27 mm 直插排针家族) `` ★ | ★**把「FTSH 家族 = 直插排针家族」当事实写** ⇒ 该族在 1.27 mm 下没有单排直插件 (§1.2) ★ | ★**main** ★ | ★**追加式订正块**: ★**划掉「直插排针家族」这一族属性表述, 改成「双排族 (直插 `-D` / 垂直贴片 `-DV` / 水平贴片 `-DH` / 混装 `-MT`)」+ 指向 ISS-383 §1.1/§1.2 与本页 §1** ★ |
| ★**(甲)** ★ | ★**同上** ★ | ★**L62** ★ | ★`` | D-1 | **Samtec** | **`FTSH-104-01-F-DV`** | ... | ★**排距 ✓ 脚数 ✓ (4 脚候选) · 直插 ✓** ⇒ ★**首选候选** | ... `` ★ | ★**四格全错**: ★**脚数 8≠4 · 排布双排≠单排 · 型态贴片≠直插** ⇒ 且这一行的证据栏用的是【家族页】⇒ **「首选候选」是靠一条家族页推出来的** ★ | ★**main** ★ | ★**追加式订正块**: ★**D-1 整行标「★**已被推翻 (ISS-394 §1) ⇒ 不得当落表件**」+ 脚数/排布/型态三格改成实测值 + 证据栏换成单品页 URL + 家族页降级为「族属性参考」** ★ |
| ★**(甲)** ★ | ★**同上** ★ | ★**L67** ★ | ★**`按板侧真值 (1×4 · 1.27 mm · 直插), 唯一同时满足三要素的候选是 `FTSH-104-01-F-DV` (D-1)`** ★ | ★**★已被推翻★: §2.3 结论 2-1 本身不成立** ⇒ 这一句是【下游全都会抄的那一句】 ★ | ★**main** ★ | ★**追加式订正块**: ★**划掉「唯一同时满足三要素的候选是 D-1」⇒ 改成「★**本族内无单排直插件; 满足板侧真值档的件在 FTS 族 (`FTS-104-01-F-S`, 见 ISS-387) ⇒ 但落表归 main**」** ★ |
| ★**(甲)** ★ | ★**同上** ★ | ★**L73** ★ | ★`` | U-1 | **Samtec** | **`FTSH-102-01-F-DV`** | ... | ★**排距 ✓ 脚数 ✓ (2 脚候选) · 直插 ✓** ⇒ ★**首选候选** `` ★ | ★**同 L62, 四格全错** ★ | ★**main** ★ | ★**同 L62 的处置** ★ |
| ★**(甲)** ★ | ★**同上** ★ | ★**L112** ★ | ★**`J_DEBUG` → `FTSH-104-01-F-DV` (D-1) / `J_UART` → `FTSH-102-01-F-DV` (U-1): 二者都落在板侧真值的「1.27 mm 直插」档内`** ★ | ★**这是【落表建议】那一格 ⇒ 若被抄 ⇒ BOM 型号栏直接填错件** ★ | ★**main** ★ | ★**追加式订正块**: ★**整行标「★**已被推翻 (ISS-394 §1) ⇒ 不得落表**」+ 指到 ISS-387 的 FTS 档** ★ |
| ★**(乙)** ★ | ★**`state/fragments/hw.yaml`** ★ | ★**L5271-5272** ★ | ★**`value: 'OI-10 已闭: J_DEBUG 首选 Samtec FTSH-104-01-F-DV (1×4 1.27mm 直插), J_UART 首选 Samtec FTSH-102-01-F-DV (1×2 1.27mm 直插); ...'`** ★ (key = `iss377_oi10_vendor_part_numbers` · 段 = `answers` · `to: main` · `ref: HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`) ★ | ★★★**本单最危险的一条**: ★**它是【已闭】(有 `answers[]` 条目) + 写「首选」+ 指向一个已被推翻的料号 ⇒ ⇒ 【它不是【未决】, 它是【已决且决错了】⇒ 下游任何读分片的人都拿它当既成事实】** ★ | ★**main** ★ | ★**追加式订正块 (★见 §4-② 的地界问题: 改一条已闭答案要不要重开 need★)** ★ |
| ★**(丙)** ★ | ★**`state/fragments/hw.yaml`** ★ | ★**L4346-4347** ★ | ★**`item: '板那一趟的 BOM 型号栏: J_DEBUG/J_UART 按板侧真值档 (FTSH-104-01-F-DV / FTSH-102-01-F-DV) 还是 Cortex-10 2×5 档 (FTSH-105-01-L-DV-K)? 另: 结构侧那三条不自洽点 (脚数 / 相对位置 / 座体真实高度) 谁去重算?'`** ★ (key = `iss380_board_trip_bom_part_fill` · 段 = `needs_from` · `to: main` · **无 `answers`** ⇒ 未答) ★ | ★**三个选项【没有一个是对的】**: ★**① 双排贴片 (已被推翻) · ② 双排贴片 2×5 (脚数与排布都不对) ⇒ ⇒ 【这条 need 现在只能被答错】** ★ | ★**main** ★ | ★**追加式订正块**: ★**选项换成「板侧真值档 = `FTS-104-01-F-S` / `FTS-102-01-F-S` (1×4 / 1×2 · 单排 · 直插)」+ 保留结构侧那三问** ★ |
| ★**(丁)** ★ | ★**`HW/check_debug_uart_seat_alignment.py`** ★ | ★**L397** ★ | ★**`"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTSH-104-01-F-DV,")`** ★ | ★**它在一个【已签收闸】的源码里, 把被推翻的料号硬编码成【BOM 真源样本】⇒ ⇒ ★**这道闸的 selftest 现在【在教人填一颗被推翻的料号】⇒ 且它自己不红** (★它判的是「有没有新料号冒出来」, 不是「这颗料号对不对」⇒ ⇒ **闸判绿 + 事实错**) ★ | ★**main** ★ | ★**改 L397 的样本料号为 `Samtec FTS-104-01-F-S` (★或任何非被推翻料号★) ⇒ ★**但这动的是【已签收件】⇒ 见 §4-②** ★ |
| ★**(戊)** ★ | ★**`state/fragments/hw.yaml`** ★ | ★**L8096-8099** ★ | ★**`note: J_DEBUG 首选 Samtec FTSH-104-01-F-DV, J_UART 首选 Samtec FTSH-102-01-F-DV, 每条带官网链接`** ★ (key = `iss380_seat_part_truth` · 段 = `interface_claims` · `ref: HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`) ★ | ★★★**本单新发现的第 5 处活副本**: ★**`interface_claims` 是【接口取值声明】那一面 ⇒ 下游读「接口取值」的人拿到的就是「首选 FTSH-104-01-F-DV」⇒ ⇒ **机器可读面也还在说旧话** ★ | ★**main** ★ | ★**追加式订正块**: ★**`note` 改成「★**这两个首选候选已于 2026-11-24 08:3x 被推翻 (ISS-394 §1) ⇒ 不得落表; 满足板侧真值档的件见 ISS-387 的 FTS 档**」** ★ |

★**对照: 不是活副本的 (读数已正确, 不在清账表里)**:

| 文件 | 为什么不算活副本 |
|---|---|
| ★**`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md`** (ISS-383, 已签收) ★ | ★**它已经把推翻写进去了**: ★**L19 「`FTSH-104-01-F-DV` = Samtec 官网单品页标题「...**8 Pin, 2 Row, SMT**...」」· L35 「脚数 `8 Pin` (不是 1×4 的 4 脚)」· L185/L186 两条 `CONFLICT` 登记 · L222/L230 「★**丙 (ISS-380 原首选 · 本单已证伪其排布/型态)**」** ⇒ ★**它【读得到推翻痕迹】⇒ 不在清账表里** ★`[实测]` |
| ★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md`** (ISS-387, 已签收) ★ | ★**L211 「★**ISS-380 §2 的 D-1 / U-1 (`FTSH-104-01-F-DV` 等) 已被 §㊳ 发现一推翻 (双排贴片), 本单【不碰它们】**」** ⇒ ★**读得到推翻痕迹** ★`[实测]` |
| ★**`state/fragments/hw.yaml` L8130 (`interface_claims` key = `iss383_vendor_part_real_spec`)** ★ | ★**它写的是「D-1 FTSH-104-01-F-DV = 8Pin 2Row SMT ... ⇒ ★**ISS-380 登记的两个首选候选件不可直接落表**」** ⇒ ★**说对了** ★`[实测]` |
| ★**`state/issue_log.yaml` L22010** ★ | ★**推翻的【原始出处】本身** ⇒ ★**它是真源, 不是活副本** ★`[实测]` |
| ★**`HW/check_fts_single_row_land_truth.py` L690-701** ★ | ★**它把 `FTSH-104-01-F-DV` 当【反例】塞进 FTS 料号字段 ⇒ 判红 ⇒ ★**是【正确的族别守卫】, 不是活副本** ★`[实测]` |

★**⇒ 清账结果**: ★**5 处活副本 (甲×5 行 / 乙 / 丙 / 丁 / 戊) ⇒ 全部集中在【那一趟会读的读数面】上 ⇒ ★**其中 (乙) 是【已决且决错】, 最危险; (丙) 是【未答且选项全错】, 只能被答错; (丁) 在【已签收闸的源码】里, 教人填错件** ★

---

## §3 正确结论现状 (★本单独立复核, 不许只抄 ISS-387★)

### §3.1 正确的料号 (板侧真值档: 1×4 / 1×2 · 单排 · 直插 · 1.27 mm)

| 料号 | 官网单品页标题 (逐字) | 板侧真值四格 | 证据等级 | 本单复现方式 |
|---|---|---|---|---|
| ★**`FTS-104-01-F-S`** ★ | ★**`.050in/1.27mm Low Profile Micro Header Strip, 4 Pin, 1 Row, Through Hole, Gold Flash/Tin, .120in Post - FTS-104-01-F-S`** ★ | ★**脚数 4 ✓ · 排布 1 Row (单排) ✓ · 型态 Through Hole (直插) ✓ · 排距 1.27 mm ✓ ⇒ 四格全中** ★ | ★`[官网]` ★ | ★**本机 2026-11-24 14:5x `curl` 实抓** `https://www.samtec.com/products/fts-104-01-f-s` ⇒ HTTP `200` · `121813` B · 落 `tmp/iss394_sbx/fts-104-01-f-s.html` ⇒ ★`[实测]` (本机实抓) ★ |
| ★**`FTS-102-01-F-S`** ★ | ★**同上结构, `2 Pin, 1 Row, Through Hole`** ★ | ★**脚数 2 ✓ · 单排 ✓ · 直插 ✓ · 1.27 mm ✓ ⇒ 四格全中** ★ | ★`[官网]` ★ | ★**本机直抓 `https://www.samtec.com/products/fts-102-01-f-s` ⇒ HTTP `429` (限流) ⇒ 降级读【盘上已签收页 ISS-387 §2 的逐字记录】⇒ ★`[实测]` (本机复读已签收件) + ★`[官网]` ★ |

★**本单本机独立复核到的【家族页之外的官网一手件】**: ★**Samtec 官网 FTS 家族目录 PDF `https://suddendocs.samtec.com/catalog_english/fts.pdf` (HTTP `200` · `468445` B · 落 `tmp/iss394_sbx/fts_catalog.pdf`) ⇒ 文字层逐字解出选项矩阵**: ★**`–S` = Single Row · `–S` = Through-hole · `–DV` = Vertical SMT · `–D` = Double · `–SV` = Vertical SMT · lead style `–01` = `(3.05 mm) .120" Post` / `–02` = `(1.91 mm) .075" Post` / `–03` = `(1.65 mm) .065" Post` / `–04` = `(3.81 mm) .150" Post` · Insulator Material = `Black Liquid Crystal Polymer` · Current Rating = `3.4 A per pin` · Operating Temp = `-55 °C to +125 °C`** ⇒ ★**⇒ 这是【厂商自己的选型手册】给的族级解码 ⇒ ★**① `FTS-xxx-01-F-S` = 单排 + 直插 + `.120"` (3.05 mm) post ⇒ 与单品页标题互相印证; ② `FTSH-xxx-01-F-DV` = 双排 + 垂直贴片 ⇒ ★**被推翻的那两个料号【在厂商自己的手册里就不是单排直插】⇒ §1 的推翻【有第二个官网一手源】** ★`[官网]` + ★`[实测]` (本机实抓 + 实解文字层) ★

★**⇒ 结论**: ★**板侧真值档 (1×4 / 1×2 · 单排 · 直插 · 1.27 mm) 【有现成可采购件】, 就在 Samtec 同厂同 1.27 mm 的【FTS】系列 ⇒ ⇒ ★**「FTSH 族内没有单排直插」这条事实成立, 但【单排直插档并非无解】** ★

### §3.2 ★**「座体高 / 尾长 / 总长 仍是 `[0数据]` 吗?」—— 本单独立复核的逐项答案** ★

★**ISS-387 L43 自己写的是「座体高 (绝缘体高) / 尾长 / 总长 / 接触形状 / 材质」都要去【分销参数表】查 ⇒ 本单逐项独立复核如下** ★

| 量 | 本单独立复核的结果 | 证据等级 | 说明 |
|---|---|---|---|
| ★**尾长 (post 长度)** ★ | ★**`.120 in` = `3.05 mm`** —— ★**官网单品页标题逐字含「.120in Post」· 官网 FTS 家族目录 PDF 的 lead style `–01` 逐字「`(3.05 mm) .120" Post`」** ⇒ ⇒ ★**⇒ 【官网一手值拿到了】⇒ 这条【不再是 `[媒体]`】** ★ | ★**`[官网]`** ★ | ★**本单实抓 (§3.1) ⇒ [实测]** ★ |
| ★**座体高 (绝缘体高)** ★ | ★**★【仍是 `[0数据]` —— 官网那一层根本没有这个数】★** ★**本单独立复核了三个官网面**: ★**① 单品页 HTML (全文扫 `Height` / `Insulation` / `Post` ⇒ 只有标题里的 `.120in Post` 与描述段, 无绝缘体高) · ② FTS 家族目录 PDF 文字层 (有 lead style 四个 post 长度 + 绝缘体【材料】`Black Liquid Crystal Polymer`, 【无】绝缘体【高度】) · ③ 单排推荐 PCB 图 PDF 的 FIG 1 文字层 (见 §3.3, 只有排距/孔径/跨距三个标注) ⇒ ⇒ ★**⇒ 座体高【在官网那一层确实不存在】⇒ ISS-387 的 `[媒体]` (DigiKey 同族 `FTS-107-01-F-S` 「Insulation Height: 0.034" (0.86mm)」) 【维持不变, 本单无新证据推翻它, 也无官网一手值可替换它】** ★ | ★**`[0数据]` (官网层) + `[媒体]` (现有 0.86 值)** ★ | ★**⇒ 「座体真实高 h」这一格【继续挂着】⇒ 见 §3.4 降级方案** ★ |
| ★**总长 / 座体外形尺寸 (宽 / 深)** ★ | ★**★【仍是 `[0数据]`】★** ★**本单独立复核**: ★**单排推荐 PCB 图 PDF 的 FIG 1 文字层【只有三个标注】(跨距公式 / `.050 1.27 (TYP)` 排距 / `.028 0.71 (TYP)` 孔径) ⇒ 【没有座体外形标注】⇒ ⇒ **与 ISS-387 L77 「直插档外形尺寸 = `[0数据]`」一致** ★ | ★**`[0数据]`** ★ | ★**⇒ `keepout_dwg` 这一格【继续挂】⇒ 见 §3.4** ★ |
| ★**接触形状 / 材质** ★ | ★**官网家族目录 PDF 给了【材质】(`Phosphor Bronze` 端子 / `Black Liquid Crystal Polymer` 绝缘体 / 镀层 `Sn or Au over 50 µ" (1.27 µm) Ni`)** ⇒ ★**材质这一格【不再是 `[0数据]`】**; ★**接触形状 (方柱 `.016" (.41mm)`) 官网家族页与 ISS-387 §2 已记 ⇒ 维持 `[官网]`** ★ | ★**`[官网]`** ★ | ★**⇒ ISS-387 L43 那行「接触形状 / 材质」可被官网手册部分收窄** ★ |

★**⇒ §3.2 一句话**: ★**尾长【从 `[媒体]`/隐含 升到 `[官网]` 3.05 mm】· 材质【从 `[0数据]` 升到 `[官网]`】· ★★**座体高与总长/外形【本单独立复核: 官网那一层确实没有 ⇒ 维持 `[0数据]`】★★ ⇒ ⇒ **ISS-387 的降级方案【继续成立, 不因本单而解除】** ★

### §3.3 官网 CAD / 打印件链接: ★**本单把 ISS-387 的一个 `[0数据]` 闭合了** ★

★**ISS-387 L76/L221 记的是**: ★**「单排版打印件直链 = `[0数据]`」· 理由: 「本机探测了 14 个候选文件名全部 403 (该域对不存在的路径返 403), `www.samtec.com` 全站 429」** ★

★**本单独立复核 (★方法: 不是猜文件名, 是【从 `FTS-104-01-F-S` 官网单品页 HTML 的「Prints and Footprints」区把直链抠出来】★)**:

```bash
curl -sS -A "Mozilla/5.0 ..." "https://www.samtec.com/products/fts-104-01-f-s" -o tmp/iss394_sbx/fts-104-01-f-s.html
grep -oE 'href="[^"]*suddendocs[^"]*footprint[^"]*"' tmp/iss394_sbx/fts-104-01-f-s.html | sort -u
```

★**读数 (本机实跑)**: ★**命中 4 条, 其中单排那一条的直链 = `https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-footprint.pdf`** ★
★**本机实抓结果**: ★**HTTP `200` · `97834` B · `application/pdf` · md5 `9b1b8166e7fd437faeb18fd9df51e3b5` · `file` 报 `PDF document, version 1.4, 6 page(s)`** ⇒ ★**⇒ 单排版打印件直链【不再是 `[0数据]`】⇒ 这是本单给 ISS-387 补上的一格** ★`[官网]` + ★`[实测]` ★

★**该单排打印件 SHEET 1 / FIG 1 的文字层逐字 (本机 `pdftotext -layout` 实跑)**:

```
REVISION D                     RECOMMENDED PCB LAYOUT FOR FTS-1XX-XX-X-SX
                                        (NO OF POS x .050[1.27]) - .050[1.27]
                                        .050 1.27 (TYP)
             .028 0.71 (TYP)
                                                       FIG 1
                                            D FTS-1XX-XX-X-S SHOWN
```

★**⇒ 三个官网一手标注**: ★**① 孔中心跨距公式 `(NO OF POS × .050[1.27]) − .050[1.27]` · ② 排距 `.050 1.27 (TYP)` · ③ 孔径 `Ø .028 0.71 (TYP)`** ⇒ ★**⇒ ★★**§3.3 的一个附带结论: 板侧钻孔 `0.65 → 0.71` 这条 (ISS-391 登记的那条) 现在有【单排件自己的官方打印件】背书, 不再只靠「双排打印件的 FIG 1 对每排成立」那条推算** ⇒ ★**该条与 ISS-391 交叉引用 (★`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` §1.1 引的是双排打印件 `fts-1xx-xx-xx-dx-xx-footprint.pdf` ⇒ 本单补的是【单排版直链本身】这一格★)** ★`[官网]` + ★`[实测]` ★

★**★重要限定 (★不许越读★)**: ★**该打印件 SHEET 1 的 FIG 1 【仍然没有座体外形标注】⇒ ⇒ §3.2 的「总长 / 座体外形 = `[0数据]`」【不因拿到这份打印件而改变】** ★`[实测]`

### §3.4 官网 CAD 链接拿不到时的降级方案 (★本单写全, 不挂起★)

| # | 降级方案 | 触发条件 | 谁执行 | 证据等级 |
|---|---|---|---|---|
| ★**①** ★ | ★**用【已取得的单排推荐 PCB 图 FIG 1 文字层】当官方 land 来源** (排距 `1.27` / 孔径 `Ø0.71` / 跨距公式) ⇒ ★**不用等官网 CAD 下载** ★ | ★**已触发 (本单已取得)** ⇒ ★**降级路径【已经生效】** ★ | ★**hw-lead (本单已落证据)** ★ | ★`[官网]` ★ |
| ★**②** ★ | ★**座体外形 (宽/深/总长) ⇒ 官网 3D/CAD 下载量外形** ⇒ 量不到就用**★**双轨: (甲) 官网 3D/CAD 下载件量外形; (乙) 落 FTS 时先打一块单板样, 用卡尺量三个量 (绝缘体高 / 外形宽 / 外形深) 回填 `keepout_dwg`** ★ | ★**座体外形 = `[0数据]` ⇒ 一直触发** ★ | ★**(甲)(乙) 归 mech-lead (★ISS-391 `OI-387-4` 已裁为走双轨降级方案, 与「板只改一次」那一趟同批★)** ★ | ★`[0数据]` → 降级后 `[实测]` ★ |
| ★**③** ★ | ★**座体高 (绝缘体高) ⇒ 官网那一层不存在 ⇒ 沿用分销参数表同族值 `0.86 mm` (`[媒体]`) 作【临时值】, 并显式标注「同族同 lead style 同 row option 取值」, 【不许】写成 `[官网]`** ★ | ★**已触发** ★ | ★**hw-lead 已登记 (本页 §3.2) + 落表时随 BOM 备注带出** ★ | ★`[媒体]` ★ |
| ★**④** ★ | ★**环宽 (annular ring) 能力 ⇒ 本板厂最小环宽** (★`Ø0.71` 配通用件 `1.000` 焊盘 ⇒ 环宽 `0.1750 → 0.1450` mm★) ⇒ 查不到就写 `[0数据]` + 降级 = 投板前向板厂索取工艺能力 (★项目已定「不再外发」⇒ 这一条归【老板/main 的商务动作】, 不由 hw-lead 外发★) ★ | ★**已触发** ★ | ★**main / 老板 (商务动作) · 已登记为 `iss387_main_ring_width_fab_capability`** ★ | ★`[0数据]` ★ |

★**⇒ §3 一句话**: ★**正确方向【本单独立复核成立】(`FTS-104-01-F-S` / `FTS-102-01-F-S` 单排直插, 官网一手件 + 官网一手手册双重背书) · 并额外闭合了 ISS-387 的「单排打印件直链 = `[0数据]`」一格 · ★**座体高与座体外形【官网那一层确实没有 ⇒ 维持 `[0数据]` + 降级方案 ②③】⇒ ⇒ ★**落表时机 = 「板只改一次」那一趟 (★`HW/BOM_v1.csv` L71 / L77 此刻型号栏仍是 `待定` ⇒ 现在纠正成本 = 改文档★)** ★

---

## §4 那 5 处各自【改了会引发什么】+ 代价 (★只摆代价, 不代拍★)

★**★边界声明: 下面 5 条的地界判断 (谁有权改 / 改不改 / 什么时候改) 全部是 main 的裁决权 ⇒ ★★本单只摆【代价】, 一条都不代拍★ ★**

### ★§4-① (甲) 真相页 L18/L62/L67/L73/L112 —— 一个已签收页的正文 ★

| 维度 | 内容 |
|---|---|
| ★**谁有权改** ★ | ★**main** (该页是 ISS-380 的交卷产物, 已签收; ★**本单零改既有页面正文**) ★ |
| ★**改的动作** ★ | ★**追加式订正块** (★不逐字替换原文★ —— ★**本项目纪律: 已签收页用【追加式】, 原地改会当场把签收指纹搞过期**) ★ |
| ★**改完会引发什么** ★ | ★**① (甲) 页变成【推翻记录的第一个落点】⇒ 以后任何读 `BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` 的人都会读到「这两个首选候选已被推翻」; ② ★**ISS-380 的 `verify_result` 里那句「§2 的 D-1/U-1 判定被推翻」有了【页级落点】⇒ 台账与页面从此一致; ③ ★**本单新闸 K1 的红条会少 5 行 (但不会全绿 —— 因为 (乙)(丁)(戊) 还在)** ★ |
| ★**代价** ★ | ★**零板侧代价 · 零结构侧代价 · 唯一代价 =【该页与 ISS-380 交卷页的正文不再逐字一致】⇒ 需 main 在签收台账里留一条「追加式订正」痕迹, 否则以后有人对不上「ISS-380 交卷时到底写了什么」** ★ |
| ★**不做的代价** ★ | ★**★那一趟 whoever 照 L67 那一句「唯一同时满足三要素的候选是 `FTSH-104-01-F-DV`」填 BOM ⇒ 装 8 脚双排贴片 ⇒ 排针插不进 ⇒ 【板改两次】★** |

### ★§4-② (乙) 一条【已闭】的 need 的答案 —— ★**本单最需要 main 裁的一条** ★

| 维度 | 内容 |
|---|---|
| ★**问题** ★ | ★**`iss377_oi10_vendor_part_numbers` 是一条【已闭】的 need 的答案 (段 `answers` · `to: main`)。★**改它要不要重开 need? 这条地界判断是 main 的, 本单不代拍。** ★ |
| ★**选项 ①: 直接追加式订正答案, 不重开 need** ★ | ★**代价 =【「已闭」这个状态本身仍然成立, 但内容已变】⇒ 后果: 任何按 `answers[].key` 查「这件事闭了没」的人, 拿到的是【一条被订正过的旧答案】⇒ 需要在同一条答案里追加 `note_addendum` 式痕迹 (★本仓既有写法: `state/issue_log.yaml` 的 `note_addendum` / `note_addendum_2` 字段★) ⇒ ★**代价最低, 但【已闭】语义会变得不干净: 「闭了」与「闭得对」被混在一处** ★ |
| ★**选项 ②: 重开 need (加一条新 key 的 `needs_from`), 把旧答案标为「已被后续 need 取代」** ★ | ★**代价 =【多一条 open need】⇒ 队列里会多一项要 main 答 ⇒ 但【语义最干净】: 「旧答案是旧的, 新问题是新的」⇒ ★**与本仓既有先例一致: `iss383_vendor_part_real_spec` 就是【新 key】把 ISS-380 的判定收窄的 (而不是去改 `iss377_...` 那条旧答案) ⇒ ★**★本单能查到的先例 =【已签收页 ISSUE-383 用的是新 key, 没动旧 key★】★ ★ |
| ★**选项 ③: 两条都做 (旧答案追加订正 + 同时开新 need)** ★ | ★**代价 =【留痕最全, 但两处要同批落, 漏一处就出现「新旧不一致」】⇒ 对齐成本最高, 但事后可追溯性最好** ★ |
| ★**★不做的代价** ★ | ★**★一条【已决且决错】的答案挂在 `answers[]` 里 ⇒ 任何读分片的人 (人 or 机器) 拿它当既成事实 ⇒ 「首选 FTSH-104-01-F-DV (1×4 1.27mm 直插)」这句话 (★该料号已被推翻, 不得落表★) 会继续被抄进别的页 ⇒ ⇒ 【板改两次】** ★ |

### ★§4-③ (丙) 一条【未答】的 need —— 选项全错 ★

| 维度 | 内容 |
|---|---|
| ★**谁有权改** ★ | ★**main** (该 need 的 `to: main`) ★ |
| ★**改的动作** ★ | ★**追加式订正块**: 把「板侧真值档 = FTSH-104/FTSH-102」换成「板侧真值档 = ★**FTS-104-01-F-S / FTS-102-01-F-S** (1×4 / 1×2 · 单排 · 直插)」★, 并保留「结构侧那三条不自洽点谁去重算」那一问 ★ |
| ★**改完会引发什么** ★ | ★**① 这条 need 从「只能被答错」变成「可以被答对」; ② ★**注意: ★**改选项 ≠ 答这条 need** ⇒ ★**【选项改了, 但答案仍要 main 自己拍 (因为「落表」本身就是 main 的动作)】⇒ 改完它依然 open ⇒ 这正是本单 K3 的判据形态: 「选项里必须至少有一个满足板侧真值档的选项」** ★ |
| ★**代价** ★ | ★**零板侧代价 · 零结构侧代价 · 唯一代价 =【这条 need 的 `item` 文本变了 ⇒ 若 main 已按旧文本在心里排过优先级, 要重排】★ |
| ★**不做的代价** ★ | ★**★main 回来答这条 need 时, 无论答 ① 还是 ②, 都是答错 ⇒ ⇒ 【板改两次】** ★ |

### ★§4-④ (丁) 一个【已签收闸】的源码 —— ★**「动它算不算动已签收件」★**

| 维度 | 内容 |
|---|---|
| ★**问题** ★ | ★**`HW/check_debug_uart_seat_alignment.py` L397 是【已签收闸】的源码。★**改它算不算「动已签收件」? 这条地界判断是 main 的, 本单不代拍。** ★ |
| ★**选项 ①: 改 L397 (把硬编码样本换成非被推翻料号)** ★ | ★**代价 =【该已签收闸的 md5 变了 ⇒ 它自己的签收指纹过期 ⇒ 需 main 重签 + 台账留痕】⇒ ★**好处 =【它不再教人填错件】⇒ 后果最小** ★ |
| ★**选项 ②: 不改 L397, 改【它的 selftest 的意图表达】** ★★(★其实 ① 就是唯一可选项, 因为 L397 是【数据】不是【判据】★)★ ★**代价 = 无 (不成立)** ★ |
| ★**选项 ③: 保留 L397 原样, 只在本单新闸里【把这处登记为已知例外】** ★ | ★**代价 =【那道闸继续教人填一颗被推翻的料号】⇒ 沙盒里若有人照抄 selftest 的样本, 就会填错 ⇒ ★**但【本单新闸 K1 会红】⇒ 至少不是静默的** ⇒ 这是【代价最低但收益也最低】的选项** ★ |
| ★**★可查到的先例 (★本单本机实查★)** ★ | ★**★先例 ①: `HW/check_fts_single_row_land_truth.py` (ISS-387, 已签收) 的 K4 【就是把「族别混用」写成机器判据】⇒ ⇒ 【「一条结论错了 ⇒ 补一道机器闸来守」在本仓是既有做法, 而不是例外】★ · ★**先例 ②: ISS-383 (已签收) 在【不改 ISS-380 页面正文】的前提下, 用【自己新页 + 自己新闸】把推翻结论做成了可查的登记 ⇒ ⇒ 【新增闸/页来承载纠正, 不动旧件】是既有做法** · ★**先例 ③: 本仓台账既有 `note_addendum` / `note_addendum_2` 的【追加式留痕】机制 ⇒ ⇒ 【追加式改已签收件而不删老字】是既有做法** ★ |
| ★**不做的代价** ★ | ★**★一道已签收闸的 selftest 继续教人填被推翻的料号 ⇒ 闸判绿 + 事实错 ⇒ 下一个照着它填 BOM 的人就装错件 ⇒ ⇒ 【板改两次】** ★ |

### ★§4-⑤ (戊) `interface_claims` 的 note —— ★**本单新发现的第 5 处** ★

| 维度 | 内容 |
|---|---|
| ★**谁有权改** ★ | ★**main** (分片归 main 合并 / 订正时由 owner 落; ★**本单只写自己那几条, 不动这一条★) ★ |
| ★**改完会引发什么** ★ | ★**① `interface_claims` 是【接口取值声明】那一面 ⇒ 改它 = 改机器可读面 ⇒ ①台账 `STATE.yaml` 合并后同步; ②本单新闸 K1/K2 会少 1 条红 ★ |
| ★**代价** ★ | ★**零板侧代价 · 唯一代价 =【`interface_claims` 的 `value` 与 `note` 要一致 (★`value` 现在写的是「见真相页 §2 (厂商型号候选表)」⇒ 指向的那张表现在仍标「首选候选」⇒ ⇒ 【只改 `note` 不改真相页 ⇒ 仍会读到旧表】⇒ ⇒ ★**这两处【必须同批落】, 否则改了一处反而制造新的不一致**】** ★ |
| ★**不做的代价** ★ | ★**机器可读面 (接口取值声明) 继续说「首选 FTSH-104-01-F-DV」 (★该料号已被推翻, 不得落表★) ⇒ 任何按 `interface_claims` 自动取值的下游会取到错件** ★ |

### ★§4-⑥ 五处【必须同批落】的时序提示 (★只摆代价, 不代拍★)

★**★若分批落, 中间态会制造【新的不一致】⇒ 中间态本身就是风险**: ★**(乙)+(丙) 同在 `state/fragments/hw.yaml` ⇒ 一条答案 + 一条 need ⇒ ★**若只落 (丙) 不落 (乙) ⇒ 「未答 need 的选项对了」但「已闭答案还错着」⇒ 本单新闸仍红; ★**若只落 (乙) 不落 (丙) ⇒ 同理; ⇒ ⇒ 【这两条【必须同批】** ★
★★**(甲)+(戊) 必须同批**: ★**(戊) 的 `value` 指向 (甲) 的表 ⇒ ⇒ **只改 (戊) 的 note 而不改 (甲) 的表 ⇒ 机器可读面说「已被推翻」而表里还写「首选候选」⇒ 反而更乱** ★
★★**(丁) 单独落**: ★**它在一个已签收闸里 ⇒ 落它要重签那道闸 ⇒ 建议与 (甲)(乙)(丙)(戊)【同批落, 但【作为独立一条可追溯】** ★
★★**★落表的时点**: ★**★全部 5 处落完 + 那一趟的封装/孔径决策定了 ⇒ 才轮到 `HW/BOM_v1.csv` L71/L77 的型号栏 ⇒ ⇒ 【BOM 型号栏落表 = 这 5 处落完之后的事, 不在同批】★** ★

---

## §5 复跑命令 (★原样可粘贴★)

### §5.1 本单自证

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 新闸正向跑 (★K1/K2/K3 现状为红 ⇒ 这是【现状即如此】, 不是闸故障★)
python3 HW/check_seat_part_verdict_propagation.py            # rc=1 ★预期★
# ② 新闸自测
python3 HW/check_seat_part_verdict_propagation.py --selftest  # rc=0 · 末行 ALL TESTS PASS
```

### §5.2 地界事实复跑 (★本单 §1/§2/§3 的每一个读数的出处★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# (甲) 真相页: 推翻痕迹 = 0
grep -c "㊳\|推翻\|订正" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md   # ⇒ 0
grep -n "FTSH" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md                # ⇒ 6 行 (L18/L62/L63/L67/L73/L112)

# (乙) 已闭答案
grep -n "iss377_oi10_vendor_part_numbers" state/fragments/hw.yaml
sed -n '5269,5276p' state/fragments/hw.yaml

# (丙) 未答 need
grep -n "iss380_board_trip_bom_part_fill" state/fragments/hw.yaml
sed -n '4344,4350p' state/fragments/hw.yaml

# (丁) 已签收闸源码里的硬编码样本
grep -n "FTSH" HW/check_debug_uart_seat_alignment.py
sed -n '393,400p' HW/check_debug_uart_seat_alignment.py

# (戊) interface_claims 的 note (★本单新发现★)
grep -n "iss380_seat_part_truth" state/fragments/hw.yaml

# BOM 型号栏此刻仍是「待定」
grep -n '^J_DEBUG\|^J_UART' HW/BOM_v1.csv

# 对照: 已签收页里【已经写对】的两处 (不在清账表里)
grep -n "8 Pin, 2 Row, SMT" HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md | head -3
grep -n "已被 §㊳ 发现一推翻" HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md
```

### §5.3 §3 的独立复核复跑 (★本单本机实抓的命令, 原样★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
mkdir -p tmp/iss394_sbx
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# ① 官网单品页标题 (★被推翻的那个料号★)
curl -sS -A "$UA" "https://www.samtec.com/products/ftsh-104-01-f-dv" -o tmp/iss394_sbx/ftsh104.html -w "HTTP=%{http_code} SIZE=%{size_download}\n"
grep -o '<title>[^<]*</title>' tmp/iss394_sbx/ftsh104.html
# ⇒ <title>.050in/1.27mm Micro Header Strip, 8 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post - FTSH-104-01-F-DV</title>

# ② 官网单品页标题 (★正确的那个料号★)
curl -sS -A "$UA" "https://www.samtec.com/products/fts-104-01-f-s" -o tmp/iss394_sbx/fts-104-01-f-s.html -w "HTTP=%{http_code} SIZE=%{size_download}\n"
grep -o '<title>[^<]*</title>' tmp/iss394_sbx/fts-104-01-f-s.html
# ⇒ <title>.050in/1.27mm Low Profile Micro Header Strip, 4 Pin, 1 Row, Through Hole, Gold Flash/Tin, .120in Post - FTS-104-01-F-S</title>

# ③ 官网家族目录 PDF (★厂商自己的选型手册: –S = Single Row / Through-hole, –DV = Vertical SMT, –01 = (3.05mm) .120" Post★)
curl -sS -A "$UA" "https://suddendocs.samtec.com/catalog_english/fts.pdf" -o tmp/iss394_sbx/fts_catalog.pdf -w "HTTP=%{http_code} SIZE=%{size_download}\n"
pdftotext -layout tmp/iss394_sbx/fts_catalog.pdf tmp/iss394_sbx/fts_catalog.txt && grep -nE "Single|Double|Vertical SMT|\.120|Post" tmp/iss394_sbx/fts_catalog.txt | head -20

# ④ 单排推荐 PCB 图 (★ISS-387 记为 [0数据] 的一格, 本单闭合★)
curl -sS -A "$UA" "https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-footprint.pdf" -o tmp/iss394_sbx/fts-1xx-xx-x-sx-footprint.pdf -w "HTTP=%{http_code} SIZE=%{size_download}\n"
md5sum tmp/iss394_sbx/fts-1xx-xx-x-sx-footprint.pdf
pdftotext -layout tmp/iss394_sbx/fts-1xx-xx-x-sx-footprint.pdf tmp/iss394_sbx/fts_sx_fp.txt && sed -n '1,20p' tmp/iss394_sbx/fts_sx_fp.txt
# ⇒ FIG 1 文字层: (NO OF POS x .050[1.27]) - .050[1.27] / .050 1.27 (TYP) / .028 0.71 (TYP)

# ⑤ 官网 3D/CAD 与单排外形尺寸: ★本单实测仍取不到 ⇒ [0数据] ⇒ 走 §3.4 降级 ②
```

### §5.4 边界复跑

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n mtime=%y size=%s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_seat_part_verdict_propagation state/gate_check.py   # ⇒ 0 (零挂链)
```

---

## §6 机器块 (§6.2 · `--emit` 可解析)

### §6.1 ★**自指问题怎么处理的 (★本单闸的设计说明·必读★)** ★

★**本单新建的真相页必然要提到被推翻的两个料号 (★那是【记账】, 不是【当首选】★) ⇒ ★**如果 K1 的匹配式写成「文件里出现 `FTSH-…-F-DV` 就红」⇒ ⇒ **本单自己的记账页会把闸打红 ⇒ 闸天天报一条假红 ⇒ ⇒ 假红的闸等于没有闸** ★**

★**本单的处理办法 (★三步, 全部机器可判★)**:

| 步 | 做法 | 为什么这样 |
|---|---|---|
| ★**1** ★ | ★**K1 的扫描面是【显式白名单】**: ★**`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` (甲) · `state/fragments/hw.yaml` (乙/丙/戊) · `HW/check_debug_uart_seat_alignment.py` (丁) · ★**外加本单自己的记账页 `HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md` (★扫它, 但它【受第 2 步的语境判据约束★)** ★ | ★**★白名单 ⇒ 漏扫别的文件 = 闸自己会红 (K1 会核对「本单登记的 `live_copies` 与实际扫描面一致」) ⇒ ⇒ **不会因为「只扫了我知道的那几个文件」而漏掉第 6 处** ★ |
| ★**2** ★ | ★**语境判据 (★记账 vs 断言★)**: ★**一行同时满足【含被推翻料号】+【含断言标记 或 口径标记】+【不含任何证伪标记】⇒ ★**⇒ 判红** ★<br>★**断言标记** = ★`首选` / `唯一同时满足` / `推荐` / `落表件` / `建议采用` / `应当采用` / `定为` / `就选` ★<br>★**口径标记** = ★`1×4` / `1×2` / `1x4` / `1x2` / `单排` / `直插` / `THT` / `排针` ★ (★= 该行在主张这颗料号满足板侧真值档★)<br>★**证伪标记** = ★`推翻` / `已证伪` / `不得` / `不许` / `禁` / `作废` / `错三格` / `全错` / `不可直接落表` / `已被推翻` / `不是单排` / `双排贴片` / `不得当` ★ | ★**⇒ 本单记账页的每一处被推翻料号【都在同一行里带证伪标记】⇒ 本单自己不会把自己打成红; ⇒★**而 (甲)(乙)(丁)(戊) 那些行【恰好没有证伪标记】⇒ 它们照样红** ⇒ ⇒ **【记账语境】与【当首选语境】被分开, 而且是逐行判的** ★ |
| ★**3** ★ | ★**机器块掩码 (★必须讲清楚, 否则闸看不懂本单为什么不被自己打红★)**: ★**扫描用的是【正文视图】(★`prose_only()` 把 ```json 机器块整块去掉★) ⇒ ⇒ 机器块里 `live_copies[].quote` 那些【逐字引用的旧原文】不会参与逐行判定 ⇒ ⇒ **它们是【引用】不是【主张】⇒ 不该红** ★ · ★**而机器块本身的完整性改由【结构判据】守**: ★**每个 `live_copies[]` 条目指向的 file 必须存在 + line 必须在文件行数内 + 那个文件里必须真的还有那个被推翻的料号 ⇒ 台账与盘面不一致 ⇒ 判红** ★ | ★**⇒ 逐行判只管【正文里的主张】, 结构判只管【台账与盘面是否还对得上】⇒ 两条互不代偿** ★ |
| ★**4** ★ | ★**反向用例把这条设计钉死 (★--selftest 里两条对着干的用例★)**: ★**用例 ⑤ 把【纯记账】片段塞进扫描面 ⇒ K1 必须【不红】** (★这正是「把匹配式放宽成『出现 FTSH 就红』」会被抓住的那一条★) · ★**用例 ⑥ 把一句【纯断言】塞进本单记账页 ⇒ K1 必须红** (★这正是「把本页一律豁免」会被抓住的那一条★) · ★**用例 ⑲ 把扫描面里的一项删掉 ⇒ K1 必须红** (★防漏扫: 必扫面是硬编码在本闸里的, 机器块少登记一个就红★) | ★**⇒ 两个方向的漏项都被堵死** ★ |

★**⇒ ★**另: K2 / K3 只扫 `state/fragments/hw.yaml` 的 `answers` / `needs_from` 两个段 ⇒ ⇒ **本单自己新写的 need / claim (走 `frag_write.py` 追加) 也在扫描面内 ⇒ ⇒ **本单写自己的 need 时, 必须【不许在那 5 处被推翻料号上写「首选」】⇒ 本单分片已按此写 (见 §6.2 的 `live_copies` 与 `needs_from` 登记) ★**

### §6.2 机器块

```json
{
 "schema": "hw.seat_part.verdict_propagation",
 "issue": "ISS-394",
 "agent": "hw-lead",
 "updated": "2026-11-24",
 "truth_doc": "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md",
 "refuted_parts": [
  "FTSH-104-01-F-DV",
  "FTSH-102-01-F-DV"
 ],
 "refuted_reason": "Samtec 官网单品页标题逐字 '8 Pin, 2 Row, SMT' / '4 Pin, 2 Row, SMT' ⇒ 双排贴片; 与板侧真值 '1x4 / 1x2 单排直插' 在 脚数/排布/型态 三格全错; 病根 = ISS-380 §2 用家族页的族属性代替具体件规格",
 "correct_parts": [
  "FTS-104-01-F-S",
  "FTS-102-01-F-S"
 ],
 "correct_parts_evidence": {
  "FTS-104-01-F-S": "[官网] 官网单品页标题逐字 '4 Pin, 1 Row, Through Hole' (4 位 / 1 排 / 直插 / 1.27mm) ⇒ 板侧真值四格全中; 本机 2026-11-24 实抓 HTTP 200 / 121813 B",
  "FTS-102-01-F-S": "[官网] 官网单品页标题逐字 '2 Pin, 1 Row, Through Hole' (2 位 / 1 排 / 直插 / 1.27mm); 本机直抓 HTTP 429 ⇒ 降级读盘上已签收页 ISS-387 §2 逐字记录"
 },
 "live_copies": [
  {
   "file": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
   "line": 18,
   "kind": "truth_page_overview",
   "quote": "J_DEBUG 侧查实 Samtec FTSH-1xx-01-F-DV (1.27 mm 直插排针家族)",
   "error": "把 FTSH 族当直插排针族; 该族在 1.27mm 下无双排直插以外的单排直插件",
   "owner": "main",
   "fix": "追加式订正块: 改成 双排族 (-D/-DV/-DH/-MT) 并指向 ISS-383 §1.1/§1.2 与本页 §1"
  },
  {
   "file": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
   "line": 62,
   "kind": "truth_page_candidate_row",
   "quote": "| D-1 | **Samtec** | **`FTSH-104-01-F-DV`** | ... | 排距 ✓ 脚数 ✓ (4 脚候选) · 直插 ✓ ⇒ 首选候选 |",
   "error": "四格全错 (脚数 8≠4 / 排布双排≠单排 / 型态贴片≠直插); 证据栏用的是家族页",
   "owner": "main",
   "fix": "追加式订正块: D-1 行标 已被推翻 不得当落表件 + 三格改实测值 + 证据栏换单品页 URL"
  },
  {
   "file": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
   "line": 67,
   "kind": "truth_page_conclusion",
   "quote": "按板侧真值 (1×4 · 1.27 mm · 直插), 唯一同时满足三要素的候选是 `FTSH-104-01-F-DV` (D-1)",
   "error": "§2.3 结论 2-1 本身不成立; 这是下游最会抄的一句",
   "owner": "main",
   "fix": "追加式订正块: 划掉 唯一同时满足三要素; 改指 FTS 族 (ISS-387) 的 FTS-104-01-F-S"
  },
  {
   "file": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
   "line": 73,
   "kind": "truth_page_candidate_row",
   "quote": "| U-1 | **Samtec** | **`FTSH-102-01-F-DV`** | ... | 排距 ✓ 脚数 ✓ (2 脚候选) · 直插 ✓ ⇒ 首选候选 |",
   "error": "同 L62: 四格全错",
   "owner": "main",
   "fix": "追加式订正块: 同 L62 的处置"
  },
  {
   "file": "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
   "line": 112,
   "kind": "truth_page_landing_advice",
   "quote": "J_DEBUG → FTSH-104-01-F-DV (D-1) / J_UART → FTSH-102-01-F-DV (U-1): 二者都落在板侧真值的 1.27 mm 直插档内",
   "error": "这是落表建议那一格; 被抄即填错件",
   "owner": "main",
   "fix": "追加式订正块: 整行标 已被推翻 不得落表 + 指到 ISS-387 的 FTS 档"
  },
  {
   "file": "state/fragments/hw.yaml",
   "line": 5271,
   "kind": "closed_answer",
   "quote": "OI-10 已闭: J_DEBUG 首选 Samtec FTSH-104-01-F-DV (1×4 1.27mm 直插), J_UART 首选 Samtec FTSH-102-01-F-DV (1×2 1.27mm 直插)",
   "error": "已决且决错: 标 已闭 + 写 首选 + 指向被推翻料号 ⇒ 下游读分片的人拿它当既成事实",
   "owner": "main",
   "fix": "追加式订正块; 重开 need 与否 = main 的地界 (本页 §4-② 摆三个选项与代价, 不代拍)"
  },
  {
   "file": "state/fragments/hw.yaml",
   "line": 4346,
   "kind": "unanswered_need",
   "quote": "板那一趟的 BOM 型号栏: J_DEBUG/J_UART 按板侧真值档 (FTSH-104-01-F-DV / FTSH-102-01-F-DV) 还是 Cortex-10 2×5 档 (FTSH-105-01-L-DV-K)?",
   "error": "三个选项没有一个满足板侧真值档 ⇒ 这条 need 只能被答错",
   "owner": "main",
   "fix": "追加式订正块: 选项换成 FTS-104-01-F-S / FTS-102-01-F-S (1×4 / 1×2 单排直插); 改选项 ≠ 答这条 need"
  },
  {
   "file": "HW/check_debug_uart_seat_alignment.py",
   "line": 397,
   "kind": "signed_gate_selftest_fixture",
   "quote": "\"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTSH-104-01-F-DV,\"",
   "error": "已签收闸的源码把被推翻料号硬编码成 BOM 真源样本 ⇒ 该闸 selftest 在教人填错件 ⇒ 闸判绿 + 事实错",
   "owner": "main",
   "fix": "换成非被推翻料号 (例如 Samtec FTS-104-01-F-S); 动已签收件算不算越界 = main 的地界 (本页 §4-④ 摆先例与代价, 不代拍)"
  },
  {
   "file": "state/fragments/hw.yaml",
   "line": 8097,
   "kind": "interface_claim_note",
   "quote": "note: J_DEBUG 首选 Samtec FTSH-104-01-F-DV, J_UART 首选 Samtec FTSH-102-01-F-DV, 每条带官网链接",
   "error": "机器可读的接口取值面仍在说旧话; 且其 value 指向 (甲) 的候选表 ⇒ 与 (甲) 必须同批落",
   "owner": "main",
   "fix": "追加式订正块: note 标 已被推翻 不得落表 + 指到 ISS-387 的 FTS 档; 与 (甲) 同批落"
  }
 ],
 "closed_need_key": "iss377_oi10_vendor_part_numbers",
 "unanswered_need_key": "iss380_board_trip_bom_part_fill",
 "board_md5": "611b869e13518c3c023fb178f91a0075",
 "board_mtime": "2026-11-06 07:07:17.362193",
 "board_size": 4940213,
 "netlist_md5": "6aee500e60ba0732f83a9cf557ba90ab",
 "pins_md5": "9174309df1ec9411ac8e8d9e80ee386a",
 "bom_md5": "5b9993992405904a60ac96a020b375d8",
 "evidence_grades": {
  "refutation": "[官网] + [媒体]",
  "correct_parts": "[官网]",
  "post_length": "[官网]",
  "insulator_material": "[官网]",
  "insulation_height": "[0数据] 官网层无 + [媒体] 现有 0.86",
  "seat_outer_dimensions": "[0数据]",
  "single_row_footprint_print": "[官网] + [实测]",
  "live_copy_scan": "[实测]",
  "board_fingerprints": "[实测]"
 },
 "degradation_plan": {
  "D1": "官方 land 来源: 已取得单排推荐 PCB 图 FIG 1 (排距 1.27 / 孔径 0.71 / 跨距公式) ⇒ 不等官网 CAD 下载",
  "D2": "座体外形 (宽/深/总长): [0数据] ⇒ 双轨 (甲 官网 3D/CAD 下载件量外形 / 乙 落 FTS 时先打单板样用卡尺量三个量回填 keepout_dwg) ⇒ 归 mech-lead, 与板只改一次那一趟同批",
  "D3": "座体高 (绝缘体高): 官网层无 ⇒ 沿用 [媒体] 同族值 0.86 mm 作临时值并显式标注, 不许写成 [官网]",
  "D4": "环宽能力 (Ø0.71 配 1.000 焊盘 ⇒ 环宽 0.1450): [0数据] ⇒ 降级 = 投板前向板厂索取工艺能力 (商务动作归 main/老板, hw-lead 不外发)"
 },
 "not_decided_here": "not_decided_here",
 "decisions": {
  "selected_part": "not_decided_here",
  "landing_timing": "not_decided_here",
  "who_fixes_live_copies": "not_decided_here",
  "reopen_closed_need": "not_decided_here",
  "touch_signed_gate": "not_decided_here",
  "bom_model_field_value": "not_decided_here",
  "seat_height_h": "not_decided_here"
 },
 "not_decided_items": [
  "选型裁决 (落表哪颗件)",
  "那 5 处活副本分别由谁改 / 什么时机改",
  "改已闭答案要不要重开 need",
  "动已签收闸的源码算不算动已签收件",
  "落表时机"
 ],
 "protected_files": {
  "HW/check_fts_single_row_land_truth.py": "5b9570fd23d6dd7125876c9110085506",
  "HW/check_debug_uart_seat_truth.py": "274f759101ca4bc131f25633dc209b0c",
  "HW/check_debug_uart_seat_alignment.py": "52e067ed99edaaced50fd565bed90042",
  "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md": "1a9ade1bde85530c09054e2fdb8d5adb",
  "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md": "debb1aed437b9137b3d0297a208ccb45",
  "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md": "a2f78e769bbe9c27c44e728539206c04"
 },
 "protected_files_note": "以上 6 件为已签收件, 本单零改动; main 落订正时须在同一批把本处对应条目的 md5 更新为新值并在本块记名, 否则本单闸 K6 会红 (那是刻意的: 改动已签收件必须留痕)",
 "scan_surface": [
  "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
  "state/fragments/hw.yaml",
  "HW/check_debug_uart_seat_alignment.py",
  "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md"
 ],
 "scan_surface_note": "★白名单扫描面: 本单闸 K1 逐个扫这 4 个文件, 并核对本块 live_copies 与扫描面一致 ⇒ 新增活副本时必须同时登记, 否则 K1 红",
 "board_write": "none",
 "table_write": "none",
 "existing_gates_touched": "none",
 "existing_pages_touched": "none",
 "chain_hits": 0,
 "outbound": "none",
 "issue_log_touched": "none",
 "other_fragments_touched": "none",
 "drill_change_ref": "ISS-391 · HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md · 钻孔 0.65 -> 0.71 (本单 §3.3 用单排版官方打印件独立背书该孔径)",
 "seat_height_status": "[0数据] 官网层确实没有 (本单独立复核三面) ⇒ 维持 ISS-387 的 [媒体] 0.86 + 降级 D2/D3",
 "footprint_print_single_row": {
  "url": "https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-footprint.pdf",
  "http_status": "200",
  "size_bytes": 97834,
  "md5": "9b1b8166e7fd437faeb18fd9df51e3b5",
  "fig1_annotations": [
    "(NO OF POS x .050[1.27]) - .050[1.27]",
    ".050 1.27 (TYP)",
    ".028 0.71 (TYP)"
  ],
  "note": "★ISS-387 L76/L221 记为 [0数据] 的一格, 本单闭合; 该打印件 FIG 1 仍无座体外形标注 ⇒ 座体外形维持 [0数据]"
 }
}
```
