# HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md —— ISS-247 · F1 落表作业包 v1

> ★**硬件总工 (hw-lead) · 2026-11-16 18:0x~18:4x · 单号 ISS-247 · verify_by = main (项目总工)** ★
> ★**本单性质: ★只出作业包, 【不落真盘】★** ⇒ ★**真盘网表/脚表/BOM/板/`.kicad_pro` 一个字节都没动** ★
> ★**配套**: `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` (下一批落表清单 v1) · `HW/check_iss247_f1_landed.py` (机器门禁) · `HANDOFF/2026-11-16_hw-lead_ISS247_F1落表作业包v1.md` (交卷单) ★
> ★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02 口径: 不再发信, 全靠自己查资料) · ★**实物 [实测] = 0 条** ★

---

## ★0 一句话

★★**F1 的真改法 = 把 `state/gen_netlist.py` 的 ★L381 / L393 两行 `add()` 的第 4 个参数 (node2 槽)★ 里那个「借来的」裸位号 `C_VBUS_OUT`, 换成本行自己的网名 (`VBUS_5V_F1` / `VBUS_5V_CHG`) ⇒ 两颗 2 脚电容的端子台账各回到 2 次 (= 脚表脚数) ⇒ 脚表 / BOM / `.net` / 板逐字节不变, 只动网表与 `SCHEMATIC_V1.md` 各 2 行** ★★

★★**并且: ★上一轮派单里那个错值「把 `node2` 改成 `C_VBUS_GND`」是错的 ★ ⇒ 本机沙盒实测: 那样改照样红 (一颗 2 脚件的端子被登记 3 次 > 脚数 2) ⇒ 本作业包已把它订正, 并在 §2.3 给出自证** ★★

---

## 1 · 病灶 (逐行 · 逐字)

### 1.1 网表现状 (`HW/netlist_v1.csv` 表A · L1 = 表头 ⇒ L2 = 第一行数据)

| 表A 行 | net | node1 | node2 | ref | 脚表登记 | ★问题★ |
|---|---|---|---|---|---|---|
| **L8** | `VBUS_5V_F1` | `FB_VBUS` | ★**`C_VBUS_OUT`**★ | `FB_VBUS` | `FB_VBUS.2 → VBUS_5V_F1` | ★**node2 借了另一颗 2 脚 C 的裸位号** ★ |
| L9 | `VBUS_5V_F1` | `VBUS_5V_F1` | `C_VBUS_OUT` | `C_VBUS_OUT` | `C_VBUS_OUT.1 → VBUS_5V_F1` | 本器件自己的端子 (合法) |
| L10 | `GND` | `C_VBUS_GND` | `GND` | `C_VBUS_GND` | `C_VBUS_GND.1 → GND` | 本器件自己的端子 (合法) |
| L11 | `VBUS_5V_CHG` | `C_VBUS_OUT` | `U_CHG pin1` | `C_VBUS_OUT` | `C_VBUS_OUT.2 → VBUS_5V_CHG` | 本器件自己的端子 (合法) |
| **L12** | `VBUS_5V_CHG` | `C_VBUS_GND` | ★**`C_VBUS_OUT`**★ | `C_VBUS_GND` | `C_VBUS_GND.2 → VBUS_5V_CHG` | ★**node2 借了另一颗 2 脚 C 的裸位号** ★ |

### 1.2 端子台账爆表 (★`C_VBUS_OUT` 的裸位号被登记 **4** 次, 而它在脚表里只有 **2** 个脚★)

```
L8 : net=VBUS_5V_F1  node2=C_VBUS_OUT (本行 ref=FB_VBUS)    ← 借用
L9 : net=VBUS_5V_F1  node2=C_VBUS_OUT (本行 ref=C_VBUS_OUT)  ← 本体
L11: net=VBUS_5V_CHG node1=C_VBUS_OUT (本行 ref=C_VBUS_OUT)  ← 本体
L12: net=VBUS_5V_CHG node2=C_VBUS_OUT (本行 ref=C_VBUS_GND)  ← 借用
⇒ 登记 4 次 > 脚数 2 ⇒ ★导出后一脚悬空 / 串联对地混在一颗上★ (ISS-242 原文)
```

### 1.3 ★**根因: `node2` 槽混用了两种绑定约定★**

| 约定 | 写法 | 合法性 | 本表实例 |
|---|---|---|---|
| **甲 (器件↔器件直连)** | `node2` = 对方的裸位号 | ★**合法** (例: L40 `R_NTC_BAT` ↔ `R_TS_PULL` = 2脚R 直连分压; L184 `C_DET_BAT` ↔ `R_BAT_DET_2`) | 遍布全表 |
| **乙 (器件↔网)** | `node2` = 网名 (`VBUS_5V_F1` / `GND` / …) | ★**合法** | L6/L7/L10 等 |

★★**F1 的 L8 / L12 误用了【约定甲】, 而且借的那颗 (`C_VBUS_OUT`) 是【2 脚 C】⇒ 它的端子标签在同一个网上被两颗件同时认领 ⇒ 端子台账从 2 变成 4** ★★
★★**注: 表A 里 `C_VBUS_OUT` 这颗 2 脚件共落进 3 个网 (`VBUS_5V_ESD`? 不 · `VBUS_5V_F1` · `VBUS_5V_CHG` · 以及被 L8/L12 借用的第 3 个语义) —— 这就是 ISS-242 说的「一颗 2 脚电容落进 3 个网」的机制** ★★

### 1.4 ★**改完之后这两颗 2 脚电容的正确拓扑 (与脚表完全自洽)★**

```
   J_TYPE_C ── FB_VBUS ──┬── VBUS_5V_F1 ──┬── C_VBUS_OUT ──┬── VBUS_5V_CHG ──┬── U_CHG pin1 (BQ25896 IN)
                          │                │                │                 │
                          │                │                └── C_VBUS_GND ──┴── GND
                          │                └── (C_VBUS_OUT 的第 1 脚在 VBUS_5V_F1)
                          └── C_VBUS_IN (输入对地)
⇒ ★C_VBUS_OUT = 串联电容 (VBUS_5V_F1 → VBUS_5V_CHG) · C_VBUS_GND = 对地电容 (VBUS_5V_CHG → GND)★ ★**π 滤波正确形态** ★
⇒ ★**电气连通性零变化** (脚表 `C_VBUS_OUT.1/.2` 与 `C_VBUS_GND.1/.2` 所属网一个都没动) ⇒ ★`.net` / 脚表 / BOM / 板 全部逐字节不变** ★
```

---

## 2 · ★**落表真源 + 两行逐字改法**★

### 2.1 ★**真源 = `state/gen_netlist.py` (★不是手改 `HW/netlist_v1.csv`★)★

`add()` 的签名 (★`state/gen_netlist.py` L345★):

```python
def add(page, net, node1, node2, ref, value, typ, dnp, ev, tbd, note, cid=""):
```

★**第 4 个参数 = `node2` 槽** ★ ★**F1 落在 ★L381 与 L393 两行的第 4 个参数上** ★
★**★行号以本机 `state/gen_netlist.py` 现值为准 (★`grep -n` 实测, 不许照抄任何旧文里的行号★)★** ★

### 2.2 ★**逐字改法 (★可直接 copy 的字符串★)★**

**★改法 1 —— `state/gen_netlist.py` L381 (FB_VBUS 的后级行)★**

```diff
-    add("P1", "VBUS_5V_F1", "FB_VBUS", "C_VBUS_OUT", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
+    add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
```

**★改法 2 —— `state/gen_netlist.py` L393 (C_VBUS_GND 的信号端行)★**

```diff
-    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "C_VBUS_OUT", "C_VBUS_GND", "[待选型] 100µF", "C",
+    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "VBUS_5V_CHG", "C_VBUS_GND", "[待选型] 100µF", "C",
```

★**两处都只动第 4 个参数 (node2) 的一个字符串, 行数不变, 其余参数一字未动** ★

### 2.3 ★**订正: 上一轮派单给的错值「`node2` → `C_VBUS_GND`」**★

| 候选值 | 结果 | ★本机实测依据★ |
|---|---|---|
| `node2` → `C_VBUS_GND` (★上一轮派单值★) | ★**照样红** ★ | `C_VBUS_GND` 的裸位号会被登记 **3** 次 (L10 node1 + L12 node1 + L12 node2) > 脚数 2 ⇒ 同样的「一颗 2 脚件落进 3 个网」没解决, 只是把撞车从 `C_VBUS_OUT` 挪到 `C_VBUS_GND` ★ |
| `node2` → `VBUS_5V_CHG` (★本作业包★) | ★**绿** ★ | 登记次数回到 2 (= 脚数) ⇒ 且 node2 = 本行自己的网名 ⇒ 与 `net` 列同网自洽 ★ |

★**自证原文 (★本机沙盒 `sb1` 实跑 `HW/check_netlist_contradiction_r3.py --selftest`★)** ★

```
  ✅ T2 把 L12 的 node2 改成 C_VBUS_GND (main 提的值) ⇒ 期望 A1 红 (一颗件登记 3 次)
       A1=1
  ✅ T3 把 L8 的 node2 改回 C_VBUS_OUT ⇒ 期望 A1 红 (C_VBUS_OUT 登记 3 次)
       A1=1
```

★**⇒ 两个改法缺一不可 (只改一处仍红), 且必须改成【自己的网名】而不是【对方的裸位号】** ★

### 2.4 ★**改完后 6 条语义判据全绿 (★由 `HW/check_iss247_f1_landed.py` 判★)★**

| 判据 | 含义 | 改前 | 改后 |
|---|---|---|---|
| **S1** | `C_VBUS_GND` 信号端行的 `node2` == 它自己的网名 (`VBUS_5V_CHG`) | ❌ 红 | ✅ 绿 |
| **S2** | `C_VBUS_OUT` 串联端行的 `node2` 是物理脚 (`U_CHG pin1`) 或自己的网名 | ✅ 绿 | ✅ 绿 |
| **S3** | `FB_VBUS` 后级行的 `node2` == 它自己的网名 (`VBUS_5V_F1`) | ❌ 红 | ✅ 绿 |
| **S4** | (通用·等价 R3-A1) 每颗 2 脚 C 的端子登记次数 ≤ 脚表脚数 | ❌ 红 (4 > 2) | ✅ 绿 |
| **S5** | (通用·等价 R3-A2) 2 脚 C 之间的裸位号对端撞车 | ❌ 红 | ✅ 绿 |
| **S6** | (反误报护栏) 2 脚 R/L/D 的合法器件↔器件直连不得判红 | ✅ 绿 | ✅ 绿 |

---

## 3 · 影响面 (★各文件变几行 · 新旧 md5★)

### 3.1 ★**逐文件影响 (★本机 `/tmp` 沙盒整树实跑, ★见 §4★)★**

| 文件 | 变几行 | 旧 md5 | 新 md5 | 说明 |
|---|---|---|---|---|
| `state/gen_netlist.py` | ★**2 行** (L381 / L393 各改 1 个字符串) ★ | ★(真源, 见 §5 复现命令里的 `md5sum`)★ | ★(落表时重算)★ | ★**唯一的真源改动** ★ |
| `HW/netlist_v1.csv` | ★**2 行** (表A **L8** / **L12** 的 `node2` 列) ★ | `611c3ba3db3dc7de7213063375b96d01` | `16ac89f77c25a3f61834cc7ebcd78a7f` | ★**网表 md5 变** ★ |
| `HW/netlist_v1_pins.csv` | ★**0 行** ★ | `ef436a37412ac9b6eac3c9f41f1edca4` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**逐字节不变** (脚表脚网一个没动) ★ |
| `HW/BOM_v1.csv` | ★**0 行** ★ | `2a7305741134788dfee9f13f34c656b4` | `2a7305741134788dfee9f13f34c656b4` | ★**逐字节不变** (位号/阻值/DNP 全没动) ★ |
| `HW/netlist_v1.net` | ★**0 行** ★ | `564fed05c1f5f9dab09efce51eebae74` | `564fed05c1f5f9dab09efce51eebae74` | ★**逐字节不变** ⇒ 电气连通性零变化 ★ |
| `HW/PCB/demo_mainboard_sch.net` | ★**0 行** ★ | `bdc3f463…` | `bdc3f463…` | ★**逐字节不变** ★ |
| `HW/SCHEMATIC_V1.md` | ★**2 行** (★表A 镜像的两行★) ★ | `289fbafa2874588412cf292b469c73fc` | `d37bbd0d8fb0754f038c734adb11316d` | ★**原理图页跟着改** ★ |
| `HW/PCB/demo_mainboard.kicad_pcb` | ★**0 行** ★ | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**逐字节不变** (★本单不碰板★) ★ |
| `HW/PCB/demo_mainboard.kicad_pro` | ★**0 行** ★ | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | ★**逐字节不变** ★ |
| `HW/PCB/demo_mainboard*.kicad_sch` (11 个) | ★**内容 0 行** ★ | — | — | ★**只差随机 UUID + 时间戳** ⇒ 见 §4.3★ |

★**净效果: ★**只动 1 个真源文件的 2 行 + 2 个生成物的 2 行各** ⇒ ★**脚表 / BOM / `.net` / 板 / `.kicad_pro` 一个字节都不变** ★★

### 3.2 ★**为什么要同一批落 (★这就是本单不落真盘的原因★)★**

★**F1 改的是真源 `state/gen_netlist.py` ⇒ 网表 md5 变 (`611c3ba3…` → `16ac89f7…`) ⇒ 同批在跑的 ISS-245 (SW 侧 H-1 重锚) / ISS-246 (MECH 侧 H-1 重锚) 锚的是【落表前】的 md5 ⇒ 锚完当场又过期** ★
⇒ ★**所以: 本轮只出作业包 (沙盒实跑), 等老板拍完 A1/A2/A3, 下一批【一次落】, 落完把新 md5 一次性广播给 SW / MECH 两边** ★

---

## 4 · ★**沙盒实跑证据 (★`/tmp` 整树实跑 · ★真盘零写入★)★**

### 4.1 ★**沙盒布局 (★本机实跑, ★已在本单交卷前清掉★)★**

| 目录 | 内容 |
|---|---|
| `…/.sandbox_iss247/sb0` | ★**基线副本** (★真盘原样拷入, ★未重生成★)★ |
| `…/.sandbox_iss247/sb_base` | ★**基线 + 未改代码重生成一遍** (★用于把【重生成噪声】从【F1 真影响】里剥掉★)★ |
| `…/.sandbox_iss247/sb1` | ★**按本作业包改法改过 + 整链重生成** (★= F1 已落表的沙盒★)★ |

★**重生成链 (★顺序是硬的: ISS-230 实测结论 —— 脚表脚号来自 `.net`★)★**

```bash
python3 state/gen_netlist.py       # 网表 (表A HW/netlist_v1.csv)
python3 state/gen_kicad_net.py     # KiCad 网表 (HW/netlist_v1.net)
python3 state/gen_netlist_pins.py  # 脚表 (表B HW/netlist_v1_pins.csv)
python3 state/gen_bom.py           # BOM (HW/BOM_v1.csv)
python3 state/gen_schematic_pages.py  # 原理图页 (HW/SCHEMATIC_V1.md)
python3 state/gen_kicad_sch.py     # KiCad 原理图 (HW/PCB/demo_mainboard*.kicad_sch)
```

### 4.2 ★**改前 → 改后 diff 原文 (★三段, ★原样★)★**

#### ★D1 · 真源 `state/gen_netlist.py` (★`sb0` → `sb1`★)★

```diff
--- OLD/state/gen_netlist.py
+++ NEW/state/gen_netlist.py
@@ -378,7 +378,7 @@
         "π 滤波输入电容位 (值待充电 IC 定; 内置则改 DNP)", "C-01")
     add("P1", "GND", "C_VBUS_IN", "GND", "C_VBUS_IN", "[待选型] 10µF", "C",
         "DNP", "[推算]", "", "π 滤波输入电容 地端", "C-01")
-    add("P1", "VBUS_5V_F1", "FB_VBUS", "C_VBUS_OUT", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
+    add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
         "必装", "[推算]", "",
         "[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗)", "C-01")
     add("P1", "VBUS_5V_F1", "VBUS_5V_F1", "C_VBUS_OUT", "C_VBUS_OUT", "[待选型] 100µF", "C",
@@ -390,7 +390,7 @@
         "又是对地电容 · 一颗 2 脚件落进 3 个网 = 导出后一脚悬空); BQ25896 建议 ≥100µF", "C-01")
     add("P1", "VBUS_5V_CHG", "C_VBUS_OUT", "U_CHG pin1", "C_VBUS_OUT", "[待选型] 100µF", "C",
         "DNP", "[推算]", "", "π 滤波电容 (后级, 串联) 位", "C-01")
-    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "C_VBUS_OUT", "C_VBUS_GND", "[待选型] 100µF", "C",
+    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "VBUS_5V_CHG", "C_VBUS_GND", "[待选型] 100µF", "C",
         "DNP", "[推算]", "",
         "π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点)", "C-01")
     add("P1", "VBUS_5V_CHG", "U_CHG", "NET_VBUS_5V_CHG", "U_CHG", "BQ25896", "IC",
```

#### ★D2 · 生成物 `HW/netlist_v1.csv` (★`sb_base` 已重生成未改 → `sb1` 已改★)★

```diff
--- OLD/HW/netlist_v1.csv
+++ NEW/HW/netlist_v1.csv
@@ -5,11 +5,11 @@
 P1,VBUS_5V_ESD,D_ESD_TC,FB_VBUS,FB_VBUS,π 滤波磁珠 [待选型],L,必装,[推算],,[VBUS_5V_ESD] VBUS 入口 π 滤波磁珠位 (阻抗/电流随充电 IC 环路稳定性定),C-01,CHG_BOARD,,
 P1,VBUS_5V_ESD,VBUS_5V_ESD,C_VBUS_IN,C_VBUS_IN,[待选型] 10µF,C,DNP,[推算],,π 滤波输入电容位 (值待充电 IC 定; 内置则改 DNP),C-01,CHG_BOARD,,
 P1,GND,C_VBUS_IN,GND,C_VBUS_IN,[待选型] 10µF,C,DNP,[推算],,π 滤波输入电容 地端,C-01,CHG_BOARD,,
-P1,VBUS_5V_F1,FB_VBUS,C_VBUS_OUT,FB_VBUS,π 滤波磁珠 [待选型],L,必装,[推算],,[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗),C-01,CHG_BOARD,,
+P1,VBUS_5V_F1,FB_VBUS,VBUS_5V_F1,FB_VBUS,π 滤波磁珠 [待选型],L,必装,[推算],,[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗),C-01,CHG_BOARD,,
 P1,VBUS_5V_F1,VBUS_5V_F1,C_VBUS_OUT,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,π 滤波后级电容位 (BQ25896 建议 ≥100µF),C-01,CHG_BOARD,,
 P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,"π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容, 又是对地电容 · 一颗 2 脚件落进 3 个网 = 导出后一脚悬空); BQ25896 建议 ≥100µF",C-01,CHG_BOARD,,
 P1,VBUS_5V_CHG,C_VBUS_OUT,U_CHG pin1,C_VBUS_OUT,[待选型] 100µF,C,DNP,[推算],,"π 滤波电容 (后级, 串联) 位",C-01,CHG_BOARD,,
-P1,VBUS_5V_CHG,C_VBUS_GND,C_VBUS_OUT,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点),C-01,CHG_BOARD,,
+P1,VBUS_5V_CHG,C_VBUS_GND,VBUS_5V_CHG,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点),C-01,CHG_BOARD,,
 P1,VBUS_5V_CHG,U_CHG,NET_VBUS_5V_CHG,U_CHG,BQ25896,IC,必装,[官方],,"[VBUS_5V_CHG] 1A 单节锂电充电 IC (TI); 输入接 VBUS_5V_F1, BAT 脚接 BAT 轨, STAT/PG 脚回主 PCB (见 P2)",C-01,CHG_BOARD,"WQFN-24 4x4mm P0.5 (RTW 24, 16mm², h<=0.8mm, TI 封装图 4224801/A)",BQ25896RTWR
```

#### ★D3 · 生成物 `HW/SCHEMATIC_V1.md` (★`sb_base` → `sb1`★)★

```diff
--- OLD/HW/SCHEMATIC_V1.md
+++ NEW/HW/SCHEMATIC_V1.md
@@ -48,11 +48,11 @@
 | VBUS_5V_ESD | D_ESD_TC | FB_VBUS | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | CHG_BOARD | [推算] |  | [VBUS_5V_ESD] VBUS 入口 π 滤波磁珠位 (阻抗/电流随充电 IC 环路稳定性定) |
 | VBUS_5V_ESD | VBUS_5V_ESD | C_VBUS_IN | C_VBUS_IN | [待选型] 10µF | C | DNP | [推算] |  | π 滤波输入电容位 (值待充电 IC 定; 内置则改 DNP) |
 | GND | C_VBUS_IN | GND | C_VBUS_IN | [待选型] 10µF | C | DNP | [推算] |  | π 滤波输入电容 地端 |
-| VBUS_5V_F1 | FB_VBUS | C_VBUS_OUT | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | CHG_BOARD | [推算] |  | [VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗) |
+| VBUS_5V_F1 | FB_VBUS | VBUS_5V_F1 | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | CHG_BOARD | [推算] |  | [VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗) |
 | VBUS_5V_F1 | VBUS_5V_F1 | C_VBUS_OUT | C_VBUS_OUT | [待选型] 100µF | C | DNP | [推算] |  | π 滤波后级电容位 (BQ25896 建议 ≥100µF) |
 | GND | C_VBUS_GND | GND | C_VBUS_GND | [待选型] 100µF | C | DNP | [推算] |  | π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容,  |
 | VBUS_5V_CHG | C_VBUS_OUT | U_CHG pin1 | C_VBUS_OUT | [待选型] 100µF | C | DNP | [推算] |  | π 滤波电容 (后级, 串联) 位 |
-| VBUS_5V_CHG | C_VBUS_GND | C_VBUS_OUT | C_VBUS_GND | [待选型] 100µF | C | DNP | [推算] |  | π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点) |
+| VBUS_5V_CHG | C_VBUS_GND | VBUS_5V_CHG | C_VBUS_GND | [待选型] 100µF | C | DNP | [推算] |  | π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点) |
 | VBUS_5V_CHG | U_CHG | NET_VBUS_5V_CHG | U_CHG | BQ25896 | IC | 必装 | CHG_BOARD | [官方] |  | [VBUS_5V_CHG] 1A 单节锂电充电 IC (TI); 输入接 VBUS_5V_F1, BAT 脚接 BAT 轨,  |
```

### 4.3 ★**上一轮那个「待查现象」的结论: `.kicad_sch` 逐字节不同 = 【纯 UUID 抖动 + 时间戳】, 与 F1 无关★**

★**实测方法: 把 11 个 `.kicad_sch` 的 UUID 与时间戳归一化后再逐字节比对 `sb_base` vs `sb1`★**

```
demo_mainboard.kicad_sch : SAME  (0e0351378a97af1c0323d95a3d6b0d6e vs 0e0351378a97af1c0323d95a3d6b0d6e)
demo_mainboard_p1.kicad_sch : SAME  (9c075497ed56d94acd78437605771abb vs 9c075497ed56d94acd78437605771abb)
demo_mainboard_p2.kicad_sch : SAME  (3bfdec902857a7c799feee102209b130 vs 3bfdec902857a7c799feee102209b130)
demo_mainboard_p3.kicad_sch : SAME  (5a138552e8a9265398baaaf1a85cac06 vs 5a138552e8a9265398baaaf1a85cac06)
demo_mainboard_p4.kicad_sch : SAME  (704d26bf6f9a3492de6a8c6a937d21c9 vs 704d26bf6f9a3492de6a8c6a937d21c9)
demo_mainboard_p5.kicad_sch : SAME  (67457362af1f65274c49da53e18bab14 vs 67457362af1f65274c49da53e18bab14)
demo_mainboard_p6.kicad_sch : SAME  (7b13947586bc4e93f86cc793be85c326 vs 7b13947586bc4e93f86cc793be85c326)
demo_mainboard_p7.kicad_sch : SAME  (1ac90752682b56cf7301785fb8de2a1c vs 1ac90752682b56cf7301785fb8de2a1c)
demo_mainboard_p8.kicad_sch : SAME  (51aedd50dfed30fef01bf26da2012b04 vs 51aedd50dfed30fef01bf26da2012b04)
demo_mainboard_p9.kicad_sch : SAME  (980c80e16d1e521e51848ee3cc662cd8 vs 980c80e16d1e521e51848ee3cc662cd8)
demo_mainboard_p10.kicad_sch : SAME  (c7e3e011192eef292b64e577f438f00b vs c7e3e011192eef292b64e577f438f00b)
```

★**⇒ 结论: ★F1 落表对原理图【图形内容】零影响 (11 个 `.kicad_sch` 归一化后逐字节相同)★; `.kicad_sch` 的 md5 天生不稳定 (`state/gen_kicad_sch.py` 每次跑都重铸随机 UUID, `STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` 每次都重写时间戳) ⇒ ★`.kicad_sch` 的 md5 不许当锚点** ★
★**⇒ 下一批落表建议: ★`.kicad_sch` 要么【不重新生成】(落表后手动 restore), 要么【接受 UUID 抖动并在台账里写明】★ ⇒ 不然每次落表都会凭空多出 11 个文件的 md5 变化, 把 SW/MECH 的重锚搞成一团乱麻** ★

---

## 5 · ★**复现命令 (★从零复跑一整串★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── ① 沙盒整树拷贝 (★真盘只读★)
SB=/tmp/iss247_replay
rm -rf $SB && mkdir -p $SB
cp -a HW $SB/HW && cp -a state $SB/state
find $SB -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# ── ② 按 §2.2 改两行 (★改法 1★)
python3 - <<'PY'
import io
p = "$SB/state/gen_netlist.py"        # ← 改成你的沙盒路径
t = io.open(p, encoding="utf-8").read()
old1 = 'add("P1", "VBUS_5V_F1", "FB_VBUS", "C_VBUS_OUT", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",'
new1 = 'add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",'
old2 = 'add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "C_VBUS_OUT", "C_VBUS_GND", "[待选型] 100µF", "C",'
new2 = 'add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "VBUS_5V_CHG", "C_VBUS_GND", "[待选型] 100µF", "C",'
assert t.count(old1) == 1, "改法1 命中数不是 1 ⇒ 行号漂移了, 停"
assert t.count(old2) == 1, "改法2 命中数不是 1 ⇒ 行号漂移了, 停"
t = t.replace(old1, new1).replace(old2, new2)
io.open(p, "w", encoding="utf-8").write(t)
print("patched OK")
PY

# ── ③ 整链重生成 (★顺序硬★)
cd $SB
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ── ④ 门禁实跑 (★期望: F1 消失, 剩 F2+F3★)
python3 HW/check_netlist_contradiction_r3.py            # rc=1 · findings=2 (F2+F3) · F1 没了
python3 HW/check_netlist_selfconsistency.py              # rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 · ★仍 18 条★
python3 state/check_netlist.py && python3 state/check_netlist_pins.py   # rc=0
python3 state/check_sch_erc.py && python3 state/check_sch_pinfull.py   # rc=0
python3 HW/check_part_selection_matrix.py               # rc=0 · 8/8
python3 HW/check_iss247_f1_landed.py                    # rc=0 · 「F1 已落表」
python3 HW/check_iss247_f1_landed.py --selftest         # rc=0 · 11/11

# ── ⑤ 受保护 md5 对照 (★5 件必须逐字节不变★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```

★**★落表前必须先核对: ★`grep -n 'add("P1", "VBUS_5V_F1", "FB_VBUS"' $SB/state/gen_netlist.py` 与 ★`grep -n 'add("P1", "VBUS_5V_CHG", "C_VBUS_GND"' $SB/state/gen_netlist.py`★ —— ★**行号会随别的批次漂移 (V-3 落表会删 `DEMO_DNP` 3 行 ⇒ 后面所有行号 -3) ⇒ 一律用【字符串唯一命中】定位, 不许用裸行号** ★★

### 5.1 ★**§5 这一整串命令, 本单已在本机端到端跑过一遍 (★原样输出★)★**

```
$ python3 - <<'PY'   # ★改两行★
patched OK
$ for s in state/gen_netlist.py state/gen_kicad_net.py state/gen_netlist_pins.py \
           state/gen_bom.py state/gen_schematic_pages.py state/gen_kicad_sch.py; do ...; done
   (★6 个生成器全部 rc=0, 无 FAIL★)
$ python3 HW/check_netlist_contradiction_r3.py --json | python3 -c "..."
findings = 2 ['F2', 'F3']
$ python3 HW/check_iss247_f1_landed.py | tail -3
  判定: ✅ F1 已落表 (两颗 2 脚电容的端子标签不再撞车)
  rc   = 0
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
         HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
16ac89f77c25a3f61834cc7ebcd78a7f  HW/netlist_v1.csv
ef436a37412ac9b6eac3c9f41f1edca4  HW/netlist_v1_pins.csv
2a7305741134788dfee9f13f34c656b4  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
```

★**⇒ 复跑用的网表 md5 `16ac89f7…` 与 §3.1 表里写的【新 md5】逐字一致 ⇒ ★**§5 的复现命令可信, 下一批照着抄即可** ★
★**⇒ 脚表 / BOM / 板 / `.kicad_pro` 四个 md5 与真盘现值逐字一致 ⇒ ★**F1 落表对它们零影响 (复跑实测)** ★
★**⇒ 复跑用的沙盒 (`/tmp/iss247_replay_test`) 已删除 ★**

---

## 6 · ★**回滚方法**★

| 场景 | 回滚动作 |
|---|---|
| ★**只回滚 F1 这一次落表 (推荐)** ★ | ① 把 `state/gen_netlist.py` 的 L381 / L393 两个字符串**改回** §2.2 的 `-` 行 (★`C_VBUS_OUT`★) ② 重跑 §5 ③ 的整链 ③ ★`md5sum` 应当回到 `611c3ba3…` (网表) / `289fbafa…` (`SCHEMATIC_V1.md`)★ ④ `HW/check_iss247_f1_landed.py` ⇒ rc=1 (F1 未落) ★ |
| ★**整批回滚 (含 V-2/V-3/V-4)** ★ | 走 `state/land_v_values.py` 自带的回滚: `python3 state/land_v_values.py --rollback state/.bak_land_v_values_<时间戳>` (★落表器在 `--apply` 前会自动打一份 `.bak_land_v_values_*` 副本★) |
| ★**已落表后的门禁口径回退** ★ | ① `HW/check_netlist_contradiction_r3.py` 的 `--selftest` **T7 / T8** 两条断言 (★落 F1 后必红, ★见 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` §3★) 改回「恰 3 条 / A1~A4 全红」 ② `HW/check_netlist_contradiction_r3.py` 主模式摘要里的 `ok = (len(res["findings"]) == 3)` 改回 3 |

★**回滚不涉及板 / 脚表 / BOM (★它们逐字节不变, ★不用回滚★) ⇒ ★**回滚面 = 1 个真源文件的 2 个字符串 + 2 个生成物 + 2 条门禁断言** ★

---

## 7 · ★**下一批必须同时做的配套改动 (★详见 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md`★)★**

| # | 配套项 | 为什么必须同批做 | 改哪 |
|---|---|---|---|
| **1** | ★**`HW/check_netlist_contradiction_r3.py` 的 `--selftest` T7 / T8 两条断言** ★ | ★**T7 断言「真文件恰 3 条 findings」· T8 断言「A1/A2/A3/A4 四条规则全红」⇒ F1 一落表 (findings 变 2 条 · A1/A2 变绿) ⇒ ★**T7 / T8 必红** ★ ⇒ ★**下一批不改这两条 ⇒ `--selftest` rc=1 ⇒ 门禁链红** ★ | `HW/check_netlist_contradiction_r3.py` 的 T7 / T8 + 主模式摘要里的 `== 3` |
| **2** | ★**`HW/check_netlist_contradiction_r3.py` 主模式摘要文案** ★ | 「主线要求 = 恰 3 条」落表后变成「恰 2 条」⇒ 文案要同步 (★**判据逻辑一个字不许动**★) | 同上 |
| **3** | ★**T1 / T2 / T3 三条反向用例必须保留** ★ | ★它们是【注入错误 ⇒ 必须抓到红】的自证 ⇒ **一条都不许删** (★落表后实测仍 11/11 中的 3 条绿★)★ | — |
| **4** | ★**新门禁 `HW/check_iss247_f1_landed.py` 的口径** ★ | 默认模式落表后自然转绿 (rc=0) ⇒ 不必改; ★但 `--expect-not-landed` 这条「现状守卫」口径会从绿变红 ⇒ 下一批要停用它或改成 `--expect-landed`★ | `HW/check_iss247_f1_landed.py` 的命令行口径 |
| **5** | ★**SW / MECH 两侧 H-1 重锚** ★ | 网表 md5 变 ⇒ ★**ISS-245 / ISS-246 锚的是落表前的 md5 ⇒ 落完必须让两边再重锚一次** ★ | `SW/SW_MD5_BASELINE_LEDGER.md` / MECH 侧台账 (★不是本单的活★) |

---

## 8 · 边界与声明 (★逐条自证★)

| 项 | 自证 |
|---|---|
| ★**真盘零写入** ★ | ★网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★**交卷前后逐字节不变** (★见交卷单 B5 ⑦★) ★ |
| ★**不碰 PCB 布线 / 布局 / 板框** ★ | ★本单只改【网表 node2 标签】, 板文件 md5 逐字节不变; 板那一趟按老板 2026-11-11 10:07 口径继续排队★ ★ |
| ★**不碰 F2 / F3** ★ | ★F2 (J_CHG 位号消歧) / F3 (板侧 DNP 标记) **本单只登记, 不做** ★ |
| ★**不碰 SW / MECH 分片与台账** ★ | ★本单只写 `state/fragments/hw.yaml` (走 `state/frag_write.py`)★ ★ |
| ★**不改已有门禁的判据逻辑 / 不把红灯调没** ★ | ★本单**新增**一个门禁, **没有改任何已有门禁的一个字节**; 真盘 `check_netlist_contradiction_r3.py` 仍恰 3 条 · `--expect-resolved` 仍 18 条 ★ |
| ★**零外发** ★ | ★没发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02 口径★)★ ★ |
| ★**不替老板拍板** ★ | ★V-2 / V-3 / V-4 三条 ★**一条没拍**★; 本单只出 F1 的作业包 ★ |
| ★**实物 [实测] = 0 条** ★ | ★本单零实物 (★板与屏不在本机★); 所有 [实测] 均为「本机脚本实跑 / 本机文件实读」 ★ |

---

> ★**本作业包只出包不落表 ⇒ ★**下一批落表请照 §5 复现命令 + §7 配套项一起做, 落完把新 md5 (网表 / 脚表 / BOM) 一次性广播给 SW (ISS-245) / MECH (ISS-246) 走 H-1 重锚** ★ ★

---

## 9 · ★★【现状订正 · 2026-11-17 05:19 实测 · hw-lead 第三轮复验】★★ F1 已落表 ⇒ ★**本作业包现在是【已执行的历史包】, 不是待办★** ★★

> ★**本段作者**: hw-lead · ★**单号**: ISS-247 (★复验轮·追加段·**老字一句没删**★) ★
> ★**依据**: ★`HW/ISS247_reverify2_acceptance_rc.log` (★本轮 20 条命令原样输出·跑前跑后 md5 对照★) · ★`HANDOFF/2026-11-17_hw-lead_ISS247_复验与下一批落表路径实测.md` (★第二轮复验单★) ★
> ★**本段只登记现状, 不改 §1~§8 一个字 (★§1~§8 是 ISS-247 交卷当时的快照, 有据可查★)** ★

### 9.1 · ★**F1 已于 2026-11-16 19:2x 由 ISS-249 真落表 (★本包 §2.2 的改法已被应用★)** ★

| ★**项** ★ | ★**2026-11-17 05:19 实测** ★ |
|---|---|
| ★**F1 落表状态** ★ | ★**已落** — `HW/check_iss247_f1_landed.py` rc=0 (S1~S6 全绿) · `--selftest` rc=0 · 用例 11 条·通过 11 条·失败 0 条 (反向 9 + 正向 2) ★ |
| ★**网表实况 (逐字)** ★ | ★`HW/netlist_v1.csv` L8 = `P1,VBUS_5V_F1,FB_VBUS,VBUS_5V_F1,FB_VBUS,…` (node2 = 自己的网名) · L10 = `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,…` · L12 = `P1,VBUS_5V_CHG,C_VBUS_GND,VBUS_5V_CHG,C_VBUS_GND,…` (node2 = 自己的网名) ⇒ ★**两颗 2 脚电容的端子登记各 2 次 = 脚表脚数 2** ★ |
| ★**真源实况 (逐字)** ★ | ★`state/gen_netlist.py` **L400** = `add("P1", "VBUS_5V_F1", "FB_VBUS", "VBUS_5V_F1", "FB_VBUS",` · **L413** = `add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "VBUS_5V_CHG", "C_VBUS_GND", "[待选型] 100µF", "C",` ★ |
| ★**R3 矛盾门禁** ★ | ★`HW/check_netlist_contradiction_r3.py` ⇒ FINDINGS=**2** (F2 `J_CHG 位号双义` + F3 `板侧 DNP 标记`) · R3-A1/A2 双绿 · rc=1 (★预期: 那两条真缺陷还在★) · `--selftest` rc=0 (12 条反向用例全过, 含 T11「改回旧值 ⇒ 回到 3 条」) ★ |

### 9.2 · ★**本包 §2.2 / §3.1 / §6 里的行号与 md5 全部作废 (★它们是 ISS-247 交卷当时的一次性快照★)** ★

| ★**条目** ★ | ★**本包原写 (2026-11-16 18:1x 快照)** ★ | ★**2026-11-17 05:19 实测现值** ★ | ★**漂了** ★ |
|---|---|---|---|
| ★**F1 改法 1 (FB_VBUS 后级行)** ★ | ★L381 ★ | ★**L400** ★ | ★**+19** ★ |
| ★**F1 改法 2 (C_VBUS_GND 信号端行)** ★ | ★L393 ★ | ★**L413** ★ | ★**+20** ★ |
| ★**网表 md5 (落表前)** ★ | ★`611c3ba3…` ★ | ★**作废** (★已被 ISS-249 + ISS-257 两次合法落表换掉★) ★ | — |
| ★**网表 md5 (只落 F1 之后)** ★ | ★`16ac89f7…` ★ | ★**现行 = `e06c1dd6…`** ★ | — |
| ★**脚表 md5** ★ | ★`ef436a37…` ★ | ★**`287e7861…`** ★ | — |
| ★**BOM md5** ★ | ★`2a730574…` ★ | ★**`94642d07…`** ★ | — |
| ★**板 / `.kicad_pro` md5** ★ | ★`611b869e…` / `3e504d2b…` ★ | ★**`611b869e…` / `3e504d2b…` (没动过)** ★ | ★**0** ★ |
| ★**`SCHEMATIC_V1.md` md5** ★ | ★`289fbafa…` → `d37bbd0d…` ★ | ★**现行 `a274748a…`** ★ | — |

### 9.3 · ★**★纪律 (★照抄这一段就不会踩坑★)** ★

1. ★**F1 不要再落第二遍**: ★§2.2 那两行字符串已经在真源里了 ⇒ 再照抄一次 = 把 `node2` 从 `VBUS_5V_F1` 改成 `VBUS_5V_F1` (空转) 或改错成别的值 ⇒ ★**要判「F1 落没落」, 跑 `python3 HW/check_iss247_f1_landed.py` (rc=0 = 已落) , 不许靠肉眼看网表★** ★
2. ★**行号 = 一次性快照**: ★§2.2 / §6 / §7 里的行号只对 2026-11-16 18:1x 那一刻有效 ⇒ ★**任何落表脚本一律用「唯一字符串 + 上下文锚点 + `assert count == 1`」定位, 不许裸行号** (★ISS-243 / ISS-249 / ISS-257 三个已落表单都是这么做的★) ★
3. ★**md5 同样是快照**: ★下一批 (V-2/V-3/V-4) 一落, 网表 md5 再变 ⇒ ★**一次落完只广播一次新 md5, SW (ISS-245) / MECH (ISS-246) 各重锚 1 次** ★
4. ★**§5 的复现命令**: ★**「只读门禁 + 沙盒」那几步现在照样能跑**; ★但**「整链重生成」那一步在真盘上是写盘动作 (会改网表 md5) ⇒ 现在只许在 `/tmp` 沙盒里跑, 真盘跑 = 无意落表** ★
5. ★**下一批落表 = V-2 / V-3 / V-4** (★F1 已出表·不用再进下一批★) ⇒ ★配方与撞车分析见 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` §10 (★2026-11-17 05:0x 沙盒 dry-run 三条全 rc=0, 每条「匹配 1 处」★) ⇒ ★**前置 = 老板 A1/A2/A3 未拍 (三条一条没拍), 本单不代拍** ★

### 9.4 · ★**本轮 (第三轮复验) 边界自证 ★**

| ★**边界** ★ | ★**自证** ★ |
|---|---|
| ★**真盘零写入** ★ | ★7 个受保护文件 + `HW/PCB/` 整树指纹 在本轮窗口 (05:18:48~05:19:05) 内跑前跑后**逐字节相同** (★`e06c1dd6…` / `287e7861…` / `94642d07…` / `611b869e…` / `3e504d2b…` / `bdd691a7…` / `a274748a…` + 整树 `a80b1367…`★) ★ ★**窗口之外 (05:19:31 / 05:19:58~59) 有别的 agent 重铸了 `HW/PCB/` 下 5 个文件 (★`BOARD_ONEPASS_WORKPACKET.md` + `STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` / `_frame_reference.kicad_pcb` = ★`gen_kicad_project.py` 的时间戳派生物★) ⇒ 整树指纹变 `bc4c58ee…` ⇒ ★**不是本单干的 (本单 11 条命令逐个 grep 过, 没一条碰生成器★)· 两件硬保护 (真板 + `.kicad_pro`) 从头到尾 0 漂** ⇒ ★**原文与归因见 `HW/ISS247_reverify2_acceptance_rc.log` §6★** ★ |
| ★**既有门禁红数没被我调没** ★ | ★`--expect-resolved` **仍 18 条** (rc=1) · R3 **仍恰 2 条** (rc=1) · selfconsistency rc=0 · `check_netlist` rc=0 · `check_netlist_pins` rc=0 · **ERC=0** rc=0 · `check_sch_pinfull` rc=0 · 选型矩阵 **8/8** rc=0 ★ |
| ★**台账闸** ★ | ★`state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18 · Q6 硬件真源闸通过) ★ |
| ★**零外发 / 零实物 / 不替老板拍板 / 不碰板 / 不碰 F2·F3** ★ | ★本轮只跑只读门禁 + `merge.py` (只刷 `STATE.yaml`) + 写本段与 1 条分片 ⇒ **网表/脚表/BOM/板/`.kicad_pro`/`HW/PCB/` 一个字没动** ★ |

