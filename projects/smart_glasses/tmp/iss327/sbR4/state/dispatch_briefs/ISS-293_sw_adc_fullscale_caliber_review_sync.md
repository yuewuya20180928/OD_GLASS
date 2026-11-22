# ISS-293 · sw-lead 任务书 —— ★★【SW_TIMING_REVIEW.md 的 ADC 段已过期: 满量程 3.3→1.8V + 判决对象 VBUS_DET_D→BAT_DET + BAT_DET 已从「全 DNP」变成「必装」⇒ 三处结论全部要订正】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 16:5x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-293 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · SW 侧复评文档口径收口 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零改网表真源** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动一份复评文档 + 一道闸, 不动板、不动网表★)

---

## ★⓪ 本单为什么现在派 (★main 16:2x~16:5x 本机实查盘面, 不抄任何交卷报告★)

★**ISS-291 (sw-lead · ADC 判决对象 + 满量程口径) 已由 main 16:4x 独立复验落 verified ⇒ sw-lead 名额空出来** ★

★**★但 main 复验时发现一件事: `SW/SW_TIMING_REVIEW.md` 这份复评文档【跟不上了】★★** ⇒ ★**它还停在【ISS-291 之前的旧口径】** ★ ⇒ ★**如果就这样留着, 下一个人照它做决策, 会照着一份已经被推翻的结论走** ★

★**⇒ 本单 = 把这份文档的 ADC 段按【盘面真值 + ISS-291 现行闸】订正, 并加一道闸防它再漂** ★

---

## ★① 病灶 (★main 16:4x 本机实读盘面, 逐条带行号★)

### ★①-1 · 【判决对象】文档说 ADC 链 = `VBUS_DET_D`, 现行闸说 = `BAT_DET`

| 位置 | 文档现状逐字 | 盘面/闸真值 |
|---|---|---|
| ★`SW/SW_TIMING_REVIEW.md` L38 (F6 行) ★ | ★「★**装机的是 `VBUS_DET_D` 链 (1M+1M+100nF) ⇒ 500kΩ / 50ms / 451ms / 0.50V (15.2%FS)** ★**不变**」★ | ★**判决对象已改成 `BAT_DET`** ★ (★`SW/tools/timing_check.py` L1397 `o["F4_adc_det"]` · 取链规则 = `by_landing_pin`★) ★**判决源 = SoM 脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` L39 `SARADC_VIN5` (1.8V 域) ⇒ 落点 `J_SOM_P1 pin38` = ADC 脚; 而 `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` = **数字脚**★** |
| ★L207 (判定表) ★ | ★「ADC 检测通道可用性 | ❌ 不通过 (500kΩ / 451ms / 15.2%FS) | ❌ **仍不通过, 数值一字不差** (装机链 = `VBUS_DET_D`)」★ | ★**现行闸 verdict = 全部 ✔ 通过** (★见 §①-3 的实跑输出★) ★ |
| ★L56 (汇总表) ★ | ★「ADC 检测通道 500kΩ / 451ms / 15.2%FS | 不变; ★新增 BAT_DET 链全 DNP | **仍成立 + 新增**」★ | ★**整行都要改** ★ |

### ★①-2 · 【满量程】文档隐含按 3.3V 算, 官方是 1.8V 域

★**★ISS-291 已把 `SW/tools/timing_check.py` 的 `DEVICE["V_DET_FS"]` 从 `3.3` 改成 `1.8` (★L81 现值逐字: `"V_DET_FS": 1.8,`★) ⇒ ★**文档里的 15.2%FS / 0.8057mV LSB 都是【按 3.3V 算出来的数】⇒ 现在全部作废** ★

★**★【官方出处 (★ISS-291 已查过并在闸里写了, 你直接引, 不要重查★)】** ★:
- ★脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` **L39** = `SARADC_VIN5` / **1.8V** 域 (★[官网]★) ★
- ★`HW/PCB/rk3572_datasheet_V1.1.txt` **L2454** = `SARADC_AVDD1V8 = 1.62 / 1.8 / 1.98V` · **L2864** = `Analog Input Range = AVSS18~AVDD18` (★[官网]★) ★
- ★⇒ 12bit ⇒ LSB = **0.439 mV** (★不是 3.3V 口径的 0.8057 mV★) ★

### ★①-3 · 【现值】现行闸的真值 (★main 16:4x 本机实跑 `python3 SW/tools/timing_check.py --only F4_adc_det` 的原样读数★)

★**★这就是本单要写进文档的【正确现值】—— 一字都不许自己编, 照抄下面的实跑读数★ ★**
```
active_chain        : BAT_DET          active_chain_pin : 38
active_chain_signal : SARADC_VIN5      active_chain_domain : 1.8V
chain_select_mode   : by_landing_pin
full_scale_v        : 1.8        adc_bits : 12      lsb_mv : 0.439
rth_ohm             : 37500.0    tau_ms  : 3.75
t_settle_to_half_lsb_ms : 33.791
leak_offset_v       : 0.0375    leak_offset_pct_fs : 2.1
standby_ua          : 26.25     supply_v : 4.2     node_v_at_supply : 1.575
node_max_abs_v      : 1.98      fs_utilization_pct : 87.5
criteria            : object_ok ✔ / fs_caliber_ok ✔ / settle_ok ✔ / leak_ok ✔ / node_ok ✔ / populated_ok ✔ ⇒ all_ok ✔
verdict             : ★判决对象 = BAT_DET 链 (网表 L186 ⇒ J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域) ⇒ 37500.0Ω / τ=3.75ms;
                      12bit (LSB=0.439mV, 满量程 1.8V) 需 33.8ms 建立 (红线 300.0ms ⇒ ✔); 1µA 漏电 ⇒ 0.0375V = 2.1% 满量程
                      (红线 0.4V ⇒ ✔; ★与网表 L182 note 写死的 2.1% FS 逐字对上 ⇒ ✔★); @4.2V 节点 1.575V ≤ abs-max 1.98V
                      ⇒ ✔ (FS 利用率 87.5%); ★老口径 (判 VBUS_DET_D + FS=3.3V) 报的那条红 = ★★假红★ ⇒ 已作废;
                      ★VBUS_DET_D 链改按【数字检测输入】口径单判 (见 F4D 段)★; ★BAT_DET 链三颗【已改成必装】
                      (V-3=E 落表后) ⇒ 电量检测分压在现网表上存在 (100k+60k+100nF ⇒ 37500.0Ω / τ=3.75ms)★
```
★**★注意 `verdict` 最后那句「老口径报的那条红 = 假红 ⇒ 已作废」★ ⇒ ★**文档 L207/L222 那两行「❌ 不通过」现在就是【一条假红被当成结论记着】⇒ 这是本单必须修的最重的一条★ ★**

### ★①-4 · 【BAT_DET 已不是 DNP】文档 §7-4 (L343) 整条 P0 已经过期

★**文档 L343 逐字**: ★「**电量分压整条 DNP, 但网还把 ADC 脚给了 SoC** | **L182/L183** `R_BAT_DET_1`/`R_BAT_DET_2` = **1M**, **dnp=DNP**; **L184/L185** `C_DET_BAT` = **100nF**, **dnp=DNP**」★

★**★盘面真值 (★main 16:4x 本机实读 `HW/netlist_v1.csv` L182~L186★)**:
| 行 | ref | value | dnp |
|---|---|---|---|
| ★L182 ★ | ★`R_BAT_DET_1` ★ | ★**100k ±1%** ★ (★**不是 1M**★) | ★**必装** ★ |
| ★L183 ★ | ★`R_BAT_DET_2` ★ | ★**60k ±1%** ★ | ★**必装** ★ |
| ★L184/L185 ★ | ★`C_DET_BAT` ★ | ★**100nF ±10%** ★ | ★**必装** ★ |
| ★L186 ★ | ★`NET_BAT_DET` → `J_SOM_P1 pin38` ★ | ★落点不变 ★ | ★**必装** ★ |

★**⇒ 文档 L343 那条【P0 需求侧阻塞】整条不成立了** ⇒ ★**且它引的「1M」这个数也错了 (真值 100k+60k) ⇒ 这是本单的第二重过期** ★
★★连带要修的 (★同一批, 一次做完★)★★: ★★L56 / L207 / L222 / L370 (CR-4) / L433 (`adc_det_sampling`) / L556 (★复现命令块里那句 `# F6: 电量链 (期望 R_BAT_DET_1/2 + C_DET_BAT 全 DNP ⇒ §7-4)`★) —— ★★这六处全都在 `SW/SW_TIMING_REVIEW.md` 这【一份文件】里 (★main 16:5x 实读确认: L556 那行是 §9 复现命令块里的一行注释, ★★不是★★ `SW/tools/timing_check.py` 里的★) ⇒ ★★所以本单只改【一份文档】, `SW/tools/timing_check.py` 一个字节都不许动★★ ★ ★★★★★

---

## ★② 根因一句话: 【ISS-291 把闸的判决源修对了, 但复评文档是【手工写的】⇒ 闸变了文档没跟着变 ⇒ 文档成了过期结论的载体】

★**⇒ 所以本单不能只是【改文档】⇒ 还得【加一道闸】把文档钉住, 否则下一轮落表/改链, 它又漂★**

---

## ★③ 要交的几件 (★每件都能独立验收★)

### ★B1 · 文档 ADC 段按真值订正 (★追加式 / 行内订正, ★**不许整段删掉重写**★)

★**★订正原则 (★本项目的铁律, 不许破★)★**: ★**老字保留, 在行内追加「★已订正 → 新值★」的标注** ★ ⇒ ★**历史判据要能追溯, 不许静默改数** ★

★**必改清单 (★main 16:4x 实读, 逐条带行号★)**:
| 行号 | 现状 | 订正成 |
|---|---|---|
| ★L38 (F6) ★ | 判决对象 `VBUS_DET_D` · 500kΩ · 451ms · 15.2%FS · 「BAT_DET 三颗全 DNP」 | ★**判决对象 = `BAT_DET` (pin38 / SARADC_VIN5 / 1.8V 域) · 37500.0Ω · τ=3.75ms · 建立 33.8ms · **2.1%FS** · LSB 0.439mV · 节点 1.575V ≤ 1.98V (FS 利用率 87.5%) · 全部判据 ✔ 通过** ★ · ★**「BAT_DET 三颗全 DNP」改为「★已改成必装 (V-3=E 落表后, 网表 L182/L183/L184 必装)★」** ★ |
| ★L56 (汇总) ★ | 同上摘要行 | ★**同上 (整行重写现值, 老句留痕)** ★ |
| ★L207 (判定表) ★ | 「❌ 不通过 (500kΩ/451ms/15.2%FS)」「❌ 仍不通过」 | ★**「✔ 通过 (37500.0Ω / 33.8ms / 2.1%FS / 节点 1.575V ≤ 1.98V)」+ ★**「★老口径 (判 VBUS_DET_D + FS=3.3V) 报的那条红 = 假红 ⇒ 已作废★」** ★ |
| ★L222 (判定表) ★ | 「电量 (BAT_DET) 通道是否存在 | ❌ **不存在 (三颗全 DNP)** ⇒ M7-R6 无硬件支撑」 | ★**「✔ 存在 (100k+60k+100nF 必装, 网表 L182~L186)」+ ★**「★★老结论『不存在 ⇒ M7-R6 无硬件支撑』已被 2026-11-17 09:58:16 落表 (V-3=E) 推翻★ ⇒ M7-R6 有硬件支撑」** ★ |
| ★L343 (§7-4 P0) ★ | 「电量分压整条 DNP」· 「1M」· 「P0 (需求侧阻塞)」 | ★**整条标为【已不成立 / 关闭】+ 写明「★真值 = 100k+60k+100nF 必装 (网表 L182~L186 实读) ⇒ 网表自相矛盾这条已被落表消除⇒ P0 解除★」★ ★**老字保留, 不许删** ★ |
| ★L370 (CR-4) ★ | 「判据改为『待 hw-lead 决策 (补装 or DNP)』」 | ★**改成「★已决策 = 补装 (V-3=E, 2026-11-17 09:58:16 落表) ⇒ 判据按 §2.6/§3.3 的 BAT_DET 现值★」★ ★**这条是 `SW/SW_REQUIREMENTS.md` M7-R6 的改动依据 ⇒ ★**你在交卷单里把「M7-R6 要不要同步改」写成【给 main 的建议】, 但 ★**不许自己改 `SW/SW_REQUIREMENTS.md`** (★需求真源 = PM 域★) ⇒ 登记 need 给 main ★ |
| ★L433 (`adc_det_sampling`) ★ | 「`BAT_DET链DNP-电量判据待定`」 | ★**改成「`BAT_DET 链已必装 ⇒ 电量判据按 BAT_DET 现值 (2.1%FS, 节点 1.575V)`」★ |
| ★L556 (★**复现命令块里那一行注释★**) ★ | ★「# F6: 电量链 (期望 R_BAT_DET_1/2 + C_DET_BAT 全 DNP ⇒ §7-4)」★ | ★**改成「# F6: 电量链 (★BAT_DET 三颗已必装 ⇒ 判据按 BAT_DET 链 37500Ω / 1.8V 域 ⇒ 见 F4_adc_det★)」★ ★★只许改这一行注释, 不许动旁边那条 `grep` 命令★★** |

★**★所有新写的数, 一律标证据等级 (`[官网]` / `[实测]` / `[推算]` / `[0数据]`)★ ⇒ ★**本文档现有行已经带这个口径 (★看 L38 行尾的 `[实测] + [推算] + [0数据]`★) ⇒ ★**照着做★**

### ★B2 · 一道新闸: `SW/SW_TIMING_REVIEW.md` 的 ADC 现值不许再漂 (★★防复发★)

★**★新建 `SW/tools/check_timing_review_adc_sync.py` (★交卷时它才存在★)** ⇒ ★**它要做的事只有一件: 【文档里写的 ADC 现值 == 闸的实跑读数】⇒ 不等 ⇒ 红** ★

★**判据 (★三条, 一条都不许放宽★)**:
1. ★**判决对象**: 文档 ADC 段必须出现 `BAT_DET` 作为装机链, 且**不许**再把 `VBUS_DET_D` 说成 ADC 链 (★它现在是数字检测输入★) ★
2. ★**满量程**: 文档必须写 `1.8` (★域★) / `LSB 0.439mV` / `2.1%FS` / `37500` (★Ω★) / `33.8ms` (★建立★), 且**不许**再出现 `15.2%FS` / `0.8057` / `500kΩ` 这三个【3.3V 口径的旧数】★
3. ★**BAT_DET 已必装**: 文档**不许**再出现「BAT_DET … 全 DNP」/「三颗全 DNP」/「不存在」这种说法 ⇒ ★**并且**必须出现「必装」★

★**★实现口径 (★别写复杂了★)**: ★**跑 `python3 SW/tools/timing_check.py --only F4_adc_det` 拿真值, 再跟文档文本做子串/正则对账** ★ ⇒ ★**不许自己重算一套 (★那会与闸脱钩★)★ ⇒ ★**读不到真值 ⇒ fail-closed 报错, 不许猜** ★

★**★反向用例 (★≥4 条, 每条贴原样 rc + 期望红组 vs 实际红组★)**:
| # | 构造 | 期望 |
|---|---|---|
| ★① ★ | ★**把文档里 `2.1%FS` 改回 `15.2%FS` ⇒ 新闸必须红** ★ | ★**红** ★ |
| ★② ★ | ★**把文档里 `BAT_DET` 改回 `VBUS_DET_D` ⇒ 新闸必须红** ★ | ★**红** ★ |
| ★③ ★ | ★**把文档里「必装」改回「全 DNP」⇒ 新闸必须红** ★ | ★**红** ★ |
| ★④ ★ | ★**正向对照: 一切如常 ⇒ 新闸 rc=0** ★ | ★**绿** ★ (★证明闸不是恒红★) ★ |

★**★反向用例必须在【沙盒副本】上做 (★真件一个字节不许碰★)★ ⇒ ★**照抄 `MECH/check_onepass_struct_crosscheck.py --selftest` 的沙盒做法 (★它有现成的沙盒副本 + `_edit_spec_json` 那套改副本的办法★)**

### ★B3 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/timing_check.py;                          echo "rc=$?"   # 期望 rc=0 (★SELFTEST 85/85★)
python3 SW/tools/timing_check.py --only F4_adc_det;        echo "rc=$?"   # 期望 rc=0
python3 SW/tools/timing_check.py --only F4D_usb_vbus_det;  echo "rc=$?"   # 期望 rc=0
python3 SW/tools/check_timing_review_adc_sync.py;          echo "rc=$?"   # ★★新建闸 ⇒ 期望 rc=0★★
python3 SW/tools/check_timing_review_adc_sync.py --selftest; echo "rc=$?" # ★★期望 rc=0 (★条数只许增不许减★)★★
python3 SW/tools/check_demo_panel_spec.py;                 echo "rc=$?"   # 期望 rc=0 (★ISS-275 那条链头不许动★)
python3 SW/tools/check_demo_panel_spec.py --selftest;      echo "rc=$?"   # 期望 rc=0
python3 state/merge.py;                                    echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                               echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                              echo "rc=$?"   # 期望 rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e13518c3c023fb178f91a0075 / .kicad_pro 3e504d2be83152e337949723e909be1b
# ★★网表 37f62ac3f0b81d92ca7d48fdea717f07 / 脚表 a4270120454aedf7a23c92cd8985c8a6
# ★★BOM 5d02bece9477ffce5fbe0193c7d5cce4 必须逐字节不变 ★★
# ★★板 mtime 仍须是 2026-11-06 07:07:17 (★md5 + mtime 双重证明★) ★★
```

★**★一条不许踩的坑 (★ISS-289 交卷单自己发现的副作用★)★**: ★**`HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 ⇒ 判「有没有偷改板」必须看【官方板那两个文件的 md5 + mtime】, 不能看目录★★ ★**

---

## ★④ 交卷物 (★4 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md` (★B1~B3 三块齐全 + 反向用例原样 rc + §①-3 那份实跑读数的来源说明★) ★
2. ★**改动的文档** `SW/SW_TIMING_REVIEW.md` (★B1 的 8 处订正, ★**追加式, 老字不删**★) ★
3. ★**新建的闸** `SW/tools/check_timing_review_adc_sync.py` (★B2 + `--selftest`★) ★
4. ★**分片** `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写 ⇒ ★**写完 `grep` 校验 `iss293` 在不在★**) ★
   ★**★另外顺手做一件小事 (★只有你能做, main 不越界写你的分片★)★**: ★**把你在 `needs_from` 里登记的 need `iss291_sw_vbus_det_d_digital_caliber` 的状态标成【已随本单闭合】(★它的内容 = VBUS_DET_D 改按数字检测输入口径单判 = ★**ISS-291 已落进 `SW/tools/timing_check.py` 的 F4D 段 + 本单的 B1 文档同步**★)⇒ ★**并把 `iss291_sw_do_not_apply_vbus_100k47k` 一并标好 (★它的意思是「★不许把 VBUS_DET_D 链改成 100k/47k★」= ★**本单没碰, 闸里那条反向用例还钉着**★)★ ⇒ ★**别自作主张把 need 关了, 在分片里写清依据就行★ ★**

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `SW/tools/timing_check.py`** (★★整个文件一个字节都不许动 — 它是 ISS-291 刚复验落 verified 的定版闸: `V_DET_FS=1.8` + 判决对象=`BAT_DET` + 85/85 自测 + 反向用例 REV-12~REV-17 已钉死 ★**main 16:5x 补充★★) ★ · ★**不许改 `SW/tools/check_demo_panel_spec.py` 的链头逻辑** (★ISS-275 已跑通的那条, 一个字节都不许动★) ★ · ★**不许改 `SW/SW_REQUIREMENTS.md`** (★需求真源 = PM 域 ⇒ 登记 need 给 main★) ★ · ★**不许碰 `HW/` 与 `MECH/` 的文件与分片** ★ · ★**零外发** ★ · ★**不替老板拍板** (★M7-R6 要不要同步改 = 建议交 main★) · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

★**★本单零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**不许发任何邮件/询价/问询/采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ★**

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss293/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★这项目的老坑, 一条都不许再踩★**:
1. ★**写分片必须用 `state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)** ★
2. ★**只写本任务允许的文件, 不碰别人的** (★`state/fragments/hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节都不许碰★) ★
3. ★**文档订正必须追加式 (★老字不许删★)** —— ★**本项目已被「静默改数」坑过 6 跳 (H-1 重锚)★ ⇒ ★**改数必须留痕 (★谁改的 / 哪个单号 / 新旧值 / 依据★)★★ ★
4. ★**不许为了让闸绿而改闸 / 放宽判据** ★
5. ★**不许自签 issue_log** ★

★**★为什么这一单必须在「板只改一次」那一趟之前做完★**: ★**文档 = 下一个人做决策的依据 ⇒ 文档里那条「ADC 不通过 (500kΩ/451ms/15.2%FS)」是【假红被当成结论记着】⇒ 那一趟要是照着它判「ADC 链不合格 ⇒ 改板」⇒ ⇒ ★**板白改第二遍**★ ⇒ ⇒ ★**文档口径必须先钉死, 板才能一次改对** ★
