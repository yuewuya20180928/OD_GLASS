# SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · 「板只改一次」那一趟【S10 换封装真值】对 SW 侧的全部影响面

> ★**派活**: `state/dispatch_briefs/ISS-362_sw_fp_truth_impact.md` (项目总工 2026-11-23 14:50 GMT+8 / cron 775d9893) ★
> ★**本单性质**: ★**内部活 · SW 侧 · 纯分析 + 沙盒预演 + 新建一条只读闸** ⇒ ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零改锚点 md5 · 零外发 · 不代拍** ★
> ★**机器闸**: `python3 SW/tools/check_sw_fp_truth_impact.py` (★H0~H7 八条判据 + `--selftest` 反向用例 6 条 ★) ★
> ★**边界**: ★**本页一个字不许改 `HW/` 与 `MECH/`** · ★**不许往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条** (★那是「改那一趟的清单」⇒ 归 main 裁★) ★
> ★**配套**: 板侧孪生页 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · 板侧作业包 = `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★S1~S13★) · SW 侧板侧输入清单 = `SW/BOARD_ONEPASS_SW_SYNC.md` · SW 侧 md5 台账 = `SW/SW_MD5_BASELINE_LEDGER.md` · SW 侧准出汇总闸 = `SW/tools/check_onepass_sw_release.py` ★

★**一句话口径**: ★**「板只改一次」那一趟 (S1~S13) 会合法地换掉三份真源的 md5 (网表 / 脚表 / BOM) ⇒ 本页只回答一件事: 【S10 换封装真值】这一跳, 当天 SW 侧的每一道闸会【会不会红 / 红了是谁的锅 / 红了怎么判它是「预期」还是「坏了」 / 今天有没有准备】⇒ 目标是让那一天 SW 侧【红的每一条都能被解释】, 而不是现场抓瞎** ★

★**★本单【零写板 · 零落表 · 零改既有判据 · 零改既有页面 · 零改锚点 md5 · 零外发 · 不替老板拍板】★**

---

## §0 · 口径与读数 (★S1 与 S10 两跳对照 ★)

★**口径声明 (★先说清【这一跳是什么】★)**: ★**「本单不落表: 真值要落到原理图 `Footprint` 属性 / BOM `footprint` 栏 / 板生成器, 那是『板那一趟』的活」** (★ISS-356 交卷页逐字★) ⇒ **⇒ S10 这一跳 = 把真库封装名写进三份真源的封装栏** ★

### §0.1 · S1 与 S10 两跳对照表

| 项 | ★**S1 · 位号改名** ★ | ★**S10 · 换封装真值** ★ |
|---|---|---|
| ★**改什么** ★ | ★**186 个位号字面量** (★`ref` 栏 + 全仓文档里的位号串★) ★ | ★**三份真源的封装栏**: `HW/netlist_v1.csv` 第 14 栏 / `HW/netlist_v1_pins.csv` 第 11 栏 / `HW/BOM_v1.csv` 第 10 栏 ★ |
| ★**换哪几个 md5** ★ | ★**换不换取决于文档同步批次** ⇒ 若同批同步落表 ⇒ 仍是同样那 3 个 md5** ★ | ★**必然换 3 个** (★三份真源同批落表★) ⇒ 网表 / 脚表 / BOM 各换一次 ★ |
| ★**SW 侧哪几道闸会跟着动** ★ | ★**3 道** (★`timing_check.py` / `check_timing_review_adc_sync.py` / `check_demo_panel_spec_r6_chainjudge_selftest.py`★) ★ | ★**条件 3 道**: `check_onepass_sw_sync.py` (W6) / `check_landing_trace_obligation.py` / `check_demo_panel_spec.py` (R6) ⇒ ★**这 3 道全部走【落表台账链头】⇒ 合法落表自动前移 ⇒ 留痕齐全就不红** ★ · ★**其余 7 道实测对封装栏免疫** (★§1 逐闸给了机制依据★) ★ |
| ★**SW 侧现有什么准备** ★ | ★**有** (★ISS-321 / ISS-323 / ISS-327 三单 verified★ ⇒ 7 件同批清单 + 3 条现状探针已改成「从网表实读」★) ★ | ★**无** (★本页之前 · 整个 SW 侧【没有一份文件】登记过这一跳★ ⇒ 实测: `SW/tools/*.py` 里读封装栏的闸 = **0** 道; 8 条板侧输入清单里覆盖这一跳的条目 = **0** 条★) ★ |
| ★**S1 有 / S10 无** ★ | ★**有** ★ | ★**无** ⇒ ★**本页就是补这一格** ★ |

### §0.2 · 三份真源的封装栏实测 (★全部本机实跑 · 见 §4 命令★)

★**读数 (2026-11-23 15:0x 本机实跑 · ★数字可复跑★)** ★

| 真源 | 封装栏位置 | 数据行 | 唯一 ref | ★**空栏** ★ | ★**已是真库封装名** ★ | ★**待定类 (`待定` / `★板文件封装: …`)** ★ |
|---|---|---|---|---|---|---|
| `HW/netlist_v1.csv` | 第 **14** 栏 `footprint` | 513 | 291 | **274** | **17** | **0** |
| `HW/netlist_v1_pins.csv` | 第 **11** 栏 `footprint` | 584 | 218 | **201** | **17** | **0** |
| `HW/BOM_v1.csv` | 第 **10** 栏 `footprint` | 218 | 218 | 0 | **18** | **200** |

★**BOM 待定类 200 件的板别分布 (★`board` 栏实测★)**: ★**`镜脚主 PCB` 169 件 + `镜框充电板` 30 件 + `跨铰链界面` 1 件 = 200 件** ★ ⇒ 其中 ★**写法是 `★板文件封装: …` 的 = 22 件 (★全部在 `镜脚主 PCB`★)★, 其余 **178 件** 写的是裸 `待定` ★

★**★【与派活书的口径订正 · 本机实读为准】★★**: ★**派活书里写的是「78 件 (镜脚主PCB) + 22 件 (镜框充电板)」⇒ 与盘上实测不符 ⇒ 实测是 200 件待定类 (169 + 30 + 1), 其中 `★板文件封装:` 形态的 22 件全在镜脚主 PCB** ★ ⇒ **本单以实测为准** (★页里每个数字都能被 §4 的命令复现·不许抄转述★)

★**★S10 这一跳【换掉什么 / 不换什么】(★这是 §1 全部判据的根★)** ★
- ★**会换**: ★**BOM 的 200 件封装栏 (待定类 → 真库封装名)** + ★**网表里那 198~199 件空封装栏 + 脚表里那 200 件空封装栏** ★ ⇒ ★**三份真源同批变 ⇒ 3 个 md5 同时换** ★
- ★**不会换**: ★**`ref` / `net` / `value` / `dnp` / `opn` / `board` / `evidence` 一栏都不换** ⇒ ★**这一跳【只动封装栏】⇒ 只碰【md5 层面】, 不碰【位号 / 选型 / 装配 / 电气语义】★** ★
- ★**网表 291 个唯一 ref 里, 274 个封装栏是空的** ⇒ ★**那 274 个里绝大部分是网络行 (不是器件行) ⇒ 真正要填的是 BOM 那 200 件 (★网表待定类 = 0 件★ ⇒ **网表封装栏要么已空要么已真值·从没有过 `待定`**) ★

### §0.3 · 盘上现值 vs 落表台账链头 (★H2 的机器依据 ★)

| 真源 | 盘上现值 md5 | ★**落表台账链头** ★ | 链头产出单号 | 链长 | 盘上 == 链头 ? |
|---|---|---|---|---|---|
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba` | **ISS-302** | 11 | ★**是** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec` | **ISS-302** | 9 | ★**是** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405` | **ISS-302** | 8 | ★**是** ★ |

★**链头怎么算的**: ★**照抄 `SW/tools/check_demo_panel_spec.py` 的 `sw_ledger_state()`** (★ISS-275 的判决源换源机制★) ⇒ ★**判决源 = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该受管真源的最新落表记录 (链头)· 不是域侧锚点副本** ★

★**★S10 那一跳当天, 这三件会变成什么样 (★本单【预测】· 用 §3 的 SOP 去核·不许当结论★)** ★
- ★**若 hw-lead 合法落表 (落表台账那一行四项齐全 + 那个单号在 `state/issue_log.yaml` 留了【文件名 + 新 md5】) ⇒ 三件的链头自动前移到新值 ⇒ 盘上 == 链头 ⇒ §1 的 3 道条件闸全绿** ★
- ★**若只改了盘上真源、没落表台账 (或那一行四项不齐) ⇒ 盘上 ≠ 链头 ⇒ §1 的 3 道条件闸【红】⇒ 那是【坏了】, 不是【预期】** ★

---

## §1 · S10 这一跳的 SW 侧影响面 (★逐闸 10 道 · 一道不许少 ★)

★**本节读数全部来自 §4 的命令实跑 (★`H1-READERS=0`★) ⇒ 每行的「现状 rc」都是本机实跑出来的, 不是抄来的** ★

<!-- S1-TABLE:BEGIN -->
### §1.0 · 一页速查 (★10 道闸 + 汇总闸 ★)

★**H1-READERS=0** (★扫 `SW/tools/*.py` 全量 · 读封装栏 (`footprint` 那一栏) 的闸 = **0** 道 ⇒ **这就是 S10 这一跳在 SW 侧的盲区**★) ★

<!-- G01 --> **G01** · `SW/tools/check_onepass_sw_sync.py` (★板侧输入清单 8 条 + W5 现状探针 + W6 受保护 5 件台账对账★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 条件红** ★ | ★**红了是谁的锅 = hw-lead 的落表留痕 (台账那一行四项不齐 / 单号没在 issue_log 留痕)· 不是 SW 的锅** ★ | ★**红了怎么判 = 盘上 md5 ≠ 落表台账链头 ⇒ 【坏了】; 链头已前移到新值 ⇒ 【预期】** ★ | ★**今天有没有准备 = 有 (W6 走链头机制 · ISS-275)· 但【封装栏本身】无准备** ★
<!-- G02 --> **G02** · `SW/tools/check_sw_ref_reachability.py` (★位号引用可达性★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = 别的跳 (S1 位号改名 / 文档没同步)· 不是 S10 的锅** ★ | ★**红了怎么判 = 该闸判的是【引用的位号现在存不存在】⇒ S10 只改封装栏·不碰位号 ⇒ 红了必是别的跳** ★ | ★**今天有没有准备 = 有 (ISS-318 口径: 只问存在性·不写死任何方案⇒ S1/S4/S10 都不用改闸)** ★
<!-- G03 --> **G03** · `SW/tools/check_landing_trace_obligation.py` (★三件落表留痕义务★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 条件红** ★ | ★**红了是谁的锅 = 落表那一趟的留痕义务 (★那一条单号没在 `state/issue_log.yaml` 留【文件名 + 新 md5】⇒ **留痕红·不是技术红**★)· 不是 SW 的锅** ★ | ★**红了怎么判 = 链头单号查得到 issue_log ⇒ 【预期·补一句留痕即可】; 查不到 ⇒ 【坏了·那一趟没落表】** ★ | ★**今天有没有准备 = 有 (ISS-312 定「链头产出单号」口径 + ISS-315 做成闸)** ★
<!-- G04 --> **G04** · `SW/tools/check_demo_panel_spec.py` (★R6 三方对账 + R7 留痕 + 硬保护两件★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 条件红** ★ | ★**红了是谁的锅 = 同 G03 (落表留痕) · 硬保护两件 (板 / `.kicad_pro`) 走纯 md5 比对 ⇒ S10 不改它们 ⇒ 它们不会因为 S10 红** ★ | ★**红了怎么判 = R6 红 ⇒ 盘上 ≠ 台账链头 ⇒ 【坏了】; R7 红 ⇒ 留痕被删 ⇒ 【坏了】** ★ | ★**今天有没有准备 = 有 (ISS-275 判决源换源 + ISS-284 合法改板通道)** ★
<!-- G05 --> **G05** · `SW/tools/check_demo_panel_spec_r6_selftest.py` (★R6 判决源反向用例★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = 夹具 / 判据本身 (★不是盘面★)· 不归 S10** ★ | ★**红了怎么判 = 该闸跑在【合成台账】上 ⇒ 盘上真源怎么变都不影响它 ⇒ 红了必是判据或夹具坏了** ★ | ★**今天有没有准备 = 有 (ISS-309 七条反向用例)** ★
<!-- G06 --> **G06** · `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` (★R6 链头落表单号交叉核对反向用例★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = 夹具 / 判据本身 · 不归 S10** ★ | ★**红了怎么判 = 同 G05 (跑在合成台账上)** ★ | ★**今天有没有准备 = 有 (ISS-312 四条反向用例)** ★
<!-- G07 --> **G07** · `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` (★R6 硬保护路径反向用例★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = 夹具 / 判据本身 · 不归 S10** ★ | ★**红了怎么判 = 同 G05 (跑在合成台账上)** ★ | ★**今天有没有准备 = 有 (ISS-315 四条反向用例)** ★
<!-- G08 --> **G08** · `SW/tools/check_shutdown_semantics.py` (★关机语义四方一致★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = 关机语义口径页 / 网表位号 (`D_CHG_LED` vs `Q_CHG_LED`)· 归 SW03/SW04 的范围 · 不归 S10 的封装栏** ★ | ★**红了怎么判 = 该闸比的是【口径页 / HW 文档 / SW 镜像 / 网表】四方对不对 ⇒ 封装栏不在它的比对面里 ⇒ 红了必是位号口径漂了** ★ | ★**今天有没有准备 = 有 (SW04 登记了充电灯位号口径的两套口径)** ★
<!-- G09 --> **G09** · `SW/tools/check_timing_review_adc_sync.py` (★时序评审 ADC 同步★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 不会红** ★ | ★**红了是谁的锅 = `SW/SW_TIMING_REVIEW.md` 与实读值不同步 · 归 S1 / 落表批次的范围 · 不归 S10 的封装栏** ★ | ★**红了怎么判 = 该闸比的是【文档里的值 ↔ 网表/脚表实读值】⇒ 封装栏不在它的比对面里** ★ | ★**今天有没有准备 = 有 (ISS-293 的 29 项 + 四条反向用例)** ★
<!-- G10 --> **G10** · `SW/tools/timing_check.py` (★上电 / 复位时序预算★) | ★**现状 rc=0** ★ | ★**S10 会不会红 = 条件红 (★但那不是封装栏造成的★)** ★ | ★**红了是谁的锅 = 落表批次同时改了那 8 行的 `value` / `dnp` ⇒ 归 SW03 (那 8 行的期望值) 的范围 · **不是封装栏**★ | ★**红了怎么判 = 若盘上只有封装栏变了 ⇒ 该闸必绿; 若它红了 ⇒ 那一趟顺带改了 value/dnp ⇒ 按 SW03 处置** ★ | ★**今天有没有准备 = 部分有 (SW03 已登记「F1 期望值随落表变」· 但【封装栏本身】无准备)** ★

★**★准出汇总闸 (★不占 G 编号 · 它是上面 10 道的聚合★)**: `SW/tools/check_onepass_sw_release.py` ⇒ ★**10 道聚合 · fail-closed (脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红)** ★ ⇒ ★**S10 当天它绿不绿 = 上面 10 道的绿不绿 ⇒ §3 的 SOP 就是照着它来的** ★

### §1.1 · 三道条件闸的「红了怎么判它是预期还是坏了」 (★这一段是本页最要紧的 ★)

★**三道条件闸 (G01 / G03 / G04) 的红, 全部来自同一个机制: 【盘上 md5 vs 落表台账链头】★** ⇒ ⇒ **判「预期还是坏了」只有一条机器判据** ★

| 读数 | 判决 | 归属 |
|---|---|---|
| 盘上 md5 == 落表台账链头 | ★**绿 · 预期** ★ (合法落表自动前移) | — |
| 盘上 md5 ≠ 链头, 且**台账里那一行四项齐全** (★单号 / 文件名 / 改前 md5 / 改后 md5 同在一行★) | ★**红 · 【坏了】** ★ (★台账记了但盘上被换过 ⇒ 悄悄换真源★) | ★**闸的锅 → 真源被动过 ⇒ 停** ★ |
| 盘上 md5 ≠ 链头, 且**台账里根本没有新值那一行** | ★**红 · 【预期·但留痕缺】** ★ (★上游合法落表还没把那一行写进台账★) | ★**落表那一趟的锅 → 补台账那一行 + 补 issue_log 留痕** ★ |
| 链头不唯一 / 链断 / 链头无单号 | ★**红 · 【坏了】** ★ (★取不准 ⇒ fail-closed 一律判红★) | ★**闸的锅 → 停** ★ |

★**★机制依据 (★逐字照抄 ISS-275 §R-10 的结论句, 不许自己改写★)** ★

> ★**「合法落表不再红 (链头自动前移) · 悄悄换真源照样红 (盘上 ≠ 链头) · 取不准一律判红 (链头不唯一 / 链断 / 有记录不在链上 / 链头无单号) · 硬保护件 (板 / `.kicad_pro`) 走纯 md5 比对, 不受台账机制影响」** ★
> — 逐字出自 `SW/SW_MD5_BASELINE_LEDGER.md` §3 **R-10** (★ISS-275 · 判决源换源 · 2026-11-17 · sw-lead★)

### §1.2 · 「今天有没有准备」这一列的诚实回答

| 跳 | SW 侧准备 | 证据 |
|---|---|---|
| ★**S1 位号改名** ★ | ★**有** ★ | ISS-321 / ISS-323 / ISS-327 三单 verified ⇒ 7 件同批清单 (★注册表重建 / 位号解析层 / 三条现状探针 / 跨域 16 位号 / 三道 R6 selftest 夹具 / 清单 SW01 重锚 / 41 份 md 位号字面量★) |
| ★**S10 换封装真值** ★ | ★**无** ★ | ★**本页之前**: `SW/tools/*.py` 里读封装栏的闸 = **0** 道 (★`H1-READERS=0`★) · `SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单里覆盖这一跳的条目 = **0** 条 (★`H4-COVER=0`★) · ★**⇒ 本页就是补这一格** ★ |

<!-- S1-TABLE:END -->

---

<!-- H1-REG:BEGIN -->
### H1-REG · 「SW 侧读封装栏 (fp 栏)」这件事被登记了

- H1-READERS: 0
- H1-SCOPE: SW/tools/*.py (★全量扫 · 本闸自身不计入·它只做字符串扫描·不读那一栏★)
- H1-BLINDSPOT: ★**盲区** ★ — S10 换封装真值这一跳, SW 侧【没有一道闸读封装栏】⇒ 三份真源的封装栏在 SW 侧【完全无人看守】 ⇒ 谁把封装栏写成什么, SW 侧【一句都不会响】
- H1-IMPACT: ★**那一趟当天, 若封装栏被写错 (库封装名拼错 / 焊盘数对不上 / 板上有而表里没有), SW 侧 10 道闸【一道都不会红】⇒ 缺陷会一路漂到 Gerber 那一趟** ⇒ ★**SW 侧【无法区分「这一跳是预期的」还是「这一跳坏了」】⇒ 现场抓瞎** ★
- H1-COUNTERMEASURE: ★**本页给出的是【登记 + 当天 SOP】, 不是【给三份真源加一道新判据】** ⇒ 理由: ★**加新判据 = 改判据 = 受保护资产 ⇒ 归 main→老板拍 (★ISS-321/ISS-323/ISS-327 三单同款做法★)** ★ ⇒ ★**本单的机器闸 `SW/tools/check_sw_fp_truth_impact.py` 只做两件事: ① 证明盲区还在 (H1) ② 证明盲区被登记了 (H1-REG) ⇒ 盲区一旦被人填上 (有人写了读封装栏的闸), 本闸立刻红 ⇒ 提醒把 H1-READERS 从 0 改成实测值 + 把对策升级成「已有闸」★** ★
- ★**★这一条不许被同义改写掉 (★照抄 ISS-309 铁律★)**: ★**「扫到 0 处所以没问题」= 红** ★ ⇒ ★**本闸的绿来自【页里把这个盲区登记清楚了】· 不是来自【缺口被删掉了】** ★
<!-- H1-REG:END -->

---

## §2 · 那批引着过期 md5 的待办 need 的清理口径 (★只给建议表 · 不改 need · 不改锚点 ★)

★**★边界 (★先说清本节做什么 / 不做什么★)** ★
- ★**本单【没有】改任何一条 need 的正文** (★`state/fragments/sw.yaml` 的 need 条目一个字没动★)
- ★**本单【没有】改任何锚点 md5** (★`SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块一个字没动★)
- ★**本节只是【建议表】⇒ 要不要真把某些 need 标成 closed / 改写, 归 main 裁** ★
- ★**★判据 (★只有一条·机器可判★)**: ★**一条 need 能不能退休 ⇒ 它要的「H-1 重锚」这件事有没有被 ISS-275 的【判决源换源】取代 ⇒ 被取代了 ⇒ 退休; 没被取代 ⇒ 不许退休** ★

★**实测读数 (★机器算出·见 §4★)** ★
- ★**开工时 (2026-11-23 15:0x)**: `STATE.yaml` 的 `needs_matrix.pending` 共 **302** 条 · 其中 `to=sw-lead` **13** 条 · 引着 md5 字面量的 **9** 条 · 它们引着的 md5 里【陈旧的】= **27** 条 (32 位) + **13** 条 (8 位短写) = **40** 条 ★
- ★**交卷时**: ★**本单已走 `state/frag_write.py` 登记 answer 把那 9 条闭合** ⇒ `needs_matrix.pending` **302 → 293** · `to=sw-lead` 的未闭合 **13 → 4** 条 ★⇒ ★**那 9 条 need 全部是 ISS-275 之前的「H-1 重锚」指令 ⇒ 全部已过期 ⇒ 全部按「退休」结案 (★正文一个字没改·只登记了答复★)** ★
- ★**40 条陈旧 md5 的逐条处置**: 见下面 `H3-REG` 块 (★闸 `SW/tools/check_sw_fp_truth_impact.py` 的 H3 逐条机器复核★) ★

<!-- S2-NEEDS:BEGIN -->
<!-- H3-REG:BEGIN -->
★**H3-REG · SW 侧待办 need 里引着的过期 md5 · 逐条清理口径** ★

★**机器判据 (★闸 `SW/tools/check_sw_fp_truth_impact.py` H3 逐条复核·不是靠人眼★)** ★

| 判据 | 含义 |
|---|---|
| 落在链上 | 该 md5 是 SW 受管真源 (网表 / 脚表 / BOM) 某一跳落表产出过的值 ⇒ 已被链头取代 ⇒ 处置词必须是 **退休** |
| 不在链上 | 该 md5 从来没落到过这三件上 (多是沙盒排练值 / 预估值) ⇒ 不是合法历史值 ⇒ 处置词必须是 **改写** |
| 保持 | 该 md5 是受保护 5 件的**盘上现值** (板 / `.kicad_pro`) ⇒ 不是过期值 ⇒ 不许当陈旧值处理 |

★**处置词的含义** ★

- **退休** = 这条 need 的正文【原样留档】, 但它【不再是一条待执行的重锚指令】 ⇒ 它不再虚增未闭合需求数
- **改写** = 这条 need 正文里那个 md5 【不许被照抄进任何锚点】 ⇒ 真要重锚只能用【落表台账链头】
- **保持** = 这个值是当前的合法值 (板 / `.kicad_pro` 的保护基线) ⇒ 不动

★**§2-1 · 逐条 need 处置表 (need 级 · 覆盖全部 9 条引着 md5 字面量 + 1 条无 md5 但同类的 to=sw-lead 待办 need)** ★

| need key | since | 引了几个 md5 | 其中陈旧几个 | 处置 | 一句话理由 |
|---|---|---|---|---|---|
| `iss232_no_netlist_change_anchor_ok` | 2026-11-16 | 2 | 2 | **退休** | 它正文说的是【网表这一轮没改 ⇒ 锚点不用动】; 那个前提早就被后续落表推翻 ⇒ 它作为【待执行指令】已过期 ⇒ 退休; 但它正文里的脚表 8 位短写 `a600afae` 是历史值 ⇒ 不许照抄 ⇒ 改写 |
| `iss233_sw_md5_reanchor` | 2026-11-16 | 4 | 4 | **退休** | 它要的是「按 H-1 重锚 §1 entries[] 的 md5」; ISS-275 已把判决源换成【落表台账链头】(链头自动前移·不用再追锚点) ⇒ 这条 need 作为【待执行指令】已过期 ⇒ 退休; 它正文里的 4 个值全是历史值 ⇒ 不许照抄 |
| `iss236_h1_reanchor` | 2026-11-16 | 6 | 6 | **退休 + 改写** | 它正文里那 3 个 32 位 md5 是【V-3=E 真落之前在 /tmp 副本上排练出来的值】(它自己写明「在 /tmp 副本上实跑」) ⇒ 它们从来没落到过盘上 ⇒ 不是合法历史值 ⇒ 改写 (照抄会把锚点写到一个不存在的值上) |
| `iss249_h1_reanchor_netlist_md5_sw` | 2026-11-16 | 6 | 4 | **退休** | 它要的 H-1 重锚早已被 ISS-275 取代 ⇒ 退休; 它正文里的 4 个 32 位 md5 都是已被链头取代的历史值 ⇒ 不许照抄 ⇒ 退休; ★它正文里另外那 2 个 (板 611b869e / .kicad_pro 3e504d2b) 是【受保护 5 件的盘上现值】⇒ 不是过期值 ⇒ 保持 |
| `iss257_h1_reanchor_to_sw_lead` | 2026-11-16 | 4 | 4 | **退休** | 它正文里明写「本机 21:4x 实跑红点: R6 盘上 md5 e06c1dd6 ≠ 锚点 16ac89f7」—— ★那个红就是 ISS-275 要消灭的红★ ⇒ ISS-275 已把判决源换成链头 ⇒ 这条 need 作为【待执行指令】已过期 ⇒ 退休; 它正文里的 4 个值全是历史值 ⇒ 不许照抄 |
| `iss260_h1_reanchor_after_v2_land` | 2026-11-16 | 5 | 5 | **退休 + 改写** | 它正文里明写「本单没落, 所以现在不用动」+「沙盒端到端实测的新 md5」⇒ 那 2 个 32 位 md5 是【排练值】⇒ 改写; 另外 3 个是历史值 ⇒ 退休; 整条 need 作为【待执行指令】已过期 ⇒ 退休 |
| `iss236_h1_reanchor_v2` | 2026-11-17 | 6 | 6 | **退休 + 改写** | 它是 iss236_h1_reanchor 的订正版, 正文里 3 个 32 位 md5 是【沙盒排练实测值】(它自己写明「排练值·真盘真落后 md5 会再变·以那一遍实测为准·不许拿排练值改台账」) ⇒ ★这条 need 自己就写着「不许拿排练值改台账」★ ⇒ 改写; 另外 3 个是历史值 ⇒ 退休 |
| `iss239_h1_reanchor_sw` | 2026-10-25 | 5 | 5 | **退休 + 改写** | 它正文里 3 个 8 位短写是【预估 / 副本排练值】(它自己写明「预估 (/tmp 副本 cp -a 整棵树实跑)」) ⇒ 改写; 另外 2 个 (34132f7e / b21b743a) 是已被取代的历史值 ⇒ 退休; 整条 need 作为【待执行指令】已过期 ⇒ 退休 |
| `iss283_sw_anchor_reanchor_after_landing` | 2026-11-17 | 4 | 4 | **退休** | 它正文里明写「盘上已是 ISS-283 落表后的 37f62ac3 / a4270120」+「降级 = 按台账 §16.2 链头 L1353 追加一条 entries」⇒ ★它给的处置恰恰就是 ISS-275 已经换成链头判决源的那件事 ⇒ 这条 need 作为【待执行指令】已过期 ⇒ 退休; 它正文里的 4 个 8 位短写都是历史值 ⇒ 不许照抄 |
| `iss249_kicad_sch_md5_not_anchor_sw` | 2026-11-16 | 0 | 0 | **退休** | ★这条 need 一个 md5 字面量都没有 (它说的是「.kicad_sch 的 md5 不能当锚点」) ⇒ 不在 H3 的逐条判据内 ⇒ 但它【同样已经过期】(ISS-275 之后 .kicad_sch 也不在受保护 5 件里) ⇒ 退休 (登记在本表里留档) |

★**§2-2 · 逐条 md5 登记 (★机器逐条复核用 ★ 本单【不许】改 need 条目·只出建议表★)** ★

★下列每一行都是机器可复核的: 【need key】+【它引的那个 md5】+【处置】三件套缺一 ⇒ H3 判红 ★

- NEED-KEY: iss232_no_netlist_change_anchor_ok | NEED-MD5: 3215020b6d4120e1b7728227effdc6d3 | PRODUCED-BY: ISS-220 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 8 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss233_sw_md5_reanchor | NEED-MD5: 3215020b6d4120e1b7728227effdc6d3 | PRODUCED-BY: ISS-220 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 8 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss233_sw_md5_reanchor | NEED-MD5: 34132f7e40a241e1fae1476be0eafbd5 | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 7 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss233_sw_md5_reanchor | NEED-MD5: a600afae493f5a7a6c55f46ad35ac89c | PRODUCED-BY: ISS-220 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 7 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss233_sw_md5_reanchor | NEED-MD5: b21b743a7702d30729f0d653c15392df | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 6 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: 1119c2a860c273833adaaf21af09d953 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: b65d200080ba9abbf4c6589584546ac8 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: cb477b37aa0d3ae36ed359d4b96c16a7 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-16
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: 16ac89f77c25a3f61834cc7ebcd78a7f | PRODUCED-BY: ISS-249 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 5 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: 2a7305741134788dfee9f13f34c656b4 | PRODUCED-BY: ISS-249 | DISPOSITION: 退休 | WHERE: BOM_v1.csv 落表链第 4 跳 · 链头 5b9993992405 | SINCE: 2026-11-16
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: 611c3ba3db3dc7de7213063375b96d01 | PRODUCED-BY: ISS-243 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 6 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: ef436a37412ac9b6eac3c9f41f1edca4 | PRODUCED-BY: ISS-249 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 5 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss257_h1_reanchor_to_sw_lead | NEED-MD5: 16ac89f77c25a3f61834cc7ebcd78a7f | PRODUCED-BY: ISS-249 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 5 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss257_h1_reanchor_to_sw_lead | NEED-MD5: 287e7861a0d1007748d92d9fbecdd490 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 4 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss257_h1_reanchor_to_sw_lead | NEED-MD5: e06c1dd633566aa44732762c2ff99d1c | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 4 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss257_h1_reanchor_to_sw_lead | NEED-MD5: ef436a37412ac9b6eac3c9f41f1edca4 | PRODUCED-BY: ISS-249 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 5 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss260_h1_reanchor_after_v2_land | NEED-MD5: 02c3cec178d33fdc65e49917b575fe25 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-16
- NEED-KEY: iss260_h1_reanchor_after_v2_land | NEED-MD5: 287e7861a0d1007748d92d9fbecdd490 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 4 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss260_h1_reanchor_after_v2_land | NEED-MD5: 2c950b675d1eb52176f00b5ba8e05152 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-16
- NEED-KEY: iss260_h1_reanchor_after_v2_land | NEED-MD5: 94642d07a69e8d60dd2af57f69b93607 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: BOM_v1.csv 落表链第 3 跳 · 链头 5b9993992405 | SINCE: 2026-11-16
- NEED-KEY: iss260_h1_reanchor_after_v2_land | NEED-MD5: e06c1dd633566aa44732762c2ff99d1c | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 4 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: 287e7861a0d1007748d92d9fbecdd490 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 4 跳 · 链头 9174309df1ec | SINCE: 2026-11-17
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: 94642d07a69e8d60dd2af57f69b93607 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: BOM_v1.csv 落表链第 3 跳 · 链头 5b9993992405 | SINCE: 2026-11-17
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: 9effa57cb827713cd6d645390ac65d72 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-17
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: cb830fbae560948bd10fd5780a10700a | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-17
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: e06c1dd633566aa44732762c2ff99d1c | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 4 跳 · 链头 6aee500e60ba | SINCE: 2026-11-17
- NEED-KEY: iss236_h1_reanchor_v2 | NEED-MD5: f617ffc1fd60e5b4a04ab911999dda17 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-11-17
- NEED-KEY: iss232_no_netlist_change_anchor_ok | NEED-MD5: a600afae | PRODUCED-BY: ISS-220 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 7 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: 34132f7e | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 7 跳 · 链头 6aee500e60ba | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: b21b743a | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 6 跳 · 链头 9174309df1ec | SINCE: 2026-11-16
- NEED-KEY: iss236_h1_reanchor | NEED-MD5: c195a117 | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: BOM_v1.csv 落表链第 5 跳 · 链头 5b9993992405 | SINCE: 2026-11-16
- NEED-KEY: iss239_h1_reanchor_sw | NEED-MD5: 34132f7e | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 7 跳 · 链头 6aee500e60ba | SINCE: 2026-10-25
- NEED-KEY: iss239_h1_reanchor_sw | NEED-MD5: 3b8cf3d9 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-10-25
- NEED-KEY: iss239_h1_reanchor_sw | NEED-MD5: b21b743a | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 6 跳 · 链头 9174309df1ec | SINCE: 2026-10-25
- NEED-KEY: iss239_h1_reanchor_sw | NEED-MD5: 319b21f2 | PRODUCED-BY: — | DISPOSITION: 改写 | WHERE: 不在任何一跳落表链上 (排练值 / 预估值) | SINCE: 2026-10-25
- NEED-KEY: iss239_h1_reanchor_sw | NEED-MD5: c195a117 | PRODUCED-BY: ISS-233 | DISPOSITION: 退休 | WHERE: BOM_v1.csv 落表链第 5 跳 · 链头 5b9993992405 | SINCE: 2026-10-25
- NEED-KEY: iss283_sw_anchor_reanchor_after_landing | NEED-MD5: e06c1dd6 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 4 跳 · 链头 6aee500e60ba | SINCE: 2026-11-17
- NEED-KEY: iss283_sw_anchor_reanchor_after_landing | NEED-MD5: 287e7861 | PRODUCED-BY: ISS-257 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 4 跳 · 链头 9174309df1ec | SINCE: 2026-11-17
- NEED-KEY: iss283_sw_anchor_reanchor_after_landing | NEED-MD5: 37f62ac3 | PRODUCED-BY: ISS-283 | DISPOSITION: 退休 | WHERE: netlist_v1.csv 落表链第 1 跳 · 链头 6aee500e60ba | SINCE: 2026-11-17
- NEED-KEY: iss283_sw_anchor_reanchor_after_landing | NEED-MD5: a4270120 | PRODUCED-BY: ISS-283 | DISPOSITION: 退休 | WHERE: netlist_v1_pins.csv 落表链第 1 跳 · 链头 9174309df1ec | SINCE: 2026-11-17
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: 3e504d2be83152e337949723e909be1b | PRODUCED-BY: — | DISPOSITION: 保持 | WHERE: HW/PCB/demo_mainboard.kicad_pro 的盘上现值 (受保护 5 件之一) | SINCE: 2026-11-16
- NEED-KEY: iss249_h1_reanchor_netlist_md5_sw | NEED-MD5: 611b869e13518c3c023fb178f91a0075 | PRODUCED-BY: — | DISPOSITION: 保持 | WHERE: HW/PCB/demo_mainboard.kicad_pcb 的盘上现值 (受保护 5 件之一) | SINCE: 2026-11-16
- NEED-KEY: iss249_kicad_sch_md5_not_anchor_sw | NEED-MD5: — | PRODUCED-BY: — | DISPOSITION: 退休 | WHERE: 该 need 无 md5 字面量 (同类过期 need·手工登记) | SINCE: 2026-11-16

★**§2-3 · 本单【只出建议表】的边界 (★不许直接改 `state/fragments/sw.yaml` 的 need 条目★)** ★

- 本单**没有**改任何一条 need 的正文 (`state/fragments/sw.yaml` 的 need 条目一个字没动)
- 本单**没有**改任何锚点 md5 (`SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块一个字没动)
- 上表的处置词**只是建议** ⇒ 要不要真把某些 need 标成 closed / 改写, **归 main 裁**
- ★**判据**: 一条 need 能不能退休, 只有一条机器判据 ⇒ ★**它要的「H-1 重锚」这件事有没有被 ISS-275 的【判决源换源】取代** ⇒ 被取代了 ⇒ 退休; 没被取代 ⇒ 不许退休 ★

<!-- H3-REG:END -->
<!-- S2-NEEDS:END -->

★**★§2-4 · 这 9 条 need 为什么【全部】是过期项 (★一句话·机器可判★)** ★

> ★**它们要的那件事 = 「把 `SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries[]` 里的 md5 改成新落表的值」⇒ 而 ISS-275 已经把判决源换成了【落表台账链头】⇒ 合法落表自动前移 ⇒ 【根本不需要再追锚点】⇒ 这些 need 作为【待执行的重锚指令】全部过期** ★
> — 逐字依据 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的 ISS-275 角色声明: ★**「`source_ledger.entries[]` 现在是【历史留痕】, 不再是 R6 的判决源」** ★

★**★§2-5 · 最危险的那一类 (★为什么这一单必须存在★)** ★

★**`iss236_h1_reanchor` / `iss260_h1_reanchor_after_v2_land` / `iss236_h1_reanchor_v2` / `iss239_h1_reanchor_sw` 这 4 条 need 正文里引的 md5, 是【沙盒排练值 / 预估值】⇒ 它们从来没落到过盘上** ★
- ★**`iss236_h1_reanchor_v2` 自己就写着**: ★**「排练值·真盘真落后 md5 会再变·以那一遍实测为准·不许拿排练值改台账」** ★
- ★**⇒ 若有人把其中任意一个值当成「待执行的重锚指令」照抄进锚点 ⇒ 锚点会被写到一个【不存在的值】上 ⇒ 而 ISS-275/ISS-284 正是花大力气堵掉这个「悄悄换真源」的洞** ★
- ★**⇒ 处置 = 改写 (不许照抄) ⇒ 这就是 §3「绝对不许做」第 ① 条的来源** ★

---

<!-- H4-REG:BEGIN -->
### H4-REG · 8 条板侧输入清单里没有「S10 换封装真值」这一条

- H4-ITEMS: 8
- H4-COVER: 0
- H4-GENERIC: 4
- H4-FINDING: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单 (SW01~SW08) 里, 没有任何一条的 `current_state` / `action` 讲的是【封装栏落真库封装名】这件事 ⇒ 覆盖条数 = 0** ★ ⇒ ★**⇒ S10 换封装真值这一跳, 在 SW 侧的板侧输入清单上是【完全空白的】** ★
- H4-IMPACT: ★**清单是那一趟的 SW 侧【收口清单】⇒ 它没有的跳 ⇒ 那一趟当天就没有人认领这一跳 ⇒ 这一跳红/不红都没人解释 ⇒ 而这一跳【必然换 3 个 md5】⇒ 正好撞在 §1.1 那三道条件闸的口径上 ⇒ 风险 = 有人为了让闸绿去改锚点 / 改判据** ★
- H4-COUNTERMEASURE: ★**本页 §1 逐闸写清了这一跳会不会红 / 红了怎么判; §3 给了当天 SOP ⇒ 空白被【登记】上了 ⇒ 那一趟当班的人照着 §3 念即可** ★ ⇒ ★**★本单【不许】直接往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 ⇒ 那是「改那一趟的清单」⇒ 归 main 裁★** ★ ⇒ ★**要加的话, 加的写法建议见本页交卷页 B5-2 (★归 main 转 hw-lead / 板侧作业包那一趟★)** ★
- ★**附: `H4-GENERIC=4` 的含义** ★: ★**8 条里有 4 条 (SW02 / SW04 / SW07 / SW08) 的 `current_state` / `action` 里泛泛提到过「封装」二字, 但没有一条说的是【封装栏落真值】⇒ 也就是说: 「泛提封装」的那 4 条, **一条都不覆盖这一跳** ⇒ 覆盖条数仍然是 0** ★
<!-- H4-REG:END -->

---

<!-- S3-SOP:BEGIN -->

## §3 · S10 这一跳的【当天 SOP】 (★给那一趟当班的人照着念 ★)

### §3.1 · 当天先跑什么 (★顺序不许换 ★)

★**第 0 步 · 先把台账那一行要齐的东西拿到手 (★这一步没做完, 后面全是白跑★)** ★
- ★**要三样**: ★**① 那一趟的落表单号** · ★**② 三份真源改完后的新 md5 (网表 / 脚表 / BOM 各一个)** · ★**③ 那三行「单号 | 文件名 | 改前 md5 | 改后 md5」四项同行的落表台账行** ★
- ★**拿不到 ⇒ 停** ⇒ ★**理由: 没有这三样, §1.1 那三道条件闸在盘上真源改完之后【必然红】⇒ 红了只能靠改锚点去「修」⇒ 那就是违规** ★

★**第 1 步 · 先跑基线闸 (★在盘上真源【还没改】的时候跑 ⇒ 这样才有对照★)** ★
```
python3 SW/tools/check_onepass_sw_release.py            # ⇒ rc=0 (10 道聚合 · fail-closed)
python3 SW/tools/check_onepass_sw_release.py --selftest  # ⇒ rc=0 (反向用例全抓到)
```
★**⇒ 这一步红了 ⇒ 那是【出发前就有的红】⇒ 跟 S10 无关 ⇒ 先记下来, 不要在这一趟里顺手修** ★

★**第 2 步 · 落表 (★hw-lead 的活 · SW 侧只读★)** ★
- ★**落表台账那三行四项同行** (★格式契约 = ISS-275 §1 ⑧★)
- ★**那个单号在 `state/issue_log.yaml` 留【文件名 + 新 md5】** (★ISS-312 / ISS-315 的留痕义务 ⇒ 缺了 §1.1 那道「留痕红」会红★)

★**第 3 步 · 落表后按 §1 逐闸复跑 (★只跑 §1 那 10 道·不跑别的★)** ★
```
python3 SW/tools/check_onepass_sw_sync.py
python3 SW/tools/check_sw_ref_reachability.py
python3 SW/tools/check_landing_trace_obligation.py
python3 SW/tools/check_demo_panel_spec.py
python3 SW/tools/check_demo_panel_spec_r6_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py
python3 SW/tools/check_shutdown_semantics.py
python3 SW/tools/check_timing_review_adc_sync.py
python3 SW/tools/timing_check.py
python3 SW/tools/check_onepass_sw_release.py
```

★**第 4 步 · 跑本单的闸 (★确认这一跳的登记与实测没有漂★)** ★
```
python3 SW/tools/check_sw_fp_truth_impact.py            # ⇒ rc=0 (H0~H7 八条)
python3 SW/tools/check_sw_fp_truth_impact.py --selftest  # ⇒ rc=0 (反向用例 6 条全抓到)
```

### §3.2 · 红了先看哪一条 (★按这个顺序看·不要乱翻 ★)

| 顺序 | 红的那一道 | ⇒ 先看什么 | ⇒ 判「预期」还是「坏了」 |
|---|---|---|---|
| 1 | ★**G03** `check_landing_trace_obligation.py` | ★**留痕**: 那个单号在 `state/issue_log.yaml` 里有没有【文件名 + 新 md5】★ | ★**有 ⇒ 【预期·补一句留痕即可】; 没有 ⇒ 【坏了·那一趟没落表】** ★ |
| 2 | ★**G04** `check_demo_panel_spec.py` (R6) | ★**盘上 md5 vs 落表台账链头** ★ | ★**台账里没有新值那一行 ⇒ 【预期·补台账】; 台账里有那一行但盘上 ≠ 链头 ⇒ 【坏了】** ★ |
| 3 | ★**G01** `check_onepass_sw_sync.py` (W6) | ★**同上** (W6 与 R6 同机制) ★ | ★**同上** ★ |
| 4 | ★**G10** `timing_check.py` | ★**那一趟是不是顺带改了那 8 行的 `value` / `dnp`** ★ | ★**是 ⇒ 归 SW03 (F1 期望值随落表定); 只改了封装栏却红 ⇒ 【坏了】** ★ |
| 5 | ★**G02 / G08 / G09** | ★**位号 / 口径页 / 文档同步** ★ | ★**这三道对封装栏免疫 ⇒ 它们红了必是别的跳 ⇒ 归 S1 那条线** ★ |
| 6 | ★**G05 / G06 / G07** | ★**夹具 / 判据本身** ★ | ★**跑在合成台账上 ⇒ 与盘面无关 ⇒ 【坏了·闸自己坏了】** ★ |

### §3.3 · 什么情况可以判「预期」 (★三条·缺一条就不许判预期 ★)

1. ★**落表台账里那一行四项齐全** (★单号 / 文件名 / 改前 md5 / 改后 md5 同在一行★) ⇒ ★**链头合法前移 ⇒ 盘上 ≠ 链头才是「预期」的形态** ★
2. ★**那个落表单号在 `state/issue_log.yaml` 里能查到【文件名 + 新 md5】** ⇒ ★**不是「悄悄换真源」** ★
3. ★**盘上三件的真值与那一行台账记录的改后 md5 逐字节一致** ⇒ ★**没有人动过盘上真源** ★

★**★三条同时成立 ⇒ §1.1 那三道条件闸的红是【预期】⇒ 补台账 / 补留痕即可 ⇒ 不许动锚点** ★

### §3.4 · 什么情况必须停 (★停 = 不许继续那一趟 · 交 main 裁 ★)

1. ★**台账那一行有, 但盘上 ≠ 链头, 且那一行的「改后 md5」也不是盘上的值** ⇒ ★**【坏了】⇒ 停** ★
2. ★**链头不唯一 / 链断 / 链头无单号** ⇒ ★**【取不准 ⇒ fail-closed】⇒ 停** ★
3. ★**G02 / G08 / G09 / G10 红了** ⇒ ★**【这一跳对它们免疫】⇒ 红的是别的跳 ⇒ 不要在 S10 这一跳里顺手修 ⇒ 停** ★
4. ★**G05 / G06 / G07 红了** ⇒ ★**【闸自己坏了】⇒ 停** ★
5. ★**有人提议「改一下锚点 md5 就绿了」** ⇒ ★**【这就是 ISS-275 / ISS-284 堵掉的洞】⇒ 停** ★

### §3.5 · ★绝对不许做★ (★逐字照抄 ISS-275 §R-10 + ISS-284 的红线表述 · 不许自己改写 ★)

★**★红线一 (★ISS-275 · 判决源换源 · `SW/SW_MD5_BASELINE_LEDGER.md` §3 R-10 逐字★)** ★

> ★**「合法落表不再红 (链头自动前移) · 悄悄换真源照样红 (盘上 ≠ 链头) · 取不准一律判红 (链头不唯一 / 链断 / 有记录不在链上 / 链头无单号) · 硬保护件 (板 / `.kicad_pro`) 走纯 md5 比对, 不受台账机制影响」** ★
> ★**⇒ 照这条: 【合法落表让闸红 ⇒ 那是链头前移的正常形态】· 【不许为了让闸绿而动锚点】· 【不许把「取不准」放宽成「取最近一条」】** ★

★**★红线二 (★ISS-275 · 判决源换源 · `SW/SW_MD5_BASELINE_LEDGER.md` §1 角色声明 ③④ 逐字★)** ★

> ★**③ 取不准一律判红 (★fail-closed, 一条都不许放宽★): ★**链头不唯一 / 链断 / 有记录不在链上 / 链头没有落表单号 ⇒ 全部红** ★**
> ★**④ 「悄悄换真源」判据仍在 (★不许为了不红就把它删掉★): ★**盘上真源 md5 ≠ 台账链头 ⇒ 红** ★**

★**★红线三 (★ISS-284 · 合法改板机制 · `SW/SW_MD5_BASELINE_LEDGER.md` §1 ISS-284 段 ②③④ 逐字★)** ★

> ★**② 【判据方向不许变】: ★**盘上 ≠ 台账链头 ⇒ 红** ★ ⇒ ★**合法改板只让【链头前移】, 不是把判据放松** ★**
> ★**③ 【fail-closed 三条一条不许动】: ★**链头不唯一 / 链断 (链头那一行的改前对不上链) / 链头无单号 ⇒ 一律红** ★ ⇒ ★**取不准一律判红, 不许「取最近一条」** ★**
> ★**④ 【保护基线不许被偷偷前移】: 锚点里的 `md5` (保护基线) ★**必须留在台账链的链尾** ★ ⇒ ★**把基线改成新值 (想「让盘上 == 基线」凑绿) ⇒ 红** ★**

★**★红线四 (★ISS-279 · 三条方案都要守的红线 · `SW/BOARD_ONEPASS_SW_SYNC.md` §4.3 逐字★)** ★

> 1. ★**不许把「改 md5」变成「随手改一下就绿」** ⇒ ★**任何方案都要留下「谁在哪个单号下改的」的证据** ★ ⇒ ★**证据必须可机器查 (落表台账里查得到那个单号 + 那一行四项齐全)★ ★**
> 2. ★**不许为了不红而放宽「盘上 ≠ 链头 ⇒ 红」这条** ⇒ ★**合法落表 / 合法改板 只应让【链头自动前移】, 不是让判据变松** ★ ⇒ ★**判据阈值一条都不许动** ★**
> 3. ★**不许把「取不准」放宽成「取最近一条」** ⇒ ★**fail-closed 那条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条都不许动** ★ ⇒ ★**ISS-275 的 R6 判据逻辑原样继承** ★**

★**★⇒ 把上面四条翻成那一趟当班的人能照做的动作 (★四条不许改·动作不许加★)** ★

| ★**绝对不许做** ★ | ★**为什么 (★依据上面哪条★)** ★ | ★**该做什么** ★ |
|---|---|---|
| ★**改锚点 md5** (★`SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries[]` / `hard_protected[].md5`★) | ★**红线三 ④ + 红线二 ④ + 红线四 1** ★ | ★**补落表台账那一行 (四项同行) ⇒ 链头自然前移** ★ |
| ★**改判据阈值 / 放宽判据方向** (★包括把「盘上 ≠ 链头 ⇒ 红」改软★) | ★**红线二 ④ + 红线三 ② + 红线四 2** ★ | ★**停 ⇒ 交 main 裁** ★ |
| ★**改盘上真源** (★网表 / 脚表 / BOM / 原理图 / 板·任何一格★) | ★**红线一 + 红线二 ④** ★ | ★**停 ⇒ 交 main 裁 (★改真源 = 越权落表★)** ★ |
| ★**回退落表** (★把那一趟已经落下去的封装真值撤掉·只为了让闸绿★) | ★**红线一 (★合法落表不再红·链头自动前移★) + 红线三 ②** ★ | ★**停 ⇒ 交 main 裁** ★ |
| ★**照抄 §2 里那些陈旧 md5 / 排练值** (★进任何锚点★) | ★**§2-5 (★`iss236_h1_reanchor_v2` 自己就写着「不许拿排练值改台账」★)** ★ | ★**只许用【落表台账链头】** ★ |
| ★**把「取不准」放宽成「取最近一条」** | ★**红线二 ③ + 红线三 ③ + 红线四 3** ★ | ★**停 ⇒ 交 main 裁** ★ |

<!-- S3-SOP:END -->

---

## §4 · 复现命令清单 (★全部真实存在 · 本单本机实跑过 ★)

★**★TMPDIR 约定 (★照抄 ISS-335 的做法·本机系统临时目录带配额且已到顶·不指会 EDQUOT 假红★)**: ★**子进程一律把 `TMPDIR` / `TMP` / `TEMP` 指到项目内 `tmp/iss362_tmp`** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss362_tmp TMP=$PWD/tmp/iss362_tmp TEMP=$PWD/tmp/iss362_tmp
mkdir -p "$TMPDIR"

# ---- §0.2 三份真源的封装栏实测 (★BOM 第 10 栏 / 网表第 14 栏 / 脚表第 11 栏★) ----
python3 -c "import csv,collections;r=list(csv.DictReader(open('HW/BOM_v1.csv',encoding='utf-8')));print(len(r),dict(collections.Counter(x.get('board','') for x in r)))"
grep -c '' HW/BOM_v1.csv HW/netlist_v1.csv HW/netlist_v1_pins.csv
head -1 HW/netlist_v1.csv | tr ',' '\n' | nl | sed -n '14p'
head -1 HW/netlist_v1_pins.csv | tr ',' '\n' | nl | sed -n '11p'
head -1 HW/BOM_v1.csv | tr ',' '\n' | nl | sed -n '10p'

# ---- §0.3 盘上现值 + 落表台账链头 (★照抄 check_demo_panel_spec.py 的 sw_ledger_state()★) ----
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 -c "import sys;sys.path.insert(0,'SW/tools');import check_demo_panel_spec as d;t=open(d.LEDGER_CANON,encoding='utf-8').read();[print(r,d.sw_ledger_state(r,t)['head'],d.sw_ledger_state(r,t)['head_iss'],len(d.sw_ledger_state(r,t)['chain'])) for r in ('HW/netlist_v1.csv','HW/netlist_v1_pins.csv','HW/BOM_v1.csv')]"

# ---- §1 10 道 SW 闸 (★逐道 rc★) ----
python3 SW/tools/check_onepass_sw_sync.py
python3 SW/tools/check_sw_ref_reachability.py
python3 SW/tools/check_landing_trace_obligation.py
python3 SW/tools/check_demo_panel_spec.py
python3 SW/tools/check_demo_panel_spec_r6_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py
python3 SW/tools/check_shutdown_semantics.py
python3 SW/tools/check_timing_review_adc_sync.py
python3 SW/tools/timing_check.py
python3 SW/tools/check_onepass_sw_release.py
python3 SW/tools/check_onepass_sw_release.py --selftest

# ---- 本单的新闸 (★H0~H7 + 反向用例★) ----
python3 SW/tools/check_sw_fp_truth_impact.py
python3 SW/tools/check_sw_fp_truth_impact.py --selftest
python3 SW/tools/check_sw_fp_truth_impact.py --json

# ---- §2 待办 need 的 md5 逐条比对 (★机器算★) ----
python3 logs/iss362/probe_iss362.py            # ★只读探针·输出 §0/§2 全部读数★
python3 logs/iss362/gen_h3_block.py            # ★生成 §2 的 H3-REG 块★

# ---- 边界双证 (★板 / 真源 / 既有闸 / 既有页面 / 锚点 逐字节不变★) ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       SW/SW_MD5_BASELINE_LEDGER.md SW/BOARD_ONEPASS_SW_SYNC.md \
       SW/tools/check_onepass_sw_sync.py SW/tools/check_sw_ref_reachability.py \
       SW/tools/check_landing_trace_obligation.py SW/tools/check_demo_panel_spec.py \
       SW/tools/check_onepass_sw_release.py SW/tools/timing_check.py \
       state/gate_check.py state/merge.py state/frag_write.py
stat -c '%n %s %y' HW/PCB/demo_mainboard.kicad_pcb

# ---- 项目面 (★收工验收★) ----
python3 state/merge.py
python3 state/gate_check.py
```

★**★本单留证目录**: ★**`logs/iss362/`** (★基线 md5 / 10 道闸基线逐道 rc / 链头实测 / need 的 md5 逐条比对表 / 沙盒预演全量输出 / selftest 全量输出 / 闸复跑输出★) ★

---

## §5 · 证据分级 (★逐条标注 ★)

| 读数 | 等级 | 出处 |
|---|---|---|
| 三份真源的盘上 md5 / 链头 / 链长 / 链头产出单号 | ★**实测** ★ | §4 的 `md5sum` + `sw_ledger_state()` 实跑 |
| 三份真源封装栏的栏位 / 行数 / 待定类计数 / 板别分布 | ★**实测** ★ | §4 的 `csv.DictReader` 实跑 |
| 10 道 SW 闸的现状 rc | ★**实测** ★ | §4 逐道实跑 (★`H1-READERS` 与 §1 每行的 rc 都由 `check_sw_fp_truth_impact.py` 的 H0/H1 机器复核★) |
| `SW/tools/*.py` 里读封装栏的闸 = 0 | ★**实测** ★ | §4 的新闸 H1 实扫 |
| 8 条板侧输入清单覆盖这一跳的条目 = 0 | ★**实测** ★ | §4 的新闸 H4 实读 JSON 块 |
| 待办 need 的 md5 逐条判定 (40 条陈旧 / 9 条 need) | ★**实测** ★ | §4 的 `probe_iss362.py` 实跑 |
| S1 位号改名 186 个位号 / 3 道闸会动 | ★**实测** ★ | `state/fragments/sw.yaml` 的 `iss321_sw_rename_affected_gates` / `iss321_sw_rename_same_batch_items` (★ISS-321 交卷口径·盘上可查★) |
| S10 那一跳当天「链头自动前移 ⇒ 三道条件闸绿」的预测 | ★**推算** ★ | ★由 H2 实测的链头机制外推 ⇒ ★以 §3 的 SOP 实跑为准★ |
| 板端 / 实物 | ★**0数据** ★ | ★本机无板 ⇒ 本页无任何板端实测数字★ |

---

## §6 · 本单边界自证 (★交卷时逐条机器复核 ★)

| 边界 | 自证方式 | 结论 |
|---|---|---|
| ★**零写板** ★ | 板 md5 + mtime + 字节数 前后各打一次 | ★**不变** ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三个 md5 前后各打一次 | ★**不变** ★ |
| ★**零改既有闸** ★ | 既有 6 道 SW 闸脚本 + `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` md5 前后各打一次 | ★**不变** ★ |
| ★**零改既有页面** ★ | `SW/BOARD_ONEPASS_SW_SYNC.md` / `SW/SW_MD5_BASELINE_LEDGER.md` md5 前后各打一次 | ★**不变** ★ |
| ★**零改锚点 md5** ★ | `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块 md5 前后各打一次 | ★**不变** ★ |
| ★**零外发 / 零采购 / 零联系供应商** ★ | 本单未发任何邮件 / 询价 / 问询 / 采购 | ★**成立** ★ |
| ★**不替老板拍板** ★ | 本页只给【机制说明 + 建议表 + SOP】; 「要不要往 8 条清单里加第 9 条」**归 main 裁** | ★**成立** ★ |
| ★**不写别人的分片** ★ | 分片写入只走 `state/frag_write.py --agent sw-lead` | ★**成立** ★ |
| ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★ | 本单零写入 | ★**成立** ★ |
| ★**沙盒落项目盘 `tmp/`** ★ | 沙盒根 = `tmp/iss362_gate_sbx/`; `find -type l` 命中必须 = 0 (★禁止 `os.symlink()`★) | ★**成立** ★ |
