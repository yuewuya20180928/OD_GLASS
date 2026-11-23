# ISS-370 · sw-lead · 「板那一趟」腿 B（网表节点具名）对 SW 侧的影响面 + 同批改动清单

★★**题**: ★**把「板只改一次」那一趟的【腿 B = 网表节点具名 200 条指令】对 SW 侧判据链的破坏面查清，并做成【逐条可执行清单 + 一条机器闸 + 沙盒预演】** ★★
★★**类别**: ★**纯分析 + 作业包 + 新建闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发** ★★

---

## ★★〇 · main 的本机实读 (★2026-11-23 17:4x~17:5x · 全部数字本机可复跑 · 不抄任何 agent 报告★) ★★

★**① 腿 B 是什么 (★已在盘 · 你只读·不许重做★)**:
- ★**指令全清单**: `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` §2.2 (★200 条: 改名 196 + 补行 4★) · §2.1 (★90 件逐件作业表★)
- ★**腿 B 网表副本 (★已在盘·★沙盒起点直接用它·不许自己重新生成★★)**: `tmp/iss364_sbx/netlist_v1_legB.csv` (★145,179 B · md5 `724f0bf71cb7ec6c74e389cf9cd8d3fe`★)
- ★**腿 B 只改 `HW/netlist_v1.csv` 两栏**: main 本机逐格比对 ⇒ ★**196 格改动全在 `node1` (120 格) + `node2` (76 格) 两栏** · `net` / `ref` / `value` / `type` / `dnp` / `board` / `footprint` 等栏 ★**一格未动** ★
- ★**行数**: 513 → 517 (★+4 = 补行 4 条★)

★**② ★★本单为什么必须存在 (★main 本机实测·★这是全篇最硬的一条★)★★**:

★**腿 B 会把 SW 侧的门禁打红 —— 而这一趟【本来就必须做腿 B】** ⇒ ⇒ **不查清 ⇒ 那一趟开工当天 SW 门禁当场红 ⇒ 板改到一半发现 ⇒ 要么硬改闸 (⇒ 把红项调没) 要么板 md5 变第二次 (⇒ 违「板只改一次」)**

★**main 本机实跑三组 (★全部可复跑·★命令在 §五★)**:

| 组 | 网表 | `SW/tools/timing_check.py` 读数 |
|---|---|---|
| ★**基线** ★ | 真网表 `HW/netlist_v1.csv` | ★**85/85 全过 · rc=0** ★ |
| ★**对照组 (★证明不是路径问题★)** ★ | ★**真网表内容·换个路径** (`tmp/iss370_sbx/netlist_REAL_copy.csv`) ★ | ★**85/85 全过 · rc=0** ★ ⇒ ★**⇒ 下面的红不是「路径」造成的★** |
| ★**腿 B 全量** ★ | `tmp/iss364_sbx/netlist_v1_legB.csv` | ★**70/85 · rc=1 · 15 条红** ★ |

★**★再拆一层 (★main 本机实跑·★把「改名」和「补行」两个作用分开·★不然你只能拿到症状拿不到根因★)★★**:

| 变体 | 构造 | 读数 | 结论 |
|---|---|---|---|
| ★**R = 只改名 (196 格·0 补行·513 行)** ★ | main 已落 `tmp/iss370_sbx/netlist_v1_rename_only.csv` | ★**71/85 · 14 条红** ★ | ★**⇒ 改名单独就造成 13 条语义红 + 1 条锚点红★** |
| ★**A = 只补行 (4 行·0 改名·517 行)** ★ | main 已落 `tmp/iss370_sbx/netlist_v1_rowadd_only.csv` | ★**73/85 · 2 条红** ★ | ★**⇒ 这 2 条全是【锚点/行数】类 (「现行网表 = 513 数据行 (行数不许变)」+「现行网表 md5 ∈ 落表台账登记的状态」) ⇒ 是【落表义务】不是【语义破坏】⇒ 合法落表 + 重锚即可解★** |

★**⇒ 一句话根因 (★main 本机读源码定位★)**: ★**腿 B 把网表节点串从【裸位号 `R_BAT_DET_2`】改成【具名脚 `R_BAT_DET_2 pin1`】⇒ 而 SW 侧 `SW/tools/timing_check.py` 的 `resolve_chain_landing()` (★L1013★) 判中点网用的是 ★**`{node1, node2} == {上臂位号, 下臂位号}` 的【精确字符串相等】★** ⇒ 改名后 `node1="R_BAT_DET_1 pin1"` / `node2="R_BAT_DET_2 pin1"` ⇒ ★**精确相等不成立 ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串 ADC 判据全塌 (★这才是那 13 条语义红的根因·不是「改名会坏」这种泛泛结论★)** ★**

★**③ ★★本单要你查的【全部 15 条红】逐条 (★main 本机跑出来的原文·★不是推测★)★★**:

| # | 红项原文 (★main 实跑打印★) | 红因初判 (★★你必须自己复核·不许照抄 main 的初判★★) |
|---|---|---|
| 1 | `ADC 源阻抗 = 37.5k (★ISS-291: 判决对象 = BAT_DET 链 → pin38 SARADC_VIN5★)` | ★取链塌 ⇒ 判决对象/源阻抗取不到★ |
| 2 | `ADC tau = 3.75ms (★ISS-291 口径★)` | ★同上★ |
| 3 | `ADC 12bit 建立 33.8ms ≤ 300ms 红线` | ★同上★ |
| 4 | `ADC 漏电偏移 37.5mV ≤ 0.4V 红线` | ★同上★ |
| 5 | ★`网表锚点: 现行网表 = 513 数据行 (行数不许变)`★ | ★**落表义务类** (★变体 A 单独就红·★⇒ 合法落表即可解★)★ |
| 6 | ★`网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)`★ | ★**落表义务类** ★ |
| 7 | `F4' 实读: ADC 判决对象 = BAT_DET 链 (落点 J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); BAT_DET 三颗必装` | ★取链塌★ |
| 8 | `F4 实读: 漏电偏移 37.5mV = 2.1% FS ⇒ 与网表 L182 note 写死的数逐字对上` | ★取链塌★ |
| 9 | `F4 实读: 判决源 = SoM 脚表 signal 列 (落点判 SAR-ADC), 取链模式 = by_landing_pin` | ★取链塌★ |
| 10 | `F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%)` | ★取链塌★ |
| 11 | `F4D 实读: VBUS_DET_D 落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (数字脚 ⇒ 不进 ADC 判据)` | ★取链塌★ |
| 12 | `REV-12 反向: 把满量程 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据必须变红` | ★**反向用例** ★★ (★★它红是因为正向判据已经塌了·⇒ 修完正向它要跟着回绿·★★)★ |
| 13 | `REV-13 反向: 把取链规则改回「元组第一条」⇒ 判决对象判据必须变红` | ★同上★ |
| 14 | `REV-14 反向: 把 BAT_DET 三颗改回 DNP ⇒ 「ADC 输入悬空」判据必须变红` | ★同上★ |
| 15 | `REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ 过压判据必须变红` | ★同上★ |

★**④ ★★SW 侧还有两处【同批必须动】的地方 (★main 本机实测·★不是推测★)★★**:
- ★**`SW/tools/check_demo_panel_spec.py` 的 R6**: main 实跑 (★沙盒 = 腿 B 网表★) ⇒ ★**红**: `R6 台账链: 盘上真源 md5 HW/netlist_v1.csv = 724f0bf71cb7 ≠ 台账最新记录 6aee500e60ba (真源被换了或台账没更新)` ★ ⇒ ★**⇒ 腿 B 一落地, 网表 md5 必变 ⇒ R6 三方对账必红 ⇒ 必须同批【落表 + 重锚】★**
- ★**`SW/tools/check_landing_trace_obligation.py`**: main 实跑 (★沙盒 = 腿 B 网表★) ⇒ ★**rc=0 全绿** ★ ⇒ ★**⇒ 它判的是【issue_log 里有没有留落表留痕】, 不判盘上 md5 ⇒ 腿 B 落地时它要一起被同批留痕 (★落表单号 + 新 md5★)★**

★**⑤ ★★哪些 SW 闸【实测不受腿 B 影响】(★negative 结论也要写·★不然下一个人还会重查★)★★** — main 本机实跑 (★沙盒 = 腿 B 网表·`--root` 指沙盒根★):

| 闸 | 读数 | 结论 |
|---|---|---|
| `SW/tools/check_shutdown_semantics.py` | ★**rc=0 · R1~R7 全过** ★ | ★不受影响 (★它按 `net` 列 + 并查集解析·不依赖精确相等★)★ |
| `SW/tools/check_sw_ref_reachability_v2.py` | ★**rc=0 · 绿** ★ | ★不受影响★ |
| `SW/tools/check_load_switch_selection.py` | ★**rc=0 · PASS** ★ | ★不受影响★ |
| `SW/tools/check_landing_trace_obligation.py` | ★**rc=0 · 全绿** ★ | ★不受影响 (★但同批要留痕★)★ |

★**⑥ ★★SW 侧已有的【同批清单】范本 (★你照它的格式写·★不要另起炉灶★)★★**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (★ISS-323 · S1 位号改名那一趟的 7 件必须同批改的活 · 逐字可执行清单★) ⇒ ★**你的产出 = 腿 B 那一趟的同款清单 (★腿 B 版★) ⇒ 结构照它 (★§0 口径与边界自证 / §0-3 逐件总表 / 逐件 9 字段 / 沙盒实测读数列 / §边界自证★)★**

★**⑦ 台账/锚点现状 (★你在其上作业·不许重写它★)**:
- `SW/SW_MD5_BASELINE_LEDGER.md` (★R6 三方对账的锚点 + 落表台账链 + H-1 重锚机制★)
- `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★落表台账本体·★网表真源的落表记录在这里★)
- `SW/BOARD_ONEPASS_SW_SYNC.md` (★SW 侧板侧输入收口·★§2 是 8 条逐条表 (★固定 9 字段★)★) ⇒ ★**你只登记·不许改它的正文★**

---

## ★★一 · 本单交付物 (★3 件 · 不许扩项★) ★★

### ★★① 第 1 件 · 一页: ★**新建** `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` ★★

★**必须包含 (★逐条·不许少★)**:
- ★**§0 口径与读数** ★: 上面 ①②③④⑤ 七条 (★每个数字都要能被 §五 的某条命令复现·**不许抄 main 的转述**·★要写「main 17:4x 实跑」并附你**自己复跑**的读数★) ★
- ★**§1 15 条红逐条表** ★: 一行一条 (★# / 红项原文 / 红因 (★你复核过的·不许抄 main 的初判★) / 归类 (★语义破坏 vs 落表义务 vs 反向用例★) / 修法 / 会红的闸 / 修完怎么自证回绿★) ★
- ★**§2 ★★「腿 B ⇒ SW 侧必须同批改的活」总表 (★本单的真命门★)★★** ★: 一行一件 (★件号 / 改哪个文件 / 归属 (★SW 域 or 跨域只给改法★) / 时序 (★必须同批 / 可板后补·★并给依据★) / 改的是脚本还是数据还是夹具还是文档 / 改法 (★照着就能干·★不许写「调整相关逻辑」这种废话★) / 沙盒实测读数 (★改前 rc + 改后 rc★) / 证据等级★) ★
  - ★**★特别地·你必须把【跨域那几件】单独列出来 (★照 ISS-323 §0-3 第 4 件的写法★)**: ★**网表真源落表 (★网表 md5 变了 ⇒ 落表台账 + R6 重锚★) ⇒ 那是 hw-lead 的地界·你只给改法 + 时序 + 会红哪道闸·不许代做·不许改 `HW/` 下任何文件★** ★
- ★**§3 三条反向自证** ★: ① 喂【只改名不补行】的网表 ⇒ 那 13 条语义红必须全在 (★证明你的分类对得上★) ② 喂【只补行不改名】的网表 ⇒ 那 2 条落表义务红必须全在、语义红必须全不在 (★证明「语义红」与「落表义务红」确实是两件事★) ③ 喂【真网表】⇒ 必须 85/85 全绿 (★证明你的沙盒没污染★)
- ★**§4 降级方案 (★逐条必填·一件不空·三选一: 官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开★)** ★
- ★**§5 未决项与卡点** ★: ★哪些真要老板拍 (★★只登记·**不许代拍**★) · ★哪些要 main 裁 (★写清「要谁回答什么」★)★

### ★★② 第 2 件 · 一条机器闸: ★**新建** `SW/tools/check_onepass_legb_sw_impact.py` ★★

★**判据 (★内容级·**不挂 md5**·沿用 `SW/tools/check_sw_fp_truth_impact.py` / `check_fp_truth_read.py` 的做法·★文档改一个字就重判★)**:
- ★**G0** ★**基准块存在且是合法 JSON** (★同款 BEGIN/END 块★) ★
- ★**G1** ★**腿 B 的三个数由脚本自己算出来** ★: 读 `tmp/iss364_sbx/netlist_v1_legB.csv` + 读 `HW/netlist_v1.csv` ⇒ ★**算出「改动格数 = 196」+「改动栏 ⊆ {node1, node2}」+「行数 513 → 517」** ★ ⇒ 页里写的 ≠ 脚本实算 ⇒ 红 ★
- ★**G2** ★**15 条红逐条齐全** ★: 从沙盒**实跑** `timing_check.py` 抓红项 ⇒ 抓到的红项集合 == 页里声明的集合 ⇒ ★**缺一条即红 + 点名** ★
  - ★**★你必须【自己实跑】timing_check 拿红项·不许抄 main 抄的 15 条 (★main 的 15 条是 main 17:4x 的读数·你可以独立复现·★复现不上要写清差异★)★** ★
- ★**G3** ★**每条红项的归类非空** (★语义破坏 / 落表义务 / 反向用例·三选一★) ⇒ ★**空 ⇒ 红 + 点名** ★
- ★**G4** ★**「语义红」与「落表义务红」可分离** ★: 脚本实跑两个变体 (★只改名 / 只补行·★**只读现成的 `tmp/iss370_sbx/netlist_v1_rename_only.csv` + `netlist_v1_rowadd_only.csv`·不许自己重新生成·不许写进真件★) ⇒ ★**判「只改名变体的红项里没有落表义务红」+「只补行变体的红项全是落表义务红」** ★ ⇒ 对不上即红 (★★这一条是本闸的核心: 它抓的是「把两类红混为一谈」★★) ★
- ★**G5** ★**§2 同批清单的每件都齐 8 字段** (★★尤其「归属」与「时序」不许空·★跨域那几件的归属必须写「跨域·不是 SW 的域」★★) ★ ⇒ ★**空 ⇒ 红 + 点名** ★
- ★**G6** 证据等级全在五级白名单 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★ ⇒ 写 `[官方]` = 红★) ★
- ★**G7** 正文无挂起措辞 (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★) ★
- ★**G8** ★**「板 md5 与三份真源 md5 前后逐字节未变」这一条不许靠本机自证·要用受保护基线值判** ★: ★**判「板 md5 == `611b869e13518c3c023fb178f91a0075`」+「网表 md5 == `6aee500e60ba0732f83a9cf557ba90ab`」+「脚表 == `9174309df1ec9411ac8e8d9e80ee386a`」+「BOM == `5b9993992405904a60ac96a020b375d8`」** ★ ⇒ ★**★这一条同时钉住「你没有偷偷改真源」—— 你的沙盒副本必须落在 `tmp/iss370_sbx/`, 改了真件 ⇒ G8 红★ ★

★**`--selftest` 反向用例 ≥7 条, 每条自证「红的是目标那一条, 其余仍绿」**: ★**① 把 §1 里某一行删掉 (★挑第 10 条·`F4 实读: ADC 节点 @4.2V`★) ⇒ G2 红且 G0/G1/G3~G8 仍绿 · ② 把 §1 某行的归类改成空 ⇒ G3 红 · ③ 把 §1 的 15 这个数改成 14 ⇒ G2 红 · ④ 把 §2 某件的「归属」清空 ⇒ G5 红 · ⑤ 把 §2 某件的「时序」清空 ⇒ G5 红 · ⑥ 把 §0 的「改动格数 196」改成 195 ⇒ G1 红 · ⑦ 正文塞「等原厂回信」⇒ G7 红 · ⑧ 把某条证据等级写成 `[官方]` ⇒ G6 红 · ⑨ 把 §2 某件的「改法」换成「调整相关逻辑」⇒ G5 红 (★判「改法里有空洞词」★)★ ★

★**★沙盒一律落项目盘 `tmp/iss370_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)★**

### ★★③ 第 3 件 · 交卷页 + 分片 + 留证 ★★
- ★**交卷页** `HANDOFF/2026-11-23_sw-lead_ISS370_腿B对SW侧影响面.md` (★B1~B6 六段齐全 + 20 条验收逐条判定 + 落盘文件清单 + 沙盒留证路径★) ★
- ★**分片** `state/fragments/sw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ ★**写前后各记一次 md5 基线·期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖** ★
- ★**留证** `logs/iss370/` (★基线 md5 / 三组对照跑分的原文输出 / 15 条红逐条 / 沙盒前后读数 / selftest 全量输出 / 闸复跑输出★) ★

---

## ★★二 · 边界 (★逐条·不许越★) ★★

★**零写板** ★ (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B ⇒ **开工前 + 交卷后各打一次双证**★) ★
★**零落表** ★ (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸** ★ (★`SW/tools/timing_check.py` · `SW/tools/check_demo_panel_spec.py` · `SW/tools/check_shutdown_semantics.py` · `SW/tools/check_sw_ref_reachability_v2.py` · `SW/tools/check_onepass_sw_sync.py` · `SW/tools/check_fp_truth_read.py` · `SW/tools/check_sw_fp_truth_impact.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节不许改★) ★
★**★你的【改法】只是清单里的字·不是真改·★** ★ (★§2 里写「这一趟要怎么改」·**不许现在就改**·★那一趟还没到★) ★
★**零改既有页面正文** ★ (★`SW/BOARD_ONEPASS_SW_SYNC.md` · `SW/SW_MD5_BASELINE_LEDGER.md` · `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` 老字一字不许删·不许改·只在交卷页里写建议★) ★
★**零挂链** ★ (★新闸交脚本但不挂进 `state/gate_check.py` —— 挂链是 main 的机制地界·ISS-330/333/362 同款★) ★
★**零外发 / 零采购 / 零联系供应商** ★ (★不发邮件·不询价·不问询·不下采购单★) ★
★**不替老板拍板** ★ (★★只登记缺口 + 给依据 + 给代价·**不许代选**★) ★
★**不写别人的分片** ★ (★只写 `state/fragments/sw.yaml`★) ★
★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★
★**证据分级必标** ★ (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★ (★ISS-360 cont0 就是死在这上面★) ★
★**★上下文纪律 (★ISS-363 就是死在这上面★)★**: ★**分段做 + 骨架先落盘 + 大文件不许整份读进对话** ★ (`HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` 176 KB · `SW/SW_MD5_BASELINE_LEDGER.md` 75 KB · ★**只 grep 你要的那几行·不许整份 cat 进上下文★**) ★

---

## ★★三 · 必跑命令 (★全部真实存在·★main 2026-11-23 17:4x~17:5x 本机实测过★) ★★

```bash
# ★★三组对照 (★main 已实跑过·你要自己复现★) ★★
python3 SW/tools/timing_check.py                                              # ★基线 · rc=0 · 85/85★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_REAL_copy.csv  # ★对照组 · rc=0 · 85/85★
python3 SW/tools/timing_check.py --netlist tmp/iss364_sbx/netlist_v1_legB.csv    # ★腿B全量 · rc=1 · 70/85★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rename_only.csv  # ★只改名 · rc=1 · 71/85★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rowadd_only.csv  # ★只补行 · rc=1 · 73/85★
python3 SW/tools/check_demo_panel_spec.py --root tmp/iss370_sbx/root         # ★R6 锚点 · rc=1 (网表 md5 变了)★
python3 SW/tools/check_shutdown_semantics.py --root tmp/iss370_sbx/root      # ★rc=0 (negative 结论)★
python3 SW/tools/check_sw_ref_reachability_v2.py --root tmp/iss370_sbx/root   # ★rc=0 (negative 结论)★
python3 SW/tools/check_landing_trace_obligation.py --root tmp/iss370_sbx/root # ★rc=0 (negative 结论)★

# ★★本单新建 (★你交的两个脚本★) ★★
python3 SW/tools/check_onepass_legb_sw_impact.py
python3 SW/tools/check_onepass_legb_sw_impact.py --selftest

# ★★既有闸复跑 (★一个字节没改·只许跑不许改★) ★★
python3 SW/tools/check_fp_truth_read.py
python3 SW/tools/check_sw_fp_truth_impact.py
python3 SW/tools/check_onepass_sw_sync.py
python3 state/merge.py                          # rc 必须 0
python3 state/gate_check.py                     # rc 必须 0 · Q1 必须 18/18
python3 state/check_brief_commands.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② 三个数 (196 / 改动栏 ⊆ {node1,node2} / 513→517) 与脚本实算一致 ③ **15 条红逐条齐全且与你自跑的集合一致** ④ 每条红有归类 (★三类之一★) ⑤ §2 同批清单每件 8 字段齐全 ⑥ 跨域那几件归属写「跨域·不是 SW 的域」且你**没碰** `HW/` 任何文件 ⑦ 改法逐条具体 (★无空洞词★) ⑧ §3 三条反向自证全部自证成功 ⑨ 证据等级全在五级白名单 ⑩ 降级方案逐件非空 ⑪ 正文零挂起措辞 ⑫ 自建闸裸跑 rc=0 ⑬ `--selftest` ≥7/7 全 PASS 且每条自证「只红目标那条」 ⑭ 沙盒在项目盘 `tmp/iss370_sbx/` (★不写 /tmp★) ⑮ **板 md5/mtime 逐字节未变** ⑯ **网表/脚表/BOM md5 逐字节未变** ⑰ 既有闸脚本一个字节没改 ⑱ `merge.py` rc=0 ⑲ `gate_check.py` rc=0 且 Q1 18/18 ⑳ 分片只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss370/` 留证在盘
