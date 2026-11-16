# ISS-239 交接单 · TPS7A20 族 7 颗 LDO 引脚功能名串号 + U_LDO_S28 缺 EN 脚

| | |
|---|---|
| **交出方** | hw-lead (硬件总工) 🔧 |
| **接收方** | main (项目总工) |
| **日期** | 2026-11-16 |
| **单号** | ISS-239 (第 2 次重派 · ★第 1 轮死于上游模型集群过载 `overloaded_error (2064)` / `unknown error, 715`, **零写盘** ⇒ 本单从零开始★) |
| **性质** | ★**内部活** · 不是 PCB 布线/布局类 · 不是老板级拍板 · **零外发** |
| **本轮产出** | `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` (新建) · `HW/check_pin_function_labels.py` (新建) · 本单 (新建) · `state/fragments/hw.yaml` (只加不改) |
| **真盘改动** | ★**0 个受保护文件被改** ★ (5 个 md5 逐字节未变, §B2-8) · ★**本单不落任何表** ★ |

---

## B1 · 结论摘要

**一句话**: ★**脚表 `HW/netlist_v1_pins.csv` 里 7 颗 TPS7A20 的 pin4/pin5 共 14 处贴了别的脚的功能名 (串号), 另有 `U_LDO_S28` 整颗缺 pin3(EN) 脚 ⇒ 共 15 处缺陷; 根因是【四层叠加】, 改法要同时动 4 个文件, 只改一个都修不干净。** ★

**详细结论 (5 条)**:

1. **★病灶一 (脚表层)**: `state/gen_netlist_pins.py` **L142~L147** 的元信息索引键是 **`(ref, net)` 且首行获胜** ⇒ `HW/netlist_v1.csv` 里 `(U_LDO_*, GND)` 有两行 (pin2 行 + pin5 行) ⇒ **pin5 继承了 pin2 的 `"GND (pin2)"`, 自己的 `"散热焊盘 (pin5, EP)"` 被丢掉**。★**实测**: `(ref,net)` ≥2 行的组 = **36 组** (自己重扫)。
2. **★病灶二 (脚表层)**: 同文件 **L218~L221**, `meta.get((ref, .net 的网名))` 落空时**兜底取"该 ref 的第一行"**。★**.net 的网名是 `BOARD_5V`, CSV 的 net 列写的是 `SYS_PCB`** ⇒ 落空 ⇒ 6 颗 LDO 兜底到 **pin3 行** ⇒ **pin4 继承了 `"EN (pin3)"`**; `U_LDO_S28` 因为没有 pin3 行 ⇒ 兜底到 **pin2 行** ⇒ **pin4 继承了 `"GND (pin2)"`**。★**这解释了第 1 轮"同 ref 同 net 复制"假设解释不了的那一半 —— 两处缺陷叠加且互相掩盖。**
3. **★病灶三 (网表层)**: `state/gen_netlist.py` **L683~L689 / L690~L696**, TPS7A20 的 pin1 行写的是**轨电压** ("2.8V")、pin4 行写的是**轨描述** ("5.0V (F13: 由 CARRIER_BOARD_EN 门控)") ⇒ ★**网表本身就没写脚功能名** ⇒ ★**即使把病灶一/二全修好, 脚表 pin4 也只会变成轨描述, 仍然不是功能名** ⇒ ★**三层必须一起改**。
4. **★病灶四 (第 0 层·产线风险)**: `state/gen_kicad_net.py` **L144~L162** 用"该 ref 的第一行"当器件 Value ⇒ ★**`.net` 里 7 颗 LDO 的 `(comp … (value …))` = `"EN (pin3)"` / `"GND (pin2)"`; 板上 7 颗 LDO 的 `Value` 属性实测也是这个** ⇒ ★**贴片程序按 Value 匹配元件 ⇒ 板上没有"TPS7A20-33"这个料号** ★ (★`HW/BOM_v1.csv` L215 的 memo 早就写了这件事, 根因一直没修★)。
5. **★`note` 列也一起串了 (同一根因, 同一处修)**: 实测 6 颗 LDO 的 `pin4` 行的 `note` 逐字复制了 `pin3` 行的 EN/P0 文案, `pin5` 行的 `note` 复制了 `pin2` 行的 GND 文案, `U_LDO_S28.pin4` 的 note 也是 pin2 的 GND 文案 ⇒ ★**`value` 与 `note` 是同一份 metadata 的两个字段 ⇒ §改法 F3 一改就一起修好, 不需额外改动** ★ ⇒ ★**但评审对图/脚表审计时读 pin4 的 note 会读到"这是 EN 脚"的文案 ⇒ 比 `value` 更容易误导人** ★
6. **★为什么 `check_sch_pinfull.py` 的 584=584 抓不到**: 原理图符号脚数与脚表脚数**同源派生** (都由 `state/gen_netlist.py` 那一族生成) ⇒ **一起错就一起过**; 而且它量的是**数量**不是**语义** ⇒ pin4 写 "EN (pin3)" 还是 "IN (pin4)" 都算 1 个脚。⇒ ★**新闸必须查【脚的功能名】**, 这就是本单新建 `HW/check_pin_function_labels.py` 的理由。

**★交付三件套**:
- `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` ⇒ **35 行逐脚对账表 + 根因定性 (带行号) + 38 组同网多脚逐组定性 + 改法映射 v1 (含 A/B 两案) + 落表时机与 H-1 重锚影响面 + 官方出处 + 证据分级**
- `HW/check_pin_function_labels.py` ⇒ **独立机器门禁, 4 类检查 + 三模式 (默认 rc=1 / `--expect-known` rc=0 / `--selftest` rc=0 10/10)**
- `state/fragments/hw.yaml` ⇒ 只加不改

---

## B2 · 验收标准自评 (★逐条 通过 / 不通过 / 未验★)

| # | 验收项 (派活单原文口径) | 自评 | 实测证据 |
|---|---|---|---|
| 1 | `python3 HW/check_pin_function_labels.py` ⇒ **rc=1** | ✅ **通过** | 实跑 rc=1; 首行 = `★当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿★` |
| 2 | 上条点名的清单 = **14 处串号 (7×pin4+pin5) + `U_LDO_S28` 缺 pin3** (多报/少报都不通过) | ✅ **通过** | 实算**恰好 15 条**: 14 条 `WRONG_FUNCTION` + 1 条 `MISSING_PIN`; 串号集合 = 7 颗 × {pin4, pin5}, **零多报零少报** (与 §B1-1 的 35 行对账表逐条一致) |
| 3 | `--expect-known` ⇒ **rc=0** | ✅ **通过** | 实跑 rc=0, 打印 `✅ 实算清单与冻结快照逐条一致 (15/15)` |
| 4 | `--selftest` ⇒ **rc=0** 且 **≥6/6** | ✅ **通过 (10/10)** | 实跑 rc=0; **T1~T10**, 每条**自证改到了目标** (T1 还额外断言"未改动的合成样本 = 0 缺陷") |
| 5 | `python3 HW/check_step1_parts_spec.py` ⇒ rc=0 (C1~C8 8/8) · `--selftest` rc=0 (T1~T8) | ✅ **通过** | 实跑 rc=0 / rc=0; ★**本单没碰这个脚本** ★ |
| 6 | `state/check_sch_pinfull.py` rc=0 (584=584) · `check_netlist.py` rc=0 · `check_netlist_pins.py` rc=0 · `check_sch_erc.py` rc=0 | ✅ **通过** | 实跑全部 rc=0; ★**本单没改脚数基线** ★ |
| 7 | `state/merge.py` rc=0 · `state/gate_check.py` rc=0 且 【Q1】**18/18** | ✅ **通过** | 实跑 rc=0 / rc=0, Q1 = 18/18 |
| 8 | 5 个受保护文件 md5 与 `34132f7e… / b21b743a… / c195a117… / 611b869e… / 3e504d2b…` 逐字节一致 | ✅ **通过** | 本单开工前 + 交卷前各 `md5sum` 一次, **逐字节一致** (★自己先复核过再报★) |
| 9 | ① 35 行逐脚对账表 | ✅ **通过** | `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` §2 (35 行, 每行带官方功能名 + 出处 + 证据等级) |
| 10 | ② 根因定性 (查到代码行) + 证明/推翻"同 (ref,net) 复制"假设 | ✅ **通过** | §3: ★**假设只解释了一半** ★ ⇒ 病根 = **缺陷①(索引首行获胜) + 缺陷②(兜底取器件首行) + 缺陷③(CSV 层没写功能名) + 缺陷④(.net/板 Value)**, 每条带文件+行号+可复现最小例子 |
| 11 | ②附 同网多脚清单逐组定性 | ✅ **通过 (★与派活单数字的差额已逐组对清·不是事实分歧★)** | ★**自己重扫**: 脚表 (ref,net) ≥2 脚 = **38 组 / 16 颗器件**; 网表 CSV (ref,net) ≥2 行 = **36 组** (排除伪 ref = 25 组 / 17 颗) ⇒ ★**派活单的 26 组 / 14 颗是脚表侧的一个不完整子集, 差 12 组, 逐组可解释**: `J_USB_C` 4 组 (名单里没这颗器件) + `U_SUPV` 1 组 (名单里没这颗器件) + `U_CHG` 1 组 (少 `SYS_CHG`) + `U_LDO_*` 各 1 组 (少 `BOARD_5V` 组) ⇒ ★★★**main 漏掉的 6 组, 恰恰就是 pin4 串号所在的那 6 组** ★★★ ⇒ 38 组逐组判: **只有 13 组 (7 颗 TPS7A20) 是语义错, 其余 25 组语义无害或措辞差** |
| 12 | ②附 解释 "584=584 为什么抓不到" | ✅ **通过** | §3.5 (同源派生 + 量数量不量语义) |
| 13 | ③ 改法映射 v1 (逐行: 改哪个文件哪一行 → 改成什么 → 依据 → 改完长什么样) | ✅ **通过** | §4.0 四个文件 F1~F4 + 行号; §4.1 改完 35 行实跑输出 |
| 13a | ③附 U_LDO_S28 补 pin3 的 **A/B 两案 + 各给代价, 不代拍** | ✅ **通过** | §4.2 A/B 对照表 (9 行代价对比, 含**板/门禁/脚数基线/一致性风险** 四类代价) |
| 14 | ③附 落表影响面 (md5 变 ⇒ 两个 H-1 锚点要重锚) + **本轮不动别人的台账** | ✅ **通过** | §7.2 点名 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 与 `SW/SW_MD5_BASELINE_LEDGER.md` §1; ★**本单没碰 MECH/ 与 SW/ 任何文件** ★ |
| 15 | ③附 补 EN 脚 ⇒ 脚表 584→585 ⇒ 脚数基线会变 (本单只写清楚, 不改) | ✅ **通过** | §7.3 (A 案 584→585 / B 案不变); ★**本单没改 `state/check_sch_pinfull.py`** ★ |
| 16 | ④ 门禁: 4 类检查 (逐脚对账 / 同器件功能名不重复且限死 IC / pinout 不许改软 / md5 未变) | ✅ **通过** | 脚本 §1 判据段; ★**② 限死 IC 是承重的** (实测: 放宽后 `CONN_CAM` 13 + `CONN_LIGHT` 8 + `J_SOM_P3` 12 + `J_USB_C` 4 = 37 脚会误报) ★ |
| 17 | ④ 门禁: 三模式 (默认 rc=1 + 首行声明 + `--expect-known` rc=0 多/少/变一条都红 + `--selftest` rc=0 ≥6 反向用例且每条自证) | ✅ **通过** | §6.2 / §6.3; ★**10 条反向用例**; ★**T1 额外断言"未改动样本 = 0 缺陷" ⇒ 证明红来自这次改动** ★ |
| 18 | ④ 门禁: 不许把判据放宽成"表里没有 IN 就当没有 IN" | ✅ **通过** | 脚本 §1 判据段: ★**底线三条** (5 脚必须齐全 / 声明了功能名的必须逐脚对得上 / 引脚号不得指向别的脚) ★ ⇒ "没声明"的只记 `NO_FUNCTION` 提示并逐条打印, 不掩盖 |
| 19 | ⑤ 交付物 1: `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` | ✅ **通过** | 新建 |
| 20 | ⑤ 交付物 2: `HW/check_pin_function_labels.py` | ✅ **通过** | 新建 |
| 21 | ⑤ 交付物 3: 本交接单 (B1~B6) | ✅ **通过** | 本文件 |
| 22 | ⑤ 交付物 4: `state/fragments/hw.yaml` (只加不改) | ✅ **通过** | 走 `state/frag_write.py` 原子写, ★**只 `--add-artifact` / `--add-claim` / `--add-need`, 没删改别人的 key** ★ |
| 23 | ⑤ 交付物 5 (可选): `/tmp` 副本实跑, 贴"改后 35 行" | ✅ **通过** | ★**`cp -a` 整棵树** (不是只 cp 几个文件) 到 `/tmp/iss239_rehearsal/smart_glasses` ★ ⇒ §5 实跑输出; ★**真盘未动** ★ |
| 24 | ⑦ 边界: 零外发 | ✅ **通过** | ★**本单没发任何邮件/消息/外网提交** ★ (官方资料自己上 ti.com 查, 每条标 [官网]/[实测]/[推算]/[0数据]) |
| 25 | ⑦ 边界: 实物 [实测] = 0 条 (板不在本机) | ✅ **通过** | ★**本单所有 [实测] 都是对仓库内文件的读/跑, 不是对实物板的测量** ★ ⇒ 板封装焊盘数的判定来自**板文件文本**, 标注为 [实测·文件] |
| 26 | ⑦ 边界: 没碰 PCB 布线/布局/板框 | ✅ **通过** | ★**只读过 `HW/PCB/demo_mainboard.kicad_pcb` 的 footprint/pad 文本, 没写** ★ |
| 27 | ⑦ 边界: 没改 `PROJECT_TRACKER.md` §0 · 没改 `state/issue_log.yaml` (verify_by = main) | ✅ **通过** | ★**两个文件本单一行没碰** ★ |
| 28 | ⑦ 边界: 没写别人的分片 · 没碰 `SW/` 与 `MECH/` 任何文件 | ✅ **通过** | ★**只写了 `state/fragments/hw.yaml`** ★ (hw-lead 自己的分片) |
| 29 | ⑦ 边界: 不许代拍 V-2 / V-3 / V-4 · 本单不落任何 V 值 | ✅ **通过** | ★**没跑 `state/land_v_values.py`, 没落任何 V 值** ★ |
| 30 | ⑦ 交卷前更正 ISS-237 的那句错话 | ✅ **通过** | 见 §B5 第 1 条 |

**★未验 / 本单做不了的 (如实写, 不装)**:

| 项 | 状态 | 原因 |
|---|---|---|
| 板封装补 pad3 的**具体几何** (X2SON 真实焊盘排布 / 散热焊盘尺寸 / 是否与现有布线冲突) | **未验** | ★**这是板域 (布线/布局) 的活, 本单不许碰** ★ ⇒ 若 main 选 A 案, 必须开板域单 |
| `state/check_pcb_nets.py` 的**实跑 rc** | **未验 (但后果已定)** | ★**本机 `import pcbnew` 加载不了** (缺 `libwx_gtk3u_gl-3.3.so.2`) ⇒ 我**自己实现了一份焊盘级比对** (口径抄它的判据说明) 实跑 ⇒ ★**A 案下 `U_LDO_S28` 恰好 1 颗不等价** ⇒ 该闸会红 ⇒ 后果确定, 但**它自己的 rc 我没跑出来** ⇒ 标 [实测·自实现] |
| 落表后的**最终状态** (脚表 585 行 / 闸转绿) | **部分验证** | ★**已在 `/tmp` 副本实跑**: 默认 rc=0 / `--expect-known` rc=0 / `--selftest` rc=0 (10/10) ⇒ ★**fix-point 稳定, 落表后 selftest 不会变红** ★ |

---

## B3 · 证据分级

| 结论 | 等级 | 出处 |
|---|---|---|
| TPS7A20 X2SON 官方 pinout = **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(EP)** | **[官方]** | TI datasheet **SBVS338H (2020-03 / rev 2024-07)** §4 *Pin Configuration and Functions* → 表 *Pin Functions: X2SON, SOT-23*; ★自己去 ti.com 下载 `https://www.ti.com/lit/ds/symlink/tps7a20.pdf` (md5 `24616a278e110d71b3a84f8e311ab5c3`) 复核** ★ |
| EN 内部 500 kΩ 下拉 · VEN(LOW)≤0.3 V 关断 / VEN(HI)≥0.9 V 使能 | **[官方]** | 同上 §5.8 |
| 封装 DQN0004A (X2SON 1.0×1.0 mm) | **[官方]** | 同上 §7 |
| 仓库两处同口径记录 | **[实测]** | `HW/CORE_MODULE_SELECTION.md` **L15** · `HW/POWER_RAIL_SPEC.md` **L41** (与官网四方一致, 无冲突) |
| 脚表 15 处缺陷 (14 串号 + 1 缺脚) | **[实测]** | `HW/check_pin_function_labels.py` 实算, 与 35 行对账表逐条一致 |
| 根因 4 条 (索引键 / 兜底 / CSV 层 / `.net` 层) | **[实测]** | 每条给了文件+行号+可复现最小例子; `/tmp` 副本实跑验证 |
| 候选① (全域 (ref,pin) 索引) 影响 **142 脚 / 31 颗器件且多数变差** | **[实测]** | `/tmp` 副本实跑 diff (`CONN_CAM.pin11`: `'GND'`→`'100nF ±10%'`) |
| 候选③ 影响 **脚表 19 脚 (18 改 + 1 新) / 584→585 行** | **[实测]** | `/tmp` 副本实跑 diff |
| 候选③ `.net` comp value 影响 **9 / 218 个器件** (7 LDO + 2 DC-DC, 全是变好) | **[实测]** | 同上 |
| 候选③ **BOM 0 行变化** | **[实测]** | 同上 (全表 diff = 0) |
| 改 pin1 会炸 BOM (value→`OUT (pin1)`, type→`RAIL`, 采购状态→"待分类") | **[实测]** | ★**副本实跑踩到后已撤回** ★ ⇒ 写进改法映射当"不要改"的依据 |
| A 案会拉红板↔网表焊盘级等价 (`U_LDO_S28` 缺 pad3, 其余 6 颗等价) | **[实测]** | 副本实跑 + 自实现焊盘级比对 (7 颗里恰好 1 颗不等价) |
| 板上 7 颗 LDO 的 `Value` 属性 = `EN (pin3)` / `GND (pin2)` | **[实测]** | `HW/PCB/demo_mainboard.kicad_pcb` 逐 footprint 解析 |
| `U_LDO_S28` 板上封装只有 pads 1,2,4,5 (无 pad3) | **[实测]** | 同上 |
| `check_netlist.py` / `check_netlist_pins.py` 不碰板 | **[实测]** | grep 源码: 无 `kicad_pcb` / `pad` / `footprint` |
| `check_sch_pinfull.py` 抓不到 = 同源派生 + 量数量不量语义 | **[实测]** | 读脚本全文 + 读 `state/gen_netlist*.py` 确认派生链 |
| 脚表 (ref,net) ≥2 脚 = **38 组 / 16 颗**; 网表 CSV ≥2 行 = **36 组** | **[实测]** | 自己重扫, **不照抄派活单的"26 组 / 14 颗"** |
| 候选 A / B 的**取舍** | **[推算]** | 代价已全部实测列出; ★**取舍留给 main, 本单不代拍** ★ |
| 板封装补 pad3 的几何可行性 | **[0数据]** | 本单**未做板几何核算** ⇒ 选 A 案须开板域单 |
| `state/check_pcb_nets.py` 自己的 rc | **[0数据]** | 本机 `import pcbnew` 失败 ⇒ 跑不出来 (后果已由自实现比对确定) |
| 实物板上的任何电气行为 | **[0数据]** | ★**板不在本机 ⇒ 本单没有任何一条实物测量** ★ |

---

## B4 · 接口取值声明 (interface_claims)

★**本单不向任何其他模块提接口取值请求** —— 本单是**只读 + 新建独立文件**的内部活, 没有跨模块接口变更。

| 接口 | 取值 | 声明 |
|---|---|---|
| 7 颗 TPS7A20 的官方 pinout | `1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(EP)` | ★**本单把这条写死在新闸里 + 交叉核对仓库两处原文** ⇒ **谁改这条, 闸会红** ⇒ 下游 (SW/mech) 若另有 pinout 口径, 走闸去对, 不要各自维护一份 ★ |
| `U_LDO_S28.pin3` 的存在性 | **待 main 拍板 (A/B 两案)** | ★**本单只给代价, 不代拍** ⇒ **在 main 拍板前, 下游不得按"5 脚齐全"去布线/备料** ★ |
| 板↔网表焊盘级等价 | A 案下 `U_LDO_S28` 不等价 (缺 pad3) | ⇒ **若 main 选 A, 板域必须同步排上补 pad3** |
| `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 / `SW/SW_MD5_BASELINE_LEDGER.md` §1 | md5 会变 ⇒ 要 H-1 重锚 | ★**本单只点名, 不动手** (那两份是别人的文件) ★ |
| 脚数基线 `584` | A 案 → 585 | ⇒ **属于落表批次; 本单不改 `state/check_sch_pinfull.py`** |
| 门禁 `HW/check_pin_function_labels.py` 的三模式语义 | 默认 rc=1 / `--expect-known` rc=0 / `--selftest` rc=0 | ⇒ **落表批次必须同步更新脚本里的 `PROTECTED_MD5` (5 个) 与 `KNOWN_DEFECTS` 快照 (+其 SHA256)** ⇒ **不改就会红, 这是设计意图** |

---

## B5 · 未决项与卡点

1. ★★**ISS-237 交卷单的错话更正 (main 要求的)** ★★
   ★**ISS-237 交卷单 M4 那句「网表里 7 颗 TPS7A20 的 EN 脚一行都没有 ⇒ 全表关断」经 main 实测不成立** —— main 2026-11-16 10:5x~11:0x 自己逐行实测: 网表 **L102 / L112 / L122 / L132 / L142 / L152 都有 EN 行** ⇒ **6/7 有 EN**, 只有 `U_LDO_S28` (因 `state/gen_netlist.py` **L710** 的 `if ref != "U_LDO_S28":` 例外) 没有。
   ⇒ ★**真病灶不是"全表关断", 而是本单这两条**: ① **14 处引脚功能名串号** (pin4/pin5) + ② **`U_LDO_S28` 缺 pin3(EN) 脚**。
   ⇒ ★★**顺带把派活单里的【根因假设 ⑤】也一并订正 (★不是事实分歧, 是假设的统计口径不够★)** ★★
   派活单假设 ⑤ 说「同一个 (ref, net) 上有两行 (pin3 的 EN 行 + pin4 的 IN 行; pin2 的 GND 行 + pin5 的 EP 行) ⇒ value/note 被复制给同网的每一个脚」。
   ★**实测: 这个假设只对 pin5 成立, 对 pin4 不成立** —— 因为 ★**pin3 行与 pin4 行在 `HW/netlist_v1.csv` 里的 `ref` 列根本不同** (pin3 行 `ref=U_LDO_S18B` / pin4 行 `ref=RAIL_BOARD_5V`) ⇒ ★**它们压根不是 (ref,net) 碰撞** ⇒ ★**这正是"那两点互相矛盾"的真相: pin5 = 真复制 ((ref,net) 首行获胜), pin4 = 假复制 (网名别名对不上 ⇒ 查不到 ⇒ 兜底取器件首行) ⇒ 两个不同机制, 必须分开修** ★
   ⇒ ★**派活单 26 组名单漏掉的 6 个 `BOARD_5V` 组, 恰恰就是 pin4 串号所在的那 6 组** ⇒ ★**按那个名单去查, 永远查不到 pin4** ★
   ⇒ ★**补充一条本单新查到、ISS-237 也没提的**: ★**"缺 EN ⇒ 关断" 的后果只在 `U_LDO_S28` 一颗上成立, 而且那颗是 DNP (camera 模组自带稳压) ⇒ 实际不装 ⇒ 不构成"整板不上电"的风险** ⇒ ★**但它一旦要装, 板上没有 pad3 且 EN 悬空 (内部 500 kΩ 下拉 ⇒ 关断) ⇒ 这条必须写进 BOM/文档** ★。

2. ★★**卡点 1 (需 main 拍板): `U_LDO_S28.pin3` 走 A 案还是 B 案?** (§4.2)
   - **A 案** (去掉 `state/gen_netlist.py` L710 的例外): 脚表 584→585, 5 脚齐全; ★**代价: 板上 `U_LDO_S28` 没有 pad3 ⇒ 板↔网表焊盘级等价变红 ⇒ 必须同时动板 (板域单) + 脚数基线 584→585 + 原理图重生成** ★
   - **B 案** (保持不发): 脚表仍 584, 板一行不动; ★**代价: 闸必须给 `U_LDO_S28.pin3` 开一条【带出处的显式豁免】⇒ "5 脚齐全"这条底线会开一条缝 ⇒ 豁免必须写进闸源码 + 收口文档 + BOM memo, 不许只在聊天里说一句** ★
   - ⇒ ★**hw-lead 倾向 B** (为颗 DNP 器件动板, 成本花在用不上的地方; A 案把落表批次风险面直接翻倍), ★**但不代拍** ★

3. ★**卡点 2 (需 main 拍板): `pin1` 要不要改成 `OUT (pin1)`?** ⇒ ★**建议不改** (★**实测会炸 BOM**: 脚表 pin1 行的 `type` 从 `IC` 变 `RAIL` ⇒ `state/gen_bom.py::_pick_value` (L143) 靠【`type != 'NET'` 的那行】认器件本体行 ⇒ BOM 7 颗 LDO 的 value/type/采购状态全坏 ⇒ 要改就得同时改 `gen_bom.py` 的口径 ⇒ **建议单独开单, 别混进 ISS-239 落表批次**) ★

4. ★**卡点 3 (需 main 排期 + 通知 owner): 落表批次的 owner 与顺序**
   - 改 `state/gen_netlist.py` (F1 L690~696 / F2 L710) · `state/gen_netlist_pins.py` (F3 L142~147 + L210~221) · `state/gen_kicad_net.py` (F4 L149~162) —— ★**三个都是受保护脚本, 本单只读没改** ★
   - 重跑生成链 `gen_netlist.py` → `gen_kicad_net.py` → `gen_netlist_pins.py` → `gen_bom.py`
   - 同步更新 `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` (5 个) + `KNOWN_DEFECTS` 快照 + 其 SHA256
   - ★**H-1 重锚**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 (mech-lead) · `SW/SW_MD5_BASELINE_LEDGER.md` §1 (sw-lead) ⇒ ★**本单只点名, 两份台账一个字没碰** ★
   - ⇒ **needs → main**

5. ★**卡点 4 (选 A 案才需要): 板域单** ⇒ `U_LDO_S28` 封装补 pad3 的几何核算 + 布线/DRC 复跑 ⇒ **本单不做, 本单也没碰板文件** ★

---

## B6 · 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── ① 门禁三模式 (★核心交付★) ─────────────────────────────
python3 HW/check_pin_function_labels.py                 # ⇒ rc=1 ; 首行写明"rc=1 属预期"
                                                          #   缺陷清单 15 条 (14 串号 + 1 缺脚)
python3 HW/check_pin_function_labels.py --expect-known   # ⇒ rc=0 (15/15 逐条一致)
python3 HW/check_pin_function_labels.py --selftest        # ⇒ rc=0 (10/10 反向用例)

# ── ② 35 行逐脚对账 (人读) ────────────────────────────────
python3 HW/check_pin_function_labels.py | sed -n '5,16p'
python3 HW/check_pin_function_labels.py | grep -A40 "缺陷清单"

# ── ③ 根因: 三处代码行 (★逐条可核★) ───────────────────────
sed -n '142,147p' state/gen_netlist_pins.py      # 索引键 (ref,net) + 首行获胜
sed -n '210,221p' state/gen_netlist_pins.py      # 兜底取"该 ref 的第一行"
sed -n '683,696p' state/gen_netlist.py           # pin1 行写轨电压 / pin4 行写轨描述
sed -n '705,721p' state/gen_netlist.py           # EN 例外 (L710) + pin2/pin5 行
sed -n '144,162p' state/gen_kicad_net.py         # 器件 Value 取"该 ref 第一行"

# ── ④ 网表 CSV 层那 7 颗的 pin1/pin4/pin5 行 (★第二层★) ──
grep -n "U_LDO_" HW/netlist_v1.csv | grep -E "pin[12345]"
grep -n "U_LDO_" HW/netlist_v1.csv | sed -n '1,12p'   # L91/L92/L93/L94/L95 (U_LDO_S28 那 5 行)

# ── ⑤ 第 0 层: .net / 板上的 Value 属性 (★产线风险★) ──────
grep -o '(comp (ref "U_LDO_[^"]*") (value "[^"]*")' HW/netlist_v1.net
grep -n 'property "Value"' HW/PCB/demo_mainboard.kicad_pcb | head -0   # 见收口文档 §3.4

# ── ⑥ 官方出处 (自己上 ti.com 查, 不发信) ──────────────────
#   https://www.ti.com/lit/ds/symlink/tps7a20.pdf   (SBVS338H, §4 Pin Functions: X2SON)
grep -n "1=OUT" HW/CORE_MODULE_SELECTION.md HW/POWER_RAIL_SPEC.md

# ── ⑦ 同网多脚清单 (自己重扫) ────────────────────────────
python3 - <<'EOF'
import csv, re
from collections import defaultdict
rows=list(csv.DictReader(open("HW/netlist_v1_pins.csv",encoding="utf-8")))
g=defaultdict(list)
for r in rows: g[(r["ref"],r["net"])].append(r["pin"])
multi={k:v for k,v in g.items() if len(v)>=2}
print("脚表 (ref,net) >=2 脚 的组数 =", len(multi), "/ 器件数 =", len(set(k[0] for k in multi)))
EOF

# ── ⑧ 全部验收门禁 (★本单交卷时的实跑口径★) ───────────────
python3 HW/check_step1_parts_spec.py && python3 HW/check_step1_parts_spec.py --selftest
python3 state/check_sch_pinfull.py && python3 state/check_netlist.py \
  && python3 state/check_netlist_pins.py && python3 state/check_sch_erc.py
python3 state/merge.py && python3 state/gate_check.py     # ⇒ 【Q1】18/18

# ── ⑨ 受保护文件 md5 (★必须逐字节不变★) ────────────────────
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 期望:
# 34132f7e40a241e1fae1476be0eafbd5  HW/netlist_v1.csv
# b21b743a7702d30729f0d653c15392df  HW/netlist_v1_pins.csv
# c195a117ff17490d4d1e1a5b8f1995a7  HW/BOM_v1.csv
# 611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
# 3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro

# ── ⑩ /tmp 副本实跑 (★整棵树 cp -a★; 真盘不动) ──────────────
#   副本已留在 /tmp/iss239_rehearsal/smart_glasses
#   里面已应用 F1+F3+F4 (+A 案的 F2), 重生成链已跑过
python3 /tmp/iss239_rehearsal/smart_glasses/HW/check_pin_function_labels.py --selftest
```

---

### 附: 交付物清单

| 文件 | 动作 | 说明 |
|---|---|---|
| `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` | **新建** | 35 行对账 + 根因 + 38 组同网多脚定性 + 改法映射 v1 (A/B) + 落表影响面 + 出处 + 证据分级 |
| `HW/check_pin_function_labels.py` | **新建** | 独立门禁, 4 类检查 + 3 模式 + 10 条反向用例 |
| `HANDOFF/2026-11-16_hw-lead_ISS239_TPS7A20引脚功能名串号与缺EN脚.md` | **新建** | 本单 (B1~B6) |
| `state/fragments/hw.yaml` | **追加** | 只 `--add-artifact` / `--add-claim` / `--add-need`, ★**没删改别人的 key** ★ |

★**本单没碰**: `state/gen_netlist.py` · `state/gen_netlist_pins.py` · `state/gen_kicad_net.py` · `state/gen_bom.py` · `state/check_*.py` (全部) · `HW/check_step1_parts_spec.py` · `HW/check_netlist_selfconsistency.py` · `MECH/**` · `SW/**` · `PROJECT_TRACKER.md` · `state/issue_log.yaml` · 板 / `.kicad_pro` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/STEP1_PARTS_SPEC.md` / `HW/PART_ALTERNATIVES_REGISTRY.md`。

---

## B7 · ★★2026-11-17 补记 (★落表后维护 · H-1 重锚第 1 跳 · 追加式·历史不改★)★★

### B7.1 起因 (★全部本机实测★)

★**ISS-239 交卷 (2026-11-16 11:50) 之后, main 12:2x~12:4x 独立实跑 11 道验收命令 ⇒ 已落 verified** ★
⇒ ★**但 2026-11-16 21:22 的 ISS-257 落表第 6 批 (G1a-7) 把 网表/脚表/BOM 三个 md5 改了** ★
⇒ ★**本闸 (`HW/check_pin_function_labels.py`) 的 5 个 md5 基线是【过期锚点】, 不是真源被偷换** ★
  (★实测 `grep -c "check_pin_function_labels" HANDOFF/*ISS257*` = 0 ⇒ ISS-257 交接单根本没提本闸★)
⇒ ★**补记前实测: `--expect-known` ⇒ rc=1 (假红)** ★ (★缺陷快照 15/15 仍一致, 多出的是 3 条 `MD5_CHANGED`★)

### B7.2 做了什么 (★逐条·文件 + 行号·详见 `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` §11★)

- ★**重锚 3 个 md5 基线** (`PROTECTED_MD5` L141~L147): 网表 → `e06c1dd6…` · 脚表 → `287e7861…` · BOM → `94642d07…`; ★**板 / `.kicad_pro` 两个值一个字节没动** ★
- ★**新增 ④b 台账对账** (L414~L458 `check4b_md5_ledger()` + L864~L891 三个常量): ★**脚本里的基线 md5 必须在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里查得到; 重锚链链尾必须 == 基线** ★ ⇒ ★**"改基线凑绿"被堵死** ★
- ★**新增 3 条反向用例 T11 / T12 / T13** (L800 / L819 / L830) ⇒ `--selftest` **10/10 → 13/13**
- ★**`KNOWN_DEFECTS` (15 条) 与其 SHA256 一个字节没动** ★ ⇒ ★**判据本体没被放宽★**

### B7.3 交卷时实测 (★本机实跑·2026-11-17★)

| 命令 | rc | 要点 |
|---|---|---|
| `python3 HW/check_pin_function_labels.py` | ★**1** ★ | ★首行「当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿」★ + ★**15 条 = 14 串号 + 1 缺脚**★ + ④/④b 0 条 |
| `python3 HW/check_pin_function_labels.py --expect-known` | ★**0** ★ | ★**15/15 逐条一致**★ |
| `python3 HW/check_pin_function_labels.py --selftest` | ★**0** ★ | ★**13/13**★ (T11/T12/T13 各带"自证改到了目标")★ |
| `python3 HW/check_step1_parts_spec.py` | 0 | C1~C8 **8/8** (★ISS-237 立的闸没被本单改红★) |
| `python3 state/check_sch_pinfull.py` | 0 | ★584=584 · 本单**没动脚数基线**★ |
| `python3 state/check_netlist.py` / `check_netlist_pins.py` / `check_sch_erc.py` | 0 / 0 / 0 | ★ERC=0★ |
| `python3 HW/check_land_row_anchors.py` | 0 | ★310/310 (★ISS-262 守卫没被打断·本文件 0 条锚点★)★ |
| `python3 state/merge.py` / `python3 state/gate_check.py` | 0 / 0 | ★【Q1】18/18★ |

### B7.4 留给 main 的 (★追加·B5 里的 3 条仍然挂着★)

- ★**落表批次现在多一件**: 除了 F1~F4 + 重生成链, ★**还要同步 `HW/check_pin_function_labels.py` 的 5 个 md5 基线 + 在 `MD5_ANCHOR_CHAIN` 追加一跳 (单号 / 旧 md5 / 新 md5 / 落表时刻 / 台账行号)** ★
- ★**MECH `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 + SW `SW/SW_MD5_BASELINE_LEDGER.md` §1 两个 H-1 重锚** (★本单仍然只点名, 不代改★)
- ★**ISS-237 那句错话照旧更正**: 「7 颗 TPS7A20 的 EN 一行都没有 ⇒ 全表关断」经 main 实测不成立 (★网表 L102/L112/L122/L132/L142/L152 都有 EN 行★) ⇒ 真病灶是本单这两条 (★pin4/pin5 功能名串号 + U_LDO_S28 缺 pin3★)
