# ISS-368 · SW09_FP_TRUTH_READ 三处同批落地补丁 (一页)

> ★**本单性质** ★: 纯作业包 + 沙盒 dry-run + 一条新闸 · ★**零写板 · 零落表 · 零改既有闸 · 真件三处零改 · 零外发 · 不代拍** ★
> ★**本单不碰真件** ★: `SW/BOARD_ONEPASS_SW_SYNC.md` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` · `SW/tools/check_fp_truth_read.py` 三件 ★**真件一个字节都没动** ★ ⇒ 本页只交【可执行的幂等补丁 + 副本 dry-run 证明 + 回滚说明】 ★
> ★**落表批次地界** ★: 「三处同批落地」的【真件落地】= main 在「板只改一次」那一趟的一键动作 ⇒ 本单零代劳 ★
> ★**本单的机器判据** ★: `SW/tools/check_sw09_patch_dryrun.py` (F1~F7) · 本闸 ★**不挂链** ★ (★挂不挂 `state/gate_check.py` 的 EXTRA_GATES = main 的机制地界★) ★

---

## §0 口径与读数

### §0.1 「三处同批」指的是哪三处

| 落点 | 文件 | 本单交的动作 | 真件状态 |
|---|---|---|---|
| ① 清单页 | `SW/BOARD_ONEPASS_SW_SYNC.md` | §2 小节头 · §2 逐条表第 9 行 · §2.1 归属步分布 S10 行 · §6 机器可读 JSON 块 = **4 处编辑 (A1~A4)** | ★**零改** ★ [实测] |
| ② 影响页 | `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` | 页首边界句 · §1 逐闸表 G01 行 · §H4-REG 块 (小节头 + 三个登记数字 + H4-FINDING + H4-IMPACT + H4-COUNTERMEASURE + 附注) · §5 证据分级行 = **11 处编辑 (B1~B11)** | ★**零改** ★ [实测] |
| ③ 新闸 | `SW/tools/check_fp_truth_read.py` | ★**只验不改** ★ ⇒ 只做【存在性 + 字节不变】双证 | ★**零改** ★ [实测] |

★**为什么必须三处同批** ★: 落点② 的 §H4-REG 是【动态登记 vs 实测】判据 (★ISS-362 闸 H4 + ISS-363 闸 F4 都读它★) ⇒
★**只改落点① ⇒ 登记还是 8/0/4 而实测已经是 9/1/5 ⇒ H4 红 + F4 红** ★ ·
★**只改落点② ⇒ 登记 9/1/5 而实测还是 8/0/4 ⇒ H4 红 + F4 红** ★ ·
⇒ ★**三处必须同批** ★ ⇒ 本单把它做成【一次可执行 · 幂等 · 可回滚 · 且有沙盒证明的动作】 ★

### §0.2 读数表 (★每个数字写清「哪个脚本产出 · 怎么复跑」★)

| # | 读数 | 值 | 产出脚本 | 怎么复跑 |
|---|---|---|---|---|
| R1 | 补丁编辑条数 | **15** 条 (★落点① 4 + 落点② 11★) · 异常 **0** 条 | `apply_sw09_three_place_patch.py --dry-run` | `python3 SW/tools/apply_sw09_three_place_patch.py --dry-run` |
| R2 | 干跑模式对真件的写入 | **0 字节** (★真件三处 md5 前后同值★) | 同上 + md5 复核 | 同上 + `md5sum` 三处 |
| R3 | 幂等 (第 2 遍 / 第 3 遍) | 逐字节 diff **= 0** · **= 0** | `check_sw09_patch_dryrun.py` 的 F3 | `python3 SW/tools/check_sw09_patch_dryrun.py` |
| R4 | 10 道 SW 闸 (副本上逐道实跑) | ★**绿 10 / 红 0** ★ | F4 (★读数缓存在 `tmp/iss368_sbx/gates_report.json`·副本一变缓存自动失效★) | `python3 SW/tools/check_sw09_patch_dryrun.py --run-gates` |
| R5 | 新闸 F1~F7 | ★**绿 7 / 红 0** ★ | `check_sw09_patch_dryrun.py` | `python3 SW/tools/check_sw09_patch_dryrun.py` |
| R6 | 反证「只改一处 ⇒ H4 红 + F4 红」 | **成立** (V0 全绿 · V1 红 · V2 红) | `logs/iss368/prove_partial_landing.py` | `python3 logs/iss368/prove_partial_landing.py` |
| R7 | 回滚 | 逐字节回到落地前原文 **= 是** · 回滚后 10 道闸 **绿 10 / 红 0** | `logs/iss368/prove_rollback.py` | `python3 logs/iss368/prove_rollback.py` |
| R8 | 板 md5 / mtime | `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` | `md5sum` + `stat` | `md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb` |
| R9 | 沙盒位置 | 项目盘 `tmp/iss368_sbx/patched` · 软链 **0** 个 | F7 | `python3 SW/tools/check_sw09_patch_dryrun.py` |

★**口径声明** ★: 本页所有读数**均为本机实跑输出** [实测] · 凡未实跑的数字本页**不写** [0数据] ·
★**本页不含任何官网读数** ★ (★本单不碰任何外部器件规格 ⇒ 官网证据条数 = 0★) [0数据]

---

## §1 三处落点逐字规格

★**读法** ★: 每处给【定位串】(★唯一锚点 · 不许靠行号★) +【原文】+【新文】+【改完怎么自证】 ★
★**本节的逐字规格由 `SW/tools/apply_sw09_three_place_patch.py` 的 `EDITS` 表直接导出** ★ (★零手抄 · 见 `logs/iss368/landings_spec_dump.md`★) [实测]

### §1.1 落点① · `SW/BOARD_ONEPASS_SW_SYNC.md` (4 处)

#### A1 · §2 逐条表 · 小节头

- **定位串 (唯一锚点)**: ★`## §2 · 逐条表 (★每条固定 9 个字段 · ★★8 条一条不许漏★★)` ★ (★在真件里 `grep -Fc` 命中 **1** 次★) [实测]
- **原文**:

```
## §2 · 逐条表 (★每条固定 9 个字段 · ★★8 条一条不许漏★★)
```

- **新文**:

```
## §2 · 逐条表 (★每条固定 9 个字段 · ★★9 条一条不许漏★★)
```

- **改完怎么自证**: ★grep「★★9 条一条不许漏★★」命中 1 次 · ★且 §6 JSON 块 items 长度 == 9★ [实测]

#### A2 · §2 逐条表 · 第 9 行 (★整行插入 · 锚点行本身不动★)

- **定位串 (唯一锚点)**: ★`|` + ★**`SW08_ESD_USB_D`** ★ | ★ISS-266+ISS-279 ★ |` ★ (★在真件里 `grep -Fc` 命中 **1** 次 ★ ⇒ 插在它的**下一行**★) [实测]
- **原文** (★锚点行逐字 · 落地后它**不变**★):

```
| ★**`SW08_ESD_USB_D`** ★ | ★ISS-266+ISS-279 ★ |
```

- **新文** (★插在锚点行之后的那一行 · 逐字★):

```
| ★**`SW09_FP_TRUTH_READ`** ★ | ★ISS-241+ISS-244 ★ | ★**S10 换封装真值: 三份真源的封装栏 (fp 栏) 必须与板面库封装名逐行一致 (★SW 侧第一跳 = 把那一栏从「没人读」变成「有闸读」★)** ★ | ★**S10** ★ | ★**板那一趟 (★板面库封装名补齐 ⇒ 归板侧/hw-lead★) + main→老板 (★加新判据 = 改判据 = 受保护资产★)** ★ | ★**[实测] 板面 186 个封装的库封装名【全空】(0/186 非空) ⇒ 「库封装名」这个真值在板面上现在不存在 ⇒ 三份真源的 fp 栏自然也换不了 ⇒ ① 网表 513 行里 423 行 fp 空 (170 个 ref 板上有) ② 脚表 584 行里 454 行 fp 空 (172 个 ref 板上有) ③ BOM 218 行 fp 全非空, 但 178 行写「待定」(81.7%) ④ BOM 的 `J_USB_C` 写「16 焊盘」而板面实际 18 个 pad (机械孔算不算焊盘的口径差) ⇒ SW 侧第一跳只能是【让那一栏机器读得到 + 把真值来源钉死】, 换真值那一跳要等板侧先补库封装名** ★ | ★**python3 SW/tools/check_fp_truth_read.py ⇒ rc=0 (★F1 那一栏按表头名可读 + F2 盘上 md5 == 落表台账链头 + F4 清单登记条数 == 本机实测条数★) ; python3 SW/tools/check_sw_fp_truth_impact.py ⇒ rc=0 (★ISS-362 的 H1/H4 登记式绿 ⇒ 加第 9 条那天, §H4-REG 的三个数字要同批同步★)** ★ |
```

- **改完怎么自证**: ★§2 表里 grep「`SW09_FP_TRUTH_READ`」命中 1 次 (★且该行 7 列齐全★) [实测]

#### A3 · §2.1 归属步分布 · S10 行

- **定位串 (唯一锚点)**: ★`|` + ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` ★ |` ★ (★在真件里 `grep -Fc` 命中 **1** 次★) [实测]
- **原文**:

```
| ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` ★ |
```

- **新文**:

```
| ★**S10** ★ | 4 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · `SW05_KEY_NETNAMES` · `SW09_FP_TRUTH_READ` ★ |
```

- **改完怎么自证**: ★§2.1 表里 S10 行条数 == 4 且条目含 `SW09_FP_TRUTH_READ` [实测]

#### A4 · §6 机器可读 JSON 块 · `items[]` 追加第 9 个对象

- **定位串 (唯一锚点)**: ★`SW/BOARD_ONEPASS_SW_SYNC.md` 里的 ★**唯一** ★ json 围栏块 (★围栏标记 = 三个反引号★) ⇒ 其 `items[]` 数组的**末尾** ★ (★JSON 块解析 = 唯一命中★) [实测]
- **原文**: ★`items[]` 长度 **8** (★SW01~SW08·8 个对象★) [实测]
- **新文** (★追加的第 9 个对象 · 9 字段齐全 · 逐字★):

```json
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
```

- **改完怎么自证**: ★§6 JSON 块 items 长度 == 9 且 items[8].id == SW09_FP_TRUTH_READ 且 9 字段齐全非空 [实测]

### §1.2 落点② · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` (11 处)

#### B1 · 页首边界句

- **定位串 (唯一锚点)**: ★整句 (★页首边界块里命中 **1** 次★) [实测]
- **原文**:

```
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · ★**不许往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条** (★那是「改那一趟的清单」⇒ 归 main 裁★) ★
```

- **新文**:

```
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · ★**第 9 条 (`SW09_FP_TRUTH_READ`) 已按 main 2026-11-23 16:58 的裁决「加」同批落地** (★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 + 本页 §H4-REG 三个数字同步★) ⇒ ★**本页后续【不许】单改一处** (★只改一处 ⇒ H4 红 + F4 红★) ★
```

- **改完怎么自证**: ★grep「已按 main 2026-11-23 16:58 的裁决「加」同批落地」命中 1 次 [实测]

#### B2 · §1 逐闸表 · G01 行

- **定位串 (唯一锚点)**: ★`(★板侧输入清单 8 条 + W5 现状探针 + W6 受保护 5 件台账对账★)` ★ (★命中 **1** 次★) [实测]
- **原文**:

```
(★板侧输入清单 8 条 + W5 现状探针 + W6 受保护 5 件台账对账★)
```

- **新文**:

```
(★板侧输入清单 9 条 + W5 现状探针 + W6 受保护 5 件台账对账★)
```

- **改完怎么自证**: ★grep「板侧输入清单 9 条」命中 1 次 [实测]

#### B3 · §H4-REG 块 · 小节头

- **定位串 (唯一锚点)**: ★`### H4-REG · 8 条板侧输入清单里没有「S10 换封装真值」这一条` ★ (★命中 **1** 次★) [实测]
- **原文**:

```
### H4-REG · 8 条板侧输入清单里没有「S10 换封装真值」这一条
```

- **新文**:

```
### H4-REG · 9 条板侧输入清单里已有「S10 换封装真值」这一条 (★`SW09_FP_TRUTH_READ`★)
```

- **改完怎么自证**: ★grep「9 条板侧输入清单里已有」命中 1 次 [实测]

#### B4 · §H4-REG 块 · `H4-ITEMS`

- **定位串 (唯一锚点)**: ★`- H4-ITEMS: 8` ★ (★在 §H4-REG 块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-ITEMS: 8
```

- **新文**:

```
- H4-ITEMS: 9
```

- **改完怎么自证**: ★H4-REG 块里 `H4-ITEMS` == 9 [实测]

#### B5 · §H4-REG 块 · `H4-COVER`

- **定位串 (唯一锚点)**: ★`- H4-COVER: 0` ★ (★在 §H4-REG 块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-COVER: 0
```

- **新文**:

```
- H4-COVER: 1
```

- **改完怎么自证**: ★H4-REG 块里 `H4-COVER` == 1 [实测]

#### B6 · §H4-REG 块 · `H4-GENERIC`

- **定位串 (唯一锚点)**: ★`- H4-GENERIC: 4` ★ (★在 §H4-REG 块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-GENERIC: 4
```

- **新文**:

```
- H4-GENERIC: 5
```

- **改完怎么自证**: ★H4-REG 块里 `H4-GENERIC` == 5 [实测]

#### B7 · §H4-REG 块 · `H4-FINDING`

- **定位串 (唯一锚点)**: ★整行 (★以 `- H4-FINDING:` 开头 · 在块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单 (SW01~SW08) 里, 没有任何一条的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 0** ★ ⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上是【完全空白的】** ★
```

- **新文**:

```
- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 9 条清单 (SW01~SW09) 里, 已有 1 条 (`SW09_FP_TRUTH_READ`) 的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 1** ★ ⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上已被【收口】** (★第 9 条于 2026-11-23 按 main 16:58 裁决「加」同批落地★) ★
```

- **改完怎么自证**: ★H4-FINDING 非空且含「覆盖条数 = 1」 [实测]

#### B8 · §H4-REG 块 · `H4-IMPACT`

- **定位串 (唯一锚点)**: ★整行 (★以 `- H4-IMPACT:` 开头 · 在块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它没有的跳 ⇒ 那一趟当天就没有人认领这一跳 ⇒ 这一跳红/不红都没人解释 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ 风险 = 有人为了让闸绿去改锚点 / 改判据** ★
```

- **新文**:

```
- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它有的跳 ⇒ 那一趟当天有人认领这一跳 ⇒ 这一跳红/不绿都有判据 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ 风险 = 有人为了让闸绿去改锚点 / 改判据** ★
```

- **改完怎么自证**: ★H4-IMPACT 非空 [实测]

#### B9 · §H4-REG 块 · `H4-COUNTERMEASURE`

- **定位串 (唯一锚点)**: ★整行 (★以 `- H4-COUNTERMEASURE:` 开头 · 在块内命中 **1** 次★) [实测]
- **原文**:

```
- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ 空白被【登记】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★本单【不许】直接往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 ⇒ 那是「改那一趟的清单」⇒ 归 main 裁★** ★ ⇒ ★**要加的话, 加的写法建议见本页交卷页 B5-2 (★归 main 转 hw-lead / 板侧作业包那一趟★)** ★
```

- **新文**:

```
- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ 这一跳被【收口】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★第 9 条 (`SW09_FP_TRUTH_READ`) 已按 main 2026-11-23 16:58 的裁决「加」同批落地** (★清单页 §2 表 + §2.1 分布表 + §6 JSON 块 三处同批 + 本页 §H4-REG 三个数字同步★) ⇒ ★**对应的机器闸 `SW/tools/check_fp_truth_read.py` 已交 (★ISS-363★) ⇒ 第 9 条与那一栏的判据都在机器上可查** ★
```

- **改完怎么自证**: ★H4-COUNTERMEASURE 非空且含「已按 main 2026-11-23 16:58 的裁决「加」同批落地」 [实测]

#### B10 · §H4-REG 块 · 附注 (★`H4-GENERIC` 的含义★)

- **定位串 (唯一锚点)**: ★整行 (★以 `- ★**附: `H4-GENERIC=4` 的含义** ★` 开头 · 在块内命中 **1** 次★) [实测]
- **原文**:

```
- ★**附: `H4-GENERIC=4` 的含义** ★: ★**8 条里有 4 条 (SW02 / SW04 / SW07 / SW08) 的 `current_state` / `action` 里泛泛提到过「封装」二字, 但没有一条说的是【封装栏落真值】⇒ 也就是说: 「泛提封装」的那 4 条, **一条都不覆盖这一跳** ⇒ 覆盖条数仍然是 0** ★
```

- **新文**:

```
- ★**附: `H4-GENERIC=5` 的含义** ★: ★**9 条里有 5 条 (SW02 / SW04 / SW07 / SW08 / SW09) 的 `current_state` / `action` 里提到过「封装」二字, 其中只有 SW09 这一条说的是【封装栏落真值】⇒ 也就是说: 「泛提封装」的那 4 条 (SW02 / SW04 / SW07 / SW08) **一条都不覆盖这一跳** ⇒ 覆盖条数 = 1 (★只算 SW09★)** ★
```

- **改完怎么自证**: ★grep「附: `H4-GENERIC=5` 的含义」命中 1 次 [实测]

#### B11 · §5 证据分级 · 覆盖条数那一行

- **定位串 (唯一锚点)**: ★整行 (★以 `| 8 条板侧输入清单覆盖这一跳的条目 = 0 |` 开头 · 命中 **1** 次★) [实测]
- **原文**:

```
| 8 条板侧输入清单覆盖这一跳的条目 = 0 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |
```

- **新文**:

```
| 9 条板侧输入清单覆盖这一跳的条目 = 1 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |
```

- **改完怎么自证**: ★grep「9 条板侧输入清单覆盖这一跳的条目 = 1」命中 1 次 [实测]

### §1.3 落点③ · `SW/tools/check_fp_truth_read.py` (★只验不改★)

- **定位串 (唯一锚点)**: ★文件路径本身 (★落点③ 没有可编辑的正文 ⇒ 本单对它只做双证★) [实测]
- **原文 / 新文**: ★**没有** ★ ⇒ 本补丁对落点③ 的编辑条数 = **0** ★ (★`EDITS` 表里没有任何一条 `file` 指向它★) [实测]
- **改完怎么自证**: ★md5 前后同值 + md5 == ISS-363 交卷基线 `cab7a6f17c1da35f4e54185ad8b62089` ★ [实测]

---

## §2 幂等性

### §2.1 机制 (★为什么跑第二遍零变更★)

★**补丁脚本的三种原子操作都自带幂等分支** ★ [实测]:

| 操作 | 第 1 遍 | 第 2 遍 / 第 3 遍 | 判据 |
|---|---|---|---|
| `replace` (★全文唯一替换★) | 原文命中 1 次 ⇒ 改 | 新文已存在 ⇒ 判定 `already` ⇒ **零变更** | 旧串计数必须 == 1 (★命中 > 1 ⇒ 判 `ambiguous` ⇒ fail-closed 不写盘★) |
| `insert_after_line` | 载荷不在页内 ⇒ 插入 | 载荷已在页内 ⇒ 判定 `already` ⇒ **零变更** | 锚点行必须全文唯一命中 |
| `json_append` | `items[]` 里没有同 `id` ⇒ 追加 | 已有同 `id` ⇒ 判定 `already` ⇒ **零变更** | `items[]` 按 `id` 判重 |

★**写盘闸 (★真件写不进去★)** ★: `--apply` 必须带 `--target-root` ⇒ 目标必须落在**项目盘 `tmp/` 下**且**不等于项目根** ⇒ 不满足直接 rc=2 拒写 [实测]

### §2.2 读数 (★逐字节 diff★)

- **F3 实跑**: 同一补丁在沙盒副本上连跑 **3 遍** ⇒ 第 1 遍后 / 第 2 遍后 / 第 3 遍后的两个文件 md5 **三组全同** ⇒ ★**第 2 遍 diff = 0 · 第 3 遍 diff = 0** ★ [实测]
- **干跑读数**: `python3 SW/tools/apply_sw09_three_place_patch.py --dry-run` ⇒ ★**编辑 15 条 · 变更 15 条 · 幂等命中(零变更) 0 条 · 异常 0 条** ★ rc=0 [实测]
  (★干跑基准是**真件**(未落地态)⇒ 15 条全是「变」是正常的; 幂等读数在**副本**上取★) [实测]
- **F3 的判据位置**: `SW/tools/check_sw09_patch_dryrun.py` 的 `f3_idempotent()` ⇒ 三遍 md5 两两比对 [实测]

---

## §3 dry-run 证明 (★副本上跑 · 真件零改★)

### §3.1 沙盒

- 位置 = 项目盘 `tmp/iss368_sbx/patched` (★在 `tmp/` 下 ⇒ F7 绿★) [实测]
- ★**零软链** ★ (★禁止 `os.symlink` · ISS-327 cont1 根因★) ⇒ 软链计数 = **0** [实测]
- 副本内容 = 真件全量复制 + 三处落地 ⇒ ★**真件三处 md5 与副本不同** (★F7 就是靠这个判「副本真的落地了」★) [实测]

### §3.2 10 道 SW 闸 (★副本上逐道实跑 · F4★)

| # | 闸 | rc | 耗时 |
|---|---|---|---|
| 1 | `SW/tools/check_onepass_sw_sync.py` | 0 | 1.13s |
| 2 | `SW/tools/check_sw_ref_reachability.py` | 0 | 0.29s |
| 3 | `SW/tools/check_landing_trace_obligation.py` | 0 | 0.11s |
| 4 | `SW/tools/check_demo_panel_spec.py` | 0 | 0.15s |
| 5 | `SW/tools/check_demo_panel_spec_r6_selftest.py` | 0 | 0.38s |
| 6 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | 0 | 0.43s |
| 7 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | 0 | 0.81s |
| 8 | `SW/tools/check_shutdown_semantics.py` | 0 | 0.09s |
| 9 | `SW/tools/check_timing_review_adc_sync.py` | 0 | 0.13s |
| 10 | `SW/tools/timing_check.py` | 0 | 0.62s |

★**绿 10 / 红 0** ★ [实测] · 读数缓存 = `tmp/iss368_sbx/gates_report.json` (★键 = 副本里两份被改页面的 md5★ ⇒ 副本内容一变缓存自动失效 ⇒ 重跑★) [实测]

### §3.3 新闸 F1~F7 (★`python3 SW/tools/check_sw09_patch_dryrun.py`★)

| 判据 | 标题 | 读数 |
|---|---|---|
| F1 | 三处同批到位 (★落点① 页内三处 + JSON 计数 == 9 + 落点③ 新闸字节未变★) | 绿 [实测] |
| F2 | §H4-REG 三个登记数字 == (9/1/5) | 绿 [实测] |
| F3 | 干跑两次的 diff == 0 (幂等 · 且补丁本身必须跑得通) | 绿 [实测] |
| F4 | 10 道 SW 闸全绿 (副本上逐道实跑) | 绿 [实测] |
| F5 | 证据等级五级白名单 | 绿 [实测] |
| F6 | 正文零挂起措辞 | 绿 [实测] |
| F7 | 沙盒在项目盘 `tmp/` (且零软链) | 绿 [实测] |

★**合计: 绿 7 / 红 0** ★ · ★**反向用例 8/8 PASS** ★ (★每条自证「红的是目标那一条 · 其余仍绿」★) [实测]

★**反向用例逐条** ★: ST-1 §2.1 分布表里拿掉 SW09 ⇒ F1 红 · ST-2 §6 JSON 块里拿掉 SW09 ⇒ F1 红 ·
ST-3 §H4-REG 三数字写回 8/0/4 ⇒ F2 红 · ST-4 把已落地的一处改坏 (★补丁锚点对不上·apply fail-closed★) ⇒ F3 红 ·
ST-5 10 道闸里第 1 道 rc 改成 1 ⇒ F4 红 · ST-6 新页里写一个白名单外的证据等级 ⇒ F5 红 ·
ST-7 新页里写一句挂起措辞 ⇒ F6 红 · ST-8 沙盒放到项目盘 `tmp/` 之外 ⇒ F7 红 [实测]

### §3.5 本单对新闸与补丁脚本做的三处修正 (★全是实测出来的缺陷·不是重写★)

| # | 缺陷 (★实测症状★) | 修正 | 影响 |
|---|---|---|---|
| D1 | `apply_sw09_three_place_patch.py` ★**不认 `--dry-run`** ★ (★argparse 直接 rc=2★) ⇒ 任务书必跑命令逐字跑不起来 | 补一个显式 `--dry-run` 旗标 (★与「默认就是干跑」同义·零副作用★) · ★**判据方向一个字没改** ★ | ★必跑命令现在 rc=0★ [实测] |
| D2 | `check_sw09_patch_dryrun.py --selftest` 的 ST-6 / ST-7 ★**把真交付页永久改坏且不还原** ★ ⇒ 跑一次 selftest 就把本页写成 F5 红 + F6 红 · ST-8 又因缺父目录直接崩 (★rc=1★) | 跑用例前对真页做快照 · ★每条用例跑完立刻逐字节还原★ · ST-8 先建父目录 · 跑完清掉残留目录 | ★selftest 现在 rc=0 · 且真页 md5 前后逐字节相同 (★已自证★)★ [实测] |
| D3 | F3 的基准 ★**读的是项目根** ★ ⇒ 沙盒怎么改都碰不到它 ⇒ ST-4 那条用例 ★**永远抓不到 F3** ★ | F3 基准改为【当前沙盒副本】(★沙盒不可用才回落项目根★) | ★反向用例从 7/8 变成 8/8★ [实测] |

★**三处修正都没动判据方向** ★: 改的都是【怎么跑】不是【判什么红】 ★ [实测]

### §3.4 反证 (★「只改一处 ⇒ H4 红 + F4 红」★)

★**跑法** ★: `python3 logs/iss368/prove_partial_landing.py` (★真件原文做「回退那一处」· 变体全在 `tmp/iss368_sbx/` 下★) [实测]

| 变体 | 做法 | ISS-362 闸 rc | ISS-363 闸 rc | H4 | F4 |
|---|---|---|---|---|---|
| V0 | 三处同批落地 (★基线★) | 0 | 0 | 绿 | 绿 |
| V1 | ★**只改落点①** ★ (清单页) · 落点② 没改 | 1 | 1 | ★**红** ★ | ★**红** ★ |
| V2 | ★**只改落点②** ★ (影响页) · 落点① 没改 | 1 | 1 | ★**红** ★ | ★**红** ★ |

★**结论: 反证成立 = 是** ★ [实测] ⇒ ★**「三处不同批」必然当场红 · 红了没法解释 · 最坏是有人为让闸绿去改锚点或改判据** ★ (★正是 ISS-273/275/284 堵掉的漏洞★) [实测]

---

## §4 回滚

### §4.1 回滚命令 (★反向补丁 · 走同一套锚点★)

```
python3 SW/tools/apply_sw09_three_place_patch.py --apply --rollback --target-root <项目盘 tmp/ 下的副本目录>
```

★**约束** ★: `--apply` 必须带 `--target-root` ⇒ 目标必须在项目盘 `tmp/` 下 ⇒ ★**回滚也写不进去真件** ★ (★rc=2 拒写★) [实测]

### §4.2 逐字节回滚读数 (★`python3 logs/iss368/prove_rollback.py`★)

| 文件 | 回滚前 (副本 = 已落地态) | 回滚后 (副本) | 真件 (落地前原文) | 逐字节相同 |
|---|---|---|---|---|
| `SW/BOARD_ONEPASS_SW_SYNC.md` | `2186777965c64e6764109214e87048de` | `b8f935db333c16fa1051f0b06ae3e6ec` | `b8f935db333c16fa1051f0b06ae3e6ec` | ★**是** ★ |
| `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` | `741a613799c375fb0764956a9c5eaf48` | `17b3c38c397e9aab06c8d2cbdd7d7461` | `17b3c38c397e9aab06c8d2cbdd7d7461` | ★**是** ★ |
| `SW/tools/check_fp_truth_read.py` | `cab7a6f17c1da35f4e54185ad8b62089` | `cab7a6f17c1da35f4e54185ad8b62089` | `cab7a6f17c1da35f4e54185ad8b62089` | ★**是** ★ |

★**逐字节回滚 = 是** ★ [实测] ⇒ ★**反向补丁是逐字节可逆的 · 不是「再改一次」** ★ [实测]

### §4.3 回滚后 10 道 SW 闸复跑 (★在回滚后的副本上逐道实跑★)

| # | 闸 | rc | 耗时 |
|---|---|---|---|
| 1 | `SW/tools/check_onepass_sw_sync.py` | 0 | 2.02s |
| 2 | `SW/tools/check_sw_ref_reachability.py` | 0 | 0.51s |
| 3 | `SW/tools/check_landing_trace_obligation.py` | 0 | 0.19s |
| 4 | `SW/tools/check_demo_panel_spec.py` | 0 | 0.27s |
| 5 | `SW/tools/check_demo_panel_spec_r6_selftest.py` | 0 | 0.65s |
| 6 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | 0 | 0.62s |
| 7 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | 0 | 0.82s |
| 8 | `SW/tools/check_shutdown_semantics.py` | 0 | 0.11s |
| 9 | `SW/tools/check_timing_review_adc_sync.py` | 0 | 0.15s |
| 10 | `SW/tools/timing_check.py` | 0 | 0.69s |

★**绿 10 / 红 0** ★ [实测] ⇒ ★**回滚后回到落地前状态 · 那道「板只改一次」那一趟之前的基线依然是绿的** ★ [实测]

### §4.4 回滚的落点写法 (★反向补丁逐条对应★)

| 落点 | 正向 | 反向 |
|---|---|---|
| A1 | 小节头 8 条 ⇒ 9 条 | 9 条 ⇒ 8 条 |
| A2 | 插入第 9 行 | 删掉那一行 (★按整行逐字匹配★) |
| A3 | S10 3 ⇒ 4 | S10 4 ⇒ 3 |
| A4 | `items[]` 追加第 9 个对象 | `items[]` 去掉同 `id` 的对象 |
| B1~B11 | 逐条替换 | 逐条反向替换 (★按新文定位★) |

★**反向补丁与正向补丁共用同一套锚点表** ★ ⇒ ★**不会出现「正向改了 15 处 · 反向只回得掉 14 处」这种半回滚** ★ [实测] (★回滚后两份页面 md5 与真件逐字节相同★)

---

## §5 未决项 (★只登记 · 不代拍★)

| # | 未决项 | 归谁 | 本单口径 |
|---|---|---|---|
| U1 | 新闸 `SW/tools/check_sw09_patch_dryrun.py` ★**挂不挂** ★ `state/gate_check.py` 的 `EXTRA_GATES` | ★**main 的机制地界** ★ | ★**本单零挂链** ★ (★`state/gate_check.py` 一个字节没改 · md5 `5f370bb8cf828473e70ccc5d6412da98` 前后同值★) [实测] |
| U2 | 真件三处的【真件落地】何时执行 | main (★落表批次地界 · 「板只改一次」那一趟的一键动作★) | ★**本单只交补丁 · 真件零改** ★ [实测] |
| U3 | ISS-368 的 `state/issue_log.yaml` 签字 | ★**main 的活** ★ | ★**本单零改该文件** ★ [实测] |
| U4 | 板面 186 个封装的库封装名补齐 (★现状 0/186 非空★) | 板侧作业包那一趟 (★归 hw-lead★) | ★**本单只把 SW 侧第 9 条的判据钉死 · 换真值那一跳不在本单** ★ [实测] (★读数转引自 ISS-363 交卷页 §B4 的 `current_state` 字段★) |
| U5 | 锚点副本跟到 ISS-302 链头 (★必须走合法换源通道: 落 decision + 留痕★) | main | ★**本单不许手改任何 md5** ★ (★三份真源的 md5 一个字节没动★) [实测] |

★**本单不代拍上面任何一条** ★ · ★**也没有把任何一条写成「已定」** ★ [实测]

---

## §6 边界自证 (★逐条·本机实跑读数★)

| 边界 | 自证读数 | 结论 |
|---|---|---|
| 零写板 | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` | ★**未变** ★ [实测] |
| 零落表 (网表/脚表/BOM) | `HW/netlist_v1.csv` `6aee500e60ba0732f83a9cf557ba90ab` · `HW/netlist_v1_pins.csv` `9174309df1ec9411ac8e8d9e80ee386a` · `HW/BOM_v1.csv` `5b9993992405904a60ac96a020b375d8` | ★**未变** ★ [实测] |
| 零落表 (锚点台账) | `SW/SW_MD5_BASELINE_LEDGER.md` `83fafcf7d22d8fa999a1db74c781956d` | ★**未变** ★ [实测] |
| 真件三处零改 | `SW/BOARD_ONEPASS_SW_SYNC.md` `b8f935db333c16fa1051f0b06ae3e6ec` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` `17b3c38c397e9aab06c8d2cbdd7d7461` · `SW/tools/check_fp_truth_read.py` `cab7a6f17c1da35f4e54185ad8b62089` | ★**未变** ★ [实测] |
| 零改既有闸 | `check_onepass_sw_sync.py` `3984cab48cea0201a5187abaaa4c9499` · `check_sw_fp_truth_impact.py` `94fa1fbb0124921df1ad391f894beacb` · `check_onepass_sw_release.py` `4d7ce982965e92c78a1ebcd3e968874e` · `state/gate_check.py` `5f370bb8cf828473e70ccc5d6412da98` · `state/merge.py` `c9191025020fefd9b475e2573a335815` · `state/frag_write.py` `3b383a52b4fa540f1d16a2c6f3811de8` | ★**未变** ★ [实测] |
| 零挂链 | 本单新闸没进任何 `EXTRA_GATES` | ★**成立** ★ [实测] |
| 零外发 / 零采购 / 零联系供应商 | 本单全程无任何外部通信动作 | ★**成立** ★ [实测] |

★**本单新写的文件只有这四件** ★ (★两个脚本 + 一页 + 交卷页, 外加分片与留证★) [实测]:
`SW/tools/apply_sw09_three_place_patch.py` · `SW/tools/check_sw09_patch_dryrun.py` · `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` (★本页★) · `HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md`

---

## §7 复现全表 (★一条一条抄着跑★)

```
python3 SW/tools/check_fp_truth_read.py
python3 SW/tools/check_fp_truth_read.py --selftest
python3 SW/tools/check_sw_fp_truth_impact.py
python3 SW/tools/check_onepass_sw_sync.py
python3 SW/tools/check_onepass_sw_release.py
python3 SW/tools/apply_sw09_three_place_patch.py --dry-run
python3 SW/tools/check_sw09_patch_dryrun.py
python3 SW/tools/check_sw09_patch_dryrun.py --selftest
python3 logs/iss368/prove_partial_landing.py
python3 logs/iss368/prove_rollback.py
python3 state/merge.py
python3 state/gate_check.py
python3 state/frag_write.py --agent sw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/BOARD_ONEPASS_SW_SYNC.md SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md SW/SW_MD5_BASELINE_LEDGER.md
```

★**留证目录** ★: `logs/iss368/` (★基线 md5 · 干跑读数 · 落点逐字导出 · 反证输出 · 回滚输出 · 闸复跑输出 · 续跑标记★) [实测]

---

★**本页结论一句话** ★: ★**三处同批落地已经被打成【一次可执行 · 幂等 · 可回滚 · 有沙盒证明】的动作** ★ ⇒ ★**「板只改一次」那一趟当天不会再出现「清单说 9 条 · 闸按 8 条判」的互相打脸** ★ [实测]
