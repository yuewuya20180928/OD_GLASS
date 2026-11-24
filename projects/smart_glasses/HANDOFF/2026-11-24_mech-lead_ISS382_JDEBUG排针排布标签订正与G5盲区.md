# ★★ISS-382 · `J_DEBUG` 排针排布标签订正 + 旧闸 `G5` 盲区 (mech-lead · 2026-11-24)★★

★**一句话**: ★**官方两个 SMD 变体实测都是 `2x4_staggered` (2 列 × 4 行交错), 已签收页把降级方案写成 `2x2` ⇒ 错的是【标签 / 维数】, 不是【结论数字】; 旧闸 `G5` 只判「字符串里含 `staggered`」, 从不把页面声明的维数与闸自己实测的维数逐字对比 ⇒ 写 `2x2` 也绿、写 `9x9` 也绿** ★
★**本单边界**: ★**零写板 · 零落表 · 零改已签收页 · 零改已签收闸 · 零挂链 · 零外发 · 不代拍** ★

---

## B1 结论摘要

★**结论 1 (标签 / 维数)**: ★**官方 `Connector_PinHeader_1.27mm.pretty` 的两个 SMD 变体 (`PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` / `_Pin1Right`), 自己解析 `.kicad_mod` 的 pad 坐标 ⇒ 都是 ★**pads=4 · 列=2 (X = ±1.5) · 行=4 (Y = ±0.635 / ±1.905) · 沿 Y 递增时列序左右交替** ★ ⇒ ★**排布 token = `2x4_staggered`** ★; 官方 THT 变体 `PinHeader_1x04_P1.27mm_Vertical` 实测 ⇒ ★**`1x4` (沿局部 Y 一列)** ★ · 证据等级 ★`[实测]` ★

★**结论 2 (已签收页的错标签)**: ★**已签收页 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 的机器块写 `"arrangement": "2x2 staggered"` (L391), 正文 6 处写「2 列 × 2 行交错」(L45 / L203 / L207 / L288) 与「2x2」(L471 / L719) ⇒ 共 ★**7 处** ★ 与实测不符; ★**同一页 L208 又写着「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」⇒ 该页自相矛盾** ★ · 证据等级 ★`[实测]` ★

★**结论 3 (标签错 ≠ 结论错)**: ★**降级方案的铜箔包络 `6.0000 × 4.4600` 本来就是按「X 向 2 列 (中心距 3.00) 且 pad 长 3.00」+「Y 向 4 行 (中心 ±0.635 / ±1.905) 且 pad 高 0.65」算出来的 ⇒ 数字与 `2x4` 完全相容** ★ ⇒ ★**铜箔包络 / 必须清空区 Y / 两个旋转档的开口余量与三档 Y 判决 / `CRIT` 判定, 一个数字都不改** ★ · 证据等级 ★`[实测]`(脚本实跑) + ★`[推算]`(本单实算) ★

★**结论 4 (旧闸 `G5` 的真盲区)**: ★**`MECH/check_jdebug_1p27_clearance.py` 的 `G5` (L576~L618) 只判 ① 降级方案几何被独立实测并单列 ② 页面 `arrangement` 字符串里【含】 `staggered` / `交错` (L589~L591) ⇒ 【从不】把页面声明的维数与闸自己实测的维数逐字对比** ★ ⇒ ★**「错标签能活着签收」的根因就在这里** ★ · 证据等级 ★`[实测]`(源码实读) ★

★**结论 5 (本单交了什么)**: ★**新页 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` (新建) + 新闸 `MECH/check_jdebug_arrangement_truth.py` (`J0`~`J5` · 10 条反向用例全抓到 · 零挂链) + 订正块草稿 (7 处逐处清单)** ★ ⇒ ★**订正块只起草, 落在哪一页 / 哪一批 / 什么时机由 main 裁** ★

---

## B2 验收标准自评

★**逐条自评 (★通过 / 不通过 / 未验★)★**:

| # | 验收标准 | 自评 | 实测依据 |
|---|---|---|---|
| 1 | ★**新页存在且机器块可解析, `land_smd.arrangement` 与实测 token 逐字相等** ★ | ★**通过** ★ | ★`python3 MECH/check_jdebug_arrangement_truth.py` ⇒ `[J2] ✅ PASS` ; 新页可复跑重生成: `python3 tmp/iss382_sbx/gen_truth.py` ⇒ `LINT: CLEAN` ★ |
| 2 | ★**三个变体排布自己实测 (两个 SMD + 一个 THT), 不拿 md5 锚当答案** ★ | ★**通过** ★ | ★`[J1] ✅ PASS` ; 三个 `.kicad_mod` md5 锚与盘上现值一致 (THT `7a5f470c…` / Left `9d6b0e63…` / Right `1579ee40…`) ★ |
| 3 | ★**已签收页排布表述逐处扫出, 与实测不符的一处都不许漏 (7 处)** ★ | ★**通过** ★ | ★`[J3] ✅ PASS` ; 输出逐条点名 L45 / L203 / L207 / L288 / L391 / L471 / L719 ★ |
| 4 | ★**「标签错」与「结论错」分开判: 结论值独立重算后逐项相等** ★ | ★**通过** ★ | ★`[J4] ✅ PASS` ; 铜箔包络 / `required_open_y` / rot0·rot90 余量与三档判决逐项相等 ★ |
| 5 | ★**证据等级五级白名单 + 零挂起措辞 + 零挂链 + 判据句/事实句分开写** ★ | ★**通过** ★ | ★`[J5] ✅ PASS` ; `grep -c check_jdebug_arrangement_truth state/gate_check.py` ⇒ `0` ★ |
| 6 | ★**板三项指纹未动 (零写板)** ★ | ★**通过** ★ | ★`[J0] ✅ PASS` ; md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` (开工前后逐字相同) ★ |
| 7 | ★**闸自证: 11 条用例 (10 条反向用例 + 1 条落地用例) 全抓到, 末行 `ALL TESTS PASS`** ★ | ★**通过** ★ | ★`python3 MECH/check_jdebug_arrangement_truth.py --selftest` ⇒ rc=0 · 末行逐字 `ALL TESTS PASS` (上一行是 `【自检结论】✅ 11 条用例全抓到 (且无额外判据被误红)`) ★ |
| 8 | ★**零改已签收件: `BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 `check_jdebug_1p27_clearance.py` 两个 md5 开工前后逐字相同** ★ | ★**通过** ★ | ★开工前 md5 `da7b02c013fa49c65b70ed3bea97b787` / `a9914b2c3e9f8f92f1fbb60d1d8bdd86` ⇒ 交卷后逐字相同 (见回复正文实测输出) ★ |
| 9 | ★**零落表: 三张表 md5 开工前后逐字相同** ★ | ★**通过** ★ | ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 开工前后逐字相同 ★ |
| 10 | ★**零改既有闸 (四个) + 零改既有页面正文 (四页)** ★ | ★**通过** ★ | ★`check_connector_clearance_caliber.py` / `check_juart_1p27_clearance.py` / `check_onepass_mech_release.py` / `check_onepass_struct_crosscheck.py` 与四页正文开工前后逐字相同 ★ |
| 11 | ★**既有闸零漂移: `check_jdebug_1p27_clearance.py` 与 `check_connector_clearance_caliber.py` 前后读数逐字相同** ★ | ★**通过** ★ | ★`K7` 基线红 2 条是开工前就有的 (ISS-374 cont2 追加已签收页所致), 交卷后读数与 `logs/iss382/before_check_connector_caliber.log` 逐字相同, ★**本单没有让它多红一条** ★ |
| 12 | ★**交卷页 `B1`~`B6` 六段齐全且标题含 gate_check 要的关键词** ★ | ★**通过** ★ | ★`python3 state/gate_check.py` ⇒ Q1 齐备率 ★**18/18** ★, 无回退 ★ |
| 13 | ★**零外发 (不发邮件 / 询价 / 问询 / 采购)** ★ | ★**通过** ★ | ★本单全程只读本机文件 + 跑脚本, 未发出任何外发请求 ★ |
| 14 | ★**不代拍: 4 条未决项只登记, 不替 main 裁决** ★ | ★**通过** ★ | ★新页 §4 逐条列「要谁回答什么 + 本单给了什么事实 + 证据等级」; 分片 `needs_from` 4 条 `to=main` ★ |
| 15 | ★**沙盒只落 `tmp/iss382_sbx/` + `logs/iss382/`, 不写系统 `/tmp`, 不用 `cp -al`** ★ | ★**通过** ★ | ★本单沙盒 = `tmp/iss382_sbx/` (脚本自建) + `logs/iss382/` (只写日志); 闸的 selftest 沙盒由闸自己建在 `<root>/tmp/iss382_sbx/selftest/`; ★**全本单零次 `cp -al`** ★ |
| 16 | ★**不自签 `state/issue_log.yaml`, 不写别人的分片** ★ | ★**通过** ★ | ★只走 `state/frag_write.py --agent mech-lead`; `hw.yaml` / `sw.yaml` / `pm.yaml` 一个字都没写 ★ |
| 17 | ★**main 落完订正块后, 本闸【一条红都不新增】(★这是「订正块敢不敢落」的前提★)** ★ | ★**通过** ★ | ★闸的落地用例 ⑪ 实跑 ⇒ 红组 `∅` ; 新页 §2.4 逐条写明这个设计 (★台账按 surface open/landed 判 + `J4` 判定结果不随标签变化★) ★ |

★**总体自评**: ★**17 条验收标准全部「通过」; 本单交付物 = 新页 + 新闸 + 交卷页 + 分片登记, 零写板 / 零落表 / 零改已签收件 / 零挂链 / 零外发 / 不代拍** ★

★**本单对新闸的 8 处修改 (★改了哪条判据 + 为什么原来的判据是错的★)★**:
★**① `canon_token` 幂等性** (★原式让闸自己的 canonical token 不是自己的不动点 ⇒ 页面按 canonical 写法声明真实排布时 `J2`/`J3` 永远红 ⇒ 误报★) ·
★**② `canon_token` 空白口径** (★原式把空白压成单空格 ⇒ `2x4 staggered` 与 `2x4_staggered` 规范化后不相等 ⇒ 误报★) ·
★**③ `J3` 台账覆盖判据补成「同一 tuple 的条目数 ≥ 该 tuple 的错表述处数」** (★原文只判「有没有」⇒ 漏登记漏检★) ·
★**④ `J3` 台账自洽** (★新增: 台账登记的每一条必须真的与实测不符, 且 `proposed` 必须逐字等于实测 token ⇒ 台账自己不许写错★) ·
★**⑤ `ctx["signed_rel"]` 从未被赋值** (★闸一跑到 `J3` 就 `KeyError` 崩溃·运行期缺陷★) ·
★**⑥ `J4` 的判据分离自证改成「不硬编码已签收页现在必然是错的」** (★原式写死「已签收页的 `arrangement` 必须 ≠ 实测 token」⇒ main 落完订正块后本闸反而会红 ⇒ 等于本单自己制造新红; 改成: 把同一个 `land_smd` 的 `arrangement` 换成实测 token 与换成 `9x9_staggered`, `J4` 的判定结果必须逐字相同 ⇒ 结构上证明 `J4` 不读标签字段★) ·
★**⑦ `J5` 的「§1/§2 表格每个数据行都要带证据等级」判据修正表头识别** (★原式把 Markdown 表头行当数据行 ⇒ 本单自己的页必红 ⇒ 误报★) ·
★**⑧ 末尾打印文案** (★把本单真相页声明的标签写成「已签收页机器块」⇒ 与事实相反·只改文案, 不动判据★)** ★
⇒ ★**8 处都只修误报 / 补漏检 / 修崩溃 / 去掉硬编码假设, 没有任何一处放松判据** ★ · 详见新页 §3.4 / §3.5

---

## B3 证据分级

★**本单全部结论按五级标注 (★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`★)★**:

| # | 断言 | 证据等级 | 复现命令 / 出处 |
|---|---|---|---|
| 1 | ★**两个官方 SMD 变体排布 = `2x4_staggered` (2 列 × 4 行交错)** ★ | ★`[实测]` ★ | ★`python3 MECH/check_jdebug_arrangement_truth.py` ⇒ `[J1]` ; 或直接 `grep -nE '\(pad ' .../PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` ★ |
| 2 | ★**官方 THT 变体排布 = `1x4`** ★ | ★`[实测]` ★ | ★同上 `[J1]`; `.kicad_mod` L177/L184/L191/L198 pad 1~4 坐标 (0,0)/(0,1.27)/(0,2.54)/(0,3.81) ★ |
| 3 | ★**已签收页 7 处错标签 (L45/L203/L207/L288/L391/L471/L719)** ★ | ★`[实测]` ★ | ★`python3 tmp/iss382_sbx/gen_ledger.py` (逐处 claim 清单) + 闸 `[J3]` 逐条点名 ★ |
| 4 | ★**降级方案结论值 (铜箔包络 / 开口余量 / 三档 Y 判决) 独立重算后与已签收页逐项相等** ★ | ★`[实测]`(脚本实跑) + ★`[推算]`(本单实算) ★ | ★闸 `[J4]` : 用 `.kicad_mod` 实测 pad 坐标 + `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 权威开口 X/Y + `MECH/service_port_check.py` 的 `CRIT` 重算 ★ |
| 5 | ★**旧闸 `G5` 只判「含 `staggered` / `交错`」, 从不对比维数 ⇒ ★**沙盒实跑: 把已签收页维数改成 `9x9 staggered`, 旧闸照样 `✅ PASS` (rc=0)★** ⇒ 真盲区实测成立, 不是推测 ★ | ★`[实测]`(源码实读 + 沙盒实跑) ★ | ★`MECH/check_jdebug_1p27_clearance.py` L576~L618, 判据在 L589~L591 ; ★`python3 tmp/iss382_sbx/prove_g5_blindspot.py` ⇒ 旧闸 `[G5] ✅ PASS` (rc=0) 而本单新闸 `J3` ❌ FAIL (点名 `L392` 的 `9x9` 漏登记) + `J2` ❌ FAIL (点名 列数 9≠2 / 行数 9≠4) ; 原始输出 `logs/iss382/prove_g5_blindspot.log` ★ |
| 6 | ★**板三项指纹 (19 天逐字节未动)** ★ | ★`[实测]` ★ | ★`md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y %s'` ★ |
| 7 | ★**三个 `.kicad_mod` md5 锚与盘上现值一致 (⇒ 标签是从一开始就写错的, 不是库件变了的陈旧锚)** ★ | ★`[实测]` ★ | ★`md5sum .../Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical*.kicad_mod` ★ |
| 8 | ★**零挂链 (新闸不挂 `state/gate_check.py`)** ★ | ★`[实测]` ★ | ★`grep -c check_jdebug_arrangement_truth state/gate_check.py` ⇒ `0` ★ |
| 10 | ★**main 落完 7 条订正块后, 本闸【一条红都不新增】(红组 `∅`)** ★ | ★`[实测]` ★ | ★闸的反向用例/落地用例 ⑪ (★`--selftest` 实跑·★台账按 surface open/landed 判·★`J4` 的判定结果不随 `arrangement` 标签变化★) ★ |
| 9 | ★**厂商型号 / 厂商 keepout 图纸 (J_DEBUG 这颗排针到底是哪家的)** ★ | ★`[0数据]` ★ | ★本单零外发、只做官方 KiCad 库件实测 ⇒ ★**厂商型号本机无数据, 不猜、不编** ★ |

★**证据分级的边界说明 (★不许把 [实测] 往上抬★)★**: ★**本单全部是「本机文件实读 + 脚本实跑」, 没有一条来自厂商官网 / 媒体 / 询价回信 ⇒ 本单没有 [官网] 级断言, 也不需要** ★

---

## B4 接口取值声明

★**本单登记 2 条 `interface_claims` (★跨模块取值口径·★冲突才能被检出★)★**:

| # | key | value | 口径说明 (★note★) |
|---|---|---|---|
| 1 | ★`jdebug_smd_arrangement_verdict` ★ | ★`2x4_staggered` (★2 列 × 4 行交错★) ★ | ★**排布判定口径**: 官方两个 SMD 变体 (`Pin1Left` / `Pin1Right`) 自己解析 `.kicad_mod` 的 pad 坐标 ⇒ pads=4 · 列=2 (X = ±1.5) · 行=4 (Y = ±0.635 / ±1.905) · 沿 Y 递增时相邻两行的列号左右交替 ⇒ token = `2x4_staggered`; ★**官方 THT 变体 = `1x4` (沿局部 Y 一列), 与 SMD 变体不是一回事** ★; ★**任何模块要引用「降级方案排布」, 一律用 `2x4_staggered`, 不许用 `2x2`** ★ (★ISS-382·mech-lead·2026-11-24★) ★ |
| 2 | ★`jdebug_arrangement_label_vs_conclusion` ★ | ★`标签 (维数) 错 ≠ 结论数字错` ★ | ★**判定口径**: 排布标签写错时, 降级方案的【铜箔包络 / 必须清空区 Y / 开口余量 / 三档 Y 判决 / `CRIT` 判定】一个数字都不许跟着改 —— 本单已独立重算逐项核对, 全部相等 ⇒ ★**订正块只许改「标签 / 维数」那一类表述** ★; ★**判据句与事实句分开写: 判据 = 声明的 token 必须与实测 token 逐字相等; 事实 = 实测 token 是 `2x4_staggered`** ★ (★ISS-382·mech-lead·2026-11-24★) ★ |

★**接口冲突自检 (★本单声明的两条口径与既有登记不冲突★)★**: ★**既有登记里 `J_DEBUG` 的铜箔包络 `6.0000 × 4.4600` (ISS-371) 与本单口径一致 —— 因为那个包络本来就是按 2 列 × 4 行算的; 本单唯一与既有登记冲突的只是【排布标签字样】, 而已签收页一个字节都没改, 所以【当前盘面无冲突】, 冲突会出现在 main 落订正块的那一刻, 由 main 裁落点** ★

---

## B5 未决项与卡点

★**4 条未决项 (★要谁回答什么 · 本单只登记不代拍 · ★不代拍 = 不替 main 裁决落点 / 改旧闸 / 挂链★)★**:

| # | 未决项 | 要谁回答 | 本单给了什么事实 | 证据等级 | 卡点 |
|---|---|---|---|---|---|
| 1 | ★**订正块落在哪一页 / 哪一批 / 什么时机** ★ | ★**main** ★ | ★**新页 §2.1 逐处清单 (7 处, 逐条给「页里写的 ⇒ 实测是什么 ⇒ 建议改成什么」) + §2.2 结论数字全部不动的事实 + §2.4「落订正块后本闸不新增红」的实测 (落地用例 ⑪ ⇒ 红组 `∅`) + 先例代价 (ISS-374 cont2 追加已签收页 ⇒ `MECH/check_connector_clearance_caliber.py` 的 `K7` 立刻红 2 条)** ★ | ★`[实测]` ★ | ★**落点由 main 裁; 本单只起草, 未落** ★ |
| 2 | ★**`G5` 的维数逐字对比判据怎么落进既有闸 (改旧闸 vs 新闸独立挂)** ★ | ★**main** ★ | ★**新页 §3.1 盲区位置 (2 条) + §3.2 规范化口径 (4 条) + §3.3 三条反向用例 (`2x2` / `2x4` / `9x9`) + §3.4 为何不改旧闸 (3 条) + §3.5 本闸落成什么 (4 条) + 本单新闸 `J2`/`J3` 已实现同一口径 (零挂链, 可随时并入)** ★ | ★`[实测]` ★ | ★**本单零改已签收闸 `MECH/check_jdebug_1p27_clearance.py` 一个字节都没动** ★ |
| 3 | ★**「标签错」要不要连带改页里引用该标签的结论句 (`L471` 的 `verdict` / `L719` 的 `verdict_summary` 文本里带着错标签字样)** ★ | ★**main** ★ | ★**新页 §2.2 已逐项独立重算: 结论数字与 `2x4` 相容 ⇒ 结论句本身不需要改; 但文本字样改不改由 main 裁** ★ | ★`[实测]` + ★`[推算]` ★ | ★**本单只登记, 未改** ★ |
| 4 | ★**本单新闸要不要挂进 `state/gate_check.py`** ★ | ★**main** ★ | ★**本单零挂链 (`grep -c` ⇒ 0); 挂链会改变 Q1/Q3 计分口径, 归 main** ★ | ★`[实测]` ★ | ★**本单零挂链** ★ |

★**另附一条 [0数据] 登记 (★不是卡点, 是本机没有的东西★)★**: ★**`J_DEBUG` 这颗排针的厂商具体型号 + 厂商 keepout 图纸, 本机无数据** ★ ⇒ ★**本单零外发 (不发询价 / 问询 / 采购), 只做官方 KiCad 库件实测; 该项已在分片 `needs_from` 登记给 hw-lead** ★

★**卡点状态 (★交卷时点★)★**: ★**本单无技术卡点; 4 条未决项全部是【要 main 裁】的决策项, 不是缺数据** ★

---

## B6 自证复现命令

★**★每条命令都可在本机独立复跑, 期望值已写明★**:

| # | 目的 | 命令 | 期望 |
|---|---|---|---|
| 1 | ★**本单新闸 (正跑)** ★ | ★`python3 MECH/check_jdebug_arrangement_truth.py` ★ | ★**rc=0 · `J0`~`J5` 全 PASS · 末行「合计: 6/6 条判据通过」** ★ |
| 2 | ★**本单新闸 (反向用例)** ★ | ★`python3 MECH/check_jdebug_arrangement_truth.py --selftest` ★ | ★**rc=0 · 末行 `ALL TESTS PASS`** ★ |
| 3 | ★**已签收闸零漂移** ★ | ★`python3 MECH/check_jdebug_1p27_clearance.py` ★ | ★**rc=0 · 与开工前读数逐字相同** ★ |
| 4 | ★**既有闸零漂移 (`K7` 基线红 2 条不许变)** ★ | ★`python3 MECH/check_connector_clearance_caliber.py` ★ | ★**rc=0 · 与 `logs/iss382/before_check_connector_caliber.log` 逐字相同** ★ |
| 5 | ★**排布逐处扫描 (不进闸也能复现)** ★ | ★`python3 tmp/iss382_sbx/gen_ledger.py` ★ | ★**打印 10 处 claim 清单 + 重建 `tmp/iss382_sbx/ledger.json`** ★ |
| 6 | ★**新页重新生成 (可复跑)** ★ | ★`python3 tmp/iss382_sbx/gen_truth.py` ★ | ★**打印 `LINT: CLEAN` + 重写 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md`** ★ |
| 7 | ★**板三项指纹 (零写板自证)** ★ | ★`md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` ★ | ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★ |
| 8 | ★**零改已签收件 / 零落表 / 零改既有闸 (开工前后对比)** ★ | ★`md5sum MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md MECH/check_jdebug_1p27_clearance.py HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv MECH/check_connector_clearance_caliber.py MECH/check_juart_1p27_clearance.py MECH/check_onepass_mech_release.py MECH/check_onepass_struct_crosscheck.py` ★ | ★**与 `logs/iss382/before_fingerprints.txt` 逐字相同** ★ |
| 9 | ★**零挂链自证** ★ | ★`grep -c check_jdebug_arrangement_truth state/gate_check.py` ★ | ★**0** ★ |
| 10 | ★**门禁链 (Q1 必须 18/18)** ★ | ★`python3 state/merge.py && python3 state/gate_check.py` ★ | ★**rc=0 · Q1 齐备率 18/18** ★ |
| 11 | ★**派活书命令自检** ★ | ★`python3 state/check_brief_commands.py` ★ | ★**rc=0** ★ |
| 11b | ★**旧闸 `G5` 真盲区的沙盒实跑证明** ★ | ★`python3 tmp/iss382_sbx/prove_g5_blindspot.py` ★ | ★**旧闸 `[G5] ✅ PASS` (rc=0, ★维数被改成 `9x9 staggered` 它照样绿★) ; 本单新闸 `J3` ❌ FAIL (点名 L392) + `J2` ❌ FAIL (点名 列数/行数差)** ★ |
| 12 | ★**库件实测直接复现** ★ | ★`grep -nE '\(pad ' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` ★ | ★**pad 坐标 (±1.5, ±0.635 / ±1.905) ⇒ 2 列 × 4 行** ★ |

★**★零外发声明 (★写在最后·★因为它是硬红线★)★**: ★**本单全程没有发出任何邮件 / 询价 / 问询 / 采购请求; 厂商信息一律本机查 (官方 KiCad 库件实测), 查不到的就写 `[0数据]` 并登记成 need, 不猜、不编、不发信** ★
