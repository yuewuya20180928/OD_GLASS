# ISS-385 · sw-lead · EVT `PWR-05` 充电电流判据与现行 `R_ILIM` 体系【不相容】的机器可判定化 (★纯分析 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸 · 零外发 · 不代拍★)

★**本单 = 纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 为什么开这个单 (★main 2026-11-24 08:3x 本机实读 + 实算 · 不抄任何 agent 报告★) ★★

★① `python3 state/advance.py --json` 实跑 (2026-11-24 08:1x) ⇒ ★**`internal: []`** ⇒ 三个总工名下零 open 可派 ⇒ ★**但台账实读: sw-lead `open 0` / `fixing 0` / `verified 77`** ⇒ ★**sw-lead 槽位真空 ⇒ 队列对 SW 这条线真断线** ★

★② ★**本单的触发源 = `state/fragments/mech.yaml` 里一条【一直没人答】的 need** (★`iss229_mech_sw_evt_pwr05_charge_current_criterion` · ★`since: 2026-11-16` · ★`due: 2026-11-19` · ★**已逾期 5 天**★): ★**mech-lead 当时只报不改, 原文写明「只报不改, SW 地界由 sw-lead 自己改」** ★ ⇒ ★**它至今没被 SW 侧接走** ★

★③ ★**它报的是什么 (main 本机实读, 一字不抄)**: ★**`SW/EVT_TEMPLATE.md` 的 `PWR-05` 写「充电电流 ≥ 1.5A @5V/2A 适配器」, 但它与现行 R_ILIM 体系不相容** ★ ⇒ ★**main 本机实读 `SW/EVT_TEMPLATE.md` L131 原文逐字**: ★**`| PWR-05 | 充电检测与充电电流 | 插 Type-C 后 `charging_state=1` (寄存器回读), 充电电流 ≥ 1.5A @5V/2A 适配器, 电池电压 10min 内上升 ≥ 0.1V, SOC 上报单调不减 |`** ★

★④ ★**为什么它【不相容】(★main 本机实读 `MECH/hinge_power_calc.json` 的 `rilim_table` 逐档算出来的·不是抄文档★)**: ★**现行 `R_ILIM` = 680Ω (V-4 裁定 2026-11-16, 已落表)** ⇒ ★**电池侧充电电流 `ICHG` max = 0.697A** ⇒ ★**★1.5A 这条线在【电池侧电流】口径下【永远达不到】(差 2.15×)★** ⇒ ★**输入侧 `IINMAX` max = 0.574A** ⇒ ★**★1.5A 在【输入电流】口径下【也达不到】(差 2.61×)★** ⇒ ★**★⇒ 【无论 PWR-05 量的是哪个量, 它按现值都是一条【永远判不过】的判据★** ★

★⑤ ★**而且这条不兼容【在旧 0.822 系数下就已存在】** (★390Ω max = 0.822A, 离 1.5A 更远★) ⇒ ★**★它【不是】ISS-229 造成的, 是一个【既存判据】★** ⇒ ★**这正是本单要登记的「既存缺陷」事实**

★⑥ ★**main 本机实读出的【另一条硬事实】(★决定本单能不能做·★很关键★)**: ★**`SW/EVT_TEMPLATE.md` 全文只有 L131 这一处提充电电流** ⇒ ★**所以这是一个【单点判据】, 不是一个散落各处的问题** ⇒ ★**⇒ 处置面很小, 但【改之前必须先把「它量哪个量」这件事定下来】** ★

★⑦ ★**main 本机实读出的【一个不能忽略的前提】**: ★**`U_CHG` (BQ25896) 与 `R_ILIM` 在网表里的 `board` 域全是 `CHG_BOARD` (★main 实读: `R_ILIM` 2 行 `board=CHG_BOARD`·`U_CHG` 8 行 `CHG_BOARD`·**没有一行 board=MAIN_PCB**★)** ⇒ ★**★⇒ PWR-05 在【demo 主 PCB】这一趟到底【适不适用】, 是一个【必须先答的前置问题】★★** ⇒ ★**★不许你直接改判据数字; ★**你必须先答「PWR-05 在 demo 板上量的是哪个量 / 适用不适用」, 再给改法★ ★★**

★⑧ ★**本单【不重复谁】**: ★**ISS-229 (mech-lead) 已 verified** ⇒ ★**改正系数那本权威表只读·不改** ★ · ★**ISS-234 (sw-lead) 已 verified** ⇒ ★**它的交付物是【真断电 vs 深睡关机 × demo 板 vs 整机】两套方案 + 负载开关选型判据, 【不含 PWR-05 判据本身】** ★ · ★**ISS-214 (已 verified) 的标题里虽含 ICHG 字样, 但 main 本机实读它的 title/desc: 【不含 `PWR-05`、不含 `EVT_TEMPLATE`】⇒ ★**零重叠** ★ · ★**ISS-381 (sw-lead) 已 verified** ⇒ ★**它做的是【布线验收线零假连通闸】(板面拓扑), 与本单的【充电电流判据】零交集** ★

---

## ★★二 · 你要回答的问题 (★mech-lead 那条 need 的原意, main 本机实读转述·★不代裁★) ★★

★**need 原文 (main 实读节选)**: ★**「请 sw-lead 复核它到底量哪个量 (输入电流 vs 电池侧电流), 并给改法 (降阈值 / 改判据对象 / 或注明 demo 板不装充电链故本项不适用 — charge IC 在 demo 板是 DNP 位)」** ★

★**★所以本单要交的是【一个判定 + 一套改法候选】, 不是【一个数字】★★** ⇒ ★**★三个必答项 (★逐条都要有机器判据支撑, 不许写「建议改成 X」了事★)★★**:

| # | 必答项 | ★判据要求★ |
|---|---|---|
| **Q1** | ★**PWR-05 的「充电电流」量的是哪个量? 充电输入电流 `IIN` 还是电池侧充电电流 `ICHG`?** | ★**给出证据 (★哪一行/哪张表推出这个读法★) + ★**★两个量在现行 680Ω 档下的真值 (main 已算出: `IINMAX` max 0.574A / `ICHG` max 0.697A★) ⇒ ★**无论哪个读法, 1.5A 都达不到 ⇒ 结论对两个量都成立★ ★** ⇒ ★**★所以本单【不必】先赌对读法也能判「1.5A 这条线不可达」★** ★ |
| **Q2** | ★**1.5A 这条线在现行硬件上【不可达】(差 2.15× / 2.61×) ⇒ 判据怎么改?** | ★**给三个候选 (★逐条写清代价 + 谁来定★)**: ★**甲 = 降阈值到硬件真值附近 (按 Q1 选定的量) + 注明这是【680Ω 档的硬件上限】** · ★**乙 = 改判据对象 (★例如改成「≥ 0.5A (0.349A×1.43× 余量内)」或改成【结构侧余量】口径·★你给候选不代拍★)** · ★**丙 = 注明本项在 demo 板上【不适用】(理由 = `U_CHG`/`R_ILIM` 的 `board` 域是 `CHG_BOARD`)** ⇒ ★**★三个候选的【代价】都要写, 哪个都不许默认选★ ★** |
| **Q3** | ★**这条判据【是不是这次才坏掉的】?** | ★**★明确写: 「该不兼容在旧 0.822 系数下就已存在 (390Ω max = 0.822A, 离 1.5A 更远) ⇒ ★**属既存判据, 不是 ISS-229 造成**」★ ⇒ ★**这一条是本单的事实分账核心 (★不许把它算到别人头上, 也不许把它藏起来★)** ★ |

★**★Q2-丙 那条你要自己实读确认 (★main 已给了指针, ★你必须复跑一遍★)★★**: ★**`HW/netlist_v1.csv` 里 `U_CHG` / `R_ILIM` 的 `board` 域** ★
```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 - <<'PY'
import csv
r=list(csv.DictReader(open('HW/netlist_v1.csv')))
for x in r:
    if x.get('ref') in ('U_CHG','R_ILIM'):
        print(x.get('ref'),'| board=',x.get('board'),'| dnp=',x.get('dnp'))
PY
```
★**main 本机实跑结果: `R_ILIM` 2 行 `board=CHG_BOARD` · `U_CHG` 8 行 `board=CHG_BOARD` · ★**没有一行 `board=MAIN_PCB`**★ ⇒ ★**⇒ PWR-05 若按字面在 demo 主 PCB 上测, ★**测的是一条【demo 板上不存在的链路】★** ⇒ ★**★这正是 Q2-丙 那个候选的机器依据★★ ★**

---

## ★★三 · 权威源 (★只读·已签收·你只许引用不许改★) ★★

| 事实 | 权威出处 | main 本机实读值 |
|---|---|---|
| ★**改正系数与方向修正** ★ | `MECH/HINGE_POWER_CALC.md` L14~L20 + `MECH/hinge_power_calc.json` 的 `rilim_table` | ★**`ICHG = η·(VBUS/VBAT)·IIN` = `1.216` @3.70V / `1.071` @4.20V; 旧 `0.822` 是它的倒数 (方向反了)** ★ |
| ★**680Ω 档真值 (max)** ★ | 同上 (`rilim_table`) | ★**`IINMAX` 0.5735A · `ICHG` 0.6974A · 单 pin 0.3487A · 余量 1.43×** ★ |
| ★**390Ω 档真值 (max)** ★ | 同上 | ★**`IINMAX` 1.0A · `ICHG` 1.216A · 单 pin 0.608A** ★ ⇒ ★**旧系数下 390Ω max 的 ICHG = 0.822A ⇒ 离 1.5A 更远 ⇒ 既存判据** ★ |
| ★**网表真值 `R_ILIM` = 680Ω (V-4 裁定)** ★ | `HW/netlist_v1.csv` L47/L48 + `HW/BOM_v1.csv` | ★**680Ω · 必装** ★ |
| ★**EVT 判据原文** ★ | `SW/EVT_TEMPLATE.md` L131 | ★**「充电电流 ≥ 1.5A @5V/2A 适配器」** ★ |
| ★**EVT 模板的归属与用途** ★ | `SW/EVT_TEMPLATE.md` L1~L8 | ★**「归属: 软件总工 sw-lead · 2026-10-25 · v1.0」·「阶段门 G3 (上电联调 + 硬指标实测) = EVT」** ★ |

★**复现命令 (main 本机跑过, rc=0)**:
```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/hinge_power_calc.py --json      # rc=0  权威表重新生成 ⇒ 你自己复算 IINMAX / ICHG
```

---

## ★★四 · 你要交什么 (★交卷物 4 件 · 逐字可执行·不许含糊★) ★★

★**★★① ★新建★ `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` — 一页说清「PWR-05 充电电流判据口径」** ★★
- §0 一句话结论: ★**「PWR-05 的『充电电流 ≥ 1.5A』在现行 R_ILIM=680Ω 档下【两个口径都达不到】(IIN 0.574A / ICHG 0.697A); 且 `U_CHG`/`R_ILIM` 的 board 域是 CHG_BOARD, demo 主 PCB 上无此链路; 该不兼容在旧 0.822 系数下已存在 ⇒ 属既存判据」** ★
- §1 ★**Q1 答: 它量哪个量** ⇒ ★**给出你的读法判定 + 证据行号 + ★**并列出【两个量都达不到 1.5A】这个【与读法无关】的结论 (★这样即使读法判错, 结论仍成立★)★** ★
- §2 ★**Q2 答: 三个改法候选 (甲/乙/丙) 逐条给【判据具体写法 + 代价 + 谁来定】** ⇒ ★**★不许代拍: 你只把三个候选摆清楚, 「选哪个」是 main/老板的地界★ ★** ★
- §3 ★**Q3 答: 既存判据的事实分账 (★含 390Ω 旧系数下的 0.822A 对照数·★证明不是本次造成★)** ★
- §4 ★**判据口径表**: ★**逐条给「判据现在长什么样 → 建议改成长什么样 → 改完的机械判读法」** ★ ⇒ ★**★机械判读法必须可执行 (★例: 「`charging_state==1` 且 `ICHG ≥ 0.60A` 且 10min 电池电压升 ≥ 0.02V」★ —— ★**具体数值你按 §三 的真值自己算, ★不许照抄本任务书★)** ★
- §5 ★**证据分级表**: ★**每行标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ⇒ ★**本单主体 = `[实测]` (本机实读文件 + 实跑 `MECH/hinge_power_calc.py` + 实读网表 board 域)** ★
- §6 ★**未决项**: ★**★「选哪个改法」这一条要写进 `needs_from` 给 main (★它是 main 地界★), 不许自己拍★** ★
- ★★**机器块**: ★**一行 `evt_pwr05_caliber:` + `ri_ohm` / `iinmax_max_a` / `ichg_max_a` / `per_pin_max_a` / `current_criterion_a` (★你定的那个数★) / `criterion_source` (量哪个量) / `applicable_on_demo_main_pcb` (★布尔·你实读 board 域得出的★)** ★★ ⇒ ★**格式照 `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` 的机器块写法 (★自己先读那份页怎么写的★)**

★**★★② ★新建★ `SW/check_evt_charge_current_criterion.py` — 新闸 (★本单【不许改既有闸】·只新建★)** ★★
- ★**它要抓什么**: ★**读 `SW/EVT_TEMPLATE.md` 的 `PWR-05` 行, 与权威真值 (`MECH/hinge_power_calc.json` 的 `rilim_table` + 网表 `R_ILIM` 的 `board` 域) 对账 ⇒ 若判据里的阈值【高于硬件真值】⇒ 红并点名 (★「PWR-05 要求 ≥ X A, 硬件真值只有 Y A ⇒ 永远判不过」★)** ★
- ★**★它【不许】误伤 (★本闸最容易写错的地方★)★★**: ★**★① 它【不许】改 `SW/EVT_TEMPLATE.md` 的正文★ ⇒ ★**「改判据」是 main 的地界, 你只交页 + 闸; 闸必须认【当前页上的判据】并如实报红, ★**不许为了让闸绿而私自把页改成另一个数**★** ⇒ ★**★② 反向用例必须含: 「把 PWR-05 的阈值改成 0.01A ⇒ 闸必须变红 (因为它不再是本文给的『硬件上限口径』)」或等价的【口径被换掉就红】判据★ ★** ⇒ ★**★③ 判据要按【语义】判 (★「≥ 1.5A」是【上限要求】还是【设计点】?), 不许按【子串】判★ ⇒ ★★**这一条是本闸的命门 (★字符串匹配会把判据改写后仍判绿★)★★ ★**
- ★**判据清单 (自己定, 但至少要有这几条)**: ★**① 阈值必须 ≤ 硬件真值 (否则永远判不过) ② 判据里若出现 ≥1.5A 而真值只有 0.697A ⇒ 红并点名 ③ 判据必须声明它量哪个量 (`IIN` 还是 `ICHG`) ④ `applicable_on_demo_main_pcb` 与网表 `board` 域一致 (网表说 CHG_BOARD ⇒ 判据必须注明不适用或改判据对象) ⑤ 证据等级标注齐全 ⑥ 零挂链** ★
- ★**★`--selftest` 至少 8 条反向用例**: ★**每条 = 「把判据/页/真值改成坏的样子 ⇒ 闸必须 rc=1 且点名」** ⇒ ★**末行必须打印 `ALL TESTS PASS`** ★
- ★**★零挂链**: ★**闸写好 + 自测过即可, ★**不许**把它挂进 `state/gate_check.py` (★挂链是 main 的地界·★先例同款★)★ ⇒ ★**页里要写明「本闸零挂链」+ `grep -c check_evt_charge_current_criterion state/gate_check.py` = 0 的实测** ★

★**★★③ 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS385_EVT充电电流判据口径核对与机器闸.md` (★新建★) · B1~B6 齐全** ★★
- ★**B1 结论摘要 · B2 验收标准自评 (逐条 通过/不通过/未验) · B3 证据分级 · B4 接口取值声明 · B5 未决项与卡点 (需要谁回答什么) · B6 自证复现命令** ★
- ★**B2 必须逐条判**: ★**Q1/Q2/Q3 三问是否都答了 (逐条判, 不许写「已全部说明」) · ★**Q2-丙 的 board 域结论是否【自己实读】过 (不许抄本任务书) · 网表/脚表/BOM md5 前后逐字相同 (零落表) · 板三项指纹逐字相同 (零写板) · `SW/EVT_TEMPLATE.md` 正文 md5 前后逐字相同 (★你【不许】改它★) · 新闸裸跑 rc=0 · 新闸 `--selftest` 末行 ALL TESTS PASS · `grep -c check_evt_charge_current_criterion state/gate_check.py` = 0** ★

★**★★④ 分片 `state/fragments/sw.yaml` (★只走 `state/frag_write.py`★)** ★★
- ★**产出物 3 条** (★真相页 + 新闸 + 交卷页★) · ★**`interface_claims` ≥ 4 条** (★逐条写清: PWR-05 量哪个量 / 硬件真值两数 / 不可达倍数 / 适用性判定·★每条带出处行号★) · ★**`needs_from` 里写「谁要答什么」** ⇒ ★**★不许把没查到的东西写成「等原厂回信」★ ⇒ ★**查不到 ⇒ `[0数据]` + 降级方案** ★

---

## ★★五 · 必跑命令 (★rc 实测·★全部真实存在·★main 本机跑过★) ★★

```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/hinge_power_calc.py --json                  # rc=0  权威表重新生成 ⇒ 复算 IINMAX / ICHG
python3 SW/check_evt_charge_current_criterion.py         # rc=0  新闸裸跑 (★新建·交卷时才存在★)
python3 SW/check_evt_charge_current_criterion.py --selftest  # rc=0  末行 ALL TESTS PASS (★新建★)
python3 SW/tools/s2_board_judge.py --selftest            # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 state/merge.py                                   # rc=0
python3 state/gate_check.py                              # rc=0  【Q1 18/18】
python3 state/check_brief_commands.py                     # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv SW/EVT_TEMPLATE.md SW/tools/s2_board_judge.py
grep -c check_evt_charge_current_criterion state/gate_check.py   # ★必须 = 0 (零挂链)
```

★**★基线 (★main 本机实跑·★交卷后必须逐字相同·★别把别人的红当成你的★)★★: ★**`python3 SW/tools/s2_board_judge.py --selftest` rc=0** ★ · ★**`python3 SW/tools/s2_board_judge.py` (★不带 `--selftest`·★它要 `--evidence-dir`) rc=3** ★ ⇒ ★**★注意: 不带 `--selftest` 跑它 rc=3 是【它自己要的参数没给】, 不是你的锅; ★**判据基线用 `--selftest` 那条 (rc=0)**** ★ · ★**`python3 SW/tools/s2_board_selftest.py` rc=2 (★【基线】·★交卷后必须逐字相同★)** ★ · ★**`python3 state/gate_check.py` rc=0 (Q1 18/18)** ★

★**★板指纹 (★零写板·★开工前后各打一次·★纳秒级比★)★★**: ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★

---

## ★★六 · 边界 (★一个字节都不许越★) ★★

★**① 零写板** ⇒ ★**`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` 逐字节不变 (★三项指纹开工前后各打一次★)** ★
★**② 零落表** ⇒ ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 逐字节不变** ★
★**★★③ 零改既有页面正文 (★本单最容易越界的一条·★盯死★)★★** ⇒ ★**★`SW/EVT_TEMPLATE.md` 的正文【一个字都不许改】★** ⇒ ★**★判据的【建议改法】只写进你的新页 + 交卷页; ★**要不要改 EVT_TEMPLATE 是 main 的地界**★** ⇒ ★**★为什么: 判据一改, EVT 模板的版本 (v1.0) + §0.4 判据来源表 + 七段判定矩阵 (L79~L119) 都得跟着动, ★**那是「改板那一趟」同批的事, 不是本单★ ⇒ ★**★提前单独改 = 中间态 = 制造 churn (★同款先例: ISS-379 Q9 / ISS-381 的 correction block 都是「与那一趟同批落」★)★** ★
★**④ 零改既有闸** ⇒ ★**`SW/tools/s2_board_judge.py` / `SW/tools/s2_board_selftest.py` md5 逐字节不变 (★★R10/§11.2 那些判据只许在新闸里另写一份, 不许改它的判据表★)★** ★
★**⑤ 零写 MECH / HW 地界** ⇒ ★**`MECH/HINGE_POWER_CALC.md` + `MECH/hinge_power_calc.json` + `HW/netlist_v1.csv` 只读** ★
★**⑥ 零外发** ⇒ ★**★不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有「批一句可以发」这个选项**★ ★**
★**⑦ 不代拍** ⇒ ★**★「PWR-05 最终改成哪一条」是 main/老板的地界; ★**你只把三个候选 + 各自的代价摆清楚 + 写进 `needs_from` 给 main**★ ⇒ ★**★「选哪个」不许你在页里写死★ ★**
★**⑧ 不自签 `state/issue_log.yaml`** ⇒ ★**签收归 main** ★
★**⑨ 只写本任务允许的文件** ⇒ ★**别写别人的分片 (`state/fragments/mech.yaml` / `hw.yaml` / `pm.yaml` 一个字节都不许动)** ★
★**⑩ 沙盒** ⇒ ★**只落 `tmp/iss385_sbx/` + `logs/iss385/`; ★**不许用 `cp -al` (★本项目吃过硬链接的亏★)** ★

---

## ★★七 · 交卷前的最后一道 (★按顺序做·★每件落盘后再做下一件★) ★★

★**① 先落真相页骨架** (★空壳也要先落盘·★宁可先落骨架再填★) ★**② 再落新闸 + 跑通 `--selftest`** ★**③ 再回头填真相页 + 跑闸** ★**④ 再落交卷页 (B1~B6)** ★**⑤ 最后写分片** ★**⑥ 跑 `python3 state/merge.py` (rc=0) + `python3 state/gate_check.py` (rc=0, Q1 18/18) + 把两行输出原样贴进回复** ★

★**★最后提醒 (★项目硬规矩 L-13★)★**: ★**你的第一个动作就是把那两份新文件 (真相页 + 新闸) 的骨架写出来落盘, 不许「想清楚了再一次性写」** ⇒ ★**本项目的墙在 12~16 分钟, 攒着写 = 零交卷** ★
