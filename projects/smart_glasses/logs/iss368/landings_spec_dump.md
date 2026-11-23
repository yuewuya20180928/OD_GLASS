# 自动导出的三处落点逐字规格 (★由 apply_sw09_three_place_patch.py 的 EDITS 表直接导出·零手抄★)

★落点③ = `SW/tools/check_fp_truth_read.py` (★只验不改·md5 基线 cab7a6f17c1da35f4e54185ad8b62089★)

---- eid=A1 · spot=①清单页 SW/BOARD_ONEPASS_SW_SYNC.md · file=SW/BOARD_ONEPASS_SW_SYNC.md · kind=replace · where=§2 逐条表 · 小节头
【定位串(唯一锚点)】
<<<OLD>>>
## §2 · 逐条表 (★每条固定 9 个字段 · ★★8 条一条不许漏★★)
<<<NEW>>>
## §2 · 逐条表 (★每条固定 9 个字段 · ★★9 条一条不许漏★★)
<<<END>>>
【自证】 ★grep「★★9 条一条不许漏★★」命中 1 次 · ★且 §6 JSON 块 items 长度 == 9★

---- eid=A2 · spot=①清单页 SW/BOARD_ONEPASS_SW_SYNC.md · file=SW/BOARD_ONEPASS_SW_SYNC.md · kind=insert_after_line · where=§2 逐条表 · 第 9 行
【定位串(唯一锚点)】
| ★**`SW08_ESD_USB_D`** ★ | ★ISS-266+ISS-279 ★ |
<<<PAYLOAD>>>
| ★**`SW09_FP_TRUTH_READ`** ★ | ★ISS-241+ISS-244 ★ | ★**S10 换封装真值: 三份真源的封装栏 (fp 栏) 必须与板面库封装名逐行一致 (★SW 侧第一跳 = 把那一栏从「没人读」变成「有闸读」★)** ★ | ★**S10** ★ | ★**板那一趟 (★板面库封装名补齐 ⇒ 归板侧/hw-lead★) + main→老板 (★加新判据 = 改判据 = 受保护资产★)** ★ | ★**[实测] 板面 186 个封装的库封装名【全空】(0/186 非空) ⇒ 「库封装名」这个真值在板面上现在不存在 ⇒ 三份真源的 fp 栏自然也换不了 ⇒ ① 网表 513 行里 423 行 fp 空 (170 个 ref 板上有) ② 脚表 584 行里 454 行 fp 空 (172 个 ref 板上有) ③ BOM 218 行 fp 全非空, 但 178 行写「待定」(81.7%) ④ BOM 的 `J_USB_C` 写「16 焊盘」而板面实际 18 个 pad (机械孔算不算焊盘的口径差) ⇒ SW 侧第一跳只能是【让那一栏机器读得到 + 把真值来源钉死】, 换真值那一跳要等板侧先补库封装名** ★ | ★**python3 SW/tools/check_fp_truth_read.py ⇒ rc=0 (★F1 那一栏按表头名可读 + F2 盘上 md5 == 落表台账链头 + F4 清单登记条数 == 本机实测条数★) ; python3 SW/tools/check_sw_fp_truth_impact.py ⇒ rc=0 (★ISS-362 的 H1/H4 登记式绿 ⇒ 加第 9 条那天, §H4-REG 的三个数字要同批同步★)** ★ |
<<<END>>>
【自证】 ★§2 表里 grep「`SW09_FP_TRUTH_READ`」命中 1 次 (★且该行 7 列齐全★)★

---- eid=A3 · spot=①清单页 SW/BOARD_ONEPASS_SW_SYNC.md · file=SW/BOARD_ONEPASS_SW_SYNC.md · kind=replace · where=§2.1 归属步分布 · S10 行
【定位串(唯一锚点)】
<<<OLD>>>
| ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` ★ |
<<<NEW>>>
| ★**S10** ★ | 4 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` · `SW09_FP_TRUTH_READ` ★ |
<<<END>>>
【自证】 ★§2.1 表里 S10 行条数 == 4 且条目含 `SW09_FP_TRUTH_READ`★

---- eid=A4 · spot=①清单页 SW/BOARD_ONEPASS_SW_SYNC.md · file=SW/BOARD_ONEPASS_SW_SYNC.md · kind=json_append · where=§6 机器可读 JSON 块 · items[]
【定位串】= §6 机器可读 JSON 块 items[] 末尾追加
<<<PAYLOAD-JSON>>>
{
  "id": "SW09_FP_TRUTH_READ",
  "source_iss": "ISS-241+ISS-244",
  "title": "S10 换封装真值: 三份真源的封装栏 (fp 栏) 必须与板面库封装名逐行一致 (★SW 侧第一跳 = 把那一栏从「没人读」变成「有闸读」★)",
  "current_state": "[实测] 板面 186 个封装的库封装名【全空】(0/186 非空) ⇒ 「库封装名」这个真值在板面上现在不存在 ⇒ 三份真源的 fp 栏自然也换不了 ⇒ ① 网表 513 行里 423 行 fp 空 (170 个 ref 板上有) ② 脚表 584 行里 454 行 fp 空 (172 个 ref 板上有) ③ BOM 218 行 fp 全非空, 但 178 行写「待定」(81.7%) ④ BOM 的 `J_USB_C` 写「16 焊盘」而板面实际 18 个 pad (机械孔算不算焊盘的口径差) ⇒ SW 侧第一跳只能是【让那一栏机器读得到 + 把真值来源钉死】, 换真值那一跳要等板侧先补库封装名",
  "action": "板侧那一趟 (★板只改一次 ⇒ 这一跳必须落在那一趟里★): 先把板面 186 个封装的库封装名补成真库封装名 ⇒ ★**同批** (★一次落表批次·不许分两批★) 把三份真源的 fp 栏换成【同一个库封装名字符串】⇒ 三份真源 md5 同批变 ⇒ 落表台账同批留痕 ⇒ SW 侧同批把 F1 的期望值 (哪一行该是什么值) 跟着走 ⇒ ★**不许只改一处 (★三处同批★)**",
  "criterion": "python3 SW/tools/check_fp_truth_read.py ⇒ rc=0 (★F1 那一栏按表头名可读 + F2 盘上 md5 == 落表台账链头 + F4 清单登记条数 == 本机实测条数★) ; python3 SW/tools/check_sw_fp_truth_impact.py ⇒ rc=0 (★ISS-362 的 H1/H4 登记式绿 ⇒ 加第 9 条那天, §H4-REG 的三个数字要同批同步★)",
  "step": "S10",
  "blocked_by": "板那一趟 (★板面库封装名补齐 ⇒ 归板侧/hw-lead★) + main→老板 (★加新判据 = 改判据 = 受保护资产★)",
  "evidence": "[实测]"
}
<<<END>>>
【自证】 ★§6 JSON 块 items 长度 == 9 且 items[8].id == SW09_FP_TRUTH_READ 且 9 字段齐全非空★

---- eid=B1 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=页首边界句
【定位串(唯一锚点)】
<<<OLD>>>
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · ★**不许往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条** (★那是「改那一趟的清单」⇒ 归 main 裁★) ★
<<<NEW>>>
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · ★**第 9 条 (`SW09_FP_TRUTH_READ`) 已按 main 2026-11-23 16:58 的裁决「加」同批落地** (★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 + 本页 §H4-REG 三个数字同步★) ⇒ ★**本页后续【不许】单改一处** (★只改一处 ⇒ H4 红 + F4 红★) ★
<<<END>>>
【自证】 ★grep「已按 main 2026-11-23 16:58 的裁决「加」同批落地」命中 1 次★

---- eid=B2 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§1 逐闸表 G01 行
【定位串(唯一锚点)】
<<<OLD>>>
(★板侧输入清单 8 条 + W5 现状探针 + W6 受保护 5 件台账对账★)
<<<NEW>>>
(★板侧输入清单 9 条 + W5 现状探针 + W6 受保护 5 件台账对账★)
<<<END>>>
【自证】 ★grep「板侧输入清单 9 条」命中 1 次★

---- eid=B3 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · 小节头
【定位串(唯一锚点)】
<<<OLD>>>
### H4-REG · 8 条板侧输入清单里没有「S10 换封装真值」这一条
<<<NEW>>>
### H4-REG · 9 条板侧输入清单里已有「S10 换封装真值」这一条 (★`SW09_FP_TRUTH_READ`★)
<<<END>>>
【自证】 ★grep「9 条板侧输入清单里已有」命中 1 次★

---- eid=B4 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-ITEMS
【定位串(唯一锚点)】
<<<OLD>>>
- H4-ITEMS: 8
<<<NEW>>>
- H4-ITEMS: 9
<<<END>>>
【自证】 ★H4-REG 块里 `H4-ITEMS` == 9★

---- eid=B5 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-COVER
【定位串(唯一锚点)】
<<<OLD>>>
- H4-COVER: 0
<<<NEW>>>
- H4-COVER: 1
<<<END>>>
【自证】 ★H4-REG 块里 `H4-COVER` == 1★

---- eid=B6 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-GENERIC
【定位串(唯一锚点)】
<<<OLD>>>
- H4-GENERIC: 4
<<<NEW>>>
- H4-GENERIC: 5
<<<END>>>
【自证】 ★H4-REG 块里 `H4-GENERIC` == 5★

---- eid=B7 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-FINDING
【定位串(唯一锚点)】
<<<OLD>>>
- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单 (SW01~SW08) 里, 没有任何一条的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 0** ★ ⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上是【完全空白的】** ★
<<<NEW>>>
- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 9 条清单 (SW01~SW09) 里, 已有 1 条 (`SW09_FP_TRUTH_READ`) 的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 1** ★ ⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上已被【收口】** (★第 9 条于 2026-11-23 按 main 16:58 裁决「加」同批落地★) ★
<<<END>>>
【自证】 ★H4-FINDING 非空且含「覆盖条数 = 1」★

---- eid=B8 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-IMPACT
【定位串(唯一锚点)】
<<<OLD>>>
- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它没有的跳 ⇒ 那一趟当天就没有人认领这一跳 ⇒ 这一跳红/不红都没人解释 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ 风险 = 有人为了让闸绿去改锚点 / 改判据** ★
<<<NEW>>>
- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它有的跳 ⇒ 那一趟当天有人认领这一跳 ⇒ 这一跳红/不绿都有判据 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ 风险 = 有人为了让闸绿去改锚点 / 改判据** ★
<<<END>>>
【自证】 ★H4-IMPACT 非空★

---- eid=B9 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · H4-COUNTERMEASURE
【定位串(唯一锚点)】
<<<OLD>>>
- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ 空白被【登记】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★本单【不许】直接往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 ⇒ 那是「改那一趟的清单」⇒ 归 main 裁★** ★ ⇒ ★**要加的话, 加的写法建议见本页交卷页 B5-2 (★归 main 转 hw-lead / 板侧作业包那一趟★)** ★
<<<NEW>>>
- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ 这一跳被【收口】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★第 9 条 (`SW09_FP_TRUTH_READ`) 已按 main 2026-11-23 16:58 的裁决「加」同批落地** (★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 + 本页 §H4-REG 三个数字同步★) ⇒ ★**对应的机器闸 `SW/tools/check_fp_truth_read.py` 已交 (★ISS-363★) ⇒ 第 9 条与那一栏的判据都在机器上可查** ★
<<<END>>>
【自证】 ★H4-COUNTERMEASURE 非空且含「已按 main 2026-11-23 16:58 的裁决「加」同批落地」★

---- eid=B10 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§H4-REG 块 · 附注 (H4-GENERIC 的含义)
【定位串(唯一锚点)】
<<<OLD>>>
- ★**附: `H4-GENERIC=4` 的含义** ★: ★**8 条里有 4 条 (SW02 / SW04 / SW07 / SW08) 的 `current_state` / `action` 里泛泛提到过「封装」二字, 但没有一条说的是【封装栏落真值】⇒ 也就是说: 「泛提封装」的那 4 条, **一条都不覆盖这一跳** ⇒ 覆盖条数仍然是 0** ★
<<<NEW>>>
- ★**附: `H4-GENERIC=5` 的含义** ★: ★**9 条里有 5 条 (SW02 / SW04 / SW07 / SW08 / SW09) 的 `current_state` / `action` 里提到过「封装」二字, 其中只有 SW09 这一条说的是【封装栏落真值】⇒ 也就是说: 「泛提封装」的那 4 条 (SW02 / SW04 / SW07 / SW08) **一条都不覆盖这一跳** ⇒ 覆盖条数 = 1 (★只算 SW09★)** ★
<<<END>>>
【自证】 ★grep「附: `H4-GENERIC=5` 的含义」命中 1 次★

---- eid=B11 · spot=②影响页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · file=SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · kind=replace · where=§5 证据分级 · 覆盖条数那一行
【定位串(唯一锚点)】
<<<OLD>>>
| 8 条板侧输入清单覆盖这一跳的条目 = 0 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |
<<<NEW>>>
| 9 条板侧输入清单覆盖这一跳的条目 = 1 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |
<<<END>>>
【自证】 ★grep「9 条板侧输入清单覆盖这一跳的条目 = 1」命中 1 次★

