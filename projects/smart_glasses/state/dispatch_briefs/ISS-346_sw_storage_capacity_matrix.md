# 【ISS-346 · sw-lead · ★★PCB 线 · 纯分析 + 机器矩阵 · 零写板 ★★】

★**题: 把 Q3「模型/rootfs 怎么存」从 [0数据] 变成【可判矩阵】—— 容量 × 存储 × 板框档 × 板侧动作 ⇒ 判定它对「板那一趟」到底卡不卡** ★

★**派活方 = 项目总工 (main / moli) · 2026-11-22 23:5x · cron fb67af40 (队列自动派活)** ★
★**来源 = 老板拍板页 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行 (need key `q3_storage_and_audio` · 决策码 Q3)** ★
★**性质**: ★**纯分析 + 新建机器矩阵生成器 + 一页决策口径类** ★ ⇒ ★**零写板 · 零改网表/脚表/BOM/原理图 · 零落表 · 零改既有闸 · 零外发 · 不替老板拍板** ★
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 事实 (★main 本机实读, 不抄任何 agent 报告★)

★**① 这张卡现在的字面口径 (main 原文实读 `DECISION_ONE_PAGER_2026-11-22.md` §① 第 6 行) ★**:
- need key = `q3_storage_and_audio` · 决策码 = **Q3** · 一句话题 = 「模型/rootfs 怎么存 (只 ADB push 是否接受外挂 SPI-NOR 16~64 MB · 板宽 12→15 mm) + 音频到底做不做」
- 建议默认值栏 (★**建议·非已决定★**) = 「外挂存储必须赶在板那一趟开工前进网表 (否则板 md5 变第二次) · 音频: tracker 全文无音频条目 ⇒ 建议先不做」
- 卡不卡 = ★**卡 (时限型)** ★ · 证据栏 = 「[官网] 型号参数可自查 · 音频 = [0数据]」

★**② SW 侧盘上已有的东西 (★别重做, 本单是在它上面【收敛】不是【重写】★) ★**:
- `SW/FLASH_AND_VERSION.md` §4.1 = 三方案 (A 全量 eMMC / B 单份+overlay / C 轻量 A/B) · §4.5.1 = 容量算术 ⇒ 分区表总量 **90210304 B** (86 MiB + 32 KiB) ⇒ **64MB SPI-NOR 装不下** ⇒ 真实条件 = 「`rootfs ≤ 30MB` **且** `flash ≥ 128MB`」
- `SW/tools/flash_layout_check.py` = 机器闸 (LAY-01~LAY-08) · 机器可读附件 = `SW/tools/s2_rescue_config.example.json` (★**partition_layout: bootloader 1MB + kernel 8MB + rootfs 30MB + app_a/b 8MB×2 + model_a/b 15MB×2 + isp 1MB + version_block 32KiB · device_total_size = 134217728 (128MB) · align 4096 · partitions 里【没有 offset 键】⇒ 偏移由检查器按序累加★** ★ ⇒ 这些是 **[推算] 占位值, 不是本项目数据** ★
- ★**main 本轮实跑基线 (原样) ★**: `python3 SW/tools/flash_layout_check.py --config SW/tools/s2_rescue_config.example.json --device-size 64MB` ⇒ LAY-01/02/05/06/07 **PASS** · LAY-03/LAY-04 **FAIL** (`最后一个分区 version_block end=90210304 > 设备容量 67108864`) · LAY-08 **PASS** (`rootfs = 30.0MB (<=30MB) → §4.1 条件式推荐 C 成立`)
- ★**模型产物体积 = [实测] 10,575,159 B = 10.09 MiB** (`SW/RKNN_BENCH.md` §3.2.2 · yolov5s INT8 切后处理版) ⇒ ⇒ §4.1 里 **model 槽 15MB 有 4.9MB 余量** (★这条是本项目**少数几个真·实测数**★)
- ★**rootfs 体积本身仍是 [0数据]** (板没做出来) ⇒ `SW-FW-B3` (severity medium) 一直挂着 · ★**所以本单的目标不是【把这个 0 填上】(填不上), 是【让结论不再依赖它】** ★

★**③ ★★本单最关键的那条事实 (main 本机实读网表 + 板面) ★★**:
- `HW/netlist_v1.csv` **L202/L204/L206/L208** = 4 条 SPI 串阻位 (`R_SER_SPI_SCLK` / `R_SER_SPI_CSn` / `R_SER_SPI_MOSI` / `R_SER_SPI_MISO`, 0Ω 调试用, 标 必装) ⇒ 各自接 **`J_BOOT1` pin1..pin4** · 网名 = `SPI_SCLK_BOOT` / `SPI_CSn_BOOT` / `SPI_MOSI_BOOT` / `SPI_MISO_BOOT`
- `HW/netlist_v1.csv` **L209** = `J_BOOT1` pin5 = `VDD_3V3_IO` · 位号类型 `CONN` · **DNP** · ★**note 逐字写明: 「SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展) | 焊盘位 GND 预留 (外挂 SPI-NOR 用)」「pin5/pin6 预留外挂 SPI-NOR 的 3V3/GND」「★V1.1: 容量下限已由 SW 总工锁死 (ISS-080): rootfs ≤30MB · **flash ≥128MB** (64MB SPI-NOR 装不下)」** ★
- `HW/netlist_v1.csv` **L210** = `J_BOOT1` pin6 = `GND` · **DNP**
- ★**板面上 `J_BOOT1` 这个封装【已经存在】** ★ (main 实读 `HW/PCB/demo_mainboard.kicad_pcb:3143` 有 `"Reference" "J_BOOT1"` 属性) ⇒ ★**⇒ SPI-NOR 档 = 焊盘位已在板 ⇒ 板侧【零动作】** ★
- ★**★推论 (★本单要把它算实, 别只信我这一句★) ★★**: 卡面写的「外挂存储必须赶在板那一趟开工前进网表 (否则板 md5 变第二次)」**只在 eMMC 档成立** (eMMC 要占板面 ⇒ 板宽 12→15 mm ⇒ 必须进网表/重出板) ⇒ ★**SPI-NOR 档 (16~64MB) 的板侧代价 = 0 (焊盘位已留) ⇒ 那一档根本不卡这一趟** ★
- ★**板框三候选 (ISS-341 已签收) ⇒ 「板宽 12→15mm」这个代价【只在产品板档成立】★**: `B160x100` = 改现役板一次 (160×100mm 台架板 · 8 铜层 · 1.60mm) · `F30A` 60×30 · `P60×15` ⇒ ⇒ ★**台架板档 = 160mm 宽 ⇒ eMMC 的 25% 板面代价 ≈ 0 ⇒ 连 eMMC 档也不卡这一趟** ★ ⇒ ⇒ **Q3 的「时限型卡」很可能是【分档才成立】, 现在还是【整卡挂着】** ⇒ 本单的作用就是把分档算出来

★**④ 板那一趟的「板只改一次」铁律 (引 `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-1~INV-4) ★**: ★**A 类步 (S1/S2/S3/S4/S6/S7/S8) 必须同趟做完 ⇒ 板 md5 只许变一次 ⇒ 任何【要改网表/改板框】的拍板项, 晚进 = 板 md5 变第二次 ⇒ 那一批 Gerber / 投产包 / 留证链 / 盖章 / 发布全部作废重做** ★

★**⑤ 本机 A7S 那条实测路径当前【不可用】 (main 本轮实读) ★**: `getent hosts radxa-cubie-a7s.local` ⇒ **无解析** · 本机**没有 `sshpass`** ⇒ ⇒ ★**「去 A7S 上量 rootfs」这条路现在走不通 ⇒ 不许把它写成阻塞项 ⇒ 走 §3 的降级方案 (★降级方案是必须项, 不是兜底选项★)★**

★**⑥ 板基线 (零写板自证用) ★**: `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` · 4940213 B

---

## §1 本单范围 (★4 件交付物, 不许扩★)

★**交卷物 (4 件)** ★

1. ★**新建★ `SW/STORAGE_CAPACITY_MATRIX.md` (★一页: 矩阵 + 区间 + 零代价路径 + 时点结论★) — 详见 §2
2. ★**新建★ `SW/tools/gen_storage_capacity_matrix.py` (★机器生成器: 改副本配置 + 逐格跑布局检查器 + 出表★) — 详见 §3
3. ★**新建★ `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md` (★交卷页 B0~B7 七块齐全★) — 详见 §5
4. ★**登记★ `state/fragments/sw.yaml` (★只走 `python3 state/frag_write.py --agent sw-lead`★ · 零重复 key★) + 原始输出落 `logs/iss346/` — 详见 §4

★**不许碰的东西 (★越界 = 交卷不算数★)★**: ★**板 `HW/PCB/demo_mainboard.kicad_pcb` (零写板) · `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 原理图 (零落表) · `SW/tools/flash_layout_check.py` / `SW/tools/s2_rescue_config.example.json` / `SW/FLASH_AND_VERSION.md` (★**只读, 一字不许改**★) · `state/fragments/pm.yaml` / `hw.yaml` / `mech.yaml` (零写别人的分片) · `state/issue_log.yaml` (★main 的派单记录, 不许自己改★) · `DECISION_ONE_PAGER_2026-11-22.md` (★main 的地界★)★**

---

## §2 D1 · `SW/STORAGE_CAPACITY_MATRIX.md` (★一页, 5 段, 不许超★)

★**① 容量 × 存储 可判矩阵 (★每格必须贴机器输出, 不许手写结论★) ★**
- 行 = rootfs ∈ {20, 30, 40, 64, 128} MB · 列 = 存储 ∈ {64MB NOR, 128MB NOR, 256MB NOR, 8GB eMMC}
- 每格写四件事: ①**装不装得下** §4.1 推荐 C 的分区表 (LAY-03 口径) ②**app/model A/B 槽要不要缩** ③**是不是必须 eMMC** ④**板侧后果** (eMMC ⇒ 占板面 ⇒ 板宽 12→15mm ⇒ 只在产品板档成立)
- ★**每格的判据来自 §3 的生成器实跑输出 (LAY-03/LAY-08 两行 + 一句人话结论) ⇒ 不许抄 `SW/FLASH_AND_VERSION.md` 的旧结论★**

★**② rootfs 体积的可判区间 (★本单的核心洞察: 结论不依赖那个 0 数据★) ★**
- 下界 = ARS45 **必须携带**的最小集合: kernel + bootloader + isp + app 槽 + **model [实测] 10.09 MiB** ⇒ ⇒ 给出「rootfs ∈ [下界, 90MB] 区间」
- ★**逐字写清: rootfs 的真值仍 [0数据] (板没做出来) · 但本矩阵【每一格的结论都不依赖真值】—— 真值落在哪一格就按那一格办** ★ ⇒ ⇒ **这就是本单的降级方案 (查不到 ⇒ 给可判区间 + 逐格结论)**
- ★**不许把 A7S 那台板 (Allwinner A733, Debian trixie) 的数冒充实测真值** ★ ⇒ A7S 路径当前不可用 (§0⑤) ⇒ **就算后来能连上, 也只能当 [实测]-代理下界, 必须标明被测对象不是 ARS45 板**

★**③ 零代价可执行路径 (★必须写成一等选项★) ★**
- 「demo 阶段只 ADB push, 不外挂存储」⇒ **板侧零动作** (网表/板面不动) ⇒ ⇒ Q3 **不卡这一趟**
- ★**代价必须写清 (不许只写好处★)**: 无 S2 救砖 / 无 A/B 回滚 ⇒ 只能重刷 ⇒ 引 `SW/FLASH_AND_VERSION.md` §4.1 方案 B 的降级口径
- ★**这给了老板一个【零代价选项】⇒ 本单的交卷页要让 main 能把 Q3 从「时限型卡」正确分档, 而不是继续整卡挂着** ★

★**④ 时点结论 (★含板框依赖★) ★**
- 若最终要外挂**存储** ⇒ 进网表的时点 = **板那一趟开工前** (引 §0④ 的 INV-1~INV-4 + 晚进的代价)
- ★**但分档**: 台架板档 (`B160x100`, 160×100mm) ⇒ eMMC/SPI-NOR 的板面代价 ≈ 0 ⇒ **时点压力从「时限型」降为「建议型」** ⇒ 产品板档 (60×30 / 60×15) ⇒ eMMC 档才真卡 (板宽 12→15mm) ⇒ 而 **SPI-NOR 档因为 `J_BOOT1` 焊盘位已在板 ⇒ 两档都不卡**
- ★**结论要标 [推算] 并把依据逐条列出来 (依据 = §0③ 的网表/板面事实 + ISS-341 的三候选判决) ⇒ 不许标 [实测]** ★

★**⑤ Q3 的两轴拆分 (★音频轴本单【不做】★) ★**
- 存储轴 = 本单做的; 音频轴 = ★**本单不碰** ★ ⇒ 只登记一条: ★**「音频轴与存储轴互不依赖 (存储轴的任何结论都不受音频决策影响)」** ★
- 音频本身 = [0数据] (tracker 全文无音频条目) ⇒ 建议先不做 ⇒ ★**这是 main 拍板页上的原话, 本单不替老板拍, 也不改拍板页** ★

---

## §3 D2 · `SW/tools/gen_storage_capacity_matrix.py` (★机器生成器 ★)

★**必须做到 (逐条) ★**
1. ★**只读** `SW/tools/s2_rescue_config.example.json` ⇒ ★**不许改那个文件** ★ ⇒ 把副本写到项目内 `tmp/iss346/` 下再改 (★TMPDIR 指项目内, 与 SW 侧既有习惯一致★)
2. 逐格只改副本里的 `partition_layout.partitions[*].size` (rootfs / model_a / model_b) ⇒ ★**不要手写 offset 键** ★ ⇒ 实测: `partitions` 里【没有 offset 键】⇒ 检查器按序累加并按 `align=4096` 对齐 (★这是 main 本轮实读配置得出的事实, 你也要自己核一遍★)
3. 逐格调 `python3 SW/tools/flash_layout_check.py --config <副本> --device-size <N>MB` ⇒ ★**收 LAY-03 (装不装得下) 与 LAY-08 (rootfs 分档) 两行结论** ⇒ `--json` 输出可留档
4. ★**不许改 `SW/tools/flash_layout_check.py`** (受保护件) ⇒ 若某格跑不出来 (例如 >256MB 边界) ⇒ ★**写清失败原因, 不许编一个结论** ★
5. 裸跑 rc=0 ⇒ 把矩阵与逐格原始输出写进 `logs/iss346/` (★**机器输出要能被别人复算**★)

★**降级路径 (★必须写进脚本注释/交卷页, 不许只写成功路径★) ★**: 若矩阵生成器某步失败 ⇒ 至少交出「可手工复算的单格命令 + 已跑通的格 + 失败原因」⇒ ★**不许交一张没有机器输出的手写表** ★

---

## §4 D4 · 分片登记 + 原始输出 (★`state/fragments/sw.yaml`, 只走 frag_write★)

★**登记 1 条 answer + 1 条 need + 2~3 条 artifact (★零重复 key★) ★**
- answer: key = `iss346_storage_capacity_matrix` · value = 矩阵结论 + 「Q3 对台架板档不卡 / 对产品板档 eMMC 档卡」的分档结论 + 零代价路径 + 证据等级
- need: to = **main** · item = 「板侧输入: 若选 SPI-NOR ⇒ `J_BOOT1` 焊盘位【已在板】⇒ 板侧零动作; 若选 eMMC ⇒ 产品板档板宽 12→15mm ⇒ 必须在这一趟开工前进网表」★**并附一条订正提示: sw.yaml 里 `iss338_need_boot_storage_answer` 写的是「3 条 SPI_*_BOOT」, 本单实读网表是【4 条】(SCLK/CSn/MOSI/MISO) 且焊盘位已在板 ⇒ 该 need 措辞需订正 —— ★**订正交 main 改, 你不许自己改真源**★** ★
- artifact: `SW/STORAGE_CAPACITY_MATRIX.md` · `SW/tools/gen_storage_capacity_matrix.py` · 交卷页

★**不许写 `state/fragments/pm.yaml` / `hw.yaml` / `mech.yaml` (★那是 main 和别的总工的地界★)★**

---

## §5 交卷页 `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md` (★B0~B7 七块齐全★)

- **B0** = 一句话结论 (★Q3 存储轴到底卡不卡, 分档说★)
- **B1** = 事实基线 (★本轮实跑的命令 + 原样输出: 布局检查器基线 / 网表 L202~L210 原文 / 板面 `J_BOOT1` 的读板结果★)
- **B2** = 容量 × 存储 矩阵 (★5×4, 每格带机器输出★)
- **B3** = rootfs 可判区间 + 降级方案 (★真值仍 [0数据], 但结论不依赖它★)
- **B4** = 零代价可执行路径 (★只 ADB push ⇒ 板侧零动作 + 它的代价★)
- **B5** = 时点结论 + 板框依赖 (★台架板档 vs 产品板档★)
- **B6** = 边界自证 (★板 md5 前后一致 + 受保护件未动 + 引用零假引用 + 必跑项输出★)
- **B7** = 交 main 的 3 条 (★不替老板拍: ①Q3 分档结论怎么写回拍板页 ②`iss338_need_boot_storage_answer` 的措辞订正 ③音频轴只登记「互不依赖」这一条★)

★**★先落盘, 后探查 (★本项目的死法都在这★)★★**: ★**第一个工具调用就把 D1 / D2 / 交卷页的骨架文件 write 出来 (每块一行标题 + 一行说明), 再逐块填内容** ★ ⇒ 断线时盘上也有半成品, 不许空手死。

---

## §6 边界自证 (★交卷时把输出原样贴进 §B6 + 回复★)

1. ★**零写板**: `md5sum HW/PCB/demo_mainboard.kicad_pcb` 开工前/交卷后 = `611b869e13518c3c023fb178f91a0075` · mtime 仍 = `2026-11-06 07:07:17.362193413` ★
2. ★**必跑项 (★rc 必须对★) ★**:
   - `python3 SW/tools/flash_layout_check.py --config SW/tools/s2_rescue_config.example.json --device-size 64MB` (基线复现 ⇒ LAY-03/04 FAIL 是【预期值】, 不是你的锅)
   - `python3 SW/tools/gen_storage_capacity_matrix.py` (★新建★ · 裸跑 rc=0)
   - `python3 state/merge.py` (★rc 必须 0★)
   - `python3 state/gate_check.py` (★Q1 必须 18/18★)
   - `python3 state/frag_write.py --agent sw-lead --show` (★登记命中数★)
3. ★**引用零假引用**: 交卷页里引用的每个文件必须逐个在盘 ⇒ 交卷前自检一次
4. ★**证据分级**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 逐条标 ★**实测必须写明被测对象 (哪块板/哪个文件/哪条命令)****

---

## §7 纪律 (★每条都要守★)

1. ★**写分片必须用 `python3 state/frag_write.py --agent sw-lead`** (★禁止 `open(p,"w")` 直接改 `state/fragments/sw.yaml`★)
2. ★**只写本任务允许的文件** (D1 / D2 / 交卷页 / `logs/iss346/` / `tmp/iss346/` / `state/fragments/sw.yaml`) ⇒ 不碰别人的
3. ★**证据分级必须标** (见 §6-4)
4. ★**★不许外发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)** ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ ⇒ ★**查型号参数 (e.g. 各家 SPI-NOR / eMMC 容量型号) 自己上网查 [官网], 不许发信问人** ★
5. ★**不许把外部依赖挂着当阻塞项** (★A7S 不可达 / 原厂没回信 ⇒ 一律换成【自己查的结果 + 证据等级 + 查不到就写降级方案】★)
6. ★**不替老板拍 Q3** ⇒ 只给选项 + 代价 + 判据
7. ★**回复 ≤ 400 字 + 6 行读数 (`MATRIX_RC` / `MERGE_RC` / `GATE_Q1` / `FRAG_ISS346_HITS` / `BOARD_MD5` / `LAY03_BASELINE`)**

★**最后一句 (★本单最容易死的地方★)**: ★**这个单子最容易死成「查不到 rootfs ⇒ 交一份 [0数据] 报告」** ★ ⇒ ★**交卷的合格形态是【结论不依赖那个 0 数据】—— 区间 + 逐格结论 + 零代价路径 + 时点分档★**
