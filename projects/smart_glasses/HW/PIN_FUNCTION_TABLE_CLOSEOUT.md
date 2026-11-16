# ISS-239 · TPS7A20 族 7 颗 LDO 引脚功能名串号 + U_LDO_S28 缺 EN 脚 —— 收口单

> 作者: hw-lead (硬件总工) · 2026-11-16 · **内部活, 不落表, 不碰 PCB 布线/布局, 不代拍老板级决策**
> 本单只做三件事: ① 逐脚对账 ② 根因定性 ③ **可落表的逐行改法映射 + 一个独立机器门禁**
> 交 main 排期落表。**本轮真盘未改任何受保护文件** (5 个 md5 逐字节未变, 见 §7)

---

## 0. 一句话结论

★**脚表里 7 颗 TPS7A20 的 pin4/pin5 共 14 处贴了别的脚的功能名 (串号), 另有 U_LDO_S28 整颗缺 pin3(EN) 脚 ⇒ 共 15 处缺陷。**
★**根因不是一处, 是三层: ① 网表 CSV 层 TPS7A20 的 pin1/pin4 行 `value` 压根没写脚功能名; ② 脚表生成器的元信息索引键是 `(ref, net)` ⇒ 同网多脚时第一个赢 ⇒ pin5 被 pin2 覆盖; ③ 同网名别名对不上时兜底取"器件首行" ⇒ pin4 继承了 EN 行的 value。外加第 0 层: `.net`/板上 7 颗 LDO 的 `Value` 属性本身就是 "EN (pin3)" / "GND (pin2)" ⇒ 贴片程序里没有这个料号。**
⇒ **改法必须同时动 4 个文件, 只改一个都修不干净** (§4)。已在 `/tmp` 副本上实跑验证 (§5)。

---

## 1. 官方 pinout 出处 + 证据分级

| 来源 | 内容 | 证据等级 |
|---|---|---|
| **TI TPS7A20 datasheet `SBVS338H` (2020-03, rev 2024-07)** §4 *Pin Configuration and Functions* → 表 *Pin Functions: X2SON, SOT-23* | X2SON 列: **IN=4 · OUT=1 · EN=3 · GND=2 · Thermal Pad=5** (N/C 只在 SOT-23 的 pin4, X2SON 无此脚) | **[官网]** · 自己去 ti.com 下载 `https://www.ti.com/lit/ds/symlink/tps7a20.pdf` (md5 `24616a278e110d71b3a84f8e311ab5c3`) 复核 |
| 同上 §5.8 Electrical Characteristics | `VEN(LOW) ≤ 0.3 V` 关断 / `VEN(HI) ≥ 0.9 V` 使能; EN 脚内部 **500 kΩ 下拉** | **[官网]** |
| 同上 §7 / 封装图 | 封装代号 **DQN0004A** (X2SON, 1.0×1.0 mm, 0.4 mm max height) | **[官网]** |
| `HW/CORE_MODULE_SELECTION.md` **L15** (表格第 6 行) | `1×1mm X2SON (DQN0004A) · **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘→GND**` | [实测] 仓库内已有记录 |
| `HW/POWER_RAIL_SPEC.md` **L41** (表格 `VDD_3V3_IO` 行) | `**1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(→GND)**` | [实测] 仓库内已有记录 |
| `state/gen_netlist.py` **L707** (生成器注释) | `★真脚号: **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(接 GND)**` | [实测] 生成器注释 |
| 板上 `U_LDO_*` 焊盘数 | 6 颗 = pads 1,2,3,4,5; **U_LDO_S28 = pads 1,2,4,5 (无 pad3)** | [实测] `HW/PCB/demo_mainboard.kicad_pcb` |

⇒ **官方 pinout 判定: `1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(EP, 接 GND)`** —— 三处仓库记录 + TI 官网**四方一致**, 无冲突。

---

## 2. ① 35 行逐脚对账表 (★7 颗 × 5 脚★)

★**判定口径 (不许自己放宽)**: 「脚表 value 与官方功能名不一致」= **错**; 「该脚在脚表里不存在」= **缺**; **不许因为"语义差不多"判成对**。
★**图例**: `✔` 对 · `✘` **错(串号)** · `○` value 未声明任何脚功能名 (器件级型号) ⇒ **提示, 不计 rc** (§6.1) · `★缺脚★` 该脚在脚表里不存在

| 位号 | pin1 (官方 OUT) | pin2 (官方 GND) | pin3 (官方 EN) | pin4 (官方 IN) | pin5 (官方散热焊盘) | 判定 |
|---|---|---|---|---|---|---|
| `U_LDO_S28` | `TPS7A20-28` ○ | `GND (pin2)` ✔ | ★**缺脚★** | `GND (pin2)` ✘ | `GND (pin2)` ✘ | **2 错 + 1 缺** |
| `U_LDO_S18B` | `TPS7A20-18` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |
| `U_LDO_S12` | `TPS7A20-12` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |
| `U_LDO_L33` | `TPS7A20-33` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |
| `U_LDO_L18` | `TPS7A20-18` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |
| `U_LDO_IO33` | `TPS7A20-33` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |
| `U_LDO_IO18` | `TPS7A20-18` ○ | `GND (pin2)` ✔ | `EN (pin3)` ✔ | `EN (pin3)` ✘ | `GND (pin2)` ✘ | **2 错** |

**合计 = 14 处串号 (7 颗 × {pin4, pin5}) + 1 处缺脚 (`U_LDO_S28.pin3`) = 15 处缺陷** ⇒ 与 `HW/check_pin_function_labels.py` 实算清单**逐条一致** (§6.3)。

★**为什么 pin1 判 `○` 而不是 `✘`**: 脚表 `value` 是**自由文本列**, 器件本体行的 value 是**型号** ("TPS7A20-28"), **不声明任何脚功能名** ⇒ 它既不是"对"也不是"串号", 只能是"未声明"。
★**这不是把判据放宽**: 底线三条 (§6.1) 一条没松 —— 5 个脚**必须齐全**、**声明了功能名的必须逐脚对得上**、**引脚号不得指向别的脚**。pin1 既齐全、也没声明、也没串号 ⇒ 不该被点名。
★**但 pin1 确实"没体现官方功能名 OUT"** ⇒ 所以它在门禁里以 **7 条 `NO_FUNCTION` 提示**打印出来, **不掩盖**; §4 的改法 v1 也把它列为**建议项** (改它会炸 BOM, 见 §4.3 ⇒ 建议**不做**)。

### 2.1 网表 CSV 层 (`HW/netlist_v1.csv`) 那 7 颗的 pin1/pin4/pin5 行本身 value 是什么 (★第二层, 与脚表不是一回事★)

| 位号 | 网表 CSV 行号 | `value` | 判定 |
|---|---|---|---|
| `U_LDO_S28` | **L91** (pin1) | `2.8V` | ★**轨电压, 不是脚功能名** ★ |
| `U_LDO_S28` | **L92** (pin4) | `5.0V (F13: 由 CARRIER_BOARD_EN 门控)` | ★**轨描述, 不是脚功能名** ★ |
| `U_LDO_S28` | L93 (pin2) | `GND (pin2)` | ✔ 对 |
| `U_LDO_S28` | L94 (pin5) | `散热焊盘 (pin5, EP)` | ✔ **对** (★所以第 1 轮那个"同 ref 同 net 复制"的说法解释不了 pin5★) |
| `U_LDO_S28` | L95 (器件行) | `TPS7A20-28` | ✔ 对 |
| 6 颗其余 LDO | **L100/L101/L110/L111/L120/L121/L130/L131/L140/L141/L150/L151** (pin1/pin4) | `1.8V`/`1.2V`/`3.3V`/`5.0V (F13: …)` | ★同上: 轨描述, 不是脚功能名★ |
| 6 颗其余 LDO | L102/L112/L122/L132/L142/L152 (pin3) | `EN (pin3)` | ✔ 对 |
| 6 颗其余 LDO | L103/L113/L123/L133/L143/L153 (pin2) | `GND (pin2)` | ✔ 对 |
| 6 颗其余 LDO | L104/L114/L124/L134/L144/L154 (pin5) | `散热焊盘 (pin5, EP)` | ✔ 对 |

⇒ ★**"网表本身没写功能名" 与 "脚表复制错" 是两回事, 改法必须同时覆盖这两层** —— 这是本单的核心结论之一。

---

## 3. ② 根因定性 (★查到代码行★)

### 3.1 缺陷 ① · 脚表生成器的元信息索引**键选错了** ⇒ 同网多脚时"第一个赢"

`state/gen_netlist_pins.py` **L142~L147**:

```python
    # (ref, net) → 元信息
    meta: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (cell(r, "ref"), cell(r, "net"))
        if key not in meta:
            meta[key] = r          # ★首行获胜★
```

★**实测**: `HW/netlist_v1.csv` 里 `(ref, net)` 键 ≥2 行的组 = **36 组** (自己重扫, 不照抄)。
★**其中 7 组就是这 7 颗 LDO 的 GND 组** —— pin2 行 (L93 类) 与 pin5 行 (L94 类) **net 都是 `GND`、ref 都是同一个 LDO** ⇒ 索引里只剩 pin2 那行 ⇒ **pin5 继承了 pin2 的 value `"GND (pin2)"`, 自己的 `"散热焊盘 (pin5, EP)"` 被丢掉**。
★**这解释了脚表 pin5 为什么错, 但解释不了 pin4** ⇒ 继续往下查。

### 3.2 缺陷 ② · 同网别名对不上时**兜底取"器件首行"** ⇒ pin4 继承了 EN 行

`state/gen_netlist_pins.py` **L210~L221**:

```python
    ref_first: dict[str, dict] = {}          # ★该 ref 的【第一行】★
    for r in rows:
        rr = cell(r, "ref")
        if rr and rr not in ref_first:
            ref_first[rr] = r
    ...
        m = meta.get((n["ref"], n["net"]))     # L218 ★按 (ref, .net 的网名) 查★
        if m is None:
            m = ref_first.get(n["ref"], {})     # L220 ★落空 ⇒ 取器件首行★
            fallback += 1
```

★**为什么落空**: `.net` 里的网名是 **`BOARD_5V`**, 而 CSV 的 `net` 列写的是 **`SYS_PCB`** ⇒ `meta[("U_LDO_S18B","BOARD_5V")]` 查不到 ⇒ 走 L220。
★**兜底拿到的是谁**: `ref_first["U_LDO_S18B"]` = CSV 里 ref 列 == U_LDO_S18B 的**第一行** = **L102 (pin3 行, value `EN (pin3)`)** ⇒ **pin4 继承了 pin3 的 value ⇒ 串号**。
★**对 `U_LDO_S28`**: 它没有 pin3 行 ⇒ `ref_first["U_LDO_S28"]` = **L93 (pin2 行, value `GND (pin2)`)** ⇒ **pin4 继承了 pin2 的 value ⇒ 串号 (换个样子)**。
⇒ ★**这就是第 1 轮"同 ref 同 net 复制"假设解释不了的那一半** —— 两处缺陷**叠加**, 且**互相掩盖**: 6 颗 LDO 的 pin4 被 EN 行覆盖, U_LDO_S28 的 pin4 被 GND 行覆盖, 而 pin5 被同网首行覆盖。

★**可复现的最小例子 (不靠任何外部结论, 直接跑得出来)**:
```
.net  net=BOARD_5V  node(ref=U_LDO_S18B, pin=pin4)   # 网名 BOARD_5V
CSV   L101: net=SYS_PCB  ref=RAIL_BOARD_5V  node2=U_LDO_S18B pin4  value="5.0V (F13: …)"
CSV   L102: net=SYS_PCB  ref=U_LDO_S18B     node1=U_LDO_S18B pin3  value="EN (pin3)"   ← ref_first 命中这行
⇒ meta.get(("U_LDO_S18B","BOARD_5V")) = None ⇒ 兜底 ref_first ⇒ value = "EN (pin3)" ⇒ 脚表 U_LDO_S18B.pin4 = "EN (pin3)"
```

### 3.2b 附: `note` 列**也一起串了** (★同一根因, 同一处修★)

★**实测**: 脚表里 6 颗 LDO 的 `pin4` 行, `note` 逐字复制了 `pin3` 行的 EN/P0 文案 (`★★**P0: EN 内部 500kΩ 下拉, 悬空 = 关断...`); `pin5` 行的 `note` 复制了 `pin2` 行的 GND 文案 (`★**之前网表里根本没画 GND ⇒ 悬空**`); `U_LDO_S28.pin4` 的 note 也是 pin2 的 GND 文案。
⇒ ★**`value` 与 `note` 是同一份 metadata 里的两个字段** ⇒ ★**§4 的 F3 一改, `note` 跟着一起修好** ⇒ **不需要额外改动** ★
⇒ ★**但要注意**: `note` 串号 ⇒ ★**评审对图/脚表审计时, 读 pin4 的 note 会读到"这是 EN 脚"的文案 ⇒ 比 `value` 更容易误导人** ⇒ 修复优先级同 `value` ★

### 3.3 缺陷 ③ · 网表 CSV 层 TPS7A20 的 pin1/pin4 行**压根没写脚功能名**

`state/gen_netlist.py`:
- **L683~L689**: pin1 (输出) 行 ⇒ `value = r.get("volt","")` ⇒ 写的是**轨电压** ("2.8V"), **不是 "OUT (pin1)"**
- **L690~L696**: pin4 (输入) 行 ⇒ `value = "5.0V (F13: 由 CARRIER_BOARD_EN 门控)"` ⇒ 写的是**轨描述**, **不是 "IN (pin4)"**
⇒ ★**即使把缺陷 ①② 全修好, 脚表 pin4 只会变成 `"5.0V (F13: …)"` —— 仍然不是脚功能名** ⇒ ★**三层必须一起改**。

### 3.4 缺陷 ④ (★第 0 层·产线风险★) · `.net` / 板 / 原理图的 `Value` 属性 = 脚功能名

`state/gen_kicad_net.py` **L144~L162**: `comp()` 用"**该 ref 的第一行**"的 value 当器件 Value ⇒
- `HW/netlist_v1.net`: `(comp (ref "U_LDO_S28") (value "GND (pin2)"))` · 其余 6 颗 `(value "EN (pin3)")`
- ⇒ **板上 7 颗 LDO 的 `Value` 属性实测就是 `"GND (pin2)"` / `"EN (pin3)"`** (`HW/PCB/demo_mainboard.kicad_pcb`, 各 footprint 的 `(property "Value" …)`)
⇒ ★**贴片程序按 Value 匹配元件 ⇒ 板上没有"TPS7A20-33"这个料号 ⇒ 这一层不修, 脚表修好了贴片还是对不上**。
⇒ ★**旁证**: `HW/BOM_v1.csv` **L215** (U_LDO_S28 行) 的 memo 已经写明这件事: `★封装/型号: 板文件封装 U_LDO_S28 的 Value 属性 = 'GND (pin2)' (4 焊盘: 1,2,4,5) ⇒ **该属性里没有型号** ⇒ opn 标 [0数据]` ⇒ **BOM 那边早就发现了, 没人修根因**。

### 3.5 为什么 `state/check_sch_pinfull.py` 的「584 = 584」抓不到这些

`state/check_sch_pinfull.py` 的判据是**逐器件比对【KiCad 导出网表里的 node 数】 vs 【脚表里该 ref 的行数(含 DNP)】**。

★**根因**: 原理图符号脚数与脚表脚数**同源派生** —— 两者都由 `state/gen_netlist.py` 那一族生成器产出 ⇒ **同一个错误在两边同时出现 ⇒ 两边一样 ⇒ 584 = 584 一样过**。
★**更具体**: `U_LDO_S28` 的 pin3 在网表里就没有 ⇒ 原理图符号**也**没有 pin3 ⇒ 脚表**也**没有 ⇒ 三方一致地少一个脚 ⇒ 尺子量的是"少得一样多"。
★**而且这把尺子量的是【数量】不是【语义】**: pin4 上写 "EN (pin3)" 还是 "IN (pin4)", **都算 1 个脚** ⇒ 串号天然测不出来。
⇒ ★**所以新门禁不能只查脚数, 得查【脚的功能名】** ⇒ 这就是 `HW/check_pin_function_labels.py` 存在的理由 (§6)。

### 3.6 附: `state/check_netlist.py` / `state/check_netlist_pins.py` 也抓不到

实测: 这两个脚本**源码里不出现 `kicad_pcb` / `pad` / `footprint`** ⇒ **它们根本不碰板** ⇒ 板↔网表焊盘级等价由 `state/check_pcb_nets.py` 管 (判据 C1/C3)。
⇒ ★**落表批次必须一并跑 `state/check_pcb_nets.py`** —— 这是 §4 里 A/B 两案代价差异的**决定性判据**。

---

## 3.7 ④ 同网多脚清单与定性 (★38 组 / 16 颗器件 —— 自己重扫, 不照抄 main 的数★)

★**为什么列这个**: §3.1 的元信息索引键是 `(ref, net)` ⇒ ★**只要一个器件有两个脚在同一网上, 它们就共用一行元信息** ⇒ 这是本类缺陷的"温床" ⇒ ★**必须把全部同网多脚的组列出来逐组判, 不许只报 TPS7A20 那 7 组, 也不许把全部组都说成 bug** ★

★**三个口径 (★自己实测·★和 main 派活单里那个"26 组 / 14 颗"的差额【逐组可解释】, 不是事实分歧★)**:
- **口径 A** `HW/netlist_v1.csv` 里 (ref, net) 键 ≥2 **行** 的组 = **36 组** (含伪 ref `RAIL_*` / `NET_*` / `TP_*` / `CHG_GND_STAR`; 排除伪 ref = **25 组 / 17 颗**)
- **口径 B** `HW/netlist_v1_pins.csv` 里 (ref, net) 键 ≥2 **脚** 的组 = **38 组 / 16 颗器件** ⇒ ★**本节下面那张表用的是口径 B (脚表侧, 因为本单查的是脚表)** ★
- **口径 C** main 派活单给的 **26 组 / 14 颗** ⇒ ★**是脚表侧 (口径 B) 的一个【不完整子集】, 差 12 组** ★

★**口径 B 与口径 C 的 12 组差额, 逐组可解释 (★自己逐器件对出来的★)**:

| 器件 | main 的组数 | 脚表实测组数 | 差额在哪 | 说明 |
|---|---|---|---|---|
| `J_USB_C` | **0** | **4** | GND / NET_USB_D_N_TYPEC / NET_USB_D_P_TYPEC / RAIL_DEMO_5V | ★**main 名单里没有这颗器件** ★ (demo 板 USB-C 座) |
| `U_SUPV` | **0** | **1** | VDD_1V8_IO | ★**main 名单里没有这颗器件** ★ |
| `U_CHG` | 4 | **5** | 少 `SYS_CHG` | |
| `U_LDO_*` 6 颗 | 各 **1** | 各 **2** | 少 `BOARD_5V` 组 | ★★★**main 漏掉的 6 组, 恰恰就是 pin4 串号所在的那 6 组** ★★★ |
| `U_LDO_S28` | 1 | 1 | — | 一致 |
| 其余 (CONN_CAM 3 / CONN_LIGHT 2 / J_CHG 3 / J_SOM_P3 1 / J_TYPE_C 5 / U_TEMP 1) | 一致 | 一致 | — | ✔ |

⇒ ★★**本节最重要的一条结论 (★★这解释了任务书里说的"那两点互相矛盾"★★)**:
★**main 的 26 组名单 (按网表 CSV 的 (ref,net) 碰撞统计) 只能看到 pin5, 看不到 pin4** —— 因为 ★**pin3 与 pin4 那两行在网表 CSV 里的 `ref` 列根本不同** (pin3 行 `ref=U_LDO_S18B` · pin4 行 `ref=RAIL_BOARD_5V`) ⇒ ★**它们压根不是 (ref, net) 碰撞** ⇒ ★**"同 (ref,net) 复制"这个假设按它自己的口径去查, 永远查不到 pin4** ★
⇒ ★**所以: pin5 = 真复制 ((ref,net) 首行获胜); pin4 = 假复制 (网名别名对不上 ⇒ 查不到 ⇒ 兜底取器件首行) ⇒ 两个不同机制, 必须分开修** ★

★**定性口径 (三条, 不放宽)**:
1. **语义错 (串号)**: 脚表 value **声明了脚功能名**, 但那个功能名/引脚号**不是本脚的** ⇒ ★**本单必须修** ★
2. **措辞差**: value 在同一网的不同脚之间**措辞不同**, 但**没有声明任何脚功能名** ⇒ ★**不修, 但在改法里顺带被纠正 (实测会变) 要知道** ★
3. **语义无害**: value 是网名/轨描述/器件描述, **不声明脚功能名** ⇒ ★**不是 bug** ★

| # | 位号 | 网 | 脚数 | 脚表 value | 判定 |
|---|---|---|---|---|---|
| 1 | `CONN_CAM` | GND | 8 | GND | 语义无害 |
| 2 | `CONN_CAM` | LIGHT_3V3 | 2 | 3.3V | 语义无害 |
| 3 | `CONN_CAM` | LIGHT_5V | 2 | 5.0V | 语义无害 |
| 4 | `CONN_LIGHT` | GND | 8 | GND | 语义无害 |
| 5 | `CONN_LIGHT` | LIGHT_3V3 | 2 | 3.3V | 语义无害 |
| 6 | `J_CHG` | BAT_CHG | 2 | 跨铰链 1.5A (双 pin 并联) | 语义无害 |
| 7 | `J_CHG` | GND | 2 | 回流 (双 pin) | 语义无害 |
| 8 | `J_CHG` | NC | 3 | 预留 (NC) | 语义无害 |
| 9 | `J_SOM_P3` | RAIL_DEMO_5V | 7 | 5-13V 输入 (SoM 侧) | 语义无害 |
| 10 | `J_TYPE_C` | GND | 5 | Type-C 16p 座 (物理脚位 A/B 编号) | 语义无害 |
| 11 | `J_TYPE_C` | NC | 2 | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | 语义无害 |
| 12 | `J_TYPE_C` | USB_D_N | 2 | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | 语义无害 |
| 13 | `J_TYPE_C` | USB_D_P | 2 | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | 语义无害 |
| 14 | `J_TYPE_C` | VBUS_5V | 4 | Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号) | 语义无害 |
| 15 | `J_USB_C` | GND | 4 | GND (4 脚 + shell) | 语义无害 |
| 16 | `J_USB_C` | NET_USB_D_N_TYPEC | 2 | Type-C 16p 座 (demo 板 5V 输入 + USB 数据) | 语义无害 |
| 17 | `J_USB_C` | NET_USB_D_P_TYPEC | 2 | Type-C 16p 座 (demo 板 5V 输入 + USB 数据) | 语义无害 |
| 18 | `J_USB_C` | RAIL_DEMO_5V | 4 | Type-C 16p 座 (demo 板 5V 输入 + USB 数据) | 语义无害 |
| 19 | `U_CHG` | BAT_CHG | 2 | BQ25896 | 语义无害 |
| 20 | `U_CHG` | NC | 2 | BQ25896 | 语义无害 |
| 21 | `U_CHG` | PGND | 2 | BQ25896 | 语义无害 |
| 22 | `U_CHG` | SW | 2 | BQ25896 | 语义无害 |
| 23 | `U_CHG` | SYS_CHG | 2 | BQ25896 | 语义无害 |
| 24 | `U_LDO_IO18` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 25 | `U_LDO_IO18` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 26 | `U_LDO_IO33` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 27 | `U_LDO_IO33` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 28 | `U_LDO_L18` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 29 | `U_LDO_L18` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 30 | `U_LDO_L33` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 31 | `U_LDO_L33` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 32 | `U_LDO_S12` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 33 | `U_LDO_S12` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 34 | `U_LDO_S18B` | BOARD_5V | 2 | EN (pin3) | ★**语义错 (串号)** ⇒ 脚 ['pin4'] 的 value 贴了别的脚的功能名 |
| 35 | `U_LDO_S18B` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 36 | `U_LDO_S28` | GND | 2 | GND (pin2) | ★**语义错 (串号)** ⇒ 脚 ['pin5'] 的 value 贴了别的脚的功能名 |
| 37 | `U_SUPV` | VDD_1V8_IO | 2 | [待选型] 电压监控 + 复位 (TPS3808G01 类) | 语义无害 |
| 38 | `U_TEMP` | GND | 2 | TMP117 数字温度计 | 语义无害 |

合计 38 组 / 16 颗器件
其中 TPS7A20 族 = 13 组 (6 颗×2 组 + U_LDO_S28×1 组)

★**结论**: ★**38 组里只有 13 组 (7 颗 TPS7A20) 是语义错** ⇒ 对应 **14 处串号** (★13 组里 `U_LDO_S28` 的 GND 组 3 个脚共用 ⇒ 点名 2 个: pin4 + pin5; 其余 6 颗各 2 组各点名 1 个 ⇒ 6×2 + 2 = 14★)。
★**其余 25 组全是语义无害或措辞差 —— 不许说成 bug** ★
★**其中 2 组是"措辞差"且实测会被改法顺带纠正**: `J_CHG` 的 NC 组 3 个脚, 脚表写 `预留 (NC)`, 网表 CSV 写 `预留 (不装)` ⇒ 改法 ③ 实跑后变成 `预留 (不装)` ⇒ ★**这不是缺陷, 是两条同义写法选了一边, 改法落地时会统一到网表那一边的措辞** ★
★**另外 4 组值得 main 知会 (但本单不判为缺陷)**: `U_TEMP` 的 GND 组 2 个脚 (`TMP117 数字温度计` vs 网表的 `TMP117 ADD0 (地址选择)`) 与 `U_SUPV` 的 VDD_1V8_IO 组 2 个脚 ⇒ 改法 ③ 实跑后这两处**会变得更准确** (各自脚的真实功能) ⇒ ★**是变好, 但要记账, 因为脚表 value 变了 ⇒ 脚表 md5 变 ⇒ 锚点要重锚** ★

---

## 4. ③ 改法映射 v1 (★交 main 排期落表·本轮不落表★)

### 4.0 一览 (★4 个文件, 少一个都修不干净★)

| # | 文件 | 改哪一行 | 改成什么 | 依据 |
|---|---|---|---|---|
| **F1** | `state/gen_netlist.py` | **L690~L696** (pin4 输入行) | `value` 由 `"5.0V (F13: 由 CARRIER_BOARD_EN 门控)"` 改为 **`f"IN (pin{_in_pin})"`** (★**只对 `part.startswith("TPS7A20")` 生效★; 轨描述保留在 note 里) | 官方 pinout 4=IN [官网] + §2.1 |
| **F2** | `state/gen_netlist.py` | **L710** (`if ref != "U_LDO_S28":`) | ★**见 §4.2 的 A/B 两案★** | §4.2 |
| **F3** | `state/gen_netlist_pins.py` | **L142~L147** (索引) + **L210~L221** (取数) | 索引键 `(ref, net)` → **`(ref, pin)`**, 且**只认【ref 列 == 该器件】的行**; 取数顺序: `meta_own[(dev,pin)]` → `meta_wire[(dev,pin)]` (**仅当它声明了脚功能名**) → `meta_net[(ref,net)]` (旧口径兜底) → `meta_dev[ref]` | §3.1/§3.2 + §5 实测 |
| **F4** | `state/gen_kicad_net.py` | **L149~L162** (器件表 value 选取) | ★**只在【当前 value 声明了脚功能名】时**才换成**器件本体行**的 value ⇒ 板上 7 颗 LDO 的 `Value` 变回 `TPS7A20-33` 等 | §3.4 + §5 实测 |

★**实测过、必须照做的两条约束 (踩过才知道)**:
- ★**F3 里"只认器件自己的行"这条限定不能省** ⇒ 去掉它就变成候选 ①, 实测影响 **142/584 脚 / 31 颗器件**, 且**多数是变差** (例: `CONN_CAM.pin11` 的 value 会从 `'GND'` 变成 `'100nF ±10%'` —— ★**把电容的值贴到了连接器的脚上**★)。详见 §5.1。
- ★**`pin1` 不要一起改** (F1 只改 pin4) ⇒ 改 pin1 会让脚表 pin1 行的 `type` 从 `'IC'` 变成 `'RAIL'` ⇒ `state/gen_bom.py::_pick_value` (L143) 靠【`type != 'NET'` 的那行】认器件本体行 ⇒ **BOM 的 value 会变成 `"OUT (pin1)"`、type 变成 `RAIL`、采购状态变成"待分类" ⇒ BOM 直接坏掉**。★**实测踩到过, 已撤回**。

### 4.1 改完脚表那几行长什么样 (★/tmp 副本实跑输出★)

| 位号 | pin1 | pin2 | pin3 | pin4 | pin5 |
|---|---|---|---|---|---|
| `U_LDO_S28` | `TPS7A20-28` (不变 ○) | `GND (pin2)` | `EN (pin3)` ←**新增** | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_S18B` | `TPS7A20-18` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_S12` | `TPS7A20-12` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_L33` | `TPS7A20-33` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_L18` | `TPS7A20-18` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_IO33` | `TPS7A20-33` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |
| `U_LDO_IO18` | `TPS7A20-18` (不变 ○) | `GND (pin2)` | `EN (pin3)` | `IN (pin4)` | `散热焊盘 (pin5, EP)` |

★**改完门禁的 35 行矩阵全 `✔`** (★`/tmp` 副本实跑, 见 §5.2★)。

### 4.2 ★U_LDO_S28 缺 pin3(EN) 的 A / B 两案 (★各给代价, 不代拍★)

★**先说一条硬事实 (两边都要面对)**: 板上 `U_LDO_S28` 的封装实测只有 **pads 1,2,4,5 —— 没有 pad3** (`HW/PCB/demo_mainboard.kicad_pcb`); 其余 6 颗是 pads 1,2,3,4,5。
★**EN 脚内部 500 kΩ 下拉 ⇒ 不接 = 关断** ⇒ **这颗 DNP 器件一旦要装, 必须补 EN**。

| | **A 案: 去掉 `if ref != "U_LDO_S28"` 例外, 让它也发 EN 行** | **B 案: 保持不发, 但脚表/文档明确写「DNP · 本体只有 4 脚列入脚表」+ 理由** |
|---|---|---|
| **改哪里** | `state/gen_netlist.py` **L710** 去掉 `if ref != "U_LDO_S28":` (⇒ L711 的 `add(...)` 去掉一层缩进) | `state/gen_netlist.py` **L710** **不动**; 改 `state/gen_netlist_pins.py` (加一行注释/元信息) + `HW/BOM_v1.csv` L215 的 memo + 门禁加**显式豁免** |
| **脚表长什么样** | **585 行**; `U_LDO_S28.pin3` = `EN (pin3)` ⇒ 5 脚齐全 | **584 行**; `U_LDO_S28` 只有 pin1/pin2/pin4/pin5 ⇒ ★**脚表里这行永远缺** ★ |
| **脚表/实体一致?** | ✔ 5 脚 = 官方 5 脚 | ✘ ★**脚表 4 脚 ≠ 官方 5 脚** ★ (⇒ 必须靠豁免说明) |
| **★代价 1: 板★** | ★★**板封装 `U_LDO_S28` 没有 pad3 ⇒ 网表↔板焊盘级不等价** ★★ ⇒ **必须同时给板补 pad3** (板文件改动 = 布线/布局域, **本单不许碰**) | ★**零板改动** ★ (板本来就没有 pad3 ⇒ 不动板就不产生不一致) |
| **★代价 2: 门禁★** | ★**闸必须把 `U_LDO_S28.pin3` 从"缺脚"改成"合格"** ⇒ 缺陷清单清零 ⇒ **默认模式 rc=0** | ★**闸必须给 `U_LDO_S28.pin3` 开一条【显式豁免】(带理由 + 出处)**, 否则闸永远红 ⇒ **闸的"5 脚齐全"底线要开一个口子** ⇒ ★**这等于把"底线"开了一条缝, 必须写进门禁源码并留出处★** |
| **代价 3: 脚数基线** | ★**脚表 584 → 585** ⇒ `state/check_sch_pinfull.py` 的基线数变 (原理图也要同步重生成) ⇒ **属于落表批次的事, 本单不改** | ★**脚表仍 584 ⇒ 脚数基线不动** ★ |
| **代价 4: 一致性风险** | ★**这颗是 DNP (camera 模组自带稳压 ⇒ 主板不供 sensor 模拟轨) ⇒ 实际不装 ⇒ 补 pad3 是为"以后可能要装"预留** ⇒ ★**为一颗不装的器件动板, 性价比要 main 判** ★ | ★**风险留在这颗身上**: 哪天要装这颗 ⇒ 板没 pad3 ⇒ 只能飞线 ⇒ **且 EN 不接 = 关断 ⇒ 装上去也不工作** ⇒ ★**必须在 BOM/文档里写死这条** ★ |
| **★实测依据★** | ★**已实跑**: A 案下板↔网表焊盘级比对 ⇒ **7 颗里恰好 1 颗 (`U_LDO_S28`) 不等价**: 网表要求 pad 3, 板上没有 ⇒ `state/check_pcb_nets.py` 的 C1「缺失」+ C3「板上焊盘数 4 ≠ 网表脚数 5」**会红** ★ | ★**已实跑**: B 案下脚表仍 584 行, 板不动 ⇒ 无不一致; 但**闸必须带豁免** ★ |

⇒ ★**我的倾向 (供 main 参考, 不是拍板)**: **B 案**。
理由: ① `U_LDO_S28` 是 **DNP** (camera 模组自带稳压), ★**为了颗不装的器件去动板封装 = 把成本花在用不上的地方**; ② A 案会把 `state/check_pcb_nets.py` 拉红, 落表批次要多改一个板文件 + 重跑布线 DRC, **风险面直接翻倍**; ③ B 案只需要在门禁里留一条**带出处的显式豁免**, 板一行不动。
⇒ ★**但 B 案有硬代价: 闸的"5 脚齐全"底线要开口子** ⇒ 若 main 选 B, **豁免必须写进门禁源码 + `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` + BOM memo**, 不许只在聊天里说一句。
⇒ ★**若 main 选 A**: 必须同时排上 **① 给 `U_LDO_S28` 封装补 pad3 (板域, 需布线/DRC 复跑) ② 脚表 584→585 ③ `check_sch_pinfull.py` 基线 584→585 ④ 原理图重生成**。

### 4.3 pin1 要不要一起改成 `OUT (pin1)` (★建议: 不改★)

- **好处**: 脚表 7 颗的 pin1 就真的"体现了官方功能名 OUT", `NO_FUNCTION` 提示清零, 脚表彻底自洽。
- **代价 (★实测踩到★)**: 脚表 pin1 行的 `type` 会从 `'IC'` 变成 `'RAIL'` ⇒ **`state/gen_bom.py::_pick_value` (L143) 靠【`type != 'NET'` 的那行】认器件本体行 ⇒ 认不到了 ⇒ BOM 的 value 变成 `"OUT (pin1)"`、type 变成 `RAIL`、采购状态变成"待分类" ⇒ ★**BOM 直接坏掉**★**。实测: 7 颗 LDO 的 BOM 行全变。**
- ⇒ ★**建议: 本轮不改 pin1**。若一定要改, **必须同时改 `state/gen_bom.py::_pick_value`**, 让它认**器件本体行** (node 串里出现裸位号的那行) 而不是"type != NET 的那行" ⇒ **那是一次独立的 BOM 生成器口径变更, 应单独开单, 不要混进 ISS-239 落表批次**。

---

## 5. ④ `/tmp` 副本实跑验证 (★真盘未动★)

★**副本**: `cp -a` 整棵树到 `/tmp/iss239_rehearsal/smart_glasses` (★不是只 cp 几个文件★) ⇒ 真盘 5 个 md5 全程未变 (§7)。

### 5.1 三个候选改法的**实测影响面** (★这是本单最硬的证据★)

| 候选 | 脚表 value 变化 | 脚表行数 | `.net` comp value 变化 | BOM 变化 | 判定 |
|---|---|---|---|---|---|
| **① 索引键 (ref,net) → (ref,pin), 全域** | ★**142 脚 / 31 颗器件** ★ | 584 | — | — | ★**否决** ★: 大量**变差** —— `CONN_CAM.pin11` `'GND'` → `'100nF ±10%'` (★**把电容的值贴到连接器的脚上**★) |
| **② 索引键改成 (ref,pin) + 只认【器件自己的行】** | **11 脚 / 10 颗** | 584 | — | — | ★**安全但不够** ★: 只修好 pin5 (7 脚), **pin4 还错** (兜底仍落在 pin3 行) |
| **③ ② + 线行 value 声明了功能名时也采信 + F1 (pin4→"IN (pin4)") + F4 (Value 换器件本体行)** | ★**19 脚 (18 改 + 1 新增)** ★ | **585** | ★**9 / 218 个器件** (7 颗 LDO + 2 颗 DC-DC, **全是变好**) ★ | ★**0 行变化** ★ | ★**采纳 (F1+F3+F4, A 案补 F2)★ ★ |

★**逐脚明细 (候选 ③ 实跑)**:
```
改前 → 改后
U_LDO_S18B.pin4   'EN (pin3)'          → 'IN (pin4)'
U_LDO_S18B.pin5   'GND (pin2)'         → '散热焊盘 (pin5, EP)'
U_LDO_S28.pin4    'GND (pin2)'         → 'IN (pin4)'
U_LDO_S28.pin5    'GND (pin2)'         → '散热焊盘 (pin5, EP)'
U_LDO_S28.pin3    (不存在)             → 'EN (pin3)'          ← 新增
J_CHG.pin9        '预留 (NC)'          → '预留 (不装)'         ← 措辞差, 顺带被纠正
J_CHG.pin10       '预留 (NC)'          → '预留 (不装)'         ← 措辞差
(其余 12 颗 LDO 的 pin4/pin5 同规律)
```

### 5.2 改完后的 35 行 (★/tmp 副本实跑输出·直接贴★)

```
     位号             pin1(OUT)              pin2(GND)              pin3(EN)               pin4(IN)               pin5(THERMAL_PAD)
     U_LDO_S28      ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_S18B     ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_S12      ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_L33      ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_L18      ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_IO33     ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
     U_LDO_IO18     ✔ OUT (pin1)           ✔ GND (pin2)           ✔ EN (pin3)            ✔ IN (pin4)            ✔ 散热焊盘 (pin5, EP)
```
★注: 上表 pin1 那一列在**最终采纳的候选 ③**里是 `TPS7A20-xx` (不变 ○), 这里是**把 pin1 也一并改了**的展示版 ⇒ **pin1 那列请以 §4.1 的表为准** (★改 pin1 会炸 BOM, 见 §4.3★)。

### 5.3 落表后门禁三个模式的预期 (★副本实测★)

| 模式 | 当前基线 | 落表后 (快照同步清空后) |
|---|---|---|
| 默认 | **rc=1** (15 条缺陷) | **rc=0** |
| `--expect-known` | **rc=0** (15/15 逐条一致) | **rc=0** |
| `--selftest` | **rc=0** (10/10) | **rc=0** (10/10) ⇒ ★**fix-point 稳定, 落表后不会变红** ★ |

---

## 6. ⑤ 独立机器门禁 `HW/check_pin_function_labels.py` (★新建·不依赖受保护脚本★)

### 6.1 判据 (★4 类检查 + 三模式★)

| 检查 | 内容 | 底线 |
|---|---|---|
| **① TPS7A20 族逐脚** | 7 颗 × 5 脚: **脚集完整** (缺 ⇒ `MISSING_PIN`) + **声明的功能名 == 官方 pinout** (≠ ⇒ `WRONG_FUNCTION`) + **value 里的 `(pinN)` 指向本脚** (≠ ⇒ 串号) | ★**5 个脚必须齐全; 声明了功能名的必须逐脚对得上; 引脚号不得指向别的脚** ★ |
| **② 同器件功能名不得重复** | 同一器件内两个脚声明同一功能名 ⇒ 点名那个**与官方 pinout 不符**的脚 | ★**限死在 IC 类** ★ (器件级 IC 判定 = 该 ref 的任一行 `type == "IC"`; ★**不限死就误报**: `CONN_CAM` 13 个 GND / `CONN_LIGHT` 8 个 GND / `J_SOM_P3` 12 个 EN / `J_USB_C` 4 个 GND —— 实测 4 类共 37 脚会误报★) |
| **③ 官方 pinout 不许被改软** | 内置 pinout 表带 **SHA256** 基线 (`15fc9f62…`) + **交叉核对仓库两处原文** (`HW/CORE_MODULE_SELECTION.md` L15 / `HW/POWER_RAIL_SPEC.md` L41) | 改表不改摘要 ⇒ 红; 改仓库原文 ⇒ 红 |
| **④ 受保护文件 md5 未变** | 5 个基线写死在脚本里: 网表 / 脚表 / BOM / 板 / `.kicad_pro` | ★**不许为了凑绿改脚本里的基线值** ★ (改基线 = 改代码, 走 review) |

★**"value 一条功能名都没声明" ⇒ 记为 `NO_FUNCTION` 提示, 不计入 rc** —— 理由: 脚表 `value` 是自由文本列, 器件本体行的 value 是**型号**; 若把它判成缺陷, 判据就被放宽成"逐字相等"了。★**但它照样逐条打印出来** (本基线 7 条 = 7 颗的 pin1) ⇒ 不掩盖。
★**底线没有松**: "脚表里没有 IN 就当没有 IN" 这种写法**不在本闸里** —— pin1/pin4 必须**存在**, 缺了就是硬缺陷。

### 6.2 三模式

| 模式 | rc | 行为 |
|---|---|---|
| 默认 (无参数) | **1** (缺陷还在 ⇒ 该红) | 首行固定写 **`★当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿★`**; 打印 35 行对账矩阵 + **15 条缺陷清单** + 7 条提示 + ④ 的 md5 结果 |
| `--expect-known` | **0** | 实算清单与**冻结快照逐条一致** ⇒ 绿; ★**多一条 / 少一条 / 变一条 ⇒ 红** ★ |
| `--selftest` | **0** | **10 条反向用例**, 每条**自证「它真的改到了目标」** (§6.3) |

### 6.3 反向用例清单 (★10 条·★每条都带"自证"★)

| # | 反向用例 | 自证方式 |
|---|---|---|
| T1 | 把 `U_LDO_L33.pin4` 改回 `"EN (pin3)"` ⇒ 仍被点名 | 断言缺陷集合**恰好** = {`U_LDO_L33.pin4`}; ★**并先断言"未改动的合成样本 = 0 缺陷"** ⇒ 证明红确实来自这次改动 |
| T2 | 删掉已知清单里一条 ⇒ `--expect-known` 红 | 用**合成快照**(不依赖真快照 ⇒ 落表后仍有效); 断言差异信息里**指出了被删的那一条** |
| T3 | 篡改内置 pinout 表 ⇒ 红 | 断言篡改后摘要**确实变了** + ③ 号检查**确实报了** |
| T4 | 把 pin4 改成 `"IN (pin4)"` ⇒ 该条从清单里消失 **且** `--expect-known` 红 | 断言该键**不在**实算清单里 + 快照比对**判红** |
| T5 | 篡改受保护 md5 基线 ⇒ 红 | 断言**正常基线必须干净** + 篡改基线后**确实报** ⇒ 证明红来自这次篡改 |
| T6 | 把 IC 限制放宽到无源件 ⇒ 红 | ★**合成一颗 R 器件 3 个脚都声明 GND**: 限死 IC 时**不报**(无误报) + 放宽后**报** ⇒ ★**证明"限死 IC"这条限制是承重的** ★ |
| T7 | 删掉 `U_LDO_S28.pin3` 行 ⇒ 报"缺脚" | 断言 `kind == "MISSING_PIN"` |
| T8 | 补上 `U_LDO_S28.pin3` ⇒ 缺脚消失 **且** `--expect-known` 红 | 断言该键**不在**实算清单里 + 快照比对**判红** |
| T9 | 真盘基线核对 | 断言真盘实算与冻结快照**逐条一致**; ★**快照非空时**必须恰好 15 条 = 14 串号 + 1 缺脚, 且串号集合**恰好** = 7 颗 × {pin4, pin5} ⇒ ★**快照清空后本段 vacuous ⇒ fix-point 稳定** ★ |
| T10 | 已知缺陷快照不许偷改 | 快照的 SHA256 与**硬编码基线**比对 |

★**T1~T8/T10 全部用合成数据或参数化注入**, 不依赖盘面 ⇒ ★**落表后 selftest 仍然是绿的 (已在副本实测)** ★。

---

## 7. ⑥ 落表时机与影响面 (★本单不落任何表★)

### 7.1 落表批次要动的文件 (★按依赖顺序★)

| 序 | 文件 | 动作 | 备注 |
|---|---|---|---|
| 1 | `state/gen_netlist.py` | F1 (L690~696) + F2 (L710, 按 A/B 案) | |
| 2 | `state/gen_netlist_pins.py` | F3 (L142~147 / L210~221) | |
| 3 | `state/gen_kicad_net.py` | F4 (L149~162) | |
| 4 | 重跑生成链 | `gen_netlist.py` → `gen_kicad_net.py` → `gen_netlist_pins.py` → `gen_bom.py` | |
| 5 | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/netlist_v1.net` | **md5 会变** ⇒ 下面 §7.2 的锚点要重锚 | ★**板文件 `.kicad_pcb` 只有 A 案才动** ★ |
| 6 | `HW/check_pin_function_labels.py` | ★**同步更新 `PROTECTED_MD5` 的 5 个基线值** ★ + ★**`KNOWN_DEFECTS` 快照清空 + 其 SHA256 改成空串的 sha256 (`e3b0c442…`)★ | ★**不改这两个 ⇒ 闸会红 ⇒ 这是设计意图** ★ |

### 7.2 ★H-1 重锚影响面 (★两个锚点都在别人的文件里·本单只点名, 不动手★)

| 锚点 | 文件 | 位置 | 为什么会被打到 | 谁改 |
|---|---|---|---|---|
| **#1** | `MECH/HW_CROSS_REVIEW_TRIAGE.md` | **§1** | 引用网表/脚表 md5 | ★**mech-lead** ★ (★**本单不许碰 MECH/ 任何文件** ★) |
| **#2** | `SW/SW_MD5_BASELINE_LEDGER.md` | **§1** | 引用网表/脚表/BOM md5 | ★**sw-lead** ★ (★**本单不许碰 SW/ 任何文件** ★) |

⇒ ★**本单只在这里点名, 由 main 排期通知对应 owner 重锚。**

### 7.3 脚数基线

- ★**当前**: 脚表 **584 行**; `state/check_sch_pinfull.py` 的「584 = 584」由**脚表行数**与**原理图 node 数**同源派生 ⇒ 一起变 ⇒ **本单不动它**。
- ★**A 案 (补 EN 行)**: 脚表 **584 → 585** ⇒ ★**`state/check_sch_pinfull.py` 的基线数随之变, 且原理图必须同步重生成** ⇒ 属落表批次的事。
- ★**B 案**: 脚表仍 **584** ⇒ **脚数基线不动** ★。
- ★**两种情况下, 本单都不许自己改基线**。

### 7.4 ★落表批次必须跑的门禁清单 (★交 main★)

```
python3 state/check_netlist.py           # rc=0
python3 state/check_netlist_pins.py      # rc=0
python3 state/check_sch_erc.py            # rc=0 (ERC=0)
python3 state/check_sch_pinfull.py        # rc=0 (584=584 或 585=585)
python3 state/check_pcb_nets.py           # rc=0  ★A 案下这里会红 ⇒ 板必须先补 pad3★
python3 HW/check_step1_parts_spec.py      # rc=0 (C1~C8)  ★ISS-237 立的闸, 不许被本单改红★
python3 HW/check_pin_function_labels.py            # 落表后 rc=0
python3 HW/check_pin_function_labels.py --expect-known  # rc=0 (快照已同步清空)
python3 HW/check_pin_function_labels.py --selftest       # rc=0 (10/10)
python3 state/merge.py && python3 state/gate_check.py   # rc=0 · 【Q1】18/18
```

---

## 8. ⑦ 证据分级汇总

| 结论 | 等级 | 依据 |
|---|---|---|
| TPS7A20 X2SON 官方 pinout = 1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘 | **[官网]** | TI SBVS338H §4 (ti.com 自查, pdf md5 `24616a27…`) |
| 脚表 14 处串号 + 1 处缺脚 = 15 处缺陷 | **[实测]** | `HW/check_pin_function_labels.py` 实算, 与 §2 对账表逐条一致 |
| 根因 = 索引键 + 兜底 + CSV 层 + `.net` 层 四处 | **[实测]** | §3 每条都给了行号 + 可复现最小例子; 副本实跑验证 (§5) |
| 候选 ① 影响 142 脚 / 31 颗器件且多数变差 | **[实测]** | `/tmp` 副本实跑 diff |
| 候选 ③ 影响 19 脚 / `.net` 9 个器件 / BOM 0 行 | **[实测]** | `/tmp` 副本实跑 diff |
| A 案会拉红板↔网表焊盘级等价 (U_LDO_S28 缺 pad3) | **[实测]** | 副本实跑 + 自己实现的焊盘级比对 (7 颗里恰好 1 颗不等价) |
| 改 pin1 会炸 BOM (value→`OUT (pin1)`, type→RAIL) | **[实测]** | 副本实跑后已撤回 |
| `check_sch_pinfull.py` 抓不到 = 同源派生 | **[实测]** | 读了 `state/check_sch_pinfull.py` 全文 + 读 `state/gen_netlist*.py` 确认派生链 |
| 板上 7 颗 LDO 的 `Value` 属性 = `EN (pin3)` / `GND (pin2)` | **[实测]** | `HW/PCB/demo_mainboard.kicad_pcb` 逐个 footprint 解析 |
| `U_LDO_S28` 板上封装只有 pads 1,2,4,5 | **[实测]** | 同上 |
| `state/check_netlist.py` / `check_netlist_pins.py` 不碰板 | **[实测]** | grep 源码: 无 `kicad_pcb` / `pad` / `footprint` |
| 板↔网表焊盘级等价由 `state/check_pcb_nets.py` 管 (C1/C3) | **[实测]** | 读 `state/check_pcb_nets.py` 判据段 |
| 候选 A/B 的**取舍** | **[推算]** (工程判断, 不是实测) | 代价已全部实测列出; ★**取舍留给 main** ★ |
| 板封装补 pad3 的具体几何 (X2SON 真实焊盘排布 / 散热焊盘尺寸) | **[0数据]** | 本单**未做板几何核算** ⇒ 若选 A, 须开板域单 |

---

## 9. ⑧ 复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# 门禁三模式
python3 HW/check_pin_function_labels.py                # rc=1 (15 条) · 首行写明"rc=1 属预期"
python3 HW/check_pin_function_labels.py --expect-known  # rc=0 (15/15)
python3 HW/check_pin_function_labels.py --selftest       # rc=0 (10/10)

# 35 行对账 (人读)
python3 HW/check_pin_function_labels.py | sed -n '5,16p'

# 网表 CSV 层那 7 颗的 pin1/pin4/pin5 行
grep -n "U_LDO_" HW/netlist_v1.csv | grep -E "pin[145]"

# 根因三处代码行
sed -n '142,147p;210,221p' state/gen_netlist_pins.py
sed -n '690,696p;705,721p' state/gen_netlist.py
sed -n '149,162p' state/gen_kicad_net.py

# 板上 7 颗 LDO 的 Value 属性 + 焊盘号
grep -o '(comp (ref "U_LDO_[^"]*") (value "[^"]*")' HW/netlist_v1.net

# 受保护文件 md5 (必须逐字节不变)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ⇒ 34132f7e40a241e1fae1476be0eafbd5 / b21b743a7702d30729f0d653c15392df /
#    c195a117ff17490d4d1e1a5b8f1995a7 / 611b869e13518c3c023fb178f91a0075 /
#    3e504d2be83152e337949723e909be1b
```

---

## 10. ⑨ 交给 main 的 3 个问题 (★不代拍★)

1. ★**U_LDO_S28 的 pin3 走 A 案还是 B 案?** (§4.2) ⇒ A 要动板 (布线/DRC 域) + 脚数基线 584→585; B 不动板但闸要留一条带出处的豁免。★**我倾向 B, 但代价要说清: B 案的"5 脚齐全"底线会开一条缝** ★
2. ★**pin1 要不要改成 `OUT (pin1)`?** ⇒ 建议**不改** (会炸 BOM, 要改 `gen_bom.py::_pick_value` 口径, 应单独开单)
3. ★**落表批次的排期与 owner**: F1~F4 四个文件 + 重生成链 + `check_pin_function_labels.py` 的 2 处基线 + **MECH `§1` / SW `§1` 两个 H-1 重锚** ⇒ 需要 main 统一排期并通知对应 owner
