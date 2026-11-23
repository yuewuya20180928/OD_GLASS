# ISS-356 · hw-lead · ★「板那一趟」封装真值基线 (100 件必装器件的占位封装 → 真库封装映射) · 纯分析/作业包 · 零写板★

★**题**: ★**「板只改一次」那一趟 (位号改名 + 板侧同步 + 布局修正 + 布线 45→0 + Gerber 重出) 现在被一个【没人算过的账】卡住** —— 板面 186 个封装 **全是自绘通用占位** (库名全是空字符串), 而 **100 件必装器件连「用哪个封装」都还没定** ⇒ ⇒ 这一趟画出去的板, 等型号定下来还得再改一次 ⇒ ⇒ **板 md5 变第二次** ⇒ ⇒ **本单 = 把「封装真值」这条缺失的基线补出来 (作业包级), 一行板都不碰** ★

★**这不是「再选一次型」** —— 选型另有单 (`HW/PART_SELECTION_MATRIX_2026-11-16.md` / `HW/PART_SELECTION_GAPS_CLOSEOUT.md` / 闸 `HW/check_part_selection_gaps.py`), 它覆盖 22 件 OPN 缺口, 且它自己的口径明写「封装名全是空字符串 ⇒ 一律按裸焊盘占位处理」⇒ ★**它绕开了封装真值, 没有建立封装真值** ⇒ ★**本单做的是它没做的那一层: 每个 ref 的「目标库封装」到底是谁** ★

---

## ① ★main 本机实读的事实 (★2026-11-23 07:3x~07:5x 实跑, 不抄任何 agent 报告★) ★

★**复现方式**: 下面每条都给了一行可重跑的读数命令; ★**你必须自己重跑一遍, 数字与本文不符时以你实读的为准, 并在交卷页写明差异** ★

| # | 事实 | 读数 | 复现命令 |
|---|---|---|---|
| F1 | BOM 总行数 | **218** | `python3 -c "import csv;print(len(list(csv.DictReader(open('HW/BOM_v1.csv')))))"` |
| F2 | 其中 `NET`/`TP` (不需要 OPN 也不需要封装) | **53** (TP 45 + NET 8) | 同上按 `type` 统计 |
| F3 | **真实器件** | **165** (R 67 / C 51 / IC 13 / SW 12 / D 6 / LED 4 / L 3 / CONN 9) | 同上按 `type` 统计 |
| F4 | `footprint` 栏 = `待定` | **129** (R 67 / C 50 / LED 4 / CONN 3 / D 2 / L 2 / SW 1) | 同上按 `footprint` 统计 |
| F5 | `opn` 栏为空 | **123** | 同上按 `opn` 统计 |
| F6 | `opn` = `[0数据]` | **12** | 同上 |
| F7 | 必装且非 NET/TP | **124** | 同上 |
| F8 | ★**必装 且 `footprint` 待定** ★ | ★**100** ★ | 同上 |
| F9 | ★**必装 且 `opn` 空 且 `footprint` 待定** ★ | ★**94** ★ | 同上 |
| F10 | 板面封装 | **186 个, 库名 100% 为空字符串** (`(footprint ""` = 186, 非空 = 0) | `grep -c '(footprint ""' HW/PCB/demo_mainboard.kicad_pcb` |
| F11 | 原理图符号的 `Footprint` 属性 | **218 个里 201 个 = `TBD`** (只有 17 个有值, 且其中 12 个是描述性文字不是库封装名) | `grep -ho '(property "Footprint" "[^"]*"' HW/PCB/demo_mainboard*.kicad_sch \| sort \| uniq -c` |
| F12 | 板生成器怎么画封装 | **全部走自绘 `make_footprint()`**; 只有 SoM 4 座 / 显示 FPC / USB-C / TMP117 四个模块画的是官方风格 land | 读 `state/gen_pcb_netlist_board.py` 的 `make_footprint`, 以及 `state/som_btb_footprint.py` · `state/display_fpc_footprint.py` · `state/usb_c_footprint.py` · `state/tmp117_footprint.py` |
| F13 | KiCad 10 官方封装库在盘 | `/home/yuewuya/kicad/AppDir/share/kicad/footprints/` = **15,777 个 `.pretty` 目录** | `ls /home/yuewuya/kicad/AppDir/share/kicad/footprints/*.pretty \| wc -l` |
| F14 | 关键库封装实测存在 | `Resistor_SMD.pretty/R_0402_1005Metric.kicad_mod` · `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod` · `Capacitor_SMD.pretty/C_0402_1005Metric.kicad_mod` · `Capacitor_SMD.pretty/C_0603_1608Metric.kicad_mod` · `Capacitor_SMD.pretty/C_0805_2012Metric.kicad_mod` · `Diode_SMD.pretty/D_SOD-523.kicad_mod` · `Diode_SMD.pretty/D_SOD-123.kicad_mod` · `LED_SMD.pretty/LED_0805_2012Metric.kicad_mod` · `Button_Switch_SMD.pretty/SW_SPST_TL3342.kicad_mod` · `Inductor_SMD.pretty/L_0805_2012Metric.kicad_mod` **全部在盘** | `ls /home/yuewuya/kicad/AppDir/share/kicad/footprints/<上面的路径>` |
| F15 | 占位封装的焊盘族 (板面实读) | 已被 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6-3 记为 7 族: `('1','2')`×105 · `('1',)`×7 · `('1'..'5')`×6 (6 只 TPS7A20 LDO) · `('1','2','3')`×4 · `('2'..'6')`×2 (`Q1`/`Q2`) · `('1'..'4')`×3 (`U_PWR_SW`/`U_EN_SW`/`J_DEBUG`) · `('4','13','14','15')`×2 | ★**自己重算一遍** (按焊盘编号 + 焊盘尺寸聚类), 与 §9-6-3 不符就在交卷页点名 ★ |
| F16 | 板指纹 (开工前) | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B | `md5sum HW/PCB/demo_mainboard.kicad_pcb` + `stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` |
| F17 | 受保护真源 (开工前) | 网表 `HW/netlist_v1.csv` `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `HW/netlist_v1_pins.csv` `9174309df1ec9411ac8e8d9e80ee386a` · BOM `HW/BOM_v1.csv` `5b9993992405904a60ac96a020b375d8` | `md5sum` 三个文件 |

★**一句话结论 (★main 的判读, 你要验证或推翻它★)**: ★**「板只改一次」的前提不是「布线归零」, 而是「每个必装器件的封装名在画板之前就定死」** ⇒ 现状 = **100 件必装器件没有封装** ⇒ ⇒ **这一趟画出去, 型号一落就得返工** ★

---

## ② 本单要交的东西 (★3 件, 不许扩项★)

### 交付物 1 — `HW/FP_TRUTH_BASELINE.md` (★新建页★)

★**页头必须写死三句**: ① 本页是**封装真值基线** (不是选型页, 不替代 `HW/PART_SELECTION_MATRIX_2026-11-16.md`) ② 本页**零写板** ③ ★**本单不落表**: 真值落到原理图 `Footprint` 属性 / BOM `footprint` 栏 / 生成器, 是**「板那一趟」的活**, 本单只出基线与判据 ★

#### §1 族级映射表 (★核心: 先定族, 再逐 ref 套用★)
★**对 F15 那 7 个占位族, 各给一张「候选真库封装」表**, 每个候选必须写清:

| 栏 | 内容 |
|---|---|
| 族 (焊盘编号 + 板面焊盘尺寸) | ★自己实读 ★ |
| 该族覆盖的 ref (全名单, 不许写「等」) | ★按 type/值/功率/耐压分档 ★ |
| 候选真库封装 `lib:name` | ★**必须在 F13 的库路径下实测存在** ⇒ 给精确相对路径 ★ |
| 焊盘数 / 焊盘网络 对得上吗 | ★沿用 `HW/PART_SELECTION_MATRIX_2026-11-16.md` 的三判据 (焊盘数 / 焊盘网络 / 本体尺寸+land pattern 能否落进现占位 fab bbox) ⇒ **不许新造判据** ★ |
| 分档依据 | ★例: R/C 默认 0402, 电源/大电流 0805/1206, ≥X V 耐压走 Y 系列 —— 每条都要有依据 ★ |
| 证据等级 | `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 五选一 |
| 降级方案 | ★必须项, 不是可选项 (★查不到就写降级: 选官网参数直接满足的替代型号 / 改设计路径绕开 / 实测样件定死★) |

★**这一族表不许出现「待定」「TBD」「待选型」当结论** ⇒ ★**给不出来的, 要么降级方案, 要么写进 §3「删件候选」** ★

#### §2 逐 ref 表 (★100 件必装 + 其余 24 件必装只做核对★)
★**每个 ref 一行**, 栏位: `ref` · `type` · `value` · `必装/DNP` · 现占位族 (焊盘编号 + 尺寸) · **目标 `lib:name`** · 库文件实存路径 + md5 · 焊盘数/网络核对结论 · 候选 OPN (若已有就抄, 没有就写 `[0数据]` + 降级) · 证据等级 · 是否触发布局/布线改动 (改封装 = 焊盘坐标/尺寸变 ⇒ **会**)

★**优先顺序**: ★**先做完 94 件「opn + footprint 双空」的必装件** ⇒ 再补那 6 件「有 opn 无 footprint」的 ⇒ 最后核对已有 footprint 的 24 件 (只写「已一致 / 不一致 + 差在哪」) ★

#### §3 删件候选 (★只给候选与代价, 不代拍★)
★**有些「必装」其实可以不上板** (例: 状态指示灯、测试点、预留跳线) ⇒ ★**逐个给: 删掉它省掉什么封装 / 代价是什么 / 删了会不会改板面 (占位焊盘还在 → 板 md5 变) ★** ⇒ ★**不代拍删不删** ★

#### §4 与既有选型页的关系 (★防重复★)
★**逐条说清**: 选型页已覆盖的 22 件 OPN 缺口 → 本页怎么引用、哪些页里的「封装兼容结论」因为本页的封装真值而**需要修订** (★点名页号/行号, 但**不许改那些页**★) ★

#### §5 对「板那一趟」的影响 (★给 main 的输入, 不代排期★)
★**点名哪些 ref 换封装后必然触发布局/布线改动** (特别是: `Q1`/`Q2` 8 脚 SON · 6 只 TPS7A20 LDO · `U_PWR_SW`/`U_EN_SW` UQFN-4 · 5 个 4 焊盘族 · `J_DEBUG` (已被 ISS-343 的 `B33_PIN_LAND_1P27` 覆盖, 别重复做)) ★

### 交付物 2 — `HW/check_fp_truth_baseline.py` (★新建闸, 自证不是装饰★)
★**判据 (内容级, 不挂 md5 —— 沿用 `HW/check_part_selection_gaps.py` 的做法, 文档改一个字就重判★)**:
- **C1** ★每个「必装 且非 NET/TP 且 footprint 待定」的 ref, ★**必须在 `HW/FP_TRUTH_BASELINE.md` 里出现且带一个目标 `lib:name` 字段 ⇒ 漏一个 = 红 + 点名 ★
- **C2** ★页里写的每个 `lib:name`, ★**对应 `.kicad_mod` 文件必须在 `/home/yuewuya/kicad/AppDir/share/kicad/footprints/` 下实测存在** ⇒ 不存在 = 红 + 点名 ★
- **C3** ★每行必须带非空的「证据等级」且取值 ∈ `[官网]/[实测]/[媒体]/[推算]/[0数据]` 五者之一 (写 `[官方]` = 红) ★
- **C4** ★每行必须带非空的「降级方案」栏 (★查不到的件不许空着 ★)
- **C5** ★页里不许出现「等原厂回信 / 等供应商确认 / 待外部回复」这类挂起措辞 (★老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料★) ⇒ 出现 = 红
- **C6** ★**件数自洽**: 判据自己跑 CSV 统计出「必装 ∩ 非 NET/TP ∩ footprint 待定」的件数 (★不许抄本文的 100★) ⇒ 与页内覆盖件数对不上 = 红

★**`--selftest` 反向用例 ≥5 条, 每条都要自证「红的是目标那一条, 其余仍绿」**: ① 删页里某一行 ⇒ C1 红 ② 把某行的 `lib:name` 改成不存在的 ⇒ C2 红 ③ 清空某行证据等级 ⇒ C3 红 ④ 清空某行降级方案 ⇒ C4 红 ⑤ 正文塞一句「等原厂回信」⇒ C5 红 ⑥ 篡改件数字段 ⇒ C6 红 ★**沙盒必须在 `tmp/` 副本上做, 真件零污染** ★

### 交付物 3 — 分片登记 + 交卷页
- `state/fragments/hw.yaml`: ★**必须走 `state/frag_write.py`** (★禁止 `open(p,"w")`★) ⇒ ≥5 条 `iss356_` 记录 (artifact ×2 + claim ×N + answer/need) ⇒ `grep -c iss356 state/fragments/hw.yaml` ≥ 5
- 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md`: ★**B1~B6 齐全** (★`state/gate_check.py` 按标题关键词判块 ⇒ 六个 `##` 块的标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`★) ⇒ ★**页内引用的每个路径都要在盘 (MISS=0)** ⇒ 占位符 0

---

## ③ 边界 (★违反了就是本单失败★)

- ★**零写板**: 板 md5 + mtime + size 三值开工前后完全一致 (F16) ⇒ **不许碰 `HW/PCB/demo_mainboard.kicad_pcb`**
- ★**零落表 (不许改真源)**: ★**不许改** `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 任何 `*.kicad_sch` / `*.kicad_pro` / `HW/PCB/*.md` 既有页 (★§4 里点名的那些页也不许改★)
- ★**不许跑会重写真件的生成器**: ★`state/gen_bom.py` · `state/gen_pcb_netlist_board.py` · `state/gen_kicad_sch.py` · `state/gen_production_pack.sh` ★**一个都不许跑** (★它们会改网表/脚表/BOM/板/投产包★) ⇒ ★**你要的一切读数都用只读方式自己读**
- ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**外部事实一律自己网上查 + 标证据等级 + 查不到就写降级方案** ⇒ ★**没有「批一句可以发」这个选项** ⇒ ★**只读公开官网页面是可以的 (GET), 不许提交表单/发信/下单** ★
- ★**只写这 4 处**: `HW/FP_TRUTH_BASELINE.md` (新建) · `HW/check_fp_truth_baseline.py` (新建) · `HANDOFF/2026-11-23_hw-lead_ISS356_封装真值基线.md` (新建) · `state/fragments/hw.yaml` (走 `frag_write.py`) · 另可写 `logs/iss356/` 放原始读数
- ★**不许改闸源码** `state/gate_check.py` (★本单闸挂不挂链 = main 地界, 你只交脚本与路径, 在交卷页写明建议★)
- ★**不许改别人的分片** (`pm.yaml` / `sw.yaml` / `mech.yaml` / `state/issue_log.yaml`)
- ★**不代拍**: 删不删件 / 用哪个封装 / 型号定不定 ⇒ **只给候选 + 代价 + 依据**, 拍板留给 main / 老板

---

## ④ 交卷前必跑 (★把原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fp_truth_baseline.py                 # rc=0
python3 HW/check_fp_truth_baseline.py --selftest       # rc=0 (末行 ALL TESTS PASS)
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                             # rc=0 (★Q1 必须 18/18★)
python3 state/frag_write.py --agent hw-lead --show     # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb                 # 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb            # 2026-11-06 07:07:17.362193413 +0800
```

★**`gate_check.py` 的 Q1 掉了先自查是不是你那份交卷页缺块** (★Q1 按每个总工**最新一份**交接单的 B1~B6 计分★) ⇒ ★**别去动别人的交接页** ★

★**如果你这一趟做不完 100 件**: ★**不要假装做完** ⇒ 交卷页写清「已做 / 未做」分界 (★逐 ref 名单★) + 未做部分的续做入口 (★下一步从哪个族开始★) ⇒ ★**宁可交 40 件真件, 不要交 100 件假件** ★

---

## ⑤ ★自证纪律 (★本项目铁律, 别踩★)★

1. ★**数字自己跑, 不抄本文, 不抄别的 agent 报告** ⇒ 与本文 (F1~F17) 不一致 ⇒ **以你实读的为准, 并在交卷页点名差异**
2. ★**引用的每个路径都要在盘** (MISS = 0) ⇒ ★**每条结论都要能指出「哪个文件的哪一行 / 哪条命令的哪个输出」**
3. ★**证据分级**: `[官网]`(厂商官网/官方 datasheet) / `[实测]`(本机可复现) / `[媒体]` / `[推算]` / `[0数据]`(查不到) ⇒ ★**写 `[官方]` 不算数 (白名单只有上面五个)**
4. ★**查不到就写降级方案** (★不是「等回复」★) ⇒ ★**降级方案是必须项**
5. ★**不许在产物上擦, 要修在产生点**: 本单只出基线页 + 闸 ⇒ **不动任何真件** ⇒ 不存在「擦」的机会
6. ★**并发写盘**: 若你发现 `HW/FP_TRUTH_BASELINE.md` 或 `HW/check_fp_truth_baseline.py` 已存在且不是你写的 ⇒ ★**停下, 在交卷页写明「撞车」, 不要覆盖别人的内容**
