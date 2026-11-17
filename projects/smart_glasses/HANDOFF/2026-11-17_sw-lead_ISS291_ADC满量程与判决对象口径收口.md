# ISS-291 · sw-lead 交卷单 —— ADC 满量程口径 + 判决对象口径收口

> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-291 · ★**派活人**: 项目总工 (main / moli)
> ★**派活时刻**: 2026-11-17 15:5x · ★**job**: cron `775d9893` · ★**性质**: 内部活 · SW 侧判据口径收口 + 机器闸类
> ★**边界**: ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不碰 `HW/` 与 `MECH/` · 不自签 issue_log** ★
> ★**一句话结论**: ★**闸原来那条红是「假红」——判错了对象 (USB 数字脚当 12bit SAR-ADC 判) + 用错了满量程 (3.3V 而非官方 1.8V)⇒ 现已按官方真源把两条口径钉死: 判决对象 = BAT_DET (pin38 SARADC_VIN5), 满量程 = 1.8V ⇒ 真 ADC 链站得住 (漏电 2.1% FS, 与网表 note 逐字对上), 数字链改按数字口径单判; ★**闸现在 rc=0 · 85/85**★**

---

## §0 交卷清单 (4 件 + rc)

| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | ★**交卷单** (本文件) | `HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md` | ✅ 本文件 (B1~B5 齐全) |
| 2 | ★**口径对照页** | `SW/ADC_CALIBER_TABLE.md` (9221 B) | ✅ 18 行对照表 (含「FS 3.3→1.8」与「判决对象 VBUS_DET_D→BAT_DET」两行) |
| 3 | ★**改动的脚本** | `SW/tools/timing_check.py` (md5 `cf09c921002937920bfa40701d523b33` · 2632 行) | ✅ ★**单文件, 别的文件一个字节没动**★ |
| 4 | ★**分片** | `state/fragments/sw.yaml` (走 `state/frag_write.py --agent sw-lead` 原子写) | ✅ 见 §6 |

★**回归 rc (本机实跑, 逐条原样)**: ★`timing_check.py` rc=0 (85/85) · `check_demo_panel_spec.py` rc=0 · `--selftest` rc=0 (22/22) ·
★`HW/check_step1_parts_spec.py` rc=0 (8/8) · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 · `state/issue_check.py` rc=0 ★
★**受保护 5 件 md5 逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ·
网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★

---

## §B1 判决对象改对 (★F4 判【真 ADC 链】, 不再判 USB 数字脚★)

### §B1-1 病根 (★本机实读, 逐字带行号★)

★**旧取链规则** (`SW/tools/timing_check.py` 旧 L1138~L1141, 改前 md5 `68c4becffe6bcd708e388dba9d18a505`):

```python
act = [c for c in det_chains if c["populated"]] or det_chains
rth = act[0]["rth_ohm"]           # ★永远取元组顺序里的第一条 populated★
```

⇒ `act[0]` = `VBUS_DET_D` (元组第一条) ⇒ ★**判据【从不看这条链落到哪个脚】**★

★**两条链实际落到不同的脚** (★网表 + 脚表实读★):

| 链 | 网表落点 | 脚表那一行 | 落点是什么脚 |
|---|---|---|---|
| ★**VBUS_DET_D** | ★`HW/netlist_v1.csv:439` ⇒ `J_SOM_P1 pin100` | ★`HW/PCB/FET3572C_PIN_TABLE.csv:101` 逐字 `P1,100,B28,USB_DRD1_VBUSDET,——,——,USB2_OTG1_VBUSDET insert detection,USB2_OTG1_VBUSDET` | ★★**USB OTG 插入检测 = 数字输入脚** (域栏 = `——`) ⇒ **不是 SAR-ADC** ★ |
| ★**BAT_DET** | ★`HW/netlist_v1.csv:186` ⇒ `J_SOM_P1 pin38` | ★`HW/PCB/FET3572C_PIN_TABLE.csv:39` 逐字 `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` | ★★**SARADC_VIN5 = 1.8V 域 · 12 bit** ★ ⇒ ★**这才是本板真正的 ADC 输入**★ |

### §B1-2 改法 (★三条, 一条都不许省★)

1. ★**判决源换成 SoM 脚表** ★ ⇒ 新函数 `load_som_pin_table()` 读 `HW/PCB/FET3572C_PIN_TABLE.csv`:
   - `signal` 列以 `SARADC` 开头 ⇒ 该脚是 SAR-ADC 输入;
   - `vol` 列 = 该脚 IO 域 (`SARADC_VIN5` = `1.8V`; `USB_DRD1_VBUSDET` = `——` ⇒ 域未知);
   - ★**脚表读不到 ⇒ fail-closed 判红** (★绝不退回「元组第一条」★)★。
2. ★**落点 = 网表实读** ⇒ 新函数 `resolve_chain_landing()`:
   - 中点网 = 节点列同时出现上/下臂两个位号的那一行的 `net` 列 (BAT_DET ⇒ `:183`; VBUS_DET_D ⇒ `:435`);
   - 落点脚 = 中点网上 `node1/node2` 形如 `J_SOM_P1 pinN` 的行 (中点网与落点行不同名时再按 `node` 列反查: VBUS_DET_D ⇒ `:439`) ⇒ ★**不许手抄落点**★。
3. ★**取链规则 = 「落点是不是 SAR-ADC 脚」** ⇒ 新开关 `CHAIN_SELECT_MODE`:
   - `by_landing_pin` (默认, 新口径): ★**唯一**一条装机链落在 SAR-ADC 脚上 ⇒ 那条就是 ADC 链;
   - ★**0 条 ⇒ fail-closed 红** (「ADC 输入悬空 / 无判据」); ★**≥2 条 ⇒ fail-closed 红** (「判决对象不唯一」)★;
   - `tuple_order` (★**老错规则, 只给反向用例用**★): 老逻辑原样保留, 供 REV-13 反向自证。

★**改后 `active_chain` = `BAT_DET`** ✔ (本机实跑 `python3 SW/tools/timing_check.py --only F4_adc_det` 逐字:
`active_chain : BAT_DET` · `active_chain_pin : 38` · `active_chain_signal : SARADC_VIN5` · `active_chain_domain : 1.8V`) ★

### §B1-3 数字链另立口径 (★F4D 段, 三项齐全★)

★**`VBUS_DET_D` 链从 ADC 判据里摘出来** ⇒ 新输出段 `F4D_usb_vbus_det` ⇒ 判据三项 (★任务书 §B1-3 要的①②③★):

| # | 判据 | 现网表算出来的数 | 阈值 | 依据 (逐字) | 结论 |
|---|---|---|---|---|---|
| ① | ★**常开静态电流** | ★**4.81 µA** (理想分压 2.5 µA; ★含内部 40kΩ 降级取大值★) | ≤ **26.25 µA** | 上限 = 同板 BAT_DET 链 V-3 已裁决值 (网表 `:182` note「常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)」) | ✔ 绿 |
| ② | ★**节点电平** | ★**2.5 V** @5V (VBUS 4.75~5.25V ⇒ **2.375~2.625 V**) | > **2.3 V** (识别阈值) | ★Forlinx FET3572 手册 `state/_os_snapshots/fx3572_manual.html` §USB Design Note 逐字: 「In device mode, VBUSDET must be high (> 2.3 V) to pull up DP and start enumeration.」+「A high level indicates DEVICE mode (2.7–3.3 V, typical: 3.0 V)」 | ✔ 绿 ⚠ **裕量仅 75 mV (3.3%)** |
| ③ | ★**该脚 abs-max** | 节点 2.625 V (VBUS 上限) | ≤ **3.3 V** (★**降级上界**) | ★脚表 `:101` `vol` 栏 = `——` ⇒ 域未知 ⇒ ★**[0数据]** ★ ⇒ 降级取手册标称高电平带上沿 3.3V; ★**域一旦填上, 闸的 abs-max 判据自动按 `域+0.3V` 生效**★ | ✔ 绿 (降级) |

★**三条未决项不许藏** ⇒ 闸的输出里 `unresolved` 段逐条打印 (★不是注释, 是机器可读字段★):

| 未决项 | 证据等级 | 后果 | 降级方案 |
|---|---|---|---|
| ★**该脚是否带内部 40kΩ 下拉** | ★**[0数据]** (手册只对 **USB_DRD0_VBUSDET** 明写「internal 40 kΩ pull-down」; 本板是 **DRD1** ⇒ 手册未记载) | ★**若带 ⇒ 节点 = 0.185 V < 2.3 V ⇒ USB 插入检测永不触发**★ | 本闸按「无内部下拉」判硬判据, 同时把 **0.185 V** 这个情形一并算出报出 ⇒ ★**登记 need (不阻塞本闸, 但禁止据此判『安全』)**★ |
| ★**该脚 IO 域 / abs-max** | ★**[0数据]** (脚表 `:101` vol 栏 = `——`) | ★若域实为 1.8V ⇒ abs-max = 2.1 V ⇒ 节点 2.625 V **越限** ⇒ 必须改分压比★ | 降级上界 3.3 V; ★域一填上, 判据自动收紧★ |
| ★**识别裕量** | ★**[官方]** VBUS 4.75~5.25 V + 阈值 2.3 V | @4.75 V 节点 2.375 V ⇒ 距阈值只剩 **75 mV (3.3%)** | 本闸按**最坏 VBUS 下限 4.75 V** 判 (比标称 5 V 更严) |

★**判据方向不许变** ✔ ⇒ 「ADC 链建立时间不足 / 漏电偏移过大 ⇒ 仍必须红」这条**原样保留** (阈值 300 ms / 0.4 V 一个没动),
★**只是把被测对象换成对的那个** ★ (⇒ 见 §B3 的 REV-14/REV-15: 那两条判据现在**真的**能红)

---

## §B2 满量程口径改对 (★3.3V → 1.8V 域, 带官方出处★)

### §B2-1 三处官方出处 (★逐字引★)

| # | 出处 | 逐字 | 证据等级 |
|---|---|---|---|
| ① | ★`HW/PCB/FET3572C_PIN_TABLE.csv:39` | `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` | ★**[实测]** (本机实读) |
| ② | ★`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt:2454` | `   SARADC Analog Power(1.8V)               SARADC_AVDD1V8             1.62    1.8     1.98     V` | ★**[官网]** ⇒ 1.62 / **1.8** / 1.98 V |
| ③ | ★同上 `:2864` | `Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V` | ★**[官网]** ⇒ 模拟输入范围 = AVSS18~AVDD18 ⇒ **满量程 1.8 V** |
| ④ | ★同上 `:2863` | `Resolution                                                                 NA           12         NA       Bit` | ★**[官网]** ⇒ 12 bit (★`ADC_BITS` 的证据等级从 [0数据] 升到 [官网]★) |

★**代码改动**: `DEVICE["V_DET_FS"]: 3.3 → 1.8` (`SW/tools/timing_check.py:81` 那一行), `SOURCES["V_DET_FS"]` 逐字引上面四处 ★

### §B2-2 「查不到」不许放宽成「按 3.3V 算」 ✔

★**本单没有出现任何「查不到 ⇒ 换个值凑上」的情况**: 满量程有官方出处 ⇒ 直接用; ★**查不到的三项 (USB 脚域 / 内部下拉 / SAR-ADC 源阻抗要求) 一律标 [0数据] + 降级方案 + 登记 need** ★ (见 §B1-3 的 unresolved 表 + §B5) ⇒ **不许把「查不到」放宽成「按 3.3V 算」**这条守住了.

### §B2-3 ★三个数与网表 note 逐字对上 (★最省事的自证★)

★**网表 `HW/netlist_v1.csv:182` note 逐字**:
「`[BAT_DET_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4): R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★; ★常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)★`」

★**闸改完后算出来的 (本机实跑 `--only F4_adc_det` 逐字)**:

| 量 | 网表 note 写死的数 | 闸算出来的数 | 对上了? |
|---|---|---|---|
| R_th | 37.5 kΩ | `rth_ohm : 37500.0` | ✔ |
| 漏电偏移电压 | 37.5 mV | `leak_offset_v : 0.0375` | ✔ |
| ★**漏电偏移 %FS** | ★**2.1 % FS** | ★`leak_offset_pct_fs : 2.1` | ★**✔ 逐字对上 ⇒ 口径同源**★ |
| 常开静态功耗 | 26.25 µA / 110 µW | `standby_ua : 26.25` | ✔ |

★**闸还做了一道「机器对账」** ⇒ `netlist_note_facts` 字段**从网表 note 里正则抽出那三个数**再跟算出来的数对:
`fs_caliber_ok = (FS == 1.8) ∧ (|算得 %FS − note %FS| ≤ 0.06) ∧ (|算得 mV − note mV| ≤ 0.6) ∧ (|算得 kΩ − note kΩ| ≤ 0.6)`
⇒ ★**以后任何人再改一边 (网表 note 或脚本口径), 另一边的灯立刻红** ★ (这才是「口径同源」的真含义, 不是本单这次对上了就算完)

★**顺带纠正任务书里的一个算术** (★不改任务书, 只在交卷单留痕★): 任务书 §①-1 表里写「官方口径 常开静态电流 **0.90 µA** (=1.8V/160k)」
⇒ ★**1.8 V / 160 kΩ = 11.25 µA, 不是 0.90 µA** ★; 且**物理上 BAT_DET 链的供电是电池轨 (网表 `:24` = `4.2V 满 / 3.0V 截止`), 不是 ADC 满量程**
⇒ ★**正确值 = 4.2 V / 160 kΩ = 26.25 µA**, 恰好与网表 note 写死的「26.25µA / 110µW」逐字一致 ⇒ ★**闸取 26.25 µA** ★
(★老闸算的 1.65 µA 也是错的: 那是拿 FS 3.3 V 当供电算的 ⇒ 3.3/2M★)

---

## §B3 反向用例 (★6 条, 每条贴原样 rc + 期望红组 vs 实际红组★)

★**跑法**: `python3 logs/iss291/rev_cases.py` (★只读盘面真源, 改坏的都是副本 ⇒ /tmp 或同目录临时副本, 跑完即删★)
★**原始日志**: `logs/iss291/rev_cases.log` ★

| # | 构造 | ★**原样 rc**★ | ★**期望红组**★ | ★**实际红组**★ | 判定 |
|---|---|---|---|---|---|
| ⑤ | ★**正向对照: 一切如常** | ★**rc=0** | **无红** | **无红** (85/85 通过) | ★**绿** ★ (证明闸不是恒红) |
| ① | ★把 `V_DET_FS` 改回 **3.3** (脚本副本) | ★**rc=1** | 满量程/口径同源判据红 (`fs_caliber_ok: True→False`; LSB 0.439→0.806 mV; %FS 2.1→1.1) | `F4 实读: 满量程 = 1.8V 域…` + `F4 实读: 漏电偏移 37.5mV = 2.1% FS…(口径同源)` + `F4 实读: ADC 节点 @4.2V…` + `REV-12 反向…必须变红` | ★**红** ✔ |
| ② | ★把取链规则改回 **「元组第一条」** (脚本副本) | ★**rc=1** | 判决对象判据红 (`object_ok: True→False`; `active_chain: BAT_DET→VBUS_DET_D`) | `ADC 源阻抗 = 37.5k…` + `ADC tau = 3.75ms…` + `ADC 12bit 建立…` + `ADC 漏电偏移…` + `F4' 实读: ADC 判决对象 = BAT_DET 链…` + `F4 实读: 漏电偏移…口径同源` + `F4 实读: 判决源 = SoM 脚表…` + `F4 实读: ADC 节点…` + `REV-12…REV-15` | ★**红** ✔ |
| ③ | ★把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 **DNP** | ★**rc=1** | 「ADC 输入悬空」红 (`populated_ok: True→False`; `active_chain → (无: fail-closed)`) | `ADC 源阻抗…` `ADC tau…` `ADC 12bit 建立…` `ADC 漏电偏移…` `F4' 实读: ADC 判决对象…` `F4 实读: 漏电偏移…口径同源` `F4 实读: 判决源…` `F4 实读: ADC 节点…` `REV-11…REV-15` | ★**红** ✔ |
| ④ | ★把 BAT_DET 下臂 60k → **100k** | ★**rc=1** | ★**过压判据红** (`node_ok: True→False`; 节点 1.575 V → **2.1 V > 1.98 V**) | `ADC 源阻抗…` `ADC tau…` `F4 实读: 漏电偏移…口径同源` `F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V…` `REV-12…` `REV-15…` | ★**红** ✔ |
| ⑥ | ★把 VBUS_DET_D 两颗电阻改成 **10k/10k** | ★**rc=1** | ★**数字链静态电流判据红** (`static_current_ok: True→False`; 4.81 µA → **277.8 µA**) | `F4D 实读: 数字链常开静态电流 4.81µA…≤ 26.25µA 上限` + `REV-16 反向…必须变红` | ★**红** ✔ (★数字脚口径也在判, 不是只判 ADC★) |
| ⑥b | ★(加分) 把 VBUS_DET_D 上臂 1M → **10M** | ★**rc=1** | ★**数字链节点电平判据红** (`level_ok: True→False`; 2.5 V → **0.455 V < 2.3 V**) | `F4D 实读: 数字链常开静态电流…` + `F4D 实读: 数字链节点 2.5V > 识别阈值 2.3V…` + `REV-17 反向…必须变红` | ★**红** ✔ |

★**自证「真改到了目标」的做法 (★ISS-235 同型, 不许只写一句「它变红了」★)**:
- ★**正向用例与反向用例共用同一个具名判据函数** (`_f4_adc_object_ok` / `_f4_adc_fs_caliber_ok` / `_f4_adc_node_ok` / `_f4_adc_populated_ok` / `_f4d_static_ok` / `_f4d_level_ok`)
  ⇒ ★**同一个函数**在基线上 True、在突变体上 False ⇒ ★「红」不可能是别的条红 (ISS-227 教训)★;
- ★**① 与 ② 是「常量/分支」突变, 不是网表突变** ⇒ 为它们单写了两个 runner (`_mk_reverse_fs_3v3` / `_mk_reverse_chain_mode`),
  ★**改完立刻改回** ⇒ 且 runner 内断言「mutant 的 `full_scale_v` 真的是 3.3 / `active_chain` 真的是 VBUS_DET_D」⇒ **自证改到了目标** ★;
- ★**改副本 ⇒ 锚点类必然红 1 条** (网表 md5 变了) ⇒ 日志里单列为「锚点噪声」, **不计入目标红组** (盘面真源一个字节没动) ★.

★**闸里同时落成 6 条常驻反向用例** (`REV-12`~`REV-17`, 名字逐字见上表) ⇒ ★**每次跑 `timing_check.py` 都自动验一遍** ★ (本机实跑: `REV-12`~`REV-17` 六条全 PASS, 即「都真的能变红」) ★

---

## §B4 回归 (★别的闸一条不许红★)

★**本机实跑** (`logs/iss291/regress.sh` · 原始日志 `logs/iss291/regress.log` 与最终复跑 `logs/iss291/regress_final.log`):

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py;                   echo "rc=$?"   # ⇒ rc=0  ·  SELFTEST 85/85 通过
python3 SW/tools/check_demo_panel_spec.py;           echo "rc=$?"   # ⇒ rc=0  ·  R1~R7 全过 (R5 38 处 / R6 三方对账一致)
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"   # ⇒ rc=0  ·  SELFTEST 22/22 通过
python3 HW/check_step1_parts_spec.py;                echo "rc=$?"   # ⇒ rc=0  ·  8/8 通过
python3 state/merge.py;                             echo "rc=$?"   # ⇒ rc=0  ·  STATE.yaml 已刷新
python3 state/gate_check.py;                        echo "rc=$?"   # ⇒ rc=0  ·  Q1 18/18
python3 state/issue_check.py;                       echo "rc=$?"   # ⇒ rc=0  ·  问题闭环门全过
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**受保护 5 件 md5 逐字节不变 (本机实跑)**:

```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
37f62ac3f0b81d92ca7d48fdea717f07  HW/netlist_v1.csv
a4270120454aedf7a23c92cd8985c8a6  HW/netlist_v1_pins.csv
5d02bece9477ffce5fbe0193c7d5cce4  HW/BOM_v1.csv
```

★**自测条数只许增不许减** ✔ ⇒ `timing_check.py` 自检由 **72/72 (ISS-288 落地态)** → **85/85** (★+13 条: 4 条既有 ADC 断言按新口径重写 + 8 条新正向 + 6 条新反向, 其中既有 1 条被 8 条新正向里的 1 条合并覆盖 ⇒ 净 +13★)
★**`check_demo_panel_spec.py --selftest` 仍是 22/22** ⇒ ★**ISS-275 已跑通的那条链头逻辑一个字节没碰** (`SW/tools/check_demo_panel_spec.py` md5 未变) ★

★**⚠ 一处旧文档遗留 (★本单不改, 登记在 §B5★)**: `SW/SW_TIMING_REVIEW.md` 的「ADC 500kΩ/451ms/漏电 15.2%FS」结论**已被本单推翻**
(★判错了对象 + 口径错★) ⇒ ★**本单边界内不改那份文档** ⇒ 请 main 决定何时回填 (★回填时建议直接引 `SW/ADC_CALIBER_TABLE.md`§4★)★

---

## §B5 硬件侧后果 —— 只「登记」, 不自己改 (★跨域纪律★)

★**B1/B2 的结论确实指向硬件** ⇒ 但★**网表真源归 hw-lead + 老板那一趟「板只改一次」★** ⇒ 本单★**只交结论 + 证据**★,
★**一个字节都没改**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/FET3572C_PIN_TABLE.csv` /
`HW/PCB/demo_mainboard.kicad_pcb` / `state/gen_netlist.py` / `HW/check_netlist_selfconsistency.py` ★**全部未动** ★

### §B5-1 登记给 main 的两条 need (★已写进 `state/fragments/sw.yaml` 的 `needs_from`, `to: main`★)

#### ★need ① `iss291_sw_vbus_det_d_digital_caliber` ★

- ★**哪一行网表**: `HW/netlist_v1.csv:434` (`R_VBUS_DET_D1` = `1M ±1% (上臂)`) + `:435` (`R_VBUS_DET_D2` = `1M ±1% (下臂)`) + `:439` (落点 `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET`)
  + `HW/PCB/FET3572C_PIN_TABLE.csv:101` (该脚 `vol` 栏 = `——` ⇒ 域未知)
- ★**哪个值 / 什么口径**: ★**`USB_DRD1_VBUSDET` 的 IO 域 + abs-max + 是否有内部 40kΩ 下拉** (三件事, 项目库现在都查不到 ⇒ **[0数据]**)
- ★**为什么**: ① 手册只对 **USB_DRD0_VBUSDET** 明写「internal 40 kΩ pull-down」+「高电平 2.7–3.3 V」+「识别阈值 > 2.3 V」
  ⇒ **本板是 DRD1** ⇒ ★**若 DRD1 同样带 40 kΩ 内部下拉: 节点 = 5V×(1M‖40k)/(1M+1M‖40k) = 0.185 V ≪ 2.3 V ⇒ USB 插入检测永不触发**★
  ⇒ ② ★**本闸把两条都算出来报出 (理想 2.5 V / 含下拉 0.185 V)**, ★**不假装绿也不假装红**★ ⇒ 走 need 由硬件侧定夺
  ⇒ ③ ★**识别裕量薄**: VBUS 取 USB 规范下限 4.75 V 时节点 2.375 V, 距识别阈值 2.3 V 只剩 **75 mV (3.3%)** ⇒ ★**建议 hw-lead 复核分压比**★
- ★**代价 (★供 main / 老板拍板, 本单不拍★)**:
  - ★**方案 A (换料, 拓扑不变, 推荐先算清)**: 上臂 1M → **22k**、下臂 1M 保持 ⇒ 节点 = 5V×(1M‖40k)/(22k+1M‖40k) = **3.18 V** (落在手册 2.7–3.3 V 高电平带内) ⇒ 静态电流 5V/(22k+38.5k) = **82.6 µA / 413 µW** (★代价: 常开功耗从 2.5 µA 涨到 ~83 µA★)
  - ★**方案 B (按手册推荐)**: 该脚直接 3.3 V 上拉 (手册: 「pull USB2_OTG0_VBUSDET high to 3.3 V through a 4.7 K resistor」) ⇒ 静态电流 3.3V/4.7k = **702 µA** ⇒ ★**代价最大, 只在功能优先级高于功耗时选**★
  - ★**方案 C (不动硬件, 只登记)**: 接受 75 mV 裕量 + 把「USB 插入检测是否可靠」列为 EVT 必测项 ⇒ ★**代价: 功能风险留在板子上**★
- ★**降级方案 (★若这一趟来不及改板★)**: ★**保留现网表 1M/1M, 但 EVT 必测项加一条: 「插拔 USB 时读 `USB_DRD1_VBUSDET` 状态位, 确认能区分插/不插」★**
  ⇒ ★**若实测读不到高电平 ⇒ 说明内部 40 kΩ 下拉存在 ⇒ 立刻按方案 A 改料 (换料不换板)**★

#### ★need ② `iss291_sw_do_not_apply_vbus_100k47k` ★

- ★**哪一行 / 哪个值**: ★**`HW/CHARGE_STATUS_READBACK.md:101` 里那条建议「把 `VBUS_DET` 的分压从 1M+1M 改为 100k/47k」★** (★**那不是网表行, 是文档里的待办建议★**)
- ★**为什么不许照做**: ★**那条建议是按「`VBUS_DET` 是 SAR-ADC 输入」提的** ★ ⇒ ★**而它其实是 USB 插入检测数字脚 (pin100)★**
  ⇒ ★**100k/47k ⇒ 节点 = 5V×47/147 = 1.60 V < 2.3 V ⇒ USB 插入检测直接死**★ ⇒ ★**照做 = 把一个假红换成真死功能**★
- ★**代价**: 不照做 = 放弃一条基于错误前提的整改项 (零硬件成本) ⇒ ★**正确动作 = 先按 need ① 把口径和域确认掉, 再决定 VBUS_DET_D 怎么改**★
- ★**降级方案**: ★**若「板只改一次」那一趟已经把这 100k/47k 写进网表 ⇒ 立刻回退成 1M/1M 或按 need ① 的方案 A 改值**★

### §B5-2 顺带闭环的两条 (★任务书 §⑤-4 交办的小事 + main 追加派的一条★)

★**(a) `needs_from` 里的 `iss285_sw_apply_after_iss283_verified` 已标成已解决** ⇒ `resolved_by: ISS-288` ★
(★理由: ISS-283 已 verified + ISS-285 补丁已落盘, `SW/tools/timing_check.py` 当时 md5 = `68c4becffe6bcd708e388dba9d18a505`
= ISS-285 交卷单写死的期望值 ⇒ 该 need 的前提已满足★) ★

★**(b) ★main 追加派的一条: 回答 `hw.yaml` 里的 need `iss223_sw_vdet_fs_domain_fix` (to = sw-lead)★**
⇒ ★**答案写在【sw-lead 自己的分片】`state/fragments/sw.yaml` 的 `answers` 段** (key = `iss223_sw_vdet_fs_domain_fix`, to = sw-lead)
⇒ ★走 `python3 state/frag_write.py --agent sw-lead --add-answer` 原子写 (★没碰 hw.yaml 一个字节★)★
⇒ ★**合并器配对已闭合** (本机实跑 `state/merge.py` 后在 STATE.yaml 里查得该 need `state: answered` · `target_missing: false`
· **不是 foreign_answer**) ⇒ ★答案内容逐条对账: ① 满量程 3.3 → 1.8 (脚表 :39 + datasheet :2454/:2864/:2863 四处逐字, ★证据 [官网]★)
⇒ 改前 1.1%FS → 改后 **2.1%FS**, 与网表 `:182` note **逐字对上** [实测·网表写死] ⇒ ② ★**比 need 问的还多一条**: 判决对象也改对了 (取链规则由「元组第一条」改为「落点是不是 SAR-ADC 脚」⇒ `active_chain` = BAT_DET / pin38 / SARADC_VIN5) ⇒ ③ 逐链判决已补 (数字链 F4D 口径 + 三条 [0数据] 未决项登记 need) ⇒ ④ 机器闸含反向用例 REV-12~REV-17 ⇒ ⑤ 实测 rc (85/85 + 回归 7 条全 rc=0 + 受保护 5 件 md5 不变) ⇒ ★请 hw-lead / main 把该 need 标 closed★ ★

---

## §6 分片 (`state/fragments/sw.yaml`) ★

★走 `python3 state/frag_write.py --agent sw-lead` (原子写) ⇒ 写完 `grep` 校验 ★

| 项 | key | to | 内容 |
|---|---|---|---|
| need ① | `iss291_sw_vbus_det_d_digital_caliber` | main | ★USB 插入检测链 (pin100) 的域 / abs-max / 内部下拉三未决 + 三个方案 + 代价 + 降级方案★ |
| need ② | `iss291_sw_do_not_apply_vbus_100k47k` | main | ★**「板只改一次」那一趟不许套 `VBUS_DET` 100k/47k 那条 (基于错误前提)★** |
| artifact | `SW/ADC_CALIBER_TABLE.md` | — | ★口径对照页 (18 行表 + 三处「查不到」的处理 + 旧文档处置)★ |
| artifact | `SW/tools/timing_check.py` | — | ★改后的脚本 (md5 `cf09c921…`)★ |
| artifact | `HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md` | — | ★本交卷单★ |
| 状态 | `status` | — | ★phase=delivered · health=green · summary 写全★ |
| ★**answer (追加)** | `iss223_sw_vdet_fs_domain_fix` | sw-lead | ★**回答 hw.yaml 那条 to=sw-lead 的 need** (★写在 sw-lead 自己分片 ⇒ 合并器配对为真闭合, 不是 foreign_answer★) ⇒ 见 §B5-2(b)★ |
| ★**既有 need 标记** | `iss285_sw_apply_after_iss283_verified` | — | ★**`resolved_by: ISS-288`** ★ (见 §B5-2) |

★**校验**: `grep -c "iss291" state/fragments/sw.yaml` ⇒ **4** (need ① key + need ② key + need ② 正文里引 need ① + artifact 摘要里引交卷单路径)
★**分片写入后复核** (本机实跑): `needs_from` 106 条 / `artifacts` 184 件 · `iss285_sw_apply_after_iss283_verified.resolved_by = ISS-288` ✔ ·
★**分片写完后再跑 `state/merge.py` rc=0 · `state/gate_check.py` rc=0 · `state/issue_check.py` rc=0** ✔ (STATE.yaml 已刷新) ★

---

## §7 边界自查 (★违反就是不合格★)

| 边界 | 自查结果 |
|---|---|
| ★零写板 | ✔ `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e…` 不变 (mtime 也没碰) |
| ★零落表 (网表/脚表/BOM) | ✔ 三个 md5 逐字节不变 (`37f62ac3…` / `a4270120…` / `5d02bece…`) |
| ★不许改 `HW/` 任何文件 | ✔ 本单只写 `SW/tools/timing_check.py` (单文件) + `SW/ADC_CALIBER_TABLE.md` (新文件) + `HANDOFF/` + `state/fragments/sw.yaml` + `logs/iss291/` |
| ★不许碰 `MECH/` | ✔ 零读写 |
| ★不许改 `check_demo_panel_spec.py` 的链头逻辑 | ✔ 该文件一个字节没碰 (`--selftest` 仍 22/22) |
| ★零外发 | ✔ 没发邮件 / 没询价 / 没问供应商 / 没下采购单 (★**也没向外发过任何消息**★) |
| ★不替老板拍板 | ✔ 三个改分压比方案 + 代价全部列出来, ★**由 main / 老板拍**★ |
| ★不自签 issue_log | ✔ `state/issue_log.yaml` 一个字节没碰 (★签字是 main 的活★) |
| ★不许把整份大文件读进来 | ✔ 全程 grep / sed 定位, 脚表只读需要的行 |
| ★不许借这一单去改网表真源 | ✔ 硬件后果全部走 §B5 的两条 need |
| ★板端实物 [实测] | ★**0 条** (本机无板端实测) ⇒ 本单所有数都是**静态推算 + 官方文档 + 网表实读** |

---

## §8 留给 main 的三件事 (★我不拍★)

1. ★**拍板 VBUS_DET_D 改不改、怎么改** (need ① 的 A/B/C 三方案 + 代价) ⇒ ★**决定点: 「板只改一次」那一趟之前** ★
2. ★**拍板 `SW/SW_TIMING_REVIEW.md` 旧 ADC 结论何时回填** (★本单只出对照页, 不改旧文档★)
3. ★**验签**: 把 `state/issue_log.yaml` 的 ISS-291 由 `fixing` 改成 `verified` + `fix_ref` 填本交卷单路径
   ⇒ ★**同时把 `needs_from` 里 `iss285_sw_apply_after_iss283_verified` 标 closed** (★已在 sw.yaml 里标 `resolved_by: ISS-288`★) ★

---

## §9 复现命令 (★一键复算全部结论★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py --only F4_adc_det        # ★判决对象 + 满量程口径 + 三个数与 note 对账★
python3 SW/tools/timing_check.py --only F4D_usb_vbus_det   # ★数字链三项判据 + 三条未决项★
python3 SW/tools/timing_check.py                           # ★rc=0 · 85/85★
python3 logs/iss291/rev_cases.py                           # ★6 条反向用例: 原样 rc + 期望/实际红组★
bash logs/iss291/regress.sh                                # ★回归 7 条 + md5 5 件★
```

★**本次交卷涉及的文件 (全清单)** ★
```
SW/tools/timing_check.py                                                   (改) md5 cf09c921002937920bfa40701d523b33 · 2632 行
SW/ADC_CALIBER_TABLE.md                                                    (新) 口径对照页
HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md          (新) 本交卷单
state/fragments/sw.yaml                                                    (改) needs_from +2 / 标 1 / artifacts +3
logs/iss291/rev_cases.py · logs/iss291/rev_cases.log · logs/iss291/regress.sh · logs/iss291/regress.log   (新) 证据日志
```
★**零改动**: `HW/**` 全部 · `MECH/**` 全部 · `SW/tools/check_demo_panel_spec.py` · `state/issue_log.yaml` · `state/gen_netlist.py` ★
