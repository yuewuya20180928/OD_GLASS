# ISS-291 · sw-lead 任务书 —— ★★【SW 侧 ADC 判据: 判决对象 + 满量程口径双错】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 15:5x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-291 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · SW 侧判据口径收口 + 机器闸类** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源 · 不碰 `HW/` 与 `MECH/`** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单不动板, 只把一条判据的口径钉死★)

---

## ★① 病灶 (★main 2026-11-17 15:4x~15:5x 本机实读 + 实跑, 逐条带行号, 不抄任何交卷报告★)

### ★①-1 · 【满量程口径错】: SW 闸写死 3.3V, 官方是 1.8V 域

| 出处 | 逐字 | 证据等级 |
|---|---|---|
| ★`SW/tools/timing_check.py:81` ★ | `"V_DET_FS": 3.3,             # V   SoC ADC 满量程 (3.3V 域) [网表 P2 RAIL_VDD_3V3_IO]` | ★**[实测]** 本机实读★ |
| ★`HW/PCB/FET3572C_PIN_TABLE.csv:39` ★ | `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` | ★**[实测]** ★★**⇒ 本板唯一用的 ADC 脚 = J_SOM_P1 pin38 = SARADC_VIN5 = 1.8V 域**★ |
| ★`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt:2454` ★ | `   SARADC Analog Power(1.8V)               SARADC_AVDD1V8             1.62    1.8     1.98     V` | ★**[官网]** ★SAR-ADC 模拟电源 = 1.8V 标称 / 1.62~1.98V★ |
| ★同上 `:2863` ★ | `Resolution                                                                 NA           12         NA       Bit` | ★**[官网]** 12 bit★ |
| ★同上 `:2864` ★ | `Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V` | ★**[官网]** ★★**模拟输入范围 = AVSS18 ~ AVDD18 ⇒ 满量程 1.8V, 不是 3.3V**★ |

★**⇒ 同一件事 (「SoM ADC 满量程是多少」), 现在有 3.3V (SW 闸) 与 1.8V (官方 + 脚表 + 网表 note) 两个判决源 ⇒ 结果一个绿一个红★★

★**★实测的两种口径算出来差多少 (main 本机按现有脚本公式手算, 逐条对得上盘面输出)★**:

| 量 | SW 闸现在用的 (FS=3.3V · VBUS_DET_D 链) | 官方口径 (FS=1.8V · 真 ADC 链 BAT_DET 100k+60k) |
|---|---|---|
| ★**LSB** ★ | ★0.806 mV (=3.3/4096)★ | ★**0.440 mV** (=1.8/4096)★ |
| ★**漏电偏移 %FS** ★ | ★0.50V / 3.3V = **15.2%**★ | ★**37.5 mV / 1.8V = 2.1%**★ |
| ★**漏电偏移电压** ★ | ★0.50 V (=1µA × 500 kΩ)★ | ★**0.0375 V** (=1µA × 37.5 kΩ)★ |
| ★**常开静态电流** ★ | ★1.65 µA (=3.3V/2M)★ | ★**0.90 µA** (=1.8V/160k)★ |

★**⇒ ★★「网表 note 说 2.1% FS」 vs 「SW 闸算 15% FS」 —— 同一个 BAT_DET 分压链, 项目里有两个数, 差 7 倍★★ ★**
★**盘面逐字 (★`HW/netlist_v1.csv:182` 的 note★)**: `[BAT_DET_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4): R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★` ★⇒ **网表按 1.8V FS 写的 (2.1%) ⇒ 网表是对的, SW 闸的 FS 口径是错的** ★

### ★①-2 · 【判决对象错】: F4 把【USB 数字检测脚】当成【SAR-ADC 输入链】在判

★**F4 代码 (`SW/tools/timing_check.py` 约 L1110~L1157) 的取链逻辑 (★main 本机实读逐字★)**:
```python
for top, bot, cap, tag in (("R_VBUS_DET_D1", "R_VBUS_DET_D2", "C_DET_VBUS_D", "VBUS_DET_D"),
                           ("R_BAT_DET_1",  "R_BAT_DET_2",  "C_DET_BAT",     "BAT_DET")):
    ...
act = [c for c in det_chains if c["populated"]] or det_chains
rth = act[0]["rth_ohm"]           # ★永远取元组顺序里的第一条 populated★
```
★**⇒ `act[0]` = `VBUS_DET_D` (元组第一条) ⇒ 判据【从不看这条链落到哪个脚】★**

★**而两条链实际落到的脚完全不同 (★main 本机实读网表逐字★)**:

| 链 | 网表行 | 落点 | 落点是什么脚 |
|---|---|---|---|
| ★**VBUS_DET_D** ★ | ★`HW/netlist_v1.csv:434~438` (R_VBUS_DET_D1/2 = 1M/1M 必装 · C_DET_VBUS_D = 100nF 必装)★ | ★`HW/netlist_v1.csv:439` ⇒ `J_SOM_P1 pin100`★ | ★★**`USB_DRD1_VBUSDET`** ★ — ★`FET3572C_PIN_TABLE.csv:101` 逐字: `P1,100,B28,USB_DRD1_VBUSDET,——,——,USB2_OTG1_VBUSDET insert detection,USB2_OTG1_VBUSDET`★ ⇒ ★**USB OTG 插入检测 = 数字输入脚 (域栏是「——」) ⇒ 不是 SAR-ADC**★ |
| ★**BAT_DET** ★ | ★`HW/netlist_v1.csv:182~186` (R_BAT_DET_1 = 100k 必装 · R_BAT_DET_2 = 60k 必装 · C_DET_BAT = 100nF 必装)★ | ★`HW/netlist_v1.csv:186` ⇒ `J_SOM_P1 pin38`★ | ★★**`SARADC_VIN5` (1.8V 域 · 12 bit)**★ ⇒ ★**这才是本板真正的 ADC 输入**★ |

★**⇒ 现在这条闸【把 USB 数字检测脚当 12bit SAR-ADC 在算建立时间/漏电偏移/满量程】, 而【真正接 ADC 的 BAT_DET 链一条判据都没有】★★**

★**★盘面实测的错位后果 (main 15:4x 本机实跑 `python3 SW/tools/timing_check.py` 抓的原样输出)★**:
- ★现行输出: `active_chain : VBUS_DET_D` · `源阻抗 500000.0Ω / τ=50.0ms` · `12bit 精度需 451ms 建立` · `1µA 漏电流 ⇒ 0.50V 偏移 (15% 满量程)` · `verdict: ★★该分压值对 ADC 不可用★★`★ ⇒ **★这是【对象错 + 满量程错】双重错之后得到的一条红★★**
- ★**真 ADC 链自己站得住 (main 本机手算, 依据官方 1.8V 域)**: BAT_DET = 100k + 60k ⇒ R_th = **37.5 kΩ** · τ = **3.75 ms** · 12bit 建立需 9.01×τ = **33.8 ms** · 漏电 1µA ⇒ **37.5 mV = 2.1% FS (与网表 note 逐字一致)** · @BAT 4.2V 满 ⇒ 节点 = 4.2×60k/160k = **1.575 V ⇒ 在 1.8V 域内 (≤1.98V abs-max)** ★⇒ **★这条链不是问题, 而闸从来没在它身上判过★**

★**⇒ ★★病灶一句话: 【判决对象 + 满量程, 两处都取错了源】★★ ★⇒ ⇒ **闸现在报的红是「假红」, 同时【真 ADC 链处于无判据状态】⇒ ★这条红既不该红, 也不该以现在这个理由红★★**

---

## ★② 根因一句话: 【判决源不一致 —— 与 ISS-273/275/286/288 同型, 但这次错的是「对象」和「物理量」, 不是 md5】

| 判据 | 现在读的是什么 | 官方真源在哪 | 现状 |
|---|---|---|---|
| ★**F4 的满量程** ★ | ★脚本里写死的常量 `DEVICE["V_DET_FS"] = 3.3`★ | ★`FET3572C_PIN_TABLE.csv:39` + `rk3572_datasheet_V1.1.txt:2454/2863/2864`★ | ★**两源不同 ⇒ 错源是脚本**★ |
| ★**F4 的判决对象** ★ | ★元组顺序第一条 populated 链 (VBUS_DET_D)★ | ★**网表 L439 vs L186 的落点** (pin100 USB 数字脚 vs pin38 SARADC)★ | ★**取链规则里【没有「落到哪个脚」这一维】★** |
| ★**「哪些脚是 ADC」这件事** ★ | ★脚本自己写死一条链表★ | ★`FET3572C_PIN_TABLE.csv` (有 signal 列 + 域列)★ | ★**脚表里有现成的真源, 脚本没去读★** |

---

## ★③ 开工前置 (★硬约束, 先看这条★)

★**本单是纯 SW 侧判据活, 不依赖任何落表 ⇒ 不存在「等某个单落完才能开工」的阻塞 ⇒ 可以直接开工★**
★**但不许借这一单去改网表真源** ★ ⇒ 若 §④ 的分析结论指向「网表那条 note 或那条分压比要改」⇒ ★**登记 need 给 main (说清要改哪一行、为什么、代价), 由 main 决定并进「板只改一次」那一趟**, 本单只交结论 + 证据, **不许自己改** ★

---

## ★④ 要交的几件 (★每件都能独立验收★)

### ★B1 · 判决对象改对 (★F4 判【真 ADC 链】, 不再判 USB 数字脚★)

1. ★**取链规则必须按「落点是不是 SAR-ADC 脚」判, 不许按元组顺序判** ★ ⇒ ★**判决源 = `HW/PCB/FET3572C_PIN_TABLE.csv` 的 signal 列 + 域列 (★pin38 = SARADC_VIN5 / 1.8V; pin100 = USB_DRD1_VBUSDET / 数字★)★**
2. ★**本板真正的 ADC 链 = BAT_DET (→ pin38) ⇒ F4 的 `active_chain` 必须是 BAT_DET** ★
3. ★**VBUS_DET_D 链必须从「ADC 链」里摘出来, 改按【数字检测输入】口径单独判** ★ ⇒ 该口径至少包含: ★**① 静态电流 (5V / (1M+1M) = 2.5 µA) ② 节点电平 (5V × 1/2 = 2.5V) ③ 该脚 (USB2 OTG1_VBUSDET) 的 abs-max (★从项目库内官方 datasheet 查; 查不到就标 [0数据] 并写降级方案, 不许编★)★**
4. ★**判据方向不许变**: 「ADC 链建立时间不足 / 漏电偏移过大 ⇒ 仍必须红」这条不许弱化; ★**只是把被测对象换成对的那个**★

### ★B2 · 满量程口径改对 (★3.3V → 1.8V 域, 带官方出处★)

1. ★**`DEVICE["V_DET_FS"]` 必须改成 1.8V** ★ ⇒ ★**出处必须逐字引三处**: ★`FET3572C_PIN_TABLE.csv:39` (实测) + `rk3572_datasheet_V1.1.txt:2454` (SARADC_AVDD1V8 = 1.62/1.8/1.98V) + `:2864` (Anglog Input Range = AVSS18~AVDD18)★ ★**证据等级标 [官网]/[实测]** ★
2. ★**不许把「查不到」放宽成「按 3.3V 算」** ★ ⇒ 若某条依据不足 ⇒ 标 [0数据] + 降级方案 + fail-closed
3. ★**改完 F4 的三个数必须与网表 note 逐字对上 (★这是最省事的自证★)**: ★**漏电偏移 %FS 必须 = 2.1% (网表 L182 note 写死的那个数) ⇒ 对上了才算口径同源**★

### ★B3 · 反向用例 (★≥5 条, 每条贴原样 rc + 期望红组 vs 实际红组★)

| # | 构造 | 期望 |
|---|---|---|
| ① | ★**把 `V_DET_FS` 改回 3.3 ⇒ 满量端口径判据必须变红** ★ | ★**红** ★ |
| ② | ★**把取链规则改回「元组第一条」⇒ active_chain 判据必须变红 (不许悄悄换回错对象)** ★ | ★**红** ★ |
| ③ | ★**把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ 「ADC 输入悬空」必须变红** ★ | ★**红** ★ |
| ④ | ★**把 BAT_DET 的下臂从 60k 改成 100k ⇒ @4.2V 节点 = 2.1V > 1.98V abs-max ⇒ 过压判据必须变红** ★ | ★**红** ★ |
| ⑤ | ★**正向对照: 一切如常 ⇒ rc=0** ★ | ★**绿** (★证明闸不是恒红★) ★ |
| ⑥ | ★**(可选加分) 把 VBUS_DET_D 链的电阻改成 10k/10k ⇒ 静态电流判据必须变红 (数字脚口径也在判, 不是只判 ADC)** ★ | ★**红** ★ |

### ★B4 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py;                   echo "rc=$?"   # 期望 rc=0 (自测全过)
python3 SW/tools/check_demo_panel_spec.py;           echo "rc=$?"   # 期望 rc=0 (R1~R7)
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_step1_parts_spec.py;                echo "rc=$?"   # 期望 rc=0 (8/8)
python3 state/merge.py;                             echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                        echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                       echo "rc=$?"   # 期望 rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… / 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… 必须逐字节不变★★
```

### ★B5 · 硬件侧后果只「登记」, 不自己改 (★跨域纪律★)

★**如果 B1/B2 的结论指向硬件必须改 (★例: VBUS_DET_D 的 2.5V 电平超出该脚 abs-max ⇒ 要改分压比★)⇒**
- ★**登记一条 need 给 main (★`state/fragments/sw.yaml` 的 `needs_from` ⇒ `to: main`★)**: ★写清【哪一行网表 / 哪个值 / 为什么 / 代价 / 降级方案】★**
- ★**不许改 `HW/netlist_v1.csv` / `state/gen_netlist.py` / BOM / 脚表 / 板** ★ ⇒ ★**网表真源归 hw-lead + 老板那一趟「板只改一次」★**
- ★**同理: 若结论指向「脚表/网表里 ADC 脚的域标注要改」⇒ 登记 need, 不许自己改** ★

---

## ★⑤ 交卷物 (★4 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md` (★B1~B5 五块齐全 + 反向用例原样 rc★) ★
2. ★**口径对照页** (★一页表: 【量 / 现值 / 改后 / 依据出处 / 证据等级】⇒ 含「FS 3.3→1.8」与「判决对象 VBUS_DET_D→BAT_DET」两行★)
3. ★**改动的脚本** (`SW/tools/timing_check.py` 单文件 ⇒ ★**不许顺手改别的文件**) ★
4. ★**分片** `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写 ⇒ ★**写完 `grep` 校验 `iss291` 在不在★**) ★
   ★**★另外顺手做一件小事 (★只有你能做, main 不越界写你的分片★)★**: ★**把你在 `needs_from` 里登记的 need `iss285_sw_apply_after_iss283_verified` 标成已解决 (★`resolved_by: ISS-288`★)** ★ ⇒ ★**理由: ISS-283 已 verified + 补丁已落盘 (`SW/tools/timing_check.py` md5 `68c4becffe6bcd708e388dba9d18a505` = ISS-285 写死的期望值) ⇒ 该 need 的前提已满足★**

---

## ★⑥ 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表 / 脚表 / BOM 一个字节不许动★) · ★**不许改 `HW/` 任何文件** (★含 `state/gen_netlist.py` / `state/land_v_values.py` / `HW/check_netlist_selfconsistency.py`★) · ★**不许碰 `MECH/`** · ★**不许改 `SW/tools/check_demo_panel_spec.py` 的链头逻辑 (★ISS-275 已跑通的那条, 一个字节都不许动★)** · ★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★⑦ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss291/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★本单为什么现在派 (★main 15:5x 实查★)★**: ★**ISS-288 (timing_check 补丁落地) 已由 main 复验落 verified ⇒ sw-lead 名额空出来; hw-lead 名额被 ISS-289 占着 (★在飞★) · mech-lead 名额被 ISS-290 占着 (★在飞★) ⇒ ★**本单是此刻唯一能合法派出去的内部活**★ ★

★**★为什么这件事必须在「板只改一次」那一趟之前做完★**: ★**板是照着网表画的 ⇒ 网表 note 说 2.1% FS 而 SW 闸说 15% ⇒ 同一个分压链在两个地方差 7 倍 ⇒ 这一趟如果带着这条红去改板, 改完还是红的, 板就白改第二遍 ⇒ ⇒ **判据口径必须先钉死, 板才能一次改对**★ ★
