# 网表 / 板 第 3 轮「自相矛盾」3 条 —— 逐条定性 + 逐字改法 (ISS-242)

· **出单**: 项目总工 (main / moli) · **执行**: 硬件总工 (hw-lead) · **日期**: 2026-11-16
· **机器门禁**: `HW/check_netlist_contradiction_r3.py` (★只判矛盾, **不落表**★)
· **交卷单**: `HANDOFF/2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md`

---

## 0. 边界 (先声明, 免得后面被误读)

| 项 | 状态 |
|---|---|
| 改网表 / 脚表 / BOM / 板文件 / 任何生成器 | ★**一件没动**★ (md5 见 §6) |
| 改 PCB 布线 / 布局 / 板框 / 走线 | ★**一件没动**★ (老板 11-11 10:07 口径: PCB 布线布局类一律不派) |
| 落表排期 | ★**由 main 排期 (H-1 重锚) —— 本页只出规格**★ |
| 零外发 | ★**零外发**★ (不发邮件 / 不联系供应商 / 不下采购单 · 老板 11-12 02:02 口径) |
| 实物 [实测] | ★**0 条**★ (本单全部依据 = 本机文件 + 本机脚本实跑) |
| V-2 / V-3 / V-4 三条待裁 | ★**一条没代拍**★ (仍等老板) |
| 别人分片 | ★**没写**★ (只写 `state/fragments/hw.yaml`) |
| `issue_log` status | ★**没自签**★ (留给 main 落 `verified`) |

### 0.1 门禁与命令

```bash
python3 HW/check_netlist_contradiction_r3.py              # 门禁: rc=1 且 findings=3 = 红 (现状就该红)
python3 HW/check_netlist_contradiction_r3.py --selftest   # 反向用例自证: rc=0 = 11/11 全抓到
python3 HW/check_netlist_contradiction_r3.py --json       # 机器可读
```

★**现状 (真文件) 就是红的**: 这 3 条缺陷**还没落表**, 门禁是【现状守卫】不是【合格证】 ⇒
**门禁 rc=1 是预期状态**, 等落表那趟跑完才是 rc=0 ★

### 0.2 实测数 vs 派单估数 (★差异来源逐条写清★)

| 项 | 派单 (brief) 写的 | ★本机实测**★ | 差异来源 |
|---|---|---|---|
| DNP 颗数 | 「41 颗 DNP 零标记」 | ★**MAIN_PCB∧DNP = 54 颗 · 在板上 43 颗 · 零标记 43 颗**★ | 54 = 43 颗真器件 + **11 颗伪器件** (`NET_KEY_CAM` / `NET_LED_B` / `NET_XTAL_IN` / `NET_XTAL_OUT` / `RAIL_BOARD_5V` / `RAIL_LIGHT_1V8` / `RAIL_SENSOR_AVDD` / `RAIL_SENSOR_CORE` / `RAIL_SENSOR_VDD_IO` / `RAIL_V_CORE` / `RAIL_V_SOC_IO`) ⇒ 伪器件 (`RAIL_*` / `NET_*` 前缀) 在板生成器里被显式跳过 (`state/gen_pcb_netlist_board.py` `if ref.startswith(PSEUDO): continue`) ⇒ **板上只有 43 颗**, 派单的 41 是把伪器件算进去/算错的估计值 |
| 空封装名 | 186/186 | ★**186/186 (一致)**★ | — |
| fp_line<2 的 | 1 个 = `J_USB_C` | ★**1 个 = `J_USB_C` (一致)**, 但**那是误报** ★ | `J_USB_C` 的丝印是用 KiCad 的 `(fp_rect` 画的 (0 fp_line + 2 fp_rect) ⇒ 按【全部 fp_* 图形原语】数, 整板 186 个里 `<2` 的 = **0 个** (详见 §5) |
| J_CHG 板侧 fp_line | 「只有 1 条 fp_line (W=6.00 H=0.00)」 | ★**4 条 fp_line, 构成 6.00 × 4.00 mm 的 F.Fab 矩形**★ | ★**派单这里写错了**: 不是 1 条, 是 4 条; 不是 H=0.00, 是 H=4.00 ⇒ 但**结论不变**: 它不是 10p@0.5mm 铰链 FPC 座, 只是一块 6×4mm 的通用占位矩形 + 2 个焊盘 |
| J_CHG 脚表行数 | 「脚表 17 行」 | ★**ref=J_CHG 的脚表行 = 10 行 (pin1..pin10)**★; 「含 J_CHG 字样的行」才是 17 行 (多出的 7 行是别的 ref 的 note 里提到 J_CHG) | 口径不同: 「J_CHG 的脚」 vs 「提到 J_CHG 的行」 |
| J_CHG 网表行 | L15-L23 | ★**ref=J_CHG 的行 = 11 行 (L16/L20/L21/L22/L23/L38/L42/L412/L433/L478/L497), board 全 = HINGE**★ | 派单数的是「L15-L23 这一段」, 实际还有 L38/L42/L412/L433/L478/L497 |

---

## 0.3 ★板级同源特征 (不是 J_CHG 一颗的错)★

★**板文件里 186/186 个 footprint 的封装名都是空字符串** (`(footprint ""`) ⇒

- ★**这不是 `J_CHG` 一颗器件的错, 是 `state/gen_pcb_netlist_board.py` 的 `make_footprint()` 从头到尾没写过封装名 (FPID)** ★
- ⇒ 落表那趟**必须改生成器, 不许只改一颗** ⇒ 否则下一批器件照样是空名
- ⇒ 门禁 `R3-A5` 把这一条当**板级同源特征**归并进 F2 的证据, **不单开 finding** (★否则 findings 变 4 条 = 多报★)
- ⇒ ★**本单不许改板** ⇒ 只出改法规格 (§2.3) ★

---

## 1. F1 — C_VBUS_OUT / C_VBUS_GND 两颗 2 脚电容在网表里端子标签撞车

### ① 现状逐字 + 行号

**表A `HW/netlist_v1.csv` L8~L12 (逐字, ★本机实读★):**

```
L8 : P1,VBUS_5V_F1,FB_VBUS,C_VBUS_OUT,FB_VBUS,π 滤波磁珠 [待选型],L,必装,[推算],,"[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗)",C-01,CHG_BOARD,,
L9 : P1,VBUS_5V_F1,VBUS_5V_F1,C_VBUS_OUT,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,π 滤波后级电容位 (BQ25896 建议 ≥100µF),C-01,CHG_BOARD,,
L10: P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,"π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容, 又是对地电容 · 一颗 2 脚件落进 3 个网 = 导出后一脚悬空); BQ25896 建议 ≥100µF",C-01,CHG_BOARD,,
L11: P1,VBUS_5V_CHG,C_VBUS_OUT,U_CHG pin1,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,π 滤波电容 (后级, 串联) 位,C-01,CHG_BOARD,,
L12: P1,VBUS_5V_CHG,C_VBUS_GND,C_VBUS_OUT,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点),C-01,CHG_BOARD,,
```

**表B `HW/netlist_v1_pins.csv` (逐脚真值, ★本机实读★):**

```
L148: C_VBUS_GND.1,GND,C_VBUS_GND,1,P1,[待选型] 100µF,C,DNP,CHG_BOARD,C-01,...   ★对地脚★
L149: C_VBUS_GND.2,VBUS_5V_CHG,C_VBUS_GND,2,P1,[待选型] 100µF,C,DNP,CHG_BOARD,C-01,... ★信号脚★
L154: C_VBUS_OUT.1,VBUS_5V_F1,C_VBUS_OUT,1,P1,[待选型] 100µF,C,DNP,CHG_BOARD,C-01,...  ★磁珠后级★
L155: C_VBUS_OUT.2,VBUS_5V_CHG,C_VBUS_OUT,2,P1,[待选型] 100µF,C,DNP,CHG_BOARD,C-01,... ★接 U_CHG pin1★
```

**门禁命中 (★本机实跑★):** `R3-A1` 命中 1 (C_VBUS_OUT 的裸位号在 node 槽里登记 **4** 次 > 脚数 2, 行 = [8, 9, 11, 12]) · `R3-A2` 命中 1 (L12: C_VBUS_GND 的对端裸位号 = C_VBUS_OUT, 而两颗在脚表里同在 `VBUS_5V_CHG` 上 ⇒ 端子标签撞车)

### ② 真源在哪个文件哪一行

| 项 | 位置 |
|---|---|
| ★**脚表 (脚级真值)** ★ | `HW/netlist_v1_pins.csv` L148/L149/L154/L155 ⇒ **C_VBUS_OUT = {VBUS_5V_F1, VBUS_5V_CHG} · C_VBUS_GND = {GND, VBUS_5V_CHG}** ⇒ ★**两颗各 2 脚, 脚表是对的**★ |
| ★**网表行 (矛盾所在)** ★ | `HW/netlist_v1.csv` L8 / L9 / L11 / L12 (生成器见下) |
| ★**网表生成器 (真源)** ★ | `state/gen_netlist.py` ★**L369** (L8) / ★**L372** (L9) / ★**L375** (L10) / ★**L379** (L11) / ★**L381** (L12)★ |
| 板侧 | ★**这两颗是 CHG_BOARD 件, 不在 demo 主 PCB 上** ★ (`board` 列全 = `CHG_BOARD` ⇒ 板生成器按 board 列过滤) ⇒ ★**本条不改板**★ |

**缺陷一句话**: ★**表A 里同一颗 2 脚 C 的端子被登记了 4 次 (L8.node2 / L9.node2 / L11.node1 / L12.node2), 而表B 说它只有 2 个脚 ⇒ 两张表自相矛盾** ★
★**根因 = 表A 的 `node2` 槽在同一个网里混用了两种绑定约定** ★
· 同款 2 脚 C 的正常写法是 **(自己 ref, 网标签)** —— 对照 L9 (node1=网标签 `VBUS_5V_F1`, node2=自己 `C_VBUS_OUT`) 与 L10 (node1=自己 `C_VBUS_GND`, node2=网标签 `GND`) ★
· 而 L12 写的是 (自己 `C_VBUS_GND`, **别人的裸位号** `C_VBUS_OUT`) ⇒ ★**C_VBUS_GND 的那个端子在 L12 里被写成了「另一颗器件」⇒ C_VBUS_OUT 的 `VBUS_5V_CHG` 端子同时被 L11.node1 和 L12.node2 认领两次** ★
· L8 同理 (node2=`C_VBUS_OUT`, 与 L9.node2 重复认领 `VBUS_5V_F1` 端子) ⇒ ★**一颗 2 脚件落进 3 个网 = 导出后一脚悬空** (★L10 的 note 自己就写着这句话★) ★

### ③ 逐字改法 (★给到生成器那一行的改前 → 改后字符串★)

**★改法 = 2 行, 把 L8 / L12 的 `node2` 从「别人的裸位号」改成「网标签」, 让每颗 2 脚 C 的端子各被认领一次** ★

**改法 1 —— `state/gen_netlist.py` ★L369★ (表A L8)**

```diff
-    add("P1", "VBUS_5V_F1", "FB_VBUS", "C_VBUS_OUT", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
+    add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
         "必装", "[推算]", "",
         "[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗)", "C-01")
```

**改法 2 —— `state/gen_netlist.py` ★L381★ (表A L12)**

```diff
-    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "C_VBUS_OUT", "C_VBUS_GND", "[待选型] 100µF", "C",
+    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "VBUS_5V_CHG", "C_VBUS_GND", "[待选型] 100µF", "C",
         "DNP", "[推算]", "", "π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点)", "C-01")
```

> ★**为什么不改成 `C_VBUS_GND`** ★: 门禁反向用例 ★**T2**★ 实跑证明 = ★**改成 `C_VBUS_GND` 照样红**★ (A1 仍命中 1: C_VBUS_OUT 还是被登记 3 次) ⇒ ★**派单里"改成 C_VBUS_GND"是错值, 不许照抄**★
> ★**为什么 L8 也要一起改**: 只改 L12 ⇒ C_VBUS_OUT 仍被登记 3 次 (L8/L9/L11) ⇒ A1 仍红 ⇒ ★**两条必须同趟改, 少一条都不绿**★ (门禁反向用例 T3 就是测这一条)

**★实跑验证 (在 /tmp 沙盒副本上, 零落表)** ★:

```
$ cd /tmp/iss242_fix && python3 state/gen_netlist.py && python3 state/gen_netlist_pins.py
  → RC=0 · 网表与真网表 diff = 【只有 L8 与 L12 两行】· 脚表 md5 逐字节相同
    b21b743a7702d30729f0d653c15392df  (改前) == b21b743a7702d30729f0d653c15392df  (改后)
$ python3 HW/check_netlist_contradiction_r3.py   (在沙盒上)
  → R3-A1: 命中 0 ✅ · R3-A2: 命中 0 ✅ ⇒ F1 绿 ⇒ findings 由 3 变 2
```

★**脚表逐字节不变** ⇒ ★**这个改法不碰脚级真值, 只把表A 的绑定约定统一** ★

### ④ 改完跑哪条命令

```bash
python3 state/gen_netlist.py            # 重出表A
python3 state/gen_netlist_pins.py        # 重出表B (★预期 md5 不变★)
python3 HW/check_netlist_contradiction_r3.py   # ★预期: R3-A1/A2 绿, findings = 2 (只剩 F2/F3)★
python3 state/check_netlist.py && python3 state/check_netlist_pins.py && python3 state/check_sch_erc.py   # rc=0
```

### ⑤ 归到 ISS-211 / 214 / 217 哪条门禁断言

| 归属 | 锚点 | 说明 |
|---|---|---|
| ★**ISS-217** ★ | 作业包 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` §3.6 (★**#6** ★「`C_VBUS_OUT` 串联在 BQ25896 的 DC 输入路径上」) + §4.C ★**补差C**★ (π 滤波真值拓扑) | ★**F1 是这族的第 3 轮新增条目** ⇒ 建议登记为新作业条目 (d12 / #12), **与 #6 同批落** (同一次 π 滤波拓扑重构里一起改) ★ |
| ★**ISS-214** ★ | §11 ★**附带发现 #6** ★ (同 #6) · 翻面判据 ★**R11** ★ | R11 判的是 **board 列** (d11 已落) ⇒ ★**F1 的端子标签撞车是 R11 之外的独立判据** ★ |
| ★**ISS-211** ★ | §10 八条 / §11 附带发现 族 | ★**F1 是本族 (网表自己跟自己打架) 的新增条目, 不属 ISS-211 原 4 条** ★ |
| ★**本单门禁** ★ | `HW/check_netlist_contradiction_r3.py` ★**R3-A1** ★ + ★**R3-A2** ★ | ★**F1 = A1 + A2** ★ |

---

## 2. F2 — J_CHG 位号双义 + 板侧封装块不可装配

### ① 现状逐字 + 行号

**网表侧 (`HW/netlist_v1.csv`, ★11 行, board 全 = HINGE★):**

```
L16 : P1,BAT_CHG,J_CHG pin1,J_CHG pin2,J_CHG,跨铰链 1.5A (双 pin 并联),NET,必装,...
L20 : P1,HINGE_RSV,J_CHG pin9,J_CHG pin9,J_CHG,预留 (不装),NET,DNP,...
L21 : P1,HINGE_RSV,J_CHG pin10,J_CHG pin10,J_CHG,预留 (不装),NET,DNP,...
L22 : P1,GND,J_CHG pin3,J_CHG pin4,J_CHG,回流 (双 pin),NET,必装,...
L23 : P1,GND,J_CHG pin4,GND,J_CHG,回流 (双 pin),NET,必装,...
L38 : P1,BAT_CHG,J_CHG,J_CHG,J_CHG,1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流),CONN,必装,...
L42 : P1,TS_BAT,J_CHG pin8,R_NTC_BAT,J_CHG,跨铰链 (高阻),NET,必装,...
L412: P1,HINGE_CHG,J_CHG,J_CHG,J_CHG,1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流),CONN,必装,...
L433: P1,NC,J_CHG pin7,NC,J_CHG,预留 (NC),NET,DNP,...
L478: P1,TS_BAT,U_CHG pin11,J_CHG pin8,J_CHG,跨铰链 (高阻),NET,必装,...
L497: P10,BAT_CHG,U_CHG pin14,J_CHG pin1,J_CHG,1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流),CONN,必装,...
```

★**脚表 `HW/netlist_v1_pins.csv`: ref=J_CHG 的行 = 10 行 (pin1..pin10)** ★
(L192 pin1=BAT_CHG / L194 pin2=BAT_CHG / L195 pin3=GND / L196 pin4=GND / L197 pin5=CHG_STAT / L198 pin6=PWR_GOOD / L199 pin7=NC / L200 pin8=TS_BAT / L201 pin9=NC / L193 pin10=NC)

**板侧 (`HW/PCB/demo_mainboard.kicad_pcb` L17633~L17739, ★本机实读★):**

```
L17633: 	(footprint ""                       ★★封装名 = 空字符串★★
L17636: 		(property "Reference" "J_CHG"
L17642: 		(property "Value" "SoM BTB CHG (100pin, 部分已分配)"   ★★占位值★★
L17635: 		(at 135.3 58)
          ... 4 × (fp_line ...)  → 构成 6.00 × 4.00 mm 的 F.Fab 矩形 ★(派单写「1 条 · W=6.00 H=0.00」, 实测是 4 条 · H=4.00)★
L17698: 		(pad "1" smd rect (at -2.1 -1.4) (net "BAT_CHG"))
L17706: 		(pad "6" smd rect (at -1.6 -1.4) (net "PWR_GOOD"))
```

⇒ ★**板上这个 J_CHG 只有 2 个焊盘 (pin1 / pin6) · 封装名空 · Value 是生成器的占位串** ★
⇒ ★**脚表说 J_CHG 有 10 脚 ⇒ 8 个脚在板上没有落点** ★
⇒ **门禁命中**: `R3-A3` 命中 1 (脚表 10 脚 / 板文件 2 个焊盘 ⇒ 无落点脚 = 8 个) · `R3-A5` 空封装名 186/186 (板级同源特征, §0.3)

### ② 真源在哪个文件哪一行

| 环节 | 真源 |
|---|---|
| ★**为什么板上有 J_CHG** ★ | `state/gen_pcb_netlist_board.py` ★**L277-L283** (`derive_pads`: 「节点串里带**编号脚**的器件 ⇒ 也要建封装」) ★+ `state/gen_pcb_netlist_board.py` ★**L231-L237** (`load_rows()` 只留 `board == MAIN_PCB` 的行) ★⇒ ★**J_CHG 的 10 脚定义全在 board=HINGE 的行里 (11 行), demo 板按 board 列过滤后一颗脚都引不到; 只有 2 行 MAIN_PCB 的行在节点串里写了 "J_CHG pinN"** ★ ⇒ `HW/netlist_v1.csv` ★**L61** ★(`PWR_GOOD`, node2=`J_CHG pin6`) + ★**L76 / L416** ★(`BAT_CHG`, node1=`J_CHG pin1`) ⇒ ⇒ **板上只画出这 2 个被主板行引用到的编号脚** ★ |
| ★**封装名为什么空** ★ | `state/gen_pcb_netlist_board.py` ★**L431-L433** (`make_footprint()`: `pcbnew.FOOTPRINT(board)` → `SetReference` → `SetValue` ⇒ ★**从头到尾没有 `SetFPID`** ⇒ 186/186 个 footprint 全是 `(footprint ""` ★ |
| ★**占位 Value 的来源** ★ | `state/gen_pcb_netlist_board.py` ★**L584-L587** (`value_of[ref] = "SoM BTB %s (100pin, 部分已分配)" % ref.split("_")[-1]` ⇒ `J_CHG` ⇒ `"SoM BTB CHG (100pin, 部分已分配)"`) ★ |
| 网表侧 | `state/gen_netlist.py` ★**L117** (`HINGE_REFS = {"J_CHG"}`) + `state/p10_rows.json` (L497 那行的真源) ★ |

### ③ 逐字改法 (★给到生成器那一行的改前 → 改后字符串★)

★**F2 必须拆成两件事: ③-A 板级同源特征 (封装名) + ③-B 位号撞车 (焊盘数) —— 只做 ③-A 不通过** ★

**③-A 板侧: 给每个 footprint 一个非空封装名 (★落表那趟必须改生成器, 不许只改一颗★)**

`state/gen_pcb_netlist_board.py` ★**L431-L433**★:

```diff
     fp = pcbnew.FOOTPRINT(board)
     fp.SetReference(ref)
     fp.SetValue(value)
+    # ★ISS-242 R3-A5: 封装名 (FPID) 不能为空 ⇒ 旧写法 186/186 个 footprint 全是 (footprint ""
+    fp.SetFPID(pcbnew.LIB_ID("ARS45_GEN", "%s_GEN" % kind))
```

> ★**[实测·本机 KiCad 10.0.8]**★: 上面这一行落盘后, 板文件里该 footprint 变成 `(footprint "ARS45_GEN:SOIC-8_GEN"` ⇒ `R3-A5` 的空封装名判据立刻绿 ★
> ★**本机实测路径**: `bash state/pcbnew_py.sh` (KiCad AppImage 自带 python · `pcbnew.Version() = 10.0.8`) ★

**③-B 位号撞车 (★主改法, 需 main / ISS-199 / ISS-202 拍板 —— 本单不代拍★)**

★**问题定性**: 板上的 J_CHG **不是** 1×10p@0.5mm 铰链 FPC 座, 它是「**主板上引出的 2 根跨铰链线**」的占位封装 (BAT_CHG + PWR_GOOD) ⇒ ★**同一个位号在网表里指 10p FPC 座、在板文件里指 2 脚跨铰链接口占位 ⇒ 装配/备料/结构三方拿到的是两个不同的件** ★

| 方案 | 改法落点 (逐字) | 门禁后果 |
|---|---|---|
| ★**A (推荐, 对齐 ISS-217 §3.4 #4 的消歧方案)** ★ | 网表侧: `state/gen_netlist.py` ★**L117** ★`HINGE_REFS = {"J_CHG"}` ⇒ 改为 `{"J_CHG_FPC"}` ★ + `state/p10_rows.json` 的 J_CHG 行 + ★**L61 / L76 / L416** ★三行的节点串 `"J_CHG pinN"` ⇒ `"J_CHG_FPC pinN"` ★; 板侧: 跨铰链接口占位另起位号 (如 `J_HINGE_CHG_IF`) ⇒ ★**板上的占位与网表里的 10p 座彻底解耦** ★ | ★**A3 绿** (占位封装不再是脚表里 10 脚的那个位号) + A5 绿 ★ ⇒ F2 绿 ★ |
| **B (板侧最小改动, 不动网表位号)** | `state/gen_pcb_netlist_board.py` ★**L431-L433** ★按 ③-A 加 `SetFPID` (占位封装用自解释名, 如 `ARS45_GEN:HINGE_IFACE_2P`) | ★**A5 绿, 但 A3 仍红** ★ (脚表 10 脚 vs 板 2 焊盘) ⇒ ★**B 单独做 = 不通过** ★ |

> ★**判定 (不代拍, 只给判据)**: ★**落表那趟必须做 A** ★ (B 单独做门禁仍红) ⇒ ★**A 触及位号消歧 ⇒ 归属 ISS-199 / ISS-202 / ISS-217 §4.C 补差C ⇒ 由 main 拍板后落** ★
> ★**V-4 (J_CHG 4 pin 并联解) 是另一条待裁** ⇒ ★**本单一条没代拍** ★

### ④ 改完跑哪条命令

```bash
python3 HW/check_netlist_contradiction_r3.py   # ★预期: R3-A3 绿 (焊盘 ≥ 脚表脚数) + R3-A5 空封装名 0 ⇒ F2 绿★
python3 state/check_netlist.py && python3 state/check_netlist_pins.py   # rc=0
python3 state/check_pcb_nets.py                # ★板侧改了才需要跑 (板只改一次那一趟)★
```

### ⑤ 归到 ISS-211 / 214 / 217 哪条门禁断言

| 归属 | 锚点 | 说明 |
|---|---|---|
| ★**ISS-217** ★ | 作业包 §3.4 ★**#4** ★「`J_CHG` 在网表与板文件里指两个不同的物理件」+ §4.C ★**补差C** ★(J_CHG 位号消歧) | ★**方案 A 就是 #4 早就写好的消歧方案** ⇒ 本单只是把它的**板侧后果 (R3-A3) 用机器判据钉住** ★ |
| ★**ISS-214** ★ | §11 附带发现 #4 (同 #4) | — |
| ★**ISS-199 / ISS-202** ★ | 铰链结构 / J_CHG pin map 地界 | ★**位号消歧的裁决归属** ★ |
| ★**本单门禁** ★ | `HW/check_netlist_contradiction_r3.py` ★**R3-A3** ★ (焊盘数 ≥ 脚表脚数) + ★**R3-A5** ★ (封装名非空) | ★**F2 = A3 + A5** ★ |

---

## 3. F3 — MAIN_PCB 上 DNP 位号在板文件里零标记 (贴片坐标会当必装)

### ① 现状逐字 + 行号

**★本机实测 (门禁 `R3-A4` 输出)★**:

```
MAIN_PCB 且 dnp=DNP 的位号数 : 54
其中在板文件里真实存在的     : 43
零标记的                     : 43
```

★**板文件里 DNP 标记机制实测 (★`grep -c` 本机实跑★)** ★:

```
$ grep -c "exclude_from"      HW/PCB/demo_mainboard.kicad_pcb   →  0
$ grep -c "(attr"             HW/PCB/demo_mainboard.kicad_pcb   →  0
$ grep -n "dnp"               HW/PCB/demo_mainboard.kicad_pcb
  192:			(hidednponfab no)
  193:			(sketchdnponfab yes)
  194:			(crossoutdnponfab yes)
```

⇒ ★**这 3 行是 KiCad 的全局显示开关 (「已标记 DNP 的器件怎么显示」), 不产生标记** ★
⇒ ★**43 颗 DNP 件在贴片坐标文件 (CPL) 与装配文件里没有任何「不贴」标记 ⇒ 贴片厂会当必装贴上** ★
⇒ ★**BOM 里 dnp 列写着 DNP ≠ 板文件里有标记** ★

★**43 颗在板上的 DNP 位号 (逐个列出)★**:

```
BT_432243 (电池座), C_BULK_LIGHT_1V8, C_BULK_SENSOR_AVDD, C_BULK_SENSOR_CORE,
C_BULK_SENSOR_VDD_IO, C_BULK_V_CORE, C_BULK_V_SOC_IO, C_DET_BAT, C_HF_LIGHT_1V8,
C_HF_SENSOR_AVDD, C_HF_SENSOR_CORE, C_HF_SENSOR_VDD_IO, C_HF_V_CORE, C_HF_V_SOC_IO,
C_KEY_CAM, C_SUPV, C_XTAL_IN, C_XTAL_OUT, D_ESD_LIGHT, D_LED_B, J_BOOT1, Q1, Q2,
Q_ENVC, R_BAT_DET_1, R_BAT_DET_2, R_ID_JMP0, R_ID_JMP1, R_LED_B, R_NTC_BAT,
R_TS_PULL, SW_KEY_CAM, TP_BAT, TP_LED_B, U_BATPROT, U_DCDC_VCORE, U_DCDC_VIO,
U_LDO_L18, U_LDO_S12, U_LDO_S18B, U_LDO_S28, U_SUPV, X1
```

★**另有 11 颗 MAIN_PCB∧DNP 不在板上** = 全是伪器件 (`NET_*` / `RAIL_*`) ⇒ 板生成器显式跳过 ⇒ **不是漏贴风险** ★

### ② 真源在哪个文件哪一行

| 环节 | 真源 |
|---|---|
| ★**网表侧 (谁是 DNP)** ★ | `HW/netlist_v1.csv` 的 `dnp` 列 (值 = `DNP` / `必装`) ★; 生成器 = `state/gen_netlist.py` 的 `add()` 第 8 参 ★ |
| ★**板侧 (为什么没标记)** ★ | `state/gen_pcb_netlist_board.py` ★**L231-L237** (`load_rows()` 把 `dnp` 列读进来了但**只用 board 列过滤, dnp 列一路没被使用**) ★ + ★**L428-L433** (`make_footprint()` 建封装时**不写任何属性**) ★ ⇒ **板文件里 0 处 `(attr` = 生成器从来没写过, 不是被人删了** ★ |
| ★**KiCad 侧的标记机制** ★ | `(attr exclude_from_pos_files exclude_from_bom dnp)` ★**[本机 KiCad 10.0.8 实跑验证过]**★ |

### ③ 逐字改法 (★给到生成器那一行的改前 → 改后字符串★)

**改法 1 —— `state/gen_pcb_netlist_board.py` ★新增模块级 DNP 表 (放在 `make_footprint()` 定义之前)★**

```diff
+ # ★ISS-242 R3-A4: DNP 位号表 (ref -> dnp 列) —— 在 main() 里由网表行填 ⇒ 板文件里写 DNP 标记
+ DNP_OF = {}
+
+
  def make_footprint(board, ref, value, kind, pins, netmap, x, y, label=True, rot=0):
```

**改法 2 —— `state/gen_pcb_netlist_board.py` ★L431-L433 之后 (与 §2.3 ③-A 同一个 hunk, 两处一起改)★**

```diff
      fp = pcbnew.FOOTPRINT(board)
      fp.SetReference(ref)
      fp.SetValue(value)
+     # ★ISS-242 R3-A5: 封装名 (FPID) 不能为空 ⇒ 旧写法 186/186 个 footprint 全是 (footprint ""
+     fp.SetFPID(pcbnew.LIB_ID("ARS45_GEN", "%s_GEN" % kind))
+     # ★ISS-242 R3-A4: DNP 件必须带 (attr exclude_from_pos_files exclude_from_bom dnp)
+     #   ⇒ 否则贴片坐标文件 (CPL) 会把这 43 颗当必装
+     if (DNP_OF.get(ref) or "").strip().upper() == "DNP":
+         fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES
+                          | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_DNP)
```

**改法 3 —— `state/gen_pcb_netlist_board.py` ★`main()` 里 `value_of` 那段之后 (★L583 附近★)填表 (★DNP 优先口径★)**

```diff
      for r in rows:
          ref = (r.get("ref") or "").strip()
          if ref and ref not in value_of:
              value_of[ref] = (r.get("value") or "")[:40]
+     for r in rows:
+         ref = (r.get("ref") or "").strip()
+         if not ref:
+             continue
+         d = (r.get("dnp") or "").strip().upper()
+         # ★DNP 优先: 同一个 ref 可能有多行 (器件行 + NET 行), NET 行的 dnp 常是「必装」
+         #   ⇒ 首行获胜会把 U_DCDC_VCORE / U_DCDC_VIO 这类漏掉 ⇒ 只要有一行写 DNP 就判 DNP
+         if d == "DNP":
+             DNP_OF[ref] = "DNP"
+         elif ref not in DNP_OF:
+             DNP_OF[ref] = d
```

> ★**[实测·本机 KiCad 10.0.8]**★: `fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_DNP)` ⇒ 板文件里落成 ★`(attr exclude_from_pos_files exclude_from_bom dnp)`★ ⇒ 门禁 `R3-A4` 的三个判据 (exclude_from_bom / exclude_from_pos_files / attr dnp) **三个都命中** ⇒ A4 绿 ★
> ★**注**: KiCad 10 的 `pcbnew.FOOTPRINT` **没有** `SetAttribute()` 方法 (★本机实测报 `'FOOTPRINT' object has no attribute 'SetAttribute'`★) ⇒ **只能用 `SetAttributes(flags)`**, 别照抄老写法 ★
> ★**注**: `make_footprint()` 有 **5 个调用点** (★L815 / L818 / L922 / L985 / L1023★) ⇒ ★**本改法用模块级 `DNP_OF` 查表, 5 个调用点一行都不用改** ⇒ 漏调用点的风险 = 0 ★

> ★★★**坑 1 (★U-4★): 「非空封装名」改法必须覆盖 4 个独立封装模块** ★★★
> ★**沙盒整树实跑实测**: 只改 `make_footprint()` ⇒ 生成的板里 ★**185 个 footprint 中 178 个拿到封装名, 7 个仍是空的** ★ ⇒ ★**这 7 颗是 4 个独立模块直接用 `pcbnew.FOOTPRINT()` 画的, 绕过 `make_footprint()`** ★:
> · `state/som_btb_footprint.py` ⇒ `J_SOM_P1` / `J_SOM_P2` / `J_SOM_P3` / `J_SOM_P4` (SoM 4 组 100pin BTB)
> · `state/usb_c_footprint.py` ⇒ `J_USB_C` (GCT USB4105-16p 自绘)
> · `state/display_fpc_footprint.py` ⇒ `CONN_LIGHT` (HIROSE FH12-22S)
> · `state/tmp117_footprint.py` ⇒ `U_TEMP`
> ⇒ ★**落表那趟必须在这 4 个模块里也补 `fp.SetFPID(...)`, 否则 R3-A5 仍红** ★

> ★★★**坑 2 (★U-5★): DNP 表必须「DNP 优先」, 不能「首行获胜」** ★★★
> ★**同一个 ref 可能有多行, NET 行的 `dnp` 常是「必装」** ★ ⇒ 实测两个漏网的例子:
> · `HW/netlist_v1.csv` ★**L70** ★ `EN_VCORE` (type=NET, dnp=必装, ref=`U_DCDC_VCORE`) · ★**L79** ★ `V_CORE` (type=IC, dnp=DNP, ref=`U_DCDC_VCORE`) ⇒ ★**首行获胜 ⇒ `U_DCDC_VCORE` 拿不到 DNP 标记** ★
> · ★**L74** ★ (type=NET, dnp=必装, ref=`U_DCDC_VIO`) · ★**L86** ★ (type=IC, dnp=DNP, ref=`U_DCDC_VIO`) ⇒ ★**同理** ★
> ⇒ ★**正确口径 = 「只要该 ref 的任一行 dnp == DNP 就判 DNP」** ★ (与门禁 `R3-A4` 的口径一致) ⇒ ★**改法 3 必须是「DNP 优先」版** ★
> ★**[实测·本机直算 + 沙盒生成器实跑对照]** ★:
> · 直算 (★按 `load_rows()` 的 board 过滤口径跑两版口径★): ★**首行获胜 ⇒ 43 颗里判出 41 颗 (漏 `U_DCDC_VCORE` / `U_DCDC_VIO`) · DNP 优先 ⇒ 43 颗全判出 (漏 0 颗)** ★
> · 沙盒生成器实跑 (★首行获胜版★): 生成的板里 ★**41 颗带 `(attr exclude_from_pos_files exclude_from_bom dnp)` · 正好少这 2 颗** ★ ⇒ ★**与直算完全对上** ★

### ④ 改完跑哪条命令

```bash
python3 state/gen_pcb_netlist_board.py        # ★板侧改动 ⇒ 只能并进「板只改一次」那一趟★
python3 HW/check_netlist_contradiction_r3.py   # ★预期: R3-A4 绿 (零标记 0 颗) ⇒ F3 绿★
python3 state/check_pcb_nets.py                # pad↔net 与网表一致
python3 state/check_pcb_drc.py                 # DRC = 0
```

### ⑤ 归到 ISS-211 / 214 / 217 哪条门禁断言

| 归属 | 锚点 | 说明 |
|---|---|---|
| ★**ISS-211** ★ | §10 ★**第 (2) 条** ★ (BAT_DET 分压链全 DNP 但 SoC ADC 脚必装) | ★**F3 是这一族的【板侧配套】**: 同一个 DNP 语义, 侧写 = 板文件里没有 DNP 标记 ⇒ 建议登记为新条目, **与 #2 同批落** ★ |
| ★**ISS-217** ★ | 作业包 (28 条) | ★**F3 在 28 条里【没有】对应条目** (★`grep "exclude_from\|贴片坐标\|CPL" HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` ⇒ 0 命中★) ⇒ **新条目** ★ |
| ★**ISS-214** ★ | §11 附带发现 | — |
| ★**本单门禁** ★ | `HW/check_netlist_contradiction_r3.py` ★**R3-A4** ★ | ★**F3 = A4** ★ |

---

## 4. 附加观察 (R3-A6) —— 留痕, ★不落表★

```
R3-A6 命中 1 条:
  C_VBUS_OUT 是 VBUS_5V_F1 ↔ VBUS_5V_CHG 之间**唯一**的连接件 (电容)
  ⇒ VBUS_5V_CHG 上的 IC ['U_CHG'] 的供电脚没有直流通路
```

· ★**归属**: **V-7** / ★**ISS-214 §4.C 补差C #4 / #6** (充电板整机阶段 **P0**) ★ ⇒ ★**本单只留痕, 不落表** ★
· ★**含义**: `C_VBUS_OUT` 是 100µF **串联**在 BQ25896 的 DC 输入路径上 ⇒ ★**稳态充不了电** (与作业包 §3.6 #6 同一件事) ⇒ **它不是本单 F1 那个"标签撞车"问题** ⇒ ★**F1 改完 ≠ 充电板可投板** ★

---

## 5. 门禁自身在本轮的一处订正 (T0 基线误红) + 反向自证

★**本轮 (14:2x 续做) 只改了门禁的【几何下限判据口径】, 真文件判定一个字节没放宽** ★

### 5.1 根因 (★与派单里写的根因【不同】★)

| | 派单 (brief) 说的 | ★本机实测**★ |
|---|---|---|
| T0 红的根因 | `_green_baseline()` 没补 186 个空封装名 ⇒ `a5["empty_name"]` 非零 | ★**不成立** ★: T0 自测输出里 `R3-A5 empty_name = 0` ⇒ ★**基线本来就补了封装名** (`PKG:<ref>`) ★ |
| ★真根因 ★ | — | ★**`a5["few_lines"]` 非零 = `['J_USB_C']`** ★ ⇒ ★**F2 的触发条件里挂着这一条 ⇒ T0 红** ★ |

★**`few_lines` 为什么会非零**: 几何下限判据只数 `(fp_line` ⇒ `J_USB_C` 的丝印是用 KiCad 的 `(fp_rect` 画的 (0 fp_line + 2 fp_rect) ⇒ ★**旧口径把它判成「没有几何」= 纯误报** ★
★**整板实测**: fp_line<2 的 = 1 个 (J_USB_C) · ★**按【全部 fp_* 图形原语】(fp_line / fp_rect / fp_poly / fp_arc / fp_circle) 数, <2 的 = 0 个** ★

### 5.2 修法 (★落在判据本身, 不许削弱真文件判定★)

| 位置 | 改法 |
|---|---|
| `parse_pcb()` | 增加 `"fp_prim"` = 全部 fp_* 图形原语数 |
| `rule_A5()` | 增加 `few_prim` (★真判据★) · `few_lines` (fp_line 旧口径) **保留在报告里留痕** |
| `analyze()` | ★**F2 的触发条件改用 `few_prim`** (不用 `few_lines`) ★ |

★**为什么不改成「在基线里把 J_USB_C 也补画图形」**: ★**那是拿合成件糊门禁** ★ ⇒ ★**J_USB_C 根本没坏** (2 个 fp_rect 丝印矩形 + 18 个焊盘) ⇒ 真正的问题是判据把它误判了 ★

### 5.3 反向自证 (★在 /tmp 沙盒副本上实跑★)

★**判据 1: 撤掉基线里的「封装名补齐」⇒ T0 必须重新变红 ⇒ 装回去 ⇒ 11/11** ★

```
$ /tmp/iss242_sc/proj (沙盒副本)
  ① 原样           → --selftest: 11 条 · 失败 0 条 · rc=0
  ② 撤掉 _green_baseline() 里的两行封装名补齐 (PKG:<ref>)
                   → --selftest: ❌ T0 红 ⇒ findings=1 (R3-A5 empty_name=186) · rc=1
  ③ 装回去        → --selftest: 11 条 · 失败 0 条 · rc=0
```

★**判据 2: 几何下限不是摆设 (新增 T9)**: ★**把 J_CHG 的 fp_* 图形原语全删掉 ⇒ `few_prim = 1` ⇒ 红** ★
★**判据 3: 反误报 (新增 T10)**: ★**`fp_line == 0` 的封装 (J_USB_C) 几何原语数 = 2 ⇒ 不得被判成「无几何」** ★ ⇒ ★**这条同时证明「fp_rect 计入几何」这条订正是承重的** ★

### 5.4 真文件判定未削弱的证据

| 用例 | 改前 | 改后 |
|---|---|---|
| T7 现状 = 恰 3 条 findings | 3 条 (F1/F2/F3) | ★**3 条 (F1/F2/F3) —— 一条没多一条没少**★ |
| T8 A1/A2/A3/A4 全红 | 1 / 1 / 1 / 43 | ★**1 / 1 / 1 / 43 —— 一条没变**★ |
| 主模式 | rc=1 · 3 条 | ★**rc=1 · 3 条**★ |

---

## 6. 受保护文件 md5 (★本机实跑, 逐字节未变★)

```
34132f7e40a241e1fae1476be0eafbd5  HW/netlist_v1.csv
b21b743a7702d30729f0d653c15392df  HW/netlist_v1_pins.csv
c195a117ff17490d4d1e1a5b8f1995a7  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
```

★**本单改动的文件只有 3 个 (全是新建 / 只读型门禁脚本)** ★:

```
HW/check_netlist_contradiction_r3.py        (门禁脚本: 上一会话落盘 + 本轮修 T0 口径)
HW/NETLIST_CONTRADICTION_R3_CLOSEOUT.md     (本页 · 新建)
HANDOFF/2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md   (交卷单 · 新建)
state/fragments/hw.yaml                     (分片 · 走 state/frag_write.py 原子写)
```

---

## 7. 一句话交卷

★**3 条缺陷逐条定性 + 逐字改法 (生成器行级, 且 F1 的改法已在 /tmp 沙盒实跑验证: 只改 2 行 ⇒ 脚表 md5 逐字节不变 ⇒ R3-A1/A2 绿) + 门禁 rc=1 且恰 3 条 + 反向用例 11/11 (含 T0 基线 0 findings + 撤掉封装名补齐 ⇒ T0 重新变红的反向自证) + 5 个受保护 md5 逐字节未变 + 零落表 + 零外发** ★
